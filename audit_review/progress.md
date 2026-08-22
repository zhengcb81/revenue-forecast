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

- ZR-507 closure：reviewer-zr507-independent accepted（1 minor + 1 info）；codegraph_freeze MISSING-001 清除；state accepted 50/117；closure-advance -> ZR-508（E_broker_web_processing）。

- ZR-508 实施完成：wiki 8e2bf3f（scheduler.py 公平性 aging/deadline/budget + claim(demand_id) 加性扩展 + 11 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical cb34ed85；独立复核运行中。

- ZR-509 实施完成：wiki ea9c49b（html_capture.py 身份门 + 12 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical 21d5335f；独立复核运行中。

- ZR-509 closure：reviewer-zr509-independent accepted（3 info）；state accepted 52/117；closure-advance -> ZR-510（E_broker_web_processing，阶段 E 收尾）。

- ZR-510 实施完成：wiki 524a535（attribution.py chunk 归属错归=0 + normalizer chunk_attribution 接线 + 9 tests）；unit 787 + 回归全绿；state triplet_green；implementer receipt canonical a01d1c85；独立复核运行中；阶段 E 收尾。

- ZR-510 closure：reviewer-zr510-independent accepted（1 info + 2 minor 修复于 wiki 26a6b22）；state accepted 53/117；closure-advance -> ZR-701（phase F_revenue_mining）；**阶段 E 出口达成（ZR-501~510 10/10）**。

- ZR-701 实施完成：revenue 1dbae63（prepare_forecast 纯函数 + validate-only 零写 + draft/validated artifact + ProcessingDemand 提交 + 7 tests）；全量 477+106 绿；state triplet_green；implementer receipt canonical fe73c583；独立复核运行中。

- ZR-701 closure：reviewer-zr701-independent 首轮 changes_required（REV-001 复杂度 ratchet 21>17）→ ff7429e 修复 → delta accepted（1 minor + 2 info 非阻断）；state accepted 54/117；closure-advance -> ZR-702（F_revenue_mining）。

- ZR-702 实施完成：revenue e9e837f（schema_fields.py 真源 + lint_input 接线 + 8 tests）；全量 485+106 绿；state triplet_green；implementer receipt canonical efe5b0f3；独立复核运行中。

- ZR-702 closure：reviewer-zr702-independent accepted（1 info）；state accepted 55/117；closure-advance -> ZR-703。

- ZR-703 closure：reviewer-zr703-independent accepted（3 info）；state accepted 56/117；closure-advance -> ZR-704。

- ZR-704 实施完成：revenue 57e33f9（REV-05 validate-only 纯只读门 4 tests，产品零改动）；全量 494+106 绿；state triplet_green；implementer receipt canonical adb7958f；独立复核运行中。

- ZR-704 closure：reviewer-zr704-independent accepted（3 info）；state accepted 57/117；closure-advance -> ZR-505。

- ZR-705 实施完成：revenue bbee038（REV-06~08 draft/formal 分离 + 互换/重 hash 攻击门，2 个真实缺口修复 + 8 tests）；全量 502+106 绿；state triplet_green；implementer receipt canonical fafc80c6；独立复核运行中。

- ZR-705 closure：reviewer-zr705-independent accepted（3 info）；state accepted 58/117；closure-advance -> ZR-706。

- ZR-706 实施完成：revenue 8466b37（FC-904 selector 契约补全 10 tests，产品零改动）；全量 509+106 绿（fc1103 环境挂起登记）；state triplet_green；implementer receipt canonical de8892ab；独立复核运行中。

- ZR-706 closure：reviewer-zr706-independent accepted（3 info）；state accepted 59/117；closure-advance -> ZR-710。

- ZR-710 实施完成：revenue 3f81318（REV-09 原子写 + 事务故障注入 + 幂等，6 tests）；全量 515+106 绿；state triplet_green；implementer receipt canonical d4fd4220；独立复核运行中。

- ZR-710 closure：reviewer-zr710-independent accepted（3 info）；state accepted 60/117；closure-advance -> ZR-601；**F1 出口达成（ZR-701~706+710 7/7）**。

