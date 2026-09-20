"""Writes changes.diff for cards M25-M28 (attempt-local statement file; no product diff).

Run:
  python -X utf8 -B scripts/write_changes_diff.py --card M26 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import os

MODEL_ID = {
    "M25": "installed_base_aftermarket",
    "M26": "store_cohorts",
    "M27": "renewable_generation",
    "M28": "aum_fee_bridge",
}

PROVENANCE = {
    "M25": ("the FIRST oracle generation had a defect in THIS card: the defaults expectation was "
            "planted as the positive value 300 while the frozen defaults input was the all-zero "
            "identity case whose hand value is 0. The generator was corrected BEFORE oracle.md was "
            "written and BEFORE the definitive product run."),
    "M26": ("the FIRST oracle generation needed no correction for THIS card (its defaults "
            "expectation 0 was already right), but the SAME generator file was corrected in this "
            "batch for M25 and M27 before oracle.md was written and before the definitive product "
            "run."),
    "M27": ("the FIRST oracle generation had a defect in THIS card: it crashed with "
            "`TypeError: Object of type Decimal is not JSON serializable` and produced no "
            "oracle.json at all. The generator was corrected BEFORE oracle.md was written and "
            "BEFORE the definitive product run."),
    "M28": ("the FIRST oracle generation needed no correction for THIS card (its defaults "
            "expectation 9.5 was already right), but the SAME generator file was corrected in this "
            "batch for M25 and M27 before oracle.md was written and before the definitive product "
            "run."),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(MODEL_ID))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()
    card = args.card
    lines = [
        "# changes.diff - %s - attempt a20260919-01" % card,
        "#",
        "# NO PRODUCT CHANGE.",
        "#",
        "# This attempt modified nothing under any production repository. The file is a statement",
        "# rather than a diff because there is no diff to show: the whole card is a read-only",
        "# formula qualification plus evidence.",
        "#",
        "# Verified after the card run:",
        "#   scripts/model_registry.py   sha256 "
        "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
        "#   scripts/model_extensions.py sha256 "
        "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        "#",
        "# The isolated code under test is a byte-identical copy held inside the attempt:",
        "#   iso/checkout_scripts/model_registry.py   (same sha256 as production)",
        "#   iso/checkout_scripts/model_extensions.py (same sha256 as production)",
        "#",
        "# Nothing was added, committed, restored or stashed in any production repo.",
        "# revenue-forecast already had pre-existing dirty files; those belong to their owner. The",
        "# pre-existing status is captured verbatim in before/git_status_revenue-forecast.txt and",
        "# after/git_status_revenue-forecast.txt so it cannot be attributed to this attempt.",
        "#",
        "# Files this attempt DID create, all inside this attempt directory:",
        "#   oracle.md, commands.json, binding.json, decision.md, review.md, handoff.json, changes.diff",
        "#   scripts/oracle_M25_M28.py, scripts/run_card.py, scripts/pack_evidence.py,",
        "#   scripts/write_docs.py, scripts/write_changes_diff.py",
        "#   evidence/%s/*  (input, oracle, cases, manifests, negative results, qualification," % card,
        "#                    integrity, oq rulings, enumeration, revision ledger, selfcheck,",
        "#                    disclosure mapping, accounting decision, reconciliation placeholder,",
        "#                    forecast integration placeholder, evidence hashes)",
        "#   before/, after/, recovery/ (including recovery/selfcheck and recovery/precorrection),",
        "#   iso/checkout_scripts/",
        "#",
        "# NOTE ON ORACLE PROVENANCE (stated here so it is not buried):",
        "#   " + PROVENANCE[card],
        "#   The pre-correction artefacts are preserved under recovery/precorrection/ and the full",
        "#   hash ledger is in evidence/%s/revision_r2.json." % card,
        "#   This is recorded as a provenance fact, not as a frozen-expectation change: no expectation",
        "#   that was ever frozen AND validated against the product was rewritten afterwards. The",
        "#   consequence - oracle.json's mtime being later than the very first product run of this",
        "#   attempt - is disclosed in review.md (section 5.1) and in revision_r2.json.",
        "#",
        "# Model under test: %s" % MODEL_ID[card],
    ]
    with open(os.path.join(args.attempt_root, "changes.diff"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print("wrote changes.diff for", card)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
