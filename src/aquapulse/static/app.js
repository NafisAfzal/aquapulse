/* ============================================================
   AquaPulse Pro v1.0.0 - friendly, bilingual consumer UI
   Pure vanilla JS. No frameworks. i18n dictionary in both
   Bangla (bn) and English (en).
   ============================================================ */
"use strict";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

/* ---------------- Bangla / English dictionary ---------------- */
const I18N = {
  en: {
    "brand.tag": "Your friendly aquarium guide",
    "nav.home": "🏠 Home Aquarium",
    "nav.farm": "🚜 Commercial Fish Farming Calculator",
    "hero.kicker": "🐠 Priced for the Bangladesh market",
    "hero.title": "Plan a beautiful aquarium — easily, worry-free.",
    "hero.title1": "Plan a beautiful aquarium,",
    "hero.title2": "easily and worry-free.",
    "hero.sub": "Know which fish can live together and exactly what it costs — a package for your budget, at Dhaka market prices.",
    "hero.b1": "100% compatible fish",
    "hero.b2": "Real Dhaka prices",
    "hero.b3": "Simple care guide",
    "s1.label": "Step 1",
    "s1.title": "How shall we build your tank?",
    "s1.desc": "Two easy ways — tell us your budget and we'll set it up, or pick your own fish.",
    "opt.a.title": "Smart Budget Architect",
    "opt.a.desc": "Tell us your budget and tank size — get 3 ready packages and pick your favourite.",
    "opt.b.title": "Custom Workbench",
    "opt.b.desc": "Pick fish, plants and cleaners yourself — we'll check if they get along.",
    "auto.title": "Find the best setup for you",
    "auto.sub": "Answer 3 quick questions, that's it!",
    "auto.budget": "Budget (BDT)",
    "auto.budget.usd": "Budget (USD)",
    "currency.bdt": "BDT",
    "climate.summer": "Tropical Summer (30–33°C)",
    "climate.winter": "Winter Indoor (18–20°C)",
    "climate.controlled": "Climate Controlled (24–25°C)",
    "auto.size": "Tank size",
    "auto.size.small": "Small (20 L)",
    "auto.size.med": "Medium (40 L)",
    "auto.size.large": "Large (75 L)",
    "auto.size.xl": "Extra Large (150 L)",
    "auto.style": "What kind of tank do you want?",
    "auto.goal1": "Calm, colorful community fish",
    "auto.goal2": "Easy, low-maintenance tank",
    "auto.goal3": "Vibrant centerpiece",
    "auto.goal4": "Shrimp breeding colony",
    "auto.btn": "🔍 Find the Best Setup for Me",
    "auto.pick": "Select This Setup",
    "mode.wizard": "Auto-Architect",
    "mode.manual": "Manual Planner",
    "mode.commercial": "Commercial",
    "auto.tanksize": "Tank size (liters)",
    "auto.goal": "What kind of tank do you want?",
    "auto.climate": "Climate",
    "btn.analyze": "Generate Setup",
    "btn.simulate": "Simulate",
    "results.title": "Your Build Options",
    "results.sub": "Three ranked blueprints - pick your favourite.",
    "saved.title": "Saved Builds",
    "catalog.title": "Species Catalog",
    "catalog.sub": "Browse compatible fish, shrimp, snails and plants.",
    "pick.title": "Pick your fish, plants and cleaners",
    "pick.sub": "Tap + to add more of each.",
    "pick.search": "Search by name…",
    "pick.all": "All",
    "pick.fish": "Colorful Fish",
    "pick.clean": "Shrimp & Snails",
    "pick.plant": "Live Plants",
    "s2.label": "Step 2",
    "s2.title": "Your Tank Checkup",
    "s2.desc": "See if your fish can live together, and whether the tank has enough space.",
    "status.ok.title": "✅ All fish will live happily together!",
    "status.ok.body": "These fish are a great match — nice choice!",
    "status.warn.title": "⚠️ A few small issues",
    "status.warn.body": "There are minor problems — check the tips below.",
    "status.danger.title": "❌ Caution — these fish may fight!",
    "status.danger.body": "Some fish may nip, fight or hurt each other. Review the list below.",
    "autofix.btn": "🔧 One-Click Auto-Fix My Tank",
    "autofix.done": "Auto-fixed! Tap the suggestions below if you want to adjust further.",
    "issues.empty": "Everything looks good — no problems found.",
    "meters.space": "Tank Space & Health",
    "meters.water": "Water Safety",
    "water.title": "Water Cleanliness Forecast",
    "water.more": "See the detailed 30-day forecast",
    "chart.nh3": "Toxic Ammonia",
    "chart.no2": "Nitrite",
    "chart.no3": "Nitrate (plant food)",
    "s3.label": "Step 3",
    "s3.title": "Shopping List & Care Guide",
    "s3.desc": "Take this list to the shop, or print it out.",
    "receipt.title": "🧾 Shopping List",
    "receipt.sub": "Fish, plants and equipment — all priced together.",
    "receipt.fish": "Fish & Plants",
    "receipt.equip": "Equipment",
    "care.title": "3 Golden Care Rules",
    "tank.specs.title": "🧪 Tank Specifications",
    "btn.download": "⬇ Download List",
    "btn.print": "🖨 Print Care Sheet",
    "farm.title": "Commercial Fish Farming Profit Calculator",
    "farm.sub": "Biofloc, RAS or pond — know your cost and profit before you start. Chita gur dosing included.",
    "farm.params": "Enter your culture details",
    "farm.params.sub": "Pick the species and system — the calculation updates instantly.",
    "farm.species": "Fish species",
    "farm.system": "System type",
    "farm.sys1": "Biofloc Tank",
    "farm.sys2": "RAS",
    "farm.sys3": "Semi-Intensive Pond",
    "farm.volume": "Water volume (liters)",
    "farm.count": "Number of fingerlings",
    "farm.init": "Fingerling weight (g)",
    "farm.target": "Harvest weight (g)",
    "farm.days": "Culture days",
    "farm.temp": "Water temperature (°C)",
    "farm.feed": "Feed price (BDT/kg)",
    "farm.fry": "Fingerling price (BDT/pc)",
    "farm.price": "Market price (BDT/kg)",
    "farm.ph": "pH",
    "farm.run": "📊 Calculate",
    "kpi.net": "Net Profit",
    "kpi.roi": "Return (ROI)",
    "kpi.roi.s": "% profit on cost",
    "kpi.feed": "Daily Feed",
    "kpi.mol": "Molasses (Chita Gur) Dose",
    "kpi.mol.s": "to keep water safe",
    "kpi.nh3": "Toxic Ammonia",
    "kpi.air": "Air Pump Needed",
    "kpi.air.s": "liters/minute",
    "farm.chart": "Fish Growth vs. Feed",
    "farm.chart1": "Total fish weight (kg)",
    "farm.chart2": "Daily feed (kg)",
    "farm.schedule": "Weekly Schedule",
    "farm.schedule.sub": "Weekly weight, feed and water condition.",
    "footer": "This tool is for guidance only — please consult an expert before deciding.",
  },
  bn: {
    "brand.tag": "সহজ অ্যাকোয়ারিয়াম পরামর্শ",
    "nav.home": "🏠 বাসার অ্যাকোয়ারিয়াম",
    "nav.farm": "🚜 বাণিজ্যিক মাছ চাষ ক্যালকুলেটর",
    "hero.kicker": "🐠 বাংলাদেশের বাজারের দামে বানানো",
    "hero.title": "সুন্দর সামঞ্জস্যপূর্ণ অ্যাকোয়ারিয়াম বানান — সহজে, নিশ্চিন্তে।",
    "hero.title1": "সুন্দর অ্যাকোয়ারিয়াম বানান,",
    "hero.title2": "সহজে আর নিশ্চিন্তে।",
    "hero.sub": "কোন মাছ একসাথে বাঁচবে, আর কত খরচ হবে — সব আগেই জেনে নিন। বাজেট অনুযায়ী প্যাকেজ, ঢাকার বাজারদরে।",
    "hero.b1": "১০০% মানানসই মাছ",
    "hero.b2": "ঢাকার সঠিক দাম",
    "hero.b3": "সহজ বাংলায় যত্ন",
    "s1.label": "ধাপ ১",
    "s1.title": "আপনার ট্যাংক কীভাবে বানাবো?",
    "s1.desc": "দুটি সহজ উপায় — বাজেট বলুন, আমরা সাজিয়ে দেবো। অথবা নিজের পছন্দমতো মাছ বেছে নিন।",
    "opt.a.title": "স্মার্ট বাজেট আর্কিটেক্ট",
    "opt.a.desc": "বাজেট আর সাইজ বললেই ৩টি রেডি প্যাকেজ — বেছে নিন যেটা ভালো লাগে।",
    "opt.b.title": "কাস্টম ওয়ার্কবেঞ্চ",
    "opt.b.desc": "নিজে মাছ, গাছ আর ক্লিনার বাছুন — আমরা মানানসই কি না দেখে দেবো।",
    "auto.title": "আপনার জন্য সেরা সেটআপ খুঁজছি",
    "auto.sub": "৩টি প্রশ্নের উত্তর দিন, ব্যস!",
    "auto.budget": "আপনার বাজেট (৳ টাকা)",
    "auto.budget.usd": "বাজেট (USD)",
    "currency.bdt": "৳ BDT",
    "climate.summer": "গ্রীষ্মের ঘর (৩০–৩৩°C)",
    "climate.winter": "শীতের ঘর (১৮–২০°C)",
    "climate.controlled": "নিয়ন্ত্রিত তাপমাত্রা (২৪–২৫°C)",
    "auto.size": "ট্যাংকের সাইজ",
    "auto.size.small": "ছোট (২০ লিটার)",
    "auto.size.med": "মাঝারি (৪০ লিটার)",
    "auto.size.large": "বড় (৭৫ লিটার)",
    "auto.size.xl": "খুব বড় (১৫০ লিটার)",
    "auto.style": "কেমন ট্যাংক চান?",
    "auto.goal1": "শান্ত আর রঙিন মাছের ট্যাংক",
    "auto.goal2": "সহজ, কম যত্নের ট্যাংক",
    "auto.goal3": "আকর্ষণীয় প্রধান মাছের ট্যাংক",
    "auto.goal4": "চিংড়ি প্রজননের ট্যাংক",
    "auto.btn": "🔍 আমার জন্য সেরা সেটআপ খুঁজুন",
    "auto.pick": "এই সেটআপটি বেছে নিন",
    "mode.wizard": "স্মার্ট আর্কিটেক্ট",
    "mode.manual": "ম্যানুয়াল প্ল্যানার",
    "mode.commercial": "বাণিজ্যিক",
    "auto.tanksize": "ট্যাংকের সাইজ (লিটার)",
    "auto.goal": "কেমন ট্যাংক চান?",
    "auto.climate": "জলবায়ু",
    "btn.analyze": "সেটআপ তৈরি করুন",
    "btn.simulate": "সিমুলেট করুন",
    "results.title": "আপনার বিল্ড অপশনগুলো",
    "results.sub": "তিনটি র্যাঙ্ক করা ব্লুপ্রিন্ট — পছন্দমতো বাছুন।",
    "saved.title": "সংরক্ষিত বিল্ডগুলো",
    "catalog.title": "প্রজাতির তালিকা",
    "catalog.sub": "সামঞ্জস্যপূর্ণ মাছ, চিংড়ি, শামুক আর গাছ ব্রাউজ করুন।",
    "pick.title": "মাছ, গাছ আর ক্লিনার বাছুন",
    "pick.sub": "প্রতিটি কার্ডে + চেপে সংখ্যা বাড়ান।",
    "pick.search": "নাম লিখে খুঁজুন…",
    "pick.all": "সব",
    "pick.fish": "রঙিন মাছ",
    "pick.clean": "চিংড়ি ও শামুক",
    "pick.plant": "পানির গাছ",
    "s2.label": "ধাপ ২",
    "s2.title": "আপনার ট্যাংকের চেকআপ",
    "s2.desc": "মাছগুলো একসাথে থাকতে পারবে কি না, আর ট্যাংকে জায়গার অভাব আছে কি না — সব এখানে।",
    "status.ok.title": "✅ সব মাছ একসাথে মিলেমিশে থাকবে!",
    "status.ok.body": "এই মাছগুলো একসাথে সুখে থাকতে পারবে। দারুণ বাছাই!",
    "status.warn.title": "⚠️ কিছুটা সমস্যা হতে পারে",
    "status.warn.body": "ছোটখাটো সমস্যা আছে — নিচের পরামর্শগুলো দেখুন।",
    "status.danger.title": "❌ সতর্কতা! এই মাছগুলো একসাথে রাখলে মারা যেতে পারে",
    "status.danger.body": "কিছু মাছ লড়াই করতে পারে বা একে অপরকে কষ্ট দিতে পারে। নিচের তালিকাটি দেখুন।",
    "autofix.btn": "🔧 এক ক্লিকে সমস্যা সমাধান করুন",
    "autofix.done": "সমাধান করা হয়েছে! আরও বদলাতে চাইলে নিচের পরামর্শগুলো দেখুন।",
    "issues.empty": "সব ঠিক আছে — কোনো সমস্যা পাওয়া যায়নি।",
    "meters.space": "ট্যাংক জায়গা ও রোগ",
    "meters.water": "পানির নিরাপত্তা",
    "water.title": "পানি পরিষ্কার রাখার গাইড",
    "water.more": "বিস্তারিত ৩০ দিনের হিসাব দেখুন",
    "chart.nh3": "বিষাক্ত অ্যামোনিয়া",
    "chart.no2": "নাইট্রাইট",
    "chart.no3": "নাইট্রেট (গাছের খাবার)",
    "s3.label": "ধাপ ৩",
    "s3.title": "মোট খরচ ও বাজারের লিস্ট",
    "s3.desc": "এই লিস্টটি নিয়ে দোকানে যান, অথবা প্রিন্ট করে নিন।",
    "receipt.title": "🧾 কেনাকাটার লিস্ট",
    "receipt.sub": "মাছ, গাছ ও সরঞ্জামের দাম একসাথে।",
    "receipt.fish": "মাছ ও গাছ",
    "receipt.equip": "যন্ত্রপাতি",
    "care.title": "যত্নের ৩টি নিয়ম",
    "tank.specs.title": "🧪 ট্যাংকের স্পেসিফিকেশন",
    "btn.download": "⬇ লিস্ট ডাউনলোড করুন",
    "btn.print": "🖨 কেয়ার শিট প্রিন্ট করুন",
    "farm.title": "বাণিজ্যিক মাছ চাষ আয় ক্যালকুলেটর",
    "farm.sub": "বায়োফ্লক, আরএএস বা পুকুর — কত লাগবে, কত আয় হবে, আগেই জেনে নিন। চিটাগুড়ের হিসাব একসাথে।",
    "farm.params": "চাষের তথ্য দিন",
    "farm.params.sub": "পদ্ধতি আর মাছের জাত বাছলেই হিসাব বদলে যাবে।",
    "farm.species": "মাছের জাত",
    "farm.system": "পদ্ধতি",
    "farm.sys1": "বায়োফ্লক ট্যাংক",
    "farm.sys2": "আরএএস (RAS)",
    "farm.sys3": "আধা-নিবিড় পুকুর",
    "farm.volume": "পানির পরিমাণ (লিটার)",
    "farm.count": "পোনা সংখ্যা",
    "farm.init": "পোনার ওজন (গ্রাম)",
    "farm.target": "বিক্রয়ের ওজন (গ্রাম)",
    "farm.days": "কত দিন চাষ করবেন",
    "farm.temp": "পানির তাপমাত্রা (°সে)",
    "farm.feed": "খাবারের দাম (৳/কেজি)",
    "farm.fry": "পোনার দাম (৳/পিস)",
    "farm.price": "বাজার দাম (৳/কেজি)",
    "farm.ph": "pH",
    "farm.run": "📊 হিসাব করুন",
    "kpi.net": "মোট লাভ",
    "kpi.roi": "রিইটার্ন (ROI)",
    "kpi.roi.s": "খরচার শতকরা লাভ",
    "kpi.feed": "দৈনিক খাবার",
    "kpi.mol": "গুড়ের পরিমাণ",
    "kpi.mol.s": "বিষ কমানোর জন্য (চিটাগুড়)",
    "kpi.nh3": "বিষাক্ত অ্যামোনিয়া",
    "kpi.air": "এয়ার পাম্প লাগবে",
    "kpi.air.s": "লিটার/মিনিট",
    "farm.chart": "মাছের বাড়ার হিসাব",
    "farm.chart1": "মোট মাছের ওজন (কেজি)",
    "farm.chart2": "দৈনিক খাবার (কেজি)",
    "farm.schedule": "সপ্তাহভিত্তিক শিডিউল",
    "farm.schedule.sub": "প্রতি সপ্তাহে মাছের ওজন, খাবার ও পানির অবস্থা।",
    "footer": "এই তথ্য শুধুমাত্র পরামর্শের জন্য — চূড়ান্ত সিদ্ধান্তে বিশেষজ্ঞের পরামর্শ নিন।",
  },
};

