# I-12-D oracle（运行前冻结）· execution_runs/I-12-D/a20260926-01

> 卡：`execution_v2/card_I-12-D.md`（1,776 B / sha `c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69`）
> 冻结时间：2026-09-26T21:1x+01:00 · role：`implementer_i12d` · 本件先于任何证据写入冻结，冻结后不改。
> 性质：实现者工作记录；**不自签、不产生 ACCEPT、不换指标、不宣称显著更准确**。

---

## 1. 卡文逐字（唯一判据）

**卡头（L5）**：`Parent：I-12；状态：planned；Owner：执行者；统计reviewer独立复算；依赖：I-12-C。`

**前提（L9-L10）**：设计规定的指标、权重、cluster/block、种子、阈值已知。

**动作（L13-L17，逐字）**：
- **0. 先执行上述metric_numeric_oracle及负例，保存 `evidence/I-12-D/metric_oracle_result.json` 与 `metric_negative_results.json`；只有指标实现合格才能处理真实样本。**
- 1. 逐样本算signed_error和abs_error，按metric_definitions处理零分母、缺失、异常及边界，保存明细不得只留平均数。
- 2. 用同一可比样本成对评model与baseline；分行业/阶段/市场/horizon报告n_companies和n_origins。
- 3. 按已批准方法给成对误差差值或skill的不确定性区间；重复年度不是独立公司，使用冻结cluster/block单位。
- 4. 同时报告误差、偏差、情景包含率与宽度；没有概率声明禁用统计区间得分。

**停止（L19-L22，逐字）**：
- 发现零分母被任意epsilon替代、样本不对齐或结果挑选→STOP_METRICS。
- 样本未达设计要求→descriptive_only，不宣称显著更准确。

**验收（L24）**：独立抽核手算样本和聚合权重；公式/排除计数一致；未经批准不得换指标。

**证据（L26，逐字 7 件）**：`evidence/I-12-D/sample_errors.csv`、`evidence/I-12-D/metrics_by_stratum.json`、`evidence/I-12-D/paired_comparison.json`、`evidence/I-12-D/interval_diagnostics.json`、`evidence/I-12-D/metric_reproduction.md`、`evidence/I-12-D/metric_oracle_result.json`、`evidence/I-12-D/metric_negative_results.json`。

**研究卡原文（research_cards.json L629-L664，步骤 1-5 = 卡文 0-4）与 metric_numeric_oracle（L836-L951 逐字）**：
- 步骤 1「先执行metric_numeric_oracle的确定性合成用例；独立手算核对MAE/WAPE/Bias/Skill/包含率/宽度及条件统计区间得分，再执行零分母和sample_id错位负例。该n=3仅测指标程序，不能记作准确性实证。」
- `comparison`：「有理数按分子/分母独立求期望，比较abs(error)<=1e-12；布尔、sample_id与undefined原因精确比较。」
- `limitation`：「n=3只验证指标实现，不能证明模型准确性改善、覆盖校准或统计显著性。」
- 三条 `negative_cases` 与 `probabilistic_interval_subcase.precondition`（「只有在预测前声明名义覆盖率1-alpha=0.8的统计区间，才计算此子用例；普通low/high情景禁称统计区间。」）

---

## 2. 上游冻结输入（运行前实测 sha256；校验器逐件复算）

