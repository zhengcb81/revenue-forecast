# I-12-E 独立统计复审件（状态登记，非签署）

> 卡：`I-12-E` · attempt：`execution_runs/I-12-E/a20260926-01` · role：`implementer_i12e`
> **本件由实现者登记「独立统计复审尚未发生」这一事实；它不是复审意见、不是签署、不构成 ACCEPT。**

## 1. 复审状态

| 项 | 值 |
|---|---|
| `statistical_reviewer_assigned` | **false**（未指派；编排层另派） |
| `industry_reviewer_assigned` | **false** |
| `reviewer_signed` | **false / unsigned** |
| `implementer_signed` | **false** |
| `verdict_issued_by_reviewer` | **false** |
| `verdict_issued_by_implementer` | **false**（实现者不判定，`verdict_authority=not_the_implementer`） |
| `produces_ACCEPT` | **false** |
| 关键统计选项签署状态 | **6 项全部 PENDING / unsigned**（字段 10、字段 11 四项、字段 12） |

**逐字依据**：卡文 Owner 栏「统计与行业reviewer」；`professional_approval.json`「statistical_reviewer/industry_reviewer 均 unsigned」「任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。」；OWNER_DECISIONS §三十四 L765「实现者不自签 · 独立复审 · 落定走三件套」。

## 2. 交给独立统计 reviewer 的复审清单（本工位不得代答）

1. 复算 `evidence/I-12-D/metric_oracle_result.json` 的 14 项指标（有理数逐项）与 3 条冻结负例；
2. 复算 `metrics_by_stratum` 的 7 层 `n_companies`/`n_origins` 与 I-12-B 计数守恒（3=2+1；9=7+2）；
3. 复算 `paired_comparison.uncertainty_interval=null` 的依据（5 项未签/未批准清单）；
4. 对本卡 6 个 `inconclusive` 比较逐条裁定档位（`supported`/`unsupported`/维持 `inconclusive`）；
5. 裁定 secondary baseline 复利读法、行业/生命周期分层赋值、gap-U1/U2 处置、u-N4 sha 差异权威版；
6. 签署 6 项关键统计阈值（须早于结果解封），并触发 `design_manifest` 新版本重冻。

## 3. 本件不包含

不含任何统计判定（无 p 值、无 CI、无显著性结论）· 不含阈值选择 · 不含对预测的修改 · 不含发布措辞 · 不解除任何 BLOCKED/OPEN 项。

## 4. 声明

`unsigned` 状态如上如实登记；若编排层后续在**本卡载体**或其复审载体写入签署，须由**该 reviewer 本人**留签 + sha256，编排层不改一字转录（OWNER_DECISIONS §三十五 落点纪律同形态）。实现者不得代签，也不得把本文件改写成「已复审」。
