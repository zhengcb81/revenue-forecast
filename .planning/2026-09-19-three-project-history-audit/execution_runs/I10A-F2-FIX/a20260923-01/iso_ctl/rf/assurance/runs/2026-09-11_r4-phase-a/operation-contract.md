# A03 operation-contract —— query_local / open_version / request_work（v0.4.1，已按 A.DR rev1/rev2/rev3 与 A.VR 更正）

> 🔴 **v0.2 更正（2026-09-11，回应 A.DR rejected）**：
> 1. **`identify` 不是无条件只读**（A-DR-04）：`cli.py:1080-1087` 在 `--refresh` 时调用 `OfficialSecurityMasterRefresher.refresh` → `security_identity.py:20` 构造请求、`:26-45` https 端点、`:1007` `requests.get`、`:348` `write_text`。**网络 + 本地写**。→ `identify` 移入"**flag 条件**"类，默认只读、`--refresh` 属 **N+W**。
> 2. **v0.1 的清单漏了 7 个叶子命令**（A-DR-05）：`worker-status/start/resume/pause/stop`（经 `add_worker_control_parser`，`cli.py:579`；分派 `:1405/:1479/:1484/:1489/:1494`）、`derived-audit`（`:972`）、`import-portfolio`（`:1336`，**规范写入**）。其中 `worker-pause/resume` 正是本契约 R3 点名要防的 **pause** 动作 → 已补入 §2.2 **S** 类。
> 3. **轴 X 混淆了"本地导出"与"对外外发"**（A-DR-12）：`export` 的 `export_dir` 默认落在 `catalog_dir/index`（`models.py:206-208`）——是**本地**动作。轴拆为 **X-local**（写入本地导出目录）与 **X-egress**（送外部服务/LLM）。
> 4. **help 文本错配**（A-DR-10）：v0.1 把 `identity-enrichment preview`（`cli.py:277`）与 `activation preview`（`:639`）的说明互换，并把"自述只读"错挂到 `extraction-quality`（`:366`）。已更正。
>
> 状态：**草案 v0.2，待 A.DR 复审**。

## 1. 三个设计接口（语义冻结）

| 接口 | 语义 | **禁止** | 失败语义 |
|---|---|---|---|
| **`query_local`** | 在**已索引集合**内查询元数据/位置/证据；`latest` 只指已索引集合中的最新版本 | 不得触网、不得 `ensure`/download、不得改 worker 状态、不得写 catalog、不得启动子进程 | 只返回"未找到/未索引"，**不得**隐式转为下载或补索 |
| **`open_version`** | 打开**指定版本**（`document_id` + 版本/source hash + locator）并返回字节/证据 | 不得改变选中版本、不得因"缺副本"改写索引、不得外发内容 | 版本不可定位 → 显式状态；不得回退到"另一个看起来相同的文件" |
| **`request_work`** | **显式**请求产生新工作（下载/规范化/摘要/抽取等），带预算与授权 | 不得被前两个接口间接触发；不得后台自启动 | 每次请求有独立回执（command card）：入口/argv/env/读写集合/网络目的地/预算/timeout |

**契约规则 R3**：任何"纯查询"接口若可能触发 `ensure`/`download`/`pause`/worker 启动，**该设计退回**（执行计划 §A03 原文）。`query_local` 与 `request_work` 必须在**进程、写入集合、网络目的地**三个层面可区分。

## 2. 现有命令映射（**分类依据已升级：真实解析器 `--help` 探针**）

> **2026-09-11 更新**：owner 已批准 `--help`-only command-manifest，**52 次探针全部 rc=0、零副作用**（前后快照：catalog/config/`__pycache__`/git 全未变）。
> 权威表面积：**41 个顶层命令 + 10 个嵌套 = 51**（`documents{retire,restore}`、`identity-enrichment{preview,verify,reject}`、`activation{preview,apply,rollback}`、`runtime-policy{show,apply}`）。
> 证据：[evidence/cli-help-matrix.json](evidence/cli-help-matrix.json)、[command-manifest.json](command-manifest.json)、[baseline-map.md](baseline-map.md) §4。
> 下列分类因此从"暂定（源码 grep）"升级为"**依据真实 help 文本**"；但仍**不是行为验证**——`--dry-run`/真实行为探针留 A06/VR（需隔离副本）。

