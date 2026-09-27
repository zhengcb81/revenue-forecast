# 产品侧修复批次（owner 2026-09-18 指令「修」）：F-BAR-10 / F-BAR-11 / F-BAR-12 / F-BAR-14 + `F-B10R2` 家族前 4 站点

> owner 的指令：**1 修**（F-BAR-10 / F-BAR-11 / F-BAR-12）、**2 不用**（生产四根+第五根共存不验证）、
> **3 不要**（R6 不加固）、**4 修**（`F-B10R2-MISSINGFILE` 一族 + `scripts/` 两处读取者）。
> 本文件记录**已完成**的部分；`F-B10R2` 家族**剩余站点**列在 §6。

## 1. 逐项结果

| 项 | 修法 | 用例 | 变异 |
|---|---|---|---|
| **F-BAR-10**（声明了 adapter 的根在无激活快照时被 v1 遍历） | `scanner._scan_catalog_impl` 改为 **`use_adapter = v2_scan_shadow or root.adapter_id is not None`**：声明即指令，快照只继续管**没声明 adapter** 的根；`ScanReport.strategy` 记录每个根实际走的路径（**分派从此可观察**） | `tests/contract/test_r4bar10_adapter_declared_root.py`（2） | **KILLED** |
| **F-BAR-11**（deny 只约束决定，字节入口仍放行） | `SourceResolver.read_verified_bytes` 在包含性检查之后加**复用根判定**：用**同一个** `policy._effective_reusable`（决定路径与跨仓 policy export 用的同一个函数），拒绝时用**已注册**的 `policy_denied`（"root policy does not authorize reuse"，`observability.py:51`）⇒ 不新增词表项、不 bump 版本；新增 `_owning_root()`（按包含性最长匹配定位根） | `tests/contract/test_r4bar11_deny_binds_the_byte_entry.py`（4） | **KILLED** |
| **F-BAR-12**（`bundle_status=available` 但 `valid_handles` 空） | 契约说 `available` 只表示"提供了真实 bundle"，而消费者会读成"可用"。**加性**新增 `bundle_valid_handle_count` / `bundle_invalid_roles` / `bundle_usable`（由 bundle 内容**派生**）；`envelope_schema_version` 仍 **1.0** ⇒ N-1 消费者不受影响 | `tests/contract/test_r4bar12_bundle_usability.py`（4） | **KILLED** |
| **F-BAR-14**（本批自己发现的**新缺陷**） | 适配器 `_normalized_from_sidecar` 原来**只映射固定子集**，而旧 v1 路径把**侧车整块**写进 `acquisition` ⇒ 适配器路径**丢字段**：`form_type`（resolver 的 form 门 ⇒ `form_type_mismatch`）、`company_name`（实体锚定）、`source_title`（标题派生 + B05 冲突检测 ⇒ B06 的 `blocked` 变 `verified_input`）、旧拼写 `filing_date`（⇒ `published_date_unknown`）、`fiscal_year` 被 `str()`（**SQL `json_extract(...) = <int>` 比类型 ⇒ 过滤查不到**）。改为**声明键透传 + 规范化键覆盖** | `tests/contract/test_r4bar14_adapter_metadata_contract.py`（2）+ 既有 7 个契约用例（B01×2、B02×1、B05×1、B06×1 等） | **KILLED**（两路：透传、标题冲突） |
| **`scripts/` 两处读取者** | `legacy_observer.py:96`、`wu904_remediation_restore.py:65` 收敛到 `store.metadata_object`（单一链、永不抛）；**棘轮从"钉住 2 个"升级为 `scripts/` 硬零**（`test_b10_scripts_have_no_direct_reader`），并把 `GATE_BOUNDARIES.readers_outside_the_scanned_roots` 的登记改写为"该项已收口，剩 `tests/` 为报告项" | 该门用例 + `barfix_scripts_readers_probe.py`（3 个变异：两处注入被门杀、不同列的 `loads` **不**误报） | **KILLED**（含控制组） |
| **`F-B10R2` 家族 站点 1–4** | ① `activation.rollback_activation`：`assertion_ids_json` 不可读 ⇒ **具名 `ActivationError`**（读成 `[]` 会"报成功却什么都没恢复"）；② `assertion_service.verify_assertion`：`evidence_json` 不可读 ⇒ **具名 `ValueError`**（不得把没读懂的证据当"已核验"复制下去）；③ `remediation.approve_proposal`：`proposal_json` 不可读/无 `policy_hash` ⇒ **具名 `RemediationError`**；④ `scanner._observe_file`：size+mtime 捷径上的 `manifest_json` 不可读 ⇒ **降级为"不是复用候选"、穿透到重新哈希**（批次不停、坏行**自愈**） | `tests/contract/test_fb10r2_unguarded_column_parses.py`（4） | 4/4 **KILLED** |

