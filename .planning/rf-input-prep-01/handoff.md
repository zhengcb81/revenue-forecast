# OWNERPKG-RF-INPUT-PREP-01 · 交接文件（handoff）

- 包ID：`OWNERPKG-RF-INPUT-PREP-01`（关联 Dashboard 缺口 G-m5-EXT-01）
- 日期：2026-11-08（UTC）
- 分支：`codex/rf-input-prep-01`；worktree：`C:/Users/郑曾波/Projects/rf-input-prep-01-wt`
- **基线 commit**：`d347c4ab43c847432ea354446cfea2947bf81d28`（`codex/rf-job-facade-01` tip）
- **内容交付 commit**：`0993abb305dc86a2197b8b2aee10a3b8d8339949`（输入 + 作业 + 快照 + 诊断 + 六路线证据全部在该 commit 内）
- `release_tag_or_commit_for_dashboard` = 同上（40 位、`git rev-parse` 可解析）
- 说明：交接记录本身由本分支后续 commit 维护；上面 pin 的是**自包含内容 commit**（输入/作业产物/证据全部可在该 commit 解析）。权威 handoff = 本分支 tip。
- PWF：`.planning/rf-input-prep-01/`（`task_plan.md` / `progress.md` / `findings.md` / `evidence/` / `review-report.md`）

## 0. 收尾状态（最终快照 · 2026-11-08）

**交付判定：部分交付（partial delivery）。** MongoDB 全链完成；Alibaba 与 catalog 登记为 NOT_RUN，`G-m5-EXT-01` 不解除。
独立审查最终计数：**OPEN P1 = 0 / P2 = 0 / P3 = 4（均为已披露限制）**。

### 0.1 提交地图（按角色区分）

| 角色 | commit | 内容 | 谁用 |
|---|---|---|---|
| 基线 | `d347c4ab43c847432ea354446cfea2947bf81d28` | `codex/rf-job-facade-01` tip（B37 线 + façade `e4b38459`） | 追溯 |
| **内容交付 commit** | `0993abb305dc86a2197b8b2aee10a3b8d8339949` | 输入、job 产物副本 + manifest、冻结快照、诊断、六路线证据、blocker **全部可在该 commit 解析** | **Dashboard 绑定点** |
| handoff commit | `0afcb16fdfcb0d20be16c175860378c9994286c1` | pin 上表内容 commit；`handoff.json/md` 定稿 | 读取交接 |
| 审查记录 commit | `42bee755f3385f9b95504a8857c1bdaa542792a7` | round 4 确认 + `handoff.json.review.round4` | 审计链 |

> 本表 pin 的三个 commit 不随文档更新而改变；`HEAD` 会因后续 handoff/PWF 文字提交前移。
> 一个 commit 无法包含自身 SHA，因此 `head_commit` 指向**自包含内容 commit**；handoff 记录由其后 commit 维护（偏离 D5，已登记）。

### 0.2 关键哈希（可在内容 commit 用 `git cat-file -p <rev>:<path> | sha256` 复算）

| 对象 | 路径 | sha256 | 字节 |
|---|---|---|---|
| 输入文档 | `inputs/mongodb-fy2025-input.json` | `d82f9b45cefddfba5d52e2abf1e35dba553a1722b1d181818dda78ba0236a993` | 146,551 |
| 引擎 canonical 输入 | 同上（内容哈希） | `6169ea8aca81638d83026153474d584ca19be38c166bb71ab0ae4e76924cde59` | — |
| 计算产物副本 | `evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__result.json` | `c0dce8c3df7e49431a351de67d15847db40a4ffd7bfa140cf378db437b017963` | 326,471 |
| 报告 Markdown | `…/stages__compute__report.md` | `0bae0856fd4e658b456b1808bec06da937d08c5fa76b2d8e421a76fcbba20e63` | 53,291 |
| 冻结快照 | `evidence/mongodb-fy2025-snapshot.json` | `4798e682d65c7ccec31742bb5095eb19e832175f942a9f6d4139b79d51007e4c` | 398,344 |
| 支持诊断 | `evidence/mongodb-support-diagnostics.json` | `564b72f09ecb…` | 9,347 |
| job registry 行 | `…/registry__publications.jsonl` | `ca8a2e35…`（line sha256） | 710 |

