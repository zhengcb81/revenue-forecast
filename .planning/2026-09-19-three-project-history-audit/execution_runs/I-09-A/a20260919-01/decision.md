# decision.md — I-09-A / a20260919-01

**卡片**：I-09-A「先定结果包提交、读可见性与幂等协议」（父项 I-09）
**角色**：revenue 发布负责人（独立签名/事务 reviewer）
**本文件性质**：**决策提案 + 开放项登记**。它**不是**签署文件，也不是 accepted。见 §0。

---

## 0. 状态与签署边界（先说清楚谁签什么）

| 项 | 状态 |
|---|---|
| 本 attempt 的协议条目 C-01…C-13 | **提案已冻结**（`oracle.md` §5，写于任何运行之前；`C-13` 为独立对抗式复核后**追加**，见 `errata.md`）；**待独立 transaction reviewer 裁定** |
| 新增错误码 `I09-E01…E10` | 提案；与 I-08-A 的 E01–E32 **不共用命名空间**（隔离声明见 `oracle.md` §5.1）。**不得**因勘误而改动 |
| 实现者是否签署 accepted | **否**。本文件不含任何 accepted/passed 自签 |
| 是否需要 owner 裁定 | **是**：OPEN-I09A-1…6（§7 与 `open_items.md`）；其中 **4 项**（-1/-2/-3/-5）阻塞 I-09-B 的绑定 |
| 勘误 | 独立复核 verdict = `changes_required`（文档/勘误层，证据层不需重跑）；逐条处置见 `errata.md`。**勘误不构成重新验收** |

**本卡不实施产品**（卡执行门 + `START_HERE.md` 第 5 行「先写 decision.md…之后再实施」）。产品仓改动 = **0**。

---

## 1. 现状事实（实测，改动前）

全部来自 `after/probe_commit.stdout.txt`、`after/probe_summary.stdout.txt`、`after/probe_registry_fault.stdout.txt`、`before/baseline_hashes.txt`。源码锚点与卡正文逐字一致（`revenue_core.py` `1821fd2a…`、`revenue_forecast.py` `6b3d960e…`、`publication_registry.py` `44662744…`），**无漂移**。

| # | 事实 | 证据 |
|---|---|---|
| **N-1** | 生产 registry 60 行、链自洽；**57 行 forecast 的 `artifact_id` 全为 `null`**；非空 `artifact_id` 共 **3 行**（全部 `snapshot`、**同值** `47a46003e300d4972db50d36f65f94525ee470fcd4742b1c61921b42b8626788`）——即**没有任何一行 forecast 携带可寻址身份**。（原写"只有 1 行"是把去重值数当行数，已勘误：`errata.md` E-1） | `before/baseline_hashes.txt`（sha256 `bc3256bb…`）+ PowerShell 独立复算（本次复核重数：非空 3 / null 57 / distinct 1） |
| **N-2** | 同一 `(input,result,engine,schema,artifact_type)` 组最多出现 **6** 次，31 组里 21 组 >1；`audit()` 对此**不报冲突**（设计如此） | 同上 |
| **N-3** | **提交先于产物**：输出写失败时 rc=2，但 registry 已有 1 行、`is_registered=true`、消费者可见 `commit_qualified=1`，而磁盘上**零个真实成员** | c02（`out.json` 位置为目录，真实 WinError 5） |
| **N-4** | **第二成员缺失仍算已提交**：JSON 已落盘（94614 B）、Markdown 写失败（rc=2），registry 1 行、读者 `commit_qualified=1` | c03 |
| **N-5** | **registry 不可达时是 fail-closed**：真实 ACL 拒绝 → rc=2、无输出文件、0 行 | c04b（`b_registry_acl_denied`） |
| **N-6** | **stdout-only 正式发布**：rc=0、registry 1 行、磁盘上零成员 → 「已提交」的包没有任何可校验产物 | c05 |
| **N-7** | `--validate-only`（draft）**零 registry 副作用** | c06 |
| **N-8** | 同一请求跑两次 → 2 行、anchor/result 相同、`audit()` 不报冲突 → **无法区分「重试」与「两次事件」** | c07/c08 |
| **N-9** | 请求**仅** `as_of_date` 不同（`2026-09-19` vs `2027-03-31`）→ `input_sha256` **不同**（`4df1ec74…` vs `6ebc0c5b…`），0 冲突 | c09/c10（真实 CLI） |
| **N-10** | 库调用者可以手工拼一个「anchor 属于请求 A、结果属于请求 B」的 result，`register_publication` **rc=0 落行成功**，registry 无任何字段能指出该错配 | c11 |
| **N-11** | `create_snapshot` 一次调用产生 **2 行**（forecast + snapshot，同 registry）；snapshot 行**无** `validation_status` | c12 |
| **N-12** | 两个真实进程并发 `_append`（同一 gate 释放、同一 registry）本次**都成功**，2 行、链自洽 | `probe_report.json.concurrency`（**单次运行，不能证明无锁安全**） |
| **N-13** | `REVENUE_PUBLICATION_REGISTRY` 指向**目录**时被静默重解释为「目录根」，真 registry 变成嵌套同名文件并**成功**写入（rc=0） | `probe_registry_fault.stdout.txt` → `a_path_as_directory` |
| **N-14** | 正式路径**已**强制 `input_sha256 == canonical_sha256(input_document)` | `trust_anchor.py:verify_input_binding`，由 `revenue_report.py:validate_published_forecast` 调用 |

**N-14 的重要性**：本计划先例（I-06-A OPEN-2：幂等键不含请求身份 → 不同 `as_of_date` 复用同一 `demand_id` 且携带首个请求的 `request_sha256`）在**正式 CLI 路径**上**不会**以同样形态出现，因为 `input_sha256` 覆盖整个请求文档且被强校验。**但这个不变量目前只存在于「调用者自觉」层面**：registry 不校验（N-10），`is_registered` 不看载荷（F-2），也没有任何字段把「哪一次请求」持久化。所以 I-06-A 的缺陷类在本系统里的**真实形态**是：

