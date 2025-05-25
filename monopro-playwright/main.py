import time
import re
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from login_info import EMAIL, PASSWORD


# ------------------ 사람처럼 타이핑 ------------------
def human_typing_selenium(element, text, min_delay=0.05, max_delay=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))


# ------------------ momail 로그인 ------------------
def login_to_momail_and_wait():
    print("[INFO] momail.kr 로그인 중...")

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://momail.kr")

        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))
        )
        email_input.click()
        human_typing_selenium(email_input, EMAIL)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="passwordField"]'))
        )
        human_typing_selenium(password_input, PASSWORD)

        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Connect"]'))
        )
        login_btn.click()
        print("[INFO] momail 로그인 완료 - 인증 메일 대기 준비")

        return driver  # 로그인된 상태 유지

    except Exception as e:
        driver.quit()
        raise e


# ------------------ momail 인증코드 추출 ------------------
def extract_code_from_momail(driver, timeout_sec=60):
    print("[INFO] 인증 코드 수신 대기 중...")

    start = time.time()
    while time.time() - start < timeout_sec:
        time.sleep(5)
        try:
            messages = driver.find_elements(By.XPATH, '//*[@id="messagesList"]/md-virtual-repeat-container/div/div[2]/md-list/md-list-item[1]/div/div[1]/div/div[1]/div[2]/div[2]')
            for message in messages:
                content = message.find_element(By.XPATH, './/div[1]/div/div[1]/div[2]/div[2]').text.strip()
                print(f"[DEBUG] 메일 내용: {content}")
                if content.startswith("Your ChatGPT code"):
                    match = re.search(r'\b(\d{6})\b', content)
                    if match:
                        code = match.group(1)
                        print("[INFO] 인증 코드 수신 완료:", code)
                        return code
        except:
            pass

    raise Exception("인증 코드 수신 실패 (타임아웃)")


# ------------------ OpenAI 로그인 ------------------
def login_openai_with_code(email, password, code):
    print("[INFO] OpenAI 로그인 시작 (Playwright)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        stealth_sync(page)

        page.goto("https://auth.openai.com/log-in", timeout=60000)

        page.wait_for_selector('input[type="email"]')
        page.type('input[type="email"]', email, delay=100)
        page.click('button[type="submit"][name="intent"][value="email"]')
        print("[INFO] 이메일 입력 완료")

        page.wait_for_selector('input[type="password"]', timeout=10000)
        page.type('input[type="password"]', password, delay=100)
        page.click('button[type="submit"]')
        print("[INFO] 비밀번호 입력 완료")

        page.wait_for_selector('input[name="code"]', timeout=15000)
        page.type('input[name="code"]', code, delay=100)
        page.click('button[type="submit"]')
        print("[INFO] 인증 코드 입력 완료 ✅")

        input("로그인 완료 확인 후 Enter를 누르면 종료됩니다.")
        browser.close()


# ------------------ 전체 실행 흐름 ------------------
if __name__ == "__main__":
    momail_driver = login_to_momail_and_wait()

    # OpenAI 로그인 시도 (인증코드 전까지)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        stealth_sync(page)

        print("[INFO] OpenAI 로그인 페이지 접속 중...")
        page.goto("https://auth.openai.com/log-in", timeout=60000)

        page.wait_for_selector('input[type="email"]')
        page.type('input[type="email"]', EMAIL, delay=100)
        page.click('button[type="submit"][name="intent"][value="email"]')
        print("[INFO] 이메일 입력 완료")

        page.wait_for_selector('input[type="password"]')
        page.type('input[type="password"]', PASSWORD, delay=100)
        page.click('button[type="submit"]')
        print("[INFO] 비밀번호 입력 완료")

        # 메일 발송 후 → momail에서 인증코드 추출
        verification_code = extract_code_from_momail(momail_driver)
        momail_driver.quit()

        # 인증 코드 입력
        page.wait_for_selector('input[name="code"]', timeout=15000)
        page.type('input[name="code"]', verification_code, delay=100)
        page.click('button[type="submit"]')
        print("[INFO] 인증 완료 ✅")

        input("확인 후 Enter 누르면 종료됩니다.")
        browser.close()
