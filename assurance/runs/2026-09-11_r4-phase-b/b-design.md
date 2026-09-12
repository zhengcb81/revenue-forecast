# B 阶段设计（b-design v0.1.1）—— 位置透明索引与只读读取

> 状态：**DESIGN_ONLY**。本文件只描述"要做什么、改哪些文件、怎么验"，**未修改任何产品代码**。
> 依据：R4 执行计划 §B（B01–B10）；阶段 A 冻结合同 **v0.4.1**（[root-contract](../2026-09-11_r4-phase-a/root-contract.md)、[operation-contract](../2026-09-11_r4-phase-a/operation-contract.md)、[identity-contract](../2026-09-11_r4-phase-a/identity-contract.md)）；owner 六项裁定 + 其**范围更正**（[owner-rulings](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md)）。
> 精确定位与哈希见 [file-scope.md](file-scope.md)；测试映射见 [test-acceptance-map.md](test-acceptance-map.md)；风险与停止规则见 [risk-and-stop-rules.md](risk-and-stop-rules.md)。
> **v0.1.1 说明**：本版按 `B.DR` 的 20 条发现重写（P0×1 + P1×7 + P2×9 + P3×3），其中 P0 与 A07/A08 命中同一事实。**逐条回应见 [findings.md](findings.md) F-B01-1**。

## 总原则（来自阶段 A 合同，B 不得违反）

| 编号 | 原则 | 来源 |
|---|---|---|
| P-1 | 能力四轴（可读/可写/可外发/可复用）**互不推导** | A02 R1 |
| P-2 | 未注册 root / 显式 deny 不因"默认等价"放行 | A02 R2 |
| P-3 | **假保证字段不得留在"已强制"清单**（`symlink_policy` **与 `read_only`**） | A02 R7 + v0.4.1 |
| P-4 | 准入语义**只能有一套**（= 生效的 `config.py`）；**导出路径 `export_policy_2x` 在产，其字节/hash 契约不可破坏** | A02 R8 + v0.4.1 范围更正 |
| P-5 | 纯查询接口不得触网/不得 `ensure`/不得改 worker 状态/不得写 catalog；**R 轴 = 无逻辑写 + 无网络 + 无子进程**，进程级副作用单列 | A03 §2.1 |
| P-6 | 路径诊断信息**不得进入业务身份**（9 处残留登记整改） | A04 R4（owner R-6） |
| P-7 | 显式 `reusable_for_filing: false` **必须生效**，且**两处活实现收敛为一处** | owner R-2 + v0.4.1 更正 |
| P-8 | `privacy_class` 缺省**不再默认可外发**；整改范围含 `legacy_research_ingest.py:128-136` | owner R-4 + v0.4.1 扩大 |
| P-9 | 接口错误**恰好五值**：`not_found` / `not_indexed` / `unavailable` / `blocked` / `ambiguous`（+ reason）；重试性/预算/超时是独立字段 | A03 §2.4 |

---

## B01 —— 字段唯一 owner 与**旧字段版本映射**（v0.1.1 补齐 B-DR-02 要求的交付物）

### B01.1 字段唯一 owner

| 语义 | 唯一 owner（设计） | 现状（已核实） | 本步决定 |
|---|---|---|---|
| 物理位置（path、adapter、symlink 政策、大小/编码限制） | **storage 层**（`config.py` → `models.RootSpec`） | `config.py:70-118`（活、唯一准入）；`policy_2x.py`/`policy_3x.py` 的 **loader** 无生产调用者 | 按 owner R-3（**范围 = 仅准入 loader**）：收敛为一套；**不动 `export_policy_2x`** |
| 业务身份（document_id、version/source_hash、locator） | **catalog 层**（`models.py` + `service.py` 投影） | `service.py:621-663` 规范位选择含路径/优先级（残留） | 按 owner R-6：**登记整改**；B 不改身份语义，先把 locator 显式化（B04） |
| 可复用资格 | **policy 层单一函数** | **三处活实现**（v0.1.2 更正，B-DR2-01）：① `resolver.py:782-786`/`:933-940`（kind-only，fail-open，不读字段）；② `policy.py:67-72 _effective_reusable`（读字段，fail-closed）；③ **`policy_2x.py:308-312 _effective_reusable_2x`**（读字段，经 `:292` 被 `export_policy_2x` 调用，再由 `cli.py:849-851` 在产） | 按 owner R-2：**对齐①的语义到②③**（`false` 生效），**不是**"删除多余实现"——③位于被冻结的跨仓导出路径（P-4），删不得。任何使②③输出变化的改动**必须与 filing-fetch 的 policy_hash 迁移同步** |
| 外发策略 | **动作边界**（调用外部服务那一刻） | `llm_summarizer.py:333-337`（白名单）；**外加一处无门出口** `legacy_research_ingest.py:128-136` | 按 owner R-4：缺省不外发 + 补门（范围含无门出口）；**注意 R-4 在现网惰性**（见 B01.2） |
| 文档证据质量 | **不由 root 字段承载**（与能力正交） | A02 C5 | B 不引入"质量即能力" |

