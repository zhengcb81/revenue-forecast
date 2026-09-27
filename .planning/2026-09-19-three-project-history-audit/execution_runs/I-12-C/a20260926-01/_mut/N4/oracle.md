# I-12-C oracle（运行前冻结）· execution_runs/I-12-C/a20260926-01

> 卡：`execution_v2/card_I-12-C.md`（1,604 B / sha `49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91`）
> 冻结时间：2026-09-26T21:0x+01:00 · role：`implementer_i12c` · 本件先于任何证据写入冻结，冻结后不改。
> 性质：实现者工作记录；**不自签、不产生 ACCEPT、不代出 unblind_receipt、不放行任何参数**。

---

## 1. 卡文逐字（唯一判据）

**卡头（L5）**：`Parent：I-12；状态：planned；Owner：执行者按设计运行；独立reviewer保管实际值；依赖：I-12-B。`

**前提（L9-L10）**：样本和设计已冻结，对应模型至少公式资格通过，所用真实映射有披露资格。

**动作（L13-L16，逐字）**：
1. 同一sample只使用origin以前资料构造驱动；保存模型、配置、参数、source manifest hash及运行日志。
2. 按冻结规则产生各baseline；baseline缺必需历史期就标not_applicable，不用未来资料补齐。
3. 在读取实际值前冻结forecast、low/base/high语义、预测时间、版本和hash；重跑必须有原因且保留旧版本。
4. 解封实际值后只做评分，不再调参；需调参进入新训练轮并使用未见过的测试集。

**停止（L19-L21，逐字）**：
- 预测冻结晚于读取实际值→该样本只能exploratory。
- 模型披露映射未通过→STOP_MODEL_ADAPTATION；不阻止其他已合格模型继续。

**验收（L23）**：每个可评分样本有冻结预测和公平基线；没有真实历史vintage的样本清晰分组。

**证据（L25，逐字）**：`evidence/I-12-C/forecast_vintages.jsonl`、`evidence/I-12-C/baseline_vintages.jsonl`、`evidence/I-12-C/forecast_manifest.json`、`evidence/I-12-C/run_logs.json`、`evidence/I-12-C/unblind_receipt.json`。

**研究卡原文（research_cards.json L582-L615，补充第 5 步）**：
- step4「解封实际值后只做评分，不再调参；需调参进入新训练轮并使用未见过的测试集。」
- step5「独立reviewer核验设计与预测manifest已冻结后才出具unblind_receipt并提供实际值；如发现资料未来信息无法排除，降为exploratory，保留原日志。」
- 验收「每个可评分样本有冻结预测和公平基线；没有真实历史vintage的样本清晰分组。」

**封存规则逐字（common_research_cards.md L289）**：「I-12-C冻结预测manifest后才由该reviewer出具unblind_receipt解封。已见实际值或重建资料含无法排除的未来信息，一律标exploratory，不能伪装真实vintage或确认性盲测。」

---

## 2. 上游冻结输入（本卡运行前实测 sha256；校验器逐件复算）

