# T1-8 前置项 ① / ④：判据是「**按异常精确类型名比较**」还是「**退回 `isinstance`**」——并把八代 runner 按 sha256 逐批登记

- 卡：`T1-8` / attempt `a20260920-02`
- 权限：`OWNER_DECISIONS.md` §13 **T1-8**（TIER-1）
- 状态：**本卡不执行推广**。T1-8 的四项前置须**先满足**，本卡处理**第 ① 项与第 ④ 项**。
- 性质：**核验 + 事实登记**（不是口径确认，也不是实施）
- 前序：`a20260920-01` 已关闭前置 **③**（方式为事实更正）；本卡承接 **①④**。前置 **②** 已由 `M17-M20/…/rc_namespace.json` 承载。

---

## 1. 裁定原文与前置的位置

`OWNER_DECISIONS.md` §13 **T1-8**：

> **授权推广**，按「建议」形态：**只改各批自己的副本**、`before/` 留旧版、**不回改历史 rc、不动冻结证据**、每批补「改 `expected` ⇒ rc=3」变异臂。四项前置**须先满足**：①**不退回 `isinstance`**；②登记 schema 约束「`expected` 只能是裸类型名」；③先修 rc 归类与「期望缺失」口径；④**逐批按 runner sha256 登记命名空间**。

**未注明的两项（本卡处理的就是它们）**：

- **①「不退回 `isinstance`」** —— 字面上**没有说明它禁止什么**。一条禁令只有在其**被禁止的属性可被检出**时才有约束力。本卡先把这个属性变成**可判定的谓词**，再对八代逐代判定。
- **④「逐批按 runner sha256 登记命名空间」** —— 要求**以 sha256 为键**逐批登记，**不得按整数跨批聚合**。

---

## 2. 六条命题（`scripts/verify_t8_pre1.py`，`overall = PASS`）

| # | 命题 | 结果 | 证据 |
|---|---|---|---|
| **P-1** | `isinstance(exc, ModelRegistryError)` 与「异常的**精确类型名** == `ModelRegistryError`」**可证不同**，故「单独由 `isinstance` 决定的 `PASS_rejected`」**无法区分目标异常与另一种异常** | **holds** | 目标 MRO = `ModelRegistryError → ValueError → Exception → BaseException → object`；**目标自身的子类**上两谓词**分叉**（`isinstance=True` / `nameeq=False`） |
| **P-2** | 对**八代 runner** 逐代（**以各自 sha256 为键**）能判定其 `PASS_rejected` 是「由 `isinstance` 单独决定」还是「受类型**名**等式约束」 | **holds** | 八代**八个不同 sha256**；分类见 §3 |
| **P-3** | 冻结树内**已存在**声明了**非目标**类型名的用例集，即 P-1 的区分**已被实例化过** | **holds** | **8 个异构用例集**（4×`TypeError` + 4×`ValueError`）；全域 147 个 `cases.json` 中 `expected` 取值分布 `ModelRegistryError:1620 / None:20 / TypeError:4 / ValueError:4` |
| **P-4** | 冻结的裁决记录**确实**把该区分**落到了 rc 上** | **holds** | `M09/…/selfcheck/B`：declared=`TypeError` / raised=`ModelRegistryError` / `raised_matches_expected_name=False` ⇒ **`FAIL_wrong_exception_type` / rc=3**；对照臂 `E`（未变异）⇒ `PASS_rejected` / rc=0 |
| **P-5** | **每一代**都读 `cases.json[].expected`（故「声明非目标名」能影响裁决） | **holds** | 八代全部 `reads_case_expected=True`；且**全以下标读**（`case["expected"]`）⇒ 缺键即 `KeyError`（与前置③结论一致：只有 M13–16/M17–20/M25–28 三代定义「缺声明」规则） |
| **P-6** | 推广所要求的**「改 `expected` ⇒ rc=3」变异臂**，在**已经装上契约闸门**的批次里**不可满足**（实测 rc=1） | **holds** | `M25` case `F1`：把 `expected` 改成 `'ValueError'` ⇒ **`raw_rc = 1`**（`harness_error=True`，`frozen case contract violated`）；见 §6 |

