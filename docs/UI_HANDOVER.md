# AquaPulse Pro — UI/UX Handover Report

> Follow-through completed 2026-11-05: see [UI_VERIFICATION.md](UI_VERIFICATION.md) for changes, measured acceptance results, 32 browser checks, 116 backend tests, screenshots, and remaining limitations. The report below records the earlier state and is retained for history.

**Date:** 2026-11-04
**Branch:** `ui-overhaul` (uncommitted working tree)
**Scope:** Frontend-only. No Python, database, pricing, or API files were modified.

---

## 1. Codebase Health (verified, not assumed)

| Check | Command | Result |
|---|---|---|
| Backend test suite | `.venv\Scripts\python -m pytest tests/ -q` | **116 passed**, 1 warning (Starlette `httpx` deprecation), 8.84s |
| JS syntax | `node --check src/aquapulse/static/app.js` | **OK** |
| Files changed | `git diff --stat` | `app.js` (+28), `index.html` (+499/−…), `style.css` (1923 lines changed) — **static assets only** |

The single warning is a third-party deprecation notice inside `fastapi/testclient.py`; it is not caused by this work.

---

## 2. What Is Already Done

- Multi-color mesh background + six `.section-shell` variants (hero/emerald/ocean/violet/amber/indigo) with 24px radius and colored 2px borders.
- CTA sizing declared for `#btn-optimize`, `.btn-generate`, `.btn-primary`: `padding: 14px 36px !important`, `min-width: 240px`, `min-height: 52px`, `inline-flex` centered.
- Amateur motion removed: no `scale(1.08)`, no neon glow; tabs/pills/buttons now use `0.15–0.18s` border/background transitions with `translateY(-1px)` max.
- Budget-pill, autofix-button, `.btn` hover/active states normalized.
- Compact topbar declaration (`padding: 10px 20px; margin: 10px auto 14px; max-width: 1280px`) and tightened hero shell (`20px 28px`).
- Category color-coding **CSS** added for `.sp-card--peaceful`, `.sp-card--semi`, `.sp-card--aggressive`, `.sp-card--plant`, `.sp-card--invert` (light + dark variants), plus `.sp-card.is-selected` teal ring and `.sp-qty-pill`.
- Species grid `repeat(auto-fill, minmax(260px, 1fr))`, blueprint grid 3-up, KPI grid, care-list — all present.
- 116/116 backend tests green.

---

## 3. Remaining Hard Frontend Tasks

### P1 — Blocking correctness (must be fixed before any screenshot review)

1. **Required DOM IDs do not exist.**
   `index.html` uses `#opt-budget`, `#opt-tank`, `#opt-goal`, `#opt-climate`, `#btn-generate`.
   The acceptance spec requires `#budget-input`, `#tank-size`, `#style-goal`, `#climate-preset`, `#btn-optimize`.
   Audit result: `btn-optimize = 0`, `budget-input = 0`, `tank-size = 0`, `style-goal = 0`, `climate-preset = 0`.
   **Decision required:** rename in `index.html` **and** update every reference in `app.js` (`#opt-budget` at 895/1069, `#opt-tank` at 524/896, `#opt-goal` at 897, `#btn-generate` at 890/1125), or amend the spec. Half-renaming will silently break `generateBlueprints()`.

2. **Budget input is vertically offset from the other three.** `index.html:70–78` places `.budget-pills` as a sibling **between** the label and `<input id="opt-budget">`. Every other column is label → control. Result: the budget control sits ~40px lower, so the 4-column row does not align. Pills must move inside the label row (flex, `justify-content: space-between`) with the input directly beneath the label.

3. **`.hero-tabs` has no CSS rule at all.** The stylesheet defines `.tabs` (`style.css:328`) but the markup uses `class="hero-tabs"` (`index.html:59`). The mode switcher therefore inherits no centering, no gap, and no pill container — this is the "weirdly left-aligned tabs" defect. Either rename the class or style `.hero-tabs`.

4. **English mode still leaks Bangla.** `applyI18n()` (`app.js:299–305`) only rewrites `[data-i18n]` text nodes and placeholders; it never touches `<option>` elements.
   - `#opt-tank` options are hardcoded Bangla (`index.html:84–87`): `২০ লিটার (Nano)`, `৭৫ লিটার (Standard)`.
   - `#opt-climate` options are hardcoded English only (`index.html:106–111`) — the inverse bug in Bangla mode.
   - Static labels at `index.html:131/135` are English-only.
   **Required:** tri-lingual option metadata (e.g. `data-en` / `data-bn` per option) + a select-hydration pass inside `applyI18n()` and `reRenderLang()`.

5. **No digit localization layer.** `fmtMoney` (`app.js:344`), `fmtMoneyBdt` (`348`), and `fmtBdt` (`919`) call `toLocaleString("en-IN")` unconditionally. There is no `formatNum()` translating `0-9 ⇄ ০-৯`. Bangla mode currently renders English digits everywhere (prices, sizes, counts, meters).

### P2 — Behavioral wiring

