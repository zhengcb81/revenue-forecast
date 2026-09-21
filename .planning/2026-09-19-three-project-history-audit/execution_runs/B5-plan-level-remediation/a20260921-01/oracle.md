# oracle.md — B5+B6 (REM-21 跨批 runner 推广 / REM-22 rc 码表冻结)

- **Card**: B5+B6（plan-level authorized actions）
- **Attempt**: `execution_runs/B5-plan-level-remediation/a20260921-01/`
- **Authority**: `OWNER_DECISIONS.md` §13 **T1-8**（REM-21）与 **T1-19**（REM-22），均为 TIER-1。
- **Kind**: 验收基准（预期先冻结，后运行）。实现者不得自签。

---

## §0 冻结时序（**先冻结、后运行**的可核证据）

本轮有两层"先冻结"：

| 层 | 冻结载体 | sha256 | mtime (UTC) | 与运行的关系 |
|---|---|---|---|---|
| 契约层（真正的预期基准） | `PROPAGATION_CONTRACT.md` | `701429ea726de69f5c6d341e5d108be0eee8ed7a32ee3deb1c88692a6512eab3` | 2026-09-21T20:21:19Z | **早于**各批变异臂的任何输出；各批 worker 在本文件落盘后才被派出 |
| 登记层（REM-22 实测码位） | `evidence/b5_scan.json` | `78a1bfbf4c3d5fdc2f91d7733ac94a559df89137b50bc3229e8c010155a9008d` | 2026-09-21T20:20:06Z | 早于 §REM-22 的 START_HERE 追加（20:22Z） |

**如实声明**：本 `oracle.md` 文件本身落盘于契约与扫描**之后**（避免把未定的预期写成"事前"）。
按 T1-24 已确立的口径，**`oracle.md` 文本本身不作为"事前冻结证据"**；本卡的预期基准是上表
契约层文件——它是可逐字节复算的独立文件，其 mtime 早于全部变异臂输出，且其 sha256 已登记于
`binding.json`。

---

## §1 范围（做什么 / 不做什么）

**做**
1. REM-22：把**冻结 rc 码表**（已由 T1-19 写入 `execution_v2/START_HERE.md`）**追加式**补上
   **实测**的各批码位登记、历史偏差映射与规范歧义登记。**不重写、不回改任何历史 rc**。
2. REM-21：把参考实现（M17–M20 runner，`94619a98…`）的**逐例 `expected` 精确类型名比较**
   推广到 **M05–M16 与 M21–M31**（六批）。**只改各批自己的副本**（落在本 attempt 目录内），
   `before/` 与历史 attempt 一律不动，**不回改历史 rc**，**每批补一个变异臂**。

**不做**
- 不改 `cases.json`、`oracle.json`、`oracle.md`、`run_result.json`、`commands.json`、`handoff.json`
  等任何冻结件；不改任何历史 attempt 目录的任何字节。
- 不改生产仓 `C:\Users\郑曾波\Projects\revenue-forecast\scripts\`（只读）。
- 不回改历史 rc；不重跑任何历史卡的测量流水线；不重冻任何冻结件。
- 不把本卡的资格外推到任何产品/准确性/披露结论。

---

## §2 参考实现（被推广的对象）

`execution_runs/M17/a20260919-01/scripts/run_card.py`
sha256 = `94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252`（36744 B）。

**权威性依据**（四卡自带证据 + reviewer r3 判定，逐条可核）：
`review.md:409`、`:422`、`:518`；`handoff.json:30,239`；
`after/final_deliverable_hashes.json:880`；`evidence/M17/evidence_hashes.json:134`；
`after/hash_table_verification.json:68`。

**sha256 更正登记**：§7.2 / §13 引用的 `5307d2cc…` 是 **r2 世代**值（`review.md:162/339/348`），
已被同一 reviewer 的 r3 判定取代。`5307d2cc…` **保留为 superseded，不回改**。

**比较语义（必须逐字保持）**
```python
# expected 只能是裸异常类型名；比较为精确类型名等值；禁止 isinstance
declared_usable = isinstance(declared, str) and bool(declared.strip())
if not declared_usable:
    verdict = "NOT_JUDGED_declaration_unusable"     # judged = False，且不是 mismatch
else:
    declared_ok = (type(exc).__name__ == declared)
    if not type(exc) is ModelRegistryError:  -> FAIL_wrong_exception_type
    elif not declared_ok:                    -> FAIL_declared_expectation_mismatch
    else:                                    -> PASS_rejected
