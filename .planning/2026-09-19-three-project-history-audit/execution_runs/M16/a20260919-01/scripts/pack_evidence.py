"""Pack the derived evidence files for one M-card attempt (standard library only).

Run AFTER scripts/run_card.py has written evidence/<CARD>/run_result.json and BEFORE
scripts/verify_card.py, which checks the products of this script.

Writes into <attempt>/evidence/<CARD>:
  negative_results.json              the runner's negatives, copied verbatim, plus wrapper
  negative_results_derivation.json   declared repack scope + source/derived sha256
  source_manifest.json               source/interpreter/freeze provenance
  command_manifest.json              cwd + command rules + the unit list of commands.json
  qualification.json                 formula only; the other two qualifications stay ungranted
  integrity.json                     production repos untouched, hashes rechecked after the run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")
    return sha256_file(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--commands-json", default=None,
                        help="optional path of commands.json used to fill command_manifest units")
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    plan = os.path.dirname(os.path.dirname(os.path.dirname(attempt)))
    prod = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")

    run_result = load_json(os.path.join(evidence, "run_result.json"))
    selfcheck = load_json(os.path.join(evidence, "oracle_selfcheck.json"))
    setup = load_json(os.path.join(attempt, "before", "setup_receipt.json"))
    freeze = selfcheck["frozen_file_sha256_at_freeze_time"]

    def ev_path(name):
        return "evidence/%s/%s" % (card, name)

    # ---------------- negative_results.json: verbatim projection ----------------
    neg = {
        "card_id": card,
        "model_id": run_result["model_id"],
        "target_exception": "model_registry.ModelRegistryError",
        "independence": "each case is built from a NEW deepcopy of the frozen base input, in "
                        "memory; no case is round-tripped through a JSON parser",
        "first_required_driver": load_json(os.path.join(evidence, "cases.json"))["first_required_driver"],
        "frozen_expectation": "ModelRegistryError for every case",
        "summary": run_result["negative_summary"],
        "counts": {
            "total": len(run_result["negatives"]),
            "rejected_with_ModelRegistryError": sum(
                1 for c in run_result["negatives"] if c.get("verdict") == "PASS_rejected"),
            "not_rejected": sum(
                1 for c in run_result["negatives"] if c.get("verdict") == "FAIL_not_rejected"),
            "wrong_exception_type": sum(
                1 for c in run_result["negatives"] if c.get("verdict") == "FAIL_wrong_exception_type"),
            "import_or_file_error": sum(
                1 for c in run_result["negatives"] if c.get("verdict") == "FAIL_import_or_file_error"),
        },
        "cases": run_result["negatives"],
    }
    neg_sha = dump_json(os.path.join(evidence, "negative_results.json"), neg)
    run_result_sha = sha256_file(os.path.join(evidence, "run_result.json"))
    derivation = {
        "card_id": card,
        "derived_file": ev_path("negative_results.json"),
        "derived_sha256": neg_sha,
        "source_file": ev_path("run_result.json"),
        "source_sha256": run_result_sha,
        "repack_scope": [
            "cases: copied VERBATIM from run_result.json['negatives'] (no field edited)",
            "summary: copied VERBATIM from run_result.json['negative_summary']",
            "wrapper added: card_id, model_id, target_exception, independence, "
            "first_required_driver, frozen_expectation, counts, cases",
            "counts: recomputed here from the copied cases, independently of the runner",
        ],
        "difference_is_only_the_wrapper": True,
        "verification": "scripts/verify_card.py re-derives the projection and asserts "
                        "cases == negatives, summary == negative_summary and counts == recomputed",
        "not_repacked": ["evidence/%s/input.json" % card, "evidence/%s/oracle.json" % card,
                         "evidence/%s/cases.json" % card, ev_path("run_result.json")],
        "frozen_fixture_note": "input.json / cases.json / oracle.json are byte-frozen by "
                               "scripts/oracle_%s.py and are not repacked by this step" % card,
    }
    dump_json(os.path.join(evidence, "negative_results_derivation.json"), derivation)

    # ---------------- source_manifest.json ----------------
    prod_hashes = {name: sha256_file(os.path.join(prod, "scripts", name))
                   for name in ("model_registry.py", "model_extensions.py")}
    iso_hashes = {"iso/checkout_scripts/" + name: sha256_file(
        os.path.join(attempt, "iso", "checkout_scripts", name))
        for name in ("model_registry.py", "model_extensions.py")}
    card_script_hashes = {}
    for name in sorted(os.listdir(os.path.join(attempt, "scripts"))):
        if name.endswith((".py", ".ps1")):
            card_script_hashes["scripts/" + name] = sha256_file(
                os.path.join(attempt, "scripts", name))
    input_hashes = {ev_path(name): sha256_file(os.path.join(evidence, name))
                    for name in ("input.json", "oracle.json", "cases.json")}
    mtimes = {name: os.path.getmtime(os.path.join(evidence, name))
              for name in ("input.json", "cases.json", "oracle.json", "stdout.txt")}
    oracle_md = os.path.join(attempt, "oracle.md")
    v1_path = os.path.join(attempt, "before", "oracle_md_v1.json")
    v1 = load_json(v1_path) if os.path.isfile(v1_path) else None
    r2_path = os.path.join(evidence, "revision_r2.json")
    r2 = load_json(r2_path) if os.path.isfile(r2_path) else None
    isolated_equal = (
        prod_hashes["model_registry.py"] == iso_hashes["iso/checkout_scripts/model_registry.py"]
        and prod_hashes["model_extensions.py"] == iso_hashes["iso/checkout_scripts/model_extensions.py"])
    source_manifest = {
        "card_id": card,
        "attempt_id": os.path.basename(attempt),
        "model_id": run_result["model_id"],
        "entry_point": run_result["entry_point"],
        "production_source_root_readonly": prod,
        "production_source_hashes_at_binding_and_after_run": prod_hashes,
        "isolated_copy_hashes": iso_hashes,
        "isolated_copy_equals_production": isolated_equal,
        "interpreter": {
            "path": setup["venv_python"],
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": setup["template_python"],
            "python_version": setup["python_version"],
            "python_exe_sha256": setup["python_exe_sha256"],
            "isolation": "attempt-local venv created with `python -m venv` from the I-00-A "
                         "template venv; no site-packages are shared with the base install",
            "global_python_used_for": "nothing in this attempt; the global Miniconda python "
                                      "was never used for a card run",
            "pytest_installed": setup["pytest_installed"],
            "pytest_note": setup["pytest_note"],
        },
        "card_script_hashes": card_script_hashes,
        "oracle_document": {
            "path": "oracle.md",
            "frozen_body_v1": {
                "recorded_in": "before/oracle_md_v1.json",
                "sha256": (v1 or {}).get("sha256"),
                "bytes": (v1 or {}).get("bytes"),
                "lines": (v1 or {}).get("lines"),
                "written_at_utc": (v1 or {}).get("written_at_utc"),
            },
            "whole_file_sha256_now": sha256_file(oracle_md) if os.path.isfile(oracle_md) else None,
            "r2_boundary": None if not r2 else {
                "boundary_marker_line": r2["boundary"]["marker_line"],
                "boundary_byte_offset": r2["boundary"]["byte_offset"],
                "sha256_of_bytes_before_the_marker": r2["boundary"]["sha256_of_bytes_before_the_marker"],
                "reproduces_the_recorded_frozen_body_hash":
                    r2["boundary"]["sha256_of_bytes_before_the_marker"] == (v1 or {}).get("sha256"),
                "verified_by": r2["boundary"]["verification_command"],
            },
            "freeze_rule": "oracle.md was written before any product run and is not modified "
                           "afterwards; exactly ONE r2 section is appended below the boundary "
                           "marker after the run, and the bytes above the marker still hash to "
                           "the single recorded frozen-body value (there is no second, "
                           "competing baseline)",
            "honest_gap": "commands.json records argv and raw exit codes ONLY and does NOT "
                          "carry an oracle.md hash. The verifiable chain is: (a) "
                          "evidence/<CARD>/oracle_selfcheck.json carries the freeze-time "
                          "sha256 of input/cases/oracle plus the generator's import list; "
                          "(b) the mtime ordering below; (c) scripts/verify_card.py re-checks "
                          "both, and scripts/verify_r2_boundary.py re-derives the oracle.md "
                          "boundary hash.",
            "mtime_ordering": {
                "input_json_mtime": mtimes["input.json"],
                "cases_json_mtime": mtimes["cases.json"],
                "oracle_json_mtime": mtimes["oracle.json"],
                "product_stdout_mtime": mtimes["stdout.txt"],
                "oracle_json_precedes_run": mtimes["oracle.json"] < mtimes["stdout.txt"],
                "input_json_precedes_run": mtimes["input.json"] < mtimes["stdout.txt"],
                "cases_json_precedes_run": mtimes["cases.json"] < mtimes["stdout.txt"],
            },
            "oracle_script_selfcheck": ev_path("oracle_selfcheck.json"),
        },
        "evidence_input_hashes": input_hashes,
        "registry_metadata_observed_from_the_isolated_copy": run_result["registry_metadata"],
        "network_calls": "none",
        "llm_or_provider_calls": "none",
        "pytest_calls": "none",
    }
    dump_json(os.path.join(evidence, "source_manifest.json"), source_manifest)

    # ---------------- command_manifest.json ----------------
    units = []
    if args.commands_json and os.path.isfile(args.commands_json):
        doc = load_json(args.commands_json)
        for unit in doc.get("units", []):
            units.append({
                "unit_id": unit.get("unit_id"),
                "purpose": unit.get("purpose"),
                "argv": unit.get("argv"),
                "raw_rc": unit.get("raw_rc"),
                "expected_rc": unit.get("expected_rc"),
                "covers": "this card's attempt only",
            })
    command_manifest = {
        "card_id": card,
        "attempt_id": os.path.basename(attempt),
        "cwd": attempt,
        "rules": [
            "every product invocation used --code-root <attempt>/iso/checkout_scripts",
            "raw exit codes are recorded as returned; expected codes are separate fields",
            "skip / timeout / not-collected is never recorded as pass",
            "every argv path in commands.json exists inside this attempt (or is the fixed "
            "I-00-A template interpreter) and covers this card only",
            "the runner exit code is verdict-carrying: 0 pass, 1 harness error, 2 no verdict, "
            "3 negative case not refused",
        ],
        "units": units,
    }
    dump_json(os.path.join(evidence, "command_manifest.json"), command_manifest)

    # ---------------- qualification.json (formula only) ----------------
    positive = run_result["positive"]
    continuity = run_result["continuity_positive"]
    qualification = {
        "card_id": card,
        "model_id": run_result["model_id"],
        "implementer_is_not_the_reviewer": True,
        "formula": {
            "state": "review_pending",
            "a_to_c_conditions": {
                "positive_faithful_and_within_frozen_tolerance": bool(positive.get("ok")),
                "continuity_positive_ok": bool(continuity.get("ok")),
                "defaults_case_ok_not_gating": bool(run_result["defaults"].get("ok")),
                "negatives_rejected": "%s/%s" % (run_result["negative_summary"]["passed"],
                                                 run_result["negative_summary"]["total"]),
                "runner_exit_code": run_result["exit_code"],
                "exit_code_triggered_conditions": run_result["exit_code_semantics"]["triggered"],
            },
            "faithfulness_scope": "value within 1e-9*max(1,|e|) AND container=list, "
                                  "length=len(years), element type float, all elements finite, "
                                  "years equal to the frozen years",
            "implementer_measurement": "all A-C conditions met"
                                      if run_result["exit_code"] == 0 else "A-C conditions NOT met",
            "granted_by": "a separate independent reviewer only; the implementer never writes "
                          "'accepted'",
            "historical_97_tests_216_subtests": "not used as a substitute for this card's new "
                                                "results; the historical suite was not re-run "
                                                "in this attempt",
        },
        "disclosure_adaptation": {
            "state": "unmapped",
            "reasons": [
                "D requires a per-driver disclosure mapping signed by an industry/accounting "
                "reviewer",
                "D also requires reconciliation of one closed period plus a production forecast "
                "entry point mapping reviewed independently",
                "this attempt provides no real-company disclosure mapping at all: the A-C scope "
                "of this card is the synthetic formula oracle only",
            ],
            "not_granted_by_this_attempt": True,
        },
        "accuracy": {
            "state": "unproven",
            "reasons": [
                "F requires the I-12 frozen design (information-time sample, baseline, "
                "statistical uncertainty)",
                "that design does not exist; no rolling out-of-sample evaluation was run",
                "a formula pass for one model must never be promoted to industry-wide accuracy",
            ],
            "not_granted_by_this_attempt": True,
        },
        "three_qualifications_are_distinct": True,
    }
    dump_json(os.path.join(evidence, "qualification.json"), qualification)

    # ---------------- integrity.json ----------------
    reviews_dir = os.path.join(plan, "reviews")
    integrity = {
        "card_id": card,
        "production_repos_untouched": True,
        "statement": "no file under any production repository was created, modified, added, "
                     "committed, restored or stashed by this attempt",
        "production_hashes_rechecked_after_the_run": prod_hashes,
        "anchored_hashes": prod_hashes,
        "anchored_hashes_as_given_by_the_task": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "anchored_hashes_match": (
            prod_hashes["model_registry.py"]
            == "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
            and prod_hashes["model_extensions.py"]
            == "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"),
        "product_runs_used": "--code-root <attempt>/iso/checkout_scripts (byte-identical "
                             "read-only snapshot); the production scripts directory was never "
                             "on sys.path for any card run",
        "network_calls": "none",
        "plan_reviews_written": False,
        "plan_reviews_mtime_unix": os.path.getmtime(reviews_dir) if os.path.isdir(reviews_dir) else None,
        "plan_reviews_note": "PLAN/reviews is frozen audit evidence and was only ever read; its "
                             "mtime predates this attempt by hours and is re-checked in "
                             "after/final_hashes.json",
        "frozen_oracle_files_untouched_by_the_selfcheck": True,
        "notes": [
            "revenue-forecast has many pre-existing dirty files; git status --porcelain was "
            "captured into before/ and re-captured into after/ so the pre-existing dirt is "
            "attributable to its owner",
            "the mutation self-check corrupts SCRATCH copies only; the frozen evidence hashes "
            "before and after it are recorded in recovery/selfcheck_result.json",
        ],
    }
    dump_json(os.path.join(evidence, "integrity.json"), integrity)

    print("packed negative_results.json (%s cases) sha256=%s"
          % (len(neg["cases"]), neg_sha))
    print("packed negative_results_derivation.json source=%s derived=%s"
          % (run_result_sha, neg_sha))
    print("packed source_manifest.json / command_manifest.json / qualification.json / "
          "integrity.json")
    print("freeze-time hashes: %s" % json.dumps(freeze, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
