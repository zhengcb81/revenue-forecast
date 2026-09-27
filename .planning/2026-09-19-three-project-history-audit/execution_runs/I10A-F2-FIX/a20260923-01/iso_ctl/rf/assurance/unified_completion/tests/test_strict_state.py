"""CA-101 strict state machine: legal transitions, dependency gate, reviewer
gate, cycle detection, and property-style rejection of illegal inputs."""

from __future__ import annotations

import itertools


from uc.dag import cycle_check
from uc.strict_state import (
    LEGAL_TRANSITIONS,
    STATES,
    validate_transition,
)


def _state(units: dict | None = None) -> dict:
    return {"units": units or {}}


def test_all_states_have_a_transition_table():
    assert set(LEGAL_TRANSITIONS) == set(STATES)


def test_transitions_are_one_directional():
    """No reverse edge may exist except the documented rework loops
    (blocked <-> preflight_locked, independent_review -> implemented)."""
    rework_pairs = {
        frozenset({"blocked", "preflight_locked"}),
        frozenset({"implemented", "independent_review"}),
        frozenset({"blocked", "implemented"}),
    }
    for src, targets in LEGAL_TRANSITIONS.items():
        for dst in targets:
            if dst in LEGAL_TRANSITIONS and src in LEGAL_TRANSITIONS[dst]:
                assert frozenset({src, dst}) in rework_pairs, (
                    f"bidirectional edge {src}<->{dst} is not a documented rework loop"
                )


def test_every_illegal_pair_rejected():
    """Property: every pair NOT in the table must be rejected."""
    for src, dst in itertools.product(STATES, STATES):
        state = _state({"X-1": {"status": src, "implementer": "impl"}})
        problems = validate_transition("X-1", state, dst, deps=[], reviewer="rev")
        should_be_legal = dst in LEGAL_TRANSITIONS.get(src, frozenset())
        if should_be_legal:
            assert not any("illegal transition" in p for p in problems), (
                f"{src}->{dst} wrongly rejected: {problems}"
            )
        else:
            assert any("illegal transition" in p for p in problems), (
                f"{src}->{dst} wrongly accepted"
            )


def test_unknown_state_rejected():
    state = _state({"X-1": {"status": "pending"}})
    problems = validate_transition("X-1", state, "accepted_today", deps=[])
    assert any("unknown state" in p for p in problems)


def test_dependency_gate_blocks_advance():
    state = _state({"X-1": {"status": "pending"}})
    problems = validate_transition(
        "X-1", state, "preflight_locked", deps=["X-0"], reviewer="rev"
    )
    assert any("dependencies unsatisfied" in p for p in problems)


def test_dependency_gate_allows_blocked_and_superseded():
    state = _state({"X-1": {"status": "pending"}})
    assert not any(
        "dependencies unsatisfied" in p
        for p in validate_transition("X-1", state, "blocked", deps=["X-0"])
    )
    assert not any(
        "dependencies unsatisfied" in p
        for p in validate_transition("X-1", state, "superseded", deps=["X-0"])
    )


def test_dependency_gate_satisfied_dep_passes():
    state = _state(
        {
            "X-0": {"status": "accepted"},
            "X-1": {"status": "pending"},
        }
    )
    assert (
        validate_transition(
            "X-1", state, "preflight_locked", deps=["X-0"], reviewer="rev"
        )
        == []
    )


def test_reviewer_gate_accepted_requires_distinct_reviewer():
    state = _state(
        {
            "X-1": {
                "status": "independent_review",
                "implementer": "impl-A",
            }
        }
    )
    assert any(
        "reviewer" in p for p in validate_transition("X-1", state, "accepted", deps=[])
    )
    assert any(
        "reviewer" in p
        for p in validate_transition(
            "X-1", state, "accepted", deps=[], reviewer="impl-A"
        )
    )
    assert (
        validate_transition("X-1", state, "accepted", deps=[], reviewer="rev-B") == []
    )


def test_cycle_check_detects_cycles():
    assert cycle_check({"A": ["B"], "B": ["A"]}) == ["A -> B -> A"]
    assert cycle_check({"A": ["B"], "B": []}) == []
    assert cycle_check({"A": ["A"]}) == ["A -> A"]


def test_cycle_check_empty_and_missing_nodes():
    assert cycle_check({}) == []
    assert cycle_check({"A": ["MISSING"]}) == []  # dangling dep is not a cycle


def test_random_illegal_graphs_rejected_by_validator():
    """Property: for every pair of states, an illegal jump must be rejected
    even with satisfied dependencies and a reviewer present."""
    state = _state(
        {
            "D-0": {"status": "accepted"},
            "X-1": {"status": "pending", "implementer": "impl"},
        }
    )
    illegal_jumps = [
        (src, dst)
        for src, dst in itertools.product(STATES, STATES)
        if dst not in LEGAL_TRANSITIONS.get(src, frozenset())
    ]
    for src, dst in illegal_jumps:
        state["units"]["X-1"]["status"] = src
        problems = validate_transition("X-1", state, dst, deps=["D-0"], reviewer="rev")
        assert any("illegal transition" in p for p in problems), (
            f"validator accepted illegal jump {src}->{dst}"
        )