两个"结果哈希"不是同一个量（findings F-16）：引擎 `result_sha256=04768c27…`（对去掉该字段的 payload 求 canonical 哈希）；
快照 `forecast_result_sha256=4587acc8…`（对完整冻结 dict 求哈希）。二者标识同一预测，不可互换核对。

### 0.3 走的是哪些模块接口（无一处 harness 自办）

| 动作 | 模块公开接口 | 产物 |
|---|---|---|
| 输入骨架对照 | `scripts/generate_input_template.py` | `evidence/template-skeleton.json`（字段零缺失） |
| 输入静态校验 / 哈希同步 / 全量校验 | `scripts/lint_input.py`、`fix_hashes.py`、`revenue_forecast.py --validate-only` | `evidence/mdb-validation-chain.json`（绑 `input_sha256=d82f9b45…`） |
| 源准备（MongoDB） | `scripts/source_preparation.py` → filing-fetch → company-wiki | `requests/mongodb-envelope.json` |
| 源采集（Alibaba 六路线） | 同上（filing-fetch 内 market/ensure 路由） | `evidence/route1..6-*.stderr.json`、`evidence/alibaba-routes.json` |
| 作业编排 | `scripts/rf_job_cli.py`（submit/act/get-status/list-jobs） | `evidence/mdb2-{submit,status,list}.*` |
| 出版审计 | `scripts/publication_registry.py audit` | job `registry/publications.jsonl` |
| 冻结快照 | `scripts/revenue_backtest.py create` | `evidence/mongodb-fy2025-snapshot.json` |
| 证据支持诊断 | `scripts/research_support_diagnostics.py` | `evidence/mongodb-support-diagnostics.json` |
| 产物入库复制 | `.planning/.../copy_job_artifacts.py`（复制 job store 字节，**不重算**） | `evidence/job-<job_id>/` + `manifest.json` |
| catalog 只读核对 | `scripts/report_catalog_cli.py list-reports` | exit 2 `owner_root_missing`（F-03 证据） |

> 被否决的越界路线：自己下载 20-F 再 `company-wiki official import`（只查过 SEC 元数据索引，未取正文，未写 catalog），
> 见 findings F-15；采集归属 filing-fetch/company-wiki。

### 0.4 仍需他人动作（本包外）

| # | 事项 | 归属 | 解除条件 | 我能立即接手的动作 |
|---|---|---|---|---|
| 1 | Alibaba 采集 | company-wiki owner（`market` 投影）/ filing-fetch owner（null market 绑定）/ 环境（`dayu-us-sdk`） | 六路线中任一条返回 `found` 且 `capture_ready=true` | 用 `build_mdb_input.py` 改出 Alibaba 版，同一流程出输入→作业→报告 |
| 2 | catalog 登记与 `list-reports` | owner/D00 交付协议 | 产出 B34 trusted research-admission 包（recorder/run/step-ledger/terminal/review receipt） | 登记后按 `list-reports --entity-id …` 附报告 ID 与 `result_sha256` |
| 3 | 并线 `main` | RF owner | main 的 D 线收口 + `scripts/` 回归 | 执行 task_plan §并线交接任务 |
| 4 | 管理目标台账（MongoDB） | 本包后续 | 取到官方业绩发布/电话会原件（同样须经 filing-fetch/company-wiki 或既有 web 研究通道） | 按 `independent_benchmark` 建目标台账并重跑作业 |

## 1. 交付了什么

| 交付物 | 状态 | 位置（均在交付 commit 内） |
|---|---|---|
| MongoDB schema 3.7 输入（v2，含口径声明） | delivered | `inputs/mongodb-fy2025-input.json`（file sha256 `d82f9b45…`，146,551 B） |
| 三步校验链（lint / fix_hashes / validate-only） | PASS 3/3 | `evidence/mdb-validation-chain.json` + `evidence/mdb-{lint,fix-hashes,validate-only}.stdout.txt` |
| rf-job/1 `full_research` 作业到终态 | succeeded | `rfjob-20261108-eb9f2a3ed336`（首次 submit 即成功，3 阶段各 1 attempt 全 exit 0） |
| 计算产物（job 内） | delivered | `job-root/.../stages/compute/result.json`（本地 job store，未入库） |
| **入库的产物副本** | delivered | `evidence/job-rfjob-20261108-eb9f2a3ed336/`（10 个文件 + `manifest.json`，逐文件 sha256） |
| job 内 publication registry 行 | delivered | `evidence/job-…/registry__publications.jsonl`（line sha256 `ca8a2e35…`） |
| 冻结快照（`revenue_backtest.py create`） | delivered | `evidence/mongodb-fy2025-snapshot.json`（`input_sha256=6169ea8a…`、`forecast_result_sha256=4587acc8…`） |
| 证据支持诊断（`research_support_diagnostics.py`） | delivered | `evidence/mongodb-support-diagnostics.json` |
| Alibaba 输入/作业 | **NOT_RUN** | `alibaba-blocker.json` + `evidence/route{1..6}-*.stderr.json` + `evidence/alibaba-routes.json` |
| catalog 登记（`import-research-*`） | **NOT_RUN** | `findings.md` F-03 |

