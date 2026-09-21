"""B5 / REM-21 batch M25-M28 - run the four arms (E/F/B/G) with REAL processes.

Arm harness (per PROPAGATION_CONTRACT.md section 5):
  E  green control     new runner, frozen cases.json (unmodified)
  F  mutation arm      new runner, first negative's "expected" -> "ValueError"  (the deliverable)
  B  inertness control OLD runner (byte copy of the historical runner), SAME mutated cases.json as F
  G  rc-classification new runner, that negative's "expected" KEY DELETED

Supplementary (extra evidence, clearly labelled, not a contract arm):
  B0 old runner on the FROZEN cases.json -> shows the old runner's unmutated baseline rc
  B1 old runner on an unknown-extra-id cases.json -> isolates that the old runner's rc=1 in arm B
     is its whole-set `expected` gate, not its structural case-count/id gate

Raw rc is read from the child process itself (subprocess returncode); nothing is inferred.
Every path is redirected into this batch's own _scratch tree; nothing under
execution_runs/<CARD>/ is ever written.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M25-M28"
OUTDIR = os.path.join(ATTEMPT, BATCH)
SCRATCH = os.path.join(ATTEMPT, "_scratch", BATCH)
CODE_ROOT = os.path.join(SCRATCH, "code_root")
CARDS = ["M25", "M26", "M27", "M28"]
ISO = os.path.join(PLAN, "execution_runs", "M25", "a20260919-01", "iso")
PY = os.path.join(ISO, "venv", "Scripts", "python.exe")
ISO_CODE_ROOT = os.path.join(ISO, "checkout_scripts")
HISTORICAL_RUNNER = os.path.join(PLAN, "execution_runs", "M25", "a20260919-01",
                                 "scripts", "run_card.py")
EXPECTED_RUNNER_SHA = "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6"
EXPECTED_REGISTRY_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
EXPECTED_EXTENSIONS_SHA = "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"
MUTATED_VALUE = "ValueError"

RUNNERS = {"new": os.path.join(OUTDIR, "run_card.py"),
           "old": os.path.join(OUTDIR, "run_card_before.py")}
ARM_RUNNER = {"E": "new", "F": "new", "B": "old", "G": "new", "B0": "old", "B1": "old"}
ARM_VARIANT = {"E": "frozen", "F": "mutated_value", "B": "mutated_value",
               "G": "deleted_key", "B0": "frozen", "B1": "extra_unknown_id"}
EVIDENCE_FILES = ["input.json", "cases.json", "oracle.json", "negative_results.json"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def arm_root(arm, card):
    return os.path.join(SCRATCH, arm, "evidence", card)


def build_arm_scratch(arm, card):
    """Copy the frozen evidence into the arm dir, then apply this arm's cases.json variant."""
    root = arm_root(arm, card)
    os.makedirs(root, exist_ok=True)
    src = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)
    for name in EVIDENCE_FILES:
        s = os.path.join(src, name)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(root, name))
    frozen_cases = os.path.join(root, "cases.json")
    frozen_sha = sha256_file(frozen_cases)
    variant = ARM_VARIANT[arm]
    mutated_case = None
    if variant != "frozen":
        doc = json.load(open(frozen_cases, encoding="utf-8"))
        target = doc["cases"][0]          # first negative case = lowest id (NEG-CARD)
        mutated_case = target["id"]
        if target.get("expected") != "ModelRegistryError":
            sys.exit("FATAL: %s first case %s expected=%r (contract says ModelRegistryError)"
                     % (card, mutated_case, target.get("expected")))
        if variant == "mutated_value":
            target["expected"] = MUTATED_VALUE
        elif variant == "deleted_key":
            del target["expected"]
        elif variant == "extra_unknown_id":
            extra = json.loads(json.dumps(doc["cases"][-1]))
            extra["id"] = "N99-EXTRA-STRUCTURAL"
            doc["cases"].append(extra)
        dump_json(frozen_cases, doc)
    return {"evidence_dir": root, "frozen_cases_sha256": frozen_sha,
            "cases_sha256": sha256_file(frozen_cases), "variant": variant,
            "mutated_case": mutated_case}


