# I-12-E oracle（运行前冻结）· execution_runs/I-12-E/a20260926-01

> 卡：`execution_v2/card_I-12-E.md`（1,469 B / sha `3c7d6da514dc9897bd7575a2e8e883bd9f883be89d1bdda6075d23a7f1ed497b`）
> 冻结时间：2026-09-26T21:2x+01:00 · role：`implementer_i12e` · 本件先于任何证据写入冻结，冻结后不改。
> 性质：实现者工作记录；**不自签、不产生 ACCEPT、不改预测、不发发布措辞**。

---

## 1. 卡文逐字（唯一判据）

**卡头（L5）**：`Parent：I-12；状态：planned；Owner：统计与行业reviewer；依赖：I-12-D。`

**前提（L9-L10）**：冻结阈值已在结果前批准；全量结果可见。

**动作（L13-L16，逐字）**：
1. 对每个预注册主要比较按冻结阈值判supported/unsupported/inconclusive，保留负skill和失败层。
2. 把结果限定到数据集、模型版本、行业、生命周期、披露质量与horizon；未覆盖分层标unproven。
3. 把公式资格、披露适配和准确性三栏合并呈现，但禁止一栏PASS覆盖另一栏不足。
4. 记录误差来源为数据/定义/驱动/时点/结构/随机，生成后续研究问题；不在本轮评分中修预测。

**停止（L19-L21，逐字）**：
- 把31公式通过或少数公司拟合直接称准确率提升→STOP_CLAIM。
- 没有达到统计判定条件却宣称普遍有效→STOP_RELEASE_WORDING。

**验收（L23）**：结论与预先规则一致；无覆盖领域、负结果和不确定性显式保留。

**证据（L25，逐字 4 件）**：`evidence/I-12-E/accuracy_qualification.json`、`evidence/I-12-E/limitations.md`、`evidence/I-12-E/error_taxonomy.json`、`evidence/I-12-E/independent_statistical_review.md`。

**研究卡原文（research_cards.json L667-L706）**：`owner_role` = 统计与行业 reviewer；`preconditions` = 「冻结阈值已在结果前批准；全量结果可见。」；动作/停止/验收与卡文一致。

---

## 2. 上游冻结输入（运行前实测 sha256；校验器逐件复算）

