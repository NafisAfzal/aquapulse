# 🌊 AquaPulse Pro v1.0.0

**A friendly, bilingual (বাংলা / English) aquarium planner with a premium dual-theme UI — for the home aquarist and the commercial farmer.**

[![Version](https://img.shields.io/badge/version-1.0.0-06b6d4?style=flat-square)](https://github.com/aquapulse/aquapulse)
[![License](https://img.shields.io/badge/license-MIT-emerald?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-10b981?style=flat-square)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-116%20passing-2563eb?style=flat-square)](https://github.com/aquapulse/aquapulse)

---

## The Problem

Planning a freshwater aquarium is hard. You have to guess:
- Which fish can actually live together without fighting?
- How much will it *really* cost at local Dhaka markets?
- How do I cycle my nitrogen levels safely?

Most apps give you generic prices from global pet stores — useless when a basic 20L tank in Bangladesh should cost **৳3,000–8,000**, not ৳30,000.

## The Solution

**AquaPulse** is a mathematical aquarium architect. It uses a **deterministic constraint solver** to build verified, 100%-compatible tank setups at real Bangladeshi retail prices.

- 🧠 **Compatibility Engine** — Pairwise species compatibility scoring with harmony ≥ 90 guarantee.
- 📐 **Auto-Architect** — Tell it your budget (BDT ৳3,000 / ৳8,000 / ৳15,000) and tank size; get 3 optimized blueprints back instantly.
- 🚜 **Commercial Mode** — Biofloc growth simulation with weekly ROI, feed conversion, and ammonia toxicity calculators.
- 🌙 **Modern Dual-Theme UI** — Light/dark modes with a bilingual বাংলা/English interface.

---

## Screenshots

| Light Theme | Dark Theme |
|-------------|------------|
| ![Light Theme](https://placehold.co/800x400/F8FAFC/0F172A?text=Light+Theme+Screenshot+Coming+Soon) | ![Dark Theme](https://placehold.co/800x400/0F172A/2DD4BF?text=Dark+Theme+Screenshot+Coming+Soon) |

---

## Features

| Feature | What It Does |
|---------|--------------|
| 🧠 Smart Compatibility | Harmony scoring, aggression matrix, parameter matching |
| 📐 Auto-Architect | Budget-constrained constraint solver, 3 ranked blueprints |
| 🐟 Species Catalog | 23 organisms with real care parameters |
| 💰 Real BDT Pricing | Hardware + livestock priced for the Bangladesh market (USD=৳120) |
| 🚜 Commercial Mode | Biofloc C:N 15:1, Emerson NH3, weekly ROI schedules |
| 🌙 Dual Theme | Light (warm alabaster) / Dark (obsidian) with persistence |
| 🌐 Bilingual UI | Full বাংলা / English i18n dictionary |
| 🖨️ Print Care Sheet | Optimized @media print layout |

---

## 1-Click Run (Windows)

The easiest way to get started — no CLI knowledge required:

1. **Download** this repository and extract it to a folder.
2. **Double-click** `start.bat` — that's it!

The script will:
- Auto-create a Python virtual environment (`.venv`)
- Install all dependencies
- Launch the server at `http://127.0.0.1:8000`
- Open your browser automatically

---

## Manual Run (Any Platform)

```bash
# Install
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux
pip install -e ".[dev]"

# Run
python run.py
# or: python -m aquapulse
```

Open **http://127.0.0.1:8000** in your browser.

---

## Run the Tests

```bash
pytest -q
# 116 passed
```

---

## API Reference

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | 3-step guided-flow SPA |
| GET | `/species` | Catalog (23 organisms) |
| GET | `/presets` | Curated starter presets |
| GET | `/climate-presets` | Room climate presets |
| GET | `/meta` | Version, exchange rate, currencies |
| POST | `/analyze-tank` | Bioload, compatibility, care plan, budget |
| POST | `/simulate-30-days` | 30-day nitrogen forecast |
| POST | `/save-build` | Persist a build to SQLite |
| POST | `/optimize-setup` | Auto-Architect: 3 blueprints from budget + size |
| POST | `/auto-fix-tank` | Remove conflicting stock until harmony >= 90 |
| GET | `/commercial-species` | 5 commercial species |
| POST | `/commercial-simulate` | Weekly biofloc growth + full ROI report |

### Example — Auto-build

```bash
curl -X POST http://127.0.0.1:8000/optimize-setup \
  -H "Content-Type: application/json" \
  -d '{"max_budget_bdt":8000,"tank_liters":40,"style_goal":"peaceful_community"}'
```

---

## Project Layout

```text
aquapulse/
├── run.py
├── start.bat
├── install.bat
├── pyproject.toml
├── README.md
├── src/aquapulse/
│   ├── api.py                     # FastAPI routes
│   ├── database.py                # SQLite catalog: species + presets
│   ├── models.py                  # Pydantic domain models
│   ├── engine/
│   │   ├── bioload.py             # Volume, fish-inches, filter capacity
│   │   ├── compatibility.py       # Pairwise compatibility resolver
│   │   ├── disease_doctor.py      # Risk scoring + medication dosages
│   │   ├── breeding.py            # Fry survival + 60-day population forecast
│   │   ├── climate.py             # Climate presets + heater/fan sizing
│   │   ├── pricing.py             # USD/BDT budget builder (1 USD = 120 BDT)
│   │   ├── nitrogen_sim.py        # 30-day NH3 -> NO2 -> NO3 simulation
│   │   ├── optimizer.py           # Auto-Architect constraint solver + auto-fix
│   │   └── commercial_aquaculture.py  # Emerson NH3, molasses dosing, ROI
│   └── static/
│       ├── index.html             # 3-step flow + commercial view
│       ├── style.css              # Dual-theme design system
│       └── app.js                 # i18n, theme engine, harmony glow
├── tests/                         # 116 pytest tests
├── docs/                          # Screenshots for README
└── scripts/
```

---

## Why It's Fast and Light

- **Backend:** Python stdlib + FastAPI, Uvicorn, Pydantic. No NumPy/Pandas/SciPy.
- **Frontend:** Vanilla HTML + CSS + JS. No build step, no framework, no npm.
- **Dependencies:** Minimal — only FastAPI, Uvicorn, Pydantic, and pytest for testing.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Star This Repo

If AquaPulse helps you build a better aquarium, please consider starring this repository! It helps the project grow and reach more aquarists.

[![GitHub Repo stars](https://img.shields.io/github/stars/NafisAfzal/aquapulse?style=social)](https://github.com/NafisAfzal/aquapulse)
