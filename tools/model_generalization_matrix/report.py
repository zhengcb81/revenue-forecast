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

SCHEMA = "model-generalization-matrix/1"


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
    required = {c.case_id: c for c in C.CASES}
    observed_ids = [r.case_id for r in results]
    missing = sorted(set(required) - set(observed_ids))
    unexpected = sorted(set(observed_ids) - set(required))
    duplicates = sorted({cid for cid in observed_ids if observed_ids.count(cid) > 1})
    for cls in sorted({c.cls for c in C.CASES}):
        rs = by_class.get(cls, [])
        expected_ids = {c.case_id for c in C.CASES if c.cls == cls}
        ok = (len(rs) == len(expected_ids) and {r.case_id for r in rs} == expected_ids
              and all(r.status in {"PASS", "REJECT_OK"} for r in rs))
        class_status[cls] = "PASS" if ok else "FAIL"
    coverage = {"missing_cases": missing, "unexpected_cases": unexpected, "duplicate_cases": duplicates}
    clean = (bool(results) and not missing and not unexpected and not duplicates
             and all(s == "PASS" for s in class_status.values())
             and not residuals and cleanup.get("restored_absent") is True
             and cleanup.get("readonly_unchanged") is True
             and cleanup.get("owned_root_restored", True) is True)

    return {
        "status": "COMPLETE" if clean else "FAILED",
        "vector_coverage": coverage,
        "combination_coverage": {
            "status": "PARTIAL",
            "remaining": [
                "M01 explicit CNY/HKD labels and same-currency scaling",
                "M04 dated acquisition/control, cross-FY and missing-quarter ancestry",
                "M06 correlated joint volume/price scenarios",
                "M07 cumulative target and gross/net/cannibalization",
                "M08 future actual/WAPE null through draft output",
            ],
            "note": "Class PASS describes declared vectors only, not every card boundary.",
        },
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
