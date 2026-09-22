# Independent Reviewer Report — I-09-C / a20260922-01

- card: I-09-C（fault-injection / concurrency / crash-recovery acceptance），父项 I-09
- attempt: `a20260922-01`
- reviewer: independent reviewer（sampled verification；工具仅 read / grep / pwsh；未 kill、未重跑任何测试、生产树只读、只写本报告两件文件）
- date: 2026-09-22
- 方法：按 handoff.next_action 自列步骤 + 委派方 must-checks 抽样复核（1 例 oracle 端到端重算、1 条 kill 臂证据链逐环节、2 项保留偏差裁定、2 项 supersession 验证、边界抽查）。

## VERDICT: **accepted_scoped**

接受范围（scope 必须随此判决一并携带，缺一不成立）：

1. 一切被测内容 = **I-09-B ISOLATED 树**（iso/rf，6/6 hash 与 I-09-B handoff 一致，见 `after/production_and_iso_hashes_after.txt`）；**生产 promotion 未做**（context CF-I08C-1），本卡不构成任何生产等价声明。
2. **F12 保留失败（F-1/F12）仍为 OPEN**：frozen {0,2} 数值域未改、未 retry-to-green、case 保持 red（verdict all_ok=false）；归属 I-09-B 产品修复轨 与 owner/I-09-A oracle-erratum 轨，二者本卡均未执行。
3. **F5 签名缺口（F-2/F5）仍为 OPEN**：signed UNCOVERED GAP（is_a_passing_fault_test=false），产品范围归 I-09-B；P-C3 单跑不构成“并发安全”。
4. **F-6 并发单跑限制**：P-C3 仅单次无强制 lock-step 重叠运行，重复/高压重叠压力测试仍开放。
5. 生产侧 **I-16 / I-17 按本卡关闭标准另行 pending**；`disclosure_adaptation=unmapped`、`accuracy=unproven` 不变。
6. 机制域限定（REM-79 句式）：本卡的“生产零改动”结论成立于 **`git status --porcelain -- scripts/` 为空 + 6 个生产锚点 hash 等于 preflight 实测值（HEAD 6f74b056…）+ hooks 仅存在于本 attempt harness/ 且 `--fault none` 时不安装** 这一域内；不是无域全称断言。

---

## Numbered findings

### F-1 (PASS) A — PC2-K8 oracle 端到端重算，与 verdict 一致
从原始字节独立重算 `evidence/cases/PC2-K8_commit_after_response_lost/`：
- `fault.json`：kind=kill、barrier_reached=true（point=commit:after, pid=11200）、registered_in_manifest=true、kill={ok:true, pid:11200, exit_code_set:4242}、**raw_returncode=4242**、normal_exit_record_present=false、target_process_still_alive=false。盘上 `barrier_11200.json` 存在、`pid_11200.json` 存在、**`writer_exited_11200.json` 缺席**（仅有 12284/17512/48820 三条正常退出记录 = seed + recovery1 + recovery2）。
- `reader_after_fault.json`（新 reader 进程 pid 48536）：chain rows=2 ok、p1 **committed_rows=1 / logical_commits=1 / consumable=true**、**distinct publication_id = c84a8ec8…**（≠ p0 的 ed9af7b6…）、member hash 全等、product commit_status 一致、**audit_problems=[]（audit=0）**、hook_trace 以 `commit:after` 收尾（与 kill 点吻合）。
- `recovery1.json` / `recovery2.json`：两个**新** writer 进程，raw_returncode=0，normal_exit_record_present=true。
- `reader_after_recovery2.json`（新 reader pid 50120）：rows=4、chain ok、p1 committed_rows=3 但 **logical_commits=1、distinct id 仍 = c84a8ec8…**、attempt_seqs=[1,2,2]（= F-3 观察项，不影响冻结预期）、**audit_problems=[]**、p0 两 member hash 与 seed 逐字节相同。
- `verdict.json`：26 checks 全 ok、all_ok=true —— **与我的重算逐项吻合**（含 expected/actual 分列：raw 4242 vs expected "kill"）。
结论：PC2-K8 的 all_ok=true 是从这些字节可复算的，非自报。