/* ---------------- Species meta (Bangla names + emoji + temper) ---------------- */
const SPECIES_META = {
  neon_tetra:       { bn: "নিয়ন টেট্রা",       en: "Neon Tetra",       emoji: "🦐" },
  guppy:            { bn: "গাপ্পি",             en: "Guppy",            emoji: "🐠" },
  molly:            { bn: "মলি",               en: "Molly",            emoji: "🐟" },
  platy:            { bn: "প্লাটি",             en: "Platy",            emoji: "🐟" },
  angelfish:        { bn: "অ্যাঞ্জেল ফিশ",      en: "Angel Fish",       emoji: "🐠" },
  discus:           { bn: "ডিসকাস",            en: "Discus",           emoji: "🐟" },
  oscar:            { bn: "অস্কার",             en: "Oscar",            emoji: "🐟" },
  betta:            { bn: "ফাইটার মাছ",         en: "Betta Fighter",    emoji: "🐠" },
  corydoras:        { bn: "কোরিডোরাস",          en: "Corydoras",        emoji: "🐟" },
  zebra_danio:      { bn: "জেব্রা ড্যানিও",     en: "Zebra Danio",      emoji: "🐟" },
  gourami:          { bn: "গৌরামি",             en: "Gourami",          emoji: "🐟" },
  tetra_blackskirt: { bn: "ব্ল্যাক টেট্রা",      en: "Black Skirt Tetra", emoji: "🐟" },
  goldfish:         { bn: "গোল্ডফিশ",           en: "Goldfish",         emoji: "🐠" },
  pleco:            { bn: "প্লেকো",             en: "Bristlenose Pleco", emoji: "🐟" },
  cherry_shrimp:    { bn: "চেরি শ্রিম্প",        en: "Cherry Shrimp",    emoji: "🦐" },
  amano_shrimp:     { bn: "আমানো শ্রিম্প",       en: "Amano Shrimp",     emoji: "🦐" },
  mystery_snail:    { bn: "মিস্টারি শামুক",      en: "Mystery Snail",    emoji: "🐌" },
  nerite_snail:     { bn: "নেরাইট শামুক",       en: "Nerite Snail",     emoji: "🐌" },
  anubias:          { bn: "আনুবিয়াস",           en: "Anubias",          emoji: "🌿" },
  java_fern:        { bn: "জাভা ফার্ন",          en: "Java Fern",        emoji: "🌿" },
  hornwort:         { bn: "হর্নওয়ার্ট",         en: "Hornwort",         emoji: "🌿" },
  java_moss:        { bn: "জাভা মস",             en: "Java Moss",        emoji: "🌿" },
  anacharis:        { bn: "অ্যানাকারিস",         en: "Anacharis",        emoji: "🌿" },
};

