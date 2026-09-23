# reviewer_report.md — M01-M04-PROPAGATE（独立复审）

- **Card / Attempt**: `execution_runs/M01-M04-PROPAGATE/a20260922-01/`
- **Authority (read live)**: `OWNER_DECISIONS.md:424`，§十八【已裁定·第四批】
- **Verdict**: **`accepted_scoped`**（带 2 项 minor 文档发现 + 1 项表述修正要求，均不影响结论）
- **Reviewer toolset**: read / grep / pwsh（受限工具集；无 git 写；四个历史 attempt 与生产仓只读；我的两次 spot run 只写 `%TEMP%\rev-m01m04-spot\`；本卡目录内我只新增 `reviewer_report.md` + `reviewer_report.sha256` 两个文件；不自签）
- **Sidecar**: `reviewer_report.sha256`
- **REM-79 self-scan on this text**: `python …\REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py reviewer_report.md` → `0 violation(s) across 1 file(s)`，exit **0**（域：本报告文件单文件扫描；全称断言均带同域限定）

---

## 0. 权威行（实读，非转述）

`OWNER_DECISIONS.md:424` 原话：

> | **A-1 = 1（①扩权）** | REM-21/T1-8 同形态门传播**扩到 M01–M04 四批**（修在副本、before/ 留旧、历史 rc 零回改、证据齐全） | 卡 `M01-M04-PROPAGATE` 已派（subagent 08e56200）；预期臂 **E=0/F=3/G=2/S=1**；登记行关闭待其复审后 |

登记行（`REMEDIATION_REGISTER.md:869`）同文：`| M01-M04-PROPAGATE（08e56200） | A-1=①扩权 | 同四前置形态；预期臂 E=0/F=3/G=2/S=1；历史 runner/rc 零回改 |`。

⇒ 本次复审判据 = 四前置（副本修复 / `before/` 留旧 / 历史 rc 零回改 / 证据齐全）+ 臂表 E=0/F=3/G=2/S=1。**域**：本卡；B 臂为契约内惰性对照（额外臂，非 owner 臂表项）。

---

## 1. Source identity — PASS

1.1 **8/8 历史 runner 复算一致（域：`M01..M04\a20260919-01` 下全部 `run_card*.py` 文件）**。
逐个 `Get-FileHash SHA256`：

| 路径（相对 `execution_runs/`） | sha256 | 字节 |
|---|---|---|
| `M01\a20260919-01\scripts\run_card.py` | `b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816` | 12222 |
| `M01\a20260919-01\recovery\r2_exit_code_selfcheck\run_card.py` | 同上 | 12222 |
| `M02\…\scripts\run_card.py` | 同上 | 12222 |
| `M02\…\recovery\r2_exit_code_selfcheck\run_card.py` | 同上 | 12222 |
| `M03\…\scripts\run_card.py` | 同上 | 12222 |
| `M03\…\recovery\r2_exit_code_selfcheck\run_card.py` | 同上 | 12222 |
| `M04\…\scripts\run_card.py` | 同上 | 12222 |
| `M04\…\recovery\r2_exit_code_selfcheck\run_card.py` | 同上 | 12222 |

（`old \ new` 与 `new \ old` 两个差集都扫了：`new \ old = ∅`、`old \ new = ∅`（域：上述 8 条路径 vs 声明的单哈希单字节数），即 8 条全部等于声明值，无任何一条落在声明之外。）

1.2 **「无门」source 核**：`before\run_card.py` grep `extra_unknown_id|case_contract|allowed_ids|id 白名单|__name__ == declared` → **零命中（域：该12222 B 文件全文）**；唯一相关硬下标是 L193 `"expected": case["expected"]`。⇒ 确无 case_contract id 闸门、确无逐例声明门。

1.3 **定位声明成立**：`execution_runs\M01-M04\` → `Test-Path = False`。M01–M04 确为四个独立卡 attempt（`decision.md` D-1 记录的定位结论为实，非猜测）。

---

## 2. Freeze-first — PASS（用 PS `CreationTime` 实测）

| 对象 | CreationTime（本地 +01:00） |
|---|---|
| `oracle.md`（sha `9ff1dedec8f2687298f6d083418558e16f85db5c247cb8c2213d2e6327dae0f4`，12579 B ✅ 复算一致） | **2026-09-22 19:49:24.524** |
| `evidence/oracle_freeze.json`（存在；记 `oracle_sha256=9ff1dede…`、`bytes=12579`、`mtime_utc=2026-09-22T18:49:24.528Z` ✅） | 2026-09-22 19:49:50.874 |
| **最早**臂输出（域：`evidence/**` 下 `run.json|out.json|stdout.txt|stderr.txt|rc.txt` 共 136 个文件按 CreationTime 排序的第 1 个） | 2026-09-22 19:53:40.619（`evidence\M01\E\evidence\M01\stderr.txt`） |
| 最晚臂输出 | 2026-09-22 19:53:56.898 |

⇒ oracle 严格早于最早臂输出 **256,095 ms（≈4 分 16 秒）**；freeze 记录文件亦严格早于最早臂输出（≈230 秒）。**先冻结、后运行成立（域：本 attempt 的136 个臂输出文件 vs oracle.md）**。

---

## 3. Arm results — PASS + 我自己的两次独立 spot run

3.1 **交付物复算**：`evidence/arms_raw.json` = `4f6d7f488abcfd5a75a58e8108b71b54b0da9fe976061f91d60998dc720364f3` ✅；`evidence/arms_summary.json` = `a3af8ebd410d5e194473115228b2bf9f971d49847fad15490052d69e767236bb` ✅。

3.2 **arms_raw 实读（顶层 = 20 元素数组，逐条列 `expected_rc` / `raw_rc` / `meets_expectation`）**：

| | E | F | G | S | B |
|---|---|---|---|---|---|
| M01 raw rc | 0 | 3 | 2 | 1 | 0 |
| M02 raw rc | 0 | 3 | 2 | 1 | 0 |
| M03 raw rc | 0 | 3 | 2 | 1 | 0 |
| M04 raw rc | 0 | 3 | 2 | 1 | 0 |
| 冻结预期 | 0 | 3 | 2 | 1 | 0 |

20/20 条 `meets_expectation = true`（域：`arms_raw.json` 的 20 条记录）。`arms_summary.json`：`all_arms_meet_frozen_expectation = true`、`deep_checks_passed = 60` / `deep_checks_total = 60` ✅。F 臂 4/4 `FAIL_declared_expectation_mismatch` on `NEG-CARD`、`raised=ModelRegistryError` vs `declared='ValueError'`、comparison 串含 `(exact type name; NOT isinstance)`；G 臂 4/4 `verdict=no_verdict`、`no_verdict_reason=cases_json_declared_expectation_missing:NEG-CARD`、`missing_count=1`、`mismatch_count=0`、`not_judged=[NEG-CARD]`。

3.3 **我自跑的两次 spot run（全新子进程，写入且仅写入 `%TEMP%\rev-m01m04-spot\`，复刻 `scripts/run_arms.py` 的 fixture 构造 + `commands.json` 的 argv 形状）**

argv（两条相同形状，runner 均为 `iso/run_card.py` = `f671732d…`，解释器 = M02 历史 venv `python.exe` = `0e818a1f…`）：

```
<py> -X utf8 -B <iso/run_card.py> --card M02 --attempt <TEMP>\{F|G} --code-root <iso/code_root> --out <TEMP>\{F|G}\out.json
```
`cwd = <TEMP>\{F|G}`，`PYTHONDONTWRITEBYTECODE=1`；fixture = 从 `M02\a20260919-01\evidence\M02\` 逐个顶层文件复制后按臂变异（F：首个 `expected=="ModelRegistryError"` 例（`NEG-CARD`, index 0）改 `"ValueError"`；G：同例 `del ["expected"]`）。

| spot | raw rc | 记录的 verdict | 关键观测 |
|---|---|---|---|
| **F**（M02 打补丁 runner） | **3** ✅ | `fail`，`exit_code_in_doc=3` | NEG-CARD 判 `FAIL_declared_expectation_mismatch`、`judged=true`、`declared='ValueError'`、`raised='ModelRegistryError'`、`declared_expectation_mismatch_case_ids=["NEG-CARD"]`、out.json 已写 |
| **G**（M02 打补丁 runner） | **2** ✅ | `no_verdict`，`exit_code_in_doc=2` | `no_verdict_reason = cases_json_declared_expectation_missing:NEG-CARD`、`declaration_unusable_case_ids=["NEG-CARD"]`、`cases_json_declared_expectations_usable=false`、`missing=1`、`mismatch=0`、out.json 已写 |

我自建的10 条断言 **10/10 PASS**，落盘 `%TEMP%\rev-m01m04-spot\spot_results.json`（含原始 rc、argv、frozen/arm cases 哈希）。跑时 runner sha 复算 = `f671732d…`。**历史 attempt 在我两次跑中零写入（域：spot 脚本的全部输出路径都在 `%TEMP%`，argv 的 `--attempt/--out/cwd` 三项均指向 `%TEMP%`）**。

---

## 4. Historical zero-touch — PASS

4.1 **两份清单 + 两份验证件复算**

| 文件 | sha256（我复算） | 声明 |
|---|---|---|
| `evidence/manifest_before.json` | `a03525360a8e8911399114223a28ab4ce9d5464e2d5ecca9cd59adedf9f02751` | `a0352536…` ✅ |
| `evidence/manifest_after.json` | `a0352536…`（与 before **逐字节相同**，raw `-ceq` 比较 = True） | `a0352536…` ✅ |
| `evidence/manifest_final_recheck.json` | `a0352536…`（raw 与 before 逐字节相同） | — |
| `evidence/manifest_verification.json` | `77a2f6b38caaba368df647abbd167f9a38827fe494f9552365fd3c918f8618a1` | `77a2f6b3…` ✅ |
| `evidence/manifest_final_verification.json` | `77a2f6b3…`（与上一文件逐字节相同） | `77a2f6b3…` ✅ |

4.2 **声称的规模/漂移复算**：`file_count = 7722`，实际条目数 = **7722**（域：`manifest_before.json.files` 的属性数）；`total_bytes = 99931221` ✅；`scope` = 四个历史 attempt 目录（`execution_runs/M01..M04/a20260919-01`）；`result=PASS`、`files_identical=7722`、`added_files=[]`、`removed_files=[]`、`changed_files=[]`、`zero_byte_drift=true`、`manifest_docs_byte_identical=true`、`live_rehash_matches_before/after=true`（**added=removed=changed=0，域：7722 条清单条目 vs before/after 两份文档 + 一次现场重哈希**）。

4.3 **三文件 spot 重哈希（跨三个历史批次）**

| 类别 | 路径（相对 `execution_runs/`） | 清单 sha | 现场 sha | 匹配 |
|---|---|---|---|---|
| runner | `M01/a20260919-01/scripts/run_card.py` | `b5fcc685…` | `b5fcc685…` | ✅（12222 B == 12222 B） |
| evidence json | `M04/a20260919-01/evidence/M04/cases.json` | `d515e1b7095b28222e6fadbfda2fcbb77b4decd49ff7bb2696044b0de7a905a4` | 同 | ✅（3184 B == 3184 B） |
| rc 载体 | `M03/a20260919-01/evidence/M03/run_result.json` | `74823d467800ac0f0d4915d18a9e54a4b32f5e14db68b5e2077b850d517441d6` | 同 | ✅（27055 B == 27055 B） |

（历史四批的 evidence 树内无 `rc.txt`；rc 载体 = `run_result.json`（域：`M01..M04/a20260919-01/evidence/**` 内 `*rc*|*exit*|*handoff*|*commands*` 的文件名扫描，命中者只有 `source_manifest.json` 与各批 `run_result.json`/`command_manifest.json`）。）

---

## 5. Patch provenance — PASS

5.1 **哈希与度量复算**

| 文件 | 我复算 | 声明 |
|---|---|---|
| `changes.diff` | `de038406681a31c053a841b9ba3da15ccfd456dd6e04d2ee99ac9a82fbdbdb64`，**+149 / −21**（净，已扣 `+++/---` 头行） | `de038406…` +149/−21 ✅ |
| `B5-fix-g1a-g3\a20260922-01\M05-M08\runner.diff` | `8263fc833fb48cbe1c2a11566d9541a5b00cfeaa5bcaf89894957911d2bac891`，10431 B，**+111 / −12** | `8263fc83…`、10431 B、+111/−12 ✅ |
| `B5-fix …\M05-M08\run_card.py` | `489ba7e35592241b91ecf393b515df2111bc4996298274226e0e1012deff230b`，20804 B | `489ba7e3…`/20804 ✅ |
| `B5-plan-level-remediation\a20260921-01\M05-M08\run_card.py` | 同 `489ba7e3…`（**逐字节相同**） | ✅ |
| `iso\run_card.py` | `f671732d4860404a925ab544b41b6fe2c6e62b9c65400b010aad2d7388ae3e0b` | `f671732d…` ✅ |
| `before\run_card.py` + `iso\run_card_before.py` | 两者均 `b5fcc685…`/12222 B | ✅ |

行数自洽：`271 − 21 + 149 = 399` == `iso/run_card.py` 实际行数 ✅。

5.2 **两个 diff 的 hunk 内容比对（两个方向的差集都算，域：两文件的 `+` 集，逐行、去头、去空行）**
- `changes.diff` 145 条 added 行 vs `runner.diff` 108 条 added 行；`only-in-changes.diff = 47`、`only-in-runner.diff = 10`。
- `only-in-runner.diff` 的唯一**代码**行 = `if not is_target:`；`changes.diff` 对应处为 `if is_import_or_file and not is_target:` / `elif not is_target:` —— 正是**已文档化的 b5fcc685 家族适配**（保留 `FAIL_import_or_file_error` 标签与 rc=1 未捕获崩溃路径，故判决分支多一层）。
- 其余差异全部是 rc 表/docstring 散文措辞与 `Authority: OWNER_DECISIONS §18 …` vs `Per-case expected enforcement (REM-21 / B5, …)` 标题行 —— **无第三类语义差异（域：上述两个差集的逐行人工判读）**。
- hunk 头各有7 个 `@@`，两侧插入点族群一一对应（rc 表块 / 声明前置块 / 判决块 / rc 路由块 / `exit_code_semantics` 块 / `negative_summary` 块 / `negative_counts` 块）。

5.3 **门形态（实读 `iso\run_card.py` 源码）**
- **精确类型名比较，非 isinstance**：L281 `declared_ok = (entry["raised"] == declared)  # exact type-name equality`；全文件 `isinstance` 仅用于 `is_target`（L264）、`is_import_or_file`（L265）、`declared_usable` 类型检查（L268）、以及 `c.get("expected")` 是否为非空 str（L133/L140）——**没有一处用 isinstance 比较声明与实抛（域：该文件399 行内全部7 处 `isinstance` 出现点）**。
- **声明前置在判定之前**：L132–140 在任何 case 循环之前算出 `unusable_declared` / `cases_declared_ok` / `no_verdict_reason`；L361 `if not cases_declared_ok or harness_incomplete: verdict="no_verdict"; exit_code=2`。unusable ⇒ rc=2 + `no_verdict` ✅。
- **mismatch ⇒ rc=3**：L294 `FAIL_declared_expectation_mismatch`；L367–369 else 分支 `verdict="fail"; exit_code=3` ✅。
- **NOT_JUDGED 分支**：L269–279 `judged=False`、`verdict="NOT_JUDGED_declaration_unusable"`、`declared_expectation_mismatch` 显式置 `False`（L273，永计入 mismatch）；L357–358 `negatives_ok` 只对 `judged` 用例求值 ⇒ NOT_JUDGED 单独不可能产生 rc=3 ✅。
- **`exit_code_semantics` 字段**（L371–391）：`harness_incomplete / positive_ok / continuity_ok / negatives_ok / verdict / exit_code / cases_json_declared_expectations_usable / declared_expectation_mismatch_case_ids / declared_expectation_not_met_case_ids / declaration_unusable_case_ids / reason_namespace` ✅。
- **删键可存活**：L243 `declared = case.get("expected")` ✅；**结构硬下标在 try 之外**：L244 `entry = {"id": case["id"], "kind": case["kind"], …}` ⇒ S 臂 `KeyError: 'kind'` 未捕获 ⇒ rc=1（与4 份 S stderr 的 `run_card.py:244 … KeyError: 'kind'` 一致）✅。
- **既有标签一个不删**：`PASS_rejected`（L296）、`FAIL_wrong_exception_type`（L292）、`FAIL_not_rejected`（L259）、`FAIL_import_or_file_error`（L290）全在 ✅。

---

## 6. 三项已披露的不主张 — 全部在册

**(i) 臂 S 的家族适配**
- **预登记于 oracle §4（先于运行）**：`oracle.md:98-106` 明写「B5-fix 字面 S 变异（`extra_unknown_id`）只在 M25–M28 生效……b5fcc685 家族的负例循环没有任何 id 白名单 / `case_contract` 闸门……**字面 extra_unknown_id 变异本卡不预跑**」；`oracle.md:143`（§7.4）再钉一次。
- **source 核（我独立做）**：`before\run_card.py` 全文 grep `extra_unknown_id|case_contract|allowed_ids` → **零命中（域：12222 B 原始字节）** ⇒ 家族确无 id 闸门，适配理由成立。
- **实测形态**：追加恰一个缺必选成员 `kind` 的例（`expected` 保持可用）⇒ `KeyError: 'kind'` 未捕获、不写 out.json、rc=1 ×4 ✅（与 decision D-4 一致）。
- **字面变体未跑/未主张** ✅（decision D-4 末句 + handoff `open_issues[0]` + oracle §7.4 三处）。

**(ii) 臂 B rc=0 = 实测值；历史 G=KeyError 未重跑**
- `exit_code_legend.md:21-24`：B = 历史字节副本同篡改 ⇒ rc=0 ×4 = 伪造绿复测；「rc=1 on a deleted `expected` (KeyError crash) remains the **historical** behaviour, recorded in B5-fix and left byte-untouched」。
- handoff `open_issues[1]`：「arm B rc=0 is a MEASUREMENT (matches B5-fix's two independent measurements E=0/F=0/B=0/G=1 …); the historical rc=1 G behaviour (KeyError) remains recorded in B5-fix and was **not re-run here**」✅。
- decision D-5 亦记「历史对照：同一四批历史形态为 E=0/F=0/B=0/G=1（B5-fix 两轮）」✅。

**(iii) REM-80 关闭 / 31-31 追认 = 父代理复审后；REM-84 超范围**
- `oracle.md:142`（§7.3）「不主张 REM-80 登记行关闭（复审后归父）」；`decision.md:74`「REM-80 登记行关闭 = 父代理在复审之后」；handoff `open_issues[2]`「REM-80 register-row closure, the 31/31-uniformity追认, and independent review belong to the parent AFTER review」✅。
- 31/31：`decision.md:60`「原 27/31 ⇒ 31/31 形态达成，**正式追认仍待复审+父关 REM-80**」✅（形态达成 ≠ 已追认，措辞未越界）。
- REM-84：handoff `open_issues[3]`「START_HERE append-3 (REM-84) is out of this card's scope」✅。

---

## 7. 边界

7.1 **`__pycache__` — 卡内文字与事实不符（见发现 F-2）**
- 现场实测（域：四个历史 attempt 全树递归）：**292 个 `__pycache__` 目录 / 3492 个 `.pyc` 文件**，全部位于各批 `iso/venv/Lib/site-packages/`（历史 venv 自带）。
- `manifest_before.json` 内 `__pycache__` 条目 = **3492**、`.pyc` 条目 = **3492** ⇒ 这些是**基线既有**项，且 before/after 两份清单逐字节相同 ⇒ **零漂移（域：3492 个 .pyc 相对 7722 条基线清单）**，即本卡未新增任何 `.pyc`。
- 本卡 attempt 目录内 `__pycache__` 目录 = **0**（域：`M01-M04-PROPAGATE/` 全树）。
- ⇒ 实质主张（`-B` + `PYTHONDONTWRITEBYTECODE=1` 未产生新字节码、历史树零漂移）成立；但 `decision.md:67`「全场零 `__pycache__`」与 `oracle.md:124`「任何位置无 `__pycache__`」是**无域的全称句且为假** → F-2。

7.2 **无产品写入 — 与卡的主张一致（域：本卡 `commands.json` 全文 + RF porcelain 与 mtime 归因）**
- `commands.json` 全文 grep `git ` → **零命中**；`setup_commands` 仅 5 条（freeze oracle / `build_manifest.py` ×2 / `make_diff.py` / `verify_manifest.py`），20 条 run argv 的 `--attempt/--out/cwd` 全部指向本 attempt 的 `evidence/<CARD>/<ARM>/` ⇒ **本卡证据内零 git 写命令、零产品路径写命令**。
- RF porcelain 现状24 行；7 个 ` M ` 的产品文件（`scripts/company_wiki_source.py`、`revenue_core.py`、`revenue_publication.py`、`revenue_report.py`、`source_preparation.py`、`tests/test_fc1105_fault_injection.py`、`tools/pre_push_gate.py`）LastWrite 最晚为 **2026-09-22 19:38:37**，**全部早于本 attempt 首次写盘（oracle.md 19:49:24）**；`.git/index` LastWrite = 19:37:17，亦早于该时点。`??` 项中属于本卡的只有 `execution_runs/M01-M04-PROPAGATE/` 本身。⇒ M 文件归 PROMOTION-EXEC / GATE-OQ 等他卡，与本卡「无产品写入」主张一致。

7.3 **无 git 写入** — 见 7.2（commands.json 零 git 命令）；本复审自己也未执行任何 git 写（仅一次只读 `git status --porcelain` 用于归因）。

7.4 **handoff 四态 + 哈希**：`b82734adb660ad0c4cc918c9a52a2b99775d5b9f857ad7f4394e863885775179` ✅ 复算一致；字段实读 = `status: "review_pending"`、`implementer_signed: false`、`disclosure_adaptation: "unmapped"`、`accuracy: "unproven"` ✅（未自签）。

7.5 **16 条 `deliverable_hashes` 全量复算 — 16/16 一致（域：`handoff.json.deliverable_hashes` 列出的全部键）**

| 交付物 | 复算 sha256 前12 | 匹配 |
|---|---|---|
| `oracle.md` | `9ff1dedec8f2` | ✅ |
| `binding.json` | `57791ef83b48` | ✅ |
| `decision.md` | `037b24b61409` | ✅ |
| `changes.diff` | `de038406681a` | ✅ |
| `commands.json` | `0df3af533fc5` | ✅ |
| `exit_code_legend.md` | `ffe8312beacb` | ✅ |
| `recovery/README.md` | `413e6cc4c404` | ✅ |
| `iso/run_card.py` | `f671732d4860` | ✅ |
| `iso/run_card_before.py` | `b5fcc68563f5` | ✅ |
| `before/run_card.py` | `b5fcc68563f5` | ✅ |
| `evidence/arms_raw.json` | `4f6d7f488abc` | ✅ |
| `evidence/arms_summary.json` | `a3af8ebd410d` | ✅ |
| `evidence/manifest_before.json` | `a03525360a8e` | ✅ |
| `evidence/manifest_after.json` | `a03525360a8e` | ✅ |
| `evidence/manifest_verification.json` | `77a2f6b38caa` | ✅ |
| `evidence/oracle_freeze.json` | `3db4abc7ecad` | ✅ |

（`handoff.binding.sha256 = 57791ef8…` 与 `binding.json` 实算一致 ✅。）

7.6 **其它 pin 复算（域：oracle §3 表全部8 项）**：`code_root/model_registry.py = 9ec65295…` ✅、`model_extensions.py = 9939480b…` ✅、解释器 `python.exe = 0e818a1f…` ✅、四批冻结 `cases.json` = M01 `462ea30c…` / M02 `b02423dd…` / M03 `62d5b69f…` / M04 `d515e1b7…` ✅（8/8 与声明一致）。

---

## Findings（编号）

**F-1（minor，文档/证据一致性）** — `evidence/arms_summary.json:412` 内嵌的 `manifest_verification.manifest_after_sha256 = 10d12ef4bcd063274b9303ff651df363b73c665d48ca02c04128a7c7c5f9ac66`，与权威件 `evidence/manifest_verification.json`（及 `manifest_final_verification.json`）记录的 `manifest_after_sha256 = a0352536…`、以及 `manifest_after.json` 的实算 sha（`a0352536…`）**互相矛盾**；也与 `decision.md:65`「两份清单 sha256 完全相同」矛盾（域：这4 处记载 vs 我对 `manifest_after.json` 的实算）。
*影响*：零漂移证明本身不受影响（两份清单文档实测逐字节相同、`manifest_final_recheck.json` 亦同值、验证件两份均 PASS）。属 `arms_summary.json` 内一份过期的派生快照。建议父代理在落定时一行更正（该文件哈希会变，需同步 `handoff.deliverable_hashes`），或在关闭登记行时把此矛盾显式记录为已知瑕疵。

**F-2（minor，无域全称句 / 事实不符）** — `decision.md:67`「全场零 `__pycache__`」与 `oracle.md:124`「任何位置无 `__pycache__`」为假：四个历史 attempt 现存 **292 个 `__pycache__` 目录 / 3492 个 `.pyc`**（历史 venv site-packages 自带，且全部在冻结基线清单内、零漂移）（域：`M01..M04/a20260919-01` 全树递归 vs `manifest_before.json` 的 3492 条 `.pyc` 条目）。
*影响*：操作性主张（本卡 `-B` + `PYTHONDONTWRITEBYTECODE=1` **未新增**任何 `.pyc`；本 attempt 目录 0 个 `__pycache__`；历史树零漂移）经我复测成立。这是 REM-79 型缺陷：全称句缺同域限定。建议措辞改为「零新增（域：本卡运行前后同一7722 条清单差集为空）+ attempt 内 0（域：本 attempt 全树）」。

**F-3（info，无缺陷记录）** — 两个 diff 的 added-line 差集（两个方向）除已文档化的 b5fcc685 家族适配与 rc 表散文外无第三类差异；`runner.diff` 侧唯一多出的代码行 `if not is_target:` 正对应本侧 `elif not is_target:`。此为**通过**的记录项，非缺陷。

---

## Unverified（我未验证 / 明确不主张）

1. **历史 G=KeyError 的现场重跑** — 未跑（历史只读纪律）；仅核对 B5-fix 的既有记录与 `exit_code_legend.md:23` 的文字。
2. **字面 `extra_unknown_id` S 变体在 b5fcc685 家族的行为** — 未跑、也未主张（卡方自己同样未跑；我只做了 source 核证明该家族无 id 闸门，故预期 rc=0 属推断而非实测）。
3. **臂 E/G/S/B 的我方独立重跑** — 我只按指示重跑了 **F 与 G 两条**（M02）；其余 18 条依赖卡方 `arms_raw.json` + 我对源码形态的静态核 + 20/20 元数据一致性检查，**未逐条重跑**。
4. **REM-80 登记行关闭、31/31 正式追认** — 按权威行归父代理复审之后；本报告不代裁、不关闭。
5. **REM-84 / START_HERE append-3** — 超范围（handoff `open_issues[3]`）。
6. **披露适配 / 准确性主张** — `disclosure_adaptation=unmapped`、`accuracy=unproven` 维持，本复审未验证也不外推。
7. **B5-fix 两轮原始测量记录本身**（`arm_matrix.json`、`M01-M04\evidence.json`）— 我只核对了 decision D-1/D-5 的引用文字，未重算 B5-fix 侧的原始证据文件。
8. **7722 文件的全量逐条现场重哈希** — 我做了清单文档比对（before/after/final_recheck 三时点逐字节相同）+ 3 条 spot 现场重哈希，**未**对 7722 条全部做现场重哈希（卡方 `verify_manifest.py` 声称做过 `live_rehash_*`，我未复跑该脚本）。

---

## 结论

**Verdict = `accepted_scoped`**，scope 限于：

1. **臂表证据（本卡 + 我的2 条 spot run）**：E=0 / F=3 / G=2 / S=1 / B=0 ×4 批，20/20 卡方记录 + 我方 F=3、G=2 独立复现（含 `FAIL_declared_expectation_mismatch` 与 `cases_json_declared_expectation_missing:NEG-CARD` 的逐字观测）。**REM-80 登记行关闭 = 父代理**，以本臂表为证据；**31/31 正式追认同样归父**。
2. **历史 rc/字节按设计保持零改动**：7722 文件 / 99,931,221 B，三时点清单逐字节相同、added=removed=changed=0（域：四个历史 attempt 的冻结清单范围）。
3. **臂 S 的家族适配已预登记（oracle §4，先于运行）且有 source 核依据（该家族无 `case_contract` id 闸门）**，字面变体未跑未主张。
4. **不接受为「已修」的部分**：F-1（`arms_summary.json` 内 `manifest_after_sha256=10d12ef4…` 与权威件矛盾）与 F-2（`decision.md`/`oracle.md` 的无域全称 `__pycache__` 句为假）作为 minor 文档缺陷随本接受一并交父代理处置（一行更正或显式记为已知瑕疵），**不阻断** gate 结论、臂表结论与零触碰结论。
5. 本报告未自签任何卡状态；`handoff.status` 维持 `review_pending`，`implementer_signed` 维持 `false`（域：本 attempt 的 `handoff.json` 四个状态字段）。
