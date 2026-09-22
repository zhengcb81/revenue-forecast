# decision.md — B5+B6（REM-21 跨批 runner 推广 / REM-22 rc 码表冻结）

- **Card**: B5+B6 · **Attempt**: `a20260921-01` · **Status**: `review_pending`（实现者不得自签）
- **Authority**: `OWNER_DECISIONS.md` §13 **T1-8**（REM-21）、**T1-19**（REM-22），TIER-1；
  另引 §5.3、§7.2、§8.12。

本文件记账本卡的**判断与事实**，不是裁决。凡属他方专业裁判者（独立 reviewer），本卡只交付证据。

---

## D-1 REM-22 的实际处置：**冻结正文已存在，本卡只做追加与实测登记**

开工时 `execution_v2/START_HERE.md` **已含**冻结码表节（`## rc 码表（冻结；owner 裁定 T1-19 / §13）`，
前像 `1bdfbd91…` / 9895 B）。该节的落盘**早于**本卡，已由 `T1-19/a20260920-01` 独立验证并留档
（其 `handoff.json.verification_summary.overall = PASS`，并记 `F-T19-5`：其中的推广前置尚未执行）。

**判断**：按 T1-12 采纳的统一规则「今后一律采用**追加新节**形态」，本卡**不重写、不就地编辑**该节，
而是追加一个新的、明确标记的实测登记节。

**实测证据**（`evidence/start_here_append_proof.json`）：

| 项 | 值 |
|---|---|
| 前像 sha256 / 字节 | `1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835` / 9895 |
| 后像 sha256 / 字节 | `e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557` / 16314 |
| `difflib` opcodes | `['equal', 'insert']`（唯一非 equal 为单次尾部 insert） |
| 增 / 删行 | **74 / 0** |
| 冻结正文原句逐字存活 | `true`（9 条锚句全部命中） |
| `APPEND_ONLY` | **true** |

---

## D-2 冻结码表的**实测**码位登记（本卡新增的事实）

对 8 个批次 runner **全量复算** sha256 并逐一定位码位分支（`evidence/b5_scan.json`、
`evidence/rc_return_paths.json`）：

| 批次 | runner sha256（前 12） | 实测 rc 集合 | rc=1 是否存在 |
|---|---|---|---|
| M01–M04 | `b5fcc68563f5` | 0 / **2** / 3 | **否** |
| M05–M08 | `fd3a11c9226a` | 0 / **2** / 3 | **否** |
| M09–M12 | `997c553b0b9e` | 0 / 1 / 2 / 3 | 是 |
| M13–M16 | `9e4a6450d6ab` | 0 / 1 / 2 / 3 | 是 |
| M17–M20 | `94619a98f576` | 0 / 1 / 2 / 3 | 是 |
| M21–M24 | `a5ee7599c37e` | 0 / **2** / 3 | **否** |
| M25–M28 | `eab0116220df` | 0 / 1 / 2 / 3 | 是 |
| M29–M31 | `9ea69c72dced` | 0 / 1 / 2 / 3 | 是 |

**结论（三处更正流传说法，均只登记、不回改）**

1. §5.3 / §13 T1-19 记「M05–M08 用 `2 = harness`」——**成立**，但其 runner **自述**为
   「harness/簿记**无法给出裁决**」（`M05/…/run_card.py:18-19`），不是"runner 自身出错"。
2. 同形态的批次**不止 M05–M08**：**M01–M04**（`M01/…/run_card.py:251-255`，自述
   `harness_incomplete`）与 **M21–M24**（`M21/…/run_card.py:384-389`，自述同 M05）**也未发出 rc=1**。
   原简报只点了 M05–M08。
3. **M25–M28 不应与上述三批混为一类**：它**已有真正的 rc=1**
   （`M25/…/run_card.py:168`、`:466`，自述 `:18`「an unguarded harness defect raised (fail loud)」），
   其码表**已经**与冻结码表一致。

⇒ 跨批聚合的真实风险面是 **M01–M04 / M05–M08 / M21–M24 三批**：它们的 `2` 同时承担
"冻结 `2`（无裁决）"的角色，且**冻结 `1`（harness 失败）在该三批不可达**；
聚合方**不得**据"未见 rc=1"推断"无 harness 失败"。

---

## D-3 参考 runner sha256 的更正：`5307d2cc…` → `94619a98…`

**问题**：§7.2 与 §13 T1-8/T1-12 把待推广的参考实现记为 runner sha256 `5307d2cc…`。
本卡全量复算 **68 份** `run_card.py` 副本后确认：**该 sha256 在本机不存在任何命中的文件**。

**根因（可逐条核对）**：`5307d2cc…` 是 reviewer **r2 世代**的记录
（`execution_runs/M17/a20260919-01/review.md:162`「runner sha256 由 `9ea69c72…` 变为 `5307d2cc…`」、
`:339`、`:348`），**已被同一 reviewer 自己的 r3 判定取代**：

