import time
import re
import pyperclip
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.account_loader import load_accounts

json_path = "../data/accounts.json"
excel_path = "../data/accounts.xlsx"

accounts = load_accounts(json_path, excel_path)

def process_account(email, password):
    options = Options()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    # 1. momail 로그인
    driver.get("https://momail.kr")
    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))).send_keys(email)
    driver.find_element(By.ID, "passwordField").send_keys(password)
    driver.find_element(By.XPATH, '//button[@aria-label="Connect"]').click()
    print("[INFO] momail 로그인 완료")

    # 2. OpenAI 브라우저 클릭 유도 후 로그인
    print("[INFO] OpenAI 브라우저를 클릭하고, 5초 안에 입력 시작")
    time.sleep(5)
    pyautogui.typewrite(email, interval=0.1)
    pyautogui.press("enter")
    time.sleep(3)
    pyautogui.typewrite(password, interval=0.15)
    pyautogui.press("enter")
    print("[INFO] 로그인 완료, 인증코드 대기")

    # 3. 인증코드 수신 대기
    verification_code = None
    timeout = time.time() + 180  # 최대 3분 대기

    while time.time() < timeout:
        try:
            driver.refresh()
            time.sleep(2)
            messages = driver.find_elements(By.XPATH, '//*[@id="messagesList"]/md-virtual-repeat-container/div/div[2]/md-list/md-list-item')
            for message in messages:
                try:
                    content = message.find_element(By.XPATH, './/div[1]/div/div[1]/div[2]/div[2]').text.strip()
                    if content.startswith("Your ChatGPT code") or re.search(r'\d{6}', content):
                        match = re.search(r'\b(\d{6})\b', content)
                        if match:
                            verification_code = match.group(1)
                            print("[INFO] 인증코드:", verification_code)
                            break
                except Exception:
                    continue
            if verification_code:
                break
        except Exception as e:
            print(f"[WARN] 인증코드 확인 중 오류: {e}")
        time.sleep(2)

    if not verification_code:
        print("[ERROR] 인증코드 못 찾음")
        return

    pyperclip.copy(verification_code)
    print("[INFO] 인증코드 복사됨. 3초 후 붙여넣기")
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press("enter")
    pyperclip.copy("")
    print("[INFO] 인증코드 붙여넣기 완료")

    # 4. 설정 진입 및 메모리 삭제
    time.sleep(8)
    def click_image(image_path):
        try:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
            if location:
                pyautogui.click(location)
                time.sleep(1)
                return True
            else:
                print(f"[ERROR] {image_path} 이미지 못 찾음")
                return False
        except Exception as e:
            print(f"[ERROR] {image_path} 처리 중 예외 발생: {e}")
            return False

    click_image("../assets/profile_button.png")
    click_image("../assets/setting_button.png")
    click_image("../assets/delete_button.png")
    click_image("../assets/delete_confirm_button.png")
    click_image("../assets/personalization_button.png")
    click_image("../assets/memory_button.png")
    click_image("../assets/delete_button_memory.png")
    click_image("../assets/reset_memory.png")
    pyautogui.press("escape")
    time.sleep(0.5)
    pyautogui.press("escape")
    
    # 5. 로그아웃 및 로그인 페이지 복귀
    click_image("../assets/logout_button.png")
    click_image("../assets/logout_button_black.png")
    if click_image("../assets/login_button_black.png"):
        print("[INFO] 로그인 버튼 클릭됨, 다음 계정 로그인 대기")
        time.sleep(5)
    else:
        print("[ERROR] 로그인 버튼 클릭 실패. 다음 계정으로 진행 어려움")

    print("[INFO] 계정 처리 완료\n")

for idx, acc in enumerate(accounts):
    print(f"[INFO] === {idx+1}번째 계정 시작: {acc['email']} ===")
    try:
        process_account(acc["email"], acc["password"])
    except Exception as e:
        print(f"[ERROR] 계정 {acc['email']} 실패: {e}")
        continue
