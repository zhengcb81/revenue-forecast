## ROOT主线接收完成 — 2026-10-16

本施工包及ROOT共因修复已正常并入主线 `033f396279aeb9980f57dbefff85b69007fcb478`，作者完整历史保留。正式工程验收和原失败见root-reception.md/json及zip。

相关技能已定点同步，实际SHA一致；不是整套替换。

ROOT随后正常推送并核对精确远端HEAD/CI；状态归总于CWP母PWF。

**Next Step：** 本包STOP；后续由ROOT接生产共享引擎、正式摘要和母E2E，不重新开启作者施工。

---

## ROOT接收更新 — 2026-10-16

ROOT接收工程验收通过，待正常提交/并线/远端/定点同步。独审复现并修复：季度typed builder误走旧年化分支；默认/显式unmodeled的比较值误造；typed range声明缺单位期间；旧金额乘除次序改变strict边界。保留默认未建模原值与unknown，不造FX。新6项和3新模型6次实际CLI通过；最终集中199PASS+119subtests/20.16s。中途196PASS/3FAIL来自本次作者3条新测试把默认unmodeled当benchmark，已保存原断言zip与失败，让调用显式请求benchmark（不改旧validator/金标），默认未建模反例继续保持。作者193+119/五模型10CLI原收据保留。0供应商，Temp恢复，主仓alert WIP/output不触碰。真实公司、母E2E和CWP生产接线不因本组件绿关闭。

**Next Step：** 正常提交并主线、可用远端发布和相关技能文件定点同步，由ROOT归总母PWF。

---

# 调查

施工卡的静态发现不等于已复现RED；由A节点核实。原失败/未知/分母保留；只更新自己的PWF。

## A 节点核实结果（2026-10-16，基线 5122107b + PWF 种子 75a7fb0c）

用真实入口（`run_forecast` / `research.target_measurement.normalize_target_bounds` /
`research.input_targets.build_management_target`）逐条复现，探针脚本在 `.du6-tmp/probe1.py`
（临时目录，交付前删除）。基线回归（卡内 8 个旧测试文件）：152 passed + 61 subtests。

### 已复现的真缺陷（经济/语义行为 RED）

1. **CNY/RMB 不贯通**：`normalize_target_bounds` 用 `target["raw_currency"] == data["currency"]`
   直接比字符串。`raw_currency="CNY"` + `data["currency"]="RMB"` 被拒
   （`typed target currency mismatch; reconcile first`）。错误来自 `target_measurement.py:40`。
2. **缺 10k/100m 等同义表达**：`_SCALES` 只有 `unit/units/thousand/million/billion/trillion/万元/亿元/亿`。
   `raw_scale="万"`（HKD 72500 万）与 `raw_scale="百万"` 被拒
   （`typed target scale is unsupported`）。`亿` 反而能过，词汇表内部就不一致。
3. **负增长不能进入流程**：`targets.py:311`（`require(raw_value >= 0, ...)`）与
   `targets.py:298`（区间下界 `low_number >= 0`）、`input_targets.py:146/139` 一律非负。
   负同比目标在 typed validator 之前就被拒
   （`management target cannot be negative: five_year_revenue_goal`）。
4. **负目标容差方向反转**：`_meets` 的 `at_least` 用 `low*(1-tolerance)`。`low=-0.10`、`t=0.01`
   得 `-0.099`，把可接受的 `o=-0.0995` 判为不达标（应放宽到 `-0.101`）。`at_most` 同理反向。
5. **attainment_ratio 对负目标颠倒好坏**：`observed/low`。`o=-0.20`、`low=-0.10` 得 `2.0`
   （200% 兑现），实际是比目标更差的下滑。
6. **operator×range 无合同**：`_meets` 在 `low != high` 时一律 `low <= observed <= high`，
   完全忽略比较词。`at_least`/`at_most`/`greater_than`/`less_than` 配双边区间的经济含义
   无法不加猜测地定义（单边阈值 vs 两个端点）。

### 假说中未复现 / 判定为有意行为，不改

- 金额非负要求：普通收入金额目标的 `raw_value >= 0` 是合理约束，保留。负值仅对
  `metric_kind == "year_over_year_growth"` 放开。
- 裸 `万元`/`wan`/`亿`/`百万` 作为 `input_unit` 仍报 unknown：DU5 冻结的「无币种不猜」，
  本卡不动（`tests/test_du5_money_unit_registry.py::UnknownSpellingTests` 钉死）。
- `base_period=None` 的同比目标已经是具名原因（`base_period_unknown` / `missing_base_period`），
  本次只补测试钉住，不改语义。
- 区间 `approximately` 的成员判定是既有 `/1` 冻结行为（`tests/test_target_measurement_comparison.py::test_quarter_band_*`），
  保持 `L <= o <= H`，不按容差外扩、不造中点。

### 接口 RED（新构造器尚不存在，单列，不冒充经济行为 RED）

- `research.input_quantities.money_currency / money_scale_factor / same_money_currency`
  未定义（`ImportError`）。
