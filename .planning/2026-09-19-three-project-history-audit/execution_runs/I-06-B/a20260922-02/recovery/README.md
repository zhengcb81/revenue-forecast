# recovery/README.md — I-06-B / a20260922-02

本 attempt 无持久运行时状态：套件每次运行自带临时 sqlite（`%TEMP%/i06b_*`），证据文件即最终状态。

## 复跑（从 attempt 根目录）

```powershell
# RED baseline（original iso；期望 8G/10R）
python scripts/run_cases.py --iso original --out evidence/red

# GREEN vs fixed 快照2（期望 16G/2R；红=H2,L3）
python scripts/run_cases.py --iso fixed --out evidence/green
```

- 每用例一个 JSON（`evidence/<arm>/<ID>.json`，含 checks/raw/耗时），`summary.json` 汇总计数，
  `run_log.txt` 逐行追加——**增量写**，复跑会追加 run_log、覆写同名用例 JSON。
- 快照完整性：`binding.json` 的 `iso_snapshots` 记录每个被测文件 sha256；若要复现 snap1 绿半场，
  需按 binding 把 `iso/fixed` 还原到 `0b6e723e…`（原文件已随修复卡继续演化，snap1 证据保留于
  `evidence/green_snap1_0b6e723e/`，无需还原即可审读）。

## 中断恢复

1. 若运行中途被杀：`evidence/<arm>/` 中已写完的用例 JSON 均有效（逐用例落盘），直接重跑缺失部分或整臂。
2. 若修复卡继续演化需再刷新快照：重新 Copy-Item → 在 oracle 追加 dated APPEND（先于运行）→ 重跑
   `evidence/green`，旧结果按 `green_snapN_<sha>` 重命名保留（本 attempt 的 snap1 即此流程先例）。
3. 残留 `%TEMP%/i06b_*` 目录可安全删除（纯 scratch）。

## 边界（恢复时同样成立）

零产品写入 · 零历史 attempt 写入 · 无 git · 无网络 · stdlib+sqlite3 only。