| r3 原文位置 | 内容 |
|---|---|
| `review.md:409` | 「M17–M20 修复后 runner sha256 = **`94619a98…`**」 |
| `review.md:422` | 「我自造臂复现（**新 runner `94619a98…`**）」 |
| `review.md:518` | 「**不改 `run_card.py` 一个字节**，以保持 reviewer 已验证的 runner sha `94619a98…` 不变」 |

**四卡自带证据一致记为 `94619a98…`**：`handoff.json:30,239`、
`after/final_deliverable_hashes.json:880`、`evidence/M17/evidence_hashes.json:134`、
`after/hash_table_verification.json:68`。

**裁定（本卡职权内的事实更正，非专业裁决）**：

- 权威参考值 = **`94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252`**（36744 B）；
- `5307d2cc…` **不回改**，作为 **superseded** 值保留并登记（T1-21 追加式 provenance 口径）；
- 凡按 `5307d2cc…` 登记过的命名空间/交接文本，一律以本更正为准（本卡已在 START_HERE 追加节登记）。

**残留（如实声明）**：`5307d2cc…` 当时对应的**具体字节内容**在本机已不可考——本卡只能证明
"它被 r3 判定取代"，**不能**证明它等于哪一份内容，也不主张曾发生内容回退。

---

## D-4 前置四项的逐项核验（REM-21 开工门）

| # | 前置 | 状态 | 依据 |
|---|---|---|---|
| ① 不退回 `isinstance` | **满足** | 参考实现 `type(exc).__name__ == declared`（`M17/…/run_card.py:458`）；本卡另加 **Arm B 惰性对照** 与 `ValueError` 诱饵（`ModelRegistryError` 是 `ValueError` 子类）实测 |
| ② 登记「`expected` 只能是裸类型名」 | **满足** | 已由 START_HERE 冻结节登记（`:113-115`）；本卡**实测复核** 31 张卡 `cases.json`：**347 例，复合写法 0、缺失 0、非字符串 0**（`evidence/b5_scan.json`） |
| ③ 先修 rc 归类与「期望缺失」口径 | **满足（由参考实现闭合）** | 参考实现：声明不可用 ⇒ `rc=2`（`no_verdict`，**先于**逐例判定，`:540-544`）；声明不符 ⇒ `rc=3`；harness ⇒ `rc=1`。T1-19 的 `F-T19-5` 曾记此项"待办"，本卡以参考实现实测闭合 |
| ④ 逐批按 runner sha256 登记命名空间 | **满足** | 8 批全量复算（D-2 表），写入 START_HERE 追加节 |

**无未满足前置。** 但发现一项**登记层缺陷**（非前置失败）：D-3 的 `5307d2cc…` 幽灵哈希——
它使"按 runner sha256 登记命名空间"这一前置在**文本层**不可核；本卡已更正。

---

## D-5 变异臂验收判据的改述（采纳 T1-8 交接项 `T1-8-pre1b-H2`）

`T1-8/a20260920-03` 的交接项明示：验收判据必须表述为「**观察 rc=3**」而非「观察 rc=0」，
因为在 isinstance-only 世代上「改 `expected`」臂**根本不会开火**——它会继续给出
`rc=0` 且 `11/11 PASS_rejected`，即**伪造的绿**，而不是"缺失的门"。

**本卡据此把每批复核做成四臂**（全部记录**真实进程退出码**）：

| 臂 | runner | cases.json | 预期 rc | 作用 |
|---|---|---|---|---|
| E | 新 | 冻结副本 | **0** | 假红对照：新门不得对现存 347 例产生假红 |
| **F** | **新** | 首个负例 `expected` → `"ValueError"` | **3** | **交付物**：证明新比较真正开火 |
| B | **旧**（逐字节副本） | 同 F | **0** | **惰性对照**：证明旧 runner 确实不开火，即"未推广的代价"成立 |
| G | 新 | 同例 `expected` 整键删除 | **2** | 前置 ③：冻结码表 `rc=2` 落地 |

`B` 臂是本卡相对原始简报的**加强项**：简报只要求"变异臂证明比较会开火"；
若无 `B` 臂，"开火"可能被误读为"原来就会红"。`E`+`F`+`B` 三者合起来才构成
"**新门开火、旧门不开火、且未篡改时仍绿**"的完整对照。

---

## D-6 已登记的规范性歧义（**只登记，不改正文**）

冻结码表 `rc=2` 的判据原文含「用例是负例且**业务上被正确拒绝**」。

- 该表述是**逐例**口径；rc 是**逐次运行**口径。
- 参考实现在**全部负例被正确拒绝**时发 `rc=0`（`M17/…/run_card.py:549`），
  只有"冻结期望本身不可用/缺失"才发 `rc=2`（`:540-544`）。
- ⇒ 聚合方**不得**把「负例被正确拒绝」读成 `rc=2`。

按 T1-12 追加纪律与 T1-19「不回改历史 rc」，本卡**不修改正文**，只在 START_HERE 追加节
第四节**登记**该歧义。消歧需 owner 另行裁定。

---

## D-7 边界与执行纪律

