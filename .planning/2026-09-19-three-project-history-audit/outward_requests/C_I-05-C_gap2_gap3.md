# 函 C —— I-05-C 的 GAP-2 / GAP-3 请他方裁决

**收件方**：

| 项 | 主题 | 待裁方 |
|---|---|---|
| **GAP-2** | `consumer_analysis` producer 不存在；真实 LLM 能力未验证 | **RF `consumer_analysis` owner**（提供入口） |
| **GAP-3** | `InvocationTracker` 事件 schema 需 reviewer 批准方可生产持久化 | **独立 reviewer** |

**授权依据**：`OWNER_DECISIONS.md` §13 **T2-14**（I-11-A 分支）与 **T1-2**（`D-W05` producer entry 已批准）。
**上游卡**：`execution_v2/card_I-05-C.md`（`owner：wiki producer 单一 owner + RF consumer_analysis owner`）。
**证据目录**：`execution_runs/I-05-C/a20260919-01/`。

---

## 0. 先说清「已解」与「未解」，避免误读

`I-05-C` 的 `handoff.json` 顶层 `status = review_pending`，`reviewer_status = pending`。
备忘：**owner 已批准 `D-W05` producer entry（2026-09-20 16:45）**，
但这**只是「批准」，不是「验收」** ⇒ `status` **保持 `review_pending` 不变**（纪律第 7 条）。

其 `remaining_gaps` 三项实测状态：

| 缺口 | 严重度 | 描述 | 状态（原文） |
|---|---|---|---|
| **GAP-1** | P2 | `produce_for_demand` 生产实现：测试中为 **mock-only**。真实实现需接 CW `service.py`（`CatalogConfig`/`CatalogStore`）与实际 producer | **UNBLOCKED 2026-09-20 by owner D-W05 approval** —— 可实现，**尚未实现**，待实现者工作、再独立复核 |
| **GAP-2** | P2 | **`consumer_analysis` producer 不存在。** 测试只证明 missing/unsupported 处理，**真实 LLM 能力未验证** | **blocked on RF `consumer_analysis` owner providing entry** |
| **GAP-3** | P3 | `InvocationTracker` 事件 schema 需 reviewer 批准方可生产持久化 | **pending reviewer decision** |

⇒ **本函只处理 GAP-2 与 GAP-3。** GAP-1 属实现者工作，不在对外请求之列。

---

## 1. GAP-2 —— RF `consumer_analysis` owner 请提供入口

### 1.1 卡对 GAP-2 的硬约束（**不得绕过**）

`card_I-05-C.md` 明文：

> **失败停止与恢复界限**
> - **缺 `consumer_analysis` 真实 owner 入口或 LLM 能力就阻断对应角色；不造绿色样例补全。**

> **固定样本**
> - **受控 LLM 假服务用于故障/计数（明确 test double），默认真实 provider 能力另验；
>   没有模型能力则真实 summary case blocked，不假称已验证。**

⇒ 起草方**已如实保持**该角色阻断，**未**造绿色样例。请贵方知悉：
**本卡在这个角色上是诚实的 `blocked`，不是拼凑的 `pass`。**

### 1.2 请贵方提供/裁定的四件事

1. **真实入口**：`consumer_analysis` 的 owner 入口是**哪个真实调用点**
   （哪个文件、哪个函数、哪个 CLI）？
   卡里列为「只允许修改」的范围含：
   > `RF consumer_analysis 对应 owner 文件须先列精确路径`
   ⇒ 请**给出精确路径**。这是卡本身要求的前置，**不能**由实现者猜。

2. **DAG 位置**：`card_I-05-C.md` 冻结的**新活动 DAG** 为
   `normalized→summary`、`normalized→sections`、**`summary→consumer_analysis`**；
   历史 `markdown` **只兼容而不补产**。
   请确认 `consumer_analysis` 在活动 DAG 中的**入边**确实只依赖 `summary`，
   还是另有依赖（如 `sections`）？

3. **LLM 能力边界**：真实 LLM 能力**未验证**。
   请明确：
   - 该角色使用的**具体 provider / 模型**是什么？
   - 若在本次评审期**无法**接入真实 provider，
     请**明确写下**「该项维持 `blocked`」，并说明**何时/以何条件**可解除。
     ⚠️ **不得**用 hermetic 假服务代替真实能力结论——卡的退出判据明文：
     > `hermetic 假服务不等于真实 LLM/投资研究质量已通过`

