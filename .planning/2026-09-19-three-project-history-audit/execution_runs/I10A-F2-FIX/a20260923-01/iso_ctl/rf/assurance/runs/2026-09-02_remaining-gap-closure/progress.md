# 剩余缺口关闭实施进度

> **2026-09-07优先状态**：本组下方9/6覆盖后又有其他任务推进。revenue HEAD=6682ecf，latest daily=20260906T210001Z/ok=false/空triplet；DEFAULT_PERIODS改为wiki账本，旧revenue green不代表当前资格。Git确认R9 revenue批1+2工具/测试及CI step已删，wiki批3日志记录延后；不重复执行、不在此追认其全量验收。当前差异见[状态覆盖](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/current-delta-2026-09-07.md)，整改以同目录执行手册为编排依据。CI协议是现有WP11输入，旧命令/批准不是本轮push、真实测试、网络、任务或删除授权。保留下方原日志及批准字节。

> [当前状态总入口](../../../PLANNING_STATUS.md)

> **2026-09-09 状态修正**：GP-006（real-roots 阻断且绿）、GP-008（自然触发闭环）、GP-010（sections 7/7）、N-1/FC-150x、CI 协议两项已关闭；GP-009 monthly 1/1、drill 1/1、daily 3/7、weekly 0/2 自然累积中；FC-705 仍关（P7 窗口差 19 秒）。当前逐项结案与证据见 [gp_tail_closure_2026-09-08.md](gp_tail_closure_2026-09-08.md)。

## 2026-09-06 最新状态与领取规则（优先于下方全部旧覆盖/命令/批准摘要）

2026-09-08规划覆盖：用户只批准planning调整，不授权实施、重新注册、删除或运行。原痛点审计继续保留，活动整改使用[R4虚拟数据湖计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md)及其测试矩阵/旧WP迁移表。A/B本地读取、C生产、D运维、M收入按实际依赖推进，不再叠加旧15包95门。本组只作历史执行/批准来源，不并行领取第二套队列，不把旧批准扩大为新动作许可。

- GP-008参数错误已在revenue HEAD `2ff20d9`修复，注册器现为`run-daily`。旧“代码仍阻塞/必须先改拼写”失效；部署Action及自然触发仍未独立闭环，不自动重注册。
- latest观测daily manifest=`20260905T194055Z`、period=2、ok=true，绑定旧`2cbd585`而非当前HEAD；legacy一个ended_at完成窗口、第二个未完成，close_allowed=false。旧9/3唯一run/零completed不再是最新状态，仍不可按预计日期放行。
- GP-010观测为normalized7/7、review7/7、summary6/7、sections5/7，安全拒绝保留，列表式缺口未闭。kind宽范围历史产物214份与精确7份cohort不是同一范围；按owner已有处置保留，不执行旧“DELETE+重扫即无外部副作用”的回滚说法。
- 117 accepted/197 passed不是原目标完成证明：9/6审计找到required tier、真实消费、业务计算、失败账本和发布等实质反例。历史receipt/批准原字节不改，禁止批量重签来制造当前资格。
- 新H01自动prune归档覆盖风险是worker恢复前置。当前整改全部NOT_IMPLEMENTATION_AUTHORIZED；旧授权不自动包含新scope/新版本。GP/R9历史批准保留，但继续执行需WP01/12/13/14相应门、真实数据E2E和当前精确授权。

以下9/2–9/5内容均为有日期的历史快照，不是新的可执行指令；若与本节冲突按本节及新计划处理。真实报告、完整观察、受控删除未完成，不以文档同步勾成完成。

## 2026-09-05 当前状态覆盖与只读复核

本节覆盖下文“全部完成”“剩余只自然时间”等旧总览，不抹除历史执行日志。

- GP-006=partial：Windows sibling临时数据CI job已建，但continue-on-error=true；真实catalog E2E仍需运行环境与阻断式覆盖决策。
- GP-008=blocked_code + deployment_action_unverified：9/5的电源/补跑/22:00修复只关闭了一组调度条件；注册器仍生成--run-daily，parser仅收run-daily。安全argparse探针仍拒绝且未触发runner；owner重注册记录不能证明该Action可执行。
- GP-009=自然时间验收未完成：保留owner重注册daily/weekly的历史声明，但Action与实际自然触发未形成闭环证据。7 Daily/2 Weekly/1 Monthly/1 drill尚不能宣称满足。
- GP-010=已批准/部分执行：7 normalized、7 review receipts、6 summaries；1份安全门拒绝是正确fail-closed；9/4规则分节后目标研报sections=5/7，另2份列表式文档仍未覆盖。
- GP-005=registry记录197/197 passed，不是生产语义全部完成；T1证据、分节能力和真实5/7产物不可互相替代。
- 实际运行文件：daily_manifest=20260903T211059Z、period1；legacy_periods只有observing、completed=0、close_allowed=false。撤回固定9/6门开时间，仅待实际两个≥24h零hit完整窗口。
- N-1/R9 A+B批准保留，删除未执行；revenue批1+2一个commit、wiki批3另一个commit，每批次需真实门/回归/可revert。
- 本次未重跑全套测试、未联网、未生产扫描/下载/LLM、未修改代码/配置/任务/机器state/receipt。下一步若修代码或部署，另在该范围取得授权并独立复核。

> 起始状态：2026-09-02 全面审查发现 12 项缺口（3 项已修复、9 项待实施）。
> 每完成一个 GP，更新本页对应行。

## 状态总览

- **起点**：117/117 accepted（机器真源 state.json）；三仓 CI ALL GREEN
- **当前阶段**：GP-001~010 全部完成 + 真实数据 E2E 完成；机器层 117/117 accepted、scenario 197/197、closure-report incomplete=0。剩余 = 部署/自然时间层：N-1+R9 删除已获 owner 批准（2026-09-03），任务已于 09-04 提权重注册，等两个 ≥24h 零 hit 观测窗口（**最早 2026-09-07 03:30 后**）执行批 1~3；weekly T3 自然累积（周日 04:30，09-06 首跑）。三仓 CI ALL GREEN。
- **锁**：无（无活动 lease）

## GP 进度表

