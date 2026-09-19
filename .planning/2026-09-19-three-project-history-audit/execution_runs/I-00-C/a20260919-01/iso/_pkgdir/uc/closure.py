"""Three-repo Closure 2.0 (CA-107).

Scans every receipt directory in all three repos, classifies each unit's
evidence (machine_valid / legacy / incomplete with precise problems), and
aggregates an honest closure report that declares the old plan incomplete
with a COMPLETE reason set — never a bare "five items remaining".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from uc.receipt import validate as receipt_validate
from uc.revision import select as revision_select
from uc.scenarios import scenario_gate

RECEIPT_DIRS: dict[str, list[Path]] = {
    "revenue": [
        Path("assurance/unified_completion/receipts"),
        Path("assurance/fc"),
    ],
    "filing": [Path("assurance/fc")],
    "wiki": [Path("assurance/fc")],
}


def scan_receipt_dirs(
    repo_roots: dict[str, Path],
) -> dict[str, list[dict[str, Any]]]:
    """Return per-repo unit-directory listings with receipt filenames."""
    found: dict[str, list[dict[str, Any]]] = {}
    for repo_name, dirs in RECEIPT_DIRS.items():
        root = repo_roots[repo_name]
        units: list[dict[str, Any]] = []
        for rel in dirs:
            base = root / rel
            if not base.is_dir():
                continue
            for unit_dir in sorted(base.iterdir()):
                if not unit_dir.is_dir():
                    continue
                units.append(
                    {
                        "unit_dir": str(unit_dir.relative_to(root)),
                        "receipts": sorted(p.name for p in unit_dir.glob("*.json")),
                    }
                )
        found[repo_name] = units
    return found


def classify_unit(
    repo_root: Path,
    unit_dir_rel: str,
    repo_roots: dict[str, Path] | None = None,
) -> dict[str, Any]:
    """Classify one unit directory's evidence.  ``repo_roots=None`` skips the
    git-object triplet check (fixture use)."""
    unit_dir = repo_root / unit_dir_rel
    problems: list[str] = []
    receipts = sorted(unit_dir.glob("*.json")) if unit_dir.is_dir() else []
    has_new_schema = False
    for receipt_path in receipts:
        try:
            payload = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{receipt_path.name}: unreadable ({exc})")
            continue
        if payload.get("schema_version") == 1:
            has_new_schema = True
            problems.extend(receipt_validate(receipt_path, repo_roots))
    selection: dict[str, Any] = {}
    if has_new_schema:
        selection, pair_problems = revision_select(unit_dir)
        problems.extend(pair_problems)
        status = "machine_valid" if not problems else "incomplete"
    else:
        # No schema-v1 receipts: grandfathered legacy history, not a defect
        # of the current evidence system (migration is CA-304 scope).
        status = "legacy" if not problems else "incomplete"
    return {
        "unit": unit_dir_rel.replace("\\", "/").split("/")[-1],
        "status": status,
        "has_new_schema": has_new_schema,
        "problems": problems,
        "selection": selection,
    }


def closure_report(
    repo_roots: dict[str, Path],
    legacy_artifact: Path,
    scenario_registry: Path,
) -> dict[str, Any]:
    """The honest three-repo closure report."""
    scan = scan_receipt_dirs(repo_roots)
    units: list[dict[str, Any]] = []
    for repo_name, listings in scan.items():
        root = repo_roots[repo_name]
        for listing in listings:
            units.append(classify_unit(root, listing["unit_dir"], repo_roots))
    legacy = json.loads(legacy_artifact.read_text(encoding="utf-8"))
    scenarios = json.loads(scenario_registry.read_text(encoding="utf-8"))
    unsatisfied_scenarios = [
        sid
        for sid, info in scenarios.get("scenarios", {}).items()
        if scenario_gate(sid, info)
    ]

    # Eighteen-vintage narrowing guard: a successor entry can only retire a
    # pending original obligation when it links back to the original id.
    # A "narrowed successor" recorded without that linkage never clears
    # the original (CA-206/301/302 form).
    pending_originals: list[str] = []
    narrowed_only: list[str] = []
    for row in legacy.get("fc_entries", []):
        cls = row.get("class")
        fc_id = str(row.get("fc_id", ""))
        if cls != "P":
            continue
        target = row.get("obligation_target")
        linked = row.get("covered_by") or row.get("successor")
        if target and target != fc_id and not linked:
            narrowed_only.append(fc_id)
        pending_originals.append(fc_id)
    fc_pending = pending_originals
    fc_contradicted = len(
        [row for row in legacy.get("fc_entries", []) if row["class"] == "C"]
    )
    reasons = [
        f"{fc_contradicted} legacy FCs contradicted by current behavior",
        f"{len(fc_pending)} legacy closure items pending ({fc_pending})",
        f"{len(unsatisfied_scenarios)} of "
        f"{scenarios['counts']['unique_total']} mandatory scenarios unsatisfied",
        "R9 legacy removal frozen (4/4 RED at audit; deletion belongs to CA-304)",
        "legacy receipt sets remain outside the machine schema (grandfathered "
        "history; migration is CA-107+CA-304 scope)",
    ]
    machine_invalid = [unit["unit"] for unit in units if unit["status"] == "incomplete"]
    if machine_invalid:
        reasons.append(
            f"{len(machine_invalid)} unit(s) with incomplete machine evidence: "
            f"{machine_invalid}"
        )
    if narrowed_only:
        reasons.append(
            f"{len(narrowed_only)} original obligation(s) carried only by a "
            f"narrowed successor without linkage: {narrowed_only}"
        )
    return {
        "schema_version": 1,
        "old_plan_verdict": "incomplete"
        if (unsatisfied_scenarios or fc_pending or machine_invalid)
        else "complete_scoped",
        "reasons": reasons,
        "units": units,
        "unit_summary": {
            status: sum(1 for unit in units if unit["status"] == status)
            for status in ("machine_valid", "legacy", "incomplete")
        },
        "scenario_summary": {
            "total": scenarios["counts"]["unique_total"],
            "unsatisfied": len(unsatisfied_scenarios),
        },
        "legacy_summary": {
            "fc_total": len(legacy["fc_entries"]),
            "contradicted": fc_contradicted,
            "pending": len(fc_pending),
        },
    }
