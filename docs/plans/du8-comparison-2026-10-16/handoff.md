# DU8-RF-COMPARISON 交接

- 卡片：`du8-comparison-2026-10-16`
- 分支：`codex/du8-rf-comparison-20261016`
- 源码基线：`e86488a701ee8a107b432749e85003b9d115d407`
- 实现 commit：`4fcdbb5ca8a9ebd3d69708ec4427a64801abd1f2`（首次实现）、
  `03f35e918540c4b8bc0d2730417b412012632ece`（审查后修复）、
  `7f286d811d5cd80f1f7e4339a0961671b125428a`（交接文档）、
  `67b15a60eda6894162523f64fa5e02a619106f07`（**最终冻结**，还原白名单外文档）
- 状态：**实现、审查修复与测试完成，工作树干净，STOP，等待 ROOT 独立验收/并线/同步技能**

## 0. 两轮独立对抗审查及其修复（必读）

本卡在冻结前接受了两轮独立审查，findings 全部修复并留证：

| 审查发现 | 严重度 | 修复 |
|---|---|---|
| 静态 guard 可用"保留 typed 分支 owner 符号、重写 legacy 分支"绕过 | 高 | guard 改为语义检查：每个比较分支都必须断言 owner 返回值，并禁止任何本地带宽；攻击已复现为失败用例，见 `receipts/guard-attack-check.txt`（exit 1） |
| `typed_level_model` 未设 `comparison_basis`，标称 typed 实走 legacy 路径 | 高 | 补 `comparison_basis` + `normalization_rationale`，并新增 `test_typed_and_legacy_models_really_take_different_paths` 断言分支归属 |
| 交接文件未提交、`implementation_commits` 为不存在的 SHA | 高 | 全部提交；SHA 改为真实值（本文件头部） |
| `handoff.json` 声称 ruff exit 0 而其收据为 exit 1 | 高 | 删除未用 import，ruff 真实通过，`receipts/c-gates.txt` 为真实输出 |
| `cleanup_receipt` 指向不存在的文件 | 中 | 已创建 `receipts/cleanup.txt` |
| 白名单外改动 `references/target-measurement-comparison.md` | 中 | 已 `git checkout` 还原，该文件零改动 |
| 白名单外新增 `tests/du8_models.py` | 中 | 移入白名单内的 `tests/fixtures/du8_comparison/models.py` |
| 缺 ownership 语义测试 | 中 | 新增 `constrained_model`（sum_cap 使 effective ≠ recognized）与两项断言，证明 owner 读约束调整后路径 |
| 仅测失败路径 sentinel，未测成功路径 | 中 | 新增成功路径 sentinel 测试（用 registry 自身 append 写入链有效记录） |
| `b-regression-focused.txt` 未覆盖 DU8 套件 | 中 | 已重跑，487 passed 含全部 DU8 套件 |

**审查同时独立确认**（对抗验证结论）：发布数字与形状相对基线**逐字节相同**
（9 个模型全等、whole-body sha16 一致、schema 3.1/3.2/3.3/3.7–3.10 全等）；
A 节点 RED 在基线可独立复现；反篡改确实独立且比基线更强；兼容面全部保持。

## 1. 已查明的根因

"某情景是否达标"的判断在基线里存在**三份**实现：

| 位置（基线行号） | 表达式 |
|---|---|
| `scripts/research/target_measurement.py:113` | `isclose(obs, low, rel_tol=t, abs_tol=max(abs(low), 1e-12) * t)` |
| `scripts/research/targets.py:769-774` | `isclose(obs, tv, rel_tol=t, abs_tol=max(1.0, abs(tv)) * t)` |
| `scripts/revenue_report.py:1039-1044` | `isclose(obs, tv, rel_tol=t, abs_tol=max(1.0, abs(tv)) * t)` |

`at_least`/`at_most` 同样三份（owner 用 `acceptance_bound`，report 在 1034-1037 内联
`v*(1∓t)`，方向对负目标相反）；`attainment_ratio` 的零/负/区间规则在
`target_measurement.py:116-126` 与 `revenue_report.py:1016-1018` 各写一份。

