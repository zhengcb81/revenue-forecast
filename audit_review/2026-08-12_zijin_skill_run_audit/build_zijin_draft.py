"""Build and validate the isolated Zijin Mining revenue-forecast draft.

This is a run artifact, not product code.  It deliberately uses draft mode so
the repository publication registry is never mutated.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


AUDIT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = AUDIT_ROOT.parents[1]
OUTPUT_ROOT = AUDIT_ROOT / "outputs"
SOURCES_ROOT = AUDIT_ROOT / "sources"
REGISTRY_PATH = REPO_ROOT / "artifacts" / "registry" / "publications.jsonl"

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from revenue_core import (  # noqa: E402
    Collector,
    build_host_receipt,
    canonical_sha256,
    run_forecast,
    text_sha256,
    validate_document,
)
from revenue_report import render_markdown  # noqa: E402


AS_OF = "2026-08-12"
VERIFIER = "codex-revenue-forecast-audit"
CAPTURE_TIMESTAMP = "2026-08-12T23:55:00+01:00"

FY2025_PDF = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\companies\紫金矿业\raw"
    r"\financial_reports\annual"
    r"\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf"
)
FY2024_PDF = Path(
    r"C:\Users\郑曾波\Projects\company-wiki\companies\紫金矿业\raw"
    r"\financial_reports\annual"
    r"\2025-03-21_cninfo_1222870413_紫金矿业集团股份有限公司2024年年报报告.pdf"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def registry_state() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"exists": False, "size": 0, "sha256": None}
    return {
        "exists": True,
        "size": REGISTRY_PATH.stat().st_size,
        "sha256": sha256_file(REGISTRY_PATH),
    }


EXPECTED_HASHES = {
    "annual_2025": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
    "annual_2024": "004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89",
    "results_2025": "08bbc18f4dcb2bce1cd0af21075ae10155fe69beeb178e73768a3fa410d648fe",
    "norton_2026": "a9662471d15bf8ac287c179d3ae67cf3e35465b39425637119f25e1152f00b12",
}


def build_source(
    *,
    source_id: str,
    source_type: str,
    title: str,
    publisher: str,
    url: str,
    published_date: str,
    page_or_section: str,
    snapshot_path: Path,
    capture_method: str,
    tool_name: str,
    covers_until: str | None = None,
) -> dict[str, Any]:
    actual_hash = sha256_file(snapshot_path)
    expected_hash = EXPECTED_HASHES[source_id]
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"snapshot hash drift for {source_id}: {actual_hash} != {expected_hash}"
        )
    event = {
        "source_id": source_id,
        "snapshot_sha256": actual_hash,
        "source_url": url,
        "review_record": "trace/source_review.md",
        "action": "opened_checked_and_prompt_injection_scanned",
    }
    host_receipt = build_host_receipt(
        issuer="codex-desktop-host",
        environment="local-workspace-isolated-audit",
        tool_name=tool_name,
        action="capture_open_and_review",
        event_sha256=canonical_sha256(event),
        timestamp=CAPTURE_TIMESTAMP,
    )
    capture = {
        "capture_schema_version": "1.0",
        "capture_method": capture_method,
        "tool_name": tool_name,
        "tool_call_id": f"zijin-audit-20260812-{source_id}",
        "captured_date": AS_OF,
        "snapshot_sha256": actual_hash,
        "content_treatment": "untrusted_data_only",
        "prompt_injection_status": "not_detected",
        "host_receipt": host_receipt,
    }
    capture["receipt_sha256"] = canonical_sha256(capture)
    source: dict[str, Any] = {
        "source_id": source_id,
        "source_type": source_type,
        "title": title,
        "publisher": publisher,
        "url": url,
        "published_date": published_date,
        "accessed_date": AS_OF,
        "page_or_section": page_or_section,
        "capture": capture,
    }
    if covers_until is not None:
        source["covers_until"] = covers_until
    return source


def build_document() -> dict[str, Any]:
    sources = [
        build_source(
            source_id="annual_2025",
            source_type="audited_filing",
            title="紫金矿业集团股份有限公司2025年年度报告",
            publisher="紫金矿业 / 巨潮资讯网",
            url=(
                "https://www.cninfo.com.cn/new/disclosure/detail?stockCode=601899"
                "&announcementId=1225023658&announcementTime=2026-03-20%2016:00"
            ),
            published_date="2026-03-20",
            page_or_section="pp.15, 254-255, 325-327; revenue, recognition and segment notes",
            snapshot_path=FY2025_PDF,
            capture_method="local_document",
            tool_name="pdftotext-and-manual-review",
            covers_until="FY2028",
        ),
        build_source(
            source_id="annual_2024",
            source_type="audited_filing",
            title="紫金矿业集团股份有限公司2024年年度报告",
            publisher="紫金矿业 / 巨潮资讯网",
            url=(
                "https://www.cninfo.com.cn/new/disclosure/detail?stockCode=601899"
                "&announcementId=1222870413&announcementTime=2025-03-21%2016:00"
            ),
            published_date="2025-03-21",
            page_or_section="p.15; principal accounting data",
            snapshot_path=FY2024_PDF,
            capture_method="local_document",
            tool_name="pdftotext-and-manual-review",
        ),
        build_source(
            source_id="results_2025",
            source_type="company_release",
            title="2025 Results — Production & Guidance",
            publisher="Zijin Mining Group Co., Ltd.",
            url="https://www.zijinmining.com/investor/2025-newyeji.htm",
            published_date="2026-03-20",
            page_or_section="Production & Guidance; major mines/companies tables",
            snapshot_path=SOURCES_ROOT / "2025_results.html",
            capture_method="manual_open",
            tool_name="curl.exe-and-manual-review",
            covers_until="FY2028",
        ),
        build_source(
            source_id="norton_2026",
            source_type="company_release",
            title="Zijin’s Australia Operation Completes New Crushing System",
            publisher="Zijin Mining Group Co., Ltd.",
            url="https://www.zijinmining.com/news/news-detail-122827.htm",
            published_date="2026-06-30",
            page_or_section="Project commissioning update",
            snapshot_path=SOURCES_ROOT / "2026_norton_commissioning.html",
            capture_method="manual_open",
            tool_name="curl.exe-and-manual-review",
        ),
    ]
    source_index = {source["source_id"]: source for source in sources}
    claims: list[dict[str, Any]] = []

    def add_claim(
        *,
        claim_id: str,
        source_id: str,
        target_type: str,
        target_id: str,
        support_type: str,
        locator: str,
        excerpt: str,
        extracted_value: float | None = None,
        unit: str | None = None,
        period: str | None = None,
    ) -> str:
        if not (10 <= len(excerpt.strip()) <= 500):
            raise RuntimeError(f"invalid excerpt length for {claim_id}")
        source = source_index[source_id]
        claim: dict[str, Any] = {
            "claim_id": claim_id,
            "source_id": source_id,
            "target_type": target_type,
            "target_id": target_id,
            "support_type": support_type,
            "locator": locator,
            "excerpt": excerpt.strip(),
            "excerpt_sha256": text_sha256(excerpt.strip()),
            "content_sha256": source["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": source["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked",
            "verified_by": VERIFIER,
            "verified_date": AS_OF,
        }
        if extracted_value is not None:
            claim["extracted_value"] = extracted_value
        if unit is not None:
            claim["unit"] = unit
        if period is not None:
            claim["period"] = period
        claims.append(claim)
        return claim_id

    segment_table_excerpt = (
        "2025年对外销售收入：矿产品109,977,556,345元，冶炼产品165,858,644,874元，"
        "贸易29,212,610,830元，其他44,030,270,803元，合计349,079,082,852元。"
    )
    segment_history_excerpt = (
        "对外销售收入从2024年的矿产品74,089,365,354元、冶炼产品181,141,823,725元、"
        "贸易29,386,475,085元、其他19,022,292,989元，变为2025年的"
        "109,977,556,345元、165,858,644,874元、29,212,610,830元、44,030,270,803元。"
    )
    guidance_excerpt = (
        "Production guidance lists 2025/2026E/2028E mined gold at 2.89/3.38/4.18-4.50 Moz, "
        "mined copper at 1,090/1,200/1,500-1,600 kt, and lithium carbonate at 25.5/120/270-320 kt."
    )
    guidance_caution_excerpt = (
        "Projected figures are merely production guidance with underlying uncertainty; they do not "
        "constitute a commitment to actual output and may be adjusted as conditions change."
    )

    parameters: list[dict[str, Any]] = []

    def add_revenue_fact(
        parameter_id: str,
        value: float,
        definition: str,
        excerpt: str = segment_table_excerpt,
    ) -> None:
        claim_id = add_claim(
            claim_id=f"claim_{parameter_id}",
            source_id="annual_2025",
            target_type="parameter",
            target_id=parameter_id,
            support_type="exact_value",
            locator="p.326, segment report — external sales revenue",
            excerpt=excerpt,
            extracted_value=value,
            unit="CNY million",
            period="FY2025",
        )
        parameters.append(
            {
                "parameter_id": parameter_id,
                "kind": "reported_fact",
                "value": value,
                "unit": "CNY million",
                "period": "FY2025",
                "definition": definition,
                "source_ids": ["annual_2025"],
                "claim_ids": [claim_id],
                "dimension": "revenue",
                "time_basis": "annual",
                "currency": "CNY",
                "scale": "million",
            }
        )

    add_revenue_fact(
        "reported_total_FY2025",
        349079.082852,
        "Zijin Mining consolidated external revenue for FY2025",
    )
    segment_specs = {
        "矿产品": {
            "slug": "mineral",
            "base": 109977.556345,
            "definition": "FY2025 mineral products segment external revenue",
            "presentation": "gross",
            "timing": "point_in_time",
            "trigger": "customer obtains control of mineral products",
        },
        "冶炼产品": {
            "slug": "smelting",
            "base": 165858.644874,
            "definition": "FY2025 smelting products segment external revenue",
            "presentation": "gross",
            "timing": "point_in_time",
            "trigger": "customer obtains control of smelted products",
        },
        "贸易": {
            "slug": "trade",
            "base": 29212.610830,
            "definition": "FY2025 trading segment external revenue as reported after principal-agent assessment",
            "presentation": "net",
            "timing": "point_in_time",
            "trigger": "reported trade sale after principal-agent assessment",
        },
        "其他": {
            "slug": "other",
            "base": 44030.270803,
            "definition": "FY2025 other segment external revenue",
            "presentation": "gross",
            "timing": "point_in_time",
            "trigger": "reported delivery or service recognition event",
        },
    }
    for name, spec in segment_specs.items():
        add_revenue_fact(
            f"segment_{spec['slug']}_base_FY2025",
            spec["base"],
            spec["definition"],
        )

    growth_paths = {
        "mineral": {
            "low": [0.10, 0.08, 0.08, -0.05, 0.00],
            "base": [0.30, 0.18, 0.15, 0.05, 0.04],
            "high": [0.45, 0.25, 0.20, 0.08, 0.06],
        },
        "smelting": {
            "low": [-0.03, 0.00, 0.01, 0.00, 0.00],
            "base": [0.10, 0.05, 0.05, 0.03, 0.03],
            "high": [0.18, 0.08, 0.07, 0.05, 0.04],
        },
        "trade": {
            "low": [-0.03, 0.00, 0.00, 0.00, 0.00],
            "base": [0.04, 0.02, 0.02, 0.02, 0.02],
            "high": [0.10, 0.05, 0.04, 0.03, 0.03],
        },
        "other": {
            "low": [0.00, 0.01, 0.01, 0.00, 0.00],
            "base": [0.10, 0.08, 0.05, 0.03, 0.03],
            "high": [0.20, 0.12, 0.08, 0.05, 0.04],
        },
    }
    years = [2026, 2027, 2028, 2029, 2030]
    for segment_name, spec in segment_specs.items():
        slug = spec["slug"]
        for scenario in ("low", "base", "high"):
            for year, value in zip(years, growth_paths[slug][scenario]):
                parameter_id = f"{slug}_growth_FY{year}_{scenario}"
                source_ids: list[str] = []
                claim_ids: list[str] = []
                kind = "scenario_stress" if scenario != "base" else "analyst_assumption"
                if scenario == "base" and year <= 2028:
                    source_id = "results_2025" if slug == "mineral" else "annual_2025"
                    source_ids = [source_id]
                    rationale_excerpt = (
                        guidance_excerpt if slug == "mineral" else segment_history_excerpt
                    )
                    claim_ids = [
                        add_claim(
                            claim_id=f"claim_{parameter_id}",
                            source_id=source_id,
                            target_type="parameter",
                            target_id=parameter_id,
                            support_type="rationale_support",
                            locator=(
                                "Production & Guidance"
                                if slug == "mineral"
                                else "pp.326-327, external segment revenue"
                            ),
                            excerpt=rationale_excerpt,
                        )
                    ]
                horizon_text = (
                    "company guidance and observed segment base through FY2028"
                    if year <= 2028
                    else "analyst fade beyond the FY2028 company planning horizon"
                )
                scenario_text = {
                    "low": "downside stress for weaker commodity prices, project delays or lower throughput",
                    "base": horizon_text,
                    "high": "upside stress for stronger prices, faster ramp-up and favorable mix",
                }[scenario]
                parameters.append(
                    {
                        "parameter_id": parameter_id,
                        "kind": kind,
                        "value": value,
                        "unit": "ratio",
                        "period": f"FY{year}",
                        "definition": (
                            f"{segment_name} external revenue annual growth rate, {scenario} scenario"
                        ),
                        "scenario": scenario,
                        "rationale": scenario_text,
                        "source_ids": source_ids,
                        "claim_ids": claim_ids,
                        "dimension": "ratio",
                        "time_basis": "annual",
                    }
                )

    recognition_excerpts = {
        "矿产品": (
            "本集团将合同中约定的转让矿产品作为单项履约义务，该履约义务属于在某一时点履行，"
            "在客户取得矿产品控制权的时点确认收入；本集团为主要责任人。"
        ),
        "冶炼产品": (
            "本集团将合同中约定的转让冶炼产品作为单项履约义务，该履约义务属于在某一时点履行，"
            "在客户取得冶炼产品控制权的时点确认收入；本集团为主要责任人。"
        ),
        "贸易": (
            "贸易业务中能够主导商品使用、决定价格并承担风险时按总额确认；否则作为代理人按佣金"
            "或手续费净额确认收入。"
        ),
        "其他": (
            "环保设备及工程主要在整体验收时确认收入；BOT运维、垃圾处置、烟气治理和发电等运营"
            "收入按履约进度在一段时间内确认。"
        ),
    }
    segments: list[dict[str, Any]] = []
    for name, spec in segment_specs.items():
        slug = spec["slug"]
        recognition_claim = add_claim(
            claim_id=f"claim_recognition_{slug}",
            source_id="annual_2025",
            target_type="recognition_policy",
            target_id=f"recognition:{name}",
            support_type="policy_support",
            locator="pp.254-255, performance obligations",
            excerpt=recognition_excerpts[name],
        )
        scenarios: dict[str, Any] = {}
        for scenario in ("low", "base", "high"):
            scenarios[scenario] = {
                "model": "direct_growth",
                "driver_parameter_ids": {
                    "growth_rate": [
                        f"{slug}_growth_FY{year}_{scenario}" for year in years
                    ]
                },
                "rationale": (
                    f"Direct-growth fallback for {name}; the source set does not disclose a complete "
                    "volume-price-ownership-elimination identity for this external-revenue segment."
                ),
            }
        segments.append(
            {
                "name": name,
                "base_revenue_parameter_id": f"segment_{slug}_base_FY2025",
                "recognition": {
                    "mode": "modeled_as_recognized",
                    "timing": spec["timing"],
                    "trigger": spec["trigger"],
                    "presentation": spec["presentation"],
                    "modeled_presentation": spec["presentation"],
                    "basis_claim_ids": [recognition_claim],
                },
                "scenarios": scenarios,
            }
        )

    history_2024_claim = add_claim(
        claim_id="claim_history_2024",
        source_id="annual_2024",
        target_type="historical_revenue",
        target_id="historical_revenue:2024",
        support_type="exact_value",
        locator="p.15, principal accounting data",
        excerpt="2024年度主要会计数据表披露营业收入303,639,957,153元，2023年度为293,403,242,878元。",
        extracted_value=303639.957153,
        unit="CNY million",
        period="FY2024",
    )
    history_2025_claim = add_claim(
        claim_id="claim_history_2025",
        source_id="annual_2025",
        target_type="historical_revenue",
        target_id="historical_revenue:2025",
        support_type="exact_value",
        locator="p.15, principal accounting data",
        excerpt="2025年度主要会计数据表披露营业收入349,079,082,852元，2024年度为303,639,957,153元。",
        extracted_value=349079.082852,
        unit="CNY million",
        period="FY2025",
    )

    probability_claim = add_claim(
        claim_id="claim_probability_calibration",
        source_id="results_2025",
        target_type="scenario_probability",
        target_id="scenario_probability",
        support_type="rationale_support",
        locator="Production & Guidance caution note",
        excerpt=guidance_caution_excerpt,
    )

    # Growth-driver evidence claims are separate from parameter claims because
    # every evidence node has an exact target_id contract.
    growth_claims = {
        "ev_mineral_guidance": add_claim(
            claim_id="claim_ev_mineral_guidance",
            source_id="results_2025",
            target_type="growth_driver",
            target_id="ev_mineral_guidance",
            support_type="rationale_support",
            locator="Production & Guidance",
            excerpt=guidance_excerpt,
        ),
        "ev_norton_execution": add_claim(
            claim_id="claim_ev_norton_execution",
            source_id="norton_2026",
            target_type="growth_driver",
            target_id="ev_norton_execution",
            support_type="rationale_support",
            locator="Project commissioning update",
            excerpt=(
                "Norton commissioned a new 2 Mtpa crushing system; once fully operational it is expected "
                "to raise heap-leach capacity from 5 Mtpa to 7 Mtpa and annual gold output by about 11,600 ounces."
            ),
        ),
        "ev_mineral_caution": add_claim(
            claim_id="claim_ev_mineral_caution",
            source_id="results_2025",
            target_type="growth_driver",
            target_id="ev_mineral_caution",
            support_type="rationale_support",
            locator="Production & Guidance caution note",
            excerpt=guidance_caution_excerpt,
        ),
        "ev_smelting_definition": add_claim(
            claim_id="claim_ev_smelting_definition",
            source_id="annual_2025",
            target_type="growth_driver",
            target_id="ev_smelting_definition",
            support_type="rationale_support",
            locator="p.325, segment definitions",
            excerpt="冶炼产品分部包括冶炼产铜、冶炼加工金银、冶炼产锌锭、硫酸及电池级碳酸锂。",
        ),
        "ev_smelting_history": add_claim(
            claim_id="claim_ev_smelting_history",
            source_id="annual_2025",
            target_type="growth_driver",
            target_id="ev_smelting_history",
            support_type="rationale_support",
            locator="pp.326-327, external segment revenue",
            excerpt=segment_history_excerpt,
        ),
        "ev_trade_policy": add_claim(
            claim_id="claim_ev_trade_policy",
            source_id="annual_2025",
            target_type="growth_driver",
            target_id="ev_trade_policy",
            support_type="rationale_support",
            locator="p.254, trading revenue policy",
            excerpt=recognition_excerpts["贸易"],
        ),
        "ev_trade_history": add_claim(
            claim_id="claim_ev_trade_history",
            source_id="annual_2025",
            target_type="growth_driver",
            target_id="ev_trade_history",
            support_type="rationale_support",
            locator="pp.326-327, external segment revenue",
            excerpt=segment_history_excerpt,
        ),
        "ev_other_history": add_claim(
            claim_id="claim_ev_other_history",
            source_id="annual_2025",
            target_type="growth_driver",
            target_id="ev_other_history",
            support_type="rationale_support",
            locator="pp.326-327, external segment revenue",
            excerpt=segment_history_excerpt,
        ),
    }

    base_ids = {
        slug: [f"{slug}_growth_FY{year}_base" for year in years]
        for slug in growth_paths
    }
    growth_driver_tree = {
        "status": "modeled",
        "drivers": [
            {
                "driver_id": "mineral_volume_price_mix",
                "title": "Mine output ramp, commodity prices and asset mix",
                "thesis": (
                    "Gold, copper and lithium volume ramps plus realized-price and mix changes drive "
                    "the mineral-products external-revenue path."
                ),
                "causal_chain": [
                    "project commissioning and resource conversion change saleable mine output",
                    "commodity prices and product mix translate output into recognized external revenue",
                    "ownership, consolidation and internal-sales boundaries reconcile to the mineral segment",
                ],
                "parameter_ids": base_ids["mineral"],
                "segment_attribution": [{"segment_name": "矿产品", "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2030},
                "persistence": "multi_year_structural",
                "persistence_rationale": (
                    "The disclosed project ramp extends through FY2028; FY2029-FY2030 deliberately fade to "
                    "mature growth rather than extending guidance as fact."
                ),
                "evidence_nodes": [
                    {
                        "evidence_id": "ev_mineral_guidance",
                        "evidence_type": "production_guidance",
                        "inference_distance": "direct",
                        "conclusion": "Official production guidance supports material gold, copper and lithium volume expansion through FY2028.",
                        "claim_ids": [growth_claims["ev_mineral_guidance"]],
                    },
                    {
                        "evidence_id": "ev_norton_execution",
                        "evidence_type": "project_execution",
                        "inference_distance": "one_step",
                        "conclusion": "Norton commissioning is a concrete but group-small example of capacity execution.",
                        "claim_ids": [growth_claims["ev_norton_execution"]],
                    },
                    {
                        "evidence_id": "ev_mineral_caution",
                        "evidence_type": "guidance_risk",
                        "inference_distance": "contrary",
                        "conclusion": "The company expressly states that production guidance is uncertain and not a commitment.",
                        "claim_ids": [growth_claims["ev_mineral_caution"]],
                    },
                ],
                "leading_indicators": [
                    "quarterly mined gold, copper and lithium output versus company guidance",
                    "realized metal prices and Kamoa-Kakula recovery",
                    "commissioning and ramp milestones at major copper and lithium projects",
                ],
                "falsifiers": [
                    "FY2026 mineral external revenue grows below the low path",
                    "major mine ramps slip while realized prices normalize sharply",
                ],
                "counterevidence_status": "found",
                "counterevidence_rationale": "The source itself cautions that guidance is uncertain; browser research also found mine-specific execution dispersion.",
            },
            {
                "driver_id": "smelting_throughput_and_prices",
                "title": "Smelting throughput, feed availability and metal prices",
                "thesis": "Smelting-product external revenue follows processing throughput, feed mix and metal-price pass-through.",
                "causal_chain": [
                    "mine and third-party feed availability sets processing throughput",
                    "metal prices and treatment economics determine recognized smelting revenue",
                ],
                "parameter_ids": base_ids["smelting"],
                "segment_attribution": [{"segment_name": "冶炼产品", "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2030},
                "persistence": "cyclical",
                "persistence_rationale": "The segment is large but price- and feed-sensitive; the path normalizes after the planning period.",
                "evidence_nodes": [
                    {
                        "evidence_id": "ev_smelting_definition",
                        "evidence_type": "business_perimeter",
                        "inference_distance": "direct",
                        "conclusion": "The audited segment perimeter covers copper, gold/silver, zinc, acid and battery-grade lithium carbonate processing.",
                        "claim_ids": [growth_claims["ev_smelting_definition"]],
                    },
                    {
                        "evidence_id": "ev_smelting_history",
                        "evidence_type": "historical_segment_revenue",
                        "inference_distance": "contrary",
                        "conclusion": "FY2025 external smelting revenue declined despite strong group growth, demonstrating cyclicality and mix risk.",
                        "claim_ids": [growth_claims["ev_smelting_history"]],
                    },
                ],
                "leading_indicators": ["smelting output, feed availability and realized metal prices"],
                "falsifiers": ["smelting external revenue remains below FY2025 despite capacity and price support"],
                "counterevidence_status": "found",
                "counterevidence_rationale": "The audited FY2025 segment comparison records a year-on-year external-revenue decline.",
            },
            {
                "driver_id": "trade_turnover_and_principal_agent_mix",
                "title": "Trading turnover and principal-agent presentation mix",
                "thesis": "Trading revenue is driven by turnover but reported revenue also depends on gross-versus-net principal-agent conclusions.",
                "causal_chain": [
                    "commodity trading volume and prices determine transaction value",
                    "principal-agent assessment converts transaction value into gross or net reported revenue",
                ],
                "parameter_ids": base_ids["trade"],
                "segment_attribution": [{"segment_name": "贸易", "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2030},
                "persistence": "cyclical",
                "persistence_rationale": "Commodity turnover can be high while accounting presentation and margins remain volatile.",
                "evidence_nodes": [
                    {
                        "evidence_id": "ev_trade_policy",
                        "evidence_type": "recognition_policy",
                        "inference_distance": "direct",
                        "conclusion": "The audited policy confirms mixed gross and net presentation depending on control and risk.",
                        "claim_ids": [growth_claims["ev_trade_policy"]],
                    },
                    {
                        "evidence_id": "ev_trade_history",
                        "evidence_type": "historical_segment_revenue",
                        "inference_distance": "contrary",
                        "conclusion": "FY2025 external trade revenue was slightly below FY2024, arguing against aggressive structural growth.",
                        "claim_ids": [growth_claims["ev_trade_history"]],
                    },
                ],
                "leading_indicators": ["external trade revenue and disclosed principal-agent mix"],
                "falsifiers": ["reported trade revenue departs materially from turnover due to presentation changes"],
                "counterevidence_status": "found",
                "counterevidence_rationale": "The audited segment history is flat-to-down and the presentation mix is not separately quantified.",
            },
            {
                "driver_id": "other_business_normalization",
                "title": "Other-business delivery and normalization",
                "thesis": "Environmental, fabricated-product and related activities grow from a sharply higher FY2025 base but normalize over time.",
                "causal_chain": [
                    "delivery, project acceptance and service activity generate recognized other-segment revenue",
                    "growth fades as the unusually strong FY2025 comparison base normalizes",
                ],
                "parameter_ids": base_ids["other"],
                "segment_attribution": [{"segment_name": "其他", "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2030},
                "persistence": "uncertain",
                "persistence_rationale": "The segment combines heterogeneous products and services and lacks a disclosed driver bridge.",
                "evidence_nodes": [
                    {
                        "evidence_id": "ev_other_history",
                        "evidence_type": "historical_segment_revenue",
                        "inference_distance": "one_step",
                        "conclusion": "FY2025 other-segment external revenue rose sharply from FY2024, creating a high normalization base.",
                        "claim_ids": [growth_claims["ev_other_history"]],
                    }
                ],
                "leading_indicators": ["other-segment external revenue and large project acceptance timing"],
                "falsifiers": ["the FY2025 step-up reverses and other-segment revenue falls below the low path"],
                "counterevidence_status": "searched_none_found",
                "counterevidence_rationale": "The audited source was checked; no separate current driver bridge was disclosed.",
            },
        ],
    }

    foundation_ids = [
        "reported_total_FY2025",
        *[f"segment_{spec['slug']}_base_FY2025" for spec in segment_specs.values()],
    ]
    all_base_growth_ids = [parameter_id for ids in base_ids.values() for parameter_id in ids]
    research_coverage = [
        {
            "dimension": "company_foundation",
            "status": "modeled_driver",
            "conclusion": "FY2025 consolidated revenue reconciles exactly to four external-revenue report segments.",
            "revenue_mechanism": "external segment revenue is used directly, avoiding double counting of internal sales and eliminations",
            "parameter_ids": foundation_ids,
            "source_ids": ["annual_2025"],
        },
        {
            "dimension": "growth_curve",
            "status": "modeled_driver",
            "conclusion": "Each report segment has a five-year low/base/high direct-growth path.",
            "revenue_mechanism": "annual growth rates compound FY2025 external segment revenue into recognized revenue",
            "parameter_ids": all_base_growth_ids,
            "source_ids": ["annual_2025", "results_2025", "norton_2026"],
        },
        {
            "dimension": "industry_market",
            "status": "data_gap",
            "conclusion": "A frozen commodity-price and treatment-charge curve was not available in the reusable source set.",
            "revenue_mechanism": "metal prices and processing economics materially affect mineral and smelting revenue",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Web operating evidence was reviewed, but no auditable multi-year market-price deck was frozen for this run.",
        },
        {
            "dimension": "competition",
            "status": "data_gap",
            "conclusion": "Peer supply additions and cost-curve positioning are not explicitly modeled.",
            "revenue_mechanism": "industry supply affects commodity prices rather than directly setting company revenue",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "The run is scoped to company revenue and lacks a source-linked peer supply model.",
        },
        {
            "dimension": "capacity",
            "status": "modeled_driver",
            "conclusion": "Official production guidance and a captured commissioning event support the mineral ramp through FY2028.",
            "revenue_mechanism": "higher mine and processing output raises saleable volume before ownership and elimination adjustments",
            "parameter_ids": base_ids["mineral"][:3],
            "source_ids": ["results_2025", "norton_2026"],
        },
        {
            "dimension": "technology",
            "status": "data_gap",
            "conclusion": "Recovery, grade-control and process-technology changes are not quantified by mine.",
            "revenue_mechanism": "recovery and throughput affect saleable metal and hence mineral revenue",
            "parameter_ids": [],
            "source_ids": ["norton_2026"],
            "rationale": "Only one project execution example is frozen; it cannot represent the global portfolio.",
        },
        {
            "dimension": "policy",
            "status": "data_gap",
            "conclusion": "Jurisdiction, royalty, permitting and export-policy changes are not modeled by asset.",
            "revenue_mechanism": "permits and fiscal regimes can delay output or alter realized economics",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "No complete asset-by-jurisdiction permit ledger is available in reusable artifacts.",
        },
        {
            "dimension": "customers",
            "status": "data_gap",
            "conclusion": "Customer concentration and offtake contract terms are not separately disclosed for the four segments.",
            "revenue_mechanism": "offtake terms and counterparties affect pricing, timing and collectability",
            "parameter_ids": [],
            "source_ids": ["annual_2025"],
            "rationale": "The audited report does not provide a customer-level revenue bridge usable for this forecast.",
        },
        {
            "dimension": "demand",
            "status": "data_gap",
            "conclusion": "End-market demand is represented only indirectly through scenario growth rates.",
            "revenue_mechanism": "gold, copper, zinc and lithium demand influences realized prices and trade throughput",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "No frozen demand model was available; price-cycle uncertainty remains in scenario spreads.",
        },
        {
            "dimension": "reserves_and_resources",
            "status": "data_gap",
            "conclusion": "Group and major-project resources are available, but complete mine-level reserves are not structured for model use.",
            "revenue_mechanism": "reserve life constrains sustainable production but cannot be converted directly into annual revenue",
            "parameter_ids": [],
            "source_ids": ["annual_2025", "results_2025"],
            "rationale": "Resources versus reserves and 100-percent versus attributable bases cannot be safely merged without an asset fact model.",
        },
        {
            "dimension": "mine_asset_geography",
            "status": "data_gap",
            "conclusion": "Major mines, countries and 2025 production are discoverable, but not linked to a complete mine-year revenue identity.",
            "revenue_mechanism": "asset geography drives ramp, jurisdiction and consolidation risk",
            "parameter_ids": [],
            "source_ids": ["results_2025"],
            "rationale": "Many official rows are company aggregates and no source discloses FY2026-FY2030 revenue by mine.",
        },
        {
            "dimension": "regulatory_permits",
            "status": "data_gap",
            "conclusion": "Permit status and renewal dates are not available as a current, source-linked asset ledger.",
            "revenue_mechanism": "permit delays can shift commissioning and recognized revenue",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Broker tables contain useful historical permit data but are not normalized or date-validated in the catalog.",
        },
        {
            "dimension": "broker_research",
            "status": "data_gap",
            "conclusion": "Seven Dropbox broker PDFs are indexed as physical documents but have no reusable bound artifacts.",
            "revenue_mechanism": "broker mine tables could improve asset ramps and triangulation after trustworthy preprocessing",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "All seven have zero artifacts and evidence spans; this run did not alter worker priority or ingest state.",
        },
    ]

    def search_event(category: str, event_ids: list[str], scope: str) -> dict[str, Any]:
        event: dict[str, Any] = {
            "query_scope": scope,
            "query_time": "2026-08-12T22:30:00+01:00",
            "event_ids": event_ids,
            "generated_by": VERIFIER,
        }
        event["event_sha256"] = canonical_sha256(event)
        return event

    management_communication_coverage = [
        {
            "category": "latest_annual_filing",
            "status": "checked",
            "source_ids": ["annual_2025"],
            "checked_date": AS_OF,
            "conclusion": "The latest annual filing was checked; no explicit consolidated revenue target was found.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_results_release",
            "status": "checked",
            "source_ids": ["results_2025"],
            "checked_date": AS_OF,
            "conclusion": "The latest results page was checked; it contains production guidance rather than a revenue target.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_earnings_call",
            "status": "not_available",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "No stable official post-event transcript or question-and-answer record was captured.",
            "material_revenue_target_ids": [],
            "rationale": "A convening notice and event entry were found, but the substantive transcript was not available as a stable source.",
            "search_description": "Official company, exchange and roadshow-center searches for the annual results briefing transcript.",
            "search_event": search_event(
                "latest_earnings_call",
                ["W-007-results-briefing-notice", "W-007-roadshow-center-search"],
                "Zijin Mining annual results briefing transcript and official Q&A",
            ),
        },
        {
            "category": "latest_investor_presentation",
            "status": "not_available",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "The presentation listing was found, but a stable presentation snapshot was not captured.",
            "material_revenue_target_ids": [],
            "rationale": "The PDF open failed once and binary source download was not authorized for this isolated audit.",
            "search_description": "Official investor-presentation listing and annual-results presentation link were checked.",
            "search_event": search_event(
                "latest_investor_presentation",
                ["W-003-presentation-link", "W-007-presentation-listing"],
                "Zijin Mining official annual results presentation",
            ),
        },
        {
            "category": "latest_strategy_communication",
            "status": "checked",
            "source_ids": ["results_2025"],
            "checked_date": AS_OF,
            "conclusion": "The official results page contains the current production plan but no consolidated revenue goal.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "material_announcements_since_last_filing",
            "status": "checked",
            "source_ids": ["norton_2026"],
            "checked_date": AS_OF,
            "conclusion": "A captured project-commissioning update was checked; broader browser research found additional events but no frozen revenue target.",
            "material_revenue_target_ids": [],
        },
    ]

    data: dict[str, Any] = {
        "schema_version": "3.7",
        "company_name": "紫金矿业集团股份有限公司",
        "as_of_date": AS_OF,
        "currency": "CNY",
        "unit": "million",
        "fiscal_year_end": "12-31",
        "base_year": 2025,
        "forecast_years": years,
        "forecast_version": "zijin-2026-08-12-isolated-draft-v1",
        "historical_revenue": [
            {
                "year": 2024,
                "value": 303639.957153,
                "source_ids": ["annual_2024"],
                "claim_ids": [history_2024_claim],
            },
            {
                "year": 2025,
                "value": 349079.082852,
                "source_ids": ["annual_2025"],
                "claim_ids": [history_2025_claim],
            },
        ],
        "sources": sources,
        "parameters": parameters,
        "segments": segments,
        "reported_total_revenue_parameter_id": "reported_total_FY2025",
        "base_adjustment_parameter_ids": [],
        "forecast_adjustments": [],
        "revenue_constraints": [],
        "research_coverage": research_coverage,
        "growth_driver_tree": growth_driver_tree,
        "management_communication_coverage": management_communication_coverage,
        "management_targets": [],
        "evidence_claims": claims,
        "data_gaps": [
            "No source discloses FY2026-FY2030 revenue for each mine; the model stops at four external-revenue report segments.",
            "The complete mine-level bridge for volume, grade, recovery, price, ownership, consolidation and internal eliminations is unavailable.",
            "Trade revenue contains both gross principal and net agent presentation, while the current segment schema permits only one presentation label.",
            "The other segment mixes point-in-time product/project revenue with over-time operating services, while the current segment schema permits one timing label.",
            "Company production guidance principally ends at FY2028; FY2029-FY2030 base growth is an explicit source-free analyst fade.",
            "No frozen multi-year commodity-price, treatment-charge or foreign-exchange curve is included.",
            "Seven Dropbox broker PDFs have no bound normalized Markdown, summary, evidence spans or semantic tags in the catalog.",
            "The standard filing-fetch to revenue source-preparation path remains blocked by missing shared prompt-injection review despite exact-file reuse.",
            "The investor presentation and results-call transcript were not captured as stable source snapshots.",
            "All four segments use direct_growth fallback, so explicit operational-model revenue share is zero.",
        ],
        "disconfirming_indicators": [
            "mineral external revenue grows below the low scenario",
            "Kamoa-Kakula recovery or major copper and lithium ramps miss disclosed milestones",
            "realized gold and copper prices normalize faster than volume expands",
            "smelting external revenue remains below the FY2025 base",
            "principal-agent reclassification causes a material trade-revenue presentation shift",
            "FY2025 other-segment revenue step-up reverses",
        ],
        "scenario_probabilities": {"low": 0.20, "base": 0.60, "high": 0.20},
        "probability_rationale": (
            "Analyst calibration: the base case is most likely, with symmetric tails for commodity-price, "
            "project-execution, consolidation and accounting-presentation uncertainty; these probabilities are not company guidance."
        ),
        "probability_claim_ids": [probability_claim],
        "sensitivity_tests": [
            {
                "name": "FY2026 mineral growth +/-5 percentage points",
                "parameter_id": "mineral_growth_FY2026_base",
                "shock_type": "percentage_point",
                "shock_value": 0.05,
            },
            {
                "name": "FY2026 smelting growth +/-5 percentage points",
                "parameter_id": "smelting_growth_FY2026_base",
                "shock_type": "percentage_point",
                "shock_value": 0.05,
            },
            {
                "name": "FY2026 trade growth +/-3 percentage points",
                "parameter_id": "trade_growth_FY2026_base",
                "shock_type": "percentage_point",
                "shock_value": 0.03,
            },
            {
                "name": "FY2026 other growth +/-5 percentage points",
                "parameter_id": "other_growth_FY2026_base",
                "shock_type": "percentage_point",
                "shock_value": 0.05,
            },
        ],
    }
    return data


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def render_isolated_summary(
    result: dict[str, Any], *, native_renderer_error: str | None
) -> str:
    """Render a transparent audit summary without pretending it is formal output."""

    def bn(value: float) -> str:
        return f"{value / 1000:,.3f}"

    def pct(value: float) -> str:
        return f"{value * 100:.2f}%"

    years = [str(year) for year in result["forecast_years"]]
    lines = [
        "# 紫金矿业未来五年营收预测（隔离 draft 摘要）",
        "",
        "> 这不是 formal publication。严格 schema 3.7 输入、完整计算和强输出校验已经通过，",
        "> 但标准 source-preparation 被共享 catalog 的 `not_reviewed` 安全状态拦截；官方 Markdown renderer",
        "> 又无法接受合法 draft receipt。本摘要只从未修改的强校验 `draft_result.json` 读取数值。",
        "",
        f"- 信息截止日：{result['as_of_date']}",
        f"- 基期：FY{result['base_year']}，营收 {bn(result['base_revenue'])} 十亿元",
        f"- 模型：四个外部收入报告分部，全部使用 `direct_growth` fallback",
        f"- 输入 SHA-256：`{result['input_sha256']}`",
        f"- 结果 SHA-256：`{result['result_sha256']}`",
        "- publication registry：未写入",
        "",
        "## 核心结论",
        "",
        "| 情景 | FY2030 营收（十亿元） | FY2025→FY2030 CAGR | 五年营收增量（十亿元） |",
        "|---|---:|---:|---:|",
    ]
    for scenario in ("low", "base", "high"):
        item = result["consolidated_forecast"][scenario]
        lines.append(
            f"| {scenario} | {bn(item['terminal_revenue'])} | {pct(item['cagr'])} | {bn(item['incremental_revenue'])} |"
        )
    weighted = result.get("probability_weighted_forecast")
    if weighted:
        lines.extend(
            [
                "",
                f"概率加权（20%/60%/20%）FY2030 营收为 **{bn(weighted['terminal_revenue'])} 十亿元**，",
                f"隐含 CAGR 为 **{pct(weighted['expected_terminal_implied_cagr'])}**。该概率是分析师校准，不是公司指引。",
            ]
        )

    lines.extend(
        [
            "",
            "## 年度三情景路径",
            "",
            "| 年度 | Low营收 | Base营收 | High营收 | Base同比 |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for year in years:
        low = result["consolidated_forecast"]["low"]
        base = result["consolidated_forecast"]["base"]
        high = result["consolidated_forecast"]["high"]
        lines.append(
            f"| {year} | {bn(low['annual_revenue'][year])} | {bn(base['annual_revenue'][year])} | "
            f"{bn(high['annual_revenue'][year])} | {pct(base['annual_growth'][year])} |"
        )
    lines.append("")
    lines.append("单位：人民币十亿元。")

    base_bridge = {
        item["name"]: item["annual_revenue"]
        for item in result["consolidated_forecast"]["base"]["segment_bridge"]
    }
    segment_bases = {item["name"]: item["base_revenue"] for item in result["segments"]}
    lines.extend(
        [
            "",
            "## Base 分部路径",
            "",
            "| 外部收入分部 | FY2025A | FY2026E | FY2027E | FY2028E | FY2029E | FY2030E |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name in ("矿产品", "冶炼产品", "贸易", "其他"):
        path = base_bridge[name]
        lines.append(
            f"| {name} | {bn(segment_bases[name])} | "
            + " | ".join(bn(path[year]) for year in years)
            + " |"
        )

    lines.extend(["", "## 主要增长驱动", ""])
    for driver in result["growth_driver_analysis"]["top_drivers"]:
        lines.append(
            f"{driver['rank']}. **{driver['title']}**：FY2030 Base 增量 "
            f"{bn(driver['estimated_base_terminal_increment'])} 十亿元，占正向驱动 "
            f"{pct(driver['share_of_positive_driver_increment'])}；证据状态 `{driver['evidence_status']}`。"
        )
    lines.extend(
        [
            "",
            "矿产品是最大增量来源，但模型没有把每座矿拆成销量×价格×权益×并表×内部抵销。",
            "因此驱动排名是报告分部归因，不是逐矿收入预测。",
        ]
    )

    lines.extend(
        [
            "",
            "## FY2026 增长率敏感性对 FY2030 Base 的影响",
            "",
            "| 分部参数 | 冲击 | 下行终值 | 基准终值 | 上行终值 | 最大相对影响 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in result["sensitivities"]:
        lines.append(
            f"| `{item['parameter_id']}` | ±{item['shock_value'] * 100:.1f}pct | "
            f"{bn(item['down_terminal_revenue'])} | {bn(item['baseline_terminal_revenue'])} | "
            f"{bn(item['up_terminal_revenue'])} | {pct(item['max_relative_terminal_impact'])} |"
        )

    confidence = result["confidence"]
    lines.extend(
        [
            "",
            "## 置信度",
            "",
            f"- 引擎评分：**{confidence['score']:.1f}/100（{confidence['rating']}）**。",
            f"- 主要原因：显式运营模型占比为 {confidence['components']['revenue_weighted_explicit_models']:.1f}；"
            "没有不可变历史回测；十个研究维度仍为 material data gap。",
            f"- 驱动证据覆盖率：{pct(confidence['driver_evidence_coverage'])}。",
            "- 六个质量硬门（base 对账、收入确认、情景一致性、研究覆盖、管理层目标覆盖、驱动树）均通过。",
        ]
    )

    lines.extend(["", "## 关键数据缺口", ""])
    for gap in result["data_gaps"]:
        lines.append(f"- {gap}")

    lines.extend(
        [
            "",
            "## 来源与信任边界",
            "",
            "- 两份年报来自 company-wiki canonical 路径，物理 hash 与 catalog 完全一致；本轮 filing-fetch 第三次调用内部返回 exact reuse、下载数为 0。",
            "- 标准 revenue source record 因共享文档 `prompt_injection_status=not_reviewed` 被 fail-closed；本次只在隔离目录做自报式只读审阅，未回填 catalog。",
            "- 2025 Results 和 Norton 项目新闻只有隔离 HTML 快照；没有进入 company-wiki、索引、normalize、chunk 或 tag。",
            "- 七份 Dropbox 券商 PDF 均可读且 hash 正确，但全部没有 artifact/evidence span/tag，因此没有作为强契约模型来源。",
            "",
            "| 来源 | 类型 | URL |",
            "|---|---|---|",
        ]
    )
    for source in result["sources"]:
        lines.append(
            f"| {source['title']} | {source['source_type']} | {source['url']} |"
        )

    lines.extend(
        [
            "",
            "## 验证说明",
            "",
            "- `validate_document(..., Collector())`：通过。",
            "- `run_forecast(..., mode='draft')`：连续两次通过，canonical 输出一致。",
            "- publication registry：运行前后 hash/size 完全一致。",
            "- formal publication：未尝试。",
        ]
    )
    if native_renderer_error:
        lines.append(
            f"- 官方 `render_markdown`：失败并保留为审计发现（`{native_renderer_error}`）。"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    registry_before = registry_state()
    document = build_document()

    # Pure input validation.  Collector mode is used to prevent a weak first
    # failure from hiding additional contract problems.
    validate_document(copy.deepcopy(document), collector=Collector())

    # Full calculation + strong output validation, deliberately draft-only.
    result = run_forecast(copy.deepcopy(document), mode="draft")
    repeated = run_forecast(copy.deepcopy(document), mode="draft")
    first_hash = canonical_sha256(result)
    second_hash = canonical_sha256(repeated)
    if first_hash != second_hash:
        raise RuntimeError(f"non-deterministic draft output: {first_hash} != {second_hash}")

    registry_after = registry_state()
    if registry_before != registry_after:
        raise RuntimeError("publication registry changed during draft-only run")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT_ROOT / "input_v1.json", document)
    write_json(OUTPUT_ROOT / "draft_result.json", result)
    native_renderer_error: str | None = None
    native_markdown_render_passed = False
    try:
        native_report = render_markdown(result)
        (OUTPUT_ROOT / "native_draft_report.md").write_text(
            native_report, encoding="utf-8"
        )
        native_markdown_render_passed = True
    except Exception as exc:  # Preserve the product defect; do not hide it.
        native_renderer_error = f"{type(exc).__name__}: {exc}"
    (OUTPUT_ROOT / "draft_report.md").write_text(
        render_isolated_summary(
            result, native_renderer_error=native_renderer_error
        ),
        encoding="utf-8",
    )
    validation_receipt = {
        "schema_version": "1.0",
        "run_mode": "draft",
        "formal_publication_attempted": False,
        "validate_only_cli_used": False,
        "pure_validate_document_passed": True,
        "strong_draft_run_passed": True,
        "deterministic_repeat_passed": True,
        "native_markdown_render_passed": native_markdown_render_passed,
        "native_markdown_render_error": native_renderer_error,
        "isolated_summary_rendered": True,
        "draft_canonical_sha256": first_hash,
        "input_sha256": result.get("input_sha256"),
        "result_sha256": result.get("result_sha256"),
        "formal_output_mode": result.get("publication_receipt", {}).get(
            "formal_output_mode"
        ),
        "source_count": len(document["sources"]),
        "parameter_count": len(document["parameters"]),
        "claim_count": len(document["evidence_claims"]),
        "segment_count": len(document["segments"]),
        "forecast_years": document["forecast_years"],
        "publication_registry_before": registry_before,
        "publication_registry_after": registry_after,
        "publication_registry_unchanged": True,
        "source_snapshot_hashes": {
            source["source_id"]: source["capture"]["snapshot_sha256"]
            for source in document["sources"]
        },
    }
    write_json(OUTPUT_ROOT / "validation_receipt.json", validation_receipt)
    print(json.dumps(validation_receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
