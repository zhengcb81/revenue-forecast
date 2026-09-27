# 独立复审报告 — T1-10 / a20260920-01

VERDICT: changes_required

- 复审对象：`execution_runs/T1-10/a20260920-01`（2026-09-20 交付，长期 `review_pending`，复审首次派出）
- 复审者：独立复审工位（N=1），与本卡实现者非同一人；本次为 owner 2026-09-26 裁定的路径 **(a) 补派独立复审**
- 复审日期：2026-09-26
- 判据来源：**回源读卡文**，非转述 —— `OWNER_DECISIONS.md` §13 **T1-10**（TIER-1）、`task_plan.md` Round 57（本卡计划侧交付）、`execution_v2/START_HERE.md`「固定九步执行法」L31-41
- 发现分级规则：**有 P1 ⇒ `changes_required`；否则 `ACCEPT`（可带 P2/P3）**
- 判据纪律：**判据匹配被判定对象的形态** —— 09-20 的 T 系协议卡形态，不用 09-25 口径苛责；同时**不因「缺陷已被 T1-10-FIX 处置」而放松**

---

## 1. 卡文合同（回源原文）

`OWNER_DECISIONS.md:216`（§13 T1-10，TIER-1）：

> **授权立卡修复**（产品 + 计划双侧）：①`claim.basis` 补**枚举校验**；②修正 `union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**注意②已烧进冻结期望**（W1 `union_seconds=2220`）⇒ 修复须同时以**追加式 provenance** 更正期望，**不得回改冻结正文**。

要点拆解（我自己的拆解，非实现者转述）：
- **动作（产品侧）**：①② 两处产品级修复。
- **动作（计划侧）**：② 的冻结期望须以**追加式 provenance** 更正（旧值留档）。
- **验收**：② = 期望已更正 **且** 冻结正文未被回改；① = `claim.basis` 具备能约束输入域的枚举校验。
- **停止/禁止**：不得回改冻结正文（②）；卡内自述不转移 `status`、不代签。

无 `execution_v2/card_T1-10.md`；`dispatch.json` / `model_cards.json` 中 **0 命中**（实测），合同仅存在于 `OWNER_DECISIONS.md` §13 与本卡 `decision.md:10-17` 的逐字引用。

---

## 2. 它实际交付了什么（逐条 + 我实测的字节数/sha256）

attempt 目录 7 个文件（我全量复算）：

| 文件 | 我实测 bytes | 我实测 sha256（前16） | 卡内登记值 | 复算 |
|---|---:|---|---|---|
| `scripts/verify_t1_10.py` | 24335 | `544ae0adb3a96920…` | `544ae0adb3a96920…` | MATCH |
| `t1_10_defect_verification.json` | 12763 | `22ead5c549311ace…` | `22ead5c549311ace…` | MATCH |
| `decision.md` | 14031 | `d7fe3ebb8dcc6868…` | `d7fe3ebb8dcc6868…` | MATCH |
| `append_only_proof_round57.json` | 676 | `c0bc84cfedad7974…` | `c0bc84cfedad7974…`（`handoff.artefacts` 表） | MATCH |
| `handoff.json` | 13153 | `715b5e0bc13a23fc…` | **不自登记（自指）**；`task_plan` 登记 `ed206347b00b86d9…` | **MISMATCH**（见 P2） |
| `run_a.json` / `run_b.json` | 12761 / 12761 | `a8ceba2fc067252a…` / `98c520562dee48b6…` | 卡明示**非交付物、不登记** | 披露属实 |

`handoff.json` 的 `artefacts` 表（卡自称权威表）**4/4 由我独立复算通过**。

交付内容逐条（我读原文，非转述）：

1. **`one_observable_result`**（九步第 1 步的可观察结果）：同一冻结 CLI，批次含 1 个 `basis` 为 list/dict 的 case ⇒ rc=4、**不写任何报告**；同批 `basis` 写成未登记串 ⇒ rc=0、13/13 裁决、仅该 case 被拒。→ **我复算：成立**（见 §4）。
2. **结论 ②**：缺陷② 早已修好且追加式 provenance 已按裁定落地 → **我复算：成立**。
3. **结论 ①**：枚举校验**已加但非全函数**（`BASIS_REGISTRY` 为 `set`，不可哈希值 ⇒ `TypeError` ⇒ `main()` 变 rc=4 且不写报告），并自记 `is_the_residual_a_new_discovery=false`（reviewer P4 已登记、从未闭合）。→ **我复算：成立**。
4. **危害形态**（P-4/P-6）：爆炸半径属「值的形态」且**跨 class**（剥夺裁决而非拒绝主张）。→ **我复算：成立**。
5. **F 段附带发现**（P-9/P-10）：I-14-B 记录的 7 个关键哈希中 2 个只能在 `LF→CRLF` 变换后复算；HEAD blob == 盘上 ⇒ 非篡改、是**字节域未声明**。→ **我复算：成立**（见 §4）。
6. **边界自述**：产品文件 0 / 冻结件写入 0 / 删除 0 / `status` 转移 0 / 代签 0。→ **当前可复算部分成立**（`git diff HEAD --name-only` 非 `.planning` = 0；见 §10）。
7. **移交（2 条，给编排层）**：(i) 立一张继承 I-14-B r2 的修订卡做容器安全写法 + 在 `oracle.md` §11 追加字段类型 rc 归属裁定；(ii) 按 T1-12 ① 在 I-14-B 三载体追加 CRLF 字节域说明。→ (i) 后续由 `T1-10-FIX` + 父落笔 §11.8 执行；**(ii) 至今无人执行**（见 §5）。

**本卡没有交付的东西（对照卡文动作）**：**产品侧 ① 的修复动作本身** —— 无 worktree、无 `changes.diff`、无畸形 `basis` 负例族/负控产物；卡内明写「本卡性质是核验、不改被测件」（`decision.md:141`、`handoff.nature_of_card`）。

---

## 3. 逐项核验表（对照卡文 动作 / 验收 / 停止）

| # | 卡文要求 | 本卡交付 | 我的独立核验 | 结论 |
|---|---|---|---|---|
| A1 | ① 产品侧：`claim.basis` 补枚举校验（能约束输入域） | 声称「校验已存在但**非全函数**」，**未做任何产品侧改动** | 盘上 `iso/natural_window.py:60` `BASIS_REGISTRY`（set）、`:202` 成员测试；我自建探针：list/dict `basis` ⇒ **rc=4 / 不写报告 / 0 裁决**，缺陷**至今在被测件上可复现** | **未达成（P1）** |
| A2 | ② 产品侧：quick_check 不得计入自然观察时长 | 声称已由 I-14-B r2 闭合 | `:174-185` 只由观察阶段构造；我跑全量 34 case：`rc=0 / 34/34`，`W1 union_seconds=1740 accept`、`W2 reject R-TOTAL-AS-OBS` | 达成（状态性要求，前序轮闭合，本卡复算正确） |
| V1 | ② 计划侧：期望须追加式更正、**不得回改冻结正文** | 声称盘上已是该形态 | `expected.W1.computed.union_seconds=1740`、`expected_superseded["W1"]…old=2220`、`pre_image_sha256=3ba2bb1799ae…`、`errata[0]=ERR-I14B-R2-01`；r1 归档件实测 `3ba2bb1799ae…` | 达成 |
| V2 | 本卡不得回改冻结正文 | 自述被核验件写入 0 | I-14-B `oracle.md` 前 26554 B 复算 = `bdd0407ab577ed45…`（= 当时登记值），当前文件 = 前像 + 2376 B 纯后缀（09-24 父落笔 §11.8）⇒ 本卡未动它 | 达成 |
| H1 | 残留须如实登记并移交（计划侧） | `decision.md §7` + `handoff.handoffs[0..1]` | 逐条读原文，移交文本具体、含「须由该卡 reviewer 出具、不可实现者自填」 | 达成 |
| S1 | 停止：不转移 `status`、不代签 | `status=review_pending`、`self_signed=false` | 读 `handoff.json:6-7` | 达成 |
| S2 | 停止：不删任何文件 | `run_a/run_b` 保留并披露 | 两文件在盘、未登记为交付物 | 达成 |
| R1 | 交付登记哈希须可复算 | `artefacts` 表 4/4；`task_plan` 散文另登 2 个哈希 | 表 4/4 MATCH；`task_plan` 的 `handoff`/`append_only` 两值**不复算** | **P2** |
| N1 | 九步载体在位性（本工位按卡要求盘点） | 见 §7 | 缺 `binding.json`/`oracle.md`/`commands.json`/步骤记录 | **P3（形态差异，见 §7）** |

---

## 4. 我的独立复算（不引实现者自述当证据）

### 4.1 核心行为复算（我自建探针，落盘仅在 `%TEMP%`）

复现环境：读只读被测件 `I-14-B/a20260919-01/iso/natural_window.py`（`7fff6f0c1e8ab202…`），输入取自冻结 `harness/cases.r2.json`，探针脚本写在 `%TEMP%\rev_t110_probe\probe.py`，报告写 `%TEMP%`。

| 臂 | 提交 | rc | 报告写出 | 已裁决 | stdout（实测） |
|---|---:|---:|---|---:|---|
| A：3 良构 + 1 个 `basis=["union_of_windows"]` | 4 | **4** | **否** | **0** | `{"ok": false, "error": "internal_error", "detail": "unhashable type: 'list'"}` |
| B：3 良构 + 1 个 `basis="wall_clock"`（对照） | 4 | **0** | 是 | **4** | `{"ok": true, … "case_count": 4 …}` |
| C：1 calendar + 6 window + 1 个 `basis={"k":"v"}` | 8 | **4** | **否** | **0** | `{"ok": false, "error": "internal_error", "detail": "unhashable type: 'dict'"}` |
| 全量 r2 冻结批 | 34 | **0** | 是 | **34** | `W1 accept / union_seconds=1740.0`；`W2 reject / R-TOTAL-AS-OBS / union_seconds=1740.0` |

⇒ 卡的核心命题 **P-3 / P-4 / P-5 / P-6 复算成立**（形态决定爆炸半径、跨 class 连带、串只伤自己）；**A2/V1 复算成立**（quick_check 未被计入，`union=1740` 而非 2220）。

### 4.2 哈希/字节域复算（我实测）

- 被测件 `iso/natural_window.py` = `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`（= 卡登记的 r2 修订）。
- F 段 7 行复算（我全量重做）：

| 文件 | 记录值 | 盘上字节 sha256 | `LF→CRLF` 后 | 判定 |
|---|---|---|---|---|
| `harness/frozen_expectations.r2.json` | `6f814d0af6a8…` | `a24d8ab3444d…` | `6f814d0af6a8…` | **仅 CRLF 域可复算** ✓ |
| `harness/cases.r2.json` | `c00a3a00ffe8…` | `23d89fb27bbd…` | `c00a3a00ffe8…` | **仅 CRLF 域可复算** ✓ |
| `harness/archive/frozen_expectations.r1.json` | `3ba2bb1799ae…` | `3ba2bb1799ae…` | `53964191a890…` | 原样可复算 ✓ |
| `harness/cases.json` | `5d8c459277da…` | `5d8c459277da…` | — | 原样可复算 ✓ |
| `oracle.md`（当时） | `bdd0407ab577…` | 前 26554 B = `bdd0407ab577…` | — | 原样可复算 ✓ |
| `iso/natural_window.py` | `7fff6f0c1e8a…` | `7fff6f0c1e8a…` | — | 原样可复算 ✓ |
| `harness/run_cases.py` | `f2a07d0b85c5…` | `f2a07d0b85c5…` | — | 原样可复算 ✓ |

- **P-10（非篡改）复算**：`git cat-file blob` 取 HEAD blob → `frozen_expectations.r2.json` blob `a24d8ab3444d…` **== 盘上**；`cases.r2.json` blob `23d89fb27bbd…` **== 盘上** ⇒ 内容自提交未变，坏的是「哈希取在哪个字节域」的**声明**。**F 段结论成立。**
- **P-8（oracle §11 当时未答该问）复算**：当前 `oracle.md` = 28930 B / `b1eb5d0cf83dd8f0…`；前 26554 B 复算 = `bdd0407ab577ed45…`（纯后缀追加，可证）。**在前像内** `### 11.` 至 §11 末尾检索 `字段类型 / unhashable / rc 4 / internal_error / isinstance` —— **全部 0 命中**；`### 11.8 rc 归属裁定`（回答该问题的正文）**完全落在 09-24 追加的 2376 B 后缀内**（触发者写明「T1-10-FIX F-3 + review.md:353 提请」）。⇒ **卡在 09-20 的 P-8 声称在交付时点为真**，未被今天的盘面证伪。
- **P-7（夹具潜伏）复算**：`harness/cases.json` 20 条 + `harness/cases.r2.json` 34 条 = 54 条，`claim.basis` 类型仅 `String/Null`，**容器 0 个** ✓。
- **A（无生产实例）复算**：`git ls-files | findstr natural_window`（排除 `.planning/`）= **0**；磁盘全仓（排除 `.planning/`）= **0** ✓。
- **锚点**：`scripts/model_extensions.py` = `9939480b717d5a49…`（与卡一致）；`scripts/model_registry.py` 现盘 `62f864b9ab3f144e…` ≠ 卡记录的 `9ec65295…` —— 归因 `git log`：`5fd82de7 promote(B-6c via MODEL-ORACLE-ALIGN): model_registry re-promotion (62f864b9, I-10-B defect-1 省缺即抛)`，属 **owner 授权的后续晋升**，非本卡改动。

