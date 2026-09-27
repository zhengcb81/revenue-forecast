# oracle.md — I-11-C / a20260926-01（开工前冻结的独立预期 + 门 0 原始输出）

> **本文件在任何实质动作（映射表落笔、变异执行、handoff 落笔）之前冻结**。写入面 = 仅 `execution_runs/I-11-C/a20260926-01/`。
> 本工位 = **映射实现者**（`implementer_i11c`）：按派单四动作消费 `I-11-B/a20260926-01` 交付物，产出参数映射表 + 可执行性核对 + 红绿变异 + STOP 核验。
> **不自签、不放行参数、不触发任何 falsifier/自动动作、不解任何 OPEN/BLOCKED、不产生 ACCEPT、不改封盘字节、不派 I-07-E**。
> 卡文 Owner（`card_I-11-C.md` L5）= 未参与参数设定的独立研究 reviewer —— **卡文本尊的 reviewer 四动作（L13-L16 可证伪替代解释/falsifier/四失败/版本触发）不在本工位执行**，交另派独立复审（派单明示）。status 交付形态 = `review_pending`。

---

## 0. 门 0 自探（写+回读+删除三步留档，本会话自探，不采信父探针）

- 探针（2026-09-26T18:00:38.6545155+01:00，本产出目录内）：`Set-Content` 写 `_gate0_probe.txt` → `Get-Content -Raw` 回读 → `Remove-Item` → `Test-Path` 确认已删。原始输出逐字转录：

```
=== GATE0 BEGIN (I-11-C/a20260926-01) ===
cwd=C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-11-C\a20260926-01
--- step0 mkdir ---
dir_exists=True
--- step1 write ---
write_ok=True
--- step2 readback ---
readback=gate0 probe I-11-C a20260926-01 write-readback-delete 2026-09-26T18:00:38.6545155+01:00

--- step3 delete ---
deleted_gone=True
probe_ts=2026-09-26T18:00:38.6545155+01:00
=== GATE0 END ===
```

**结论：`gate0_passed=true`（写 ✅ / 回读 ✅ / 删 ✅；零提权、零破坏性替代；探针已删，未留残件）。**

---

## 1. 开工授权（逐字回源）

### 1.1 派单（编排层本轮，父 agent `session-19074bf0-0205-4315-af73-9db57597275a`）

- 工位 = `I-11-C`「校准后参数映射」实现者；依赖 `I-11-B`（其交付 `review_pending`）。
- 派单原文指定：产出目录 `execution_runs\I-11-C\a20260926-01\`（新建，实测已建）；四件产出 `oracle.md` / `parameter_mapping.json` / `mapping_verification.json` / `handoff.json`；四动作 + 硬约束见派单原文（`handoff.json` authorized_by 全文转录）。

### 1.2 `card_I-11-C.md` 卡文（逐字，回源实测 25 行全卡）

- L3 节标题：`## I-11-C · 独立反方审查与触发更新`
- **L5（派单要求逐字收录）**：`Parent：I-11；状态：planned；Owner：未参与参数设定的独立研究reviewer；依赖：I-11-B。`
- L7 前提：`冻结参数版本，reviewer先读原始证据再读结论。`（本工位据此不回改任何参数载体；冻结语义 = 只读消费）
- L11-L16 卡文动作（**reviewer 面，本工位不执行**）：`1. 逐命题提出一个可证伪替代解释，并搜集已有证据中的反例，不允许只复述结论。 2. 填写falsifier的观测量、阈值、日期、来源路线和恢复规则；阈值必须专业审定。 3. 分别检查事实错、机制错、幅度错、时点错四种失败；在收益预测中逐项标风险，而非统一降低一个信心分。 4. 变更触发时创建新版本与delta，不覆盖旧快照；保留旧预测供I-12评分。`
- L18-L21 卡文停止（reviewer 面）：`无独立reviewer或反证只有空泛风险词→STOP_REVIEW。` / `触发更新会改写旧预测而非新增版本→STOP_LINEAGE。`
- L23 验收：`每个量化命题都有可执行触发器、反方判断和保留历史的更新规则。`
- L25 证据：`evidence/I-11-C/challenge_review.md`、`evidence/I-11-C/falsifiers.json`、`evidence/I-11-C/change_policy.json`、`evidence/I-11-C/qualitative_decision.json`（**reviewer 工位写入面，本卡不代建**）。
- **角色分界登记（unverified-D1）**：派单标题「校准后参数映射」与卡文标题「独立反方审查与触发更新」不同名。判读：编排层将 I-11-C 拆为两站——本站=映射实现者（执行派单四动作，产出消费 `I-11-B` 的映射表），另站=独立复审（卡文 L13-L16 真 owner 动作）。本站不越权执行 reviewer 动作；该拆分是否符合 owner 意图**留编排层确权**，本站按派单执行并如实登记。

