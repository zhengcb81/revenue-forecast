# 独立复核报告 · OWNERPKG-RF-INPUT-PREP-01

- 复核对象：分支 `codex/rf-input-prep-01`，base `d347c4ab`，HEAD `60072ba5`，worktree `C:/Users/郑曾波/Projects/rf-input-prep-01-wt`
- 复核人：未参与实现的独立 reviewer；本报告为本次唯一新增文件
- 时间：2026-11-08（UTC）；方式：固定命令 + 10-K 文本抽取抽样 + 输入/证据 JSON 结构化读取

## 1. 结论

**FAIL** —— 数据真实性与诚实性核验通过；交付合同未达标（包 §8 要求 0 OPEN P1/P2 才能交接）。

- OPEN：**P1 = 2，P2 = 1，P3 = 4**
- 数据面：MongoDB FY2025 六项披露数字与 10-K 文本完全一致；31 个参数中 27 个增长参数全部为 `analyst_assumption`；capture/hash 自洽，未发现伪造。
- 交付面：`handoff.json` 的 commit 字段仍为占位符；handoff 指向的 job 产物不在交付 commit 内。两项均直接阻断 Dashboard 按固定 commit 消费。

## 2. 复核命令表

6/6 实际执行，无“未执行”项。

| # | 命令 | exit | 输出（trim） |
|---|---|---|---|
| 1 | `python scripts/lint_input.py ...inputs/mongodb-fy2025-input.json` | 0 | `ok: no findings` |
| 2 | `python scripts/fix_hashes.py ...inputs/mongodb-fy2025-input.json` | 0 | `ok: no hash drift`（输入文件未被改写） |
| 3 | `python scripts/revenue_forecast.py ...inputs/mongodb-fy2025-input.json --validate-only` | 0 | `valid` |
| 4 | `python -B scripts/rf_job_cli.py ... get-status --job-id rfjob-20261108-ea663b8bd33e` | 0 | `status=succeeded`、`status_known=true`、`allowed_actions=[]`、`cost={USD,0.00}`、`cost_state=known`、`new_downloads=0`、`paid_model_calls=0`；source attempt1 failed→attempt2 `reused_existing`；compute/publication completed |
| 5 | `git diff --name-only d347c4ab..HEAD` | 0 | 68 个文件，**68/68** 以 `.planning/rf-input-prep-01/` 开头；非写域 0；**无 `job-root/` 文件** |
| 6 | `python .planning/rf-input-prep-01/verify_excerpt_fidelity.py` | 0 | `{"distinct_excerpts": 14, "verbatim_count": 12}` |

## 3. 独立核验表

