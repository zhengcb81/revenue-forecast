# DECISION — RF-STEP9-TRIAGE（终稿；活文档历史已随每文件收口增量落至本版）

- card: RF-STEP9-TRIAGE · attempt: a20260923-01 · oracle: `oracle.md`（实现前冻结；人类确认不可用 → 见 handoff.unresolved_question）
- **归因 12/12 完成**（五协议腿齐）；small-safe 修 7 文件已 iso 红→绿入 `changes.diff`；RF 生产树零写入（close 核验见 §6）。
- 防灾令遵行: 每文件跑完即填表、evidence 即写即落；本文=增量合并后的终稿。

## 0. 环境钉（详 binding.md）

| env | rf sha | wiki sha | 备注 |
|---|---|---|---|
| RF 生产树（只读） | 开卡 `977fa1e8` → close 时并发推进至 `b7a6a116`(batch-9) | n/a | 脏项=基线原样+并发卡产物（§6）；本卡 10 文件（8 测试+2 工具）`b0d016a6..b7a6a116` **零变更**，`git apply --check` rc=0 @close 树 |
| WSL 复现克隆 `~/rf-ci-repro` | `b0d016a6` | 主臂 `5d72529` · 对照臂 `31c0afcb`（跑后恢复） | 目录名 **rf-ci-repro ≠ revenue-forecast** = 家族 C 病灶 |
| WSL 布局沙盒 `/tmp/s9lay`·`/tmp/s9iso`·`/tmp/s9isomis` | 逐跑钉（46bd8b16 / 8b7229c3 / 70dd9f6e / 95df2661 / ec307d20 / b0d016a6） | 每跑 before/after 核 `5d72529` | 规范名 + 兄弟符号链接；/tmp 跨 WSL 重启会清（见 commands 事件项） |
| Windows 本地臂 `%TEMP%\s9win\revenue-forecast` | `b0d016a6` | `5d72529`（win2 臂；经本地 fetch 修复） | filing `89c8bdb2cfba4d88720d005d0558f422957e8ade`；python 3.13.9 |

`b0d016a6..977fa1e8` 仅 3 个 audit(planning) 提交，tests/tools/scripts 面只动 `test_cross_repo_chain_e2e.py`+`host_assumption_allowlist.json`（不在本卡 8 文件）→ 归因两 sha 等效。
env 补 facts: `evidence/env_facts.txt`（filing=89c8bdb2…, wiki_at_start 记录两次状态见 §7 事件项）。

## 1. 12 行归因总表（终值）

