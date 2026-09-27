# reviewer_report.md — RF-RATCHET-REST-B / a20260923-01 (independent review)

Reviewer: independent reviewer subagent (read/grep/pwsh only; no product writes; no（域：本卡授予复审者的工具集 read/grep/pwsh）
state-changing git in the RF repo; all runnable work under `%TEMP%\rf-review-b` and the（域：本次复审可运行工作的落盘位置 %TEMP%）
card's own `%TEMP%\rf-rest-b` scratch; `PYTHONIOENCODING=utf-8` throughout; no network).
This file + `reviewer_report.sha256` are the reviewer's ONLY writes.（域：本卡复审写盘面 = 2 个文件）

## VERDICT: **ACCEPT (sign) — scope-limited, 2 minor findings + 3 cross-card notes; no rework of delivery required.**

Card claim set re-verified from live bytes and independent re-runs: three promotion-
introduced ratchet rows fixed by code-refactor-down-only
(`model_registry.py` 28→8 ≤9, `revenue_core.py` 23→6 ≤6, `revenue_publication.py`
16→5 ≤10), no byte-locks, revert-not-refactor falsified, zero behavior change,
`review_pending`/unsigned handoff. All substantively CONFIRMED. Findings F-1/F-2 are（域：本报告 §1–§8 各节复算项）
evidence/documentation defects inside the attempt (delivery bytes unaffected);
F-3..F-5 are attribution/routing notes for the parent.

## 1. Deliverables (all re-hashed live)（域：§1 表内 6 类交付物）

| artifact | live result | claim | verdict |
|---|---|---|---|
| `oracle.md` | sha256 `98dcb0a8fdd05b81fb437b1ce750d359da3d29f2f93648598ca95e580c606f4d`, 20053 B | `98dcb0a8…` | ✓ |
| frozen-first | oracle mtime 21:15:25 < binding 21:17:50 < first judged run (red_verbatim 21:20:49, red_judged 21:22:57); pre-freeze measure scans 21:07:52 disclosed in oracle §9 as pre-freeze, non-judged | frozen before first judged run | ✓ |
| `binding_before.json` | 40 pins counted (`pins=40`); 39/40 re-hashed live and still match; sole drift = `REMEDIATION_REGISTER.md` (concurrent shared-doc churn, already ` M` in the card's own porcelain baseline — not attributable to this card) | 40 pins | ✓ |
| `commands.json` / `decision.md` / `handoff.json` / `recovery/README.md` + `recovery/before_images/` | read in full; handoff `status=review_pending`, `self_sign=false`, `signature=null` | review_pending/unsigned, you sign | ✓ |
| `changes.diff` | sha256 `bcca249844b39dc3c48e86c4bacacd9a4d97fe4f250f64860ba588ba4d6731e9`, 23626 B; exactly 3 `diff --git` sections (`scripts/{model_registry,revenue_core,revenue_publication}.py`); hunks 2/9/2 | exactly 3 files, 2/9/2 | ✓ |
| `git apply --check` (reviewer's own run) | **rc=0** against the live repo (read-only check) | applies cleanly | ✓ |
| independent applier (reviewer-written, in `%TEMP%`) | applying `changes.diff` to the LIVE production bytes reproduces `refactored/` byte-for-byte: `2154ad4f…`, `678f5f1b…`, `1910e276…` (== `refactored/manifest.json` after-shas), 0 content mismatches over 13 hunks | diff == delivery | ✓ |
| skip/xfail/baseline/marker scan of diff | **0 matches** | none | ✓ |（域：changes.diff 3 文件）
| `refactored/manifest.json` | before-shas == live production == promotion payload pins; after-shas == live `refactored/` files; byte counts 30116→32306 / 25842→27234 / 24917→25634 | before→after, hunks 2/9/2 | ✓ |
| `evidence/` incl. `bytelock/` | present (bytelock, families_before/after + external_corroboration, green, integrity, measure, mutation, red, revert) | present | ✓ |

## 2. Byte-lock pre-check (reviewer's own greps + re-run of their scanner)

- Full sha256 + 8-char/12-char prefix literals of the three live files over `tests/`,
  `tools/`, `assurance/` → **0 hits** (own grep, three separate runs).
- Name references `model_registry.py|revenue_core.py|revenue_publication.py` over
  `tests/` (9) + `tools/` (6) = **15** — matches the card's count.
- Re-ran their `bytelock_scan.py` read-only: `total sha-literal hits = 0`,
  `total name references = 15`, `total hashing-call lines = 138`; live production hashes
  printed by the scan == binding pins (`62f864b9…`, `8a761498…`, `bc2bb4a3…`).
  Reviewer's read of the hashing-call enumeration: all artifact/guard/config/payload-level（域：138 行哈希调用枚举）
  (`run_coverage_gates` floors, ratchet table, comment-only line refs) — none hashes the
  three files' bytes.
- The 3 assertion needles preserved in delivery bytes:
  `tests/test_model_extensions_anchor.py:137-139` `assertIn("build_extension_specs", …)`
  → present at `refactored model_registry.py` L10/L244; `tests/test_skill_documentation.py`
  validate-before-sign order → in refactored `revenue_core.py`
  `validate_published_forecast(result, data)` index 19070 < `build_publication_receipt(` index 19794;
  `tests/test_structure_targets.py` ≤2500 → refactored `revenue_core.py` = 772 lines (live 706).
- **Conclusion: NO byte-lock on any of the three files → helper-split path (option i)
  compliant for all three rows; option (ii) STOP not triggered. CONFIRMED independently.**（域：§2 字节锁复算的 3 文件）

## 3. CC numbers (both implementations, reviewer-run)

Ran the card's import-based `scan_all_violations.py` AND the inlined
`independent_crosscheck.py` against `%TEMP%\rf-rest-b\iso_after\scripts`, which the
reviewer proved ≡ (production + `refactored/` overlay): recursive hash compare of the six
roots = **232 identical files, only the 3 target files differ**, and those 3 hash exactly（域：6 目录递归哈希比对）
to the `refactored/` pins.

- My rows: `model_registry.py ok actual=8 ≤9`, `revenue_core.py ok actual=6 ≤6`,
  `revenue_publication.py ok actual=5 ≤10` (identical in both implementations).
- Derived 3-key run of the REAL test module's loop (`derived_3key.py`, reviewer re-run):
  `ok 8≤9 / ok 6≤6 / ok 5≤10`, DERIVED-3KEY: PASS, rc 0.
- Sibling rows untouched bit-for-bit: the OTHER 5 violating files are byte-identical
  between the runnable tree and live production (the232-identical-file compare covers
  them; `changes.diff` cannot touch them) and scan in every run as（域：双实现 × 双树扫描）
  F1 32>23, F2 22>21, F3 17>9, F5 114>88, N1 27>10 — unchanged numbers.
- Full-row residual = **4 frozen + 1 new** (both implementations), exactly the claim.

## 4. Zero-behavior families (reviewer's own BEFORE/AFTER pair, run in `%TEMP%`)

Built `%TEMP%\rf-review-b\iso_before` (= verified tree with the 3 files restored to
production bytes) and ran the card's frozen `scratch/run_families.py` on both trees with
identical commands/flags (rc + timing-stripped + traceback-line-normalized compare,
reviewer's own comparator):

| family | BEFORE | AFTER (refactored final bytes) | identical |
|---|---|---|---|
| F0 ratchet | rc1, **2 failed** (`analysis/confidence.py max 32 > 23`, `model_extensions.py max 27 > 10`) | same rc, same two first-abort messages | ✓ |
| F1 B1 battery (11 files) | rc1, **1 failed, 99 passed** (`test_attestation::configured_provider…`) | same rc/counts/test | ✓ |
| F2 I-08-C 13-node | rc0, **13 passed** | rc0, 13 passed | ✓ |
| F3 5-file model battery | rc0, **59 passed / 202 subtests** | same | ✓ |
| F5 golden lock | rc0, 1 passed (5 pinned result hashes) | same | ✓ |
| F6 needles | rc0, 9 passed/18 subtests | same | ✓ |
| F7 models | rc0, 9 passed/31 subtests | same | ✓ |
| F8 adversarial | rc1, **1 failed, 5 passed** (`test_receipt_attacks::context_fabrication…`) | same rc/counts/test | ✓ |
| F9 backtest | rc0, 17 passed | same | ✓ |

`ALL_IDENTICAL` (9/9 rc + normalized stdout) from the reviewer's comparator; matches the
card's `evidence/families_before_after_identity.txt` and their raws.

- **The 2 pre-existing HEAD reds**: F1's `test_attestation::
  test_configured_provider_means_host_signed_publication` and F8's `test_receipt_attacks::
  test_context_fabrication_is_rejected_by_final_validation` fail identically BEFORE and
  AFTER (1F/99P, 1F/5P) — the governing invariant BEFORE==AFTER holds. Oracle §6's
  "all pass" expectation was disproven by the measured BEFORE baseline and DISCLOSED.
  Corroboration files present and consistent (`evidence/families_before/external_
  corroboration/`: `win_head_*` = 1F/6P and 1F/2P RC=1 on production HEAD, `wsl_atEc3_*`
  twins same outcomes), citing RF-STEP9-TRIAGE's independent runs; the reviewer also read
  TRIAGE's own win_head/wsl raws under `execution_runs/RF-STEP9-TRIAGE/a20260923-01/
  evidence/` — same test ids, same assertion line, same E27 error. Externally corroborated ✓.
- **mypy 69==69**: reviewer ran `mypy scripts --no-error-summary --ignore-missing-imports`
  independently on BOTH trees: **69 `: error:` lines each, error sets line-identical
  (0 differences)**, and byte-identical to the card's recorded `mypy_after.txt` (diff = 0).
  Their recorded before/after pair differs only in 2 `note:` lines of untouched（域：their mypy_before vs mypy_after 行集）
  `forecast/segments.py` (mypy overload-note nondeterminism), not errors — claim holds.
  The `list | tuple` annotation fix is present at `refactored model_registry.py` L424/L449;
  the pre-fix `-> object:` / `values: object,` bytes survive in the card's `%TEMP%`
  `mut_tree\scripts\model_registry.py`, confirming annotations as the only post-catch byte（域：post-catch 字节变更面）
  change. **Final-byte family rerun confirmed by mtime**: final delivery bytes
  22:25:07 < mypy_after 22:26:19 < scan_after_all3 22:27:50 < families AFTER raws
  22:38–22:43 (F4 final 22:38:54).
- **ruff rc=0** and **py_compile rc=0** — reviewer's own runs on the three refactored files
  (pycache redirected to `%TEMP%`), matching `evidence/green/ruff_after.txt`.
- Literal/comment parity re-ran their scripts: `LITERAL_PARITY` missing=0 on all three（域：3 个目标文件的字面量/注释）
  (added = 8+4 helper docstrings, 0 for revenue_core); `COMMENT_PARITY` 27/27, 37/37, 40/40
  missing=0 added=0. `global` statements: 2 in live production (`revenue_core` L135/L190,
  pre-existing helpers untouched — same lines in delivery) → **no new `global` introduced**;
  the two `_ATTESTATION_LAST_FAILURE = None` dead-stores remain local (L307/L468);
  `__all__` block unchanged.

## 5. Revert-not-refactor probe (raws verified + reviewer re-ran the decisive checks)

- Overlay sources are **sha256 file-content pins, not git object ids** — see F-3.
  Verified by re-hash: `PROMOTION-EXEC/recovery/before_images/B-1/revenue_core.py` =
  `1821fd2a8a4efa2b…` (14136 B), `…/revenue_publication.py` = `183803bbd1f884b6…`
  (10681 B), `MODEL-ORACLE-ALIGN/recovery/before_images/registry_repromotion/
  model_registry.py` = `9ec6529550f189a4…` (26446 B); each also matches its carrier
  (`binding.json`/`oracle.md`/`decision.md`/`promotion_exec_log.jsonl` before_sha256).
  The card's `%TEMP%\rf-rest-b\iso_revert` three files are byte-identical to those images
  (sha1 compare, all three equal).（域：iso_revert 的 3 覆盖文件）
- Raws read: F2 revert rc1 `test_e11_host_signed_label_flip_is_rejected_at_consumption`
  FAILED / 12 passed; F4 revert `phase=after total=7 passed=5 failed=2` (R-B1-N1, R-B2-N1),
  rc3; F1 revert rc0 **100 passed**; F3/F7 revert green (aligned, non-dispositive as disclosed).
- **Reviewer independent re-runs**: F2 on `iso_revert` → `1 failed, 12 passed`, rc1, e11
  `DID NOT RAISE ForecastInputError` (vs 13/13 rc0 on the refactored tree, reviewer-run);
  `verify_i10b.py after` (verifier sha `8822a927…` == pin) via reviewer's own mirror →
  **revert 5/7 rc3, after 7/7 rc0**; F1 B1 battery on `iso_revert` → **100 passed rc0**.
- **VERDICT: revert falsified — CONFIRMED independently** (refactor was the only（域：F1/F2/F4 回退探针结果）
  compliant path).

## 6. Mutation honesty

- Disclosed false-green incident is real and documented: `mut3_vacuous_first_attempt_note.txt`
  ("` or False` after the colon → SyntaxError → `_max_complexity` returns 0 → vacuous
  `ok actual=0`") + decision.md §E method lesson. Honesty: credit given.
- Parse-guarded replacements verified in raws: mut1 registry `FAIL actual=10 > 9` → restore
  `ok actual=8`; mut2 publication `FAIL actual=11 > 10` → restore `ok actual=5`;
  mut3 core `FAIL actual=8 > 6` → `restored_scan_green` shows `ok actual=6`.
  3 RED + 3 GREEN raws present, sequence-consistent with the per-file order.
- **Restore-sha check (reviewer re-hash of `%TEMP%\rf-rest-b\mut_tree`)**:
  `revenue_publication.py` == delivery `1910e276…` ✓; `model_registry.py` =
  `96134215…` = the delivery bytes *before* the later `list|tuple` annotation fix
  (diff = exactly the 2 annotations) — consistent with restore-then-fix timing ✓;
  **`revenue_core.py` = delivery bytes + the still-injected ` or False`
  (live scan of `mut_tree` now reports `FAIL revenue_core.py actual=8 > 6`)** →
  see Finding F-1.

## 7. Frozen invariants

1. `tools/tests/test_complexity_ratchet.py` live sha256 = `eb1a36cfd54a8b96e3b5dca6ca4b7a89ca6b1e1605d22eedb69f643245edd10a`, 3014 B — **untouched** ✓ (before==after trivially; also pinned in 3 sibling bindings).
2. **FROZEN_MAX literal block**: reviewer reproduced **both** shas from that same file —
   `78c06a872d71320f…` = REST-B's documented binding rule ("text between (incl.)
   `FROZEN_MAX = {` and (incl.) `NEW_FILE_MAX = 10`", raw contiguous slice) ✓; and
   `1e9cce36115c381…` = the sibling's value, whose rule is *undocumented in
   RF-RATCHET-FIX's binding* — reviewer reverse-engineered it exactly:
   `sha256(ast.get_source_segment(FROZEN_MAX assign) + "\n" + ast.get_source_segment(NEW_FILE_MAX assign))`.
   Both are functions of the same untouched file ⇒ before==after holds under both.
   Attribution: the `1e9cce36` pin lives in **RF-RATCHET-FIX**'s `binding_before.json:185`
   (predecessor, attempt incomplete: only oracle/binding/evidence/iso/recovery on disk),（域：RF-RATCHET-FIX 目录清单）
   **not RF-RATCHET-FIX-2** — FIX-2 records no block sha at all (only full-file `eb1a36cf`（域：FIX-2 冻结证明文件）
   in its `frozen_sha_proof.txt`). → cross-card note CN-1 (+ internal note F-2).
3. Three production files live-re-hash == promotion payload pins (`62f864b9…` /
   `8a761498…` / `bc2bb4a3…`) and `recovery/before_images/` == live → **zero product
   writes** ✓. Scoped porcelain (reviewer's own `git status --porcelain`): **0 entries
   under `scripts/ tests/ tools/ config/ e2e/`**; every current entry is planning/temp（域：git status --porcelain 当前快照）
   churn present at or after the card's baseline (incl. pre-existing `.tmp-r41-mutation/`
   and `assurance/…/plan_inputs.json.bak`, both already in `porcelain_baseline.txt`) ✓.
4. No skip/xfail/baseline/marker additions in the diff ✓; no such text introduced in the
   three files (literal/comment parity + ruff/py_compile/mypy clean) ✓.

## 8. Disclosures checked

- Mid-run mypy +1 `zip(years, object)` catch-and-fix: confirmed (pre-fix bytes survive in
  `mut_tree`; final bytes carry `list | tuple`; mypy sets identical69; families AFTER
  re-run on final bytes — mtime window above) ✓.
- F8 line-number normalization: their `families_before_after_identity.txt` records the sole
  diff `revenue_publication.py:396 → 416`; reviewer re-ran their `f8_recheck.py` →
  `F8 identical (timings+line-refs normalized): True`; my own comparator independently
  normalizes the same refs and reports identical ✓. (Task text says "396→416"; the card's
  records say 396→416 in decision.md §D and the identity file — consistent.)
- Pre-existing 2 reds corroboration files present (4 files: `win_head_*` ×2, `wsl_atEc3_*` ×2)
  + TRIAGE's own raws in its attempt ✓.
- "Living document" incremental decision.md: consistent with evidence mtimes throughout.

## FINDINGS

**F-1 (MEDIUM, evidence-integrity; delivery unaffected) — the `revenue_core` mutation was
never restored in the scratch tree, and the cited restore-green raw predates the cited red.**
Evidence: `%TEMP%\rf-rest-b\mut_tree\scripts\revenue_core.py` still contains the injected
`or False` (reviewer's live scan of `mut_tree` = `FAIL revenue_core.py actual=8 > 6`);
file mtime 22:12:05 vs red raw 22:12:13 vs the only core restore-green raw 22:11:20 — i.e.（域：mut3 时间线 3 个原始件）
the green raw belongs to the *earlier vacuous-attempt cycle*, not to the parse-guarded
attempt. decision.md §E pairs them as one red→restore cycle ("restore → ok actual=6 …
(mut3_…_restored_scan_green.txt)"), and handoff/commands inherit that wording. Impact:
none on delivery (`refactored/` revenue_core = clean 6≤6, proven by two independent（域：交付字节 refactored/ 3 文件）
implementations and two independent family batteries); `mut_tree` is declared disposable
in `recovery/README.md`. Required action: append a one-line correction to decision.md §E at
land-time (green raw @22:11:20 = pre-attempt-2 restore; post-attempt-2 restore not
evidenced; scratch left mutated). No code rework.

**F-2 (LOW, documentation inconsistency; invariant substantively true) — `oracle.md` §8.1
pins the frozen-table block sha as `1e9cce36…` while `binding_before.json`/`commands.json`/
`decision.md`/`handoff.json`/`recovery/README.md` all record `78c06a87…`, and handoff（域：REST-B 文档集 5 份）
disclosure #5 states the *oracle* uses the `78c06a87` rule (it does not — it cites
`1e9cce36`).** Both shas verified by the reviewer as sha256 of the same untouched literal
block under two different, now-documented extraction rules (§7.2). `before==after` holds
under either rule, so no invariant breach; only the cross-document citation of "the block（域：两条提取规则的同源块）
sha" is inconsistent. Fix at land-time: one sentence aligning oracle §8.1 with the binding
rule (or citing both pairs).

**F-3 (INFO/attribution) — `1821fd2a`/`183803bb`/`9ec65295` are not git objects**
(`git cat-file -t` / `rev-parse` → "Not a valid object name"); they are sha256
file-content pins, verified by live re-hash against the carriers and the overlay tree
(§5). The oracle's wording never claimed git objecthood; the review checklist's
"git cat-file" step is inapplicable. Substance: VERIFIED.

**F-4 (INFO/routing correction) — REST-B's "2 pre-existing HEAD reds → 另行派卡" suggestion
is already superseded**: REMEDIATION_REGISTER §81 (line 1632) records
「其建议『2 既有 HEAD 红另行派卡』→ 已被 TRIAGE 路由覆盖（#1 入其 7 文件 diff、#2→I-08-B-14FILE
已派）——无需新卡」. Confirmed: TRIAGE `changes.diff` = 7 files including
`tests/adversarial/test_receipt_attacks.py` (#1), TRIAGE `handoff.md` line 37 = #2 →
`I-08-B-14FILE/a20260923-01` dispatched (register §81①). **No new cards needed.**
Also: REST-B routes its sibling rows to "RF-RATCHET-FIX", but the completing owner card is
**RF-RATCHET-FIX-2** (status `complete`, `changes.diff` = exactly
`scripts/analysis/confidence.py` + `scripts/model_extensions.py`).

**F-5 (INFO/pin churn) — 1 of 40 binding pins (`REMEDIATION_REGISTER.md`) no longer matches
live** (concurrent register edits; already dirty at baseline). Point-in-time binding, not
attributable to this card.

### Cross-card notes (for the parent, not violations)
- **CN-1 (FROZEN_MAX block-sha rule)**: two rules exist for the same quantity —
  REST-B = literal contiguous slice (`78c06a87…`, documented in its `binding_before.json`);
  RF-RATCHET-FIX = AST source-segment join with a single `\n` (`1e9cce36…`, rule
  reconstructed by this review, undocumented at capture). Both anchor the same untouched
  full-file sha `eb1a36cf…`. **Recommendation: REST-B's binding rule is authoritative for
  future checks** (documented + reproducible); record CN-1 so later reviewers comparing the
  two pins do not read either as drift. FIX-2 pins neither (full-file only).（域：FIX-2 冻结证明）
- **CN-2**: remaining masked rows are covered — REST-A = 3 files
  (`forecast/calc.py`, `generate_input_template.py`, `research/targets.py`; status
  `review_pending`, diff present), RF-RATCHET-FIX-2 = 2 files (`complete`). No further
  ratchet cards required beyond these.
- **CN-3**: the 2 pre-existing HEAD reds are routed (F-4) — cite TRIAGE, do not re-dispatch.

## SCOPE IF ACCEPTING (for the parent's single landing batch)

`changes.diff` = exactly 3 files (`scripts/model_registry.py`, `scripts/revenue_core.py`,
`scripts/revenue_publication.py`; `git apply --check` rc0 re-verified by this review;
independent applier reproduces delivery bytes exactly). Parent batches it with
**RF-RATCHET-FIX-2**'s 2-file diff + **RF-RATCHET-REST-A**'s 3-file diff (+ per TRIAGE's
report, TRIAGE's own 7-file diff was already proposed for the same landing batch) → one
apply+commit+push = the ratchet-green push. Remaining5 masked rows = REST-A(3) +
FIX-2(2) — both in flight/delivered, no new cards. The 2 pre-existing HEAD reds are
already routed (TRIAGE #1 → its 7-file diff; #2 → I-08-B-14FILE dispatched) — cite, no new
cards (this corrects REST-B's "另行派卡" wording). FROZEN_MAX-rule discrepancy = CN-1 note
for the parent. Full-repo suite + coverage gate remain the parent's push-gate obligation
(NR-2/NR-3, unchanged posture).

## UNVERIFIED / OUT OF SCOPE

- Full-repo test suite and `tools/run_coverage_gates.py` (70/70/80) — deliberately not run
  (card's NR-2/NR-3; parent push gate). Reviewer ran only F0–F9 + F4 + revert probes.（域：本次复审执行的测试族 F0–F9+F4+回退）
- Internal correctness of RF-RATCHET-FIX-2 / RF-RATCHET-REST-A / TRIAGE / I-08-B-14FILE
  deliveries — other reviewers' scope.
- `delivery_acceptance=unproven` / `dispatch_acceptance=unmapped` are parent-side states;
  this report does not promote them.
- Network-dependent claims: none made or checked (no network used).（域：本报告全部断言）

## SIGNATURE

- Reviewer verdict: **ACCEPT (scope-limited)** — F-1/F-2 appended as one-line corrections
  at land-time; CN-1..CN-3 relayed to the parent; no delivery rework; no new cards.
- Report integrity: `reviewer_report.sha256` sidecar written alongside this file (computed
  after the REM-79 self-scan below).
- The implementer handoff remains `review_pending` / `self_sign=false` / unsigned — the
  implementer must not self-sign; this reviewer report is the signature artifact.
- REM-79 self-scan: `python -X utf8 -B tools/check_domain_assertions.py reviewer_report.md`
  run with `PYTHONIOENCODING=utf-8` (REM79-MECHANIZATION `tools/check_domain_assertions.py`
  v1.2.0-correction2) — **0 violations, rc 0**; the 25 initially flagged lines each carry a
  same-line （域：…） qualifier, per the frozen REM-79 rule (域：本行断言的作用域).
