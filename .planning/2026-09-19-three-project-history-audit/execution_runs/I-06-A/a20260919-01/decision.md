# decision.md — I-06-A / a20260919-01（D-W06 专业决策）

实现者：本 attempt（wiki 持久需求 owner / RF 消费实施者角色）。
**本文件不是决策签署。** D-W06 要求"先指定单一持久 owner 与迁移及 API；没有 schema 不能让执行者自行选
SQLite/文件队列"（card_I-06-A 按序执行第 1 条），因此：

> **产品仓改动 = 0。** 本 attempt 只在 attempt 目录内写了一份 **UNRATIFIED 候选实现**，
> 用于证明冻结要求可实现、可观察、可跨进程验证；它不是产品决策，也不得据此开始实施。

## 0. 现状（改动前，实测）

| 事实 | 证据 |
|---|---|
| RF `scripts/source_preparation.py` 的 `_preparation_demands = DemandQueue()` 是 **模块级内存队列**；`_submit_preparation_demand` 在 `raise`（not_reviewed）之后 | 源码 sha256 `5ec16eaf…ce46`；`before/cli-logs/b1-first-run/stderr.txt` |
| 两个独立进程对同一 request + 同一 handle 都得到同一条阻断，且**零持久需求** | `before/case_results_baseline.json`、`before/demand.cross-process.json`（`database_exists=false`） |
| RF 与 CW 各有一份 **纯内存** `DemandQueue`（同一语义、两套实现、无持久化） | RF `fcdfcad8…afc1`；CW `90f232ed…3c8b` |
| 现有 14 项 ZR-507 合同测试只覆盖内存状态机 | `after/cmd-tests-demand.stdout.txt`（14 passed） |

## 1. OPEN 决策（必须由 wiki 来源审核 owner + 安全 reviewer + RF 消费 owner 签署）

### OPEN-1：唯一持久 owner 的位置

| 选项 | 内容 | 后果 / 兼容性 |
|---|---|---|
| A | 扩展 CW `source_catalog/store.py`（catalog.sqlite3 增表 + `_apply_additive_migrations`） | 复用既有 migration 机制；但需求与"文档目录"生命周期绑定，prune/archiving 会连带影响；CW 是卡片建议方向（"选定 company-wiki 单一持久需求 owner"） |
| B | CW 新模块 + 独立 SQLite 文件（catalog 同级） | 与 I-15-A 的 prune 解耦；需要新的 owner/初始化路径与 doctor 检查 |
| C | RF 侧独立 DB 文件 | RF 变成唯一 owner，与"CW 单一 owner、RF 只提交/查询"的建议冲突；跨仓查询需要 RF 常驻 |
| D | 复用现有 JDBC/JSONL 文件队列 | 需要自建原子写与锁；并发正确性风险最高 |

**本 attempt 的候选实现选 B 的形状**（独立 SQLite 文件 + stdlib 锁语义），仅因为它在 attempt 内最容易隔离验证。
**建议采纳 A**（卡片建议 + 复用既有 migration 纪律），但这必须由签署者决定。

### OPEN-2：表 / migration / API 与幂等键的权威定义

候选（本 attempt 冻结的三元组，实测可用）：
`demand_key = sha256(canonical_json({source_sha256, review_policy, role_set}))`，
其中 `review_policy = envelope.policy_hash`，`role_set = 逗号分隔的请求角色集`。
候选表 `processing_demands(demand_id, demand_key, kind, status, source_id, source_sha256, review_policy,
role_set, gaps_json, request_sha256, request_json, candidate_marker, attempts, lease_owner, lease_until,
created_at, updated_at)`。
**需要签署者明确**：键是否包含 `original request binding`（本候选用 `request_sha256` 记录但不参与键）、
`role_set` 的规范化形式、以及 status 枚举是否复用既有 `pending/running/completed/failed/terminal_failed`。

> **实测反例（本 attempt 的 `c8`/`c9` 探针）**：同一 source bytes / policy / 角色集、但请求不同
> （`entity` 与 `as_of_date` 变化）时，候选返回**同一个** `demand_id`，且该行记录的 `request_sha256`
> 仍是**第一次**请求的 hash——**新请求被静默并入旧需求**。
> 即：候选的键**不满足**卡片 W06A-P1 的"含原请求绑定"要求。
> 这不是实现 bug，而是 OPEN-2 键定义未定导致的必然结果；签署者必须先裁决"请求身份是否参与键、
> 以及不参与时如何避免静默合并"。证据：`after/case_results_candidate.json`（c8/c9）、
> `after/request-to-demand-binding.json`。

### OPEN-3：跨进程 claim/lease/完成规则

候选人令 `claim(owner, lease_seconds)` 是**显式**单次授权（CLI `claim`），不自动恢复 worker。
需要签署者决定：是否复用现有内存队列的状态机语义（dedupe/lease/backoff/attempt cap），
以及 lease 过期回收是否自动、由谁触发。

### OPEN-4：审核方法、reviewer 身份与失效条件

