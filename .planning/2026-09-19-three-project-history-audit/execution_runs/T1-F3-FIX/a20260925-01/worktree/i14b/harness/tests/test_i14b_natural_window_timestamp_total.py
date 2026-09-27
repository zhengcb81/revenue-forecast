"""T1-F3-FIX: the timestamp parser `_parse` must be a TOTAL function.

Repair authority (frozen in ../../../../../T1-F3-FIX/a20260925-01/oracle.md before
any run): I-14-B oracle.md section 11.8, third bullet:

    时间戳畸形（`_parse` 抛 `ValueError`，如 `started_at="not-a-timestamp"`）
    -> `reject_claim` + 新码 `R-TIMESTAMP-MALFORMED`（本节为该码的唯一授权来源；
    词表自 16 码增至 17 码），无法解析的时间字段在 `computed` 中置 `null`，
    其余派生量按可得事实计算。

Before the fix a single present-but-malformed timestamp field made `_parse`
raise `ValueError: Invalid isoformat string`, which escaped classify() into
main()'s internal-error handler: rc=4, NO report file, the WHOLE batch left
with 0 adjudications - the same verdict-stripping shape as defect (1).

Against the PRE-fix SUT (T1-F2-FIX's fixed iso 9b1ebda2...) every TS-* test
below is RED (rc=4 / no report / uncaught ValueError) - that IS the defect
proof.  Run:

  I14B_SUT=<sut> <python> -X utf8 -B -m pytest -p no:cacheprovider \
      --basetemp <scratch> -q harness/tests/test_i14b_natural_window_timestamp_total.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
ATTEMPT = HARNESS.parent

SUT_PATH = Path(os.environ.get("I14B_SUT", str(ATTEMPT / "iso" / "natural_window.py")))

FROZEN_NOW = "2026-09-20T02:56:38Z"
BAD = "not-a-timestamp"

CASES = json.loads((HARNESS / "cases.r2.json").read_text(encoding="utf-8"))
BY_ID = {c["case_id"]: c for c in CASES["cases"]}
F_C1, F_C2, F_C3 = BY_ID["C1"]["fields"], BY_ID["C2"]["fields"], BY_ID["C3"]["fields"]
CLAIM_C1, CLAIM_C3 = BY_ID["C1"]["claim"], BY_ID["C3"]["claim"]

# verbatim from test_i14b_natural_window_container_total.py:50-63
GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}

SAMPLE_SPAN_1680 = {"basis": "sample_span", "natural_observation_seconds": 1680}
UNION_1740 = {"basis": "union_of_windows", "natural_observation_seconds": 1740}

DAILY = [
    {"run_id": "T2-2026-09-11", "started_at": "2026-09-11T03:30:00Z",
     "ok": True, "report_sha256": "d1b0"},
    {"run_id": "T2-2026-09-12", "started_at": "2026-09-12T03:30:00Z",
     "ok": True, "report_sha256": "d1b1"},
    {"run_id": "T2-2026-09-13", "started_at": "2026-09-13T03:30:00Z",
     "ok": True, "report_sha256": "d1b2"},
    {"run_id": "T2-2026-09-14", "started_at": "2026-09-14T03:30:00Z",
     "ok": True, "report_sha256": "d1b3"},
    {"run_id": "T2-2026-09-15", "started_at": BAD,
     "ok": True, "report_sha256": "d1b4"},
]

LOGIN_FIELDS = {
    "login_check": {
        "anchor_event": {"event_id": "E1", "anchor_at": "2026-09-20T00:00:00Z"},
        "labels": [
            {"name": 0, "sampled_at": "2026-09-20T00:00:00Z",
             "captured_at": "2026-09-20T00:00:00Z",
             "evidence_kind": "live_ui_capture"},
            {"name": 5, "sampled_at": BAD,
             "captured_at": "2026-09-20T00:00:05Z",
             "evidence_kind": "live_ui_capture"},
            {"name": 10, "sampled_at": "2026-09-20T00:00:10Z",
             "captured_at": "2026-09-20T00:00:10Z",
             "evidence_kind": "live_ui_capture"},
        ],
    }
}

NEW_CODE = "R-TIMESTAMP-MALFORMED"

# the 16-code vocabulary of the pre-fix SUT (I-14-B oracle.md sec 2 + sec 11.3)
VOCAB_16 = {
    "R-ANCHOR-NOT-SHARED", "R-BASIS-UNKNOWN", "R-CLAIM-EXCEEDS", "R-DUP-RUN-ID",
    "R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-LABEL-ANCHOR", "R-NO-INTERVAL",
    "R-NO-SAMPLES", "R-POSTHOC-CAPTURE", "R-QC-IN-OBS", "R-SAME-INSTANT",
    "R-SAMPLE-OUTSIDE", "R-SIMULATED-CLOCK", "R-SUM-OVERLAP", "R-TOTAL-AS-OBS",
}


# ---------------------------------------------------------------------------
# shapes
# ---------------------------------------------------------------------------
def _win(cid: str, fields: dict, claim) -> dict:
    return {"case_id": cid, "class": "window_accounting", "requirement_id": "W-1",
            "claim": claim, "fields": dict(fields)}


def _cal(cid: str, fields: dict, claim, present: bool = True) -> dict:
    case = {"case_id": cid, "class": "calendar", "requirement_id": "C-1",
            "fields": json.loads(json.dumps(fields))}
    if present:
        case["claim"] = claim
    return case


def _login(cid: str, fields: dict) -> dict:
    return {"case_id": cid, "class": "login_anchor", "requirement_id": "L-1",
            "claim": {}, "fields": json.loads(json.dumps(fields))}


def ts1() -> dict:
    f = dict(GOOD_FIELDS)
    f["started_at"] = BAD
    return _win("F3-TS1", f, dict(SAMPLE_SPAN_1680))


def ts2() -> dict:
    f = dict(GOOD_FIELDS)
    f["sampled_at"] = list(GOOD_FIELDS["sampled_at"])
    f["sampled_at"][3] = BAD          # 00:06
    return _win("F3-TS2", f, dict(UNION_1740))


def ts5() -> dict:
    f = dict(GOOD_FIELDS)
    f["started_at"] = ["2026-09-20T00:00:00Z"]     # TYPE error, not a format one
    return _win("F3-TS5", f, dict(SAMPLE_SPAN_1680))


def ts3() -> dict:
    return _cal("F3-TS3", {"clock_source": "system_utc",
                           "ledger": {"daily": json.loads(json.dumps(DAILY)),
                                      "weekly": [], "monthly": [], "alerts": []}},
                {})


def ts4() -> dict:
    return _login("F3-TS4", LOGIN_FIELDS)


def ts3_no_tamper() -> dict:
    d = json.loads(json.dumps(DAILY))
    d[4]["started_at"] = "2026-09-15T03:30:00Z"
    return _cal("F3-TS3-GOOD", {"clock_source": "system_utc",
                                "ledger": {"daily": d, "weekly": [],
                                           "monthly": [], "alerts": []}}, {})


def stable_window() -> dict:
    return _win("F3-STAB-W", dict(GOOD_FIELDS), dict(UNION_1740))


TS_CASES = {
    "TS1": ts1, "TS2": ts2, "TS3": ts3, "TS4": ts4, "TS5": ts5,
}


# ---------------------------------------------------------------------------
# runners
# ---------------------------------------------------------------------------
def _run(cases, tmp_path, name="run", frozen: str = FROZEN_NOW):
    doc = {"frozen_now_utc": frozen, "cases": cases}
    cpath = tmp_path / f"{name}.cases.json"
    rpath = tmp_path / f"{name}.report.json"
    cpath.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(SUT_PATH),
         "--cases", str(cpath), "--report", str(rpath)],
        capture_output=True)
    report = None
    if rpath.exists():
        report = json.loads(rpath.read_text(encoding="utf-8"))
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), \
        proc.stderr.decode("utf-8", "replace"), report, rpath.exists()


def _classify(case, tol=5.0, cap_tol=5.0):
    spec = importlib.util.spec_from_file_location("i14b_sut_ts_total", SUT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from datetime import datetime, timezone
    frozen = datetime(2026, 9, 20, 2, 56, 38, tzinfo=timezone.utc)
    return mod.classify(case, frozen, tol, cap_tol)


# ---------------------------------------------------------------------------
# RED/GREEN: the per-case refusal family
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("cid", sorted(TS_CASES))
def test_malformed_timestamp_is_a_per_case_refusal_not_a_batch_kill(cid, tmp_path):
    rc, out, err, report, written = _run([TS_CASES[cid]()], tmp_path, cid)
    assert written, f"{cid}: no report written (verdict stripped) rc={rc} out={out!r}"
    assert rc == 0, f"{cid}: rc={rc} out={out!r}"
    assert "internal_error" not in out
    v = report["verdicts"][0]
    assert v["verdict"] == "reject_claim"
    assert NEW_CODE in v["refusals"], v["refusals"]
    assert "Invalid isoformat" not in out + err


def test_ts1_affected_time_field_is_null_and_the_rest_is_still_computed(tmp_path):
    rc, out, err, report, written = _run([ts1()], tmp_path, "TS1")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["refusals"] == [NEW_CODE]
    c = v["computed"]
    assert c["started_at"] is None                      # affected -> null
    assert c["observation_finished_at"] == "2026-09-20T00:29:00Z"   # unaffected
    assert c["scheduled_at"] is None
    assert c["observation_span_seconds"] == 1680.0      # from the 15 samples
    assert c["sample_count"] == 15
    assert c["first_sampled_at"] == "2026-09-20T00:00:00Z"
    assert c["last_sampled_at"] == "2026-09-20T00:28:00Z"
    assert c["quick_check_seconds"] == 480.0
    assert c["command_total_seconds"] is None           # needs the broken start
    assert c["schedule_lag_seconds"] is None
    assert c["union_seconds"] == 0.0
    assert c["sum_seconds"] == 0
    assert c["overlap_seconds"] == 0.0
    assert c["observation_interval_count"] == 0
    assert c["observation_intervals"] == []
    assert c["quick_check_overlap_seconds"] == 0.0
    assert c["basis"] == "sample_span"
    assert c["basis_registered"] is True


def test_ts2_unaffected_time_field_keeps_its_bytes(tmp_path):
    rc, out, err, report, written = _run([ts2()], tmp_path, "TS2")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["refusals"] == [NEW_CODE]
    c = v["computed"]
    assert c["started_at"] == "2026-09-20T00:00:00Z"    # NOT nulled
    assert c["observation_finished_at"] == "2026-09-20T00:29:00Z"
    assert c["sample_count"] == 14                      # one sample unreadable
    assert c["observation_span_seconds"] == 1680.0
    assert c["union_seconds"] == 1740.0
    assert c["sum_seconds"] == 1740.0
    assert c["observation_interval_count"] == 1
    assert c["observation_intervals"] == [["2026-09-20T00:00:00Z",
                                           "2026-09-20T00:29:00Z"]]
    assert c["command_total_seconds"] == 2220.0


def test_ts3_calendar_counts_the_records_it_can_read(tmp_path):
    rc, out, err, report, written = _run([ts3()], tmp_path, "TS3")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["refusals"] == [NEW_CODE]
    assert v["computed"] == {
        "daily_count": 4, "daily_same_day_runs_dropped": 0, "weekly_count": 0,
        "monthly_count": 0, "alert_count": 0, "window_status": "pending",
        "clock_source": "system_utc",
    }


def test_ts3_tamper_free_twin_is_accepted(tmp_path):
    rc, out, err, report, written = _run([ts3_no_tamper()], tmp_path, "TS3G")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["verdict"] == "accept_claim"
    assert v["refusals"] == []
    assert v["computed"]["daily_count"] == 5


def test_ts4_login_keeps_label_count_and_refuses(tmp_path):
    rc, out, err, report, written = _run([ts4()], tmp_path, "TS4")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["refusals"] == [NEW_CODE]
    c = v["computed"]
    assert c["label_count"] == 3
    assert c["anchor_event_id"] == "E1"
    assert c["shared_anchor_event_id"] == "E1"
    assert c["label_offsets_seconds"] == [0, 10]     # offsets, not errors
    assert c["label_offset_max_error_seconds"] == 0.0
    assert c["capture_latency_max_seconds"] == 0.0


def test_ts5_a_type_error_field_uses_the_same_new_code(tmp_path):
    rc, out, err, report, written = _run([ts5()], tmp_path, "TS5")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["verdict"] == "reject_claim"
    assert v["refusals"] == [NEW_CODE]
    assert v["computed"]["started_at"] is None


def test_direct_classify_never_raises_on_a_malformed_timestamp():
    for cid, build in TS_CASES.items():
        got = _classify(build())
        assert got["verdict"] == "reject_claim", cid
        assert NEW_CODE in got["refusals"], cid


# ---------------------------------------------------------------------------
# rc domain: rc=2 stays document/call domain, rc=4 stays internal-error only
# ---------------------------------------------------------------------------
def test_document_domain_frozen_instant_stays_rc2(tmp_path):
    rc, out, err, report, written = _run([stable_window()], tmp_path, "DOC",
                                         frozen=BAD)
    assert rc == 2
    assert not written
    payload = json.loads(out.strip().splitlines()[-1])
    assert payload["error"] == "malformed_input"
    assert payload["detail"] == f"Invalid isoformat string: '{BAD}'"


def test_internal_error_path_is_still_reachable(tmp_path):
    # a DOCUMENT-level type error that section 11.8 does NOT enumerate must not
    # be swallowed: the internal-error handler still fires (before == after).
    rc, out, err, report, written = _run("abc", tmp_path, "CTRL")
    assert rc == 4
    assert not written
    payload = json.loads(out.strip().splitlines()[-1])
    assert payload["error"] == "internal_error"
    assert "has no attribute 'get'" in payload["detail"]


def test_missing_required_timestamp_key_still_raises_keyerror():
    # boundary declared in oracle.md sec 8 item 1: missing keys are NOT in the
    # section 11.8 authorization and must keep their original behaviour.
    f = dict(GOOD_FIELDS)
    del f["started_at"]
    with pytest.raises(KeyError):
        _classify(_win("F3-MISSING", f, dict(UNION_1740)))


# ---------------------------------------------------------------------------
# stable rows: well-formed behaviour must not move
# ---------------------------------------------------------------------------
def test_well_formed_window_is_still_accepted(tmp_path):
    rc, out, err, report, written = _run([stable_window()], tmp_path, "STAB")
    assert rc == 0 and written
    v = report["verdicts"][0]
    assert v["verdict"] == "accept_claim"
    assert v["refusals"] == []
    assert v["computed"]["union_seconds"] == 1740.0


def test_well_formed_subset_of_r2_is_byte_stable_between_runs(tmp_path):
    ids = ["W1", "X5", "C1"]
    cases = [json.loads(json.dumps(BY_ID[i])) for i in ids]
    rc1, out1, e1, rep1, w1 = _run(cases, tmp_path, "good1")
    rc2, out2, e2, rep2, w2 = _run(cases, tmp_path, "good2")
    assert rc1 == rc2 == 0 and w1 and w2
    assert rep1 == rep2


# ---------------------------------------------------------------------------
# batch: one malformed case must not destroy the others (section 11.8 item 4)
# ---------------------------------------------------------------------------
def test_single_malformed_case_cannot_kill_the_batch(tmp_path):
    cases = [ts2()] + [json.loads(json.dumps(BY_ID[i])) for i in ("W1", "X5", "C1")]
    rc, out, err, report, written = _run(cases, tmp_path, "BATCH")
    assert written, f"no report: rc={rc} out={out!r}"
    assert rc == 0, out
    assert report["case_count"] == 4
    assert len(report["verdicts"]) == 4
    bad = report["verdicts"][0]
    assert bad["verdict"] == "reject_claim"
    assert bad["refusals"] == [NEW_CODE]

    only_good = [json.loads(json.dumps(BY_ID[i])) for i in ("W1", "X5", "C1")]
    rc2, out2, err2, rep2, w2 = _run(only_good, tmp_path, "GOODONLY")
    assert rc2 == 0 and w2
    # the three well-formed verdicts are byte-identical with and without the bad one
    assert json.dumps(report["verdicts"][1:], ensure_ascii=False) == \
        json.dumps(rep2["verdicts"], ensure_ascii=False)


# ---------------------------------------------------------------------------
# vocabulary: 16 -> 17, only the new code added
# ---------------------------------------------------------------------------
def test_refusal_vocabulary_is_exactly_17_and_the_16_old_ones_are_untouched():
    src = SUT_PATH.read_text(encoding="utf-8")
    found = set(re.findall(r"\bR-[A-Z0-9-]+\b", src))
    assert found - VOCAB_16 == {NEW_CODE}, sorted(found - VOCAB_16)
    assert VOCAB_16 - found == set(), sorted(VOCAB_16 - found)
    assert len(found) == 17, sorted(found)
