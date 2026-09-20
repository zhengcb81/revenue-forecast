# oracle.md — I-06-A / a20260919-01（运行前冻结的独立预期）

状态：**冻结**。冻结时点 = 本文件写入时刻。此前的 `scripts/w06a_make_fixture.py` 只生成固定样本与
TEST-ONLY 的 filing-fetch 替身，未调用被测实现；`before/`（原始产品字节）与 `after/`（attempt 内候选副本）
的判据全部取自本文件第 3 节的预注册表。

**重要范围声明**：D-W06 **未签**（见 `decision.md`）。因此本 attempt 的产品改动 = **零**；
`after/` 的候选结论只证明"冻结要求可实现且可观察"，**不**证明产品已实现 I-06-A。

---

## 0. 卡片义务与本文件覆盖范围

| 卡片条目 | 本文件对应 |
|---|---|
| W06A-P1：合格来源但 not_reviewed，从实际 source-preparation CLI 发起 | 第 3.1 节 B1 / C1 |
| W06A-P2：退出进程后第二进程重提完全相同需求 | 第 3.2 节 B2 / C2+C3+C4 |
| W06A-N1：source/hash/policy 或请求角色集合改变 | 第 3.3 节 C5+C6 |
| W06A-N2：持久 DB 写失败/数据非法/权限不足 | 第 3.4 节 C7 |
| W06A-N3：worker 处于 paused | 第 3.5 节 全过程 paused 字节不变 |
| 共同证据外还须保存三份 JSON | `demand.cross-process.json`、`request-to-demand-binding.json`、`paused-before-after.json` |

不属于本卡：真实审核执行与"从原请求恢复"（I-06-B）；这里**不**声称任何 review 已完成、不伪造 `not_detected`。

## 1. 冻结指纹

### 1.1 锚点与隔离

| 项 | 值 |
|---|---|
| RF `scripts/source_preparation.py`（**被测入口**） | `5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46` |
| RF `scripts/processing_demand.py`（第二个内存实现） | `fcdfcad8ebd1fc20febf3c157dcd20ad92708fd69d00373ef9a943e5a820afc1` |
| CW `src/company_wiki/source_catalog/processing_demand.py`（wiki 内存实现） | `90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b` |
| 解释器 | `<attempt>/iso/venv/Scripts/python.exe`（同 I-05-A，模板 `0e818a1f…42cd`） |
| 产品副本（原始） | `<attempt>/iso/rf`（RF 最小树：scripts + SKILL.md + CHANGELOG.md；`scripts` 为生产字节副本） |
| 产品副本（候选） | `<attempt>/iso/rf_fixed`（`iso/rf` 的克隆 + 候选 overlay；`iso/candidate-manifest.json` 记 hash） |
| 候选模块 | `<attempt>/iso/candidate/processing_demand_store.py`、`w06a_candidate_patch.py`（**未批准，不是产品决策**） |
| TEST-ONLY filing-fetch 替身 | `<attempt>/iso/ff/scripts/fetch_filing.py`（无网络、无 worker；从 `W06A_HANDLE_JSON` 原样读取 handle） |
| 隔离公司仓 | `<attempt>/iso/cw/src`（供 `company_wiki_source._dag_closure` 导入 `artifact_dag`） |

### 1.2 固定样本

| 样本 | sha256 | 说明 |
|---|---|---|
| `samples/source_bytes.txt` | `80a76889bdafda4ae14d66429082ca33f41cfd3174fe61ef8f2a40d2bc643d71` | "已落盘"的原件字节；其 hash 即 handle 的 `snapshot_sha256` |
| `samples/request.json` | 见 `before/case_results_baseline.json` | 用户请求：`{as_of_date: 2026-09-19, document_kind: annual_report, entity: 翡翠矿业}` |
| `samples/handle.json` | 见 `before/case_results_baseline.json` | capture_ready handle + `resolution_envelope`（`download_events=0`、`parser_calls=0`、`llm_calls=0`、`prompt_injection_status="not_reviewed"`、`bundle.valid_handles.normalized`） |
| 变更源（N1 用） | 运行期生成于 `%TEMP%\w06a\…\source_bytes_changed.txt`，hash 记在结果 JSON 的 `changed_source_bytes_sha256` | 同 policy、同角色集，只有字节不同 |

## 2. 被测断言的语义（冻结）

1. **"持久需求"的判据（本 attempt 冻结的定义）**：另一个进程在**不共享内存**的前提下，能读到一个包含
   `source_id`、`source_sha256`、`review_policy`、`role_set`、结构化 `gaps`、`request_sha256`（原请求绑定）
   与下一动作的记录，且 `status` 处于 active（pending/running/failed）。
   该定义来自卡片 W06A-P1 的字段清单，**不**引用任何现有产品 API（现在没有这种 API）。
2. **幂等键（冻结的候选三元组）**：`(source bytes sha256, review_policy, role_set)`。
   注入点、键的权威位置与表结构属 D-W06 未签项，本 attempt 只作为候选。