---

## 3. P-2：八代 runner 的裁决谓词 —— **必须按 sha256 指名，不得按整数聚合**（前置④）

| 批次族 | runner sha256（前 12） | 字节 | 类型**名**等式谓词 | `PASS_rejected` 由 `isinstance` **单独**决定 |
|---|---|---|---|---|
| **M01-M04** | `b5fcc68563f5` | 12222 | **无** | **是（禁用形态）** |
| **M05-M08** | `fd3a11c9226a` | 14758 | **无** | **是（禁用形态）** |
| M09-M12 | `997c553b0b9e` | 28912 | **有**（`raised_matches_expected_name`） | 否 |
| **M13-M16** | `9e4a6450d6ab` | 32038 | **无** | **是（禁用形态）** |
| M17-M20 | `94619a98f576` | 36744 | **有**（`declared_ok = raised_name == declared`） | 否 |
| M21-M24 | `a5ee7599c37e` | 20133 | **有**（`expected_type_matches_raised`） | 否 |
| **M25-M28** | `eab0116220df` | 22720 | **无** | **是（禁用形态）** |
| **M29-M31** | `9ea69c72dced` | 28242 | **无** | **是（禁用形态）** |

**八代八个不同 sha256**，且**恰好每代一个**，与前置④「逐批按 runner sha256 登记命名空间」的形态吻合。

**「禁用形态」的精确判据**（不是「有没有调用 `isinstance`」，而是「`PASS_rejected` 由什么决定」）：

```python
entry["verdict"] = ("PASS_rejected" if is_target
                    else ("FAIL_wrong_exception_type" if not is_import_or_file
                          else "FAIL_import_or_file_error"))
```

即 `PASS_rejected ⟺ is_target`。**八代中有五代是这个形态**（M01-04 / M05-08 / M13-16 / M25-28 / M29-31）。另三代在该三元式之外**另有**一个类型**名**等式；注意它们**仍然保留** `is_target = isinstance(...)` 调用（用于 `FAIL_wrong_exception_type` 与 `FAIL_import_or_file_error` 的分流），**故「调用 `isinstance`」本身不是判据**。

---

## 4. P-1 的方向 —— **本卡必须先纠正我自己的一个错误判据**

**首版探针（`.planning/_pwf_tmp/probe_t1_8_mro.py` rev 1）结论是「无分叉」，而那个结论是错的。**

- **我写了什么**：按**声明名**构造异常（`cls = getattr(mr, declared)` 后 `cls("probe")`），再比 `isinstance(exc, ModelRegistryError)` 与 `type(exc).__name__ == "ModelRegistryError"`。
- **我得到什么**：对 `ValueError` / `TypeError` / `KeyError` **两谓词皆 False** ⇒ 报「无分叉」。
- **为什么这是坏的探针**：它在**非目标类**上比较两个**必然一致**的谓词。**分叉是单侧的，且落在目标的「子孙」一侧，不在「祖先」一侧。**

**正确的读法**：

| 形态 | 精确类型名 | `isinstance(exc, 目标)` | 名等式 | 是否分叉 |
|---|---|---|---|---|
| 目标自身 | `ModelRegistryError` | **True** | **True** | 否 |
| **目标的子类** | `SubclassOfTarget` | **True** | **False** | **是** |
| 目标基类下的**兄弟** | `SiblingUnderBase` | False | False | 否 |
| **目标基类自身**（`ValueError`） | `ValueError` | False | False | 否 |

⇒ **`isinstance` 比名等式「接受得更多」，方向是「**向目标的子孙放宽**」，不是「向 `ValueError` 放宽」。**

**这对本案的直接后果**：`cases.json` 里那 4 个 declared=`ValueError` **在 `isinstance` 判据下会被正确拒绝**（`isinstance(ValueError(), ModelRegistryError) is False`）—— 所以「声明的 `ValueError` 会假过」这个直觉说法**不成立**。真正会假过的，是一个**类型名不是 `ModelRegistryError` 但它是其子类**的异常。

