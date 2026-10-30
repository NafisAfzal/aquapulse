"""Breeding forecast: prolific breeders, fry survival and 60-day growth.

The model is deliberately simple and deterministic:

* Fry survival starts at 55%.
* Dense plant cover adds a bonus (moss and floating plants are best).
* Predatory / large tank-mates subtract a penalty.
* Each prolific species contributes fry based on a per-month rate, the
  number of mature females and the survival percentage over 60 days.

The projected population is then compared with tank volume to warn about
an impending overstock "population boom".
"""
from __future__ import annotations

from typing import Dict, List

from ..models import (
    BreederInfo,
    BreedingReport,
    Species,
    StockingItem,
    TankConfig,
)

# species id -> (label, fry per month per mature female)
PROLIFIC: Dict[str, Dict] = {
    "guppy": {"kind": "livebearer", "fry_per_month": 20},
    "molly": {"kind": "livebearer", "fry_per_month": 24},
    "platy": {"kind": "livebearer", "fry_per_month": 18},
    "cherry_shrimp": {"kind": "shrimp", "fry_per_month": 14},
    "pleco": {"kind": "egg_layer", "fry_per_month": 20},
    "mystery_snail": {"kind": "snail", "fry_per_month": 25},
}

# plant id -> cover points per plant (capped per species and overall)
COVER_POINTS = {
    "java_moss": 10,
    "hornwort": 9,
    "java_fern": 7,
    "anacharis": 7,
    "anubias": 4,
}
DEFAULT_COVER = 3
MAX_COVER_BONUS = 35
MAX_PREDATION = 45

PREDATOR_IDS = {"angelfish", "betta", "oscar", "gourami"}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def predict_breeding(
    species_by_id: Dict[str, Species],
    stocking: List[StockingItem],
    tank: TankConfig,
) -> BreedingReport:
    present: List[tuple[Species, int]] = []
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is not None and item.count > 0:
            present.append((sp, item.count))

    fish = [(sp, n) for sp, n in present if sp.is_fish]
    animals = [(sp, n) for sp, n in present if not sp.is_plant]

    current_population = sum(n for _, n in animals)
    current_inches = sum(sp.size_cm * 0.393701 * n for sp, n in fish)

    # ---- Plant cover bonus -------------------------------------------------
    cover_bonus = 0.0
    for sp, n in present:
        if sp.is_plant:
            cover_bonus += min(n, 3) * COVER_POINTS.get(sp.id, DEFAULT_COVER)
    cover_bonus = min(MAX_COVER_BONUS, cover_bonus)

    # ---- Predation penalty -------------------------------------------------
    predation = 0.0
    predators: List[str] = []
    for sp, n in fish:
        if sp.size_cm >= 8 or sp.aggression_rating >= 0.5 or sp.id in PREDATOR_IDS:
            predation += 10 + 8 * sp.aggression_rating
            predators.append(sp.name)
    predation = min(MAX_PREDATION, predation)

    survival = round(_clamp(55 + cover_bonus - predation, 5, 95), 1)

    # ---- Breeder offspring over 60 days ------------------------------------
    details: List[BreederInfo] = []
    offspring_total = 0
    projected_inches = current_inches
    for sp, n in present:
        meta = PROLIFIC.get(sp.id)
        if meta is None:
            continue
        kind = meta["kind"]
        if kind == "livebearer":
            mature_females = n * 0.5
        elif kind == "shrimp":
            mature_females = n * 0.4
        elif kind == "snail":
            mature_females = n * 0.5
        else:  # egg_layer: assume pairs
            mature_females = max(1.0, n // 2) if n >= 2 else 0.0
        fry = mature_females * meta["fry_per_month"] * 2.0 * (survival / 100.0)
        fry_i = int(round(fry))
        offspring_total += fry_i
        projected_inches += fry_i * sp.size_cm * 0.393701
        details.append(BreederInfo(
            species_id=sp.id,
            name=sp.name,
            emoji=sp.emoji,
            count=n,
            offspring_60d=fry_i,
        ))

    projected_population = current_population + offspring_total

    # ---- Overstock risk ----------------------------------------------------
    volume_gal = max(tank.volume_gal, 0.1)
    if not details:
        boom_risk = "none"
    elif projected_inches > volume_gal * 1.25:
        boom_risk = "boom"
    elif projected_inches > volume_gal:
        boom_risk = "moderate"
    else:
        boom_risk = "stable"

    notes: List[str] = []
    if not details:
        notes.append("No prolific breeders stocked — no population explosion expected.")
    else:
        names = ", ".join(d.name for d in details)
        notes.append(
            f"{names} can produce ~{offspring_total} fry in 60 days "
            f"at {survival:.0f}% survival."
        )
    if details and cover_bonus < 10:
        notes.append("Add java moss or floating plants to give fry hiding cover.")
    if predators:
        notes.append("Fry predators present: " + ", ".join(sorted(set(predators))) + ".")
    if boom_risk == "boom":
        notes.append(
            f"Population boom warning: projected {projected_inches:.0f}\" of fish "
            f"in a {volume_gal:.0f} gal tank. Plan rehoming or a larger tank."
        )
    elif boom_risk == "moderate":
        notes.append("Projected stock will approach the tank's capacity within 60 days.")
    if details and survival >= 80:
        notes.append("Excellent fry survival — consider a dedicated grow-out tank.")

    return BreedingReport(
        prolific_species=details,
        fry_survival_pct=survival,
        projected_population_60d=projected_population,
        current_population=current_population,
        boom_risk=boom_risk,
        cover_bonus_pct=round(cover_bonus, 1),
        predation_penalty_pct=round(predation, 1),
        notes=notes,
    )
