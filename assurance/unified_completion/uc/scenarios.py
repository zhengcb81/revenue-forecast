"""197-scenario machine result registry (CA-105).

Imports scenario IDs from the two frozen matrices (old 95 + new 102), records
per-scenario source, machine-extractable tier requirement, owner work unit,
and a result cell (status + evidence path + fixture/oracle hashes).  The
registry makes the required-result total machine-computable and lets closure
go red on any required cell that is not ``passed``/``expected_failure_pass``.

Rules (from the CA-105 card): markers are never pass; a scenario whose tier
cannot be extracted from the frozen table is recorded as
``matrix_defined`` (countable, but honest about extraction); any drift in the
frozen matrices is already caught by the plan manifest.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uc.casfile import cas_update, exclusive_publish, sha256_bytes, sha256_file

OLD_MATRIX = Path(
    "audit_review/2026-08-09_full_completion_assurance_plan/scenario_matrix.md"
)
NEW_MATRIX = Path(
    "audit_review/2026-08-13_zijin_data_lake_remediation_plan/scenario_matrix.md"
)

SCENARIO_RE = re.compile(
    r"\b(?:EX|DBX|DL|LT|AR|SAFE|CTRL|OPS|PORT|IDX|UJ|AUD|AUD2|MIG|"
    r"READ|BR|MINE|REV|ZJ|WU)-\d{2,3}\b"
)
TIER_RE = re.compile(r"^T\d(?:[/+ ]T\d)*$")


def _extract_ids(text: str) -> list[str]:
    return sorted(set(SCENARIO_RE.findall(text)))


def _extract_tiered(text: str) -> dict[str, str]:
    """Tier from table rows whose second column is a pure tier expression."""
    tiered: dict[str, str] = {}
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if SCENARIO_RE.fullmatch(cells[0]) and TIER_RE.fullmatch(cells[1]):
            tiered[cells[0]] = cells[1]
    return tiered


def build(repo_root: Path, output: Path, force_sha256: str | None = None) -> str:
    """Parse both frozen matrices into the registry; publish once/CAS-replace."""
    old_text = (repo_root / OLD_MATRIX).read_text(encoding="utf-8")
    new_text = (repo_root / NEW_MATRIX).read_text(encoding="utf-8")
    old_ids = _extract_ids(old_text)
    new_ids = _extract_ids(new_text)
    overlap = sorted(set(old_ids) & set(new_ids))
    if overlap:
        raise ValueError(
            f"scenario matrices overlap ({len(overlap)} ids): {overlap[:10]}…"
        )
    tiers = {**_extract_tiered(old_text), **_extract_tiered(new_text)}

    # Owner WU mapping is provenance-only: record the source, and leave owner
    # to the matrix prose (machine extraction of owner is CA-107's job).
    scenarios: dict[str, dict[str, Any]] = {}
    for scenario_id in sorted(set(old_ids) | set(new_ids)):
        source = "old95" if scenario_id in old_ids else "new102"
        scenarios[scenario_id] = {
            "source": source,
            "tier": tiers.get(scenario_id, "matrix_defined"),
            "status": "pending",
            "evidence_path": None,
            "fixture_hash": None,
            "oracle": None,
        }
    payload = {
        "schema_version": 1,
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "old95": sha256_file(repo_root / OLD_MATRIX),
            "new102": sha256_file(repo_root / NEW_MATRIX),
        },
        "counts": {
            "old95": len(old_ids),
            "new102": len(new_ids),
            "unique_total": len(scenarios),
        },
        "scenarios": scenarios,
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    if force_sha256 is not None:
        return cas_update(output, data, force_sha256)
    if not exclusive_publish(output, data):
        raise FileExistsError(
            f"scenario registry already exists at {output}; pass force_sha256 "
            "to CAS-replace"
        )
    return sha256_bytes(data)


def verify(repo_root: Path, registry_path: Path) -> list[str]:
    """Re-parse the frozen matrices and compare against the registry."""
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        return [f"unsupported schema {payload.get('schema_version')!r}"]
    problems: list[str] = []
    for name, path in (("old95", OLD_MATRIX), ("new102", NEW_MATRIX)):
        actual = sha256_file(repo_root / path)
        if actual != payload["sources"].get(name):
            problems.append(f"source drift: {name}")
    if problems:
        return problems
    old_ids = _extract_ids((repo_root / OLD_MATRIX).read_text(encoding="utf-8"))
    new_ids = _extract_ids((repo_root / NEW_MATRIX).read_text(encoding="utf-8"))
    if (
        len(old_ids) != payload["counts"]["old95"]
        or len(new_ids) != payload["counts"]["new102"]
    ):
        problems.append(
            f"scenario counts drifted: old {len(old_ids)} != "
            f"{payload['counts']['old95']} or new {len(new_ids)} != "
            f"{payload['counts']['new102']}"
        )
    registered = set(payload["scenarios"])
    expected = set(old_ids) | set(new_ids)
    if registered != expected:
        problems.append(
            f"registry scenario set differs: missing={sorted(expected - registered)[:5]} "
            f"extra={sorted(registered - expected)[:5]}"
        )
    return problems


def closure_report(payload: dict[str, Any]) -> dict[str, Any]:
    """Machine summary: how many required cells are unsatisfied (closure red
    while any scenario status is pending/blocked)."""
    unsatisfied = [
        scenario_id
        for scenario_id, info in payload.get("scenarios", {}).items()
        if info.get("status") not in ("passed", "expected_failure_pass")
    ]
    return {
        "total_scenarios": payload.get("counts", {}).get("unique_total"),
        "unsatisfied": len(unsatisfied),
        "unsatisfied_ids": unsatisfied[:10],
        "closure_ready": not unsatisfied,
    }
