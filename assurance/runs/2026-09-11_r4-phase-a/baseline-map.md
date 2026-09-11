# R4 A01 基线映射（baseline-map）

> 阶段：**A（统一合同与真实基线）** · 步骤：**A01 重核三仓当前代码/配置**
> 运行目录：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-a/`（**不写回审计证据目录**，符合 handbook §2.5 / §3）
> 状态：**只读**。本轮**未执行任何 CLI**（连 `--help` 也留到 command-manifest 批准后，handbook §2.8），**未改产品代码/配置/DB/任务**。

## 0. 输入冻结（2026-09-11 21:xx 本地实测）

| 仓 | HEAD | 工作树 |
|---|---|---|
| company-wiki | `7d4852f` | 干净 |
| revenue-forecast | `4c8bc27` | 仅运行指针未跟踪（`daily_manifest.json` 已停跟踪；`assurance/runs/<UTC>/` 已被 .gitignore 覆盖） |
| filing-fetch | `b44edd8` | 干净 |

**候选定位文件哈希（A01 输入，sha256 前 16 位 / 字节）**

| 文件 | sha256(16) | bytes |
|---|---|---|
| wiki `config/source_catalog.yaml` | `f9eb72a6c37c2dfe` | 1712 |
| wiki `src/company_wiki/source_catalog/resolver.py` | `6962b258ce198f19` | 56769 |
| wiki `src/company_wiki/source_catalog/service.py` | `6412b19e8e9a3073` | 55519 |
| wiki `src/company_wiki/source_catalog/policy.py` | `78320c429e4b7bc9` | 3384 |
| wiki `src/company_wiki/source_catalog/scanner.py` | `c2ada3e26a53b535` | 62894 |
| wiki `src/company_wiki/source_catalog/cli.py` | `2f5c574034369707` | 65553 |
| wiki `src/company_wiki/source_catalog/config.py` | `e96cea75cb27bcf6` | 9744 |
| wiki `src/company_wiki/source_catalog/models.py` | `fc6cc009fb22f6d6` | 10292 |
| filing `scripts/fetch_filing.py` | `046cc7dc4e3ff2f4` | 48392 |
| filing `scripts/filing_contracts.py` | `2d1b2e3374f1d0c2` | 22631 |
| revenue `scripts/company_wiki_source.py` | `aeeb7b2a63047c73` | 14377 |
| revenue `scripts/source_preparation.py` | `5ec16eaf0fe48012` | 9605 |

> wiki `src/company_wiki/source_catalog/` 现有 **86 个 .py**；`reader.py` 存在。

> **v0.2 补记（A-DR-09：HEAD/工作树再冻结）**：上表是 **A01 时刻**（21:0x）的实测值。A02–A04 的文档与 run 目录本身随后被提交，revenue HEAD 因此前移：`4c8bc276…`（A01）→ **`b644e167b299965812eee3a6013727d4cd76bf57`**（本文件 A02–A04 提交后，工作树**干净**）。`4c8bc27..b644e16` 只含 run 目录的 4 个提交、**不含任何产品文件**，故 §0 的 12 个输入哈希在提交后**仍逐字节成立**（A.DR 已独立复核）。checkpoint.json 的 `revenue_head`/`revenue_dirty` 已按本注记重冻结。
> **v0.2 补记（A-DR-08：边界声明收窄）**：§0 的"干净"仅指 **git 工作树**；它**不**覆盖 `.source_catalog` 等被 ignore 的运行时状态。实测该目录下 `catalog.sqlite3-shm` 在本 run 期间（21:18:15）有过写入、且 21:26:47 再次出现，**归属未知**；v0.1 的"未触碰 DB"式表述不得被读作"期间无任何连接"。证据与实验见 [boundary-audit.md](boundary-audit.md)。
> **v0.2 更正（A-DR-15 / A-DR-02）**：§1 表 ②③ 行的机制描述与 §2 的复用链表述见就地更正。

## 1. 主链：query → identify → resolve → open → 消费

| 跳 | 入口（实测） | 进程形态 | 读写性质（代码判读） |
|---|---|---|---|
| ① query/identify | wiki `cli.py` 子命令 `identify`（面积为 §4：41 顶层 + 10 嵌套 = 51 个解析器节点，其中 4 个是纯分组 → **47 个叶子命令**） | 同进程 | 只读：解析请求→身份/路由，不落盘。**例外**：`identify --refresh` 触网+写（`cli.py:1080-1087`、`security_identity.py:1007/:348`）——见 A03 更正 1 |
| ② resolve（复用） | wiki `cli.py::resolve` → `service.py` → `resolver.py` | 同进程 | 只读：在已索引集合上返回 handle（`resolver.py` 内 `is_canonical` 2 处 `:915/:1157`；复用判定读 `root.kind` ∈ `reusable_root_kinds`，`resolver.py:782-786`/`:933-940`）。**v0.2 更正（A-DR-02）**：v0.1 写的"`priority` 1 处分支"**是错的**——`resolver.py` 内 `priority` 仅 1 处命中且位于**字符串字面量** `:531`；真正的优先级排序在 **SQL**：`service.py:329`/`:527`，以及 `service.py:643-653` 的 canonical 选择键 `(root_priority, root_id, relative_path, location_id)` |
| ③ ensure（下载，显式） | wiki `cli.py::ensure` | 同进程 + 可能 fork 子进程 | **三道闸（v0.2 按 `cli.py:742-824` 重述，A-DR-15）**：① 无 `--allow-download` 且 mode≠`latest_as_of` → `:752-758` **纯读**返回 resolve 结果；② 有 `--allow-download` 或 `latest_as_of` → 写流程（`:760-762` 先取 `get_catalog().store`，**写入器初始化可能先建 catalog**）；③ worker `desired_state=="paused"` 时 `:764-771` **RuntimeError 拒绝**下载，**除非**显式 `--allow-acquisition-while-paused`；**被该 flag 放行时才** `:772-778` 记暂停期审计（`_append_paused_acquisition_audit` → 追加 `catalog_dir/paused_acquisition.log`，`:109`；best-effort，失败只 warn 不阻断）。v0.1 把审计写成"worker 非 paused 时记录"，**方向写反了** |
| ④ open/读取 | wiki `cli.py::query`/`preview`/`documents`/`export` 等 | 同进程 | 只读（`preview` 允许不扩大正式分析/LLM 许可——A03/A07 要冻结此边界） |
| ⑤ 消费（跨仓） | **filing**：`scripts/fetch_filing.py::_run_company_wiki_json`（L199–213，`subprocess.run` + Windows `CREATE_NO_WINDOW`）→ 调 wiki CLI；**revenue**：`scripts/source_preparation.py`（L3–4 注释即"真实跨仓链：filing-fetch (resolve/ensure) → company-wiki catalog"，`subprocess` L18、`subprocess.run` L99） | **子进程** | 取决于所选子命令；resolve 路线只读、ensure 路线写 |

### 1.1 子进程清单（v0.2 **逐模块重建**，A-DR-06）

> v0.1 的 wiki 侧只有一句"`ensure` 内部按 provider 起子进程"，**严重低估**。实测 `company-wiki/src` 全树 grep `subprocess\.|Popen|os\.system|CREATE_NO_WINDOW` 命中 **7 个模块、12 个真实 spawn 调用点**：

| 模块 | spawn 点 | 被执行体 | 性质 / 边界 |
|---|---|---|---|
| `adapter_process.py` | `:137` `subprocess.run`（`creationflags` `:135`） | `self.command`（**配置驱动的适配器 CLI**），JSON 经 stdin，`cwd=project_root` | **外部 provider 子进程**；A02/A03 的 R 类接口必须证明不触达 |
| `dayu_cli_adapter.py` | `:192` `subprocess.Popen`（`:188` flags；`:197-198` PIPE） | **dayu CLI**（`--base/--config/--quiet`；注释自述等待 Docling/RapidOCR 后处理） | **外部 provider CLI + 网络边界**：这是 v0.1 完全漏掉的"网络出口"之一 |
| `control.py` | `:91` `subprocess.run` | `powershell.exe -NoProfile -Command Get-CimInstance Win32_Process …`（`:81-90` 脚本） | 系统面**只读**进程枚举 |
| `control.py` | `:1127` `self.popen(...)`（`:651` 默认 `subprocess.Popen`；`:1131` `DEVNULL`） | **worker 启动**（`-File` 脚本；`:1119` `CREATE_NO_WINDOW`） | **S 类**：后台进程启动 → `worker-start/resume` 一路 |
| `lock.py` | `:85` `subprocess.run`（`:101` flags） | `powershell.exe -ExecutionPolicy Bypass -Command Get-CimInstance …CreationDate` | 系统面**只读**（PID 复用防护） |
| `normalizer.py` | `:286` `subprocess.run` | **`taskkill.exe /PID <pid> /T /F`** | **本机破坏性动作**（强杀进程树）——`normalize` 不是纯 W，含 D 语义，A03 需补注 |
| `normalizer.py` | `:1261` `subprocess.run` | **`antiword <path>`**（`.doc` → markdown） | 外部可执行体（本地转换） |
| `startup.py` | `:107`/`:124`/`:176`/`:212`（默认参数 `runner=subprocess.run`） | **`schtasks.exe`**（计划任务安装/卸载/查询；`:100` 附近 `/F`） | **S 类**：Windows 登录任务 |
| `worker.py` | `:110` `subprocess.run` | `git -C <root> rev-parse --short HEAD` | 只读（代码版本戳） |

跨仓 spawn（前表 ⑤）：filing `fetch_filing.py:213`、revenue `source_preparation.py:99`。
**另有两处非本链调度/观测**：`revenue/scripts/legacy_observer.py`、`revenue/tools/daily_t2_runner.py`（声明不在 A 阶段主链上）。

## 2. root 分支与副作用面

- 生产 config `source_catalog.yaml`：`privacy_class` 全为 **public**；`kind` 出现 `company_raw` / `dayu_portfolio` / `directory`（四 root 的 `future_lake` 与 `dropbox_stock` 在 9/7 快照中分别以 `directory` kind + `future_lake` 根名存在，A02 要冻结等价）。
- **v0.2 更正（A-DR-02）**：v0.1 写的"`resolver.py` 的可复用判定链：`reusable_root_kinds` → `is_canonical` → `priority`"**不成立**。真实判定：复用只看 **`root.kind ∈ reusable_root_kinds`**（`resolver.py:782-786` 构造可复用 root 集合、`:933-940` 在 canonical locations 上测试 `root_id` 是否属于该集合），**从不读 `reusable_for_filing`**（显式 `false` 无法关闭复用 = fail-open）；`is_canonical` 是**位置代表权**（由 `service.py:643-653` 决定，非复用判定）；`priority` 不参与复用判定，只参与位置排序。详见 [root-contract.md](root-contract.md) 更正 2 与 R8。
- **迁移期分支**：`legacy_bridge_allowed` 在 `resolver.py` 出现 **10 处**——属 R9 批 3 的删除对象（bridge 关闭后无实际流量），A 阶段只需**记录**，不动。

## 3. 自 9/7 诊断以来的"已变更"标记（绝不复原旧 bug）

| 变更 | 事实 |
|---|---|
| R9 批 1+2 已删 | revenue 4 工具 + 5 测试 + quality.yml 重接线（`289fb6b`，2026-09-06） |
| 调度修复 | `2ff20d9`（`--run-daily`）、`56ba0eb`/`b049165`（`safe.directory`、SYSTEM 路径）、`c701f6d/3ea24b7/e9a6071`（22:00 触发 + 电源条件） |
| 观测语义修复 | wiki `25a8eea`（sample pass 走生产快照门）、`623e831`（列表式章节标题） |
| **2026-09-10/11 新增** | revenue `41117ce`（FC-705 窗口补足 24h）、`e957d94`（停止跟踪运行指针）、agent 层无产品改动 |
| 诊断行号 | 9/7 诊断文档的行号**只是定位线索**（handbook §2.3），本映射以**符号**为准 |

## 4. CLI 表面积（2026-09-11 **已由真实解析器确认**，owner 批准的 `--help` command-manifest）

| 项 | 值 |
|---|---|
| 探针 | **52 次 `python -B -m company_wiki.source_catalog.cli <cmd> [sub] --help`**，全部 rc=0 |
| **顶层命令 41 个** | scan, normalize, summarize, fingerprint-backfill, extract-sections, export, policy-export, derived-audit, status, focus-cleanup, documents, identity-enrichment, identify, query, evidence, evidence-list, sections-list, reconcile-retire, archive-retired-evidence, prune-retired-evidence, size-report, extraction-quality, duplicates, duplicate-preview, duplicate-recycle, resolve, ensure, close-gap, import-portfolio, run, worker, worker-status, worker-start, worker-resume, worker-pause, worker-stop, install-startup, uninstall-startup, startup-status, activation, runtime-policy |
| **嵌套 10 个** | `documents {retire,restore}`、`identity-enrichment {preview,verify,reject}`、`activation {preview,apply,rollback}`、`runtime-policy {show,apply}` |
| **零副作用（前后快照比对）** | `catalog.sqlite3` 未变、`config/source_catalog.yaml` 未变、`__pycache__` 未变、git dirty 行数未变 —— **全部 true** |
| 证据 | [evidence/cli-help-matrix.json](evidence/cli-help-matrix.json)、[command-manifest.json](command-manifest.json)、执行器 [evidence/run_cli_help_matrix.py](evidence/run_cli_help_matrix.py) |

> **更正（如实）**：§0/§1 早先写的"47 个子命令"来自**源码 grep**；真实解析器给出的是 **41 顶层 + 10 嵌套 = 51 个命令**。以本表为准。

## 5. 本步未覆盖（如实声明）

1. ~~逐条副作用矩阵未做~~ → **已完成**：51 个命令的 `--help` 探针（§4），零副作用已由前后快照证明。**仍未做**：`--dry-run` 行为探针（会打开生产 catalog，属数据读取动作，留 A06/VR 在隔离副本上做）。
2. **真实语料选取与基线 trace**（A05/A06）需 owner 的**精确数据读取许可**（2026-09-11 已获原则批准，具体样本清单待 A05 提交后逐项确认）；本步未读任何真实报表正文。
3. **错误状态码全集**（A06 冻结对象）未整理。
4. 上表哈希为**工作树当前字节**；A02 冻结前若发生并发提交需重算（handbook §2.3：并发漂移则重审受影响部分）。**已执行（v0.2）**：run 目录 4 个提交后 12 个输入哈希仍逐字节一致（A.DR 独立复核 12/12 HASH_OK）。
5. **子进程逐条副作用矩阵**：v0.2 已补 §1.1 的 **7 模块 / 12 spawn 点**静态清单；**仍未做**的是"每条 spawn 在真实执行时的实际 argv/写入集合"（属 A06/VR，需隔离副本）。
