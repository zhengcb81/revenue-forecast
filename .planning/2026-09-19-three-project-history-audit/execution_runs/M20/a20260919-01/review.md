# M20 · implementer review record — cohort_subscription（客户流量与时间暴露）

Card M20（`execution_v2/card_M20.md`），Parent I-10，model_id `cohort_subscription`，
attempt `execution_runs/M20/a20260919-01`。标题/卡号/model_id 与 `oracle.md`、`decision.md`、
`handoff.json` 一致。

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts and issue its own verdict.

## 1. 做了什么（可复核的清单）

| 步骤 | 结果 | 证据 |
|---|---|---|
| A 绑定 | 只读复制进本 attempt，副本与生产 hash 相等 | `binding.json`、`evidence/M20/source_manifest.json` |
| 冻结 | `oracle.md`（手算）→ `oracle.json`（独立 stdlib 脚本，含桥平衡 assert）→ 首次产品 stdout | `source_manifest.json` → `mtime_ordering` |
| B 正例 | 实测 `[195.0]` vs 手算 `[195]`，abs_diff 0.0，容差 1.95e-07 | `evidence/M20/stdout.txt` |
| B 保真 | 扁平 `list`、长度 1 = `len(years)` = `len(expected)`、普通有限 `float` | `run_result.json` → `fidelity` |
| B 连续性（两年，卡片用例） | 实测 `[195.0, 240.0]` vs 期望 `[195, 240]` | `run_result.json` |
| B 默认值 | 实测 `[220.0]` vs 手算 `[220]`（三个显式默认 + `usage_revenue` 静默 0；**不参与判定**） | `run_result.json` |
| C 负例 | 11/11 以 `ModelRegistryError` 拒绝 | `evidence/M20/negative_results.json` |
| 桥断裂语义 | CONT-BREAK 实测消息 `cohort customer continuity failed: FY2028`，与冻结预期（第二年 opening 比第一年 closing 多 1）一致 | `negative_results.json` |
| 保真重生成 | `input/oracle/cases.json` 重生成后 sha256 **逐字节相同** | `evidence/M20/oracle_regen_proof.json` |
| 变异证明 | 副本篡改 → rc 3 / 3 / 2 / 1；未篡改 → rc 0；冻结件 hash 未变 | `evidence/M20/mutation_selfcheck.json` |
| 边界探针 | `timing_factor=[0]` → `5.0`；1e-12 级跨年失衡被容忍 → `[195.0, 240.000000000002]` | `evidence/M20/extra_probes.json` |
| D/E/F | **未做**（D 需专业决策；E 属 I-10-A；F 需 I-12 冻结设计） | `decision.md`、`handoff.json` |

## 2. oracle 的独立性（本卡要害）

- 期望值来自 `scripts/oracle_M20.py`（stdlib only，`Decimal` 精度 50），
  `evidence/M20/oracle_selfcheck.json` 记录 `product_import_present = false`；
  脚本在生成时对客户桥做 `assert`（`期初 + 新客 − 流失 == 期末`），
  因此不平衡的输入不可能被写成"正例期望"。
- runner 只调用一个产品函数，期望只从 `evidence/M20/oracle.json` 读。
- 负例全部由新的内存 deepcopy 构造，不经 JSON 解析器；`PASS_rejected` 要求
  `isinstance(exc, ModelRegistryError)`，导入/文件错误记 FAIL。
- 卡片引用的行号（入口 308、注册 240）在隔离副本上逐行复核（两个 anchor 均为 true）。
- **本卡是四卡中唯一真正的存量桥**：年内平衡与跨年连续两条检查都被负例击中
  （NEG-CARD 与 CONT-BREAK），且断裂例的两个年度**各自**平衡——这正是卡片 L123 的设计意图，
  实测消息与冻结预期逐字一致。

## 3. 结果明细（含实际异常消息）

