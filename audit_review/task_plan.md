# 项目设计目标达成审查计划

## 审查目标

以根目录 `task_plan.md` 及其引用的设计、契约和历史审查文档为基准，全面核验 `revenue-forecast` 与相关项目（至少包括 `filing-fetch`、`company-wiki`）是否达到设计目标。结论必须能回溯到计划条目、实现、测试或运行验证。

## Phase 1（基线与范围）— 状态：completed

- [x] 提取计划文档中的设计目标、完成声明、验收条件与跨项目依赖
- [x] 识别实际相关仓库、版本状态和 CodeGraph 可用性
- [x] 建立“计划目标 → 实现 → 测试 → 结论”核验矩阵

## Phase 2（revenue-forecast 核验）— 状态：completed

- [x] 审查架构、契约、核心工作流、脚本与代理资产
- [x] 审查测试覆盖、静态质量门与实际运行结果
- [x] 核验计划中历史问题是否真实关闭、是否发生回归

### 2.1 执行结果

| 结果 | 详情 |
|------|------|
| 质量门 | compileall/ruff 绿；253/253 tests + tools 4/4；coverage 总 87%（F-07 分模块未达标） |
| 核心缺口 | F-01（receipt 先于验证）、F-02 Critical（弱验证路径+snapshot 动态复现 ACCEPTED）、F-10（engine 矩阵过窄/过宽）、F-11 Critical（Phase 8 伪完成）、F-04（旧 owner 双活） |
| 对抗测试 | 概率/目标/禁止字段重签拒绝已覆盖；敏感性无 input 路径与 snapshot 全哈希重签未覆盖（探针 `audit_review/probe_snapshot_forgery.py` 确认可利用） |

## Phase 3（跨项目核验）— 状态：completed

- [x] 审查 filing-fetch 的接口、证据与落盘契约
- [x] 审查 company-wiki 的目录、索引、不可变证据和消费路径
- [x] 审查其它被计划或实现引用的仓库边界

### 3.1 执行结果

| 结果 | 详情 |
|------|------|
| filing-fetch | reuse-first/identity/deadline/契约/handle 深验证落地；117/117 tests、coverage 96%；F-06 非 hermetic、F-14 无客户端 receipt（Low） |
| company-wiki | 单 writer/reuse-first/identity fail-closed/issuer 归一/journal/debug trace/retire+restore 实现+测试确认；1629/1630（F-09 竞态）；ruff 6 项红（F-13） |
| invest-core/framework | 单向依赖/禁止重建收入已落地且测试全绿；CodeGraph 已初始化（用户授权）；结构上无 input 参数，F-02 穿透字面+结构双确认 |
| 安装副本 | F-08 High：revenue `.codex` 34 文件漂移；filing-fetch 两安装目录缺文件且含 pycache；canonical 有未提交增强 |

## Phase 4（端到端与风险核验）— 状态：completed

- [x] 执行可复现测试、校验器和关键集成检查
- [x] 检查文档/实现/测试之间的漂移与伪完成风险
- [x] 按严重度评估缺口、影响和修复优先级

### 4.1 执行结果

| 结果 | 详情 |
|------|------|
| 全量门 | revenue 253 绿 / filing-fetch 117 绿（5 skip）/ company-wiki 1629 绿 1 红（F-09 复现 3/3 过，判竞态）/ invest-core 36 绿（1 skip）/ invest-framework 22 绿 |
| 动态复现 | F-02 无 input 弱路径 ACCEPTED（首次会话）；snapshot 全哈希重签 ACCEPTED（本会话探针）；带 input 强路径均 REJECTED |
| 漂移 | F-03 版本基线、F-05 SKILL/CHANGELOG/契约漂移、F-12 签发顺序文档与实现相反；计划文档 164[x]/387[ ]，Phase 8/17/19 状态自相矛盾 |
| 分级 | Critical×2（F-02、F-11）；High×5（F-01、F-04、F-08、F-10、F-12）；Medium×6（F-03、F-05、F-06、F-07、F-09、F-13）；Low×1（F-14） |

## Phase 5（审查结论与改进计划）— 状态：completed

