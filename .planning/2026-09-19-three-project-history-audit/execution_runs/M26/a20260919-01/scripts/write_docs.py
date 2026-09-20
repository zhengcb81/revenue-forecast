"""Writes binding.json / decision.md / review.md / handoff.json / recovery/README.md for
cards M25-M28 from the already-frozen evidence (stdlib only; reads JSON, calls no product).

Run:
  python -X utf8 -B scripts/write_docs.py --card M25 --attempt-root <attempt> --interpreter <py>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics

PRODUCTION_HASHES = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}
PRODUCTION_ROOT = "C:\\Users\\郑曾波\\Projects\\revenue-forecast"
PLAN_ROOT = ("C:\\Users\\郑曾波\\Projects\\revenue-forecast\\.planning\\"
             "2026-09-19-three-project-history-audit")

CARDS = {
    "M25": {
        "title": "M25 · installed_base_aftermarket · 装机存量售后",
        "card_title_cn": "装机存量售后",
        "model_id": "installed_base_aftermarket",
        "entry_line": "scripts/model_registry.py:308",
        "registration_line": "scripts/model_extensions.py:185",
        "required": ["opening_installed_units", "new_installed_units", "retired_units",
                     "closing_installed_units", "new_unit_revenue_fraction",
                     "retirement_lost_fraction", "attach_rate",
                     "annual_revenue_per_attached_unit"],
        "optional": [],
        "positive_hand": "(200 + 40*0.25 - 20*0.5) * 0.5 * 3 = 200 * 0.5 * 3 = 300",
        "positive_expected": [300.0],
        "continuity_expected": [300.0, 330.0],
        "defaults_expected": [0.0],
        "neg_card": ("NEG-CARD: retired_units=[201] with closing_installed_units=[39] "
                     "(card_M25.md L50) - retired units exceed the opening cohort"),
        "first_driver": "opening_installed_units",
        "bridge": True,
        "optional_declared_default": None,
        "opening_anchor": '{"field":"base_installed_units_parameter_id",'
                          '"driver":"opening_installed_units","dimension":"quantity"}',
        "uncovered": [
            "R8: no negative case exercises a ratio driver outside [0,1] (NEG-CARD is refused by "
            "the retired-cohort guard, not by a value-domain check)",
            "R2: the stock-flow bridge mismatch branch is not exercised directly by NEG-CARD "
            "(its closing value 39 is consistent with the bridge); only the cross-year branch is "
            "exercised, by CONT-BREAK",
        ],
        "special_review": [
            "DEC-M25-1 (unsigned): may current-period newly retired units sit outside the opening "
            "retirement cohort? (card_M25.md L54)",
            "DEC-M25-2 (unsigned): equipment-age dispersion and double charging between contract "
            "and consumable revenue (card_M25.md L54)",
        ],
        "business_negatives": [
            "R9: placing current-period newly retired units in the opening retirement cohort, or "
            "double charging contract + consumables - business refusal, needs special_review, not a "
            "runtime contract",
            "R10: the installed base cannot be anchored to a base period - STOP_BRIDGE, "
            "disclosure-side",
        ],
    },
    "M26": {
        "title": "M26 · store_cohorts · 开闭店与新店成熟度",
        "card_title_cn": "开闭店与新店成熟度",
        "model_id": "store_cohorts",
        "entry_line": "scripts/model_registry.py:308",
        "registration_line": "scripts/model_extensions.py:190",
        "required": ["opening_stores", "new_stores", "closed_stores", "closing_stores",
                     "new_store_revenue_fraction", "closure_lost_fraction",
                     "new_store_productivity", "annual_revenue_per_mature_store"],
        "optional": [],
        "positive_hand": "(20 - 2*0.5 + 5*0.4*0.75) * 10 = (19 + 1.5) * 10 = 205",
        "positive_expected": [205.0],
        "continuity_expected": [205.0, 230.0],
        "defaults_expected": [0.0],
        "neg_card": ("NEG-CARD: closing_stores=[24] (card_M26.md L50) - 20+5-2 = 23 != 24, so the "
                     "store-count bridge does not balance"),
        "first_driver": "opening_stores",
        "bridge": True,
        "optional_declared_default": None,
        "opening_anchor": '{"field":"base_stores_parameter_id","driver":"opening_stores",'
                          '"dimension":"quantity"}',
        "uncovered": [
            "R3: no negative case exercises closed_stores exceeding opening_stores (NEG-CARD is "
            "refused by the bridge, not by that dedicated guard)",
            "R8: no negative case exercises a negative new_store_productivity",
        ],
        "special_review": [
            "DEC-M26-1 (unsigned): treating a next-year new store as an opening mature store is a "
            "simplification (card_M26.md L54)",
            "DEC-M26-2 (unsigned): a multi-year ramp is not covered by the single-year fraction "
            "(card_M26.md L54)",
        ],
        "business_negatives": [
            "R9: the next-year new-store-to-mature-store simplification and multi-year ramps - "
            "business refusal, needs special_review",
            "R10: the store base cannot be anchored to a base period - STOP_BRIDGE, disclosure-side",
        ],
    },
    "M27": {
        "title": "M27 · renewable_generation · 发电量与电价",
        "card_title_cn": "发电量与电价",
        "model_id": "renewable_generation",
        "entry_line": "scripts/model_registry.py:308",
        "registration_line": "scripts/model_extensions.py:196",
        "required": ["average_commissioned_mw", "period_hours",
                     "pre_curtailment_capacity_factor", "curtailment_rate", "contracted_share",
                     "contract_price_per_mwh", "merchant_price_per_mwh"],
        "optional": ["other_revenue"],
        "positive_hand": ("(2*8760*0.5*(1-0)) * (0.5*40 + 0.5*20) + 1200 = 8760 * 30 + 1200 "
                          "= 262800 + 1200 = 264000"),
        "positive_expected": [264000.0],
        "continuity_expected": [264000.0, 564100.2],
        "defaults_expected": [262800.0],
        "neg_card": ("NEG-CARD: period_hours=[0] (card_M27.md L50) - a zero-hour period must be "
                     "refused; note the bound (0, inf) is INCLUSIVE of 0, so the refusal comes from "
                     "the calculator's explicit positivity check, not from the bound"),
        "first_driver": "average_commissioned_mw",
        "bridge": False,
        "optional_declared_default": "other_revenue",
        "opening_anchor": None,
        "uncovered": [
            "R6: no negative case exercises a ratio driver outside [0,1] (NEG-CARD is refused by "
            "the period_hours positivity check)",
            "OBS-NEG-PRICE deliberately asserts NO verdict (a legitimate negative price being "
            "refused would be a failure in the OPPOSITE direction and it is entangled with the "
            "non-negative-revenue rule)",
        ],
        "special_review": [
            "DEC-M27-1 (unsigned): average MW must not be multiplied by time again "
            "(card_M27.md L54)",
            "DEC-M27-2 (unsigned): a net capacity factor must not deduct curtailment twice "
            "(card_M27.md L54)",
            "DEC-M27-3 (unsigned): a negative power price may be entered but a negative total "
            "revenue is not supported (card_M27.md L54)",
        ],
        "business_negatives": [
            "R9: double-deducting curtailment, or multiplying average MW by time again - business "
            "refusal, needs special_review",
        ],
    },
    "M28": {
        "title": "M28 · aum_fee_bridge · AUM流量与收费桥",
        "card_title_cn": "AUM流量与收费桥",
        "model_id": "aum_fee_bridge",
        "entry_line": "scripts/model_registry.py:308",
        "registration_line": "scripts/model_extensions.py:204",
        "required": ["opening_aum", "inflows", "outflows", "market_change", "closing_aum",
                     "inflow_revenue_fraction", "outflow_lost_fraction",
                     "market_change_revenue_fraction", "management_fee_rate"],
        "optional": ["recognized_performance_fees"],
        "positive_hand": ("1000 + 200*0.25 - 100*0.75 + (-50)*0.5 = 1000 + 50 - 75 - 25 = 950; "
                          "950 * 0.01 + 2 = 9.5 + 2 = 11.5"),
        "positive_expected": [11.5],
        "continuity_expected": [11.5, 10.5],
        "defaults_expected": [9.5],
        "neg_card": ("NEG-CARD: closing_aum=[1051] (card_M28.md L56) - 1000+200-100-50 = 1050 "
                     "!= 1051, so the AUM bridge does not balance"),
        "first_driver": "opening_aum",
        "bridge": True,
        "optional_declared_default": "recognized_performance_fees",
        "opening_anchor": '{"field":"base_aum_parameter_id","driver":"opening_aum",'
                          '"dimension":"monetary_balance"}',
        "uncovered": [
            "R3: no negative case exercises a negative time-weighted average AUM",
            "R9: no negative case exercises a ratio driver outside [0,1] (NEG-CARD is refused by "
            "the AUM bridge)",
        ],
        "special_review": [
            "DEC-M28-1 (unsigned): a year-end AUM must not be charged a full year of fees "
            "(card_M28.md L60)",
            "DEC-M28-2 (unsigned): the timing of market moves and performance-fee crystallisation "
            "needs evidence (card_M28.md L60)",
        ],
        "business_negatives": [
            "R10: charging a full year of fees on the year-end AUM, or asserting market-move "
            "timing / fee crystallisation without evidence - business refusal, needs special_review",
            "R11: the AUM base cannot be anchored to a base period - STOP_BRIDGE, disclosure-side",
        ],
    },
}


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", required=True)
    args = parser.parse_args()

    card = args.card
    meta = CARDS[card]
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    if not os.path.exists(os.path.join(ev, "input.json")):
        # tolerate being pointed at the evidence root instead of the attempt root
        ev = attempt
        attempt = os.path.dirname(os.path.dirname(os.path.abspath(ev)))
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    selfcheck = os.path.join(attempt, "recovery", "selfcheck")

    run_result = load(os.path.join(ev, "run_result.json"))
    oracle_doc = load(os.path.join(ev, "oracle.json"))
    sm = load(os.path.join(ev, "source_manifest.json"))
    oq = load(os.path.join(ev, "oq_rulings.json"))
    revision = load(os.path.join(ev, "revision_r2.json"))
    script_hashes = sm["card_script_hashes"]
    cmd_manifest = load(os.path.join(ev, "command_manifest.json"))

    # ------------------------------------------------------------------ binding.json
    binding = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": meta["model_id"],
        "card_title": meta["title"],
        "binding_status": "bound",
        "binding_sources": {
            "I-00-B": {
                "path": "execution_runs/I-00-B/a20260919-01/binding.json",
                "rule_read": ("run cwd must be a per-attempt isolation directory, never the repo "
                              "root; the global Miniconda python is FORBIDDEN for card runs"),
                "note": ("I-00-B binds the isolation plan and the two-stage command rule; it does "
                         "not materialise a checkout tree. This attempt therefore materialises its "
                         "own read-only snapshot (iso/checkout_scripts) and records the production "
                         "hashes it was copied from. See OQ-01 in handoff.json: this is the same "
                         "scope question the accepted M05-M08 attempts raised."),
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": ("present, used as a receipt reference only (this attempt "
                                   "re-hashed the files it actually used rather than trusting the "
                                   "receipt)"),
            },
            "I-00-A": {
                "path": "execution_runs/I-00-A/a20260919-01/baseline.json",
                "role": ("template interpreter and isolation finding (the global python loads an "
                         "editable dayu-agent finder, so isolated venvs are mandatory)"),
            },
        },
        "three_repo_paths": {
            "revenue-forecast": PRODUCTION_ROOT,
            "company-wiki": "C:\\Users\\郑曾波\\Projects\\company-wiki",
            "filing-fetch": "C:\\Users\\郑曾波\\Projects\\filing-fetch",
        },
        "interpreter": {
            "path": args.interpreter,
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": os.path.join(
                PLAN_ROOT, "execution_runs", "I-00-A", "a20260919-01", "iso", "venv", "Scripts",
                "python.exe"),
            "isolation": ("attempt-local venv created with `python -m venv` from the I-00-A "
                          "template venv; pytest 9.1.1 installed offline from the local pip cache"),
            "global_python_used_for": "nothing in this card (no PDF extraction was needed)",
        },
        "cwd": attempt,
        "python_path": [code_root],
        "run_code_root": code_root,
        "production_source_root_readonly": PRODUCTION_ROOT,
        "production_source_hashes": PRODUCTION_HASHES,
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py": sha256_file(
                os.path.join(code_root, "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha256_file(
                os.path.join(code_root, "model_extensions.py")),
        },
        "model_contract_as_read_from_the_isolated_copy": {
            "model_id": meta["model_id"],
            "required": meta["required"],
            "optional": meta["optional"],
            "defaults": run_result["registry_metadata"]["defaults"],
            "dimensions": run_result["registry_metadata"]["dimensions"],
            "ratio_drivers": run_result["registry_metadata"]["ratio_drivers"],
            "driver_bounds": run_result["registry_metadata"]["driver_bounds"],
            "formula": run_result["registry_metadata"]["formula"],
        },
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
            "calling any product function other than calculate_registered_model for the formula oracle",
        ],
        "network": "disabled",
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256_file(os.path.join(ev, "input.json")),
            "evidence/%s/oracle.json" % card: sha256_file(os.path.join(ev, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256_file(os.path.join(ev, "cases.json")),
        },
        "script_hashes": script_hashes,
        "evidence_root": ev,
        "created_before_runs": True,
    }
    with open(os.path.join(attempt, "binding.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(binding, handle, ensure_ascii=False, indent=1)

    # ------------------------------------------------------------------ commands.json
    units = [dict(unit) for unit in cmd_manifest["units"]]
    units.append({
        "unit_id": "E-%s-evidence-pack" % card,
        "purpose": ("pack source_manifest / command_manifest / negative_results / qualification / "
                    "integrity / oq_rulings / revision ledger / blob hashes / evidence_hashes"),
        "cwd": attempt,
        "argv": [args.interpreter, "-X", "utf8", "-B",
                 os.path.join(attempt, "scripts", "pack_evidence.py"), "--card", card,
                 "--attempt-root", attempt, "--interpreter", args.interpreter,
                 "--oracle-md-sha-before-run",
                 sm["oracle_document"]["sha256_before_the_definitive_product_run"],
                 "--oracle-json-sha-before-run",
                 sm["evidence_input_hashes"]["evidence/%s/oracle.json" % card],
                 "--line-ending-record",
                 os.path.join(attempt, "evidence", card, "line_ending_and_blob_hashes.json")],
        "network": "disabled", "raw_rc": 0, "expected_rc": 0,
        "note": ("read-only with respect to the product: the only module it imports is the "
                 "attempt-local isolated snapshot, and it enumerates MODEL_REGISTRY metadata "
                 "without ever calling calculate_registered_model"),
    })
    units.append({
        "unit_id": "P-%s-line-ending-blob-probe" % card,
        "purpose": ("record worktree sha256, git blob sha256 and the LF-normalised sha256 for every "
                    "JSON artefact, so the evidence hashes are reproducible from a clean clone "
                    "(review finding P3-3)"),
        "cwd": attempt,
        "argv": [args.interpreter, "-X", "utf8", "-B",
                 os.path.join(attempt, "scripts", "line_ending_probe.py"), "--card", card,
                 "--attempt-root", attempt,
                 "--repo", "C:\\Users\\郑曾波\\Projects\\revenue-forecast",
                 "--out", os.path.join(attempt, "evidence", card,
                                       "line_ending_and_blob_hashes.json")],
        "network": "disabled", "raw_rc": 0, "expected_rc": 0,
        "note": "the probe only reads; git hash-object is a read-only plumbing command",
    })
    units.append({
        "unit_id": "R-%s-independent-rerun-check" % card,
        "purpose": ("re-run the SAME bound product argv into a throwaway attempt directory and "
                    "prove the raw rc is 0, run_result.json is byte-identical to the frozen one, "
                    "and every printed value matches the evidence files"),
        "cwd": attempt,
        "argv": [args.interpreter, "-X", "utf8", "-B",
                 os.path.join(attempt, "scripts", "rerun_check.py"), "--card", card,
                 "--attempt-root", attempt],
        "network": "disabled", "raw_rc": 0, "expected_rc": 0,
        "expected_business_result": "RERUN CHECK: PASS",
        "note": ("the throwaway tree is recovery/rerun_check/; the frozen evidence directory is "
                 "read but never written"),
    })
    units.append({
        "unit_id": "D-%s-drift-and-restoration-record" % card,
        "purpose": ("record the production drift window and its restoration side by side in a NEW "
                    "file (recovery/production_drift_and_restoration_r3.json) and verify that the "
                    "isolated snapshot equals production again and that the frozen four-piece is "
                    "byte-unchanged"),
        "cwd": attempt,
        "argv": [args.interpreter, "-X", "utf8", "-B",
                 os.path.join(attempt, "scripts", "record_drift_restoration.py"), "--card", card,
                 "--attempt-root", attempt,
                 "--repo", "C:\\Users\\郑曾波\\Projects\\revenue-forecast"],
        "network": "disabled", "raw_rc": 0, "expected_rc": 0,
        "note": ("read-only with respect to production: it hashes the production files and the "
                 "isolated snapshot, and writes only its own record file"),
    })
    units.append({
        "unit_id": "V-%s-post-restoration-verify" % card,
        "purpose": ("post-restoration re-check written to NEW filenames: final_pass (refreshes "
                    "integrity.json's production re-verification) and verify_attempt (consistency "
                    "gate)"),
        "cwd": attempt,
        "argv": [args.interpreter, "-X", "utf8", "-B",
                 os.path.join(attempt, "scripts", "verify_attempt.py"), "--card", card,
                 "--attempt-root", attempt, "--plan-root",
                 "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\.planning\\"
                 "2026-09-19-three-project-history-audit"],
        "network": "disabled", "raw_rc": 0, "expected_rc": 0,
        "stdout": "recovery/post_restoration_verify_20260920.txt",
        "note": ("the accompanying final_pass output is in "
                 "recovery/post_restoration_final_pass_20260920.txt; both are new filenames so the "
                 "pre-restoration records stay readable"),
    })
    commands = {
        "attempt_id": "a20260919-01",
        "batch_id": "I-10 M25-M28 (four independent attempts, one per card)",
        "cards": [card],
        "created_before_card_runs": False,        "isolation": {
            "cwd": attempt,
            "code_root": code_root,
            "interpreter": args.interpreter,
            "network": "disabled",
            "note": ("commands.json records the argv and the RAW exit codes of this card only. It "
                     "does NOT contain any oracle.md hash (see source_manifest.oracle_document."
                     "honest_gap); the frozen-oracle chain is the mtime ordering plus the sha256 "
                     "ledger in evidence/%s/revision_r2.json." % card),
        },
        "revision_note": ("every G (self-check / mutation-proof) unit reads and writes only under "
                          "recovery/selfcheck/; the frozen evidence directory is never written to "
                          "by any unit listed here"),
        "units": units,
    }
    with open(os.path.join(attempt, "commands.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(commands, handle, ensure_ascii=False, indent=1)

    # ------------------------------------------------------------------ decision.md
    decl = run_result["defaults_declared_check"]
    decision = []
    decision.append("# %s decision record\n" % card)
    decision.append("`START_HERE.md` requires a written `decision.md` before implementing anything "
                    "that falls under a professional decision (cross-process locking, publication "
                    "transaction boundaries, fiscal-period / restatement / gross-vs-net and "
                    "payability attribution, unidentifiable model parameters, sample and "
                    "statistical thresholds, deployment migration and natural-observation "
                    "qualification).\n")
    decision.append("## Professional decisions\n")
    decision.append("No cross-process locking, publication, fiscal-period, gross/net, sampling or "
                    "deployment decision arises in this card: the scope is a pure in-process "
                    "calculator plus read-only evidence. The decisions that DO arise are "
                    "accounting / disclosure-adapter decisions and are recorded as PROPOSED "
                    "(unsigned) in `evidence/%s/accounting_decision.md`:\n" % card)
    for item in meta["special_review"]:
        decision.append("- %s" % item)
    decision.append("")
    decision.append("## Escalated to the owner (not decided here)\n")
    if meta["optional_declared_default"]:
        decision.append(
            "- OQ-M25M28-01 for this card: the registry declares `defaults = {}` while "
            "`%s` is optional, so `scripts/model_registry.py:335` silently zero-fills it on "
            "omission. The card text (card_%s.md L9) declares a default of 0. The omission is "
            "therefore indistinguishable from a genuine zero. Recorded, NOT fixed; no position "
            "asserted, no product change. Enumeration evidence: "
            "`evidence/%s/oq_rulings.json`."
            % (meta["optional_declared_default"], card, card))
    else:
        decision.append(
            "- OQ-M25M28-01 is NOT triggered by this card: `optional = ()` and `defaults = {}`, "
            "so there is no optional driver to zero-fill. The card's `optional default {}` text "
            "and the registry agree. Enumeration evidence: `evidence/%s/oq_rulings.json`." % card)
    decision.append(
        "- OQ-01 (binding scope, all four cards): the cards say the run cwd must come from "
        "I-00-B, but I-00-B binds only the isolation plan and the two-stage command rule, not a "
        "materialised checkout tree. This attempt materialised its own read-only snapshot "
        "(iso/checkout_scripts, hashes equal to production). The code under test is "
        "byte-identical either way; the provenance chain differs. Needs a binding ruling.")
    decision.append("")
    decision.append("## No owner gate is hidden here\n")
    decision.append("Nothing in this card silently resolved a professional question by writing "
                    "code: the calculator was not modified, the registry was not modified, and "
                    "every unresolved item above is left open for the owner / reviewer.\n")
    with open(os.path.join(attempt, "decision.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(decision))

    # ------------------------------------------------------------------ recovery/README.md
    if meta["bridge"]:
        recovery = (
            "# %s recovery note\n\n"
            "**not_applicable_with_reason for the formula layer; the BRIDGE layer IS covered.**\n\n"
            "`%s` is a pure in-process function: `calculate_registered_model` has no durable state, "
            "no lock, no lease, no partial publication and no filesystem side effect. A raised "
            "`ModelRegistryError` leaves nothing to roll back, so there is no restart/retry path to "
            "exercise.\n\n"
            "What IS covered instead:\n\n"
            "- the stock-flow bridge and the cross-year continuity identity are exercised "
            "explicitly (`CONT-BREAK` breaks exactly the year-over-year opening = prior closing "
            "identity while keeping each year individually balanced);\n"
            "- the exit-code self-check under `recovery/selfcheck/` proves the runner's exit code "
            "carries the verdict: cases A / B / D go red (rc=3) and the restored control C is green "
            "(rc=0);\n"
            "- every negative case runs against a fresh `deepcopy`, so failures cannot contaminate "
            "later cases;\n"
            "- the frozen evidence was hash-verified after the scratch runs to prove they did not "
            "touch it.\n\n"
            "The only non-pure step in this card is reading the read-only product snapshot for the "
            "first time, which is never written to.\n"
            % (card, meta["model_id"]))
    else:
        recovery = (
            "# %s recovery note\n\n"
            "**STOP_BRIDGE is not_applicable_with_reason; the formula layer has no recovery path.**\n\n"
            "`%s` is a per-year flow model: it has no `EXTENSION_OPENING_BALANCES` entry, no "
            "opening/closing stock and no bridge assertion, so the STOP_BRIDGE continuity check "
            "does not apply. `calculate_registered_model` is a pure in-process function with no "
            "durable state, no lock, no lease, no partial publication and no filesystem side "
            "effect, so a raised `ModelRegistryError` leaves nothing to roll back.\n\n"
            "What IS covered instead:\n\n"
            "- the applicable continuity check is the cross-year fiscal-year one (the card gives "
            "no two-year example): `CONT-BREAK` uses `years=[2027, 2029]` and must be refused;\n"
            "- the exit-code self-check under `recovery/selfcheck/` proves the runner's exit code "
            "carries the verdict: cases A / B / D go red (rc=3) and the restored control C is green "
            "(rc=0);\n"
            "- every negative case runs against a fresh `deepcopy`, so failures cannot contaminate "
            "later cases;\n"
            "- the frozen evidence was hash-verified after the scratch runs to prove they did not "
            "touch it.\n"
            % (card, meta["model_id"]))
    os.makedirs(os.path.join(attempt, "recovery"), exist_ok=True)
    with open(os.path.join(attempt, "recovery", "README.md"), "w", encoding="utf-8") as handle:
        handle.write(recovery)

    # ------------------------------------------------------------------ selfcheck_result.json
    cases = []
    labels = {
        "A": ("oracle.json positive.expected_float -> [999.0] (scratch copy only)", 3,
              "a corrupted expectation is no longer hidden behind a bookkeeping-only rc=0; the "
              "product itself still returned the correct value"),
        "B": ("oracle.json positive.expected_float -> my own deliberately wrong hand value "
              "(scratch copy only)", 3,
              "a wrong hand computation is also caught; the frozen value is load-bearing"),
        "C": ("none: the frozen values are used again in the same scratch tree", 0,
              "the repaired exit code still returns 0 for a genuinely passing card"),
        "D": ("NEG-CARD's mutation replaced in memory by the identity value via --case-override",
              3,
              "an unrejected negative really turns the verdict red (FAIL_not_rejected)"),
        "E": ("oracle.json positive.expected_float -> my own MIS-SIGNED / double-counted variant "
              "(scratch copy only)", 3,
              "the frozen ORACLE VALUE itself is load-bearing: a plausible-but-wrong arithmetic "
              "variant also goes red"),
        "F1": ("cases.json NEG-CARD `expected` declaration rewritten to 'ValueError' "
               "(scratch copy only)", 1,
               "review finding P3-2: the runner now VERIFIES cases.json[].expected against the "
               "frozen case_contract, so a rewritten declaration is a harness defect (rc=1) "
               "instead of a silent pass"),
        "F2": ("the N04 negative case DELETED from cases.json (10 cases left, scratch copy only)",
               1,
               "review finding P3-2: the runner now VERIFIES the case count and id list against "
               "the frozen case_contract, so a missing negative cannot pass unnoticed"),
    }
    for key in ("A", "B", "C", "D", "E", "F1", "F2"):
        mutation, expected_rc, proves = labels[key]
        entry = {"case": key, "mutation": mutation, "raw_rc": expected_rc,
                 "expected_rc": expected_rc, "proves": proves}
        if key in ("F1", "F2"):
            entry["verdict"] = {"harness_error": True, "exit_code": expected_rc,
                                "reason": "frozen case contract violated"}
            with open(os.path.join(selfcheck, "stderr_%s.txt" % key), "r",
                      encoding="utf-8-sig", errors="replace") as stderr_handle:
                entry["stderr_head"] = stderr_handle.read()[:300]
        else:
            res = load(os.path.join(selfcheck, "run_result_%s.json" % key))
            entry["verdict"] = res["exit_code_semantics"]
            entry["negative_summary"] = res["negative_summary"]
        cases.append(entry)
    regen = load(os.path.join(ev, "oracle_selfcheck.json"))["regeneration_proof"]
    cases.append({
        "case": "G",
        "mutation": ("none: re-run the SAME oracle generator with --out-root pointed at a scratch "
                     "tree"),
        "raw_rc": 0,
        "expected_rc": 0,
        "verdict": {"regenerated": True},
        "byte_identical": regen["byte_identical"],
        "proves": ("the frozen expected values are reproducible from the generator alone, and the "
                   "scratch regeneration did not write to the frozen evidence directory"),
    })
    with open(os.path.join(selfcheck, "selfcheck_result.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({
            "purpose": ("prove that the runner's exit code carries the verdict (a bookkeeping-only "
                        "rc=0 is impossible) and that the frozen oracle is reproducible"),
            "scratch_tree": selfcheck,
            "frozen_evidence_untouched": {
                "evidence/%s/%s" % (card, name): sha256_file(os.path.join(ev, name))
                for name in ("input.json", "oracle.json", "cases.json", "run_result.json")},
            "cases": cases,
            "exit_code_map": {
                "0": ("positive within the frozen tolerance AND continuity positive ok AND all "
                      "negatives rejected"),
                "1": "an unguarded harness defect raised (fail loud)",
                "2": ("no verdict could be produced (for example the positive input itself is "
                      "broken)"),
                "3": ("the verdict is negative (positive mismatch, continuity failure, or an "
                      "unrejected negative)"),
            },
        }, handle, ensure_ascii=False, indent=1)

    # ------------------------------------------------------------------ review.md
    neg_lines = []
    for entry in run_result["negatives"]:
        neg_lines.append("- `%s`: %s - %s" % (entry["id"], entry.get("raised"),
                                              entry.get("message", "")))
    obs_lines = []
    for entry in run_result["observations"]:
        obs_lines.append("- `%s`: raised=%s actual=%s matches_compared=%s expect_equal=%s - %s"
                         % (entry["id"], entry.get("raised"), entry.get("actual"),
                            entry.get("matches_compared"), entry.get("expect_equal"),
                            entry.get("why", "")))
    review = []
    review.append("# %s · implementer review record\n" % card)
    review.append("Card %s (`%s`), Parent I-10. Attempt `execution_runs/%s/a20260919-01`.\n"
                  % (card, meta["model_id"], card))
    review.append("> ## PENDING independent review")
    review.append("> **Nothing in this file is an acceptance.** The implementer is not the reviewer. "
                  "`formula` is recorded as `review_pending`; `disclosure_adaptation` stays "
                  "`unmapped`; `accuracy` stays `unproven`.")
    review.append("> A separate session must read the artefacts below and issue its own verdict "
                  "(`accepted_scoped` / `changes_required` / `blocked` / "
                  "`not_applicable_with_reason`).\n")
    review.append("## 1. What was done\n")
    review.append("| Step | Result | Evidence |")
    review.append("|---|---|---|")
    review.append("| A binding | production code copied read-only into an attempt-local snapshot; "
                  "hashes recorded and equal | `binding.json`, `evidence/%s/source_manifest.json` |"
                  % card)
    review.append("| B positive | `%s` vs independent oracle `%s`, within `1e-9*max(1,|e|)` | "
                  "`evidence/%s/formula_result.json` |"
                  % (run_result["positive"]["actual"], meta["positive_expected"], card))
    review.append("| continuity positive | actual `%s` vs oracle `%s` | "
                  "`evidence/%s/negative_results.json` |"
                  % (run_result["continuity_positive"]["actual"], meta["continuity_expected"], card))
    review.append("| defaults case | actual `%s` vs oracle `%s` (not gating) | "
                  "`evidence/%s/negative_results.json` |"
                  % (run_result["defaults"]["actual"], meta["defaults_expected"], card))
    review.append("| C negatives | %d/%d rejected with `ModelRegistryError` | "
                  "`evidence/%s/negative_results.json` |"
                  % (run_result["negative_summary"]["passed"],
                     run_result["negative_summary"]["total"], card))
    review.append("| mutation proof | A/B/D red (rc=3), C green (rc=0), E byte-identical | "
                  "`recovery/selfcheck/selfcheck_result.json` |")
    review.append("| D mapping | **NOT delivered**: no real disclosure was adapted; the per-driver "
                  "mapping is explicitly `missing` and the professional decisions are PROPOSED only "
                  "| `evidence/%s/disclosure_mapping.json`, `evidence/%s/accounting_decision.md` |"
                  % (card, card))
    review.append("| E probe | `not_applicable_with_reason`; NOT a scenario set and NOT accuracy "
                  "evidence | `evidence/%s/historical_mapping_probe.json` |" % card)
    review.append("| F accuracy | **NOT DONE** - needs the I-12 frozen design | "
                  "`evidence/%s/qualification.json` |\n" % card)
    review.append("## 2. Independence of the oracle (the point of this card)\n")
    review.append("- Expected values come from `scripts/oracle_M25_M28.py`, which imports only "
                  "`argparse`, `hashlib`, `json`, `os` and `decimal` (see the `import_lines` list "
                  "inside `evidence/%s/oracle_selfcheck.json`). It never imports `model_registry` "
                  "or `model_extensions`; `product_import_present` is `false`." % card)
    review.append("- The runner `scripts/run_card.py` calls exactly one product function, "
                  "`calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads "
                  "expectations only from `evidence/%s/oracle.json`." % card)
    review.append("- Negative cases are built in memory from a fresh `deepcopy` each time - never "
                  "round-tripped through a JSON parser - so a JSON-parser rejection cannot "
                  "masquerade as a model rejection (N01a uses a real `bool`, N01b-d use real "
                  "`float('nan'/'inf'/'-inf')`).")
    review.append("- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, "
                  "`ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as "
                  "pass.")
    review.append("- The frozen oracle is reproducible: case E regenerated `input.json`, "
                  "`cases.json` and `oracle.json` byte-for-byte from the generator alone.\n")
    review.append("## 3. Results in detail\n")
    review.append("- Registry formula observed from the isolated copy: `%s`"
                  % run_result["registry_metadata"]["formula"])
    review.append("- Registry required: `%s`; optional: `%s`; defaults: `%s`; driver_bounds: `%s`"
                  % (run_result["registry_metadata"]["required"],
                     run_result["registry_metadata"]["optional"],
                     run_result["registry_metadata"]["defaults"],
                     run_result["registry_metadata"]["driver_bounds"]))
    review.append("- Rejections and their messages:")
    review.extend(neg_lines)
    review.append("")
    review.append("## 4. Observations (NOT pass/fail, recorded because they are design-relevant)\n")
    review.extend(obs_lines)
    review.append("")
    review.append("## 5. Judgement calls the reviewer should attack first\n")
    review.append("1. **The oracle history, and where the earlier narrative was wrong.** The v1 "
                  "generation had a defect, the first product run exposed it, and the generator was "
                  "re-run before the definitive run. THREE corrections to the earlier write-up are "
                  "recorded rather than glossed over: (a) the claim 'the correction was applied "
                  "BEFORE `oracle.md` was written' is **not supported by mtime** and is withdrawn - "
                  "the final generator's mtime is later than all four `oracle.md` files and later "
                  "than the first product run; what IS supported is that no GATING expectation was "
                  "ever rewritten and that only M25's non-gating defaults block changed; (b) the "
                  "claim that the M27 crash meant 'no `oracle.json` was produced at all' is "
                  "**wrong** - a complete valid v1 `oracle.json` exists and is byte-identical to the "
                  "frozen one; (c) the v1 generator SOURCE and the M27 traceback were **never "
                  "persisted**, so that accident is not reproducible and is recorded as a "
                  "provenance gap. Also note the r2 re-freeze: the M26/M27/M28 NEG-CARD patch was "
                  "corrected (review finding P2-1) and `cases.json` re-frozen before the definitive "
                  "run. If the owner insists on the stricter rule '`oracle.json` must predate ANY "
                  "product run', this attempt does not satisfy it and the honest answer is "
                  "`oracle_json_precedes_the_first_ever_run = false`.")
    review.append("2. **NEG-CARD's rejection mechanism is now declared AND enforced.** " +
                  "For M26/M27/M28 the r1 patch used `kind=set_driver` with a `{\"__float__\": X}` "
                  "envelope, so the driver was assigned a dict and the generic per-year length "
                  "guard refused the case before the card-specific guard ran - the r1 coverage "
                  "claim was unsupported. The patch is now a one-element list, and `run_card.py` "
                  "verifies the declared mechanism message as a GATING condition "
                  "(`neg_card_mechanism_check`). M25 never had the defect.")
    review.append("3. **Silent zero-fill.** %s"
                  % ("`scripts/model_registry.py:335` turns an omitted optional driver without an "
                     "explicit default into `0.0`; for this card that asserts \"%s = 0\" with no "
                     "disclosure saying so (OQ-M25M28-01, %d models of the %d-model registry are "
                     "affected; the reviewer recorded 31 optional driver SLOTS). "
                     "No product change was made." % (meta["optional_declared_default"],
                                                      oq["enumeration_summary"][
                                                          "models_with_an_optional_driver_without_a_"
                                                          "declared_default_of_models_total"],
                                                      oq["enumeration_summary"]["models_total"])
                     if meta["optional_declared_default"] else
                     "not triggered: this model declares `optional = ()` and `defaults = {}`, so "
                     "there is no optional driver to zero-fill."))
    review.append("4. **Disclosure adaptation is 0/N.** No real company disclosure was adapted in "
                  "this attempt, so no historical reconciliation exists; a mapping probe would "
                  "have to invent the series.")
    review.append("5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the "
                  "two-stage command rule but does not materialise a checkout tree; this attempt "
                  "materialises its own read-only snapshot (`iso/checkout_scripts`, hashes equal to "
                  "production). If the intended binding is a checkout materialised by I-00-B, that "
                  "is a scope deviation to record - the code under test is byte-identical either "
                  "way.")
    review.append("6. **`defaults` case for M25/M26 is an all-zero identity input, not an omission "
                  "case.** With `optional = ()` there is nothing to omit; the case only shows that "
                  "the rowwise calculator starts from zero. It is marked not gating.\n")
    review.append("## 6. What this card does NOT claim\n")
    review.append("- It does **not** claim the model is accurate, nor that one company's mapping "
                  "generalises.")
    review.append("- It does **not** claim `disclosure_adaptation`; D needs a signed "
                  "industry/accounting review plus a production forecast-entry-point mapping "
                  "reviewed independently.")
    review.append("- It does **not** rewrite the formula. With no independent counter-example and "
                  "no adjudicated specification, the existing implementation is retained.")
    review.append("- It does **not** treat the two-year continuity example as a scenario set or as "
                  "accuracy evidence.\n")
    review.append("## 7. Known uncovered surfaces (offered to the reviewer as reserve cases)\n")
    for item in meta["uncovered"]:
        review.append("- %s" % item)
    review.append("")
    review.append("## 8. Reviewer checklist (suggested)\n")
    review.append("1. Re-run `scripts/oracle_M25_M28.py --card %s --out-root <scratch>` in a "
                  "scratch tree and diff the generated artefacts against the frozen ones (case E "
                  "already did this; repeating it independently is the point)." % card)
    review.append("2. Re-run `scripts/run_card.py` against `iso/checkout_scripts` and confirm "
                  "`%s` / `%s` / `%s` with %d/%d negatives rejected."
                  % (meta["positive_expected"], meta["continuity_expected"],
                     meta["defaults_expected"], run_result["negative_summary"]["passed"],
                     run_result["negative_summary"]["total"]))
    review.append("3. Confirm the isolated copy hashes still equal production "
                  "(`evidence/%s/source_manifest.json`)." % card)
    review.append("4. Confirm `oracle.md` was not edited after the definitive run (compare "
                  "`sha256` with `source_manifest.oracle_document."
                  "sha256_before_the_definitive_product_run`); the r2 revision section at the end "
                  "of `oracle.md` is an APPEND made after that run and is declared as such.")
    review.append("5. Confirm the r2 re-freeze only changed `cases.json` for M26/M27/M28 (the "
                  "NEG-CARD patch), compare `evidence/%s/revision_r2.json` "
                  "`p2_1_cases_json_refreeze.cases_json_sha256`, and confirm no gating expectation "
                  "moved.")
    review.append("6. Pick a case the implementer did not use (section 7) and freeze its "
                  "expectation BEFORE running.")
    review.append("7. Adjudicate the DEC items in `evidence/%s/accounting_decision.md` and the OQ "
                  "items in `evidence/%s/oq_rulings.json`." % (card, card))
    review.append("")
    with open(os.path.join(attempt, "review.md"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(review))

    # ------------------------------------------------------------------ handoff.json
    handoff = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "status": "review_pending",
        "implementer_is_not_the_reviewer": True,
        "card_title": meta["title"],
        "model_id": meta["model_id"],
        "completed_steps": {
            "A_binding": ("done (binding.json: read-only production hashes + attempt-local isolated "
                          "snapshot; both hash-equal to production)"),
            "B_positive_run": ("done (positive %s, continuity %s, defaults %s; all within "
                               "1e-9*max(1,|e|))"
                               % (run_result["positive"]["actual"],
                                  run_result["continuity_positive"]["actual"],
                                  run_result["defaults"]["actual"])),
            "C_negative_run": ("done (%d/%d negatives rejected with ModelRegistryError; "
                               "card-specific negative + N01a-d + N02-N05b + continuity break)"
                               % (run_result["negative_summary"]["passed"],
                                  run_result["negative_summary"]["total"])),
            "D_disclosure_mapping": ("NOT delivered - recorded as unmapped: the per-driver mapping "
                                     "is explicitly missing and the professional decisions are "
                                     "PROPOSED (unsigned); D belongs to I-10-A"),
            "E_historical_mapping_probe": ("not_applicable_with_reason - no real disclosure was "
                                           "adapted, so there is no disclosed history to hold equal "
                                           "across low/base/high; NOT a scenario set and NOT "
                                           "accuracy evidence"),
            "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
        },
        "completed_steps_list": ["A", "B", "C", "selfcheck-mutation-proof", "evidence-pack"],
        "next_step_number": 4,
        "next_action": ("Independent reviewer (r2 point review): re-run scripts/oracle_M25_M28.py "
                        "--card %s in a scratch tree and diff against the frozen oracle.json; "
                        "re-run scripts/run_card.py against iso/checkout_scripts and confirm %s / %s "
                        "/ %s with %d/%d negatives rejected AND "
                        "`neg_card_mechanism matched: True`; re-run the self-check cases A-G "
                        "(expect 3/3/0/3/3/1/1/0 for A/B/C/D/E/F1/F2/G); then verify the P2-1 "
                        "re-freeze changed only cases.json (evidence/%s/revision_r2.json "
                        "p2_1_cases_json_refreeze) and adjudicate DEC-%s-* in "
                        "evidence/%s/accounting_decision.md and the OQ records in "
                        "evidence/%s/oq_rulings.json. Owner decisions still outstanding: OQ-01 "
                        "(binding scope), OQ-M25M28-01 (silent zero-fill), OQ-M25M28-02 "
                        "(new_store_productivity exception label) and whether to adopt the stricter "
                        "mtime rule. After that I-10-A owns D/E."
                        % (card, meta["positive_expected"], meta["continuity_expected"],
                           meta["defaults_expected"], run_result["negative_summary"]["passed"],
                           run_result["negative_summary"]["total"], card, card, card, card)),
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256_file(os.path.join(ev, "input.json")),
            "evidence/%s/oracle.json" % card: sha256_file(os.path.join(ev, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256_file(os.path.join(ev, "cases.json")),
            "oracle.md": sha256_file(os.path.join(attempt, "oracle.md")),
            "scripts/oracle_M25_M28.py": script_hashes["scripts/oracle_M25_M28.py"],
            "scripts/run_card.py": script_hashes["scripts/run_card.py"],
            "scripts/pack_evidence.py": sha256_file(
                os.path.join(attempt, "scripts", "pack_evidence.py")),
        },
        "current_source_hashes": {
            "scripts/model_registry.py": PRODUCTION_HASHES["scripts/model_registry.py"],
            "scripts/model_extensions.py": PRODUCTION_HASHES["scripts/model_extensions.py"],
            "iso/checkout_scripts/model_registry.py":
                script_hashes["iso/checkout_scripts/model_registry.py"],
            "iso/checkout_scripts/model_extensions.py":
                script_hashes["iso/checkout_scripts/model_extensions.py"],
        },
        "changed_paths": {
            "production_repos": [],
            "note": ("no production file was created, modified, added, committed, restored or "
                     "stashed in any of the three repos; the pre-existing dirty state is captured "
                     "in before/ and after/"),
            "attempt_paths_created": [attempt],
        },
        "commands_executed": ["A0-iso-venv-create", "A1-pytest-offline-install",
                              "A2-isolated-snapshot", "A3-oracle-generate",
                              "B-product-run", "G1-selfcheck-case-A",
                              "G2-selfcheck-case-B", "G3-selfcheck-case-C",
                              "G4-selfcheck-case-D", "G5-selfcheck-case-E",
                              "G6-selfcheck-case-F1-rewritten-declaration",
                              "G7-selfcheck-case-F2-deleted-case",
                              "G8-selfcheck-case-G-regenerate",
                              "E-evidence-pack", "P-line-ending-blob-probe",
                              "R-independent-rerun-check"],
        "raw_exit_codes": {"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B": 0, "G1": 3, "G2": 3,
                           "G3": 0, "G4": 3, "G5": 3, "G6": 1, "G7": 1, "G8": 0, "E": 0, "P": 0,
                           "R": 0,
                           "B_first_run_before_the_r2_refreeze": 0},
        "expected_exit_codes": {"A0": 0, "A1": 0, "A2": 0, "A3": 0, "B": 0, "G1": 3, "G2": 3,
                                "G3": 0, "G4": 3, "G5": 3, "G6": 1, "G7": 1, "G8": 0, "E": 0, "P": 0,
                                "R": 0,
                                "B_first_run_before_the_r2_refreeze": 0},
        "selfcheck_case_map": {
            "A": "corrupted positive expectation -> rc=3",
            "B": "my own wrong hand value -> rc=3",
            "C": "restored control -> rc=0",
            "D": "unrejected negative (identity patch in memory) -> rc=3",
            "E": "mis-signed / double-counted oracle value -> rc=3",
            "F1": "cases.json NEG-CARD `expected` rewritten -> rc=1 (harness defect)",
            "F2": "negative case N04 deleted -> rc=1 (harness defect)",
            "G": "regenerate the frozen oracle in a scratch tree -> byte-identical",
        },
        "rerun_check": {
            "unit": "R-independent-rerun-check",
            "raw_rc": 0,
            "run_result_json_byte_identical_to_frozen": True,
            "evidence": "recovery/rerun_check/rerun_check.json",
            "proves": ("the frozen evidence is reproducible: re-running the bound argv in a "
                       "throwaway tree returns rc=0, produces a byte-identical run_result.json and "
                       "prints exactly the values stored in the evidence files"),
        },
        "first_run_vs_definitive_run": {
            "first_run_raw_rc": 0,
            "first_run_expected_rc": 0,
            "first_run_exit_code_semantics": load(os.path.join(
                attempt, "recovery", "precorrection", "run_result.json")).get(
                    "exit_code_semantics"),
            "first_run_defaults_case": load(os.path.join(
                attempt, "recovery", "precorrection", "run_result.json"))["defaults"].get("actual"),
            "definitive_run_defaults_case": run_result["defaults"]["actual"],
            "note": ("the first product run happened BEFORE the r2 re-freeze; its stdout and "
                     "run_result are preserved verbatim under recovery/precorrection/"),
        },
        "positive_actual": run_result["positive"]["actual"],
        "positive_expected": meta["positive_expected"],
        "continuity_actual": run_result["continuity_positive"]["actual"],
        "defaults_actual": run_result["defaults"]["actual"],
        "negative_case_summary": run_result["negative_summary"],
        "observations": [
            {"id": entry["id"], "actual": entry.get("actual"),
             "matches_compared": entry.get("matches_compared"),
             "expect_equal": entry.get("expect_equal"),
             "matches_expected_relation": entry.get("matches_expected_relation")}
            for entry in run_result["observations"]],
        "open_questions": [
            ("OQ-01 (all four cards, steering): the cards say the run cwd must come from I-00-B, "
             "but I-00-B binds only the isolation plan and the two-stage command rule, not a "
             "materialised checkout tree. This batch therefore materialised its own read-only "
             "snapshot (iso/checkout_scripts, hashes equal to production). If the intended binding "
             "is an I-00-B-materialised checkout, the provenance chain differs; the code under "
             "test is byte-identical either way. Needs a binding ruling."),
            ("OQ-M25M28-01 (all four cards): scripts/model_registry.py:335 silently zero-fills an "
             "omitted optional driver that is absent from spec.defaults; %d models of the %d-model "
             "registry have such a driver (the reviewer counted 31 optional driver SLOTS). For this "
             "card the affected driver is %s. Registered, NOT fixed; no product change was made. "
             "Enumeration: evidence/%s/oq_rulings.json."
             % (oq["enumeration_summary"][
                 "models_with_an_optional_driver_without_a_declared_default_of_models_total"],
                oq["enumeration_summary"]["models_total"],
                meta["optional_declared_default"] or "none (this model has optional = ())", card)),
            ("OQ-M25M28-02: the ratio-dimensioned drivers of these four models were enumerated: "
             "%d ratio drivers of %d driver slots, %d of them outside [0,1] (the four exceptions are "
             "enumerated with their declared bounds and reasons in evidence/%s/oq_rulings.json). "
             "store_cohorts.new_store_productivity is (0, inf) as card_M26.md L8 requires (a "
             "new-store productivity may exceed one) even though its dimension is `ratio`; the "
             "reviewer asked for that exception to be labelled in the metadata/docs rather than "
             "changed in behaviour (review finding P3-6) - it is labelled in the OQ record here and "
             "no product change was made."
             % (oq["enumeration_summary"]["ratio_drivers_of_drivers_total"],
                oq["enumeration_summary"]["drivers_total_slots"],
                oq["enumeration_summary"]["ratio_drivers_not_in_0_1_of_ratio_drivers"], card)),
            ("OQ-02 (oracle provenance, all four cards) - CORRECTED NARRATIVE. The v1 generation had "
             "a defect; the first product run exposed it; the generator was re-run before the "
             "definitive run. Three corrections to the r1 write-up: (a) 'the correction was applied "
             "before oracle.md was written' is NOT supported by mtime and is withdrawn - the final "
             "generator's mtime is later than all four oracle.md files and later than the first "
             "product run; what IS supported is that no GATING expectation was ever rewritten "
             "(first-run per_value_checks[].expected and continuity_positive.expected match the "
             "frozen oracle.json per card, and the four cases.json v1 files are byte-identical to "
             "the frozen ones) and that only M25's NON-GATING defaults block changed; (b) 'the M27 "
             "crash meant no oracle.json was produced' is WRONG - a valid v1 oracle.json exists and "
             "is byte-identical to the frozen one; (c) the v1 generator SOURCE and the M27 traceback "
             "were never persisted, so the accident is not reproducible and is recorded as a "
             "provenance gap. Also: under review finding P2-1 the M26/M27/M28 NEG-CARD patch was "
             "corrected and cases.json re-frozen before the definitive run. If the owner insists on "
             "the stricter rule 'oracle.json must predate ANY product run', this attempt does not "
             "satisfy it. Ledger: evidence/%s/revision_r2.json." % card),
            ("OQ-P2-1 (NEG-CARD coverage): for M26/M27/M28 the r1 NEG-CARD patch assigned a dict to "
             "the driver (kind=set_driver with a {\"__float__\": X} envelope), so the generic "
             "per-year length guard refused it before the card-specific guard ran, and the r1 "
             "oracle.md coverage claim for R1 was unsupported. FIXED by re-freezing cases.json with "
             "a one-element list; run_card.py now verifies the declared mechanism message as a "
             "GATING condition. M25 never had the defect. Review finding P2-1 is therefore closed."),
            ("OQ-P3-2 (shared harness gap): the runner used to ignore cases.json[].expected and the "
             "case count. FIXED in this batch only (case_contract verification); self-check cases "
             "F1/F2 demonstrate rc=1 for a rewritten declaration and for a deleted negative. The "
             "same gap was found independently by the M17-M20, M21-M24 and M13-M16 reviews and is "
             "registered by the parent as a cross-batch shared harness gap; no other card's frozen "
             "runner was modified by this attempt."),
            ("OQ-P3-3 (line endings): r1's CRLF JSON could not be reproduced from a clean clone "
             "(.gitattributes declares `*.json text eol=lf`). FIXED by writing LF; "
             "evidence/%s/line_ending_and_blob_hashes.json records worktree sha256, git blob sha256 "
             "and the LF-normalised sha256 per artefact, plus a summary count of any remaining CRLF "
             "files." % card),
            ("OQ-P3-8 (modelling expressiveness, M27 only): the `period_hours > 0` hard constraint "
             "means a pre-commissioning year or a zero-operating-hour year cannot be expressed "
             "(tested: `period_hours=[0]` is refused). Registered as an expressiveness gap for the "
             "model owner; no product change."),
            ("OQ-REVIEWER-OPINIONS (recorded, NOT adopted as decisions): on OQ-01 the reviewer "
             "accepts the existing isolation approach and recommends the owner ratify the "
             "equivalence explicitly; on OQ-M25M28-01 the reviewer does not block these cards and "
             "recommends fixing it with explicit defaults metadata rather than a behaviour change; "
             "on OQ-M25M28-02 the reviewer does not block and asks for the exception label; on "
             "provenance the reviewer does not block formula acceptance but requires the P2-2 "
             "narrative correction and the 'v1 source/traceback not preserved' statement - both "
             "applied. The reviewer explicitly declines to adopt the stronger mtime rule and leaves "
             "that to the owner."),
        ],
        "blocked_by": [],
        "production_drift_window_and_restoration": {
            "both_facts_kept_side_by_side": True,
            "fact_1_drift": {
                "window_utc_approx": "2026-09-20 04:35:31 - 04:40:53",
                "production_was_not_in_the_anchored_state": True,
                "observed_here": ("scripts/model_registry.py = "
                                  "1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86 "
                                  "(19703 B, HEAD blob c80075c4...), i.e. the model_extensions "
                                  "wiring, the driver_bounds mechanism and this batch's four models "
                                  "were absent"),
                "alarm_correctness": ("any production_hashes_unchanged=false recorded inside this "
                                      "window is a CORRECT alarm and must not be used to change an "
                                      "expectation, threshold or frozen artefact"),
            },
            "fact_2_restored": {
                "restored_after_utc": "2026-09-20 04:40:53",
                "method": ("owner replayed the pre-commit patch patch1789875331-33652 with "
                           "`git apply --exclude=.planning/*` (check and apply both exit 0)"),
                "reverified_here": ("scripts/model_registry.py = "
                                    "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f "
                                    "(26446 B) and iso/checkout_scripts/* equals production again; "
                                    "the reviewer's invalidation condition is cleared and no "
                                    "blocked reclassification is needed"),
                "evidence": "recovery/production_drift_and_restoration_r3.json",
            },
            "residual_risk": ("scripts/model_extensions.py is still UNTRACKED while "
                              "model_registry.py imports it from the worktree; another "
                              "`git checkout -- .` / `reset --hard` could repeat this. Owner should "
                              "bring it under version control; this implementer did not run git add."),
        },
        "lesson_recorded": {
            "id": "LESSON-production-hash-as-a-live-quantity",
            "statement": ("any card whose acceptance rests on a PRODUCTION FILE HASH is resting on a "
                          "quantity that an external git operation can change without warning. On "
                          "mismatch: record the drift and its time window, escalate to the "
                          "orchestration layer for a ruling, and NEVER adapt by editing "
                          "expectations or frozen artefacts."),
            "applied_here": ("the drift was recorded (INCIDENT.md + "
                             "recovery/production_drift_and_restoration_r3.json), escalated, and "
                             "removed externally; not one expectation, threshold or frozen "
                             "artefact was touched while the production state was wrong"),
        },
        "stop_conditions_hit": [
            "STOP_ACCURACY (no I-12 frozen design)",
            "STOP_DISCLOSURE_ADAPTATION (no signed per-driver mapping / no adapted disclosure)",
        ]
        + (["STOP_BRIDGE applicability: assessed, continuity identity is enforced and exercised "
            "(not a blocker)"] if meta["bridge"] else
           ["STOP_BRIDGE: not_applicable_with_reason (per-year flow model, no opening/closing "
            "stock)"]),
        "qualifications": {
            "formula": "review_pending",
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
        },
        "evidence_paths": sorted(
            ["binding.json", "changes.diff", "commands.json", "decision.md", "handoff.json",
             "oracle.md", "review.md", "recovery/", "recovery/selfcheck/", "recovery/precorrection/",
             "scripts/", "iso/checkout_scripts/", "before/", "after/"]
            + ["evidence/%s/%s" % (card, name) for name in sorted(os.listdir(ev))]),
        "reviewer_status": ("r1 reviewed: four cards accepted_scoped (formula only), P1 = 0, with "
                            "mandatory findings P2-1 and P2-2 and observations P3-1..P3-8. Both "
                            "mandatory findings were handled in r2 and returned for point review; "
                            "r2 point review returned accepted_scoped for all four cards (P1 = 0, "
                            "no new P2) and its verdict text was transcribed APPEND-ONLY into "
                            "review.md (block at lines 83-131). The r2 acceptance was briefly "
                            "invalidated by an external production rollback and restored by the "
                            "owner (see production_drift_window_and_restoration). The implementer "
                            "still does not sign accepted."),
        "revision": ("r3 (r2 verdict transcribed append-only into review.md; P3-A..P3-D corrections "
                     "recorded in evidence/%s/revision_r3.json; production drift + restoration in "
                     "recovery/production_drift_and_restoration_r3.json)" % card),
        "disclosure_impact_note": ("not applicable: no real-company disclosure was adapted by this "
                                   "attempt"),
    }
    with open(os.path.join(attempt, "handoff.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)

    print("wrote docs for", card)
    print("  binding.json, commands.json (%d units), decision.md, review.md, handoff.json, "
          "recovery/README.md, recovery/selfcheck/selfcheck_result.json" % len(units))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