## 2. MongoDB 结果摘要（可复核）

- 引擎 4.3.0 / schema 3.7；`result_sha256=04768c2742d663e3e7ac748c9fde8c7648cc1cd0e424e4d931e150379c038816`
  （`input_sha256=6169ea8a…`，canonical）
- 基准年 FY2025（10-K，财年结束 2025-01-31，filed 2025-03-21）：US$ 2,006.443m
- 口径：`rf-revenue-basis/1`，operations=total、statement_status=as_reported、period_kind=fiscal_year（报告"口径"列显示"总额/原表"）
- 三段（披露口径，Note 9）：Atlas-related 1,405.184 / Other subscription 538.680 / Services 62.579（合计=总收入，精确对账）
- 情景（US$m）：

| 年 | low | base | high |
|---|---|---|---|
| 2026 | 2,180.071 | 2,316.536 | 2,443.711 |
| 2027 | 2,315.671 | 2,650.175 | 2,929.059 |
| 2028 | 2,424.255 | 2,993.792 | 3,448.819 |
| CAGR | 6.51% | 14.27% | 19.79% |

- 置信度 49.0（`low`）；limitations 如实包含：direct 回退模型、3 个 research data gap、单源未三角化、无历史回测。
- 管理沟通 6 类全部 `incomplete`（逐条写明读到/未读到）；`management_targets=[]`（未取到官方数字目标，故不登记目标）。
- v1 作业 `rfjob-20261108-ea663b8bd33e` 仅为历史：v1 输入含渲染式表格 excerpt 且无口径声明，已被 v2 取代（见 findings F-11/F-13）。

## 3. Alibaba 为什么 NOT_RUN（采集层，6 条路线，全部经 filing-fetch → company-wiki）

所有路线都由 `scripts/source_preparation.py` → `filing_fetch_client` → filing-fetch skill → company-wiki 驱动；零下载、零付费。
没有一条路线由本 harness 自行下载或手工登记（详见 findings F-15）。

| # | 路线 | 机器原因（实测） | 证据 |
|---|---|---|---|
| 1 | HK 09988 FY2026 `reuse_only`（exact） | `company-wiki source query market mismatch`（calls 2，downloads 0） | `evidence/route1-hk-fy2026-reuse.stderr.json` |
| 2 | HK FY2026 `fetch_if_missing`（exact, reuse-first ensure） | `company-wiki operation market mismatch`（calls 2，downloads 0） | `evidence/route2-hk-fy2026-fetch-if-missing.stderr.json` |
| 3 | HK FY2025 `reuse_only`（exact，本地元数据对账） | `source_blocked: local_metadata_gap`（`local_metadata_incomplete`，blocks_download=true） | `evidence/route3-hk-fy2025-reuse.stderr.json` |
| 4 | HK `latest_as_of` `reuse_only`（带 bounded metadata-discovery limits） | `source_blocked: company-wiki ensure blocked`（`local_metadata_incomplete`） | `evidence/route5-hk-latest-as-of-reuse.stderr.json` |
| 5 | HK `latest_as_of` `fetch_if_missing` | `source_blocked: company-wiki ensure blocked`（`local_metadata_incomplete`） | `evidence/route6-hk-latest-as-of-fetch-if-missing.stderr.json` |
| 6 | US BABA FY2026 20-F `fetch_if_missing` | `fatal: company-wiki ensure exited 1` → `provider_failed`（`dayu-us-sdk discover exited 1`，0 次 HTTP） | `evidence/route4-us-fy2026-fetch-if-missing.stderr.json` |