后果：report 的 legacy 分支重算的是**与生产端相同的第二份公式**，因此它对两套口径的
分叉完全无感，"报告独立校验"在该路径上退化为"两个同函数结果互比"。

## 2. 可复现反例（A 节点 RED）

用仓内现有 synthetic fixture（`test_management_targets.add_target` +
`test_recognition_bridge.forecast_document`）构造 legacy 目标：
`target_value=0.5`、`comparison="approximately"`、`comparison_tolerance=0.01`，
三情景收入同比例缩到 observed=0.4905。基线行为：

```
legacy/report 带宽   [0.490, 0.510]     -> meets_target = true   （写入快照）
typed owner 带宽     [0.495, 0.505]     -> meets_target = false
report 校验          通过（重算同一份 legacy 公式，看不见分歧）
```

差异 1.9%，远超任何浮点尾差。网格扫描：target 0.5 有 99 个 1e-4 网格点不一致；
target 0.0 有 200 个；负目标在 `at_least`/`at_most` 上数百点不一致。
该反例现由 `tests/fixtures/du8_comparison/hand_anchors.py::DIVERGENCE_CASE`
与 `tests/test_du8_hand_anchors.py::test_the_two_paths_disagree_exactly_where_the_anchors_say` 冻结。

## 3. 职责/接口变化

**新增唯一 owner** `scripts/research/target_comparison.py`：

```python
LEGACY_COMPARISON_ROW_KEYS       # 7 键（3.2+）
LEGACY_COMPARISON_ROW_KEYS_31    # 4 键（schema 3.1）

legacy_acceptance_bound(value, tolerance, *, lower) -> float
legacy_target_ratio(observed, target_value) -> float | None
legacy_meets_target(observed, target_value, comparison, tolerance) -> bool
legacy_comparison_row(*, observed, target_value, measurement_basis,
                      measurement_periods, period_values, comparison,
                      tolerance, schema_version="3.2") -> dict
legacy_comparison_tolerance(target) -> float
compare_legacy_target_measurement(target, result, *, periods=None) -> dict
is_modeled_comparison(target) -> bool
compare_target_measurement(target, result, parameters=None, *, periods=None) -> dict
```

`compare_target_measurement` 是统一入口：`is_typed_target(target)` 为真走
`research.target_measurement`（DU6 冻结，原样委托），否则走 legacy 路径。
分支只由**声明形状**决定；typed 目标传 `periods` 覆盖会被拒绝而非静默丢弃。

**删掉的重复计算分支**：

- `scripts/research/targets.py::add_management_target_analysis` 中 732-790 行的
  legacy 内联比较（含 769-774 的 `isclose`、763-767 的 `meets_target` 调用、
  779-789 的行拼装与 `attainment_ratio` 调用）整段删除，改为一次
  `compare_target_measurement` 调用。
- `scripts/revenue_report.py` 中原 1016-1048 行的 `expected_ratio` 计算、
  `expected_meets` 的三分支内联重算与 `comparison_op`/`tolerance_val` 读取整段删除。

报告侧**保留**的部分：从输出自己的收入路径 + 目标声明期间重建每期值，逐字段
断言 `modeled_value`/`target_value`/行键集/期间/期间值，**然后**才与 owner 判定比对。
这是刻意保留的独立输入绑定，不是重复计算。

## 4. 现行为兼容矩阵

| 面 | 状态 |
|---|---|
| legacy 行键集（3.2+） | 7 键不变，`set(...) ==` 精确校验 |
| legacy 行键集（schema 3.1） | 4 键不变 |
| typed `management-target-comparison/1` | 行键集与全部数值语义 = DU6 原样 |
| legacy `approximately` abs_tol | `max(1.0, |v|)*t` 逐字 |
| legacy `at_least`/`at_most` | `v*(1∓t)` 逐字（负目标向零收窄，保持） |
| legacy `attainment_ratio` | 仅 `v == 0` 置 null |
| typed 数值语义 | `max(|v|,1e-12)*t`、符号安全 `acceptance_bound`、严格比较、双端区间不取中点 |
| unmodeled / out_of_horizon | `scenario_comparison = {}`，不伪造 `comparison_value` |
| quarterly 原生桥 | 季度求和，不乘四 |
| CNY/RMB 同币、万亿缩放、无 FX 不跨币 | 由 DU5/DU6 层承担，未触碰 |
| 0.8 / 旧 schema 默认语义 | 未触碰 |
| old gold / old wire | 未刷新 |