### 4.3 `task_plan.md` 登记值复算（我实测，P2 依据）

- 实盘 `handoff.json` = 13153 B / `715b5e0bc13a23fcf508525f8935c5ce781783dff5187e7d008ff48f7b2271ee`。
- `task_plan.md:714`（Round 57 再补记）登记 = 13153 B / `ed206347b00b86d96629e917a2c33f8054f9e323accc40f2d2d2ab0934501306` ⇒ **哈希不复算**（字节数相同）。
- **等长单点替换取证**：把盘上文本中唯一的 `c0bc84cfedad7974…`（artefacts 表内 append_only 证明的 sha）替换为 `fb7bf6a0a8e9e602…`（`task_plan:714` 登记的值）后重哈希 ⇒ **精确等于 `ed206347…`**。
  ⇒ 登记值是「artefacts 表尚写 `fb7bf6a0…`」的**自洽前像**；此后该表更新为 `c0bc84cf…`（盘上证明件实测即此值），`task_plan` 散文未随之更正。
- `task_plan.md:714` 登记的 `append_only_proof_round57.json = fb7bf6a0…` 亦与盘上 `c0bc84cf…` 不符。
- 卡自述规则：「记录哈希一律以 `handoff.json` 的 `artefacts` 表为权威……本文件的散文数字仅为提示，不得用作比对依据」（`task_plan:713-714`）⇒ **该规则为本卡自设且已披露**，但 `handoff.json` 自身哈希**只有散文这一处登记**，该登记不可复算 ⇒ 记 **P2**。