| # | 失败节点 | 复现 raw（WSL 主臂@b0d016a6/wiki@5d72529） | 首红 / 引入提交 | 先在于 46bd8b16? | 宿主相关(Win)? | 根因类 | 家族 | 范围级 | 修案 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | receipt_attacks::test_context_fabrication_is_rejected_by_final_validation | `wsl_head_tests_adversarial_...` 1F/2P；E27@revenue_publication.py:396，爆点=建单 L47 | 成对 `wsl_preEc3_95df2661` 绿 → `wsl_atEc3` 红；`-S attestation_missing_record`=ec307d20 | 否（`wsl_anchor46` 绿） | 否——`win2_head` RC=1 同 E27 签名 | (ii) 测试期望 vs owner 授权产品变更（B1/REM-01 E27：host_signed 无记录禁建单） | A: B1 晋升(ec307d20) 余波 | **small-safe-fix NOW ✓已做** | iso H1: 建单 `unattested`；红→绿 `iso_ok_receipt_attacks` RC=0 |
| 2 | attestation::test_configured_provider_means_host_signed_publication | `wsl_head_tests_test_attestation` 1F/6P；`attestation_capability()`=False | 成对 95df2661 绿 → ec307d20 红；`-S provider_absent`=ec307d20 | 否 | 否——win2 RC=1 同 `False is not true` | (ii) 同上，**且 B1 显式预断红**: B1 decision.md §5 = I-08-A §7.1 点名必须断的 false-green，改写权归 **I-08-B** | A | **family-card-needed（本卡不动）✓** | 落 I-08-B `a20260919-01` 14 文件（其 handoff.next_action: "from a card authorised to write it"） |
| 3-5 | fc1102×3（healthy_lake / report_isolated / trend_delta） | `wsl_head_tests_test_fc1102` 3F/1P；签名 `manifest triplet commits missing: ['revenue']` | **环境判非 sha 判**: 同 sha b0d016a6 规范名 `wsl_layhead_fc*` **绿**；错名 46bd8b16 `wsl_misname46*` **红** | 等效"是"——错名布局下锚点即红（`wsl_misname46_*` RC=1@46bd8b16）→ 与 sha 无关的复现环境病 | 否——目录名相关: Windows 规范名 `win2_head` **RC=0** | (iv) 环境/复现布局: 克隆名 `rf-ci-repro`≠`revenue-forecast` → `_manifest()`/runner `parent/"revenue-forecast"` 找不到自仓 → 空 sha → missing | C: 复现布局（×5） | **small-safe-fix NOW ✓已做** + 备选零代码=复现克隆改名 | iso H5a/H5c: revenue 改 `PROJECT_ROOT`（规范名下逐字等价）；错名红→绿 `iso_misfix_fc1102` RC=0 + 规范回归 `iso_ok_fc1102` RC=0 |
| 6-7 | fc1302×2（recurring_unchanged / interrupted_delta） | `wsl_head_tests_test_fc1302` 2F/1P；同签名 + `manifest_missing:["revenue"]` | 同 #3-5（同一 runner 检查） | 同上（misname46 同 raw 对） | 同上——Windows 规范名 `win2_head` **RC=0** | (iv) 同上 | C | 同 #3-5 ✓已做 | iso H5b/H5c；`iso_misfix_fc1302` RC=0 + `iso_ok_fc1302` RC=0 |
| 8 | single_owner::test_only_canonical_client_may_use_subprocess_download_adapters | `wsl_head_tests_test_single_owner` 1F/2P；`revenue_core.py imports subprocess (second download owner)` | 成对 95df2661 绿 → ec307d20 红；`-S 'import subprocess' -- revenue_core.py`=仅 ec307d20（provider spawn L223/230） | 否 | 否——AST 平台无关，win2 RC=1 同签名 | (i)/(ii) 冲突型: B1 授权产品（provider 必须 spawn）撞 R3 冻结守卫，守卫自注 "No new entries without review" | A（ec307d20 子机制: subprocess 守卫） | **owner 裁定(2)=守卫收窄 → 已执行 ✓**（OWNER_DECISIONS §22 / register §84, owner 2026-09-23；原 STOP 解除） | H6 收窄至声明语义（download adapters only；**零新白名单条目**、豁免仍精确={filing_fetch_client, source_preparation}、判据不删、justification 首行入 changes.diff 头）。读证 `guard_readproof.txt`：实现=仅此测试文件(G1)；subprocess 面=3 文件(2 豁免+revenue_core)；revenue_core 12/12 领域词 hits=0；canonical client=thin subprocess CLI(声明下载属主)。**红绿变异六证**：R1 基线红(`wsl_head`/`win2_head`) → G1 `g_g1` RC=0（收窄净树）→ 防旁路 `g_b1`(filing-CLI 下载) RC=1 NEW_MSG + `g_b2`(curl/xlsx 无下载词) RC=1 NEW_MSG → 变异 M1 回全宽 `g_m1` RC=1（revenue_core 再红=收窄承重非空转）+ M2 射程清零 `g_m2` RC=0（反例放行=旁路开口→反例承重）→ 终绿 `iso_ok_single_owner` RC=0；`PROMOTION_SURFACE_DIFF_EMPTY=YES`（B1 晋升面零字节）；**changes.diff 文件数 7→8**（H6=守卫面追加；`git apply --check` 加头后 bash 重导复验 rc=0，见 §6） |
| 9 | zr1102::test_c4_mutation_patrol_capabilities | `wsl_head_tests_test_zr1102` 1F/8P；栈 `mutation_patrol._resign → build_publication_receipt → E27` | 成对 95df2661 绿 → ec307d20 红（E27 首现） | 否 | 否——win2 RC=1 同 E27 签名 | (i) 产品工具缺陷: `_resign` 仍铸 host_signed 无记录，未随 E27 适配（金样本本即 unattested） | A（与 #1 同 E27 机制） | **small-safe-fix NOW ✓已做** | iso H2: `_resign`→`unattested`；绿 `iso_ok_zr1102` RC=0 + **patrol CLI `PATROL_RC=0`**（accepted==0 语义保真） |
| 10-11 | zr601::test_c1_negative_asset_drivers_rejected / ::test_c1_recovery_rate_out_of_range_rejected | `wsl_head_tests_test_zr601` 2F/8P；期望旧消息，实际 `driver X outside permitted bounds [0.0, inf\|1.0]` | 成对 `wsl_pre70dd_8b7229c3` 绿 → `wsl_at70dd` 红；blame calc.py:119-121=70dd9f6e；`-S 'cannot be negative'@calc` 消失=70dd9f6e | 否 | 否——win2 RC=1 同 regex 签名（纯产品消息） | (ii) 测试期望漂移: fcap→main 检出换 `model_registry.driver_value_bounds` 统一界检查，**拒绝语义保真**（-1.0/1.5 仍拒，仅文案变） | B: fcap 检出(70dd9f6e) ×3 | **small-safe-fix NOW ✓已做（条件达成）** | iso H3: match 双匹配（旧\|新，对检出可逆）；**全 10 用例绿 `iso_ok_zr601` RC=0**（无 DID NOT RAISE → 熔断未触发） |
| 12 | zr708::test_c2_accuracy_record_consumed_by_confidence | `wsl_head_tests_test_zr708` 1F/6P；栈 `confidence.py:151 → document.py:796 require(origin<available<=cutoff)` | 成对 8b7229c3 绿 → 70dd9f6e 红；`-S 'future information leak'@document.py`=70dd9f6e；**同提交** `-S 'Only usable after...'@test_backtest`=70dd9f6e | 否 | 否——win2 RC=1 同 future-leak 签名 | (ii) 夹具漏适配: 同提交给姊妹测试 `test_backtest.py:245` 打了 `data["as_of_date"]="2028-03-01"` 同款补丁，zr708 同链路漏打 | B（**卡片指定链接实锤**: 70dd9f6e 同时改 confidence.py=棘轮文件 与 document.py 新防泄漏检查，zr708 经 confidence.py:151 触发——与 RF-RATCHET-FIX 同源不同面） | **small-safe-fix NOW ✓已做** | iso H4: 同款一行；绿 `iso_ok_zr708` RC=0（全 7 用例） |