> 分类轴：**R**=只读 / **W**=本地写 / **N**=网络或 provider / **X**=外发（LLM/外部服务/导出到外部位置） / **D**=破坏性（删除/回收） / **S**=系统（任务/自启动/后台）。

### 2.1 可支撑 `query_local`（R，**flag 条件须标注**）

> **v0.4.1 定义（A-VR-03/A-VR-07 要求统一口径）**：本表的 **R 轴 = 无逻辑写 + 无网络 + 无子进程**。**进程级文件系统副作用单列**（见本表 `进程级副作用` 列）：即使"不写业务数据"，打开**可写** `CatalogStore` 仍会 `mkdir` 父目录、以读写方式连接、设 WAL、跑 DDL 与增量迁移并 commit（`store.py:925/932/995-997/1008`）。**凡是带✱的行 = 会建库/迁移但无逻辑写**；要变成真正的只读，须改走 `SourceCatalog.reader`（`reader.py:165/181`：`mode=ro` + `PRAGMA query_only=ON`）。

| 命令 | help 摘要（实测） | 进程级副作用（v0.4.1） | 备注 |
|---|---|---|---|
| `query` | query catalog metadata and artifact paths | 只读 reader（无建库） | 纯查询 |
| `evidence` / `evidence-list` | 按 source ID + locator 查单条 / 列有界证据 | 只读 reader | 纯查询 |
| `sections-list` | list extracted MD&A / business sections for one document | 只读 reader | 纯查询 |
| `size-report` | read-only catalog size / disk-health report | 只读 reader | help 自述只读 |
| `status` | show catalog counts | 只读 reader | 纯查询 |
| `duplicates` ✱ | list exact-copy groups and protected canonical locations | **建库/WAL/DDL/迁移**（`cli.py:1043` 构造可写 store） | 无逻辑写，但**不是零副作用** |
| `duplicate-preview` ✱ | 重校验一份非规范 exact-copy 并签发确认 token | **建库/WAL/DDL/迁移**（`cli.py:1152`） | token **不落盘**（`duplicate_cleanup.py:361/392-396`，A.VR 已静态确认） |
| `identity-enrichment preview` ✱ | preview a candidate assertion **without writing**（`cli.py:277`） | **建库/WAL/DDL/迁移**（`cli.py:1159`） | 断言不写库，但库文件会被建/迁移 |
| `activation preview` ✱ | preview（`cli.py:634-637` 分组 help；叶子 help `:639-641` "read-only: which assertions would flip"） | **建库/WAL/DDL/迁移**（`cli.py:1270`） | 自述只读；**未自述具体读写集合** → 待 VR 行为证明 |
| `startup-status` | show Windows logon task status | 无（系统查询） | 只读（系统面） |
| `runtime-policy show` | load and print the current snapshot（absent 时 fail closed） | 只读 | 只读 |
| `extraction-quality` | assess deterministic source/extraction quality **without span bodies**（`cli.py:366`） | **已静态确认为只读**（`extraction_quality.py:263-270`，A.VR 结论） | 归 R |
| `resolve` | resolve an existing source **before any downloader is considered** | 只读（`cli.py:1165-1200` 只碰读模型；且 `:1182` 会输出 policy_export 快照，见 §2.3） | 设计上属"查询+复用" |
| **`identify`（flag 条件）** | resolve a company name/alias/ticker | 默认：只读且**不写**（`security_identity.py:308-311/418-433`，A.VR 静态确认）；`--refresh` = **网络 + 本地写** | `--refresh` 属 **N+W**，不得置于 `query_local` 之后 |

> **注（避免重复计数）**：`ensure` 的**裸调用形式**（无 `--allow-download`、mode≠`latest_as_of`）按其实现 `cli.py:752-758` 实际是**纯读**路径，但本表**不另计一行**——该叶子已在 §2.2 的 N 类按 **flag 条件**登记（同一叶子只计一次）。同理 `activation preview` 在本表、`activation apply/rollback` 在 §2.2 S 类。

### 2.2 必须归入 `request_work` 或更高授权（非查询）

