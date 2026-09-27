"""I-14-B frozen acceptance suite (hand-written assertions from oracle.md).

The suite is independent of the runner: it asserts the oracle values directly,
including the two numbers the card freezes (observation 29 min vs command total
37 min) and the overlap counterexample (union 2400 s vs sum 2940 s).

The subject under test is selected by the I14B_SUT environment variable, so the
SAME command can be pointed at the BEFORE revision (expected: failures) and the
AFTER revision (expected: pass).

Run:
  <iso-python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <scratch> -q \
      harness/tests/test_i14b_natural_window.py
"""

from __future__ import annotations

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
CASES = json.loads((HARNESS / "cases.json").read_text(encoding="utf-8"))
FROZEN_NOW = CASES["frozen_now_utc"]
BY_ID = {c["case_id"]: c for c in CASES["cases"]}


def _load():
    spec = importlib.util.spec_from_file_location("i14b_sut", SUT_PATH)
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
# the card's frozen timing oracle: observation 29 min, NOT 37
# ---------------------------------------------------------------------------

def test_synthetic_window_observation_is_29_minutes_not_37():
    got = classify("W1")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["observation_span_seconds"] == 29 * 60 == 1740
    assert got["computed"]["quick_check_seconds"] == 8 * 60 == 480
    assert got["computed"]["command_total_seconds"] == 37 * 60 == 2220
    assert got["computed"]["sample_count"] == 30
    # 1740 + 480 == 2220 is the arithmetic coincidence that makes adding tempting
    assert (got["computed"]["observation_span_seconds"]
            + got["computed"]["quick_check_seconds"]
            == got["computed"]["command_total_seconds"])


def test_fields_are_reported_separately_and_never_collapsed():
    computed = classify("W1")["computed"]
    for key in ("scheduled_at", "started_at", "first_sampled_at", "last_sampled_at",
                "observation_finished_at", "observation_span_seconds",
                "quick_check_seconds", "command_total_seconds"):
        assert key in computed, f"missing separated field {key}"
    assert computed["scheduled_at"] != computed["observation_finished_at"]
    assert computed["sum_used_for_natural_duration"] is False


def test_command_total_may_not_be_called_the_observation():
    got = classify("W2")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-TOTAL-AS-OBS"]
    assert got["computed"]["observation_span_seconds"] == 1740


def test_quick_check_may_not_be_added_to_the_observation():
    got = classify("W3")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-QC-IN-OBS"]


# ---------------------------------------------------------------------------
# overlapping windows are never summed
# ---------------------------------------------------------------------------

def test_overlapping_windows_are_summed_by_the_cheat_and_refused():
    got = classify("W4")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-SUM-OVERLAP"]
    assert got["computed"]["sum_seconds"] == 2940
    assert got["computed"]["union_seconds"] == 2400
    assert got["computed"]["overlap_seconds"] == 540 == 9 * 60
    assert got["computed"]["union_seconds"] != got["computed"]["sum_seconds"]


def test_overlapping_windows_union_is_accepted():
    got = classify("W5")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["union_seconds"] == 2400
    assert got["computed"]["sum_seconds"] == 2940  # reported, never used


def test_single_sample_is_unmeasured_not_zero():
    got = classify("W6")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-NO-SAMPLES"]
    assert got["computed"]["observation_span_seconds"] is None


def test_sample_outside_the_window_is_not_counted():
    got = classify("W7")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-SAMPLE-OUTSIDE"]
    assert got["computed"]["observation_span_seconds"] == 1740
    assert got["computed"]["samples_outside_window"] == 1


# ---------------------------------------------------------------------------
# calendar: the historical attack and the pending rule
# ---------------------------------------------------------------------------

def test_historical_attack_7_ids_one_future_instant_empty_hashes_is_refused():
    got = classify("C1")
    assert got["verdict"] == "reject_claim"
    assert got["computed"]["daily_count"] == 0
    assert got["computed"]["window_status"] == "pending"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE",
                               "R-FUTURE-CLOCK", "R-SAME-INSTANT"]


