"""Fish Doctor: deterministic disease-risk scoring & medication dosages.

The module evaluates four common aquarium ailments from tank conditions and
the 30-day nitrogen forecast, then computes exact medication quantities
scaled to the actual water volume (litres):

1. Ich / white-spot      — chilly water, temperature mismatch or swings
2. Fin rot / bacterial   — fin-nippers + high nutrients or overcrowding
3. Ammonia/nitrite burn   — forecast peaks above safe thresholds
4. Osmotic / pH shock     — wide pH/GH incompatibilities in the stock

Everything is pure arithmetic: no randomness, no external services.
"""
from __future__ import annotations

from typing import Dict, List

from ..models import (
    DiseaseReport,
    DiseaseRisk,
    DosageItem,
    SimulationStep,
    Species,
    StockingItem,
    TankConfig,
)

# Species with reduced salinity tolerance: scaleless fish, inverts, plants.
SALT_SENSITIVE_IDS = {
    "corydoras", "pleco",
    "cherry_shrimp", "amano_shrimp",
    "mystery_snail", "nerite_snail",
    "anubias", "java_fern", "hornwort", "java_moss", "anacharis",
}

SAFE_NH3 = 0.25   # ppm
SAFE_NO2 = 0.50   # ppm


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def _severity(risk: float) -> str:
    if risk >= 70:
        return "critical"
    if risk >= 45:
        return "high"
    if risk >= 20:
        return "moderate"
    return "low"


def _present(species_by_id: Dict[str, Species], stocking: List[StockingItem]) -> List[tuple[Species, int]]:
    out = []
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is not None and item.count > 0:
            out.append((sp, item.count))
    return out


def _total_fish_inches(present: List[tuple[Species, int]]) -> float:
    return sum(sp.size_cm * 0.393701 * count for sp, count in present if sp.is_fish)


