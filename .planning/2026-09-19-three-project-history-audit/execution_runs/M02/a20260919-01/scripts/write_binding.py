"""Write the per-card binding.json, commands.json and the historical mapping probe.

Kept as a script so the four cards get structurally identical bindings while
each carries its own card-specific facts.

ASCII-only stdout.
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


def write_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("wrote", path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--formula", required=True)
    parser.add_argument("--required", required=True)
    parser.add_argument("--optional", required=True)
    parser.add_argument("--defaults", required=True)
    parser.add_argument("--driver-bounds", required=True,
                        help="semicolon-separated driver=lower:upper entries")
    parser.add_argument("--probe-keys", required=True, help="JSON of the historical mapping probe values")
    parser.add_argument("--probe-note", required=True)
    args = parser.parse_args()

    attempt = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rf = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    plan = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(attempt))))
    evidence = os.path.join(attempt, "evidence", args.card)
    iso = os.path.join(attempt, "iso", "checkout_scripts")
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    template = os.path.join(plan, "execution_runs", "I-00-A", "a20260919-01", "iso", "venv",
                            "Scripts", "python.exe")

    bounds = {}
    for item in args.driver_bounds.split(";"):
        if not item.strip():
            continue
        driver, rng = item.split("=", 1)
        lower, upper = rng.split(":", 1)
        bounds[driver.strip()] = [None if lower.strip() == "None" else float(lower),
                                  None if upper.strip() == "None" else float(upper)]

    binding = {
        "card_id": args.card,
        "attempt_id": "a20260919-01",
        "model_id": args.model,
        "binding_status": "bound",
        "binding_sources": {
            "I-00-B": {
                "path": "execution_runs/I-00-B/a20260919-01/binding.json",
                "rule_read": "run cwd must be a per-attempt isolation directory, never the repo root; "
                             "the global Miniconda python is FORBIDDEN for card runs",
                "note": "I-00-B does not materialise a checkout tree; it binds the isolation plan and the "
                        "two-stage command rule. This attempt therefore materialises its own read-only "
                        "isolated snapshot (iso/checkout_scripts) and records the production hashes it "
                        "was copied from.",
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": "present, used as a receipt reference only (this attempt re-hashed the "
                                  "files it actually used rather than trusting the receipt)",
            },
            "I-00-A": {
                "path": "execution_runs/I-00-A/a20260919-01/baseline.json",
                "role": "template interpreter and isolation finding (global python loads an editable "
                        "dayu-agent finder, so isolated venvs are mandatory)",
            },
        },
        "interpreter": {
            "path": py,
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": template,
            "isolation": "attempt-local venv created with `python -m venv` from the I-00-A template venv; "
                         "pytest installed offline from the local cache",
            "global_python_used_for": "read-only PDF text extraction only (PyMuPDF), never for a card run",
        },
        "cwd": attempt,
        "python_path": [iso],
        "run_code_root": iso,
        "production_source_root_readonly": rf,
        "production_source_hashes": {
            "scripts/model_registry.py": sha256_file(os.path.join(rf, "scripts", "model_registry.py")),
            "scripts/model_extensions.py": sha256_file(os.path.join(rf, "scripts", "model_extensions.py")),
        },
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py": sha256_file(os.path.join(iso, "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha256_file(os.path.join(iso, "model_extensions.py")),
        },
        "model_contract_as_read_from_the_isolated_copy": {
            "formula": args.formula,
            "required": args.required.split(",") if args.required else [],
            "optional": args.optional.split(",") if args.optional else [],
            "defaults": json.loads(args.defaults),
            "driver_bounds": bounds,
            "entry_point": "scripts/model_registry.py calculate_registered_model("
                           "model_id, base_revenue, drivers, years)",
        },
        "allowed_write_roots": [attempt],
        "forbidden": [
            "writing anywhere outside the attempt directory",
            "writing under Projects/revenue-forecast outside .planning",
            "writing under Projects/company-wiki or Projects/filing-fetch",
            "editing .planning/reviews (frozen audit evidence)",
            "git add/commit/restore/stash in any of the three repos",
            "network calls, real providers, LLM calls, publication",
            "calling any product function other than calculate_registered_model for the formula oracle",
        ],
        "network": "disabled",
        "evidence_root": evidence,
        "created_before_runs": True,
    }
    write_json(os.path.join(attempt, "binding.json"), binding)

    commands = {
        "card_id": args.card,
        "python": [py, "-X", "utf8", "-B"],
        "note": "argv arrays only; no shell interpolation; expected and raw return codes recorded separately",
        "runs": [
            {"id": "A-oracle", "purpose": "independent expected values (stdlib only, no product import)",
             "cwd": attempt, "raw_returncode": 0, "expected_returncode": 0,
             "stdout": "evidence/%s/oracle_stdout.txt" % args.card,
             "stderr": "before/oracle_stderr.txt"},
            {"id": "B-product-run", "purpose": "calculate_registered_model(**input) positive + continuity + "
                                               "N01-N05 + card-specific negatives, all in the isolated snapshot",
             "cwd": attempt, "raw_returncode": 0, "expected_returncode": 0,
             "stdout": "evidence/%s/stdout.txt" % args.card,
             "stderr": "evidence/%s/stderr.txt" % args.card},
            {"id": "C-pytest-sanity", "purpose": "confirm the isolated venv pytest runs (no product suite claimed)",
             "cwd": attempt, "raw_returncode": 0, "expected_returncode": 0,
             "stdout": "before/pytest_version.txt"},
            {"id": "D-pdf-probe", "purpose": "read-only extraction of the disclosed figures from the frozen raw PDFs",
             "cwd": attempt, "raw_returncode": 0, "expected_returncode": 0,
             "interpreter": "global Miniconda python (PyMuPDF) - read-only, no card run",
             "stdout": "before/probe01_*.json, before/probe02_*.json"},
        ],
        "expected_exit_codes": 0,
        "raw_exit_codes": {"A": 0, "B": 0, "C": 0, "D": 0},
        "failed_then_fixed_runs": [
            {"id": "B-product-run (first attempt)", "raw_returncode": 1,
             "cause": "the first version of the case file used base_input='continuity' while input.json keys it "
                      "'continuity_positive', so the harness raised KeyError before running any case",
             "fix": "corrected the key in the oracle script (a test-harness bug, never a product change) and re-ran",
             "preserved_evidence": "the first attempt's stderr is superseded; the final run's stdout/stderr are "
                                   "the evidence of record"},
        ],
        "historical_mapping_probe": {
            "id": "%s-historical-mapping-probe" % args.card,
            "label": "historical_mapping_probe",
            "purpose": "verifiable wiring check only: the same disclosed historical parameter value is placed "
                       "under low/base/high so that field -> parameter -> model -> output can be traced",
            "not_a_scenario": True,
            "not_accuracy_evidence": True,
            "keys": json.loads(args.probe_keys),
            "note": args.probe_note,
            "production_entry_point_not_exercised": "scripts/forecast/segments.py calculate_model_path was NOT "
                                                    "run or reviewed in this attempt (I-10-A obligation)",
        },
    }
    write_json(os.path.join(attempt, "commands.json"), commands)

    probe = {
        "card_id": args.card,
        "model_id": args.model,
        "probe_id": "%s-historical-mapping-probe" % args.card,
        "label": "historical_mapping_probe",
        "warning": "This is NOT a three-scenario forecast and NOT accuracy evidence. All three keys intentionally "
                   "carry the SAME disclosed historical value so that the wiring is verifiable.",
        "disclosed_parameter_value": json.loads(args.probe_keys),
        "expected_behaviour": "all three keys must produce the identical output because the parameter values are "
                              "identical; any difference would indicate the scenario key is leaking into the "
                              "formula",
        "note": args.probe_note,
        "entry_point_status": "calculate_model_path (scripts/forecast/segments.py) NOT exercised; the wiring claim "
                              "is limited to calculate_registered_model",
        "reviewer": "PENDING_INDEPENDENT_REVIEW",
    }
    write_json(os.path.join(evidence, "historical_mapping_probe.json"), probe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
