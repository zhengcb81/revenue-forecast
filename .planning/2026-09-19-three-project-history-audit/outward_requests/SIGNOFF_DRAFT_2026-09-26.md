# 三函回执 · owner 签收件（草案）

- 编制：编排层（父）· 2026-09-26 15:25
- 依据：`OUTWARD-RECEIPT-SUFFICIENCY/a20260926-01`（**ALL PASS**）+ `OUTWARD-LETTERS-RECEIPT-AUDIT/a20260926-01`（**ALL PASS**）+ 父三件一手证据
- 性质：**供 owner 签收**；本件**不是**外部方真实签署，**不产生 ACCEPT、不解除任何 BLOCKED、不改任何卡 status**

---

## A. 头部（签收时必须逐字保留的限定）

> 我（owner）以**本人身份**签收本件。
> **我确认：`outward_requests/RESPONSES.md` 中登记的三份 T2 裁定是「owner 终确下的 role-play 模拟裁定」—— 非外部方真实签署、未在任何函上签字。**
> **本签收不产生 `ACCEPT`、不解除 `I-06-A`/任何 `BLOCKED-*`、不变更任何卡 `status`、不代任何收件方作答。**

---

## B. 事实段（逐条可回源）

### B1. 三函已送达（2026-09-22）
`outward_requests/_provenance.json → issuance_2026_09_22.physical_transmission` 载 owner 原话「**给你回执**」；登记册 §三十九「三函递交=已完成」、边界句「**送达回执，非裁定回复**」。
- 函 A 签发 sha `cd88bd4cece0271d…`（11546 B / 185 行）
- 函 B 签发 sha `f494ac3db7ce2ff2…`（15946 B / 246 行）
- 函 C 签发 sha `73fb856e…`（11673 B）

### B2. 已收到 vs 尚未收到（**核心**）
| 函 | 内容 | 回执状态 |
|---|---|---|
| **A** | `OPEN-4/5/6`（wiki 来源审核 owner · 安全 reviewer · RF 消费 owner） | **已登记 3 份**（2026-09-22，owner 终确 role-play）—— **性状 = 非真实签署** |
| **B** | `OPEN-D1/D2/D3` 信任根 · `D7` W/T/L · `D5/D6` · `I09A-1…6` | **0 行**（`RESPONSES.md` 全文无「函 B」/「OPEN-D」） |
| **C** | `I-05-C` GAP-2 / GAP-3 | **0 行**（GAP-2 = blocked on RF consumer_analysis owner；GAP-3 = pending reviewer decision） |

### B3. 请求项 ↔ 回应对照（**见 `audit_report.md` 的对照表**）
- 函 A 的请求项：`OPEN-4` 待裁 **3 件** · `OPEN-5` 待裁 **4 件** + 已知不一致 · `OPEN-6` 待裁 **1 件** → 三份 ruling 有逐项回应
- **但条件兑现仅 4/7**（`RECEIPT-AUDIT` 实测）：
  - `O4-C1` **partial** —— 导出 JSON non-authoritative 副本标注（产品字节 0 命中）
  - `O4-C4` **unfulfilled** —— 需 **函 B T2-9/OPEN-D1 真实回执 + 信任根文件实测存在**；**在此之前回执不得标称 signed（`ruling L102`）**
  - `O4-C5` **partial** —— 缺两条新正例测试
  - `O4-C6` **partial** —— 被覆盖旧收据 sha 未显式并列留档
  - `O5-C2` **unfulfilled** —— **`resume` 接口本体不存在**（RF scripts `'resume'` 0 命中）
  - `O5-C3` **partial** —— 输入绑定（余见 `receipt_consistency.json`）

### B4. 信任根状态（逐字）
- `T2-SIM-OPEN4-WIKI/ruling.md L102`：「**信任根建成并核验前，任何回执不得宣称『已签名审核』；只能记为『未签名归属记录』，不得作为完成 `D-W06` 审核要求的凭据用于产品晋级。**」
- `outward_requests/B_signature_trust_domain.md L28`：「**不存在可用于生产验证的信任根**」
- `L1`（标题栏）：`OPEN-D7 —— W/T/L 三数值（最高优先，因为它把系统卡在拒服务状态）`

---

## C. 选择段（**二选一落笔**，按 `README:25` 六要素：选择·理由·反例·兼容影响·恢复规则·被拒绝的替代方案）

### 甲（默认 · 与现状一致）
> **维持现有口径**：`RESPONSES` 三行 = **已预置、待签收**（`signable_now=false`）；本项判据 `L1–L5` **仍 FAIL**；**门①（`I-06-A`）按 `§19+§21` 例外维持已解**，**其效力不外溢到本项**。
> - **理由**：`README:12`「读成 owner 已裁 = **等同伪造签名**」；`README:24`「owner 均不得代收件方作答」
> - **反例（什么会推翻它）**：三收件方**本人**在**自己卡载体**留签 + 信任根建成核验 ⇒ `L1–L4` 同时成立
> - **兼容影响**：`task_plan L301` 括注须改（见 D 段）；19 卡链的三根（`I-11`/`I-08`/`I-14-E`）**不受影响**
> - **恢复规则**：未来真回执须「本人卡载体 + 接收记录 + sha256」由编排层**不改一字**转录
> - **被拒绝的替代方案**：**把 owner 签收记成「本项达成」**（→ 触发 `README:12` = 伪造签名）

### 乙（收紧）
> **按字面真实外部回执「重开门①」**（`§73` 反向选项）—— 那是**收紧、不是达成**；须 owner 明示选它。

---

