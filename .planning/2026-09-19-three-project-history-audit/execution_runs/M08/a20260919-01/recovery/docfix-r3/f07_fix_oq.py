"""F-M08-07 fix: correct the oq_rulings.json counts and the attribution.

Two defects are fixed, and every original string is preserved:

  1. counts.  The enumeration is redone from the code (f07_enumerate.py) and the file
     is rebuilt from that evidence:
        ratio_drivers_total           40 -> 41
        ratio_drivers_not_in_0_1      3  -> 4
        the missing one is direct_growth.growth_rate: dimension "ratio", but its domain
        is the hard-coded (-1, inf) contract in driver_value_bounds, not the [0,1]
        ratio default
  2. attribution.  The file named the independent reviewer as its author and used the
     first person ("enumerated the whole registry").  It is rewritten in the third
     person and now states who enumerated and who reviewed.

Nothing is dropped: the original `source` and `reviewer_basis` strings are kept
verbatim under `*_original_r2`, and a `corrections_applied` block records was/now.

Usage: <iso venv python> -X utf8 -B f07_fix_oq.py [--apply] > f07_fix_oq.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
APPLY = "--apply" in sys.argv
ENUM_CMD = ("iso venv python -X utf8 -B recovery/docfix-r3/f07_enumerate.py "
            "> recovery/docfix-r3/f07_enumerate.out.txt")
SOURCE_FIXED = (
    "enumerated by the implementer of attempt a20260919-01 from that attempt's isolated "
    "registry copy (iso/checkout_scripts, sha256 "
    "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f); the OQ-02 and "
    "OQ-04 rulings were reviewed and countersigned by the independent reviewer of the "
    "same attempt"
)
BASIS_FIXED = (
    "the implementer enumerated the whole registry and the independent reviewer checked "
    "the enumeration. Every driver whose dimension is revenue_per_activity or "
    "revenue_per_unit carries the (0, inf) default and none is in [0,1]. Only the ratio "
    "dimension defaults to [0,1]: 41 ratio drivers in total, of which 37 take the [0,1] "
    "default and 4 do not -- bank_revenue.asset_yield and bank_revenue.funding_cost both "
    "declared (-inf, inf) because interest and funding rates may be negative, "
    "store_cohorts.new_store_productivity declared (0, inf), and "
    "direct_growth.growth_rate hard-coded (-1, inf) in driver_value_bounds because a "
    "growth rate may be a contraction. Two further priced-volume drivers "
    "(renewable_generation.contract_price_per_mwh and "
    "renewable_generation.merchant_price_per_mwh) are declared (-inf, inf) but are not "
    "ratio-dimensioned. The r2 count of 40 ratio drivers with 3 exceptions was therefore "
    "wrong by one on both numbers; the ruling itself is unaffected"
)


def sha_file(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    print("== F-M08-07 fix: oq_rulings.json counts + attribution ==")
    print(f"apply={APPLY}")
    ledger: dict[str, object] = {}
    for card in CARDS:
        ev = os.path.join(BASE, card, "a20260919-01", "evidence", card)
        oq_path = os.path.join(ev, "oq_rulings.json")
        enum_path = os.path.join(ev, "oq_rulings_enumeration.json")
        old = json.load(open(oq_path, encoding="utf-8"))
        enum = json.load(open(enum_path, encoding="utf-8"))["enumeration"]
        idx = enum["effective_bounds_index"]
        old_perf = old["OQ_02"]["enumeration_performed"]

        before_sha = sha_file(oq_path)
        before_bytes = os.path.getsize(oq_path)
        print("")
        print(f"-- {card} --")
        print(f"   before sha256={before_sha} bytes={before_bytes}")
        print(f"   was: ratio_drivers_total={old_perf['ratio_drivers_total']} "
              f"not_in_0_1={len(old_perf['ratio_drivers_not_in_0_1'])} "
              f"={[r['driver'] for r in old_perf['ratio_drivers_not_in_0_1']]}")
        print(f"   now: ratio_drivers_total={enum['ratio_drivers_total']} "
              f"not_in_0_1={enum['ratio_drivers_not_in_0_1_total']} "
              f"={[r['model_id'] + '.' + r['driver'] for r in enum['ratio_drivers_not_in_0_1']]}")
        print(f"   enumeration evidence sha256={sha_file(enum_path)}")

        outside = [
            {
                "driver": f"{r['model_id']}.{r['driver']}",
                "bounds": r["effective_bounds"],
                "declared_bounds": r["declared_bounds"],
                "reason": r["outside_reason"],
            }
            for r in enum["ratio_drivers_not_in_0_1"]
        ]

        oq02 = old["OQ_02"]
        new = {
            "card_id": old["card_id"],
            "source": SOURCE_FIXED,
            "source_original_r2": old["source"],
            "enumerated_by": "implementer of attempt a20260919-01 "
                             "(re-enumerated for finding F-M08-07)",
            "reviewed_by": "independent reviewer of attempt a20260919-01 (point review of "
                           "the r2 response; the OQ rulings below are the reviewer's, the "
                           "enumeration is not)",
            "enumeration_command": ENUM_CMD,
            "enumeration_evidence": f"evidence/{card}/oq_rulings_enumeration.json",
            "enumeration_evidence_sha256": sha_file(enum_path),
            "OQ_02": {
                "ruling": oq02["ruling"],
                "ruled_by": "independent reviewer of attempt a20260919-01",
                "reviewer_basis": BASIS_FIXED,
                "reviewer_basis_original_r2": oq02["reviewer_basis"],
                "enumeration_performed": {
                    "enumerated_by": "implementer of attempt a20260919-01",
                    "code_root": enum["code_root"],
                    "model_registry_sha256": enum["model_registry_sha256"],
                    "models_total": enum["models_total"],
                    "drivers_total": enum["drivers_total"],
                    "ratio_drivers_total": enum["ratio_drivers_total"],
                    "ratio_drivers_taking_the_0_1_default":
                        enum["ratio_drivers_in_0_1_total"],
                    "ratio_drivers_not_in_0_1_total":
                        enum["ratio_drivers_not_in_0_1_total"],
                    "ratio_drivers_not_in_0_1": outside,
                    "revenue_per_activity_and_per_unit_drivers_total":
                        enum["revenue_per_activity_or_per_unit_total"],
                    "revenue_per_activity_and_per_unit_default_bounds": [0.0, None],
                    "revenue_per_activity_and_per_unit_exceptions": [
                        {"driver": f"{r['model_id']}.{r['driver']}",
                         "bounds": r["effective_bounds"]}
                        for r in enum["revenue_per_activity_or_per_unit_outside_0_inf"]
                    ],
                    "usage_platform.monetization_rate_bounds":
                        idx["usage_platform.monetization_rate"],
                    "subscription.timing_factor_bounds":
                        idx["subscription.timing_factor"],
                    "services.utilization_bounds": idx["services.utilization"],
                    "explicit_driver_bounds_sets":
                        enum["models_with_explicit_driver_bounds"],
                    "growth_rate_bounds": idx["direct_growth.growth_rate"],
                },
                "consequence": oq02["consequence"],
                "observed_probe": oq02["observed_probe"],
            },
            "OQ_04": old["OQ_04"],
            "corrections_applied": [
                {
                    "finding": "F-M08-07",
                    "field": "OQ_02.enumeration_performed.ratio_drivers_total",
                    "was": old_perf["ratio_drivers_total"],
                    "now": enum["ratio_drivers_total"],
                    "why": "the registry has 41 ratio-dimensioned drivers; the r2 count "
                           "dropped direct_growth.growth_rate",
                },
                {
                    "finding": "F-M08-07",
                    "field": "OQ_02.enumeration_performed.ratio_drivers_not_in_0_1",
                    "was": [r["driver"] for r in old_perf["ratio_drivers_not_in_0_1"]],
                    "now": [r["driver"] for r in outside],
                    "why": "direct_growth.growth_rate has dimension ratio but the "
                           "hard-coded (-1, inf) domain, so it is a fourth ratio driver "
                           "outside [0,1]",
                },
                {
                    "finding": "F-M08-07",
                    "field": "source / reviewer_basis",
                    "was": "the independent reviewer was named as the author, in the first "
                           "person ('enumerated the whole registry')",
                    "now": "third person; states that the implementer enumerated and the "
                           "independent reviewer reviewed and countersigned",
                    "why": "attribution must not credit the reviewer with the "
                           "implementer's enumeration; both originals are preserved "
                           "verbatim under source_original_r2 and "
                           "reviewer_basis_original_r2",
                },
            ],
        }

        out = json.dumps(new, indent=1, ensure_ascii=False) + "\n"
        out_bytes = out.encode("utf-8")
        after_sha = hashlib.sha256(out_bytes).hexdigest()
        print(f"   after  bytes={len(out_bytes)} sha256={after_sha}")
        if APPLY:
            open(oq_path, "w", encoding="utf-8", newline="").write(out)
            got = sha_file(oq_path)
            print(f"   APPLIED -> {got} match={got == after_sha}")
            if got != after_sha:
                raise SystemExit(f"{card}: post-write hash mismatch")

        ledger[card] = {
            "oq_rulings_path": f"evidence/{card}/oq_rulings.json",
            "sha256_before": before_sha,
            "bytes_before": before_bytes,
            "sha256_after": after_sha,
            "bytes_after": len(out_bytes),
            "ratio_drivers_total_was": old_perf["ratio_drivers_total"],
            "ratio_drivers_total_now": enum["ratio_drivers_total"],
            "ratio_drivers_not_in_0_1_was":
                len(old_perf["ratio_drivers_not_in_0_1"]),
            "ratio_drivers_not_in_0_1_now": enum["ratio_drivers_not_in_0_1_total"],
            "enumeration_evidence": f"evidence/{card}/oq_rulings_enumeration.json",
            "enumeration_evidence_sha256": sha_file(enum_path),
        }

    with open(os.path.join(HERE, "f07_fix_oq.json"), "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f07_fix_oq.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
