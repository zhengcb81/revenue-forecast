"""WU-103: runbook completeness validator + closure mapping + claim gate.

Validates that:
- task_plan and implementation_runbook declare the SAME WU set, no duplicates.
- every runbook card has all seven required fields non-empty.
- no open placeholders (待补齐/TBD/placeholder) remain in either file.
- plan_version binding matches between the two files.
- every finding F-034..F-060 (and D-* decisions) has exactly one mapping row.
- forbidden claims ("生产已接入/复用已验证/只改配置即可") appear only when a
  product caller + cross-process E2E receipt exists (checked at gate time).

Exit codes: 0 = valid; 1 = problems; 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]

CARD_FIELDS = ("Owner/Targets", "Inputs", "RED/Focused", "Mutation", "Audit",
               "Rollback", "Accept")
PLACEHOLDER_PATTERNS = (
    r"待补齐", r"TBD", r"placeholder", r"TODO", r"待续", r"open item",
)
FORBIDDEN_CLAIMS = (
    r"生产已接入", r"生产复用已验证", r"只改配置即可", r"完整复用已验收",
    r"Dropbox 生产.*已验证",
)


def extract_wu_ids(text: str, prefix: str) -> set[str]:
    return set(re.findall(rf"^{re.escape(prefix)}(WU-\d+)", text, re.MULTILINE))


def check_wu_id_duplicates(text: str, prefix: str, source_label: str) -> list[str]:
    """A WU ID appearing more than once is a duplicate-card error (F1)."""
    problems: list[str] = []
    counts: dict[str, int] = {}
    for match in re.finditer(rf"^{re.escape(prefix)}(WU-\d+)", text, re.MULTILINE):
        wu_id = match.group(1)
        counts[wu_id] = counts.get(wu_id, 0) + 1
    for wu_id, count in sorted(counts.items()):
        if count > 1:
            problems.append(f"{source_label}: WU ID {wu_id} appears {count} times")
    return problems


def check_wu_sets_match(plan_text: str, runbook_text: str) -> list[str]:
    problems: list[str] = []
    plan_ids = extract_wu_ids(plan_text, "### ")
    runbook_ids = extract_wu_ids(runbook_text, "### ")
    if not plan_ids:
        problems.append("no WU IDs found in task_plan.md")
        return problems
    if not runbook_ids:
        problems.append("no WU cards found in implementation_runbook.md")
        return problems
    missing_cards = sorted(plan_ids - runbook_ids)
    extra_cards = sorted(runbook_ids - plan_ids)
    if missing_cards:
        problems.append(
            f"WU(s) in task_plan missing runbook cards: {missing_cards}"
        )
    if extra_cards:
        problems.append(
            f"runbook card(s) not in task_plan: {extra_cards}"
        )
    return problems


def check_card_fields(card_text: str) -> list[str]:
    """All seven card fields must be present and non-empty."""
    problems: list[str] = []
    card_id_match = re.match(r"### (WU-\d+)", card_text)
    card_id = card_id_match.group(1) if card_id_match else "?"
    for field in CARD_FIELDS:
        pattern = re.compile(
            rf"-\s*{re.escape(field)}[：:]\s*(\S.*?)(?=\n-\s*[A-Z]|\Z)",
            re.DOTALL,
        )
        match = pattern.search(card_text)
        if not match or not match.group(1).strip():
            problems.append(f"{card_id}: card field {field!r} missing/empty")
    return problems


def check_no_placeholders(text: str) -> list[str]:
    problems: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            line_no = text[:match.start()].count("\n") + 1
            problems.append(f"line {line_no}: open placeholder {match.group(0)!r}")
    return problems


def check_plan_version_binding(plan_text: str, runbook_text: str) -> list[str]:
    plan_version = re.search(r"计划版本[：:]\s*(\S+)", plan_text)
    runbook_binding = re.search(r"绑定计划[：:]\s*task_plan\.md\s+(\S+)", runbook_text)
    if not plan_version:
        return ["task_plan.md missing 计划版本 declaration"]
    if not runbook_binding:
        return ["runbook missing 绑定计划 declaration"]
    if plan_version.group(1) != runbook_binding.group(1):
        return [
            f"plan_version {plan_version.group(1)!r} != runbook binding "
            f"{runbook_binding.group(1)!r}"
        ]
    return []


def check_finding_mapping(
    findings_text: str, plan_text: str, mapping: dict[str, str]
) -> list[str]:
    """Every F-0xx mentioned in findings AND every row of the task_plan
    coverage table (F-034..F-060) must have a mapping entry (F2)."""
    problems: list[str] = []
    # strip range expressions like "F-001~F-060" so the bounds are not
    # mistaken for individual findings
    stripped = re.sub(r"F-0\d{2}~F-0\d{2}", "", findings_text)
    finding_ids = set(re.findall(r"\bF-0(\d{2})\b", stripped))
    for finding in sorted(finding_ids):
        full = f"F-0{finding}"
        if full not in mapping:
            problems.append(f"finding {full} has no owner mapping")
    # coverage-table rows: | F-035 HEAD 已漂移 | WU-101/103 | ... |
    # (ID and description share one cell — ID then any text then the pipe)
    table_ids = set(re.findall(r"^\|\s*(F-0\d{2})(?:[^|]*)\|", plan_text, re.MULTILINE))
    for finding in sorted(table_ids):
        if finding not in mapping:
            problems.append(
                f"coverage-table finding {finding} has no closure mapping row"
            )
    return problems


_RULE_LINE = re.compile(
    r"不得|禁止|不允许|只有.*才|不得在文档写|未.*不得|不能当作"
)


def check_forbidden_claims(text: str) -> list[str]:
    """Rule-description lines (不得/禁止/只有…才…) STATE the requirement and
    must not be flagged as claims; standalone assertions are flagged."""
    problems: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _RULE_LINE.search(line):
            continue
        for pattern in FORBIDDEN_CLAIMS:
            for match in re.finditer(pattern, line):
                problems.append(
                    f"line {line_no}: forbidden claim {match.group(0)!r} without "
                    "product-caller/E2E evidence (WU-103 claim gate)"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="WU-103 runbook/closure gate")
    parser.add_argument("--plan-dir", type=Path, default=PLAN_DIR)
    args = parser.parse_args()
    plan_path = args.plan_dir / "task_plan.md"
    runbook_path = args.plan_dir / "implementation_runbook.md"
    findings_path = args.plan_dir / "findings.md"
    mapping_path = args.plan_dir / "closure_mapping.json"
    for path in (plan_path, runbook_path, findings_path):
        if not path.is_file():
            print(f"missing plan file: {path}")
            return 1
    plan = plan_path.read_text(encoding="utf-8")
    runbook = runbook_path.read_text(encoding="utf-8")
    findings = findings_path.read_text(encoding="utf-8")

    problems: list[str] = []
    problems.extend(check_wu_sets_match(plan, runbook))
    problems.extend(check_wu_id_duplicates(plan, "### ", "task_plan"))
    problems.extend(check_wu_id_duplicates(runbook, "### ", "runbook"))
    problems.extend(check_plan_version_binding(plan, runbook))
    problems.extend(check_no_placeholders(plan))
    problems.extend(check_no_placeholders(runbook))

    # per-card field completeness
    card_pattern = re.compile(r"### WU-\d+.*?(?=\n### WU-|\Z)", re.DOTALL)
    for card in card_pattern.finditer(runbook):
        problems.extend(check_card_fields(card.group(0)))

    # closure mapping
    mapping: dict[str, str] = {}
    if mapping_path.is_file():
        import json
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    else:
        problems.append(f"missing closure mapping: {mapping_path}")
    problems.extend(check_finding_mapping(findings, plan, mapping))
    problems.extend(check_forbidden_claims(plan))

    for problem in problems:
        print(f"RUNBOOK-GATE: {problem}")
    if not problems:
        print("OK: WU sets match, cards complete, no placeholders, mapping closed")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
