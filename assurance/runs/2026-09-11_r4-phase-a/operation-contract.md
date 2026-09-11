# A03 operation-contract —— query_local / open_version / request_work（v0.3.1 草案，已按 A.DR rev1/rev2/rev3 更正）

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

| 命令 | help 摘要（实测） | 备注 |
|---|---|---|
| `query` | query catalog metadata and artifact paths | 纯查询 |
| `evidence` / `evidence-list` | 按 source ID + locator 查单条 / 列有界证据 | 纯查询 |
| `sections-list` | list extracted MD&A / business sections for one document | 纯查询 |
| `size-report` | read-only catalog size / disk-health report | help 自述只读 |
| `status` | show catalog counts | 纯查询 |
| `duplicates` | list exact-copy groups and protected canonical locations | 纯查询 |
| `startup-status` | show Windows logon task status | 只读（系统面） |
| `runtime-policy show` | load and print the current snapshot（absent 时 fail closed） | 只读 |
| `identity-enrichment preview` | preview a candidate assertion **without writing**（`cli.py:277`） | help 自述不写 |
| `activation preview` | preview（`cli.py:634-637` 分组 help "preview/apply/rollback cohort-epoch activation (FC-203)"；叶子 help 见 `:639-641`） | **自述只读**（叶子 help 原文 "read-only: which assertions would flip"），但**未自述具体读写集合** → 待 VR 行为证明（见 §2.3 第 4 条、§4 问题 2）。**v0.3 更正（A-DR2-07）**：v0.2 此行残留"只读性未自述"，与本文件 §2.3/§4 自相矛盾，已按叶子 help 原文改写 |
| `extraction-quality` | assess deterministic source/extraction quality **without span bodies**（`cli.py:366`） | "无 span 正文"≠"只读"，**不标只读** |
| `duplicate-preview` | revalidate one noncanonical exact-copy and **issue a confirmation token** | **待确认**：token 是否落盘 |
| `resolve` | resolve an existing source **before any downloader is considered** | 设计上属"查询+复用"；VR 需证明无隐式下载 |
| **`identify`（flag 条件）** | resolve a company name/alias/ticker | **默认只读；`--refresh` = 网络 + 本地写**（更正 1）→ 该 flag 属 **N+W**，不得置于 `query_local` 之后 |

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

### 2.3 高风险映射（v0.2：一条已就地定性，三条仍需 VR；两处已静态收窄）

1. **`identify` 的 flag 分裂（新增，A-DR-04 要求登记）**：本契约规则 R3 点名的正是"隐藏的 `ensure`/`refresh` 路径"这一类。实测 `cli.py:1080-1087`：`args.refresh` 为真时先构造 `OfficialSecurityMasterRefresher(store).refresh(markets=…)`，而 `security_identity.py:20` 引入 `requests`、`:26-45` 定义 https 端点、`:1007` `requests.get`、`:348` `write_text`、`:1047` `def refresh`。→ **`identify` 默认（无 `--refresh`）可留在 R（待 VR 实测确认）；`identify --refresh` 同时是 N（网络）+ W（本地写），必须走 `request_work` 或更高授权，且不得被 `query_local`/`open_version` 间接触达。** VR 的验证脚本必须**只**用无 `--refresh` 形式（与 A04 V5 同一约束）。
2. **`resolve` 是否绝对无网络/无写——静态部分已收窄（v0.2）**：`cli.py:1165-1200` 该分支经 `self.reader`/`SourceCatalog.query_filing_candidates` 与 `self.query` 读取，二者只碰读模型；分支内无 `subprocess`、无网络调用。→ **机制层面已判读为"纯读"**；VR 只需在隔离副本上做**边界确认**（证明不写 catalog、不触网），不再作为"机制未知"的开放项。它是 filing/revenue 跨仓链的第一跳（见 [baseline-map.md](baseline-map.md) §1 ②），所以该确认仍必须有。
3. **`summarize` 与 LLM 出口的关系**：`summarize` 自述 "deterministic source-only"，而 LLM 摘要经 `llm_summarizer`（受 `privacy_class` + review receipt 门控）；VR 需确认 `summarize`/`run`/`worker` 三条路径中哪条可能到达 LLM，并把它归入 **X-egress** 而不是 **W**。
4. **`activation preview` 的只读性**：help 文本（`cli.py:639`）为 "read-only: which assertions would flip"——**自述只读**；但 `activation apply/rollback` 已归 **S**，`preview` 是否真的只读仍待 VR 用行为证明。
5. **`duplicate-preview` 的 confirmation token 是否落盘**：决定它属 R 还是 W（§4 问题 1）。

