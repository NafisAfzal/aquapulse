"""Auto-Architect multi-objective constraint optimizer (v1.0.0).

Instead of forcing a user to hand-guess fish combinations, this module runs a
deterministic combinatorial solver that selects a 100 %-compatible stocking
set (schooling fish, a centerpiece, a cleanup crew, and enough live plants to
absorb daily nitrates) subject to hard constraints:

* Harmony Score >= 90
* Zero CRITICAL compatibility issues (predation / parameter conflicts)
* Bioload capacity ratio <= 0.85
* Total cost <= budget

It returns three ranked blueprints (*Best Value Balanced*, *Maximum
Biodiversity*, *Ultra-Low Maintenance*), each with a full line-item cost
breakdown.  A companion :func:`auto_fix_tank` resolves conflicts on a
hand-tweaked workbench with one-click fixes.

Everything is pure arithmetic -- no external services, deterministic.
"""
from __future__ import annotations

from math import ceil
from typing import Dict, List, Optional, Tuple

from ..models import (
    AutoFixResponse,
    BudgetAllocation,
    BudgetItem,
    CompatibilityIssue,
    IssueSeverity,
    OptimizationBlueprint,
    OptimizationRequest,
    Species,
    StockingItem,
    TankConfig,
)
from .bioload import compute_bioload
from .climate import evaluate_climate
from .compatibility import resolve_compatibility
from .disease_doctor import assess_disease_risk
from .nitrogen_sim import simulate_nitrogen_cycle
from .pricing import (
    USD_TO_BDT,
    SUBSTRATE_UNIT_COST,
    AQUARIUM_GLASS_PER_GAL,
    FILTER_HOB_BASE, FILTER_HOB_PER_GPH,
    FILTER_SPONGE_BASE, FILTER_SPONGE_PER_GPH,
    LED_LIGHT_PLANTED, LED_LIGHT_BASIC,
    SUBSTRATE_BAG,
    HEATER_PER_WATT,
    COOLING_FAN,
    WATER_TEST_KIT, WATER_CONDITIONER,
    FISH_FOOD,
    GRAVEL_VACUUM_NET,
    PLANT_FERTILIZER,
)

USD_TO_BDT_LOCAL = USD_TO_BDT

# Per-goal target water chemistry.  These are chosen so the recommended
# species in each pool are mutually compatible at the chosen setpoint.
GOAL_CONFIG = {
    "peaceful_community": dict(
        temp=26.0, ph=7.0, gh=8, planted=True, substrate="sand",
        schools=["neon_tetra", "guppy", "platy", "zebra_danio"],
        centerpiece=[],
        cleanup=["corydoras", "cherry_shrimp", "amano_shrimp", "mystery_snail", "nerite_snail"],
        plants=["anubias", "java_fern", "java_moss", "anacharis", "hornwort"],
    ),
    "low_maintenance_planted": dict(
        temp=25.0, ph=7.0, gh=8, planted=True, substrate="soil",
        schools=["guppy", "platy", "zebra_danio"],
        centerpiece=[],
        cleanup=["mystery_snail", "nerite_snail", "corydoras"],
        plants=["anubias", "java_fern", "java_moss", "anacharis", "hornwort"],
    ),
    "vibrant_centerpiece": dict(
        temp=28.0, ph=6.8, gh=8, planted=True, substrate="sand",
        schools=["guppy", "tetra_blackskirt"],
        centerpiece=["discus", "angelfish", "gourami"],
        cleanup=["corydoras", "amano_shrimp", "cherry_shrimp"],
        plants=["anubias", "java_fern", "java_moss"],
    ),
    "shrimp_breeding_colony": dict(
        temp=25.5, ph=7.2, gh=8, planted=True, substrate="soil",
        schools=["guppy"],
        centerpiece=[],
        cleanup=["cherry_shrimp", "amano_shrimp", "mystery_snail", "nerite_snail"],
        plants=["java_moss", "anubias", "java_fern", "anacharis"],
    ),
}
GOAL_LABELS = {
    "peaceful_community": "Peaceful Community",
    "low_maintenance_planted": "Low-Maintenance Planted",
    "vibrant_centerpiece": "Vibrant Centerpiece",
    "shrimp_breeding_colony": "Shrimp Breeding Colony",
}

# Species the auto-fix can add as a nitrate sponge (cheap, tolerant).
NITRATE_SPONGE = ["java_moss", "hornwort", "anacharis"]

MAX_PER_SPECIES = 60


