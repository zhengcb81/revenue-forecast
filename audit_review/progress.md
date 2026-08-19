# 审查进度日志（历史归档）

> **2026-08-13 最终入口覆盖：** 本日志已关闭，且不再把FCAP作为执行入口。新任务只从 [audit_review/README.md](README.md) 的 `current_next` 继续；本文仅保留历史过程。

## 2026-08-03

- 已完整读取 `planning-with-files` 技能说明并建立独立审查底稿。
- 已盘点根项目和同级项目；确认根项目 CodeGraph 已初始化。
- 已记录审查开始时的工作树状态：仅 `.coverage` 存在既有修改。
- 下一步：提取根计划的阶段、状态、未完成项、验收标准及跨项目引用。
- 已提取 Phase 0–19 的结构性状态与历史审查标题；发现计划首页、阶段标题、追加状态表和阶段内状态存在明显漂移。
- 已确定审查策略：以可执行验收和实际工件为准，把 `[x]`/`completed` 仅视为待验证声明。
- 计划自动汇总的首次 PowerShell 命令发生 ParserError；已记录，下一次改用先收集数组再输出的写法。
- 第二种 PowerShell 汇总虽成功执行，但因换行/编码表现未识别阶段标题；未将其 checklist 汇总视为有效证据，后续更换解析方式。
- CodeGraph 状态核验通过：39 files / 1024 nodes / 1335 edges。
- 改用 `rg` 流解析完成 Phase 清单统计：164 checked / 387 unchecked，确认状态回填严重不一致。
- 已获取根项目 CodeGraph 文件树并识别核心实现/测试边界。
- 已核验 filing-fetch 与 company-wiki 的 CodeGraph 均可用；准备进入跨仓库结构与契约核验。
- 已获取两个相关仓库的结构树，完成审查边界收敛：filing-fetch 全部、company-wiki source-catalog 与被引用契约。
- 已重新读取本次审查计划并提取根计划 Phase 0 的 10 项一级目标、版本基线和通用质量门，建立正式核验主轴。
- 已用 CodeGraph 获取 publication 与 filing acquisition 上下文；锁定 receipt 调用顺序/独立重算和旧 acquisition 可达性为首批深查项。
- 尝试调用图查询 publication 调用顺序，但 CodeGraph 未返回边；已记录为图解析局限并切换到聚焦上下文/源码验证。
- 已取得 `run_forecast` 完整源码并发现 F-01：receipt 在 validator 前构造；下一步检查 validator 的自包含性与正式 consumer gate。
- 已取得 validator 主体源码，确认大量独立语义重算已实现；同时发现两阶段签发模型仍未形成。
- 已定位输入可选造成的强/弱验证分叉，并发现代码版本 3.10/schema 3.6 与 Phase 0 发布基线漂移；列为 F-02/F-03 待动态复现。
- 已建立 publication/rehash 对抗测试索引，准备逐个检查是否覆盖 F-01/F-02。
- 已确认所谓“public API receipt order”测试并不验证 publication receipt 的真实调用顺序，F-01 仍成立；发现一个 CodeGraph 测试方法片段错配，后续用具体文件与运行证据交叉处理。
- 已字面核验 sensitivity 对抗用例与 `_republish` 辅助，下一步动态验证无输入路径是否接受伪造工件。
- 首次动态 probe 因 PowerShell/native 参数引号处理触发 SyntaxError；已记录，改走 stdin 执行。
- 动态 probe 成功：伪造 sensitivity 在无 input validator 下被接受、在带 input validator 下被拒绝。F-02 升级为 Critical。
- 已发现 filing-fetch 核心符号与 handle 对抗测试，准备执行一次项目级 CodeGraph explore。
- 已完成 filing-fetch 唯一一次 CodeGraph explore；核心 reuse-first、identity、deadline、contract、handle 深验证设计基本落地。
- 已定位 company-wiki resolver 与 acquisition service 核心符号，准备进行项目级聚焦 explore。
- 已完成 company-wiki 唯一一次聚焦 explore；单 writer、reuse-first、identity fail-closed、issuer 归一、journal 与 debug trace 主体设计均有实现证据。
- 已确认 revenue 根仓库仍保留一套完整旧 filing owner；下一步核验其文档/CLI 可达性和废弃状态。
- 已确认旧 owner 仍是可执行下载 CLI，形成 F-04；同时发现 SKILL/CHANGELOG/schema/version 多处漂移，形成 F-05。
- 跨仓库 git/安装路径盘点首次命令发生 PowerShell ParserError；已记录并改为数组收集写法。
- 已完成五仓库 git/工作树与四个安装目录盘点；记录 filing-fetch 未提交能力和普通目录同步风险。
- 已运行 revenue 四组 targeted suites，共 41 tests 全绿；已将“测试通过但 F-02 未覆盖”纳入结论。
- 第一轮全量：revenue 253 + tools 4 全绿；filing-fetch 105 中 6F/2E/4S。准备核对解释器与测试安装契约后给 F-06 定级。
- 确认解释器差异：Miniconda Python 可 import company-wiki，bundled Python 不可；filing-fetch 未声明该依赖。已用计划规定的默认 `python` 重跑全量，运行中。
- filing-fetch 默认 Python 全量完成：117/117 通过、5 skipped。F-06 定级 Medium（环境/依赖声明），非当前功能回归。
- revenue 完整质量门完成：compileall/ruff 绿、253 tests 绿、coverage 87% 总门通过；发现 F-07 逐模块 coverage 未达目标。
- company-wiki 全量 pytest 已收集 1630 项，运行中；filing-fetch coverage 运行中。
- filing-fetch 完整质量门完成：compileall/ruff 绿、117 tests 绿（5 skip）、coverage 96%。company-wiki 运行至约 30%。
- 字面审查 invest-core/framework，确认 F-02 会穿透正式 invest adapter 与 bundle；同时确认单向依赖/禁止收入重建的主体设计已实现。
- Phase 3 与 Phase 4 机器证据（2026-08-03 审查运行）：revenue `python -m pytest tests` 253 passed 全绿；filing-fetch 117/117 passed（5 skipped）；company-wiki pytest 1630 收集、1629 passed 1 失败判竞态（F-09）；invest-core 36 passed（1 skip）；invest-framework 22 passed；compileall/ruff 门均通过。
- company-wiki 全量运行约 37%，尚未出现失败。
- invest-core 36 tests（1 skip）与 invest-framework 22 tests 全绿，compileall/ruff 均通过；company-wiki 约 38%。
- revenue 安装同步默认检查完成：`.agents` 58 files MATCH；`.codex` 待显式检查。
- 显式检查发现 revenue `.codex` 34-file DIFF；盘点 filing-fetch 两套安装也有缺文件/pycache/内容状态分叉。登记 F-08 High。
- company-wiki 全量完成：1629 pass / 1 fail（worker supervisor 终止后事件日志 PermissionError），登记 F-09 待复现。
- F-09 targeted 连跑 3 次全过，判为 suite-load 竞态/非确定性 teardown，维持 Medium。
- 深查 workflow/backtest：发现 snapshot 持有 input 却调用弱 validator，F-02 影响扩展到回测；另登记 F-10 legacy engine compatibility matrix 缺失。
- 对照 Phase 8 与实现/文档，确认 trusted host receipt、mandatory search events、fail-to-draft、sensitivity completeness 均未落地；登记 F-11 Critical 与 F-12 High。
- company-wiki compileall 通过、ruff 失败 6 项，登记 F-13；进程观测未发现 pytest 临时 worker 残留。
- 已取得 create_snapshot 源码，确认 snapshot identity/hash 不能弥补 validate_snapshot 未传 input 的语义缺口；准备动态复现。
- 用户明确最终目标是完整细致的改进计划，而非立即实施；已将 Phase 5 交付标准扩展，继续保持业务代码只读。
- 已按用户要求确认持续落盘机制：每两次查看/搜索补充 findings/progress/task_plan；company-wiki 全量 pytest 当前运行至约 35%。
- Phase 1 完成，进入 Phase 2/4 的实现与全量质量门交叉核验。
- invest-core CodeGraph 状态查询失败（未初始化）；等待是否允许初始化，其他核心仓库审查继续。
- 用户指示继续。恢复会话：重读三份底稿，确认下一阶段为 snapshot 动态复现 + Phase 2/3/4 收尾 + Phase 5 改进计划。
- bash 工具实为 git-bash（非 PowerShell）；首次 here-string 语法失败，改为将探针落盘为 `audit_review/probe_snapshot_forgery.py` 再执行，不再重复原命令。
- snapshot 伪造动态复现成功：`validate_snapshot(forged)` ACCEPTED、带 input 强路径 REJECTED。F-02 扩展结论已写入 findings。
- filing-fetch 待确认点关闭：request_id/status 门有实现+测试；授权审计链在 company-wiki DownloadReceipt/provenance/journal；登记 F-14（Low，无客户端 receipt）。
- company-wiki 待确认点关闭：retire/restore 实现（store.py:334-414，审计行）+6/6 测试；scanner 在 canonical_writer.py:185 热路径被全部 import 测试间接覆盖，证据强度升级。
- F-10 精确取证：output validator 3.4/3.5 绑当前 engine 过窄（CHANGELOG：3.4 由 v3.5.0 引入，真实配对 3.5.0–3.10.0），snapshot 任意 engine 过宽；3.3/3.4/3.5 无配对测试。
- 用户授权 invest-core CodeGraph 初始化；invest-core（183 节点）与 invest-framework（149 节点）均已建索引。结构确认：invest 消费链无任何函数接受 input，F-02 穿透字面+结构双确认。
- 用户选择交付物并入现有底稿。已完成：task_plan Phase 2/3/4 标记 completed 并补执行结果表；findings 回填 10 目标核验矩阵+审查结论+问题清单；task_plan 新增 Phase 6 改进计划（A/B/C/D 四阶段，含优先级/依赖/文件/RED/步骤/验收/回滚）。
- 错误记录新增 3 条（bash 非 PowerShell、codegraph CLI 子命令、相对路径静默无输出）。
- Phase 5 完成。全部审查阶段结束；业务代码未改动（只读审查）；新增文件仅 `audit_review/probe_snapshot_forgery.py`（诊断探针）。

