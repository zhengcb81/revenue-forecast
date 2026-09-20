# review.md — I-06-A / a20260919-01

> ## PENDING independent review
> **本文件由实现者撰写，不构成任何验收结论。** 实现者未自签 `accepted`、未写 `passed`。
> 独立 reviewer 必须自己重算至少一个专属 oracle，并攻击文末列出的案例。
> **r2（2026-09-19，复审后）：复审结论 = blocked（保持 blocked）**，附 F-I06A-01..05；
> 已逐条处置（F-I06A-06/07 复审判定 PASSED）。逐条 file:line、新 raw rc 与新哈希见
> 同目录 eview_r2_disposition.md\；产品仓仍为**零改动**，候选保持 **UNRATIFIED**，
> **不得被后续卡直接提升为产品实现**。

- card: I-06-A（parent I-06），attempt `a20260919-01`
- 状态：`review_pending`；**产品仓改动 = 0（D-W06 未签）**

## 1. 我实际做了什么（可核对清单）

1. 隔离环境：`iso/venv`（同 I-05-A，模板解释器 `0e818a1f…42cd`）、`iso/rf`（生产 `scripts/` 的字节副本 +
   SKILL.md/CHANGELOG.md）、`iso/cw/src`（wiki `src/` 副本，供 `artifact_dag` 导入）。
2. TEST-ONLY filing-fetch 替身 `iso/ff/scripts/fetch_filing.py`：**无网络、无 worker、无 provider**，
   按真实调用约定（`--config/--timeout-seconds` + stdin request）从 `W06A_HANDLE_JSON` 原样返回 handle。
3. 固定样本：`samples/request.json`、`samples/source_bytes.txt`（`80a76889…3d71`）、`samples/handle.json`
   （`resolution_envelope`：`download_events=0`、`parser_calls=0`、`llm_calls=0`、`prompt_injection_status="not_reviewed"`）。
4. `before/`（**原始产品字节**）：两个独立进程跑**真实** `source_preparation.py`，两次都 rc=3、
   同一条 `not_reviewed` 阻断、**零持久需求**（`before/demand.cross-process.json.database_exists=false`）。
5. 候选 overlay（`iso/candidate` → 克隆 `iso/rf_fixed`）：登记移到阻断之前；失败即抛（不回退内存）；
   阻断文案携带 `demand_queued/demand_id/gaps/next_action` 与 paused 说明。**未改安全判定、未写产品仓。**
6. `after/`：C1..C7 全部按 oracle 判定通过；`after/cmd-tests-demand.stdout.txt` = 现有 ZR-507 内存合同 14 passed。

## 2. 正例 / 负例逐条预期与实际

| case | 冻结预期（oracle §3） | before（原始产品） | after（候选，UNRATIFIED） |
|---|---|---|---|
| B1/C1 合格来源 not_reviewed | rc=3；阻断文案不变；登记在阻断前 | rc=3、阻断、**零持久需求** | rc=3、同一阻断前缀 + `demand_queued demand_id=…` |
| B2/C3 第二进程重提同一 request | 同一 active demand ID | 再次 rc=3、仍零持久需求 | 同一 `demand-4d7be1d6f4514a7c` |
| C2/C4 第三进程查询 | rc=0 且 `len(demands)==1` | 无查询接口可用（无 DB） | rc=0、1 条 active（重复后仍 1 条） |
| C5 改变 source hash | 新 demand、旧需求不被关闭 | 无需求可谈 | 新 `demand-017c1ed335de4b04`，两条并存 |
| C6 变更后查询 | 2 条 active，key 不同 | 同上 | 2 条，key 不同 |
| C7 持久 DB 写失败 | 不报告 `demand_queued`，结构化失败，不静默回退 | 无需求机制 | `demand could not be registered durably`，无 `demand_queued`，DB 行数不变 |
| N3 worker paused | 前后字节/哈希完全不变，不自动 resume | 未接触 worker | 前后字节/哈希不变，只报告 paused |
| 伪造 review | 不得出现 | 无 review 行 | 无 review 行（gaps 只记 `not_reviewed`） |
| **c8/c9 附加探针**（同 source/policy/角色、**不同请求**） | 记录性（无 PASS/FAIL） | n/a | **候选复用 c1 的 demand**（`demand-9892a84494194365`）——见 §4.9 |

## 3. 独立复算（我不会用它替代 reviewer 的复算）

- `after/demand.cross-process.json.independent_key_check`：直接用**普通 sqlite3** 读表，再独立重算
  `canonical_sha256({source_sha256, review_policy, role_set})`，2/2 与记录一致；
  `source_sha256` 等于固定样本文件与变更样本文件的实际 sha256。
