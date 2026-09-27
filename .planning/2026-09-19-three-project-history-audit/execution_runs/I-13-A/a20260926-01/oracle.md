# I-13-A · 买方交付逐项评分 —— oracle（**先冻结**，产物后写）

> 卡：`execution_v2/card_I-13-A.md`（1,383 B · sha256 `daaf300ebd3762e875e3c8b413de9e88d08110fe23709d5362030b544b14599b`）
> attempt：`execution_runs/I-13-A/a20260926-01`（新建）· role：`implementer_i13a` · 链位：19 卡链第 5 卡，`I-13` 串行链头，与 `I-12` 并行
> 依赖：`I-07-E` + `I-11-C` **均 `accepted_scoped`**（磁盘实测见 §3）
> **本件性质**：买方评分**实现者**工位 —— 按冻结评分尺机械打分 + 核 hard_blocks；**不自签**、`status=review_pending`、`releases_nothing=true`、不派 `I-13-B`。
> **冻结时序**：本文件写于 scorecard/blocking/artifact_references/verification/handoff **之前**；§6 预期与 §7 变异是产物必须逐条对上的**事前判据**，事后不得改写（如需更正 ⇒ 新建 attempt，不覆盖本件）。

---

## §0 门 0 自探（原始输出，逐字留档）

```
=== GATE0 BEGIN (I-13-A/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-13-A\a20260926-01
--- step0 mkdir ---
dir_exists=True
--- step1 write ---
write_ok=True
--- step2 readback ---
readback=gate0 probe I-13-A a20260926-01 write-readback-delete 2026-09-26T20:24:23.3543802+01:00
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
=== GATE0 END ===
```

- 三步自探（写 / 回读 / 删）= 本会话、零提权、探针已删无残件；封盘与 store 为**只读复哈希**。
- 结论：`gate0_passed=true`；封盘 `f2178768…` 零字节、store `b2063ac8…` 零改动（定稿时再复验一次，见 handoff）。

---

## §1 授权逐字（`authorized_by` 源）

### 1.1 派单（编排层 · 父 `session-19074bf0-0205-4315-af73-9db57597275a`，2026-09-26）
> 「你是编排层派单的**实现者**，开 **`I-13-A`**（19 卡链第 5 卡，`I-13` 串行链头，与 `I-12` 链并行）。依赖 `I-07-E` **+ `I-11-C` 均已落定 `accepted_scoped`**。」
> 硬性纪律（A 级 · V3 全量档）：**oracle 先冻结**（卡文判据 + 上游 sha + 红线 + `EA` 模板 + 变异 ≥3）+ **门 0 自探留档** · **不放行参数** · 不触发自动动作 · **不自签** · **落定父直写** · 封盘 `f2178768…` 零字节 · 禁五份计划文件 · 禁 `.planning` 外 · 禁 git 写 · **禁 `git status`** · 禁联网（需则 `provenance` 四件）· **fail-closed**：数据不足 ⇒ `STOP`（合格）· **不派 `I-13-B`**。
> **红线**：`base 124,248.63`（真值 38,175.95）`OPEN-2` 前禁消费 —— **只登记不消费**。

### 1.2 `OWNER_DECISIONS.md §三十四`（L745-L780，2026-09-26 15:4x）
- L754 owner 选择「**A**」；L757「改判 `I-11-B` 的开工门槛 —— 以 `MERGE` 七条当前 `5✅ + 2❌` 现状开工；`i11b_unblocked` 的语义从『7/7 才开』改为『**owner 明文许可开工**』」；L758「`C3`/`C5` 的残余**不丢、不隐藏**」。
- L761-L766 硬约束：**oracle 先冻结** / **不放行任何参数** / **不触发任何 falsifier·自动动作** / **实现者不自签 · 独立复审 · 落定走三件套** / `expert_assumption` 必须带敏感性区间 + `equivalent_to_disclosure_basis=false`。
- L769-L775 边界：不解除 `OPEN-2/3/5/6` 与任何 `BLOCKED-*`、不放行参数、**不产生 `ACCEPT`**、不代签。
- L779：「后继卡按卡文依赖顺序（`I-11-C ← I-11-B`）**另派**」——同理本卡 `I-13-A` 由编排层本轮另派行使。

