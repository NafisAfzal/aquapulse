# AquaPulse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a complete, production-grade interactive aquatic ecosystem simulator, fish compatibility resolver, and nitrogen-cycle forecaster called AquaPulse, with a FastAPI backend and a single-file HTML5 Canvas frontend.

**Architecture:** A layered design — `models.py` (Pydantic) defines the domain contracts; `database.py` seeds a SQLite catalog of 20+ species; `engine/` holds three pure-algebraic simulation modules (bioload, compatibility, nitrogen_sim); `api.py` exposes REST endpoints; `static/` holds the interactive frontend.

**Tech Stack:** Python 3.11 stdlib + fastapi, uvicorn, pydantic, pytest, httpx. Frontend: Vanilla HTML5 Canvas + CSS3 + Vanilla JS. No GPU, no heavy deps, <5 MB footprint, <10 ms per simulation.

**Spec:** User-provided project brief (AquaPulse vision in the task description).

## Global Constraints

- Python stdlib only (`sqlite3`, `math`, `json`, `dataclasses`, `unittest`) + `fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`.
- No PyTorch / TensorFlow / Pandas / SciPy / heavy node_modules.
- Total disk footprint under 5 MB (excluding .venv).
- All simulations must be purely algebraic/discrete-step, executing in under 10 ms.
- 30-day daily nitrogen cycle simulation.
- SQLite catalog seeded with 20+ fish, shrimp, snails, and plants.
- Modern dark-mode glassmorphic aquatic UI.

## Review Focus

- Empty tank configs must not crash (no fish stocked).
- Duplicate species / zero counts must be handled gracefully.
- Extreme temperature/pH values must produce sensible compatibility warnings, not NaNs.
- Missing species IDs in a stocking list must be rejected with a clear error.
- The 30-day simulation must always return exactly 30 steps and monotonic-ish bacterial growth.

---

## Task 1: Domain Models (`models.py`)