| 类别 | 命令（**v0.2 已补全**） |
|---|---|
| **W 本地写** | `scan`、`normalize`、`summarize`、`fingerprint-backfill`、`extract-sections`、`documents retire`、`documents restore`、`identity-enrichment verify`、`identity-enrichment reject`、`reconcile-retire`（dry-run 默认）、`focus-cleanup`（dry-run 或 apply）、`run`（scan→normalize→summarize→export）、**`derived-audit`（`cli.py:972`/`:976-980` 调 `reconcile_artifacts`）**、**`import-portfolio`（规范写入，`cli.py:1336`）** |
| **N 网络/provider**（**flag 条件，v0.2 按 `cli.py:742-824` 细化；v0.3 补全条件连接词**） | `ensure`：**裸调用（无 `--allow-download` 且 mode≠`latest_as_of`）走 `:752-758` 纯读路径（R）**；一旦 `--allow-download` 或 `latest_as_of`，即进入写流程（`:760-762` 先取 `get_catalog().store`，**写入器初始化可能先建 catalog**）。三道闸（**按源码原文给全连接条件**）：① `--allow-download` 决定是否进入获取路径（`:751-752`）；② `latest_as_of` 即使无该 flag 也强制走写流程（help 自述"仅返回 metadata-only gap plan、不下载"）；③ **`if args.allow_download and desired_state == "paused" and not args.allow_acquisition_while_paused:` → `RuntimeError` 拒绝**（`:764-771`；**注意三个条件是与关系，缺少 `args.allow_download` 时该拒绝分支不成立**）；**仅当 `args.allow_download and desired_state == "paused"` 时才写入暂停期审计**（`:772-778` → `_append_paused_acquisition_audit`，`:109` 追加 `catalog_dir/paused_acquisition.log`，best-effort、失败只 warn 不阻断）。`close-gap`：同样在 paused 且无 override 时拒绝（`:1217-1218`，条件为 `desired_state == "paused" and not args.allow_acquisition_while_paused`）。**`identify --refresh`**（网络+写，见更正 1） |
| **X-local 本地导出** | `export`（写 `catalog_dir/index`，`models.py:206-208`）、`policy-export`、`archive-retired-evidence` |
| **X-egress 对外外发** | LLM 摘要路径（经 `llm_summarizer`，受 `privacy_class` + review receipt 门控；具体入口命令待 VR 确认，见 §2.3） |
| **D 破坏性** | `prune-retired-evidence`（**物理删除**，dry-run 默认）、`duplicate-recycle`（移入回收站，需确认 token） |
| **S 系统/后台** | `worker`、**`worker-status` / `worker-start` / `worker-resume` / `worker-pause` / `worker-stop`**（`cli.py:579` 注册、`:1405/:1479/:1484/:1489/:1494` 分派）、`install-startup` / `uninstall-startup`、**`activation apply` / `activation rollback`**、`runtime-policy apply`（**v0.3.1 更正，A-DR3-13**：`activation preview` 只在 §2.1，不在此行重复，S 类叶子数 = **11**，与 §2.3 的对账一致） |

### 2.3 高风险映射（v0.4.1：两条已静态闭环，一条新增无门出口）