- [x] 输出总体达成度与分项目结论 → 见 findings.md「审查结论」
- [x] 输出证据化问题清单和设计目标核验矩阵 → 见 findings.md「核验矩阵」
- [x] 输出完整细致的分阶段改进计划，不实施业务修复 → 见下文 Phase 6
- [x] 每项改进给出优先级、依赖、文件/符号、RED 测试、实施步骤、验收命令、迁移/回滚条件

## Phase 6（改进计划 — 交付物，不实施业务修复）

> 依赖约定：A=Critical 先行；B 依赖 A 的契约面；C/D 可与 B 并行。所有阶段以 RED 测试先行，修复落地前不得关闭对应发现。

### 阶段 A（Critical：正式可信链）

#### A1 两阶段签发与自包含验证契约（修 F-01、F-02、F-12 核心）

- 优先级：P0；依赖：无；阻塞 A3、B4。
- 文件/符号：
  - `scripts/revenue_core.py::run_forecast`（当前 draft→receipt→hash→validate）
  - `scripts/revenue_report.py::validate_forecast_output`（data 可选造成强弱分叉）
  - `scripts/revenue_publication.py::build_publication_receipt`（公开可任意调用）
  - `scripts/revenue_backtest.py::validate_snapshot`（:78 持有 input 却走弱路径）
  - `invest-core/scripts/invest_contracts.py::validate_revenue_forecast`（:258 无 input 参数）
- RED 测试（先写先红）：
  1. `tests/test_output_report.py`：伪造 sensitivity + `_republish` 全哈希重签后，调用新的正式发布验证入口必须拒绝；现有 `test_rehashed_forged_sensitivity_terminals_are_rejected` 保留为强路径对照。
  2. `tests/test_backtest.py`：复刻 `audit_review/probe_snapshot_forgery.py` 攻击——伪造 snapshot 内 sensitivity 并重签 receipt/result/snapshot 全部哈希，`validate_snapshot` 必须拒绝。
  3. `tests/test_publication_pipeline.py`：`build_publication_receipt` 不得接受未经强验证上下文的结果；公开 API 在验证前不得返回 pass receipt（现有同名测试需升级为监控真实调用顺序）。
  4. invest-core `tests/test_revenue_adapter.py`：携带伪造 sensitivity 的 revenue artifact 必须被 `validate_revenue_forecast` 拒绝。
- 实施步骤：
  1. 将 `validate_forecast_output` 拆为两个显式入口：`validate_published_forecast(result, input)`（强，正式唯一入口）与受限的 `validate_legacy_output(result)`（仅 legacy read-only，明确弱化 gate 清单）。
  2. `build_publication_receipt` 改为只接受强验证返回的 verification context（含 input_sha256、已执行 gate 清单、validator 版本），或私有化并由 validator 内部调用；receipt 的 `gate_ids` 必须反映实际执行的 gate，不得固定声明 `output_recomputation`。
  3. `run_forecast` 改为 draft→`validate_published_forecast(draft, input)`→签发 receipt→写 result hash→返回。
  4. `validate_snapshot` 传入 `snapshot["input_document"]` 走强入口；snapshot schema 不变。
  5. invest-core `validate_revenue_forecast` 改为校验新 receipt 契约（verification context 绑定），结构上无需接受 input（由 A1.2 让工件自包含）。
- 验收命令：
  - `python -m pytest tests/ -q`（revenue 全绿，含 4 个新 RED 转正）
  - `python -m pytest tests -q`（invest-core / invest-framework 全绿）
  - `python audit_review/probe_snapshot_forgery.py` 两行输出必须均为 REJECTED
- 迁移/回滚：
  - receipt 格式变更需 bump publication receipt schema 并在 CHANGELOG 记录；旧 receipt 工件由 `validate_legacy_output` 只读接受且不得进入 invest。
  - 回滚 = revert 本阶段提交并重跑五仓库全量；探针输出回到 ACCEPTED 即视为回滚后风险重现，必须阻断发布。

#### A2 Trusted workflow attestation（修 F-11）