| # | 路径（相对计划根） | 字节 | sha256 |
|---|---|---|---|
| U1 | `execution_v2/card_I-12-C.md` | 1604 | `49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91` |
| U2 | `execution_v2/card_I-12-B.md`（本批上游卡文） | 1549 | `f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b` |
| U3 | `execution_v2/research_cards.json` | 40058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` |
| U4 | `execution_v2/common_research_cards.md` | 14736 | `2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b` |
| U5 | `execution_v2/START_HERE.md` | 20436 | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` |
| U6 | `execution_v2/review_and_handoff.md` | 4005 | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| U7 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` |
| U8 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json` | 22317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` |
| U9 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json` | 5334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` |
| U10 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json` | 5618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` |
| U11 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/sample_manifest.jsonl`（本批上游样本表） | 11085 | `679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702` |
| U12 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/exclusions.jsonl` | 3060 | `a4940267efc9683793baef0f52668e93b657c8c6ccd756b6349224e5275d3e93` |
| U13 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/source_vintages.jsonl` | 4741 | `9f9d263f535e5bf3b421f2e0242eb853012708a243503edd4e64daf1529b6e56` |
| U14 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/actuals_policy_application.json` | 7916 | `998823537e8f493545562a05b1e0308f1865b0231ddb44b1bfc9fee5a7ac3942` |
| U15 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/split_manifest.json` | 1776 | `3a42cc85ce71ec4eb9aa5595948237e7ea3d62fdc6d3844c2e7bab05d11eddb7` |
| U16 | `execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json`（披露适配签署面） | 66887 | `373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522` |
| U17 | `execution_runs/I-10-A/a20260923-01/evidence/I-10-A/disclosure_qualification.json`（前像，仅对照） | 8603 | `6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb` |
| U18 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` |
| U19 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json` | 13863 | `3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf` |
| U20 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘，只读**） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| U21 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` |

**上游状态读取**：
- I-12-A = `accepted_scoped`（2026-09-26 20:4x）；`unseal_gate.currently_satisfied=false`、`test_results_unsealed=false`；双签在飞（professional_approval 双双 `unsigned`）。
- I-12-B = 本批刚落，`status=review_pending`（**未验收**）；7 样本 / 0 可评分 / `limited`。
- 披露适配（U16，v2 2026-09-25）：`ZJ-MIN-M09`、`ZJ-SMT-M09`、`XM-PHONE-M03`、`XM-EV-M03` = `mapped/signed=true`；`MS-PBP-M05`、`MS-IC-M06` = `unmapped/partial_STOP_DISCLOSURE_ADAPTATION/signed=false`；紫金贸易/其他、微软 MPC 无 case（未覆盖）。
- 公式资格：M01–M31 = `accepted_scoped`（仅 A–C 公式面，**不外推到披露适配或准确性**）。
- 参数：`params_released=false`；store `low/base/high` 全 null、两个 `_PLACEHOLDER` 在位。

---

## 3. 授权逐字

- **§三十四（L745-L780）**：硬约束「oracle 先冻结」「不放行任何参数」「不触发任何 falsifier/自动动作」「实现者不自签 · 独立复审 · 落定走三件套」；边界「不解除 OPEN-2/3/5/6」「不放行参数（两个 _PLACEHOLDER + MSFT 四参数 + 新两分部参数）」「不产生 ACCEPT、不改任何 status/decision/decision_sha256（除非是新卡自己的写入面）」「不代签行业面 / 会计面 / 外部方」。
- **§三十七（L852-L871）**：「给你授权所有的沙箱操作，不要再问我了」；边界「纪律 16/17/18/19/20 全部继续有效」「生产零未授权改动」「产品仓提交不在本授权内」。本卡使用面 = 零提权；禁 git（含 `git status`）、禁联网。
- **派单（2026-09-26）**：顺序 B→C→D→E；每卡先冻结 oracle + 门 0；红绿变异 ≥3；fail-closed 数据/历史期不足 ⇒ `not_applicable` 或 STOP 判 `blocked`（合格）。

---

## 4. 红线（只登记、不消费）

- `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE`：登记值 **124,248.63**（真值 38,175.95）；「OPEN-2 前禁消费」。
- 本卡处置：`registered_not_consumed`；`evidence/I-12-C/**` **禁止出现该两个字面量**（K5 具名检查）；本 oracle 仅登记。

---

## 5. 判据 K（校验器 `_verify.py`；全绿 rc=0，违例 rc=3，缺件/坏 JSON rc=1）

| id | 判据 |
|---|---|
| K1 | `forecast_vintages.jsonl` 恰 7 行（对齐 U11 的 7 个 sample_id）；`forecast.low/base/high` 全为 `null`；`forecast_value_state` = `not_produced_params_not_released`；`model_version=null`；`reason` 必含 `params_released=false`。 |
| K2 | `baseline_vintages.jsonl` 恰 14 行（7 primary + 7 secondary）；每个 sample_id 各 1 primary、1 secondary；primary 值 = 冻结设计字段 8 的「最后可得同口径年度值」（紫金 FY2025 四分部、微软 FY2026 三分部，均为 origin 前已披露值）；secondary 为有理数（分子/分母）+ 十进制；**全部行 `value_state` 不得是 released parameter**；每行 `available_at<=origin=true`；`seasonal_same_quarter` 在 manifest 内标 `not_applicable`。 |
| K3 | `forecast_manifest.json`：`freeze_before_unblind=true`、`actuals_read_by_this_station=false`、`low_high_semantics="scenario_band_not_probabilistic"`、`version="v1"`、`reruns=0`、`input_hashes`（两个 jsonl）与现场复算一致、`disclosure_qualification_counts` = {signed:2, stop:2, uncovered:3}。 |
| K4 | `unblind_receipt.json`：`issued=false`、`issued_by=null`、`issued_by_role=independent_reviewer`、`this_station_cannot_issue=true`、`preconditions_unmet` ≥4 项、`scorable_samples=0`。 |
| K5 | `evidence/I-12-C/**` 无 `124248.63`/`124,248.63`/`38175.95`；`params_released=false`、`implementer_signed=false`、`open2_ban_observed=true`（handoff 与 manifest 双处）。 |
| K6 | 上游一致性：U1-U21 现场复算 sha 全等。 |
| K7 | 封盘/store 零字节（U20 = `f2178768…`/51,697 B；U21 = `b2063ac8…`/61,231 B）。 |
| K8 | `run_logs.json`：`model_runs=[]` 且带原因；`commands` 全部落在本 attempt 目录；`network_used=false`、`git_used=false`。 |
| K9 | handoff 形态：`status=review_pending`、`gate0_passed=true`、`releases_nothing=true`、`git_diff_non_planning=0`、`written_files` 覆盖五件证据。 |

**rc 码表（本卡自描述）**：`0`=全 K 通过；`1`=harness 失败；`2`=无裁决（未用）；`3`=具名 K 违例。

---

## 6. 变异清单（红臂；`_mut/<id>` 副本，原件字节不动）

| id | 变异 | 期望 |
|---|---|---|
| N1 | 给某样本写入 `forecast.base = 123456`（未放行参数却出数） | rc=3（K1） |
| N2 | 把紫金矿产品 primary baseline 改掉（+1 元） | rc=3（K2） |
| N3 | `unblind_receipt.issued=true`、`issued_by="implementer_i12c"`（自出解封回执） | rc=3（K4） |
| N4 | `forecast_manifest.freeze_before_unblind=false`（冻结晚于读实际值） | rc=3（K3） |
| N5 | evidence 内写入红线字面量 `124248.63` | rc=3（K5） |
| 绿臂 | 原件 | rc=0 |

---

## 7. 门 0 原始输出（先于证据写入执行）

```text
=== GATE0 BEGIN (I-12-C/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-C\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-C a20260926-01 write-readback-delete 2026-09-26T21:04:49+01:00
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
--- step6 upstream B (this batch, prior card) ---
I-12-B_sample_manifest_sha256=679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702
I-12-B_sample_manifest_bytes=11085
=== GATE0 END ===
```

---

## 8. fail-closed 预期（写证据前声明）

1. **预测值 = 0 条**：`params_released=false`（§三十四 硬约束 + store low/base/high 全 null + 两 `_PLACEHOLDER` 在位），且本卡无 I-00-B 绑定的可运行命令（`binding_status=unbound` ⇒ START_HERE「命令不能猜」）⇒ 不产出任何数值预测；`forecast_vintages` 7 行全部 `null` + 原因。**这不是缺陷绕过，是授权边界**。
2. **基线照产**：字段 8 冻结规则（naive level persistence / YoY carried forward）作用于 origin 前已披露值，输出是规则计算结果、**不是被放行参数**（`value_state` 逐行声明）。缺历史期者标 `not_applicable`（季节性同季 baseline：本审计为年度序列 ⇒ `not_applicable`，其 not_applicable 获批仍归 reviewer）。
3. **解封回执不由本工位出**：`unblind_receipt.issued=false`，出具权 = 独立 reviewer；前置四条件（双签 + 13 字段完成 + manifest 重冻 + 编排层明文解封）当前 0/4 满足。
4. **STOP_MODEL_ADAPTATION 按段登记**：`MS-PBP-M05`/`MS-IC-M06` = `partial_STOP_DISCLOSURE_ADAPTATION` ⇒ 该两段触发（逐字「不阻止其他已合格模型继续」）；紫金矿产品/冶炼 2 段 signed；紫金贸易/其他、微软 MPC = 无 case 未覆盖（另码登记，不混同「通过」）。
5. **可评分样本 = 0**：目标期 FY2027 未结束 + 未解封 ⇒ 卡文验收在本 attempt 不可达成 ⇒ fail-closed 判 `blocked`（合格形态）。
6. **不读测试/准确性结果**：本卡读面 = 卡文 + 上游 I-12-A/B/C/D/E 相关件 + 披露适配 + I-07-E/I-11 转录；不读任何回测/准确性产出。