- ZR-601 实施完成：revenue 1d32047（F2 asset facts 契约 10 tests，产品零改动）；全量 525+106 绿；state triplet_green；implementer receipt canonical ccbc5616；独立复核运行中。

- ZR-601 closure：reviewer-zr601-independent accepted（26/26 对抗断言；1 minor docstring 3-period 标签 + 1 info 范围 diff）；state accepted 61/117；closure-advance -> ZR-602。

- ZR-602 实施完成：revenue cb82620（asset facts basis 契约：resource≠reserve 隔离钉死 + 加性 basis 键 fail-closed + 族内单位一致性门，15 tests）；全量 540+106 绿；state triplet_green；implementer receipt canonical 44b70d75；独立复核运行中。

- ZR-602 closure：reviewer-zr602-independent accepted（22/22 对抗断言；1 minor REV-001 unhashable ownership_basis → delta 修复 c9b0cfc + delta accepted；REV-001→info，REV-002~004 info）；state accepted 62/117；closure-advance -> ZR-603；**停止点：用户指示本卡跑完后更新全部 planning docs 后停止**。

- ZR-603 实施完成（2026-08-22 恢复）：revenue b52568b（ownership/consolidation timeline + geography 层级：effective-dated fraction 契约、链式一次连乘、apply-once 权益门、可检索地理索引，22 tests，+500 行 3 文件）；全量 567+106 绿；state triplet_green；implementer receipt canonical 36a7e343；独立复核运行中。

- ZR-603 closure：reviewer-zr603-independent changes_required（1 blocking REV-001 isinstance guard + 3 minor）→ delta 修复 03d716e + delta accepted；REV-001~004→info，REV-005 minor（container 形状硬化超出验收范围，登记 ZR-607 后续）；state accepted 63/117；closure-advance -> ZR-604。

- ZR-604 实施完成：revenue 2636e55（冲突保存与人工 review：双 assertion + resolution status，11 tests，+238 行 3 文件）；全量 585+106 绿；state triplet_green；implementer receipt canonical 58159699；独立复核运行中。

- ZR-604 closure：reviewer-zr604-independent accepted（17/17 对抗断言；1 minor REV-001 null resolution_status 语义不一致——非阻断）；state accepted 64/117；closure-advance -> ZR-610。

- ZR-610 实施完成（2026-08-22）：无产品代码改动——ADR 文档 adr_mining_accounting.md 覆盖 8 条会计决策（逐矿贡献=模型估计/resource≠reserve/basis 元数据/ownership timeline/单位一致性/冲突解决/地区层级/ADR 边界）；state triplet_green；implementer receipt canonical 5140ceed；独立会计 reviewer 运行中。

- ZR-610 closure：独立会计 reviewer accepted（8 条决策全部通过会计合理性审查，2 info 非阻断）；state accepted 65/117；closure-advance -> ZR-605。

- ZR-605 实施完成（2026-08-22）：revenue b02f17b（MineYearOperation 输入合同：七字段必填 gap-on-missing + derive_saleable_volume + resource 模型驱动映射，30 tests）；全量 615+106 绿；state triplet_green；implementer receipt canonical 3f780700；独立复核运行中。

- ZR-605 closure：reviewer-zr605-independent accepted（7/7 对抗断言组；1 minor REV-001 inf 值未拒——登记 ZR-606 后续 + 1 info）；state accepted 66/117；closure-advance -> ZR-606。

- ZR-606 实施完成（2026-08-22）：revenue cf3ada7（商业量价层：price/payability/TC-RC/premium/byproduct/FX/royalty 带 provenance，finite_number 数值加固（ZR-605 REV-001 落地），不重复计价，敏感性重算，24 tests）；全量 639+106 绿；state triplet_green；implementer receipt canonical 64f99205；独立复核运行中。

- ZR-606 closure：reviewer accepted（首轮 accepted → REV-001 minor delta 修复 47fe715 → delta 复审 staged-not-committed → commit 落地后 accepted）；REV-001→info，REV-002 minor implementer receipt 重封 + 2 info；state accepted 67/117；closure-advance -> ZR-607。

