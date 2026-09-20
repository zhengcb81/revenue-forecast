"""Generate handoff.json for one attempt from the evidence actually on disk.

Nothing here is transcribed by hand: hashes come from the evidence files, exit codes come
from the rc records, and the open questions come from oq_rulings.json.

Usage:
  python -X utf8 -B write_handoff.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

import card_units

# Per-card, accurate pass history (see process_history.json for the full record and the gaps).
PROCESS = {
    "M17": {
        "measurement_executions": 3,
        "closing_executions": 7,
        "c2_origin": ("a unit ADDED during this attempt after measurement pass 1 (it did not exist in "
                      "the first pass)"),
        "detail": ("pass 1 = 13 units before C2 existed; pass 2 = 14 units with the probe constant "
                   "still 105.0; pass 3 = 14 units after it was corrected to 90.0. The post-review "
                   "fixes re-executed B, C2, E and the pack for this card once more."),
    },
    "M18": {
        "measurement_executions": 1,
        "closing_executions": 7,
        "c2_origin": ("an EXISTING unit of this attempt's unit list, delivered byte-identically from "
                      "the M17 attempt (it was not added after a first pass)"),
        "detail": ("the single measurement pass ran 14 units; the post-review fixes re-executed B, C2, "
                   "E and the pack for this card once more."),
    },
}
PROCESS["M19"] = {**PROCESS["M18"]}
PROCESS["M20"] = {**PROCESS["M18"]}



def atomic_dump(path, doc):
    """Write JSON through a temp file + os.replace so an interrupted write cannot truncate it."""
    tmp = path + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    info = card_units.CARDS[card]
    evidence = os.path.join(attempt, "evidence", card)

    run = load(os.path.join(evidence, "run_result.json"))
    oracle = load(os.path.join(evidence, "oracle.json"))
    oq = load(os.path.join(evidence, "oq_rulings.json"))
    mutation = load(os.path.join(evidence, "mutation_selfcheck.json"))
    regen = load(os.path.join(evidence, "oracle_regen_proof.json"))
    probes = load(os.path.join(evidence, "extra_probes.json"))
    commands = load(os.path.join(attempt, "commands.json"))
    qualification = load(os.path.join(evidence, "qualification.json"))
    source_manifest = load(os.path.join(evidence, "source_manifest.json"))

    raw_codes = {u["unit_id"]: u["raw_rc"] for u in commands["units"]}
    expected_codes = {u["unit_id"]: u["expected_rc"] for u in commands["units"]}
    product_rc = raw_codes.get("B-product-run")

    open_questions = []
    for ruling in oq["rulings"]:
        open_questions.append("%s (%s) - %s; status=%s; requires_ruling_from=%s"
                              % (ruling["id"], ruling["title"], ruling.get("finding",
                                 ruling.get("observation", "")), ruling["status"],
                                 ruling["requires_ruling_from"]))
    process_note = (
        "OQ-05 (process, per card, parameterised after independent review P2-2): THIS card's "
        "measurement pipeline was executed %s time(s) and the closing sequence was executed %s times. "
        "The C2 extra-boundary-probe unit is %s. Superseded executions rewrote the same files, so the "
        "byte-level records only prove the LAST execution of each unit; the declared pass structure "
        "and the honest gaps are in process_history.json, and review.md states the same facts for this "
        "card. The frozen oracle expectations were never modified by any later pass"
        % (PROCESS[card]["measurement_executions"],
           PROCESS[card]["closing_executions"],
           PROCESS[card]["c2_origin"]))
    open_questions.append(process_note)

    doc = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": info["model_id"],
        "card_title": info["title"],
        "status": "review_pending",
        "implementer_is_not_the_reviewer": True,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "completed_steps": {
            "A_binding": ("done - binding.json binds the attempt-local interpreter, the read-only "
                          "isolated snapshot, the model contract read back from that snapshot and the "
                          "write allowlist"),
            "B_positive_run": ("done - positive %s vs independent oracle %s; continuity %s vs %s; "
                               "defaults %s vs %s (defaults are recorded, not gating)"
                               % (run["positive"].get("actual"),
                                  oracle["positive"]["expected_float"],
                                  run["continuity_positive"].get("actual"),
                                  oracle["continuity_positive"]["expected_float"],
                                  run["defaults"].get("actual"),
                                  run["defaults"].get("expected"))),
            "C_negative_run": ("done - %s/%s negatives rejected with ModelRegistryError; each case ran "
                               "on a fresh in-memory deepcopy"
                               % (run["negative_summary"]["passed"], run["negative_summary"]["total"])),
            "D_disclosure_mapping": ("NOT done - the card marks D [professional_decision_required]; no "
                                     "disclosure mapping, accounting_decision.md, historical_"
                                     "reconciliation.json or forecast_integration.json was produced. "
                                     "The card states these do not block the A-C formula dispatch and "
                                     "must not be filled in speculatively"),
            "E_historical_mapping_probe": ("NOT done - E is [executable_after_D] and belongs to the "
                                           "I-10-A鍏堣 work; inventing a probe here would be a "
                                           "fabricated scenario set"),
            "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
        },
        "completed_steps_list": ["A", "B", "C"],
        "next_step_number": 4,
        "next_action": ("Independent reviewer: re-run scripts/run_card.py against the isolated snapshot "
                        "and compare with evidence/%s/run_result.json (positive %s, continuity %s, "
                        "negatives %s/%s, raw rc %s), then adjudicate the entries in "
                        "evidence/%s/oq_rulings.json. After that, the FIRST unfinished card action is "
                        "step D, which needs a professional (industry/accounting) decision before any "
                        "mapping may be written; step E then depends on I-10-A."
                        % (card, run["positive"].get("actual"),
                           run["continuity_positive"].get("actual"),
                           run["negative_summary"]["passed"], run["negative_summary"]["total"],
                           product_rc, card)),
        "input_hashes": {
            "evidence/%s/input.json" % card: sha256(os.path.join(evidence, "input.json")),
            "evidence/%s/oracle.json" % card: sha256(os.path.join(evidence, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256(os.path.join(evidence, "cases.json")),
            "oracle.md": sha256(os.path.join(attempt, "oracle.md")),
            "scripts/oracle_%s.py" % card: sha256(os.path.join(attempt, "scripts",
                                                               "oracle_%s.py" % card)),
            "scripts/run_card.py": sha256(os.path.join(attempt, "scripts", "run_card.py")),
        },
        "current_source_hashes": {
            "scripts/model_registry.py": source_manifest[
                "production_source_hashes_at_binding_and_after_run"]["scripts/model_registry.py"],
            "scripts/model_extensions.py": source_manifest[
                "production_source_hashes_at_binding_and_after_run"]["scripts/model_extensions.py"],
            "iso/checkout_scripts/model_registry.py": source_manifest["isolated_copy_hashes"][
                "iso/checkout_scripts/model_registry.py"],
            "iso/checkout_scripts/model_extensions.py": source_manifest["isolated_copy_hashes"][
                "iso/checkout_scripts/model_extensions.py"],
        },
        "changed_paths": {
            "production_repos": [],
            "note": ("no production file was created, modified, added, committed, restored or stashed "
                     "in any of the three repos; the pre-existing dirty state is captured in before/ "
                     "and after/"),
            "attempt_paths_created": [attempt],
            "other_attempts_created_or_overwritten": [],
        },
        "commands_executed": [u["unit_id"] for u in commands["units"]],
        "raw_exit_codes": raw_codes,
        "expected_exit_codes": expected_codes,
        "product_run_returncode": product_rc,
        "positive_actual": run["positive"].get("actual"),
        "positive_expected": oracle["positive"]["expected_float"],
        "continuity_actual": run["continuity_positive"].get("actual"),
        "defaults_actual": run["defaults"].get("actual"),
        "negative_case_summary": run["negative_summary"],
        "observation_summary": [{"id": o["id"], "raised": o.get("raised"), "actual": o.get("actual"),
                                 "matches_expected": o.get("matches_expected"),
                                 "matches_compared": o.get("matches_compared")}
                                for o in run["observations"]],
        "extra_boundary_probes": [{"id": p["id"], "raised": p.get("raised"), "actual": p.get("actual"),
                                   "gating": False} for p in probes["probes"]],
        "mutation_selfcheck": {
            "runs": [{"label": r["label"], "raw_rc": r["raw_returncode"],
                      "expected_rc": r["expected_rc"], "verdict": r["verdict_in_result_file"]}
                     for r in mutation["runs"]],
            "frozen_evidence_unchanged": mutation["frozen_evidence_unchanged"],
            "red_then_green": mutation["all_mutations_produced_the_expected_exit_code"],
        },
        "oracle_regeneration_byte_identical": regen["all_byte_identical"],
        "negative_declared_expectation_enforcement": {
            "declared_expectations_in_cases_json": run["negative_summary"].get(
                "declared_expectations_in_cases_json"),
            "comparison": run["negative_summary"].get("declared_expectation_comparison"),
            "declared_expectation_mismatches": run["negative_counts"].get(
                "declared_expectation_mismatch"),
            "runner_sha256": sha256(os.path.join(attempt, "scripts", "run_card.py")),
            "independent_review_basis": ("independent review P2-1: the previous runner did not compare "
                                         "cases.json's per-case 'expected'; this runner compares the "
                                         "raised exception's exact type name and refuses the case on "
                                         "mismatch (never by isinstance, because ModelRegistryError "
                                         "is a ValueError subclass)"),
        },
        "open_questions": open_questions,
        "blocked_by": [],
        "stop_conditions_hit": [
            "STOP_DISCLOSURE_ADAPTATION (no disclosure mapping; professional decision not taken)",
            "STOP_ACCURACY (no I-12 frozen design)",
        ],
        "qualifications": {
            "formula": qualification["formula"]["state"],
            "disclosure_adaptation": qualification["disclosure_adaptation"]["state"],
            "accuracy": qualification["accuracy"]["state"],
        },
        "qualification_semantics": {
            "disclosure_adaptation_unmapped_means": ("ZERO output, not partial progress: no "
                                                     "disclosure_mapping.json, no accounting_decision.md, "
                                                     "no historical_reconciliation.json and no "
                                                     "forecast_integration.json exist for this card"),
            "accuracy_unproven_means": ("no I-12 frozen design exists, so no out-of-sample evaluation "
                                        "was run at all; the formula pass must never be read as "
                                        "accuracy evidence"),
        },
        "evidence_paths": sorted(
            os.path.relpath(os.path.join(root, name), attempt).replace("\\", "/")
            for root, _dirs, files in os.walk(evidence) for name in files),
        "reviewer_status": ("r1 reviewed by an independent session; verdict accepted_scoped (formula "
                            "qualification only). The implementer has NOT signed anything as accepted. "
                            "Post-review P2/P3 dispositions are recorded in review.md (r2 section) and "
                            "the batches' rc/qualification semantics in the batch handoff. formula "
                            "remains review_pending until the reviewer confirms the r2 fixes."),
        "process_history_pointer": "process_history.json",
        "process_history_summary": {
            "measurement_pipeline_executions_declared": PROCESS[card]["measurement_executions"],
            "closing_executions_declared": PROCESS[card]["closing_executions"],
            "c2_unit_origin": PROCESS[card]["c2_origin"],
            "detail": PROCESS[card]["detail"],
            "observed_records_prove": "only the LAST execution of each unit (see process_history.json)",
        },
        "batch_handoff_pointer": ("../M17-M20/a20260919-01/batch_handoff.md and "
                                  "../M17-M20/a20260919-01/rc_namespace.json (dedicated batch-level "
                                  "documentation; contains no card artefacts)"),
        "revision": ("r2" if load(os.path.join(evidence, "revision_r2.json")).get("r2_append_performed")
                     else "r1"),
    }
    out = os.path.join(attempt, "handoff.json")
    atomic_dump(out, doc)
    print("handoff written", out)
    print("status", doc["status"], "next_step_number", doc["next_step_number"])
    print("positive", doc["positive_actual"], "negatives", doc["negative_case_summary"])
    print("raw codes", json.dumps(raw_codes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
