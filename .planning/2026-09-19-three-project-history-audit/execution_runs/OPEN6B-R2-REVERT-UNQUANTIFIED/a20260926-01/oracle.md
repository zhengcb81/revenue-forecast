# `OPEN6B-R2-REVERT-UNQUANTIFIED` · 判据（Oracle，**先冻结**）

- 工位：`implementer_r2_revert`（**有写入面的实现者**，`ruling_6b.md L97` 明定该写入归属）
- 载体（新建、唯一写入面）：`execution_runs/OPEN6B-R2-REVERT-UNQUANTIFIED/a20260926-01/`
- 上游依据（**本工位已逐字回源，不采信派单转述**）：
  - `OWNER_DECISIONS.md §三十三`（**当轮新立**）sha256 `9075f9aac00ded42164b4a4a5f8087b99f1312b67163749b6e63fdcf7d6dffb4`（96,826 B）
  - `execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/not_closed.json` sha256 `f1545f064329ccaa2fcfc7271bc79e8b5b3f620b1178f5ce09aa22ef02d26aea`（17,593 B）
  - `execution_runs/OPEN6B-TOLERANCE-RULING/a20260926-01/ruling_6b.md` sha256 `e5d1efce3821c252d0da18b7cd5734192993328f03da6c918eaa42db417ee3df`（28,628 B）
  - `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘原件**）sha256 `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B，**本工位自算，与父所知前缀 `f2178768…` 一致**）
- 冻结时点：**2026-09-26T14:5xZ（门 0 之后、任何落点写入之前）**
- 一句话：本 oracle 只定义「**落点在哪**」「**退什么字段**」「**哪一支被授权退**」「**怎么回滚**」「**什么算 blocked**」「**变异清单**」；**不含任何签署权、不含任何解除权、不修订 `revert_rule` 字面**。

---

## ① 授权（逐字回源）

### 1.1 `OWNER_DECISIONS.md §三十三`（L716–L741，**整节逐字读**）

- 标题（L716）：`## 三十三、【已裁定·第十七批】**\`6b\` 的 R2 恢复路径：「确认适用 (c) 不改规则（建议）」**（2026-09-26 15:1x，选项式问答原话）`
- 提问（L721）：`…… \`OPEN6B-R2-INVENTORY-BRIDGE\` 工位推荐路径 **(c) 退 \`unquantified\`**，**但 \`hypotheses.json L315 revert_rule\` 两条字面触发实测均不成立** ⇒ 执行 (c) 需先确认「无法凑平 ⇒ 口径不一致」这一支是否适用、或先修订 \`revert_rule\`。三选一。`
- **owner 选择（L722，原话）**：**`「确认适用 (c) 不改规则（建议）」`**
- 执行映射（L724–L732）四条：
  1. **认裁定**：残差是**结构性、跨年、金行专属**（**+93 / +154 千克**，**93–154 倍于 1 千克粒度**）⇒ 属 `ruling_6b L97` 的「**结构差无法解释**」支。
  2. **授权编排层按 (c) 执行** `revert_rule` 的那一支 → **退 `unquantified`**。
  3. **⚠️ 不修订 `revert_rule 字面`** —— 但执行记录里**必须写明**：本支适用理由 / 实测证据 / 字面触发不成立的事实如实登记（① `83,161 ≤ 84,477` 未超 ② 方向一致）+ 「无法凑平 ⇒ 口径不一致」支由本裁定确认适用 / 恢复条件三条（公司披露按金属拆分期末存货千克 / 并购标的购买日存货重量明细 / 产销量表加「在产品·在途·寄售」数量列 —— **任一出现即可按 `oracle §3.2` 重评**）。
  4. **`(b)` 的复活条件入册为待办**：须同时 ① owner 按 `DEC-14` 修订 `A-6.2`（含 `I-11-A`/`I-11-C` 校验器同步）② 另取**可核的黄金存货数量**；**缺一即退化为「为解锁而签」**。
