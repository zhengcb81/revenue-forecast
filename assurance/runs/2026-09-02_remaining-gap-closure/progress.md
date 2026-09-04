# 剩余缺口关闭实施进度

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