## 2026-08-16 恢复会话（ZR-204 收尾 → ZR-205 进行中）

- ZR-204（锁/错误 taxonomy）独立复核 accepted：分类矩阵 7 项抽查全对、双 CLI 发射点接入 structured_error、15 个 taxonomy 单测绿、受影响 contract 批量 3 个失败均为已知既有（security_identity×2 + extraction_quality），无 ZR-204 回归。reviewer receipt 已签并入库（canonical 5d62798e…）。
- 机器状态：ZR-204 accepted → closure-advance → ZR-205；revenue commit 217b303 落库（pre-commit 全套 ~7min 通过）。
- ZR-205（filing deadline-aware retry）preflight + 实现完成：
  - filing-fetch _classify_wiki_error 消费 ZR-204 canonical 码（catalog_locked/catalog_busy/db_timeout/worker_paused/fatal），N-1 类名形态保留，非 JSON/未知 fail closed fatal；ZR102-F2 filing 侧根因关闭（raw lock → catalog_busy retryable）。
  - retry：{catalog_locked, catalog_busy, db_timeout}，±20% jitter、cap 60s、wait=min(jittered, remaining) 无 sleep 超 deadline；worker_paused/fatal 不自动重试。
  - 信封：成功带 calls/downloads，失败带 stage/attempts/calls/downloads（READ-09/READ-10）。
  - 验证：filing 全套 328 passed / 6 skipped；branch coverage 91.45%≥90；complexity 34≤34；mypy 干净；companies-reuse E2E golden identical；commit 0e5d209（skill sync 后）。
  - implementer receipt 已签（canonical 446f66ba…）；state → independent_review；独立复核进行中（subagent）。
  - ZR102-F1（exact 无授权下载）移交 ZR-407（阶段 D authorization-bound GapPlan），ZR205-IMPL-003 登记。

