# MODEL-ORACLE-ALIGN — oracle.md（开工前冻结 / frozen BEFORE any write）

- 卡：`MODEL-ORACLE-ALIGN` — align the RF model TEST battery to I-10-B defect-1（省缺即抛）semantics,
  then RE-ATTEMPT row **B-6c**（unblock what PROMOTION-EXEC STOPPED+REVERTED）
- attempt：`a20260922-01`
- 冻结时间：2026-09-22 20:07 +01:00（本文件是本 attempt 的**第一个写入**；其后本文件一字不改）
- parent：`session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- interpreter：`C:\Miniconda\python.exe` 3.13.9 / pytest 9.1.1（与源卡同一解释器，实测）

## 0. 权限链（authority chain，逐层引用）

1. **OWNER_DECISIONS.md §十八（2026-09-22，原话逐字）**：「A-1: 1, A-2: 授权, **B: 全批**， C:更新函件」
   → 执行映射行 **B = 全批** = 「§十七 B-1..B-7 **全部批准**」。B-6c（I-10-B → RF `scripts/model_registry.py`）
   在已批准清单内 —— **晋升授权早已存在，不因 STOP 而失效**。
2. **PROMOTION-EXEC `a20260922-01/decision.md` §B-6c STOP detail**：晋升按哈希落地后 5 文件电池
   **31 failed / 53 passed**，全部 traceback 在 promoted `scripts/model_registry.py:410`；frozen failure rule
   已执行（control pre-check 前像注册表 = **59 passed rc 0** → STOP → 逐字节 REVERT `9ec65295…` → post-revert
   59 passed rc 0）。其结语明确移交：「before B-6c can be re-attempted, RF's
   `tests/test_model_economic_guardrails.py` needs an alignment/replacement decision … This is an
   owner/parent orchestration call — NOT decided here.」**本卡就是那一次委派的对齐执行。**
3. **产品语义权威（不可逆向）**：I-10-B defect-1（T1-22）**省缺即抛** = approved product semantics。
   本卡**永不**把 registry 语义改回 silent-0.0-fill；只对齐 TEST 侧。
4. **E1E7-ERRATA-LANDING `a20260921-01` 前瞻披露先例（同物种，镜像其效力语言）**：
   DEC-E1E7-4 逐字句式 ——「修复未晋升 ⇒ 在晋升之前现行冻结值仍然权威；本条为前瞻披露
   （promotion 前置知会），**不改变任何现行期望、不改变任何 status、不改变任何资格**」。
   本卡的对齐编辑同样按此效力落地：**调用方显式化 = 0 业务含义变化**；M05/M14/M20/M24 四份
   defaults-相位翻转的 oracle 前瞻披露（E1E7 已落卡）**仅因本卡 B-6c 成功落地而由 INACTIVE 转为
   ACTIVE** —— 只登记后果，不回改那些卡的任何字节。
5. 同物种先例：DW15 / I-15-A「product contract tests encode the wrong oracle」finding。

## 1. 作用对象与写边界（exactly 2 production files）

| 角色 | 路径 | before（实测，写前 pin） |
|---|---|---|
| 被对齐的测试（唯一允许改的 TEST 文件） | `tests/test_model_economic_guardrails.py` | sha256 `665164528d7d37663ff37474ddae20bfcf3c16eceefde3e6f54473324251ab77` / **7988 B** |
| 重新晋升的 registry（唯一允许改的 PRODUCT 文件） | `scripts/model_registry.py` | sha256 `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` / **26446 B**（before-image 与 `PROMOTION-EXEC/recovery/before_images/B-6c/model_registry.py` 同像） |

晋升源（实测复核通过）：`execution_runs/I-10-B/a20260919-01/iso/rf/scripts/model_registry.py`
= sha256 **`62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081`** / **30116 B**。
伴生 `scripts/model_extensions.py` **不动**（生产与 I-10-B iso 均为 `9939480b…` / 14475 B，实测一致）。

**除此之外生产树零写入**；不碰其他测试文件、不碰任何其他 product 文件、无 git 写、CW 只读、
B-6b/natural_window 出卡外、不自签（da=unmapped, acc=unproven）。

## 2. RED 基线：31 个失败用例的完整清单（来自 PROMOTION-EXEC evidence，冻结为期望清单）

电池（PROMOTION-EXEC 原命令，原样复跑）：
`python -X utf8 -B -m pytest tests/test_model_{registry_contract,economic_guardrails,extensions,extensions_anchor,integration_bounds}.py -p no:cacheprovider --basetemp=<attempt>/scratch/* -q`（cwd = 树根）

计数对账：**59 test items**（control = 59 passed / 202 subtests passed）。promoted 下
**31 failed entries = 6 item-level FAILED + 25 SUBFAILED**，53 passed items + 177 subtests passed
（6+53 = 59 items；25+177 = 202 subtests）。卡面「31/84」= 31 failed entries / (31+53) entries。
**31 个失败全部落在 `tests/test_model_economic_guardrails.py`，全部源于 `model_registry.py:410`
省缺即抛（或其掩盖下的 regex 不匹配）** —— PROMOTION-EXEC 已证 control 同电池 59 passed ⇒ 回归
solely by B-6c。

### 2a. item-level FAILED（6）

| # | 测试 | 缺省字段（省缺即抛所指） |
|---|---|---|
| 1 | `test_bank_negative_rates_preserve_sign_without_probability_clamp` | `bank_revenue.other_revenue` |
| 2 | `test_churn_timing_is_revenue_lost_after_exit` | `cohort_subscription.usage_revenue` |
| 3 | `test_inconsistent_customer_timing_cannot_create_negative_exposure` | `cohort_subscription.usage_revenue`（regex "time exposure" 被 :410 抢先） |
| 4 | `test_large_backlog_preserves_small_revenue_increment` | `project_backlog.backlog_remeasurements` |
| 5 | `test_late_customer_additions_do_not_earn_half_year_automatically` | `cohort_subscription.usage_revenue` |
| 6 | `test_reserve_downgrade_is_not_saleable_depletion` | `reserve_depletion.other_revenue` |

### 2b. SUBFAILED（25）

- 25.1 `test_overflow_and_negative_net_revenue_fail_closed` subTest `{'units':[1e308],'unit_revenue':[1e308]}` → `unit_sales.other_revenue`（regex "finite" 被 :410 抢先；第二 subTest 已带 `other_revenue` 本就通过）
- 25.2–25.25 `test_public_calculator_preserves_every_existing_case_without_mutation` 的 24 个 model subTest：
  `subscription_arr_bridge`, `renewable_generation`, `aum_fee_bridge`, `unit_sales`,
  `capacity_utilization`, `subscription`, `usage_platform`, `services`, `project_backlog`,
  `resource`, `infrastructure`, `bank_revenue`, `asset_management`, `retail_franchise`,
  `transport`, `real_estate_rental`, `licensing_commercial`, `advertising`, `gaming`,
  `cohort_subscription`, `delivery_pipeline`, `milestone_royalty`, `insurance_service`,
  `reserve_depletion`
  （`direct_growth`、`direct_revenue` 两个 subTest 无 optional，本就通过）

**已核实不失败、不需改动的邻居用例**（防过度对齐）：`test_nonfinite_input_is_rejected_for_every_model`
（`required[0]` 先于 optional 抛 "finite"）、`test_scenario_customer_capacity_bounds`
（`utilization` 是 required，先抛）、`test_resources_cannot_deplete_beyond_available_stock`
（`closing_reserves` required bounds 先抛）、`test_fx_backlog_remeasurement_is_not_fictitious_revenue`
（已显式给出 `backlog_remeasurements`）、`test_driver_path_length_and_unknown_driver_fail`、
`test_boolean_and_text…`、`test_year_gaps…`、`test_shutdown_can_reach_zero…`。
**这些用例在 RED 中属于 53 passed，GREEN 中必须仍然原样通过（逐字节不改其断言）。**

## 3. 冻结期望（O 系列 —— GREEN 后逐条核对）

- **O-1 RED**：未改动的 `tests/test_model_economic_guardrails.py` + promoted registry（`62f864b9…`）
  在隔离树上复跑同电池 ⇒ 复现 **31 failed / 53 passed / 177 subtests passed**（raw 输出入
  `evidence/01_red_promoted_battery.txt`）。失败集合 = 第 2 节清单逐一对应。
- **O-2 对齐方法 = make callers explicit（唯一合法方法）**：测试把**此前隐含的缺省值显式传入**
  （no-default optional 的旧隐含值 = `0.0`；declared-default optional 保持省略即可，因其在两棵树上
  语义完全一致）——**保留每个用例原本要测的东西**（guardrail 数学 / 业务规则）。
  **绝不**把 silent-0.0 塞回 registry。
- **O-3 断言改写条款（仅限 genuinely asserts silent-fill 本身者）**：若某用例本身就是「省略字段 ⇒
  得到 0.0」这一旧行为的断言，则其断言替换为 defect-1 期望（raise `ModelRegistryError`，信息含
  `has no explicit default`），并加注释引用 **I-10-B defect-1（T1-22，省缺即抛）** +
  **E1E7-ERRATA-LANDING 前瞻披露先例**。逐例（若有）列入 `decision.md` 的
  per-case 表 `assertion-rewrite` 列；**预期主路径全部为 explicit-default**。
- **O-4 双树 GREEN（证明只去隐藏依赖、不改业务含义）**：同一份改写后的测试文件必须
  ①在 promoted 树（`62f864b9…`）上整电池全绿；②在 before-image 树（`9ec65295…`）上整电池全绿。
  两棵树各自 raw 输出入 evidence。期望值均为：**0 failed / 59 passed items / 202 subtests passed**。
- **O-5 变异式反证（fix 非空转）**：把**一处**已对齐的调用改回省略该字段 ⇒ 该用例必须再次在
  `model_registry.py:410` 失败 ⇒ 还原 ⇒ 复跑恢复全绿。raw 输出入 `evidence/04_mutation_*.txt`。
- **O-6 零外扩**：除 §1 两个生产文件外，生产树与任何其他测试文件零字节变化（写前/写后哈希对账
  入 binding；git 只读 `status --porcelain` / `--no-optional-locks diff` 作证）。
- **O-7 生产落地顺序**：iso GREEN 先于生产写入；先写对齐后的
  `tests/test_model_economic_guardrails.py`，再以字节精确 copy 覆盖 `scripts/model_registry.py`
  ← `62f864b9…`（先留 before-image 于本 attempt `recovery/before_images/`，两份都留）。
- **O-8 生产验证**：
  1. 对齐后 5 文件电池（cwd=生产树）⇒ 期望 **0 failed / 59 passed / 202 subtests passed**；
  2. 13 节点 I-08-C 套件（`I-08-C/a20260919-01/test_i08c_consumer_rejection.py`，sha `3f83fdf2…` / 13152 B，
     `RF_IMPORT_ROOT=<生产树>`）⇒ 期望 **13/13 rc 0**（PROMOTION-EXEC run-wide final 亦 13/13，须在
     full promotion 下复验）；
  3. I-10-B 自身 commands.json 的 focused 核（`verify_i10b.py` after 相位，7 例）——若可在**本 attempt
     目录内**跑而不写 I-10-B attempt 则跑（PROMOTION-EXEC NR-4 的边界同样约束本卡）；否则如实登记
     not-run + 理由。
  4. `py_compile` promoted registry + 对齐测试 ⇒ rc 0。
- **O-9 冻结失败规则**：若诚实对齐后仍有某用例不绿 —— **该用例 STOP**：生产两文件全部回到
  before-image（test 文件也回 `66516452…`），精确报告该用例（它就是「与 defect-1 真不兼容的业务
  期望」候选），不改语义、不缩小断言、不硬凑绿。
- **O-10 交付物**：`oracle.md`（本文件，先冻结）、`binding.json`（双 before-pin + 源 pin）、
  `commands.json`、`decision.md`（31 例 per-case 对齐表：explicit-default vs assertion-rewrite，
  逐例引证据）、`changes.diff`（repo 前缀，明确分 test-alignment vs registry-repromotion 两段）、
  `handoff.json`（review_pending，unsigned）、`evidence/`（RED / GREEN×2 / mutation / 13-node /
  production runs raw）、`recovery/README.md`（两文件精确回滚：before-image 全路径 + 哈希）。

## 4. 本卡不做

- 不回改 registry 语义到 silent-0.0；不给 registry specs 填 0.0 default（那是改产品语义，出卡）。
- 不改 `tests/test_models.py` / `tests/test_model_extensions*.py` / 任何其他测试或 product 文件。
- 不跑、不改 CW 任何东西；不碰 `tools/pre_push_gate.py`；不碰 B-6b/natural_window。
- 无 git add/commit/restore/stash；无对外发布；不自签；M05/M14/M20/M24 等卡的 oracle 字节不动。

## 5. 写前只读侦察记录（provenance）

冻结前完成的读取：PROMOTION-EXEC decision/commands/binding/evidence `B-6c_model_focused_tests.txt`
（31 条短摘要逐条抄录）、E1E7 decision+oracle（先例语言）、I-10-B commands.json（电池与缺陷定义）、
OWNER_DECISIONS §十八、生产 `scripts/model_registry.py`（前像 :335 silent-fill）、
`tests/test_model_economic_guardrails.py`（152 B 行级全读）、`tests/test_models.py`、
`forecast/segments.py:96-115`（**唯一生产调用方在调用前把每个 optional 显式物化
`spec.get("defaults", {}).get(driver, 0.0)` ⇒ 生产链路不受省缺即抛影响**）、
`tests/conftest.py`（registry tmp 隔离 fixture）、golden_behavior_hashes（不含 model_registry pin）。
实测哈希：promoted `62f864b9…`/30116 ✓、`model_extensions.py` 两处 `9939480b…` ✓、
I-08-C `3f83fdf2…`/13152 ✓、interpreter 3.13.9/pytest 9.1.1 ✓。
