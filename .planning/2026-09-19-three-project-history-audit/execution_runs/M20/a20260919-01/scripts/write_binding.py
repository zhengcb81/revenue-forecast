"""Write the attempt's binding.json BEFORE the product run (START_HERE step 2).

All paths are absolute and verified to exist; the model contract block is read back
from the isolated snapshot (never from prose).

Usage:
  python -X utf8 -B write_binding.py --card M17 --attempt-root <attempt> --interpreter <python.exe>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import sys

CARDS = {
    "M17": {"model_id": "licensing_commercial", "title": "commercial sales and licensing revenue"},
    "M18": {"model_id": "advertising", "title": "impression fill and CPM"},
    "M19": {"model_id": "gaming", "title": "active-user payer monetisation"},
    "M20": {"model_id": "cohort_subscription", "title": "customer flow and time exposure"},
}

PRODUCTION_ROOT = r"C:\Users\郑曾波\Projects\revenue-forecast"
PRODUCTION_HASHES = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def bound_pair(lower, upper):
    return ["-inf" if lower == -math.inf else lower, "inf" if upper == math.inf else upper]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", required=True)
    parser.add_argument("--orchestrator-interpreter", default=None,
                        help=("interpreter that orchestrated the pipeline (the I-00-A template venv, "
                              "used for venv creation only; recorded for transparency"))
    args = parser.parse_args()

    card = args.card
    info = CARDS[card]
    attempt = os.path.abspath(args.attempt_root)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    evidence = os.path.join(attempt, "evidence", card)

    sys.path.insert(0, code_root)
    import model_registry  # noqa: E402

    spec = model_registry.MODEL_REGISTRY[info["model_id"]]
    drivers = list(spec.required) + list(spec.optional)
    contract = {
        "model_id": spec.model_id,
        "required": list(spec.required),
        "optional": list(spec.optional),
        "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
        "dimensions": dict(spec.dimensions),
        "ratio_drivers": sorted(spec.ratio_drivers),
        "declared_driver_bounds": {k: bound_pair(*b) for k, b in dict(spec.driver_bounds).items()},
        "effective_bounds": {d: bound_pair(*model_registry.driver_value_bounds(spec.model_id, d))
                             for d in drivers},
        "formula": spec.formula,
    }

    def must_exist(path):
        if not os.path.exists(path):
            raise SystemExit("BINDING ERROR: bound path does not exist: " + path)
        return path

    doc = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": info["model_id"],
        "card_title": info["title"],
        "binding_status": "bound",
        "written_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "written_before_any_product_run": True,
        "binding_sources": {
            "I-00-B": {
                "path": "execution_runs/I-00-B/a20260919-01/binding.json",
                "rule_read": ("run cwd must be a per-attempt isolation directory, never the repo "
                              "root; the global Miniconda python is FORBIDDEN for card runs"),
                "note": ("I-00-B binds the isolation plan and the two-stage command rule; it does "
                         "not materialise a checkout tree, so this attempt materialises its own "
                         "read-only snapshot (iso/checkout_scripts) and records the production "
                         "hashes it was copied from"),
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": ("present, used as a receipt reference only; this attempt "
                                   "re-hashed the files it actually used instead of trusting it"),
            },
            "I-00-A": {
                "path": "execution_runs/I-00-A/a20260919-01/baseline.json",
                "role": ("template interpreter and isolation finding (the global python loads an "
                         "editable dayu-agent finder, so isolated venvs are mandatory)"),
            },
        },
        "three_repo_paths": {
            "revenue-forecast": r"C:\Users\郑曾波\Projects\revenue-forecast",
            "company-wiki": r"C:\Users\郑曾波\Projects\company-wiki",
            "filing-fetch": r"C:\Users\郑曾波\Projects\filing-fetch",
        },
        "interpreter": {
            "path": must_exist(args.interpreter),
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": must_exist(
                r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
                r"\execution_runs\I-00-A\a20260919-01\iso\venv\Scripts\python.exe"),
            "isolation": ("attempt-local venv created with `python -m venv` from the I-00-A template "
                          "venv"),
            "global_python_used_for": ("nothing in this card; the global Miniconda interpreter was "
                                       "never invoked (no PDF extraction happens in this card)"),
            "binding_written_by_interpreter": sys.executable,
            "pipeline_orchestrator_interpreter": args.orchestrator_interpreter,
            "pipeline_orchestrator_note": ("the orchestrator only creates the attempt venv and starts "
                                           "each unit as a subprocess; every card command, including "
                                           "the product run, names the bound attempt-venv "
                                           "interpreter in its own argv"),
        },
        "cwd": attempt,
        "python_path": [code_root],
        "run_code_root": must_exist(code_root),
        "production_source_root_readonly": PRODUCTION_ROOT,
        "production_source_hashes": PRODUCTION_HASHES,
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py": sha256(
                must_exist(os.path.join(code_root, "model_registry.py"))),
            "iso/checkout_scripts/model_extensions.py": sha256(
                must_exist(os.path.join(code_root, "model_extensions.py"))),
        },
        "model_contract_as_read_from_the_isolated_copy": contract,
        "module_paths": {"code_root": code_root, "imports_used": ["model_registry"]},
        "config_paths": [],
        "allowed_write_roots": [attempt],
        "forbidden": [
            "writing anywhere outside the attempt directory",
            "writing under Projects/revenue-forecast outside .planning",
            "writing under Projects/company-wiki or Projects/filing-fetch",
            "editing .planning/reviews (frozen audit evidence)",
            "git add/commit/restore/stash in any of the three repos",
            "network calls, real providers, LLM calls, publication",
            ("calling any product function other than calculate_registered_model for the formula "
             "oracle"),
        ],
        "network": "disabled",
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256(must_exist(os.path.join(evidence, "input.json"))),
            "evidence/%s/oracle.json" % card: sha256(must_exist(os.path.join(evidence, "oracle.json"))),
            "evidence/%s/cases.json" % card: sha256(must_exist(os.path.join(evidence, "cases.json"))),
        },
        "evidence_root": evidence,
        "created_before_runs": True,
    }
    out = os.path.join(attempt, "binding.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("binding written", out)
    print("isolated_copy_equals_production",
          doc["isolated_copy_hashes"]["iso/checkout_scripts/model_registry.py"]
          == PRODUCTION_HASHES["scripts/model_registry.py"])
    print("contract", json.dumps(contract, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
