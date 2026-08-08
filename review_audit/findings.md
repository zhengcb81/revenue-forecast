# 审查研究发现

## 发现 1：项目时间线与审查历史
- 日期：2026-08-08
- 内容：
  - revenue-forecast 经历过两轮审查：
    1. 2026-07-26 AUDIT_REPORT.md（第一轮审计）：Critical-1（output validator 非独立语义重算器，概率/目标/敏感性/禁止字段伪造可绕过）、Critical-2（pass receipt 签发过早）、High-1~5、Medium-1~3。
    2. 2026-08-03 audit_review/（第二轮审计）：发现 F-01~F-14，含 2 Critical（F-02 弱验证路径+snapshot重签 ACCEPTED；F-11 Phase 8 伪完成）、5 High、6 Medium、1 Low。第二轮审计只出了改进计划（阶段A-D），声明"不实施业务修复"。
  - 第一轮审计后有 13-Phase 改进计划（task_plan.md，声称 2026-07-30 全部完成，294 tests 绿）。
  - 第二轮审计的改进计划似乎已被实施：commit 1a6c7f9（08-04）"feat: Phase 6 audit fixes — strong publication, attestation, compatibility registry" 对应 audit_review 阶段 A（A1 两阶段签发、A2 attestation、B2 compatibility registry）。
  - 08-07 最新提交：engine E2E harness + auto-run on commit/CI（revenue 与 filing-fetch 均有）。
- 影响：本次审查必须重点核验 1a6c7f9 是否真正修复了 F-01/F-02/F-10/F-11/F-12，而非表面修复。

## 发现 2：filing-fetch CI 挣扎信号
- 日期：2026-08-08
- 内容：filing-fetch git log 显示 5e34345（hermetic full-chain E2E harness）之后有 15+ 个连续 "fix(ci)" 提交，全部在解决 PYTHONPATH/company_wiki 导入问题（015c509→8322b2a）。
- 影响：E2E 的"hermetic"声明与实际环境依赖（company-wiki 必须相邻 checkout）存在张力；CI 环境脆弱性是对抗性审查重点。

## 发现 3：company-wiki 当前状态
- 日期：2026-08-08
- 内容：近期工作集中在 source_catalog（portfolio reuse、MD&A section extraction、catalog space remediation、prune retired evidence）。有未提交变更：config/source_catalog.yaml、llm_cost_log.csv、未跟踪 source_manifests/archive/。
- 影响：catalog-space-remediation 计划 Phase 5/6 仍 pending（存储迁移、验收文档）。

## 发现 4：三项目设计目标（来自 SKILL.md/README）
- revenue-forecast（v3.x，schema 3.6）：从来源可追溯的经营驱动构建可审计的分部收入预测。核心承诺：
  a) 正式输出必须经 validate_published_forecast（强验证、需输入）+ publication receipt 在验证后签发；
  b) 11 步强制工作流（九维覆盖、信息集冻结、管理层目标门、历史/base 核对、来源/参数登记、收入曲线拆分、收入确认、三情景、驱动树、聚合bridge、敏感性、置信度、验证交付、冻结回测）；
  c) 大量 Hard failure gates；
  d) 范围纪律：只做收入，不做估值/评级；非收入分析移交 invest-*；
  e) filing 获取委托 filing-fetch（内置 filing_acquisition.py 已弃用）；
  f) 输入构建辅助工具（generate_input_template/lint_input/fix_hashes）。
- filing-fetch（v1.4.0）：按需、市场路由、reuse-first 获取财报入 company-wiki。核心承诺：
  a) schema 1.1 精确字段、拒绝未知字段、禁止显式 entity 请求；
  b) identify→resolve(reuse)→ensure(download, 需授权)→validate handle 深验证；
  c) worker pause-around 下载；deadline/timeout；fail closed；
  d) 所有权边界：identity/catalog/下载/去重/canonical 写归 company-wiki；跨技能请求/授权/handle 验证归 filing-fetch；消费侧记录归消费技能。
- company-wiki：上游公司资料供应与来源智能平台。核心承诺：
  a) 不可变来源（原文+SHA-256+采集器版本+来源时间）；
  b) 证据定位（页码/段落/表格坐标/稳定 locator）；EvidenceSpan；
  c) source manifest + 只读 export（版本化契约、exact_highest 协商、fail closed）；
  d) canonical IngestService（不下载、不写研究语义）；
  e) source_catalog：分布式原始资料索引、后台 worker（空闲+电源门控）、统一下载入口（A股 StockInfo / HK-US dayu）、portfolio reuse；
  f) 产品边界：只做上游来源/解析，不做研究语义/投资结论（BOUNDARY-0）。

