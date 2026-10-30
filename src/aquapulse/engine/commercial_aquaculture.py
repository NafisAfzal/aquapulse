"""Commercial biofloc & aquaculture ROI simulator (v1.0.0).

A real-world planning engine for South Asian / Bangladeshi fish farmers and
hatchery operators.  Supports five commercial species and produces a
week-by-week growth, feed, water-quality and financial schedule.

Scientific core
---------------
Unionized ammonia (the toxic fraction) uses the Emerson pKa equation:

    pKa = 0.09018 + 2729.92 / T_K          (T_K in kelvin)
    f_NH3 = 1 / (1 + 10 ** (pKa - pH))

Biofloc carbon dosing targets a 15:1 C:N ratio: we compute the nitrogen the
feed adds to the system, subtract the feed's own C:N, and dose the remainder
with molasses (≈45 % carbon by mass).

Aeration is sized per system type, and the oxygen balance is checked against
each species' minimum DO to flag night-time / emergency risk.

All arithmetic is deterministic and pure — no external services.
"""
from __future__ import annotations

from math import ceil
from typing import Dict, List

from ..models import (
    CommercialReport,
    CommercialRequest,
    CommercialSpeciesInfo,
    CommercialSummary,
    CommercialWeeklyRow,
)

# Realistic 2026 Bangladeshi farm-gate defaults.
DEFAULT_FEED_PRICE_BDT = 60.0
DEFAULT_FINGERLING_PRICE_BDT = 12.0
DEFAULT_MARKET_PRICE_BDT = 180.0
DEFAULT_MOLASSES_PRICE_BDT = 25.0
DEFAULT_ELECTRICITY_RATE_BDT = 9.0

# Target C:N ratio for heterotrophic biofloc.
TARGET_C_N = 15.0
FEED_CARBON_FRACTION = 0.40      # ~40 % carbon in dry feed
MOLASSES_CARBON_FRACTION = 0.45  # ~45 % carbon in molasses (chita gur)
NITROGEN_RETENTION = 0.30        # fish retain ~30 % of ingested N
O2_PER_KG_FEED = 0.9             # kg O2 consumed per kg feed (biofloc-heavy)
RESPIRATION_PER_KG_FISH = 0.002  # kg O2 per kg biomass per day

# Aeration (L/min per m³ of water) by system type.
AERATION_LPM_PER_M3 = {
    "Biofloc Tank": 6.0,
    "RAS": 4.0,
    "Semi-Intensive Pond": 1.5,
}
SYSTEM_TYPES = list(AERATION_LPM_PER_M3.keys())

COMMERCIAL_SPECIES: List[Dict] = [
    dict(id="monosex_tilapia", name="Monosex Tilapia",
         scientific_name="Oreochromis niloticus", optimal_temp_c=28.0,
         protein_pct=28.0, fcr_target=1.6, survival_rate=0.92,
         typical_target_g=800.0, do_min_mg_l=3.0,
         feed_start=0.040, feed_end=0.018,
         notes="Hardy, fast-growing. Low-protein feed works well in biofloc."),
    dict(id="pabda_catfish", name="Pabda Catfish",
         scientific_name="Ompok pabda", optimal_temp_c=28.0,
         protein_pct=38.0, fcr_target=1.8, survival_rate=0.85,
         typical_target_g=120.0, do_min_mg_l=4.0,
         feed_start=0.050, feed_end=0.022,
         notes="High-value freshwater catfish; needs higher-protein feed."),
    dict(id="gulsha_tengra", name="Gulsha / Tengra",
         scientific_name="Mystus cavasius", optimal_temp_c=28.0,
         protein_pct=35.0, fcr_target=1.7, survival_rate=0.85,
         typical_target_g=60.0, do_min_mg_l=4.0,
         feed_start=0.050, feed_end=0.024,
         notes="Small premium catfish; sensitive to low dissolved oxygen."),
    dict(id="climbing_perch_koi", name="Climbing Perch / Koi",
         scientific_name="Anabas testudineus", optimal_temp_c=28.0,
         protein_pct=30.0, fcr_target=1.5, survival_rate=0.90,
         typical_target_g=250.0, do_min_mg_l=2.5,
         feed_start=0.045, feed_end=0.020,
         notes="Air-breathing labyrinth fish; tolerates low DO and high density."),
    dict(id="golda_prawn", name="Golda Prawn",
         scientific_name="Macrobrachium rosenbergii", optimal_temp_c=27.0,
         protein_pct=35.0, fcr_target=1.9, survival_rate=0.75,
         typical_target_g=100.0, do_min_mg_l=4.5,
         feed_start=0.045, feed_end=0.020,
         notes="Freshwater prawn; needs higher DO and shelter/refuge."),
]
SPECIES_BY_ID: Dict[str, Dict] = {s["id"]: s for s in COMMERCIAL_SPECIES}


