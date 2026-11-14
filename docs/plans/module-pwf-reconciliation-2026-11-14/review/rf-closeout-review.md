# RF-PLAN-WORKTREE-CLOSEOUT 独立审查报告（draft）

- 审查日期：2026-11-14
- Reviewer：独立 reviewer agent（未参与本卡实施）
- 仓库：`C:/Users/郑曾波/Projects/revenue-forecast`
- **绑定审查 HEAD：`a7a1818a12f5226fe6eb1190cf373fbdf02ddc0d`**（base = 其父提交 `ec5ba0044b3252d2fc58c4a50c2fe9bc234cf5ad` = 当前 `origin/main`，候选未推送）
- 审查方式：全程只读（`git show` / `git worktree list --porcelain` / `git merge-base --is-ancestor` / `git cat-file` / `python -I` 只读解析 / 文件存在性检查）；零写入仓库、零 checkout/reset。

## 0. 结论（一行）

**PASS** —— 无必须修复项；5 项建议（其中 R-1 为建议推送前修正的证据表述错误，非阻断），详述见第 3 节。

## 1. 审查范围

候选提交 `a7a1818a` 全部变更及其交接物（`rf-closeout-handoff.md` + `rf-closeout-handoff.json`）、PLANNING_STATUS canon 区与 5 处回链、清理执行结果与实时 Git/文件系统状态的一致性、吸收证据真实性、status 用词与卡定义的符合性。

## 2. 逐项发现

### V-1 提交范围核查 — 关闭（PASS）

- `git show --stat a7a1818a`：8 文件、+1277/-0，全部为文档（PLANNING_STATUS.md +57、mb11 task_plan.md +2、w20 task_plan.md +2、findings.md +2、progress.md +2、task_plan.md +2、review/rf-closeout-handoff.json +1126 新增、review/rf-closeout-handoff.md +84 新增）。零代码文件。
- `git diff --check a7a1818a~1..a7a1818a`：无输出（exit 0），无空白错误。
- 主仓 tracked 状态：`git status --porcelain` 仅 6 组 untracked（`.mimosa/`、`.planning/m8-native-adoption-20261031/`、`.planning/source-quote-adoption-20261030/`、`delivery/dashboard-b34-wuxi-20261101/`、`delivery/dashboard-b37-wuxi-20261102/`、`output/`），零 tracked 修改；HEAD=main=a7a1818a，父提交=`ec5ba004`=`origin/main`（实测）。

### V-2 handoff.json schema 核查 — 关闭（PASS）

- 裸 JSON `python -I json.load` 可解析（无 BOM/注释/尾逗号）。
- `schema_version=1`；顶层键恰为卡要求的 13 键：schema_version / lane / repo_root / canonical_pwf / base / final / dispositions / dirty_exceptions / cleanup / tests / independent_review / remaining_items / next_step。
- `dispositions` 共 94 项，kind 分布 **branch=19、worktree=61、projects_dir=14**，与卡要求逐一相符。
- 全部 94 项均含 `kind/path/status/reason/evidence` 四要素（程序化检查零缺漏）。
- `base.remote_head` 与 `final.remote_head` 均非 null（=`ec5ba0044b32...`，实测与当前 origin/main 一致）。`final.head=ec5ba004`（=base）：文档提交无法自含自身 SHA，JSON 以"提交前状态 + independent_review.reviewed_head 注明 'SELF - 本提交即审查候选，精确 SHA 记入 rf-closeout-review.md'"处理，自洽。
- `independent_review` 含 reviewer_agent / reviewed_head / result(=PENDING，本报告即其闭环) / report_path。

### V-3 disposition 与实时状态一致性 — 关闭（PASS）

