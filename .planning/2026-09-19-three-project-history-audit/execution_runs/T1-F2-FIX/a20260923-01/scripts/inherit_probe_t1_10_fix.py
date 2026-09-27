"""T1-10-FIX verification engine (a20260923-01).

Freezes-then-measures the repair of defect (1): the J16 `claim.basis`
enumeration validation was not a total function, so a malformed basis CRASHED
the adjudication machinery (rc=4, no report, whole batch undecided) instead of
being rejected.  Shapes and expectations are frozen in ../oracle.md (written
BEFORE any run); this script only measures against them.

Subcommands
  probe      --sut <path> --out-dir <dir> [--phase before|after]
             family sweep B1..B12 via the real CLI, direct classify() traceback
             capture, blast-radius arms A/B/C, adjacent-discovery probes.
  mutation   --sut <fixed path> --out-dir <dir>
             MUT-G1/G2 revert one guard each in a scratch copy (crash must
             return); MUT-G3 grep-count the mutate.r2.py J16 anchor.
  nc         --sut <fixed path> --worktree <i14b dir> --out-dir <dir>
             T1-8-style fabricated-green negative controls NC-1/NC-2 + PC.
  invariants --sut <fixed> --baseline <pristine> --worktree <i14b dir>
             --before-dir <evidence/before> --after-dir <evidence/after> --out <json>
             I-1 defect(2) untouched, I-2 byte-identical valid-input reports,
             stable-family row equality, refusal-code set equality, pins.

No git.  Writes only inside this attempt.  No timestamps in outputs
(idempotent evidence: same inputs -> same bytes).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent                      # .../T1-10-FIX/a20260923-01
EXEC = ATTEMPT.parent.parent                        # .../execution_runs
PLAN = EXEC.parent                                  # .../2026-09-19-three-project-history-audit

assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN
assert (ATTEMPT / "oracle.md").is_file(), "FATAL: oracle.md missing (freeze first)"

FROZEN_NOW = "2026-09-20T02:56:38Z"
PY = sys.executable

# GOOD_FIELDS / window_case / calendar_case verbatim from
# T1-10/a20260920-01/scripts/verify_t1_10.py L99-129 (the block's own probes).
GOOD_FIELDS = {
    "started_at": "2026-09-20T00:00:00Z",
    "observation_finished_at": "2026-09-20T00:29:00Z",
    "sampled_at": ["2026-09-20T00:%02d:00Z" % i for i in range(0, 30, 2)],
    "quick_check_started_at": "2026-09-20T00:29:00Z",
    "quick_check_finished_at": "2026-09-20T00:37:00Z",
    "command_finished_at": "2026-09-20T00:37:00Z",
}

# Oracle sec 1: the frozen malformed-basis family.  id -> (claim, frozen class)
FAMILY: dict[str, object] = {
    "B1":  {"basis": ["union_of_windows"], "natural_observation_seconds": 1740.0},
    "B2":  {"basis": {"name": "union_of_windows"}, "natural_observation_seconds": 1740.0},
    "B3":  ["union_of_windows"],
    "B4":  {"natural_observation_seconds": 1740.0},
    "B5":  {"basis": "union_of_windows", "natural_observation_seconds": 1740.0,
            "unrelated": "x"},
    "B6":  {"basis": "union_of_windows", "natural_observation_seconds": 1740.0},
    "B7":  {"basis": "wall_clock", "natural_observation_seconds": 1740.0},
    "B8":  {"basis": None, "natural_observation_seconds": 1740.0},
    "B9":  {"basis": 5, "natural_observation_seconds": 1740.0},
    "B10": {"basis": "", "natural_observation_seconds": 1740.0},
    "B11": {"basis": [["x"]], "natural_observation_seconds": 1740.0},
    "B12a": "s",
    "B12b": 5,
    "B12c": True,
}
CRASH_SHAPES = ["B1", "B2", "B3", "B11", "B12a", "B12b", "B12c"]
ACCEPT_STABLE = ["B5", "B6"]
REJECT_STABLE = ["B4", "B7", "B8", "B9", "B10"]
STABLE = ACCEPT_STABLE + REJECT_STABLE

REGISTERED = ["command_total", "observation_plus_quick_check", "sample_span",
              "sum_of_windows", "union_of_windows"]

BASELINE_SUT_SHA = "7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796"

# Exact fix text (frozen here so MUT-G1/G2 revert precisely these blocks).
BASELINE_REGISTRY_BLOCK = '''BASIS_REGISTRY = {
    "sample_span",
    "command_total",
    "observation_plus_quick_check",
    "sum_of_windows",
    "union_of_windows",
}'''
FIXED_REGISTRY_BLOCK = '''BASIS_REGISTRY = (
    "sample_span",
    "command_total",
    "observation_plus_quick_check",
    "sum_of_windows",
    "union_of_windows",
)'''
BASELINE_CARRIER_LINES = '''    basis = (fields.get("_claim") or {}).get("basis")
    wanted = (fields.get("_claim") or {}).get("natural_observation_seconds")'''
FIXED_CARRIER_LINES = '''    claim = fields.get("_claim")
    if not isinstance(claim, dict):
        claim = {}
    basis = claim.get("basis")
    wanted = claim.get("natural_observation_seconds")'''
J16_ANCHOR = "    if basis not in BASIS_REGISTRY:  # J16 / P1"

PIN_HASHES = {
    "oracle.md": "bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3",
    "review.md": "ab93734d430bd2814d55ae8be5f22297c4a3888c8ac83f0c43192fa0576142ed",
    "changes.r2.diff": "660bc943187db1c083ef8f04b3c642f3917a3040a5eae376c4fcbbb7ef2c2104",
    "harness/run_cases.py": "f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23",
    "harness/mutate.r2.py": "4f741cb72af5cdb62095b422d4d87d6440082091a53969704201616bed383def",
    "harness/tests/test_i14b_natural_window.py": "413ff05c52e07acacf0491a0ec3f2cd1c426011995b45d7ad3edaab65a38ad4e",
    "harness/tests/test_i14b_natural_window_r2.py": "ace076871c811441bc454692323dbba71243086ec7287880eed9b51a8114d1e9",
    "harness/cases.json": "5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64",
    "harness/cases.r2.json": "23d89fb27bbdb599646290ba5dbf096a0d1513d63c7a6d19f3f16fe9f88279de",
    "harness/frozen_expectations.json": "3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b",
    "harness/frozen_expectations.r2.json": "a24d8ab3444dd1c75eaa3533f424a048bdced4f0f66408cb04622ead760667ba",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _window_case(cid: str, claim: object) -> dict:
    return {"case_id": cid, "class": "window_accounting",
            "requirement_id": "W-1", "claim": claim, "fields": dict(GOOD_FIELDS)}


def _calendar_case(cid: str) -> dict:
    return {"case_id": cid, "class": "calendar", "requirement_id": "C-1",
            "claim": {"status": "pending"},
            "fields": {"clock_source": "system_utc",
                       "ledger": {"daily": [], "weekly": [], "monthly": [], "alerts": []}}}


def invoke_cli(sut: Path, cases: list, raw_dir: Path, tag: str) -> dict:
    """Run the SUT CLI on a batch; capture rc/stdout/stderr/report as raws."""
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
        v = report["verdicts"][0] if len(report["verdicts"]) == 1 else None
        row.update({
            "case_count": report["case_count"],
            "cases_decided": len(report["verdicts"]),
            "verdict": v["verdict"] if v else "<batch>",
            "refusals": v["refusals"] if v else None,
            "basis_registered": (v or {}).get("computed", {}).get("basis_registered"),
            "verdicts": report["verdicts"],
        })
    else:
        row.update({"case_count": None, "cases_decided": 0, "verdict": None,
                    "refusals": None, "basis_registered": None, "verdicts": None})
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
                      "refusals": got["refusals"],
                      "basis_registered": got["computed"].get("basis_registered")}))
except Exception as exc:
    print(json.dumps({"raised": True, "type": type(exc).__name__, "msg": str(exc),
                      "traceback": traceback.format_exc()}))
'''


def invoke_direct(sut: Path, claim: object, raw_dir: Path, tag: str) -> dict:
    case = _window_case("DIRECT-" + tag, claim)
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


def cmd_probe(args) -> int:
    sut = Path(args.sut).resolve()
    out = Path(args.out_dir).resolve()
    raw = out / "raw"
    checks: list[dict] = []

    def check(name: str, holds: bool, detail: str = "") -> None:
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    # pairing guard: before-phase probes the pristine baseline, after-phase the
    # fixed SUT -- a mis-paired run must fail loudly, never silently pass.
    sut_sha = sha256_file(sut)
    if args.phase == "before":
        assert sut_sha == BASELINE_SUT_SHA, (
            "before-phase must probe the pristine baseline SUT, got %s" % sut_sha)
    else:
        assert sut_sha != BASELINE_SUT_SHA, (
            "after-phase must probe the FIXED SUT, got the baseline sha %s" % sut_sha)

    family_rows = {}
    for cid, claim in FAMILY.items():
        row = invoke_cli(sut, [_window_case(cid, claim)], raw, cid)
        row["direct"] = invoke_direct(sut, claim, raw, cid)
        family_rows[cid] = row

    if args.phase == "before":
        for cid in CRASH_SHAPES:
            r = family_rows[cid]
            check(f"RED {cid}: rc=4 no report", r["rc"] == 4 and not r["report_written"],
                  f"rc={r['rc']} report={r['report_written']} {r['stdout_head'][:120]}")
            check(f"RED {cid}: batch fully undecided (adjudication denied)",
                  r["cases_decided"] == 0, f"decided={r['cases_decided']}")
            check(f"RED {cid}: direct classify raises unhandled",
                  r["direct"].get("raised") is True,
                  f"{r['direct'].get('type')}: {r['direct'].get('msg')}")
    else:  # after
        for cid in CRASH_SHAPES:
            r = family_rows[cid]
            check(f"GREEN {cid}: rc=0 report written, batch decided",
                  r["rc"] == 0 and r["report_written"] and r["cases_decided"] == 1,
                  f"rc={r['rc']} report={r['report_written']}")
            check(f"GREEN {cid}: reject + R-BASIS-UNKNOWN + basis_registered=false",
                  r["verdict"] == "reject_claim"
                  and r["refusals"] == ["R-BASIS-UNKNOWN"]
                  and r["basis_registered"] is False,
                  f"verdict={r['verdict']} refusals={r['refusals']} "
                  f"reg={r['basis_registered']}")
            check(f"GREEN {cid}: no internal_error, empty stderr",
                  "internal_error" not in r["stdout_head"] and not r["stderr_nonempty"],
                  r["stdout_head"][:120])
            check(f"GREEN {cid}: direct classify no longer raises",
                  r["direct"].get("raised") is False,
                  f"{r['direct'].get('type')}: {r['direct'].get('msg')}")
    for cid in ACCEPT_STABLE:
        r = family_rows[cid]
        check(f"{args.phase} {cid}: accept (stable)",
              r["rc"] == 0 and r["verdict"] == "accept_claim" and r["refusals"] == [],
              f"rc={r['rc']} verdict={r['verdict']}")
    for cid in REJECT_STABLE:
        r = family_rows[cid]
        check(f"{args.phase} {cid}: reject + R-BASIS-UNKNOWN (stable)",
              r["rc"] == 0 and r["verdict"] == "reject_claim"
              and r["refusals"] == ["R-BASIS-UNKNOWN"],
              f"rc={r['rc']} verdict={r['verdict']} refusals={r['refusals']}")
    check(f"{args.phase}: every family member stays inside frozen rc domain {{0,4}}",
          all(family_rows[c]["rc"] in (0, 4) for c in FAMILY),
          str({c: family_rows[c]["rc"] for c in FAMILY}))

    # ---- blast-radius arms (T1-10 C_blast_radius shapes) -----------------
    n_good = 12
    good = [_window_case("GOOD-%02d" % i, FAMILY["B6"]) for i in range(n_good)]

    arm_a_cases = list(good)
    arm_a_cases.insert(5, _window_case("BAD-LIST", FAMILY["B1"]))
    arm_b_cases = list(good)
    arm_b_cases.insert(5, _window_case("BAD-STR", FAMILY["B7"]))
    arm_c_cases = [_calendar_case("CAL-OK")] + [_window_case("GOOD-%02d" % i,
                                                             FAMILY["B6"]) for i in range(6)]
    arm_c_cases.insert(3, _window_case("BAD-DICT", FAMILY["B2"]))

    arms = {
        "arm_A_1list_among_12good": invoke_cli(sut, arm_a_cases, raw, "armA"),
        "arm_B_1unregistered_str_among_12good": invoke_cli(sut, arm_b_cases, raw, "armB"),
        "arm_C_dict_among_mixed_classes": invoke_cli(sut, arm_c_cases, raw, "armC"),
    }
    a, b, c = (arms["arm_A_1list_among_12good"],
               arms["arm_B_1unregistered_str_among_12good"],
               arms["arm_C_dict_among_mixed_classes"])
    if args.phase == "before":
        check("RED armA: single list basis destroys all 13 verdicts",
              a["rc"] == 4 and a["cases_decided"] == 0,
              f"rc={a['rc']} decided={a['cases_decided']}")
        check("RED armB contrast: unregistered STR refuses only itself",
              b["rc"] == 0 and b["cases_decided"] == 13,
              f"rc={b['rc']} decided={b['cases_decided']}")
        check("RED armC: blast crosses class (calendar victim undecided)",
              c["rc"] == 4 and c["cases_decided"] == 0,
              f"rc={c['rc']} decided={c['cases_decided']}")
    else:
        def rejected_ids(row):
            return sorted(v["case_id"] for v in (row.get("verdicts") or [])
                          if v["verdict"] == "reject_claim")
        check("GREEN armA: batch fully decided, only the malformed case rejected",
              a["rc"] == 0 and a["cases_decided"] == 13
              and rejected_ids(a) == ["BAD-LIST"],
              f"rc={a['rc']} decided={a['cases_decided']} rejected={rejected_ids(a)}")
        check("GREEN armB: str contrast unchanged (refuses only itself)",
              b["rc"] == 0 and b["cases_decided"] == 13 and rejected_ids(b) == ["BAD-STR"],
              f"rc={b['rc']} rejected={rejected_ids(b)}")
        check("GREEN armC: cross-class blast gone; calendar victim decided",
              c["rc"] == 0 and c["cases_decided"] == 8
              and rejected_ids(c) == ["BAD-DICT"],
              f"rc={c['rc']} decided={c['cases_decided']} rejected={rejected_ids(c)}")

    # ---- adjacent discovery probes (out of scope: registered, not fixed) --
    adjacent = {}
    adjacent["clock_source_container_J7"] = invoke_cli(sut, [{
        "case_id": "ADJ-CLOCK", "class": "calendar", "requirement_id": "C-1",
        "claim": {"status": "pending"},
        "fields": {"clock_source": ["system_utc"],
                   "ledger": {"daily": [], "weekly": [], "monthly": [], "alerts": []}}},
    ], raw, "adj_clock")
    adjacent["calendar_claim_carrier"] = invoke_cli(sut, [{
        "case_id": "ADJ-CALCLAIM", "class": "calendar", "requirement_id": "C-1",
        "claim": ["pending"],
        "fields": {"clock_source": "system_utc",
                   "ledger": {"daily": [], "weekly": [], "monthly": [], "alerts": []}}},
    ], raw, "adj_calclaim")
    bad_time = dict(GOOD_FIELDS)
    bad_time["started_at"] = "not-a-timestamp"
    adjacent["malformed_timestamp_schema"] = invoke_cli(sut, [{
        "case_id": "ADJ-TS", "class": "window_accounting", "requirement_id": "W-1",
        "claim": FAMILY["B6"], "fields": bad_time}], raw, "adj_ts")

    doc = {"card": "T1-10-FIX", "attempt_id": "a20260923-01", "phase": args.phase,
           "sut_path": str(sut), "sut_sha256": sha256_file(sut),
           "family": family_rows, "blast_radius": arms,
           "adjacent_discovery": {k: {"rc": v["rc"],
                                      "report_written": v["report_written"],
                                      "stdout_head": v["stdout_head"]}
                                  for k, v in adjacent.items()},
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


def _probe_crash(sut: Path, cid: str, out: Path, tag: str) -> dict:
    row = invoke_cli(sut, [_window_case(cid, FAMILY[cid])], out / "raw", tag)
    return {"shape": cid, "rc": row["rc"], "report_written": row["report_written"],
            "stdout_head": row["stdout_head"]}


def cmd_mutation(args) -> int:
    fixed = Path(args.sut).resolve()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    scratch = out / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    source = fixed.read_text(encoding="utf-8")
    checks = []

    def check(name, holds, detail=""):
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    # MUT-G3: the mutator's J16 anchor must still be exactly-once.
    baseline = Path(args.baseline).resolve().read_text(encoding="utf-8")
    anchor_fixed = source.count(J16_ANCHOR)
    anchor_baseline = baseline.count(J16_ANCHOR)
    check("MUT-G3: mutate.r2.py J16 anchor exactly-once in fixed SUT",
          anchor_fixed == 1, f"count={anchor_fixed}")
    check("MUT-G3: anchor also exactly-once in baseline (comparison)",
          anchor_baseline == 1, f"count={anchor_baseline}")
    reg_def_ok = source.count(FIXED_REGISTRY_BLOCK) == 1
    car_def_ok = source.count(FIXED_CARRIER_LINES) == 1
    check("fixed registry block present exactly once", reg_def_ok, "")
    check("fixed carrier guard present exactly once", car_def_ok, "")

    arms = []
    if reg_def_ok:
        mutant = source.replace(FIXED_REGISTRY_BLOCK, BASELINE_REGISTRY_BLOCK)
        mpath = scratch / "MUT-G1_registry_tuple_back_to_set.py"
        mpath.write_text(mutant, encoding="utf-8")
        rows = [_probe_crash(mpath, cid, out, f"MUT-G1_{cid}") for cid in ("B1", "B2", "B11")]
        crashed = all(r["rc"] == 4 and not r["report_written"] for r in rows)
        check("MUT-G1: guard reverted -> crash RETURNS (non-vacuous)", crashed,
              json.dumps(rows, ensure_ascii=False))
        arms.append({"arm": "MUT-G1", "reverts": "BASIS_REGISTRY tuple -> set",
                     "mutant_sha256": sha256_file(mpath), "probes": rows,
                     "crash_returned": crashed})
    if car_def_ok:
        mutant = source.replace(FIXED_CARRIER_LINES, BASELINE_CARRIER_LINES)
        mpath = scratch / "MUT-G2_carrier_guard_removed.py"
        mpath.write_text(mutant, encoding="utf-8")
        rows = [_probe_crash(mpath, cid, out, f"MUT-G2_{cid}") for cid in ("B3", "B12a")]
        crashed = all(r["rc"] == 4 and not r["report_written"] for r in rows)
        check("MUT-G2: carrier guard removed -> crash RETURNS (non-vacuous)", crashed,
              json.dumps(rows, ensure_ascii=False))
        arms.append({"arm": "MUT-G2", "reverts": "claim carrier guard -> original line",
                     "mutant_sha256": sha256_file(mpath), "probes": rows,
                     "crash_returned": crashed})

    doc = {"card": "T1-10-FIX", "attempt_id": "a20260923-01",
           "fixed_sut_sha256": sha256_file(fixed),
           "baseline_sut_sha256": sha256_file(Path(args.baseline).resolve()),
           "arms": arms, "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    (out / "mutation_results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"mutation": doc["overall"], "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


def _run_runner(sut: Path, cases: Path, expectations: Path, out_dir: Path,
                label: str, raw: Path) -> dict:
    raw.mkdir(parents=True, exist_ok=True)
    runner = Path(__file__).resolve().parent.parent / "worktree" / "i14b" / "harness" / "run_cases.py"
    assert runner.is_file(), "FATAL: runner not found: %s" % runner
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
    return {"runner_rc": proc.returncode, "runner_stdout": proc.stdout,
            "gate_ok": gate.get("ok"), "mismatch_count": gate.get("mismatch_count"),
            "mismatch_case_ids": sorted({m.get("case_id") for m in gate.get("mismatches", [])}),
            "accepted_ineligible_count": gate.get("accepted_ineligible_count"),
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
    window_ids = [c["case_id"] for c in cases_doc["cases"]
                  if c.get("class") == "window_accounting"]
    accepted_window = [cid for cid in window_ids
                       if exp_doc["expected"][cid]["verdict"] == "accept_claim"]
    check("fixture: 18 window cases on this surface", len(window_ids) == 18,
          f"count={len(window_ids)}")
    check("poison budget >= T1-8's 11 declarations", len(window_ids) >= 11,
          f"window claims={len(window_ids)}, accepted-declarations={len(accepted_window)}")

    # ---- PC first: unpoisoned gate must be GREEN (positive control) ------
    pc = _run_runner(sut, harness / "cases.r2.json", harness / "frozen_expectations.r2.json",
                     out / "pc_runner", "PC-unpoisoned", raw)
    check("PC: unpoisoned gate green (rc=0 ok=true mismatch=0)",
          pc["runner_rc"] == 0 and pc["gate_ok"] is True
          and pc["mismatch_count"] == 0,
          f"rc={pc['runner_rc']} ok={pc['gate_ok']} mismatch={pc['mismatch_count']}")

    # ---- NC-1: poison the CLAIM inputs (enumeration claim declarations) --
    nc1 = json.loads(json.dumps(cases_doc))
    for c in nc1["cases"]:
        if c.get("class") == "window_accounting":
            if not isinstance(c.get("claim"), dict):
                c["claim"] = {}
            c["claim"]["basis"] = ["union_of_windows"]      # malformed (defect-1 shape)
    nc1_path = out / "nc1_cases_poisoned.json"
    nc1_path.write_text(json.dumps(nc1, ensure_ascii=False, indent=2), encoding="utf-8")
    sut_run = invoke_cli(sut, nc1["cases"], raw, "nc1_sut_batch")
    check("NC-1 SUT: machinery survives mass poisoning (rc=0, 34/34 decided)",
          sut_run["rc"] == 0 and sut_run["cases_decided"] == 34,
          f"rc={sut_run['rc']} decided={sut_run['cases_decided']}")
    nc1_gate = _run_runner(sut, nc1_path, harness / "frozen_expectations.r2.json",
                           out / "nc1_runner", "NC-1-claim-poison", raw)
    check("NC-1: gate does NOT go green on poisoned claims (rc=1 ok=false)",
          nc1_gate["runner_rc"] == 1 and nc1_gate["gate_ok"] is False,
          f"rc={nc1_gate['runner_rc']} ok={nc1_gate['gate_ok']}")
    check("NC-1: every declared-accept window claim flips to mismatch",
          all(cid in nc1_gate["mismatch_case_ids"] for cid in accepted_window),
          f"accepted={accepted_window} mismatched={nc1_gate['mismatch_case_ids']}")

    # ---- NC-2: poison the ASSERTION declarations (expectations) ----------
    nc2 = json.loads(json.dumps(exp_doc))
    for cid in window_ids:
        old = nc2["expected"][cid]["verdict"]
        new = "reject_claim" if old == "accept_claim" else "accept_claim"
        nc2["expected"][cid]["verdict"] = new
        nc2["expected"][cid]["refusals"] = (
            [] if new == "accept_claim" else ["R-BASIS-UNKNOWN"])
    nc2_path = out / "nc2_expectations_poisoned.json"
    nc2_path.write_text(json.dumps(nc2, ensure_ascii=False, indent=2), encoding="utf-8")
    nc2_gate = _run_runner(sut, harness / "cases.r2.json", nc2_path,
                           out / "nc2_runner", "NC-2-declaration-poison", raw)
    check("NC-2: gate does NOT go green on poisoned declarations (rc=1 ok=false)",
          nc2_gate["runner_rc"] == 1 and nc2_gate["gate_ok"] is False,
          f"rc={nc2_gate['runner_rc']} ok={nc2_gate['gate_ok']}")
    check("NC-2: all 18 window declarations flagged as mismatch",
          all(cid in nc2_gate["mismatch_case_ids"] for cid in window_ids),
          f"mismatched={nc2_gate['mismatch_case_ids']}")
    check("NC-2: not a T1-8-style fabricated green (never rc=0 with poison)",
          nc2_gate["runner_rc"] != 0, f"rc={nc2_gate['runner_rc']}")

    doc = {"card": "T1-10-FIX", "attempt_id": "a20260923-01",
           "sut_sha256": sha256_file(sut),
           "t1_8_reference": "T1-8/a20260920-03 poisoned 11 declarations -> rc=0 / 11-11 PASS_rejected = fabricated green; this surface must behave oppositely",
           "poisoned_claim_declarations": len(window_ids),
           "poisoned_assertion_declarations": len(window_ids),
           "pc": pc, "nc1": nc1_gate, "nc2": nc2_gate,
           "nc1_sut_rc": sut_run["rc"], "nc1_sut_decided": sut_run["cases_decided"],
           "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    (out / "nc_results.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"negative_control": doc["overall"],
                      "failed": doc["failed_checks"]}, ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


def _changed_old_lines(baseline: str, fixed: str) -> list[int]:
    old_lines = baseline.splitlines(keepends=True)
    new_lines = fixed.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    changed: list[int] = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            changed.extend(range(i1 + 1, i2 + 1))     # 1-based old line numbers
    return changed


def cmd_invariants(args) -> int:
    sut = Path(args.sut).resolve()
    baseline_path = Path(args.baseline).resolve()
    wt = Path(args.worktree).resolve()
    before_dir = Path(args.before_dir).resolve()
    after_dir = Path(args.after_dir).resolve()
    checks = []

    def check(name, holds, detail=""):
        checks.append({"name": name, "holds": bool(holds), "detail": detail})

    baseline = baseline_path.read_text(encoding="utf-8")
    fixed = sut.read_text(encoding="utf-8")

    # I-1: defect (2) region untouched + pinned carriers untouched
    changed = _changed_old_lines(baseline, fixed)
    overlap = sorted(set(changed) & set(range(174, 198)))
    check("I-1: no changed baseline line inside :174-197 (defect-2 quick_check/J15/J6 zone)",
          overlap == [], f"overlap={overlap}")
    check("I-1: changed baseline lines are only the two J16 entry blocks",
          set(changed).issubset(set(range(57, 67)) | set(range(199, 201))),
          f"changed={changed}")
    for rel, want in PIN_HASHES.items():
        p = wt / rel
        got = sha256_file(p) if p.is_file() else "<absent>"
        check(f"I-1 pin untouched: {rel}", got == want, f"got={got}")
    exp = json.loads((wt / "harness" / "frozen_expectations.r2.json").read_text(encoding="utf-8"))
    old_val = exp.get("expected_superseded", {}).get("W1", {}).get(
        "computed.union_seconds", {}).get("old")
    check("I-1: expected_superseded W1 old=2220 still present (defect-2 provenance)",
          old_val == 2220, f"old={old_val}")
    new_val = exp.get("expected", {}).get("W1", {}).get("computed", {}).get("union_seconds")
    check("I-1: expected W1 union_seconds still 1740", new_val == 1740, f"new={new_val}")

    # refusal vocabulary: no new R-* codes introduced
    code_re = re.compile(r'"(R-[A-Z0-9-]+)"')
    codes_before = sorted(set(code_re.findall(baseline)))
    codes_after = sorted(set(code_re.findall(fixed)))
    check("I-4: refusal-code vocabulary identical (no new R-*)",
          codes_before == codes_after, f"before={codes_before} after={codes_after}")

    # I-2: byte-identical valid-input reports
    for gate in ("cmd-CASES-r1", "cmd-CASES-r2"):
        b = before_dir / gate / "sut_report.json"
        a = after_dir / gate / "sut_report.json"
        bb = sha256_file(b) if b.is_file() else "<absent>"
        aa = sha256_file(a) if a.is_file() else "<absent>"
        check(f"I-2: {gate} SUT report byte-identical before==after", bb == aa,
              f"before={bb} after={aa}")
    for gate in ("cmd-CASES-r1", "cmd-CASES-r2"):
        bg = before_dir / gate / "cases_report.json"
        ag = after_dir / gate / "cases_report.json"
        bok = json.loads(bg.read_text(encoding="utf-8")) if bg.is_file() else {}
        aok = json.loads(ag.read_text(encoding="utf-8")) if ag.is_file() else {}
        fields = ("ok", "mismatch_count", "accepted_ineligible_count", "case_count",
                  "sut_raw_returncode", "mismatches")
        same = all(bok.get(k) == aok.get(k) for k in fields)
        if gate == "cmd-CASES-r2":
            # the frozen r2 gate must be green in both phases (oracle sec 6)
            holds = same and bok.get("ok") is True and bok.get("mismatch_count") == 0
        else:
            # the r1 gate on a r2-family SUT carries the DOCUMENTED expected_
            # superseded delta (W1 union 2220->1740, defect-2 provenance); its
            # only invariant here is before==after identity, not greenness.
            holds = same
        check(f"I-2: {gate} gate fields before==after" +
              (" and green" if gate == "cmd-CASES-r2" else " (r1 superseded-delta allowed)"),
              holds, json.dumps({k: [bok.get(k), aok.get(k)] for k in fields[:5]},
                                ensure_ascii=False))

    # stable family rows identical before==after
    bf = json.loads((before_dir / "probes" / "family_results.json").read_text(encoding="utf-8"))
    af = json.loads((after_dir / "probes" / "family_results.json").read_text(encoding="utf-8"))
    for cid in STABLE:
        brow = {k: bf["family"][cid].get(k) for k in
                ("rc", "verdict", "refusals", "basis_registered", "verdicts")}
        arow = {k: af["family"][cid].get(k) for k in
                ("rc", "verdict", "refusals", "basis_registered", "verdicts")}
        check(f"I-2: stable family row {cid} byte-equal before==after", brow == arow,
              json.dumps({"before": brow, "after": arow}, ensure_ascii=False))

    # family suites: before==after and green in both phases
    def _read_sum(path: Path) -> dict:
        # suite summaries are written by PowerShell Out-File -> may carry a BOM
        return json.loads(path.read_text(encoding="utf-8-sig"))

    for suite in ("suite_r1", "suite_r2"):
        b = before_dir / f"{suite}.json"
        a = after_dir / f"{suite}.json"
        if not (b.is_file() and a.is_file()):
            check(f"suites present: {suite}", False, "missing summary json")
            continue
        bj = _read_sum(b)
        aj = _read_sum(a)
        check(f"family suite before==after green: {suite}",
              bj.get("passed") == aj.get("passed") and bj.get("failed") == aj.get("failed")
              and bj.get("failed") == 0,
              json.dumps({"before": bj, "after": aj}, ensure_ascii=False))

    # the NEW malformed-basis family suite: RED before the fix, GREEN after
    bb = before_dir / "suite_basis_total.json"
    ab = after_dir / "suite_basis_total.json"
    btxt = before_dir / "suite_basis_total.txt"
    atxt = after_dir / "suite_basis_total.txt"
    if bb.is_file() and ab.is_file():
        bj = _read_sum(bb)
        aj = _read_sum(ab)
        failed_ids_before = []
        if btxt.is_file():
            raw = btxt.read_bytes()
            text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") \
                else raw.decode("utf-8-sig", errors="replace")
            failed_ids_before = [ln.strip() for ln in text.splitlines()
                                 if ln.startswith("FAILED ")]
        crash_id_hits = {c: any(f"[{c}]" in f for f in failed_ids_before)
                         for c in ("B1", "B2", "B3")}
        check("RED->GREEN: new suite failed pre-fix on >=3 malformed shapes "
              "(B1/B2/B3 ids present in FAILED list)",
              bj.get("failed", 0) >= 3 and all(crash_id_hits.values()),
              json.dumps({"failed": bj.get("failed"), "hits": crash_id_hits,
                          "failed_ids_head": failed_ids_before[:6]}, ensure_ascii=False))
        check("RED->GREEN: new suite fully green post-fix (23 tests)",
              aj.get("failed") == 0 and aj.get("passed") == 23,
              json.dumps({"after": aj}, ensure_ascii=False))
        after_txt = ""
        if atxt.is_file():
            raw = atxt.read_bytes()
            after_txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") \
                else raw.decode("utf-8-sig", errors="replace")
        check("RED->GREEN: post-fix suite stdout has no FAILED lines",
              "FAILED" not in after_txt, "")
    else:
        check("RED->GREEN: new basis-total suite summaries present", False,
              "missing suite_basis_total.json")

    # J16 surface: the 20-arm mutation proof stays all-red in both phases
    bmu = json.loads((before_dir / "mutations.json").read_text(encoding="utf-8")) \
        if (before_dir / "mutations.json").is_file() else {}
    amu = json.loads((after_dir / "mutations.json").read_text(encoding="utf-8")) \
        if (after_dir / "mutations.json").is_file() else {}
    check("J16 surface: 20-arm mutation proof before==after all-red",
          bmu.get("mutation_count") == amu.get("mutation_count") == 20
          and bmu.get("all_mutants_red_again") is True
          and amu.get("all_mutants_red_again") is True
          and bmu.get("all_expected_cases_red") is True
          and amu.get("all_expected_cases_red") is True
          and [m.get("cases_red") for m in bmu.get("mutants", [])]
          == [m.get("cases_red") for m in amu.get("mutants", [])],
          json.dumps({"before": {k: bmu.get(k) for k in
                                 ("mutation_count", "all_mutants_red_again",
                                  "all_expected_cases_red")},
                      "after": {k: amu.get(k) for k in
                                ("mutation_count", "all_mutants_red_again",
                                 "all_expected_cases_red")}}))

    doc = {"card": "T1-10-FIX", "attempt_id": "a20260923-01",
           "baseline_sut_sha256": sha256_file(baseline_path),
           "fixed_sut_sha256": sha256_file(sut),
           "changed_baseline_lines": changed,
           "checks": checks,
           "failed_checks": [c["name"] for c in checks if not c["holds"]],
           "overall": "PASS" if all(c["holds"] for c in checks) else "FAIL"}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2,
                                         sort_keys=True), encoding="utf-8")
    print(json.dumps({"invariants": doc["overall"], "failed": doc["failed_checks"]},
                     ensure_ascii=False, indent=2))
    return 0 if doc["overall"] == "PASS" else 3


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe")
    p.add_argument("--sut", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--phase", choices=["before", "after"], required=True)
    p.set_defaults(func=cmd_probe)

    m = sub.add_parser("mutation")
    m.add_argument("--sut", required=True)
    m.add_argument("--baseline", required=True)
    m.add_argument("--out-dir", required=True)
    m.set_defaults(func=cmd_mutation)

    n = sub.add_parser("nc")
    n.add_argument("--sut", required=True)
    n.add_argument("--worktree", required=True)
    n.add_argument("--out-dir", required=True)
    n.set_defaults(func=cmd_nc)

    i = sub.add_parser("invariants")
    i.add_argument("--sut", required=True)
    i.add_argument("--baseline", required=True)
    i.add_argument("--worktree", required=True)
    i.add_argument("--before-dir", required=True)
    i.add_argument("--after-dir", required=True)
    i.add_argument("--out", required=True)
    i.set_defaults(func=cmd_invariants)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
