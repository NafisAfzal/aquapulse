"""Pydantic domain models for AquaPulse.

These models define the contracts shared between the engine modules, the
FastAPI layer, and the frontend. They are intentionally dependency-free
apart from ``pydantic``.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field


class SpeciesCategory(str, Enum):
    FISH = "fish"
    INVERTEBRATE = "invertebrate"
    PLANT = "plant"


class SwimZone(str, Enum):
    TOP = "top"
    MID = "mid"
    BOTTOM = "bottom"


class Temperament(str, Enum):
    PEACEFUL = "peaceful"
    SEMI_AGGRESSIVE = "semi-aggressive"
    AGGRESSIVE = "aggressive"


class Species(BaseModel):
    """A catalog entry describing a single organism."""
    id: str
    name: str
    scientific_name: str = ""
    category: SpeciesCategory = SpeciesCategory.FISH
    size_cm: float = Field(gt=0, le=120)
    min_tank_gal: float = Field(ge=0)
    temperament: Temperament = Temperament.PEACEFUL
    swim_zone: SwimZone = SwimZone.MID
    min_temp_c: float = Field(ge=0, le=40)
    max_temp_c: float = Field(ge=0, le=40)
    min_ph: float = Field(ge=0, le=14)
    max_ph: float = Field(ge=0, le=14)
    min_gh: float = Field(ge=0, le=30)
    max_gh: float = Field(ge=0, le=30)
    aggression_rating: float = Field(ge=0, le=1, default=0.2)
    fin_nipper: bool = False
    territorial: bool = False
    plant_safe: bool = True
    bioload_factor: float = Field(ge=0.1, le=5, default=1.0)
    emoji: str = "🐟"
    price_usd: float = Field(ge=0, default=5.0)
    description: str = ""

    def temp_range(self) -> tuple[float, float]:
        return (self.min_temp_c, self.max_temp_c)

    def ph_range(self) -> tuple[float, float]:
        return (self.min_ph, self.max_ph)

    def gh_range(self) -> tuple[float, float]:
        return (self.min_gh, self.max_gh)

    @property
    def is_fish(self) -> bool:
        return self.category == SpeciesCategory.FISH

    @property
    def is_plant(self) -> bool:
        return self.category == SpeciesCategory.PLANT


class StockingItem(BaseModel):
    """A species id and how many of them the user wants."""
    species_id: str
    count: int = Field(gt=0, le=1000)


class TankConfig(BaseModel):
    """User-configured aquarium dimensions and water parameters."""
    length_in: float = Field(gt=0, le=300, default=24)
    width_in: float = Field(gt=0, le=120, default=12)
    height_in: float = Field(gt=0, le=120, default=16)
    water_level_pct: float = Field(gt=0, le=100, default=90)
    filter_gph: float = Field(ge=0, le=10000, default=100)
    filter_type: str = Field(default="HOB")  # HOB / canister / sponge / internal
    substrate: str = Field(default="sand")   # sand / gravel / soil / bare
    planted: bool = True
    temperature_c: float = Field(ge=0, le=45, default=25)
    ph: float = Field(ge=0, le=14, default=7.0)
    gh: float = Field(ge=0, le=30, default=8)
    stocking: List[StockingItem] = Field(default_factory=list)
    water_change_pct: float = Field(ge=0, le=100, default=25)
    water_change_freq_days: int = Field(ge=1, le=30, default=7)
    feeding_per_day: int = Field(ge=0, le=10, default=2)
    food_amount_g: float = Field(ge=0, le=50, default=1.5)
    # v1.0.0 additions
    room_climate: str = Field(default="climate_controlled")
    currency: str = Field(default="USD")  # USD or BDT
    feeding_level: float = Field(ge=0, le=3, default=1.0)

    @property
    def water_height_in(self) -> float:
        return self.height_in * (self.water_level_pct / 100.0)

    @computed_field
    @property
    def volume_gal(self) -> float:
        """Volume in US gallons: L*W*H(in) / 231."""
        return round((self.length_in * self.width_in * self.water_height_in) / 231.0, 3)

    @computed_field
    @property
    def volume_l(self) -> float:
        return round(self.volume_gal * 3.785411784, 3)

    @computed_field
    @property
    def surface_area_in2(self) -> float:
        return round(self.length_in * self.width_in, 2)


class SimulationStep(BaseModel):
    """One day of the nitrogen-cycle simulation."""
    day: int
    ammonia_mg_l: float
    nitrite_mg_l: float
    nitrate_mg_l: float
    ph: float
    oxygen_mg_l: float
    bacteria_aob: float
    bacteria_nob: float
    plant_uptake_nitrate: float
    water_changed: bool = False


class IssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CompatibilityIssue(BaseModel):
    type: str
    severity: IssueSeverity
    message: str
    species_a: Optional[str] = None
    species_b: Optional[str] = None
    value: Optional[float] = None


class CompatibilityReport(BaseModel):
    score: float = Field(ge=0, le=100)
    verdict: str
    issues: List[CompatibilityIssue] = Field(default_factory=list)


class BioloadResult(BaseModel):
    volume_gal: float
    volume_l: float
    total_fish_inches: float
    total_bioload_points: float
    filter_capacity_points: float
    capacity_ratio: float
    stocking_rating: str
    zone_crowding: dict[str, float]
    zone_capacity: dict[str, float]
    warnings: List[str] = Field(default_factory=list)


class CareItem(BaseModel):
    name: str
    detail: str
    cadence: str


class BudgetItem(BaseModel):
    item: str
    category: str
    cost_usd: float
    cost_bdt: float = 0.0
    qty: float = 1
    note: str = ""


class DosageItem(BaseModel):
    product: str
    quantity: float
    unit: str
    note: str = ""


class DiseaseRisk(BaseModel):
    id: str
    name: str
    risk_pct: float = Field(ge=0, le=100)
    severity: str
    causes: List[str] = Field(default_factory=list)
    advice: str = ""
    dosages: List[DosageItem] = Field(default_factory=list)


class DiseaseReport(BaseModel):
    risks: List[DiseaseRisk] = Field(default_factory=list)
    overall_risk: float = Field(ge=0, le=100)
    salt_sensitive_species: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class BreederInfo(BaseModel):
    species_id: str
    name: str
    emoji: str = "🐟"
    count: int
    offspring_60d: int


class BreedingReport(BaseModel):
    prolific_species: List[BreederInfo] = Field(default_factory=list)
    fry_survival_pct: float = Field(ge=0, le=100)
    projected_population_60d: int = 0
    current_population: int = 0
    boom_risk: str = "stable"
    cover_bonus_pct: float = 0
    predation_penalty_pct: float = 0
    notes: List[str] = Field(default_factory=list)


class ClimateReport(BaseModel):
    preset_id: str
    preset_name: str
    room_temp_c: float
    target_temp_c: float
    heater_watts_required: int = 0
    cooling_fan_recommended: bool = False
    expected_temp_after_mitigation_c: float
    warnings: List[str] = Field(default_factory=list)
    species_thermal_conflicts: List[str] = Field(default_factory=list)


class CurrencyTotals(BaseModel):
    usd: float
    bdt: float


class AnalyzeResponse(BaseModel):
    tank: TankConfig
    bioload: BioloadResult
    compatibility: CompatibilityReport
    care_plan: List[CareItem] = Field(default_factory=list)
    budget: List[BudgetItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    # v1.0.0
    disease: DiseaseReport | None = None
    breeding: BreedingReport | None = None
    climate: ClimateReport | None = None
    totals: CurrencyTotals | None = None
    exchange_rate: float = 120.0


class SimulateResponse(BaseModel):
    steps: List[SimulationStep]
    summary: dict


class Preset(BaseModel):
    id: str
    name: str
    description: str
    tank: TankConfig
    stocking: List[StockingItem]


class SaveBuildResponse(BaseModel):
    id: int
    ok: bool


# --------------------------------------------------------------------------
# v1.0.0 - Auto-Architect constraint optimizer
# --------------------------------------------------------------------------

class OptimizationRequest(BaseModel):
    """Inputs for the multi-objective setup constraint solver."""
    max_budget_bdt: float = Field(ge=0, default=20000.0)
    max_budget_usd: Optional[float] = Field(default=None, ge=0)
    tank_liters: float = Field(ge=5, le=2000, default=75.0)
    climate_preset: str = Field(default="climate_controlled")
    style_goal: str = Field(default="peaceful_community")
    currency: str = Field(default="USD")

    @computed_field
    @property
    def budget_usd(self) -> float:
        if self.max_budget_usd is not None:
            return self.max_budget_usd
        return round(self.max_budget_bdt / 120.0, 2)


class BudgetAllocation(BaseModel):
    hardware_usd: float = 0.0
    hardware_bdt: float = 0.0
    livestock_usd: float = 0.0
    livestock_bdt: float = 0.0
    total_usd: float = 0.0
    total_bdt: float = 0.0
    under_budget: bool = True


class OptimizationBlueprint(BaseModel):
    """One complete, constraint-verified setup proposal."""
    id: str
    label: str
    tagline: str
    tank: TankConfig
    stocking: List[StockingItem] = Field(default_factory=list)
    harmony_score: float = Field(ge=0, le=100)
    verdict: str = ""
    capacity_ratio: float = 0.0
    fish_inches: float = 0.0
    cost: BudgetAllocation = BudgetAllocation()
    lines: List[BudgetItem] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class OptimizationResponse(BaseModel):
    request: OptimizationRequest
    blueprints: List[OptimizationBlueprint] = Field(default_factory=list)


class AutoFixResponse(BaseModel):
    """Result of a one-click conflict auto-fix on the current workbench."""
    tank: TankConfig
    fixes: List[str] = Field(default_factory=list)
    harmony_score: float = 100.0
    verdict: str = ""
    capacity_ratio: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    ok: bool = True


# --------------------------------------------------------------------------
# v1.0.0 - Commercial biofloc & aquaculture ROI simulator
# --------------------------------------------------------------------------

class CommercialSpeciesInfo(BaseModel):
    id: str
    name: str
    scientific_name: str = ""
    optimal_temp_c: float = 28.0
    protein_pct: float = 30.0
    fcr_target: float = 1.7
    survival_rate: float = Field(ge=0, le=1, default=0.9)
    typical_target_g: float = 250.0
    do_min_mg_l: float = 3.5
    notes: str = ""


class CommercialRequest(BaseModel):
    species_id: str = "monosex_tilapia"
    volume_l: float = Field(ge=1000, le=200000, default=10000.0)
    stocking_count: int = Field(ge=1, le=1000000, default=5000)
    initial_weight_g: float = Field(ge=0.1, default=20.0)
    target_weight_g: float = Field(ge=1.0, default=500.0)
    duration_days: int = Field(ge=30, le=365, default=120)
    ph: float = Field(ge=0, le=14, default=7.5)
    temperature_c: float = Field(ge=0, le=45, default=28.0)
    feed_price_bdt: float = Field(ge=0, default=60.0)
    fingerling_price_bdt: float = Field(ge=0, default=12.0)
    market_price_bdt: float = Field(ge=0, default=180.0)
    system_type: str = Field(default="Biofloc Tank")
    molasses_price_bdt: float = Field(ge=0, default=25.0)
    electricity_rate_bdt: float = Field(ge=0, default=9.0)


class CommercialWeeklyRow(BaseModel):
    week: int
    day: int
    weight_g: float
    biomass_kg: float
    survival_pct: float
    feed_kg_day: float
    feed_rate_pct: float
    cumulative_feed_kg: float
    tan_mg_l: float
    nh3_mg_l: float
    molasses_g_day: float
    aeration_lpm: float
    do_mg_l: float


class CommercialSummary(BaseModel):
    harvest_biomass_kg: float = 0.0
    survival_pct: float = 0.0
    fcr: float = 0.0
    total_feed_kg: float = 0.0
    total_molasses_kg: float = 0.0
    fingerling_cost_bdt: float = 0.0
    feed_cost_bdt: float = 0.0
    electricity_cost_bdt: float = 0.0
    molasses_cost_bdt: float = 0.0
    probiotics_cost_bdt: float = 0.0
    labor_cost_bdt: float = 0.0
    total_cost_bdt: float = 0.0
    gross_revenue_bdt: float = 0.0
    net_profit_bdt: float = 0.0
    roi_pct: float = 0.0
    break_even_bdt_per_kg: float = 0.0
    nh3_fraction: float = 0.0
    tan_mg_l: float = 0.0
    nh3_mg_l: float = 0.0
    aeration_lpm: float = 0.0
    max_biomass_kg: float = 0.0
    max_daily_feed_kg: float = 0.0
    max_daily_molasses_g: float = 0.0
    warnings: List[str] = Field(default_factory=list)


class CommercialReport(BaseModel):
    request: CommercialRequest
    species: CommercialSpeciesInfo
    rows: List[CommercialWeeklyRow] = Field(default_factory=list)
    summary: CommercialSummary
