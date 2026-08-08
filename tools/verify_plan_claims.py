"""Verify that "completed" plan claims are backed by machine evidence (R5, RC-2).

Parses a markdown plan (default: ``task_plan.md``), finds every
``## Phase N（...）— 状态：completed`` section and reports:

1. **Unchecked items**: a completed section with ``[ ]`` items needs an
   explicit ``豁免`` (waiver) note inside the section, else it is a
   name-only completion (N-02/F-11 lesson).
2. **Evidence**: the progress log must mention the phase with a test command
   + pass count + date; a completed claim without evidence is reported.

Exit code 0 = all completed claims backed; 1 = problems found.
``--json`` emits a machine-readable report.  Runs standalone or in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PHASE_HEADING = re.compile(
    r"^##\s+Phase\s+(\d+)[^\n]*—\s*状态：completed\s*$", re.IGNORECASE
)
CHECKBOX_UNCHECKED = re.compile(r"\[ \]")
CHECKBOX_CHECKED = re.compile(r"\[x\]")


def parse_plan(plan_text: str) -> list[dict]:
    """Return per-phase: number, unchecked count, has_waiver."""
    phases: list[dict] = []
    current: dict | None = None
    for line in plan_text.splitlines():
        heading = PHASE_HEADING.match(line)
        if heading:
            current = {
                "number": int(heading.group(1)),
                "unchecked": 0,
                "has_waiver": False,
            }
            phases.append(current)
            continue
        if current is None:
            continue
        if CHECKBOX_UNCHECKED.search(line):
            current["unchecked"] += 1
        if "豁免" in line:
            current["has_waiver"] = True
    return phases


def evidence_in_progress(progress_text: str, phase_number: int) -> bool:
    """A phase is evidence-backed when the log mentions it plus a test command,
    a pass count, and a date — the machine-verifiable completion signature."""
    mentions_phase = (
        f"Phase {phase_number}" in progress_text
        or f"phase {phase_number}" in progress_text.lower()
    )
    if not mentions_phase:
        return False
    has_command = bool(re.search(r"pytest|python [\w./-]+\.py", progress_text))
    has_passed = bool(re.search(r"passed|通过|全绿", progress_text))
    has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}", progress_text))
    return has_command and has_passed and has_date


def verify(plan_text: str, progress_text: str) -> tuple[list[str], list[dict]]:
    problems: list[str] = []
    report: list[dict] = []
    for phase in parse_plan(plan_text):
        number = phase["number"]
        entry: dict = {
            "phase": number,
            "unchecked_items": phase["unchecked"],
            "waiver": phase["has_waiver"],
            "evidence": evidence_in_progress(progress_text, number),
            "ok": True,
            "problems": [],
        }
        if phase["unchecked"] > 0 and not phase["has_waiver"]:
            entry["ok"] = False
            entry["problems"].append(
                f"Phase {number}: {phase['unchecked']} unchecked item(s) in a "
                "completed section with no waiver note"
            )
        if not entry["evidence"]:
            entry["ok"] = False
            entry["problems"].append(
                f"Phase {number}: no machine evidence (test command + pass "
                "count + date) in progress.md"
            )
        if not entry["ok"]:
            problems.extend(entry["problems"])
        report.append(entry)
    return problems, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify completed plan claims")
    parser.add_argument("--plan", type=Path, default=None, help="plan markdown path")
    parser.add_argument("--progress", type=Path, default=None, help="progress log path")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    plan_path = args.plan or root / "task_plan.md"
    progress_path = args.progress or root / "progress.md"
    if not plan_path.is_file() or not progress_path.is_file():
        print(f"missing plan/progress file: {plan_path} {progress_path}")
        return 2
    problems, report = verify(
        plan_path.read_text(encoding="utf-8"),
        progress_path.read_text(encoding="utf-8"),
    )
    if args.json:
        print(json.dumps({"ok": not problems, "problems": problems, "phases": report}, indent=2, sort_keys=True))
        return 1 if problems else 0
    for problem in problems:
        print(f"PLAN-VERIFY: {problem}")
    if not problems:
        print(f"OK: all completed claims in {plan_path.name} are evidence-backed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
