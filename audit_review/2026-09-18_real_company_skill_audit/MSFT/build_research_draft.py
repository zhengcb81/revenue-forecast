"""Company-specific audit workpaper builder. NOT a formal forecasting engine.

Records analyst scenario candidates and factual historical reconciliation.
Never creates claims, captures, signatures, publication receipts or forecast.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = "https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm"
CALL = "https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4"

rows = [
    ("Azure", "Agents and Infra", 72610, 101938,
     [[.28,.18,.12],[.40,.32,.25],[.48,.42,.35]],
     "New-perimeter FY26 growth was about 40%; FY27 Q1 outlook 44-45% CC. Base allows a strong first half then moderation; low represents delayed energization/consumption and high sustained delivery. Later-year decay is analyst judgment, not management guidance or estimated probability.",
     "Billable compute/token consumption and realized revenue per unit are unavailable; capex is not revenue-capable capacity. No independent capacity ceiling is quantified.",
     ["Azure comparable-perimeter growth", "new data-center commissioning", "consumption outside frontier model companies", "remaining performance obligations next-12-month portion"],
     "Two successive quarters of comparable Azure growth below 30%, reduced consumption or material commissioning delays would challenge Base."),
    ("Microsoft 365 cloud", "Agents and Infra", 84605, 100299,
     [[.10,.08,.06],[.17,.16,.14],[.22,.23,.20]],
     "New-perimeter FY26 cloud growth is observed; FY27 Q1 commercial CC guide roughly 17% and consumer mid-teens. Base reflects seat growth plus premium mix/AI monetization then gradual maturation; low represents weak paid retention and mix dilution; high requires renewed paid expansion. Published guide is not identical to aggregate GAAP cloud revenue.",
     "No same-perimeter average paid seats, realized net ARPU or opening/closing ARR bridge. Paid end-period GitHub/365 seats and list prices cannot reconstruct recognized annual revenue.",
     ["paid seat growth on recast basis", "Copilot paid adoption and renewal", "net realized commercial cloud ARPU", "usage billing contribution"],
     "Comparable seat growth below 4% or commercial-cloud growth below 12% for two quarters undermines Base."),
    ("Productivity and server licensing", "Agents and Infra", 35391, 37285,
     [[-.10,-.10,-.08],[-.05,-.04,-.03],[0,0,0]],
     "FY27 Q1 recast guide low-single decline and FY27 original product/server guide mid-single decline support shrinkage. Base treats cloud migration as persistent but moderating; low adds accelerated substitution; high is stable recognition. Migration must not be added again to cloud growth.",
     "Cloud migration cohort, licensing renewal calendar, standalone selling prices and contract recognition mix unavailable.",
     ["licensing revenue on recast basis", "large long-duration contract recognition", "on-premises to cloud migration"],
     "Licensing grows persistently while cloud growth does not weaken, or decline exceeds 10%, requiring re-evaluation of mix and recognition."),
    ("Search and advertising", "Devices and Consumer", 22171, 24835,
     [[.03,.02,.02],[.08,.08,.07],[.13,.13,.11]],
     "FY27 Q1 ex-TAC outlook is mid-to-high single growth; Base takes a moderate GAAP path with stable TAC/mix only as an assumption. Low reflects weaker ad demand and monetization; high requires share plus pricing gains. GAAP and ex-TAC growth are not treated as identical facts.",
     "Missing eligible impressions, realized CPM, TAC bridge and LinkedIn premium-subscription carve-out; forecast remains a mixed stream fallback.",
     ["recast GAAP revenue", "ex-TAC revenue and TAC bridge", "search share and query monetization", "LinkedIn advertising demand"],
     "ex-TAC growth falls below 3% or TAC/mix reverses so that GAAP growth diverges materially from Base."),
    ("XBOX", "Devices and Consumer", 23455, 21790,
     [[-.08,-.03,0],[.01,.05,.04],[.08,.10,.08]],
     "Recent revenue decline and weak FY27 Q1 contrast with management's return-to-growth aim. Base makes only a slight first-year recovery then modest content-led growth; low explicitly allows target failure; high requires successful releases and subscriptions. No probability assigned.",
     "No independently verified title-by-title release timing, paid cohorts, payer monetization or hardware/content mix bridge.",
     ["content-and-services revenue", "paid subscriptions", "release timing", "hardware decline"],
     "A material content delay or another full-year decline invalidates the near-term recovery mechanism."),
    ("Industry solutions", "Agents and Infra", 18417, 20345,
     [[.04,.04,.04],[.10,.10,.09],[.15,.15,.13]],
     "Recast cloud outlook high-single growth plus mixed products supports a cautious growth path; Base allows ERP and industry adoption with CRM hiring-cycle drag. Low assumes sales cycles remain elongated; high requires broad customer conversion.",
     "Dynamics/LinkedIn/Healthcare units and pricing are not separately reconciled under new perimeter. Industry cloud KPI is not the whole mixed revenue line.",
     ["recast industry-cloud growth", "ERP and CRM bookings", "hiring demand", "healthcare deployment timing"],
     "Cloud growth below 5% for two quarters or delayed customer projects challenges Base."),
    ("Windows OEM and devices", "Devices and Consumer", 17315, 17087,
     [[-.25,-.08,-.04],[-.18,0,.02],[-.10,.05,.04]],
     "FY27 outlook high-teens decline and Q1 low-twenties decline inform a weak first year. Base assumes inventory normalization followed by small replacement recovery; low prolongs component-cost and demand stress; high assumes faster normalization. No fabricated unit shipments.",
     "No same-perimeter OEM license units, hardware unit mix, realized pricing or channel stock-flow history.",
     ["OEM and devices revenue", "channel inventory", "PC unit demand", "component-driven pricing"],
     "Persistent excess inventory or a further double-digit decline in FY28 invalidates Base normalization."),
    ("Frontier and support services", "Agents and Infra", 7760, 8260,
     [[0,.01,.01],[.05,.05,.04],[.08,.08,.07]],
     "Service attachment to deployed enterprise systems supports moderate growth near its recent range. Low reflects customer budget rationalization; high assumes deployment and support demand. This is analyst extrapolation, with no exact management full-year target.",
     "No billable hours, realized fee rates, headcount utilization or contracted-service backlog bridge.",
     ["recast services revenue", "enterprise deployment activity", "support renewals"],
     "Services decline despite cloud deployment growth suggests decoupling and invalidates the attach assumption."),
]

draft = {
    "artifact_status": "research_assumption_draft_not_validated_forecast",
    "not_for_investment_decision": "No validated forecast, confidence score, host attestation, or skill publication is claimed.",
    "company": "Microsoft Corporation", "ticker": "MSFT", "as_of_date": "2026-09-18",
    "compiled_date": "2026-09-19", "currency": "USD", "unit": "million", "fiscal_year_end": "06-30",
    "base_year": 2026, "forecast_years": [2027,2028,2029],
    "sources_opened": [{"url":SOURCE,"published_date":"2026-09-02","locators":["slides 7-9","slides 15-18","slides 20-21"]}, {"url":CALL,"published_date":"2026-07-29","locators":["Amy Hood FY27 outlook","Satya Nadella Xbox remarks"]}],
    "historical_revenue": {"FY2025":281724,"FY2026":331839},
    "common_scenario_conditions": {
        "low":"Slower AI consumption and paid adoption, delayed capacity, weaker enterprise budgets, persistent device inventory and failed gaming recovery.",
        "base":"Delivered cloud growth and paid AI mix coexist with on-premise migration and device correction; no material new acquisition/FX benefit assumed.",
        "high":"Supply and customer consumption expand together, paid AI retention is robust, enterprise adoption widens, and legacy/consumer stabilization is faster.",
        "probabilities":"None; conditional scenarios are not calibrated prediction intervals."
    },
    "curves": [],
    "formal_blockers": ["Capture-ready canonical 10-K required for recognition review", "Actual source_preparation record and immutable source capture required", "Material guidance ledger and checked evidence claims not yet built", "Long-horizon assumptions lack frozen out-of-sample calibration", "Underlying unit/price data insufficient for auditable operating identities"]
}
for name,group,old,base,rates,why,gap,indicators,falsifier in rows:
    draft["curves"].append({"name":name,"reportable_segment":group,"FY2025_revenue":old,"FY2026_revenue":base,"history_source_url":SOURCE,"history_locator":"slide 17 As Restated", "candidate_model":"direct_growth", "assumption_kind":"analyst_assumption_for_base_scenario_stress_for_low_and_high", "annual_growth_assumptions":dict(zip(["low","base","high"],rates)),"rationale":why,"data_gap":gap,"leading_indicators":indicators,"falsifier":falsifier})

checks = {"FY2025_sum":sum(x[2] for x in rows),"FY2026_sum":sum(x[3] for x in rows)}
checks["FY2025_reconciles"] = checks["FY2025_sum"] == 281724
checks["FY2026_reconciles"] = checks["FY2026_sum"] == 331839
checks["FY2026_reportable_segments"] = {g:sum(x[3] for x in rows if x[1]==g) for g in ["Agents and Infra","Devices and Consumer"]}
checks["result_scope"] = "Historical arithmetic only; no revenue_forecast.py run or publication receipt"
draft["historical_arithmetic_checks"] = checks
(ROOT/"research_assumptions.draft.json").write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding="utf-8")
lines = ["# MSFT 三情景假设草案", "", "状态：研究工作底稿，尚非 validated forecast。未输出 forecast.json/forecast.md，未伪造 capture 或 receipt。", "", "所有增长率为分析师待验证假设，不是公司披露的预测值。低/高情景不代表概率区间。各格依次为 FY2027 / FY2028 / FY2029。", "", "| 业务 | Low | Base | High |", "|---|---|---|---|"]
for r in draft["curves"]:
    f=lambda vals:" / ".join(f"{x:.0%}" for x in vals)
    lines.append("| "+r["name"]+" | "+" | ".join(f(r["annual_growth_assumptions"][s]) for s in ["low","base","high"])+" |")
lines += ["", "上述量级以新口径历史和短期指引为锚，但FY2028–FY2029减速/复苏路径主要属于判断；未做独立单位经济校准。完整机制、缺口、领先指标、反证阈值和历史桥见 research_assumptions.draft.json。", "", "## 口径核验", "", f"FY2025八线和={checks['FY2025_sum']}，FY2026八线和={checks['FY2026_sum']}；与公司总额闭合。FY2026新两分部为{checks['FY2026_reportable_segments']}。", "", "最新IR首页→aka.ms/KPIFY27→微软官方CDN FY27ExternalKPIs.pptx 与SEC 8-K/Exhibit 99.1相互印证重分类存在。PPT viewer在web工具返回安全重定向错误，未声称该PPT字节已在本子任务下载核验。SEC一手正文已实际打开。", "", "此草案保留旧模板作为过程证据，但正式输入必须使用八条新口径曲线。"]
(ROOT/"scenario_draft.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps(checks,ensure_ascii=False,indent=2))
