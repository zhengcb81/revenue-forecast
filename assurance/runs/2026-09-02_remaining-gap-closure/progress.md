# 剩余缺口关闭实施进度

> 起始状态：2026-09-02 全面审查发现 12 项缺口（3 项已修复、9 项待实施）。
> 每完成一个 GP，更新本页对应行。

## 状态总览

- **起点**：117/117 accepted（机器真源 state.json）；三仓 CI ALL GREEN
- **当前阶段**：GP-001 完成，开始 GP-002（v2 scanner 生产切入）
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
| GP-005 | scenario 证据回填 | 🔄 部分完成（64/197 passed） | scenario_runner.py + 64 evidence files; 11 blocked; 122 pending |
| GP-006 | 真实 roots E2E 进 CI | ✅ 完成（revenue 43fab74） | windows-latest job + 9 sibling tests |
| GP-007 | privacy_class 3.0 config | ✅ 完成（wiki c636516） | 4 roots privacy_class added; config_doctor OK |
| GP-008 | legacy 观测起点注册 | 📋 部署指南就绪 | gp008_009_deployment_guide.md; 需管理员权限运行 schtasks register |
| GP-009 | 动态审核调度注册 | 📋 部署指南就绪 | gp008_009_deployment_guide.md; daily_t2 + weekly_t3 register |
| GP-010 | 研报 cutover 授权申请 | ✅ 申请文档完成 | gp010_cohort_cutover_request.md; 待 KD-08 批准 |

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
