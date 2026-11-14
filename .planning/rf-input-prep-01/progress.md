# progress · OWNERPKG-RF-INPUT-PREP-01

节点定义见 `task_plan.md`。时间均为 UTC（记录来自本会话实测）。

## 2026-11-08 · N1-N2 开包

- 读 `INPUT-PREPARATION-PACKAGE.md`（119 行）；加载 `revenue-forecast` + `filing-fetch` 技能。
- 基线盘点：`main`=90c562ac（无 façade），`codex/rf-job-facade-01`=d347c4ab（含 façade e4b38459）。
- 新建分支与独立 worktree：`git worktree add -b codex/rf-input-prep-01 <wt> codex/rf-job-facade-01` → HEAD d347c4ab，50862 文件检出。

## 2026-11-08 · N3 源采集判定（决定性节点）

- MongoDB：
  - `reuse_only` FY2026 10-K（`companies/MongoDB, Inc/...10-K 2026-01-31.htm`，2,218,293 B）→ `upstream_error: handle published_date must use YYYY-MM-DD format`
    （CWP 候选 `capture_ready=false`、`published_date=null`）。
  - `reuse_only` FY2025 10-K（dayu_portfolio 根，2,108,287 B，sha256 `b3788068…`）→ **成功**：`source-preparation-result/1`，
    `reused_existing`，`downloads=0`，`published_date=2025-03-21`，verified read `2026-11-08T08:29:31Z`。
  - 结论：以包 §2 指定的 FY2025 为基准年（FY2026 年报原件存在但非 capture-ready，登记为研究限制）。
- Alibaba：4 条路线全部具名失败（详见 `alibaba-blocker.json`）：
  1. HK 09988 FY2026 `reuse_only` → `company-wiki source query market mismatch`（候选 market 投影为 null，ff 与身份 market 绑定不一致）
  2. HK FY2026 `fetch_if_missing` → `company-wiki operation market mismatch`
  3. HK FY2025 `reuse_only` → `source_blocked: local_metadata_gap`（CWP 诊断 `local_metadata_incomplete`，blocks_download=true）
  4. US BABA FY2026 20-F `fetch_if_missing` → `fatal: company-wiki ensure exited 1`（CWP 直跑报 `adapter dayu-us-sdk discover exited 1`，http_exchanges=0）
  - 旁证：CWP 自己的 `ensure` 对同一 HK 文档返回 `reused_existing`（downloads=0）——缺口在 ff 的候选 market 绑定 vs CWP 投影，不在账号/网络。

## 2026-11-08 · N4-N5 MongoDB 输入编制

- 原文读取（本地转文本，仅研究用）：FY2025 10-K → 2,389 行 / 470,213 字符。
- 取数（USD 千元 → 百万，Note 9 分拆表与合并利润表逐项对齐）：
  - 总收入 FY2025 2,006,443 / FY2024 1,683,011 / FY2023 1,284,040
  - Atlas-related 1,405,184 / 1,105,351 / 808,263；Other subscription 538,680 / 521,975 / 426,859；Services 62,579 / 55,685 / 48,918
  - 三段合计=总收入（精确相等，无 base adjustment）
- 情景：3 段 × 3 年 × low/base/high 共 27 个 `analyst_assumption` 增长率（明确标注"幅度非披露，属分析师判断"）。
- 增长驱动树：3 根（Atlas 消费扩张 / 企业客户群扩张 / 合约背压+递延转换），权重按段各 1.0，证据节点 7 个全部 claim 背书。
- 管理沟通覆盖：6 类全部 `incomplete`（每类写明读到什么、没读到什么；未虚构 `not_available` 搜索事件）。
- 生成脚本 `build_mdb_input.py`（可重放）；输出 1 source / 31 parameters / 73 claims / 3 segments。

## 2026-11-08 · N6 校验链

| 步骤 | 命令 | 结果 |
|---|---|---|
| lint | `python scripts/lint_input.py <input>` | exit 0，`ok: no findings` |
| fix_hashes | `python scripts/fix_hashes.py <input>` | exit 0，`ok: no hash drift` |
| validate-only | `python scripts/revenue_forecast.py <input> --validate-only` | exit 0，`valid` |

（首次 validate 报 2 个缺陷并修复：excerpt 535 字符超 500 上限 → 拆为 `policy_db`/`policy_license`；驱动树证据节点引用了
`recognition_policy` claim → 改为 7 个 `growth_driver` 证据 claim。修复后一次通过。）

## 2026-11-08 · N7 job 提交与终态