| 项 | 值 | 证据 |
|---|---|---|
| 历史 runner 副本（67 份可按卡归属 + 1 份批次级 iso）sha256 | **0 处不符** | `evidence/boundary_verification.json` |
| 31 张卡 `cases.json` | **0 处改动** | 同上（对 `b5_scan.json` 基线） |
| 历史 M 卡目录内文件**在开工后**被修改 | **0**（扫描 37,323 个文件） | 同上 |
| 生产仓 `scripts/model_registry.py` | `9ec6529550f189a4…`（锚定值，未变） | `binding.json` |
| 生产仓 `scripts/model_extensions.py` | `9939480b717d5a49…`（锚定值，未变） | `binding.json` |
| 历史 rc 回改 | **0** | 本卡只写自己的 attempt 目录与 START_HERE 追加节 |
| 状态转移 / 自签 | **0** | `handoff.json.status = review_pending` |

**注**：生产工作树在本卡开工前即有**既有**改动（`assurance/unified_completion/manifests/plan_inputs.json`、
`.tmp-r41-mutation/` 等），**非本卡产生**；本卡对生产树零写入。

---

## D-8 未决 / 交 reviewer

1. 六批被推广 runner 的**代码正确性**与**是否真正等价于参考语义**——须独立 reviewer 复核，
   不得由本卡自证。
2. D-6 的 `rc=2` 措辞歧义是否需 owner 消歧。
3. `5307d2cc…` 的字节内容不可考（D-3 残留）——是否需要更强的考古动作由 reviewer/owner 决定。
4. 本卡**不**主张任何历史卡资格变化，**不**主张被推广 runner 已获接受。

---

## D-9 【重要更正】REM-21 的实际范围：六批中**只有四批**真缺闸门

### D-9.1 触发

M21-M24 worker 在执行 **arm B**（历史 runner + 被篡改的 `cases.json`）时实测得 **rc = 3**，
与 `PROPAGATION_CONTRACT.md` §5 预测的 rc=0 **不符**。编排层在历史字节上直接复核，确认该 worker 正确。

### D-9.2 复核结论（直接读历史代码）

| 批次 | 历史 runner 是否**已有**逐例精确类型名闸门 | 证据（`file:line`） |
|---|---|---|
| **M09-M12** | **已有** | `M09/a20260919-01/scripts/run_card.py:427` 计算 `raised_matches_expected_name`；**`:430-431`** `elif is_target and entry["raised_matches_expected_name"]: PASS_rejected` |
| **M21-M24** | **已有** | `M21/a20260919-01/scripts/run_card.py:304` 计算 `expected_type_matches_raised`；**`:312-313`** `elif not ...: FAIL_expected_type_mismatch` |

两处的 `entry["raised"]` 均由 `type(exc).__name__` 赋值 ⇒ 是**精确类型名等值**，不是 isinstance。
⇒ 这两批**本来就已经符合** REM-21 要推广的语义。

### D-9.3 判据工具自身的缺陷（本卡自曝）

`evidence/b5_scan.json` 的 `compares_raised_to_expected` 标志**不可靠**：对**全部 8 批**均为 `false`，
**连参考实现 M17-M20 也判错**（其朴素正则 `raised\w*\s*==` 无法跨越 `entry["raised"] == ...` 中的 `"]`）。

已由 `evidence/ast_gate_analysis.json` 取代。该 AST 分析**自带对照并通过自我检验**：

| 对照 | 批次 | 期望 L3 | 实测 L3 |
|---|---|---|---|
| 正对照 | M17-M20 | `true` | `true` |
| 负对照 | M29-M31 | `false` | `false` |

`_selftest.PASS = true`。**教训**（与 `T1-8/a20260920-03` 自己的附注同族）：一个恒返回 false 的判据
与一个正确判据，**在正样本上不可区分**；判据必须同时对**正样本**与**负样本**测试。

### D-9.4 更正后的范围（六批）

| 批次 | 推广前 | 本卡动作 | 性质 |
|---|---|---|---|
| M05-M08 | 无闸门 | 新增逐例闸门 | **真推广** |
| M09-M12 | **已有闸门** | 仅补前置③（rc=2 声明可用性优先级）与 §2 计数/字段 | 合规性补齐 |
| M13-M16 | 无逐例闸门（仅集合级声明缺口语义检查） | 新增逐例闸门 | **真推广** |
| M21-M24 | **已有闸门** | 仅补前置③与 §2 计数/字段 | 合规性补齐 |
| M25-M28 | 无逐例闸门（仅整集 `case_contract` 闸门） | 新增逐例闸门 | **真推广** |
| M29-M31 | 无闸门 | 新增逐例闸门 | **真推广** |

**对 owner 简报的更正**：§7.2 / §13 T1-8 称「M05–M16 / M21–M31 各批的"逐例拒绝语义"仍无自动门」，
并称参考实现是「**唯一**精确类型名」。实测：**M09-M12 与 M21-M24 也已有该门** ⇒「唯一」不成立。
「**四批**」这一**计数**与实测的非合规批数（M05-M08 / M13-M16 / M25-M28 / M29-M31）**恰好一致**，
但简报所隐含的**批次标签**与实测集合不同。本卡**不改** owner 文本（T1-12 追加纪律），只在此登记。

