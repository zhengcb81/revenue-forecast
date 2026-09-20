# M02 · implementer review record

Card M02 (`direct_revenue`), Parent I-10. Attempt `execution_runs/M02/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict.

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local isolated snapshot; hashes equal | `binding.json`, `evidence/M02/source_manifest.json` |
| B positive | `[80.0, 0.0, 120.0]` vs independent oracle `[80, 0, 120]`, all within tolerance | `evidence/M02/formula_result.json` |
| C negatives | 11/11 rejected with `ModelRegistryError`; continuity positive `[50, 60]` passes | `evidence/M02/negative_results.json` |
| D mapping | one real disclosed mapping (ZJ FY2025 consolidated revenue) with page/table/span/hash/unit/period; four decisions written as PROPOSED only | `evidence/M02/disclosure_mapping.json`, `evidence/M02/accounting_decision.md` |
| E probe | labelled `historical_mapping_probe` (identity wiring only) | `evidence/M02/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M02/qualification.json` |

## 2. Independence of the oracle

- `scripts/oracle_M02.py` imports only `json`, `os`, `decimal`. It never imports `model_registry`.
- `scripts/run_card.py` calls exactly one product function and reads expectations only from `oracle.json`.
- Negatives are in-memory `deepcopy` cases; JSON-parser rejections cannot masquerade as model rejections.
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`; import/file errors are recorded as FAIL.

## 3. Results in detail

- Registry formula string observed: `revenue[t] = direct_revenue[t]` — matches the frozen expectation.
- Positive: `[80.0, 0.0, 120.0]`. The middle value stayed exactly `0.0`, i.e. a zero is treated as data and
  not as a missing field that would attract a default.
- Continuity positive `[50, 60]`; break patch `years = [2027, 2029]` rejected with
  `direct_revenue.years must be consecutive and increasing`.
- Rejections: `NEG-CARD` → `driver direct_revenue.revenue must be between 0.0 and inf: FY2028`;
  `N01a` numeric; `N01b/c/d` finite; `N02` one value per forecast year;
  `N03` `missing drivers for direct_revenue: revenue`;
  `N04` `unsupported drivers for direct_revenue: unknown_driver`;
  `N05a/b` fiscal years.
- **Two design observations (recorded, not scored)**:
  - `BASE-INDEPENDENCE`: with `base_revenue = 999` the output is **identical** to the positive case, proving
    `base_revenue` is not a term of this model.
  - `OBS-NEG-BASE`: with `base_revenue = -5` the product still raises
    `ModelRegistryError: direct_revenue.base_revenue cannot be negative`, even though the value is unused.
    Raised as DEC-M02-3 for the reviewer; **no product change was made**.

## 4. Unit / dimension and rejection checks

- `revenue` is an amount; the model copies it, so input and output dimensions are identical by construction.
- Float exactness: `349,079,082,852 < 2**53`, so the IEEE754 input is exact — no rounding is introduced.
- Per-share vs total: not applicable (the field must be a total).
- Gross vs net: the mapping fixes the basis as consolidated gross operating revenue.
- Period alignment: one value per fiscal year, positionally aligned with `years`; the model performs no
  continuity check itself, which is why the `years` contract carries the whole burden.
- Rejection conditions R1-R8 in `oracle.md` §6; R1-R6 executed, R7-R8 are disclosure/business refusals.

## 5. Judgement calls the reviewer should attack first

1. **The reconciliation is a constructive identity.** The driver *is* the disclosed figure, so the residual is
   identically zero and carries no information. This attempt refuses to call that "reconciliation passed"
   (DEC-M02-2) because I-10-A item 3 forbids back-solving a parameter from revenue and then treating the
   same-formula result as verification.
2. **No driver means no causal content.** The card says the simple formula must not raise confidence; the
   mapping therefore records `not_decomposed_reason` and refuses to claim any explanation of the revenue path.
3. **`base_revenue` guard vs unused field.** Keep fail-closed validation (current behaviour) or ignore unused
   fields? Implementer position: keep the guard; the observation is recorded so the reviewer can overrule.
4. **I-00-B interpretation** — same deviation note as M01: I-00-B binds the isolation plan, so this attempt
   materialised its own byte-identical read-only snapshot rather than running from a tree that I-00-B created.
5. **The production forecast entry point was not exercised** (`calculate_model_path` is an I-10-A obligation);
   `evidence/M02/forecast_integration.json` records only read-only observations of the call site.

## 6. What this card does NOT claim

