"""Legacy disposition registry (CA-004): machine-freeze the audit's per-item
classification of the old plan's 71 FCs, 10 rollout waves and 5 closure items
into a validated registry with exact successor mapping.

Sources (all frozen inputs, hash-verified by the plan manifest):

- ``legacy_fc_status_registry.md``  — 71 FC rows: I/C/S/P class + reason + successors
- ``legacy_transition_matrix.md``   — R0~R9 waves + pain-point mapping
- ``completion_audit.md``           — per-Phase dispositions

Machine acceptance (from the frozen registry): exactly 71 unique FC rows;
class counts I=31 / C=26 / S=9 / P=5; every row has at least one successor;
every successor id is defined in the CA/ZR registries; the merged graph
(FC->successor + CA/ZR dependencies) is acyclic.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uc.casfile import cas_update, exclusive_publish, sha256_bytes, sha256_file
from uc.dag import _expand_dep_cell, load_dag

FC_REGISTRY = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/"
    "legacy_fc_status_registry.md"
)
TRANSITION_MATRIX = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/"
    "legacy_transition_matrix.md"
)
COMPLETION_AUDIT = Path(
    "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/completion_audit.md"
)

FC_ROW_RE = re.compile(r"^\|\s*(FC-\d{3,4})\s*\|")
WAVE_ROW_RE = re.compile(r"^\|\s*(R\d)\s*\|")
CLASS_NAMES = {
    "I": "implemented_not_independently_verified",
    "C": "contradicted_by_current_behavior",
    "S": "stale_evidence",
    "P": "pending",
}
EXPECTED_COUNTS = {"I": 31, "C": 26, "S": 9, "P": 5}
EXPECTED_FC_ROWS = 71
EXPECTED_WAVES = 10


class LegacyValidationError(Exception):
    """The frozen legacy tables violate their own machine acceptance."""


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _successors(cell: str) -> list[str]:
    normalized = cell.replace("～", "~")
    return sorted(_expand_dep_cell(normalized))


def parse_fc_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = FC_ROW_RE.match(line)
        if not match:
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        rows.append(
            {
                "fc_id": match.group(1),
                "old_status": cells[1],
                "class": cells[2],
                "class_name": CLASS_NAMES.get(cells[2], f"unknown:{cells[2]}"),
                "reason": cells[3],
                "successors": _successors(cells[4]),
            }
        )
    return rows


def parse_waves(text: str) -> list[dict[str, Any]]:
    """Wave rows: the successor cell is series shorthand (e.g. ``CA-001～109``
    spans gaps where CA-005..CA-100 do not exist).  Keep the raw cell and the
    range-expanded candidates; validation filters candidates to defined ids."""
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = WAVE_ROW_RE.match(line)
        if not match:
            continue
        cells = _cells(line)
        if len(cells) < 4:
            continue
        rows.append(
            {
                "wave": match.group(1),
                "class": cells[1],
                "class_name": CLASS_NAMES.get(cells[1], f"unknown:{cells[1]}"),
                "successors_raw": cells[3],
                "successors": _successors(cells[3]),
            }
        )
    return rows


def _defined_successors(expanded: list[str], known_units: set[str]) -> list[str]:
    return [s for s in expanded if s in known_units]


def validate(
    fc_rows: list[dict[str, Any]],
    waves: list[dict[str, Any]],
    known_units: set[str],
) -> list[str]:
    """Return validation problems (empty = valid)."""
    problems: list[str] = []
    ids = [row["fc_id"] for row in fc_rows]
    if len(ids) != EXPECTED_FC_ROWS:
        problems.append(f"FC rows: {len(ids)} != {EXPECTED_FC_ROWS}")
    if len(set(ids)) != len(ids):
        problems.append("FC ids are not unique")
    counts = {cls: 0 for cls in CLASS_NAMES}
    for row in fc_rows:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
    for cls, expected in EXPECTED_COUNTS.items():
        if counts.get(cls) != expected:
            problems.append(f"class {cls}: {counts.get(cls)} != expected {expected}")
    for row in fc_rows:
        if not row["successors"]:
            problems.append(f"{row['fc_id']}: no successor")
        unknown = [s for s in row["successors"] if s not in known_units]
        if unknown:
            problems.append(f"{row['fc_id']}: unknown successors {unknown}")
    if len(waves) != EXPECTED_WAVES:
        problems.append(f"waves: {len(waves)} != {EXPECTED_WAVES}")
    wave_names = [w["wave"] for w in waves]
    if sorted(wave_names) != [f"R{i}" for i in range(EXPECTED_WAVES)]:
        problems.append(f"waves incomplete: {sorted(wave_names)}")
    for wave in waves:
        defined = _defined_successors(wave["successors"], known_units)
        if not defined:
            problems.append(
                f"{wave['wave']}: no defined successor in "
                f"{wave.get('successors_raw')!r}"
            )
    # Acyclicity over the merged graph (FC -> successor, CA/ZR -> deps).
    return problems


def _cycle_check(
    fc_rows: list[dict[str, Any]], unit_deps: dict[str, list[str]]
) -> list[str]:
    graph: dict[str, list[str]] = {unit: list(deps) for unit, deps in unit_deps.items()}
    for row in fc_rows:
        graph.setdefault(row["fc_id"], [])
        for successor in row["successors"]:
            graph[row["fc_id"]].append(successor)
    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> list[str]:
        state[node] = 1
        cycle: list[str] = []
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                cycle = stack[stack.index(nxt) :] + [nxt]
                return cycle
            if state.get(nxt) == 0:
                found = visit(nxt, stack + [nxt])
                if found:
                    return found
        state[node] = 2
        return []

    for node in graph:
        state.setdefault(node, 0)
    for node in graph:
        if state[node] == 0:
            cycle = visit(node, [node])
            if cycle:
                return [f"cycle: {' -> '.join(cycle)}"]
    return []


def build(repo_root: Path, output: Path, force_sha256: str | None = None) -> str:
    """Parse + validate the frozen legacy tables; publish the machine registry."""
    fc_text = (repo_root / FC_REGISTRY).read_text(encoding="utf-8")
    wave_text = (repo_root / TRANSITION_MATRIX).read_text(encoding="utf-8")

    fc_rows = parse_fc_rows(fc_text)
    waves = parse_waves(wave_text)
    unit_deps = load_dag(repo_root)
    known_units = set(unit_deps)
    problems = validate(fc_rows, waves, known_units)
    problems.extend(_cycle_check(fc_rows, unit_deps))
    if problems:
        raise LegacyValidationError("; ".join(problems))

    counts = {cls: 0 for cls in CLASS_NAMES}
    for row in fc_rows:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
    payload = {
        "schema_version": 1,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "legacy_fc_status_registry.md": sha256_file(repo_root / FC_REGISTRY),
            "legacy_transition_matrix.md": sha256_file(repo_root / TRANSITION_MATRIX),
            "completion_audit.md": sha256_file(repo_root / COMPLETION_AUDIT),
        },
        "counts": counts,
        "fc_entries": fc_rows,
        "waves": waves,
        "closure_items": [r for r in fc_rows if r["fc_id"].startswith("FC-150")],
        "known_units": sorted(known_units),
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if force_sha256 is not None:
        return cas_update(output, data, force_sha256)
    if not exclusive_publish(output, data):
        raise FileExistsError(
            f"legacy disposition already exists at {output}; pass force_sha256 to CAS-replace"
        )
    return sha256_bytes(data)


def verify(repo_root: Path, artifact_path: Path) -> list[str]:
    """Re-parse the frozen sources, re-validate, and compare against the
    published artifact.  Returns drift/problems (empty = fresh)."""
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"unsupported schema {payload.get('schema_version')!r}")
    problems: list[str] = []
    for name, path in (
        ("legacy_fc_status_registry.md", FC_REGISTRY),
        ("legacy_transition_matrix.md", TRANSITION_MATRIX),
        ("completion_audit.md", COMPLETION_AUDIT),
    ):
        actual = sha256_file(repo_root / path)
        if actual != payload["sources"].get(name):
            problems.append(f"source drift: {name}")
    if problems:
        return problems
    fc_rows = parse_fc_rows((repo_root / FC_REGISTRY).read_text(encoding="utf-8"))
    waves = parse_waves((repo_root / TRANSITION_MATRIX).read_text(encoding="utf-8"))
    unit_deps = load_dag(repo_root)
    problems.extend(validate(fc_rows, waves, set(unit_deps)))
    problems.extend(_cycle_check(fc_rows, unit_deps))
    if fc_rows != payload.get("fc_entries") or waves != payload.get("waves"):
        problems.append("artifact entries differ from re-parsed frozen sources")
    return problems