/* ---------------- State ---------------- */
const state = {
  lang: "bn",
  currency: "BDT",
  theme: "light",
  view: "home",
  species: [],
  stocking: new Map(),
  analysis: null,
  currentBlueprint: null,
  cycleSteps: null,
  blueprints: [],
  commercial: null,
  exchangeRate: 120,
  spFilter: "all",
  spSearch: "",
  budgetBdt: 8000,
  panel: "auto",
};

/* ---------------- i18n helpers ---------------- */
function t(key) { return (I18N[state.lang] && I18N[state.lang][key]) || (I18N.en[key]) || key; }
function applyI18n() {
  document.documentElement.lang = state.lang;
  $("#toast").textContent = "";
  $("#toast").classList.remove("show");
  document.body.dataset.lang = state.lang;
  $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
  document.title = state.lang === "bn" ? "AquaPulse Pro · আপনার অ্যাকোয়ারিয়াম, সহজ ও সুন্দর"
                                        : "AquaPulse Pro · Plan your aquarium beautifully";
  renderBudgetControls();
}

// Localize display text only. Input values and API payloads remain numeric.
function localizeDigits(value) {
  return String(value).replace(/[0-9০-৯]/g, (digit) => {
    const n = digit >= "০" ? digit.charCodeAt(0) - "০".charCodeAt(0) : Number(digit);
    return state.lang === "bn" ? "০১২৩৪৫৬৭৮৯"[n] : String(n);
  });
}
function formatNum(value, fractionDigits = 0) {
  if (value == null || value === "" || !Number.isFinite(Number(value))) return "—";
  return Number(value).toLocaleString(state.lang === "bn" ? "bn-BD" : "en-IN", {
    minimumFractionDigits: fractionDigits, maximumFractionDigits: fractionDigits,
  });
}
function bdtPrefix() { return state.lang === "bn" ? "৳" : "BDT "; }

function renderBudgetControls(updateInput = false) {
  const input = $("#budget-input");
  const usd = state.currency === "USD";
  $("label[for='budget-input']").textContent = t(usd ? "auto.budget.usd" : "auto.budget");
  input.min = usd ? (500 / state.exchangeRate).toFixed(2) : "500";
  input.max = usd ? (200000 / state.exchangeRate).toFixed(2) : "200000";
  input.step = usd ? "0.01" : "1";
  if (updateInput) input.value = usd ? (state.budgetBdt / state.exchangeRate).toFixed(2) : String(state.budgetBdt);
  $$(".budget-pill").forEach((pill) => {
    const bdt = Number(pill.dataset.budget);
    pill.textContent = usd ? "$" + formatNum(bdt / state.exchangeRate) : bdtPrefix() + formatNum(bdt);
    const active = Math.abs(state.budgetBdt - bdt) < 0.01;
    pill.classList.toggle("active", active);
    pill.setAttribute("aria-pressed", String(active));
  });
}

/* ---------------- Theme engine ---------------- */
function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.dataset.theme = theme;
  $("#theme-light").classList.toggle("active", theme === "light");
  $("#theme-dark").classList.toggle("active", theme === "dark");
  savePrefs();
}

/* ---------------- Persistent preferences ---------------- */
function savePrefs() {
  try { localStorage.setItem("aq_prefs", JSON.stringify({ theme: state.theme, lang: state.lang, currency: state.currency })); } catch (_) {}
}
function loadPrefs() {
  try {
    const p = JSON.parse(localStorage.getItem("aq_prefs") || "{}");
    if (p.theme) state.theme = p.theme;
    if (p.lang) state.lang = p.lang;
    if (p.currency) state.currency = p.currency;
  } catch (_) {}
}

