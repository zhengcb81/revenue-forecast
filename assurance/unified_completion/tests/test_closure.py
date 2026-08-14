"""CA-107 three-repo closure: unit classification, honest aggregate report."""

from __future__ import annotations

import json
from pathlib import Path


import uc.closure as cl
from uc.receipt import canonical_hash, sign


def _repo_layout(tmp_path):
    revenue = tmp_path / "revenue"
    filing = tmp_path / "filing-fetch"
    wiki = tmp_path / "company-wiki"
    for repo in (revenue, filing, wiki):
        (repo / "assurance" / "fc").mkdir(parents=True, exist_ok=True)
    (revenue / "assurance" / "unified_completion" / "receipts").mkdir(
        parents=True, exist_ok=True
    )
    return {"revenue": revenue, "filing": filing, "wiki": wiki}


def _implementer(unit: str, implementer: str = "impl-A") -> dict:
    return sign(
        {
            "schema_version": 1,
            "unit": unit,
            "kind": "implementer",
            "created_at_utc": "2026-08-14T00:00:00Z",
            "revision": "r1",
            "implementer": implementer,
            "base_triplet": {"revenue": "0" * 40},
            "result_triplet": {"revenue": "0" * 40},
            "plan_sha256": "a" * 64,
            "commands": [{"command": "pytest", "exit_code": 0}],
            "touched_files": ["x.py"],
            "side_effect_counts": {"downloads": 0},
        }
    )


def _reviewer(target_hash: str, reviewer: str = "rev-B") -> dict:
    return sign(
        {
            "schema_version": 1,
            "unit": "CA-T",
            "kind": "reviewer",
            "created_at_utc": "2026-08-14T00:00:00Z",
            "reviewer": reviewer,
            "verdict": "accepted",
            "reviewed_object_sha256": target_hash,
            "commands": [{"command": "pytest", "exit_code": 0}],
            "findings": [],
        }
    )


def _write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def test_scan_finds_three_repos(tmp_path):
    roots = _repo_layout(tmp_path)
    scan = cl.scan_receipt_dirs(roots)
    assert set(scan) == {"revenue", "filing", "wiki"}


def test_classify_machine_valid_pair(tmp_path):
    roots = _repo_layout(tmp_path)
    unit_dir = roots["revenue"] / "assurance/unified_completion/receipts" / "CA-T"
    unit_dir.mkdir(parents=True)
    impl = _implementer("CA-T")
    _write(unit_dir / "11_implementer_receipt.json", impl)
    _write(unit_dir / "12_reviewer_receipt.json", _reviewer(canonical_hash(impl)))
    verdict = cl.classify_unit(
        roots["revenue"],
        "assurance/unified_completion/receipts/CA-T",
    )
    assert verdict["status"] == "machine_valid"
    assert verdict["selection"]["verdict"] == "accepted"


def test_classify_legacy(tmp_path):
    roots = _repo_layout(tmp_path)
    unit_dir = roots["filing"] / "assurance/fc" / "FC-903"
    unit_dir.mkdir(parents=True)
    _write(
        unit_dir / "11_implementer_receipt.json",
        {"fc_id": "FC-903", "status": "accepted"},
    )
    verdict = cl.classify_unit(roots["filing"], "assurance/fc/FC-903", roots)
    assert verdict["status"] == "legacy"
    assert verdict["problems"] == []


def test_classify_tampered_new_schema_incomplete(tmp_path):
    roots = _repo_layout(tmp_path)
    unit_dir = roots["revenue"] / "assurance/unified_completion/receipts" / "CA-T"
    unit_dir.mkdir(parents=True)
    impl = _implementer("CA-T")
    _write(unit_dir / "11_implementer_receipt.json", impl)
    review = _reviewer(canonical_hash(impl))
    review["verdict"] = "maybe"  # tamper: illegal verdict, invalidates canonical hash
    _write(unit_dir / "12_reviewer_receipt.json", review)
    verdict = cl.classify_unit(
        roots["revenue"],
        "assurance/unified_completion/receipts/CA-T",
        roots,
    )
    assert verdict["status"] == "incomplete"
    assert any("canonical_hash mismatch" in p for p in verdict["problems"])


def _artifacts(tmp_path):
    legacy = tmp_path / "legacy.json"
    legacy.write_text(
        json.dumps(
            {
                "fc_entries": [
                    {"fc_id": "FC-1501", "class": "P"},
                    {"fc_id": "FC-501", "class": "C"},
                ]
            }
        ),
        encoding="utf-8",
    )
    scenarios = tmp_path / "scenarios.json"
    scenarios.write_text(
        json.dumps(
            {
                "counts": {"unique_total": 197},
                "scenarios": {
                    "AR-01": {"status": "pending"},
                    "AR-02": {"status": "passed"},
                },
            }
        ),
        encoding="utf-8",
    )
    return legacy, scenarios


def test_closure_report_honest_incomplete(tmp_path):
    roots = _repo_layout(tmp_path)
    legacy, scenarios = _artifacts(tmp_path)
    report = cl.closure_report(roots, legacy, scenarios)
    assert report["old_plan_verdict"] == "incomplete"
    assert any("contradicted" in reason for reason in report["reasons"])
    assert any("pending" in reason for reason in report["reasons"])
    assert any("unsatisfied" in reason for reason in report["reasons"])
    assert any("R9" in reason for reason in report["reasons"])
    assert report["scenario_summary"]["unsatisfied"] == 1
    assert report["legacy_summary"]["pending"] == 1


def test_closure_report_lists_incomplete_units(tmp_path):
    roots = _repo_layout(tmp_path)
    legacy, scenarios = _artifacts(tmp_path)
    unit_dir = roots["revenue"] / "assurance/unified_completion/receipts" / "CA-T"
    unit_dir.mkdir(parents=True)
    _write(unit_dir / "11_implementer_receipt.json", _implementer("CA-T"))
    report = cl.closure_report(roots, legacy, scenarios)
    unit = next(u for u in report["units"] if u["unit"] == "CA-T")
    assert unit["status"] == "incomplete"
    assert any("no reviewer receipt" in p for p in unit["problems"])
