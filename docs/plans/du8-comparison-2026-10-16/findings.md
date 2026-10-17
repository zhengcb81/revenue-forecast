# 调查（A节点，作者实测）

基线 HEAD `e86488a701ee8a107b432749e85003b9d115d407`（源码基线 `0feea9b0` + ROOT PWF 种子）。
所有数字均由本工区实跑 `python -X utf8 -B` 得到，探针脚本 `tools/du8_probe_*.py`、`tools/du8_scan.py` 为临时
诊断件，B节点结束前删除，不入交付。

## 1. 责任分化（实读代码，行号为基线）

同一个"比较是否达标"的经济判断在仓内存在**三份**实现：

| 位置 | 表达式 | 用途 |
|---|---|---|
| `scripts/research/target_measurement.py:113` | `math.isclose(observed, low, rel_tol=t, abs_tol=max(abs(low), 1e-12) * t)` | typed owner（DU6 冻结） |
| `scripts/research/targets.py:769-774` | `math.isclose(observed, tv, rel_tol=t, abs_tol=max(1.0, abs(tv)) * t)` | legacy 生产端 |
| `scripts/revenue_report.py:1039-1044` | `math.isclose(observed, tv, rel_tol=t, abs_tol=max(1.0, abs(tv)) * t)` | legacy 报告校验端 |

`at_least`/`at_most` 同样三份：owner 用 `acceptance_bound()`（`target_measurement.py:85-94`，负目标向外放宽），
report 在 `revenue_report.py:1034-1037` 内联重算 `v*(1∓t)`（负目标会向内收窄，方向相反）。
`attainment_ratio` 的零/负/区间规则在 owner（`target_measurement.py:116-126`）与 report
（`revenue_report.py:1016-1018`，仅 `target_value == 0`）各写一份。

## 2. 分叉可达且已在输出中可见（RED）

`tools/du8_probe_reachable.py` 用**现有公开 fixture**（`test_management_targets.add_target`
+ `test_recognition_bridge.forecast_document`）构造 legacy 目标，令
`target_value=0.5`、`comparison="approximately"`、`comparison_tolerance=0.01`，
把三情景收入同比例缩到 observed=0.4905：

```
modeled_value              0.4905
target_value               0.5
emitted meets_target       true          <- 引擎输出并写入快照
owner meets_target         false         <- 唯一 owner 的判定
owner  abs band            [0.495, 0.505]
report abs band            [0.490, 0.510]
```

`tools/du8_scan.py` 量化分叉区间：target 0.5 时有 99 个 1e-4 网格点不一致；
target 0.0 时 200 个；负目标（report 只接受非负点目标，typed 允许负增长）在
`at_least`/`at_most` 上数百点不一致。**这不是浮点尾差**：0.4905 相对 0.5 差 1.9%，
远超任何 ulp，是两套公式的实质口径差。

`tools/du8_probe_report.py` 证明 report 对这个分叉**完全无感**：
`validate_published_forecast(재seal 后的 result, data)` 直接通过，因为 report 重算的是
与生产端相同的第二份公式。也就是说，"报告独立校验"目前在 legacy 路径上退化为
"两个同函数结果互比"，正是施工卡 §4 明令不得作为独立性的形态。

## 3. 打字/旧分支靠 `is_typed_target` 分流，且旧分支无 owner 校验

`revenue_report.py:952-955` 对 typed 目标做 `comparisons == compare_target_measurement(...)`（委托），
`revenue_report.py:956-1048` 对 legacy 目标内联重算 5 个字段。
`research/targets.py:728-731` 同样形状。报告校验一旦与 owner 分叉，typed 目标跟随 owner、
legacy 目标跟随自带副本，两条路径的未来修改必然漂移。

## 4. 已冻结、本卡不得更改的兼容事实

- typed `management-target-comparison/1` 的数值语义（DU6 交接白名单外无法收敛）；
- legacy 三套 scenario 键集 `{measurement_basis, measurement_periods, modeled_period_values,
  modeled_value, target_value, attainment_ratio, meets_target}`（`test_target_measurement_comparison.py:138-139` 锁定）；
- schema 3.1/3.2/3.3/BOUND 的历史输出形状（`test_management_targets.py:210-265` 锁定）；
- `0.8`/旧 schema 默认语义、CNY/RMB 别名、万亿缩放、无 FX 不跨币。

## 5. 结论与更窄方案

责任缺口真实存在，但**不是**可以随手统一数值的 bug：legacy 的
`max(1.0, |v|)*t` 与 typed 的 `max(|v|,1e-12)*t` 都是有意的历史口径。
因此本卡的收敛目标是**责任唯一**：把 legacy 的乘除次序、键集与默认值原样搬进一个
owner 内的显式兼容路径，让 `targets.py`、`revenue_report.py` 都只调用它，
并保留 legacy 数值不变（old gold / old wire 不动）。

## 6. 实施后的独立对抗复核（两轮，全部修复）

两轮独立审查在首次实现 commit 上核对了上述判断，并确认：发布数字与形状相对基线
**逐字节相同**（9 个模型全等、whole-body sha16 一致、schema 3.1/3.2/3.3/3.7–3.10
全等）；A 节点 RED 可在基线独立复现；反篡改独立且比基线更强。

同时发现的真实缺陷（均已在最终 commit 修复）：

1. **静态 guard 可绕过**（高）。把 report 的 legacy 委托整体替换为本地带宽重算，
   只要 typed 分支仍保留 `compare_target_measurement` 符号，旧 guard 全绿。
   现已改为语义 guard：每个比较分支都必须断言 owner 返回值，且禁止任何本地带宽；
   该攻击已复现为失败用例（`receipts/guard-attack-check.txt`，exit 1）。
   **这条纠正了本文档先前"guard 非空转"的说法过于乐观。**
2. `typed_level_model` 未设 `comparison_basis`，标称 typed 实走 legacy 路径（高）。
   已修复并由 `test_typed_and_legacy_models_really_take_different_paths` 断言。
3. `handoff.json` 的 `implementation_commits` 曾填入**不存在的 SHA**，且声称 ruff
   exit 0 而其收据为 exit 1（高）。均为作者自查时发现并修正。
4. 两处白名单外改动（`references/target-measurement-comparison.md`、
   `tests/du8_models.py`）已还原/移入 `tests/fixtures/du8_comparison/`。
5. 缺 ownership 语义测试、缺成功路径 sentinel 测试，均已补。

## 7. 仍保留的有意差异（非缺陷）

- legacy 与 typed 的 `approximately` 带宽在 `|v| < 1` 及负点目标上不同；
- legacy `at_least`/`at_most` 对负目标向零收窄；
- 报告输入绑定的 `rel_tol=1e-9, abs_tol=1e-9` 身份带宽是既有的，非比较容差。
