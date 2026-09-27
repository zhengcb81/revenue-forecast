# INCIDENT — I-00-A errata 重采曾把捕获文件写进 filing-fetch 生产仓（瞬时、零残留）

- **incident_id**: `20260924-i00a-errata-capture-inside-filing-fetch`
- **severity**: P2（纪律违反；无数据丢失、无产品行为变更）
- **detected_by**: `I-00-A/a20260919-01` 补裁决独立复审（`reviewer_report.md` §4 **N1**，sha256 `24cf91cffec60e2d…`/19149 B）
- **verified_by**: 父代理（编排层）独立复算 —— **非照抄复审结论**，见下「独立取证」
- **registered_at**: 2026-09-24
- **status**: CLOSED-WITH-RECORD（零残留已实测；本文件 = 纪律事件登记，**不改变任何卡 status、不回改任何既有字节**）

---

## 1. 发生了什么

`I-00-A` 卡的 **errata 重采**（为修复原阻断项 F1「三份 git 证据字节级完全相同、须按各仓重新捕获」）在**重新执行 `git status` 取证**时，输出文件被写到了**被观测仓（`filing-fetch` 生产仓）内部**，而不是卡的 attempt 目录。

后果是：那次 `git status` 的输出里，**它自己**以未跟踪文件的形态出现。

## 2. 独立取证（父代理，2026-09-24）

被指文件：`execution_runs/I-00-A/a20260919-01/git_filing-fetch.txt` —— **127 B**（重采件）；
同目录另有 `git_filing-fetch.wrong-capture.txt` —— **3068 B**（原错误捕获件，按「更名保留」处置，字节未删）。

在 `git_filing-fetch.txt` 内正则命中 `?? git_filing-fetch.txt` = **2 处**：

```
?? git_filing-fetch.txt
?? git_filing-fetch.txt
```

⇒ `?? ` 是 `git status --porcelain` 的**未跟踪**标记。捕获文件出现在**自己那次捕获的输出**里，只有一种解释：**文件在 `git status` 扫描时已经位于该仓工作树内**（或在同一工作树内被先后两次捕获）。这与复审 N1 的判定一致，且本记录的证据来自父方独立复算。

## 3. 当前状态（已实测，非声明）

- **零残留**：复审实测四个候选残留路径全部 `False`；`filing-fetch` 仓 `porcelain` 为空。
- **产品零改动**：`git diff HEAD --name-only` 非 `.planning` = **0**（父本轮多次复算一致）。
- 该文件被写入的是 **`.txt` 取证输出**，不是产品源码、不是配置、不是数据 ⇒ **无产品行为变更、无数据丢失**。

## 4. 判定

**瞬时纪律违反（P2）**：取证动作的**落点选择**错误（把输出写进被观测仓），不是伪造、不是篡改、不是越权改产品。

**为什么仍要登记**：本计划的隔离纪律是**结构性**要求 —— 一次写进生产仓的取证输出，即便内容无害，也会
1. 让被观测仓的 `porcelain` 从 clean 变 dirty，**污染它自己要证明的那个事实**（本卡要证的正是「FF 仓 clean」）；
2. 在下一次 `git checkout/reset` 或 hook 的 stash→checkout→replay 链中成为**不可预期的输入**（本仓已发生过该链失败导致工作树重置的事故，见 `_isolation_incidents/20260920-precommit-stash-production-rollback/`）；
3. 使「观测者不改变被观测系统」这一前提失效。

⇒ **「零残留」不等于「未发生」**；本文件即为该区分的载体。

## 5. 本记录的边界（明确声明）

- 本 incident **只登记、不处置**：未回改 `I-00-A` 任何既有字节（复审报告、`review.md`、`handoff.json`、errata 前后件全部只读）。
- 本 incident **不改变任何卡的 `status`**，**不代签任何裁决**。
- 本 incident **不产生产品改动**、不执行任何 git 写操作、不联网。
- 修复建议**不在本文件内裁决**（是否要求后续 errata 类取证强制写 `%TEMP%` 或 attempt 内、是否入 `START_HERE` 纪律条，属 owner / review 面）；此处只提出该问题存在。

## 6. 关联

- 源发现：`execution_runs/I-00-A/a20260919-01/reviewer_report.md` §4 **N1**（P2）
- 同族纪律事件目录：`execution_runs/_isolation_incidents/`
  - `20260920-model-registry-extension-rollback/`
  - `20260920-precommit-stash-production-rollback/`（**同一风险的已发生形态**：hook 的 stash→checkout→replay 链失败）
  - `20260920-prereg-expectations-leak/`
- 登记册对应行由父代理随本轮 PWF 折入（本目录不改登记册）。
