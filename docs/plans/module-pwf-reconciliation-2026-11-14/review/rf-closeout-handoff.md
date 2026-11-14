# RF-PLAN-WORKTREE-CLOSEOUT Handoff

- 日期：2026-11-14
- Owner 卡：company-wiki `docs/plans/module-pwf-reconciliation-2026-11-14/owner_cards/rf_closeout.md`（只读对照）
- 仓库：`C:\Users\郑曾波\Projects\revenue-forecast`（本卡唯一写入仓）
- 落点说明：卡规定唯一写入仓为 revenue-forecast 且不得改 CWP/company-wiki；故固定交付路径 `docs/plans/module-pwf-reconciliation-2026-11-14/review/` 在 **RF 仓内**创建（company-wiki 侧同名目录已存在且属 ROOT，未触碰）。

## 1. Canonical PWF

根 `PLANNING_STATUS.md` 已固定为 RF 唯一 canonical 状态入口：顶部新增 canon 区（快照 / 关闭收据对齐 / 活动计划 / 跨 owner 等待项 / 未来主线计划 / dirty exceptions），全部历史内容保留于下方历史区。根 `task_plan.md`、`progress.md`、`findings.md`、`docs/plans/mb11-rf-2026-11-11/task_plan.md`、`docs/plans/w20-rf-adoption-2026-10-28/task_plan.md` 五处已加回链与状态对齐注记。未新建 START_HERE。

## 2. 基线与最终状态

| 项 | 值 |
|---|---|
| base | `main` @ `ec5ba0044b3252d2fc58c4a50c2fe9bc234cf5ad` = `origin/main`（开工实测，与卡快照一致） |
| final branch | `main` |
| final HEAD | 本文件所在候选提交（工作树变更全部为文档；精确 SHA 由独立 review 报告绑定记录；base `ec5ba004` 无代码改动） |
| remote | https://github.com/zhengcb81/revenue-forecast.git |
| remote_head | `ec5ba004`（开工基线，即 base；候选通过审查后推送，届时远端 = base + 本候选链） |

## 3. 状态冲突对齐

- MB-RF：task_plan 与 handoff §7/§9 的"未合入/已合入"冲突 → 以 §9 为准（`codex/mb11-rf` bf314bfb 是 main 祖先；ROOT 并线 origin/main=6b045b76 在 main 历史）。已在 mb11 task_plan 加注。
- W20："COMPLETE 待ROOT接收" vs 分支已并入 → `codex/w20-rf-adoption-20261028`（3e8fbc55）是 main 祖先，收据 `delivery/w20-rf-adoption/handoff.json` 在 main；已加注取代"待接收"。
- DU11 root reception task_plan 第 4 点 "IN PROGRESS" 为当时 push 收尾，已被 main 推进取代（d578da58 是 main 祖先）。
- 先前所报 `revenue_report.py` / `test_output_report.py` / `input-schema.md` dirty 已被 `ec5ba004` 吸收，未重复登记。

## 4. 逐项账目与处置

完整逐项处置见本仓 review 包同目录 `rf-closeout-handoff.json`（`dispositions` 数组，schema_version=1）；此处摘要：

- **19 个非 main 祖先分支**：ACTIVE_KEEP 2（rf-job-facade-01、rf-input-prep-01——D4-06 后并线）、ABSORBED 2（du5、revenue-source-reader）、ACTIVE_KEEP 1（dashboard-rf-b37-release——施工包基线）、EVIDENCE_KEEP 14（dashboard 系 lane 收据在分支树内、ROOT 接收未执行，不跨仓结案）。
- **61 个注册 worktree**：主仓 ACTIVE_KEEP；39 个 DELETE_AFTER_OWNER_CONFIRMATION（lane 收据在 main + clean 或 dirty 已证吸收 + 无唯一内容/运行状态/配置引用）；**19 个 EVIDENCE_KEEP**（运行登记/未结案 lane/草稿不确定/位于 Dashboard 树内待协调）；2 个 ACTIVE_KEEP（facade、input-prep）。39+19+2+1=61。
- **14 个 Projects RF core 候选目录**：主仓保留；12 个随 worktree 删除；r1-targets EVIDENCE_KEEP（.planning/r1w05 中间运行日志）；其余 6 个 RF 顶层目录与 3 个 dashboard-owner-rf-* 目录随 worktree 处置。9 个 `revenue-forecast-audit*` 目录（约 773MB）属 RFAudit owner，原样保留。

### 4.1 关键吸收证据（删除项抽样）

- w04-research-authoring worktree（dirty 122 行）：`git diff` 新增行 73/73 逐行存在于 main 的 SKILL.md/research-coverage.md；`docs/w04_research_authoring_card.md` 与 main 字节等价（SHA1 36421d54）；HANDOFF.md 内容等价（仅换行差异）。
- du5 分支（ahead=1）：唯一残差 e2f6afd0 为 docs 收尾；`handoff.json` 与 `receipts/registry-incident.json`（6919B）同 main 字节等价；main 的 progress.md 含更超前的"ROOT接收收尾 — 2026-10-16"记录。
- Temp 残损壳（rf-merge-review / rf-narrative-consumer / rfv2-tdd）：tracked 大面积 D（壳损伤）、untracked 为空，分支已并入或已被 P5-RF source-v2 取代。
- 配置引用：`git grep` 生产面（scripts/tools/config/references/.github/tests）对 39 删除路径与 19 分支名零活引用；tests 唯一命中为注释（指向仓内分支路径，非被删路径）。