## 发现 N-05（Major，环境）：company-wiki 生产配置被测试夹具污染，实链路当前断裂
- company-wiki config/source_catalog.yaml（未提交的工作树修改）被覆写为单行 JSON 夹具：
  `{"schema_version":"1.0","catalog_dir":"config/.source_catalog","roots":[{"root_id":"fake","path":"/tmp",...}]}`
- 真实 catalog 在 `.source_catalog/security_master/{cn,hk,us}.json`（存在且完好），原配置
  `catalog_dir: "${PROJECT_ROOT}/.source_catalog"` 被改成相对路径 `config/.source_catalog`。
- 直接后果：filing-fetch 4 个 live conformance 测试失败（identify CN/HK/US + ambiguous），
  错误为 "no security-master snapshots found in ...config\.source_catalog\security_master"。
  本机 filing-fetch→company-wiki 实链路当前不可用。
- skip 守卫不足：test_real_tool_conformance.py::_wiki_available 只查 source_catalog.yaml 存在，
  不查 security_master/配置有效性，导致"应 skip 的 live 测试"变成红。
- 污染源未在代码中找到（filing-fetch/company-wiki 均无该字符串），疑似调试会话手写；
  说明缺少"生产配置完整性"防护与测试写路径审计。

## 发现 N-06（F-08 复发）：安装副本再次漂移，且无强制门
- tools/sync_installations.py 默认检查 .agents/.claude/.codex 三目标，漂移时 exit 1（实测正确）。
- 当前实测：.agents 漂移 3 文件（.gitignore、scripts/filing_fetch_client.py、tests/test_filing_acquisition.py）；
  .codex 漂移 2 文件；.claude 一致。
- 漂移方向值得警惕：.agents 版 filing_fetch_client.py 含 canonical 没有的 --no-pause-worker
  支持——安装副本领先/分叉于 canonical，正是 F-08 要消灭的"多状态并存"。
- sync 检查未进 pre-commit/CI，漂移无人拦截。

## 发现 N-07（F-07 移动球门）：分模块 coverage 门存在但阈值按现状设定
- tools/run_coverage_gates.py 实测 exit 0，但阈值：filing_fetch_client 40%（实际 51%）、
  company_wiki_source 60%（实际 77%）、revenue_forecast 60%（实际 81%）、核心模块 70%。
- 计划 Phase 0 原文是"新模块 statement coverage 目标不低于 90%"。跨项目关键边界
  filing_fetch_client 仅 51%，其 CLI 主路径 179-240 行大面积未覆盖。

## 发现 N-08（F-03 未解决 + 文档自相矛盾）
- SKILL_VERSION=ENGINE_VERSION=3.10.0、SCHEMA=3.6（实测）。Phase 6 重大契约变更
  （两阶段签发、host_receipt 必填、compat registry）全部挂在 CHANGELOG "Unreleased"。
- host_receipt 成为 capture 必填字段是破坏性输入契约变更：3.10.0 时代旧输入将无法通过验证，
  但版本号未动、无迁移条目（违反计划 0.3.10 规则）。
- CHANGELOG 同一 Unreleased 段内两条矛盾记录：旧条目（行31-34）写
  "drafts, publishes (signs publication receipt...), runs the output validator"（先签后验），
  Phase 6 条目（行63-68）写先验后签。F-12 在 compliance-contract 修好，CHANGELOG 仍留反序陈述。

## 发现 N-09（F-13 部分 + CI 无 ruff 门）
- company-wiki ruff 从 6 项降为 1 项：tests/contract/test_source_catalog_reusable_roots.py:13
  unused pytest import（新增测试文件引入的新回归）。
- company-wiki CI（ci.yml）只跑 unit+contract（3.11-3.13 矩阵）+ CLI smoke + secret scan，
  无 ruff 门、不跑 integration/acceptance。
- revenue CI（quality.yml）只跑 pytest + engine E2E，无 ruff/compileall/coverage/sync 检查；
  pre-commit（已配置 hooksPath=.githooks）也只有 pytest + E2E。

## 发现 N-10（E2E 真实性与范围）
- 两个 E2E harness 均为真：真子进程跑 CLI、golden 按语义哈希键控、双跑确定性、
  有变异自证记录；实测均 PASS（revenue input=bb8e3984c13e；filing-fetch golden=biren-e2e-v1）。
