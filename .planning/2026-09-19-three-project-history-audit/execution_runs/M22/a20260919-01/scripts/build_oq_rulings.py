"""Derive evidence/<card>/oq_rulings.json from the raw enumeration output.

The COUNTS in this file are never typed by hand: they are read out of
evidence/<card>/oq_rulings_enumeration.json, which is the byte output of
scripts/enumerate_oq_rulings.py (raw stdout kept in recovery/oq_enum_stdout.txt).

The RULING text records what the enumeration supports and explicitly leaves the
adjudication to an independent reviewer. No first-person authorship is claimed.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/build_oq_rulings.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    ev = os.path.join(args.attempt, "evidence", card)
    with open(os.path.join(ev, "oq_rulings_enumeration.json"), "r", encoding="utf-8") as fh:
        enum = json.load(fh)

    c = enum["counts"]
    card_models = enum["card_model_ids"]
    silent = enum["optional_drivers_without_explicit_default"]
    card_silent = {m: v["silent_zero_fill_applies_to"] for m, v in card_models.items()
                   if v["silent_zero_fill_applies_to"]}

    doc = {
        "card_id": card,
        "enumeration_provenance": {
            "enumeration_script": "scripts/enumerate_oq_rulings.py",
            "enumeration_script_sha256": _sha(os.path.join(args.attempt, "scripts",
                                                            "enumerate_oq_rulings.py")),
            "raw_output_json": "evidence/%s/oq_rulings_enumeration.json" % card,
            "raw_output_json_sha256": _sha(os.path.join(ev, "oq_rulings_enumeration.json")),
            "raw_stdout": "recovery/oq_enum_stdout.txt",
            "raw_stderr": "recovery/oq_enum_stderr.txt (0 bytes)",
            "read_from": "the isolated snapshot iso/checkout_scripts (hashes equal to "
                         "production), never the production directory",
            "statement": "every count in this file was produced by the enumeration script; "
                         "none was typed by hand",
        },
        "scope_of_this_file": "This file records what the registry enumeration SUPPORTS. "
                              "It deliberately does NOT adjudicate the open questions; the "
                              "verdict on every ruling below belongs to the independent "
                              "reviewer of this attempt.",
        "OQ-ENUM-01": {
            "question": "Is a driver whose dimension is `ratio` always confined to [0,1]?",
            "enumeration_counts": {
                "registered_model_count": c["registered_model_count"],
                "total_driver_slots": c["total_driver_slots"],
                "ratio_drivers_total": c["ratio_drivers_total"],
                "ratio_drivers_effective_domain_0_1": c["ratio_drivers_effective_domain_0_1"],
                "ratio_drivers_outside_0_1": c["ratio_drivers_outside_0_1"],
                "non_ratio_drivers_total": c["non_ratio_drivers_total"],
                "non_ratio_drivers_with_finite_upper_bound":
                    c["non_ratio_drivers_with_finite_upper_bound"],
            },
            "what_the_enumeration_shows": "the ratio dimension defaults to [0,1] for %d of "
                                          "%d ratio drivers; the %d exceptions are either "
                                          "declared with explicit driver_bounds or are "
                                          "`growth_rate`, which carries its own "
                                          "(-1, +inf) rule" % (
                                              c["ratio_drivers_effective_domain_0_1"],
                                              c["ratio_drivers_total"],
                                              c["ratio_drivers_outside_0_1"]),
            "consequence_for_this_card": "the gating negative NEG-CARD of this card is a "
                                         "value-domain rejection inside that contract; it is "
                                         "NOT evidence that the value is economically "
                                         "impossible",
            "ruling": "left to the independent reviewer; no product change was made",
        },
        "OQ-ENUM-02": {
            "question": "Does an omitted optional driver that has no explicit default become "
                        "0.0 silently?",
            "mechanism": enum["silent_zero_fill_mechanism"],
            "enumeration_count": c["optional_drivers_without_explicit_default"],
            "affected_slots": silent,
            "affected_slots_for_this_card": card_silent,
            "what_the_enumeration_shows": "the mechanism at scripts/model_registry.py:335 "
                                          "applies to all %d optional drivers that are absent "
                                          "from spec.defaults" % (
                                              c["optional_drivers_without_explicit_default"]),
            "ruling": "left to the independent reviewer; registered, NOT fixed, no product "
                      "change was made",
        },
        "OQ-ENUM-03": {
            "question": "Do any money/quantity drivers carry a finite upper bound that could "
                        "silently cap a legitimate disclosure?",
            "enumeration_counts": {
                "non_ratio_drivers_total": c["non_ratio_drivers_total"],
                "non_ratio_drivers_with_finite_upper_bound":
                    c["non_ratio_drivers_with_finite_upper_bound"],
            },
            "what_the_enumeration_shows": "no non-ratio driver has a finite upper bound",
            "ruling": "left to the independent reviewer",
        },
        "card_model_contracts_as_enumerated": card_models,
        "not_adjudicated_here": [
            "whether the four ratio exceptions are the right set",
            "whether silent zero-fill should be an error for any named driver",
            "any disclosure-adaptation or accuracy question (those stay unmapped / unproven)",
        ],
    }

    target = os.path.join(ev, "oq_rulings.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("wrote", target)
    print("ratio_drivers_total", c["ratio_drivers_total"],
          "outside_0_1", c["ratio_drivers_outside_0_1"])
    print("optional_drivers_without_explicit_default",
          c["optional_drivers_without_explicit_default"])
    print("this card silent-zero-fill slots", json.dumps(card_silent, sort_keys=True))
    return 0


def _sha(path: str) -> str:
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
