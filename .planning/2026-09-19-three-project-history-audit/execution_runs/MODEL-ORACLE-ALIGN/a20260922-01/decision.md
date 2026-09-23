# decision.md — MODEL-ORACLE-ALIGN a20260922-01

- 卡：把 RF 模型 **TEST 电池**对齐到 I-10-B defect-1（省缺即抛）语义，然后 **重试 B-6c**
  （解锁 PROMOTION-EXEC STOPPED+REVERTED 的那一行）
- attempt：`a20260922-01` · status：**`review_pending`（不自签；da=unmapped，acc=unproven）**
- `oracle.md` 先冻结（sha256 `146ce313…` / 12543 B，本 attempt 第一个写入），`binding.json` 双 before-pin
  全部实测于首次生产写入之前。

## 权威链（逐层）

1. **OWNER_DECISIONS §十八原话**：「A-1: 1, A-2: 授权, **B: 全批**， C:更新函件」→ **B = 全批** =
   「§十七 B-1..B-7 全部批准」——B-6c 晋升授权早已存在，STOP 不撤销它。
2. **PROMOTION-EXEC decision.md §B-6c**：同电池 promoted = 31 failed / 53 passed（全在
   `model_registry.py:410`），control 前像 = 59 passed rc 0 ⇒ 回归 solely by B-6c；其结语把
   「test battery 对齐 / 替换决策」明确移交给 owner/parent —— **本卡即那次委派的执行**。
3. **产品语义权威**：I-10-B defect-1（T1-22）省缺即抛 = approved product semantics。
   本卡**没有**把 registry 改回 silent-0.0；registry 段只做字节精确的原样重晋升。
4. **E1E7-ERRATA-LANDING DEC-E1E7-4 先例（镜像其效力语言）**：本对齐是调用方显式化，
   **不改变任何现行期望、不改变任何 status、不改变任何资格**；同时登记一个后果 ——
   PROMOTION-EXEC 因 B-6c 未落地而记为 INACTIVE 的 **M05/M14/M20/M24 四份 defaults-相位前瞻披露
   （E1E7 已逐卡落地）随本次 B-6c 成功落地而转为 ACTIVE**；那些卡的字节本卡一字未动。

## 结果一句话

**RED 31 → GREEN 59/202（双树）→ 变异体被 :410 击杀 → 生产落地两文件哈希精确 →
5 文件电池 59/202 rc0 → 13 节点 I-08-C 13/13 rc0 → I-10-B 自带 verify 7/7 rc0 → 无 STOP。**

| 项 | 计数 |
|---|---|
| per-case 对齐表 | **31 = 31 explicit-default + 0 assertion-rewrite** |
| RED（promoted 树，未改测试） | **31 failed / 53 passed / 177 subtests**，rc 1 —— 失败集合与 PROMOTION-EXEC 记录**逐行一致**（31/31 identical，`evidence/01_red_promoted_battery.txt` vs 其 `B-6c_model_focused_tests.txt`） |
| GREEN（promoted 树） | **0 failed / 59 passed / 202 subtests**，rc 0（`evidence/02_…`） |
| GREEN（before-image 树） | **0 failed / 59 passed / 202 subtests**，rc 0（`evidence/03_…`）——证明只去隐藏依赖、不改业务含义 |
| 变异检查 | 1 处对齐调用改回省略 ⇒ 该用例在 **`model_registry.py:410`** 再次失败（rc 1，`missing driver for bank_revenue: other_revenue has no explicit default`）⇒ 还原 ⇒ 全电池恢复 rc 0（`evidence/04a/04b`） |
| 生产最终态 | test = `89a76809…`（对齐版）；registry = `62f864b9…`（I-10-B promoted 源，30116 B）——均为期望哈希，逐字节复核通过 |
| 生产 5 文件电池 | **59 passed / 202 subtests，rc 0**（`evidence/05_…`，verbose 复跑 `05b_…` 同数） |
| 13 节点 I-08-C（full promotion 下复验） | **13 passed，rc 0**（`evidence/06_…`；RF_IMPORT_ROOT=生产树） |
| I-10-B 自带 focused 核（`verify_i10b.py after`） | **total 7 / passed 7 / failed 0，rc 0**（`evidence/07_…`；在本 attempt 的 `iso/rf/scripts` 副本上跑，**零写入 I-10-B attempt** —— 规避 PROMOTION-EXEC NR-4 的边界） |
| py_compile（两文件） | rc 0 `PYCOMPILE_OK both`（`evidence/05a_…`） |

