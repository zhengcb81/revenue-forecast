# 进度

ROOT仅建立已提交基线的独占工作树/启动计划；尚未实施、未跑业务测试；0API，未复制原件、AUTO、密钥或主仓WIP。

## 2026-10-16 A 节点：done

- 基线确认：`codex/du6-rf-targets-20261016` @ `75a7fb0c`（源码基线 `5122107b` + PWF 种子）。
- 基线回归（卡列 8 个旧文件）：152 passed + 61 subtests。
- 接口表/真值表/单位角色/手算期望写入 `INTERFACES.md`（DU6 作者段）。
- 新测试 `tests/test_du6_target_measurement_boundaries.py` + 夹具
  `tests/fixtures/du6_targets/hand_computed_expectations.json`。
- RED 收据 `receipts/red-run.txt`：32 failed / 18 passed / 24 subtests。
  18 个通过项全是「旧正确行为必须保持」的对照断言（金额非负、DU5 裸量不猜、
  正目标容差位一致、区间 approximately 成员判定等）。
- 接口 RED 单列（`money_currency`/`money_scale_factor`/`same_money_currency`、
  `build_management_target(comparison_spec=...)` 尚不存在），未冒充经济行为 RED。

## 2026-10-16 B 节点：done

- `research/input_quantities.py`：并入有限别名（trillion/万亿、万元、亿元、units）到
  **同一张** Currency×Scale 表，导出 `money_currency` / `money_scale_factor` /
  `same_money_currency`。既有转换字典条目、家族划分、DU5 sensitivity 责任不变，
  裸 `万元`/`wan`/`亿`/`百万` 仍 unknown。
- `research/target_measurement.py`：删除私有 `_SCALES`，改用共享查询；CNY/RMB 同币贯通；
  新 `acceptance_bound` / `meets_target` / `attainment_ratio`；具名诊断
  `typed_comparison_operator_range_incompatible`；负点目标补显式
  `reason="attainment_ratio_withheld_nonpositive_target"`。
- `research/targets.py`：typed 增长目标放行带符号 raw（金额仍非负）；非 typed 达标判断
  与 attainment_ratio 改用共享语义（正目标与旧式 `v*(1±t)` 逐位一致）。
- `research/input_targets.py`：新增 `comparison_spec` / `normalization_rationale`；
  与 `conversion` 互斥（具名诊断 `typed_comparison_spec_conflicts_with_conversion`）；
  旧缺省调用形状不变。
- `references/management-targets.md`：新增单位、带符号增长、比较合同、attainment_ratio 四节。
- 集中回归（卡列命令）：**193 passed + 119 subtests**（基线 152+61 全保留）。
- 相邻回归（golden_behavior_lock / output_report / data_contract / management_operation_clock /
  native_research_bindings / m3_period_flow_consumers / research_evidence_roles）：
  125 passed + 1 skipped，金标未刷新。
- Ruff 仅改动文件：All checks passed。

## 2026-10-16 C 节点：done（待独立审查后收尾）

- 5 份合成模型（HKD 万缩放正金额、CNY 亿元同币正金额、负同比、跨零区间、
  run-rate/CC 无转换具名 gap）全部走 `builder → run_forecast →
  validate_published_forecast → 公开 CLI --validate-only / --output / --markdown`，
  exit 0；负控 4 项（跨币、金额负值、operator×range、错误 unit family）exit 2 具名拒。
- registry 隔离：`REVENUE_PUBLICATION_REGISTRY=.du6-tmp/registry.jsonl`（5 条正式发布），
  仓库默认 `artifacts/registry/publications.jsonl` 全程**不存在**。
- 独立手算试读 51 项全过（`receipts/independent-quality-check.json`）；不导入被测代码。
- 0 供应商 / LLM / 外部网络；未读取密钥；无生产写入。