4. **角色缺失语义**：`W05C-N3` 要求「无适用 producer / 无 credentials / unsupported 文档」
   须返回**明确区分**的 `missing / unsupported / not_applicable`。
   请确认 `consumer_analysis` 缺入口时应归入**哪一类**（这决定下游如何报告）。

### 1.3 ⚠️ 与函 A 的耦合（请两方对齐）

`consumer_analysis` 的缺失处理会经 `I-06-A` 的 demand/handoff 路径回传。
若贵方在**函 A** 的 OPEN-4/OPEN-5 中也参与（RF 消费 owner 负责 OPEN-5），
请在两边**使用同一套缺失语义**，避免出现「A 说 `missing`、C 说 `not_applicable`」的分歧。

---

## 2. GAP-3 —— `InvocationTracker` 事件 schema 请 reviewer 批准

### 2.1 待批的 schema 字段（原文）

> "`InvocationTracker` schema: reviewer needs to approve the event schema for production use
> (**role / producer_name / call_status / attempt_number / error / artifact_id**)."

### 2.2 卡的原始要求（决定 schema 必须满足什么）

`card_I-05-C.md` 的 `W05C-N2` / `W05C-P1` 有两条**互相拉扯**的硬要求：

> **W05C-P1**：只调用 sections producer 1 次、**parser=0 / LLM=0**；读到新 sections；**第二次 producer=0**。

> **W05C-N2**：LLM 第一次失败第二次成功，或 parser 失败未产 artifact。
> 预期：**真实调用 attempts=2** 或失败 **parser=1**，
> **不以 artifacts INSERT 数=1/0 充当调用次数**。

⇒ 核心纪律：**「实际调用次数」必须记在真实调用边界**，**不能从结果表倒推**。
请贵方在批准 schema 时确认：

1. **六个字段是否足够** 满足上述「attempts=2」「成功/失败/重试可区分」的要求？
   特别是：
   - `attempt_number` 是**每角色**计数还是**每 producer**计数？
   - `call_status` 的**权威闭集**是什么（`ok / error / refused / skipped`?）？
   - `artifact_id` 在**失败调用**（未产 artifact）时取什么值（`null` 还是别的占位）？
2. **是否需要 `duration` / `started_at` / `provider` / `model` / `request_id`** 等补充字段？
   （`role` 与 `producer_name` 并列已存在，请确认二者语义不重叠。）
3. **持久化介质**：与 `D-W06` 已裁的单一 CW 持久 owner
   （`src/company_wiki/source_catalog/store.py`，`catalog.sqlite3`，`_apply_additive_migrations`）
   **同库**，还是另立？
   （这属 `START_HERE.md` 明文归专业审查的「跨进程锁与崩溃恢复机制」范围。）
4. **口径要求**：卡要求
   > `raw退出码、expected退出码、业务判定分开；跳过、超时、未采集不是通过`
   ⇒ 请确认事件里如何**表达「未采集」**（不能与 `ok` 混同）。

### 2.3 本卡已备好的证据（供 reviewer 审阅）

`execution_runs/I-05-C/a20260919-01/` 下已产出：
`decision.md`（64 行）· `oracle.md`（111 行）· `commands.json` ·
`producer-invocations.json` · `requested-role-dag-matrix.json` ·
`retry-count-vs-artifact-count.json` · `second-reuse.json` · `case_results.json` · `changes.diff`。
⇒ **reviewer 无需**向实现者索取额外材料即可开审。

---

## 3. 请勿做的事（明确边界）

- **不得**因 owner 已批准 `D-W05` 就认为 I-05-C 已验收 ⇒
  `status` 维持 `review_pending`，须由 **独立 reviewer** 出结论。
- **不得**为 GAP-2 造绿色样例、假称 LLM 已验。
- **不得**把 hermetic 假服务的通过**外推**为真实 LLM / 投资研究质量通过。
- **不得**以「按最佳实践」代替 schema 决定。
- **不得**把 `missing / unsupported / not_applicable` 混为一类。

---

## 4. 回执要求

- **落点**：`execution_runs/I-05-C/a20260919-01/` 下各卡自己的载体
  （`decision.md` / `review.md` / `handoff.json` / 新建 `rulings_*.md`），**不在本函上签字**。