- ⚠️ 边界（L734–L737）四条：**只处理 R2 这一行** ⇒ `BLOCKED-6b` 是否变 `accepted` 仍须按 `ruling_6b L110` 另判（4 条逐条签署，现 `signed_count=3`/`not_signed_count=1`）· 不解除 `BLOCKED-6a/6b/6c`、`OPEN-2/6/11`、不放行参数、不产生 `ACCEPT`、不代签 `τ` · **执行者不修订 `revert_rule` 字面**（owner 选择 #2「不改规则」）。
- 执行纪律（L740–L741）：**R2 退 `unquantified` 的写入属有写入面的实现者/编排层**（`ruling_6b L97` 明定）⇒ 派工须给足字节级回滚（`hypotheses*.json` 前像 + `supersedes`）；**若执行中发现 `revert_rule` 写入面不在计划目录内（须写产品仓）⇒ 停、报 `blocked`、不试替代写法（纪律 16/17）**。

### 1.2 `ruling_6b.md`（**L66 / L90 / L94–L97 / L104 / L110 逐字**）

| 行 | 逐字原文 |
|---|---|
| **L66** | `### 2.3 Q3 · R2（\`H-CN-ZIJIN-VOL-03\`）是否补登数值容差 → **不补登，\`NOT_SIGNED (insufficient_evidence)\`**` |
| **L90** | `**附带测量（非放行）**：四产品的**上限判据**（\`销售量 ≤ 生产量 + 期初库存\`）与**方向判据**（销量高于产量 ⇒ 库存下降）实测**均通过** —— 这是我自算的**测量事实**，不构成对 R2 的放行，也不产生 ACCEPT；R2 的**凑平支**按 OPEN-11 R4 第5步在容差签署前**不执行**。` |
| **L94** | `**恢复规则（R2 可被签署的三个互斥路径，均须新版本）**：` |
| **L95** | `(a) 取得**存货桥闭合证据**（在产品 / 在途 / 寄售 / 并购范围明细，OPEN-11 R6 条件2）解释 154 千克，恒等式按新口径重述后，在 \`0 < τ ≤ 1 单位\` 内按 A-6.3(2) 选基础签署；` |
| **L96** | `(b) 若确须 \`τ > 1 单位\` ⇒ 先由 owner 修订 A-6.2（DEC-14，含 I-11-A / I-11-C 校验器同步），我**不代改**；` |
| **L97** | `(c) 若结构差无法解释 ⇒ 按 \`hypotheses.json\` L315 \`revert_rule\` 退 \`unquantified\` —— 该写入属有写入面的实现者 / 编排层，**我不执行**。` |
| **L104** | ``R2 | \`H-CN-ZIJIN-VOL-03\` | 无 | 1 吨 / 1 千克 | **154 千克**（铜+1、锌0、银−1、金+154） | **\`NOT_SIGNED\`** | \`insufficient_evidence\` `` |
| **L110** | `**恢复规则（整条 \`BLOCKED-6b\`）**：新建 \`OPEN6B-TOLERANCE-RULING-R2\`（附本裁 \`decision_sha256\`、证据链、作用域）追加裁定；R1/R3/R4 的签署值不受 R2 影响，但**整条 BLOCKED 的状态**由 owner / 编排层在 R2 解决后重判；本文件与被审 attempt 一律**不回改**。` |

⇒ **本工位只执行 L97 的 (c) 写入；L110 的整条 `BLOCKED-6b` 重判权**不属本工位（现 `signed_count = 3` / `not_signed_count = 1`）。

### 1.3 `not_closed.json`（**实测依据**，逐字要点）