旁证：CWP 自己的 `ensure` 对同一 HK 文档返回 `reused_existing`（downloads=0）——缺口在 **filing-fetch 的候选 market 绑定 vs CWP 的 market 投影**。
修复项见 `alibaba-blocker.json.remediation_options_for_operator`。**没有**为 Alibaba 编造任何数字或"已交付"声明。

## 4. catalog 登记为什么 NOT_RUN

`import-research-attempt|import-research-publication` 只接受 `<owner-root>/delivery/<run_id>` 的 **B34 trusted research-admission 包**
（`run.json`、`execution/{scope,step-ledger,budget-observation,terminal,deployment-update-ff-reviewed}.json`、`execution/requests/`、
recorder 事件、native compute/validate/snapshot capture、独立审查 receipt）。本包走 `rf-job/1` façade（job store 布局），未产出该协议包；
补造会把"未发生的执行"写成发生。job 内 registry 已 validated、报告字节完整可读；`list-reports` 实测 **exit 2**
`owner_root_missing: the owner root has no managed report catalog`。

## 5. 验收证据索引（包 §5）

| §5 | 证据 |
|---|---|
| 5.1 输入 + 三步校验 | `inputs/mongodb-fy2025-input.json`；`evidence/mdb-validation-chain.json`（lint/fix/validate 全 exit 0、`valid`） |
| 5.2 真实作业到终态 | `evidence/mdb2-submit.stdout.json`、`mdb2-status.stdout.json`、`mdb2-list.stdout.json`（JobView：succeeded / cost 0.00 / known / 0 下载 / 0 付费） |
| 5.3 失败样本（自然发生） | v1 作业 `source-1` attempt failed（deployment 配置错误 `config_error`）→ resume 后成功；`evidence/mdb-submit.stdout.json`、`mdb-resume-1.stdout.json` |
| 5.4 报告可读（catalog 侧） | **NOT_RUN**（§4）；job 侧与入库副本：`evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__report.md`（sha256 `0bae0856…`） |
| 5.5 Dashboard 消费字段 | 本文 §2 + `handoff.json` + `evidence/artifacts.json`（job id / result_sha256 / input_sha256 / 两条产物路径） |
| 5.6 诚实标注 | §3/§4/§6 + `findings.md`（F-01…F-14 逐条，NOT_RUN 均带原因） |
| §8-1 独立重审 | `review-report.md`（两轮：round1 FAIL 1P1/3P2/3P3 → 全部处置；round2 见 §7） |

## 6. 预算（包 §3.1）

- `limits_ref=owner-approved-1usd`：`max_cost_usd="1.00"`、`max_new_downloads=0`、`max_attempts_per_stage=3`。
- 实际：MongoDB **0.00 USD**（`cost_state=known`；0 下载、0 付费调用；v2 job `wall_seconds_used=8.131113`）。
- Alibaba 0.00 USD（6 条路线均在采集层失败，`downloads=0`、`cost_usd=0`）。
- 合计 0.00 / 授权 2.00（两家各 1.00）。逐笔：无付费调用。

## 7. §8-1 独立重审

| 轮次 | 审查者 | 结论 | OPEN |
|---|---|---|---|
| round 1 | 独立 agent（未参与实现） | FAIL（数据真实性通过；交付面/证据标注/口径声明不足） | P1 1 / P2 3 / P3 3 |
| round 2 | 独立 agent（限时，未参与实现） | FAIL（同上快照，未含 v2 修复） | P1 2 / P2 1 / P3 4 |
| round 3（delta） | 同上 agent 复验 v2 + 交付面修复 | PASS-with-findings（唯一剩余 P2 = task_plan 哈希过期，已修） | **P1 0 / P2 0 / P3 4** |
| round 4（最终 delta） | 同上 agent 复验最终快照 `0993abb3` | **PASS** | **P1 0 / P2 0 / P3 4** |

round 1/2 的全部 P1/P2 处置见 `progress.md` 的 v2 修复表与 `findings.md` F-11…F-16；报告原文在 `review-report.md`
（未改写审查者文字；round 4 追加在该文件末尾）。**round 4 的独立复算结论**：
`git rev-parse 0993abb3` 通过；快照 blob sha256 `4798e682…`（398,344 B）与记录一致；输入 blob `d82f9b45…`（146,551 B）
且 `--validate-only` 退出 0 `valid`；`d347c4ab..HEAD` 118 文件 118/118 在 `.planning/rf-input-prep-01/`，工作树干净。

