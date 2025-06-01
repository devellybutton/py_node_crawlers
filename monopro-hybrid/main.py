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
from selenium.webdriver.common.action_chains import ActionChains
import cv2

# 1. momail 로그인
options = Options()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

driver.get("https://momail.kr")
wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))).send_keys(EMAIL)
driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
driver.find_element(By.XPATH, '//button[@aria-label="Connect"]').click()
print("[INFO] momail 로그인 완료")

# 2. OpenAI 브라우저 창에 직접 포커스 후 타이핑 시작
print("[INFO] OpenAI 브라우저를 클릭하고, 5초 안에 입력 시작")
time.sleep(5)

# 이메일 타이핑 (안전한 속도)
pyautogui.typewrite(EMAIL, interval=0.1)
pyautogui.press("enter")
time.sleep(3)

# 비밀번호 입력 전 추가 확인
time.sleep(1)
pyautogui.typewrite(PASSWORD, interval=0.15)
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
            except Exception:
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

# 4. 인증코드 입력
pyperclip.copy(verification_code)
print("[INFO] 인증코드 복사됨. 브라우저에 포커스한 후 3초 내로 자동 붙여넣기")
time.sleep(3)
pyautogui.hotkey('ctrl', 'v')
pyautogui.press("enter")
pyperclip.copy("")  # 클립보드 초기화
print("[INFO] 인증코드 붙여넣기 완료")

# 5. OpenAI 내 설정 진입 → 메모리 삭제
print("[INFO] 로그인 후 설정 진입 시작")
time.sleep(8)  # 페이지 로딩 완료 대기

# 계정 아이콘 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/profile_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] profile_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] profile_button 처리 중 예외 발생:", e)

# 안 되는 구간 디버깅용!
# pyautogui.screenshot("debug_current.png")
# print("[DEBUG] 현재 화면을 'debug_current.png'로 저장했습니다")

# 설정 메뉴 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/setting_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] setting_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] setting_button 처리 중 예외 발생:", e)

# "모든 채팅 삭제하기" 버튼 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/delete_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] delete_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] delete_button 처리 중 예외 발생:", e)

# "삭제 확인" 버튼 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/delete_confirm_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] delete_confirm_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] delete_confirm_button 처리 중 예외 발생:", e)

# "개인 맞춤 설정" 탭 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/personalization_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] personalization_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] personalization_button 처리 중 예외 발생:", e)

# "메모리 관리하기" 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/memory_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] memory_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] memory_button 처리 중 예외 발생:", e)

# "모두 삭제" 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/delete_button_memory.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] delete_memory_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] delete_memory_button 처리 중 예외 발생:", e)

# "메모리 지우기" 버튼 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/reset_memory.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] reset_memory 이미지 못 찾음")
except Exception as e:
    print("[ERROR] reset_memory 처리 중 예외 발생:", e)

# ESC 키로 모달 닫기
print("[INFO] ESC 키로 모달창들 닫기")
pyautogui.press("escape")
time.sleep(0.5)
pyautogui.press("escape")

# 로그아웃
try:
    location = pyautogui.locateCenterOnScreen("../assets/logout_button.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] logout_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] logout_button 처리 중 예외 발생:", e)

# 모달창에서 로그아웃 버튼 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/logout_button_black.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] logout_button 이미지 못 찾음")
except Exception as e:
    print("[ERROR] logout_button 처리 중 예외 발생:", e)

# 모달창에서 로그인 버튼 클릭
try:
    location = pyautogui.locateCenterOnScreen("../assets/login_button_black.png", confidence=0.8)
    if location:
        pyautogui.click(location)
        time.sleep(1)
    else:
        print("[ERROR] login_button_black 이미지 못 찾음")
except Exception as e:
    print("[ERROR] logout_button_black 처리 중 예외 발생:", e)

# 마무리
print("[INFO] 모든 작업 완료")
# driver.quit()