| # | 主张 | 判定 | 证据 |
|---|---|---|---|
| 1 | 合并总收入 FY2025/FY2024/FY2023 = 2,006,443 / 1,683,011 / 1,284,040 千美元 | verified | `mdb-fy2025-10k.txt:900-902,957-959,1258-1260,1885,1894`，三张表数值互证 |
| 2 | 分拆行 FY2025：Atlas-related 1,405,184；Other subscription 538,680；Services 62,579 | verified | `mdb-fy2025-10k.txt:1887-1892`（行标签与单元格一致） |
| 3 | `reported_total = 2006.443`（USD million） | verified | 输入 `parameters[0]`：value=2006.443，unit=`USD million`，kind=`reported_fact` |
| 4 | 三段 `*_base` = 1405.184 / 538.680 / 62.579 | verified | `atlas_base` / `other_subscription_base` / `services_base` 三条 `reported_fact` |
| 5 | 27 个增长参数全部 `analyst_assumption`，无 `reported_fact` | verified | 31 个参数：`reported_fact=4`（total+3 base）、`analyst_assumption=27`（3 段×3 年×3 情景） |
| 6 | `capture.snapshot_sha256 = b3788068…` | verified | source[0].capture 与 company_wiki_trace（byte_size=2,108,287）一致 |
| 7 | `host_receipt` 存在且完整 | verified | issuer=company-wiki、action=verified_read、event_sha256=b3788068…、timestamp=2026-11-08T08:29:31Z |
| 8 | `capture.receipt_sha256` = `fix_hashes.py` 重算值 | verified | 525ce1ed…；fix_hashes 语义=canonical_sha256(capture 去掉 receipt_sha256)，第 2 步 `no hash drift` 即一致；`host_receipt.receipt_sha256=09d6a26a…` 是 host 内层自哈希，不要求等于外层值 |
| 9 | job 终态 succeeded、零成本 | verified | 命令 4 输出；三阶段 3/3 completed，wall=8.06s |
| 10 | 预算上限 1.00 USD、实际 0.00 | verified | `deployment-mongodb.json` 的 `max_cost_usd="1.00"`；JobView `cost={USD,0.00}`、0 下载/0 付费调用 |
| 11 | 写域仅 `.planning/rf-input-prep-01/` | verified | 命令 5：68/68 合规 |
| 12 | 未改引擎/CLI、未改 Dashboard/company-wiki | verified | 命令 5 变更集无 `scripts/`、无其他仓路径 |
| 13 | 无伪造 receipt/hash | verified（未发现） | 结构自洽 + fix_hashes 无漂移 + snapshot_sha 与 source record 一致 |
| 14 | `handoff.json head_commit` / `release_tag_or_commit_for_dashboard` 可解析 | **contradicted** | `handoff.json:8-9` 均为 `HEAD_COMMIT_PLACEHOLDER`，实际 HEAD 为 `60072ba5` |
| 15 | handoff 指向的 job 产物在交付 commit 内 | **contradicted** | 命令 5 的 68 文件无 `job-root/`；但 handoff 的 `result_artifact`/`report_markdown` 均在 `job-root/` 下 |
| 16 | `task_plan.md` N5 输入哈希与交付一致 | **contradicted** | 记 `1c82fc34…`；实际 sha256=`04d30eb0…`（handoff/artifacts/excerpt-fidelity 三处一致） |
| 17 | Alibaba NOT_RUN 及具体原因 | verified | `alibaba-blocker.json` 四条具名路线 + `requests/*stderr.txt` 留档 |
| 18 | catalog 登记 NOT_RUN 及原因 | verified | handoff `catalog_status=NOT_RUN`；JobView `this_job_registered=false`；`owner_root_missing` |
| 19 | management targets NOT_RUN | verified（文档层） | handoff `not_delivered` 第三条 + findings F-04；未逐条复核 input 内 coverage |
| 20 | 2/14 excerpt 非逐字 | verified（已披露） | `evidence/excerpt-fidelity.json` + findings F-11 |

## 4. 发现清单

### F-01（P1，OPEN）handoff 的 commit 字段为占位符
- 位置：`.planning/rf-input-prep-01/handoff.json:8-9`
- 事实：`head_commit` 与 `release_tag_or_commit_for_dashboard` 均为 `HEAD_COMMIT_PLACEHOLDER`。
- 影响：包 §7 要求该字段为可 `git rev-parse` 解析的 40 位 commit，Dashboard 以“固定候选 commit”消费（§6/§7、progress.md:74）。占位符使交接合同不可执行。
- 修复：填入实际 40 位 commit（至少 `60072ba5…`）；用两次提交或附加 `handoff_commit` 字段解决“文件无法自指自身 commit”，同步 handoff.md。

### F-02（P1，OPEN）handoff 引用的 job 产物未进入交付 commit
- 位置：`handoff.json` `inputs[0].result_artifact` / `report_markdown`；`.planning/rf-input-prep-01/job-root/`
- 事实：命令 5 的 68 个文件全部在 `.planning/rf-input-prep-01/` 下且不含任何 `job-root/` 文件（job 为本次新建，base 中亦无）。`result.json`（`result_artifact_sha256=2fa1170d…`）、`report.md`、`publications.jsonl` 仅存在于 worktree，未入库。
- 影响：progress.md:74 要求 Dashboard“按固定 commit + result.json + result_sha256”消费；交付 commit 上这些字节不存在，`result_sha256=e5c6ceb3…` 无对应可读取产物，交付链实质断点。
- 修复：将 `stages/compute/result.json`、`report.md`、`registry/publications.jsonl`（及 source/compute/publication 的 envelope/audit）纳入提交，或复制到 `evidence/` 并更新 handoff 路径；若坚持不入库，须在 handoff 明确“从 worktree 读取”的绝对路径并删除 commit 语义。

