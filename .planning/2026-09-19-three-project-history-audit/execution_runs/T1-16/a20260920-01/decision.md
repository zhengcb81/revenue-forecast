# T1-16 裁定记录 —— M02-01「被忽略字段是否仍受域约束」口径确认

- **卡**：T1-16（`OWNER_DECISIONS.md` §13，**TIER-1**）
- **attempt**：`a20260920-01`
- **性质**：**口径确认**（interpretation confirmation）—— 但**比 T1-17 / T1-24 更强一档**（见 §1）
- **裁定原文（逐字）**：

  > **T1-16** | **第四节：M02-01 被忽略字段是否仍受域约束** | **选 A（保持 fail-closed）**。理由：`base=-5` 实测仍被拒，说明现行为已是 fail-closed；改为 B（忽略未用字段）会放松校验面，风险大于收益。

- **落点**：`execution_runs/T1-16/a20260920-01/`

---

## 1. 本卡与 T1-17 / T1-24 的关键差别

T1-17 / T1-24 核验的是「裁定的**采纳形态**已在**文书**中成立」。
T1-16 核验的是**另一类、且更强的主张**：裁定**选 A = 「保持现行为」**，理由是「**现行为已是 fail-closed**」。

⇒ 该理由是一条**关于产品的、而非关于文书的**事实前提。**若该前提为假**（产品已不再拒绝负的 `base_revenue`），那么「选 A」就是在**选一个不存在的东西** —— 甚至是在**产品已经漂移到 B 的情况下宣称选了 A**。

因此本卡必须**以执行复现该前提，而不是引证**。引证该卡**自己记录的观测**，等于**引证被检验的东西本身** —— 这是循环论证。这与 T1-13 的方向性信任同一纪律：**一项决定的正当性依赖于世界的一个状态，本卡必须证明该状态「现在」成立。**

---

## 2. 五条命题

`scripts/verify_t16.py`，`overall = PASS` / **exit 0**。

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **S-1** | 校验器对 `base_revenue` 执行的是**统一的、dispatch 前的**负数检查，**与该模型是否真的使用该字段无关** | **holds** | ①源码：检查位于 `calculate_registered_model` 内、**先于** dispatch；②**执行探针**：对 `direct_revenue`（`del base_revenue`，**不用**该字段）与 `direct_growth`（`current = base_revenue`，**真用**）**双双抛错** ⇒ 该检查**不可能**是模型条件性的 |
| **S-2** | 对 `direct_revenue`，该字段**确实被忽略**：`base = 999` 与 `base = 1` 输出**完全相同** | **holds** | `base_1 = base_999 = [10.0, 12.0]`；源码 `_direct_revenue` 首行 `del base_revenue, years`（`model_registry.py:98`） |
| **S-3** | 拒绝是**真实的** `ModelRegistryError`，且**消息形态与记录一致** | **holds** | 实测 `ModelRegistryError: direct_revenue.base_revenue cannot be negative`；与 `evidence/M02/run_result.json > observations[OBS-NEG-BASE].message` **一致** |
| **S-4** | 被否的**选项 B 不在生效** —— 负 base **绝不会被静默忽略**，且该守卫是**无条件的** | **holds** | 负 base 对该「忽略字段」模型**仍然抛错**（**若为 B，此处本应返回值**）；守卫为裸 `if base < 0: raise …`，**无模型成员测试** |
| **S-5** | 裁定**不命令写操作**：冻结证据**未被触碰**，门**仍登记为 owner 保留**（**未自裁**） | **holds** | 产品文件改动 `[]`；`M02` 卡目录改动 `[]`；`handoff.json.open_questions` 仍载 `requires_owner_or_specialist_ruling`；`review.md` 载 `CLOSED-AS-RESERVED` |