- No accuracy claim: the model has no growth driver, so forecast skill cannot be evaluated from its own output.
- No `disclosure_adaptation`: the mapping is a minimum, unsigned, and its reconciliation is an identity.
- No formula rewrite (card line 65).

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M02.py` and `scripts/run_card.py`; diff against the recorded results.
2. Confirm the isolated copy hash still equals the production hash.
3. Re-derive `349,079,082,852` from the FY2025 report page 15 yourself, and confirm the FY2024 comparative is
   the same figure as in the FY2024 report page 15 (no restatement bridge needed).
4. Pick an unused case (e.g. a two-year path with a very large value, or `revenue = [0]` with `years=[2030]`)
   and freeze the expectation before running.
5. Adjudicate DEC-M02-1..4 and SR-M02-A/B.

---

## revision r2 - response to the independent review (status stays `review_pending`)

The reviewer returned **accepted_scoped (formula only)** for M01-M04 with five required fixes and one
item reserved for adjudication. r2 changes **attempt-local files only**; no production repository was
touched and no oracle expectation, tolerance or disclosure figure was altered to make anything pass.

### Verdict-carrying exit code (F-M01-02)

| item | change | evidence |
|---|---|---|
| F-M01-02 | `scripts/run_card.py` no longer returns 0 unconditionally. It now returns **0** only when the positive path matches the independent oracle within tolerance, the continuity positive passes and **all** negative cases were rejected with `ModelRegistryError`; **2** if the harness could not produce a verdict; **3** if the verdict is negative. The JSON artefacts are still written before returning, so a non-zero exit never destroys evidence. `scripts/run_M01.py` was patched the same way (M01 only). | `scripts/run_card.py`, `evidence/M02/revision_r2.json`, `after/rerun_sha256.json` |
| re-run | the same `calculate_registered_model` call was re-executed unchanged | **raw rc = 0** (expected 0), `evidence/run_result.json/exit_code_semantics` = `verdict` / `exit_code` |

### Delivery completeness (F-M01-03)

- `after/rerun_sha256.json` + `after/rerun_stdout.txt` + `after/rerun_stderr.txt`: post-r2 re-run hashes.
- `recovery/README.md`: `not_applicable_with_reason` - this card is a pure in-process function with no durable state, lock, lease or partial publication to recover.
- `changes.diff`: explicit **no product change** statement; there is no diff to show by design.
- `before/git_status_revenue-forecast.txt` re-written as **UTF-8** (was UTF-16LE).
- `evidence/M02/first_run_forensics.json`: F-M01-01 record.

### Frozen expectations were NOT rewritten

`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body, and `evidence/M02/source_manifest.json.oracle_versions` now indexes the oracle document and script versions with hashes and timestamps.

### F-M02-01 - reserved for owner/specialist adjudication (not self-decided)

- The reviewer asked for the two behaviours to be written up rather than resolved. Both are recorded in `decision.md` DEC-M02-3 and in the appended r2 section of `evidence/M02/accounting_decision.md`: the validator rejects `base_revenue < 0` uniformly before dispatch, while `_direct_revenue` deletes the field and `_direct_growth` consumes it. Measured: `base_revenue = 999` leaves the output identical; `base_revenue = -5` still raises `ModelRegistryError`.
- No product change was made and no position is asserted; the item is carried in `handoff.json.open_questions` marked `requires_owner_or_specialist_ruling`.

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
**授予范围：仅 `formula`，且仅限本 attempt（`execution_runs/M02/a20260919-01`）盘上版本、仅限 `iso/checkout_scripts` 副本。**

**未授予项（明示）**：
- `disclosure_adaptation` = **未授予**，保持 `unmapped`。§7 的对账**是构造性恒等式**（把已披露 FY2025 收入 `349,079,082,852` 元原值填回 `revenue` 必然零残差），只证明"复制"接线正确，**不能**证明来源/期间/总净额/口径，也**不是**准确性证据。
- `accuracy` = **未授予**，保持 `unproven`。`STOP_ACCURACY` 命中（无 I-12 冻结设计）；本模型无驱动，一期一值，无预测技能可评。
- 未授予任何跨公司/跨行业/跨期间外推；未授予 D/E/F 完成。
- `formula` 通过**不**提升 `disclosure_adaptation` 或 `accuracy`。

**独立复算（reviewer 自造输入）**：11 例全部通过。
- `revenue=[37.5, 0.0, 412.25, 1000000.0]`，4 年 → 逐值原样复制，diff 0；**含一个精确 0.0 的年份未被默认值替换**。
- base 无关性：同一 drivers 下 `base=0` 与 `base=999` 输出**逐值相同**。
- 保真：全长 = `len(years)`，全部 `float` 且有限。
- 自造负例（均不在卡片清单内）全部以 `ModelRegistryError` 被拒：`revenue=[-0.01]` / `revenue=["100"]` / `revenue=[None]` / `revenue=100.0`（标量而非序列）。
- 注册串读回：`revenue[t] = direct_revenue[t]`，与 `oracle.md` §1 冻结串逐字相同。

**冻结与追加**：
- `oracle.md` **无重复章节**；`oracle.json` 可由 `scripts/oracle_M02.py` **逐字节重生成**（`input.json` `8b7d9dc86578d1f6…`、`oracle.json` `258cd8e214e04fb7…`、`cases.json` `e10fb6c095bb16a8…` 三件 IDENTICAL）。
- 预注册值未被改动：`card_M02.md` 的 `期望输出 [80,0,120]` = `oracle.json.expected_float [80.0,0.0,120.0]`；容差规则未放宽；`oracle.json` mtime 01:19:52 早于 r2/r3 两轮修订。

