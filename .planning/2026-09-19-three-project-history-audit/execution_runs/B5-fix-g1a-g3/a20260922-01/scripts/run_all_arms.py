"""B5-fix-g1a-g3 (a20260922-01) unified arm harness — REAL child processes, RAW rc only.

Arms (PROPAGATION_CONTRACT §5 + owner G1-a ruling 2026-09-22):
  E  green control : runner "new", frozen cases.json (unmodified)          expect rc=0
  F  mutation arm  : runner "new", first-in-file negative's `expected`
                     -> "ValueError"                                       expect rc=3
  B  inertness     : runner "old" (byte copy of the historical runner),
                     SAME mutated cases as F                               -> measured, unchanged
  G  rc-class arm  : runner "new", that negative's `expected` key DELETED  expect rc=2 (no_verdict)
  S  structural    : runner "new", one EXTRA case with an unknown id       expect rc=1
                     (M25-M28 only — proves the structural arm still aborts at rc=1,
                      unchanged by the G1-a routing)

Runner roles:
  * the six REM-21 batches use this attempt's OWN copies (B5's patch + this card's fixes);
  * M01-M04 and M17-M20 have no patched copy (never in REM-21 scope / reference batch):
    both roles are byte-copies of the historical runner — measurement only.

Nothing under execution_runs/<CARD>/ is written: evidence is COPIED into
<ATTEMPT>/_scratch/<batch>/<arm>/evidence/<CARD>/, outputs land in the arm dir, and every
child runs with -B + PYTHONDONTWRITEBYTECODE=1 so no __pycache__ can appear anywhere
historical. The historical runners themselves are only ever READ (copied out, never touched).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch")

BATCHES = {
    "M01-M04": {"cards": ["M01", "M02", "M03", "M04"], "rep": "M01", "arms": "E/B/G/F"},
    "M05-M08": {"cards": ["M05", "M06", "M07", "M08"], "rep": "M05", "arms": "E/B/G/F"},
    "M09-M12": {"cards": ["M09", "M10", "M11", "M12"], "rep": "M09", "arms": "E/B/G/F"},
    "M13-M16": {"cards": ["M13", "M14", "M15", "M16"], "rep": "M13", "arms": "E/B/G/F"},
    "M17-M20": {"cards": ["M17", "M18", "M19", "M20"], "rep": "M17", "arms": "E/B/G/F"},
    "M21-M24": {"cards": ["M21", "M22", "M23", "M24"], "rep": "M21", "arms": "E/B/G/F"},
    "M25-M28": {"cards": ["M25", "M26", "M27", "M28"], "rep": "M25", "arms": "E/B/G/F/S"},
    "M29-M31": {"cards": ["M29", "M30", "M31"], "rep": "M29", "arms": "E/B/G/F"},
}
# arm order within a batch: E first (green control on a fresh copy), then G, B, F — any order
# works because every arm rebuilds its own evidence copy; E is listed first for readable logs.
ARM_ORDER = ("E", "G", "B", "F", "S")
ARM_RUNNER = {"E": "new", "F": "new", "G": "new", "S": "new", "B": "old"}
ARM_VARIANT = {"E": "frozen", "F": "mutated_value", "B": "mutated_value",
               "G": "deleted_key", "S": "extra_unknown_id"}
OPTIONAL_FLAGS = ("--run-result-out", "--formula-out", "--negative-out")
MUTATED_VALUE = "ValueError"
EXPECTED_REGISTRY_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
EXPECTED_EXTENSIONS_SHA = "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"


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


def supported_flags(runner_path):
    src = open(runner_path, encoding="utf-8").read()
    return set(re.findall(r"add_argument\(\s*[\"'](--[a-z0-9-]+)[\"']", src))


def setup_batch(batch, cfg):
    rep = cfg["rep"]
    bscratch = os.path.join(SCRATCH, batch)
    code_root = os.path.join(bscratch, "code_root")
    os.makedirs(code_root, exist_ok=True)
    iso_scripts = os.path.join(PLAN, "execution_runs", rep, "a20260919-01", "iso",
                               "checkout_scripts")
    for name in ("model_registry.py", "model_extensions.py"):
        src = os.path.join(iso_scripts, name)
        dst = os.path.join(code_root, name)
        if not os.path.exists(dst) or sha256_file(dst) != sha256_file(src):
            shutil.copyfile(src, dst)
    reg_sha = sha256_file(os.path.join(code_root, "model_registry.py"))
    ext_sha = sha256_file(os.path.join(code_root, "model_extensions.py"))
    assert reg_sha == EXPECTED_REGISTRY_SHA, (batch, reg_sha)
    assert ext_sha == EXPECTED_EXTENSIONS_SHA, (batch, ext_sha)
    py = os.path.join(PLAN, "execution_runs", rep, "a20260919-01", "iso", "venv", "Scripts",
                      "python.exe")
    runners = {"new": os.path.join(ATTEMPT, batch, "run_card.py"),
               "old": os.path.join(ATTEMPT, batch, "run_card_before.py")}
    runner_sha = {role: sha256_file(p) for role, p in runners.items()}
    flags = {role: sorted(supported_flags(p) & set(OPTIONAL_FLAGS)) for role, p in runners.items()}
    # both roles must be invoked with the SAME flag set, else arm comparisons are not like-for-like
    common = sorted(set(flags["new"]) & set(flags["old"]))
    return {"scratch": bscratch, "code_root": code_root, "py": py, "runners": runners,
            "runner_sha256": runner_sha, "flags": common,
            "code_root_sha256": {"model_registry.py": reg_sha, "model_extensions.py": ext_sha}}


def build_evidence(batch, card, arm, variant):
    """Copy the card's historical evidence (top-level files only) into the arm dir, then apply
    this arm's cases.json variant. Returns variant metadata."""
    root = os.path.join(SCRATCH, batch, arm, "evidence", card)
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    src = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)
    copied = []
    for name in sorted(os.listdir(src)):
        s = os.path.join(src, name)
        if os.path.isfile(s):
            shutil.copyfile(s, os.path.join(root, name))
            copied.append(name)
    info = {"evidence_dir": root, "copied_files": len(copied), "variant": variant,
            "frozen_cases_sha256": None, "cases_sha256": None, "mutated_case": None,
            "mutated_case_index": None}
    cases_path = os.path.join(root, "cases.json")
    info["frozen_cases_sha256"] = sha256_file(cases_path)
    if variant != "frozen":
        doc = json.load(open(cases_path, encoding="utf-8"))
        target = None
        index = None
        for i, case in enumerate(doc["cases"]):
            if case.get("expected") == "ModelRegistryError":
                target, index = case, i
                break
        assert target is not None, (batch, card, "no case with expected=ModelRegistryError")
        info["mutated_case"] = target["id"]
        info["mutated_case_index"] = index
        if variant == "mutated_value":
            target["expected"] = MUTATED_VALUE
        elif variant == "deleted_key":
            del target["expected"]
        elif variant == "extra_unknown_id":
            extra = json.loads(json.dumps(doc["cases"][-1]))
            extra["id"] = "N99-EXTRA-STRUCTURAL"
            doc["cases"].append(extra)
        dump_json(cases_path, doc)
    info["cases_sha256"] = sha256_file(cases_path)
    return info


