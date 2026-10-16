# DU6-RF-TARGET-MEASURES 交接

`schema_version=du6-handoff/1`；机器可读版见 `handoff.json`。

- 分支 `codex/du6-rf-targets-20261016`，源码基线 `5122107bbc86c3d1e79886b372700c05d19bb349`，
  PWF 种子 `75a7fb0c`，**实现提交 `62c90520624c8cea00c565e300a5d441f0f05803`**。
- 本线未并主线、未推安装副本、未改 CI/配置/凭证/生产原件；`production_writes=0`、`supplier_calls=0`。

## 做了什么

把管理层目标的**单位、带符号增长与比较语义**收敛到共用责任层：

1. **一张货币/规模表**（`research/input_quantities.py`）：DU5 的 Currency×Scale 描述同时承载
   目标层词汇（`trillion`/`万亿`、`万元`、`亿元`、`units`），并导出
   `money_currency` / `money_scale_factor` / `same_money_currency`。
   `target_measurement.py` 的私有 `_SCALES` 删除。CNY≡RMB 贯通；HKD/USD/RMB 无 FX 仍拒；
   无币种裸量仍不猜。DU5 既有转换字典与 sensitivity 责任逐条保留（129 组旧 record 重推导通过）。
2. **带符号增长**：`metric_kind="year_over_year_growth"` 允许负 raw 单值/跨零区间下界，
   按原百分比进入同一流程；`level_multiple=0.9` 就是 −10%。普通收入金额的非负要求原样保留。
   「下降 10%」永远不会被写成 +10%。
3. **比较合同**（真值表见 `INTERFACES.md` §5）：容差带一律 `|目标|` 宽度、向零外放宽，
   目标负号不反转哪边算缺口；严格比较不加容差。正/零目标的 `at_least`/`at_most` 仍用
   原式 `v*(1±t)`，**逐位一致**。区间两端保留、不造中点；只有 `approximately` 配区间有
   无歧义含义，其余 operator×range 给具名诊断 `typed_comparison_operator_range_incompatible`。
4. **attainment_ratio**：只对正点目标给；负目标（会把「跌更多」显示成 200% 兑现）、零目标、
   区间一律 None，且负点目标的可比行补显式
   `reason="attainment_ratio_withheld_nonpositive_target"`。`modeled_value`/`meets_target`/
   `difference_percentage_points`/`derived_revenue_benchmark` 一律照算，不用 null 抹掉观测值。
5. **typed 构建**：`build_management_target(..., comparison_spec=, normalization_rationale=)`
   直接产出 `comparison_basis` 与 `comparison_value`，消费者不再手工 patch 目标字典；
   与 `conversion` 互斥（具名诊断）。旧缺省调用逐字节不变。

## 证据

| 项 | 结果 | 收据 |
|---|---|---|
| 首个行为 RED | 32 failed / 18 passed / 24 subtests（18 绿全是「旧正确行为必须保持」对照组） | `receipts/red-run.txt` |
| 实现后回退复核 | 源码回退 HEAD 重跑最终版测试：36 failed / 20 passed；原 32 条 RED 中 **31 条仍 RED**，无断言削弱 | `receipts/red-reverify-after-implement.txt`、`red_old.txt`、`red_new.txt` |
| 集中回归（卡列命令） | **193 passed + 119 subtests**，exit 0（基线 152+61 全保留） | `receipts/central-regression-final.txt` |
| 相邻面加固 | 117 passed + 1 skipped（含 golden_behavior_lock，**金标未刷新**） | `receipts/adjacent-regression.txt` |
| 公开 CLI 端到端 | 5 合成模型 `--validate-only` 与 `--output`/`--markdown` 全 exit 0；4 负控全 exit 2 具名拒 | `receipts/c-receipt.json` |
| 独立手算试读 | 51 项全过（不导入被测代码） | `receipts/independent-quality-check.json` |
| 清理 | 自建 `.du6-tmp` 已删；默认 registry 全程不存在；夹具 SHA 与记录一致 | `receipts/cleanup-receipt.json`、`receipts/fixture-shas.txt` |

C 节点 5 份合成模型：HKD 万→百万同币缩放正金额（72500 万 = 725 百万）、CNY 亿元 on RMB 同币、
负同比 −10%（builder 产出、无手工 patch）、跨零区间 [−10%, +5%]、run-rate/CC 无支持转换
（**保持具名 gap**：`management_target:cc_run_rate_gap: unmodeled_data_gap (...)`，未填假数字）。
负控：跨币、金额负值、operator×range、错误 unit family —— 真实退出码均为 2，stderr 带具名诊断。

## 如实说明（不是全部通过）

- **夹具 SHA 并非全程不变**。RED 时点记录的 SHA 之后发生了改动，原因逐条列在 `findings.md`：
  ① 夹具手算笔误更正（`cny_wanyuan_to_rmb_100m.expected` 0.5→5.0，公式 `50000*1e4/1e8` 本就是 5.0）；
  ② 测试脚手架修正（claim 对齐、comparison_value 由测试手填、情景档位、浮点精确化）+ B 节新增 4 测试。
  **没有一条 RED 断言被放松**（回退复核为证）。原文「核对不变」措辞过强，已在 findings 更正。
- **`test_strict_comparisons_stay_strict_for_negative_points` 不是修复项而是保持项**。
  A 节点把它记为行为 RED 是错的：`greater_than`/`less_than` 在 HEAD 上对点目标本就严格，
  原 RED 由测试自身的浮点噪声造成。现已改为精确二进制分数的严格边界保持断言。
- **独立手算的独立性是分层的**：`raw`/`statement`/`comparison_value`/区间两端是绝对手算锚定；
  但 pp 差、derived benchmark、区间成员的期望值由已发布 JSON 的 `modeled_value`/`base_value`
  反推，属公式级独立。若 `modeled_value` 自洽而错，这项抓不到。
- **单测 + 合成 E2E 通过 ≠ 全部公司预测通过**。本次 0 真实公司、0 供应商、0 外部网络；
  未跑全仓回归、未做真实预测质量评估。

## 剩余 / 交给 ROOT

1. `references/money-unit-conversion.md`（本线白名单外）的 scale 词汇表需补 `trillion`/`万亿`
   并注明 `万元`/`亿元`/`units` 是目标层合法拼写 —— 一处最小文档补充。
2. 非 typed 的 `approximately` 用 `abs_tol=max(1.0,|v|)*t`、typed 用 `max(|v|,1e-12)*t`：
   历史两个口径，`revenue_report.py`（只读）对非 typed 独立重算用前者，统一需 ROOT 协调。
3. `operator×range` 只定义了 `approximately`；如业务确需 `at_least [L,H]` 之类表达，
   需先有可引用的口径定义再扩合同。`comparison_spec` 与 `conversion` 互斥，
   「季度 typed + 证据化年化转换」组合未覆盖，需要时另开卡。

无需新增人工签收 JSON / private-public / 授权文件。本线 STOP 等 ROOT 验收。
