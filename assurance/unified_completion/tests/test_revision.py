"""CA-103 revision selector + reviewer pairing: chain validation, latest
revision selection, stale-accepted prevention, finding closure."""

from __future__ import annotations

import json
from pathlib import Path


from uc.receipt import canonical_hash, sign
from uc.revision import select


def _implementer(
    revision: str,
    supersedes: str | None = None,
    implementer: str = "impl-A",
) -> dict:
    receipt = {
        "schema_version": 1,
        "unit": "CA-T",
        "kind": "implementer",
        "created_at_utc": "2026-08-14T00:00:00Z",
        "revision": revision,
        "implementer": implementer,
        "base_triplet": {"revenue": "0" * 40},
        "result_triplet": {"revenue": "0" * 40},
        "plan_sha256": "a" * 64,
        "commands": [{"command": "pytest", "exit_code": 0}],
        "touched_files": ["x.py"],
        "side_effect_counts": {"downloads": 0},
    }
    if supersedes:
        receipt["supersedes"] = supersedes
    return sign(receipt)


def _reviewer(
    target_hash: str,
    verdict: str = "accepted",
    reviewer: str = "rev-B",
    findings: list | None = None,
) -> dict:
    return sign(
        {
            "schema_version": 1,
            "unit": "CA-T",
            "kind": "reviewer",
            "created_at_utc": "2026-08-14T00:00:00Z",
            "reviewer": reviewer,
            "verdict": verdict,
            "reviewed_object_sha256": target_hash,
            "commands": [{"command": "pytest", "exit_code": 0}],
            "findings": findings or [],
        }
    )


def _write(unit_dir: Path, payloads: list[dict], names: list[str]) -> None:
    unit_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in zip(names, payloads):
        (unit_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def test_single_revision_unique_pair(tmp_path):
    impl = _implementer("r1")
    _write(
        tmp_path,
        [impl, _reviewer(canonical_hash(impl))],
        ["11_implementer_receipt.json", "12_reviewer_receipt.json"],
    )
    selection, problems = select(tmp_path)
    assert problems == []
    assert selection["latest_revision"] == "r1"
    assert selection["verdict"] == "accepted"


def test_superseded_chain_selects_latest(tmp_path):
    r1 = _implementer("r1")
    r2 = _implementer("r2", supersedes="r1")
    _write(
        tmp_path,
        [r1, r2, _reviewer(canonical_hash(r2))],
        ["11_r1.json", "11_r2.json", "12_reviewer_receipt.json"],
    )
    selection, problems = select(tmp_path)
    assert problems == []
    assert selection["latest_revision"] == "r2"


def test_reviewer_referencing_stale_revision_red(tmp_path):
    r1 = _implementer("r1")
    r2 = _implementer("r2", supersedes="r1")
    _write(
        tmp_path,
        [r1, r2, _reviewer(canonical_hash(r1))],
        ["11_r1.json", "11_r2.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("no reviewer receipt references the latest" in p for p in problems)


def test_reviewer_self_red(tmp_path):
    impl = _implementer("r1", implementer="same-person")
    _write(
        tmp_path,
        [impl, _reviewer(canonical_hash(impl), reviewer="same-person")],
        ["11_implementer_receipt.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("reviewer identity equals implementer" in p for p in problems)


def test_stale_accepted_must_not_win(tmp_path):
    r1 = _implementer("r1")
    r2 = _implementer("r2", supersedes="r1")
    _write(
        tmp_path,
        [
            r1,
            r2,
            _reviewer(canonical_hash(r1), verdict="accepted"),
            _reviewer(canonical_hash(r2), verdict="changes_required"),
        ],
        ["11_r1.json", "11_r2.json", "12_review_r1.json", "12_review_r2.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("stale accepted must not win" in p for p in problems)


def test_unknown_supersedes_red(tmp_path):
    r2 = _implementer("r2", supersedes="r0-missing")
    _write(
        tmp_path,
        [r2, _reviewer(canonical_hash(r2))],
        ["11_r2.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("supersedes unknown" in p for p in problems)


def test_fork_red(tmp_path):
    r1 = _implementer("r1")
    r2a = _implementer("r2a", supersedes="r1")
    r2b = _implementer("r2b", supersedes="r1")
    _write(
        tmp_path,
        [r1, r2a, r2b, _reviewer(canonical_hash(r2a))],
        ["11_r1.json", "11_r2a.json", "11_r2b.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("fork" in p for p in problems)


def test_duplicate_revision_red(tmp_path):
    r1 = _implementer("r1")
    _write(
        tmp_path,
        [r1, r1, _reviewer(canonical_hash(r1))],
        ["11_r1.json", "11_r1_dup.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("duplicate revision id" in p for p in problems)


def test_p1_finding_without_successor_red(tmp_path):
    impl = _implementer("r1")
    review = _reviewer(
        canonical_hash(impl),
        findings=[{"id": "F-1", "severity": "P1", "summary": "blocking"}],
    )
    _write(
        tmp_path,
        [impl, review],
        ["11_implementer_receipt.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("unclosed P1 finding without successor" in p for p in problems)


def test_p1_finding_with_successor_ok(tmp_path):
    impl = _implementer("r1")
    review = _reviewer(
        canonical_hash(impl),
        findings=[
            {
                "id": "F-1",
                "severity": "P1",
                "summary": "blocking",
                "successor": "CA-999",
            }
        ],
    )
    _write(
        tmp_path,
        [impl, review],
        ["11_implementer_receipt.json", "12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert problems == []


def test_two_reviewers_same_hash_red(tmp_path):
    impl = _implementer("r1")
    _write(
        tmp_path,
        [
            impl,
            _reviewer(canonical_hash(impl), reviewer="rev-B"),
            _reviewer(canonical_hash(impl), reviewer="rev-C"),
        ],
        [
            "11_implementer_receipt.json",
            "12_reviewer_receipt.json",
            "12_reviewer_dup.json",
        ],
    )
    _selection, problems = select(tmp_path)
    assert any("reviewer receipts reference the latest" in p for p in problems)


def test_no_implementer_receipt_red(tmp_path):
    _write(
        tmp_path,
        [_reviewer("0" * 64)],
        ["12_reviewer_receipt.json"],
    )
    _selection, problems = select(tmp_path)
    assert any("no implementer receipt" in p for p in problems)
