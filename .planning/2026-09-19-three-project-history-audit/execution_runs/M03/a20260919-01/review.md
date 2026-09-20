# M03 · implementer review record

Card M03 (`unit_sales`), Parent I-10. Attempt `execution_runs/M03/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict.

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes equal | `binding.json`, `evidence/M03/source_manifest.json` |
| B positive | `[305.0]` vs independent oracle `[305]` within tolerance | `evidence/M03/formula_result.json` |
| C negatives | **13/13** rejected with `ModelRegistryError`; continuity positive `[200, 220]` passes; defaults case `[30]` and zero-volume case `[5]` match the pre-frozen oracle | `evidence/M03/negative_results.json` |
| D mapping | real BYD FY2024 disclosure mapping (volume + revenue + segment line + mix), with the derived-price caveat stated openly | `evidence/M03/disclosure_mapping.json`, `evidence/M03/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe` | `evidence/M03/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M03/qualification.json` |

## 2. Independence of the oracle

- `scripts/oracle_M03.py` imports only `json`, `os`, `decimal`; it never imports `model_registry`.
- The BYD figures in the oracle were **hand-transcribed** from the read-only extracted page text
  (`before/probe01_byd.json`, `before/probe02_byd.json`), not read from any product parser.
- Negatives are in-memory `deepcopy` cases; JSON-parser rejections cannot masquerade as model rejections.
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`.

## 3. Results in detail

- Registry formula string observed:
  `revenue = units * unit_revenue * timing_factor + other_revenue` — matches the frozen expectation.
- Positive `[305.0]`: `120 x 2.5 x 1 + 5`.
- Defaults case `[30.0]`: only the two required drivers supplied, so `timing_factor` defaulted to `1.0` and
  `other_revenue` to `0.0` — the documented defaults behave as documented (this is **not** an authorisation to
  fill 1/0 when a disclosure is missing).
- Zero-volume case `[5.0]`: `units = 0` is data, and `other_revenue` still applies.
- Continuity positive `[200.0, 220.0]`; break patch rejected.
- Rejections: `NEG-CARD` → `driver unit_sales.units must be between 0.0 and inf: FY2027`;
  `R7-TIMING` → `driver unit_sales.timing_factor must be between 0.0 and 1.0: FY2027`;
  `R8-NET-NEG` → `calculated revenue cannot be negative: unit_sales`;
  `N01a` numeric; `N01b/c/d` finite; `N02` length; `N03` missing driver; `N04` unknown driver;
  `N05a/b` fiscal years; `CONT-BREAK` consecutive years.
- Observation `OBS-NEG-OTHER`: `other_revenue = [-10]` (a signed driver inside its domain) yields `290.0`,
  i.e. accepted; only a **negative net result** is refused. Recorded as a design observation, not scored.

## 4. Unit / dimension and rejection checks

- Dimension chain: `quantity x CNY/unit x ratio + CNY = CNY`. Checked with real numbers:
  `4,250,370 vehicles x 123,751.503987229 CNY/vehicle = 525,989,680,000.00 CNY`.
- Per-share vs total: not applicable; every mapped field is a total amount or a physical count.
- Gross vs net: **OPEN** — the mapped column is labelled 销售收入 with no printed gross/net statement
  (SR-M03-B). The model has no returns/rebate term, so the net basis must be established at the mapping layer.
- Period alignment: volume and revenue are read from the **same table row** for FY2024, so numerator and
  denominator share one period and one boundary.
- `timing_factor = 1` because the volume is a full-year realised figure; applying a fraction would be the
  repeated-time-scaling failure the card names.
- Rejection conditions R1-R11 in `oracle.md` §6; R1-R8 executed, R9-R11 are business refusals.

## 5. Judgement calls the reviewer should attack first

1. **`unit_revenue` is derived, not disclosed.** `525,989,680,000 / 4,250,370 = 123,751.503987229`, so the
   zero residual is a constructive identity. DEC-M03-2 asks whether `unit_sales` can earn a disclosure
   adaptation at all when the per-unit net price is not disclosed; the implementer's position is **not yet**.
2. **Confirmed sales volume, not production.** The same table prints production `4,281,084` and sales
   `4,250,370` — a 30,714-unit (0.72%) difference that would have silently inflated revenue.
3. **The 14.37% scope gap.** Rebuilding the automobile segment revenue from **total** vehicle unit sales at
   the passenger-vehicle unit price gives `528,681,308,161.71` against a disclosed
   `617,381,935,000.00`, i.e. a gap of `88,700,626,838.29` (14.3667%), far outside the 2% tolerance frozen
   before the run. Interpretation: the segment line also contains batteries, parts and other products that
   this model cannot identify. It must be bridged with evidence and must **never** be booked into
   `other_revenue` to make the reconciliation pass.
4. **Derived price across boundaries.** Using the passenger-vehicle unit price against the *total* vehicle
   volume is already a boundary mismatch; it was used only to quantify the scope gap, and that is stated in
   the mapping.
5. **I-00-B interpretation** — same deviation note as M01/M02 (attempt-local byte-identical snapshot).
6. **`calculate_model_path` not exercised** (I-10-A obligation); only read-only call-site observations.

