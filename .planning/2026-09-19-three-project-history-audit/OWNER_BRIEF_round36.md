# Owner 裁决包（Round 36 整理；Round 37 已更新）

**生成时间**：2026-09-20（round 36）；**最近更新**：2026-09-20 16:45（round 37）
**生成者**：父代理
**用途**：把当前**唯一阻塞整体推进**的决策项集中成一份可逐条批注的清单。
**性质**：本文件只做**汇总与导航**，不产生任何新裁决。每条的权威出处均已给出，裁决须写回原载体。

---

## 0. 总览

| # | 项目 | 卡 | 卡状态 | 阻塞类型 | 需要谁 | 结果 |
|---|---|---|---|---|---|---|
| A | `D-W05` producer entry 批准 | I-05-C | `review_pending` | 授权缺失 | 项目 owner | ✅ **已批准**（2026-09-20 16:45） |
| B | `D-W06` OPEN-1…OPEN-6 签署 | I-06-A | `blocked` | 决策缺失（**OPEN-2 为决定性**） | wiki 来源审核 owner + 安全 reviewer + RF 消费 owner | ⏳ 待签 |
| C | I-08-A 收口方式 | I-08-A | `review_pending` | **路径性**（reviewer 禁止写入「已接受」） | 项目 owner + 安全 reviewer | ⏳ 待定 |
| D | 6 张卡陈旧 `reviewer_status` 对齐 | M09–M12 / I-14-B / I-15-A | 均 `accepted_scoped` | 字段滞后 | 派实现者即可，**无需 owner** | ⏳ 待派 |
| E | I-00-A 补裁决 | I-00-A | `review_pending` | 待独立结论 | 独立 reviewer | ⏳ 待审 |
| F | 未建 21 张卡推进 | I-10-A … I-17-B | 未建 | 排期 | 项目 owner 确认起点 | ⏳ 待定 |

**当前盘上口径**：已建 **65/86**；`accepted_scoped` **61** / `review_pending` **3** / `blocked` **1** / 未建 **21**。

**Round 37 变化**：**A 项已裁定** —— owner 原话「批准 D-W05」。I-05-C 的 `GAP-1` 由 `blocked` 转 **UNBLOCKED**（可进入真实实现），
但 **`GAP-2`（RF `consumer_analysis` owner 未提供 entry）仍硬阻塞该角色**，`GAP-3`（事件 schema）待 reviewer。
**`status` 保持 `review_pending`** —— 批准是授权，不是验收。

---

## A. `D-W05` producer entry 批准 —— ✅ 已批准（2026-09-20 16:45）

> **Owner 原话**：「批准 D-W05」

**已批准的实质**：I-05-C 的 `produce_for_demand` 可从 **mock-only** 转为**真实实现**，
接进 CW `service.py` 的现有 producer（`CatalogConfig`/`CatalogStore`）；**不新增重复 parser**；
调用事件记录在**实际调用边界**（不从结果表倒推）。

**登记位置**：
- 载体：`execution_runs/I-05-C/a20260919-01/handoff.json` → `rulings_applied["D-W05_producer_entry"]`，并把 `GAP-1.status` 改为 `UNBLOCKED…`
- 裁定单：`OWNER_DECISIONS.md` 新增「十二、【已裁定·第三批】」
- 证据：`.planning/_pwf_tmp/d_w05_approval_provenance.json`、`d_w05_gap1_status_provenance.json`

### 本批准**不覆盖**的范围（如实保留，不得外推）

| ID | 内容 | 状态 |
|---|---|---|
| **GAP-2** | `consumer_analysis` producer **不存在**；真实 LLM 能力未验证 | **仍阻塞** —— 须 **RF `consumer_analysis` owner 提供入口**；**不得造绿色样例补全** |
| **GAP-3** | `InvocationTracker` 事件 schema 需 reviewer 批准后方可生产持久化 | **待 reviewer 决定** |

---

## A-0. 原始申请内容（留档）

**权威出处**：`execution_runs/I-05-C/a20260919-01/decision.md`、`handoff.json`

**卡本身已完备**：`decision.md`（65 行，四项决策）、`oracle.md`、`commands.json`、
`producer-invocations.json`、`requested-role-dag-matrix.json`、`retry-count-vs-artifact-count.json`、`second-reuse.json`。
命令实测：`w05c-main-tests` **19 passed** / `w05b-regression` **20 passed** / `w05c-regression-fc904` **11 passed**。

**已就绪的设计结论（等待被批，不是等待被设计）**：
1. **Active DAG 改写**：`summary→[markdown]` 改为 `summary→[normalized]`；历史 `markdown` 角色保留在 dict 中供兼容读取，但**不再是任何活跃 producer 链的必需项**。
2. **`select_artifact_roles` 的 `producer_events` 作用域**：只含**被请求**的角色，不含全下游闭包（现为 `_dag_closure(role)` 全量，会把未请求的 `consumer_analysis` 也拉进来）。
3. **调用计数机制**：新增 `produce_for_demand()` 包装，记录**真实调用事件**，不以 artifact INSERT 数充当调用次数。
4. **不新增重复 parser**：复用 `normalize_catalog` / `extract_sections_catalog` / `summarize_catalog`。