- 范围局限（E2E_DESIGN.md 已诚实声明）：revenue E2E 只覆盖引擎计算+1 个 fixture（biren），
  不覆盖 11 步研究工作流的 agent 行为面；23 个模型中仅覆盖该 fixture 用到的少数。
- company-wiki tests/e2e/ 只有 test_config_loading.py（名不副实）；真实管线覆盖在
  integration/（test_full_pipeline.py 等），但 CI 不跑 integration/acceptance。
- filing-fetch CI 显式 --ignore live/download 测试；本地有生产 wiki 时 live 套件必跑且当前红（N-05）。

## 发现 N-11（验证上下文的语义边界，设计性）
- VerificationContext 可由任何知道算法的人重算（probe 即如此构造）；receipt 不是密码学证书，
  而是"强验证曾运行"的结构化声明。安全性完全依赖消费者重新运行 validate_published_forecast。
  这是已文档化的诚实设计（compliance-contract Trust boundary 表），但必须配合 N-01 修复
  （绑定实际验证的输入）才成立。invest-core 已走强路径（invest_contracts.py:369-378），
  但被 N-01 穿透（probe_invest_cross.py 实测 ACCEPTED）。

## 发现 7：测试套件实跑基线（2026-08-08）
| 项目 | 结果 |
|---|---|
| revenue-forecast pytest | 280 passed（与声称一致）|
| revenue engine E2E | PASS |
| revenue ruff/compileall | 全绿 |
| revenue coverage gates | exit 0（但阈值按现状设定，见 N-07）|
| revenue sync check | exit 1（.agents/.codex 漂移，见 N-06）|
| filing-fetch pytest | 117 passed / 4 failed（live，因 N-05）/ 6 skipped |
| filing-fetch E2E | PASS（hermetic 自建种子生效）|
| filing-fetch ruff/compileall | 全绿 |
| company-wiki pytest | 1665 passed / 0 failed（384s；F-09 竞态未复现）|
| company-wiki ruff | 1 error（N-09）|

## 发现 5：E2E 现状
- revenue-forecast e2e/：引擎级 E2E（run_revenue_forecast_e2e.py + golden expected/），golden 按 canonical input sha 键控，双跑确定性、强验证断言、变异自证。纯引擎离线，不涉及 wiki/网络。08-07 新增，pre-commit + CI 自动运行。
- filing-fetch e2e/：全链路 E2E（run_filing_fetch_e2e.py + golden），synthetic seeds 自建（不依赖生产 companies/），但依赖相邻 company-wiki checkout（CI clone 到 $HOME/Projects/company-wiki）。
- company-wiki：tests/e2e/ 存在（待查）；tests/contract/ 有 source_catalog worker 契约测试。
- 关键疑问：revenue E2E 只覆盖引擎计算，不覆盖 11 步工作流的 agent 行为面（这部分靠 lint/gate 测试）；filing-fetch E2E 的 hermetic 是"半 hermetic"（依赖 company-wiki 代码但不依赖生产数据）。

## 发现 N-01（新 Critical）：嵌入 input_document 未绑定 input_sha256，锚点可冒用
- 日期：2026-08-08（动态复现，三个探针）
- 背景：Phase 6 A1 修复让 run_forecast 把 input_document 深拷贝嵌入结果（revenue_core.py:2160），
  使无 input 的消费者也能走强验证（validate_forecast_output 调度器从 result["input_document"] 取输入）。
- 缺口：revenue_report.py::_validate_forecast_output **从不校验** canonical_sha256(input_document)==input_sha256。
  snapshot 路径有该检查（revenue_backtest.py:97-99），独立 result 路径没有——不对称。
- 复现（review_audit/probe_embedded_input.py、probe_anchor_swap.py、probe_invest_cross.py）：
  1. D1：整体替换嵌入输入（保持原 input_sha256），重签 receipt/result hash → validate_forecast_output ACCEPTED。
  2. D2：把 13 个 assumption/stress 参数 ×1.5 重跑引擎（base 终值 181.5→272.25，+50%），
     把结果 input_sha256 改回合法锚点，重签所有 hash → validate_forecast_output ACCEPTED。
  3. 跨仓库：invest_contracts.validate_revenue_forecast(forged) ACCEPTED；adapt_revenue(forged) ACCEPTED。
     伪造数字进入 invest-* 正式消费边界。
  4. 对照：同样手法对 snapshot → REJECTED（validate_snapshot 有指纹绑定）；
     仅改参数不重跑引擎 → REJECTED（敏感性重算生效）。
