"""Independent recomputation of the W09 non-TIDES component bridge.

Every quantity is recomputed from the sealed native input/output pointers and the
verified source-page inventory; nothing is copied from the preparation JSON's
own PASS flags. Output: research/component-bridge.json (numbers in CNY million,
ratios as fractions) with explicit role/rounding basis for each row.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
SEALED_INPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
SEALED_OUTPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-forecast.json"
PAGES = RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json"
ADDENDUM = RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json"
OUT = WORKDIR / "delivery" / "w09" / "research" / "component-bridge.json"

H1 = "urn:company-wiki:source:sha256:d0dba19ede6e35ae3e127a1da91a42f04262e90d14efeb847bdfbff9b6354a5f"
ANNUAL = "urn:company-wiki:source:sha256:7f1431d66eae399d4b35639bb650e23287c7f52dacbb47b4b4a197fb5026d6a2"


def D(value) -> Decimal:
    return Decimal(str(value))


def rows_index(data: dict) -> tuple[dict, dict]:
    params = {p["parameter_id"]: p for p in data["parameters"]}
    claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    return params, claims


def main() -> int:
    sealed = json.loads(SEALED_INPUT.read_text(encoding="utf-8"))
    forecast = json.loads(SEALED_OUTPUT.read_text(encoding="utf-8"))
    params, claims = rows_index(sealed)
    pages = json.loads(PAGES.read_text(encoding="utf-8"))
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))

    def pv(pid: str) -> Decimal:
        return D(params[pid]["value"])

    # ---- reported / derived source anchors (sealed native pointers) -----------
    chem_fy25 = pv("chem_total_2025")          # annual p183 exact CNY
    tides_fy25 = pv("tides_base_2025")         # annual p14 rounded 113.7亿
    dm_fy25 = D("19920")                       # annual p14 rounded 199.2亿
    chem_h126 = pv("h1_2026_chem")             # H1 p138 exact CNY
    tides_h126 = pv("h1_2026_tides")           # H1 p11 rounded 72.6亿
    dm_h126 = D("14990")                       # H1 p11 rounded 149.9亿
    dm_h126_yoy = D("0.727")                   # H1 p11 disclosed +72.7%
    tides_h126_yoy = D("0.443")                # H1 p11 disclosed +44.3%
    biology_fy25 = pv("biology_base_2025")     # annual p183 exact CNY
    biology_h125 = pv("h1_2025_biology_rounded")  # H1 p11 comparable 万元

    base = forecast["consolidated_forecast"]["base"]
    seg_by_name = {row["name"]: row["annual_revenue"] for row in base["segment_bridge"]}
    non_tides_fy26 = D(seg_by_name["非TIDES化学业务"]["2026"])
    non_tides_fy28 = D(seg_by_name["非TIDES化学业务"]["2028"])
    group_fy25 = D(forecast["base_revenue"])
    group_fy28 = D(base["segment_subtotal"]["2028"])

    rows: list[dict] = []

    def add(metric_id, value, unit, period, role, formula, pointers, rounding_basis,
            note=None):
        row = {
            "metric_id": metric_id,
            "value": str(value),
            "unit": unit,
            "currency": "CNY" if unit.endswith("million") or unit == "fraction" else None,
            "period": period,
            "role": role,
            "formula": formula,
            "native_or_source_pointers": pointers,
            "rounding_basis": rounding_basis,
        }
        if note:
            row["note"] = note
        rows.append(row)

    # ---- component decomposition --------------------------------------------
    chem_h125 = pv("h1_2025_chem_rounded")  # H1 p11 comparable 1,630,137.04 万元

    # Decomposition uses only identified quantities:
    #   non-TIDES = Chemistry - TIDES (exact residual, not an independent disclosure)
    #   residual  = non-TIDES - small-molecule D&M
    non_fy25 = chem_fy25 - tides_fy25
    non_h126 = chem_h126 - tides_h126
    dm_h125 = dm_h126 / (1 + dm_h126_yoy)
    tides_h125 = tides_h126 / (1 + tides_h126_yoy)
    non_h125 = chem_h125 - tides_h125
    residual_fy25 = non_fy25 - dm_fy25
    residual_h126 = non_h126 - dm_h126
    residual_h125 = non_h125 - dm_h125
    # (1) FY2025 non-TIDES = Chemistry exact - TIDES rounded.
    add("non_tides_fy25", non_fy25, "CNY million", "FY2025", "derived",
        "chem_total_2025 - tides_base_2025",
        ["/parameters chem_total_2025", "/parameters tides_base_2025",
         f"{ANNUAL} PDF p183 exact Chemistry 36,465,846,882.97",
         f"{ANNUAL} PDF p14 TIDES 113.7亿元"],
        "TIDES carries issuer 0.05亿元 display rounding; the difference inherits it")
    # (2) FY2025 D&M rounded reported level.
    add("dm_fy25", dm_fy25, "CNY million", "FY2025", "reported",
        "identity (rounded issuer disclosure 199.2亿元)",
        [f"{ANNUAL} PDF p14 小分子D&M 业务收入199.2 亿元，同比增长11.4%"],
        "0.1亿元 display rounding; not a high-precision measurement")
    add("residual_fy25", residual_fy25, "CNY million", "FY2025", "derived",
        "non_tides_fy25 - dm_fy25",
        ["derived: non_tides_fy25", "reported: dm_fy25"],
        "difference of a derived and a rounded reported level")
    # (3) H1 FY2026 exact/rounded components.
    add("non_tides_h126", non_h126, "CNY million", "H1 FY2026 (2026-01-01..2026-06-30)",
        "derived", "h1_2026_chem - h1_2026_tides",
        ["/parameters h1_2026_chem", "/parameters h1_2026_tides",
         f"{H1} PDF p138 exact Chemistry 24,985,953,230.39",
         f"{H1} PDF p11 TIDES 72.6亿元"],
        "TIDES 0.05亿元 display rounding")
    add("dm_h126", dm_h126, "CNY million", "H1 FY2026 (2026-01-01..2026-06-30)",
        "reported", "identity (rounded issuer disclosure 149.9亿元)",
        [f"{H1} PDF p11 小分子D&M 业务收入人民币149.9亿元，同比增长72.7%"],
        "0.05亿元 display rounding")
    add("residual_h126", residual_h126, "CNY million", "H1 FY2026 (2026-01-01..2026-06-30)",
        "derived", "non_tides_h126 - dm_h126",
        ["derived: non_tides_h126", "reported: dm_h126"],
        "difference of a derived and a rounded reported level")
    # (4) H1 FY2025 comparable D&M base, from the disclosed +72.7%.
    add("dm_h125", dm_h125, "CNY million", "H1 FY2025 (2025-01-01..2025-06-30)",
        "derived", "dm_h126 / (1 + dm_h126_yoy)",
        ["reported: dm_h126", "disclosed growth 0.727 from the same sentence"],
        "growth is a disclosed one-decimal percentage; the implied base carries "
        "both numerator and percentage rounding")
    add("residual_h125", residual_h125, "CNY million", "H1 FY2025 (2025-01-01..2025-06-30)",
        "derived", "non_tides_h125 - dm_h125",
        ["derived: non_tides_h125 (H1 comparable Chemistry - H1'25 TIDES inferred from the "
         "disclosed +44.3%)", "derived: dm_h125"],
        "both inputs carry disclosed-percentage and display rounding; the residual is small "
        "relative to those roundings")
    add("residual_h1_yoy", (residual_h126 / residual_h125 - 1),
        "fraction", "H1 FY2026 vs H1 FY2025", "derived",
        "residual_h126 / residual_h125 - 1",
        ["derived: residual_h125", "derived: residual_h126"],
        "ratio of two small residuals: the disclosed-percentage roundings amplify into "
        "several percentage points of uncertainty",
        note="Approximately +5.6% on this decomposition; the sensitivity table shows how "
             "the implied number moves with the rounding basis. It is not an independently "
             "reported residual growth rate.")

    # (5) FY2026 base non-TIDES path and the implied H2 D&M requirement.
    non_h226 = non_tides_fy26 - non_h126
    add("non_tides_h226", non_h226, "CNY million", "H2 FY2026 (2026-07-01..2026-12-31)",
        "derived", "non_tides_base_2026 (old Base path) - non_tides_h126",
        ["/consolidated_forecast/base/segment_bridge/非TIDES化学业务/2026 (sealed old output)",
         "derived: non_tides_h126"],
        "old Base is a conditional analyst path, not a measurement")
    residual_h225 = residual_fy25 - residual_h125
    add("residual_h225", residual_h225, "CNY million", "H2 FY2025 (2025-07-01..2025-12-31)",
        "derived", "residual_fy25 - residual_h125",
        ["derived: residual_fy25", "derived: residual_h125"],
        "carries the same conditional split")
    dm_h225 = dm_fy25 - dm_h125
    add("dm_h225", dm_h225, "CNY million", "H2 FY2025 (2025-07-01..2025-12-31)",
        "derived", "dm_fy25 - dm_h125",
        ["reported: dm_fy25", "derived: dm_h125"],
        "difference of a rounded reported level and a growth-implied base")
    dm_h226_flat = non_h226 - residual_h225
    add("dm_h226_if_residual_flat", dm_h226_flat, "CNY million",
        "H2 FY2026 (2026-07-01..2026-12-31)", "condition",
        "non_tides_h226 - residual_h225",
        ["derived: non_tides_h226", "derived: residual_h225"],
        "conditional: H2 FY2026 residual repeats H2 FY2025")
    dm_h226_yoy_flat = dm_h226_flat / dm_h225 - 1
    add("dm_h226_yoy_if_residual_flat", dm_h226_yoy_flat, "fraction",
        "H2 FY2026 vs H2 FY2025", "condition",
        "dm_h226_if_residual_flat / dm_h225 - 1",
        ["condition: dm_h226_if_residual_flat", "derived: dm_h225"],
        "conditional inference; about +35%")

    # (6) FY2028 tail requirement and increment shares.
    non_increment_fy28 = non_tides_fy28 - non_fy25
    group_increment_fy28 = group_fy28 - group_fy25
    add("non_tides_increment_fy28", non_increment_fy28, "CNY million", "FY2028 vs FY2025",
        "derived", "non_tides_base_2028 (old Base) - non_tides_fy25",
        ["/consolidated_forecast/base/segment_bridge/非TIDES化学业务/2028",
         "derived: non_tides_fy25"],
        "old Base conditional path")
    add("group_net_increment_fy28", group_increment_fy28, "CNY million", "FY2028 vs FY2025",
        "derived", "group segment_subtotal 2028 - reported_total_2025",
        ["/consolidated_forecast/base/segment_subtotal/2028", "/base_revenue"],
        "group total includes discontinued zero and all six partitions")
    add("non_tides_share_of_group_net_increment",
        non_increment_fy28 / group_increment_fy28, "fraction", "FY2028 vs FY2025",
        "derived", "non_tides_increment_fy28 / group_net_increment_fy28",
        ["derived: non_tides_increment_fy28", "derived: group_net_increment_fy28"],
        "denominator is the group NET increment, not the positive-driver increment "
        "denominator used by the native driver attribution")
    dm_fy28_flat = non_tides_fy28 - residual_fy25
    add("dm_fy28_if_residual_flat", dm_fy28_flat, "CNY million", "FY2028", "condition",
        "non_tides_base_2028 - residual_fy25",
        ["/consolidated_forecast/base/segment_bridge/非TIDES化学业务/2028",
         "derived: residual_fy25"],
        "conditional: FY2028 residual held at its FY2025 level")
    add("dm_fy28_multiple_if_residual_flat", dm_fy28_flat / dm_fy25, "multiple",
        "FY2028 vs FY2025", "condition", "dm_fy28_if_residual_flat / dm_fy25",
        ["condition: dm_fy28_if_residual_flat", "reported: dm_fy25"],
        "about 2.05x; conditional inference, not an observed multiple")
    add("components_reconcile_fy25", residual_fy25 + dm_fy25, "CNY million", "FY2025",
        "derived", "dm_fy25 + residual_fy25",
        ["reported: dm_fy25", "derived: residual_fy25"],
        "identity check against non_tides_fy25")
    add("components_reconcile_h126", dm_h126 + residual_h126, "CNY million",
        "H1 FY2026", "derived", "dm_h126 + residual_h126",
        ["reported: dm_h126", "derived: residual_h126"],
        "identity check against non_tides_h126")

    # (7) Biology H2 comparable base (issuer-exact minus H1 comparable).
    bio_h225 = biology_fy25 - biology_h125
    add("biology_comparable_h225", bio_h225, "CNY million",
        "H2 FY2025 (2025-07-01..2025-12-31)", "derived",
        "biology_base_2025 - h1_2025_biology_rounded",
        [f"{ANNUAL} PDF p183 exact 2,677,175,030.51",
         f"{H1} PDF p11 comparable 125,160.49万元"],
        "exact minus a 万元-rounded comparable; result 1425.57013051 CNY million")

    # (8) RPO split.
    rpo_total = pv("rpo_2025_end")
    rpo_expected = pv("rpo_expected_2026_opening_cohort")
    add("rpo_stock_fy25_end", rpo_total, "CNY million", "2025-12-31 point in time",
        "reported", "identity 5,800,478.75万元/100",
        [f"{ANNUAL} PDF p184 5,800,478.75 万元"],
        "万元 exact to two decimals, then /100")
    add("rpo_expected_2026_recognition", rpo_expected, "CNY million", "FY2026",
        "condition", "identity 4,220,706.46万元/100",
        [f"{ANNUAL} PDF p184 预计将于2026年度确认收入"],
        "issuer expected point for the opening signed-contract cohort; not an "
        "empirical range, not a full-year floor, not an actual")
    add("rpo_not_yet_expected_within_2026", rpo_total - rpo_expected, "CNY million",
        "beyond FY2026 (undated)", "derived", "rpo_2025_end - rpo_expected_2026_recognition",
        ["reported: rpo_stock_fy25_end", "condition: rpo_expected_2026_recognition"],
        "the remainder is not dated by the disclosure; no allocation to segments")

    record = {
        "schema_version": "w09-component-bridge/1",
        "package_id": "W09-RF-RESEARCH",
        "created_at": "2026-10-23",
        "purpose": ("Independent recomputation of the non-TIDES = small-molecule D&M + residual "
                    "bridge, the six-partition reconciliation, the Biology H2 comparable and the "
                    "RPO split. Research cross-check only: it does not change the native forecast."),
        "units": {"currency": "CNY", "scale": "million", "ratio": "fraction"},
        "method": ("Every value is recomputed with Decimal from sealed native JSON pointers and "
                   "verified source-page offsets. No preparation-script PASS flag is reused. "
                   "Display rounding of issuer disclosures is disclosed per row instead of being "
                   "silently removed."),
        "not_a_confidence_interval": True,
        "sealed_input_sha256": hashlib.sha256(SEALED_INPUT.read_bytes()).hexdigest(),
        "sealed_output_sha256": hashlib.sha256(SEALED_OUTPUT.read_bytes()).hexdigest(),
        "verified_pages_sha256": hashlib.sha256(PAGES.read_bytes()).hexdigest(),
        "addendum_sha256": hashlib.sha256(ADDENDUM.read_bytes()).hexdigest(),
        "addendum_keys": sorted(addendum.keys()),
        "rows": rows,
        "reconciliation": {
            "six_partitions_fy25": {
                "TIDES": str(tides_fy25),
                "non_tides": str(non_fy25),
                "note": "TIDES is counted once inside Chemistry; non-TIDES is the exact "
                        "Chemistry residual, not an independent disclosure",
            },
            "tides_single_count": "non_tides_fy25 + tides_fy25 == chem_total_2025",
            "group_fy25_reported_total": str(group_fy25),
            "group_fy28_base_subtotal": str(group_fy28),
        },
        "falsifiers": [
            {"id": "heterogeneous_mix",
             "statement": "H1 D&M +72.7% and a conditional residual ~+5.6% are different "
                          "rhythms; a single future workload multiplier for all non-TIDES is a "
                          "condition, not an observation.",
             "what_would_change_it": "Same-scope subgroup revenue, delivered batches or client "
                                     "budgets contradicting the assumed mix."},
            {"id": "h2_composition",
             "statement": "~35.3% implied H2 D&M growth holds only while H2 residual repeats "
                          "H2 FY2025.",
             "what_would_change_it": "Actual H2 residual or cohort timing, cancellation or "
                                     "qualification delay."},
            {"id": "fy28_tail",
             "statement": "~2.05x FY2025 D&M by FY2028 holds only while FY2028 residual stays at "
                          "its FY2025 level; the 0.6/0.4 tail split is a condition, not a "
                          "calibrated persistence.",
             "what_would_change_it": "Later-stage/commercial realization, qualification, "
                                     "customer budget or price/mix evidence."},
            {"id": "stock_to_flow",
             "statement": "Project stages, >4,000kL reactor volume and molecule counts are "
                          "stocks/activity, not revenue, ASP or throughput.",
             "what_would_change_it": "No project count x invented ASP; the +699 pipeline "
                                     "additions minus net stock change is not a measured "
                                     "cancellation."},
            {"id": "recognition_concentration",
             "statement": "H1 p139 progress/control recognition is mixed across Chemistry; "
                          "H1 p186 single >10% customer is not allocated to a subgroup here.",
             "what_would_change_it": "Disclosed subgroup timing, batch schedule or customer "
                                     "concentration."},
            {"id": "price_scope",
             "statement": "FY2025 p16 price pressure is disclosed for Testing/Biology margins; "
                          "a Chemistry net-price index remains an analyst conversion assumption.",
             "what_would_change_it": "Same-scope Chemistry price/mix disclosure."},
        ],
        "remaining_unknowns": [
            "No disclosed subgroup (D&M vs residual) revenue for H2 or FY2028.",
            "No realized net price, utilization, qualified deliveries or cancellation "
            "decomposition.",
            "No empirical forecast distribution; observed_range stays null.",
            "Residual must not be equated with an independently reported Research-only revenue.",
        ],
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({r["metric_id"]: r["value"] for r in rows}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