- **worktree 注册**：`git worktree list` = 22 条（主仓 + 21），与 JSON keep 集合（22 条，含主仓 ACTIVE_KEEP）**逐路径精确相等**，无多余、无缺失。`git worktree prune --dry-run` 零条目。
- **39 个删除项**：逐路径存在性检查，38 个已不存在；唯一残留 `AppData/Local/Temp/rf-merge-review-20260927` 仅剩 `.pytest_cache`（访问 Permission denied），已不在注册表——与 JSON cleanup.paths 的 PARTIAL 收据（ACL 拒绝、takeown 亦拒、需提权会话）及 handoff.md §6 完全一致。
- **19 个分支**：逐一 `git rev-parse` + `git merge-base --is-ancestor <branch> main`，全部存在且全部 NON-ANCESTOR（19/19）。分支名集合与 JSON branch 处置名单**精确相等**。evidence 中可核对的 tip 均一致：d00/deploy-root/b31 同 tip `c1e27877`（evidence "same tip as d00/b31" ✓）、du5 残差 `e2f6afd0`（subject "docs: finalize handoff verdict and receipt hygiene" ✓）、b37-release 基线 `28d646d3` ✓。
- **全仓分支计数声明**：本地分支实测 84 个，其中非 main 祖先恰好 19 个——canon 区"本地分支 84（其中 19 个非 main 祖先）"精确成立。
- **REACHABLE 判定复核**：fc-* 系列 9 个 detached HEAD SHA（26bdfb27 / 1b41d62f / 9315ddf3 / 4750fecd / 387e6ac5 / 91cbc137 / 58db9486 / 4a4c1089 / a9f1ff18）逐一 `merge-base --is-ancestor` 验证，全部 REACHABLE from main，与 evidence 判定一致。dashboard-owner-rf-* 三个 UNREACHABLE tip（1db861f1 / c1e27877 / 11e0a2a7）确为 main 不可达（对应分支保留、工作树保留，判定自洽）。
- **保留项 dirty 证据实存**：`rf-period-evidence-20261010/artifacts/registry/publications.jsonl`（35,450B）与 `rf-source-ref-v2-integration-20261003/.../publications.jsonl`（3,830B）均存在；w07 `.planning/w07-rf-model-quality/`（5 个未跟踪条目）、w08 `.planning/w08-rf-combinations/`、r1-targets `.planning/r1w05/` 均实测为 untracked 附件——5 个 Temp/harness/r1-targets 的 EVIDENCE_KEEP 理由成立。
- **主仓 6 组 untracked**：与 `git status` 实测逐一相符，dirty_exceptions 6 项一一对应。
- **MERGED 组复核**：canon 区声称的 du6/du8/du67/du11/r1 系/w14/w16 分支（du6-rf-targets、du8-rf-comparison、root-du67、root-du8、w14-rf-clean-chain、w16-rf-basis、r1-w09、r1-targets、r1-narrative-availability、r1-source-boundary、r1-local-budget-observation）逐一验证均为 main 祖先（11/11）；du11 `d578da58`、MB-RF `bf314bfb`、W20 `3e8fbc55` 均实测 main 祖先。
- **facade 引用**：`tests/test_rf_job_facade.py:7` 注释引用 `.planning/rf-job-facade-01/evidence/`（分支保留路径），与"tests 唯一命中为注释"声明一致；facade canon 行引用的 release HEAD `e4b38459` 实测为 facade 分支祖先且在分支 handoff.md 中存在。

### V-4 吸收证据真实性抽查 — 关闭（du5 PASS；facade 发现 R-1；w04 见 OBS-1）

