"""Tests for the commercial biofloc & aquaculture ROI engine (v1.0.0)."""
from __future__ import annotations

import math

from aquapulse.engine.commercial_aquaculture import (
    DEFAULT_FEED_PRICE_BDT,
    DEFAULT_FINGERLING_PRICE_BDT,
    DEFAULT_MARKET_PRICE_BDT,
    list_commercial_species,
    nh3_fraction,
    simulate_commercial,
)
from aquapulse.models import CommercialRequest


def _req(**kw):
    defaults = dict(species_id="monosex_tilapia", volume_l=10000,
                    stocking_count=5000, initial_weight_g=20,
                    target_weight_g=500, duration_days=120, ph=7.5,
                    temperature_c=28.0, feed_price_bdt=DEFAULT_FEED_PRICE_BDT,
                    fingerling_price_bdt=DEFAULT_FINGERLING_PRICE_BDT,
                    market_price_bdt=DEFAULT_MARKET_PRICE_BDT,
                    system_type="Biofloc Tank", molasses_price_bdt=25.0,
                    electricity_rate_bdt=9.0)
    defaults.update(kw)
    return CommercialRequest(**defaults)


def test_catalog_has_five_species():
    cats = list_commercial_species()
    assert len(cats) == 5
    ids = {c.id for c in cats}
    assert ids == {"monosex_tilapia", "pabda_catfish", "gulsha_tengra",
                   "climbing_perch_koi", "golda_prawn"}
    for c in cats:
        assert c.scientific_name
        assert 0 < c.survival_rate <= 1
        assert c.protein_pct > 0


def test_emerson_nh3_fraction():
    # pH 7.0 at 28°C -> small but nonzero; pH 9.0 -> much higher.
    f7 = nh3_fraction(7.0, 28.0)
    f9 = nh3_fraction(9.0, 28.0)
    assert 0.005 < f7 < 0.02
    assert f9 > 0.3
    assert f9 > f7 * 10
    # Higher temperature increases the toxic fraction at fixed pH.
    assert nh3_fraction(7.5, 32.0) > nh3_fraction(7.5, 22.0)


def test_emerson_fraction_bounded():
    for ph in (6.0, 7.0, 7.5, 8.5):
        for t in (20, 28, 33):
            f = nh3_fraction(ph, t)
            assert 0.0 <= f <= 1.0


def test_simulate_returns_weekly_rows():
    rep = simulate_commercial(_req(duration_days=120))
    assert len(rep.rows) == math.ceil(120 / 7)  # 18 weeks
    assert rep.rows[0].week == 1
    assert rep.rows[-1].day == 120
    # Monotonic growth.
    weights = [r.weight_g for r in rep.rows]
    assert weights == sorted(weights)
    assert rep.rows[-1].weight_g == 500.0


def test_growth_matches_target():
    rep = simulate_commercial(_req(initial_weight_g=20, target_weight_g=500))
    assert abs(rep.rows[-1].weight_g - 500.0) < 0.5


def test_survival_bounded_and_expected():
    rep = simulate_commercial(_req())
    assert rep.rows[0].survival_pct <= 100
    final_survival = rep.rows[-1].survival_pct
    assert abs(final_survival - 92.0) < 2.0  # tilapia survival_rate=0.92


def test_financials():
    rep = simulate_commercial(_req())
    s = rep.summary
    assert s.harvest_biomass_kg > 0
    assert s.total_cost_bdt > 0
    assert s.gross_revenue_bdt > 0
    assert s.net_profit_bdt == s.gross_revenue_bdt - s.total_cost_bdt
    assert abs(s.roi_pct - (s.net_profit_bdt / s.total_cost_bdt * 100.0)) < 0.1
    assert s.break_even_bdt_per_kg > 0
    assert s.fcr > 0


def test_fingerling_cost_matches_count_and_price():
    rep = simulate_commercial(_req(stocking_count=1000, fingerling_price_bdt=10))
    assert rep.summary.fingerling_cost_bdt == 1000 * 10


def test_market_price_drives_roi():
    low = simulate_commercial(_req(market_price_bdt=100)).summary
    high = simulate_commercial(_req(market_price_bdt=300)).summary
    assert high.roi_pct > low.roi_pct
    assert high.net_profit_bdt > low.net_profit_bdt


def test_break_even_price():
    rep = simulate_commercial(_req())
    s = rep.summary
    assert abs(s.break_even_bdt_per_kg - s.total_cost_bdt / s.harvest_biomass_kg) < 1.0


def test_aeration_scales_with_volume():
    small = simulate_commercial(_req(volume_l=5000)).summary.aeration_lpm
    large = simulate_commercial(_req(volume_l=20000)).summary.aeration_lpm
    assert large > small


def test_biofloc_carbon_dosing_positive():
    rep = simulate_commercial(_req(species_id="monosex_tilapia"))
    assert all(r.molasses_g_day >= 0 for r in rep.rows)
    assert rep.summary.max_daily_molasses_g > 0


def test_high_protein_species_needs_more_molasses():
    til = simulate_commercial(_req(species_id="monosex_tilapia")).summary.max_daily_molasses_g
    pab = simulate_commercial(_req(species_id="pabda_catfish")).summary.max_daily_molasses_g
    # Higher protein feed -> lower feed C:N -> more carbon dose needed.
    assert pab > til


def test_toxicity_warning_when_nh3_high():
    rep = simulate_commercial(_req(ph=9.0))
    assert any("NH₃" in w or "ammonia" in w.lower() for w in rep.summary.warnings)


def test_do_warning_when_low():
    rep = simulate_commercial(_req(species_id="golda_prawn"))
    assert any("DO" in w or "oxygen" in w.lower() for w in rep.summary.warnings)


def test_unknown_species_falls_back_to_tilapia():
    rep = simulate_commercial(_req(species_id="nope"))
    assert rep.species.id == "monosex_tilapia"


def test_all_five_species_simulate():
    for cat in list_commercial_species():
        rep = simulate_commercial(_req(species_id=cat.id))
        assert rep.rows
        assert rep.summary.harvest_biomass_kg > 0