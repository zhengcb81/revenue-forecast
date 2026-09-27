# probe_root_* 从仓库根移入本卡 attempt（P2-2 处置）

- **原因**：独立复审 `be4ba16f` 判 P2 —— 仓库根出现 `probe_root_m700/m777/m777kw`（创建 2026-09-25 21:54:02，1 B 探针文件），**位于 `.planning` 之外**，且 `analysis.md §8.4` 未披露。
- **卡文写入面**（`card_I-14-E-TESTSIDE.md`）= 本卡 attempt 目录 + `iso/`；**仓库根不在其内** ⇒ 属越界写。
- **处置**（仿 D-1 先例：**先保全证据、再清产品树**）：把字节原样**移入** `evidence/probe_root_removed_from_repo_root/<dir>/`（sha256 逐件记于 `PROBE_ROOT_REMOVAL.json`），随后删除仓库根的 3 个目录。
- **未销毁任何证据**：文件被**移动**而非删除，原 sha 在 JSON 内可核。
- **git 面**：这些目录本就 **untracked**，`git diff HEAD --name-only` 非 `.planning` 处置前后**均为 0**（已复测）。
- **本处置由父执行**，**不改卡的任何裁决**；`VERDICT: blocked` 与 P2-2 的定性**原样保留**，重交时仍须按复审恢复条件 ③ 修正（探针原始输出落盘 + `probe_root_*` 披露）。

## 补充：`probe_root_m700` **未能清除**（如实登记）

- `probe_root_m777` / `probe_root_m777kw` **已移入本目录并从仓库根删除**（1 B 各一件，sha 记于 `PROBE_ROOT_REMOVAL.json`）。
- **`probe_root_m700` 删不掉**：该目录以 **mode `0o700`** 创建，本会话无法访问 —— 与本卡 `handoff` 披露的 `%TEMP%\i14ets*`、`probe_att_m700` 残留**同因**。
  - `Get-Acl` → `Attempted to perform an unauthorized operation`；
  - `icacls /reset /T` → **rc=5**（access denied）；
  - `[System.IO.Directory]::Delete(recursive)` → `Access to the path ... is denied.`
- **状态**：仍在仓库根，**空目录**（本会话从未见到其中文件）。
- **git 影响**：untracked 且为空 ⇒ `git diff HEAD --name-only` 非 `.planning` **仍 = 0**（已复测）。
- **不伪造已清除**：本 README 与 JSON 同时登记失败；若日后在有权限的上下文中可删，由届时的父/owner 处理。
