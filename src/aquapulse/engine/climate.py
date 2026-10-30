"""Climate presets and heater / cooling-fan sizing.

Three realistic room climates are modelled:

* ``tropical_summer``  — 30–33°C room (Dhaka summer). Evaporative fan
  cooling drops the water ~2.5°C, but a fan alone cannot beat a heatwave.
* ``winter_indoor``    — 18–20°C room. A heater is mandatory; we size it
  with the 1 W per litre per 5°C-rise rule, rounded up to 25 W steps.
* ``climate_controlled`` — 24–25°C room, the easy case.

The module only does arithmetic; no external services.
"""
from __future__ import annotations

from typing import Dict, List

from ..models import ClimateReport, Species, StockingItem, TankConfig

CLIMATE_PRESETS: Dict[str, Dict] = {
    "tropical_summer": {
        "name": "Tropical Summer (30–33°C)",
        "room_temp_c": 31.5,
        "description": "Hot, humid room. Evaporative cooling needed.",
    },
    "winter_indoor": {
        "name": "Winter Indoor (18–20°C)",
        "room_temp_c": 19.0,
        "description": "Cool room. A heater is required for tropical stock.",
    },
    "climate_controlled": {
        "name": "Climate-Controlled (24–25°C)",
        "room_temp_c": 24.5,
        "description": "Stable room temperature year-round.",
    },
}
DEFAULT_CLIMATE = "climate_controlled"

WATTS_PER_LITER_PER_5C = 1.0
FAN_COOLING_C = 2.5
HEATER_STEP_W = 25


def list_climate_presets() -> List[Dict]:
    return [
        {"id": key, "name": meta["name"], "room_temp_c": meta["room_temp_c"],
         "description": meta["description"]}
        for key, meta in CLIMATE_PRESETS.items()
    ]


def evaluate_climate(
    species_by_id: Dict[str, Species],
    stocking: List[StockingItem],
    tank: TankConfig,
) -> ClimateReport:
    preset = CLIMATE_PRESETS.get(tank.room_climate, CLIMATE_PRESETS[DEFAULT_CLIMATE])
    preset_id = tank.room_climate if tank.room_climate in CLIMATE_PRESETS else DEFAULT_CLIMATE
    room = preset["room_temp_c"]
    target = tank.temperature_c
    volume_l = max(tank.volume_l, 0.1)

    # 1 W/L raises ~5°C; round up to the next commercially available size.
    delta = target - room
    if delta > 0:
        raw_watts = volume_l * (delta / 5.0) * WATTS_PER_LITER_PER_5C
        heater_watts = max(HEATER_STEP_W, int(-(-raw_watts // HEATER_STEP_W) * HEATER_STEP_W))
    else:
        heater_watts = 0

    fan_recommended = (room - target) > 1.0
    expected = room - FAN_COOLING_C if fan_recommended else room

    warnings: List[str] = []
    conflicts: List[str] = []

    if heater_watts > 0:
        warnings.append(
            f"Install a {heater_watts} W heater "
            f"({volume_l:.0f} L × {delta:.1f}°C rise, 1 W/L per 5°C rule)."
        )
    else:
        warnings.append("No heater required at this room temperature.")

    if fan_recommended:
        warnings.append(
            f"Room is {room:.1f}°C vs a {target:.1f}°C target: add an evaporative "
            f"cooling fan (≈−{FAN_COOLING_C:.1f}°C). Top up evaporation daily."
        )
        if expected > target + 0.5:
            warnings.append(
                f"Even with a fan the water may sit at {expected:.1f}°C — "
                "consider air-conditioning or a chiller."
            )
    elif room > target + 0.2:
        warnings.append("Room runs slightly warm; monitor temperature daily.")

    # Thermal conflicts for the actual stock.
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is None or item.count <= 0 or sp.is_plant:
            continue
        if room > sp.max_temp_c:
            conflicts.append(
                f"{sp.name} may overheat: room {room:.0f}°C exceeds its "
                f"{sp.max_temp_c:.0f}°C maximum."
            )
        elif room < sp.min_temp_c and heater_watts == 0:
            conflicts.append(
                f"{sp.name} needs at least {sp.min_temp_c:.0f}°C but the room is {room:.0f}°C."
            )
    warnings.extend(conflicts)

    return ClimateReport(
        preset_id=preset_id,
        preset_name=preset["name"],
        room_temp_c=round(room, 1),
        target_temp_c=round(target, 1),
        heater_watts_required=heater_watts,
        cooling_fan_recommended=fan_recommended,
        expected_temp_after_mitigation_c=round(expected, 1),
        warnings=warnings,
        species_thermal_conflicts=conflicts,
    )