> **一个已提交的、可被消费者查询到的发布，无法证明它是哪一次请求的产物，也无法证明它的成员是完整的。**

---

## 2. 决策 D-1：一个 publication 的身份

### 2.1 选项

| 选项 | 内容 | 后果 |
|---|---|---|
| **A（采纳）** | 新增 `publication_id` = `canonical_sha256({"publication_id_schema_version": "1.0", **identity_payload})`，`identity_payload` 精确字段集 = `identity_schema_version` / `request` / `artifact_type` / `artifact_id` / `engine_version` / `schema_version` / `receipt_schema_version` / `package_target` / `members` | 身份可寻址、与机器无关、可被消费者独立复算；需在 registry 行追加键 |
| B | 继续用 `input_sha256` 当身份 | 已被 N-1/N-8/N-10 证伪：57 行 `artifact_id=null`，且同 anchor 可承载任意 result |
| C | 用 `result_sha256` 当身份 | 把「产出什么」和「哪次发布」混为一谈：幂等重试（同请求、同结果）会变成新身份；且 result 在 commit 前必须已知，等于把身份依赖于执行完成 |
| D | 复用 `snapshot` 的 `snapshot_id` 形状 | `snapshot_id` 绑定 `forecast_result_sha256`（`revenue_backtest.py:46-58`）→ 与 C 同病；且它属于 backtest 域，不是发布域 |

### 2.2 理由

1. **必须可被独立复算**：身份的全部输入都必须是**消费者手上就有的字节**（请求文档、schema/engine 版本、成员角色名）。C/D 依赖「结果字节」，而结果字节正是需要被验证的东西 → 循环。
2. **必须与机器/目录无关**：因此 `members` 只存**相对角色名**，不存绝对路径（否则同一发布在两台机器上是两个身份）。
3. **必须能区分「哪一次请求」**：`request` 子对象同时放 `request_sha256`（全覆盖）与可读身份字段（`company_name`/`as_of_date`/`forecast_version`/`schema_version`/`fiscal_year_end`/`currency`/`unit`）。只放 hash 也能区分，但**不可读**，事故复盘时无法一眼看出「这是哪个 as-of」。
4. **`engine_version`/`schema_version`/`receipt_schema_version` 参与**：同一请求在不同引擎/schema 下是**不同发布**（`audit()` 的 generation 语义已如此，N-2），保留它才不会把两代产物折叠。
5. **`artifact_type`/`artifact_id` 参与**：forecast 与 snapshot 共用同一 registry 与同一 anchor（N-11），不区分就会把 snapshot 当成 forecast 的同一身份。

### 2.3 反例（这一决策可能错在哪）

| 反例 | 若成立则说明 |
|---|---|
| R-1 同一请求在两台**不同目录**下发布，身份应相同（否则同一逻辑发布被拆成两个） | `package_target` 必须是**逻辑目标名**（如 `company=<x>/as_of=<d>/formal`）而**不是**路径；若 reviewer 认为目标名也无法跨机器稳定，则 `package_target` 必须移出身份 → **改 C-01** |
| R-2 同一请求在**同一台机器**上发布到两个不同目录（例如 `out/a.json` 与 `out/b.json`），消费者应视为同一发布 | 与 R-1 冲突。二者只能选一，必须由 reviewer 裁定 → **OPEN-I09A-2** |
| R-3 消费者只拿到一个结果文件、拿不到请求文档 | 则它**无法**复算身份，只能信任 registry 行；这削弱「独立复算」但不破坏「不可静默合并」（因为合并判据在写入侧） |
| R-4 `receipt_schema_version` 升版（I-08-A OPEN-D4）后，历史发布的身份应**不变** | 采纳 A 会让身份改变 → 历史行需要「旧身份保留、不重算」的兼容规则（已写入 §5 兼容矩阵） |

### 2.4 兼容影响

- **registry 行新增键**（追加式，旧行保持可读，符合 I-08-A §10 第 6 项与 R1.2 的追加键先例）。
- **receipt 不变**：`publication_id` **不进** `publication_receipt`（receipt 已有 `receipt_sha256` 与 `validated_payload_sha256`；贸然加键会动 `PUBLICATION_RECEIPT_SCHEMA_VERSION`，属 I-08-A OPEN-D4 的范围，本卡不得越权）。
- **不改变** `result_sha256` 语义：仍覆盖整个 result（含 receipt）。
- 与 **I-08-A OPEN-D4** 的耦合：身份含 `receipt_schema_version` → D4 未裁前**不得**把身份值写进任何规范常数表。

### 2.5 恢复规则

- 身份是**纯函数**：无需恢复，可随时重算。
- 若某行缺少 `publication_id`（历史行）：**不得**事后补算并写成「一直如此」；只能标为 `identity_unknown`（见 §5 兼容矩阵）。

### 2.6 被拒绝的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 只加 `request_sha256` 到行里，不引入 `publication_id` | 不足以回答「这条行是不是一次**已提交**发布的成员」（P-D1 的形状）；也不能区分 forecast/snapshot（N-11） |
| 把身份写进**文件名** | 身份需要覆盖「成员集合与版本」而不只是路径；且文件名是文件系统的属性，会被复制/改名绕过 |
| 用**自增序号**当身份 | 跨进程/跨机器不唯一，且不能从输入复算 |
| 用 `uuid4()` 当身份 | 同上；且幂等重试会产生新身份，直接破坏 C-08 |
| 把 `result_sha256` 也放进身份（「更保险」） | 见 C-03：会让幂等重试变成新身份，与 I-08-A §5「同输入重跑 = 新行 + 旧行保留」的审计意图冲突 |

### 2.7 C-01 的强制附注（独立复核后**追加**，C-01 正文一字未改）

