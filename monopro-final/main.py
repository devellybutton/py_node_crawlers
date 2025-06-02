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

def parse_account_selection(selection_input):
    """
    계정 선택 입력을 파싱하여 실행할 계정 인덱스 리스트 반환
    예: "5" -> [4] (5번째 계정, 0부터 시작하므로 인덱스 4)
    예: "3-7" -> [2, 3, 4, 5, 6] (3번째부터 7번째까지)
    예: "1,3,5" -> [0, 2, 4] (1,3,5번째 계정들)
    예: "8-10,15" -> [7, 8, 9, 14] (8-10번째와 15번째)
    """
    if not selection_input.strip():
        return list(range(len(accounts)))  # 전체 계정
    
    indices = []
    parts = selection_input.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # 범위 지정 (예: "3-7")
            try:
                start, end = map(int, part.split('-'))
                if start < 1 or end > len(accounts) or start > end:
                    print(f"[ERROR] 잘못된 범위: {part} (계정 수: {len(accounts)})")
                    continue
                indices.extend(range(start - 1, end))  # 1-based를 0-based로 변환
            except ValueError:
                print(f"[ERROR] 잘못된 범위 형식: {part}")
                continue
        else:
            # 단일 번호 (예: "5")
            try:
                num = int(part)
                if num < 1 or num > len(accounts):
                    print(f"[ERROR] 잘못된 계정 번호: {num} (계정 수: {len(accounts)})")
                    continue
                indices.append(num - 1)  # 1-based를 0-based로 변환
            except ValueError:
                print(f"[ERROR] 잘못된 번호 형식: {part}")
                continue
    
    return sorted(list(set(indices)))  # 중복 제거 및 정렬

def show_account_list():
    """계정 목록 표시"""
    print("\n=== 계정 목록 ===")
    for idx, acc in enumerate(accounts):
        print(f"{idx + 1:2d}. {acc['email']}")
    print(f"총 {len(accounts)}개 계정")
    print("================\n")