## 2026-08-17~18（阶段 D：ZR-306/307/401 closure）

- ZR-306 closure：SourceBundle role DAG 最小失效 property tests（wiki a608980，6 tests，产品零改动）；复核 accepted。
- ZR-307 closure：filing 分阶段 envelope + resolution trace（filing df66796，338 tests）；复核 accepted。
- ZR-401 closure（RootPolicy 3.0 严格加载器）：wiki 251615e（12 tests，787 unit，McCabe max 8，mypy clean）；独立复核 accepted（5 条非阻断 findings，REV-003 生产 config 未切 3.0 已记显式决策延期至 ZR-402/403 或阶段 D 出口）；closure→ZR-402。
- 机器状态：current_phase=D_lifecycle_roots_freshness，current_next=ZR-402；accepted 36/117（A0 8 + B 9 + C 11 + D 8）。
- 停止点（用户指示：收尾并更新全部 planning docs 后停止）：ZR-402（adapter registry）未领取；三仓 HEAD：revenue fd017c9 / wiki 251615e / filing df66796（均未 push）。

## 2026-08-18 阶段 D 收官（ZR-402~406 closure → 用户指示：收官 + 更新全部 planning docs 后停止）

- ZR-402 closure：adapter registry 路由契约（wiki 57cd72e，36 tests：kind/ID 无关路由 + 零 kind 分支机械门 + M1~M9 mutation 击杀表；产品零改动）；复核 accepted（3 info）。
- ZR-403 closure：dedupe/resolver 泛化（wiki 87ee0ac，7 tests：四上下文含 future_lake、health→priority、读不写 canonical、10-shuffle 稳定；产品零改动）；复核 accepted（1 info）。
- ZR-404 closure：envelope 加性扩展（wiki f45f7ed，11 tests：policy/epoch/cohort/source-hash 一致 + 排除 trace + canonical rationale 脱敏 + 冲突 fail closed；schema 保持 1.0，filing 零改动）；复核 accepted（3 info）。
- ZR-405 closure：跨仓 policy-root containment（wiki e56eb5f：policy-export 端点 + resolve/ensure 响应内嵌 + export 可复用性归一化；filing 3087f28：响应内嵌消费 + hash 对 policy document 计算 + envelope 交叉校验；18 tests）；复核 accepted（1 minor REV-002 close-gap 响应内嵌 policy_export → 后续 ZR-407 + 3 info）。
- ZR-406 closure：正交 gap-plan 矩阵（wiki 45ae721，39 collected = 30 格参数化矩阵 + 9 聚焦；capture_ready 防御过滤）；首轮 changes_required（REV-001 计数 12≠13、REV-002 矩阵 24/30）→ 真·数据驱动 30 格修正 → delta accepted（2 minor 转录）。
- 机器状态：current_phase=D_lifecycle_roots_freshness，current_next=ZR-407；accepted 41/117（A0 8 + B 9 + C 11 + D 13）。
- 停止点（用户指示：收官并更新全部 planning docs 后停止）：ZR-407 未领取；恢复清单：ZR-407（authorization-bound GapPlan/CloseGap，含 ZR405-REV-002）→ ZR-408（下载执行/single-flight）→ ZR-409（future_lake 生产切换，阶段 D 出口）→ E。
- 三仓 HEAD（本地 fcap，未 push）：revenue c9a3add（ZR-406 closure 提交进行中）、wiki 45ae721、filing 3087f28。