- 影响：设计目标 3（"不可通过改结果+重算 hash 绕过"）在新攻击面下未达成；
  与 F-02 同族但攻击面是 Phase 6 修复本身引入的。攻击者需要能构造完整合法输入——
  这正是 generate_input_template/lint_input 工具链降低门槛的事，且项目威胁模型明确包含"不诚实 agent"。
- 修复建议（一行级）：_validate_forecast_output 中，若 result 含 input_document，
  require canonical_sha256(result["input_document"])==result["input_sha256"]；
  若显式传入 data，require canonical_sha256(data)==result["input_sha256"]。补 RED 测试。

## 发现 N-02（Major）：Phase 10"物理模块拆分"伪完成
- task_plan.md Phase 10 标 completed，但 10.1 全部 11 个拆分项复选框未勾选，10.4 完成标准
  （revenue_core 只留编排）未达成：revenue_core.py 现 3922 行（审计时 2324 行，反而 +69%）。
- 唯一被抽出的 scripts/forecast/compute.py（435 行）从未接入，Phase 14 commit 89b2d0c 自认
  "Phase 10 extraction never wired in; revenue_core keeps its own copies"，删除死代码使
  coverage 82%→87% 从而通过 --fail-under=84 门（以删未测代码提覆盖率）。
- 残留空壳目录：scripts/analysis/、scripts/research/ 只有空 __init__.py；scripts/forecast/ 只有 __pycache__。
- audit_review 第二轮审计的核验矩阵 #9 却判"达成"（理由：publication/contracts/constraints/backtest/report
  已拆，revenue_core 高密度是"文档化停点"）——与 Phase 10 原始完成标准不符，属降低标准的追认。

## 发现 N-03（Major）：F-04 旧 filing owner 只封了 CLI，库级双活仍在
- filing_acquisition.py::main() 已 hard-fail（实测返回 deprecation error，exit 3）✓
- 但模块仍导出完整可用 owner：resolve_filing/AcquisitionManager/AdapterRegistry/
  CanonicalSourceWriter/DayuCliAdapter 等（__all__ 明列），AcquisitionManager.resolve
  含完整 subprocess 下载路径（filing_acquisition.py:1931-1985）。
- Python 调用者仍可 from filing_acquisition import resolve_filing; resolve_filing(request=..., allow_download=True)
  绕开 filing-fetch/company-wiki 的 identity/journal/契约门。
- SKILL.md 称该模块"retained only for legacy test fixtures"——与实际能力不符（文档漂移）。

## 发现 N-04（F-11 部分达成）：attestation 结构化但无 trusted-verifier fail-closed 门
- 已做：host_receipt 成为 capture 必填字段并结构验证（contracts/evidence.py:234-266）；
  not_available 管理沟通强制 machine-generated search_event（revenue_core.py:3297-3326，实测必填）；
  compliance-contract.md 明确 trust boundary 表格，承认 host trust 依赖；要求交付附 TRUST_BOUNDARY.md。
- 未做：Phase 8 原始要求"无 trusted verifier 只能 draft"的 fail-closed 能力门不存在
  （全库无 trusted/unattested capability 判断）；host_receipt 各字段（issuer/environment/event_sha256）
  仍由输入作者自填，无独立 verifier 验证。formal 模式在任何环境下都可签发。
- 文档内部漂移：compliance-contract.md:61 称 search_event "optional"，代码实际强制必填。
- 判定：若以 Phase 8 原文为基线=未达成；若以现行文档化设计（诚实声明 host trust）为基线=一致。
  第二轮审计 A2 计划的第 1/2 条（runtime capability + 独立 verifier）未实施。

## 发现 6：已验证为真实的修复（对抗核验通过）
- F-01（receipt 签发顺序）：run_forecast 实际 draft→validate_published_forecast→签发（revenue_core.py:2227-2243）。✓
- F-02 旧攻击面：probe_snapshot_forgery.py 全知攻击者两路均 REJECTED。✓
- F-10（engine 兼容矩阵）：schema_compatibility.py 不可变 registry，3.4 接受 3.5.0-3.10.0（修过窄），
  未知 engine fail closed（修过宽），output/snapshot 共用。snapshot validator 已接入（revenue_backtest.py:94-96）。✓
- snapshot 路径强验证：validate_snapshot 调 validate_published_forecast(result, input_document)，
  且有输入指纹/身份字段/snapshot_id 多重绑定。✓
- invest-core 已升级为强路径消费（invest_contracts.py:369-378 用嵌入 input 走强验证）——
  但被 N-01 穿透。
