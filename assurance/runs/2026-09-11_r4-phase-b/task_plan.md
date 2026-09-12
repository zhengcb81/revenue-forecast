# R4 Phase B 运行计划（task_plan）—— 位置透明索引与只读读取

> 运行目录：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-b/`（**本 run 的证据产物只落在此目录**，不写回审计证据目录）
> 权威来源：[R4 执行计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md) §B（B01–B10） · [R4 测试矩阵](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md)（L01–L12 / P / O / M） · [接班手册](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-handbook.md) §2/§3/§5
> 阶段 A 产物（冻结输入）：[../2026-09-11_r4-phase-a/](../2026-09-11_r4-phase-a/)（A01–A04 v0.3.1、A.DR rev3 `accepted_with_findings`、owner 六项裁定 = [owner-rulings-2026-09-11.md](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md)）
> 状态：**B 设计 v0.1.1（DESIGN_ONLY）**；`B.DR` 首轮 **rejected**（1×P0+7×P1+9×P2+3×P3，20 条已逐条更正，见 [findings.md](findings.md) F-B01-1）；产品代码**未被修改**；B 的实施需 owner 批准本包 DEV 工作包与文件范围（handbook **§1 第 5 项** + §3；v0.1 曾误写"§2.5"）

## 0. 起点与授权

| 项 | 值 |
|---|---|
| 阶段 A 门 | **A 合同已更正为 v0.4.1**（A.DR rev3 accepted_with_findings → A07 `accepted_with_findings`、A08 `rejected`；两份复审的意见已就地更正） |
| owner 指令（2026-09-11 夜） | "接着做 B 阶段，一直做不要停" → 授权**连续推进 B 的设计**；不等于批准产品写入 |
| owner 裁定（G2） | 六项已定案；**R-3 的范围已收窄为"仅准入 loader"**（`export_policy_2x` 在产、不在收敛范围），并把 R-4 范围扩大至无门外发出口、R-1 追加 `read_only` —— 见 [owner-rulings](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md) |
| 本 run 可做 | 设计、文件范围、测试/验收映射、风险评估、只读核对、独立复审 |
| 本 run 不可做（需另行批准） | 任何产品代码/配置/DB 写入；`--help` 之外的 CLI 执行；网络/下载/LLM；删除；任务注册；worker 恢复 |
| 隔离边界 | 行为验证一律在**隔离副本**上做；生产 catalog 49,677,344,768 B，禁止行为探针 |

## 1. B 的十个步骤（执行计划 §B 原文 → 本 run 的落地编号）

| 步骤 | 执行计划原文动作（摘） | 交付物 | 状态 |
|---|---|---|---|
| **B01** | 每个 root 字段的唯一 owner（path/adapter 在 storage，身份在 catalog，外发策略在动作边界）；旧字段版本映射 | [b-design.md](b-design.md) §B01 | 设计完成 |
| **B02** | 选同版本全部候选 location：注册/能力→状态→可读/同 hash→健康 I/O 偏好；优先级只在合格集合内排序 | [b-design.md](b-design.md) §B02 | 设计完成 |
| **B03** | 稳定只读字节提供：固定句柄或受控快照；流式 hash；TOCTOU/云占位/坏字节/中断 | [b-design.md](b-design.md) §B03 | 设计完成 |
| **B04** | 绝对路径与 location_id 留在诊断；移动后 source/version/locator 仍可解引用 | [b-design.md](b-design.md) §B04 | 设计完成 |
| **B05** | metadata 按原文/捕获来源/质量合并；保留 provenance 与冲突，**不以 priority 决定真伪** | [b-design.md](b-design.md) §B05 | 设计完成 |
| **B06** | 本地可读与正式 capture 分开：缺 URL 可预览，身份/期间不明不得默认为可信财报 | [b-design.md](b-design.md) §B06 | 设计完成 |
| **B07** | 唯一版本化读取合同；缺/未知版本明确不兼容；旧客户端在边界 adapter 一次转换 | [b-design.md](b-design.md) §B07 | 设计完成 |
| **B08** | 独立 VR 在新隔离环境重跑 L01–L12 与必要旧 C01–C10；独立文件/OS 观察证零副作用 | 待 B.VR（隔离副本） | **阻塞：需隔离副本（G8）** |
| **B09** | 真实四 root + 第五 root 新注册做一次端到端 query→open→consumer 最小读取 | 待 B.AR（隔离副本 + owner 样本确认） | **阻塞：需隔离副本 + G7** |
| **B10** | 小范围切到单一读取链；旧入口仅显式版本 adapter；记录可回退版本与移除条件 | 待 B.AR 通过后 | **阻塞：前序门** |

## 2. 门（不可自签）

| 门 | 内容 | 现状 |
|---|---|---|
| **B.DR** | 独立设计审查：字段 owner 合并/弃用、**收敛现存两处 effective_reusable（不得出现第三处）**、显式 `false` 必须保留含义；测试与验收映射是否覆盖 L01–L12 | **rev1 = rejected**（20 条，已逐条更正为 v0.1.1）→ **待 rev2**（须基于新冻结提交与新输入哈希集） |
| **B.VR** | 隔离环境重跑 L01–L12（+必要旧 C01–C10），独立 OS/文件观察证明本地零副作用 | 阻塞（G8） |
| **B.AR** | 从原文独立复本身份与 hash；真实四 root + 第五 root 的最小读取 | 阻塞（G8 + G7） |
| **D.SAFE 交叉** | H01（自动 prune 可达性）与写/删除路径的隔离证据 | 见 [risk-and-stop-rules.md](risk-and-stop-rules.md) |
| **A07/A08（阶段 A）** | A07 = `accepted_with_findings`（22 负例 + 5 值错误模型已并入 A03 §2.4）；A08 = `rejected`（117 行映射已产出，桥接表待做） | 已完成并更正入 v0.4.1 |

## 3. B 的停止条件（硬停止，任一触发即停并记录）

1. 需要写产品文件、写 DB、注册任务、恢复 worker、联网、下载、外发 → 停，请授权。
2. 需要看到**未注册 root / 越界路径 / reparse 逃逸**的样本才能继续 → 停，不自行制造。
3. 真实源缺失（无 URL、身份/期间不明）→ 记 blocked，**不合成补位**。
4. 基线漂移（三仓 HEAD/配置/schema 与冻结值不同）→ 重审受影响部分，不覆盖他人改动。
5. 需要在生产 catalog 上做行为验证 → 停（G8）。
6. 测试为 skip/unknown/rc0 空输出 → 不计通过。

## 4. 交付边界（本 run）

- **只写文档**：本目录内 task_plan / findings / progress / b-design / file-scope / test-acceptance-map / risk-and-stop-rules / checkpoint 与 A05/A06 准备件。
- **不改**：`company-wiki` 与 `filing-fetch` 的任何文件；`revenue-forecast` 内除本目录外的任何文件。
- 三仓推送仍走各自强制 gate（revenue 的 gate 会**只读**打开生产 catalog，已在阶段 A 的 [boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) 归因）。

## 5. 变更记录

| 时间（本地，实测） | 变更 |
|---|---|
| 2026-09-12 07:43–07:46 | 建立 B run 目录；B01–B07 设计 v0.1、文件范围、测试映射、风险/停止规则；A05/A06 准备件；提交 `B.DR` 复审（提交 07:46:12 / 07:46:17） |
| 2026-09-12 07:54–08:0x | **B.DR = rejected**（20 条；8 条 claim 未复现）+ **A07 = accepted_with_findings** + **A08 = rejected**（三份复审共同命中同一 P0） |
| 2026-09-12 08:0x–09:0x | **阶段 A 更正为 v0.4.1**（P0 范围更正、C2/C4/§2/§5、R 轴与进程级副作用、五值错误模型、版本轴、无门出口、A 台账一致性）；**B 设计更正为 v0.1.1**（20 条逐条处置，见 [findings.md](findings.md) F-B01-1） |
