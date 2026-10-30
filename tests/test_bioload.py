from aquapulse.database import Database
from aquapulse.engine.bioload import compute_bioload
from aquapulse.models import StockingItem, TankConfig


def test_bioload_empty_tank():
    """Empty stocking produces no fish inches."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    result = compute_bioload(all_species, [], tank)
    assert result.total_fish_inches == 0.0
    assert result.total_bioload_points == 0.0
    assert result.stocking_rating == "adequate"


def test_bioload_volume_and_limits():
    """Basic volume and "1 inch per gallon" limit."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="neon_tetra", count=12),
                StockingItem(species_id="platy", count=4),
                StockingItem(species_id="corydoras", count=6)]
    result = compute_bioload(all_species, stocking, tank)
    # 24x12x16 @ 90% water = ~17.95 gal
    assert abs(result.volume_gal - 17.95) < 0.1
    assert result.total_fish_inches > 0
    # 33.9" in 17.95 gal -> overstocked warning
    assert result.total_fish_inches > tank.volume_gal


def test_bioload_underfiltered_rating():
    """Filter too small triggers marginal/underfiltered rating."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    # 200 GPH / 50 gal = 4x; use tiny filter
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=40)
    stocking = [StockingItem(species_id="neon_tetra", count=10)]
    result = compute_bioload(all_species, stocking, tank)
    assert result.stocking_rating in {"marginal", "underfiltered"}


def test_bioload_crowding_zone_warning():
    """When many fish share a zone, warn about crowding."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=10, width_in=10, height_in=12, filter_gph=50)
    # Many mid-zone neutrals would crowd
    stocking = [StockingItem(species_id="platy", count=50)]
    result = compute_bioload(all_species, stocking, tank)
    assert any("mid" in w for w in result.warnings)


def test_bioload_combined_species():
    """Top/mid/bottom fish all contribute to same total."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="guppy", count=10),   # top
                StockingItem(species_id="neon_tetra", count=8),   # mid
                StockingItem(species_id="corydoras", count=6)]    # bottom
    result = compute_bioload(all_species, stocking, tank)
    assert result.total_fish_inches > 0
    assert result.stocking_rating == "adequate"


def test_bioload_plants_and_invertebrates_skipped():
    """Only fish count toward inches; invertebrates skipped."""
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    tank = TankConfig(length_in=24, width_in=12, height_in=16, filter_gph=200)
    stocking = [StockingItem(species_id="cherry_shrimp", count=20),
                StockingItem(species_id="anubias", count=5)]
    result = compute_bioload(all_species, stocking, tank)
    assert result.total_fish_inches == 0.0
    assert result.total_bioload_points == 0.0
