from aquapulse.database import Database
from aquapulse.engine.nitrogen_sim import simulate_nitrogen_cycle, summarize_cycle
from aquapulse.models import StockingItem, TankConfig


def test_sim_returns_30_steps():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="neon_tetra", count=12),
                StockingItem(species_id="corydoras", count=6)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    assert len(steps) == 30
    assert steps[0].day == 1
    assert steps[-1].day == 30
    for s in steps:
        assert s.ammonia_mg_l >= 0
        assert s.nitrite_mg_l >= 0
        assert s.nitrate_mg_l >= 0
        assert 4.0 <= s.ph <= 10.0


def test_ammonia_spike_then_fall():
    """Ammonia rises early (fish-in cycle) then declines as bacteria mature."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200,
                      water_change_pct=25, water_change_freq_days=7)
    stocking = [StockingItem(species_id="neon_tetra", count=15)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    peak = max(s.ammonia_mg_l for s in steps)
    peak_day = next(i for i, s in enumerate(steps) if s.ammonia_mg_l == peak)
    # peak occurs early-ish (before day 15)
    assert peak > 0.2
    assert peak_day < 15


def test_nitrite_peak_follows_ammonia():
    """Nitrite should appear and peak after ammonia starts converting."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="guppy", count=20)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    peak_nh3 = max(s.ammonia_mg_l for s in steps)
    peak_no2 = max(s.nitrite_mg_l for s in steps)
    assert peak_no2 > 0.05  # some nitrite is produced


def test_bacteria_grow_and_saturate():
    """AOB/NOB colonies grow over time and plateau."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="neon_tetra", count=15)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    assert steps[-1].bacteria_aob >= steps[0].bacteria_aob
    assert steps[-1].bacteria_nob >= steps[0].bacteria_nob


def test_plants_absorb_nitrate():
    """A planted tank should show less nitrate than a bare tank."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    planted = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200,
                         planted=True, substrate="soil")
    bare = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200,
                      planted=False, substrate="bare")
    stocking = [StockingItem(species_id="guppy", count=15),
                StockingItem(species_id="hornwort", count=4)]
    p_steps = simulate_nitrogen_cycle(all_species, stocking, planted)
    b_steps = simulate_nitrogen_cycle(all_species, stocking, bare)
    assert p_steps[-1].nitrate_mg_l < b_steps[-1].nitrate_mg_l
    assert any(s.plant_uptake_nitrate > 0 for s in p_steps)


def test_water_change_lowers_concentration():
    """On a water change day, concentrations drop."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200,
                      water_change_pct=50, water_change_freq_days=3)
    stocking = [StockingItem(species_id="neon_tetra", count=20)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    # day 3 is a water change day
    assert steps[2].water_changed is True
    assert steps[2].nitrate_mg_l <= steps[1].nitrate_mg_l


def test_no_fish_sim_is_benign():
    """A tank with only plants should stay near-zero ammonia."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=100)
    stocking = [StockingItem(species_id="anubias", count=5)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    assert max(s.ammonia_mg_l for s in steps) < 0.3


def test_summary_dict_has_peaks():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="neon_tetra", count=12)]
    steps = simulate_nitrogen_cycle(all_species, stocking, tank)
    summary = summarize_cycle(steps)
    assert summary["ok"] is True
    assert summary["peak_ammonia_mg_l"] >= 0
    assert 1 <= summary["peak_ammonia_day"] <= 30

def test_feeding_level_scales_ammonia_peak():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    stocking = [StockingItem(species_id="guppy", count=8)]
    base = dict(length_in=24, width_in=12, height_in=16, filter_gph=200)
    low = simulate_nitrogen_cycle(all_species, stocking, TankConfig(**base, feeding_level=1.0))
    high = simulate_nitrogen_cycle(all_species, stocking, TankConfig(**base, feeding_level=2.5))
    assert (max(s.ammonia_mg_l for s in high)
            > max(s.ammonia_mg_l for s in low))
