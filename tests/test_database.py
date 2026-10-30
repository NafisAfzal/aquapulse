import pytest

from aquapulse.database import Database, SEED_SPECIES
from aquapulse.models import Species, SpeciesCategory


@pytest.fixture()
def db():
    return Database()  # in-memory


def test_seed_has_at_least_20_species(db):
    species = db.get_species()
    assert len(species) >= 20
    assert len(species) == len(SEED_SPECIES)


def test_all_species_have_required_traits(db):
    for s in db.get_species():
        assert s.id and s.name
        assert s.max_temp_c >= s.min_temp_c
        assert s.max_ph >= s.min_ph
        assert s.max_gh >= s.min_gh
        assert 0.0 <= s.aggression_rating <= 1.0
        assert s.price_usd >= 0


def test_categories_cover_fish_shrimp_snail_plant(db):
    cats = {s.category for s in db.get_species()}
    assert cats == {SpeciesCategory.FISH, SpeciesCategory.INVERTEBRATE, SpeciesCategory.PLANT}
    # explicitly verify shrimp and snail exist
    ids = {s.id for s in db.get_species()}
    assert "cherry_shrimp" in ids
    assert "nerite_snail" in ids
    assert "anubias" in ids


def test_get_species_by_id_roundtrip(db):
    s = db.get_species_by_id("neon_tetra")
    assert isinstance(s, Species)
    assert s.name == "Neon Tetra"
    assert db.get_species_by_id("does_not_exist") is None


def test_presets_seeded_and_wellformed(db):
    presets = db.get_presets()
    assert len(presets) >= 3
    for p in presets:
        assert p.tank.volume_gal > 0
        assert p.stocking
        by_id = {s.id for s in db.get_species()}
        for item in p.stocking:
            assert item.species_id in by_id, f"preset {p.id} references unknown {item.species_id}"


def test_save_build_roundtrip(db):
    build_id = db.save_build("my build", {"species": ["neon_tetra"]})
    assert build_id >= 1
    rows = db._conn.execute("SELECT id, name FROM saved_builds").fetchall()
    assert any(r["id"] == build_id and r["name"] == "my build" for r in rows)


def test_species_ids_unique(db):
    ids = [s.id for s in db.get_species()]
    assert len(ids) == len(set(ids))