### B01.2 旧字段版本映射（**16 个字段名 / 12 行合并项**——v0.1.2 更正计数与遗漏，B-DR2-10；`admission_profile_id` 于 v0.1.2 补入）

| 字段（现状） | 语义 owner | 目标处置 | 迁移/兼容条件（**必须先测 N-1，L11**） |
|---|---|---|---|
| `read_only` | storage | **降级为"文档性字段"**：真实可写判据 = `kind == 'company_raw'`（`canonical_writer.py:126-131/284-287`） | 保留字段以免破坏 YAML 解析；**删除其"安全承诺"表述**；若未来要真强制，须实现读取点并配负例 |
| `reusable_for_filing` | policy（单一函数） | **保留并使 `false` 生效**（对齐三处实现，见 §B01.1） | ②③ 的输出变化 ⇒ **policy_hash 变化** ⇒ 必须与 filing-fetch 的 FC-501 期望值同步迁移（跨仓）；`None` 保持"跟随 kind" |
| `symlink_policy` | storage | **候选删除**（owner R-1 倾向删） | 删除前须确认无外部消费者读取该 YAML 键（含 filing/revenue 与本仓测试）；删除是 YAML 变更 → 触发 A01 重冻结 |
| `priority` | storage | **保留，但只作排序**（B02 第 4 段），**退出 metadata 真伪判定**（B05） | 无 schema 变更；语义变更须有 L01/L08 负例 |
| `privacy_class` | 动作边界 | **缺省改为不外发**（owner R-4） | **v0.1.2 关键限定（B-DR2-02）**：现网 `config/source_catalog.yaml` 的**四个 root 全部显式声明 `privacy_class: public`**（`:19/:24/:29/:40`）→ **受影响集合 = 0，该改动在现网是惰性的**；其验收**只能靠合成配置**（新增 root 或删掉声明）。`models.py:105` 与 `config.py:144` 两处默认值必须同改；**不得声称现网行为会因此变化** |
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

**DR 检查点（B.DR 第一项）**：① 字段映射完整（12 行 / 16 名 + `kind`）；② **`false` 语义在①resolver 上生效，且②③的输出变化与 policy_hash 迁移绑定**（v0.1.2 更正：不是"收敛为一处"，因为第三处在冻结的导出路径内）；③ 显式 `false` 含义保留。

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

**读取预算与取消（v0.1.2 补，B-DR2-11）**：
- 资格判定（第 3 段）**每个候选最多读 `min(file_size, 1 MiB)` 采样 + 首末块**用于摘要校验；**单次请求的资格判定总量上限 = 32 MiB / 64 个候选**，超限即停止并把剩余候选标 `unknown`（不是 `unavailable`）；
- **不联网**（见下）；**必须可取消**：调用方取消后不得继续读盘（L06 的"有限资源/可取消"）；
- 交付读取（B03）**另计预算**：单次 `open_version` 上限由调用方给出 `max_bytes`，超过即 `blocked`。

**测试**：L01/L02/L03/L04（L03 的关键验收"撤首选→自动切换"由 `_handle` 承担）；预算与取消由 **L06** 与 **L12** 覆盖。

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
1. 每个字段记录 **provenance**（root/source/抓取时间/原始片段或 hash）；
2. 一致 → 取值 + 合并 provenance；冲突 → **保留全部候选 + 冲突标记**，不自动择一；
3. `priority` **退出"真伪"判定**，只在"必须给出单一值"时用于**候选排序**；
4. **覆盖面 = 上表全部列**（title / source_type / document_kind / published_date / source_status / primary_source_id / metadata_json），不只是 `metadata_json`。

**落点与持久化（v0.1.2 定案，B-DR2-05/B-DR2-12）**：v0.1.1 的"只在读取合同输出、不落库"**无法满足 L08**——因为落选值已被 `scanner.py:1078-1081` 的 UPDATE **覆盖销毁**，读取层再也拿不到它们。因此 B05 改为：

1. **在写入侧停止销毁**：`scanner.py:1078-1081` 改为**保留**落选来源的值与 provenance，存进**既有列** `metadata_json`（**不新增列、不改 DDL**，因此无需 `store.py`，仍在 allowed F3 范围内）——形如 `{"value": …, "provenance": [ … ], "conflicts": [ {value, source, captured_at} ]}`；
2. **`metadata_priority` 的处置**：该列**保留**（由 `scanner` 继续维护，用于"必须给出单一值"时的排序提示），但**不再决定哪些列被写**；`:1038` 的 `elif root.priority <= existing_document["metadata_priority"]` 分支语义必须改写为"**只决定是否补充 provenance/冲突记录**"，不得再整体覆盖 `title/source_type/document_kind/published_date/source_status/primary_source_id`；
3. **读取合同**（B05 的输出）暴露 `provenance` 与 `conflicts` 两个字段；
4. **若 owner 要求把 provenance 提升为一等列**（可查询、可索引），那需要 `store.py` DDL/迁移 → **升级为独立工作包**（不在本包范围）。