> **C-01-附注（强制）**：`identity_payload` 的字段集**封闭**；I-08-B 的 attestation 锚（以及任何未来行内键）**不得**进入 `identity_payload`——否则一次**重签**就会改变发布身份，直接破坏 C-08 的幂等语义。当 `receipt_schema_version`（I-08-A **OPEN-D4**）或行 schema 升版时，**历史行的身份一律不重算**：旧行保留其原 `publication_id`，新行使用新版本。
> **「历史行身份不重算」由倾向提升为强制条款**（复核裁定意见②），并与 I-08-A OPEN-D4 **同批裁决**。
> 字段分工必须显式列出：**参与身份** = `identity_payload` 的九个字段（C-01 点名）；**不参与身份但随行持久化** = `members` 的路径映射（`member_paths`）、`member_sha256`、`attempt_seq`、`state`、`supersedes`、attestation 锚。归属：`OPEN-I09A-3`。

---

## 3. 决策 D-2：幂等（重复提交 / 重放如何判定与去重）

### 3.1 冻结判据

1. `idempotency_key = canonical_sha256({"idempotency_key_schema_version": "1.0", "publication_id": <id>})`。
2. **键相同 ⇒ 同一逻辑发布**（重试/重放）。允许的行为是：**幂等返回既有 committed 结果**（可追加一条**审计行**，但必须携带同一 `publication_id` 与递增 `attempt_seq`）。
3. **键不同 ⇒ 不同发布**。**禁止**复用已提交身份承载另一份载荷。
4. **`publication_id` 相同但 `result_sha256` 不同** ⇒ `I09-E05`（幂等键重用），拒绝。
5. **同一 `publication_id` 出现第二条 committed 行** ⇒ `I09-E06`，除非协议显式允许（本卡不允许）。
6. **请求身份不参与身份的实现** ⇒ 必须能报 `I09-E03`。判据见 §3.3。

### 3.2 「逻辑幂等重试」与「允许的重复审计行」分别定义

| 概念 | 定义 | 计数口径 |
|---|---|---|
| 逻辑发布（logical publication） | 由 `idempotency_key` 识别的单元 | **每个键最多 1 个 committed** |
| 审计行（audit line） | registry 里的物理行 | **可 >1**（I-08-A §5 已冻结），但每行须有同一 `publication_id` 与不同 `attempt_seq` |
| committed | 一个成员齐备、hash 一致、且被某个 committed 行引用的版本 | 每 `publication_id` **恰好 1 个** |

**这直接回答卡动作 1 的「逻辑幂等重试与允许重复审计行分别定义」**：`logical_commits = distinct(publication_id where committed)`；`audit_lines = 行数`。N-8 的现状是二者**无法区分**，这正是 `publication_id` 要补的缺口。

### 3.3 本卡必须给出的「I-06-A OPEN-2 类缺陷」判据

**判据（可执行）**：给定两个提交 `S_a`、`S_b`，若 `request_sha256(S_a) != request_sha256(S_b)` 而 `publication_id(S_a) == publication_id(S_b)`，则实现**必须**拒绝 `S_b`，错误码 `I09-E03 identity_request_mismatch`。

**为什么不能只靠 `input_sha256`**：`is_registered(input_sha256)`（F-2）只看 anchor 是否出现过。若把 anchor 当身份，就得到 I-06-A OPEN-2 的同型缺陷：**两个不同请求被静默并入同一身份，而该身份行携带的是第一次请求的 `request_sha256`**。

### 3.4 反例（可证伪）

**F-IDEM（必答反例）**：`R_a`(`as_of_date=2026-09-19`) 与 `R_b`(`as_of_date=2027-03-31`)，其余字段逐字节相同。

| 检验 | 冻结期望 | 本次实测（提案实现，纯函数） |
|---|---|---|
| `request_sha256` 不同 | 必须 | `4df1ec74ea2924d86686bcb2eaccccaabb6e89c284c5a8896d9377bc2374cead` vs `6ebc0c5b74001b133c182ec7d97d1e380ce8779f32527a8766ce7b8daa0b08df` → **不同** ✅ |
| `publication_id` 不同 | 必须 | `8336b8848d6413718cd7d1367cba4d64f82138d4f097d54d74c9c41e71cbf07f` vs `1621b74c6144efc34cfc14b603efad48e2b10e9c7a75c20e6a1b8456b6aae27e` → **不同** ✅ |
| `idempotency_key` 不同 | 必须 | `59e47254a0e2ab0af0ed404d28c1963edf5858850e8022a3fe6b0d2c64297dd9` vs `80ec2be9da0dbfe55b3393f361d5bd4e85c8f8ccdee95e0dc54545a3f4748910` → **不同** ✅ |
| 独立复算（第二次用 json+hashlib 从零重算 `publication_id`） | 必须一致 | `independent_recomputation_matches=true` ✅ |
| 同一请求两次 | 身份必须相同 | `publication_id_same=true`、`idempotency_key_same=true` ✅ |
| 仅 `company_name` 不同 | 身份必须不同 | `aa2ab31eb8ee32e88fcb88746e323ea79c81bf34eace7d66e83f5281700a4e5f` ✅ |
| `engine_version` 4.1.0→4.2.0 | 身份必须不同 | `e62a356af1dec79f4dbb244c59a0f428cfdb35ed00ec139a3ffdb0a1d7a4d211` ✅ |
| `artifact_type` forecast→snapshot | 身份必须不同 | `32a65cd1041e6f1cdedcc8925740eb58b8b97b06db93039d91973fee10d1ba7c` ✅ |

**推翻条件**：出现一次实测，其中两个请求仅 `as_of_date` 不同而得到**同一** `publication_id`（或同一幂等键）且**未**报 `I09-E03`。则 C-02/C-09 作废，必须重新裁定「请求身份是否参与身份」。

**适用范围限定（复核 E-7，必须随上表一并阅读）**：上表的 8 个检验是对 **harness 字面量载荷**的自洽性检验——`proposed_identity()` 里 `package_target="out.json"`、`members=["out.json"]` 是**硬编码字面量**，且 `members` 用的是**文件名**而非 C-04 要求的**相对角色名**。因此该表只证明「同一算法两次实现一致 + `as_of_date`/`company_name`/`engine_version`/`artifact_type` 四个维度都改变身份」，**不**证明 `package_target`/`members` 已与生产事实绑定（分别属 `OPEN-I09A-1` 与 `OPEN-I09A-3`）。**不得**据此宣称身份契约已可用于生产落地。

