# PROMOTION-EXEC (a20260922-01) — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `accepted_scoped` — 6 non-blocking findings (F-1..F-6), 8 unverified items (U-1..U-8)
- **carrier** = `reviewer_report.md`
- **carrier sha256** = `E2A42D2DE28997D78A63085BD3D2AC24C28DB75CB4E7A37FDDA809ADA7C1FBBB` — **20561 B**, 260 lines, UTF-8 without BOM, LF line endings only (0 CR), single trailing LF
- **pin** = `reviewer_report.md.sha256` (84 B, sidecar's own sha256 `cff9b20da9dcad81fe91ec1e67561d11dd97aa6a6f76b95a7b0a4efdd1bcfe6a`) reads `E2A42D2DE28997D78A63085BD3D2AC24C28DB75CB4E7A37FDDA809ADA7C1FBBB  reviewer_report.md` (two spaces, no trailing newline; sibling naming correct) — verified read-only at landing: independent re-hash of the carrier == sidecar content == dispatch pin (expected prefix `E2A42D2DE28997D78A63085BD3D2AC24C28DB75CB4E7A37FDDA809ADA7C1FBBB`, **full 64-hex match, not merely a prefix**), byte size 20561 == dispatched, verdict line greps to `accepted_scoped`.
- **line-count note (non-blocking, disclosed):** the dispatch brief's "257 lines" reproduces **only** when this UTF-8 file is decoded with this host's PowerShell 5.1 default ANSI/CP936 codepage, which swallows 3 LF bytes (CP936 LF count = 257 — and the same decode mojibakes every `—`). UTF-8-correct counts all agree at **260**: `wc -l` 260, .NET `ReadAllLines` 260, `Get-Content -Encoding utf8` 260, reader tool 260. Non-blocking bookkeeping nuance; the sha256 and 20561 B byte proof are exact and unaffected by it.
- **ruling location** = `reviewer_report.md` **L3**: ``**Verdict: `accepted_scoped`** — 6 non-blocking findings (F-1..F-6), 8 unverified items (U-1..U-8).``; title/meta/authority/writes-scope **L1–L11**; acceptance scope **L13–L21**; contract re-hash §0 **L25–L32**; freeze-first ordering §1 **L34–L58**; row outcomes §2 **L60–L79**; B-6c STOP+REVERT §3 **L81–L110**; 13-node suite §4 **L112–L122**; cited verifications §5 **L124–L139**; boundaries §6 **L141–L167**; deliverables §7 **L169–L188**; findings heading **L192**; findings F-1..F-6 **L194–L222**; unverified U-1..U-8 **L224–L244**; verdict rationale **L246–L255**; REM-79 self-check **L257–L260**.
- **byte proof** (0-based byte offsets against the file as it stands at `carrier_sha256`; multi-line regions include internal LFs and exclude the terminating LF): verdict line L3 bytes 65..165 (101 B) sha256 `7226cff1cb40276c050b8876668f434231998da19321b76c8a7cb11bdfceaa8f`; meta L1–L11 bytes 0..992 (993 B) `4b1d6ab224f7835eacef48c3818ee9017321f56666c68d091da7bee38803a218`; acceptance scope L13–L21 bytes 995..1801 (807 B) `4c473314a20f49a0343b455782b70b76d013ddb2851a0ef2316a5311036e7d0f`; §0 L25–L32 bytes 1809..2379 (571 B) `56343661eb65f5c9206777b4bb525c1a84854e80254e3d072479b1159beaa7fe`; §1 L34–L58 bytes 2382..4492 (2111 B) `330f8a6fa7125b838b52b748f3eba8277466dbe25911e331017affb07fb26694`; §2 L60–L79 bytes 4495..6894 (2400 B) `d1eec75deabfa6a154b18e1242680803b5ea72a70cd3a1a44ab9711e2b95c638`; §3 L81–L110 bytes 6897..9581 (2685 B) `5eeb74c415d8e708e31cfa0510ceb743313559a19455d747cdf37eef99f0717f`; §4 L112–L122 bytes 9584..10280 (697 B) `ed3da1fea2aaea35df6e87b52616143283ca37fad7526d850f5a4db3abf32058`; §5 L124–L139 bytes 10283..11526 (1244 B) `bae2708eadd1052f24b032eb4b340102a8b6d70975412c3994ad3b8dce1b3101`; §6 L141–L167 bytes 11529..13820 (2292 B) `e467e4a4fca847c8de883b0526715b440be3fe29e37572774811f07bbf739763`; §7 L169–L188 bytes 13823..15337 (1515 B) `3b128cb408f6d0dcc4a50ecb0d37203178f580280478a3d848d6ccdd1b2e188c`; findings heading L192 bytes 15345..15380 (36 B) `568213f5eb38c756c7adee39136f1b0a1589b91fe02738659736805962f514c6`; findings F-1..F-6 L194–L222 bytes 15383..17899 (2517 B) `84fcb937d60afd550d8a44d15b6139dbf497189a023d477326214dcdbd79df05`; findings section L192–L222 bytes 15345..17899 (2555 B) `ab85c6189cc260d8bb83f4752841b795bd46f38ea89f75d7fc7a227f454175dc`; unverified list L224–L244 bytes 17902..19477 (1576 B) `505223f80d5188a5dd3ba34a8007d0c4cac149cd75eb22fcd9a4c8630398b2bd`; verdict rationale L246–L255 bytes 19480..20270 (791 B) `32dd85e8b2acc96538223dd3123e278ad818a82753aff58365464844c92b5e65`; REM-79 self-check L257–L260 bytes 20273..20559 (287 B) `ee59730cb48c92a57f44c2dd8f43dbaa0d6b921a6cf2e9af436e0272c5fa4376`; whole file minus trailing LF 20560 B `23607fe825c12ab7dda63e80b31252a9880995e18885adffef3d8ea299763faf`.
- **reviewer** = **独立复核** (independent reviewer subagent of parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`, parent-dispatched; **NOT the implementer**; date 2026-09-22; wrote only `reviewer_report.md` + `reviewer_report.md.sha256` inside this attempt — 2 files, domain: its own writes; everything else read-only, domain: tool scope = read/grep/pwsh, 0 write operations; all git usage read-only — domain: `status --porcelain`, `log`, `rev-parse`, `hash-object`, `diff --no-optional-locks` (5 subcommands, 0 writes); no test suite re-executed — domain: method scope declared in its §0, per brief).
- **nature of this file** = **bookkeeping transcription adds no acceptance of its own.** The implementer never signs (`handoff.json` `implementer_signed=false`, `implementer_never_signs_acceptance=true`); this landing pass never signs; nothing here authorizes anything beyond restating the reviewer's byte-pinned ruling. `review.md` did not previously exist in this attempt (no implementer stub) — created by the carrier-landing pass, not by the implementer and not by the reviewer. 0 bytes were written to `reviewer_report.md` or its sidecar by this pass.

---

## Acceptance scope (verbatim condition of the verdict — carrier L13–L21)

- **B-6c is NOT promoted** — blocked on test-battery wrong-oracle alignment (`tests/test_model_economic_guardrails.py` vs I-10-B semantics) — a separate card; dispatch records that separate card as **MODEL-ORACLE-ALIGN, in flight** (`execution_runs/MODEL-ORACLE-ALIGN/` present on disk).
- **B-6b has no production target by card design** (I-14-B's 13-line card declares no production target path) ⇒ BLOCKED-unresolved; I-14-I skipped; nothing to promote.
- **B-4's CW-suite sampling (CF-I14FR1-3) is still owed** at the CW/batch-4 side (pre-merge).
- **B-5 execution (prune/archive, dry-run included) remains owner-unsigned / UNAUTHORIZED (E-4)**; this card promoted the CODE, never the execution (domain: E-4 code-only split).
- **Git commits = the parent's act, after this review**; this card made no commits (domain: git log window 19:38–19:56 empty, both repos). Exact lists transcribed into `handoff.json.acceptance_scope`: **RF = the 5 `scripts/` files** (revenue_core, revenue_publication, revenue_report, company_wiki_source, source_preparation); **CW = 3 M + 2 new** (observability/prune_retired_evidence/archive_retired_evidence M; conftest.py + tests/contract/test_short_basetemp_convention.py new); **EXCLUDE `tests/test_fc1105_fault_injection.py` + `tools/pre_push_gate.py` — GATE-OQ-FIX's**; no `git add -A`.

---

## 1. Freeze-first corroboration chain (carrier §1, L34–L58)

- Ordering reproduced from the attempt's **own** files, live-stat'd: **oracle `2026-09-22 19:38:36.358` → binding `19:38:36.971` (+0.6 s) → execution log creation `19:40:59.184` (row-1 ts `2026-09-22T18:40:59.025Z` = 19:40:59.025+01:00) → CW new-file first write `19:43:38.484`** (conftest.py; second new file `19:43:38.490`) — exactly the ordering claimed; the parent-measured oracle CreationTime reproduces to the millisecond on the reviewer's own `Get-Item` read.
- In-attempt textual corroboration: `oracle.md` L12-13 ("nothing below may be edited after the first production write"), L156-157 ("Frozen at: before the first production write"); `binding.json` `binding_status="bound (oracle.md frozen first; all hashes measured live before any production write)"`; `commands.json` `contract_verified_first.written_before_run`.
- No production-tree file's own timeline contradicts it: promoted-file LastWriteTimes are the source-iso times (copy preserves mtime); the only CreationTime-anchored writes are the two CW new files (domain: NTFS CreationTime anchors, 2 files).
- **No commits in the run window in either repo**: RF `HEAD = 4b1c690b 2026-09-22T14:03:00+01:00`, CW `HEAD = f39bd5a 2026-09-19T08:42:58+01:00` — no commit exists inside 19:38–19:56 (domain: `git log -3 --format=%cI`, read-only, live).
- **Parent's transcript "RF porcelain CLEAN at 19:35:20" = U-1**: not found on disk anywhere the reviewer searched (plan-root `*.md`, repo-root `*.md`) — it is **chat-transcript evidence only, not on-disk**; it is parent-side evidence and is **not needed** for the ordering proof, which **stands on the attempt's own timestamps**.

## 2. Per-row live-hash confirmations (carrier §2, L60–L79 — all OK)

| row | live measurement (sha256 prefix / bytes) | result |
|---|---|---|
| B-1 `RF/scripts/revenue_core.py` | `8a761498f5eb729e` / 25842 | OK (== expected) |
| B-1 `RF/scripts/revenue_publication.py` | `bc2bb4a33e36ed9a` / 24917 | OK |
| B-1 `RF/scripts/revenue_report.py` | `212f00598feca408` / 73973 | OK |
| B-2 `RF/scripts/company_wiki_source.py` | `7d1bd8f9d9122dc4` / 20545 | OK |
| B-2 `RF/scripts/source_preparation.py` | `91a6dc32466e9d67` / 9921 | OK |
| B-2 CW copy `src/…/source_preparation.py` | **ABSENT** (`Test-Path` False) | OK (== expected ABSENT) |
| B-3 `CW/src/…/observability.py` | `2f6449949c76b97c` / 43746 | OK |
| B-4 `CW/conftest.py` (new) | `a908c9da7b77ace0` / 9031, C=19:43:38.484, `??` untracked | OK (created == src) |
| B-4 `CW/tests/contract/test_short_basetemp_convention.py` (new) | `1fd4e0d81750b7dd` / 9899, C=19:43:38.490, `??` untracked | OK (created == src) |
| B-5 `CW/src/…/prune_retired_evidence.py` | `0c99bbe0c5f4ef16` / 23115 | OK |
| B-5 `CW/src/…/archive_retired_evidence.py` | `bbe855e4495e82d2` / 9894 | OK |
| B-5 E-4 note | `decision.md` L20 + `oracle.md` §B-5 + `handoff.json unmapped_or_unproven[1]` present | OK |
| B-6a | CW conftest `a908c9da…` ≠ `c22be9f3…`; CW unit test `1fd4e0d8…` ≠ `b0402b56…` | OK (not promoted) |
| B-6b | `card_I-14-B.md` read in full: **exactly 13 lines**, no production target path; I-14-I skipped (log row 7); `natural_window.py` ABSENT in `RF/scripts/` and `CW/src/` (recursive) | OK (BLOCKED + absent) |
| B-6c | `RF/scripts/model_registry.py` = `9ec6529550f189a4` / 26446 (= before-image); `git hash-object` == `git rev-parse HEAD:scripts/model_registry.py` = `20bca1626a015ce3dddd00540a4710a4a9508e7d` ⇒ worktree == HEAD blob; RF porcelain shows **no** ` M scripts/model_registry.py` | OK (reverted) |
| B-7a / boundary | `RF/tools/pre_push_gate.py` = `3df161a7ceea17de` / 11654 (= binding before-hash), LastWrite **19:34:01.829 predates the 19:38:36 oracle** | OK (untouched by this card) |

**11/11 landed files byte-exact to their sources, with the B-6a/B-6b/B-6c/B-7a negatives confirmed.**

## 3. B-6c STOP arithmetic decomposition (carrier §3, L81–L110)

- `promotion_exec_log.jsonl` row 8 (read in full): `status="STOPPED+REVERTED (verification FAILED)"`, `reverted=true`, explicit `revert_reason` + `consequence_note`.
- Raw battery `evidence/B-6c_model_focused_tests.txt` (111044 B, 1819 lines) tail reads **"31 failed, 53 passed, 177 subtests passed in 5.69s"**. Reviewer's decomposition: short summary = **6 `FAILED` + 25 `SUBFAILED` = 31**; methods **6 + 53 = 59**; subtests **177 + 25 = 202** — both exactly equal the control/post-revert totals, so promoted state and before-image state ran the **same** battery.
- Tracebacks: **29 `model_registry.py:<n>` references in the raw file (domain: raw file, 29 refs), every one at `:410`** (`ModelRegistryError`), zero at any other line (domain: raw-file grep, 0 other sites). All failure/`SUBFAILED` records name `tests/test_model_economic_guardrails.py` (6 FAILED lines in that file; no other test file in the summary). **2 of the 31 failure records are subtest-summary lines carrying no separate traceback block** — the 29-vs-31 nuance = F-3.
- **Control pre-check** `evidence/B-6c_PRECHECK_same_battery_before_image.txt`: **"59 passed, 202 subtests passed in 4.02s"** (rc 0 in `commands.json`); **post-revert** `evidence/B-6c_POSTREVERT_battery.txt`: **"59 passed, 202 subtests passed in 2.73s"** ⇒ **59 → 31 fail → 59**, caused solely by this row.
- `recovery/before_images/`: **all 9 before-images re-hashed** (domain: 9 files under recovery/before_images) — each equals its `binding.json` `before_sha256` exactly (B-1 ×3, B-2 ×2, B-3, B-5 ×2, B-6c `9ec6529550f189a4…`/26446). **9/9 == binding pins**, and the B-6c image **== the live production file** (production reverted byte-exact == HEAD blob).
- Frozen failure rule executed: STOP, revert to before-image `9ec65295` byte-exact, post-revert rerun 59 passed rc0, continue other rows, report.

## 4. Consequence verification (carrier §3 tail, L101–L110)

- **Four M-card oracles `M05/M14/M20/M24/a20260919-01/oracle.md`: `git hash-object` == `git rev-parse HEAD:` for all four** (domain: the four M-card oracle.md paths) — `cbea2e8f…`, `aee22197…`, `d6a7f115…`, `584a0426…`; `git status --porcelain` clean on each; `git status -- '*oracle.md'` lists only three **untracked** new-card oracles (domain: GATE-OQ-FIX, M01-M04-PROPAGATE, PROMOTION-EXEC itself) — **no tracked oracle.md modified**.
- Each of the four still carries the E1E7-appended **"the fix is NOT promoted"** non-promotion statement (grep hits M05:246, M14:362, M20:233, M24:394) ⇒ because B-6c was reverted, the four M-card oracle **forward-disclosures remain INACTIVE**, the E1E7 carriers' statements remain **accurate**, and **no oracle was touched by this card** (`decision.md` L54-57, `handoff.json e1e7_consequence`, jsonl `consequence_note`).

## 5. 13-node suite claims (carrier §4, L112–L122)

- Post-B1 raw `evidence/B-1_i08c13_post_promotion.txt` (104 B) read verbatim: `.............   [100%]` / **`13 passed in 9.21s`** — the raw file itself says 13 passed, not just a summary.
- Run-wide FINAL raw `evidence/RUNWIDE_i08c13_final.txt` (104 B): **`13 passed in 3.56s`**; `commands.json RUNWIDE-final-13node` records `RF_IMPORT_ROOT` = promoted production (`rc: 0`).
- Frozen test file re-hashed live: `I-08-C/a20260919-01/test_i08c_consumer_rejection.py` = `3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb` / **13152 B** == the `binding.json` frozen pin (`frozen_r4: true`).

## 6. Cited verifications (carrier §5, L124–L139)

- **REM-49 parity** `evidence/B-2_rem49_parity_proof.txt`: `before_sha 37a3eeae…`, `after_sha 91a6dc32…`, diff = **one comment-only line** (135-141 region), `TOKENS_EQUAL_IGNORING_COMMENTS True 1085 1085`, `AST_EQUAL True`, `COMPILE_OK both` (domain: that evidence file, 4/4 markers present) — **1085/1085 tokens + AST + compile**.
- **FC-904** `evidence/B-2_fc904_production.txt`: **`11 passed in 12.18s`**.
- **B3-PREREQ rem49** `evidence/B-2_rem49_comment_test.txt`: **`5 passed in 0.72s`**; **zero-write spot**: the reviewer enumerated the attempt's **46 git-TRACKED files** (`git ls-files B3-PREREQ/*`), compared `git hash-object` vs `git rev-parse HEAD:` — **0 mismatches (46 files == HEAD)** and **0 files with LastWriteTime ≥ 19:38:00** (newest tracked mtime 2026-09-22 **11:22:59**, ~8 h before the window).
- **py_compile/import per row**: rc in `commands.json` (B-1 0, B-2 0, B-3 0, B-4 0, B-5 attempt1 rc 1 → disclosed + explicit-cfile retry rc 0, B-6c 0); raw content exists for B-3 (`IMPORT_OK`) and B-5 (`PYCOMPILE_OK` ×2 + `IMPORT_OK` ×2 + the disclosed rc-1 attempt). The B-1/B-2/B-4/B-6c py_compile raw files are **0 B** → F-2.

## 7. Boundaries (carrier §6, L141–L167 — re-hashed / re-run live by the reviewer)

- **CW dirty-3 byte-unchanged**: `CLAUDE.md` `963869fa08c04230…` (7907 B), `README.md` `302bd10b386b4aad…` (13873 B), `src/…/artifact_dag.py` `0c8b1d6d1a28c94f…` (2814 B) — live hashes == `binding.json.protected_before_hashes` == `RUNWIDE_final_integrity.txt`.
- **`tests/test_fc1105_fault_injection.py` is NOT this card's file**: live `git diff` = exactly one hunk `-…timeout=120` → `+…timeout=300` in `_t2(...)`; HEAD blob `59d8a3c8…`, worktree blob `787141fd…`, identical to `evidence/ATTRIBUTION_fc1105_not_this_card.txt` (729 B); attributed to GATE-OQ-FIX in `decision.md` L73-78 + `handoff.json.boundary_verification.porcelain_note`; **absent from `files_touched_per_repo`** (this card claims 5 RF files; live porcelain = those 5 + fc1105 + pre_push_gate + pre-existing `.planning` M rows).
- **Gate untouched predates oracle**: `tools/pre_push_gate.py` `3df161a7…`/11654 live == binding before-hash == `RUNWIDE_final_integrity.txt`; LastWrite **19:34:01.829 precedes the 19:38:36 oracle** ⇒ no write by this card (the value equals GATE-OQ's, as claimed).
- **Zero git write verbs**: `commands.json` git-string census = only `git status --porcelain (read-only)` and `--no-optional-locks diff` (fc1105 attribution) plus the explicit `not_run_commands` entry `NR-1-git-anywhere`; regex count of `git (add|commit|restore|stash|reset|checkout|switch|merge)` = **0**. Live: no commit inside the run window in either repo; live porcelain matches `RUNWIDE_final_integrity.txt` **row-for-row**:
  - **RF**: 5 `scripts/` M + `tests/test_fc1105_fault_injection.py` M + `tools/pre_push_gate.py` M + 10 pre-existing `.planning` M + untracked attempt dirs (PROMOTION-EXEC C=19:38:36, GATE-OQ-FIX C=19:30:38, M01-M04-PROPAGATE C=19:48:26 — concurrent cards) + 3 pre-existing untracked (`.tmp-r41-mutation` C=2026-09-20, `plan_inputs.json.bak` C=2026-09-21, B3-PREREQ `b3_reference/iso/` newest 2026-09-21 22:22).
  - **CW**: dirty-3 M + 3 promoted M + 2 untracked new files — **exactly 8 rows, nothing else**.

## 8. Deliverables (carrier §7, L169–L188)

- `changes.diff`: **121426 B**, sha256 `f8ecff9db4065c8634ead03f003385c39f49c19a08129bece7fef08174db4464` == claim; repo-prefixed `=== REPO: revenue-forecast ===` / `=== REPO: company-wiki ===`, **10 `+++ b/…` sections (5 RF + 5 CW)**, every row header carries `# before_sha256` / `# after_sha256`; the B-6c block (line 1030) reads `--- row B-6c(REVERTED) ---`, before == after == `9ec65295…`, **`# NET: NO-OP (reverted to identical before-image; promotion did not land)`**.
- `handoff.json` (pre-verdict): `status=review_pending`, `implementer_signed=false`, `implementer_never_signs_acceptance=true`, `ready_for_review=true`, no self-sign; `unmapped_or_unproven[0]` = B-6c follow-up, `[1]` = B-5 E-4/unsigned, `[2]` = B-4 CF-I14FR1-3. **(This landing supersedes only the stale status prose; the pre-verdict text is preserved under `*_historical_pre_verdict`.)**
- **All JSON strict-parsed** (domain: attempt tree minus `precheck_repo`/`basetemp`/`pycache`) with `json.load`/`json.loads` per line — **`JSON_STRICT_OK`, 0 errors** (binding, handoff, commands + each jsonl row).
- `recovery/README.md` (69 lines): **per-row revert commands exist for all rows** — B-1, B-2, B-3, B-4 (= delete the two new files), B-5, B-6b (nothing), B-6c (already reverted), B-7a (do not revert) — each with the expected after-hash, plus the protected-files section; **each referenced before-image exists and re-hashes to its binding pin (§3)**.

---

## Findings F-1..F-6 (transcribed from carrier L192–L222 — all NON-BLOCKING, carried in `handoff.json.carried_findings`)

- **F-1 (LOW, wording) — record-note:** `handoff.json deliverables.evidence/` says "raw stdout per verification (**14 files** …)" while the live `evidence/` directory contains **16 files** (counted: ATTRIBUTION, B-1×2, B-2×5, B-3, B-4, B-5, B-6c×4, RUNWIDE×2). No evidence file is missing — the prose count is stale. Carried, not corrected here.
- **F-2 (LOW, evidence self-containment) — record-note:** `evidence/B-1_pycompile.txt`, `B-2_pycompile.txt`, `B-4_pycompile.txt`, `B-6c_pycompile.txt` are **0 B**, so those four raw_out pointers do not themselves show rc; rc 0 appears solely in `commands.json`/`promotion_exec_log.jsonl`. B-3/B-5 equivalents do carry content. Non-blocking (empty stdout is normal for successful `py_compile`) but not independently inspectable as claimed.
- **F-3 (LOW, precision) — record-note:** "failure tracebacks all at `model_registry.py:410`" is accurate for **every traceback present** (29 refs, all `:410`, 0 elsewhere) but the raw file holds **31 failure records = 6 FAILED + 25 SUBFAILED**, 2 of which are subtest-summary records with no own traceback block. The arithmetic otherwise reconciles perfectly (6+53=59 methods; 177+25=202 subtests vs both controls).
- **F-4 (LOW, cross-card prose) — record-note:** `decision.md` L43 adds "(one more node flips on defect-2 sign-role rules)" while the summary attributes all 31 to defect-1 at `:410`; the raw file shows solely `:410` (`ModelRegistryError`) sites — the defect-2 sentence is an interpretation **not evidenced by a second traceback site** in that raw file. Would matter solely if reused as the failure taxonomy for the follow-up card.
- **F-5 (LOW, provenance recording) — record-note:** run-1 records its env as a structured `"env": {"RF_IMPORT_ROOT": …}` field, while `RUNWIDE-final-13node` embeds `RF_IMPORT_ROOT=production` **solely inside the free-text `command` string** (no structured env field). Both runs' raw outputs show 13 passed; the final run's env is therefore asserted, not separately machine-pinned.
- **F-6 (INFO, method) — method note:** the reviewer's brief restricted it to read/grep/pwsh with no test execution, so **every pass-count claim (13/13, 11, 5, 59, 31/53) is verified as a recorded raw artifact with internally consistent arithmetic, not re-executed**. Same restriction ⇒ no test wrote anything during the review; the reviewer's own writes are solely its report and sidecar.

## Unverified U-1..U-8 (carrier L224–L244 — carried verbatim-in-substance)

- **U-1:** the parent's "independent RF porcelain CLEAN at 19:35:20" — no on-disk record found in plan-root/repo-root `*.md` (searched `19:35`); **parent-side chat-transcript evidence, not reproducible from files**; not needed for the ordering proof, which stands on the attempt's timestamps.
- **U-2:** actual test re-execution (13-node suite, FC-904, rem49, the 5-file model battery, precheck/post-revert reruns) — verified as recorded outputs solely (F-6).
- **U-3:** rc of the four 0-B py_compile raw files (F-2) — relies on `commands.json` rc entries.
- **U-4:** the `RF_IMPORT_ROOT` value actually exported for the FINAL 13-node run (F-5) — asserted in a free-text command string, not pinned separately.
- **U-5:** `RW`-side suites not run by design/card: DW15 15-test harness (guard refuses production paths), CW suite incl. **CF-I14FR1-3** sampling (owed at CW/batch-4), the `tools/pre_push_gate.py` load-side/OQ-01-OQ-02 proof (owed at batch-4 push), I-14-D's 44-case oracle + 95-row rule table (cited-only, bind the iso tree).
- **U-6:** pre-promotion RUN-B fact ("exactly {e11,e13} red, 11 passed, rc 1") — a card-recorded frozen fact from I-08-C's attempt, not re-derived here.
- **U-7:** manifest/carry-forward items outside this card's execution: B-6d "(及更早项)" UNRESOLVED, E1E7 GAP-2 (JSON carriers not landed), B-2 carried wording items (C2/W05B/W05C), B-3 carried gaps (F-REV-D-02/03, C12) — accepted as carried declarations, not re-verified.
- **U-8:** the parent's eventual commits (no commit exists in-window; the content of future commits is necessarily unverified at review time).

## Verdict rationale (transcribed from carrier L246–L255)

Each check mandated by the reviewer's brief passed against LIVE disk or the attempt's raw records: contract re-hash OK; freeze-first ordering reproduced from the attempt's own timestamps; 11/11 landed files byte-exact with B-6b/B-6a/B-6c/B-7a negatives confirmed; the single STOP+REVERT row (B-6c) fully evidenced (59→31 fail→59, before-images byte-exact, production == HEAD blob); boundary claims (CW dirty-3, gate, fc1105 attribution, no git writes) all reproduce; deliverables (changes.diff, handoff unsigned/review_pending, strict-parseable JSON, recovery README) intact. Findings F-1..F-6 are documentation/precision issues with **zero effect on the on-disk promotion state** ⇒ **`accepted_scoped`** under the scope stated at the top of this file. REM-79 self-check on the report: v1.2.0-correction2, first pass 28 violations → revised → final pass **0 violations, exit 0** (carrier L257–L260).

---

**What this landing did:** created `review.md` (this file); edited `handoff.json` (status + `status_before_bookkeeping_fix` + `status_authority` + `bookkeeping` + `acceptance_scope` + 7 `carried_findings` entries + stale pre-verdict prose superseded under `*_historical_pre_verdict`; pre-image 9688 B / sha256 `8bb4f14da73be612e0f86f515d2d67235a384a05a011cc3d4799d7721f3bf6f1`); created `evidence/PROMOTION-EXEC/qualification.json`. **Exactly three files written.** 0 bytes written to `reviewer_report.md` or its sidecar, 0 production bytes, **0 git writes (no git command executed by this pass)**; no verdict of its own; the implementer still signs nothing.
