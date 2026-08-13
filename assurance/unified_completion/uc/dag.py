"""Dependency DAG over CA/ZR work units, parsed from the frozen registries.

Two formats exist in the frozen specs and both are parsed here:

- CA registry: ``### CA-NNN：title`` headings with ``- 依赖：…`` lines;
- ZR registry: table rows ``| ZR-NNN | owner | deps | goal | evidence |``
  where the deps cell may be ``无``, a comma list, or a ``ZR-A~B`` range.

CA-001 scope: derive the *unlock set* without a second source of truth.
The full strict state machine is CA-101's job.
"""

from __future__ import annotations

import re
from pathlib import Path

UNIT_RE = re.compile(r"\b(?:CA|ZR)-\d{3,4}\b")
RANGE_RE = re.compile(r"^(?P<kind>CA|ZR)-(?P<start>\d{3,4})~(?P<end>\d{3,4})$")
HEADING_RE = re.compile(r"^#{2,4}\s+(CA-\d{3})\b")
DEP_LINE_RE = re.compile(r"^\s*[-*]\s*依赖[:：]\s*(.+)$")
ZR_ROW_RE = re.compile(r"^\|\s*(ZR-\d{3,4})\s*\|")

# Freeze the registry file locations (verified by the manifest as frozen inputs).
CA_REGISTRY = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/"
    "completion_assurance_registry.md"
)
ZR_REGISTRY = Path(
    "audit_review/2026-08-13_zijin_data_lake_remediation_plan/work_unit_registry.md"
)


def _expand_dep_cell(cell: str) -> list[str]:
    """Expand a dependency cell: ``无``/empty -> [], comma lists and ``A~B``
    ranges -> explicit unit ids, in numeric order."""
    cell = cell.strip()
    if not cell or cell == "无":
        return []
    tokens = [token.strip() for token in re.split(r"[,，、]", cell) if token.strip()]
    units: list[str] = []
    for token in tokens:
        token = token.strip("`")
        range_match = RANGE_RE.match(token)
        if range_match:
            kind, start, end = (
                range_match.group("kind"),
                int(range_match.group("start")),
                int(range_match.group("end")),
            )
            if start > end or end - start > 200:
                raise ValueError(f"invalid dependency range: {token}")
            width = len(range_match.group("start"))
            units.extend(f"{kind}-{n:0{width}d}" for n in range(start, end + 1))
        elif UNIT_RE.fullmatch(token):
            units.append(token)
        else:
            # Non-unit prose (e.g. "全部mandatory ZR/CA功能单元") keeps only the
            # concrete unit ids it contains; anything else is dropped explicitly.
            units.extend(UNIT_RE.findall(token))
    return sorted(set(units))


def parse_deps(registry_text: str, unit_kind: str = "CA") -> dict[str, list[str]]:
    """Parse dependency edges for ``unit_kind`` registries (CA headings or ZR
    table rows)."""
    deps: dict[str, list[str]] = {}
    if unit_kind == "CA":
        current: str | None = None
        for line in registry_text.splitlines():
            heading = HEADING_RE.match(line)
            if heading:
                current = heading.group(1)
                deps.setdefault(current, [])
                continue
            if current is None:
                continue
            match = DEP_LINE_RE.match(line)
            if match:
                deps[current] = _expand_dep_cell(match.group(1))
    else:
        for line in registry_text.splitlines():
            row = ZR_ROW_RE.match(line)
            if not row:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            deps[row.group(1)] = _expand_dep_cell(cells[2])
    return deps


def load_dag(repo_root: Path) -> dict[str, list[str]]:
    """Parse CA + ZR registries and merge their dependency edges."""
    ca_text = (repo_root / CA_REGISTRY).read_text(encoding="utf-8")
    zr_text = (repo_root / ZR_REGISTRY).read_text(encoding="utf-8")
    merged = parse_deps(ca_text, unit_kind="CA")
    for unit, unit_deps in parse_deps(zr_text, unit_kind="ZR").items():
        merged.setdefault(unit, [])
        merged[unit] = sorted(set(merged[unit]) | set(unit_deps))
    return merged


def next_units(state: dict, dag: dict[str, list[str]]) -> list[str]:
    """Units that are not yet accepted AND whose every dependency is accepted.

    ``state["units"][unit]["status"] in {"accepted", "already_satisfied"}``
    counts as satisfied.  Returns the full unlock set; the single-writer rule
    (README §6) means the caller must proceed with at most one at a time.
    """
    units = state.get("units", {})
    accepted = {
        unit
        for unit, info in units.items()
        if isinstance(info, dict)
        and info.get("status") in {"accepted", "already_satisfied"}
    }
    unlocked: list[str] = []
    for unit, unit_deps in sorted(dag.items()):
        if unit in accepted:
            continue
        if unit in units and units[unit].get("status") == "in_progress":
            continue
        if all(dep in accepted for dep in unit_deps):
            unlocked.append(unit)
    return unlocked
