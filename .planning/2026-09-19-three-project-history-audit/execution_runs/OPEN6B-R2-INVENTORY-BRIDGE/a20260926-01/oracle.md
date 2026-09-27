# `OPEN6B-R2-INVENTORY-BRIDGE` · 判据（Oracle，**先冻结**）

- 工位：`evidence_acquirer_r2`（**证据取证工位，非签署人**）
- 载体（新建、唯一写入面）：`execution_runs/OPEN6B-R2-INVENTORY-BRIDGE/a20260926-01/`
- 上游依据（**本工位已逐字回源**，不采信派单转述）：`execution_runs/OPEN6B-TOLERANCE-RULING/a20260926-01/ruling_6b.md`
- 冻结时点：**2026-09-26T13:24Z（门 0 之后、任何取证动作之前）**
- 一句话：本 oracle 只定义「**什么算存货桥闭合证据**」「**什么算闭合**」「**什么算 blocked**」「**变异清单**」；**不含、也不产生任何 τ 建议值以外的签署权**。

---

## ① 授权（逐字回源，`ruling_6b.md`）

| 项 | 逐字原文 | 出处 |
|---|---|---|
| R2 判定 | `R2 \| H-CN-ZIJIN-VOL-03 \| 无 \| 1 吨 / 1 千克 \| **154 千克**（铜+1、锌0、银−1、金+154） \| **\`NOT_SIGNED\`** \| insufficient_evidence` | `ruling_6b.md` **L104** |
| Q3 结论 | `### 2.3 Q3 · R2（\`H-CN-ZIJIN-VOL-03\`）是否补登数值容差 → **不补登，\`NOT_SIGNED (insufficient_evidence)\`**` | **L66** |
| 阻断实测 | `R2 金   1,734 +  82,743 −  83,161 =  1,316 ;  期末  1,470 ⇒ Δ = +154 千克` | **L148**（L132–L150 自算块） |
| 两带交集为空 | `可容带 = 0 < τ ≤ 1 单位` / `覆盖实测所需带 = τ ≥ 154 千克` / `两带交集为空` | **L79–L81** |
| **恢复路径 (a)（本卡授权原文）** | `(a) 取得**存货桥闭合证据**（在产品 / 在途 / 寄售 / 并购范围明细，OPEN-11 R6 条件2）解释 154 千克，恒等式按新口径重述后，在 0 < τ ≤ 1 单位内按 A-6.3(2) 选基础签署` | **L95**（L94–L97 三路径块） |
| 状态归属 | `整条 BLOCKED-6b 的状态由 owner / 编排层在 R2 解决后重判` | **L110** |
| 前置条件2原文 | `2. 存货桥闭合证据（在产品/在途/寄售、并购范围；state_reason L244 点名；R3 实测差 154 千克尚未解释）；` | `I11A-OPEN11-IND/a20260924-01/ruling.md` **L192** |
| 口径来源 | `观测 scope = 控股并表矿山，不含非控股企业`；`observation.raw_value = …库存 1,470 千克；产销量表说明：本表不含非控股企业相关数据` | `I-11-A/…/hypotheses.json` `H-CN-ZIJIN-VOL-03.observation` |
| 结构性候选 | `falsifier_candidates[0] = 并购范围变化`；`[1] = 在途/寄售库存`；`alternative_explanations[0] = 本期销量高于产量主要来自并购标的的期初库存` | 同上 |
| 网络口径 | `允许 web_search/web_fetch 取证（专家 reviewer 职权），但每条外部证据必须落 provenance.json（URL + 取回 UTC + 原文引文 + 快照 sha）；外部来源不得冒充本地可核事实` | `progress.md` **L1244** |

**本工位不做**：不签 `τ`、不写 `tolerance_signed.json`、不改 `ruling_6b.md`、不产生 `ACCEPT`、不解除 `BLOCKED-6b/6a/6c`、不改 `threshold_basis` / `threshold_review_status`、不执行 (c) 的 `revert_rule` 写入、不代 owner 修订 A-6.2。

