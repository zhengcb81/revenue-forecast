"""I-14-I rider suite -- discharging I-14-H's mandatory closing conditions.

I-14-H was accepted only CONDITIONALLY (review.md sha256 97997d6d..., section 5):
the 14-case end-to-end run_cases.py gate had NEVER passed, because

  (a) an unhashable container basis (list / dict) reached
      `if basis not in BASIS_REGISTRY:` at iso/natural_window.py:202, which
      hashes the value, raised TypeError: unhashable type, and aborted the WHOLE
      batch (CLI rc 4, no report written) instead of refusing the single case;
      the frozen expectations for H5/H6 demand per-case R-BASIS-UNKNOWN; and
  (b) `quick_check_in_observation_intervals` and `sum_used_for_natural_duration`
      were hardcoded `False` literals, so every assertion about them was
      tautological -- and in overlap scenarios the literal contradicted fact.

This suite is the pytest half of the discharge.  The end-to-end half is
`after/CMD-I14I-GATE-CASES14` (unmodified run_cases.py, unmodified 14 frozen
cases/expectations, rc 0) with `cases_report.json` landed in the I-14-H evidence
directory.

FACT BASE (W1 arithmetic, hand-derived, unchanged from I-14-H):
  observation 00:00-00:29 = 1740 s, quick_check 00:29-00:37 = 480 s,
  command total 00:00-00:37 = 2220 s.  1740 + 480 = 2220 is the summing trap.
Overlap scenario arithmetic (hand-derived for this card):
  windows [00:00-00:29] + [00:20-00:49] -> union 2940, sum 3480, window overlap
  540, and quick_check overlap 480 (the [00:20-00:49] window covers 00:29-00:37).

SCOPE: SYNTHETIC-TIMER-ONLY synthetic time input.  This suite grants nothing
about real natural observation, real UI immediacy, SLO/performance,
disclosure_adaptation or accuracy.

Subject under test comes from I14I_SUT (default: the fixed working copy
iso/natural_window.py).  Point it at before/natural_window.i14b-after-2.py to
reproduce RED (the pre-fix revision), or at before/natural_window.r1sut.py for
the do-not-regress arm (r1 silently ACCEPTED container bases).

Run:
  C:\\Miniconda\\python.exe -X utf8 -B -m pytest -p no:cacheprovider \\
      --basetemp harness/scratch/pytest-i14i-green -v harness/test_i14i_natural_window.py
"""

from __future__ import annotations

import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent

SUT_PATH = Path(os.environ.get("I14I_SUT", str(ATTEMPT / "iso" / "natural_window.py")))
FROZEN_NOW = datetime(2026, 9, 20, 2, 56, 38, tzinfo=timezone.utc)