## D. 落点段
- 本件**落 `OWNER_DECISIONS.md` 追加节**（若签）
- **不进函件、不进 `RESPONSES.md`**（**2026-09-23 冻结令**）
- 未来真回执的落法：**本人卡载体 + 接收记录 + sha256** → 编排层不改一字转录

## E. 尾部 · **本签收不产生的效力**（逐条）
1. 不把 `RESPONSES` 三行变成「已签收」
2. 不代 wiki 来源审核 owner / 安全 reviewer / RF 消费 owner / 跨仓双方 / 独立 reviewer 本人签收
3. 不解除 `OPEN-4 ruling L102` 过渡期规则（需**信任根建成并核验**）
4. 不产生**函 B** 全部回执内容
5. 不产生**函 C** 全部回执内容（GAP-2 / GAP-3）
6. 不产生任何 `ACCEPT`、不解 `I-06-A`、不改任何卡 `status`
7. 不解 19 卡链三根中的 `I-11`（MERGE 七条 `5✅+2❌`、`i11b_unblocked=false`）与 `I-14-E`

---

## F. **签收能解 4 / 不能解 6**（`SUFFICIENCY Q4` 实测）

**能解**：① `L301` 括注时效 ② `L1` 的 owner 侧部分 ③ 对标准 E 的追认（不新增效力）④ 授权追发/更新三函（§十八 C 先例，送达仍归 owner）

**不能解**：① `L2` 变「已签收」 ② `L3` 代三方签 ③ `L4` 信任根 ④ 函 B 全部内容 ⑤ 函 C 全部内容 ⑥ 任何 ACCEPT / 解 `I-06-A` / 改 status

---

## G. 需 owner 一并择定的表述项（**裁定工位明确留给父**）
`task_plan L301` 括注已陈旧（**我已于 15:15 追加更正注，原文保留**）：
- 「owner **发送**」→ 实况是 **三函 2026-09-22 已送达、缺的是「回复到达」**
- 「本会话 `workspace-write` **不可提权**」→ 实况 **approval=ask、父当日三次提权全获批**
- **判据名建议改为「三函真实外部回执」**

---

## H. ⚠️ **两路审计对 `I-06-A` 状态的差异 —— 已查清、以本注为准**

**差异**：
- `SUFFICIENCY Q5` 判 **`I-06-A` 闸已解**（依据 `a20260922-02 = accepted_scoped`）
- `RECEIPT-AUDIT D7` 判「`I-06-A/handoff.json` 仍 `status=blocked`、`still_awaiting_other_parties` 含 `OPEN-4/5/6`、mtime **2026-09-20 17:10:56**」

**父回源查清（两条路径都存在）**：
```
execution_runs/I-06-A/a20260919-01/handoff.json  mtime 2026-09-20 17:10  status=blocked（有 awaiting 字段）  ← D7 读的这个
execution_runs/I-06-A/a20260922-02/handoff.json  mtime 2026-09-23 00:35  status=accepted_scoped             ← 卡级最新
execution_runs/I-06-A/handoff.json               **不存在**
```
**⇒ 结论**：
1. **卡级生效载体 = `a20260922-02`（`accepted_scoped`）** —— **`SUFFICIENCY` 正确**（**纪律 10 + 纪律 20：多 attempt 必须卡级取最新**）。
2. **`RECEIPT-AUDIT D7` 读的是被取代的 `a20260919-01`** —— **与父第 37 起同型**。其观察（「旧载体仍 `blocked`」）**属实但非当前状态**；旧 attempt **本就按追加式不回改**。
3. **两路对「三函回执本身是否充分」的结论一致**：`SUFFICIENCY = insufficient` · `RECEIPT-AUDIT = inconsistent / 门 4/7` ⇒ **不影响本件 C 段的选择**。
4. **`task_plan L20`「19/19 全 gated on `I-06-A`」与 `L301`「仍等外部：三函回执」两处，均须按本件 G/H 段择定表述。**

---

## I. `RECEIPT-AUDIT` 的缺口两分类（供选择时对照）

**A · 要 owner 签收**（6 项）：① D1/D2 补登补勘误授权 ② `RESPONSES L15` 漏记 `D-续4` 是否补勘误 ③ **13/29 条件的最终认定**（载体卡多为 `accepted_scoped`）④ `C7` 绿证 iso/现盘守卫指纹差异复核 ⑤ `D7` 的 `I-06-A` 解除权 ⑥ `J7` 要素① 缺 5 文件是否补声明

**B · 要外部方真实回执**（5 项）：① 函 A 三门**本人卡载体签收** ② **函 B 全部请求零回执**（`D1/D2/D3/D5/D6/D7/I09A-1..6`）③ 函 C `GAP-2/GAP-3` 零回执 ⇒ `O5-C6` 无法定稿 ④ `O4-C4`/`O6-C3`/`C4` 依赖**函 B `T2-9/OPEN-D1` + 信任根实测存在** ⑤ `O5-C2/C3/C7` + 边界记 4/7 依赖 **`resume` 接口本体（实测不存在）**

**关键实测数字**：函 A **请求 20 → 回应 20 → 缺 0**（覆盖完整）；**但条件兑现仅 13/29 = 44.8%**（含部分 19/29 = 65.5%）· **`J7` 要素①「非外部方真实签署」缺 5 个文件**（函 A/B/C、`README`、`_provenance` 都只写了要素②）· **`J5` `_provenance` 触发 `blocked#5`**（`README updates.after` 指纹 +195B 无勘误）

---

## 签收

`owner 签名 / 日期：____________________`
`选择（甲 / 乙）：____________________`
