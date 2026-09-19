"""Minimal machine state (bootstrap v1) for the unified completion area.

`audit_review/README.md` §12: after CA-001 the machine state at
``assurance/unified_completion/state.json`` is the source of truth; the
README control fields (§0) only mirror it.  This module writes/reads that
state with CAS discipline.  The strict state machine and receipt schema are
versioned later by CA-101/CA-102 (N/N-1 policy); v1 is intentionally small.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from uc.casfile import cas_update, exclusive_publish, sha256_file, sha256_bytes

SCHEMA_VERSION = 1


class StateExistsError(Exception):
    """Bootstrap refused: state.json already exists (no silent overwrite)."""


def read_state(state_path: Path) -> dict[str, Any] | None:
    """Current state or None when it does not exist yet."""
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def bootstrap_state(
    state_path: Path,
    plan_id: str,
    base_triplet: dict[str, str],
    control_page: str,
    control_page_sha256: str,
    manifest_path: str,
    manifest_sha256: str,
    current_phase: str,
    current_next: str,
) -> str:
    """Create the machine state exactly once.  Returns its content hash."""
    now = datetime.now(timezone.utc)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": plan_id,
        "machine_state_authority": True,
        "control_page": control_page,
        "control_page_sha256": control_page_sha256,
        "machine_manifest": manifest_path,
        "machine_manifest_sha256": manifest_sha256,
        "base_triplet": dict(sorted(base_triplet.items())),
        "plan_status": "ready_for_implementation",
        "implementation_status": "in_progress",
        "current_phase": current_phase,
        "current_next": current_next,
        "active_owner": None,
        "lease": None,
        "blocked_reason": None,
        "last_control_update": now.strftime("%Y-%m-%d"),
        "updated_at_utc": now.isoformat(),
        "units": {},
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if not exclusive_publish(state_path, data):
        raise StateExistsError(f"machine state already exists: {state_path}")
    return sha256_bytes(data)


def update_state(
    state_path: Path,
    transform_state: Callable[[dict[str, Any]], dict[str, Any]],
) -> tuple[str, str]:
    """CAS read-modify-write of the machine state.

    ``transform_state`` receives the parsed dict and returns the new dict.
    Returns ``(expected_hash_used, new_hash)``.  Raises CASConflict when
    another writer changed the state in between; callers re-read and retry.
    """
    current = read_state(state_path)
    if current is None:
        raise FileNotFoundError(f"machine state missing: {state_path}")
    expected = sha256_file(state_path)
    new_state = transform_state(dict(current))
    new_state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    data = json.dumps(new_state, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    new_hash = cas_update(state_path, data, expected)
    return expected, new_hash
