# I-12-E 局限与覆盖登记（limitations）

> 卡：`I-12-E` · attempt：`execution_runs/I-12-E/a20260926-01` · role：`implementer_i12e`
> 本件是**实现者的登记**，不是统计判定、不是签署、不产生 ACCEPT、不发发布措辞。

## 1. 前提未满足（卡文 L9-L10 逐字核对）

- 「冻结阈值已在结果前批准」= **不满足**：`professional_approval.json` 统计/行业 reviewer 双双 unsigned，6 项关键统计阈值全 PENDING（派单记「双签在飞」）。
- 「全量结果可见」= **不满足**：`scorable_samples=0`、`n_pairs=0`、`forecast_values_frozen=0`、`unblind_receipt=not_issued`、`test_results_unsealed=false`。
- ⇒ **0/2** 满足 ⇒ 每个预注册比较记 **`inconclusive`**（`accuracy_qualification.json`），并声明这是**默认登记而非专业判定**（`verdict_is_fail_closed_default_not_professional_determination=true`）。
- ⇒ 本卡整卡判定：**blocked（合格形态）**，裁定权归统计与行业 reviewer / 编排层。

## 2. 范围限定（卡文动作 2）

结论只限定到：`dataset`（本审计三家公司，可评 entity=2）· `model_version`（unbound，无预测值）· `industry`（**unproven**，设计未赋值）· `lifecycle`（**unproven**，设计未赋值）· `disclosure_quality`（4 signed / 2 STOP / 3 段无 case）· `horizon`（FY2027：h2FY 紫金、h1FY 微软）。**不外推**到任何未列范围。

## 3. 未覆盖分层（全部标 unproven，共 7 项）

| 分层 | 状态 | 原因 |
|---|---|---|
| market=H（小米） | `unproven` | gap-U1 原文不可读 / gap-U2 披露日未登记 ⇒ 排除（EX-001），不补选公司 |
| industry（行业） | `unproven` | 设计字段 3 未赋值 |
| lifecycle（生命周期） | `unproven` | 设计字段 3/7 未赋值 |
| 微软 PBP / IC 披露适配 | `unproven` | `partial_STOP_DISCLOSURE_ADAPTATION` |
| 紫金 贸易/其他 + 微软 MPC | `unproven` | 无披露适配 case |
| model_version | `unproven` | params 未放行 ⇒ 无 forecast 可评 |
| dataset 外推 | `unproven` | 仅 3 家公司单一数据集 |

## 4. 负结果与不确定性显式保留（卡文验收）

- **负结果保留**：本 attempt 的负结果即 `n=0` 与 `descriptive_only`（继承 I-12-D）——不隐藏、不四舍五入、不以「样本太少」为由删除任何已登记层。
- **负 skill 规则先冻结**：`negative_skill_preserved_rule=true`；一旦有 skill 观测，负值不得删除。
- **失败层保留**：`failed_strata_preserved_rule=true`；失败层不并层、不静默丢弃。
- **不确定性**：`uncertainty_interval=null`（方法未批准，I-12-D `interval_method_not_approved=true`）；无概率声明 ⇒ `interval_score`/`pinball` 禁用。
- **状态链**：`descriptive_only`（I-12-D）→ `inconclusive`（本卡）→ 无 `supported`/`unsupported`。

## 5. 三栏合并但禁止一栏 PASS 盖另一栏（卡文动作 3）

| 栏 | 状态 | 不外溢 |
|---|---|---|
| 公式资格 | `pass_scoped`（M01–M31 仅 A–C 公式面） | **不蕴含**披露适配、**不蕴含**准确性 |
| 披露适配 | `partial`（4 signed / 2 STOP / 3 段无 case） | **不蕴含**准确性 |
| 准确性 | **`unproven`**（0 可评分样本 + 阈值未签 + 结果封存） | 不因前两栏而改写 |

`no_cross_column_pass_override=true`（由校验器 E3 强制）· `accuracy_improvement_claimed=false`。

## 6. 停止条款登记（逐字）

- `STOP_CLAIM`：「把31公式通过或少数公司拟合直接称准确率提升→STOP_CLAIM。」→ **未触发**（本件无任何准确性提升主张；准确性栏 = `unproven`）。
- `STOP_RELEASE_WORDING`：「没有达到统计判定条件却宣称普遍有效→STOP_RELEASE_WORDING。」→ **未触发**（无普遍有效主张；正式发布格 = `blocked`）。

## 7. 本轮不做什么

不修预测（`forecast_fixed_this_round=false`）· 不放行参数 · 不自签 · 不产生 ACCEPT · 不改任何卡 status/decision/decision_sha256 · 不解除 OPEN-2/3/5/6 · 不读测试/准确性结果（封存）· 禁 git（含 `git status`）· 禁联网 · 封盘 `f2178768…` 零字节。

## 8. 解除本卡 blocked 的条件（交复审/编排层）

1. 统计 + 行业 reviewer 双签落地（6 项阈值），且**早于**任何结果解封；
2. `design_manifest` 新版本重冻并经独立复核；
3. 参数放行决定（owner/复审）+ 目标期 FY2027 结束；
4. 独立 reviewer 收集封存实际值并出具 `unblind_receipt` → 新 attempt 才可把比较档位从 `inconclusive` 改为 `supported`/`unsupported`（结果后补阈值一律作废为探索性）。

> 局限声明（逐字，research_cards.json `metric_numeric_oracle.limitation`）：n=3只验证指标实现，不能证明模型准确性改善、覆盖校准或统计显著性。
> `accuracy_improvement_claimed=false`。