- **du5**：`git diff main codex/du5-rf-units-20261015 -- docs/plans/du5-units-2026-10-15/handoff.json` 输出为空（两侧相同）；`git cat-file -s` 两侧 `receipts/registry-incident.json` 均 **6919 字节**，与 evidence"byte-equal (6919B)"精确一致。ABSORBED 判定成立。
- **facade**：作者声明"main ff1c69e0 blob identical for rf_job_facade.py"。实测：`git show codex/rf-job-facade-01:scripts/rf_job_facade.py | sha1` = `d518cd06`，`git show ff1c69e0:... | sha1` = `a53490b4`，**不相等**；blob `c83ca89b`(分支,1442 行) vs `dba52967`(ff1c69e0,1451 行)，差异恰为 9 行 `source_reader_command` 校验/传参块（ff1c69e0 多出）；main 后又经 `cd24976a` 演进。→ **R-1（建议推送前修正表述，非阻断）**：分支版本是 ff1c69e0 版本的真子集（1442/1451 行全部相同、仅少 9 行 main 后加块），"代码已被 main 重落地"的方向与结论不变；且该 evidence 支撑的处置是 ACTIVE_KEEP（分支+工作树均保留，无可逆损失），并线决策仍被 D4-06 + facade handoff §8-3 + `pytest -k rf_job` 回归门控。live 工作树 clean、文件=分支 blob（实测）。
- **w04**：指定代理检查 `git diff codex/w04-... codex/w04-...^ -- SKILL.md references/research-coverage.md` 两方向均 **0 行**——tip 提交 `b7fe04aa`（54 文件，742+/56-）根本未触碰这两个文件，故"73/73 dirty 新增行存在于 main"的逐行收据在删除后**无法从 git 对象独立复验**（dirty diff 未提交、工作树已删）。可复核部分：evidence 所记 `docs/w04_research_authoring_card.md` SHA1 `36421d54` 与 main 实测 hash `36421d540635fa8d89501f66943ab0a6ba45b52f` 精确一致（自洽）；分支 tip 的 research-coverage.md 与 main 零差异、SKILL.md 仅 15 行分支侧独有（该内容在保留的分支 ref 中，无损失）。→ OBS-1（信息级）：该收据仅存在于 disposition evidence + cleanup.paths note（"dirty verified absorbed (73/73 lines in main)"）两处文档记录，属删除动作的固有不可复验风险，已在收据中文书记载。

### V-5 状态对齐注记复核 — 关闭（PASS）

- `bf314bfb`、`3e8fbc55`（及 `d578da58`）均实测 main 祖先（`merge-base --is-ancestor` exit 0）。
- PLANNING_STATUS.md 顶部 canon 区就位：RF Planning Canonical 状态入口声明 + 快照 + 关闭收据对齐表 + 活动计划 + 跨 owner 等待项 + 未来主线计划 + dirty exceptions + 「历史区」分界，历史内容完整保留于下方。
- 5 处回链逐一存在且相对路径解析正确：根 `task_plan.md` / `progress.md` / `findings.md`（→ `PLANNING_STATUS.md`，同层）；`docs/plans/mb11-rf-2026-11-11/task_plan.md` / `docs/plans/w20-rf-adoption-2026-10-28/task_plan.md`（→ `../../../PLANNING_STATUS.md`，上溯 3 层=根）。mb11 注记写明"MERGED：bf314bfb 是 main 祖先，§9 为准、§7 过时"；w20 注记写明"MERGED：3e8fbc55 已是 main 祖先，「待ROOT接收」被并入事实取代"——与实测祖先关系一致。

### V-6 清理边界安全性 — 关闭（PASS）

- 39 个删除路径 + cleanup.paths 全 39 条逐一规范化比对：**零条目位于 RF 仓目录（`C:/Users/郑曾波/Projects/revenue-forecast/`）之内**；`revenue-forecast-*` 删除项均为兄弟目录（非子路径），RF 仓自身未删任何内容。
- RFAudit 9 目录（revenue-forecast-audit 及 8 个变体）实测全部存在；不出现在任何 disposition/cleanup 条目中——"RFAudit owner 所有、本卡不清理"成立。
- 删除集合无含唯一 untracked 内容者：39 项 evidence 全部为 "REACHABLE+clean"、"damaged shell + untracked 空"、"absorbed"（w04/du5 见 V-4）或 "duplicate of main tip"（rf-impl，HEAD=ec5ba004=主仓 tip）；唯一 dirty 项 w04 的吸收证据已按 V-4 记录（收据在案、事后不可独立复验，属固有风险而非违规）。
- 生产面配置引用：对 4 个删除路径样本（rf-merge-review-20260927 / revenue-forecast-du5-units / revenue-forecast-w20-adoption / _harness_worktrees / rf-narrative-consumer）grep `scripts tools config tests .github references` **零命中**。

