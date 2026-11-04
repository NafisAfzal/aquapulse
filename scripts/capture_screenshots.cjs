// npm run screenshots -- http://127.0.0.1:8000
const { chromium } = require("playwright");
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");

async function main() {
  const destination = path.resolve(__dirname, "../docs");
  fs.mkdirSync(destination, { recursive: true });
  const browser = await chromium.launch(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
    ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {});
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const response = await page.goto(process.argv[2] || process.env.AQUAPULSE_URL || "http://127.0.0.1:8000", { waitUntil: "networkidle" });
    assert.ok(response.ok(), "Application must respond successfully");
    await page.locator("#lang-en").click();
    await page.locator(".sp-card").first().waitFor();
    await page.evaluate(() => document.fonts.ready);
    for (const theme of ["light", "dark"]) {
      await page.locator(`#theme-${theme}`).click();
      await page.waitForFunction(value => document.documentElement.dataset.theme === value, theme);
      await page.mouse.move(0, 0);
      // Allow button feedback and theme styles to settle before the capture.
      await page.waitForTimeout(1000);
      const filename = path.join(destination, `${theme}-theme.png`);
      await page.screenshot({ path: filename, fullPage: false, animations: "disabled" });
      const png = fs.readFileSync(filename);
      assert.equal(png.subarray(0, 8).toString("hex"), "89504e470d0a1a0a");
      assert.equal(png.readUInt32BE(16), 1440);
      assert.equal(png.readUInt32BE(20), 900);
      assert.ok(png.length > 20 * 1024, "Screenshot must exceed 20 KB");
      console.log(`Saved ${path.relative(process.cwd(), filename)} (1440 x 900, ${png.length} bytes)`);
    }
    assert.deepEqual(errors, [], "No application runtime errors during capture");
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
