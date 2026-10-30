"""30-day discrete nitrogen-cycle simulation.

Daily discrete differential simulation of the classic fish-in cycle:

    NH3 (ammonia) --Nitrosomonas--> NO2 (nitrite) --Nitrobacter--> NO3 (nitrate)

The simulation is purely algebraic (Euler steps, one per day) so each
30-day run completes in well under 10 ms.

State vector per day:
    ammonia_mg_l, nitrite_mg_l, nitrate_mg_l, ph,
    oxygen_mg_l, bacteria_aob, bacteria_nob, plant_uptake_nitrate

Dynamics
--------
Ammonia production
    P_nh3 = (bioload_points * 0.02 + food_amount_g * 0.08) * feeding_per_day
    expressed as mg/day; divided by volume to get mg/L.
Nitrosomonas (AOB) growth
    Monod-ish saturation: rate = k_aob * nh3 / (kh_nh3 + nh3); colony grows
    toward a carrying capacity proportional to available surface area.
Nitrobacter (NOB) growth
    rate = k_nob * no2 / (kh_no2 + no2); converts nitrite to nitrate.
Bacterial growth
    dB/dt = rate * colony * (1 - colony / capacity)
Plant uptake
    Uptake is proportional to plant bioload and nitrate concentration,
    capped by a light/CO2 ceiling.
Water change
    Every `water_change_freq_days` days, all dissolved concentrations are
    multiplied by (1 - pct/100). Bacteria survive a water change.
pH drift
    Nitrification releases acid; nitrate buffering with the substrate
    pulls pH down slightly over time.
"""
from __future__ import annotations

from typing import Dict, List

from ..models import Species, StockingItem, TankConfig, SimulationStep

# --- tunable constants (calibrated to behave like a real 30-day cycle) ---
K_AOB = 1.1            # max conversion rate per day at saturation
KH_NH3 = 0.05          # half-saturation for ammonia (mg/L)
K_NOB = 1.0            # max nitrite conversion rate
KH_NO2 = 0.15          # half-saturation for nitrite (mg/L)
AOB_HALF = 1.2         # bacteria population at which conversion is half-max
NOB_HALF = 1.5
GROWTH_AOB = 1.4       # colony growth rate /day
GROWTH_NOB = 1.1       # colony growth rate /day
NH3_PER_POINT = 0.08   # mg ammonia per bioload point per feeding
NH3_PER_FOOD = 0.15    # mg ammonia per gram of food per feeding
PLANT_UPTAKE_MAX = 0.6  # max mg/L of nitrate removed per day by plants
O2_MAX = 8.5
O2_AMMONIA_PENALTY = 1.6  # mg/L O2 lost per mg/L ammonia
PH_DRIFT_PER_NITRATE = 0.0008
SUBSTRATE_SURFACE_AREA = {
    "bare": 0.5, "sand": 0.8, "gravel": 1.0, "soil": 1.6,
}


