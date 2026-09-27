# I-17-A / a20260926-01 独立复审报告（B 级轻审）

- **裁决行 VERDICT：`ACCEPT`（P1=0 · P2=1 · P3=4）** —— 本报告仅为复审产物，**未写卡状态**（卡仍 `review_pending`）。
- 复审角色：独立复审工位（父会话派单，2 次工位失败后接手复审）；只读回源，写入面 = 本目录 2 个新文件。
- 回源：被审 4 件（`oracle.md` 42 行骨架 · `requirement_register.json` · `verification.json` · `handoff.json`）+ `execution_v2/card_I-17-A.md`（11 行，L6-L9 四动作 + 退出逐字一致）+ 账本 7 件 + 日报 `assurance/runs/20260926T210002Z/report.json`。

## 签定清单（卡动作 1「由 reviewer 签定具体要求清单」）
签定 `requirement_register.requirements` 共 **7 条**为须保留要求：`D1-daily-7checks`、`D2-daily-alert-chain`、`W1-weekly-t3`、`W2-weekly-triplet-binding`、`M1-monthly-manifest`、`M2-legacy-periods`、`R1-release-gate`。其中 `R1`（`due=null`）仅登记 pending、**不得开始计时**，补齐 `due` 并经复审后方可计时。旧周期未盲目复活（daily/weekly/monthly 各以现有账本最新 run 为窗口起点），失败记录未删除（`W1` 保留 09-20 / 09-27 两次 `T3 suite exit 1`）。

## 四项轻核结果

### 1. 裁决行 + 发现清单
见上 VERDICT 行与下方 P 清单；`counts` 行与 7 条清单见 P3-2（语义混装，已披露）。

### 2. ⭐「7 daily」实证核 —— **通过**
- 日报 `report.json` 的 `checks` 为 **dict，len = 7**（实数：`triplet / policy_freshness / samples / scan_health / legacy_hits / latency / roots_fingerprint`）。
- 与登记 `daily_checks_verbatim` **逐字一致且同序**（7/7 完全匹配）。
- 「2 weekly」= `W1`（`weekly_manifest.json` 最新 `20260927T033001Z ok=false` + `weekly_alert.jsonl` 4 条）+ `W2`（triplet binding，manifest 内 filing/revenue/wiki 三 sha 均在）→ **解释合理**；`monthly M1+M2(+R1)` 与 `monthly_manifest.json` / `legacy_periods.json` / `ledger.release_gate` 对应成立。

### 3. F1 字段抽验（D1 · W1 · M2，另全量扫 7 条）—— **通过，无 P1**
| 项 | start | due | timezone | frequency | interruption_allowed | recovery_rule | status | 判 |
|---|---|---|---|---|---|---|---|---|
| D1 | 有 | 有（09-27T21:00Z） | 有 | 有 | true | 有 | in_progress | 七字段齐、due 存在 ⇒ 计时合规 |
| W1 | 有 | 有（10-04T03:31Z） | 有 | 有 | true | 有 | pending | 失败窗口保留、按 recovery_rule 重启，未标完成 |
| M2 | 有 | 有（10-06T21:00Z） | 有 | 有 | true | 有 | pending | 备注称 missing due 与实值矛盾（见 P3-3），但**未标 in_progress** ⇒ 硬判据过 |
- 关键项：**`due` 缺失者未标 `in_progress`** —— 全 7 条中仅 `R1 due=null`，其 `status=pending` ✅；4 条 `in_progress`（D1/D2/W2/M1）`due` 均存在 ✅。**无「F1 字段被跳过却标 in_progress」**。

### 4. 来源 sha 自算 —— **7/7 一致**
自算 sha256 前 16 位（bytes）vs `verification.source_shas` = `requirement_register.ledger_sources`（两处登记完全相同）：

| 文件 | 自算 | 登记 | bytes |
|---|---|---|---|
| daily_manifest.json | `130f120afbef999c` | 同 | 457 ✅ |
| weekly_manifest.json | `d45445baafb3dd2f` | 同 | 364 ✅ |
| monthly_manifest.json | `703f45844030f14e` | 同 | 349 ✅ |
| legacy_periods.json | `58cd90d3f9abcf9c` | 同 | 1078 ✅ |
| ledger.json | `f4bea6bd4ce692c9` | 同 | 1302 ✅ |
| daily_alert.jsonl | `7bfec4c407ab1a5d` | 同 | 603 ✅ |
| weekly_alert.jsonl | `5d40aaa83961136f` | 同 | 607 ✅ |