3. **顺序可观察**：安全阻断的**判定文本不变**（`prompt_injection_status=not_reviewed` 仍在错误里），
   但登记必须发生在阻断**之前**，所以阻断消息里应能看到 demand 标识。
4. **禁止项**：不得静默回退内存；不得把未审原文标为安全；不得自动 resume/启动 worker。

## 3. 预注册判据（冻结；before/after 均在此之下判定）

### 3.1 W06A-P1 正例（B1 / C1）

- **B（原始产品）预期**：CLI 退出码 3；stderr 恰为
  `{"error_code":"upstream","error":"prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)"}`；
  stdout 为空；**无任何持久需求**（进程退出即不可恢复）。
  → PASS 条件：以上全部成立。若出现持久需求，则基线已经满足本卡（走"无需修改的复验"）。
- **C（候选）预期**：退出码仍为 3；stderr 仍是**同一条**安全阻断（同一前缀），
  且额外包含 `demand_queued`、`demand_id=`、`gaps=`、`next_action=`、以及 paused 说明；
  结构化失败时**不**出现 `demand_queued`。
  → PASS 条件：上述全部成立，且 DB 中出现恰好 1 条 active 需求。

### 3.2 W06A-P2 正例：跨进程幂等（B2 / C2+C3+C4）

- **B 预期**：第二个独立进程得到与 B1 完全相同的阻断；仍然零持久需求；
  两次运行不能给出"同一 active demand ID 可读且只有一项待办"。
- **C 预期**：
  - C3（第二个独立进程，同一 request/handle）退出码 3，且其 `demand_id` **等于** C1 的 `demand_id`；
  - C2 与 C4（**第三个进程**，只做查询）返回 0，且 `len(demands) == 1`，`status` 为 active；
  - C4 的 `updated_at >= C1 的 created_at`（重复请求被登记为同一项，不是每进程 `pd-0`）。
  → PASS 条件：以上全部成立。

### 3.3 W06A-N1 负例：源 hash / policy / 角色集合改变（C5+C6）

- **C 预期**：C5 使用**不同字节**（新 hash）的同一文档，退出码 3，得到**不同于** C1 的 `demand_id`；
  C6 查询返回 2 条 active 需求，两条的 `demand_key` 不同（旧需求**未**被新回执关闭）。
  → PASS 条件：两条记录都在、`status` 均为 active、旧记录的 gaps 仍指向 review 缺口。

### 3.4 W06A-N2 负例：持久 DB 写失败（C7）

- **C 预期**：把 `RF_W06_DEMAND_STORE` 指到一个**位于普通文件之下**的路径（`mkdir`/打开必然失败）后，
  退出码 3；stderr 中出现 `demand could not be registered durably` **且不出现** `demand_queued`；
  安全阻断文案与判定不变；DB 行数不增加；**不得**出现内存回退的痕迹（例如仍报告排队成功）。
  → PASS 条件：以上全部成立。

### 3.5 W06A-N3 负例：worker 处于 paused（全过程）

- 冻结：`iso/rf` 与 `iso/rf_fixed` 都**不含**真实 worker 控制文件；本 attempt 在 `%TEMP%` 建
  `worker_control.json`（`desired_state="paused"`）并以 `RF_W06_WORKER_CONTROL` 指向它。
- **预期**：所有 case 前后该文件的**字节完全相同**（`sha256` 与内容均不变）；
  候选只**报告** paused 与"resume 需显式授权动作"，不自动 resume、不启动后台。
  → PASS 条件：`paused_unchanged == true` 且错误文案包含 paused 说明。

### 3.6 附加探针（`c8`/`c9`）：同 source/policy/角色但**不同请求**

本探针不在卡片固定样本内，是实现在发现候选键的薄弱点后**追加**的记录性探针（有 findings，不是达标条件）：

- 冻结的问题：候选幂等键 = `(source_sha256, review_policy, role_set)`，**不含请求**。
  因此"同一份原文、同一策略、同一角色集，但请求不同（实体/as_of_date 变化）"时，
  候选会**复用**既有 demand，并把文档中记录的 `request_sha256` 留在**第一次**的请求上。
- 记录判据（不做 PASS/FAIL）：`c8` 的 `demand_id` 是否等于 `c1` 的；`c9` 的行数；
  两条 `request_sha256` 是否都等于**原始** `samples/request.json` 的 canonical hash
  （若是，则新请求未被绑定——这正是 OPEN-2 需要裁决的点）。

### 3.7 独立复算（reviewer 应至少重算一项）

- 用**普通 sqlite3**（不经候选 API）打开 DB，核对 `processing_demands` 行数与
  `demand_key`（按 `canonical_sha256({source_sha256, review_policy, role_set})` 独立重算）。
- 核对 `source_sha256` 等于 `samples/source_bytes.txt` 的实际 sha256（`80a76889…3d71`）。