### 1.3 `OWNER_DECISIONS.md §三十七`（L852-L871，2026-09-26 17:5x）
- 授权原话：「**给你授权所有的沙箱操作，不要再问我了**」；覆盖三仓读写 / 系统调用 / 文件落点 / 网络取证。
- 边界：纪律 16/17/18/19/20 继续有效；**生产零未授权改动**；**`git add/commit/push` 不在授权内**。
- 本卡使用面 = **零提权**（全部写入都在本 attempt 目录普通文件）；**网络 = 0**（`provenance` 四件未触发）。

### 1.4 卡文面（`card_I-13-A.md` 逐字要点）
- L5「Parent：I-13；状态：planned；Owner：**独立买方 reviewer，不参与该预测设定**；依赖：I-07-E、I-11-C。」
- L9 前提：「预测包及证据可读；**可以没有 I-12 准确性优势，但必须诚实标未证实**。」
- L11-L15 动作 1/2/3；L19-L20 停止；L22 验收；L24 证据三件（`evidence/I-13-A/*.json`）。

---

## §2 卡文判据冻结（评分尺 = 卡文动作点名的 `buy_side_dimensions` / `hard_blocks`，逐字）

> **回源面声明（V2-4）**：本卡派单只读清单 = ① `card_I-13-A.md` ② `I-07-E/a20260926-01`（summary 26KB + verification + accepted_scoped handoff）③ `I-11-C/a20260926-01`（`parameter_mapping.json` 18 映射 + accepted_scoped handoff）④ `OWNER_DECISIONS §三十四`+`§三十七` ⑤ 红线。卡文 L13「按 **buy_side_dimensions** 逐维打 0/1/2」与 L14「先核 **hard_blocks**」**直接点名**该两把尺、卡内未定义 ⇒ 本站**定域读** `execution_v2/research_cards.json` L192-L259（`buy_side_dimensions` 8 维 / `hard_blocks` 7 条 / `buy_side_classification` 1 条）取尺，**逐字冻结于 §2.1-§2.3**，此后不再展开该文件其余部分；**除该定域读外，清单外零读**（`START_HERE.md` / `common_research_cards.md` / `review_and_handoff.md` / 其他卡 attempt 均未读）。

### 2.1 `buy_side_dimensions`（8 维 × 0/1/2，逐字）
| id | title | score0 | score1 | score2 |
|---|---|---|---|---|
| B01 | 证据与信息日 | 重大事实无来源、未来信息泄漏或原文无法读。 | 来源可定位但至少一处重大结论未完成原文核查/版本对齐。 | 全部重大事实有原文/页码/hash/available_at且核查记录可复核。 |
| B02 | 收入定义与历史桥 | 币种/尺度/总净额/期间/并表范围错，或实质性未解释差额。 | 定义已知但重述/分部历史对账有待review。 | 历史收入、经营量价与分部合计可对账；差额及范围获审定。 |
| B03 | 因果驱动与参数 | 只有目标增速，或参数无依据/重复计数。 | 驱动明确但校准、时点或双计审查未完成。 | 主要驱动逐参数有证据或明确假设、幅度校准、时间和反方审查。 |
| B04 | 模型经济约束 | 单位/存量桥/产销/供需/收入确认存在矛盾。 | 公式通过但至少一项专业适配待签。 | 适用模型、存量锚点、单位、会计和生命周期约束均签署。 |
| B05 | 情景和敏感性 | 低高次序/依赖不合理、相关driver独立乱调或情景冒充概率。 | 有三情景但关键约束或敏感性未走查。 | 联合情景、关键约束、方向/幅度敏感性和非线性交互解释完整。 |
| B06 | 投资者决策信息 | 无法解释收入增长来源、时点、主要风险和可证伪条件。 | 能回答主体问题但贡献分解/预期差口径未完整说明。 | 增长贡献、路径、预期差或不可得说明、催化/反证及更新触发器清晰可追溯。 |
| B07 | 资格与准确性诚实 | 把合成测试/拟合/情景范围宣传为实际准确性证明。 | 局限写明但公式/适配/准确性三栏混在一起。 | 三栏独立；I-12已完成则准确转述，未完成清楚写unproven及覆盖缺口。 |
| B08 | 复现与交付完整 | 关键输入/输出/版本缺失，或伪造运行/发布回执。 | 可复算主体但证据链/独立签署/接续项未齐。 | 版本hash、命令日志、引用、独立审阅与接续项齐全；发布资格另行真实验证。 |

