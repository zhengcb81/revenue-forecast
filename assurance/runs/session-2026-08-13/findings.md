# 研究发现（Session 工作记忆）

## 发现 1：项目控制面与现状
- 日期：2026-08-13
- 内容：`audit_review/README.md` 是唯一执行入口；`current_next=CA-001`；机器状态 `assurance/unified_completion/state.json` 尚不存在（not_started）。
- 旧账本 66/71 在严格 current-triplet 口径下为 0/71；R9 强门 4/4 RED。117 工作单元（92 ZR + 25 CA）、197 场景、T0–T4 分层，自然时间门不可豁免。
- 影响：一切从 CA-001 开始；不得从旧计划或看似简单的 ZR 起步。

## 发现 2：启动前机械检查全部通过
- 30 输入快照 hash（程序化解析 input_snapshot.md）全部匹配；8 冻结 annex hash 全部匹配。
- 三仓 HEAD 与审计截面一致，均在 fcap 分支；有 GitHub origin 但未设 upstream 跟踪。
- dirty：revenue 8（audit_review 内 3 个修改 + 5 个未跟踪目录）、filing 0、wiki 4。
- 影响：基线干净，可以领取 CA-001。

## 发现 3：旧工具无锁无 CAS
- `tools/closure_ledger.py` 输出用 `write_text` 直接覆盖；`tools/closure_gate.py` 用子串判断 accepted，无 hash 校验。
- 无任何 lock/CAS/manifest 校验机制（grep tools/ 确认）。
- 影响：CA-001 RED 基于真实旧工具演示成功（RED-A/B 归档 receipts/CA-001/red/）。

## 发现 4：ZR 注册表格式
- ZR 是表格格式（`| ZR-306 | owner | 依赖 | 目标 | 证据 |`），依赖列有 无/逗号列表/区间（ZR-101~104）三种形态；**ZR-1001~1105 是 4 位编号**。
- CA 注册表是标题格式（`### CA-001` + `- 依赖：`）。
- 影响：dag.py 双格式解析 + 区间展开；真实解析 25 CA + 92 ZR。

## 发现 5：Windows 文件系统语义（重要）
- `read_text` 句柄无 FILE_SHARE_DELETE：并发 rename/unlink 抛 WinError 32。
- 重试循环必须按代际守卫：盲目重试 rename 会把对端刚发布的新锁搬走（曾造成破锁"双赢"）。
- 影响：casfile/lock 全部写路径实现有界重试 + 内容 hash 条件操作。

## 发现 6：pre-commit 钩子
- `.githooks/pre-commit` 跑全仓 pytest + 引擎 E2E + sync_installations（bash），提交需数分钟。
- 影响：本地 commit 用后台任务 + 长超时。

## 发现 7：真实仓库 manifest 结构
- 合并去重后 44 个冻结输入条目：README §13(8) ∪ 快照(30) ∪ 内容(14)，annex(5) 已含于前两者。
- 真实 manifest-verify 通过（含 30 个 mtime 校验）。

