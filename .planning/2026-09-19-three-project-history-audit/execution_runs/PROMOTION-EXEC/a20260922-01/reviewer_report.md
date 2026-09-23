# PROMOTION-EXEC (a20260922-01) — Independent Reviewer Report

**Verdict: `accepted_scoped`** — 6 non-blocking findings (F-1..F-6), 8 unverified items (U-1..U-8).

Reviewer: independent, parent-dispatched (parent agent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`),
NOT the implementer. Date: 2026-09-22. This attempt does not self-sign (`handoff.json`:
`status=review_pending`, `implementer_signed=false` — read live).
This report and its `.sha256` sidecar are the only two files this review authored — domain: my own writes in this session (2 files).
Everything else this review touched was read-only — domain: tool scope of this review = read/grep/pwsh, 0 write operations.
All git usage by this review was read-only — domain: git subcommands invoked = `status --porcelain`, `log`, `rev-parse`, `hash-object`, `diff --no-optional-locks` (5 subcommands, 0 of them writes).
No test suite was re-executed — domain: method scope declared in §0 (read/grep/pwsh only), per brief.

**Acceptance scope (verbatim condition of this verdict):**
- B-6c is **NOT promoted** — blocked on test-battery wrong-oracle alignment
  (`tests/test_model_economic_guardrails.py` vs I-10-B semantics) — a separate card.
- B-6b has **no production target by card design** (I-14-B's 13-line card declares no production target path) ⇒ BLOCKED-unresolved;
  I-14-I skipped; nothing to promote.
- B-4's CW-suite sampling (**CF-I14FR1-3**) is still owed at the CW/batch-4 side (pre-merge).
- B-5 execution (prune/archive, dry-run included) remains **owner-unsigned / UNAUTHORIZED (E-4)**;
  this card promoted the CODE, never the execution (domain: E-4 code-only split).
- Git commits = **parent's** act, after this review; this card made no commits (domain: git log window 19:38–19:56 empty, both repos).

---

## 0. Contract re-hash (done first, never from memory)

- `PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md`: live sha256 =
  `6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac`, 19190 B — **matches** the
  expected value in the brief and the pins in `binding.json`/`oracle.md`.
- Manifest read in full (153 lines): rows B-1..B-7 with source/target hashes, B-6b target cell
  UNRESOLVED, B-6a superseded-by-B-4, B-6c carrying the E1E7 E-flips, B-6d UNRESOLVED.
  The attempt's per-row expectations in `oracle.md` are derived from it without drift.

## 1. Freeze-first ordering — corroborated from the attempt's OWN records (live stat)

| artifact (attempt's own) | CreationTime (live) | LastWrite |
|---|---|---|
| `oracle.md` | **2026-09-22 19:38:36.358** | 19:38:36.399 |
| `binding.json` | 2026-09-22 19:38:36.971 | 19:38:37.000 |
| `promotion_exec_log.jsonl` | **2026-09-22 19:40:59.184** (row-1 ts `2026-09-22T18:40:59.025Z` = 19:40:59.025+01:00) | 19:55:28.693 |
| CW `conftest.py` (first NEW-file production write, row B-4) | **2026-09-22 19:43:38.484** | 08:38:20 (source mtime preserved by copy) |
| CW `tests/contract/test_short_basetemp_convention.py` | 2026-09-22 19:43:38.490 | — |

- Ordering: **oracle 19:38:36.358 → binding 19:38:36.971 → execution log creation 19:40:59 →
  CW new-file first write 19:43:38** — exactly the ordering claimed; the parent-measured oracle
  CreationTime 19:38:36.358 reproduces to the millisecond on my own `Get-Item` read.
- In-attempt textual corroboration: `oracle.md` L12-13 ("nothing below may be edited after the
  first production write"), L156-157 ("Frozen at: before the first production write");
  `binding.json` `binding_status="bound (oracle.md frozen first; all hashes measured live before
  any production write)"`; `commands.json` `contract_verified_first.written_before_run`.
