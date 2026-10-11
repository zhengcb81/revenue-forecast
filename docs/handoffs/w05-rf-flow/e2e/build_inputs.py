"""W05-RF-FLOW CLI E2E input builder (scratch evidence, not product code).

Builds two frozen schema-3.10 fixture inputs for the isolated CLI run:

* case1_acquisition — control date 2026-05-31 (sealed) post-control contribution
  2026-05-31..2026-06-30 = 1.29190208 CNY million (sealed purchase-to-end
  revenue 1,291,902.08 CNY) plus a clearly synthetic H2 estimate, composed into
  an explicit FY2026 derived bridge with a scope rationale, and fed to the
  forecast DAG through the acquisition_contribution adjustment;
* case2_offset_fy — non-12-31 fiscal year (FYE 06-30) short flows including a
  10-day window and an exact three-way partition sum.

Every amount except 1.29190208 is synthetic fixture data; the company names say
so. Nothing here claims a real reported company revenue.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from test_recognition_bridge import forecast_document  # noqa: E402
from test_w05_dated_contribution_contract import (  # noqa: E402
    add_window_parameter,
    parameter,
)

OUT = Path(sys.argv[1])

SCOPE_RATIONALE = (
    "pre-control window 2026-01-01..2026-05-30 is outside the group "
    "consolidation perimeter from control date 2026-05-31 (out-of-scope, not "
    "missing data, never zero-filled); post-control amount is the sealed "
    "purchase-to-end figure, the H2 amount is a synthetic fixture estimate"
)


def case1_acquisition() -> dict:
    data = forecast_document()
    data["schema_version"] = "3.10"
    data["company_name"] = "FixtureCo Acquisition Contribution (synthetic)"
    add_window_parameter(
        data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        definition="acquired entity revenue from control date 2026-05-31 to period end (purchase-to-end)",
    )
    scenario_ids: dict[str, list[str]] = {"low": [], "base": [], "high": []}
    h2_values = {"low": 30.0, "base": 40.0, "high": 50.0}
    y2_values = {"low": 200.0, "base": 300.0, "high": 400.0}
    for scenario in ("low", "base", "high"):
        h2_id = f"cmp_h2_2026_{scenario}"
        add_window_parameter(
            data, h2_id, h2_values[scenario], "2026-07-01", "2026-12-31", 2026,
            kind="scenario_stress", claim=False,
            definition=f"H2 2026 contribution ({scenario}) under continued control",
            rationale="synthetic scenario stress; fixture amount, not a reported figure",
        )
        parameter(data, h2_id)["scenario"] = scenario
        fy_id = f"cmp_fy2026_{scenario}"
        add_window_parameter(
            data, fy_id, 1.29190208 + h2_values[scenario], "2026-01-01", "2026-12-31", 2026,
            kind="derived_fact", claim=False, formula="x0+x1",
            input_parameter_ids=["cmp_post_2026", h2_id],
            definition="full-year 2026 group contribution of the acquired entity",
            rationale=SCOPE_RATIONALE,
        )
        parameter(data, fy_id)["scenario"] = scenario
        y2_id = f"cmp_fy2027_{scenario}"
        add_window_parameter(
            data, y2_id, y2_values[scenario], "2027-01-01", "2027-12-31", 2027,
            kind="scenario_stress", claim=False,
            definition="full-year 2027 contribution under continued control",
            rationale="synthetic scenario stress; fixture amount, not a reported figure",
        )
        parameter(data, y2_id)["scenario"] = scenario
        scenario_ids[scenario] = [fy_id, y2_id]
    data.setdefault("forecast_adjustments", []).append(
        {
            "name": "acq_scope_change",
            "category": "acquisition_contribution",
            "scenario_parameter_ids": scenario_ids,
        }
    )
    return data


def case2_offset_fy() -> dict:
    data = forecast_document()
    data["schema_version"] = "3.10"
    data["company_name"] = "FixtureCo Offset Fiscal Year (synthetic)"
    data["fiscal_year_end"] = "06-30"
    # FY2026 = 2025-07-01..2026-06-30 under a 06-30 fiscal year end.
    add_window_parameter(data, "fy26_a", 7.0, "2025-07-01", "2025-12-31", 2026)
    add_window_parameter(data, "fy26_b", 10.0, "2026-01-01", "2026-05-31", 2026)
    add_window_parameter(data, "fy26_c", 3.0, "2026-06-01", "2026-06-30", 2026)
    add_window_parameter(
        data, "fy26_ten_day", 1.0, "2026-06-01", "2026-06-10", 2026,
        definition="synthetic ten-day observation window (supporting fact)",
    )
    add_window_parameter(
        data, "fy26_total", 20.0, "2025-07-01", "2026-06-30", 2026,
        kind="derived_fact", claim=False, formula="x0+x1+x2",
        input_parameter_ids=["fy26_a", "fy26_b", "fy26_c"],
        definition="explicit full-year composition over the offset fiscal window",
    )
    return data


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in (
        ("case1_acquisition", case1_acquisition),
        ("case2_offset_fy", case2_offset_fy),
    ):
        data = builder()
        path = OUT / f"{name}.input.json"
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {path} sha256={__import__('hashlib').sha256(path.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