---

## 5. 与 `T1-10-FIX` 的覆盖关系

`T1-10-FIX/a20260923-01`（合并链第 1 腿、已 `accepted_scoped`，`handoff.json` 26509 B / `e6b9a94a40313b9a…`；`changes.diff` 11534 B / `625ecfe45f3d713a…`）：

| 本卡交付/发现 | T1-10-FIX 是否处置 | 盘面现状（我实测） |
|---|---|---|
| 缺陷① `claim.basis` 枚举非全函数（P-2–P-8） | **✅ 全覆盖**：E1 载体读取 / E2 J16 守卫 / E3 `basis_registered` 三入口，畸形 basis = 干净 per-case 拒绝；RED/GREEN/变异/负控/不变量齐（其 `handoff.proven` 逐条列出） | **修复未落盘**：canonical 被测件仍 `7fff6f0c…`，我的探针**仍复现 rc=4**；修复只存在于 `changes.diff`（其 `handoff` 明写「NOT applied by anyone」） |
| 缺陷② quick_check 计入（P-1） | 不需处置（其 `mapping.defect_2_state` = untouched、区段不相交） | 已闭合（§4.1/§4.2 复算） |
| **F 段 CRLF 哈希域（P-9/P-10）** | **❌ 未处置**：仅在 `decision.md:123` 作为「同族教训」被引用一次 | **❌ 移交也未执行**：I-14-B `binding.json`/`commands.json`/`handoff.json` 中 `CRLF`/`autocrlf` **0 命中**；`23d89fb2` 全计划只出现在本卡自己的 `task_plan.md:694/703` |
| 移交(i) 新修订卡（容器安全写法） | ✅ 由 FIX 交付 | 未 apply（同上） |
| 移交(i) `oracle.md` §11 字段类型 rc 归属 | ✅ 由 **FIX 的独立复审者**裁 F-3 → 父 09-24 落笔 `### 11.8`（我复算：纯后缀、前像 `bdd0407a…` 完好） | 已落盘 |
| FIX 自己新增的 F-1/F-2/F-3/P4 容器族 | 非本卡发现（FIX `unproven` 自列，已路由 T1-F2-FIX / T1-F3-FIX） | 不计入本卡 |