- No production-tree file's own timeline contradicts this: promoted-file LastWriteTimes are the
  source-iso times (copy preserves mtime); the only CreationTime-anchored writes are the two CW new files above (domain: NTFS CreationTime anchors, 2 files).
- Commit-level corroboration of "no git writes": RF `HEAD = 4b1c690b 2026-09-22T14:03:00+01:00`,
  CW `HEAD = f39bd5a 2026-09-19T08:42:58+01:00` — **no commit exists inside the 19:38–19:56 run
  window** in either repo (domain: `git log -3 --format=%cI`, read-only, live).
- Parent's independent RF porcelain at 19:35:20 CLEAN: **not found on disk** anywhere I searched
  (plan-root `*.md`, repo-root `*.md`) — recorded as U-1; it is parent-side evidence and is not
  needed for the ordering proof above, which stands on the attempt's own timestamps.

## 2. Row outcomes vs LIVE disk (hashes re-measured live during this review)

| row | live measurement (sha256 prefix / bytes) | expected | result |
|---|---|---|---|
| B-1 `RF/scripts/revenue_core.py` | `8a761498f5eb729e` / 25842 | `8a761498…` / 25842 | OK |
| B-1 `RF/scripts/revenue_publication.py` | `bc2bb4a33e36ed9a` / 24917 | `bc2bb4a3…` / 24917 | OK |
| B-1 `RF/scripts/revenue_report.py` | `212f00598feca408` / 73973 | `212f0059…` / 73973 | OK |
| B-2 `RF/scripts/company_wiki_source.py` | `7d1bd8f9d9122dc4` / 20545 | `7d1bd8f9…` / 20545 | OK |
| B-2 `RF/scripts/source_preparation.py` | `91a6dc32466e9d67` / 9921 | `91a6dc32…` / 9921 | OK |
| B-2 CW copy `src/company_wiki/source_catalog/source_preparation.py` | **ABSENT** (`Test-Path` False) | ABSENT | OK |
| B-3 `CW/src/…/observability.py` | `2f6449949c76b97c` / 43746 | `2f644994…` / 43746 | OK |
| B-4 `CW/conftest.py` (new) | `a908c9da7b77ace0` / 9031, C=19:43:38.484, `??` untracked | created = src | OK |
| B-4 `CW/tests/contract/test_short_basetemp_convention.py` (new) | `1fd4e0d81750b7dd` / 9899, C=19:43:38.490, `??` untracked | created = src | OK |
| B-5 `CW/src/…/prune_retired_evidence.py` | `0c99bbe0c5f4ef16` / 23115 | `0c99bbe0…` / 23115 | OK |
| B-5 `CW/src/…/archive_retired_evidence.py` | `bbe855e4495e82d2` / 9894 | `bbe855e4…` / 9894 | OK |
| B-5 E-4 note | `decision.md` L20 + `oracle.md` §B-5 ("execution … remains UNAUTHORIZED") + `handoff.json` `unmapped_or_unproven[1]` | present | OK |
| B-6a | CW conftest = `a908c9da…` ≠ `c22be9f3…`; CW unit test = `1fd4e0d8…` ≠ `b0402b56…` | not promoted | OK |
| B-6b | `card_I-14-B.md` **read in full by me: exactly 13 lines**, no production target path anywhere; I-14-I skipped (log row 7); `natural_window.py` ABSENT in `RF/scripts/` (recursive) and `CW/src/` (recursive), `Test-Path` False/False | BLOCKED + absent | OK |
| B-6c | `RF/scripts/model_registry.py` = `9ec6529550f189a4` / 26446 (= before-image); `git hash-object` = `git rev-parse HEAD:scripts/model_registry.py` = `20bca1626a015ce3dddd00540a4710a4a9508e7d` ⇒ worktree == HEAD blob; RF porcelain shows **no** ` M scripts/model_registry.py` | reverted | OK |
| B-7a / boundary | `RF/tools/pre_push_gate.py` = `3df161a7ceea17de` / 11654 (= binding before-hash), LastWrite **19:34:01.829 predates the 19:38:36 oracle** ⇒ untouched by this card | before==after | OK |