## 2026-08-18 晚（ZR-407/408 closure 补提交 → ZR-409）

- ZR-407 三仓产物补提交：wiki bdffc54（actionable union + ensure 只读路径）、filing 5a1c18f（_gap_plan_has_actionable_candidate）、revenue 6145dad（closure）；复核 accepted → closure→ZR-408。
- ZR-408 closure：验收钉死卡（产品零改动），跨进程 spawn 双进程 single-flight oracle 补强；22 contract + 787 unit 绿；复核 accepted（3 info）→ closure→ZR-409。
- 机器状态：current_phase=D_lifecycle_roots_freshness，current_next=ZR-409；accepted 42/117（D 14/16）。
- 三仓 HEAD：revenue（closure 提交进行中）、wiki 71aa798、filing 5a1c18f（均未 push）。

## 2026-08-19（阶段 D 出口达成 → 阶段 E 启动）

- ZR-409 closure（阶段 D 出口卡）：生产 config 新增第四根 future_lake（directory+sidecar_filing_v1，仅配置接入，产品 core diff=0，wiki eb3aa79）；三真实 root 只读旅程（companies 紫金 601899/2025 exact、dayu-only 金斯瑞 HK1548/2021 exact 且 companies 无同 hash 前提钉死、Dropbox 星环 688031/2024 fail-closed capture_incomplete——生产数据现状）+ 紫金跨根共享 canonical=companies；EX-08 生产形状扫描/导出；EX/LT/DL/IDX/UJ 场景→测试映射钉死复跑全绿（28 contract + 787 unit）。复核 accepted（5 info，REV-001/002 tidy，wiki 726d63d）→ closure→ZR-501，phase=E_broker_web_processing。
- 机器状态：current_phase=E_broker_web_processing，current_next=ZR-501；accepted 43/117（A0 8 + B 9 + C 11 + D 16）。
- **阶段 D 出口达成**：16/16 全闭。
- 三仓 HEAD：revenue（closure 提交进行中）、wiki 726d63d、filing 5a1c18f（均未 push）。