### F-2 (PASS) B — PC1-K6 kill 臂证据链逐环节验证
- `state/barrier_27488.json` 存在（point=commit:before）。
- `state/pid_27488.json` 存在且内容 = new_run manifest 登记（pid=27488=实际运行 writer 的 `os.getpid()`，parent_pid=22488=venv launcher）；**被 kill 的 27488 是 manifest 登记 PID，不是 launcher PID**（launcher 22488 单独记录为 launcher_pid）。
- `fault.json`：**raw_returncode=4242**、kill.ok=true、registered_in_manifest=true。
- **`writer_exited_27488.json` 确认缺席**（state 内仅有 22772/39920/9296 三条退出记录，均属未被 kill 的进程）——finally 未运行的直接证据成立。
- `reader_after_fault.json`（**新** reader 进程 42980）：**P0 consumable=true**、chain rows=1 ok；**P1 committed_rows=0、logical_commits=0、consumable=false**；hook_trace 止于 `commit:before`（与 kill 点一致）；audit_problems=[]。
- verdict 28 checks 全 ok（`fault_matrix_summary.json` 与 `results_summary.json` 一致：raw=4242 / expected="kill" 分列）。
结论：该 kill 臂五个环节全部由文件本身证实。

### F-3 (PASS + 2 项裁定) C1 — F12/F1 归属链与处置裁定
读 `harness/probe_f12.py` + `evidence/cases/F12_stdout_pipe/{fault.json,pipe_controls.json,verdict.json}`：
- 臂本体：`fault.json` raw=**120**，stderr = `Exception ignored on flushing sys.stdout: OSError: [Errno 22] Invalid argument`；冻结期望 "0 or 2" 记录在旁未改。
- 控制链：**A(pipe with reader)=0 / B(pipe, no reader)=120 / C(stdout→file)=0**，同一 harness、同一 CLI、同一输入、同一隔离 registry，唯一变量是 stdout 去向；harness 仅保留 4242（kill），`harness_maps_child_rc=false`，只读 `Popen.returncode`。
- **裁定 (i) 归属是否可靠？—— 是。** A/B/C 单变量对照 + harness 不改写子进程 rc + B 的 stderr 机制证据（CPython finalization stdio flush），足以把 rc=120 归到产品 CLI 自身的退出码。**一处小瑕疵（不改裁定）**：`probe_f12.py` 第 65 行把 B 阶段的 `err` 变量误记为 C 的 stderr 字段（C 分支未单独取 stderr），故 `pipe_controls.json` 里 C 的 stderr 文案实为 B 的陈旧值；**A/B/C 三个 returncode 均各自分支正确采集，归属结论不受影响**。
- **裁定 (ii) 处置是否正确？—— 是。** “保留为 TRUE 失败 + 不重跑到绿 + 不改 frozen 期望”是唯一诚实处置：改数值域 = 改冻结 oracle（须 owner），重跑到绿 = 掩盖偏差。case 保持 all_ok=false，且 substantively F12 的“无保证/不可达保证”恰恰被这次不可预测性证实。
- **裁定 (iii) 归属：双轨，均不在本卡。** ① 若冻结数值域 {0,2} 必须成立 → **owner / I-09-A oracle-erratum**（数值域勘误）；② 若要消除偏差本身 → **I-09-B 产品修复**（规范化 broken-pipe 退出码）。本卡两项皆未做，正确。
- **F12 retained 是否阻塞本卡验收？—— 不阻塞。** F12 已按“carried product finding”正确定位：产品缺陷在 I-09-B 轨、oracle 数值域在 owner 轨，二者均超出 I-09-C（故障注入验收卡）的修改权限；本卡的义务是如实记录——已履行。故 accepted_scoped 必须携带 F12 OPEN（见 scope §2）。