**注**：M09-M12 与 M21-M24 的改动仍在 owner 授权范围内——owner 明列的四项前置中，
**前置③「先修 rc 归类与『期望缺失』口径」是必须满足项**，这两批的 delta 正是落地前置③
（此前它们**没有**"声明不可用"这条路径，`rc=2` 原本只表示"正例抛错"）。

### D-9.5 arm B 判据的更正（**取代** `oracle.md` §4 的 N-2 预测行）

> Arm B 的 rc 是**实测值，不是预测值**。`rc = 0` ⇒ 历史 runner **未**开火（"伪造的绿"）；
> `rc = 3` ⇒ 历史 runner **本来就会开火**。**两者都是合法结论**；不得为迁就预测而调整实测值。

已同步追加到 `PROPAGATION_CONTRACT.md` §8（Erratum 1）与 `oracle.md` §9（Erratum 1），
并按 T1-12 形态标注"§4 的 N-2 行已过时，以本节为准"。**两处均为追加，未改写既有字节。**

---

## D-10 M25-M28：arm B 出现**第三种**行为（rc=1），并暴露一处冻结件内的锚冲突

### D-10.1 第三种 arm B 行为

M25-M28 worker 实测 arm B（历史 runner + 单例 `expected` 被改）返回 **rc = 1**，
既不是预测的 `0`，也不是 M21-M24 的 `3`。

**根因（该 worker 定位）**：历史 M25-M28 runner 的**整集** `case_contract` 闸门
（`run_card_before.py:140-168`，`wrong_declaration` → `contract_problems` → `return 1`）
在**任何逐例判定之前**就以 rc=1 中止。⇒ 该批**有**保护，但保护形态不同。

**两个后果（均为本卡新登记的事实）**：

1. **该闸门只是部分有效**：它按"整集必须声明同一值"判据，故能抓住**单例**篡改，
   却对**整批**篡改失明。M29-M31 的 `H_blanket` 臂（全部 11 例改成 `"ImportError"`）
   在同类世代上实测仍为 **rc=0** ⇒ 整集判据**不能**替代逐例判据。
2. **rc 归类存疑**：按冻结码表，"声明期望不符"属**未达预期**（rc=3），
   而"runner 自身出错"才是 rc=1。历史实现把"用例声明集自相矛盾"当作 **harness 缺陷**（rc=1）。
   本卡**只登记、不回改**（该行为已烧进历史 rc 归档）。

### D-10.2 冻结件内的锚冲突（**报告，不修改**）

M25-M28 的**冻结** `cases.json` 携带 `case_contract.rule` 文本，其内容为：
声明不同的 `expected` 使 harness **"refuse to issue a verdict (rc=1)"**。

该冻结文本**同时**与两处冲突：
- 与**冻结 rc 码表**冲突（声明不符 ⇒ rc=3，不是 rc=1）；
- 与 **REM-21 的强制形态**冲突（须**逐例**判、且 mismatch ⇒ rc=3）。

消解它需要编辑冻结件，而 **T1-11 明令 M25-M28 冻结件自此只许追加**（`case_contract` 与
`scripts/run_card.py` 为**互锁对**，改任一方须整体重跑重冻并记为新 rN）。
⇒ 本卡**不动**该文本，登记为需 reviewer/owner 裁定的锚冲突。

> 若 owner 认定"单例声明不同"确属 fixture 缺陷（rc=1 合理），则 REM-21 推广在 M25-M28
> 需改为"合并语义"；若认定属逐例判定（rc=3），则该冻结 `rule` 文本须追加更正。
> **两种读法都改变 M25-M28 的对外契约**，故不由实现者代裁。

### D-10.3 变更目标歧义的实测无害性

合同 §5 的"第一个负例（最低 id）"在 id 混用连字符与字母时**自相矛盾**：
ASCII `'-'`(0x2D) < `'0'`(0x30) < `'A'`，故 `sorted(ids)[0]` 是 `CONT-BREAK`，
而文件顺序给出 `NEG-CARD`。**本卡自曝该措辞缺陷**（合同 §5/§6 双重表述不自洽）。

M21-M24 worker 用 `F2`/`B2` 两臂**实测两种读法**，rc **完全相同**（3/3）⇒
该歧义**不可能改变任何结果**。各批按合同**主条款**（冻结数组顺序）取值，并各自登记所选 id。

### D-10.4 本卡**未**触发 T1-11 的 `case_contract` 互锁（关键澄清）

T1-11 警告：M25-M28 的 `case_contract` 与 `scripts/run_card.py` 是**互锁对**，
改任一方都会使 `cases.json` / `run_result.json` 的哈希失效，**必须整体重跑重冻并记为新 rN**。