### 2.2 `hard_blocks`（7 条，逐字）
1. 实质性单位/币种/尺度/期间/总净额或并表范围错误。
2. 重要事实无可核原文、hash错、源实际读取未证实或信息泄漏。
3. 存量桥、收入对账、产销/供需约束失败且未获明确适用性裁决。
4. 参数冒充披露、管理层目标冒充独立证据、同一驱动双计。
5. 伪造模型运行、生产接线、下载/索引/发布回执或以文件名替代实际行为。
6. 未通过适用模型公式与披露资格，却以正式预测交付。
7. 把未验证概率、回测提升或准确性作为已经成立的结论。

### 2.3 `buy_side_classification`（逐字）
> 「任一硬阻断或任一维度0→**blocked**；没有0但存在1→**research_draft_needs_review**；全部八维2且独立签署→**buy_side_review_ready**。总分0–16只展示，不能抵消阻断；该标签不是投资回报保证或准确性认证。」

### 2.4 卡文动作 / 停止 / 验收 / 证据（逐字）
- 动作 1：「按buy_side_dimensions逐维打0/1/2并引用产物页/字段；**缺失不靠总分补偿**。」
- 动作 2：「**先核hard_blocks，再看评分**；每个blocking issue写**可复现样例、影响收入/场景/决策和所需修正**。」
- 动作 3：「全2才给buy_side_review_ready；任何0为blocked，只有1没有0则research_draft_needs_review。总分仅展示，不作自动放行阈值。」
- 停止：「任一hard_block成立→blocked，**禁止以总分或文字解释豁免**。」「未证明准确性只能写unproven，**不因这一事实自动否定**可审阅的研究草案。」
- 验收：「每个分值可由明确证据复核；不把分值或ready标签解释为投资建议正确率。」
- 证据：`evidence/I-13-A/buy_side_scorecard.json`、`evidence/I-13-A/blocking_issues.json`、`evidence/I-13-A/artifact_references.json`。

---

## §3 上游 sha 冻结（本站**只读复算**，2026-09-26；algorithm=sha256）

| # | path（相对 `.planning/2026-09-19-three-project-history-audit/`） | bytes | sha256 | 上游自记一致性 |
|---|---|---|---|---|
| 1 | `execution_v2/card_I-13-A.md` | 1383 | `daaf300ebd3762e875e3c8b413de9e88d08110fe23709d5362030b544b14599b` | 本站首测 |
| 2 | `OWNER_DECISIONS.md` | 109029 | `17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d` | == I-11-C handoff `input_hashes` ✅ |
| 3 | `execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md` | 26132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | == I-07-E handoff `written_files` ✅ |
| 4 | `execution_runs/I-07-E/a20260926-01/handoff.json` | 14267 | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` | 定稿后自记（`status=accepted_scoped`） |
| 5 | `execution_runs/I-07-E/a20260926-01/verification.json` | 10089 | `237bc2d394ec5726c05adc00f6b7de2b88e302aafe658300f64fbac5dd25671c` | == I-07-E handoff `written_files` ✅ |
| 6 | `execution_runs/I-07-E/a20260926-01/reviewer_report.md` | 9555 | `6b48a2f5e2085f70c29315b4da1537ba80006833ef721468d9c11a87d714cca2` | == I-07-E `status_authority.carrier_sha256` ✅ |
| 7 | `execution_runs/I-11-C/a20260926-01/parameter_mapping.json` | 54875 | `d542b34d3429f2409417c2d72cb4335ad2fdde5bf1875103b79a0a2abce7192c` | == I-07-E `input_hashes` + I-11-C `written_files_hashes` ✅ |
| 8 | `execution_runs/I-11-C/a20260926-01/mapping_verification.json` | 9193 | `cecdcb33281727f7c450d7c121d420dd743edbe53c88dbff25491cf8e4cb633f` | == I-07-E `input_hashes` ✅ |
| 9 | `execution_runs/I-11-C/a20260926-01/handoff.json` | 20258 | `da25f736cfde6f97047a691ddff28f1b079c6c29d1cfeac03729ce4c32b9c453` | == I-07-E verification `upstream_inputs` ✅（`status=accepted_scoped`） |
| 10 | `execution_runs/I-11-C/a20260926-01/oracle.md` | 16336 | `437a7758da4c038762ff72ca95b9cca7492e41fd87b8cd6eca70b397680a01ec` | == I-07-E verification `upstream_inputs` ✅ |
| 11 | `execution_runs/I-11-B/a20260926-01/expert_assumptions.json` | 8580 | `9f8b844e342ec17e731cbe4554388005f5070e0c586de329782df86ee3abd79f` | == I-07-E + I-11-C 双记 ✅（EA 模板源） |
| 12 | `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**，只读） | 51697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 零字节 ✅ |
| 13 | `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（**store**，只读） | 61231 | `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | 零改动 ✅ |

