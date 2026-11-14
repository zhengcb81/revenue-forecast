# PWF · OWNERPKG-RF-INPUT-PREP-01（RF native forecast input 编制 + rf-job/1 提交）

- 包ID：`OWNERPKG-RF-INPUT-PREP-01`
- 分支：`codex/rf-input-prep-01`；worktree：`C:/Users/郑曾波/Projects/rf-input-prep-01-wt`
- 基线：`d347c4ab43c847432ea354446cfea2947bf81d28`（`codex/rf-job-facade-01` tip = `codex/dashboard-rf-b37-release` 线 + job façade）
- 开工时间：2026-11-08（UTC）
- 目标：为 Alibaba / MongoDB 各编制 schema 3.7 完整输入 → rf-job/1 `full_research` → 终态 → catalog 登记 → 交接 Dashboard

## 基线选择（需要说明的决策点）

包 §6 要求"基线=你仓当前已发布主线HEAD"。本仓存在两条并行线：

| 线 | HEAD | 内容 | 是否含 rf-job façade |
|---|---|---|---|
| `main` | `90c562ac` | D 线 docs/收口（42 commits，`main..facade` 之外的独立线） | 否（`git ls-tree main` 无 `scripts/rf_job_cli.py`） |
| `codex/rf-job-facade-01` | `d347c4ab` | B37 release 线 + rf-job/1 façade（`e4b38459`） | 是 |

`rf-job/1` 提交契约（包 §4）**只能**在 façade 线执行，且该线的 `codex/rf-job-facade-01` handoff §6 已明示"不能安全并线 main"
（main 是 docs-only D 线收口，并线=把 B37 基线整体并入）。因此本包以 façade 线 HEAD 为基线，
并在 handoff §"并线状态"登记显式并线交接任务（分支/SHA/条件/触发人）。

## 节点与状态

| # | 节点 | 状态 | 证据 |
|---|---|---|---|
| N1 | 读包 §1-§7、加载 revenue-forecast / filing-fetch 技能 | done | 本会话记录 |
| N2 | 仓/分支/worktree/基线盘点 | done | `git worktree add -b codex/rf-input-prep-01`；HEAD=d347c4ab |
| N3 | 源采集可用性判定（MongoDB / Alibaba） | done | `.planning/rf-input-prep-01/alibaba-blocker.json`、`requests/*.json`、`evidence/mdb-validation-chain.json` |
| N4 | MongoDB FY2025 10-K 原文逐页读取（收入附注/分部/确认政策） | done | `mdb-fy2025-10k.txt`（本地转文本，仅研究用） |
| N5 | MongoDB schema 3.7 输入编制 | done | `inputs/mongodb-fy2025-input.json`（v2 交付版，file sha256 `d82f9b45…`、146,551 B、canonical `6169ea8a…`；v1 的 `04d30eb0…`、v2 中间版 `6687a3b5…` 均已被取代） |
| N6 | 校验链 lint → fix_hashes → validate-only 全过 | done | `evidence/mdb-validation-chain.json`（3/3 exit 0，"valid"） |
| N7 | rf-job/1 提交 + 终态 | done | `rfjob-20261108-eb9f2a3ed336`（v2），status=succeeded，0 下载/0 付费；v1 `rfjob-20261108-ea663b8bd33e` 保留为历史 |
| N8 | job 内 publication registry 行（result_sha256） | done | `evidence/artifacts.json`（v2 `result_sha256=04768c27…`） |
| N9 | catalog 登记（`import-research-*`） | **NOT_RUN** | 见 findings F-03：需要 B34 trusted research-admission 包（recorder/run/step-ledger/deployment-updated + review receipt），本包未产出；伪造会失真 |
| N10 | Alibaba 输入/作业/登记 | **NOT_RUN** | `alibaba-blocker.json`：4 条采集路线全部具名失败 |
| N11 | 证据入库 + commit | done | 本目录 + 分家 commit |
| N12 | 独立 agent 重审（未参与实现） | done（round1 FAIL 1P1/3P2/3P3 → round2 FAIL 2P1/1P2/4P3 → round3 delta：**P1=0 / P2=0**（本轮修完后），P3 随交） | `review-report.md` |

## 硬边界核对

- 引擎零改动：`revenue_forecast.py` / `lint_input.py` / `fix_hashes.py` / `rf_job_*.py` / `report_catalog*.py` 全部未改（`git status` 仅新增 `.planning/rf-input-prep-01/`）。
- 预算：`limits_ref=owner-approved-1usd`（`max_cost_usd="1.00"`），实际 0.00 USD（0 新下载、0 付费模型调用、0 网络出站以外的重复采集）。
- 写域：仅本仓新分支/worktree 内 `.planning/rf-input-prep-01/`；未改 Dashboard 仓、未改 company-wiki 仓代码与数据。
- 未冒充：Alibaba 与 catalog 登记均按 NOT_RUN 如实登记（见 handoff `not_delivered`）。

## 并线交接任务（§8-3，不能安全并线）

| 项 | 内容 |
|---|---|
| 结论 | 不能安全并线 |
| 原因 | `main`（`90c562ac`）是独立 docs/D 线，`git ls-tree main` 无 `scripts/rf_job_cli.py` / `report_catalog_identity_cli.py`，包 §4 契约不可执行；façade handoff §6 已判定同结论 |
| 待并分支 | `codex/rf-job-facade-01`（facade `e4b38459`） + `codex/rf-input-prep-01`（本包，HEAD 见 `handoff.json.head_commit`） |
| 条件 | `main` 的 D 线收口（D4-06 ROOT 组合验收）完成；`scripts/` 全量回归通过；`e4b38459` 已是本包基线的祖先（实测） |
| 触发人 | RF owner |
| Dashboard 侧 | 不追踪分支名，按 `handoff.json.release_tag_or_commit_for_dashboard` 固定 commit 消费（本机仓无远端，本包不推送） |

## 后续（本包外，需另行派工）

1. **Alibaba**：CWP 修复 document `e39fbf9c…` 的 market 投影，或恢复 `dayu-us-sdk` discover，或 FF 允许 null market 绑定 → 用 `build_mdb_input.py` 改造成 Alibaba 版并重跑同一流程。
2. **catalog 登记**：另立 owner 包补齐 B34 trusted research-admission 协议（recorder/run、`execution/{scope,step-ledger,budget-observation,terminal,deployment-update-ff-reviewed}.json`、native captures、独立审查 receipt），再跑 `import-research-attempt` → `import-research-publication` → `list-reports` 验收。
