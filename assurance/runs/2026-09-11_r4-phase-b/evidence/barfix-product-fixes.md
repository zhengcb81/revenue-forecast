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

## 6. `F-B10R2` 家族**剩余**站点（未做，需继续）

| 站点 | 现状 |
|---|---|
| `normalizer.normalize_catalog` 的 **unsupported handler 里的 `IngestService.ingest`** | 主文件缺失 ⇒ `SourceManifestMismatchError` 逃出、**饿死队列里后面的文档**（r3/r4 已实测 S1/S4/S7/S8/S12）。修法需与"逐文档失败"语义对齐（**行为改动**，要有行为级探针 + 变异 + 复审） |
| 成功路径的 `IngestService.ingest`、其后的 transaction 块、**两处 `fetchall`** | 同为"单文档问题可能中止整轮"，需同类处置 |
| `_atomic_write` 的 `mkdir` | r4 已用人造 FS 阻塞驱动过（S10），但**修法未落地** |