### 1.3 `OWNER_DECISIONS.md §三十四`（L745-L780，2026-09-26 15:4x，选项式问答原话）逐字依据

- L754：**owner 选择「A」**；L757：**「改判 I-11-B 的开工门槛 —— 以 MERGE 七条当前 5✅ + 2❌ 现状开工；i11b_unblocked 的语义从『7/7 才开』改为『owner 明文许可开工』。」**
- L758：**「C3/C5 的残余不丢、不隐藏 —— 列为 I-11-B 开工后的并行欠账，每项在卡内载体以 expert_assumption 或 unverified 形式登记」**
- L761-L766 开工卡硬约束（本站延续适用）：**oracle 先冻结**（含改判逐字依据 + `C3/C5` 残余清单 + `expert_assumption` 标注要求）／**不放行任何参数**（`low/base/high` 仍 null、`_PLACEHOLDER` 维持）／**不触发任何 falsifier/自动动作**（`ACCT L230` + `IND L299`）／**实现者不自签 · 独立复审 · 落定走三件套**／**每一条以 `expert_assumption` 承接的判断，必须给敏感性区间 + `equivalent_to_disclosure_basis=false`**（同 `H4` 的 `(iv)` 形态）
- L769-L775 边界：**不解除** `OPEN-2/3/5/6` 任何一条；**不解除** `BLOCKED-6a/6b/6c`、`BLOCKED-NEEDS-ORIGIN-BYTES`；**不放行参数**（两个 `_PLACEHOLDER` + MSFT 四参数 + 新两分部参数）；**不产生 `ACCEPT`**、**不改任何 `status`/`decision`/`decision_sha256`**（除非是新卡自己的写入面）；**不代签**。
- L777-L779：派工给足（七条现状含 sha · C3/C5 残余清单 · EA 模板 · 红绿双向变异 · fail-closed）；**「`I-11-B` 的 `I-11-C` 后继卡」按卡文依赖顺序（`I-11-C ← I-11-B`）另派，不在本节一并授权** —— 本轮编排层派单即该「另派」的行使；§三十四 改判语义与边界约束由本站延续执行。

### 1.4 依赖实测（回源，开工前提）