## 4. 未签专业决策（不实施，交由 reviewer）

D-W06 的下列字段**未签**，因此**没有任何产品仓改动**；全部候选选择写在 `decision.md`，附选项/后果：

- OPEN-1：唯一持久 owner 的位置（CW `store.py` 扩展表 / CW 新模块 / RF 侧 DB 文件 / 复用现有 SQLite catalog）。
- OPEN-2：表/migration/API 与幂等键的权威定义（本 attempt 冻结的候选三元组是否被采纳）。
- OPEN-3：跨进程 claim/lease/完成规则（是否复用现有内存队列的状态机语义）。
- OPEN-4：审核方法、reviewer 身份、双绑定与失效条件。
- OPEN-5：消费/恢复命令与原请求恢复接口（当前**不存在**，不得假装存在）。
- OPEN-6：`not_detected` / `detected_and_ignored` 的判定归属。

---

# 附录 A（追加式，2026-09-19 复审后；**不修改上面已冻结的正文**）

复审结论：**I-06-A = blocked（保持 blocked）**，附 F-I06A-01..05；F-I06A-06/07 复审判定 PASSED
（attempt 内写未批准候选、产品仓 0 改动**不**违反"D-W06 前不得实施"；候选必须保持 UNRATIFIED）。

## A.1 复审新增/更新的判据

| id | 复审内容 | 本 attempt 的处置与判据 |
|---|---|---|
| F-I06A-01 (high) | 同 source/policy/role_set 仅 `as_of_date` 变（2026-09-19→2027-03-31）⇒ 复用同一 `demand_id`，行内 `request_sha256` 仍是第一次请求 | 新增真实 CLI 探针 `c10`（rc=3）+ 第三进程查询 `c11`。独立重算两个 request 的 canonical sha256 并记录：原 `d8afcf319185da071bd364c5d2ef6dfa9264e8bbc929ee737b9cefab963bdd62`、仅 as_of 变 `4bddf9e6963e7d0474e754a89a1a184d8315b059410e98d34dd3e02375e10b84`。**该 case 与 c8/c9 一并写成 D-W06 OPEN-2 的必答依据**（见 decision.md），本 attempt 不自决 |
| F-I06A-02 (medium) | store 写失败时 `prompt injection not reviewed` 完全不在 stderr，与 oracle §3.4"安全判定文案不变"不符 | 已修候选：登记失败**不再抛走安全判定**，而是把 `demand_store_error=…` 作为**同一条阻断的附加子句**；`demand_queued` 在该情形**不出现**。判据（新）：C7 的 stderr 必须同时包含 `prompt injection not reviewed` **与** `demand_store_error=`，且**不含** `demand_queued`；rc 仍为 3；0 行落库 |
| F-I06A-03 (medium) | decision.md/review.md 引用留存证据中不存在的 demand ID | 已改：全部叙述改用**该次留存的真实 ID**（`demand-84179f79057143d4` / `demand-1f24…` 系列会随每次运行变化，故文档改为引用 `after/demand.cross-process.json` 而不是硬写字面量） |
| F-I06A-04 (low-med) | `role_set` 只来自环境变量；且候选默认 `"normalized,summary,sections"` 与 commands.json 用的 `"normalized,sections"` 不一致 | 候选默认值统一为 `"normalized,sections"`；该维度写进 D-W06 OPEN-2 待裁项（角色集合的权威来源与规范化形式） |
| F-I06A-05 (low) | 缺 `recovery/` | 已补 `recovery/README.md`（NA + 理由） |
| F-I06A-06/07 | 复审判定 PASSED | 候选继续标注 `UNRATIFIED`；`handoff.json` 明确"不得被后续卡直接提升为产品实现" |

## A.2 不变的基线反例（复审确认成立）

两个独立进程运行真实 `source_preparation.py`：rc=3/3、stderr 字节相同、**零持久需求**
（`before/demand.cross-process.json.database_exists=false`）。本轮重跑后仍成立。

## A.3 本附录不改动的部分

`oracle.md` 正文 §3.1–§3.5 的候选判据除 F-I06A-02 的 C7 判据被本条强化外，其余不变；
`decision.md` 的候选实现仍为 **UNRATIFIED**，产品仓仍为 **零改动**。

## A.4 C7 判据强化（F-I06A-02）

C7（持久 DB 写失败）的判据更新为**必须同时成立**：

1. rc=3；
2. stderr **同时包含** `prompt injection not reviewed`（安全判定不变）与
   `demand_store_error=demand_store_unavailable:`（结构化失败）；
3. stderr **不含** `demand_queued`（需求未持久化）；
4. DB 行数不增加；无内存回退痕迹。

原 §3.4 只写了"不报告 demand_queued / 结构化失败"，未要求安全判定文案仍在，故 r1 候选
把安全判定"吞掉"也满足旧判据；本条为复审 F-I06A-02 的更正，**追加**而不改写 §3.4 原文。