**上游落定实测**：
- `I-07-E/a20260926-01/handoff.json` → `"status": "accepted_scoped"`、`status_transition: review_pending -> accepted_scoped`、`status_authority.carrier=reviewer_report.md`（sha 同上 #6，`three_way_match=true`）✅
- `I-11-C/a20260926-01/handoff.json` → `"status": "accepted_scoped"`、`status_authority.carrier_sha256=0664b8cf…`、`three_way_match=true` ✅
- `I-11-C/parameter_mapping.json` 结构实测：`mapping_rows=18`；`value_states = mapped_not_released:13 | not_executable_no_propagation:1 | unmapped_declined_no_number:4`；`value_policy.params_released=false`；**`rows_claiming_released=0`**；`new_value` 全表**不含 124,248.63**（`contains_124248_63_in_new_value=False`）✅
- 层内登记差异（**只登记不更正**，见 §6 P12）：`u-N4` store `US-MSFT-10K-FY2026.doc_sha256` 63 位 vs I-07-B 实测 64 位。

---

## §4 ⭐ OPEN-2 红线（**只登记、不消费**）

> 派单逐字：「**红线**：`base 124,248.63`（真值 38,175.95）`OPEN-2` 前禁消费 —— 只登记不消费。」

- `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE`（登记除法成立值）= **124,248.63** 元/吨铜当量（109,977,556,345 ÷ 885,141）；store 自写除式真值 = **38,175.95**（按合成分母 2,880,807）；差 3.25×/3.26×。
- 本站红线动作：**只登记**该对值与出处（`I-07-E summary §F`、`I-11-C mapping row5 i11b_proposed_values`）；**禁止**进入任何收入路径/年度路径/分部加总/敏感性/情景/下游映射；`open2_ban_observed=true`。
- 机器可检判据：本 attempt 全部 JSON **不得出现** `consumed_for_forecast` / `params_released=true` / 任何把 124,248.63 写进 `released` 或 `new_value` 的形态；分数表内引用该值只能带 `registered_not_consumed` 语境。

---

## §5 `EA` 模板（冻结：`expert_assumptions.json` 7 条 · H4 (iv) 形态）

| id | 敏感性区间要点 | `equivalent_to_disclosure_basis` |
|---|---|---|
| EA-1 | 量 [0.9,1.1] / 价·收入 ±5% / g 按 (1+g)×0.95,1.05−1 | `false` |
| EA-2 | 系数 23/24/25 ⇒ 134,919.5 / 124,248.63 / 113,577.74；每 +1 ⇒ −10,670.89（两点差分，非偏导） | `false` |
| EA-3 | 基期=最后可得同口径年度值；±0% vs 趋势外推 ±10% 敏感性 | `false` |
| EA-4 | MSFT 三档 g（0.102/0.16/0.218 等）；注记区间不符=unverified-N3 | `false` |
| EA-5 | 矿产品分部基期 109,977,556,345（双路同值）；语义张力 ⇒ base 差约 3.17 倍 | `false` |
| EA-6 | 联合档 ≈−14.5% / +15.5%；独立极值 ≈+21% 不可能（`STOP_SCENARIO` 拦截对象） | `false` |
| EA-7 | `analyst_assumption_declined`（四槽位不给幅度假设，维持 null/_PLACEHOLDER） | `false` |