/* ---------------- API ---------------- */
async function api(path, body) {
  const opts = body === undefined
    ? { method: "GET" }
    : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const res = await fetch(path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

/* ---------------- Currency formatting ---------------- */
function fmtMoney(usd) {
  if (state.currency === "BDT") return fmtMoneyBdt(usd);
  return "$" + formatNum(usd, 2);
}
function fmtMoneyBdt(usd) { return bdtPrefix() + formatNum(usd * state.exchangeRate); }

function spName(id) {
  const meta = SPECIES_META[id];
  if (!meta) return id;
  return state.lang === "bn" ? meta.bn : meta.en;
}
function sp(speciesId) { return state.species.find((s) => s.id === speciesId); }
function stockingList() {
  return Array.from(state.stocking.entries()).filter(([, c]) => c > 0).map(([id, count]) => ({ species_id: id, count }));
}
function totalStock() { let n = 0; state.stocking.forEach((c) => n += c); return n; }

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(el._h);
  el._h = setTimeout(() => el.classList.remove("show"), 3200);
}

/* ============================================================
   RENDERING
   ============================================================ */

/* ---- Species grid (manual pick) ---- */
function renderSpeciesGrid() {
  const grid = $("#sp-grid");
  const focused = document.activeElement;
  const focusKey = focused?.hasAttribute("data-inc") ? "inc" : focused?.hasAttribute("data-dec") ? "dec" : null;
  const focusSpecies = focusKey ? focused.dataset[focusKey] : null;
  grid.innerHTML = "";
  const q = state.spSearch.trim().toLowerCase();
  const filtered = state.species.filter((s) => {
    if (state.spFilter !== "all" && s.category !== state.spFilter) return false;
    if (!q) return true;
    return (s.name.toLowerCase().includes(q) || (SPECIES_META[s.id] && (SPECIES_META[s.id].bn.includes(q) || SPECIES_META[s.id].en.toLowerCase().includes(q))));
  });

  filtered.forEach((s) => {
    const meta = SPECIES_META[s.id] || { bn: s.name, en: s.name, emoji: s.emoji || "🐟" };
    const count = state.stocking.get(s.id) || 0;
    const temper = s.category === "plant" ? "neutral"
      : s.category === "invertebrate" ? "cleaner"
      : (s.aggression_rating >= 0.4 || s.fin_nipper) ? "aggressive" : "peaceful";
    const badge = temper === "peaceful" ? (state.lang === "bn" ? "শান্ত" : "Peaceful")
      : temper === "aggressive" ? (state.lang === "bn" ? "রাগী / আগ্রাসী" : "Aggressive")
      : temper === "neutral" ? (state.lang === "bn" ? "পানির গাছ" : "Plant")
      : (state.lang === "bn" ? "পানি পরিষ্কার রাখে" : "Cleaner");

    const card = document.createElement("div");
    const category = s.category === "plant" ? "plant" : s.category === "invertebrate" ? "invert"
      : s.aggression_rating >= 0.7 ? "aggressive" : temper === "aggressive" ? "semi" : "peaceful";
    card.className = `sp-card sp-card--${category}${count > 0 ? " is-selected" : ""}`;
    card.dataset.speciesId = s.id;
    card.innerHTML = `
      ${count > 0 ? `<span class="sp-qty-pill">×${formatNum(count)}</span>` : ""}
      <div class="sp-head">
        <div class="sp-emoji">${meta.emoji}</div>
        <div>
          <div class="sp-name">${state.lang === "bn" ? meta.bn : meta.en}</div>
          <div class="sp-sci">${s.scientific_name}</div>
        </div>
      </div>
      <div class="sp-desc">${s.description}</div>
      <div class="sp-meta">
        <span class="sp-price">${fmtMoney(s.price_usd)}</span>
        <span class="sp-badge ${temper}">${badge}</span>
      </div>
      <div class="stepper">
        <span class="sp-size">${localizeDigits(s.size_cm)} cm · ${state.lang === "bn" ? "ট্যাংক" : "tank"} ≥${formatNum(s.min_tank_gal)} gal</span>
        <div class="stepper-btns">
          <button data-dec="${s.id}" aria-label="decrease">−</button>
          <span class="val">${formatNum(count)}</span>
          <button data-inc="${s.id}" aria-label="increase">+</button>
        </div>
      </div>`;
    card.querySelector('[data-inc]').onclick = () => { bump(s.id, +1); };
    card.querySelector('[data-dec]').onclick = () => { bump(s.id, -1); };
    grid.appendChild(card);
  });

  if (!filtered.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;color:#64748B;text-align:center;padding:30px">${state.lang === "bn" ? "কোনো কিছু পাওয়া যায়নি" : "Nothing found"}</div>`;
  }
  updateTabCounts();
  if (focusKey) grid.querySelector(`[data-${focusKey}="${CSS.escape(focusSpecies)}"]`)?.focus({ preventScroll: true });
}

/* ---- Tab badge counters ---- */
function updateTabCounts() {
  const counts = { all: state.species.length, fish: 0, invertebrate: 0, plant: 0 };
  state.species.forEach((s) => { if (counts[s.category] !== undefined) counts[s.category]++; });
  $$("#sp-tabs [data-filter]").forEach((tab) => {
    const c = tab.querySelector(".cnt");
    if (c) c.textContent = formatNum(counts[tab.dataset.filter] || 0);
  });
}

function bump(id, delta) {
  const s = sp(id);
  if (!s) return;
  let c = state.stocking.get(id) || 0;
  c = Math.max(0, Math.min(200, c + delta));
  if (c === 0) state.stocking.delete(id); else state.stocking.set(id, c);
  renderSpeciesGrid();
  renderStockChips();
  scheduleAnalyze();
}

function renderStockChips() {
  const box = $("#stock-list");
  box.innerHTML = "";
  const list = stockingList();
  if (!list.length) {
    box.innerHTML = `<div style="color:#64748B;font-size:14px">${state.lang === "bn" ? "এখনো কিছু বাছেননি — উপরে থেকে মাছ বা গাছ যোগ করুন।" : "Nothing selected yet — add fish or plants above."}</div>`;
    return;
  }
  list.forEach(({ species_id, count }) => {
    const meta = SPECIES_META[species_id] || {};
    const chip = document.createElement("span");
    chip.className = "stock-chip";
    chip.innerHTML = `${meta.emoji || "🐟"} <span class="nm">${spName(species_id)}</span> <span class="ct">×${formatNum(count)}</span> <button class="rm" data-rm="${species_id}" aria-label="remove">×</button>`;
    chip.querySelector("[data-rm]").onclick = () => { state.stocking.delete(species_id); renderSpeciesGrid(); renderStockChips(); scheduleAnalyze(); };
    box.appendChild(chip);
  });
}

/* ---- Blueprint local naming + tier colour (honest, by strategy id) ---- */
const BP_META = {
  best_value:     { icon: "✨", tier: "budget",
    bn: "বাজেট-ফ্রেন্ডলি ব্যালান্সড", en: "Budget-Friendly Balanced",
    bnTag: "কম খরচে সেরা ভারসাম্য — নতুনদের জন্য দারুণ", enTag: "Best balance at the lowest cost — great for beginners" },
  biodiversity:   { icon: "🌿", tier: "community",
    bn: "রঙিন কমিউনিটি ট্যাংক", en: "Vibrant Community Tank",
    bnTag: "বেশি রঙিন মায়়ার প্রাণবধ্দ ট্যাংক", enTag: "Richest mix of compatible species — a lively ecosystem" },
  low_maintenance:{ icon: "💎", tier: "premium",
    bn: "সহজ গাছের ট্যাংক", en: "Premium Planted, Low-Care",
    bnTag: "কম যত্নে টিকেশন গাছের সুন্দর সাজানো", enTag: "Hardy, heavily planted setup with minimal upkeep" },
};

/* ---- Package / blueprint cards ---- */
function renderBlueprints() {
  const box = $("#pkg-list");
  box.innerHTML = "";
  if (!state.blueprints.length) return;
  state.blueprints.forEach((bp) => {
    const meta = BP_META[bp.id] || { icon: "🐟", tier: "community",
      bn: bp.label, en: bp.label, bnTag: bp.tagline, enTag: bp.tagline };
    const el = document.createElement("div");
    el.className = "pkg-card " + meta.tier;
    const fish = bp.stocking.map((s) => `<span>${formatNum(s.count)}× ${spName(s.species_id)}</span>`).join("");
    const ratioPct = Math.round(bp.capacity_ratio * 100);
    const safeLabel = bp.harmony_score >= 90 ? (state.lang === "bn" ? "নিরাপদ" : "Safe")
      : bp.harmony_score >= 70 ? (state.lang === "bn" ? "সতর্ক" : "Caution") : (state.lang === "bn" ? "ঝুঁকি" : "Risky");
    const safeCls = bp.harmony_score >= 90 ? "peaceful" : bp.harmony_score >= 70 ? "neutral" : "aggressive";
    el.innerHTML = `
      <div class="pkg-top">
        <div>
          <div class="pkg-name">${meta.icon} ${state.lang === "bn" ? meta.bn : meta.en}</div>
          <div class="pkg-tag">${state.lang === "bn" ? meta.bnTag : meta.enTag}</div>
        </div>
        <span class="sp-badge ${safeCls}">${safeLabel}</span>
      </div>
      <div class="pkg-metrics">
        <div class="pkg-metric">${state.lang === "bn" ? "জায়গা" : "Space"}<b>${formatNum(ratioPct)}%</b></div>
        <div class="pkg-metric">${state.lang === "bn" ? "মাছের মাপ" : "Fish"}<b>${localizeDigits(bp.fish_inches)}"</b></div>
        <div class="pkg-metric">${state.lang === "bn" ? "ট্যাংক" : "Tank"}<b>${formatNum(bp.tank.volume_l)} L</b></div>
      </div>
      <div class="pkg-fish">${fish}</div>
      <div class="pkg-foot">
        <div class="pkg-total">${fmtMoney(bp.cost.total_usd)}<small>${state.lang === "bn" ? "মোট খরচ" : "Total cost"} · ${bp.cost.under_budget ? "✓" : "✗"}</small></div>
        <button class="btn small" data-load="${bp.id}">${t("auto.pick")}</button>
      </div>`;
    el.querySelector("[data-load]").onclick = () => loadBlueprint(bp);
    box.appendChild(el);
  });
}

function loadBlueprint(bp) {
  const tk = bp.tank;
  state.stocking.clear();
  bp.stocking.forEach((s) => state.stocking.set(s.species_id, s.count));
  state._tankOverride = { ...tk };
  state.currentBlueprint = bp;
  $("#manual-liters").value = Math.round(tk.volume_l);
  renderSpeciesGrid();
  renderStockChips();
  switchPanel("manual");
  analyze();
  toast(state.lang === "bn" ? "সেটআপটি ট্যাংকে লোড হয়েছে!" : "Setup loaded into your tank!");
  $("#step2").scrollIntoView({ behavior: "smooth" });
}

/* ---- Status banner ---- */
function renderStatus(score) {
  const box = $("#status-banner");
  let cls, icon, title, body;
  if (score >= 90) { cls = ""; icon = "✅"; title = t("status.ok.title"); body = t("status.ok.body"); }
  else if (score >= 70) { cls = "warn"; icon = "⚠️"; title = t("status.warn.title"); body = t("status.warn.body"); }
  else { cls = "danger"; icon = "❌"; title = t("status.danger.title"); body = t("status.danger.body"); }
  document.body.dataset.harmony = score >= 90 ? "ok" : score >= 70 ? "warn" : "danger";
  box.innerHTML = `<div class="status ${cls}">
    <div class="status-icon">${icon}</div>
    <div>
      <div class="status-title">${title}</div>
      <div class="status-body">${body}</div>
    </div>
  </div>`;
}

/* ---- Human-readable issue list ---- */
function plainIssue(issue, smap) {
  const nm = (id) => id ? (spName(id)) : "";
  switch (issue.type) {
    case "fin_nipping": return state.lang === "bn"
      ? `${nm(issue.species_a)} মাছের লেজ কেটে দিতে পারে ${nm(issue.species_b)} মাছের — আলাদা রাখাই ভালো।`
      : `${nm(issue.species_a)} may nip the fins of ${nm(issue.species_b)} — better to keep them apart.`;
    case "aggression": return state.lang === "bn"
      ? `${nm(issue.species_a)} আর ${nm(issue.species_b)} দুজনেই রাগী — মারামারি করতে পারে।`
      : `${nm(issue.species_a)} and ${nm(issue.species_b)} are both aggressive — they may fight.`;
    case "territorial": return state.lang === "bn"
      ? `${nm(issue.species_a)} আর ${nm(issue.species_b)} দুজনেই নিজের এলাকা বানাতে চায় — একসাথে রাখলে সমস্যা।`
      : `${nm(issue.species_a)} and ${nm(issue.species_b)} are both territorial — they will clash.`;
    case "predation": return state.lang === "bn"
      ? `${nm(issue.species_a)} (বড় মাছ) ${nm(issue.species_b)} মাছকে খেয়ে ফেলতে পারে!`
      : `${nm(issue.species_a)} (the bigger fish) may eat ${nm(issue.species_b)}!`;
    case "invertebrate_predation": return state.lang === "bn"
      ? `${nm(issue.species_a)} চিংড়ি/শামুক ${nm(issue.species_b)} মাছ খেয়ে ফেলতে পারে।`
      : `${nm(issue.species_a)} shrimp/snail may be eaten by ${nm(issue.species_b)}.`;
    case "param_temperature": return state.lang === "bn"
      ? `${nm(issue.species_a)} আর ${nm(issue.species_b)}-এর পছন্দের তাপমাত্রা আলাদা।`
      : `${nm(issue.species_a)} and ${nm(issue.species_b)} need different water temperatures.`;
    case "param_ph": return state.lang === "bn"
      ? `${nm(issue.species_a)} আর ${nm(issue.species_b)}-এর পানির অম্লতা (pH) আলাদা।`
      : `${nm(issue.species_a)} and ${nm(issue.species_b)} need different pH.`;
    case "param_gh": return state.lang === "bn"
      ? `${nm(issue.species_a)} আর ${nm(issue.species_b)}-এর পানি শক্ততা (GH) আলাদা।`
      : `${nm(issue.species_a)} and ${nm(issue.species_b)} need different water hardness.`;
    default: return issue.message;
  }
}

function renderIssues(issues) {
  const box = $("#issues-box");
  if (!issues || !issues.length) {
    box.innerHTML = `<div style="color:#047857;font-weight:700;font-size:15px">${t("issues.empty")}</div>`;
    return;
  }
  box.innerHTML = `<ul class="issues">` + issues.slice(0, 6).map((i) =>
    `<li><span class="em">${i.severity === "critical" ? "⛔" : i.severity === "warning" ? "⚠️" : "💡"}</span><span>${plainIssue(i)}</span></li>`).join("") + `</ul>`;
}

/* ---- Meters ---- */
function renderMeters(analysis) {
  const spaceFill = $("#space-fill"), spacePct = $("#space-pct"), spaceSub = $("#space-sub");
  const waterFill = $("#water-fill"), waterPct = $("#water-pct"), waterSub = $("#water-sub");
  if (!analysis) {
    spacePct.textContent = waterPct.textContent = "—";
    spaceFill.style.width = waterFill.style.width = "0%";
    spaceSub.textContent = waterSub.textContent = "";
    return;
  }
  const ratio = analysis.bioload.capacity_ratio;
  const pct = Math.min(100, Math.round(ratio * 100));
  spacePct.textContent = formatNum(pct) + "%";
  spaceFill.style.width = pct + "%";
  spaceFill.className = "meter-fill " + (pct > 100 ? "bad" : pct > 85 ? "warn" : "");
  spaceSub.textContent = ratio > 1
    ? (state.lang === "bn" ? "ট্যাংক ছোট! মাছ কমান বা বড় ট্যাংক নিন।" : "Tank is too small! Reduce fish or get a bigger tank.")
    : ratio > 0.85
    ? (state.lang === "bn" ? "জায়গা প্রায় ভরে গেছে — আর মাছ যোগ করবেন না।" : "Almost full — don't add more fish.")
    : (state.lang === "bn" ? "পর্যাপ্ত জায়গা আছে।" : "Enough space available.");

  const steps = state.cycleSteps || [];
  let waterScore = 100;
  if (steps.length) {
    const peakA = Math.max(...steps.map((s) => s.ammonia_mg_l));
    const peakN = Math.max(...steps.map((s) => s.nitrite_mg_l));
    const no3 = steps[steps.length - 1].nitrate_mg_l;
    waterScore = Math.max(0, Math.round(100 - (peakA > 0.25 ? (peakA - 0.25) * 120 : 0) - (peakN > 0.25 ? (peakN - 0.25) * 60 : 0) - (no3 > 40 ? (no3 - 40) * 0.5 : 0)));
  }
  waterPct.textContent = formatNum(waterScore) + "%";
  waterFill.style.width = waterScore + "%";
  waterFill.className = "meter-fill " + (waterScore < 60 ? "bad" : waterScore < 85 ? "warn" : "");
  waterSub.textContent = waterScore >= 85
    ? (state.lang === "bn" ? "সপ্তাহে পানি বদলালে পানি নিরাপদ থাকবে।" : "With weekly water changes the water stays safe.")
    : (state.lang === "bn" ? "পানি ঝুঁকিতে — নিচের গাইড দেখুন, গাছ যোগ করুন।" : "Water is risky — see the guide below, add plants.");
}

/* ---- Water forecast summary + chart ---- */
function renderWaterSummary() {
  const box = $("#water-summary");
  if (!state.cycleSteps || !state.cycleSteps.length) {
    box.textContent = state.lang === "bn" ? "মাছ যোগ করলে এখানে পানির অবস্থা দেখা যাবে।" : "Add fish to see the water forecast here.";
    return;
  }
  const steps = state.cycleSteps;
  const peakA = Math.max(...steps.map((s) => s.ammonia_mg_l));
  const no3 = steps[steps.length - 1].nitrate_mg_l;
  const wc = 25, freq = 7;
  box.textContent = localizeDigits(state.lang === "bn"
    ? `সপ্তাহে ${freq} দিন পর পর ${wc}% পানি বদলালে এবং ${Math.max(1, Math.round(no3 / 15))}টি গাছ রাখলে পানি সম্পূর্ণ নিরাপদ থাকবে (বিষাক্ত অ্যামোনিয়া সর্বোচ্চ ${peakA.toFixed(2)} mg/L)।`
    : `Changing ${wc}% water every ${freq} days and keeping ~${Math.max(1, Math.round(no3 / 15))} plants keeps the water completely safe (peak toxic ammonia ${peakA.toFixed(2)} mg/L).`);
}

function renderChart() {
  const canvas = $("#chart");
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth || 620, H = canvas.clientHeight || 230;
  canvas.width = W * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);
  const steps = state.cycleSteps;
  if (!steps || !steps.length) {
    ctx.fillStyle = "#64748B"; ctx.font = "15px 'Segoe UI', sans-serif";
    ctx.fillText(state.lang === "bn" ? "মাছ যোগ করলে এখানে হিসাব দেখা যাবে।" : "Add fish to see the forecast.", 20, H / 2);
    return;
  }
  const pad = { l: 40, r: 12, t: 12, b: 26 };
  const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
  const maxV = Math.max(0.25, ...steps.map((s) => Math.max(s.ammonia_mg_l, s.nitrite_mg_l, s.nitrate_mg_l)));
  ctx.strokeStyle = "#E2E8F0"; ctx.fillStyle = "#64748B"; ctx.font = "11px 'Segoe UI', sans-serif";
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + ih - (ih * i / 4);
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    ctx.fillText(localizeDigits((maxV * i / 4).toFixed(1)), 6, y + 3);
  }
  const x = (i) => pad.l + (iw * i / Math.max(1, steps.length - 1));
  const y = (v) => pad.t + ih - (ih * v / maxV);
  // lethal line 0.25
  ctx.strokeStyle = "#94A3B8"; ctx.setLineDash([5, 4]); ctx.lineWidth = 1.2;
  ctx.beginPath(); ctx.moveTo(pad.l, y(0.25)); ctx.lineTo(W - pad.r, y(0.25)); ctx.stroke(); ctx.setLineDash([]);
  const plot = (key, color) => {
    ctx.strokeStyle = color; ctx.lineWidth = 2.2; ctx.beginPath();
    steps.forEach((s, i) => { const yy = y(s[key]); i ? ctx.lineTo(x(i), yy) : ctx.moveTo(x(i), yy); });
    ctx.stroke();
  };
  plot("ammonia_mg_l", "#DC2626");
  plot("nitrite_mg_l", "#D97706");
  plot("nitrate_mg_l", "#2563EB");
  ctx.fillStyle = "#64748B";
  [0, 7, 14, 21, 29].forEach((d) => ctx.fillText("d" + formatNum(d + 1), x(Math.min(d, steps.length - 1)) - 10, H - 8));
}

