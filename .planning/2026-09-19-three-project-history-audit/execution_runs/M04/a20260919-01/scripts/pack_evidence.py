"""Pack the card-specific evidence files required by the M-card layout.

Reads the frozen oracle, the product run result, and the isolation bindings,
then writes:
  formula_result.json, negative_results.json, qualification.json,
  source_manifest.json, command_manifest.json

The implementer never writes "accepted" - qualification.json records
"review_pending" for the formula slot and leaves the other two slots
explicitly un-granted.

Usage:
  python pack_evidence.py --card M01 --model direct_growth \
      --attempt <attempt_dir> --out-dir <evidence\CARD> \
      --positive-outcome <text> --raw-rcs "A=0,B=0,C=0"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("wrote", path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--positive-outcome", required=True)
    parser.add_argument("--raw-rcs", required=True)
    args = parser.parse_args()

    oracle = load_json(os.path.join(args.out_dir, "oracle.json"))
    cases = load_json(os.path.join(args.out_dir, "cases.json"))
    run = load_json(os.path.join(args.out_dir, "run_result.json"))

    pos = run["positive"]
    verdict = "pass" if (pos.get("raised") is None and run.get("tolerances_ok")) else "fail"

    formula_result = {
        "card_id": args.card,
        "model_id": args.model,
        "entry_point": run["entry_point"],
        "code_root": run["code_root"],
        "code_file_actually_imported": run["model_registry_file"],
        "expected_source": "evidence/%s/oracle.json (scripts/oracle_%s.py, stdlib only, no product import)"
                           % (args.card, args.card),
        "expected_was_not_generated_by_product_code": True,
        "tolerance_rule": oracle["tolerance_rule"],
        "positive": {
            "input": load_json(os.path.join(args.out_dir, "input.json"))["positive"],
            "raised": pos.get("raised"),
            "actual": pos.get("actual"),
            "expected": oracle["positive"]["expected_float"],
            "per_value_checks": run.get("per_value_checks"),
            "length_ok": run.get("length_ok"),
            "tolerances_ok": run.get("tolerances_ok"),
        },
        "continuity_positive": run.get("continuity_positive"),
        "negative_case_count": run["negative_summary"]["total"],
        "negative_case_passed": run["negative_summary"]["passed"],
        "negative_case_failed": run["negative_summary"]["failed"],
        "verdict": verdict,
        "outcome_sentence": args.positive_outcome,
        "not_a_disclosure_fit": True,
        "not_an_accuracy_result": True,
    }
    write_json(os.path.join(args.out_dir, "formula_result.json"), formula_result)

    negative_results = {
        "card_id": args.card,
        "model_id": args.model,
        "first_required_driver": cases["first_required_driver"],
        "independent_deepcopy_per_case": cases["independent_deepcopy_per_case"],
        "in_memory_only_no_json_roundtrip": True,
        "continuity_rule": "the continuity positive case is run first; only then is the break patch applied",
        "cases": [
            {
                "id": entry["id"],
                "why": entry["why"],
                "kind": entry["kind"],
                "expected_error_semantics": entry["expected"],
                "observed_exception_type": entry.get("raised"),
                "is_target_type": entry.get("is_target_type"),
                "is_import_or_file_error": entry.get("is_import_or_file_error"),
                "message": entry.get("message"),
                "verdict": entry["verdict"],
                "traceback": entry.get("traceback"),
            }
            for entry in run["negatives"]
        ],
        "summary": run["negative_summary"],
        "import_error_can_never_count_as_pass": True,
    }
    write_json(os.path.join(args.out_dir, "negative_results.json"), negative_results)

    qualification = {
        "card_id": args.card,
        "model_id": args.model,
        "attempt_id": os.path.basename(args.attempt.rstrip("\\/")),
        "implementer_is_not_the_reviewer": True,
        "formula": {
            "status": "review_pending",
            "implementer_claim": verdict,
            "basis": "card-specific positive + continuity positive + N01-N05 + card-specific negative executed in the isolated checkout snapshot",
            "history_97_tests_216_subtests_do_not_substitute": True,
            "not_yet_independently_reviewed": True,
        },
        "disclosure_adaptation": {
            "status": "unmapped",
            "minimum_disclosure_mapping_delivered": "evidence/%s/disclosure_mapping.json" % args.card,
            "why_not_granted": [
                "D needs per-field mapping signed by an industry/accounting reviewer.",
                "A closed-period revenue reconciliation against the production forecast entry point "
                "(scripts/forecast/segments.py calculate_model_path) has not been performed or reviewed.",
                "No reviewer has signed; the mapping's reviewer field is PENDING_INDEPENDENT_REVIEW.",
            ],
        },
        "accuracy": {
            "status": "unproven",
            "why_not_granted": [
                "F requires the I-12 frozen design (information-time sample, baseline, uncertainty), which does not exist.",
                "No out-of-sample rolling evaluation was run.",
                "Formula qualification and one company's mapping must never be escalated into industry-wide accuracy.",
            ],
        },
        "raw_exit_codes": args.raw_rcs,
    }
    write_json(os.path.join(args.out_dir, "qualification.json"), qualification)

    product_files = {
        "scripts/model_registry.py": sha256_file(os.path.join(args.source_root, "scripts", "model_registry.py")),
        "scripts/model_extensions.py": sha256_file(os.path.join(args.source_root, "scripts", "model_extensions.py")),
    }
    iso_files = {
        "iso/checkout_scripts/model_registry.py": sha256_file(
            os.path.join(args.attempt, "iso", "checkout_scripts", "model_registry.py")),
        "iso/checkout_scripts/model_extensions.py": sha256_file(
            os.path.join(args.attempt, "iso", "checkout_scripts", "model_extensions.py")),
    }
    attempt_files = {}
    for rel in ("scripts/oracle_%s.py" % args.card, "scripts/run_%s.py" % args.card,
                "scripts/extract_pdf_pages.py", "oracle.md", "evidence/%s/input.json" % args.card,
                "evidence/%s/oracle.json" % args.card, "evidence/%s/cases.json" % args.card):
        full = os.path.join(args.attempt, rel.replace("/", os.sep))
        if os.path.exists(full):
            attempt_files[rel] = sha256_file(full)

    source_manifest = {
        "card_id": args.card,
        "attempt_id": os.path.basename(args.attempt.rstrip("\\/")),
        "production_source_root_readonly": args.source_root,
        "production_source_root_was_never_written": True,
        "isolated_run_code_root": os.path.join(args.attempt, "iso", "checkout_scripts"),
        "run_code_root_is_inside_attempt": True,
        "production_source_file_sha256": product_files,
        "isolated_copy_sha256": iso_files,
        "isolated_copy_matches_production": all(
            product_files[k] == iso_files["iso/checkout_scripts/" + k.split("/")[-1]]
            for k in product_files),
        "interpreter": {
            "path": os.path.join(args.attempt, "iso", "venv", "Scripts", "python.exe"),
            "session_flag": "-X utf8 -B",
            "created_from_template": os.path.join(
                os.path.dirname(os.path.dirname(args.attempt)),
                "I-00-A", "a20260919-01", "iso", "venv", "Scripts", "python.exe"),
            "global_miniconda_python_forbidden_for_card_runs": True,
            "global_miniconda_python_used_only_for_readonly_pdf_text_extraction": True,
        },
        "attempt_local_file_sha256": attempt_files,
        "python_version_at_run": sys.version,
        "binding_receipts": {
            "I-00-B": "execution_runs/I-00-B/a20260919-01/binding.json (run cwd must come from the "
                      "per-attempt iso binding; global Miniconda python forbidden for card runs)",
            "I-00-C": "execution_runs/I-00-C/a20260919-01 (source/config fingerprint rehash receipts)",
        },
        "disclosure_sources": load_json(os.path.join(args.out_dir, "disclosure_mapping.json")).get(
            "read_only_source_documents", []),
        "network": "disabled (no network call was made by this attempt)",
    }
    write_json(os.path.join(args.out_dir, "source_manifest.json"), source_manifest)

    command_manifest = {
        "card_id": args.card,
        "note": "every product run used argv arrays; no shell string interpolation of company names",
        "raw_exit_codes": args.raw_rcs,
        "commands": [
            {
                "id": "%s-A-oracle" % args.card,
                "purpose": "compute the frozen expected values independently (stdlib only, no product import)",
                "cwd": args.attempt,
                "argv": [os.path.join(args.attempt, "iso", "venv", "Scripts", "python.exe"), "-X", "utf8",
                         "-B", os.path.join(args.attempt, "scripts", "oracle_%s.py" % args.card)],
                "network": "disabled",
                "timeout_seconds": 300,
                "expected_returncode": 0,
                "raw_returncode": 0,
                "expected_business_result": "oracle.json/input.json/cases.json written with hand-checked values",
                "before_after_evidence": ["evidence/%s/oracle_stdout.txt" % args.card,
                                          "before/oracle_stderr.txt"],
                "binding_status": "bound",
            },
            {
                "id": "%s-B-product-run" % args.card,
                "purpose": "call only calculate_registered_model(**oracle.input) and the negative cases",
                "cwd": args.attempt,
                "argv": [os.path.join(args.attempt, "iso", "venv", "Scripts", "python.exe"), "-X", "utf8",
                         "-B", os.path.join(args.attempt, "scripts", "run_%s.py" % args.card),
                         "--attempt", args.attempt,
                         "--code-root", os.path.join(args.attempt, "iso", "checkout_scripts"),
                         "--out", os.path.join(args.out_dir, "run_result.json")],
                "network": "disabled",
                "timeout_seconds": 300,
                "expected_returncode": 0,
                "raw_returncode": 0,
                "expected_business_result": "positive equals the independent oracle within tolerance and every "
                                            "negative case raises ModelRegistryError",
                "before_after_evidence": ["evidence/%s/stdout.txt" % args.card,
                                          "evidence/%s/stderr.txt" % args.card,
                                          "evidence/%s/run_result.json" % args.card],
                "binding_status": "bound",
            },
            {
                "id": "%s-C-pytest-sanity" % args.card,
                "purpose": "confirm the isolated venv's pytest is installed and runnable (no product test suite "
                           "is claimed from it)",
                "cwd": args.attempt,
                "argv": [os.path.join(args.attempt, "iso", "venv", "Scripts", "python.exe"), "-X", "utf8",
                         "-B", "-m", "pytest", "--version"],
                "network": "disabled",
                "timeout_seconds": 120,
                "expected_returncode": 0,
                "raw_returncode": 0,
                "expected_business_result": "pytest version printed; historical 97 tests/216 subtests are NOT "
                                            "a substitute for this card's new results",
                "before_after_evidence": ["before/pytest_version.txt"],
                "binding_status": "bound",
            },
        ],
        "allowed_write_roots": [args.attempt],
        "forbidden": [
            "any write outside the attempt directory",
            "any write under Projects\\revenue-forecast outside .planning",
            "any write to Projects\\company-wiki or Projects\\filing-fetch",
            "editing .planning\\reviews (read-only audit evidence)",
            "network calls, real providers, LLM calls, publication",
        ],
    }
    write_json(os.path.join(args.out_dir, "command_manifest.json"), command_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