冻结判据：`count=7`、`all_have_sensitivity_interval=true`、`all_equivalent_to_disclosure_basis_false=true`（`I-11-B/expert_assumptions.json` sha `9f8b844e…`，EAF L75-L77）；`equivalent_to_disclosure_basis=true` 出现次数必须为 **0**。**本卡不新增 EA**。

---

## §6 事前预期（P 系列）—— 产物必须逐条复现

| id | 预期（写产物前冻结） |
|---|---|
| P1 | 8 维全部给出分值 ∈ {0,1,2}，每维 ≥1 条 `file:line`/字段级证据引用；**预期分值 B01=1, B02=1, B03=1, B04=1, B05=1, B06=1, B07=2, B08=1（合计 9/16，展示用）** |
| P2 | **维度 0 的个数 = 0** ⇒ 单凭分数不构成 blocked；若出现 0 ⇒ 与本预期不符须查明 |
| P3 | hard_blocks 7 条逐条给 `disposition ∈ {established, not_established}` + 依据 + 反证登记 |
| P4 | **HB1 = not_established**：交付面无单位/币种/尺度/期间/总净额/并表范围错误；分部恒等式 584,049,229,264−234,970,146,412=349,079,082,852 差=0；`u-N2`（REALIZED_UNIT 分母不自洽）传播值 `null` 未进任何路径 |
| P5 | **HB2 = not_established**：ZJ `CN-ZIJIN-AR2025` sha + p327/p328/p44/p56 + `published_at=available_at=2026-03-20`；MSFT `US-MSFT-10K-FY2026` + table 74/76 + `2026-07-29`；HK 源不可读处**显式 blocked-缺位不造数**（gap-U1/U2）；`u-N4` 63 位转录缺陷随附 64 位实测值可核 |
| P6 | **HB3 = established（fail-closed 从严读法）**：`存量桥/量恒等式未闭合且未获明确适用性裁决` —— ①`BLOCKED-6b/OPEN-11` 库存桥 **154 千克容差未签**（`parameter_mapping.json` row8 `carve_out`、`I-07-E summary §B1` #8/#9 状态列、两份上游 handoff `blocked_by` 记「未解」）②`H4` 口径桥 269t/534kg **闭合不了**、`§三十六` 追加支**已授权但 Q2 重跑/会签未成**；**反证同登记**（收入对账恒等式差=0、Cu 878,180+6,763=884,943 与 Au 82,743+418=83,161 主恒等式逐位闭合、受影响参数 `mapped_not_released` 零传播、上游复审按『登记不阻断』接受）⇒ **裁定权归独立买方 reviewer，本站不自裁、不豁免** |
| P7 | **HB4 = not_established**：`management_target_is_not_independent=true`（PLAN 105t/120万t 仅对照）、E1-E7 逐条 `ALLOWED_ONCE/PROHIBITED_CO_USE`、派生值标「推导值非披露原文」 |
| P8 | **HB5 = not_established**：门 0 与各校验器为真实运行（原始输出留档）、`synthetic_quarantine_enforced=true`、发布格 `blocked` 未伪造回执 |
| P9 | **HB6 = not_established**：`formal_publication_slot=blocked`、`params_released=false`、13 行 `mapped_not_released` + 5 行零传播 ⇒ 非正式预测交付 |
| P10 | **HB7 = not_established**：`accuracy=unproven`、情景带不称置信/概率、无回测提升主张 |
| P11 | **分类（按 §2.3 机械推导）= `blocked`**（因 HB3 established；分数侧无 0，若无 HB3 则为 `research_draft_needs_review`）⇒ **卡文 STOP = 是** ⇒ **不派 `I-13-B`**；同时必须写明：**该 blocked 不以『准确性未证明』为由**（卡文 L20 禁止） |
| P12 | blocking issue 三件套齐（可复现样例 / 影响收入·场景·决策 / 所需修正）+ **反证登记**（residual 不隐藏，§三十四 L758） |
| P13 | `artifact_references.json` 覆盖三公司 × 关键字段，路径+行号/字段可复核；小米 blocked-缺位如实登记（不写 3/3） |
| P14 | `verification.json`：绿臂 rc=0 + 红臂 ≥3 且违例具名 + **上游 13 件 sha 全量复算一致** |
| P15 | `handoff.json`：`role=implementer_i13a`、`authorized_by` 逐字、`gate0_passed=true`+原始输出、`open2_ban_observed=true`、`params_released=false`、`status=review_pending`、`implementer_signed=false`、`releases_nothing=true`、`written_files`、`git_diff_non_planning=0` |

