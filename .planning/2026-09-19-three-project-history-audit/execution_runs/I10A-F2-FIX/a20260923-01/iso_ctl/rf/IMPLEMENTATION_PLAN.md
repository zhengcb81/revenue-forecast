# 三项目改进路线图实施计划（revenue-forecast / filing-fetch / company-wiki）

> **2026-08-09 状态覆盖：`completed_historical_scope + superseded`。** R0–R9 的历史实施和提交保留为已完成证据；最新审查发现的 data-lake 泛化、Dropbox、SourceBundle/artifact 生产接线、latest 闭环、动态审核和代码质量缺口由 [FCAP r2](audit_review/2026-08-09_full_completion_assurance_plan/task_plan.md) 接管。本文件不再是活动进度镜像，也不得签发新的完成声明。

依据：`review_audit/roadmap.md`（R1-R9，2026-08-08 批准后生效）。
执行期间 roadmap.md 是唯一计划可信来源；本文件是执行进度镜像（阶段状态 + 验收证据）。

## 阶段总览

| # | 阶段 | 根因 | 优先级 | 状态 |
|---|------|------|--------|------|
| 0 | 止血：恢复 company-wiki 生产配置 | RC-4 (N-05) | 立即 | completed |
| 1 | R1.1 输入锚点绑定不变式 | RC-1 (N-01) | P0 | completed |
| 2 | R1.2 发布登记处 | RC-1 | P0 | completed |
| 3 | R1.3 跨仓库 conformance 链 | RC-1 | P0 | completed |
| 4 | R2 attestation 能力门 + 签名 | RC-5 (N-04/F-11) | P0 | completed |
| 5 | R3 filing 所有权终局收敛 | RC-3 (N-03/F-04) | P0 | completed |
| 6 | R4 环境与安装不变性 | RC-4 (N-05/N-06) | P1 | completed |
| 7 | R5 可执行验收与计划治理 | RC-2 (N-02/F-11) | P1 | completed（CI 接入项随 R8 解除） |
| 8 | R6 常态化对抗测试 | RC-6 (N-01 三代) | P1 | completed |
| 9 | R7 版本与发布纪律 | RC-7 (N-08/F-03) | P1 | completed（4.0.0 / schema 3.7） |
| 10 | R8 文档对齐与目标回填 | 全部 | P2 | completed |
| 11 | R9 Phase 10 重开——真模块拆分 | RC-2 遗留 (N-02) | P2 | 已立项（独立会话，结构目标有意红着） |

## 阶段 0：止血（N-05）
**Goal**: 恢复 company-wiki 生产配置到 git HEAD。
**Success Criteria**: `git diff config/source_catalog.yaml` 为空；恢复前后哈希记入 progress.md。
**Status**: pending

## 阶段 1：R1.1 输入锚点绑定（RED 先行）— 状态：completed（2026-08-08）
**Goal**: input_sha256 从自报变成可机器复验；N-01 全部变体关闭。
**Success Criteria**:
- [x] 4 个 RED 测试先红（D1/D2/回归钉住/invest 跨仓）
- [x] 修复后：`python -m pytest tests -q` 全绿（283 passed + 126 subtests）
- [x] `python review_audit/probe_anchor_swap.py` D2/D3 打印 REJECTED
- [x] `python review_audit/probe_invest_cross.py` 两行 REJECTED
- [x] invest-core 37 passed；E2E PASS；安装副本已同步（.agents/.codex MATCH，.claude 为 junction）
**证据**: review_audit/progress.md 会话 3；深根因（normalize_probabilities mutation data → 哈希/嵌入移至 _build_forecast_draft 尾部）
**Status**: completed

## 阶段 2：R1.2 发布登记处
**Goal**: append-only 登记处 + 行级哈希 + lookup/audit CLI + invest require_registered_input。
**Success Criteria**: 4 个 RED 测试转绿；`publication_registry.py audit` exit 0；formal 无登记处即失败。
**Status**: pending

## 阶段 3：R1.3 跨仓库 conformance 链
**Goal**: 三跳伪造 fixture（revenue 生成 → 攻击重签 → 三处全拒）。
**Success Criteria**: fixture 在 revenue/invest-core/invest-framework 三仓 CI 各跑一遍。
**Status**: pending

## 阶段 4：R2 attestation 能力门 + 主机签名器
**Goal**: 自填字符串即 formal 成为不可能；真签名路径可用。
**Success Criteria**: 无签名器 formal 拒绝/降级（按裁定）；伪签名/白名单外签名拒绝。
**Status**: pending

## 阶段 5：R3 filing 单 owner 收敛
**Goal**: 代码层消灭第二 owner。
**Success Criteria**: 守卫测试先红→删除后绿；filing_acquisition.py 不可导入。
**Status**: pending