**三项待决（卡内 `remaining_gaps` 原文）**：

| ID | 级别 | 内容 | 状态原文 |
|---|---|---|---|
| GAP-1 | P2 | `produce_for_demand` 生产实现：测试中仅 mock。真实实现需 CW `service.py` 集成 `CatalogConfig`/`CatalogStore` | ✅ **UNBLOCKED** 2026-09-20（D-W05 已批） |
| GAP-2 | P2 | `consumer_analysis` producer **不存在**；测试只证明 missing/unsupported 处理；真实 LLM 能力未验证 | `blocked on RF consumer_analysis owner providing entry` |
| GAP-3 | P3 | `InvocationTracker` 事件 schema 需 reviewer 批准后才能做生产持久化 | `pending reviewer decision` |

**需要 owner 做的**：批准 `D-W05` producer entry（含消费侧 entry）。**GAP-2 另需 RF `consumer_analysis` owner 提供入口**。

---

## B. `D-W06` OPEN-1…OPEN-6 签署 —— 解锁 I-06-A

**权威出处**：`execution_runs/I-06-A/a20260919-01/decision.md`（124 行，逐项列了选项与后果）

**重要前提**：`decision.md` 开宗明义 **「本文件不是决策签署」**，且**产品仓改动 = 0**。
attempt 内只有一份 **UNRATIFIED 候选实现**，用于证明冻结要求可实现、可观察、可跨进程验证。

**现状（改动前实测）**：RF `scripts/source_preparation.py` 的 `_preparation_demands` 是**模块级内存队列**；
两个独立进程对同一 request 都得到同一条阻断且**零持久需求**；RF 与 CW 各有一份**纯内存** `DemandQueue`。

### OPEN 清单（每条都给了选项 / 后果 / 建议）

| ID | 主题 | 本 attempt 建议 |
|---|---|---|
| OPEN-1 | 唯一持久 owner 的位置 | 候选人令形状为 B；**建议采纳 A**（扩展 CW `source_catalog/store.py`，复用既有 migration 机制） |
| **OPEN-2** | **表 / migration / API 与幂等键的权威定义** | **决定性项，见下** |
| OPEN-3 | 跨进程 claim/lease/完成规则 | 需决定是否复用内存队列状态机语义；lease 过期回收是否自动 |
| OPEN-4 | 审核方法、reviewer 身份与失效条件 | **完全未定**；I-06-B 依赖此项 |
| OPEN-5 | 消费/恢复命令与原请求恢复接口 | **当前不存在**（不得假装存在） |
| OPEN-6 | `not_detected` / `detected_and_ignored` 判定归属 | 安全 reviewer 决定：命中时隔离（默认）还是"有证据地忽略" |

### OPEN-2 为何是决定性的

候选幂等键 = `sha256(canonical_json({source_sha256, review_policy, role_set}))` —— **不含请求身份**。

**三个独立实测反例**（走真实 `source_preparation.py` CLI，rc=3）：

| case | 变化 | 结果 |
|---|---|---|
| `c8`/`c9` | 同 source/policy/roles，`entity` 与 `as_of_date` 都变 | 返回**与 c1 相同的 `demand_id`**；该行 `request_sha256` 仍是第一次请求 |
| `c10`/`c11` | 同 source/policy/roles，**只有 `as_of_date` 变** | 同样复用同一 `demand_id`；行内 `request_sha256` 与 `request_hashes.asof_only_changed` **不一致** |

⇒ **不同请求被静默并入同一需求**。这不是实现 bug，而是 OPEN-2 键定义未定导致的必然结果，
且候选的键**不满足**卡片 W06A-P1 的「含原请求绑定」要求。

**为何执行者不自行修**（原文）：把请求身份加进键会立刻改变「重复请求幂等」的语义（W06A-P2 要求同一请求复用同一项），
并决定「同一份原文在不同 as-of 下应否拆成两个需求」—— **这是业务语义，属 D-W06 待裁项，不得由执行者自选。**

**同时待裁**：`role_set` 的权威来源与规范化形式（当前只从 `RF_W06_ROLE_SET` 环境变量读，默认 `normalized,sections`）；
以及 c7 情形下错误文案的对外契约（安全判定 + `demand_store_error=` 附加子句）。

**需要谁签**：wiki 来源审核 owner + 安全 reviewer + RF 消费 owner。
**签署前**：I-06-A 保持 `blocked`，候选保持 `UNRATIFIED` 且**不得被后续卡直接提升为产品实现**。

---

## C. I-08-A 收口方式 —— 路径性阻塞，与别卡不同

**权威出处**：`execution_runs/I-08-A/a20260919-01/review.md` §5.5、`handoff.json`

