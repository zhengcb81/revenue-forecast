# R4 Phase A 发现（findings）

> **v0.2 更正（2026-09-11，回应 A.DR rejected）**：F-A01-2 的引用**已改写**（删除了两处 docstring 引用，A-DR-06）；F-A01-3/F-A01-6 的"47"表述已按真实解析器更正为 **51 节点 / 47 叶子**；新增 **F-A01-8**（catalog `-shm` 边界观测，A-DR-08）与 **F-A01-9**（A.DR 复审结论记录）。

## F-A01-1：A 阶段的设计准入本身需要"精确 DEV/数据读取许可"，当前授权只够只读映射

- 证据：执行计划 §2 表格——「A 合同与真实基线 | 设计准入 = 文档完成后，**未来精确DEV/数据读取许可**」；handbook §2.5「首次实施前用户须批准 DEV 精确工作包及文件范围」。
- 影响：A01（读代码/配置）可在只读范围内先做；**A05/A06（真实语料、基线 trace）必须等精确数据读取许可**，A02–A04 的合同设计可在 A01 收口后提交 A.DR。
- 处置：本 run 只做只读映射，不越门。
- **状态更新（2026-09-11）**：owner 已批准 **A 阶段精确 DEV/数据读取许可** + `--help`-only command manifest + VR reviewer 指派。该批准**不**含产品写入、真实命令执行（`--help` 之外）、网络、删除、worker 恢复。

## F-A01-2：跨仓主链是"子进程级联"，不是进程内调用

- 证据（**v0.2 仅保留符号级可核实引用**）：filing `scripts/fetch_filing.py:199` `_run_company_wiki_json` → `:209` `creationflags = subprocess.CREATE_NO_WINDOW` → `:213` `subprocess.run`（调 wiki CLI）；revenue `scripts/source_preparation.py:18` `import subprocess` → `:99` `subprocess.run`（`L3-5` 为模块 docstring 中的链路说明，**不作为证据**）。
- **已删除的错误引用**（A-DR-06）：v0.1 引用的 revenue `scripts/company_wiki_source.py:12/261`（`filing_fetch_client.resolve_filing`）**是 docstring 文本，不是代码**——该文件内 `subprocess`/`filing_fetch_client` 命中全部落在 docstring（模块 docstring L1-14、函数 docstring L259-267），**无 import、无调用**。引用与 handbook §2.3"以符号为准"的要求相抵触，故删除。
- 影响：A03 的"副作用表"必须**按子进程边界**给（解释器路径/cwd/argv/env/读写集合/网络/预算/timeout），不能只按函数调用描述；VR 的隔离测试也要在子进程层观测。
- **范围更正**：级联**不止跨仓两处**——wiki 侧自身另有 **7 模块 / 12 个 spawn 点**（见 [baseline-map.md](baseline-map.md) §1.1），其中 `dayu_cli_adapter.py:192` 与 `adapter_process.py:137` 是**外部 provider 边界**。

## F-A01-3：wiki CLI 面很大（**51 个解析器节点 / 47 个叶子命令**），其中既有只读也有写

- 证据（v0.2 更正，"47 个子命令"的旧表述有歧义）：`cli.py` 解析器实测 **41 顶层 + 10 嵌套 = 51 个节点**，其中 4 个是纯分组（`documents`/`identity-enrichment`/`activation`/`runtime-policy`）→ **47 个叶子命令**。含只读面（`query/evidence/evidence-list/sections-list/status/duplicates/size-report/startup-status`）与写/外部/系统面（`scan/normalize/summarize/ensure/close-gap/import-portfolio/derived-audit/prune-retired-evidence/duplicate-recycle/worker*/install-startup/...`）。
- 影响：A03 必须为每个对外接口标注"纯读 / 可能写 / 可能外发 / 破坏性 / 系统"；`ensure` 的闸门**不止两道**（v0.2 更正，A-DR-15）：`--allow-download` 决定是否进入获取路径、`latest_as_of` 强制写流程、worker `paused` **拒绝**下载（须 `--allow-acquisition-while-paused` 才放行并记审计）。属既有安全面，A 阶段**只记录不改**。
- 未做：逐条副作用矩阵的**行为层**（`--dry-run`/真实执行）——需隔离副本，留 A06/VR。