## Rule (c) 判定：0 个 assertion-rewrite

**31 个失败用例全部为 explicit-default。没有任何一个用例「本身就是对 silent-0.0-fill 的断言」，
因此 rule (c) 未被触发，未替换任何断言为 raise 期望。** 判据（逐例核对过）：

- 31 例的断言目标全部是 **guardrail 数学 / 业务规则**（负利率符号、churn 时序、backlog fsum、
  reserve downgrade、overflow fail-closed、time-exposure 负暴露、CASES 期望值保真……）；
  silent-fill 只出现在**输入物化**环节（旧 registry `:335`
  `drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))`），不是任何断言的对象。
- 什么才会触发 rule (c)：存在一条形如「**省略字段 ⇒ 结果与 0.0 等价 / 不应抛**」的断言
  （即把旧行为本身当作期望）。本文件中不存在这样的用例 —— 若存在，本表该行会标
  `assertion-rewrite` 并给出替换后的 raise 断言 + 引用注释；本轮该列为 **—（无）**。
- 兜底证据：双树 GREEN —— 若某例真在断言 silent-fill，它在 promoted 树上不可能因「传显式 0.0」
  而变绿；31/31 变绿 ⇒ 全部只是调用方缺显式入参。

## 31 例 per-case 对齐表

证据列说明：RED = `evidence/01_red_promoted_battery.txt`（与 PROMOTION-EXEC
`evidence/B-6c_model_focused_tests.txt` 逐行同集，见其行号）；语义不变证明 = 双树同绿
`evidence/02/03`（同输入两棵树算出同一结果）。

### A. item-level FAILED（6）

| # | 用例 | RED 缺省字段（:410 报错） | 对齐改法（make callers explicit） | 类别 | 保留的被测规则（证据） |
|---|---|---|---|---|---|
| 1 | `test_bank_negative_rates_preserve_sign_without_probability_clamp` | `bank_revenue.other_revenue` | drivers 显式加 `"other_revenue": [0]`（原隐含值 0.0） | explicit-default | 负利率不被夹：`1000·(-0.005) − 800·(-0.01) + 2 + 0 = 5`；`driver_value_bounds(bank_revenue, funding_cost) == (-inf, inf)` 断言未动（RED 行 4–65） |
| 2 | `test_churn_timing_is_revenue_lost_after_exit` | `cohort_subscription.usage_revenue` | 显式 `"usage_revenue": [0]` | explicit-default | churn 退出后收入丢失：`[960]`（带 churn）→ `[1200]`（不带），断言未动（RED 行 66–127） |
| 3 | `test_inconsistent_customer_timing_cannot_create_negative_exposure` | `cohort_subscription.usage_revenue`（掩盖了 regex） | 显式 `"usage_revenue": [0]` | explicit-default | 负 time-exposure 仍必须抛：`assertRaisesRegex(…, "time exposure")` 恢复可达（曝光 `0+10·0−10·1<0`）；断言未动（RED 行 128–145） |
| 4 | `test_large_backlog_preserves_small_revenue_increment` | `project_backlog.backlog_remeasurements` | 显式 `"backlog_remeasurements": [0]` | explicit-default | 1e16 背景下 1 元增量不被吞：`fsum → [1]`（断言未动，RED 行 146–206） |
| 5 | `test_late_customer_additions_do_not_earn_half_year_automatically` | `cohort_subscription.usage_revenue` | 显式 `"usage_revenue": [0]` | explicit-default | 晚增客不自动半折：`≈1300`（fraction 1/12）→ `[1200]`（fraction 0），断言未动（RED 行 207–268） |
| 6 | `test_reserve_downgrade_is_not_saleable_depletion` | `reserve_depletion.other_revenue` | 显式 `"other_revenue": [0]` | explicit-default | reserve 下调不是可售耗竭：`10·0.8·5 = [40]`（`reserve_revisions=[-20]` 本就显式），断言未动（RED 行 1726–1786） |

