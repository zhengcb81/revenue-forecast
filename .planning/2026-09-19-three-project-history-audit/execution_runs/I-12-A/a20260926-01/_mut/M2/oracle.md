# I-12-A · 专业冻结评估设计 —— oracle（**先冻结**）

> 卡：`execution_v2/card_I-12-A.md`（sha `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` / 1,467 B）· attempt：`execution_runs/I-12-A/a20260926-01`（**新建**）· role：`implementer_i12a` · Parent：`I-12`（19 卡链第 4 卡，`I-12` 串行链头）
> 依赖：`I-07-E` = **`accepted_scoped`**（2026-09-26 20:1x 落定；本 oracle §2 复核其 handoff `status=accepted_scoped`、`status_transition=review_pending -> accepted_scoped`、`by=landing_parent_v3`）
> 冻结时间：**2026-09-26 20:1x（UTC+01 本地戳 `2026-09-26T20:17:16+01:00` 之后、任何设计产物之前）**
> 写入面（唯一）：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-12-A/a20260926-01/`（含 `evidence/I-12-A/`、`_mut/`）

---

## §0 冻结声明（本文件先于一切产物；时序可证）

1. **oracle 先冻结**：本文件写入 → 回读 → 计 sha → 才开始写 `evidence/I-12-A/*.json`；本文件 sha 记入 `design_manifest.json` 与 `verification.json`。
2. **测试集结果保持封存**：本工位**未读**任何测试集/回测/准确性结果（含 `I-10-B`、`I-13` 及任何 accuracy 数值面）；回源面严格限定于派单只读清单（卡文 + 上游 `I-07-E/a20260926-01` 三件 + `OWNER_DECISIONS §三十四/§三十七` + 红线登记），另加为逐项填表所必需的 `execution_v2/research_cards.json` L115-L129 `evaluation_design_fields` 字段清单与 L130-L191 `metric_definitions` 公式面（**仅公式与字段定义，不含任何结果值**）。
3. **OPEN-2 红线**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base 124,248.63`（真值 38,175.95）**OPEN-2 前禁消费** ⇒ 本卡**只登记不消费**（见 §4）。
4. **不放行参数** · 不触发自动动作 · **不自签**（独立复审另派）· 落定父直写（V3）· **不派 `I-12-B`**（依赖顺序另派）。
5. 封盘 `I-11-A/hypotheses.json` `sha=f2178768…` **零字节**；store `hypotheses_v3.json` `sha=b2063ac8…` 零改动（门 0 只读复哈希，§8）。

---

## §1 卡文判据（逐字；动作 / 停止 / 验收以卡文为准）

**卡头**：`I-12-A · 专业冻结评估设计`；`Parent：I-12；状态：planned；Owner：统计reviewer和行业reviewer共同签字；依赖：I-07-E。`

**前提（逐字）**：「上游证据资格/版本边界可用；无需等待完整I-07或I-10准确性结果。」

**动作（逐字）**：
1. 「逐项填写evaluation_design_fields，未定项标PENDING，不由弱模型选择方便通过的阈值。」
2. 「选择primary endpoint、baseline、权重、样本最小数量/功效、成对比较、cluster/block方法、CI和多重比较校正。」
3. 「严格区分真实历史vintage与重建实验；低/高情景没有概率标签就只评情景包含率。」
4. 「将设计、reviewer身份、签署、版本和SHA256冻结；测试集结果在此之前保持封存。」

**停止（逐字）**：
- 「任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。」
- 「已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。」

**验收（逐字）**：「evaluation_design_fields全部完成或有获批not_applicable；SHA256冻结在结果解封前。」

**证据（逐字）**：`evidence/I-12-A/evaluation_design.json`、`evidence/I-12-A/professional_approval.json`、`evidence/I-12-A/design_manifest.json`。

**字段面（冻结自 `research_cards.json` L115-L129，13 项，逐条原样进 `evaluation_design.json.fields[*].field`）**：primary endpoint 唯一性 · 样本单位 `entity×segment×origin×horizon×model_version` · 公司池与抽样 · 信息截点 · 训练/调参/验证/最终测试时间划分 · 实际值定义 · horizon 分层 · 朴素 baseline · 指标/权重/零分母/缺失与「low/high 是情景还是统计区间」 · 最小样本量/功效 · 比较设计（成对/cluster-block/CI/重复抽样/多重比较校正） · **成功失败阈值（由统计与行业 reviewer 签字；禁止看到结果后补阈值）** · 中止/重跑/版本修订与 manifest SHA256 冻结。

**「关键统计选项/阈值」清单（本卡冻结为未签署即触发停止①的项）**：
`最小样本量/每层样本数`、`统计功效或可接受CI宽度`、`置信水平(CI level/α)`、`重复抽样次数与随机种子`、`多重比较校正方法`、`成功/失败阈值（经济显著改善幅度、可接受偏差/覆盖/区间宽度）`、`中止阈值`。
> 以上**任一未由「统计reviewer + 行业reviewer」签署**（卡头 Owner 栏）⇒ 卡文停止①字面成立 ⇒ **`BLOCKED_PROFESSIONAL_DECISION`**。
> 实现者**不得**代签（§三十四 L765「实现者不自签 · 独立复审」；派单硬性纪律）。

---

## §2 上游 sha 清单（只读复算，2026-09-26 20:1x 实测）

| # | 路径（相对 plan root） | bytes | sha256 | 与上游冻结值 |
|---|---|---|---|---|
| 1 | `execution_v2/card_I-12-A.md` | 1,467 | `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` | 本卡卡文（派单指定源） |
| 2 | `execution_v2/research_cards.json` | 40,058 | `4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263` | 字段清单/指标公式面 |
| 3 | `OWNER_DECISIONS.md` | 109,029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` | ✅ 与 I-07-E `verification.json` L29 逐字节一致 |
| 4 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26,132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | ✅ 与 I-07-E handoff L92 一致 |
| 5 | `execution_runs/I-07-E/a20260926-01/verification.json` | 10,089 | `237bc2d394ec5726c05adc00f6b7de2b88e302aafe658300f64fbac5dd25671c` | ✅ 与 I-07-E handoff L96 一致 |
| 6 | `execution_runs/I-07-E/a20260926-01/handoff.json` | 14,267 | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` | 落定件（`accepted_scoped`） |
| 7 | `execution_runs/I-07-E/a20260926-01/oracle.md` | 18,913 | `5f3685e0b7f628a089636e2226fd03eef95952d0d6b2ba22f3cb7a7cee5ca7fc` | ✅ 与 I-07-E handoff L88 一致 |
| 8 | `execution_runs/I-07-E/a20260926-01/evidence/I-07-E/qualification.json` | 767 | `60f2e263db99b9c595dbedf54226c18fc2f8e8ca5ee3f417b71f8ac9df09fb08` | 上游证据资格 |
| 9 | `execution_runs/I-07-E/a20260926-01/reviewer_report.md` | 9,555 | `6b48a2f5e2085f70c29315b4da1537ba80006833ef721468d9c11a87d714cca2` | ✅ 与 I-07-E handoff L172/carrier 一致 |
| 10 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | ✅ 零字节（派单 `f2178768…`） |
| 11 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（**store，只读**） | 61,231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | ✅ 零改动；`low/base/high` 全 null、两 `_PLACEHOLDER` 在位 |

**上游资格面（冻结）**：`I-07-E/handoff.json` → `status=accepted_scoped`、`implementer_signed=false`、`params_released=false`、`releases_nothing=true`、`open2_ban_observed=true`、`status_authority.three_way_match=true`、`accuracy=unproven`（「准确性 F 归后继 I-12，卡文 L6/L12」）。
**卡前提满足性**：「上游证据资格/版本边界可用」= 上表 11 件可读可复算 + `I-07-E` 落定 ✅；「无需等待完整 I-07/I-10 准确性结果」= 本卡**不读**任何准确性结果 ✅。

---

## §3 授权（逐字）

**`OWNER_DECISIONS §三十四`（L745-L780）—— 本卡沿用其「开工卡硬约束」形态**：
- L757：「改判 `I-11-B` 的开工门槛 —— 以 `MERGE` 七条当前 `5✅ + 2❌` 现状开工；`i11b_unblocked` 的语义从『7/7 才开』改为『owner 明文许可开工』」
- L761-L766 硬约束逐条：「**oracle 先冻结**」「**不放行任何参数**」「**不触发任何 falsifier/自动动作**」「**实现者不自签 · 独立复审 · 落定走三件套**」「每一条以 `expert_assumption` 承接的判断，必须给敏感性区间 + `equivalent_to_disclosure_basis=false`」
- L769-L775 边界：「不解除 `OPEN-2/3/5/6` 任何一条」「不放行参数」「不产生 `ACCEPT`、不改任何 `status`/`decision`/`decision_sha256`（除非是新卡自己的写入面）」「不代签行业面 / 会计面 / 外部方」
- L779：「`I-11-B` 的 `I-11-C` 后继卡按卡文依赖顺序另派，**不在本节一并授权**」（形态沿用 ⇒ 本卡**不派 `I-12-B`**）

**`OWNER_DECISIONS §三十七`（L852-L871）—— 全沙箱常设授权**：
- L855-L856：「本会话内编排层（父）的一切沙箱提权操作，owner 一次性常设授权，**无需逐次审批**」，覆盖三仓读写 / `OpenProcess` 等系统调用 / 任意目录文件创建修改 / 网络取证。
- L859-L863 边界（**授权 ≠ 免除纪律**）：「纪律 16/17/18/19/20 全部继续有效」「破坏性操作仍须前像留痕+写后验证+fail-closed 回滚；派单仍须标能力主体」「**产品仓提交（`git add/commit/push`）不在本授权内**」。
- **本卡使用面 = 零提权**（全部动作在本 attempt 目录普通文件写入）；`git` 一律不调用（`git status` 派单禁用；`git_diff_non_planning=0` 由写入面枚举推导）；**禁联网** ⇒ `external_retrieval_not_local=false`（零外部检索）。

---

## §4 ⭐ OPEN-2 红线（**只登记、不消费**；`open2_ban_observed` 必须为 `true`）

| 登记项 | 值 | 性质 | 本卡处置 |
|---|---|---|---|
| `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 登记除法成立值 | **124,248.63** 元/吨铜当量 | 推导值，非披露原文 | **`consumed_for_forecast`** —— 禁入任何 endpoint / baseline / actual / 权重 / 样本分层 / 情景包含率计算 |
| store 自写除式真值（对照） | **38,175.95** | 先天缺陷对照 | 只登记；与上值差 3.25×/3.26× |
| I-11-B proposed 三档 | 118,036.2 / 124,248.63 / 130,461.06 | `proposed_not_released` | 只登记；传播值 = null |
| EA-2 系数两点差分 | 系数 +1 ⇒ −10,670.89 | 非偏导 | 只登记 |
| 红线原文出处 | `REMEDIATION_REGISTER.md` L3951「OPEN-2 前禁消费」（转引自上游 `I-07-E §F`，本卡不回读该 486 KB 登记册） | — | 全程遵守 |

**消费面定义（本卡）**：把上述任一数值作为评估设计的输入、阈值、样本筛选条件、分层边界、baseline 或 actual ⇒ 视为 `consumed_for_forecast` ⇒ 红臂 `M2` 击杀。

---

## §5 EA 模板冻结（转引上游 `I-07-E §B3`；本卡**不新增 EA、不改 EAF**）

- 7 条全量 `EA-1..EA-7`；实测 `count=7`、`all_have_sensitivity_interval=true`、`all_equivalent_to_disclosure_basis_false=true`。
- **常量**：`equivalent_to_disclosure_basis=false`（每条必带）；`=true` 出现次数必须为 0。
- `EA-7 = analyst_assumption_declined`（两分金属实现价、`MSFT_CLOUD`、`MSFT_LICENSING` 显式拒绝出数，维持 `null`/`_PLACEHOLDER`）。
- 评估设计中任何承接判断的项（如 band 形状、基线选择）沿用 `expert_assumption` 形态：敏感性区间 + `equivalent_to_disclosure_basis=false`。

---

## §6 预期判据（校验器 `_verify_design.ps1` 冻结为 J1-J6）

| id | 不变量 |
|---|---|
| `J1_release_lock` | `handoff.params_released=false` / `implementer_signed=false` / `releases_nothing=true` / `status=review_pending` / `params_released_count=0` |
| `J2_open2_ban` | `handoff.open2_ban_observed=true`；`oracle.md`/`evaluation_design.json` 带 `registered_not_consumed` 且**禁**出现 `consumed_for_forecast` |
| `J3_upstream_sha` | `design_manifest.json.upstream_inputs` 11 件逐件按 sha256 复算比对（含封盘 `f2178768…`、store `b2063ac8…`） |
| `J4_professional_signoff` | `professional_approval.json`：`statistical_reviewer`/`industry_reviewer` 两块 `signed=false`、`signature_status=unsigned`、**`implementer_signed=false`**、`stop_condition_triggered=BLOCKED_PROFESSIONAL_DECISION`（未签署 ⇒ 必须为 STOP，不得静默通过） |
| `J5_result_seal` | `design_manifest.json.test_results_unsealed=false` 且 `evaluation_design.json.test_results_sealed=true`；`accuracy_results_read=false` |
| `J6_manifest_freeze` | `design_manifest.json` 内登记的 `oracle.md`/`evaluation_design.json`/`professional_approval.json` sha256 与磁盘实测逐件一致 |

**exit_code_legend（冻结，与 I-07-E 同名同义）**：`0`=ALL_INVARIANTS_OK · `1`=harness 失败 · `2`=无裁决 · `3`=不变量违例（具名 J1..J6）。跨批聚合先读 legend，不假设码表一致。

---

## §7 变异清单（红绿双向，≥3；本卡 **5 红 + 1 绿**，在 `_mut/` 副本执行，原件字节不动）

| id | 变异（仅 `_mut/Mx/` 副本） | 期望 rc | 击杀判据 |
|---|---|---|---|
| `GREEN` | 原件（`oracle.md`+`evidence/*`+`handoff.json`+`verification.json`） | **0** | J1-J6 全 OK |
| `M1` | `handoff.json` `params_released` false→true（模拟放行参数） | 3 | J1 |
| `M2` | `oracle.md` 红线登记 `registered_not_consumed`→`consumed_for_forecast`（模拟消费 OPEN-2 禁消费值） | 3 | J2 |
| `M3` | `design_manifest.json` 内 `evaluation_design.json` 的 sha256 改 1 个 hex 位（模拟冻结指纹不符） | 3 | J6 |
| `M4` | `professional_approval.json` 把 `industry_reviewer.signed` false→true 且 `stop_condition_triggered` 改空（模拟实现者自签/静默通过） | 3 | J4 |
| `M5` | `design_manifest.json` `test_results_unsealed` false→true（模拟结果提前解封） | 3 | J5 |

`M3` 变异同时会让 J3/J6 的复算路径受检；红臂原始输出逐字存 `_mut/Mx/verifier_output.txt`。

---

## §8 门 0 自探原始输出（逐字）

```
=== GATE0 BEGIN (I-12-A/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast
attempt_dir=.planning\2026-09-19-three-project-history-audit\execution_runs\I-12-A\a20260926-01
--- step1 write ---
write_ok=True
--- step2 readback ---
gate0 probe I-12-A a20260926-01 write-readback-delete 2026-09-26T20:17:16.4769068+01:00
--- step3 delete ---
deleted_gone=True
--- step4 sealed sha (read-only) ---
sealed_I-11-A_hypotheses_sha256=f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28
sealed_matches_f2178768=True
sealed_bytes=51697
--- step5 store sha (read-only) ---
store_hypotheses_v3_sha256=b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff
store_matches_b2063ac8=True
=== GATE0 END ===
```

---

## §9 STOP 判定规则（fail-closed；本卡不自裁他卡）

- **停止①**：`§1 关键统计选项/阈值清单` 中任一项在 `professional_approval.json` 内无「统计reviewer + 行业reviewer」签署 ⇒ **`BLOCKED_PROFESSIONAL_DECISION`**（卡文逐字）。实现者无签署资格 ⇒ 该条件在本 attempt 内**必然成立**，必须如实登记，不得以「已填写」冒充「已签署」。
- **停止②**：「已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功」。本卡 `test_results_sealed=true`（未读结果）⇒ 本 attempt **未触发**停止②；设计此后任何改动 ⇒ 必须新开探索版本，旧结果不得追认。
- **数据不足 ⇒ STOP 判 `blocked`（合格）**：字段缺失、样本量无法核算、签署缺位一律 fail-closed，不以「设计已填」推进到解封。
- **裁定权边界**：卡文停止条件的最终裁定 = 独立复审/编排层；本站只**登记触发事实**，不改任何卡 `status`/`decision`/`decision_sha256`，不产生 `ACCEPT`。

---

## §10 本卡不做什么（边界自宣）

不放行任何参数（`params_released=false`、放行计数 0）· 不触发任何 falsifier/自动动作 · **不自签**（`implementer_signed=false`，独立复审另派）· 不产生 `ACCEPT` · 不改任何卡 `status`/`decision`/`decision_sha256` · 封盘 `I-11-A/hypotheses.json` 零字节（`f2178768…`）· store 零改动（`b2063ac8…`，`low/base/high` 全 null、两 `_PLACEHOLDER` 在位）· 不新建 hypotheses 版本（`supersedes` 未启用）· **不派 `I-12-B`**（依赖顺序另派）· 不写五份计划文件 · 不写 `.planning` 之外（`git_diff_non_planning=0`）· 禁 git（含 `git status`，本卡零 git 调用）· 禁联网（`external_retrieval_not_local=false`）· **不读测试集/准确性结果**（封存）· OPEN-2 只登记不消费（`open2_ban_observed=true`）· 缺信息标 `PENDING`、残余不隐藏（fail-closed）。
