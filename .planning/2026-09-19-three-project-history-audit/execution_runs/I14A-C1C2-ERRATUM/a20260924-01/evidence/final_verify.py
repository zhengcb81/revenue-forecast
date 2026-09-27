"""Final self-verification for I14A-C1C2-ERRATUM (re-parses every JSON it wrote).

Checks, in order:
  1. handoff.json re-parses and carries the mandated fields;
  2. every entry in handoff.written_files matches the bytes on disk;
  3. the sealed attempt's two appended sections keep their pre-image prefix
     (prefix_bytes_preserved) and match the recorded post-image;
  4. git status of the sealed attempt shows ONLY oracle.md and decision.md;
  5. git diff HEAD --name-only has 0 non-.planning lines;
  6. red / green / mutation raw verdicts match what handoff.json claims;
  7. this attempt's oracle.md still equals its frozen hash.

Writes evidence/final_verification.json.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
EXEC_RUNS = ATTEMPT.parents[1]
SEALED = EXEC_RUNS / "I-14-A" / "a20260919-01"
REPO = ATTEMPT.parents[4]
OUT = ATTEMPT / "evidence" / "final_verification.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_text_auto(p: Path) -> str:
    """Some raw captures were redirected by PowerShell, which writes UTF-16;
    decode by BOM so the check reads the bytes that are actually on disk."""
    raw = p.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw.decode("utf-8-sig")
    return raw.decode("utf-8")


def jload(p: Path) -> dict:
    return json.loads(read_text_auto(p))


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    handoff = jload(ATTEMPT / "handoff.json")          # re-parse #1
    checks["handoff_status_review_pending"] = handoff.get("status") == "review_pending"
    checks["handoff_implementer_signed_false"] = handoff.get("implementer_signed") is False
    checks["handoff_no_acceptance_claim"] = handoff.get("does_not_claim_I14A_acceptance") is True
    checks["handoff_D2_resign_pending"] = handoff.get("D2_resign_pending") is True
    checks["handoff_route_A_selected"] = handoff["C1_route"].get("selected") == "A"
    checks["handoff_has_route_reason_and_counterexample"] = (
        len(handoff["C1_route"].get("reason", [])) >= 3
        and len(handoff["C1_route"].get("counterexample_against_B", [])) >= 3
    )
    checks["handoff_c2_both_claims"] = (
        "claim_1_catalog_db" in handoff["C2_findings"]
        and "claim_2_inline_comments" in handoff["C2_findings"]
        and "reading_correction" in handoff["C2_findings"]
    )

    bad = []
    for entry in handoff["written_files"]:
        p = ATTEMPT / entry["path"]
        if not p.is_file():
            bad.append(f"missing {entry['path']}")
            continue
        if p.stat().st_size != entry["bytes"]:
            bad.append(f"bytes {entry['path']} {p.stat().st_size} != {entry['bytes']}")
        if sha(p) != entry["sha256"]:
            bad.append(f"sha {entry['path']} {sha(p)} != {entry['sha256']}")
    checks["written_files_match"] = not bad
    details["written_files_mismatches"] = bad

    # json re-parse of every json this attempt produced
    reparsed = []
    json_errors = []
    for p in sorted(ATTEMPT.rglob("*.json")):
        if "venv" in p.parts or "fixture_root" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            json.loads(read_text_auto(p))
            reparsed.append(str(p.relative_to(ATTEMPT)))
        except (ValueError, UnicodeDecodeError) as exc:
            json_errors.append(f"{p}: {exc}")
    checks["all_json_reparsed"] = not json_errors
    details["json_files_reparsed"] = len(reparsed)
    details["json_errors"] = json_errors

    # sealed append proofs
    proofs = jload(ATTEMPT / "evidence" / "prefix_proofs.json")
    sealed_results = []
    for entry in handoff["sealed_appends"]:
        p = REPO / entry["file"] if entry["file"].startswith("execution_runs") else SEALED / Path(entry["file"]).name
        p = EXEC_RUNS / "I-14-A" / "a20260919-01" / Path(entry["file"]).name
        raw = p.read_bytes()
        n = entry["pre_image"]["bytes"]
        prefix_ok = hashlib.sha256(raw[:n]).hexdigest() == entry["pre_image"]["sha256"]
        post_ok = len(raw) == entry["post_image"]["bytes"] and sha(p) == entry["post_image"]["sha256"]
        sealed_results.append({"file": p.name, "prefix_bytes_preserved": prefix_ok,
                               "post_image_matches": post_ok})
        checks[f"prefix_preserved_{p.name}"] = prefix_ok and post_ok
    details["sealed_appends"] = sealed_results
    checks["prefix_proofs_all_true"] = proofs.get("all_prefixes_preserved") is True

    # git status of the sealed attempt (read-only)
    st = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--porcelain", "--",
         ".planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    changed = sorted(l.strip() for l in st.stdout.splitlines() if l.strip())
    expected = sorted([
        "M .planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/decision.md",
        "M .planning/2026-09-19-three-project-history-audit/execution_runs/I-14-A/a20260919-01/oracle.md",
    ])
    checks["sealed_only_two_appended_files"] = changed == expected
    details["sealed_git_status"] = changed

    # git diff HEAD, non-.planning count
    df = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "HEAD", "--name-only"],
                        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    lines = [l for l in df.stdout.splitlines() if l.strip()]
    non = [l for l in lines if not l.startswith(".planning/")]
    checks["git_diff_non_planning_zero"] = len(non) == 0
    details["git_diff_total_lines"] = len(lines)
    details["git_diff_non_planning"] = len(non)
    details["git_diff_non_planning_paths"] = non[:20]

    # red arm
    red_runs = []
    for i in range(1, 6):
        v = jload(ATTEMPT / "evidence" / "red" / "e0_repeat" / f"run{i}" / "E0-baseline-F4" / "verdict.json")
        red_runs.append({"run": i, "all_ok": v["all_ok"], "failed": v["failed_checks"]})
    details["red_runs"] = red_runs
    checks["red_arm_reproduced"] = (
        sum(1 for r in red_runs if not r["all_ok"]) >= 1
        and all(r["failed"] == ["fixture_pid_is_in_samples"] for r in red_runs if not r["all_ok"])
    )
    red_suite = read_text_auto(ATTEMPT / "evidence" / "red" / "suite" / "stdout.txt")
    checks["red_suite_rc1"] = "1 failed, 11 passed, 1 skipped" in red_suite
    details["red_suite_tail"] = red_suite.strip().splitlines()[-1]

    # green arm
    green_runs = []
    for i in range(1, 6):
        v = jload(ATTEMPT / "evidence" / "green" / "e0_repeat" / f"run{i}" / "E0-baseline-F4" / "verdict.json")
        green_runs.append(v["all_ok"])
    checks["green_arm_5_of_5"] = all(green_runs)
    details["green_runs_all_ok"] = green_runs
    sweep = jload(ATTEMPT / "evidence" / "green" / "sweep.stdout.json")
    checks["green_sweep_all_ok"] = sweep.get("all_ok") is True
    green_suite = read_text_auto(ATTEMPT / "evidence" / "green" / "suite" / "stdout.txt")
    checks["green_suite_rc0"] = "12 passed, 1 skipped" in green_suite
    details["green_suite_tail"] = green_suite.strip().splitlines()[-1]

    # mutations
    mut = {}
    for arm, expect_red, expect_failed in [
        ("m1", True, ["peak_rss_gt", "peak_rss_source", "rss_sample_count_min_gte",
                      "rss_pids_include_child_pids"]),
        ("m2", True, ["fixture_pid_is_in_samples"]),
        ("m3", True, ["fixture_pid_is_in_samples"]),
        ("m4", False, []),
    ]:
        payload = jload(ATTEMPT / "evidence" / "mutations" / arm / "arm.stdout.json")
        ok = (payload["runner_all_ok"] is not expect_red) and \
             (payload["failed_checks"] == expect_failed)
        mut[arm] = {"all_ok": payload["runner_all_ok"],
                    "failed_checks": payload["failed_checks"],
                    "matches_frozen_expectation": ok}
        checks[f"mutation_{arm}_as_expected"] = ok
    details["mutations"] = mut

    # erratum oracle still frozen
    frozen = [e for e in handoff["written_files"] if e["path"] == "oracle.md"][0]
    checks["oracle_still_frozen"] = sha(ATTEMPT / "oracle.md") == frozen["sha256"]

    # probe byte-identity with the sealed probe
    checks["probe_identical_to_sealed"] = (
        sha(ATTEMPT / "iso" / "slo_probe_patched.py")
        == sha(SEALED / "iso" / "slo_probe_patched.py")
        == "14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e"
    )

    payload = {
        "purpose": "final self-verification of the I14A-C1C2-ERRATUM append-only round",
        "checks": checks,
        "failed_checks": [k for k, v in checks.items() if not v],
        "all_passed": all(checks.values()),
        "details": details,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    parsed = jload(OUT)                                   # re-parse #2
    print(json.dumps({"all_passed": parsed["all_passed"],
                      "failed": parsed["failed_checks"],
                      "git_diff_non_planning": parsed["details"]["git_diff_non_planning"]},
                     ensure_ascii=False, indent=2))
    return 0 if parsed["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
