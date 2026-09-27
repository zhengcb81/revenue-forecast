"""I-14-B acceptance suite r2 -- the independent review's blocking findings.

r2 adds tests for the two findings that made the r1 review return
`changes_required`, plus the sibling hole and the two coverage gaps the reviewer
recorded:

  P1  the claim's basis is a closed enumeration          (X1-X4)
  P2  quick_check is never part of the observation union (X5-X9)
  sibling: no declared observation interval -> unmeasured (X10, X11)
  coverage: weekly stale / monthly stale must be refused  (X12, X13)
  P3-a: a second run on the same UTC day is ignored, visibly (X14)

The r1 suite is preserved at harness/archive/test_i14b_natural_window.r1.py and
still passes unchanged against the r2 revision.

Subject under test comes from I14B_SUT (default iso/natural_window.py).

Run:
  <iso-python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <scratch> -q \
      harness/tests/test_i14b_natural_window.r2.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ATTEMPT = HARNESS.parent

SUT_PATH = Path(os.environ.get("I14B_SUT", str(ATTEMPT / "iso" / "natural_window.py")))
CASES = json.loads((HARNESS / "cases.r2.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((HARNESS / "frozen_expectations.r2.json").read_text(encoding="utf-8"))
FROZEN_NOW = CASES["frozen_now_utc"]
BY_ID = {c["case_id"]: c for c in CASES["cases"]}


def _load():
    spec = importlib.util.spec_from_file_location("i14b_sut_r2", SUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUT = _load()


def _parse(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def classify(case_id: str, tol: float = 5.0, cap_tol: float = 5.0) -> dict:
    return SUT.classify(BY_ID[case_id], _parse(FROZEN_NOW), tol, cap_tol)


# ---------------------------------------------------------------------------
# the whole r2 frozen set
# ---------------------------------------------------------------------------

def test_all_thirty_four_frozen_cases_match_the_r2_expectations():
    bad = []
    for case_id, exp in EXPECTED["expected"].items():
        got = classify(case_id)
        if got["verdict"] != exp["verdict"] or sorted(got["refusals"]) != sorted(exp["refusals"]):
            bad.append((case_id, exp["verdict"], got["verdict"], exp["refusals"], got["refusals"]))
    assert bad == []
    assert len(EXPECTED["expected"]) == 34


def test_r1_cases_are_byte_identical_copies_not_edits():
    r1_path = HARNESS / "archive" / "cases.r1.json"
    exp_r1_path = HARNESS / "archive" / "frozen_expectations.r1.json"
    r1 = json.loads(r1_path.read_text(encoding="utf-8"))
    r2_first = CASES["cases"][:len(r1["cases"])]
    assert json.dumps(r2_first, sort_keys=True) == json.dumps(r1["cases"], sort_keys=True)
    # the recorded pre-image hashes must match the archived r1 bytes
    assert hashlib.sha256(r1_path.read_bytes()).hexdigest() == CASES["r1_pre_image_sha256"]
    assert hashlib.sha256(exp_r1_path.read_bytes()).hexdigest() == EXPECTED["r1_pre_image_sha256"]


def test_the_corrected_r1_value_is_retained_not_erased():
    superseded = EXPECTED["expected_superseded"]["W1"]["computed.union_seconds"]
    assert superseded["old"] == 2220, "the r1 value must be preserved verbatim"
    assert superseded["new"] == 1740
    assert superseded["pre_image_sha256"] == EXPECTED["r1_pre_image_sha256"]
    assert EXPECTED["expected"]["W1"]["computed"]["union_seconds"] == 1740


# ---------------------------------------------------------------------------
# P2: the natural observation union is observation-only
# ---------------------------------------------------------------------------

def test_w1_union_excludes_quick_check():
    computed = classify("W1")["computed"]
    assert computed["union_seconds"] == 1740
    assert computed["sum_seconds"] == 1740
    assert computed["observation_interval_count"] == 1
    assert computed["quick_check_seconds"] == 480
    assert computed["quick_check_overlap_seconds"] == 0
    assert computed["quick_check_in_observation_intervals"] is False
    # 1740 != 2220: the 37-minute command total is not the observation
    assert computed["command_total_seconds"] == 2220
    assert computed["union_seconds"] != computed["command_total_seconds"]


def test_honest_1740_claim_under_union_of_windows_is_now_supported():
    got = classify("X5")
    assert got["verdict"] == "accept_claim"
    assert got["refusals"] == []


def test_thirty_seven_minutes_cannot_be_claimed_as_the_observation():
    for case_id in ("X6", "X7"):
        got = classify(case_id)
        assert got["verdict"] == "reject_claim", case_id
        assert got["refusals"] == ["R-CLAIM-EXCEEDS"], case_id
        assert got["computed"]["union_seconds"] == 1740, case_id


def test_a_window_that_copies_the_quick_check_span_is_refused():
    for case_id in ("X8", "X9"):
        got = classify(case_id)
        assert got["verdict"] == "reject_claim", case_id
        assert "R-QC-IN-OBS" in got["refusals"], case_id
        assert got["computed"]["quick_check_overlap_seconds"] == 480, case_id


# ---------------------------------------------------------------------------
# P1: the basis enumeration is closed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case_id", ["X1", "X2", "X3", "X4"])
def test_unregistered_basis_is_refused(case_id):
    got = classify(case_id)
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-BASIS-UNKNOWN"]
    assert got["computed"]["basis_registered"] is False


def test_registered_basis_set_is_exactly_the_five_frozen_values():
    assert sorted(SUT.BASIS_REGISTRY) == [
        "command_total", "observation_plus_quick_check", "sample_span",
        "sum_of_windows", "union_of_windows",
    ]


def test_every_registered_basis_still_reaches_its_own_judgement():
    # negative control: the enumeration does not turn the classifier into a blanket reject
    assert classify("W1")["refusals"] == []                      # sample_span, honest
    assert classify("W2")["refusals"] == ["R-TOTAL-AS-OBS"]       # command_total
    assert classify("W3")["refusals"] == ["R-QC-IN-OBS"]          # observation_plus_quick_check
    assert classify("X6")["refusals"] == ["R-CLAIM-EXCEEDS"]      # union_of_windows
    assert classify("X7")["refusals"] == ["R-CLAIM-EXCEEDS"]      # sum_of_windows


# ---------------------------------------------------------------------------
# sibling hole: no declared observation interval is unmeasured, not zero
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("case_id", ["X10", "X11"])
def test_absent_observation_interval_is_unmeasured(case_id):
    got = classify(case_id)
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-NO-INTERVAL"]
    assert got["computed"]["observation_interval_count"] == 0
    assert got["computed"]["observation_span_seconds"] is None


# ---------------------------------------------------------------------------
# coverage gaps recorded by the reviewer
# ---------------------------------------------------------------------------

def test_stale_weekly_window_cannot_be_claimed_complete():
    got = classify("X12")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS"]
    assert got["computed"]["weekly_count"] == 0
    assert got["computed"]["daily_count"] == 7


def test_stale_monthly_window_cannot_be_claimed_complete():
    got = classify("X13")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS"]
    assert got["computed"]["monthly_count"] == 0
    assert got["computed"]["weekly_count"] == 2


def test_second_run_on_the_same_utc_day_is_ignored_and_reported():
    got = classify("X14")
    assert got["computed"]["daily_count"] == 6
    assert got["computed"]["daily_same_day_runs_dropped"] == 1
    assert got["verdict"] == "reject_claim"  # 6 < 7, so the complete claim still fails


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
