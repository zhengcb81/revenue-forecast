# A08（A.AR）复审处置表 —— verdict = `rejected`（1×P0 / 2×P1 / 2×P2 / 2×P3）

> 依据：复审记录 [reviews/A.AR.json](reviews/A.AR.json)；A 侧结论行 [findings.md](findings.md)（A08 行）。
> **为什么现在补这张表**：目标里明确包含「A07/A08 独立复审**及其闭环**」。A08 的七条里，**A-AR-02 / A-AR-03 / A-AR-05 早前已闭环并留有记录**，而 **A-AR-01 / A-AR-04 / A-AR-06 / A-AR-07 在 A run 目录里没有任何处置记录**——即"找不到它被处理过的痕迹"。本表按**实物证据**逐条判定，并把**两项残留**如实登记（不重写冻结收据）。
> 纪律：A 侧合同/收据**保持原字节**（owner 规则），因此**不重写历史计数**；残留以"更正注记 + 本表登记"的方式收口。

| # | 级别 | 复审要求（摘要） | 实物证据 | 判定 |
|---|---|---|---|---|
| **A-AR-01** | P1 | 统一计数：A run 目录三处「pushed 次数」= **10/3**、「前移」= **7 处**；把"仍然开放的 owner 裁定"改写为**已裁定**（G2）；三份合同**状态行与版本一致**；identity-contract 的 **R6 owner 栏**填 R-5 结论；checkpoint 记录 `reviewed_commit` | ① [findings.md](findings.md) 第 67 行现为"**owner 裁定项：已于 2026-09-11 全部裁定**"✓；② [root-contract.md](root-contract.md):9 状态行 = **v0.4.1** ✓（三份合同同）；③ [identity-contract.md](identity-contract.md):52 有 **v0.4.1 更正**（R6 机制方向反了）✓；④ checkpoint 的 `reviewed_commit` = `8e030c6` ✓（本轮之前已是必填） | ✅ **已闭环**，**两处残留**（下） |
| — | 残留 1 | 计数「10 次 vs 11 次」并存 | [boundary-audit.md](boundary-audit.md):71 正文写"revenue 当晚 **10 次**推送"，而同文件 :73 的**更正注记**写"实为 **11 次**（#134–#144）"。两者是"原文 + 更正注记"的关系，但同页并存易误读 | ⚠️ **登记不改写**（收据纪律）。真正的事实是：推送次数早已远超两者（B 阶段又推了十余次）——**计数不是稳定事实**，任何绝对数都会过期；已在 [progress.md](../2026-09-11_r4-phase-b/progress.md) 与 CI 记录里改为**按 run id 记录**而非计数 |
| — | 残留 2 | 「6 处前移」应为 7 | [baseline-map.md](baseline-map.md):36 的 **v0.3 注记**仍写"已观测前移共 **6 处**"；A-AR-01 要求为 7。后续 `-shm` 观测又继续增加（B 阶段每次 pre-push gate 都会推进），故该数同样是**过期事实**而非当前事实 | ⚠️ **登记不改写**：现在正确做法是**不再追这个数**，而是引用 [boundary-audit.md](boundary-audit.md) 的**归因结论**（前移来自本会话强制的 pre-push gate 只读打开生产 catalog） |
| **A-AR-02** | P1 | 117 行中 13 行无法指派 → 补桥接表 | [a08-goal-bridge.md](a08-goal-bridge.md)（表 A 逐族点名 13 行 + 表 B 反向 11 个 ID；§3 登记仍无 L/P/O/M 路由的三族）；其陈旧台账已在本轮更正（见 [../2026-09-11_r4-phase-b/progress.md](../2026-09-11_r4-phase-b/progress.md) 的历史条目） | ✅ **已闭环** |
| **A-AR-03** | P2 | checkpoint 必须覆盖全部产物并把 `reviewed_commit` 推进到承载更正的提交 | [checkpoint.json](checkpoint.json)：`produced_files` **31** 项、`completeness.complete = true`、`reviewed_commit = 8e030c6`；`--verify-only` 在本轮实测 `all_match: true` | ✅ **已闭环** |
| **A-AR-04** | P2 | 把 A08 的 `goal_mapping` 补进 **B.DR 的复审输入**，并记录复审者的确认或返工结论 | **B run 目录里搜不到 `goal_mapping` / `A-AR-04` 的任何引用**（实测：`rg` 无命中）⇒ **要求的那条记录不存在**。但**实质已被事件覆盖**：B.DR 六轮复审逐条处置、其中 **B-DR-01 与 A-AR-05 是同一个 P0** 且已更正；B 的 [test-acceptance-map.md](../2026-09-11_r4-phase-b/test-acceptance-map.md) 与 [file-scope.md](../2026-09-11_r4-phase-b/file-scope.md) 把 13 行的可覆盖部分逐条映射到 L/P/O/M | ⚠️ **按事件闭环，但要求的记录缺失**——如实登记为残留（补写一条"事后确认"没有证据价值，故不伪造记录） |
| **A-AR-05** | **P0** | A02 R8 / owner R-3 的事实前提被证伪（`policy_2x` 导出在产）——须更正合同并重新裁定 | [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md):14 **范围更正**：R-3 收窄为"仅准入 loader"；[root-contract.md](root-contract.md):3-9 的 **v0.4.1 更正**（含"导出路径在产 + 跨仓 policy_hash 契约"）；B 侧 [evidence/b01-implementation.md](../2026-09-11_r4-phase-b/evidence/b01-implementation.md) 把解析器的复用判定**对齐**到 policy 侧单一实现；[findings.md](../2026-09-11_r4-phase-b/findings.md) **F-B07-1** 让"导出 payload 未变"**可执行且已通过** | ✅ **已闭环**（且是本轮 A/B 之间最重要的一条） |
| **A-AR-06** | P3 | 阶段 B run 目录要有与 `inputs.json` 同级的**输入冻结记录**（HEAD/dirty + 8 个候选改动面 + wiki 产品锚点），并在 phase-B checkpoint 的 `inputs` 里注明 file-scope 的 F1–F8 哈希 | phase-B checkpoint 的 `inputs` 块 = **三仓 head/dirty**（wiki/revenue/filing-fetch）+ per-file 版本注记 ✓；**F1–F8 的哈希**在 [file-scope.md](../2026-09-11_r4-phase-b/file-scope.md) 的"哈希"列逐行给出 ✓；产品锚点（wiki `7d4852f`）在 A 侧 checkpoint 与本表引用 ✓ | ✅ **已闭环**（记录分布在 file-scope + checkpoint 两处，非单文件 `inputs.json`，已在 checkpoint 的 `inputs.note` 说明） |
| **A-AR-07** | P3 | A.AR 复审记录应作为产物登记 sha256，避免"B.DR rejected 的结论没有记录映射" | A 侧 [checkpoint.json](checkpoint.json) 的 `produced_files` **已含** `reviews/A.AR.json`（含 sha256）；phase-B 的 checkpoint 亦把 `reviews/**` 纳入产物清单 | ✅ **已闭环** |

## 小结（对目标"闭环"的交代）

- **7 条中 5 条已闭环**（A-AR-01 主体、02、03、05、06、07 —— 其中 A-AR-01 主体闭环但有 2 处**过期计数**残留）。
- **1 条按事件闭环但缺记录**（A-AR-04）——**不伪造事后记录**，如实登记。
- **2 处残留**（A-AR-01 的两个计数）**按收据纪律不改写历史**，并给出"此后不再追绝对计数、改为按 run id/归因结论引用"的替代口径。