宿主列终值依据: `win2_head_*`（8 raw, wiki=5d72529, python 3.13.9, 规范名）——6 个 A/B 族文件与 WSL **同签名红**（宿主无关），fc×2 **RC=0**（目录名相关、非 OS 相关）。首次 `win_head_*` 中 fc×2 因本卡自建 wiki 检出中断（`missing:['wiki']`）判废，保留为过程记录，被 win2 取代。

## 2. 家族分组（假设 → 裁定）

- **家族 A — B1 晋升 `ec307d20` 余波（4 项: #1/2/8/9）**: 同一引入提交四子机制（E27 建单×2、capability 握手化、spawn 撞守卫）。→ 卡片原假设 receipt/attestation/single_owner/zr1102 为"单例"，**修正为同源家族**。
- **家族 B — fcap→main 检出 `70dd9f6e`（3 项: #10/11/12）**: 消息文案漂移 + 夹具漏适配。→ 卡片原假设 zr601×2、zr708 分立，**修正为同族**；**zr708↔confidence.py 链接按卡片要求实锤**（同提交双面，经 confidence.py:151 触发）。
- **家族 C — 复现布局（5 项: #3-7）**: 目录名病。→ 卡片原假设 fc1102/fc1302 各一族，**修正为同一环境家族**。
- 嫌疑清单裁定: `ec307d20`✓A 族 · `70dd9f6e`✓B 族 · `5fd82de7`/`5db4734a`=棘轮卡事项（非本 12 任一引入）· B1(ec307d20)✓。
- **先在判**: 锚点 46bd8b16 规范布局 8 文件全绿（`wsl_anchor46_*`）→ A/B 族 7 项无一先在于末绿；家族 C 错名锚点即红（`wsl_misname46_*`）→ 与 sha 无关。
- **(v) 兄弟互作 = 无**: 旧钉 31c0afcb 对照 8 文件全红同签名（`wsl_oldwiki_*`）→ wiki 钉非这 12 之因；家族 C 机制不含 wiki 值（missing=['revenue'] 自引用），cipin 对照判定**冗余弃跑**（/tmp 跨 WSL 重启清除致 cd 连败两次 + 机制正交，理由入档 commands §事件）。
- **(vi) 顺序/夹具态 = 无**: 12 项在文件级隔离跑逐项复现（raw 逐文件），无顺序依赖迹象。

