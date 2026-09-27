#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-D sample-side evidence builder.

Gate rule (card action 0): only runs after _metric_oracle.py reported
all_expected_pass=True and all negatives pass.  Real scorable samples = 0 upstream,
so the per-sample detail table is emitted header-only and every aggregate is
registered as undefined / descriptive_only (fail-closed, no significance claim).
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "evidence", "I-12-D")

STRATA = [
    {"stratum_id": "market=A", "axis": "market", "value": "A", "companies": ["CN-ZIJIN"],
     "n_companies": 1, "n_origins": 1, "origins": ["2026-03-20"], "registered_samples": 4, "n_scorable": 0},
    {"stratum_id": "market=US", "axis": "market", "value": "US", "companies": ["US-MSFT"],
     "n_companies": 1, "n_origins": 1, "origins": ["2026-07-29"], "registered_samples": 3, "n_scorable": 0},
    {"stratum_id": "market=H", "axis": "market", "value": "H", "companies": [],
     "n_companies": 0, "n_origins": 0, "origins": [], "registered_samples": 0, "n_scorable": 0,
     "note": "小米（HK）按设计字段 3 排除（gap-U1/gap-U2）⇒ 不入分层；不补选公司（卡文停止②）"},
    {"stratum_id": "horizon=h2FY", "axis": "horizon", "value": "h2FY", "companies": ["CN-ZIJIN"],
     "n_companies": 1, "n_origins": 1, "origins": ["2026-03-20"], "registered_samples": 4, "n_scorable": 0},
    {"stratum_id": "horizon=h1FY", "axis": "horizon", "value": "h1FY", "companies": ["US-MSFT"],
     "n_companies": 1, "n_origins": 1, "origins": ["2026-07-29"], "registered_samples": 3, "n_scorable": 0},
    {"stratum_id": "industry=unassigned", "axis": "industry", "value": None, "companies": ["CN-ZIJIN", "US-MSFT"],
     "n_companies": 2, "n_origins": 2, "origins": ["2026-03-20", "2026-07-29"], "registered_samples": 7,
     "n_scorable": 0, "unproven": True,
     "note": "设计字段 3 未给出行业取值 ⇒ 分层键留空，按未覆盖分层标 unproven（卡文动作 2 的 n 仍如实报）"},
    {"stratum_id": "lifecycle=unassigned", "axis": "lifecycle", "value": None, "companies": ["CN-ZIJIN", "US-MSFT"],
     "n_companies": 2, "n_origins": 2, "origins": ["2026-03-20", "2026-07-29"], "registered_samples": 7,
     "n_scorable": 0, "unproven": True,
     "note": "设计字段 3/7 未给出生命周期取值 ⇒ 同上，标 unproven"},
]