### V-7 handoff.md 叙述与 JSON 数字一致性 — 关闭（基本一致，3 项小误差见 R-2/R-3/R-4）

- 61→22 注册 worktree ✓（实测）；9779.6 MB 预删 = cleanup.paths 逐路径 mb 之和（精确 9779.6）✓；571,331 文件预删 = 逐路径 files 之和 ✓；实释放 569,766 文件 = 571,331 − 1,565（保留孤儿目录 files）✓；"38 完整 + 1 部分" ✓（JSON 收据 35×OK|remove + 3×OK|remove-force + 1×PARTIAL）。
- `cleanup.bytes=10218934272` = 9745.5 MiB = **9.517 GiB ≈ "约 9.52 GB"** ✓（叙述 GB 值与 bytes 精确吻合）；叙述 MB 值 "≈9746.6"系由逐路径四舍五入值推导（9779.6−33.0），与 bytes 换算差 1.1 MB（R-4，信息级）。

### V-8 status 用词评估 — 关闭（PASS，含两处争议项定论）

- **争议 (a)：39 个 worktree + 12 个 projects_dir 的 DELETE_AFTER_OWNER_CONFIRMATION** —— 卡定义四要件逐项满足：lane 收据在 main（各项 evidence 给出 main 内收据路径，抽查 w14/w16/du6/du8/r1 系/w20 全部实测成立）或为 REACHABLE 残壳/重复检出；无唯一内容（untracked 空或已证吸收）；无 dirty 唯一工作（唯一 dirty 项 w04 有在案收据）；无配置引用（V-6 grep 零命中）；分支 ref 全部保留（19/19 SHA 未动实测）。owner=RF 依卡授权按收据自行结案，用词正确。
- **争议 (b)：rf-merge-review-20260927** —— 实际结果"注册已清 + 目录因 ACL 保留"与 disposition 状态 DELETE_AFTER_OWNER_CONFIRMATION 的关系：该 disposition 描述的是已决定的处置（删），同文件 cleanup.paths 以 PARTIAL 收据如实记录执行结果（"deregistered, directory retained / orphan dir left in Temp pending elevated session"），handoff.md §6 亦有叙述——**不需要更改 status 用词**；但该 disposition 条目自身未交叉注记 PARTIAL 结果、且孤儿目录的待提权删除未列入 remaining_items（→ R-5，建议补强，非阻断）。
- ABSORBED 2 项：du5 证据实测成立（V-4）；revenue-source-reader 的依据实测成立（main `docs/plans/mb11-rf-2026-11-11/card_audit.md` A0-5 "原型不建第二 reader | NO_CHANGE_PROVEN" 在案；main 存在 `company_wiki_source_v2.py` / `company_wiki_source_reader_v2.py`）。
- EVIDENCE_KEEP 34 / ACTIVE_KEEP 7：抽查全部成立（运行台账 2 份实存、w07/w08/r1-targets 未跟踪草稿实存且"未被 main 取代"表述如实、facade/input-prep 为唯一检出且等 D4-06、dashboard 系 15 分支收据在分支树内不跨仓结案、b37-release 为施工包基线）。

## 3. 发现与建议清单