**生产锚点**：`scripts/model_registry.py` = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` —— **一致**（**这是必要的**：裁定的前提是关于**这个**构建的，锚点漂移则前提不可判）。
**范围**：`.planning` 之外的产品文件改动 **0 条**。

---

## 3. 为何 S-1 要用「两个模型」而不是只看源码

只看源码（`if base < 0` 在 dispatch 之前）**不足以**证成 S-1 的主张。源码可能：
- 在别处**覆写**结果；
- 被**后续**逻辑绕过；
- 或实际路径根本不经过该守卫。

⇒ 探针**刻意挑两个模型**：一个 `del`s 该字段、一个**消费**它。**若检查是模型条件性的**（例如「只校验会被用到的字段」，那正是选项 B 的某种形态），**两个模型必然给出不同结果**。**实测二者都抛错** ⇒ 该检查**结构性**地不依赖模型。

**判据必须匹配对象的形态**：S-1 的主张是「**统一性**」（uniformity），而**统一性只能用「在应当相同的多个实例上实测相同」来证明** —— 单点观测在原理上无法支持一个普遍命题。

---

## 4. 本卡自行犯下并已修正的错误（如实登记）

两项均为 **harness 缺陷**，**不是产品缺陷**，且**都由护栏/异常显式暴露、未造成误报**：

1. **`@dataclass` 加载期 `AttributeError: 'NoneType' object has no attribute '__dict__'`**
   - **根因**：`importlib` 加载时**未先把模块注册进 `sys.modules`**；而 `@dataclass` 经 `sys.modules[cls.__module__]` 解析注解 ⇒ 模块缺席即崩。
   - **修正**：`exec_module` **之前**先 `sys.modules[spec.name] = mod`（并在失败时清理）。
   - **性质**：harness 缺陷。**若误判为产品缺陷，会得出「产品不可导入」的错误结论。**

2. **`ModelSpec.get` 不存在（`'ModelSpec' object has no attribute 'get'`）**
   - **根因**：我按 **dict** 写探针（`spec.get("drivers")`），而 `ModelSpec` 是 **frozen dataclass**（字段 `model_id / required / optional / defaults / dimensions / ratio_drivers / formula / calculator / driver_bounds`）。
   - **修正**：改为按声明字段构造驱动映射（`required + optional`，`ratio_drivers` 给无量纲值、其余给单位量级值）。
   - **性质**：又是**「判据/假设必须匹配对象形态」** —— 这次连**对象的类型**（dict vs dataclass）都假设错了。

⇒ 两项均已登记于 `handoff.json.error_made_and_corrected_in_this_card`。

---

## 5. 为何本卡**不改**任何载体

- **裁定的前提已在盘上成立**（S-1…S-4 全部实测 PASS）⇒ **无写入需求**。裁定选 A = 「**保持**现行为」，**本卡正是通过不写入来完成它**。
- **M02-01 仍是 owner 保留项**（S-5 已证）。裁定**给出了答案**（选 A），但这**不改变**「该卡当时把此项登记为 `requires_owner_or_specialist_ruling`」这一历史事实为真 ⇒ **回写 `open_questions` 为「已裁」正是 T1-21 禁止的那类回改**。
- ⇒ **口径文书的正确载体是本卡的记录**（与 T1-14、T1-20、T1-21、T1-17 同理）。

**⚠️ 本卡**不**声称 D/E 步骤已解决**：`decision.md` 载 E 属 I-10-A、F 需 I-12 冻结设计。本卡**只**回答 M02-01 这一项。

---

## 6. 边界

| 边界 | 值 |
|---|---|
| 产品代码改动 | **0 处**（裁定选 A = 保持现行为 ⇒ **不写入即执行**） |
| 被裁定对象写入 | **0 次**（`M02` 卡目录 `review.md`/`oracle.md`/`handoff.json`/`decision.md`/`evidence/*` 均未改） |
| `status` 转移 | **0 次**（M02 保持 `accepted_scoped` / `review_pending`-formula） |
| 代签 | **无** |
| 产品文件改动 | **0 条**（`.planning` 之外） |
| 生产锚点 | `9ec6529550f189a4…` **一致** |
| JSON 可解析 | 是；登记哈希**零失配** |

---

## 7. 产物

| 产物 | 说明 |
|---|---|
| `scripts/verify_t16.py` | 五命题验证器（含对**生产模块**的直接执行探针） |
| `t16_m02_01_fail_closed_scope.json` | 结构化结果（含 S-1…S-5 全部子证据） |
| `decision.md` | 本文件 |
| `handoff.json` | 移交编排层 |
