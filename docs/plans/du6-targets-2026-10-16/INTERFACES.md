# DU6 接口、隔离和交接

这是工程分工说明，不是许可链。用户既有处理授权继续有效；本轮三卡离线，0供应商调用，不创建 authorization/canary/人工签收。

## 启动与文件所有权

1. 只在总表指定的独立工作目录启动，读本卡副本、task_plan 和本文件。核对实际 branch、base 和状态。不要在主仓或旧 DU5 工作树施工，不重置解释不清的修改。
2. 每条线只能改自己的卡列出的精确白名单及自己的 PWF；不改兄弟仓、CWP、共享总计划、配置/凭证、生产原件、AUTO、registry、CI 或安装目录。需要白名单外接口时提交具体反例和建议给 ROOT，继续能独立做的部分。
3. ROOT 接收前冻结 RF 目标计量清单、AUDIT 新 importer 范围、FF 两个矩阵工具源文件。任何外部改动先核对，不自动覆盖。
4. 自己源码的 import 必须指向本工作树，禁止全局 editable install。测试使用当前仓 runner，不另造测试平台。日常快测，B/C 集中回归和真实 CLI；不每 commit 全仓跑。
5. CodeGraph 用于结构调查；无索引按 AGENTS 处理。已点名文件可以直接读，不能因索引缺失宣称代码不存在。

## 冻结边界

- RF：原 normalize_target_bounds、compare_target_measurement 结果形状、builder 缺省语义及历史 typed 合同。新 signed 目标必须由明确 typed 输入进入，原文不改；同币缩放和跨币 FX 分开。无证据的 CC/净额/季度桥不猜。
- AUDIT：已发布 NarrativeBundle /2、/3 和 EvidenceSpan，转换到现 summary-review-map/1；每条 claim、support/context 和原语言不改。只给 bundle 时不得冒认全文召回；完整性不足给范围和 unknown。原 reader/packet/attach/compare 复用，不新语义评分器。
- FF：audit(report, *, evidence_root=None) 默认兼容，replay 只重定位既有相对 artifact，实际 SHA/CaseSpec/原 findings 和未知 usage 保留。不得因搬迁成功升级历史 FAIL；不新 pack 格式、第二 oracle 或持久证据库。

## 测试与空间

- 测试输入只读；输出放自己创建的 TemporaryDirectory/tmp_path。进入前记录 sentinel/已存在文件，所有成功/错误/超时路径恢复原样；新输出原先没有则删除。只删除已核绝对路径位于自己的测试根内的目录，不做全备份恢复。
- 所有 formal forecast 的进程内调用和子进程都必须在 import/执行前指向隔离 registry；前后核对默认 registry 是否存在及 SHA，不能删除真实已有 registry。RF alerts/output 不属于本卡。
- 真实/合成样本分列；只读已有公开小样本，不复制 PDF/AUTO。旧失败、原分母、旧 receipt 和原始 SHA 保留。缺少样本写 NOT_RUN，不造 placeholder 通过。
- 只保留首个行为 RED、最终集中结果和 C 节点 CLI/清理收据。优先小 JSON 汇总及压缩原日志，交接材料目标≤10MiB；不因压缩删失败、裁正文或改原日志。不要打印环境变量和 key。
- FF 真实41链只能用 launch 中固定 CWP/ET 已提交源码依赖。它是离线 fixture 联调，不是实际供应商触达/新鲜原件质量验证。

## 三个大节点与交付

A：读真实代码与 PWF，冻结接口和独立手算/字段期望，先用实际入口复现行为错误。import error 不能作为唯一 RED；区分静态假说和已复现问题。

B：在所属责任层消除共因，集中跑自己的测试和卡列旧回归；不得通过删旧断言、公司特判、扩大预算或复制第二实现洗绿。

C：跑卡内实际公开 CLI、错误路径与恢复；独立质量试读/手算，正常 commit 后写 handoff.md/json，STOP 等 ROOT。作者不并主线、不推安装副本；ROOT 负责合流、精确 CI 与最终跨仓质量。

handoff.json 最少字段：

```json
{"schema_version":"du6-handoff/1","card_id":"DU6-...","base_commit":"full40sha","branch":"codex/...","implementation_commits":[],"changed_paths":[],"interfaces_reused":[],"entrypoints":[],"red_receipts":[],"tests":[{"command":"...","exit_code":0,"passed":0,"failed":0,"skipped":0,"receipt":"relative/path"}],"fixtures":[],"independent_review":[],"old_failures_preserved":true,"known_limits":[],"not_run":[],"root_integration_steps":[],"production_writes":0,"supplier_calls":0,"cleanup_receipt":"relative/path"}
```

production_writes 指生产原件/配置/AUTO/真实 registry；不禁止卡内源码修改。交付 SHA 可由单独 handoff commit 记录前一实现，不自引用。所有真实/合成、缺失/未测和剩余问题照实列出；ROOT 签收是原大节点质量核验，不再添加许可手续。

---

# DU6 作者接口冻结（A 节点，作者写）