- `build_management_target(..., comparison_spec=...)` 未定义（`TypeError: unexpected keyword argument`）。

### RED 收据

- `docs/plans/du6-targets-2026-10-16/receipts/red-run.txt`：32 failed / 18 passed / 24 subtests passed
  （18 通过项全部是「旧正确行为必须保持」的对照断言）。
- 夹具 SHA（运行前记录，B/C 结束后核对不变）：
  - `tests/test_du6_target_measurement_boundaries.py` = `419b078127ca7d746ca9c1c9687c656d10e46326ebf09ad5fbc57a9ad4db2a1b`
  - `tests/fixtures/du6_targets/hand_computed_expectations.json` = `476f2d8dd3466140b33de7700ca4967a1721446bca95a5e96d194786d7898870`
- 默认 registry `artifacts/registry/publications.jsonl`：**不存在**（运行前）；结束后必须仍不存在。
- 临时目录 `C:/Users/郑曾波/Projects/revenue-forecast-du6-targets/.du6-tmp` 由本线创建，结束删除。

## B/C 后的 RED 复核：断言未被削弱（2026-10-16）

施工卡要求「不修改旧金标洗绿」。为证明新测试没有在实现过程中被削弱，把 4 个源文件
**回退到 HEAD**（实现整体撤掉）后重跑**最终版**测试文件：

- 原始 RED 收据 `receipts/red-run.txt`：32 failed / 18 passed / 24 subtests。
- 回退复跑 `receipts/red-reverify-after-implement.txt`：36 failed / 20 passed / 24 subtests。
- 差集见 `receipts/red_old.txt` 与 `receipts/red_new.txt`：

**仍 RED（31/32，未削弱）**：原 RED 全部条目除下述 1 条外，在无实现的情况下依然失败。

**唯一差异（1 条）——是测试伪影，不是削弱断言**：
`SignedComparisonTruthTableTests::test_strict_comparisons_stay_strict_for_negative_points`
最初 RED 的原因是**测试自身**的浮点噪声（观测值算出来是 `-0.09999999999999998`，
与目标 `-0.10` 不严格相等），并非代码缺陷：`_meets` 的 `greater_than`/`less_than`
在 HEAD 上对**点目标**本来就是严格且与符号无关的（`observed > low` / `observed < low`）。
施工卡 C 节「严格比较保持严格」是**保持项**而非缺陷项，A 节点把它误记为行为 RED。
现已改用精确二进制分数（`-1/8`、`-1/16`、`-1/4`）做严格相等边界，成为一条
**保持断言**：实现前后都必须为真。本条在 `findings.md` 的「未复现/有意行为」中如实更正。

**新增 5 条在 HEAD 上 RED（B 节补充覆盖，绑定本次改动）**：
`test_same_currency_scale_conversion_runs_in_both_directions`（同币反向转换）×2 subcase、
`test_zero_base_revenue_stays_a_nonpositive_base_reason`、
`test_original_scope_quarter_and_schema_rejections_are_preserved`、
`test_default_call_shape_is_unchanged_for_a_positive_amount`（旧缺省调用形状）。

**纯保持断言（HEAD 与实现都通过）**：`test_inverted_range_bounds_are_refused` 等
18+ 条 —— 它们在 RED 收据里就是绿色，是「旧正确行为必须保持」的对照组。

### 夹具 SHA 的如实记录（更正上文「核对不变」措辞）

上文 A 节点记录的 SHA 是 **RED 冻结时点**的快照，B/C 阶段夹具与测试都发生了改动，
因此「核对不变」不成立，措辞过强。实际改动与原因如下（无一条 RED 断言被放松）：

| 文件 | RED 时点 SHA | 最终 SHA | 改动与原因 |
|---|---|---|---|
| `tests/fixtures/du6_targets/hand_computed_expectations.json` | `476f2d8d…` | 见 `receipts/fixture-shas.txt` | ① 手算笔误更正：`cny_wanyuan_to_rmb_100m.expected` 由 `0.5` 改 `5.0`（该条 `formula` 写的是 `50000 * 1e4 / 1e8`，正确值就是 5.0；实现未改，是夹具手算写错，由独立手算试读抓出）；② 新增 `cny_100m_to_rmb_wanyuan_reverse`（同币反向转换手算） |
| `tests/test_du6_target_measurement_boundaries.py` | `419b0781…` | 见 `receipts/fixture-shas.txt` | 全部是**测试脚手架修正 + 新增覆盖**，不含断言放松：claim 的 `target_id`/`unit` 对齐、`comparison_value` 由测试手填（不经被测代码）、情景档位改造以满足引擎 low≤base≤hs 排序、`assertEqual`→`approx`（`0.9-1` 在浮点下不等于 `-0.1`）、严格边界改精确二进制分数、B 节新增 4 个测试 |

`references/money-unit-conversion.md`（白名单外）未改动；其 scale 词汇表未列 DU6 新增的
`trillion`/`万亿` 与目标词汇 `万元`/`亿元`/`units`，需 ROOT 做一处最小文档补充，
已写入 `handoff.json` 的 `root_integration_steps`。