**结论**：FIX **覆盖了本卡缺陷①与移交(i)的全部**，**未触及本卡 F 段（哈希字节域）及其移交(ii)**；本卡交付中 **FIX 未触及的问题 = F 段 + 其移交至今未执行**（另见 P2/P3）。

---

## 6. 「双向无指针」的独立验证

我用**大小写敏感 + 逐字**检索（**不用**模糊 `Contains`，以避免登记册已记录的第 17 起假阳性）：

**方向 1 — `T1-10/a20260920-01` 全树（7 文件）：**
- 字面 `T1-10-FIX` ⇒ **0**
- 字面 `a20260923` ⇒ **0**
- 字面 `superseded_by` ⇒ **0**
- `"next…":` 键 ⇒ **0**（无 `next_action`/`next_*`；但**存在 `handoffs[]` 数组 2 条，`to: "orchestration layer"`**，是移交条目、非状态指针）

**方向 2 — `T1-10-FIX/a20260923-01/handoff.json`：**
- 字面 `a20260920` ⇒ **0**
- 字面 `/T1-10/` ⇒ **0**
- ⇒ **handoff ↔ handoff 双向无指针，成立**（与 §136-F 实测一致）。

**⚠️ 但在 attempt 粒度上，登记册的「T1-10-FIX 也全文不提 T1-10/a20260920」过宽（我独立证伪）：**
- `T1-10-FIX/binding.json:27-29` 明确以**只读输入 pin** 引用：`T1-10/a20260920-01/decision.md`（`d7fe3ebb…`）、`…/scripts/verify_t1_10.py`（`544ae0ad…`）、`…/t1_10_defect_verification.json`（`22ead5c5…`）—— 三个 sha 与我在本卡实测**逐一相等**。
- `T1-10-FIX/oracle.md:20`：「探针形状逐字取自 **T1-10 的块**：`T1-10/a20260920-01/scripts/verify_t1_10.py` L99–116」。
- 性质：**只读引用（输入依赖），不是取代/关闭指针**（无 `superseded_by`、无状态指针、handoff 内 0 命中）。
- ⇒ 精确表述应为：**「两卡 handoff 互无指针；FIX 侧 binding/oracle 单向引用本卡为只读输入」**。这是**登记册表述**问题（同族：以偏概全），**不是本卡交付缺陷**，记为给父的观察。

