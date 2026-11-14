# findings · OWNERPKG-RF-INPUT-PREP-01

严重度：P1=阻断交付；P2=显著缺陷；P3=已披露限制。

## F-01（P2，已绕过）filing-fetch 候选 `market` 投影为 null 时整条复用链失败

- 现象：company-wiki `source_query_cli` 对 HKEX FY2026 年报返回完整候选（`capture_ready=true`、`published_date=2026-06-18`、
  sha256 `e39fbf9c…`），但候选 `market=null`；filing-fetch `validate_source_candidate` 用
  `handle[market] != company_identity[market]` 判定 → `company-wiki source query market mismatch`。
- 影响：Alibaba 唯一在册年报原件（FY2026 HKEX）无法被 ff 复用；`reuse_only`、`fetch_if_missing`、`local_prepare` 三条路径均失败
  （`source query`/`operation` market mismatch、`local_metadata_gap`）。
- 旁证：CWP 自己的 `ensure` 对同一文档返回 `reused_existing`（downloads=0），说明 CWP 认为可复用，拒绝发生在 ff 的绑定检查。
- 归类：**采集层跨 owner 缺口**（CWP 元数据投影 / filing-fetch 绑定），不是 RF 引擎缺陷；按包 §3.3 只登记不改。
- 交接对象：CWP owner（修 market 投影）+ FF owner（是否允许 null market 绑定身份 market）；Alibaba 因此在包内 NOT_RUN。

## F-02（P2，已绕过）MongoDB FY2026 10-K 原件非 capture-ready

- 现象：`companies/MongoDB, Inc/raw/.../10-K 2026-01-31.htm` 已在 CWP，但 `source_query` 候选 `capture_ready=false`、
  `published_date=null`、`https_url=null`；ff 报 `handle published_date must use YYYY-MM-DD format`。
- 影响：本可作 FY2026 基准的最新审计年报不可用，只能用包 §2 指定的 FY2025 10-K（dayu_portfolio 根，`b3788068…`，capture_ready=true）。
- 后果（已在输入/报告中如实披露）：基准年落后一年；FY2026 审计结果未纳入；`latest_annual_filing` 覆盖状态为 `incomplete`。
- 归类：采集层（CWP source-facts/元数据）缺口，登记不改。

## F-03（P1，未完成，NOT_RUN）catalog 登记需要 B34 trusted research-admission 包

- 现象：`report_catalog_identity_cli.py import-research-attempt|publication` 只读 `<owner-root>/delivery/<run_id>` 固定包，
  要求 `run.json` / `execution/scope.json` / `step-ledger.json` / `budget-observation.json` / `terminal.json` /
  `deployment-update-ff-reviewed.json` / `requests/` + recorder 事件 + 独立审查 receipt + native compute/validate/snapshot capture。
- 本包走的是 rf-job/1 façade（job store 布局），没有产出该协议包；补造会把"未发生的执行"写成发生 → 失真，故不做。
- 现状：job 内 `registry/publications.jsonl` 已有 validated 行（`result_sha256=e5c6ceb3…`），报告字节完整可读；
  `report_catalog_cli.py list-reports` 因无 managed catalog 返回 `owner_root_missing`（如实证据）。
- 交接：Dashboard MODULE-m5-RF-REPORT-ACCEPTANCE 侧按固定 commit 消费 job 产物，或另立 owner 包补 research-admission 协议。

## F-04（P3）管理沟通覆盖全部 `incomplete`

- 只打开 FY2025 10-K（收入附注/分部/MD&A/风险因素）。未取到业绩发布、电话会、投资者演示、后续公告原件。
- 输入内 6 类记录逐条写明"读到什么/没读到什么"；未使用 `not_available`（因为材料客观可得，只是本包未采集），
  未虚构 search_event。引擎把它记录为 coverage gaps（报告中可见），不阻断正式校验。

## F-05（P3）三段均用 `direct_growth` 直接回退模型

