# B 阶段设计（b-design v0.1.7）—— 位置透明索引与只读读取

> **v0.1.7（2026-09-12）**：**B02 实施回填**（owner §8 授权后第一步）—— 新增 [§B02 实施偏差](#b02--同版本候选-location-的选择v011新增-_handle-锚点与资格判定不得联网约束) 说明（段 3 的 hash 相等在 B02 中实现为"优先 + 逐候选诊断"，**字节硬门归 B03 读路径**；依据、复跑命令与新哈希见 [evidence/b02-implementation.md](evidence/b02-implementation.md)）；设计正文其余部分**未改**，B03–B07 仍为 DESIGN_ONLY。
> **v0.1.6（2026-09-12）**：第五轮 `B.DR-rev5` = rejected（2×P1 / 4×P2 / 5×P3，均为文本与落点级）→ 本版按「新值在场 **且旧值不再作为断言**」的标准逐条落地：N-1 从 B07 完成定义彻底移除、`metadata_json` 整列替换被禁（含 `:1073-1077`/`:1095-1099` 锚点）、`legacy_observer.py:90` 与 `schema_version` 补入、覆盖率棘轮与 `NEW_FILE_MAX` 登记、`B-payload-hash` 标注为**当前不可执行（无基线、需待批 CLI）**、VR-N21 从 B 移除、计数与状态行全部对齐。
> **v0.1.4（2026-09-12）**：owner 六项边界已定（[owner-scope-decisions-2026-09-12.md](owner-scope-decisions-2026-09-12.md)）——S-1 允许新增测试（F10/F11 已批）、S-2 把 R-1/R-4 留在 B 之外、S-3 冻结在产导出、S-4 消费者侧归 C、S-5 隔离副本两级、S-6 需要第四轮复审。
> **v0.1.3（2026-09-12）**：按 `B.DR-rev3` 的 11 条更正——**把 owner R-1/R-4 的整改移出 B 的处置与验收**（载体在禁区，见 §B01.3）、B05 补**逐列合并规则**（冲突不得按 priority 择一）、B02 预算改为**能证明整文件 hash 的判据**且不引入五值之外的状态、B06/B07 的可签切分与 file-scope 步骤行补齐、护栏改为真断言。

> 状态：**DESIGN_ONLY**。本文件只描述"要做什么、改哪些文件、怎么验"，**未修改任何产品代码**。
> 依据：R4 执行计划 §B（B01–B10）；阶段 A 冻结合同 **v0.4.1**（[root-contract](../2026-09-11_r4-phase-a/root-contract.md)、[operation-contract](../2026-09-11_r4-phase-a/operation-contract.md)、[identity-contract](../2026-09-11_r4-phase-a/identity-contract.md)）；owner 六项裁定 + 其**范围更正**（[owner-rulings](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md)）。
> 精确定位与哈希见 [file-scope.md](file-scope.md)；测试映射见 [test-acceptance-map.md](test-acceptance-map.md)；风险与停止规则见 [risk-and-stop-rules.md](risk-and-stop-rules.md)。
> **v0.1.1 说明**：本版按 `B.DR` 的 20 条发现重写（P0×1 + P1×7 + P2×9 + P3×3），其中 P0 与 A07/A08 命中同一事实。**逐条回应见 [findings.md](findings.md) F-B01-1**。

## 总原则（来自阶段 A 合同，B 不得违反）

| 编号 | 原则 | 来源 |
|---|---|---|
| P-1 | 能力四轴（可读/可写/可外发/可复用）**互不推导** | A02 R1 |
| P-2 | 未注册 root / 显式 deny 不因"默认等价"放行 | A02 R2 |
| P-3 | **假保证字段不得留在"已强制"清单**（`symlink_policy` **与 `read_only`**）——**处置本身不属于 B 范围**（owner R-1 的整改在禁区文件内），B 只按其读取语义行事 | A02 R7 + v0.4.2 |
| P-4 | 准入语义**只能有一套**（= 生效的 `config.py`）；**导出路径 `export_policy_2x` 在产，其字节/hash 契约不可破坏** | A02 R8 + v0.4.1 范围更正 |
| P-5 | 纯查询接口不得触网/不得 `ensure`/不得改 worker 状态/不得写 catalog；**R 轴 = 无逻辑写 + 无网络 + 无子进程**，进程级副作用单列 | A03 §2.1 |
| P-6 | 路径诊断信息**不得进入业务身份**（残留锚点数以 A 侧 [identity-contract](../2026-09-11_r4-phase-a/identity-contract.md) §1 的清单为准——A 记 **9 处**，B 的 file-scope §3 另列 **11 个排序锚点**，差异已注明） | A04 R4（owner R-6） |
| P-7 | 显式 `reusable_for_filing: false` **必须生效**（对齐语义）；**不得新增第二套 effective_reusable**（执行计划 §B01 原文；现存第三处在冻结的导出路径内，不可删） | owner R-2 + 执行计划 §B01 |
| P-8 | `privacy_class` 缺省**不再默认可外发**（owner R-4）——**该整改不属于 B 范围**（承载文件在禁区，见 §B01.3）；B 只**引用**该裁定，不实施、不验收 | owner R-4 + v0.4.2 惰性限定 |
| P-9 | 接口错误**恰好五值**：`not_found` / `not_indexed` / `unavailable` / `blocked` / `ambiguous`（+ reason）；重试性/预算/超时是独立字段 | A03 §2.4 |

---

## B01 —— 字段唯一 owner 与**旧字段版本映射**（v0.1.1 补齐 B-DR-02 要求的交付物）

### B01.1 字段唯一 owner

| 语义 | 唯一 owner（设计） | 现状（已核实） | 本步决定 |
|---|---|---|---|
| 物理位置（path、adapter、symlink 政策、大小/编码限制） | **storage 层**（`config.py` → `models.RootSpec`） | `config.py:70-118`（活、唯一准入）；`policy_2x.py`/`policy_3x.py` 的 **loader** 无生产调用者 | 按 owner R-3（**范围 = 仅准入 loader**）：收敛为一套；**不动 `export_policy_2x`** |
| 业务身份（document_id、version/source_hash、locator） | **catalog 层**（`models.py` + `service.py` 投影） | `service.py:621-663` 规范位选择含路径/优先级（残留） | 按 owner R-6：**登记整改**；B 不改身份语义，先把 locator 显式化（B04） |
| 可复用资格 | **policy 层单一函数** | **三处活实现**（v0.1.2 更正，B-DR2-01）：① `resolver.py:782-786`/`:933-940`（kind-only，fail-open，不读字段）；② `policy.py:67-72 _effective_reusable`（读字段，fail-closed）；③ **`policy_2x.py:308-312 _effective_reusable_2x`**（读字段，经 `:292` 被 `export_policy_2x` 调用，再由 `cli.py:849-851` 在产） | 按 owner R-2：**对齐①的语义到②③**（`false` 生效），**不是**"删除多余实现"——③位于被冻结的跨仓导出路径（P-4），删不得。任何使②③输出变化的改动**必须与 filing-fetch 的 policy_hash 迁移同步** |
| 外发策略 | **动作边界**（调用外部服务那一刻）——**不属于 B**（S-2） | `llm_summarizer.py:333-337`（白名单）；另有 `legacy_research_ingest.py:128-136` 无门出口 | **B 不实施、不验收**（S-2）；仅**引用**记录，供 owner 的独立整改工作包使用 |
| 文档证据质量 | **不由 root 字段承载**（与能力正交） | A02 C5 | B 不引入"质量即能力" |

### B01.2 旧字段版本映射（**16 个字段名 / 12 行合并项**——v0.1.2 更正计数与遗漏，B-DR2-10；`admission_profile_id` 于 v0.1.2 补入）

| 字段（现状） | 语义 owner | 目标处置 | 迁移/兼容条件（**先做 L11 的当前协议与未知版本拒绝判定**；N-1 未定义，不得作为前置） |
|---|---|---|---|
| `read_only` | storage | **B 不改其处置**（S-2：R-1 属独立工作包）；B 只按**实际语义**行事 | 真实可写判据 = `kind == 'company_raw'`（`canonical_writer.py:126-131/284-287`）；B 的读取路径**不得**依赖 `read_only` 的默认值 |
| `reusable_for_filing` | policy（单一函数） | **保留并使 `false` 生效**（对齐三处实现，见 §B01.1） | ②③ 的输出变化 ⇒ **policy_hash 变化** ⇒ 必须与 filing-fetch 的 FC-501 期望值同步迁移（跨仓）；`None` 保持"跟随 kind" |
| `symlink_policy` | storage | **B 不改**（S-2：R-1 属独立工作包） | B 的 L05 负例只验证**读取路径**的 symlink/reparse 行为，不验证（也不修改）该字段的处置 |
| `priority` | storage | **保留，但只作排序**（B02 第 4 段），**退出 metadata 真伪判定**（B05） | 无 schema 变更；语义变更须有 L01/L08 负例 |
| `privacy_class` | 动作边界 | **B 不改**（S-2：owner R-4 属独立工作包） | **v0.1.5 更正（B-DR4-02）**：v0.1.2/v0.1.3 曾在此写"缺省改为不外发"与"两处默认值必须同改"——**那是 R-4 的实施指令，不属于 B**。B 只记录事实：现网四个 root **全部显式声明 `privacy_class: public`**（`:19/:24/:29/:40`），故 R-4 在现网**惰性**（受影响集合 = 0）；**B 不实施该变更，也不产出"合成配置"断言** |
| `cohort` | catalog | 保留 | 现不在活 loader 的允许字段集（`config.py:75-81`）→ **声明即被拒**；如需启用属新特性 |
| `canonical_write_target` | storage | **暂不引入**（当前声明即被 `config.py:75-84` 拒绝） | 若要引入，须在 `config.py` 正式实现并配写目标负例；**不得恢复 `policy_2x` 的 loader** |
| `adapter_id` / `adapter_version_range` | storage | 保留 | `config.py:96-105` 强制"必须已注册" → 保持 |
| **`admission_profile_id`**（v0.1.2 补） | storage | 保留 | 与 `adapter_id` 同属"必须已注册"面；须在 B01 的机器可读产物里给出其注册表位置 |
| `allowed_document_kinds` / `allowed_statuses` | storage | 保留 | 属准入白名单 |
| `sidecar_suffixes` / `max_file_size` / `encoding` | storage | 保留 | 无变更 |
| `routes` | storage | 保留 | 无变更 |
| `kind` | storage | 保留（唯一能力判据之一） | `models.py:39 ROOT_KINDS` + `:141-142` 准入 |

> **计数口径（v0.1.2）**：上表共 **12 行合并项**，展开后含 **16 个字段名**（`read_only`、`reusable_for_filing`、`symlink_policy`、`priority`、`privacy_class`、`cohort`、`canonical_write_target`、`adapter_id`、`adapter_version_range`、`admission_profile_id`、`allowed_document_kinds`、`allowed_statuses`、`sidecar_suffixes`、`max_file_size`、`encoding`、`routes`）+ `kind` 本身。v0.1.1 写"14 字段"且漏 `admission_profile_id`。

**产出**：`field-owner-map.json`（机器可读版，供 A06/A08 与 B.VR 引用）。

**DR 检查点（B.DR 第一项）**：① 字段映射完整（12 行 / 16 名 + `kind`）；② **`false` 语义在①resolver 上生效**，②③的输出变化与 policy_hash 迁移绑定；**不得新增第二套 effective_reusable**（执行计划 §B01 原文）；③ 显式 `false` 含义保留。

### B01.3 owner R-1/R-4 的整改**不在 B 的处置与验收范围内**（v0.1.3 更正，B-DR3-01）

`B.DR-rev3` 指出：v0.1.2 把 owner **R-4**（外发门整改，含 `legacy_research_ingest.py:128-136`）与 **R-1**（`symlink_policy`/`read_only` 假保证处置）写进了 B01 的"处置"与验收映射，但**这些改动的承载文件全在 [file-scope.md](file-scope.md) §2 的禁区**（`llm_summarizer.py`、`legacy_research_ingest.py`、以及删除 YAML 字段所需的 `config/source_catalog.yaml` 变更）→ 该设计要素**在提案范围内不可实现**（属"写了却做不了"）。据此：

| 项 | B 的角色（v0.1.3） |
|---|---|
| **R-4**（隐私缺省 + 无门出口） | **注册在 A 侧与 owner 裁定里，不属于 B**；B 的设计**不依赖**它（B06 的 `qualification` 只描述资格事实，不实现外发门）；**B 的验收不含 R-4** |
| **R-1**（`symlink_policy` / `read_only` 假保证） | 同上：**B 不改这两个字段的处置**；B 只按其**实际语义**行事（写轴判据 = `kind == 'company_raw'`；symlink 行为由 B03 的读取路径与 L05 负例覆盖） |
| **把它们纳入 B 的条件** | 若 owner 希望 B 一并做，须**扩大 allowed_files**（把相关文件移出禁区）并**重签**工作包——属**新的 scope 决定**，本设计不自行改判 |

> 理由不是"减少工作量"，而是 `B.DR-rev3` 的判据：**设计要素必须映射到范围内的可写文件**，否则不可实施。

---

## B02 —— 同版本候选 location 的选择（v0.1.1：新增 `_handle` 锚点与"资格判定不得联网"约束）

**目标**：把"选哪一份文件"从"先取 canonical 再筛"改为**先构造全部合格候选，再在合格集合内排序**。

现状问题（已核实）：`resolver.py:912-921` 先在 `is_canonical` 上过滤；`is_canonical` 由 `service.py:643-653` 的 `(root_priority, root_id, relative_path, location_id)` 排序取 `ordered[0]` 决定；**且 `resolver.py:1142 _handle` 内还有第二次同样的过滤**（`:1153-1165`）并以 `Path(canonical["absolute_path"]).is_file()`（`:1166`）决定 handle 有无 —— 即"撤掉首选后能否自动切换"由**这两处**共同决定（v0.1.1 补，B-DR-04）。

**设计**：四段式（顺序即语义）

| 段 | 内容 | 硬约束 |
|---|---|---|
| 1. 注册/能力 | location 所属 root 已注册且具备所需能力（读/复用） | 未注册 → `not_found`（A02 R2） |
| 2. 状态与安全 | `location_status == 'active'`；**provider 拒绝路径（`.rejections`）继续排除在合格集之外**（保持现行语义，**不是**"只标记"——v0.1.1 更正，B-DR-06）；被安全策略拒绝的 source **不因换 root 而放行** | 见 [risk-and-stop-rules.md](risk-and-stop-rules.md) O03 交叉 |
| 3. 可读且同 hash | 候选的**已在本地**字节能读到与目标 `content_sha256` 相同的摘要 | **资格判定不得联网**（v0.1.1 新增，B-DR-08）：需要云占位 hydration 的候选一律判 `unavailable`，**不得**在查询期触发下载 |
| 4. 健康/IO 偏好 | **仅在此已合格集合内**按 `priority` → `root_id` → `relative_path` → `location_id` 排序 | 排序**只决定"先用哪个"**，不决定"谁合格" |

**输出**：`canonical`（排序第一）+ **完整候选清单**（含每个候选的排除原因与所落五值状态）。

**实现点**（两处，必须同改）：`service.py:621-663 _annotate_locations`（资格与排序分离）与 `resolver.py:1142-1224 _handle`。
**`_handle` 的具体要求（v0.1.2 更正，B-DR2-06）**：现行 `:1166` 是 `if canonical is None or not Path(canonical["absolute_path"]).is_file(): return None` —— **整体放弃**，因此"首选不可用→改用下一份合格候选"**今天并不存在**，v0.1.1 写"保留该行为"是错的。B02 要求：
1. `_handle` 新增**合格候选清单**入参（由 `service._annotate_locations` 产出），按第 4 段的排序逐份尝试；
2. 只有在**清单内所有候选都不可读**时才返回 `None`（= `unavailable`），而不是第一份不可读就放弃；
3. 返回值必须携带"实际选中的是哪一份 + 为什么选它"，供 L03/L07 的引用不变验收。

**读取预算与取消（v0.1.3 重写，B-DR3-03/B-DR2-11）**：v0.1.2 的"每候选抽样 ≤1 MiB + 首末块"**不能证明整文件 `content_sha256` 相同**，因此 L03 的"合格副本切换"将不可判定。改为：

1. **资格判定的摘要判据必须覆盖整文件**：对进入第 3 段的候选，**按文件大小上限**决定是否允许全量流式 hash——`file_size ≤ per_candidate_bytes_cap`（默认 **256 MiB**，可配置）时**全量计算** `content_sha256`；超过上限则**直接判 `unavailable`**（reason=`exceeds_candidate_cap`），**不得**以抽样结果声称"同 hash"；
2. **抽样只用于排除**：允许先比对 `size` 与首末块以**快速排除**明显不同的候选（省 I/O），但**任何"合格"结论都必须由全量 hash 支撑**；
3. **单请求总量**：`max_candidates`（默认 64）与 `max_total_bytes`（默认 2 GiB 流式读）双上限；**任一超限 → `blocked`（reason=budget_exceeded）**，并把未判定的候选列入诊断；
4. **不引入五值之外的状态**（B-DR3-03）：v0.1.2 草案里的 `unknown` **撤销**——"未判定"在返回里表达为 `blocked`/`unavailable` + `pending_candidates` 诊断列表，错误模型仍**恰好五值**（A03 §2.4）；
5. **可取消**：调用方取消后不得继续读盘；已读字节计入证据（L06 的"有限资源/可取消"）。

**测试**：L01/L02/L03/L04（L03 的关键验收"撤首选→自动切换"由 `_handle` 承担）；预算与取消由 **L06** 与 **L12** 覆盖。

**⚠️ 实施偏差（v0.1.7 回填，2026-09-12；经 `B.VR` rev1/rejected、rev2/accepted_with_findings、rev3/accepted_with_findings 三轮收紧；待 owner 确认 = [S-10](owner-scope-decisions-2026-09-12.md) / [S-11](owner-scope-decisions-2026-09-12.md)）**：本段第 3 段的"同 hash"在 **B02 的实际实现**里是两条规则：

1. **验证通过的副本永远优先被服务**（无论 rank）——仍**真的读字节**并做**整文件**摘要比对（上限 256 MiB/候选；抽样只用于排除），验证通过时记 `verified_sha256`；
2. **只有在没有任何候选通过验证时**，才允许**一行**凭目录声明被服务：**本版本（文档自身 source 组）合格候选中那一行 legacy `is_canonical`**，trace 记 `unverified_<该行自身的失败状态>_on_pre_b02_canonical`。**注意：该行不是"pre-B02 会服务的那一行"的逐位复制**——pre-B02 有两个缺陷且 rev4 不恢复：(a) `.rejections` 当时按**子串**匹配（rev4 按**路径段**，因此 rev4 在 `my.rejections_backup/` 这类路径上**更宽**）；(b) 当时**不限定 source 组**（rev4 限定，因此 rev4 **更严**，不会取另一版本的行）。权威表述见 [evidence/b02-implementation.md](evidence/b02-implementation.md) §3 的差异表；
3. **其余任何副本都必须字节验证通过**，否则不返回句柄（→ `unavailable`）；**取消永不回答**（读取中途取消、收尾守卫、粘性取消都算）；
4. **字节级硬门归 B03 的读路径**（"只返回验证版本字节或明确失败"）——B03 落地前，规则 2 的那一行仍可能字节漂移而被服务（trace 已标注；见 [evidence/b02-implementation.md](evidence/b02-implementation.md) §8）。

> **v0.1.7 修订记录（同一版内，三次）**：rev2 曾写"首选（rank 1）副本凭声明服务"→ 被 `B.VR` rev2 用反例证伪（`.rejections` 占最优优先级时 pre-B02 = `missing` 而 rev2 = `reused_exact`）；rev3 曾写"锚定到 pre-B02 会服务的那一行，故不宽于 pre-B02 **由构造保证**"→ 被 `B.VR` rev3 用两个反例证伪（子串 vs 路径段、source 组限定）；rev4 改为上面的**差异列举**写法。

**另一处命名偏差（S-11）**：预算耗尽（`budget_exceeded`）在 `resolve` 里**不是**设计写的 `blocked`，而是"按 pre-B02 信任级服务首选副本 + trace 标记"：`ResolutionStatus` 只有五个值、没有 `blocked`，新增第六值会违反 A03 §2.4。`_ReadBudget` 的计数**每次请求重置**（取消保持粘性）。

**为什么让步**：A 侧**冻结断言**的合成目录里，文件字节与其声明的 `content_sha256` **和** `byte_size` 都不一致（`test_source_catalog_sql_pushdown.py` 把 13 B 的文件声明为 1000 B；`test_source_catalog_determinism.py` 用 `b"%PDF-fake"` 配 `sha256(b"same-bytes")`），因此任何"先验证再服务首选"的硬门都会失败 4 条既有断言：`test_source_catalog_determinism.py::{test_same_hash_three_roots_picks_priority_primary_preserves_all,test_same_period_different_hash_is_ambiguous}`、`test_source_catalog_sql_pushdown.py::{test_resolver_uses_sql_pushdown_not_all_table_query,test_old_period_not_shadowed_by_cap}`。按 **S-1**（只新增测试、**不得修改既有断言**），让步只能发生在实现侧。复跑命令与实测输出见 evidence 文件 §3。

---

## B03 —— 稳定只读字节提供（v0.1.1：补"读回复验"，闭合 TOCTOU，B-DR-07）

**目标**：返回的字节必须是**已验证版本**的字节。

**设计**（三级，含 v0.1.1 的复验要求）：

1. **固定句柄读取 + 读后复验**：以只读共享打开 → 记录 `size` + 首末块与全量流式 hash → **在返回前再次对"实际返回的字节"重算摘要**，与 `content_sha256` 比较；不一致即失败。**仅"打开时校验"不足以闭合 TOCTOU**：Windows 的共享模式只在打开时裁决，既有写者句柄不受后续只读打开影响（B-DR-07）。
2. **受控快照**：句柄不可固定（云占位/被占用/跨卷）时，读取**既有**受控快照，并在返回值标注 `bytes_source=snapshot` + 快照 hash。
3. **显式失败**：hash 不符/中断/占位不可读/ACL 拒绝/损坏 → 返回五值中的 `unavailable` 或 `blocked` + reason。

**禁止**：只信 `mtime`/文件名；在 `query`/`open` 内**隐式新建快照并宣称零写**（新建快照=另需批准的准备动作，写入路径与空间单列）；纯读取建缓存。

**测试**：L05（打开后替换/同 size 改内容/路径重指/symlink 逃逸）、L06（占用/ACL/占位/损坏/超大/中断）。

---

## B04 —— 路径留在诊断，引用不因搬家失效

- 绝对路径与 `location_id` **只用于诊断**；引用 = `document_id` + `content_sha256` + locator（locator 内含 `root_id` + 相对路径）。
- 搬家 → 新 location 行；旧行按 `location_status` 标记（`moved`/`missing`）；**解析时在 B02 的合格集合上重新定位**，命中同 hash 即同一版本（不触发重新下载、不改变模型输入）。
- 找不到任何合格副本 → `unavailable`；**不取另一修订**。
- **v0.1.1 明确（A-VR-02）**：现行 `scanner.py:1120-1128` 的 `ON CONFLICT(root_id,relative_path) DO UPDATE SET source_id=…,document_id=…` 会**改指**同一位置行，使被取代修订不再可打开 → "旧引用仍可解引用"是**本步的设计目标**，须由 L03/L07 负例验证。

**测试**：L03、L07。

---

## B05 —— metadata 合并：来源优先，冲突保留（v0.1.1：覆盖整条 UPDATE，B-DR-03；落点与持久化决策，B-DR-12）

**现状（已核实）**：`scanner.py:1007-1081`。开关在 `:1038`（`elif root.priority <= existing_document["metadata_priority"]`）；进入分支后 `:1078-1081` 的 `UPDATE documents SET primary_source_id=…, title=?, source_type=?, document_kind=?, published_date=COALESCE(…), source_status=?, metadata_priority=?, metadata_json=?, last_seen_at=?` —— **只有 `metadata_json` 受 `prefer_new` 影响（`:1074-1076`）**，其余列全部取自**按 priority 胜出**的那一份。v0.1 只写"metadata 真伪"是**不完整**的（B-DR-03 正确）。

**设计**：
1. 每个字段记录 **provenance**（来源标识 + 抓取时间 + **hash 或短规范化值**；**不得存原文片段**，见下条 v0.1.6 约束）；
2. 一致 → 取值 + 合并 provenance；冲突 → **保留全部候选 + 冲突标记**，不自动择一；
3. `priority` **退出"真伪"判定**，只在"必须给出单一值"时用于**候选排序**；
4. **覆盖面 = 上表全部列**（title / source_type / document_kind / published_date / source_status / primary_source_id / metadata_json），不只是 `metadata_json`。
5. **`metadata_json` 在胜利路径上也不得整列替换**（v0.1.6 新增，B-DR5-03）：`scanner.py:1073-1077` 在 `prefer_new` 时用新字典**整体替换**该列（会一并抹掉 `prompt_injection_review` 与 `r4_provenance`），`:1095-1099` 的更高优先级重扫分支**不是整列替换**（实测只写 `last_seen_at`，v0.1.6 更正，B-DR6-10），但它同样**不得**被改成整列替换——两处都按**读-改-写**处理。**F3 的锚点因此扩为 `scanner.py:1007-1099`**（含 `:1009-1027` INSERT）。

**落点与持久化（v0.1.2 定案，B-DR2-05/B-DR2-12）**：v0.1.1 的"只在读取合同输出、不落库"**无法满足 L08**——因为落选值已被 `scanner.py:1078-1081` 的 UPDATE **覆盖销毁**，读取层再也拿不到它们。因此 B05 改为：

1. **在写入侧停止销毁**：`scanner.py:1078-1081` 改为**保留**落选来源的值与 provenance，存进**既有列** `metadata_json`（**不新增列、不改 DDL**，因此无需 `store.py`，仍在 allowed F3 范围内）。
   ⚠️ **v0.1.5 关键更正（B-DR4-01，P1）**：该列是**多方共享的扁平 JSON 命名空间**，不是 B 的私有字段 —— 既有读取点至少包括：`service.py:271-272`（按 `$.acquisition.fiscal_year` / `$.dayu_meta.fiscal_year` 过滤）、`llm_summarizer.py:388-392`（按 `$.prompt_injection_review.*` 做 LLM 门，**且该文件在禁止表内，B 无权修**）、`prompt_injection.py:101-128`、`scanner.py:1039-1045`，以及 **`scripts/legacy_observer.py:90`**（FC-705/R9 权威账本用 `LIKE '%acquisition%'` 探测该列——shared 列的**非路径读取者**）。因此写入形状**必须是可加性的**：
   - **只在保留键下新增**：`{"r4_provenance": {"schema_version": "1.0", "fields": {<列名>: {"value": …, "sources": […], "conflicts": […]}}}}`；
   - **既有键一律原样保留**（不得重命名/搬移/改变类型）；
   - **回归断言**：L08 必须加一条 `json_extract` 断言，证明 **fiscal_year 过滤**与 **prompt_injection_review 门** 在改动后仍读到原值（否则本步即视为破坏共享命名空间，必须回到设计）；
   - B05 的读取侧只读 `r4_provenance`，**不得**假设整列由自己独占；
   - **禁止把原文片段写进 provenance**（v0.1.6，B-DR5-05）：只允许**来源标识 + 时间 + hash/短规范化值**，避免无意的正文入库给 `LIKE` 类消费者带来误命中；
   - 保留键带 **`schema_version`**（v0.1.6，B-DR5-11）：`r4_provenance = {"schema_version": "1.0", "fields": {…}}`（`r4_` 指 **R4 计划**，不是复审轮次）。
   形状示意（**仅新增保留键**）：`{"acquisition": {…}, "dayu_meta": {…}, "prompt_injection_review": {…}, "r4_provenance": {"schema_version": "1.0", "fields": {…}}}`；
2. **`metadata_priority` 的处置**：该列**保留**（由 `scanner` 继续维护，用于"必须给出单一值"时的排序提示），但**不再决定哪些列被写**；`:1038` 的 `elif root.priority <= existing_document["metadata_priority"]` 分支语义必须改写为"**只决定是否补充 provenance/冲突记录**"，不得再整体覆盖 `title/source_type/document_kind/published_date/source_status/primary_source_id`；
3. **读取合同**（B05 的输出）暴露 `provenance` 与 `conflicts` 两个字段；
4. **若 owner 要求把 provenance 提升为一等列**（可查询、可索引），那需要 `store.py` DDL/迁移 → **升级为独立工作包**（不在本包范围）。

**逐列合并规则（v0.1.3 新增，B-DR3-02）**：取消"整行覆盖"并不等于没有单值来源；B05 必须为每一列给出规则，否则读取侧会出现"没有值"或"值随扫描顺序变化"：

| 列 | 合并规则 | 冲突时 |
|---|---|---|
| `title` / `source_type` / `document_kind` | 取**声明该列且来源可追**的值；多来源一致 → 单值 + provenance 列表 | 真冲突 → **保留全部候选 + `conflicts`**，读取合同返回 **`blocked`**（执行计划 §B05 原文"真冲突仍 blocked/待选择"；v0.1.5 更正，B-DR4-08——`ambiguous` 只用于 **L07 的"版本关系未知"**，不用于字段冲突）；**不得按 priority 择一** |
| `published_date` | **只允许由"报告自身声明"的来源写入**（现有 `capture_ready` 恢复路径见下） | 冲突 → 保留候选 + `blocked` |
| `source_status` | 取**最新一次真实观测**的状态（可追时间戳） | 冲突 → 保留 + `blocked` |
| `primary_source_id` | 取 **exact-copy 组内**按 B02 第 4 段排序的第一份（**仅此列允许用排序结果**） | 无冲突概念 |
| `metadata_json` | 承载 `provenance` 与 `conflicts`（既有列，无 DDL 变更） | — |

**粒度与不变式（v0.1.5 补，B-DR4-08）**：状态是**响应级**（整份响应一个五值状态），冲突明细是**字段级**（`r4_provenance.fields[<列>].conflicts`）；`capture_ready` 的不变式 = "**只要有任一合格副本且身份/期间可判，capture_ready 不得因合并规则改变而变 false**"，该不变式须在 L09 用例里断言。

**必须保留的既有恢复路径（回归风险，B-DR3-02）**：`scanner.py:1046-1058` 的注释记录了 `capture_ready` 死锁——若 `published_date`/`source_url` 无法补齐，某些 capture 永远不就绪。B05 改写合并语义时**必须显式保留"后来来源补齐缺失列"的能力**（即：**后到的、更权威的字段可以补空值，但不能覆盖已确认的单值**），并在 L08 用例里加入"先缺后补"分支。

**测试**：L08（交换 priority/扫描顺序 → 业务事实不变、可信字段有来源、冲突保留）。

---

## B06 —— 本地可读与正式 capture 分离；**preview 合同归 B06**（v0.1.1：B-DR-14）

- 返回值携带**资格标签**：`preview`（本地可读、provenance 可能有缺口）vs `verified_input`（身份+期间+来源齐备）。
- **承载接口（v0.1.2 定案，B-DR2-07）**：本仓**没有顶层 `preview` 命令**（A03 §2.1/§4 已确认）；因此 B06 的承载**不是新命令，而是既有 `resolve` 的响应包**：
  - 载体 = **`ResolutionEnvelope`**（`resolver.py:359-417`，由 `:418-552 build_resolution_envelope` 构造）新增 **`qualification`** 字段（取值 `preview` / `verified_input` + 缺口清单）；
  - 该字段由 **B06 定义**，并要求**消费者既有的许可门**（`revenue-forecast/scripts/company_wiki_source.py:280-281` 的 `capture_ready`）与之对齐——B 只提供事实，**不改消费者**；
  - 若 owner 要求新增独立命令，则属**新增能力**，须单列请求/拒绝语义与 allowed 文件（**待批准**）。
- 缺 URL/捕获日志但有本地导入 hash → 可 preview 并标缺口；身份/期间不明 → 正式合同 `blocked`；缺文本 → 只返回所需产物的 pending，不伪造 URL、不默认联网。

**测试**：L09、L10（**不含** VR-N21：无门外发出口属 owner R-4 独立工作包，S-2）。

---

## B07 —— 唯一版本化读取合同（v0.1.1：范围重划，B-DR-05）

**目标**：对外只有一个**版本化**读取合同；不兼容**明确报错**；旧客户端在**边界 adapter** 一次转换。

**范围重划（v0.1.2 定案，B-DR-05 + B-DR2-03）**：v0.1 把"缺 policy 禁止静默退回 `companies`"与"边界 adapter"写成 B07 的实现，但两者都没有可改的文件（消费者仓与 `adapters/*` 都在禁区）。按执行计划 §B「主责任 wiki；filing/revenue 仅最小协议适配」，**B07 只签 wiki 侧**：

| L11 验收句（矩阵原文） | B 可签部分（wiki 侧，本包 allowed 内） | 不可签部分（归 C / 消费者仓） |
|---|---|---|
| "支持兼容由单 adapter 转换且来源不变" | **wiki 侧的版本化读取合同本身**：`schema_version` + `ResolutionEnvelope`（`resolver.py:359-552`）的**当前版本**判定与拒绝语义（`not_found/not_indexed/unavailable/blocked/ambiguous`）；**N-1 不在其中**（下方说明） | **消费者侧的转换实现**：`filing-fetch/scripts/filing_contracts.py`、`revenue` 侧 adapter —— 归 **C**；B 只在验收记录里注明"消费者侧未验" |
| "未知拒绝，无 companies 静默 fallback，无第二权限语义" | **wiki 侧不新增任何 fallback 分支**；在合同里**显式声明"本接口无目录级 fallback 语义"**；并给出探测负例（构造未知版本 → 必须 `not_found`/`blocked`，不得读到别的目录） | **消费者侧的 `companies` fallback 代码**（若存在）在 `filing-fetch` 内 → 归 **C**；B 不得声称已删除它 |
| （新增，本包要求）`resolve` 输出的 **policy_export payload 字节/hash 不变** | ✅ **必须由 B 自测**（见 [test-acceptance-map.md](test-acceptance-map.md) §1c 的 `B-payload-hash`） | — |
| ⚠️ **N-1 支持** | **v0.1.5 更正（B-DR4-03）：从 B 的完成定义中移除** —— 两侧代码目前都只接受 `"1.0"`（wiki `resolver.py:163-166`、filing `filing_contracts.py:273-277`），**不存在 N-1 规则**；`filing-audit.md:61` 反而要求废除"字段缺失即降级"的伪 N-1，改为**显式版本协商** | **登记为待定义项**：N-1 的定义与实现属**跨仓协议工作**，不在 B 的完成定义内；B 只保证"**未知版本必须显式拒绝**"（`not_found`/`blocked`），不承诺向后兼容 |

> **B07 的"完成"因此是**："wiki 侧版本化合同 + 未知版本显式拒绝 + 无新增 fallback + payload hash 不变"四件（**不含 N-1**，见上表说明）；其中 **`payload hash 不变` 当前为 `blocked`**（无冻结基线、取值需待批 CLI，见 [test-acceptance-map.md](test-acceptance-map.md) §1c），**不得计入已满足项**；**消费者侧的 adapter 转换与 fallback 删除明确不在 B 的签名内**（C 阶段）。

**测试**：L11、L12（L11 的消费者侧部分标记为"B 只验 wiki 侧"）。

---

## B0x —— 复杂度棘轮约束（v0.1.5 新增，B-DR4-06）

**事实（reviewer 实测复算）**：`tests/contract/test_fc1204_complexity_ratchet.py` 是**默认运行**的门，且以下文件**恰好顶格**：

| 文件 | 实测 | 冻结上限 |
|---|---|---|
| `config.py` | 46 | 46 |
| `scanner.py` | 140 | 140 |
| `policy.py` | 5 | 5 |
| `resolver.py` | 32 | 103（有余量） |
| `models.py` | 5 | 18（有余量） |

**另一道默认门（v0.1.6 新增，B-DR5-06）**：**新增文件本身有上限** —— 棘轮的 `NEW_FILE_MAX = 10`，且 CI 实跑**覆盖率棘轮**（`tests/contract/test_fc1204_coverage_ratchet.py`，`ci.yml:64`）：**TIER1 `policy.py`/`service.py` = 95%**、**TIER2 `resolver.py` = 86%**。B 的 F10 新测试**只增文件不增被测源码**，但 B05 改 `service.py`、B02 改 `resolver.py` 会**直接影响这两档覆盖率** → 每步实施后必须**真跑覆盖率棘轮**（`FC1204_COVERAGE_GATE=1`），并把结果入证据。

**后果**：B 在 `config.py`/`scanner.py`/`policy.py` 内**只要新增一个判定点，棘轮即失败**；而该门自述的补救是"**更新棘轮表**"，那需要**修改既有测试文件**——与 F10"仅新增"**互斥**。

**设计约束（B 必须遵守）**：
1. **B02/B03/B05/B07 的实现必须在棘轮文件内保持复杂度中性**（不新增判定点；用既有分支内的数据流与提前返回重组，或把新判定放进**新增的独立模块/函数**——新增文件不计入既有文件的上限）；
2. 每一步实施后**必须真跑** `pytest tests/contract/test_fc1204_complexity_ratchet.py -q`，并把结果入证据；
3. 若某步**无法**做到复杂度中性，则该步**停止**，并按 §5 的边界流程请 owner 决定"是否允许更新棘轮表"（属新增 scope 问题 **S-7**，见 [task_plan.md](task_plan.md) §5）。

## B08–B10（实施与验收，本轮不执行）

- **B08**：独立 VR 在新隔离环境重跑 L01–L12（+必要旧 C01–C10），**独立文件/OS 观察**证明本地零副作用；不得用人工构造 catalog 结果冒充真实 parser/索引；云场景无法测**如实标限制**。
- **B09**：真实四 root + 第五 root 新注册，做一次端到端 `query → open → consumer` 最小读取；独立 AR 从原文重核身份与 hash；**只允许隔离副本变化**。
- **B10**：小范围切到单一读取链，旧入口仅显式版本 adapter；记录可回退版本与移除条件；**无法兼容则停止切换**，不永久双跑。

**共同前置**：隔离副本（G8，两级方案见 [findings.md](findings.md) F-B00-3，B.DR 已独立复核技术前提）、owner 样本确认（G7）、D.SAFE 交叉。
