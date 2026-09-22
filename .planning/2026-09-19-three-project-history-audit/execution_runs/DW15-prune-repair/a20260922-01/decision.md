# DW15-REPAIR decision.md — implementer's card decision (NOT a signature)

Card: `DW15-REPAIR` · attempt `a20260922-01` · date 2026-09-22 · role: implementer.
**Status: `review_pending`. The implementer does not sign acceptance; an independent
data-recovery reviewer must review and re-sign. `disclosure_adaptation = unmapped`,
`accuracy = unproven`.**

## 1. The owner ruling, restated in my own words

On 2026-09-22 the owner ruled (verbatim, `PLAN/OWNER_DECISIONS.md` §15):
「A-1，授权"修代码"卡」 — and re-confirmed it §16 as `A-1 = b: 允许修 prune 代码，
不授权执行 prune`.

What that grants **this** card:

- I am authorized to **repair the code** — the two retired-evidence scripts
  (`prune_retired_evidence.py`, `archive_retired_evidence.py`) — in an **isolated
  copy**, following the proposal I-15-A already documented in its `decision.md`
  (the source of truth for what is broken and how the repair should behave).

What it explicitly does **not** grant, and which I therefore did **not** do:

- **No production prune.** Not a dry run, not an apply, nothing that could delete
  or archive real evidence data ran during this card — not once, not against any
  real catalog or archive root.
- **No promotion.** The fix lives in `<attempt>/iso/fixed/`; the product repos
  stayed read-only in place (hash-verified unchanged). Promoting the fix into the
  repo is a separate owner decision.
- **No self-signing.** After this repair, a **data-recovery reviewer must re-sign**
  before any real execution can happen. That re-sign is a separate future step,
  not part of this card, and is expected to remain outstanding when this card
  hands off.

## 2. The five defects and how each was repaired (property → implementation)

Oracle frozen **before any run**: `oracle.md` (sha256
`003f48da31f131a4b35604807cb1c37aef968c413edfb4d0181854f2462e0574`).

| # | Defect | Property frozen in oracle | Repair (in `iso/fixed`) |
|---|---|---|---|
| 1 | 空目录也删 | only a **verified** archive manifest may authorise deletion; empty dir / bare snapshot / broken snapshot / "dir is old" each authorise nothing; when a verified due manifest exists, delete exactly the authorised still-retired digest-matching rows | `_load_verified_archives()` re-reads every `*.manifest.json`: schema, `ok`, archive sha256+size, full gzip re-read with per-row digest recomputation; unverified ⇒ `due=false`, apply deletes 0. Selection = manifest ids ∩ live rows with identical digest ∩ `source_status='retired'` |
| 2 | 同日覆写 | two runs at the same instant each keep their own complete output; run-1 bytes/receipts unchanged after run-2 | archive: per-run `retired-evidence-<uuid>.jsonl.gz` (never a shared per-day name, publish is create-if-absent); prune: per-run `prune-retired-<uuid>.json` receipt, only its own run ever rewrites it (temp+replace) |
| 3 | 时钟取目录名 | (a) **no system-clock API** may appear in either module (static scan) — path components come only from the injected `now` or a non-clock token; (b) retention = `now − manifest.verified_completed_at`, never a directory/file name | both signatures take a **required** timezone-aware `now` (TypeError otherwise); date dir from `now`, token/receipt names from uuid4; `_is_due()` parses `verified_completed_at` only; zero `datetime.now/utcnow/today/gmtime/strftime/time()/fromtimestamp` occurrences (scan-proven) |
| 4 | TOCTOU | the state a delete acts on is re-verified **atomically with** the delete; any drift ⇒ whole apply refused, 0 deleted, never silent narrowing | dry-run freezes `PrunePlan` (ids + digests + archive sha256s + plan hash); apply inside `CatalogOperationLock` re-verifies archive bytes and every planned row's digest/status **before the first delete** (`PruneRefused` on any mismatch), then each batch re-reads and re-verifies its rows **in the same SQLite transaction** that deletes them |
| 5 | 崩溃后不可恢复 | kill during snapshot write ⇒ no truncated file at any published path, prior snapshot byte-identical, evidence present; kill between snapshot-write and delete ⇒ pending receipt names the full plan; kill after batch 1 ⇒ every deleted id ⊆ receipt plan ∩ snapshot | archive: temp file → fsync → full re-read verification → atomic create-if-absent publish (the old `archive_retired_evidence.py:65` `gzip.open(..., "wt")` truncation is gone); prune: **pending receipt before the first delete**, atomic rewrite after every committed batch, `status: complete` at the end |

I-15-A's D-W15-4 left the receipt **durability medium** (DB table vs JSON file
under `artifacts/gates`) for the reviewer to choose. Because the owner's ruling
covers "修代码" only and this medium is part of the unsigned D-W15 set, I
implemented the **JSON-file-under-`artifacts/gates` option** (the lighter of the
two documented options) so the crash-safety property is testable now; **the
reviewer may replace it**, and this choice is declared as an open item in
`handoff.json` — not treated as decided.

## 3. RED → GREEN per defect

15 tests, one suite, run against two trees (variant bound by `DW15_VARIANT`):