## 3. 逐文件证据链（要点；全量 raw 在 evidence/）

- **#1** E27 消息 @`revenue_publication.py:396`，爆点建单 L47 非断言；测试本义=伪造 gate_ids 终验拒（L35-55），与标签无关 → H1 改 `unattested` 不移本义。
- **#2** B1 decision.md §5 原文 "rewriting it is I-08-B's item"，期望失败码 E32 `provider_capability_unproven`；B1 commands.json 预期 "EXACTLY ONE expected failure = 该测试"；I-08-B handoff.status=`accepted_scoped`, next_action=落 14 文件（授权卡）。**本卡改它=越权 → STOP。**
- **#3-7** 机制: 测试 `_manifest()`（fc1102 L116-133 / fc1302 L23-41）与 runner `daily_t2_runner.py:77-84` 把 revenue 解析为 `PROJECT_ROOT.parent/"revenue-forecast"`，而 heads 用 `_head(PROJECT_ROOT)`——**同函数两处解析不一致**即 bug 面；复现克隆名不符 → 空 sha。三点半绿: head 错名红 / anchor 规范绿 / anchor 错名红 / head 规范绿（WSL+Win 双平台）。**推论（披露为推论）**: CI 工作区名=repo 名+`ci_checkout_siblings` 三件套按构造齐 → 这 5 项真 CI 大概率不红；register §55"本仓固有14"中 5 项实为复现环境病（无网未实测 GH 日志 → handoff.unproven）。
- **#8** 守卫注释 L19-22 "No new entries without review" = 明文 review 门；spawn=attestation 非 download（revenue_core L223/230）→ 三选项交 owner。
- **#9** 金样本 unattested（test_attestation L63-68 佐证）；H2 后 patrol `accepted==0` 回归真实 gate/hash 拒绝（B1 前 host_signed 无记录在验单反而 trivially-reject 风险），CLI RC=0。
- **#10-11** 旧=require(value>=0)+ratio 上下限；新=界表统一检查；被测两例仍拒 → 类 (ii) 依据；iso 全 10 绿 → 5 字段无放行回归。
- **#12** 棘轮链接: 70dd9f6e 同改 confidence.py(+16 行 usable_origins, RF-RATCHET-FIX 同文件) 与 document.py 新检查；修案蓝本=同提交 test_backtest.py:245 逐字先例。

## 4. 范围级汇总

- **small-safe-fix NOW（已做，iso 红→绿，仅 changes.diff）**: #1, #9, #10-11（条件达成）, #12, #3-7（稳健化 + 零代码备选并列披露）, **#8（owner 裁定(2) 后追加执行：H6 守卫收窄，六证齐）**。
- **family-card-needed**: #2 → 落 I-08-B 14 文件（handoff 已写明授权路径；`I-08-B-14FILE/a20260923-01` 父方已派）。
- ~~owner-ruling-needed（STOP 带证据）~~: #8 → **owner 裁定 (2) 守卫收窄并已执行**（§1#8 行 = 六证）。
- 明确不做: 棘轮×2（RF-RATCHET-FIX）、盲改、RF 生产任何写入。

## 5. changes.diff（终）— **8 文件 9 hunk**（`grep -c '^@@'` 实测=9；`git diff --stat`=56+/23-；文件数 **7→8**；`#` 逐文件 justification 头随文件交付，加头后 `git apply --check` rc=0）

（`evidence/iso_fix_plan.md` H1-H5 执行单 + H6 守卫收窄；补丁器 `%TEMP%\ci_step9_iso_patch.py` 逐串 count 断言 10 项全过）:
1. `tests/adversarial/test_receipt_attacks.py` — host_signed→unattested（H1/#1）
2. `tools/mutation_patrol.py` — _resign host_signed→unattested（H2/#9）
3. `tests/test_zr601_asset_facts.py` — 2× match 双匹配（H3/#10-11）
4. `tests/test_zr708_backtest_reverify.py` — +as_of 2028-03-01（H4/#12）
5. `tests/test_fc1102_t2_runner.py` — revenue→PROJECT_ROOT（H5a/#3-5）
6. `tests/test_fc1302_scan_health.py` — 同上（H5b/#6-7）
7. `tools/daily_t2_runner.py` — missing 检查 revenue→PROJECT_ROOT（H5c，规范名下逐字等价）
8. `tests/test_single_owner_guard.py` — **H6a+H6b owner 裁定(2) 守卫收窄**（DOWNLOAD_DOMAIN 12 词 + 射程=subprocess∧域；零新条目、零豁免变更、判据不删）