| # | 路径 | 字节 | sha256 |
|---|---|---|---|
| U1 | `execution_v2/card_I-12-D.md` | 1776 | `c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69` |
| U2 | `execution_v2/card_I-12-C.md` | 1604 | `49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91` |
| U3 | `execution_v2/research_cards.json`（指标公式 L130-L191 + oracle L836-L951） | 40058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` |
| U4 | `execution_v2/common_research_cards.md` | 14736 | `2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b` |
| U5 | `execution_v2/START_HERE.md` | 20436 | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` |
| U6 | `execution_v2/review_and_handoff.md` | 4005 | `602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9` |
| U7 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` |
| U8 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json`（字段 9/10/11/12） | 22317 | `203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0` |
| U9 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json`（6 项阈值 unsigned） | 5334 | `0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1` |
| U10 | `execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json` | 5618 | `ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178` |
| U11 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/sample_manifest.jsonl` | 11085 | `679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702` |
| U12 | `execution_runs/I-12-B/a20260926-01/evidence/I-12-B/actuals_policy_application.json` | 7916 | `998823537e8f493545562a05b1e0308f1865b0231ddb44b1bfc9fee5a7ac3942` |
| U13 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_vintages.jsonl` | 9918 | `42daea726d9d1d0c5e538881d5f31c663b3a5619a3f2d6dd7350e48a5965cf1f` |
| U14 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/baseline_vintages.jsonl` | 14104 | `043f31c9441030a003b5d2cba3286676d35fff30a801909e08b255c3f17a2cbc` |
| U15 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_manifest.json` | 5467 | `03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a` |
| U16 | `execution_runs/I-12-C/a20260926-01/evidence/I-12-C/unblind_receipt.json` | 1968 | `99ed0139434a2777f4ede1454782fb83c60f315c3d83e00e1c8b175324e991f1` |
| U17 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘，只读**） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` |
| U18 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（store，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` |

**前提核验（卡文 L9-L10）**：
- **已知**：指标公式（研究卡 L130-L191）、权重（设计字段 9：primary=entity 等权 macro、secondary=micro，两套并报）、cluster=entity / block=origin（字段 11 `structure_frozen`）。
- **未知（PENDING/unsigned）**：置信水平、重复抽样次数、随机种子、多重比较校正（字段 11 `threshold_items_unsigned` 四项）+ 样本量/功效（字段 10）+ 成功失败阈值（字段 12）⇒ 动作 3「按**已批准**方法给不确定性区间」**无可批准方法** ⇒ fail-closed 不算区间，逐项登记。
- **可执行面**：动作 0（合成 oracle + 负例）、动作 1/2 的明细与分层计数（样本为 0 时按 descriptive_only 登记）、动作 4 的四类并报（n=0 时登记不可算）。

---

## 3. 授权逐字

- **§三十四（L745-L780）**：「oracle 先冻结」「不放行任何参数」「不触发任何 falsifier/自动动作」「实现者不自签 · 独立复审 · 落定走三件套」；边界「不解除 OPEN-2/3/5/6」「不产生 ACCEPT、不改任何 status/decision/decision_sha256（除非是新卡自己的写入面）」。
- **§三十七（L852-L871）**：「给你授权所有的沙箱操作，不要再问我了」；边界「纪律 16/17/18/19/20 全部继续有效」「生产零未授权改动」「产品仓提交不在本授权内」。本卡零提权；禁 git（含 `git status`）、禁联网。
- **派单（2026-09-26）**：D 卡要点「先跑 metric oracle + 负例 → 合格才碰真实样本」；fail-closed 数据/历史期不足 ⇒ `not_applicable` 或 STOP 判 `blocked`（合格）。

---

## 4. 红线（只登记、不消费）

`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 登记值 **124,248.63**（真值 38,175.95），「OPEN-2 前禁消费」。本卡 `evidence/I-12-D/**` 禁止出现该两个字面量（D8 具名检查）；oracle 仅登记。

---

## 5. 判据 D（校验器 `_verify.py`；全绿 rc=0，违例 rc=3，缺件/坏 JSON rc=1）

| id | 判据 |
|---|---|
| D1 | `metric_oracle_result.json`：`synthetic=true`、`qualification=metric_implementation_only_not_accuracy_evidence`；逐项把实算结果与 research_cards.json `metric_numeric_oracle.expected`（**冻结期望，独立来源**）比对——有理数按数值相等（同时 abs(diff)<=1e-12 复核）、布尔/样本/原因精确比；全部 `pass=true`；`probabilistic_interval_subcase.computed=false` 且 `precondition_met=false`。 |
| D2 | `metric_negative_results.json`：3 条冻结负例逐条 `pass=true`——① 零分母 ⇒ WAPE/NormalizedBias/normalized_width = `undefined` + `zero_denominator`，MAE 仍可定义，**未加 epsilon**；② `forecast_sample_ids` 错位 ⇒ 拒绝按位置评分（`alignment_rejected`）；③ baseline loss=0 ⇒ skill=`undefined`，不得记 100% improvement。另 2 条扩展控制（high<low 数据错误、无名义覆盖禁算 interval_score）亦须 pass。 |
| D3 | `sample_errors.csv`：**仅表头、0 数据行**（真实样本不可评分）；表头含 sample_id/entity/segment/origin/horizon/actual/forecast/baseline/signed_error/abs_error 等字段；不得只留平均数（明细结构在位）。 |
| D4 | `metrics_by_stratum.json`：分市场/行业/生命周期/horizon 分层，逐层报 `n_companies`、`n_origins`、`n_scorable=0`；`state=descriptive_only`；`significance_claimed=false`；零分母/缺失计数器在位。 |
| D5 | `paired_comparison.json`：成对比较 `n_pairs=0`、`state=blocked_no_scorable_samples`、cluster=entity / block=origin 已登记、`uncertainty_interval=null` 且 `interval_method_not_approved=true`；无显著性宣称。 |
| D6 | `interval_diagnostics.json`：`probabilistic_claim_made=false`；`interval_score=disabled`、`pinball=disabled`、理由=无名义覆盖率声明（设计字段 9）；CI 四项 PENDING/unsigned 逐条登记；情景包含率/宽度 n=0 不可算。 |
| D7 | `metric_reproduction.md`：含 oracle 关键式手算过程（误差和/绝对误差和/分母/baseline 损失/宽度和）+ 复跑命令 + limitation 逐字（n=3 不证明准确性）。 |
| D8 | `evidence/I-12-D/**` 无 `124248.63`/`124,248.63`/`38175.95`；`params_released=false`、`implementer_signed=false`、`open2_ban_observed=true`（handoff）。 |
| D9 | 上游一致性：U1-U18 现场复算 sha 全等；封盘/store 零字节。 |
| D10 | handoff 形态：`status=review_pending`、`gate0_passed=true`、`releases_nothing=true`、`git_diff_non_planning=0`、`written_files` 覆盖 7 件证据。 |

