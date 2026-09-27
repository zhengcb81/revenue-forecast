# reviewer_report.md — RF-RATCHET-FIX-2 / attempt a20260923-01 — independent review

Reviewer: delegated reviewer subagent of parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.
Review date: 2026-09-23 (session runtime), Windows / Python 3.13.9, RF HEAD `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb`.
Method: read/grep/pwsh; re-runs confined to `%TEMP%` with `-B -p no:cacheprovider` + fresh `--basetemp`;
RF product sources READ-ONLY; git verbs read-only (`status`/`diff`/`log`/`-1`/`rev-parse`/`cat-file`); no network.
Reviewer write boundary: this report + its `.sha256` sidecar in the attempt dir — nothing else on disk in RF.
Signature note: reviewer signs HERE (report + sidecar). `handoff.json` was NOT touched — it stays
`review_state=review_pending / signed=false`; recording the sign-off in `handoff.json` is the parent/owner's
action (reviewer never self-signs the executor's handoff).

## VERDICT: **ACCEPT** — all 7 verification gates pass; 5 findings (0 blocking, 1 LOW, 4 INFO); 4 items unverified.

Scope-if-accepting (parent's commit plan, endorsed): `changes.diff` = exactly the 2 files → parent applies
(RF commit) after REST-A/REST-B land together for a single ratchet-green push; KEEP-RED row-pass posture
transcribed (sibling rows = REST-A: F2/F3/F5, REST-B: F4/F6/F7); the 2 pre-existing family failures are
already routed to RF-STEP9-TRIAGE (cited in §4); predecessor-death lineage disclosed (oracle §0 + APPEND A,
prefix-proven verbatim).

---

## 1. Deliverables (9/9 present)

| # | deliverable | live check |
|---|---|---|
| 1 | `oracle.md` | predecessor `RF-RATCHET-FIX/a20260923-01/oracle.md` content is a byte-exact **prefix** of this oracle's §0 (`StartsWith` = True; solely a `---` separator + blank line precede the dated `APPEND A (2026-09-23 21:38 +01:00)`). Frozen-first ordering: oracle mtime `21:41:34` < first judged-run raws `red_verbatim_command.txt 21:45:57` < `ratchet_red_judged.txt 21:47:38` |
| 2 | `binding.json` | written `21:43:13`, preceding the first judged run and each later judged run; pins 6 key shas, 2 in-scope rows, 6 out-of-scope rows, golden-lock gate, READ-ONLY vehicle |
| 3 | `commands.md` | chronological log §§1–9; verbatim `-B` rejection + judged equivalents documented |
| 4 | `decision.md` | CC table §0, golden-lock verdict §1, hunk→helper map §2, families §3, GREEN/KEEP-RED §4, mutations §5, disclosures §7 |
| 5 | `handoff.json` | `status=complete`, `review_state=review_pending`, `signed=false`, `blockers=[]` |
| 6 | `recovery.md` | resume point + re-verify recipe + hard constraints |
| 7 | `changes.diff` | 12078 bytes, exactly 2 file pairs (see §2 below) |
| 8 | `evidence/` | 6 subdirs present: `red`(2) `measure`(9) `green`(4) `mutation`(9) `families`(2) `integrity`(6) |
| 9 | `iso/` | 4 pinned byte copies: both `.baseline` + both `.refactored` |

### 1a. changes.diff roundtrip — reviewer's own difflib roundtrip into %TEMP% (two independent methods)

- Method A (difflib, `%TEMP%\rev_roundtrip.py`): regenerating `difflib.unified_diff(baseline, refactored, n=3)`
  from `iso/*.baseline` vs `iso/*.refactored` reproduces `changes.diff` **byte-exactly** (`True`, 12078 == 12078);
  parsing the stored hunks and applying them to the baselines yields bytes identical to
  `iso/*.refactored` AND to the judged `%TEMP%\rf2-iso-work` files:
  `confidence.py sha 2c954c3d…663e4` / `model_extensions.py sha cfcca87a…ebc085` on each of the three sides.
- Method B (`git -c core.autocrlf=false apply --check` then `apply` in a fresh non-repo `%TEMP%\rev-apply`
  seeded with the baselines): `CHECK_EXIT=0`, `APPLY_EXIT=0`, applied hashes == the same two shas.
- File set: diff headers = `a/scripts/analysis/confidence.py`, `a/scripts/model_extensions.py` — **exactly 2 files**;
  no test files, no marker/skip/xfail/cap content anywhere in the diff (grep: 0 code matches; matches found
  were confined to prose lines in md/json files).

## 2. Both rows — live re-hash + ratchet metric re-measured with BOTH implementations

Live RF re-hash (reviewer, SHA-256):

| file | live sha256 | card value | matches |
|---|---|---|---|
| `scripts/analysis/confidence.py` | `e5c0b1ac7cf91ca85b9f3e78b7ccfb35ddf963f305579cbd5e8195490103c5d7` | binding `key_shas_before` == frozen_sha_proof before/after | YES (RF source untouched — delivery is `changes.diff`) |
| `scripts/model_extensions.py` | `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` | binding before == frozen_sha_proof after | YES |
| `tools/tests/test_complexity_ratchet.py` | `eb1a36cfd54a8b96e3b5dca6ca4b7a89ca6b1e1605d22eedb69f643245edd10a` | frozen BEFORE == AFTER == oracle §4 expected | YES |
| `tests/golden_behavior_hashes.json` | `4e68b98cc16027bc370900e346f8554245e2e2155d0e22edc4beadba5f2933b5` | binding == frozen_sha_proof after (unchanged) | YES |
| `tests/test_model_extensions_anchor.py` / `tests/test_golden_behavior_lock.py` | `954e08ac…524f9` / `b1271784…c88` | binding == frozen_sha_proof after | YES |

Refactored "after" bytes live solely in `iso/*.refactored` + `changes.diff` + judged `%TEMP%\rf2-iso-work`
(the three copies sha-equal: `2c954c3d…`, `cfcca87a…`) — RF working tree intentionally still holds the RED state.

Metric re-measured by the reviewer with BOTH implementations (import of the test module's
`_mccabe`/`_max_complexity`, and a fully inlined twin) — implementations agree on each of the 6 measured files:

| target | FILE_MAX (import) | FILE_MAX (inlined) | card claim | §0 table |
|---|---|---|---|---|
| live confidence.py (HEAD baseline) | 32 | 32 | 32 before | matches |
| live model_extensions.py (HEAD baseline) | 27 | 27 | 27 before | matches |
| refactored confidence.py | **17** (≤ 23) | **17** | 17 after | matches |
| refactored model_extensions.py | **8** (≤ 10) | **8** | 8 after | matches |

Per-function CC of the refactored files matches decision §0 row-for-row (confidence:
`parameter_revenue_weights 17, _limitations 16, _evidence_quality 7, _sensitivity_metrics 5,
_explicit_model_share 3, _quality_gates 3, calculate_confidence 3` → FILE_MAX 17;
model_extensions: `_check_driver_bounds 8, build_extension_specs 8, _validate_calculated_output 7,
_arr 5, _resolve_paths 5, _check_driver_numeric 5, _validate_driver_paths 4, _validated_calculator 3,
…` → FILE_MAX 8). Baseline rows match too (`calculate_confidence 32`, `_validated_calculator 27`).
`FROZEN_MAX['analysis/confidence.py']=23`, `forecast/calc.py=21`, `NEW_FILE_MAX=10` read live from the
frozen test module; frozen-table sha before == after == `eb1a36cf…` (re-hashed live).

## 3. Golden-lock NO-CONFLICT verdict — CONFIRMED (static + runtime, reviewer re-ran both)

- Static: `tests/test_model_extensions_anchor.py:126-139` read line-by-line — computes
  `digest = hashlib.sha256(raw).hexdigest()` then asserts the single predicate `len(digest) == 64`; no pinned digest
  anywhere in the function (remaining asserts: file exists, non-empty, `model_registry.py` still names
  `build_extension_specs`). `tests/test_golden_behavior_lock.py` docstring + code: pins
  `canonical_sha256(run_forecast(...))` per model family = **behavior** lock, refreshed solely via
  `--update-golden`. No source-byte lock on `model_extensions.py` → verdict NO CONFLICT is correct.
- Runtime (reviewer, fresh basetemps): `python -B -m pytest tests/test_golden_behavior_lock.py
  tests/test_model_extensions_anchor.py -q -p no:cacheprovider` → **7 passed, 17 subtests** on live
  (pristine) tree and **7 passed, 17 subtests** on the refactored `%TEMP%\rf2-iso-work` tree.
  `golden_behavior_hashes.json` sha unchanged live (row above).
  Their raws `golden_lock_before.txt`/`golden_lock_after.txt` both read `7 passed, 17 subtests`.
  → matches the card's "7 passed/17 subtests BEFORE and AFTER" claim exactly.

## 4. Zero-behavior — reviewer ran the documented 24-file family command, both sides

Command = decision §3's 24-file union (17 confidence-touching + 7 model_extensions importers),
`-q -p no:cacheprovider --basetemp %TEMP%\rev-fam-{after,before}-bt`, `PYTHONIOENCODING=utf-8`:

- **AFTER** (judged refactored tree `%TEMP%\rf2-iso-work`): `2 failed, 283 passed, 149 subtests passed in 59.86s`,
  failures = `tests/test_zr708_backtest_reverify.py::test_c2_accuracy_record_consumed_by_confidence` +
  `tests/adversarial/test_receipt_attacks.py::ReceiptAttackTests::test_context_fabrication_is_rejected_by_final_validation`.
- **BEFORE** (pristine `%TEMP%\rf2-iso`, byte == live per `iso_vs_live_hashes.txt` + reviewer re-hash):
  `2 failed, 283 passed, 149 subtests passed in 144.24s`, **identical failure pair**.
- Their raws `family_before_stdout.txt` / `family_after_stdout.txt`: same totals (`2 failed, 283 passed,
  149 subtests`), same pair, 66.97s / 283.99s. Reviewer's before/after both reproduce the claim.

Cross-check of the 2 failures against RF-STEP9-TRIAGE (already-routed finding):
`RF-STEP9-TRIAGE/a20260923-01/oracle.md` §1 lists them as scope items
**#1** `tests/adversarial/test_receipt_attacks.py::test_context_fabrication_is_rejected_by_final_validation`
(line 14) and **#12** `tests/test_zr708_backtest_reverify.py::test_c2_accuracy_record_consumed_by_confidence`
(line 25); its §2 explicitly routes ratchet-count failures OUT to RF-RATCHET-FIX; its raws
(`win_head_*`, `wsl_head_*` for both files) show both failing at HEAD pre-fix, and its `decision.md`
rows 1/12 classify them as pre-existing (E27 attestation gate; 70dd9f6e future-leak fixture) with
small-safe-fixes already staged in TRIAGE's own `changes.diff`. → the pair is pre-existing and routed.

## 5. GREEN / KEEP-RED posture — real runs by the reviewer

- Judged RED on live RF: `2 failed` with exactly `analysis/confidence.py max 32 > 23` and
  `model_extensions.py max 27 > 10` (matches oracle §2 + `ratchet_red_judged.txt`).
- After-refactor run on `%TEMP%\rf2-iso-work`: `1 failed, 1 passed` —
  **`test_new_files_stay_simple` FULLY GREEN** (its pass = the `.` in `F.`),
  frozen test **first-aborts on the NEXT row**: `AssertionError: 22 not less than or equal to 21 :
  forecast/calc.py max 22 > 21` — exactly the expected KEEP-RED shape (F1 executed-and-passed inside the
  real loop; remaining RED owned by REST-A).
- Full-row scan (reviewer, both trees, no first-abort masking): live = 7 frozen violations + 1 new-file
  violation, row-by-row identical to oracle §3's table (F1 32/23, F2 22/21, F3 17/9, F4 28/9, F5 114/88,
  F6 23/6, F7 16/10, N1 27/10); refactored tree = **confidence row ok (actual 17 ≤ 23)**, model_extensions
  violation gone (0 new-file violations), remaining = exactly F2–F7 (6 rows) routed to REST-A/REST-B.
  The attempt's own import-based scan + inlined twin also re-run by reviewer: identical outputs.
- **MUTATION re-run (reviewer, independent)**: regenerated both mutants from the judged WORK tree with
  `make_mutants.py`'s exact algorithm → byte-identical to their pinned raws
  (`confidence_mut1.py 5476b81d…6dc97`, `model_extensions_mut2.py 153ec474…ed2a4e`);
  measured with the test's own metric: MUT1 `calculate_confidence CC=24, FILE_MAX=24`;
  MUT2 `_validate_driver_paths CC=11, FILE_MAX=11`.
  Ran the ratchet in cloned `%TEMP%\rev-mut1` / `rev-mut2` trees:
  - MUT1 in → frozen message flips to `analysis/confidence.py max 24 > 23` (`1 failed, 1 passed`);
    restore → flips back to `forecast/calc.py max 22 > 21`. **Both directions proven.**
  - MUT2 in → new-file test flips to `model_extensions.py max 11 > 10` (`2 failed`);
    restore → `1 failed, 1 passed` (new-file GREEN again). **Red→green proven.**
  Their raws (`confidence_mut1_cc/_ratchet/_restored_ratchet`, `model_ext_mut2_cc/_ratchet/_restored`)
  match these outcomes; restore proofs consistent.
- **No skip/xfail/marker additions**: grep over the attempt (diff, iso copies, md/json) — 0 code matches;
  ratchet test sha unchanged; FROZEN_MAX/NEW_FILE_MAX values unchanged (read live: 23 / 10 / calc 21).
- `ruff check` on the judged refactored files: `All checks passed!` (reviewer re-ran, exit 0).

## 6. Disclosures — each recorded (verified at the stated location)

1. **`-B` pytest quirk (exit 4)**: `commands.md §1` (raw + `exit 4, unrecognized arguments: -B`),
   `decision.md §7`, `oracle §7`/`§8`/APPEND A3, `handoff.notes_for_parent`, and the raw itself
   `evidence/red/red_verbatim_command.txt` (pytest usage error, `inifile: None`). Judged form
   `python -B -m pytest …` documented in `commands.md §2`.
2. **Porcelain = concurrent siblings**: `frozen_sha_proof.txt` porcelain_delta_note + `decision.md §7`.
   Reviewer re-computed baseline↔after delta: added lines belong to RF-STEP9-TRIAGE/BOOKKEEP-REPAIR/
   I-08-C-RESIDUAL/I-10-A/PUSH-LOGS-ARCHIVE/REGISTRY-CLOSURE/OWNER_DECISIONS.md — 0 production-source
   paths, 0 paths owned by this attempt (its files present in BOTH snapshots). Live `git diff` during this
   review shows the same sibling churn pattern growing; `git status --porcelain -- scripts tests tools` = empty.
3. **WSL-not-run (Windows-only decision)**: `decision.md §7` ("no WSL run executed"), `oracle §7`,
   `handoff.notes_for_parent`.
4. **Predecessor-refactor provenance**: `decision.md §7` — helper-extraction shape adopted from
   predecessor's in-flight `iso/*.fixed` after this attempt's own review + independent verification.
   Reviewer verified the stronger fact: `iso/*.refactored` are **byte-identical** to predecessor's
   `iso/*.fixed` (2c954c3d…/cfcca87a…), `.orig` == `.baseline` == live (e5c0b1ac…/9939480b…), and each
   judged run's raw post-dates this attempt's oracle freeze — consistent with the disclosure.

## 7. Boundary at close (re-checked after the reviewer's runs)

- Live RF vs HEAD: `git rev-parse HEAD` = `b7a6a116…` (== binding);
  `git status --porcelain -- scripts tests tools` = **empty**; `git diff --stat HEAD -- scripts` = **empty**
  → live `scripts/` tree holds **0 changed files** (see finding F-REV-RF2-05 for the phrasing nuance);
  whole-repo `git diff --name-only HEAD` = the sibling planning files (OWNER_DECISIONS, REMEDIATION_REGISTER,
  TRIAGE oracle, findings/progress/task_plan, RESPONSES, two other attempts' review/handoff) — 0 owned by
  this attempt, 0 under `scripts|tests|tools`.
- Frozen test file untouched (sha `eb1a36cf…` live, re-hashed).
- Network verbs: grep over the whole attempt tree for `Invoke-WebRequest|curl|wget|pip install|
  requests.(get|post)|urllib` = **0 matches**; measure/mutation scripts are stdlib-only on re-read.
- State-changing git: grep for `git commit|add|checkout|reset|stash|switch|merge|rebase` over the attempt =
  **0 matches**; documented git verbs are read-only (`log/-1`, `status --porcelain`, `diff --no-index`,
  `apply --check`). One scratch `git init` exists at `%TEMP%\rf2-applycheck` (finding F-REV-RF2-04) —
  outside RF, RF's `.git` untouched.
- Reviewer's own writes: `%TEMP%\rev-*` scratch (scripts, trees, basetemps) + these 2 report files.
  Attempt dir went 43 → 45 files (the 2 reviewer files); RF product sources never opened for write.

---

## FINDINGS

- **F-REV-RF2-01 (LOW) — predecessor inventory count unit.** APPEND A0 says "38 files under
  `RF-RATCHET-FIX/a20260923-01/`"; live recount = **29 files** (37 recursive entries + root = 38 entries).
  The number counts directories/root as entries, not files. Related precision nit: A0 says
  "`binding.json` … never written" — true for that filename; the predecessor left a
  `binding_before.json` pre-freeze artifact instead. No impact on evidence or the fix; suggest parent
  transcribes "38 entries (29 files)" in future lineage references.
- **F-REV-RF2-02 (INFO) — golden-lock raw ordering.** `golden_lock_before.txt` mtime `22:18:58` is
  LATER than `golden_lock_after.txt` (`22:16:24`) and later than the refactor greens (22:04–22:15);
  the static gate was genuinely first (`binding.json` 21:43:13). Both raws report `7 passed, 17 subtests`,
  and the reviewer re-ran both trees independently with identical results — verdict unaffected; the
  before/after file mtimes stand inverted relative to their names.
- **F-REV-RF2-03 (INFO) — delivered bytes originate from the predecessor.** `iso/*.refactored` ==
  predecessor `iso/*.fixed` byte-for-byte (disclosed as provenance in decision §7). The successor's
  contribution = adoption + full independent re-verification (the judged runs are post-freeze, each re-run by this
  reviewer). Lineage is honestly disclosed; flagging so the parent's commit message can carry it.
- **F-REV-RF2-04 (INFO) — undisclosed scratch git init.** `%TEMP%\rf2-applycheck/.git` implies a
  `git init` in scratch not itemized in `commands.md` (which documents `diff --no-index`) or `recovery.md`
  (which documents `apply --check`). Harmless (scratch directory; reviewer reproduced the apply check WITHOUT
  any init — `git apply` works in a plain directory, exit 0).
- **F-REV-RF2-05 (INFO) — boundary phrasing vs live state.** Parent's gate text said "live scripts/ tree =
  only the 2 files changed vs git HEAD"; measured live state = **0 changed files**. This matches the card's
  contract (RF sources READ-ONLY; the 2-file change set exists solely in `changes.diff`, which the parent
  applies at commit time). Not a card violation — recorded so the parent does not read "0 changes" as a
  missing delivery.

## UNVERIFIED (declared, with reason)

1. **WSL arm** — not executed by card-optional choice; Windows-only decision disclosed (§6.3). No WSL
   evidence exists to re-verify.
2. **Register §55 origin rows for the out-of-scope violations (F2–F7)** — re-verification covered the 2 in-scope origins,
   checked live (`70dd9f6e` last-touches `scripts/analysis/confidence.py` 2026-09-20 15:04; `5db4734a`
   = sole commit touching `scripts/model_extensions.py`; both commits exist). F3–F7 provenance accepted
   from oracle §3 without re-derivation (out of card scope).
3. **Predecessor raws' contents** — treated as READ-ONLY baseline: inventoried, hashed, oracle compared
   byte-wise, iso artifacts compared; their internal evidence files were NOT re-executed (solely the equivalence
   was re-proven from scratch by this review).
4. **REST-A / REST-B card existence and assignments** — routing rows read from `binding.json`/oracle §3;
   sibling card files not inspected (outside this attempt's boundary).

## REPRODUCTION (reviewer's own commands, each re-runnable)

```
python -B %TEMP%\rev_roundtrip.py                 # difflib regen + hunk-apply roundtrip (byte-exact)
python -B %TEMP%\rev_cc.py                        # dual-impl CC: live 32/27, refactored 17/8
python -B %TEMP%\rev_scan.py <repo-root>          # full-row scan, no masking (live & WORK trees)
python -B %TEMP%\rev_mutant.py                    # mutant regeneration == pinned raws (sha equal)
cd RF;        python -B -m pytest tools/tests/test_complexity_ratchet.py -q -p no:cacheprovider --basetemp %TEMP%\rev-red-live-bt   # 2 failed (32>23, 27>10)
cd %TEMP%\rf2-iso-work; python -B -m pytest tools/tests/test_complexity_ratchet.py -q -p no:cacheprovider --basetemp %TEMP%\rev-green-work-bt  # 1 failed,1 passed (calc 22>21)
cd RF;        python -B -m pytest tests/test_golden_behavior_lock.py tests/test_model_extensions_anchor.py -q -p no:cacheprovider --basetemp %TEMP%\rev-gold-live-bt   # 7 passed, 17 subtests
cd %TEMP%\rf2-iso-work; <same golden pair>        # 7 passed, 17 subtests
cd %TEMP%\rf2-iso{-work}; python -B -m pytest <decision §3 24 files> -q -p no:cacheprovider --basetemp %TEMP%\rev-fam-{before,after}-bt
                                                   # both: 2 failed, 283 passed, 149 subtests (same pair)
cd %TEMP%\rev-mut{1,2}; python -B -m pytest tools/tests/test_complexity_ratchet.py -q ...   # MUT1 24>23 flip / MUT2 11>10 flip + restores
git -C RF status --porcelain -- scripts tests tools  # empty
git -C RF diff --name-only HEAD                     # sibling planning files, 0 product files
```

— end of reviewer report —