- `verdict.bridge_closed = false`；`residual_explained_kg = null`；`suggested_tau_basis = null`；`trigger = ["B1","B2"]`
- `verdict.closure_computation`：`sum_A_kg = null`、`actual = "无法计算 —— 没有任何一条满足 C1 的调整项"`、`gap_kg = 154`
- `statement`：`四条线各查到方向一致但零数量的证据；净可量化解释量 = 0 千克；与 154 千克的差 = 154 千克（> A-6.2 上限 1 千克的 154 倍）`
- `evidence_sufficiency_vs_oracle.C1_quantified = "FAIL（四条线 0 千克）"`
- `blocked_triggers_fired = ["B1: ΣAᵢ = 0 千克（无可计入项），|154 − 0| = 154 > 1 千克", "B2: 找到的证据全部为定性/金额级（QUAL 或非数量级），无一条满足 C1"]`
- `cross_year_structural_test.result`：`16 个『行×年』检验中 14 个落在 ±1 单位（A-6.2 帽内）；只有『矿山产金』连续两年超帽：FY2024 +93 千克、FY2025 +154 千克（两年合计 +247 千克）`
- `next_step.recommend = "(c)"`，三条 `recommend_reason`（结构性/跨年/金行专属 93–154 倍粒度 · 四线无数量 ⇒ (b) 亦无 A-6.3 可核基础 · (a) 实证不可达）
- ⚠️ `caveat_that_must_be_resolved_by_owner`（逐字）：`hypotheses.json L315 revert_rule 的两个字面触发条件实测均不成立 —— ①『销售量 > 生产量 + 期初库存』：83,161 ≤ 84,477（未超）；②『与库存量同比变动方向相反』：方向一致（库存下降）。故执行 (c) 需要 owner/编排层先确认『无法凑平 ⇒ 口径不一致』这一支是否适用于本情形，或先修订 revert_rule；**本工位不执行该写入**`
- `what_would_close_it_later`（三条恢复条件）：`任一年出现下列之一即可按 oracle §3.2 重评：公司披露按金属拆分的期末存货数量（千克）、并购标的购买日存货的重量明细、产销量表新增『在产品/在途/寄售』数量列`
- `releases_nothing = true`、`signed_by_this_station = false`、`does_not_sign_tau = true`

⇒ §三十三 已把上述 `caveat` 裁定为**「确认适用 (c) 不改规则」**，本工位据此**只执行、不修订**。

---

## ② 门 0 · 写入面预检 + 目标目录写探针（**原始输出，逐字**）

> 纪律 16/17/19：**不采信父代理的探针与权限**（父提权可写 ≠ 我可写，能力须标主体）。本工位在**自己的目标目录**内重做「建临时文件 → 回读 → sha → 删除」，并**自探落点位置**。

```
== [1] mkdir ==
created: C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\OPEN6B-R2-REVERT-UNQUANTIFIED\a20260926-01
== [2] write ==
write OK bytes=92
== [3] read back ==
readback: GATE0-PROBE a20260926-01 utc=2026-09-26T14:52:50Z nonce=1b0fa283-737d-4ca2-b76b-394abcc0769c
readback_equals_written: True
== [4] sha256 ==
sha256: 867345aafe295c3b95576dac8e23005dabbae9c9d444a3420487ab7b4291666c
== [5] delete ==
probe_exists_after_delete: False
== [6] landing-point inventory (all hypotheses.json in repo) ==
C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\BLOCKED6C-THRESHOLD-REVIEW-STATUS\a20260926-01\iso\evidence\I-11-A\hypotheses.json
C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\BLOCKED6C-THRESHOLD-REVIEW-STATUS\a20260926-01\iso_patched\evidence\I-11-A\hypotheses.json
C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-11-A\a20260919-01\evidence\I-11-A\hypotheses.json
C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I11A-OPEN12-VALIDATOR-COMPLETENESS\a20260925-01\iso\evidence\I-11-A\hypotheses.json
C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I11A-OPEN12-VALIDATOR-COMPLETENESS\a20260925-01\iso_patched\evidence\I-11-A\hypotheses.json
== [7] landing check ==
landing_path=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-11-A\a20260919-01\evidence\I-11-A\hypotheses.json
inside_planning=True
== GATE0 RESULT: write=True read=True delete=True ==
```

**门 0 判定（逐条）**