- 披露口径只有 "Atlas-related / Other subscription / Services" 三段收入，没有 usage/seat/ARR 分母可校准原生经营模型，
  故按技能要求以 `direct_growth` 作为透明回退，并在 rationale 明示；置信度 components 中
  `revenue_weighted_explicit_models=0.0`、总分 49.0（low）如实反映。

## F-06（P3）增长幅度无独立校准

- low/base/high 增长率是分析师判断（幅度非披露）：base 取 FY2025 实际增速的温和减速路径，low 叠加披露的
  "existing Atlas applications 增长放缓" 宏观逆风，high 叠加 RPO/客户群动量。已在参数 `rationale` 与报告 limitations 中披露。
- 未做主题弹性/反事实、未做历史回测（无冻结快照历史），因此 `historical_accuracy=0.0` 记录为 "No immutable historical backtest record"。

## F-07（P2，环境）US 采集适配器不可用

- `company-wiki ensure --entity "Alibaba Group Holding Ltd" --market US ...` → `adapter dayu-us-sdk discover exited 1`，
  `http_exchanges=0`、`cost_usd=0`。任何美股原始件下载当前都不可行（影响 Alibaba 20-F 备选路线）。
- 归类：环境/配置缺口，登记交操作者。

## F-08（P3）deployment `company_wiki_config` 语义易错

- façade 的 `stages.source.company_wiki_config` 实际传给 filing-fetch 的 `--config`，必须是 **filing-fetch 自己的**
  `{schema_version:"1.0", company_wiki_root:...}` 配置；指向 RF 仓 `config/company_wiki.json`（schema 2.0 + adapters）
  会在 0.88s 内 `config_error`（本包首次 submit 即踩到，已用 resume 修复并留痕）。
- 建议：deployment example 里加一句注释或在 Deployment.load 校验该配置的 schema_version。

## F-09（P3）`publication` 阶段 audit 产物为空文件

- `stages/publication/audit.json` = 0 字节（`e3b0c442…` = 空串 sha256），因为 `publication_registry.py audit` 成功时静默（exit 0）。
- 建议：审计成功时输出一行 JSON，避免"空产物"被误读为失败。

## F-10（P3，已披露）输入内的 capture 与 job source 阶段 capture 是两次真实读取

- 输入里的 source 记录来自提交前的 verified read（v2：08:5x），job 的 source 阶段在作业运行时又做了一次 verified read：
  两者 `source_id` 与 `snapshot_sha256`（`b3788068…`）相同，`receipt_sha256` 不同（各自真实 receipt）。
- 原因：façade 的 source 阶段读取的是 job 自己的 request 结果，无法自引用同一个 job 内尚未发生的读取（先有输入、后有 job）。
  两次读取都是真实的、同字节的；不构成伪造。
- 证据：`evidence/artifacts.json`、`evidence/job-rfjob-20261108-eb9f2a3ed336/stages__source__result-envelope.json`。

## F-11（P3，v2 已修复）两个表格式 excerpt 原为"阅读顺序渲染"，非字节子串

- v1：14 个去重 excerpt 中 12 个是 `mdb-fy2025-10k.txt` 的逐字子串；`claim_reported_total_2025` 与 `claim_atlas_base`
  是表格行的阅读顺序渲染（行标签 + 单元格值，` | ` 分隔；转换器把每个单元格输出到单独一行）。
- v2 修复：构建脚本改为 `_slice()` 从已核对文本精确切片 + `_assert_verbatim()` fail-fast，14/14 逐字；
  核验见 `evidence/excerpt-fidelity.json`（`verbatim_count=14`、`reformatted_table_blocks=[]`）。v2 作业用修正后的输入重跑。

## F-12（P2，v2 已修复）job store 位于根 `.gitignore` 的 `artifacts/` 下，产物不在 commit 内

- 现象：`.planning/rf-input-prep-01/job-root/artifacts/...` 被根 `.gitignore` 忽略，`git cat-file` 取不到 job 的 result.json/report.md；
  交接若只写 job-store 路径，Dashboard 按 commit 消费会落空。
