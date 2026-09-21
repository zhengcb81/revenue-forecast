"""I-14-H acceptance tests -- the two product-level defects of natural_window.py.

Defect 1  claim.basis has no enumeration check: in the r1 revision every
          unregistered basis ('' / null / missing key / 'wall_clock' / a
          container) fell through the if/elif dispatch with allowed=None, so
          J1/J2/J3/J11 were all skipped and the claim was ACCEPTED.
          Fix: basis must belong to BASIS_REGISTRY, else R-BASIS-UNKNOWN (J16).
Defect 2  quick_check was appended to the observation intervals, so
          union_of_windows/sum_of_windows measured 2220 s (37 min) instead of
          1740 s (29 min) and the dishonest 2220 claim was ACCEPTED while the
          honest 1740 claim was REJECTED (direction inverted).
          Fix: observation intervals contain the observation phase only
          (quick_check never enters), plus J15 for the renamed-window variant.

Facts shared by all cases (W1 arithmetic): observation 00:00-00:29 = 1740 s,
quick_check 00:29-00:37 = 480 s, command total 00:00-00:37 = 2220 s.
1740 + 480 = 2220 is exactly the summing trap the oracle must refuse.

Subject under test comes from I14H_SUT (default: the fixed working copy
iso/natural_window.py, SUT_VERSION "i14b-after-2").  Point I14H_SUT at
before/natural_window.r1sut.py (sha256 495a4411..., the reviewed defective r1
revision) to reproduce RED: every defect test below fails there.

Run:
  C:\\Miniconda\\python.exe -X utf8 -B -m pytest -p no:cacheprovider \
      --basetemp harness/scratch/pytest-i14h -v harness/test_i14h_natural_window.py
"""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent

SUT_PATH = Path(os.environ.get("I14H_SUT", str(ATTEMPT / "iso" / "natural_window.py")))
FROZEN_NOW = datetime(2026, 9, 20, 2, 56, 38, tzinfo=timezone.utc)


def _load():
    spec = importlib.util.spec_from_file_location("i14h_sut", SUT_PATH)
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


def _run(fields: dict, claim: dict) -> dict:
    case = {"case_id": "I14H-T", "class": "window_accounting",
            "requirement_id": "SYNTHETIC-TIMER-ONLY(I-14-H#1,#2)",
            "claim": claim, "fields": fields}
    return SUT.classify(case, FROZEN_NOW, 5.0, 5.0)


def _claim(seconds, basis=..., status: str = "eligible") -> dict:
    claim = {"status": status, "natural_observation_seconds": seconds}
    if basis is not ...:
        claim["basis"] = basis
    return claim


# ---------------------------------------------------------------------------
# control (must pass on BOTH revisions: the harness itself is sound)
# ---------------------------------------------------------------------------

def test_w1_baseline_honest_sample_span_claim_accepted():
    out = _run(_w1_fields(), _claim(1740, "sample_span"))
    assert out["verdict"] == "accept_claim", out
    assert out["refusals"] == [], out
    assert out["computed"]["observation_span_seconds"] == 1740


# ---------------------------------------------------------------------------
# defect 1: claim.basis must be a closed enumeration (J16 / R-BASIS-UNKNOWN)
# ---------------------------------------------------------------------------

def test_d1_unknown_basis_name_rejected():
    out = _run(_w1_fields(), _claim(2220, "wall_clock"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


def test_d1_empty_string_basis_rejected():
    out = _run(_w1_fields(), _claim(99999, ""))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


def test_d1_null_basis_rejected():
    out = _run(_w1_fields(), _claim(2220, None))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


def test_d1_missing_basis_key_rejected():
    out = _run(_w1_fields(), _claim(99999))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out


def test_d1_registered_basis_still_judged_on_merits():
    """Negative control: a REGISTERED basis is not refused as unknown; it is
    still judged -- command total (2220) is not the observation (1740)."""
    out = _run(_w1_fields(), _claim(2220, "command_total"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-TOTAL-AS-OBS"], out


# ---------------------------------------------------------------------------
# defect 2: quick_check never counts toward the natural observation duration
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
    """J15 variant: renaming quick_check into a second declared window is the
    same defect -- the window covering the quick_check interval is refused."""
    windows = [
        {"started_at": "2026-09-19T00:00:00Z", "finished_at": "2026-09-19T00:29:00Z"},
        {"started_at": "2026-09-19T00:29:00Z", "finished_at": "2026-09-19T00:37:00Z"},
    ]
    out = _run(_w1_fields(windows=windows), _claim(2220, "union_of_windows"))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-QC-IN-OBS"], out
    assert out["computed"]["quick_check_overlap_seconds"] == 480, out


# ---------------------------------------------------------------------------
# known residual (reviewer P4 / T1-10 P-3, frozen as cases H5/H6): a container
# basis must be refused per case with R-BASIS-UNKNOWN, but i14b-after-2 raises
# TypeError (unhashable) and crashes the whole batch (rc 4), while r1 silently
# accepted it.  xfail documents the residual without blocking this suite.
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="residual P4/T1-10 P-3: i14b-after-2 crashes the batch "
                          "(TypeError, rc 4) on an unhashable container basis; r1 "
                          "silently accepted it; the oracle demands per-case "
                          "R-BASIS-UNKNOWN (frozen cases H5/H6)")
def test_container_basis_refused_per_case():
    out = _run(_w1_fields(), _claim(99999, ["union_of_windows"]))
    assert out["verdict"] == "reject_claim", out
    assert out["refusals"] == ["R-BASIS-UNKNOWN"], out
