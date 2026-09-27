# CA-004 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。
> 全部实验只读；旧计划目录、产品代码、catalog、roots 零写。

## RED-A：旧 closure 用子串判定自由文本状态 → 66/71 假绿

**证据（2026-08-13 实测）**：

| 事实 | 值 |
|---|---|
| `python tools/closure_gate.py --json` | `closure_gate: FAIL` 但 `accepted_fcs: 66, total_fcs: 71` |
| 判定机制 | `tools/closure_gate.py` 源码：`"accepted" in status`（Markdown 子串） |
| 自由文本状态实例（旧 registry，47 行中 4 例） | `completed_plan_baseline` ×3、`**accepted（-a/-b/-c/-d 全部 accepted 2026-08-12）→ Phase 9 COMPLETE**` |
| 结论 | 任何含 "accepted" 的自由文本都被计为完成——与冻结审计"0 项可直接继承"矛盾 |

## RED-B：FC-1301 自依赖、Phase14 不在状态机、registry 行数漂移

**证据（2026-08-13 实测）**：

| 事实 | 值 |
|---|---|
| 旧 registry FC-1301 依赖列 | `FC-1301(链)` —— 自依赖 |
| Phase14 R0~R9 | 不在 71 行 FC 状态机内（closure_gate 只数 71 行，不验证波次） |
| 旧 registry 当前 FC 行数 | 47（与冻结审计的 71 行口径不符——旧目录仍被其他程序改写的历史证据） |

## 新工具对照（本卡实现）

`uc.legacy_disposition`：解析冻结投影表（71 FC + R0~R9 + FC-150x），机器验证
行数=71、ID 唯一、分类计数精确 I=31/C=26/S=9/P=5、每行 successor 至少一个且
全部在 CA/ZR 注册表中有定义、合并图无环；工件 exclusive publish，source 漂移
检测（三个源文件 hash 与冻结 manifest 一致）。旧 `accepted` 只作历史登记字段，
不进入新状态机。
