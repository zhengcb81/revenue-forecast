# Closure Ledger — 2026-08-08 对抗性审查关闭账本

> 机器可读版本：`closure_ledger.json`（schema 1.0）。本文件是同一账本的人类可读视图。
> 全集 = findings.md 的 F-001~F-034 + 历史问题追踪矩阵每一行 + 风险 R-001~R-014 + 场景矩阵（task_plan WU-6.2）。
> 校验：`python tools/verify_closure_ledger.py --ledger ... --repo revenue --repo-dir ... [--repo filing --repo-dir ...] [--repo wiki --repo-dir ...]`。

## 0. 总览

| 集合 | 行数 | resolved/superseded/controlled | not_a_defect | partial/unresolved |
|---|---:|---:|---:|---:|
| 发现 F-001~F-034 | 34 | 29 | 4 | 1（F-034） |
| 历史矩阵 | 21 | 19 | 0 | 2（A-F06、C-Space） |
| 风险 R-001~R-014 | 14 | 13 | 0 | 1（R-014） |
| 场景 E2E-* | 30 | 29 | 0 | 1（E2E-R03） |
| **合计** | **99** | **90** | **4** | **5** |

**诚实的结论**：由于存在 partial 行（F-034 / A-F06 / C-Space / R-014 / E2E-R03），**不得宣称"上述问题全部消除"**。
可以宣称：本计划枚举的、可测试的 F/N/P/C 问题均被修复，或被明确分类为已失效/非缺陷；三项核心用户场景有持续测试和生产只读证据（WU-10.1 独立验收签字后）。

## 1. 关键分类理由

- **not_a_defect（4）**：F-001（CodeGraph 索引是工具事实）、F-002（历史资产分散是环境事实，隔离目录处理）、F-003（三仓角色接线是架构事实）、F-013（49 GB catalog 是真实规模，只读快照+采样处理）。
- **partial（5）**：见 §3。
- **superseded（25）**：每行 rationale 给出当前证明（CodeGraph / 删除 guard / compat test），未直接删行。

## 2. 状态速查（按集合）

### 发现
| ID | 状态 | 修复 WU | 关键证据 |
|---|---|---|---|
| F-001 | not_a_defect | — | CodeGraph 索引存在 |
| F-002 | not_a_defect | WU-0.1 | 工作文件隔离 |
| F-003 | not_a_defect | WU-3/4/5 | 三仓职责接线 |
| F-004 | superseded | WU-6.1/6.2 | 37 场景 registry + spy 计数 |
| F-005 | superseded | WU-0/1/7/8 | 旧结论被回执取代 |
| F-006 | superseded | WU-7.2 | N-01 锚点绑定 + mutation patrol |
| F-007 | superseded | WU-8.3 | verifier 三仓全绿（4/1/5） |
| F-008 | superseded | WU-6.2/6.3/9.1 | 场景矩阵 + 双配置门 + shadow |
| F-009 | superseded | WU-2A.2/3.1/3.3 | Strategy B 落地，promotion 无调用者 |
| F-010 | superseded | WU-3.1~3.3/6.2 | E2E-R01~R08 闭环 |
| F-011 | superseded | WU-5.1~5.4 | ArtifactHandle 9 门 + SourceBundle |
| F-012 | resolved_config_only | WU-2A.0~2A.2 | 双配置启用（hash 384ef481/cfcb8dbe） |
| F-013 | not_a_defect | WU-0.2/9.1 | 快照 + 只读采样 |
| F-014 | superseded | WU-2A.1/2A.2 | 配置契约测试取代 DB 列 |
| F-015 | partial | WU-6.2/9.1 | 披露机制有；生产错误未清零（R-014） |
| F-016 | superseded | WU-6.2 | 场景矩阵逐行落地 |
| F-017 | resolved | WU-6.2/6.3 | harness 名称与范围对齐 |
| F-018 | superseded | WU-5.1~5.4 | 跨仓衍生物消费闭环 |
| F-019 | resolved | WU-2A.1/2A.2 | doctor fail-fast + hash 固化 |
| F-020 | superseded | WU-4.1~4.3 | LatestPolicy + GapPlan |
| F-021 | superseded | WU-3.2 | SQL pushdown 1128→43ms |
| F-022 | superseded | WU-5.3 | query_source_bundle 接线 |
| F-023 | superseded | WU-3.1/4.1/3.3 | 生产抽样语义测试覆盖 |
| F-024 | superseded | WU-3.1 | query active-only + 防御 + mutation |
| F-025 | superseded | WU-5.1 | 9 fail-closed 门 |
| F-026 | superseded | WU-3.2 | 物化消除 + 上限 1000 |
| F-027 | superseded | WU-8.3 | 三仓计划声明 verifier |
| F-028 | superseded | WU-5.3/5.4 | 消费方调用数 + lineage 断言 |
| F-029 | superseded | WU-7.1 | 三仓 PR 门 |
| F-030 | superseded | WU-1.1 | AST 唯一符号门 |
| F-031 | superseded | WU-1.1 | 11 组重定义修复 |
| F-032 | superseded | WU-6.2/9.1/10.1 | 场景矩阵 + 生产证据 |
| F-033 | superseded | WU-1.2/7.1 | 185 ruff 清零 + 门禁 |
| F-034 | **partial** | WU-2A.0/2A.2 | 探针证伪 config-only；用户决策记录缺口 |