- `after/request-to-demand-binding.json`：`request_sha256` 独立重算，2/2 匹配；gaps 原样记录 `not_reviewed`。
- `after/paused-before-after.json`：前后内容与 sha256 相等；真实 worker control 从未被触碰。

## 4. 已知局限 / 未验证（如实列出）

1. **D-W06 未签 → 没有产品实现**。本 attempt 只证明"冻结要求可实现且可观察"。
   `iso/candidate/*` 与 `iso/rf_fixed/*` 是 **UNRATIFIED 候选**，不是决策，也不得据此开始实施。
2. **filing-fetch 是 TEST-ONLY 替身**（正式脚本在 `<attempt>/iso/ff/scripts/fetch_filing.py` 开头即声明）。
   真实 provider/market 路由不在本卡范围（I-07）。
3. **未测并发 claim**：候选的 `claim(owner, lease_seconds)` 只做了单进程验证；跨进程竞争/租约过期未测。
4. **未测迁移**：候选表是新建的；对既有 catalog 的 additive migration 未实现（属 OPEN-1/2）。
5. **CW 侧没有单一持久 owner**：本 attempt 未在 CW 写任何东西；`iso/cw` 只有 I-05-A 的 `src` 副本 + 为
   C7 复制的一份测试文件。
6. **`RF_W06_*` 环境变量注入点是候选选择**，不是冻结契约；D-W06 必须决定真实接线方式。
7. **`role_set` 的语义**：候选用 `RF_W06_ROLE_SET` 环境变量（固定 `normalized,sections`），
   并非从请求/信封推导；键因此对"角色集合变化"只做了**形式**验证（改 env 即改键），
   未做"同一 request 在不同角色需求下应否拆成两个 demand"的语义判断。
8. **阻断文案变长**：候选在错误消息里加了 demand 信息，可能影响既有消费者对 stderr 文本的断言；
   本 attempt **未**搜索 RF 中对该文案的文本断言（reviewer 应检查）。
9. **候选的请求绑定是自证的薄弱点（实测反例）**：探针 `c8` 用**同一 source bytes / policy / 角色集**、
   但请求字段不同（`entity`、`as_of_date` 变化）再跑一次真实 CLI，候选返回了**与 C1 相同的
   `demand_id`（`demand-9892a84494194365`）**，并且 `c9` 中该行记录的 `request_sha256` 仍等于**原始**
   `samples/request.json` 的 canonical hash。
   即：**新请求被静默并入旧需求**。卡片 W06A-P1 要求需求"包含…原请求绑定"，
   候选实现只满足"记录了某次请求的绑定"，**不满足**"绑定的是本次请求"。
   这是本 attempt 已知的最严重缺陷，属 OPEN-2 必须裁决的键定义问题（键是否包含请求身份）。
   证据：`after/case_results_candidate.json.cases.c8_*`、`c9_*`；`after/request-to-demand-binding.json`。
   实现者**不**把它标为通过，也不通过改键来掩盖（改键等于自行决定 OPEN-2）。
10. **`role_set` 只来自环境变量**（`RF_W06_ROLE_SET`），未从请求/信封推导；因此"角色集合变化"这一维度
    只在形式上成立，语义上未接线（见 §5 attack 3）。

## 5. reviewer 请优先攻击

1. **C7 的失败路径真实性**：把 store 路径指向一个**存在但只读**的目录（而非"位于文件之下"），
   验证候选是否仍拒绝而不回退；再构造"DB 文件存在但 schema 不兼容"的情形。
2. **C3 的"同一 demand"是否只是字符串相等**：请在同一 request 下改变**非键字段**（例如 `request` 中的
   `entity` 字段但保持 source/policy/roles），判断应否复用；当前候选复用（因为 request 不参与键），
   这可能与卡片"原请求绑定"的要求冲突——**这是我最担心的一处**。
3. **`role_set` 来源**：构造两个角色需求不同的请求（同一 source/policy），验证是否应产生两个 demand；
   当前候选只有改环境变量才能做到，说明该维度未被真正接线。
4. **阻断文案兼容性**：搜索 RF/FF 中对 `prompt injection not reviewed` 的文本断言与消费者。
5. **worker 语义**：验证候选是否在任何路径上触碰 worker_control（应只有 `read_worker_control`）；
   并确认没有后台线程/进程被创建。
6. **`gaps` 的完备性**：候选只对 `normalized/summary/sections/markdown` 与 review 生成 gap；
   判断是否遗漏 `consumer_analysis` 或"缺文本/工具版本"等 gap（OPEN-4）。
7. **是否真的"没有第二套持久实现"**：本 attempt 在 attempt 内写了候选模块；
   请判断这是否违反"D-W06 前不得实施"的边界（我认为不违反，因为零产品写入，但需 reviewer 确认）。