### F-03（P2，OPEN）task_plan 记录的输入哈希与交付输入不一致
- 位置：`.planning/rf-input-prep-01/task_plan.md:30`
- 事实：记 `input_sha256 1c82fc34…`；交付文件实际 sha256=`04d30eb0…`，handoff.json、evidence/artifacts.json、evidence/excerpt-fidelity.json 三处均为 `04d30eb0…`。
- 影响：审计轨迹出现两个“最终输入”版本，且 `evidence/mdb-validation-chain.json` 未绑定 input_sha256（仅命令/exit/stdout），不能证明校验链跑在交付字节上；本次现场重跑 1-3 均通过，功能无问题，但可追溯性受损。
- 修复：更新 N5 为 `04d30eb0…` 或记录 `1c82fc34→04d30eb0` 的修订原因；在 validation-chain 证据中写入 input_sha256 与运行时间。

### F-04（P3，已披露）2/14 excerpt 为阅读顺序渲染而非逐字子串
- 位置：`evidence/excerpt-fidelity.json`；claims `claim_reported_total_2025`、`claim_atlas_base`
- 事实：`verbatim_count=12/14`；两段表格 excerpt 与抽取文本的单元格换行方式不同，但数字序列与 `verbatim_block` 完全一致，locator 指向同一披露表行。
- 影响：不构成数值失真；下游若把 excerpt 当逐字引文会误判。findings F-11 已如实披露。
- 修复（可选）：改用 `verbatim_block` 原文串，或在 claim 内标注 `rendered: true`。

### F-05（P3，已披露）publication `audit.json` 为 0 字节
- 位置：`job-root/.../stages/publication/audit.json`；JobView `publication.sha256=e3b0c442…`（空串哈希）
- 影响：成功语义与空产物在 Dashboard 侧可能被误读为失败；findings F-09 已披露，属发布器输出习惯，不在本包改引擎授权内。
- 修复：交接说明标注“0 字节=成功（audit 静默）”；引擎侧后续输出一行 JSON（包外）。

### F-06（P3，已披露）catalog 登记 NOT_RUN，§5.4 正式读取路径未打通
- 事实：handoff `catalog_status=NOT_RUN`、`catalog_report_id=null`；JobView `this_job_registered=false`；`list-reports` 返回 `owner_root_missing`。
- 判断：原因具体（缺 B34 trusted research-admission 包），未伪造登记，属诚实 NOT_RUN；但包 §5.4“正式报告可读”验收项未满足。

### F-07（P3，已披露）Alibaba 与 management targets 为 NOT_RUN
- 事实：`alibaba-blocker.json` 记录 4 条具名失败路线（market mismatch×2、local_metadata_gap、US adapter exit 1），对应 `requests/*.txt/json` 留档；management targets 无官方材料，6 类 coverage 全 incomplete。
- 判断：均有具体原因与证据，未发明数字或搜索事件；属采集层/范围限制。

正向结论：除 F-01~F-03 外，未发现数字编造、receipt/hash 伪造、引擎或跨仓改动。MongoDB 输入、作业、报告的数字与命令证据均可落到 repo 内文件。

## 5. 未覆盖/未能验证项

