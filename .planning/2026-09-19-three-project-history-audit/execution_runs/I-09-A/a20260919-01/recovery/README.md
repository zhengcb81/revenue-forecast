# recovery/README.md — I-09-A / a20260919-01

## 结论：本卡**没有需要恢复的产品状态**

卡片原文（恢复边界）：**「仅修改本次设计文档；旧包/registry 只读；不预先迁移生产历史」**。

本 attempt：

- **产品仓改动 = 0**，生产 registry 零写入（前/后 sha256 均为 `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`）；
- 没有发布任何 artifact、没有启动 provider/worker、没有取任何锁、没有执行任何产品命令；
- 因此不存在「异常后需要回滚的持久状态」。

按 `review_and_handoff.md` 的目录要求，本文件给出**本 attempt 自身产物的撤回与恢复步骤**（供 owner / reviewer 使用）。

## 1. 撤回本 attempt 的全部影响

| 影响 | 位置 | 撤回动作 |
|---|---|---|
| attempt 目录（证据） | `<PLAN>\execution_runs\I-09-A\a20260919-01\` | 保留（证据不得删除）；如需彻底撤回，删除整个 attempt 目录即可，**产品仓无需任何动作** |
| 隔离 venv | `<attempt>\iso\venv` | 可删（删除后无法复跑探针；建议保留至 reviewer 完成复跑） |
| 隔离副本 | `<attempt>\iso\rf\scripts` | 可删；重建方式 = 重新 `Copy-Item` 产品 `scripts/` |
| 探针 scratch（含所有 case 私有 registry） | `<attempt>\iso\scratch\`（`probe`、`probe2`、`smoke`、`addendum`、`tmp`、若干 `dirread*`） | 可删；**注意**：删除后 `after/probe_commit.stdout.txt` 与 `after/probe_commit_report.json` 仍是原始证据（它们是拷贝件） |
| 冻结的目录联结 | `C:\i09a`（NTFS junction → 本 attempt 目录） | `cmd /c rmdir C:\i09a`（**只删联结，不删目标**）。最终探针**不依赖**它 |
| ACL 变更 | `<attempt>\iso\scratch\addendum\reg_acl` | **已复原**并在复核中确认无 `DENY` 行；若发现残留：`icacls <path> /remove:d <user>` |

## 2. 复跑与漂移处理

1. 复跑前**必须**重算 `before/baseline_hashes.txt` 里登记的生产锚点 hash；若 `scripts/revenue_core.py` / `revenue_forecast.py` / `publication_registry.py` 任一变化 → 按 `START_HERE` 漂移分支**停止复跑**，记录新旧 hash 与差异，交 reviewer 重审 oracle。
2. 复跑使用**新的** `--work` 目录（例如 `--work <attempt>\iso\scratch\probe3`），**不得**复用旧 case 目录（否则故障注入物与残留 registry 会污染结果）。
3. 复跑后请与 `after/probe_commit_report.run2.json` 做**不变量比对**（case、producer_rc、registry 行数、成员存在性、读者 9 项），而不是比对字节。
4. 若复跑出现不同**结论**（不只是不同 hash），保留两次原始输出，交 owner 定位，**不得**择一发布。

## 3. 异常情形的确定动作

| 情形 | 动作 |
|---|---|
| 探针在写 case 文件时失败 | 该 case 记录为失败；**不得**换 fixture/公司/口径重跑以求 PASS |
| registry 链在 scratch 内损坏 | 删除该 case 私有 registry 重跑；**绝不允许**对生产 registry 做任何修复 |
| 发现生产锚点漂移 | 停止，保留现场，登记 drift（本 attempt 已核验：8/8 锚点前后一致、43/43 隔离副本一致） |
| 并发 burst 出现链断 | **保留** scratch 与两份 stdout，登记为失败证据；不得重跑抹掉 |
| 同一失败连续两次 | 停止盲重试，交 owner（START_HERE「两次相同失败」分支） |

## 4. 本 attempt 明确的**不**恢复项

- **不**回滚、**不**编辑、**不**删除生产 `artifacts/registry/publications.jsonl` 的任何历史行。
- **不**对 60 行旧记录补算 `publication_id`（那会伪造历史，见 `decision.md` §5.5）。
- **不**预先迁移任何生产历史（卡恢复边界原文）。
