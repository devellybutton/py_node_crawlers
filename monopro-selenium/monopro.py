import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import random
from login_info import EMAIL, PASSWORD

# 사람처럼 타이핑하는 함수
def human_typing(element, text, min_delay=0.05, max_delay=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

# 크롬 옵션 설정 (헤드리스 사용 X)
# options = Options()
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

# 드라이버 실행 (탐지 회피)
driver = uc.Chrome(options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # momail.kr 먼저 로그인해서 인증 대기 준비
    print("[INFO] momail.kr 로그인 중...")
    driver.get("https://momail.kr")

    email_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))
    )
    email_input.click()
    # email_input.send_keys(EMAIL)
    human_typing(email_input, EMAIL)

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="passwordField"]'))
    )
    # password_input.send_keys(PASSWORD)
    human_typing(password_input, PASSWORD)

    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Connect"]'))
    )
    login_btn.click()

    print("[INFO] momail 로그인 완료")

    # OpenAI 로그인 페이지 새 탭에서 접속
    driver.execute_script("window.open('https://auth.openai.com/log-in', '_blank');")
    driver.switch_to.window(driver.window_handles[1])

    print("[INFO] OpenAI 로그인 페이지 접속 중...")
    driver.get("https://auth.openai.com/log-in")

    # 이메일 입력
    # input 태그 중 type="email"인 필드 찾기 
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    # email_input.send_keys(EMAIL)
    human_typing(email_input, EMAIL)

    continue_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"][name="intent"][value="email"]')
    continue_btn.click()
    print("[INFO] 이메일 입력 후 계속 버튼 클릭 완료")

    # 비밀번호 입력 페이지로 전환 대기
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]'))
    )
    human_typing(password_input, PASSWORD)

    continue_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    continue_btn.click()
    print("[INFO] 비밀번호 입력 후 계속 버튼 클릭 완료")

    # momail 탭으로 돌아가 인증코드 수신
    driver.switch_to.window(driver.window_handles[0])
    print("[INFO] 인증 메일 대기 중...")
    time.sleep(5)

    # 메일 로딩 대기
    driver.switch_to.window(driver.window_handles[0])
    print("[INFO] 인증 메일 대기 중...")
    time.sleep(5)  # DOM 업데이트용 대기

    # 최신 메일에서 인증코드 추출
    messages = driver.find_elements(By.XPATH, '//*[@id="messagesList"]/md-virtual-repeat-container/div/div[2]/md-list/md-list-item[1]/div/div[1]/div/div[1]/div[2]/div[2]')

    # 인증 이메일에서 6자리 숫자 코드 추출
    verification_code = None
    for message in messages:
        try:
            content = message.find_element(By.XPATH, './/div[1]/div/div[1]/div[2]/div[2]').text.strip()
            print(f"[DEBUG] 메일 내용: {content}")
            if content.startswith("Your ChatGPT code"):
                match = re.search(r'\b(\d{6})\b', content)
                if match:
                    verification_code = match.group(1)
                    print('메일 인증코드: ', verification_code)
                    break
        except Exception as e:
            print(f"[INFO] 형식에 맞지 않는 이메일은 건너 뜁니다")
            continue
    
    if not verification_code:
        raise Exception("인증 코드를 찾을 수 없음")

    # OpenAI 이메일 인증 탭으로 돌아가기
    driver.switch_to.window(driver.window_handles[1])
    print("[INFO] 이메일 인증 코드 입력 중...")

    # 인증 코드 입력
    code_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "code"))
    )
    # code_input.send_keys(verification_code)
    human_typing(code_input, verification_code)

    # 계속 버튼 클릭
    continue_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    continue_btn.click()

    print("[INFO] ****** 인증 완료!")

except Exception as e:
    print(f"[ERROR] 예외 발생: {e}")

# finally:
#     # 종료 전 대기
#     time.sleep(5)
#     driver.quit()
