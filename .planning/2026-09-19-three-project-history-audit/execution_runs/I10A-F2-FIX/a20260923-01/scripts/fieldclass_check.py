#!/usr/bin/env python3
"""I10A-F2-FIX crafted per-field-class omit check (oracle §4 family non-vacuity).

Runs calculate_model_path (the real entry) against crafted inputs covering the
frozen field-class split and records, per case: raised? / message / value.
Exit 0 always; the JSON is the evidence.

Cases (frozen expectations):
  FC1 unit_sales, other_revenue OMITTED (RAISE class)   -> ForecastInputError
     "missing driver for unit_sales: other_revenue has no explicit default"
  FC2 resource, other_revenue OMITTED (RAISE class)     -> same shape
  FC3 unit_sales, timing_factor OMITTED (tolerant class)-> OK, timing 1.0
  FC4 unit_sales, other_revenue EXPLICIT 0.0            -> OK, value == base*units*price
  FC5 unit_sales, other_revenue key present with None   -> existing malformed raise
     ("must be a list of parameter_ids"), never silent
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ATT / "iso" / "rf" / "scripts"))

from forecast.segments import calculate_model_path  # noqa: E402

YEARS = [2026, 2027]


def params(entries: dict[str, tuple[float, str, str]]) -> dict:
    index = {}
    for pid, (value, dimension, scenario) in entries.items():
        index[pid] = {
            "value": value,
            "unit": "test",
            "dimension": dimension,
            "period": "FY2026" if pid.endswith("26") else "FY2027",
            "scenario": scenario,
        }
    return index


def base_params() -> dict:
    return params(
        {
            "u26": (10.0, "quantity", "all"),
            "u27": (11.0, "quantity", "all"),
            "p26": (5.0, "revenue_per_unit", "all"),
            "p27": (5.0, "revenue_per_unit", "all"),
            "t26": (1.0, "ratio", "all"),
            "t27": (1.0, "ratio", "all"),
            "o26": (0.0, "revenue", "all"),
            "o27": (0.0, "revenue", "all"),
        }
    )


CASES = []


def case(cid, model, driver_ids, expect, expect_msg_contains=None, note=""):
    CASES.append(
        {
            "id": cid,
            "model": model,
            "driver_ids": driver_ids,
            "expect": expect,
            "expect_msg_contains": expect_msg_contains,
            "note": note,
        }
    )


case(
    "FC1",
    "unit_sales",
    {"units": ["u26", "u27"], "unit_revenue": ["p26", "p27"]},
    "raise",
    "missing driver for unit_sales: other_revenue has no explicit default",
    "RAISE class omitted",
)
case(
    "FC2",
    "resource",
    {
        "saleable_volume": ["u26", "u27"],
        "realized_price": ["p26", "p27"],
    },
    "raise",
    "missing driver for resource: other_revenue has no explicit default",
    "RAISE class omitted (I-10-A GREEN requirement)",
)
case(
    "FC3",
    "unit_sales",
    {"units": ["u26", "u27"], "unit_revenue": ["p26", "p27"]},
    "ok_declared_default",
    None,
    "tolerant class: timing_factor omitted -> declared 1.0 (but FC1 shows "
    "other_revenue still raises; FC3 uses explicit other_revenue below)",
)
case(
    "FC4",
    "unit_sales",
    {
        "units": ["u26", "u27"],
        "unit_revenue": ["p26", "p27"],
        "timing_factor": ["t26", "t27"],
        "other_revenue": ["o26", "o27"],
    },
    "ok_value",
    None,
    "explicit 0.0 accepted (I-10-B R-B1-N3); values must equal "
    "10*5, 11*5 with other 0",
)
case(
    "FC5",
    "unit_sales",
    {
        "units": ["u26", "u27"],
        "unit_revenue": ["p26", "p27"],
        "timing_factor": ["t26", "t27"],
        "other_revenue": None,
    },
    "raise_malformed",
    "must be a list of parameter_ids",
    "present-but-None is malformed, never silent",
)
# FC3 corrected: tolerant class means ONLY timing_factor omitted while the
# RAISE-class driver is supplied explicitly.
CASES[2]["driver_ids"] = {
    "units": ["u26", "u27"],
    "unit_revenue": ["p26", "p27"],
    "other_revenue": ["o26", "o27"],
}


def main() -> int:
    index = base_params()
    results = []
    all_ok = True
    for c in CASES:
        row = {"id": c["id"], "model": c["model"], "note": c["note"]}
        try:
            out = calculate_model_path(
                c["model"], 100.0, c["driver_ids"], index, YEARS, "base"
            )
            values = [out["annual_revenue"][str(y)] for y in YEARS]
            row["outcome"] = "ok"
            row["annual_revenue"] = values
            if c["expect"].startswith("ok"):
                row["pass"] = True
                if c["expect"] == "ok_value":
                    row["pass"] = values == [50.0, 55.0]
                if c["expect"] == "ok_declared_default":
                    row["pass"] = out["driver_values"]["timing_factor"] == {
                        "2026": 1.0,
                        "2027": 1.0,
                    }
            else:
                row["pass"] = False
        except Exception as exc:  # noqa: BLE001 — classify, do not swallow
            row["outcome"] = "raised"
            row["error_type"] = type(exc).__name__
            row["error"] = str(exc)
            if c["expect"] == "raise":
                row["pass"] = (
                    row["error_type"] == "ForecastInputError"
                    and row["error"] == c["expect_msg_contains"]
                )
            elif c["expect"] == "raise_malformed":
                row["pass"] = (
                    row["error_type"] == "ForecastInputError"
                    and c["expect_msg_contains"] in row["error"]
                )
            else:
                row["pass"] = False
        all_ok = all_ok and bool(row["pass"])
        results.append(row)
    payload = {
        "artifact": "field_class_check",
        "cases": results,
        "all_pass": all_ok,
    }
    out_path = ATT / "evidence" / "field_class_check.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({"all_pass": all_ok, "cases": [(r["id"], r["pass"]) for r in results]}))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
