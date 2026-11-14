# 独立重审报告 · Part 4 诚实性分片（OWNERPKG-REVENUE-FORECAST-01 §8-1）

- 审查分片：honesty（诚实性）。审查者未参与本包实现（独立分片）。
- 日期：2026-11-08。审查对象：worktree `C:/Users/郑曾波/Projects/rf-job-facade-01-wt`，分支 `codex/rf-job-facade-01`，HEAD `8cd4e18a`（基线 `28d646d3`）。
- 依据：施工包 `investment-dashboard/handoffs/owner-requests/revenue-forecast/BUILD-PACKAGE.md` §5.7 / §3.6 / §8-1。
- 方法：只读核对 + 重跑 README 声明的两条 pytest 命令（conftest 将 registry 重定向到 tmp，不写仓内数据）。**未重跑 drill.py**（会覆盖 evidence 现状文件）。本分片只写了本报告文件，未改任何实现代码。

---

## 逐项核对结论

### 核对 1 — evidence/README.md 的 NOT_RUN/限制清单：**基本完整、真实，无 mock 冒充真实**

- NOT_RUN ①：真实生产三仓链路未跑，如实说明（"the drill runs the real CLIs offline against the isolated-lake fixture instead"），原因登记为预算闸门（生产运行仅限 owner 批准的演练），并说明 fixture 路径行使同样的 subprocess 合同、零下载。与实况相符：drill.py 确实以真实子进程驱动 `scripts/rf_job_cli.py` + 真实 filing-fetch checkout（`FF_ROOT = ~/Projects/filing-fetch`）+ IsolatedLake 离线 fixture（drill.py:37-38, 137-172）。
- NOT_RUN ②：catalog 管理登记未做且如实说明（facade 范围外，G-m8-RF-05；facade 只产出登记就绪证据）。与实现一致：`job_view()` 的 `catalog_history` 明示 external explicit management import、`this_job_registered=False`（scripts/rf_job_facade.py:1250-1255），全仓 grep 无 façade 调用 `import-research-attempt` 的路径。
- FakeStageRunner/单测被明确声明"不作为跨仓真实证据"（README §5.7 第 3 条），且措辞精确：process-level 证据仅限 drill 与 `tests/test_rf_job_facade_cli.py` 的真实子进程测试。核实：`test_rf_job_facade_cli.py` 全部走 subprocess + IsolatedLake，无 FakeStageRunner；FakeStageRunner（rf_job_facade.py:708）只被单测文件使用。
- 全文未发现把 mock/单测说成真实演练的措辞；"real" 一词仅用于 CLI --help 输出、JobView、子进程链，均属实。
- 自然失败样本（对 fixture 提交不存在的公司触发 filing-fetch 自然报错）是真实链路的真实失败语义，非伪造数据，README 描述准确（exit 3、zero downloads、attempts 记录在案）。
- 小瑕疵：README 第 5-6 行交叉引用"see progress.md 2026-11-07"，但预算边界上报实际登记在 progress.md 的 2026-11-08 节（progress.md:36-38）→ 记 FND-H2。

### 核对 2 — findings.md F-04 六条 vs 实现：**六条全部与实现一致（含两条抽验通过）**