function renderCycleSummary() {
  const box = $("#cycle-summary");
  const steps = state.cycleSteps;
  if (!steps || !steps.length) { box.innerHTML = ""; return; }
  const peakA = Math.max(...steps.map((s) => s.ammonia_mg_l));
  const peakN = Math.max(...steps.map((s) => s.nitrite_mg_l));
  const fin = steps[steps.length - 1];
  const cell = (k, v, cls) => `<div class="csum"><div class="k">${k}</div><div class="v ${cls}">${localizeDigits(v)}</div></div>`;
  box.innerHTML = cell(state.lang === "bn" ? "সর্বোচ্চ বিষাক্ত অ্যামোনিয়া" : "Peak toxic ammonia", peakA.toFixed(3) + " mg/L", peakA > 0.25 ? "bad" : "ok")
    + cell(state.lang === "bn" ? "সর্বোচ্চ নাইট্রাইট" : "Peak nitrite", peakN.toFixed(3) + " mg/L", peakN > 0.25 ? "bad" : "ok")
    + cell(state.lang === "bn" ? "শেষ নাইট্রেট" : "Final nitrate", fin.nitrate_mg_l.toFixed(0) + " mg/L", fin.nitrate_mg_l <= 40 ? "ok" : "warn")
    + cell(state.lang === "bn" ? "শেষ pH" : "Final pH", fin.ph.toFixed(2), "ok")
    + cell(state.lang === "bn" ? "অক্সিজেন" : "Oxygen", fin.oxygen_mg_l.toFixed(1) + " mg/L", fin.oxygen_mg_l >= 4 ? "ok" : "warn");
}

/* ---- Receipt ---- */
function reportBudget() {
  const items = state.analysis?.budget ?? state.currentBlueprint?.lines;
  return Array.isArray(items) ? items.filter((item) => item && typeof item === "object") : [];
}

function finiteNumber(value, fallback) {
  return value != null && value !== "" && Number.isFinite(Number(value)) ? Number(value) : fallback;
}

// Use the calculated tank first; inputs supply defaults for absent result fields.
function reportTank() {
  const tank = readTankConfig();
  const result = state.analysis?.tank ?? state.currentBlueprint?.tank ?? {};
  for (const key of Object.keys(tank)) {
    if (typeof tank[key] === "number") tank[key] = finiteNumber(result[key], tank[key]);
  }
  const gallons = tank.length_in * tank.width_in * tank.height_in * tank.water_level_pct / 100 / 231;
  tank.volume_gal = finiteNumber(result.volume_gal, finiteNumber(state.analysis?.bioload?.volume_gal, gallons));
  tank.volume_l = finiteNumber(result.volume_l, finiteNumber(state.analysis?.bioload?.volume_l, tank.volume_gal * 3.785411784));
  return tank;
}

