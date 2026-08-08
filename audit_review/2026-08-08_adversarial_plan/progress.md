# 审查进度日志

## 实施回执（WU-0.1 基线清单与只读保护）

```json
{
  "work_unit": "WU-0.1",
  "baseline_commits": {"revenue": "14770c1a3b90c4916d80240b72d74a73eae90743", "filing": "43330550fb3ea77d36acd92e26861377564a7607", "wiki": "325086af1a5d966f1f01b389109dd26d1b6a63bc"},
  "red_test_ids": ["test_requires_readonly_flag", "test_collects_baseline_facts", "test_catalog_opened_readonly", "test_probe_root_unchanged"],
  "red_exit_code": 1,
  "changed_files": ["tools/audit_baseline.py", "tools/tests/test_audit_baseline.py", "audit_review/2026-08-08_adversarial_plan/progress.md"],
  "focused_commands": ["python -m pytest tools/tests/test_audit_baseline.py -v"],
  "repo_commands": ["python -m pytest tests -q", "ruff check tools/audit_baseline.py tools/tests/test_audit_baseline.py"],
  "cross_repo_commands": ["python tools/audit_baseline.py --read-only --catalog <wiki>/.source_catalog/catalog.sqlite3 --config <wiki>/config/source_catalog.yaml --config <filing>/config/company_wiki.json --repos <3 repos> --probe-roots <dropbox>"],
  "tests_collected_before": 301,
  "tests_collected_after": 301,
  "skipped_tests": [],
  "network_calls": 0,
  "parser_calls": 0,
  "llm_calls": 0,
  "real_root_writes": 0,
  "real_root_hash_before": {"companies": "479d07d7336b9fcfdf52138987fa42ab5a0abb3130af901a5748f501b3b78e8d", "dayu": "370f26ee11ece9bbab90aadf9e77d2dcca45a74ed341c52a99bbac94f298d9d6", "dropbox": "0e352f5bad0328ad1966fa9a8880e6208fb23c626e5cb7d62036c59fff38dd46"},
  "real_root_hash_after": {"companies": "479d07d7336b9fcfdf52138987fa42ab5a0abb3130af901a5748f501b3b78e8d", "dayu": "370f26ee11ece9bbab90aadf9e77d2dcca45a74ed341c52a99bbac94f298d9d6", "dropbox": "0e352f5bad0328ad1966fa9a8880e6208fb23c626e5cb7d62036c59fff38dd46"},
  "config_hashes": {"source_catalog": "eb0018d9046c339d2d1074ba0d9d4603893ac7014e8407e1d060adb57d4b6db7", "root_policy_export": "c4567d5d19e23084eb7789cfafcca4e394c1ad86e1e45b216ca85ab58a7facef"},
  "mutation_proof": {"mode_rw_only": "green (no behavioral change, query_only still blocks)", "mode_rw_plus_no_query_only": "RED (test_open_catalog_readonly_rejects_writes failed)"},
  "reviewer": "agent-skills:code-reviewer (agentId ab036f82c1b11e84d)",
  "review_findings": [
    {"severity": "minor", "desc": "工具未自动采集测试收集数，由 receipt 手工记录", "resolution": "accepted as-is; collection 由 receipt 承担"},
    {"severity": "minor", "desc": "collect_catalog 内重复 PRAGMA query_only", "resolution": "accepted as-is; 纵深防御"},
    {"severity": "minor", "desc": "roots/scan_runs 降级时 error 仍为 None", "resolution": "fixed: 降级时写入 error 说明并重跑 5 passed + ruff 全绿"}
  ],
  "status": "accepted"
}
```

- WU-0.1 事实补充：生产 catalog 只读采样确认 user_version=0、3 roots、167 scan_runs、documents=23488、locations=46505、size=49,272,315,904 bytes、最近 scan `completed_with_errors`（dropbox `Product_Revenue_Forecast_Model.xlsx` empty file）；三仓 HEAD 与计划基线一致；company-wiki dirty（`llm_cost_log.csv`、`source_manifests/archive/`）为用户修改，本 WU 未触碰。

