import time
import re
import pyperclip
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from login_info import EMAIL, PASSWORD

# 1. momail 로그인 후 코드 추출
options = Options()
driver = webdriver.Chrome(options=options)

driver.get("https://momail.kr")
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))
).send_keys(EMAIL)

driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
driver.find_element(By.XPATH, '//button[@aria-label="Connect"]').click()
print("[INFO] momail 로그인 완료")

# 2. OpenAI 브라우저 창에 직접 포커스 후 타이핑 시작
print("[INFO] OpenAI 브라우저를 클릭하고, 5초 안에 입력 시작")
time.sleep(5)

# 이메일 타이핑
pyautogui.typewrite(EMAIL, interval=0.05)
pyautogui.press("enter")
time.sleep(2)

# 비밀번호 타이핑
pyautogui.typewrite(PASSWORD, interval=0.05)
pyautogui.press("enter")
print("[INFO] 로그인 완료, 인증코드 대기")

# 3. 인증코드 수신 대기
verification_code = None
timeout = time.time() + 60

while time.time() < timeout:
    try:
        driver.refresh()
        time.sleep(2)

        messages = driver.find_elements(By.XPATH, '//*[@id="messagesList"]/md-virtual-repeat-container/div/div[2]/md-list/md-list-item')
        
        for message in messages:
            try:
                content = message.find_element(By.XPATH, './/div[1]/div/div[1]/div[2]/div[2]').text.strip()
                print(f"[DEBUG] 메일 내용: {content}")
                if content.startswith("Your ChatGPT code") or re.search(r'\d{6}', content):
                    match = re.search(r'\b(\d{6})\b', content)
                    if match:
                        verification_code = match.group(1)
                        print("[INFO] 인증코드:", verification_code)
                        break
            except Exception as e:
                print("[INFO] 형식에 맞지 않는 이메일은 건너뜀")
                continue

        if verification_code:
            break
    except Exception as e:
        print(f"[WARN] 인증코드 확인 중 오류: {e}")
    time.sleep(2)

if not verification_code:
    print("[ERROR] 인증코드 못 찾음")
    driver.quit()
    exit()

# 4. 인증코드 입력 (브라우저 포커스 필요)
pyperclip.copy(verification_code)
print("[INFO] 인증코드 복사됨. 브라우저에 포커스한 후 3초 내로 자동 붙여넣기")
time.sleep(3)
pyautogui.hotkey('ctrl', 'v')
pyautogui.press("enter")

driver.quit()