"""CA-102 content-addressed receipts: canonical hashing, kind-specific
required fields, N/N-1 policy, tamper detection."""

from __future__ import annotations

import json
from pathlib import Path


from uc.receipt import canonical_hash, sign, validate


def _base_receipt(kind: str) -> dict:
    receipt = {
        "schema_version": 1,
        "unit": "CA-999",
        "kind": kind,
        "created_at_utc": "2026-08-14T00:00:00Z",
        "base_triplet": {"revenue": "0" * 40, "filing": "1" * 40, "wiki": "2" * 40},
        "result_triplet": {"revenue": "3" * 40, "filing": "4" * 40, "wiki": "5" * 40},
    }
    if kind == "implementer":
        receipt.update(
            {
                "plan_sha256": "a" * 64,
                "commands": [{"command": "pytest -q", "exit_code": 0}],
                "touched_files": ["assurance/unified_completion/uc/receipt.py"],
                "side_effect_counts": {"downloads": 0},
                "implementer": "impl-A",
                "scenario_results": [],
                "scenario_note": "governance card; no scenario mapping",
            }
        )
    elif kind == "reviewer":
        receipt.update(
            {
                "reviewer": "rev-B",
                "verdict": "accepted",
                "reviewed_object_sha256": "6" * 40,
                "commands": [{"command": "pytest -q", "exit_code": 0}],
            }
        )
    else:
        receipt.update(
            {
                "closure": {"decision": "accepted", "by": "rev-B", "next": "CA-1000"},
                "state_sha256": "b" * 64,
                "manifest_sha256": "c" * 64,
                "control_page_sha256": "d" * 64,
            }
        )
    return receipt


def _write(receipt: dict, path: Path) -> None:
    path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def test_sign_verify_roundtrip(tmp_path):
    receipt = sign(_base_receipt("implementer"))
    path = tmp_path / "r.json"
    _write(receipt, path)
    assert validate(path) == []
    assert receipt["canonical_hash"] == canonical_hash(receipt)


def test_tamper_detected(tmp_path):
    path = tmp_path / "r.json"
    _write(sign(_base_receipt("implementer")), path)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("impl-A", "impl-X"), encoding="utf-8")
    problems = validate(path)
    assert any("canonical_hash mismatch" in p for p in problems)


def test_missing_canonical_hash_red(tmp_path):
    path = tmp_path / "r.json"
    _write(_base_receipt("implementer"), path)
    problems = validate(path)
    assert any("missing canonical_hash" in p for p in problems)


def test_unknown_field_tolerated(tmp_path):
    receipt = _base_receipt("implementer")
    receipt["future_field"] = {"anything": 1}  # present BEFORE signing
    path = tmp_path / "r.json"
    _write(sign(receipt), path)
    assert validate(path) == []


def test_unknown_schema_version_rejected(tmp_path):
    receipt = sign(_base_receipt("implementer"))
    receipt["schema_version"] = 99
    path = tmp_path / "r.json"
    _write(receipt, path)
    problems = validate(path)
    assert any("schema_version" in p for p in problems)


def test_kind_required_fields(tmp_path):
    receipt = _base_receipt("implementer")
    del receipt["touched_files"]
    path = tmp_path / "r.json"
    _write(receipt, path)
    problems = validate(path)
    assert any("touched_files" in p for p in problems)


def test_empty_commands_red(tmp_path):
    receipt = _base_receipt("implementer")
    receipt["commands"] = []
    path = tmp_path / "r.json"
    _write(receipt, path)
    problems = validate(path)
    assert any("commands" in p for p in problems)


def test_policy_placeholder_rejected(tmp_path):
    receipt = sign(_base_receipt("implementer"))
    receipt["policy_sha256"] = "not-applicable"
    path = tmp_path / "r.json"
    _write(receipt, path)
    problems = validate(path)
    assert any("policy_sha256" in p for p in problems)


def test_fabricated_triplet_rejected(tmp_path):
    receipt = sign(_base_receipt("implementer"))
    receipt["result_triplet"]["revenue"] = "f" * 40  # no such git object
    path = tmp_path / "r.json"
    _write(receipt, path)
    repo_roots = {
        "revenue": Path(__file__).resolve().parents[3],
        "filing": Path(__file__).resolve().parents[3].parent / "filing-fetch",
        "wiki": Path(__file__).resolve().parents[3].parent / "company-wiki",
    }
    problems = validate(path, repo_roots)
    assert any("not a real git object" in p for p in problems)


def test_reviewer_verdict_enum(tmp_path):
    receipt = sign(_base_receipt("reviewer"))
    receipt["verdict"] = "maybe"
    path = tmp_path / "r.json"
    _write(receipt, path)
    problems = validate(path)
    assert any("verdict" in p for p in problems)


def test_closure_kind_valid(tmp_path):
    path = tmp_path / "r.json"
    _write(sign(_base_receipt("closure")), path)
    assert validate(path) == []
