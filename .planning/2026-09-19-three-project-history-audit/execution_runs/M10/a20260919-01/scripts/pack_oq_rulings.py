"""Writes evidence/<CARD>/oq_rulings.json from the enumerated registry facts.

Every count in the ruling document is copied from evidence/<CARD>/registry_enumeration.json,
which is produced by scripts/enumerate_registry_facts.py (read-only contract read). The raw
console of that enumeration is preserved as
after/console_C-<CARD>-registry-enumeration_<CARD>.txt.

Wording rule: third-person, objective. The ruling document names who performed the
enumeration, who has NOT reviewed it yet, and which raw output backs each count. It never
attributes the enumeration to the reviewer and never uses the first person.

Run:
  python -X utf8 -B scripts/pack_oq_rulings.py --card M09 --attempt <attempt>
"""

from __future__ import annotations

import argparse
import json
import os


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)

    enum = load_json(os.path.join(evidence, "registry_enumeration.json"))
    run = load_json(os.path.join(evidence, "run_result.json"))
    integrity = load_json(os.path.join(evidence, "integrity.json"))
    facts = enum["facts"]
    per_card = enum["per_card"]
    target = per_card[card]
    observations = {o["id"]: o for o in run["observations"]}

    doc = {
        "card_id": card,
        "model_id": enum["target_model_id"],
        "document_kind": "open-question ruling sheet built from an enumerated registry read",
        "enumeration_provenance": {
            "performed_by": "the implementer session of attempt a20260919-01, by running "
                            "scripts/enumerate_registry_facts.py against the attempt-local isolated copy",
            "enumeration_script": "scripts/enumerate_registry_facts.py",
            "machine_readable_output": "evidence/%s/registry_enumeration.json" % card,
            "raw_console_output": "after/console_C-%s-registry-enumeration_%s.txt" % (card, card),
            "read_kind": enum["read_kind"],
            "reviewed_by": "PENDING - no independent reviewer has ruled on this attempt; the card is at "
                           "status review_pending, so every ruling below is an implementer-side registration, "
                           "not an accepted ruling",
            "product_change_made": False,
        },
        "OQ_1_silent_zero_fill": {
            "statement": "scripts/model_registry.py:335 substitutes 0.0 for an omitted optional driver that "
                         "has no declared default, so the input 'the item is absent' and 'the item could not "
                         "be found' become indistinguishable.",
            "enumerated_counts": {
                "batch_cards": enum["batch_scope"],
                "batch_optional_driver_count": facts["batch_optional_driver_count"],
                "batch_optional_drivers_without_a_declared_default":
                    facts["batch_optional_drivers_without_declared_default"],
                "batch_optional_drivers_without_a_declared_default_total":
                    facts["batch_optional_drivers_without_declared_default_total"],
                "registry_optional_drivers_without_a_declared_default_total":
                    facts["registry_optional_drivers_without_declared_default_total"],
                "this_card_optional_drivers": target["optional"],
                "this_card_optional_drivers_without_a_declared_default":
                    target["optional_drivers_without_declared_default"],
                "this_card_declared_defaults": target["declared_defaults"],
            },
            "why_it_matters_for_this_card": {
                "M09": "an omitted `other_revenue` asserts 'no other revenue' although the card's own "
                       "business negatives warn that by-products may already sit inside the realised price",
                "M10": "`reserve_revisions` omitted becomes 0, so a missing reserve revision silently "
                       "becomes a balanced reserve statement - the exact field the card warns about",
                "M11": "an omitted `other_revenue` asserts 'no capacity fee and no subsidy', which is a "
                       "regulatory claim, not an arithmetic one",
                "M12": "an omitted `other_revenue` asserts 'no other operating income' for a bank, where "
                       "other operating income is usually material",
            }[card],
            "observed_probe": "the defaults case of this card (driver omitted) is measured in "
                              "evidence/%s/run_result.json -> defaults" % card,
            "action": "registered, NOT fixed; no product change",
        },
        "OQ_2_bank_totals_guard_vs_rate_domain": {
            "applies_to_this_card": card == "M12",
            "statement": "For bank_revenue the rejected case is a revenue-TOTAL refusal, not a "
                         "rate-domain refusal: the two rate drivers keep explicit (None, None) bounds, so "
                         "negative rates are accepted while a negative total is not.",
            "enumerated_counts": {
                "bank_revenue_rate_driver_bounds": per_card["M12"]["explicit_driver_bounds"],
                "ratio_drivers_whose_effective_bounds_are_not_0_1_count":
                    facts["ratio_drivers_whose_effective_bounds_are_not_0_1_count"],
                "ratio_drivers_whose_effective_bounds_are_not_0_1":
                    facts["ratio_drivers_whose_effective_bounds_are_not_0_1"],
            },
            "observed_probes": {
                "OBS-NEG-RATE-ACCEPTED": observations.get("OBS-NEG-RATE-ACCEPTED", {}).get("actual"),
                "OBS-NEG-RATE-TOTAL-NEG": observations.get("OBS-NEG-RATE-TOTAL-NEG", {}).get("raised"),
                "OBS-RATE-GT1": observations.get("OBS-RATE-GT1", {}).get("actual"),
            },
            "consequence": "the card's negative must not be read as 'interest rates must be positive'. The "
                           "genuine adapter limitation is that a bank year with negative total revenue "
                           "cannot be represented, and common_model_cards.md L11 forbids clipping it to "
                           "zero; that needs an owner ruling (see DEC-M12-3).",
        },
        "OQ_3_negative_price_and_tariff_not_expressible": {
            "applies_to_this_card": card in ("M09", "M11"),
            "statement": "`revenue_per_unit` and `revenue_per_activity` drivers default to [0, inf), so a "
                         "negative realised price (M09) or a rebate-style negative tariff (M11) cannot be "
                         "expressed at this entry point.",
            "enumerated_counts": {
                "drivers_with_dimension_revenue_per_unit_or_revenue_per_activity":
                    facts["revenue_per_unit_and_revenue_per_activity_driver_count"],
                "such_drivers_that_admit_negative_values":
                    facts["revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values"],
                "such_drivers_that_admit_negative_values_count":
                    facts["revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values_count"],
                "observed_default_bounds_for_that_dimension_family":
                    facts["revenue_per_unit_and_revenue_per_activity_default_bounds_observed"],
                "this_card_driver_bounds": {
                    d["driver"]: [d["effective_lower_bound"], d["effective_upper_bound"]]
                    for d in target["drivers"]},
            },
            "observed_probes": {
                "OBS-PRICE-NEG": observations.get("OBS-PRICE-NEG", {}).get("message"),
                "OBS-TARIFF-NEG": observations.get("OBS-TARIFF-NEG", {}).get("message"),
            },
            "consequence": "registered, not fixed: the driver-domain guard fires before the calculator, and "
                           "a negative total would be refused as well. Whether the contract should admit "
                           "negative prices is an owner decision; this attempt asserts no position.",
        },
        "OQ_4_reserve_sign_routing": {
            "applies_to_this_card": card == "M10",
            "statement": "Within reserve_depletion the four reserve stock drivers are non-negative "
                         "([0, inf)) while `reserve_revisions` is explicitly signed ((-inf, inf)); a "
                         "negative `additions` is therefore refused and every downward reserve movement "
                         "must be routed through `reserve_revisions`.",
            "enumerated_counts": {
                "reserve_volume_driver_count": len(facts["reserve_volume_drivers"]),
                "reserve_volume_drivers_non_negative_count":
                    facts["reserve_volume_drivers_non_negative_count"],
                "reserve_volume_drivers_signed_count": facts["reserve_volume_drivers_signed_count"],
                "reserve_volume_drivers": facts["reserve_volume_drivers"],
            },
            "observed_probe": {
                "OBS-REVISION-POS": observations.get("OBS-REVISION-POS", {}).get("actual"),
                "note": "a positive revision keeps the balance and does not change revenue",
            },
            "consequence": "registered as contract, not as a defect: the mapping must route signs "
                           "correctly. No product change.",
        },
        "OQ_5_concurrent_external_writer": {
            "statement": "Production source files under scripts/ carry a LastWriteTime inside this "
                         "attempt's window even though this attempt issued no write command against any "
                         "production path; their sha256 values are byte-identical to the task anchors.",
            "enumerated_counts": {
                "files_with_mtime_inside_the_attempt_window":
                    integrity["production_working_tree_mtime_finding"]["file_count"],
                "file_list": [row["path"] for row in
                              integrity["production_working_tree_mtime_finding"]
                              ["files_with_mtime_inside_the_attempt_window"]],
                "distinct_mtimes": sorted({row["mtime"] for row in
                                           integrity["production_working_tree_mtime_finding"]
                                           ["files_with_mtime_inside_the_attempt_window"]}),
            },
            "consequence": "mtime alone cannot serve as an untouched-proof for production files in this "
                           "window; the sha256 evidence can. Needs a binding ruling on how concurrent "
                           "writers are treated.",
        },
        "OQ_6_binding_provenance": {
            "statement": "I-00-B binds the isolation plan and the two-stage command rule but materialises "
                         "no checkout tree, so this attempt materialised its own read-only snapshot.",
            "enumerated_counts": {
                "isolated_snapshot_path": "iso/checkout_scripts",
                "isolated_copy_equals_production": True,
                "evidence": "evidence/%s/source_manifest.json -> isolated_copy_hashes" % card,
            },
            "consequence": "the code under test is byte-identical either way; if the intended binding is a "
                           "checkout materialised by I-00-B, that is a scope deviation to record.",
        },
    }

    with open(os.path.join(evidence, "oq_rulings.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    print("card", card)
    print("OQ_1 batch optional drivers without a declared default",
          facts["batch_optional_drivers_without_declared_default_total"], "/",
          facts["batch_optional_driver_count"],
          "this card:", target["optional_drivers_without_declared_default"])
    print("OQ_2 ratio drivers with non-[0,1] bounds",
          facts["ratio_drivers_whose_effective_bounds_are_not_0_1_count"])
    print("OQ_3 per-unit/per-activity drivers",
          facts["revenue_per_unit_and_revenue_per_activity_driver_count"], "negative-capable",
          facts["revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values_count"])
    print("OQ_4 reserve_volume drivers",
          facts["reserve_volume_drivers_non_negative_count"], "non-negative,",
          facts["reserve_volume_drivers_signed_count"], "signed")
    print("OQ_5 production files with an in-window mtime",
          integrity["production_working_tree_mtime_finding"]["file_count"])
    print("wrote", os.path.join(evidence, "oq_rulings.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
