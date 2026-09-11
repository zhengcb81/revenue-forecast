# R4 Phase A 运行计划（task_plan）

> 运行目录：`revenue-forecast/assurance/runs/2026-09-11_r4-phase-a/`（未来获准 run 目录；**不写回审计证据目录**）
> 权威来源：[R4 执行计划](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-execution-plan.md) · [真实测试矩阵](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md) · [接班手册 §2/§3](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/execution-handbook.md)
> 状态：**A01 已启动（只读）**；阶段整体仍 **NOT_IMPLEMENTATION_AUTHORIZED**

## 授权边界（本 run 生效）

- 本次授权（owner 2026-09-11「做R4 主计划」）**仅覆盖只读的 A01 基线映射**：读代码/配置、记录 hash、映射调用链。
- **不包含**：产品代码/配置/DB 写入、任何 CLI 执行（含 `--help`/`--dry-run`）、网络、下载、LLM、任务注册、自启动、删除、外发。
- 按 handbook §2.5：**首次实施前须由 owner 批准精确 DEV 工作包与文件范围**；本 run 不越过该门。

## A 阶段 8 步与状态

| 步骤 | 动作 | 产出 | 状态 |
|---|---|---|---|
| **A01** | 重核三仓代码/配置，映射 query→identify→resolve→open→消费、子进程/hash、root 分支与副作用 | `baseline-map.md` | **部分完成**（主链+哈希+root 已映射；47 子命令副作用矩阵待 command-manifest） |
| A02 | 冻结四个已批准 root 的读取等价；root capability 与文档证据质量分开；显式 deny/未注册 root 不放行 | root-contract | 未开始（需 A01 收口 + A.DR 前置） |
| A03 | 定义 `query_local` / `open_version` / `request_work` 三接口；本地 latest 只指已索引集合 | operation-contract + 副作用表 | 未开始 |
| A04 | 定义对外引用 `document_id` + 版本/source hash + locator；路径诊断不入业务身份 | identity-contract | 未开始 |
| A05 | 独立 Data-Agent 从**真实资料**挑报告/版本并标注 | corpus-manifest + 独立 oracle | **阻塞**：需精确数据读取许可 |
| A06 | 冻结 L01–L12 本地测试与错误状态；生成小型只读 trace/profile（禁止整库重复扫描） | 每例基线结果 | **阻塞**：需数据读取许可 + command-manifest |
| A07 | 独立 VR 核查询/读取的身份-字节-来源合同；preview 不扩大正式分析/LLM 许可 | 设计负例与副作用审查 | 未开始（需独立 reviewer，实现者不得自签） |
| A08 | 独立 AR 签"合同/基线可供实施"；生成旧目标→阶段/test 初版映射 | 只解锁 B 的目标明确性 | 未开始 |

## 阶段门（不可自签）

- **A.DR**（设计审查）：A01–A04 合同文档完成后提交，需独立 reviewer。
- **A.VR/AR**：隔离验证与真实结果验收；A05/A06 涉及真实语料，需 owner 精确许可。
- 记录要求：真实 task/agent ID、输入 hash、原始结果、verdict；**名字字符串/未回复/用量中断不计通过**。

## 停止条件

- 需要写产品文件 / 起进程 / 联网 / 读真实语料正文 / 触碰 worker·任务·自启动 → **停并请授权**。
- 发现并发漂移（HEAD 变化、他人在写同一文件）→ 重审受影响部分，不覆盖别人变更。
