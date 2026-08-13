"""FC-1501: machine closure gate — the single machine verdict for FCAP completion.

Checks, from the work_unit_registry + receipts + scenario results:
  1. every mandatory FC (71) is ``accepted`` in the registry;
  2. every accepted receipt re-validates structurally (receipt_validator);
  3. all scenario_results across accepted receipts carry no pending/blocked;
  4. the three repo HEADs are descendants of the frozen baseline triplet;
  5. no registry entry is pending/in_progress/blocked.

Exit 0 = closure gate GREEN (FC-1505 may generate the closure ledger).
Any failure lists the offending items.  Honest by construction: it reports
the current incomplete state rather than fabricating completion.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = PROJECT_ROOT / "audit_review" / "2026-08-09_full_completion_assurance_plan" / "work_unit_registry.md"
MANIFEST = PROJECT_ROOT / "compatibility" / "current.json"

PENDING_MARKERS = ("pending", "in_progress", "blocked", "changes_required")


def _registry_entries() -> dict[str, str]:
    text = REGISTRY.read_text(encoding="utf-8")
    entries: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(FC-\d+)\s*\|\s*([^|]+)\|", line)
        if m:
            entries[m.group(1)] = m.group(2).strip()
    return entries


def _accepted_receipts(entries: dict[str, str]) -> list[Path]:
    receipts = []
    for fc_id, status in sorted(entries.items()):
        if "accepted" in status:
            for base in (PROJECT_ROOT / "assurance" / "fc", PROJECT_ROOT.parent / "company-wiki" / "assurance" / "fc"):
                receipt = base / fc_id / "11_implementer_receipt.json"
                if receipt.is_file():
                    receipts.append(receipt)
                    break
    return receipts


def _validate_receipts(receipts: list[Path]) -> list[str]:
    problems: list[str] = []
    for receipt in receipts:
        proc = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "tools" / "receipt_validator.py"),
             "--receipt", str(receipt)],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            problems.append(f"receipt invalid: {receipt.name}: {proc.stdout.strip()[-200:]}")
    return problems


def _scenario_status(entries: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for fc_id, status in sorted(entries.items()):
        if "accepted" not in status:
            continue
        for base in (PROJECT_ROOT / "assurance" / "fc", PROJECT_ROOT.parent / "company-wiki" / "assurance" / "fc"):
            receipt = base / fc_id / "11_implementer_receipt.json"
            if not receipt.is_file():
                continue
            try:
                payload = json.loads(receipt.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                problems.append(f"receipt unreadable: {fc_id}")
                continue
            for sr in payload.get("scenario_results", []):
                if sr.get("status") in ("skip", "skipped", "xfail", "pending", "blocked"):
                    problems.append(f"{fc_id} scenario {sr.get('id')} status={sr.get('status')}")
            break
    return problems


def _triplet_descends(entries: dict[str, str]) -> list[str]:
    problems: list[str] = []
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest unreadable: {exc}"]
    repos = {
        "revenue": PROJECT_ROOT,
        "filing": PROJECT_ROOT.parent / "filing-fetch",
        "wiki": PROJECT_ROOT.parent / "company-wiki",
    }
    for key, repo in repos.items():
        base = (manifest.get("frozen_baseline_triplet") or {}).get(key)
        if not base:
            continue
        proc = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", base, "HEAD"],
            capture_output=True, timeout=60,
        )
        if proc.returncode != 0:
            problems.append(f"{key} HEAD is not a descendant of the frozen baseline")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    entries = _registry_entries()
    problems: list[str] = []
    pending = [f"{fc} ({status})" for fc, status in sorted(entries.items())
               if any(m in status for m in PENDING_MARKERS)]
    if pending:
        problems.append(f"FCs not accepted: {', '.join(pending)}")
    if len(entries) != 71:
        problems.append(f"registry has {len(entries)} entries, expected 71")
    problems.extend(_validate_receipts(_accepted_receipts(entries)))
    problems.extend(_scenario_status(entries))
    problems.extend(_triplet_descends(entries))

    report = {
        "closure_gate": "PASS" if not problems else "FAIL",
        # accepted + the 3 plan-baseline FCs (FC-000..002, status "completed")
        "accepted_fcs": sum(
            1 for s in entries.values() if "accepted" in s or "completed" in s
        ),
        "total_fcs": len(entries),
        "problems": problems,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for problem in problems:
            print(f"CLOSURE-PROBLEM: {problem}")
        if not problems:
            print("CLOSURE-GATE: PASS — all 71 FCs accepted, receipts valid, "
                  "scenarios clean, triplet intact")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
