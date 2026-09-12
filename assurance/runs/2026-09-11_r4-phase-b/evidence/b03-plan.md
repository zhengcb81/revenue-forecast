# B03 实施计划（稳定只读字节提供）——v0.1（2026-09-12）

> 依据：[b-design.md](../b-design.md) §B03（三级设计：固定句柄 + 读后复验 / 受控快照 / 显式失败）；允许集：[file-scope.md](../file-scope.md) §3b 的 B03 行 = **F4 `reader.py`（只读底座）+ F2 `resolver.py`（切换与失败语义）**，新断言落 **F10 `tests/contract/`（仅新增文件）**。
> 本步承接 **S-10 的另一半**："只返回验证版本字节或明确失败"的**字节级硬门**（B02 已把"同 hash"实现为**优先 + 逐候选诊断**，非首选副本走 `_verify_candidate`，首选副本仍按目录声明服务）。

## 1. 现状清点（实测锚点，2026-09-12，HEAD = `0e28d99`）

| 事实 | 锚点 | 含义 |
|---|---|---|
| 单文件全量流式摘要 | `resolver.py:162-169 _sha256_of_file` | 逐块读全文件；**采样只能否决、不能证明相等**（B-DR3-03） |
| 非首选候选的字节校验 | `resolver.py:244-276 _verify_candidate` | 预算/上限（`_CANDIDATE_BYTES_CAP` 256 MiB、`_REQUEST_MAX_CANDIDATES` 64、`_REQUEST_MAX_BYTES` 2 GiB）→ 全量摘要 → 不等即拒；**只在被选中服务前调用** |
| 云占位拒读 | `resolver.py:172-178 _needs_hydration`（属性 `0x400000/0x40000/0x1000`） | `stat` 阶段就拒，**不触发联网水合** |
| 首选副本的信任级别 | `resolver.py:150-152` 注释 + §3 差异清单 a–d（[evidence/b02-implementation.md](b02-implementation.md) §3） | **按目录声明服务**（= 本步要闭合的口子） |
| 句柄只给路径 | `resolver.py:413 canonical_path` / `:1525 canonical_path=canonical["absolute_path"]` | 消费者拿到**路径**，自己 `open()` ⇒ 校验与真正读取之间存在 **TOCTOU 窗口** |
| 只读底座 | `reader.py:144 ReadOnlyCatalogReader`（`mode=ro` + `query_only`） | 只是**目录**的只读访问；**没有任何"取字节"的入口** |
| 受控快照 | **不存在**（全库 `snapshot` 命中均为 runtime policy / quality / 页级 / DB 行快照，见 §5） | 设计第 2 级"读取**既有**受控快照"**无对象可读** |

## 2. 本步要交付的规则（落 F2，必要时把纯函数落 F4）

新增**字节服务入口**（唯一被认可的取字节方式），语义如下——逐条都对应可写的用例：

| # | 规则 | 失败时的显式结果 |
|---|---|---|
| R1 | 取字节前先 `stat`，命中云占位属性 ⇒ **拒绝**（不读、不联网） | `unavailable` + reason `placeholder_not_hydrated` |
| R2 | 以**只读共享**打开；边流式读入缓冲边算摘要；**对"实际返回的字节"复算**并与请求的 `content_sha256` 比较（首选副本**一视同仁**） | `unavailable` + reason `content_sha256_mismatch`（附短摘要，绝不返回部分字节） |
| R3 | 读取过程中文件被替换/截断/中断 ⇒ 复验不等或 I/O 错 ⇒ 失败（**不得**回退到"打开时校验过"的说法） | `unavailable` + `read_failed` / `truncated_during_read` |
| R4 | 超上限（`_CANDIDATE_BYTES_CAP`）或超预算 ⇒ 失败，**不做**"先返回一部分" | `blocked` + `exceeds_candidate_cap` / `budget_exhausted` |
| R5 | 返回结构带**证据**：`bytes_source="handle"`、`verified_sha256`、`size`、`read_at`（UTC）；**不新增 `SourceHandle` 字段**（payload 形状不变，B02 先例） | — |
| R6 | 取消（`_ReadBudget.cancel()`）在读取过程中生效 ⇒ **绝不**返回句柄或字节 | `unavailable` + `cancelled` |

**明确不做**（设计原文禁止项）：只信 `mtime`/文件名；在 `query`/`open` 内**隐式新建**快照并宣称零写；纯读取建缓存；任何写路径（本步不碰 `store.py`/`canonical_writer.py`）。

## 3. 用例清单（F10，**仅新增文件**，命名 `test_r4b03_*.py`）