METRICS = ["MAE", "WAPE", "Bias_U", "NormalizedBias", "skill_vs_baseline",
           "scenario_containment", "mean_width", "normalized_width"]


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    os.makedirs(EV, exist_ok=True)
    oracle_path = os.path.join(EV, "metric_oracle_result.json")
    neg_path = os.path.join(EV, "metric_negative_results.json")
    if not (os.path.exists(oracle_path) and os.path.exists(neg_path)):
        print("HARNESS: action-0 oracle outputs missing; refusing to write sample side")
        return 1
    with open(oracle_path, "r", encoding="utf-8") as f:
        oracle = json.load(f)
    with open(neg_path, "r", encoding="utf-8") as f:
        negs = json.load(f)
    if oracle.get("verdict") != "PASS_metric_implementation_qualified_only" or not negs.get("all_pass"):
        print("HARNESS: metric implementation not qualified; refusing to write sample side")
        return 1

    # ---------- sample_errors.csv (header only; 0 scorable rows) ----------
    header = ["sample_id", "entity", "segment_code", "origin", "horizon_fy", "model_version",
              "actual", "forecast_base", "baseline_primary", "signed_error", "abs_error",
              "baseline_abs_error", "scorable", "exclusion_reason"]
    with open(os.path.join(EV, "sample_errors.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)

    # ---------- metrics_by_stratum.json ----------
    strata_out = []
    for s in STRATA:
        row = dict(s)
        row["metrics"] = {m: {"value": None, "defined": False, "reason": "no_scorable_samples"}
                          for m in METRICS}
        row["state"] = "descriptive_only"
        strata_out.append(row)

    metrics_by_stratum = {
        "schema": "i12d_metrics_by_stratum/1",
        "card": "I-12-D",
        "attempt": "execution_runs/I-12-D/a20260926-01",
        "role": "implementer_i12d",
        "detail_source": {"path": "evidence/I-12-D/sample_errors.csv", "data_rows": 0,
                          "note": "明细结构在位（逐样本列），本 attempt 无任何可评分观测 ⇒ 0 行；不以平均数代替明细（卡文动作 1）"},
        "counts": {
            "registered_samples": 7,
            "scorable_samples": 0,
            "missing_pairs": 7,
            "zero_denominator_occurrences": 0,
            "epsilon_substitutions": 0,
            "excluded_entities": 1,
            "excluded_rows": 2
        },
        "missing_and_zero_denominator_policy": {
            "missing": "缺失观测排除并计数，不插补、不前值填充（设计字段 9）",
            "zero_denominator": "分母 0 ⇒ undefined 并计数，不加任意 epsilon（设计字段 9；实测于 metric_negative_results N1）"
        },
        "weights": {
            "primary": "entity 等权 macro-average",
            "secondary": "micro（WAPE 汇总口径）",
            "both_must_be_reported": True,
            "reported_here": "两套均登记为 undefined（0 可评分观测）；聚合权重结构已冻结，未用于任何宣称"
        },
        "strata": strata_out,
        "state": "descriptive_only",
        "state_reason": "样本未达设计要求（卡文停止②逐字）：可评分样本 0 ⇒ descriptive_only，不宣称显著更准确",
        "significance_claimed": False,
        "accuracy_improvement_claimed": False,
        "metrics_not_computed_reason": "上游 I-12-B scorable_samples=0（目标期未结束 + 解封门未满足）与 I-12-C forecast_values_frozen=0（params 未放行）⇒ 无可评分观测",
        "oracle_gate": {"metric_implementation": "PASS (metric_oracle_result.json)",
                        "negatives": "PASS (metric_negative_results.json)",
                        "stop_METRICS_triggered": negs.get("stop_triggered")}
    }
    write_json(os.path.join(EV, "metrics_by_stratum.json"), metrics_by_stratum)

    # ---------- paired_comparison.json ----------
    paired = {
        "schema": "i12d_paired_comparison/1",
        "card": "I-12-D",
        "attempt": "execution_runs/I-12-D/a20260926-01",
        "role": "implementer_i12d",
        "pairing_rule": "成对同样本：模型 vs baseline 在完全相同的 entity×segment×origin×horizon 观测集上比较（同缺失集）；设计字段 11 structure_frozen",
        "cluster_unit": "entity",
        "block_unit": "origin",
        "time_dependence_rule": "时间相关性按 origin 分块重抽样处理，不假设观测独立（同上；本 attempt 未执行重抽样——无观测且方法未批准）",
        "n_pairs": 0,
        "n_companies": {"A": 1, "US": 1, "H": 0},
        "n_origins": {"2026-03-20": 1, "2026-07-29": 1},
        "paired_differences": [],
        "skill_vs_baseline": {"value": None, "defined": False, "reason": "no_scorable_samples"},
        "state": "blocked_no_scorable_samples",
        "uncertainty_interval": None,
        "interval_method_not_approved": True,
        "interval_method_pending_items": [
            "confidence_level（CI 水平/α）— PENDING/unsigned（设计字段 11）",
            "bootstrap_or_resample_repetitions — PENDING/unsigned",
            "random_seed — PENDING/unsigned",
            "multiplicity_correction — PENDING/unsigned（候选 Holm FWER / BH FDR，由统计 reviewer 定）",
            "最小样本量/功效/可接受 CI 宽度 — PENDING（设计字段 10）"
        ],
        "why_no_interval": "卡文动作 3 要求「按已批准方法」；当前无任何已批准的区间方法（阈值 unsigned）⇒ 不算区间、不猜种子、不挑方法",
        "cluster_block_repeated_years_rule": "重复年度不是独立公司 ⇒ 以 entity 为 cluster、origin 为 block（已在结构层冻结；本 attempt 无观测可聚）",
        "significance_claimed": False,
        "negative_skill_preserved_rule": "负 skill 不得删除（设计字段 1 / metric_definitions）；本 attempt 无 skill 可删",
        "state_reason": "上游 forecast_values_frozen=0 且 scorable_samples=0"
    }
    write_json(os.path.join(EV, "paired_comparison.json"), paired)

    # ---------- interval_diagnostics.json ----------
    interval = {
        "schema": "i12d_interval_diagnostics/1",
        "card": "I-12-D",
        "attempt": "execution_runs/I-12-D/a20260926-01",
        "role": "implementer_i12d",
        "probabilistic_claim_made": False,
        "low_high_semantics": "scenario_band_not_probabilistic（设计字段 9）",
        "interval_score": {"enabled": False, "status": "disabled",
                           "reason": "无 1-alpha 名义覆盖率事前声明 ⇒ 情景带禁用统计区间得分（metric_definitions boundary）",
                           "gate_tested": "metric_negative_results case E2（请求即被拒）"},
        "pinball": {"enabled": False, "status": "disabled",
                    "reason": "无事前声明的 tau 分位预测；不可把 base 擅自称中位数"},
        "confidence_intervals": {
            "computed": False,
            "reason": "阈值/方法未签署（设计字段 11 threshold_items_unsigned + 字段 10 PENDING）⇒ 卡文动作 3 的「已批准方法」不存在",
            "pending_items": [
                "confidence_level", "bootstrap_or_resample_repetitions", "random_seed",
                "multiplicity_correction", "min_sample_size/power/acceptable_ci_width"
            ],
            "no_seed_fixed_by_implementer": True,
            "seed_note": "实现者不擅自固定一个『刚好好看』的种子（设计字段 11 prohibition 逐字）"
        },
        "scenario_containment": {"value": None, "defined": False, "reason": "no_scorable_samples",
                                 "must_report_together_with": "interval_width（同时报宽度）"},
        "interval_width": {"mean": None, "normalized": None, "defined": False,
                           "reason": "no_scorable_samples",
                           "boundary": "high<low = 数据错误（实测于 metric_negative_results case E1）；极宽区间的高包含率不代表质量高"},
        "n_scorable": 0,
        "state": "descriptive_only",
        "significance_claimed": False
    }
    write_json(os.path.join(EV, "interval_diagnostics.json"), interval)

    # ---------- metric_reproduction.md ----------
    md = """# I-12-D 指标复现说明（metric_reproduction）

> 卡：`I-12-D` · attempt：`execution_runs/I-12-D/a20260926-01` · role：`implementer_i12d`
> 目的：让独立 reviewer **手算抽核** oracle 与聚合权重；本件不含任何准确性主张。

## 1. Oracle 手算（合成 n=3；期望逐字来自 `research_cards.json` `metric_numeric_oracle.expected`）

- 误差和 = 10 + 10 − 20 = 0 ⇒ `Bias_U = 0/3 = 0`
- 绝对误差和 = 10 + 10 + 20 = 40 ⇒ `MAE = 40/3`，`WAPE = 40/300 = 2/15`
- 实际值分母 = 100 + 0 + 200 = 300 ⇒ `NormalizedBias = 0/300 = 0`，`normalized_width = 70/300 = 7/30`
- baseline 绝对误差和 = 0 + 0 + 50 = 50 ⇒ `skill = 1 − 40/50 = 1/5 = 0.2`
- 情景包含：S1 `90<=100<=120` T；S2 `0<=0<=20` T；S3 `170<=200<=190` F ⇒ `2/3`
- 宽度和 = 30 + 20 + 20 = 70 ⇒ `mean_width = 70/3`
- 比较规则（逐字）：`有理数按分子/分母独立求期望，比较abs(error)<=1e-12；布尔、sample_id与undefined原因精确比较。`

复跑：`python _metric_oracle.py` → 输出 `evidence/I-12-D/metric_oracle_result.json`（`all_expected_pass=true`、`verdict=PASS_metric_implementation_qualified_only`）与 `metric_negative_results.json`（5/5 pass，`stop_triggered=false`）。

## 2. 负例与边界（逐条实测）

| 用例 | 输入 | 观测 | 判定 |
|---|---|---|---|
| N1 零分母 | `actual=[0,0,0]` | WAPE / NormalizedBias / normalized_width = `undefined`+`zero_denominator`；MAE 仍可定义；**未加 epsilon**；负 skill −1/5 保留 | pass |
| N2 样本错位 | `forecast_sample_ids=[S1,S3,S2]` | `status=rejected`、`reason=sample_id_misalignment`，不产出任何指标 | pass |
| N3 baseline loss=0 | `baseline=[100,0,200]` | `skill=undefined`（`zero_denominator_baseline_loss`），未记 100% improvement | pass |
| E1 high<low | `high=[80,20,190]` | S1 标 `interval_data_error`，`mean_width=undefined`，不静默平均 | pass |
| E2 无名义覆盖 | 请求 `IS_alpha` | `interval_score=rejected`、`pinball=rejected` | pass |

## 3. 真实样本侧（fail-closed）

- `sample_errors.csv` = **仅表头、0 数据行**：上游 `I-12-B scorable_samples=0`（目标期 FY2027 未结束 + 解封门 `currently_satisfied=false`）与 `I-12-C forecast_values_frozen=0`（`params_released=false`）⇒ 无观测可评分。
- `metrics_by_stratum.json`：逐层 `n_companies`/`n_origins` 如实登记（market A 1/1、US 1/1、H 0/0；h2FY 1/1、h1FY 1/1），`n_scorable=0`，`state=descriptive_only`，`significance_claimed=false`。
- `paired_comparison.json`：`n_pairs=0`、`uncertainty_interval=null`、`interval_method_not_approved=true`（CI/种子/重抽样/多重比较/样本量 5 项 unsigned 或 PENDING）。
- `interval_diagnostics.json`：`probabilistic_claim_made=false`，`interval_score`/`pinball` 禁用。

## 4. 聚合权重（结构已冻结，本 attempt 未产生数值）

primary = entity 等权 macro-average；secondary = micro（两套必须并报）。两者在本 attempt 均为 `undefined (no_scorable_samples)`；**不得**因未报数值而改用其他权重或指标（卡文验收「未经批准不得换指标」）。

## 5. Limitation（逐字）

> n=3只验证指标实现，不能证明模型准确性改善、覆盖校准或统计显著性。

> 样本未达设计要求→descriptive_only，不宣称显著更准确。（卡文停止②逐字）
"""
    with open(os.path.join(EV, "metric_reproduction.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)

    print("sample_errors.csv rows=0 (header only)")
    print("metrics_by_stratum strata=%d state=descriptive_only" % len(strata_out))
    print("paired_comparison n_pairs=0 interval=null")
    print("interval_diagnostics probabilistic=false")
    print("metric_reproduction.md written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