绿证据（8 文件 diff 终版重跑）: `iso_ok_receipt_attacks/single_owner/zr1102/zr601/zr708` RC=0 · `iso_attestation_untouched` RC=1（#2 依设计保持红=I-08-B 所有）· `iso_misfix_fc{1102,1302}` RC=0 · `iso_ok_fc{1102,1302}` RC=0 · `iso_patrol_cli.txt` PATROL_RC=0 · `iso_env.txt` wiki 前后=5d72529 · **#8 六证** `g_g1`(0)/`g_b1`(1)/`g_b2`(1)/`g_m1`(1)/`g_m2`(0)+R1(1) · `PROMOTION_SURFACE_DIFF_EMPTY=YES`。
未做（披露）: ruff/mypy 未跑（无环境；py_compile 8 文件过）；全量 step9 选集未复跑（8 目标文件+guard+patrol 已验）。

## 6. 关闭核验（终值）

- **RF 产品/测试/工具零改动** ✓：`porcelain_close.txt` 中无任何 `scripts/ tests/ tools/ compatibility/ .github/` 路径条目（`NO_PRODUCT_PATH_CHANGES=YES` 判定入 `evidence/porcelain_delta.txt`）。
- 与基线的方向性差异（`porcelain_delta.txt`，共享工作区含并发卡）: ①本卡 attempt 文件（基线已含 `?? RF-STEP9-TRIAGE/` 目录级条目，close 展开为文件级）②并发兄弟/父方卡产物（` M OWNER_DECISIONS.md`、` M RESPONSES.md`、`?? AUDIT-*/RF-RATCHET-*/I-10-A/CW-GATE-UNBLOCK-2/PUSH-LOGS-ARCHIVE/...` 等）——**非本卡所写**：本卡命令面 = RF 只读 + attempt 目录写 + /tmp、%TEMP% 写（commands.md 全清单）。基线中 ` M REMEDIATION_REGISTER.md` 的状态变化由并发方处置（登记册推进），非本卡动作。
- `git apply --check changes.diff` @生产 HEAD = **rc 0** ✓（只读）。
- WSL wiki == `5d72529` ✓（close 复核 + iso_env）；`~/rf-ci-repro` == `b0d016a6` 未动 ✓；Windows 臂 wiki=5d72529（%TEMP% 私有克隆，不涉生产）。

## 7. 过程事件（自洽披露）

1. `cipin.sh` 首跑把 `~/company-wiki` 翻到 31c0afcb 后因 `/tmp/s9lay` 已被 WSL 重启清空而在 cd 处断（`%TEMP%\cipin.log`），**未及恢复**；`mis46cipin_env.sh` 的守卫（wiki≠5d72529 即拒跑并记 `env_facts.txt`）防了二次翻动；iso_run 步 0 恢复至 5d72529 并断言（`iso_env.txt`）。
2. Windows 首跑（`win_head_*`）wiki 检出中断（`wcheckout_rc=128`, wco.err `unable to read tree`）→ fc×2 判废；本地 `fetch` 修复后 win2 全 8 重跑取代。
3. WSL HCS 超时/实例重启多次 → /tmp 沙盒需每次重建（脚本已幂等化）；重复的 mis46cipin 调用为无害重跑（同结果覆盖写；其间一次瞬态 RC=4 后被两次 RC=1 覆盖）。
4. **#8 首轮五跑无效**: H6 补丁编辑被「先读后改」策略拒 → 补丁器缺 H6 → 五跑=基线等价红（`%TEMP%\guard_run.log`）；按策略读文件重打 H6 后第 2/3 轮六证全部有效（`guard_run2.log`/`guard_run3.log`）。
5. **changes.diff 头部追加事故（PS5.1）**: 用 PowerShell ANSI(GBK) 读写含 CJK 的 diff → 非法尾字节吞换行 + mojibake → `git apply` corrupt-at-93；处置=弃 PS、**bash 字节安全重导**（`ci_step9_changes_finalize.sh`：守卫脚本重跑重生 pristine body → `cat` header+body → `git apply --check` rc=0 → CJK 完好探针=1）；hunk 计数按实测 9 修正（`ci_step9_hunkfix.sh` 复验 rc=0）。