## 5. 未提交例外（dirty exceptions）

- 主仓 6 组 untracked：`.mimosa/`、`.planning/m8-native-adoption-20261031/`、`.planning/source-quote-adoption-20261030/`、`delivery/dashboard-b34-wuxi-20261101/`、`delivery/dashboard-b37-wuxi-20261102/`、`output/` — EVIDENCE_KEEP，与 MB-RF handoff §9/§10 口径一致，原样保留。
- 保留 worktree 的 dirty 逐项登记于 JSON `dirty_exceptions`。

## 6. 清理收据

- 候删 39 个：**38 个完整删除**（`git worktree remove` 35 + `--force` 3），1 个部分完成。
- 部分完成：`AppData/Local/Temp/rf-merge-review-20260927` — `--force` 已清除注册但目录删除被 `.pytest_cache` 的 Windows ACL 拒绝（`takeown` 亦拒绝，需提权会话）；孤儿目录（33MB，残壳）留在 Temp，登记为保留例外。逐路径结果见 JSON `cleanup.paths`。
- 空间收据：39 路径预删实测合计 **9779.6 MB / 571,331 文件**；实际释放 **10218934272 bytes ≈ 9745.5 MiB（约 9.52 GB）/ 569,766 文件**（扣除保留孤儿目录）。逐路径 MB/文件数见 JSON `cleanup.paths`。
- worktree 注册数：**61 → 22**（= 主仓 + 21 个保留集合成员，逐项与处置表一致）；19 个分支引用全部未删、SHA 与开工快照逐一相同。

## 7. 测试与检查

本卡改动范围：PLANNING_STATUS.md + 5 个 PWF 文件头注记 + 本 review 包 3 个文件，**纯文档**。按卡执行文档-only 检查：

| 检查 | 命令 | 结果 |
|---|---|---|
| JSON 可解析 | `python -I -c "import json;json.load(open(...,encoding='utf-8'))"` | PASS（94 项 disposition，覆盖 61 worktree + 19 分支 + 14 Projects 候选，零缺漏） |
| 链接有效 | 5 处回链相对路径逐一解析 | PASS（5/5 OK；canon 区标题就位） |
| git diff --check | `git diff --check`（工作树变更，空白错误） | PASS（提交前实测无输出） |
| worktree 一致性 | `git worktree list` 计数 + prune | PASS（61 → 22，保留集合逐一匹配） |
| 分支无损 | 19 refs SHA 与开工 TSV 对照 | PASS（19/19 一致） |

不涉及代码改动，故未运行 pytest 回归（卡：纯文档改动做 PWF/JSON/link/`git diff --check`）。

## 8. 独立审查

- reviewer agent：独立 reviewer agent（general-purpose，未参与实施）
- 审查绑定 HEAD：`a7a1818a12f5226fe6eb1190cf373fbdf02ddc0d` 全量审查 PASS（V-1~V-8）；修正提交按报告 §3 对 R-1/R-2/R-3/R-5 单点复核，记录于报告 §6
- 结论：PASS（无必须修复项；R-1..R-5 建议已在本修正提交落实）
- 报告：`docs/plans/module-pwf-reconciliation-2026-11-14/review/rf-closeout-review.md`
- 流程：作者提交候选 HEAD `a7a1818a` → 独立 reviewer 全量审查（PASS，5 项非阻断建议）→ 作者修正提交（本提交）→ reviewer 单点复核 → 推送并确认远端含已审树（修正提交与 bookkeeping 提交仅含审查记录与建议修正，遵循 MB-RF handoff §5 先例：审查绑定内容提交，文档提交随后）。

## 9. 剩余项与唯一下一步

- 剩余项：
  1. D4-06（ROOT 组合验收）未关闭 → facade/input-prep 并线与 Dashboard 系 15 分支的"ROOT 接收"均为跨 owner 等待项，已登记于 PLANNING_STATUS canon 区。
  2. 21 个保留 worktree（EVIDENCE/ACTIVE）与其 dirty 附件原样保留，待各自 lane 结案后由后续卡处置。
  3. Temp 两个含 publications.jsonl 的残损壳（rf-period-evidence、rf-source-ref-v2）保留运行登记；若 ROOT 认可登记无审计价值可另行删除。
  4. Temp 孤儿目录 `rf-merge-review-20260927`：worktree 注册已清，目录因 `.pytest_cache` ACL 拒绝（takeown 亦拒，需提权会话）保留，待提权会话删除。
- 唯一下一步：等待 D4-06 关闭后由 RF owner 按 facade handoff §8-3 决策 `git merge codex/rf-job-facade-01`（并线后回归 `pytest tests/ -q -k rf_job`）。
