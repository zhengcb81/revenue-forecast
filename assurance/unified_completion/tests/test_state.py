"""Machine state: exact-once bootstrap, CAS update, conflict detection."""

from __future__ import annotations

import json

import pytest

from uc.casfile import CASConflict
from uc.state import StateExistsError, bootstrap_state, read_state, update_state

TRIPLET = {
    "revenue": "c" * 40,
    "filing": "f" * 40,
    "wiki": "w" * 40,
}


def _bootstrap(path) -> None:
    bootstrap_state(
        state_path=path,
        plan_id="TEST-PLAN",
        base_triplet=TRIPLET,
        control_page="audit_review/README.md",
        control_page_sha256="a" * 64,
        manifest_path="assurance/unified_completion/manifests/plan_inputs.json",
        manifest_sha256="b" * 64,
        current_phase="A0_bootstrap_and_rebaseline",
        current_next="CA-001",
    )


def test_bootstrap_creates_minimal_schema(tmp_path):
    path = tmp_path / "state.json"
    _bootstrap(path)
    state = read_state(path)
    assert state["schema_version"] == 1
    assert state["machine_state_authority"] is True
    assert state["current_next"] == "CA-001"
    assert state["base_triplet"] == TRIPLET
    assert state["units"] == {}


def test_bootstrap_is_exact_once(tmp_path):
    path = tmp_path / "state.json"
    _bootstrap(path)
    with pytest.raises(StateExistsError):
        _bootstrap(path)
    # original state untouched
    assert read_state(path)["current_next"] == "CA-001"


def test_update_state_transform(tmp_path):
    path = tmp_path / "state.json"
    _bootstrap(path)
    expected, new_hash = update_state(path, lambda s: {**s, "current_next": "CA-002"})
    state = read_state(path)
    assert state["current_next"] == "CA-002"
    assert new_hash != expected


def test_update_state_detects_concurrent_modification(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    _bootstrap(path)

    def rogue_transform(state):
        # a rogue writer modifies the file behind our back inside the window
        rogue = dict(state)
        rogue["current_next"] = "CA-999"
        path.write_text(
            json.dumps(rogue, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return {**state, "current_next": "CA-002"}

    with pytest.raises(CASConflict):
        update_state(path, rogue_transform)
    # our write was refused; the file still holds the rogue value — the
    # conflict was DETECTED, not silently overwritten
    assert read_state(path)["current_next"] == "CA-999"


def test_update_state_missing_state(tmp_path):
    with pytest.raises(FileNotFoundError):
        update_state(tmp_path / "state.json", lambda s: s)
