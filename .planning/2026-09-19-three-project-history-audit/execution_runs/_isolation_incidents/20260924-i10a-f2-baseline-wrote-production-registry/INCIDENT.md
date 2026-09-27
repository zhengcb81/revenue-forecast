# INCIDENT — 测试基线运行向生产仓 `publications.jsonl` 追加 5 条（未授权生产写）

- **incident_id**: `20260924-i10a-f2-baseline-wrote-production-registry`
- **severity**: **P2 → 待 owner 定夺是否升 P1**（未授权生产写，但落在 gitignore 文件、无被跟踪文件被改）
- **detected_by**: 修卡工位 `I10A-F2-FIX/a20260923-01` **自报**（其 handoff `D-1`，`remediation=BLOCKED`）
- **verified_by**: 父代理（编排层）独立取证 —— 见 §2
- **registered_at**: 2026-09-24
- **status**: **RESOLVED** —— owner 2026-09-24 选定 (a)，已执行；详见同目录 `REMEDIATION_RECORD.md`
- ~~**status**: **OPEN — 待 owner 裁 remediation**（本文件只登记，**未做任何修复**）~~

---

## 1. 发生了什么

修卡工位 `I10A-F2-FIX` 为跑 **I-6 value identity 基线**，**直接在生产仓**执行了 `golden_value_identity.py`。该脚本内部调用产品函数 `run_forecast`，而 `run_forecast` 会向发布登记表追加记录 ⇒ 生产仓的

```
C:\Users\郑曾波\Projects\revenue-forecast\artifacts\registry\publications.jsonl
```

**被追加了 5 行**（工位实测并**主动上报**，未隐瞒；其自述：已证明可安全截断回 60 行，但文件带 **ReadOnly 属性**，其**未擅自清除生产文件的保护位** ⇒ 自判 `remediation=BLOCKED`，交 owner/reviewer）。

**根因**：基线运行**应当在隔离副本（iso）内跑**，而该次跑在了生产树上。这是**测试面与生产面的边界违反**，不是产品缺陷。

## 2. 父方独立取证（2026-09-24，脚本 `_pwf_tmp/forensic_d1.py` + `verify_truncation_safety.py`）

| 检查 | 实测 |
|---|---|
| 文件行数 | **65 行**（应为 60） |
| 文件字节 / sha256 | **50229 B** / `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55` |
| 是否被 git 跟踪 | `git ls-files --error-unmatch` **rc=1**（未跟踪） |
| 是否 gitignore | `git check-ignore -v` **rc=0 → `.gitignore:16:artifacts/`** ✓ |
| 带 `2026-09-24T20:02` 的行 | **index 60–64，恰 5 条** |
| 这 5 行 `registered_at` | `20:02:50.848835` → `20:02:51.036956`（**全落在 190 ms 内** = 单次命令连写） |
| JSON 可解析 | **5/5 OK**（`engine_version=4.1.0`、`artifact_type=forecast`） |
| `artifact_id` | **5 条全为 `null`** |
| `line_sha256` | 5 条全 present |
| 只读属性 | **True**（`st_file_attributes & 0x1`）—— 正是挡住工位修复的属性 |
| **被跟踪文件被写？** | **无** ⇒ `git diff HEAD --name-only` 非 `.planning` = **0** 成立（多轮复测一致） |

**结论**：**产品仓工作树被改，但只改在 gitignore 文件上；版本控制层零污染。**

## 3. ⚠️ 截断安全性：**父方无法独立证明**（这是本记录最重要的一句）

工位称「iso 前 60 行字节相同 ⇒ 可安全截断」。父方**独立复核未通过**：

- 计划内 `publications.jsonl` 候选引用 **105 个**，**没有任何一个与生产文件前 60 行字节相符**（`verify_truncation_safety.py` 匹配列表为空）。
- 即 **找不到可信的 pristine 基准**，因此 **「截断即复原」这一说法目前无独立证据支撑**。
- 旁证：计划内 `WC-4-RC120/.../iso/rf/artifacts/registry/publications.jsonl` = **52545 B**，**比生产文件（50229 B）更大** ⇒ 各 iso 快照取自不同时点/不同树，**不能直接当前像**。

**因此**：本记录**不建议**、也**未执行**任何截断。按「**声称不得多于方法所能支持**」，该决定交 owner。

## 4. 可供 owner 决策的事实（不含建议）

**支持截断的事实**：
- 5 行时间戳**连续且落在 190 ms 内**，形态与单次 `run_forecast` 追加一致；
- **`artifact_id` 全为 `null`** ⇒ 按 id 引用它们的下游（若有）本就取不到；
- 文件被 `.gitignore:16` 覆盖 ⇒ 不进版本控制，截断不影响任何提交/推送；
- 尾 5 行是**连续尾块**，截断即去尾，不产生空洞。

**反对截断（或要求先补证）的事实**：
- **无 pristine 基准** ⇒ 无法证明「60 行」就是事故前状态（也许事故前已是 62 行？**没有证据**）；
- 这是**产品自身的发布登记表**，删除记录属于**改动产品数据**，与「生产零未授权改动」是**同一类动作**，只是方向相反；
- 文件带 **ReadOnly**，清属性本身就是一次生产文件元数据改动。

**可选处置**（供选择，父方未择一）：
- **(a)** 清 ReadOnly → 截断至 60 行 → 记录前后 sha（**复原事故态**）
- **(b)** 保留 5 行 → 在本 incident 内登记其 sha 与出处，作为**已披露的生产态偏差**长期在案（**不复原**）
- **(c)** 先补证（找/建 pristine 基准，或由 owner 提供事故前状态）再择 (a)/(b)

## 5. 本记录的边界

- 本 incident **只登记，未修复**：目标文件**字节未动**、ReadOnly **未清**、`git` 零写操作、未联网。
- **未改变任何卡的 status**、**未代签**；`I10A-F2-FIX` 仍 `review_pending`，其 D-1 仍 `remediation=BLOCKED`。
- 目标文件当前 sha **`18310fae…` / 50229 B / 65 行**（父取证时点），任何后续动作前后都应复算比对。
- 与既有纪律事件同族：`20260924-i00a-errata-capture-inside-filing-fetch`（N1）、`20260920-precommit-stash-production-rollback`。⇒ **本轮已是「测试面写进生产面」的第 2 例**，两例都源于**取证/基线运行没有强制隔离在 iso 内**。

## 6. 关联

- 源披露：`execution_runs/I10A-F2-FIX/a20260923-01/handoff.json` 的 `D-1`（51834 B / `00ae453b05a78435…`）
- 事故目录：`execution_runs/_isolation_incidents/20260924-i10a-f2-baseline-wrote-production-registry/`
- 取证脚本（父，只读）：`.planning/_pwf_tmp/forensic_d1.py`、`verify_truncation_safety.py`
- 待办：owner 裁 §4 的 (a)/(b)/(c)；登记册对应行由父随 PWF 折入
