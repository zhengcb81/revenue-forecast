"""Strict work-unit state machine (CA-101).

Replaces Markdown substring status juggling with:

- a closed state enum (CA registry 12 states ∪ runbook lifecycle states);
- ONE-DIRECTIONAL legal transitions (rework loops are explicit);
- a dependency gate: leaving ``pending`` (except to ``blocked``/``superseded``)
  requires every dependency to be ``accepted`` or ``already_satisfied``;
- a reviewer gate: ``accepted`` requires a reviewer identity distinct from the
  recorded implementer;
- per-unit single-writer locks (the caller wires uc.lock around transitions).
"""

from __future__ import annotations

from typing import Iterable

# CA registry §0 enum ∪ runbook §1 lifecycle states.
STATES = frozenset(
    {
        "pending",
        "preflight_locked",
        "drift_classified",
        "red_proved",
        "implemented",
        "focused_green",
        "owner_repo_green",
        "triplet_green",
        "real_tier_green",
        "rollback_green",
        "independent_review",
        "accepted",
        "blocked",
        "superseded",
        "already_satisfied",
    }
)

TERMINAL_STATES = frozenset({"accepted", "superseded"})

LEGAL_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset(
        {"preflight_locked", "blocked", "superseded", "already_satisfied"}
    ),
    "preflight_locked": frozenset({"drift_classified", "red_proved", "blocked"}),
    "drift_classified": frozenset(
        {"red_proved", "blocked", "superseded", "already_satisfied"}
    ),
    "red_proved": frozenset({"implemented", "blocked"}),
    "implemented": frozenset({"focused_green", "blocked"}),
    "focused_green": frozenset({"owner_repo_green", "blocked"}),
    "owner_repo_green": frozenset({"triplet_green", "blocked"}),
    "triplet_green": frozenset({"real_tier_green", "independent_review", "blocked"}),
    "real_tier_green": frozenset({"rollback_green", "independent_review", "blocked"}),
    "rollback_green": frozenset({"independent_review", "blocked"}),
    # changes_required rework loops back to implemented; accepted is terminal.
    "independent_review": frozenset({"accepted", "implemented", "blocked"}),
    "accepted": frozenset(),
    "blocked": frozenset({"preflight_locked", "implemented", "superseded"}),
    "superseded": frozenset(),
    "already_satisfied": frozenset({"independent_review", "accepted", "blocked"}),
}

# States that require every dependency satisfied before entering.
DEP_GATED_STATES = frozenset(STATES - {"pending", "blocked", "superseded"})


class IllegalTransition(Exception):
    """The requested state change violates the one-directional transition table."""


class DependencyGateError(Exception):
    """A transition was attempted while dependencies are unsatisfied."""


class ReviewerGateError(Exception):
    """``accepted`` requires a reviewer distinct from the implementer."""


def legal_transition(from_state: str, to_state: str) -> bool:
    return to_state in LEGAL_TRANSITIONS.get(from_state, frozenset())


def _deps_satisfied(
    unit_id: str,
    deps: Iterable[str],
    units: dict[str, dict],
) -> bool:
    for dep in deps:
        info = units.get(dep, {})
        if info.get("status") not in ("accepted", "already_satisfied"):
            return False
    return True


def validate_transition(
    unit_id: str,
    current: dict,
    target_status: str,
    *,
    deps: Iterable[str],
    reviewer: str | None = None,
    implementer: str | None = None,
) -> list[str]:
    """Return validation problems (empty = transition legal)."""
    problems: list[str] = []
    if target_status not in STATES:
        problems.append(f"unknown state: {target_status!r}")
        return problems
    units = current.get("units", {})
    info = units.get(unit_id, {})
    from_status = info.get("status", "pending")
    if from_status not in STATES:
        problems.append(f"current state not in enum: {from_status!r}")
        return problems
    if not legal_transition(from_status, target_status):
        problems.append(f"illegal transition: {from_status} -> {target_status}")
    if target_status in DEP_GATED_STATES and not _deps_satisfied(unit_id, deps, units):
        unsatisfied = [
            dep
            for dep in deps
            if units.get(dep, {}).get("status") not in ("accepted", "already_satisfied")
        ]
        problems.append(f"dependencies unsatisfied: {unsatisfied}")
    if target_status == "accepted":
        record_implementer = info.get("implementer") or implementer
        if not reviewer:
            problems.append("accepted requires a reviewer identity")
        elif reviewer == record_implementer:
            problems.append("reviewer must differ from implementer")
    return problems
