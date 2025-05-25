import time
import pyautogui
import pyperclip

email = "your@email.com"
password = "yourpassword123"

# 1. 로그인 창 포커스 맞춰두고 시작
print("크롬 창을 클릭해서 포커스를 맞춰주세요 (3초 후 자동 입력 시작)")
time.sleep(3)

# 2. 이메일 입력
pyautogui.typewrite(email, interval=0.05)
pyautogui.press("enter")

# 3. 비밀번호 입력
time.sleep(2)
pyautogui.typewrite(password, interval=0.05)
pyautogui.press("enter")

# 4. 인증코드 입력 (예시)
verification_code = "123456"
pyperclip.copy(verification_code)

print("인증코드 입력 준비 중... 창 포커스 맞추세요 (3초 후 붙여넣기)")
time.sleep(3)
pyautogui.hotkey("ctrl", "v")
pyautogui.press("enter")