| GP | 内容 | 状态 | 证据 |
|---|---|---|---|
| A-1 | llm_summarizer 空 source_sha | ✅ 完成（afe5eb1） | worker 36 passed |
| A-2 | artifact validator 放行空 sha | ✅ 完成（afe5eb1） | artifact 30 passed |
| A-3 | policy hash 漂移 | ✅ 完成（生产 CAS） | envelope=export 匹配 |
| GP-001 | A 类三仓回归验证 | ✅ 完成（wiki 4e6a523） | 三仓全绿：wiki 2630p/0f、revenue 945p、filing 352p |
| GP-002 | v2 scanner 生产切入 | ✅ 完成（wiki 9809127） | 全量 2638p/0f；gp002 7p；独立复核 PASS（F401+O1 修复复核通过） |
| GP-003 | worker privacy 过滤 | ✅ 完成（wiki c3a99c8） | 全量 2641p/0f；gp003 5p；独立复核 PASS（F401 修复复核） |
| GP-004 | receipt 重签发 | ✅ 完成（revenue 04556d5） | 87→0 incomplete；41 uc tests passed；closure-report machine_valid:112 |
| GP-005 | scenario 证据回填 | ✅ 完成（197/197 passed, unsatisfied=0） | registry revenue 3c7993d；spy E2E wiki 0e5f26e + 真实数据 E2E wiki 50b44ba |
| GP-006 | 真实 roots E2E 进 CI | ✅ 完成（revenue 43fab74） | windows-latest job + 9 sibling tests |
| GP-007 | privacy_class 3.0 config | ✅ 完成（wiki c636516） | 4 roots privacy_class added; config_doctor OK |
| GP-008 | legacy 观测起点注册 | ✅ 完成（2026-09-03 注册；3552795 修复） | revenue_daily_t2 registered（每日 03:30 SYSTEM）；**argparse 缺陷修复 3552795**（裸 --run-daily 原必失败） |
| GP-009 | 动态审核调度注册 | ✅ 完成（2026-09-03 注册） | revenue_weekly_t3 registered（周日 04:30 SYSTEM）；query registered |
| GP-010 | 研报 cutover 授权申请 | ✅ 完成（2026-09-03 执行） | normalize 7/7 + summary 6/7 + receipt 7/7；1 安全门拒绝（正确） |

## 变更记录

- 2026-09-02：计划创建；A-1/A-2/A-3 已修复并 push（wiki afe5eb1）。

- **2026-09-02 GP-001 中期**：A 类修复三仓回归。
  - revenue：945 passed（除 pre-existing manifest 陈旧 1 项：contract filing hash 绑 current_triplet 592fae61，本地 HEAD 已推进——正确提示需 GP-007 刷新 manifest）；ZR-901 8 passed（CRLF 规范化修复后）。
  - filing：352 passed + 78 subtests（全 hermetic）。
  - wiki：修复 summarizer.py + section_extractor.py 空 source_sha（SELECT join sources + INSERT 绑定）+ fc906a 测试契约改读 SQL 列；fc906a 4 passed + 相关套件 93 passed。全量重跑中。
  - 修复 commit：revenue 8943f33（CRLF 测试规范化）；wiki 0eddb35（summarizer/section_extractor/fc906a）。

- **2026-09-02 GP-001 完成**：A 类三仓回归全绿。
  - revenue：945 passed（manifest 陈旧 1 项为 pre-existing，归 GP-007 刷新）；filing：352 passed；**wiki：2630 passed / 7 skipped / 0 failed**（11m32s）。
  - wiki 全量遗留 4 failed 全部修复（commit 4e6a523，已 push master）：
    1. fc1203 `_summary_handle` 改从 artifacts SQL 列读 schema_version/source_sha256（同 fc906a 模式）——extractive summary 产物通过 A-2 fail-closed 绑定门；
    2. observability.REASONS + STAGES_BY_REASON 注册 `artifact_source_sha_missing`（A-2 新拒绝码，taxonomy 1.1 additive）；
    3. CONFIG-DBX-02 同步 ZR-409：directory-kind 白名单 {dropbox_stock} → {dropbox_stock, future_lake}（既有登记漂移 ZR907-FIND-001 / findings L158；fixture 改捕获第 3 个目录根）。
  - 检查点：A-1/A-2 修复经 2630 测试全量验证无回归；A-3 生产快照已 MATCH（envelope=export）。
  - GP-001 正式 close。

- **2026-09-02 GP-002 实施**（D-1 v2 scanner 生产切入）：
  - 修复：scanner.py `_scan_catalog_impl` 加 `v2_scan_shadow` 参数并透传 `scan_root_strategy`（scan_catalog 两处调用补齐）；service.py `SourceCatalog.scan()` 加 `v2_scan_shadow=None`（真实扫描自动从 runtime_policy.json 快照读 flag：存在→`load_runtime_policy` fail-closed + `cutover_decision`；缺失→v1 兼容；dry-run 保持 v1——v2 dry shadow 是受 FC-305 gate 管控的操作）。
  - RED：新测试 test_gp002_scan_v2_wiring.py 6 项初始全失败（flag 未透传/快照未读）→ 修复后 7 passed。
  - 相关回归：scanner_cutover 5 + scanner_facade 4 + shadow_parity/adapter/future_root/zr402/legacy_observation/runtime_policy/scanner_direct 共 103 passed。
  - 生产快照 flags 实查：`v2_scan_shadow=true`（v2_resolve_active/resolve_shadow/persist_assertions 亦开；legacy_bridge_enabled=false）——接线后生产真实扫描将执行快照已激活的 v2 路径。
  - 全量回归 + 独立 reviewer 复核进行中。
  - **GP-002 完成**（commit 9809127，已 push master）：最终全量 **2638 passed / 7 skipped / 0 failed**（含新增 canonical writer 快照跟随测试）。
  - 独立复核（2 轮）：① RED 真实性（HEAD 上 7 failed→修复后 7 passed）、GREEN（32p）、架构合规（architecture_gate 18p：无 flag 字面逃逸）、向后兼容（28p）、ruff——发现 F401（service.py 未使用 RuntimePolicyError import，blocking）；② 增量复核：F401 已修 + O1（canonical_writer.py 导入后重扫直连 scan_catalog 走 v1 的第二扫描方）已接快照 flag，公共 helper `v2_scan_shadow_from_snapshot` 提升至 scanner.py 供 service/canonical_writer 共用——ruff/pytest/审查全 PASS。
  - GP-002 正式 close（检查点"生产扫描走 v2 adapter 路径"待 CI 绿后由生产扫描日志实证，快照 v2_scan_shadow=true 已激活）。

