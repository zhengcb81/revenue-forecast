# GATE-OQ-FIX — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `accepted_scoped` (11 findings, none blocking; F-8 minor only)
- **carrier** = `reviewer_report.md`
- **carrier sha256** = `478ef11d8eb8f51b1fa31bd6ffeae1fb092b48ed3c92d0d13fecfaa5a02f9280` — **18628 B**, 271 lines, UTF-8 without BOM, LF-only (0 CR), single trailing LF
- **pin** = `reviewer_report.sha256` (85 B, sidecar's own sha256 `9e6809c2555d43cdff68d4829beedec81aa52373868d6da3d8448736050c870f`) reads `478ef11d8eb8f51b1fa31bd6ffeae1fb092b48ed3c92d0d13fecfaa5a02f9280  reviewer_report.md` — verified read-only at landing: independent re-hash == sidecar == dispatch pin (expected prefix `478ef11d…`), byte size 18628 == dispatched, verdict line greps to `accepted_scoped`.
- **ruling location** = `reviewer_report.md` **L3**: ``**Verdict: `accepted_scoped`**``; meta/method/authority **L1–L18**; findings heading **L22**; the 11 findings F-1..F-11 **L24–L225**; unverified list **L229–L250**; REM-79 self-check **L252–L255**; scope note (conditions) **L257–L271**
- **byte proof** = verdict line L3 bytes 65..94 (30 B) sha256 `a2780d6ed412db4e465042a1c6079c3b6794296d6b3ef97b1a563a3f001965f0`; meta L1–L18 bytes 0..1349 (1350 B) `0caf33f92d7866a8fbf17bccab8fffe27f8221385ad130371403359f1d06d632`; findings heading L22 bytes 1357..1367 (11 B) `1824c2f9e430a89ccd24ec9ef1334f51a25d163b1e66e33e10ae970154542fec`; findings section L24–L225 bytes 1370..15823 (14454 B) `2b90628779ec0d741a09929b96eb146e7f157168aff427a779340b731cf16698`; unverified list L229–L250 bytes 15831..17473 (1643 B) `bc371226c76309b8414443077fb0f7ed14504e887d6ef369d460af73b616dbea`; REM-79 self-check L252–L255 bytes 17476..17682 (207 B) `08c123d340cc5d56c833041fc7c66ac6f7c1f919b4278d66401013b68b40a58e`; scope note L257–L269 bytes 17685..18542 (858 B) `c4eedb0773e109868e865cc42f3d6e0df4c67b97e602b1959535c0b88c9310f8`; closing line L271 bytes 18545..18626 (82 B) `4a9ae587cc06c25fff4ab017f399ea9365c985061c4a1bc86809075b956da050`; whole file minus trailing LF 18627 B `6314ea085b165043076eef11a17f5c7ff4bce73ee71a00ff1c35fb8ca3b7b5c2`
- **reviewer** = 独立复核 (independent reviewer subagent of session-bfecd191-fbc3-4a66-8ed1-6562479bf102; NOT the implementer; wrote only `reviewer_report.md` + `reviewer_report.sha256` inside this attempt; no full gate run, no pytest run, no git writes of any kind)
- **nature of this file** = bookkeeping transcription, adds no acceptance of its own. The implementer never signs; this landing pass never signs; nothing here authorizes anything beyond restating the reviewer's ruling.

`review.md` did not previously exist in this attempt (no implementer stub); created by the carrier-landing pass — not by the implementer and not by the reviewer. 0 bytes were written to `reviewer_report.md` or its sidecar by this pass.

## What the 11 findings established (transcribed from `reviewer_report.md` L24–L225)

### F-1 — Oracle frozen before any target-byte change: VERIFIED (with 2 briefing corrections)

- Reviewer re-measured CreationTime on this card's own files (local UTC+1 / UTC): `before/*.orig` (2 byte-copies) 19:30:39.18 / 18:30:39Z · `oracle.md` 19:33:04.575 / 18:33:04.575Z · `evidence/oracle_freeze.json` 19:33:15.470 / 18:33:15.470Z (record `frozen_utc` 18:33:14.8071481Z) · `binding.json` 19:33:39 · `tools/pre_push_gate.py` live mtime (Fix-1 apply) 19:34:01 / 18:34:01Z · `changes.diff` 19:34:10 · `tests/test_fc1105_fault_injection.py` live mtime (final restore) 19:38:37 / 18:38:37Z — sequence: **oracle C → freeze record +10 s → first target write +47 s**.
- Freeze record present; its `oracle_sha256` `b08b51df…aae5851` re-computes to `oracle.md`'s sha256 (exact match); both `before_sha256` pins inside it equal the reviewer's independent re-hashes of the two `before/*.orig` copies; asserts `both_files_untouched_at_freeze: true`, `edits_applied_at_freeze: false`, empty scoped porcelain, HEAD `4b1c690b`.
- **No byte of either target file was written before the freeze instant**: first target mtime 18:34:01Z vs freeze 18:33:14.8Z — the freeze rule holds on an independent clock reading, not solely on the card's own record.
- **Correction 1 (briefing data belonged to a sibling card — recorded per dispatch):** the parent's earlier briefing numbers "oracle 19:38:36.358 = earliest, binding +0.6 s" are NOT this card's measurement — those exact values match `PROMOTION-EXEC/a20260922-01` (oracle.md C = 19:38:36.3583778, binding.json C = 19:38:36.9710668 → +0.61 s). The reviewer corrected this cross-card mix-up; GATE-OQ-FIX's own freeze is 19:33:04 / 19:33:15 local and **passes on its own numbers**.
- **Correction 2:** "oracle = earliest file in the attempt" is literally false here — `before/pre_push_gate.py.orig` and `before/test_fc1105_fault_injection.py.orig` were created 2 min 25 s BEFORE `oracle.md` (C1 snapshot step, 18:30:39Z). They are read-only copies (copying a snapshot modifies no target byte), so the substantive freeze property is intact; flagged so the parent does not repeat the "earliest file" formulation against this attempt.

### F-2 — The two edits are surgical: VERIFIED

- `changes.diff` sha256 re-computed = `e821500800ee5814fe71bed1c0ec434b14a3f73b2558ee0baf76c3053243951b` (matches the `e8215008…` pin and `final_deliverable_hashes.json`).
- Exactly **2** `diff --git` headers, no third file, no mode/rename/hunk noise: (1) `tools/pre_push_gate.py` **+1/−0**, hunk `@@ … @@ def _real_data() -> int`, the single added line is `        timeout=1800,` inside `_real_data()`'s `>_run(...)` call, diff index `483486bd..9004104d`; (2) `tests/test_fc1105_fault_injection.py` **+1/−1**, line 60 in the `_t2()` helper `timeout=120,` → `timeout=300,`, diff index `59d8a3c8..787141fd`.
- **`_run` default stays 1200**: live `tools/pre_push_gate.py` L73 still reads `def _run(cmd, label, timeout: int = 1200, *, blocking: bool = True)`. **No other call site changed**: line-level `Compare-Object` of `before/*.orig` vs live — gate 281→282 lines with exactly one added object (`timeout=1800,`); test 169→169 with exactly one swapped object (120→300); remaining timeout-bearing lines unchanged (L83 `timeout=timeout` pass-through, L238 pytest `--timeout=180`), and test **L158's pre-existing `timeout=60` is byte-identical** to the before-copy.
- **Live re-hashes**: `tools/pre_push_gate.py` = `3df161a7ceea17de95b36845bdb3c4cee729dca215c56853868780dce7331484` ✓ and `tests/test_fc1105_fault_injection.py` = `98ddcdc70b208a35b87b89d83870fe8985156e94ea6596dd6c2b02e6335f8e62` ✓ — both match `binding.json` `hash_anchors_after`, `handoff.json`, `final_state_verification.json`, `final_deliverable_hashes.json`.
- `evidence/git_diff_final_after_mutation_restore.txt` re-hashes to the SAME `e8215008…` as `changes.diff` — the recorded diff is the post-restore worktree state byte-for-byte.

### F-3 — Before-pins and the batch-1..3 push-pin: VERIFIED

- `before/pre_push_gate.py.orig` sha256 re-computed = `cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b` (…`6df0b`) ✓; test before-copy = `0bcd7ac81dba2c03362c9d0fa21ef59188f096f872b49e6efffc9cb028a0856e` ✓.
- **`cf09ade8…` IS the batch-1..3 push-pinned gate blob across ALL commits, confirmed via `git rev-parse`:** the before-copy's blob (`git hash-object`) = `483486bdd14084f573c0c64f2996c8ae7c4b81d4`, and `git rev-parse <tip>:tools/pre_push_gate.py` returns the identical blob `483486bd…` at `6f74b056` (batch-1 tip), `3861f08d` (batch-2), `17565057` (batch-3a), `60489e34` (batch-3b), `4b1c690b` (batch-3c) and current HEAD; blob size 11632 = file size; HEAD == origin/main == `4b1c690b`. The pre-batch tip `ab20cebe` carries a DIFFERENT gate blob (`b5725cb6…`), exactly as expected because 600→1200 landed in batch-1 — the card entered on precisely the content those batches pushed. Method note: content compared via `rev-parse`/`hash-object`, never via a `git show |` string pipeline (encoding-unsafe for this non-ASCII file).

### F-4 — Claims vs evidence (integrity smokes): VERIFIED — honest, not deleted

- `compileall` rc=0 in the `commands.json` ledger with raw outputs present (`_ca_stdout.txt` 0 B / `_ca_stderr.txt` 0 B — quiet success); `ruff` rc=0 with raw "All checks passed!"; ast retry rc=0 "AST OK: both files parse"; `--help` rc=0 with full usage and the boundary note — no gate step output anywhere, i3 held.
- **The disclosed first-attempt ast rc=1 is PRESENT and annotated (honesty, not deletion)**: raw `evidence/_ast_stderr.txt` retains the bare-`import` SyntaxError; `ast_compileall_ruff.txt` carries the appended disclosure (Start-Process ArgumentList quoting artifact; retry rc=0; compileall/ruff of that unit valid); `commands.json` C7 and `handoff.json` C7 both record `raw_rc: 1` with the note rather than smoothing it to 0.
- **GBK-artifact bonus disclosure (honesty signal)**: `json_validation.txt` discloses a first-attempt pwsh JSON validation FAILURE (GBK read-side quote-swallowing) as "VOID AS A FILE VERDICT" before the authoritative python pass — failure disclosed, not hidden.
- Arithmetic spot-checks re-computed exactly: 1200−1182.3 = 17.7 s (≈1.48 % of cap); 1800−1182.3 = 617.7 s; 1800/1182.3 = 1.522 (+52.2 %); 1800/691.71 = 2.60 (2.6×); 300/44.00 = 6.82 (6.8×); 300/120 = 2.5; 120/44 = 2.73 (≥2.7× inflation already observed) — `decision.md`/`oracle.md` §6 re-compute exactly.

### F-5 — The two f2 runs and the mutation cross-check: VERIFIED

- `f2_standalone_timeout300.txt`: rc=0, raw `1 passed in 59.69s`; wall 79.4 == recorded window 18:35:34.9208963Z→18:36:54.2853784Z (79.36 s) ✓; ambient python 2→2, "no burners started by this card"; test-state sha `98ddcdc7…` ✓.
- `f2_mutation_120_rerun.txt`: rc=0, raw `1 passed in 59.45s`; wall 67.6 == window 18:37:11.8158024Z→18:38:19.4359784Z (67.62 s) ✓; `mutation_state_sha256` = `0bcd7ac8…0856e` equals the before-hash AND the reviewer's independent re-hash of the before-copy → **`mutation_state_equals_before_hash: True` is byte-equal TRUE**; its HONEST READING header matches pre-registered oracle §5.5 (pass at BOTH 120 and 300 ⇒ standalone cannot distinguish ⇒ NOT load-proven standalone).
- Final state restored and re-verified by the reviewer now: gate `3df161a7…`, test `98ddcdc7…`; `final_state_verification.json` agrees (`timeout=300 restored`, mutation fully undone).

### F-6 — No load faking (0 burners): VERIFIED by spot-check

- Ambient counts on every ambient-bearing artifact: 2 at freeze (`oracle_freeze.json`), 2/2 around the timeout-300 run, 2/2 around the mutation run.
- The full `commands.json` ledger contains no burner/spammer/load-inducing command; the sole subprocesses evidenced are the two exact-node pytest runs, compileall/ruff/ast, and `--help`.
- Repo-root `.tmp-r41-mutation/` predates this card (created 2026-09-20 18:31 local) and is unrelated. The claimed "0 burners" is consistent with each observable — nothing suggests induced, faked, or inflated load in either direction.

### F-7 — Honest-uncertainty parity: CORE VERIFIED

- `handoff.json` carries: `status: review_pending` (pre-verdict, as it must be before landing); `reviewer_status.implementer_signed: false` with "implementer never signs acceptance"; `qualification_state` `disclosure_adaptation: "unmapped"`, `accuracy: "unproven"`.
- `reviewer_status.not_granted` includes **"load-proof of either fix (stays owed to batch-4 push)"** verbatim. **U-1** present with correct direction (standalone passes at BOTH 120 and 300 ⇒ cannot claim load-proof; 300 = ~6.8× the 44.00 s baseline, 2.5× the failed value); **U-2** present (1800 never live-GREEN-proven here; worst 1182.3 s → 617.7 s margin / +52.2 % headroom vs 17.7 s / +1.5 % at 1200). U-3 plus `open_questions_disposition` carry **OQ-03 as `carried_open`** / "not in this card's authorization" — OQ-03 untouched ✓.

### F-8 — Minor, non-blocking: two U-items lacked three literal figures — FIXED DURING LANDING

- The briefing specified U-1 must carry "failure needed ≥2.7× inflation" and U-2 must carry "2.6× normal 691.71 s" and "bounded"; those clauses were NOT in `handoff.json` (greps for `2.7`, `691`, `2.6`, `bounded` returned no hit there). They DO exist inside the same card: ≥2.7× in `decision.md` Fix-2 §2 and oracle §6; 2.6×/691.71 s in `decision.md` Fix-1 §3 and oracle §6; "bounded" in `decision.md` Fix-1 §5 / Fix-2 §3 and oracle §6. Substance and direction of the honest uncertainty were fully carried; the gap was only which deliverable file holds which figure; no overclaim anywhere. Reviewer treated it as **non-blocking** and offered the remedy: a one-line append to U-1/U-2, no re-verification cycle needed.
- **Landed per the reviewer's option:** this pass appended the three literal figures to the existing U-1/U-2 entries in `handoff.json` (U-1: "failure needed ≥2.7× inflation"; U-2: "2.6× the normal-domain 691.71 s" + "bounded, not unbounded") and marked both entries `f8_parity_supplemented: true` with the note that the figures were already in `decision.md`/oracle §6 and were added for literal handoff parity per reviewer F-8. No other content of those entries changed; no re-verification cycle was needed or performed.

### F-9 — Boundaries: VERIFIED (exactly 2 production files touched by this card)

- mtime scan of `tools/` + `tests/` for LastWriteTime in the card's window 19:30–19:47 local returns exactly the two authorized files — `tools/pre_push_gate.py` (19:34:01) and `tests/test_fc1105_fault_injection.py` (19:38:37) — plus `__pycache__` `.pyc` byproducts of compileall/pytest (untracked/ignored; absent from `git status --porcelain`).
- The five ` M scripts/*.py` entries in `git status --porcelain` (incl. CW `scripts/company_wiki_source.py`) each carry mtimes BEFORE the window opened (2026-09-21 21:14/21:21/21:29/21:32 and 2026-09-22 10:36 local) — not written by this card. `.planning/.../progress.md` is in-window (18:36:25Z) but disclosed as parallel-card/lifecycle-written; this card's ledger contains no command that writes it.
- `commands.json` records solely read-only git verbs (`status`, `diff`, `numstat`, `rev-parse`, `reflog`, `show`); no add/commit/push/stash/checkout/reset/restore. Reviewer's external corroboration: **reflog has ZERO entries during 19:30–19:47** (last commit 14:03 local, batch-3c), the **index is empty** (staged set = 0 paths), and **HEAD == origin/main == `4b1c690b`** now equals the freeze-time value (**HEAD unchanged**).
- `handoff.json` `changed_paths` = exactly the two files; `changed_paths_statement` confines remaining writes to this attempt directory — consistent with the file inventory (24 files, all inside the attempt dir except the two targets).

### F-10 — Commit-scope warning: CONSISTENT with observable state

- `handoff.json` `git_writes.commit_scope_for_parent` instructs: commit EXACTLY `tools/pre_push_gate.py` + `tests/test_fc1105_fault_injection.py`, with an explicit "do NOT `git add -A`" because the shared worktree carries unrelated modifications; `shared_workspace_disclosure.observed_not_mine` names the 5 scripts/CW files (with pre-window mtimes), `progress.md`, and the untracked `PROMOTION-EXEC/` + `B3-PREREQ/.../iso/` dirs. The reviewer's own read-only `git status --porcelain` shows precisely that set — the warning is consistent with what is on disk.
- Wording note: the card hedges attribution as "parallel section-18 cards AND pre-existing drift", while the parent briefing states the scripts/CW changes "belong to the parallel PROMOTION-EXEC card (mtimes = source-preserved copies)". The card's hedged wording is the weaker/safer claim — no conflict to resolve; PROMOTION-EXEC itself is NOT reviewed (explicitly out of scope).

### F-11 — Deliverable pins and given inputs: RE-VERIFIED

- **14/14 deliverable sha256 values** recorded in `evidence/final_deliverable_hashes.json` re-computed against the current files: **0 mismatches** (oracle, binding, commands, decision, changes.diff, handoff, and 8 evidence files).
- Given inputs (not re-timed, spot-corroborated read-only at their cited sources in `GATE-TIMEOUT-1200/a20260922-01`): `gate_green_1200.txt` L66 "1 failed, 63 passed, 1 xfailed … in 1159.84s"; real-data wall 1182.3 s in `commands.json` L63; `"real_data": 691.71` in G2 `per_step_wall_s`; `1 passed in 44.00s` in `evidence/f2_standalone_lightload.txt` L2; f2 FAILED line at L65.
- Oracle pre-registration quality note (observation, not a violation): oracle §5 named planned artifacts `evidence/compileall.txt` / `ast_check.txt` / `help_smoke.txt` / `ruff_two_files.txt`; actual capture consolidated them into `ast_compileall_ruff.txt` + `ast_and_help_smoke.txt` (+ raw `_ca_*`/`_ruff_*`/`_ast_*` parts) and `handoff.json` evidence_paths point at the actual names — substance of every pre-registered check is present, merely filenames differ from the freeze-time plan.

## Reviewer's flagged observation (recorded for the parent)

REM-79 checker item (carrier L247–L250): the checker used for the report's self-check is the **frozen v1.2.0-correction2 copy under `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/`** (the attempt's frozen copy); the **repo-root `tools/check_domain_assertions.py` named in that card's handoff is NOT present in the live tree** (Test-Path false) — noted for the parent, not investigated further. The REM-79 self-check over `reviewer_report.md` before pinning: **0 violations, exit 0** (carrier L252–L255).