**本卡不触发该互锁**，理由：
- 互锁描述的是**该批自己的历史 attempt 内**那一对文件的一致性；
- 本卡**未改**历史 attempt 内的任何一方（`cases.json` 与 `scripts/run_card.py` 均逐字节不变，
  由 `evidence/boundary_verification.json` 的 68/68 + 31/31 复核证明）；
- 本卡改的是**本 attempt 目录内的新副本**，它是一份**新工件**，不是对历史冻结件的重冻，
  也不取代任何历史 `run_result.json`。

⇒ 历史 `cases.json` / `run_result.json` 的哈希**依然有效**；本卡的副本与之**并存**。
唯一残留的是 **D-10.2 的锚冲突**（冻结 `case_contract.rule` 文本的措辞与新副本行为不符），
该冲突**只影响可读性/对外契约表述**，不影响任何历史哈希的有效性。

---

## D-11 【核心实测结论】arm B 出现**四种**互不相同的行为 —— 简报的单一叙事不成立

把 arm B 当作**测量**（而非预测）后，六批的历史 runner 对**同一份**"单例 `expected` → `ValueError`"
篡改，给出了**四种**不同反应。这是本卡最有价值的一手事实：

| 批次 | arm B 实测 rc | 历史 runner 的机制 | 是否读了**实际抛出的异常** | 判定 |
|---|---|---|---|---|
| **M05-M08** | **0** | **无任何声明闸门**；判决只由 `isinstance(exc, ModelRegistryError)` 决定 | 是（但只比类型归属，不比声明） | **真正的"伪造的绿"** |
| **M29-M31** | **0** | 同上（无声明闸门） | 同上 | **真正的"伪造的绿"** |
| **M09-M12** | **3** | **逐例精确类型名闸门**（`:427` + `:430-431`） | 是，且比声明名 | **本来已合规** |
| **M21-M24** | **3** | **逐例精确类型名闸门**（`:304` + `:312-313`） | 是，且比声明名 | **本来已合规** |
| **M13-M16** | **2** | **集合级 blanket 比较**（`:189-192/200`，`declared != TARGET_EXCEPTION` → `gaps`） | **否** —— 从不读抛出的异常 | 有保护但**不给裁决**（rc=2） |
| **M25-M28** | **1** | **整集 `case_contract` 中止**（`:140-168` → `return 1`） | **否** | 有保护但**当 harness 缺陷**（rc=1） |

### D-11.1 四条结论

1. **"未推广的代价"只对两批成立**：只有 **M05-M08 与 M29-M31** 是简报所说的那种
   "改 `expected` 后仍 rc=0"的**伪造的绿**（M05-M08 已由本卡四个卡逐一实测；M29-M31 另加
   `H_blanket` 臂复现历史 reviewer 的 P2 实验，全 11 例 → `ImportError` 仍 rc=0）。
2. **两批本来已合规**（M09-M12、M21-M24）——「参考实现是**唯一**精确类型名」不成立（见 D-9）。
3. **两批有保护但归类不同**：M13-M16 发 **rc=2**（无裁决），M25-M28 发 **rc=1**（harness 缺陷）。
   二者都**不读实际抛出的异常**，故都**不是**逐例声明强制；且按冻结码表，
   "声明不符"应为 **rc=3**（未达预期），故这两批的历史归类**与冻结码表不一致**。
4. ⇒ 跨批聚合若假设"arm B 恒为 rc=0"，会在 **4 个批次**上得出错误结论。
   这正是本卡把 arm B 从"预测"改为"测量"的直接价值。

### D-11.2 M25-M28 的**被迫**设计偏离（已登记，需 reviewer 裁定）

M25-M28 worker 报告并实测：**若保留**整集 `case_contract` 的 rc=1 中止，
则 **arm F 不可能成立** —— 被篡改的首例在任何逐例判定之前就触发整集闸门。

⇒ 该批把闸门**一分为二**：**结构类**问题（用例数/id 集不符）仍驱动 rc=1（不变）；
**整集声明不一致**改为**记录但不驱动 rc**（`case_contract_check.set_level_declaration_violations`）。
逐例闸门随后给出 rc=3。

**判断**：该偏离**由 owner 自己的验收判据强制**——T1-8 明确要求"每批补'改 `expected` ⇒ rc=3'变异臂"；
不解除整集中止，该臂在 M25-M28 上**永远不可能**观测到 rc=3。故偏离是**实现授权目标的必要条件**，
而非实现者的自选。**但它改变了本副本的 rc 归类**（原先 rc=1 的情形现为 rc=3），
并与冻结 `case_contract.rule` 文本冲突（D-10.2）⇒ **须由 reviewer 裁定**，实现者不代裁。
`rc_values_changed_by_this_patch = []`（码值与码名未改，改的是归类路径）。

### D-11.3 M13-M16 的**键重命名**（已声明偏离合同 §2）

合同 §2 要求"不得删除或重命名既有字段"。M13-M16 报告：把既有的
`expectation_consistency.facts.declared_expectations` **重命名**为合同要求的新名
`declared_expectations_in_cases_json`，理由是**同一概念不留两个名字**（M05-M08 同办）。