- 优先级：P0；依赖：无（与 A1 并行，但 receipt 契约需与 A1.2 对齐）；阻塞 B4。
- 文件/符号：
  - `scripts/revenue_core.py` capture 契约（tool_name/tool_call_id 自填字符串）
  - management `not_available.search_event`（当前可选）
  - `references/compliance-contract.md`（承认 host trust 但 runtime 仍签 formal）
  - `require_sensitivity_completeness`（当前 opt-in）
- RED 测试：
  1. 自填 tool_call_id + 无 host receipt → 不得产出 `formal_output_mode="formal"`（只能 draft/unattested）。
  2. `not_available` 缺 machine-generated search_event → 输入验证失败。
  3. formal 且 sensitivity completeness 未满足（无测试也无结构化排除）→ 降级 draft 或拒绝。
  4. invest-core 拒绝无 attestation 的 formal artifact。
- 实施步骤：
  1. 定义 runtime capability：有 trusted verifier→formal；无→draft/unattested，且 invest fail closed。
  2. host receipt 绑定 normalized request/response hash、tool/action、timestamp、environment、issuer，由输入作者无法调用的 verifier 验证；禁止自填 tool_call_id 替代。
  3. communication/search、capture/open、exception approval、sensitivity exclusion 共用同一 attestation contract。
  4. formal 模式强制 sensitivity completeness（移除 opt-in 或 formal 默认开启）。
- 验收命令：`python -m pytest tests/ -q`；新增 attestation 对抗套件全绿；`ruff check scripts tests` 绿。
- 迁移/回滚：旧 formal 工件无 attestation → 只能按 legacy read-only 消费，invest 拒绝；回滚 revert + 全量。

#### A3 跨仓库 conformance 链（固化 A1/A2）

- 优先级：P0；依赖：A1、A2。
- 文件/符号：revenue `tests/`、invest-core `tests/test_revenue_adapter.py`、invest-framework `tests/`（bundle_validator/company_orchestrator 用例）。
- RED 测试：一条 revenue→invest-core→framework 的伪造 artifact（重签全哈希）端到端用例，三跳均必须拒绝。
- 实施步骤：在 invest-framework 增加跨仓库 fixture（由 revenue 生成、经 `_republish` 重签），接入 CI。
- 验收命令：三仓库全量 pytest 绿；伪造 fixture 用例 RED→绿。
- 迁移/回滚：fixture 仅测试资产；回滚删除 fixture 不影响产品代码。

### 阶段 B（High：清旧物、封发布面）

#### B1 旧 filing owner 下线（修 F-04）

- 优先级：P1；依赖：无；建议与 A 并行。
- 文件/符号：`scripts/filing_acquisition.py`（完整 config/adapter registry/writer/manager/CLI）、`tests/test_filing_acquisition.py`、`tools/sync_installations.py` manifest。
- RED 测试：`python scripts/filing_acquisition.py --allow-download ...` 必须 hard-fail 或该入口不存在；发布 manifest 不含旧 owner。
- 实施步骤（二选一，推荐 1）：
  1. 从 `scripts/` 与安装 manifest 删除 `filing_acquisition.py`；测试 fixture 移入 `tests/fixtures/` 并改为不可执行下载的 stub。
  2. 保留文件但移除 `main()`/下载路径，全部公开入口改为转发 `filing_fetch_client.resolve_filing` 的 thin shim 或 hard-fail。
- 验收命令：`python -m pytest tests/ -q` 绿；`python tools/sync_installations.py --check`（含 `.codex`，见 B3）绿；grep 确认 SKILL/references 无旧路径引用。
- 迁移/回滚：删除前在 CHANGELOG 记录移除；git 历史可回滚；fixture 迁移需同步更新 `tests/test_filing_acquisition.py` import。

#### B2 schema/engine compatibility registry（修 F-10）

- 优先级：P1；依赖：无。
- 文件/符号：`scripts/revenue_report.py:105-132`（内联 if-elif）、`scripts/revenue_backtest.py:71-75`（任意 engine）、新 `scripts/schema_compatibility.py`（建议）。
- RED 测试：
  1. schema 3.4 + engine ∈ {3.5.0..3.9.0} 的真实历史配对必须接受（当前过窄会红）。
  2. schema 3.4 + 未知 engine（如 9.9.9）必须拒绝。
  3. snapshot legacy schema + 矩阵外 engine 必须拒绝（当前过宽会红）。
  4. 3.3/3.4.0、3.5/3.10.0 配对补测。