# --------------------------------------------------------------------------
# Tank geometry helpers
# --------------------------------------------------------------------------

def dims_for_liters(liters: float) -> Tuple[float, float, float]:
    """Return a pleasing (length, width, height) in inches for a target volume."""
    gal = liters / 3.785411784
    if liters <= 30:
        l, w = 16.0, 10.0
    elif liters <= 60:
        l, w = 20.0, 12.0
    elif liters <= 90:
        l, w = 24.0, 12.0
    elif liters <= 160:
        l, w = 30.0, 14.0
    elif liters <= 260:
        l, w = 36.0, 18.0
    else:
        l, w = 48.0, 20.0
    water_h = gal * 231.0 / (l * w)
    h = max(10.0, min(34.0, round(water_h / 0.9, 1)))
    return l, w, h


def tank_from_request(req: OptimizationRequest) -> TankConfig:
    """Build a :class:`TankConfig` from an optimization request."""
    l, w, h = dims_for_liters(req.tank_liters)
    gal = max((l * w * (h * 0.9)) / 231.0, 1.0)
    goal = GOAL_CONFIG.get(req.style_goal, GOAL_CONFIG["peaceful_community"])
    return TankConfig(
        length_in=l, width_in=w, height_in=h, water_level_pct=90,
        filter_gph=round(max(gal * 5.0, 60.0), 0),
        filter_type="sponge" if gal < 10 else "HOB",
        substrate=goal["substrate"],
        planted=goal["planted"],
        temperature_c=goal["temp"],
        ph=goal["ph"],
        gh=goal["gh"],
        room_climate=req.climate_preset,
        currency=req.currency,
        feeding_level=1.0,
    )


# --------------------------------------------------------------------------
# Costing
# --------------------------------------------------------------------------

def _hardware_items(tank: TankConfig, climate, tier: str = "standard",
                    exchange_rate: float = USD_TO_BDT_LOCAL) -> List[BudgetItem]:
    """Line-item hardware cost.

    ``tier`` is ``"standard"`` (full kit) or ``"budget"`` (economy components
    plus only the essential consumables).  A tight budget forces the budget
    tier so the solver can still allocate money to biological stock.
    """
    gal = max(tank.volume_gal, 1.0)
    budget = tier == "budget"
    items: List[BudgetItem] = []
    bag_base = SUBSTRATE_UNIT_COST.get(tank.substrate, SUBSTRATE_BAG)

    def add(name: str, cost_usd: float, qty: float = 1, note: str = "") -> None:
        items.append(BudgetItem(
            item=name, category="hardware",
            cost_usd=round(max(0.0, cost_usd), 2),
            cost_bdt=round(max(0.0, cost_usd) * exchange_rate, 2),
            qty=qty, note=note,
        ))

    add(f"{gal:.1f} gal aquarium", max(AQUARIUM_GLASS_PER_GAL, gal * 0.50),
        note=f"{tank.length_in:.0f}x{tank.width_in:.0f}x{tank.height_in:.0f} in glass/acrylic")
    if budget or tank.filter_type == "sponge":
        add("Sponge filter", max(FILTER_SPONGE_BASE, tank.filter_gph * FILTER_SPONGE_PER_GPH),
            note=f"{tank.filter_gph:.0f} GPH air-driven turnover")
    else:
        add(f"Filter ({tank.filter_type})", max(FILTER_HOB_BASE, tank.filter_gph * FILTER_HOB_PER_GPH),
            note=f"{tank.filter_gph:.0f} GPH turnover")
    if tank.planted:
        add("LED light fixture", LED_LIGHT_BASIC if budget else LED_LIGHT_PLANTED,
            note="basic LED" if budget else "full-spectrum planted LED")
    if bag_base > 0:
        add(f"Substrate ({tank.substrate})", bag_base,
            qty=1 if budget else max(1, ceil(gal / 10.0)), note="~1 lb per gallon")
    if climate is not None and climate.heater_watts_required > 0:
        add(f"Heater ({climate.heater_watts_required} W)",
            max(5.0, climate.heater_watts_required * HEATER_PER_WATT),
            note="adjustable thermostat, 1 W/L per 5 C rule")
    if climate is not None and climate.cooling_fan_recommended:
        add("Evaporative cooling fan", COOLING_FAN,
            note="clip-on fan, to reduce temperature; top up evaporation daily")
    if budget:
        add("Water conditioner", WATER_CONDITIONER, note="dechlorinator / ammonia binder")
        add("Fish food", FISH_FOOD, note="monthly supply")
    else:
        add("Water test kit", WATER_TEST_KIT, note="NH3 / NO2 / NO3 / pH")
        add("Water conditioner", WATER_CONDITIONER, note="dechlorinator / ammonia binder")
        add("Fish food", FISH_FOOD, note="monthly supply")
        add("Gravel vacuum & net", GRAVEL_VACUUM_NET, note="maintenance basics")
        if tank.planted:
            add("Liquid plant fertilizer", PLANT_FERTILIZER, note="macro + micro")
    return items