function renderReport() {
  renderReceipt();
  renderTankSpecs();
  renderCare();
}

function renderReceipt(budget) {
  const ul = $("#budget-list");
  ul.innerHTML = "";
  const source = budget ?? reportBudget();
  const items = (Array.isArray(source) ? source : []).filter((i) => i && typeof i === "object").map((i) => ({
    ...i, item: i.item ?? (state.lang === "bn" ? "পণ্যের নাম নেই" : "Unnamed item"),
    qty: finiteNumber(i.qty, 1), cost_usd: finiteNumber(i.cost_usd, null),
  }));
  const fish = items.filter((i) => i.category !== "hardware");
  const equip = items.filter((i) => i.category === "hardware");
  const row = (i) => `<li>
    <span class="bi-cat">${i.category === "hardware" ? "" : (i.category === "plants" ? (state.lang === "bn" ? "গাছ" : "Plant") : (state.lang === "bn" ? "মাছ" : "Fish"))}</span>
    <span class="bi-name">${localizeDigits(i.item)}</span>
    <span class="bi-qty">×${localizeDigits(i.qty)}</span>
    <span class="bi-cost">${i.cost_usd === null ? "—" : fmtMoney(i.cost_usd * i.qty)}</span>
  </li>`;
  if (fish.length) { ul.innerHTML += `<li class="receipt-group">${t("receipt.fish")}</li>` + fish.map(row).join(""); }
  if (equip.length) { ul.innerHTML += `<li class="receipt-group">${t("receipt.equip")}</li>` + equip.map(row).join(""); }
  if (!items.length) {
    ul.innerHTML = `<li style="color:#64748B">${state.lang === "bn" ? "খরচ দেখতে মাছ বেছে হিসাব করুন।" : "Select fish and calculate to see costs."}</li>`;
  }
  const complete = items.length > 0 && items.every((i) => i.cost_usd !== null);
  const usd = complete ? items.reduce((a, b) => a + b.cost_usd * b.qty, 0) : null;
  const bdt = complete ? usd * state.exchangeRate : null;
  $("#budget-totals").innerHTML = `
    <div class="bt-item total"><div class="k">${state.lang === "bn" ? "মোট" : "Total"}</div><div class="v">${complete ? fmtMoney(usd) : "—"}</div></div>
    <div class="bt-item alt"><div class="k">≈ ${state.currency === "BDT" ? "USD" : "BDT"}</div><div class="v">${complete ? (state.currency === "BDT" ? "$" + formatNum(usd, 2) : fmtMoneyBdt(usd)) : "—"}</div></div>`;
  return bdt;
}

/* ---- Tank Specifications ---- */
function renderTankSpecs() {
  const box = $("#tank-specs");
  if (!box) return;
  const tank = reportTank();
  const liters = tank.volume_l;
  const feedG = (tank.food_amount_g * tank.feeding_level * tank.feeding_per_day).toFixed(1);
  const labels = {
    bn: {
      size: "ট্যাংকের সাইজ",
      filter: "ফিল্টার",
      temp: "তাপমাত্রা",
      ph: "pH",
      gh: "সংঘনতা (GH)",
      stocking: "মাছের সংখ্যা",
      water: "পানির বদলানো",
      feed: "খাবার দেওয়া",
      fish: "মাছ",
      plants: "গাছ",
      equipment: "সরঞ্জাম",
      cleaners: "ক্লিনার",
    },
    en: {
      size: "Tank Size",
      filter: "Filter",
      temp: "Temperature",
      ph: "pH",
      gh: "Hardness (GH)",
      stocking: "Livestock Count",
      water: "Water Change",
      feed: "Feeding",
      fish: "Fish",
      plants: "Plants",
      equipment: "Equipment",
      cleaners: "cleaners",
    },
  };
  const L = labels[state.lang] || labels.en;
  // Count hardware items from budget
  const budgetItems = reportBudget();
  const hwCount = budgetItems.filter(i => i.category === "hardware").length;
  const fishQty = stockingList().filter(s => { const sp = state.species.find(x => x.id === s.species_id); return sp && sp.category === "fish"; }).reduce((a, s) => a + s.count, 0);
  const plantQty = stockingList().filter(s => { const sp = state.species.find(x => x.id === s.species_id); return sp && sp.category === "plant"; }).reduce((a, s) => a + s.count, 0);
  const cleanQty = stockingList().filter(s => { const sp = state.species.find(x => x.id === s.species_id); return sp && sp.category === "invertebrate"; }).reduce((a, s) => a + s.count, 0);
  box.innerHTML = `<table class="specs-table">
    <tr><td class="k">${L.size}</td><td class="v">${formatNum(liters)} L · ${formatNum(tank.volume_gal)} gal</td></tr>
    <tr><td class="k">${L.filter}</td><td class="v">${formatNum(tank.filter_gph)} GPH</td></tr>
    <tr><td class="k">${L.temp}</td><td class="v">${localizeDigits(tank.temperature_c)}°C</td></tr>
    <tr><td class="k">${L.ph}</td><td class="v">${localizeDigits(tank.ph)}</td></tr>
    <tr><td class="k">${L.gh}</td><td class="v">${localizeDigits(tank.gh)} dGH</td></tr>
    <tr><td class="k">${L.stocking}</td><td class="v">${formatNum(fishQty)} ${L.fish} · ${formatNum(plantQty)} ${L.plants} · ${formatNum(cleanQty)} ${L.cleaners}</td></tr>
    <tr><td class="k">${L.water}</td><td class="v">${formatNum(tank.water_change_pct)}% ${state.lang === "bn" ? "প্রতি" : "every"} ${formatNum(tank.water_change_freq_days)} ${state.lang === "bn" ? "দিন" : "days"}</td></tr>
    <tr><td class="k">${L.feed}</td><td class="v">${formatNum(tank.feeding_per_day)}× ${state.lang === "bn" ? "দিনে" : "/day"} · ${localizeDigits(feedG)} g</td></tr>
    <tr><td class="k">${L.equipment}</td><td class="v">${formatNum(hwCount)} ${state.lang === "bn" ? "টি" : "items"}</td></tr>
  </table>`;
}

/* ---- Care rules ---- */
function renderCare() {
  const box = $("#care-list");
  const tank = reportTank();
  const feedG = (tank.food_amount_g * tank.feeding_level * tank.feeding_per_day).toFixed(1);
  const rules = [
    state.lang === "bn" ? `দিনে ${tank.feeding_per_day} বার, মোট ${feedG} গ্রাম খাবার দিন। মাছ ২ মিনিটে যা খেতে পারে ততটাই যথেষ্ট।` : `Feed ${tank.feeding_per_day}x/day, ${feedG} g total. Only what they eat in 2 minutes.`,
    state.lang === "bn" ? `প্রতি ${tank.water_change_freq_days} দিনে ${tank.water_change_pct}% পানি বদলান। নতুন পানি ফিল্টার করা/ডিক্লোরিনেটেড হতে হবে।` : `Change ${tank.water_change_pct}% water every ${tank.water_change_freq_days} days. Always dechlorinate.`,
    state.lang === "bn" ? `পানির তাপমাত্রা ${tank.temperature_c}°C রাখুন। হঠাৎ বদলাবেন না।` : `Keep the water at ${tank.temperature_c}°C. Avoid sudden changes.`,
  ];
  box.innerHTML = rules.map((r, i) => `<li><span class="n">${formatNum(i + 1)}</span><span>${localizeDigits(r)}</span></li>`).join("");
}

/* ---- Tank config reader ---- */
function readTankConfig() {
  const ov = state._tankOverride || {};
  const inputLiters = finiteNumber($(state.panel === "manual" ? "#manual-liters" : "#tank-size")?.value, 40);
  const liters = inputLiters > 0 ? inputLiters : 40;
  const tank = {
    length_in: 24, width_in: 12,
    height_in: liters * 1000 / (24 * 12 * 2.54 ** 3 * 0.9),
    water_level_pct: 90,
    filter_gph: 100, filter_type: "HOB", substrate: "sand", planted: true,
    temperature_c: 25, ph: 7.0, gh: 8,
    stocking: stockingList(),
    water_change_pct: 25, water_change_freq_days: 7, feeding_per_day: 2, food_amount_g: 1.5,
    room_climate: $("#climate-preset").value, currency: state.currency, feeding_level: 1.0,
  };
  for (const key of Object.keys(tank)) {
    if (typeof tank[key] === "number") tank[key] = finiteNumber(ov[key], tank[key]);
    else if (key !== "stocking" && key !== "currency" && key !== "room_climate") tank[key] = ov[key] ?? tank[key];
  }
  return tank;
}

/* ============================================================
   ANALYSIS + RESULTS
   ============================================================ */
let _analyzeTimer = null;
let _analysisVersion = 0;
function scheduleAnalyze() {
  clearTimeout(_analyzeTimer);
  _analysisVersion++;
  state.analysis = null;
  state.currentBlueprint = null;
  renderReport();
  _analyzeTimer = setTimeout(analyze, 500);
}