| # | F-04 条目 | 核对结果 |
|---|---|---|
| 1 | 阻塞式 submit | **属实**（抽验）：`submit()` 创建 durable job 后同步调用 `self._orchestrate_locked(...)`（scripts/rf_job_facade.py:1331），编排跑完才返回；`_orchestrate_locked` 串行跑完三阶段（:1421-1437）。README/drill 的 kill 演练（taskkill /T /F 杀 submit 进程树）也印证 submit 期间进程就是编排进程。 |
| 2 | catalog 登记独立 | 属实：facade 不做管理登记，JobView.catalog_history 硬编码 `this_job_registered=False` + 指向外部显式 import 命令（:1250-1255）。 |
| 3 | source_snapshot_ids 只记录 | **属实**（抽验）：全仓 grep 仅 3 处——请求校验（:460-465）、写入 job scope（:484）；从不被读回用于构建阶段请求（source 阶段请求 = 模板 + company_query + as_of_date，:822-827），不映射为阶段输入。 |
| 4 | company_query 不硬核对 | 属实：`_validate_forecast_input` 只做 `as_of_date == information_as_of` 相等核对（:508），company_name 与 company_query 无任何交叉核对（grep `company_name` 在 rf_job_facade.py 零命中）。 |
| 5 | compute 注册表窗口重复登记 | 登记属实且被演练自然复现：引擎先 `prepare_forecast`（formal 追加 registry）后写 result.json（revenue_forecast.py:85-91），kill 窗口存在；最新一轮 drill 的 `publication_registered_lines: 2`（drill_summary.json:106）即同锚点重复登记行的真实产物，façade 未静默去重，与登记一致。 |
| 6 | budget 由 façade 记录 | 属实：elapsed 由 façade 计时累加（:1020-1022），download/model 计数来自 producer receipt/纯计算属性（:863-880, :907-914），非外置 recorder。小缺口见 FND-H4（失败 attempt 不计入 wall budget，未在 F-04 登记）。 |

### 核对 3 — drill_summary.json 与 README 一致性：**工作区当前证据集自洽；HEAD 已提交版与 README 存在矛盾（FND-H1）**

- 步数与结论：drill_summary.json（工作区）恰 8 步、全部 `ok=true`、`failures: []`；drill_summary.md 8 行 PASS、Failures: 0；progress.md "8/8 PASS" 一致。
- README 引用的文件全部存在于 evidence/：help-root/submit/get-status/act/list-jobs.txt（5 份，内容为真实 argparse 输出、exit=0）、drill.py、drill_summary.json、drill_summary.md、natural_failure_jobview.json、cost_known_sample.json、cost_unknown_sample.json、budget_observation.json。
- README §5.2/§5.3 的具体断言逐条能在 drill_summary.json 找到对应字段（same_owner_job_id、idempotent_replay、stage_attempts_before==after、source_attempt_count==1、compute attempt 2 完成等）。
- **但**：三个证据 JSON（drill_summary.json / natural_failure_jobview.json / budget_observation.json）在 HEAD 之后被重新生成且未提交（`git status` 为 M）。HEAD 提交版 drill_summary 显示 kill 落在 publication 阶段（restart 时 compute=completed、publication=interrupted、resume 后 compute attempt 1 即完成），与已提交 README §5.3 "the killed compute attempt legitimately retried" 矛盾；工作区版本（kill 落在 compute、attempt 2 重试成功）才与 README 吻合。两轮都是真实运行、8/8 全过、语义一致，无造假，但 HEAD 自身证据链不自洽 → FND-H1（P2，须在 §6 交接前提交再生成证据）。
- README 声明的测试计数经重跑验证：`pytest -k rf_job` → **36 passed**（25.78s）；`test_rf_job_boundary_regression.py + test_report_catalog_deployment.py` → **45 passed**（7+38，与 README 分项一致）。

### 核对 4 — evidence/ 样本是否真实过程产物：**是，均为 drill.py 程序化写出，互相吻合**

- `drill.py`（465 行）在运行中直接写出全部样本：natural_failure_jobview.json（:403-405）、cost 两样本（:419-424）、budget_observation.json（:438-445）、drill_summary.json/md（:451-461）。样本形状与 `job_view()` 实现逐字段吻合（catalog_history/command_recovery/scope/attempts 等）。
- natural_failure_jobview.json：真实自然失败形状——status=failed、source attempt exit_code=3、elapsed 1.894s、observations `{acquisition_calls:1, download_events:0}`、cost known 0.00；与 drill_summary 步骤 5.4 的 owner_job_id（rfjob-20261108-56990214fa47）/数值完全一致；与 F-06（calls≠付费）修复后语义一致。
- cost 样本与 drill_summary 步骤 5.5 逐字节一致（known：USD 0.00/failed；unknown：null/interrupted）。known 样本来自"每次 attempt 都有观测"的自然失败 job，README §5.5 描述准确，无夸大。
- budget_observation.json：`new_downloads_total: 0`、`paid_model_calls_total: 0`（0 下载 0 付费）✓；两个 job 的 budget 值与各自 job.json 口径一致（killed job 的 compute attempt 1 被杀无观测，elapsed 为 null，如实呈现不回填）。
- 交叉 ID 一致性：budget_observation、drill_summary、natural_failure_jobview 三者间的 owner_job_id 完全互相对应，同一轮运行的产物。