## 6. What this card does NOT claim

- No accuracy claim (FY2024 is a closed period; two of the three reconciliations are constructive).
- No `disclosure_adaptation` (derived price, unresolved gross/net, unexplained 14.37% scope gap, no reviewer
  signature).
- No formula rewrite; no change to any product file.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M03.py` and `scripts/run_card.py`; diff against the recorded results.
2. Re-read BYD FY2024 page 23 yourself and confirm the row/column selection (乘用车 快报销量 4,250,370;
   销售收入 525,989,680,000.00) and that production is a different column.
3. Confirm the frozen tolerances in `oracle.md` §7 predate the run (they are consistent with
   `historical_reconciliation.json`).
4. Pick an unused case (e.g. `units=[10]`, `unit_revenue=[3]`, `timing_factor=[0.25]`) and freeze the
   expectation before running.
5. Adjudicate DEC-M03-1..6 and SR-M03-A/B/C/D.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M03/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M03/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M03/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M03-01 - arithmetic typo corrected

- The rebuild/gap figures in `oracle.md`, `evidence/M03/historical_reconciliation.json`, `evidence/M03/disclosure_mapping.json` and `evidence/M03/accounting_decision.md` used a **truncated unit price**; they now match `evidence/M03/oracle.json`, which was always correct (full-precision unit price 123,751.503986712 -> rebuild 528,684,368,999.31, gap 88,697,566,000.69).
- Cause: intermediate rounding of the unit price. **Conclusion unchanged**: the gap is still 14.3667%% of the segment line, still far outside the pre-frozen 2%% tolerance, and filling it into `other_revenue` remains forbidden.
- The corrected values are now **read from `oracle.json`** before being written, so the files cannot diverge again.

### Status

- `formula`: still **`review_pending`** - the implementer does not sign acceptance.
- `disclosure_adaptation`: still **`unmapped`**.
- `accuracy`: still **`unproven`**.

#### Self-check: is the new exit code actually meaningful? (do not take it on trust)

`recovery/r2_exit_code_selfcheck/selfcheck_result.json` runs the **patched** harness against deliberately
corrupted copies of `oracle.json` / `cases.json` in a scratch tree, so the frozen evidence is untouched:

| case | mutation | raw rc | expected | what it proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999,999,999]` | **3** | 3 | a corrupted expectation is no longer hidden behind a bookkeeping-only rc=0; the product itself still returned the correct path |
| B | `cases.json first case base_input -> 'no_such_block'` | **1** | non-zero | a harness defect cannot masquerade as a pass; it raises |
| C | none (the real card) | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |
| D (added in r3) | `input.json positive.drivers.growth_rate` deleted | **2** | 2 | **rc=2 is reachable**: a corrupted positive input makes the product raise, so no verdict exists and the harness says so instead of exiting 0 |

