# reviewer_report.md — TTL-30D-POLICY / a20260922-01（独立复审签署，2026-09-22）

> 签署性质：本文件是**独立复审者**对本 attempt 的验收裁决。实现方未签（handoff.unsigned.implementer_signed=false 已核），本报告不代实现方签、也不声称任何外部方签名。复审动作限于 read / grep / pwsh（含 %TEMP% 内复跑）；对 CW/RF 生产树零写、零 git。

## Verdict

**ACCEPT — 证据链齐备、原始件自洽、披露诚实**；接受范围严格限定为父派发所列五项：

1. 生产提交权归父：CW guard 单文件，after = `142AE84838960D500528F2BD3BEE1742758152E0518E061A67ED3997CA6DD7DD`（勿 `git add -A`）。
2. U-1（N7 窗口内 past-now 类）维持 **unproven**，本卡未宣称已堵死。
3. U-2（cap 不在 RULESET_HASH 载荷）= **声明式契约 + 运维纪律**的如实披露，非缺陷。
4. U-3（CLIP vs REJECT 先例冲突）= 父欠一次归一裁决，须与 I-06-A/a20260922-02 复审协调；本报告只记录分歧、不裁全局选择。
5. 零产品测试编辑（复算成立，见 F9）。

## Findings（逐项复核，编号即复核次序）

### F1 — 交付件重哈希（逐项相符）
live 重算与 `evidence/final_deliverable_hashes.json` / handoff / decision §6 **逐项相符**：
`oracle.md`=30c4b637dd174f2bcfd3c0a6778519f543c94b70c9a4e93f94eec8551ca704c2（13447 B）、`oracle_freeze.json`=50c94d63…8ddc、`binding.json`=d3ed1e35…9379、`commands.json`=566c0893…e788、`decision.md`=acd9bff8…e7bc、`recovery.md`=79eeca05…fb1b、`handoff.json`=e4e6fbd9…16c7c、`changes.diff`=8271158b…dbd3、`iso/`=142ae848…7dd、`mutants/m1`=61cdab69…b779、`mutants/m2`=f75eed61…d90f、`caller_audit.txt`=b42b2153…8c6a、`product_tests_before/after/mutant_m1`=58b4ba08…/39fe2be5…/56cd47b8…、`hashes.json`=b0a8615b…32a6。全 attempt 字节扫描：**0** 个文件带 UTF-8 BOM（与 `bom_remaining: []` 相符）。

### F2 — 冻结先行（CreationTime 顺序实证）
CreationTime 升序：`oracle.md` 22:53:00（attempt 内最早）→ `iso/` 22:55:47 → `scripts/ttl30d_probe.py` 22:57:01 → `evidence/red_before.json` 22:57:22（第一次运行）。oracle.md 末次写入 22:55:45 **早于**首跑 22:57:22 ⇒ §5 勘误（含 §5-3 N7 预登记非门禁）落在预跑窗口内，与 oracle_freeze.json 的 errata_note 一致；oracle 收尾哈希 == 冻结哈希（F1）；`red_before.json` 内嵌 guard_sha256=f900a13d… == 冻结前态 ⇒ 预期先于目标被触碰而固定。frozen-first 成立。

### F3 — before/after 锚 == live 生产
binding/decision/handoff 的 before=`F900A13D7C22FE3BD742485C6B603DE11B92A56D2414a2A046216CCD3B0B9C08`（大小写归一后）== 我方 live 重算 `f900a13d…9c08`（CW 生产 guard）；after=`142AE848…7dd` == iso live 重算 ✓。

### F4 — changes.diff 可复现且无 git
用该卡 `scripts/make_diff.py`（difflib，读 live 生产 + iso）重新生成到 %TEMP%：**112 行 / 6 hunks / sha256=8271158bf034e6fec60b65d48bec173f5ee1a98ad1538d29a8daebcbd29fdbd3 == 卡面哈希**，逐字节相同。6 个 hunk 头：@@ -20,12 / -58,6 / -157,13 / -187,6 / -194,6 / -211,6。