### F-4 (PASS + 1 项裁定) C2 — F5/F2 锁缺口裁定
- `evidence/cases/F5_lock_not_implemented/verdict.json`：constructed=false、reason 明确（实现内不存在跨进程 commit lock，构造锁获取失败 = 自行补选，被禁）、code_scan lock_keywords_found=[]、**is_a_passing_fault_test=false、not_a_pass=true、checks=[]（0 checks）**。
- 我独立 grep 被测树 `iso/rf/scripts/publication_registry.py`：无 Lock/flock/msvcrt/filelock/acquire 任何锁原语（唯一 "lock" 命中是英文单词 "blocks" 的子串注释）；生产 `scripts/publication_registry.py` 同样零锁原语。
- P-C3 `verdict.json` 现场证据：`lock_evidence.lock_tokens_in_publication_registry_py=[]`，frozen F5 E 栏 = n/a(锁未实现)。
- **裁定：signed-gap-as-nonpass 正确，且不构成本卡的 blocking。** 实现里没有锁 → 该冻结故障点客观不可构造；签名（signing record，all_ok=true 仅表示“签名动作完成”）+ is_a_passing_fault_test=false + 明示 not_a_pass，既不虚报通过也不冒充阻塞。产品是否该有锁 = I-09-B（或 owner 卡）的设计决定。**F5 保持 OPEN（scope §3）**。

### F-5 (PASS) D — 两项 supersession 披露均在盘且如实
- `evidence/k_arms_first_attempt_supersession.md`：完整时间线（第 1 轮 600s 超时终止 → 会话内观测 → `--force` rmtree 重跑覆盖）、**session 转录的首轮数值逐例保留**（K1 182.83s / K2 182.62s / K3 182.89s，唯一失败检查 fault_raw_returncode_is_harness_kill，raw 空，barrier_reached=false）、**原字节不可恢复的诚实声明**（不伪造内容）、**launcher-PID 根因**（Popen.pid=45816 ≠ os.getpid()=42452 → 找不到 barrier → 拒 kill）、**判据不变声明**（§5：通过标准与首轮相同，变的只是 harness 找对 PID）。四项齐备。
- `evidence/tpub/README.md` + 原始输出核验：run1 = **8 failed / 40 passed，exit=1**，8 个失败**全部** ModuleNotFoundError `_cffi_backend`（我实测 run1 文件内 `_cffi_backend` 命中 = 8，FAILED 行 = 8，全部在 tests/test_attestation.py 的 Ed25519 import）→ **确属本卡 venv 环境缺陷而非产品/测试失败**；run1 原文**保留未被覆盖**；run2 = **48 passed，exit=0**；**delta 解释成立**：run1 总数 8+40=48 = run2 的 48，同一 48 测试，修复 = 从兄弟 attempt venv 拷回缺失的 `_cffi_backend.cp313-win_amd64.pyd`，argv/env 相同；失败测试身份由 test_attestation.py sha256=17934e28…（= I-09-B 副本）+ 行号 466/355 对齐证明。另 `tpub_i09b.txt` = **11 passed**（新绑定点）。

