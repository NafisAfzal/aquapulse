"""Pairwise species-compatibility resolver.

For every ordered pair of distinct species present in the tank we run a
set of fast algebraic checks:

1. Fin-nipping      – a fin_nipper vs. a species with long fins
                      (proxied by aggression rating of the victim: peaceful
                      fish with a large body are the most likely victims).
2. Aggression       – combined aggression score of the pair.
3. Territorial      – two territorial species sharing the same swim zone.
4. Predation        – size mismatch: if the predator is >= 2.5x the size
                      of the other, smaller species is at risk of being eaten
                      (only applies when predator has aggression_rating >= 0.5).
5. Water parameters – temperature / pH / GH intervals must overlap for
                      both species to coexist comfortably.

Each check produces a :class:`CompatibilityIssue` with a severity. The
overall score starts at 100 and is reduced by a weighted penalty per
issue.
"""
from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple

from ..models import (
    CompatibilityIssue,
    CompatibilityReport,
    IssueSeverity,
    Species,
    StockingItem,
    Temperament,
    SwimZone,
    TankConfig,
)

PENALTIES = {
    IssueSeverity.INFO: 2,
    IssueSeverity.WARNING: 8,
    IssueSeverity.CRITICAL: 20,
}

PREDACTION_SIZE_RATIO = 2.5
PREDACTION_MIN_AGGRESSION = 0.5


def _ranges_overlap(a: Tuple[float, float], b: Tuple[float, float]) -> bool:
    return a[0] <= b[1] and b[0] <= a[1]


def _param_issue(label: str, a: Species, b: Species,
                 a_range: Tuple[float, float], b_range: Tuple[float, float]) -> CompatibilityIssue | None:
    if _ranges_overlap(a_range, b_range):
        return None
    return CompatibilityIssue(
        type=f"param_{label}",
        severity=IssueSeverity.CRITICAL,
        message=(f"{a.name} and {b.name} need incompatible {label}: "
                 f"{a_range[0]}-{a_range[1]} vs {b_range[0]}-{b_range[1]}"),
        species_a=a.id,
        species_b=b.id,
    )


def _check_pair(a: Species, b: Species) -> List[CompatibilityIssue]:
    issues: List[CompatibilityIssue] = []

    # 1. Fin-nipping (only fish nip; plants/shrimp are not sources)
    if a.is_fish and b.is_fish:
        nip_a = a.fin_nipper and b.temperament == Temperament.PEACEFUL
        nip_b = b.fin_nipper and a.temperament == Temperament.PEACEFUL
        if nip_a or nip_b:
            nipper = a if nip_a else b
            victim = b if nip_a else a
            issues.append(CompatibilityIssue(
                type="fin_nipping",
                severity=IssueSeverity.WARNING,
                message=f"{nipper.name} may nip the fins of {victim.name}",
                species_a=nipper.id,
                species_b=victim.id,
            ))

        # 2. Aggression
        combined = (a.aggression_rating + b.aggression_rating) / 2.0
        if combined >= 0.7:
            issues.append(CompatibilityIssue(
                type="aggression",
                severity=IssueSeverity.CRITICAL,
                message=f"{a.name} and {b.name} are both highly aggressive",
                species_a=a.id,
                species_b=b.id,
                value=round(combined, 2),
            ))
        elif combined >= 0.45:
            issues.append(CompatibilityIssue(
                type="aggression",
                severity=IssueSeverity.WARNING,
                message=f"{a.name} and {b.name} may clash (combined aggression {combined:.2f})",
                species_a=a.id,
                species_b=b.id,
                value=round(combined, 2),
            ))

        # 3. Territorial overlap
        if a.territorial and b.territorial and a.swim_zone == b.swim_zone:
            issues.append(CompatibilityIssue(
                type="territorial",
                severity=IssueSeverity.WARNING,
                message=f"{a.name} and {b.name} are both territorial in the {a.swim_zone.value} zone",
                species_a=a.id,
                species_b=b.id,
            ))

        # 4. Predation / size mismatch
        if a.size_cm >= PREDACTION_SIZE_RATIO * b.size_cm and a.aggression_rating >= PREDACTION_MIN_AGGRESSION:
            issues.append(CompatibilityIssue(
                type="predation",
                severity=IssueSeverity.CRITICAL,
                message=f"{a.name} ({a.size_cm} cm) may eat {b.name} ({b.size_cm} cm)",
                species_a=a.id,
                species_b=b.id,
                value=round(a.size_cm / max(b.size_cm, 0.001), 1),
            ))
        if b.size_cm >= PREDACTION_SIZE_RATIO * a.size_cm and b.aggression_rating >= PREDACTION_MIN_AGGRESSION:
            issues.append(CompatibilityIssue(
                type="predation",
                severity=IssueSeverity.CRITICAL,
                message=f"{b.name} ({b.size_cm} cm) may eat {a.name} ({a.size_cm} cm)",
                species_a=b.id,
                species_b=a.id,
                value=round(b.size_cm / max(a.size_cm, 0.001), 1),
            ))

        # 5. Water parameter mismatches
        for label, ra, rb in (
            ("temperature", a.temp_range(), b.temp_range()),
            ("ph", a.ph_range(), b.ph_range()),
            ("gh", a.gh_range(), b.gh_range()),
        ):
            issue = _param_issue(label, a, b, ra, rb)
            if issue:
                issues.append(issue)

    # Invertebrates vs. predators: shrimp get eaten by many fish
    if (a.category.name == "INVERTEBRATE" and b.category.name == "FISH") or \
       (b.category.name == "INVERTEBRATE" and a.category.name == "FISH"):
        inv = a if a.category.name == "INVERTEBRATE" else b
        fis = b if a.category.name == "INVERTEBRATE" else a
        if fis.aggression_rating >= 0.6 and not fis.is_plant:
            issues.append(CompatibilityIssue(
                type="invertebrate_predation",
                severity=IssueSeverity.CRITICAL,
                message=f"{inv.name} is likely to be eaten by {fis.name}",
                species_a=inv.id,
                species_b=fis.id,
            ))

    return issues


def resolve_compatibility(species_by_id: Dict[str, Species],
                          stocking: List[StockingItem],
                          tank: TankConfig | None = None) -> CompatibilityReport:
    present: List[Species] = []
    seen = set()
    for item in stocking:
        sp = species_by_id.get(item.species_id)
        if sp is None or sp.id in seen:
            continue
        seen.add(sp.id)
        present.append(sp)

    issues: List[CompatibilityIssue] = []
    for a, b in combinations(present, 2):
        issues.extend(_check_pair(a, b))

    score = 100.0
    for issue in issues:
        score -= PENALTIES[issue.severity]
    score = max(0.0, min(100.0, score))

    if score >= 80:
        verdict = "excellent"
    elif score >= 55:
        verdict = "good"
    elif score >= 30:
        verdict = "risky"
    else:
        verdict = "incompatible"

    # Any critical issue (predation, incompatible water params) overrides
    # the score-based verdict: the tank is simply not viable as-is.
    if any(issue.severity == IssueSeverity.CRITICAL for issue in issues):
        verdict = "incompatible"

    if not present:
        return CompatibilityReport(score=100.0, verdict="empty tank", issues=[])

    return CompatibilityReport(score=round(score, 1), verdict=verdict, issues=issues)