- 每项须含：**选择 · 理由 · 反例 · 兼容影响 · 恢复规则 · 被拒绝的替代方案**。
- **GAP-2**：请给出**精确入口路径**，或明确写下「维持 blocked 及其解除条件」。
- **GAP-3**：请给出**已批准/需修改的字段清单**（含 `call_status` 闭集）。
- 完成后通知编排层，由其在本目录 `RESPONSES.md` 登记一行，**不改一字裁决内容**。

---

## 5. 本函的自证（起草动作）

| 项 | 值 |
|---|---|
| 起草人 | 编排层（owner 执行人，**非**收件方、**非**签署者） |
| 授权依据 | `OWNER_DECISIONS.md` §13 **T2-14** / **T1-2** |
| 引用前像 | `execution_runs/I-05-C/a20260919-01/handoff.json` 7087 B（`status = review_pending`，`reviewer_status = pending`） |
| 本函写入了什么 | 仅新增本 `outward_requests/` 目录下的文件；**未修改**任何载体、产品源码、门 |
| 不产生 | 任何裁定、任何签名、任何 `status` 变化 |
| 本函**不**做的 | 不代替 RF `consumer_analysis` owner 提供入口；不代替 reviewer 批 schema |

---

## 更新（2026-09-22，追加式更新段）

> **性质**：本节系 2026-09-22 更新 pass（`OWNER_DECISIONS.md` §十八 C「更新函件」）在原函**之后追加**；原函正文逐字节未动（前缀证明见本目录 `_provenance.json` 的 `updates_2026_09_22`）。以下事实取自本计划记录并注明出处；本节**不新增、不删改任何待裁项**。

### 一、I-05-C 相关修复状态（截至 2026-09-22）

1. **四项交付面修复已在代码中完成（隔离树）并经独立复审**：REM-11（`bundle=None` 路径仍返回完整下游闭包）、REM-12（`w05b-regression` 绑 I-05-B 陈旧 iso 字节）、REM-13（docstring 仍述旧闭包语义）、REM-14（retry-count-vs-artifact-count 证据行错配），由 B3 卡（`execution_runs/B3-I05C-delivery-fixes/a20260921-01/`）在隔离副本修复；独立复审 = **ACCEPT**（全部 9 项声明经独立重跑证实，登记册 §十【收尾批】），卡状态 `accepted_scoped`（晋升清单 B-2 块）。
2. **B3 的三项后置条件（RF-1/RF-5/CF-1 = REM-47/48/49）已关闭**：由 B3-PREREQ 卡修复、独立复审 `accepted_scoped`、载体落定后按登记册权关闭（登记册 §二十三、§二十四）；五系计分板记「B3 系 ✅ 全套」，含原始 ACCEPT 回填与 REM-47/48/49 父关闭（§二十七）。
3. **owner 已批准晋升，REM-49 注释修复随批**：`OWNER_DECISIONS.md` §十八「B: 全批」批准 §十七 B-1…B-7（含 B-2 = B3 系）；§十七 B-2 记「REM-47/48/49 已关；REM-49 硬前置已满足于 fixed2」，登记册 §二十四记「REM-49 是 B3 晋升的硬前置已满足于 fixed2」，晋升清单（`6759d1eb…`）行 B-2 条件明记 REM-49 comment fix (fixed2) **rides same batch**；执行卡 `PROMOTION-EXEC` 已按该清单派出（登记册 §三十三）。清单量取时生产目标仍为 UNFIXED——**批准在手、执行卡已派；本节不声称晋升已落生产**。
4. **必须说清的边界**：REM-11…14 是 I-05-C 的**交付面/证据面**缺陷（登记册 §二表，卡项 P2-1/P2-2/P3-1/P3-2），**不是**本函的 GAP-2/GAP-3。就 GAP-2（`consumer_analysis` producer 不存在）与 GAP-3（`InvocationTracker` 事件 schema 待批）本身而言，本计划记录（登记册 §十八–§三十二、`OWNER_DECISIONS.md` §十五–§十八）**没有**新的裁定或状态变化记载；起草方不把上列修复表述为 GAP-2/GAP-3 已解。
5. 上述修复与晋升状态**是否改变贵方对本函 GAP-2/GAP-3 的裁定需要，由贵方决定**；起草方不代为判断、不预设结论。

### 二、对原函的影响

原函全部请求项（GAP-2 四问：精确入口路径 / DAG 入边 / LLM 能力边界 / 角色缺失语义；GAP-3 四项 schema 确认；§3 请勿做的事；§4 回执要求与落点）**原样保留**。

**原函请求项不变，以上更新供贵方在裁定时一并知悉。**