**教训（本项目第 16 次同源）**：**判据的「方向」也要匹配对象** —— 本次具体形态是「**我在两个谓词必然一致的域上证明了它们一致**」。这与第 6 次（比对面不匹配）、第 11 次（从「两者可分」推「两者同码」）、第 14 次（枚举校验非全函数）、第 15 次（哈希字节域）同族，但**新在**：错不在量、不在面、不在域，而在**我把「放宽的方向」搞反了**。

---

## 5. P-3 / P-4：冻结证据已经实例化了这个区分

**8 个异构用例集**（全域 147 个 `cases.json` 中仅此 8 个）：

```
M09/…/recovery/selfcheck/B/evidence/M09/cases.json   {'TypeError': 1, 'ModelRegistryError': 10}
M10 … 同形   M11 … 同形   M12 … 同形
M25/…/recovery/selfcheck/cases/F1/evidence/M25/cases.json   {'ValueError': 1, 'ModelRegistryError': 10}
M26 … 同形   M27 … 同形   M28 … 同形
```

**M09 五臂是一套完整的变异对照**（五臂**全部**由 `997c553b` 执行）：

| 臂 | `cases.json` 的 `NEG-CARD.expected` | 变异 | 实测裁决 |
|---|---|---|---|
| A | `ModelRegistryError` | oracle 正例期望值 → `[999.0]` | rc **2**（`no_verdict_fidelity`） |
| **B** | **`TypeError`** | **声明被改写为非目标名** | **rc 3**（`FAIL_wrong_exception_type`） |
| C | `ModelRegistryError` | NEG-CARD 变异值 → `0`（不再被拒） | rc **3**（`FAIL_not_rejected`） |
| D | `ModelRegistryError` | 正例期望缺失 | rc **2** |
| E | `ModelRegistryError` | **无变异（对照）** | rc **0**（`pass`） |

**B 臂的关键三元组**（`run_result.json` 实读）：

```
expected                        = 'TypeError'
raised                          = 'ModelRegistryError'
raised_matches_expected_name    = False
verdict                         = 'FAIL_wrong_exception_type'
is_target_type                  = True     <-- isinstance 说「对」，名等式说「错」
```

⇒ **这正是 P-1 分叉的逆向实例**：`is_target_type=True` 却 `raised_matches_expected_name=False`，**只有名等式能把它判负**。`E` 臂作对照（未变异 ⇒ `PASS_rejected` / rc=0）⇒ 差异**归因于声明被改写**，而非环境。

---

## 6. P-6：推广所要求的变异臂**在装了契约闸门的批次里不可满足**

`M25-M28` 是**唯一**在冻结件里带 `case_contract` 的一代：

```json
"case_contract": {
  "expected_count": 11,
  "expected_ids": ["NEG-CARD","N01a",…,"CONT-BREAK"],
  "declared_expected_exception": "ModelRegistryError",
  "rule": "every case's `expected` must equal declared_expected_exception and the id list
           must equal expected_ids, otherwise the harness refuses to issue a verdict (rc=1)"
}
```

**F1 臂实测**：把 `NEG-CARD.expected` 改成 `'ValueError'` ⇒ **`raw_rc = 1`**（`harness_error = True`，`reason = "frozen case contract violated"`），**而不是 rc=3**。

**这与裁定的推广要求直接冲突**：

- 裁定要求「**每批补「改 `expected` ⇒ rc=3」变异臂**」；
- 但在 `M25-M28`（以及任何采纳该契约闸门的批次）里，**改 `expected` 是 harness 缺陷（rc=1），不是判负（rc=3）**。

⇒ **该字面要求不可在全部批次上满足**：若照抄进 `M25-M28`，会写下一个**与实测相反的期望值**（把 rc=1 记成 rc=3），即**在推广里植入一个假期望**。**本卡不解决该冲突**（属裁定层），仅**登记并移交**（§8.2）。

**旁证**：八代中**只有 `94619a98`（M17-M20）**声明 `declared_expectations_enforced=True`，且有 `NOT_JUDGED_declaration_unusable` 这一「不可用声明不判」的第三类；`M25-M28` 的 `F1` 证明「声明不可改写」是**另一条更强的**约束。⇒ **「声明被改写」在各代映射到的 rc 并不唯一**，这**再次印证前置④的必要性**：**不得按整数跨批聚合**。

