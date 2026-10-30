"""Tests for the Auto-Architect constraint optimizer (v1.0.0)."""
from __future__ import annotations

from aquapulse.database import Database
from aquapulse.engine.optimizer import (
    build_optimized_setups,
    auto_fix_tank,
    dims_for_liters,
    tank_from_request,
)
from aquapulse.models import (
    OptimizationRequest,
    StockingItem,
    TankConfig,
)


def _smap():
    return {s.id: s for s in Database().get_species()}


def _req(**kw):
    defaults = dict(max_budget_bdt=20000, tank_liters=75,
                    climate_preset="climate_controlled",
                    style_goal="peaceful_community", currency="USD")
    defaults.update(kw)
    return OptimizationRequest(**defaults)


def test_returns_three_ranked_blueprints():
    bps = build_optimized_setups(_smap(), _req())
    assert [b.id for b in bps] == ["best_value", "biodiversity", "low_maintenance"]
    assert all(b.label for b in bps)
    assert all(b.tagline for b in bps)


def test_blueprints_meet_constraints():
    smap = _smap()
    for style in ("peaceful_community", "low_maintenance_planted",
                  "vibrant_centerpiece", "shrimp_breeding_colony"):
        for b in build_optimized_setups(smap, _req(style_goal=style)):
            assert b.harmony_score >= 90, (style, b.label, b.harmony_score)
            assert b.capacity_ratio <= 0.85, (style, b.label, b.capacity_ratio)
            assert b.cost.under_budget, (style, b.label, b.cost.total_usd)


def test_blueprints_have_budget_lines_and_rationale():
    for b in build_optimized_setups(_smap(), _req()):
        assert b.lines, "expected line-item cost breakdown"
        assert b.rationale, "expected human rationale"
        assert b.tank.volume_l > 0


def test_budget_currency_conversion():
    # ৳20,000 budget == $166.67 (at 120 BDT/USD)
    req = _req(max_budget_bdt=20000)
    assert abs(req.budget_usd - 20000 / 120.0) < 0.01
    # Explicit USD overrides BDT.
    req2 = _req(max_budget_bdt=1, max_budget_usd=250)
    assert req2.budget_usd == 250.0


def test_usd_budget_path():
    bps = build_optimized_setups(_smap(), _req(max_budget_usd=400, max_budget_bdt=0))
    assert bps[0].cost.under_budget


def test_larger_budget_stocks_more():
    smap = _smap()
    small = build_optimized_setups(smap, _req(max_budget_bdt=8000))[0]
    large = build_optimized_setups(smap, _req(max_budget_bdt=50000))[0]
    small_fish = sum(s.count for s in small.stocking)
    large_fish = sum(s.count for s in large.stocking)
    assert large_fish >= small_fish


def test_goal_styles_produce_distinct_blueprints():
    smap = _smap()
    peaceful = build_optimized_setups(smap, _req(style_goal="peaceful_community"))[0]
    planted = build_optimized_setups(smap, _req(style_goal="low_maintenance_planted"))[0]
    assert {s.species_id for s in peaceful.stocking} != {s.species_id for s in planted.stocking}


def test_biodiversity_variant_has_more_distinct_species():
    smap = _smap()
    best = build_optimized_setups(smap, _req(max_budget_bdt=50000))[0]
    biodiv = build_optimized_setups(smap, _req(max_budget_bdt=50000))[1]
    assert len({s.species_id for s in biodiv.stocking}) >= \
        len({s.species_id for s in best.stocking})


def test_dims_for_liters_approximately_matches_volume():
    for liters in (20, 75, 120, 250):
        l, w, h = dims_for_liters(liters)
        gal = (l * w * h * 0.9) / 231.0
        assert abs(gal - liters / 3.785411784) / (liters / 3.785411784) < 0.25


def test_tank_from_request_uses_climate():
    t = tank_from_request(_req(climate_preset="winter_indoor", tank_liters=75))
    assert t.room_climate == "winter_indoor"
    assert t.filter_gph > 0
    assert t.volume_l > 0


def test_auto_fix_resolves_overstocked_conflicting_tank():
    smap = _smap()
    tank = TankConfig(
        length_in=24, width_in=12, height_in=16, filter_gph=60,
        stocking=[StockingItem(species_id="oscar", count=2),
                  StockingItem(species_id="neon_tetra", count=10),
                  StockingItem(species_id="betta", count=1)],
    )
    fx = auto_fix_tank(smap, tank)
    assert fx.harmony_score >= 90
    assert fx.fixes, "expected actionable fixes"
    # Oscar (predator) must be gone.
    assert all(s.species_id != "oscar" for s in fx.tank.stocking)


def test_auto_fix_returns_clean_stocking():
    smap = _smap()
    tank = TankConfig(
        length_in=24, width_in=12, height_in=16, filter_gph=100,
        stocking=[StockingItem(species_id="neon_tetra", count=8),
                  StockingItem(species_id="corydoras", count=4),
                  StockingItem(species_id="anubias", count=2)],
    )
    fx = auto_fix_tank(smap, tank)
    assert fx.ok or fx.harmony_score >= 90
    assert fx.tank.stocking


def test_auto_fix_temperature_reconciliation():
    smap = _smap()
    # Guppy max 28°C and cory max 26°C together — solver should reconcile temp.
    tank = TankConfig(
        length_in=24, width_in=12, height_in=16, filter_gph=100, temperature_c=32,
        stocking=[StockingItem(species_id="guppy", count=6),
                  StockingItem(species_id="corydoras", count=4)],
    )
    fx = auto_fix_tank(smap, tank)
    # cory max 26, guppy max 28 -> overlap up to 26.
    assert fx.tank.temperature_c <= 26.0