## 8. §8-3 并线状态（不能安全并线）

- `main`（`90c562ac`）无 `scripts/rf_job_cli.py` / `report_catalog_identity_cli.py`（`git ls-tree main` 实测为空），包 §4 契约在 main 上不可执行；
- 并线 = 把 B37 基线整体并入 main 的大规模整合，façade handoff §6 已判定"不满足安全并线条件"。
- **并线交接任务**：`codex/rf-job-facade-01` + `codex/rf-input-prep-01` 整体并入 `main`；条件：main 的 D 线收口（D4-06 ROOT 组合验收）完成且 `scripts/` 回归通过；触发人：RF owner。本包不推远端。

## 9. Dashboard 接入指引

1. 绑定 `release_tag_or_commit_for_dashboard`（40 位 commit）。
2. 读入库产物：`evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__result.json`（sha256 `c0dce8c3…`）与 `…__report.md`（sha256 `0bae0856…`）；
   `result_sha256=04768c27…`，`input_sha256=6169ea8a…`。
3. `rf-job/1` 路由（固定 argv、业务 JSON 无路径）：`python scripts/rf_job_cli.py --owner-root <dir> --deployment-config <path> submit|get-status|act|list-jobs`。
4. catalog 消费：本包未登记 managed catalog（§4）。若 Dashboard 的 MODULE-m5-RF-REPORT-ACCEPTANCE 需要 `list-reports`，
   需另立 owner 包补齐 B34 research-admission 协议。
5. Alibaba 待 CWP 修 market 投影或恢复 US adapter 后，用同一流程重跑（输入编制脚本 `build_mdb_input.py` 可直接改造成 Alibaba 版）。

## 10. 包要求逐条对照（§1-§8）· 2026-11-08 自查

完整机读清单在 `handoff.json.package_compliance`（27 条）。汇总：**PASS 20 / PARTIAL 5 / NOT_RUN 2**。

未达成的 7 条（全部为 Alibaba 采集阻塞与 catalog 协议缺口的直接后果，无一隐藏）：

| 条款 | 状态 | 缺口 | 阻塞原因 |
|---|---|---|---|
| §1 两份完整输入 | PARTIAL | Alibaba 无输入 | 采集层：6 条路线具名失败（见 §3） |
| §1 两份作业到终态 | PARTIAL | 只有 MongoDB | 同上（无输入即不能提交） |
| §5.2 两份真实作业 + JobView | PARTIAL | 只有 1 份 JobView | 同上 |
| §5.5 Dashboard 消费字段 | PARTIAL | `catalog_report_id=null` | 无 catalog 登记 |
| §3.4 不冒充已完成 | PARTIAL（如实标注侧已做） | 交付不完整，已声明 G-m5-EXT-01 未解除 | 同上 |
| §4 catalog 显式登记 | NOT_RUN | 无 `import-research-attempt/publication` | 需 B34 trusted research-admission 包（recorder/step-ledger/terminal/review receipt），本包未产出 |
| §5.4 list-reports 可读 + 报告ID | NOT_RUN | `list-reports` exit 2 `owner_root_missing` | 同上 |

**偏离包字面要求但已披露的 5 项**（`handoff.json.deviations`，其中仅 D1 需操作者裁定）：

| ID | 包要求 | 实际 | 理由 |
|---|---|---|---|
| D1 | §6 基线=已发布主线 HEAD | 基线=facade 线 `d347c4ab` | `main` 无 `rf_job_cli.py`，§4 契约在 main 不可执行 |
| D2 | §2 用模板生成 | 用 `build_mdb_input.py` 构建，再与模板逐字段对比 | 模板只有 FIXME 占位；对比结果：模板字段**零缺失**（仅模板自带 `_comment` 不在交付件） |
| D3 | §2.1 `browser_open` 类抓取 | `capture_method=local_document`（company-wiki verified read） | 技能规定路线；snapshot/receipt 真实且可重算 |
| D4 | §3.1 `max_bytes` 保守值 | `reuse_only` 请求禁止 `acquisition_limits`；仅设超时与 0 新下载 | filing-fetch 契约；Alibaba 下载向探针带 8 MB/120s/0.00 USD |
| D5 | §7 `head_commit`=最终 commit | pin 自包含内容 commit `0993abb3…`；handoff 记录在后续 commit | commit 无法包含自身 SHA |