**判断**：属**已声明的**偏离合同 §2 字面。因历史 attempt 未被触碰，**不影响任何历史哈希**；
但本副本的输出 schema 与该批历史输出**不再逐键相同**。⇒ 交 reviewer 裁定是保留合并名
还是恢复旧名并并存两个键。

### D-11.4 六批 arm 汇总（全部为真实进程退出码）

| 批次 | E | F（交付物） | B（实测） | G | 与合同预期 |
|---|---|---|---|---|---|
| M05-M08 | 0 | **3** | **0** | 2 | E/F/G 符；B 实测 |
| M09-M12 | 待其自报 | 待其自报 | 待其自报 | 待其自报 | 进行中 |
| M13-M16 | 0 | **3** | **2** | 2 | E/F/G 符；B 实测 |
| M21-M24 | 0 | **3** | **3** | 2 | E/F/G 符；B 实测 |
| M25-M28 | 0 | **3** | **1** | 2 | E/F/G 符；B 实测 |
| M29-M31 | 0 | **3** | **0** | 2 | E/F/G 符；B 实测 |

**六批的 E/F/G 三臂全部符合预期**（E=0、F=3 且 mismatch≥1、G=2）；
**B 臂按实测登记，四种取值**。

---
---

# 以下为 **B5-fix-g1a-g3 · attempt `a20260922-01`** 的追加记录

> 本文件第 1–361 行为 B5 attempt（`B5-plan-level-remediation/a20260921-01`）`decision.md`
> 的**原样只读复制**（sha256 与 B5 `handoff.json` 记录一致），以保留完整上下文；
> B5 的 attempt 是**封存证据**，本卡从未写入其中。以下 D-F* 各节是本修复卡自己的判断与实测。

- **Card**: B5-fix-g1a-g3 · **Attempt**: `a20260922-01` · **Status**: `review_pending`（实现者不自签）
- **Authority**: owner 裁定（2026-09-22 逐字）「**D，G1-a**」——G1-a 为本卡 Fix 2 的执行授权；
  G2 的 owner 最终裁定为「**留置**（或给取舍）」，推翻早前"分类优先级勘误"的指示（见 D-F3）。
- **闭环对象**: 独立 reviewer 报告 `B5-plan-level-remediation/a20260921-01/reviewer_report.md`
  的 3 项 BLOCKING（F-1/F-2/F-3）+ 本卡指定的廉价 findings（F-4…F-7）。

---

## D-F1 Fix 1（BLOCKING，F-1/G3）：M13-M16 **双键并存**，并更正 B5 的一项不实声明

**改动位置**：本 attempt `M13-M16/run_card.py` 的 `expectation_consistency.facts` 构造处
（`declared_in_cases = sorted(...)` 一次计算，**同值写入两个键**）：

- `declared_expectations` —— 历史键，名字与含义**原样保留**（下游真实读取方：
  `execution_runs/M14/a20260919-01/recovery/consolidated_report.py:75` 索引该键路径）；
- `declared_expectations_in_cases_json` —— 合同 §2 要求的键名，**追加**而非替换（合同 §2 是
  additive 列表，且合同明文禁止删除/重命名既有字段）。

**实测证明**（`evidence/g3_reader_proof.json`，`PASS=true`）：
从**历史字节**中的 `consolidated_report.py` 里正则提取第 75 行的真实读取表达式
`run["expectation_consistency"]["facts"]["declared_expectations"]`，然后 eval 于：

| 输入 | 结果 |
|---|---|
| 冻结历史 `M14/evidence/M14/run_result.json`（基线） | ✅ 读出 `["ModelRegistryError"]` |
| **B5 补丁 runner 的输出**（B5 `_scratch/M13-M16/E/M14/run_result.json`，只读取） | ❌ **`KeyError: 'declared_expectations'`** —— F-1 断裂被原样复现 |
| 本卡补丁 runner 输出，E/F/G 三臂 × M13–M16（12 份） | ✅ 全部可读，**双键都在且同值** |
| 本卡 arm B 输出（历史 runner 字节副本，4 份） | ✅ 旧键在、新键不在 —— 历史 runner 形态**未被改动**（边界要求） |

**声明更正（登记，不回改他卡）**：B5 实现者曾声称「M05-M08 也做了同样的（重命名）事」——
该说法**不准确**：M05-M08 的 runner **根本没有 `expectation_consistency.facts` 块**，
不存在可重命名的键。**未**在 M05-M08 添加该块（不扩大改动面），仅在此登记更正。

## D-F2 Fix 2（BLOCKING，F-2/G1-a）：M25-M28 集合级闸门的**显式路由**

**设计与落点**（全部在本 attempt `M25-M28/run_card.py`，历史件零改动）：

1. **结构问题**（无 `case_contract`、用例数/id 集不符、未知 id）⇒ **rc=1，原样不变**
   （harness/fixture/file 故障；代码位置：整集闸门的 `if structural_problems: return 1` 分支，
   注释改为说明"值差异永不进入此中止"）。