- 首次 submit（deployment `company_wiki_config` 指向 RF 仓 `config/company_wiki.json`）→ source 阶段 exit 3
  （filing-fetch `config_error`：ff 只接受自己的 `{schema_version:1.0, company_wiki_root}` 配置）。
- 修正 deployment 指向 `filing-fetch/config/company_wiki.json`，用 `act --action resume` 重跑未完成阶段：
  - source attempt 1 failed（0.88s）→ attempt 2 completed（7.39s，`reused_existing`，downloads=0，model_calls=0）
  - compute completed（0.49s，纯计算器）→ publication completed（0.18s，只读审计）
  - JobView：`status=succeeded`，`status_known=true`，`allowed_actions=[]`，`cost={USD,0.00}`，`cost_state=known`，
    `budget={new_downloads:0, paid_model_calls:0, wall_seconds_used:8.061832}`
- 计算产物：`stages/compute/result.json`（324,811 B，file sha256 `2fa1170d…`，`result_sha256=e5c6ceb3…`）、`report.md`（53,179 B）。
  与本地独立重算逐字段一致（`consolidated_forecast` 相等）。
- 基线/情景：base 2,006.443 → 2,316.536 / 2,650.175 / 2,993.792（CAGR 14.27%）；
  low 2,180.071/2,315.671/2,424.255（6.51%）；high 2,443.711/2,929.059/3,448.819（19.79%）。
- 置信度 49.0（rating low），limitations 如实含："direct fallback model"、"3 个 data gap"、"单源未三角化"、"无历史回测"。

## 2026-11-08 · N8-N10

- N8：job registry `publications.jsonl` 已有 1 行（`validation_status=validated`，`result_sha256=e5c6ceb3…`，`prev_line_sha256=null`）。
- N9 catalog 登记：`report_catalog_cli.py --owner-root <job-root> list-reports` → `owner_root_missing: the owner root has no managed report catalog`。
  登记需 `import-research-attempt|publication` 的 trusted 包（`execution/scope.json`/`step-ledger.json`/`budget-observation.json`/`terminal.json`/
  `deployment-update-ff-reviewed.json`/`requests/` + recorder + review receipt）。本包未产出该协议包 → 记 NOT_RUN（F-03），不做伪造。
- N10 Alibaba：NOT_RUN（采集层，4 路线具名失败）。

## 待办（移交）

- Dashboard 侧 MODULE-m5-RF-REPORT-ACCEPTANCE 消费 job 产物（固定 commit + `result.json` + `result_sha256`）。
- Alibaba：CWP 修复 market 投影或恢复 US adapter 后，按本包同一流程重跑（输入编制脚本可直接复用）。

## 2026-11-08T08:50Z · N12 独立重审首轮 → v2 修复

独立审查（`review-report.md`，未参与实现）结论 **FAIL**：OPEN P1=1 / P2=3 / P3=3；同时明确未发现伪造数字、伪造 receipt 或哈希不符，
MongoDB 侧 A–G 七类核验（校验链、job 终态、result/input 哈希、写域、10-K 数字、excerpt 保真、capture 重算）全部通过。逐条处置：

| 审查项 | 处置 |
|---|---|
| P1 handoff 占位符/审查块预填 0/0 | 本文件与 `handoff.json`/`handoff.md` 已更新为真实 commit 与真实审查计数；最终 commit 号在交付时回填 |
| P2 job-root 产物被 `.gitignore` 的 `artifacts/` 忽略，不在 commit 内 | 新增 `copy_job_artifacts.py`：把 job.json / result.json / report.md / registry 行 / 阶段日志按字节复制到 `evidence/job-<job_id>/` 并出 `manifest.json`（含逐个 sha256）；`collect_artifacts.py` 同时记录 job-store 与 tracked copy 两条路径 |
| P2 Alibaba 路线 1/2 证据文件错标（stderr 被覆盖、envelope 0 字节） | 新增 `capture_alibaba_blockers.py`，以每次独立文件重放路线 1/2/3：`evidence/route{1,2,3}-*.{stdout.json,stderr.json}` + `evidence/alibaba-routes.json`；路线 1 = `source query market mismatch`（calls 2、downloads 0），路线 2 = `operation market mismatch`，路线 3 = `source_blocked: local_metadata_gap`。`alibaba-blocker.json` 已按实测重写 |
| P2 §2.3 口径声明未落地（`revenue_basis` 未应用） | 应用 v2 修复：`reported_total` 与 3 条历史观测均带 `rf-revenue-basis/1`（operations=total、statement_status=as_reported、period_kind=fiscal_year）；报告“口径”列由“未声明”变为“总额/原表” |
| P3 两个表格 excerpt 非逐字 | v2 的同一次修复把两张表 excerpt 改为 `mdb-fy2025-10k.txt` 的**精确切片**（构建脚本 `_slice()` + `_assert_verbatim()` fail-fast），14/14 逐字；`evidence/excerpt-fidelity.json` 由 `verify_excerpt_fidelity.py` 重算 |
| P3 handoff/PWF 路径错误、`list-reports` exit 记错、task_plan 输入 sha 过期 | 全部修正：`list-reports` 实测 **exit 2**（`owner_root_missing`）；task_plan 输入 sha 更新为 v2 `6687a3b5…`；handoff 证据路径改为真实文件名 |