6. **Category classes are styled but never applied.** `renderSpeciesGrid()` sets `card.className = "sp-card"` (`app.js:396`). The new `.sp-card--*` rules are dead CSS until the render function maps `category`/`aggression_rating` → `--peaceful` / `--semi` / `--aggressive` / `--plant` / `--invert`.

7. **No selected-state rendering.** `.sp-card.is-selected` and `.sp-qty-pill` exist in CSS only; `renderSpeciesGrid()` never toggles the class or injects the quantity pill when `count > 0`.

8. **Budget quick-pills are currency-blind.** `index.html:73–75` hardcodes `৳3,000 / ৳8,000 / ৳15,000`. `reRenderCurrency()` (`app.js:1166`) re-renders species, receipt and blueprints but **not** the pills. Required mapping: `৳3,000 / ৳8,000 / ৳15,000` ⇄ `$25 / $67 / $125`, with correct digit script per language.

9. **Topbar has a redundant nested container.** `.topbar` (`style.css:103`) is itself a max-width 1280 flex row, but `index.html:17` nests a single `.wrap` child inside it, which re-applies max-width and 20px padding. Net effect: double horizontal inset and a flex context with one child. Flatten to `brand` + centered view-nav + utility cluster in one row, and keep `.topbar` non-wrapping above 640px.

### P3 — Responsive & layout verification

10. **Two inline grids cannot respond.** `index.html:217` (`grid-template-columns: 1fr 1fr`) and `index.html:287` (`1.2fr 1fr`) are inline styles, so no media query can collapse them. At 390px these produce two ~160px columns — the primary source of horizontal overflow. Move both to classes (`.checkup-grid`, `.receipt-grid`) with 1-column collapses at ≤1024px and ≤640px.

11. **Mobile audit uncovered issues but unmeasured.** `@media(max-width: 620px)` sets `.sp-grid` to 2 columns and `@media(max-width: 400px)` to 1; the 390px viewport falls between them, so species cards stay 2-up on a 390px phone. Needs an explicit `≤480px` single-column rule.

12. **Above-the-fold position has never been measured.** The claim "Build Options starts above y≈650" is currently unverified. Hero title is 36px + subtitle + tabs + 4 fields + CTA; a vision pass should confirm `#step3` (blueprints) intersects the 900px fold, and the 768px laptop fold separately.

### P4 — Verification harness (stale, must be replaced)

13. **`scripts/verify_ui.cjs` is outdated and would fail.** It targets `http://127.0.0.1:8098`, a removed Chromium path, `#opt-manual`, `.pkg-card`, `.orb`, `step-mint/step-blue/step-amber`, `[data-budget="35000"]`, and `window.AquaPulseDebug.harmony`. It does not implement any of the six required assertions.

14. **`verify_ui.py` is equally stale** — it drives `#btn-generate` and old selectors, and its geometry expectations no longer match the 4-column spec.

15. **Required replacement checks** (plain-text PASS/FAIL, no image reading needed):
    - input tops of the four controls, max spread ≤ 4px;
    - `#btn-optimize` width ≥ 220, height ≥ 48, computed `padding-left/right` ≥ 28px;
    - blueprint section `getBoundingClientRect().top < 680` at 1440×900;
    - zero `[\u0980-\u09FF]` in `document.body.innerText` after `বাংলা` is stripped, English active;
    - `.sp-card--peaceful` / `--plant` / `--invert` present with three distinct `backgroundImage` values;
    - `document.documentElement.scrollWidth <= 390` at 390×844.

### P5 — Visual judgment (genuinely needs a vision-capable model)

16. Gradient balance between the six shells — verify no shell reads muddy in dark mode and borders remain ≥3:1 against their fills.
17. Species badge contrast on the new tinted cards (sky/amber/emerald/violet) in both themes.
18. Focus-visible rings on `.tab`, `.budget-pill`, `.stepper button`, and the CTA — not currently specified.
19. Receipt/spec table and care-rule typography at 1440px; the `1.2fr 1fr` split may still crowd the specs column.
20. Print stylesheet (`style.css:1367`) hides `.section-shell` entirely — confirm the care sheet still prints legibly, since the shells now carry the page background.

---

## 4. Handover Position

- **Backend: intact and provably green.** 116/116 tests pass; no Python, model, pricing, or API file appears in `git diff`.
- **Data & pricing: untouched.** BDT/USD conversion, receipt totals, blueprint ranking and commercial simulation all still run through the original backend contract.
- **HTML/CSS structure: intact and syntactically valid.** `app.js` passes `node --check`; all original hooks (`#opt-budget`, `#pkg-list`, `#sp-grid`, `#nav-home`/`#nav-farm`, `#panel-auto`/`#panel-manual`, KPI ids, commercial inputs) are still present, so nothing is detached from the runtime.
- **Nothing is committed or pushed.** Working tree holds uncommitted edits on `ui-overhaul`; `push_fixes.bat` commits without pushing and must not be run until the P1 items are resolved.

**Recommended next step for the receiving model:** resolve items 1–3 first (ID contract, budget pill placement, `.hero-tabs` rule), since every geometry assertion in the acceptance spec depends on those selectors existing and sharing a baseline. Items 4–8 are self-contained `app.js` work. Items 10–12 are layout-only. Item 13–15 is a single clean rewrite of the verification script.
