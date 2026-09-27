"""WU-1406 RED/audit tests: wave controller (WAVE-01..08)."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from release_state import (  # noqa: E402
    ReleaseState,
    next_allowed_wave,
    validate_manual_flag_change,
    validate_state,
)


def _state(**waves) -> ReleaseState:
    state = ReleaseState.fresh()
    for wave, status in waves.items():
        state.waves[wave] = status
    return state


def test_wave01_skipped_upstream_fails():
    state = _state(R2="completed")
    assert validate_state(state)


def test_wave01_valid_chain_passes():
    state = _state()
    for wave in ("R0", "R1", "R2"):
        state.waves[wave] = "completed"
        for cp in state.checkpoints[wave]:
            state.checkpoints[wave][cp] = True
    assert validate_state(state) == []


def test_wave02_missing_checkpoints_fails():
    state = _state(R0="completed", R1="completed")
    for cp in state.checkpoints["R0"]:
        state.checkpoints["R0"][cp] = True
    # R1 checkpoints not filled
    assert validate_state(state)


def test_wave03_started_before_previous_fails():
    state = _state(R3="active")
    assert validate_state(state)


def test_wave04_stop_the_line_blocks():
    state = _state(R0="completed", R1="active")
    for wave in ("R0",):
        for cp in state.checkpoints[wave]:
            state.checkpoints[wave][cp] = True
    state.stopped = ["v2_released_unsafe_candidate"]
    problems = validate_state(state)
    assert any("WAVE-04" in p for p in problems)


def test_wave05_override_on_non_overridable_fails():
    state = _state()
    state.overrides = [{"gate": "hash", "expires_at": "2099-01-01"}]
    assert validate_state(state)


def test_wave06_override_without_expiry_fails():
    state = _state()
    state.overrides = [{"gate": "test_count", "expires_at": ""}]
    assert validate_state(state)


def test_wave07_manual_flag_change_requires_release_id():
    assert validate_manual_flag_change({}, "v2_resolve_active=True")
    assert validate_manual_flag_change({}, "release-2026-08-09: v2 flag") == []


def test_wave08_next_allowed_wave():
    state = _state(R0="completed", R1="completed")
    for wave in ("R0", "R1"):
        for cp in state.checkpoints[wave]:
            state.checkpoints[wave][cp] = True
    assert next_allowed_wave(state) == "R2"
    state.waves["R2"] = "active"
    assert next_allowed_wave(state) is None  # one cohort at a time


def test_invalid_status_fails():
    state = _state(R0="banana")
    assert validate_state(state)
