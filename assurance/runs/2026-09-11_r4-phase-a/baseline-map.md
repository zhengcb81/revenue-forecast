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

## 1. 主链：query → identify → resolve → open → 消费

| 跳 | 入口（实测） | 进程形态 | 读写性质（代码判读） |
|---|---|---|---|
| ① query/identify | wiki `cli.py` 子命令 `identify`（共 **47** 个子命令） | 同进程 | 只读：解析请求→身份/路由，不落盘 |
| ② resolve（复用） | wiki `cli.py::resolve` → `service.py` → `resolver.py` | 同进程 | 只读：在已索引集合上返回 handle（`resolver.py` 内 `is_canonical` 2 处、`reusable_root_kinds` 3 处、`priority` 1 处分支） |
| ③ ensure（下载，显式） | wiki `cli.py::ensure` | 同进程 + 可能 fork 子进程 | **写**：仅显式 `--allow-download` 且 worker 非 paused（`_append_paused_acquisition_audit` 记审计） |
| ④ open/读取 | wiki `cli.py::query`/`preview`/`documents`/`export` 等 | 同进程 | 只读（`preview` 允许不扩大正式分析/LLM 许可——A03/A07 要冻结此边界） |
| ⑤ 消费（跨仓） | **filing**：`scripts/fetch_filing.py::_run_company_wiki_json`（L199–213，`subprocess.run` + Windows `CREATE_NO_WINDOW`）→ 调 wiki CLI；**revenue**：`scripts/source_preparation.py`（L3–4 注释即"真实跨仓链：filing-fetch (resolve/ensure) → company-wiki catalog"，`subprocess` L18）+ `scripts/company_wiki_source.py`（经 `filing_fetch_client.resolve_filing`） | **子进程** | 取决于所选子命令；resolve 路线只读、ensure 路线写 |

**子进程清单（A01 实测到的跨仓 spawn 点）**：filing `fetch_filing.py` L213 `subprocess.run`（→wiki CLI）；revenue `source_preparation.py`（filing-fetch → wiki catalog 两段）；wiki 侧 `ensure` 内部按 provider 起子进程；`scripts/legacy_observer.py`（观测，非本链）；revenue `tools/daily_t2_runner.py`（调度，非本链）。

## 2. root 分支与副作用面

- 生产 config `source_catalog.yaml`：`privacy_class` 全为 **public**；`kind` 出现 `company_raw` / `dayu_portfolio` / `directory`（四 root 的 `future_lake` 与 `dropbox_stock` 在 9/7 快照中分别以 `directory` kind + `future_lake` 根名存在，A02 要冻结等价）。
- `resolver.py` 的可复用判定链：`reusable_root_kinds` → `is_canonical` → `priority`（顺序即语义，A02 冻结）。
- **迁移期分支**：`legacy_bridge_allowed` 在 `resolver.py` 出现 **10 处**——属 R9 批 3 的删除对象（bridge 关闭后无实际流量），A 阶段只需**记录**，不动。

## 3. 自 9/7 诊断以来的"已变更"标记（绝不复原旧 bug）

| 变更 | 事实 |
|---|---|
| R9 批 1+2 已删 | revenue 4 工具 + 5 测试 + quality.yml 重接线（`289fb6b`，2026-09-06） |
| 调度修复 | `2ff20d9`（`--run-daily`）、`56ba0eb`/`b049165`（`safe.directory`、SYSTEM 路径）、`c701f6d/3ea24b7/e9a6071`（22:00 触发 + 电源条件） |
| 观测语义修复 | wiki `25a8eea`（sample pass 走生产快照门）、`623e831`（列表式章节标题） |
| **2026-09-10/11 新增** | revenue `41117ce`（FC-705 窗口补足 24h）、`e957d94`（停止跟踪运行指针）、agent 层无产品改动 |
| 诊断行号 | 9/7 诊断文档的行号**只是定位线索**（handbook §2.3），本映射以**符号**为准 |

## 4. 本步未覆盖（如实声明）

1. **47 个子命令的逐条副作用矩阵**未做——需要 run 每个 `--help`/`--dry-run`，属**执行动作**，等 command-manifest 批准（handbook §2.5/§2.8）。
2. **真实语料选取与基线 trace**（A05/A06）需 owner 的**精确数据读取许可**；本步未读任何真实报表正文。
3. **错误状态码全集**（A06 冻结对象）未整理。
4. 上表哈希为**工作树当前字节**；A02 冻结前若发生并发提交需重算（handbook §2.3：并发漂移则重审受影响部分）。
