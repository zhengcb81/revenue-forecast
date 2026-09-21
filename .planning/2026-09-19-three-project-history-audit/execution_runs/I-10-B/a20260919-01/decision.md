# I-10-B 决策记录（decision.md）

- 卡：`execution_v2/card_I-10-B.md`（来源 `OWNER_DECISIONS.md` §13 **T1-22**）
- attempt：`a20260919-01`
- status：**planned（未升格）**

---

## DEC-I10B-1：缺陷①的修复形态

**问题**：`model_registry.py:335` 的
`values = drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))`
把「driver **不存在**」与「driver **没找到**」编码成**同一输入**。

**候选方案**

| 方案 | 内容 | 处置 |
|---|---|---|
| (a) | 把隐式 0 改为**显式 0** | **否决** —— 仍无法区分「没找到」，只是把歧义写在明处 |
| (b) | 省略时按「该 driver 语义上是否可省」判定，可省才补默认 | **否决** —— 引入与缺陷②同类的「按名字/语义猜测」 |
| **(c)** | **省缺即抛 `ModelRegistryError`；仅当 `spec.defaults` 有显式值时才允许省缺** | **采纳** |

**理由**：卡文第 1 点已显式排除 (a)。选 (c) 使「省略」与「显式给值」在契约上**可区分**，
且判定依据是**已声明的 `spec.defaults` 数据**，不是新造的语义猜测。

**采纳的代码**（`changes.diff` 第二个 hunk）：

```python
if driver not in drivers:
    if driver not in spec.defaults:
        raise ModelRegistryError(
            f"missing driver for {model_id}: {driver} has no explicit default"
        )
    values: object = [spec.defaults[driver]] * len(years)
else:
    values = drivers[driver]
```

**负例**

- `R-B1-N1`：只有 optional driver 且无显式 default 的模型，省缺时**必须抛** —— 通过
- `R-B1-N3`：**显式给 0.0** 仍然**被接受**（区分了「省略」与「显式 0」）—— 通过
- `R-B1-P1`：省略**有**默认值的 optional driver（`unit_sales.timing_factor` default=1.0）**仍合法** —— 通过
- `R-B1-P1b`：声明的默认值就是实际使用的值（省略 == 显式）—— 通过

---

## DEC-I10B-2：缺陷②的符号规则

**问题**：`_SIGNED_DRIVERS` 是**按名字硬编码**的集合，导致
`other_revenue` signed 而同语义的 `usage_revenue` / `franchise_system_sales` /
`supply_revenue` / `recognized_performance_fees` 落在 `[0, inf)`。

**采纳规则**：`dimension ∈ _REVERSAL_CAPABLE_DIMENSIONS` **且** `driver ∈ _REVERSAL_CAPABLE_DRIVERS`

```python
_REVERSAL_CAPABLE_DIMENSIONS = {"backlog", "revenue", "reserve_volume", "aum_fee"}
_REVERSAL_CAPABLE_DRIVERS = { ... 15 个显式角色位 ... }

def _is_reversal_capable(driver, dimension) -> bool:
    return dimension in _REVERSAL_CAPABLE_DIMENSIONS and driver in _REVERSAL_CAPABLE_DRIVERS
```

**为什么是「语义角色」而不是「换一个名字集合」**

`_REVERSAL_CAPABLE_DRIVERS` 是**显式声明的角色位**，且**必须**经 `dimension` 闸门才生效：

- 单独把某 driver 写进角色表，**不会**让它获得符号 —— 它的 declared dimension 也必须合格。
- 因此既有的**数量型**（如 `closing_stores`）与**比率型** driver 的符号**不可能**被误改。
- 缺陷③的负例即验证此点：名不在任何角色表里的新 driver **不得**静默获得「按名字猜测」的符号。

**名字硬编码任意性的实测证据**：`recognized_performance_fees`、`reserve_revisions`、
`backlog_remeasurements` **均不在** `_SIGNED_DRIVERS`，却**早已**经 `driver_bounds` 元数据
到达 `(-inf, inf)` —— 同一语义角色、两种名字待遇。这正是本项要消除的东西。

**负例**

- `R-B2-N1`：`franchise_system_sales` 传负值**必须被接受** —— 通过
- `R-B2-P1`：数量型 driver `closing_stores` 保持 `[0, inf)` —— 通过
- `R-B2-N2`：身份不明的 driver 名抛 `ModelRegistryError`，**不得**凭名字获得符号 —— 通过

**`_SIGNED_DRIVERS` 的处置**：降为 `_SIGNED_DRIVERS = _REVERSAL_CAPABLE_DRIVERS`
**仅供导入兼容**；`driver_value_bounds()` **不再读它**。

---

## DEC-I10B-3：值域变更的判据选择（本轮修正）

**问题**：首版 `compute_compat.py` 把「最终下界为 `-inf`」当作「本次变更」。

