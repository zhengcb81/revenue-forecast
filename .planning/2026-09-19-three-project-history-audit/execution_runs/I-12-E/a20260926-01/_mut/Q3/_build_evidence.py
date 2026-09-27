#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-E evidence builder (deterministic).

Premise check (card L9-L10) is evaluated first and recorded verbatim:
  - frozen thresholds approved before results  -> FALSE (double sign-off in flight,
    6 key statistical options PENDING)
  - all results visible                        -> FALSE (0 scorable samples,
    results sealed, unblind receipt not issued)
=> fail-closed: every pre-registered comparison is registered `inconclusive`
   (a default registration, NOT a professional determination).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "evidence", "I-12-E")

CARD = "I-12-E"
ATTEMPT = "execution_runs/I-12-E/a20260926-01"
ROLE = "implementer_i12e"

THRESHOLDS_UNSIGNED = [
    "字段 10：最小公司数 / 每层最小样本数 / 目标统计功效 / 可接受 CI 宽度 / 效应量定义 — PENDING",
    "字段 11：置信水平（CI level/α） — PENDING（unsigned）",
    "字段 11：重复抽样次数 — PENDING（unsigned）",
    "字段 11：随机种子 — PENDING（unsigned）",
    "字段 11：多重比较校正方法 — PENDING（unsigned；候选 Holm FWER / BH FDR）",
    "字段 12：成功/失败阈值（经济显著改善幅度、可接受偏差、情景包含率、区间宽度） — PENDING",
]

COMPARISONS = [
    ("CMP-PRIMARY-MACRO", "primary_endpoint macro（entity 等权）", 2, 2, 7, 0),
    ("CMP-MARKET-A", "market=A（紫金矿业）", 1, 1, 4, 0),
    ("CMP-MARKET-US", "market=US（微软）", 1, 1, 3, 0),
    ("CMP-HORIZON-h2FY", "horizon=h2FY（FY2025→FY2027）", 1, 1, 4, 0),
    ("CMP-HORIZON-h1FY", "horizon=h1FY（FY2026→FY2027）", 1, 1, 3, 0),
    ("CMP-MARKET-H", "market=H（小米，已排除）", 0, 0, 0, 0),
]

UNCOVERED = [
    {"stratum": "market=H", "state": "unproven", "reason": "小米按设计字段 3 排除（gap-U1 证据不可读 / gap-U2 披露日未登记）；exclusions.jsonl EX-001"},
    {"stratum": "industry=unassigned", "state": "unproven", "reason": "设计字段 3 未给出行业取值 ⇒ 分层键留空"},
    {"stratum": "lifecycle=unassigned", "state": "unproven", "reason": "设计字段 3/7 未给出生命周期取值"},
    {"stratum": "disclosure_quality=US-MSFT PBP/IC", "state": "unproven", "reason": "MS-PBP-M05 / MS-IC-M06 = partial_STOP_DISCLOSURE_ADAPTATION（signed=false）"},
    {"stratum": "disclosure_quality=CN-ZIJIN TRADE/OTHER + US-MSFT MPC", "state": "unproven", "reason": "无披露适配 case（未覆盖），不得记为通过"},
    {"stratum": "model_version=unbound", "state": "unproven", "reason": "params_released=false ⇒ forecast_values_frozen=0，无模型版本可评"},
    {"stratum": "dataset=single_frame_3_entities", "state": "unproven", "reason": "仅本审计三家公司；可评 entity=2，不外推到其他数据集/市场"},
]

