# evidence/ — WC-4 = F12-RC120 证据索引

逐文件 sha256 见 `MANIFEST.sha256`（本目录 + 子目录全量）。分组如下：

## A. 冻结与绑定
- `pins_freeze.txt` —— binding 19 个 pin 的**逐行原文**（I-09-A F12 冻结行、owner §22/§23、REGISTRY §八十四 F12 行、WC-4 规格、owner-vote register note、SA-DEFECT 错措辞行、I-09-C handoff/pipe_controls/reviewer、probe_f12.py:64-66、生产/iso CLI 全文 pin）

## B. 地面真相（oracle 冻结**前**的复核，如实披露为 phase0）
- `mech/mech_cases.json` —— 5 个无 RF 代码片段 × 3 种 stdout 汇：M0=120、M1=120、M2/M3=2（修复形态）、M4=120（只 catch 不够）
- `mech/grep_120_and_emitter.txt` —— 产品源 `120` 全是 FC-120x、退出码形 0 命中；`Exception ignored on flushing sys.stdout` 字面量命中 `python313.dll` offset 5921656（dll sha `d97a9810…`）
- `probe_f12_line65_fix.diff` —— I-09-C 封存 harness 的 C.stderr 误标修正（交付不改封存字节）

## C. 红绿变异（每阶段 `probe.json` 含 `checks` 与机械 verdict）

> 产品测试两版：**v1**=3 个子进程用例（证据文件改名 `*_v1_subprocess_only.txt` 留档）；**v2**=8 用例（3 端到端 + 5 in-process 单元守卫；动机=coverage 子进程钩子本机未生效，见 commands P1）。

| 阶段 | 文件 | 关键观测（v2 口径） |
|---|---|---|
| RED（=pristine 字节） | `rgm/red/probe.json`、`rgm/red_probe_console.txt`、`rgm/red_pytest_newtest.txt` | F12=**120**、`Exception ignored` 在；产品测试 **6 failed, 2 passed**（端到端 `got 120` + 5 个 helper 缺失） |
| GREEN run1 | `rgm/green/probe_run1_after_fix.json`、`rgm/green_probe_console.txt`、`rgm/green_pytest_newtest.txt` | F12=**2**、产品文本在、无 `Exception ignored`；**8 passed** |
| GREEN 终版 | `rgm/green/probe.json`、`rgm/green_probe_final_console.txt`、`green_pytest_final.txt` | 同上（run1 与终版 `probe.json` sha 相同 ⇒ 可复现） |
| MUTATION-1（整体回退，字节=pristine 与 RED 同态） | `rgm/mut1/probe.json`、`mut1_probe_console.txt`、`mut1_pytest_newtest.txt` | 120 复现 + **6 failed, 2 passed** ⇒ 捕获 |
| MUTATION-2（只留 catch、去换流） | `rgm/mut2/probe.json`、`mut2_probe_console.txt`、`mut2_pytest_newtest.txt` | 文本在、仍 120；测试 **2 failed, 6 passed**（恰为两条半承重断言）⇒ 两半都承重 |
| ❌失败尝试（不作证据） | `rgm/*_failed_mutant_leftover*` 三件 | mutate2 未回退就跑 green ⇒ `GREEN_NOT_MET`；已改名归档 |

`rgm/cli_original.py` = pristine 快照（sha 与生产 pin 同）；`rgm/input_valid.json` = 共享合法输入；`rgm/stdout|registry|...` = 各阶段产物（法式 N5 等）。

## D. 回归家族（8 个 grep 命中文件）
- `rgm/family_before_raw.txt`（未修 iso + sibling 检出）= **64 passed, 48 subtests**
- `rgm/family_after_raw.txt`（已修 iso、新测试 v1 版在盘）= **64 passed, 48 subtests**
- `rgm/family_final_raw.txt`（**终版 iso 树**，cli=`4e6b64a7…` + 新测试 v2 版在盘）= **64 passed, 48 subtests**
- `rgm/family_compare.txt` = before vs **final** 逐行 diff（**仅 wall-clock 两行不同**；0 skip/xfail）；`family_compare_v1testfile.txt` = before vs after-v1（同样仅时间行）
- 三日志为 PowerShell `*>` 重定向的 UTF-16，解码比对脚本 = `harness\compare_family.py`（可传路径参数）
- 披露：家族 try1（iso 缺 sibling `filing-fetch` 检出）2 个环境红、原始日志被 try2 同名覆盖 → 摘要在 `commands.md P1 ⤴C4-try1`

## E. 质量与完整性
- `rgm/ruff_fixed_files.txt` —— ruff 0.15.18（CI 钉版）两文件 `All checks passed!`（rc 0）
- `rgm/ratchet_iso_failure.txt` —— `tools/tests/test_complexity_ratchet.py` 在 iso 的失败取证（**生产逐条同红=既有红**：confidence 32>23、model_extensions 27>10）；本卡文件同算法单测 `OWN_FILE_RATCHET_OK`（max 18==frozen 18，三树同值，见 commands Q2b）
- `rgm/coverage_subset_fixed.txt` —— per-module 覆盖门子集实测 `scripts/revenue_forecast.py` **73% ≥ 60**、**新增语句 0 miss**（缺行全为 `main()` 既有行）
- `production_zero_write_before.txt` / `production_zero_write_after.txt` —— `scripts` 树 `d29e761d…`、`tests` 树 `a0d7667c…` 开工/收尾相同；新测试不在生产树
- `MANIFEST.sha256` —— 全量哈希清单（57 项；八件套总账在 attempt 根 `DELIVERABLES.sha256`）
