// openai_momail_auth.js
const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");
const { EMAIL, PASSWORD } = require("./loginInfo.js");

puppeteer.use(StealthPlugin());

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
  });
  const [momailPage] = await browser.pages();

  console.log("[INFO] momail.kr 로그인 중...");
  await momailPage.goto("https://momail.kr", { waitUntil: "networkidle2" });
  await momailPage.waitForSelector(
    'input[placeholder="예: example@momail.kr"]'
  );
  await momailPage.type('input[placeholder="예: example@momail.kr"]', EMAIL, {
    delay: 100,
  });
  await momailPage.type("#passwordField", PASSWORD, { delay: 100 });
  await momailPage.click('button[aria-label="Connect"]');
  console.log("[INFO] momail 로그인 완료");

  // OpenAI 로그인
  const openaiPage = await browser.newPage();
  await openaiPage.goto("https://auth.openai.com/log-in", {
    waitUntil: "networkidle2",
  });
  console.log("[INFO] OpenAI 로그인 시작");
  await openaiPage.waitForSelector('input[type="email"]');
  await openaiPage.type('input[type="email"]', EMAIL, { delay: 100 });
  await openaiPage.click('button[type="submit"][name="intent"][value="email"]');

  await openaiPage.waitForSelector('input[type="password"]');
  await openaiPage.type('input[type="password"]', PASSWORD, { delay: 100 });
  await openaiPage.click('button[type="submit"]');

  console.log("[INFO] 이메일/비밀번호 입력 완료, 인증코드 대기...");

  // momail에서 인증코드 대기
  await momailPage.bringToFront();
  await momailPage.waitForTimeout(5000);

  let code = null;
  try {
    const messageSelector =
      "#messagesList md-list md-list-item:nth-child(1) div[ng-bind-html]";
    await momailPage.waitForSelector(messageSelector, { timeout: 10000 });
    const messageText = await momailPage.$eval(
      messageSelector,
      (el) => el.innerText
    );
    const match = messageText.match(/\b(\d{6})\b/);
    if (match) {
      code = match[1];
      console.log(`[INFO] 인증코드 감지됨: ${code}`);
    }
  } catch (err) {
    console.log("[ERROR] 인증 메일을 찾을 수 없습니다.");
    await browser.close();
    return;
  }

  // 인증코드 입력
  if (code) {
    await openaiPage.bringToFront();
    await openaiPage.waitForSelector('input[name="code"]');
    await openaiPage.type('input[name="code"]', code, { delay: 100 });
    await openaiPage.click('button[type="submit"]');
    console.log("[INFO] 인증 완료 시도");
  }

  // 인증 결과 확인 대기
  await openaiPage.waitForTimeout(5000);
  await browser.close();
})();
