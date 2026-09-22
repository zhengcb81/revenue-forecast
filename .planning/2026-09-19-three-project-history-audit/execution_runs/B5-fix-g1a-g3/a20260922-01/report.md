# report.md — B5-fix-g1a-g3（修复卡：闭环 B5 独立评审的 2 项 BLOCKING + F-3..F-7）

- **Card**: `B5-fix-g1a-g3` · **Attempt**: `a20260922-01` · **Status**: `review_pending`
- **Authority**: owner 裁定（2026-09-22 逐字）「**D，G1-a**」（Fix 2 执行授权）；G2 的 owner 最终裁定
  「**留置**（或给取舍）」——推翻早前"分类优先级勘误"指示（见 §G2-留置项）。
- **被修复对象**: `B5-plan-level-remediation/a20260921-01/reviewer_report.md`
  （verdict: NOT ACCEPTED AS-IS — 3 blocking: F-1/F-2/F-3；cheap: F-4..F-7）
- **模式**: 历史件/生产/B5 attempt 全部只读；一切改动都在本 attempt 内的副本上；
  实现者**不自签**；`disclosure_adaptation=unmapped`、`accuracy=unproven`。

---

## 1. 路由设计（G1-a）与落点

全部逻辑只存在于**本 attempt 的一份副本**：`execution_runs\B5-fix-g1a-g3\a20260922-01\M25-M28\run_card.py`
（源为 B5 的补丁副本，B5 与历史件零改动；diff 见 `M25-M28\runner.diff`）。

| 触发 | rc | 代码落点（本副本） | 语义 |
|---|---|---|---|
| **结构问题**（无 `case_contract`、用例数/id 集不符、未知 id） | **1，原样不变** | 整集闸门 `if structural_problems:` 的早退分支（注释改写：值差异永不进入此中止） | harness/fixture/file 故障 |
| **声明不可用**（`expected` 缺失/畸形/非非空字符串） | **2 + `no_verdict`** | ① `unusable_declared` 在 case 循环**之前**计算；② 路由 `set_level_route_rc==2`；③ 最终裁决 `harness_incomplete or not cases_declared_ok or set_level_route_rc == 2` 拥有最高优先级 | **在任何用例被判定之前**求值（冻结 rc 表 START_HERE L90–115："该命令不产生裁决"） |
| **可用但不同的 `expected`（逐例）** | **3** | 逐例精确类型名判定（`declared_ok = raised_name == declared`）**+** 集合级路由直接断言 `set_level_forces_fail = (set_level_route_rc == 3)` 参与最终退出码 | owner 强制臂（M25-M28 历史上不可达） |

**集合级闸门不再是"记录但不驱动"**：`case_contract_check.set_level_declaration_gating` 由
`false` 改为 **`true`**，并新增 `set_level_declaration_routing`（authority、三支路由规则、
逐例路由 id、`value_difference_never_rc1`、`never_left_nongating`、`load_bearing`）与
`frozen_rule_text_conflict`（见 §G2）；`exit_code_semantics` 输出
`set_level_declaration_route` / `set_level_unusable_case_ids` / `set_level_usable_diff_case_ids` /
`declaration_usability_decided_before_case_judgment` / `value_difference_never_maps_to_rc1`。

**rc 常量零改动**：无任何既有 rc 被重编号，本卡只加路由、不加新码。
**冻结件零编辑**：`cases.json`、68 个历史 runner、`before/`、`START_HERE.md` 全部字节不变（§2/边界）。

## 2. 实测 E/F/B/G（+S）——31/31 卡，全部真实子进程 raw rc

数据：`_scratch\arms_raw.json`（128 runs）→ `evidence\arm_matrix.json`；逐批
`<batch>\evidence.json`。变异目标：文件序**首例** `expected=="ModelRegistryError"`（= `NEG-CARD`，全卡一致）。

| 批次 | 卡数 | E | **F** | B（历史 runner，同篡改） | **G** | S 结构臂 | 判定 |
|---|---|---|---|---|---|---|---|
| M01-M04 † | 4 | 0 | **0** | 0 | **1** | — | ❌ 不统一（超出 T1-8 授权范围，见 §5-G1） |
| M05-M08 | 4 | 0 | **3** | 0 | 2 | — | ✅ |
| M09-M12 | 4 | 0 | **3** | 3 | 2 | — | ✅ |
| M13-M16 | 4 | 0 | **3** | 2 | 2 | — | ✅ |
| M17-M20 ‡ | 4 | 0 | **3** | 3 | 2 | — | ✅（参考批，字节副本） |
| M21-M24 | 4 | 0 | **3** | 3 | 2 | — | ✅ |
| **M25-M28** | 4 | 0 | **3**（route=3） | **1** | **2**（route=2，no_verdict） | **1** | ✅ G1-a 三臂全按裁定 |
| M29-M31 | 3 | 0 | **3** | 0 | 2 | — | ✅ |