- 未读 2,108,287 B HTML 原件（硬约束）；六项数字基于 470 KB 文本抽取抽样核验，未做 HTML 字节级比对。
- 第 6 项输出与 `evidence/excerpt-fidelity.json` 完全一致；未审阅 `verify_excerpt_fidelity.py` 是否独立重算（若仅读取该 JSON，则该命令不构成独立证据）。
- 未复跑 company-wiki / filing-fetch；Alibaba 四条失败路线仅核对留档 artifact，未独立复现 machine cause。
- 未验证 `limits_ref` 是否支持 `max_bytes`；deployment 仅见 `max_cost_usd`/`max_wall_seconds`/`max_new_downloads`（包 §3 提及 max_bytes）。
- 未逐字节比对 `evidence/mongodb-forecast.json` 与 job `result.json`；二者记录的 `result_sha256=e5c6ceb3…` 一致。
- 复核开始时 worktree 已存在未跟踪的 `review-report.md`（不在 `d347c4ab..HEAD` 的 68 文件内），本报告将其覆盖；其来源/作者未验证。
- 未验证 Dashboard/company-wiki 仓的实际读取行为与验收卡。

## round 3 · delta 复核（60072ba5..10092580；handoff 4bf28e00）

**范围**：按修正后的最终快照复核。复核期间分支从 `3503e12c` 前移到 `10092580`/`4bf28e00`；`git merge-base --is-ancestor 3503e12c HEAD` 与 `39cf1433` 均为 exit 1，旧 pair 已被取代、未复用。最终 `git status` clean。

### R3 命令与结果

| # | 命令 | exit | 输出（trim） |
|---|---|---|---|
| 1 | `git rev-parse 10092580` / `git rev-parse HEAD` | 0 | `1009258075f835c5d5f7d4cff563cb8fc722c740` / `4bf28e00b409a316b49dd7d906e0424d10d09471`；`git log --oneline 60072ba5..HEAD` = 10092580、4bf28e00 两提交 |
| 2 | `git diff --stat 60072ba5..10092580` | 0 | 49 files, +10,006/−190（v2 输入、job 字节副本、Alibaba 证据）；`10092580..4bf28e00` 另 4 文件（`.gitattributes`/`.gitignore`/`handoff.json`/`handoff.md`） |
| 3 | `git cat-file -e 10092580:.planning/rf-input-prep-01/evidence/job-rfjob-20261108-eb9f2a3ed336/stages__compute__result.json` | 0 | 文件在提交内 |
| 4 | `python scripts/lint_input.py ...inputs/mongodb-fy2025-input.json` | 0 | `ok: no findings` |
| 5 | `python scripts/fix_hashes.py ...inputs/mongodb-fy2025-input.json` | 0 | `ok: no hash drift` |
| 6 | `python scripts/revenue_forecast.py ...inputs/mongodb-fy2025-input.json --validate-only` | 0 | `valid` |
| 7 | `python -B scripts/rf_job_cli.py ... get-status --job-id rfjob-20261108-eb9f2a3ed336` | 0 | `succeeded`、`status_known=true`、`allowed_actions=[]`、`cost={USD,0.00}`、`new_downloads=0`、`paid_model_calls=0`、三阶段 completed；publication `audit.json` sha=`e3b0c442…`（空） |
| 8 | `python .planning/rf-input-prep-01/verify_excerpt_fidelity.py` | 0 | `{"distinct_excerpts": 14, "verbatim_count": 14}` |
| 9 | manifest-vs-committed-blob（10 文件，自写只读 Python） | 0 | 10/10 `sha256` 与 `byte_size` 均等于 `10092580` 提交 blob；`result` `c0dce8c3…`（326,471 B）、`report` `0bae0856…`（53,291 B） |
| 10 | 提交内 input/blob 哈希（同上） | 0 | `inputs/mongodb-fy2025-input.json` = `d82f9b45…`，146,551 B；`reported_total=2006.443`、3 条 `historical_revenue` 均带 `rf-revenue-basis/1`（operations=total / as_reported / fiscal_year） |
| 11 | Alibaba `route{1,2,3}-*.stderr.json` 对照 `alibaba-blocker.json` | 0 | route1=`company-wiki source query market mismatch`；route2=`operation market mismatch`；route3=`local_metadata_gap`，与 blocker 一一对应；route4 旧 `requests/alibaba-20f-stderr.txt` 仍在 |
| 12 | 交付文档输入哈希扫描 | 0 | handoff.json / progress.md / evidence/artifacts.json 均为 `d82f9b45…`；**task_plan.md:30 仍为 `6687a3b5…`** |

