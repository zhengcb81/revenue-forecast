# REVIEWER REPORT — RF-STEP9-TRIAGE / a20260923-01

- card: RF-STEP9-TRIAGE（12/12 失败归因 + 7 文件 small-safe 修）· attempt: a20260923-01 · reviewer: 独立复审子代理（父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`）· date: 2026-09-23
- review 域声明：本报告全部判词的观察域 = 本复审会话（2026-09-23，RF 生产树只读、RF HEAD=`b7a6a116`、WSL `~/rf-ci-repro`=`b0d016a6`、wiki=`5d72529`、%TEMP% 克隆=`s9revclone`、无网络、无状态变更 git）。超出该域的事实均标 UNVERIFIED。
- 方法：read / grep / pwsh（含只读 git log/show/diff/status、%TEMP% 克隆实跑、`wsl -d Ubuntu` 只读复核）；零产品写入；本 attempt 内只写本报告 + `.sha256` 两个文件。

## 0. VERDICT

**ACCEPT（签署复审通过；卡面 review_pending → 复审接受，落定由父方执行）**，附 5 条 minor findings（全为文书/计数级，无一动摇归因、修案或边界结论）。§55 计数修正裁定 = **CORRECT（附 unproven 注记）**，见 §5。范围-if-接受见 §7。

## 1. 交付物核验（九步全在、冻结先行）

| 交付物 | 结论 | 复审实证 |
|---|---|---|
| oracle.md 冻结先行 | ✓（实现前冻结口径自卡文自冻；人类确认不可用已如实披露，父方 §81 追认） | mtime 域=本盘：oracle 19:37:41 早于首个判据 raw `wsl_head_*receipt` 19:40:55；内容含五腿协议、三档范围级、RF 只读+changes.diff-only 规则 |
| binding.md | ✓ 全钉（RF 两 sha、wiki 主/对照臂、filing、锚、逐 raw sha、CI 参照） | 与 raw 头逐项比对一致；`b0d016a6..977fa1e8` 等效性声明我未逐 commit 复核，但已独立证明 `b0d016a6..HEAD(b7a6a116)` 对本卡 10 文件 diff = **空**（见 §6） |
| commands.md | ✓ 十步+事件披露；无网络动词 | grep 命中仅 2 处：`git fetch C:\...\company-wiki`（本地路径 fetch，非网络）与 recovery 的回滚指令（文档性，未执行） |
| decision.md | ✓ 12 行终表 + 家族三分裁定 + §55 修正提案均在 | 逐行抽验见 §2-§5；hunk 计数文书误差见 F-1 |
| changes.diff | ✓ 7 文件；`apply --check` **rc=0** 我亲跑（%TEMP% 克隆 `s9revclone`@`b7a6a116`），随后真 `git apply` rc=0 + `py_compile` 7 文件 rc=0；5423 B 与卡面一致 | 实际 hunk 数 = **7**（非卡面所称 8，见 F-1） |
| handoff.md | ✓ review_pending/unsigned 如实（oracle 追认未决 → 父已 §81 追认，本报告确认关闭） | unmapped 4 出口 + unproven 5 条齐 |
| recovery.md | ✓ 可执行重跑路径 + 翻动恢复如实（cipin 留置 wiki@31c0afcb → iso 步0 恢复） | `iso_env.txt` wiki_before=wiki_after=`5d72529` ✓ |
| evidence/ | ✓ 实数 **72** 文件；handoff 枚举 71（漏计 porcelain-baseline，见 F-3） | 复审实读 >20 件（见下），四点矩阵 8 raw + iso 绿 8 raw + 成对 12 raw + win2 8 raw 中的抽验全数通过 |
| 父方 oracle 追认 | ✓ 已由父写入 oracle.md 尾部（+5 行，` M` 来源，见 F-5/§6） | register §81 同文 |

## 2. 归因抽验（3 行独立复核）

### (a) #1 receipt_attacks → `ec307d20` 引入 · H1 语义保真 — **CONFIRMED**
- 引入提交：`git log -S 'attestation_missing_record' -- scripts/` = **仅 `ec307d20`**（B1-B2 晋升提交，2026-09-22T20:44:25+01:00）✓；`provider_absent` 同 ✓。
- 成对 raw（域=WSL `/tmp/s9lay/revenue-forecast` 规范名、wiki 每跑前后=`5d72529`）：`wsl_preEc3_95df2661…receipt` = **3 passed RC=0** → `wsl_atEc3…receipt` = **1F RC=1**，爆点 `revenue_publication.py:396` E27 `attestation_missing_record`，建单行 L47 ✓；`wsl_anchor46…receipt` 绿（46bd8b16 非先在）✓；`win2_head…receipt` 同签名红（宿主无关）✓；head 主臂同 E27 ✓；iso 绿 `iso_ok_receipt_attacks` = 3 passed RC=0 ✓。
- H1 语义保真：diff 把 `attestation_status="host_signed"` → `"unattested"`；产品签名默认值实测 `def build_publication_receipt(..., attestation_status: str = "unattested", ...)`，G3a（I-08-A §2.5 E26→落 G3a 保留）明文 `unattested` 合法、`host_signed` 无记录才拒（E27→G4）。测试本义（实读 L35-55）= **伪造 `executed_gate_ids` 后 `validate_published_forecast` 终验必须拒**（`assertRaises(ForecastInputError)` 在 L54-55，与 attestation 标签正交）→ 标签改动不移本义，且 iso 3/3 绿证明拒绝路径仍触发。引用核：B1 decision（`B1-I08C-product-fixes/a20260921-01/decision.md` L182-187）逐字含 "rewriting it is I-08-B's item … frozen E32" ——但位置是 **§4 第 5 条**（§5 是 Measured results），卡面引作 "§5" = 章节号误差（F-4）；B1 `commands.json` L163 "99 passed, **EXACTLY ONE expected failure**: …false-green source" ✓ 逐字。

### (b) #12 zr708 → `70dd9f6e` 同提交双面 + 姊妹测试补丁漏打 — **CONFIRMED**
- `git show --stat 70dd9f6e -- scripts/analysis/confidence.py scripts/contracts/document.py tests/test_backtest.py` = **三个都动**：confidence.py +16（usable_origins/limitations）、document.py 53 行面（含新增 `require(origin < available <= cutoff, "historical accuracy future information leak: …")`）、test_backtest.py +1 ✓。
- 姊妹补丁逐字先例：`git show 70dd9f6e -- tests/test_backtest.py` = `+    data["as_of_date"] = "2028-03-01"  # Only usable after these actuals are known.`；活树行号实测 = **test_backtest.py:245**（卡面行号精确）✓；`-S 'Only usable after these actuals are known'` = 仅 70dd9f6e ✓。
- zr708 活树 L76-77 **无** as_of（漏打实证）✓；失败栈 raw（head + at70dd 同签名）= `confidence.py:151 → document.py:796` E-future-leak ✓；成对 8b7229c3 绿（7 passed）→ 70dd9f6e 红（1F/6P）✓；iso 绿 `iso_ok_zr708` 7 passed RC=0 ✓（H4 与姊妹补丁逐字同款，含同注释）。
- H4 同一类：**夹具漏适配的一行**（同提交对姊妹测试打了同款、本测试漏打）= small-safe 条件满足 ✓。卡面 "confidence.py=棘轮文件同源不同面" 链接成立（70dd9f6e 同时是 confidence.py 棘轮违规的引入提交，register §55 棘轮条目互证）。

