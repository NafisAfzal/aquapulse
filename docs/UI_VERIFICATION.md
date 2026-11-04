# AquaPulse UI follow-through

Verified 2026-11-05 on the existing `ui-overhaul` working tree at `D:\AI\aquapulse`.
Local application: <http://127.0.0.1:8000>. No commit, push, or deployment performed.

## Changes

- `src/aquapulse/static/index.html`: renamed all five acceptance selectors and their labels; moved presets into the budget label group; translated tank/climate options using the existing dictionary mechanism; flattened the topbar; replaced inline grids with responsive classes; preserved meter IDs during translation; restored the missing molasses KPI; identified the printable care sheet.
- `src/aquapulse/static/app.js`: updated selector callers, wired visible mode tabs, localized displayed numbers and currency presets, retained an exact BDT budget across currency changes, and passed supported climate presets to the optimizer. English displays the currency code `BDT` because the acceptance scan includes the Taka symbol in its prohibited Unicode range. Scientific names replace Bangla secondary names in English catalog cards.
- The same script now renders category and selected classes with quantity pills, preserves keyboard focus after quantity changes, validates the budget before submitting, and re-renders empty/results states on language changes. Fixed the undefined `feedG` exception and the tank volume display's missing division by 100. Manual tank-size changes now reach the existing analysis contract. Auto-fix retains loaded tank dimensions.
- `src/aquapulse/static/style.css`: styles centered hero tabs; preserves the aligned control baseline; collapses form, checkup, receipt and catalog layouts on narrower screens; improves dark inactive tabs, badges, shell borders and receipt headings; adds focus outlines and reduced-motion support; prints the receipt, specs and care content.
- `scripts/verify_ui.cjs`: replaces obsolete checks with the six acceptance assertions and exercised interactions/error recovery. Uses managed Chromium by default, with an optional browser executable override.
- `verify_ui.py`: invokes the same Node verification runner, avoiding two diverging test suites and a separate Python Playwright dependency.

Backend source, API models, database source, pricing and simulation code were not modified.

## Actual checks

| Check | Result |
| --- | --- |
| `.venv\Scripts\python -m pytest tests/ -q` | **116 passed, 1 warning in 6.08s** |
| `node --check src\aquapulse\static\app.js` | Exit 0 |
| `node --check scripts\verify_ui.cjs` | Exit 0 |
| `.venv\Scripts\python verify_ui.py` | **32/32 checks passed**, exit 0 |
| `git diff --check` | Exit 0; Git also warns about LF/CRLF conversion |

The backend warning is `StarletteDeprecationWarning` for using `httpx` with `starlette.testclient`.

The browser runner used the existing Playwright installation through `NODE_PATH=C:\Users\USER\node_modules` and the installed Chromium 1248 executable through `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`. `UI_SCREENSHOT_DIR=docs\ui-verification` saved the captures below. No application dependency was installed or changed.

### Six acceptance assertions

| Assertion | Measured result |
| --- | --- |
| Four control tops within 4px | **429.53125px** for all four: **0px spread** |
| CTA width ≥220, height ≥48, horizontal padding ≥28px | **240 × 52px**, **36px** left/right |
| Build Options above 680px at 1440×900 | **581.53125px** from document top |
| English text contains no Bangla-range Unicode | **PASS** in initial and loaded-result states |
| Peaceful/plant/invertebrate backgrounds are distinct | **PASS**, three different computed background images |
| No horizontal page overflow at 390×844 | **390px** document width; home and commercial views pass |

Additional checks cover visible mode switching, exact BDT optimizer budget while displaying USD, climate request payload, three generated blueprints, blueprint loading, correct displayed liters, selected quantities, Bangla display digits, language re-rendering, surviving meter IDs, invalid budget rejection, print-media content, the 1366×768 fold, keyboard focus/quantity controls, commercial KPIs/schedule, removing the last selected unit, and recovery from a 503 response or an empty optimizer result. Expected HTTP failures run in a separate page; the normal workflow records zero runtime/console errors.

## Captures

| Surface | Light | Dark |
| --- | --- | --- |
| Desktop, 1440×900 | [Light](ui-verification/desktop-light.png) | [Dark](ui-verification/desktop-dark.png) |
| Mobile, 390×844 | [Light](ui-verification/mobile-light.png) | [Dark](ui-verification/mobile-dark.png) |
| Receipt/specs/care | [Light](ui-verification/receipt-light.png) | [Dark](ui-verification/receipt-dark.png) |
| Species card | [Light](ui-verification/species-light.png) | [Dark](ui-verification/species-dark.png) |

Desktop/mobile captures and the receipt/card captures were inspected in both themes across the two review passes. Print was checked using Chromium's print-media emulation; a physical printout was not tested.

## Corrections to the earlier handover

The pre-change browser reproduction already had aligned input tops, Build Options around 572px, and a single-column species grid at 390px (390 is below the old 400px breakpoint). These were not reproduced as baseline failures. The missing acceptance IDs, untranslated content, unwired tabs/classes and runtime exception were reproduced. Adding `data-i18n` to options uses the existing translation pass; no second select-specific hydration system was needed. Climate choices were corrected to the three presets actually defined by the backend.

## Limits and remaining observations

- The Impeccable detector ran once and exited 1 with warnings. It flags the inherited gradient text, nested cards, violet/cyan palette, glow shadows, width transitions, small version label, and static-source contrast pairs. This task preserves the established visual direction; it does not certify all contrast combinations or full WCAG compliance.
- Existing backend-provided catalog descriptions, receipt item names and commercial species names remain English in Bangla mode. Native numeric input values remain ASCII for parsing and API submission; output prices, counts, sizes and meters use Bangla digits.
- Verification used desktop Chromium with emulated viewport sizes, not physical phones or every browser. The default managed-browser path was not exercised on this machine; the executable override was used.
- The manual budget field and saved-builds area predate this work and remain without a complete end-to-end workflow. Existing numerical/model claims and optimizer-versus-analysis pricing consistency were outside this frontend follow-through.
- Existing untracked screenshots and `push_fixes.bat` were preserved and the batch file was not run. The prior handover remains as historical context.