以下是本线要实现/复用的接口与比较合同。A 节点先在此冻结签名与真值表，再写 RED。

## 1. 共享金额接口（`research.input_quantities`，唯一单位描述）

DU5 的 Currency×Scale 描述是唯一单位表。DU6 只在该表内**增加有限别名**，并导出目标消费者要用的查询接口；不新建第二张表，不改任何既有转换字典条目、`convert_input_quantity`/`validate_input_quantity_*`/`build_sensitivity_test` 的既有语义。

新增别名（并入 `_MONEY_SCALE_ALIASES` / `_MONEY_SCALE_FACTORS`）：

| 拼写 | 归一化 scale | 因子（货币基本单位） | 来源 |
|---|---|---|---|
| `trillion` / `万亿` | `trillion` | 1e12 | 目标词汇（原 `_SCALES` 有） |
| `万元` | `10k` | 1e4 | 目标词汇（原 `_SCALES` 有） |
| `亿元` | `100m` | 1e8 | 目标词汇（原 `_SCALES` 有） |
| `units` | `unit` | 1 | 目标词汇（原 `_SCALES` 有） |

`10k`/`wan`/`万`、`100m`/`yi`/`亿`、`thousand`/`千`、`million`/`百万`、`billion`/`十亿`、`unit`/`元` 已在 DU5 表内，直接复用（原 `_SCALES` 缺这些同义表达）。

**不改的**：裸 `万元`/`wan`/`亿`/`百万` 作为 `input_unit` 仍是 unknown（无币种不猜）；`units`/`thousand_units`/`million_units` 仍是 count 家族；USD/HKD/RMB 仍互不换算。

新增公开查询接口（供 `target_measurement` 复用，不做第二表）：

```python
research.input_quantities.money_currency(currency) -> str | None
    # "CNY"/"cny"/"RMB" -> "rmb"；"USD" -> "usd"；"HKD" -> "hkd"；未知 -> None

research.input_quantities.money_scale_factor(scale) -> float | None
    # "百万" -> 1e6；"万"/"万元" -> 1e4；"亿"/"亿元" -> 1e8；"trillion" -> 1e12；未知 -> None

research.input_quantities.same_money_currency(a, b) -> bool
    # 两者都能解析且规范化后相等；任一未知 -> False
```

## 2. `normalize_target_bounds` 端口（形状不变）

```python
research.target_measurement.normalize_target_bounds(target, data) -> tuple[float, float]
```

- 金额类：`factor = money_scale_factor(raw_scale) / money_scale_factor(data["unit"])`；要求 `raw_unit == f"{raw_currency} {raw_scale}"`；要求 `same_money_currency(raw_currency, data["currency"])`。
- 增长类（`metric_kind == "year_over_year_growth"`）：按 `raw_ratio_basis` 归一（`percent`→/100，`fraction`→原值，`level_multiple`→−1）。允许负值。
- `low <= high` 仍要求。

## 3. `compare_target_measurement` 端口（`management-target-comparison/1` 行形状冻结）

每 scenario 行保留现有键：`metric_kind/period/unit/modeled_value/target_value/target_low/target_high/comparison/comparison_status/reason/meets_target/attainment_ratio`，同比另有 `base_value/base_period/numerator_value/difference_percentage_points/derived_revenue_benchmark`，金额类另有 `difference`。不加新键、不改 `/1`。

## 4. `build_management_target` 新增可选入参

```python
build_management_target(statement, *, ..., comparison_tolerance=0.01,
                        comparison_spec: dict | None = None) -> {"target","claims","notes"}
```

- `comparison_spec=None`：与旧行为逐字节一致（缺省调用保持）。
- `comparison_spec` 给出时即 typed 比较合同：
  - `{"schema_version": "management-target-comparison/1", "metric_kind": ..., "period": ...}`，可选 `base_period` / `raw_ratio_basis` / `scenario_parameter_ids`。
  - 写入 `target["comparison_basis"]`，并由同一套归一化语义算 `comparison_value`（点目标=归一化值；区间目标=None）。
  - `metric_kind == "year_over_year_growth"` 时允许带符号 raw 单值/区间（**只**对增长比率；金额仍非负）。
  - 与 `conversion` 互斥（两者同时给出给具名诊断 `typed_comparison_spec_conflicts_with_conversion`）。
  - 消费者不再手工 patch target 字典。

## 5. 带符号比较真值表（`_meets` 合同）

记 `o`=观测值，`v`=点目标，`[L,H]`=区间目标（L<H），`t`=`comparison_tolerance ∈ [0,0.25]`。容差带一律用 `|目标|` 做宽度，目标负号**不改变比较方向**；严格比较不加容差。

### 5.1 点目标 `v`（L == H）

