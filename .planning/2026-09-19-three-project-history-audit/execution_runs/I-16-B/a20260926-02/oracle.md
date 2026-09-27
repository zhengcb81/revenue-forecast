# I-16-B a20260926-02 —— 部署执行 oracle（**事后补记，如实标注**）

> **冻结状态**：本文件在**部署执行之后**写入（P3：本 attempt 未事前独立冻结 oracle）。
> **实际执行依据（执行前已冻结）**：① `OWNER_DECISIONS §三十九`（owner 批 `R1-R8` 全量）② `execution_runs/I-16-A/a20260926-01/deployment_proposal.md`（`accepted_scoped`，sha 见其 handoff）③ `impact_scope.json`（`production_change_executed=false` 时点快照）
> 以上三件均为**执行前已冻结**的有效判据；本文件仅记录执行过程与结果，**不追改任何判据**。

## 执行窗口
- 起：R6 备份完成（`catalog.sqlite3` `sha 63c359aa` 一致，4.4s）
- 记录时刻（UTC）：2026-09-27T06:29:31Z

## 步骤与结果（逐条）
| # | 步骤 | 结果 |
|---|---|---|
| S1 | R4 门：重绑组合（`RF:b7a6a116/dirty=48 · CW:dbe4745/dirty=109 · DAYU:2115c86/dirty=2`，artifacts=31） | **J1–J8 `rc=0` 全绿** |
| S2 | R5：按**完整相对路径**重跑快照还原 | **GREEN**（109 行→109 唯一目的地、0 碰撞、写前写后 0 失配）——**原 drill `basename` 覆盖缺陷经代码实证（`_recovery_drill.py L42`）并修复** |
| S3 | R6：`catalog.sqlite3` 备份 | `sha 63c359aa…` 与源一致（记录 `r6_backup/catalog_backup.json`） |
| S4 | 入口 shim ×4（`dayu-cli/render/web/wechat`） | 4/4 加载并执行；`--help rc=0` |
| S5 | `dayu-cli sessions` | **受环境限制**（`workspace` 不存在于 rf / `~/.edgar` 拒写 / `host_store` 拒写）——`EDGAR_LOCAL_DATA_DIR` 改道证明**部分为沙箱伪象**；根因链完整留档 |
| S6 | **已有复用**（卡文 L9①） | **3/3 `capture_ready`**：`ZIJIN AR2024` · `ZIJIN AR2025` · `MSFT FY2025`（各含 `content_sha256`/`location urn`/`collector`） |
| S7 | **新文件摄取**（卡文 L9②） | **3 次失败，全部为早于本会话的既有缺陷**（见下 `findings`） |
| S8 | **工件失效最小重算**（卡文 L9③） | **未观察到实况失效事件 ⇒ `unverified`**（机制在位：`artifacts 8191` 行 + `producer_events`/`activation_journal` 表；无安全触发方式且不伪造） |
| S9 | worker 状态 | **`desired_state=paused` 维持**，**未启动/未停止/未无条件 resume**（卡文 L8） |

## findings（S7 三失败，逐条排除本会话改动）
1. **`ZIJIN SA2025`**：CN 路由 `calls=3 downloads=0` —— 数据可得性（`AR2024/AR2025` 可得 ⇒ 非路由故障）
2. **`MSFT 10-K FY2026`**：`canonical_import_failed`（`canonical_path` 空、文件落带哈希后缀名）—— **canonical 名被 2026-09-19 已有文件占用**（mtime 实证早于本会话 5 天）；且**该 09-19 文件本身也未入索引**（复用 `not_found`）⇒ 长期既有
3. **`MSFT 10-Q FY2026`**：`dayu CLI 不支持的 form_type: ['10-Q/A']` —— 代码在 **`dayu/fins/pipelines/sec_form_utils.py L107`，`mtime 2026-05-30`**（4 个月未动、**非 B2 晋升文件**）⇒ 非回归

## 边界自证
零 git 写（三仓 `git diff HEAD --name-only` 只读：`RF 3830/非.planning 0` · `CW` 含本次授权摄取写入 · `DAYU 2115c86` 未动）· **`dayu-agent` 未提交未修改**（owner 指令）· 未放行参数 · 未代 `I-14-E` 出结论 · 未派 `I-17-A` · 封盘 `f2178768…` 零字节 · 恢复路径：`R6` 备份 + `R5` GREEN + `I-16-A` 演练
