# 三项目对抗性审查 — 实施计划

目标：以对抗性视角深入审查 revenue-forecast / filing-fetch / company-wiki 三个项目的
设计、架构、代码质量、测试（尤其E2E）、文档，回答三个问题：
1. 是否达成最初设计要求？
2. md文档中列出的历史问题/痛点是否被完整解决？
3. 实际使用中是否达成用户期待？

原则：不信任文档自述，一切以实际代码与可运行测试为准（plan drift detection）。

## Phase 1（读取规划文档，梳理目标与痛点）— 状态：completed
- [x] revenue-forecast: task_plan.md / SKILL.md / AUDIT_REPORT.md / audit_review（两轮历史审计）
- [x] filing-fetch: SKILL.md / E2E_DESIGN.md / pyproject / CI
- [x] company-wiki: README.md / ci.yml / docs/plans 各子计划
- [x] 汇总：各项目原始设计目标清单 + 历史痛点清单（findings.md 发现 4）

## Phase 2（结构与代码审查）— 状态：completed
- [x] revenue-forecast: scripts 结构（发现 N-02 空壳包/3922 行）、publication/attestation/registry 代码
- [x] filing-fetch: fetch_filing/contracts、live 测试守卫、pyproject（F-06 部分修复）
- [x] company-wiki: source_catalog/resolver/ensure、测试组织、CI

## Phase 3（E2E测试专项审查）— 状态：completed
- [x] E2E 真实性：两个 harness 均为真子进程+golden+双跑+变异自证（发现 N-10）
- [x] E2E 覆盖度：revenue=引擎级单 fixture；company-wiki e2e 名不副实（只测 config）
- [x] 实际运行：revenue 280 绿 / filing-fetch 117+4红(live) / company-wiki 1665 全绿（发现 7）

## Phase 4（对抗性核验）— 状态：completed
- [x] 历史 F-01~F-14 逐条对照代码与探针（发现 6：F-01/F-02旧面/F-10 真修复；F-04/F-07/F-08/F-11/F-13 部分；F-03 未解决）
- [x] 新攻击面：N-01 嵌入输入锚点漏洞（三探针动态复现，穿透 invest-core）
- [x] 环境核验：N-05 生产配置污染、N-06 安装漂移复现

## Phase 5（输出报告与路线图）— 状态：completed
- [x] findings.md 完整发现（N-01~N-11 + 已验证修复 + 测试基线）
- [x] roadmap.md 根因级改进路线图（R1-R9 + 动态发现能力矩阵 + 依赖图）
- [ ] 用户裁定后开始实施（当前明确不实施）

## 关键结论（详见 findings.md / roadmap.md）
- 设计要求达成度：业务引擎与结构门禁强；正式可信链存在新 Critical 缺口（N-01）。
- 历史痛点：两轮审计 14+6 项中约六成真实修复，四成部分/未解决/复发。
- 用户期待：引擎可用且确定性强，但本机实链路当前断裂（N-05）、安装漂移（N-06）。

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| bash 管道后 `$?` 捕获的是 tail 退出码，误判 sync exit 0 | 1 | 重跑 `python ... > NUL; echo $?` 确认真实 exit 1 |
| rg 在 bash 工具不可用 | 1 | 改用 grep 工具 |
| pyright LSP 对 sys.path 注入导入报噪音错误 | 1 | 确认为预先存在类型检查噪音（项目用 ruff），不影响运行 |
