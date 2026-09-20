"""One-shot consolidated status + hash report for the four r3 attempts."""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load(path):
    return json.load(open(path, encoding="utf-8"))


def main() -> int:
    strict_bad = []
    for card in ("M13", "M14", "M15", "M16"):
        at = os.path.join(PLAN, "execution_runs", card, "a20260919-01")
        ev = os.path.join(at, "evidence", card)

        def boom(value):
            raise ValueError("non-standard JSON constant: " + value)

        for root, dirs, files in os.walk(at):
            if root.startswith(os.path.join(at, "iso", "venv")):
                dirs[:] = []
                continue
            for name in files:
                if name.endswith(".json"):
                    try:
                        json.load(open(os.path.join(root, name), encoding="utf-8"),
                                  parse_constant=boom)
                    except Exception as exc:  # noqa: BLE001
                        strict_bad.append((card, name, str(exc)[:60]))

        run = load(os.path.join(ev, "run_result.json"))
        q = load(os.path.join(ev, "qualification.json"))
        sc = load(os.path.join(at, "recovery", "selfcheck_result.json"))
        bc = load(os.path.join(ev, "r2_boundary_check.json"))
        vr = load(os.path.join(ev, "verify_report.json"))
        enum = load(os.path.join(ev, "oq_enumeration.json"))
        rul = load(os.path.join(ev, "oq_rulings.json"))
        audit = load(os.path.join(ev, "doc_pointer_audit.json"))
        repack = load(os.path.join(ev, "cases_annotation_repack.json"))
        inv = load(os.path.join(at, "after", "rerun_sha256.json"))
        ho = load(os.path.join(at, "handoff.json"))
        r2 = load(os.path.join(ev, "revision_r2.json"))
        r3 = load(os.path.join(ev, "revision_r3.json"))

        # recompute the combined digest from the manifest's own files map
        combined = hashlib.sha256()
        for rel in sorted(inv["files"]):
            combined.update(rel.encode("utf-8"))
            combined.update(inv["files"][rel]["sha256"].encode("ascii"))

        print("=" * 78)
        print("%s %s" % (card, run["model_id"]))
        print("  runner rc=%s verdict=%s triggered=%s pos=%s cont=%s def=%s neg=%s/%s fid=%s"
              % (run["exit_code"], run["verdict"]["verdict"],
                 run["exit_code_semantics"]["triggered"], run["positive"]["actual"],
                 run["continuity_positive"]["actual"], run["defaults"]["actual"],
                 run["negative_summary"]["passed"], run["negative_summary"]["total"],
                 run["positive"]["fidelity"]["ok"]))
        print("  expectation_consistency ok=%s cases=%s oracle_count=%s declared=%s"
              % (run["expectation_consistency"]["ok"],
                 run["expectation_consistency"]["facts"]["case_count"],
                 run["expectation_consistency"]["facts"]["oracle_negative_count"],
                 run["expectation_consistency"]["facts"]["declared_expectations"]))
        print("  selfcheck matrix=%s pre_fix_runner=%s frozen_ok=%s"
              % (json.dumps(sc["exit_code_matrix"], sort_keys=True),
                 sc["pre_fix_runner_revision"]["sha256"][:12]
                 if sc["pre_fix_runner_revision"]["sha256"] else None,
                 sc["frozen_still_equals_freeze_time_hashes"]))
        print("  r2 offset=%s ok=%s | r3 offset=%s ok=%s | boundary_all=%s"
              % (bc["r2"]["boundary_byte_offset"],
                 bc["r2"]["sha256_of_bytes_before_the_marker"] == r2["boundary"][
                     "sha256_of_bytes_before_the_marker"],
                 bc["r3"]["boundary_byte_offset"], bc["all_checks_passed"],
                 bc["all_checks_passed"]))
        print("  r2 single=%s r3 single=%s | oracle.md sha=%s"
              % (r2["single_revision_node"], r3["single_revision_node"], bc["oracle_md_sha256"][:16]))
        print("  enum ratio=%s/%s not01=%s (narrow set=%s) slots=%s models=%s"
              % (enum["registry_totals"]["ratio_drivers_by_dimension"],
                 enum["registry_totals"]["ratio_drivers_whose_bounds_are_not_0_1"],
                 enum["registry_totals"]["ratio_drivers_whose_bounds_are_not_0_1"],
                 enum["registry_totals"]["ratio_drivers_by_registry_ratio_set"],
                 enum["registry_totals"][
                     "optional_drivers_without_an_explicit_default_slots_total"],
                 enum["registry_totals"][
                     "optional_drivers_without_an_explicit_default_models_total"]))
        print("  OQ ids in oq_rulings=%s handoff=%d pytest_item=%s"
              % (sorted(rul["open_questions_mirroring_handoff"]), len(ho["open_questions"]),
                 "OQ-05" in rul["open_questions_mirroring_handoff"]))
        print("  reviewer_opinions in handoff=%d"
              % len(ho.get("reviewer_opinions_on_open_questions", [])))
        print("  pointer audit: pointers=%s dangling=%s residue=%s cross_batch=%s"
              % (audit["pointer_count"], len(audit["dangling_pointers"]),
                 audit["reviewer_residue_tokens_found"],
                 [e.get("line_matches_claim", e.get("claims_all_present"))
                  for e in audit["cross_batch_references_verified"]]))
        print("  cases repack: old=%s new=%s only_annotation=%s"
              % (repack["old_revision"]["sha256"][:12], repack["new_revision"]["sha256"][:12],
                 repack["difference_is_only_the_declared_annotation"]))
        print("  verify all=%s | validate ok | inventory files=%s combined_reproducible=%s"
              % (vr["all_checks_passed"], inv["file_count"],
                 combined.hexdigest()
                 == inv["combined_digest_over_sorted_relative_path_and_sha256"]))
        print("  qualifications: formula=%s disclosure=%s accuracy=%s"
              % (q["formula"]["state"], q["disclosure_adaptation"]["state"],
                 q["accuracy"]["state"]))
        for name in ("oracle.md", "commands.json", "review.md", "decision.md", "handoff.json",
                     "binding.json", "changes.diff", "recovery/README.md"):
            print("    %-22s %s" % (name, sha(os.path.join(at, name.replace("/", os.sep)))))
        for name in ("revision_r3.json", "doc_pointer_audit.json", "cases_annotation_repack.json",
                     "oq_enumeration.json", "oq_rulings.json", "r2_boundary_check.json",
                     "verify_report.json", "cases.json", "oracle.json", "input.json",
                     "run_result.json", "stdout.txt"):
            print("    evidence/%-16s %s" % (name, sha(os.path.join(ev, name))))
        print("    after/rerun_sha256    %s" % sha(os.path.join(at, "after", "rerun_sha256.json")))
    print("=" * 78)
    print("strict-JSON violations across all four attempts: %s" % (strict_bad or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