def run_arm(arm, card):
    info = build_arm_scratch(arm, card)
    root = os.path.join(SCRATCH, arm)
    out_path = os.path.join(root, "out_%s.json" % card)
    rr_path = os.path.join(root, "formula_result_%s.json" % card)
    so_path = os.path.join(root, "stdout_%s.txt" % card)
    se_path = os.path.join(root, "stderr_%s.txt" % card)
    argv = [PY, "-X", "utf8", "-B", RUNNERS[ARM_RUNNER[arm]],
            "--card", card,
            "--attempt", root,
            "--code-root", CODE_ROOT,
            "--out", out_path,
            "--run-result-out", rr_path]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    with open(so_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(proc.stdout)
    with open(se_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(proc.stderr)
    doc = None
    if os.path.exists(out_path):
        doc = json.load(open(out_path, encoding="utf-8"))
    rr_doc = None
    if os.path.exists(rr_path):
        rr_doc = json.load(open(rr_path, encoding="utf-8"))
    sem = (doc or {}).get("exit_code_semantics", {})
    nsum = (doc or {}).get("negative_summary", {})
    negs = (doc or {}).get("negatives", [])
    return {
        "arm": arm,
        "card": card,
        "runner_role": ARM_RUNNER[arm],
        "runner_path": RUNNERS[ARM_RUNNER[arm]],
        "cases_variant": info["variant"],
        "mutated_case": info["mutated_case"],
        "frozen_cases_sha256": info["frozen_cases_sha256"],
        "arm_cases_sha256": info["cases_sha256"],
        "argv": argv,
        "cwd": root,
        "raw_rc": proc.returncode,
        "out_json": out_path,
        "out_json_sha256": sha256_file(out_path) if os.path.exists(out_path) else None,
        "run_result_out_json": rr_path,
        "run_result_out_sha256": sha256_file(rr_path) if os.path.exists(rr_path) else None,
        "run_result_out_identical_to_out": (doc == rr_doc) if (doc and rr_doc) else None,
        "out_written": doc is not None,
        "verdict": (doc or {}).get("verdict"),
        "verdict_in_semantics": sem.get("verdict"),
        "exit_code_in_doc": sem.get("exit_code"),
        "no_verdict_reason": (doc or {}).get("no_verdict_reason"),
        "verdict_reasons": (doc or {}).get("verdict_reasons"),
        "harness_incomplete": sem.get("harness_incomplete"),
        "positive_ok": sem.get("positive_ok"),
        "continuity_ok": sem.get("continuity_ok"),
        "negatives_ok": sem.get("negatives_ok"),
        "neg_card_mechanism_ok": sem.get("neg_card_mechanism_ok"),
        "cases_json_declared_expectations_usable": sem.get("cases_json_declared_expectations_usable"),
        "declaration_unusable_case_ids": sem.get("declaration_unusable_case_ids"),
        "declared_expectation_mismatch_case_ids": sem.get("declared_expectation_mismatch_case_ids"),
        "declared_expectation_mismatch_ids": sem.get("declared_expectation_mismatch_ids"),
        "not_judged_case_ids": sem.get("not_judged_case_ids"),
        "negative_counts": (doc or {}).get("negative_counts"),
        "negative_summary_total": nsum.get("total"),
        "negative_summary_passed": nsum.get("passed"),
        "negative_summary_failed": nsum.get("failed"),
        "negative_summary_failed_judged": nsum.get("failed_judged"),
        "negative_summary_not_judged": nsum.get("not_judged"),
        "negative_summary_judged": nsum.get("judged"),
        "declared_expectations_enforced": nsum.get("declared_expectations_enforced"),
        "declared_expectations_in_cases_json": nsum.get("declared_expectations_in_cases_json"),
        "declared_expectation_comparison": nsum.get("declared_expectation_comparison"),
        "case_contract_check": (doc or {}).get("case_contract_check"),
        "case_contract_problems": (doc or {}).get("case_contract_problems"),
        "negatives": [{k: e.get(k) for k in
                       ("id", "expected", "declared", "raised", "verdict", "judged",
                        "declared_expectation_ok", "declared_expectation_mismatch",
                        "declared_expectation_not_met", "declared_expectation_comparison")}
                      for e in negs],
        "stderr_head": proc.stderr[:2000],
        "stdout_tail": proc.stdout[-3000:],
    }


def main():
    results = []
    for arm in ("E", "F", "B", "G", "B0", "B1"):
        for card in CARDS:
            r = run_arm(arm, card)
            results.append(r)
            print("[%s/%s] raw_rc=%s verdict=%r mismatch_ids=%s unusable_ids=%s not_judged=%s"
                  % (arm, card, r["raw_rc"], r["verdict"],
                     r["declared_expectation_mismatch_case_ids"],
                     r["declaration_unusable_case_ids"], r["not_judged_case_ids"]), flush=True)
    dump_json(os.path.join(SCRATCH, "arms_raw.json"), results)
    print("wrote", os.path.join(SCRATCH, "arms_raw.json"))


if __name__ == "__main__":
    main()