† **M01-M04 从未在 T1-8 的六个授权批次内**（无补丁存在）：F=0（无逐例闸门的伪造的绿）、
G=1（删键 → 硬下标崩溃）。**仅测量，未打补丁**（本卡无权扩权）——见 §5-G1。
‡ M17-M20 参考批，两角色均为历史字节副本，仅测量。

- **六个 REM-21 批次 23/23 卡：E=0、F=3、G=2 全部统一且符合预期**；加参考批 → **27/31 统一**。
- **arm B 与 B5 记录逐一相同、零变化**：M05=0、M09=3、M13=2、M21=3、**M25=1（原样记录，未改）**、M29=0。
- **arm G = 2（no_verdict），不是 1、不是 3**：23/23 卡；reason
  `cases_json_declared_expectation_missing:NEG-CARD`；该例 `NOT_JUDGED`，绝不计入 mismatch。
- **arm S（新增，M25-M28）= 1**：结构中止未被路由改动。
- **F-6 合规重跑**：M05-M08 由 B5 的 `CONT-BREAK` 改回合同的 `NEG-CARD`，结果与 B5/reviewer
  完全一致（E0/F3/B0/G2）——无结果变化，偏离已登记。

> 口径更正：简报转述的"expected uniform … on all 31 cards"在字面上**不成立**——
> 统一性是 **27/31**（M01-M04 从未推广）。已即时上报父 agent。

## 3. 双键证明（Fix 1 / F-1 / G3）

**改动**：本 attempt `M13-M16\run_card.py` 的 `expectation_consistency.facts` 一次计算、
**同值写入两个键**：`declared_expectations`（历史键，原名原义保留）+
`declared_expectations_in_cases_json`（合同 §2 键名，追加而非替换）。

**证明**（`evidence\g3_reader_proof.json`，`PASS=true`；脚本 `scripts\g3_reader_proof.py`）：

1. 从**历史字节** `execution_runs\M14\a20260919-01\recovery\consolidated_report.py` 中
   **正则提取**第 75 行的真实读取表达式
   `run["expectation_consistency"]["facts"]["declared_expectations"]`（逐字：
   `                 run["expectation_consistency"]["facts"]["declared_expectations"]))`），
   再对该表达式 eval：

| 输入文档 | 结果 |
|---|---|
| 冻结基线 `M14\evidence\M14\run_result.json` | ✅ 读出 `["ModelRegistryError"]` |
| **B5 补丁输出**（B5 `_scratch\M13-M16\E\M14\run_result.json`，只读） | ❌ **`KeyError: 'declared_expectations'`** —— **F-1 断裂被原样复现** |
| 本卡补丁输出，**E/F/G × M13–M16 = 12 份** | ✅ 全部读通，**双键都在且同值** |
| 本卡 **arm B** 输出（历史 runner 字节副本 ×4） | ✅ 旧键在、新键不在 —— 历史 runner 输出形态**未被改动** |

2. reviewer 要求的"四臂输出均含旧键"：旧键在 **E/F/G/B 全 16 份**输出中都存在
   （arm B 由历史 runner 产出，本就只有旧键）；新键在补丁 runner 的 12 份中全部存在。

**声明更正（Fix 1 附带）**：B5 实现者的「M05-M08 也做了同样的事」**不准确**——
M05-M08 的 runner **没有 `expectation_consistency.facts` 块**，无键可改；本卡**未**添加该块，
仅登记更正（decision.md D-F1、handoff.json `corrections`、各 evidence open_issues）。

## 4. F-3 … F-7 处置