## 2026-08-19（ZR-501 closure + ZR-502 实施完成，待独立复核）
- ZR-501 closure：wiki 8c5f24f 复核 accepted（REV-001 page_count IPC envelope 修复，delta accepted）；revenue 465033c；state accepted 44/117。
- ZR-502 实施完成：wiki 19c3b73（homepage_identity.py 纯函数 + normalizer first_page_text/frontmatter 接线 + sidecar filing_date 映射 + 词汇注册 + 11 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical 74b0027a；独立复核运行中。

- ZR-502 closure：reviewer-zr502-independent accepted（3 info）；state accepted 45/117；closure-advance -> ZR-503（E_broker_web_processing）；README cursor 已镜像 ZR-503。

- ZR-503 实施完成：wiki e8e2926（entity_detection.py 纯函数 + normalizer 全文接线 detected_entities + multi_entity_attribution_needed flag + 零硬编码/golden 锚定 13 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical c39c67e5；独立复核运行中。

- ZR-503 closure：reviewer-zr503-independent accepted（3 info）；state accepted 46/117；closure-advance -> ZR-504（E_broker_web_processing）。

- ZR-504 实施完成：wiki 2781df9（test-only 页码保真 golden 10 tests，产品 src 零改动）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical 3ce9e3b3；独立复核运行中。

- ZR-504 closure：reviewer-zr504-independent accepted（2 info）；state accepted 47/117；closure-advance -> ZR-505（E_broker_web_processing）。

- ZR-505 实施完成：wiki 7c44904（test-only typed table 保真 golden 11 tests，产品 src 零改动）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical b31691c6；独立复核运行中。

- ZR-505 closure：reviewer-zr505-independent accepted（1 info + 1 minor 计数）；state accepted 48/117；closure-advance -> ZR-506（E_broker_web_processing）。

- ZR-506 实施完成：wiki cbc6d8c（section_chunk_fact.py 纯函数 + normalizer document_structure 接线 + 14 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical 2d00aeb4；独立复核运行中。

- ZR-506 closure：reviewer-zr506-independent accepted（2 info）；state accepted 49/117；closure-advance -> ZR-507（E_broker_web_processing）。

- ZR-507 实施完成：wiki bd337c4（processing_demand.py ProcessingDemand API + 14 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical f1eace9a；独立复核运行中。