- registry formula：`revenue = (opening_customers + new_customers * new_customer_revenue_fraction - churned_customers * churned_customer_lost_fraction) * revenue_per_customer * timing_factor + usage_revenue`
- required `['opening_customers', 'new_customers', 'churned_customers', 'ending_customers', 'revenue_per_customer']`；
  optional `['timing_factor', 'usage_revenue', 'new_customer_revenue_fraction', 'churned_customer_lost_fraction']`；
  declared defaults `{timing_factor: 1.0, new_customer_revenue_fraction: 0.5, churned_customer_lost_fraction: 0.5}`
  （`usage_revenue` **不在**其中 → 静默补 0）
- effective bounds：客户五项 `[0.0, inf]`、`revenue_per_customer [0.0, inf]`、
  `timing_factor [0.0,1.0]`、`new_customer_revenue_fraction [0.0,1.0]`、
  `churned_customer_lost_fraction [0.0,1.0]`、`usage_revenue [0.0, inf]`（**非** signed）
- 11 个负例消息：
  - `NEG-CARD`：cohort customer bridge failed: FY2027
  - `N01a`：cohort_subscription.opening_customers.FY2027 must be numeric
  - `N01b/c/d`：cohort_subscription.opening_customers.FY2027 must be finite
  - `N02`：driver cohort_subscription.opening_customers must contain one value per forecast year
  - `N03`：missing drivers for cohort_subscription: opening_customers
  - `N04`：unsupported drivers for cohort_subscription: unknown_driver
  - `N05a/b`：cohort_subscription.years must contain fiscal years
  - `CONT-BREAK`：cohort customer continuity failed: FY2028
- 负例计数：`rejected_with_ModelRegistryError=11`、`not_rejected=0`、`wrong_exception_type=0`、
  `import_or_file_error=0`。
- 退出码：`B-product-run` 原始 rc = **0**（= 期望 0）；runner 回读校验
  `printed_matches_evidence_file: True`。

## 4. 观察项与探针（均**不**参与退出码）

- `OBS-BASE-IGNORED`：`base_revenue=999` → `[195.0]`（calculator 丢弃 `base_revenue`）。
- `OBS-DEFAULT-EQUIV`：显式写四个可选 driver（1 / 0 / 0.5 / 0.5）与省缺相同（`[220.0]`）。
- `OBS-ZERO-CUSTOMERS`：全零客户桥 + `usage_revenue=[7]` → `[7.0]`，说明 `exposure < 0` 守卫
  接受暴露恰为 0。
- `PROBE-TIMING-ZERO`：`[5.0]`（ratio 域含下端点）。
- `PROBE-CONTINUITY-TOLERANCE`：`opening=[100, 120.000000000001]` → `[195.0, 240.000000000002]`，
  即 1e-12 级失衡在 `isclose(rel_tol=1e-9, abs_tol=1e-9)` 下被容忍。

## 5. 请 reviewer 优先攻击的点

1. **`ending_customers` 是输入而非推算值。** 模型只校验 `期初+新客−流失 == 期末` 与跨年连续；
   若披露的期末数本身错，桥会"自洽地错"。请确认这属于披露适配缺口而不是公式问题。
2. **"年中"时点不可运行时拒绝。** 注册表默认 `timing_factor = 1.0`（不是 0.5），
   本 attempt 没有为任何公司默认年中；但真实适配时必须由专业角色给发生月份（`DEC-M20-1`）。
3. **价格分层 / 同年新增又流失的群组无法表达**（`DEC-M20-2`）。
4. **桥容差 1e-9 是否合适**：实测 1e-12 失衡被容忍，1 户错配被拒。请判定容差是否需要收紧
   （若收紧，必须另立卡，不得在本卡改）。
5. **静默 0**：`usage_revenue` 无显式 default，被 `spec.defaults.get(driver, 0.0)` 静默补 0
   （`OQ-02`；注册表级 31 个可选 driver 同现象）。