def test_incomplete_window_stays_pending_and_is_accepted_as_pending():
    got = classify("C2")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["daily_count"] == 5
    assert got["computed"]["window_status"] == "pending"
    assert got["refusals"] == []


def test_synthetic_ledger_satisfying_every_rule_reaches_complete():
    # SYNTHETIC fixture only: proves the algorithm, grants no real observation
    got = classify("C3")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["daily_count"] == 7
    assert got["computed"]["weekly_count"] == 2
    assert got["computed"]["monthly_count"] == 1
    assert got["computed"]["alert_count"] == 1
    assert got["computed"]["window_status"] == "complete"


def test_claiming_complete_with_six_days_is_refused():
    got = classify("C4")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS"]
    assert got["computed"]["daily_count"] == 6


def test_simulated_clock_cannot_complete_a_window():
    got = classify("C5")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-SIMULATED-CLOCK"]
    assert got["computed"]["window_status"] == "complete"  # records alone


def test_duplicate_run_id_does_not_count_twice():
    got = classify("C6")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS", "R-DUP-RUN-ID"]
    assert got["computed"]["daily_count"] == 6


def test_empty_evidence_hash_does_not_count():
    got = classify("C7")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE"]
    assert got["computed"]["daily_count"] == 0


# ---------------------------------------------------------------------------
# login anchors 30/60/120
# ---------------------------------------------------------------------------

def test_honest_anchor_labels_are_accepted():
    got = classify("L1")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["label_offsets_seconds"] == [30, 60, 120]
    assert got["computed"]["label_offset_max_error_seconds"] == 0
    assert got["computed"]["capture_latency_max_seconds"] == 1


def test_cumulative_waits_29_88_207_are_not_anchor_instants():
    got = classify("L2")
    assert got["verdict"] == "reject_claim"
    assert got["computed"]["label_offsets_seconds"] == [29, 88, 207]
    assert got["computed"]["label_offset_max_error_seconds"] == 87 == abs(207 - 120)


def test_post_hoc_log_cannot_be_passed_off_as_immediate_capture():
    got = classify("L3")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-POSTHOC-CAPTURE"]
    assert got["computed"]["capture_latency_max_seconds"] == 3600


def test_one_snapshot_relabelled_three_times_is_refused():
    got = classify("L4")
    assert got["verdict"] == "reject_claim"
    assert got["computed"]["label_offsets_seconds"] == [30, 30, 30]
    assert got["computed"]["label_offset_max_error_seconds"] == 90
    assert got["refusals"] == ["R-LABEL-ANCHOR", "R-SAME-INSTANT"]


def test_labels_must_share_one_anchor_event():
    got = classify("L5")
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-ANCHOR-NOT-SHARED"]


# ---------------------------------------------------------------------------
# tolerance is an input, and the historical pattern is rejected across a range
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tol", [0, 1, 2, 5, 10, 20, 30, 60, 86])
def test_cumulative_wait_refusal_is_tolerance_stable_below_87(tol):
    assert classify("L2", tol=tol)["verdict"] == "reject_claim"


def test_the_refusal_is_a_real_threshold_not_a_blanket_reject():
    assert classify("L2", tol=87)["verdict"] == "accept_claim"


def test_posthoc_refusal_is_tolerance_independent():
    for tol in (0, 5, 87, 600):
        assert classify("L2b", tol=tol)["verdict"] == "reject_claim"
        assert classify("L3", tol=tol)["verdict"] == "reject_claim"


def test_all_twenty_frozen_cases_match_the_frozen_expectations():
    expected = json.loads((HARNESS / "frozen_expectations.json").read_text(encoding="utf-8"))
    bad = []
    for case_id, exp in expected["expected"].items():
        got = classify(case_id)
        if got["verdict"] != exp["verdict"] or sorted(got["refusals"]) != sorted(exp["refusals"]):
            bad.append((case_id, exp["verdict"], got["verdict"], exp["refusals"], got["refusals"]))
    assert bad == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