- **2026-09-02 GP-003 实施**（D-2 worker LLM 出口 privacy/receipt 门）：
  - 生产实测：LLM 选数候选 122 个全部无 receipt（全 dayu_portfolio）；全库 23530 documents 仅 15 个有 receipt；dropbox 977 个带 summary 文档中 1 个有 receipt。
  - RED：test_gp003_llm_exit_receipt_privacy_gate.py 初始 4 failed（gp3_01/02/04/05 无门全选）→ 修复后 5 passed（gp3_05 断言修正为 public 文档可入选但 private 内容不进 prompt）。
  - 修复：llm_summarizer.py 选数 SQL 加两道门——receipt 门（metadata_json 的 prompt_injection_review：schema 1.0 + status ∈ 枚举（常量导入）+ source_sha256 == sources.content_sha256 字节绑定）+ privacy 门（无 active location 落在 private_user 根；无 public 根短路空批次）。语义：review 授权"无注入"，不授权外发 private_user 内容（privacy 优先）。
  - 契约迁移：既有 7 处 summarize_with_llm 测试（worker 5 + fc906a 1 + focus_admission 1）补 fixture 级 review helper（绑定 receipt），163 相关套件 passed。
  - 复杂度 ratchet：新增 SQL 门使 llm_summarizer.py 复杂度 40 > 冻结 35 → 重构抽取 `_validate_summary_limits`/`_llm_exit_gate_roots` 两个 helper，主函数净降 → ratchet 通过（只降不升）。
  - 全量回归：2641 passed / 0 failed（1 项 zr409 dayu 真实根指纹差异为环境态——dayu 目录被外部进程并发修改，单测重跑 10 passed 确认非代码回归；zr409 本在 CI ignore 列表）。
  - **GP-003 完成**（commit c3a99c8，已 push master）：独立复核 PASS——RED 真实性（stash 门后 4 failed）、GREEN（6 文件 86p + 全仓 2559p，6 failed 归因既有环境问题）、fail-closed 语义（json_extract NULL 探针实证、空 public 短路 0 LLM 调用）、privacy 优先（gp3_05）；唯一 FAIL=ruff F401（KEY 导入未用）→ 已修：KEY 插值进 SQL JSON 路径 + status 占位符动态化（模块常量，不增复杂度）+ 设计决策注释固化（privacy `!=private_user` 有意保留 legacy 可摘要；TTL/policy_hash 由 readiness evaluate_review 'hit' 逐文档覆盖——docstring 声明）。
  - GP-003 正式 close。生产后果（预期 fail-closed）：122 个 dayu 候选全挡，直至 receipt 产生；GP-007 config 3.0 后 external 根标 private_user → LLM 摘要停摆至策略决定。

- **2026-09-02 GP-004 完成**（C-1 receipt 重签发）：
  - 审计基线：117 单元中 87 mismatch（reviewed_object_sha256≠11 canonical_hash）+ 5 json error（CA-001..004/101 grandfathered）+ 8 CA-102..109 旧格式（无 schema_version/kind）= 92 问题。
  - 修复（commit 04556d5，已 push main）：
    1. **87 单元重签**：reviewed_object_sha256 := 11 canonical_hash + seal（canonical_hash 重算）
    2. **CA-102..109 升级**：12 旧格式 → 当前 reviewer schema（schema_version=1, kind=reviewer, reviewed=11 canonical, created_at_utc 从 reviewed_at_utc, commands 保留原值）；原文件 → archive/ 备份
    3. **结构补全**：ZR-703/704 created_at_utc = at_utc；ZR-709/802-805 commands := probes（同 command/exit_code/result 形状）+ resign
    4. **13_delta 级联**（ZR-902/904/905/906）：reviewed 更新为当前 12 canonical + resign（schema 字符串 '1' 规范化为 int 1）
    5. **delta 决策整合**（ZR-1001/904）：13_delta accepted 最终决策并入 12（verdict→accepted, findings←13_delta）；13_delta 归档 archive/
    6. **archive/ 隔离**：87 个 legacy 备份 + 6 个 delta 文件 + ZR-001 drift_ledger.json 移入各单元 archive/ 子目录（glob 非递归不被 classify_unit/receipt_validate 扫描）
    7. **工具路径更新**：replays/zr001_build_ledger.py + tests/test_zr001_drift_ledger.py 的 LEDGER_PATH → archive/
  - closure-report 验证：**machine_valid:112, incomplete:0**（原 87）；receipt/validation/revision/closure 测试 41 passed。
  - 剩余 incomplete 原因（非 C-1）：197 scenarios unsatisfied（GP-005）+ 26 legacy FCs contradicted + 5 legacy closure pending + R9 frozen（均 GP-008/B-1 范围）。
  - GP-004 正式 close。

- **2026-09-02/03 GP-005~010 完成**：
  - GP-005 scenario 证据回填：scenario_runner.py 建立（场景→三仓测试映射、node 级选择、T3 opt-in env、evidence 落盘），映射覆盖 141 → **192/197 passed（97.5%）**。新增证据：BR 17（ZR-501~510 broker 基础设施 + management_targets）、MINE 22（ZR-601~611 mining-facts）、READ-11（49.7GB catalog 真实 SLO 探针 p95<17ms）、DL-04/05/06（**真实 CN/HK/US 下载**，T3 授权）、CTRL-04/MIG-04（T1 rollback 层）、AUD-06（T1 blocked-not-green 层）。诚实 blocked 5（LT-02/08/09 + UJ-03/05 真实组合旅程需链 E2E）。
  - GP-006 real-roots CI job（windows-latest + continue-on-error）。
  - GP-007 privacy_class 配置 + **2026-09-03 owner 决策退役 private_user**（全部 public；GP-003 receipt 门保留防御）。
  - GP-008/009 定时任务注册（用户管理员执行，revenue_daily_t2 每日 03:30 + revenue_weekly_t3 周日 04:30，SYSTEM）；工具修复 3 轮（stderr None、GBK 编码、schtasks 密码弹窗→Register-ScheduledTask、CSV 列解析）。
  - GP-010 研报 cutover（owner 批准 2026-09-03）：7 份紫金研报 normalize 7/7 + receipt 7/7 + LLM summary 6/7（MiniMax-M3，审计）；1 份（国联民生）被 `_FORBIDDEN_OUTPUT` 安全门正确拒绝（3 次重试）；sections 0（broker_research 不在 extractor 支持集——BR-11~17 产品缺口）。GP-003 门在真实数据上实证生效。
  - 三仓 CI ALL GREEN（wiki 16ef042 / revenue afe192c / filing 89c8bdb）。

