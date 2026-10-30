from aquapulse.models import (
    Species, TankConfig, StockingItem, SpeciesCategory, SwimZone, Temperament,
)


def test_species_constructs():
    s = Species(
        id="neon_tetra", name="Neon Tetra", size_cm=3.5, min_tank_gal=10,
        min_temp_c=20, max_temp_c=27, min_ph=5.5, max_ph=7.5,
        min_gh=1, max_gh=10,
    )
    assert s.id == "neon_tetra"
    assert s.is_fish
    assert s.temp_range() == (20.0, 27.0)


def test_species_rejects_negative_size():
    try:
        Species(id="bad", name="Bad", size_cm=-1, min_tank_gal=5,
                min_temp_c=20, max_temp_c=26, min_ph=6, max_ph=7, min_gh=1, max_gh=8)
        assert False, "expected validation error"
    except Exception:
        pass


def test_tank_volume_math():
    t = TankConfig(length_in=24, width_in=12, height_in=16, water_level_pct=75)
    # water height = 16 * 0.75 = 12 in; volume = 24*12*12/231
    assert abs(t.volume_gal - (24 * 12 * 12) / 231.0) < 1e-3
    assert abs(t.volume_l - t.volume_gal * 3.785411784) < 1e-2
    assert abs(t.water_height_in - 12.0) < 1e-9


def test_tank_defaults_are_sane():
    t = TankConfig()
    assert t.volume_gal > 0
    assert t.planted is True


def test_stocking_item_rejects_zero_count():
    try:
        StockingItem(species_id="x", count=0)
        assert False, "expected validation error"
    except Exception:
        pass