**结论**：MongoDB 侧按包完成（输入、校验、作业、产物、证据、独立重审）；Alibaba 与 catalog 两项未完成且不可在本包内完成。**G-m5-EXT-01 不解除。**

## 11. 问题详述（背景 / 意图 / 遇到 / 影响 / 建议）

本节把本包实际遇到的问题逐条讲清楚，供 Dashboard 与各 owner 复现与排期。机读版在 `handoff.json.issues`；
参数级细节见 `findings.md` F-01…F-16。

### 11.1 Alibaba：唯一在册年报缺 `market` 投影，filing-fetch 拒绝复用（阻断交付）

- **背景**：包 §0 记录 Dashboard 侧实体 `ENT_e4d964f0…` / 挂牌 `LST_591474dd…`，来源记为阿里 20-F；但 company-wiki 里
  `阿里巴巴－Ｗ` 只有**一份**在册年报原件（HKEX FY2026，`document sha256=e39fbf9c…`，4,172,424 B，2026-06-18 披露），
  其 `source_query` 投影为 `market=null`（同候选 `capture_ready=true`、`published_date=2026-06-18`、`security_id=09988`）。
- **当时打算做什么**：按包 §2 用 `source_preparation.py` → filing-fetch 取 capture-ready handle，再建 schema 3.7 输入 → 提交作业。
- **遇到什么**：filing-fetch 对候选做 `candidate.market != company_identity.market` 硬绑定，六条路线全部被拒：
  ① exact/reuse_only → `company-wiki source query market mismatch`；② exact/fetch_if_missing → `operation market mismatch`；
  ③ FY2025/reuse_only → `source_blocked: local_metadata_gap`（`blocks_download=true`）；④ latest_as_of/reuse_only →
  `ensure blocked: local_metadata_incomplete`；⑤ latest_as_of/fetch_if_missing → 同上；⑥ US 20-F/fetch_if_missing →
  `ensure exited 1`（`provider_failed`，`dayu-us-sdk discover exited 1`，0 次 HTTP）。六条全部 `downloads=0`。
- **影响**：Alibaba 无法建输入、无法提交作业；不是预算、网络或身份解析问题（身份解析成功，CWP 自己也认为该原件 `reused_existing`）。
- **建议**：
  1. **CWP owner**：修 `document e39fbf9c…` 的 `market` 投影（其 provider sidecar 里 `market:"HK"` 明确存在，是投影丢失）——这是最小修复；
  2. **FF owner**：允许候选 `market=null` 时回落到已验证身份的 market，并在回执里标注 `market_source=identity_fallback`，避免"数据不全即拒"；
  3. **环境**：恢复 US 采集适配器（`dayu-us-sdk`），使 20-F 路线可用；
  4. 验收：六条任一路线返回 `status=found` + `capture_ready=true` + `market` 非 null。
- **归属**：CWP owner / FF owner / 环境；解除后我可用 `build_mdb_input.py` 的 Alibaba 变体在半天内出输入→作业→报告。

### 11.2 MongoDB：最新审计年报在库但非 capture-ready，基准年被迫回退

- **背景**：CWP 有 `companies/MongoDB, Inc/raw/…10-K 2026-01-31.htm`（2,218,293 B），sidecar 里有 filing_date/market，
  但 `source_query` 候选 `capture_ready=false`、`published_date=null`、`https_url=null`。
- **当时打算做什么**：用 FY2026（ended 2026-01-31）作基准年，得到最新审计数。
- **遇到什么**：ff 报 `handle published_date must use YYYY-MM-DD format`（实为 null 不是格式错）；FY2025 10-K（dayu_portfolio 根，
  `b3788068…`）则完全可用。
- **影响**：基准年退回 FY2025（2,006.443 US$m），比信息日（2026-11-08）落后一年；已在输入的 `management_communication_coverage.latest_annual_filing`
  与报告 limitations 中明示。
- **建议**：CWP 用 `source-facts` 一类受管入口补齐该文档的公开日/market 投影；FF 把"字段缺失"与"格式非法"分成两个具名错误码。
- **归属**：CWP owner（数据）/ FF owner（错误语义）。

### 11.3 catalog 登记不在 façade 内，且需要另一套记录协议（§5.4 未达成）