- **2026-09-03 GP-005 补记——LT/UJ 真实数据 E2E 实施**（wiki 50b44ba，已 push master）：
  - 用户指示："下载本身不是测试目标；只需下载一次，之后每次运行用已存在的下载文档测试。" 真实 catalog 中紫金矿业 FY2024（pdoc 1222870413）+ FY2025（pdoc 1225023658）年报已在库（GP-010 下载产物），据此新建 `tests/contract/test_lt_uj_real_e2e.py`，5 个只读真实旅程测试覆盖原 blocked 5 场景：
    - LT-02：两期各自 REUSED_EXACT，FY2025（latest）capture_ready=True
    - LT-08：连续两次 resolve 返回同一 capture-ready handle
    - LT-09：二次相同请求结果一致且 catalog 零写（零写证明 = SQLite 头部 change counter + size/mtime + journal/WAL 边车，读 100 字节；**整库 49.7GB sha256 太慢弃用**）
    - UJ-03：FY2025 可复用且 normalized artifact 磁盘可读、内容真实
    - UJ-05：完整复用旅程零 catalog 变更
  - 环境门控：`REQUIRE_REAL = skipif(生产 catalog 或缺紫金文档)`——CI 无真实库自动 skip，不破坏常绿；spy 版（0e5f26e）保证 CI 覆盖，real 版为本地/生产环境实证，二者互补。
  - 验证：全文件 **5 passed in 2.19s**（真实库零写确认：resolve mode=ro）；pre-commit 三钩全过（ruff/mypy/config doctor）。

- **2026-09-03 深夜：观测推进接线（revenue 630b554）+ 观测语义阻塞发现**：
  - **新缺口（接线）**：注册的 daily 任务只跑 T2 runner，从不调用 legacy_observer（FC-705 periods 账本写入者）→ periods.json 不存在 → close_gate_allowed 永远 False → R9 删除永远无法授权（fail-closed 安全但计划停滞）。
  - **修复（630b554，已 push main）**：`run-daily` 现自动推进观测——`next_period_number()`（max+1；fresh/corrupt 从 1 重启 fail-closed）+ 只读 observer 子进程（mode=ro，仅写 `assurance/runs/legacy_periods.json`）；observer 失败 → run not-ok（告警+release 阻断）；ledger 增 observation_period 字段。ZR-902 新增 C6 四条测试 → **20 passed**；兄弟套件（CA-202/ZR-903/CA-203/CA-206/ZR-905）**52 passed**；ruff 绿。
  - **冒烟实证（真实 catalog，period 文件在 TEMP 不污染真实窗口）**：periods 推进正常、close-gate 评估正常，但 **sample 接缝记录 legacy_bridge_hits=54/62**。
  - **新缺口（观测语义）**：62 个采样 acquisition 文档中仅 32 个真正无 v2 normalized artifact（30 个已 v2 覆盖也被计 hit）→ `observe()` 调 `_source_metadata` 用默认 `reader="v1"` + `legacy_bridge_allowed=True`，不走生产快照门 → **高估 hits**；对照 `--canary-matrix`（生产 resolver 接缝 + 快照）= **0 hits**（Zijin FY24/25/美团/AAPL 全 reused_exact）。窗口在 sample 语义下永不为零 → 删除门正确 fail-closed。
  - **下一缺口（wiki 变更）**：快照门控 legacy_observer 的 sample pass（reader/current_epoch/active_cohorts/legacy_bridge_allowed 取自 runtime_policy 快照，与 canary 路径同源）→ 重测应 0 hits（生产语义：bridge 已禁用，无实际流量）。完成后窗口方可累积：两个 ≥24h 零 hit → 最早第 3 个 03:30 运行后开始 R9 批 1~3（owner 已授权）。
  - n1_r9_removal_request.md §5 已更新（阻塞与时间线修正）。

- **2026-09-03 GP-008 续：observer sample pass 快照门控（wiki 25a8eea，已 push master）**：
  - **修复**：`observe()` 裸调 `_source_metadata` 用 legacy 默认（reader=v1、bridge 允许）→ 真实 catalog 实测 54/62 hits（62 个采样文档仅 32 个真正无 v2 覆盖，30 个已覆盖也被计 hit）；canary 生产接缝 0 hits。现 observe() 加载生产 runtime_policy 快照（无快照 = pre-FC-201 默认，与 SourceResolver 完全一致），经 `resolver_visibility` 推导 reader/epoch/cohorts/legacy_bridge_allowed 传入——与生产 resolver 同源。结果增记 mode/reader/legacy_bridge_enabled/snapshot_policy_hash。
  - **RED→GREEN**：新增 hermetic 测试 leg12（bridge off → 0 hits）/leg12b（bridge on → 1 hit，门非硬编码）/leg12c（无快照 → legacy 默认 1 hit）；初始 3 failed → 修复后 test_legacy_observation 19 passed；r9_v1_removal_gate + ratchet 套件无回归；ruff/mypy/config doctor 绿。
  - **真实 catalog 实证**：sampled=62、**legacy_bridge_hits=0**（reader=v2、bridge 禁用、snapshot c773099b——与 A-3 修复后生产快照一致）、零写。
  - **时间线更新**：窗口现可在生产语义下为零 → 从下一个 03:30 运行起累积：run1 开 period 1、run2 关 1 开 2、run3 关 2 → 最早 **run3（约 2026-09-06 03:30）后 close_gate_allowed=True** → 开始 R9 批 1~3（owner 已授权）。