### (c) 家族 C 四点矩阵 → 目录名依赖、非 sha 回归 — **CONFIRMED（复审实读全部矩阵 raw + 机制活 grep + 修案双布局绿）**

矩阵（域=WSL、wiki 每跑前后=`5d72529`、fc1102 与 fc1302 两文件各四点全读）：

| # | sha | 布局 | raw | 结果 |
|---|---|---|---|---|
| 1 | b0d016a6 | 规范名 `/tmp/s9lay/revenue-forecast` | `wsl_layhead_fc_*` | fc1102 4P / fc1302 3P **RC=0 绿** |
| 2 | b0d016a6 | 错名 `~/rf-ci-repro` | `wsl_head_tests_test_fc*` | fc1102 3F / fc1302 2F **RC=1 红**，签名 `manifest triplet commits missing: ['revenue']` |
| 3 | 46bd8b16（末绿锚） | 规范名 | `wsl_anchor46_*` | 4P/3P **RC=0 绿** |
| 4 | 46bd8b16 | 错名 `/tmp/s9mis/rfclone` | `wsl_misname46_*` | 3F/2F **RC=1 红**，同签名 |

旁证：Windows 规范名 `win2_head_fc*` = **RC=0 绿**（双平台同为目录名相关、非 OS 相关）✓。→ 同 sha 红绿翻转仅由**目录名**驱动、末绿锚在错名下即红 → **与 sha 无关的复现环境病，非仓 sha 回归** ✓。

