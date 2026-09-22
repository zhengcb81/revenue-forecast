#!/usr/bin/env python3
"""verify.py — the RED -> GREEN -> mutation harness for REM79-MECHANIZATION.

Runs the naive (RED) and real (GREEN) checkers as separate processes against the
frozen corpus, compares every result to the FROZEN oracle_table.json, runs the
three pre-declared mutations, and writes all raw outputs under evidence/.

Nothing here edits any file outside this attempt; plan files are not touched.
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
EVID = ATTEMPT / "evidence"
PY = sys.executable or "python"

commands_run = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd, cwd=ATTEMPT):
    """Run a command, capture raw stdout/stderr/rc; return dict."""
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True,
        encoding="utf-8", errors="replace",
        env={"PYTHONUTF8": "1", "PATH": "/usr/bin:/bin", **_clean_env()},
    )
    commands_run.append({
        "argv": cmd, "cwd": str(cwd), "rc": proc.returncode,
    })
    return proc


def _clean_env():
    import os
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return env


def save(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def violation_lines(report):
    return {
        e["path"]: sorted(v["line"] for v in e.get("violations", []))
        for e in report["files"] if "error" not in e
    }


def load_oracle():
    return json.loads((ATTEMPT / "oracle_table.json").read_text(encoding="utf-8"))


def expected_by_file(oracle):
    return {
        rel: sorted(meta["expect_flagged_lines"])
        for rel, meta in oracle["files"].items()
    }


def check_hash_freeze(oracle, base: Path):
    """Corpus must still match the FROZEN hashes before any run."""
    freeze = json.loads((EVID / "freeze_record.json").read_text(encoding="utf-8"))
    results = []
    for rel, want in freeze["corpus_sha256"].items():
        got = sha(ATTEMPT / rel)
        results.append({"file": rel, "expected": want, "actual": got,
                        "ok": want == got})
    ok = all(r["ok"] for r in results)
    save(base / "corpus_hash_guard.json",
         json.dumps({"all_match_freeze": ok, "files": results},
                    ensure_ascii=False, indent=2))
    return ok


def main() -> int:
    # optional round tag: `verify.py round2` writes under evidence/round2/...,
    # leaving round-1 raw evidence untouched; no tag = original evidence/ paths.
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    base = (EVID / tag) if tag else EVID
    base.mkdir(parents=True, exist_ok=True)
    oracle = load_oracle()
    expect = expected_by_file(oracle)
    combined = oracle["combined_run"]["files_in_order"]
    summary = {"schema": "rem79-verify-summary/1",
               "verified_at": datetime.now(timezone.utc).isoformat(),
               "tag": tag or "round1"}

    # ---------------------------------------------------- 0. freeze guard ----
    if not check_hash_freeze(oracle, base):
        print("FATAL: corpus drifted from frozen hashes; aborting", file=sys.stderr)
        return 2

    naive = ["harness/naive_checker_marker_only.py"]
    real = ["tools/check_domain_assertions.py"]

    # ---------------------------------------------------------- 1. RED -------
    red_dir = base / "red"
    proc_txt = run([PY, "-B", *naive, *combined])
    save(red_dir / "naive_text_stdout.txt", proc_txt.stdout)
    save(red_dir / "naive_text_stderr.txt", proc_txt.stderr)
    proc_js = run([PY, "-B", *naive, "--json", *combined])
    save(red_dir / "naive_json_stdout.json", proc_js.stdout)
    save(red_dir / "naive_json_stderr.txt", proc_js.stderr)
    naive_report = json.loads(proc_js.stdout)
    naive_lines = violation_lines(naive_report)

    red_mismatches = {
        rel: {"oracle_expected": expect[rel], "naive_reported": naive_lines.get(rel, [])}
        for rel in combined if naive_lines.get(rel, []) != expect[rel]
    }
    naive_false_positives = {
        rel: naive_lines.get(rel, [])
        for rel in oracle["files"]
        if oracle["files"][rel]["role"].startswith("negative")
        and naive_lines.get(rel, [])
    }
    naive_caught_all_positives = all(
        4 in naive_lines.get(rel, [])
        for rel in oracle["files"] if oracle["files"][rel]["role"].startswith("positive")
    )
    red_verdict = {
        "arm": "RED",
        "variant": "naive_marker_only",
        "text_stdout_rc": proc_txt.returncode,
        "json_stdout_rc": proc_js.returncode,
        "mismatch_count": len(red_mismatches),
        "mismatches": red_mismatches,
        "false_positive_files": naive_false_positives,
        "caught_all_oracle_positives": naive_caught_all_positives,
        "verdict": "RED_FAILS_ORACLE_AS_REQUIRED"
        if red_mismatches and naive_false_positives
        else "RED_UNEXPECTEDLY_MATCHED_ORACLE",
        "oracle_requirement": oracle["red_arm_contract"]["red"]["must_fail_oracle"],
    }
    save(red_dir / "red_verdict.json",
         json.dumps(red_verdict, ensure_ascii=False, indent=2))

    # --------------------------------------------------------- 2. GREEN ------
    green_dir = base / "green"
    g_txt = run([PY, "-B", *real, *combined])
    save(green_dir / "check_text_stdout.txt", g_txt.stdout)
    save(green_dir / "check_text_stderr.txt", g_txt.stderr)
    g_js = run([PY, "-B", *real, "--json", *combined])
    save(green_dir / "check_json.json", g_js.stdout)
    save(green_dir / "check_json_stderr.txt", g_js.stderr)
    green_report = json.loads(g_js.stdout)
    green_lines = violation_lines(green_report)

    per_file = {}
    for rel in combined:
        p = run([PY, "-B", *real, "--json", rel])
        save(green_dir / "per_file" / f"{Path(rel).name}.json", p.stdout)
        per_file[rel] = {
            "rc": p.returncode,
            "expect_rc": oracle["files"][rel]["expect_exit_code"],
            "reported": sorted(v["line"] for v in json.loads(p.stdout)["files"][0].get("violations", [])),
            "expect": expect[rel],
        }
        per_file[rel]["rc_ok"] = per_file[rel]["rc"] == per_file[rel]["expect_rc"]
        per_file[rel]["lines_ok"] = per_file[rel]["reported"] == per_file[rel]["expect"]

    green_mismatches = {
        rel: {"oracle_expected": expect[rel], "green_reported": green_lines.get(rel, [])}
        for rel in combined if green_lines.get(rel, []) != expect[rel]
    }
    total_ok = green_report["totals"]["violations"] == oracle["combined_run"]["expect_total_violations"]
    rc_ok = g_js.returncode == oracle["combined_run"]["expect_exit_code"]
    green_verdict = {
        "arm": "GREEN",
        "variant": "check_domain_assertions",
        "json_rc": g_js.returncode,
        "expect_json_rc": oracle["combined_run"]["expect_exit_code"],
        "rc_ok": rc_ok,
        "total_violations": green_report["totals"]["violations"],
        "expect_total_violations": oracle["combined_run"]["expect_total_violations"],
        "total_ok": total_ok,
        "line_mismatches": green_mismatches,
        "per_file": per_file,
        "verdict": "GREEN_MATCHES_ORACLE_EXACTLY"
        if not green_mismatches and all(v["rc_ok"] for v in per_file.values())
        and rc_ok and total_ok
        else "GREEN_MISMATCH",
    }
    save(green_dir / "green_verdict.json",
         json.dumps(green_verdict, ensure_ascii=False, indent=2))

    # ------------------------------------------------------ 3. MUTATIONS -----
    mut_dir = base / "mutations"
    mut_verdicts = {}
    decl = oracle["mutations"]

    # MUT-A
    p = run([PY, "-B", *real, "--json", "mutations/a_strip_domain.md"])
    save(mut_dir / "a_strip_domain.json", p.stdout)
    rep = json.loads(p.stdout)["files"][0].get("violations", [])
    lines_a = sorted(v["line"] for v in rep)
    mut_verdicts["a_strip_domain"] = {
        "declared_expect": decl["a_strip_domain"]["expect_flagged_lines"],
        "reported": lines_a, "rc": p.returncode,
        "verdict": "MUT_A_PASS" if lines_a == decl["a_strip_domain"]["expect_flagged_lines"]
        and p.returncode == decl["a_strip_domain"]["expect_exit_code"] else "MUT_A_FAIL",
    }

    # MUT-B
    p = run([PY, "-B", *real, "--json", "mutations/b_add_domain.md"])
    save(mut_dir / "b_add_domain.json", p.stdout)
    lines_b = sorted(v["line"] for v in json.loads(p.stdout)["files"][0].get("violations", []))
    mut_verdicts["b_add_domain"] = {
        "declared_expect": decl["b_add_domain"]["expect_flagged_lines"],
        "reported": lines_b, "rc": p.returncode,
        "verdict": "MUT_B_PASS" if lines_b == decl["b_add_domain"]["expect_flagged_lines"]
        and p.returncode == decl["b_add_domain"]["expect_exit_code"] else "MUT_B_FAIL",
    }

    # MUT-C
    p = run([PY, "-B", *real, "--json", "mutations/c_offbyone.md"])
    save(mut_dir / "c_offbyone.json", p.stdout)
    lines_c = sorted(v["line"] for v in json.loads(p.stdout)["files"][0].get("violations", []))
    baseline = decl["c_offbyone"]["oracle_baseline_payload_line"]
    declared_actual = decl["c_offbyone"]["expect_reported_payload_line"]
    mismatches_baseline = lines_c != [baseline]
    mut_verdicts["c_offbyone"] = {
        "oracle_baseline": [baseline],
        "declared_reported": [declared_actual],
        "reported": lines_c,
        "report_mismatches_oracle_baseline": mismatches_baseline,
        "verdict": "MUT_C_PASS" if lines_c == [declared_actual] and mismatches_baseline
        else "MUT_C_FAIL",
    }
    save(mut_dir / "mutation_verdicts.json",
         json.dumps(mut_verdicts, ensure_ascii=False, indent=2))

    # -------------------------------------------------------- 4. summary -----
    summary["red"] = red_verdict
    summary["green"] = green_verdict
    summary["mutations"] = mut_verdicts
    summary["commands_run"] = commands_run
    all_ok = (
        red_verdict["verdict"] == "RED_FAILS_ORACLE_AS_REQUIRED"
        and green_verdict["verdict"] == "GREEN_MATCHES_ORACLE_EXACTLY"
        and all(v["verdict"].endswith("_PASS") for v in mut_verdicts.values())
    )
    summary["overall"] = "PROTOCOL_SATISFIED" if all_ok else "PROTOCOL_BREACH"
    save(base / "verify_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    save(base / "commands_run.json", json.dumps(commands_run, ensure_ascii=False, indent=2))

    print(f"RED   : {red_verdict['verdict']} (mismatches={red_verdict['mismatch_count']})")
    print(f"GREEN : {green_verdict['verdict']} (violations={green_report['totals']['violations']})")
    for name, v in mut_verdicts.items():
        print(f"MUT-{name.upper()[:1]}: {v['verdict']} reported={v.get('reported') or v.get('reported')}")
    print(f"OVERALL: {summary['overall']}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