- 实施步骤：抽出单一 immutable `(schema_version, engine_version, mode)` registry（每行注释 CHANGELOG 溯源）；forecast/output/snapshot/invest 四处共用；删除 if-elif 链。
- 验收命令：`python -m pytest tests/ -q` 绿；registry 单测覆盖全部受支持配对。
- 迁移/回滚：registry 初版必须复现当前全部合法配对 + 修正后的 3.4 集合；回滚 revert。

#### B3 安装同步封口（修 F-08）

- 优先级：P1；依赖：B1（manifest 内容）。
- 文件/符号：`tools/sync_installations.py`（默认只查 `.agents`）、revenue `.codex/skills`（34 文件漂移）、filing-fetch 两安装目录（缺 SKILL/CHANGELOG/references、含 pycache）、filing-fetch 未提交增强（e2e/pyproject）。
- RED 测试：sync `--check` 默认覆盖 `.agents` + `.codex` 双目标；漂移时 exit≠0；manifest 拒绝 `__pycache__`/`.coverage`/计划底稿。
- 实施步骤：
  1. 提交或丢弃 filing-fetch 未跟踪增强，使 canonical worktree=git HEAD。
  2. 定义每个 skill 唯一 canonical manifest（含哈希），`.agents`/`.codex` 均为默认 check 目标。
  3. 用 sync 工具重建 `.codex` 副本；CI 发布前哈希 manifest fail closed。
- 验收命令：`python tools/sync_installations.py --check`（双目标）exit 0；filing-fetch 等价命令 exit 0。
- 迁移/回滚：副本重建为纯拷贝，可随时回滚；CI 门先行灰度（warn→fail）。

#### B4 文档契约对齐（修 F-12、F-05、F-03）

- 优先级：P1；依赖：A1、A2（先修实现再改文档，禁止反向适配）。
- 文件/符号：`references/compliance-contract.md`（"validator then signs"）、`SKILL.md`（Versioning/Formal output gate 仍写 3.4 receipt、工具列表重复、input helpers 标 3.5）、`CHANGELOG.md`（Unreleased vs SKILL_VERSION=3.10.0）、根 `task_plan.md` 首页状态。
- RED 测试：`tests/test_skill_documentation.py` 扩展——文档中的 schema/engine/签发顺序声明必须与 `revenue_core` 常量及真实调用顺序一致（AST/调用顺序探针断言）。
- 实施步骤：A1/A2 落地后统一改文档；bump `SKILL_VERSION` 并补 CHANGELOG 条目；计划首页回写当前真实状态。
- 验收命令：`python -m pytest tests/test_skill_documentation.py -q` 绿；文档/常量 diff 为空。
- 迁移/回滚：纯文档+常量，revert 即可。

### 阶段 C（Medium：质量门封口）

#### C1 coverage 分模块门（修 F-07）

- 优先级：P2；依赖：B1（旧 owner 移除后基线变化）。
- 文件/符号：coverage 配置（`.coveragerc`/pyproject）、`scripts/filing_fetch_client.py`（41%）、`revenue_forecast.py`（subprocess 未采集）。
- RED/验收：CI 分模块 threshold（新增模块 ≥90%）；启用 coverage subprocess/multiprocessing 或补 in-process main 测试。
- 验收命令：`coverage run -m pytest tests/ && coverage report --fail-under=...` 分模块达标。

#### C2 filing-fetch hermetic（修 F-06）

- 优先级：P2；依赖：B3（未提交文件先入 canonical）。
- 文件/符号：filing-fetch `pyproject.toml`（无依赖/pythonpath 声明）、`tests/test_e2e_isolated_wiki.py`（import company_wiki）、real-tool conformance 的 Windows 子进程解码。
- 实施步骤：声明 company-wiki 依赖（editable/path）或测试内显式 sys.path fixture；子进程 stdout/stderr 统一 `encoding="utf-8", errors="replace"`；CI 用干净解释器复跑。
- 验收命令：干净 venv 中 `python -m pytest tests -q` 117 全绿（5 skip）。