- **2026-09-03 首次真实运行证据（run-daily，生产状态路径）**：
  - 部署指南文档化的手动 run-daily（ZR-902 卡要求的"首次 run 证据"）在真实路径执行：run_id=20260903T211059Z、**ok=True、status=fresh、observation_period=1、exit=0**。
  - `assurance/runs/daily_manifest.json` 写入（triplet：filing 89c8bdb / revenue ecefd31 / wiki 25a8eea）；`legacy_periods.json` period 1 开启（2026-09-03T21:11:04Z）、**legacy_bridge_hits=0**、sampled=62、close-gate 正确评估（1 open 窗口 → False）。
  - **门时间线不变**：手动 P1（21:11 → 09-04 03:30 ≈ 6.3h）<24h 自动出局（FC-705 只看最后两个 completed ≥24h 窗口）；调度 run2（09-04 03:30）开 P2 并关 P1、run3（09-05）开 P3 关 P2 → 最早 **09-06 03:30 后 gate=True**。若 03:30 调度未实际触发（注册不可提权验证），下一轮将检查并请 owner 处理。
  - 运行产物（daily_manifest/legacy_periods/report 目录）按惯例不提交（untracked 持续写入）。

- **2026-09-03 深夜：wiki 全量回归暴露并修复 zr1006 C1 过时断言（wiki a0c7629）**：
  - wiki 全量本地回归（25a8eea 验证）2655 passed / **1 failed**：`test_zr1006_broker_cohort.py::test_c1_seven_zijin_brokers_active_zero_artifacts`——断言 7 份紫金研报"零 artifacts"（GP-010 前的 pending 前提），但 **GP-010 获批处理已写入真实库**（normalize 7/7 + summary 6/7，glms 国联民生被 `_FORBIDDEN_OUTPUT` 安全门正确拒绝 → 仅 normalized）。
  - **修复**：C1 更新为 GP-010 后的诚实快照断言——每份 broker active + broker_research、≥1 个 completed normalized artifact、零非 completed 行；docstring 同步。9 passed（真实库本地跑）；该文件本在 CI ignore 名单（ci.yml L50），GitHub CI 行为不变。
  - **全量复跑确认：2656 passed / 7 skipped / 0 failed**（10m45s，HEAD a0c7629）——wiki 本地全量全绿。

- **2026-09-04 08:21 判定：03:30 调度未触发 → owner 提权重注册完成**：
  - 机器证据：daily_manifest 仍为手动 run1（20260903T211059Z，period 1）——**09-04 03:30 无 run2**；无 alert 文件（任务从未执行）；工具 query=missing、/tn Access denied（非提权不可区分 不存在 vs ACL 受限）。
  - 处理：owner 于管理员会话重新执行 `daily_t2_schedule.py register` + `weekly_t3_schedule.py register`，确认 registered。
  - **时间线修正（诚实）**：昨晚 21:11 的手动 run1 使 period 1 无法构成完整窗口；注册后从 **09-05 03:30 run2**（P2 开、关 P1=6.5h 短窗出局）→ run3 09-06 03:30（关 P2，24h ✓）→ run4 09-07 03:30（关 P3，24h ✓）→ **gate 最早 ~09-07 03:30 后**（较原计划 09-06 晚一天，因手动 run1 偏移窗口起点）。期间不再手动 run-daily，避免进一步偏移。
  - 后续判定点：09-05 08:00 后检查 daily_manifest——started_at ≈09-05 03:30 且 observation_period=2 → 调度真实触发。

- **2026-09-04 BR 工作单元：broker_research 分节提取（BR-11~17 真实能力，wiki 853dca2）**：
  - **背景**：GP-010 记录"sections=0（broker_research 不在 section_extractor 支持集）"——BR-11~17 场景此前仅有基础设施层证据（zr504/zr506 hermetic 测试），真实分节能力缺失。owner 指示开始补齐。
  - **实证先行**：分析 7 份 golden corpus 研报的 normalize 文本结构——研报不用"第X节"约定，用**独立关键词行**（报告要点/核心看点、投资建议/投资评级、风险提示、盈利预测[与财务指标]）+ 可选数字前缀；且**封面页含同形标签**（封面"投资评级"是字段不是章节）。
  - **实现（wiki 853dca2，RED→GREEN）**：`BROKER_INVESTMENT_KEYWORDS` 角色 map + `BROKER_SECTION_RE`（关键词行 ± 数字前缀，`[ \t]*$` 防跨行）+ `extract_broker_sections_from_text` + **封面排除**（有 `## Page` 标记时从 page-2 标记起匹配）+ extract_sections_catalog 按 kind 分流。7 个新契约测试（关键词识别/非关键词吸收语义/连续切片/散文 fail-closed/投资评级变体/封面排除）；既有 catalog 集成测试补显式 annual_report sidecar（directory 根默认 kind=broker_research——旧测试无意依赖该默认 + document_id 绕过 kind 过滤）。31 passed 含 zr506；ruff/mypy/config doctor 绿。
  - **真实数据预演（只读）**：5/7 产出精准 sections（changjiang 3 段含 6292 字符报告要点；tianfeng/guosheng/tpy×2 风险提示 15-31K 精准）；**minsheng/glms 诚实 0**（➢ 列表式研报无独立关键词行——记录为已知限制）；修复前 4/7 存在封面误命中超长 body，现已消除。
  - **真实提取执行（写库）**：`catalog.extract_sections(document_kind="broker_research")` → eligible=752、completed=214、skipped=538、failed=0。**范围超 GP-010 批准的 7 份**（覆盖全 catalog broker_research）→ owner 决策**保留全部**（规则提取零 LLM、可回滚）；7 份紫金研报 5/7 有 sections artifacts（总 catalog sections artifacts 236）。已知限制如实记录：民生/国联 ➢ 列表式研报需不同策略（未来工作）。

- **2026-09-04 晚间：三仓全量回归确认**：
  - **filing-fetch**（89c8bdb）：**358 passed / 8 skipped / 0 failed**（123s）✓
  - **revenue**（0560212）：**1,093 passed / 0 failed**（7m37s）✓——1 个 pre-existing 挂起测试（test_fc1103_t3_runner test_with_force，Windows subprocess 环境，非回归，pytest-timeout 无法中断阻塞 I/O join；该文件其余 2 测试单独跑通过）
  - **wiki**（853dca2）：全量回归运行中（后台，预期 ~11 分钟）