## 5. 实际运行命令

```text
# 新单元/锚点/往返套件（108 passed, 6 skipped）
python -X utf8 -B -m pytest tests/test_du8_target_comparison_owner.py \
  tests/test_du8_hand_anchors.py tests/test_du8_target_report_roundtrip.py -q

# B 节点集中回归（487 passed, 7 skipped，含全部 DU8 套件）
python -X utf8 -B -m pytest tests/test_management_targets.py \
  tests/test_target_measurement_comparison.py tests/test_management_target_semantics.py \
  tests/test_independent_targets.py tests/test_structure_targets.py \
  tests/test_du6_target_measurement_boundaries.py tests/test_du67_typed_builder_composition.py \
  tests/test_output_report.py tests/test_data_contract.py tests/test_golden_behavior_lock.py \
  tests/test_single_owner_guard.py tests/test_architecture_dependency_uses.py \
  tests/test_du8_target_comparison_owner.py tests/test_du8_hand_anchors.py \
  tests/test_du8_target_report_roundtrip.py tests/test_du5_money_unit_registry.py \
  tests/test_du5_root_unit_boundaries.py tests/test_input_quantity_conversion.py \
  tests/test_evidence_input_lineage.py tests/test_contract_registry.py \
  tests/test_schema_compatibility.py tests/test_scenarios_confidence.py \
  tests/test_growth_driver_tree.py tests/test_lint_input.py tests/test_publication_pipeline.py \
  tests/test_revenue_constraints.py -q

# 门禁
python -X utf8 -B -m ruff check scripts tests tools
python -X utf8 -B -m mypy scripts/contracts/ scripts/schema_compatibility.py \
  scripts/filing_fetch_client.py scripts/trust_anchor.py
python -X utf8 -B tools/host_assumption_guard.py --roots tests tools scripts
```

## 6. 数字/单位手工锚点（≥5，均用 `decimal`，不 import 生产比较模块）

`tests/fixtures/du8_comparison/hand_anchors.py`：

| 锚点 | 算式 | 期望 |
|---|---|---|
| `legacy_approximately_abs_tol_small_target` | `max(1, 0.5) * 0.01` | `0.01` |
| `legacy_approximately_abs_tol_large_target` | `max(1, 144) * 0.01` | `1.44` |
| `legacy_at_least_bound_144` | `144 * (1 - 0.01)` | `142.56` |
| `legacy_at_most_bound_144` | `144 * (1 + 0.01)` | `145.44` |
| `legacy_attainment_ratio_4905_over_500` | `0.4905 / 0.5` | `0.981` |
| `typed_approximately_abs_tol_half` | `max(0.5, 1e-12) * 0.01` | `0.005` |
| `typed_approximately_abs_tol_large` | `max(144, 1e-12) * 0.01` | `1.44` |
| `typed_at_least_negative_widens_down` | `-0.10 - 0.01 * |{-0.10}|` | `-0.101` |
| `typed_at_most_negative_widens_up` | `-0.10 + 0.01 * |{-0.10}|` | `-0.099` |

锚点文件 `tests/fixtures/du8_comparison/hand_anchors.py` 只 import `decimal`，
不 import 任何生产比较模块；由 `tests/test_du8_hand_anchors.py` 逐项对 owner 断言。

## 7. 反篡改证据

**行为冻结的独立复核**：`receipts/behaviour-freeze-recheck.txt` 用一个不依赖本卡
fixture 的独立脚本，在 `e86488a7` 的临时 worktree 与当前树上跑同一组 synthetic 模型
（legacy annual / legacy approximately / legacy cumulative / typed level），
比较 `management_target_coverage` 与**整个结果体**（排除 `result_sha256`）的 sha256。
结果：**DIFFERENCES: NONE**，两个 sha 逐模型完全相同
（如 legacy_annual `body_sha abac1dfc2256f3aa` 在两树一致）。该 worktree 已删除。