6. **`usage_revenue` 非 signed**：与 M17/M18/M19 的 `other_revenue` 不同，本模型的 `usage_revenue`
   有效域是 `[0, inf)`，因此负用量收入会被拒。请确认这不是不一致而是刻意（`usage_revenue` 不在
   `_SIGNED_DRIVERS` 集合内）。
7. **隔离绑定来源**：I-00-B 未物化 checkout，本 attempt 自行物化只读快照（hash 与生产相等），
   需 owner 裁定（`OQ-01`）。
8. **pytest 未安装**：`A0b` 离线探测 rc = 1（无本地 wheel、网络禁用）；本卡无命令需要 pytest。

## 6. 本卡**不**主张什么

- 不主张模型准确，也不主张一家公司的映射可外推（`accuracy = unproven`）。
- 不主张 `disclosure_adaptation`（D 未作，属专业决策）。
- 不重写公式（本卡零产品改动）。

## 7. 建议 reviewer 动作

1. 在 scratch 重跑 `scripts/oracle_M20.py --card M20 --out-root <scratch>`，逐字节比对冻结的三个文件。
2. 重跑 `scripts/run_card.py`（argv 见 `commands.json` 的 `B-product-run`），比对 `run_result.json`。
3. 确认隔离副本 hash 仍等于生产。
4. 复算一个本卡未使用的 oracle：建议两年 `opening=[100,110]`、`new=[30,0]`、`churned=[20,0]`、
   `ending=[110,110]`、`revenue_per_customer=[3,3]`、两个比例 `[0.5,0.5]`、`timing=[1,1]`、
   `usage=[0,0]`；手算 2027 暴露 = 100+15−10 = 105 → 315，2028 暴露 = 110 → 330，先冻结再运行。
5. 裁定 `evidence/M20/oq_rulings.json` 的 OQ-01…OQ-05。

---

退出码自检（本卡自带）：见 `evidence/M20/mutation_selfcheck.json`。

| case | 篡改（仅作用于 `recovery/selfcheck/` 的副本） | 实测 rc | 期望 rc | 证明 |
|---|---|---|---|---|
| A | `oracle.json` 正例期望每个值 +1 | **3** | 3 | 篡改的期望无法躲在 rc=0 后面 |
| B | `cases.json` 的 N04 驱动名换成已注册的 `usage_revenue` | **3** | 3 | 未被拒绝的负例会被判为负 |
| C | 正例 `expected_float`/`tolerances` 各多一项 | **2** | 2 | 保真不符 → 拒绝给判定 |
| D | scratch 副本删除 `cases.json` | **1** | 1 | harness 失败与判定失败可区分 |
| E | 未篡改副本 | **0** | 0 | 绿可恢复 |

冻结件在 A–E 之后重新 hash，与运行前一致（`frozen_evidence_unchanged: true`）。

### 记录收尾单元（不产生任何产品行为）

`H-write-handoff`（生成 `handoff.json`）与 `Z-close-attempt`（写 `commands.json` 与
`after/final_deliverable_hashes.json`）在测量流水线（A0…G，14 个单元）之后**单独**由
`scripts/run_closing.py` 执行，各有独立 command-run-id 记录：
`evidence/M20/runs/H-write-handoff/`、`evidence/M20/runs/Z-close-attempt/`。
`commands.json` 由 Z 自己写，所以 Z 自己的 rc.json 是在它返回**之后**才刷新的：`commands.json` 中
Z 的 `raw_rc`（当前为 0）来自**同 argv 的上一次执行**，该口径写在该单元的 `raw_rc_note` 里；
**最近一次执行**的 raw rc 始终在 `evidence/M20/runs/Z-close-attempt/rc.json`（自述其
stdout/stderr 的 sha256）与 `pipeline_run.json`。
`after/final_deliverable_hashes.json` 按构造排除它自己与 `runs/Z-close-attempt/**`
（原因见该文件的 `excluded_from_the_table`）。

---

状态：`formula = review_pending`；`disclosure_adaptation = unmapped`；`accuracy = unproven`。