- **RED (original code)**: `iso/baseline` — byte-identical to production
  (`2358c73b…` / `143fef01…`, matching I-15-A's declared hashes) —
  **15 failed / 0 passed**, rc=1, each failure on the behavioural assertion of its
  own frozen property (e.g. "an empty old directory authorised the deletion of
  ['a1','a2','a3','b1']"; "the second apply in the same second overwrote the first
  receipt"; "a published snapshot is not crash-safe: 2 rows, expected 4").
  Evidence: `evidence/red_baseline_stdout.txt`.
- **GREEN (repaired code)**: `iso/fixed` — **15 passed / 0 failed**, rc=0.
  Evidence: `evidence/green_fixed_stdout.txt`.

Per defect: D1 t_d1_1..4 RED→GREEN · D2 t_d2_1..2 RED→GREEN ·
D3 t_d3_1..4 RED→GREEN · D4 t_d4_1..2 RED→GREEN · D5 t_d5_1..3 RED→GREEN.

## 4. Five-mutation matrix (declared in oracle §3 BEFORE runs; observed == declared)

| mutation | revert | declared RED | observed RED | == |
|---|---|---|---|---|
| M1 | D1: no verified manifest ⇒ original authorisation (dir-age due, delete all retired) | t_d1_1, t_d1_2, t_d1_3 | t_d1_1, t_d1_2, t_d1_3 | ✅ |
| M2 | D2: fixed output names (`retired-evidence.jsonl.gz`, `prune-retired.json`), overwrite allowed | t_d2_1, t_d2_2 | t_d2_1, t_d2_2 | ✅ |
| M3 | D3: retention clock = oldest archive **directory name vs `datetime.now`** (manifest gate kept) | t_d3_1, t_d3_2, t_d3_3 | t_d3_1, t_d3_2, t_d3_3 | ✅ |
| M4 | D4: pre-delete and in-transaction row re-verification removed (plan trusted) | t_d4_1, t_d4_2 | t_d4_1, t_d4_2 | ✅ |
| M5 | D5: snapshot written straight to its published path; no pending receipt before the first delete | t_d5_1, t_d5_2, t_d5_3 | t_d5_1, t_d5_2, t_d5_3 | ✅ |

Built by `harness/make_mutants.py`: each anchor must match **exactly once** or
the mutant is not built. Machine evidence: `evidence/mutation_matrix.json`;
raw outputs `evidence/mutant_m*_stdout.txt`.

Not mutation-bound, declared so in oracle §3: t_d1_4 (verified-manifest path,
outside M1's fallback) and t_d3_4 (archive-side clock, outside M3's prune-side
revert) — both RED on baseline, GREEN under all five mutants, exactly as declared.

**Instrument fixes during the card (harness only, declared sets never changed):**
(1) t_d5_1's crash wrapper initially lacked the context-manager protocol — fixed
so the baseline failure is behavioural, not a TypeError; (2) `receipts_for()`
glob widened `prune-retired-*.json` → `prune-retired*.json` so the instrument can
observe M2's reverted fixed receipt name. Both are test-harness changes; the
frozen oracle expectations and mutation declarations were untouched.

## 5. Zero real data touched — explicit statement

- Every catalog, archive, manifest, and receipt exercised by this card was
  **synthetic**, created by the tests themselves under `%TEMP%` (pytest
  `tmp_path`), guarded by `guard_scratch()` (BINDING-REFUSED outside
  `%TEMP%`/attempt or if the path contains `.source_catalog`).
- **No production prune or archive ran** — not dry-run, not apply. The production
  catalog (49.7 GB) was never opened, not even read, by this card.
- Production repo files were **read only to copy them into `iso/`**; after the
  whole attempt the production hashes are **unchanged**
  (`prune 2358c73b…`, `archive 143fef01…` in `Projects\company-wiki` **and** in
  the `.review-zr407-20260818` snapshot); `worker_control.json` hash is identical
  to I-15-A's record (desired_state still paused); no git write operation was
  performed in any repo; no other card's attempt or frozen artifact was modified.

## 6. Remaining gaps (expected, incl. the reviewer re-sign)

1. **Data-recovery reviewer re-sign is OUTSTANDING and expected to remain so**
   (owner §16 `E-4`: D-W15 production execution stays unsigned; A-1's grant ends
   at repairing code). Nothing here authorises a real prune.
2. **Promotion** of `iso/fixed` into `company-wiki` is a separate owner decision;
   the repo still contains the defective originals.
3. **Receipt durability medium** (JSON file implemented; DB table was the other
   documented option) — reserved for the reviewer per I-15-A D-W15-4.
4. **API changes** are breaking: `now` is now required and apply can take a
   frozen `plan`; the product's own contract tests
   (`test_source_catalog_prune_retired.py` encodes the *wrong* oracle per
   I-15-A; `test_source_catalog_archive_retired.py` calls without `now`) were
   deliberately NOT touched and will need their replacement at promotion.
5. **Scale unproven**: fixtures are 5-span catalogs; nothing here says anything
   about the real 25.7M-row / 49.7 GB case (manifest verification re-reads the
   whole snapshot at plan time).
6. **Old archives without a manifest** stay unusable for prune (W15-R8 forbids
   guessing; no upgrade path was invented here).
7. **`catalog_identity` binding** is minimal (`<db filename>:<schema version>`);
   I-15-A's fuller identity (db file identity) is not implemented.
8. **No restore CLI** was invented (W15-R7 restorability is shown via manifest
   digests only; see `recovery/README.md`).
9. W15-R6 idempotence and W15-P1 exact-set behaviour are covered by these
   tests; R6's "second apply of the same plan" is exercised via t_d2_2's second
   apply, but no dedicated multi-plan interleaving test exists.