**Files:**
- Create: `src/aquapulse/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Produces: `Species`, `TankConfig`, `StockingItem`, `SimulationStep`, `CompatibilityIssue`, `CompatibilityReport`, `AnalyzeResponse`, `SimulateResponse`, `BioloadResult`, `CarePlan`, `BudgetItem`, `Preset` Pydantic models.

- [x] **Step 1: Write `models.py`** with Pydantic models and helpers (volume computation, defaults). Species carries: id, name, scientific_name, category, size_cm, min_tank_gal, temperament, swim_zone, min_temp_c, max_temp_c, min_ph, max_ph, min_gh, max_gh, aggression_rating, fin_nipper, territorial, plant_safe, bioload_factor, emoji, description.

- [x] **Step 2: Write `tests/test_models.py`** asserting model construction, validation of negative values, and TankConfig volume helpers.

- [x] **Step 3: Run tests** — `pytest tests/test_models.py -v` → PASS.

---

## Task 2: Species Catalog + SQLite (`database.py`)

**Files:**
- Create: `src/aquapulse/database.py`
- Test: `tests/test_database.py`

**Interfaces:**
- Produces: `Database` class with `get_species()`, `get_species_by_id()`, `get_presets()`, `save_build()`, `init()`.

- [x] **Step 1: Write `database.py`** with an in-memory/on-disk SQLite schema and a seed list of 24 species (12+ fish, shrimp, snails, plants) + 3 presets.

- [x] **Step 2: Write `tests/test_database.py`** asserting ≥20 species seeded, all required fields present, and lookups work.

- [x] **Step 3: Run tests** — `pytest tests/test_database.py -v` → PASS.

---

## Task 3: Bioload Engine (`engine/bioload.py`)

**Files:**
- Create: `src/aquapulse/engine/bioload.py`
- Test: `tests/test_bioload.py`

**Interfaces:**
- Produces: `compute_bioload(species_by_id, stocking, tank)` → `BioloadResult` with volume_gal, volume_l, total_fish_inches, total_bioload_points, filter_capacity_points, capacity_ratio, stocking_rating, crowding (per-zone dict), warnings list.

- [x] **Step 1: Write `bioload.py`** implementing the "1 inch per gallon" heuristic adjusted by species bioload_factor, filter GPH vs. tank volume capacity, and swim-zone crowding.

- [x] **Step 2: Write `tests/test_bioload.py`** asserting exact volume math, filter capacity rating, and zone crowding detection.

- [x] **Step 3: Run tests** — PASS.

---

## Task 4: Compatibility Engine (`engine/compatibility.py`)

**Files:**
- Create: `src/aquapulse/engine/compatibility.py`
- Test: `tests/test_compatibility.py`

**Interfaces:**
- Produces: `resolve_compatibility(species_by_id, stocking, tank)` → `CompatibilityReport` with `score`, `verdict`, `issues`, `pair_issues`.

- [x] **Step 1: Write `compatibility.py`** with pairwise checks: fin-nipping (fin_nipper × peaceful), aggression (temperament + aggression_rating), territorial overlap (same swim zone + territorial), predation (size ratio > 2.5×), temperature overlap, pH overlap, GH overlap.

- [x] **Step 2: Write `tests/test_compatibility.py`** asserting each conflict type fires and score/verdict are correct.

- [x] **Step 3: Run tests** — PASS.

---

## Task 5: Nitrogen Cycle Simulator (`engine/nitrogen_sim.py`)

**Files:**
- Create: `src/aquapulse/engine/nitrogen_sim.py`
- Test: `tests/test_nitrogen_sim.py`

**Interfaces:**
- Produces: `simulate_nitrogen_cycle(species_by_id, stocking, tank, config)` → `list[SimulationStep]` (exactly 30 steps).

- [x] **Step 1: Write `nitrogen_sim.py`** implementing daily discrete dynamics: ammonia production ∝ feeding × bioload; AOB convert NH3→NO2, NOB convert NO2→NO3 (Monod-ish saturation); bacterial growth on substrate; plant nitrate uptake; water change dilution; pH drift from nitrate.

- [x] **Step 2: Write `tests/test_nitrogen_sim.py`** asserting ammonia spike early, nitrite peak after, nitrate rises, bacteria grow, water change reduces concentration, and exactly 30 steps returned.

- [x] **Step 3: Run tests** — PASS.

---

## Task 6: FastAPI Endpoints (`api.py`)

**Files:**
- Create: `src/aquapulse/api.py`
- Test: `tests/test_api.py`

**Interfaces:**
- Produces: FastAPI app with routes `/species`, `/presets`, `/analyze-tank`, `/simulate-30-days`, `/save-build`, `/` (serves index.html), `/static`.

- [x] **Step 1: Write `api.py`** wiring database + engines into REST endpoints.

- [x] **Step 2: Write `tests/test_api.py`** using `TestClient` to hit each endpoint and validate responses (incl. error on unknown species).

- [x] **Step 3: Run tests** — PASS.

---

## Task 7: Frontend (`static/index.html`, `style.css`, `app.js`)

**Files:**
- Create: `src/aquapulse/static/index.html`, `style.css`, `app.js`

**Interfaces:**
- Consumes: API endpoints. Produces: interactive canvas aquarium with swimming fish, charts, care plan, budget.

- [x] **Step 1: Write `index.html`** — dashboard layout: tank config panel, species picker, canvas aquarium, compatibility panel, chemistry chart, care plan + budget.

- [x] **Step 2: Write `style.css`** — dark glassmorphic aquatic theme, responsive.

- [x] **Step 3: Write `app.js`** — fish boids animation, tank builder, fetch API calls, canvas line chart of 30-day chemistry, water tint shift.

- [x] **Step 4: Smoke-test** — run server, curl `/` returns 200 and HTML; curl `/species` returns JSON.

---

## Task 8: Packaging + Docs (`pyproject.toml`, `README.md`)

**Files:**
- Create: `pyproject.toml`, `README.md`

- [x] **Step 1: Write `pyproject.toml`** with minimal deps.
- [x] **Step 2: Write `README.md`** with run guide, math formulas, architecture.
- [x] **Step 3: Full test run** — `pytest -v` all green. Verify footprint < 5 MB (excluding .venv).