`tests/test_du8_target_comparison_owner.py::LegacyAntiTamperTests` 与
`tests/test_du8_target_report_roundtrip.py`（参数化到全部 7 个合成模型）对
`modeled_value`、`target_value`（区间目标改 `target_low`）、`attainment_ratio`、
`meets_target`、`measurement_periods`、`measurement_basis`、`modeled_period_values`
逐项篡改并重新封 `result_sha256`，全部被
`validate_forecast_output` / `validate_published_forecast` 拒绝。
另覆盖：伪造 scenario 键、删除行内字段、legacy 行冒充 typed 行。

**独立性说明**：报告校验不是"调同一函数再比同函数"。它先独立重建期间值并与发布行
逐字段比对（输入绑定），再与 owner 判定比对。篡改 `modeled_value` 会先在绑定阶段
被拒，与 owner 是否被调用无关。独立对抗审查另测了三种洗白尝试
（缩小声明窗口、改 `measurement_basis`、连同收入路径一起改写并重封 hash），
全部被拒。

**结构 guard 的反绕过证据（两次攻击）**：

- `receipts/guard-attack-check.txt`：把 report 的 legacy 委托整体替换为本地带宽重算
  （避开旧 guard 的字面量），旧 guard 全绿（19 passed），新 guard **exit 1 捕获**。
- `receipts/guard-attack-2-producer.txt`：把 `targets.py` 生产端的 owner 委托改成
  返回空字典，**11 个测试失败**（含行为测试），证明生产端不止靠静态 guard 兜底。

两次攻击均在临时副本/可还原写入上执行，事后 `git diff HEAD` 为空，证实已还原。

## 8. NOT_RUN / 不跑范围

- **无真实公司、无付费、0 供应商调用、0 翻译、0 HTTP、0 生产写入。**
- 全部模型为 synthetic，来自仓内既有测试 fixture。**scope 输出明示合成，不宣称
  买方模型质量通过。**
- 未跑：真实 filing/来源升级后的端到端（属 ROOT 的 CWP/ET 接线）；
  未跑兄弟仓 FF/AUDIT 的联调；未安装技能；未推远端。
- 白名单外**未改**：`scripts/contracts/`、builder (`input_targets.py`)、forecast 引擎、
  CLI 入口、旧测试/gold、config、assurance/output/registry、CI、安装副本。
- 环境限制造成的既有失败（基线与实现**逐字相同**，见 receipts）：
  `tests/test_rf_coverage_report.py`、`tests/test_ca306_terminal_closure.py`、
  `tests/test_zr1001_release_readiness.py`、`tests/test_zr1009_legacy_removal.py`
  因缺 `uc` 模块无法收集；`tests/test_zr709_zijin_journey.py::test_j1_*` 因缺
  filing-fetch 兄弟仓失败。这些**非本卡引入**，已用 stash 对照验证。

## 9. 清理

所有测试运行写入 pytest `tmp_path`；CLI 子进程通过
`REVENUE_PUBLICATION_REGISTRY` 指向临时目录，未触碰真实 registry。
sentinel 用 `scripts/publication_registry.py` 自身的 append 写入**链有效**记录
（手写行会被正确判为 tampered），成功与失败两条路径均断言：
预存字节保留、每行仍可解析、仓根不产生 registry 文件。
A 节点临时探针 `tools/du8_probe_*.py`、`tools/du8_scan.py`、
`tools/du8_guard_attack_check.py`、`tools/du8_attack_debug.py`
均在交付前删除，未入 commit；攻击复现结论保存在
`receipts/guard-attack-check.txt`。

## 10. ROOT 如何接收

1. `git log` 确认最终 commit `67b15a60eda6894162523f64fa5e02a619106f07`
   与 `handoff.json.implementation_commits` 对齐；`git status` 应为空。
2. 跑 §5 的集中回归命令复现 487 passed。
3. 独立验收建议重点：用 `git diff <base> <final>` 确认白名单外零改动；
   用 §2 的反例在基线上复核 RED 真实存在；重放
   `receipts/guard-attack-check.txt` 的攻击确认 guard 仍能捕获。
4. 本卡不等待来源升级：ROOT 可在 CWP 新原文摘要交付后继续调用相同 RF 公开接口
   （`scripts/revenue_forecast.py`），无需本卡再次改动。
