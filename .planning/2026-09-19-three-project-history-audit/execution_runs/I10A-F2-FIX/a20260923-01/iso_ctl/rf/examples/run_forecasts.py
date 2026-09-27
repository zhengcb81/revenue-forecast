"""Non-formal example: build and run revenue forecasts for 腾讯 (HK) and 微软 (US).

This script is NOT a production entry point. It demonstrates the input shape and
is intentionally kept out of the formal scripts/ package. Do not use its inputs
as a substitute for a properly researched forecast.
"""
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from revenue_core import run_forecast, FORECAST_SCHEMA_VERSION, canonical_sha256, text_sha256  # noqa: E402
from revenue_report import validate_forecast_output, render_markdown  # noqa: E402

SCENARIOS = ("low", "base", "high")
RESEARCH_DIMS = ("company_foundation", "growth_curve", "industry_market", "competition", "capacity", "technology", "policy", "customers", "demand")
MGMT_CATS = ("latest_annual_filing", "latest_results_release", "latest_earnings_call", "latest_investor_presentation", "latest_strategy_communication", "material_announcements_since_last_filing")


def _claim(cid, sid, ttype, tid, stype, excerpt, vdate, receipt_sha="a"*64, **extra):
    return {"claim_id": cid, "source_id": sid, "target_type": ttype, "target_id": tid,
            "support_type": stype, "locator": "Annual report", "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt), "content_sha256": "a"*64,
            "capture_receipt_sha256": receipt_sha,
            "verification_status": "opened_and_checked", "verified_by": "research-agent",
            "verified_date": vdate, **extra}


def _add_param(data, pid, value, year, scenario, kind="analyst_assumption", unit="RMB 100 million", dim="revenue"):
    p = {"parameter_id": pid, "kind": kind, "value": value, "unit": unit,
         "period": f"FY{year}", "definition": pid, "scenario": scenario,
         "rationale": "forecast", "source_ids": ["filing"]}
    p["dimension"] = dim
    p["time_basis"] = "annual"
    if dim in ("revenue",):
        p["currency"] = data["currency"]
        p["scale"] = data["unit"]
    data["parameters"].append(p)
    return pid


