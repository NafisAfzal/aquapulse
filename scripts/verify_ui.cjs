/* node scripts/verify_ui.cjs [URL]; requires Playwright and managed Chromium.
 * Optional: PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH, UI_SCREENSHOT_DIR. */
const { chromium } = require("playwright");
const path = require("node:path");
const fs = require("node:fs");
const BASE = process.argv[2] || process.env.AQUAPULSE_URL || "http://127.0.0.1:8000";
let failures = 0, checks = 0;
function ok(name, condition, detail = "") {
  checks++;
  if (!condition) failures++;
  console.log((condition ? "PASS " : "FAIL ") + name + (detail ? " [" + detail + "]" : ""));
}
async function check(name, run) {
  try { await run(); } catch (e) { ok(name, false, e.message); }
}
(async () => {
  const browser = await chromium.launch(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
    ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {});
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    page.setDefaultTimeout(5000);
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
    await page.goto(BASE, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.locator("#lang-en").click();
    await check("four controls align", async () => {
      const tops = await page.evaluate(() => ["budget-input", "tank-size", "style-goal", "climate-preset"]
        .map(id => document.getElementById(id).getBoundingClientRect().top));
      ok("four controls align", Math.max(...tops) - Math.min(...tops) <= 4, tops.join(", "));
    });
    await check("CTA size and padding", async () => {
      const b = await page.locator("#btn-optimize").evaluate(el => {
        const r = el.getBoundingClientRect(), s = getComputedStyle(el);
        return { w:r.width, h:r.height, l:parseFloat(s.paddingLeft), r:parseFloat(s.paddingRight) };
      });
      ok("CTA size and padding", b.w >= 220 && b.h >= 48 && b.l >= 28 && b.r >= 28, JSON.stringify(b));
    });
    const top = await page.locator("#step3").evaluate(el => el.getBoundingClientRect().top + scrollY);
    ok("build options above 680px at 1440x900", top < 680, top + "px");
    const leaks = () => page.evaluate(() => document.body.innerText.replaceAll("বাংলা", "").match(/[\u0980-\u09FF]+/g) || []);
    ok("English has no Bangla text", (await leaks()).length === 0, (await leaks()).slice(0,6).join(", "));
    await check("distinct species category backgrounds", async () => {
      const fills = await page.evaluate(() => ["peaceful","plant","invert"].map(c => {
        const el = document.querySelector(".sp-card--" + c);
        return el && getComputedStyle(el).backgroundImage;
      }));
      ok("distinct species category backgrounds", fills.every(f => f && f !== "none") && new Set(fills).size === 3);
    });
    if (await page.locator("#btn-optimize").count()) {
      await page.locator('[data-tab="manual"]').click();
      ok("manual tab opens panel", await page.locator("#panel-manual").isVisible() && !await page.locator("#panel-auto").isVisible());
      await page.locator('[data-tab="wizard"]').click();
      ok("wizard tab restores panel", await page.locator("#panel-auto").isVisible());
      await page.locator('[data-budget="8000"]').click();
      await page.locator("#cur-usd").click();
      ok("USD budget pills", (await page.locator(".budget-pill").allTextContents()).join("/") === "$25/$67/$125");
      ok("USD input preserves BDT budget", Math.abs(Number(await page.locator("#budget-input").inputValue()) - 8000/120) < 0.01);
      await page.locator("#climate-preset").selectOption("winter_indoor");
      const requestPromise = page.waitForRequest(r => r.url().endsWith("/optimize-setup"));
      const responsePromise = page.waitForResponse(r => r.url().endsWith("/optimize-setup"));
      await page.locator("#btn-optimize").click();
      const request = (await requestPromise).postDataJSON(), response = await responsePromise;
      await page.waitForFunction(() => window.AquaPulseDebug.blueprints.length === 3);
      ok("optimizer gets BDT budget and selected climate", request.max_budget_bdt === 8000 && request.climate_preset === "winter_indoor", JSON.stringify(request));
      ok("three blueprints render", response.ok() && await page.locator(".pkg-card").count() === 3);
      await page.locator(".pkg-card [data-load]").first().click();
      await page.waitForFunction(() => window.AquaPulseDebug.analysis !== null && document.querySelector("#care-list").children.length === 3);
      ok("blueprint renders specs and care", await page.locator("#tank-specs tr").count() >= 8 && await page.locator("#care-list li").count() === 3);
      ok("tank liters match loaded blueprint", await page.locator("#tank-specs tr").first().innerText().then(text => text.includes("75 L")));
      ok("selected cards include quantity pills", await page.locator(".sp-card.is-selected .sp-qty-pill").count() > 0);
      await page.locator("#lang-bn").click();
      const banglaDigits = sel => page.locator(sel).first().evaluate(el => /[০-৯]/.test(el.textContent));
      ok("Bangla digits in money, quantities and specs", await banglaDigits(".sp-price") && await banglaDigits(".is-selected .val") && await banglaDigits("#tank-specs"));
      await page.locator("#lang-en").click();
      ok("English re-renders loaded results", (await leaks()).length === 0, (await leaks()).slice(0,6).join(", "));
      ok("meter IDs survive language changes", await page.locator("#space-pct").count() === 1 && await page.locator("#water-pct").count() === 1);
      await page.locator("#cur-bdt").click();
      await page.locator('[data-tab="wizard"]').click();
      await page.locator("#budget-input").fill("0");
      let invalidRequests = 0;
      const onRequest = r => { if (r.url().endsWith("/optimize-setup")) invalidRequests++; };
      page.on("request", onRequest);
      await page.locator("#btn-optimize").click();
      ok("invalid budget blocked before API", !await page.locator("#budget-input").evaluate(el => el.checkValidity()) && invalidRequests === 0);
      page.off("request", onRequest);
      await page.locator('[data-budget="8000"]').click();
      await page.emulateMedia({ media: "print" });
      ok("print includes receipt, specs and care", await page.locator("#budget-totals").isVisible() && await page.locator("#tank-specs").isVisible() && await page.locator("#care-list").isVisible());
      ok("print hides input and catalog", !await page.locator("#hero").isVisible() && !await page.locator("#sp-grid").isVisible());
      await page.emulateMedia({ media: "screen" });
      await page.setViewportSize({ width:1366, height:768 });
      ok("build options within laptop fold", await page.locator("#step3").evaluate(el => el.getBoundingClientRect().top + scrollY) < 768);
      await page.setViewportSize({ width:1440, height:900 });
      await page.keyboard.press("Tab");
      await page.locator("#btn-optimize").focus();
      ok("keyboard focus has visible outline", await page.locator("#btn-optimize").evaluate(el => getComputedStyle(el).outlineStyle !== "none"));
      await page.locator('[data-inc="oscar"]').focus();
      await page.keyboard.press("Enter");
      ok("stepper keeps keyboard focus after add", await page.evaluate(() => document.activeElement?.dataset.inc === "oscar"));
      ok("added species gets selected state", await page.locator('[data-species-id="oscar"].is-selected .sp-qty-pill').count() === 1);
      await page.locator('[data-dec="oscar"]').click();
      ok("removing last unit clears selection", await page.locator('[data-species-id="oscar"].is-selected').count() === 0);
      await page.locator('[data-tab="commercial"]').click();
      const commercialResponse = page.waitForResponse(r => r.url().endsWith("/commercial-simulate"));
      await page.locator("#btn-commsim").click();
      await commercialResponse;
      await page.waitForFunction(() => document.querySelector("#comm-table-wrap tbody tr") !== null);
      ok("commercial report renders KPIs and schedule", await page.locator("#ex-mol").isVisible() && await page.locator("#comm-table-wrap tbody tr").count() > 0);
      await page.setViewportSize({ width:390, height:844 });
      ok("commercial view has no mobile overflow", await page.evaluate(() => document.documentElement.scrollWidth <= 390));
      await page.locator("#nav-home").click();
    }
    await page.setViewportSize({ width:390, height:844 });
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    ok("no overflow at 390x844", width <= 390, width + "px");
    ok("mobile species grid is single column", await page.locator("#sp-grid").evaluate(el => getComputedStyle(el).gridTemplateColumns.split(" ").length === 1));
    if (process.env.UI_SCREENSHOT_DIR) {
      fs.mkdirSync(process.env.UI_SCREENSHOT_DIR, { recursive:true });
      for (const theme of ["light","dark"]) {
        await page.locator("#theme-" + theme).click();
        for (const [device,width,height] of [["desktop",1440,900],["mobile",390,844]]) {
          await page.setViewportSize({ width,height });
          await page.evaluate(() => window.scrollTo({ top:0, behavior:"instant" }));
          await page.screenshot({ path:path.join(process.env.UI_SCREENSHOT_DIR, device + "-" + theme + ".png") });
          if (device === "desktop") {
            await page.locator("#care-sheet").screenshot({ path:path.join(process.env.UI_SCREENSHOT_DIR, "receipt-" + theme + ".png") });
            await page.locator(".sp-card").first().screenshot({ path:path.join(process.env.UI_SCREENSHOT_DIR, "species-" + theme + ".png") });
          }
        }
      }
    }
    // Isolate expected HTTP failures so they cannot mask errors in normal flows.
    const failurePage = await context.newPage();
    await failurePage.goto(BASE, { waitUntil:"networkidle" });
    await failurePage.locator("#lang-en").click();
    await failurePage.route("**/optimize-setup", route => route.fulfill({ status:503, contentType:"application/json", body:JSON.stringify({detail:"Temporarily unavailable"}) }));
    await failurePage.locator("#btn-optimize").click();
    await failurePage.waitForFunction(() => !document.querySelector("#btn-optimize").disabled);
    ok("optimizer failure shows error and restores button", (await failurePage.locator("#toast").innerText()).includes("Temporarily unavailable"));
    await failurePage.unroute("**/optimize-setup");
    await failurePage.route("**/optimize-setup", route => route.fulfill({ status:200, contentType:"application/json", body:JSON.stringify({blueprints:[]}) }));
    await failurePage.locator("#btn-optimize").click();
    await failurePage.waitForFunction(() => !document.querySelector("#btn-optimize").disabled);
    ok("empty optimizer response offers recovery", (await failurePage.locator("#toast").innerText()).includes("try a higher budget") && await failurePage.locator(".pkg-card").count() === 0);
    await failurePage.close();
    ok("no browser runtime or console errors", errors.length === 0, errors.join(" | "));
    await context.close();
  } finally { await browser.close(); }
  console.log((checks - failures) + "/" + checks + " checks passed");
  process.exitCode = failures ? 1 : 0;
})().catch(e => { console.error("FAIL verification stopped: " + e.stack); process.exitCode = 1; });