## Unverified / not reviewed (explicit list, carrier L229–L250)

1. **Full gate run — never executed** by the card nor by the review (card boundary i3 + review boundary); consequently no live RED/GREEN of any gate step here.
2. **Load-side behavior of both fixes** — `timeout=1800` under real ambient load and f2 inside a loaded real-data suite are NOT demonstrated (U-1/U-2; `load-proof` stays `not_granted`); owed to batch-4's live push.
3. **PROMOTION-EXEC card and its scripts/CW modifications** — out of scope; only GATE-OQ-FIX's boundary claim/consistency with observable mtimes/status was confirmed, not PROMOTION-EXEC's ownership.
4. **Completeness of `commands.json`** — an absent-command claim can never be proven from inside; corroborated solely by reflog/index/HEAD/mtime evidence (F-9).
5. **Given inputs 1182.3 s / 691.71 s / 44.00 s** — spot-corroborated at source but not independently re-timed (oracle §2 designates them already-confirmed).
6. **Remote state** (GitHub Actions, `origin/main` beyond equality at review time) — no network access used; not checked.
7. **OQ-03 substance** (GBK UnicodeDecodeError reader-thread warnings) — untouched by this card, remains registered-open, not reviewed here.
8. **REM-79 checker provenance** — frozen v1.2.0-correction2 copy used; repo-root `tools/check_domain_assertions.py` absent from the live tree (see observation above).

