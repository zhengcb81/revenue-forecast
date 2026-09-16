# B10 实施计划：**小范围切到单一读取链**，旧入口仅作**显式版本 adapter**

> **状态：计划已就绪，前序门已通过 ⇒ 可开工（实施本身仍需独立复审 + 变异证明 + 本地两个 CI 步骤 + 远端 CI 全绿）。**
> 前序门 = **B.AR 复审**——`B.VR-bar` 判 `adjudication = APPROVE_WITH_FINDINGS` + **`authorization_adjudication = OVERREACH`**（[b-ar-record.md](../b-ar-record.md) §0.1：额外命令、`--limit 100` 超限、102 次调用对 25 次预算、违反非零即停）。
> owner 随后**把裁定权授予我**（`授权你批准，不用问我`）⇒ 我的裁定：**只读批量授权追认；越界证据保留、违规在案、不重做**，并把边界改成**机械强制 + 自测**（见 [owner-authorisation-and-my-adjudication-2026-09-16.md](../owner-authorisation-and-my-adjudication-2026-09-16.md)）。B.AR 记为**通过（范围受限）**，其中未做的残余（第五 root 注册 / 跨仓端到端）**不在**本次授权的写边界内。
> 权威要求（[R4 执行计划 §B](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)，与 [task_plan.md](../task_plan.md) B10 行一致）：
> "小范围切到单一读取链，旧入口仅显式版本 adapter；记录可回退版本与旧字段移除条件"；
> 验收："**变更独立审查后才切换**；回退代码/配置**不回滚**原始数据和历史来源证据；**无法兼容则停切换**，不永久默默双跑"。

## 1. 只读侦察（本次实测，全部为 file:line 证据）

> **机器导出的完整基线见 [b10-recon.md](b10-recon.md)** 与 [evidence/b10-read-chain-inventory.json](../evidence/b10-read-chain-inventory.json)
> （AST 扫描：21 个解析点 = 2 个单一链调用 + **10 个确认的直接读取者** + 9 个启发式候选；含一处**假阳性**的教训）。
> 下面这节是最初的手工侦察，保留以对照。

**读取链 A —— 现行单一链（字节级）**
- `SourceResolver.resolve(request)` → `SourceHandle`（`resolver.py:1282`）
- `SourceResolver.read_verified_bytes(handle, expected_content_sha256=…)` → 一次读取、对**同一缓冲**取摘要，返回字节或**显式失败**（`resolver.py:1936`；契约见 `ByteReadResult`，`resolver.py:343`：`data`/`status`/`reason`/`byte_size`/`bytes_source`）

**读取链 B —— 旧入口（声明级，claim-level）**
- `ReadOnlyCatalogReader.resolve_handle(document_id, expected_content_sha256=…)`（`reader.py:333`）：只读 document 行 + `source_sha`，比较"**目录声称的**"摘要；**从不打开文件、从不计算摘要**
- `ReadOnlyCatalogReader.bundle(…)`（`reader.py:353`）：同上一句话的判定 + `build_source_bundle`
- **src 内调用者：0**（`resolve_handle(` 仅出现在 `reader.py:108` 协议与 `:333` 实现；`.bundle(` 在 src 内无匹配）；`tests/` 中 8 处引用

**第二处重复（同一合同的第二份实现）**
- `service._read_shared_metadata(raw)`（`service.py:81`，catch `TypeError/ValueError/RecursionError`）
- `store.metadata_object(raw)`（`store.py:934`，catch `JSONDecodeError/TypeError/RecursionError/UnicodeDecodeError`）
- 两者语义**等价**（`JSONDecodeError ⊂ ValueError`、`UnicodeDecodeError ⊂ ValueError`；非 dict → `{}`）⇒ 真正的第二份实现
- 仍在**自行解析**共享列 `documents.metadata_json` 的模块（B05 登记的残留）：`artifact_backfill.py:175`、`artifact_read_model.py:105`、`extraction_quality.py:195`、`normalizer.py:1441/1633/1684`、`prompt_injection.py:108/151`、`prompt_injection_guard.py:118`、`resolver.py:816`、`scanner.py:1330/1405/1697`、`section_query.py:109`、`service.py:432`、`source_lifecycle.py:151`

## 2. "无法兼容则停切换"的**逐入口判定**（先判定，再动手）

