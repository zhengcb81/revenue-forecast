"""Build evidence/<CARD>/oq_rulings.json from the raw enumeration output (standard library only).

Every count in the narrative is READ FROM ``evidence/<CARD>/oq_enumeration.json`` (produced by
``scripts/enumerate_driver_bounds.py``); none is hand-typed. The OQ list mirrors
``scripts/card_facts.json``'s ``open_questions`` (or, if that file is absent, the attempt's
``handoff.json``) one-to-one, so the numbering a reader sees in ``decision.md`` / ``review.md``
is the SAME numbering the owner sees in ``handoff.json`` - the F-03 finding of 2026-09-20 was
exactly that these two lists disagreed.

Attribution is deliberately third-person and objective:

  enumerated_by : the implementer session of attempt a20260919-01, by running the script above
                  (automated enumeration; no human counting)
  reviewed_by   : an independent reviewer, 2026-09-20, who re-implemented the enumeration and
                  reported 40/3 (declared ratio_drivers set) versus 41/4 (dimension predicate),
                  ruling the dimension predicate authoritative - hence the counts below

The implementer never writes an "accepted" ruling for its own evidence, and no reviewer is
named as an author of this file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


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
    enum_path = os.path.join(evidence, "oq_enumeration.json")
    enum = load_json(enum_path)
    totals = enum["registry_totals"]
    counts = enum["counts"]
    model_id = enum["model_id"]

    facts_path = os.path.join(attempt, "scripts", "card_facts.json")
    handoff_path = os.path.join(attempt, "handoff.json")
    if os.path.isfile(facts_path):
        open_questions = load_json(facts_path)["open_questions"]
        numbering_source = "scripts/card_facts.json:open_questions (mirrors handoff.json 1:1)"
    elif os.path.isfile(handoff_path):
        open_questions = load_json(handoff_path)["open_questions"]
        numbering_source = "handoff.json:open_questions (read directly)"
    else:
        open_questions = []
        numbering_source = "NONE AVAILABLE at build time - the OQ list could not be mirrored"

    oq_blocks = {}
    for index, question in enumerate(open_questions, start=1):
        oq_blocks["OQ-%02d" % index] = question

    optional_without_default = counts["card_optional_drivers_without_an_explicit_default_names"]
    signed_names = counts["card_drivers_signed_and_unbounded_names"]

    rulings = {
        "card_id": card,
        "model_id": model_id,
        "generated_by_script": "scripts/build_oq_rulings.py",
        "raw_enumeration": {
            "file": "evidence/%s/oq_enumeration.json" % card,
            "sha256": sha256_file(enum_path),
            "produced_by": "scripts/enumerate_driver_bounds.py",
            "command": "<attempt>/iso/venv/Scripts/python.exe -X utf8 -B "
                       "<attempt>/scripts/enumerate_driver_bounds.py --card %s --attempt "
                       "<attempt> --code-root <attempt>/iso/checkout_scripts" % card,
        },
        "attribution": {
            "enumerated_by": "the implementer session of attempt a20260919-01, by executing the "
                             "enumeration script above against the isolated read-only copy "
                             "(automated; no human counting)",
            "reviewed_by": "an independent reviewer (2026-09-20): the reviewer re-implemented the "
                           "enumeration independently and reported 40/3 under the declared "
                           "ratio_drivers-set predicate versus 41/4 under the dimension predicate, "
                           "ruling the dimension predicate authoritative and matching the M05-M08 "
                           "r3 correction. The counts below follow it.",
            "author_of_this_file": "the implementer session (scripts/build_oq_rulings.py); no "
                                   "reviewer is named as an author",
            "counting_rule": "every number below is read from the raw enumeration file; the "
                             "script does not accept hand-typed counts",
            "oq_numbering_source": numbering_source,
        },
        "enumerated_counts_as_read_from_the_raw_file": {
            "registry_models": totals["models"],
            "registry_drivers": totals["drivers"],
            "registry_ratio_drivers": totals["ratio_drivers_by_dimension"],
            "registry_ratio_drivers_by_registry_ratio_set":
                totals["ratio_drivers_by_registry_ratio_set"],
            "registry_ratio_drivers_whose_bounds_are_not_0_1":
                totals["ratio_drivers_whose_bounds_are_not_0_1"],
            "registry_optional_drivers_without_an_explicit_default_slots_total":
                totals["optional_drivers_without_an_explicit_default_slots_total"],
            "registry_optional_drivers_without_an_explicit_default_models_total":
                totals["optional_drivers_without_an_explicit_default_models_total"],
            "card_required_drivers": counts["card_required_drivers"],
            "card_optional_drivers": counts["card_optional_drivers"],
            "card_optional_drivers_without_an_explicit_default":
                counts["card_optional_drivers_without_an_explicit_default"],
            "card_drivers_signed_and_unbounded": counts["card_drivers_signed_and_unbounded"],
            "card_drivers_with_lower_bound_exactly_zero":
                counts["card_drivers_with_lower_bound_exactly_zero"],
            "card_drivers_with_inclusive_upper_bound_one":
                counts["card_drivers_with_inclusive_upper_bound_one"],
        },
        "enumerated_counts_with_units": {
            "models_total_registry_wide": totals["models"],
            "driver_slots_total_registry_wide": totals["drivers"],
            "ratio_driver_slots_total_registry_wide_by_dimension_predicate":
                totals["ratio_drivers_by_dimension"],
            "ratio_driver_slots_total_registry_wide_by_declared_set_predicate":
                totals["ratio_drivers_by_registry_ratio_set"],
            "ratio_driver_slots_not_bounded_0_1_registry_wide":
                totals["ratio_drivers_whose_bounds_are_not_0_1"],
            "optional_driver_slots_without_an_explicit_default_registry_wide":
                totals["optional_drivers_without_an_explicit_default_slots_total"],
            "models_owning_at_least_one_such_optional_slot_registry_wide":
                totals["optional_drivers_without_an_explicit_default_models_total"],
            "unit_note": "a slot is a (model, driver) pair; a model-level count counts a model "
                         "once however many such slots it owns. Both numbers are given because "
                         "earlier batches quoted one or the other without labelling the unit.",
        },
        "enumerated_contract_facts": {
            "ratio_driver_predicate": enum["ratio_driver_predicate"],
            "ratio_drivers_whose_bounds_are_not_0_1":
                enum["ratio_drivers_whose_bounds_are_not_0_1"],
            "silent_zero_fill": {
                "mechanism": enum["fill_mechanism_line"],
                "instances_for_this_model": optional_without_default,
                "count": counts["card_optional_drivers_without_an_explicit_default"],
                "why_it_matters_for_this_card":
                    "for %s the filled drivers are %s: omitting them asserts 'there is no such "
                    "revenue', which is indistinguishable from 'the disclosure was not found'. "
                    "No product change was made." % (model_id, ", ".join(optional_without_default)),
                "status": "registered, NOT fixed",
            },
            "signed_and_unbounded_drivers": {
                "names": signed_names,
                "count": counts["card_drivers_signed_and_unbounded"],
                "mechanism": "scripts/model_registry.py:352-353 rejects a negative calculated "
                             "revenue (ModelRegistryError 'calculated revenue cannot be negative')",
                "status": "registered, NOT fixed",
            },
            "inclusive_domain_edges": {
                "drivers_with_lower_bound_exactly_zero":
                    counts["card_drivers_with_lower_bound_exactly_zero_names"],
                "drivers_with_inclusive_upper_bound_one":
                    counts["card_drivers_with_inclusive_upper_bound_one_names"],
                "handling": "the edges are exercised by the non-gating observation "
                            "OBS-BOUND-INCLUSIVE and by the card-specific negative case, which is "
                            "built with set_driver_element so it fails the VALUE-domain guard "
                            "rather than the array-length guard",
                "status": "closed for this card by observation; no product change",
            },
        },
        "open_questions_mirroring_handoff": oq_blocks,
        "no_product_change_made": True,
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(evidence, "oq_rulings.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(rulings, handle, ensure_ascii=True, indent=1)
        handle.write("\n")
    print("wrote %s" % path)
    print("counts quoted from the raw enumeration: %s"
          % json.dumps(rulings["enumerated_counts_as_read_from_the_raw_file"], sort_keys=True))
    print("oq ids mirrored: %s" % sorted(oq_blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
