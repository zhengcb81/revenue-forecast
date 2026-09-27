"""T1-F3-FIX verification driver (subcommands; no product code is imported here
except through real subprocess runs of the SUT).

Every subcommand writes raw artefacts under evidence/<phase>/... so that a
reviewer can re-read raw rc + raw stdout/stderr instead of trusting summaries.

Subcommands:
  freeze                              write evidence/freeze.json (oracle + pins)
  probes   --phase before|after       probe family TS1..TS5 + DOC-2 + CTRL-4
  gates    --phase before|after       run_cases gates on cases.r2.json / cases.json
  suites   --phase before|after       the 4 inherited suites + this card's new suite
  ncmissing --phase before|after      T1-F2-FIX's 7 missing-key rows, byte-compare
  vocab    --phase before|after       refusal-code vocabulary regex count
  batch    --phase before|after       B-NEG / B-POS / B-BYTE-1 / B-BYTE-2
  mut20    --phase before|after       harness/mutate.r2.py 20 arms
  mutations                           the 4 T1-F3-FIX mutation arms
  invariants                          aggregate checks incl. line disjointness
  diff                                build changes.diff (difflib, no git)
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # .../a20260925-01/scripts
ATTEMPT = HERE.parent                             # .../a20260925-01
WT = ATTEMPT / "worktree" / "i14b"                # isolation worktree
HARNESS = WT / "harness"
SUT = WT / "iso" / "natural_window.py"
BASELINE = ATTEMPT / "baseline" / "natural_window.t1_f2fixed.pristine.py"
EVID = ATTEMPT / "evidence"
PY = str(Path(sys.executable))
RUN_CASES = HARNESS / "run_cases.py"
CASES_R2 = HARNESS / "cases.r2.json"
CASES_R1 = HARNESS / "cases.json"
EXP_R2 = HARNESS / "frozen_expectations.r2.json"
EXP_R1 = HARNESS / "frozen_expectations.json"
MUTATE_R2 = HARNESS / "mutate.r2.py"

FROZEN_NOW = "2026-09-20T02:56:38Z"
BAD = "not-a-timestamp"
NEW_CODE = "R-TIMESTAMP-MALFORMED"
VOCAB_16 = {
    "R-ANCHOR-NOT-SHARED", "R-BASIS-UNKNOWN", "R-CLAIM-EXCEEDS", "R-DUP-RUN-ID",
    "R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-LABEL-ANCHOR", "R-NO-INTERVAL",
    "R-NO-SAMPLES", "R-POSTHOC-CAPTURE", "R-QC-IN-OBS", "R-SAME-INSTANT",
    "R-SAMPLE-OUTSIDE", "R-SIMULATED-CLOCK", "R-SUM-OVERLAP", "R-TOTAL-AS-OBS",
}
SUITES = [
    "test_i14b_natural_window.py",
    "test_i14b_natural_window_r2.py",
    "test_i14b_natural_window_basis_total.py",
    "test_i14b_natural_window_container_total.py",
]
NEW_SUITE = "test_i14b_natural_window_timestamp_total.py"

PINS = {
    "harness/run_cases.py": None,
    "harness/mutate.r2.py": None,
    "harness/cases.json": None,
    "harness/cases.r2.json": None,
    "harness/frozen_expectations.json": None,
    "harness/frozen_expectations.r2.json": None,
    "harness/tests/test_i14b_natural_window.py": None,
    "harness/tests/test_i14b_natural_window_r2.py": None,
    "harness/tests/test_i14b_natural_window_basis_total.py": None,
    "harness/tests/test_i14b_natural_window_container_total.py": None,
}
PIN_EXPECT = {
    "harness/run_cases.py": "f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23",
    "harness/mutate.r2.py": "4f741cb72af5cdb62095b422d4d87d6440082091a53969704201616bed383def",
    "harness/cases.json": "5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64",
    "harness/cases.r2.json": "23d89fb27bbdb599646290ba5dbf096a0d1513d63c7a6d19f3f16fe9f88279de",
    "harness/frozen_expectations.json": "3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b",
    "harness/frozen_expectations.r2.json": "a24d8ab3444dd1c75eaa3533f424a048bdced4f0f66408cb04622ead760667ba",
    "harness/tests/test_i14b_natural_window.py": "413ff05c52e07acacf0491a0ec3f2cd1c426011995b45d7ad3edaab65a38ad4e",
    "harness/tests/test_i14b_natural_window_r2.py": "ace076871c811441bc454692323dbba71243086ec7287880eed9b51a8114d1e9",
    "harness/tests/test_i14b_natural_window_basis_total.py": "316e369c9afc9d8df04a425945b97e41378e87f3ac17c721d0ab9ddf90904bfd",
    "harness/tests/test_i14b_natural_window_container_total.py": "f39f1b912cfb664d207a95d8e7853c79dfc76cda6bdebd94afc9ea87e064387c",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wjson(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def rmtree(p: Path) -> None:
    shutil.rmtree(p, ignore_errors=True)


def subprocess_run(argv, cwd=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(argv, cwd=cwd, env=e, capture_output=True)


def case_by_id() -> dict:
    doc = json.loads(CASES_R2.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in doc["cases"]}


CBY = case_by_id()

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
             "captured_at": "2026-09-20T00:00:00Z", "evidence_kind": "live_ui_capture"},
            {"name": 5, "sampled_at": BAD,
             "captured_at": "2026-09-20T00:00:05Z", "evidence_kind": "live_ui_capture"},
            {"name": 10, "sampled_at": "2026-09-20T00:00:10Z",
             "captured_at": "2026-09-20T00:00:10Z", "evidence_kind": "live_ui_capture"},
        ]}}


def _win(cid, fields, claim):
    return {"case_id": cid, "class": "window_accounting", "requirement_id": "W-1",
            "claim": claim, "fields": dict(fields)}


def _cal(cid, fields, claim, present=True):
    c = {"case_id": cid, "class": "calendar", "requirement_id": "C-1",
         "fields": json.loads(json.dumps(fields))}
    if present:
        c["claim"] = claim
    return c


def probe_cases() -> dict:
    f1 = dict(GOOD_FIELDS); f1["started_at"] = BAD
    f2 = dict(GOOD_FIELDS); f2["sampled_at"] = list(GOOD_FIELDS["sampled_at"])
    f2["sampled_at"][3] = BAD
    f5 = dict(GOOD_FIELDS); f5["started_at"] = ["2026-09-20T00:00:00Z"]
    return {
        "TS1": _win("F3-TS1", f1, dict(SAMPLE_SPAN_1680)),
        "TS2": _win("F3-TS2", f2, dict(UNION_1740)),
        "TS3": _cal("F3-TS3", {"clock_source": "system_utc",
                               "ledger": {"daily": json.loads(json.dumps(DAILY)),
                                          "weekly": [], "monthly": [], "alerts": []}}, {}),
        "TS4": {"case_id": "F3-TS4", "class": "login_anchor", "requirement_id": "L-1",
                "claim": {}, "fields": json.loads(json.dumps(LOGIN_FIELDS))},
        "TS5": _win("F3-TS5", f5, dict(SAMPLE_SPAN_1680)),
    }


def run_sut(sut: Path, cases_obj, out_dir: Path, name: str, frozen: str = FROZEN_NOW):
    out_dir.mkdir(parents=True, exist_ok=True)
    cpath = out_dir / f"{name}.cases.json"
    rpath = out_dir / f"{name}.report.json"
    if rpath.exists():
        rpath.unlink()
    cpath.write_text(json.dumps({"frozen_now_utc": frozen, "cases": cases_obj},
                                ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([PY, "-X", "utf8", "-B", str(sut),
                           "--cases", str(cpath), "--report", str(rpath)],
                          capture_output=True)
    (out_dir / f"{name}.stdout.txt").write_bytes(proc.stdout)
    (out_dir / f"{name}.stderr.txt").write_bytes(proc.stderr)
    (out_dir / f"{name}.argv.json").write_text(json.dumps(
        {"argv": [PY, "-X", "utf8", "-B", str(sut), "--cases", str(cpath),
                  "--report", str(rpath)], "raw_returncode": proc.returncode},
        indent=2), encoding="utf-8")
    report = json.loads(rpath.read_text(encoding="utf-8")) if rpath.exists() else None
    return {"raw_returncode": proc.returncode,
            "stdout": proc.stdout.decode("utf-8", "replace"),
            "stderr": proc.stderr.decode("utf-8", "replace"),
            "report_written": rpath.exists(),
            "report_sha256": sha(rpath) if rpath.exists() else None,
            "report": report}


# --------------------------------------------------------------------------
# freeze
# --------------------------------------------------------------------------
def cmd_freeze(_args) -> int:
    oracle = ATTEMPT / "oracle.md"
    pins = {}
    for rel in PINS:
        p = WT / rel
        pins[rel] = {"sha256": sha(p), "bytes": p.stat().st_size,
                     "expected": PIN_EXPECT[rel], "equal": sha(p) == PIN_EXPECT[rel]}
    plan = ATTEMPT.parents[2]  # 2026-09-19-three-project-history-audit
    ext = {}
    for rel in ("execution_runs/I-14-B/a20260919-01/oracle.md",
                "execution_runs/T1-10-FIX/a20260923-01/review.md",
                "execution_runs/T1-10-FIX/a20260923-01/reviewer_report.md",
                "execution_runs/T1-10-FIX/a20260923-01/changes.diff",
                "execution_runs/T1-10-FIX/a20260923-01/handoff.json",
                "execution_runs/T1-F2-FIX/a20260923-01/changes.diff",
                "execution_runs/T1-F2-FIX/a20260923-01/handoff.json"):
        p = plan / rel
        ext[rel] = {"sha256": sha(p), "bytes": p.stat().st_size}
    doc = {
        "card": "T1-F3-FIX", "attempt_id": "a20260925-01",
        "oracle": {"sha256": sha(oracle), "bytes": oracle.stat().st_size,
                   "mtime_utc": __import__("datetime").datetime.utcfromtimestamp(
                       oracle.stat().st_mtime).isoformat() + "Z",
                   "frozen_before_first_run": True},
        "sut_baseline": {"sha256": sha(BASELINE), "bytes": BASELINE.stat().st_size},
        "sut_worktree_at_freeze": {"sha256": sha(SUT), "bytes": SUT.stat().st_size,
                                   "equals_baseline": sha(SUT) == sha(BASELINE)},
        "harness_pins": pins,
        "external_authority": ext,
        "git_boundary_before_run": git_boundary(),
        "note": "written before any SUT / harness / pytest run of this card",
    }
    wjson(EVID / "freeze.json", doc)
    print(json.dumps({"oracle_sha": doc["oracle"]["sha256"],
                      "sut_at_freeze": doc["sut_worktree_at_freeze"],
                      "pins_ok": all(v["equal"] for v in pins.values()),
                      "git_non_planning": doc["git_boundary_before_run"]["non_planning"]},
                     indent=2))
    return 0


def git_boundary() -> dict:
    proc = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "HEAD",
                           "--name-only"], cwd=str(ATTEMPT.parents[4]),
                          capture_output=True)
    lines = [l for l in proc.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    non = [l for l in lines if not l.replace("\\", "/").startswith(".planning/")]
    return {"total": len(lines), "non_planning": len(non),
            "non_planning_paths": non, "raw_exit": proc.returncode}


# --------------------------------------------------------------------------
# probes
# --------------------------------------------------------------------------
def cmd_probes(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    out = EVID / phase / "probes"
    rmtree(out)
    raw = out / "raw"
    cases = probe_cases()
    results = {}
    for cid, case in cases.items():
        results[cid] = run_sut(sut, [case], raw, cid)
    # document domain
    results["DOC2"] = run_sut(sut, [dict(cases["TS1"])], raw, "DOC2", frozen=BAD)
    # internal-error control: `cases` is a document-level string
    results["CTRL4"] = run_sut(sut, "abc", raw, "CTRL4")

    # direct classify() call (no process boundary)
    direct = {}
    for cid, case in cases.items():
        argv = [PY, "-X", "utf8", "-B", "-c",
                "import importlib.util,sys,json;"
                "spec=importlib.util.spec_from_file_location('sut', sys.argv[1]);"
                "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
                "from datetime import datetime,timezone;"
                "case=json.load(open(sys.argv[2],encoding='utf-8'))['cases'][0];"
                "f=datetime(2026,9,20,2,56,38,tzinfo=timezone.utc);"
                "r=m.classify(case,f,5.0,5.0);print(json.dumps(r,ensure_ascii=False))",
                str(sut), str(raw / f"{cid}.cases.json")]
        p = subprocess_run(argv)
        direct[cid] = {"returncode": p.returncode,
                       "stdout": p.stdout.decode("utf-8", "replace")[:2000],
                       "stderr": p.stderr.decode("utf-8", "replace")[:2000]}
    results["_direct_classify"] = direct

    checks = evaluate_probes(phase, results)
    doc = {"phase": phase, "sut": str(sut), "sut_sha256": sha(sut),
           "results": summarize(results), "direct": direct,
           "checks": checks,
           "checks_pass": all(c["ok"] for c in checks),
           "checks_failed": [c["name"] for c in checks if not c["ok"]]}
    wjson(out / "results.json", doc)
    print(json.dumps({"phase": phase, "sut_sha256": doc["sut_sha256"],
                      "n_checks": len(checks),
                      "failed": doc["checks_failed"]}, indent=2))
    return 0 if doc["checks_pass"] else 1


def summarize(results) -> dict:
    out = {}
    for k, v in results.items():
        if k.startswith("_"):
            continue
        out[k] = {"raw_returncode": v["raw_returncode"],
                  "report_written": v["report_written"],
                  "stdout_tail": v["stdout"].strip().splitlines()[-1][:400]
                  if v["stdout"].strip() else "",
                  "stderr_tail": v["stderr"].strip().splitlines()[-1][:400]
                  if v["stderr"].strip() else "",
                  "verdicts": (v["report"] or {}).get("verdicts")}
    return out


RED_EXPECT = {
    "TS1": (4, False, "Invalid isoformat string: 'not-a-timestamp'"),
    "TS2": (4, False, "Invalid isoformat string: 'not-a-timestamp'"),
    "TS3": (4, False, "Invalid isoformat string: 'not-a-timestamp'"),
    "TS4": (4, False, "Invalid isoformat string: 'not-a-timestamp'"),
    "TS5": (4, False, "'list' object has no attribute 'endswith'"),
    "DOC2": (2, False, "Invalid isoformat string: 'not-a-timestamp'"),
    "CTRL4": (4, False, "has no attribute 'get'"),
}

GREEN_COMPUTED = {
    "TS1": {
        "refusals": [NEW_CODE],
        "computed": {
            "scheduled_at": None, "started_at": None,
            "first_sampled_at": "2026-09-20T00:00:00Z",
            "last_sampled_at": "2026-09-20T00:28:00Z",
            "observation_finished_at": "2026-09-20T00:29:00Z",
            "observation_span_seconds": 1680.0, "sample_count": 15,
            "samples_outside_window": 0, "quick_check_seconds": 480.0,
            "command_total_seconds": None, "schedule_lag_seconds": None,
            "observation_interval_count": 0, "observation_intervals": [],
            "quick_check_in_observation_intervals": False,
            "quick_check_overlap_seconds": 0.0, "union_seconds": 0.0,
            "sum_seconds": 0, "overlap_seconds": 0.0, "basis": "sample_span",
            "basis_registered": True, "sum_used_for_natural_duration": False}},
    "TS2": {
        "refusals": [NEW_CODE],
        "computed": {
            "scheduled_at": None, "started_at": "2026-09-20T00:00:00Z",
            "first_sampled_at": "2026-09-20T00:00:00Z",
            "last_sampled_at": "2026-09-20T00:28:00Z",
            "observation_finished_at": "2026-09-20T00:29:00Z",
            "observation_span_seconds": 1680.0, "sample_count": 14,
            "samples_outside_window": 0, "quick_check_seconds": 480.0,
            "command_total_seconds": 2220.0, "schedule_lag_seconds": None,
            "observation_interval_count": 1,
            "observation_intervals": [["2026-09-20T00:00:00Z",
                                       "2026-09-20T00:29:00Z"]],
            "quick_check_in_observation_intervals": False,
            "quick_check_overlap_seconds": 0.0, "union_seconds": 1740.0,
            "sum_seconds": 1740.0, "overlap_seconds": 0.0,
            "basis": "union_of_windows", "basis_registered": True,
            "sum_used_for_natural_duration": False}},
    "TS3": {
        "refusals": [NEW_CODE],
        "computed": {"daily_count": 4, "daily_same_day_runs_dropped": 0,
                     "weekly_count": 0, "monthly_count": 0, "alert_count": 0,
                     "window_status": "pending", "clock_source": "system_utc"}},
    "TS4": {
        "refusals": [NEW_CODE],
        "computed": {"anchor_event_id": "E1", "shared_anchor_event_id": "E1",
                     "label_offsets_seconds": [0, 10],
                     "label_offset_max_error_seconds": 0.0,
                     "capture_latency_max_seconds": 0.0, "label_count": 3}},
    "TS5": {"refusals": [NEW_CODE], "computed_started_at": None},
}


def evaluate_probes(phase: str, results: dict) -> list:
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    for cid, (rc, written, frag) in RED_EXPECT.items():
        r = results[cid]
        if phase == "before":
            chk(f"{cid} RED: rc={rc} / report_written={written} / detail~{frag}",
                r["raw_returncode"] == rc and r["report_written"] == written
                and frag in r["stdout"],
                f"observed rc={r['raw_returncode']} written={r['report_written']} "
                f"stdout={r['stdout'].strip()[:300]!r}")
        else:
            if cid in ("DOC2", "CTRL4"):
                chk(f"{cid} UNCHANGED vs RED (rc={rc})",
                    r["raw_returncode"] == rc and r["report_written"] == written
                    and frag in r["stdout"],
                    f"observed rc={r['raw_returncode']} written={r['report_written']} "
                    f"stdout={r['stdout'].strip()[:300]!r}")
            else:
                v = (r["report"] or {}).get("verdicts", [{}])[0]
                chk(f"{cid} GREEN: rc=0 + report + reject + {NEW_CODE}",
                    r["raw_returncode"] == 0 and r["report_written"]
                    and v.get("verdict") == "reject_claim"
                    and NEW_CODE in (v.get("refusals") or []),
                    f"rc={r['raw_returncode']} written={r['report_written']} "
                    f"verdict={v.get('verdict')} refusals={v.get('refusals')}")

    if phase == "after":
        for cid in ("TS1", "TS2", "TS3", "TS4", "TS5"):
            exp = GREEN_COMPUTED[cid]
            v = (results[cid]["report"] or {}).get("verdicts", [{}])[0]
            got_ref = v.get("refusals")
            chk(f"{cid} refusals == {exp['refusals']}", got_ref == exp["refusals"],
                f"got {got_ref}")
            if cid == "TS5":
                chk("TS5 computed.started_at is null",
                    v.get("computed", {}).get("started_at") is None,
                    repr(v.get("computed", {}).get("started_at")))
            else:
                got = v.get("computed", {})
                diffs = {k: (got.get(k), val) for k, val in exp["computed"].items()
                         if got.get(k) != val}
                chk(f"{cid} computed == hand-computed expectation", not diffs,
                    json.dumps(diffs, ensure_ascii=False, default=str))
        # direct classify must never raise after the fix
        for cid in ("TS1", "TS2", "TS3", "TS4", "TS5"):
            d = results["_direct_classify"][cid]
            chk(f"{cid} direct classify() does not raise",
                d["returncode"] == 0 and "Traceback" not in d["stderr"],
                d["stderr"][:300])
    else:
        for cid in ("TS1", "TS2", "TS3", "TS4", "TS5"):
            d = results["_direct_classify"][cid]
            chk(f"{cid} RED direct classify() raises",
                d["returncode"] != 0 and "Traceback" in d["stderr"],
                d["stderr"][:300])
    return checks


# --------------------------------------------------------------------------
# gates
# --------------------------------------------------------------------------
def cmd_gates(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    out = EVID / phase / "gates"
    rmtree(out)
    summary = {}
    for label, cases, exp in (("r2", CASES_R2, EXP_R2), ("r1", CASES_R1, EXP_R1)):
        d = out / f"cmd-CASES-{label}"
        proc = subprocess.run(
            [PY, "-X", "utf8", "-B", str(RUN_CASES), "--sut", str(sut),
             "--out-dir", str(d), "--label", f"t1f3fix-{phase}-{label}",
             "--cases", str(cases), "--expectations", str(exp)],
            capture_output=True)
        (d / "runner.stdout.txt").write_bytes(proc.stdout)
        (d / "runner.stderr.txt").write_bytes(proc.stderr)
        gate = json.loads((d / "cases_report.json").read_text(encoding="utf-8"))
        rep = d / "sut_report.json"
        summary[label] = {
            "runner_rc": proc.returncode, "ok": gate.get("ok"),
            "mismatch_count": gate.get("mismatch_count"),
            "accepted_ineligible": gate.get("accepted_ineligible"),
            "case_count": gate.get("case_count"),
            "sut_raw_returncode": gate.get("sut_raw_returncode"),
            "sut_report_sha256": sha(rep) if rep.exists() else None,
            "mismatch_ids": sorted({m["case_id"] for m in gate.get("mismatches", [])}),
        }
    wjson(out / "summary.json", {"phase": phase, "sut_sha256": sha(sut),
                                 "gates": summary})
    print(json.dumps(summary, indent=2))
    return 0


# --------------------------------------------------------------------------
# suites
# --------------------------------------------------------------------------
def cmd_suites(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    out = EVID / phase / "suites"
    rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    # sandbox accommodation, inherited byte-identically from T1-F2-FIX
    # (scripts/pytest_tmp_acl_plugin.py sha256 e96890fe3275a6ef72063b0c112afdd6
    # 6607a2b4ae50c08cdd8664594f0002aa3 / 1725 B, equal to theirs): on this host
    # os.mkdir(path, 0o700) succeeds but yields a directory the creating process
    # cannot even list, so pytest dies in
    # cleanup_dead_symlinks BEFORE printing its summary.  The g1_ prefix keeps the
    # basetemp names away from three such 0o700 dirs left by the two plugin-less
    # instrument runs (they are undeletable and are disclosed as such).
    plugin_dir = ATTEMPT / "scripts"
    for suite in SUITES + [NEW_SUITE]:
        bt = ATTEMPT / "_pytest_tmp" / f"g1_{phase}_{suite[:24]}"
        rmtree(bt)
        proc = subprocess.run(
            [PY, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
             "-p", "pytest_tmp_acl_plugin",
             "--basetemp", str(bt), "-q", str(HARNESS / "tests" / suite)],
            capture_output=True, cwd=str(WT),
            env={**os.environ, "I14B_SUT": str(sut),
                 "PYTHONPATH": str(plugin_dir)
                 + (os.pathsep + os.environ["PYTHONPATH"]
                    if os.environ.get("PYTHONPATH") else "")})
        text = (proc.stdout + proc.stderr).decode("utf-8", "replace")
        (out / f"{suite}.stdout.txt").write_text(text, encoding="utf-8")
        passed = sum(int(m) for m in re.findall(r"(\d+) passed", text))
        failed = sum(int(m) for m in re.findall(r"(\d+) failed", text))
        errors = sum(int(m) for m in re.findall(r"(\d+) error", text))
        results[suite] = {"pytest_rc": proc.returncode, "passed": passed,
                          "failed": failed, "errors": errors,
                          "is_new_suite": suite == NEW_SUITE}
    wjson(out / "suites_summary.json", {"phase": phase, "sut_sha256": sha(sut),
                                        "suites": results})
    print(json.dumps(results, indent=2))
    return 0


# --------------------------------------------------------------------------
# NC-MISSING (T1-F2-FIX's 7 rows)
# --------------------------------------------------------------------------
def nc_rows() -> dict:
    f1, f2, f3 = CBY["C1"]["fields"], CBY["C2"]["fields"], CBY["C3"]["fields"]
    c1, c3 = CBY["C1"]["claim"], CBY["C3"]["claim"]

    def cal(fields, claim, present=True):
        case = {"case_id": "NC", "class": "calendar", "requirement_id": "C-1",
                "fields": json.loads(json.dumps(fields))}
        if present:
            case["claim"] = json.loads(json.dumps(claim))
        return case

    rows = {}
    kf3 = json.loads(json.dumps(f3)); kf3.pop("clock_source", None)
    rows["K7"] = (kf3, c3, True)
    for cid, fields, claim, present in (
            ("S7a", f2, {}, True), ("S7b", f2, {"other": 1}, True),
            ("S7c", f2, None, False), ("S8", f1, {}, True),
            ("S9", f1, c1, True), ("S10", f2, CBY["C2"]["claim"], True)):
        f = json.loads(json.dumps(fields))
        f["clock_source"] = "system_utc"
        rows[cid] = (f, claim, present)
    out = {}
    for cid, (fields, claim, present) in rows.items():
        out[cid] = cal(fields, claim, present)
    return out


NC_STABLE = {
    "K7": ("reject_claim", ["R-SIMULATED-CLOCK"]),
    "S7a": ("accept_claim", []),
    "S7b": ("accept_claim", []),
    "S7c": ("accept_claim", []),
    "S8": ("reject_claim", ["R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-SAME-INSTANT"]),
    "S9": ("reject_claim", ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK",
                            "R-SAME-INSTANT"]),
    "S10": ("accept_claim", []),
}


def cmd_ncmissing(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    out = EVID / phase / "nc_missing"
    rmtree(out)
    rows = nc_rows()
    res = {}
    for cid, case in rows.items():
        r = run_sut(sut, [case], out, cid)
        v = ((r["report"] or {}).get("verdicts") or [{}])[0]
        res[cid] = {"rc": r["raw_returncode"], "report_written": r["report_written"],
                    "verdict": v.get("verdict"), "refusals": v.get("refusals"),
                    "verdict_json": json.dumps(v, ensure_ascii=False, sort_keys=True)}
    checks = []
    for cid, (want_v, want_r) in NC_STABLE.items():
        got = res[cid]
        ok = (got["rc"] == 0 and got["verdict"] == want_v
              and got["refusals"] == want_r)
        checks.append({"name": f"{cid} == {want_v} {want_r}", "ok": ok,
                       "detail": json.dumps(got, ensure_ascii=False)})
    s8 = res["S8"]["refusals"] or []
    checks.append({"name": "S8 rejects WITHOUT R-CLAIM-EXCEEDS", "ok":
                   "R-CLAIM-EXCEEDS" not in s8, "detail": json.dumps(s8)})
    doc = {"phase": phase, "sut_sha256": sha(sut), "rows": res, "checks": checks,
           "checks_pass": all(c["ok"] for c in checks),
           "failed": [c["name"] for c in checks if not c["ok"]]}
    wjson(out / "results.json", doc)
    print(json.dumps({"phase": phase, "failed": doc["failed"]}, indent=2))
    return 0 if doc["checks_pass"] else 1


# --------------------------------------------------------------------------
# vocabulary
# --------------------------------------------------------------------------
def vocab_of(sut: Path) -> set:
    return set(re.findall(r"\bR-[A-Z0-9-]+\b", sut.read_text(encoding="utf-8")))


def cmd_vocab(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    found = vocab_of(sut)
    doc = {"phase": phase, "sut_sha256": sha(sut), "count": len(found),
           "codes": sorted(found),
           "added_vs_baseline16": sorted(found - VOCAB_16),
           "missing_vs_baseline16": sorted(VOCAB_16 - found),
           "regex": r"\bR-[A-Z0-9-]+\b"}
    if phase == "before":
        doc["check"] = (len(found) == 16 and not doc["added_vs_baseline16"]
                        and not doc["missing_vs_baseline16"])
    else:
        doc["check"] = (len(found) == 17
                        and set(doc["added_vs_baseline16"]) == {NEW_CODE}
                        and not doc["missing_vs_baseline16"])
    wjson(EVID / phase / "vocab.json", doc)
    print(json.dumps(doc, indent=2))
    return 0 if doc["check"] else 1


# --------------------------------------------------------------------------
# batch negative control
# --------------------------------------------------------------------------
def batch_cases():
    good = [json.loads(json.dumps(CBY[i])) for i in ("W1", "X5", "C1")]
    bad = probe_cases()["TS2"]
    return good, bad


def cmd_batch(args) -> int:
    phase, sut = args.phase, Path(args.sut)
    out = EVID / phase / "batch"
    rmtree(out)
    good, bad = batch_cases()
    res = {}
    res["mixed"] = run_sut(sut, [bad] + good, out, "mixed")
    res["good_only"] = run_sut(sut, good, out, "good_only")

    checks = []
    if phase == "before":
        checks.append({"name": "B-NEG: one bad case blows up the whole batch "
                               "(rc=4 / no report / 0 adjudications)",
                       "ok": res["mixed"]["raw_returncode"] == 4
                       and not res["mixed"]["report_written"],
                       "detail": f"rc={res['mixed']['raw_returncode']} "
                                 f"written={res['mixed']['report_written']} "
                                 f"stdout={res['mixed']['stdout'].strip()[:200]!r}"})
        checks.append({"name": "control: good-only batch still adjudicates "
                               "(rc=0, 3 verdicts)",
                       "ok": res["good_only"]["raw_returncode"] == 0
                       and len(res["good_only"]["report"]["verdicts"]) == 3,
                       "detail": f"rc={res['good_only']['raw_returncode']}"})
    else:
        m, g = res["mixed"], res["good_only"]
        checks.append({"name": "B-POS: mixed batch rc=0 / report written / 4 verdicts",
                       "ok": m["raw_returncode"] == 0 and m["report_written"]
                       and len(m["report"]["verdicts"]) == 4,
                       "detail": f"rc={m['raw_returncode']} "
                                 f"written={m['report_written']} "
                                 f"n={len((m['report'] or {}).get('verdicts', []))}"})
        bad_v = m["report"]["verdicts"][0]
        checks.append({"name": "bad case alone refused with the new code",
                       "ok": bad_v["verdict"] == "reject_claim"
                       and bad_v["refusals"] == [NEW_CODE],
                       "detail": json.dumps(bad_v["refusals"])})
        checks.append({"name": "B-BYTE-1: good verdicts byte-identical with and "
                               "without the bad case",
                       "ok": json.dumps(m["report"]["verdicts"][1:],
                                        ensure_ascii=False)
                       == json.dumps(g["report"]["verdicts"], ensure_ascii=False),
                       "detail": "verdicts[1:] vs good_only.verdicts"})
        checks.append({"name": "B-BYTE-2: good-only report byte-identical "
                               "before vs after (cross-phase, checked in invariants)",
                       "ok": True, "detail": "sha recorded for cross-phase compare"})
    doc = {"phase": phase, "sut_sha256": sha(sut),
           "mixed": {k: v for k, v in res["mixed"].items() if k != "report"},
           "mixed_verdicts": (res["mixed"]["report"] or {}).get("verdicts"),
           "good_only": {k: v for k, v in res["good_only"].items() if k != "report"},
           "good_only_verdicts": (res["good_only"]["report"] or {}).get("verdicts"),
           "good_only_report_sha256": res["good_only"]["report_sha256"],
           "checks": checks, "checks_pass": all(c["ok"] for c in checks),
           "failed": [c["name"] for c in checks if not c["ok"]]}
    wjson(out / "results.json", doc)
    print(json.dumps({"phase": phase, "failed": doc["failed"]}, indent=2))
    return 0 if doc["checks_pass"] else 1


# --------------------------------------------------------------------------
# 20-arm mutation ratchet
# --------------------------------------------------------------------------
def cmd_mut20(args) -> int:
    phase = args.phase
    out = EVID / phase / "mut20"
    rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    mut_out = out / "mutations.r2.json"
    proc = subprocess.run([PY, "-X", "utf8", "-B", str(MUTATE_R2),
                           "--out", str(mut_out)], capture_output=True, cwd=str(WT))
    (out / "stdout.txt").write_text(
        proc.stdout.decode("utf-8", "replace"), encoding="utf-8")
    (out / "stderr.txt").write_text(
        proc.stderr.decode("utf-8", "replace"), encoding="utf-8")
    doc = json.loads(mut_out.read_text(encoding="utf-8")) if mut_out.exists() else {}
    muts = doc.get("mutants", [])
    summary = {"phase": phase, "sut_sha256": sha(SUT), "runner_rc": proc.returncode,
               "mutation_count": len(muts),
               "all_mutants_red_again": all(m["red_again"] for m in muts),
               "all_expected_cases_red": all(m["expected_cases_are_red"] for m in muts),
               "load_bearing": sum(1 for m in muts if m["red_again"]),
               "non_red": [m["mutant_id"] for m in muts if not m["red_again"]],
               "expected_cases_not_red": [m["mutant_id"] for m in muts
                                          if not m["expected_cases_are_red"]]}
    wjson(out / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    ok = (summary["mutation_count"] == 20 and summary["all_mutants_red_again"]
          and summary["all_expected_cases_red"])
    return 0 if ok else 1


# --------------------------------------------------------------------------
# the four T1-F3-FIX mutation arms
# --------------------------------------------------------------------------
ARM_A = {
    "name": "MUT-F3-A: _parse restored to its PRE-fix body (catches nothing)",
    "old": '''def _parse(ts: str) -> datetime | None:
    """T1-F3-FIX: TOTAL over every JSON value (I-14-B oracle.md sec 11.8).

    A present-but-malformed timestamp used to raise ValueError out of here
    ("Invalid isoformat string: ..."), which escaped classify() into main()'s
    internal-error handler: rc=4, no report written, and the WHOLE batch left
    with zero adjudications - the same verdict-stripping shape as defect (1).
    A non-string or unparsable value now yields None instead; every consumer
    below treats None as "this field carries no timing fact", and classify()
    refuses that ONE case with the new R-TIMESTAMP-MALFORMED code (section
    11.8 is the code's only authorisation source; vocabulary 16 -> 17).
    """
    if not isinstance(ts, str):
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
''',
    "new": '''def _parse(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
''',
    "expect": "TS1..TS5 fall back to rc=4 / no report / 0 adjudications",
}
ARM_B = {
    "name": "MUT-F3-B: the new refusal code is removed",
    "old": 'refusals.append("%s")' % NEW_CODE,
    "new": "pass  # MUT-F3-B",
    "expect": "TS1..TS5 lose the new code and flip to accept_claim",
}
ARM_C = {
    "name": "MUT-F3-C: computed time echoes are not nulled",
    "old": "    if key not in fields:\n        return None\n    raw = fields[key]\n    return raw if _parse(raw) is not None else None",
    "new": "    return fields.get(key)",
    "expect": "TS1 / TS5 computed.started_at is the raw malformed string, not null",
}
ARM_D = {
    "name": "MUT-F3-D: the degraded observation-window path is removed",
    "old": "    if started is None:\n        obs_finished = None",
    "new": "    pass  # MUT-F3-D",
    "expect": "TS1 / TS5 (the cases whose started_at is unreadable) fall back to "
              "rc=4 (TypeError comparing None with a datetime); TS2/TS3/TS4 keep "
              "rc=0 because their started_at parses",
}
# per-arm red predicate: arm -> (cids that MUST be rc=4, cids that must NOT be)
ARM_RC4_CIDS = {1: ["TS1", "TS2", "TS3", "TS4", "TS5"], 4: ["TS1", "TS5"]}


def cmd_mutations(_args) -> int:
    out = EVID / "after" / "mutations"
    rmtree(out)
    src = SUT.read_text(encoding="utf-8")
    arms = [ARM_A, ARM_B, ARM_C, ARM_D]
    checks = []
    for i, arm in enumerate(arms, 1):
        occ = src.count(arm["old"])
        entry = {"arm": arm["name"], "anchor_occurrences": occ,
                 "expect": arm["expect"], "anchor_found_exactly_once": occ == 1}
        if occ != 1:
            entry["error"] = "anchor not found exactly once - arm NOT executed"
            checks.append({"name": arm["name"], "ok": False,
                           "detail": entry["error"]})
            wjson(out / f"arm{i}.json", entry)
            continue
        mutant_src = src.replace(arm["old"], arm["new"])
        mdir = out / f"arm{i}"
        mdir.mkdir(parents=True, exist_ok=True)
        mpath = mdir / "mutant_natural_window.py"
        mpath.write_text(mutant_src, encoding="utf-8")
        entry["mutant_sha256"] = sha(mpath)
        entry["mutant_bytes"] = mpath.stat().st_size
        entry["mutant_diff_lines"] = sum(
            1 for l in difflib.unified_diff(src.splitlines(),
                                            mutant_src.splitlines(), n=0)
            if l[:1] in "+-" and not l.startswith(("+++", "---")))
        runs = {}
        for cid, case in probe_cases().items():
            runs[cid] = run_sut(mpath, [case], mdir, cid)
        entry["runs"] = {cid: {"rc": r["raw_returncode"],
                               "report_written": r["report_written"],
                               "stdout_tail": r["stdout"].strip().splitlines()[-1][:300]
                               if r["stdout"].strip() else "",
                               "verdicts": (r["report"] or {}).get("verdicts")}
                         for cid, r in runs.items()}
        if i in ARM_RC4_CIDS:
            must = ARM_RC4_CIDS[i]
            ok = all(runs[c]["raw_returncode"] == 4
                     and not runs[c]["report_written"] for c in must)
            entry["rc4_required_on"] = must
        elif i == 2:
            ok = all((runs[c]["report"] or {}).get("verdicts", [{}])[0]
                     .get("verdict") == "accept_claim"
                     for c in probe_cases())
        else:  # arm 3
            v1 = (runs["TS1"]["report"] or {}).get("verdicts", [{}])[0]
            v5 = (runs["TS5"]["report"] or {}).get("verdicts", [{}])[0]
            ok = (v1.get("computed", {}).get("started_at") is not None
                  and v5.get("computed", {}).get("started_at") is not None)
        entry["arm_is_red_as_expected"] = ok
        checks.append({"name": arm["name"], "ok": ok,
                       "detail": json.dumps({c: entry["runs"][c]["rc"]
                                             for c in entry["runs"]})})
        wjson(out / f"arm{i}.json", entry)

    doc = {"arms": checks, "all_arms_red": all(c["ok"] for c in checks),
           "failed": [c["name"] for c in checks if not c["ok"]]}
    wjson(out / "results.json", doc)
    print(json.dumps(doc, indent=2))
    return 0 if doc["all_arms_red"] else 1


# --------------------------------------------------------------------------
# invariants
# --------------------------------------------------------------------------
def cmd_invariants(_args) -> int:
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)[:1500]})

    # --- pins -------------------------------------------------------------
    frz = json.loads((EVID / "freeze.json").read_text(encoding="utf-8"))
    now_pins = {rel: sha(WT / rel) for rel in PIN_EXPECT}
    changed = {k: (frz["harness_pins"][k]["sha256"], v)
               for k, v in now_pins.items()
               if frz["harness_pins"][k]["sha256"] != v}
    chk("I-7a harness pins byte-identical freeze -> after", not changed, changed)
    wrong = {k: v for k, v in now_pins.items() if v != PIN_EXPECT[k]}
    chk("I-7b harness pins still equal their dispatch values", not wrong, wrong)

    # --- oracle freeze (append-only erratum discipline) --------------------
    oracle = ATTEMPT / "oracle.md"
    raw = oracle.read_bytes()
    frozen_sha = frz["oracle"]["sha256"]
    frozen_bytes = frz["oracle"]["bytes"]
    prefix_sha = hashlib.sha256(raw[:frozen_bytes]).hexdigest()
    chk("oracle freeze: the text frozen before the first run is still an "
        "unbroken byte prefix (only an APPEND-ONLY erratum follows)",
        prefix_sha == frozen_sha and len(raw) > frozen_bytes,
        f"frozen={frozen_bytes}B sha={frozen_sha[:16]}.. now={len(raw)}B "
        f"prefix_sha={prefix_sha[:16]}..")

    # --- temporal: RED evidence predates the SUT edit ----------------------
    cut = SUT.stat().st_mtime
    late = [str(p.relative_to(EVID)) for p in (EVID / "before").rglob("*")
            if p.is_file() and p.stat().st_mtime > cut + 1.0]
    chk("temporal: every evidence/before artefact predates the SUT edit "
        "(RED was genuinely measured on the pre-fix image)",
        not late, late[:12])
    chk("baseline copy still byte-identical to the recorded left image",
        sha(BASELINE) == frz["sut_baseline"]["sha256"]
        == "9b1ebda2b75c4d1124d0d20a95d7a16cb31b8d9564c1c90da9b4d2d77eaa3ba2",
        sha(BASELINE))

    # --- vocabulary -------------------------------------------------------
    vb = json.loads((EVID / "before" / "vocab.json").read_text(encoding="utf-8"))
    va = json.loads((EVID / "after" / "vocab.json").read_text(encoding="utf-8"))
    chk("I-3 vocabulary 16 -> 17 with only R-TIMESTAMP-MALFORMED added",
        vb["count"] == 16 and va["count"] == 17
        and set(va["added_vs_baseline16"]) == {NEW_CODE}
        and not va["missing_vs_baseline16"],
        f"before={vb['count']} after={va['count']} added={va['added_vs_baseline16']}")

    # --- gates byte-identity ---------------------------------------------
    gb = json.loads((EVID / "before" / "gates" / "summary.json").read_text("utf-8"))
    ga = json.loads((EVID / "after" / "gates" / "summary.json").read_text("utf-8"))
    for label in ("r2", "r1"):
        b, a = gb["gates"][label], ga["gates"][label]
        keys = ("runner_rc", "ok", "mismatch_count", "case_count",
                "sut_raw_returncode", "sut_report_sha256", "mismatch_ids")
        diff = {k: (b[k], a[k]) for k in keys if b[k] != a[k]}
        chk(f"I-1 gate {label}: before == after on {keys}", not diff, diff)
    chk("I-1 gate r2 is green (rc=0, ok, 34/34, mismatch=0)",
        ga["gates"]["r2"]["runner_rc"] == 0 and ga["gates"]["r2"]["ok"] is True
        and ga["gates"]["r2"]["mismatch_count"] == 0
        and ga["gates"]["r2"]["case_count"] == 34, ga["gates"]["r2"])

    # --- suites -----------------------------------------------------------
    sb = json.loads((EVID / "before" / "suites" / "suites_summary.json").read_text("utf-8"))
    sa = json.loads((EVID / "after" / "suites" / "suites_summary.json").read_text("utf-8"))
    for suite in SUITES:
        b, a = sb["suites"][suite], sa["suites"][suite]
        chk(f"I-1 suite {suite}: before == after and 0 failures",
            b["passed"] == a["passed"] and b["failed"] == a["failed"] == 0
            and b["errors"] == a["errors"] == 0 and a["pytest_rc"] == 0,
            f"before={b} after={a}")
    nb, na = sb["suites"][NEW_SUITE], sa["suites"][NEW_SUITE]
    chk("I-1 new suite RED before (failures > 0) / GREEN after (0 failures)",
        nb["failed"] + nb["errors"] > 0 and na["failed"] == na["errors"] == 0
        and na["pytest_rc"] == 0 and na["passed"] >= 15,
        f"before={nb} after={na}")

    # --- 20 arms ----------------------------------------------------------
    for phase in ("before", "after"):
        p = EVID / phase / "mut20" / "summary.json"
        if not p.exists():
            chk(f"mut20 {phase} present", False, "missing")
            continue
        s = json.loads(p.read_text(encoding="utf-8"))
        chk(f"mut20 {phase}: 20 arms all red / all expected cases red",
            s["mutation_count"] == 20 and s["all_mutants_red_again"]
            and s["all_expected_cases_red"], s)

    # --- NC-MISSING -------------------------------------------------------
    ncb = json.loads((EVID / "before" / "nc_missing" / "results.json").read_text("utf-8"))
    nca = json.loads((EVID / "after" / "nc_missing" / "results.json").read_text("utf-8"))
    rows_b = {k: v["verdict_json"] for k, v in ncb["rows"].items()}
    rows_a = {k: v["verdict_json"] for k, v in nca["rows"].items()}
    chk("I-2 NC-MISSING: 7 rows byte-identical before == after",
        rows_b == rows_a and sorted(rows_a) == sorted(NC_STABLE),
        json.dumps({k: (rows_b.get(k), rows_a.get(k)) for k in rows_a
                    if rows_b.get(k) != rows_a.get(k)}, ensure_ascii=False))
    chk("I-2 NC-MISSING: after-phase checks all pass",
        nca["checks_pass"], nca["failed"])

    # --- probes / batch / mutations --------------------------------------
    pb = json.loads((EVID / "before" / "probes" / "results.json").read_text("utf-8"))
    pa = json.loads((EVID / "after" / "probes" / "results.json").read_text("utf-8"))
    chk("step3 RED reproduced (all before checks pass)", pb["checks_pass"],
        pb["checks_failed"])
    chk("step7 GREEN (all after checks pass)", pa["checks_pass"],
        pa["checks_failed"])
    for phase in ("before", "after"):
        b = json.loads((EVID / phase / "batch" / "results.json").read_text("utf-8"))
        chk(f"batch {phase} negative control passes", b["checks_pass"], b["failed"])
    bb = json.loads((EVID / "before" / "batch" / "results.json").read_text("utf-8"))
    ba = json.loads((EVID / "after" / "batch" / "results.json").read_text("utf-8"))
    chk("B-BYTE-2: good-only report byte-identical before == after",
        bb["good_only_report_sha256"] == ba["good_only_report_sha256"],
        f"{bb['good_only_report_sha256']} vs {ba['good_only_report_sha256']}")
    mut = json.loads((EVID / "after" / "mutations" / "results.json").read_text("utf-8"))
    chk("mutation arms: all 4 red as expected", mut["all_arms_red"], mut["failed"])

    # --- line disjointness ------------------------------------------------
    dis = compute_disjointness()
    chk("I-6 line disjointness: my changed lines touch no foreign zone",
        dis["disjoint_from_all_foreign"], json.dumps(dis["foreign_hits"]))
    chk("I-6 line disjointness: _parse body zone is covered (my scope)",
        dis["parse_zone_touched"], dis["my_changed_or_inserted_on_L2"])

    # --- diff reversibility ----------------------------------------------
    diff_path = ATTEMPT / "changes.diff"
    if diff_path.exists():
        rev = verify_diff_reversibility(diff_path)
        chk("I-8 changes.diff applied to the left image reproduces the fixed SUT "
            "byte-for-byte", rev["sut_equal"], rev)
        chk("I-8 changes.diff rebuilds the new test file byte-for-byte",
            rev["test_equal"], rev)
        stats = diff_stats(diff_path)
        recorded = json.loads((ATTEMPT / "diff_stats.json").read_text(encoding="utf-8"))
        chk("I-8 diff_stats.json matches an independent recount "
            "(bytes / sha / added / removed / files)",
            recorded.get("bytes") == stats["bytes"]
            and recorded.get("sha256") == stats["sha256"]
            and recorded.get("lines_added") == stats["lines_added"]
            and recorded.get("lines_removed") == stats["lines_removed"]
            and recorded.get("files") == stats["files"],
            {"recorded": {k: recorded.get(k) for k in
                          ("bytes", "sha256", "lines_added", "lines_removed", "files")},
             "recount": stats})
    else:
        chk("changes.diff present", False, "missing")

    # --- boundary ---------------------------------------------------------
    gbnd = git_boundary()
    chk("I-9 git diff HEAD --name-only non-.planning count == 0",
        gbnd["non_planning"] == 0, gbnd)
    # two prerequisite cards untouched
    plan = ATTEMPT.parents[2]
    pre = {}
    for rel, expect in (("execution_runs/T1-10-FIX/a20260923-01/changes.diff",
                         "625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac"),
                        ("execution_runs/T1-10-FIX/a20260923-01/handoff.json",
                         "e6b9a94a40313b9ad600ba09011b64dfebb7d683b0b590fc4e2f78c10269433e"),
                        ("execution_runs/T1-F2-FIX/a20260923-01/changes.diff",
                         "bc87bf81bc53aad17f5c2f1047db467c64a92ec0b431499d94a438e8cbd3f3ca"),
                        ("execution_runs/T1-F2-FIX/a20260923-01/handoff.json",
                         "662b7895114399c19aaddee523cc4718bd0c662e8cfdc7660641dfa47e897904"),
                        ("execution_runs/I-14-B/a20260919-01/oracle.md",
                         "b1eb5d0cf83dd8f059d7f011427447a4b79b211c19167f0190b2c140cb34ade6")):
        got = sha(plan / rel)
        pre[rel] = {"expected": expect, "got": got, "equal": got == expect}
    chk("I-9 two prerequisite cards + I-14-B oracle byte-identical (0 writes)",
        all(v["equal"] for v in pre.values()), json.dumps(pre, indent=1))

    doc = {"checks": checks, "total": len(checks),
           "failed": [c["name"] for c in checks if not c["ok"]],
           "passed": sum(1 for c in checks if c["ok"]),
           "verdict": "PASS" if all(c["ok"] for c in checks) else "FAIL"}
    wjson(EVID / "after" / "invariants.json", doc)
    print(json.dumps({"total": doc["total"], "passed": doc["passed"],
                      "failed": doc["failed"], "verdict": doc["verdict"]},
                     indent=2))
    return 0 if doc["verdict"] == "PASS" else 1


FOREIGN_ZONES_ON_L2 = {
    "T1-10-FIX changed {67-75, 81, 214-224}": [(67, 75), (81, 81), (214, 224)],
    "T1-F2-FIX changed {56-63, 367-379, 461-476}": [(56, 63), (367, 379), (461, 476)],
    "defect-2 {189-212}": [(189, 212)],
}
PARSE_ZONE_ON_L2 = [(89, 95)]


def _hunks(left: Path, right: Path):
    l = left.read_text(encoding="utf-8").splitlines(keepends=True)
    r = right.read_text(encoding="utf-8").splitlines(keepends=True)
    sm = difflib.SequenceMatcher(None, l, r, autojunk=False)
    changed_old = []
    inserted_at = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            changed_old.append((i1 + 1, i2))
        elif tag == "insert":
            # conservative: the insertion sits between old 1-based lines i1 and
            # i1+1, so it is recorded as touching BOTH of those old lines.
            lo = max(1, i1)
            hi = i1 + 1
            inserted_at.append((lo, hi))
    return (sorted(x for x in changed_old + inserted_at if x[0] <= x[1]),
            sorted(x for x in changed_old if x[0] <= x[1]),
            sorted(x for x in inserted_at if x[0] <= x[1]))


def compute_disjointness() -> dict:
    zones, replaced, inserted = _hunks(BASELINE, SUT)
    hits = {}
    for name, zs in FOREIGN_ZONES_ON_L2.items():
        for a, b in zones:
            for c, d in zs:
                if a <= d and c <= b:
                    hits.setdefault(name, []).append({"my": [a, b], "zone": [c, d]})
    touched = any(a <= d and c <= b for a, b in zones
                  for c, d in PARSE_ZONE_ON_L2)
    doc = {"my_changed_or_inserted_on_L2": zones,
           "my_replaced_lines_on_L2": replaced,
           "my_insert_boundaries_on_L2": inserted,
           "foreign_zones_on_L2": {k: v for k, v in FOREIGN_ZONES_ON_L2.items()},
           "foreign_hits": hits,
           "disjoint_from_all_foreign": not hits,
           "parse_zone_on_L2": PARSE_ZONE_ON_L2,
           "parse_zone_touched": touched}
    wjson(EVID / "after" / "line_disjointness.json", doc)
    return doc


def verify_diff_reversibility(diff_path: Path) -> dict:
    lines = diff_path.read_text(encoding="utf-8").splitlines(keepends=True)
    files = {}
    cur = None
    hunks = {}
    i = 0
    hunk_re = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("--- "):
            name = ln[4:].strip()
            if name == "/dev/null":
                cur = None
            i += 1
            continue
        if ln.startswith("+++ b/"):
            cur = ln[6:].strip()
            hunks.setdefault(cur, [])
            i += 1
            continue
        m = hunk_re.match(ln)
        if m and cur:
            o1 = int(m.group(1)); oc = int(m.group(2) or 1)
            i += 1
            body = []
            od = nd = 0
            while i < len(lines) and (od < oc or nd < int(m.group(4) or 1)):
                b = lines[i]
                if b.startswith("\\"):
                    i += 1; continue
                if b.startswith("+"): nd += 1
                elif b.startswith("-"): od += 1
                elif b.startswith(" "): od += 1; nd += 1
                else: break
                body.append(b); i += 1
            hunks[cur].append((o1, oc, body))
            continue
        i += 1

    def apply(base_lines, hs):
        res, pos = [], 0
        for o1, oc, body in hs:
            start = o1 - 1
            res.extend(base_lines[pos:start])
            for b in body:
                if b.startswith(("+", " ")):
                    res.append(b[1:])
            pos = start + sum(1 for b in body if not b.startswith("+"))
        res.extend(base_lines[pos:])
        return "".join(res)

    base = BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
    got = apply(base, hunks.get("iso/natural_window.py", []))
    want = SUT.read_text(encoding="utf-8")
    test_path = HARNESS / "tests" / NEW_SUITE
    got_test = apply([], hunks.get(f"harness/tests/{NEW_SUITE}", []))
    return {"sut_equal": got == want,
            "sut_rebuilt_sha": hashlib.sha256(got.encode()).hexdigest(),
            "sut_want_sha": hashlib.sha256(want.encode()).hexdigest(),
            "test_equal": got_test == test_path.read_text(encoding="utf-8"),
            "files_in_diff": sorted(k for k, v in hunks.items() if v)}


def diff_stats(diff_path: Path) -> dict:
    text = diff_path.read_text(encoding="utf-8")
    added = sum(1 for l in text.splitlines() if l.startswith("+")
                and not l.startswith("+++"))
    removed = sum(1 for l in text.splitlines() if l.startswith("-")
                  and not l.startswith("---"))
    files = [l[6:].strip() for l in text.splitlines() if l.startswith("+++ b/")]
    return {"bytes": diff_path.stat().st_size,
            "sha256": sha(diff_path), "lines_added": added,
            "lines_removed": removed, "files": files, "n_files": len(files)}


def cmd_diff(_args) -> int:
    a_lines = BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
    b_lines = SUT.read_text(encoding="utf-8").splitlines(keepends=True)
    test_path = HARNESS / "tests" / NEW_SUITE
    n_lines = test_path.read_text(encoding="utf-8").splitlines(keepends=True)

    parts: list[str] = []
    parts.extend(difflib.unified_diff(a_lines, b_lines,
                                      fromfile="a/iso/natural_window.py",
                                      tofile="b/iso/natural_window.py"))
    parts.extend(difflib.unified_diff(
        [], n_lines, fromfile="/dev/null",
        tofile="b/harness/tests/" + NEW_SUITE))
    text = "".join(parts)
    p = ATTEMPT / "changes.diff"
    p.write_text(text, encoding="utf-8", newline="")
    stats = diff_stats(p)
    stats["files_touched"] = [
        {"path": "iso/natural_window.py",
         "change": "modified (_parse made total + per-case malformed-timestamp "
                   "refusal + computed time-field nulling + document-domain rc=2 guard)",
         "baseline_sha256": sha(BASELINE),
         "baseline_meaning": "T1-F2-FIX fixed iso = merge-order pre-image (9b1ebda2...)",
         "fixed_sha256": sha(SUT)},
        {"path": "harness/tests/" + NEW_SUITE,
         "change": "added (F-3 malformed-timestamp negative family)",
         "sha256": sha(test_path)},
    ]
    hunks = []
    for ln in parts:
        if ln.startswith("@@"):
            head = ln.splitlines()[0]
            tok = head.split()[1]
            first = tok.lstrip("-").split(",")[0]
            cnt = tok.lstrip("-").split(",")[1] if "," in tok else "1"
            start, count = int(first), int(cnt)
            hunks.append({"old_start": start, "old_count": count,
                          "old_range": [start, start + count - 1] if count
                          else [start, start]})
    stats["hunks"] = hunks
    stats["merge_order"] = ("T1-10-FIX 625ecfe4... first -> T1-F2-FIX bc87bf81... "
                            "second (left side of THIS diff = 9b1ebda2...) -> "
                            "this diff third")
    stats["no_git"] = True
    wjson(ATTEMPT / "diff_stats.json", stats)
    print(json.dumps(stats, indent=2))
    return 0


# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("freeze")
    for name in ("probes", "gates", "suites", "ncmissing", "vocab", "batch", "mut20"):
        p = sub.add_parser(name)
        p.add_argument("--phase", required=True, choices=("before", "after"))
        p.add_argument("--sut", default=str(SUT))
    sub.add_parser("mutations")
    sub.add_parser("invariants")
    sub.add_parser("diff")
    args = ap.parse_args()
    return {"freeze": cmd_freeze, "probes": cmd_probes, "gates": cmd_gates,
            "suites": cmd_suites, "ncmissing": cmd_ncmissing,
            "vocab": cmd_vocab, "batch": cmd_batch, "mut20": cmd_mut20,
            "mutations": cmd_mutations, "invariants": cmd_invariants,
            "diff": cmd_diff}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