async function analyze() {
  const version = ++_analysisVersion;
  state.analysis = null;
  renderReport();
  const list = stockingList();
  if (!list.length) {
    state.analysis = null;
    state.currentBlueprint = null;
    state.cycleSteps = null;
    $("#status-banner").innerHTML = `<div class="status" style="background:var(--slate);border-color:var(--border)">
      <div class="status-icon">🐟</div>
      <div><div class="status-title">${state.lang === "bn" ? "এখনো কিছু বাছেননি" : "Nothing picked yet"}</div>
      <div class="status-body">${state.lang === "bn" ? "ধাপ ১ে মাছ বা গাছ যোগ করুন — তারপর এখানে চেকআপ দেখবেন।" : "Add fish or plants in Step 1 — the checkup will appear here."}</div></div>
    </div>`;
    $("#issues-box").innerHTML = `<div style="color:#64748B;font-size:15px;padding:8px 0">${state.lang === "bn" ? "মাছ বাছলে এখানে ট্যাংকের চেকআপ দেখা যাবে।" : "Pick fish to see the tank checkup here."}</div>`;
    $("#btn-autofix").disabled = true;
    renderMeters(null);
    renderWaterSummary();
    renderCycleSummary();
    renderChart();
    renderReceipt([]);
    renderTankSpecs();
    renderCare();
    return;
  }
  try {
    const cfg = readTankConfig();
    const [res, sim] = await Promise.all([
      api("/analyze-tank", cfg),
      api("/simulate-30-days", cfg),
    ]);
    if (version !== _analysisVersion) return;
    state.analysis = res;
    state.cycleSteps = sim.steps;
    state.exchangeRate = res.exchange_rate || state.exchangeRate;
    renderStatus(res.compatibility.score);
    renderIssues(res.compatibility.issues);
    renderMeters(res);
    renderWaterSummary();
    renderCycleSummary();
    renderChart();
    renderReceipt(res.budget);
    renderTankSpecs();
    renderCare();
    $("#btn-autofix").disabled = res.compatibility.score >= 90;
  } catch (e) {
    if (version !== _analysisVersion) return;
    toast(state.lang === "bn" ? "হিসাব করা গেল না: " + e.message : "Could not calculate: " + e.message);
  }
}

async function autoFix() {
  const list = stockingList();
  if (!list.length) return;
  const btn = $("#btn-autofix");
  btn.disabled = true;
  try {
    const cfg = readTankConfig();
    const res = await api("/auto-fix-tank", cfg);
    state._tankOverride = { ...res.tank };
    state.currentBlueprint = null;
    state.stocking.clear();
    res.tank.stocking.forEach((s) => state.stocking.set(s.species_id, s.count));
    renderSpeciesGrid();
    renderStockChips();
    toast(state.lang === "bn" ? "সমস্যার সমাধান হয়েছে! 🎉" : "Problems auto-fixed! 🎉");
    await analyze();
    $("#step2").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    toast(state.lang === "bn" ? "সমাধান করা গেল না: " + e.message : "Could not fix: " + e.message);
    btn.disabled = false;
  }
}

/* ============================================================
   AUTO-BUILD BLUEPRINTS
   ============================================================ */
async function generateBlueprints() {
  if (!$("#wizard-form").reportValidity()) return;
  const btn = $("#btn-optimize");
  btn.disabled = true;
  btn.textContent = state.lang === "bn" ? "খুঁজছি…" : "Finding…";
  try {
    const liters = Number($("#tank-size").value);
    const goal = $("#style-goal").value;
    const req = { max_budget_bdt: state.budgetBdt, tank_liters: liters, style_goal: goal,
      climate_preset: $("#climate-preset").value, currency: state.currency };
    const res = await api("/optimize-setup", req);
    state.blueprints = res.blueprints || [];
    renderBlueprints();
    if (state.blueprints.length) {
      $(".pkg-list").scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      toast(state.lang === "bn" ? "কোনো সেটআপ পাওয়া যায়নি, বাজেট বাড়িয়ে দেখুন।" : "No setup found — try a higher budget.");
    }
  } catch (e) {
    toast(state.lang === "bn" ? "খুঁজে পাওয়া গেল না: " + e.message : "Could not find: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = t("btn.analyze");
  }
}

/* ============================================================
   COMMERCIAL MODE RENDERING
   ============================================================ */
function fmtBdt(bdt) {
  if (state.currency === "BDT") return bdtPrefix() + formatNum(Math.round(bdt));
  return "$" + formatNum(bdt / state.exchangeRate, 2);
}

async function loadCommercialSpecies() {
  const sel = $("#comm-species");
  sel.innerHTML = "";
  const species = await api("/commercial-species");
  species.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = state.lang === "bn" ? s.name + " (" + s.scientific_name + ")" : s.name + " (" + s.scientific_name + ")";
    if (s.id === "monosex_tilapia") opt.selected = true;
    sel.appendChild(opt);
  });
}

async function commercialSimulate() {
  const btn = $("#btn-commsim");
  btn.disabled = true;
  btn.textContent = state.lang === "bn" ? "হিসাব করছি..." : "Calculating...";
  try {
    const req = {
      species_id: $("#comm-species").value,
      volume_l: parseFloat($("#comm-volume").value) || 10000,
      stocking_count: parseInt($("#comm-stock").value) || 5000,
      initial_weight_g: parseFloat($("#comm-init").value) || 20,
      target_weight_g: parseFloat($("#comm-target").value) || 500,
      duration_days: parseInt($("#comm-days").value) || 120,
      ph: parseFloat($("#comm-ph").value) || 7.5,
      temperature_c: parseFloat($("#comm-temp").value) || 28,
      feed_price_bdt: parseFloat($("#comm-feed").value) || 60,
      fingerling_price_bdt: parseFloat($("#comm-fry").value) || 12,
      market_price_bdt: parseFloat($("#comm-price").value) || 180,
      system_type: $("#comm-system").value,
      molasses_price_bdt: 25,
      electricity_rate_bdt: 9,
    };
    const res = await api("/commercial-simulate", req);
    state.commercial = res;
    renderCommercialReport(res);
  } catch (e) {
    toast(state.lang === "bn" ? "হিসাব করা গেল না: " + e.message : "Could not calculate: " + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = t("btn.simulate");
  }
}

function renderCommercialReport(res) {
  const sum = res.summary;
  $("#ex-net").textContent = fmtBdt(sum.net_profit_bdt);
  $("#ex-net-sub").textContent = state.lang === "bn" ? "মোট লাভ" : "Net profit";
  $("#ex-roi").textContent = formatNum(sum.roi_pct, 1) + "%";
  $("#ex-feed").textContent = formatNum(sum.max_daily_feed_kg || 0, 2) + " kg";
  $("#ex-fcr").textContent = "FCR: " + formatNum(sum.fcr || 0, 2);
  $("#ex-mol").textContent = formatNum(sum.max_daily_molasses_g || 0) + " g";
  $("#ex-nh3").textContent = formatNum(sum.nh3_mg_l || 0, 3) + " mg/L";
  $("#ex-tan").textContent = "TAN: " + formatNum(sum.tan_mg_l || 0, 3) + " mg/L";
  $("#ex-aer").textContent = (state.lang === "bn" ? "বায়ু: " : "Air: ") + formatNum(sum.aeration_lpm || 0, 1) + " L/min";

  // Chart
  const canvas = $("#comm-chart");
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth || 620, H = canvas.clientHeight || 230;
  canvas.width = W * dpr; canvas.height = H * dpr;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);
  const pad = { l: 40, r: 12, t: 12, b: 26 };
  const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
  const rows = res.rows;
  if (!rows.length) {
    ctx.fillStyle = "#64748B"; ctx.font = "15px 'Segoe UI', sans-serif";
    ctx.fillText(state.lang === "bn" ? "হিসাব করলে হিসাব দেখা যাবে।" : "Run simulation to see growth chart.", 20, H / 2);
    return;
  }
  const maxW = Math.max(...rows.map((r) => r.biomass_kg), 1);
  const maxF = Math.max(...rows.map((r) => r.feed_kg_day), 0.01);
  ctx.strokeStyle = "#E2E8F0"; ctx.fillStyle = "#64748B"; ctx.font = "11px 'Segoe UI', sans-serif";
  for (let i = 0; i <= 4; i++) {
    const y = pad.t + ih - (ih * i / 4);
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    ctx.fillText(localizeDigits((maxW * i / 4).toFixed(1)), 6, y + 3);
  }
  const x = (i) => pad.l + (iw * i / Math.max(1, rows.length - 1));
  const yW = (v) => pad.t + ih - (ih * v / maxW);
  const yF = (v) => pad.t + ih - (ih * v / maxF);
  ctx.lineWidth = 2.2;
  ctx.strokeStyle = "#0D9488"; ctx.beginPath();
  rows.forEach((r, i) => { const yy = yW(r.biomass_kg); i ? ctx.lineTo(x(i), yy) : ctx.moveTo(x(i), yy); });
  ctx.stroke();
  ctx.strokeStyle = "#D97706"; ctx.beginPath();
  rows.forEach((r, i) => { const yy = yF(r.feed_kg_day); i ? ctx.lineTo(x(i), yy) : ctx.moveTo(x(i), yy); });
  ctx.stroke();
  ctx.fillStyle = "#64748B";
  [0, 4, 8, 12, 16, 20, 24, 28].forEach((d) => ctx.fillText("W" + formatNum(Math.floor(d / 7) + 1), x(Math.min(d, rows.length - 1)) - 10, H - 8));

  // Table
  const tw = $("#comm-table-wrap");
  const headers = [
    state.lang === "bn" ? "সপ্তাহ" : "Week",
    state.lang === "bn" ? "দিন" : "Day",
    state.lang === "bn" ? "ওজন (গ্রাম)" : "Weight (g)",
    state.lang === "bn" ? "বায়োমাস (কেজি)" : "Biomass (kg)",
    state.lang === "bn" ? "খাবার/দিন (কেজি)" : "Feed/day (kg)",
    state.lang === "bn" ? "NH3 (mg/L)" : "NH3 (mg/L)",
  ];
  let html = `<table class="batch"><thead><tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>`;
  rows.forEach((r) => {
    html += `<tr><td class="num">${formatNum(r.week)}</td><td class="num">${formatNum(r.day)}</td><td class="num">${formatNum(r.weight_g)}</td><td class="num">${formatNum(r.biomass_kg, 2)}</td><td class="num">${formatNum(r.feed_kg_day, 3)}</td><td class="num">${formatNum(r.nh3_mg_l, 3)}</td></tr>`;
  });
  html += `</tbody></table>`;
  tw.innerHTML = html;

  // Summary totals
  const summaryBox = $("#comm-summary");
  summaryBox.innerHTML = `
    <div class="bt-item total"><div class="k">${state.lang === "bn" ? "মোট লাভ" : "Net Profit"}</div><div class="v">${fmtBdt(sum.net_profit_bdt)}</div></div>
    <div class="bt-item alt"><div class="k">ROI</div><div class="v">${formatNum(sum.roi_pct, 1)}%</div></div>`;
}