### 核对 5 — task_plan.md Nodes vs 实际进度：**无"标完成实际没做"；问题是反向的滞后未勾选（FND-H3）**

- 前 4 节点（读包/侦察/基线/PWF 登记）勾选，与 git/progress 相符。
- **重点检查项**：`§8-1 独立重审` 与 `§6 handoff` 均如实标记未完成（`[ ]`）——核实：handoff.md/handoff.json 在 `.planning/rf-job-facade-01/` 下不存在（仓内其他 handoff 属历史包），本分片审查即是 §8-1 进行中的一部分。诚实。
- 反向问题：设计（design.md 已定稿，2026-11-07）、G-m8-RF-01..05（已实现并各自有 commit）、单元测试（36 passed）、验收证据 §5.1-§5.7（evidence/ 齐全）共 9 个节点实际已做但 checkbox 未勾。无静默缩水、无虚报完成，但 PWF 计划资产滞后，§8-2"每个节点更新"未贯彻到 checkbox → FND-H3（P3）。

### 核对 6 — progress.md 时间线 vs git log：**大体吻合**

| progress 记录 | git log 对应 | 吻合 |
|---|---|---|
| 2026-11-07 开工/基线/建分支/PWF 登记 | `abfba190 docs(job): register ... planning package`（11-07 21:14） | ✓ |
| 2026-11-07 设计定稿 + G-01..05 契约测试 + 真实子进程集成 + 全量 36 passed | `60ac299d`(22:51 feat G-01) → `709c6fea`/`e65ba44e`/`732ff8b0`(22:52 G-02/03/04) → `caf6e259`(22:54 集成) → `99e1d52d`(22:54 docs) | ✓ |
| 2026-11-08 预算边界上报→演练三轮迭代→853c26d9 修复→演练 8/8→§5.6→§5.7 | `853c26d9`(00:07 fix) `1d2b6f5c`(00:07 演练证据) `8cd4e18a`(00:09 findings) | ✓ |
| "遗留：演练证据、独立重审、handoff 待办"（11-07 节） | 与当前实际状态一致（handoff 未写、重审进行中） | ✓ |

- 最后一轮演练再生成（约 00:13，产生当前工作区证据）发生在末次 commit 之后，progress.md 未记一行——归入 FND-H1/FND-H3 一并整改。
- 附带红线佐证：`git diff --name-only 28d646d3..HEAD` 仅新增 `scripts/rf_job_cli.py`、`scripts/rf_job_facade.py`、`config/rf_job_deployment.example.json`（+tests/.planning），既有引擎/CLI 文件零改动，与 design.md/F-04 声明一致。

---

## Findings