def build_tencent():
    """Build forecast input for 腾讯 (HK)."""
    data = {
        "schema_version": FORECAST_SCHEMA_VERSION,
        "company_name": "腾讯控股",
        "as_of_date": "2026-07-21",
        "currency": "CNY",
        "unit": "100 million",
        "fiscal_year_end": "12-31",
        "base_year": 2024,
        "forecast_years": [2025, 2026, 2027],
        "sources": [{
            "source_id": "filing",
            "source_type": "regulatory_filing",
            "title": "腾讯控股 2024 年報",
            "publisher": "Hong Kong Stock Exchange",
            "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2025/0408/2025040800668_c.pdf",
            "accessed_date": "2026-07-21", "page_or_section": "Revenue note", "published_date": "2025-04-08",
        }],
        "evidence_claims": [],
        "parameters": [],
        "historical_revenue": [
            {"year": 2023, "value": 6090.0, "source_ids": ["filing"], "claim_ids": []},
            {"year": 2024, "value": 6603.0, "source_ids": ["filing"], "claim_ids": []},
        ],
        "segments": [
            {
                "name": "Tencent",
                "base_revenue": 6603.0, "base_revenue_parameter_id": "total_revenue_base",
                "recognition": {"mode": "modeled_as_recognized", "timing": "point_in_time",
                                "trigger": "service delivery", "presentation": "gross",
                                "modeled_presentation": "gross"},
                "scenarios": {},
            }
        ],
        "reported_total_revenue_parameter_id": "total_revenue_base",
        "research_coverage": [],
        "management_communication_coverage": [],
        "management_targets": [],
        "forecast_adjustments": [],
        "growth_driver_tree": {"roots": []},
    }

    # Parameters
    _add_param(data, "total_revenue_base", 6603.0, 2024, "base", kind="reported_fact")
    growth_rates = {"low": [0.05, 0.05, 0.04], "base": [0.08, 0.08, 0.07], "high": [0.11, 0.10, 0.09]}
    for sc in SCENARIOS:
        rev = 6603.0
        for i, year in enumerate([2025, 2026, 2027]):
            rev *= (1 + growth_rates[sc][i])
            _add_param(data, f"revenue_{sc}_{year}", round(rev, 1), year, sc)

    # Segment scenarios
    seg = data["segments"][0]
    for sc in SCENARIOS:
        ids = [f"revenue_{sc}_{y}" for y in [2025, 2026, 2027]]
        seg["scenarios"][sc] = {
            "model": "direct_revenue",
            "driver_parameter_ids": {"revenue": ids},
            "rationale": f"{sc} case: AI+advertising growth drives {sc} revenue",
        }

    # Source capture (must be before claims)
    for s in data["sources"]:
        s["accessed_date"] = data["as_of_date"]
        cap = {"capture_schema_version": "1.0", "capture_method": "local_document",
               "tool_name": "company-wiki-catalog", "tool_call_id": "preflight-hk",
               "captured_date": data["as_of_date"], "snapshot_sha256": "a"*64,
               "content_treatment": "untrusted_data_only", "prompt_injection_status": "not_detected"}
        cap["receipt_sha256"] = canonical_sha256(cap)
        s["capture"] = cap
    receipt_sha = data["sources"][0]["capture"]["receipt_sha256"]

    # Recognition claim
    rec_claim_id = "claim_recognition_Tencent"
    data["evidence_claims"].append(_claim(rec_claim_id, "filing", "recognition_policy",
        "recognition:Tencent", "policy_support", "Revenue recognized at point of service delivery", "2026-07-21",
        receipt_sha=receipt_sha))
    seg["recognition"]["basis_claim_ids"] = [rec_claim_id]

    # Evidence claims for history
    for rec in data["historical_revenue"]:
        cid = f"claim_history_{rec['year']}"
        rec["claim_ids"] = [cid]
        data["evidence_claims"].append(_claim(cid, "filing", "historical_revenue",
            f"historical_revenue:{rec['year']}", "exact_value",
            f"Tencent FY{rec['year']} revenue: {rec['value']} 100M CNY", "2026-07-21",
            receipt_sha=receipt_sha, extracted_value=rec["value"], unit="CNY 100 million", period=f"FY{rec['year']}"))

    # Parameter claims
    for p in data["parameters"]:
        cid = f"claim_parameter_{p['parameter_id']}"
        stype = "exact_value" if p["kind"] in ("reported_fact", "management_guidance") else "rationale_support"
        extra = {"extracted_value": p["value"], "unit": p["unit"], "period": p["period"]} if stype == "exact_value" else {}
        data["evidence_claims"].append(_claim(cid, "filing", "parameter", p["parameter_id"], stype,
            f"Evidence for {p['parameter_id']}", "2026-07-21", receipt_sha=receipt_sha, **extra))
        p["claim_ids"] = [cid]

    # Research coverage
    for dim in RESEARCH_DIMS:
        status = "modeled_driver" if dim == "growth_curve" else "data_gap"
        entry = {"dimension": dim, "status": status, "conclusion": f"Reviewed {dim} for Tencent", "source_ids": ["filing"]}
        if dim == "company_foundation":
            entry["revenue_mechanism"] = "Tencent generates revenue from VAS, advertising, fintech and enterprise services"
        if dim == "growth_curve":
            entry["revenue_mechanism"] = "AI-powered advertising and gaming drive growth"
        else:
            entry["revenue_mechanism"] = f"Indirect influence via {dim}"
        if status == "data_gap":
            entry["rationale"] = f"Dimension {dim} reviewed but not separately modeled"
        data["research_coverage"].append(entry)
    data["research_coverage"][-2]["conclusion"] = "Direct revenue scenario drives forecast"
    growth = next(r for r in data["research_coverage"] if r["dimension"] == "growth_curve")
    growth["parameter_ids"] = [p["parameter_id"] for p in data["parameters"] if p["scenario"] == "base"]

    # Management communication
    for cat in MGMT_CATS:
        data["management_communication_coverage"].append({"category": cat, "status": "checked",
            "source_ids": ["filing"], "checked_date": data["as_of_date"],
            "conclusion": "No material forward revenue target found", "material_revenue_target_ids": []})

    # Growth driver tree
    data["growth_driver_tree"] = {"status": "data_gap", "drivers": [],
        "rationale": "Detailed growth driver tree not modeled for this forecast"}

    return data


