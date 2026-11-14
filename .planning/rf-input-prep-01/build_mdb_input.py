"""Build the MongoDB, Inc. native revenue-forecast input (schema 3.7).

Every value comes from one of two places:
  * the verified company-wiki source record produced by source_preparation.py
    (real capture receipt, real snapshot SHA-256), or
  * an excerpt of the FY2025 Form 10-K original that was opened and read
    locally (see .planning/rf-input-prep-01/mdb-fy2025-10k.txt).

Analyst growth rates are labelled ``analyst_assumption`` and carry
rationale-support claims pointing at disclosed context; they are never
presented as disclosed facts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "scripts"))

from contracts.evidence import canonical_sha256, text_sha256  # noqa: E402

ENVELOPE = ROOT / "requests" / "mongodb-envelope.json"
FILING_TEXT = ROOT / "mdb-fy2025-10k.txt"
_FILING = FILING_TEXT.read_text(encoding="utf-8")


def _slice(start: str, end: str) -> str:
    """Exact verbatim slice of the checked filing text."""
    begin = _FILING.index(start)
    finish = _FILING.index(end, begin) + len(end)
    return _FILING[begin:finish]
OUT = ROOT / "inputs" / "mongodb-fy2025-input.json"

COMPANY = "MONGODB, INC."
AS_OF = "2026-11-08"
CURRENCY = "USD"
UNIT = "million"
FY_END = "01-31"
BASE_YEAR = 2025
FORECAST_YEARS = [2026, 2027, 2028]

# Disclosed FY2025/FY2024/FY2023 (Note 9 disaggregation, USD thousands -> million)
HISTORY_TOTAL = {2023: 1284.040, 2024: 1683.011, 2025: 2006.443}
HISTORY_ATLAS = {2023: 808.263, 2024: 1105.351, 2025: 1405.184}
HISTORY_OTHER = {2023: 426.859, 2024: 521.975, 2025: 538.680}
HISTORY_SERVICES = {2023: 48.918, 2024: 55.685, 2025: 62.579}

ATLAS = "MongoDB Atlas-related"
OTHER = "Other subscription (Enterprise Advanced and related)"
SERVICES = "Services"

GROWTH = {
    ATLAS: {
        "low": {2026: 0.12, 2027: 0.09, 2028: 0.07},
        "base": {2026: 0.20, 2027: 0.18, 2028: 0.16},
        "high": {2026: 0.27, 2027: 0.24, 2028: 0.21},
    },
    OTHER: {
        "low": {2026: 0.00, 2027: -0.02, 2028: -0.03},
        "base": {2026: 0.04, 2027: 0.04, 2028: 0.03},
        "high": {2026: 0.09, 2027: 0.08, 2028: 0.07},
    },
    SERVICES: {
        "low": {2026: 0.08, 2027: 0.07, 2028: 0.06},
        "base": {2026: 0.12, 2027: 0.11, 2028: 0.10},
        "high": {2026: 0.15, 2027: 0.14, 2028: 0.13},
    },
}

SLUG = {ATLAS: "atlas", OTHER: "other_subscription", SERVICES: "services"}

# Reporting basis declared for the reported total and every historical
# observation: consolidated total (no continuing/discontinued split) and
# as-reported (no restatement), full fiscal years of the January year-end.
REPORTING_BASIS = {
    "schema_version": "rf-revenue-basis/1",
    "operations": "total",
    "statement_status": "as_reported",
    "period_kind": "fiscal_year",
}

# Verbatim passages read from the FY2025 Form 10-K original. The table rows are
# rendered in document reading order (the HTML splits cells with markup).
EXCERPTS = {
    "total_table": _slice(
        "Subscription\n| $ | 1,943,864", "1,284,040 | 100 |"
    ),
    "disagg_table": _slice(
        "Subscription product categories and services:", "1,284,040 |"
    ),
    "disagg_basis": (
        "The Company also disaggregates its subscription products between its "
        "MongoDB Atlas-related offerings and other subscription products, which "
        "include MongoDB Enterprise Advanced."
    ),
    "atlas_mix": (
        "During the year ended January 31, 2025, MongoDB Atlas revenue represented "
        "70% of our total revenue, as compared to 66% in the prior year, reflecting "
        "the continued growth of MongoDB Atlas since its introduction in June 2016."
    ),
    "atlas_mix_long": (
        "MongoDB Atlas represented 70%, 66% and 63% of our total revenue for the "
        "fiscal years ended January 31, 2025, 2024 and 2023, respectively."
    ),
    "subscription_growth": (
        "Total revenue growth reflects increased demand for our platform and related "
        "services. Subscription revenue increased by $316.5 million primarily due to "
        "an increase of $269.4 million from our Direct Sales Customers, inclusive of "
        "the impact from Direct Sales Customers who were self-serve customers of "
        "MongoDB Atlas in the prior-year period."
    ),
    "headwind": (
        "During the year ended January 31, 2025, the macroeconomic environment "
        "negatively impacted our business. For instance, we experienced slower than "
        "historical growth rates for our existing MongoDB Atlas applications."
    ),
    "rpo": (
        "As of January 31, 2025, the aggregate transaction price allocated to "
        "remaining performance obligations was $748.0 million. Approximately 59% is "
        "expected to be recognized as revenue over the next 12 months 37% in 13 to 36 "
        "months and the remainder thereafter."
    ),
    "customers": (
        "As of January 31, 2025, we had over 7,500 customers that were sold through "
        "our direct sales force and channel partners, as compared to over 7,000 and "
        "over 6,400 such customers as of January 31, 2024 and 2023, respectively."
    ),
    "atlas_customers": "We had over 53,100 MongoDB Atlas customers as of January 31, 2025.",
    "cohort_100k": (
        "The number of customers with $100,000 or greater in ARR and annualized MRR "
        "was 2,396, 2,052 and 1,651 as of January 31, 2025, 2024 and 2023, respectively."
    ),
    "deferred": (
        "Approximately 18% and 25% of the total revenue recognized in the years ended "
        "January 31, 2025 and 2024 was from deferred revenue at the beginning of each "
        "respective period."
    ),
    "policy_db": (
        "Performance obligations related to database-as-a-service solutions are "
        "recognized on a usage-basis, as the use of this service represents a direct "
        "measurement of the value of the goods or services transferred to date "
        "relative to the remaining goods or services promised under the contract."
    ),
    "policy_license": (
        "License revenue is recognized at a point in time, upon delivery and transfer "
        "of control of the underlying license to the customer, which is typically the "
        "subscription start date. Revenue from PCS is recognized ratably over the "
        "contract duration."
    ),
    "policy_services": (
        "Services Revenue. Services revenue is comprised of consulting and training "
        "services and is recognized over the period of delivery of the applicable "
        "services."
    ),
    "atlas_definition": (
        "MongoDB Atlas is our hosted multi-cloud database-as-a-service (\u201cDBaaS\u201d) "
        "offering, which we run and manage in the cloud, and includes comprehensive "
        "infrastructure and management, as well as a host of additional features, "
        "such as MongoDB Atlas Search, Vector Search, time series, data lifecycle, "
        "application-driven analytics, and stream processing."
    ),
    "rpo_quarterly": (
        "We also offer a free tier of MongoDB Atlas, which provides access to our "
        "hosted database solution with limited processing power and storage, as well "
        "as certain operational limitations."
    ),
}


def _assert_verbatim() -> None:
    for key, excerpt in EXCERPTS.items():
        if excerpt not in _FILING:
            raise AssertionError(f"excerpt {key} is not a verbatim slice of the filing text")


def main() -> int:
    _assert_verbatim()
    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    source = envelope["source"]
    sid = source["source_id"]
    snapshot = source["capture"]["snapshot_sha256"]
    receipt = canonical_sha256(
        {key: value for key, value in source["capture"].items() if key != "receipt_sha256"}
    )
    source["capture"]["receipt_sha256"] = receipt

    claims: list[dict] = []
    parameters: list[dict] = []

    def claim(
        claim_id: str,
        target_type: str,
        target_id: str,
        support_type: str,
        excerpt_key: str,
        locator: str,
        **extra,
    ) -> str:
        excerpt = EXCERPTS[excerpt_key]
        record = {
            "claim_id": claim_id,
            "source_id": sid,
            "target_type": target_type,
            "target_id": target_id,
            "support_type": support_type,
            "locator": locator,
            "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": snapshot,
            "capture_receipt_sha256": receipt,
            "verification_status": "opened_and_checked",
            "verified_by": "rf-input-prep-01/owner-harness",
            "verified_date": AS_OF,
        }
        record.update(extra)
        if record["target_type"] == "parameter":
            record.setdefault("research_role_status", "unclassified")
        claims.append(record)
        return claim_id

    def parameter(
        parameter_id: str,
        kind: str,
        value: float,
        period: str,
        dimension: str,
        definition: str,
        rationale: str,
        claim_ids: list[str],
        *,
        scenario: str | None = None,
        unit_label: str | None = None,
        revenue_basis: dict | None = None,
    ) -> None:
        record = {
            "parameter_id": parameter_id,
            "kind": kind,
            "value": value,
            "unit": unit_label or (f"{CURRENCY} {UNIT}" if dimension in {"revenue", "backlog", "monetary_balance"} else "ratio"),
            "period": period,
            "definition": definition,
            "dimension": dimension,
            "time_basis": "annual",
            "source_ids": [sid],
            "scenario": scenario,
            "rationale": rationale,
            "claim_ids": claim_ids,
        }
        if dimension in {"revenue", "backlog", "monetary_balance"}:
            record.update(currency=CURRENCY, scale=UNIT)
        if revenue_basis is not None:
            record["revenue_basis"] = dict(revenue_basis)
        parameters.append(record)

    # --- reported total -----------------------------------------------------
    claim(
        "claim_reported_total_2025",
        "parameter",
        "reported_total",
        "exact_value",
        "total_table",
        "Consolidated Statements of Operations Data - Revenue table, Total revenue row",
        extracted_value=HISTORY_TOTAL[2025],
        unit=f"{CURRENCY} {UNIT}",
        period="FY2025",
    )
    parameter(
        "reported_total",
        "reported_fact",
        HISTORY_TOTAL[2025],
        "FY2025",
        "revenue",
        "Consolidated total revenue for fiscal year ended 2025-01-31, as reported (ASC 606).",
        "As-reported consolidated total revenue; equals the sum of the three disclosed revenue categories.",
        ["claim_reported_total_2025"],
        revenue_basis=REPORTING_BASIS,
    )

    # --- segment base revenue ----------------------------------------------
    segment_rows = {
        ATLAS: (HISTORY_ATLAS[BASE_YEAR], "MongoDB Atlas-related"),
        OTHER: (HISTORY_OTHER[BASE_YEAR], "Other subscription"),
        SERVICES: (HISTORY_SERVICES[BASE_YEAR], "Services"),
    }
    for segment, (value, row_label) in segment_rows.items():
        slug = SLUG[segment]
        cid = claim(
            f"claim_{slug}_base",
            "parameter",
            f"{slug}_base",
            "exact_value",
            "disagg_table",
            f"Note 9 Revenue - Disaggregation of Revenue, row '{row_label}'",
            extracted_value=value,
            unit=f"{CURRENCY} {UNIT}",
            period="FY2025",
        )
        parameter(
            f"{slug}_base",
            "reported_fact",
            value,
            "FY2025",
            "revenue",
            f"FY2025 external recognized revenue for {segment}, as disclosed in the Note 9 disaggregation.",
            "Exact disclosed row value; the three rows sum to the reported consolidated total.",
            [cid],
        )

    # --- analyst growth assumptions ---------------------------------------
    context = {
        ATLAS: ("atlas_mix", "atlas_customers"),
        OTHER: ("subscription_growth", "cohort_100k"),
        SERVICES: ("rpo", "customers"),
    }
    for segment in (ATLAS, OTHER, SERVICES):
        slug = SLUG[segment]
        first_key, second_key = context[segment]
        for scenario in ("low", "base", "high"):
            for year in FORECAST_YEARS:
                rate = GROWTH[segment][scenario][year]
                pid = f"{slug}_growth_{year}_{scenario}"
                cids = [
                    claim(
                        f"claim_{pid}",
                        "parameter",
                        pid,
                        "rationale_support",
                        first_key,
                        f"Segment context for the {segment} {scenario} {year} growth assumption",
                    )
                ]
                if scenario == "low":
                    cids.append(
                        claim(
                            f"claim_{pid}_headwind",
                            "parameter",
                            pid,
                            "rationale_support",
                            "headwind",
                            "Item 7 MD&A - macro headwind disclosure on existing Atlas application growth",
                        )
                    )
                else:
                    cids.append(
                        claim(
                            f"claim_{pid}_peer",
                            "parameter",
                            pid,
                            "rationale_support",
                            second_key,
                            f"Segment context for the {segment} {scenario} {year} growth assumption",
                        )
                    )
                direction = "decelerating" if scenario != "high" else "resilient"
                parameter(
                    pid,
                    "analyst_assumption",
                    rate,
                    f"FY{year}",
                    "ratio",
                    (
                        f"{scenario.capitalize()}-case year-over-year growth of {segment} "
                        f"recognized revenue in FY{year} (fraction, not percent points)."
                    ),
                    (
                        f"Analyst judgement: the magnitude is not disclosed. FY2025 reported "
                        f"{segment} growth and the disclosed demand/headwind context support a "
                        f"{direction} path; low-case values lean on the disclosed macro headwind "
                        f"and high-case values on the disclosed remaining-performance-obligation "
                        f"and customer-cohort momentum."
                    ),
                    cids,
                    scenario=scenario,
                    unit_label="ratio",
                )

    # --- historical revenue -------------------------------------------------
    history_claim_excerpts = {
        2023: "disagg_table",
        2024: "disagg_table",
        2025: "total_table",
    }
    history = []
    for year in (2023, 2024, 2025):
        cid = claim(
            f"claim_history_{year}",
            "historical_revenue",
            f"historical_revenue:{year}",
            "exact_value",
            history_claim_excerpts[year],
            "Consolidated revenue table / Note 9 disaggregation total row",
            extracted_value=HISTORY_TOTAL[year],
            unit=f"{CURRENCY} {UNIT}",
            period=f"FY{year}",
            evidence_role="history_base",
        )
        history.append(
            {
                "year": year,
                "value": HISTORY_TOTAL[year],
                "source_ids": [sid],
                "claim_ids": [cid],
                "revenue_basis": dict(REPORTING_BASIS),
            }
        )

    # --- recognition policies ----------------------------------------------
    recognition_claims = {}
    for segment, excerpt_key, locator in (
        (ATLAS, "policy_db", "Note 2 - revenue recognition (DBaaS usage-based)"),
        (OTHER, "policy_license", "Note 2 - revenue recognition (term license point in time, PCS ratable)"),
        (SERVICES, "policy_services", "Item 7 MD&A - Services Revenue recognition over the delivery period"),
    ):
        recognition_claims[segment] = [
            claim(
                f"claim_recognition_{SLUG[segment]}",
                "recognition_policy",
                f"recognition:{segment}",
                "policy_support",
                excerpt_key,
                locator,
            )
        ]
    atlas_definition_claim = claim(
        "claim_atlas_definition",
        "recognition_policy",
        f"recognition:{ATLAS}",
        "policy_support",
        "atlas_definition",
        "Item 1 Business - MongoDB Atlas offering description",
    )
    recognition_claims[ATLAS].append(atlas_definition_claim)
    if OTHER in recognition_claims:
        recognition_claims[OTHER].append(
            claim(
                "claim_recognition_other_license_split",
                "recognition_policy",
                f"recognition:{OTHER}",
                "policy_support",
                "policy_db",
                "Note 2 - revenue recognition (DBaaS usage-based, contrasted with licence/PCS timing)",
            )
        )

    aggregation_boundaries = {
        ATLAS: (
            "Published Atlas-related revenue aggregates usage-based DBaaS consumption billed "
            "monthly in arrears with sales-assisted annual contracts; the exact split between "
            "self-serve and sales-assisted consumption is not disclosed, so no finer recognition "
            "algorithm is invented."
        ),
        OTHER: (
            "Other subscription combines term-license revenue recognized at a point in time with "
            "post-contract support recognized ratably; the disclosed category is already recognized "
            "revenue and the license/PCS split is not published."
        ),
        SERVICES: (
            "Services aggregates consulting and training engagements recognized over the delivery "
            "period; engagement-level progress is not disclosed, so the disclosed annual category is "
            "used as-is."
        ),
    }

    segments = []
    for segment in (ATLAS, OTHER, SERVICES):
        slug = SLUG[segment]
        segments.append(
            {
                "name": segment,
                "base_revenue_parameter_id": f"{slug}_base",
                "recognition": {
                    "mode": "modeled_as_recognized",
                    "timing": "mixed",
                    "presentation": "gross",
                    "modeled_presentation": "gross",
                    "trigger": (
                        {
                            ATLAS: "Consumption of the managed database service during the period (usage-based).",
                            OTHER: "Delivery and transfer of control of the term licence, with support recognized ratably over the contract term.",
                            SERVICES: "Delivery of consulting and training services over the engagement period.",
                        }[segment]
                    ),
                    "aggregation_boundary": aggregation_boundaries[segment],
                    "basis_claim_ids": recognition_claims[segment],
                },
                "scenarios": {
                    scenario: {
                        "model": "direct_growth",
                        "driver_parameter_ids": {
                            "growth_rate": [
                                f"{slug}_growth_{year}_{scenario}" for year in FORECAST_YEARS
                            ]
                        },
                        "rationale": (
                            f"{scenario.capitalize()} case: year-over-year growth of the disclosed "
                            f"{segment} revenue category, driven by the analyst assumptions above. "
                            "direct_growth is a transparent fallback because the filing discloses no "
                            "usage, seat, or ARR denominator that could calibrate a native operating model."
                        ),
                    }
                    for scenario in ("low", "base", "high")
                },
            }
        )

    # --- research coverage --------------------------------------------------
    def evidence_claim(claim_id: str, evidence_id: str, excerpt_key: str, locator: str) -> str:
        return claim(
            claim_id,
            "growth_driver",
            evidence_id,
            "rationale_support",
            excerpt_key,
            locator,
            evidence_role="mechanism_direction",
        )

    evidence_claims = {
        "atlas_consumption_revenue_basis": evidence_claim(
            "claim_ev_atlas_consumption_basis",
            "atlas_consumption_revenue_basis",
            "policy_db",
            "Note 2 - revenue recognition (DBaaS usage-based)",
        ),
        "atlas_mix_and_growth": evidence_claim(
            "claim_ev_atlas_mix",
            "atlas_mix_and_growth",
            "subscription_growth",
            "Item 7 MD&A - revenue comparison narrative",
        ),
        "atlas_macro_slowdown": evidence_claim(
            "claim_ev_atlas_macro_slowdown",
            "atlas_macro_slowdown",
            "headwind",
            "Item 7 MD&A - macro headwind on existing Atlas application growth",
        ),
        "direct_sales_customers": evidence_claim(
            "claim_ev_direct_sales_customers",
            "direct_sales_customers",
            "customers",
            "Item 7 MD&A - Direct Sales Customers disclosure",
        ),
        "large_customer_cohort": evidence_claim(
            "claim_ev_large_customer_cohort",
            "large_customer_cohort",
            "cohort_100k",
            "Item 7 MD&A - customers with $100,000 or greater in ARR and annualized MRR",
        ),
        "rpo_stock": evidence_claim(
            "claim_ev_rpo_stock",
            "rpo_stock",
            "rpo",
            "Note 9 Revenue - Remaining Performance Obligations",
        ),
        "deferred_revenue_share": evidence_claim(
            "claim_ev_deferred_revenue_share",
            "deferred_revenue_share",
            "deferred",
            "Note 9 Revenue - Contract Liabilities",
        ),
    }

    coverage = [
        {
            "dimension": "company_foundation",
            "status": "modeled_driver",
            "conclusion": "MONGODB, INC. reports as a single operating segment; FY2025 total revenue reconciles exactly to three disclosed revenue categories.",
            "revenue_mechanism": "Recognized subscription and services revenue under ASC 606 equals the reported consolidated total.",
            "parameter_ids": ["reported_total", "atlas_base", "other_subscription_base", "services_base"],
            "source_ids": [sid],
            "rationale": "Base perimeter verified against the audited FY2025 consolidated statements of operations.",
        },
        {
            "dimension": "growth_curve",
            "status": "modeled_driver",
            "conclusion": "FY2023-FY2025 revenue grew from 1,284.0 to 2,006.4 USD million, with Atlas-related revenue rising from 808.3 to 1,405.2.",
            "revenue_mechanism": "Atlas consumption growth plus a slower-growing term-license and support base drives the consolidated curve.",
            "parameter_ids": [
                "atlas_growth_2026_base",
                "atlas_growth_2027_base",
                "atlas_growth_2028_base",
                "other_subscription_growth_2026_base",
                "services_growth_2026_base",
            ],
            "source_ids": [sid],
            "rationale": "Three consecutive audited years and the disclosed category split establish the historical curve; forward levels remain analyst assumptions.",
        },
        {
            "dimension": "industry_market",
            "status": "data_gap",
            "conclusion": "No independent database-market size or growth series was read under the bounded one-source research budget.",
            "revenue_mechanism": "Market growth would bound Atlas consumption expansion, but no measured market series enters the model.",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "A market forecast without a bound, checked primary source would be an invented input; the gap is disclosed instead.",
        },
        {
            "dimension": "competition",
            "status": "data_gap",
            "conclusion": "Competitive share and pricing evidence is limited to issuer risk-factor statements; no independent share or price series was checked.",
            "revenue_mechanism": "Competitive pricing would change monetization of consumed workload, which the model does not calibrate.",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Issuer-authored risk language cannot calibrate a competitive price or share path.",
        },
        {
            "dimension": "capacity",
            "status": "immaterial",
            "conclusion": "Delivery capacity is procured cloud infrastructure under multi-year commitments; no disclosed capacity ceiling constrains recognized revenue in the horizon.",
            "revenue_mechanism": "Atlas capacity is elastic third-party cloud capacity, so capacity is a cost input rather than a revenue ceiling.",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "The filing describes non-cancelable cloud capacity commitments as a margin matter, not a revenue constraint.",
        },
        {
            "dimension": "technology",
            "status": "modeled_driver",
            "conclusion": "The disclosed platform roadmap (vector search, stream processing, search nodes) expands the addressable workload set but has no published revenue conversion.",
            "revenue_mechanism": "New workload capabilities raise eligible consumption, which the Atlas growth assumption is conditioned on.",
            "parameter_ids": ["atlas_growth_2027_base", "atlas_growth_2028_base"],
            "source_ids": [sid],
            "rationale": "Product capability is mapped only to the growth assumption it informs; no separate revenue line is invented.",
        },
        {
            "dimension": "policy",
            "status": "data_gap",
            "conclusion": "Data-privacy and AI regulation are described qualitatively; no quantified revenue exposure or dated compliance cost was disclosed.",
            "revenue_mechanism": "Regulatory change could alter regional demand or hosting topology, which is not calibrated.",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "No quantified exposure was read, so the model cannot carry a policy-driven adjustment.",
        },
        {
            "dimension": "customers",
            "status": "modeled_driver",
            "conclusion": "Direct Sales Customers exceeded 7,500 (from 6,400 two years earlier) and customers with at least $100,000 of ARR/MRR rose to 2,396; over 53,100 Atlas customers were reported.",
            "revenue_mechanism": "Larger enterprise cohorts expand committed subscription revenue, which informs the other-subscription growth assumption.",
            "parameter_ids": ["other_subscription_growth_2026_base", "other_subscription_growth_2027_base"],
            "source_ids": [sid],
            "rationale": "Customer and cohort counts are disclosed stocks; they inform direction and level discipline but do not by themselves produce a revenue path.",
        },
        {
            "dimension": "demand",
            "status": "modeled_driver",
            "conclusion": "Demand growth is measured only through consumption; the filing discloses slower growth of existing Atlas applications under macro pressure.",
            "revenue_mechanism": "Consumption growth of existing and new applications drives usage-based Atlas revenue.",
            "parameter_ids": ["atlas_growth_2026_base", "atlas_growth_2027_base"],
            "source_ids": [sid],
            "rationale": "Demand evidence is issuer-disclosed and directional; the magnitude stays an analyst assumption.",
        },
    ]

    # --- management communication coverage ---------------------------------
    communication = [
        {
            "category": "latest_annual_filing",
            "status": "incomplete",
            "source_ids": [sid],
            "checked_date": AS_OF,
            "conclusion": (
                "FY2025 Form 10-K (filed 2025-03-21) read for the revenue note, MD&A revenue discussion "
                "and risk factors. A later FY2026 Form 10-K original exists in local storage but is not a "
                "capture-ready registered source (no published_date in the catalog projection), so the "
                "latest audited annual report could not be incorporated and completeness is not claimed."
            ),
            "rationale": (
                "The information set for this forecast is the FY2025 audited annual filing; the FY2026 "
                "audited annual is a named, disclosed acquisition gap rather than an unread silent omission."
            ),
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_results_release",
            "status": "incomplete",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "No official results release was retrieved in this bounded source acquisition; quarterly guidance wording is therefore not represented in the target ledger.",
            "rationale": "Reading a release would oblige a modelled or benchmarked target; none was acquired, so no target is asserted.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_earnings_call",
            "status": "incomplete",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "No official earnings-call transcript was retrieved; call commentary is not represented.",
            "rationale": "Transcript availability through configured providers was not established in this run.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_investor_presentation",
            "status": "incomplete",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "No investor presentation was retrieved; presentation-only targets are not represented.",
            "rationale": "Presentation originals were not part of the bounded acquisition.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "latest_strategy_communication",
            "status": "incomplete",
            "source_ids": [sid],
            "checked_date": AS_OF,
            "conclusion": "The FY2025 10-K strategy and MD&A sections were read; no dated numeric revenue target appears in them, and later strategy communications were not acquired.",
            "rationale": "The annual filing is the only official strategy original opened in this run.",
            "material_revenue_target_ids": [],
        },
        {
            "category": "material_announcements_since_last_filing",
            "status": "incomplete",
            "source_ids": [],
            "checked_date": AS_OF,
            "conclusion": "No post-FY2025-filing announcement set was acquired, so post-filing material targets are not represented.",
            "rationale": "Announcement completeness would require the issuer filing index and exhibits, which were outside this run's acquisition.",
            "material_revenue_target_ids": [],
        },
    ]

    # --- causal growth-driver tree -----------------------------------------
    tree = {
        "status": "modeled",
        "drivers": [
            {
                "driver_id": "atlas_usage_expansion",
                "title": "Atlas consumption expansion",
                "thesis": (
                    "Atlas revenue is recognized on measured consumption; continued workload migration and "
                    "new application demand raise consumed workload, while disclosed macro pressure slows the "
                    "growth of existing applications."
                ),
                "causal_chain": [
                    "Existing and new applications consume more database workload",
                    "Consumed usage is billed monthly in arrears",
                    "Usage-based revenue is recognized as the service is delivered",
                    "Atlas-related revenue grows at the modelled rate",
                ],
                "parameter_ids": [
                    "atlas_growth_2026_base",
                    "atlas_growth_2027_base",
                    "atlas_growth_2028_base",
                ],
                "segment_attribution": [{"segment_name": ATLAS, "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2028},
                "persistence": "uncertain",
                "persistence_rationale": (
                    "Consumption growth has persisted for three audited years but the issuer discloses "
                    "macro-driven slowing of existing applications, so persistence is not assumed structural."
                ),
                "evidence_nodes": [
                    {
                        "evidence_id": "atlas_consumption_revenue_basis",
                        "evidence_type": "issuer_recognition_disclosure",
                        "inference_distance": "direct",
                        "conclusion": "Atlas revenue is usage-based and billed in arrears, so consumption is the recognized-revenue driver.",
                        "claim_ids": [evidence_claims["atlas_consumption_revenue_basis"]],
                    },
                    {
                        "evidence_id": "atlas_mix_and_growth",
                        "evidence_type": "issuer_operating_disclosure",
                        "inference_distance": "one_step",
                        "conclusion": "Atlas rose to 70% of total revenue from 63% two years earlier, evidencing sustained consumption growth.",
                        "claim_ids": [evidence_claims["atlas_mix_and_growth"]],
                    },
                    {
                        "evidence_id": "atlas_macro_slowdown",
                        "evidence_type": "issuer_counterevidence",
                        "inference_distance": "contrary",
                        "conclusion": "The issuer reports slower-than-historical growth of existing Atlas applications.",
                        "claim_ids": [evidence_claims["atlas_macro_slowdown"]],
                    },
                ],
                "leading_indicators": [
                    "Quarterly Atlas consumption growth disclosed in later filings",
                    "Remaining performance obligations recognised within twelve months",
                ],
                "falsifiers": [
                    "Atlas revenue growth below 7% in any forecast year",
                    "Disclosed consumption growth turning negative",
                ],
                "counterevidence_status": "found",
                "counterevidence_rationale": (
                    "The filing itself discloses macro-driven slowing of existing Atlas applications; the "
                    "low case is built around that headwind rather than dismissed."
                ),
            },
            {
                "driver_id": "enterprise_estate_expansion",
                "title": "Enterprise estate and large-cohort expansion",
                "thesis": (
                    "Growth in Direct Sales Customers and in the at-least-$100,000 ARR cohort supports "
                    "term-license and support revenue, whose growth is far slower than Atlas."
                ),
                "causal_chain": [
                    "Direct sales expands the enterprise customer count",
                    "Large customers standardize additional workloads",
                    "Term licences and support renew and expand",
                    "Other subscription revenue grows modestly",
                ],
                "parameter_ids": [
                    "other_subscription_growth_2026_base",
                    "other_subscription_growth_2027_base",
                    "other_subscription_growth_2028_base",
                ],
                "segment_attribution": [{"segment_name": OTHER, "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2028},
                "persistence": "uncertain",
                "persistence_rationale": (
                    "Customer counts grew each year, but the disclosed category grew only 3.2% in FY2025 "
                    "as customers migrated workloads to Atlas, so expansion is modelled as low growth."
                ),
                "evidence_nodes": [
                    {
                        "evidence_id": "direct_sales_customers",
                        "evidence_type": "issuer_operating_disclosure",
                        "inference_distance": "one_step",
                        "conclusion": "Direct Sales Customers grew from over 6,400 to over 7,500 in two years.",
                        "claim_ids": [evidence_claims["direct_sales_customers"]],
                    },
                    {
                        "evidence_id": "large_customer_cohort",
                        "evidence_type": "issuer_operating_disclosure",
                        "inference_distance": "one_step",
                        "conclusion": "Customers with at least $100,000 of ARR or annualized MRR rose to 2,396.",
                        "claim_ids": [evidence_claims["large_customer_cohort"]],
                    },
                ],
                "leading_indicators": [
                    "Disclosed Direct Sales Customer count",
                    "Customers with at least $100,000 ARR",
                ],
                "falsifiers": [
                    "Other subscription revenue declining in the base case",
                    "Direct Sales Customer count contracting",
                ],
                "counterevidence_status": "searched_none_found",
                "counterevidence_rationale": (
                    "The filing discloses customer-count expansion and single-digit category growth; no "
                    "contrary evidence on the enterprise base was found within the opened filing."
                ),
            },
            {
                "driver_id": "deferred_and_backlog_visibility",
                "title": "Contracted backlog and deferred-revenue conversion",
                "thesis": (
                    "Remaining performance obligations and deferred revenue give bounded visibility into "
                    "near-term recognized revenue, including services delivered alongside deployments."
                ),
                "causal_chain": [
                    "Contracted backlog and deferred revenue are carried into the period",
                    "Obligations are satisfied as services are delivered",
                    "Previously deferred amounts are recognized as revenue",
                    "Services and support revenue is partly supported by that stock",
                ],
                "parameter_ids": [
                    "services_growth_2026_base",
                    "services_growth_2027_base",
                    "services_growth_2028_base",
                ],
                "segment_attribution": [{"segment_name": SERVICES, "weight": 1.0}],
                "horizon": {"start_year": 2026, "end_year": 2028},
                "persistence": "uncertain",
                "persistence_rationale": (
                    "Backlog is a bounded stock that converts within roughly three years; it supports the "
                    "near-term path but is not a multi-year growth mechanism."
                ),
                "evidence_nodes": [
                    {
                        "evidence_id": "rpo_stock",
                        "evidence_type": "issuer_contract_disclosure",
                        "inference_distance": "direct",
                        "conclusion": "748.0 USD million of remaining performance obligations existed at FY2025 year end, 59% due within twelve months.",
                        "claim_ids": [evidence_claims["rpo_stock"]],
                    },
                    {
                        "evidence_id": "deferred_revenue_share",
                        "evidence_type": "issuer_contract_disclosure",
                        "inference_distance": "one_step",
                        "conclusion": "18% of FY2025 revenue came from deferred revenue outstanding at the start of the period.",
                        "claim_ids": [evidence_claims["deferred_revenue_share"]],
                    },
                ],
                "leading_indicators": [
                    "Remaining performance obligations at each period end",
                    "Deferred revenue balance",
                ],
                "falsifiers": [
                    "Services revenue contracting while backlog grows",
                    "Backlog conversion slower than the disclosed twelve-month share",
                ],
                "counterevidence_status": "data_gap",
                "counterevidence_rationale": (
                    "No independent evidence on services attach or backlog cancellation was read; the "
                    "high case could therefore be exceeded or missed without a checked signal."
                ),
            },
        ],
        "rationale": (
            "One root per disclosed revenue category: each root maps only to that category's Base growth "
            "parameters, and the weights are analyst allocations rather than identified causal effects."
        ),
    }

    document = {
        "schema_version": "3.7",
        "company_name": COMPANY,
        "as_of_date": AS_OF,
        "currency": CURRENCY,
        "unit": UNIT,
        "fiscal_year_end": FY_END,
        "base_year": BASE_YEAR,
        "forecast_years": FORECAST_YEARS,
        "forecast_version": "rf-input-prep-01-mongodb-fy2025-v2",
        "sources": [source],
        "parameters": parameters,
        "evidence_claims": claims,
        "segments": segments,
        "reported_total_revenue_parameter_id": "reported_total",
        "base_adjustment_parameter_ids": [],
        "historical_revenue": history,
        "research_coverage": coverage,
        "management_communication_coverage": communication,
        "management_targets": [],
        "growth_driver_tree": tree,
        "sensitivity_tests": [
            {
                "name": "Atlas FY2028 base growth 2 percentage points lower",
                "parameter_id": "atlas_growth_2028_base",
                "shock_type": "percentage_point",
                "shock_value": 0.02,
            },
            {
                "name": "Other subscription FY2028 base growth 1 percentage point lower",
                "parameter_id": "other_subscription_growth_2028_base",
                "shock_type": "percentage_point",
                "shock_value": 0.01,
            },
            {
                "name": "Services FY2028 base growth 1 percentage point lower",
                "parameter_id": "services_growth_2028_base",
                "shock_type": "percentage_point",
                "shock_value": 0.01,
            },
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUT),
                "sources": len(document["sources"]),
                "parameters": len(parameters),
                "claims": len(claims),
                "segments": len(segments),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
