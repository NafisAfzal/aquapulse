"""SQLite-backed species catalog and preset/build persistence.

We seed a rich catalog of 24 organisms (freshwater fish, shrimp, snails,
and aquarium plants) with realistic water-parameter preferences, behavior
traits, and budget pricing. The catalog lives in an on-disk SQLite file
(``aquapulse.db``) created next to this package; tests use a throwaway
in-memory database.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from typing import List, Optional

from .models import Preset, Species, SpeciesCategory, SwimZone, Temperament, TankConfig, StockingItem

# Hard real-world-ish species data. Values (temp C, pH, GH) are typical
# ranges for the popular freshwater aquarium trade.
SEED_SPECIES = [
    # --- Community / centerpiece fish ---
    dict(id="neon_tetra", name="Neon Tetra", scientific_name="Paracheirodon innesi",
         category="fish", size_cm=3.5, min_tank_gal=10, temperament="peaceful",
         swim_zone="mid", min_temp_c=20, max_temp_c=27, min_ph=5.5, max_ph=7.5,
         min_gh=1, max_gh=10, aggression_rating=0.05, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.6, emoji="🦐",
         price_usd=0.50, description="Small, calm schooling fish; ideal for community planted tanks."),
    dict(id="guppy", name="Guppy", scientific_name="Poecilia reticulata",
         category="fish", size_cm=4.5, min_tank_gal=10, temperament="peaceful",
         swim_zone="top", min_temp_c=22, max_temp_c=28, min_ph=6.8, max_ph=8.0,
         min_gh=8, max_gh=18, aggression_rating=0.08, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.8, emoji="🐠",
         price_usd=0.50, description="Colorful livebearer; keep in groups, hardy beginner fish."),
    dict(id="molly", name="Molly", scientific_name="Poecilia sphenops",
         category="fish", size_cm=7.0, min_tank_gal=20, temperament="peaceful",
         swim_zone="top", min_temp_c=22, max_temp_c=29, min_ph=7.0, max_ph=8.5,
         min_gh=10, max_gh=20, aggression_rating=0.1, fin_nipper=True,
         territorial=False, plant_safe=True, bioload_factor=1.1, emoji="🐟",
         price_usd=0.50, description="Active top-dweller; sometimes nips long-finned tankmates."),
    dict(id="platy", name="Platy", scientific_name="Xiphophorus maculatus",
         category="fish", size_cm=5.0, min_tank_gal=10, temperament="peaceful",
         swim_zone="mid", min_temp_c=20, max_temp_c=28, min_ph=6.8, max_ph=8.0,
         min_gh=8, max_gh=18, aggression_rating=0.08, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.9, emoji="🐟",
         price_usd=0.40, description="Tough, friendly livebearer well-suited to beginners."),
    dict(id="angelfish", name="Angelfish", scientific_name="Pterophyllum scalare",
         category="fish", size_cm=15.0, min_tank_gal=30, temperament="semi-aggressive",
         swim_zone="mid", min_temp_c=24, max_temp_c=30, min_ph=6.0, max_ph=7.5,
         min_gh=2, max_gh=10, aggression_rating=0.45, fin_nipper=True,
         territorial=True, plant_safe=True, bioload_factor=1.5, emoji="🐠",
         price_usd=1.25, description="Tall, graceful cichlid; territorial when mature, nips long fins."),
    dict(id="discus", name="Discus", scientific_name="Symphysodon aequifasciatus",
         category="fish", size_cm=20.0, min_tank_gal=55, temperament="peaceful",
         swim_zone="mid", min_temp_c=27, max_temp_c=32, min_ph=5.0, max_ph=7.0,
         min_gh=1, max_gh=8, aggression_rating=0.2, fin_nipper=False,
         territorial=True, plant_safe=True, bioload_factor=1.8, emoji="🐟",
         price_usd=2.08, description="Beautiful but demanding; needs warm, soft, pristine water."),
    dict(id="oscar", name="Oscar", scientific_name="Astronotus ocellatus",
         category="fish", size_cm=35.0, min_tank_gal=75, temperament="aggressive",
         swim_zone="mid", min_temp_c=23, max_temp_c=28, min_ph=6.0, max_ph=8.0,
         min_gh=5, max_gh=15, aggression_rating=0.9, fin_nipper=True,
         territorial=True, plant_safe=False, bioload_factor=3.0, emoji="🐟",
         price_usd=1.25, description="Large predator; re-scapes tanks, eats small fish and plants."),
    dict(id="betta", name="Betta (Siamese Fighter)", scientific_name="Betta splendens",
         category="fish", size_cm=6.5, min_tank_gal=5, temperament="aggressive",
         swim_zone="top", min_temp_c=24, max_temp_c=30, min_ph=6.0, max_ph=7.5,
         min_gh=2, max_gh=10, aggression_rating=0.85, fin_nipper=True,
         territorial=True, plant_safe=True, bioload_factor=0.8, emoji="🐠",
         price_usd=2.08, description="Gorgeous but aggressive toward similar fins; keep alone or with peaceful bottom-dwellers."),
    dict(id="corydoras", name="Panda Corydoras", scientific_name="Corydoras panda",
         category="fish", size_cm=4.0, min_tank_gal=10, temperament="peaceful",
         swim_zone="bottom", min_temp_c=22, max_temp_c=26, min_ph=6.0, max_ph=7.5,
         min_gh=2, max_gh=12, aggression_rating=0.05, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.7, emoji="🐟",
         price_usd=1.00, description="Gentle armored catfish; needs a group and soft sandy substrate."),
    dict(id="zebra_danio", name="Zebra Danio", scientific_name="Danio rerio",
         category="fish", size_cm=5.0, min_tank_gal=10, temperament="peaceful",
         swim_zone="top", min_temp_c=18, max_temp_c=26, min_ph=6.5, max_ph=7.5,
         min_gh=5, max_gh=15, aggression_rating=0.1, fin_nipper=True,
         territorial=False, plant_safe=True, bioload_factor=0.8, emoji="🐟",
         price_usd=0.50, description="Fast, hardy schooling fish; may chase but rarely harms tankmates."),
    dict(id="gourami", name="Dwarf Gourami", scientific_name="Trichogaster lalius",
         category="fish", size_cm=7.0, min_tank_gal=10, temperament="semi-aggressive",
         swim_zone="mid", min_temp_c=24, max_temp_c=28, min_ph=6.0, max_ph=7.5,
         min_gh=4, max_gh=12, aggression_rating=0.4, fin_nipper=False,
         territorial=True, plant_safe=True, bioload_factor=1.0, emoji="🐟",
         price_usd=2.08, description="Colorful labyrinth fish; males can be territorial."),
    dict(id="tetra_blackskirt", name="Black Skirt Tetra", scientific_name="Gymnocorymbus ternetzi",
         category="fish", size_cm=6.0, min_tank_gal=15, temperament="semi-aggressive",
         swim_zone="mid", min_temp_c=20, max_temp_c=28, min_ph=6.0, max_ph=7.5,
         min_gh=3, max_gh=12, aggression_rating=0.5, fin_nipper=True,
         territorial=False, plant_safe=True, bioload_factor=1.0, emoji="🐟",
         price_usd=0.50, description="Active tetra known to nip fins of slower tankmates."),
    dict(id="goldfish", name="Fancy Goldfish", scientific_name="Carassius auratus",
         category="fish", size_cm=18.0, min_tank_gal=20, temperament="peaceful",
         swim_zone="mid", min_temp_c=18, max_temp_c=24, min_ph=6.5, max_ph=8.0,
         min_gh=5, max_gh=15, aggression_rating=0.15, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=3.5, emoji="🐠",
         price_usd=1.25, description="Heavy bioload waste producer; needs big filter and frequent water changes."),
    dict(id="pleco", name="Bristlenose Pleco", scientific_name="Ancistrus dolichopterus",
         category="fish", size_cm=12.0, min_tank_gal=25, temperament="peaceful",
         swim_zone="bottom", min_temp_c=22, max_temp_c=28, min_ph=6.5, max_ph=7.5,
         min_gh=3, max_gh=15, aggression_rating=0.2, fin_nipper=False,
         territorial=True, plant_safe=True, bioload_factor=1.6, emoji="🐟",
         price_usd=1.00, description="Algae-eating armored catfish; territorial over hiding spots."),
    dict(id="cherry_shrimp", name="Cherry Shrimp", scientific_name="Neocaridina davidi",
         category="invertebrate", size_cm=2.5, min_tank_gal=5, temperament="peaceful",
         swim_zone="bottom", min_temp_c=20, max_temp_c=28, min_ph=6.5, max_ph=7.8,
         min_gh=3, max_gh=10, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.15, emoji="🦐",
         price_usd=0.50, description="Tiny scavenger; excellent cleanup crew, prey to larger fish."),
    dict(id="amano_shrimp", name="Amano Shrimp", scientific_name="Caridina multidentata",
         category="invertebrate", size_cm=3.5, min_tank_gal=10, temperament="peaceful",
         swim_zone="bottom", min_temp_c=20, max_temp_c=28, min_ph=6.5, max_ph=7.8,
         min_gh=3, max_gh=12, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.2, emoji="🦐",
         price_usd=0.65, description="Hardworking algae grazer; needs stable, mature water."),
    dict(id="mystery_snail", name="Mystery Snail", scientific_name="Pomacea bridgesii",
         category="invertebrate", size_cm=5.0, min_tank_gal=10, temperament="peaceful",
         swim_zone="bottom", min_temp_c=18, max_temp_c=28, min_ph=7.0, max_ph=8.5,
         min_gh=8, max_gh=20, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=False, bioload_factor=0.5, emoji="🐌",
         price_usd=0.50, description="Active scavenger; can munch soft-leaved plants."),
    dict(id="nerite_snail", name="Nerite Snail", scientific_name="Neritina natalensis",
         category="invertebrate", size_cm=2.5, min_tank_gal=5, temperament="peaceful",
         swim_zone="bottom", min_temp_c=20, max_temp_c=28, min_ph=7.0, max_ph=8.5,
         min_gh=8, max_gh=18, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.3, emoji="🐌",
         price_usd=0.65, description="Prolific algae eater; won't eat healthy plants."),
    # --- Plants ---
    dict(id="anubias", name="Anubias Nana", scientific_name="Anubias barteri var. nana",
         category="plant", size_cm=10.0, min_tank_gal=0, temperament="peaceful",
         swim_zone="bottom", min_temp_c=20, max_temp_c=30, min_ph=5.5, max_ph=8.0,
         min_gh=2, max_gh=15, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.1, emoji="🌿",
         price_usd=1.50, description="Low-light rhizome plant; great for beginners and shrimp."),
    dict(id="java_fern", name="Java Fern", scientific_name="Microsorum pteropus",
         category="plant", size_cm=15.0, min_tank_gal=0, temperament="peaceful",
         swim_zone="bottom", min_temp_c=20, max_temp_c=28, min_ph=6.0, max_ph=7.5,
         min_gh=2, max_gh=12, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.1, emoji="🌿",
         price_usd=1.50, description="Tough low-light plant; attach to wood or rock."),
    dict(id="hornwort", name="Hornwort", scientific_name="Ceratophyllum demersum",
         category="plant", size_cm=30.0, min_tank_gal=0, temperament="peaceful",
         swim_zone="mid", min_temp_c=15, max_temp_c=30, min_ph=6.0, max_ph=8.5,
         min_gh=2, max_gh=15, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.15, emoji="🌿",
         price_usd=0.66, description="Fast-growing floating/background stem plant; excellent nitrate sponge."),
    dict(id="java_moss", name="Java Moss", scientific_name="Taxiphyllum barbieri",
         category="plant", size_cm=8.0, min_tank_gal=0, temperament="peaceful",
         swim_zone="bottom", min_temp_c=15, max_temp_c=28, min_ph=5.5, max_ph=8.0,
         min_gh=1, max_gh=12, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.1, emoji="🌿",
         price_usd=0.66, description="Hardy carpeting/refuge plant; great for shrimp fry."),
    dict(id="anacharis", name="Anacharis", scientific_name="Egeria densa",
         category="plant", size_cm=40.0, min_tank_gal=0, temperament="peaceful",
         swim_zone="mid", min_temp_c=15, max_temp_c=28, min_ph=6.5, max_ph=8.5,
         min_gh=3, max_gh=15, aggression_rating=0.0, fin_nipper=False,
         territorial=False, plant_safe=True, bioload_factor=0.15, emoji="🌿",
         price_usd=0.66, description="Rapid grower; aggressive nitrate and nutrient consumer."),
]

SEED_PRESETS = [
    dict(id="nano_shrimp_bowl", name="Nano Shrimp Bowl", description="A tiny planted 5-gal shrimp and snail paradise.",
         tank=dict(length_in=12, width_in=10, height_in=12, water_level_pct=90,
                   filter_gph=40, filter_type="sponge", substrate="sand", planted=True,
                   temperature_c=25, ph=7.0, gh=8, water_change_pct=25,
                   water_change_freq_days=7, feeding_per_day=1, food_amount_g=0.5),
         stocking=[dict(species_id="cherry_shrimp", count=10),
                   dict(species_id="nerite_snail", count=1),
                   dict(species_id="anubias", count=2),
                   dict(species_id="java_moss", count=1)]),
    dict(id="community_20g", name="Community 20-Gallon", description="A classic peaceful community tank with plants and a cleanup crew.",
         tank=dict(length_in=24, width_in=12, height_in=16, water_level_pct=90,
                   filter_gph=150, filter_type="HOB", substrate="gravel", planted=True,
                   temperature_c=25, ph=7.0, gh=8, water_change_pct=25,
                   water_change_freq_days=7, feeding_per_day=2, food_amount_g=1.5),
         stocking=[dict(species_id="neon_tetra", count=12),
                   dict(species_id="platy", count=4),
                   dict(species_id="corydoras", count=6),
                   dict(species_id="cherry_shrimp", count=8),
                   dict(species_id="anubias", count=2),
                   dict(species_id="java_fern", count=3)]),
    dict(id="angelfish_40g", name="Angelfish Show Tank", description="A centerpiece angelfish setup with soft water and gentle tankmates.",
         tank=dict(length_in=36, width_in=12, height_in=24, water_level_pct=90,
                   filter_gph=250, filter_type="canister", substrate="sand", planted=True,
                   temperature_c=27, ph=6.8, gh=4, water_change_pct=30,
                   water_change_freq_days=7, feeding_per_day=2, food_amount_g=2.0),
         stocking=[dict(species_id="angelfish", count=2),
                   dict(species_id="corydoras", count=8),
                   dict(species_id="amano_shrimp", count=6),
                   dict(species_id="java_fern", count=4),
                   dict(species_id="anubias", count=3)]),
]


class Database:
    """Thin SQLite wrapper for the species catalog and saved builds."""

    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "aquapulse.db")
        self._lock = threading.Lock()
        # FastAPI/TestClient run sync endpoints in a threadpool, so the
        # connection must be usable across threads.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()
        self._seed()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS species (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS presets (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS saved_builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        self._conn.commit()

    def _seed(self) -> None:
        # Always upsert seed data so price/schema changes take effect.
        for sp in SEED_SPECIES:
            self._conn.execute(
                "INSERT OR REPLACE INTO species (id, data) VALUES (?, ?)",
                (sp["id"], json.dumps(sp)),
            )
        for pr in SEED_PRESETS:
            self._conn.execute(
                "INSERT OR REPLACE INTO presets (id, data) VALUES (?, ?)",
                (pr["id"], json.dumps(pr)),
            )
        self._conn.commit()

    def get_species(self) -> List[Species]:
        with self._lock:
            rows = self._conn.execute("SELECT data FROM species ORDER BY id").fetchall()
        return [Species(**json.loads(r["data"])) for r in rows]

    def get_species_by_id(self, species_id: str) -> Optional[Species]:
        with self._lock:
            row = self._conn.execute("SELECT data FROM species WHERE id = ?", (species_id,)).fetchone()
        if row is None:
            return None
        return Species(**json.loads(row["data"]))

    def get_presets(self) -> List[Preset]:
        with self._lock:
            rows = self._conn.execute("SELECT data FROM presets ORDER BY id").fetchall()
        out = []
        for r in rows:
            d = json.loads(r["data"])
            out.append(Preset(
                id=d["id"],
                name=d["name"],
                description=d.get("description", ""),
                tank=TankConfig(**d["tank"]),
                stocking=[StockingItem(**s) for s in d["stocking"]],
            ))
        return out

    def save_build(self, name: str, payload: dict) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO saved_builds (name, data) VALUES (?, ?)",
                (name, json.dumps(payload)),
            )
            self._conn.commit()
            return cur.lastrowid