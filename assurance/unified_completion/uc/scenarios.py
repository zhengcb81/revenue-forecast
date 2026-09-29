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
from pathlib import Path, PureWindowsPath
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


SATISFIED_STATUSES = ("passed", "expected_failure_pass")


def _evidence_problems(
    info: dict[str, Any], repo_root: Path,
) -> tuple[list[str], bool]:
    """Evidence-completeness problems for a cell whose status is satisfied.

    A satisfied status alone never proves completion (DEF-I00C-GATE-NEG):
    the cell must carry its evidence path, the declared required capability
    must actually be covered by that evidence, and a present oracle must not
    be empty — validated commands or invariants that are empty mean nothing
    was validated.

    A recorded fixture_hash is the SHA-256 of the evidence_path file. Closure
    re-reads those bytes; a plausible-looking digest is not evidence.
    Reporting does not modify the registry payload.
    """
    problems: list[str] = []
    evidence_path = info.get("evidence_path")
    if not isinstance(evidence_path, str) or not evidence_path.strip():
        problems.append("passed without evidence_path")
    fixture_hash = info.get("fixture_hash")
    hash_pending = bool(evidence_path and not fixture_hash)
    if hash_pending:
        problems.append("evidence_path without fixture_hash")
    elif evidence_path and (
        not isinstance(fixture_hash, str)
        or re.fullmatch(r"[0-9a-fA-F]{64}", fixture_hash) is None
    ):
        problems.append("fixture_hash is not a SHA-256 hex digest")
    if (
        isinstance(evidence_path, str)
        and evidence_path.strip()
        and isinstance(fixture_hash, str)
        and re.fullmatch(r"[0-9a-fA-F]{64}", fixture_hash)
    ):
        relative = Path(evidence_path.replace("\\", "/"))
        if (
            relative.is_absolute()
            or relative.drive
            or PureWindowsPath(evidence_path).drive
            or ".." in relative.parts
        ):
            problems.append("evidence_path is outside repo_root")
        else:
            try:
                root = repo_root.resolve(strict=True)
                evidence = (root / relative).resolve(strict=True)
                if not evidence.is_relative_to(root):
                    problems.append("evidence_path is outside repo_root")
                elif not evidence.is_file():
                    problems.append("evidence_path is not a file")
                elif sha256_file(evidence).lower() != fixture_hash.lower():
                    problems.append("evidence SHA-256 mismatch")
            except (OSError, RuntimeError):
                problems.append("evidence_path is missing or unreadable")
    required = info.get("required_capability")
    if required and required not in (info.get("covered_capabilities") or []):
        problems.append(
            f"required capability {required!r} not covered by evidence "
            f"(covered={info.get('covered_capabilities') or []})"
        )
    oracle = info.get("oracle")
    if isinstance(oracle, dict):
        commands = oracle.get("validated_commands")
        invariants = oracle.get("invariants")
        if commands is not None and not commands:
            problems.append("oracle validated_commands is empty")
        if invariants is not None and not invariants:
            problems.append("oracle invariants is empty")
    elif isinstance(oracle, str) and not oracle.strip():
        problems.append("oracle is empty")
    return problems, hash_pending


def closure_report(payload: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Machine summary: how many required cells are unsatisfied (closure red
    while any scenario status is pending/blocked, or a satisfied cell lacks
    supporting evidence, capability coverage, or a non-empty oracle)."""
    unsatisfied: list[str] = []
    pending_hash = 0
    for scenario_id, info in payload.get("scenarios", {}).items():
        if info.get("status") not in SATISFIED_STATUSES:
            unsatisfied.append(scenario_id)
            continue
        problems, hash_pending = _evidence_problems(info, repo_root)
        if hash_pending:
            pending_hash += 1
        if problems:
            unsatisfied.append(f"{scenario_id}: " + "; ".join(problems))
    return {
        "total_scenarios": payload.get("counts", {}).get("unique_total"),
        "unsatisfied": len(unsatisfied),
        "unsatisfied_ids": unsatisfied[:10],
        "closure_ready": not unsatisfied,
        # Historical key retained for existing callers; missing hash blocks.
        "evidence_hash_pending": pending_hash,
    }