仍然完全未定：审核方法（哪个检测器/工具/版本）、reviewer 身份如何绑定、`source_sha256` 与 `policy_hash`
的双绑定形式、以及"策略变更后旧回执失效"的判定。I-06-B 依赖此项。

### OPEN-5：消费/恢复命令与原请求恢复接口

**当前不存在**（不得假装存在）。候选只提供 `list` / `claim` 两个只读/单次授权命令；
"从原请求恢复"的接口（把 demand 变回一次成功的 source preparation）未实现。

### OPEN-6：`not_detected` / `detected_and_ignored` 判定归属

安全 reviewer 决定：检测命中时是隔离（默认）还是"有证据地 detected_and_ignored"。
本 attempt 只把 `observed: "not_reviewed"` 原样记录到 gap，不产生任何 review 结论。

## 2. 候选实现（UNRATIFIED）实测结论

候选 = `iso/rf_fixed`（`iso/rf` 的克隆）+ `iso/candidate/processing_demand_store.py` +
`w06a_candidate_patch.py`（不改安全判定，只把登记移到阻断之前）。
候选与原件的完整差异见 `changes.diff`。

实测（`after/case_results_candidate.json`、`after/demand.cross-process.json`）：

| 判据 | 结果 |
|---|---|
| C1 合格来源 not_reviewed，登记发生在阻断前 | 退出码 3；错误含 `demand_queued demand_id=… gaps=4 next_action=…`；安全判定文本不变 |
| C2+C4 第三个进程可读，且只有 1 项待办 | 查询 rc=0，`len(demands)==1`（重复请求后仍为 1） |
| C3 第二个独立进程重提同一 request | 得到**相同的** `demand_id`（`demand-4d7be1d6f4514a7c`） |
| C5 改变 source hash | 新 `demand_id`（`demand-017c1ed335de4b04`）；旧需求**未**被关闭 |
| C6 变更后查询 | 2 条 active，`demand_key` 不同 |
| C7 持久写失败（store 路径位于普通文件之下） | 退出码 3；`demand could not be registered durably`；**无** `demand_queued`；DB 行数不变 |
| N3 worker paused | 全 case 前后 `worker_control.json` 字节与 sha256 完全不变；只报告 paused 与"需显式授权" |
| 未伪造 review | 全程零 review 行、零 `not_detected` |
| 幂等键独立复算 | 普通 sqlite3 读取后独立重算 `canonical_sha256(...)`，2/2 与记录一致 |

**候选不证明的东西**：不证明 schema/事务边界正确（D-W06 未签）、不证明并发 claim 正确（未测并发 claim）、
不证明 CW 侧 owner 存在、不证明真实审核可执行、不证明能从原请求恢复。

## 3. 恢复规则（本 attempt 差异）

- 生产仓零写入：`iso/rf` 与 `iso/cw` 都是 attempt 内副本；`iso/rf_fixed` 是克隆。
- 撤回：删除 `iso/rf_fixed` 与 `iso/candidate` 即可，产品仓无需任何动作。
- 迁移失败/损坏：候选 DB 只存在于 `%TEMP%\w06a\…`，删除即可；未触碰任何生产 pending。

---

### OPEN-2 必答依据（复审 F-I06A-01 + 本 attempt 的 c8/c9/c10 实测）

**问题**：候选的幂等键 = `(source_sha256, review_policy, role_set)`，**不含请求身份**。
签署者必须裁决：请求身份是否参与键；若不参与，如何避免"不同请求被静默并入同一需求"。

**三个独立实测（全部走真实 `source_preparation.py` CLI，rc=3；留存于
`after/case_results_candidate.json` 与 `after/demand.cross-process.json`）**：

| case | 变化 | 结果 |
|---|---|---|
| `c8`/`c9` | 同 source/policy/roles，`entity` 与 `as_of_date` 都变 | 返回**与 c1 相同的 `demand_id`**；该行 `request_sha256` 仍是第一次请求 |
| `c10`/`c11` | 同 source/policy/roles，**只有 `as_of_date` 变**（2026-09-19→2027-03-31，复审给出的构造） | 同样复用同一 `demand_id`；`request_hashes.asof_only_changed = 4bddf9e6963e7d0474e754a89a1a184d8315b059410e98d34dd3e02375e10b84` 与行内 `request_sha256 = d8afcf319185da071bd364c5d2ef6dfa9264e8bbc929ee737b9cefab963bdd62`（第一次请求）**不一致** |

**为什么本 attempt 不自行修**：把请求身份加进键会立刻改变"重复请求幂等"的语义
（W06A-P2 要求同一请求复用同一项），并决定"同一份原文在不同 as-of 下应否拆成两个需求"——
这是业务语义，属 D-W06 待裁项，不得由执行者自选。

**同时待裁**：`role_set` 的权威来源与规范化形式（当前候选只从 `RF_W06_ROLE_SET` 环境变量读取，
默认已统一为 `normalized,sections`），以及 c7 情形下错误文案的对外契约
（安全判定 + `demand_store_error=` 附加子句，见 r2 处置）。
