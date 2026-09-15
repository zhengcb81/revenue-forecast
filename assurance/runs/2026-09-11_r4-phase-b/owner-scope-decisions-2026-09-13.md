# Owner 裁定记录（2026-09-13/14，第三批：十项）

> 本轮由 owner 对"要我裁定什么"那张十项表整体回以「**批准**」= 按表内**建议列**执行。
> 记录纪律：每条写**裁定内容**、**它授权了什么/没授权什么**、**落在哪**。未获授权的部分**不**顺手做。

| # | 事项 | 裁定 | 授权 / 边界 | 落点 |
|---|---|---|---|---|
| 1 | **G8 隔离副本** | **批准两级**：① 机制层在非生产路径建小 catalog（**可立即开工**）；② 真实字节在隔离根下**只读**引用（另批） | 授权 B08/B.VR 的**机制层**开工；**未**授权任何生产 catalog 写入、未授权复制/移动真实语料 | [task_plan.md](task_plan.md) B08 行；机制层计划见 §B08 |
| 2 | **G7 = A05 样本清单 + 只读命令 manifest** | **确认清单照写**；命令**逐条批**（本次不批任何命令） | 授权把 A05 清单定为权威；**未**授权执行 manifest 中任何命令 | [../2026-09-11_r4-phase-a/a05-corpus-sample-plan.md](../2026-09-11_r4-phase-a/a05-corpus-sample-plan.md)、[../2026-09-11_r4-phase-a/command-manifest-readonly.json](../2026-09-11_r4-phase-a/command-manifest-readonly.json) |
| 3 | **G5 边界观测** | **做**（独立、只读） | 授权派一个**独立会话**做只读边界观测并出记录；**未**授权它执行任何 wiki CLI 或写产品 | `reviews/G5-boundary-observation.json`（本轮派出） |
| 4 | **G6 指派原件** | **出一份常设指派记录** | owner 侧文件；本轮先出**草案**待 owner 一句确认，**不**代替 owner 签署 | `operator-reviewer-assignment-DRAFT.md` |
| 5 | **`preview` 不可达** | **维持现状**（已定义、不可达 + 登记） | 不改跨仓 `capture_incomplete` 门、不加新入口 | 已登记于 [findings.md](findings.md) F-B06-1/B06 段 |
| 6 | **未知 `schema_version` 用裸 `ValueError`** | **维持现状**（编程错误用 ValueError，解析结果用合同五值） | 不改合同、不改用例 | 已登记于 findings B07 P2 段 |
| 7 | **FC-1301 词表门加宽 + 位置式 reason 注册** | **立项**（独立工作包） | 授权**写工作包**（范围/验收/风险）；**未**授权实施（动 `observability.REASONS` + taxonomy 版本号，属产品改动） | `packages/fc1301-taxonomy-coverage.md` |
| 8 | **B05 读侧畸形共享列抛异常** | **立项**（独立工作包） | 同上：先出包，实施另批 | `packages/b05-read-side-malformed-columns.md` |
| 9 | **日常 T2 是否同样分档** | **套用**（与周度一致） | 授权改 `tools/daily_t2_schedule.py` + 用例 + 变异证明 | 本轮实施并提交 |
| 10 | **B10**（单一读取链） | **按原计划等**（B.AR 通过后） | 不提前开工 | [task_plan.md](task_plan.md) B10 行 |

## 本次裁定的直接后果（写清楚，避免以后误读）

- **可以立即开工**：#9（已做）、#1 的**机制层**、#3 的观测会话。
- **仍然被门挡住**：B08 的**真实字节**部分（G8 第②级未批）、B09/B.AR（G7 命令未批）、B10（等 B.AR）。
- **本轮不实施**：#7、#8（只出包，等 owner 对包的一次 go/no-go）。
- **owner 侧待办**：#4 的草案确认（一句话）。

## 未在本次裁定内、也不自行推进的事项

- 任何**产品写入/删除**、任何**数据命令**、manifest 里的只读命令、生产 catalog 的任何写、任何**跨仓合同**变更。
- 三仓 CI 的进一步加门（现已在 commit/push 链路 + 仓内契约测试；owner 未要求再加）。