| 项 | 实测 | 结论 |
|---|---|---|
| 写/读/删三步 | `write=True read=True delete=True`（探针已删，不留残迹） | `gate0_passed = true` |
| 落点位置 | 全仓 `hypotheses.json` 共 **5 份，全部位于 `.planning\…` 计划目录内**（上列 [6]），**产品仓 0 份** | **落点在计划目录内 ⇒ 走 `hypotheses_h4_v1.json` 形态**（`provenance.supersedes_sha256` 指向封盘原件 + `modified_indices`，**封盘原件零字节改动**） |
| 是否须写产品仓 | **否**。`revert_rule` 的落点（`hypotheses[2].state`）与 `revert_rule` 字面所在行**均在计划目录**；产品仓无任何 `hypotheses.json` | **未触发**「须写产品仓 ⇒ 立即停、报 `blocked`」分支 |
| 5 份副本一致性 | 5 份 sha256 **全等于** `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`（51,697 B，UTF-8 无 BOM、LF、crlf=0） | 封盘原件基线唯一、可复算 |
| 破坏性替代 | **未使用** `git apply` / `>` 重定向 / 删后重写（`findings` R115 教训） | 合规 |

**基线（写入前自算）**：`git -c core.quotepath=false diff HEAD --name-only` ⇒ 总 **3830** 行、**非 `.planning` = 0**（未执行 `git status`）。

---

## ③ `revert_rule` 字面与本工位定位到的分支

- **文件（唯一含该规则的落点文件）**：`execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`
- **行号**：**L315**（`falsifier.revert_rule`）；**字节区**：**`[19071, 19346)`**（0-based，UTF-8，行首 `\n` 前后各计，行文本 275 字节）
- **同条目定位**：数组下标 **`2`** = `H-CN-ZIJIN-VOL-03`（`hypothesis_id` 在 **L241，字节 `[13750, 13789)`**；`state` 在 **L243，字节 `[14016, 14059)`**；阈值句 `falsifier.threshold` 在 **L310，字节 `[17940, 18378)`**）
- **字面（逐字，owner 选择 #2「不改规则」⇒ 本工位只读不改）**：

```
"revert_rule": "若销售量超过『生产量+上期期末库存』，或与库存量同比变动方向相反且无法凑平，判定为口径不一致（可能产销量表口径变化），该参数退回 unquantified 并保留旧快照，不得用差额继续外推。"
```

- **规则的三个支**（按字面结构）：
  - **支①（字面触发 1）**：`销售量 > 生产量 + 上期期末库存`
  - **支②（字面触发 2 + 凑平）**：`与库存量同比变动方向相反` **且** `无法凑平`
  - **支③（阈值句 L310 的「无法凑平 ⇒ 判口径不一致」支）**：`方向相反或无法凑平 ⇒ 判口径不一致` —— **本支的适用性由 `OWNER_DECISIONS §三十三` 当轮裁定确认适用**
- **本工位执行的分支**：**支③（「无法凑平 ⇒ 口径不一致」）**，依据 = §三十三 L722 owner 原话 `「确认适用 (c) 不改规则（建议）」`；**支①/支② 的字面触发不成立（如实登记，见 `revert_r2.json` §三十三四件）**。

---

## ④ 写入面与回滚（前像）

| 项 | 值 |
|---|---|
| **目标文件（新建）** | `execution_runs/OPEN6B-R2-REVERT-UNQUANTIFIED/a20260926-01/hypotheses_r2_v1.json` |
| **基线（supersedes）** | 封盘原件 `execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`，sha256 `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`，51,697 B |
| **封盘原件** | **零字节改动**（写入前后各复算一次 sha，两值须相等） |
| **前像** | `preimage/hypotheses.json`（完整副本）+ `preimage/preimage_manifest.json`（sha256 + bytes + 复算记录）—— **回滚唯一依据，先落盘并复算** |
| **回滚步骤** | ① `preimage/hypotheses.json` 复算 sha = `f2178768…` ② 该副本即封盘原件的逐字节镜像（封盘原件本就未改）③ 删除 `hypotheses_r2_v1.json` 即回到派单前状态；本载体其余文件均可整目录删除，**产品仓与封盘原件无需任何回滚动作** |
| **文件形态** | 顶层仍为与封盘同形的 **8 元素 JSON 数组**；`provenance` 附在被改动的下标 `2` 条目内（JSON 数组无顶层伴随键）—— 与 `hypotheses_h4_v1.json` 同构 |

## ⑤ 改动白名单（**只许这些**）

