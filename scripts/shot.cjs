const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({
    executablePath: "C:\\Users\\USER\\AppData\\Local\\ms-playwright\\chromium-1243\\chrome-win64\\chrome.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto("http://127.0.0.1:8098", { waitUntil: "networkidle" });
  await page.evaluate(() => { localStorage.removeItem("aq_prefs"); });
  await page.reload({ waitUntil: "networkidle" });
  await page.screenshot({ path: "docs/ui-v4-light.png", fullPage: false });
  await page.click("#theme-dark");
  await page.waitForTimeout(500);
  await page.screenshot({ path: "docs/ui-v4-dark.png", fullPage: false });
  // also capture the full page light for a wide view
  await page.click("#theme-light");
  await page.waitForTimeout(400);
  await page.screenshot({ path: "docs/ui-v4-light-full.png", fullPage: true });
  await browser.close();
  console.log("screenshots done");
})();