- `execution_runs/I-11-B/a20260926-01/` 在位 7 文件：`calibration_plan.json`(32,665 B) / `expert_assumptions.json`(8,580 B) / `synthetic_mechanism_check.json`(8,035 B) / `oracle.md`(17,723 B) / `handoff.json`(11,349 B) / `revert_or_stop.json`(4,367 B) / `verify_plan.py`(4,495 B)。
- I-11-B `handoff.json`：`status=review_pending`、`expert_assumptions_count=7`、`params_released=false`、`implementer_signed=false`、18 槽位（14 出数 proposed_not_released + 4 显式拒绝出数）、`stop_calibration_triggered=false`、`stop_scenario_triggered=false`、严格读法之争已登记待独立复审裁定（revert_or_stop.json L13-L17）。
- store 侧在位只读：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`（61,231 B）。
- **依赖状态 = `review_pending`，非 accepted**：本站按「有写入面的下游实现者消费 review_pending 交付物」继续（§三十四 owner 明文许可开工的同一逻辑链 + 派单明示依赖状态）；本站产物同为 `review_pending`，一并交独立复审，不因此放宽任何验收。

---

## 2. C3 / C5 残余清单（红线：逐条登记，全部 `unverified`，不隐藏、不当作已解）

> 派单硬约束：「C3/C5 残余清单逐条 `unverified`」。I-11-B 曾将 C3-② 记 `verified_by_parent`（父证）；本站无产品仓读面，**一律降记 `unverified` 并注明其父证来源**，从严处理。

| # | 项 | 本站登记 | 依据（文件+行） |
|---|---|---|---|
| C3-① | origin 字节（62,953 B 已落；E1 等级仍 BLOCKED-PARTIAL） | `unverified` | I-11-B oracle.md §3.1；OPEN3-E1-ORIGIN-BYTES-R2/a20260926-01/handoff.json |
| C3-② | B2 晋升（父对账称已完成；本站无读面） | `unverified`（父证转录，不自证） | I-11-B handoff.json L33；B2-PROMOTION/a20260926-01 |
| C3-③ | ACCT-R2 定级（RULED ≠ 通过；E1=BLOCKED-PARTIAL/S1/4 语料降 E3） | `unverified` | OPEN-3-ACCT-R2/a20260926-01/handoff.json |
| C3-④ | IND-r2 在跑未归（目录空） | `unverified` | execution_runs/OPEN-3-IND-R2/a20260926-01/（空） |
| C3-⑤ | MSFT 六参数/新两分部参数/HK 参数维持不放行 | `unverified` | I11A-OPEN-MERGE 两半裁定；I-11-B oracle §3.1 ⑤ |
| C5-① | 6c accepted_scoped（带 2×P2+3×P3，非 clean accept） | `unverified` | BLOCKED6C-THRESHOLD-REVIEW-STATUS/a20260926-01/handoff.json |
| C5-② | H4 口径桥残差 269 吨/534 千克（§三十六 追加修订后须重跑 Q2，会签未成） | `unverified` | OPEN6H4-IND-COUNTERSIGN/a20260926-01/handoff.json；OWNER_DECISIONS §三十六（L820-L848）——修订授权≠会签完成 |
| C5-③ | 6b 恒等式容差（路径(c) unquantified；R2 NOT_SIGNED；整条归 ruling_6b L110 另判） | `unverified` | OPEN6B-R2-REVERT-UNQUANTIFIED/a20260926-01；OPEN6B-TOLERANCE-RULING/a20260926-01/ruling_6b.md L110 |
| C5-④ | H2 基准（交付仍 still_blocked；A-6.3 全套 0/3） | `unverified` | OPEN6H2-ACCT-SIGNOFF/a20260926-01/handoff.json |

**fail-closed 宣言**：以上 9 项在本站任何载体中不写成「已解」；`expert_assumption` 只承接校准幅度判断，不冲销任何 BLOCKED。

---

## 3. `expert_assumption` 标注模板（冻结；§三十四 L766「同 H4 的 (iv) 形态」）

```json
{
  "id": "EA-x",
  "assumption": "……（明确写出假设内容）",
  "basis": "……（为何只能靠分析师判断；缺口是什么）",
  "sensitivity_interval": {"low": "…", "base": "…", "high": "…", "unit": "…", "band_rationale": "…"},
  "equivalent_to_disclosure_basis": false,
  "carrier_form": "A-6.3 (iv) expert_assumption + 敏感性区间",
  "release_state": "not_released",
  "blocked_by_residuals": ["…"]
}
```

- 缺任一字段 ⇒ 该条不成立 ⇒ 对应映射触发 STOP；`equivalent_to_disclosure_basis=false` 为常量禁止改写。
- 管理层目标不得用作独立准确性证据（card_I-11-B.md L14；`management_target_is_not_independent=true` 恒成立）。
- 本站**不新增 EA**：I-11-B 的 EA-1…EA-7 为本站映射的唯一 EA 来源面；本站发现的新缺口一律以 `unverified-Nx` 登记，不造新假设。

---

## 4. 冻结的判据与预期（在任何复算/变异执行之前写下）

### 4.1 可执行性判据（动作 1）

每槽位四查，全过 = `executable`；任一不过 = `not_executable` + 缺什么：
(i) **幅度**：new_value 三档与 base 的关系可由登记带（±5%/±10%/增长率换算/恒等式 τ）逐位复算（容差 ±0.5 最小单位或精确相等）；(ii) **单位**：unit 字段与量纲链一致（元/吨/千克/小数，金克↔千克换算明确）；(iii) **起止年份**：period_start/period_end 明确且基期值可得；(iv) **转换公式**：公式逐项可复算，公式文本与登记数值自洽（数值代入公式能得到登记结果）。

### 4.2 预期（冻结，执行前写下；执行后逐条对表）

| 预期 | 内容 |
|---|---|
| P1 | 18 槽位中 13 个 `executable`（四分部 SEG×4、可售量 VOL×4、PLAN×1（限情景对照）、RECONCILIATION×1、MSFT 增速×3），5 个 `not_executable`（REALIZED_UNIT×1：公式自洽性存疑，见 P2；COPPER/GOLD REALIZED×2、MSFT CLOUD/LICENSING×2：I-11-B 已显式拒绝出数 EA-7） |
| P2 | `ZIJIN_MINERAL_REALIZED_UNIT_REVENUE_FY2027` 转换公式**疑似不自洽**：store L170/L175 登记分母 `(884,943 + 83,161×24)`，按字面合成 = 2,880,807 吨，而登记分母 = 885,141 吨；109,977,556,345/885,141 ≈ 124,248.63 的除法本身与 ±5% 带算术自洽，但分母合成式与数值不闭合 ⇒ 本站按 `not_executable`（缺：分母权威推导/原值算术更正，需 AR 回源，归独立复审/会计面）处置，**该槽位 proposed 值不经本站传播**。预期执行后确认为真发现，登记 `unverified-N2` |
| P3 | EA-4 `band_rationale` 的「三分部收入合计区间 [320,763, 348,432] USD mn」与其自身增长率带换算（预期 ≈[375,283, 414,787]）不符 ⇒ 登记为注记层不一致 `unverified-N3`（不影响 new_value 算术，不影响可执行性判定） |
| P4 | SEG×4 的 ±5% 带与差额法 base、VOL×4 的 ±10% 带、MSFT×3 的增长率换算、PLAN 的达成率带、RECONCILIATION 的 584,049,229,264−234,970,146,412=349,079,082,852 恒等式，全部逐位复算成立 |
| P5 | 合成示例隔离清单（2/8760/0.5/0.6/0.7/40/20/30/32/34/1200/264000/281520/299040/17520）在本站映射表任何**数值字段**中零出现（文本引用不算；1,200,000=铜计划吨数与示例 1200 非复制，按 I-11-B part_3 先例登记） |
| P6 | 红绿变异：绿（原件）rc=0；5 个红变异（released 翻转/合成数注入/EA 缺区间引用/非 null 放行/残余写 resolved）全 rc=1 且违例具名 |
| P7 | STOP：槽位级 STOP 覆盖 5 个 not_executable 槽位（无数字传播）；卡级 STOP_CALIBRATION/STOP_SCENARIO 按操作读法（触发式，从严）不触发——每个传播幅度皆可溯源（contract arithmetic / 已签容差 / EA+区间）；严格读法之争**原样继承** I-11-B revert_or_stop.json L13-L17 的登记与升级路径，交独立复审 |
| P8 | store 侧（hypotheses_v3）全程只读零改动；`low/base/high` 全 null、`released=false`、`_PLACEHOLDER` 在位；本站不产生 hypotheses 新版本（无需 `supersedes` 形态，`hypotheses_h4_v1.json` 形态先例仅作参照） |

### 4.3 红绿双向变异清单（冻结；副本执行，原件字节不动）

| 编号 | 变异（副本上） | 期望（红） | 期望（绿） |
|---|---|---|---|
| M1 | 把任一映射行 `value_state` 翻为 `released` | rc≠0（J3：非 released 常量破坏） | 原件 rc=0 |
| M2 | 向任一真实参数数值字段注入合成数 281,520 | rc≠0（J2：合成数隔离破坏） | 原件 rc=0 |
| M3 | `handoff.params_released` 翻 `true` | rc≠0（J1：不放行破坏） | 原件 rc=0 |
| M4 | 把某 EA 引用的 `sensitivity_interval` 删除（模拟 EA 缺件仍被引用） | rc≠0（J2：EA 模板缺件不得承接映射） | 原件 rc=0 |
| M5 | 把 C3/C5 残余某项 registration 改为 `resolved` | rc≠0（J4：残余隐藏红线） | 原件 rc=0 |

校验器 = 本目录 `verify_mapping.py`（本站自写，只读校验；不变量 J1-J4 见该文件头）。红绿 rc 进 `mapping_verification.json` / `handoff.json`。

### 4.4 STOP 判据（冻结）

- **STOP_MAPPING（槽位级）**：任一槽位映射不可执行 / 数据不足 ⇒ 该槽位**不出数**、不传播，登记缺什么 + `unverified-Nx`，fail-closed。
- **STOP_CARD（卡级）**：操作读法（从严触发式）= 凡本站传播的任一幅度既无可核来源（contract arithmetic / 已签容差 / 历史关系）又非明确 EA 承接 ⇒ 卡判 `blocked`；严格读法 = 存在任一 not_executable 槽位即整卡 blocked —— 两读法之争与 I-11-B 同构，**原样继承其升级路径交独立复审**，本站不自裁。
- STOP_SCENARIO（继承）：量 high × 价 high × 其他收入 high 独立叠加（≈+21% 不可能联合）或同一事件贡献两通道 ⇒ 触发。本站映射表须逐行携带联动约束标记（EA-6）。

### 4.5 边界自宣（本 oracle 不做什么）

- 不执行卡文 L13-L16 reviewer 四动作（可证伪替代解释/falsifier 表/四失败标注/版本触发规则）——真 owner 面，另派。
- 不放行任何参数：`hypotheses*.json`、`model_cards*` 全程只读；不新建版本（若确需 ⇒ `hypotheses_h4_v1.json` 形态 `supersedes`+`modified_indices` 落本目录、封盘原件零字节——本站**不需要**，映射全部落本站 `parameter_mapping.json`）。
- 不触发任何 falsifier/自动动作（ACCT L230 + IND L299）；不解 OPEN-2/3/5/6、不解任何 BLOCKED-*；不派 I-07-E；不产生 ACCEPT；不写 `evidence/I-11-C/*`（reviewer 写入面）；不写五份计划文件；不写 `.planning` 之外；禁 git 写、禁 `git status`（git 只读 diff 计数除外，同 I-11-B 先例）；不联网。
- 合成示例数字只用于隔离核验，禁止进入真实公司任何字段。
