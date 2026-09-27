# T1-10 / a20260920-01 复审裁决落定（review.md）

> **`Test-Path` 断言（本文件创建前实测）：`False`** —— 本文件由 carrier-landing 簿记 pass **新建**；创建前本 attempt 内**没有** `review.md`（当时 attempt 根恰为 9 个文件：7 个既有交付文件 + `reviewer_report.md` + `reviewer_report.sha256`）。
> 同批断言：`Test-Path <attempt>\evidence` = **`False`**、`Test-Path <attempt>\evidence\T1-10\qualification.json` = **`False`** —— 目录与文件一并新建。
> **本文件只转录，不产生新裁决、不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
> 转录者 = carrier-landing 簿记执行者（与本卡实现者、复审者均非同一人）；本 pass 未重跑任何命令、未联网、未跑任何测试、未执行任何 git 写操作、**未使用 `git status`**。
> 字节域声明（P3-1 同族，本 pass 主动声明自己写的每个文件）：本文件 = **UTF-8 without BOM、LF-only（CR=0）、单尾 LF**；`handoff.json` 保持其既有 **CRLF** 域（CR=537、538 行）不变；`evidence/T1-10/qualification.json` = UTF-8 without BOM、LF-only。

---

## 0. 裁决来源（唯一权威 = 复审报告载体，全程只读）

| 项 | 值 |
|---|---|
| **当前裁决 carrier（唯一权威）** | `reviewer_report.md`（本 attempt 内，本 pass 只读、写入 0 字节） |
| 字节 | **25115 B** |
| sha256（本 pass 自算） | **`598f55d5cbd638f62d8775d06652b5010c33e1c465e53f55b34ceb3175b0370d`**（对盘上 25115 字节重算；与侧车钉值一致） |
| 总行数 | **246 行**（LF-only、CR=0、LF=246、单尾 LF） |
| 编码 | UTF-8 without BOM（首三字节 `23 20 E7` = `# `） |
| **裁决行（本 pass 自行定位）** | 第 **3** 行；字节区 **[47, 72]**（0-based、含行尾 LF，**26 B**）；该行 sha256 `501cc91c3dc9566eeb7032d7c8aa2faccb5b68a41bf1582d848c4193f32d9488`；仅文本 [47, 71] / 25 B / `3edab02acc91a428984c76b7e09defaeac09ea32ad3fd4a317413f11ec8d0db0` |
| **裁决行文本** | **`VERDICT: changes_required`** |
| 定位方法 | 本 pass 对载体字节做**逐行扫描**（首个以 `VERDICT:` 起始的行），得到 L3，随后按 sha256 状态重算字节区 —— 行号与字节区均为**本 pass 实测**，非照抄派单 |
| 分级规则（L9 逐字） | - 发现分级规则：**有 P1 ⇒ `changes_required`；否则 `ACCEPT`（可带 P2/P3）** （字节区 [593, 685] / 93 B / `d1ac845cfd9267c25d78447de27dc0f43e6f6146591c11e86e7bc8784d1a6d72`；本 pass 实测，非照抄） |
| **计数** | **P1 = 1（P1-1）/ P2 = 1（P2-1）/ P3 = 3（P3-1、P3-2、P3-3）**（报告 §8；其末段标注「（非本卡）给父的登记册观察」是对父的观察，**不计入本卡发现**） |
| 复审日期 | 2026-09-26（报告 L7）；路径 = owner 2026-09-26 裁定的 **(a) 补派独立复审**（报告 L6） |
| 侧车 | `reviewer_report.sha256`，**85 B**，自身 sha256 `02a403986819d520858b22af978ee267f2579827a876b74318ccbc2865146534`；内容（含尾 LF）= `598f55d5cbd638f62d8775d06652b5010c33e1c465e53f55b34ceb3175b0370d  reviewer_report.md` —— 与本 pass 自算 sha **一致**；本 pass 写入 **0 字节** |
| 复审者 | 独立复审工位（N=1），**与本卡实现者非同一人**（报告 L5-6）；其在本 attempt 只写了报告 + 侧车两个文件（报告 §10） |