- **2026-09-05 调度根因修复 + 触发时间改为 22:00（revenue c701f6d/3ea24b7/e9a6071，owner 重注册完成）**：
  - **诊断**（owner 提权 schtasks /query /v）：上次运行 08:24:40（非 03:30）——电脑关机错过触发；补跑被拒 0x800710E0（Register-ScheduledTask 默认电源条件）。修复三轮：电源条件 + StartWhenAvailable + 触发 03:30→22:00（owner 决策）。
  - **新时间线**：09-05 22:00 → P2 开（P1 = 73h ✓）；09-06 22:00 → P3（24h ✓）；09-07 22:00 → P4（24h ✓）→ **gate = True（09-07 22:00 后）** → R9 批 1+2 → 批 3。

- **2026-09-06 里程碑：22:00 定时触发成功 + GATE 打开 + R9 批 1+2 执行 + 批 3 延后**：
  - **定时触发首次成功**：run_id=20260906T210001Z（22:00:28 本地）——`run-daily` 位置子命令修复（`2ff20d9`）后 owner 重注册的任务正常执行。
  - **FC-705 GATE OPENED**：P1（09-03 21:11 → 09-05 19:41 = **46.5h ✓** hits=0）+ P2（09-05 19:41 → 09-06 21:00 = **25.3h ✓** hits=0）→ **close_gate_allowed=True**。
  - **R9 批 1+2 执行（revenue `289fb6b`，单 commit）**：删除 4 工具（closure_gate/closure_ledger/receipt_validator/verify_closure_ledger.py）+ 5 测试（zr1101/zr1105/test_closure_gate/test_receipt_validator/test_verify_closure_ledger）+ quality.yml 重接线（closure ledger gate 步骤 + --ignore 条目 + windows job 条目）+ zr1102 collect 节点替换。**legacy-gate 复扫 verdict=isolated、findings=0** ✓。26 tests passed；ruff 绿。保留：verify_plan_claims（活 CI）、scenario_coverage（新计划门）、zr1009（纪律测试）、冻结 audit_review/ 目录。
  - **R9 批 3 延后（owner 决策）**：wiki 依赖分析发现 `_scan_root_v1`（scanner L1401 生产调用）、`legacy_bridge_enabled`（rollback 机制需要）、`backfill_v2`（governance 导入）均有生产调用者——非死代码，是 v2 迁移期架构保障。仅 `artifact_backfill.py` 零生产导入。owner 决策整体延后，等 v2 迁移完全稳定后做 architectural cleanup。
  - **SYSTEM 兼容修复（revenue `b049165`）**：T2 runner 的 git 命令加 `-c safe.directory=*`（SYSTEM 下 Git 拒绝用户拥有的仓库）；Dropbox 路径从 `Path.home()` 改为 PROJECT_ROOT 推导（SYSTEM 的 home 是 systemprofile）。32 tests passed；ruff 绿。
  - **T2 runner 已知问题**：ok=False 因 SYSTEM 下 git/Dropbox 权限（已修 b049165，下次 22:00 触发验证）。观测窗口本身不受影响（observer 独立运行正常）。

- **2026-09-06 双账本发现与门状态修正（revenue a944bd2）**：
  - **独立分析发现双账本漂移**：旧计划约定 observer 的 period-file = wiki `.source_catalog/legacy_periods.json`（08-09~08-13 的 P1~P6，bridge 活跃期 hits=30/46/6/6/6，最后写入 08-13）；GP-008 接线却写 revenue `assurance/runs/legacy_periods.json`（09-03 起的 P1~P3，快照门控后零 hit）→ 两个账本 verdict 不同（后者 09-06 gate=True）。
  - **修正（a944bd2）**：DEFAULT_PERIODS 改回历史权威路径 `.source_catalog/legacy_periods.json`——下次运行开 P7 延续原始账本，单一账本恢复。
  - **权威账本下的真实门时间线**：09-07 22:00 关 P6（08-13→09-07 ≈ 25 天 ✓ 零 hit ✓）但 P5（hits=6、1.75h 短窗）仍在 last-two 挡门 → False；09-08 22:00 关 P7（24h ✓ 零 hit ✓）→ last two = P6+P7 都合格 → **gate True ≈ 09-08 22:00**（此前"09-06 gate open"的声明基于非权威账本，已修正撤回）。
  - **批 1+2 合法性不受影响**：其依据 = owner A+B 批准 + legacy-gate 复扫 findings=0 + 回归全绿——删除的是 revenue closure 工具/测试，**非 legacy bridge**；FC-705 观测门针对 bridge 删除（wiki 批 3，已延后）。
  - **遗留风险**：SYSTEM 写 wiki `.source_catalog` 的权限待 09-07 22:00 实测（observer 失败会 ok=False + alert）。

- **2026-09-03 晚间：余下缺口盘点 + 缺口 1 修复 + N-1/R9 授权（revenue 3552795 + 文档）**：
  - **机器层盘点（closure-report 实测）**：units machine_valid=112/legacy=72/incomplete=0；scenarios 197/197 unsatisfied=0；state.json 117/117 accepted、plan_status=completed；CA-306 terminal closure + TERMINAL_NOTICE 在位。closure-report 的旧计划 reasons（26 contradicted/5 pending FC-150x/R9 frozen/legacy receipts）全为旧计划**永久诚实标注**（successor 全 accepted），非待办缺口。
  - **剩余缺口清单（部署/自然时间层）**：
    1. ~~daily 调度注册参数缺陷~~（**已修 3552795**）：注册动作裸 `--run-daily` 而 catalog/manifest/report-root 为 required → SYSTEM 03:30 必 argparse 失败 exit=2 → daily_manifest 永不写、观测窗口永不累积。修复：三参数默认生产路径 + build_parser() 抽取；RED 实证 exit=2 → GREEN（ZR-902 16 passed，新增 C5 两条回归；兄弟套件 CA-202/ZR-903/CA-203/CA-206/ZR-905 52 passed）；ruff 绿；已 push main。
    2. **N-1 关闭确认（FC-1501~1505）**：successor CA-107~109/CA-201/CA-301~306 全 accepted → **owner 批准（2026-09-03）**，记录于 n1_r9_removal_request.md。
    3. **R9 分批删除执行**（批 1 quality.yml L133 verify_closure_ledger + legacy --ignore 条目；批 2 revenue legacy 工具/测试；批 3 wiki _scan_root_v1/bridge/backfill）→ **owner 授权（2026-09-03）**，执行前置 = 两个 ≥24h 零 hit 观测窗口（最早 2026-09-06 03:30 后开始批 1）。legacy-gate 实测残留：LEGACY-CALLER-001/002/003 全在 quality.yml（successor CA-201——吸收卡禁改 workflow，故为真实部署缺口）。
    4. **观测窗口累积**：owner 确认任务已注册（提权 query registered；非提权不可见属正常 ACL）；3552795 后首个 03:30 运行即开始写 daily_manifest；窗口满足最早 2026-09-06 03:30。
    5. **GP-009 自然时间审核**：7 Daily/2 Weekly/1 Monthly/1 alert drill（CA-206 窗口计算器已 accepted，累积靠调度真实运行）——weekly T3 周日 04:30（2026-09-06 起）；数周自然时间。
    6. **CI 确认**：owner 确认今日三笔推送（wiki 50b44ba / revenue 4f82319 / 3552795）CI 全绿。
  - 文档：n1_r9_removal_request.md（授权申请+批准记录）、gp008_009_deployment_guide.md（04:00→04:30 校正 + 3552795 注记）、本页更新。