| id | 处置一句话 | 证据 |
|---|---|---|
| **F-3** | **已修**：六批 `evidence.json` 全部重建，`arms.{E,F,B,G}` 由真实运行填充（rc/rc_per_card/verdict/mismatch/mutated_case/note），机器消费者不再读到 `null` | `<batch>\evidence.json` |
| **F-4** | **已登记**：M25-M28 历史"缺 expected ⇒ rc=1"来自**整集 `case_contract` 闸门**（`None != declared` → `run_card_before.py:140-168` 中止），**非** `KeyError`；无 KeyError、无输出 JSON；结论（rc=1 非 rc=3）不变。**START_HERE append 2 原文未编辑**（本卡无该授权）→ 见 §5-G4 | `M25-M28\evidence.json`；arm B 实测 1×4 |
| **F-5** | **已登记**：arm G 在 M25-M28 是第二项语义变更（历史 rc=1 且**符合**冻结码表"期望文件缺失→rc=1"字面 → 补丁 rc=2+no_verdict），为 T1-19 统一所需，与 G1 并列登记 | 同上 + `g1a_routing` 块 |
| **F-6** | **已登记 + 合规重跑**：B5 曾变异 `CONT-BREAK`（末例）而非合同的首/最低 id `NEG-CARD` 且未声明；本卡按合同用 NEG-CARD 重跑，E0/F3/B0/G2 与 reviewer 独立复跑一致 ⇒ 无结果变化 | `M05-M08\evidence.json`；`arms_raw.json` |
| **F-7** | **已修**：`scripts\verify_append_fixed.py` —— 嵌入 **19 条**冻结节全文行，断言 `len(set)==len`、断言嵌入表 == 从**字节验证前缀**实时抽取的行序列、逐句按**整行**校验前缀+当前文件；链证复跑通过（PRE/POST1 前缀 sha、单次 insert、+108/−0、+34/−0） | `evidence\start_here_append_proof_fixed.json`（`APPEND_ONLY=true`） |

## 5. 剩余缺口（如实列，不代裁）

- **G2-留置项（单列供父 agent 复核）**：见下节——冲突**留置**，双方冻结文本原样共存，本卡不裁优先级。
- **G1 · M01-M04 范围发现**：四卡从未被 REM-21 推广（不在 T1-8 六批授权内），实测
  E=0/**F=0**/**B=0**/**G=1**：改 `expected` 仍伪造的绿；删键 → 硬下标崩溃 rc=1。
  "uniform on all 31 cards" 因此**只成立到 27/31**。是否扩权推广 M01-M04 是 **owner 决定**，
  本卡仅测量、已上报。
- **G3 · `consolidated_report.py:75` 是恢复脚本、非 runner**：本卡证明其读取表达式对新输出
  可用；但该文件位于历史 M14 树内，**未被（也不应被）本卡改动**——它对 B5 输出会 KeyError 的事实
  只因 B5 输出不再产生（封存），历史树内读者仍读历史冻结输出（基线 ✅ 读通）。
- **G4 · START_HERE append 2 的 F-4 更正未落盘到 START_HERE**：本卡**没有**向
  `START_HERE.md` 追加的授权（T1-12/T1-19 的追加须 owner 授权），更正目前只存在于本卡载体。
  若需进册，须父 agent/owner 授权一次"append 3"。
- **G5 · 既有记录不一致（B5 内部，非本卡造成）**：B5 `binding.json` 实际
  `96733875…`/22652 B ≠ B5 自己 `handoff.json` 记录的 `06ff8064…`/20819 B。
  本卡只读发现、不修不写；供父 agent 决定如何处置封存件内部的记录漂移。
- **G6 · F-8（评审的 informational：追加节重复表头）不在本卡 Fix 清单内**，未处置；
  其"字节级纯追加"已被 §F-7 链证覆盖（`APPEND_ONLY=true`）。
- 本卡状态 `review_pending`；下一动作是**独立 reviewer** 复核，实现者不自签。

---

## §G2-留置项（owner 最终裁定：留置 —— 供父 agent 单独复核）

> **已知冲突，owner 裁定留置**：M25-M28 冻结 `case_contract.rule` 文本写「不同 `expected` ⇒
> 拒发裁决 rc=1」；冻结 rc 表（START_HERE L90–115）与 G1-a 裁定要求 rc=2/rc=3。
> owner **不裁定哪个冻结件优先**，选择将该冲突**永久留置登记**。本卡实现按 G1-a 路由
> （这是独立的执行裁定）；冲突双方文本**原样共存于册**，T1-11 下不编辑任何冻结件
> （`cases.json`、历史 runner、`before/` 一律不动）。

1. **无优先级断言**：本卡不主张"rc 表优先于 rule 文本"或反之——owner 明确拒绝该取舍；
2. 登记内容 = 冲突存在 + 实现依据 = G1-a **执行**裁定；
3. 同一登记镜像于 `decision.md` D-F3、`handoff.json:g2_conflict_record`、
   `M25-M28\evidence.json:g1a_routing.frozen_rule_text_conflict`，以及补丁 runner 自身输出的
   `case_contract_check.frozen_rule_text_conflict`（含 `precedence_between_frozen_artifacts:
   "NOT asserted - owner declined to rule"`）。

---

*本报告所有 rc 均为子进程进程退出码实测，非推断；所有历史读取只读；*
*`disclosure_adaptation=unmapped`、`accuracy=unproven`；`status=review_pending`；实现者不自签。*