TAXONOMY = {
    "data": [
        {"id": "u-N4", "item": "US-MSFT-10K-FY2026 sha 转录层 63 位 vs 实测 64 位（缺尾位）", "source_ref": "I-07-E §D1（u-N4）+ I-11-A source_map.json / store"},
        {"id": "gap-U1", "item": "HK-XIAOMI-AR2025 原文在本回源面不可读（STOP_EVIDENCE，不引用任何值）", "source_ref": "I-11-A source_map.json not_readable_in_this_attempt"},
    ],
    "definition": [
        {"id": "u-N5", "item": "store H-01 original_value 与矿产品分部语义张力（差额法 vs 分部合计口径）", "source_ref": "I-07-E §D1（u-N5）/ unverified-N1"},
        {"id": "E5-elim", "item": "含内部交易的分部总计不得作收入基期（否则高估约 67%）⇒ 统一用对外销售收入口径", "source_ref": "I-07-E §C4 / 设计字段 6 gross_net"},
        {"id": "H4-residual", "item": "H4 口径桥残差闭合不了（含内外翻转），整改未完", "source_ref": "OWNER_DECISIONS §三十六 + I-07-E §B3 EA-1 blocked_by_residuals=OPEN-6"},
    ],
    "driver": [
        {"id": "OPEN-2", "item": "单位收入参数转换公式分母不自洽（差约 3.25×/3.26×）⇒ 数值只登记不消费，具体数值见本卡 oracle §4 红线登记，不在本件复制", "source_ref": "REMEDIATION_REGISTER.md L3951（转引 I-07-E §F）"},
        {"id": "u-N6", "item": "EA-4 增速带换算注记区间与自身带换算结果不符", "source_ref": "I-07-E §D1（u-N6）/ unverified-N3"},
    ],
    "timing": [
        {"id": "gap-U2", "item": "披露日未在回源面登记 ⇒ available_at<=origin 无法验证（fail-closed 不入池）", "source_ref": "I-07-E §A gap-U2 / 设计字段 4"},
        {"id": "unseal", "item": "解封门 0/4 满足 + 目标期 FY2027 未结束 ⇒ 实际值不可得，评分时点未到", "source_ref": "I-12-A design_manifest.unseal_gate + I-12-B actuals_policy_application"},
    ],
    "structure": [
        {"id": "dup-row", "item": "合并行与分部行同 origin×horizon 会双计权 ⇒ 误差池只计分部层", "source_ref": "设计字段 2 duplicate_rule / I-12-B exclusions EX-002/EX-003"},
        {"id": "E6-prohibited", "item": "Microsoft Cloud 聚合不得与 IC 分部并列（PROHIBITED_CO_USE）", "source_ref": "I-07-E §C3 E6"},
    ],
    "random": [
        {"id": "n0-random", "item": "可评分样本 n=0 ⇒ 随机成分不可估；有观测后须按 origin block（非观测独立）估计", "source_ref": "I-12-D paired_comparison.json + 设计字段 11 structure_frozen"},
        {"id": "repeat-year", "item": "重复年度不是独立公司 ⇒ cluster=entity / block=origin，否则会低估不确定性", "source_ref": "卡文动作 3 逐字 + 设计字段 11"},
    ],
}