## 阶段 6：R4 环境与安装不变性
**Goal**: 配置/安装/测试写路径 fail-closed 防护。
**Success Criteria**: config_doctor 异常 exit≠0；sync --check 进 pre-commit/CI；人为改动安装文件门红。
**Status**: pending

## 阶段 7：R5 可执行验收 — 状态：completed（2026-08-08）
**Goal**: completed 只能由机器证据支撑。
**Success Criteria**:
- [x] `tools/verify_plan_claims.py`：解析 task_plan.md completed 声明；未勾选项需豁免
      说明；progress.md 需证据块（测试命令+通过数+日期）；--json 机器可读；5 项单测绿。
- [x] 实测旧 task_plan.md：Phase 2-9 大量未勾选 → 伪完成机器证据（N-02 教训落地）。
- [x] `tests/test_structure_targets.py`：revenue_core ≤2500 行 + 无空壳包。
      **当前 2 项有意红**（revenue_core 3960 行；analysis/research 空壳）——显式标注
      "未达成"，R9 拆分后转绿；禁止静默提高上限（N-02）。
- [x] ~~verify_plan_claims 进 CI：推迟到 R8~~ — `superseded`：后续已有 verifier/CI 历史资产，但最新 current-triplet、FC receipt 与 95-scenario 总门由 FC-103/104/1101 重建；旧延期项不再独立 pending。
**Status**: completed（CI 接入项移至 R8）

## 阶段 8：R6 常态化对抗测试
**Goal**: 攻击即测试 + 模糊变异巡检 + 漂移探测器。
**Success Criteria**: 对抗套件全绿；mutation_patrol 语义变异被接受即 exit≠0。
**Status**: pending

## 阶段 9：R7 版本与发布纪律
**Goal**: 版本号与契约变更一致；CHANGELOG 自洽。
**Success Criteria**: 版本 bump（按裁定）；迁移 fixture；release_checklist 全绿。
**Status**: pending

## 阶段 10：R8 文档对齐 — 状态：completed（2026-08-08）
**Goal**: 文档与代码一致；伪完成条目 reopened。
**Success Criteria**:
- [x] compliance-contract.md search_event 必填表述修正（N-04 文档漂移）
- [x] SKILL.md：schema 3.7、attestation 能力门（REVENUE_ATTESTATION_PROVIDER）、
      发布登记处、host_signer 白名单说明
- [x] company-wiki README：tests/e2e 名实不符修正（指向 integration/ 真管线）
- [x] task_plan.md：15 个伪完成 Phase 标 `completed_in_name_only → reopened`
      （verify_plan_claims 机器核验）；工具对回填后计划 exit 0
- [x] verify_plan_claims 正则行尾锚定（reopened 段退出核验）
**Status**: completed

## 阶段 11：R9 真模块拆分 — 状态：completed（2026-08-08）
**Goal**: revenue_core 3960 行行为锁定式拆分。
**Success Criteria**:
- [x] Golden 行为锁（5 模型族：volume/capacity/subscriber/backlog/bank）：
      `tests/test_golden_behavior_lock.py`，拆分前后 hash 逐字节一致
      （E2E golden 亦未变：input=0e1cc8d4 result=fedcd224acf2）
- [x] revenue_core.py 3960 → **468 行**（目标 ≤2500）
- [x] 职责组迁移（ast 保真 + re-export，外部 `from revenue_core import X` 面不变）：
      contracts/{constants,document}.py、forecast/{calc,segments}.py、
      analysis/{sensitivity,confidence}.py、research/{drivers,targets,coverage}.py；
      空壳包全部填实（test_no_empty_placeholder_packages 转绿）
- [x] 无循环依赖（DAG：calc/constants ← 各模块 ← revenue_core）
- [x] 每次迁移全量测试 + golden 比对；跨仓 invest-core 41 / invest-framework 24 /
      filing-fetch 115 全绿
- [x] test_structure_targets 3 项转绿；mutation_patrol 零接受；
      release_checklist OK；drift_patrol 5 项 OK
- [x] callers 非空：re-export 后全部外部调用方（revenue_report/backtest/CLI/探针/
      invest-*）零改动通过（codegraph/导入面验证）
**Status**: completed

## 用户裁定记录
| 裁定项 | 问题 | 用户决定 | 日期 |
|--------|------|----------|------|
| R1.2 | 登记处方案：本地 JSONL vs 更重方案 | 本地 JSONL（按 roadmap 规格） | 2026-08-08 |
| R7 | 版本号：3.11.0 vs 4.0.0 | 4.0.0（R2.1 改 receipt 契约，schema 3.7，3.6 转 legacy） | 2026-08-08 |
| R2.1 | unattested formal 是否默认拒绝 | 默认拒绝（invest-core 策略可配降级并留痕） | 2026-08-08 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| （执行中记录） | | |
