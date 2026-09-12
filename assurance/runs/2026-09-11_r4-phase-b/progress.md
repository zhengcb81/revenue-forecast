# R4 Phase B 进度（progress）

## 2026-09-12 07:43 — B 阶段启动（设计，DESIGN_ONLY；时间戳为实测，v0.1.2 更正）

- **授权**：owner「接着做 B 阶段，一直做不要停」（2026-09-11 夜）。按 handbook §1 第 5 项 + §3 解释为：**B 的设计可连续推进**；产品代码写入与 `--help` 之外的命令执行**仍需精确批准**。
- **起点**：阶段 A 收口 —— A.DR rev3 = `accepted_with_findings`（0×P0/P1）、owner 六项裁定（G2）已定、A02 封版为 `root-contract v0.4`、CI 全绿（revenue #144 / wiki #103）。
- **本 run 建立**：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-b/`（**不在审计证据目录内**）。

### 1. 本轮交付（全部为文档）

| 文件 | 内容 |
|---|---|
| [task_plan.md](task_plan.md) | B01–B10 状态、B.DR/B.VR/B.AR/D.SAFE 门、停止条件、交付边界 |
| [b-design.md](b-design.md) | **v0.1.1**：B01（含 14 字段 owner/版本映射表）、B02（四段式 + `_handle` 同改 + 禁联网资格判定）、B03（读后复验闭合 TOCTOU）、B04、B05（覆盖整条 UPDATE；持久化决策）、B06（preview 合同归 B06）、B07（范围重划表） |
| [file-scope.md](file-scope.md) | **v0.1.1**：8+1 候选文件的绝对路径、符号、行号、冻结哈希与"是否 A01 冻结项"逐行标注；`policy_2x` 的**在产导出路径**改为禁区首行；owner R-6 的排序锚点分类（11 个） |
| [test-acceptance-map.md](test-acceptance-map.md) | B 步骤 → L/P/O/M 映射、**裁定↔测试绑定表**、反覆盖更正（O03 = 交叉）、完成定义 |
| [risk-and-stop-rules.md](risk-and-stop-rules.md) | H01/D.SAFE 交叉、10 条硬停止、6 类"看起来跑通"陷阱、引用口径更正 |
| [findings.md](findings.md) | **F-B01-1：B.DR 20 条发现逐条处置表**；F-B00-1…5 |
| Phase A 侧 | [a05-corpus-sample-plan.md](../2026-09-11_r4-phase-a/a05-corpus-sample-plan.md)、[a06-baseline-plan.md](../2026-09-11_r4-phase-a/a06-baseline-plan.md)、[command-manifest-readonly.json](../2026-09-11_r4-phase-a/command-manifest-readonly.json) |

### 2. 关键设计结论（一句话版）

1. **B02 与 B05 同根**："位置/优先级被当成业务判据"——B02 把它从**资格**降为**排序**，B05 把它从 **metadata 真伪**彻底移除；两次改动一次收敛。
2. **B03 的字节安全**靠"固定句柄 → 受控快照 → 显式失败"三级，**禁止**只信 mtime/文件名，**禁止**在 query/open 内隐式建快照还宣称零写。
3. **B06/B07** 靠 `preview` 与 `verified_input` 的**资格标签**分离，配一个版本化读取合同 + 边界 adapter；缺 policy **不得**静默退回 `companies`。
4. **B08 的隔离副本不必是 50 GB 拷贝**：机制层用小 catalog（既有测试机制），只有 R1 真实读取需要真实字节——已写入 findings F-B00-3。

### 2b. 实际副作用（v0.1.3 更正为"已发生"，B-DR3-11）

| 动作 | 状态 | 证据 |
|---|---|---|
| 推送本 run 目录（`1b4bab4`/`4c37ca3`/`9d21963`/`472bd206`/`8e3396b`） | **已发生**（`origin/main` = `8e3396b`；CI #145/#146/#147 全 success） | GitHub Actions |
| 推送触发的强制 gate 打开生产 catalog（只读） | **已发生**（`-shm` 前移：2026-09-12 08:32:21 等） | [../2026-09-11_r4-phase-a/boundary-audit.md](../2026-09-11_r4-phase-a/boundary-audit.md) |
| A06-D0 基线运行（`pytest`，CI 等价子集） | **已发生**，且**打开了生产 catalog（只读）**（`-shm` 08:11:45 / 08:13:46） | [../2026-09-11_r4-phase-a/baseline/a06-d0-baseline.md](../2026-09-11_r4-phase-a/baseline/a06-d0-baseline.md) |
| 本 run 内的 CLI（含 `--help`） | **未执行** | 作者声明（无独立观测产物——该限制已登记为 G5） |

> v0.1.2 之前此处用**将来时**描述推送，属陈述失真；现按实际发生登记。

### 3. 本步实际副作用（如实）

- **执行过**：只读文件读取（源码/grep/哈希/行号）、文档写作。
- **未执行**：任何 CLI（含 `--help`）、任何数据命令、网络、产品写入、任务/worker 操作、删除。
- **注意**：本 run 的推送仍会触发 revenue 的强制 pre-push gate，其 real-data 套件会**只读**打开生产 catalog（阶段 A 已归因并披露）。

### 4. 未完成 / 阻塞（不阻塞设计，阻塞实施）

1. **B.DR rev2**（本轮已提交）：v0.1.1 须由**另一名**独立 reviewer 复审，且 rev2 必须基于**新的冻结提交与新输入哈希集**（B.DR 明确要求）。
2. **B 的 DEV 工作包与文件范围批准**（[file-scope.md](file-scope.md)）——owner 一句话即可，之后才能改代码。
3. **隔离副本（G8）**——建议按 findings F-B00-3 分两级；B.DR 已独立复核该技术前提（wiki 既有测试确实用 `tmp_path` 造 catalog）。
4. **A05 样本清单（G7）与只读命令 manifest**——已写好待确认。
5. **A-AR-02 的桥接表**（13 行无法指派 → E01–E13 / U117 / FC903 / CL·AC → L/P/O/M）——A08 的整改项，待做。
6. **B05 的 provenance 持久化**——本轮决定**不落库**；若 owner 要求持久化，需独立工作包（含 `store.py` DDL/迁移）。

### 5. 变更记录（真实时间）

| 时间（本地） | 变更 |
|---|---|
| 2026-09-12 07:43–07:46 | 建立 B run 目录；交付 v0.1 六份文档 + Phase A 三份准备件；提交 `B.DR` 复审（**已推送**：`1b4bab4`/`4c37ca3` 在 revenue #145） |
| 2026-09-12 07:54–08:05 | **B.DR = rejected**（20 条 / 8 条 claim 未复现）、**A07 = accepted_with_findings**、**A08 = rejected**（三份复审共同命中同一 P0） |
| 2026-09-12 08:05–09:20 | 阶段 A → **v0.4.1**（并在 rev2 后 → **v0.4.2**）；B → **v0.1.1** 再 → **v0.1.2**；A06-D0 基线产出（787 unit / 1748 contract passed）；两份 checkpoint 重建（`reviews/**` 纳入产物清单）；上述提交**已推送**，CI #146 success |