---

## 7. 结论：前置 ① 与 ④ 的落地状态

- **①「不退回 `isinstance`」** —— **本卡把它变成可判定谓词**，并给出判定结果：**八代中五代是禁用形态**（§3）。⇒ 推广时**须逐代处理**，**不得把任一代的形态当作「已满足」**；且**判据是「`PASS_rejected` 由什么决定」，不是「有没有调用 `isinstance`」**。
- **④「逐批按 runner sha256 登记命名空间」** —— **本卡按 sha256 逐批给出八代的登记表**（§3），八代**八个不同 sha256**。⇒ **该前置的登记形态已在盘上**；本卡**不写** `rc_namespace.json`（属编排层，见 §8.3）。
- **本卡不宣称前置 ①②③④ 全部关闭**：①④ 经本卡核验**可判定/可登记**，但**①仍有五代处于禁用形态** ⇒ **推广仍不得先行**。

---

## 8. 移交编排层 / owner 的提示（本卡不做）

1. **`task_plan.md` 的 T1-8 段需要一条追加式更正**：此前记录「前置 ①④ 仍未落实」，本卡给出的是**更精确的形态** —— **④ 的登记表已在本卡 §3 给出（八代八个 sha256）**；**① 的判定结果是「五代禁用、三代合规」**，而非「未落实」。建议按 **T1-12 ①** 形态追加，**不回改正文**。
2. **裁定层需澄清「每批补『改 `expected` ⇒ rc=3』变异臂」**：该字面要求在 `M25-M28` 上**与实测相反**（实测 rc=1）。建议改为「**每批补一条『声明被改写 ⇒ 失败』的变异臂，其具体 rc 按该代契约取值**」（M25-M28 取 1，M09-M12 取 3）。**须由裁定方出具，不可由实现者自填**（T1-24 / T1-21 纪律）。
3. **`rc_namespace.json` 建议补两列**（按 **T1-12 ①** 追加，**不回改原值**）：`pass_rejected_predicate`（`isinstance-only` / `name-equality`）与 `case_contract_present`（`yes` / `no`）。
4. **`M25-M28` 的 `case_contract` 与「`expected` 只能是裸类型名」的 schema 约束（前置②）语义重叠**：契约说的是 **`expected` 必须等于** `declared_expected_exception`，比「是裸类型名」**更强**。⇒ 前置②的登记形态可能需要与该契约对齐（**属裁定层**）。

---

## 9. 产物

| 产物 | 字节 | sha256 |
|---|---|---|
| `scripts/verify_t8_pre1.py` | 见下方 | `23213d948047c80dc349d3624d84bb8c49bb42c575fa42f33ae2cd64e9c80ddf` |
| `t8_pre1_pre4_verification.json` | 16057 | `5fb6e414b57a649b9a7754e56d035dc324f67986b5ce3f413d48fe1933a51697` |

**幂等性**：连跑 **4 次同哈希**（`5fb6e414…`）；证据 JSON 内**不含任何环境取值**（无 temp 路径、无时间戳、无随机名），全部为常量、哈希或**从冻结证据读出**的值。

> **自哈希说明**：`handoff.json` **不登记自身哈希**（自指）；其 sha256 只记于 `task_plan.md` 与本目录之外。

**边界**：runner 编辑 **0**；**回改历史 rc 0**；冻结证据写入 **0**；`START_HERE.md` 写入 **0**；`rc_namespace.json` 写入 **0**；**产品文件 0 条**（`git status --porcelain -- . ':(exclude).planning'` 仅 `.tmp-r41-mutation/` 一条，系**本轮之前** T1-5 遗留的未跟踪临时树，**本轮未触碰、未删除**）；生产锚点 `scripts/model_registry.py` = `9ec6529550f189a4…` **一致**；`status` 转移 **0**；**代签 0**；**删除 0**。

**本卡自行修正的判据错误**：首版 MRO 探针在「两谓词必然一致」的域上比较，得出错误的「无分叉」结论；已在 §4 如实登记，并改在**目标子类**上重测。