字节区定义（与本计划既往落定一致）：0-based 字节偏移，按文件处于上述 sha256 状态时计算；**单行区含行尾 LF**；**多行区含内部 LF、不含末尾 LF**。

本 pass 复算并核验（sha 全部与上表一致，逐区断言通过）：§8 发现分级 [18307,22746] / 4440 B / `db62d5d9…`、P1-1 [18347,20580] / 2234 B / `8efa9014…`、P1-1 边界行 L196 [20258,20581] / 324 B / `1e41ae1e…`、P2-1 [20624,21311] / 688 B / `09507e6a…`、P3-1 [21334,22045] / 712 B / `dba4b51d…`、P3-2 [22048,22230] / 183 B / `21c9d8cd…`、P3-3 [22232,22473] / 242 B / `aa6003f7…`、§9 unverified [22754,24009] / 1256 B / `fbfbb03f…`、其 6 个条目 [22790,24009] / 1220 B / `707bf3df…`、L55「本卡没有交付的东西」[4705,4999] / 295 B / `3ff5bc7d…`。

---

## 1. 裁决转录（status 面）

```
review_pending  --(复审报告 L3: VERDICT: changes_required)-->  changes_required
```

| 项 | 值 |
|---|---|
| status | `review_pending` → **`changes_required`**（按报告原文，未归一化、未软化） |
| status_before | `review_pending` |
| status_transition | `review_pending -> changes_required` |
| status_history | **2 条**：① `review_pending`（2026-09-20 交付时，本卡实现者，self_signed=false、status_transitions=0）② `changes_required`（2026-09-26，复审者 L3 原文，簿记转录） |
| 落定面 | `handoff.json` 状态面（本文件）+ `evidence/T1-10/qualification.json` —— 三处写入面见 §5 |
| **P1 是否阻断** | **是**。按 L9 规则，有 P1 ⇒ `changes_required`；**本卡未被接受、未被关闭** |

**这不是 ACCEPT**：`changes_required` 不等于 accepted；本 pass 不解除任何 `OPEN-*` / `BLOCKED-*` 条目，不裁定门读法例外，不晋升任何 diff，不代签。

---

## 2. 必须随卡携带的五条发现（逐字，不得弱化）

### P1-1 — 阻断（P1）

位置：`reviewer_report.md` **L187–196**，字节区 **[18347, 20580]** / **2234 B** / `8efa9014f2c096b97b554c9ca9be13c92179ae8f334739cc93403812e53ec990`

```
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
```

> **逐字转录，不弱化、不关闭、不降级。** 本 pass 对 P1-1 的处置 = 原样携带（`handoff.json.carried_findings` 同步镜像）。

### P2-1 — 非阻断，须登记更正（P2）

位置：`reviewer_report.md` **L200–205**，字节区 **[20624, 21311]** / **688 B** / `09507e6a6e631f07851cead957e65a5d52ca4e8df9ce02eebb9417efb0734948`

```
**P2-1 `task_plan.md` Round 57 登记的两个 sha256 不可复算。**
- `handoff.json`：登记 `ed206347b00b86d9…` vs 实盘 `715b5e0bc13a23fc…`（同为 13153 B）。
- `append_only_proof_round57.json`：登记 `fb7bf6a0a8e9e602…` vs 实盘 `c0bc84cfedad7974…`（同为 676 B）。
- 成因已由我取证闭合（等长单点替换，见 §4.3），非内容篡改；`handoff.artefacts` 表 4/4 正确。
- 影响：`handoff.json` 自身不登记自哈希 ⇒ **该卡主载体的唯一登记位不可复算**。
- 建议处置（不属我执行）：追加式勘误一行，登记实盘 `715b5e0bc13a23fcf508525f8935c5ce781783dff5187e7d008ff48f7b2271ee`，原值不回改。
```

> **逐字转录，不弱化、不关闭、不降级。** 本 pass 对 P2-1 的处置 = 原样携带（`handoff.json.carried_findings` 同步镜像）。