---

## ② 门 0 · 目标目录真实写探针（**原始输出，逐字**）

> 纪律 16/17：**不采信父代理的探针**，本工位在**自己的目标目录**内重做「建临时文件 → 回读 → 删除」三步。命令 = `pwsh` 内联（`New-Item` → `WriteAllText` → `ReadAllText` → `Get-FileHash` → `Remove-Item`）。

```
== [1] mkdir ==
created: C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\OPEN6B-R2-INVENTORY-BRIDGE\a20260926-01
== [2] write ==
write OK bytes=92
== [3] read back ==
readback: GATE0-PROBE a20260926-01 utc=2026-09-26T13:24:43Z nonce=1fa5aee7-265f-4aee-8021-b5a22dd47ceb
readback_equals_written: True
== [4] sha256 ==
sha256: 788dfc9fb4be4a93061c7b0907328a48a61015fab0abab275d22e5241ee79392
== [5] delete ==
probe_exists_after_delete: False
== GATE0 RESULT: write=True read=True delete=True ==
```

- **`gate0_passed = true`**（三步全成功；探针文件已删除，不留残迹）。
- 任一步失败 ⇒ 立即停手报 `blocked`、明写「无写权限」，**禁止任何破坏性替代**（`git apply` / `>` 重定向 / 删后重写 一律禁用 —— 教训见 `findings` Round 115）。**本次未触发该分支。**

**基线（写入前自算）**：`git -c core.quotepath=false diff HEAD --name-only` ⇒ 总 3830 行、**非 `.planning` = 0**。

---

## ③ 闭合判据（什么算「闭合」）

### 3.1 恒等式与重述口径

- **原口径（未闭合）**：`期末库存量 = 期初库存量 + 生产量 − 销售量 + ε`，四产品实测 `ε = {铜 +1 吨, 锌 0 吨, 银 −1 千克, 金 +154 千克}`（`ruling_6b.md` L147–L150，本工位**复算复核**后再用）。
- **新口径（路径 (a) 要求的重述）**：`期末 = 期初 + 产量 − 销量 + Σᵢ Aᵢ`，其中每个 `Aᵢ` 是一条**存货桥调整项**，且**必须给出千克（或吨→千克可换算）数量**与来源锚。

### 3.2 闭合的**充分必要**条件（五条同时成立，缺一即不闭合）

| # | 判据 | 说明 |
|---|---|---|
| **C1** | **可量化** | 每条调整项 `Aᵢ` 都有**数量**（`kg` 或 `t`，显式单位）；只有定性叙述（「并购并表导致口径变化」）**不算** |
| **C2** | **来源可核** | 每条 `Aᵢ` 满足 §④ 的证据分级；本地可核件须带 `file + 页/行锚 + 逐字引文 + sha256`；外部件须带 provenance **四件**（URL + 取回 UTC + 原文引文 + 快照 sha256）且标 `external_retrieval_not_local` |
| **C3** | **方向正确** | 调整项必须**解释 `+154`（实际期末高于桥值）**，即净额为**正**；反号项不得与正号项对冲后凑数（对冲须各自有独立来源） |
| **C4** | **残差进帽** | 重述后 `residual_new = 期末 − (期初 + 产量 − 销量 + ΣAᵢ)`，须 `\|residual_new\| ≤ 1 千克`（= A-6.2 上限，`g = 1 千克`）。等价地 `\|154 − ΣAᵢ\| ≤ 1` |
| **C5** | **口径同集** | 调整项与产销量表**同一资产集口径**（控股并表矿山、不含非控股企业）；若某项本质是「口径外资产」，须显式写成**口径重述**（把期初/期末或产量/销量换到新集合）而非塞进 `Aᵢ` 数字 |

**闭合判定**：`bridge_closed = C1 ∧ C2 ∧ C3 ∧ C4 ∧ C5 = true`。
**闭合值**：`residual_explained_kg = ΣAᵢ`（`int`，千克；铜/锌按 1000 换算后并入）。`handoff.residual_explained_kg` 在未闭合时 = **`null`**（**NE-3 纪律：不以 0 或估计值代填**）。