## 2026-08-08

- 新需求：用户明确 Dropbox 不应被排除，要求优先只改配置并补齐测试/案例；开始重新核验当前 config schema 是否能安全表达“只允许 dropbox_stock，不放开所有 directory”。
- 方法：继续按 planning-with-files 更新原三件套；产品实施仍未开始。

- 完成：完整读取 `planning-with-files/SKILL.md`，创建本轮隔离工作区。
- 完成：确认三个项目 CodeGraph 均已初始化并记录索引规模。
- 完成：盘点三个仓库根目录，确认历史规划与审计资产存在。
- 当前：Phase 1，恢复最初设计目标、历史问题和前次审查结论。
- 完成：用 CodeGraph 盘点三个项目结构；定位复用、下载抑制、冷启动、真实工具一致性等现有测试资产。
- 完成：枚举相关历史计划、审计、设计与验证文档，明确优先读取集合。
- 完成：读取 2026-08-03 `audit_review` 三份底稿，提取当时全量测试证据、14 项发现及 A-D 改进阶段；全部标记为“历史声明待复核”。
- 完成：读取 2026-08-08 `review_audit` 与后续实施镜像，提取 N-01~N-11、R1~R9 和声称的实施证据；识别 `IMPLEMENTATION_PLAN.md` 总览/正文状态冲突。
- 完成：读取 filing-fetch 历史规划、E2E 设计、SKILL 与变更记录；确认其确定性 E2E 不等价于三真实根目录复用验收。
- 完成：读取 company-wiki portfolio reuse 两轮规划与总设计；确认最终决策为 Strategy B 配置驱动只读复用，Strategy A 自动 promotion 已弃用。
- 完成：CodeGraph 深查 filing-fetch 与 company-wiki 复用主链；确认多根 handle 校验、dayu metadata enrichment、resolver 复用测试与 section 子系统存在，尚待生产配置/索引/调用证据闭环。
- 完成：核对当前双侧复用配置和三根文件资产；确认 Dropbox 虽被扫描配置引用，但未进入 reusable kinds 或 allowed handle roots。
- 完成：只读检查生产 catalog schema；确认 artifacts/evidence_spans 可承载衍生物谱系，但复用/只读策略仅存在于外部配置。
- 完成：确认三个真实根均已被生产 catalog 扫描；记录位置/文档/衍生物统计及连续扫描带错误状态。
- 修正：初次文件数受 `.gitignore` 影响，已用不受 ignore 规则影响的枚举纠正 companies 实际规模。
- 问题：一次 SQLite 查询引用不存在的 roots.read_only；已按 schema 改写待重跑。
- 问题：一次 artifacts/evidence 大 join 无输出；后续拆分单条查询并记录退出码。
- 完成：检索三项目现有复用、下载抑制、衍生物和新鲜度相关测试；识别组合场景与 consumer 零调用断言的明显空白。
- 完成：逐行审阅 reusable roots、download suppression、section/reconciliation、filing E2E、revenue client/source 测试；确认当前 E2E 是 companies-only reuse smoke，衍生物未进入 consumer 契约。
- 完成：审阅 resolver/acquisition 真实代码与 section 调用图；确认无 latest gap 语义、reuse 命中即跳过 discovery、resolver 全库扫描、section query 未接 consumer。
- 完成：生产 catalog 只读抽样多根财报；观察到 company_raw 多期共存、dayu `.rejections` location 与 upstream_rejected 文档，已转化为状态过滤验收项。
- 完成：审阅 SourceCatalog.query 与 EvidenceQueryService；确认 query 未排除 rejected/quarantined、全表物化，且衍生物路径选择缺少完成/绑定/版本门。
- 完成：读取 core-section 与 catalog-space-remediation planning 三件套及 company-wiki 主计划相关段；确认子计划状态/checkbox/DoD/实际执行存在系统性漂移，章节能力未接 consumer。
- 完成：审阅三仓库 CI/pre-commit/coverage 配置并执行测试收集；确认关键质量门未进 CI、company-wiki 通过 F811 ignore 容忍重复测试定义。
- 问题：一次 PowerShell 命令误用 bash 续行符，已改为数组参数并成功执行。
- 问题：一次 PowerShell 中文输出编码错误，已切换显式 UTF-8；未把乱码输出用作证据。
- 修改范围：仅新增 `audit_review/2026-08-08_adversarial_plan/` 下三个 Markdown 工作文件。
- 完成：三仓当前基线测试均通过——revenue-forecast `301 passed + 106 subtests`（12.86s）；filing-fetch 离线/隔离集 `115 passed, 1 skipped + 27 subtests`（55.58s，明确排除 real-tool conformance 与 download E2E）；company-wiki unit+contract `1608 passed`（362.56s）。这些结果仅证明现有收集范围，不代表用户全链路已达标。
- 完成：只读 Ruff 复核——filing-fetch 代码/测试/E2E 全绿；revenue-forecast 的产品相关目录有 185 个 Ruff 错误；company-wiki 配置口径仅报 1 个 unused import，但以 isolated F811 复核确认 `test_source_catalog_worker.py` 有 11 个重复测试定义，被项目级 ignore 隐藏。
- 完成：记录审查基线提交：revenue-forecast `14770c1a...`、filing-fetch `43330550...`、company-wiki `325086af...`。company-wiki 已有 `llm_cost_log.csv` 修改和 `source_manifests/archive/` 未跟踪内容，本轮未触碰；revenue 仅新增本审查目录。
- 当前：把审查结论、历史问题追踪、E2E 情景矩阵和弱模型执行闸门固化为最终实施计划；仍未修改任何产品代码、测试或配置。
- 已更新：原计划的工作包继续保留，并新增 Dropbox config-only 的 WU-2A.0~2A.5；长期 root-id RootPolicy 降为条件性 WU-2B，不再是启用 Dropbox 的前置。
- 已更新：在原 27 个 E2E 基础上增加 E2E-DBX-01~10，共 37 个唯一场景 ID；Dropbox 场景要求 runtime diff=0、两侧配置原子部署、跨进程零下载/零写入和真实只读 canary。
- 已更新：`findings.md` 汇总 34 项发现，新增 F-034 证明 config-only 可行性；保留分维度验收、两轮历史问题追踪、filing-fetch 专项矩阵和 14 项风险登记。
- 完成：最终自审确认 3 个 planning 文件存在、无 `待审查/待定义/TODO/TBD` 占位、原六项要求及追加 Dropbox 硬需求逐条映射，产品实施状态明确为全部 pending。
- 最终复核：计划中现有 37 个唯一 E2E ID、4 个 CONFIG-DBX 测试 ID、findings F-001~F-034；Markdown `git diff --check` 无异常，工作区仍只新增本审查目录。
- 最终修改范围：仅 `revenue-forecast/audit_review/2026-08-08_adversarial_plan/` 三个新 Markdown 文件；未触碰 filing-fetch/company-wiki 产品文件，未下载文件，未写生产 catalog。
- 本轮状态：规划与审查完成；等待用户后续明确授权后，才可从 WU-0.1 开始实施。
- 追加核验：CodeGraph 证明当前 `ROOT_KINDS` 仅含 company_raw/directory/dayu_portfolio，生产配置中 Dropbox 是唯一 directory root；因此无需 runtime 改动即可通过 YAML 追加 `directory`、filing JSON 追加 Dropbox path 启用。
- 追加计划：新增 WU-2A.0~2A.5、CONFIG-DBX-01~04、E2E-DBX-01~10、runtime forbidden-path diff、生产只读双层验收和精确回滚；若状态过滤负例暴露 F-024，先由独立 WU-3.1 修复通用 resolver，再部署 Dropbox 配置，不能在 Dropbox WU 偷改 runtime。
- 追加治理：新增弱模型 12 步执行清单、F-001~F-034 closure ledger 和“已知问题可闭环但未知缺陷不能绝对保证”的保证边界。