def process_account(email, password):
    options = Options()
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    try:
        # 1. momail 로그인
        driver.get("https://momail.kr")
        wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="예: example@momail.kr"]'))).send_keys(email)
        driver.find_element(By.ID, "passwordField").send_keys(password)
        driver.find_element(By.XPATH, '//button[@aria-label="Connect"]').click()
        print("[INFO] momail 로그인 완료")

        # 2. OpenAI 브라우저 클릭 유도 후 로그인
        print("[INFO] OpenAI 브라우저에서 이메일 입력창을 클릭한 후 Enter를 눌러주세요...")
        input("준비되면 Enter를 눌러주세요: ")
        print("[INFO] 5초 후 이메일 입력을 시작합니다...")
        time.sleep(5)

        for i in range(3, 0, -1):
            print(f"[INFO] {i}초...")
            time.sleep(1)

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
                time.sleep(3)
                # 이메일 목록 새로고침 버튼을 두 번 클릭
                refresh_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/section/div/div[1]/md-toolbar[2]/div/button[2]')))
                refresh_button.click()
                time.sleep(3)
                refresh_button.click()
                print("[INFO] 새로고침 버튼 두 번 클릭 완료")
                time.sleep(3)  # 새로고침 후 로딩 대기

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
            time.sleep(3)

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
        def click_image_with_wait(image_path, timeout=30):
            """이미지가 화면에 나타날 때까지 기다린 후 클릭"""
            print(f"[INFO] {image_path} 이미지 대기 중...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    location = pyautogui.locateCenterOnScreen(image_path, confidence=0.7)
                    if location:
                        pyautogui.click(location)
                        print(f"[INFO] {image_path} 클릭 완료")
                        time.sleep(1)
                        return True
                    else:
                        time.sleep(1) # 1초 대기 후 다시 시도
                        return False
                except Exception as e:
                    print(f"[ERROR] {image_path} 처리 중 오류: {e}")
                    time.sleep(1)
            
            print(f"[ERROR] {image_path} 이미지를 {timeout}초 동안 찾지 못함")
            return False

        click_image_with_wait("../assets/profile_button.png")
        click_image_with_wait("../assets/setting_button.png")
        click_image_with_wait("../assets/delete_button.png")
        click_image_with_wait("../assets/delete_confirm_button.png")
        click_image_with_wait("../assets/personalization_button.png")
        click_image_with_wait("../assets/memory_button.png")
        click_image_with_wait("../assets/delete_button_memory.png")
        click_image_with_wait("../assets/reset_memory.png")
        pyautogui.press("escape")
        time.sleep(0.5)
        pyautogui.press("escape")
        
        # 5. 로그아웃 및 로그인 페이지 복귀
        if click_image_with_wait("../assets/profile_button.png"):
            if click_image_with_wait("../assets/logout_button.png"):
                time.sleep(0.5)
                if click_image_with_wait("../assets/logout_button_black.png"):
                    time.sleep(0.5)
                    if click_image_with_wait("../assets/login_button_black.png"):
                        print("[INFO] 로그인 버튼 클릭됨, 다음 계정 로그인 대기")
                        time.sleep(5)
                    else:
                        print("[ERROR] 로그인 버튼 클릭 실패. 다음 계정으로 진행 어려움")
                else:
                    print("[ERROR] 검은색 로그아웃 버튼 클릭 실패")
            else:
                print("[ERROR] 로그아웃 버튼 클릭 실패")
        else:
            print("[ERROR] 프로필 버튼 클릭 실패")

        print("[INFO] 계정 처리 완료\n")
        return True

    except Exception as e:
        print(f"[ERROR] 계정 처리 중 오류: {e}")
        return False
    finally:
        driver.quit()

def main():
    show_account_list()
    
    print("실행할 계정을 선택하세요:")
    print("예시:")
    print("  전체: 엔터만 누르기")
    print("  단일: 5")
    print("  범위: 8-20")
    print("  복수: 1,3,5")
    print("  혼합: 8-10,15,20-22")
    print("  종료: q")
    
    while True:
        selection = input("\n선택: ").strip()
        
        if selection.lower() == 'q':
            print("프로그램을 종료합니다.")
            sys.exit(0)
        
        try:
            selected_indices = parse_account_selection(selection)
            if not selected_indices:
                print("[ERROR] 유효한 계정이 선택되지 않았습니다.")
                continue
            
            selected_accounts = [(i, accounts[i]) for i in selected_indices]
            
            print(f"\n선택된 계정 ({len(selected_accounts)}개):")
            for i, acc in selected_accounts:
                print(f"  {i + 1:2d}. {acc['email']}")
            
            confirm = input("\n계속 진행하시겠습니까? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
            
            break
            
        except Exception as e:
            print(f"[ERROR] 입력 처리 중 오류: {e}")
            continue
    
    # 선택된 계정들 처리
    success_count = 0
    fail_count = 0
    
    for i, acc in selected_accounts:
        print(f"\n[INFO] === {i + 1}번째 계정 시작: {acc['email']} ===")
        print(f"[INFO] 진행률: {success_count + fail_count + 1}/{len(selected_accounts)}")
        
        try:
            if process_account(acc["email"], acc["password"]):
                success_count += 1
                print(f"[SUCCESS] {acc['email']} 처리 완료")
            else:
                fail_count += 1
                print(f"[FAIL] {acc['email']} 처리 실패")
        except Exception as e:
            fail_count += 1
            print(f"[ERROR] 계정 {acc['email']} 실패: {e}")
        
        # 마지막 계정이 아니라면 계속 진행 여부 확인
        if i != selected_indices[-1]:
            continue_choice = input("\n다음 계정을 계속 진행하시겠습니까? (y/n/q): ").strip().lower()
            if continue_choice == 'n':
                print("사용자가 중단을 선택했습니다.")
                break
            elif continue_choice == 'q':
                print("프로그램을 종료합니다.")
                break
    
    print(f"\n=== 실행 결과 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"총 처리: {success_count + fail_count}개")
    print("==================")

if __name__ == "__main__":
    main()