## 2. 变异矩阵：**8/8 KILLED**（`barfix-mutations.json`，每个变异跑在临时副本里）

| 变异 | 结果 |
|---|---|
| `F-BAR-10` 回退到 `use_adapter = v2_scan_shadow` | KILLED（适配器用例红、控制用例仍绿） |
| `F-BAR-11` 关掉策略门（`if False`） | KILLED |
| `F-BAR-12` `bundle_usable = True`（不再派生） | KILLED |
| `F-BAR-14` 取消透传（`normalized = {}`） | KILLED（两条路各自被杀） |
| `FB10R2-scanner` 回退成 `json.loads(...)`（**忠实回退**） | KILLED |
| `FB10R2-activation` 取消 `except`（**忠实回退**） | KILLED |
| `FB10R2-remediation` 回退成裸 `metadata_object` | KILLED |
| `FB10R2-assertion` 回退成裸 `json.loads` | KILLED |

**两处我自己的变异写作错误（已修，登记）**：`FB10R2-scanner` 与 `FB10R2-activation` 的第一版是**等价变异**
（`metadata_object` 同样永不抛；activation 那处只禁用了"不是 list"的检查而非解析守卫），因此**存活**——
存活原因正确（变异等价），但也说明"存活"不能直接读成"测试有洞"。**教训**：变异必须**忠实回退被修的那一行**，
而不是替换成一个语义相近的写法。

`barfix_scripts_readers_probe.py` 另证（`barfix-scripts-readers.json`）：
旧表达式在**深嵌套**与**非字符串**输入上**逃逸**（`RecursionError` / `TypeError`），新链永不逃逸并给出
`state`；注入后两脚本文件按**行尾不敏感指纹**逐字节还原。

## 3. 对既有用例的两处**期望更新**（不是放宽）

1. `test_r4b02_rejected_copy_stays_reclaimable_next_to_healthy_copies`：`total_groups 2 → 1`、
   `total_reclaimable_copies 3 → 2`。**原因可测**：旧的"第二组"是**侧车自己被当文档**形成的一组
   （三条相同的 `.pdf.source.json`），正是 F-BAR-10 修掉的那个假象；同一夹具在"声不声明 adapter"两种配置下
   实测：groups 2→1、reclaimable 3→2、documents `['2025','2025.pdf.source']` → `['2025']`。
   用例的**意图**（被拒绝的副本仍在规划器给出的清单里）**原样保留**，并**新增**一条"侧车不得再是文档"的断言。
2. 无其它期望变更。F-BAR-10 的直接后果是**更多根走适配器路径**，因此 F-BAR-14 的字段合约必须先补齐——
   顺序不能反，否则"修好分派、弄坏复用"。

## 4. 本地与远端 CI

见 [progress.md](../progress.md) 同日条目（本地 unit/contract 两步 + 远端 `quality` 的 run id）。

## 5. 这一批的边界

- **没有**动生产 catalog；**没有**动任何真实根；所有变异都在 `%TEMP%` 副本里跑，仓库按指纹核对未变。
- **没有**改 `envelope_schema_version`、**没有**新增 reason 词表项、**没有** bump taxonomy 版本。
- **没有**改 `future_lake`/`dropbox_stock` 的**声明**（只改"声明了 adapter 的根怎么被扫"）。

## 6. `F-B10R2` 家族 normalize 侧站点（**2026-09-19 全部收口**）

owner 2026-09-18 的第四条指令（「4，修」）覆盖 `F-B10R2-MISSINGFILE` 家族与 `scripts/` 两处读取者；
下表是**该指令下已交付**的处置（原文的"剩余/未做"状态由本表取代）：

| 站点 | 现状（2026-09-19） |
|---|---|
| `normalizer.normalize_catalog` 的 **unsupported handler 里的 `IngestService.ingest`** | **已修**：改走 `_ingest_without_raising`（永不抛），不可读/不匹配的 manifest 变成**具名**逐文档失败 `ingest_failed:<Exc>`（r3/r4 实测的 S1/S4/S7/S8/S12 形状现在都落在这一条上） |
| 成功路径的 `IngestService.ingest`、其后的 transaction 块 | **已修**：`ingest_failed:<Exc>` 与 `artifact_record_failed:<Exc>`，均 `continue` |
| **第一处 `fetchall`**（循环内取该文档的 locations） | **已修**：`locations_read_failed:<Exc>`（**可重试**，耗尽预算后 `retry_exhausted:<code>`） |
| **第二处 `fetchall`**（`backfill_text_fingerprints` 里取 locations） | **已修**（2026-09-19，本文件 §7）：同形守卫 + 退避 + `retry_exhausted:` 终态；变异 `FB10R2N-backfill-read` KILLED |
| `_atomic_write` 的 `mkdir` / 写盘 | **已修**：`artifact_write_failed:<Exc>` + 记录 `artifact_byte_size` |
| 包内 4 处未守卫的同名列解析 | **已修**：`activation.py`（`ActivationError`）、`assertion_service.py`（`ValueError`）、`remediation.py`（`RemediationError`）、`scanner.py`（size+mtime 捷径**降级为重新哈希**，批次不停、坏行自愈） |
| `scripts/legacy_observer.py` / `scripts/wu904_remediation_restore.py` | **已修**：收敛到 `store.metadata_object`；棘轮升级为**硬零** |