**这是错的**：修复前就已有 **37 个** cell 处于 `[-inf, inf)`（`other_revenue` 14 个、
`bank_revenue.asset_yield`、`bank_revenue.funding_cost`、`aum_fee_bridge.market_change` 等）。
用「下界是否为 `-inf`」作判据会**同时**犯两个错：夸大波及面、**掩盖**真实变更集。

**采纳判据**：对 `(model, driver)` 的 `(lo, hi)` **对**做 BEFORE/AFTER 差分，
只取**实际发生变化**的 cell。

**结果**：165 个 cell 中**恰好 5 个**变化，全部为下界放宽、上界不变。

> 这与本项目既往的第 5 次同源教训一致：**判据必须匹配被判定对象的形态**——
> 追加式编辑用前缀判据、中部插入用 `difflib`、值域变更用**差分**而非**终态**。

---

## DEC-I10B-4：兼容性影响的双路径判定

卡文第 3 点要求「任何边界变化都要附『哪个 M 卡的哪个用例会受影响』」。
值域改动与被省略默认值的改动**是两条不同的传播路径**，必须分开判定：

### 路径 (a) — 值域放宽（缺陷②）

**结论：零个冻结判定受影响。**

- 全 M01–M31 证据树 **1579** 个 JSON 全量扫描。
- `CASE_TARGET` 17 个：其 `value` 全为**正数**或**类型/长度类负例**
  （`__bool__` / `nan` / `inf` / `-inf` / 空数组 / 未知 driver），**无一**依赖「负的实数值应被 `[0, inf)` 拒绝」。
- 唯一负值命中：`M14/recovery/probes/signed_driver_probe.json` —— 该件**自述**
  `"purpose": "post-hoc design probe (NOT a frozen case, NOT the oracle)"`。
- M14 另有两处把旧行为记为**契约边界**：`cases.json > extra_observations[OBS-SUPPLY-BOUND]`
  与 `oq_rulings.json > open_questions_mirroring_handoff[OQ-03]`。
  两者**均自带「不门禁 / 属未决 D/E 决策」声明** ⇒ 不是 pass condition。

### 路径 (b) — 省缺即抛（缺陷①）

**结论：四张卡各一个相位（`defaults`）翻转。**

实测对照（BEFORE vs AFTER，真实入口 `calculate_registered_model`）：

| 卡 | `positive` | `continuity_positive` | `defaults` |
|---|---|---|---|
| M05 | 未变 | 未变 | **`ok [600.0]` → 抛** |
| M14 | 未变 | 未变 | **`ok [50.0]` → 抛** |
| M20 | 未变 | 未变 | **`ok [220.0]` → 抛** |
| M24 | 未变 | 未变 | **`ok [210.0]` → 抛** |

**根因**：四张卡的 `defaults` 输入块**都省略了**至少一个「optional 且无显式默认」的 driver
（M05/M20/M24 为 `usage_revenue`；M14 为 `franchise_system_sales` 等三者）。
其冻结期望成立**恰恰依赖**缺陷①的静默补 0 —— 最直白的书面自证是
`M24 evidence/M24/oracle.json > hand_notes.defaults`：
「**usage_revenue omitted -> 0**; 200 - 15 + 15 + 10 + 0 = 210」。

**这不是缺陷，而是修复的预期后果**：缺陷①的定义就是「把『不存在』与『没找到』编码成同一输入」，
四张卡的 `defaults` 相位正踩在这个歧义上。

---

## DEC-I10B-5：受影响冻结件的处置

**卡文第 3 点**：「受影响的历史期望**一律追加更正、不回改**（沿用 T1-12 的统一规则）」
**卡文第 5 点**：「**不得**为本卡扩大 allowlist 去改 31 张 M 卡的正文或证据」

⇒ **本卡不执行任何冻结件编辑**。只产出**待登记清单**（`compatibility_impact.md` §5，E-1…E-7），
交由编排层按 **T1-12 ① 形态**（追加新节 + 行级「第 X 行已过时，以本节为准」标注）落地。

**禁止**任何「回改为从未如此」的写法；旧值一律原样保留。

---

## 未决 / 待他方

| 项 | 性质 | 状态 |
|---|---|---|
| 本卡是否落地生产 | **owner 职权内** | 待编排层决定；本卡未落地 |
| 四卡 `defaults` 相位的追加式勘误（E-1…E-4） | owner 职权内，但**须按 T1-12 形态** | 已列清单，未执行 |
| E-5/E-6（M14 `OBS-SUPPLY-BOUND` / `OQ-03`） | `OQ-03` 原文自述**属 D/E 决策** | 见下 |
| I-10-B 的独立验收 | **TIER-2：须独立 reviewer 出具** | **未取得；不得记为已验收** |

> **执行纪律第 7 条**：「总的批准」不得膨胀为「所有的结论」。
> M14 `OQ-03` 的终局裁定、以及本卡的独立验收，**均须他方出具**。
> 本文件不代签、不预判。