### F5 — 计数从原始件复算
- RED `red_before.json`：gating_total=16、gating_passed=**7**、gating_failed=**9**，红集={C0,G1,N1,N2,N3,N5,N6,N8,N9} == 预登记集（派发方所记 9 = 其计数含 G1，吻合）；N7 为 gating=false、观测 hit。
- GREEN `green_after.json`：**16/16**，failed=[]，内嵌 guard_sha256=142ae848… ✓；`green_confirm.json`（还原后复测）：**16/16** ✓。
- MUT-1 `mutation_m1_cap_removed.json`：gating_failed={G1,N1,N2,N3,N8,N9} == 冻结集（10/16），内嵌 sha=61cdab69… == m1 文件 ✓。
- MUT-2 `mutation_m2_pastnow_removed.json`：gating_failed={N5,N6} == 冻结集（14/16），内嵌 sha=f75eed61… ✓。
- 变异纯度（我方 difflib 逐行比对 iso↔m1/iso↔m2）：**m1 = iso 恰减 5 行 cap+isfinite 块（单 hunk）**；**m2 = iso 恰减 past-now 分支块（单 hunk）**；一次只翻一个 guard 成立。

### F6 — 我方独立复跑两例（%TEMP%\rev-ttl30d-rev1，新镜像 + iso 守卫）
- 探针全表：**16/16，failed=[]**，guard_sha256=142ae848…。
- **N1（超帽 365d）**：raise `PromptInjectionGuardError`，message **逐字** `ttl_seconds exceeds policy cap of 2592000s` ✓。
- **N5（FIXED iso 上 past-now）**：raised=null、`status=not_reviewed`、`cache_state=tampered`、reason=`receipt reviewed_at is after now (clock anomaly; now may only tighten freshness)`（含 `reviewed_at`）✓。
- 附带：G1 raise 文案与 N1 **同一逐字串**；N7 观测 hit（与预登记非门禁一致）；N8 文案 `ttl_seconds must be a finite number`、N9 走 cap 文案。

### F7 — 实现轨迹（iso after 逐行读过）
- 常量 `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400 * 30`（L85）；前有注释块 L77-84（§十九/C6/4c/policy_hash 覆盖面），模块 docstring L24-36 声明「cap 属 policy_hash 覆盖的政策面、改值=政策变更、旧回执按 OPEN-4 4c 读取时失效」；`__all__` L267 含该常量 ⇒ C0 三条件齐。
- 校验序（L239-250，全部在 L250 `_receipt_from_store` **之前**）：source_sha256 格式 → policy_hash 格式 → `ttl<0` → **`>cap` 逐字 raise** → `math.isfinite`（NaN 拒）→ 才查 receipt ⇒ 缺失 receipt 也拒超帽（先非法输入后查库）。
- `_freshness` L201-210：`now_seconds < reviewed_at` ⇒ `not_reviewed/tampered`（clock-anomaly 文案），位于 age>ttl 比较之前；`now==reviewed_at` 仍 fresh（严格 `<` 边界，P3 绿）。
- 边界语义核对：`-inf` → `>=0` 文案；`+inf` → cap 文案；`NaN` → finite 文案（探针 N8/N9 复跑证实）。

### F8 — 透传继承（G1 代码路径）
`readiness_graph.py` L82 参数 → L102 `ttl_seconds=ttl_seconds` 传入 `evaluate_review` → L115/L132 公开入口透传；readiness 侧**无**自建上限 ⇒ 自动继承（我的探针 G1 与他们 raw 同文案 raise）。readiness 文件本身零改动（不在 diff 内）。

### F9 — 零测试编辑：独立复算成立
- 全 CW 仓 grep `ttl_seconds`：产品测试调用点 = `test_prompt_injection_guard.py` 10 处（L187/201/214/228/241/253/268/286/298/302）+ `test_readiness_graph.py` L223 与 L181（`"ttl_seconds": TTL`，TTL=86400*30 见 L34）⇒ **12 处**，与 decision §7 的 10+2 一致；最大值 **== 2592000 == cap**；`>cap` 计数 = **0**。
- 诱饵排除：`tests/contract/test_source_catalog_control.py` L700/707 的 `now + 86400 * 365` 是 `llm_summary_failures` 过期时间戳列，非 `ttl_seconds`（该文件 grep 无 ttl_seconds）。
- 其余 CW `ttl_seconds` 命中均在 docs/plans 的 json schema（`authorization_ttl_seconds` 最大 2592000、journal `ttl_seconds` 最大 300）= 异域，非 guard 调用点。
- 编辑面：CW `tests/` 最新 mtime = 22:22:42 < 本 attempt 窗口起点 22:53 ⇒ **0** 个 CW 测试文件在本卡执行期内被写。
- 结论：`caller_audit.txt` 的「max==cap、>cap=0 ⇒ 零测试编辑」复算成立。

