# R4 Phase B 运行计划（task_plan）—— 位置透明索引与只读读取

> 运行目录：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-b/`（**本 run 的证据产物只落在此目录**，不写回审计证据目录）
> 权威来源：[R4 执行计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md) §B（B01–B10） · [R4 测试矩阵](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md)（L01–L12 / P / O / M） · [接班手册](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-handbook.md) §2/§3/§5
> 阶段 A 产物（冻结输入）：[../2026-09-11_r4-phase-a/](../2026-09-11_r4-phase-a/)（A01–A04 v0.3.1、A.DR rev3 `accepted_with_findings`、owner 六项裁定 = [owner-rulings-2026-09-11.md](../2026-09-11_r4-phase-a/owner-rulings-2026-09-11.md)）
> 状态：**B 设计 v0.1.7——owner 已授权实施（[owner-scope-decisions-2026-09-12.md](owner-scope-decisions-2026-09-12.md) §8）；B02 已实施**（F1+F2+F10，见 [evidence/b02-implementation.md](evidence/b02-implementation.md)），**待 B.VR 独立复审**；B04/B05/B01/B03/B06/B07 仍为 DESIGN_ONLY（产品代码未动）；`B.DR` 前六轮 rejected 已逐条更正（[findings.md](findings.md) F-B01-1）；每步独立 commit + 棘轮/覆盖率复跑 + 独立复审

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
| **B02** | 选同版本全部候选 location：注册/能力→状态→可读/同 hash→健康 I/O 偏好；优先级只在合格集合内排序 | [b-design.md](b-design.md) §B02 | ✅ **已实施 rev3**（F1+F2+F10；27 新用例）→ [evidence/b02-implementation.md](evidence/b02-implementation.md)；`B.VR` rev1 = **rejected**（7 条已处置）→ rev2 = **accepted_with_findings**（5 条已处置，见 [findings.md](findings.md) F-B02-4/F-B02-5）→ **待 B.VR rev3**；⚠️ 两处已登记偏差 **S-10/S-11**（待 owner） |
| **B03** | 稳定只读字节提供：固定句柄或受控快照；流式 hash；TOCTOU/云占位/坏字节/中断 | [b-design.md](b-design.md) §B03 | 设计完成 |
| **B04** | 绝对路径与 location_id 留在诊断；移动后 source/version/locator 仍可解引用 | [b-design.md](b-design.md) §B04 | ✅ **已实施**（F10 验收 4 用例 + 发现登记；**产品代码零改动**——设计目标在 B02 之后已成立，本步负责验收并钉住）→ [evidence/b04-implementation.md](evidence/b04-implementation.md)；⚠️ **F-B04-1**：同路径被新修订覆盖后旧引用不可解引用（`scanner.py:1123`，不在 allowed 集）→ 登记独立工作包 |
| **B05** | metadata 按原文/捕获来源/质量合并；保留 provenance 与冲突，**不以 priority 决定真伪** | [b-design.md](b-design.md) §B05 | 设计完成 |
| **B06** | 本地可读与正式 capture 分开：缺 URL 可预览，身份/期间不明不得默认为可信财报 | [b-design.md](b-design.md) §B06 | 设计完成 |
| **B07** | 唯一版本化读取合同；缺/未知版本明确不兼容；旧客户端在边界 adapter 一次转换 | [b-design.md](b-design.md) §B07 | 设计完成 |
| **B08** | 独立 VR 在新隔离环境重跑 L01–L12 与必要旧 C01–C10；独立文件/OS 观察证零副作用 | 待 B.VR（隔离副本） | **阻塞：需隔离副本（G8）** |
| **B09** | 真实四 root + 第五 root 新注册做一次端到端 query→open→consumer 最小读取 | 待 B.AR（隔离副本 + owner 样本确认） | **阻塞：需隔离副本 + G7** |
| **B10** | 小范围切到单一读取链；旧入口仅显式版本 adapter；记录可回退版本与移除条件 | 待 B.AR 通过后 | **阻塞：前序门** |

## 2. 门（不可自签）

| 门 | 内容 | 现状 |
|---|---|---|
| **B.DR** | 独立设计审查：字段 owner 合并/弃用、**不得新增第二套 effective_reusable**（执行计划 §B01 原文）、显式 `false` 必须保留含义；测试与验收映射是否覆盖 L01–L12 | **rev1–rev6 = rejected**（最新一轮 rev6 的 13 条已逐条处置；架构无需推翻）（20 条，已逐条更正为 v0.1.1）→ **待 rev2**（须基于新冻结提交与新输入哈希集） |
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

- **实施已授权**（owner §8）：B02 起，改动**严格限于** [file-scope.md](file-scope.md) 的 allowed 集（F1–F10）；超出 allowed 集即停并请示（§3 停止条件）。
- **文档落在本目录**：task_plan / findings / progress / b-design / file-scope / test-acceptance-map / risk-and-stop-rules / evidence / checkpoint。
- **仍不改**：`filing-fetch` 的任何文件；`revenue-forecast` 内除本目录外的任何文件；`company-wiki` 内 allowed 集以外的文件（含 `config/source_catalog.yaml`、`scripts/**`、`.source_catalog/**`）。
- 三仓推送仍走各自强制 gate（revenue 的 gate 会**只读**打开生产 catalog，已在阶段 A 的 [boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) 归因）。


## 5. 边界已由 owner 定案（2026-09-12，见 [owner-scope-decisions-2026-09-12.md](owner-scope-decisions-2026-09-12.md)）

### 5b. 裁定结果（owner 2026-09-12「全按推荐来」）

| # | 裁定 | 落地 |
|---|---|---|
| S-1 | ✅ B **可以新增**测试文件（仅新增、不改既有断言） | [file-scope.md](file-scope.md) F10 生效 |
| S-2 | ❌ owner R-1/R-4 整改**不纳入 B**（另立工作包） | [b-design §B01.3](b-design.md) |
| S-3 | ❌ **不动**在产 `export_policy_2x`（跨仓 policy_hash 保持） | `B-payload-hash` 逐次验证 |
| S-4 | ➡️ 消费者侧（filing/revenue）**归 C**，B 不签 | B07 完成定义 = wiki 侧四件 |
| S-5 | ✅ G8 **两级**：L1 机制层**可立即开工** | [b-vr-protocol.md](b-vr-protocol.md) §1 |
| S-6 | ✅ 需要**第四轮**复审，先写实边界再送 | `B.DR-rev4` = rejected（文本/落点级，11 条）→ **v0.1.5 一次收敛**，随后送 `B.DR-rev5` |
| **S-8**（v0.1.6 新增，**待 owner**，列于本节而非 §5b 的"裁定结果"表内） | 把执行计划 §B07 的「**先测 N-1 支持合同**」整体移出 B，是否同意？ | 两侧代码只接受 `1.0`，包内无 N-1 规则；按本包自订标准「范围改判须 owner 确认」 | **同意**：N-1 登记为跨仓协议待定义项，B 只承诺「未知版本显式拒绝」 | **不同意**：需先定义 N-1 规则再纳入 B07 |
| **S-7**（v0.1.5 新增，**待 owner**） | 若某步**无法**做到复杂度中性，是否允许**更新复杂度棘轮表**（= 修改既有测试文件 `test_fc1204_complexity_ratchet.py`，与 F10"仅新增"互斥）？ | 见 [b-design §B0x](b-design.md)；**作者建议：不允许**，改用把新判定放进**新增独立模块/函数**的方式保持棘轮文件不变 |
| **S-10**（v0.1.7 新增，**待 owner**） | B02 段 3 的"同 hash"**硬门**与 A 侧 4 条冻结断言冲突（那些 fixture 的字节与声明 hash 本就不同）→ 实施为"**优先 + 逐候选诊断**"，字节硬门归 B03 读路径。**是否认可这一让步？** | 依据与复跑命令：[evidence/b02-implementation.md](evidence/b02-implementation.md) §3；**作者建议：认可**（S-1 明令不得改既有断言；B03 落地后硬门补齐）。若 owner 不认可，可选：(a) 申请修改那 4 条既有断言（需 owner 另行批准、与 S-1 互斥）；(b) 把 B03 提前并与 B02 合并交付 |

> **实施已授权**（2026-09-12 第二批，见 [owner-scope-decisions-2026-09-12.md](owner-scope-decisions-2026-09-12.md) §8）：owner 原话「全按推荐：定 S-7/S-8 并开始实施」→ **B02 已实施**（F1+F2+F10），按序推进 B04 → B05 → B01 → B03 → B06 → B07，每步独立 commit + 棘轮/覆盖率复跑 + 独立复审。**新增待确认项 S-10**（B02 段 3 的硬门偏差）见 §5b 下方的待定表。

三轮 `B.DR` 均判 rejected，但**剩余 P1 全部不是文字问题，而是"B 可以动哪里"的决定**：

| # | 决定 | 现状 | 若"是" | 若"否" |
|---|---|---|---|---|
| **S-1** | **B 是否可以改测试文件？** | allowed 里原本没有测试；v0.1.3 新增 **F10**（`tests/contract/**` 仅新增），**2026-09-12 已获批（S-1）** | 新增断言有落笔处，B08/B.VR 可按同一套用例验证 | 本包**不能声称可实施**（B-DR3-04 的 P1 只能以"不实施"收口） |
| **S-2** | **owner R-4（外发门 + 无门出口）与 R-1（假保证字段）是否纳入 B？** | 已移出 B（[b-design §B01.3](b-design.md)），承载文件在禁区 | 需把这些文件移出禁区并**重签**工作包（涉及安全门，建议单独工作包） | 维持现状：它们留在 owner 的整改清单里，B 只引用 |
| **S-3** | **是否连 `export_policy_2x` 一并收敛（跨仓 policy_hash 迁移）？** | owner R-3 已收窄为"仅准入 loader"；导出路径冻结 | 需 filing-fetch 同步迁移方案 + 新裁定 | 维持现状（推荐） |
| **S-4** | **B07 的消费者侧（filing/revenue 的 adapter 与 `companies` fallback）归谁？** | v0.1.3 明确 **B 不签**，并把它留给 C | 把消费者仓纳入 B 的 allowed（跨仓工作包） | 维持"归 C"（与执行计划 §B 的"filing/revenue 仅最小协议适配"一致，但**该适配本身仍未指派**） |
| **S-5** | **G8 隔离副本按"两级"做吗？**（机制层用小 catalog；真实字节读取另批） | [findings.md](findings.md) F-B00-3 已提案，B.DR 已独立复核技术前提 | 机制层可立即开工（A06-D0 基线已就绪） | 只能等 G8 完整方案，B08/B.VR 继续阻塞 |
| **S-6** | **是否需要第四轮 B.DR？** | 三轮 rejected；剩余 P1 均为 scope 决定 | 更正后送 rev4（须全新会话） | 视为"设计已到 scope 边界"，B 停在设计态，等 scope 决定 |

> **作者的判断（供 owner 参考）**：S-1、S-2、S-4 是**同一类问题**——"B 的边界画在哪"；建议一次性决定，避免每轮复审都因边界不清被拒。

## 6. 变更记录

| 时间（本地） | 变更 |
|---|---|
| 2026-09-12 10:40–11:00 | `B.DR-rev4` = rejected（11 条，均文本/落点级）→ **v0.1.5**：B05 共享列改为保留键可加性写法（含 json_extract 回归断言）、S-2 全面落地、B07 移除未定义的 N-1、登记复杂度棘轮约束（§B0x）与 **S-7**、冲突状态改回 `blocked`、生成器写路径加断言 |

| 时间（本地，实测） | 变更 |
|---|---|
| 2026-09-12 07:43–07:46 | 建立 B run 目录；B01–B07 设计 v0.1、文件范围、测试映射、风险/停止规则；A05/A06 准备件；提交 `B.DR` 复审（提交 07:46:12 / 07:46:17） |
| 2026-09-12 07:54–08:05 | **B.DR = rejected**（20 条；8 条 claim 未复现）+ **A07 = accepted_with_findings** + **A08 = rejected**（三份复审共同命中同一 P0） |
| 2026-09-12 08:05–09:35 | **阶段 A 更正为 v0.4.1**（P0 范围更正、C2/C4/§2/§5、R 轴与进程级副作用、五值错误模型、版本轴、无门出口、A 台账一致性）；**B 设计更正为 v0.1.1 → v0.1.2 → v0.1.3**（三轮共 20+15+11 条逐条处置；v0.1.3 另把 R-1/R-4 移出 B、补 F10 测试落点、重写 B02 预算与 B05 合并规则、生成器改真断言，见 [findings.md](findings.md) F-B01-1） |
| 2026-09-12（实施期） | owner 授权实施（`owner-scope-decisions-2026-09-12.md` §8）→ **B02 实施**（F1 `service.py` + F2 `resolver.py` + F10 新测试 16 用例）；RED/GREEN 探针落盘；棘轮/覆盖率/全量套件复跑；段 3 偏差登记为 **S-10**；见 [evidence/b02-implementation.md](evidence/b02-implementation.md) |
| 2026-09-12（实施期，复审后） | **`B.VR` rev1 = rejected**（2×P1/2×P2/3×P3，独立会话逐位复现了作者的全量/覆盖率/探针数字）→ **B02 rev2**：非首选副本回退删除（只服务**验证通过**的副本）、遗留注解契约恢复（修 `duplicate_cleanup` StopIteration）、预算按请求重置、理由带 source 组、`.rejections` 按路径段匹配、水合掩码补 `RECALL_ON_OPEN`；新增 7 个回归用例；偏差重述为 **S-10/S-11**；见 [findings.md](findings.md) F-B02-4 |
