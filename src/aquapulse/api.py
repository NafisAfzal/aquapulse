"""FastAPI application exposing the AquaPulse engine.

Endpoints
---------
GET  /                    -> serves the SPA dashboard (index.html)
GET  /static/*            -> static assets
GET  /species             -> full species catalog
GET  /presets             -> curated tank presets
POST /analyze-tank        -> bioload + compatibility + care plan + budget
POST /simulate-30-days    -> 30-day nitrogen-cycle forecast
POST /save-build          -> persist a build for later recall
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import Database
from .engine.bioload import compute_bioload
from .engine.breeding import predict_breeding
from .engine.climate import evaluate_climate, list_climate_presets
from .engine.commercial_aquaculture import (
    list_commercial_species,
    simulate_commercial,
)
from .engine.compatibility import resolve_compatibility
from .engine.disease_doctor import assess_disease_risk
from .engine.nitrogen_sim import simulate_nitrogen_cycle, summarize_cycle
from .engine.optimizer import auto_fix_tank, build_optimized_setups
from .engine.pricing import USD_TO_BDT, build_budget, budget_totals
from .models import (
    AnalyzeResponse,
    AutoFixResponse,
    BioloadResult,
    CareItem,
    CommercialReport,
    CommercialRequest,
    CommercialSpeciesInfo,
    CompatibilityReport,
    CurrencyTotals,
    OptimizationRequest,
    OptimizationResponse,
    SaveBuildResponse,
    SimulateResponse,
    Species,
    StockingItem,
    TankConfig,
)

STATIC_DIR = Path(__file__).parent / "static"

db = Database()
app = FastAPI(title="AquaPulse Pro", version="1.0.0",
              description="Aquarium planning platform: Smart Setup Optimizer & Commercial Biofloc/Aquaculture ROI engine")


class SaveBuildRequest(BaseModel):
    name: str
    payload: dict


@app.get("/")
def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"detail": "frontend not built"}, status_code=200)


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _species_map() -> Dict[str, Species]:
    return {s.id: s for s in db.get_species()}


def _validate_stocking(stocking: List[StockingItem]) -> None:
    known = _species_map()
    for item in stocking:
        if item.species_id not in known:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown species_id '{item.species_id}' in stocking",
            )


@app.get("/species")
def species() -> List[Species]:
    return db.get_species()


@app.get("/presets")
def presets():
    return db.get_presets()


@app.get("/climate-presets")
def climate_presets():
    return list_climate_presets()


@app.get("/meta")
def meta():
    return {"version": "1.0.0", "exchange_rate": USD_TO_BDT, "currencies": ["USD", "BDT"]}


@app.post("/analyze-tank")
def analyze_tank(tank: TankConfig) -> AnalyzeResponse:
    _validate_stocking(tank.stocking)
    smap = _species_map()

    bioload = compute_bioload(smap, tank.stocking, tank)
    compat = resolve_compatibility(smap, tank.stocking, tank)
    steps = simulate_nitrogen_cycle(smap, tank.stocking, tank, days=30)

    climate = evaluate_climate(smap, tank.stocking, tank)
    disease = assess_disease_risk(smap, tank.stocking, tank, steps)
    breeding = predict_breeding(smap, tank.stocking, tank)
    budget = build_budget(tank, tank.stocking, smap, climate)
    usd_total, bdt_total = budget_totals(budget)

    care_plan = _build_care_plan(tank, bioload, compat, disease, climate, breeding)

    warnings: List[str] = list(bioload.warnings)
    if compat.issues:
        for issue in compat.issues[:5]:
            warnings.append(f"[{issue.severity.value}] {issue.message}")
    if tank.volume_gal < 1:
        warnings.append("Tank volume under 1 gallon is impractical.")
    warnings.extend(climate.warnings[:3])
    if disease.overall_risk >= 45:
        warnings.append(f"[warning] Fish Doctor: overall disease risk {disease.overall_risk:.0f}%.")

    return AnalyzeResponse(
        tank=tank,
        bioload=bioload,
        compatibility=compat,
        care_plan=care_plan,
        budget=budget,
        warnings=warnings,
        disease=disease,
        breeding=breeding,
        climate=climate,
        totals=CurrencyTotals(usd=usd_total, bdt=bdt_total),
        exchange_rate=USD_TO_BDT,
    )


@app.post("/simulate-30-days")
def simulate_30_days(tank: TankConfig) -> SimulateResponse:
    _validate_stocking(tank.stocking)
    smap = _species_map()
    steps = simulate_nitrogen_cycle(smap, tank.stocking, tank, days=30)
    summary = summarize_cycle(steps)
    return SimulateResponse(steps=steps, summary=summary)


@app.post("/save-build", response_model=SaveBuildResponse)
def save_build(req: SaveBuildRequest) -> SaveBuildResponse:
    build_id = db.save_build(req.name, req.payload)
    return SaveBuildResponse(id=build_id, ok=True)


# --------------------------------------------------------------------------
# 1.0.0 - Auto-Architect constraint solver
# --------------------------------------------------------------------------

@app.post("/optimize-setup", response_model=OptimizationResponse)
def optimize_setup(req: OptimizationRequest) -> OptimizationResponse:
    smap = _species_map()
    blueprints = build_optimized_setups(smap, req)
    return OptimizationResponse(request=req, blueprints=blueprints)


@app.post("/auto-fix-tank", response_model=AutoFixResponse)
def auto_fix(req: TankConfig) -> AutoFixResponse:
    _validate_stocking(req.stocking)
    smap = _species_map()
    return auto_fix_tank(smap, req)


# --------------------------------------------------------------------------
# 1.0.0 - Commercial biofloc & aquaculture ROI engine
# --------------------------------------------------------------------------

@app.get("/commercial-species")
def commercial_species() -> List[CommercialSpeciesInfo]:
    return list_commercial_species()


@app.post("/commercial-simulate", response_model=CommercialReport)
def commercial_simulate(req: CommercialRequest) -> CommercialReport:
    return simulate_commercial(req)


# --------------------------------------------------------------------------
# Care plan & budget generators
# --------------------------------------------------------------------------

def _build_care_plan(tank: TankConfig, bioload: BioloadResult,
                     compat: CompatibilityReport, disease=None, climate=None,
                     breeding=None) -> List[CareItem]:
    plan: List[CareItem] = []
    freq = tank.water_change_freq_days
    plan.append(CareItem(
        name="Water change",
        detail=(f"Replace {tank.water_change_pct:.0f}% of the water every {freq} day(s). "
                f"Always dechlorinate and match temperature."),
        cadence=f"every {freq} day(s)",
    ))
    effective_food = tank.food_amount_g * tank.feeding_level
    plan.append(CareItem(
        name="Feed fish",
        detail=(f"Feed {tank.feeding_per_day}x/day, {effective_food:.1f} g total "
                f"(feeding level {tank.feeding_level:.1f}×). "
                f"Skip one day per week to let the fish rest."),
        cadence="daily",
    ))
    plan.append(CareItem(
        name="Test water",
        detail="Test ammonia, nitrite, nitrate and pH weekly. Target NH3/NH4 < 0.25, NO2 < 0.25, "
                "NO3 < 40 mg/L.",
        cadence="weekly",
    ))
    plan.append(CareItem(
        name="Filter maintenance",
        detail=f"Rinse filter media in tank water (never tap water) every 2-4 weeks. "
                f"Your {tank.filter_type} filter moves {tank.filter_gph:.0f} GPH.",
        cadence="every 2-4 weeks",
    ))
    if compat.issues:
        plan.append(CareItem(
            name="Compatibility watch",
            detail="; ".join(i.message for i in compat.issues[:3]),
            cadence="ongoing",
        ))
    if bioload.capacity_ratio > 1.0:
        plan.append(CareItem(
            name="Reduce stocking",
            detail=f"Stocking ratio {bioload.capacity_ratio:.2f} exceeds 1.0\"/gal. "
                    f"Consider removing fish or upgrading the filter.",
            cadence="one-time",
        ))
    if climate is not None:
        plan.append(CareItem(
            name="Temperature control",
            detail=("; ".join(climate.warnings[:2]) or "Temperature is stable."),
            cadence="daily check",
        ))
    if disease is not None and disease.overall_risk >= 25:
        top = max(disease.risks, key=lambda r: r.risk_pct)
        plan.append(CareItem(
            name="Fish Doctor",
            detail=f"Top risk: {top.name} ({top.risk_pct:.0f}%). "
                    + (top.dosages[0].note if top.dosages else top.advice),
            cadence="daily until resolved",
        ))
    if breeding is not None and breeding.boom_risk in ("moderate", "boom"):
        plan.append(CareItem(
            name="Breeding control",
            detail=f"Projected {breeding.projected_population_60d} animals in 60 days "
                    f"({breeding.boom_risk} risk). Plan rehoming or a grow-out tank.",
            cadence="review monthly",
        ))
    return plan

