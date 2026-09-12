# R4 Phase B 进度（progress）

## 2026-09-11 23:3x — B 阶段启动（设计，DESIGN_ONLY）

- **授权**：owner「接着做 B 阶段，一直做不要停」（2026-09-11 夜）。按 handbook §2.5 解释为：**B 的设计可连续推进**；产品代码写入与 `--help` 之外的命令执行**仍需精确批准**。
- **起点**：阶段 A 收口 —— A.DR rev3 = `accepted_with_findings`（0×P0/P1）、owner 六项裁定（G2）已定、A02 封版为 `root-contract v0.4`、CI 全绿（revenue #144 / wiki #103）。
- **本 run 建立**：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-b/`（**不在审计证据目录内**）。

### 1. 本轮交付（全部为文档）

| 文件 | 内容 |
|---|---|
| [task_plan.md](task_plan.md) | B01–B10 状态、B.DR/B.VR/B.AR/D.SAFE 门、停止条件、交付边界 |
| [b-design.md](b-design.md) | B01–B07 设计（含 P-1…P-8 原则、四段式候选选择、稳定只读字节、metadata provenance、preview/verified 分离、版本化读取合同）与 B08–B10 前置 |
| [file-scope.md](file-scope.md) | 8 个候选改动文件的绝对路径 + 符号/行号 + 冻结哈希；禁止清单；回退策略 |
| [test-acceptance-map.md](test-acceptance-map.md) | B 步骤 → L01–L12/P/O/M 测试 ID → 验收点 → 完成定义（防"勾成完成"） |
| [risk-and-stop-rules.md](risk-and-stop-rules.md) | H01 交叉、D.SAFE 交叉、10 条硬停止、5 类"看起来跑通但不算通过"陷阱 |
| [findings.md](findings.md) | 设计期发现 F-B00-1…5（含"G8 可分两级"的关键判断） |
| Phase A 侧新增 | [a05-corpus-sample-plan.md](../2026-09-11_r4-phase-a/a05-corpus-sample-plan.md)、[a06-baseline-plan.md](../2026-09-11_r4-phase-a/a06-baseline-plan.md)、[command-manifest-readonly.json](../2026-09-11_r4-phase-a/command-manifest-readonly.json) |

### 2. 关键设计结论（一句话版）

1. **B02 与 B05 同根**："位置/优先级被当成业务判据"——B02 把它从**资格**降为**排序**，B05 把它从 **metadata 真伪**彻底移除；两次改动一次收敛。
2. **B03 的字节安全**靠"固定句柄 → 受控快照 → 显式失败"三级，**禁止**只信 mtime/文件名，**禁止**在 query/open 内隐式建快照还宣称零写。
3. **B06/B07** 靠 `preview` 与 `verified_input` 的**资格标签**分离，配一个版本化读取合同 + 边界 adapter；缺 policy **不得**静默退回 `companies`。
4. **B08 的隔离副本不必是 50 GB 拷贝**：机制层用小 catalog（既有测试机制），只有 R1 真实读取需要真实字节——已写入 findings F-B00-3。

### 3. 本步实际副作用（如实）

- **执行过**：只读文件读取（源码/grep/哈希/行号）、文档写作。
- **未执行**：任何 CLI（含 `--help`）、任何数据命令、网络、产品写入、任务/worker 操作、删除。
- **注意**：本 run 的推送仍会触发 revenue 的强制 pre-push gate，其 real-data 套件会**只读**打开生产 catalog（阶段 A 已归因并披露）。

### 4. 未完成 / 阻塞（不阻塞设计，阻塞实施）

1. **B 的 DEV 工作包与文件范围批准**（[file-scope.md](file-scope.md)）——owner 一句话即可，之后才能改代码。
2. **B.DR 独立设计审查**——本轮已提交复审（见 §5）。
3. **隔离副本（G8）**——建议按 findings F-B00-3 分两级；机制层可立即做。
4. **A05 样本清单（G7）与只读命令 manifest**——已写好待确认。
5. **A07/A08**（阶段 A 的 VR/AR）——可基于现有合同立即启动。

### 5. 变更记录

| 时间（本地） | 变更 |
|---|---|
| 23:3x | 建立 B run 目录；交付上述 6 份文档 + Phase A 三份准备件；提交 B.DR 复审 |