**F-IDEM-LIB（现状即可证伪的更强版本）**：c11 已实测——`register_publication` 接受「anchor 属 A、载荷属 B」的 result 并 rc=0 落行。故**当前实现不满足** F-IDEM 的判据（它连身份都没有）。

### 3.5 兼容影响

- 现状 60 行**没有** `publication_id`：它们**不能**因此被当作「已提交但无身份」而拒绝，也不能被补算成有身份。见 §5。
- 现有测试 `test_zr710_publication_txn.py::test_c3_...`（同输入两次 → 2 行）**不受影响**（行数不变，只是每行多一个键）。
- `audit()` 的冲突判据**不改**（N-2 的 generation 语义保留）；本协议只**新增**一个 `commit_status` 入口，不移除旧入口。

### 3.6 恢复规则

- 幂等重试**不得**修改已 committed 行（hash 链不允许）。重试只允许追加审计行。
- 若发现同一 `publication_id` 的两行 committed（`I09-E06`），恢复动作 = 追加一条 `supersedes` 补偿行（`E31` 语义），**不**编辑历史。

### 3.7 被拒绝的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 幂等键 = `input_sha256` | 就是 I-06-A OPEN-2 的缺陷形状（N-10 已证伪） |
| 幂等键 = `input_sha256 + result_sha256` | 同请求重跑若结果字节相同则为同键（可接受），但一旦 `registered_at`/签名时间进入 result，同请求重跑就会变成**新键**→ 幂等失效。故 result 不进键 |
| 幂等键 = `idempotency_key` 由调用者提供（客户端 token） | 弱模型/脚本可复用旧 token 冒充重试；身份必须可从产物复算 |
| 「同请求第二次直接**拒绝**（不允许重试）」 | 与 I-08-A §5 冻结的「同输入重跑 → 新行 + 旧行保留」冲突 |
| 「同请求第二次直接**返回缓存**且不落行」 | 会丢失审计历史（I-08-A §5 明确要求保留旧行）→ 采纳「落审计行 + 逻辑 commit 仍为 1」 |

---

## 4. 决策 D-3：结果包成员、提交语义与 stdout/库 API

### 4.1 冻结的成员表

| 成员角色 | 必需性 | 现状 | 协议要求 |
|---|---|---|---|
| `output_json` | **正式发布必需** | `--output` 有则写 | 参与身份与成员表；**必须**在 commit 前落盘 |
| `output_markdown` | 可选（请求了才必需） | `--markdown` 有则写（**第二个独立写**，N-4） | 若请求了则参与成员表；缺失 = 不可提交 |
| `registry_line` | **必需** | `register_publication` | **唯一 commit 点**的载体 |
| `receipt` | 必需 | 在 result 内（`publication_receipt`） | 随 `output_json` 一起持久化；**不单独成文件** |
| `manifest` | **明确不需要独立文件** | — | 成员表就在 commit 行里（避免多文件原子性问题）；理由见 4.4 |

**注意**：`probe_report.json.identity.payload_members = ["out.json"]`，即本次实测的成员角色名用的是**文件名**。这**满足**「与目录无关」，但**不满足**「与用户选择的文件名无关」。协议要求角色名用**稳定逻辑名**（`output_json`/`output_markdown`），把路径放到行内的独立 `member_paths` 字段（不参与身份）→ 登记为 **OPEN-I09A-3**（谁决定逻辑名清单）。

### 4.2 `--output` 缺省（stdout-only）的提交语义

| 选项 | 内容 | 后果 |
|---|---|---|
| **A（采纳）** | stdout-only **不是**可消费的 committed 正式包：`members=[]` 时**拒绝**进入 formal commit，报 `I09-E08 package_unsupported_combination`；如需正式发布必须给 `--output` | 与 N-6 的缺陷正面冲突（现状 rc=0 + registry 1 行）；需改 CLI 行为 → 属 I-09-B |
| B | 允许 stdout-only，但行内标 `state="ephemeral"`，读者不视为 committed | 保留现有用法；但「正式发布」与「临时导出」共用一个 CLI 旗标，容易误用 |
| C | 把 stdout 内容也写进 registry 行（内联载荷） | registry 会膨胀且把公司数据写进审计文件，且不解决「终端与磁盘不可能共同回滚」 |

**采纳 A**，理由：卡片原文要求「no-output/stdout 输送失败的可达保证单列，不能承诺对终端 stdout 和磁盘做不可能的共同回滚」。**终端 stdout 无法回滚**，因此协议**不承诺**「打印成功」，只承诺「committed 行的成员在磁盘上可验证」。**明确登记的保证范围**：

- **可达保证（formal）**：`output_json` 落盘 + `registry_line` 落定 → 消费者可验证。
- **不可达保证**：stdout 是否被终端/管道消费；进程在打印前被杀。这些**不进入**提交资格判据。

### 4.3 直接 `run_forecast` 库调用（无输出路径）

| 选项 | 内容 |
|---|---|
| **A（采纳）** | 库调用**只**产出「未持久化的结果」；`register_publication` **不得**由库函数隐式调用；正式提交必须经显式 commit API（带成员表） |
| B | 保留现状（`run_forecast` 内部 `register_publication`） | 就是 N-3/N-6 的成因：注册发生在还没有任何文件路径的时刻 |
| C | 库调用写一个默认路径 | 隐式写用户文件系统，最差 |

**采纳 A**。**关键约束**（卡动作 2 原文：「不可偷偷把 library 行为改成未登记还称正式」）：A **不是**「悄悄删掉库的注册行为」，而是**显式登记**为 API 兼容变更——库调用返回的对象**不再**自带提交资格，提交资格由 registry 行（含成员表）给出。该变更**必须**进 §5 的 API 兼容矩阵，并由 I-09-B 在跨仓消费者检查后实施。