机制活 grep（域=RF 生产树 HEAD b7a6a116 只读）：`tools/daily_t2_runner.py:72` `"revenue": _head(PROJECT_ROOT)` vs `:79-80` missing 检查用 `PROJECT_ROOT.parent / {"revenue": "revenue-forecast", …}`；`tests/test_fc1102_t2_runner.py:119` `PROJECT_ROOT.parent / repo`、`tests/test_fc1302_scan_health.py:27` `PROJECT_ROOT.parent / name` —— **自仓两处解析不一致**即病灶，克隆名 ≠ `revenue-forecast` → manifest 自引用空 sha → missing ['revenue']。与卡面机制引用逐字吻合 ✓。

H5a/H5c 修案 = revenue→`PROJECT_ROOT`（diff 两个 hunk 实读 ✓）；**双布局绿**：`iso_misfix_fc{1102,1302}`（错名 `/tmp/s9isomis/rfiso` + 补丁）RC=0 ✓ + `iso_ok_fc{1102,1302}`（规范名回归）RC=0 ✓ → 规范名下与原式**逐字等价**（`PROJECT_ROOT == parent/"revenue-forecast"` 当且仅当名合规），CI/生产零行为变化成立。备选零代码方案（克隆改名）已并列披露 ✓。

## 3. #8 STOP 裁定 — **CORRECT POSTURE CONFIRMED**
- 守卫自注实读（`tests/test_single_owner_guard.py:19-22`）：`ORCHESTRATORS = {"source_preparation.py"}` 上方注释 = "No new entries without review — a second *download owner* is exactly what this guard forbids." → **明文 review 门** ✓。
- 引入：`git log -S 'import subprocess' -- scripts/revenue_core.py` = **仅 ec307d20** ✓；`git show ec307d20 -- scripts/revenue_core.py` 实见 `+import subprocess` + provider spawn `subprocess.run([str(resolved)], …)` + `TimeoutExpired` 分支（attestation 握手，非 download）✓。
- 成对 + 双平台：95df2661 绿（3P）→ ec307d20 红（1F `revenue_core.py imports subprocess`）、`win2_head` 同签名红（AST 平台无关）✓。
- 三选项齐：decision §1#8 行实录 ①审查后入白名单+注记 spawn=attestation 非 download ②守卫收窄至 download-adapter 符号面 ③spawn 挪入 canonical client，且注明均触守卫契约 → owner 裁 ✓。**STOP（owner-ruling-needed）正确**：任一选项都改 R3 冻结守卫语义，超出本卡 small-safe 授权。

## 4. #2 family-card 路由 — **CORRECT（非本卡修面）CONFIRMED**
- B1 decision 引文逐字 ✓（见 §2(a)；章节号 §5→实为 §4#5，F-4）。
- I-08-A §7.1 实读：标题 "**7.1 I-08-B 的验收前置：先失败，再改**"；点名假绿源 `tests/test_attestation.py:71` 的 `test_configured_provider_means_host_signed_publication`；要求新语义落地前同断言先红、失败码 **E32 `provider_capability_unproven`**、改写权转 I-08-B ✓。
- I-08-B `handoff.json`：`status=accepted_scoped`、`next_action` 逐字 "Apply the **SAME 14 files (9 edited + 5 added)** to the product repo **from a card authorised to write it**" ✓（14/9/5 计数其内部多处自洽）。
- 实证红与预断吻合：`wsl_atEc3…attestation` = `attestation_capability()` False、1F/6P、恰为断言 `assertTrue(attestation_capability())` 处 ✓；成对 95df2661 绿 ✓。
- 裁定：**family-card-needed（落 I-08-B-14FILE 授权卡）为正确路由；本卡不动它 = 守住改写权边界** ✓。父已派卡（register §81 ①）。

## 5. §55 计数修正裁定 — **CORRECT（14 → 9），附 unproven 注记**

**判词**：接受提案——`本仓固有14`（register §55 取证段，域=register 2026-09-23 版）中的 **fc×5（fc1102×3 + fc1302×2）应从"仓缺陷/真 CI 红"计数中剔出**，改记 "复现环境病（目录名依赖）"；§55 残余计数修正为 **9 = 棘轮×2 + A/B 族 7（#1/2/8/9/10/11/12）**，其中 5（#1/9/10/11/12）由本 changes.diff 覆盖（待合并落地批），#2 待 I-08-B-14FILE，#8 待 owner 三选一。