2. **声明不可用**（`expected` 缺失 / 畸形 / 非非空字符串）⇒ **rc=2 + `no_verdict`**，
   判定源 `unusable_declared` 在**任何用例被判定之前**计算（case 循环之前），最终裁决分支
   `harness_incomplete or not cases_declared_ok or set_level_route_rc == 2` 拥有最高优先级
   ——与冻结 rc 表（START_HERE L90–115）的"该命令不产生裁决"一致。
3. **可用但不同的 `expected`（逐例）** ⇒ **rc=3**：既由逐例精确类型名判定驱动，
   **又**由集合级路由 `set_level_route_rc == 3` 在最终退出码判定中**直接断言**（`set_level_forces_fail`），
   即集合级闸门本身是 load-bearing 的。
4. 集合级闸门状态从 `set_level_declaration_gating: false`（B5 的"记录但不驱动"）
   改为 **`true` + `set_level_declaration_routing` 结构**（路由规则、authority、逐例路由 id、
   `value_difference_never_rc1`、`never_left_nongating`），并在
   `exit_code_semantics` 里输出 `set_level_declaration_route` / `set_level_unusable_case_ids` /
   `set_level_usable_diff_case_ids` / `declaration_usability_decided_before_case_judgment`。
5. 退出码常量**零改动**（本卡只加路由，不新增、不重编号任何 rc）。

**实测**（`_scratch/arms_raw.json`，128 个真实子进程；`evidence/arm_matrix.json`）：

| 臂 | M25 | M26 | M27 | M28 | 判据 |
|---|---|---|---|---|---|
| E 绿对照 | 0 | 0 | 0 | 0 | ✅ |
| **F（owner 强制臂：`expected`→`"ValueError"`）** | **3** | **3** | **3** | **3** | ✅ 路由字段 `route=3`；mismatch=`NEG-CARD`；该臂在 M25-M28 上**历史上不可达** |
| G（删除该例 `expected` 键） | **2** | **2** | **2** | **2** | ✅ `verdict=no_verdict`，reason `cases_json_declared_expectation_missing:NEG-CARD`，`route=2`；**不是 1、不是 3** |
| B（**历史** runner 字节副本 + 同一篡改 cases） | **1** | **1** | **1** | **1** | ✅ 历史行为**原样记录、未改**（整集 `case_contract` 中止） |
| S 结构臂（追加未知 id 用例，新增） | **1** | **1** | **1** | **1** | ✅ 结构 rc=1 **未被路由改动** |

**其余五批回归复测**（同表全部卡片）：E=0 / F=3 / G=2 **全部 19 张卡无回归**；
arm B 与 B5 记录逐一相同（M05=0、M09=3、M13=2、M21=3、M29=0）。

## D-F3 Fix 3：G2 冲突登记 —— **owner 裁定：留置（不裁定优先级）**

> **已知冲突，owner 裁定留置**：M25-M28 冻结 `case_contract.rule` 文本写「不同 `expected` ⇒
> 拒发裁决 rc=1」；冻结 rc 表（START_HERE L90–115）与 G1-a 裁定要求 rc=2/rc=3。
> owner **不裁定哪个冻结件优先**，选择将该冲突**永久留置登记**。本卡实现按 G1-a 路由
> （这是独立的执行裁定）；冲突双方文本**原样共存于册**，T1-11 下不编辑任何冻结件
> （`cases.json`、历史 runner、`before/` 一律不动，由 `evidence/boundary_verification.json` 复核）。

**要点登记**：① **不写**「rc 表优先于 rule 文本」这类优先级断言——owner 明确拒绝了该取舍；
② 只登记冲突存在 + 实现依据是 G1-a 执行裁定；③ 冻结件零编辑。
**本项单列，供父 agent 复核**（见 `report.md` §G2-留置项）。同一登记镜像于 `handoff.json`
的 `g2_conflict_record` 与 `M25-M28/run_card.py` 输出内的 `case_contract_check.frozen_rule_text_conflict`。

## D-F4 Fix 4：F-3 … F-7 处置