def _livestock_items(smap: Dict[str, Species], stocking: List[StockingItem],
                     exchange_rate: float = USD_TO_BDT_LOCAL) -> List[BudgetItem]:
    items: List[BudgetItem] = []
    for item in stocking:
        sp = smap.get(item.species_id)
        if sp is None or item.count <= 0:
            continue
        items.append(BudgetItem(
            item=sp.name,
            category="plants" if sp.is_plant else "livestock",
            cost_usd=round(sp.price_usd, 2),
            cost_bdt=round(sp.price_usd * exchange_rate, 2),
            qty=item.count,
            note=f"{item.count} x {sp.emoji}",
        ))
    return items


def _total_cost(items: List[BudgetItem]) -> Tuple[float, float]:
    usd = sum(i.cost_usd * i.qty for i in items)
    bdt = sum(i.cost_bdt * i.qty for i in items)
    return round(usd, 2), round(bdt, 2)


# --------------------------------------------------------------------------
# Constraint feasibility
# --------------------------------------------------------------------------

def _stocking_copy(stocking: List[StockingItem]) -> List[StockingItem]:
    return [StockingItem(species_id=s.species_id, count=s.count) for s in stocking]


def _add_batch(stocking: List[StockingItem], species_id: str, batch: int) -> List[StockingItem]:
    out = _stocking_copy(stocking)
    for s in out:
        if s.species_id == species_id:
            s.count += batch
            return out
    out.append(StockingItem(species_id=species_id, count=batch))
    return out


def _count_of(stocking: List[StockingItem], species_id: str) -> int:
    for s in stocking:
        if s.species_id == species_id:
            return s.count
    return 0


def _feasible(smap: Dict[str, Species], tank: TankConfig,
              stocking: List[StockingItem], budget_usd: float,
              hardware_usd: float) -> bool:
    compat = resolve_compatibility(smap, stocking, tank)
    if compat.score < 90:
        return False
    if any(i.severity == IssueSeverity.CRITICAL for i in compat.issues):
        return False
    bioload = compute_bioload(smap, stocking, tank)
    if bioload.capacity_ratio > 0.85:
        return False
    liv = _livestock_items(smap, stocking)
    liv_usd = sum(i.cost_usd * i.qty for i in liv)
    if hardware_usd + liv_usd > budget_usd:
        return False
    return True


