本卡由 [root_cards.md](root_cards.md) 原文抽取并在 owner 裁定后新立。先读 [执行协议](START_HERE.md)、[root_cards.md 共用规则](common_root_cards.md) 和 [独立验收](review_and_handoff.md)；不需要读取全册。状态 planned，运行 cwd 必须由 I-00-B 绑定。

## I-14-E-TESTSIDE — 重启节点时序抖动的**测试侧施加**（新立卡，owner 2026-09-24 裁定 A）

Parent：I-14。前置：**I-14-E**（`a20260919-01`，测量与归因已交付、结论栏未填）。Owner：测试维护者；独立 reviewer。
新立依据：`OWNER_DECISIONS.md` §二十五（owner 选项 **A**：另立一张「施加卡」）；卡文来源=I-14-C r5 `decision.md §19-②`（§13 T1-7 授权立卡）。

**为什么需要本卡**：`I-14-E` 源卡的退出判据是「测试在负载波动下不再随机红/绿，且无需改动产品代码」，但其任务书边界是**生产仓只读**，两者冲突（源卡 `review.md §3.4` 与 `after/proposed-test-side-change.md §3` 已如实登记并请求 owner 裁定）。owner 裁定 = **把施加动作独立成卡**，源卡保持 pending 至本卡回来。

### 写入边界（本卡的核心约束，逐条硬性）

本计划通行纪律是「**修复在 iso 隔离副本、生产零合并、晋升独立授权**」—— 本卡沿用它：

| 路径 | 允许 |
|---|---|
| 本卡 attempt 目录 `.planning/**/execution_runs/I-14-E-TESTSIDE/**`（含 `iso/` 公司仓副本） | ✅ **允许写**（红绿变异全部在此跑） |
| `company-wiki/tests/**`（真仓） | ⚠️ **本卡不直接写** —— 施加结果以 **`changes.diff`** 交付，**应用到真 `company-wiki/tests/**` 属晋升，由父/owner 授权后执行** |
| `company-wiki/src/**`、`company-wiki/scripts/**` | ❌ **绝对禁止**（= 产品实现；改它即 P1） |
| 其他任何 `.planning` 外路径 | ❌ 禁止 |

**判据自证**：结束前 `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` **必须仍 = 0**（本卡在 iso 内作业，故该不变量**继续成立**，不像直接改真仓那样会破）。
**违反第 3 行即 P1 无效**：卡片第 2 条原文「**不得**为让测试变绿而改产品代码」。

### 可选修法（源卡 `after/proposed-test-side-change.md` 已给三条，本卡按其排序）

1. **建议 1（推荐）**：`-WorkerHangTimeoutSeconds` 由**同一次测试内实测的启动带宽**导出（如 `max(2.0, 4 × t0)`），而非写死 0.5 s。依据=源卡独立测量：Q1/Q2 实测上尾 1.7–2.5 s、外加 8 忙循环时 25/25 越线。
2. **建议 2（可选，需与 1 同用）**：让重启后的子进程写入自己的 `worker_runtime.json`（新鲜心跳）后再退出 —— **源卡实测它单独不解决问题**（`Start-Process` 到写出 runtime 之间 `$Runtime` 仍 null，仍走 uptime 分支）。
3. **建议 3（默认不取）**：放宽断言 `== 2` → `>= 2`。**若采用，须由测试维护者书面说明为什么「重启次数」不是该节点的产品语义**，否则按卡片第 4 条视为事后放宽。
4. **节点②**（`test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`）：三个预算 15/15/20 s 同样改为由**实测包装器延迟**导出（如 `max(30, 6 × 实测延迟)`）。

**禁止**：把阈值改成「刚好不再失败」的数（源卡独立测量显示上尾到 2.5 s，0.7 s 之类即事后放宽）；把 `~25%` 观测值升格为规范常量（源卡第 6 条）。

### 九步要点（按 START_HERE 固定九步）

1. **先冻结 oracle**：新的 `expected` 必须由**源卡的原始 24×2 观测带**与**独立带宽测量**手算，**不得由重跑生成**；冻结后再跑第一次。
2. 边界自证：写入面 = 仅 `CW/tests/**` + 本 attempt；`before/final_hashes.json` 证明 `CW/src/**`、`CW/scripts/**` 运行前后逐字节相同。
3. 红→绿：施加前必须**先复现红**（在源卡测得的负载条件下该节点仍随机红/绿），施加后在同一条件下跑绿。
4. **变异证明**：至少一个变异体（如把导出公式退回写死 0.5 s）必须把新判据打红。
5. 负载条件须**独立测量记录**，不得只在空闲机上跑一次就报绿。
6. 产出 `changes.diff`（**只含 `CW/tests/**` 文件**，逐文件披露）。
7. `handoff.json` 顶层 `status=review_pending`、`implementer_signed=false`；`blocked_by`/`unverified` 如实。
8. 交付证据入本 attempt。
9. 只读自证 + 报父派复审。

**退出**：本卡自己的判据变绿 + 变异打红 + 边界自证（产品代码 0 字节改动）三者齐备。
**验收**：ACCEPT 只能由独立 reviewer 签；本卡不代签、不晋升、不改源卡 `I-14-E` 的任何字节与 status。
**恢复**：回退测试改动；保留源卡 24 次原始观测记录与本卡全部原始日志。
