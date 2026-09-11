# A03 operation-contract —— query_local / open_version / request_work（v0.1 草案）

> 阶段 A · 步骤 A03 · 只读产出 · 状态：**草案，待 A.DR**。分类为**暂定**：子命令的 `--help` 未运行（按 handbook §2.5/§2.8 需 command-manifest 批准），本表依据 `cli.py` 解析器 help 文本与代码判读，**VR 必须逐条复核**。

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

### 2.1 可支撑 `query_local`（R，暂定）

| 命令 | help 摘要 | 备注 |
|---|---|---|
| `identify` | resolve a company name, alias, or ticker to one verified listed security | 纯身份解析 |
| `query` | query catalog metadata and artifact paths | 纯查询 |
| `evidence` / `evidence-list` | 按 source ID + locator 查单条 / 列有界证据 | 纯查询 |
| `sections-list` | 列出已抽取章节 | 纯查询 |
| `size-report` | read-only catalog size / disk-health report | 自述只读 |
| `extraction-quality` | assess quality without span bodies | 自述只读 |
| `status` | show catalog counts | 纯查询 |
| `duplicates` | list exact-copy groups and protected canonical locations | 纯查询 |
| `startup-status` | show Windows logon task status | 只读（系统面） |
| `runtime-policy show` | load and print the current snapshot（absent 时 fail closed） | 只读 |
| `identity-enrichment preview` | read-only: which assertions would flip | 自述只读 |
| `activation preview` | preview（FC-203） | 待 VR 确认是否纯读 |
| `duplicate-preview` | revalidate one noncanonical exact-copy and **issue a confirmation token** | **待确认**：是否写 token/状态 |
| `resolve` | resolve an existing source **before any downloader is considered** | 设计上属"查询+复用"；VR 需确认无隐式下载 |

### 2.2 必须归入 `request_work` 或更高授权（非查询）

| 类别 | 命令 |
|---|---|
| **W 本地写** | `scan`、`normalize`、`summarize`、`fingerprint-backfill`、`extract-sections`、`retire`、`restore`、`verify`、`reject`、`reconcile-retire`（dry-run 默认）、`focus-cleanup`（dry-run 或 apply）、`run`（scan→normalize→summarize→export） |
| **N 网络/provider** | `ensure`（`--allow-download` + worker paused 审计双闸）、`close-gap` |
| **X 外发/导出** | `export`、`policy-export`、`archive-retired-evidence` |
| **D 破坏性** | `prune-retired-evidence`（**物理删除**，dry-run 默认；与 H01 风险同一片区域）、`duplicate-recycle`（移入回收站，需确认 token） |
| **S 系统/后台** | `worker`（后台批处理）、`install-startup` / `uninstall-startup`（Windows 登录任务）、`activation apply/rollback`、`runtime-policy apply` |

### 2.3 待 VR 明确的两处高风险映射

1. **`resolve` 是否绝对无网络/无写**：文档说"before any downloader is considered"，但它是 filing/revenue 跨仓链的第一跳（见 [baseline-map.md](baseline-map.md) §1 ②）；VR 需在隔离副本中用真实命令证明它不写 catalog、不触网。
2. **`summarize` 与 LLM 出口的关系**：`summarize` 自述"deterministic source-only"，而 LLM 摘要经 `llm_summarizer`（受 `privacy_class` + review receipt 门控）；VR 需确认 `summarize`/`run`/`worker` 三条路径中哪条可能到达 LLM，并把它归入 **X** 而不是 **W**。

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

## 4. 交给 A.DR / VR 的问题

1. `duplicate-preview` 的 confirmation token 是否构成写？决定它属 R 还是 W。
2. `activation preview` 的只读性（help 未自述只读）。
3. `resolve` 的"无网络/无写"是否要求 VR 用真实命令证明（而非代码判读）。
4. `latest` 的"已索引集合"边界：是否需要显式排除"已 retire 但文件仍在"的文档（与 A04 身份契约交叉）。

## 5. 边界

- 本文件是设计草案：**未运行任何 CLI**、未改产品代码/配置；映射为暂定，VR 复核前不得据此执行。