| id | 处置 | 证据 |
|---|---|---|
| **F-3** | **已修**：本卡为**六批全部**重建 `evidence.json`，`arms.{E,F,B,G}` 用真实运行填充（`rc`/`rc_per_card`/`verdict`/`mismatch`/`mutated_case`/`note`），机器消费者读 `evidence["arms"][arm]["rc"]` 不再得 `null` | 各 `<batch>/evidence.json` |
| **F-4** | **已登记**：M25-M28 历史上"缺 `expected` ⇒ rc=1"来自**整集 `case_contract` 闸门**（`case.get("expected")` → `None != declared` → `run_card_before.py:140-168` 中止），**不是**硬下标 `KeyError`；无 KeyError、无输出 JSON。结论（rc=1 而非 rc=3）不变。**START_HERE append 2 的原文未被本卡编辑**（本卡无向 START_HERE 追加的授权）——更正载体是本 decision/handoff/report；见"剩余缺口" | `M25-M28/evidence.json` open_issues；arm B 实测 rc=1 ×4 |
| **F-5** | **已登记**：arm G 在 M25-M28 是**第二项语义变更**（历史 rc=1，来自整集闸门、且**符合**冻结码表"期望文件缺失 → rc=1"的字面；补丁后 rc=2 + no_verdict），为 T1-19 跨批统一所必需；与 G1 并列登记 | `M25-M28/evidence.json` open_issues + `g1a_routing` |
| **F-6** | **已登记**：B5 的 M05-M08 变异了 `CONT-BREAK`（文件末例）而非合同的首/最低 id `NEG-CARD`，且 `open_issues` 未声明该偏离。**本卡四臂全部按合同改用 NEG-CARD**，实测 E=0/F=3/B=0/G=2 与 reviewer 独立复跑一致 ⇒ 无结果变化 | `M05-M08/evidence.json`；`arms_raw.json` `mutated_case=NEG-CARD` ×4 卡 |
| **F-7** | **已修**：本卡 `scripts/verify_append_fixed.py` 替换锚句操作数——嵌入**19 条**冻结节全文行（全部 distinct，`len(set)==len` 断言），且断言嵌入表与**从字节验证的冻结前缀实时抽取**的行序列完全相等；逐句按**整行**同时校验前缀与当前文件。链证（PRE/POST1 前缀 sha、单次 insert、+108/−0 与 +34/−0）复跑通过 | `evidence/start_here_append_proof_fixed.json`（`APPEND_ONLY=true`） |

## D-F5 实测臂矩阵（31/31 卡，全部真实子进程 rc）

| 批次 | 卡 | E | F | B | G | S | 备注 |
|---|---|---|---|---|---|---|---|
| M01-M04 | 4 | 0 | **0** | 0 | **1** | — | **超出 T1-8 六批授权范围**：无逐例闸门（F=伪造的绿）、删键崩溃 rc=1；**仅测量、未打补丁**（见"剩余缺口"） |
| M05-M08 | 4 | 0 | 3 | 0 | 2 | — | ✅（NEG-CARD，F-6） |
| M09-M12 | 4 | 0 | 3 | 3 | 2 | — | ✅ |
| M13-M16 | 4 | 0 | 3 | 2 | 2 | — | ✅ + 双键证明 |
| M17-M20 | 4 | 0 | 3 | 3 | 2 | — | ✅ 参考批（字节副本，仅测量） |
| M21-M24 | 4 | 0 | 3 | 3 | 2 | — | ✅ |
| M25-M28 | 4 | 0 | **3** | **1** | **2** | **1** | ✅ G1-a 路由；F 历史上不可达 |
| M29-M31 | 3 | 0 | 3 | 0 | 2 | — | ✅ |

- **六个 REM-21 批次（23 卡）：E=0/F=3/G=2 全部统一、全部符合预期**；加参考批 M17-M20 → **27/31 统一**。
- **"all 31 cards" 口径更正**：M01-M04 不在 T1-8 的六个授权批次内，从未被推广，
  实测 E=0/F=0/B=0/G=1 —— 该四卡**不满足** E=0/F=3/G=2。已向父 agent 上报为范围发现；
  本卡**未**越权修补它们。
- arm B 是**测量**：六个批次与 B5 记录逐一相同（0/3/2/3/1/0），历史行为零改动。

## D-F6 边界复核（`evidence/boundary_verification.json`，OVERALL PASS）

- 68/68 历史 `run_card.py` 字节不变（67 张卡树 + `M05-M08/a20260919-01/iso` 基线），
  批内一致且逐一等于记录的批 sha256；
- 31/31 冻结 `cases.json` 字节不变（347 例，`expected` 全为 `ModelRegistryError`，0 畸形）；
- `START_HERE.md` 自 B5 起零字节变化（== B5 记录的 POST2 `a9cb5a4a…`）——本卡未追加、未编辑；
- `git status --porcelain` 覆盖 `execution_runs/M01..M31`：**0 行**（37323 个历史文件零触碰）；
- 生产锚不变：`scripts/model_registry.py 9ec65295…` / `model_extensions.py 9939480b…`；
- B5 封存 attempt：其 12 个 runner 文件与 5/6 个交付件仍等于 **B5 自己 handoff 里记录的值**
  （写于本卡之前）。**1 处既有不一致被如实报告**：B5 `binding.json` 实际
  `96733875…`/22652 B ≠ B5 handoff 记录的 `06ff8064…`/20819 B —— 系 B5 自身记录问题，
  本卡只读、不修、不回写。

## D-F7 状态

`status = review_pending`；`implementer_signed = false`；**实现者不自签**。
`disclosure_adaptation = unmapped`，`accuracy = unproven`。
下一动作：**独立 reviewer** 复核本修复卡（重点：G1-a 路由三支、双键读取证明、G2 留置措辞、
31 卡臂矩阵与 M01-M04 范围发现）。