def list_commercial_species() -> List[CommercialSpeciesInfo]:
    return [CommercialSpeciesInfo(
        id=s["id"], name=s["name"], scientific_name=s["scientific_name"],
        optimal_temp_c=s["optimal_temp_c"], protein_pct=s["protein_pct"],
        fcr_target=s["fcr_target"], survival_rate=s["survival_rate"],
        typical_target_g=s["typical_target_g"], do_min_mg_l=s["do_min_mg_l"],
        notes=s["notes"],
    ) for s in COMMERCIAL_SPECIES]


def nh3_fraction(ph: float, temp_c: float) -> float:
    """Fraction of TAN that is toxic unionized ammonia (Emerson pKa)."""
    t_k = temp_c + 273.15
    pka = 0.09018 + 2729.92 / t_k
    return 1.0 / (1.0 + 10.0 ** (pka - ph))


def simulate_commercial(req: CommercialRequest) -> CommercialReport:
    meta = SPECIES_BY_ID.get(req.species_id)
    if meta is None:
        meta = SPECIES_BY_ID["monosex_tilapia"]
    species = CommercialSpeciesInfo(
        id=meta["id"], name=meta["name"], scientific_name=meta["scientific_name"],
        optimal_temp_c=meta["optimal_temp_c"], protein_pct=meta["protein_pct"],
        fcr_target=meta["fcr_target"], survival_rate=meta["survival_rate"],
        typical_target_g=meta["typical_target_g"], do_min_mg_l=meta["do_min_mg_l"],
        notes=meta["notes"],
    )

    volume_m3 = max(req.volume_l, 1.0) / 1000.0
    duration = max(1, req.duration_days)
    protein_frac = meta["protein_pct"] / 100.0
    start_rate = meta["feed_start"]
    end_rate = meta["feed_end"]
    n_weeks = ceil(duration / 7.0)

    f_nh3 = nh3_fraction(req.ph, req.temperature_c)
    aeration_lpm = AERATION_LPM_PER_M3.get(req.system_type, 6.0) * volume_m3

    # Feed C:N (carbon fraction vs. protein-derived N).
    n_per_kg_feed = protein_frac / 6.25
    feed_cn = FEED_CARBON_FRACTION / n_per_kg_feed if n_per_kg_feed > 0 else 99.0
    carbon_needed_per_kg_feed = max(0.0, (TARGET_C_N - feed_cn) * n_per_kg_feed * (1.0 - NITROGEN_RETENTION))

    rows: List[CommercialWeeklyRow] = []
    cumulative_feed = 0.0
    max_biomass = 0.0
    max_feed_day = 0.0
    max_molasses_g = 0.0
    max_tan = 0.0
    max_nh3 = 0.0
    max_aeration = 0.0

    for week in range(1, n_weeks + 1):
        day = min(week * 7, duration)
        progress = day / duration
        # Linear growth model (deterministic).
        weight_g = req.initial_weight_g + (req.target_weight_g - req.initial_weight_g) * progress
        survival = meta["survival_rate"] ** progress
        biomass_kg = req.stocking_count * survival * weight_g / 1000.0
        feed_rate = start_rate - (start_rate - end_rate) * progress
        feed_kg_day = biomass_kg * feed_rate
        cumulative_feed += feed_kg_day

        # Nitrogen & biofloc carbon.
        n_excreted_kg = feed_kg_day * n_per_kg_feed * (1.0 - NITROGEN_RETENTION)
        tan_mg_l = n_excreted_kg * 1e6 / max(req.volume_l, 1.0)  # mg/L
        nh3_mg_l = tan_mg_l * f_nh3
        carbon_needed_kg = carbon_needed_per_kg_feed * feed_kg_day
        molasses_g_day = carbon_needed_kg / MOLASSES_CARBON_FRACTION * 1000.0 if carbon_needed_kg > 0 else 0.0

        # Dissolved oxygen estimate: saturated ~8 mg/L at 20°C, minus temp and load.
        do_mg_l = max(0.5, 8.0 - (req.temperature_c - 20.0) * 0.15 - tan_mg_l * 0.05 - nh3_mg_l * 0.5)

        rows.append(CommercialWeeklyRow(
            week=week, day=day,
            weight_g=round(weight_g, 1),
            biomass_kg=round(biomass_kg, 2),
            survival_pct=round(survival * 100.0, 1),
            feed_kg_day=round(feed_kg_day, 2),
            feed_rate_pct=round(feed_rate * 100.0, 2),
            cumulative_feed_kg=round(cumulative_feed, 2),
            tan_mg_l=round(tan_mg_l, 3),
            nh3_mg_l=round(nh3_mg_l, 4),
            molasses_g_day=round(molasses_g_day, 1),
            aeration_lpm=round(aeration_lpm, 1),
            do_mg_l=round(do_mg_l, 2),
        ))

        max_biomass = max(max_biomass, biomass_kg)
        max_feed_day = max(max_feed_day, feed_kg_day)
        max_molasses_g = max(max_molasses_g, molasses_g_day)
        max_tan = max(max_tan, tan_mg_l)
        max_nh3 = max(max_nh3, nh3_mg_l)
        max_aeration = max(max_aeration, aeration_lpm)

    final = rows[-1]
    harvest_biomass = final.biomass_kg
    total_molasses_kg = round(sum(r.molasses_g_day for r in rows) / 1000.0 * 7.0, 2)
    total_feed_kg = round(final.cumulative_feed_kg, 2)

    # Financials.
    fingerling_cost = req.stocking_count * req.fingerling_price_bdt
    feed_cost = total_feed_kg * req.feed_price_bdt
    molasses_cost = total_molasses_kg * req.molasses_price_bdt
    # Aeration blower: ~0.025 kW per L/min, running 24 h.
    kwh_per_day = aeration_lpm * 0.025 * 24.0
    electricity_cost = kwh_per_day * duration * req.electricity_rate_bdt
    probiotics_cost = round(total_feed_kg * 5.0, 2)
    labor_cost = duration * 150.0
    total_cost = (fingerling_cost + feed_cost + electricity_cost + molasses_cost +
                  probiotics_cost + labor_cost)
    gross_revenue = harvest_biomass * req.market_price_bdt
    net_profit = gross_revenue - total_cost
    roi_pct = (net_profit / total_cost * 100.0) if total_cost > 0 else 0.0
    break_even = (total_cost / harvest_biomass) if harvest_biomass > 0 else 0.0

    # FCR from the actual feed:gain.
    gain_kg = harvest_biomass - (req.stocking_count * req.initial_weight_g / 1000.0)
    fcr = total_feed_kg / gain_kg if gain_kg > 0 else meta["fcr_target"]

    warnings: List[str] = []
    if max_nh3 > 0.05:
        warnings.append(f"Peak toxic NH₃ {max_nh3:.3f} mg/L exceeds the 0.05 mg/L safe threshold "
                        f"— reduce feed or raise pH-stable alkalinity.")
    if final.do_mg_l < species.do_min_mg_l:
        warnings.append(f"Projected DO {final.do_mg_l:.1f} mg/L is below the {species.do_min_mg_l:.1f} "
                        f"mg/L minimum for {species.name} — increase aeration.")
    if abs(req.temperature_c - species.optimal_temp_c) > 4:
        warnings.append(f"Culture temperature {req.temperature_c:.0f}°C is far from the "
                        f"{species.optimal_temp_c:.0f}°C optimum for {species.name}.")
    if req.system_type == "Biofloc Tank":
        warnings.append("Night-time DO risk: biofloc consumes O₂ continuously — keep a backup "
                        "blower/generator and monitor dawn DO.")
    if roi_pct <= 0:
        warnings.append("Projected ROI is ≤ 0% — review market price, feed cost or survival assumptions.")

    summary = CommercialSummary(
        harvest_biomass_kg=round(harvest_biomass, 2),
        survival_pct=final.survival_pct,
        fcr=round(fcr, 2),
        total_feed_kg=total_feed_kg,
        total_molasses_kg=total_molasses_kg,
        fingerling_cost_bdt=round(fingerling_cost, 2),
        feed_cost_bdt=round(feed_cost, 2),
        electricity_cost_bdt=round(electricity_cost, 2),
        molasses_cost_bdt=round(molasses_cost, 2),
        probiotics_cost_bdt=round(probiotics_cost, 2),
        labor_cost_bdt=round(labor_cost, 2),
        total_cost_bdt=round(total_cost, 2),
        gross_revenue_bdt=round(gross_revenue, 2),
        net_profit_bdt=round(net_profit, 2),
        roi_pct=round(roi_pct, 1),
        break_even_bdt_per_kg=round(break_even, 2),
        nh3_fraction=round(f_nh3, 5),
        tan_mg_l=round(max_tan, 3),
        nh3_mg_l=round(max_nh3, 4),
        aeration_lpm=round(max_aeration, 1),
        max_biomass_kg=round(max_biomass, 2),
        max_daily_feed_kg=round(max_feed_day, 2),
        max_daily_molasses_g=round(max_molasses_g, 1),
        warnings=warnings,
    )

    return CommercialReport(request=req, species=species, rows=rows, summary=summary)