### 逐项裁定

| 项 | 裁定 | 依据 |
|---|---|---|
| round-2 P1-1 handoff 占位符 | **closed（handoff commit 4bf28e00）** | `head_commit` = `release_tag_or_commit_for_dashboard` = `10092580…`（40-hex，`rev-parse` 可解析）；残留见 P3-1 |
| round-2 P1-2 job 产物未入库 | **closed** | `cat-file -e` exit 0；manifest 10/10 与提交 blob 的 sha256+字节数一致 |
| round-2 P2-3 task_plan 输入哈希 | **still open** | `task_plan.md:30` 仍记 `6687a3b5…`；实际交付 `d82f9b45…` |
| round-2 P3-4 表格 excerpt | **closed** | fidelity 14/14；`excerpt-fidelity.json` 已折叠进 `10092580` |
| 新增 revenue_basis | **verified** | reported_total 与 3 条 historical 均为 `rf-revenue-basis/1` |
| 新增 job | **verified** | succeeded、0 下载/0 付费、0.00 USD、`result_sha256=04768c27…`、artifact `c0dce8c3…` |
| Alibaba routes 1-3 证据 | **verified** | 三个 stderr 的 reason 与 blocker 一致；route4 沿用旧证据 |

### 残留/新增发现

- **P3-1（新，已披露级）** 内容 commit `10092580` 内的 `handoff.json` 仍是 `HEAD_COMMIT_PLACEHOLDER`；修正后的 handoff 只在 `4bf28e00`。`handoff.json` 的 `handoff_commit`/`pin_commit` 为 null，`handoff.md` 也未点名 `4bf28e00`。只 checkout 内容 commit、按 §7 读 handoff 的消费者会再次看到占位符。修复：增加 `handoff_commit: 4bf28e00…` 并在 handoff.md 注明“内容 commit 内的 handoff 为打包前副本”。
- **P2（仍未关，原 P2-3）** `task_plan.md:30`：“v2 input sha256 `6687a3b5…`；v1 `04d30eb0…` 已被 v2 取代”。实际交付 v2 = `d82f9b45…`（146,551 B）；handoff.json、progress.md、evidence/artifacts.json 均一致，唯 task_plan 未更新。修复：改为 `d82f9b45…` 并注明 v2 修订（excerpt 保真折叠）原因。
- 已披露 P3（未变化）：publication `audit.json` 0 字节；catalog 登记 NOT_RUN（缺 B34 trusted 包，§5.4 未满足）；Alibaba NOT_RUN（route4 未重放，旧证据保留）；management targets NOT_RUN。

### R3 最终计数

**OPEN P1 = 0，P2 = 1，P3 = 4**。按 §8-1 当前**尚不可交接**（仅剩 task_plan 一处哈希未同步；修一行即可）。关闭后 P1=P2=0，可作为“部分交付”交接；但 catalog 未登记、Alibaba 未交付，G-m5-EXT-01 仍不能宣告解除。

## round 4 · 最终 delta（0993abb3 / 0afcb16f）

- 验证：`git rev-parse 0993abb3` 解析通过；HEAD `0afcb16f` 的 handoff `head_commit` 与 `release_tag_or_commit_for_dashboard` 均 pin `0993abb3`；snapshot blob sha256=`4798e682…`（398,344 B，`forecast_result_sha256=4587acc8…`）；input blob=`d82f9b45…`（146,551 B），`revenue_forecast.py --validate-only` exit 0 `valid`。
- 写域：`d347c4ab..HEAD` 118 文件 118/118 在 `.planning/rf-input-prep-01/`；**P1/P2 = 0/0**。
