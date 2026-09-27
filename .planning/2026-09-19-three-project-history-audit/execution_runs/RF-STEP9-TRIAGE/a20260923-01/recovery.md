# RECOVERY — RF-STEP9-TRIAGE / a20260923-01

## 现态（自洽声明）
- RF 生产树: **零写入**（porcelain 与 `evidence/porcelain-baseline.txt` 一致；`git apply --check` 只读通过）。
- 本 attempt 目录 = 全部交付物；`changes.diff` 自足可应用（base b0d016a6，7 文件在 b0d016a6..977fa1e8 间未变 → 生产 HEAD 可直接 `git apply`）。
- WSL `~/company-wiki` = `5d72529`（iso_env wiki_after + close 复核双证）；`~/rf-ci-repro` = `b0d016a6`（未被本卡改动）。
- %TEMP% 脚本与补丁器保留: `ci_repro_step9_*.sh` · `ci_step9_iso_patch.py` · `ci_step9_iso_run.sh`；`%TEMP%\s9win`（Windows 臂克隆）保留。
- /tmp 沙盒（s9lay/s9mis/s9iso/s9isomis）为一次性，WSL 重启即清——**不需要恢复**，脚本幂等可重建。

## 若中断/重跑
1. 读 `oracle.md` → `decision.md` §1 终表（所有结论已落盘，不依赖内存）。
2. 复现单文件: `wsl -- bash %TEMP%\ci_repro_step9_files_head.sh`（主臂）；raw 即写 `evidence/`。
3. 复验修案: `wsl -- bash %TEMP%\ci_step9_iso_run.sh`（重建双布局 → 断言补丁 → 全绿 → 重导 changes.diff；步 0 自动恢复/断言 wiki=5d72529，遇父方新 sha 即 abort 不翻动）。
4. 守卫型对照: `ci_repro_step9_mis46_cipin_env.sh`（wiki≠5d72529 时只记 env_facts 拒跑——保留此行为）。
5. Windows 臂: `%TEMP%\s9win` 若在则直接重跑 win2 循环；若丢，按 commands.md §4 重建（clone --no-checkout + 本地 fetch 5d72529 + co）。

## 翻动恢复（本卡造成的已知翻动均已还原）
- `~/company-wiki` 曾被 `cipin.sh` 留在 31c0afcb（未及恢复）→ 已由 iso_run 步 0 恢复 5d72529 ✓（`evidence/iso_env.txt`）。
- 若父方已把 wiki 推到更新 sha: 上述脚本守卫会 abort 并记 `env_facts.txt`——**不要手工改回**，以父方 sha 为准并重跑对应 raw。

## 生产回滚
无需（RF 未动）。若落地卡应用 changes.diff 后需回滚: `git checkout -- <7 文件>`（diff 即完整反向依据）。