- **背景**：包 §4 要求作业成功后用 `report_catalog_identity_cli.py import-research-attempt` 登记，使 Dashboard 能 `list-reports`。
- **当时打算做什么**：登记 managed catalog，附报告 ID 与 `result_sha256`。
- **遇到什么**：该命令只接受 `<owner-root>/delivery/<run_id>` 的 **B34 trusted research-admission 包**——`run.json`、
  `execution/{scope,step-ledger,budget-observation,terminal,deployment-update-ff-reviewed}.json`、`execution/requests/`、
  recorder 事件流、native compute/validate/snapshot captures、独立 review receipt；且要求 operator 提供实际 recorder 的 SHA。
  rf-job/1 façade 产出的是 job store（`job.json` + `stages/` + `registry/publications.jsonl`），两者不是同一协议。
  `list-reports` 实测 exit 2 `owner_root_missing: the owner root has no managed report catalog`。
- **影响**：§5.4 未达成；报告只能按 commit + 文件消费；Dashboard 的 null 纪律不受影响（未登记就不显示）。
- **建议**：
  1. **owner/D00**：给 façade 作业定义 admission adapter——把 job.json/stage attempts/artifacts 映射成 admission 包，
     并在记录里显式标注"执行者是 façade"（可审计、不冒充 recorder 事件）；
  2. 或新增轻量登记接口：接受 `result_sha256 + 独立审查 receipt + 输入哈希`，由 owner 背书后入 catalog；
  3. 本包已提供的替代消费面：入库产物副本 + `manifest.json`（逐文件 sha256）+ `key_hashes`。
- **归属**：owner/D00 交付协议；**不要**用 harness 侧补造记录来绕过（见 11.10）。

### 11.4 `deployment.company_wiki_config` 语义与直觉不符（首次作业失败的根因）

- **背景**：`config/rf_job_deployment.example.json` 的键名是 `company_wiki_config`。
- **当时打算做什么**：指向仓内 `config/company_wiki.json`（company-wiki 的 schema 2.0 配置）。
- **遇到什么**：façade 把该路径当 filing-fetch 的 `--config` 传下去，而 filing-fetch 只接受自己的
  `{schema_version:"1.0", company_wiki_root}` 形态 → 0.88 s 内 `config_error`，source attempt 1 failed（该失败已作为 §5.3 的真实样本保留）。
- **影响**：首次提交失败；用 `act --resume` 修正后成功（也顺带验证了恢复语义）。
- **建议**：`Deployment.load` 对该文件做 schema 校验，或把键名改为 `filing_fetch_config`；example 里加一行说明。
- **归属**：RF owner（工具改进）。

### 11.5 job store 落在根 `.gitignore` 的 `artifacts/` 下（审查方 P1）

- **背景**：owner-root 必须在仓内（本包用 `.planning/rf-input-prep-01/job-root`），façade 固定写到 `<root>/artifacts/rf_jobs/`。
- **遇到什么**：根 `.gitignore` 忽略 `artifacts/` → job 产物不进 commit，按 commit 消费会落空；独立审查判 P1。
- **影响**：交付链路断在"产物不在 commit 内"。
- **建议**：façade 在作业完成时导出 bundle（或默认把 job store 放非忽略路径），并在 JobView 里给出可入库的产物清单。
- **已做缓解**：`copy_job_artifacts.py` 按字节复制到 `evidence/job-<job_id>/` + `manifest.json`；`evidence/.gitattributes` 用 `* -text` 保证 checkout 后哈希不变。
- **归属**：RF owner。

### 11.6 publication 阶段成功时静默，产物是 0 字节文件（P3）

- **遇到什么**：`stages/publication/audit.json` = 0 字节（`e3b0c442…` = 空串哈希），因为 `publication_registry.py audit` 成功时不输出。
- **影响**：容易被误读为失败或空实现。
- **建议**：成功时打印一行 JSON（`result_sha256` / registry line / `validation_status` / registry 路径）。
- **归属**：RF owner。

### 11.7 输入 capture 与 job source 阶段 capture 是两次真实读取（易被误判为伪造）

