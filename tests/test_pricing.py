"""Tests for the dual-currency budget builder."""
import pytest

from aquapulse.database import Database
from aquapulse.engine.climate import evaluate_climate
from aquapulse.engine.pricing import USD_TO_BDT, build_budget, budget_totals
from aquapulse.models import StockingItem, TankConfig


@pytest.fixture(scope="module")
def smap():
    return {s.id: s for s in Database().get_species()}


def make_tank(**kw) -> TankConfig:
    base = dict(length_in=24, width_in=12, height_in=16, filter_gph=200,
                temperature_c=25, ph=7.0, gh=8)
    base.update(kw)
    return TankConfig(**base)


def build(smap, tank, stocking):
    climate = evaluate_climate(smap, stocking, tank)
    items = build_budget(tank, stocking, smap, climate)
    return items, climate


def test_bdt_conversion_on_every_line(smap):
    tank = make_tank()
    items, _ = build(smap, tank, [StockingItem(species_id="guppy", count=4)])
    assert USD_TO_BDT == 120.0
    for item in items:
        assert item.cost_bdt == pytest.approx(item.cost_usd * USD_TO_BDT, abs=0.01)


def test_winter_budget_includes_sized_heater(smap):
    tank = make_tank(room_climate="winter_indoor")
    items, climate = build(smap, tank, [StockingItem(species_id="guppy", count=4)])
    heaters = [i for i in items if i.item.startswith("Heater")]
    assert climate.heater_watts_required == 100
    assert heaters and "100 W" in heaters[0].item
    assert not any("cooling fan" in i.item.lower() for i in items)


def test_tropical_budget_includes_fan_not_heater(smap):
    tank = make_tank(room_climate="tropical_summer", temperature_c=25)
    items, _ = build(smap, tank, [StockingItem(species_id="guppy", count=4)])
    assert any("cooling fan" in i.item.lower() for i in items)
    assert not any(i.item.startswith("Heater") for i in items)


def test_budget_has_all_core_hardware(smap):
    tank = make_tank()
    items, _ = build(smap, tank, [StockingItem(species_id="java_moss", count=3)])
    names = " | ".join(i.item for i in items)
    for expected in ("aquarium", "Filter", "LED", "Substrate", "Heater"):
        assert expected in names


def test_totals_account_for_quantities(smap):
    tank = make_tank()
    items, _ = build(smap, tank, [StockingItem(species_id="guppy", count=5)])
    usd, bdt = budget_totals(items)
    manual_usd = sum(i.cost_usd * i.qty for i in items)
    assert usd == pytest.approx(manual_usd, abs=0.01)
    assert bdt == pytest.approx(usd * USD_TO_BDT, rel=0.001)


def test_livestock_and_plants_are_separate_categories(smap):
    tank = make_tank()
    items, _ = build(smap, tank, [StockingItem(species_id="guppy", count=2),
                                  StockingItem(species_id="java_moss", count=1)])
    guppy = next(i for i in items if i.item == "Guppy")
    moss = next(i for i in items if i.item == "Java Moss")
    assert guppy.category == "livestock" and guppy.qty == 2
    assert moss.category == "plants"
    assert guppy.cost_bdt > 0 and moss.cost_bdt > 0