### 4.4 反例

| 反例 | 若成立则说明 |
|---|---|
| R-5 某个已部署脚本依赖「`run_forecast` 返回即已注册」，去掉隐式注册会静默破坏它 | 必须在 I-09-B 前做消费者清单（`grep` 已确认仓内仅 `revenue_core`/`revenue_backtest` 调用；**跨仓 invest-core 未验**） |
| R-6 Markdown 是「可选装饰」，缺了也应算提交 | 与卡原文 P-D2「绝不见 P0/P1 混包」冲突；本协议取「请求了就必须有」 |
| R-7 成员表放行内会让行变大到影响 `_read_entries` 性能 | 60 行 × 数十字节，可忽略；但若成员数增长需重新评估 |

### 4.5 恢复规则

- `members` 中任一成员缺失/不符 → 该版本 `committed=false`；恢复动作 = 重新写成员（幂等，同 `publication_id`）或追加补偿行撤销；**不**补造缺失的正式结果（I-09-B 卡动作 5 原文）。
- stdout-only 被拒绝后**不留**任何 registry 行（fail closed）。

### 4.6 被拒绝的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 独立 `manifest.json` 文件作为提交标记 | 多文件原子性无解：manifest 与成员之间没有原子交换机制（Windows 无目录 fsync，见 D-4），会把「唯一 commit 点」变成两个 |
| 用 `os.replace` 一次性换入整个目录 | Windows 不支持目录 rename-into-place 的原子替换；跨卷更不可能（卡明确禁止假原子） |
| 把 stdout 也当作成员并回滚 | 终端不可回滚（不可能承诺） |
| 让 Markdown 失败只 warn 不算失败 | 半包可见（N-4），违反 P-D2 |

---

## 5. 决策 D-4：提交协议、唯一 commit 点、平台持久性

### 5.1 冻结的状态机

```
prepare (无 commit 资格)
  P0 validate_document / validate_published_forecast      (强验证)
  P1 构造载荷 + payload_sha256 + publication_id            (纯计算)
  P2 L3 provider 验签 → publication_attestation            (I-08-A §7 第 4 步)
  P3 validate_publication_receipt
  P4 计算成员字节 + 每个成员的 content_sha256
  P5 每个成员独立原子落盘 (同目录 tmp + fsync + os.replace)
  ---------------------------------------------------------------
commit (唯一 commit 点)
  C1 取 registry 提交锁
  C2 重新读链尾 → 组装行 (publication_id, members[], member_sha256[], attempt_seq, state="committed", attestation 锚)
  C3 append + flush + fsync   ← 单次追加 = 唯一 commit 点
  C4 释放锁
  ---------------------------------------------------------------
visible
  V1 返回成功；CLI 可选打印 stdout（不承诺）
```

**为何唯一 commit 点选在 C3**：它是现有系统里**唯一**既有「**单次追加**」又有「链式 hash 校验」的持久化动作（`_append` 的 `open("a")` + `flush` + `fsync`，且 `_read_entries` 每次全量校验链）。**注意措辞（复核 E-8）**：这里是「单次追加」，**不承诺抗撕裂**——一次追加若被中途打断而产生半行，由**链校验 fail-closed 检出**（故障点 **F7**），而不是被阻止。两个替代位置都不成立：

- 选「成员写盘全部完成」：多文件之间无原子边界（P5-a 成功、P5-b 失败 = N-4 的半包）。
- 选「回报调用者成功」：回报不是持久动作，P-D3 的崩溃点就在这里。

### 5.2 崩溃一致性假设（必须显式承认的限制）

| 假设 | 依据 | 若不成立 |
|---|---|---|
| 同卷 `os.replace` 原子 | `_atomic_write_text` 现状（REV-09/ZR-710 已验） | 跨卷必须**拒绝**（`I09-E09`），**不得**退化成 copy+replace 假原子 |
| `os.fsync(fd)` 提交文件内容 | 现状 `_append` 已用 | 若平台不保证，则 fsync 只提供「尽力」 |
| **目录 fsync 在 Windows 不可用** | 平台事实 | **不承诺**「rename 后目录项在掉电后仍存在」；掉电语义仍属 I-09-C/未验 |
| 多文件之间**没有**原子边界 | 同上 | 这正是选 C3 为唯一 commit 点的原因 |
| 跨卷**不能**用一次 rename | 卡失败停止条件原文 | 协议要求 `I09-E09` |

### 5.3 读者契约（卡动作 4）

**消费者只消费 `committed` 且各成员 hash 一致的版本**：

```
commit_status(publication_id, member_paths) == "committed"
  ⟺ ∃ 唯一 committed 行 L:
        ① L.publication_id == publication_id
        ② L.state == "committed"
        ③ ∀ 角色 r ∈ L.members: 成员存在 且 sha256(bytes) == L.member_sha256[r]
        ④ L.input_sha256 与 anchor/载荷一致（沿用 trust_anchor.verify_input_binding）
        ⑤ L 位于链自洽的 registry 中（_read_entries 已保证）
```

### 5.4 需要更新的现有入口（逐条）

| 入口 | 现状语义 | 协议要求 |
|---|---|---|
| `is_registered(anchor)` | anchor 出现过（F-2） | **保留**为「anchor 历史存在性」查询（向后兼容），但**禁止**作为 commit 资格；新增 `commit_status(...)` |
| `lookup(anchor)` | 返回该 anchor 全部行 | 保留；行内新增 `publication_id`/`state`/`members` 后，调用者可用之判 commit |
| `audit(result_files)` | 同 generation 多 result = 冲突 | **保留**；新增检查：同一 `publication_id` 出现 >1 committed 行 → 报告（对应 `I09-E06`） |
| `publication_registry.py lookup/audit` CLI | 打印/退出码 | 保留；`audit` 新增的检查**不改变**现有退出码约定（有 problem 才 1） |
| `revenue_backtest`（snapshot） | 同 registry、无 `validation_status`（N-11） | 保留兼容；snapshot 行必须带自己的 `publication_id`（`artifact_type="snapshot"`），**不得**被读成 forecast 的提交 |
| **旧 append 行（60 行）** | 无 `publication_id`/`members` | 见 5.5 兼容矩阵；**不伪造 commit 资格** |

