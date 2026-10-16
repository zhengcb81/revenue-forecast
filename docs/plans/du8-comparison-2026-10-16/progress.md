# 进度

## A 节点：调查与真实行为 RED —— 完成

- 读施工卡/INTERFACES/仓内源码，实读三处比较实现（typed owner、legacy 生产、legacy 报告校验）。
- 用临时探针证明分叉**可达且已在输出中可见**：legacy 目标 0.5、`approximately`、
  observed 0.4905 → 引擎输出 `meets_target=true`，而唯一 owner 判 false；report 校验通过。
- 第一份行为 RED 保存于 `receipts/red-before.txt`（4 个真实失败）。
- 结论写入 `findings.md`；临时探针已在交付前删除。

## B 节点：所属层实施与集中回归 —— 完成

- 新增唯一 owner `scripts/research/target_comparison.py`；legacy 与 typed 作为两条
  显式兼容路径并存，不合并数值语义。
- `scripts/research/targets.py` 删除 legacy 内联比较；`scripts/revenue_report.py`
  删除 `expected_ratio`/`expected_meets` 内联重算，改为委托 + 保留独立输入绑定。
- 集中相关快套件一次：`receipts/b-regression-focused.txt`（486 passed, 7 skipped）。

## C 节点：公开入口 E2E、恢复与交接 —— 完成

- 用真实 CLI（`scripts/revenue_forecast.py`）跑 7 个合成完整模型
  （legacy annual/approximately/cumulative、constrained、typed level/growth/quarterly），
  输出再 validate/render；逐字段篡改全部被拒。
- registry/output 全程隔离；成功与失败两条路径都断言 sentinel 保留、仓根无写入。
- `receipts/c-du8-suites.txt`（107 passed, 6 skipped）、`receipts/c-gates.txt`
  （ruff/mypy/host guard 全 0）、`receipts/cleanup.txt`。
- handoff.md / handoff.json / receipts/ 齐备。

## 独立审查与修复 —— 完成

两轮独立对抗审查（一个查代码真伪、一个逐条核验收要求）在首次实现 commit 上
发现的问题全部修复并留证：guard 可绕过、标称 typed 实走 legacy、交接未提交且 SHA 伪造、
虚报 ruff 绿、缺 cleanup 收据、两处白名单外改动、缺 ownership 测试、缺成功路径 sentinel。
详见 `handoff.md` 第 0 节与 `receipts/guard-attack-check.txt`。

## 状态

工作树干净，最终 commit `03f35e918540c4b8bc0d2730417b412012632ece`。
0 供应商 / 0 网络 / 0 付费 / 0 生产写入。**STOP，等待 ROOT 独立验收与并线。**