### F10 — 诚实缺口 U-1 / U-2 / U-3（含引文核对）
- **U-1**：oracle §5-3 把 N7 定为预登记**非门禁**结构性限制 —— 由 F2 的时间证据证其先于首跑落笔；red/green 两轮 N7 观测皆 hit、gating=false、decision §5-1 与 handoff.unproven 如实记 ⇒ 未当通过宣称，维持 unproven ✓。
- **U-2**：iso 内 `RULESET_HASH = sha256(json(_RULESET_PATTERNS))`（L69-73），cap 常量**不在**载荷 ⇒ 改 cap 不自动翻 policy_hash，属实。裁定依据引文核对：OWNER_DECISIONS.md:439 逐字吻合；OPEN-6 ruling.md:172 C6 逐字吻合（负例「被拒或被策略上限截断」在位）；:215「L168 纯调用方比较、无策略侧上限」在位；OPEN-4 ruling.md:63（4c APPROVE：读取时失效、政策内容变⇒作废全量重审）与 :116-127（policy_hash 不符 ⇒ ignored→not_reviewed、下次读取时失效、全量重审拒增量补审）在位；「**TTL 的数值不由本裁定规范**」逐字在 **:137**；**:194** 语义相同（「本裁定全文未写规范数值…TTL 归数值裁定轨道」）但非该句逐字 —— decision §1 把 :137/:194 并称「明文」属**轻微引注瑕疵**（见 F14-3），不改结论。U-2 定性=声明式契约 + 运维纪律、自动翻转会作废全部现存回执、超本卡授权 ⇒ 如实披露成立。
- **U-3**：先例实现**双方都在盘上**已证 —— I-06-A/a20260922-02 iso 守卫 live 重算 = `cf9174b538288f71349f3d33b46f96eacb6a16f5df4906764b08439230119c03`；其 L78-82 `effective_receipt_ttl` = **CLIP**（`min(float(ttl), RECEIPT_TTL_POLICY_CAP_SECONDS)`，L71 常量=86400*30）于 L296 应用（另有 L297 `effective_review_instant` 钳 now）。**生产两者皆无**：live CW guard grep `effective_receipt_ttl|RECEIPT_TTL_POLICY_CAP|effective_review_instant|policy cap` = 0 命中 ⇒ 分歧记录在案、归一权在父（与 I-06-A 复审协调）；本报告不裁 CLIP/REJECT 全局选择 ✓。

### F11 — 产品基线 26
raw 三件：before「26 passed in 9.46s」、after「26 passed in 13.68s」、mutant m1「26 passed in 16.66s」，均带同一 CW-BASETEMP-DECISION 头。我方在 %TEMP% 镜像**独立复跑一次**（iso 守卫、零测试编辑）：**26 passed in 4.52s** ⇒ m1 下产品测试仍 26 = 帽变异是探针独测（oracle 探针为唯一探测器）的诚实陈述成立。

### F12 — commands 账本诚实（GBK + BOM）
- C11a rc=1（GBK 编码 U+21D2 致 stdout 管道失败、19 行残片）**已披露**；C11b 直写 UTF-8 覆盖 —— 我方复现（F4）得同一哈希 ⇒ 终件干净、残片未被当证据使用。
- BOM：`scripts/_final_hashes.py` **检查 4 个候选件**（`evidence/hashes.json` + 3 个 product_tests txt），`final_deliverable_hashes.json` 记 `bom_normalized` = **3 件**（3 个 product_tests；hashes.json 当时无 BOM）、`bom_remaining` = []；三件 product_tests 的 mtime 均为收尾 23:17:00.21x 与该次归一动作吻合。我方全树字节扫描 = 0 BOM，raw 件内容（26 passed 三行结构）完好 ⇒ 原始件自洽。
- 轻微账本缺口：**commands.json 未列 BOM 归一步骤**（该事实只在 evidence/final_deliverable_hashes.json + 脚本内可查）—— 记为披露渠道瑕疵，非隐匿（见 F14-2）。派发方所称「4 BOM-normalized」对应**受检候选 4 件**；实际落笔归一 3 件，以 `bom_normalized` 为准。

