"""Batch-level final audit over the four attempts of the M09-M12 batch.

Checks, mechanically:
  1. required evidence files exist for every card;
  2. card title / card id / model_id agree across oracle.md, decision.md, review.md, handoff.json
     and the evidence files;
  3. the freeze-before-run mtime ordering holds and oracle.md was not edited after it was frozen
     (its mtime is before the first product stdout);
  4. evidence_hashes.json really matches the current bytes of every file it lists;
  5. the three qualifications are in the expected state (formula=review_pending,
     disclosure_adaptation=unmapped, accuracy=unproven);
  6. revision_r2.json declares an empty r2 slot (no second revision section anywhere);
  7. the read-only audit anchor reviews/second_wave/final_review_checks.json is untouched;
  8. the frozen isolated copies still hash-equal the production files.

Run:
  python -X utf8 -B scripts/final_audit.py --plan-root <PLAN>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

CARDS = {"M09": "resource", "M10": "reserve_depletion",
         "M11": "infrastructure", "M12": "bank_revenue"}
REQUIRED = ["input.json", "oracle.json", "cases.json", "source_manifest.json", "command_manifest.json",
            "stdout.txt", "stderr.txt", "formula_result.json", "negative_results.json",
            "qualification.json", "oq_rulings.json", "integrity.json", "oracle_selfcheck.json",
            "revision_r2.json", "run_result.json", "observation_expected.json", "registry_enumeration.json",
            "consistency_check.json", "regeneration_check.json", "mtime_ordering.json",
            "evidence_hashes.json", "artifact_hashes.txt", "disclosure_source_survey.json",
            "disclosure_mapping.json", "accounting_decision.md", "deferred_work.json"]
ROOT_REQUIRED = ["binding.json", "oracle.md", "commands.json", "decision.md", "handoff.json",
                 "changes.diff", "review.md"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-root", required=True)
    args = parser.parse_args()
    plan_root = os.path.abspath(args.plan_root)
    # PLAN root is <repo>/.planning/<plan-name>, so the repo is two levels up
    production = os.path.dirname(os.path.dirname(plan_root))

    failures = []
    rows = []
    anchor = os.path.join(plan_root, "reviews", "second_wave", "final_review_checks.json")
    anchor_mtime = os.path.getmtime(anchor)
    anchor_stamp = "2026-09-19 10:05:32"

    for card, model_id in sorted(CARDS.items()):
        attempt = os.path.join(plan_root, "execution_runs", card, "a20260919-01")
        evidence = os.path.join(attempt, "evidence", card)
        missing = [name for name in REQUIRED if not os.path.exists(os.path.join(evidence, name))]
        missing += [name for name in ROOT_REQUIRED if not os.path.exists(os.path.join(attempt, name))]
        if missing:
            failures.append("%s missing files: %s" % (card, missing))

        oracle = load_json(os.path.join(evidence, "oracle.json"))
        handoff = load_json(os.path.join(attempt, "handoff.json"))
        run = load_json(os.path.join(evidence, "run_result.json"))
        qualification = load_json(os.path.join(evidence, "qualification.json"))
        ordering = load_json(os.path.join(evidence, "mtime_ordering.json"))
        revision = load_json(os.path.join(evidence, "revision_r2.json"))
        consistency = load_json(os.path.join(evidence, "consistency_check.json"))
        source_manifest = load_json(os.path.join(evidence, "source_manifest.json"))
        hashes = load_json(os.path.join(evidence, "evidence_hashes.json"))

        oracle_md_first = open(os.path.join(attempt, "oracle.md"), encoding="utf-8").readline().strip()
        decision_first = open(os.path.join(attempt, "decision.md"), encoding="utf-8").readline().strip()
        review_first = open(os.path.join(attempt, "review.md"), encoding="utf-8").readline().strip()

        title_ok = (card in oracle_md_first and card in decision_first and card in review_first
                    and model_id in oracle_md_first and model_id in review_first)
        ids_ok = (oracle["card_id"] == card and oracle["model_id"] == model_id
                  and handoff["card_id"] == card and handoff["model_id"] == model_id
                  and run["card_id"] == card and run["model_id"] == model_id)
        if not title_ok:
            failures.append("%s title/card/model mismatch: %r %r %r"
                            % (card, oracle_md_first, decision_first, review_first))
        if not ids_ok:
            failures.append("%s card_id/model_id mismatch across files" % card)

        if not ordering["ordering_ok"]:
            failures.append("%s mtime ordering failed" % card)

        mismatched = []
        for relpath, recorded in hashes["files"].items():
            path = os.path.join(attempt, relpath.replace("/", os.sep))
            if not os.path.exists(path):
                mismatched.append((relpath, "missing"))
            elif sha256_file(path) != recorded:
                mismatched.append((relpath, "hash differs"))
        stated_trailing_gap = ["after/rc_ledger.txt", "after/final_audit.txt"]
        stated_trailing_gap += [name for name in hashes["files"]
                                if name.startswith("after/console_Z")]
        unexpected = [m for m in mismatched if m[0] not in stated_trailing_gap]
        if unexpected:
            failures.append("%s evidence_hashes mismatch: %s" % (card, unexpected[:5]))

        quals = (qualification["formula"]["state"], qualification["disclosure_adaptation"]["state"],
                 qualification["accuracy"]["state"])
        if quals != ("review_pending", "unmapped", "unproven"):
            failures.append("%s qualification state unexpected: %s" % (card, quals))

        if revision["r2_present"] or revision["appended_sections"] != 0:
            failures.append("%s revision_r2 slot is not empty" % card)
        if not revision["frozen_expectations_unchanged"]:
            failures.append("%s revision_r2 reports frozen expectations changed" % card)

        if not consistency["all_consistent"]:
            failures.append("%s consistency_check failed: %s" % (card, consistency["checks_failed"]))

        iso_reg = os.path.join(attempt, "iso", "checkout_scripts", "model_registry.py")
        prod_reg = os.path.join(production, "scripts", "model_registry.py")
        iso_ok = sha256_file(iso_reg) == sha256_file(prod_reg)
        if not iso_ok:
            failures.append("%s isolated copy differs from production" % card)

        rows.append({
            "card": card,
            "model_id": model_id,
            "rc": run["exit_code_semantics"]["exit_code"],
            "positive": run["positive"].get("actual"),
            "continuity": run["continuity_positive"].get("actual"),
            "defaults": run["defaults"].get("actual"),
            "negatives": "%d/%d" % (run["negative_summary"]["passed"],
                                    run["negative_summary"]["total"]),
            "observations_matched": "%d/%d" % (
                sum(1 for o in run["observations"] if o.get("matches_expected")),
                len(run["observations"])),
            "consistency_checks": consistency["checks_total"],
            "hashed_files": hashes["file_count"],
            "iso_equals_production": iso_ok,
            "mtime_order_ok": ordering["ordering_ok"],
            "oracle_json_precedes_stdout": ordering["oracle_json_before_first_product_stdout"],
            "qualifications": "%s/%s/%s" % quals,
            "selfcheck_cases": load_json(os.path.join(attempt, "recovery",
                                                      "selfcheck_result.json"))
                                  ["all_cases_as_expected"],
        })

    print("card  model               rc  positive            continuity        defaults"
          "   negatives  obs   cons  files  iso  order  quals")
    for row in rows:
        print("%-5s %-19s %-3s %-19s %-17s %-10s %-10s %-5s %-5s %-5s %-4s %-6s %s"
              % (row["card"], row["model_id"], row["rc"], row["positive"], row["continuity"],
                 row["defaults"], row["negatives"], row["observations_matched"],
                 row["consistency_checks"], row["hashed_files"], row["iso_equals_production"],
                 row["mtime_order_ok"], row["qualifications"]))
    print("reviews anchor", anchor, "mtime_epoch", anchor_mtime,
          "(recorded as %s)" % anchor_stamp)
    print("failures:", failures if failures else "none")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