**证据（三腿，复审全部独立实读）**：
1. **四点矩阵**：§2(c) 表 —— 同 sha 双布局翻转、双文件、双平台齐备，末绿锚错名即红 ⇒ 非 sha、非 OS、纯目录名。
2. **机制**：活 grep 证实 `_manifest`/runner 自仓解析 `parent/"revenue-forecast"` 与 heads `_head(PROJECT_ROOT)` 不一致（见 §2(c)）。
3. **CI 工作区构造（域=RF `.github/workflows/quality.yml` + `tools/ci_checkout_siblings.py` @ b7a6a116 活读）**：`actions/checkout@v4` 默认检出至 `GITHUB_WORKSPACE` = `/home/runner/work/<repo>/<repo>`；origin=`github.com/zhengcb81/revenue-forecast` ⇒ 末段 = **revenue-forecast（规范名）**；`SIBLING_DIR="$(dirname "$GITHUB_WORKSPACE")"` + `ci_checkout_siblings.py --sibling-root "$SIBLING_DIR" --skip revenue` 把 filing/wiki 落为同名规范目录（脚本 `dest = checkout_root/<revenue-forecast|filing-fetch|company-wiki>`，docstring 自注 mirrors local dev layout）⇒ CI 内 `PROJECT_ROOT.parent/"revenue-forecast" == PROJECT_ROOT` **按构造恒等** ⇒ fc×5 的 missing 检查在真 CI 按构造通过（绿色 by construction）。

**Unproven 注记（= 实现方 unproven#1，必须随判词入册）**：**真实 GitHub CI 的步9 逐测试日志未读**（本卡无网络；GH steps API 只到 step 级、不到 test 级）。"真 CI 绿" 是**机制推论非实测**；且 register §55 "两臂均红" 的臂证据来自本地重放（重放环境目录名即病灶），与环境病解释自洽但不构成 CI 实测。**若日后读到 GH 日志中 fc1102/fc1302 逐测试红，本判词须复议。**

**不采纳 reject**：无任何反证（不存在"真 CI 规范名下 fc×5 红"的观测）。

## 6. 收口边界 — **CLEAN**

- **零产品改动**（域=本复审会话活测）：`git status --porcelain` 现态 100 条**全部** `.planning/**`；对 `scripts|tests|tools|compatibility|e2e|.github/` 的状态行过滤 = **0 命中**；`porcelain_close.txt`/`porcelain_delta.txt` 同样 0 产品路径命中（grep `^.{3}(scripts|…)/` 无匹配）✓；实现载体 = changes.diff（我亲跑 apply --check rc0 @`%TEMP%\s9revclone`@b7a6a116、真 apply rc0、py_compile 7 文件 rc0）✓。
- **porcelain delta 归属**：delta 87 行 = ①本卡 attempt 文件（基线 `?? RF-STEP9-TRIAGE/` 目录级 → close 展开文件级）②并发兄弟卡产物（`M OWNER_DECISIONS/RESPONSES/…`、`?? AUDIT-*/RF-RATCHET-*/I-10-A/CW-GATE-UNBLOCK-2/PUSH-LOGS-ARCHIVE/I-07-D/…`）——与卡面声明一致；基线 5 条实读（UTF-16）= `M REMEDIATION_REGISTER` + `?? I-07-D/` + `?? RF-STEP9-TRIAGE/` + `?? .tmp-r41-mutation/` + `?? assurance/…plan_inputs.json.bak`，与 binding 逐条同 ✓。
- **本卡 10 文件跨并发推进零变更**：`git diff --stat b0d016a6..HEAD(b7a6a116)` 对 8 测试+2 工具 = **空输出** ✓（卡面 10 文件声明亲证）。
- **` M oracle.md` 归因**：batch-9（`b7a6a116`）已提交 attempt 部分文件；现工作树 oracle.md 相对 HEAD **+5 行 = 父方"追认"段**（内容与 register §81 互证、带日期标注）——**父方收口动作，非实现者、非本复审写入**；披露即可，实现者 close 证据（porcelain_close 22:31 / delta 22:38）先于该追认。
- **WSL 环境钉（活复测）**：`~/rf-ci-repro` = `b0d016a645f…` ✓、`~/company-wiki` = `5d725294304a…` ✓、`~/revenue-forecast` **不存在**（错名病灶仍在复现环境，与卡面自述一致）✓；filing 钉 `89c8bdb2…`（env_facts 实测记录，未再翻动）。
- **无网络**：attempt 文档 grep 无 curl/wget/http/gh api/Invoke-WebRequest/push；唯二命中为本地路径 fetch 与文档性回滚指令 ✓。本复审亦全程无网络。

## 7. FINDINGS（全 minor；无一阻断 ACCEPT）

