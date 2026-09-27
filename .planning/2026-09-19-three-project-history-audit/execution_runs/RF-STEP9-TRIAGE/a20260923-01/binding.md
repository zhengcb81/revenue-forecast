# BINDING — RF-STEP9-TRIAGE / a20260923-01

## 钉

| 项 | 值 |
|---|---|
| RF 生产树 | `C:\Users\郑曾波\Projects\revenue-forecast` 开卡 `977fa1e8…` → close `b7a6a116…`(batch-9, 并发父方推进)（READ-ONLY；只写本 attempt 目录；本卡 10 文件两 sha 间零变更；`git apply --check` rc=0 @close） |
| RF porcelain 基线 | `evidence/porcelain-baseline.txt`（M REMEDIATION_REGISTER.md；?? I-07-D/；?? RF-STEP9-TRIAGE/；?? .tmp-r41-mutation/；?? assurance/.../plan_inputs.json.bak；3 个权限拒绝目录告警原样） |
| WSL 复现克隆 | `~/rf-ci-repro` @ `b0d016a645f52ce914197629b3ca5995609d9e89`（=RF 分支批次 5c；目录名 **rf-ci-repro**，本卡家族 C 病灶） |
| WSL wiki | `~/company-wiki`：主臂/锚点/引入对/沙盒 = `5d725294304a1edb1731bd5de3720fe3608b00f4`（每跑 raw 头记 before/after）；对照臂 = `31c0afcb963ae7539173454022af6c34521bc363`（跑后恢复 5d72529，raw 尾记 wiki_restored） |
| WSL filing | `~/filing-fetch` = `89c8bdb2cfba4d88720d005d0558f422957e8ade`（`evidence/env_facts.txt` 实测；fc 三元组自引用不依赖其值） |
| WSL python | Python 3.12.3，venv-less --user 依赖 |
| 布局沙盒（WSL） | `/tmp/s9lay/revenue-forecast`（规范名）+ `/tmp/s9lay/{filing-fetch,company-wiki}` 符号链接 → 家中兄弟；rf sha 逐跑：46bd8b16 / 8b7229c3(=70dd9f6e^) / 70dd9f6e / 95df2661(=ec307d20^) / ec307d20 / b0d016a6；wiki 每跑 before/after 核 `5d72529` |
| 错名对照（WSL） | `/tmp/s9mis/rfclone` @46bd8b16（**非规范名**）→ `wsl_misname46_*` 双文件 RC=1（wiki=5d72529 记于 raw 头） |
| Windows 本地臂 | `%TEMP%\s9win\revenue-forecast`（规范名）@ `b0d016a6`；filing = `89c8bdb2cfba4d88720d005d0558f422957e8ade`；wiki 首跑检出中断（`wcheckout_rc=128`，`win_head_*` fc×2 判废保留为过程记录）→ 本地 `fetch` 修复后 **win2 臂 wiki=`5d725294304a1edb1731bd5de3720fe3608b00f4`**，全 8 重跑 = `win2_head_*`（fc×2 RC=0，余 6 同签名 RC=1） |
| Windows python | Python 3.13.9 + pytest 9.1.1 + cryptography 50.0.1 + pyyaml（RF 生产解释器） |
| CI 参照 | `.github/workflows/quality.yml` ubuntu `verify` job step9 = `python -m pytest tests tools/tests -q --ignore×22`（与 `%TEMP%\ci_repro_step9c.sh` 逐字同选集）；CI 布局 = `/home/runner/work/revenue-forecast/revenue-forecast` + `ci_checkout_siblings` |

## b0d016a6..977fa1e8 等效性
仅 3 audit(planning) 提交；tests/tools 面 diff = `tests/test_cross_repo_chain_e2e.py` + `tests/contract/host_assumption_allowlist.json`（不在本卡 8 文件）→ 归因在生产 HEAD 同效。

## git 锚（evidence/git_anchors.txt 全量）
- 末绿锚 #287: `46bd8b16f295e41d3e6228fd0f38b8f175656e8a`（2026-09-20T08:42:41+01:00）
- 嫌疑: `5db4734a`（08:51, model registry 入 VCS）、`70dd9f6e`（15:04, fcap→main 检出）、`ec307d20`（9-22 20:44, PROMOTION-EXEC B1-B2）、`5fd82de7`（MODEL 晋升）、`95df2661`（=ec307d20^）、`8b7229c3`（=70dd9f6e^）
- 引入对（沙盒成对红绿）: 95df2661 绿→ec307d20 红（#1/2/8/9）；8b7229c3 绿→70dd9f6e 红（#10/11/12）
- `-S` 首现: `attestation_missing_record`=ec307d20 · `provider_absent`=ec307d20 · `import subprocess`@revenue_core=ec307d20 · `outside permitted bounds`@calc=70dd9f6e · `cannot be negative`@calc 消失=70dd9f6e · `future information leak`@document=70dd9f6e(+a026fa7f 早期) · `Only usable after these actuals`@test_backtest=70dd9f6e

## per-file raw sha（evidence/ 内每 raw 头含 rf_sha+wiki_sha+cmd+date_utc）
- WSL 主臂 8: `wsl_head_tests_*`（rf=b0d016a6, wiki=5d72529）
- 锚点 8: `wsl_anchor46_*`（rf=46bd8b16, wiki=5d72529, 规范布局 → 全绿）
- 布局翻绿 2: `wsl_layhead_fc_*`（rf=b0d016a6, 规范布局 → 绿）
- 引入对 12: `wsl_pre70dd_8b7229c3_*`(2绿) `wsl_at70dd_*`(2红) `wsl_preEc3_95df2661_*`(4绿) `wsl_atEc3_*`(4红)
- 旧钉对照 8: `wsl_oldwiki_*`（rf=b0d016a6, wiki=31c0afcb → 全红同签名）
- Windows 8: `win_head_*`（rf=b0d016a6；6 个非 wiki 文件有效，fc×5 待规范重跑）
- 错名锚点 2: `wsl_misname46_*`（rf=46bd8b16, wiki=5d72529, 错名 → 双红）
- iso 绿 8 + patrol: `iso_ok_*`(6) · `iso_misfix_*`(2) · `iso_patrol_cli.txt`(PATROL_RC=0) · `iso_env.txt`(wiki 前后=5d72529)
- 过程/对照: `win_head_*`(8, fc×2 判废保留) · `env_facts.txt` · `porcelain_close.txt` · `porcelain_delta.txt` · `iso_fix_plan.md`
- **弃跑入档**: `cipin`（CI 钉×规范名×head）——/tmp 跨 WSL 重启清除致 cd 连败 + 机制与 wiki 正交（missing=['revenue'] 不含 wiki 值，oldwiki 臂已覆盖钉维度），冗余非缺口（decision §2）

## 布局/命令脚本（%TEMP%, 可复跑）
`ci_repro_step9_files_head.sh` · `ci_repro_step9_sandbox.sh` · `ci_repro_step9_oldwiki.sh` · `ci_repro_step9_misname46.sh` · `ci_repro_step9_cipin.sh` · `%TEMP%\ci_repro_step9.sh` / `ci_repro_step9c.sh`（父方既有，step9 选集源）

## 披露
- git worktree/clone 均在 WSL home、/tmp、%TEMP%；RF 生产零 git 变更、零文件写入（基线核验见 close）。
- 无网络。家族 C "真 CI 不红" 为**推论**（布局机制 + 沙盒绿），未实测 GitHub 日志（无网）。
- 家族 C 修案若落地，复现环境错名即不再致红；错名对照 raw 留档证明修前状态。