## Scope note — conditions of this acceptance (carrier L257–L271, verbatim in substance)

`accepted_scoped` grants exactly this: the two edits as written are surgical, authorized (§十八 B), and evidence-backed, with honest uncertainty preserved. It grants **NO load-proof, NO accuracy, NO disclosure mapping**. Specifically:

- **OQ-01 / OQ-02 load-side GREEN is owed by batch-4's live push** (real-data step completes <1800 s under that push's ambient load; `test_f2_missing_samples_fails` passes inside the loaded real-data suite) — per oracle §5.6 and §十八 execution order.
- **OQ-03 remains registered-open** (out of this card's authorization).
- `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`; **commit/push of the two files remains the parent's reserved action** (§十八 iii).
- F-8 is recorded as a non-blocking documentation gap, not a condition of acceptance — and was fixed during this landing per the reviewer's remedy option (see F-8 above).

## Not granted / boundaries of THIS file

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; load-proof of either fix stays **not_granted** (owed to batch-4 push). This landing grants no extension of scope beyond the carrier's scope note. Commit authority stays with the parent (§十八 iii). **0 production writes** by this landing: `reviewer_report.md` + `reviewer_report.sha256` untouched (0 bytes), no git command executed, no pytest/gate run, no signature produced.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this pass on the parent's dispatch; the verdict itself was authored only at `reviewer_report.md` L3 by 独立复核 — never by the implementer and never by this file's author.
- Exactly three files written: `review.md` (created, this file), `handoff.json` (status + status_before_bookkeeping_fix + status_authority + bookkeeping + F-8 parity supplement on U-1/U-2 + 11 carried findings appended + stale pre-verdict fields superseded under `*_historical_pre_verdict`; all other pre-existing keys untouched), `evidence/GATE-OQ-FIX/qualification.json` (created).
- sha256 before → after: `review.md` **none (absent) → created, hash reported to the parent** (a file cannot embed its own final hash); `handoff.json` **`0a02a80abbedcab04e72b3d4865d47aca766eccb20589e0fbccaccc45af569ad` (14558 B, == the pin in `final_deliverable_hashes.json`) → post-edit hash reported to the parent**; `qualification.json` **none (absent) → created, hash reported to the parent**. Post-write, `reviewer_report.md` re-hashes to `478ef11d…f9280` / 18628 B (0 bytes written to the carrier).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; `verdict_is_transcribed_not_authored: true`.