### F13 — 边界：生产零写 / 零 git / recovery 单文件
- 生产零写：CW guard live 重算 == f900a13d（F3）；对 CW 全树做本卡窗口（22:50–23:20）mtime 扫描：源码/测试**零**写入，唯一命中 `.source_catalog/catalog.sqlite3-shm`（SQLite 瞬态旁车；`catalog.sqlite3`/`-wal` 停留在 09-19，数据文件未动）—— 该旁车无法归因到具体进程（窗口内有兄弟 attempt 并行），记入 Unverified。
- 零 git：我的边界禁 git ⇒ **porcelain spot 未能执行**；替代证据 = commands.json 全程无 git 动词、changes.diff 由 difflib 生成且不依赖 git 可逐字节复现（F4）。
- recovery.md = **恰 1 文件**回滚：正向锚 142AE848→落地、回滚锚 F900A13D（=生产 HEAD 现字节），after→before 哈希对齐齐、提交范围「恰好 1 个文件、勿 git add -A」、回滚后行为复归 before 基线并注明产品测试仍 26（探针存在的理由）—— 与 F1/F3 相符。
- 附带观测（RF 仓、TTL 卡范围外）：`revenue-forecast/tests/test_fc905b_trusted_receipt.py`、`tests/test_message_contract_pins.py` 在窗口内被写（23:15:07.9839532 / 23:12:33.4872869），内容与兄弟卡 `FIX-W06-GAPS/a20260922-01/iso/rf/*` **逐字节相同**（db8bbb48… / 41da045c…）；RF 根 `.pytest_cache\v\cache\nodeids` 22:55:37 亦在窗口内。该组写入与本卡 ledger/iso/脚本**无交集**，归因指向兄弟卡，非本卡 —— 报父处置（见 Unverified 第 2 条）。

### F14 — 瑕疵清单（不阻断接受）
1. （信息）oracle.md 的「frozen-first」目前靠文件系统时间戳 + 收尾哈希双证；若计划层要更强证据，后续卡可加冻结时刻的外部时间锚。
2. （轻微）BOM 归一步骤未入 commands.json 步骤表（F12）。
3. （轻微）decision §1 把 OPEN-4「:137,:194」并称逐字明文；:194 为同义非逐字（:137 逐字无误）。
4. （提示）decision/handoff 记「prod 与 iso 均 LF-only（0 CRLF）」— 我方按哈希链复现 diff 与该陈述一致，未另做逐行 EOL 计数（非门禁项）。

## Unverified（明确未验 / 维持开放）

1. **git 状态与 porcelain spot**：复审边界禁 git，未跑 `git status`/`diff`；RF/CW 的 git 卫生以 mtime 扫描 + 哈希 + 卡面 ledger 替代（F13）。
2. **窗口内非本卡写入的归因**：`catalog.sqlite3-shm`（CW）与两件 RF 测试文件 + RF `.pytest_cache` 的写入者，仅凭内容/时间相关性判为兄弟活动（FIX-W06-GAPS），无逐进程取证；请父按 sibling 卡口径处置 RF 测试文件写入是否越界。
3. **U-1**（now∈[reviewed_at, 合法 now) 窗口内 past-now）：结构性不可判，维持 unproven；证明需可信时钟/单调锚的契约变更。
4. **U-2**（cap 入 RULESET_HASH 载荷的自动作废）：未实现、按授权不做；= 声明式契约 + 运维纪律披露。
5. **U-3**（CLIP vs REJECT 归一）：只证双方实现存在、生产两者皆无；全局裁决留父 + I-06-A 复审。
6. **U-4**（生产接线行为）：shadow-only 模块尚无生产入口调用 evaluate_review，按设计未验。
7. 本报告不含任何外部签名；实现方自始未签（handoff.unsigned 逐项核过）。

## REM-79 自检

对本报告原文运行 `REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py v1.2.0-correction2`（stdlib、只读）：**`0 violation(s) across 1 file(s)`，exit 0** —— 本文件即定稿，随后落 `reviewer_report.sha256`。

## 复跑与足迹

- 复跑环境：`%TEMP%\rev-ttl30d-rev1`（新镜像 = CW src 拷贝 + 2 测试 + 2 conftest + iso 守卫 142ae848）；探针 16/16；pytest 26 passed；变异纯度比对与 diff 复现脚本产物均落 %TEMP%。
- 生产足迹：CW/RF **零写**（F13）、**零 git**；本报告与 `reviewer_report.sha256` 是我写入 attempt 的**仅有**两个文件。
