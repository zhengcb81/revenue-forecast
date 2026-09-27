# I-17-B 冻结 oracle（a20260926-01）

> **状态：FROZEN（首动作落骨架，本文件写入即冻结；此后不因结果回改判据）**
> 卡：`execution_v2/card_I-17-B.md`（12 行）· 角色：`implementer_i17b_final_audit`（**未参与该项实施的终审者**）
> 复审另派；**本工位不自签**、**不放行参数**、**不解除任何 `OPEN/BLOCKED-*`**、**不代签会计/买方面**。

## 0. 运行时（真实时间，不沿用卡文日期）

- 实际运行启动：`2026-09-27T09:22:42+01:00`（`Get-Date` 原始输出见 §7）
- 时区：本机 `+01:00`；账本/周任务时间戳为 `+00:00`（UTC）
- 现在 = **2026-09-27（本地 09:2x）**；日期按实际运行启动
- 工作目录：`C:\Users\郑曾波\Projects\revenue-forecast`
- 本卡唯一写入面：`.planning\2026-09-19-three-project-history-audit\execution_runs\I-17-B\a20260926-01\`

## 1. 卡文 5 动作判据（逐字，L6–L10 + 退出 L12）

1. 从总纲I-00…17逐条查所有子卡、NA理由、依赖与真实用户旅程；子卡数量全绿不自动推出parent完成。
2. 在当前有效组合重跑I-00-C六负例，缺真实场景/自然观察/证据映射必须继续阻断相应业务完成。
3. 分别报告来源获取、数据湖/工件、正式预测、买方质量、准确性证据和持续服务六种资格；“未证明优于基准”是合法准确性结论，但不能改写为提高。
4. 对审查期间发生的并行代码/config变更重核受影响证据；不向过期版本发通过结论。
5. 输出最终报告包含已完成、限域通过、blocked、合理退役/NA及下一动作。禁止以“全部通过，除……”掩盖阻断项。
> 退出：结论与证据一致，失败也能如实关闭本次验收工作；产品完成资格仅授予确实满足的范围。

**硬判据派生（运行前冻结）**

- `A1` 逐条覆盖总纲 18 项（I-00…I-17）× `dispatch.json` **92 张**执行卡 + 独立补充卡；每卡必须落五分类之一，**不得空缺**；**子卡全绿 ≠ parent 完成**（`review_and_handoff.md:43` 三条件缺一不可）。
- `A2` 六负例在**当前有效组合**逐个重跑；任一负例未被拒绝 ⇒ 相应业务完成**继续 blocked**（fail-closed）。
- `A3` 六种资格**分别**给状态，互不代偿；`accuracy` 只允许 `GRANTED / NOT_GRANTED / UNPROVEN_BASELINE` 三值，**“未证明优于基准”登记为合法准确性结论**，**禁止改写为“提高”**。
- `A4` 并行变更（`cw dbe4745` + 授权摄取写入 + 两外部周任务文件 + `I-16-B` 部署窗口 + 未提交他人改动）逐条重核受影响证据；证据版本早于变更 ⇒ **不得对该证据发通过结论**，只能 `RECHECK_REQUIRED` / `STALE`。
- `A5` 报告必须含 `已完成 / 限域通过 / blocked / 合理退役·NA / 下一动作` 五分类**分列计数**；**出现任何 blocked 却写“全部通过（除……）” ⇒ 判据失败**。
- `F5` 不放行参数 · 不自签 · 禁五份计划文件 · 禁 `.planning` 外写 · 禁 git 写 · **禁 `git status`** · 禁联网。

## 2. 只读来源（V2-4 清单）+ 15 张上游 `sha`

### 2.1 卡文与授权语境

| # | 来源 | sha256 / 说明 |
|---|---|---|
| S1 | `execution_v2/card_I-17-B.md`（1297 B） | `08266a1bb932e16ff79dac9756ac4cf79cee9e8f0b3a4b291d26f123f03ee477` |
| S2 | `execution_v2/card_I-00-C.md`（2240 B，六负例原文） | `19e9e0b370d3ec640ccdfae47914512c9cf50a0c41e9071a0a6bf9829d5e594e` |
| S3 | `OWNER_DECISIONS.md`（115984 B；读 §三十四~§三十九） | `56c8992bcb3bfedb496f34cd7760b74a108da2511a23a4d446f2177603ac3330` |
| S4 | `REMEDIATION_REGISTER.md`（500372 B；读尾部 §157–§162） | `7bff0589206b5f31b90f28cfe94ee8dc2bd17f399c30c752c627e9e4fde83340` |
| S5 | `implementation_plan.md`（总纲 I-00…17，18 项） | 见 §7 实测 |
| S6 | `execution_v2/dispatch.json`（92 卡）+ `dispatch.md` | 见 §7 实测 |

### 2.2 15 张上游链卡 `handoff.json` sha256（全量复算，非转述）

| # | 上游卡 / attempt | handoff sha256 | `status` |
|---|---|---|---|
| U1 | `I-17-A/a20260926-01` | `3f29ac8021cda673c88a1b4586255d2fd82cbf4d3cff1a6542362eb651e4971f` | `accepted_scoped` |
| U2 | `I-07-B/a20260923-01` | `e43cf258e78f1ddc2085ef5e8c5d6cb3e2a730179cb18f566c6da4e15acb9e99` | `accepted_scoped` |
| U3 | `I-07-C/a20260923-01` | `550b489da48c5366069cef5248735d4804837469c67ae467348185c7388491f7` | `accepted_scoped` |
| U4 | `I-07-D/a20260923-01` | `82bb03aca1756d0cec155d039150e930d7b2a885659ad73d5a94e1c032d09e13` | `accepted_scoped` |
| U5 | `I-07-E/a20260926-01` | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` | `accepted_scoped` |
| U6 | `I-10-A/a20260923-01` | `a3f2208ac8601e1a1711d3f6aa30b3e935148bb93017c8a21d350c10dbea3c58` | `accepted_scoped` |
| U7 | `I-11-B/a20260926-01` | `4c3c5c908f7c69b23f3ecec52fc81fcbd766e1bfa1174422f8abafbbd7caed31` | `accepted_scoped` |
| U8 | `I-11-C/a20260926-01` | `da25f736cfde6f97047a691ddff28f1b079c6c29d1cfeac03729ce4c32b9c453` | `accepted_scoped` |
| U9 | `I-12-A/a20260926-01` | `7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714` | `accepted_scoped` |
| U10 | `I-12-BE/a20260926-01` | `dfb71c25bd62902ab248444c46d6579bf96acb7653968d8d77d8ac1208b2e3d8` | `accepted_scoped` |
| U11 | `I-13-A/a20260926-01` | `0b466621ff964c8e3347cc96033bf7abd1f800eaf9eda75c3555209ac60a2f97` | `accepted_scoped` |
| U12 | `I-13-BC/a20260926-01` | `2dfa7a0918a75c862fdf5b378bb50523cf94ff56a48e3b31353d5f0b724f8dfa` | `accepted_scoped` |
| U13 | `I-16-A/a20260926-01` | `8b6849109db11f962d5b3bb5fb0dd863ba200ad8bbfea1a2202f035835dca29f` | `accepted_scoped` |
| U14 | `I-16-B/a20260926-01` | `0e2fdeeb9013d980e1e95f55ae460ac0eddf9affed710ff705705f349ebb920a` | **`blocked`**（前置未满足） |
| U15 | `I-16-B/a20260926-02` | `e0d0371d13f0d2d077e4a22212d2f522e6b250829220eb27eb494952db871ab6` | `accepted_scoped`（部署窗口执行） |
| U16 | `I-00-C/a20260919-01` | `1a9315f9e24faa471f9a9656a0f6f2e38c5b624b0a22ad07b03c83209e0a203c` | `accepted_scoped` |

