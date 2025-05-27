## 문제: 모달창이나 드롭다운 요소를 DevTools에서 확인하려고 하면 사라짐

### 상황
- 모달, Select Box, 드롭다운 등 일시적으로 표시되는 UI 요소를 DevTools에서 확인하고 싶음
- Elements 탭을 열거나 마우스를 움직이는 순간 해당 요소가 사라짐

---

## 원인
- 해당 UI 요소는 JavaScript로 동적으로 렌더링되며, 외부 클릭 또는 포커스 이동 시 사라지도록 되어 있음
- F8(Pause script execution) 등으로 스크립트를 멈추면, 아직 DOM에 붙기 전이거나 transition 중이어서 제대로 표시되지 않거나 사라짐

---

## 해결 방법: `setTimeout` + `debugger` 사용

### 단계별 실행

1. 콘솔에 아래 코드 입력
   ```js
   setTimeout(() => { debugger; }, 3000);
   ```
2. 엔터를 입력한 뒤 3초 안에 모달 또는 드롭다운을 띄움
3. 3초 후 자동으로 JavaScript 실행이 중단됨
4. 이 상태에서 Elements 탭으로 이동하면 해당 요소가 사라지지 않고 DOM에서 확인 가능

![Image](https://github.com/user-attachments/assets/b1a2aaa6-f13c-4bc3-a5c2-7bb74908a0ab)