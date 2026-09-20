"""!!! M31 CARD-TEXT CONSTANT CORRECTED (F-02 withdrawal, 2026-09-20T03:38:58.563523+00:00) !!!

The M31 entry below used to claim that card_M31.md L9 does NOT list net_revenue_per_unit.  That
claim was FALSE and was withdrawn by finding F-02: card_M31.md L9 lists all seven drivers and
model_cards.md L2818 lists the same seven, byte-identical.  The constant is now the seven drivers
with card_text_required_matches_registry = True, so a regeneration cannot re-create the retracted
record.  See evidence/M31/binding.json card_text_required_list_vs_registry.errata.superseded_values
for the withdrawn values.
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
    "M29": {"model_id": "commercial_launch", "title": "supply-constrained commercial launch",
            "registration_file": "model_extensions.py", "registration_line": 211,
            "declared_required": ["eligible_units", "annual_supply_capacity", "adoption_rate",
                                  "commercial_year_fraction", "net_revenue_per_unit"],
            "card_text_required_list": ["eligible_units", "annual_supply_capacity", "adoption_rate",
                                        "commercial_year_fraction", "net_revenue_per_unit"],
            "card_text_required_matches_registry": True,
            "declared_optional": []},
    "M30": {"model_id": "finite_adoption", "title": "finite market adoption",
            "registration_file": "model_extensions.py", "registration_line": 216,
            "declared_required": ["opening_unserved_market", "new_eligible_units",
                                  "removed_eligible_units", "adopted_units",
                                  "closing_unserved_market", "net_revenue_per_unit"],
            "card_text_required_list": ["opening_unserved_market", "new_eligible_units",
                                        "removed_eligible_units", "adopted_units",
                                        "closing_unserved_market", "net_revenue_per_unit"],
            "card_text_required_matches_registry": True,
            "declared_optional": []},
    "M31": {"model_id": "inventory_sellthrough", "title": "inventory and sell-through bridge",
            "registration_file": "model_extensions.py", "registration_line": 220,
            "declared_required": ["opening_inventory", "saleable_production", "purchased_units",
                                  "scrapped_units", "sold_units", "closing_inventory",
                                  "net_revenue_per_unit"],
            "card_text_required_list": ["opening_inventory", "saleable_production", "purchased_units",
                                        "scrapped_units", "sold_units", "closing_inventory",
                                        "net_revenue_per_unit"],
            "card_text_required_matches_registry": True,
            "card_text_divergence_note": None,
            "card_text_divergence_withdrawal_note": (
                "F-02 WITHDRAWAL: an earlier version of this constant claimed that card_M31.md L9 "
                "does NOT list net_revenue_per_unit. That claim was false: card_M31.md L9 lists all "
                "seven drivers and model_cards.md L2818 lists the same seven, byte-identical. The "
                "constant is now seven drivers with card_text_required_matches_registry = True; see "
                "evidence/M31/binding.json "
                "card_text_required_list_vs_registry.errata.superseded_values for the withdrawn "
                "values."),
            "declared_optional": []},
}

PRODUCTION_ROOT = r"C:\Users\郑曾波\Projects\revenue-forecast"
PRODUCTION_HASHES = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}
TEMPLATE_INTERPRETER = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
                        r"\2026-09-19-three-project-history-audit\execution_runs\I-00-A"
                        r"\a20260919-01\iso\venv\Scripts\python.exe")
ENTRY_POINT_LINE = 308


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
    declared_matches_registry = (
        sorted(info["declared_required"]) == sorted(spec.required)
        and sorted(info["declared_optional"]) == sorted(spec.optional))
    if not declared_matches_registry:
        raise SystemExit("BINDING ERROR: the drivers declared in this file do not match the registry "
                         "contract for %s: declared required=%s optional=%s, registry required=%s "
                         "optional=%s" % (info["model_id"], info["declared_required"],
                                          info["declared_optional"], list(spec.required),
                                          list(spec.optional)))

    # Verified line anchors: the card cites an entry-point line and a registration line.
    registry_lines = open(os.path.join(code_root, "model_registry.py"), "r",
                          encoding="utf-8").read().splitlines()
    registration_lines = open(os.path.join(code_root, info["registration_file"]), "r",
                              encoding="utf-8").read().splitlines()
    entry_text = registry_lines[ENTRY_POINT_LINE - 1]
    reg_text = registration_lines[info["registration_line"] - 1]
    anchors = {
        "entry_point_line_claimed_by_card": ENTRY_POINT_LINE,
        "entry_point_line_text": entry_text,
        "entry_point_anchor_ok": entry_text.startswith("def calculate_registered_model"),
        "registration_file": info["registration_file"],
        "registration_line_claimed_by_card": info["registration_line"],
        "registration_line_text": reg_text.strip(),
        "registration_anchor_ok": ('make("%s"' % info["model_id"]) in reg_text,
        "anchor_rule": ("the line numbers cited by the card are re-checked against the isolated copy "
                        "in THIS step, before the product run; a mismatch aborts the binding instead "
                        "of being carried forward silently"),
    }
    if not (anchors["entry_point_anchor_ok"] and anchors["registration_anchor_ok"]):
        raise SystemExit("BINDING ERROR: card anchors do not hold: " + json.dumps(anchors))

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
                "rule_read": ("run cwd must be a per-attempt isolation directory, never the repo root; "
                              "the global Miniconda python is FORBIDDEN for card runs"),
                "note": ("I-00-B binds the isolation plan and the two-stage command rule; it does not "
                         "materialise a checkout tree, so this attempt materialises its own read-only "
                         "snapshot (iso/checkout_scripts) and records the production hashes it was "
                         "copied from"),
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": ("present, used as a receipt reference only; this attempt re-hashed "
                                   "the files it actually used instead of trusting it"),
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
            "created_from_template": must_exist(TEMPLATE_INTERPRETER),
            "isolation": ("attempt-local venv created with `python -m venv` from the I-00-A template "
                          "venv"),
            "global_python_used_for": ("nothing in this card; the global Miniconda interpreter was "
                                       "never invoked (no PDF extraction happens in this card)"),
            "binding_written_by_interpreter": sys.executable,
            "pipeline_orchestrator_interpreter": args.orchestrator_interpreter,
            "pipeline_orchestrator_note": ("the orchestrator only creates the attempt venv and starts "
                                           "each unit as a subprocess; every card command, including "
                                           "the product run, names the bound attempt-venv interpreter "
                                           "in its own argv"),
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
        "declared_drivers_match_registry_contract": declared_matches_registry,
        "card_text_required_list_vs_registry": {
            "card_text_required_list": info["card_text_required_list"],
            "registry_required": list(spec.required),
            "card_text_matches_registry": info["card_text_required_matches_registry"],
            "divergence_note": info.get("card_text_divergence_note"),
        },
        "card_anchors_verified_before_the_run": anchors,
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
    print("declared_drivers_match_registry_contract", declared_matches_registry)
    print("anchors", json.dumps(anchors, ensure_ascii=False))
    print("contract", json.dumps(contract, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