---

## §7 变异清单（≥3，红绿双向；**副本执行，原件字节不动**）

**校验器**：`_verify_i13a.py`（python 3.13，只读校验）。**exit code legend（冻结）**：
`0 = ALL_INVARIANTS_OK`；`1 = harness 失败（文件缺失/JSON 不可解析）`；`2 = 本校验器不产生`；`3 = 不变量违例（具名 J1..J5）`。

不变量：
- **J1 release/authority lock**：`handoff.params_released=false` ∧ `implementer_signed=false` ∧ `releases_nothing=true` ∧ `status=review_pending` ∧ `gate0_passed=true` ∧ `git_diff_non_planning=0` ∧ `releases_nothing` 各项为真。
- **J2 scorecard rule**：8 维齐全、分值 ∈{0,1,2}、每维有证据引用；`classification` 必须等于由（hard block dispositions + 分值）机械推出的标签；`total` 与分值和一致且**不得**用总分覆盖阻断。
- **J3 open2 ban**：全部产物无 `consumed_for_forecast`；124,248.63 仅出现在带 `registered_not_consumed` 语境的登记字段；`open2_ban_observed=true`。
- **J4 upstream sha**：`verification.json` 的 `upstream_inputs` 逐件复算 == 记录值（13 件，含封盘与 store）。
- **J5 evidence completeness**：每条 hard block 有 `reproducible_sample`/`impact`/`required_fix`（established 者三者必填；not_established 者必须有 `basis` + `counter_evidence`）；每维 ≥1 引用。

| id | 变异（在 `_mut/` 副本上） | 期望 |
|---|---|---|
| GREEN | 原件五件 + 上游 13 件 | rc=0 `ALL_INVARIANTS_OK` |
| M1 | `buy_side_scorecard.json` → 把 `B07.score` 改 2→0，同时 `classification` 不改 | rc=3 违例含 **J2**（分数与分类不一致 / 出现 0 未触发 blocked） |
| M2 | `blocking_issues.json` → `HB3.disposition` `established`→`not_established`，`classification` 保持 `blocked` | rc=3 违例含 **J2**（有 0/无阻断与分类矛盾） |
| M3 | `handoff.json` → `params_released` `false`→`true` | rc=3 违例含 **J1** |
| M4 | `verification.json` → 上游 `card_I-13-A.md` sha 改 1 个 hex 位 + 产物内塞 `consumed_for_forecast` | rc=3 违例含 **J4**（并触发 **J3**） |
| M5（备用） | `artifact_references.json` → 删除 B06 的 evidence 引用 | rc=3 违例含 **J5** |

绿臂在定稿（handoff 写完）后**再跑一次**（`GREEN_FINAL`），证明原件未被红臂污染。

---

## §8 边界（本站不做什么）

不放行任何参数（`params_released=false`）· 不触发任何 falsifier/自动动作 · **不自签**（`implementer_signed=false`）· 不产生 `ACCEPT`、不改任何 `status`/`decision`/`decision_sha256` · 封盘 `f2178768…` 零字节 · store `b2063ac8…` 零改动（`low/base/high` 全 null、两个 `_PLACEHOLDER` 在位）· **不派 `I-13-B`**（也不派 I-12/I-16/I-17）· 不写五份计划文件 · 不写 `.planning` 之外 · 禁 git 写、**禁 `git status`**（只用 `git diff HEAD --name-only` 只读计数）· 禁联网（`provenance` 四件未触发）· 合成示例数隔离不进真实数值字段 · 残余不隐藏（fail-closed）。