```
**禁止退回 `isinstance`**：`ModelRegistryError` 是 `ValueError` 的子类，用 isinstance 会让
`expected="ValueError"` 的篡改静默通过（M17 r3 已实测该反例 → rc=3）。

---

## §3 正例预期（每批）

| 编号 | 预期 | 依据 |
|---|---|---|
| P-1 | **Arm E**（新 runner + 未篡改的冻结 cases.json 副本）→ **rc = 0**、`verdict = pass`、全部负例 `PASS_rejected`、`declared_expectation_mismatch = 0` | 新增门不得对现存 31 张卡产生假红；`b5_scan.json` 实测 347 例的 `expected` 全为裸类型名 `ModelRegistryError` |
| P-2 | 未篡改运行下 `declared_expectations_in_cases_json` 恰为 `['ModelRegistryError']`（该批） | 同上 |

---

## §4 负例预期（每批，**预期先冻结**）

| 编号 | 臂 | 篡改（只作用于本 attempt 的 scratch 副本） | 预期 rc | 预期判定 | 失败即意味着 |
|---|---|---|---|---|---|
| N-1 | **F** 变异臂（本卡交付物） | 该批**首个**负例的 `expected` 改成 `"ValueError"`（该例仍抛 `ModelRegistryError`） | **3** | `declared_expectation_mismatch ≥ 1`、该例 `FAIL_declared_expectation_mismatch` | 新比较**未真正开火** ⇒ 推广无效 |
| N-2 | **B** 惰性对照 | 与 N-1 **同一** 篡改后的 cases.json，但跑**旧**（未打补丁、逐字节复制的）runner | **0** | 全部负例仍 `PASS_rejected` | 旧 runner 本来就已开火（则本卡前提不成立）；或旧 runner 返回非 0（则对照无效） |
| N-3 | **G** rc 归类臂（前置 ③） | 该批**同一**负例的 `expected` 键**整键删除** | **2** | `verdict = no_verdict`；reason 指明该例声明缺失/不可用；该例**不得**计入 mismatch | 冻结码表 `rc=2` 未落地 ⇒ 前置 ③ 未闭合 |
| N-4 | 边界 | 三个臂对**同一批**使用同一份 code_root 与同一解释器 | — | 只有 runner 版本与 cases.json 内容不同 | 对照不可比 |

**为什么 N-1 用 `ValueError` 作诱饵**：`ModelRegistryError` 是 `ValueError` 的子类。
`isinstance` 判定会**放过**该篡改（这正是 T1-8 a20260920-03 量化的"伪造的绿"：
rc=0 且 11/11 `PASS_rejected`）；**精确类型名等值**必定抓住它。故该臂同时检验
"新门存在"与"新门没有退回 isinstance"。

**为什么必须有 N-2**：T1-8 的交接项 `T1-8-pre1b-H2` 明确要求把验收判据改述为
"观察 rc=3"而不是"观察 rc=0"，并警告在 isinstance-only 世代上该臂**不会开火**。
N-2 正是该警告的实测对照：**旧 runner 必须仍然 rc=0**，否则说明"未推广的代价"不成立。

---

## §5 REM-22 的预期（附录动作）

| 编号 | 预期 |
|---|---|
| R-1 | `START_HERE.md` 的**冻结码表节原文逐字不变**（追加而非改写） |
| R-2 | 追加的实测节含**全部 8 个批次**的 runner sha256 与码位 `file:line` |
| R-3 | 三处历史偏差（M01–M04 / M05–M08 / M21–M24 的 `2` 且无 `rc=1`）登记为 **legacy、不回改**，并给出映射 |
| R-4 | 追加为**纯追加**：`difflib` 仅 `equal`+单次 `insert`，删除 0 行；前像逐字节保存在后像前缀中 |
| R-5 | 任何历史 rc、历史证据字节数**零改动** |
| R-6 | `M25–M28` 已含真正 `rc=1`，**不得**与上述三批混为一类（更正流传说法） |

---

## §6 本卡**不**主张

1. 不主张任何历史卡的 formula / disclosure_adaptation / accuracy 资格发生变化。
2. 不主张被推广的 runner 已被独立 reviewer 接受——本卡交付 `handoff.json.status = review_pending`。
3. 不主张 `rc=2` 判据措辞的歧义已由本卡消解（§REM-22 只**登记**，消歧须 owner 另行裁定）。
4. 不主张 M17–M20 之外任何批次的**其他**品质（如声明一致性机制等价性）已被评估。
5. 不主张 `5307d2cc…` 与 `94619a98…` 之间曾发生内容回退；只主张前者是**被取代的世代值**。

---

## §7 已知残留与未验证项（不得当已证）

1. `5307d2cc…` 对应的**具体字节内容**在本机已不存在（无任何文件命中该 sha256）。
   本卡只能证明"它被 r3 判定取代"，**不能**证明它当时等于哪一份内容。
2. 六批 runner 的**声明一致性机制的等价性**未作评估；本卡只新增逐例精确类型名闸门。
3. 变异臂在**本 attempt 的 scratch 副本**上运行，不重跑任何历史卡的测量流水线；
   因此本卡不产生任何历史 `run_result.json` 的新版本。
4. 各批 runner 与 `cases.json` 的**互锁关系**（如 M25–M28 的 `case_contract`）未逐一形式化：
   本卡按 T1-11 只改副本、不重冻。
5. 判据若被读成"负例被正确拒绝 ⇒ rc=2"，会与参考实现冲突（参考实现在该情形发 rc=0）。
   该歧义已登记，未消解。

---

## §8 失败判据（出现任一即本卡不通过）

- 任一臂的 rc 取自推断而非真实进程退出码；
- 任一历史 attempt 目录被写入一个字节；
- 任一历史 rc 被回改；
- N-1 未开火（rc ≠ 3）或 N-2 意外开火（rc ≠ 0），且未在 `open_issues` 中如实登记；
- `START_HERE.md` 的追加不是纯追加（删除行 > 0 或冻结正文被改写）；
- 实现者自签 accepted。

---

## §9 ERRATUM 1（追加节；**§4 的 N-2 行已过时，以本节为准**）

按 T1-12 采纳的追加形态登记：**§4 表格中 N-2 行对 arm B 的"预期 rc = 0"是一个被实测证伪的预测**，
本节取代该行的预测部分；N-2 的**作用**（惰性对照）不变。

**证伪来源**：M21-M24 worker 实测其历史 runner 在 `expected` 被改成 `"ValueError"` 后返回
**rc = 3**，与 §4 的预测不符。编排层在历史字节上直接复核并独立确认：

| 批次 | 历史 runner 已有的逐例闸门 | 证据 |
|---|---|---|
| **M09-M12** | `entry["raised_matches_expected_name"] = (entry["raised"] == case["expected"])`；判决 `elif is_target and entry["raised_matches_expected_name"]: PASS_rejected` | `M09/a20260919-01/scripts/run_card.py:427`、**`:430-431`** |
| **M21-M24** | `entry["expected_type_matches_raised"] = (entry["raised"] == case["expected"])`；判决 `elif not entry["expected_type_matches_raised"]: FAIL_expected_type_mismatch` | `M21/a20260919-01/scripts/run_card.py:304`、**`:312-313`** |

两处均为**精确类型名等值**（`entry["raised"]` 由 `type(exc).__name__` 赋值），即这两批
**本来就已符合** REM-21 要推广的语义。

**§4 N-2 的更正判据（取代原预测）**：

> Arm B 的 rc 是**实测值，不是预测值**。`rc = 0` ⇒ 历史 runner **未**开火（即"伪造的绿"）；
> `rc = 3` ⇒ 历史 runner **本来就会开火**。**两者都是合法结论**，不得为迁就预测而调整实测值。

**更正后的 REM-21 实际范围**（六批中）：

| 批次 | 推广前是否已有逐例闸门 | 本卡动作 |
|---|---|---|
| M05-M08 | **无** | 新增闸门（真推广） |
| M09-M12 | **有**（`:430-431`） | 仅补 rc=2 声明可用性优先级与 §2 计数/字段 |
| M13-M16 | **无**（只有集合级声明缺口语义检查） | 新增闸门（真推广） |
| M21-M24 | **有**（`:312-313`） | 仅补 rc=2 声明可用性优先级与 §2 计数/字段 |
| M25-M28 | **无**（只有整集 `case_contract` 闸门） | 新增逐例闸门（真推广） |
| M29-M31 | **无** | 新增闸门（真推广） |

⇒ 授权范围内的六批中，**四批真缺闸门、两批本来已合规**。owner 简报"只有 M17–M20 比较 `expected`"
**属过度概括**；"四批"这一**计数**恰好与实测的非合规批数一致，但**批次标签不同**。

**判据工具本身的更正（本卡自曝缺陷，一并登记）**：
`evidence/b5_scan.json` 的 `compares_raised_to_expected` 标志**不可靠**（对全部 8 批均为 `false`，
连参考实现 M17-M20 也判错）。已由 `evidence/ast_gate_analysis.json` 取代——该 AST 分析
**自带正对照（M17-M20 ⇒ L3 true）与负对照（M29-M31 ⇒ L3 false）并通过**（`_selftest.PASS = true`）。
教训与 `T1-8/a20260920-03` 自己的附注同族：**一个恒返回 false 的判据与一个正确判据在正样本上不可区分**。

**§4 其余各行（N-1 rc=3、N-3 rc=2、N-4）不变。** 本节的追加不修改本文件任何既有字节。