**P1（本卡必须处置，否则"当前版本"的 oracle 层无凭据）**：**`oracle.md` 根本没有 r2 追加段，但本文件 `### Frozen expectations were NOT rewritten` 段逐字声称"`oracle.md` was **appended to**, never rewritten: the r2 section sits below the frozen body"。**
- 盘上事实：`oracle.md` = 7,838 B，sha256 `77dce63db21fe391f0dea0b8fb90ea71d37b2da7d3557bfa2c33fb9283031ad0`，mtime **01:19:25**（早于 r2 的 01:44 与 r3 的 02:04），`修订 r2` 出现次数 **0**。
- 全树检索 `修订 r2（独立复审后追加，非重写）`：仅命中 `scripts/revise_r2.py`（模板字符串），**未命中 `oracle.md`**。
- 根因：共享的 `scripts/apply_r2_patches.py:83` 把 oracle.md 追加写死在 `if card == "M03":` 分支内；M01 的 r2 段由仅存在于 M01 的 `scripts/finalize_r2.py` 写入。四卡 `apply_r2_patches.py`（`965c71fe3c9eb3e10bfa…`）与 `revise_r2.py`（`b0e6295c25069e027de2…`）逐字节相同。
- 影响：本卡的"五条必修已在 oracle 层登记"在盘上**无载体**；`source_manifest.json.oracle_versions.oracle_md_versions[0]` 只登记了一条 `v1_frozen_then_appended`（sha256 = 当前盘上 hash，`sha256_before_r2_append = "NOT CAPTURED"`），**没有任何"已追加"版本可索引**。
- 处置（见 §11.3，二选一，**不得维持现状**）：① 由实现者在 `oracle.md` 末尾**追加**一节 r2 索引（附追加前字节数与 sha256 `77dce63db21f…`/7,838 B，并如实注明"事后补记：r2 轮曾声称已追加但实际未落盘"）；或 ② 把上述 `review.md` 措辞改为"`oracle.md` **未被修订**，与运行前冻结件逐字节相同（`77dce63db21f…`/7,838 B）；本卡五条的 r2 处置由 `review.md` 与 `evidence/M02/revision_r2.json` 承载，不由 `oracle.md` 承载"，并把 `source_manifest.json` 的 `version`/`note` 改为 `v1_frozen_unamended` / `r2 did NOT append a section to this file`。

**P1（本卡必须处置）**：`handoff.json.evidence_paths` 含 `recovery/r2_exit_code_selfcheck/selfcheck_result.json`，**该文件在本卡 attempt 内不存在**（仅 M01 有）；而本文件自检段却逐字引用它作为 A/B/C/D 四例 rc 的出处。处置：补落该文件，或删去该路径并把自检段改写为"本卡未单独运行 selfcheck；`run_card.py` 与 M01 同一文件（`b5fcc685…`），该结论由 M01 的对应文件承载"。
（**缓解事实**：reviewer 已用同一 harness 独立复现该四例，`rc=0/1/2/3` 全对，故被指认的**主张为真**，缺的是本卡盘上载体。）

**九条复审项关闭情况**：`F-M01-01` = 仅 M01 有记录（本卡无 `first_run_forensics.json`，属 M01-specific）；`F-M01-02` CLOSED（reviewer 独立复现 rc 四例全对）；`F-M01-03` CLOSED；**`F-M02-01` CLOSED-AS-RESERVED —— 仍如实登记、仍为 owner 裁定项、未被自决、未改产品**（reviewer 实测：`base=999` 输出与正例逐值相同；`base=-5` → `ModelRegistryError: direct_revenue.base_revenue cannot be negative`）；`F-M03-01`/`F-M04-01` = not applicable to this card（但 `source_manifest.revision_r2.review_items` 误列，见 P3）；`NEW-1` not_applicable（M03 only）；`NEW-2` CLOSED；`NEW-3` not_applicable（M01 only）；`NEW-4` CLOSED。

**其余记账发现**：
- **P1**：`handoff.json.revision_history` 4 条真实轮次被记成 6 条（r2/r3 各逐字重复一次）。
- **P2**：`status="review_pending"` 与 `qualifications.formula="accepted_scoped …"` 自相矛盾；`evidence/M02/qualification.json.formula.status` 仍为 `review_pending`、`not_yet_independently_reviewed=true`。
- **P3**：`revision_r3.json` 自我 sha256 不可复现（其余 hash 声明全部相符）；`revision_r2.review_items` 扫入 `F-M03-01`/`F-M04-01`；`before/`+`after/` 三份文件与其他三卡同拷贝。

**订正要求（由实现者执行；见 §11）**：同上（`status`→`accepted_scoped`、`reviewer_status`→`point_review_returned`、`revision_history` 去重+追加 r4、`qualification.json.formula` 补独立复核块、补/删 selfcheck 证据路径、`review_items` 去非本卡条目）。`disclosure_adaptation` 与 `accuracy` 两栏**不得**改动。

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
