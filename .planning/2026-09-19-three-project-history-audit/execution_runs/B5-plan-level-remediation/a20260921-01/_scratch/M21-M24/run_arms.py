"""B5 / REM-21 batch M21-M24 -- arm driver.

Runs the four contract arms (E green control, F mutation, B inertness, G rc-classification)
for every card M21..M24 with REAL child processes, capturing the RAW process exit code.

Nothing under execution_runs/<CARD>/ is ever written: every path is redirected into
_scratch/M21-M24/<arm>/.  Runs are made with the batch's own isolated venv interpreter and
-B so no __pycache__ can appear anywhere.
"""

import json
import os
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M21-M24")
OUTDIR = os.path.join(ATTEMPT, "M21-M24")

PY = os.path.join(PLAN, "execution_runs", "M21", "a20260919-01", "iso", "venv", "Scripts",
                  "python.exe")
CODE_ROOT = os.path.join(SCRATCH, "code_root")
CARDS = ("M21", "M22", "M23", "M24")

ARMS = {
    # arm: (runner file, cases profile)
    "E": ("run_card.py", "frozen"),
    "F": ("run_card.py", "mutate-NEG-CARD-to-ValueError"),
    "B": ("run_card_before.py", "mutate-NEG-CARD-to-ValueError"),
    "G": ("run_card.py", "delete-NEG-CARD-expected"),
}
# extra arm: same mutation applied to the LOWEST-ID case (CONT-BREAK) instead, to prove the
# choice between "lowest id" and "first negative in file order" does not change any rc value.
EXTRA_ARMS = {
    "F2": ("run_card.py", "mutate-CONT-BREAK-to-ValueError"),
    "B2": ("run_card_before.py", "mutate-CONT-BREAK-to-ValueError"),
}


def load(p):
    with open(p, "r", encoding="utf-8") as h:
        return json.load(h)


def dump(o, p):
    with open(p, "w", encoding="utf-8") as h:
        json.dump(o, h, ensure_ascii=False, indent=1)


MUST_KEEP = ("verdict", "negative_summary", "negative_counts", "negatives",
             "exit_code_semantics", "frozen_declaration_assertion",
             "required_message_ids_assertion")


def run_one(arm, card, runner_file, profile):
    arm_dir = os.path.join(SCRATCH, arm)
    ev = os.path.join(arm_dir, "evidence", card)
    out_json = os.path.join(arm_dir, "out_%s.json" % card)
    rr_json = os.path.join(arm_dir, "run_result_%s.json" % card)
    for stale in (out_json, rr_json):
        if os.path.exists(stale):
            os.remove(stale)
    # build the argv: exactly the batch's own B-unit shape, every path redirected into scratch
    argv = [PY, "-X", "utf8", "-B", os.path.join(OUTDIR, runner_file),
            "--card", card,
            "--attempt", arm_dir,
            "--code-root", CODE_ROOT,
            "--out", out_json,
            "--run-result-out", rr_json]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=arm_dir, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    rec = {
        "arm": arm, "card": card, "profile": profile,
        "runner_file": runner_file,
        "runner_sha256": sha256(os.path.join(OUTDIR, runner_file)),
        "cases_json_sha256": sha256(os.path.join(ev, "cases.json")),
        "argv": argv,
        "cwd": arm_dir,
        "raw_rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "out_json": out_json,
        "out_json_exists": os.path.exists(out_json),
    }
    if rec["out_json_exists"]:
        doc = load(out_json)
        rec["verdict"] = (doc.get("exit_code_semantics") or {}).get("verdict")
        rec["no_verdict_reason"] = (doc.get("frozen_declaration_assertion") or {}).get(
            "no_verdict_reason")
        n = {e["id"]: e for e in doc.get("negatives", [])}
        rec["negative_counts"] = doc.get("negative_counts")
        rec["negatives_brief"] = {
            k: {"verdict": v.get("verdict"),
                "raised": v.get("raised"),
                "declared": v.get("declared"),
                "declared_expectation_mismatch": v.get("declared_expectation_mismatch"),
                "declared_expectation_not_met": v.get("declared_expectation_not_met"),
                "declared_expectation_ok": v.get("declared_expectation_ok"),
                "declared_expectation_comparison": v.get("declared_expectation_comparison"),
                "expected_type_matches_raised": v.get("expected_type_matches_raised"),
                "judged": v.get("judged"),
                "message_requirement_met": v.get("message_requirement_met"),
                }
            for k, v in n.items()}
        rec["echoed_expected_field"] = {k: v.get("expected") for k, v in n.items()}
        rec["missing_upstream_keys"] = [k for k in MUST_KEEP if k not in doc]
    return rec


def sha256(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    runs = {}
    arms = {**ARMS, **EXTRA_ARMS}
    for arm in arms:
        if which != "all" and arm != which:
            continue
        runner_file, profile = arms[arm]
        for card in CARDS:
            rec = run_one(arm, card, runner_file, profile)
            runs["%s/%s" % (arm, card)] = rec
            print("arm=%-3s card=%s raw_rc=%s verdict=%s mismatches=%s"
                  % (arm, card, rec["raw_rc"], rec.get("verdict"),
                     (rec.get("negative_counts") or {}).get("declared_expectation_mismatch")))
    path = os.path.join(SCRATCH, "arm_runs.json")
    if which == "all":
        dump(runs, path)
    else:
        prev = load(path) if os.path.exists(path) else {}
        prev.update(runs)
        dump(prev, path)
    print("wrote", path, "(%d runs)" % len(runs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