### F-6 (PASS) E — 边界抽查
- **stop-condition log（4 条，全部未触发，均有证据）**：① 未登记 PID 不得 kill —— 抽验 K6/K8 两臂均 barrier+manifest 双前置，且第 1 轮无法核验时**拒绝 kill 并记为 harness 失败**（supersession §3）；② 不得低于所声称持久化保证 —— K6 kill 后新 reader 见 0 行、K8 kill 后新 reader 逐行重算链 ok，errno 臂 rc=2 无部分可见；③ 不得删历史行 —— F7 两轮 recovery 后 registry 字节不变（reader_after_fault/recovery1 均 1282 B，verdict 含 `registry_bytes_unchanged_no_history_deletion`）；④ 不得用“仅异常路径”冒充真退出 —— 抽验 2 臂 raw=4242 + writer_exited 缺席，7 条 OSError 臂明确标注 exception-path-only。
- **路径边界**：`harness/common.py` 明示 allowed_write_roots=attempt；`child_env()` 仅按例覆写 `REVENUE_PUBLICATION_REGISTRY` 指向该例 state/registry；evidence 全树 grep `AppData|C:\Miniconda|site-packages\revenue` **零命中**；pytest basetemp 也落在 `evidence/tpub/` 内。未见任何指向真实 registry / 用户包 / 生产树的写入路径。
- **git（我本人只读实测）**：`git status --porcelain -- scripts/` = **空**，`git rev-parse HEAD` = `6f74b056631e0cb50a28b57bdcf979514dadb8f9`（= `after/production_and_iso_hashes_after.txt` 记录值）。
- **状态与签署**：`handoff.json` status=**review_pending**、implementer_self_acceptance=false、implementer_never_signs_acceptance=true、reviewer_status=pending —— **无自我签署**。
- **hook 位置文档**：`evidence/hook_positions.md` 存在；6 个 wrap target（H1–H6）与 fault 点命名、hook_trace 序列（抽验 K6 止于 commit:before、K8 止于 commit:after）自洽；产品零编辑由 after-hashes（生产 6 锚点 = preflight 值）+ iso 6/6 = I-09-B + `changes.diff` 头部零产品 diff 三重印证。

### F-7 (MINOR, non-blocking) probe_f12.py 控制 C 的 stderr 字段错标
第 65 行 `(err or b"")` 复用了 B 阶段变量，C 分支的 stderr 未被采集 → `pipe_controls.json.C_stdout_to_file.stderr` 实为 B 的陈旧文案。**不影响** A/B/C returncode 归属（三分支 rc 各自正确），但该字段不应被当作 C 的观测值引用。建议随 F12 产品/erratum 轨一并修正 probe（harness 级，非本卡义务）。

---

## Unverified list（抽样之外，如实列出）

1. 其余 22 个 fault case 未逐例重算（已抽：PC2-K8 全量重算、PC1-K6 全链、F12、F5、F7 关键检查；其余以 `results_summary.json`/`fault_matrix_summary.json` 交叉一致 + 24/26 计数自洽为据）。
2. P-C5（27 checks）与 P-C3（12 checks）未逐条审计；仅抽验 lock_evidence、4 行链尾、consumer bad_samples=[]。
3. `commands.json` 中 inv1/inv2/inv4 harness-defect 轮与 TIMEOUT@600s 轮的细节未逐条审计（supersession 披露已覆盖 K 系列同类问题）。
4. “13 次真实进程终止”总数未独立数全（results_summary 中 rc=4242 者 11 例 + PC4a = 12 个可定位 kill 事件；第 13 个未定位，疑为 PC4a 内第二次 kill/计数口径差异）—— 不影响抽验结论。
5. k_arms 首轮原始字节按定义不可恢复 —— 接受其 session 转录披露为唯一留痕（这正是该披露的声明内容）。
6. `evidence/eol_reconstruction.txt` 的原始重算输出未由我复跑重导（preflight §4/§6 STOP→裁决 B 的四元组轨迹已读；EOL 判定属 parent 既有裁决，本卡只复核留痕未被删改——已确认 §4.1 STOP 行与判据原文原样保留、§6 仅追加）。
7. tpub run2 “同 argv/env” 声明未做逐参数 diff（只核了两轮输出与 README）。

## 复核工具与边界声明

- 仅用 read / grep / pwsh；未使用不存在的工具；未 kill 任何进程、未重跑任何测试/矩阵；生产树仅做了一次只读 `git status`/`rev-parse`。
- 本 reviewer 写入仅两件：`reviewer_report.md` 与其 `reviewer_report.sha256`；未签署任何 accepted 于 handoff/decision 等实现者文件；判决以本报告 + 向 parent 的回传为准。