- **背景**：输入必须先存在才能提交作业；façade 的 source 阶段是独立子进程，又做了一次 verified read。
- **遇到什么**：同一 `source_id`/`snapshot_sha256`（`b3788068…`），但 `receipt_sha256` 不同（`525ce1ed…` vs `d528bd98…`）。
- **影响**：审计时若不知道这是两次读取，会怀疑"receipt 对不上"。
- **建议**：façade 支持在 `forecast_input` 里声明"期望 source 阶段复现的 snapshot"，并在 source 阶段做一致性校验与记录；
  或把 source 阶段 envelope 作为输入的一部分冻结。
- **已做**：F-10 记录两次读取的时间与哈希。
- **归属**：RF owner。

### 11.8 两个"结果哈希"不是同一个量（易误用）

- **遇到什么**：引擎 `result_sha256=04768c27…` 是对**去掉该字段**的 payload 求 canonical 哈希；`revenue_backtest.py create`
  的快照里 `forecast_result_sha256=4587acc8…` 是对**完整冻结 dict** 求哈希，两者对同一预测给出不同值。
- **影响**：若拿一个去核对另一个会误判"不一致"。
- **建议**：schema 明确命名（`engine_result_sha256` vs `frozen_payload_sha256`），或在快照里同时记录引擎哈希。
- **已做**：F-16 + `handoff.json.key_hashes` 里逐条标注。

### 11.9 表格式 excerpt 的"逐字"陷阱（审查方 P3）

- **背景**：10-K 是 HTML，表格转文本后一行会被拆成多行单元格。
- **当时打算做什么**：手写"阅读顺序"excerpt 以覆盖三段收入。
- **遇到什么**：手写串不是原文子串（12/14 逐字）；审查方指出后，改为从已核对文本**切片**并加 fail-fast 断言。
- **影响**：v1 输入的证据保真被扣分；v2 修复（14/14 逐字）并重跑作业。
- **建议**：把"excerpt 必须来自已核对文本的切片"写进流程（`lint_input.py` 可加 `--require-excerpt-in-text <text>` 选项），
  避免作者凭记忆或手工排版。
- **归属**：RF owner（工具改进）。

### 11.10 越界采集的诱惑（已否决，留作警戒）

- **背景**：Alibaba 卡死时，最省事的解法是自己 HTTPS 下载 20-F，再用 company-wiki `official import` 登记；技术上可行。
- **当时做了什么**：只查询了 SEC `submissions` 元数据索引（未取正文），随后按操作者指示**停止并放弃**该路线；未写任何 catalog。
- **为什么不采用**：本项目是多模块系统，采集归属 `filing-fetch` → `company-wiki`；harness 自办采集即使能过校验，也绕过了模块边界与审计链。
- **建议**：在包的 §3 红线里加"禁止路线"清单（harness 自下载、手工 catalog 写入、改其他 owner 仓），并规定三步处置：
  **换模块支持的参数再试 → 记录机器原因 → 升级给 owner**。
- **归属**：包作者（下次开工单时）。

### 11.11 基线偏离：包说"已发布主线 HEAD"，但 main 不含 façade

- **背景**：包 §6 要求基线=已发布主线 HEAD；实测 `main`（`90c562ac`）没有 `scripts/rf_job_cli.py` / `report_catalog_identity_cli.py`。
- **采用**：façade 线 `codex/rf-job-facade-01` tip `d347c4ab`（含交付 commit `e4b38459`，实测为其祖先）。
- **影响**：与包字面要求不一致，已登记为偏离 D1，**需操作者裁定**。
- **建议**：包在写"基线=主线"前先验证该线是否含所需入口；或直接写"以交付 façade commit 所在线为基线"。
- **归属**：包作者/操作者。

### 11.12 包 §0 的既有交付陈述与磁盘不符（信息项，本包不处理）

- **观察**：§0 称药明康德已有"3 runs / 4 validated reports"；磁盘上 B34 只有 v2（6 行 registry）、B37 有 v1–v3（9 行 registry），
  且这两个 `delivery/` 目录是**未跟踪文件**，不在任何 commit 的树里（`git log --all -- delivery/…` 为空）。
- **影响**：若 Dashboard 按 §0 的陈述去找 WuXi 报告，可能在 commit 上找不到。
- **建议**：Dashboard 以 managed catalog 为准核对这 4 份报告；WuXi 交付目录应入库（另立 owner 包），否则其可消费性无法按 commit 复现。
- **归属**：Dashboard/D00。本包按操作者指示**不处理** WuXi。