### B. SUBFAILED（25）

| # | 用例 · subTest | RED 缺省字段 | 对齐改法 | 类别 | 保留的被测规则（证据） |
|---|---|---|---|---|---|
| 7 | `test_overflow_and_negative_net_revenue_fail_closed` · `{'units':[1e308],'unit_revenue':[1e308]}` | `unit_sales.other_revenue`（regex `"finite"` 被 :410 抢先） | 该 subTest 元组显式加 `"other_revenue": [0]` | explicit-default | 溢出 fail-closed 恢复可达：`1e308·1e308→inf→"must be finite"`；第二 subTest（`other_revenue=[-2]` → "negative"）本就显式、逐字未动（RED 行 269–286） |
| 8 | `test_public_calculator…` · `subscription_arr_bridge` | `usage_revenue` | 新 helper `_with_explicit_missing_defaults`：对 CASES 缺席的每个 optional 显式填 `spec.defaults.get(d, 0.0)`（= 旧 registry 的确切隐含值） | explicit-default | EXTENSION_CASES 期望值逐项保真 + 输入不被改写（`assertEqual(explicit, before)` 仍是同一「no-mutation on the object passed」性质） |
| 9 | 同上 · `renewable_generation` | `other_revenue` | helper 同上 | explicit-default | 同上（RED 行 347–406） |
| 10 | 同上 · `aum_fee_bridge` | `recognized_performance_fees` | helper 同上 | explicit-default | 同上（RED 行 407–466） |
| 11 | 同上 · `unit_sales` | `other_revenue` | helper 同上 | explicit-default | `[50, 60]` 保真（RED 行 467–525） |
| 12 | 同上 · `capacity_utilization` | `other_revenue` | helper 同上 | explicit-default | `[144, 162]` 保真（RED 行 526–585） |
| 13 | 同上 · `subscription` | `usage_revenue` | helper 同上 | explicit-default | `[200, 220]` 保真（RED 行 586–645） |
| 14 | 同上 · `usage_platform` | `fixed_revenue` | helper 同上 | explicit-default | `[20, 24]` 保真（RED 行 646–705） |
| 15 | 同上 · `services` | `other_revenue` | helper 同上 | explicit-default | `[160, 180]` 保真（RED 行 706–765） |
| 16 | 同上 · `project_backlog` | `backlog_remeasurements` | helper 同上 | explicit-default | `[55, 75]` 保真（RED 行 766–825） |
| 17 | 同上 · `resource` | `other_revenue` | helper 同上 | explicit-default | `[50, 55]` 保真（RED 行 826–885） |
| 18 | 同上 · `infrastructure` | `other_revenue` | helper 同上 | explicit-default | `[200, 210]` 保真（RED 行 886–945） |
| 19 | 同上 · `bank_revenue` | `other_revenue` | helper 同上 | explicit-default | `[44, 49]` 保真（RED 行 946–1005） |
| 20 | 同上 · `asset_management` | `performance_fee_revenue` | helper 同上 | explicit-default | `[10, 11]` 保真（RED 行 1006–1065） |
| 21 | 同上 · `retail_franchise` | `franchise_system_sales`（首触；`recognized_fee_rate`、`supply_revenue` 亦缺席） | helper 同上（填全部缺席 optional） | explicit-default | `[50, 60]` 保真（RED 行 1066–1125） |
| 22 | 同上 · `transport` | `ancillary_revenue` | helper 同上 | explicit-default | `[160, 180]` 保真（RED 行 1126–1185） |
| 23 | 同上 · `real_estate_rental` | `other_revenue` | helper 同上 | explicit-default | `[200, 220]` 保真（RED 行 1186–1245） |
| 24 | 同上 · `licensing_commercial` | `milestone_revenue`（首触；`royalty_revenue`、`service_revenue` 亦缺席） | helper 同上 | explicit-default | `[50, 60]` 保真（RED 行 1246–1305） |
| 25 | 同上 · `advertising` | `other_revenue` | helper 同上 | explicit-default | `[160, 180]` 保真（RED 行 1306–1365） |
| 26 | 同上 · `gaming` | `other_revenue` | helper 同上 | explicit-default | `[200, 240]` 保真（RED 行 1366–1425） |
| 27 | 同上 · `cohort_subscription` | `usage_revenue`（`timing_factor`/两个 fraction 有声明 default，helper 也显式物化为 1.0/0.5/0.5） | helper 同上 | explicit-default | `[210, 225]` 保真 —— 0.5 的声明缺省绝不能被写成 0（双树同绿证其值未变）（RED 行 1426–1485） |
| 28 | 同上 · `delivery_pipeline` | `other_revenue` | helper 同上 | explicit-default | `[50, 70]` 保真（RED 行 1486–1545） |
| 29 | 同上 · `milestone_royalty` | `milestone_revenue`（`service_revenue` 亦缺席） | helper 同上 | explicit-default | `[10, 12]` 保真（RED 行 1546–1605） |
| 30 | 同上 · `insurance_service` | `other_revenue` | helper 同上 | explicit-default | `[200, 220]` 保真（RED 行 1606–1665） |
| 31 | 同上 · `reserve_depletion` | `other_revenue`（首触；`reserve_revisions` 亦缺席、无声明 default） | helper 同上 | explicit-default | `[360.0, 455.4]` 保真（RED 行 1666–1725） |