**rc 码表（本卡自描述）**：`0`=全 D 通过；`1`=harness 失败；`2`=无裁决（未用）；`3`=具名 D 违例。

---

## 6. 变异清单（红臂；`_mut/<id>` 副本，原件字节不动）

| id | 变异 | 期望 |
|---|---|---|
| P1 | 把 `metric_oracle_result.json` 的 WAPE 期望值改掉（结果挑选/换指标形态） | rc=3（D1） |
| P2 | 把零分母负例结果改成 `WAPE=0.0（epsilon 代入）` | rc=3（D2） |
| P3 | 在 `sample_errors.csv` 塞入一行伪造的评分明细 | rc=3（D3） |
| P4 | 在 `interval_diagnostics.json` 声称已算 95% CI（阈值未签却出区间） | rc=3（D6） |
| P5 | 在 `metrics_by_stratum.json` 写 `significance_claimed=true`（宣称显著更准确） | rc=3（D4/D5） |
| 绿臂 | 原件 | rc=0 |

---

## 7. 门 0 原始输出（先于证据写入执行）

```text
=== GATE0 BEGIN (I-12-D/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-D\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-D a20260926-01 write-readback-delete 2026-09-26T21:14:27+01:00
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
--- step6 upstream B/C evidence (this batch) ---
sample_manifest.jsonl sha256=679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702 bytes=11085
forecast_vintages.jsonl sha256=42daea726d9d1d0c5e538881d5f31c663b3a5619a3f2d6dd7350e48a5965cf1f bytes=9918
baseline_vintages.jsonl sha256=043f31c9441030a003b5d2cba3286676d35fff30a801909e08b255c3f17a2cbc bytes=14104
--- step7 research_cards metric fixture (read-only) ---
research_cards.json sha256=4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263
=== GATE0 END ===
```

---

## 8. fail-closed 预期（写证据前声明）

1. **oracle 先行**：动作 0 的输出（`metric_oracle_result.json` + `metric_negative_results.json`）是处理真实样本的**前置门**；本卡在 oracle 全绿之前不写任何真实样本评分文件。
2. **真实样本 = 0 行**：上游 I-12-B `scorable_samples=0`（目标期未结束 + 未解封）、I-12-C `forecast_values_frozen=0`（params 未放行）⇒ `sample_errors.csv` 只有表头；分层 n_scorable=0；成对比较 n_pairs=0；`state=descriptive_only`，**不宣称显著更准确**。
3. **不确定性区间不算**：CI 水平/重抽样次数/种子/多重比较校正四项 `PENDING/unsigned` ⇒ 动作 3 无「已批准方法」可依 ⇒ `uncertainty_interval=null`、`interval_method_not_approved=true`（不是「算不出来」，是「未获批，不算」）。
4. **无概率声明 ⇒ 禁用统计区间得分**：设计字段 9 明确 low/high = 情景带 ⇒ `interval_score`/`pinball` 禁用；`probabilistic_interval_subcase` 前置不满足 ⇒ **不计算**（只登记），并以扩展控制验证「请求即被拒」。
5. **不换指标**：指标集合 = 冻结 `metric_definitions`（可选项 sMAPE/MASE/interval_score/pinball 未事前声明 ⇒ 不启用）。
6. **不读测试/准确性结果**：本卡读面 = 卡文 + 研究卡公式/ oracle 段 + I-12-A 字段 + I-12-B/C 证据（均为本批登记面，非准确性结果）。
