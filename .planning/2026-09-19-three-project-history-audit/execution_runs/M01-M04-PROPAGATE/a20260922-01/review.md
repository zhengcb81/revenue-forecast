# review.md — M01-M04-PROPAGATE（carrier 落地转录；非新裁决）

## Verdict block

- **Verdict**: **`accepted_scoped`**（复审报告 L5 与 L243；scope 四条 + 不接受为「已修」的 F-1/F-2 随接受一并交父处置，见下）
- **Carrier（父代理）**: `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- **Reviewer 文件 + pin（本次落地独立复算）**: `execution_runs/M01-M04-PROPAGATE/a20260922-01/reviewer_report.md`
  - bytes = **24604**（与声明一致）
  - sha256 = `3217a506e53dfcc876949a34eec71258458021f8e58fa953de63308b6bd703f6`（本次独立 `Get-FileHash` 复算；sidecar `reviewer_report.sha256` 存在且内容 = 同值 `…308b6bd703f6  reviewer_report.md`，与复算逐字符一致）
  - verdict 行 = L5；findings 段 = L216–224；结论/scope 段 = L243–249
- **Reviewer = 独立复核**（报告自述工具集 read / grep / pwsh，无 git 写；四历史 attempt 与生产仓只读；两次 spot run 只写 `%TEMP%\rev-m01m04-spot\`；本卡目录内 reviewer 只新增 `reviewer_report.md` + `reviewer_report.sha256`；不自签）
- **bookkeeping transcription adds no acceptance of its own** — 本文件只是对 `reviewer_report.md` 的转录（transcribe in substance）+ 两项 minor 修正的落地记录；`handoff.status` 从 `review_pending` → `accepted_scoped` 的权威是 reviewer 报告本身，本转录不产生任何新的接受、不关闭任何登记行、不代裁 REM-80/31-31。

---

## 1. 权威行已验证（实读，非转述）

- `OWNER_DECISIONS.md:424` 原话（§十八【已裁定·第四批】）：
  > | **A-1 = 1（①扩权）** | REM-21/T1-8 同形态门传播**扩到 M01–M04 四批**（修在副本、before/ 留旧、历史 rc 零回改、证据齐全） | 卡 `M01-M04-PROPAGATE` 已派（subagent 08e56200）；预期臂 **E=0/F=3/G=2/S=1**；登记行关闭待其复审后 |
- 登记行 `REMEDIATION_REGISTER.md:869` 同文：
  > `| M01-M04-PROPAGATE（08e56200） | A-1=①扩权 | 同四前置形态；预期臂 E=0/F=3/G=2/S=1；历史 runner/rc 零回改 |`
- ⇒ 判据 = 四前置（副本修复 / before 留旧 / 历史 rc 零回改 / 证据齐全）+ 臂表 E=0/F=3/G=2/S=1（B 臂为契约内惰性对照，非 owner 臂表项）。

## 2. Source identity — PASS

- **8/8 历史 runner 复算一致**（域：`M01..M04\a20260919-01` 下全部 `run_card*.py`）：全部 `b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816` / **12222 B**（`scripts\run_card.py` + 各 `recovery\r2_exit_code_selfcheck\run_card.py`，四批各二）。
- **两个差集方向都为空**：`new \ old = ∅`、`old \ new = ∅`（域：上述 8 条路径 vs 声明的单哈希单字节数）——8 条全部等于声明值，无一条落在声明之外。
- **无 id 闸门 source-verified**：`before\run_card.py` grep `extra_unknown_id|case_contract|allowed_ids|id 白名单|__name__ == declared` → 零命中（域：该 12222 B 文件全文）；唯一相关硬下标是 L193 `"expected": case["expected"]`。
- ⇒ 该家族确无 case_contract id 闸门、确无逐例声明门 → **arm-S 家族适配理由成立**（字面 `extra_unknown_id` 变异在本家族不构成结构故障）。
- 定位声明成立：`execution_runs\M01-M04\` → `Test-Path = False`；M01–M04 确为四个独立卡 attempt。

## 3. Freeze-first — PASS

| 对象 | CreationTime |
|---|---|
| `oracle.md`（sha `9ff1dedec8f2687298f6d083418558e16f85db5c247cb8c2213d2e6327dae0f4`，12579 B，复算一致） | **2026-09-22 19:49:24.524** |
| `evidence/oracle_freeze.json`（`oracle_sha256=9ff1dede…`、`bytes=12579`、`mtime_utc=2026-09-22T18:49:24.528Z`） | 2026-09-22 19:49:50.874 |
| 最早臂输出（域：`evidence/**` 下 136 个 `run.json|out.json|stdout.txt|stderr.txt|rc.txt` 按 CreationTime 排序第 1） | 2026-09-22 19:53:40.619 |

⇒ **oracle 19:49:24.524 < freeze 记录 < 最早臂输出**，oracle 严格早于最早臂输出 **256,095 ms ≈ +256 秒（约 4 分 16 秒）**；freeze 记录亦早 ≈230 秒。**先冻结后运行成立**（域：本 attempt 136 个臂输出文件 vs oracle.md）。

## 4. Arm results — PASS（含 reviewer 两次全新 spot run）

- 臂表（raw rc，四批逐格）：**E=0 / F=3 / G=2 / S=1 / B=0 ×4**，与冻结预期逐格相同；**20/20 `meets_expectation=true`**（域：`arms_raw.json` 20 条记录）；`arms_summary.json`：`all_arms_meet_frozen_expectation=true`、**深度断言 60/60**。
  - F 臂 4/4 `FAIL_declared_expectation_mismatch` on `NEG-CARD`、`raised=ModelRegistryError` vs `declared='ValueError'`、comparison 串含 `(exact type name; NOT isinstance)`。
  - G 臂 4/4 `verdict=no_verdict`、`no_verdict_reason=cases_json_declared_expectation_missing:NEG-CARD`、`missing_count=1`、`mismatch_count=0`、`not_judged=[NEG-CARD]`。
  - S 臂 4/4 未捕获 `KeyError: 'kind'`、不写 out.json、rc=1；B 臂 4/4 rc=0（伪造绿在本 attempt 复测，旧 runner 输出无任何 enforcement 字段）。
- 交付物复算：`arms_raw.json` = `4f6d7f488abcfd5a75a58e8108b71b54b0da9fe976061f91d60998dc720364f3` ✅；`arms_summary.json` 复审时 = `a3af8ebd410d…`（**本次落地 F-1 修正后已变**，见 §8）。
- **Reviewer 的两次全新 spot run**（独立子进程，argv 形状 `<py> -X utf8 -B <iso/run_card.py> --card M02 --attempt <TEMP>\{F|G} --code-root <iso/code_root> --out <TEMP>\{F|G}\out.json`，`cwd=<TEMP>\{F|G}`，`PYTHONDONTWRITEBYTECODE=1`）：
  - **F → rc=3** ✅：`verdict=fail`、`exit_code_in_doc=3`、NEG-CARD 判 `FAIL_declared_expectation_mismatch`、`declared='ValueError'` / `raised='ModelRegistryError'`、`declared_expectation_mismatch_case_ids=["NEG-CARD"]`。
  - **G → rc=2** ✅：`verdict=no_verdict`、`no_verdict_reason=cases_json_declared_expectation_missing:NEG-CARD`、`declaration_unusable_case_ids=["NEG-CARD"]`、`missing=1`、`mismatch=0`。
  - reviewer 自建断言 **10/10 PASS**（落盘 `%TEMP%\rev-m01m04-spot\spot_results.json`）；**全部输出只进 %TEMP%**（域：spot 脚本输出路径 + argv 的 `--attempt/--out/cwd` 三项均指向 `%TEMP%`）→ 历史 attempt 在两次跑中零写入。

## 5. Historical zero-touch — PASS

- **清单/验证件复算**：`manifest_before.json` = `manifest_after.json` = `manifest_final_recheck.json` = **`a03525360a8e8911399114223a28ab4ce9d5464e2d5ecca9cd59adedf9f02751`**（三份 raw 逐字节相同，本次落地再次独立复算确认）；`manifest_verification.json` = `manifest_final_verification.json` = **`77a2f6b38caaba368df647abbd167f9a38827fe494f9552365fd3c918f8618a1`**。
- **规模/漂移**：`file_count=7722`（实际条目数 7722）、`total_bytes=99931221`；`result=PASS`、`files_identical=7722`、`added=[] removed=[] changed=[]`、`zero_byte_drift=true`、`manifest_docs_byte_identical=true`、`live_rehash_matches_before/after=true`（added=removed=changed=0，域：7722 条清单条目 vs 两份文档 + 现场重哈希声明）。
- **三文件现场 spot 重哈希（跨三个历史批次）全中**：runner `M01/…/scripts/run_card.py` = `b5fcc685…`/12222 B；evidence json `M04/…/evidence/M04/cases.json` = `d515e1b7…`/3184 B；**rc 载体** `M03/…/evidence/M03/run_result.json` = `74823d46…`/27055 B。
- **rc 载体说明**：历史四批 evidence 树内**无 `rc.txt`**；rc 载体 = `run_result.json`（域：`M01..M04/a20260919-01/evidence/**` 文件名扫描）。

## 6. Patch provenance — PASS

- **哈希/度量复算**：`changes.diff` = `de038406…`，**+149/−21**；镜像 `B5-fix-g1a-g3\a20260922-01\M05-M08\runner.diff` = `8263fc83…`/10431 B，+111/−12；`B5-fix …\M05-M08\run_card.py` = `489ba7e3…`/20804 B 且与 `B5-plan-level-remediation\a20260921-01\M05-M08\run_card.py` **逐字节相同**；`iso\run_card.py` = `f671732d…`；`before\run_card.py` 与 `iso\run_card_before.py` 均 = `b5fcc685…`/12222 B。
- **行数自洽**：**271 − 21 + 149 = 399** == `iso/run_card.py` 实际行数 ✅。
- **两个 diff 的 added-line 双向差集比对**（域：两文件 `+` 集，逐行、去头、去空行）：`only-in-changes.diff=47`、`only-in-runner.diff=10`；`only-in-runner.diff` 唯一**代码**行 = `if not is_target:`，本侧对应 `if is_import_or_file and not is_target:` / `elif not is_target:` —— 正是**已文档化的 b5fcc685 家族适配**；其余差异全为 rc 表/docstring 散文与标题行 —— **无第三类语义差异**；hunk 头各 7 个 `@@`，两侧插入点族群一一对应。
- **门形态（逐行引用 `iso\run_card.py`）**：
  - 精确类型名比较 **==compare L281** `declared_ok = (entry["raised"] == declared)  # exact type-name equality`（全文件 7 处 `isinstance` 无一处比较声明与实抛）；
  - **声明前置 L132-140 → L361**（任何 case 循环前算出 `unusable_declared`/`cases_declared_ok`/`no_verdict_reason`；L361 unusable ⇒ `no_verdict` + rc=2）；
  - **mismatch → rc3：L294** `FAIL_declared_expectation_mismatch` + **L367-369** else 分支 `verdict="fail"; exit_code=3`；
  - **NOT_JUDGED L269-279**（`judged=False`、`verdict="NOT_JUDGED_declaration_unusable"`、L273 `declared_expectation_mismatch` 显式置 False）；
  - **`negatives_ok` 仅 judged（L357-358）** ⇒ NOT_JUDGED 单独不可能产生 rc=3；
  - **`exit_code_semantics` L371-391** 全字段在册（harness_incomplete / positive_ok / continuity_ok / negatives_ok / verdict / exit_code / usable / mismatch ids / not-met ids / unusable ids / reason_namespace）；
  - **`case.get` L243**（删键可存活 → G 臂走声明前置）+ **硬下标 `case["kind"]` L244 在 try 之外** ⇒ S 臂 `KeyError: 'kind'` 未捕获 → rc=1（与 4 份 S stderr 一致）；
  - 既有标签一个不删：`PASS_rejected`(L296)、`FAIL_wrong_exception_type`(L292)、`FAIL_not_rejected`(L259)、`FAIL_import_or_file_error`(L290)。

## 7. 三项已披露的不主张 — 全部在册；边界

- **(i) arm-S 家族适配**：预登记于 `oracle.md:98-106`（§4，先于运行）+ `oracle.md:143`（§7.4）再钉；source 核（本复核独立 grep，零命中）支撑；实测形态 = 恰一个缺 `kind` 例 → rc=1 ×4；**字面变体未跑/未主张**（decision D-4 + handoff `open_issues[0]` + oracle §7.4 三处）。
- **(ii) B rc=0 = 实测值；历史 G=KeyError 未重跑**：`exit_code_legend.md:21-24` + handoff `open_issues[1]` + decision D-5（历史形态 E=0/F=0/B=0/G=1，B5-fix 两轮）三处一致 ✅。
- **(iii) REM-80 关闭 / 31-31 追认归父；REM-84 超范围**：`oracle.md:142`、`decision.md:74`、handoff `open_issues[2]` ✅；`decision.md:60`「27/31 ⇒ 31/31 形态达成，**正式追认仍待复审+父关 REM-80**」措辞未越界 ✅；handoff `open_issues[3]` ✅。
- **边界**：
  - **0 git 写命令**：`commands.json` 全文 grep `git ` 零命中；`setup_commands` 仅 5 条（freeze / build_manifest ×2 / make_diff / verify_manifest），20 条 run argv 的 `--attempt/--out/cwd` 全指本 attempt `evidence/<CARD>/<ARM>/` ⇒ 本卡证据内零 git 写、零产品路径写。
  - **产品 M 文件全部早于本 attempt 首次写盘**：RF porcelain 7 个 ` M ` 文件 LastWrite 最晚 2026-09-22 19:38:37，**`.git/index` LastWrite = 19:37:17 < oracle.md 19:49:24** ⇒ M 文件归他卡（PROMOTION-EXEC / GATE-OQ 等）。
  - **16/16 `deliverable_hashes` 全量复算一致**（oracle/binding/decision/changes/commands/legend/README/iso×2/before/arms_raw/arms_summary/manifest_before/after/verification/oracle_freeze；`handoff.binding.sha256=57791ef8…` 与 `binding.json` 实算一致）；handoff 自身 sha `b82734adb660…` 复算一致（复审时点）。
  - **8/8 oracle §3 pins**：`model_registry.py=9ec65295…`、`model_extensions.py=9939480b…`、解释器 `python.exe=0e818a1f…`、四批冻结 `cases.json` = `462ea30c…`/`b02423dd…`/`62d5b69f…`/`d515e1b7…` 全中。
  - 复审时 `handoff.status=review_pending`、`implementer_signed=false`、`disclosure_adaptation=unmapped`、`accuracy=unproven`（未自签）。

## 8. F-1 — corrected during landing（本 carrier 落地执行）

- **发现**：`evidence/arms_summary.json` 内嵌 `manifest_verification.manifest_after_sha256 = 10d12ef4bcd063274b9303ff651df363b73c665d48ca02c04128a7c7c5f9ac66`，与权威件 `manifest_verification.json` / `manifest_final_verification.json` 记录的 `a0352536…`、`manifest_after.json` 实算 sha、`decision.md:65`「两份清单 sha256 完全相同」互相矛盾（域：这 4 处记载 vs `manifest_after.json` 实算）。零漂移证明本身不受影响。
- **落地修正（在写 handoff/review 之前执行，故本文件携带修正后哈希）**：`manifest_after_sha256` **就地更正为权威值 `a03525360a8e8911399114223a28ab4ce9d5464e2d5ecca9cd59adedf9f02751`**；新增同级键 `manifest_after_sha256__stale_derived_value = 10d12ef4…`（旧值原样留存）；新增 `f1_correction_note` = "stale derived snapshot inside deliverable, corrected during carrier landing per reviewer F-1; authoritative zero-drift proof unchanged (manifest_verification 77a2f6b3…)"。
- **哈希**：`evidence/arms_summary.json` **before `a3af8ebd410d5e194473115228b2bf9f971d49847fad15490052d69e767236bb` → after `69743d73916b3e22a01d076e0ea0a8047cd78ab4f1f022c3965a1bac8633f169`**；修正后文件 JSON 复解析 = OK，`deep_checks 60/60`、`all_arms_meet_frozen_expectation=true` 不变。已同步 `handoff.deliverable_hashes`。

## 9. F-2 — scoped during landing（decision.md 就地改；oracle.md 冻结不动）

- **发现**：`decision.md:67`「全场零 `__pycache__`」与 `oracle.md:124`「任何位置无 `__pycache__`」为**无域全称句且为假**——四历史 attempt 现存 **292 个 `__pycache__` 目录 / 3492 个 `.pyc`**（历史 venv site-packages 自带；`manifest_before.json` 内 `.pyc` 条目 = 3492，且 before/after 逐字节相同 ⇒ 基线既有、零漂移）；本卡 attempt 目录内 `__pycache__` = **0**。操作性主张（`-B` + `PYTHONDONTWRITEBYTECODE=1` 零新增、历史树零漂移）经复测成立。
- **落地修正（decision.md 就地）**：原句替换为限定形式 —— 「`__pycache__`/`.pyc`：四历史 attempt 内既有 292 目录/3492 pyc（全在冻结基线清单内，两向 diff=0=零漂移）；**本卡零新增**（域=7722 条清单）；本 attempt 目录内 0」，并在 `（原句留存：…）` 内**逐字保留原句**（见 `decision.md:67`）。
- **`oracle.md` 保持字节未动（冻结）**：sha256 复算仍 = `9ff1dedec8f2687298f6d083418558e16f85db5c247cb8c2213d2e6327dae0f4`、12579 B，与冻结记录一致；其 L124 全称句**不改字节**，改由本文件 + `handoff.bookkeeping` 的限定重述承担（见 §11）。
- **哈希**：`decision.md` **before `037b24b61409cb725c9afa08c10e29736add64b9f440c6aa2733f57c8644cd2a` → after `18dfc2dacb665650307ea2db75bde57f82d1289e9d50597f7ac81884cea761f2`**；已同步 `handoff.deliverable_hashes`。

## 10. F-3 — pass（无缺陷记录项）

两个 diff 的 added-line 差集（两个方向）除已文档化的 b5fcc685 家族适配与 rc 表散文外无第三类差异；`runner.diff` 侧唯一多出的代码行 `if not is_target:` 正对应本侧 `elif not is_target:`。**通过**的记录项，非缺陷。

## 11. Unverified 清单（原样携带，不主张）

1. 历史 G=KeyError 未现场重跑（历史只读纪律；仅核对 B5-fix 既有记录 + `exit_code_legend.md:23` 文字）。
2. 字面 `extra_unknown_id` S 变体在 b5fcc685 家族的行为未跑、未主张（预期 rc=0 属推断而非实测）。
3. reviewer 只独立重跑了 F 与 G 两条（M02）；其余 18 条依赖卡方 `arms_raw.json` + 静态源码核 + 20/20 元数据一致性，未逐条重跑。
4. REM-80 登记行关闭、31/31 正式追认归父代理复审之后；本文件不代裁、不关闭。
5. REM-84 / START_HERE append-3 超范围（handoff `open_issues[3]`）。
6. `disclosure_adaptation=unmapped`、`accuracy=unproven` 维持，未验证也不外推。
7. B5-fix 两轮原始测量记录（`arm_matrix.json`、`M01-M04\evidence.json`）只核对引用文字，未重算原始证据文件。
8. 7722 文件未逐条现场全量重哈希（做了三时点清单逐字节比对 + 3 条 spot 现场重哈希；未复跑 `verify_manifest.py`）。

**oracle L124 全称句的限定重述（域=冻结基线清单）**：zero-new-`__pycache__` (domain: 7722-entry manifest, both diff directions empty) + 0 in attempt dir; oracle frozen, universal scoped here —— 与 `decision.md:67` 限定句一致；`oracle.md` 本体字节不动。

## 12. 验收 scope（转录 reviewer 结论 L243-249）

1. **臂表证据（本卡 20 条 + reviewer 2 条 spot run）**：E=0/F=3/G=2/S=1/B=0 ×4、20/20 + 60/60 + F=3/G=2 独立复现；**REM-80 登记行关闭 = 父代理**（以本臂表为证据）；**31/31 正式追认同样归父**。
2. **历史 rc/字节按设计保持零改动**：7722 文件 / 99,931,221 B，三时点清单逐字节相同、added=removed=changed=0（域：四历史 attempt 冻结清单范围）。
3. **arm-S 家族适配已预登记（oracle §4，先于运行）且有 source 核依据**，字面变体未跑未主张。
4. **F-1 / F-2 已于本次落地处置**（§8/§9，非阻断项，复审已明示不阻断 gate/臂表/零触碰结论）；F-3 = pass。
5. 本卡未自签任何状态：`implementer_signed` 维持 `false`；状态推进的权威 = `reviewer_report.md`（sha `3217a506…`）；本 `review.md` 是转录，**bookkeeping transcription adds no acceptance of its own**。