def simulate_nitrogen_cycle(
    species_by_id: Dict[str, Species],
    stocking: List[StockingItem],
    tank: TankConfig,
    days: int = 30,
) -> List[SimulationStep]:
    vol = max(tank.volume_gal, 0.1)

    bioload_points = 0.0
    plant_biomass = 0.0
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is None:
            continue
        if sp.is_fish:
            bioload_points += sp.bioload_factor * item.count
        elif sp.is_plant:
            plant_biomass += item.count

    surface = SUBSTRATE_SURFACE_AREA.get(tank.substrate, 1.0)
    bacteria_cap = 12.0 * surface * (vol / 10.0)
    ammonia_prod_mg_day = (bioload_points * NH3_PER_POINT
                           + tank.food_amount_g * NH3_PER_FOOD * tank.feeding_level) * tank.feeding_per_day

    # Starting state: fresh, essentially un-cycled tank
    ammonia = 0.05
    nitrite = 0.0
    nitrate = 5.0
    aob = 0.01 if tank.planted else 0.005
    nob = 0.008 if tank.planted else 0.003
    ph = tank.ph
    water_change_pct = tank.water_change_pct
    water_change_freq = tank.water_change_freq_days

    steps: List[SimulationStep] = []
    for day in range(1, days + 1):
        # 1. Daily ammonia input (mg/L added to the system)
        ammonia += ammonia_prod_mg_day / vol

        # 2. AOB conversion ammonia -> nitrite (mg/L).  Saturation is on both
        #    the substrate (Monod) and the colony population, so sparse early
        #    colonies convert slowly and ammonia accumulates -> the classic
        #    fish-in ammonia spike.
        conv_aob = (K_AOB
                    * ammonia / (KH_NH3 + ammonia)
                    * aob / (aob + AOB_HALF))
        conv_aob = min(conv_aob, ammonia)
        ammonia -= conv_aob
        nitrite += conv_aob

        # 3. NOB conversion nitrite -> nitrate (mg/L)
        conv_nob = (K_NOB
                    * nitrite / (KH_NO2 + nitrite)
                    * nob / (nob + NOB_HALF))
        conv_nob = min(conv_nob, nitrite)
        nitrite -= conv_nob
        nitrate += conv_nob

        # 4. Plant nitrate uptake
        plant_uptake = 0.0
        if plant_biomass > 0:
            plant_uptake = min(nitrate, PLANT_UPTAKE_MAX * plant_biomass * 0.05
                               * min(1.0, nitrate / 20.0))
            nitrate -= plant_uptake

        # 5. Bacterial colony growth (logistic toward capacity)
        aob += GROWTH_AOB * aob * (1 - aob / bacteria_cap) * (ammonia + 0.02)
        nob += GROWTH_NOB * nob * (1 - nob / bacteria_cap) * (nitrite + 0.02)
        aob = min(aob, bacteria_cap)
        nob = min(nob, bacteria_cap)

        # 6. Oxygen balance
        oxygen = max(2.0, O2_MAX - ammonia * O2_AMMONIA_PENALTY - nitrite * 0.4)

        # 7. pH drift from accumulating nitrate (nitrification acidifies)
        ph = max(4.5, ph - PH_DRIFT_PER_NITRATE * nitrate)

        water_changed = False
        if day % water_change_freq == 0:
            keep = 1.0 - (water_change_pct / 100.0)
            ammonia *= keep
            nitrite *= keep
            nitrate *= keep
            water_changed = True

        # Clamp numerical dust
        ammonia = max(0.0, ammonia)
        nitrite = max(0.0, nitrite)
        nitrate = max(0.0, nitrate)

        steps.append(SimulationStep(
            day=day,
            ammonia_mg_l=round(ammonia, 4),
            nitrite_mg_l=round(nitrite, 4),
            nitrate_mg_l=round(nitrate, 3),
            ph=round(ph, 3),
            oxygen_mg_l=round(oxygen, 3),
            bacteria_aob=round(aob, 4),
            bacteria_nob=round(nob, 4),
            plant_uptake_nitrate=round(plant_uptake, 4),
            water_changed=water_changed,
        ))

    return steps


def summarize_cycle(steps: List[SimulationStep]) -> Dict:
    if not steps:
        return {"ok": False, "reason": "empty simulation"}
    peak_ammonia = max(s.ammonia_mg_l for s in steps)
    peak_nitrite = max(s.nitrite_mg_l for s in steps)
    final = steps[-1]
    peak_ammonia_day = max(range(len(steps)), key=lambda i: steps[i].ammonia_mg_l) + 1
    peak_nitrite_day = max(range(len(steps)), key=lambda i: steps[i].nitrite_mg_l) + 1
    stable = (final.ammonia_mg_l < 0.25 and final.nitrite_mg_l < 0.25)
    return {
        "ok": True,
        "peak_ammonia_mg_l": round(peak_ammonia, 3),
        "peak_ammonia_day": peak_ammonia_day,
        "peak_nitrite_mg_l": round(peak_nitrite, 3),
        "peak_nitrite_day": peak_nitrite_day,
        "final_nitrate_mg_l": final.nitrate_mg_l,
        "final_ph": final.ph,
        "final_oxygen_mg_l": final.oxygen_mg_l,
        "cycled_by_day_30": stable,
    }
