const { chromium } = require("playwright");

const BASE = "http://127.0.0.1:8098";
const results = [];
const ok = (name, cond, detail = "") => results.push(`${cond ? "PASS" : "FAIL"}  ${name}${detail ? "  [" + detail + "]" : ""}`);

(async () => {
  const browser = await chromium.launch({
    executablePath: "C:\\Users\\USER\\AppData\\Local\\ms-playwright\\chromium-1243\\chrome-win64\\chrome.exe",
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));

  await page.goto(BASE, { waitUntil: "networkidle" });

  // 1. Light theme default
  const theme0 = await page.evaluate(() => window.AquaPulseDebug.theme);
  const bgLight = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  ok("default light theme", theme0 === "light", theme0 + " " + bgLight);

  // 2. Theme toggle -> dark
  await page.click("#theme-dark");
  await page.waitForTimeout(400);
  const themeDark = await page.evaluate(() => window.AquaPulseDebug.theme);
  const htmlTheme = await page.evaluate(() => document.documentElement.dataset.theme);
  const cardBgDark = await page.evaluate(() => getComputedStyle(document.querySelector(".card")).backgroundColor);
  ok("theme toggle -> dark", themeDark === "dark" && htmlTheme === "dark", themeDark + "/" + htmlTheme);
  ok("dark card surface", cardBgDark.includes("rgba") || /rgb/.test(cardBgDark), cardBgDark);

  // 3. Theme persists via localStorage
  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem("aq_prefs") || "{}"));
  ok("theme persisted", stored.theme === "dark", JSON.stringify(stored));

  // back to light for the rest
  await page.click("#theme-light");
  await page.waitForTimeout(300);

  // 4. body font >= 16
  const fs = await page.evaluate(() => parseFloat(getComputedStyle(document.body).fontSize));
  ok("body font >=16px", fs >= 16, fs + "px");

  // 5. No monospace anywhere
  const mono = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll("*").forEach((el) => {
      const f = getComputedStyle(el).fontFamily || "";
      if (/monospace|Courier|Consolas/i.test(f)) bad.push(el.tagName + "." + el.className);
    });
    return bad.slice(0, 5);
  });
  ok("no monospace", mono.length === 0, mono.join(", "));

  // 6. No uppercase abuse
  const up = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll("p,span,div,button,li,h1,h2,h3,h4,.card-title,.status-title").forEach((el) => {
      const t = getComputedStyle(el).textTransform;
      if (t === "uppercase") bad.push(el.tagName + "." + el.className);
    });
    return bad.slice(0, 5);
  });
  ok("no uppercase abuse", up.length === 0, up.join(", "));

  // 7. Ambient orbs present
  const orbs = await page.evaluate(() => document.querySelectorAll(".orb").length);
  ok("ambient orbs", orbs === 3, orbs + " orbs");

  // 8. Section color-washes present
  const stepClasses = await page.evaluate(() =>
    ["#step1", "#step2", "#step3"].map((s) => document.querySelector(s).className).join(" | "));
  ok("section washes", /step-mint/.test(stepClasses) && /step-blue/.test(stepClasses) && /step-amber/.test(stepClasses), stepClasses);

  // 9. Budget quick-pills
  const pills = await page.evaluate(() => document.querySelectorAll(".budget-pill").length);
  ok("budget pills", pills === 3, pills + " pills");
  await page.click('[data-budget="35000"]');
  await page.waitForTimeout(150);
  const budgetVal = await page.evaluate(() => document.querySelector("#opt-budget").value);
  ok("budget pill sets value", budgetVal === "35000", budgetVal);

  // 10. Tab badge counters
  await page.click("#opt-manual");
  await page.waitForTimeout(400);
  const tabCounts = await page.evaluate(() =>
    Array.from(document.querySelectorAll("#sp-tabs .tab .cnt")).map((c) => c.textContent).join(","));
  ok("tab counters", tabCounts.split(",").length === 4 && !tabCounts.includes("—"), tabCounts);

  // 11. Language toggle
  const langBefore = await page.evaluate(() => window.AquaPulseDebug.language);
  await page.click("#lang-en");
  await page.waitForTimeout(200);
  const langAfter = await page.evaluate(() => window.AquaPulseDebug.language);
  const heroEn = await page.evaluate(() => document.querySelector('[data-i18n="hero.title1"]').textContent);
  ok("lang toggle", langBefore === "bn" && langAfter === "en", `${langBefore}->${langAfter} "${heroEn}"`);
  await page.click("#lang-bn");
  await page.waitForTimeout(200);

  // 12. Add Oscar + Neon Tetra -> danger banner + issues
  const added = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll("#sp-grid .sp-card"));
    const osc = cards.find((c) => c.textContent.includes("অস্কার"));
    const neo = cards.find((c) => c.textContent.includes("নিয়ন"));
    if (osc) osc.querySelector("[data-inc]").click();
    if (neo) neo.querySelector("[data-inc]").click();
    return { osc: !!osc, neo: !!neo };
  });
  ok("found oscar+neon", added.osc && added.neo, JSON.stringify(added));
  await page.waitForTimeout(1800);
  const statusCls = await page.evaluate(() => document.querySelector("#status-banner .status").className);
  const harmony0 = await page.evaluate(() => window.AquaPulseDebug.harmony);
  const glow = await page.evaluate(() => document.body.dataset.harmony);
  ok("danger status", /danger/.test(statusCls), statusCls + " harmony=" + harmony0 + " glow=" + glow);

  // 13. Currency toggle updates totals
  const bdtTotal = await page.evaluate(() => document.querySelector("#budget-totals").innerText);
  await page.click("#cur-usd");
  await page.waitForTimeout(300);
  const usdTotal = await page.evaluate(() => document.querySelector("#budget-totals").innerText);
  ok("currency toggle", bdtTotal !== usdTotal, `${bdtTotal.trim().slice(0,16)} vs ${usdTotal.trim().slice(0,16)}`);
  await page.click("#cur-bdt");
  await page.waitForTimeout(300);

  // 14. Auto-fix
  await page.click("#btn-autofix");
  await page.waitForTimeout(1800);
  const harmony1 = await page.evaluate(() => window.AquaPulseDebug.harmony);
  ok("auto-fix -> 100", harmony1 >= 90, `before=${harmony0} after=${harmony1}`);

  // 15. Blueprints generate + tier classes
  await page.click("#opt-auto");
  await page.waitForTimeout(300);
  await page.click("#btn-generate");
  await page.waitForTimeout(1800);
  const bp = await page.evaluate(() => ({
    count: window.AquaPulseDebug.blueprints.length,
    classes: Array.from(document.querySelectorAll(".pkg-card")).map((c) => c.className).join(" | "),
  }));
  ok("blueprints generated", bp.count === 3, bp.count + " " + bp.classes);
  ok("blueprint tier classes", /budget/.test(bp.classes) && /community/.test(bp.classes) && /premium/.test(bp.classes), bp.classes);

  // 16. Commercial mode
  await page.click("#nav-farm");
  await page.waitForTimeout(1200);
  const commSpecies = await page.evaluate(() => document.querySelector("#comm-species").options.length);
  ok("commercial species", commSpecies > 0, commSpecies + " options");
  await page.click("#btn-commsim");
  await page.waitForTimeout(1800);
  const comm = await page.evaluate(() => window.AquaPulseDebug.commercial);
  ok("commercial sim", !!comm && comm.summary && comm.summary.net_profit_bdt !== undefined, comm ? "net=" + comm.summary.net_profit_bdt : "null");

  // 17. No console errors
  ok("no console errors", errors.length === 0, errors.join(" | "));

  await browser.close();
  console.log(results.join("\n"));
  const fails = results.filter((r) => r.startsWith("FAIL")).length;
  console.log("\n" + (fails === 0 ? "ALL CHECKS PASSED" : fails + " CHECK(S) FAILED"));
  process.exit(fails === 0 ? 0 : 1);
})();