---

## 7. 九步协议在位性（缺什么如实列出）

九步原文：`execution_v2/START_HERE.md:31-41`。本 attempt 载体盘点：

| 步 | 要求载体 | 本 attempt | 判定 |
|---|---|---|---|
| 1 领取 | card-id/parent/实现者/独立 reviewer + 一个可观察结果 | `handoff.card/attempt/authority` + `one_observable_result` 齐；**实现者/独立 reviewer 姓名缺** | 部分在位 |
| 2 绑定 | `binding.json`（路径/sha/argv/允许写目录/输入 hash） | **缺文件**；被测件与输入 sha 记于 `handoff.subject` + 证据 JSON；**argv 未以 binding 形式登记** | **缺** |
| 3 读证据 | 源文件/现行测试/原反例 | `decision.md §3-§5` 逐行带行号引用（`:60/:202/:174-185/:468-473`）+ `review.md` P4 逐字引用 | 在位 |
| 4 冻结预期 | `oracle.md` | **缺文件**（核验卡无预期冻结载体；`t1_10_defect_verification.json` 承载 `propositions` 10 条 + `overall=PASS`，非 oracle 形态） | **缺** |
| 5 运行前检查 | `commands.json` | **缺文件**；证据 JSON 内含逐臂 rc/stdout/报告写出记录 | **缺（代偿存在）** |
| 6 最小修改 | diff | 不适用（本卡声明零改动；见 P1：正是「该改未改」） | n/a |
| 7 修改后检查 | 同输入重跑 | 证据 + 自述「连跑 4 次同哈希 `22ead5c5…`」 | 在位（自述部分 unverified） |
| 8 交审 | diff/完整输出/未满足项 | `handoff` + `decision.md §6-§7`（未满足项显式列出） | 在位 |
| 9 接续 | reviewer 接受后更新范围/下一卡 | **无 `review.md`、无 `nine_step` 键、无 `next_action` 键**；`handoffs[]` 2 条给编排层 | 待本次复审 |