| comparison | 判定 | 容差 | 备注 |
|---|---|---|---|
| `at_least` | `o >= v - t*|v|` | 向下放宽 | v>0 与旧式 `v*(1-t)` **完全等价**；v<0 时向更负方向放宽（方向不再反转）；v=0 → `o>=0` |
| `at_most` | `o <= v + t*|v|` | 向上放宽 | v>0 与旧式 `v*(1+t)` 等价；v<0 向上放宽；v=0 → `o<=0` |
| `approximately` | `isclose(o, v, rel_tol=t, abs_tol=max(|v|,1e-12)*t)` | 对称 | 与旧式相同 |
| `greater_than` | `o > v` | 无（严格） | 与旧式相同 |
| `less_than` | `o < v` | 无（严格） | 与旧式相同 |

### 5.2 区间目标 `[L,H]`（L < H，两端都保留，不造中点）

| comparison | 判定 | 备注 |
|---|---|---|
| `approximately` | `L <= o <= H` | 冻结旧 `/1` 行为：区间两端即所述精度，容差不再外扩（t=0 亦然）；跨零区间同样成立 |
| `at_least` | **具名不兼容** | 单边下限对双边区间，下限是 L 还是 H 无法不加猜测地定义 |
| `at_most` | **具名不兼容** | 同上，上限是 L 还是 H 不可无猜测定义 |
| `greater_than` | **具名不兼容** | 严格比较只命名一个阈值，区间命名两个 |
| `less_than` | **具名不兼容** | 同上 |

具名诊断：`ForecastInputError("typed_comparison_operator_range_incompatible: ...")`。

- 目标会进入比较（`modeled_scenario`/`scenario_boundary`/`independent_benchmark`）→ **校验期即拒**。
- 目标只是保留为缺口（`unmodeled_data_gap`/`out_of_horizon`）→ 不拒，但记 `comparison_status="not_comparable"`、`comparison_reason="operator_range_incompatible"`（沿用 `base_period_unknown` 的既有具名原因模式），比较侧同样防御性拒。

### 5.3 `attainment_ratio`

`None if observed is None or low != high or low <= 0 else observed / low`。

- 负目标（`low < 0`）不给比率：`observed/low` 会把「跌得更多」显示成 >100% 的「超额完成」。
- 零目标（`low == 0`）沿用既有 None（除零守卫，行为不变）。
- 区间目标沿用既有 None（不造中点）。
- **不许**用 null 抹掉可比较观测值：`modeled_value`/`meets_target`/`difference_percentage_points`/`difference`/`derived_revenue_benchmark` 一律照算。
- 仅当 `low < 0`（真正新增的 signed 情形）在可比行补 `reason="attainment_ratio_withheld_nonpositive_target"` 作为显式原因；正/零/区间行保持 `/1` 原样，不改旧输出。

## 6. 各数值范围/单位角色

| 角色 | 字段 | 允许 | 禁止 |
|---|---|---|---|
| 金额目标 | `raw_target_value(_low/_high)` | 非负金额 | 负金额（具名拒） |
| 增长比率目标 | 同上 | 带符号（含负） | 由负增长放行负**金额** |
| `raw_unit` | | 必须 `f"{raw_currency} {raw_scale}"` | 模糊货币符号、无币种裸量 |
| `raw_currency` | | USD/RMB/CNY/HKD（CNY≡RMB） | EUR 等未知；HKD↔USD/RMB 无 FX 证据 |
| `raw_scale` | | unit/units/元/thousand/千/10k/wan/万/万元/million/百万/100m/yi/亿/亿元/billion/十亿/trillion/万亿 | share/count 家族拼写（`ratio`/`pp`/`million_units` 等） |
| `data["unit"]` | | 同上 scale 词汇 | 未知 scale |
| `raw_ratio_basis` | | percent/fraction/level_multiple | 缺失 |

## 7. 独立手算期望（写进测试的常数）

1. HKD `万`→`million`：`72500 万 HKD × (1e4/1e6) = 725 百万 HKD`。
2. HKD `亿`→`million`：`7.25 亿 HKD × (1e8/1e6) = 725 百万 HKD`。
3. CNY 目标 + RMB 模型（同币）：`500 亿元 CNY = 500 亿元 RMB`，scale 同为 `亿元` 时 `factor=1`。
4. `level_multiple=0.9` → 归一化增长 `0.9 - 1 = -0.10`；`level_multiple` 区间 `[0.9, 1.05]` → `[-0.10, 0.05]`（跨零）。
5. `percent=-10` → `-0.10`；`percent` 区间 `[-10, 5]` → `[-0.10, 0.05]`。
6. `at_least`、`v=-0.10`、`t=0.01`：下限 `-0.10 - 0.01*0.10 = -0.101`；`o=-0.0995` 判 True（旧式给 `-0.099` 会误判 False）。
7. `at_most`、`v=-0.10`、`t=0.01`：上限 `-0.10 + 0.01*0.10 = -0.099`；`o=-0.0995` 判 True（旧式给 `-0.101` 会误判 False）。
8. 同比 `difference_percentage_points = (o - 目标) * 100`：`o=-0.20`、目标 `-0.10` → `-10.0` pp。
9. `derived_revenue_benchmark = base * (1 + 目标)`：base=200、目标 `-0.10` → 180.0。
10. 负目标 `attainment_ratio is None`；`o=-0.20`、`v=-0.10` 旧式给 2.0（误导）。
