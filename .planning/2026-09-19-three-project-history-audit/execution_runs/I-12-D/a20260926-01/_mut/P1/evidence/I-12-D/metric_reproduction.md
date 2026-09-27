# I-12-D 指标复现说明（metric_reproduction）

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