### 历史矩阵
| ID | 状态 | 修复 WU | 说明 |
|---|---|---|---|
| A-F01 | resolved | WU-7.1 | receipt 顺序/锚点 guard + CI audit |
| A-F02 / N-01 | resolved | WU-7.2 | 输入锚点绑定 + mutation patrol |
| A-F03 / N-08 | resolved | WU-8.2/8.3 | 版本对齐 + 声明 verifier |
| A-F04 / N-03 | resolved | WU-7.1 | 旧 owner 移除 + single-owner guard |
| A-F05/F12 | resolved | WU-8.2/8.3 | 文档/契约一致 |
| A-F06 | **partial** | WU-6.2/7.1 | synthetic harness 改善；CI sibling 浮动未消除 |
| A-F07 / N-07 | resolved | WU-7.1 | coverage 门以 pytest 收集为准（89%） |
| A-F08 / N-06 | resolved | WU-7.1 | sync 门（缺安装目标不算 drift 已修正） |
| A-F09 | resolved | WU-1.1 | worker 测试恢复执行 |
| A-F10 | resolved | WU-7.1/4.1 | 契约 registry + 9 mode 测试 |
| A-F11 / N-04/N-11 | resolved | WU-7.2 | attestation 防护 + cryptography 门 |
| A-F13 / N-09 | resolved | WU-1.1/1.2/7.1 | F811 移除 + ruff 门 |
| A-F14 | resolved | WU-4.2/4.3 | GapPlan + 授权 receipt 返回 |
| N-02 | resolved | WU-1.2 | 模块拆分收尾（25 常量删除） |
| N-05 | resolved | WU-0.1/2A.1/7.1 | 配置恢复 + hash 固化 |
| N-10 | resolved | WU-6.2/6.3 | 场景矩阵 + 命名纪律 |
| P-Strategy-B | resolved | WU-2A.2/3.1/3.3 | dayu 只读复用闭环 |
| P-Dropbox | **partial** | WU-2A.0~2A.2 | config-only 已启用；runtime 缺口（F-034） |
| P-Latest | resolved | WU-4.1~4.3 | LatestPolicy/GapPlan/授权 |
| P-Derived | resolved | WU-5.1~5.4 | 消费方 parser/LLM=0 |
| C-Space | **partial** | WU-8.3/0.2 | 4 周观察期未满，verifier 正确拒绝 |

### 风险
| ID | 状态 | 控制方式 |
|---|---|---|
| R-001 | controlled | 双白名单 + 契约 + 探针 |
| R-002 | controlled | directory root 集合锁 + 负例 |
| R-003 | controlled | fail-closed + mutation-proved |
| R-004 | controlled | LatestPolicy/GapPlan |
| R-005 | controlled | ArtifactHandle 9 门 |
| R-006 | controlled | 跨进程调用计数断言 |
| R-007 | controlled | SQL pushdown + 上限 + 探针 |
| R-008 | controlled | unique symbol gate |
| R-009 | controlled | doctor + hash 固化 |
| R-010 | controlled | registry + 命名纪律 |
| R-011 | controlled | metadata/fetch 分离 + receipt 门 |
| R-012 | controlled | 只读策略 + 全回执 0 写入 |
| R-013 | controlled | receipt + 时间门 |
| R-014 | **partial** | 披露机制有；7 天 SLA 观察未满 |

## 3. partial 行明细（不得宣称全部消除）

| ID | 剩余风险 | 依赖/门 |
|---|---|---|
| F-034 | scanner 不持久化 directory 根元数据 → Dropbox 正例复用未验 | 用户决策 config-only；正例 E2E 需 scanner 修复决策 |
| E2E-R03 | 同上（Dropbox 正例） | 同上 |
| A-F06 | filing CI 依赖相邻 company-wiki 浮动代码 | WU-7.1 部分（sync 门已进 CI） |
| C-Space | catalog 空间增长 4 周观察期未满（49 GB 趋势未反转） | WU-8.3 timed gate ≥28 天 |
| R-014 | 生产扫描持续 completed_with_errors；SLA 7 天观察未满 | E2E-F05 披露 + shadow 探针监控 |

## 4. 允许的声明（WU-10.1 已签字：accepted，2026-08-08）

WU-10.1 独立验收（agent-skills:code-reviewer aa2ec46bebdc35040）verdict=accepted：
三仓全量 343/1697/142 绿、三维度突变翻红还原、三根只读 canary、gap metadata-only、
parser/LLM=0 spy 断言、verifier 三仓全绿、config hash 精确复现（详见 progress.md WU-10.1 回执）。

1. "三根均可安全复用" —— 配置/负例/canary 证据（注意：Dropbox 正例受 F-034 限制，表述为"配置已启用 + 负例拒绝安全"）。
2. "latest 请求能识别并只补有效缺口" —— GapPlan + 授权 E2E。
3. "有效已处理资产会被 consumer 实际复用" —— E2E-D01~D06 调用计数断言。
4. "上述能力由跨仓 E2E 和生产只读 canary 持续守护" —— WU-7.1 CI + WU-9.1 shadow。

## 5. 复现命令

```bash
# closure ledger 校验（三仓）
python tools/verify_closure_ledger.py \
  --ledger audit_review/2026-08-08_adversarial_plan/closure_ledger.json \
  --repo revenue --repo-dir <revenue> \
  --repo filing --repo-dir <filing-fetch> \
  --repo wiki --repo-dir <company-wiki>

# planning claim verifier（三仓）
python tools/verify_plan_claims.py --plan-dir .
```