- 修复：`copy_job_artifacts.py` 把 job.json / result.json / report.md / registry/publications.jsonl / 阶段日志按字节复制到
  `evidence/job-<job_id>/` 并生成 `manifest.json`（逐文件 sha256）；`evidence/artifacts.json` 同时记录 job-store 与 tracked copy 两条路径及各自哈希。
- job store 仍保留为 `get-status` 复放源（本地有效，不入库）。

## F-13（P3，v2 已修复）§2.3 口径声明未落地

- v1 输入未声明 `revenue_basis`，报告显示"口径 未声明 / basis not declared"。
- v2：`reported_total` 与 3 条历史观测均带 `rf-revenue-basis/1`（`operations=total`、`statement_status=as_reported`、`period_kind=fiscal_year`）；
  报告"口径"列显示"总额/原表"。
- 剩余限制（如实）：未声明 `business_boundary_id`/`comparison_group_id`/`basis_claim_ids`，引擎因此仍把"同比口径可比性"标为
  "未核实口径"——这是**未做可比性验证**，不是未声明口径；不硬凑可比声明。

## F-14（P2，v2 已修复）Alibaba 路线证据错标 / 空文件

- v1 的 `requests/alibaba-stderr.txt` 被路线 3 的运行覆盖（内容是 `local_metadata_gap`，而 blocker 把它标为路线 1），
  `alibaba-envelope.json` 为 0 字节——独立审查判定为"证据层面过度陈述"。
- v2：`capture_alibaba_blockers.py` 以每路线独立文件重放，得到
  `evidence/route1-hk-fy2026-reuse.{stdout.json,stderr.json}`、`route2-…`、`route3-…` 与 `evidence/alibaba-routes.json`；
  `alibaba-blocker.json` 已按实测重写（路线 1 `source query market mismatch` calls=2；路线 2 `operation market mismatch` calls=2；
  路线 3 `source_blocked: local_metadata_gap`；路线 4 `ensure exited 1` / `dayu-us-sdk discover exited 1`）。

## F-15（P2，边界决定）拒绝"自己抓取 + 手工 import"的越界路线

- 事实：为解开 Alibaba，我曾验证过一条非模块路线——自己用 HTTPS 下载 SEC 20-F，再用 company-wiki `official import`
  登记。只做了 SEC 的**元数据索引**查询（`data.sec.gov/submissions`，未下载任何年报正文），随后被操作者否决并停止。
- 决定：**不采用**。本项目的采集归属 `filing-fetch` → `company-wiki`，任何"harness 自己下载 + 手工登记"的路径都绕过模块边界，
  即便能过校验也不构成可接受交付。据此 Alibaba 保持 NOT_RUN，交由 CWP/FF owner 修投影或适配器。
- 影响：Alibaba 的 6 条路线全部改由 `source_preparation.py` → `filing_fetch_client` → filing-fetch → company-wiki 驱动并留证
  （`evidence/alibaba-routes.json`），无一条绕过模块接口。
- 教训：遇到模块拒绝时，正确动作是"换模块支持的参数再试 + 记录机器原因 + 升级给 owner"，而不是在 harness 侧补一段下载器。

## F-16（P3，口径澄清）两个哈希不是同一个量

- 交付作业的 `result.json`：`result_sha256=04768c27…`（引擎对 **去掉 `result_sha256` 字段后**的 payload 做 canonical 哈希）。
- `revenue_backtest.py create` 生成的冻结快照：`forecast_result_sha256=4587acc8…`（对**完整冻结 dict**做 canonical 哈希），
  其 `input_sha256=6169ea8a…` 与作业一致。
- 实测：快照内 `forecast_result` 与交付 `result.json` **整字典相等**（数值/分段/基准/置信度全同），两哈希分别标识同一预测的不同封装；
  不互相替代，也不能拿一个去核对另一个。已在 `handoff.json.inputs[0].derived_artifacts` 写明。