### 5.5 API / 语义兼容矩阵（旧行如何解读）

| 行类型 | 可读 | commit 资格 | 依据 |
|---|---|---|---|
| 新行，`state="committed"`，成员齐备且 hash 一致 | ✅ | **是** | C-06 |
| 新行，`state="committed"`，成员缺失/hash 不符 | ✅（审计用） | **否**；报 `I09-E10`/`I09-E02`；`E31` 适用 | C-10 |
| 新行，审计行（同一 `publication_id`，`attempt_seq>1`） | ✅ | 是（**同一个**逻辑 commit，不增加计数） | C-08 |
| **旧行（无 `publication_id`）** | ✅ | **否**（`identity_unknown`）；**不得**事后补算、**不得**删、**不得**重签 | 卡恢复边界 + I-08-A §10 第 10 项 |
| 旧行且 `artifact_type=snapshot`（3 行，无 `validation_status`） | ✅ | 否 | I-08-A §6.4 已冻结其「不是 artifact、是注册行级旧记录」 |
| draft（`--validate-only`） | 不落行 | 不适用 | N-7 |
| stdout-only（协议 A 后） | 拒绝 | 不适用 | D-3 A |

**与 I-08-A `classify()` 的关系（关键，卡关闭标准要求「I-08 信任状态与提交状态独立且一致」）**：

| | committed（本卡） | 未 committed |
|---|---|---|
| **G2 验签通过** | 可能（正常正式发布） | 可能（**prepared 但未提交**：签名已有、成员未齐） |
| **G3a 无签名声明（含 3.7/3.8）** | 可能（发布成功但 `unattested`，N-1 的 57 行就是此类） | 可能 |
| **G1（3.0–3.6）** | **不可能**（G1 不得重签/不得新建下游；本协议不给 G1 任何提交路径） | 是（旧行 = `identity_unknown`） |
| **G4 无效** | **`identity_payload` 层面不可能**；但**「声称 `host_signed` 却无 attestation 记录」的形状当前可被接受并注册** —— 见下方降级说明 | 是 |

**G4 格的降级说明（复核 P2-3 的实测反证，必须一并阅读）**：复核人用自造边界输入实测到
`validator_accepts_host_signed_without_record=true`、`register_rc=0`、`rows=2`、`validation_status=["validated","validated"]`；
源码依据 `revenue_publication.py:222-226` **只校验 `attestation_status` 的取值合法性**，全产品 grep `publication_attestation|attestation_record` **0 命中**。
因此：

> 上表「G4 不可能」**只在本协议自身的身份/提交规则内成立**；对 I-08-A `classify()` 的 G3b/G4 而言，**该分支在生产里没有实现落点**，属**未兑现的断言**，**由 I-08-B 的 attestation 门实现；落地前不得声称已闭**。

**新增 C-13（只新增，不改 C-01…C-12）**：

> **C-13**：「receipt 声称 `host_signed` 但**无任何 attestation 记录**」的形状，在 attestation 门落地后**必须于提交前拒绝**，且**不得**被算作 committed。错误码**归属 I-08-B 的 attestation 门**定义（本卡**不**占用、**不**新造 I-08-A 的错误码号）。在 I-08-B 落地前，该形状**必须**被显式标为「兼容缺口未闭」，并在交付说明中保留上述实测反证。

**两个状态相互独立**：`committed` 只说「成员齐备且被登记」，**不**说「可信」；`G2` 只说「签名可复验」，**不**说「提交完成」。二者**不得**互相推导。R-LEGACY-1/E29 的「3.8 不获得自动旁路」在本协议里表现为：**3.8 不因为 schema 版本而获得任何提交便利**，仍须走 C1–C3 与 attestation 门。

### 5.6 恢复规则（旧包保留与撤销）

1. **旧包保留**：任何恢复动作**不得**删除或改写历史行；`_append` 的链式 hash 使改写必然被检出。
2. **撤销**：追加补偿行 `state="revoked"`、`supersedes=<被撤销行 line_sha256>`；读者按 5.3 判为不可消费。对应 `E31 publication_rollback_required`（I-08-A §2.5 明确「属 I-09-A」）。
3. **E31 的判定点**（本卡冻结）：**已 append 的 committed 行所声明的任一必需成员不存在或 hash 不符** → 必须回滚注册（补偿行），**不得**留可消费半发布。
4. **恢复再崩溃**：恢复本身是「追加一条补偿行」，因此**天然可重入**；重复执行只会产生多条补偿行（幂等：同一 `supersedes` 的补偿行第二次应被 `I09-E06` 拒绝 → 恢复必须先在锁内检查是否已补偿）。

### 5.6b 孤儿成员规则 + E31 触发语义重述（**批准 §7 改序的附带条件**；复核裁定意见①）

改序（P5 成员落盘 → C3 唯一 append）引入一个新的失败形状：**成员已落盘、但 C3 从未成功** → 磁盘上存在**孤儿成员**（无任何 committed 行声明它们）。冻结规则：

1. **孤儿成员一律不可消费**：`commit_status` 找不到 committed 行 ⇒ 消费者必须报不可消费；**禁止**「文件存在即可读」。
2. **孤儿不是资产也不是垃圾**：**不得**自动删除（可能是另一个 publication 的成员，或一次待重试的 prepare）；删除必须由显式恢复动作在锁内执行，并留痕。
3. **重试即复用**：重试同一 `idempotency_key` 时**必须**复用同一 `package_target` 与同一成员角色名，重写成员字节后再次走 C1–C3；**不得**旁路出第二套命名。
4. **孤儿判定必须可复算**：`orphan_members(package_target) = 目标目录内的成员文件 − 被 committed 行引用的成员`。审计入口（`audit`）**应当**报告孤儿数量，但**不得**在只有孤儿时把发布算成成功。
5. **不进 registry 的 prepare 状态**：孤儿**不写行**（写 prepare 行会让旧读者把它读成已提交，即 P-D1 形状，明确禁止）。