> 15 张链卡 = U1–U13 + U15 + U16（`I-16-B` 取有效 attempt `a20260926-02`）；U14 作为**同卡前一 attempt 的 blocked 历史**一并登记，**不得丢弃**。

## 3. 门 0 自探留档（写 / 回读 / 删 —— 原始输出）

```text
== GATE0 START ==
2026-09-27T09:29:04+01:00
WRITE_OK bytes=27
READBACK=[gate0 i17b probe payload]
SHA256=568bf936cde182eb27c21e3314a6beecc1b1d41be3e5615be33b78120e0f0659
DELETE_OK
== GATE0 END ==
```

⇒ `gate0_passed = true`（写入面 = 本 attempt 目录；回读逐字节一致；删除后 `Test-Path = false`）。

## 4. 变异计划（≥3；红绿均留 `rc` 原始输出；**expected 运行前手算冻结，不由被测脚本生成**）

校验器：`verify_i17b.ps1`（本目录，只读源 + 只写本目录）。冻结 `exit_code_legend` 见 §5。

| ID | 变异（RED 臂，仅作用于本目录副本） | 冻结 expected（运行前） | GREEN 臂（恢复后） |
|---|---|---|---|
| `MUT-1` | 上游 sha 清单副本中把 `I-00-C` 的 handoff sha 首字符 `1`→`2` | 校验器复算源文件 sha 与清单不符 ⇒ **`rc=3`** | 还原 ⇒ **`rc=0`** |
| `MUT-2` | 把证据映射表中六负例 `N6` 的裁决由 `reject` 改为 `accept` | 六负例须**全 reject**，出现 `accept` ⇒ **`rc=3`** | 还原 ⇒ **`rc=0`** |
| `MUT-3` | 把外部阻断信号副本 `weekly_manifest.json` 的 `"ok": false` 改为 `true` | 与源文件字节不符且源为 `false` ⇒ **`rc=3`** | 还原 ⇒ **`rc=0`** |
| `MUT-4` | 从五分类清单副本中删除 `blocked` 分类条目 | 五分类必须齐备且 blocked 计数≥1（实测存在阻断） ⇒ **`rc=3`** | 还原 ⇒ **`rc=0`** |