| # | 路径 | 字节 | sha256 |
|---|---|---|---|
| U1 | `execution_v2/card_I-12-E.md` | 1469 | `3c7d6da514dc9897bd7575a2e8e883bd9f883be89d1bdda6075d23a7f1ed497b` |
| U2 | `execution_v2/card_I-12-D.md` | 1776 | `c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69` |
| U3 | `execution_v2/research_cards.json` | 40058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` |
| U4 | `execution_v2/common_research_cards.md` | 14736 | `2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b` |
| U5 | `execution_v2/START_HERE.md` | 20436 | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` |
| U6 | `execution_v2/review_and_handoff.md` | 4005 | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| U7 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` |
| U8 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json` | 22317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` |
| U9 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json` | 5334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` |
| U10 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json` | 5618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` |
| U11 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/sample_manifest.jsonl` | 11085 | `679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702` |
| U12 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/exclusions.jsonl` | 3060 | `a4940267efc9683793baef0f52668e93b657c8c6ccd756b6349224e5275d3e93` |
| U13 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_manifest.json` | 5467 | `03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a` |
| U14 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/unblind_receipt.json` | 1968 | `99ed0139434a2777f4ede1454782fb83c60f315c3d83e00e1c8b175324e991f1` |
| U15 | `execution_runs/I-12-D/a20260926-01/evidence/I-12-D/metric_oracle_result.json` | 8415 | `0d64d62e0f60df0a253bea58b9cb0841b0377198631cccdc7a0109e7366e83ca` |
| U16 | `execution_runs/I-12-D/a20260926-01/evidence/I-12-D/metrics_by_stratum.json` | 12085 | `ad14f515bcb4f796bf063957a5a005f26b08babea312b94a6367de98b3392e2e` |
| U17 | `execution_runs/I-12-D/a20260926-01/evidence/I-12-D/paired_comparison.json` | 1961 | `5709203bac2753c37fe6c56853f4f6d875d5149a1fd56edc993f275ce6e2e0d5` |
| U18 | `execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json` | 66887 | `373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522` |
| U19 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` |
| U20 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘，只读**） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| U21 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` |

### 前提核验（卡文 L9-L10，写证据前先判）

| 前提 | 状态 | 证据 |
|---|---|---|
| 冻结阈值已在结果前批准 | **不满足** | U9 `professional_approval`：statistical/industry reviewer 双双 `unsigned`；6 项关键统计选项/阈值全 `PENDING`（派单记「双签在飞」）；U8 字段 10/11阈值/12 = PENDING/unsigned |
| 全量结果可见 | **不满足** | U16 `scorable_samples=0`、`state=descriptive_only`；U17 `n_pairs=0`；U13 `forecast_values_frozen=0`；U14 `unblind_receipt state=not_issued`；`test_results_unsealed=false` |

⇒ **前提 0/2 满足** ⇒ 本卡**不得**给出 `supported`/`unsupported` 判定（那需要冻结阈值与结果）；按 fail-closed 全部记 `inconclusive` 并**显式声明这是默认登记、不是专业判定**，整卡判 `blocked`（合格形态），裁定权归统计与行业 reviewer。

---

## 3. 授权逐字

- **§三十四（L745-L780）**：「oracle 先冻结」「不放行任何参数」「不触发任何 falsifier/自动动作」「实现者不自签 · 独立复审 · 落定走三件套」；边界「不解除 OPEN-2/3/5/6」「不产生 ACCEPT、不改任何 status/decision/decision_sha256（除非是新卡自己的写入面）」「不代签行业面 / 会计面 / 外部方」。
- **§三十七（L852-L871）**：「给你授权所有的沙箱操作，不要再问我了」；边界「纪律 16/17/18/19/20 全部继续有效」「生产零未授权改动」「产品仓提交不在本授权内」。本卡零提权；禁 git（含 `git status`）、禁联网。
- **派单（2026-09-26）**：E 卡要点「按冻结阈值判 supported/unsupported/inconclusive（保负 skill 与失败层）· 限定分层（未覆盖标 unproven）· 三栏合并但禁一栏 PASS 盖另一栏」；fail-closed 数据/历史期不足 ⇒ `not_applicable` 或 STOP 判 `blocked`（合格）。

---

## 4. 红线（只登记、不消费）

`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 登记值 **124,248.63**（真值 38,175.95），「OPEN-2 前禁消费」。`evidence/I-12-E/**` 禁止出现该两个字面量（E7 具名检查）；oracle 仅登记。

---

## 5. 判据 E（校验器 `_verify.py`；全绿 rc=0，违例 rc=3，缺件/坏 JSON rc=1）

| id | 判据 |
|---|---|
| E1 | `accuracy_qualification.json`：`premise.thresholds_approved_before_results=false`、`premise.all_results_visible=false`、`premise.met=0/2`；每个预注册比较 `verdict` ∈ {`inconclusive`}（**不得出现 supported/unsupported**）；`threshold_state=unsigned`；`verdict_is_fail_closed_default_not_professional_determination=true`；`judge_authority` = 统计与行业 reviewer（`not_assigned`）；`negative_skill_preserved_rule=true`；`failed_strata_preserved=true`。 |
| E2 | 范围限定六键齐全（`dataset`/`model_version`/`industry`/`lifecycle`/`disclosure_quality`/`horizon`）；`uncovered_strata` 至少含 market=H、industry、lifecycle 三项且逐项 `state=unproven`；无任何分层被标 `proven`。 |
| E3 | 三栏：`formula_qualification`、`disclosure_adaptation`、`accuracy` 三键齐全；`no_cross_column_pass_override=true`；`accuracy.state=unproven`；`accuracy_improvement_claimed=false`；`formula_pass_does_not_imply_accuracy=true`；`disclosure_signing_does_not_imply_accuracy=true`。 |
| E4 | `error_taxonomy.json`：六类（`data/definition/driver/timing/structure/random`）齐全且各有 ≥1 条登记项；`follow_up_questions` ≥3 条；`forecast_fixed_this_round=false`；每条登记项带 `source_ref`。 |
| E5 | `limitations.md`：含 `unproven`、`inconclusive`、`descriptive_only`、`STOP_CLAIM`、`STOP_RELEASE_WORDING`、覆盖缺口（小米/行业/生命周期/微软分部）、负结果与不确定性保留、n=0 事实；且**不得**出现「准确率提升」「accuracy improved」式结论。 |
| E6 | `independent_statistical_review.md`：`reviewer_assigned=false`、`signed=false`、`implementer_signed=false`、`verdict_issued=false`；含「未签署/unsigned」字样；声明本件为状态登记、不是签署、不构成 ACCEPT。 |
| E7 | `evidence/I-12-E/**` 无 `124248.63`/`124,248.63`/`38175.95`；handoff `params_released=false`、`implementer_signed=false`、`open2_ban_observed=true`。 |
| E8 | 上游一致性：U1-U21 现场复算 sha 全等。 |
| E9 | 封盘/store 零字节（U20 = `f2178768…`/51,697 B；U21 = `b2063ac8…`/61,231 B）。 |
| E10 | handoff 形态：`status=review_pending`、`gate0_passed=true`、`releases_nothing=true`、`git_diff_non_planning=0`、`written_files` 覆盖 4 件证据。 |

