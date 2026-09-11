# R4 Phase A 进度（progress）

## 2026-09-11 — A01 启动（只读）

- **授权**：owner「做R4 主计划」（2026-09-11）。按 handbook §2/§3 解释为**只读 A01 起点**；不覆盖任何写/执行/联网/删除/自启动。
- **建立 run 目录**：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-a/`（**不在审计证据目录内**，符合"不写回本审计证据"）。
- **输入冻结（实测）**：wiki `7d4852f`（干净）、revenue `4c8bc27`（仅运行指针未跟踪）、filing `b44edd8`（干净）；12 个候选定位文件 sha256/字节已记录（见 [baseline-map.md](baseline-map.md) §0）。
- **A01 产出**：主链 query→identify→resolve→open→消费 的 5 跳映射、跨仓子进程 spawn 点、root/kind 分支、9/7 以来"已变更"标记（绝不复原旧 bug）。
- **本步实际副作用**：无。未执行任何 CLI（含 `--help`）、未读写产品数据、未联网、未起进程、未改产品文件。
- **未完成/未知**：
  1. 47 个子命令的逐条副作用矩阵（需 command-manifest 批准后跑 `--help`/`--dry-run`）；
  2. A05/A06 的真实语料与基线 trace（需 owner 精确数据读取许可）；
  3. 错误状态码全集（A06 冻结对象）。
- **下一步（精确）**：
  - **建议顺序**：先请 owner 批准「A 阶段只读数据许可 + command-manifest（仅 `--help`/`--dry-run`）」→ 完成 A01 副作用矩阵 → 提交 **A.DR**（A01–A04 合同文档）→ 再谈 A05/A06 的真实语料。
  - 若不批准执行类动作：可先做 **A02 root-contract 设计文档**（纯文档，不跑命令）。
- **checkpoint**：见 [checkpoint.json](checkpoint.json)。
