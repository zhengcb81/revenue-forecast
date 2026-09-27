"""T1-F2-FIX verification engine (a20260923-01).

Freezes-then-measures the repair of F-1 (J7 `clock_source` set-membership non-
total), F-2 (calendar `claim.status` carrier read non-total) and the expanded
P4 container family (windows / sampled_at / ledger list carriers).  Shapes and
expectations are frozen in ../oracle.md (base, written BEFORE any run) plus its
APPENDIX (P4 expansion, append-only before any run); this script only measures
against them.

Prerequisite layer: T1-10-FIX changes.diff 625ecfe4... (fixed iso 064e5381...).
The RED baseline (phase=before) IS that fixed iso; merge order = theirs first,
mine second, T1-F3-FIX third.

Subcommands
  pins       --write | --check        evidence/pin_hashes.sha256.tsv
  probe      --sut <path> --out-dir <dir> [--phase before|after]
             F-1 K1..K8 / F-2 S1..S10 / P4 W,S,L shapes / PT pending-routed rows
             / joint batches J1,J1b,J2,J3 / arms A,B,C,D + direct classify raws
  suites     --tree <i14b dir> --phase before|after --out-dir <dir>
             pytest r1 + r2 + T1-10-FIX's 23-test suite (I14B_SUT = tree iso)
  inherit    --sut <path> --phase before|after --out-dir <dir>
             T1-10-FIX's own probe script (byte-identical copy) -> its 39 checks
  reports    --sut <path> --phase before|after --out-dir <dir>
             frozen gates r2 (34) + r1 (20) through run_cases.py -> report bytes
  mutation   --sut <fixed> --baseline <pristine> --out-dir <dir>
             MUT-F1/F2/P4 guard reverts (crash must return) + anchor counts
  nc         --sut <fixed> --worktree <i14b dir> --out-dir <dir>
             PC + NC-1 (input poison) + NC-2 (declaration poison), raws on disk
  invariants --out <json> (reads evidence/before + evidence/after)

No git.  Writes only inside this attempt.  No timestamps in outputs
(idempotent evidence: same inputs -> same bytes).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent                      # .../T1-F2-FIX/a20260923-01
EXEC = ATTEMPT.parent.parent                        # .../execution_runs
PLAN = EXEC.parent                                  # .../2026-09-19-three-project-history-audit

assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN
assert (ATTEMPT / "oracle.md").is_file(), "FATAL: oracle.md missing (freeze first)"

FROZEN_NOW = "2026-09-20T02:56:38Z"
PY = sys.executable

# phase pairing guards -------------------------------------------------------
BASE_T1_10_FIXED_SHA = "064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d"
R2_BASELINE_SHA = "7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796"
ORACLE_SHA = "ea63701c288fdc890cd985b077dce37c4a53aebd438e1548add9d047714f30ce"

WT_AFTER = ATTEMPT / "worktree" / "i14b"
WT_BEFORE = ATTEMPT / "worktree_before" / "i14b"
HARNESS = WT_AFTER / "harness"
CASES_R2 = HARNESS / "cases.r2.json"

GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}

R_SIM = ["R-SIMULATED-CLOCK"]                 # oracle sec 2 J7
R_CLAIM = ["R-CLAIM-EXCEEDS"]                 # oracle sec 2 J11
R_NOSAMPLES = ["R-NO-SAMPLES"]                # oracle sec 2 J4
C1_REF = ["R-CLAIM-EXCEEDS", "R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-SAME-INSTANT"]
S8_REF = ["R-EMPTY-EVIDENCE", "R-FUTURE-CLOCK", "R-SAME-INSTANT"]

EMPTY_FIELDS = {"clock_source": "system_utc",
                "ledger": {"daily": [], "weekly": [], "monthly": [], "alerts": []}}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mtime_str(path: Path) -> str:
    try:
        import datetime as _dt
        return _dt.datetime.fromtimestamp(
            path.stat().st_mtime, _dt.timezone.utc).isoformat().replace(
            "+00:00", "Z")
    except OSError:
        return "<unreadable>"


def _deep(obj):
    return json.loads(json.dumps(obj))


def _cases_by_id() -> dict:
    doc = json.loads(CASES_R2.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in doc["cases"]}


CBY = _cases_by_id()
F_C1, F_C2, F_C3 = CBY["C1"]["fields"], CBY["C2"]["fields"], CBY["C3"]["fields"]
CLAIM_C1, CLAIM_C2, CLAIM_C3 = CBY["C1"]["claim"], CBY["C2"]["claim"], CBY["C3"]["claim"]


def _cal(cid: str, fields: dict, claim=_deep(CLAIM_C3), claim_present: bool = True) -> dict:
    case = {"case_id": cid, "class": "calendar", "requirement_id": "C-1",
            "fields": _deep(fields)}
    if claim_present:
        case["claim"] = claim
    return case


def _win(cid: str, fields: dict, claim) -> dict:
    return {"case_id": cid, "class": "window_accounting", "requirement_id": "W-1",
            "claim": claim, "fields": _deep(fields)}


def _c3(**over) -> dict:
    f = _deep(F_C3)
    f.update(over)
    return f


def _good(**over) -> dict:
    f = dict(GOOD_FIELDS)
    f.update(over)
    return f


# ---------------------------------------------------------------------------
# frozen shapes (oracle.md sec 2 K*/S*/J*/arms + APPENDIX A.2 P4/PT)
# ---------------------------------------------------------------------------

W_DICT = {"w1": {"window_id": "w1", "started_at": "2026-09-20T00:00:00Z",
                 "finished_at": "2026-09-20T00:29:00Z"}}
DAILY_ENTRY = {"run_id": "r1", "started_at": "2026-09-08T03:30:00Z", "ok": True,
               "report_sha256": "a" * 64}
W_LIST_W5 = [{"window_id": "a", "started_at": "2026-09-20T00:00:00Z",
              "finished_at": "2026-09-20T00:29:00Z"},
             {"window_id": "b", "started_at": "2026-09-20T00:20:00Z",
              "finished_at": "2026-09-20T00:40:00Z"}]
UNION_1740 = {"basis": "union_of_windows", "natural_observation_seconds": 1740.0}
UNION_2220 = {"basis": "union_of_windows", "natural_observation_seconds": 2220.0}
UNION_2400 = {"basis": "union_of_windows", "natural_observation_seconds": 2400.0}
SAMPLE_1740 = {"basis": "sample_span", "natural_observation_seconds": 1740.0}

K_TAMPER = {
    "K1": ["system_utc"],
    "K2": {"source": "system_utc"},
    "K3": [["x"]],
    "K4": "system_utc",
    "K5": "simulated_clock_advanced_by_7_days",
    "K6": 5,
    "K7": "<ABSENT>",
    "K8": True,
}

S_SHAPES = {                       # id -> (fields, claim, claim_present)
    "S1": (EMPTY_FIELDS, ["pending"], True),
    "S2": (F_C1, ["complete"], True),
    "S3": (F_C2, "pending", True),
    "S4": (F_C2, 5, True),
    "S5": (F_C2, True, True),
    "S6": (F_C3, ["pending"], True),
    "S7a": (F_C2, {}, True),
    "S7b": (F_C2, {"other": 1}, True),
    "S7c": (F_C2, None, False),
    "S8": (F_C1, {}, True),
    "S9": (F_C1, _deep(CLAIM_C1), True),
    "S10": (F_C2, _deep(CLAIM_C2), True),
}

CRASH_RAW = {                      # fragment expected in RED internal_error detail
    "K1": "unhashable type: 'list'",
    "K2": "unhashable type: 'dict'",
    "K3": "unhashable type: 'list'",
    "S1": "'list' object has no attribute 'get'",
    "S2": "'list' object has no attribute 'get'",
    "S3": "'str' object has no attribute 'get'",
    "S4": "'int' object has no attribute 'get'",
    "S5": "'bool' object has no attribute 'get'",
    "S6": "'list' object has no attribute 'get'",
    "P4-W1": "string indices must be integers",
    "P4-W2": "string indices must be integers",
    "P4-S1": "Invalid isoformat string: 'a'",
    "P4-L1": "string indices must be integers",
    "P4-L2": "string indices must be integers",
}

CRASH_SHAPES = list(CRASH_RAW)


def build_case(shape_id: str) -> dict:
    if shape_id.startswith("K"):
        tamper = K_TAMPER[shape_id]
        fields = _c3()
        if tamper == "<ABSENT>":
            fields.pop("clock_source", None)
        else:
            fields["clock_source"] = _deep(tamper)
        return _cal(shape_id, fields, _deep(CLAIM_C3))
    if shape_id.startswith("S"):
        fields, claim, present = S_SHAPES[shape_id]
        f = _deep(fields)
        f["clock_source"] = "system_utc"
        return _cal(shape_id, f, _deep(claim), claim_present=present)
    if shape_id == "P4-W1":
        return _win(shape_id, _good(windows=_deep(W_DICT)), _deep(UNION_1740))
    if shape_id == "P4-W2":
        return _win(shape_id, _good(windows=_deep(W_DICT)), _deep(UNION_2220))
    if shape_id == "P4-S1":
        return _win(shape_id, _good(sampled_at={"a": "2026-09-20T00:01:00Z"}),
                    _deep(UNION_1740))
    if shape_id == "P4-L1":
        f = _deep(F_C3)
        f["ledger"]["daily"] = {"d1": _deep(DAILY_ENTRY)}
        return _cal(shape_id, f, _deep(CLAIM_C3))
    if shape_id == "P4-L2":
        f = _deep(F_C2)
        f["ledger"]["daily"] = {"d1": _deep(DAILY_ENTRY)}
        return _cal(shape_id, f, _deep(CLAIM_C2))
    if shape_id == "P4-STAB-W":
        # oracle A.2: "windows 正常列表（W5 形，union 2400）" -> the literal W5
        # fixture (its own fields carry observation_finished_at=00:40 and no
        # quick_check keys, which is what makes the row a clean accept).
        return _win(shape_id, _deep(CBY["W5"]["fields"]), _deep(CBY["W5"]["claim"]))
    if shape_id == "P4-STAB-S":
        return _win(shape_id, _good(), _deep(SAMPLE_1740))
    if shape_id == "PT-1":
        f = _good()
        f["started_at"] = "not-a-timestamp"
        return _win(shape_id, f, _deep(UNION_1740))
    if shape_id == "PT-2":
        return _win(shape_id, _good(sampled_at=["not-a-timestamp"]), _deep(UNION_1740))
    raise KeyError(shape_id)


# composite batches / arms ---------------------------------------------------
WGOOD = _win("W-GOOD", _good(), _deep(UNION_1740))
C3GOOD = _cal("C3-GOOD", F_C3, _deep(CLAIM_C3))
C2GOOD = _cal("C2-GOOD", F_C2, _deep(CLAIM_C2))
BAD_F1 = _cal("BAD-F1", _c3(clock_source=["system_utc"]), _deep(CLAIM_C3))
BAD_F2 = _cal("BAD-F2", F_C2, ["pending"])
CONTRAST = _cal("BAD-STR-CONTRAST", _c3(clock_source="simulated_clock_advanced_by_7_days"),
                _deep(CLAIM_C3))
P4W2 = build_case("P4-W2")
P4S1 = build_case("P4-S1")
P4L1 = build_case("P4-L1")


def _batch(prefix: str, base: dict, n: int, bad_at: int, bad: dict) -> list:
    cases = []
    for i in range(n):
        item = _deep(base)
        item["case_id"] = "%s-%02d" % (prefix, i)
        cases.append(item)
    bad = _deep(bad)
    cases[bad_at] = bad
    return cases


BATCHES = {
    "J1": [WGOOD, C3GOOD, C2GOOD, BAD_F1, BAD_F2],
    "J1b": [WGOOD, C2GOOD, C3GOOD, BAD_F2, BAD_F1],
    "J2": [P4W2, P4S1, C3GOOD, P4L1, WGOOD],
    "J3": [WGOOD, C3GOOD, C2GOOD, BAD_F1, BAD_F2, P4W2, P4S1, P4L1],
    # NOTE (instrument conformance, see decision.md "instrument corrections"):
    # oracle sec 2 / A.2 freezes each arm as 6 GOODS + 1 BAD = 7 cases; the
    # first draft of _batch(n=6, replace-at-3) built only 6.  n=7 + replace
    # yields exactly 6 goods + 1 bad, which is what the frozen rows demand
    # (RED 0/7, GREEN 7/7).  Shapes/expectations themselves are NOT changed.
    "armA": _batch("CAL-OK", C3GOOD, 7, 3, BAD_F1),
    "armB": _batch("CAL-OK", C3GOOD, 7, 3, CONTRAST),
    "armC": [WGOOD, _deep(C3GOOD), _deep(C3GOOD), _deep(C2GOOD), _deep(C2GOOD),
             BAD_F1, BAD_F2],
    "armD": _batch("WIN-OK", WGOOD, 7, 3, P4S1),
}
# give armC goods distinct ids
for _i, _c in enumerate(BATCHES["armC"]):
    _c["case_id"] = ["W-GOOD", "C3-GOOD-1", "C3-GOOD-2", "C2-GOOD-1", "C2-GOOD-2",
                     "BAD-F1", "BAD-F2"][_i]

BATCH_IDS = {k: [c["case_id"] for c in v] for k, v in BATCHES.items()}


# ---------------------------------------------------------------------------
# CLI / direct invocation raws
# ---------------------------------------------------------------------------

def invoke_cli(sut: Path, cases: list, raw_dir: Path, tag: str) -> dict:
    raw_dir.mkdir(parents=True, exist_ok=True)
    cases_path = raw_dir / f"{tag}.cases.json"
    report_path = raw_dir / f"{tag}.report.json"
    cases_path.write_text(json.dumps({"frozen_now_utc": FROZEN_NOW, "cases": cases},
                                     ensure_ascii=False), encoding="utf-8")
    if report_path.exists():
        report_path.unlink()
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", str(sut), "--cases", str(cases_path),
         "--report", str(report_path)],
        capture_output=True, text=True)
    (raw_dir / f"{tag}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (raw_dir / f"{tag}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    (raw_dir / f"{tag}.rc.txt").write_text(str(proc.returncode), encoding="utf-8")
    report = None
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    row = {"rc": proc.returncode, "report_written": report is not None,
           "stdout_head": proc.stdout[:300], "stderr_nonempty": bool(proc.stderr)}
    if report is not None:
        row.update({
            "case_count": report["case_count"],
            "cases_decided": len(report["verdicts"]),
            "verdicts": report["verdicts"],
        })
    else:
        row.update({"case_count": None, "cases_decided": 0, "verdicts": None})
    if report is not None and len(report["verdicts"]) == 1:
        v = report["verdicts"][0]
        row["verdict"] = v["verdict"]
        row["refusals"] = v["refusals"]
        row["computed"] = v["computed"]
    else:
        row["verdict"] = "<batch>" if report is not None else None
        row["refusals"] = None
        row["computed"] = None
    return row


DIRECT_CODE = r'''
import importlib.util, json, sys, traceback
from datetime import datetime
sut, frozen_now, case_json = sys.argv[1], sys.argv[2], sys.argv[3]
case = json.loads(case_json)
spec = importlib.util.spec_from_file_location("sut_probe", sut)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
ts = frozen_now[:-1] + "+00:00" if frozen_now.endswith("Z") else frozen_now
fn = datetime.fromisoformat(ts)
try:
    got = m.classify(case, fn, 5.0, 5.0)
    print(json.dumps({"raised": False, "verdict": got["verdict"],
                      "refusals": got["refusals"]}))
except Exception as exc:
    print(json.dumps({"raised": True, "type": type(exc).__name__, "msg": str(exc),
                      "traceback": traceback.format_exc()}))
'''


def invoke_direct(sut: Path, case: dict, raw_dir: Path, tag: str) -> dict:
    raw_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", "-c", DIRECT_CODE, str(sut), FROZEN_NOW,
         json.dumps(case)],
        capture_output=True, text=True)
    (raw_dir / f"{tag}.direct.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    try:
        row = json.loads(proc.stdout)
    except Exception:
        row = {"raised": None, "parse_error": True, "stdout": proc.stdout[:500]}
    (raw_dir / f"{tag}.direct.json").write_text(
        json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    return row


def rejected_ids(row: dict) -> list:
    return sorted(v["case_id"] for v in (row.get("verdicts") or [])
                  if v["verdict"] == "reject_claim")


def accepted_ids(row: dict) -> list:
    return sorted(v["case_id"] for v in (row.get("verdicts") or [])
                  if v["verdict"] == "accept_claim")


def verdict_of(row: dict, cid: str) -> dict:
    for v in (row.get("verdicts") or []):
        if v["case_id"] == cid:
            return v
    return {}


# ---------------------------------------------------------------------------
# probe
# ---------------------------------------------------------------------------

STABLE_EXPECT = {                 # must hold in BOTH phases, rows byte-equal
    "K4": ("accept_claim", []),
    "K5": ("reject_claim", R_SIM),
    "K6": ("reject_claim", R_SIM),
    "K7": ("reject_claim", R_SIM),
    "K8": ("reject_claim", R_SIM),
    "S7a": ("accept_claim", []),
    "S7b": ("accept_claim", []),
    "S7c": ("accept_claim", []),
    "S8": ("reject_claim", S8_REF),
    "S9": ("reject_claim", C1_REF),
    "S10": ("accept_claim", []),
    "P4-STAB-W": ("accept_claim", []),
    "P4-STAB-S": ("accept_claim", []),
}

GREEN_EXPECT = {                  # after-phase expectations for crash shapes
    "K1": ("reject_claim", R_SIM),
    "K2": ("reject_claim", R_SIM),
    "K3": ("reject_claim", R_SIM),
    "S1": ("reject_claim", R_CLAIM),
    "S2": ("reject_claim", C1_REF),
    "S3": ("reject_claim", R_CLAIM),
    "S4": ("reject_claim", R_CLAIM),
    "S5": ("reject_claim", R_CLAIM),
    "S6": ("accept_claim", []),
    "P4-W1": ("accept_claim", []),
    "P4-W2": ("reject_claim", R_CLAIM),
    "P4-S1": ("reject_claim", R_NOSAMPLES),
    "P4-L1": ("reject_claim", R_CLAIM),
    "P4-L2": ("accept_claim", []),
}

PROBE_SHAPES = CRASH_SHAPES + list(STABLE_EXPECT) + ["PT-1", "PT-2"]


def cmd_probe(args) -> int:
    sut = Path(args.sut).resolve()
    out = Path(args.out_dir).resolve()
    raw = out / "raw"
    checks: list[dict] = []

    def check(name: str, holds: bool, detail: str = "") -> None:
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    sut_sha = sha256_file(sut)
    if args.phase == "before":
        assert sut_sha == BASE_T1_10_FIXED_SHA, (
            "before-phase must probe T1-10-FIX's fixed SUT (064e5381), got %s" % sut_sha)
    else:
        assert sut_sha not in (BASE_T1_10_FIXED_SHA, R2_BASELINE_SHA), (
            "after-phase must probe the FIXED SUT, got base sha %s" % sut_sha)

    rows: dict[str, dict] = {}
    for sid in PROBE_SHAPES:
        case = build_case(sid)
        row = invoke_cli(sut, [case], raw, sid)
        row["direct"] = invoke_direct(sut, case, raw, sid)
        rows[sid] = row

    for sid in CRASH_SHAPES:
        r = rows[sid]
        if args.phase == "before":
            check(f"RED {sid}: rc=4, no report, batch 0 decided",
                  r["rc"] == 4 and not r["report_written"] and r["cases_decided"] == 0,
                  f"rc={r['rc']} report={r['report_written']} decided={r['cases_decided']}")
            check(f"RED {sid}: raw internal_error = {CRASH_RAW[sid]!r}",
                  CRASH_RAW[sid] in r["stdout_head"],
                  r["stdout_head"][:160])
            check(f"RED {sid}: direct classify raises unhandled ({CRASH_RAW[sid]!r})",
                  r["direct"].get("raised") is True
                  and CRASH_RAW[sid] in str(r["direct"].get("msg")),
                  f"{r['direct'].get('type')}: {r['direct'].get('msg')}")
        else:
            want_v, want_r = GREEN_EXPECT[sid]
            check(f"GREEN {sid}: rc=0, report written, 1 decided",
                  r["rc"] == 0 and r["report_written"] and r["cases_decided"] == 1,
                  f"rc={r['rc']} report={r['report_written']}")
            check(f"GREEN {sid}: verdict {want_v} + refusals {want_r}",
                  r["verdict"] == want_v and r["refusals"] == want_r,
                  f"verdict={r['verdict']} refusals={r['refusals']}")
            check(f"GREEN {sid}: no internal_error, empty stderr, direct no-raise",
                  "internal_error" not in r["stdout_head"]
                  and not r["stderr_nonempty"] and r["direct"].get("raised") is False,
                  f"stdout={r['stdout_head'][:80]} direct={r['direct'].get('raised')}")

    for sid, (want_v, want_r) in STABLE_EXPECT.items():
        r = rows[sid]
        check(f"{args.phase} {sid}: stable {want_v} + {want_r} + rc=0",
              r["rc"] == 0 and r["verdict"] == want_v and r["refusals"] == want_r
              and r["direct"].get("raised") is False,
              f"rc={r['rc']} verdict={r['verdict']} refusals={r['refusals']}")

    # PT rows: timestamp-class, pending-routed to T1-F3-FIX -> recorded, no checks
    pt_rows = {sid: {k: rows[sid].get(k) for k in
                     ("rc", "report_written", "stdout_head", "verdict", "refusals")}
               for sid in ("PT-1", "PT-2")}

    check(f"{args.phase}: every probe row inside frozen rc domain {{0,4}}",
          all(rows[s]["rc"] in (0, 4) for s in PROBE_SHAPES),
          str({s: rows[s]["rc"] for s in PROBE_SHAPES}))

    # ---- batches / arms ---------------------------------------------------
    batch_rows = {k: invoke_cli(sut, v, raw, k) for k, v in BATCHES.items()}
    if args.phase == "before":
        for k in ("J1", "J1b", "J2", "J3", "armA", "armC", "armD"):
            r = batch_rows[k]
            n = len(BATCHES[k])
            check(f"RED {k}: single malformed case destroys all {n} verdicts "
                  f"(rc=4, 0 decided)",
                  r["rc"] == 4 and r["cases_decided"] == 0,
                  f"rc={r['rc']} decided={r['cases_decided']} "
                  f"raw={r['stdout_head'][:120]}")
        b = batch_rows["armB"]
        check("RED armB contrast: untrusted STRING clock refuses only itself "
              "(pre-existing correct refusal)",
              b["rc"] == 0 and b["cases_decided"] == 7
              and rejected_ids(b) == ["BAD-STR-CONTRAST"],
              f"rc={b['rc']} rejected={rejected_ids(b)}")
        check("RED J1b: raw names the claim-carrier crash (BAD-F2 first)",
              "'list' object has no attribute 'get'" in batch_rows["J1b"]["stdout_head"],
              batch_rows["J1b"]["stdout_head"][:160])
        check("RED J2: raw names the windows container crash (P4-W2 first)",
              "string indices must be integers" in batch_rows["J2"]["stdout_head"],
              batch_rows["J2"]["stdout_head"][:160])
    else:
        def green_batch(k: str, want_rejected: list) -> None:
            r = batch_rows[k]
            n = len(BATCHES[k])
            check(f"GREEN {k}: rc=0, {n}/{n} decided, only-BAD rejected",
                  r["rc"] == 0 and r["cases_decided"] == n
                  and rejected_ids(r) == sorted(want_rejected)
                  and len(accepted_ids(r)) == n - len(want_rejected),
                  f"rc={r['rc']} decided={r['cases_decided']} "
                  f"rejected={rejected_ids(r)} accepted={accepted_ids(r)}")
            check(f"GREEN {k}: no internal_error, empty stderr",
                  "internal_error" not in r["stdout_head"] and not r["stderr_nonempty"],
                  r["stdout_head"][:120])

        green_batch("J1", ["BAD-F1", "BAD-F2"])
        green_batch("J1b", ["BAD-F1", "BAD-F2"])
        green_batch("J2", ["P4-W2", "P4-S1", "P4-L1"])
        green_batch("J3", ["BAD-F1", "BAD-F2", "P4-W2", "P4-S1", "P4-L1"])
        green_batch("armA", ["BAD-F1"])
        green_batch("armC", ["BAD-F1", "BAD-F2"])
        green_batch("armD", ["P4-S1"])
        b = batch_rows["armB"]
        check("GREEN armB contrast: unchanged (refuses only itself)",
              b["rc"] == 0 and b["cases_decided"] == 7
              and rejected_ids(b) == ["BAD-STR-CONTRAST"],
              f"rc={b['rc']} rejected={rejected_ids(b)}")
        check("GREEN J1: BAD-F1 refusal = R-SIMULATED-CLOCK, BAD-F2 = R-CLAIM-EXCEEDS",
              verdict_of(batch_rows["J1"], "BAD-F1").get("refusals") == R_SIM
              and verdict_of(batch_rows["J1"], "BAD-F2").get("refusals") == R_CLAIM,
              json.dumps({cid: verdict_of(batch_rows["J1"], cid).get("refusals")
                          for cid in ("BAD-F1", "BAD-F2")}, ensure_ascii=False))
        check("GREEN J2: P4-W2/P4-S1/P4-L1 refusal classes per oracle vocabulary",
              verdict_of(batch_rows["J2"], "P4-W2").get("refusals") == R_CLAIM
              and verdict_of(batch_rows["J2"], "P4-S1").get("refusals") == R_NOSAMPLES
              and verdict_of(batch_rows["J2"], "P4-L1").get("refusals") == R_CLAIM,
              json.dumps({cid: verdict_of(batch_rows["J2"], cid).get("refusals")
                          for cid in ("P4-W2", "P4-S1", "P4-L1")}, ensure_ascii=False))

    doc = {"card": "T1-F2-FIX", "attempt_id": "a20260923-01", "phase": args.phase,
           "sut_path": str(sut), "sut_sha256": sut_sha,
           "shapes": rows,
           "pending_routed_timestamp_rows": pt_rows,
           "batches": batch_rows,
           "batch_ids": BATCH_IDS,
           "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    out.mkdir(parents=True, exist_ok=True)
    (out / "family_results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"phase": args.phase, "overall": doc["overall"],
                      "checks": len(checks), "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


# ---------------------------------------------------------------------------
# suites (pytest) / inherit (T1-10-FIX probe) / reports (frozen gates)
# ---------------------------------------------------------------------------

SUITES = {
    "suite_r1": "harness/tests/test_i14b_natural_window.py",
    "suite_r2": "harness/tests/test_i14b_natural_window_r2.py",
    "suite_basis23": "harness/tests/test_i14b_natural_window_basis_total.py",
    "suite_container29": "harness/tests/test_i14b_natural_window_container_total.py",
}
# inherited suites must be green in BOTH phases; the NEW suite is RED before by design
INHERITED_SUITES = ("suite_r1", "suite_r2", "suite_basis23")
NEW_SUITE = "suite_container29"


def cmd_suites(args) -> int:
    tree = Path(args.tree).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Basetemp root v2: _pytest_tmp still holds two EMPTY, UN-deletable
    # directories (before_suite_basis23 / before_suite_container29) left behind
    # by the first before-phase run, where pytest's own
    # `basetemp.mkdir(mode=0o700)` produced a directory this sandbox maps to an
    # ACL the creating user cannot list or remove (PermissionError WinError 5).
    # They are kept as quirk evidence; the root therefore moved one level over
    # so a fresh generation of basetemps can be created (and cleaned up) again.
    basetemp_parent = ATTEMPT / "_pytest_tmp2"
    basetemp_parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["I14B_SUT"] = str(tree / "iso" / "natural_window.py")
    # load the attempt-local plugin that widens pytest's 0o700 basetemp mode
    env["PYTHONPATH"] = str(SCRIPT.parent) + os.pathsep + env.get("PYTHONPATH", "")
    summary = {}
    for name, rel in SUITES.items():
        suite = tree / rel
        assert suite.is_file(), "missing suite %s" % suite
        basetemp = basetemp_parent / f"{args.phase}_{name}"
        proc = subprocess.run(
            [PY, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
             "-p", "pytest_tmp_acl_plugin",
             "--basetemp", str(basetemp), "-q", str(suite)],
            capture_output=True, env=env, cwd=str(tree))
        (out / f"{name}.stdout.txt").write_bytes(proc.stdout)
        (out / f"{name}.stderr.txt").write_bytes(proc.stderr)
        text = proc.stdout.decode("utf-8", errors="replace")
        m_fail = re.search(r"(\d+) failed", text)
        m_pass = re.search(r"(\d+) passed", text)
        m_err = re.search(r"(\d+) error", text)
        summary[name] = {
            "rc": proc.returncode,
            "failed": int(m_fail.group(1)) if m_fail else 0,
            "passed": int(m_pass.group(1)) if m_pass else 0,
            "errors": int(m_err.group(1)) if m_err else 0,
            "suite": rel, "sut": env["I14B_SUT"],
        }
    (out / "suites_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.phase == "before":
        # the NEW container suite is RED on the pre-fix tree by design; the three
        # inherited suites must already be green there (T1-10-FIX fixed state)
        ok = all(summary[n]["failed"] == 0 and summary[n]["errors"] == 0
                 for n in INHERITED_SUITES)
        ok = ok and summary[NEW_SUITE]["failed"] >= 10      # RED = defect proof
    else:
        ok = all(v["failed"] == 0 and v["errors"] == 0 for v in summary.values())
    return 0 if ok else 3


def cmd_inherit(args) -> int:
    sut = Path(args.sut).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    script = SCRIPT.parent / "inherit_probe_t1_10_fix.py"
    assert script.is_file(), "missing inherited probe copy: %s" % script
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", str(script), "probe", "--phase", "after",
         "--sut", str(sut), "--out-dir", str(out)],
        capture_output=True, text=True)
    (out / "inherit.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (out / "inherit.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    (out / "inherit.rc.txt").write_text(str(proc.returncode), encoding="utf-8")
    try:
        printed = json.loads(proc.stdout)
    except Exception:
        printed = {}
    result = {"rc": proc.returncode,
              "t1_10_probe_checks": printed.get("checks"),
              "t1_10_probe_overall": printed.get("overall"),
              "t1_10_probe_failed": printed.get("failed"),
              "sut_sha256": sha256_file(sut)}
    fr = out / "family_results.json"
    if fr.is_file():
        theirs = json.loads(fr.read_text(encoding="utf-8"))
        result["t1_10_adjacent_rows"] = theirs.get("adjacent_discovery")
        result["t1_10_checks_len"] = len(theirs.get("checks", []))
        result["t1_10_failed"] = theirs.get("failed_checks")
    (out / "inherit_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if (result.get("t1_10_probe_overall") == "PASS"
                 and not result.get("t1_10_probe_failed")) else 3


def _run_gate(sut: Path, cases: Path, expectations: Path, out_dir: Path,
              label: str) -> dict:
    runner = HARNESS / "run_cases.py"
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", str(runner), "--sut", str(sut),
         "--cases", str(cases), "--expectations", str(expectations),
         "--out-dir", str(out_dir), "--label", label],
        capture_output=True, text=True)
    (out_dir / "runner.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (out_dir / "runner.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    (out_dir / "runner.rc.txt").write_text(str(proc.returncode), encoding="utf-8")
    gate = json.loads((out_dir / "cases_report.json").read_text(encoding="utf-8"))
    return {"runner_rc": proc.returncode, "gate_ok": gate.get("ok"),
            "mismatch_count": gate.get("mismatch_count"),
            "accepted_ineligible_count": gate.get("accepted_ineligible_count"),
            "case_count": gate.get("case_count"),
            "sut_raw_returncode": gate.get("sut_raw_returncode"),
            "cases_sha256": gate.get("cases_sha256"),
            "expectations_sha256": gate.get("expectations_sha256"),
            "sut_report_sha256": sha256_file(out_dir / "sut_report.json")
            if (out_dir / "sut_report.json").is_file() else None,
            "mismatch_case_ids": sorted({m.get("case_id")
                                         for m in gate.get("mismatches", [])})}


def cmd_reports(args) -> int:
    sut = Path(args.sut).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    r2 = _run_gate(sut, HARNESS / "cases.r2.json", HARNESS / "frozen_expectations.r2.json",
                   out / "cmd-CASES-r2", "r2-frozen-gate")
    r1 = _run_gate(sut, HARNESS / "cases.json", HARNESS / "frozen_expectations.json",
                   out / "cmd-CASES-r1", "r1-frozen-gate")
    doc = {"phase": args.phase, "sut_sha256": sha256_file(sut),
           "r2_gate": r2, "r1_gate": r1}
    (out / "reports_summary.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0 if (r2["gate_ok"] is True and r2["mismatch_count"] == 0) else 3


# ---------------------------------------------------------------------------
# mutation
# ---------------------------------------------------------------------------

MUT_ANCHORS = {
    "MUT-7-J7": "    if clock_source not in TRUSTED_CLOCKS:  # J7",
    "MUT-11-J11": '    if claim_status == "complete" and computed_status != "complete":  # J11',
    "MUT-15-J16": "    if basis not in BASIS_REGISTRY:  # J16 / P1",
    "MUT-16-P2": "        intervals = [(started, obs_finished)]",
    "sorted_TRUSTED": "sorted(TRUSTED_CLOCKS)",
    "TRUSTED_def": 'TRUSTED_CLOCKS = ("system_utc", "scheduler_trusted")',
    "BASIS_tuple_def": "BASIS_REGISTRY = (",
}

# exact fix blocks (frozen here so the MUT reverts target precisely these)
FIXED_TRUSTED = 'TRUSTED_CLOCKS = ("system_utc", "scheduler_trusted")'
BASELINE_TRUSTED = 'TRUSTED_CLOCKS = {"system_utc", "scheduler_trusted"}'

FIXED_F2_BLOCK = '''    claim = fields.get("_claim")
    if not isinstance(claim, dict):
        claim = {"status": "complete"}  # T1-F2-FIX F-2 fail-closed read surrogate
    claim_status = claim.get("status")'''
BASELINE_F2_LINE = '    claim_status = (fields.get("_claim") or {}).get("status")'

FIXED_P4_BLOCK = '''    fields = dict(case.get("fields") or {})
    # T1-F2-FIX (P4 container family): present-but-container carriers are
    # normalised at this single entry so EVERY read site (windows 2, sampled_at
    # 2, ledger 1+4) is total; absent keys stay untouched (byte-identical).
    for _key in ("windows", "sampled_at"):
        if _key in fields and not isinstance(fields[_key], list):
            fields[_key] = []
    if "ledger" in fields:
        _ledger = fields["ledger"]
        if not isinstance(_ledger, dict):
            fields["ledger"] = {}
        else:
            _ledger = dict(_ledger)
            for _sub in ("daily", "weekly", "monthly", "alerts"):
                if _sub in _ledger and not isinstance(_ledger[_sub], list):
                    _ledger[_sub] = []
            fields["ledger"] = _ledger
    fields["_claim"] = case.get("claim") or {}'''
BASELINE_P4_BLOCK = '''    fields = dict(case.get("fields") or {})
    fields["_claim"] = case.get("claim") or {}'''


def _crash_probe(sut: Path, shape: str, out: Path, tag: str) -> dict:
    row = invoke_cli(sut, [build_case(shape)], out / "raw", tag)
    return {"shape": shape, "rc": row["rc"], "report_written": row["report_written"],
            "cases_decided": row["cases_decided"], "stdout_head": row["stdout_head"]}


def cmd_mutation(args) -> int:
    fixed = Path(args.sut).resolve()
    baseline = Path(args.baseline).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    scratch = out / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    source = fixed.read_text(encoding="utf-8")
    base_source = baseline.read_text(encoding="utf-8")
    checks = []

    def check(name, holds, detail=""):
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    # MUT-A1: mutator anchor lines exactly-once and byte-identical before==after
    for aid, line in MUT_ANCHORS.items():
        if aid in ("TRUSTED_def",):
            check(f"MUT-A2: {aid} exactly-once in FIXED (tuple form)",
                  source.count(line) == 1, f"count={source.count(line)}")
            continue
        if aid == "BASIS_tuple_def":
            check(f"MUT-A2: {aid} exactly-once in fixed AND baseline "
                  f"(T1-10-FIX prerequisite not reverted)",
                  source.count(line) == 1 and base_source.count(line) == 1,
                  f"fixed={source.count(line)} base={base_source.count(line)}")
            continue
        cf, cb = source.count(line), base_source.count(line)
        check(f"MUT-A1: {aid} anchor exactly-once fixed==baseline==1 and identical",
              cf == 1 and cb == 1, f"fixed={cf} base={cb}")
    check("MUT-A1: baseline still carries the set form of TRUSTED_CLOCKS",
          base_source.count(BASELINE_TRUSTED) == 1,
          f"count={base_source.count(BASELINE_TRUSTED)}")
    check("MUT-A2: fix blocks present exactly-once in fixed SUT",
          source.count(FIXED_TRUSTED) == 1 and source.count(FIXED_F2_BLOCK) == 1
          and source.count(FIXED_P4_BLOCK) == 1,
          json.dumps({"trusted": source.count(FIXED_TRUSTED),
                      "f2": source.count(FIXED_F2_BLOCK),
                      "p4": source.count(FIXED_P4_BLOCK)}))

    arms = []

    def revert_arm(arm: str, fixed_block: str, base_block: str, shapes: tuple,
                   reverts: str) -> None:
        if source.count(fixed_block) != 1:
            check(f"{arm}: revert target found exactly once", False,
                  f"count={source.count(fixed_block)}")
            return
        mutant = source.replace(fixed_block, base_block)
        mpath = scratch / f"{arm}.py"
        mpath.write_text(mutant, encoding="utf-8")
        rows = [_crash_probe(mpath, s, out, f"{arm}_{s}") for s in shapes]
        crashed = all(r["rc"] == 4 and not r["report_written"]
                      and r["cases_decided"] == 0 for r in rows)
        check(f"{arm}: guard reverted -> crash RETURNS on every probed shape "
              f"(non-vacuous)", crashed, json.dumps(rows, ensure_ascii=False))
        arms.append({"arm": arm, "reverts": reverts, "mutant_sha256": sha256_file(mpath),
                     "probes": rows, "crash_returned": crashed})

    revert_arm("MUT-F1", FIXED_TRUSTED, BASELINE_TRUSTED,
               ("K1", "K2", "K3"), "TRUSTED_CLOCKS tuple -> set")
    revert_arm("MUT-F2", FIXED_F2_BLOCK, BASELINE_F2_LINE,
               ("S1", "S3"), "F-2 carrier guard -> original single line")
    revert_arm("MUT-P4", FIXED_P4_BLOCK, BASELINE_P4_BLOCK,
               ("P4-W2", "P4-S1", "P4-L1"), "P4 classify-entry normalisation removed")

    doc = {"card": "T1-F2-FIX", "attempt_id": "a20260923-01",
           "fixed_sut_sha256": sha256_file(fixed),
           "baseline_sut_sha256": sha256_file(baseline),
           "arms": arms, "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    (out / "mutation_results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"mutation": doc["overall"], "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


# ---------------------------------------------------------------------------
# negative control
# ---------------------------------------------------------------------------

def _run_runner(sut: Path, cases: Path, expectations: Path, out_dir: Path,
                label: str, raw: Path) -> dict:
    raw.mkdir(parents=True, exist_ok=True)
    runner = HARNESS / "run_cases.py"
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", str(runner), "--sut", str(sut),
         "--cases", str(cases), "--expectations", str(expectations),
         "--out-dir", str(out_dir), "--label", label],
        capture_output=True, text=True)
    (raw / f"{label}.runner.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (raw / f"{label}.runner.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    (raw / f"{label}.runner.rc.txt").write_text(str(proc.returncode), encoding="utf-8")
    gate_path = out_dir / "cases_report.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
    return {"runner_rc": proc.returncode, "gate_ok": gate.get("ok"),
            "mismatch_count": gate.get("mismatch_count"),
            "mismatch_case_ids": sorted({m.get("case_id")
                                         for m in gate.get("mismatches", [])}),
            "accepted_ineligible_count": gate.get("accepted_ineligible_count"),
            "cases_sha256": gate.get("cases_sha256"),
            "case_count": gate.get("case_count")}


def cmd_nc(args) -> int:
    sut = Path(args.sut).resolve()
    wt = Path(args.worktree).resolve()
    out = Path(args.out_dir).resolve()
    raw = out / "raw"
    out.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name, holds, detail=""):
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    harness = wt / "harness"
    cases_doc = json.loads((harness / "cases.r2.json").read_text(encoding="utf-8"))
    exp_doc = json.loads((harness / "frozen_expectations.r2.json").read_text(encoding="utf-8"))
    frozen_cases_sha = sha256_file(harness / "cases.r2.json")

    # ---- PC: unpoisoned gate must be GREEN --------------------------------
    pc = _run_runner(sut, harness / "cases.r2.json", harness / "frozen_expectations.r2.json",
                     out / "pc_runner", "PC-unpoisoned", raw)
    check("PC: unpoisoned gate green (rc=0 ok=true mismatch=0)",
          pc["runner_rc"] == 0 and pc["gate_ok"] is True and pc["mismatch_count"] == 0,
          f"rc={pc['runner_rc']} ok={pc['gate_ok']} mismatch={pc['mismatch_count']}")

    # ---- NC-1: INPUT-side poison (>=1 clock_source + >=1 claim.status) ----
    nc1 = json.loads(json.dumps(cases_doc))
    for c in nc1["cases"]:
        if c["case_id"] == "C3":
            c["fields"]["clock_source"] = ["system_utc"]        # clock payload poison
        if c["case_id"] == "C2":
            c["claim"] = ["pending"]                            # status carrier poison
    nc1_path = out / "nc1_cases_poisoned.json"
    nc1_path.write_text(json.dumps(nc1, ensure_ascii=False, indent=2), encoding="utf-8")
    sut_run = invoke_cli(sut, nc1["cases"], raw, "nc1_sut_batch")
    check("NC-1 SUT: machinery survives input poisoning (rc=0, 34/34 decided)",
          sut_run["rc"] == 0 and sut_run["cases_decided"] == 34,
          f"rc={sut_run['rc']} decided={sut_run['cases_decided']} "
          f"raw={sut_run['stdout_head'][:120]}")
    nc1_gate = _run_runner(sut, nc1_path, harness / "frozen_expectations.r2.json",
                           out / "nc1_runner", "NC-1-input-poison", raw)
    check("NC-1: gate NOT green on poisoned inputs (rc=1 ok=false; C3+C2 mismatched)",
          nc1_gate["runner_rc"] == 1 and nc1_gate["gate_ok"] is False
          and "C3" in nc1_gate["mismatch_case_ids"]
          and "C2" in nc1_gate["mismatch_case_ids"],
          f"rc={nc1_gate['runner_rc']} ok={nc1_gate['gate_ok']} "
          f"mismatched={nc1_gate['mismatch_case_ids']}")
    check("NC-1: sha channel also flags it (gate cases_sha != frozen pin)",
          nc1_gate.get("cases_sha256") != frozen_cases_sha,
          f"gate={nc1_gate.get('cases_sha256')} pin={frozen_cases_sha}")

    # ---- NC-2: DECLARATION-side poison (clock + claim.status declarations) -
    nc2 = json.loads(json.dumps(exp_doc))
    for cid in ("C5", "C4"):          # C5 = clock_source case, C4 = claim.status case
        nc2["expected"][cid]["verdict"] = "accept_claim"
        nc2["expected"][cid]["refusals"] = []
    nc2_path = out / "nc2_expectations_poisoned.json"
    nc2_path.write_text(json.dumps(nc2, ensure_ascii=False, indent=2), encoding="utf-8")
    nc2_gate = _run_runner(sut, harness / "cases.r2.json", nc2_path,
                           out / "nc2_runner", "NC-2-declaration-poison", raw)
    check("NC-2: gate NOT green on poisoned declarations (rc=1 ok=false, >=4 rows)",
          nc2_gate["runner_rc"] == 1 and nc2_gate["gate_ok"] is False
          and (nc2_gate["mismatch_count"] or 0) >= 4
          and {"C5", "C4"}.issubset(set(nc2_gate["mismatch_case_ids"])),
          f"rc={nc2_gate['runner_rc']} ok={nc2_gate['gate_ok']} "
          f"mismatch={nc2_gate['mismatch_count']} ids={nc2_gate['mismatch_case_ids']}")
    check("NC-2: not a T1-8-style fabricated green (never rc=0 with poison)",
          nc2_gate["runner_rc"] != 0, f"rc={nc2_gate['runner_rc']}")

    doc = {"card": "T1-F2-FIX", "attempt_id": "a20260923-01",
           "sut_sha256": sha256_file(sut),
           "t1_8_reference": "T1-8/a20260920-03 poisoned 11 declarations -> rc=0 / 11-11 "
                             "PASS_rejected = fabricated green; this surface must behave oppositely",
           "nc1_input_poison": {"clock_source": "C3 -> [\"system_utc\"]",
                                "claim_status": "C2 claim -> [\"pending\"]"},
           "nc2_declaration_poison": {"C5_clock": "verdict->accept refusals->[]",
                                      "C4_status": "verdict->accept refusals->[]"},
           "pc": pc, "nc1": nc1_gate, "nc2": nc2_gate,
           "nc1_sut_rc": sut_run["rc"], "nc1_sut_decided": sut_run["cases_decided"],
           "frozen_cases_sha256": frozen_cases_sha,
           "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    (out / "nc_results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"negative_control": doc["overall"],
                      "failed": doc["failed_checks"]}, ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


# ---------------------------------------------------------------------------
# pins + invariants
# ---------------------------------------------------------------------------

PIN_TARGETS = [
    # (label, path relative to ATTEMPT or absolute-planned, immutable?)
    ("worktree_before/i14b/iso/natural_window.py", True),          # RED image 064e5381
    ("worktree/baseline/natural_window.t1_10fixed.pristine.py", True),  # diff left
    ("worktree_before/i14b/harness/run_cases.py", True),
    ("worktree_before/i14b/harness/mutate.r2.py", True),
    ("worktree_before/i14b/harness/cases.json", True),
    ("worktree_before/i14b/harness/cases.r2.json", True),
    ("worktree_before/i14b/harness/frozen_expectations.json", True),
    ("worktree_before/i14b/harness/frozen_expectations.r2.json", True),
    ("worktree_before/i14b/harness/tests/test_i14b_natural_window.py", True),
    ("worktree_before/i14b/harness/tests/test_i14b_natural_window_r2.py", True),
    ("worktree_before/i14b/harness/tests/test_i14b_natural_window_basis_total.py", True),
    ("worktree_before/i14b/oracle.md", True),
    ("worktree_before/i14b/review.md", True),
    ("worktree_before/i14b/changes.r2.diff", True),
    ("worktree/i14b/harness/run_cases.py", True),
    ("worktree/i14b/harness/mutate.r2.py", True),
    ("worktree/i14b/harness/cases.json", True),
    ("worktree/i14b/harness/cases.r2.json", True),
    ("worktree/i14b/harness/frozen_expectations.json", True),
    ("worktree/i14b/harness/frozen_expectations.r2.json", True),
    ("worktree/i14b/harness/tests/test_i14b_natural_window.py", True),
    ("worktree/i14b/harness/tests/test_i14b_natural_window_r2.py", True),
    ("worktree/i14b/harness/tests/test_i14b_natural_window_basis_total.py", True),
    ("worktree/i14b/oracle.md", True),
    ("worktree/i14b/review.md", True),
    ("worktree/i14b/changes.r2.diff", True),
    ("oracle.md", True),
    ("scripts/inherit_probe_t1_10_fix.py", True),
]

EXTERNAL_PINS = [
    ("T1-10 changes.diff (prerequisite)",
     EXEC / "T1-10-FIX" / "a20260923-01" / "changes.diff",
     "625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac"),
    ("T1-10 oracle.md",
     EXEC / "T1-10-FIX" / "a20260923-01" / "oracle.md",
     "afe8b61a3274e2473fe08db116e362bacf30e7c99facc90ec13d9453c929e4fb"),
    ("T1-10 decision.md",
     EXEC / "T1-10-FIX" / "a20260923-01" / "decision.md",
     "7adebb7a340a22b49afa67dec94cd8d3cfea2aee25792ca2c574fd0cea9f780d"),
    ("T1-10 handoff.json",
     EXEC / "T1-10-FIX" / "a20260923-01" / "handoff.json",
     "f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445"),
    ("T1-10 verify script (inherited copy source)",
     EXEC / "T1-10-FIX" / "a20260923-01" / "scripts" / "verify_t1_10_fix.py",
     "88f15ee66c6df28ffb528b1366f25d11d65b44e80a758256f52dbadcbb4515bf"),
    ("T1-10 after probe evidence (39 checks)",
     EXEC / "T1-10-FIX" / "a20260923-01" / "evidence" / "after" / "probes" / "family_results.json",
     "f7394f8c31fe2a02cc85cc624061de762fdbc2562701902f11d47f269334fbb1"),
    ("M-T-REVIEW t1_review_flips.md (T1-10 repair block)",
     EXEC / "M-T-REVIEW" / "a20260923-01" / "landing_package" / "t1_review_flips.md",
     "90bcefb9aadfe098dee1f16802bdf0af9ac7af9b2d74b21cc10a45e07b26c33b"),
    ("I-14-B r2 baseline SUT (source, read-only)",
     EXEC / "I-14-B" / "a20260919-01" / "iso" / "natural_window.py",
     R2_BASELINE_SHA),
]


def _pin_rows() -> list:
    rows = []
    for rel, _immutable in PIN_TARGETS:
        p = ATTEMPT / rel
        rows.append((rel, sha256_file(p) if p.is_file() else "<absent>"))
    for label, path, _want in EXTERNAL_PINS:
        rows.append((str(path), sha256_file(path) if path.is_file() else "<absent>"))
    return rows


def cmd_pins(args) -> int:
    out = ATTEMPT / "evidence" / "pin_hashes.sha256.tsv"
    if args.mode == "write":
        rows = _pin_rows()
        text = "".join(f"{sha}\t{rel}\n" for rel, sha in rows)
        out.write_text(text, encoding="utf-8", newline="")
        print(json.dumps({"wrote": str(out), "pins": len(rows)}, indent=2))
        return 0
    # check
    assert out.is_file(), "pin table missing; run pins --write first"
    stored = {}
    for line in out.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        sha, rel = line.split("\t", 1)
        stored[rel] = sha
    mismatches = []
    for rel, sha in _pin_rows():
        if stored.get(rel) != sha:
            mismatches.append({
                "path": rel,
                "scope": "external" if Path(rel).is_absolute()
                         else "attempt_internal",
                "stored": stored.get(rel),
                "now": sha,
                "mtime": _mtime_str(Path(rel) if Path(rel).is_absolute()
                                    else ATTEMPT / rel),
            })
    internal = [m for m in mismatches if m["scope"] == "attempt_internal"]
    external = [m for m in mismatches if m["scope"] == "external"]
    doc = {
        "pins": len(stored),
        "attempt_internal_mismatches": internal,
        "external_carrier_drift": external,
        "attempt_internal_ok": not internal,
        "external_drift_disclosed_not_repinned": True,
        "ok": not internal,
        "note": "attempt-internal pins are this card's frozen inputs and must "
                "never move; external carriers belong to other cards and are "
                "disclosed here with both shas + mtime instead of re-pinned "
                "(re-writing this table would destroy the evidence it exists "
                "to provide)",
    }
    check_out = ATTEMPT / "evidence" / "boundary_check.json"
    check_out.write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0 if not internal else 3


def _changed_old_lines(baseline: str, fixed: str) -> list:
    old_lines = baseline.splitlines(keepends=True)
    new_lines = fixed.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    changed: list[int] = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            changed.extend(range(i1 + 1, i2 + 1))     # 1-based old line numbers
    return changed


def cmd_invariants(args) -> int:
    out = Path(args.out).resolve()
    before_dir = ATTEMPT / "evidence" / "before"
    after_dir = ATTEMPT / "evidence" / "after"
    baseline_path = ATTEMPT / "worktree" / "baseline" / "natural_window.t1_10fixed.pristine.py"
    fixed_path = WT_AFTER / "iso" / "natural_window.py"
    checks = []

    def check(name, holds, detail=""):
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    baseline = baseline_path.read_text(encoding="utf-8")
    fixed = fixed_path.read_text(encoding="utf-8")

    # --- changed-line zones (merge-order / F-3 disjointness) ---------------
    changed = _changed_old_lines(baseline, fixed)
    forbidden = (list(range(60, 75))       # T1-10-FIX registry/comment block
                 + list(range(207, 218))   # T1-10-FIX E1 carrier guard block
                 + list(range(182, 206))   # defect-2 quick_check/J15/J6 zone (fixed numbering)
                 + list(range(82, 89))     # _parse timestamp zone (T1-F3-FIX third layer))
                 )
    overlap = sorted(set(changed) & set(forbidden))
    check("I-6/I-10: changed lines disjoint from T1-10-FIX blocks {60-74,207-217}, "
          "defect-2 zone 182-205, and _parse zone 82-88 (F-3 third layer)",
          overlap == [], f"changed={changed} overlap={overlap}")
    allowed = sorted(set(range(50, 60)) | set(range(354, 365)) | set(range(439, 447)))
    check("I-6: changed lines confined to this card's three hunk zones "
          "{50-59, 354-364, 439-446}",
          set(changed).issubset(set(allowed)), f"changed={changed}")

    # --- prerequisite layer intact ----------------------------------------
    check("prereq: T1-10-FIX fix blocks still present in fixed SUT",
          fixed.count("BASIS_REGISTRY = (") == 1
          and fixed.count('claim = fields.get("_claim")\n    if not isinstance(claim, dict):'
                          '\n        claim = {}\n    basis = claim.get("basis")') == 1,
          "")
    check("prereq: T1-10-FIX changes.diff still at pinned sha 625ecfe4...",
          sha256_file(EXEC / "T1-10-FIX" / "a20260923-01" / "changes.diff")
          == "625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac", "")

    # --- pins (immutability + read-only boundary) --------------------------
    # Split into (a) this attempt's OWN frozen inputs and (b) external carriers
    # owned by other cards.  (a) must never move; (b) is monitored and any
    # movement is disclosed verbatim instead of being silently re-pinned --
    # re-writing evidence/pin_hashes.sha256.tsv after a foreign write would
    # destroy exactly the evidence the table exists to provide.
    pin_file = ATTEMPT / "evidence" / "pin_hashes.sha256.tsv"
    stored = {}
    for line in pin_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            sha, rel = line.split("\t", 1)
            stored[rel] = sha
    bad = []
    for rel, sha_now in _pin_rows():
        if stored.get(rel) != sha_now:
            bad.append({"path": rel, "stored": stored.get(rel), "now": sha_now,
                        "scope": "external" if Path(rel).is_absolute()
                                 else "attempt_internal",
                        "mtime": _mtime_str(Path(rel) if Path(rel).is_absolute()
                                            else ATTEMPT / rel)})
    internal_bad = [m for m in bad if m["scope"] == "attempt_internal"]
    external_drift = [m for m in bad if m["scope"] == "external"]
    check(f"pins: {len(stored) - len(external_drift)} attempt-internal inputs "
          f"byte-unchanged across the whole run (source READ-ONLY = 0 writes)",
          not internal_bad,
          json.dumps(internal_bad, ensure_ascii=False)[:600])
    check("pins: every drifted input, if any, is an EXTERNAL carrier of another "
          "card and is disclosed below with both shas + mtime (never re-pinned)",
          all(m["scope"] == "external" for m in bad)
          and all(m["stored"] and m["now"] for m in bad),
          json.dumps(external_drift, ensure_ascii=False)[:900])

    # --- I-2: byte-identical normal-path reports --------------------------
    for gate, r2 in (("cmd-CASES-r2", True), ("cmd-CASES-r1", False)):
        b = before_dir / gate / "sut_report.json"
        a = after_dir / gate / "sut_report.json"
        bb = sha256_file(b) if b.is_file() else "<absent>"
        aa = sha256_file(a) if a.is_file() else "<absent>"
        check(f"I-2: {gate} SUT report byte-identical before==after", bb == aa,
              f"before={bb} after={aa}")

    def _summary(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}

    rb = _summary(before_dir / "reports_summary.json")
    ra = _summary(after_dir / "reports_summary.json")
    check("I-1: r2 frozen gate green before==after (rc0, mismatch0, 34/34)",
          rb.get("r2_gate", {}).get("gate_ok") is True
          and ra.get("r2_gate", {}).get("gate_ok") is True
          and rb.get("r2_gate", {}).get("mismatch_count") == 0
          and ra.get("r2_gate", {}).get("mismatch_count") == 0
          and rb.get("r2_gate", {}).get("cases_sha256")
          == ra.get("r2_gate", {}).get("cases_sha256"),
          json.dumps({"before": rb.get("r2_gate"), "after": ra.get("r2_gate")})[:400])
    fields = ("runner_rc", "gate_ok", "mismatch_count", "accepted_ineligible_count",
              "case_count", "sut_raw_returncode")
    r1_same = all(rb.get("r1_gate", {}).get(k) == ra.get("r1_gate", {}).get(k)
                  for k in fields)
    check("I-1: r1 gate fields before==after (pre-existing superseded delta, not ours)",
          r1_same, json.dumps({k: [rb.get("r1_gate", {}).get(k),
                                   ra.get("r1_gate", {}).get(k)] for k in fields})[:400])

    # --- stable probe rows byte-equal --------------------------------------
    bf = _summary(before_dir / "probes" / "family_results.json")
    af = _summary(after_dir / "probes" / "family_results.json")
    stable = list(STABLE_EXPECT)
    for sid in stable:
        brow = {k: bf.get("shapes", {}).get(sid, {}).get(k)
                for k in ("rc", "verdict", "refusals", "verdicts")}
        arow = {k: af.get("shapes", {}).get(sid, {}).get(k)
                for k in ("rc", "verdict", "refusals", "verdicts")}
        check(f"I-1: stable shape row {sid} byte-equal before==after", brow == arow,
              json.dumps({"before": brow, "after": arow}, ensure_ascii=False)[:300])
    for k in ("armB",):
        brow = {kk: bf.get("batches", {}).get(k, {}).get(kk)
                for kk in ("rc", "cases_decided", "verdicts")}
        arow = {kk: af.get("batches", {}).get(k, {}).get(kk)
                for kk in ("rc", "cases_decided", "verdicts")}
        check(f"I-1: arm {k} row byte-equal before==after", brow == arow, "")

    # --- PT pending-routed rows recorded (no adjudication) -----------------
    pt_before = bf.get("pending_routed_timestamp_rows", {})
    pt_after = af.get("pending_routed_timestamp_rows", {})
    check("I-10: PT-1/PT-2 recorded as pending-routed in both phases "
          "(observation only: rc recorded, NOT adjudicated by this card)",
          set(pt_before) == {"PT-1", "PT-2"} and set(pt_after) == {"PT-1", "PT-2"},
          json.dumps({"before": {k: v.get("rc") for k, v in pt_before.items()},
                      "after": {k: v.get("rc") for k, v in pt_after.items()}}))

    # --- I-2 refusal vocabulary -------------------------------------------
    code_re = re.compile(r'"(R-[A-Z0-9-]+)"')
    codes_before = sorted(set(code_re.findall(baseline)))
    codes_after = sorted(set(code_re.findall(fixed)))
    check("I-2: refusal-code vocabulary identical (no new R-*, no R-TIMESTAMP-*)",
          codes_before == codes_after,
          f"before={codes_before} after={codes_after}")

    # --- suites + inherit + mutation20 -------------------------------------
    sb = _summary(before_dir / "suites" / "suites_summary.json")
    sa = _summary(after_dir / "suites" / "suites_summary.json")
    for name in INHERITED_SUITES:
        bj, aj = sb.get(name, {}), sa.get(name, {})
        check(f"inherited family suite green before==after: {name} "
              f"(failed=0 both, passed equal)",
              bj.get("failed") == 0 and aj.get("failed") == 0
              and bj.get("errors") == 0 and aj.get("errors") == 0
              and bj.get("passed") == aj.get("passed"),
              json.dumps({"before": bj, "after": aj}, ensure_ascii=False))
    nb, na = sb.get(NEW_SUITE, {}), sa.get(NEW_SUITE, {})
    check("RED->GREEN: NEW container suite failed pre-fix "
          "(>=16 failed: F-1/F-2/P4 shapes) and fully green post-fix (29 passed)",
          nb.get("failed", 0) >= 16 and nb.get("passed", 0) == 13
          and na.get("failed") == 0 and na.get("passed") == 29,
          json.dumps({"before": nb, "after": na}, ensure_ascii=False))
    new_txt = after_dir / "suites" / f"{NEW_SUITE}.stdout.txt"
    if new_txt.is_file():
        check("RED->GREEN: post-fix NEW suite stdout has no FAILED lines",
              b"FAILED" not in new_txt.read_bytes(), "")

    ib = _summary(before_dir / "inherit" / "inherit_result.json")
    ia = _summary(after_dir / "inherit" / "inherit_result.json")
    check("inherit: T1-10-FIX's own probe 39/39 PASS on both trees "
          "(their 23-test basis family + arms unaffected)",
          ib.get("t1_10_probe_overall") == "PASS" and not ib.get("t1_10_probe_failed")
          and ia.get("t1_10_probe_overall") == "PASS" and not ia.get("t1_10_probe_failed")
          and ib.get("t1_10_probe_checks") == 39 and ia.get("t1_10_probe_checks") == 39,
          json.dumps({"before": {k: ib.get(k) for k in
                                 ("t1_10_probe_checks", "t1_10_probe_overall",
                                  "t1_10_probe_failed")},
                      "after": {k: ia.get(k) for k in
                                ("t1_10_probe_checks", "t1_10_probe_overall",
                                 "t1_10_probe_failed")}}, ensure_ascii=False))

    m20b = _summary(before_dir / "mut20" / "mutations.r2.json")
    m20a = _summary(after_dir / "mut20" / "mutations.r2.json")
    check("MUT-A3: 20-arm machinery all-red on both trees, per-arm red sets identical "
          "(MUT-7->C5, MUT-15->X1..X4 anchors re-read after fix)",
          m20b.get("mutation_count") == m20a.get("mutation_count") == 20
          and m20b.get("all_mutants_red_again") is True
          and m20a.get("all_mutants_red_again") is True
          and m20b.get("all_expected_cases_red") is True
          and m20a.get("all_expected_cases_red") is True
          and [m.get("cases_red") for m in m20b.get("mutants", [])]
          == [m.get("cases_red") for m in m20a.get("mutants", [])],
          json.dumps({"before": {k: m20b.get(k) for k in
                                 ("mutation_count", "all_mutants_red_again",
                                  "all_expected_cases_red")},
                      "after": {k: m20a.get(k) for k in
                                ("mutation_count", "all_mutants_red_again",
                                 "all_expected_cases_red")}}, ensure_ascii=False))

    # --- own mutation + nc -------------------------------------------------
    mut = _summary(after_dir / "mutation" / "mutation_results.json")
    check("MUT-F1/F2/P4 + anchors: own mutation subcommand PASS",
          mut.get("overall") == "PASS",
          json.dumps(mut.get("failed_checks"), ensure_ascii=False))
    nc = _summary(after_dir / "nc" / "nc_results.json")
    check("negative control PASS (PC green; NC-1/NC-2 both NOT green)",
          nc.get("overall") == "PASS",
          json.dumps(nc.get("failed_checks"), ensure_ascii=False))

    # --- probe phase results ----------------------------------------------
    for phase, d in (("before", before_dir), ("after", after_dir)):
        pr = _summary(d / "probes" / "family_results.json")
        check(f"probe {phase}: overall PASS", pr.get("overall") == "PASS",
              json.dumps(pr.get("failed_checks"), ensure_ascii=False)[:400])

    doc = {"card": "T1-F2-FIX", "attempt_id": "a20260923-01",
           "prereq_sut_sha256": sha256_file(baseline_path),
           "fixed_sut_sha256": sha256_file(fixed_path),
           "changed_prereq_lines": changed,
           "external_pin_drift": external_drift,
           "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True),
                   encoding="utf-8")
    print(json.dumps({"invariants": doc["overall"],
                      "checks": len(checks),
                      "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pins")
    p.add_argument("--mode", choices=["write", "check"], required=True)
    p.set_defaults(func=cmd_pins)

    p = sub.add_parser("probe")
    p.add_argument("--sut", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--phase", choices=["before", "after"], required=True)
    p.set_defaults(func=cmd_probe)

    p = sub.add_parser("suites")
    p.add_argument("--tree", required=True)
    p.add_argument("--phase", choices=["before", "after"], required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_suites)

    p = sub.add_parser("inherit")
    p.add_argument("--sut", required=True)
    p.add_argument("--phase", choices=["before", "after"], required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_inherit)

    p = sub.add_parser("reports")
    p.add_argument("--sut", required=True)
    p.add_argument("--phase", choices=["before", "after"], required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_reports)

    p = sub.add_parser("mutation")
    p.add_argument("--sut", required=True)
    p.add_argument("--baseline", required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_mutation)

    p = sub.add_parser("nc")
    p.add_argument("--sut", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_nc)

    p = sub.add_parser("invariants")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_invariants)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