## F-A01-4：迁移期分支仍在链上，但不属 A 阶段动作

- 证据：`resolver.py` 中 `legacy_bridge_allowed` 出现 **10 处**（分布于 8 个不同行：L316/575/581/601/741/747/829/1116）；R9 执行包把 bridge/flags 列为批 3 删除对象（revenue `assurance/fc/Phase-14/01_r9_packet.md` §1）。
- 影响：A 阶段记录其存在与位置即可；删除归 R9（技术门 FC-705 + owner 政策门 + 独立 receipt/reviewer）。

## F-A01-5：9/7 诊断行号不可当坐标

- 证据：handbook §2.3「9/7诊断行号只是定位线索」；本步实测 `scanner.py` 与包内行号已漂移（facade 在 `1375-1407`，包写 `1357-1360`）。
- 处置：本映射一律按**符号 + 实测行号**双写，执行时以符号为准。

## F-A01-6：CLI 表面积已由真实解析器确认 —— 51 节点 / 47 叶子（源码 grep 的"47"数值巧合但含义错）

- 证据：owner 2026-09-11 批准的 `--help`-only command-manifest 执行 **52 次探针**，全部 rc=0；输出见 [evidence/cli-help-matrix.json](evidence/cli-help-matrix.json)。真实命令树：41 顶层 + `documents{retire,restore}` / `identity-enrichment{preview,verify,reject}` / `activation{preview,apply,rollback}` / `runtime-policy{show,apply}`。
- 零副作用（**v0.2 限定范围**）：前后快照比对 `catalog.sqlite3`、`config/source_catalog.yaml`、`__pycache__` 目录集合、git dirty 行数 —— 四项全部 true（未变）。**但该快照未包含 `-shm`/`-wal` 伴生文件**，故它**不能**证明"无任何进程打开过数据库"（见 F-A01-8）。
- 处置：A01 §4 以探针结果为准并保留更正说明；A03 §2 的分类依据从"源码 grep（暂定）"升级为"真实 help 文本"。

## F-A01-7：`--help` 探针证明"解析期无副作用"，但不等于"行为层无副作用"

- 证据：`cli.py:860-868` —— `main()` 先 `parse_args`（`--help` 在此 exit），之后才 `config.resolve(strict=True)` + `load_catalog_config`；且模块级只有 `if __name__ == "__main__":` 与 `__all__`（无导入期副作用）。
- 影响：这解释了零副作用，但**不能**推出"任何 `--dry-run` 也安全"——dry-run 会走到 config/DB 层。
- 处置：行为探针（`--dry-run`、只读查询）必须在**隔离副本**上做，且属 A06/VR 范围。

## F-A01-8：`-shm` 前移**已归因**为"本仓强制 push 门会只读打开生产 catalog" —— 原"零副作用"快照存在**覆盖盲区**（次生发现：边界声明漏掉 push 协议）

- 证据（v0.2 新增，回应 A-DR-08；**定案于 22:1x**）：
  1. A.DR 独立观测：`catalog.sqlite3-shm` `LastWriteTime = 2026-09-11 21:18:15`（checkpoint.json 写于 21:16:54 之后 81 秒）；全 `.source_catalog` 树中该日仅此一个文件被改。
  2. 作者观测：同一文件在 `21:26:47` 再次出现。
  3. **归因证据（决定性）**：`revenue-forecast/tools/pre_push_gate.py:184-199` 的 **real-data 套件直接对生产 catalog 跑 pytest**；本会话当晚 **push 5 次**（GitHub Actions 外部时间戳：`#136 21:09:02`、`#137 21:12:29`、`#138 21:16:28`、`#139 21:19:16`、`#140 21:27:44`，全部 success），每次推送**之前**必须跑完该 gate（约 4–5 min，real-data 为最后一步）→ #139 的 real-data ≈ **21:18:15**、#140 的 ≈ **21:26:47**，与两处前移吻合。22:03 手动跑同一 gate 时把 `-shm` 推到 **22:05:03**（复现实验）。
  4. **标定**：22:00 每日任务（`legacy_observer.py --read-only`）在 22:00:02/22:00:18 前移 `-shm` → **只读打开 WAL 库确实更新 `-shm`**；同时主库与 `-wal`（0 字节）全程未变 → **无逻辑写入证据**。
  5. **阴性对照**：`--help` 探针（52×2 轮）、纯 import、watch 窗口（99 样本 / 25 min，窗内无 push）**零前移**；wiki 的 CI 等价门（22:00:22–22:01:45）**未前移**。
  6. 已排除：无 `company_wiki`/`source_catalog` 进程；`company-wiki-source-catalog-worker` 任务不存在；`.source_catalog` 与 `Projects` 非 reparse point、不在 Dropbox/OneDrive 内。