另：`oracle.md` 自算 `2f75858de4c5c7c1…` = `handoff.oracle_sha256` ✅。**无伪造**。

### 5. 变异复核（只读，未复跑写盘）—— **与期望吻合**
`verification.checks`：`green_no_missing_required_fields rc=0 violations=[]`；`M1_missing_due_must_not_time rc=3`；`M2_missing_recovery_rule_rejected rc=3`；`M3_failure_not_deleted_nor_spliced rc=0` → **三臂 rc = 3/3/0，符合期望**；`red_green={green_rc:0, red_arms:3, all_match:true}` 自洽。红臂违规列表（M1 列 4 条 due-missing、M2 列 7 条 recovery_rule）对应的是**注入变异态**——正式 register 中这些项 `due`/`recovery_rule` 均存在（§3 已核），故按合成变异理解；rc 语义与变异输入留档问题见 `unverified`。

## P 清单
- **P1：0 项。** 来源 sha 无伪造；无「缺字段却 in_progress」；周失败（09-13/09-20/09-27 not-ok + 09-06 blocked）4 条 alert 与 `weekly_manifest.ok=false` 原样保留、register W1 如实登记，**未删改拼接**；`tasks_installed=0`（handoff/verification 双处声明，未见安装痕迹）。
- **P2（1 项）**
  - P2-1：`handoff.implementation_note` 如实披露「2 次工位失败后父接手」——按指示**判 P2（不判 P1）**；连带 `handoff.gate0 = "n/a - parent execution"`，即 oracle §3 写/回读/删自探**从未执行**，属真实证据缺口（披露诚实，但门 0 证据缺失）。
- **P3（4 项）**
  - P3-1：`oracle.md` 仍为工位骨架 **SKELETON、未补 FROZEN**：`_SHA_CARD_/_SHA_OWNERDEC_/_SHA_DR_/_SHA_VER_/_SHA_HO_/_SHA_WM_/_SHA_WA_/_SHA_EXTRA_`、`_GATE0_PENDING_`、`_MUT_PENDING_`、`_TIME_PENDING_` 占位全部未填（sha 实值仅存在于 verification/handoff）。
  - P3-2：`counts` 语义混装：`daily=7` 数的是日报 checks 项数而非需求条数，`total=7` 数的是需求条数；`monthly_or_legacy=3` 已含 R1 又被 `release=1` 重复计（7+2+3+1≠7）。`note_on_counts` 已如实披露口径 → P3。
  - P3-3：字段与备注自相矛盾：`M2` 备注称 "missing due field" 但实有 `due=2026-10-06T21:00:28Z`；`R1` 备注称 `fields_complete=false` 但字段值为 `true`（二者状态均为 pending，未触发 F1 硬伤）。
  - P3-4：版本一致性差异未登记：日报 `20260926T210002Z` 的 `wiki=bf0c8b27…` 与 weekly `20260927T033001Z` 的 `wiki=dbe47450…` 7 小时内不一致（filing/revenue 稳定），register 未记录该观察，而卡 L8 明确要求覆盖「版本一致性」。
- 观察项（不计级）：`W1 status=pending` 而 due（10-04）未到，按 F3 本可 `in_progress`；现按失败重启窗口保守挂 pending，方向安全，登记备查。

## `unverified`（未核 / 无法只读复现）
1. 变异三臂**未复跑**（遵只读纪律）：`rc` 疑为固定「检出码」而非违规计数（M1 列 4 条、M2 列 7 条却同为 rc=3）；变异输入副本/脚本未留档，只读条件下无法独立复现。
2. `gate0` 写/回读/删自探未执行（披露为 n/a），oracle §3/§4/§5 三段始终 `_PENDING_`。
3. `tasks_installed=0` 为声明值，未枚举系统级计划任务/cron 交叉验证；未跑 `git status`（禁令）。
4. `OWNER_DECISIONS.md` §三十八/§三十九 原文与其 sha 未核（不在 V2-4 回源清单内，oracle 亦为占位）。
5. 「2 weekly」中 W1 每轮真实时长/内容是否达退出判据（需跨自然周观察）未核。

## 没做的事
未改被审 4 件与任何账本（收尾复哈希：`oracle 2f75858d…` / `register 0ccebdda…` / `verification 19cf188b…` / `handoff 94b325a1…`，7 账本 sha16 与上表逐一相同，**均未变动**）；未写卡状态；未装任务、未重启周期；未跑变异；未用 `git status`、未做任何 git 写；未联网；未在本目录外写任何文件。