#### C3 worker teardown 确定化（修 F-09）

- 优先级：P2；依赖：无。
- 文件/符号：company-wiki `tests/contract/test_source_catalog_worker_bootstrap.py::test_terminating_supervisor_does_not_leave_an_orphan_worker`、worker/supervisor 启动停止路径。
- 实施步骤：确定性 teardown handshake + 句柄关闭确认 + 进程树终止；stress/repeat（如 50 次）进 CI；禁止加盲目 sleep、禁止标 flaky/skip。
- 验收命令：全量 pytest 连续 3 轮无 PermissionError；repeat 套件全绿且无残留进程。

#### C4 company-wiki ruff 门（修 F-13）

- 优先级：P2；依赖：无。
- 文件/符号：`tests/contract/test_source_catalog_download_suppression.py`、`test_source_catalog_retire.py`（5 unused import + 1 unused local）。
- 实施步骤：清理或确认 helper 接入断言；ruff 加入 PR 必跑门。
- 验收命令：`ruff check src scripts tests` 绿；1630 全量不劣化。

### 阶段 D（Low/治理）

- D1（F-14，P3）：filing-fetch 响应契约增加 gap/authorization receipt 字段（下载授权+journal 引用随 handle 返回）；RED：无授权下载返回的 handle 必须带可校验 receipt。依赖 A1 契约风格。
- D2（P3）：company-wiki 为 `scan_catalog` 增加 1-2 个确定性直接单测（sidecar 配对/排除之外的 catalog 重建断言）。
- D3（P3）：invest-core schema-3.3 normalizer skip 的兼容边界写入文档；根计划文档治理——状态表单一可信来源、completed 判定以验收项全勾选+测试证据为准。
- D4（P3）：invest-framework CodeGraph 已在审查中初始化（149 节点）；建议两 invest 仓库把 `.codegraph/` 纳入常规维护。

### 阶段总依赖图

```
A1 ─┬─→ A3 ─→ B4
A2 ─┘         ↑
B1 ─→ B3      │
B2 ───────────┘（文档对齐最后）
C1─C4、D1─D4 可与 B 并行
```

## 错误记录

| 错误 | 尝试 | 处理 |
|---|---:|---|
| 暂无 | 0 | — |
| PowerShell ParserError：`foreach` 结果直接接管道产生空管道元素 | 1 | 改为先赋值数组、再单独排序输出；不重复原命令 |
| PowerShell `Get-Content` 阶段汇总未识别标题，且行数与 `rg` 不一致 | 2 | 放弃该解析路径，改用 UTF-8 Python/`rg` 解析；结果不作为证据 |
| CodeGraph 未给出 `run_forecast` callees / publication builder callers | 1 | 视为解析局限，不把“无边”当作无调用；改用聚焦 context 和源码/测试 |
| invest-core CodeGraph 未初始化 | 1 | 请求用户是否允许运行 `codegraph init -i`；未授权前不修改该仓库 |
| CodeGraph 某测试方法的符号名与返回代码主体错配 | 1 | 仅对该已知文件使用字面读取并以实际测试为准，不泛化否定整个索引 |
| PowerShell 将多行 Python 作为 `-c` 参数时剥离引号，触发 SyntaxError | 1 | 不重复 `-c` 传参；改为把 here-string 通过 stdin 管道传给 Python `-` |
| PowerShell 路径盘点再次把 `foreach` 直接接到管道，触发 ParserError | 1 | 先收集 `$pathRows`，再单独 `Format-List`；后续避免该语法模式 |
| 误将 bash 工具当 PowerShell，here-string 报 `=: command not found` | 1 | 探针落盘为 `audit_review/probe_snapshot_forgery.py` 再执行；不再用 shell here-string 传多行脚本 |
| `codegraph search` 子命令不存在（CLI 与 MCP 工具名不同） | 1 | 改用 `codegraph query`；先 `--help` 确认子命令 |
| 相对路径探针在错误 cwd 下静默无输出（`Path.exists()` 守卫吞掉分支） | 1 | 用 `ls`/`wc` 核实真实路径，探针脚本一律用绝对路径或显式 workdir |