- ZR-607 实施完成（2026-08-22）：revenue 073fd4d（internal flow 会计桥：可追踪 InternalFlow + gross/net elimination 桥，29 tests）；全量 674+106 绿；state triplet_green；implementer receipt canonical 05c102fb；独立复核运行中。

- ZR-607 closure：reviewer-zr607-independent accepted（9/9 对抗断言组；零 blocking/minor，1 info）；state accepted 68/117；closure-advance -> ZR-608。

- ZR-608 实施完成（2026-08-22）：revenue 3081967（asset→segment→group reconciliation：容差门 + 诚实 fallback + 防伪收入，11 tests；注：ZR-607 closure 文件被合入本 commit——流程偏差记录）；全量 685+106 绿；state triplet_green；implementer receipt canonical d5497096；独立复核运行中。

- ZR-608 closure：reviewer-zr608-independent accepted（46/46 对抗断言；零 blocking，5 info/minor）；state accepted 69/117；closure-advance -> ZR-611。

- ZR-611 实施完成（2026-08-22）：revenue 288ac88（通用多矿合成 E2E：八类场景全链确定性可重算，test-only 11 tests 零产品改动；注：ZR-608 closure 文件被合入本 commit——流程偏差第二次）；全量 696+106 绿；state triplet_green；implementer receipt canonical 9667ac1c；独立复核运行中。

- ZR-611 closure：reviewer-zr611-independent accepted（独立数学重算 + 八类非空洞 + 确定性位级一致；1 minor + 5 info）；state accepted 70/117；closure-advance -> ZR-609。

- ZR-609 实施完成（2026-08-22）：revenue e541d55（紫金 pilot + 第二家泛化：三主要资产逐矿可回答 + 纯金矿商泛化零硬编码，test-only 9 tests 零产品改动；父 404a2bb = ZR-611 closure 独立落地——修正无第三次流程偏差）；全量 705+106 绿；state triplet_green；implementer receipt canonical ee6dd908（初版 f314d7d9 修正）；独立复核运行中。

- ZR-609 closure：reviewer-zr609-independent accepted（手算独立重算 + 25 项非空洞 + 零硬编码 tokenize 扫描；2 minor：REV-001 流程偏差记录有误已修正、REV-002 receipt 重封 ee6dd908 + 3 info）；state accepted 71/117；closure-advance -> ZR-711；**停止点：用户指示本阶段工作做完后更新全部 planning docs 后停止**。

- ZR-711 实施完成（2026-08-23）：revenue b0d7291 + delta e75debb（additive schema 3.8 opt-in：3.8 词汇+EMIT、版本门 {3.7,3.8}、validate_operating_units 复用 validate_mine_year_operation、schema_optin converter 三函数、15 tests，REV-001 capture-integrity gate 修复）；全量 720+106 绿；implementer receipt canonical f273d1ee（初版修正中）；独立复核 reviewer-zr711-independent delta 复审运行中。

- ZR-711 closure：reviewer changes_required（REV-001 blocking：capture-integrity 门只认 3.7）→ delta e75debb 修复 + delta accepted；REV-001→resolved，REV-002 minor 计数修正 + REV-003/004 info；state accepted 72/117；closure-advance -> ZR-707。

- ZR-707 实施完成（2026-08-23）：revenue fdb560e（mixed recognition/gross-net + multi-commodity product matrix：validate_mixed_recognition/validate_commodity_matrix/validate_presentation_consistency，13 tests）；全量 733+106 绿；state triplet_green；implementer receipt canonical 91aefa2c；独立复核运行中。

- ZR-707 closure：reviewer-zr707-independent accepted（11/11 对抗断言；4 info）；state accepted 73/117；closure-advance -> ZR-708。

- ZR-708 实施完成（2026-08-23）：revenue a9405f8（already_satisfied 重验：snapshot 不可变/accuracy→confidence 消费链/四层 hash，test-only 7 tests 零产品改动）；全量 740+106 绿；state triplet_green；implementer receipt canonical a9f5b356；独立复核运行中。

- ZR-708 closure：reviewer-zr708-independent accepted（对抗探针全过；4 info）；state accepted 74/117；closure-advance -> ZR-712。