### FND-H1
- **severity**: P2
- **title**: 演练证据在末次 commit 后重新生成且未提交；HEAD 证据集与已提交 README 自相矛盾
- **reproduction**: `git status --short` → 3 个 M（budget_observation.json / drill_summary.json / natural_failure_jobview.json）；`git show HEAD:.planning/rf-job-facade-01/evidence/drill_summary.json` 的"5.3 restart get-status"显示 compute=completed、publication=interrupted（kill 实际落在 publication），而已提交 README §5.3 写"the killed compute attempt legitimately retried"（与工作区版本一致，kill 落在 compute、attempt 2 重试）。HEAD 上 README 与 drill_summary 对不上。
- **root_cause**: 1d2b6f5c 提交的证据取自较早一轮运行；随后（约 00:13）重跑 drill.py 再生成证据（工作区），只提交了 findings/progress（8cd4e18a），未提交新证据；README 文本按目标场景（kill compute）撰写。两轮均为真实运行、8/8 全过、语义一致——是证据封存流程缺陷，不是造假。
- **retest**: 提交当前工作区三个证据文件（它们与 README 自洽且互洽），复核 `git status` 干净、HEAD 的 drill_summary/README/budget_observation 三者一致；progress.md 补记一行再生成原因。
- **reviewer_status**: OPEN（0 OPEN P1/P2 方可进 §6；本条须在交接前关闭）

### FND-H2
- **severity**: P3
- **title**: README 交叉引用日期错误（预算边界上报登记为 2026-11-08，README 指向 2026-11-07）
- **reproduction**: evidence/README.md 第 5-6 行 "Budget boundary was reported to the operator before the first drill run (see progress.md 2026-11-07)"；progress.md:36-38 该条在 "## 2026-11-08" 节。
- **root_cause**: 演练跨零点（11-07 深夜→11-08 凌晨），README 引用时未对齐 progress 分节日期。
- **retest**: README 改为 "2026-11-08"（或写"演练当次运行前"）。
- **reviewer_status**: OPEN

### FND-H3
- **severity**: P3
- **title**: task_plan.md Nodes 滞后：9 个已完成节点未勾选（无反向虚报；§8-1/§6 如实未勾）
- **reproduction**: task_plan.md Nodes 中"产出设计 / G-m8-RF-01..05 / 单元测试 / 验收证据 §5.1-§5.7"均 `[ ]`，但 design.md 存在、五个 G 条目各有独立 commit、36+45 测试重跑通过、evidence/ 齐全。`§8-1`/`§6` 如实 `[ ]`（handoff 文件不存在，属实）。
- **root_cause**: 完成节点后只更新了 progress.md 未回勾 task_plan checkbox（§8-2 的节点更新只做了一半）。
- **retest**: 按 §8-2 将实际完成节点勾选（§8-1/§6 保持未勾直至真实完成）；progress.md 补记 11-08 末次证据再生成一行。
- **reviewer_status**: OPEN

### FND-H4
- **severity**: P3
- **title**: budget.wall_seconds_used 不计失败/被杀 attempt 耗时，F-04 第 6 条未登记此口径
- **reproduction**: scripts/rf_job_facade.py:1018-1027 仅在 stage 完成后累加 elapsed；budget_observation.json 中自然失败 job（rfjob-20261108-56990214fa47）wall_seconds_used=0.0，而其 source attempt elapsed=1.894s（attempt 记录如实含 elapsed，仅预算累加跳过）。被杀 attempt（elapsed null）同理不计。
- **root_cause**: 预算累加点放在完成路径上；后果是重复失败可消耗大量墙钟而不触墙预算闸门。attempt 级耗时仍被如实记录，故非数据造假，属未登记的口径限制。
- **retest**: 在 findings F-04 补一条该口径（或改为对 failed/interrupted attempt 也累加 elapsed 后再判闸门），二选一。
- **reviewer_status**: OPEN

---

## 结论（诚实性维度）

- §5.7 NOT_RUN/限制清单：完整、真实，无 mock/单测冒充真实跨仓证据的措辞。
- F-04 六条限制与实现全部一致（抽验 blocking submit、source_snapshot_ids 均属实）。
- evidence 样本为真实过程产物，互相吻合；0 下载 0 付费属实；36/45 测试计数重跑复现。
- task_plan/progress 与 git log 时间线吻合；无任何"标完成实际没做"的节点。
- 计 4 个 finding：**P2 × 1（FND-H1，须在 §6 交接前关闭）、P3 × 3**。无 P1。
- 本分片为只读审查，除本报告外未写任何文件；未重跑 drill.py 以免覆盖证据现状。
