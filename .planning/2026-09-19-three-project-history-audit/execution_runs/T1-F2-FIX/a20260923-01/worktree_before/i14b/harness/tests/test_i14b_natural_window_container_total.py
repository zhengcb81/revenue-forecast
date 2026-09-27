"""T1-F2-FIX: clock_source / claim.status / container carriers must be TOTAL.

Repair sources (frozen in ../oracle.md, written before any run):
  * F-1  J7 `clock_source` guard consumed a SET -> a container clock_source
         raised TypeError ("unhashable type") and destroyed the whole batch
         (T1-10-FIX decision sec 6, F-1 row; reviewer P4 did not name it).
  * F-2  calendar `claim.status` carrier read had no type guard -> a truthy
         non-object claim raised AttributeError and destroyed the batch.
         GREEN semantics = parent pre-freeze ruling: present-but-malformed =>
         FAIL-CLOSED structured refusal (unverifiable claim read as the
         strongest status, the UNCHANGED J11 line then refuses with the
         existing R-CLAIM-EXCEEDS when the facts fall short of complete);
         an ABSENT status key keeps its byte-identical original behaviour.
  * P4   container carriers `windows` / `sampled_at` / `ledger.{daily,weekly,
         monthly,alerts}` were not lists/dicts -> TypeError/ValueError killed
         the batch.  evidence-degraded normalisation at the classify() entry:
         normalised carriers can only DEGRADE the computed facts (attacker
         values never enter a computation), so over-claims still hit the
         existing refusal classes (oracle APPENDIX A.3/A.5).

Against the PRE-fix SUT (T1-10-FIX's fixed iso 064e5381...) this suite is RED:
TypeError/AttributeError/ValueError tracebacks on the container shapes and on
the batch test - that IS the defect proof.  Run:

  I14B_SUT=<sut> <python> -X utf8 -B -m pytest -p no:cacheprovider \
      --basetemp <scratch> -q harness/tests/test_i14b_natural_window_container_total.py

Timestamp-string malformed input (started_at="not-a-timestamp", sampled_at
containing bad strings) is OUT OF SCOPE here: that is F-3's track
(T1-F3-FIX), pending-routed per the card.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ATTEMPT = HARNESS.parent

SUT_PATH = Path(os.environ.get("I14B_SUT", str(ATTEMPT / "iso" / "natural_window.py")))

FROZEN_NOW = "2026-09-20T02:56:38Z"
CASES = json.loads((HARNESS / "cases.r2.json").read_text(encoding="utf-8"))
BY_ID = {c["case_id"]: c for c in CASES["cases"]}
F_C1, F_C2, F_C3 = BY_ID["C1"]["fields"], BY_ID["C2"]["fields"], BY_ID["C3"]["fields"]
CLAIM_C1, CLAIM_C2, CLAIM_C3 = BY_ID["C1"]["claim"], BY_ID["C2"]["claim"], BY_ID["C3"]["claim"]

GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}
EMPTY_LEDGER = {"daily": [], "weekly": [], "monthly": [], "alerts": []}
EMPTY_FIELDS = {"clock_source": "system_utc", "ledger": dict(EMPTY_LEDGER)}

R_SIM = ["R-SIMULATED-CLOCK"]
R_CLAIM = ["R-CLAIM-EXCEEDS"]
R_NOSAMPLES = ["R-NO-SAMPLES"]
C1_REF = ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-SAME-INSTANT"]
S8_REF = ["R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-SAME-INSTANT"]

TRUSTED_STRINGS = {"system_utc", "scheduler_trusted"}
REGISTERED_BASIS_NAMES = {"sample_span", "command_total", "observation_plus_quick_check",
                          "sum_of_windows", "union_of_windows"}


def _load():
    spec = importlib.util.spec_from_file_location("i14b_sut_container_total", SUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUT = _load()


def _parse(ts: str):
    from datetime import datetime, timezone
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _cal(cid: str, fields: dict, claim, claim_present: bool = True) -> dict:
    case = {"case_id": cid, "class": "calendar", "requirement_id": "C-1",
            "fields": json.loads(json.dumps(fields))}
    if claim_present:
        case["claim"] = json.loads(json.dumps(claim))
    return case


def _win(cid: str, fields: dict, claim) -> dict:
    return {"case_id": cid, "class": "window_accounting", "requirement_id": "W-1",
            "claim": json.loads(json.dumps(claim)),
            "fields": json.loads(json.dumps(fields))}


def _classify(case: dict) -> dict:
    return SUT.classify(case, _parse(FROZEN_NOW), 5.0, 5.0)


def _c3(**over) -> dict:
    f = json.loads(json.dumps(F_C3))
    f.update(over)
    return f


def _good(**over) -> dict:
    f = dict(GOOD_FIELDS)
    f.update(over)
    return f


UNION_1740 = {"basis": "union_of_windows", "natural_observation_seconds": 1740.0}
UNION_2220 = {"basis": "union_of_windows", "natural_observation_seconds": 2220.0}
UNION_2400 = {"basis": "union_of_windows", "natural_observation_seconds": 2400.0}
SAMPLE_1740 = {"basis": "sample_span", "natural_observation_seconds": 1740.0}
W_DICT = {"w1": {"window_id": "w1", "started_at": "2026-09-20T00:00:00Z",
                 "finished_at": "2026-09-20T00:29:00Z"}}
DAILY_ENTRY = {"run_id": "r1", "started_at": "2026-09-08T03:30:00Z", "ok": True,
               "report_sha256": "a" * 64}


# ---------------------------------------------------------------------------
# F-1: clock_source container -> clean J7 refusal; scalars byte-stable
# ---------------------------------------------------------------------------

CLOCK_CONTAINERS = {
    "list": ["system_utc"],
    "dict": {"source": "system_utc"},
    "nested": [["x"]],
}


@pytest.mark.parametrize("shape", sorted(CLOCK_CONTAINERS))
def test_container_clock_source_refused_not_crashing(shape):
    case = _cal("K-" + shape, _c3(clock_source=CLOCK_CONTAINERS[shape]), CLAIM_C3)
    got = _classify(case)                     # pre-fix: TypeError unhashable
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == R_SIM
    assert got["computed"]["clock_source"] == CLOCK_CONTAINERS[shape]


CLOCK_SCALARS = {
    "trusted": ("system_utc", "accept_claim", []),
    "untrusted_str": ("simulated_clock_advanced_by_7_days", "reject_claim", R_SIM),
    "int": (5, "reject_claim", R_SIM),
    "bool": (True, "reject_claim", R_SIM),
}


@pytest.mark.parametrize("name", sorted(CLOCK_SCALARS))
def test_scalar_clock_sources_keep_their_frozen_behaviour(name):
    value, verdict, refusals = CLOCK_SCALARS[name]
    fields = _c3(clock_source=value)
    if name == "trusted":
        pass                                    # key present with trusted value
    case = _cal("K-" + name, fields, CLAIM_C3)
    got = _classify(case)
    assert got["verdict"] == verdict
    assert got["refusals"] == refusals


def test_absent_clock_source_key_keeps_frozen_behaviour():
    fields = _c3()
    fields.pop("clock_source", None)
    got = _classify(_cal("K-absent", fields, CLAIM_C3))
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == R_SIM


def test_clock_membership_is_total_over_every_json_value_shape():
    shapes = ["system_utc", "scheduler_trusted", "simulated_x", "", None, 5, 1.5, True,
              [], {}, ["system_utc"], {"source": "system_utc"}, [["x"]]]
    for value in shapes:
        got = value in SUT.TRUSTED_CLOCKS       # pre-fix: TypeError for list/dict
        want = isinstance(value, str) and value in TRUSTED_STRINGS
        assert got == want, f"membership not total/equal for {value!r}"


# ---------------------------------------------------------------------------
# F-2: claim.status carrier  (parent pre-freeze ruling: fail-closed + missing != malformed)
# ---------------------------------------------------------------------------

MALFORMED_CARRIERS = {
    "list_on_empty": (EMPTY_FIELDS, ["pending"], True),
    "list_on_c2": (F_C2, ["pending"], True),
    "str": (F_C2, "pending", True),
    "int": (F_C2, 5, True),
    "bool": (F_C2, True, True),
}


@pytest.mark.parametrize("name", ["list_on_empty", "str", "int", "bool"])
def test_malformed_status_carrier_fails_closed_with_existing_code(name):
    fields, claim, present = MALFORMED_CARRIERS[name]
    f = json.loads(json.dumps(fields))
    f["clock_source"] = "system_utc"
    got = _classify(_cal("S-" + name, f, claim, claim_present=present))
    assert got["verdict"] == "reject_claim"     # pre-fix: AttributeError rc-4
    assert got["refusals"] == R_CLAIM           # J11, existing vocabulary


def test_malformed_status_carrier_on_c1_attack_facts_refused_with_all_codes():
    f = json.loads(json.dumps(F_C1))
    f["clock_source"] = "system_utc"
    got = _classify(_cal("S-c1", f, ["complete"]))
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == C1_REF            # fail-closed J11 joins the ledger codes


def test_malformed_status_carrier_over_complete_facts_is_accepted():
    # frozen boundary (oracle sec 3.3): complete facts support EVERY status claim,
    # and no vocabulary code refuses a claim the facts fully substantiate.
    f = json.loads(json.dumps(F_C3))
    f["clock_source"] = "system_utc"
    got = _classify(_cal("S-c3", f, ["pending"]))
    assert got["verdict"] == "accept_claim"
    assert got["refusals"] == []


MISSING_STATUS_CASES = {
    "empty_dict_c2": (F_C2, {}, True, "accept_claim", []),
    "unknown_key_c2": (F_C2, {"other": 1}, True, "accept_claim", []),
    "absent_key_c2": (F_C2, None, False, "accept_claim", []),
    "empty_dict_c1_attack": (F_C1, {}, True, "reject_claim", S8_REF),
    "original_c1": (F_C1, json.loads(json.dumps(CLAIM_C1)), True, "reject_claim", C1_REF),
    "original_c2": (F_C2, json.loads(json.dumps(CLAIM_C2)), True, "accept_claim", []),
}


@pytest.mark.parametrize("name", sorted(MISSING_STATUS_CASES))
def test_missing_status_key_keeps_original_byte_identical_behaviour(name):
    fields, claim, present, verdict, refusals = MISSING_STATUS_CASES[name]
    f = json.loads(json.dumps(fields))
    f["clock_source"] = "system_utc"
    got = _classify(_cal("MISS-" + name, f, claim, claim_present=present))
    assert got["verdict"] == verdict
    assert got["refusals"] == refusals
    # 缺键≠畸形: a missing status NEVER picks up the fail-closed R-CLAIM-EXCEEDS
    if name == "empty_dict_c1_attack":
        assert "R-CLAIM-EXCEEDS" not in got["refusals"]


# ---------------------------------------------------------------------------
# P4: windows / sampled_at / ledger containers  (evidence-degraded normalisation)
# ---------------------------------------------------------------------------

def test_windows_container_degrades_to_evidence_default_and_accepts_honest_claim():
    got = _classify(_win("P4-W1", _good(windows=json.loads(json.dumps(W_DICT))),
                         dict(UNION_1740)))
    assert got["verdict"] == "accept_claim"     # pre-fix: TypeError string indices
    assert got["refusals"] == []
    assert got["computed"]["union_seconds"] == 1740.0


def test_windows_container_overclaim_still_refused():
    # anti-weaponisation (oracle APPENDIX A.5): degraded windows can only LOWER
    # the supported ceiling, so an inflated claim hits J11.
    got = _classify(_win("P4-W2", _good(windows=json.loads(json.dumps(W_DICT))),
                         dict(UNION_2220)))
    assert got["verdict"] == "reject_claim"
    assert got["refusals"] == R_CLAIM


def test_sampled_at_container_is_refused_with_no_samples():
    got = _classify(_win("P4-S1", _good(sampled_at={"a": "2026-09-20T00:01:00Z"}),
                         dict(UNION_1740)))
    assert got["verdict"] == "reject_claim"     # pre-fix: Invalid isoformat 'a'
    assert got["refusals"] == R_NOSAMPLES
    assert got["computed"]["sample_count"] == 0


def test_ledger_container_with_complete_claim_is_refused():
    f = json.loads(json.dumps(F_C3))
    f["ledger"]["daily"] = {"d1": dict(DAILY_ENTRY)}
    got = _classify(_cal("P4-L1", f, CLAIM_C3))
    assert got["verdict"] == "reject_claim"     # pre-fix: TypeError string indices
    assert got["refusals"] == R_CLAIM
    assert got["computed"]["daily_count"] == 0
    assert got["computed"]["window_status"] == "pending"


def test_ledger_container_with_pending_claim_control_is_accepted():
    f = json.loads(json.dumps(F_C2))
    f["ledger"]["daily"] = {"d1": dict(DAILY_ENTRY)}
    got = _classify(_cal("P4-L2", f, CLAIM_C2))
    assert got["verdict"] == "accept_claim"
    assert got["refusals"] == []


def test_stable_container_neighbours_unchanged():
    # P4-STAB rows are STABILITY controls: a normal list carrier must keep the
    # verdict of the harness fixture it is modelled on (oracle.md APPENDIX A.2:
    # "windows 正常列表（W5 形，union 2400） -> rc=0 accept" and
    # "sampled_at 正常 30 串 -> rc=0 (W1 族原样)").  Building them from the
    # pinned cases.r2.json fixtures W5 / W1 is what makes the row exact --
    # a hand-rolled "_good(windows=...)" keeps quick_check inside the declared
    # window and therefore (correctly) trips the pre-existing J15 refusal,
    # which would measure the fixture, not the container repair.
    w5 = _classify(_win("P4-STAB-W", BY_ID["W5"]["fields"], BY_ID["W5"]["claim"]))
    assert w5["verdict"] == "accept_claim" and w5["refusals"] == []
    w1 = _classify(_win("P4-STAB-S", BY_ID["W1"]["fields"], BY_ID["W1"]["claim"]))
    assert w1["verdict"] == "accept_claim" and w1["refusals"] == []


def test_normal_carriers_are_byte_identical_semantics():
    # dict/list carriers take the original path: original C1/C2/C3 verdicts hold
    c1 = _classify(_cal("C1", F_C1, CLAIM_C1))
    assert c1["verdict"] == "reject_claim" and c1["refusals"] == C1_REF
    c2 = _classify(_cal("C2", F_C2, CLAIM_C2))
    assert c2["verdict"] == "accept_claim" and c2["refusals"] == []
    c3 = _classify(_cal("C3", F_C3, CLAIM_C3))
    assert c3["verdict"] == "accept_claim" and c3["refusals"] == []


# ---------------------------------------------------------------------------
# the adjudication machinery cannot be blown up by a single malformed case
# ---------------------------------------------------------------------------

def test_one_malformed_case_cannot_kill_the_batch(tmp_path):
    cases = [
        _win("W-GOOD", dict(GOOD_FIELDS), dict(UNION_1740)),
        _cal("C3-GOOD", F_C3, CLAIM_C3),
        _cal("C2-GOOD", F_C2, CLAIM_C2),
        _cal("BAD-F1", _c3(clock_source=["system_utc"]), CLAIM_C3),
        _cal("BAD-F2", F_C2, ["pending"]),
        _win("BAD-P4W", _good(windows=json.loads(json.dumps(W_DICT))), dict(UNION_2220)),
        _win("BAD-P4S", _good(sampled_at={"a": "2026-09-20T00:01:00Z"}),
             dict(UNION_1740)),
        _cal("BAD-P4L", {**json.loads(json.dumps(F_C3)),
                         "ledger": {**json.loads(json.dumps(F_C3))["ledger"],
                                    "daily": {"d1": dict(DAILY_ENTRY)}}}, CLAIM_C3),
    ]
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
    assert report["case_count"] == 8
    verdicts = {v["case_id"]: v for v in report["verdicts"]}
    assert verdicts["BAD-F1"]["refusals"] == R_SIM
    assert verdicts["BAD-F2"]["refusals"] == R_CLAIM
    assert verdicts["BAD-P4W"]["refusals"] == R_CLAIM
    assert verdicts["BAD-P4S"]["refusals"] == R_NOSAMPLES
    assert verdicts["BAD-P4L"]["refusals"] == R_CLAIM
    for cid in ("W-GOOD", "C3-GOOD", "C2-GOOD"):
        assert verdicts[cid]["verdict"] == "accept_claim"   # collateral = 0
    assert "internal_error" not in proc.stdout
    assert proc.stderr == ""


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