### P3-1 — 观察（P3）

位置：`reviewer_report.md` **L209–211**，字节区 **[21334, 22045]** / **712 B** / `dba4b51d1dff87e42e6959d6710d5371cf7eddb6af39bc94d73cc78cebe5e3e0`

```
**P3-1 本卡三个 JSON 载体为 CRLF 工作副本域，git blob（LF）哈希不同，卡未声明字节域。**
- `handoff.json` 盘 13153 B（CR=179）/ blob `82e15a7a0e40…`（12974 B）；`t1_10_defect_verification.json` 盘 12763 B（CR=288）/ blob `6116e32a03bd…`（12475 B）；`append_only_proof_round57.json` 盘 676 B（CR=18）/ blob `a2ba612b3738…`（658 B）。`decision.md` 与 `verify_t1_10.py` 为 LF-only，blob == 盘。
- 卡的登记值与**盘上（CRLF）**一致，日常复算可用；但从 **git blob 复算会不等** —— 恰是本卡自己立的 F 段同族（「哈希取在哪个字节域没写明」），本卡未对自己的登记做同样声明。全文件无 BOM。
```

> **逐字转录，不弱化、不关闭、不降级。** 本 pass 对 P3-1 的处置 = 原样携带（`handoff.json.carried_findings` 同步镜像）。

### P3-2 — 观察（P3）

位置：`reviewer_report.md` **L213**，字节区 **[22048, 22230]** / **183 B** / `21c9d8cd4d6157f82dd00a35a32a5f6fd43cbcaf0faa839e7273e409249be08c`

```
**P3-2 九步载体缺 2/4/5/9**（`binding.json`/`oracle.md`/`commands.json`/步骤或 `next_action` 记录）—— 见 §7，按同日 T 卡形态记为形态差异，不阻断。
```

> **逐字转录，不弱化、不关闭、不降级。** 本 pass 对 P3-2 的处置 = 原样携带（`handoff.json.carried_findings` 同步镜像）。

### P3-3 — 观察（P3）

位置：`reviewer_report.md` **L215**，字节区 **[22232, 22473]** / **242 B** / `aa6003f7f3bb51be5cd383e7c59c2f711830bb18c128edb431c3af37905c628e`

```
**P3-3 `nature_of_card` 自称 `verification + residual closure`**，但本卡实际**未闭合任何残留**（其 `conclusion.defect_1` 亦如实写明未闭合）—— 措辞与事实不一致的轻微自述瑕疵，披露本身诚实。
```

> **逐字转录，不弱化、不关闭、不降级。** 本 pass 对 P3-3 的处置 = 原样携带（`handoff.json.carried_findings` 同步镜像）。

**P1-1 的三个要点（摘自上文逐字块，仅作索引，不替代原文）**：产品侧修复① **本卡未交付**；被测件 **至今可复现 rc=4 / 不写报告 / 0 裁决**；修复 **只存在于 `T1-10-FIX` 的 `changes.diff`（11534 B / `625ecfe4…`）且 `NOT applied`**；本卡给出的 **三条不修理由经复核均不足以支撑整体推迟**；**不因 T1-10-FIX 已 accepted 而放松**。

> 派单口径备注（如实登记）：派单在「落定内容」里把修复所在载体写作 `T1-F3-FIX` 的 diff；**载体原文（L189）写的是 `T1-10-FIX` 的 `changes.diff`（11534 B / `625ecfe4…`）**。本 pass 按**载体原文逐字转录**，未按派单改写；`T1-F3-FIX` 的 diff（`693d6239…`，合并链 3/3）**同样未 apply**，该事实单列于 `qualification.json.not_granted`。

---

## 3. 复审者保留的裁量（逐字，本 pass 不裁）

**派单指定逐字文本：**

```
若 owner 裁定本卡义务形态 = T1-22 的 `is_a_fix=false / the ruling authorises carding` 形态，可由同形态门读法例外豁免 —— 该裁量属 owner，我不裁
```