## 发现 8：CA-002 环境冻结预研（只读收集）
- 日期：2026-08-13
- 工具链：Python 3.13.9 / git 2.51.2.windows.1 / Node v24.11.0 / SQLite 3.51.0。
- OS：Windows NT 10.0.26200.0（单机实施环境；Linux 属产品测试目标，非本机变量）。
- 三仓 fcap 均无 upstream 跟踪（origin 存在：github.com/zhengcb81/*）；dirty 8/0/4（与审计一致）。
- 已安装 skills：21 个。
- 影响：CA-002 需机器化：精确 triplet equality gate、upstream/remote-base 区分、dirty allowlist、toolchain/OS/skills 指纹、config/policy/catalog fingerprint；发布资格区分 local-only 与已推送。

## 发现 9：冻结输入的可复现性缺口（closure 干跑暴露，给 CA-002/CA-004 的 successor 线索）
- 日期：2026-08-13
- 缺口 1（行尾）：git 默认 checkout 将跟踪文件转 CRLF，与冻结 LF 字节 hash 不符 → 干净复核必须 `git -c core.autocrlf=false clone`。
- 缺口 2（未提交/脏树）：`audit_review/README.md` 与两个 2026-08-13 计划目录未跟踪；旧 FCAP 的 findings/progress/task_plan/work_unit_registry.md 工作树内容≠已提交内容 → 干净复核必须从原工作树整体复制 `audit_review/`（Copy-Item 保留 mtime）。
- 缺口 3（mtime 不可复现）：git checkout 重置 mtime → 新增 `--mtime off` 模式（hash+size 仍强制），严格模式保留为原工作树防篡改门（commit 4d629b9）。
- 验证：throwaway clone（autocrlf=false + 整体复制 audit_review）→ manifest-verify 严格模式 OK → state-update/closure-advance 重放 rc=0 → closure 后 verify 仍 OK → current_next=CA-002。README 无 BOM，补丁字节安全。
- 影响：CA-002 冻结 triplet 时须把"冻结输入已提交且可复现"作为环境清单的一部分；CA-004 处置旧计划时引用这些缺口。

## 发现 10：CA-003 CodeGraph 预研（只读）
- 日期：2026-08-13
- 每仓 `.codegraph/`：codegraph.db（SQLite+WAL）、config.json（include/exclude 模式，含 py/ts/js 等）。
- CLI：`C:\Users\郑曾波\nodejs\codegraph.ps1`（@colbymchenry/codegraph）：init/index/sync/status/query/files/context/serve/unlock/affected。
- 当前 4 个 `codegraph serve --mcp` 进程在跑（读服务，非索引写入者）；CA-003 独占窗口需避开其它 index writer（README 已授权三目录重跑）。
- revenue 当前索引：171 files / 2,977 nodes / 4,978 edges / python-only，status 报 "Index is up to date"。
- 影响：CA-003 用 `index`（独占）+ `status` 验证 indexed commit 精确等于 CA-002 HEAD；为核心用户旅程生成 caller 报告；runtime_policy=None 回退等旁路登记为阻断 finding。

## 发现 11：CA-003 必查旁路证据（只读预研，供 RED 使用）
- SourceResolver.__init__（wiki src\company_wiki\source_catalog\resolver.py:633）：runtime_policy: dict | None = None（可选回退）。
- 生产调用缺省构造（不传 policy）：acquisition.py:308/396、canonical_writer.py:157/205、close_gap.py:403；仅 cli.py:1004 显式传 policy。
- 结论：同一请求 resolve 走 v2、ensure/close-gap 回 v1 的旁路结构真实存在 → CA-003 production caller 报告必须登记为阻断 finding。
- codegraph project_metadata 表为空；indexed commit 的持久化位置待 CA-003 用 index/status 实测确定。

## 发现 12：CA-003 caller 报告目标定位（只读）
- CatalogStore：wiki src\company_wiki\source_catalog\store.py:920
- v1 scanner：wiki src\company_wiki\source_catalog\scanner.py:272/1374 + shadow_parity.py
- artifact bindings/backfill：wiki src\company_wiki\source_catalog\artifact_backfill.py:28/54/277/285
- filing handle validation：filing scripts\fetch_filing.py:752/757/883 + scripts\filing_contracts.py:350
- publication registry：revenue scripts\publication_registry.py:30
- source preparation：revenue scripts\revenue_core.py:177（prepare_forecast 相关）
- dynamic runners：revenue tools\*.py（closure_gate/ledger、daily_t2_runner、weekly_t3_runner、slo_probe 等）
- ProcessingDemand：wiki 中未发现独立类（与审计"ProcessingDemand尚不存在"一致）→ CA-003 报告需登记为缺失。

## 发现 13：ZR-001 复核暴露的伪 sha 与证据密封耦合（2026-08-14）
- 第三次伪 sha：reviewer 简报手写 9db69d7d9e…（真实 9db69d7d58f…）；receipt 本身已用 git rev-parse 真实值（result_triplet=7afcb965d190e27083c774ba3ff8e0a1b37b7653 通过 receipt-validate 的 git-object 检查）。
- 证据密封耦合：reviewer 原地重放会覆盖 sealed evidence（observed_at_utc/临时路径/真实 catalog 指纹随时间变化）→ 三 replay 脚本增加 --evidence-dir，重放写临时目录；sealed evidence 只读。ledger 重建为 2a80f744…（frozen_at_utc 固定 + builder --verify 保证字节确定性）。
- 教训：任何交给子代理的 sha 必须来自 git rev-parse 输出；重放类脚本必须支持输出目录隔离。

## 发现 14：ZR-002/004 共享证据映射（README §7，A0 收尾用）
- ZR-002（command/scenario/receipt schema 冻结、计划写锁、shared-resource lock）→ 全部由 CA 链实现：command attestation=CA-104、scenario registry hash=CA-105、receipt schema=CA-102、计划写锁/CAS=CA-001、per-unit 单 writer 锁=CA-101。关闭方式：already_satisfied receipt 引用 CA-102/104/105 + CA-001/101，独立 reviewer accepted。
- ZR-004（旧全面计划每项只读处置）→ CA-004 legacy disposition（71 FC、I=31/C=26/S=9/P=5、legacy_disposition.json sha 22b88123…）。同上 already_satisfied 关闭。
- ZR-003 golden corpus 样本全部在机：年报 PDF×2（companies 紫金矿业/raw）、7 份研报 PDF（Dropbox 金属及加工/有色金属/紫金矿业/，含 20240304 长江多实体对比）、错误 strategy HTML（audit sources/2026_strategy.html，hash b2d215df… 复核一致）、预测 input/result（audit outputs/input_v1.json + draft_result.json）。

## 发现 15：ZR-201~203 真只读落地中的关键修复（2026-08-14）
- SQLite WAL 读协议在 side 文件缺失时创建空 -wal/-shm（-shm 固定 32KiB 头）——reader 零写（数据文件字节不变、无 committed frames），生产 catalog 由 writer 维护 side 文件故无影响（ZR201-IMPL-001）。
- reader 只读连接跨线程共享（concurrency single-flight 测试触发）→ check_same_thread=False 对 mode=ro+query_only 安全（无事务状态）。
- 写流程此前依赖 resolver 的 store 构造隐式创建空 catalog；重接后 writer initializer 显式化到 AcquisitionCoordinator/CloseGapTransaction/CLI ensure+close-gap（语义零变化，仅时序显式）。
- SourceCatalog.close() 释放缓存 reader 连接——Windows 临时目录清理（fc1105 f6 的 WinError 32）。
- 3 个既有测试的 SQL 捕获接缝 store→reader（resolver_sql_perf/semantic_duplicates/pipeline bulk-query），断言本体未放宽。

## 发现 16：ZR-204 错误发射契约变更与停止点（2026-08-14）
- wiki CLI 顶层 + identity_cli 两处错误发射从 `type(exc).__name__` 统一为 canonical code + retryable（fatal 对非锁错误）。
- 受影响 contract 测试 7 处断言改 canonical 码（evidence_query/extraction_quality/focus_cleanup/security_identity×3/paused_guard×2）；complexity ratchet 要求分类器表驱动（16→≤10）。
- 恢复清单见 progress.md「2026-08-14 23:30 用户 STOP」节；ZR-204 的 revenue 侧 receipt/复核/closure 未做。

## 发现 17：ZR-204/ZR-205 复核与 closure（2026-08-16）
- ZR-204 accepted：独立复核 7 项全过（矩阵 7 形态、双 CLI 发射点、15 单测、受影响 contract 3 失败均为已知既有、receipt/state 校验）。error_type 从异常类名→canonical 码是跨消费方契约变更（ZR204-IMPL-001），filing N-1 类名映射仅服务旧 wiki。
- ZR-205 accepted（1 条 low 措辞 finding）：ZR205-REV-002 指出 IMPL-002 误把 OperationalError 文本映射归因到 filing——实际该映射在 wiki 侧 classify_error_type，filing 只直通 canonical 码 + 类名 N-1；端到端 raw lock 仍 retryable（无行为缺口），IMPL-002 措辞已修正重签（canonical 446f66ba→9a4b1775）。
- ZR102-F2 filing 侧根因关闭（ZR205-IMPL-002）；ZR102-F1 移交 ZR-407（ZR205-IMPL-003，原 successor=ZR-205 修正为阶段 D authorization-bound GapPlan）。
- 信封契约扩展（READ-09/10）：成功带 calls/downloads，失败带 stage/attempts/calls/downloads；additive，revenue client 按 key 读取不受影响。
## 发现 18：ZR-206 真实 49GB catalog 基线（2026-08-16，T2 只读实测）
- 真实 catalog 49.62GB / schema 1.2.0 / evidence_spans 27,178,657 行——'49GB 级'是真实规模，不是合成近似。
- status()/health() p95≈8.0s（27.2M 行 COUNT 走 COVERING INDEX idx_spans_document，EXPLAIN 确认无 Python 全表扫描）——冻结门 12000ms；其余 typed 查询 p95≤33ms（query 1.8ms / entities_like 0.6ms / location_counts 33ms / document 级 ≤0.3ms）。
- 内存冻结门 256MB（tracemalloc 峰值，counts 只物化 8 个 int）；50 并发 resolve 无 deadlock/下载/串线（每请求独立 reader 连接——生产模型是每 CLI 请求独立子进程/连接；共享连接并发会触发 sqlite3 InterfaceError，故测试按生产模型写）。
- 零写指纹：WAL/SHM 已存在（live 前置条件）时读会话前后 DB/WAL/SHM/目录逐字节一致；reader 文档明示 '缺 side 文件时可能创建空 -wal/-shm'，hermetic twin 以保持 writer 连接模拟 live 状态。

## 发现 19：阶段 D ZR-301~305（2026-08-17）
- ZR-301（readiness 求值器）：八阶段 shadow 求值 + ConsumerRequirements fail-closed；unknown 永不满足（无 safety receipt 不绿）。
- ZR-302（prompt-injection guard）：独立 producer 缓存生命周期 hit/ignored/expired/tampered/absent；not_reviewed 不伪绿；首轮复核抓出 mypy 注解回归（REV-001）+ malformed→absent 措辞（REV-002）+ TTL 边界测试缺（REV-003），全修正后 accepted——教训：新 helper 的 mypy 注解要一次到位，卡片矩阵措辞要与实现逐字对齐。
- ZR-303（统一决策图）：safety 阶段由 guard 缓存判定驱动（hit→satisfied；其余→blocker+next action）；blocker→next_action 完备（无死路）；纯函数确定性。
- ZR-304（producer journal + artifact read model）：失败无 artifact 也有 attempt（独立 producer_attempts 表，不改冻结触发器）；calls_this_request 与历史严格分离；read model 归一 bindings 优先/legacy 回退/source SHA mandatory/未知 role fail-closed；复核 REV-001 提示 KNOWN_ARTIFACT_ROLES 与冻结 source_bundle 不一致 → 改 import 单一真源。
- ZR-305（legacy 五桶迁移验收）：FC-901 机制已实现，本卡纯验收钉死端到端证据（五桶守恒、dry-run 确定性、apply→真实 SourceBundle 命中、幂等、不删、可逆）。

## 发现 20：ZR-305/306（2026-08-17 阶段收尾）
- ZR-305 纯验收：FC-901 五桶机制已实现，端到端证据钉死（桶守恒、dry-run 确定性、apply→真实 SourceBundle 命中、幂等、不删、可逆）。
- ZR-306 property tests：artifact_dag（WU-803）失效语义验证——document_hash 全失效；producer-key 变更=传递下游闭包；缺失子树只重算依赖；幂等+手工闭包对照；DAG 无环；PRODUCER_KEYS 含 prompt/model/config hash。
- 教训：并发 commit 竞争再次发生（ZR-304 closure 与 ZR-305 receipt 合并进同一 commit，消息误导）——已 amend 修正；今后 closure 与下一卡 receipt 的 revenue commit 需串行提交。

## 发现 21：ZR-401 RootPolicy 3.0 复核（2026-08-18 收尾）
- ZR-401（RootPolicy 3.0 严格加载器）独立复核 accepted，5 条 findings 全部非阻断：
  - **REV-001（minor）**：`privacy_class` "required, no default" 对 company_raw 不字面成立——缺省时走 2.x 默认 public 隐式加载（policy_2x.py:151 默认值先落属性，3.0 门读已默认化的属性）；external-root 缺省与显式 null 均拒绝。无权限扩大（public 是 company_raw 唯一合法值），"无隐式默认扩大权限"证据成立。建议后续在原始 YAML 上加显式在场检查（可并入 ZR-402/403 或授权卡）。
  - **REV-002（info）**：contract 计数过报——receipt 记 "43 passed"，真实 28 passed + 1 skipped（同一命令 HEAD 复跑）。无测试失败。
  - **REV-003（info，需显式决策）**：生产 config.py 未切 3.0 loader（HEAD 零 diff），receipt 已披露延期（ZR-402/403 或阶段 D 出口切换，回滚纪律保持）。**coordinator 显式决策已记录**：卡片验收标准为条件性（"生产 config 加载切换到 3.0 loader"），本卡 closure 时视为已记录偏差接受延期，切换工作并入 ZR-402/403（adapter registry/dedupe 落地后），届时以 contract 测试钉死切换。
  - **REV-004（info）**：mypy 在 wiki venv 缺失，用 base python mypy 1.19.0；reviewer 未改任何 tracked 文件（仅测试产物 .coverage/coverage.json）。
  - **REV-005（info）**：receipt plan_sha256=861e28f9… 与当前 00_wu_card.md hash 4d36301f… 不符——卡片在计划冻结后更新过（claim 时间戳更新所致），冻结计划 hash 引用的是冻结时卡片。
- 实施要点（供后续卡参考）：3.0 严格加载器 = schema 门（1.x/2.x 拒绝并给迁移提示，绝不静默升级）+ 共享 2.x 表面（yaml_schema_version='3.0'）+ external→private_user / company_raw→public 强制 + external 写目标/未知字段/非只读复用 fail closed + 版本化导出（隐私脱敏 ${PROJECT_ROOT}/ token + 确定性 sha256）+ McCabe max 8 ≤ 10。
- 教训：卡片措辞与实现逐字对齐的重要性再次验证（REV-001/002 均属"措辞 vs 实现/实测"类）；reviewer receipt 的 canonical hash 97e562bd… 独立重算一致。

## 发现 22：ZR-402~406 阶段 D 中段（2026-08-18 收官）
- **ZR-402（adapter 路由契约）**：RED 探针证三幸存突变体——S2 kind 路由突变体在现有断言下存活（canonical 配对只测同配）、S3 conformance determinism 无负例、S4 路由五模块零 kind 分支无机械门（FC-1201 是 token-mention ratchet 且 adapter_dispatch/admission 在 allowlist 内=盲区）；S1 诚实负例（facade 失败封闭已被 seam02+ex08×2 完整钉死，不重复造）。M8 kind 路由/ M9 facade 回退等突变体以进程内重放 kill 证明钉死。
- **ZR-403（dedupe/resolver 泛化）**：`_annotate_locations` 结构上 health 先于 priority（active 过滤后再按 (root_priority, root_id, relative_path, location_id) 排序），但无 killer——本卡以 retired/.rejections 高优先级竞争测试钉死；locations 表无 is_canonical 列（canonical 纯读时派生）由 PRAGMA 断言钉死。future_lake 进入四上下文矩阵（同字节四根=恰一 document）。
- **ZR-404（envelope 加性）**：跨仓契约要点——envelope_schema_version 保持 "1.0"，新字段纯加性，filing validate_resolution_envelope 对未知键宽容（跨仓透传测试直接加载 filing_contracts.py 验证）；policy_snapshot 严格形状（policy_hash 64-hex/current_epoch 文本/active_cohorts str-list，违者 ValueError）与 filing 校验器逐字同规则；路径脱敏 ${PROJECT_ROOT}/${USER_PROFILE} token。mypy 基线 2 条既有错误（resolver.py list()/assertion arg）继承，移交后续质量卡。
- **ZR-405（跨仓 policy containment，本段最大设计教训）**：初版方案（filing 每请求额外 subprocess 调 policy-export）导致 89 个既有 subprocess mock 测试失败——**改为 wiki resolve/ensure 响应内嵌 `policy_export`（零额外调用）后既有测试零改动通过**。第二个坑：policy hash 契约——validate_handle 原对整个 snapshot dict（含 policy_hash 键）重算 hash 与 wiki canonical 永不相等；修正为对 policy DOCUMENT 计算（排除 policy_hash 键，与 uc canonical_hash 纪律一致）。第三个坑：token 化 path_ref 破坏字节级 hash 契约——export payload 必须 verbatim（绝对路径，本地通道可信）。第四个坑：1.x 最小配置 per-root reusable_for_filing=None 使 export 全 None → filing 拒绝一切 handle——两个 exporter 归一化为 resolver-consistent effective reusable（kind ∈ reusable_root_kinds 缺省）。
- **ZR-406（gap-plan 矩阵）**：首轮复核 changes_required 暴露两处 claim 不实——"13 tests" 实为 12（pytest collect 计数必须实跑后写）；"5×6 全格" 实为 24/30（5 格缺失）。修正为真·数据驱动 itertools.product 30 格参数化 + cells-distinct 完备性守卫 + 全 30 格 hash 确定性/区分度 → delta accepted。语义澄清：newer_revision 列在无可用 local 时为 genuine missing；unusable local（capture_ready=False）过滤后 provider 同周期列表为真缺失（不伪绿）。capture_ready 防御过滤须在所有结局分支一致（含 provider_error 早退）——首版漏了早退分支，测试当场抓出。
- **综合教训**：① claim 计数一律实跑后写（第二次 count overclaim 被 reviewer 抓出，ZR401-REV-002 → ZR406-REV-001）；② 跨仓契约设计先查既有 mock/测试面（subprocess 方案 89 失败教训）；③ 字节级 hash 契约禁止 payload 重塑（token 化/字段裁剪都会破坏）；④ 防御过滤要覆盖全部早退分支；⑤ 复杂度 ratchet 维护用 helper 提取（cli.py 140、gap_plan 20 两处）。

## 发现 23：ZR-407/408 阶段 D 尾段（2026-08-18 晚）
- **ZR-407（authorization-bound close-gap actionable union）**：RED 为两侧只认 `missing` 为 actionable——newer_revision-only 授权计划在 filing 侧 3 次子进程后仍返回结构化 gap（未调 close-gap）、在 wiki 侧以 fetch_events=0 误终为 reused。修复：wiki `_actionable_candidates` = missing ∪ newer_revision（外锁/内锁重验与 staging 候选选择统一，plan hash 绑定该有序集）；filing `_gap_plan_has_actionable_candidate` 同语义。owner 修复（用户明确授权）：exact/no-download `ensure` 走 reader 返回 attempt=null，不触 writer initializer/journal（real-tool conformance 的只读生产 catalog 入口语义冲突），`_run_ensure_command` 抽取保持 cli.py ratchet。三仓产物先前 accepted 但未提交——本会话补提交（wiki bdffc54、filing 5a1c18f、revenue 6145dad）。
- **ZR-408（CloseGap staging→validate→canonical commit/recovery 验收，产品零改动）**：复跑 FC-801/FC-804/canonical-writer 未定位产品 RED（staging 校验失败不提交+清理、canonical 仅 companies/、re-resolve/idempotence、线程 single-flight、retry/failure journal 均已覆盖）；唯一证据缺口=single-flight 仅同进程线程。补强 Windows spawn 双进程 oracle：两 child 各自重建 catalog/coordinator/writer 共享 temp root+binding，adapter append-only fetch log 恰一条、fetch_events=[0,1]、documents=1——现有 `_acquisition_mutex` 文件锁被进程级验证。22 contract + 787 unit 绿；复核 accepted（3 info）→ closure→ZR-409。
- **教训（新增）**：⑥ receipt result_triplet 手写 sha 再次出错（71aa798d31… 非真实对象，真实 71aa798eb4…）——所有 64-hex 值必须 git rev-parse/Get-FileHash 注入（第 8 次伪 sha 类事件）；⑦ pre-commit skill-sync 检查要求 sync 在 filing 仓库 CWD 运行（在 revenue CWD 跑 `tools/sync_installs_b3.py` 路径失败并被 pre-commit 拦截）；⑧ 并发跑多个重 pytest 进程会让既有线程级 single-flight 测试 flake（SQLite InterfaceError，单跑绿，非回归）；⑨ 跨会话遗留进程（PID 20528）需先确认退出再清理其临时目录（Windows Access denied 教训）。

## 发现 24：阶段 D 出口 ZR-409（2026-08-19）
- **future_lake 仅配置接入**：生产 config 第四根（directory+sidecar_filing_v1+read_only+reusable+p40，path=${PROJECT_ROOT}/future_lake）+ 仓库内 fixture 目录——EX-08 生产版；产品 src diff=0（`git diff -- src/` 空），由 git 证据钉死。
- **三真实 root 只读旅程**：(a) companies 紫金 601899/2025 exact；(b) dayu-only 金斯瑞 HK1548/2021（内容 72b3ed25… companies 零 location——前提测试钉死，满足 exec plan"dayu 独有样本不得用 companies 副本冒充"）；(c) Dropbox 星环 688031/2024 **fail-closed**（source_url http 非 https → capture_incomplete → MISSING + download_required）——生产数据诚实现状（Dropbox 独有 annual 378 内容中 53 独有，2 http + 51 无 URL，无一 capture-ready；325 与 companies 共享）。紫金跨根共享 canonical=companies（p10<p30，ZR-403 语义在生产数据上复现）。
- **零写证据口径修正**：真实根浅指纹（top-level 列表）+ 样本文件 (size,mtime,sha256)；**catalog-DIR 指纹不用于断言**——后台 worker 并发写真实 catalog（ZR-206 fingerprint_identical=false 教训在真实环境再次成立）；full rglob 指纹在 49GB 根上会超时（首次实现即超时，改用浅指纹）。
- **场景映射方法论**：EX/LT/DL/IDX/UJ 44 场景→既有测试映射表写入 receipt（EX-01~08、LT-01~10、DL-01~03/07~10、IDX-01~08、UJ-01/02/04/06/07 已实现；DL-04~06/UJ-03/05/08 等 T3 移交 ZR-802/806）——避免"已有测试"冒充"场景全绿"。
- **教训**：⑩ 真实根旅程的请求构造以 catalog 实际元数据为准（form_type='FY' 非 'annual_report'、entity 用真实公司名金斯瑞非臆断、URL scheme 决定 capture_ready）——样本选择凭外部知识会连环失败（金风科技→金斯瑞、form_type 过滤、http 样本）；⑪ 只读旅程测试要区分"产品缺陷"与"数据现状"（Dropbox http URL 是数据现状，resolver fail-closed 是正确行为，测试钉死 fail-closed 并登记 finding 而非改产品）。

## 发现 25：ZR-502 首页身份验证（2026-08-19）
- 判定信号演进：token 交集（CJK 无空格零命中误判 contradiction）→ 4-gram 滑窗（通用片段假阳性：foreign cover 的'股份有限公司/年度报告'交叠误判 consistent）→ **归一化子串包含**（declared 值整体 in page_norm；长名称精确、短值（publisher/security_id）同样适用；'…摘要' 页 vs declared title 子串命中 consistent）。
- published_date 链路：company_raw sidecar 契约键 = filing_date（dayu acquisition 契约），scanner 只认 filing_date；sidecar_filing_v1 补 published_at->filing_date 显式映射（非文件名猜测，F-043 合规）；缺 date 的 sidecar 在 resolver 走 published_date_unknown -> AMBIGUOUS（fail-closed 而非误复用）。
- 封闭词汇扩展：新 quality_flag / evidence reason 必须注册 QualityFlag 枚举 + observability REASONS/STAGES_BY_REASON（fc1301 taxonomy gate 自动捕获未注册码——本卡 3 个 reason 码被 gate 当场抓出）；homepage_identity_contradiction 仅进 frontmatter（review 信号），artifact metadata flags 保持 parser 原始集（两通道不混淆）。
- _frontmatter document 双形态：normalize_catalog 传 sqlite3.Row（metadata_json 为 JSON 字符串列，需 json.loads + 下标访问），测试 fixture 传 dict——.get/.下标 混用即 AttributeError/KeyError（本卡 3 次修复迭代：.get on Row -> 下标 on dict-missing-key -> isinstance 分支 + json.loads）。
- 既有基线失败登记：corrupt pdf/xls（fitz 分类）、dropbox_config_invariants×2（ZR-409 future_lake 使 directory-kind 集合含 future_lake，测试期望 {dropbox_stock} 漂移）、security_identity×2（stale_cache 环境态）、worker_bootstrap×1（时序）、integration×3（fitz）、pipeline/extraction_quality（meeting.html 子进程 parser 失败走 _failed -> 'parser_failed' 未注册 QualityFlag——既有缺陷，stash 基线对照证非本卡引入）。
## 发现 26：ZR-701（F1 入口，2026-08-19）
- validate-only 零写是真实产品缺口：run_forecast(mode="formal") 自动 register_publication（revenue_core.py:180）——validate-only 也触发注册写盘（c2 测试抓出）。修复：prepare_forecast(mode="draft") 强验证 + build_draft_receipt + 零注册；draft receipt 与 validate_forecast_output 不兼容（后者要求 formal_output_mode=formal）→ 仅 formal 跑输出校验。
- 复杂度 ratchet 教训：prepare_source 的 or 链 BoolOp + if 块 +4 复杂度（17→21）破坏 FC-1204-b 冻结 gate——helper 提取（_demand_key cc4 + _submit_preparation_demand cc2）回 17；reviewer 用干净父提交对照组证实父绿子红归属本卡。scripts 产品改动必须跑 tools/tests/test_complexity_ratchet.py。
- skill-sync 前置：scripts 产品代码改动后 pre-commit R4.2 拦截 commit——tools/sync_installations.py --apply 必须先跑。
- draft/validated 显式 artifact：publication_registry validation_status 加性键（旧条目无键可读）；formal 条目 receipt_sha256+result_sha256 绑定（原子发布）。
- ProcessingDemand 跨仓同契约：revenue scripts/processing_demand.py 独立实现（wiki ZR-507 语义），零跨仓 import；prepare_source 成功 enqueue（key=source_id dedupe）。
- mypy 基线：publication_registry.py:215 audit() tuple 类型错误为既有（非本卡引入）。

## 发现 27：ZR-601（F2 首卡 asset facts，2026-08-20）
- 机制探针正确（非负强制/缺省 fail-closed/公式手算已实现）→ test-only 卡：10 tests 钉死 stock-flow 平衡/连续性/非负、缺省矩阵 fail-closed、MODEL_SPECS 公式与 required/formula 词汇。
- 测试陷阱（后续 F2 卡参考）：① YEARS 2 期时 3 期驱动样本不会被计算——不平衡探针需 2 期自身触发；② 连续性破坏样本必须同时保持 balance（opening[1]=closing[0] 同步改），否则探针误报为平衡错误而非连续性错误；③ recovery_rate 是 ratio_driver——负值报 "cannot be negative" 而 >1 报 "must be between 0 and 1"，断言消息需按 driver 类型区分；④ MODEL_SPECS 是 mappingproxy——测试用下标访问，勿用 .get()。
- reviewer 1 minor：docstring 说 "3-period" 实为 2-period（cosmetic，未改产品）；closure 后 F2 计数 8/13。

## 发现 28：ZR-602（F2 第二卡 asset facts basis 契约，2026-08-21）
- 探针三缺口：P1 resource≠reserve 语义隔离机制已存在（segments.py `unsupported drivers` 拒绝跨模型驱动注入）→ test-only 钉死；P2 basis 元数据全仓零词汇（ownership_basis/reporting_standard/measurement_date）→ **真实产品缺口**；P3 unit 无一致性门 → 真实缺口（基础版）。
- **basis 设计为加性声明契约**：参数携带 `basis` 键时必须完整合法（ownership_basis ∈ {one_hundred_percent, equity_share, consolidated}、reporting_standard 非空、measurement_date ISO），半成品 fail-closed；缺省（无 basis）兼容既有——golden/industry e2e 全链路零破坏（全量 540+106 绿实证）。全量必填接入点留给 ZR-605/610。
- **单位一致性按维度分组**：MODEL_DRIVER_DIMENSIONS 同维度驱动 unit 归一化（strip+lower）后必须一致——kt-vs-t 跨驱动/跨期漂移拒绝；换算表不实现（ZR-610 ADR 范围）。resource/reserve 共享 realized_price/other_revenue 是合法跨族通用驱动；族特异词汇（saleable_volume vs opening_reserves/additions/depletion/closing_reserves/recovery_rate）不相交。
- **ratchet 两次触发教训**：加性校验仍会推高主函数 McCabe——document.py 内联 basis 块 33>32 → 提取 validate_parameter_basis（None 早退 + .get() 接线）；segments.py 内联 unit 门 17>15 → 提取 _check_asset_fact_unit_consistency。新校验一律 helper 提取。
- 零产品硬编码：ASSET_FACT_MODELS/枚举均为通用矿业词汇（zijin 不在集合）。
- **REV-001 修复（delta c9b0cfc）**：`basis["ownership_basis"] in 枚举` 对 unhashable 值（list/dict）抛 TypeError 而非 ForecastInputError——require 条件加 isinstance(str) guard 后统一 ForecastInputError，+5 参数化回归测试（20 passed）。教训：成员测试前先类型守卫，契约异常类型必须统一。

## 发现 29：ZR-603（F2 第三卡 ownership timeline 与地区层级，2026-08-22）
- 探针词汇陷阱：`consolidated_forecast`（场景合并）、`segment_attribution`（驱动归因）、`equity_share`（ZR-602 枚举值）都是**无关同名**——grep 命中≠机制存在，需逐个看语义再判定缺口。
- ownership timeline 契约设计：lookup 取最新 effective_date ≤ on_date；早于首条目 fail-closed（不隐式回溯——收购前不能假装有权益）；period 内变更默认拒绝（不静默平均），显式 allow_pro_rata 才日加权——诚实缺省 + 显式升级模式。
- apply-once 权益门与 ZR-602 basis 枚举**逐字对齐**：one_hundred_percent 恰一次乘有效份额；equity_share 拒绝（already applied——Kamoa/Porgera 双重折算防线）；consolidated 拒绝（合并口径不在此层折算）。三值各一条无歧义规则，ZR-607 会计桥再扩展。
- document.py 集成零 McCabe 模式第二次复用：validate_segments 循环内纯调用 + helper None 早退——加性键校验不推高主函数复杂度（ZR-602 先例）。
- geography_index 拒绝静默省略：无 geography 的资产进索引 = fail-closed（宁可拒绝不可漏计资产）。
- **REV-001~004 delta 修复（03d716e）**：首轮 reviewer 抓出 4 个输入类型泄漏——REV-001 basis 缺 isinstance(str) guard（与 ZR-602 REV-001 同类：成员测试前先类型守卫，教训已重犯）、REV-002 missing period KeyError、REV-003 None revenue float(None) TypeError、REV-004 非 dict 地理容器 AttributeError——全部修复 + 7 回归测试。**REV-005 minor**（container 形状硬化：apply_ownership_share 对 annual_revenue=None/str/list 仍抛 TypeError）登记为 ZR-607 会计桥后续。
- **教训（第二次重犯）**：`in` 运算符对 unhashable 值直接抛 TypeError，必须在 require 条件内先 isinstance(str) guard。ZR-602 和 ZR-603 两次独立卡的 REV-001 都是同一类 bug——说明这是系统性风险：凡是 `value in {set}` 的模式都要前缀类型守卫。

## 发现 30：ZR-604（F2 第四卡冲突保存与人工 review，2026-08-22）
- 冲突机制现状：semantic_groups（document.py:471-479）检测同语义键不同值 → 硬失败，无 assertion_status/resolution_status——真实产品缺口：Bisha kt/t 等多来源冲突无法表达"两个来源都可信但值不同，需人工 review"。
- 设计：冲突解决逻辑提取为 `_validate_conflict_resolution` helper——all resolution_status + ≤1 accepted → 允许共存（冲突已解决）；否则保持原行为硬失败（backward compatible）。`_validate_parameter_status_fields` 校验 assertion/resolution 枚举值——additive None 早退。semantic_groups 循环改造为调用 helper（validate_parameters max 保持 32）。
- 零 McCabe 增量模式第三次复用成功：helper 提取+纯调用+None 早退——additive 键校验不推高主函数复杂度。
- 双 assertion 语义：assertion_status（primary/secondary）标识事实来源角色；resolution_status（accepted/rejected/pending_review/under_review）跟踪 review 结果——同一事实的两个来源均被保留，不静默覆盖。
- **与 ZR-602/603 同步教训**：ZR-604 的 additive 键（assertion_status/resolution_status）与 ZR-602 的 basis 键、ZR-603 的 ownership/geography 键采用完全相同的模式——constants 词汇 + validate_parameters 内 helper 调用 + None 早退 + 无变动则零回归。F2 前四卡的 document.py 集成模式已稳定。
- **REV-001 minor（null resolution_status 语义）**：`"resolution_status": null` 在 `_validate_conflict_resolution` 中视为"已解决"（key 存在即 counted），但 `_validate_parameter_status_fields` 视 None 为缺省（通过）。建议后续改为 `item.get("resolution_status") is not None` 或显式拒绝 null 值——登记为 F2 后续（ZR-605 消费方或 ZR-610 ADR）。

## 发现 31：ZR-610（F2 会计 ADR 冻结，2026-08-22）
- ADR 文档（adr_mining_accounting.md）冻结 8 条会计决策：逐矿贡献=模型估计（IFRS 8 一致性——分部而非逐矿披露）、resource≠reserve（JORC/NI 43-101/PRC）、basis 三字段（IFRS 10/IAS 28/100%运营口径）、ownership timeline（IFRS 3 收购日语义 + 链式权益一次连乘）、单位一致性（JORC 实务）、双 assertion（best practice vs 静默覆盖）、地区层级、ADR 边界（冻结 vs 移交 ZR-605~608）。
- 独立会计 reviewer 验证了每个 ADR 引用与实际代码一致（calculate_model_path/apply_ownership_share/geography_index 等）——文档与实现逐字对齐。
- 2 info findings：REV-001 equity_share 是运营/管理口径非 IFRS 收入行（IAS 28）——建议澄清句；REV-002 pro-rata 日加权是 IFRS 3 收购日确认的模型近似——建议注释。均登记后续。

## 发现 32：ZR-605（F2 MineYearOperation 输入合同，2026-08-22）
- 七字段必填合同（volume/grade/recovery/payable/product/period/scenario）：任一缺失 → gap（不默认 0）——ADR §1 诚实 gap 原则的具体化。
- derive_saleable_volume = volume×grade×recovery×payable——把上游产量驱动分解为 resource 模型的 saleable_volume 单一驱动（单位继承 volume×grade 语义，如 kt×g/t=kg 金属量）。
- to_resource_model_drivers 映射可直接喂 calculate_model_path(model="resource")——MineYearOperation → 模型消费闭环。
- NEW_FILE_MAX=10 门：validate_mine_year_operation 内联 18 复杂度 → 提取 _positive_numeric/_ratio helpers 回 ≤10——新文件也要警惕 ratchet。
- **REV-001 minor（inf 值未拒）**：`volume=inf`/`realized_price=inf` 通过校验（inf>0）；NaN 已被拒。登记 ZR-606 后续：数值校验复用 contracts.evidence.finite_number / math.isfinite。

## 发现 33：ZR-606（F2 商业量价层，2026-08-22）
- 商业条款 provenance 结构：每个变量 = {value, source, assumption, period}——来源/假设/期限可追溯（"每个变量有来源/假设/期限"的机械化）。
- **ZR-605 REV-001 教训立即落地**：commercial terms 的 value 全部走 finite_number（inf/-inf/NaN 拒绝）——前卡 minor 在本卡即修复，未等集中处理。教训闭环：reviewer minor → 下一卡直接加固。
- 不重复计价设计：byproduct_credit 是**独立加项**（固定值，不乘 volume）——副产品收入不进入主商品 volume×price 路径，多商品路径天然无重复。
- 纯函数敏感性重算：calculate_net_revenue(saleable_volume, terms) 幂等确定性——price/FX 变动重算可复现（Δnet = Δprice×volume×(1−royalty)×FX）。
- **ZR606-REV-001 修复（delta 47fe715）**：saleable_volume 未走 finite_number（NaN/inf 静默传播）→ 路由 finite_number + 6 回归测试。**流程教训**：delta 复审首轮判 changes_required 是因为 pre-commit 钩子运行时 reviewer 看到 staged-not-committed——提交与复核之间需确认 commit 落地（git rev-parse HEAD 验证）再发复审。
- **REV-002 教训**：implementer receipt 的 result_triplet 在 delta 后需重封（uc 工具不强制跨 receipt triplet 相等，但链条一致性要求重签）。
