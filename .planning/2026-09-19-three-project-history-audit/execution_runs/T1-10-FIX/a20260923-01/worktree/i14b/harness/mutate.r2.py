"""I-14-B mutation proof r2: revert ONE judgement at a time in a scratch copy.

This is the r2 revision of harness/mutate.py (r1 preserved at
harness/archive/mutate.r1.py).  It keeps the r1 15 mutations and adds the five
judgements introduced by the P1/P2 fix:

  MUT-15  J16 basis enumeration            -> X1, X2, X3, X4
  MUT-16  P2 quick_check back in the union -> W1, X5, X6, X7
  MUT-17  J15 declared window over quick_check -> X8, X9
  MUT-18  J4b absent interval             -> X10, X11
  MUT-19  J10c same-UTC-day second run    -> X14

Every mutation is a literal, asserted single-occurrence replacement applied to a
scratch copy; the SUT itself is never edited.

Usage:
  <iso-python> -X utf8 -B harness/mutate.r2.py --out evidence/mutations.r2.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SUT = ATTEMPT / "iso" / "natural_window.py"
SCRATCH = HERE / "scratch" / "mutants-r2"
CASES = HERE / "cases.r2.json"
EXPECTATIONS = HERE / "frozen_expectations.r2.json"

MUTATIONS = [
    ("MUT-1-J1-overlap-summed", "J1",
     "    union = _measure_union(intervals)  # J1",
     "    union = sum_seconds  # MUT-1",
     ["W4", "W5"]),
    ("MUT-2-J2-command-total-as-observation", "J2",
     "        if command_total is not None and span is not None and command_total > span:  # J2",
     "        if False:  # MUT-2",
     ["W2"]),
    ("MUT-3-J3-quick-check-inside", "J3",
     "        if quick_check is not None:  # J3",
     "        if False:  # MUT-3",
     ["W3"]),
    ("MUT-4-J4-unmeasured-is-zero", "J4",
     '    if "sampled_at" in fields and len(in_window) < 2:  # J4',
     "    if False:  # MUT-4",
     ["W6"]),
    ("MUT-5-J5-sample-outside-window", "J5",
     "    if outside:  # J5",
     "    if False:  # MUT-5",
     ["W7"]),
    ("MUT-6-J6-future-clock", "J6",
     "        if _parse(entry[\"started_at\"]) > frozen_now:            # J6",
     "        if False:  # MUT-6",
     ["C1"]),
    ("MUT-7-J7-simulated-clock", "J7",
     "    if clock_source not in TRUSTED_CLOCKS:  # J7",
     "    if False:  # MUT-7",
     ["C5"]),
    ("MUT-8-J8-empty-evidence-hash", "J8",
     '        if not entry.get("report_sha256"):                      # J8',
     "        if False:  # MUT-8",
     ["C7"]),
    ("MUT-9-J9-duplicate-run-id", "J9",
     '        if first_index.get(str(entry.get("run_id"))) != index:  # J9',
     "        if False:  # MUT-9",
     ["C6"]),
    ("MUT-10a-J10a-same-instant-chain", "J10a",
     '        if instant_counts.get(_parse(entry["started_at"]), 0) > 1:  # J10a',
     "        if False:  # MUT-10a",
     ["C1"]),
    ("MUT-10b-J10b-same-instant-login", "J10b",
     "    if len(sampled_stamps) != len(set(sampled_stamps)):  # J10b",
     "    if False:  # MUT-10b",
     ["L4"]),
    ("MUT-11-J11-claim-exceeds-facts", "J11",
     '    if claim_status == "complete" and computed_status != "complete":  # J11',
     "    if False:  # MUT-11",
     ["C4"]),
    ("MUT-12-J12-label-anchor-offset", "J12",
     "    if anchor_at is not None and max_error is not None and max_error > tol:  # J12",
     "    if False:  # MUT-12",
     ["L2", "L4"]),
    ("MUT-13-J13-shared-anchor", "J13",
     "    if not shared:  # J13",
     "    if False:  # MUT-13",
     ["L5"]),
    ("MUT-14-J14-posthoc-capture", "J14",
     "    if posthoc or (max_latency is not None and max_latency > cap_tol):  # J14",
     "    if False:  # MUT-14",
     ["L2b", "L3"]),
    ("MUT-15-J16-basis-enumeration", "J16 (P1)",
     "    if basis not in BASIS_REGISTRY:  # J16 / P1",
     "    if False:  # MUT-15",
     ["X1", "X2", "X3", "X4"]),
    ("MUT-16-P2-quick-check-in-union", "P2",
     "        intervals = [(started, obs_finished)]",
     "        intervals = [(started, obs_finished)] + ([(qc_started, qc_finished)] "
     "if qc_started is not None and qc_finished is not None else [])  # MUT-16",
     ["W1", "X5", "X6", "X7"]),
    ("MUT-17-J15-window-covers-quick-check", "J15",
     "    if qc_overlap_seconds > 0:  # J15",
     "    if False:  # MUT-17",
     ["X8", "X9"]),
    ("MUT-18-J4b-absent-observation-interval", "J4b",
     "    if not intervals and span is None:  # J4b",
     "    if False:  # MUT-18",
     ["X10", "X11"]),
    ("MUT-19-J10c-same-utc-day-second-run", "J10c",
     "        if prev_date is not None and day == prev_date:  # J10c",
     "        if False:  # MUT-19",
     ["X14"]),
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ATTEMPT / "evidence" / "mutations.r2.json"))
    args = ap.parse_args()

    source = SUT.read_text(encoding="utf-8")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    results = []

    for mut_id, judgement, old, new, expected_red in MUTATIONS:
        occurrences = source.count(old)
        if occurrences != 1:
            raise SystemExit(f"mutation {mut_id}: expected exactly 1 occurrence, found {occurrences}")
        mutant = SCRATCH / f"{mut_id}.py"
        mutant.write_text(source.replace(old, new), encoding="utf-8")

        out_dir = ATTEMPT / "evidence" / "mutations-r2" / mut_id
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(HERE / "run_cases.py"),
             "--sut", str(mutant), "--cases", str(CASES),
             "--expectations", str(EXPECTATIONS),
             "--out-dir", str(out_dir), "--label", mut_id],
            capture_output=True,
        )
        gate_path = out_dir / "cases_report.json"
        gate = json.loads(gate_path.read_text(encoding="utf-8")) if gate_path.exists() else {}
        failing = sorted({m["case_id"] for m in gate.get("mismatches", [])})
        results.append({
            "mutant_id": mut_id,
            "judgement_reverted": judgement,
            "replaced_line": old,
            "replacement_line": new,
            "mutant_path": str(mutant),
            "mutant_sha256": sha256_file(mutant),
            "runner_raw_returncode": proc.returncode,
            "red_again": proc.returncode != 0,
            "mismatch_count": gate.get("mismatch_count"),
            "accepted_ineligible": gate.get("accepted_ineligible"),
            "cases_red": failing,
            "expected_re_red_cases": expected_red,
            "expected_cases_are_red": all(c in failing for c in expected_red),
        })

    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "revision": "r2",
        "sut_sha256": sha256_file(SUT),
        "cases_sha256": sha256_file(CASES),
        "expectations_sha256": sha256_file(EXPECTATIONS),
        "runner_sha256": sha256_file(HERE / "run_cases.py"),
        "control": "the unmutated r2 SUT passes the same runner (after/cmd-CASES-r2, rc 0, 34/34)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mutants": results,
        "all_mutants_red_again": all(r["red_again"] for r in results),
        "all_expected_cases_red": all(r["expected_cases_are_red"] for r in results),
        "load_bearing_judgement_count": sum(1 for r in results if r["red_again"]),
        "mutation_count": len(results),
    }
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("mutation_count", "load_bearing_judgement_count",
                                          "all_mutants_red_again", "all_expected_cases_red",
                                          "sut_sha256")}, indent=2))
    for record in results:
        print(f'{record["mutant_id"]}: rc={record["runner_raw_returncode"]} '
              f'mismatch={record["mismatch_count"]} red_cases={",".join(record["cases_red"])}')
    return 0 if doc["all_mutants_red_again"] and doc["all_expected_cases_red"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