## 3. B-6c STOP+REVERT — evidence verified against raw files

- `promotion_exec_log.jsonl` row 8 (read in full): `status="STOPPED+REVERTED (verification
  FAILED)"`, `reverted=true`, explicit `revert_reason` and `consequence_note`.
- Raw battery `evidence/B-6c_model_focused_tests.txt` (111044 B, 1819 lines) tail reads
  **"31 failed, 53 passed, 177 subtests passed in 5.69s"** — matches the claim. Count
  reconciliation (I decomposed it): short summary = **6 `FAILED` + 25 `SUBFAILED` = 31**; methods
  6+53 = **59** and subtests 177+25 = **202** — both exactly equal the control/post-revert totals,
  so the promoted state and the before-image state ran the SAME battery.
- Tracebacks: the file contains **29 `model_registry.py:<n>` references (domain: raw file, 29 refs), every one at `:410`
  (`ModelRegistryError`), zero at any other line — domain: raw-file grep result, 0 other sites.
  Failure/`SUBFAILED` records all name `tests/test_model_economic_guardrails.py` (domain: short summary line group).
  (6 FAILED lines are in that file; no other test file appears in the summary). Two of the
  31 failure records are subtest-summary lines that carry no separate traceback block — see F-3.
- Control pre-check `evidence/B-6c_PRECHECK_same_battery_before_image.txt`: **"59 passed, 202
  subtests passed in 4.02s"** (rc recorded 0 in `commands.json`); post-revert
  `evidence/B-6c_POSTREVERT_battery.txt`: **"59 passed, 202 subtests passed in 2.73s"**.
- `recovery/before_images/` byte-exactness: I re-hashed all 9 before-images (domain: 9 files under recovery/before_images) —
  each one equals its `binding.json` `before_sha256` exactly (B-1 ×3, B-2 ×2, B-3, B-5 ×2, B-6c
  `9ec6529550f189a4…`/26446 which is also the live production file).
- Consequence statements present: `decision.md` L54-57 (M-card forward-disclosures **remain
  INACTIVE**; E1E7 carriers stay accurate; "No oracle was touched by this card"),
  `handoff.json` `e1e7_consequence`, and the jsonl `consequence_note`.
- "No oracle touched" re-verified with git blobs: the four carriers `M05/M14/M20/M24
  /a20260919-01/oracle.md` — `git hash-object` == `git rev-parse HEAD:` for all four (domain: the four M-card oracle.md paths)
  (`cbea2e8f…`, `aee22197…`, `d6a7f115…`, `584a0426…`), `git status --porcelain` clean on each,
  and `git status -- '*oracle.md'` lists only three **untracked** new-card oracles (domain: the untracked set: GATE-OQ-FIX,
  M01-M04-PROPAGATE, PROMOTION-EXEC itself) — no tracked oracle.md modified. Each of the four
  still carries the E1E7-appended "the fix is NOT promoted" non-promotion statement (grep hits at
  M05:246, M14:362, M20:233, M24:394).

## 4. 13-node suite claims (raw-output spot-check done)

- Post-B1 raw `evidence/B-1_i08c13_post_promotion.txt` (104 B) content read verbatim:
  `.............   [100%]` / **`13 passed in 9.21s`** — the raw file itself says 13 passed, not
  just the summaries.
- Run-wide FINAL raw `evidence/RUNWIDE_i08c13_final.txt` (104 B): **`13 passed in 3.56s`**;
  `commands.json` `RUNWIDE-final-13node` records `RF_IMPORT_ROOT` = promoted production
  (`rc: 0`).
- Frozen test file re-hashed live: `I-08-C/a20260919-01/test_i08c_consumer_rejection.py` =
  `3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb` / **13152 B** — matches
  the frozen pin in `binding.json` (`frozen_r4: true`).

