"""WU-203 RED/audit tests: exact/latest state machine contract."""
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from reuse_latest_policy import (  # noqa: E402
    exact_decision,
    latest_gap,
    authorization_valid,
    canonical_gap_hash,
)


def test_exact_valid_handle_reuses_without_discovery():
    decision = exact_decision(has_valid_handle=True, allow_discovery=True)
    assert decision == "REUSED"
    assert "discovery" not in decision.lower() or decision == "REUSED"


def test_exact_missing_without_auth_returns_not_found():
    decision = exact_decision(has_valid_handle=False, allow_download=False)
    assert decision == "NOT_FOUND"


def test_exact_missing_with_auth_returns_download():
    decision = exact_decision(has_valid_handle=False, allow_download=True)
    assert decision == "DOWNLOAD"


def test_exact_valid_never_triggers_discovery():
    # mutation target: exact 调 discovery 必须失败
    assert exact_decision(has_valid_handle=True) != "DISCOVER"


def test_latest_gap_only_missing_periods():
    coverage = {"2024", "2025"}
    discovered = {"2025", "2026"}
    gap = latest_gap(coverage, discovered)
    assert gap == ["2026"]


def test_latest_gap_empty_when_covered():
    gap = latest_gap({"2024", "2025"}, {"2024", "2025"})
    assert gap == []


def test_latest_covered_period_not_in_gap():
    # mutation target: 把 covered period 加入 missing 必须失败
    gap = latest_gap({"2024"}, {"2024", "2025"})
    assert "2024" not in gap


def test_authorization_hash_binding():
    auth = {"gap_plan_hash": "abc", "policy_hash": "pol1", "expires_at": "2099-01-01"}
    now = "2026-01-01"
    assert authorization_valid(auth, gap_plan_hash="abc", policy_hash="pol1", now=now)


def test_authorization_stale_hash_invalid():
    auth = {"gap_plan_hash": "abc", "policy_hash": "pol1", "expires_at": "2099-01-01"}
    # gap plan changed -> old authorization must be invalid
    assert not authorization_valid(auth, gap_plan_hash="xyz", policy_hash="pol1",
                                   now="2026-01-01")


def test_authorization_expired_invalid():
    auth = {"gap_plan_hash": "abc", "policy_hash": "pol1", "expires_at": "2025-01-01"}
    assert not authorization_valid(auth, gap_plan_hash="abc", policy_hash="pol1",
                                   now="2026-01-01")


def test_canonical_gap_hash_deterministic_and_binds_plan():
    a = canonical_gap_hash(["2026"], covered={"2024", "2025"})
    b = canonical_gap_hash(["2026"], covered={"2024", "2025"})
    assert a == b
    assert a != canonical_gap_hash(["2027"], covered={"2024", "2025"})
