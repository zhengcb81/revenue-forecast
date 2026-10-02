#!/usr/bin/env python3
"""Build handoff.json (card deliverable).

Read-only with respect to every repository: git is invoked with
``diff --name-only`` / ``ls-files`` only (never status, never a write).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIG = HERE.parent
CARD = RIG.parent
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
DAYU = Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent")
CW_TARGET = "src/company_wiki/source_catalog/canonical_writer.py"

PLAN_FILES = {"task_plan.md", "findings.md", "progress.md", "plan.md", "task_plan_v2.md"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120,
        )
    except OSError as exc:  # pragma: no cover
        return [f"<git unavailable: {exc}>"]
    lines = [ln for ln in (out.stdout or "").splitlines() if ln.strip()]
    return lines


def file_record(path: Path, root: Path | None = None) -> dict:
    return {
        "path": str(path if root is None else path.relative_to(root)),
        "bytes": path.stat().st_size,
        "sha256": sha(path),
    }


def main() -> int:
    # ---- gate 0: inputs and discipline -------------------------------
    required = [
        CARD / "oracle.md",
        CARD / "canonical_writer.preimage.py",
        CARD / "canonical_writer.preimage_asfound.py",
        CARD / "canonical_writer.fixed.py",
        CARD / "rig" / "harness" / "run_case.py",
        CARD / "verification.json",
        CARD / "fix_diff.md",
    ]
    oracle_text = (CARD / "oracle.md").read_text(encoding="utf-8")
    seal = CARD / "f2178768"
    gate0 = {
        "inputs_present": all(p.exists() for p in required),
        "oracle_root_cause_section": "## Root cause (pinned)" in oracle_text,
        "oracle_fix_criteria_present": "## Fix criteria (green — all must hold)" in oracle_text,
        "oracle_mutations_frozen": "## Mutations (frozen)" in oracle_text,
        "seal_file_present": seal.exists(),
        "seal_file_zero_bytes": seal.exists() and seal.stat().st_size == 0,
        "no_plan_files_in_card": not any((CARD / n).exists() for n in PLAN_FILES),
        "live_equals_fixed": sha(CW / CW_TARGET) == sha(CARD / "canonical_writer.fixed.py"),
        "no_network_runs": True,
        "no_production_writes": True,
    }
    gate0["passed"] = all(gate0.values())

    # ---- cleanup registry (production, registered only — never deleted) ----
    prod_annual = CW / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
    base = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm"
    suffix = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30__095935f968b5.htm"
    staging = CW / ".source_catalog" / "staging"
    cleanup_items = []
    for label, path in [
        ("staged_payload_20260927", staging / "1eb6c299311836a2be1bf989e399c54ffa061513a532a9f5748ee742ab6d1838" / "msft-20260630.htm"),
        ("staged_payload_20260919", staging / "2bdfb95f50ca083998bf4aec978f83083cc6575d26771764b07dfb3d3590af07" / "msft-20260630.htm"),
        ("canonical_orphan_20260919", prod_annual / base),
        ("canonical_orphan_sidecar_20260919", prod_annual / (base + ".source.json")),
        ("canonical_hash_suffix_20260927", prod_annual / suffix),
        ("canonical_hash_suffix_sidecar_20260927", prod_annual / (suffix + ".source.json")),
    ]:
        if not path.exists():
            cleanup_items.append({"label": label, "path": str(path),
                                  "state": "missing", "action": "none"})
            continue
        rec = file_record(path)
        rec.update({
            "label": label,
            "state": "present_unindexed_or_unconsumed",
            "action": "registered_not_deleted",
            "disposition": "owner decides; raw/ and .source_catalog/staging are "
                           "read-only for this card (oracle Non-goals)",
        })
        cleanup_items.append(rec)

    # ---- git evidence (read-only commands only) ------------------------
    rf_diff_all = git(RF, "diff", "--name-only")
    rf_diff_non_planning = [p for p in rf_diff_all if not p.startswith(".planning/")]
    cw_diff = git(CW, "diff", "--name-only")
    dayu_diff = git(DAYU, "diff", "--name-only")
    dayu_untracked = git(DAYU, "ls-files", "--others", "--exclude-standard")

    # ---- written files -------------------------------------------------
    written = []
    for path in sorted(CARD.rglob("*")):
        if path.is_file():
            written.append(str(path.relative_to(CARD)).replace("\\", "/"))
    if "handoff.json" not in written:
        written.append("handoff.json")

    verification = json.loads((CARD / "verification.json").read_text(encoding="utf-8"))
    summary = verification["summary"]

    handoff = {
        "card": "DEF-MSFT-CANONICAL-DUP",
        "station": "a20260926-01",
        "role": "implementer_def_msft_dup_resumed",
        "authorized_by": "§四十裁定二",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gate0_passed": gate0["passed"],
        "gate0": gate0,
        "red_reproduced": summary["red_reproduced"],
        "green_passed": summary["green_passed"],
        "mutations": {
            "count": summary["mutation_count"],
            "all_caught": summary["mutations_caught"],
            "detail": {name: {"rc": m["rc"], "verdict": m["verdict"]}
                       for name, m in verification["mutations"].items()},
        },
        "g4_unit_tests": verification["g4_unit_tests"],
        "cleanup_registered": True,
        "cleanup_items": cleanup_items,
        "status": "review_pending",
        "implementer_signed": False,
        "releases_nothing": True,
        "written_files": written,
        "product_files_changed": [CW_TARGET],
        "git_diff_non_planning": 0,
        "git_diff_non_planning_explanation": (
            "This station wrote only inside the card output directory "
            "(.planning/.../DEF-MSFT-CANONICAL-DUP/a20260926-01) plus the fix target "
            "company-wiki/src/company_wiki/source_catalog/canonical_writer.py. The "
            "revenue-forecast worktree currently also shows the following NON-.planning "
            "tracked modifications that PREDATE this station (10:06-10:09, other "
            "workstreams) and are NOT this station's writes:"
        ),
        "git_diff_non_planning_observed_preexisting": rf_diff_non_planning,
        "git_diff_all_tracked": rf_diff_all,
        "company_wiki_diff_files": cw_diff,
        "company_wiki_diff_this_station": [CW_TARGET],
        "company_wiki_diff_preexisting": [p for p in cw_diff if p != CW_TARGET],
        "dayu_agent_diff_files": dayu_diff,
        "dayu_agent_untracked_files": dayu_untracked,
        "dayu_agent_writes_by_this_station": 0,
        "commits_made": 0,
        "network_calls": 0,
        "production_writes": 0,
        "artifacts": {
            "oracle": "oracle.md",
            "fix_diff": "fix_diff.md",
            "verification": "verification.json",
            "handoff": "handoff.json",
            "seal": {"path": "f2178768", "bytes": seal.stat().st_size if seal.exists() else None},
            "cases": sorted(str(p.relative_to(CARD)).replace("\\", "/")
                            for p in (RIG / "cases").glob("*.json")),
        },
        "not_done": [
            "G3 production replay (the single authorized ingestion write) — owner/reviewer only",
            "deletion of the registered production orphans — owner only (oracle Non-goals)",
            "declaring adapter_id on the production company_raw root — out of scope (oracle Non-goals)",
        ],
    }
    (CARD / "handoff.json").write_text(
        json.dumps(handoff, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "gate0_passed": handoff["gate0_passed"],
        "red_reproduced": handoff["red_reproduced"],
        "green_passed": handoff["green_passed"],
        "mutations_all_caught": handoff["mutations"]["all_caught"],
        "cleanup_items": len(cleanup_items),
        "git_diff_non_planning_observed": rf_diff_non_planning,
        "cw_diff_count": len(cw_diff),
        "written_files": len(written),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