def assess_disease_risk(
    species_by_id: Dict[str, Species],
    stocking: List[StockingItem],
    tank: TankConfig,
    steps: List[SimulationStep] | None = None,
) -> DiseaseReport:
    present = _present(species_by_id, stocking)
    fish = [(sp, n) for sp, n in present if sp.is_fish]
    has_fish = bool(fish)
    volume_l = max(tank.volume_l, 0.1)

    peak_nh3 = max((s.ammonia_mg_l for s in steps), default=0.0) if steps else 0.0
    peak_no2 = max((s.nitrite_mg_l for s in steps), default=0.0) if steps else 0.0

    salt_names = [sp.name for sp, _ in present if sp.id in SALT_SENSITIVE_IDS]

    risks: List[DiseaseRisk] = []

    # ------------------------------------------------------------------
    # 1. Ich — cold water, cold-sensitive stock, thermal mismatch
    # ------------------------------------------------------------------
    causes: List[str] = []
    risk = 0.0
    if has_fish:
        if tank.temperature_c < 24:
            risk += (24 - tank.temperature_c) * 10
            causes.append(f"Water is {tank.temperature_c:.1f}°C — below the 24°C white-spot comfort floor")
        chilled = [(sp, sp.min_temp_c - tank.temperature_c) for sp, _ in fish
                   if tank.temperature_c < sp.min_temp_c]
        if chilled:
            worst_sp, gap = max(chilled, key=lambda x: x[1])
            risk += gap * 18
            causes.append(f"{worst_sp.name} needs at least {worst_sp.min_temp_c:.0f}°C")
        mids = [(sp.min_temp_c + sp.max_temp_c) / 2 for sp, _ in fish]
        avg_mid = sum(mids) / len(mids) if mids else 25.0
        if avg_mid - tank.temperature_c > 2:
            risk += (avg_mid - tank.temperature_c) * 6
            causes.append("Stock's average comfort midpoint is warmer than the tank")
        if abs(tank.temperature_c - 25.5) > 3.5:
            risk += (abs(tank.temperature_c - 25.5) - 3.5) * 5
            causes.append("Large deviation from the 25–26°C stability band")
    risk = _clamp(risk)
    dosages: List[DosageItem] = []
    if risk >= 25:
        salt_rate = 1.0 if salt_names else 2.0
        dosages.append(DosageItem(
            product="Aquarium salt", quantity=round(salt_rate * volume_l, 1), unit="g",
            note=(f"{salt_rate:g} g/L over {volume_l:.1f} L"
                  + (" (half dose: salt-sensitive stock present)" if salt_names else "")),
        ))
        dosages.append(DosageItem(
            product="Aquarium salt (tablespoons)", quantity=round(salt_rate * volume_l / 15.0, 2),
            unit="tbsp", note="1 tbsp ≈ 15 g; dissolve fully before adding",
        ))
        safe_heat = min((sp.max_temp_c for sp, _ in fish), default=29.0) - 1.0
        if safe_heat >= 27.0:
            dosages.append(DosageItem(
                product="Temperature target", quantity=round(min(29.0, safe_heat), 1), unit="°C",
                note="Raise gradually (≤1°C/hour) and hold for 10–14 days",
            ))
        else:
            dosages.append(DosageItem(
                product="Medication (alternative)", quantity=round(volume_l / 40.0 * 5.0, 1),
                unit="ml", note="Temperature method unsafe for current stock; use an ich medication per label",
            ))
        dosages.append(DosageItem(
            product="Water change", quantity=25, unit="%",
            note="Vacuum the substrate; repeat every 2–3 days during treatment",
        ))
    risks.append(DiseaseRisk(
        id="ich", name="Ich (White Spot Disease)", risk_pct=round(risk, 1),
        severity=_severity(risk), causes=causes,
        advice=("Chilly or unstable water lets Ichthyophthirius multiply. "
                "Treat the whole tank, not just affected fish."),
        dosages=dosages,
    ))

    # ------------------------------------------------------------------
    # 2. Fin rot / bacterial infection
    # ------------------------------------------------------------------
    causes = []
    risk = 0.0
    if has_fish:
        nippers = [(sp, n) for sp, n in fish if sp.fin_nipper]
        if nippers:
            risk += 18 * len(nippers)
            causes.append("Fin-nipping stock: " + ", ".join(sp.name for sp, _ in nippers))
        if peak_nh3 > SAFE_NH3:
            risk += 30
            causes.append(f"Forecast ammonia peak {peak_nh3:.2f} ppm exceeds {SAFE_NH3} ppm")
        if peak_no2 > SAFE_NO2:
            risk += 25
            causes.append(f"Forecast nitrite peak {peak_no2:.2f} ppm exceeds {SAFE_NO2} ppm")
        inches = _total_fish_inches(fish)
        if inches > tank.volume_gal:
            risk += 20
            causes.append(f"Overcrowded: {inches:.1f}\" of fish in {tank.volume_gal:.1f} gal")
        if len(nippers) >= 2:
            risk += 10
            causes.append("Multiple fin-nippers multiply stress injuries")
    risk = _clamp(risk)
    dosages = []
    if risk >= 25:
        salt_rate = 1.0 if salt_names else 2.0
        dosages.append(DosageItem(
            product="Aquarium salt", quantity=round(salt_rate * volume_l, 1), unit="g",
            note=f"{salt_rate:g} g/L; half dose if salt-sensitive stock is present",
        ))
        dosages.append(DosageItem(
            product="Antibacterial (Melafix-type)", quantity=round(volume_l / 38.0 * 5.0, 1), unit="ml",
            note="5 ml per 38 L; follow the product label and remove carbon",
        ))
        dosages.append(DosageItem(
            product="Water change", quantity=50, unit="%",
            note="Do a 50% change now, then 25% daily until regrowth is visible",
        ))
    risks.append(DiseaseRisk(
        id="fin_rot", name="Fin Rot & Bacterial Infection", risk_pct=round(risk, 1),
        severity=_severity(risk), causes=causes,
        advice="Clean water is the primary cure. Treat wounds early before they reach the body.",
        dosages=dosages,
    ))

    # ------------------------------------------------------------------
    # 3. Ammonia / nitrite gill burn
    # ------------------------------------------------------------------
    causes = []
    risk = 0.0
    if has_fish:
        if peak_nh3 > SAFE_NH3:
            risk += 45 + (peak_nh3 - SAFE_NH3) * 100
            causes.append(f"Peak ammonia {peak_nh3:.2f} ppm > {SAFE_NH3} ppm")
        if peak_no2 > SAFE_NO2:
            risk += 30 + (peak_no2 - SAFE_NO2) * 50
            causes.append(f"Peak nitrite {peak_no2:.2f} ppm > {SAFE_NO2} ppm")
    risk = _clamp(risk)
    dosages = []
    if risk >= 25:
        dosages.append(DosageItem(
            product="Water change (immediate)", quantity=50, unit="%",
            note="Match temperature and dechlorinate; repeat daily while peaks persist",
        ))
        dosages.append(DosageItem(
            product="Water conditioner (Prime-type)", quantity=round(volume_l / 200.0 * 5.0, 1), unit="ml",
            note="5 ml per 200 L; binds chlorine/chloramine and detoxifies ammonia",
        ))
        dosages.append(DosageItem(
            product="Feeding", quantity=50, unit="% reduction",
            note="Feed half rations until NH₃ and NO₂ return below 0.25 ppm",
        ))
    risks.append(DiseaseRisk(
        id="gill_burn", name="Ammonia / Nitrite Gill Burn", risk_pct=round(risk, 1),
        severity=_severity(risk), causes=causes,
        advice="Gill tissue burns in elevated nitrogen waste. Dilution and a mature filter are the fix.",
        dosages=dosages,
    ))

    # ------------------------------------------------------------------
    # 4. Osmotic / pH shock
    # ------------------------------------------------------------------
    causes = []
    risk = 0.0
    if has_fish:
        ph_lo = min(sp.min_ph for sp, _ in fish)
        ph_hi = max(sp.max_ph for sp, _ in fish)
        ph_span = ph_hi - ph_lo
        if ph_span > 2.0:
            risk += (ph_span - 2.0) * 14
            causes.append(f"Stock pH ranges span {ph_span:.1f} units ({ph_lo:.1f}–{ph_hi:.1f})")
        off = [sp.name for sp, _ in fish if not (sp.min_ph <= tank.ph <= sp.max_ph)]
        if off:
            risk += min(45, 12 * len(off))
            causes.append("Tank pH outside the comfort range of: " + ", ".join(off[:4]))
        gh_lo = min(sp.min_gh for sp, _ in fish)
        gh_hi = max(sp.max_gh for sp, _ in fish)
        gh_span = gh_hi - gh_lo
        if gh_span > 8:
            risk += (gh_span - 8) * 6
            causes.append(f"GH requirements span {gh_span:.0f}°dGH ({gh_lo:.0f}–{gh_hi:.0f})")
        gh_off = [sp.name for sp, _ in fish if not (sp.min_gh <= tank.gh <= sp.max_gh)]
        if gh_off:
            risk += min(25, 8 * len(gh_off))
            causes.append("Tank GH outside the comfort range of: " + ", ".join(gh_off[:4]))
    risk = _clamp(risk)
    dosages = []
    if risk >= 25:
        dosages.append(DosageItem(
            product="Water change (matched)", quantity=25, unit="%",
            note="Use water with the same temperature and pH; never shock with a full change",
        ))
        dosages.append(DosageItem(
            product="pH adjust rate", quantity=0.2, unit="pH/hour",
            note="Move pH no faster than 0.2 units per hour toward the target",
        ))
        dosages.append(DosageItem(
            product="Buffer (KH)", quantity=round(volume_l / 10.0, 1), unit="g",
            note="1 g per 10 L to stabilise KH; dissolve in a cup of tank water first",
        ))
    risks.append(DiseaseRisk(
        id="osmotic_shock", name="Osmotic / pH Shock", risk_pct=round(risk, 1),
        severity=_severity(risk), causes=causes,
        advice="Keep pH, GH and temperature stable; stability matters more than exact values.",
        dosages=dosages,
    ))

    overall = max((r.risk_pct for r in risks), default=0.0)
    notes: List[str] = []
    if salt_names:
        notes.append("Salt-sensitive species present: " + ", ".join(salt_names[:6])
                     + (", …" if len(salt_names) > 6 else "")
                     + " — use half salt doses or a salt-free alternative.")
    if overall >= 70:
        notes.append("Critical risk: begin treatment now and consider quarantine.")
    elif overall >= 45:
        notes.append("High risk: test water daily and start the lowest-risk treatment first.")
    elif overall >= 20:
        notes.append("Moderate risk: monitor closely; improve water quality before adding stock.")
    else:
        notes.append("No urgent disease risk detected. Maintain weekly water changes.")
    if not has_fish:
        notes.append("No fish stocked — disease risk is not applicable to plants/invertebrates alone.")

    return DiseaseReport(
        risks=risks,
        overall_risk=round(overall, 1),
        salt_sensitive_species=salt_names,
        notes=notes,
    )