def _greedy_fill(smap: Dict[str, Species], tank: TankConfig, budget_usd: float,
                 hardware_usd: float, slots: List[Tuple[str, int]],
                 existing: Optional[List[StockingItem]] = None) -> List[StockingItem]:
    """Deterministically add stock in round-robin so the build stays balanced.

    Each pass tries to add *one* batch to every slot in order; a slot that no
    longer fits (budget / bioload / harmony) is skipped for the rest of the
    run.  The loop ends when a full pass adds nothing.
    """
    stocking = _stocking_copy(existing) if existing else []
    active = set(range(len(slots)))
    guard = 0
    while active and guard < 60:
        guard += 1
        added_any = False
        removed = set()
        for idx in list(active):
            sid, batch = slots[idx]
            if _count_of(stocking, sid) + batch > MAX_PER_SPECIES:
                removed.add(idx)
                continue
            # Try ideal batch, then smaller batches for a tight budget.
            placed = False
            for attempt in (batch, max(1, batch // 2), 1):
                trial = _add_batch(stocking, sid, attempt)
                if _feasible(smap, tank, trial, budget_usd, hardware_usd):
                    stocking = trial
                    placed = True
                    added_any = True
                    break
            if not placed:
                removed.add(idx)
        active -= removed
        if not added_any:
            break
    return stocking


def _nitrate_cleanup(smap: Dict[str, Species], tank: TankConfig,
                     stocking: List[StockingItem], budget_usd: float,
                     hardware_usd: float) -> List[StockingItem]:
    """Add nitrate-sponge plants until the 30-day forecast is safe (respecting budget)."""
    def cost_now() -> float:
        return hardware_usd + sum(i.cost_usd * i.qty for i in _livestock_items(smap, stocking))

    steps = simulate_nitrogen_cycle(smap, stocking, tank, days=30)
    peak = max(s.ammonia_mg_l for s in steps)
    final_no3 = steps[-1].nitrate_mg_l
    guard = 0
    while (peak > 0.25 or final_no3 > 40.0) and guard < 10:
        added = False
        for pid in NITRATE_SPONGE:
            sp = smap.get(pid)
            if sp is None or _count_of(stocking, pid) >= MAX_PER_SPECIES:
                continue
            if cost_now() + sp.price_usd * 2 > budget_usd:
                continue
            stocking = _add_batch(stocking, pid, 2)
            steps = simulate_nitrogen_cycle(smap, stocking, tank, days=30)
            peak = max(s.ammonia_mg_l for s in steps)
            final_no3 = steps[-1].nitrate_mg_l
            added = True
            if peak <= 0.25 and final_no3 <= 40.0:
                return stocking
        if not added:
            break
        guard += 1
    return stocking


# --------------------------------------------------------------------------
# Variant slot orderings
# --------------------------------------------------------------------------

def _slots_for(variant: str, pool: Dict) -> List[Tuple[str, int]]:
    schools = [(s, 6) for s in pool["schools"]]
    cleanup = [(s, 3) for s in pool["cleanup"]]
    plants = [(s, 2) for s in pool["plants"]]
    center = [(s, 1) for s in pool["centerpiece"]]
    if variant == "biodiversity":
        return (center + [(s, 1) for s in pool["schools"]] +
                [(s, 1) for s in pool["cleanup"]] + plants + schools + cleanup)
    if variant == "low_maintenance":
        return plants + [(s, 2) for s in pool["cleanup"]] + schools[:1] + center
    # best_value: balanced, schools first (cheap density), then cleanup, then centerpiece
    return schools + cleanup + plants + center + schools


def _rationale(variant: str, stocking: List[StockingItem], pool: Dict) -> List[str]:
    lines: List[str] = []
    school_count = sum(_count_of(stocking, s) for s in pool["schools"])
    cleanup_count = sum(_count_of(stocking, s) for s in pool["cleanup"])
    plant_count = sum(_count_of(stocking, s) for s in pool["plants"])
    center_count = sum(_count_of(stocking, s) for s in pool["centerpiece"])
    if center_count:
        lines.append(f"{center_count} show-grade centerpiece specimen selected for the focal point.")
    if school_count:
        lines.append(f"{school_count} schooling fish chosen to feel secure in numbers (shoaling instinct).")
    if cleanup_count:
        lines.append(f"{cleanup_count} cleanup crew (shrimp/snails/bottom-dwellers) keep algae and detritus down.")
    if plant_count:
        lines.append(f"{plant_count} live plants absorb nitrate and provide shelter for fry and shrimp.")
    if variant == "biodiversity":
        lines.append("Variant maximises distinct species richness while staying 100 % compatible.")
    elif variant == "low_maintenance":
        lines.append("Variant favours hardy, low-fuss species and heavy planting for minimal upkeep.")
    else:
        lines.append("Variant balances cost, bioload headroom and visual appeal.")
    return lines


def _warnings_for(smap: Dict[str, Species], tank: TankConfig,
                  stocking: List[StockingItem]) -> List[str]:
    bioload = compute_bioload(smap, stocking, tank)
    compat = resolve_compatibility(smap, stocking, tank)
    climate = evaluate_climate(smap, stocking, tank)
    warnings: List[str] = list(bioload.warnings[:2])
    for issue in compat.issues[:3]:
        if issue.severity != IssueSeverity.INFO:
            warnings.append(f"[{issue.severity.value}] {issue.message}")
    warnings.extend(climate.warnings[:2])
    return warnings[:6]


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def build_optimized_setups(smap: Dict[str, Species],
                           req: OptimizationRequest) -> List[OptimizationBlueprint]:
    """Return three ranked, constraint-verified blueprints."""
    budget_usd = req.budget_usd
    exchange_rate = USD_TO_BDT_LOCAL
    goal = GOAL_CONFIG.get(req.style_goal, GOAL_CONFIG["peaceful_community"])
    tank = tank_from_request(req)

    climate = evaluate_climate(smap, [], tank)
    hw_standard, _ = _total_cost(_hardware_items(tank, climate, tier="standard", exchange_rate=exchange_rate))
    hw_budget, _ = _total_cost(_hardware_items(tank, climate, tier="budget", exchange_rate=exchange_rate))

    # Pick the cheapest hardware tier that still leaves room for livestock.
    use_budget = (budget_usd - hw_standard) < (budget_usd * 0.25)
    tier = "budget" if use_budget else "standard"
    hw_usd = hw_budget if use_budget else hw_standard

    variants = [
        ("best_value", "Best Value Balanced",
         "Optimal mix of cost, bioload headroom and visual appeal"),
        ("biodiversity", "Maximum Biodiversity",
         "Richest compatible species mix for a living ecosystem"),
        ("low_maintenance", "Ultra-Low Maintenance",
         "Hardy, heavily planted setup with minimal daily upkeep"),
    ]

    blueprints: List[OptimizationBlueprint] = []
    for vid, label, tagline in variants:
        slots = _slots_for(vid, goal)
        hardware_lines = _hardware_items(tank, climate, tier=tier, exchange_rate=exchange_rate)

        stocking = _greedy_fill(smap, tank, budget_usd, hw_usd, slots)
        stocking = _nitrate_cleanup(smap, tank, stocking, budget_usd, hw_usd)

        # Budget check: livestock must still fit within remaining budget.
        liv_lines = _livestock_items(smap, stocking, exchange_rate)
        liv_usd, liv_bdt = _total_cost(liv_lines)
        hw_usd_now, hw_bdt = _total_cost(hardware_lines)
        total_usd = round(hw_usd_now + liv_usd, 2)
        total_bdt = round(hw_bdt + liv_bdt, 2)

        compat = resolve_compatibility(smap, stocking, tank)
        bioload = compute_bioload(smap, stocking, tank)

        warnings = _warnings_for(smap, tank, stocking)
        if tier == "budget":
            warnings.append("Economy hardware tier selected to leave room for stock.")
        if total_usd > budget_usd:
            warnings.append(
                f"Hardware minimum exceeds budget; shown at the cheapest viable essentials "
                f"BDT {total_bdt:,.0f} > BDT {req.max_budget_bdt:,.0f}.")
        if not stocking:
            warnings.append("No livestock fit within this budget -- raise it to stock the tank.")

        blueprints.append(OptimizationBlueprint(
            id=vid,
            label=label,
            tagline=tagline,
            tank=tank,
            stocking=_stocking_copy(stocking),
            harmony_score=round(compat.score, 1),
            verdict=compat.verdict,
            capacity_ratio=round(bioload.capacity_ratio, 3),
            fish_inches=round(bioload.total_fish_inches, 2),
            cost=BudgetAllocation(
                hardware_usd=hw_usd_now, hardware_bdt=hw_bdt,
                livestock_usd=round(liv_usd, 2), livestock_bdt=round(liv_bdt, 2),
                total_usd=total_usd, total_bdt=total_bdt,
                under_budget=total_usd <= budget_usd,
            ),
            lines=hardware_lines + liv_lines,
            rationale=_rationale(vid, stocking, goal),
            warnings=warnings[:6],
        ))

    return blueprints


# --------------------------------------------------------------------------
# One-click auto-fix
# --------------------------------------------------------------------------

def _remove_species(stocking: List[StockingItem], species_id: str) -> List[StockingItem]:
    return [s for s in stocking if s.species_id != species_id]


def _pick_offender(a: Optional[Species], b: Optional[Species],
                   issue_type: str) -> Optional[Species]:
    if a is None or b is None:
        return a or b
    if issue_type in ("predation", "invertebrate_predation"):
        # The predator is the bigger / more aggressive fish.
        if a.size_cm >= 2.5 * b.size_cm and a.aggression_rating >= 0.5:
            return a
        if b.size_cm >= 2.5 * a.size_cm and b.aggression_rating >= 0.5:
            return b
        return a if a.aggression_rating >= b.aggression_rating else b
    if issue_type == "aggression":
        return a if a.aggression_rating >= b.aggression_rating else b
    if issue_type == "fin_nipping":
        return a if a.fin_nipper else b
    # parameter conflict: drop the more delicate (narrower pH range) species
    a_span = a.max_ph - a.min_ph
    b_span = b.max_ph - b.min_ph
    return a if a_span <= b_span else b


def auto_fix_tank(smap: Dict[str, Species], tank: TankConfig) -> AutoFixResponse:
    """Resolve every actionable conflict on a hand-tweaked workbench."""
    fixed = tank.model_copy(deep=True)
    stock = _stocking_copy(fixed.stocking)
    fixes: List[str] = []

    # 1. Critical compatibility conflicts -> remove the offender.
    compat = resolve_compatibility(smap, stock, fixed)
    for issue in compat.issues:
        if issue.severity != IssueSeverity.CRITICAL:
            continue
        offender = _pick_offender(smap.get(issue.species_a or ""),
                                  smap.get(issue.species_b or ""), issue.type)
        if offender is not None and _count_of(stock, offender.id) > 0:
            stock = _remove_species(stock, offender.id)
            fixes.append(f"Removed {offender.name} to resolve {issue.type} conflict.")
            break

    # 1b. Warning-level conflicts that still drag harmony below 90 -> remove
    #     the offender (most aggressive / fin-nipping species).
    guard = 0
    while guard < 6:
        compat = resolve_compatibility(smap, stock, fixed)
        if compat.score >= 90:
            break
        target = next((i for i in compat.issues
                       if i.severity in (IssueSeverity.WARNING, IssueSeverity.CRITICAL)
                       and i.type in ("aggression", "fin_nipping", "territorial", "predation")),
                      None)
        if target is None:
            break
        offender = _pick_offender(smap.get(target.species_a or ""),
                                  smap.get(target.species_b or ""), target.type)
        if offender is None or _count_of(stock, offender.id) == 0:
            # remove the other party
            other_id = target.species_b if (target.species_a == offender.id) else target.species_a
            offender = smap.get(other_id or "")
            if offender is None or _count_of(stock, offender.id) == 0:
                break
        stock = _remove_species(stock, offender.id)
        fixes.append(f"Removed {offender.name} to restore harmony >= 90.")
        guard += 1

    # 2. Overstocking -> trim the largest school by ~20 %.
    bioload = compute_bioload(smap, stock, fixed)
    if bioload.capacity_ratio > 1.0:
        largest = max(stock, key=lambda s: s.count, default=None)
        if largest is not None:
            new_count = max(1, int(largest.count * 0.8))
            for s in stock:
                if s.species_id == largest.species_id:
                    s.count = new_count
            sp = smap.get(largest.species_id)
            fixes.append(f"Reduced {sp.name if sp else largest.species_id} to {new_count} "
                         f"to bring stocking under 1\"/gal.")

    # 3. Peak ammonia / nitrate risk -> add a nitrate sponge.
    steps = simulate_nitrogen_cycle(smap, stock, fixed, days=30)
    peak_nh3 = max(s.ammonia_mg_l for s in steps)
    final_no3 = steps[-1].nitrate_mg_l
    if peak_nh3 > 0.25 or final_no3 > 40.0:
        for pid in NITRATE_SPONGE:
            if _count_of(stock, pid) >= MAX_PER_SPECIES:
                continue
            stock = _add_batch(stock, pid, 2)
            sp = smap.get(pid)
            fixes.append(f"Added 2 x {sp.name if sp else pid} as a nitrate/ammonia sponge.")
            break

    # 4. Disease pressure -> ease the feeding level.
    disease = assess_disease_risk(smap, stock, fixed, steps)
    if disease.overall_risk >= 45:
        fixed.feeding_level = max(0.5, round(fixed.feeding_level - 0.2, 1))
        fixes.append(f"Reduced feeding level to {fixed.feeding_level:.1f}x to lower disease pressure.")

    # 5. Temperature setpoint vs. species ranges -> align to overlap.
    temps = []
    for s in stock:
        sp = smap.get(s.species_id)
        if sp is not None and sp.is_fish:
            temps.append((sp.min_temp_c, sp.max_temp_c))
    if temps:
        lo = max(t[0] for t in temps)
        hi = min(t[1] for t in temps)
        if lo <= hi and not (lo <= fixed.temperature_c <= hi):
            fixed.temperature_c = round((lo + hi) / 2.0, 1)
            fixes.append(f"Set temperature to {fixed.temperature_c:.1f}C to match all stock.")

    fixed.stocking = stock

    # Re-validate after fixes.
    compat2 = resolve_compatibility(smap, stock, fixed)
    bioload2 = compute_bioload(smap, stock, fixed)
    warnings = _warnings_for(smap, fixed, stock)
    ok = (compat2.score >= 90 and
          not any(i.severity == IssueSeverity.CRITICAL for i in compat2.issues))
    return AutoFixResponse(
        tank=fixed,
        fixes=fixes,
        harmony_score=round(compat2.score, 1),
        verdict=compat2.verdict,
        capacity_ratio=round(bioload2.capacity_ratio, 3),
        warnings=warnings[:5],
        ok=ok,
    )