> **完整性对账（v0.2）**：47 个叶子命令 = **§2.1 的 15 个**（`query`、`evidence`、`evidence-list`、`sections-list`、`size-report`、`status`、`duplicates`、`startup-status`、`runtime-policy show`、`identity-enrichment preview`、`activation preview`、`extraction-quality`、`duplicate-preview`、`resolve`、`identify`）**+ §2.2 的 32 个**（W 14 + N 2 + X-local 3 + D 2 + S 11）＝ **47** ✓。
> 面积基线：AST `add_parser` 47 处，其中 `cli.py:579`（`add_worker_control_parser` 内）复用 5 次；实测 `--help` 探针 41 顶层 + 10 嵌套 = 51 个解析器节点，减去 4 个纯分组解析器（`documents:255`、`identity-enrichment:272`、`activation:634`、`runtime-policy:664`）= **47**。v0.1 漏列的 7 个（`worker-status/start/resume/pause/stop`、`derived-audit`、`import-portfolio`）已全部落位；`identify --refresh` 与 `activation preview`/`activation apply`/`activation rollback` 按 flag/子命令分轴，不额外计入叶子数。

## 3. 副作用表（每接口必填字段，执行时逐条填）

```
interface: query_local | open_version | request_work
entrypoint: <python 绝对路径 + 模块/函数>
argv: [...]            cwd: <绝对路径>
env_keys: [...]        （秘密值不落盘）
read_set: [...]        write_set: [...]
network_destinations: [...]   budget: <bytes/tokens/费用>   timeout: <s>
subprocesses: [...]    exit_expectation: <code + 业务状态>
evidence_path: <run 目录相对路径>
independent_approval: <reviewer/时间>
```

## 4. 交给 A.DR / VR 的问题（v0.2）

1. `duplicate-preview` 的 confirmation token 是否构成写？决定它属 R 还是 W。
2. `activation preview` 的只读性（help 自述 "read-only: which assertions would flip"，但未自述到具体读写集合）。
3. `resolve` 已由代码判读定性为纯读（§2.3 第 2 条）；**是否同意**把 VR 的范围收窄为"隔离副本上的边界确认"（不写 catalog、不触网），而不再作为机制开放项？
4. `latest` 的"已索引集合"边界：是否需要显式排除"已 retire 但文件仍在"的文档（与 A04 身份契约交叉）。
5. `identify` 默认形式（无 `--refresh`）是否确实不写 identity cache？（`--identity-cache-dir` 的存在提示缓存可能落盘；这是 §2.1 中 `identify` 保住 R 的前提。）
6. `extraction-quality` 既不属"help 自述只读"，其写入集合也未在 help 中说明；是否同意其归 R 需要 VR 实测（而非按名称推断）？

## 5. 边界

- 本文件是设计草案：**除 §2 记载的 52 次 `--help` 探针（owner 批准范围）外，未运行任何 CLI**、未改产品代码/配置；映射为暂定，VR 复核前不得据此执行。**v0.3.1 更正（A-DR3-04）**：v0.2 的"未运行任何 CLI"与 §2 的探针记录自相矛盾，现限定范围。