def build_microsoft():
    """Build forecast input for 微软 (US)."""
    data = {
        "schema_version": FORECAST_SCHEMA_VERSION,
        "company_name": "Microsoft Corporation",
        "as_of_date": "2026-07-21",
        "currency": "USD",
        "unit": "100 million",
        "fiscal_year_end": "06-30",
        "base_year": 2025,
        "forecast_years": [2026, 2027, 2028],
        "sources": [{
            "source_id": "filing",
            "source_type": "regulatory_filing",
            "title": "Microsoft 10-K FY2025",
            "publisher": "SEC EDGAR",
            "url": "https://www.sec.gov/Archives/edgar/data/789019/000095017025100235/msft-20250630.htm",
            "accessed_date": "2026-07-21", "page_or_section": "Revenue note", "published_date": "2025-07-30",
        }],
        "evidence_claims": [],
        "parameters": [],
        "historical_revenue": [
            {"year": 2024, "value": 2451.0, "source_ids": ["filing"], "claim_ids": []},
            {"year": 2025, "value": 3054.0, "source_ids": ["filing"], "claim_ids": []},
        ],
        "segments": [
            {
                "name": "Microsoft",
                "base_revenue": 3054.0, "base_revenue_parameter_id": "total_revenue_base",
                "recognition": {"mode": "modeled_as_recognized", "timing": "point_in_time",
                                "trigger": "subscription/service delivery", "presentation": "gross",
                                "modeled_presentation": "gross"},
                "scenarios": {},
            }
        ],
        "reported_total_revenue_parameter_id": "total_revenue_base",
        "research_coverage": [],
        "management_communication_coverage": [],
        "management_targets": [],
        "forecast_adjustments": [],
        "growth_driver_tree": {"roots": []},
    }

    _add_param(data, "total_revenue_base", 3054.0, 2025, "base", kind="reported_fact", unit="USD 100 million")
    growth_rates = {"low": [0.10, 0.10, 0.09], "base": [0.14, 0.13, 0.12], "high": [0.18, 0.16, 0.14]}
    for sc in SCENARIOS:
        rev = 3054.0
        for i, year in enumerate([2026, 2027, 2028]):
            rev *= (1 + growth_rates[sc][i])
            _add_param(data, f"revenue_{sc}_{year}", round(rev, 1), year, sc, unit="USD 100 million")

    seg = data["segments"][0]
    for sc in SCENARIOS:
        ids = [f"revenue_{sc}_{y}" for y in [2026, 2027, 2028]]
        seg["scenarios"][sc] = {
            "model": "direct_revenue",
            "driver_parameter_ids": {"revenue": ids},
            "rationale": f"{sc} case: Azure AI + Copilot drive {sc} growth",
        }

    # Source capture (must be before claims)
    for s in data["sources"]:
        s["accessed_date"] = data["as_of_date"]
        cap = {"capture_schema_version": "1.0", "capture_method": "local_document",
               "tool_name": "company-wiki-catalog", "tool_call_id": "preflight-us",
               "captured_date": data["as_of_date"], "snapshot_sha256": "a"*64,
               "content_treatment": "untrusted_data_only", "prompt_injection_status": "not_detected"}
        cap["receipt_sha256"] = canonical_sha256(cap)
        s["capture"] = cap
    receipt_sha = data["sources"][0]["capture"]["receipt_sha256"]

    # Recognition claim
    rec_claim_id = "claim_recognition_Microsoft"
    data["evidence_claims"].append(_claim(rec_claim_id, "filing", "recognition_policy",
        "recognition:Microsoft", "policy_support", "Revenue recognized at point of service delivery", "2026-07-21",
        receipt_sha=receipt_sha))
    seg["recognition"]["basis_claim_ids"] = [rec_claim_id]

    for rec in data["historical_revenue"]:
        cid = f"claim_history_{rec['year']}"
        rec["claim_ids"] = [cid]
        data["evidence_claims"].append(_claim(cid, "filing", "historical_revenue",
            f"historical_revenue:{rec['year']}", "exact_value",
            f"Microsoft FY{rec['year']} revenue: {rec['value']} 100M USD", "2026-07-21",
            receipt_sha=receipt_sha, extracted_value=rec["value"], unit="USD 100 million", period=f"FY{rec['year']}"))

    for p in data["parameters"]:
        cid = f"claim_parameter_{p['parameter_id']}"
        stype = "exact_value" if p["kind"] in ("reported_fact", "management_guidance") else "rationale_support"
        extra = {"extracted_value": p["value"], "unit": p["unit"], "period": p["period"]} if stype == "exact_value" else {}
        data["evidence_claims"].append(_claim(cid, "filing", "parameter", p["parameter_id"], stype,
            f"Evidence for {p['parameter_id']}", "2026-07-21", receipt_sha=receipt_sha, **extra))
        p["claim_ids"] = [cid]

    for dim in RESEARCH_DIMS:
        status = "modeled_driver" if dim == "growth_curve" else "data_gap"
        entry = {"dimension": dim, "status": status, "conclusion": f"Reviewed {dim} for Microsoft", "source_ids": ["filing"]}
        if dim == "company_foundation":
            entry["revenue_mechanism"] = "Microsoft generates revenue from cloud (Azure), productivity (M365), and personal computing"
        if dim == "growth_curve":
            entry["revenue_mechanism"] = "Azure AI and Copilot adoption drive growth"
        else:
            entry["revenue_mechanism"] = f"Indirect influence via {dim}"
        if status == "data_gap":
            entry["rationale"] = f"Dimension {dim} reviewed but not separately modeled"
        data["research_coverage"].append(entry)
    data["research_coverage"][-2]["conclusion"] = "Direct revenue scenario drives forecast"
    growth = next(r for r in data["research_coverage"] if r["dimension"] == "growth_curve")
    growth["parameter_ids"] = [p["parameter_id"] for p in data["parameters"] if p["scenario"] == "base"]

    for cat in MGMT_CATS:
        data["management_communication_coverage"].append({"category": cat, "status": "checked",
            "source_ids": ["filing"], "checked_date": data["as_of_date"],
            "conclusion": "No material forward revenue target found", "material_revenue_target_ids": []})

    data["growth_driver_tree"] = {"status": "data_gap", "drivers": [],
        "rationale": "Detailed growth driver tree not modeled for this forecast"}

    return data