**E31（`publication_rollback_required`，I-08-A §2.5 归属本卡）触发语义重述**：

> **E31 的触发条件** = 「一条**已 append** 的 committed 行所声明的**任一必需成员**不存在、或实际 hash ≠ 行内 hash」。
> **不是**触发条件：仅有孤儿成员（无 committed 行）；仅有 prepare 失败；仅有成员写盘失败但 C3 未发生。
> **恢复动作** = 在锁内**追加**一条补偿行（`state="revoked"`、`supersedes=<被撤销行 line_sha256>`），**绝不**改写/删除历史行（hash 链不可变）；补偿后再重写成员并由新的 committed 行接管。
> **归属**：改序本身**必须由 I-08-A 的 owner 写进上游文本**（本卡只登记条件，不改 I-08-A 文档）。

### 5.7 被拒绝的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 引入 SQLite / 新数据库保存提交状态 | 卡失败停止条件与 START_HERE 均明确：弱模型**不得**自选 DB 架构 |
| 新增第二个 registry 文件（prepare 日志） | 两个文件之间无原子边界 → 又回到多文件问题；且「谁能改」的 owner 不明 |
| 把 `state="prepared"` 先写进同一 registry | **会让旧读者把 prepare 行读成已提交**（P-D1 的失败形状原样重现）→ 明确拒绝 |
| 依赖文件系统锁（`O_EXCL` 锁文件）而不动 `_append` | 锁文件与 registry 之间无原子关系；持锁者崩溃后锁残留需超时回收，等于引入第二套 lease 协议（应复用 I-04-C 的结论，而不是另造） |
| 「先把 output 写到最终位置再 register」 | **顺序反了**会制造另一种半包：磁盘有产物、registry 无行 → 消费者看不到，但审计缺失；协议要求「成员落盘（不可见）→ 一次 append 变可见」，因此成员必须写在**同一目标目录**、且只有在 append 之后才被承认为该发布的成员 |

---

## 6. 决策 D-5：跨进程串行化与链尾更新

### 6.1 现状

`_append`：`existing = _read_entries()` → 读链尾 → `open("a")` 写一行。**读与写之间没有锁**（F-1）。N-12 的两次并发**碰巧**都成功（窗口极小），**不构成安全性证据**。

### 6.2 冻结要求

1. **同一 registry 的提交必须串行化**：C1 取锁 → C2 读链尾 → C3 append+fsync → C4 释放。
2. **锁的作用域**：`<registry>.lock`（同目录文件），由 `msvcrt.locking`（Windows，stdlib）或等价 stdlib 原语提供**跨进程**互斥。**不得**引入新依赖。
3. **同一 publication 并发**（同一 `publication_id` 两个进程）：串行化 + C-08 幂等判据 → **恰好 1 个 committed**，第二个退化为审计行或返回既有结果。
4. **不同 publication 并发**：允许并行到 C1 之前（验证/成员落盘可并行）；C1–C4 串行。
5. **锁获取失败**：可重试至超时，超时报 `I09-E07 publication_lock_contention`。**不得**在失败后无锁 append。
6. **持锁者崩溃**：Windows 的 `msvcrt.locking` 由 OS 在进程退出时释放 → 无需超时回收。**但**这条**未实测**（本卡不实现锁）→ 标为 I-09-B 必验项。
7. **跨卷**：`package_target` 与 registry 不同卷时，成员落盘与 registry 追加无法共享同一原子域 → 报 `I09-E09`，**不得**假装原子。

### 6.3 反例

| 反例 | 若成立则说明 |
|---|---|
| R-8 两个进程同时取锁，一个在 C2 读到旧链尾 | 锁未覆盖「读链尾」→ 会产生 `prev_line_sha256` 相同或链断；必须由 I-09-C 的真实两进程压测覆盖 |
| R-9 `msvcrt.locking` 在**同一进程内**多线程不可重入 | 若未来有线程并发，需要进程内锁 → 登记，不在本卡范围 |
| R-10 网络盘（SMB）上 `locking` 语义弱 | 协议不承诺网络文件系统；须**显式拒绝或标注不支持** → 归 OPEN-I09A-4 |

### 6.4 被拒绝的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 不加锁，靠 `open("a")` 的 O_APPEND 原子性 | `_append` 的**链尾读取**不是原子的；两行可能引用同一 `prev_line_sha256` → 链断（可检出不等于可接受） |
| 用「重试直到链自洽」代替锁 | 会**重复追加**（同一发布多行），把幂等问题变成并发问题 |
| 每个发布者写独立文件再合并 | 等于新建第二套 registry（被拒） |
| 用文件时间戳/`mtime` 做乐观并发 | 精度不足（Windows 上可能出现相同 mtime），且不是原子判据 |

---

## 7. 逐故障点固定 oracle（卡动作 6 要求「签署故障点表」）

`rc` 一栏 = **producer 进程退出码**；「可见版本」= 读者进程判定。**A** = 本卡冻结预期（提案）；**E** = 本次实测（`probe_commit`/`probe_registry_fault`）。`n/a` = 本卡未实测（I-09-C 范围），**不得**当作通过。