def _load():
    spec = importlib.util.spec_from_file_location("i14i_sut", SUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUT = _load()


def _w1_fields(**overrides) -> dict:
    """W1-shaped synthetic facts: 29 min observation + 8 min quick_check."""
    fields = {
        "scheduled_at": "2026-09-18T23:45:00Z",
        "started_at": "2026-09-19T00:00:00Z",
        "sampled_at": ["2026-09-19T00:00:00Z", "2026-09-19T00:29:00Z"],
        "observation_finished_at": "2026-09-19T00:29:00Z",
        "quick_check_started_at": "2026-09-19T00:29:00Z",
        "quick_check_finished_at": "2026-09-19T00:37:00Z",
        "command_finished_at": "2026-09-19T00:37:00Z",
    }
    fields.update(overrides)
    return fields


def _overlap_fields(**overrides) -> dict:
    """Overlapping declared windows: [00:00-00:29] + [00:20-00:49].

    Hand arithmetic: union 2940, sum 3480, window overlap 540; the second window
    covers the whole quick_check interval, so quick_check overlap = 480.
    """
    fields = _w1_fields(
        sampled_at=["2026-09-19T00:00:00Z", "2026-09-19T00:20:00Z",
                    "2026-09-19T00:49:00Z"],
        observation_finished_at="2026-09-19T00:49:00Z",
        windows=[
            {"started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
            {"started_at": "2026-09-19T00:20:00Z", "finished_at": "2026-09-19T00:49:00Z"},
        ],
    )
    fields.update(overrides)
    return fields


def _renamed_window_fields() -> dict:
    """J15 rename variant: window B copies the quick_check span (frozen as H11/H12)."""
    return _w1_fields(windows=[
        {"started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
        {"started_at": "2026-09-19T00:29:00Z", "finished_at": "2026-09-19T00:37:00Z"},
    ])


def _run(fields: dict, claim: dict) -> dict:
    case = {"case_id": "I14I-T", "class": "window_accounting",
            "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-I#1,#2,#6)",
            "claim": claim, "fields": fields}
    return SUT.classify(case, FROZEN_NOW, 5.0, 5.0)


def _claim(seconds, basis=..., status: str = "eligible") -> dict:
    claim = {"status": status, "natural_observation_seconds": seconds}
    if basis is not ...:
        claim["basis"] = basis
    return claim


# ---------------------------------------------------------------------------
# controls: the harness itself is sound on BOTH revisions
# ---------------------------------------------------------------------------

def test_w1_baseline_honest_sample_span_claim_accepted():
    out = _run(_w1_fields(), _claim(1740, "sample_span"))
    assert out["verdict"] == "accept_claim", out
    assert out["refusals"] == [], out
    assert out["computed"]["observation_span_seconds"] == 1740


def test_d1_registered_basis_still_judged_on_merits():
    """Negative control (frozen as H7): a REGISTERED basis must NOT be refused by
    the new type guard; it is still judged -- the command total (2220) is not the
    observation (1740)."""
    out = _run(_w1_fields(), _claim(2220, "command_total"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-TOTAL-AS-OBS"], out
    assert "R-BASIS-UNKNOWN" not in out["refusals"], out


def test_d1_registered_string_basis_not_over_refused():
    """Negative control N1: the type guard must not turn a registered string
    basis into a refusal -- an honest 1740 union claim stays ACCEPTED."""
    out = _run(_w1_fields(), _claim(1740, "union_of_windows"))
    assert out["verdict"] == "accept_claim", out
    assert out["refusals"] == [], out
    assert out["computed"]["basis_registered"] is True, out


# ---------------------------------------------------------------------------
# defect 1 (scalar): claim.basis must be a closed enumeration (J16)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("basis,label", [
    ("wall_clock", "unregistered name"),
    ("", "empty string"),
])
def test_d1_unknown_string_basis_rejected(basis, label):
    out = _run(_w1_fields(), _claim(2220, basis))
    assert out["verdict"] == "reject_claim", (label, out)
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], (label, out)


def test_d1_null_basis_rejected():
    out = _run(_w1_fields(), _claim(2220, None))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


def test_d1_missing_basis_key_rejected():
    out = _run(_w1_fields(), _claim(99999))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


# ---------------------------------------------------------------------------
# THE RIDER (card items 1-4): a container basis must be refused PER CASE, not
# crash the batch.  I-14-H's xfail is GONE -- this is now a real pass.
#
# Measured pre-fix boundary (oracle.md section 1, before/CMD-I14I-PREFIX-PROBE):
#   list  (incl. nested) -> TypeError: unhashable type: 'list' at :202
#   dict  (incl. nested) -> TypeError: unhashable type: 'dict' at :202
#   set / tuple          -> already reached R-BASIS-UNKNOWN (hashable), frozen
#                           here explicitly so "accidentally correct" is not
#                           mistaken for covered
#   int / float / bool   -> already reached R-BASIS-UNKNOWN (hashable scalar)
# The crash is list/dict-SPECIFIC, not container-general.  Every row is frozen
# separately so neither over- nor under-fitting can hide here.
# ---------------------------------------------------------------------------

CONTAINER_BASES = [
    pytest.param(["union_of_windows"], id="list-of-one-registered-name"),
    pytest.param({"kind": "union_of_windows"}, id="dict-kind"),
    pytest.param(["union_of_windows", "sample_span"], id="list-two-elements"),
    pytest.param({"kind": ["union_of_windows"]}, id="nested-list-in-dict"),
    pytest.param([{"kind": "union_of_windows"}], id="nested-dict-in-list"),
    pytest.param({"union_of_windows"}, id="set"),
    pytest.param(("union_of_windows",), id="tuple"),
    pytest.param([], id="empty-list"),
    pytest.param({}, id="empty-dict"),
    pytest.param(0, id="int-zero"),
    pytest.param(1.0, id="float-one"),
    pytest.param(True, id="bool-true"),
]


@pytest.mark.parametrize("basis", CONTAINER_BASES)
def test_container_basis_refused_per_case(basis):
    """Frozen as cases H5/H6 in the end-to-end gate.  Pre-fix this raised
    TypeError (list/dict) or silently accepted (r1) -- never a per-case refusal."""
    out = _run(_w1_fields(), _claim(99999, basis))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out
    assert out["computed"]["basis_registered"] is False, out


@pytest.mark.parametrize("basis", CONTAINER_BASES)
def test_container_basis_does_not_break_report_serialisation(basis):
    """Ancillary defect found while bounding the rider: `computed["basis"]` used to
    echo the raw claim value, and a `set` basis made json.dumps(report) raise
    TypeError at the WRITE step -- i.e. even a correctly decided case could still
    abort the batch.  A per-case refusal is only real if the report can be written."""
    out = _run(_w1_fields(), _claim(99999, basis))
    encoded = json.dumps(out["computed"])          # must not raise
    assert isinstance(encoded, str)
    echo = out["computed"]["basis"]
    assert echo is None or isinstance(echo, str), out["computed"]["basis"]


def test_container_basis_does_not_abort_the_rest_of_the_batch():
    """The rider's actual point: one poisoned case must not stop the others."""
    cases = []
    for index, basis in enumerate([["union_of_windows"], {"kind": "x"}, ["a"]]):
        cases.append({"case_id": f"B{index}", "class": "window_accounting",
                      "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-I#1)",
                      "claim": _claim(99999, basis), "fields": _w1_fields()})
    cases.append({"case_id": "OK", "class": "window_accounting",
                  "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-I#1)",
                  "claim": _claim(1740, "union_of_windows"), "fields": _w1_fields()})
    verdicts = [SUT.classify(c, FROZEN_NOW, 5.0, 5.0) for c in cases]
    assert [v["case_id"] for v in verdicts] == ["B0", "B1", "B2", "OK"]
    assert all(v["refusals"] == ["R-BASIS-UNKNOWN"] for v in verdicts[:3]), verdicts
    assert verdicts[3]["verdict"] == "accept_claim", verdicts[3]


# ---------------------------------------------------------------------------
# defect 2 (unchanged from I-14-H, kept here so the merged suite is self-contained)
# ---------------------------------------------------------------------------

def test_d2_observation_intervals_contain_observation_only():
    out = _run(_w1_fields(), _claim(1740, "union_of_windows"))
    got = out["computed"]
    assert got["union_seconds"] == 1740, got          # r1 measured 2220
    assert got["sum_seconds"] == 1740, got
    assert got["observation_interval_count"] == 1, got
    assert got["quick_check_in_observation_intervals"] is False, got
    assert got["quick_check_overlap_seconds"] == 0, got


def test_d2_honest_1740_union_claim_accepted():
    out = _run(_w1_fields(), _claim(1740, "union_of_windows"))
    assert out["verdict"] == "accept_claim", out      # r1 rejected the honest claim
    assert out["refusals"] == [], out


def test_d2_dishonest_2220_union_claim_rejected():
    out = _run(_w1_fields(), _claim(2220, "union_of_windows"))
    assert out["verdict"] == "reject_claim", out      # r1 accepted 2220
    assert out["refusals"] == ["R-CLAIM-EXCEEDS"], out


def test_d2_dishonest_2220_sum_claim_rejected():
    out = _run(_w1_fields(), _claim(2220, "sum_of_windows"))
    assert out["verdict"] == "reject_claim", out      # r1 accepted 2220
    assert out["refusals"] == ["R-CLAIM-EXCEEDS"], out


def test_d2_renamed_quick_check_window_rejected():
    """J15 variant (frozen as H11): renaming quick_check into a second declared
    window is the same defect -- the window covering the quick_check interval is
    refused."""
    out = _run(_renamed_window_fields(), _claim(2220, "union_of_windows"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-QC-IN-OBS"], out
    assert out["computed"]["quick_check_overlap_seconds"] == 480, out
    assert out["computed"]["union_seconds"] == 2220, out


def test_d2_renamed_window_honest_claim_double_refusal():
    """Frozen as H12, which has NO other pytest counterpart (I-14-H carried
    finding CF-I14H-3).  Honest 1740 s claim + a window that covers quick_check:
    BOTH the claim-exceeds judgement and the J15 judgement must fire."""
    out = _run(_renamed_window_fields(), _claim(1740, "union_of_windows"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-CLAIM-EXCEEDS", "R-QC-IN-OBS"], out
    assert out["computed"]["quick_check_overlap_seconds"] == 480, out
    assert out["computed"]["union_seconds"] == 2220, out


# ---------------------------------------------------------------------------
# defect 3 (card item 6): the two output keys must be DERIVED, not literals.
#
# Pre-fix both were the literal `False`, so every assertion about them was
# tautological AND, in overlap scenarios, the reported value contradicted fact.
# The four scenarios below take the (quick_check_in_observation_intervals,
# sum_used_for_natural_duration) pair through all four combinations
# (F,F) (T,T) (T,F) (F,T), so each key is independently fail-able and neither can
# impersonate the other.
# ---------------------------------------------------------------------------

def test_d3_baseline_shape_reports_both_keys_false():
    """(False, False): no overlap in the measured intervals, and the basis is not
    the sum.  Frozen as W1 in the end-to-end gate."""
    got = _run(_w1_fields(), _claim(1740, "sample_span"))["computed"]
    assert got["quick_check_overlap_seconds"] == 0, got
    assert got["quick_check_in_observation_intervals"] is False, got
    assert got["sum_used_for_natural_duration"] is False, got


def test_d3_renamed_window_reports_quick_check_inside_observation():
    """(True, False): THIS is the scenario the reviewer named as contrary to fact
    -- union_seconds 2220, quick_check overlap 480, two intervals, yet the field
    reported False.  Frozen as H11/H12."""
    got = _run(_renamed_window_fields(), _claim(2220, "union_of_windows"))["computed"]
    assert got["union_seconds"] == 2220, got
    assert got["observation_interval_count"] == 2, got
    assert got["quick_check_overlap_seconds"] == 480, got
    assert got["quick_check_in_observation_intervals"] is True, got
    assert got["sum_used_for_natural_duration"] is False, got


def test_d3_overlapping_sum_claim_reports_both_keys_true():
    """(True, True): overlapping declared windows AND the sum taken as the basis.
    union 2940 / sum 3480 / window overlap 540 / quick_check overlap 480."""
    out = _run(_overlap_fields(), _claim(3480, "sum_of_windows"))
    got = out["computed"]
    assert got["union_seconds"] == 2940, got
    assert got["sum_seconds"] == 3480, got
    assert got["overlap_seconds"] == 540, got
    assert got["quick_check_overlap_seconds"] == 480, got
    assert got["quick_check_in_observation_intervals"] is True, got
    assert got["sum_used_for_natural_duration"] is True, got
    assert "R-SUM-OVERLAP" in out["refusals"], out


def test_d3_overlapping_union_claim_reports_overlap_only():
    """(True, False): same overlapping windows, but the union is the basis -- so
    the sum was NOT used for the natural duration."""
    got = _run(_overlap_fields(), _claim(2940, "union_of_windows"))["computed"]
    assert got["union_seconds"] == 2940, got
    assert got["quick_check_in_observation_intervals"] is True, got
    assert got["sum_used_for_natural_duration"] is False, got


def test_d3_disjoint_sum_claim_reports_sum_used_without_overlap():
    """(False, True): the boundary proving the two keys do not imply each other.
    Disjoint windows [00:00-00:29] + [01:00-01:29]: no quick_check overlap, but
    the sum WAS consumed as the natural duration."""
    fields = _w1_fields(
        sampled_at=["2026-09-19T00:00:00Z", "2026-09-19T00:29:00Z",
                    "2026-09-19T01:29:00Z"],
        observation_finished_at="2026-09-19T01:29:00Z",
        windows=[
            {"started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
            {"started_at": "2026-09-19T01:00:00Z", "finished_at": "2026-09-19T01:29:00Z"},
        ],
    )
    got = _run(fields, _claim(3480, "sum_of_windows"))["computed"]
    assert got["sum_seconds"] == 3480, got
    assert got["union_seconds"] == 3480, got
    assert got["overlap_seconds"] == 0, got
    assert got["quick_check_overlap_seconds"] == 0, got
    assert got["quick_check_in_observation_intervals"] is False, got
    assert got["sum_used_for_natural_duration"] is True, got


def test_d3_sum_key_is_false_when_sum_basis_is_not_registered():
    """The flag tracks "was the sum consumed as the natural duration", not "does
    the string 'sum_of_windows' appear somewhere": an unregistered basis never
    reaches the sum branch, and a container basis is not a registered name."""
    got = _run(_w1_fields(), _claim(99999, ["sum_of_windows"]))["computed"]
    assert got["basis_registered"] is False, got
    assert got["sum_used_for_natural_duration"] is False, got


def test_d3_keys_are_booleans_not_truthy_strings():
    """Guard against a lazy derivation that would satisfy `== False` / `== True`
    comparisons while reporting a non-boolean to downstream readers."""
    for fields, claim in (
        (_w1_fields(), _claim(1740, "sample_span")),
        (_renamed_window_fields(), _claim(2220, "union_of_windows")),
        (_overlap_fields(), _claim(3480, "sum_of_windows")),
    ):
        got = _run(fields, claim)["computed"]
        assert type(got["quick_check_in_observation_intervals"]) is bool, got
        assert type(got["sum_used_for_natural_duration"]) is bool, got
