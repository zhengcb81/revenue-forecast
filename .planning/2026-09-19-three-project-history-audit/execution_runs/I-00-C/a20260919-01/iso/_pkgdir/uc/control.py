"""Control-page (README §0) CAS patching and the closure-advance step.

`audit_review/README.md` §0 is the human-readable execution cursor.  Machine
state is authoritative after CA-001; the control fields on the page are a
mirror updated only through this module, under the control-page lock, with a
CAS hash check — never by free-form editing.
"""

from __future__ import annotations

import re
from typing import Callable

README_SECTION0_FIELDS = (
    "plan_id",
    "authority",
    "plan_status",
    "implementation_status",
    "current_phase",
    "current_next",
    "active_owner",
    "lease",
    "blocked_reason",
    "last_control_update",
)
_FIELD_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[a-z_]+):(?P<rest>.*)$")

ReadmeTransform = Callable[[str], str]


def patch_section0(text: str, fields: dict[str, str]) -> str:
    """Replace the §0 yaml field values listed in ``fields``.

    Only lines inside the first ```yaml block whose keys match
    README_SECTION0_FIELDS are touched; every other line is left byte-identical.
    Raises ValueError for unknown keys or a missing yaml block.
    """
    unknown = sorted(set(fields) - set(README_SECTION0_FIELDS))
    if unknown:
        raise ValueError(f"unknown README §0 fields: {unknown}")
    lines = text.splitlines(keepends=True)
    in_yaml = False
    replaced: set[str] = set()
    out: list[str] = []
    for line in lines:
        if line.strip() == "```yaml":
            in_yaml = not in_yaml
            out.append(line)
            continue
        if in_yaml:
            match = _FIELD_RE.match(line)
            if match and match.group("key") in fields:
                indent, key, rest = (
                    match.group("indent"),
                    match.group("key"),
                    match.group("rest"),
                )
                value = fields[key]
                rest = rest.strip()
                out.append(f"{indent}{key}: {value}\n")
                replaced.add(key)
                continue
        out.append(line)
    if not replaced:
        raise ValueError("README §0 yaml block not found or no field matched")
    missing = set(fields) - replaced
    if missing:
        raise ValueError(f"README §0 fields not found in yaml block: {sorted(missing)}")
    return "".join(out)


def plan_release_fields(now_iso: str) -> dict[str, str]:
    """§0 fields written when a unit is released/blocked (lease cleared)."""
    return {
        "active_owner": "unassigned",
        "lease": "none",
        "last_control_update": now_iso[:10],
    }


def plan_advance_fields(
    *, current_next: str, current_phase: str, now_iso: str
) -> dict[str, str]:
    """§0 fields written when the machine DAG advances ``current_next``."""
    return {
        "implementation_status": "in_progress",
        "current_phase": current_phase,
        "current_next": current_next,
        "active_owner": "unassigned",
        "lease": "none",
        "last_control_update": now_iso[:10],
    }