**载体原文（`reviewer_report.md` L196，字节区 [20258, 20581] / 324 B / `1e41ae1e4eaa5c036e064e1d936f98e178f9132053649f27c8a07f3e5518c072`）：**

```
- **边界**：若 owner 另裁「本卡义务形态 = 特征化 + 立卡（`T1-22` 的 `is_a_fix=false / why_not_a_fix=the ruling authorises carding` 形态）」，则本 P1 可由**同形态门读法例外**（§二十四式）豁免 —— 该裁量**属 owner，不属复审者**；我按卡文动作项如实分级。
```

**本 pass 的立场**：`ruled_by_this_pass = false`。**不裁定门读法例外**、**不以该例外弱化 P1-1**；例外若成立，属 **owner** 裁量（§二十四式），本 pass 只转录、不授予。

---

## 4. unverified（6 条逐字照录，`reviewer_report.md` §9 L221–228）

字节区 [22754, 24009] / 1256 B / `fbfbb03fef216cd37832d7c87452e3703eb540ca0e5749aca2c33991fea432ed`；6 个条目行 [22790, 24009] / 1220 B / `707bf3df071d54f93d5a48335809df0c26f72cc6dc638303ed4c2f0ff5873831`。

```
1. **未复跑 `scripts/verify_t1_10.py` 本身**：其 `__file__` 路径断言要求真实仓库结构，且会在 attempt 内重写 `t1_10_defect_verification.json` ⇒ 违反「只写两文件」。**替代**：自建 `%TEMP%` 探针独立复算核心行为（§4.1）；脚本正文只作静态阅读。
2. **证据 JSON 的 4 次幂等同哈希自述**（`22ead5c5…` 连跑 4 次）—— 未复现；我只能验证该文件现存字节与登记一致。
3. **09-20 当时的瞬时边界**（产品树 0 写入、锚点当时值）无法回溯；我只能复算**当前** `git diff HEAD --name-only` 非 `.planning` = 0，以及 `model_registry.py` 的漂移归因于 `git log 5fd82de7`。
4. `run_a.json` / `run_b.json` 的生成过程（卡已披露为幂等调试遗留、非交付物）—— 未验证。
5. `M-T-REVIEW` 22 卡裁定的原始载体（`reviews/T1_rulings.md` / `acceptance_rulings.md`）—— 我只读了 `landing_package/t1_review_flips.md` 转录块，**未**回源到其原始裁决文件。
6. `REMEDIATION_REGISTER` §136-F 的父侧「假阳性第 17 起」自述 —— 我只验证结论方向（逐字检索），未复算父当时那条 `Contains('supersede')` 的执行现场。
```

**6 条一条不少、一字未改**；本 pass 不把其中任何一条写成已验证。

---

## 5. 落定清单与边界

| 文件 | 状态 |
|---|---|
| `review.md` | **本文件，新建**（创建前 `Test-Path` = `False`） |
| `handoff.json` | **状态面转录**：`status` `review_pending → changes_required` + `status_before` / `status_transition` / `status_history`（2 条）+ `status_authority`（carrier + 自算 sha + 25115 B + 246 行 + 编码 + L3 行号与字节区 [47,72] + `verdict_word_written_by_reviewer` + `pin_sidecar`）+ `carried_findings`（5 条逐字）+ `reviewer_discretion_reserved` + `unverified`（6 条逐字）+ `pre_image` + `implementer_signed=false` + `verdict_is_transcribed_not_authored=true` + `bookkeeping`；顶键 20 → 35 |
| `evidence/T1-10/qualification.json` | **新建**（`evidence/` 与 `evidence/T1-10/` 目录一并新建；创建前 `Test-Path` = `False`） |

**handoff 前像 → 后像**：`13153 B / 715b5e0bc13a23fcf508525f8935c5ce781783dff5187e7d008ff48f7b2271ee` → `34650 B / 765ed10377e427ea61decee7efe13b3fb7418a1431c895637d8c68dc980ddb50`。
本 pass 已做**反向重建校验**：把状态面插入段剥离后重算，精确复现前像 `13153 B / 715b5e0b…` ⇒ **所有非状态面字节零改动**（CRLF 域保持不变，CR=537 / 538 行）。