0. **【新增·P1，A-VR-04】无门的正文外发**：`company_wiki/src/company_wiki/legacy_research_ingest.py:128-136` —— `content[:8000]` 直接进 `self._llm.generate(prompt)`（prompt 组装 `:117-121`，发送 `:124`），**不读 `privacy_class`、不查 review receipt、不做字节绑定**；唯一前置是构造时注入了 client（`:114-115`）。这是**独立于 `worker` 的第二条 LLM 出口**，且**完全没有门**。→ 已并入 owner **R-4** 的整改范围（见 [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md)），并须在 A06/L10 增加负例（A.VR 的 VR-N21）。
1. **`identify` 的 flag 分裂（A-DR-04 要求登记）**：`cli.py:1080-1087` 在 `--refresh` 时构造 `OfficialSecurityMasterRefresher` → 网络 + 本地写（`security_identity.py:1007`/`:348`）。**v0.4.1 补充静态结论（A.VR）**：**无 `--refresh` 时 `identify` 不写**（`security_identity.py:308-311/418-433`）→ 默认形式可留在 R；`--refresh` 走 `request_work` 或更高授权，VR 脚本**只**用无 `--refresh` 形式。
2. **`resolve` 是否绝对无网络/无写——静态部分已收窄**：`cli.py:1165-1200` 经只读读模型；分支内无 `subprocess`、无网络调用。**v0.4.1 补充（B.DR-01/A.AR-05）**：`resolve` 会在 `cli.py:1182` 输出 **policy_export 快照**（`_policy_export_payload` → `export_policy_2x`），该快照是 filing-fetch 的 FC-501 containment 来源 → **resolve 是"只读但产生对外契约产物"**，B02/B04 改动 resolve 时必须保持该 payload 的字节/hash 契约。
3. **`summarize` 与 LLM 出口的关系——v0.4.1 静态闭环（A.VR 结论）**：LLM 出口**只经 `worker`**：`cli.py:1499-1519` 在 `worker` 分支构造 `build_configured_llm_client` 并注入 `SourceCatalogWorker`；`worker.py:689-705` 在暂停态检查（`cli.py:1510`）+ `scheduler_policy.require_dispatch(SourceOnlyStage.SUMMARIZING, "summarize_with_llm")`（`:691-693`）+ retry-after 窗口（`:689-690`）之后调用 `self.catalog.summarize_with_llm`。**CLI `summarize`/`run` 是确定性的**（`cli.py:959-960` → `get_catalog().summarize(...)`，无 LLM client）。→ **X-egress 入口 = `worker`（S 类）**；本契约 §2.2 已在 S 类列 `worker`，**v0.4.1 追加标注：`worker` 同时是 X-egress 入口**。加上第 0 条，X-egress 入口**共两个**（一个受三重门控、一个完全无门）。
4. **`activation preview` 的只读性**：叶子 help 自述只读（`cli.py:639-641`），但**会建库/迁移**（§2.1 ✱）→ 只读性须由 VR 用行为证明（观察目标是"业务数据未被改"，不是"库文件未被碰"）。
5. **`duplicate-preview` 的 confirmation token**：**已静态确认不落盘**（`duplicate_cleanup.py:361` 派生、`:392-396` 重算）→ 归 R（受 §2.1 ✱ 的进程级副作用约束）。

### 2.4 接口错误模型（v0.4.1 新增，采纳 A.VR 的标准化词表）

三个接口的错误状态**恰好五值**，不得新造状态机：

| 状态 | 含义 | 典型触发 |
|---|---|---|
| `not_found` | 请求对象在**已索引集合之外**（含未注册 root、越界 locator） | A02 R2 |
| `not_indexed` | 路径存在但尚未进入索引 | L09 本地导入 provenance |
| `unavailable` | 曾经可用、当前无任何**合格**副本（含全失效、被撤、云占位不可读） | L03/L06 |
| `blocked` | 被策略/授权/质量门拒绝（含 `privacy_class` 拒绝、来源不明） | L10/L11 |
| `ambiguous` | 存在多个候选而**规则无法判定**（真实修订 vs 同 hash 副本关系未知） | L07 原文用词 |

每值附**人类可读 reason**；**重试性 / 预算 / 超时是独立字段，不是状态**。落不进这五值的 = **合同缺口**，须登记而非新增状态。

> **完整性对账（v0.2）**：47 个叶子命令 = **§2.1 的 15 个**（`query`、`evidence`、`evidence-list`、`sections-list`、`size-report`、`status`、`duplicates`、`startup-status`、`runtime-policy show`、`identity-enrichment preview`、`activation preview`、`extraction-quality`、`duplicate-preview`、`resolve`、`identify`）**+ §2.2 的 32 个**（W 14 + N 2 + X-local 3 + D 2 + S 11）＝ **47** ✓。
> 面积基线：AST `add_parser` 47 处，其中 `cli.py:579`（`add_worker_control_parser` 内）复用 5 次；实测 `--help` 探针 41 顶层 + 10 嵌套 = 51 个解析器节点，减去 4 个纯分组解析器（`documents:255`、`identity-enrichment:272`、`activation:634`、`runtime-policy:664`）= **47**。v0.1 漏列的 7 个（`worker-status/start/resume/pause/stop`、`derived-audit`、`import-portfolio`）已全部落位；`identify --refresh` 与 `activation preview`/`activation apply`/`activation rollback` 按 flag/子命令分轴，不额外计入叶子数。

## 3. 副作用表（每接口必填字段，执行时逐条填）

