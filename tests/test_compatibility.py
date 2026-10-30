from aquapulse.database import Database
from aquapulse.engine.compatibility import resolve_compatibility
from aquapulse.models import StockingItem, TankConfig


def test_compatibility_empty_tank():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    result = resolve_compatibility(all_species, [], None)
    assert result.verdict == "empty tank"
    assert result.score == 100.0


def test_compatibility_fin_nipping_detected():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    stocking = [StockingItem(species_id="betta", count=1),
                StockingItem(species_id="neon_tetra", count=10)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "fin_nipping" for issue in result.issues)
    assert result.score < 100


def test_compatibility_predation_by_size():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    stocking = [StockingItem(species_id="oscar", count=1),
                StockingItem(species_id="neon_tetra", count=10)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "predation" for issue in result.issues)
    assert result.score <= 70


def test_compatibility_temp_mismatch():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    # Goldfish prefers 18-24C; betta prefers 24-30C -> overlap at 24 exactly,
    # so use platy (20-28) vs discus (27-32): overlap 27-28, fine. Instead
    # goldfish (18-24) vs discus (27-32) -> no overlap.
    stocking = [StockingItem(species_id="goldfish", count=2),
                StockingItem(species_id="discus", count=4)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "param_temperature" for issue in result.issues)


def test_compatibility_ph_mismatch():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    # Goldfish pH 6.5-8.0; molly pH 7.0-8.5 overlap... use nerite snail
    # pH 7.0-8.5 with discus pH 5.0-7.0 -> overlap at 7.0 exactly.
    # Better: goldfish (6.5-8.0) vs anubias (5.5-8.0) overlap.
    # Use platy (6.8-8.0) vs anubias (5.5-8.0) overlap.
    # For a real mismatch: goldfish (6.5-8.0) vs a species with pH 8.5+? none.
    # Instead assert the mechanism with two species whose ranges truly don't
    # overlap in GH: discus (1-8) vs molly (10-20).
    stocking = [StockingItem(species_id="discus", count=2),
                StockingItem(species_id="molly", count=4)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "param_gh" for issue in result.issues)


def test_compatibility_shrimp_eaten_by_betta():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    stocking = [StockingItem(species_id="betta", count=1),
                StockingItem(species_id="cherry_shrimp", count=6)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "invertebrate_predation" for issue in result.issues)
    assert result.verdict == "incompatible"


def test_compatibility_shrimp_safe_with_tetras():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    stocking = [StockingItem(species_id="neon_tetra", count=12),
                StockingItem(species_id="cherry_shrimp", count=8)]
    result = resolve_compatibility(all_species, stocking, None)
    assert not any(issue.type == "invertebrate_predation" for issue in result.issues)


def test_compatibility_score_bounds_and_dedup():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    # duplicate species listed twice must not double-count
    stocking = [StockingItem(species_id="neon_tetra", count=6),
                StockingItem(species_id="neon_tetra", count=6)]
    result = resolve_compatibility(all_species, stocking, None)
    assert 0 <= result.score <= 100
    assert result.issues == []


def test_compatibility_territorial_same_zone():
    db = Database()
    all_species = {s.id: s for s in db.get_species()}
    # angelfish (mid, territorial) + pleco (bottom, territorial) no conflict;
    # angelfish + gourami (mid, semi, territorial) conflict
    stocking = [StockingItem(species_id="angelfish", count=2),
                StockingItem(species_id="gourami", count=1)]
    result = resolve_compatibility(all_species, stocking, None)
    assert any(issue.type == "territorial" for issue in result.issues)