**只读并复哈希（本 pass 写入 0 字节）**：

| 文件 | 字节 | sha256 |
|---|---:|---|
| `reviewer_report.md` | 25115 | `598f55d5cbd638f62d8775d06652b5010c33e1c465e53f55b34ceb3175b0370d` |
| `reviewer_report.sha256` | 85 | `02a403986819d520858b22af978ee267f2579827a876b74318ccbc2865146534` |
| `decision.md` | 14031 | `d7fe3ebb8dcc68689f876f7cd7fa03ab09ae13119a72d61c1f54afcecf30e232` |
| `t1_10_defect_verification.json` | 12763 | `22ead5c549311acea517bdf9819fcf97ad04c24c48edfb82cfc5451cabcb413c` |
| `scripts/verify_t1_10.py` | 24335 | `544ae0adb3a969209eee5ab5ddbdb781a63a5a6a2b615d8025386b22223ab983` |
| `append_only_proof_round57.json` | 676 | `c0bc84cfedad79741eca280928bbdf35e6714ce0beb4e48ea28709551fb0a08a` |
| `run_a.json` | 12761 | `a8ceba2fc067252abf6647f7d03d35bbfed37758ade5795599ac1f27f4295f3e` |
| `run_b.json` | 12761 | `98c520562dee48b69453b4af0b8965f5c0d96537b9eaabfc655e03eabdf0b1be` |

**我（本 pass）没做的事**：

- **未把 `changes_required` 当作 accepted** —— 本卡仍是有 P1 的未通过态。
- **未解除任何 `OPEN-*` / `BLOCKED-*` 条目**，未做任何参数阈值放行，未放宽任何判据。
- **未裁定 §二十四式门读法例外** —— 该裁量属 owner（载体 L196 原文如此保留）。
- **未晋升、未 apply 任何 `changes.diff`**（`T1-10-FIX` `625ecfe4…`、`T1-F2-FIX` `bc87bf81…`、`T1-F3-FIX` `693d6239…` 三者均仍 `NOT applied`）。
- **未代签**：`implementer_signed = false`；**未替复审者或实现者落定任何接受**。
- **未写** `reviewer_report.md` / `reviewer_report.sha256`、本 attempt 其余 7 个既有文件、五份计划文件（`REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`）、`.planning` 之外任何文件。
- **未跑任何测试 / 探针 / `verify_t1_10.py`**，**未联网**，**未执行任何 git 写命令**，**未使用 `git status`**；收尾只用 `git -c core.quotepath=false diff HEAD --name-only` 计数。
- **未修改任何一条发现的措辞或级别**，未新增发现，未关闭残留。

---

## 6. qualification 摘要（详见 `evidence/T1-10/qualification.json`）

| 键 | 值 |
|---|---|
| `formula` | `not_applicable_with_reason`（本卡被判据化的是**核验证据与判据**，无任何公式/情景/数值推导；本 pass 更只做簿记转录） |
| `disclosure_adaptation` | `unmapped`（复审未授予任何披露适配资格） |
| `accuracy` | `unproven`（复审未主张任何 accuracy 资格） |
| `granted_scope` | 本卡的**设计与核验交付**（可观察结果、缺陷② 闭合的核验、缺陷① 的特征化、危害形态、F 段字节域发现、边界自述可复算部分、两条移交）+ 裁决转录面 |
| `not_granted` | **产品侧修复①（未交付）** · 任何 `OPEN-*`/`BLOCKED-*` 解除 · 参数阈值放行 · **门读法例外（owner 裁量）** · `T1-F3-FIX` 已 apply 的声明 · 晋升 · **`T1-10` 的 ACCEPT** · accuracy · disclosure adaptation · formula 资格 · 代签 |
| `verdict` | `changes_required`（L3，转录非自创） |

**当前状态**：`changes_required` —— **非 accepted、非关闭**；五条发现随卡携带；门读法例外与晋升归 owner；本 pass 只做簿记转录。