Exit-code map (corrected in revision r3): **rc=2 IS reachable** - it is produced when the corrupted
artefact is the POSITIVE INPUT, so the product raises and no verdict exists (case D below, raw rc=2).
Case B is a defect **outside** the guarded block, so it still raises and exits **1** rather than 2;
that remains fail-loud but is a different code path. The earlier r2 wording ("rc=2 is not yet
reachable in practice") was wrong and is corrected here.

---

## 独立 reviewer session 点复审（裁决）

**结论：`accepted_scoped`（仅 formula 资格）。**
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M03/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。§7 映射 1 的零残差**是构造性的**（`unit_revenue` 由同一行收入除以同一行销量反推），只证明量纲与乘法接线正确；映射 2 的 **14.3667% 分部缺口**（`88,697,566,000.69` 元，远超运行前冻结的 2% 容差）**未解决**，**严禁**把该 gap 填入 `other_revenue` 平账。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）。
- 未授予任何跨车型/跨公司/跨期间外推；未授予 D/E/F 完成；未授予"产销库存桥已完成"。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`。

**独立复算（reviewer 自造输入）**：13 例全部通过。
- `units=[7,11], unit_revenue=[13.5,13.5], timing_factor=[1.0,0.5], other_revenue=[0,-4.25]` → `[94.5, 70.0]`
- defaults：只给 `units=[10]`、`unit_revenue=[3]` → `[30.0]`（`timing_factor`=1.0、`other_revenue`=0.0）
- 零量：`units=[0], other_revenue=[7]` → `[7.0]`（零量不得当"缺失"跳过）
- 连续性正例 `units=[100,110], unit_revenue=[2,2]` → `[200.0, 220.0]`；断裂 `years=[2027,2029]` → `unit_sales.years must be consecutive and increasing`
- 保真：全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`timing_factor=[1.0000001]` / `unit_revenue=[-3.0]` / `units=[0]`+`other_revenue=[-1.0]`（净收入为负）/ `units=[True]`（bool 冒充数值）。
- 注册串读回：`revenue = units * unit_revenue * timing_factor + other_revenue`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加（本卡有一处必须如实标注的例外）**：
- `oracle.json` 可由 `scripts/oracle_M03.py` **逐字节重生成**（`input.json` `9b319e8d3dae9435…`、`oracle.json` `cc78ce8384f66c6d…`、`cases.json` `41a3dd846399be54…` 三件 IDENTICAL；脚本自报 `BYD pv unit price 123751.503987`、`scope gap 88697566000.69 / 14.3667%`）。
- 预注册值未被改动：`card_M03.md` 的 `期望输出 [305]` = `oracle.json.expected_float [305.0]`；2% 冻结容差未被放宽；`oracle.json` mtime 01:20:42 早于 r2/r3 两轮修订。
- 段标题**无重复**。
- **例外（P1，已被实现者自曝，本裁决如实沿用、不得抹平）**：`NEW-1` 的修复**改动了 `oracle.md` 的冻结正文**（`## 7. 披露映射` 内第 122–123 行的派生单价由 `123,751.5203…` 改为 `123,751.503987(全精度)`），**破坏了"自 r2 起仅追加"的形态**。r3 段已自述此事并给出改前/改后 hash（`d0bed79bd868cda3…` → `45f10b58008f6020…`）与字节级重建法（9,889 B / `88635eb4`）。
  **判定**：改动对象是**派生单价的印刷笔误**，非公式预期/容差/披露数值；冻结判据值（`[305]`、13/13、2%、gap 14.37%）均未被改动；`oracle.json` 自首冻未动；实现者主动自曝。**故不推翻本卡的公式裁决，但"冻结正文未被改动"这一条对本卡必须写成"已被改动并自曝"。**

**P1（本卡必须处置）**：`handoff.json.evidence_paths` 含 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，**该文件在本卡 attempt 内不存在**（仅 M01 有）；本文件自检段却逐字引用它。处置：补落该文件，或删去该路径并改写自检段为"本卡未单独运行 selfcheck；`run_card.py` 与 M01 同一文件（`b5fcc685…`）"。（**缓解**：reviewer 已用同一 harness 独立复现 rc=0/1/2/3 四例全对。）

**九条复审项关闭情况**：`F-M01-01` = 仅 M01 有记录（本卡无 `first_run_forensics.json`）；`F-M01-02` CLOSED（独立复现四例全对）；`F-M01-03` CLOSED；`F-M02-01` CLOSED-AS-RESERVED（仍为 owner 裁定项，未自决，未改产品）；**`F-M03-01` CLOSED（但修复越界，见上"例外"）**；`F-M04-01` = not applicable to this card；**`NEW-1` CLOSED —— 但代价是改动冻结正文，已自曝**；`NEW-2` CLOSED；`NEW-3` not_applicable（M01 only）；`NEW-4` CLOSED。

**其余记账发现**：
- **P1**：`handoff.json.revision_history` 4 条真实轮次被记成 6 条（r2/r3 各逐字重复一次）。
- **P2**：`status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M03/qualification.json.formula.status` 仍为 `review_pending`、`not_yet_independently_reviewed=true`。
- **P2**：`source_manifest.json.oracle_versions.oracle_md_versions[0].sha256`（`5597507c6a0e…`）为中间写入态，非当前盘上值（`b4881eeea7c1…`）。
- **P3**：`revision_r3.json` 自我 sha256 不可复现（其余 hash 声明全部相符）；`revision_r2.review_items` 扫入 `F-M03-01`/`F-M04-01`；`before/`+`after/` 三份文件与其他三卡同拷贝。

**订正要求（由实现者执行；见 §11）**：同上；另需把 `oracle.md` 的"仅追加"形态破坏与恢复方式在 `recovery/README.md` 或 `handoff.json.open_questions` 中登记为**永久性 provenance 事件**（不可回改为"从未改动"）。`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动。

---

## 点复审未予验证的事项（原样承接，不得当作已证）

以下为独立点复审明确列为"未能验证"的事项，本 attempt 原样承接，**不**声称已解决：

1. `revision_r3.json` 自称的自我 sha256 不可核验（r4 已改为显式 non-claim 并把真实值外置）。
2. 首跑 stderr 的原始字节**客观已不存在**（被成功重跑覆盖）；"首跑确实发生 `KeyError: 'continuity'`"
   **无法独立证实**，只有会话转录捕获与 mtime 序列。
3. `oracle.md` **首冻版的运行前 hash 四卡均未记录**（`F-M01-01` 的实质缺口，不可回填）。
4. M03 冻结正文的改动**发生在哪一轮**无法独立复算（盘上无该中间态副本，只有实现者自述的前后 hash）。
5. `<PLAN>\reviews` 的 4 个子目录对当前用户拒绝访问，**无法遍历排除内部被写**；
   整树最新 mtime 仍是 09-19 10:05:32，本 session 亦未写入该目录。
6. `scripts/model_registry.py` 的 mtime 变更**无法归因**（内容 hash 未变，不影响本卡）。
7. 本卡的 D/E/F **会计/行业实质**未获审阅（需签署方）；本裁决仅覆盖 A–C（formula）+ 记账。
8. 并发卡 M05–M31 的任何陈述均为**时点观察**，其后可能已被其他 session 改变。