| 用例 | 覆盖 | 对应设计 |
|---|---|---|
| 打开后**替换**（同 size 改内容） | R2/R3：读后复验必须发现（"打开时校验"理论在此**必然失败**，B-DR-07） | L05 |
| 同 size、同 mtime 的**内容**改动 | R2：不靠 mtime/size 判定 | 禁止项 |
| 读**中途**截断/追加 | R3 | L05/L06 |
| 云占位属性置位（合成 `st_file_attributes`） | R1：**零读取**、零联网 | L06 |
| ACL 拒绝 / 文件被独占占用 | R3/R4：显式失败而非崩溃 | L06 |
| 超上限文件 | R4 | L06 |
| 取消发生在读取中 | R6 | L06 |
| **首选副本**（rank 1、漂移字节） | R2：闭合 S-10 的口子——B02 会服务它，B03 的字节入口必须拒绝 | L05 + S-10 |
| symlink 逃逸（只读路径不跟随出 root） | 读取面负例 | L05 |
| 正常路径的正例 | R5：字节 + 证据齐全（`bytes_source`/`verified_sha256`/`size`） | L05 |

> 既有用例**一条都不改**（F10 硬约束）；本步新增的用例若在 B02 语义下会失败，属**预期**（那正是 S-10 的偏差），用例内以注释写明原因。

## 4. 棘轮与覆盖率（硬约束，开工前先量）

| 约束 | 值 | 影响 |
|---|---|---|
| `resolver.py` 复杂度上限 | 103（冻结） | 新函数自身复杂度须 ≤103；**不得**把判定塞进既有函数使其超限 |
| `reader.py` | **不在**冻结表 ⇒ 每个模块级函数 ≤ `NEW_FILE_MAX`=10 | 若把纯函数落 F4，必须保持 ≤10 |
| 覆盖率 | TIER2 `resolver.py` ≥ 86；`scanner.py` ≥ 91；TIER1 `service.py` ≥ 95 | 新分支必须有用例覆盖（否则覆盖率掉档） |
| 新增文件 | `tests/contract/` 新文件不受旧上限约束 | 新用例落这里 |

## 5. 已知限制（**如实登记**，不假装实现）

1. **设计第 2 级（受控快照）无对象可读**：全库检索 `snapshot` 的命中都是 runtime policy / quality / 页级 / focus_cleanup 的 DB 行快照，**不存在"源字节的受控快照"**。设计中"读取**既有**受控快照"因此**当前不可实现**；"新建快照"是**被明令禁止**的（写入路径 + 空间，需另批）。→ 本步只登记该级为**未实现 + 触发条件**（句柄不可固定时，行为是 R3/R4 的**显式失败**，而不是"静默降级"）。
2. **云占位/大文件只能在合成属性上测**：本机（Windows）无法真实制造召回型占位文件 ⇒ R1 用合成 `st_file_attributes` 测；真实云行为属 G8 隔离副本/B08，**不声称已验证**。
3. **`B-payload-hash` 仍不可执行**：本步**不新增** `SourceHandle` 字段，也不改变响应 payload 形状；但该门本身仍没有冻结基线。
4. **消费侧接线不在本步**：F 列表不含 `cli.py`/消费仓；"唯一版本化读取合同"是 **B07** 的交付。本步交付的是**可被 B07 接的字节入口**。

## 6. 作者在本步内自行决定的事项（记录理由，不上升 owner）

| 决定 | 理由 |
|---|---|
| 字节入口放在 **F2 `resolver.py`**（与 `_sha256_of_file`/`_verify_candidate`/`_needs_hydration`/预算同处），而非 F4 | 这些机制都在 F2，拆开会产生跨文件私有依赖；F4 的职责是**目录**只读底座，不是文件字节 |
| **不改** `SourceHandle` 字段 | payload 形状变化无法用 `B-payload-hash` 验证（该门不可执行）；B02 已有先例 |
| 首选副本的校验放在**字节入口**而非 `resolve()` | owner 的 S-10 裁定原文："字节硬门归 **B03 读路径**"；在 `resolve()` 里全量读文件会让每次查询都产生整文件 I/O（L12 的"查询零成本"会不成立） |
| 失败值沿用五值模型里的 `unavailable`/`blocked` | 与执行计划 §B03 原文一致（"返回五值中的 `unavailable` 或 `blocked` + reason"） |

## 7. 停止规则（沿用 [risk-and-stop-rules.md](../risk-and-stop-rules.md)）

命中任一即停并记录：需要改 allowed 集之外的文件；需要新建快照/写路径；需要真实云占位或 G8 隔离副本才能继续；覆盖率/棘轮无法在既有文件内保持；发现"只返回验证字节"与 B02/B05 的既有断言冲突。