**形态对照（不用 09-25 口径苛责）**：同日 T 系卡（`T1-13/14/15/16/17/18/20/21/22/23…`）载体系 `decision.md + handoff.json + verify_*.py + 证据 JSON (+ review.md 后由 D9 批次补建)`，**同样无 `binding.json`/`oracle.md`/`commands.json`**，且**同日 T 卡 `handoff` 无一含 `nine_step` 键**（`nine_step` 键最早见 09-22 之后的卡）。`T1-6`（同日）因执行了产品改动而带 `binding/commands/changes.diff`。
⇒ 缺载体**按形态记为 P3**，不作阻断；但「九步可核载体缺 2/4/5/9」如实记录。

---

## 8. 发现分级

### P1（阻断）

**P1-1 卡文授权的产品侧修复①未在本卡交付。**
- 卡文动作（§13 T1-10）含产品侧 ①「`claim.basis` 补枚举校验」；本卡交付为**核验 + 登记 + 移交**（`nature_of_card` 明写「does NOT modify any frozen artefact」），**无 worktree、无 `changes.diff`、无畸形 `basis` 负例族与负控产物**。
- 至本次复审时点，**缺陷在 canonical 被测件上仍可复现**（我自建探针：list/dict `basis` ⇒ rc=4、0 裁决、不写报告），修复**仅存在于 `T1-10-FIX` 的 `changes.diff`（11534 B / `625ecfe4…`）且未被 apply**。
- 本卡给出的三条不修理由经我复核**不足以支撑整体推迟**：
  1. 「r2 冻结件、改须重冻（T1-11 互锁）」—— T1-11 禁的是**回改冻结正文与重冻**，不禁**卡内 worktree + changes.diff**；**同日 T 系卡即有此形态**（`T1-6/changes.diff`、`T1-13/t13_changes.diff`、`T1-19/t19_changes.diff`），`T1-10-FIX` 也正是以该形态交付。
  2. 「`oracle.md` §11 口径属 reviewer」—— 该口径只约束**oracle 正文**，不阻断代码修复；`T1-10-FIX` 即**先交代码、后由其复审者裁 F-3**。
  3. 「本卡性质是核验」—— 这是**卡自设的性质**，与卡文「授权立卡修复（产品 + 计划双侧）」的动作项不一致；`handoffs[0]` 请求的「授权一张新修订卡」**正是本卡已持有的授权**。
- **不因 T1-10-FIX 已 accepted 而放松**：FIX 是另一张卡的交付（其 `handoff` 首个 `status_authority.authority_note` 原文："this card is the 立修卡 the block allows; it does NOT self-close T1-10 - closure requires the independent acceptance the block names"）；且修复至今未落盘。
- 与既有独立裁定**一致**：`M-T-REVIEW/a20260923-01`（N=1）对本卡的裁决即 `changes_required`，理由同为「修复①未闭合、校验非全函数」。
- **边界**：若 owner 另裁「本卡义务形态 = 特征化 + 立卡（`T1-22` 的 `is_a_fix=false / why_not_a_fix=the ruling authorises carding` 形态）」，则本 P1 可由**同形态门读法例外**（§二十四式）豁免 —— 该裁量**属 owner，不属复审者**；我按卡文动作项如实分级。

### P2（非阻断，须登记更正）

**P2-1 `task_plan.md` Round 57 登记的两个 sha256 不可复算。**
- `handoff.json`：登记 `ed206347b00b86d9…` vs 实盘 `715b5e0bc13a23fc…`（同为 13153 B）。
- `append_only_proof_round57.json`：登记 `fb7bf6a0a8e9e602…` vs 实盘 `c0bc84cfedad7974…`（同为 676 B）。
- 成因已由我取证闭合（等长单点替换，见 §4.3），非内容篡改；`handoff.artefacts` 表 4/4 正确。
- 影响：`handoff.json` 自身不登记自哈希 ⇒ **该卡主载体的唯一登记位不可复算**。
- 建议处置（不属我执行）：追加式勘误一行，登记实盘 `715b5e0bc13a23fcf508525f8935c5ce781783dff5187e7d008ff48f7b2271ee`，原值不回改。

### P3（观察）