## 7. 第二处 `fetchall` 的补修（2026-09-19）

- **为什么还有一处**：2026-09-18 那批把 normalize 侧的四处守卫做完后，`backfill_text_fingerprints`
  里的 `locations` 读取**仍是裸的**——一条失败的语句（库被锁、索引损坏）会**逃出整个回填批次**，
  饿死它后面的每一份文档。owner 指令原文点名的是"**两处** `fetchall`"，这就是第二处。
- **处置**：与第一处**同形**——`except sqlite3.Error` ⇒ `locations_read_failed:<Exc>`；**读失败与文档无关**，
  所以先记 **`retryable_failed` + 退避**，`attempt_count` 达到 `retry_limit` 才落 `failed_terminal`
  （`retry_exhausted:<code>`），随后 `failed += 1; continue`。
  **登记的限制**：`record_fingerprint_outcome` 调用本身**不**加守卫——连结果行都写不进去的库是硬停，
  吞掉它只会**静默丢掉记录**；另两条批级读取（`select_fingerprint_batch`、`fingerprint_status`）在循环
  **之外**，失败**无法归因到某一份文档**，因此仍是整批失败（未改）。
- **用例**（`tests/contract/test_fbar_b10r2_normalize_guards.py`，2 条）：`retry_limit=1` ⇒ 终态 + 具名原因
  + 其后两份健康文档 `completed`；`retry_limit=3` ⇒ `retryable_failed` / `attempt_count=1` /
  `last_error_code=locations_read_failed:OperationalError` / `next_retry_at=2027-01-15T08:15:00Z`。
  第二条是**必要的**：没有它，一个无条件写终态的守卫也能骗过第一条。
- **变异 `FB10R2N-backfill-read`**（忠实回退：`except sqlite3.Error` → `except ()`）：
  **副本内基线 7 passed ⇒ 回退后 `2 failed, 5 passed`**（红的那两条正是新增的两条回填用例），
  即先红后绿；数字取自 `barfix-mutations.json` 的 `baseline` / `mutated`。
  （**更正 F-IR-10**：本节旧版写的是 `2 failed, 4 passed` / `6 passed`——那是**第三条用例尚未加入**时的
  旧计数，与同节下面的"7 passed"自相矛盾。）
  全矩阵 **17/17 KILLED**（`src_fingerprint_identical` 与 `git_status_identical` 均为真）。
- **顺带把第四个守卫也变成"被驱动"**：`normalize_catalog` 的**记录事务**（`artifact_record_failed`）
  此前只有"与其它守卫同形"这句话撑着——那是**阅读**不是**证明**。现在有独立故障注入
  （`test_a_failing_record_transaction_is_a_per_document_failure`）：harness 播种完成后才**武装**开关，
  而 `normalize_catalog` 每份文档**只开一次** `store.transaction()`（span 删除 / span 插入 / artifact
  upsert / fingerprint 更新共用），所以"第一次调用抛错"是**无歧义**的——第一次抛，第二次仍必须提交。
  变异 `FB10R2N-record` 副本内先红（`1 failed, 6 passed`，红的那条正是新用例）⇒ 修后绿（7 passed）。
  **更正**：本文件旧版与用例 docstring 曾写"记录事务由探针覆盖"——`barfix_normalize_probe.py` 驱动的是
  **通用 handler 的 `_ingest_without_raising`**（另一处站点），**不能**拿来当这处的证据。
- **同时修掉的两处 harness 缺陷**（都是我自己的账目问题，已入 `barfix_mutations.py` 的自检）：
  ① `FB10R2N-read` 在矩阵里被**声明了两次**（重复字典键会**静默**丢掉前一份定义，"16 条"看着仍对）；
  ② 变异锚点若在目标文件里出现多次，`replace(..., 1)` 会改到**第一处**——一个陈旧变异照样报 KILLED。
  现在 `_self_check()` 在跑之前先拒绝这两种矩阵，并**加了第三条**：替换文本若**已存在**，该变异
  **什么都没改**（本 run 已登记过两次"没有变异的变异"）。三条检查覆盖了 17 条变异；
  我为此写的一次性审计脚本已删除（其检查已并入自检，避免录里留两份会漂移的副本），
  `barfix-mutations.json` 由**加了自检之后**的同一份 harness 重跑生成。