> **v0.4.1（A-VR-07）：本节不再是空模板——下表给出 §2.1 五个 R 叶子的静态初值**（由本轮静态判读得到；标 `TO-VERIFY` 的字段须在隔离副本上实测确认）。**未填的接口不得被读作"副作用已登记"。**

| 接口 / 命令 | entrypoint | read_set | write_set | network_destinations | subprocesses | 待实测 |
|---|---|---|---|---|---|---|
| `query` | `cli.py` → `get_catalog().query` → `reader.py` | catalog.sqlite3（`mode=ro`+`query_only`） | ∅ | ∅ | ∅ | 无（机制层已闭合） |
| `evidence` / `evidence-list` | 同上（reader） | 同上 | ∅ | ∅ | ∅ | 输出上限行为 |
| `sections-list` | 同上（reader） | 同上 + sections 派生表 | ∅ | ∅ | ∅ | 无 |
| `status` | 同上（reader；`reader.py:132` 返回 schema/health） | 同上 | ∅ | ∅ | ∅ | 无 |
| `duplicates` ✱ | `cli.py:1043` 构造 **可写** `CatalogStore` | catalog.sqlite3（RW 连接） | **catalog.sqlite3 的 DDL/迁移/commit**（无业务行写入） | ∅ | ∅ | 迁移是否在只读副本上可跳过（TO-VERIFY） |
| 其余 R 叶子（`size-report`/`startup-status`/`runtime-policy show`/`resolve` etc.） | 见 §2.1 | catalog.sqlite3 或 policy 快照 | ∅（`resolve` 额外输出 policy_export **快照文本**，不落盘） | ∅（`resolve` 不触网） | ∅ | `resolve` 的 payload 字节契约（B02/B04 必测） |

**每接口在真实执行时仍须逐条补全的字段**（handbook §3）：

```
interface: query_local | open_version | request_work
entrypoint: <python 绝对路径 + 模块/函数>
argv: [...]            cwd: <绝对路径>
env_keys: [...]        （秘密值不落盘）
read_set: [...]        write_set: [...]
network_destinations: [...]   budget: <bytes/tokens/费用>   timeout: <s>
subprocesses: [...]    exit_expectation: <五值状态之一 + rc>
evidence_path: <run 目录相对路径>
independent_approval: <reviewer/时间>
```

## 4. 交给 A.DR / VR 的问题（v0.4.1 状态）

1. `duplicate-preview` 的 token → **静态已答**：不落盘（`duplicate_cleanup.py:361/392-396`）→ 归 R（受 ✱ 进程级副作用约束）。
2. `activation preview` 的只读性 → 叶子 help 自述只读，但**会建库/迁移**；须 VR **行为**证明（VR-N22）。
3. `resolve` → **静态已答**：只读 + 网络 ∅ + 子进程 ∅；**但会输出 policy_export 快照（跨仓契约产物）**，B02/B04 必须保其字节/hash 契约。
4. `latest` 的"已索引集合"边界：是否排除"已 retire 但文件仍在"的文档（与 A04 交叉）→ **仍未答**，留 VR。
5. `identify` 默认形式是否写 identity cache → **静态已答**：不写（`security_identity.py:308-311/418-433`）。
6. `extraction-quality` 是否归 R → **静态已答**：只读（`extraction_quality.py:263-270`）。
7. **【v0.4.1 新增】`preview` 的合同归属**（A-VR-04）：A03 §1 只定义 `query_local`/`open_version`/`request_work`，**本仓没有顶层 `preview` 命令**，而正式分析/LLM 的许可门实际在**消费者仓**（`revenue-forecast/scripts/company_wiki_source.py:280-281`：`capture_ready is not True → raise`）→ 本契约**不声称已定义 preview**；preview 合同责任划给 **B06**（`preview` vs `verified_input` 资格标签），A 阶段无 preview 合同。

## 5. 边界

- 本文件是设计草案：**除 §2 记载的 52 次 `--help` 探针（owner 批准范围）外，未运行任何 CLI**、未改产品代码/配置；映射为暂定，VR 复核前不得据此执行。**v0.3.1 更正（A-DR3-04）**：v0.2 的"未运行任何 CLI"与 §2 的探针记录自相矛盾，现限定范围。