- ZR-712 实施完成（2026-08-23）：revenue 2373c42（版本化 ConfidencePolicy + 反博弈：policy 数据化/六类 mutations 检测/rating caps 重算，15 tests）；全量 755+106 绿；state triplet_green；implementer receipt canonical fcc237aa；独立复核运行中。

- ZR-712 closure：reviewer-zr712-independent accepted（首轮 accepted → REV-001/002/004 minor delta 修复 1c04684 → delta accepted，REV-003 info 保留）；state accepted 75/117；closure-advance -> ZR-713；**docs 一致性修复：补 ZR-608/ZR-611/ZR-708 缺失 findings 条目 + ZR-709 合流卡提及**。

- ZR-713 实施完成（2026-08-23）：revenue cb34700（rolling-origin 引擎：严格 as-of 泄漏 fail-closed、company/segment/mine-volume 三层、四层 immutable hash、cap 不伪造 metrics，10 tests）；全量 768+106 绿；state triplet_green；implementer receipt canonical 57c1d269；独立复核运行中。

- ZR-713 closure：reviewer-zr713-independent 首轮 changes_required（REV-001 blocking 三层 byte-identical 非独立评估——segment 层发 company wape、mine-volume 未用 ZR-605 契约；REV-002 minor level/as_of 未绑 hash 链）→ delta 3479718 修复（segment 独立 wape、mine-volume 走 ZR-605 契约 fail-closed、record_sha256 绑定 {level,as_of}、snapshot_id=快照身份；15 tests，全量 773+106，pre-commit 776+106 + E2E PASS）→ delta accepted（21/21 探针）；implementer receipt 重封 f71fdf5f、reviewer receipt canonical 8125837d；state accepted 76/117；closure-advance -> ZR-709（F2 合流卡——F2 常规链全闭，仅剩 ZR-709 合流终验）。

- ZR-709 实施完成（2026-08-23）：revenue ac68807（F2 合流终验 fixture，test-only +919 行 1 文件 9 tests 产品零改动）——J1 真实 source_preparation 子进程链复用年报+研究沟通（reuse_receipt 可解释、缺失 kind fail-closed + ProcessingDemand 补齐）；J2 五年 FY2026-2030 输入由契约函数代数推导、mine 贡献×segment reconcile 10/10 闭合、白银 +120=诚实 gap、3.8 operating_units 嵌入零漂移；J3 draft 渲染零注册、formal 位级重放 + snapshot 回放。全量 782+106 零回归；ruff 0；sync MATCH 147；implementer receipt canonical 134a2b13。

- ZR-709 closure：reviewer-zr709-independent accepted（干净 checkout ac68807：产品 diff=0、全量复放 782+106、12/12 对抗探针含手算位精确与伪造价格→gap、无空断言、硬编码零新增、hash 全对；4 info 无阻断）；reviewer receipt canonical 40206902；closure receipt state_sha 73e10e70/control 102b02f4；**state accepted 77/117（F 24/24 全闭）**；phase->G_real_e2e；closure-advance -> **ZR-802**（README §6 阶段 G 首卡，ZR-801 已由 CA-105 吸收）。

- ZR-802 实施完成（2026-08-23）：revenue 1b55f6f（阶段 G 首卡组合旅程，test-only +353 行 1 文件 7 tests 产品零改动）——五状态×跨根：existing exact 复用（dl=0/llm=0/outcome=reused_existing）、missing 结构化 not_found 且 lake 计数不变式（零写入零伪造）、future-dated stale 拒绝不污染既有复用、跨根双候选 ambiguous fail-closed 不择一、partial 角色读子集+DAG 最小生产闭包；C2 二次调用幂等同身份零下载；C3 八阶段证据投影按真实键钉死。全量 789+106 零回归；ruff 0；sync MATCH 148；implementer receipt canonical 6a1c6869。

- ZR-802 closure：reviewer-zr802-independent accepted（11 探针 V1-V7：diff=test-only、全量复放 789+106、8/8 独立反伪造探针、硬编码零命中、hash 全对；1 minor REV-001 parser>=1 vs 精确预算属上游信封内部计数登记后续、3 info）；reviewer receipt canonical 051e4f64；**state accepted 78/117**；closure-advance -> **ZR-803**。