/* ============================================================
   INIT + EVENT HANDLERS
   ============================================================ */
function switchPanel(mode) {
  state.panel = mode;
  $("#panel-auto").hidden = mode !== "auto";
  $("#panel-manual").hidden = mode !== "manual";
  $("#opt-auto").classList.toggle("selected", mode === "auto");
  $("#opt-manual").classList.toggle("selected", mode === "manual");
  $$(".hero-tabs [data-tab]").forEach((tab) => {
    const active = tab.dataset.tab === (mode === "auto" ? "wizard" : "manual");
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-pressed", String(active));
  });
}

function bindEvents() {
  // Theme toggle (persistent)
  $("#theme-light").onclick = () => applyTheme("light");
  $("#theme-dark").onclick = () => applyTheme("dark");

  // Language toggle (persistent)
  $("#lang-bn").onclick = () => { state.lang = "bn"; applyI18n(); savePrefs(); $("#lang-bn").classList.add("active"); $("#lang-en").classList.remove("active"); reRenderLang(); };
  $("#lang-en").onclick = () => { state.lang = "en"; applyI18n(); savePrefs(); $("#lang-en").classList.add("active"); $("#lang-bn").classList.remove("active"); reRenderLang(); };

  // Currency toggle (persistent)
  $("#cur-bdt").onclick = () => { state.currency = "BDT"; savePrefs(); $("#cur-bdt").classList.add("active"); $("#cur-usd").classList.remove("active"); reRenderCurrency(); };
  $("#cur-usd").onclick = () => { state.currency = "USD"; savePrefs(); $("#cur-usd").classList.add("active"); $("#cur-bdt").classList.remove("active"); reRenderCurrency(); };

  // Budget quick-pills
  $("#budget-input").oninput = () => {
    state.budgetBdt = Number($("#budget-input").value) * (state.currency === "USD" ? state.exchangeRate : 1);
    renderBudgetControls();
  };
  $$(".budget-pill").forEach((pill) => {
    pill.onclick = () => {
      state.budgetBdt = Number(pill.dataset.budget);
      renderBudgetControls(true);
    };
  });

  // Ripple feedback on buttons
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn, .tab, .stepper button, .budget-pill");
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const r = document.createElement("span");
    r.className = "ripple";
    const size = Math.max(rect.width, rect.height);
    r.style.width = r.style.height = size + "px";
    r.style.left = (e.clientX - rect.left - size / 2) + "px";
    r.style.top = (e.clientY - rect.top - size / 2) + "px";
    btn.appendChild(r);
    setTimeout(() => r.remove(), 620);
  });

  // Mode nav
  $("#nav-home").onclick = () => {
    state.view = "home";
    $("#view-home").hidden = false;
    $("#view-farm").hidden = true;
    $("#nav-home").classList.add("active");
    $("#nav-farm").classList.remove("active");
  };
  $("#nav-farm").onclick = async () => {
    state.view = "farm";
    $("#view-home").hidden = true;
    $("#view-farm").hidden = false;
    $("#nav-farm").classList.add("active");
    $("#nav-home").classList.remove("active");
    if (!$("#comm-species").options.length) await loadCommercialSpecies();
    if (state.commercial) renderCommercialReport(state.commercial);
  };

  // Option cards
  $("#opt-auto").onclick = () => switchPanel("auto");
  $("#opt-manual").onclick = () => switchPanel("manual");
  $$(".hero-tabs [data-tab]").forEach((tab) => {
    tab.onclick = () => tab.dataset.tab === "commercial" ? $("#nav-farm").click()
      : switchPanel(tab.dataset.tab === "wizard" ? "auto" : "manual");
  });
  $("#manual-liters").oninput = () => {
    if (!$("#manual-liters").checkValidity()) return;
    state._tankOverride = null;
    scheduleAnalyze();
  };
  $("#tank-size").onchange = () => { state._tankOverride = null; scheduleAnalyze(); };
  $("#climate-preset").onchange = scheduleAnalyze;

  // Species tabs
  $$("[data-filter]").forEach((tab) => {
    tab.onclick = () => {
      state.spFilter = tab.dataset.filter;
      $$("[data-filter]").forEach((t) => t.classList.toggle("active", t === tab));
      renderSpeciesGrid();
    };
  });

  // Species search
  $("#sp-search").oninput = () => {
    state.spSearch = $("#sp-search").value;
    renderSpeciesGrid();
  };

  // Generate button
  $("#wizard-form").onsubmit = (event) => { event.preventDefault(); generateBlueprints(); };
  $("#panel-manual form").onsubmit = (event) => event.preventDefault();
  $("#comm-form").onsubmit = (event) => { event.preventDefault(); commercialSimulate(); };

  // Auto-fix
  $("#btn-autofix").onclick = autoFix;

  // Print buttons
  window.addEventListener("beforeprint", renderReport);
  $("#btn-print").onclick = () => window.print();
  $("#btn-comm-print").onclick = () => window.print();

  // Download list
  $("#btn-download").onclick = () => {
    renderReport();
    const list = $("#budget-list").innerText;
    const total = $("#budget-totals").innerText;
    const blob = new Blob([list + "\n\n" + total + "\n\n" + $("#tank-specs").innerText + "\n\n" + $("#care-list").innerText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "aquapulse_shopping_list.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  // Commercial simulate
  $("#btn-commsim").onclick = commercialSimulate;

  // Initial render (restore saved preferences)
  loadPrefs();
  applyTheme(state.theme);
  $("#lang-bn").classList.toggle("active", state.lang === "bn");
  $("#lang-en").classList.toggle("active", state.lang === "en");
  $("#cur-bdt").classList.toggle("active", state.currency === "BDT");
  $("#cur-usd").classList.toggle("active", state.currency === "USD");
  applyI18n();
  renderBudgetControls(true);
  switchPanel("auto");
  renderStockChips();
  analyze();
  loadSpecies();
  loadCommercialSpecies();
}

function reRenderCurrency() {
  renderBudgetControls(true);
  renderSpeciesGrid();
  renderBlueprints();
  renderReceipt();
  if (state.commercial) renderCommercialReport(state.commercial);
}

function reRenderLang() {
  renderReport();
  renderBudgetControls();
  renderSpeciesGrid();
  renderStockChips();
  renderBlueprints();
  if (state.analysis) {
    renderStatus(state.analysis.compatibility.score);
    renderIssues(state.analysis.compatibility.issues);
    renderMeters(state.analysis);
    renderWaterSummary();
    renderCycleSummary();
    renderReceipt(state.analysis.budget);
    renderCare();
    renderTankSpecs();
    renderChart();
  } else if (!stockingList().length) {
    analyze();
  }
  if (state.commercial) renderCommercialReport(state.commercial);
}

async function loadSpecies() {  try {
    state.species = await api("/species");
    renderSpeciesGrid();
  } catch (e) {
    toast(state.lang === "bn" ? "মাছের তালিকা আনা গেল না: " + e.message : "Could not load species: " + e.message);
  }
}

/* ============================================================
   DEBUG HOOKS (for Playwright verification)
   ============================================================ */
window.AquaPulseDebug = {
  get mode() { return state.view; },
  get theme() { return state.theme; },
  get currency() { return state.currency; },
  get language() { return state.lang; },
  get analysis() { return state.analysis; },
  get stocking() { return Array.from(state.stocking.entries()); },
  get blueprints() { return state.blueprints; },
  get commercial() { return state.commercial; },
  get harmony() { return state.analysis?.compatibility?.score || 0; },
  get bioloadRatio() { return state.analysis?.bioload?.capacity_ratio || 0; },
  setCurrency(c) { state.currency = c; },
  setLanguage(l) { state.lang = l; applyI18n(); },
  setTheme(t) { applyTheme(t); },
};

/* ============================================================
   START
   ============================================================ */
document.addEventListener("DOMContentLoaded", bindEvents);