**未被触碰的邻居用例（RED 已绿 ⇒ 不得过度对齐，逐字节保持原样）**：
`test_nonfinite_input_is_rejected_for_every_model`（`required[0]` 先于 optional 抛 "finite"）、
`test_scenario_customer_capacity_bounds_do_not_admit_above_one`（`utilization` 是 required）、
`test_resources_cannot_deplete_beyond_available_stock`（`closing_reserves` required bounds 先抛）、
`test_fx_backlog_remeasurement_is_not_fictitious_revenue`（字段本就显式）、
`test_boolean_and_text…`、`test_year_gaps…`、`test_driver_path_length…`、
`test_shutdown_can_reach_zero…` —— 全部在 `changes.diff` 中零改动。

## 对齐改法的精确构成（changes.diff §1，+40/−5 行，无断言弱化）

1. 模块级注释块（引用 I-10-B defect-1 + E1E7 DEC-E1E7-4 先例）+ helper
   `_with_explicit_missing_defaults`（缺席 optional → `spec.defaults.get(d, 0.0)`，**逐值复制旧
   registry 的隐含物化**，含声明缺省也显式物化 = 完全显式调用方）。
2. public sweep 3 行：把「直接传 CASES dict」改为「传显式化副本」，no-mutation 断言目标同步改为
   实际传入的对象（性质不变：**断言被传对象未被 registry 改写**）；数值断言
   `assertAlmostEqual(observed, target)` 逐字未动。
3. 7 个手写调用点：**只加输入字段**（5 行原地追加显式字段 + 2 行改写为带显式字段的同一字面量），
   全部断言语句（`assertEqual`/`assertAlmostEqual`/`assertRaisesRegex`）逐字未动。
4. **registry 语义零改动**：§2 就是 I-10-B 源 `62f864b9…` 的字节精确落地（defect-1 省缺即抛
   `:410` + defect-2 语义角色符号规则），不是本卡的编辑。

## 生产最终态（两文件）

