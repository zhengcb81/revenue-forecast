"""!!! STALE SOURCE WARNING (bounded-text pass, 2026-09-20T03:38:51.970887+00:00) !!!

This file already ran for attempt a20260919-01.  It is kept for provenance and for the record
of HOW the evidence was produced, but it MUST NOT be re-run against this attempt:

  * re-running it would rewrite evidence/<CARD>/source_manifest.json from values measured now,
  * and the pack's own oracle_document wording was corrected after the independent reviewer
    found the original freshness wording self-contradictory (finding F-04 / residual R-4), so a
    re-run would re-emit corrected wording over an attempt whose evidence was already sealed.

The sealed evidence under evidence/<CARD>/ is the record; scripts/verify_remediation.py is the
read-only re-check; recovery/remediation_r2.json and the errata section of oracle.md list what
was corrected.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

CARDS = {"M29": "commercial_launch", "M30": "finite_adoption",
         "M31": "inventory_sellthrough"}

NEXT_CARD = {"M29": "M30", "M30": "M31", "M31": "I-10-A"}


def sha256(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")

    run_result = load(os.path.join(evidence, "run_result.json"))
    oracle = load(os.path.join(evidence, "oracle.json"))
    cases = load(os.path.join(evidence, "cases.json"))
    mutation = load(os.path.join(evidence, "mutation_selfcheck.json"))
    regen = load(os.path.join(evidence, "oracle_regen_proof.json"))
    enumeration = load(os.path.join(evidence, "registry_enumeration.json"))
    binding = load(os.path.join(attempt, "binding.json"))
    commands = load(os.path.join(attempt, "commands.json"))
    pipeline = load(os.path.join(attempt, "pipeline_run.json"))
    source_manifest = load(os.path.join(evidence, "source_manifest.json"))

    rc_by_unit = {}
    for unit in commands.get("units", []):
        rc_by_unit[unit["unit_id"]] = {"raw_rc": unit.get("raw_rc"),
                                       "expected_rc": unit.get("expected_rc")}
    for unit in pipeline.get("units_run", []):
        rc_by_unit.setdefault(unit["unit_id"], {"raw_rc": unit["raw_rc"],
                                                "expected_rc": unit["expected_rc"]})

    exit_code = run_result.get("exit_code")
    status = "review_pending" if exit_code == 0 else (
        "blocked_no_verdict" if exit_code == 2 else (
            "blocked_harness_error" if exit_code == 1 else "stop_formula"))

    completed = []
    for unit_id in ("A0-iso-venv-record", "A1-isolated-snapshot", "A2-oracle-freeze-and-generate",
                    "A3-write-binding", "B-product-run", "C-registry-enumeration",
                    "C2-extra-boundary-probes", "D-oracle-regen-verify", "E-mutation-selfcheck",
                    "G1-state-after", "F-write-commands", "G-pack-evidence",
                    "H-write-handoff", "H2-write-closing-docs", "Z-close-attempt"):
        entry = rc_by_unit.get(unit_id)
        completed.append({"step": unit_id,
                          "raw_rc": None if entry is None else entry["raw_rc"],
                          "expected_rc": None if entry is None else entry["expected_rc"],
                          "done": bool(entry and entry["raw_rc"] == entry["expected_rc"])})
    self_reference = ("Z-close-attempt writes the command record that contains its own entry, so its "
                      "raw_rc in commands.json is null by construction (a command cannot record its "
                      "own return code before returning); its actual raw code is in "
                      "evidence/%s/runs/Z-close-attempt/rc.json and in closing_run.json" % card)
    commands_note = ("commands.json is written in phase 'final' by the Z-close-attempt unit AFTER this "
                     "handoff; the raw_rc values below are therefore the values recorded by the "
                     "phase-'post' record for every unit up to G-pack-evidence, and null for the "
                     "closing units. The authoritative final record is commands.json (phase final) "
                     "plus closing_run.json")

    handoff = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": CARDS[card],
        "status": status,
        "implementer_is_not_the_reviewer": True,
        "signed_by": "nobody: the implementer never writes 'accepted'; an independent reviewer does",
        "objective_of_this_card": ("M29/M30/M31 A-C formula qualification only: freeze the "
                                   "expectations independently, run the single product entry point, "
                                   "reject every negative, prove the oracle is regenerable and that "
                                   "the runner goes red before green"),
        "completed_steps": completed,
        "next_step_number": 4,
        "next_action": ("an independent reviewer reads binding.json, oracle.md, commands.json, "
                        "evidence/%s/*.json and review.md, recomputes the positive/continuity "
                        "expectations by hand from card_%s.md, replays at least one negative case and "
                        "the mutation self-check against the same code_root, and either writes "
                        "accepted_scoped (formula qualification only) or changes_required; the "
                        "implementer must not pre-empt that verdict" % (card, card)),
        "next_card_in_the_series": NEXT_CARD[card],
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256(os.path.join(evidence, "input.json")),
            "evidence/%s/oracle.json" % card: sha256(os.path.join(evidence, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256(os.path.join(evidence, "cases.json")),
        },
        "current_source_hashes": {
            "iso/checkout_scripts/model_registry.py": sha256(os.path.join(code_root,
                                                                         "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha256(os.path.join(code_root,
                                                                           "model_extensions.py")),
            "scripts/oracle_%s.py" % card: sha256(os.path.join(attempt, "scripts",
                                                               "oracle_%s.py" % card)),
            "scripts/run_card.py": sha256(os.path.join(attempt, "scripts", "run_card.py")),
        },
        "production_source_hashes": binding["production_source_hashes"],
        "changed_paths": [],
        "changed_paths_statement": ("this attempt changed no product file; it wrote only inside "
                                    + attempt),
        "commands_executed": [{"unit_id": unit["unit_id"], "argv": unit["argv"],
                              "expected_rc": unit["expected_rc"], "raw_rc": unit.get("raw_rc")}
                             for unit in commands.get("units", [])],
        "raw_exit_codes": rc_by_unit,
        "raw_exit_codes_note": commands_note,
        "self_reference_note": self_reference,
        "expected_exit_codes": {unit: info["expected_rc"] for unit, info in rc_by_unit.items()},
        "runner_exit_code": exit_code,
        "runner_verdict": run_result.get("verdict"),
        "negative_summary": run_result.get("negative_summary"),
        "frozen_positive_expected": oracle["positive"]["expected_float"],
        "frozen_positive_actual": run_result.get("positive", {}).get("actual"),
        "continuity_expected": oracle["continuity_positive"]["expected_float"],
        "continuity_actual": run_result.get("continuity_positive", {}).get("actual"),
        "oracle_regenerable_byte_for_byte": regen.get("all_byte_identical"),
        "mutation_selfcheck_red_then_green": mutation.get(
            "all_mutations_produced_the_expected_exit_code"),
        "frozen_evidence_unchanged_by_mutation_selfcheck": mutation.get(
            "frozen_evidence_unchanged"),
        "enumeration_counts": enumeration["totals"],
        "open_questions": [
            {"id": "OQ-01", "title": "isolation binding provenance (batch-wide)",
             "requires_ruling_from": "owner (dispatch/binding)",
             "evidence": "evidence/%s/oq_rulings.json" % card},
            {"id": "OQ-02", "title": ("no optional driver and no default in these three models, so the "
                                      "silent zero-fill path is unreachable through them"),
             "requires_ruling_from": "independent reviewer", "evidence":
             "evidence/%s/oq_rulings.json + registry_enumeration.json" % card},
            {"id": "OQ-03", "title": "card business negative the calculator cannot fully enforce",
             "requires_ruling_from": "industry/accounting reviewer (I-10-A / D)",
             "evidence": "evidence/%s/oq_rulings.json" % card},
            {"id": "OQ-04", "title": "numerical domain / boundary observations of this model",
             "requires_ruling_from": "independent reviewer",
             "evidence": "evidence/%s/oq_rulings.json + extra_probes.json + binding.json" % card},
            {"id": "OQ-05", "title": "oracle.md's present mtime is a post-hoc value and is NOT pre-run "
                                     "evidence (measured: oracle_md_mtime < product_stdout_mtime)",
             "requires_ruling_from": "independent reviewer (accept the recorded freshness claim or "
                                     "demand a fresh attempt)",
             "evidence": "evidence/%s/source_manifest.json oracle_document.freshness_claim" % card},
        ],
        "blocked_by": [],
        "evidence_paths": {
            "binding": "binding.json",
            "oracle_document": "oracle.md",
            "oracle_frozen": "evidence/%s/oracle.json" % card,
            "positive_and_negatives": "evidence/%s/run_result.json" % card,
            "negatives": "evidence/%s/negative_results.json" % card,
            "formula_result": "evidence/%s/formula_result.json" % card,
            "stdout": "evidence/%s/stdout.txt" % card,
            "stderr": "evidence/%s/stderr.txt" % card,
            "registry_enumeration": "evidence/%s/registry_enumeration.json" % card,
            "extra_probes": "evidence/%s/extra_probes.json" % card,
            "oracle_regen_proof": "evidence/%s/oracle_regen_proof.json" % card,
            "mutation_selfcheck": "evidence/%s/mutation_selfcheck.json" % card,
            "qualification": "evidence/%s/qualification.json" % card,
            "oq_rulings": "evidence/%s/oq_rulings.json" % card,
            "integrity": "evidence/%s/integrity.json" % card,
            "revision_r2": "evidence/%s/revision_r2.json" % card,
            "source_manifest": "evidence/%s/source_manifest.json" % card,
            "command_manifest": "evidence/%s/command_manifest.json" % card,
            "evidence_hashes": "evidence/%s/evidence_hashes.json" % card,
            "commands": "commands.json",
            "pipeline_run": "pipeline_run.json",
            "review": "review.md",
            "decision": "decision.md",
            "recovery": "recovery/README.md",
            "final_hashes": "after/final_deliverable_hashes.json",
        },
        "reviewer_status": "not_reviewed (implementer cannot self-sign)",
        "qualification_state": {
            "formula": status,
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
        },
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generated_by": ("scripts/write_handoff.py, from the evidence files on disk; no field is "
                         "transcribed from prose"),
    }
    out = os.path.join(attempt, "handoff.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)
    print("handoff written", out)
    print("status", status, "runner exit_code", exit_code,
          "negatives", run_result.get("negative_summary", {}).get("passed"),
          "/", run_result.get("negative_summary", {}).get("total"))
    print("next_action:", handoff["next_action"][:120], "...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
