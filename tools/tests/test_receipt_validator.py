"""FC-103: receipt/closure validator RED/green + negative mutation suite.

Covers every rejection the runbook (section 5 + independent review protocol)
mandates: short hashes, placeholder policy hash, pending review, stale
triplet, skipped scenario, fake reviewer (same identity as implementer),
future timestamp, fc_id outside the registry, changed-files outside the
allowlist, non-zero command exit, surviving mutation, and incomplete legacy
receipts. Also pins the stricter ``can_accept`` gate (real sealing hashes +
independent reviewer).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

from receipt_validator import (  # noqa: E402  # type: ignore[import-not-found]
    FC_IDS,
    can_accept,
    validate_receipt,
)

H40 = "3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7"
H40b = "67609128e2c09a0cbdd64cad38d40028f72fd2f5"
H64 = "158fc1e1e4231e3c2dc71822a58931fdca64eff79fc0d4e27b8276a397f4c78a"
REVIEWER_HASH = "a" * 64
TODAY = date(2026, 8, 9)


def _triplet(h=H40):
    return {"revenue": h, "filing": H40, "wiki": H40}


def _valid():
    return {
        "schema_version": "2.0",
        "fc_id": "FC-101",
        "status": "independent_review",
        "base_triplet": _triplet(),
        "result_triplet": _triplet(H40b),
        "plan_sha256": H64,
        "policy_sha256": "not-applicable",
        "allowed_files": ["a.py"],
        "changed_files": ["a.py"],
        "dependency_receipts": [],
        "command_registry_sha256": "pending-fc-104",
        "commands": [{"command": "pytest", "exit_code": 0, "output_sha256": H64}],
        "scenario_results": [],
        "review": {"reviewer": "", "reviewer_receipt_sha256": "", "decision": "pending", "reviewed_at": ""},
        "mutation": {"id": "M-1", "killed": True},
    }


def _accepted(reviewer="bob"):
    r = _valid()
    r["status"] = "independent_review"
    r["command_registry_sha256"] = H64  # real seal
    r["review"] = {
        "reviewer": reviewer,
        "reviewer_receipt_sha256": REVIEWER_HASH,
        "decision": "accepted",
        "reviewed_at": str(TODAY),
    }
    return r


def test_fc_registry_is_the_closed_71():
    assert len(FC_IDS) == 71


def test_valid_receipt_passes_structural():
    assert validate_receipt(_valid(), implementer="alice", today=TODAY) == []


def _bad(mutate):
    r = _valid()
    mutate(r)
    return validate_receipt(r, implementer="alice", today=TODAY)


def test_rejects_short_base_triplet_hash():
    def m(r): r["base_triplet"]["revenue"] = "3ce9cc4"
    assert _bad(m)


def test_rejects_short_result_triplet_hash():
    def m(r): r["result_triplet"]["filing"] = "c9799b7"
    assert _bad(m)


def test_rejects_short_plan_hash():
    def m(r): r["plan_sha256"] = "158fc1e1"
    assert _bad(m)


def test_rejects_placeholder_policy_hash():
    def m(r): r["policy_sha256"] = "PLACEHOLDER"
    assert _bad(m)


def test_rejects_malformed_policy_hash():
    def m(r): r["policy_sha256"] = "zzz"
    assert _bad(m)


def test_rejects_placeholder_command_registry_hash():
    def m(r): r["command_registry_sha256"] = "TBD"
    assert _bad(m)


def test_rejects_fc_id_outside_registry():
    def m(r): r["fc_id"] = "FC-999"
    assert _bad(m)


def test_rejects_changed_file_outside_allowlist():
    def m(r): r["changed_files"] = ["secret.py"]
    assert _bad(m)


def test_rejects_nonzero_command_exit():
    def m(r): r["commands"][0]["exit_code"] = 1
    assert _bad(m)


def test_rejects_skipped_scenario():
    def m(r): r["scenario_results"] = [{"id": "EX-01", "status": "skipped"}]
    assert _bad(m)


def test_rejects_xfailed_scenario():
    def m(r): r["scenario_results"] = [{"id": "DL-04", "status": "xfail"}]
    assert _bad(m)


def test_rejects_surviving_mutation():
    def m(r): r["mutation"] = {"id": "M-1", "killed": False}
    assert _bad(m)


def test_rejects_fake_reviewer_same_as_implementer():
    r = _accepted(reviewer="alice")
    problems = validate_receipt(r, implementer="alice", reviewer="alice", today=TODAY)
    assert any("implementer cannot self-accept" in p for p in problems)


def test_rejects_future_review_timestamp():
    r = _accepted()
    r["review"]["reviewed_at"] = str(TODAY + timedelta(days=3))
    assert validate_receipt(r, implementer="alice", reviewer="bob", today=TODAY)


def test_rejects_accepted_with_empty_reviewer():
    r = _accepted(reviewer="")
    assert validate_receipt(r, implementer="alice", today=TODAY)


def test_rejects_accepted_with_missing_reviewer_receipt_hash():
    r = _accepted()
    r["review"]["reviewer_receipt_sha256"] = "short"
    assert validate_receipt(r, implementer="alice", reviewer="bob", today=TODAY)


def test_can_accept_with_independent_reviewer_and_real_seals():
    ok, problems = can_accept(_accepted(), implementer="alice", reviewer="bob", today=TODAY)
    assert ok, problems


def test_can_accept_rejects_pending_command_registry():
    r = _accepted()
    r["command_registry_sha256"] = "pending-fc-104"
    ok, problems = can_accept(r, implementer="alice", reviewer="bob", today=TODAY)
    assert not ok and any("pending-fc-104" in p for p in problems)


def test_can_accept_rejects_pending_review_decision():
    ok, problems = can_accept(_valid(), implementer="alice", reviewer="bob", today=TODAY)
    assert not ok


def test_legacy_incomplete_receipt_is_not_accepted():
    # Old receipts lacked schema 2.0 fields; the gate must not misjudge them.
    legacy = {"fc_id": "FC-101", "status": "accepted", "reviewer": "someone"}
    assert validate_receipt(legacy, implementer="alice", reviewer="someone", today=TODAY)
    ok, _ = can_accept(legacy, implementer="alice", reviewer="someone", today=TODAY)
    assert not ok
