# W16 独立审查 S1：写入范围 + B08 硬编码（只读静态审查）

- 审查对象：`revenue-forecast-w16-basis` 工区，`094d55ad..84e2152f`（w16: optional revenue basis metadata for historical observations）
- 审查方式：`git diff` / `grep` 静态检查，未改任何仓库文件、未改 git 状态、未联网
- 审查人角色：S1，未参与 W16 实现
- 日期：2026-10-25

## 结论

两项全部 PASS，finding 数：0。

## 项 1：写入范围 — PASS

命令：`git -C 工区 diff 094d55ad..84e2152f --stat`（先按任务要求跑了 `--stat -- scripts tests`）。

`-- scripts tests` 输出 7 个文件、+1389/-24：

```
scripts/contracts/document.py       |  44 +--
scripts/generate_input_template.py  |  12 +
scripts/lint_input.py               |  16 ++
scripts/research/revenue_basis.py   | 535 ++++
scripts/revenue_report.py           | 130 +++-
tests/test_w16_revenue_basis.py     | 415 ++++
tests/test_w16_revenue_basis_cli.py | 261 ++++
```

全量 diff（不限路径）共 15 个文件，逐一对照允许清单：

| 路径 | 清单匹配 |
|---|---|
| docs/plans/w16-rf-basis-2026-10-25/{COMMON,INPUTS,START_HERE,construction_card,findings,handoff.template,progress,task_plan}（8 个） | docs/plans/w16-rf-basis-2026-10-25/** |
| scripts/research/revenue_basis.py | scripts/revenue/** |
| scripts/contracts/document.py | 精确列出 |
| scripts/revenue_report.py | 精确列出 |
| scripts/lint_input.py | 精确列出 |
| scripts/generate_input_template.py | 精确列出 |
| tests/test_w16_revenue_basis.py、tests/test_w16_revenue_basis_cli.py | tests/test_w16_* |

- 越界文件：无。`scripts/schema_fields.py` 与 `delivery/w16/**` 在允许清单内但本 diff 未改动（允许≠必须）。
- 工作区状态干净（仅未跟踪的 `delivery/w16/`，即本报告所在目录）。

## 项 2：B08 硬编码 — PASS

方法：取 diff 中 scripts 的全部新增行（`grep '^+'`，共 718 行）存为工区外临时文件后逐模式 grep，tests 新增行同样处理；查毕已删临时文件。

模式清单逐一计数（scripts 新增行）：药明 0 / 安踏 0 / 中芯 0 / ATU 23 / Testing 0 / 603259 0 / 688981 0 / 2020 0 / page.?235 0 / 45,456 0 / 2,035 0 / 特判 0；tests 新增行全部为 0。

23 处 `ATU`（大小写不敏感，含 `atu` 子串）逐行核验与去重抽样（第 29/101/422/667/710 行等）均为 `statement_status`、`STATEMENT_STATUSES`、`STATEMENT_LABELS`、`(status, reason)` 等标识符内子串，非公司代码 ATU —— 全部为误报，且均属通用口径字段（as_reported/restated），与具体公司无关。

纵深加固扫（超出任务清单的自愿项，均为 0）：
- 无分隔数字：`45456|2035` → 0
- 英文名/其他代码：`wuxi|anta\b|smic|01813|02020|HK` → 0
- 页码逻辑：`\bpage\b|页码|页 ?[0-9]` → 0
- 特判标记：`特|公司名|硬编码` → 0

结构核验：新模块 `scripts/revenue_basis.py` 自述为 B08 唯一规则所有者，`contracts/document.py` 仅改为 import 并委托（`parse_revenue_basis` / `validate_basis_against_document` / `require_total_operations_for_base` / `validate_historical_claim_alignment`），未见任何按公司/页码/数值分支的 `if` 逻辑；对无 `revenue_basis` 记录保留原行为。

## Findings

无。两项均 PASS，未发现 S1-x finding。