FOLLOW_UP = [
    "双签落地且 design_manifest 新版本重冻后：字段 10/11/12 的具体阈值（最小样本量、CI 宽度、α、重抽样次数、种子、多重比较校正、经济显著改善幅度）应如何取？",
    "gap-U1（小米原文可读性）与 gap-U2（披露日登记）如何解除，才可让 market=H 层进入评估池而不补假数据？",
    "紫金贸易/其他分部与微软 MPC 缺披露适配 case：是否补建 case 并由行业/会计 reviewer 签署？",
    "secondary baseline「同比延续」跨 h 年的复利读法是否采认（影响 skill 分母口径）？",
    "US-MSFT sha 63/64 转录差异（u-N4）由谁裁决、以哪一版为权威？",
    "目标期 FY2027 结束后：实际值由独立 reviewer 收集封存、出具 unblind_receipt 的时序与一次性解封规则如何落地？",
]


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    os.makedirs(EV, exist_ok=True)

    comparisons = []
    for cid, stratum, nc, no, nreg, nsc in COMPARISONS:
        comparisons.append({
            "comparison_id": cid,
            "pre_registered": True,
            "primary_endpoint": "SKILL_WAPE_VS_NAIVE_BASELINE（设计字段 1）",
            "stratum": stratum,
            "n_companies": nc,
            "n_origins": no,
            "n_registered_samples": nreg,
            "n_scorable": nsc,
            "observed_skill": None,
            "observed_wape": None,
            "threshold_applied": None,
            "threshold_state": "unsigned",
            "verdict": "inconclusive",
            "verdict_reason": [
                "冻结阈值未在结果前批准（professional_approval 双签 unsigned；6 项关键阈值 PENDING）",
                "全量结果不可见（scorable_samples=0；forecast_values_frozen=0；unblind_receipt=not_issued；test_results_unsealed=false）"
            ],
            "verdict_is_fail_closed_default_not_professional_determination": True,
            "judge_authority": "统计reviewer + 行业reviewer（not_assigned）",
            "negative_skill_rule": "负 skill 一旦产生不得删除、不得因难看而剔除（设计字段 1 / metric_definitions）",
            "failed_strata_rule": "失败层保留原样、不并入其他层、不静默丢弃（卡文动作 1 逐字）",
        })

    qual = {
        "schema": "i12e_accuracy_qualification/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "premise": {
            "card_verbatim": "冻结阈值已在结果前批准；全量结果可见。",
            "thresholds_approved_before_results": False,
            "all_results_visible": False,
            "checks": [
                {"item": "冻结阈值已在结果前批准", "met": False,
                 "evidence": "I-12-A professional_approval.json：statistical_reviewer/industry_reviewer 双双 unsigned；unsigned_key_statistical_options 6 项全 PENDING（派单记「双签在飞」）"},
                {"item": "全量结果可见", "met": False,
                 "evidence": "I-12-D metrics_by_stratum scorable_samples=0 / paired_comparison n_pairs=0；I-12-C forecast_values_frozen=0；I-12-C unblind_receipt state=not_issued；test_results_unsealed=false"}
            ],
            "met_count": "0/2",
            "consequence": "前提未满足 ⇒ 本卡不作 supported/unsupported 判定；全部比较按 fail-closed 记 inconclusive（默认登记，非专业判定），整卡判 blocked（合格形态）",
        },
        "primary_endpoint": {"id": "SKILL_WAPE_VS_NAIVE_BASELINE", "ref": "evaluation_design fields[1]（frozen）",
                             "direction": "Skill>0 = 优于朴素 baseline；负 skill 不得删除"},
        "threshold_state": "unsigned",
        "thresholds_unsigned": THRESHOLDS_UNSIGNED,
        "anti_cherry_pick_rule": "任何阈值在结果解封后补写 ⇒ 该次评估作废为探索性（exploratory），不得作确认性成功（设计字段 12 逐字）",
        "comparisons": comparisons,
        "comparison_counts": {"pre_registered": len(comparisons),
                              "supported": 0, "unsupported": 0, "inconclusive": len(comparisons)},
        "judge_authority": {"roles": ["统计reviewer", "行业reviewer"], "assigned": False,
                            "signature_status": "unsigned",
                            "implementer_did_not_determine": True,
                            "note": "实现者不自签（§三十四 L765）；本件为登记，不是专业判定、不产生 ACCEPT"},
        "negative_and_failed_preservation": {
            "negative_skill_preserved_rule": True,
            "failed_strata_preserved_rule": True,
            "observed_negative_skills": [],
            "observed_negative_skill_note": "n=0 ⇒ 本 attempt 无 skill 观测；规则先冻结，有值后照此执行",
        },
        "scope_limitation": {
            "dataset": "本审计三家公司（紫金矿业 CN A+H / 小米集团 HK / 微软 US）；可评 entity=2",
            "model_version": "unbound（params_released=false，forecast_values_frozen=0）",
            "industry": "unproven（设计字段 3 未赋值）",
            "lifecycle": "unproven（设计字段 3/7 未赋值）",
            "disclosure_quality": "4 case signed / 2 case STOP_DISCLOSURE_ADAPTATION / 3 段无 case（disclosure_adaptation_v2）",
            "horizon": "FY2027（h2FY 紫金 / h1FY 微软）；不与其它 horizon 混成单一平均",
            "no_generalization": "结论不外推到未列数据集、模型版本、行业、生命周期、披露质量或 horizon"
        },
        "uncovered_strata": UNCOVERED,
        "three_column": {
            "presentation": "三栏合并呈现（卡文动作 3）",
            "no_cross_column_pass_override": True,
            "formula_qualification": {
                "column_state": "pass_scoped",
                "value": "M01-M31 = accepted_scoped（仅 A–C 公式面，调度验收）",
                "source_ref": "disclosure_adaptation_v2 每 case formula.status + I-07-E §E + common_research_cards.md L11",
                "does_not_imply": ["disclosure_adaptation", "accuracy"],
                "formula_pass_does_not_imply_accuracy": True,
            },
            "disclosure_adaptation": {
                "column_state": "partial",
                "value": "4 signed（ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03）+ 2 STOP（MS-PBP-M05 / MS-IC-M06）+ 3 段无 case",
                "source_ref": "execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json",
                "does_not_imply": ["accuracy"],
                "disclosure_signing_does_not_imply_accuracy": True,
            },
            "accuracy": {
                "column_state": "unproven",
                "state": "unproven",
                "value": "未评估：0 可评分样本 + 阈值未签 + 结果封存",
                "source_ref": "I-12-D metrics_by_stratum/paired_comparison + I-12-A unseal gate",
            },
            "accuracy_improvement_claimed": False,
            "override_examples_forbidden": [
                "不得因公式栏 pass_scoped 而把准确性栏写成 pass",
                "不得因 4 例披露签署而把准确性栏写成 pass",
                "不得因少数公司拟合而写成准确率提升"
            ],
        },
        "stops": {
            "STOP_CLAIM": {
                "rule_verbatim": "把31公式通过或少数公司拟合直接称准确率提升→STOP_CLAIM。",
                "triggered": False,
                "basis": "本件 accuracy 栏=unproven、accuracy_improvement_claimed=false、无任何 supported 判定；变异 Q3 可验证本判据"
            },
            "STOP_RELEASE_WORDING": {
                "rule_verbatim": "没有达到统计判定条件却宣称普遍有效→STOP_RELEASE_WORDING。",
                "triggered": False,
                "basis": "未产生任何普遍有效/发布措辞；发布格=blocked；scope_limitation.no_generalization 在位"
            },
        },
        "counts": {"comparisons": len(comparisons), "supported": 0, "unsupported": 0,
                   "inconclusive": len(comparisons), "uncovered_strata": len(UNCOVERED),
                   "scorable_samples": 0, "accuracy_improvement_claimed": False},
        "declarations": {"params_released": False, "implementer_signed": False,
                         "releases_nothing": True, "open2_ban_observed": True,
                         "produces_ACCEPT": False, "verdict_authority": "not_the_implementer"},
    }
    write_json(os.path.join(EV, "accuracy_qualification.json"), qual)

    taxonomy = {
        "schema": "i12e_error_taxonomy/1",
        "card": CARD,
        "attempt": ATTEMPT,
        "role": ROLE,
        "categories": TAXONOMY,
        "category_ids": ["data", "definition", "driver", "timing", "structure", "random"],
        "category_source_verbatim": "记录误差来源为数据/定义/驱动/时点/结构/随机（卡文动作 4 逐字）",
        "follow_up_questions": FOLLOW_UP,
        "forecast_fixed_this_round": False,
        "no_prediction_changes": True,
        "no_prediction_changes_note": "不在本轮评分中修预测（卡文动作 4 逐字）；本件只登记来源与后续问题",
        "counts": {"categories": len(TAXONOMY),
                   "items": sum(len(v) for v in TAXONOMY.values()),
                   "follow_up_questions": len(FOLLOW_UP)},
        "declarations": {"params_released": False, "implementer_signed": False, "open2_ban_observed": True},
    }
    write_json(os.path.join(EV, "error_taxonomy.json"), taxonomy)

    limitations = """# I-12-E 局限与覆盖登记（limitations）

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
"""
    with open(os.path.join(EV, "limitations.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(limitations)

    review = """# I-12-E 独立统计复审件（状态登记，非签署）

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
"""
    with open(os.path.join(EV, "independent_statistical_review.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(review)

    print("accuracy_qualification comparisons=%d inconclusive=%d uncovered=%d"
          % (len(comparisons), len(comparisons), len(UNCOVERED)))
    print("error_taxonomy categories=%d items=%d questions=%d"
          % (len(TAXONOMY), sum(len(v) for v in TAXONOMY.values()), len(FOLLOW_UP)))
    print("limitations.md + independent_statistical_review.md written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
