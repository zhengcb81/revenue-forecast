# COMMANDS — RF-STEP9-TRIAGE / a20260923-01（增量记录；每步即写）

基座: CI step9 选集 = `%TEMP%\ci_repro_step9c.sh` 逐字（= quality.yml L36-59），文件级 = 同环境 `python3 -m pytest <file> -q` + `PYTHONPATH=$HOME/company-wiki/src`。
所有 WSL 脚本落 `%TEMP%\ci_repro_step9_*.sh`；raw 落 `evidence/`，头含 `rf_sha/wiki_sha/cmd/date_utc`。

1. **主臂 12 复现**: `wsl -- bash /mnt/c/.../Temp/ci_repro_step9_files_head.sh` → 8 文件 12 失败（RC 逐一写 raw）→ `wsl_head_*`。
2. **布局沙盒矩阵**: `ci_repro_step9_sandbox.sh`（/tmp/s9lay 规范名克隆+兄弟符号链接；顺序: b0d016a6→fc×2 · 46bd8b16→全 8 · 8b7229c3→zr601/zr708 · 70dd9f6e→同2 · 95df2661→A族4 · ec307d20→同4；wiki 每跑 before/after 钉 5d72529）→ `wsl_layhead_fc_*` `wsl_anchor46_*` `wsl_pre70dd_*` `wsl_at70dd_*` `wsl_preEc3_*` `wsl_atEc3_*`。
3. **兄弟对照（v 类排除）**: `ci_repro_step9_oldwiki.sh`（wiki→31c0afcb，主臂 8 文件，跑毕恢复 5d72529）→ `wsl_oldwiki_*` 全红同签名。
4. **Windows 臂**: pwsh `git -c core.longpaths=true clone` RF→`%TEMP%\s9win\revenue-forecast`@b0d016a6；filing 钉 89c8bdb2；首跑 wiki 检出中断（wcheckout_rc=128, wco.err `unable to read tree`）→ `win_head_*` fc×2 判废保留；**修复** = 本地 `git fetch C:\...\company-wiki 5d72529` + co（rc=0, src 在）→ **win2 全 8 重跑** `win2_head_*`：fc×2 **RC=0**、余 6 **RC=1 同 WSL 签名**。
5. **错名锚点对照**: `ci_repro_step9_misname46.sh`（/tmp/s9mis/rfclone 非规范名@46bd8b16）→ fc×2 **RC=1**（raw 头 wiki=5d72529）= 错名布局下末绿锚亦红 → 与 sha 无关实证 ✓。
6. **CI 钉对照（cipin）**: **弃跑**——`%TEMP%\cipin.log` 记两番 `/tmp/s9lay` 被 WSL 重启清空致 cd 断（首番还把 wiki 留在 31c0afcb 未及恢复，见事件①）；机制与 wiki 正交 + oldwiki 臂已覆盖钉维度 → 冗余，理由入 decision §2 / binding。
7. **git 归因**: `git log -S/-L/blame` 批量 → `evidence/git_anchors.txt` ✓。
8. **iso 小修**: `ci_step9_iso_patch.py`（逐串 count 断言，H5c 为 regex 容错）+ `ci_step9_iso_run.sh`：步0 恢复/断言 wiki=5d72529 → 双布局克隆 → 8 hunk 全 APPLIED + py_compile 过 → **绿 8**: `iso_ok_{receipt,zr1102,zr601,zr708}` RC=0、`iso_ok_fc{1102,1302}` RC=0（规范回归）、`iso_misfix_fc{1102,1302}` RC=0（错名翻绿）→ patrol CLI `PATROL_RC=0` → 导 `changes.diff`（7 文件 8 hunk, 5423B）。
9. **close**: `porcelain_close.txt` + 方向性 `porcelain_delta.txt`（产品/测试/工具路径零命中）+ `git apply --check` rc0 + wiki/rf 复核（5d72529 / b0d016a6）。
10. **事件**: ①`cipin.sh` 留 wiki@31c0afcb 未还（`cipin.log`+`env_facts.txt`）→ `mis46cipin_env.sh` 守卫拒二次翻动 → iso 步0 恢复（`iso_env.txt`）②WSL HCS 超时/重启多次 → /tmp 沙盒每次重建（脚本幂等）③重复的 mis46cipin 调用=无害重跑同结果（其间一次瞬态 RC=4 后被两次 RC=1 覆盖）④#8 首轮 H6 编辑被策略拒→五跑=基线等价（`guard_run.log` 无效轮），读文件重打后 `guard_run2/3.log`=六证有效轮 ⑤changes.diff 头部 PS5.1 ANSI 吞换行→corrupt-at-93 → bash 字节安全重导修复（事件详 decision §7.4-5）。
11. **#8 守卫收窄执行（owner 裁定(2), OWNER_DECISIONS §22/§84）**: `ci_step9_guard_run.sh`（幂等重建 iso → 普查读证 `guard_readproof.txt`：实现=仅 `tests/test_single_owner_guard.py`(G1)、subprocess 面=3 文件(2 豁免+revenue_core)、revenue_core 12/12 领域词 hits=0、canonical client=thin subprocess CLI → 10 补丁+py_compile → `run_guard`×5 变异序列（G1/B1/B2/M1/M2）→ 终绿 8 文件+patrol+attestation 未触对照 → 错名/规范 fc 回归 → 导 changes.diff + 晋升面零字节核）。
12. **changes.diff 终导（字节安全）**: `ci_step9_changes_finalize.sh` = 重跑守卫脚本重生 pristine body → **bash** `cat` header+body（弃 PS5.1 ANSI，吞换行事故见事件⑤）→ `git -C RF apply --check` **rc=0** → 计数核（8 文件/9 hunk/CJK 探针）→ `ci_step9_hunkfix.sh` 修正 10→9 hunk 措辞并复验 rc=0。#8 状态载体=**`handoff_guard8.json`（追加件，引用基判 handoff.json sha 前缀 3942a338；绝不覆写 handoff.json=父方防覆盖令）**。