**P3-1 本卡三个 JSON 载体为 CRLF 工作副本域，git blob（LF）哈希不同，卡未声明字节域。**
- `handoff.json` 盘 13153 B（CR=179）/ blob `82e15a7a0e40…`（12974 B）；`t1_10_defect_verification.json` 盘 12763 B（CR=288）/ blob `6116e32a03bd…`（12475 B）；`append_only_proof_round57.json` 盘 676 B（CR=18）/ blob `a2ba612b3738…`（658 B）。`decision.md` 与 `verify_t1_10.py` 为 LF-only，blob == 盘。
- 卡的登记值与**盘上（CRLF）**一致，日常复算可用；但从 **git blob 复算会不等** —— 恰是本卡自己立的 F 段同族（「哈希取在哪个字节域没写明」），本卡未对自己的登记做同样声明。全文件无 BOM。

**P3-2 九步载体缺 2/4/5/9**（`binding.json`/`oracle.md`/`commands.json`/步骤或 `next_action` 记录）—— 见 §7，按同日 T 卡形态记为形态差异，不阻断。

**P3-3 `nature_of_card` 自称 `verification + residual closure`**，但本卡实际**未闭合任何残留**（其 `conclusion.defect_1` 亦如实写明未闭合）—— 措辞与事实不一致的轻微自述瑕疵，披露本身诚实。

**（非本卡）给父的登记册观察**：§136-F 的「`T1-10-FIX` 也全文不提 `T1-10/a20260920`」只在 **handoff 粒度**成立；attempt 粒度上 FIX 的 `binding.json:27-29` 与 `oracle.md:20` 明确引用本卡为只读输入（sha 三项逐一相符）。

---

## 9. unverified（如实记录）

1. **未复跑 `scripts/verify_t1_10.py` 本身**：其 `__file__` 路径断言要求真实仓库结构，且会在 attempt 内重写 `t1_10_defect_verification.json` ⇒ 违反「只写两文件」。**替代**：自建 `%TEMP%` 探针独立复算核心行为（§4.1）；脚本正文只作静态阅读。
2. **证据 JSON 的 4 次幂等同哈希自述**（`22ead5c5…` 连跑 4 次）—— 未复现；我只能验证该文件现存字节与登记一致。
3. **09-20 当时的瞬时边界**（产品树 0 写入、锚点当时值）无法回溯；我只能复算**当前** `git diff HEAD --name-only` 非 `.planning` = 0，以及 `model_registry.py` 的漂移归因于 `git log 5fd82de7`。
4. `run_a.json` / `run_b.json` 的生成过程（卡已披露为幂等调试遗留、非交付物）—— 未验证。
5. `M-T-REVIEW` 22 卡裁定的原始载体（`reviews/T1_rulings.md` / `acceptance_rulings.md`）—— 我只读了 `landing_package/t1_review_flips.md` 转录块，**未**回源到其原始裁决文件。
6. `REMEDIATION_REGISTER` §136-F 的父侧「假阳性第 17 起」自述 —— 我只验证结论方向（逐字检索），未复算父当时那条 `Contains('supersede')` 的执行现场。

---

## 10. 边界声明（我做了什么 / 没做什么）

**我写入的文件（仅两个，均为新建）**：
- `execution_runs/T1-10/a20260920-01/reviewer_report.md`（本文件）
- `execution_runs/T1-10/a20260920-01/reviewer_report.sha256`

**我没做的事**：
- 未改本 attempt 任何既有字节（7 个既有文件 0 字节改动）；未改 `handoff.json`/`status`/`handoff` 字段；**未替本卡落定**；未代签任何 `accepted`。
- 未写生产树、未写 `I-14-B`、未写 `T1-10-FIX`、未写登记册/`task_plan`/`OWNER_DECISIONS`。
- **未执行任何写态 git 命令**；**未用 `git status`**；只读命令限于 `git diff HEAD --name-only` / `ls-files` / `ls-tree` / `cat-file` / `rev-parse` / `log`。
- **未联网**。
- 测试仅在 `%TEMP%\rev_t110_probe\` 隔离副本运行；**沙箱（`.planning` 内受限目录）未被我写入**。
- 未裁定 §二十四式的门读法例外（该裁量属 owner）。

**收尾实测**：`git -c core.quotepath=false diff HEAD --name-only` ⇒ 共 3829 条、**全部 `.planning/*`**，**非 `.planning` = 0**。