### 3.3 建议基础（**仅当闭合成立才允许给**）

- 闭合 ⇒ 按路径 (a) 原文，`suggested_tau_basis` 必须落在 `0 < τ ≤ 1 单位`，且按 **A-6.3(2)** 四类基础之一给出**建议**（本工位**只给建议，不签**）：
  - 可选基础：A-6.3(2)(i) **来源披露舍入粒度**（`g = 1 千克`，与 R1/R3/R4 同构）；或 A-6.3(2)(ii) **同口径历史离散**（四产品两期实测 `max|ε|` 上界）。
  - **禁止**建议任何 `τ > 1 单位`（那属路径 (b)，须 owner 修订 A-6.2）。
- 未闭合 ⇒ `suggested_tau_basis = null`，并**明示下一步走 (b) 还是 (c)**（判据见 §⑤）。

---

## ④ 「什么算存货桥证据」（证据分级）

### 4.1 四条线（路径 (a) 与 OPEN-11 R6 条件2 点名）

| 线 | 合格证据形态（**必须至少能给出数量**） | 常见不合格形态 |
|---|---|---|
| **L1 在产品 / 在产品结转** | 存货附注按类别的**数量或金额**（原材料/在产品/库存商品/发出商品），或产销量表表注中的口径说明 | 只有金额、无法换算为千克且公司未披露单位重量/含量 |
| **L2 在途** | 「发出商品」「在途物资」明细、交付条款（FOB/CIF）说明、期末在途量 | 只有会计科目名，无量 |
| **L3 寄售** | 「寄售」库存披露（矿山/冶炼厂/交易所托管量） | 无 |
| **L4 并购范围** | **交割日、并表起始时点、取得的存货（收购日公允价值）数量或金额**、并表范围变更表、`本表不含非控股企业` 口径注 | 只有交易金额/股权比例，无存货量 |

### 4.2 证据等级（沿用会计面 E1/E2 分级与 `progress.md` L1244）

| 等级 | 定义 | 可否用于闭合 |
|---|---|---|
| **L-LOCAL** | 本地盘上可核原件（`company-wiki/.../annual/*.pdf` 或本计划内 extract），带 sha256 + 页锚 + 逐字引文 | **可** |
| **E1-EXT** | 外部取回，**四件齐全**（URL + 取回 UTC + 逐字引文 + 快照 sha256） | **可作线索与佐证**；单独承重须同时满足四件，且**不得标称本地可核** |
| **E2-EXT** | 外部取回但四件不全（如 `sha256 = null`、无正文） | **不可**用于 C1/C2 |
| **QUAL** | 仅定性、无量 | **不可**（不满足 C1） |

**外部证据落地纪律**：凡动用 `web_search`/`web_fetch` ⇒ `provenance.json` **必落**（本目录内），四件缺一即降级为 E2。

### 4.3 排除项（**明确不算**存货桥证据）

1. **摘要口径数**（如「矿山产金 72,938 千克」的经营摘要）—— OPEN-11 已裁其口径 ≠ 产销量表口径（差 4,663 千克），**混用即口径错配**；
2. **权益产量**（含联营合营）—— `double_count_check` 明禁与产销量表控股口径相加；
3. **冶炼/加工环节的金额型存货**（无重量换算依据）—— 除非同一文件给出单位重量或含量；
4. **本工位自己的算术** —— 复算是**核验**，不是**证据**；`Aᵢ` 必须有外部于本计算的来源。

---

## ⑤ `blocked` 触发（合格结果，不许造绿样）

判 `blocked`（产出 `not_closed.json`）当且仅当**任一**成立：

