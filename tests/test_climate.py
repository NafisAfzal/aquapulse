"""Tests for climate presets, heater sizing and fan cooling."""
import pytest

from aquapulse.database import Database
from aquapulse.engine.climate import (
    CLIMATE_PRESETS,
    evaluate_climate,
    list_climate_presets,
)
from aquapulse.models import StockingItem, TankConfig


@pytest.fixture(scope="module")
def smap():
    return {s.id: s for s in Database().get_species()}


def make_tank(**kw) -> TankConfig:
    base = dict(length_in=24, width_in=12, height_in=16, filter_gph=200,
                temperature_c=25, ph=7.0, gh=8)
    base.update(kw)
    return TankConfig(**base)


def test_preset_listing_has_three_climates():
    presets = list_climate_presets()
    assert len(presets) == 3
    ids = {p["id"] for p in presets}
    assert ids == set(CLIMATE_PRESETS)
    assert all(p["name"] and p["room_temp_c"] > 0 for p in presets)


def test_winter_indoor_sizes_heater(smap):
    tank = make_tank(room_climate="winter_indoor",
                     stocking=[StockingItem(species_id="guppy", count=4)])
    rep = evaluate_climate(smap, tank.stocking, tank)
    assert rep.room_temp_c == 19.0
    assert rep.heater_watts_required == 100  # 68 L, +6°C, rounded to 25 W
    assert rep.cooling_fan_recommended is False
    assert any("W heater" in w for w in rep.warnings)


def test_climate_controlled_needs_only_trickle_heat(smap):
    tank = make_tank(room_climate="climate_controlled")
    rep = evaluate_climate(smap, [], tank)
    assert rep.heater_watts_required == 25
    assert rep.cooling_fan_recommended is False


def test_tropical_summer_recommends_evaporative_fan(smap):
    tank = make_tank(room_climate="tropical_summer", temperature_c=25)
    rep = evaluate_climate(smap, [StockingItem(species_id="guppy", count=4)], tank)
    assert rep.heater_watts_required == 0
    assert rep.cooling_fan_recommended is True
    assert rep.room_temp_c == 31.5
    assert rep.expected_temp_after_mitigation_c == 29.0
    assert any("fan" in w.lower() for w in rep.warnings)


def test_heat_sensitive_shrimp_flagged_in_tropical_summer(smap):
    tank = make_tank(room_climate="tropical_summer", temperature_c=25,
                     stocking=[StockingItem(species_id="cherry_shrimp", count=6)])
    rep = evaluate_climate(smap, tank.stocking, tank)
    assert rep.species_thermal_conflicts
    assert any("Cherry Shrimp" in c for c in rep.species_thermal_conflicts)


def test_unknown_preset_falls_back_to_controlled(smap):
    tank = make_tank(room_climate="mars_base")
    rep = evaluate_climate(smap, [], tank)
    assert rep.preset_id == "climate_controlled"
    assert rep.room_temp_c == 24.5


def test_heater_grows_with_water_volume(smap):
    small = make_tank(length_in=20, width_in=10, height_in=12,
                      room_climate="winter_indoor")
    large = make_tank(length_in=36, width_in=18, height_in=18,
                      room_climate="winter_indoor")
    small_rep = evaluate_climate(smap, [], small)
    large_rep = evaluate_climate(smap, [], large)
    assert large_rep.heater_watts_required > small_rep.heater_watts_required
    assert small_rep.heater_watts_required % 25 == 0
