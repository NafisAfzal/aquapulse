"""Dual-currency (USD / BDT) budget builder.

Prices are realistic 2026 retail estimates for the Bangladesh local market
and are converted to Bangladeshi Taka (BDT) with :data:`USD_TO_BDT`.
Hardware is sized from the actual tank and climate report, so a winter
build automatically includes a correctly sized heater while a tropical
summer build includes a cooling fan.
"""
from __future__ import annotations

from math import ceil
from typing import Dict, List, Tuple

from ..models import BudgetItem, ClimateReport, Species, StockingItem, TankConfig

USD_TO_BDT = 120.0

# Realistic Bangladesh retail hardware pricing (USD)
AQUARIUM_GLASS_PER_GAL = 0.50      # ~$0.50/gal glass cost
FILTER_HOB_BASE = 5.00             # ~$600 HOB filter
FILTER_HOB_PER_GPH = 0.08          # ~$0.08/GPH
FILTER_SPONGE_BASE = 3.00          # ~$360 sponge filter
FILTER_SPONGE_PER_GPH = 0.04       # ~$0.04/GPH
LED_LIGHT_PLANTED = 5.00           # ~$600 full-spectrum planted LED
LED_LIGHT_BASIC = 2.50             # ~$300 basic LED
SUBSTRATE_BAG = 2.50               # ~$300 per bag (sand/gravel/soil)
HEATER_PER_WATT = 0.12             # ~$0.12/W (~$12 for 100W), min $5
COOLING_FAN = 3.00                 # ~$360 clip-on evaporative fan
WATER_TEST_KIT = 3.50              # ~$420
WATER_CONDITIONER = 1.00           # ~$120
FISH_FOOD = 1.00                   # ~$120 monthly supply
GRAVEL_VACUUM_NET = 2.00           # ~$240
PLANT_FERTILIZER = 2.00            # ~$240

SUBSTRATE_UNIT_COST = {
    "bare": 0.0,
    "sand": SUBSTRATE_BAG,
    "gravel": SUBSTRATE_BAG,
    "soil": SUBSTRATE_BAG,
}


def _money(value: float) -> float:
    return round(max(0.0, value), 2)


def build_budget(
    tank: TankConfig,
    stocking: List[StockingItem],
    species_by_id: Dict[str, Species],
    climate: ClimateReport | None = None,
    exchange_rate: float = USD_TO_BDT,
) -> List[BudgetItem]:
    items: List[BudgetItem] = []

    def add(item: str, category: str, cost_usd: float, qty: float = 1, note: str = "") -> None:
        cost_usd = _money(cost_usd)
        items.append(BudgetItem(
            item=item,
            category=category,
            cost_usd=cost_usd,
            cost_bdt=round(cost_usd * exchange_rate, 2),
            qty=qty,
            note=note,
        ))

    # ---- Hardware --------------------------------------------------------
    gallons = max(tank.volume_gal, 1.0)
    add(
        f"{gallons:.1f} gal aquarium",
        "hardware",
        max(AQUARIUM_GLASS_PER_GAL, gallons * 0.50),
        note=f"{tank.length_in:.0f}x{tank.width_in:.0f}x{tank.height_in:.0f} in glass/acrylic",
    )
    if tank.filter_type == "sponge":
        add(
            "Sponge filter",
            "hardware",
            max(FILTER_SPONGE_BASE, tank.filter_gph * FILTER_SPONGE_PER_GPH),
            note=f"{tank.filter_gph:.0f} GPH air-driven turnover",
        )
    else:
        add(
            f"Filter ({tank.filter_type})",
            "hardware",
            max(FILTER_HOB_BASE, tank.filter_gph * FILTER_HOB_PER_GPH),
            note=f"{tank.filter_gph:.0f} GPH turnover",
        )
    add(
        "LED light fixture",
        "hardware",
        LED_LIGHT_PLANTED if tank.planted else LED_LIGHT_BASIC,
        note="full-spectrum planted LED" if tank.planted else "basic LED",
    )

    substrate_cost = SUBSTRATE_UNIT_COST.get(tank.substrate, SUBSTRATE_BAG)
    if substrate_cost > 0:
        bags = max(1, ceil(gallons / 10.0))
        add(
            f"Substrate ({tank.substrate})",
            "hardware",
            substrate_cost,
            qty=bags,
            note=f"{bags} bag(s), ~1 lb per gallon",
        )

    if climate is not None and climate.heater_watts_required > 0:
        add(
            f"Heater ({climate.heater_watts_required} W)",
            "hardware",
            max(5.0, climate.heater_watts_required * HEATER_PER_WATT),
            note="adjustable thermostat, 1 W/L per 5 C rule",
        )
    if climate is not None and climate.cooling_fan_recommended:
        add(
            "Evaporative cooling fan",
            "hardware",
            COOLING_FAN,
            note="clip-on fan, to reduce temperature; top up evaporation daily",
        )

    add("Water test kit", "consumables", WATER_TEST_KIT, note="NH3 / NO2 / NO3 / pH")
    add("Water conditioner", "consumables", WATER_CONDITIONER, note="dechlorinator / ammonia binder")
    add("Fish food", "consumables", FISH_FOOD, note="monthly supply")
    add("Gravel vacuum & net", "hardware", GRAVEL_VACUUM_NET, note="maintenance basics")
    if tank.planted:
        add("Liquid plant fertilizer", "consumables", PLANT_FERTILIZER, note="macro + micro")

    # ---- Livestock & plants ---------------------------------------------
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is None or item.count <= 0:
            continue
        category = "plants" if sp.is_plant else "livestock"
        add(sp.name, category, sp.price_usd, qty=item.count,
            note=f"{item.count} x {sp.emoji}")

    return items


def budget_totals(items: List[BudgetItem]) -> Tuple[float, float]:
    """Return (USD, BDT) totals, accounting for quantity."""
    usd = sum(i.cost_usd * i.qty for i in items)
    bdt = sum(i.cost_bdt * i.qty for i in items)
    return round(usd, 2), round(bdt, 2)