def run_one(batch, cfg, env, arm, card):
    runner_role = ARM_RUNNER[arm]
    variant = ARM_VARIANT[arm]
    runner = env["runners"][runner_role]
    arm_dir = os.path.join(env["scratch"], arm)
    os.makedirs(arm_dir, exist_ok=True)
    info = build_evidence(batch, card, arm, variant)
    out_path = os.path.join(arm_dir, "out_%s.json" % card)
    for stale in (out_path, os.path.join(arm_dir, "formula_result_%s.json" % card),
                  os.path.join(arm_dir, "run_result_%s.json" % card),
                  os.path.join(arm_dir, "negative_results_%s.json" % card)):
        if os.path.exists(stale):
            os.remove(stale)
    argv = [env["py"], "-X", "utf8", "-B", runner,
            "--card", card,
            "--attempt", arm_dir,
            "--code-root", env["code_root"],
            "--out", out_path]
    for flag in env["flags"]:
        argv += [flag, os.path.join(arm_dir, flag.lstrip("-") + "_%s.json" % card)]
    proc = subprocess.run(argv, cwd=arm_dir, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    with open(os.path.join(arm_dir, "stdout_%s.txt" % card), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(proc.stdout)
    with open(os.path.join(arm_dir, "stderr_%s.txt" % card), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(proc.stderr)

    doc = None
    if os.path.exists(out_path):
        doc = json.load(open(out_path, encoding="utf-8"))
    sem = (doc or {}).get("exit_code_semantics") or {}
    nsum = (doc or {}).get("negative_summary") or {}
    ncnt = (doc or {}).get("negative_counts") or {}
    ccc = (doc or {}).get("case_contract_check") or {}
    facts = ((doc or {}).get("expectation_consistency") or {}).get("facts") or {}
    negs = (doc or {}).get("negatives") or []
    rec = {
        "batch": batch, "arm": arm, "card": card,
        "runner_role": runner_role, "runner_path": runner,
        "runner_sha256": env["runner_sha256"][runner_role],
        "cases_variant": variant,
        "mutated_case": info["mutated_case"],
        "mutated_case_index": info["mutated_case_index"],
        "frozen_cases_sha256": info["frozen_cases_sha256"],
        "arm_cases_sha256": info["cases_sha256"],
        "evidence_copied_files": info["copied_files"],
        "argv": argv, "cwd": arm_dir,
        "raw_rc": proc.returncode,
        "out_written": doc is not None,
        "out_json": out_path if doc is not None else None,
        "out_json_sha256": sha256_file(out_path) if doc is not None else None,
        "verdict": (doc or {}).get("verdict"),
        "verdict_in_semantics": sem.get("verdict"),
        "exit_code_in_doc": sem.get("exit_code"),
        "no_verdict_reason": (doc or {}).get("no_verdict_reason") or sem.get("no_verdict_reason"),
        "verdict_reasons": (doc or {}).get("verdict_reasons"),
        "mismatch_ids": sem.get("declared_expectation_mismatch_case_ids"),
        "unusable_ids": sem.get("declaration_unusable_case_ids"),
        "not_judged_ids": sem.get("not_judged_case_ids"),
        "set_level_route": sem.get("set_level_declaration_route"),
        "set_level_usable_diff_ids": sem.get("set_level_usable_diff_case_ids"),
        "set_level_unusable_ids": sem.get("set_level_unusable_case_ids"),
        "cases_declared_usable": sem.get("cases_json_declared_expectations_usable"),
        "mismatch_count": ncnt.get("declared_expectation_mismatch"),
        "missing_count": ncnt.get("declared_expectation_missing_in_cases_json"),
        "negative_summary_not_judged": nsum.get("not_judged"),
        "case_contract_route_rc": ccc.get("set_level_declaration_route_rc"),
        "case_contract_gating": ccc.get("set_level_declaration_gating"),
        "structural_problems": ccc.get("structural_problems"),
        "negatives": [{"id": e.get("id"), "expected": e.get("expected"),
                       "declared": e.get("declared"), "raised": e.get("raised"),
                       "verdict": e.get("verdict"), "judged": e.get("judged"),
                       "declared_expectation_mismatch": e.get("declared_expectation_mismatch")}
                      for e in negs],
        "g3_facts_keys": sorted(facts.keys()),
        "g3_old_key_present": "declared_expectations" in facts,
        "g3_new_key_present": "declared_expectations_in_cases_json" in facts,
        "g3_keys_equal": (("declared_expectations" in facts)
                          and ("declared_expectations_in_cases_json" in facts)
                          and facts["declared_expectations"] == facts["declared_expectations_in_cases_json"]),
        "stderr_head": proc.stderr[:1200],
        "stdout_tail": proc.stdout[-1200:],
    }
    return rec


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None  # optional: batch name filter
    results = []
    for batch, cfg in BATCHES.items():
        if only and batch != only:
            continue
        env = setup_batch(batch, cfg)
        arms = [a for a in ARM_ORDER if a in cfg["arms"]]
        print("== %s runner_new=%s runner_old=%s flags=%s"
              % (batch, env["runner_sha256"]["new"][:12],
                 env["runner_sha256"]["old"][:12], ",".join(env["flags"])), flush=True)
        for arm in arms:
            for card in cfg["cards"]:
                rec = run_one(batch, cfg, env, arm, card)
                results.append(rec)
                print("  [%s/%s] %s raw_rc=%s verdict=%r mismatch=%s unusable=%s "
                      "route=%s mutated=%s"
                      % (arm, card, rec["runner_role"], rec["raw_rc"], rec["verdict"],
                         rec["mismatch_ids"], rec["unusable_ids"],
                         rec["case_contract_route_rc"], rec["mutated_case"]), flush=True)
    dump_json(os.path.join(SCRATCH, "arms_raw.json"), results)
    print("wrote", os.path.join(SCRATCH, "arms_raw.json"), "(%d runs)" % len(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
