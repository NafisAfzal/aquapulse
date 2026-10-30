"""Bioload and stocking-density calculations.

Rules of thumb:
* 1 inch of fish per gallon (classical heuristic).
* Each species has ``bioload_factor``; total points = sum(size_cm/2.54 * factor * count).
* Filter capacity = filter_gph / tank_volume_gal.  >= 4 means "adequate"; < 4 means
  "underfiltered" (a minimum of 4× turnover is recommended).
* Swim-zone crowding: each zone gets its own running inches-of-fish total.
  > 50 % of tank volume worth of inches in a single zone is a warning.
"""
from __future__ import annotations

from typing import Dict, List

from ..models import BioloadResult, StockingItem, TankConfig, SwimZone, Species


CM_TO_INCH = 0.393701


def compute_bioload(
    species_by_id: Dict[str, Species],
    stocking: List[StockingItem],
    tank: TankConfig,
) -> BioloadResult:
    total_inches = 0.0
    total_points = 0.0
    zone_inches: Dict[str, float] = {z.value: 0.0 for z in SwimZone}
    # Zone capacity heuristic: 50% of volume-gal worth of inches per zone
    vol = tank.volume_gal
    zone_capacity: Dict[str, float] = {z: vol * 0.5 if vol > 0 else 0.0 for z in zone_inches}

    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is None or not sp.is_fish:
            continue

        fish_inches = sp.size_cm * CM_TO_INCH * item.count
        total_inches += fish_inches
        total_points += sp.bioload_factor * item.count
        zone_inches[sp.swim_zone.value] += fish_inches

    filter_ratio = tank.filter_gph / vol if vol > 0 else 0.0
    if filter_ratio >= 4:
        rating = "adequate"
    elif filter_ratio >= 2:
        rating = "marginal"
    else:
        rating = "underfiltered"

    warnings: List[str] = []
    if total_inches > vol:
        warnings.append(f"Overstocked: {total_inches:.1f}\" of fish in {vol:.1f} gal "
                        f"(recommended max {vol:.1f}\")")
    for zone_name, inch_count in zone_inches.items():
        cap = zone_capacity.get(zone_name, 0)
        if cap > 0 and inch_count > cap:
            warnings.append(f"{zone_name} zone crowded: {inch_count:.1f}\" in "
                            f"{cap:.1f}\" capacity")
    if filter_ratio < 2:
        warnings.append(f"Filter too small for volume "
                        f"({filter_ratio:.1f}x turnover, recommend ≥ 4x)")

    return BioloadResult(
        volume_gal=vol,
        volume_l=vol * 3.785411784,
        total_fish_inches=round(total_inches, 2),
        total_bioload_points=round(total_points, 2),
        filter_capacity_points=round(filter_ratio, 2),
        capacity_ratio=round(total_inches / vol, 3) if vol > 0 else 0.0,
        stocking_rating=rating,
        zone_crowding=zone_inches,
        zone_capacity=zone_capacity,
        warnings=warnings,
    )
