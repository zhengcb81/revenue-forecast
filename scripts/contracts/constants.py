"""Shared literal constants, extracted from revenue_core.py (R9 split).

Single source of truth for schema/enum constants; revenue_core re-exports
them so the external ``from revenue_core import X`` surface is unchanged.
"""

from __future__ import annotations


SCENARIOS = ("low", "base", "high")


SKILL_VERSION = "4.0.0"


FORECAST_SCHEMA_VERSION = "3.7"


SUPPORTED_FORECAST_SCHEMA_VERSIONS = {
    "3.0",
    "3.1",
    "3.2",
    "3.3",
    "3.4",
    "3.5",
    "3.6",
    FORECAST_SCHEMA_VERSION,
}


WORKFLOW_RECEIPT_SCHEMA_VERSION = "1.0"


PUBLICATION_RECEIPT_SCHEMA_VERSION = "1.0"


PARAMETER_KINDS = {
    "reported_fact",
    "derived_fact",
    "management_guidance",
    "analyst_assumption",
    "scenario_stress",
}


SOURCE_RANKS = {
    "audited_filing": 1,
    "exchange_filing": 1,
    "regulatory_filing": 1,
    "official_statistics": 1,
    "company_release": 2,
    "investor_presentation": 2,
    "earnings_transcript": 2,
    "official_operating_data": 2,
    "contract_award": 3,
    "customer_filing": 3,
    "tender_document": 3,
    "sector_regulator": 3,
    "industry_association": 4,
    "primary_market_dataset": 4,
    "specialist_research": 5,
    "reputable_news": 5,
}


PARAMETER_DIMENSIONS = {
    "revenue",
    "quantity",
    "ratio",
    "revenue_per_unit",
    "activity",
    "revenue_per_activity",
    "monetary_balance",
    "area",
    "revenue_per_area",
    "backlog",
    "coverage_units",
    "reserve_volume",
}


# ZR-602: asset fact basis contract — ownership/standard/measurement-date
# vocabulary for mining asset facts (resource/reserve/grade/capacity/permit).
# ``basis`` is an additive optional parameter key: when present it must carry
# every required field (fail-closed, no half-baked basis), and asset-fact
# family drivers are unit-consistent (normalized equality, no kt-vs-t drift).
ASSET_FACT_OWNERSHIP_BASES = {
    "one_hundred_percent",
    "equity_share",
    "consolidated",
}

ASSET_FACT_BASIS_REQUIRED = (
    "ownership_basis",
    "reporting_standard",
    "measurement_date",
)

# Generic mining asset-fact model families (model ids are generic mining
# vocabulary, not company/mine names — zero product hardcoding).
ASSET_FACT_MODELS = frozenset({"resource", "reserve_depletion"})


# ZR-604: dual-assertion conflict resolution — when parameters with the
# same semantic key (definition/period/unit/scenario) carry different
# values, ALL must carry resolution_status and at most one is accepted;
# otherwise the original hard-fail (unresolved conflict) applies.
# Assertion_status identifies which assertion is primary vs secondary;
# resolution_status tracks the review outcome.
ASSERTION_STATUSES = {
    "primary",
    "secondary",
}

RESOLUTION_STATUSES = {
    "accepted",
    "rejected",
    "pending_review",
    "under_review",
}


MONETARY_DIMENSIONS = {
    "revenue",
    "revenue_per_unit",
    "revenue_per_activity",
    "monetary_balance",
    "revenue_per_area",
    "backlog",
}


TIME_BASES = {"annual", "point_in_time"}


RECOGNITION_MODES = {"modeled_as_recognized", "lagged_activity"}


RECOGNITION_TIMING = {"point_in_time", "over_time"}


PRESENTATIONS = {"gross", "net"}


ADJUSTMENT_CATEGORIES = {
    "intersegment_elimination",
    "acquisition_contribution",
    "disposal_contribution",
    "foreign_exchange",
    "reclassification",
    "other",
}


RESEARCH_DIMENSIONS = (
    "company_foundation",
    "growth_curve",
    "industry_market",
    "competition",
    "capacity",
    "technology",
    "policy",
    "customers",
    "demand",
)


RESEARCH_COVERAGE_STATUSES = {"modeled_driver", "data_gap", "immaterial"}


MANAGEMENT_COMMUNICATION_CATEGORIES = (
    "latest_annual_filing",
    "latest_results_release",
    "latest_earnings_call",
    "latest_investor_presentation",
    "latest_strategy_communication",
    "material_announcements_since_last_filing",
)


MANAGEMENT_COMMUNICATION_STATUSES = {"checked", "not_available", "not_applicable"}


MANAGEMENT_TARGET_TREATMENTS = {
    "modeled_scenario",
    "scenario_boundary",
    "sensitivity_only",
    "unmodeled_data_gap",
    "out_of_horizon",
}


MANAGEMENT_TARGET_PERIMETERS = {"matched", "reconciled", "mismatch"}


MANAGEMENT_TARGET_COMPARISONS = {"at_least", "at_most", "approximately"}


MANAGEMENT_TARGET_MEASUREMENT_BASES = {
    "annual_period",
    "run_rate_at_period_end",
    "cumulative_periods",
    "ambiguous",
}


GROWTH_DRIVER_TREE_STATUSES = {"modeled", "data_gap"}


GROWTH_DRIVER_PERSISTENCE = {
    "multi_year_structural",
    "cyclical",
    "temporary",
    "uncertain",
}


GROWTH_DRIVER_INFERENCE_DISTANCES = {"direct", "one_step", "analogical", "contrary"}


GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES = {"found", "searched_none_found", "data_gap"}