| ID | 级 | 内容 | 建议处置 |
|---|---|---|---|
| F-1 | MINOR | `changes.diff` 实际 **7 hunks**（7 `@@` 头，复审 grep 计数）；decision §5 / commands §8 / register §81 均称 "8 hunk/8H"（推断=把 zr601 单 hunk 内 2 处编辑或 H5 三拆重复计数）。7 文件数与 5423 B 均 ✓，apply rc0 ✓ | 父落定转录时改 7H；不需重生成 diff |
| F-2 | MINOR | `evidence/git_anchors.txt` 实为**生成脚本本身**（19 行 echo 命令、无输出），binding "git 锚（…全量）" 表述过强 | 内容实证已由复审独立补齐（`-S` 六串 + show 两提交全与卡面一致）；建议 binding 改注 "脚本，输出见证词/复审报告" 或补存输出 |
| F-3 | MINOR | handoff evidence 枚举 = 71 项，实数 **72**（漏计 `porcelain-baseline.txt`） | 落定补一行 |
| F-4 | MINOR | 决策表 #2 引 "B1 decision.md §5"，原文实位 = **§4 第 5 条**（§5=Measured results）；引文逐字无误、`commands.json` "EXACTLY ONE expected failure" ✓ | 落定改 §4#5 |
| F-5 | MINOR（披露） | 复审期间父方追认段写入 oracle.md（` M`，+5 行）——post-close 父动作，已归因 | 无动作；父提交时一并入库即可 |

（观察、不立案：`wsl_oldwiki` 对照臂中 fc1102 的红含旧钉 TypeError 附加签名，decision §2(v) "全红同签名" 对 fc1102 略宽——方向性结论"wiki 钉非这 12 之因"不受影响，主臂@新钉已全量复现 12 项。）

## 8. UNVERIFIED（如实边界）

1. **真实 GH CI 逐测试日志未读**（无网络）→ §55 CORRECT 判词带复议条款（§5）。
2. changes.diff **未全量 step9 选集复验**（仅 8 目标文件 + patrol CLI + py_compile 域内；复审另证 apply/py_compile rc0，未重跑 pytest 全集）。
3. ruff/mypy 未跑（环境无 ruff；字符串级改动）→ 落地卡补静态面。
4. cipin 对照弃跑：复审判定**冗余非缺口**成立（missing=['revenue'] 机制与 wiki 值正交、oldwiki 臂已覆盖钉维度、/tmp 跨重启清除如实入档）。
5. `b0d016a6..977fa1e8` 等效性声明未逐 commit 复核（以 `b0d016a6..b7a6a116` 10 文件零 diff 的亲测替代）。

## 9. 范围-if-接受（供父方排批）

1. **changes.diff = 7 文件**（receipt_attacks / mutation_patrol / zr601 / zr708 / fc1102 / fc1302 / daily_t2_runner；hunk 计数以复审 7H 为准）→ 父与 ratchet 三卡（FIX-2/REST-B/REST-A）+ REST diffs **合并为一次 apply+commit+push 批**；apply --check 已双证 rc0（实现方 + 复审）。
2. **#2 → I-08-B-14FILE 授权卡**（父已派，register §81①）——本卡不动。
3. **#8 → owner 三选一**（白名单注记 / 守卫收窄 / spawn 挪位）——register §81② 待 owner 票。
4. **家族三分**（A=ec307d20×4 / B=70dd9f6e×3 / C=布局×5）随本判词转录 register。
5. **§55 计数修正 = CORRECT（14→9）+ unproven#1 注记 + 复议条款** → 父凭本判词入册（§81④）。
6. oracle 未决问题：父 §81 追认已录（oracle.md 尾段），handoff unsigned 段关闭 ✓。

## 10. 合规自检

- 写入面：仅 `reviewer_report.md` + `reviewer_report.sha256`（本两文件）；RF 产品/测试/工具/其他 attempt 零写入。
- git：全部只读（log/show/diff/status/rev-parse/clone-from-source）；唯一状态变更 = %TEMP% 克隆内 apply（域外）。
- 网络：无。WSL：只读 rev-parse/ls。%TEMP%：`s9revclone`（留作复审复跑证据，父可清）。
- REM-79 自检：`REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`（PYTHONIOENCODING=utf-8）对本报告扫描 = **0 violation(s)、exit 0**（域=本复审会话 2026-09-23 单文件单次运行）。
- 不自签声明：本报告为复审判词；卡面 status 落定（review_pending → accepted）与登记册写入**由父方执行**，本代理不改卡面任何既有文件。
