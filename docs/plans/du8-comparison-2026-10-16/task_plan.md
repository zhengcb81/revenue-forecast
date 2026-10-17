# DU8-RF-COMPARISON

状态：**A/B/C 完成，两轮独立对抗审查的 findings 全部修复，源码已冻结，STOP 等待 ROOT 独立验收与并线。**
工作目录`C:/Users/郑曾波/Projects/revenue-forecast-du8-comparison`；分支`codex/du8-rf-comparison-20261016`；
源码基线`0feea9b097747165a37009ad4a7ed5616cf46c38`；冻结源码见 `handoff.json.frozen_source_tree`
（发布数字/形状相对基线逐字节一致，见两份 behaviour-freeze 收据；源码字节并非冻结对象，报告侧校验形状在审查后重塑）。

PLAN_ID：`du8-comparison-2026-10-16`；计划目录为本目录，先读施工卡/INTERFACES/findings/progress，不恢复其他根计划。

## A：调查与真实行为RED

Status: **done**

实读三处比较实现（typed owner / legacy 生产 / legacy 报告校验），独立冻结期望，
证明分叉可达且在已发布输出中可见（legacy 目标 0.5、observed 0.4905 → 引擎
`meets_target=true`，唯一 owner 判 false，报告校验通过）。第一份 RED 存于
`receipts/red-before.txt`。结论见 `findings.md`。

## B：所属层实施与集中回归

Status: **done**

新增唯一 owner `scripts/research/target_comparison.py`；legacy 与 typed 作为显式兼容
路径并存，数值语义不合并。`targets.py`、`revenue_report.py` 删除内联重算改为委托，
报告侧保留独立输入绑定。集中相邻快套件一次：`receipts/b-regression-focused.txt`
（486 passed, 7 skipped），含按施工卡补齐的所有边界族。

## C：公开入口E2E、恢复与交接

Status: **done**

真实 CLI 跑 7 个合成完整模型（legacy annual/approximately/cumulative、constrained、
typed level/growth/quarterly），输出再 validate/render；逐字段篡改全部被拒；
registry/output 全程隔离，成功与失败两路径均断言 sentinel 保留。
`receipts/c-du8-suites.txt`（107 passed, 6 skipped）、`receipts/c-gates.txt`
（ruff/mypy/host guard 全 0）、`receipts/cleanup.txt`、`receipts/guard-attack-check.txt`、
`receipts/guard-attack-2-producer.txt`、`receipts/behaviour-freeze-recheck.txt`。
`handoff.md`/`handoff.json` 齐备且每个 SHA、每个收据路径、每项计数均已核对。

## 独立审查

Status: **done（两轮完成并修复；第三轮独立复核进行中）**

两轮独立审查确认发布数字与形状相对基线逐字节相同、RED 可在基线复现、反篡改独立
且更强；并发现 9 类真实缺陷（guard 可绕过、标称 typed 实走 legacy、交接未提交且
SHA 伪造、虚报 ruff 绿、缺 cleanup 收据、两处白名单外改动、缺 ownership 测试、
缺成功路径 sentinel、回归收据未覆盖 DU8 套件），**全部已修复并留证**，
详见 `handoff.md` 第 0 节。

## Next Step

ROOT 独立验收：核对最终 commit 与 `handoff.json` 对齐、复现 486 passed、
确认白名单外零改动、复核 RED 与两次 guard 攻击收据。本卡不再改动源码。