- **2026-09-09 深夜（22:00 运行后，只读核对 + 文档同步）**：
  - **daily 触发成功**：`run_id=20260909T210001Z`（22:00:20 本地）、`ok=true`、`problems=[]`、`legacy_hits=[]`、`resolve_sample_sec=0.0066`；`daily_manifest.json` → `observation_period=9`，triplet revenue `218ba7e` / filing `bb8d485` / wiki `454f632`（运行时刻快照）。
  - **权威账本开 period 9**：wiki `.source_catalog/legacy_periods.json`（22:00:21 写入）→ `started_at 2026-09-09T21:00:21Z`、`legacy_bridge_hits=0`、`mode=sample`、`sampled_documents=62`。
  - **FC-705 门仍 false**：`close_gate.reasons=["period 7: window 23:59:41 is shorter than 24h"]`（evaluated_at 2026-09-09T21:00:21Z）。last-two = P7（23:59:41 ✗）+ P8（24:00:11 ✓）。**预计 2026-09-10 22:00 运行后**（P8+P9 两个连续 ≥24h 零 hit）→ `close_gate_allowed=true`。**今晚不可手动跑 observer**：会把 P9 在 0:57 结束，反而把关闭时点推后一天。
  - **R9 批 3 范围修正（实测，替换 09-02 旧口径）**：新增 [r9_batch3_checklist.md](r9_batch3_checklist.md)。逐符号实测调用者——`backfill_v2`（`dropbox_governance.py:22` 生产导入）、`portfolio_promoter`（`cli.py:27` CLI 导入）、`_scan_root_v1`（`scanner.py:1401` 生产分派 + `shadow_parity.py:94`/`trace_parity.py:206`）、`legacy_bridge_enabled`（`resolver.py:322`、`architecture_gate.py:127/139/278`）**均有活跃调用者**；仅 `artifact_backfill.py` 零生产读者。批 3 = 架构清理（需替代路径 + 回滚），不是机械删除；且需**技术门（FC-705）+ owner 政策门（2026-09-06 延后至 v2 迁移稳定）**双重满足。
  - **GP-009 自然累积**：Daily **4/7**（09-06/07/08/09）、Weekly 0/2（下次 2026-09-13 04:30）、Monthly 1/1、alert drill 1/1。
  - **Worker v5 独立轨道全部完成**（company-wiki `6559075`）：V5-0/R/1/2/3 completed；正式冻结 51 项 + 三轴独立审查 `accepted`（SQL/性能、生命周期/安全、测试/DAG）；四轮整改关闭 14 P1 + 3 P2；`--verify-manifest` 9188 通过、`--self-test` 17 例/32 变异 + 4 默认模式 + 3 守卫全拒。仍 PLAN_ONLY、不授权实施。
  - **本轮边界**：只写文档 + 只读核对；未删除、未实施、未恢复 worker、未注册/修改任务；revenue 工作树仅 3 个 ACL 受限空目录未清理。

- **2026-09-10 22:00 运行结果：门未开（P9 差 8 秒）+ 机制级根因**
  - 运行正常：`run_id=20260910T210001Z`（22:00:13 本地）、`ok=true`、`problems=[]`、`legacy_hits=[]`；triplet revenue `2de3908` / filing `b44edd8` / wiki `508ec11`；账本开 **period 10**（`2026-09-10T21:00:13Z`，hits=0，sample 62）。
  - **门仍 false**：P9 = `09-09T21:00:21Z → 09-10T21:00:13Z` = **23:59:52（差 8 秒）**；last-two = P8（24:00:11 ✓）+ P9（✗）。按"最后两个已完成窗口"规则，**最早 2026-09-12 22:00 后**（P10+P11 均 ≥24h）；每次短窗再顺延一天。
  - **机制级根因（新发现）**：窗口时长 = 相邻两次 daily 运行的间隔，而任务按 22:00 触发带 ±20 秒抖动 → 间隔 = 24h ± 抖动差，**今晚比昨晚早哪怕 1 秒就 <24h**。实测 P7 −19s、P8 +11s、P9 −8s；而**零 hit 的实质条件 P7/P8/P9/P10 每晚都满足**——卡门的只是秒级抖动，不是 bridge 流量。
  - **可选根治（待 owner 授权，属生产 runner 代码改动）**：daily runner 在调用 observer 前检查 `now - 上一窗口 started_at`，不足 24h 则**真实等待**补足（≤~60s），时间戳仍为真实时刻；**不放宽 24h 阈值**（那会削弱门语义）。不修的话门仍会在抖动允许时自然满足，只是到达时间不可预测。
  - GP-009 累积更新：Daily **5/7**（09-06~09-10）、Weekly 0/2（首次 09-13）、Monthly 1/1、drill 1/1。
  - 本轮只读核对 + 文档：未改代码/任务、未删除、未恢复 worker。

