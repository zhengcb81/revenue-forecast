"""WU-1406: strangler-wave controller — machine-readable release state.

R0..R11 waves with non-exchangeable order; CP0..CP8 per-slice checkpoints;
stop-the-line conditions block the next wave.  Manual flag changes without
a release/incident ID fail.  Overrides require explicit user authorization,
double review, a reason and an expiry — never on hash/path/external-write/
integrity gates.

WAVE-01..08 test vectors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

R_WAVES = (
    "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10", "R11",
)
WAVE_ORDER = {wave: index for index, wave in enumerate(R_WAVES)}

# wave -> required upstream waves (all must be completed)
WAVE_REQUIRES = {
    "R1": ("R0",),
    "R2": ("R1",),
    "R3": ("R2",),
    "R4": ("R3",),
    "R5": ("R4",),
    "R6": ("R5",),
    "R7": ("R6",),
    "R8": ("R7",),
    "R9": ("R8",),
    "R10": ("R9",),
    "R11": ("R10",),
}

CP0_CP8 = tuple(f"CP{i}" for i in range(9))

# stop-the-line conditions (each is a predicate name; a trigger blocks)
STOP_CONDITIONS = (
    "unclassified_selected_diff",
    "v2_released_unsafe_candidate",
    "v2_missing_verified_candidate",
    "external_write_detected",
    "unauthorized_network_download",
    "catalog_integrity_failed",
    "real_root_mutation",
    "test_count_decreased",
    "targeted_mutation_survived",
    "rollback_drill_failed",
    "user_dirty_file_touched",
)

# gates that can NEVER be overridden
NON_OVERRIDABLE = {"hash", "path", "external_write", "integrity"}


@dataclass
class ReleaseState:
    waves: dict[str, str] = field(default_factory=dict)  # wave -> status
    checkpoints: dict[str, dict[str, bool]] = field(default_factory=dict)
    stopped: list[str] = field(default_factory=list)
    overrides: list[dict] = field(default_factory=list)

    @classmethod
    def fresh(cls) -> "ReleaseState":
        return cls(
            waves={wave: "not_started" for wave in R_WAVES},
            checkpoints={wave: {cp: False for cp in CP0_CP8} for wave in R_WAVES},
        )


def validate_state(state: ReleaseState) -> list[str]:
    """WAVE-01..08: reject skipped waves, missing receipts, stopped lines."""
    problems: list[str] = []
    for wave, status in state.waves.items():
        if status not in {"not_started", "active", "completed"}:
            problems.append(f"{wave}: invalid status {status!r}")
            continue
        if status == "completed":
            required = WAVE_REQUIRES.get(wave, ())
            for upstream in required:
                if state.waves.get(upstream) != "completed":
                    problems.append(
                        f"WAVE-01: {wave} completed but upstream {upstream} "
                        f"is {state.waves.get(upstream)}"
                    )
            missing_cp = [
                cp for cp in CP0_CP8
                if not state.checkpoints.get(wave, {}).get(cp)
            ]
            if missing_cp:
                problems.append(
                    f"WAVE-02: {wave} completed but missing checkpoints "
                    f"{missing_cp}"
                )
        if wave != "R0" and status in {"active", "completed"}:
            prev = R_WAVES[WAVE_ORDER[wave] - 1]
            if state.waves.get(prev) not in {"active", "completed"}:
                problems.append(
                    f"WAVE-03: {wave} started before {prev} reached active"
                )
    # stop-the-line blocks the next wave
    if state.stopped:
        next_wave = None
        for wave in R_WAVES:
            if state.waves.get(wave) == "active":
                next_wave = wave
                break
        if next_wave:
            problems.append(
                f"WAVE-04: stop-the-line triggered ({state.stopped}) while "
                f"{next_wave} active — next wave blocked"
            )
    # overrides must never touch non-overridable gates
    for override in state.overrides:
        if override.get("gate") in NON_OVERRIDABLE:
            problems.append(
                f"WAVE-05: override touches non-overridable gate "
                f"{override.get('gate')}"
            )
        if not override.get("expires_at"):
            problems.append(f"WAVE-06: override without expiry: {override}")
    return problems


def validate_manual_flag_change(flags: dict, change: str) -> list[str]:
    """A manual flag change without a release/incident ID fails (WAVE-07)."""
    if not change or not change.startswith("release-") and \
            not change.startswith("incident-"):
        return ["WAVE-07: manual flag change without release/incident ID"]
    return []


def next_allowed_wave(state: ReleaseState) -> str | None:
    """The next wave that may transition to active (WAVE-08)."""
    for wave in R_WAVES:
        if state.waves.get(wave) == "active":
            return None  # one cohort at a time
    for wave in R_WAVES:
        if state.waves.get(wave) == "not_started":
            required = WAVE_REQUIRES.get(wave, ())
            if all(state.waves.get(r) == "completed" for r in required):
                return wave
    return None
