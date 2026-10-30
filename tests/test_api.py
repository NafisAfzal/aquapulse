import pytest
from fastapi.testclient import TestClient

from aquapulse.api import app

client = TestClient(app)


def test_index_served():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_species_endpoint():
    resp = client.get("/species")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) >= 20
    assert all("id" in s and "name" in s for s in data)


def test_presets_endpoint():
    resp = client.get("/presets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    assert all(p["tank"]["volume_gal"] > 0 for p in data)


def test_analyze_tank_basic():
    payload = {
        "length_in": 24, "width_in": 12, "height_in": 16, "water_level_pct": 90,
        "filter_gph": 200, "temperature_c": 25, "ph": 7.0, "gh": 8,
        "stocking": [{"species_id": "neon_tetra", "count": 12}],
    }
    resp = client.post("/analyze-tank", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["bioload"]["volume_gal"] > 0
    assert data["compatibility"]["score"] >= 0
    assert data["care_plan"]
    assert data["budget"]


def test_analyze_tank_empty_stocking():
    payload = {"length_in": 24, "width_in": 12, "height_in": 16,
               "stocking": []}
    resp = client.post("/analyze-tank", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["compatibility"]["verdict"] == "empty tank"


def test_analyze_tank_unknown_species_422():
    payload = {"stocking": [{"species_id": "does_not_exist", "count": 3}]}
    resp = client.post("/analyze-tank", json=payload)
    assert resp.status_code == 422
    assert "Unknown species_id" in resp.json()["detail"]


def test_simulate_30_days():
    payload = {
        "length_in": 24, "width_in": 12, "height_in": 16, "filter_gph": 200,
        "stocking": [{"species_id": "neon_tetra", "count": 12}],
    }
    resp = client.post("/simulate-30-days", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["steps"]) == 30
    assert data["summary"]["ok"] is True
    assert data["summary"]["peak_ammonia_mg_l"] >= 0


def test_save_build():
    resp = client.post("/save-build", json={"name": "test build", "payload": {"x": 1}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["id"] >= 1


def test_meta_endpoint():
    resp = client.get("/meta")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "1.0.0"
    assert data["exchange_rate"] == 120.0
    assert data["currencies"] == ["USD", "BDT"]


def test_climate_presets_endpoint():
    resp = client.get("/climate-presets")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert {p["id"] for p in data} == {"tropical_summer", "winter_indoor", "climate_controlled"}


def test_analyze_tank_v2_sections():
    payload = {
        "length_in": 24, "width_in": 12, "height_in": 16, "filter_gph": 200,
        "temperature_c": 20, "ph": 7.0, "gh": 8,
        "stocking": [{"species_id": "neon_tetra", "count": 8}],
    }
    resp = client.post("/analyze-tank", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert [r["id"] for r in data["disease"]["risks"]] == [
        "ich", "fin_rot", "gill_burn", "osmotic_shock"]
    assert data["disease"]["overall_risk"] > 0
    assert data["breeding"]["fry_survival_pct"] >= 0
    assert data["climate"]["preset_id"] == "climate_controlled"
    assert data["totals"]["usd"] > 0
    assert data["totals"]["bdt"] == pytest.approx(
        data["totals"]["usd"] * data["exchange_rate"], rel=0.002)
    assert data["exchange_rate"] == 120.0


def test_analyze_budget_items_have_bdt():
    payload = {"filter_gph": 150,
               "room_climate": "winter_indoor",
               "stocking": [{"species_id": "guppy", "count": 3}]}
    data = client.post("/analyze-tank", json=payload).json()
    assert data["budget"]
    for item in data["budget"]:
        assert item["cost_bdt"] == pytest.approx(item["cost_usd"] * 120.0, abs=0.01)
    assert any(i["item"].startswith("Heater") for i in data["budget"])
    manual_usd = sum(i["cost_usd"] * i["qty"] for i in data["budget"])
    assert data["totals"]["usd"] == pytest.approx(manual_usd, abs=0.01)


def test_feeding_level_increases_ammonia_forecast():
    base = {"length_in": 24, "width_in": 12, "height_in": 16, "filter_gph": 200,
            "stocking": [{"species_id": "guppy", "count": 8}]}
    low = client.post("/simulate-30-days", json={**base, "feeding_level": 0.3}).json()
    high = client.post("/simulate-30-days", json={**base, "feeding_level": 3.0}).json()
    assert high["summary"]["peak_ammonia_mg_l"] > low["summary"]["peak_ammonia_mg_l"]


# --------------------------------------------------------------------------
# v1.0.0
# --------------------------------------------------------------------------

def test_optimize_setup_returns_three_blueprints():
    resp = client.post("/optimize-setup", json={
        "max_budget_bdt": 20000, "tank_liters": 75,
        "climate_preset": "climate_controlled",
        "style_goal": "peaceful_community", "currency": "BDT",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["blueprints"]) == 3
    ids = [b["id"] for b in data["blueprints"]]
    assert ids == ["best_value", "biodiversity", "low_maintenance"]
    for bp in data["blueprints"]:
        assert bp["harmony_score"] >= 90
        assert bp["capacity_ratio"] <= 0.85
        assert bp["cost"]["under_budget"] is True


def test_optimize_setup_output_shape():
    bp = client.post("/optimize-setup", json={
        "max_budget_bdt": 50000, "tank_liters": 120,
        "climate_preset": "tropical_summer", "style_goal": "vibrant_centerpiece",
    }).json()["blueprints"][0]
    assert bp["label"]
    assert bp["tank"]["volume_gal"] > 0
    assert isinstance(bp["stocking"], list)
    assert bp["lines"]
    assert bp["rationale"]


def test_optimize_setup_usd_budget():
    data = client.post("/optimize-setup", json={
        "max_budget_usd": 300, "tank_liters": 60,
        "style_goal": "shrimp_breeding_colony",
    }).json()
    assert len(data["blueprints"]) == 3


def test_auto_fix_tank_resolves_conflicts():
    tank = {
        "length_in": 24, "width_in": 12, "height_in": 16,
        "filter_gph": 60, "temperature_c": 25, "ph": 7.0, "gh": 8,
        "stocking": [
            {"species_id": "oscar", "count": 2},
            {"species_id": "neon_tetra", "count": 10},
            {"species_id": "betta", "count": 1},
        ],
    }
    resp = client.post("/auto-fix-tank", json=tank)
    assert resp.status_code == 200
    data = resp.json()
    assert data["harmony_score"] >= 90
    assert data["fixes"]
    assert all(s["species_id"] != "oscar" for s in data["tank"]["stocking"])
    assert data["ok"] is True


def test_commercial_species_endpoint():
    data = client.get("/commercial-species").json()
    assert len(data) == 5
    assert {c["id"] for c in data} == {
        "monosex_tilapia", "pabda_catfish", "gulsha_tengra",
        "climbing_perch_koi", "golda_prawn"}


def test_commercial_simulate():
    resp = client.post("/commercial-simulate", json={
        "species_id": "monosex_tilapia", "volume_l": 10000,
        "stocking_count": 5000, "initial_weight_g": 20,
        "target_weight_g": 500, "duration_days": 120, "ph": 7.5,
        "temperature_c": 28.0, "feed_price_bdt": 60,
        "fingerling_price_bdt": 12, "market_price_bdt": 180,
        "system_type": "Biofloc Tank",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["species"]["id"] == "monosex_tilapia"
    assert len(data["rows"]) == 18
    s = data["summary"]
    assert s["harvest_biomass_kg"] > 0
    assert s["total_cost_bdt"] > 0
    assert s["net_profit_bdt"] == pytest.approx(
        s["gross_revenue_bdt"] - s["total_cost_bdt"], abs=0.01)
    assert 0.0 < s["nh3_fraction"] <= 1.0


def test_commercial_simulate_validation_422():
    resp = client.post("/commercial-simulate", json={"species_id": "x", "volume_l": 1})
    assert resp.status_code == 422