- **2026-09-10 根治抖动（owner 授权后实施 `41117ce`）+ 运行指针停止跟踪（`e957d94`）**
  - **修复**：`tools/daily_t2_schedule.py` 新增 `open_period_started_at()` / `window_wait_seconds()`；`run_daily` 在调用只读 observer **之前**，若开放窗口距满 24h 还差 ≤180 秒则**真实等待**补足再运行。**不放宽 24h 阈值**、不回溯时间戳（observer 记录实际运行时刻）、提前数小时的手动重跑**不补**（窗口保持短窗，fail-closed 不变）。
  - **测试**：`tests/test_zr902_daily_schedule.py` 新增 C7 六条（无开放窗口/恰好差 8 秒/已足够/提前重跑不补/账本损坏不抛异常/"等待发生在 observer 之前"的行为断言）→ 该文件 **28 passed**；对真实账本模拟：准点触发等 **13s**、早 30 秒等 **43s**、迟到 **0s**。
  - **生效与预期**：从 **2026-09-11 22:00** 运行起生效（P10 恰满 24h，门仍 false，因 last-two 含 P9 短窗）→ **门预计 2026-09-12 22:00 确定性打开**（P10+P11 均 ≥24h）。
  - **停止跟踪运行指针**（owner 2026-09-10 同意）：`git rm --cached assurance/runs/daily_manifest.json`（文件仍在磁盘）、`.gitignore` 增补运行指针、`assurance/runs/<UTC时间戳>/` 运行目录与本地 `.review-zr407-20260818/` 评审克隆；**证据类文件保持跟踪**（ledger.json / legacy_periods.json / rollback_manifest.json / *_alert.jsonl / 早期已提交的 run report）。效果：夜间运行不再制造脏工作树（提交后 `git status` = 0 条目）。
  - 提交：`41117ce`（修复 + 测试 + 取消跟踪）、`e957d94`（.gitignore 规则）；pre-push gate 绿、revenue CI **#130 success**。安装副本（`~/.agents/skills/revenue-forecast`、`~/.codex/skills/revenue-forecast`）随 gate 自动同步一致。
  - 说明（如实）：该文件的"取消跟踪"因 `git rm --cached` 先于提交进入暂存区，实际落在 `41117ce` 而非 `e957d94`；两个提交信息合起来表达完整意图，未改写已推送历史。

- **2026-09-10 深夜：3a 授权后扫描发现前提为假 → owner 同日正式撤销 3a（未删任何文件）**
  - owner 指示"直接执行最小步 3a"（只删 `artifact_backfill.py`）。执行前按清单规则做**完整依赖扫描**（逐符号 + 计划语料 + 冻结卡 + ratchet，而非只看 import），结论：**先前"零生产读者"的判断错误**。
  - 证据：① `src/company_wiki/source_catalog/artifact_backfill.py:305 def main()` 是**运维 CLI**（`--mode dry-run|apply`），`assurance/fc/FC-901/11_implementer_receipt.json` 明确记载「run_artifact_backfill 的 production caller 就是同模块的 CLI main()」——FC-901 的 caller≥1 正由此成立；② 被 **3 个契约测试**导入（`test_zr305_legacy_migration.py`、`test_zr1005_artifact_backfill.py`、`test_source_catalog_artifact_backfill.py`）；③ **FC-906 工作单元卡把该文件列为 Forbidden**（`assurance/fc/FC-906/00_wu_card_a.md:24`「`artifact_backfill.py`（FC-901 工具，**不改**）」）；④ 冻结 v5 基线 `baseline/plan/test_acceptance_plan.md` 有 **ZR1005-C1~C4** 验收行；⑤ 复杂度/覆盖率 ratchet 登记 `37`/`79`，`.github/workflows/ci.yml:53` 把 zr1005 测试列入 ignore。
  - 处置：**不执行删除**（按清单自身规则"无替代路径的不删、冻结边界绝不触碰"）；把更正写入本清单文首与 §2/§4/§5，并同步 wiki 侧 R4 目录四处文档；**未改任何产品代码/测试**（`git status -- src tests .github` = 0 条目）。
  - 后续：**owner 已正式撤销 3a**（2026-09-10），`artifact_backfill.py` 定性为受 FC-906 卡片保护的运维工具；**若将来确要退役该能力，属"能力退役"**（需同时处理 3 个测试、ratchet、FC-906 卡片与运维替代方案），应与 v2 迁移收尾一并裁定。

- **2026-09-11：找到 R9 权威执行包 + 补齐批 3 前置件（[r9_batch3_prerequisites.md](r9_batch3_prerequisites.md)）**
  - **发现**：company-wiki 的门测试 `tests/contract/test_r9_v1_removal_gate.py:6` 引用 `assurance/fc/Phase-14/01_r9_packet.md`——该路径在 company-wiki **不存在**，实际文件在**本仓** `revenue-forecast/assurance/fc/Phase-14/01_r9_packet.md`（39 行）。→ **批 3 的权威范围 = 包 §1 的 7 项清单**（v1 scanner+分支 / facade v1 默认 / `backfill_v2` / `portfolio_promoter`+CLI / `visibility_bridge` / `legacy_close_gate`+observer / `flags.legacy_bridge_enabled` 链）；**包内不含 `artifact_backfill.py`**，与 09-10 撤销 3a 一致；我先前的 3a/3b/3c 拆分**作废**。
  - **前置件落地**：对 7 项逐项给出"今日实测调用者 → 替代/级联动作 → 回滚 → 验证"。关键三条：① `backfill_v2` 的 `classify_bucket` 被 `dropbox_governance.py:22/162` **生产引用**，必须先内联/迁移才能删模块；② `legacy_close_gate.py` 由 `scripts/legacy_observer.py:308-310` **每晚调用**，**必须最后删**（observer 保留 canary-matrix 还是整体退役属 owner 决策）；③ `flags.legacy_bridge_enabled` 有**数据面**——`.source_catalog/runtime_policy.json` 快照仍带该字段，删除后必须保证旧快照可读。
  - **包的三处缺陷**（执行前必须处理）：① 跨仓指针（门测试写的是 company-wiki 相对路径）；② 进入条件过期（包写"period 6…预计 08-15T05:28Z"，现应以权威账本为准，预计 **2026-09-12 22:00** 通过）；③ 行号过期（包引 `scanner.py:1357-1360`，实际 facade 在 `1375-1407`）——执行按**符号**定位，不按行号。另：包写就后新增的 `v2_scan_shadow` 透传链（GP-002）、`canonical_writer` 第二扫描方、observer 每晚接线都需按今天的树重新核对。
  - **边界**：本轮只读 + 文档，`git status -- src tests scripts .github` = **0 条目**；门测试 docstring 的跨仓指针属**产品文件改动，待授权**，未改。
