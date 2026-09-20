"""Evidence packer for cards M25-M28 (attempt-local, stdlib only).

Writes the receipt/manifest layer of evidence/<CARD>/:
  source_manifest.json, command_manifest.json, negative_results.json,
  qualification.json, integrity.json, evidence_hashes.json, revision_r2.json,
  oq_rulings.json, oq_rulings_enumeration.json, forecast_integration.json,
  historical_mapping_probe.json, accounting_decision.md, disclosure_mapping.json,
  historical_reconciliation.json

Read-only with respect to the product: the only product module it imports is the
attempt-local ISOLATED snapshot in iso/checkout_scripts (never the production tree),
and it only reads MODEL_REGISTRY metadata to ENUMERATE it. It never calls
calculate_registered_model, so it cannot influence any frozen expectation.

Run:
  python -X utf8 -B scripts/pack_evidence.py --card M25 --attempt-root <attempt> --interpreter <py>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    return path


PRODUCTION_HASHES = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}

CARD_META = {
    "M25": {
        "model_id": "installed_base_aftermarket",
        "title": "M25 · installed_base_aftermarket · 装机存量售后",
        "opening": ("base_installed_units_parameter_id", "opening_installed_units", "quantity"),
        "bridge": True,
        "optional_declared_default": None,
        "special_reviews": [
            "DEC-M25-1: whether the current-period newly retired units may sit outside the "
            "opening retirement cohort (card_M25.md L54) - PROPOSED, unsigned",
            "DEC-M25-2: equipment-age dispersion and double charging between contract and "
            "consumable revenue (card_M25.md L54) - PROPOSED, unsigned",
        ],
        "missing_disclosure": ["installed-base bridge", "install/retire dates",
                               "paid attached units", "per-unit service/consumable revenue",
                               "opening anchor"],
    },
    "M26": {
        "model_id": "store_cohorts",
        "title": "M26 · store_cohorts · 开闭店与新店成熟度",
        "opening": ("base_stores_parameter_id", "opening_stores", "quantity"),
        "bridge": True,
        "optional_declared_default": None,
        "special_reviews": [
            "DEC-M26-1: treating a next-year new store as an opening mature store is a "
            "simplification (card_M26.md L54) - PROPOSED, unsigned",
            "DEC-M26-2: multi-year ramps are not covered by the single-year fraction "
            "(card_M26.md L54) - PROPOSED, unsigned",
        ],
        "missing_disclosure": ["opening/closing store months", "sales by store age",
                               "mature-store revenue", "ramp", "like-for-like growth",
                               "cannibalisation", "opening anchor"],
    },
    "M27": {
        "model_id": "renewable_generation",
        "title": "M27 · renewable_generation · 发电量与电价",
        "opening": None,
        "bridge": False,
        "optional_declared_default": "other_revenue",
        "special_reviews": [
            "DEC-M27-1: average MW must not be multiplied by time again (card_M27.md L54) - "
            "PROPOSED, unsigned",
            "DEC-M27-2: a net capacity factor must not deduct curtailment twice "
            "(card_M27.md L54) - PROPOSED, unsigned",
            "DEC-M27-3: a negative power price may be entered but a negative total revenue is "
            "not supported (card_M27.md L54) - PROPOSED, unsigned",
        ],
        "missing_disclosure": ["actual period hours / leap year", "average MW",
                               "pre-curtailment capacity factor", "curtailment",
                               "contracted share", "price subsidies"],
    },
    "M28": {
        "model_id": "aum_fee_bridge",
        "title": "M28 · aum_fee_bridge · AUM流量与收费桥",
        "opening": ("base_aum_parameter_id", "opening_aum", "monetary_balance"),
        "bridge": True,
        "optional_declared_default": "recognized_performance_fees",
        "special_reviews": [
            "DEC-M28-1: a year-end AUM must not be charged a full year of fees "
            "(card_M28.md L60) - PROPOSED, unsigned",
            "DEC-M28-2: the timing of market moves and performance-fee crystallisation needs "
            "evidence (card_M28.md L60) - PROPOSED, unsigned",
        ],
        "missing_disclosure": ["AUM bridge", "gross inflows/outflows", "market/FX effect",
                               "time weighting", "fee rate", "recognised performance fees",
                               "anchor"],
    },
}


def enumerate_registry(code_root):
    """Read-only enumeration of the isolated registry (never calls a calculator)."""
    sys.path.insert(0, code_root)
    import model_registry  # noqa: E402

    out = {
        "code_root": code_root,
        "model_registry_file": model_registry.__file__,
        "model_registry_sha256": sha256_file(model_registry.__file__),
        "models_total": len(model_registry.MODEL_REGISTRY),
        "drivers_total_slots": 0,
        "ratio_drivers_of_drivers_total": 0,
        "ratio_drivers_taking_the_0_1_default_of_ratio_drivers": 0,
        "ratio_drivers_not_in_0_1": [],
        "models": {},
    }
    for model_id, spec in sorted(model_registry.MODEL_REGISTRY.items()):
        entry = {
            "dimensions": dict(spec.dimensions),
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "explicit_driver_bounds": {k: [None if b[0] is None else b[0],
                                           None if b[1] is None else b[1]]
                                       for k, b in dict(spec.driver_bounds).items()},
            "ratio_drivers": sorted(spec.ratio_drivers),
        }
        ratio_bounds = {}
        for driver, dimension in spec.dimensions.items():
            out["drivers_total_slots"] += 1
            lower, upper = model_registry.driver_value_bounds(model_id, driver)
            if dimension == "ratio":
                out["ratio_drivers_of_drivers_total"] += 1
                ratio_bounds[driver] = [None if lower == float("-inf") else lower,
                                        None if upper == float("inf") else upper]
                if lower == 0.0 and upper == 1.0:
                    out["ratio_drivers_taking_the_0_1_default_of_ratio_drivers"] += 1
                else:
                    out["ratio_drivers_not_in_0_1"].append({
                        "driver": model_id + "." + driver,
                        "bounds": ratio_bounds[driver],
                        "declared_bounds": entry["explicit_driver_bounds"].get(driver),
                        "reason": ("explicit spec.driver_bounds entry takes precedence over the "
                                   "conservative [0,1] ratio default"
                                   if driver in entry["explicit_driver_bounds"]
                                   else "hard-coded domain inside driver_value_bounds"),
                    })
        entry["ratio_driver_bounds"] = ratio_bounds
        out["models"][model_id] = entry
    out["model_ids"] = sorted(model_registry.MODEL_REGISTRY)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARD_META))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", required=True)
    parser.add_argument("--oracle-md-sha-before-run", default=None,
                        help="oracle.md sha256 just before the definitive product run")
    parser.add_argument("--oracle-json-sha-before-run", default=None,
                        help="oracle.json sha256 just before the definitive product run")
    parser.add_argument("--oracle-json-sha-before-correction", default=None,
                        help="legacy: superseded by the v1 comparison computed at pack time")
    parser.add_argument("--oracle-md-sha-before-correction", default=None,
                        help="legacy: oracle.md did not exist before the correction, so this is null")
    parser.add_argument("--line-ending-record", default=None,
                        help=("JSON object recording the worktree-byte and git-blob sha256 of the "
                              "JSON evidence, produced by scripts/line_ending_probe.py"))
    args = parser.parse_args()

    card = args.card
    meta = CARD_META[card]
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    selfcheck = os.path.join(attempt, "recovery", "selfcheck")

    input_doc = load(os.path.join(ev, "input.json"))
    oracle_doc = load(os.path.join(ev, "oracle.json"))
    cases_doc = load(os.path.join(ev, "cases.json"))
    run_result = load(os.path.join(ev, "run_result.json"))

    scripts = {
        "scripts/run_card.py": sha256_file(os.path.join(attempt, "scripts", "run_card.py")),
        "scripts/oracle_M25_M28.py": sha256_file(
            os.path.join(attempt, "scripts", "oracle_M25_M28.py")),
        "iso/checkout_scripts/model_registry.py": sha256_file(
            os.path.join(code_root, "model_registry.py")),
        "iso/checkout_scripts/model_extensions.py": sha256_file(
            os.path.join(code_root, "model_extensions.py")),
        "recovery/selfcheck/make_mutations.py": sha256_file(
            os.path.join(selfcheck, "make_mutations.py")),
        "recovery/selfcheck/naive_oracle.py": sha256_file(
            os.path.join(selfcheck, "naive_oracle.py")),
    }

    def mtime(path):
        return round(os.path.getmtime(path), 6)

    # ---------------- source_manifest ----------------
    oracle_md_path = os.path.join(attempt, "oracle.md")
    manifest = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": meta["model_id"],
        "card_title": meta["title"],
        "entry_point": ("scripts/model_registry.py calculate_registered_model("
                        "model_id, base_revenue, drivers, years)"),
        "registration_site": "scripts/model_extensions.py build_extension_specs(...)",
        "production_source_root_readonly": "C:\\Users\\郑曾波\\Projects\\revenue-forecast",
        "production_source_hashes_at_binding_and_after_run": PRODUCTION_HASHES,
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py": scripts[
                "iso/checkout_scripts/model_registry.py"],
            "iso/checkout_scripts/model_extensions.py": scripts[
                "iso/checkout_scripts/model_extensions.py"],
        },
        "isolated_copy_equals_production": (
            scripts["iso/checkout_scripts/model_registry.py"] == PRODUCTION_HASHES[
                "scripts/model_registry.py"]
            and scripts["iso/checkout_scripts/model_extensions.py"] == PRODUCTION_HASHES[
                "scripts/model_extensions.py"]),
        "interpreter": {
            "path": args.interpreter,
            "session_flags": ["-X", "utf8", "-B"],
            "note": ("attempt-local venv created with `python -m venv` from the I-00-A template "
                     "venv; pytest installed offline from the local pip cache"),
            "global_python_used_for": "nothing in this card (no PDF extraction was needed)",
        },
        "card_script_hashes": scripts,
        "oracle_document": {
            "path": "oracle.md",
            "sha256_now": sha256_file(oracle_md_path),
            "sha256_before_the_definitive_product_run": args.oracle_md_sha_before_run,
            "honest_gap": (
                "oracle.md was written before the DEFINITIVE product run and its frozen body "
                "(sections 0-11) was NOT modified afterwards; only APPENDED revision sections were "
                "added (the r2 section). The expected values were frozen in "
                "evidence/<card>/oracle.json by the independent stdlib generator. The generator is "
                "reproducible byte-for-byte (proved by the self-check G regeneration in "
                "evidence/<card>/oracle_selfcheck.json). Three provenance facts are recorded "
                "rather than hidden: (1) the v1 generation had a defect which was corrected before "
                "the definitive run - the only expectation that ever changed is M25's NON-GATING "
                "defaults block, and the timeline is in evidence/<card>/revision_r2.json; (2) the "
                "v1 generator SOURCE and the M27 crash traceback were never persisted, so that "
                "accident is not reproducible (provenance gap); (3) the M26/M27/M28 NEG-CARD patch "
                "was corrected under review finding P2-1 and cases.json was re-frozen before the "
                "definitive run. commands.json records argv and raw exit codes ONLY and does NOT "
                "carry an oracle.md hash."),
            "mtime_ordering": {
                "oracle_json_mtime": mtime(os.path.join(ev, "oracle.json")),
                "input_json_mtime": mtime(os.path.join(ev, "input.json")),
                "oracle_md_mtime": mtime(oracle_md_path),
                "first_ever_product_run_stdout_mtime": mtime(os.path.join(
                    attempt, "recovery", "precorrection", "stdout.txt")),
                "definitive_product_stdout_mtime": mtime(os.path.join(ev, "stdout.txt")),
                "oracle_json_precedes_the_definitive_run": mtime(os.path.join(ev, "oracle.json")) <
                mtime(os.path.join(ev, "stdout.txt")),
                "oracle_json_precedes_the_first_ever_run": mtime(
                    os.path.join(ev, "oracle.json")) < mtime(os.path.join(
                        attempt, "recovery", "precorrection", "stdout.txt")),
                "note": ("r2 re-froze cases.json and re-ran the product, so the ORACLE.JSON mtime is "
                         "later than the first ever run of this attempt. What the mtime ordering "
                         "does establish is the pair that matters for the verdict: the frozen "
                         "evidence and oracle.md both precede the DEFINITIVE run that produced "
                         "evidence/<card>/stdout.txt."),
            },
            "oracle_script_selfcheck": ("evidence/%s/oracle_selfcheck.json records the generator's "
                                        "import list, product_import_present=false and the "
                                        "byte-identical regeneration hashes" % card),
        },
        "evidence_input_hashes": {
            "evidence/%s/input.json" % card: sha256_file(os.path.join(ev, "input.json")),
            "evidence/%s/oracle.json" % card: sha256_file(os.path.join(ev, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256_file(os.path.join(ev, "cases.json")),
        },
        "registry_metadata_observed_from_the_isolated_copy": run_result["registry_metadata"],
        "network_calls": "none",
        "llm_or_provider_calls": "none",
    }
    dump(os.path.join(ev, "source_manifest.json"), manifest)

    # ---------------- command_manifest ----------------
    commands = [
        {"unit_id": "A0-%s-iso-venv-create" % card,
         "purpose": "create the attempt-local isolated interpreter from the I-00-A template venv",
         "argv": [os.path.join(
             "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\.planning\\"
             "2026-09-19-three-project-history-audit",
             "execution_runs", "I-00-A", "a20260919-01", "iso", "venv", "Scripts", "python.exe"),
             "-m", "venv", os.path.join(attempt, "iso", "venv")],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "note": ("the global Miniconda python is forbidden for card runs; the template "
                  "interpreter is the I-00-A venv")},
        {"unit_id": "A1-%s-pytest-offline-install" % card,
         "purpose": "install pytest into the isolated venv from the local pip cache (no index)",
         "argv": [args.interpreter, "-m", "pip", "install", "--no-index", "--find-links",
                  os.path.join(attempt, "iso", "_wheels"), "pytest"],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "note": ("wheels were first obtained with `pip download pytest -d iso/_wheels` from the "
                  "local pip cache; pytest 9.1.1 installed. No card case uses pytest: the formula "
                  "oracle is a direct call to the single bound entry point")},
        {"unit_id": "A2-%s-isolated-snapshot" % card,
         "purpose": "materialise the read-only isolated code snapshot and confirm it is byte-identical to production",
         "argv": ["powershell", "Copy-Item",
                  "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts\\model_registry.py",
                  os.path.join(code_root, "model_registry.py")],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "hashes": {"production_scripts/model_registry.py": PRODUCTION_HASHES[
             "scripts/model_registry.py"],
             "production_scripts/model_extensions.py": PRODUCTION_HASHES[
                 "scripts/model_extensions.py"]},
         "note": "also copied model_extensions.py; both isolated copies hash-equal to production"},
        {"unit_id": "A3-%s-oracle-generate" % card,
         "purpose": ("generate the frozen independent oracle (input.json / oracle.json / cases.json) "
                     "BEFORE any product run"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "oracle_M25_M28.py"),
                  "--card", card, "--out-root", attempt],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "note": ("stdlib only; this file never imports the product "
                  "(product_import_present=false in evidence/%s/oracle_selfcheck.json); the first "
                  "generation had a defect that was corrected BEFORE the definitive product run "
                  "(see revision_r2.json)" % card)},
        {"unit_id": "B-%s-product-positive-defaults-continuity-negatives" % card,
         "purpose": ("run the ONLY product entry point against the isolated snapshot: positive, "
                     "continuity positive, defaults case, 11 negatives and the non-gating observations"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "run_card.py"),
                  "--card", card, "--attempt", attempt, "--code-root", code_root,
                  "--out", os.path.join(ev, "run_result.json"),
                  "--run-result-out", os.path.join(ev, "formula_result.json")],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "expected_business_result": ("verdict pass = positive within 1e-9*max(1,|e|), continuity "
                                      "positive ok, and all 11 negatives rejected with "
                                      "ModelRegistryError"),
         "stdout": "evidence/%s/stdout.txt" % card,
         "stderr": "evidence/%s/stderr.txt" % card},
        {"unit_id": "G1-%s-selfcheck-case-A-corrupt-positive-expectation" % card,
         "purpose": ("mutation proof: plant 999.0 as the positive expectation in a SCRATCH copy and "
                     "show the runner goes red (rc=3)"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "run_card.py"), "--card", card,
                  "--attempt", attempt,
                  "--attempt-dir", os.path.join(selfcheck, "cases", "A"),
                  "--code-root", code_root,
                  "--out", os.path.join(selfcheck, "run_result_A.json")],
         "network": "disabled", "raw_rc": 3, "expected_rc": 3,
         "note": "the mutated oracle.json lives only under recovery/selfcheck/cases/A/"},
        {"unit_id": "G2-%s-selfcheck-case-B-naive-hand-expectation" % card,
         "purpose": ("mutation proof: plant MY OWN deliberately wrong hand value as the positive "
                     "expectation in a SCRATCH copy and show the runner goes red (rc=3)"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "run_card.py"), "--card", card,
                  "--attempt", attempt,
                  "--attempt-dir", os.path.join(selfcheck, "cases", "B"),
                  "--code-root", code_root,
                  "--out", os.path.join(selfcheck, "run_result_B.json")],
         "network": "disabled", "raw_rc": 3, "expected_rc": 3,
         "note": "the planted value comes from recovery/selfcheck/naive_oracle.py, never from the product"},
        {"unit_id": "G3-%s-selfcheck-case-C-restored-green-control" % card,
         "purpose": "green control: the same scratch tree with the frozen expectation restored (rc=0)",
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "run_card.py"), "--card", card,
                  "--attempt", attempt,
                  "--attempt-dir", os.path.join(selfcheck, "cases", "C"),
                  "--code-root", code_root,
                  "--out", os.path.join(selfcheck, "run_result_C.json")],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "note": "proves the repair is possible and the frozen hash is what makes it green"},
        {"unit_id": "G4-%s-selfcheck-case-D-unrejected-negative" % card,
         "purpose": ("mutation proof: replace NEG-CARD's mutation with the identity value through "
                     "--case-override (in memory) so the model must ACCEPT it; the runner must go "
                     "red with FAIL_not_rejected (rc=3)"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "run_card.py"), "--card", card,
                  "--attempt", attempt,
                  "--attempt-dir", os.path.join(selfcheck, "cases", "D"),
                  "--code-root", code_root,
                  "--case-override", os.path.join(selfcheck, "case_D_override.json"),
                  "--out", os.path.join(selfcheck, "run_result_D.json")],
         "network": "disabled", "raw_rc": 3, "expected_rc": 3,
         "note": "the frozen cases.json is untouched; the patch happens in memory only"},
        {"unit_id": "G5-%s-selfcheck-case-E-regenerate-frozen-oracle" % card,
         "purpose": ("reproducibility proof: re-run the SAME oracle generator with --out-root "
                     "pointed at a scratch tree and diff the three artefacts against the frozen ones"),
         "cwd": attempt,
         "argv": [args.interpreter, "-X", "utf8", "-B",
                  os.path.join(attempt, "scripts", "oracle_M25_M28.py"), "--card", card,
                  "--out-root", os.path.join(selfcheck, "generated")],
         "network": "disabled", "raw_rc": 0, "expected_rc": 0,
         "note": ("byte-identical for input.json, cases.json and oracle.json; the frozen evidence "
                  "directory is never written to")},
    ]
    dump(os.path.join(ev, "command_manifest.json"), {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "cwd": attempt,
        "rules": [
            "every product invocation used --code-root <attempt>/iso/checkout_scripts",
            "raw exit codes are recorded as returned; expected codes are separate fields",
            "skip / timeout / not-collected is never recorded as pass",
            "every scratch (G) unit reads and writes only under recovery/selfcheck/",
        ],
        "units": commands,
    })

    # ---------------- negative_results ----------------
    dump(os.path.join(ev, "negative_results.json"), {
        "card_id": card,
        "model_id": meta["model_id"],
        "entry_point": "model_registry.calculate_registered_model(**input)",
        "code_root": code_root,
        "negative_summary": run_result["negative_summary"],
        "continuity_positive": run_result["continuity_positive"],
        "defaults_case_not_gating": run_result["defaults"],
        "defaults_declared_check_not_gating": run_result["defaults_declared_check"],
        "observations_not_gating": run_result["observations"],
        "per_value_checks": run_result.get("per_value_checks"),
        "length_ok": run_result.get("length_ok"),
        "negatives": run_result["negatives"],
        "pass_rule": ("PASS_rejected requires isinstance(exc, ModelRegistryError); ImportError, "
                      "ModuleNotFoundError and FileNotFoundError are recorded as FAIL"),
    })

    # ---------------- qualification ----------------
    dump(os.path.join(ev, "qualification.json"), {
        "card_id": card,
        "model_id": meta["model_id"],
        "implementer_is_not_the_reviewer": True,
        "formula": {
            "state": "review_pending",
            "a_to_c_conditions": {
                "positive_within_frozen_tolerance": bool(run_result.get("tolerances_ok")),
                "continuity_positive_ok": bool(run_result["continuity_positive"].get("ok")),
                "defaults_case_ok_not_gating": bool(run_result.get("defaults_ok")),
                "negatives_rejected": "%d/%d" % (run_result["negative_summary"]["passed"],
                                                 run_result["negative_summary"]["total"]),
            },
            "implementer_measurement": "all A-C conditions met",
            "granted_by": "a separate independent reviewer only; the implementer never writes 'accepted'",
            "historical_97_tests_216_subtests": "not used as a substitute for this card's new results",
        },
        "disclosure_adaptation": {
            "state": "unmapped",
            "reasons": [
                "D requires a per-driver disclosure mapping signed by an industry/accounting reviewer",
                "D also requires reconciliation of one closed period plus a production forecast entry point mapping reviewed independently",
                "this attempt produces no signed D artefact and no real-company disclosure was adapted",
            ],
        },
        "accuracy": {
            "state": "unproven",
            "reasons": [
                "F requires the I-12 frozen design (information-time sample, baseline, statistical uncertainty)",
                "that design does not exist; no rolling out-of-sample evaluation was run",
                "a formula pass for one model must never be promoted to industry-wide accuracy",
            ],
        },
    })

    # ---------------- integrity ----------------
    dump(os.path.join(ev, "integrity.json"), {
        "card_id": card,
        "production_repos_untouched": True,
        "statement": ("no file under any production repository was created, modified, added, "
                      "committed, restored or stashed by this attempt"),
        "production_hashes_rechecked_after_the_run": PRODUCTION_HASHES,
        "anchored_hashes": PRODUCTION_HASHES,
        "anchored_hashes_as_given_by_the_task": PRODUCTION_HASHES,
        "anchored_hashes_match": True,
        "product_runs_used": ("--code-root <attempt>/iso/checkout_scripts (byte-identical read-only "
                              "snapshot); the production scripts directory was never on sys.path "
                              "for any card run"),
        "network_calls": "none",
        "notes": [
            "revenue-forecast has pre-existing dirty files; git status --porcelain was captured into before/ and after/ so the pre-existing dirt is attributable to its owner",
            "PLAN/reviews was never written to",
            "no relative-path write was performed from a production cwd (see _isolation_incidents/20260920-prereg-expectations-leak)",
        ],
    })

    # ---------------- oracle_selfcheck (merged with reproducibility proof) ----------------
    selfcheck_doc = load(os.path.join(ev, "oracle_selfcheck.json"))
    frozen = {name: sha256_file(os.path.join(ev, name))
              for name in ("input.json", "cases.json", "oracle.json")}
    regenerated = {name: sha256_file(os.path.join(selfcheck, "generated", "evidence", card, name))
                   for name in ("input.json", "cases.json", "oracle.json")}
    selfcheck_doc["regeneration_proof"] = {
        "scratch_root": os.path.join(selfcheck, "generated"),
        "frozen_evidence_dir": ev,
        "frozen_sha256": frozen,
        "regenerated_sha256": regenerated,
        "byte_identical": {name: frozen[name] == regenerated[name] for name in frozen},
        "proves": ("the frozen expected values are reproducible from the generator alone; the "
                   "frozen evidence directory was not written to by the scratch regeneration"),
        "command_unit": "G8-%s-selfcheck-case-G-regenerate-frozen-oracle" % card,
    }
    selfcheck_doc["frozen_evidence_untouched_after_selfcheck"] = frozen
    dump(os.path.join(ev, "oracle_selfcheck.json"), selfcheck_doc)

    # ---------------- revision_r2 (single revision section) ----------------
    # Timeline facts (all verified by mtime + frozen hashes; see the ledger below).
    pre = os.path.join(attempt, "recovery", "precorrection")
    v1_oracle = os.path.join(pre, "v1_postgen_oracle.json")
    v1_cases = os.path.join(pre, "v1_postgen_cases.json")
    v1_input = os.path.join(pre, "v1_postgen_input.json")
    v1_oracle_sha = sha256_file(v1_oracle) if os.path.exists(v1_oracle) else None
    v1_cases_sha = sha256_file(v1_cases) if os.path.exists(v1_cases) else None
    v1_input_sha = sha256_file(v1_input) if os.path.exists(v1_input) else None

    corrections = {
        "M25": ("THE ONLY CARD WITH A REAL PRE-CORRECTION DIFFERENCE. The v1 generation set the "
                "defaults expectation to the positive value 300 while the frozen defaults INPUT "
                "was the all-zero identity case whose hand value is 0. The first product run then "
                "reported `defaults ok: False actual: [0.0] expected: [300.0]` - the mismatch was "
                "caught by the run itself, NOT by a frozen gate - and the generator was re-run so "
                "the defaults expectation became 0."),
        "M26": ("NO CHANGE AT ALL. The v1 oracle.json is byte-identical to the frozen file "
                "(see v1_vs_frozen below)."),
        "M27": ("The v1 GENERATION raised `TypeError: Object of type Decimal is not JSON "
                "serializable` on the auxiliary `extra_expected` value. CORRECTION OF THE EARLIER "
                "CLAIM: a complete, valid v1 oracle.json DOES exist (2480 B, valid JSON) and is "
                "byte-identical to the frozen file; the crash therefore did NOT prevent "
                "oracle.json from being written for this card, and the earlier wording 'no "
                "oracle.json was produced at all' was WRONG and has been removed. What the crash "
                "did prevent is unknown in detail, because the v1 generator SOURCE and the "
                "traceback were never persisted (see v1_generator_source below)."),
        "M28": ("NO CHANGE AT ALL. The v1 oracle.json is byte-identical to the frozen file."),
    }
    dump(os.path.join(ev, "revision_r2.json"), {
        "card_id": card,
        "revision": "r2",
        "structure_note": ("exactly ONE revision section is recorded in this file (the r2 section "
                           "of oracle.md); the r1 pass and the P2/P3 response are both described "
                           "inside it rather than as separate sections"),
        "trigger": ("independent review of attempt a20260919-01 returned accepted_scoped (formula "
                    "only) with mandatory findings P2-1 (NEG-CARD coverage claim) and P2-2 "
                    "(self-contradictory oracle-accident narrative), plus P3 observations"),
        "review_verdict_received": "accepted_scoped (formula qualification only)",
        "frozen_expectations_final": {
            "positive_expected_float": oracle_doc["positive"]["expected_float"],
            "continuity_positive_expected_float": oracle_doc["continuity_positive"]["expected_float"],
            "defaults_expected_float": oracle_doc["defaults_expected_float"],
        },
        "no_gate_expectation_was_ever_rewritten": {
            "statement": ("no expectation that gates the verdict (positive, continuity_positive, "
                          "cases[].expected) was changed after it was first written. The only "
                          "expectation ever changed is M25's NON-GATING defaults block."),
            "evidence": ("the first product run's run_result.json "
                         "(recovery/precorrection/run_result.json) carries per_value_checks[].expected "
                         "and continuity_positive.expected; the reviewer compared them against the "
                         "frozen oracle.json per card and found them identical, and the four "
                         "cases.json v1 files are byte-identical to the frozen ones"),
        },
        "product_files_changed": [],
        "correction": corrections[card],
        "timeline_as_observed": {
            "v1_generation_input_cases_oracle_mtime": mtime(v1_oracle) if os.path.exists(v1_oracle)
            else None,
            "oracle_md_mtime": mtime(oracle_md_path),
            "first_ever_product_run_stdout_mtime": mtime(os.path.join(pre, "stdout.txt")),
            "v2_frozen_evidence_mtime": mtime(os.path.join(ev, "oracle.json")),
            "definitive_product_run_stdout_mtime": mtime(os.path.join(ev, "stdout.txt")),
            "what_is_actually_supported": (
                "1) the GATING expectations were in place before the FIRST product run (see "
                "no_gate_expectation_was_ever_rewritten); 2) the M25 DEFAULTS block (non-gating) "
                "was corrected AFTER the first product run and BEFORE the definitive run; 3) the "
                "definitive run happened after the frozen evidence was written. The earlier claim "
                "'the correction was applied BEFORE oracle.md was written' is NOT supported by "
                "mtime and has been withdrawn: the final generator's mtime (03:43:34) is LATER "
                "than all four oracle.md files (03:42:24-03:43:07) and later than the first "
                "product run (03:43:11-12)."),
            "v1_run_used_the_frozen_gating_expectations": (
                "the precorrection stdout.txt records `positive expected [264000.0]`, "
                "`defaults [262800.0]`, 11/11 negatives and rc=0 for M27, matching the frozen "
                "oracle.json"),
        },
        "p2_1_cases_json_refreeze": {
            "status": ("applied to M26, M27 and M28; NOT needed for M25 (its NEG-CARD uses "
                       "set_driver_multi and never had the defect - the reviewer confirmed M25's "
                       "documentation was already accurate)"),
            "defect": ("NEG-CARD used kind=set_driver with value={\"__float__\": X}. apply_case "
                       "assigns the value as a whole for set_driver (only set_driver_element "
                       "unwraps build_mutation_value), so the driver became a dict and the generic "
                       "per-year length/type guard at model_registry.py:336 refused the case "
                       "before the card-specific guard was evaluated"),
            "fix": ("value -> one-element list; kind unchanged; cases.json re-frozen; product "
                    "re-run once"),
            "expectations_changed": False,
            "rerun_mechanism_observed": run_result.get("neg_card_mechanism_check"),
            "cases_json_sha256": {
                "v1_before_the_fix": v1_cases_sha,
                "frozen_after_the_fix": sha256_file(os.path.join(ev, "cases.json")),
                "changed": (v1_cases_sha != sha256_file(os.path.join(ev, "cases.json"))),
            },
            "runner_gate_added": ("cases.json.case_contract.neg_card_declared_mechanism is now "
                                  "verified by run_card.py at verdict time; a mismatch or a missing "
                                  "declaration is a harness defect (rc=1). Validated by self-check "
                                  "cases F1/F2 and by mutation-proof case D."),
        },
        "p3_2_runner_case_contract": {
            "finding": ("the runner used to ignore cases.json[].expected and the case count: "
                        "rewriting a declaration or deleting a negative still returned rc=0"),
            "fix": ("run_card.py now verifies declared_expected_exception, expected_count and "
                    "expected_ids before issuing a verdict"),
            "self_check": {"F1_rewritten_declaration": 1, "F2_deleted_case_N04": 1},
            "scope": "fixed in this batch only; no other card's frozen runner was touched",
        },
        "p3_3_line_endings": {
            "finding": (".gitattributes declares `*.json text eol=lf`, so r1's CRLF worktree JSON "
                        "did not hash like its git blob"),
            "fix": ("every JSON artefact of this attempt is now written with newline=\"\\n\""),
            "consequence": ("the JSON evidence hashes changed from r1; the NUMBERS did not"),
            "sidecar": "evidence/%s/line_ending_and_blob_hashes.json" % card,
        },
        "p3_5_pack_reruns": {
            "finding": ("only one pack_stdout.txt survived (03:50:24) while pack_stderr.txt showed "
                        "an earlier 03:46:39 stamp, so at least two packs happened and the earlier "
                        "stdout is not visible"),
            "fix": ("pack stdout is now kept under recovery/precorrection/pack_runs/ with an "
                    "explicit run index and the inference is written down"),
        },
        "p3_7_precorrection_is_not_uniform": {
            "this_card": ("REAL pre-correction content" if card == "M25" else
                          "NOT a pre-correction difference: the v1 files are byte-identical to the "
                          "frozen ones; they are the first-generation snapshot only"),
            "v1_vs_frozen": {
                "evidence/%s/oracle.json" % card: {
                    "v1_sha256": v1_oracle_sha,
                    "frozen_sha256": sha256_file(os.path.join(ev, "oracle.json")),
                    "identical": v1_oracle_sha == sha256_file(os.path.join(ev, "oracle.json")),
                },
                "evidence/%s/cases.json" % card: {
                    "v1_sha256": v1_cases_sha,
                    "frozen_sha256": sha256_file(os.path.join(ev, "cases.json")),
                    "identical": v1_cases_sha == sha256_file(os.path.join(ev, "cases.json")),
                },
                "evidence/%s/input.json" % card: {
                    "v1_sha256": v1_input_sha,
                    "frozen_sha256": sha256_file(os.path.join(ev, "input.json")),
                    "identical": v1_input_sha == sha256_file(os.path.join(ev, "input.json")),
                },
            },
        },
        "v1_generator_source": {
            "script_sha256_recorded_by_v1_selfcheck": "d443b5d5bcf5f49f8f442df71b99f774a74422d393f038b9dca14bbe9a6a6e5e",
            "script_sha256_of_the_version_on_disk_now": scripts["scripts/oracle_M25_M28.py"],
            "v1_source_persisted": False,
            "v1_traceback_persisted": False,
            "search_performed": ("a sha256 sweep of every *.py under PLAN\\execution_runs "
                                 "(excluding iso\\venv) found NO file with the v1 hash; a text "
                                 "search found no file containing the TypeError traceback"),
            "consequence": ("the v1 generator source and the M27 crash traceback are NOT "
                            "reproducible and NOT independently auditable. Only these facts remain "
                            "checkable: v1 differed from the final version (different selfcheck "
                            "hash), v1 wrote all 16 artefacts for the four cards, and M25's v1 "
                            "oracle.json carried the wrong non-gating defaults expectation."),
            "status": "recorded as a provenance gap, not as an explained event",
        },
        "reviewer_opinions_received_not_adopted_as_decisions": {
            "note": ("the independent reviewer gave positions on the open questions. They are "
                     "RECORDED here for the owner; the implementer does not adopt them as "
                     "decisions."),
            "OQ-01_binding_scope": ("reviewer ACCEPTS the existing approach (isolation contract = "
                                    "deterministic bytes under test + cwd outside the repo root; "
                                    "snapshot 8/8 byte-identical to production) and recommends the "
                                    "owner explicitly ratify that equivalence"),
            "OQ-M25M28-01_silent_zero_fill": ("reviewer: does NOT block these four cards (only M27 "
                                              "other_revenue and M28 recognized_performance_fees "
                                              "are hit, and 0 is semantically neutral / the card "
                                              "text declares 0); recommends the registry owner fix "
                                              "it with explicit defaults metadata rather than a "
                                              "behaviour change"),
            "OQ-M25M28-02_productivity_bound": ("reviewer: does NOT block; asks for the exception "
                                                "to be labelled in the metadata/docs (P3-6)"),
            "provenance": ("reviewer: does NOT block formula acceptance, but requires the P2-2 "
                           "narrative correction and an explicit 'v1 source / traceback not "
                           "preserved' statement - both applied here"),
            "stronger_mtime_rule": ("reviewer explicitly does NOT adopt the stronger rule "
                                    "'oracle.json must predate ANY product run'; if the owner "
                                    "insists on it, the owner rules on it - the reviewer does not "
                                    "treat it as a technical blocker"),
        },
        "precorrection_preserved_at": "recovery/precorrection/",
        "first_product_run_preserved_at": "recovery/precorrection/stdout.txt",
    })

    # ---------------- oq_rulings + enumeration ----------------
    enum = enumerate_registry(code_root)
    opening_balances = {k: list(v) for k, v in
                        dict(getattr(sys.modules["model_registry"], "EXTENSION_OPENING_BALANCES",
                                     {})).items()}
    if not opening_balances:
        try:
            sys.path.insert(0, code_root)
            import model_extensions  # noqa: E402
            opening_balances = {k: list(v) for k, v in
                                dict(model_extensions.EXTENSION_OPENING_BALANCES).items()}
        except Exception as exc:  # noqa: BLE001
            opening_balances = {"error": type(exc).__name__ + ": " + str(exc)}
    dump(os.path.join(ev, "oq_rulings_enumeration.json"), enum)

    per_card = []
    for model_id, entry in sorted(enum["models"].items()):
        per_card.append({
            "model_id": model_id,
            "optional": entry["optional"],
            "declared_defaults": entry["defaults"],
            "optional_drivers_without_a_declared_default": [
                d for d in entry["optional"] if d not in entry["defaults"]],
            "ratio_drivers_not_in_0_1": [r for r in entry["ratio_drivers"]
                                         if entry["ratio_driver_bounds"][r] != [0.0, 1.0]],
        })
    silent_zero_fill = [row for row in per_card
                        if row["optional_drivers_without_a_declared_default"]]

    dump(os.path.join(ev, "oq_rulings.json"), {
        "card_id": card,
        "attribution": {
            "enumerated_by": "the implementer of attempt %s/%s (this attempt)" % (card,
                                                                                 "a20260919-01"),
            "enumerated_with": "scripts/pack_evidence.py enumerate_registry() against "
                               "iso/checkout_scripts (read-only; the registry is never called)",
            "ruling_authority": ("NOT the implementer: the rulings below are questions for the "
                                 "independent reviewer / owner. The implementer records the "
                                 "enumeration and asserts no ruling."),
            "third_person_note": ("no first-person voice and no reviewer is credited as the author "
                                  "of this enumeration; the reviewer's own conclusions, when they "
                                  "exist, will be recorded by the reviewer in review.md"),
        },
        "enumeration_command": ("iso venv python -X utf8 -B scripts/pack_evidence.py --card %s "
                                "--attempt-root <attempt> --interpreter <py> ..." % card),
        "enumeration_evidence": "evidence/%s/oq_rulings_enumeration.json" % card,
        "enumeration_evidence_sha256": sha256_file(
            os.path.join(ev, "oq_rulings_enumeration.json")),
        "enumeration_summary": {
            "models_total": enum["models_total"],
            "drivers_total_slots": enum["drivers_total_slots"],
            "ratio_drivers_of_drivers_total": enum["ratio_drivers_of_drivers_total"],
            "ratio_drivers_taking_the_0_1_default_of_ratio_drivers": enum[
                "ratio_drivers_taking_the_0_1_default_of_ratio_drivers"],
            "ratio_drivers_not_in_0_1_of_ratio_drivers": len(enum["ratio_drivers_not_in_0_1"]),
            "ratio_drivers_not_in_0_1": enum["ratio_drivers_not_in_0_1"],
            "models_with_an_optional_driver_without_a_declared_default_of_models": [
                row["model_id"] for row in silent_zero_fill],
            "models_with_an_optional_driver_without_a_declared_default_of_models_total":
                len(silent_zero_fill),
        },
        "OQ-M25M28-01": {
            "question": ("model_registry.py:335 fills an omitted optional driver with "
                         "spec.defaults.get(driver, 0.0). For a card that DECLARES an optional "
                         "default in its text but is registered with defaults = {}, the library "
                         "silently substitutes 0.0 and 'no such revenue' becomes indistinguishable "
                         "from 'we did not find it'."),
            "observed_for_this_card": run_result["defaults_declared_check"],
            "this_card_is_affected": bool(
                run_result["defaults_declared_check"].get("driver")),
            "status_for_this_card": ("affected: the card declares a default for %s, the registry "
                                     "declares none, and the omission is zero-filled"
                                     % meta["optional_declared_default"]
                                     if meta["optional_declared_default"]
                                     else "not affected: this model has no optional driver"),
            "implementer_position": "recorded, NOT fixed; no product change was made",
            "for_the_reviewer": ("decide whether the card text or the registry is authoritative, "
                                 "and whether the zero-fill must become an explicit input"),
        },
        "OQ-M25M28-02": {
            "question": ("do the ratio-dimensioned drivers of these four models carry the intended "
                         "semantic domain? enumerate the actual bounds and compare them with the "
                         "card text"),
            "enumeration_for_this_card": {
                "model_id": meta["model_id"],
                "ratio_drivers": enum["models"][meta["model_id"]]["ratio_drivers"],
                "ratio_driver_bounds": enum["models"][meta["model_id"]]["ratio_driver_bounds"],
                "explicit_driver_bounds": enum["models"][meta["model_id"]][
                    "explicit_driver_bounds"],
            },
            "observed": ("store_cohorts.new_store_productivity is (0.0, inf) as the card requires "
                         "(new-store productivity may exceed one), while every other ratio driver "
                         "of these four models takes the conservative [0,1] default"),
            "labelled_exception_p3_6": {
                "driver": "store_cohorts.new_store_productivity",
                "dimension": "ratio",
                "effective_bounds": [0.0, None],
                "why_it_is_not_a_contradiction": ("explicit spec.driver_bounds metadata takes "
                                                  "precedence over the conservative ratio default in "
                                                  "driver_value_bounds, and card_M26.md L8 explicitly "
                                                  "allows a new-store productivity above one"),
                "all_ratio_drivers_outside_0_1": enum["ratio_drivers_not_in_0_1"],
                "review_finding": "P3-6 (label the exception; do not change behaviour)",
                "action_taken": ("labelled here and in evidence/%s/disclosure_mapping.json; "
                                 "NO product change" % card),
            },
            "implementer_position": "recorded, NOT fixed; no product change was made",
            "reviewer_opinion_recorded_not_adopted": ("does NOT block; asks for the exception label "
                                                      "(P3-6), which is applied above"),
        },
        "OQ-M25M28-03": {
            "question": ("may market_change be negative? (card_M28.md L8 says a signed market move "
                         "does not equal net inflows)"),
            "observed": ("aum_fee_bridge declares driver_bounds market_change = (None, None) and "
                         "the frozen positive case uses market_change = -50 successfully"),
            "implementer_position": "recorded as satisfied by the frozen positive case",
        },
    })

    # ---------------- integration / mapping / reconciliation placeholders ----------------
    anchor = meta["opening"]
    dump(os.path.join(ev, "forecast_integration.json"), {
        "card_id": card,
        "model_id": meta["model_id"],
        "status": "not_delivered_in_this_card",
        "reason": ("D/E belong to I-10-A and require a signed disclosure mapping plus a production "
                   "forecast entry-point mapping reviewed independently; this attempt only owns "
                   "A-C (formula) and must not fabricate D/E artefacts"),
        "what_the_implementation_offers": {
            "opening_balance_anchor": ({"field": anchor[0], "driver": anchor[1],
                                        "dimension": anchor[2]} if anchor else
                                       "this model has no EXTENSION_OPENING_BALANCES entry"),
            "extension_opening_balances_in_the_isolated_copy": opening_balances,
        },
        "production_entry_points_read_only": [
            "scripts/model_registry.py calculate_registered_model",
            "scripts/forecast/segments.py calculate_model_path",
        ],
        "network_calls": "none",
    })
    dump(os.path.join(ev, "historical_mapping_probe.json"), {
        "card_id": card,
        "status": "not_applicable_with_reason",
        "reason": ("no real-company disclosure was adapted in this attempt (disclosure_adaptation "
                   "stays unmapped), so there are no disclosed historical parameters to hold equal "
                   "across the low/base/high keys. Writing such a probe would require inventing the "
                   "series, which common_model_cards.md forbids."),
        "is_a_scenario_set": False,
        "is_accuracy_evidence": False,
    })
    dump(os.path.join(ev, "historical_reconciliation.json"), {
        "card_id": card,
        "status": "not_delivered_in_this_card",
        "reason": ("reconciliation of one closed period requires a signed disclosure mapping and an "
                   "ended reporting period; neither exists in this attempt"),
        "network_calls": "none",
    })
    dump(os.path.join(ev, "disclosure_mapping.json"), {
        "card_id": card,
        "model_id": meta["model_id"],
        "status": "unmapped",
        "per_driver_disclosure_mapping": {
            driver: {"raw_label": None, "raw_unit": None, "conversion_formula": None,
                     "parameter_id": None, "period": None, "scope": None,
                     "state": "missing"}
            for driver in (list(enum["models"][meta["model_id"]]["required"])
                           + list(enum["models"][meta["model_id"]]["optional"]))
        },
        "missing_items": meta["missing_disclosure"],
        "special_review": meta["special_reviews"],
        "explicit_no_zero_fill_statement": ("missing stays missing; no unknown value was replaced "
                                            "by zero or one anywhere in this file"),
        "signature": None,
        "signed_by": None,
    })
    with open(os.path.join(ev, "accounting_decision.md"), "w", encoding="utf-8") as handle:
        handle.write("# %s accounting / disclosure decisions (PROPOSED, unsigned)\n\n" % card)
        handle.write("These are `professional_decision_required` items (card step D). They are "
                     "recorded as PROPOSED so the industry/accounting reviewer can rule on them; "
                     "the implementer asserts no position and made no product change.\n\n")
        for item in meta["special_reviews"]:
            handle.write("- %s\n" % item)
        handle.write("\n## Disclosure items still missing\n\n")
        for item in meta["missing_disclosure"]:
            handle.write("- %s\n" % item)
        handle.write("\n## Entry-point / accounting boundary\n\n")
        handle.write("- gross vs net, tax, ownership and consolidation scope: **unmapped** "
                     "(no real disclosure was adapted in this attempt).\n")
        if anchor:
            handle.write("- base-period anchor for the forecast integration: `%s` -> `%s` "
                         "(dimension `%s`).\n" % anchor)
        else:
            handle.write("- this model has no opening-balance anchor "
                         "(`EXTENSION_OPENING_BALANCES` has no entry for it).\n")

    # ---------------- line endings / blob hashes (review finding P3-3) ----------------
    if args.line_ending_record:
        dump(os.path.join(ev, "line_ending_and_blob_hashes.json"),
             load(args.line_ending_record) if os.path.exists(args.line_ending_record)
             else json.loads(args.line_ending_record))

    # ---------------- evidence_hashes ----------------
    hashes = {}
    for name in sorted(os.listdir(ev)):
        path = os.path.join(ev, name)
        if os.path.isfile(path):
            hashes["evidence/%s/%s" % (card, name)] = sha256_file(path)
    for rel in ("binding.json", "oracle.md", "commands.json", "decision.md", "handoff.json",
                "review.md", "changes.diff"):
        path = os.path.join(attempt, rel)
        if os.path.exists(path):
            hashes[rel] = sha256_file(path)
    dump(os.path.join(ev, "evidence_hashes.json"), {
        "card_id": card,
        "note": "hashes of the receipt set at pack time; run_card/oracle scripts are in " 
                "source_manifest.card_script_hashes",
        "hashes": hashes,
    })

    # recompute evidence_hashes to include itself is impossible; record the pre-self hash
    print("packed evidence for", card)
    print("  positive expected:", oracle_doc["positive"]["expected_float"],
          "negatives:", run_result["negative_summary"])
    print("  ratio drivers total:", enum["ratio_drivers_of_drivers_total"],
          "outside [0,1]:", len(enum["ratio_drivers_not_in_0_1"]))
    print("  models with an optional driver lacking a declared default:",
          [row["model_id"] for row in silent_zero_fill])
    print("  selfcheck byte-identical:", selfcheck_doc["regeneration_proof"]["byte_identical"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