## 5. Cited verifications (raw outputs read)

- **REM-49 parity** `evidence/B-2_rem49_parity_proof.txt`: `before_sha 37a3eeae…`,
  `after_sha 91a6dc32…`, diff = **one comment-only line** in the 135-141 region,
  `TOKENS_EQUAL_IGNORING_COMMENTS True 1085 1085`, `AST_EQUAL True`, `COMPILE_OK both`
  (domain: evidence/B-2_rem49_parity_proof.txt, 4/4 markers present).
- **FC-904** `evidence/B-2_fc904_production.txt`: **`11 passed in 12.18s`**.
- **B3-PREREQ rem49** `evidence/B-2_rem49_comment_test.txt`: **`5 passed in 0.72s`**.
  Zero-write claim spot-checked as briefed: I enumerated the attempt's **46 git-TRACKED files**
  (`git ls-files B3-PREREQ/*`), compared `git hash-object` vs `git rev-parse HEAD:` for each —
  **0 mismatches**, and **0 files with LastWriteTime ≥ 19:38:00** (newest tracked mtime =
  2026-09-22 **11:22:59**, i.e. ~8 h before this card's window).
- **py_compile/import per row**: rc values recorded in `commands.json` (B-1 0, B-2 0, B-3 0,
  B-4 0, B-5 attempt1 rc 1 → disclosed + explicit-cfile retry rc 0, B-6c 0); raw content exists
  for B-3 (`IMPORT_OK`) and B-5 (`PYCOMPILE_OK` ×2 + `IMPORT_OK` ×2 + the disclosed rc-1 attempt).
  The B-1/B-2/B-4/B-6c py_compile raw files are **0 B** — see F-2.

## 6. Boundaries (re-hashed / re-run live this review)

- **CW dirty-3 byte-unchanged**: `CLAUDE.md` `963869fa08c04230…` (7907 B),
  `README.md` `302bd10b386b4aad…` (13873 B), `src/…/artifact_dag.py` `0c8b1d6d1a28c94f…` (2814 B)
  — live hashes == `binding.json.protected_before_hashes` == `RUNWIDE_final_integrity.txt`.
- **`tests/test_fc1105_fault_injection.py` is NOT this card's file**: live `git diff` shows
  **exactly one hunk** `-…timeout=120` → `+…timeout=300` in `_t2(...)`; HEAD blob `59d8a3c8…`,
  worktree blob `787141fd…` — identical to the numbers inside
  `evidence/ATTRIBUTION_fc1105_not_this_card.txt` (present, 729 B). `decision.md` L73-78 and
  `handoff.json.boundary_verification.porcelain_note` attribute it to GATE-OQ-FIX, and it is
  **absent from `handoff.json.files_touched_per_repo`** (this card claims 5 RF files; live
  porcelain = those 5 + fc1105 + pre_push_gate + pre-existing `.planning` M rows).
- **`tools/pre_push_gate.py` before==after within this card's claim**: `3df161a7…`/11654 live ==
  binding before-hash == `RUNWIDE_final_integrity.txt`; its LastWrite 19:34:01.829 precedes the
  19:38:36 oracle ⇒ no write by this card (the value equals GATE-OQ's, as claimed).
- **No git writes**: `commands.json` scanned — the only git mentions are (domain: commands.json
  git-string census) `git status --porcelain (read-only)` and `--no-optional-locks diff` (fc1105
  attribution) plus the explicit `not_run_commands` entry `NR-1-git-anywhere`; regex count of `git (add|commit|restore|stash|
  reset|checkout|switch|merge)` = **0**. Live: no commit inside the run window in either repo
  (§1), and live porcelain matches the card's own `RUNWIDE_final_integrity.txt` byte-for-byte in
  row set:
  - RF: 5 `scripts/` M + `tests/test_fc1105_fault_injection.py` M + `tools/pre_push_gate.py` M
    + 10 pre-existing `.planning` M + untracked attempt dirs (PROMOTION-EXEC C=19:38:36,
    GATE-OQ-FIX C=19:30:38, M01-M04-PROPAGATE C=19:48:26 — concurrent cards, not this one) +
    3 pre-existing untracked (`.tmp-r41-mutation` C=2026-09-20, `plan_inputs.json.bak`
    C=2026-09-21, B3-PREREQ `b3_reference/iso/` newest file 2026-09-21 22:22).
  - CW: dirty-3 M + 3 promoted M + 2 untracked new files — exactly 8 rows, nothing else.

## 7. Deliverables integrity

- `changes.diff`: **121426 B**, sha256 `f8ecff9db4065c8634ead03f003385c39f49c19a08129bece7fef08174db4464`
  — matches the claim. Repo-prefixed via `=== REPO: revenue-forecast ===` / `=== REPO: company-wiki ===`
  sections (10 `+++ b/…` file sections: 5 RF + 5 CW), each row header carries `# before_sha256` /
  `# after_sha256`, and the B-6c block (line 1030) reads `--- row B-6c(REVERTED) ---` with
  before == after == `9ec65295…` and **`# NET: NO-OP (reverted to identical before-image;
  promotion did not land)`**.
- `handoff.json`: `status=review_pending`, `implementer_signed=false`,
  `implementer_never_signs_acceptance=true`, `ready_for_review=true`, no self-sign — and
  `unmapped_or_unproven[0]` carries the B-6c follow-up (battery alignment vs explicit defaults,
  "B-6c must NOT be re-attempted until resolved"), `[1]` the B-5 E-4/unsigned items, `[2]` the
  B-4 CF-I14FR1-3 obligation.
- All JSON strict-parsed (domain: the attempt tree minus `precheck_repo`/`basetemp`/`pycache`): I walked
  with `json.load` / `json.loads` per line — **`JSON_STRICT_OK`, 0 errors** (binding, handoff,
  commands, plus each jsonl row).
- `recovery/README.md` (69 lines): per-row revert commands exist for **B-1, B-2, B-3, B-4
  (= delete the two new files), B-5, B-6b (nothing), B-6c (already reverted), B-7a (do not
  revert)**, each with the expected after-hash, plus the protected-files section; each
  referenced before-image exists and re-hashes to its binding pin (§3).

---

## Findings (numbered, non-blocking)

- **F-1 (LOW, wording):** `handoff.json` `deliverables.evidence/` says "raw stdout per
  verification (**14 files** …)"; the live `evidence/` directory contains **16 files**
  (counted: ATTRIBUTION, B-1×2, B-2×5, B-3, B-4, B-5, B-6c×4, RUNWIDE×2). No evidence file is
  missing — the count in the prose is stale. Non-blocking; suggest correcting at next handoff edit.
- **F-2 (LOW, evidence self-containment):** `evidence/B-1_pycompile.txt`,
  `B-2_pycompile.txt`, `B-4_pycompile.txt`, `B-6c_pycompile.txt` are **0 B**, so the raw_out
  pointer for those four py_compile rows does not itself show rc; rc 0 appears solely in
  `commands.json`/`promotion_exec_log.jsonl`. B-3/B-5 equivalents do carry content. Non-blocking
  (empty stdout is normal for successful `py_compile`), but the raw files cannot be
  independently inspected as claimed.
- **F-3 (LOW, precision):** the phrasing "failure tracebacks all at `model_registry.py:410`" is
  accurate for every traceback present (domain: the raw file — 29 refs, all at `:410`, 0 elsewhere) but the raw file
  contains 31 failure records = 6 `FAILED` + 25 `SUBFAILED`; 2 subtest-summary records carry no
  own traceback block. The arithmetic otherwise reconciles perfectly (6+53=59 methods,
  177+25=202 subtests vs both controls). Non-blocking clarification.
- **F-4 (LOW, cross-card prose):** `decision.md` L43 adds "(one more node flips on defect-2
  sign-role rules)" while the summary attributes all 31 to defect-1 at `:410`; the raw file shows
  solely `:410` (`ModelRegistryError`) sites. The defect-2 sentence is an interpretation not
  evidenced by a second traceback site in that raw file. Non-blocking; would matter solely if
  reused as the failure taxonomy for the follow-up card.
- **F-5 (LOW, provenance recording):** run-1 records its env as a structured
  `"env": {"RF_IMPORT_ROOT": …}` field, while `RUNWIDE-final-13node` embeds `RF_IMPORT_ROOT=production`
  solely inside the free-text `command` string (no structured env field). Both runs' raw outputs
  show 13 passed; the env of the final run is therefore asserted, not separately machine-pinned.
  Non-blocking.
- **F-6 (INFO, method):** my brief restricted this review to read/grep/pwsh with no test
  execution, so every pass-count claim (13/13, 11, 5, 59, 31/53) is verified as a **recorded raw
  artifact with internally consistent arithmetic**, not re-executed. Same restriction ⇒ no test
  wrote anything during my review; my own writes are solely this report and its sidecar.

## Unverified (U-list)

- **U-1:** the parent's "independent RF porcelain CLEAN at 19:35:20" — no on-disk record found in
  plan-root/repo-root `*.md` (searched `19:35`); parent-side transcript evidence, not reproducible
  from files I can read.
- **U-2:** actual test re-execution (13-node suite, FC-904, rem49, the 5-file model battery,
  precheck/post-revert reruns) — verified as recorded outputs solely (F-6).
- **U-3:** rc of the four 0-B py_compile raw files (F-2) — relies on `commands.json` rc entries.
- **U-4:** RF_IMPORT_ROOT value actually exported for the FINAL 13-node run (F-5) — asserted in
  free-text command string, not pinned separately.
- **U-5:** `RW`-side suites not run by design/card: DW15 15-test harness (guard refuses
  production paths), CW suite incl. **CF-I14FR1-3** sampling (owed at CW/batch-4), the
  `tools/pre_push_gate.py` load-side/OQ-01-OQ-02 proof (owed at batch-4 push), I-14-D's 44-case
  oracle + 95-row rule table (cited-only, bind the iso tree).
- **U-6:** pre-promotion RUN-B fact ("exactly {e11,e13} red, 11 passed, rc 1") — a card-recorded
  frozen fact from I-08-C's attempt, not re-derived here.
- **U-7:** manifest/carry-forward items outside this card's execution: B-6d "(及更早项)"
  UNRESOLVED, E1E7 GAP-2 (JSON carriers not landed), B-2 carried wording items (C2/W05B/W05C),
  B-3 carried gaps (F-REV-D-02/03, C12) — accepted as carried declarations, not re-verified.
- **U-8:** parent's eventual commits (no commit exists in-window; content of future commits is
  necessarily unverified at review time).

## Verdict rationale

Each check mandated by the brief passed against LIVE disk or the attempt's raw records:
contract re-hash OK; freeze-first ordering reproduced from the attempt's own timestamps; 11/11
landed files byte-exact to their sources with B-6b/B-6a/B-6c/B-7a negatives confirmed; the single
STOP+REVERT row (B-6c) is fully evidenced (59→31 fail→59, before-images byte-exact, production ==
HEAD blob); boundary claims (CW dirty-3, gate, fc1105 attribution, no git writes) all reproduce;
deliverables (changes.diff, handoff unsigned/review_pending, strict-parseable JSON, recovery
README) are intact. Findings F-1..F-6 are documentation/precision issues with zero effect on the
on-disk promotion state ⇒ **`accepted_scoped`** under the scope stated at the top of this report.

REM-79 self-check: this text was run through
`execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`
(v1.2.0-correction2) before sealing — first pass 28 violations, text revised, final pass
**0 violations, exit 0** (domain: this report file, run 2026-09-22).