| 编号 | 严重度 | 内容 | 关闭状态 |
|---|---|---|---|
| R-1 | MEDIUM（建议推送前修正，非阻断） | handoff.json:166 facade evidence "main ff1c69e0 blob identical for rf_job_facade.py" 严格不成立：分支版 1442 行 = ff1c69e0 版 1451 行减去 9 行 `source_reader_command` 块（blob c83ca89b vs dba52967；live 工作树同测）。建议改为"分支版完全包含于 main ff1c69e0 版（后者多 9 行 source_reader_command 块；main 后经 cd24976a 演进）"。不影响本卡任何处置（该项为 ACTIVE_KEEP，无可逆动作），并线决策仍被 D4-06 + §8-3 + 回归门控 | 建议（可随后续 docs-only 修正提交或推送前 amend，reviewer 复核一行） |
| R-2 | LOW | "61→22（= 主仓 + **20** 个保留集合成员）"（handoff.md §6 与 JSON tests[3] 同文）差一：实际为主仓 + **21**（19 EVIDENCE + 2 ACTIVE 非主仓 worktree）；总数 22 本身正确且实测 | 建议 |
| R-3 | LOW | handoff.md §6 "remove 34 + --force 4" 拆分与 JSON 收据（35 remove + 3 remove-force）不符；总数 38 一致。建议以后者为准 | 建议 |
| R-4 | INFO | 叙述 "≈9746.6 MB" 与 cleanup.bytes 换算 9745.5 MiB 差 1.1 MB（逐路径四舍五入推导所致）；"约 9.52 GB"与 bytes 精确一致。可不改 | 信息 |
| R-5 | LOW | Temp 孤儿 `rf-merge-review-20260927`（已注销注册、ACL 待提权删除）未列入 remaining_items，且对应 disposition 条目无 PARTIAL 交叉注记（结果仅记载于同文件 cleanup.paths 与 handoff.md §6）。建议 remaining_items 增补第 4 项 | 建议 |
| OBS-1 | INFO | w04 "73/73 dirty 行存在于 main" 收据在删除后不可从 git 对象独立复验（tip 提交未触碰 SKILL.md/research-coverage.md，指定代理检查零行）；可复核的卡文档 SHA1 36421d54 与 main 实测一致。属删除动作固有风险，收据已在 disposition evidence + cleanup.paths note 双处记载 | 信息（无需动作） |

**无必须修复项（none blocking）。**

## 4. 审查覆盖度说明

- 已核对：候选提交全部 8 文件 diff；JSON 全部 94 项 disposition 字段完整性；22/22 保留 worktree 逐路径与注册表比对；39/39 删除路径存在性；19/19 分支存在性 + 非祖先判定 + 可核对 tip/subject；9/9 detached-HEAD REACHABLE 判定；84 本地分支/19 非祖先计数声明；11 个 MERGED 组分支祖先判定；3 个对齐注记 SHA 祖先判定；5/5 回链解析；6 组 untracked 与 dirty_exceptions 比对；du5/facade/w04 三组吸收证据；RFAudit 9 目录；生产面配置引用 grep；清理数字全量复算。
- 不可复核（已在正文注明）：已被删除工作树中未提交 dirty 内容（w04 73 行）的逐行收据、已删残壳的 "untracked 为空" 声明——仅收据在案。

## 5. 最终结论

**PASS** —— 候选提交 `a7a1818a12f5226fe6eb1190cf373fbdf02ddc0d`（base `ec5ba0044b3252d2fc58c4a50c2fe9bc234cf5ad`）通过独立审查：改动纯文档、交接物 schema 完整、94 项处置与实时状态精确一致、清理边界安全（RF 仓与 RFAudit 零触碰）、对齐注记与吸收证据可核实。R-1（facade "blob identical" 表述）建议作者在推送前以后续 docs-only 提交修正表述，reviewer 将对该单点复核；R-2/R-3/R-5 为可合并入同一修正提交的低危建议；均不阻断推送流程。

（审查绑定：本报告绑定 HEAD a7a1818a；若作者按 §8 流程修正后产生新候选 HEAD，需对本报告 R-1/R-2/R-3/R-5 单点复核后重出结论。）