| # | 触发 | 附带要求 |
|---|---|---|
| **B1** | 四条线查完，`ΣAᵢ`（仅计满足 C1–C3 的项）与 154 的差 `\|154 − ΣAᵢ\| > 1 千克` | 须**逐线**写明「查到什么、各差多少」 |
| **B2** | 找到的证据**全部为 QUAL 级**（只有定性，无量） | 同上 |
| **B3** | 找到量但属 §4.3 排除项（口径错配 / 权益口径 / 无换算依据） | 同上 |
| **B4** | 任一条线**根本查不到**（本地语料无该附注 / 外部取回失败） | 如实登记失败，**不得据检索失败反推「不存在」** |

**下一步指向判据（写进 `not_closed.json` 与报告）**：
- 若证据显示**残差必须由 `>1 千克` 的真实结构性差承担、且无法在同口径内重述** ⇒ 建议 **(b)**（owner 修订 A-6.2）；
- 若证据显示**披露根本不提供可量化存货明细、差额属不可量化结构差** ⇒ 建议 **(c)**（退 `unquantified`，写入归实现者/编排层，**本工位不执行**）。
- 两者可同时提示，但须**给出优先级与理由**；**不得**由本工位代选、代写。

---

## ⑥ 变异清单（红绿判别力，交付前跑）

**判据实现** `closes(items)` = C1 ∧ C2 ∧ C3 ∧ C4 ∧ C5（§3.2，`python -c` 内联实现，不落盘脚本）。

| 变异 | 构造 | 期望 | rc 含义 |
|---|---|---|---|
| **绿 `g1_real_bundle`** | 满足五条的真实项（`ΣAᵢ = 154 ± 1`，带完整锚） | **闭合 = true** | 绿须通过 |
| `m1_qualitative_only` | 只有「并购并表导致口径变化」，无量 | **false**（C1 失败） | rc=0 才算检出 |
| `m2_unanchored_number` | 有 `154 千克` 但无文件/页锚/引文/sha | **false**（C2 失败） | rc=0 |
| `m3_rounding_scale` | 只有舍入级 `0.3088 千克`（R3 下界证据） | **false**（C4 失败，`\|154−0.3\|>1`） | rc=0 |
| `m4_external_no_provenance` | 外部件缺 URL 或缺 sha256（E2） | **false**（C2 失败） | rc=0 |
| `m5_wrong_direction` | 项为 `−154 千克` | **false**（C3 失败） | rc=0 |
| `m6_scope_mismatch` | 项来自摘要口径（与表口径差 4,663 千克族） | **false**（C5 失败） | rc=0 |
| `m7_short_by_12kg` | `ΣAᵢ = 142`（差 12） | **false**（C4 失败） | rc=0 |

**合格**：绿 `closes = true`，7 个红变异全部 `closes = false`（`ALL_MUTANTS_DETECTED = true`）。
**不合格处置**：判据不足 ⇒ 修 `closes` 实现后重跑；**不得**改期望值迁就实现。

---

## ⑦ 写入面与禁止项（自检用）

- **只写**本目录：`oracle.md` / `inventory_bridge.json` 或 `not_closed.json` / `provenance.json`（如用外部）/ `ruling_r2_path_a.md` / `handoff.json`。
- **产品仓（`C:\Users\郑曾波\Projects\company-wiki`）只读**；`pdftotext` / PyMuPDF **只读取文、输出只落本目录**；若须 filing-fetch 写产品仓 ⇒ 先过门 0 并在 `handoff` 登记新文件路径与 sha（本卡**预计不触发**）。
- **零 git 写**；**禁 `git status`**；收尾用 `git -c core.quotepath=false diff HEAD --name-only` 计数（非 `.planning` 须 = 0）。
- **禁碰** `.planning` 内他卡与封盘 `I-11-A` / `OPEN6-TOLERANCE-*` / `BLOCKED6C-*` / `OPEN6H2-*`。
- **不授予**：`signed_by_this_station = false`、`releases_nothing = true`；`BLOCKED-6b`、`BLOCKED-6a/6c`、`OPEN-6`、`OPEN-2`、参数放行、`threshold_basis`、`threshold_review_status` 一律不动。
