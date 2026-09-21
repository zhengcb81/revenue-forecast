"""Round 67 verification: the interruption forensics, the carrier gap, and the append proofs.

Design rules taken from this project's own accumulated discipline:

  * SCOPE GUARD IS A HARD GATE.  A predicate that searched zero places reports "not found",
    and "not found" is not evidence (lesson #20: an empty scope read as a negative finding).
    Every input is asserted to exist before any proposition is evaluated.
  * EACH PREDICATE IS RESPONSIVE.  A test that cannot fail is not a test (lesson #19).  Each
    predicate is therefore also run against a SYNTHETIC MUTATED input and must go red, in
    memory, with no file touched.
  * UNITS GO IN THE FIELD NAMES.  `*_bytes` vs `*_lines` vs `*_seconds` (lesson #25).
  * NO ENVIRONMENT-DERIVED VALUES ARE RECORDED.  No "now", no temp paths, so the evidence
    JSON is byte-identical across runs.

Propositions:
  P-1  the interruption is reproducible from disk bytes (not inferred)
  P-2  no artifact in the interrupted attempt postdates the abort
  P-3  neither I-14-D nor I-14-E-APPLY has an r3 / APPLY-era carrier
  P-4  all four carriers' appends are append-only, per their own independent proofs
  P-5  the product anchor is unchanged and no product file outside .planning is modified
  P-6  nothing was deleted: every must-preserve path is still present
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
PLAN = REPO / ".planning/2026-09-19-three-project-history-audit"
EXEC = PLAN / "execution_runs"
ATTEMPT = EXEC / "_bookkeeping_20260921_round67"

BENCH_LOG = EXEC / "I-14-E-APPLY/a20260921-01/after/bench.log"
B4_LOG = EXEC / "I-14-E-APPLY/a20260921-01/after/arm-logs/B4-nonvacuity-quiet.log"
APPLY_DIR = EXEC / "I-14-E-APPLY/a20260921-01"
I14D_DIR = EXEC / "I-14-D/a20260919-01"

ANCHOR_REL = "scripts/model_registry.py"
ANCHOR_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
ANCHOR_BYTES = 26446

# `STATUS_CONTROL_C_EXIT`: the process was terminated. NOT a business failure code.
STATUS_CONTROL_C_EXIT = 3221225786

ABORT_MINUTE = datetime(2026, 9, 21, 23, 39, 0)   # nothing may postdate this

PROOFS = {
    "task_plan.md": ATTEMPT / "append_only_proof_round67_task_plan.json",
    "findings.md": ATTEMPT / "append_only_proof_round67_findings.json",
    "progress.md": ATTEMPT / "append_only_proof_round67_progress.json",
    "REMEDIATION_REGISTER.md": ATTEMPT / "append_only_proof_round67_register.json",
}

MUST_PRESERVE = [
    ".tmp-r41-mutation",
    "assurance/unified_completion/manifests/plan_inputs.json.bak",
    ".planning/_pwf_tmp/_pre60_tail.bin",
    ".git/COMMIT_MSG_R58.txt",
    ".git/COMMIT_MSG_R59.txt",
    ".git/COMMIT_MSG_R59b.txt",
    ".git/COMMIT_MSG_T17.txt",
]

REQUIRED_INPUTS = [BENCH_LOG, B4_LOG, APPLY_DIR, I14D_DIR,
                   I14D_DIR / "handoff.json", I14D_DIR / "review.md",
                   I14D_DIR / "scratch/oracle_r3.json", I14D_DIR / "scratch/rule_r3.json",
                   REPO / ANCHOR_REL] + list(PROOFS.values())


# ---------------------------------------------------------------- predicates
# Each takes explicit data so the SAME function can be fed a mutated input.

def p1_interruption_reproducible(bench_text: str, b4_bytes: int) -> dict:
    lines = [ln for ln in bench_text.splitlines() if ln.strip()]
    tail = lines[-3:]
    arm_exit = [ln for ln in lines if "EXIT=" in ln][-1:] or [""]
    exit_code = None
    m = re.search(r"EXIT=(\d+)", arm_exit[0])
    if m:
        exit_code = int(m.group(1))
    return {
        "bench_tail_3_lines": tail,
        "last_arm_exit_code": exit_code,
        "last_arm_exit_is_status_control_c": exit_code == STATUS_CONTROL_C_EXIT,
        "last_line_is_a_new_arm_start": bool(tail and "START" in tail[-1]),
        "b4_arm_log_bytes": b4_bytes,
        "b4_arm_log_is_empty": b4_bytes == 0,
        "holds": (exit_code == STATUS_CONTROL_C_EXIT
                  and bool(tail and "START" in tail[-1])
                  and b4_bytes == 0),
    }


def p2_nothing_postdates_abort(newest_mtime: datetime, newest_rel: str) -> dict:
    return {
        "newest_mtime_in_attempt": newest_mtime.isoformat(sep=" "),
        "newest_artifact": newest_rel,
        "abort_minute_boundary": ABORT_MINUTE.isoformat(sep=" "),
        "newest_precedes_boundary": newest_mtime < ABORT_MINUTE,
        "holds": newest_mtime < ABORT_MINUTE,
    }


def p3_carrier_is_stale(carrier_mtime: datetime, newest_artifact_mtime: datetime,
                        carrier_rel: str) -> dict:
    return {
        "carrier": carrier_rel,
        "carrier_mtime": carrier_mtime.isoformat(sep=" "),
        "newest_artifact_mtime": newest_artifact_mtime.isoformat(sep=" "),
        "carrier_predates_the_newest_artifact": carrier_mtime < newest_artifact_mtime,
        "holds": carrier_mtime < newest_artifact_mtime,
    }


def p4_proofs_are_append_only(proofs: dict) -> dict:
    per_target = {}
    for name, proof in sorted(proofs.items()):
        r1 = proof.get("route_1_difflib", {})
        r2 = proof.get("route_2_raw_prefix", {})
        ok = (proof.get("APPEND_ONLY") is True
              and proof.get("pre_image_constant_reproduced") is True
              and r1.get("deleted_lines") == 0
              and set(r1.get("opcodes", ["?"])) <= {"equal", "insert"}
              and r2.get("prefix_is_the_entire_pre_image") is True)
        per_target[name] = {
            "APPEND_ONLY": proof.get("APPEND_ONLY"),
            "pre_image_constant_reproduced": proof.get("pre_image_constant_reproduced"),
            "byte_delta": proof.get("byte_delta"),
            "deleted_lines": r1.get("deleted_lines"),
            "prefix_is_the_entire_pre_image": r2.get("prefix_is_the_entire_pre_image"),
            "ok": ok,
        }
    return {"per_target": per_target,
            "all_ok": all(v["ok"] for v in per_target.values()),
            "holds": all(v["ok"] for v in per_target.values())}


def p5_anchor_and_scope(anchor_sha: str, anchor_bytes: int, product_paths: list) -> dict:
    return {
        "anchor_rel": ANCHOR_REL,
        "anchor_sha256": anchor_sha,
        "anchor_expected_sha256": ANCHOR_SHA,
        "anchor_bytes": anchor_bytes,
        "anchor_expected_bytes": ANCHOR_BYTES,
        "anchor_matches": (anchor_sha == ANCHOR_SHA and anchor_bytes == ANCHOR_BYTES),
        "modified_paths_outside_planning": product_paths,
        "no_product_file_modified": product_paths == [],
        "holds": (anchor_sha == ANCHOR_SHA and anchor_bytes == ANCHOR_BYTES
                  and product_paths == []),
    }


def p6_nothing_deleted(present: dict) -> dict:
    return {
        "paths_checked": present,
        "absent": [k for k, v in present.items() if not v],
        "all_present": all(present.values()),
        "holds": all(present.values()),
    }


# ---------------------------------------------------------------- helpers

def newest_file(root: Path):
    best = (None, None)
    for p in root.rglob("*"):
        try:
            if p.is_file():
                t = datetime.fromtimestamp(p.stat().st_mtime)
                if best[0] is None or t > best[0]:
                    best = (t, str(p.relative_to(REPO)).replace("\\", "/"))
        except OSError:
            continue
    return best


def main() -> int:
    # ---- hard scope guard: refuse to report "not found" about a scope never searched ----
    missing = [str(p.relative_to(REPO)) for p in REQUIRED_INPUTS if not p.exists()]
    if missing:
        raise SystemExit("FATAL: scope guard -- required inputs missing: %s" % missing)

    bench_text = BENCH_LOG.read_text(encoding="utf-8", errors="replace")
    b4_bytes = B4_LOG.stat().st_size

    apply_newest_mtime, apply_newest_rel = newest_file(APPLY_DIR)
    i14d_newest_mtime, i14d_newest_rel = newest_file(I14D_DIR)

    proofs = {k: json.loads(v.read_text(encoding="utf-8")) for k, v in PROOFS.items()}

    anchor_bytes = (REPO / ANCHOR_REL).read_bytes()
    anchor_sha = hashlib.sha256(anchor_bytes).hexdigest()

    diff = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--", ".", ":(exclude).planning"],
        cwd=str(REPO), capture_output=True, text=True).stdout
    outside = [ln for ln in diff.splitlines() if ln.strip()]

    present = {p: (REPO / p).exists() for p in MUST_PRESERVE}

    results = {
        "P-1": p1_interruption_reproducible(bench_text, b4_bytes),
        "P-2": p2_nothing_postdates_abort(apply_newest_mtime, apply_newest_rel),
        "P-3a": p3_carrier_is_stale(
            datetime.fromtimestamp((I14D_DIR / "handoff.json").stat().st_mtime),
            i14d_newest_mtime, "I-14-D/.../handoff.json"),
        "P-3b": p3_carrier_is_stale(
            datetime.fromtimestamp((I14D_DIR / "review.md").stat().st_mtime),
            i14d_newest_mtime, "I-14-D/.../review.md"),
        "P-3c": {
            "apply_dir_has_handoff_json": (APPLY_DIR / "handoff.json").exists(),
            "apply_dir_has_review_md": (APPLY_DIR / "review.md").exists(),
            "holds": not (APPLY_DIR / "handoff.json").exists()
                     and not (APPLY_DIR / "review.md").exists(),
        },
        "P-4": p4_proofs_are_append_only(proofs),
        "P-5": p5_anchor_and_scope(anchor_sha, len(anchor_bytes), outside),
        "P-6": p6_nothing_deleted(present),
    }

    # ---- responsiveness self-check: every predicate must go red on a mutated input ----
    neg = {
        "NC-1 exit code was a business failure": p1_interruption_reproducible(
            bench_text.replace("EXIT=3221225786", "EXIT=0"), b4_bytes)["holds"],
        "NC-2 B4 arm log had content": p1_interruption_reproducible(
            bench_text, 42)["holds"],
        "NC-3 an artifact postdates the abort": p2_nothing_postdates_abort(
            datetime(2026, 9, 21, 23, 45, 0), "synthetic")["holds"],
        "NC-4 the carrier is newer than the artifacts": p3_carrier_is_stale(
            datetime(2026, 9, 21, 23, 40, 0), i14d_newest_mtime,
            "synthetic")["holds"],
        "NC-5 a proof reports a deletion": p4_proofs_are_append_only(
            dict(proofs, **{next(iter(proofs)): dict(
                proofs[next(iter(proofs))],
                route_1_difflib=dict(proofs[next(iter(proofs))]["route_1_difflib"],
                                     deleted_lines=1))}))["holds"],
        "NC-6 the anchor drifted": p5_anchor_and_scope(
            "0" * 64, len(anchor_bytes), outside)["holds"],
        "NC-7 a product file was modified": p5_anchor_and_scope(
            anchor_sha, len(anchor_bytes), ["scripts/model_registry.py"])["holds"],
        "NC-8 something was deleted": p6_nothing_deleted(
            dict(present, **{MUST_PRESERVE[0]: False}))["holds"],
    }
    neg_ok = all(v is False for v in neg.values())

    overall = all(r["holds"] for r in results.values()) and neg_ok

    out = {
        "card": "_bookkeeping_20260921_round67",
        "round": 67,
        "propositions": results,
        "negative_controls": {k: {"holds": v, "correctly_red": v is False}
                              for k, v in neg.items()},
        "negative_controls_all_correctly_red": neg_ok,
        "overall": "PASS" if overall else "FAIL",
    }
    dest = ATTEMPT / "round67_verification.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")

    for k, r in results.items():
        print("%-6s holds=%s" % (k, r["holds"]))
    print("negative controls all correctly red =", neg_ok)
    print("overall =", out["overall"])
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
