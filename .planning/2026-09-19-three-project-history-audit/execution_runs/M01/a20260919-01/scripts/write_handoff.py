"""Generate handoff.json for the four M cards with the required field set.

Fields per review_and_handoff.md: card_id, attempt_id, status, completed_steps,
next_step_number, next_action, input_hashes, current_source_hashes,
changed_paths, commands_executed, raw_exit_codes, expected_exit_codes,
open_questions, blocked_by, evidence_paths, reviewer_status.

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import json
import os

PLAN = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast", ".planning",
                    "2026-09-19-three-project-history-audit")

CARDS = {
    "M01": {
        "model": "direct_growth",
        "next_action": ("Independent reviewer: re-run scripts/oracle_M01.py, then re-run scripts/run_card.py "
                        "against iso/checkout_scripts and confirm the recorded positive [220,110,0], the 11 "
                        "rejected negatives, and the frozen-source hashes; then decide whether the ZJ "
                        "FY2024->FY2025 14.96% single-rate probe is admissible as a historical_mapping_probe. "
                        "After that, I-10-A owns D/E for this model."),
        "open_questions": [
            "SR-M01-A: is the FY2025 comparative of FY2024 on the same PRC ASBE basis as the FY2024 report's own figure? (checked identical here, reviewer to confirm)",
            "SR-M01-B: for a cyclical miner, may direct_growth ever be the 'short-term fallback for a mature stable business'?",
            "SR-M01-C: confirm the zero-base commercialisation wording is a business refusal, not a runtime case.",
            "Is the I-00-B interpretation used here (attempt-local isolated snapshot because I-00-B binds only the isolation plan) the intended binding, or must the snapshot come from an I-00-B-materialised checkout?",
        ],
        "blocked_by": [],
    },
    "M02": {
        "model": "direct_revenue",
        "next_action": ("Independent reviewer: re-run scripts/oracle_M02.py and scripts/run_card.py, confirm "
                        "positive [80,0,120], the 11 rejected negatives and the base-independence observation, "
                        "then rule on DEC-M02-3 (should an ignored base_revenue still be domain-checked) and on "
                        "whether a constructive zero residual can ever satisfy the card's reconciliation "
                        "requirement (implementer says no). Then I-10-A owns D/E."),
        "open_questions": [
            "DEC-M02-2: can direct_revenue earn a disclosure adaptation without an independent revenue estimate, given the reconciliation is an identity?",
            "DEC-M02-3: current behaviour rejects a negative base_revenue even though the formula ignores it. Keep fail-closed (A) or ignore unused fields (B)?",
            "SR-M02-B: for an IFRS 17 insurer, is direct_revenue admissible at all before the CSM/coverage-unit reconciliation?",
        ],
        "blocked_by": [],
    },
    "M03": {
        "model": "unit_sales",
        "next_action": ("Independent reviewer: re-run scripts/oracle_M03.py and scripts/run_card.py, confirm "
                        "positive [305], the defaults case [30], the zero-volume case [5] and the 13 rejected "
                        "negatives; then rule on DEC-M03-2 (is a derived per-vehicle price acceptable as "
                        "unit_revenue) and on the 14.37% automobile-segment scope gap. Then I-10-A owns D/E."),
        "open_questions": [
            "DEC-M03-2: unit_revenue is derived from the same table's revenue cell, making the zero residual constructive. Is that admissible for a disclosure adaptation?",
            "DEC-M03-3 / SR-M03-B: is BYD's 销售收入 column net of returns/rebates, and is it VAT-exclusive? The table does not say.",
            "SR-M03-A: is 快报销量 the audited confirmed sales figure or a preliminary operating figure that may be restated?",
            "SR-M03-C: should the mapping be split per model line instead of one blended per-vehicle price?",
            "The 14.37% gap versus the automobile segment line is unexplained (batteries/parts); confirm no plug may be added to other_revenue.",
        ],
        "blocked_by": [],
    },
    "M04": {
        "model": "capacity_utilization",
        "next_action": ("Independent reviewer: re-run scripts/oracle_M04.py and scripts/run_card.py, confirm "
                        "positive [730], the defaults case [1440] and the 15 rejected negatives; then adjudicate "
                        "the ACTIVE STOP_DISCLOSURE_ADAPTATION (DEC-M04-1: period-end capacity annualised is not "
                        "the year-average available capacity) and SR-M04-A/SR-M04-B. Then I-10-A owns D/E."),
        "open_questions": [
            "DEC-M04-1: the frozen 0.5% volume tolerance FAILED at 21.40%. Choose between an average-capacity disclosure, an audited capacity-ramp bridge, or per-issuer not_applicable_with_reason.",
            "DEC-M04-2 / SR-M04-A: does the disclosed 产能利用率 already embed yield, i.e. is yield=1 a scope statement or a hidden assumption?",
            "DEC-M04-4: the gap mixes wrong capacity basis and output-versus-sales; no inventory bridge exists, so no apportionment was attempted. Confirm that is correct.",
            "SR-M04-B: this PDF's sidecar is a stub with no provider receipt or URL, so the document identity cannot be cross-checked against a publisher hash. Acceptable as disclosure evidence?",
            "SR-M04-C: should the model's capacity contract require 'average available capacity' explicitly?",
        ],
        "blocked_by": [],
    },
}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    rf = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    for card, meta in CARDS.items():
        attempt = os.path.join(PLAN, "execution_runs", card, "a20260919-01")
        evidence = os.path.join(attempt, "evidence", card)
        run = json.load(open(os.path.join(evidence, "run_result.json"), encoding="utf-8"))
        oracle = json.load(open(os.path.join(evidence, "oracle.json"), encoding="utf-8"))

        handoff = {
            "card_id": card,
            "attempt_id": "a20260919-01",
            "status": "review_pending",
            "implementer_is_not_the_reviewer": True,
            "completed_steps": {
                "A_binding": "done (binding.json: read-only production hashes + attempt-local isolated snapshot)",
                "B_positive_run": "done (positive equals the independent oracle within 1e-9*max(1,|e|))",
                "C_negative_run": "done (card-specific negative + N01-N05 + continuity break, all rejected with ModelRegistryError)",
                "D_disclosure_mapping": "minimum disclosure mapping delivered; professional decisions written as PROPOSED only, not signed",
                "E_historical_mapping_probe": "delivered as a labelled historical_mapping_probe; NOT a scenario set and NOT accuracy evidence",
                "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
            },
            "completed_steps_list": ["A", "B", "C", "D-minimum", "E-probe"],
            "next_step_number": 4,
            "next_action": meta["next_action"],
            "input_hashes": {
                "disclosed_source_documents": [
                    {"doc_id": d.get("doc_id"), "pdf_sha256": d.get("pdf_sha256"),
                     "sidecar_sha256": d.get("sidecar_sha256"),
                     "local_hash_matches_publisher_receipt": d.get("local_hash_matches_publisher_receipt")}
                    for d in json.load(open(os.path.join(evidence, "disclosure_mapping.json"),
                                            encoding="utf-8")).get("read_only_source_documents", [])
                ],
                "evidence_input_json": sha256_file(os.path.join(evidence, "input.json")),
                "evidence_oracle_json": sha256_file(os.path.join(evidence, "oracle.json")),
                "evidence_cases_json": sha256_file(os.path.join(evidence, "cases.json")),
            },
            "current_source_hashes": {
                "scripts/model_registry.py": sha256_file(os.path.join(rf, "scripts", "model_registry.py")),
                "scripts/model_extensions.py": sha256_file(os.path.join(rf, "scripts", "model_extensions.py")),
                "iso/checkout_scripts/model_registry.py": sha256_file(
                    os.path.join(attempt, "iso", "checkout_scripts", "model_registry.py")),
                "iso/checkout_scripts/model_extensions.py": sha256_file(
                    os.path.join(attempt, "iso", "checkout_scripts", "model_extensions.py")),
            },
            "changed_paths": {
                "production_repos": [],
                "note": "no production file was created, modified, added, committed, restored or stashed in any of the three repos",
                "attempt_paths_created": [attempt],
            },
            "commands_executed": ["A-oracle", "B-product-run", "C-pytest-sanity", "D-pdf-probe"],
            "raw_exit_codes": {"A": 0, "B": 0, "C": 0, "D": 0,
                               "first_B_attempt_before_harness_fix": 1},
            "expected_exit_codes": {"A": 0, "B": 0, "C": 0, "D": 0},
            "negative_case_summary": run["negative_summary"],
            "positive_actual": run["positive"].get("actual"),
            "positive_expected": oracle["positive"]["expected_float"],
            "open_questions": meta["open_questions"],
            "blocked_by": meta["blocked_by"],
            "stop_conditions_hit": (["STOP_DISCLOSURE_ADAPTATION (period-end capacity annualised fails the frozen "
                                     "0.5% volume tolerance by 21.40%)"] if card == "M04" else [])
                                  + (["STOP_ACCURACY (no I-12 frozen design)"] if card != "M04" else
                                     ["STOP_ACCURACY (no I-12 frozen design)",
                                      "STOP_DISCLOSURE_ADAPTATION (period-end capacity basis)"]),
            "qualifications": {
                "formula": "review_pending (implementer claim: pass; independent review required)",
                "disclosure_adaptation": "unmapped",
                "accuracy": "unproven",
            },
            "evidence_paths": sorted(
                ["binding.json", "commands.json", "oracle.md", "decision.md", "review.md", "handoff.json"]
                + ["evidence/%s/%s" % (card, name) for name in sorted(os.listdir(evidence))]
                + ["before/", "iso/checkout_scripts/", "scripts/"]
            ),
            "reviewer_status": "pending",
        }
        out = os.path.join(attempt, "handoff.json")
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(handoff, handle, ensure_ascii=False, indent=1)
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
