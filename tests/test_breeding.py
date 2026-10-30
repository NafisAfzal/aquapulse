"""Tests for the breeding / fry-survival forecast engine."""
import pytest

from aquapulse.database import Database
from aquapulse.engine.breeding import predict_breeding
from aquapulse.models import StockingItem, TankConfig


@pytest.fixture(scope="module")
def smap():
    return {s.id: s for s in Database().get_species()}


def make_tank(**kw) -> TankConfig:
    base = dict(length_in=24, width_in=12, height_in=16, filter_gph=200,
                temperature_c=25, ph=7.0, gh=8)
    base.update(kw)
    return TankConfig(**base)


def test_guppies_are_identified_as_prolific(smap):
    tank = make_tank(stocking=[StockingItem(species_id="guppy", count=6)])
    rep = predict_breeding(smap, tank.stocking, tank)
    assert [b.species_id for b in rep.prolific_species] == ["guppy"]
    assert rep.prolific_species[0].offspring_60d > 0
    assert rep.projected_population_60d > rep.current_population
    assert rep.notes


def test_plant_cover_improves_fry_survival(smap):
    bare = make_tank(stocking=[StockingItem(species_id="guppy", count=6)])
    planted = make_tank(stocking=[StockingItem(species_id="guppy", count=6),
                                  StockingItem(species_id="java_moss", count=3)])
    bare_rep = predict_breeding(smap, bare.stocking, bare)
    planted_rep = predict_breeding(smap, planted.stocking, planted)
    assert planted_rep.fry_survival_pct > bare_rep.fry_survival_pct
    assert planted_rep.cover_bonus_pct > 0
    assert planted_rep.projected_population_60d > bare_rep.projected_population_60d


def test_predators_reduce_fry_survival(smap):
    calm = make_tank(stocking=[StockingItem(species_id="guppy", count=6)])
    risky = make_tank(stocking=[StockingItem(species_id="guppy", count=6),
                                StockingItem(species_id="angelfish", count=2)])
    calm_rep = predict_breeding(smap, calm.stocking, calm)
    risky_rep = predict_breeding(smap, risky.stocking, risky)
    assert risky_rep.predation_penalty_pct > 0
    assert risky_rep.fry_survival_pct < calm_rep.fry_survival_pct
    assert any("predator" in n.lower() for n in risky_rep.notes)


def test_population_boom_flagged_in_small_tank(smap):
    tank = make_tank(length_in=20, width_in=10, height_in=12,
                     stocking=[StockingItem(species_id="guppy", count=6)])
    rep = predict_breeding(smap, tank.stocking, tank)
    assert rep.boom_risk == "boom"
    assert any("boom" in n.lower() for n in rep.notes)


def test_no_breeders_means_no_boom(smap):
    tank = make_tank(stocking=[StockingItem(species_id="neon_tetra", count=6)])
    rep = predict_breeding(smap, tank.stocking, tank)
    assert rep.prolific_species == []
    assert rep.boom_risk == "none"
    assert rep.projected_population_60d == rep.current_population


def test_cherry_shrimp_are_prolific(smap):
    tank = make_tank(stocking=[StockingItem(species_id="cherry_shrimp", count=10),
                               StockingItem(species_id="java_moss", count=2)])
    rep = predict_breeding(smap, tank.stocking, tank)
    assert any(b.species_id == "cherry_shrimp" for b in rep.prolific_species)
    assert rep.projected_population_60d > 10


def test_survival_is_bounded(smap):
    tank = make_tank(stocking=[StockingItem(species_id="guppy", count=3),
                               StockingItem(species_id="oscar", count=2),
                               StockingItem(species_id="angelfish", count=2)])
    rep = predict_breeding(smap, tank.stocking, tank)
    assert 5 <= rep.fry_survival_pct <= 95