- **结论**：先前"无法归因 / 疑为环境周期性触碰"的表述**已撤回**；正确表述是——**本会话的 push 协议会以只读方式打开生产 catalog**，两次前移即由其造成。**A 阶段的设计动作**（读代码、写文档、`--help` 探针）确实不触碰该库，但"本会话未运行任何会打开 catalog 的代码路径"这一更强的说法**是错的**。
- 影响：
  - v0.1（及 A01 §4/F-A01-6）的"零副作用"结论**范围过窄**：快照只看主库文件，看不到 `-shm`/`-wal`。
  - **门禁教训（重要）**：任何"零触碰生产数据"的边界声明**必须显式排除 push 协议**（gate 会读生产 catalog）；边界证据应以**外部时间戳 + 隔离副本**为准，而非作者声明。
- 处置：1) [boundary-audit.md](boundary-audit.md) 全文按归因结论重写；2) 快照字段扩展为三件套并重跑；3) G5（操作员级独立观测）**保留**——作者自证永不构成独立证据；4) 该"push 即读生产库"的事实已写入 A02/A03 的 VR 约束与后续阶段注意事项。
- 处置：
  1. 边界声明收窄为"作者会话未执行任何会打开 catalog 的 CLI/代码路径"，并把 shm 观测写入 [boundary-audit.md](boundary-audit.md)。
  2. 证据执行器 [evidence/run_cli_help_matrix.py](evidence/run_cli_help_matrix.py) 的快照字段**扩展**为 `catalog.sqlite3` + `-shm` + `-wal`（覆盖盲区修复），并重跑 manifest 记录前后值。
  3. **未完成（需 owner/操作员）**：本机无法自行开启对象访问审计或取得可靠的句柄级证据；该项登记为 A 阶段门禁的**操作员动作**（见 [task_plan.md](task_plan.md) 门禁表）。

## F-A01-9：A.DR 首轮复审结论 = **rejected**（8×P1 / 5×P2 / 3×P3），更正已就地完成并送复审

- 证据：本轮独立复审记录 [reviews/A.DR.json](reviews/A.DR.json)（reviewer session `7cd316cc-…`，非作者会话）。复审确认的正向事实：12/12 输入哈希与字节数、三个 HEAD、root 配置表、51 节点 CLI 结构、checkpoint 7 个产物哈希、跨仓 spawn 引用、仓库与目录边界隔离。
- P1 更正映射：A-DR-01/02/03 → [root-contract.md](root-contract.md) v0.2（新增 R7/R8）；A-DR-04/05/10/12 → [operation-contract.md](operation-contract.md) v0.2；A-DR-06/15 → [baseline-map.md](baseline-map.md) §1.1/§0 与 F-A01-2；A-DR-07/13 → [identity-contract.md](identity-contract.md) v0.2；A-DR-08 → 本文件 F-A01-8 与 [boundary-audit.md](boundary-audit.md)。P2/P3：A-DR-09（三份台账一致化，见 task_plan/checkpoint）、A-DR-11（inputs.json + command-manifest 说明）、A-DR-14（A02 §1 引用拆分）、A-DR-16（复审 ID 由编排方从外部戳记 → 见 task_plan 门禁表）。
- **仍然开放的 owner 裁定**（A.DR 明确要求先裁定再冻结 A02）：`symlink_policy` 假保证是否升级为 B/C 强制整改；`reusable_for_filing` fail-open 是否强制 `false` 生效；两套分叉准入实现（R8）收敛方向；`privacy_class` 缺省 public 是否改为 fail-closed；R6 owner 指派；R4 严格读法（位置代表权是否算违例）。