**冻结不变式（供 MUT 判据）**
- 六负例在**当前有效组合**下预期**全部 `reject`**；若实测有 `accept`，则**如实记 `rc=3` 并把相应业务完成登记为 blocked**——**不改判据贴合结果**。
- 外部信号源实测 `"ok": false`（`assurance/runs/weekly_manifest.json`，`run_id 20260927T033001Z`），**预期 blocked 信号成立**。
- 五分类中 `blocked` 计数**运行前预测 ≥1**（依据：7 张 `review_pending` 子卡 + 3 张无 run 卡 + 周任务两连败）。若实测为 0，同样如实记录并解释，**不伪造**。

## 5. `exit_code_legend`（本批自描述；跨批聚合先读本表）

| rc | 含义 | 判据 |
|---|---|---|
| `0` | 通过 | 校验器正常结束且**业务判定通过** |
| `1` | harness 失败 | 脚本自身出错 / 输入文件缺失 / 路径未绑定 |
| `2` | 无裁决 | 冻结期望本身缺失或不可用，在任何用例判定之前发出 |
| `3` | 未达预期 | 判定可能且不成立：负例未被拒绝 / 清单缺项 / sha 不符 / 阻断信号被改写 |

## 6. 六种资格（冻结定义与判据；`A3`）

| 资格 | 允许状态 | 授予前提（全部满足才可 `GRANTED`） |
|---|---|---|
| Q1 来源获取 | `GRANTED / GRANTED_SCOPED / NOT_GRANTED / BLOCKED` | 三市场真实来源链 + 二次复用 + 跨根泛化证据，且证据版本未被并行变更作废 |
| Q2 数据湖/工件 | 同上 | 工件资格、审核队列、实际读取与最小重算证据 |
| Q3 正式预测 | 同上 | 真实 source-preparation 产物 → 计算 → 验证 → 发布全链，**按公司分列**，3/3 才可全称 |
| Q4 买方质量 | 同上 | 买方交付逐项评分 + 情景走查 + 资格冻结（I-13 全链） |
| Q5 准确性证据 | `GRANTED / NOT_PROVEN_VS_BASELINE / NOT_GRANTED / BLOCKED` | `NOT_PROVEN_VS_BASELINE`（**未证明优于基准**）是**合法结论**；**禁止**改写为 `提高` |
| Q6 持续服务 | 同上 | 部署复验 + 自然观察真实时长；`pending/in_progress` ⇒ 不授予 |

**fail-closed**：任一资格证据不足 ⇒ 报 `blocked`；`blocked` 也是**合格的验收关闭形态**（退出条款明令「失败也能如实关闭」）。

## 7. 原始时间与来源实测输出

```text
2026-09-27T09:22:42+01:00
08266a1bb932e16ff79dac9756ac4cf79cee9e8f0b3a4b291d26f123f03ee477  1297  card_I-17-B.md
19e9e0b370d3ec640ccdfae47914512c9cf50a0c41e9071a0a6bf9829d5e594e  2240  card_I-00-C.md
56c8992bcb3bfedb496f34cd7760b74a108da2511a23a4d446f2177603ac3330  115984  OWNER_DECISIONS.md
7bff0589206b5f31b90f28cfe94ee8dc2bd17f399c30c752c627e9e4fde83340  500372  REMEDIATION_REGISTER.md
```

`S5`/`S6` 的 sha 在 `verification.json` 的 `source_hashes` 中补录（同一冻结回合内，不改本表判据）。
