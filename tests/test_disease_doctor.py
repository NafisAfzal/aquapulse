"""Tests for the Fish Doctor disease-risk engine."""
import pytest

from aquapulse.database import Database
from aquapulse.engine.disease_doctor import assess_disease_risk
from aquapulse.engine.nitrogen_sim import simulate_nitrogen_cycle
from aquapulse.models import StockingItem, TankConfig


@pytest.fixture(scope="module")
def smap():
    return {s.id: s for s in Database().get_species()}


def make_tank(**kw) -> TankConfig:
    base = dict(length_in=24, width_in=12, height_in=16, filter_gph=200,
                temperature_c=25, ph=7.0, gh=8)
    base.update(kw)
    return TankConfig(**base)


def report(smap, tank: TankConfig):
    steps = simulate_nitrogen_cycle(smap, tank.stocking, tank)
    return assess_disease_risk(smap, tank.stocking, tank, steps), steps


def risk_of(report_obj, key):
    return next(r for r in report_obj.risks if r.id == key)


def test_report_contains_all_four_diseases(smap):
    tank = make_tank(stocking=[StockingItem(species_id="neon_tetra", count=6)])
    rep, _ = report(smap, tank)
    assert [r.id for r in rep.risks] == ["ich", "fin_rot", "gill_burn", "osmotic_shock"]
    assert all(0 <= r.risk_pct <= 100 for r in rep.risks)
    assert rep.overall_risk == max(r.risk_pct for r in rep.risks)


def test_cold_water_increases_ich_risk(smap):
    cold = make_tank(temperature_c=20.0,
                     stocking=[StockingItem(species_id="neon_tetra", count=8)])
    warm = make_tank(temperature_c=26.0,
                     stocking=[StockingItem(species_id="neon_tetra", count=8)])
    cold_rep, _ = report(smap, cold)
    warm_rep, _ = report(smap, warm)
    assert risk_of(cold_rep, "ich").risk_pct > risk_of(warm_rep, "ich").risk_pct
    assert risk_of(cold_rep, "ich").severity in ("high", "critical")
    assert any("°C" in c for c in risk_of(cold_rep, "ich").causes)


def test_overfeeding_drives_gill_burn(smap):
    low = make_tank(stocking=[StockingItem(species_id="guppy", count=6)],
                    feeding_per_day=2, feeding_level=0.2)
    high = make_tank(stocking=[StockingItem(species_id="guppy", count=6)],
                     feeding_per_day=4, feeding_level=3.0)
    low_rep, low_steps = report(smap, low)
    high_rep, high_steps = report(smap, high)
    assert max(s.ammonia_mg_l for s in high_steps) > max(s.ammonia_mg_l for s in low_steps)
    assert risk_of(high_rep, "gill_burn").risk_pct > risk_of(low_rep, "gill_burn").risk_pct
    assert risk_of(high_rep, "gill_burn").risk_pct >= 45
    assert any("ammonia" in c.lower() or "nitrite" in c.lower()
               for c in risk_of(high_rep, "gill_burn").causes)


def test_fin_rot_flags_nippers_and_overcrowding(smap):
    tank = make_tank(length_in=20, width_in=10, height_in=12,
                     stocking=[StockingItem(species_id="angelfish", count=6)],
                     feeding_per_day=4, feeding_level=3.0)
    rep, _ = report(smap, tank)
    fin = risk_of(rep, "fin_rot")
    assert fin.risk_pct >= 45
    causes = " ".join(fin.causes)
    assert "Fin-nipping" in causes
    assert "Overcrowded" in causes
    assert fin.dosages


def test_osmotic_shock_from_incompatible_ranges(smap):
    tank = make_tank(ph=7.35, gh=9.0,
                     stocking=[StockingItem(species_id="discus", count=2),
                               StockingItem(species_id="molly", count=2)])
    rep, _ = report(smap, tank)
    osmotic = risk_of(rep, "osmotic_shock")
    assert osmotic.risk_pct >= 45
    assert any("pH" in c for c in osmotic.causes)
    assert osmotic.dosages


def test_salt_dosage_scales_with_volume(smap):
    small = make_tank(length_in=24, width_in=12, height_in=16, temperature_c=20.0,
                      stocking=[StockingItem(species_id="neon_tetra", count=6)])
    large = make_tank(length_in=36, width_in=18, height_in=18, temperature_c=20.0,
                      stocking=[StockingItem(species_id="neon_tetra", count=6)])
    small_rep, _ = report(smap, small)
    large_rep, _ = report(smap, large)
    small_salt = next(d for d in risk_of(small_rep, "ich").dosages if d.product == "Aquarium salt")
    large_salt = next(d for d in risk_of(large_rep, "ich").dosages if d.product == "Aquarium salt")
    assert small_salt.unit == "g"
    ratio = large_salt.quantity / small_salt.quantity
    assert ratio == pytest.approx(large.volume_l / small.volume_l, rel=0.01)


def test_salt_sensitive_stock_gets_half_dose_warning(smap):
    tank = make_tank(temperature_c=20.0,
                     stocking=[StockingItem(species_id="corydoras", count=4),
                               StockingItem(species_id="java_moss", count=1)])
    rep, _ = report(smap, tank)
    assert any("corydoras" in n.lower() for n in rep.salt_sensitive_species)
    assert "Java Moss" in rep.salt_sensitive_species
    ich = risk_of(rep, "ich")
    salt = next(d for d in ich.dosages if d.product == "Aquarium salt")
    assert salt.quantity == pytest.approx(tank.volume_l, rel=0.01)  # 1 g/L half dose
    assert "half dose" in salt.note.lower()
    assert any("salt-sensitive" in n.lower() for n in rep.notes)


def test_ich_dosages_include_spoons_and_water_change(smap):
    tank = make_tank(temperature_c=20.0,
                     stocking=[StockingItem(species_id="guppy", count=6)])
    rep, _ = report(smap, tank)
    products = [d.product for d in risk_of(rep, "ich").dosages]
    assert "Aquarium salt (tablespoons)" in products
    assert "Water change" in products
    assert "Temperature target" in products
    assert any(d.unit.endswith("C") for d in risk_of(rep, "ich").dosages)


def test_invertebrate_only_tank_is_not_disease_scored(smap):
    tank = make_tank(stocking=[StockingItem(species_id="cherry_shrimp", count=8),
                               StockingItem(species_id="java_moss", count=2)])
    rep, _ = report(smap, tank)
    assert rep.overall_risk == 0
    assert any("No fish" in n for n in rep.notes)


def test_healthy_tank_has_no_medication(smap):
    tank = make_tank(temperature_c=25.0, ph=7.0, gh=6.0,
                     filter_gph=400, feeding_per_day=1, feeding_level=0.6,
                     stocking=[StockingItem(species_id="neon_tetra", count=4),
                               StockingItem(species_id="java_moss", count=3)])
    rep, _ = report(smap, tank)
    if rep.overall_risk < 25:
        assert all(not r.dosages for r in rep.risks)