| # | 故障点 | 冻结预期（A） | rc（A） | 恢复动作（A） | 本卡实测（E） |
|---|---|---|---|---|---|
| F1 | prepare 前（输入强验证失败） | provider 调用 0、registry 新增 0、无成员 | 2 | 无（fail closed） | 未构造（I-08-A A-D4 已覆盖同类） |
| F2 | prepare 中（载荷/身份计算失败） | 同上 | 2 | 无 | n/a |
| F3 | JSON 落盘失败（P5-a） | 无成员可见、无 committed 行 | 2 | 重试写成员 | ✅ c02（rc=2；但**现状**仍留 1 行 → 见 F9） |
| F4 | Markdown 落盘失败（P5-b） | 同上（成员不齐 ⇒ 不可提交） | 2 | 重试写 Markdown | ✅ c03（rc=2；**现状**读者仍见 commit_qualified=1） |
| F5 | registry 锁获取失败 | 无 committed 行 | 2 | 超时后重试 | n/a（锁未实现） |
| F6 | registry append 前崩溃 | 无 committed 行；成员成为**孤儿**（不可消费） | — (kill) | 孤儿清理或重写 | n/a（I-09-C） |
| F7 | append 写了一半（torn line） | 链校验失败 ⇒ 整个 registry 不可读（fail closed） | 2 | 人工介入/从备份修复 | n/a（现状 `_read_entries` 会报错） |
| F8 | append + fsync 完成、回报前崩溃 | **已 committed**；重试必须得到**同一**逻辑 commit | — (kill) | 幂等重试 | 部分：N-8 显示现状无身份 ⇒ 重试不可判定 |
| F9 | 成员已落盘、registry append 失败 | 无 committed 行（成员不可见） | 2 | 重试 append | ✅ c04b（rc=2、无输出、0 行） |
| F10 | commit 可见后、返回前崩溃 | 已 committed；读者可见；调用者未知 | n/a | 幂等重试（同 `publication_id`） | n/a（I-09-C） |
| F11 | 恢复过程再崩溃 | 补偿行半写 ⇒ 链断 ⇒ registry 不可读 | — | 重入恢复（先查是否已补偿） | n/a（I-09-C） |
| F12 | stdout 输送失败（管道关闭/终端退出） | **无保证**（不可达保证，D-3 C-12 明列） | 0 或 2 | 无 | 未构造（不可承诺） |

**结论**：F3/F4/F9 三点的**现状行为**与冻结预期**相反**（现状：提交先于产物；预期：产物齐备才提交）。这三条正是 I-09-B 的实现目标。

---

## 8. 与 I-08-A 契约的一致性检查（逐条，含冲突登记）

| # | I-08-A 冻结项 | 本卡如何消费 | 冲突？ |
|---|---|---|---|
| A1 | 错误码 E01–E32 单一来源 | 只引用 `E31`；新增码一律 `I09-E**`（10 个，不同前缀） | 无 |
| A2 | `classify()` G1/G2/G3a/G3b/G4 | 提交状态**独立**（§5.5 矩阵）；G1/G4 **不可能是** committed | 无 |
| A3 | `host_signed` 只能由 L3 验签产出（R-PROV-1） | 提交动作**不产生** `host_signed`；`attestation_status` 仍由 L3 决定 | 无 |
| A4 | 信任域键名 `public_keys` | 不触碰信任域加载 | 无 |
| A5 | R-LEGACY-1 / E29（3.8 属 G3a，无自动旁路） | 3.8 **不获得**任何提交便利；G1 集合无提交路径 | 无 |
| A6 | §7 顺序「验证→签名→注册→写 output」+ 第 8 步补偿 | 本卡要求改为「验证→签名→**成员落盘**→**唯一 append**」；§7 第 7 步「写 output」在 append 之后 | ⚠️ **次序修正**，需 reviewer 明示确认 → **`OPEN-I09A-6`**（原误指 `-1`/`-2`，两项问题陈述均不覆盖次序；勘误见 `errata.md` E-3） |
| A7 | §6.4（registry 行不含签名/attestation 字段）+ §10 第 6 项（I-08-B 要加 attestation 锚） | 本卡新增 `publication_id`/`state`/`members`/`member_sha256`/`attempt_seq`/`supersedes`；I-08-B 的 attestation 锚需与之**合并字段集**、一次升版 | ⚠️ 需字段集合并，否则两次追加会打架 → **OPEN-I09A-3** |
| A8 | §5「同输入重跑 → 新行 + 旧行保留」 | C-08 沿用，并加 `publication_id` 使「重试 vs 新发布」可区分 | 无 |
| A9 | OPEN-D4（receipt schema 是否升 2.0） | 身份含 `receipt_schema_version` | ⚠️ **未决依赖**：D4 未裁前不得冻结生产身份值 → **OPEN-I09A-1** |
| A10 | E31 「属 I-09-A」 | §5.6 给出判定点与补偿机制 | 无（本卡履行归属） |
| A11 | 参数 `W`/`T`/`L`（OPEN-D7 未裁） | 本卡**不使用**这三个参数；提交协议不引入新数值 | 无 |

---

## 9. 本卡范围外但已登记的事项

| 事项 | 归属 |
|---|---|
| `registry_file()` 把「目录」当根 → 静默重解释（N-13，fail-open） | OPEN-I09A-4（需 owner 决定是否修 + 谁修） |
| 跨仓消费者（invest-core `adapt_revenue`）如何读 `commit_status` | 本卡 scope 外，须 owner 另开卡（与 I-08-A OPEN-D6 同批） |
| 真实 kill / 掉电 / 重复恢复 | I-09-C |
| provider 与签名载荷落地 | I-08-B（本卡只消费其字段名） |
| `PLAN/reviews` 目录 mtime 与任务的「10:05」不一致（实测 2026-09-19 9:14:20） | 观察项，见 `review.md` §5 |

---

## 10. 本卡未做 / 未验证

- 未实现任何一条协议（设计卡）；`iso/` 内只有**只读探针**与**纯函数**身份计算，产品仓零写入。
- 未实现提交锁、未压测并发（N-12 是单次运行）。
- 未做真实 kill / 掉电 / 重复恢复。
- 未裁决 OPEN-I09A-1…5。
- 未验证跨仓消费者。
- **未授予的资格**：提交协议**不是「已定案」**（待独立 transaction reviewer 裁定）；`I09-E**` 错误码**不是「已生效」**（未实现）；三类资格（★见 `review.md` §2）分别陈述，互不继承。
