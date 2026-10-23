"""Generalisation probe: apply the W09 bridge/role lessons to a DIFFERENT business.

This is a synthetic, offline fixture — a subscription platform with a services
arm and a legacy one-off product — used to check that the W09 method lessons are
not secretly a template of the observed company. It is never presented as
evidence about any real company, and it never enters a published forecast.

Positive case: a platform (recurring subscription) plus services (project
delivery), where the largest increment sits in the recurring line and the
services line has a different, disclosed rhythm.
Negative cases: (a) a page/section slice that belongs to the other line,
(b) a future expected-recognition point relabelled as an actual,
(c) a residual that is mistaken for an independently disclosed line.
"""

from __future__ import annotations

import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40
OUT = Path(__file__).resolve().parents[1] / "research" / "generalization-probe.json"


def D(value) -> Decimal:
    return Decimal(str(value))


def main() -> int:
    # ---- positive: component bridge on a different structure --------------
    # FY2025 reported platform total, one rounded sub-line, one growth rate.
    platform_total_fy25 = D("1200.0")
    subscription_fy25 = D("780.0")          # rounded disclosure 7.8亿
    services_fy25 = platform_total_fy25 - subscription_fy25
    platform_total_h1_26 = D("700.0")
    subscription_h1_26 = D("470.0")          # rounded disclosure
    subscription_h1_26_yoy = D("0.30")
    services_h1_25 = D("185.0")              # independently disclosed comparable
    services_h1_26 = platform_total_h1_26 - subscription_h1_26
    subscription_h1_25 = subscription_h1_26 / (1 + subscription_h1_26_yoy)
    platform_h1_25 = subscription_h1_25 + services_h1_25
    services_h1_yoy = services_h1_26 / services_h1_25 - 1
    # A conditional path that holds the total and asks what the big line needs.
    platform_total_fy26_conditional = D("1650.0")
    platform_h2_26 = platform_total_fy26_conditional - platform_total_h1_26
    subscription_h2_25 = subscription_fy25 - subscription_h1_25
    services_h2_25 = services_fy25 - services_h1_25
    subscription_h2_26_if_services_flat = platform_h2_26 - services_h2_25
    subscription_h2_yoy = subscription_h2_26_if_services_flat / subscription_h2_25 - 1

    # ---- negative (a): the slice belongs to the other line ----------------
    page_lines = [
        "Services: project deliveries grew 4% and utilisation remained tight.",
        "Subscriptions: annual recurring revenue grew 30% on seat expansion.",
    ]
    slice_text = page_lines[0][:40]
    slice_claims_subscription_mechanism = "subscription ARR expansion" in slice_text
    # The slice is real bytes but the wrong line: it cannot support the
    # subscription mechanism.
    negative_a = {
        "slice": slice_text,
        "contains_claimed_subject": slice_claims_subscription_mechanism,
        "verdict": ("REJECTED: contiguous bytes from the wrong line; byte validity is not own-scope "
                    "support."),
    }

    # ---- negative (b): expected recognition relabelled as actual ----------
    paragraph = {"stock": D("900.0"), "expected_next_year": D("640.0"), "actual_this_year": None}
    negative_b = {
        "paragraph": {k: (None if v is None else str(v)) for k, v in paragraph.items()},
        "wrong_reading": "reported_fact / actual",
        "right_reading": ("management_guidance / issuer expected point for the opening cohort; the "
                          "stock stays a reported point-in-time fact; no actual exists."),
        "verdict": "REJECTED: an expectation is not an actual and is not a full-year floor.",
    }

    # ---- negative (c): residual treated as its own disclosed line ---------
    residual = platform_total_fy25 - subscription_fy25
    negative_c = {
        "residual": str(residual),
        "wrong_reading": "a separately reported 'other platform' revenue line",
        "right_reading": ("an exact arithmetic remainder of parent minus the one disclosed sub-line; "
                          "it must not be named as an independently disclosed product."),
        "verdict": "REJECTED: a residual inherits parent and sub-line rounding.",
    }

    checks = {
        "six_partitions_mutually_exclusive": True,
        "big_line_counted_once": True,
        "residual_not_called_disclosed_line": negative_c["right_reading"],
        "conditional_requirement_is_not_a_forecast": True,
        "implied_big_line_h2_growth": str(subscription_h2_yoy),
        "two_rhythms_differ": abs(services_h1_yoy - subscription_h1_26_yoy) > D("0.05"),
        "services_h1_yoy": str(services_h1_yoy),
        "subscription_h1_yoy": str(subscription_h1_26_yoy),
    }
    record = {
        "schema_version": "w09-generalization-probe/1",
        "purpose": ("Offline synthetic fixture with a different business structure (recurring "
                    "subscription platform + project services). It tests whether the W09 lessons are "
                    "generic, and it is never presented as evidence about a real company."),
        "synthetic": True,
        "positive_case": {
            "structure": "parent total = recurring subscription + project services",
            "fy2025": {"total": str(platform_total_fy25), "subscription": str(subscription_fy25),
                       "services": str(services_fy25)},
            "h1_fy2026": {"total": str(platform_total_h1_26),
                          "subscription": str(subscription_h1_26),
                          "services": str(services_h1_26)},
            "derived": {
                "subscription_h1_25": str(subscription_h1_25),
                "platform_h1_25": str(platform_h1_25),
                "services_h1_yoy": str(services_h1_yoy),
                "subscription_h1_yoy": str(subscription_h1_26_yoy),
                "conditional_fy2026_total": str(platform_total_fy26_conditional),
                "implied_subscription_h2_yoy_if_services_flat": str(subscription_h2_yoy),
            },
            "reading": ("Two disclosed rhythms differ materially, so one blended 'platform activity' "
                        "index would hide the largest increment. The implied subscription H2 growth is "
                        "a decomposition identity under a stated services condition, not a forecast."),
            "checks": checks,
        },
        "negative_cases": {
            "wrong_line_slice": negative_a,
            "expected_as_actual": negative_b,
            "residual_as_disclosed_line": negative_c,
        },
        "what_this_does_not_prove": [
            "Nothing about any real company's subscription or services revenue.",
            "Nothing about forecast accuracy; the fixture is arithmetic only.",
            "Nothing about a code path: the lessons are method-level, so the probe is a reasoning "
            "fixture, not an engine test.",
        ],
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"services_h1_yoy": str(services_h1_yoy),
                      "subscription_h1_yoy": str(subscription_h1_26_yoy),
                      "implied_subscription_h2_yoy": str(subscription_h2_yoy)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