| 入口 | 语义 | 与链 A 兼容？ | 判定 |
|---|---|---|---|
| `resolve_handle` | **声明级**：信目录声称的摘要 | **不兼容**：链 A 是**字节级**（真读文件、对缓冲取摘要）。把它悄悄改成链 A 会**改变失败语义**（原本"声称相符"即返回） | **停切换**：保留为**显式 v1 adapter**，在注册表里写死"**claim-level、从不核验字节**"，并写**移除条件**（见 §4） |
| `bundle` | 同上（+ 组装 SourceBundle） | 同上 | 同上 |
| `service._read_shared_metadata` | 与 `store.metadata_object` **完全等价** | **兼容** | **切换**：改为委托 `store.metadata_object`；本名保留为**显式 adapter 别名**（一行 + 版本注释） |
| 其余 10 处自解析点 | 各自 catch 组合不同、失败语义不一 | **逐点判定**：先加用例固定**当前**行为，再切换；行为一旦变化即**停下并报 owner**（不做"顺手改语义"） | **分批切换**，每批一次提交 + 独立复审 |

> 这一节是 B10 的核心：**"不永久默默双跑"**意味着每一条要么收敛、要么**具名**为 adapter（有名、有版本、有移除条件），不允许"两份都在跑且没人知道"。

## 3. 实施步骤（每步一提交、可独立回退）

| 步 | 动作 | 验收 |
|---|---|---|
| B10-1 | 新增**读取链注册表**（机器可读）：链 A 为唯一字节级链；列出每个旧入口的 `version`/`semantics`/`removal_condition`/`callers` | 注册表与 `grep` 实测一致；新增一个未登记的 claim-level 入口 ⇒ 门**红** |
| B10-2 | `service._read_shared_metadata` → 委托 `store.metadata_object`（本名保留为 adapter 别名） | 行为等价用例全绿；变异：把委托改回第二份实现 ⇒ **收敛门红** |
| B10-3 | 分批把 §1 的 10 处自解析点切到 `metadata_object`（先固定当前行为，再切） | 每批：定点用例 + 契约套件；**任何行为变化即停** |
| B10-4 | `resolve_handle`/`bundle` 就地标注为**显式 v1 adapter**（docstring + 注册表条目 + 类型层面的"claim-level"命名） | 门要求：凡返回"可用句柄"的入口必须在注册表内声明**是否字节级**；未声明 ⇒ 红 |
| B10-5 | 记录**可回退版本**与**移除条件**（§4） | 文档 + 注册表一致；独立复审确认 |
| B10-6 | 独立复审（`B.VR-b10`）→ 处置 → 本地两个 CI 步骤 + 远端 CI 全绿 → 记录入库 | 与 B05 同规格 |

**复杂度棘轮**：本轮所有改动都发生在**既有文件**内且以"抽走分支/委托"为主 ⇒ 棘轮只应**下降**；若某文件超基线，按 **S-7** 抽新函数而**不动**棘轮表（基线只能降）。

## 4. 可回退版本与移除条件（切换前先写死）

- **可回退版本**：切换前的 wiki 提交（实施时写入注册表与 `progress.md`），回退方式 = `git revert` 该批提交。**回退不回滚任何原始数据/历史来源证据**（本工作包**不写**任何 catalog 数据）。
- **旧字段/旧入口移除条件**（全部满足才可移除）：
  1. 该入口在 `src/` 与 `adapters/` 内**调用者为 0** 且连续**两个** R4 验收周期无新增调用者；
  2. 其语义已被链 A 的**显式等价**能力覆盖（声明级调用者改用"链 A + 明确降级说明"）；
  3. 注册表里该条目被 owner 或验证者标记 `removable`，且有独立复审记录；
  4. 删除后**契约套件与真实数据套件**全绿。

## 5. 风险与停规则

| 风险 | 处置 |
|---|---|
| 把 claim-level 入口静默改成字节级 ⇒ 旧调用者语义变化 | **不做**（§2 已判"不兼容"）；保持具名 adapter |
| 10 处自解析点里有的**故意**允许抛错（fail-closed 到调用方） | 先加用例固定当前行为；变化即停并上呈 owner |
| 共享列是**多方命名空间**（B05 已知），切换读取器可能改变 `metadata_problem` 判定 | 切换后必须重跑 B05 的 15 个变异 + 两个契约文件 |
| 触到生产数据的诱惑 | **停**（G8/G7 边界；本工作包不写数据） |

## 6. 与其它工作包的边界

- **不**改消费者仓（revenue/filing）任何行为（B07 已把"边界 adapter"归为 wiki 侧版本化合同）。
- **不**改 `schema_version`/taxonomy 版本等**冻结常量**（B07/FC-1301 的教训：先查谁把它钉住）。
- **不**新增 CLI 入口、**不**新增写路径。
