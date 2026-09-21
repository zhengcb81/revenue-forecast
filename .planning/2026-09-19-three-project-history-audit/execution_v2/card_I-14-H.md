本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-H — natural_window.py 的两个产品级缺陷

Parent：I-14。依赖：I-00-B。Owner：观测逻辑维护者；独立 reviewer。

来源：`OWNER_DECISIONS.md` §7 第 4 项 + §13 **T1-10**（授权立卡，**产品 + 计划双侧**）。

锚点：I-14-B 的 `iso/natural_window.py`（`SUT_VERSION = "i14b-after-2"`；
`BASIS_REGISTRY` 在 `:60`；`derive_window` 在 `:128`；`_claim.basis` 分发在 `:199-222`）。

1. **缺陷①：`claim.basis` 无枚举校验。** 实测被 accept：`basis=''`、`basis` 缺键、`basis=None`、
   `basis='wall_clock'` **全部被接受** ⇒ J1/J2/J3/J11 可被一个字段名绕过。
   修复：`basis` 必须属于封闭枚举 `{sample_span, command_total, observation_plus_quick_check,
   sum_of_windows, union_of_windows}`；未登记/空串/`null`/缺键一律**拒绝**（`R-BASIS-UNKNOWN`）。
2. **缺陷②：`union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**
   实测：**2220 被接受而诚实的 1740 被拒** ⇒ 方向倒置。
   修复：自然观察区间**只由观察阶段构成**；无 `windows[]` 时 `intervals = [(started_at,
   observation_finished_at)]`，quick_check **永不进入**；`union_seconds`/`sum_seconds` 同为观察口径。
   并另加 J15 覆盖"把 quick_check 改名成第二个窗"的变体。
3. **⚠ ②已烧进冻结期望。** `harness/frozen_expectations.json`（r1，sha256
   `3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b`）中
   `expected.W1.computed.union_seconds = 2220`。
   修复**必须同时**以**追加式 provenance** 更正该期望（旧 2220 → 新 1740），
   并新增锚定断言 `sum_seconds=1740`、`observation_interval_count=1`、
   `quick_check_overlap_seconds=0`、`quick_check_in_observation_intervals=false`。
4. **不得回改冻结正文。** 旧值必须保留于 `expected_superseded`（含 old/new/`pre_image_sha256`/时刻/原因），
   并附 r1→r2 期望映射的机械 unified diff。**"从未有过 2220"是禁止的写法**——
   I-14-B 已按此形态落地过 r2，本卡沿用同一形态（`oracle.md` §11.4 为范本）。
5. 注意 I-14-B 的 r2 已**先改实现、后冻结期望**（与其 §4 理想次序相反）。本卡若沿用，
   必须同样如实声明时序，并以 `before/cmd-CASES-r2-r1sut` 型独立复现证明期望不是"照修好的实现写"。
6. 不得改 `SUT_VERSION` 以掩盖差异；不得以"更新期望贴合实现"代替建立新 oracle。

退出：两个缺陷各有可失败用例（RED→GREEN），且期望更正以追加式 provenance 留痕。
恢复：回退实现与期望追加节；保留 `expected_superseded` 与全部原始输出。