**测试**：L08（交换 priority/扫描顺序 → 业务事实不变、可信字段有来源、冲突保留）。

---

## B06 —— 本地可读与正式 capture 分离；**preview 合同归 B06**（v0.1.1：B-DR-14）

- 返回值携带**资格标签**：`preview`（本地可读、provenance 可能有缺口）vs `verified_input`（身份+期间+来源齐备）。
- **承载接口（v0.1.2 定案，B-DR2-07）**：本仓**没有顶层 `preview` 命令**（A03 §2.1/§4 已确认）；因此 B06 的承载**不是新命令，而是既有 `resolve` 的响应包**：
  - 载体 = **`ResolutionEnvelope`**（`resolver.py:359-417`，由 `:418-552 build_resolution_envelope` 构造）新增 **`qualification`** 字段（取值 `preview` / `verified_input` + 缺口清单）；
  - 该字段由 **B06 定义**，并要求**消费者既有的许可门**（`revenue-forecast/scripts/company_wiki_source.py:280-281` 的 `capture_ready`）与之对齐——B 只提供事实，**不改消费者**；
  - 若 owner 要求新增独立命令，则属**新增能力**，须单列请求/拒绝语义与 allowed 文件（**待批准**）。
- 缺 URL/捕获日志但有本地导入 hash → 可 preview 并标缺口；身份/期间不明 → 正式合同 `blocked`；缺文本 → 只返回所需产物的 pending，不伪造 URL、不默认联网。

**测试**：L09、L10（含 A07 的 VR-N21：无门外发出口的负例）。

---

## B07 —— 唯一版本化读取合同（v0.1.1：范围重划，B-DR-05）

**目标**：对外只有一个**版本化**读取合同；不兼容**明确报错**；旧客户端在**边界 adapter** 一次转换。

**范围重划（v0.1.2 定案，B-DR-05 + B-DR2-03）**：v0.1 把"缺 policy 禁止静默退回 `companies`"与"边界 adapter"写成 B07 的实现，但两者都没有可改的文件（消费者仓与 `adapters/*` 都在禁区）。按执行计划 §B「主责任 wiki；filing/revenue 仅最小协议适配」，**B07 只签 wiki 侧**：

| L11 验收句（矩阵原文） | B 可签部分（wiki 侧，本包 allowed 内） | 不可签部分（归 C / 消费者仓） |
|---|---|---|
| "支持兼容由单 adapter 转换且来源不变" | **wiki 侧的版本化读取合同本身**：`schema_version` + `ResolutionEnvelope`（`resolver.py:359-552`）的兼容判定；**N-1 支持**的判定逻辑与拒绝语义（`not_found/not_indexed/unavailable/blocked/ambiguous`） | **消费者侧的转换实现**：`filing-fetch/scripts/filing_contracts.py`、`revenue` 侧 adapter —— 归 **C**；B 只在验收记录里注明"消费者侧未验" |
| "未知拒绝，无 companies 静默 fallback，无第二权限语义" | **wiki 侧不新增任何 fallback 分支**；在合同里**显式声明"本接口无目录级 fallback 语义"**；并给出探测负例（构造未知版本 → 必须 `not_found`/`blocked`，不得读到别的目录） | **消费者侧的 `companies` fallback 代码**（若存在）在 `filing-fetch` 内 → 归 **C**；B 不得声称已删除它 |
| （新增，本包要求）`resolve` 输出的 **policy_export payload 字节/hash 不变** | ✅ **必须由 B 自测**（见 [test-acceptance-map.md](test-acceptance-map.md) §1c 的 `B-payload-hash`） | — |

> **B07 的"完成"因此是**："wiki 侧版本化合同 + N-1 判定 + 无新增 fallback + payload hash 不变"四件；**消费者侧的 adapter 转换与 fallback 删除明确不在 B 的签名内**（C 阶段）。

**测试**：L11、L12（L11 的消费者侧部分标记为"B 只验 wiki 侧"）。

---

## B08–B10（实施与验收，本轮不执行）

- **B08**：独立 VR 在新隔离环境重跑 L01–L12（+必要旧 C01–C10），**独立文件/OS 观察**证明本地零副作用；不得用人工构造 catalog 结果冒充真实 parser/索引；云场景无法测**如实标限制**。
- **B09**：真实四 root + 第五 root 新注册，做一次端到端 `query → open → consumer` 最小读取；独立 AR 从原文重核身份与 hash；**只允许隔离副本变化**。
- **B10**：小范围切到单一读取链，旧入口仅显式版本 adapter；记录可回退版本与移除条件；**无法兼容则停止切换**，不永久双跑。

**共同前置**：隔离副本（G8，两级方案见 [findings.md](findings.md) F-B00-3，B.DR 已独立复核技术前提）、owner 样本确认（G7）、D.SAFE 交叉。
