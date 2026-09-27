# recovery.md — WC-4 = F12-RC120

**原则**：生产 RF 全程零写（已证），所以「恢复」只有两件事——① 重建/撤销本 attempt 的 iso 与证据；② 若父批次已把 `changes.diff` 落到生产，给出反向路径。

## 0. 磁盘布局

```
<PLAN>\execution_runs\WC-4-RC120\a20260923-01\
  oracle.md  oracle.sha256  binding.json  commands.md  decision.md
  changes.diff  handoff.md  recovery.md  evidence\  harness\
  iso\rf\            <- RF 生产镜像（本卡唯一被改的代码树 = 修复态）
  iso\filing-fetch\  <- 同级技能检出副本（家族 2 个环境依赖测试需要）
```
- 临时只用 `%TEMP%`（`mech_case.py` 的 snippet 目录）与 attempt 内 `evidence\rgm\stdout|registry|...`。
- **无 git**：所有校验用 sha256 + difflib。

## 1. 完整重建（从零重跑 rgm）

```powershell
cd C:\Users\郑曾波\Projects\revenue-forecast
$A='.planning\2026-09-19-three-project-history-audit\execution_runs\WC-4-RC120\a20260923-01'

# 1) 复算冻结件（应与本文件记录一致）
(Get-FileHash -Algorithm SHA256 "$A\oracle.md").Hash.ToLower()
#   7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8

# 2) 重建 iso（如被删除）
robocopy (Get-Location) "$A\iso\rf" /MIR /XD .git .planning .pytest_cache .mypy_cache .ruff_cache .codegraph .benchmarks .workbuddy-ai __pycache__ venv .venv node_modules /XF NUL /NP /NFL /NDL /NJH
robocopy 'C:\Users\郑曾波\Projects\filing-fetch' "$A\iso\filing-fetch" /MIR /XD .git __pycache__ .pytest_cache /NP /NFL /NDL /NJH

# 3) 阶段（顺序不可换：iso 源在阶段间被改写）
python -B "$A\harness\make_input.py"                # 生成共享合法输入
python -B "$A\harness\probe_wc4.py" --stage red     # 期望 rc=0，F12=120（红）
python -m pytest "$A\iso\rf\tests\test_stdout_flush_exit_domain.py" -q -p no:cacheprovider   # 期望 6 failed, 2 passed
python -B "$A\harness\apply_fix.py" apply           # iso: pristine -> fixed
python -B "$A\harness\probe_wc4.py" --stage green   # 期望 F12=2
python -m pytest "$A\iso\rf\tests\test_stdout_flush_exit_domain.py" -q -p no:cacheprovider   # 期望 8 passed
python -B "$A\harness\apply_fix.py" revert          # MUTATION-1（字节=pristine，与 RED 同态）
python -B "$A\harness\probe_wc4.py" --stage mut1    # 期望 F12=120 + 测试 6 failed/2 passed
python -B "$A\harness\apply_fix.py" apply; python -B "$A\harness\apply_fix.py" mutate2      # MUTATION-2
python -B "$A\harness\probe_wc4.py" --stage mut2    # 期望 F12=120（文本在）+ 测试 2 failed/6 passed
python -B "$A\harness\apply_fix.py" apply           # 终态回 fixed（status 应= state=fixed, sha 4e6b64a7…）
python -B "$A\harness\make_diff.py"; python -B "$A\harness\verify_diff.py"
python -B "$A\harness\check_ratchet_own_file.py"    # 期望 OWN_FILE_RATCHET_OK（18<=18）
```

家族（before=未修、after=已修，同一 iso 同一环境）：
```powershell
$files=@('test_industry_end_to_end','test_publication_pipeline','test_verbose_validation','test_zr701_f1_draft_formal','test_zr704_validate_only_gate','test_zr710_publication_txn','test_zr803_chaos_recovery','test_zr804_platform_shape') | ForEach-Object { "$A\iso\rf\tests\$_.py" }
python -m pytest @files -q -p no:cacheprovider
python -B "$A\harness\compare_family.py"            # before/after 逐行比对
```

## 2. iso 状态机（唯一可改的代码树）

| 状态 | sha256(revenue_forecast.py) | 如何到达 |
|---|---|---|
| pristine（=生产） | `2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36` | robocopy 镜像 / `apply_fix.py revert` |
| **fixed（交付态，当前）** | `4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977` | `apply_fix.py apply` |
| mutate2（变异体） | `347400d6059e661e0fe3328bc4ef902c0a7c3b1c8a1bc62b42dedee1c0cc0507` | fixed 后 `apply_fix.py mutate2` |

- 权威 pristine 快照：`evidence\rgm\cli_original.py`（sha 同 pristine）——`apply_fix.py revert` 只认它；快照若损坏，直接重跑第 2) 步的 robocopy。
- **若忘记从 mutate2 恢复就跑 green**：判据会红（本卡真实踩过一次，见 commands.md P1 ❌C10-try1）；恢复=重跑 `apply_fix.py apply`（已改为从 pristine 重建，锚失败不再可能）。

## 3. 生产侧恢复（若 changes.diff 已被父批落地）

1. 生产原字节可从本卡 `evidence\rgm\cli_original.py` 取回（sha 与 binding pin 互证）。
2. 新增测试文件 `tests\test_stdout_flush_exit_domain.py`：**删除该文件**即可回到交付前状态（生产在本卡结束时确无此文件，见 `production_zero_write_after.txt`）。
3. 复算：`scripts` 树 sha 应回到 `d29e761d20d0b00c397ad43109008f0575cca91cf71f31cfc3a658fa81470564`、`tests` 树 sha 回到 `a0d7667ceaf0d7f321ae0212727affa4a18f79bb4c7ade8813d00f2cc5292950`（注意：这两值是本卡时点快照；若其间有其它卡落地，以彼时清单为准）。

## 4. 放弃整卡（anti-death / 重开）

- 直接删除 `iso\`（约 64 MB）即可；`evidence\`、`harness\`、8 件套都在 attempt 目录内，自足可复审。
- 生产树**从未被本卡写入**（`production_zero_write_before/after.txt` 双证），故无需回滚生产。
- 若复审判 `changes_required`：改动面=2 文件，按复审意见重出 diff（`make_diff.py` 重新生成）即可，oracle/binding 不动（形态判据未变）。

## 5. 出事时的求证顺序

1. `oracle.sha256` 是否仍匹配（冻结未被偷改）→ 2. `binding.json` 的 `prod_cli_before` 是否 == 当前生产 CLI sha → 3. `evidence\rgm\<stage>\probe.json` 的 `iso_cli_sha256` 是否对应表 §2 的三态 → 4. `family_compare.txt` 的 diff 是否仍只有时间行 → 5. `commands.md P1` 是否含失败尝试披露（3 次，见 handoff §2/§4）。
