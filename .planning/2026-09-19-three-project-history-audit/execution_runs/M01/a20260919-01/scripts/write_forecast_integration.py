"""Read-only inspection record for the production forecast entry point.

IMPORTANT: this script only READS scripts/forecast/segments.py and records its
sha256 plus the facts observed at the call site. It never imports or runs it.
Exercising the production entry point is an I-10-A obligation, not an M-card
step B/C obligation.

ASCII-only stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

PLAN = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast", ".planning",
                    "2026-09-19-three-project-history-audit")

CARDS = {"M01": "direct_growth", "M02": "direct_revenue", "M03": "unit_sales",
         "M04": "capacity_utilization"}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    rf = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    rel = os.path.join("scripts", "forecast", "segments.py")
    target = os.path.join(rf, rel)
    payload = {
        "card_id": None,
        "model_id": None,
        "entry_point": "scripts/forecast/segments.py calculate_model_path(model, base_revenue, driver_ids, "
                       "parameter_index, years, scenario)",
        "source_file": target,
        "source_sha256": sha256_file(target),
        "how_observed": "read-only source inspection of the call site during this attempt",
        "was_it_run": False,
        "was_it_imported": False,
        "observed_facts": [
            "calculate_model_path validates model membership against MODEL_SPECS and the scenario against SCENARIOS",
            "it collects required and optional driver parameter IDs and rejects missing/extra drivers",
            "it resolves driver series from the parameter index per year and scenario, then calls "
            "calculate_registered_model(model, base_revenue, drivers, years)",
            "ModelRegistryError raised by the model layer is re-wrapped as ForecastInputError, so a formula "
            "rejection surfaces as a forecast-input rejection rather than an unhandled error",
            "it re-checks finite and non-negative revenue for every year before returning annual_revenue keyed "
            "by year",
            "it returns the formula string, annual_revenue and the resolved driver values, i.e. the path is "
            "traceable back to parameter IDs",
        ],
        "why_it_was_not_run": [
            "card step B/C scope is calculate_registered_model only",
            "running the production forecast entry point belongs to I-10-A step E (I-10-A is a separate card "
            "and is explicitly NOT a dependency of the M cards)",
            "no I-11 parameter calibration exists yet, so a production run would have no reviewed inputs",
        ],
        "consequence_for_this_card": "the field -> parameter -> model -> output wiring claim is limited to "
                                     "calculate_registered_model; the production forecast entry-point mapping "
                                     "stays unverified and is carried in handoff.json as an I-10-A obligation",
        "reviewer": "PENDING_INDEPENDENT_REVIEW",
    }
    for card, model in CARDS.items():
        doc = dict(payload)
        doc["card_id"] = card
        doc["model_id"] = model
        out = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card,
                           "forecast_integration.json")
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
        print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
