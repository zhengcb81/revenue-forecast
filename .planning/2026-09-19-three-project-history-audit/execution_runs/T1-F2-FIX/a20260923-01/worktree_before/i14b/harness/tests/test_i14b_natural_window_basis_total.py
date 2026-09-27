"""T1-10-FIX: J16 `claim.basis` validation must be a TOTAL function.

Repair source (authoritative): M-T-REVIEW's T1-10 `changes_required` block,
`execution_runs/M-T-REVIEW/a20260923-01/landing_package/t1_review_flips.md` L28-40:

    补全 claim.basis 校验覆盖面至全部入口（…立修卡并带畸形 basis 负例族 +
    裁决机关不可被单例炸毁的负控）… 建议同步纳入 T1-8 续查的 fabricated-green 负控。

Defect (1) as recorded by T1-10/a20260920-01 (P-3..P-6) and I-14-B review.md P4
(L352-353): `BASIS_REGISTRY` was a `set`, so `basis not in BASIS_REGISTRY` RAISED
`TypeError: unhashable type` for a container basis instead of refusing the claim;
`main()` turned that into rc=4 with NO report, i.e. one malformed case destroyed
every other case's verdict -- the guard itself was the single point of failure.

Contract frozen by T1-10-FIX oracle.md sections 1-3:
  * every `claim.basis` input shape (E1 carrier read :199, E2 guard :202,
    E3 `basis_registered` :247) is total over all JSON values -- never raises;
  * a malformed basis is a CLEAN per-case refusal with the SAME semantics as the
    neighbouring scalar validation: `reject_claim` + `["R-BASIS-UNKNOWN"]` +
    `computed.basis_registered is False` (oracle.md sec 11.3, no new R-* codes);
  * a single malformed case can never kill the batch (rc stays 0, report written,
    every case decided).

Against the PRE-fix SUT (7fff6f0c...) this suite is RED: TypeError/AttributeError
tracebacks on B1/B2/B3/B11/B12* and on the registry-totality probe -- that IS the
defect-(1) proof.  Run:

  I14B_SUT=<sut> <iso-python> -X utf8 -B -m pytest -p no:cacheprovider \
      --basetemp <scratch> -q harness/tests/test_i14b_natural_window_basis_total.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ATTEMPT = HARNESS.parent

SUT_PATH = Path(os.environ.get("I14B_SUT", str(ATTEMPT / "iso" / "natural_window.py")))

FROZEN_NOW = "2026-09-20T02:56:38Z"          # T1-10 verify_t1_10.py FROZEN_NOW
# GOOD_FIELDS verbatim from T1-10/a20260920-01/scripts/verify_t1_10.py L99-106
GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}

# Oracle sec 1 shapes B1..B12: the malformed-basis negative family.
CLAIMS: dict[str, object] = {
    # -- crash shapes (RED before the fix, GREEN after) --------------------
    "B1":  {"basis": ["union_of_windows"], "natural_observation_seconds": 1740.0},  # array
    "B2":  {"basis": {"name": "union_of_windows"}, "natural_observation_seconds": 1740.0},  # object
    "B3":  ["union_of_windows"],         # carrier is an array: basis unreadable
    "B11": {"basis": [["x"]], "natural_observation_seconds": 1740.0},  # nested container
    "B12a": "s",                          # carrier truthy non-object: str
    "B12b": 5,                            # carrier truthy non-object: int
    "B12c": True,                         # carrier truthy non-object: bool
    # -- stable neighbours (frozen by oracle sec 11.3; must not change) ----
    "B4":  {"natural_observation_seconds": 1740.0},                      # missing-required
    "B5":  {"basis": "union_of_windows", "natural_observation_seconds": 1740.0,
            "unrelated": "x"},                                           # unknown-key
    "B6":  {"basis": "union_of_windows", "natural_observation_seconds": 1740.0},
    "B7":  {"basis": "wall_clock", "natural_observation_seconds": 1740.0},
    "B8":  {"basis": None, "natural_observation_seconds": 1740.0},
    "B9":  {"basis": 5, "natural_observation_seconds": 1740.0},
    "B10": {"basis": "", "natural_observation_seconds": 1740.0},
}

CRASH_SHAPES = ["B1", "B2", "B3", "B11", "B12a", "B12b", "B12c"]
SCALAR_NEIGHBOURS = ["B4", "B7", "B8", "B9", "B10"]

REGISTERED = {"sample_span", "command_total", "observation_plus_quick_check",
              "sum_of_windows", "union_of_windows"}


def _load():
    spec = importlib.util.spec_from_file_location("i14b_sut_basis_total", SUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUT = _load()


def _parse(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def _case(cid: str, claim: object) -> dict:
    return {
        "case_id": cid,
        "class": "window_accounting",
        "requirement_id": "W-1",
        "claim": claim,
        "fields": dict(GOOD_FIELDS),
    }


def _classify(cid: str) -> dict:
    return SUT.classify(_case(cid, CLAIMS[cid]), _parse(FROZEN_NOW), 5.0, 5.0)


# ---------------------------------------------------------------------------
# the malformed-basis negative family: refused, never crashed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cid", CRASH_SHAPES)
def test_malformed_basis_is_refused_not_crashing(cid: str):
    got = _classify(cid)
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-BASIS-UNKNOWN"]
    assert got["computed"]["basis_registered"] is False


@pytest.mark.parametrize("cid", CRASH_SHAPES)
def test_malformed_basis_refusal_matches_neighbouring_scalar_semantics(cid: str):
    # the same refusal set the scalar neighbours (wall_clock / null / 5 / "") get
    scalar = _classify("B7")
    got = _classify(cid)
    assert got["refusals"] == scalar["refusals"]
    assert got["verdict"] == scalar["verdict"]


@pytest.mark.parametrize("cid", SCALAR_NEIGHBOURS)
def test_scalar_and_missing_neighbours_keep_their_frozen_behaviour(cid: str):
    got = _classify(cid)
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == ["R-BASIS-UNKNOWN"]
    assert got["computed"]["basis_registered"] is False


def test_unknown_key_does_not_reject_an_otherwise_valid_claim():
    got = _classify("B5")
    assert got["verdict"] == "accept_claim"
    assert got["refusals"] == []


def test_registered_basis_control_is_accepted():
    got = _classify("B6")
    assert got["verdict"] == "accept_claim"
    assert got["computed"]["basis_registered"] is True


def test_registry_membership_is_total_over_every_json_value_shape():
    shapes = ["union_of_windows", "wall_clock", "", None, 5, 1.5, True,
              [], {}, ["union_of_windows"], {"name": "x"}, [["x"]], {"a": {"b": [1]}}]
    for value in shapes:
        # pre-fix: a list/dict probe raises TypeError right here (RED)
        got = value in SUT.BASIS_REGISTRY
        want = isinstance(value, str) and value in REGISTERED
        assert got == want, f"membership not total/equal for {value!r}"


# ---------------------------------------------------------------------------
# the adjudication machinery cannot be blown up by a single malformed case
# ---------------------------------------------------------------------------

def test_one_malformed_case_cannot_kill_the_batch(tmp_path):
    cases = [_case("GOOD-01", dict(CLAIMS["B6"])),
             _case("GOOD-02", dict(CLAIMS["B6"])),
             _case("BAD-LIST", CLAIMS["B1"]),
             _case("GOOD-03", dict(CLAIMS["B6"])),
             _case("BAD-CARRIER", CLAIMS["B3"])]
    cases_path = tmp_path / "cases.json"
    report_path = tmp_path / "report.json"
    cases_path.write_text(
        json.dumps({"frozen_now_utc": FROZEN_NOW, "cases": cases}),
        encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(SUT_PATH),
         "--cases", str(cases_path), "--report", str(report_path)],
        capture_output=True, text=True)

    # pre-fix: rc=4 and NO report at all (every case's verdict destroyed)
    assert proc.returncode == 0, f"rc={proc.returncode} stdout={proc.stdout!r}"
    assert report_path.exists(), "report must be written for the whole batch"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_count"] == 5                      # every case decided
    verdicts = {v["case_id"]: v for v in report["verdicts"]}
    assert verdicts["BAD-LIST"]["verdict"] == "reject_claim"
    assert verdicts["BAD-LIST"]["refusals"] == ["R-BASIS-UNKNOWN"]
    assert verdicts["BAD-CARRIER"]["verdict"] == "reject_claim"
    assert verdicts["BAD-CARRIER"]["refusals"] == ["R-BASIS-UNKNOWN"]
    for cid in ("GOOD-01", "GOOD-02", "GOOD-03"):
        assert verdicts[cid]["verdict"] == "accept_claim"  # collateral = 0
    assert "internal_error" not in proc.stdout
    assert proc.stderr == ""


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
