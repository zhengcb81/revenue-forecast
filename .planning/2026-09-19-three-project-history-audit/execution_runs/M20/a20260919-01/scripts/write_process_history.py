"""Write process_history.json: what was executed, in which pass, and what survives on disk.

Motivation (independent review P3-3): pipeline_run.json only describes the LAST pipeline pass and
carries no pass history, so a reader cannot see that a unit was executed more than once.  This file
separates two things that must not be conflated:

  * OBSERVED - rebuilt mechanically from the surviving evidence/<CARD>/runs/<UNIT>/rc.json records
    (started_utc / finished_utc / raw rc / stdout sha256 of the LAST execution of each unit);
  * DECLARED - the pass structure as declared by the implementing session, including executions
    whose records were overwritten by a later execution of the identical argv.  Declared entries
    are labelled as such and are NOT presented as on-disk evidence.

Usage:
  python -X utf8 -B write_process_history.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

import card_units

# The closing sequence (P/H/Z units) was executed once per bookkeeping change.  Pass 6 is the pass
# this file is written in, so its own units are counted as DECLARED rather than observed.
CLOSING_PASSES = [
    {"pass": 1, "kind": "closing", "units": "H,Z", "trigger": "first closing after the evidence pack"},
    {"pass": 2, "kind": "closing", "units": "H,Z",
     "trigger": "close_attempt.py extended to refresh handoff.json"},
    {"pass": 3, "kind": "closing", "units": "H,Z",
     "trigger": "evidence_hashes.json exclusion of the final hash table fixed"},
    {"pass": 4, "kind": "closing", "units": "H,Z",
     "trigger": "final hash table exclusion of the closing unit's own capture records fixed"},
    {"pass": 5, "kind": "closing", "units": "Z",
     "trigger": "review.md wording about the closing unit's rc corrected"},
    {"pass": 6, "kind": "closing", "units": "R2,G,P,H,Z",
     "trigger": ("post-review fixes: runner declared-expectation enforcement (P2-1), probe wording "
                 "(P3-2), OQ-05 parameterisation and ruling entry (P2-2, P3-1), process history "
                 "(P3-3), M17 oracle.md section 13 append")},
]

# Declared pass history per card.  Every number here is declared by the implementing session;
# the on-disk records can only show the LAST execution of each unit.
DECLARED = {
    "M17": {
        "measurement_pipeline_executions_declared": 3,
        "measurement_pipeline_passes": [
            {"pass": 1, "units": 13, "trigger": "initial attempt",
             "note": ("C2-extra-boundary-probes did not exist yet; the frozen oracle.md was already "
                      "written and was not modified")},
            {"pass": 2, "units": 14, "trigger": "C2 probe unit added",
             "note": ("the probe constant for PROBE-NEG-MILESTONE was still 105.0, i.e. derived from "
                      "'110 - 5' instead of '40x2 - 5 + 5 + 10 = 90'")},
            {"pass": 3, "units": 14, "trigger": "probe constant corrected to 90.0",
             "note": ("produced the surviving rc.json/stdout records for every measurement unit")},
        ],
        "rewritten_generations_forensically_visible": 2,
        "forensic_explanation": ("the runs/<UNIT> directories were created in pass 1 (13 of them) and "
                                "the C2 directory in pass 2; every rc.json was last rewritten in pass "
                                "3, so the file system distinguishes 2 generations while the session "
                                "executed the pipeline 3 times"),
        "post_review_unit_reexecutions_declared": ["B-product-run", "C2-extra-boundary-probes",
                                                   "E-mutation-selfcheck", "G-pack-evidence"],
        "closing_executions_declared": len(CLOSING_PASSES),
        "closing_passes": CLOSING_PASSES,
        "pack_executions_declared": 8,
        "c2_unit_origin": ("ADDED during this attempt (after measurement pass 1); it is a card-specific "
                           "unit of this attempt, not a template unit"),
    },
    "M18": {
        "measurement_pipeline_executions_declared": 1,
        "measurement_pipeline_passes": [
            {"pass": 1, "units": 14, "trigger": "initial attempt",
             "note": "produced the surviving rc.json/stdout records for every measurement unit"},
        ],
        "rewritten_generations_forensically_visible": 1,
        "forensic_explanation": ("all 14 runs/<UNIT> directories were created and written within the "
                                "same pass, so directory creation and file writing are milliseconds "
                                "apart and no second generation is visible"),
        "post_review_unit_reexecutions_declared": ["B-product-run", "C2-extra-boundary-probes",
                                                   "E-mutation-selfcheck", "G-pack-evidence"],
        "closing_executions_declared": len(CLOSING_PASSES),
        "closing_passes": CLOSING_PASSES,
        "pack_executions_declared": 6,
        "c2_unit_origin": ("delivered byte-identically from the M17 attempt as an EXISTING unit of this "
                           "attempt's unit list; it was NOT added to this card after a first pass"),
    },
}

DECLARED["M19"] = {**DECLARED["M18"]}
DECLARED["M20"] = {**DECLARED["M18"]}


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
    evidence = os.path.join(attempt, "evidence", card)
    units = card_units.build_units(card, attempt) + card_units.r2_units(card, attempt) \
        + card_units.closing_units(card, attempt)

    observed = []
    for unit in units:
        record = {"unit_id": unit["unit_id"], "argv": unit["argv"],
                  "expected_rc": unit["expected_rc"], "rc_record": unit["rc_record"]}
        if os.path.isfile(unit["rc_record"]):
            rc_doc = load(unit["rc_record"])
            record.update({
                "raw_returncode_last_execution": rc_doc.get("raw_returncode"),
                "started_utc_last_execution": rc_doc.get("started_utc"),
                "finished_utc_last_execution": rc_doc.get("finished_utc"),
                "stdout_path": rc_doc.get("stdout_path"),
                "stdout_sha256_last_execution": rc_doc.get("stdout_sha256"),
                "stderr_sha256_last_execution": rc_doc.get("stderr_sha256"),
            })
        else:
            record["rc_record_note"] = ("the closing unit currently executing writes its own record "
                                        "after it returns")
        observed.append(record)

    doc = {
        "card_id": card,
        "model_id": card_units.CARDS[card]["model_id"],
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "purpose": ("make repeated executions of the same argv visible: pipeline_run.json only "
                    "describes the last pipeline pass and closing_run.json only the last closing pass"),
        "observed_last_execution_per_unit": {
            "source": "evidence/%s/runs/<UNIT>/rc.json (rewritten by the capture wrapper on every "
                      "execution, so only the LAST execution survives)" % card,
            "units": observed,
            "units_with_surviving_records": sum(
                1 for r in observed if "raw_returncode_last_execution" in r),
            "units_without_surviving_records": [r["unit_id"] for r in observed
                                                if "raw_returncode_last_execution" not in r],
        },
        "declared_execution_history": DECLARED[card],
        "declared_vs_observed": {
            "declared": ("the pass structure above is DECLARED by the implementing session; it is not "
                         "reconstructible from the surviving records alone"),
            "observed": ("the byte-level records can only prove the last execution of each unit; the "
                         "counts of earlier executions with identical argv are not on disk"),
            "reconciliation": ("the declared measurement-pass count and the forensically visible "
                               "generation count differ for M17 exactly because the two later passes "
                               "rewrote the same files, which is stated in forensic_explanation"),
        },
        "honest_gaps": [
            ("the raw stdout/rc of every superseded execution were overwritten in place; the only "
             "on-disk trace of an earlier execution is a directory-creation timestamp"),
            ("this file itself is written during a closing pass, so the closing pass it belongs to is "
             "counted as declared, not as observed"),
        ],
        "pointer_to_last_pipeline_pass": "pipeline_run.json",
        "pointer_to_last_closing_pass": "recovery/closing_run.json",
    }
    out = os.path.join(attempt, "process_history.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("process_history written", out)
    print("units with surviving rc records:", doc["observed_last_execution_per_unit"]
          ["units_with_surviving_records"], "of", len(observed))
    print("declared measurement pipeline executions:",
          DECLARED[card]["measurement_pipeline_executions_declared"])
    print("declared closing executions:", DECLARED[card]["closing_executions_declared"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
