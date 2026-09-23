# PROMOTION-EXEC a20260922-01 — Frozen Oracle (written BEFORE any production write)

Owner ruling: `OWNER_DECISIONS.md` §十八 verbatim「B: 全批」(2026-09-22) — ALL promotion rows
of the approved manifest are executed by this card. The ruling lifts the session's
"生产零合并" prohibition **FOR THE ITEMS LISTED IN THIS ORACLE ONLY**, with per-item
verification. No git commits (parent commits after this card's evidence).

Contract: `../PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md`
(19190 B, sha256 `6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac`
— VERIFIED at run start, byte count and hash both matched).

Frozen rules (this oracle is the per-row expectation set; nothing below may be
edited after the first production write):

1. Write boundary: ONLY the target paths listed per row below may be written.
   Everything else READ-ONLY. company-wiki's 3 pre-existing dirty files
   (CLAUDE.md `963869fa…`, README.md `302bd10b…`, src/…/artifact_dag.py `0c8b1d6d…`)
   must remain byte-untouched. No git add/commit/restore/stash. No self-sign.
2. Per row: record live before-hash of EVERY target → copy source→target
   byte-exact → verify src sha == target sha → run the row's verification →
   append one line to `promotion_exec_log.jsonl` + save raw stdout under `evidence/`.
3. Failure rule: if a row's verification FAILS → STOP that row, revert the target
   to its before-image from `recovery/before_images/<row>/`, record the failure,
   continue the other rows, report. Never leave a half-promoted file.
4. Restore images for every modified target are copied to
   `recovery/before_images/<row>/` BEFORE the copy step (B-4 creates new files —
   its "revert" = delete the created files; documented in recovery/README.md).
5. Python: `C:\Miniconda\python.exe` (3.13.9, pytest 9.1.1, same interpreter the
   source cards used). ALL python/pytest runs use `-B` + `PYTHONPYCACHEPREFIX`
   pointed into this attempt (so no `__pycache__` is written into any production
   tree) and `-p no:cacheprovider` + `--basetemp` inside this attempt.
6. Rows NOT executing: **B-6a** (I-14-F originals superseded by R1 — verify
   nothing of them lands), **B-7a/OQ-01** (tools/pre_push_gate.py belongs to the
   concurrent GATE-OQ-FIX card — verify untouched by this card), **B-6b/I-14-I**
   (target resolution rule below).

## Per-row frozen expectations

All source and target hashes below were measured LIVE by this attempt before any
write and match the manifest exactly.

### B-1 — RF revenue 安全三项 ← B1 iso fixed3
| file | src (iso fixed) | target before | expected after |
|---|---|---|---|
| scripts/revenue_core.py | `8a761498…ac883` (25842 B) | `1821fd2a…beae` (14136 B) | `8a761498…` |
| scripts/revenue_publication.py | `bc2bb4a3…fcd0` (24917 B) | `183803bb…48ba` (10681 B) | `bc2bb4a3…` |
| scripts/revenue_report.py | `212f0059…7d3b` (73973 B) | `a85fb484…971f` (69765 B) | `212f0059…` |
- Verification: src==target sha; `python -m py_compile` rc 0; **I-08-C's 13-node suite**
  (`test_i08c_consumer_rejection.py` 13152 B / `3f83fdf2…`, verified live) with
  `RF_IMPORT_ROOT` pointed at the NOW-PROMOTED production tree → expect
  **13 collected / 13 passed / rc 0**.
  FROZEN FACT pair: pre-promotion card RUN-B (RF_IMPORT_ROOT unset → then-unfixed
  production) was **exactly {e11, e13} red, 11 passed, rc 1**
  (`scratch/fixround/runB_production.stdout.txt` in I-08-C's attempt); RUN-A on
  B1's fixed tree was 13/13 rc 0. Both facts recorded; this run must reproduce
  RUN-A's result against production bytes now equal to that fixed tree.

### B-2 — RF company_wiki_source + source_preparation ← B3 / B3-PREREQ (same batch)
| file | src | target before | expected after |
|---|---|---|---|
| scripts/company_wiki_source.py | `7d1bd8f9…48ce` (B3 iso/fixed, 20545 B) | `225fecdd…4294` (19364 B) | `7d1bd8f9…` |
| scripts/source_preparation.py | `91a6dc32…bf4d` (B3-PREREQ iso/fixed2, 9921 B) | `37a3eeae…e2a7` (9908 B) | `91a6dc32…` |
- **Repo-by-hash resolution (manifest constraint)**: live probe found
  `37a3eeae…` in `revenue-forecast/scripts/source_preparation.py` and CONFIRMED
  `company-wiki/src/company_wiki/source_catalog/source_preparation.py` ABSENT
  ⇒ the SP target is the RF path; both B-2 files ride the same batch as required.
- Verification: src==target sha both files; py_compile rc 0 both;
  REM-49 zero-behaviour-delta proof: unified diff vs the B3-fixed baseline
  (`37a3eeae…` before-image) must be **comment-only (line 138 region)**,
  `ast.dump` parity equal, `compile()` ok; **FC-904** (lives in RF, not CW —
  `tests/test_fc904_artifact_selection.py`) → expect **11 passed / rc 0**;
  B3-PREREQ card-cited `tests/test_rem49_comment_fix.py` (read-only run in its
  own attempt) → expect **5 passed / rc 0**.

### B-3 — CW observability 脱敏 `[^\s]+` ← I-14-D r6 tree
| file | src (r6) | target before | expected after |
|---|---|---|---|
| src/company_wiki/source_catalog/observability.py | `2f644994…2464` (43746 B) | `a73826aa…be5a` (30087 B) | `2f644994…` |
- Verification: src==target sha; py_compile rc 0; module imports cleanly
  (`import company_wiki.source_catalog.observability`, read-only, `-B`).
- Carried (recorded, not re-verified here): r7 = record-fix only, r6 = code
  deliverable; F-REV-D-02 dead `_VALUE` hazard, F-REV-D-03 atom-table gap,
  C12 precondition, 95-row rule table rc-3 by design.

### B-4 — CW root conftest.py + tests/contract/test_short_basetemp_convention.py ← I-14-F-R1 (NEW FILES)
| file | src (R1 iso/tree) | target before | expected after |
|---|---|---|---|
| conftest.py (CW root) | `a908c9da…4249` (9031 B) | **ABSENT** (live-confirmed) | created, `a908c9da…` |
| tests/contract/test_short_basetemp_convention.py | `1fd4e0d8…a835` (9899 B) | **ABSENT** (live-confirmed) | created, `1fd4e0d8…` |
- Verification: created files byte-equal to source (sha); py_compile rc 0 both;
  place-holder: company-wiki suite runs belong to the CW side (CF-I14FR1-3
  broader sampling obligation stays open pre-merge; RF gate runs at batch-4 push).

### B-5 — CW prune/archive 五缺陷 ← DW15 iso/fixed (CODE PROMOTION ONLY)
| file | src (DW15 fixed) | target before | expected after |
|---|---|---|---|
| src/company_wiki/source_catalog/prune_retired_evidence.py | `0c99bbe0…90b0` (23115 B) | `2358c73b…ae46` (4658 B) | `0c99bbe0…` |
| src/company_wiki/source_catalog/archive_retired_evidence.py | `bbe855e4…28ac` (9894 B) | `143fef01…53e0` (3291 B) | `bbe855e4…` |
- Verification (DW15's 15-test harness CANNOT run against production — its
  guard `DW15-neg-bind` refuses any path outside %TEMP%/attempt or containing
  `source_catalog`): (a) diff-equality proof src==target byte-exact (sha +
  length), (b) py_compile rc 0, (c) both modules import cleanly read-only.
- **E-4 FROZEN: this row is code promotion ONLY — production prune/archive
  EXECUTION (dry-run included) remains UNAUTHORIZED; data-recovery reviewer
  re-sign stays UNSIGNED.** Breaking-API note rides: `'now'` now REQUIRED,
  `apply` accepts a frozen plan; product contract tests encode the wrong oracle
  (I-15-A) and are UNTOUCHED — they need replacement at promotion.

### B-6b / I-14-I coupling — natural_window.py (RESOLVE FIRST, wave order I-14-B → I-14-I)
Resolution rule (this card): read I-14-B's OWN card + carriers.
- `execution_v2/card_I-14-B.md` (13 lines, read in full): declares computation/
  evidence obligations only — **NO production target path anywhere**.
- I-14-B binding.json: `iso/natural_window.py` = "attempt-local subject under
  test … NOT product code"; `product_repos_read_only`; D-6 (any production-tree
  write) explicitly NOT granted.
- I-14-B handoff: "any production-tree write permission (D-6)" in not_granted.
- Manifest B-6b: production target UNRESOLVED (live probes found no production
  `natural_window.py` in RF scripts/ or CW src/, only plan-internal iso copies).
- **FROZEN OUTCOME: card declares NO production target ⇒ mark BLOCKED-unresolved
  and SKIP I-14-I (no guessing paths). NO natural_window.py may exist in either
  production tree after this run (verified negative check).**

### B-6a — I-14-F originals: DO NOT PROMOTE (verify nothing lands)
- Expected after-run state: CW `conftest.py` == R1 `a908c9da…` (NOT I-14-F
  `c22be9f3…`), CW unit test == R1 `1fd4e0d8…` (NOT I-14-F `b0402b56…`).

### B-6c — RF model_registry 省缺即抛+语义角色 ← I-10-B iso
| file | src | target before | expected after |
|---|---|---|---|
| scripts/model_registry.py | `62f864b9…5081` (30116 B) | `9ec65295…d17f` (26446 B) | `62f864b9…` |
- Verification: src==target sha; py_compile rc 0; focused RF model tests
  (source-card-cited concern): `tests/test_model_registry_contract.py`,
  `tests/test_model_economic_guardrails.py`, `tests/test_model_extensions.py`,
  `tests/test_model_extensions_anchor.py`, `tests/test_model_integration_bounds.py`
  → expect ALL PASS / rc 0.
- **E1E7 CONSEQUENCE NOTE (recorded, not acted on): after this row the four
  M-card oracle forward-disclosures (M05/M14/M20/M24 defaults-phase flips, M14
  E-5/E-6/E-7) become ACTIVE. The four oracle.md carriers were already landed
  append-only by E1E7-ERRATA-LANDING; this card does NOT touch them.**

### B-7a (OQ-01) — NOT in this card
- `tools/pre_push_gate.py`: before-hash recorded live
  `3df161a7ceea17de95b36845bdb3c4cee729dca215c56853868780dce7331484` (11654 B),
  already ` M` in porcelain BEFORE this run (concurrent GATE-OQ-FIX card owns it).
  This card must not write it; after-hash re-measured and compared — a change is
  attributed to the concurrent card, never to this one.

### Run-wide final checks (frozen)
- CW dirty-3 file hashes unchanged: CLAUDE.md `963869fa…`, README.md `302bd10b…`,
  artifact_dag.py `0c8b1d6d…`.
- RF porcelain after: exactly the 4 promoted RF files become ` M` under scripts/
  (+ pre-existing .planning modifications); no other production file touched.
- No `natural_window.py` in RF scripts/ or CW src/.
- Final I-08-C 13-node suite against the fully-promoted production tree → **13/13 rc 0**.

Frozen at: before the first production write; expectations above were derived from
live measurements + the verified manifest only.