v2 结果（重新提交的新作业，未覆盖旧作业）：

- 输入：`inputs/mongodb-fy2025-input.json`，file sha256 `d82f9b45cefddfba5d52e2abf1e35dba553a1722b1d181818dda78ba0236a993`（schema 3.7，forecast_version `…-v2`）
- 作业：`rfjob-20261108-eb9f2a3ed336`，**首次 submit 即 succeeded**；source/compute/publication 各 1 次 attempt 全 exit 0；
  `downloads=0`、`paid_model_calls=0`、`cost={USD,0.00}`、`cost_state=known`、`wall_seconds_used=8.131113`
- 引擎：`result_sha256=04768c2742d663e3e7ac748c9fde8c7648cc1cd0e424e4d931e150379c038816`，
  `input_sha256=6169ea8aca81638d83026153474d584ca19be38c166bb71ab0ae4e76924cde59`（v2 canonical），base 2,006.443，情景数值与 v1 一致（口径字段不影响算术）
- 证据：`evidence/job-rfjob-20261108-eb9f2a3ed336/`（10 个 tracked copy + manifest，result.json 复制件 sha256 `c0dce8c3…`）
- v1 作业 `rfjob-20261108-ea663b8bd33e` 保留在 job store 作为历史（其输入已被 v2 取代，不再作为交付候选）。

## 2026-11-08T09:2xZ · 只走模块接口的收尾（操作者指令）

操作者要求：项目由多模块组成，一切动作必须通过模块间的公开接口，不得由 harness 自行承担底层任务。据此：

1. **撤回越界路线**：曾评估"自己 HTTPS 下载 SEC 20-F + company-wiki `official import`"，只查过 SEC 元数据索引（未下载正文），
   已放弃并登记（findings F-15）。Alibaba 采集只走 `source_preparation.py → filing_fetch_client → filing-fetch → company-wiki`。
2. **Alibaba 六路线复验**（全部经上述模块链，零下载、零付费）：exact/reuse_only、exact/fetch_if_missing、FY2025/reuse_only、
   latest_as_of/reuse_only（带 bounded metadata-discovery limits）、latest_as_of/fetch_if_missing、US 20-F/fetch_if_missing。
   结果：`source query market mismatch`、`operation market mismatch`、`local_metadata_gap`、`ensure blocked: local_metadata_incomplete` ×2、
   `ensure exited 1`（`provider_failed`）。证据：`evidence/route{1..6}-*.{stdout.json,stderr.json}` + `evidence/alibaba-routes.json`。
3. **补两个模块接口产物**：
   - `scripts/revenue_backtest.py create` → `evidence/mongodb-fy2025-snapshot.json`（冻结快照，`input_sha256=6169ea8a…`，
     冻结 payload 与交付 `result.json` **整字典相等**；`forecast_result_sha256=4587acc8…`）
   - `scripts/research_support_diagnostics.py` → `evidence/mongodb-support-diagnostics.json`（分段×年×情景证据支持诊断）
   两者已写入 `handoff.json.inputs[0].derived_artifacts`，evidence 清单 16 行。
4. **哈希口径澄清**（findings F-16）：`result_sha256=04768c27…` = 引擎对**去掉该字段后的 payload** 做的 canonical 哈希；
   快照 `forecast_result_sha256=4587acc8…` = 对**完整冻结 dict** 的 canonical 哈希。两哈希标识同一预测的不同封装，不能互换核对。
5. **catalog 登记仍 NOT_RUN**：`import-research-attempt|publication` 需要 owner 侧 B34 research-admission 记录包
   （recorder/run/step-ledger/terminal/review receipt），不在本仓模块接口内；不越界补造。
