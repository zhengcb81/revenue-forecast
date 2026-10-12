"""Assemble the ``model-generalization-matrix/1`` report from case results.

The report is a source/model engineering artifact only.  It always carries
``source_truth_verified=false`` and ``economic_reasonableness="not_evaluated"``:
this package stresses the engine's math boundaries; it never certifies a real
company's numbers and never issues a research conclusion.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .runner import CaseResult
from . import cases as C
from . import combinations as CB

SCHEMA = "model-generalization-matrix/1"


def required_case_ids() -> list[str]:
    """The single authoritative required list (W07 16 + W08 combinations)."""
    return [c.case_id for c in C.CASES] + [c.case_id for c in CB.COMBINATION_CASES]


def _combination_coverage(results: list[CaseResult]) -> dict[str, Any]:
    """Per-group coverage consumed from the SAME list the report requires.

    A group is closed only when every case in its authoritative
    ``required_case_ids`` actually ran and landed on its expected outcome
    (PASS or REJECT_OK).  A missing case, an unexecuted case, an ERROR or a
    mismatch leaves the group ``OPEN`` — an unknown is never a pass.
    """
    by_id = {r.case_id: r for r in results}
    groups: dict[str, Any] = {}
    open_groups: list[str] = []
    for group_id in sorted(CB.COMBINATION_GROUP_REQUIREMENTS):
        spec = CB.COMBINATION_GROUP_REQUIREMENTS[group_id]
        required = list(spec["required_case_ids"])
        observed = [cid for cid in required if cid in by_id]
        missing = [cid for cid in required if cid not in by_id]
        not_run = [cid for cid in observed if by_id[cid].status == "NOT_RUN"]
        failed = [
            cid for cid in observed
            if by_id[cid].status not in {"PASS", "REJECT_OK", "NOT_RUN"}
        ]
        closed = not missing and not not_run and not failed and bool(observed)
        groups[group_id] = {
            "title": spec["title"],
            "native_entry": spec["native_entry"],
            "closes": spec["closes"],
            "required_case_ids": required,
            "observed_case_ids": observed,
            "missing_case_ids": missing,
            "not_run_case_ids": not_run,
            "unexpected_status_case_ids": failed,
            "status": "CLOSED" if closed else "OPEN",
            "evidence": {
                cid: {
                    "status": by_id[cid].status,
                    "native_entries": sorted(
                        {ref.get("entry") for ref in by_id[cid].native_refs}
                    ),
                    "native_ref_count": len(by_id[cid].native_refs),
                }
                for cid in observed
            },
        }
        if not closed:
            open_groups.append(group_id)
    return {
        "status": "COMPLETE" if not open_groups else "PARTIAL",
        "open_groups": open_groups,
        "groups": groups,
        "note": (
            "Group status comes from the authoritative per-group required_case_ids "
            "manifest, never from a case count. An unknown/not-run case leaves its "
            "group OPEN."
        ),
    }


def _sha_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Counts:
    total: int = 0
    passed: int = 0
    failed: int = 0
    reject_ok: int = 0
    reject_mismatch: int = 0
    errored: int = 0
    not_run: int = 0

    def to_json(self) -> dict[str, int]:
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "reject_ok": self.reject_ok,
            "reject_mismatch": self.reject_mismatch,
            "errored": self.errored,
            "not_run": self.not_run,
        }


def build_report(
    results: list[CaseResult],
    *,
    started_at: str,
    finished_at: str,
    wall_seconds: float,
    cleanup: dict[str, Any],
    residuals: list[str],
    engine_versions: dict[str, Any],
) -> dict[str, Any]:
    counts = Counts()
    for r in results:
        counts.total += 1
        if r.status == "PASS":
            counts.passed += 1
        elif r.status == "FAIL":
            counts.failed += 1
        elif r.status == "REJECT_OK":
            counts.reject_ok += 1
        elif r.status == "REJECT_MISMATCH":
            counts.reject_mismatch += 1
        elif r.status == "ERROR":
            counts.errored += 1
        else:
            counts.not_run += 1

    # Class-level roll-up: a class is green only when its legal and counter/unknown
    # vectors both land on their expected outcome.
    class_status: dict[str, str] = {}
    by_class: dict[str, list[CaseResult]] = {}
    for r in results:
        by_class.setdefault(r.cls, []).append(r)
    required = {cid: True for cid in required_case_ids()}
    all_cases = list(C.CASES) + list(CB.COMBINATION_CASES)
    observed_ids = [r.case_id for r in results]
    missing = sorted(set(required) - set(observed_ids))
    unexpected = sorted(set(observed_ids) - set(required))
    duplicates = sorted({cid for cid in observed_ids if observed_ids.count(cid) > 1})
    for cls in sorted({c.cls for c in all_cases}):
        rs = by_class.get(cls, [])
        expected_ids = {c.case_id for c in all_cases if c.cls == cls}
        ok = (len(rs) == len(expected_ids) and {r.case_id for r in rs} == expected_ids
              and all(r.status in {"PASS", "REJECT_OK"} for r in rs))
        class_status[cls] = "PASS" if ok else "FAIL"
    coverage = {"missing_cases": missing, "unexpected_cases": unexpected, "duplicate_cases": duplicates}
    combination_coverage = _combination_coverage(results)
    clean = (bool(results) and not missing and not unexpected and not duplicates
             and all(s == "PASS" for s in class_status.values())
             and combination_coverage["status"] == "COMPLETE"
             and not residuals and cleanup.get("restored_absent") is True
             and cleanup.get("readonly_unchanged") is True
             and cleanup.get("owned_root_restored", True) is True)

    return {
        "status": "COMPLETE" if clean else "FAILED",
        "vector_coverage": coverage,
        "required_case_ids": required_case_ids(),
        "combination_coverage": combination_coverage,
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds": round(wall_seconds, 6),
        "engine_versions": engine_versions,
        "source_truth_verified": False,
        "economic_reasonableness": "not_evaluated",
        "scope": (
            "Finite cross-mechanism combination stress matrix over the native draft "
            "engine. Synthetic engineering vectors; no real company, no source truth, "
            "no buy-side conclusion."
        ),
        "counts": counts.to_json(),
        "class_status": class_status,
        "cases": [r.to_json() for r in results],
        "cleanup": cleanup,
        "residuals": residuals,
    }


def write_report(report: dict[str, Any], out_root: str) -> dict[str, str]:
    import os

    os.makedirs(out_root, exist_ok=False)
    json_path = os.path.join(out_root, "model-generalization-matrix.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    md_path = os.path.join(out_root, "model-generalization-matrix.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(report))
    return {"json": json_path, "markdown": md_path}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Model Generalization Matrix (`model-generalization-matrix/1`)",
        "",
        f"- execution status: {report['status']}",
        f"- combination coverage: {report['combination_coverage']['status']}",
        f"- generated_at: {report['generated_at']}",
        f"- wall_seconds: {report['wall_seconds']}",
        f"- source_truth_verified: {report['source_truth_verified']}",
        f"- economic_reasonableness: {report['economic_reasonableness']}",
        "",
        report["scope"],
        "",
        "## Counts",
        "",
        "| total | passed | failed | reject_ok | reject_mismatch | errored | not_run |",
        "|---|---|---|---|---|---|---|",
    ]
    c = report["counts"]
    lines.append(
        f"| {c['total']} | {c['passed']} | {c['failed']} | {c['reject_ok']} | "
        f"{c['reject_mismatch']} | {c['errored']} | {c['not_run']} |"
    )
    lines += ["", "## Class status", "", "| class | status |", "|---|---|"]
    for cls in sorted(report["class_status"]):
        lines.append(f"| {cls} | {report['class_status'][cls]} |")
    combo = report.get("combination_coverage", {})
    lines += [
        "",
        "## Combination group coverage (C01-C05)",
        "",
        f"- status: {combo.get('status')}",
        f"- open groups: {combo.get('open_groups')}",
        f"- required cases: {len(report.get('required_case_ids', []))}",
        "",
        "| group | status | required | observed | missing |",
        "|---|---|---|---|---|",
    ]
    for group_id, group in sorted(combo.get("groups", {}).items()):
        lines.append(
            f"| {group_id} | {group['status']} | {len(group['required_case_ids'])} | "
            f"{len(group['observed_case_ids'])} | {group['missing_case_ids']} |"
        )
    lines += ["", "## Cases", ""]
    for case in report["cases"]:
        lines.append(f"### {case['case_id']} — {case['status']}")
        lines.append("")
        lines.append(f"- class: {case['class']}  vector: {case['vector']}  mode: {case['mode']}")
        lines.append(f"- boundary: {case['boundary']}")
        lines.append(f"- expected: `{json.dumps(case['expected'], ensure_ascii=False)}`")
        lines.append(f"- observed: `{json.dumps(case['observed'], ensure_ascii=False)}`")
        for a in case["assertions"]:
            mark = "✓" if a["passed"] else "✗"
            lines.append(
                f"  - {mark} {a['name']} ({a['kind']}): expected={a['expected']} observed={a['observed']}"
            )
        lines.append("")
    lines += ["## Cleanup / residuals", ""]
    lines.append(f"- cleanup: `{json.dumps(report['cleanup'], ensure_ascii=False)}`")
    lines.append(f"- residuals: {report['residuals']}")
    lines.append("")
    return "\n".join(lines)