**特殊性**：该卡的 reviewer **明文禁止**把「已接受」写入任何载体。
故其 `reviewer_status` 字段虽已记录「独立 reviewer 已于 2026-09-20 出具 `accepted_scoped`，
范围限设计/契约提案，逐字记录于 `review.md` §5.5」，但**该字段明确声明它不把 status 置为 accepted**。

⇒ **不得走常规「`handoff.status = accepted_scoped`」收口路径**，须单独商定收口方式。

**另有一批 OPEN 待裁（D1–D7）**，其中 D1/D2/D3 有**成组约束**：

| ID | 内容 | 裁决者 | 备注 |
|---|---|---|---|
| D1 | 权威信任根（仓配置文件 / 机器级只读路径 / OS keystore） | 项目 owner（安全/运维提选项） | **D1/D2/D3 须一组成批裁**，否则 I-08-B 要重做信任域 |
| D2 | 谁可持有 L3 私钥、一人可否多钥、是否需双人控制 | 项目 owner 政策 | 同上 |
| D3 | 密钥吊销是否追溯使已发布物失效（设计默认：否） | 项目 owner + 独立安全 reviewer 二次检查 | 同上 |
| D4 | 新增 `publication_attestation` 子对象是否把 `PUBLICATION_RECEIPT_SCHEMA_VERSION` 升到 2.0（推荐）还是留 1.0 加可选键 | revenue publication owner **可单独决定** | 无需上报 |
| D5 | 消费侧降级开关 `require_attestation=False` 是否保留、谁可授权、是否必须留痕（现存于 `invest_contracts.py:1070-1071`，未修改） | invest-core 消费 owner + revenue publication owner 共同 | — |
| D6 | 谁落消费侧 schema 3.8 opt-in 门（规则已冻结于 `decision.md` §6.3，但实施需改跨仓 `invest_contracts.py:1116-1127`，超出本卡范围） | 计划 owner 决定并开卡 | — |
| D7 | 三个数值参数**无证据支撑**：W（发布窗口，E18）、T（provider 超时上限，E07）、L（provider stdout 上限，E06；早前硬编码 65536 已在 r3 撤回） | owner 选证据基准，实现者供测量 | — |

---

## D. 6 张卡陈旧 `reviewer_status` 对齐 —— **无需 owner，派实现者即可**

`status` 与 `reviewer_status` 存在**直接矛盾**，且该字段属**实现者字段**（非裁决字节）：

| 卡 | `status` | `reviewer_status`（现状原文） | 矛盾点 |
|---|---|---|---|
| `M09` | `accepted_scoped` | ✅ **已对齐**（round 38）：`RESOLVED -- independent review round 1 returned accepted_scoped (granted: formula only)`，指向载体报告行 20 | 原称「未收到裁决」，已订正 |
| `M10` | `accepted_scoped` | 同上 | 同上 |
| `M11` | `accepted_scoped` | 同上 | 同上 |
| `M12` | `accepted_scoped` | 同上 | 同上 |
| `I-14-B` | `accepted_scoped` | `r1 review returned changes_required (… verdict section 1). T…` | 停留在 r1 的 `changes_required` |
| `I-15-A` | `accepted_scoped` | ✅ **已对齐**（round 38）：`RESOLVED -- the r2 independent review returned accepted_scoped, scoped to frozen evidence + diagnostic counterexamples ONLY` | 原称「待审」，已订正 |

**修复纪律**：**只改 `reviewer_status` 这一个字段，不动任何裁决字节**（`review.md` 正文、封盘时间、清单均不得触碰）。
`M09–M12` 的裁决出处为 `evidence/<CARD>/reviewer_report_m09m12.md`（40679 B / `5a44fd4e…`，已登记 `in_card_verdict_region=false`）。

---

## E. I-00-A 补裁决

**现状**：`review_pending`；盘上最新独立结论仍为 `changes_required`。
**性质**：该卡限定只读基线。**需独立 reviewer 出结论**，owner 不直接改写。

---

## F. 未建 21 张卡

`I-10-A`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B`（含 `I-10-M25M28` 占位目录）。
**需 owner 确认起点**（建议 `I-10-A`）后按调度表推进。

---

## 附：读盘纪律（本计划已登记的全部四条）

1. **顶层 `status` 必须 `json.load` 取**，不得 `grep -m1'"status"'` —— 该键在内部子对象中大量重用。
2. **`git status --porcelain` 的 `' M'` 不是内容差异的证据** —— 实测 146 条中 79 条（54%）为 index 陈旧伪差异；判据用 `git diff HEAD --name-only`。
3. **不得用「on-disk 字节 == blob」作恢复判据** —— 本仓库 `core.autocrlf = true`，须用 `git diff <ref> -- <path>` 是否为空（裸字节比对曾误报 62 例假失败）。
4. **判定「文件为何变了」必须看 `git reflog` 的 `checkout: moving from … to …`** —— 不得只用「它变成了什么版本」。