def run_and_save(data, name, output_dir):
    """Run forecast and save results."""
    print(f"\n{'='*60}")
    print(f"Running forecast for {name}...")
    print(f"{'='*60}")

    try:
        result = run_forecast(data)
        validate_forecast_output(result)

        # Save JSON
        json_path = output_dir / f"{name}_forecast.json"
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  JSON saved: {json_path}")

        # Save Markdown
        md = render_markdown(result)
        md_path = output_dir / f"{name}_forecast.md"
        md_path.write_text(md, encoding="utf-8")
        print(f"  Markdown saved: {md_path}")

        # Print summary
        base = result["consolidated_forecast"]["base"]
        low = result["consolidated_forecast"]["low"]
        high = result["consolidated_forecast"]["high"]
        base_rev = base["annual_revenue"]
        print(f"\n  Base year revenue: {list(base_rev.values())[0]} {data['currency']} {data['unit']}")
        print(f"  Base CAGR: {base['cagr']:.1%}")
        print(f"  Low/High CAGR: {low['cagr']:.1%} / {high['cagr']:.1%}")
        print(f"  Forecast years: {data['forecast_years']}")
        print(f"  Base annual: {base['annual_revenue']}")
        print(f"  Low annual:  {low['annual_revenue']}")
        print(f"  High annual: {high['annual_revenue']}")
        print("  Status: SUCCESS")

    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return False
    return True


if __name__ == "__main__":
    output_dir = SKILL_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    # Run 腾讯
    tencent = build_tencent()
    run_and_save(tencent, "tencent_hk", output_dir)

    # Run 微软
    microsoft = build_microsoft()
    run_and_save(microsoft, "microsoft_us", output_dir)
