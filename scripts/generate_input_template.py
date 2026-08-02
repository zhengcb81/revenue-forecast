"""Emit a schema 3.6 input skeleton pre-filled with correct field names.

The 688785 exercise showed ~65% of input-build failures are field-name / shape
mistakes the author could never infer from docs alone. This generator emits a
structurally consistent skeleton (correct keys, a strict 9-key capture, wired
parameter/claim/source references, the nine research dimensions and six
management categories) so the author fills in *values*, not field names.

Every hash is a ``0``x64 placeholder marked for recompute; the intended workflow
is: edit values/excerpts -> ``lint_input.py`` (pre-flight) -> ``fix_hashes.py``
(recompute hashes) -> ``revenue_forecast.py --validate-only``.

CLI mirrors ``revenue_forecast.py`` conventions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from revenue_core import (  # noqa: E402
    FORECAST_SCHEMA_VERSION,
    MANAGEMENT_COMMUNICATION_CATEGORIES,
    RESEARCH_DIMENSIONS,
)

PLACEHOLDER_HASH = "0" * 64


def build_template(
    name: str,
    base_year: int,
    forecast_years: list[int],
    currency: str,
    unit: str,
    segment_names: list[str],
) -> dict[str, Any]:
    """Build a schema 3.6 skeleton with FIXME placeholders and consistent references."""
    base_year = int(base_year)
    forecast_years = sorted({int(year) for year in forecast_years})
    as_of = f"{base_year}-06-30"
    source_id = "src_primary_filing"
    monetary_unit = f"{currency} {unit}"

    source: dict[str, Any] = {
        "source_id": source_id,
        "source_type": "exchange_filing",
        "title": "FIXME: filing title",
        "publisher": "FIXME: filing publisher or exchange",
        "url": "https://FIXME.invalid/replace-with-real-filing-url",
        "published_date": f"{base_year}-01-15",
        "accessed_date": as_of,
        "page_or_section": "FIXME: revenue note page or section",
        "capture": {
            "capture_schema_version": "1.0",
            "capture_method": "browser_open",
            "tool_name": "FIXME: capture tool name",
            "tool_call_id": "FIXME: capture tool call id",
            "captured_date": as_of,
            "snapshot_sha256": PLACEHOLDER_HASH,
            "content_treatment": "untrusted_data_only",
            "prompt_injection_status": "not_detected",
            "receipt_sha256": PLACEHOLDER_HASH,
        },
    }

    parameters: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []

    def add_parameter(parameter_id: str, kind: str, value: float, period: str,
                      dimension: str = "revenue", scenario: str | None = None,
                      rationale: str | None = None) -> str:
        parameters.append({
            "parameter_id": parameter_id,
            "kind": kind,
            "value": value,
            "unit": monetary_unit if dimension == "revenue" else "ratio",
            "period": period,
            "definition": f"FIXME: define {parameter_id}",
            "dimension": dimension,
            "time_basis": "annual",
            "source_ids": [source_id],
            "scenario": scenario,
            "rationale": rationale,
            "claim_ids": [f"claim_{parameter_id}"],
        })
        claims.append({
            "claim_id": f"claim_{parameter_id}",
            "source_id": source_id,
            "target_type": "parameter",
            "target_id": parameter_id,
            "support_type": "rationale_support",
            "locator": "FIXME: locator within the source",
            "excerpt": f"FIXME: checked excerpt supporting {parameter_id}.",
            "excerpt_sha256": PLACEHOLDER_HASH,
            "content_sha256": PLACEHOLDER_HASH,
            "capture_receipt_sha256": PLACEHOLDER_HASH,
            "verification_status": "opened_and_checked",
            "verified_by": "FIXME: research agent",
            "verified_date": as_of,
        })
        return parameter_id

    reported_id = "reported_total"
    add_parameter(reported_id, "reported_fact", 0.0, f"FY{base_year}", rationale="FIXME: reported total revenue")

    segment_base_ids: list[str] = []
    for segment in segment_names:
        slug = segment.lower().replace(" ", "_")
        base_pid = f"{slug}_base"
        add_parameter(base_pid, "reported_fact", 0.0, f"FY{base_year}", rationale=f"FIXME: {segment} base revenue")
        segment_base_ids.append(base_pid)

    segments: list[dict[str, Any]] = []
    for segment, base_pid in zip(segment_names, segment_base_ids):
        slug = segment.lower().replace(" ", "_")
        scenarios: dict[str, Any] = {}
        for scenario in ("low", "base", "high"):
            driver_ids = [
                add_parameter(
                    f"{slug}_{scenario}_{year}", "analyst_assumption", 0.1, f"FY{year}",
                    dimension="ratio", scenario=scenario,
                    rationale=f"FIXME: {segment} {scenario} growth rate for FY{year}",
                )
                for year in forecast_years
            ]
            scenarios[scenario] = {
                "model": "direct_revenue",
                "driver_parameter_ids": {"revenue": driver_ids},
                "rationale": f"FIXME: {segment} {scenario} revenue path rationale",
            }
        segments.append({
            "name": segment,
            "base_revenue_parameter_id": base_pid,
            "recognition": {
                "mode": "modeled_as_recognized",
                "timing": "point_in_time",
                "trigger": "FIXME: recognition trigger",
                "presentation": "gross",
            },
            "scenarios": scenarios,
        })

    historical: list[dict[str, Any]] = []
    for year in (base_year, base_year - 1):
        claim_id = f"claim_history_{year}"
        claims.append({
            "claim_id": claim_id,
            "source_id": source_id,
            "target_type": "historical_revenue",
            "target_id": f"historical_revenue:{year}",
            "support_type": "exact_value",
            "locator": "FIXME: historical revenue locator",
            "excerpt": f"FIXME: checked excerpt for FY{year} revenue.",
            "excerpt_sha256": PLACEHOLDER_HASH,
            "content_sha256": PLACEHOLDER_HASH,
            "capture_receipt_sha256": PLACEHOLDER_HASH,
            "verification_status": "opened_and_checked",
            "verified_by": "FIXME: research agent",
            "verified_date": as_of,
        })
        historical.append({"year": year, "value": 0.0, "source_ids": [source_id], "claim_ids": [claim_id]})

    research = [
        {
            "dimension": dimension,
            "status": "data_gap",
            "conclusion": f"FIXME: {dimension} conclusion",
            "revenue_mechanism": f"FIXME: {dimension} revenue mechanism",
            "rationale": f"FIXME: why {dimension} remains a data gap, or set status=modeled_driver and map parameters",
        }
        for dimension in RESEARCH_DIMENSIONS
    ]
    management = [
        {
            "category": category,
            "status": "not_checked",
            "source_ids": [],
            "checked_date": as_of,
            "conclusion": f"FIXME: {category} review conclusion",
            "material_revenue_target_ids": [],
        }
        for category in MANAGEMENT_COMMUNICATION_CATEGORIES
    ]

    return {
        "_comment": (
            "Schema 3.6 skeleton. Replace every FIXME value, then run: "
            "lint_input.py <file>  ->  fix_hashes.py <file>  ->  "
            "revenue_forecast.py <file> --validate-only."
        ),
        "schema_version": FORECAST_SCHEMA_VERSION,
        "company_name": name,
        "as_of_date": as_of,
        "currency": currency,
        "unit": unit,
        "fiscal_year_end": "12-31",
        "base_year": base_year,
        "forecast_years": forecast_years,
        "sources": [source],
        "parameters": parameters,
        "evidence_claims": claims,
        "segments": segments,
        "reported_total_revenue_parameter_id": reported_id,
        "base_adjustment_parameter_ids": [],
        "historical_revenue": historical,
        "research_coverage": research,
        "management_communication_coverage": management,
        "growth_driver_tree": {
            "status": "data_gap",
            "drivers": [],
            "rationale": "FIXME: build a causal driver tree, or keep status=data_gap",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", required=True, help="company name")
    parser.add_argument("--base-year", type=int, required=True, help="base fiscal year (e.g. 2025)")
    parser.add_argument("--forecast-years", type=int, nargs="+", required=True, help="forecast years (e.g. 2026 2027)")
    parser.add_argument("--currency", default="USD", help="currency code (default USD)")
    parser.add_argument("--unit", default="million", help="monetary unit (default million)")
    parser.add_argument("--segments", nargs="+", required=True, help="segment display names")
    parser.add_argument("--output", type=Path, help="write skeleton here (default stdout)")
    args = parser.parse_args(argv)

    data = build_template(
        args.name, args.base_year, args.forecast_years,
        args.currency, args.unit, args.segments,
    )
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