| 文件 | before | after（= 期望） | 验证 |
|---|---|---|---|
| `tests/test_model_economic_guardrails.py` | `665164528d7d…` / 7988 B | **`89a76809321e87d852ec8d5863650eed8ac1b47c52c8f1b38db4768f7d5ac82a`** | = iso 对齐版逐字节 |
| `scripts/model_registry.py` | `9ec6529550f1…` / 26446 B | **`62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081`** / 30116 B | = I-10-B promoted 源逐字节（写前 before-hash guard 通过后才写） |

生产前像均存 `recovery/before_images/`（哈希复核 = 原 before 值）。

## 边界事件（如实登记）

1. **py_compile 首次调用 CLI 误用（rc 1）**：`python -m py_compile <test> <scratch\guard.pyc>`
   把第二个位置参数当源文件读 → Errno 2。该次调用在报错**前**已对齐地编译了测试文件，副作用 =
   `tests/__pycache__/test_model_economic_guardrails.cpython-313.pyc`（20:17:01，13577 B，派生
   自**当前已对齐的**生产源，git-ignored；同目录 357 个兄弟 pyc 均为既有）。随后以显式 `cfile`
   重跑 rc 0（`evidence/05a`），**生产源文件本身从未处于风险中**。无 `.pyc` 写入 `scripts/`。
2. **`Copy-Item` 保留源 mtime**：`scripts/model_registry.py` 落地后 mtime 显示 2026-09-20 19:22:26
   （I-10-B 源文件时间），内容哈希 `62f864b9…` 逐字节复核通过；mtime 非内容事实，登记备查。
3. **并发卡痕迹未动**：`tests/test_fc1105_fault_injection.py`、`tools/pre_push_gate.py` 的 ` M`
   仍是 GATE-OQ-FIX 卡的（本卡前后一致）；仓根 `.pytest_cache` mtime 2026-07-12（远早于本卡，
   未被触碰 —— 全部 pytest 运行带 `-p no:cacheprovider`）。
4. 生产 `scripts/`/`tests/`/`config/`/`tools/` 自 20:13 起的**全部**写入 = 恰好本卡两个目标文件
   + 上述派生 pyc（`evidence/08_final_integrity.txt` 的 recent-write 扫描）。

## 生产链路为何不受省缺即抛影响（写前核实，防止「以为只有测试错」）

`scripts/forecast/segments.py:96-115` 是**唯一**生产调用方：它在调用
`calculate_registered_model` **之前**把每个 optional 显式物化
（`_optional_series(..., float(spec.get("defaults", {}).get(driver, 0.0)))`），
因此生产链路永远传完整 driver 集；`tests/test_models.py`（走 `calculate_model_path`）同理。
grep 证实 `calculate_registered_model(` 的调用点 = 生产 1 处 + 本测试文件 20 处，别无其他。

## 边界遵守

- 生产写入**恰好 2 个**授权文件；其他测试/product 文件哈希前后相等（`binding.json` 邻居 pin 全对上）。
- **registry 语义未被本卡编辑**（§2 是源文件字节复制）；从未把 silent-0.0 塞回 registry。
- 无任何 git 写（git 仅 `status`/只读）；CW 零接触；B-6b/natural_window 未碰；
  `tools/pre_push_gate.py` 未碰；I-10-B attempt 零写入（verify 复制到本 attempt 跑）。
- 不自签：`handoff.status = review_pending`，无 signature；da=unmapped，acc=unproven。

## 未跑 / 移交

| 项 | 状态 |
|---|---|
| 全仓 test suite（5 文件电池以外） | 未跑 —— 卡面只要求对齐电池 + 13 节点 + I-10-B focused 核；全量门在父的 batch-4 push 门跑 |
| M05/M14/M20/M24 四卡 oracle 的 ACTIVE 化 | **后果登记**，本卡不回改那些字节（E1E7 追认节自会生效） |
| 父分仓提交 | **父保留提交权**（§十八 执行映射 ③）；本卡零 git 写 |
| 独立复审 | `review_pending` —— 本卡不自签 | 