| 字段 | 前 | 后 |
|---|---|---|
| `hypotheses[2].state`（**`target_field`**） | `pending_professional_decision` | **`unquantified`** |
| `hypotheses[2].state_reason` | 原文（保留在 `revert_r2.json` 前像段） | 记录本次退回依据（§三十三 / (c) / 不改字面） |
| `hypotheses[2].provenance`（新增） | 不存在 | `hypotheses_version_provenance/1`：`supersedes_sha256` + `modified_indices=[2]` + `unchanged_indices` + 分支说明 |

**明令禁改（本工位白名单之外一律不动）**：`revert_rule` 字面 · `falsifier` 其余键 · `threshold_basis`（仍 `arithmetic_identity`）· `threshold_review_status`（仍 `not_reviewed`）· `decision.*`（仍 `pending`）· `parameter_mapping.low/base/high`（仍 `null`）· 其余 7 个下标 · `ruling_6b.md` · `OPEN6-TOLERANCE-TABLE/*` · `tolerance_signed.json`（**不创建**）· 五份计划文件 · 封盘 `I-11-A` 任一字节 · 任何 `status`/`decision` 字段。

## ⑥ 红绿变异清单（≥3，先冻结后执行）

| id | 类型 | 变异输入 | **期望**（不符即红） |
|---|---|---|---|
| `g1_real_revert` | **绿（正例）** | 实测件：残差 `154`、`ΣAᵢ=0`、`C1 FAIL`、`B1/B2` 触发、支③ owner 已确认（§三十三）、三条恢复条件**均不出现** | `revert_applied = true`（**按裁定该退的这一支必须真退**），`branch_used = 无法凑平⇒口径不一致(owner-confirmed)` |
| `m1_default_literal_only` | **红（默认/弱化触发 ⇒ 不该退的被退）** | 同一实测件，但 `owner_branch_confirmed = false`（**只认两条字面触发**） | `revert_applied = false`（① 83,161 ≤ 84,477 未超、② 方向一致 ⇒ 字面路径本就不触发）；若判 `true` = 红 |
| `m2_recovery_condition_present` | **红（恢复条件被误判为已满足 ⇒ 反向的红：此处不得退）** | 实测件 + 注入恢复条件之一（`公司披露按金属拆分期末存货千克 = 1,470`） | `revert_applied = false` 且 `recovery_triggered = true`（转 `oracle §3.2` 重评）；若仍判 `true` = 红 |
| `m3_in_cap_closeable` | **红（不该退的被退）** | 铜行实测件（残差 `+1` 吨在 A-6.2 帽内、可凑平、无 owner 支） | `revert_applied = false`；若判 `true` = 红 |

**执行方式**：`revert_eval.py`（本载体内，`python -B` 运行，无 `__pycache__`）逐案独立进程执行，**每案单独记 `rc`**；全案断言通过 ⇒ 汇总 `rc = 0`。变异只在**判定函数**上做，**不触碰任何被保护文件**。

## ⑦ fail-closed · blocked 触发（任一成立即判 `blocked`，给实测）

1. `revert_rule` 落点**须写产品仓**（本工位无产品仓写权）⇒ `blocked`，明写「无写权限」，**禁止任何破坏性替代**；
2. **规则分支定位不到**（找不到 L315 / 找不到 `hypotheses[2]` / `state` 键缺失）⇒ `blocked`；
3. **前像复算不符**（`preimage` 或封盘原件 sha ≠ `f2178768…`，或字节数 ≠ 51,697）⇒ `blocked`；
4. 写后 `json.load` 重解析失败、或出现 BOM/CRLF ⇒ `blocked`。

## ⑧ 本 oracle **不授予**什么（同时是交付自检表）

不解除 `BLOCKED-6b`（`L110` 明定由 owner/编排层在 R2 解决后重判，现 `3 签 1 不签`）· 不解除 `BLOCKED-6a/6c` · 不解除 `OPEN-2/6/11` · **不签 `τ`** · **不代签** · 不放行参数（`low/base/high` 仍 `null`）· **不产生 `ACCEPT`** · **不修订 `revert_rule` 字面** · 不改两半区裁定 · 不改 `threshold_basis`/`threshold_review_status` · 禁 git 写（含 `git status`）· 禁联网 · 禁写五份计划文件。