**rc 码表（本卡自描述）**：`0`=全 E 通过；`1`=harness 失败；`2`=无裁决（未用）；`3`=具名 E 违例。

---

## 6. 变异清单（红臂；`_mut/<id>` 副本，原件字节不动）

| id | 变异 | 期望 |
|---|---|---|
| Q1 | 把某比较的 `verdict` 改成 `supported`（阈值未签却下判定） | rc=3（E1） |
| Q2 | `no_cross_column_pass_override=false` 且把 `accuracy.state` 改成 `pass`（一栏 PASS 盖另一栏） | rc=3（E3） |
| Q3 | `accuracy_improvement_claimed=true`（把 31 公式通过说成准确率提升） | rc=3（E3/E5） |
| Q4 | evidence 写入红线字面量 `124248.63` | rc=3（E7） |
| Q5 | `error_taxonomy` 删掉 `random` 类并清空 `follow_up_questions` | rc=3（E4） |
| 绿臂 | 原件 | rc=0 |

---

## 7. 门 0 原始输出（先于证据写入执行）

```text
=== GATE0 BEGIN (I-12-E/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-E\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-E a20260926-01 write-readback-delete 2026-09-26T21:22:34+01:00
readback_match=True
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
sealed_bytes=51697
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
store_matches_b2063ac8=True
store_bytes=61231
--- step6 upstream B/C/D evidence (this batch) ---
sample_manifest.jsonl sha256=679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702 bytes=11085
forecast_manifest.json sha256=03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a bytes=5467
metric_oracle_result.json sha256=0d64d62e0f60df0a253bea58b9cb0841b0377198631cccdc7a0109e7366e83ca bytes=8415
metrics_by_stratum.json sha256=ad14f515bcb4f796bf063957a5a005f26b08babea312b94a6367de98b3392e2e bytes=12085
paired_comparison.json sha256=5709203bac2753c37fe6c56853f4f6d875d5149a1fd56edc993f275ce6e2e0d5 bytes=1961
--- step7 design thresholds state (read-only) ---
professional_approval.json sha256=0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1
threshold_signatures=statistical_reviewer unsigned; industry_reviewer unsigned; 6 key statistical options PENDING
=== GATE0 END ===
```

---

## 8. fail-closed 预期（写证据前声明）

1. **判定档位只用 `inconclusive`**：冻结阈值未批准（0/2 前提）⇒ 任何 `supported`/`unsupported` 都会违反「按冻结阈值判」；`inconclusive` 是**默认登记**，不是专业判定，须由统计与行业 reviewer 复核后改档。
2. **负 skill 与失败层保留规则照登**：本 attempt 无 skill 可算（n=0），保留规则以字段形式冻结；一旦有值，负 skill 不得删除、失败层不得合并。
3. **未覆盖分层标 unproven**：market=H（小米被排除）、industry/lifecycle（设计未赋值）、微软 PBP/IC（STOP_DISCLOSURE_ADAPTATION）、紫金贸易/其他与微软 MPC（无 case）逐项登记。
4. **三栏独立**：公式栏（M01–M31 accepted_scoped，仅公式面）/ 披露栏（4 signed + 2 STOP + 3 uncovered）/ 准确性栏（`unproven`）—— 任一栏的 PASS **不得**外溢；`no_cross_column_pass_override=true` 由校验器强制。
5. **不修预测**：本轮只登记误差来源与后续研究问题，`forecast_fixed_this_round=false`。
6. **不读测试/准确性结果**：读面 = 卡文 + 研究卡 + I-12-A/B/C/D 本批登记件 + 披露适配 + I-07-E 汇总。
