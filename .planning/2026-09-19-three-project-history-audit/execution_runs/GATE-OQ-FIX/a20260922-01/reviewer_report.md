# Independent review — card GATE-OQ-FIX, attempt a20260922-01

**Verdict: `accepted_scoped`**

- Reviewer: independent reviewer (subagent of session-bfecd191-fbc3-4a66-8ed1-6562479bf102),
  NOT the implementer. Implementer did not sign acceptance (verified: `handoff.json`
  `reviewer_status.implementer_signed = false`, state `review_pending`).
- Method: sampled independent verification on 2026-09-22 (local, UTC+1). Tools limited to
  read / grep / pwsh (read-only inspection). **No full gate run ever** (boundary honored:
  this review executed no `pre_push_gate.py` run and no pytest run). No git writes of any
  kind by this reviewer. Production READ-ONLY during review: this reviewer modified exactly
  2 files — `reviewer_report.md` and `reviewer_report.sha256` — both inside this attempt dir.
- Hashes below were re-computed by this reviewer during this review unless explicitly
  marked "given" (already-confirmed inputs per oracle §2).
- Authority: `OWNER_DECISIONS.md` §十八 row 「B = 全批」 clears §十七 B-7 and dispatches this
  card (e29afc4): "real-data 门 1200→1800（仅该步）、f2 内部 timeout 120→300". The verbatim
  owner quote carried in `oracle.md` §1, `binding.json` and `handoff.json` matches the owner
  document. OQ-03 is outside this authority and the card treats it as out of scope (correct).

---

## Findings

### F-1 — Oracle frozen before any target-byte change: VERIFIED (with 2 briefing corrections)

Re-measured CreationTime/UTC of each file in the attempt, sorted:

| artifact | CreationTime (local UTC+1) | CreationTime (UTC) |
|---|---|---|
| `before/*.orig` (2 byte-copies) | 19:30:39.18 | 18:30:39Z |
| `oracle.md` | 19:33:04.575 | 18:33:04.575Z |
| `evidence/oracle_freeze.json` | 19:33:15.470 | 18:33:15.470Z (record: `frozen_utc` 18:33:14.8071481Z) |
| `binding.json` | 19:33:39.257 | 18:33:39Z |
| `changes.diff` | 19:34:10 | 18:34:10Z |
| `tools/pre_push_gate.py` (live mtime, Fix-1 apply) | 19:34:01 | 18:34:01Z |
| `tests/test_fc1105_fault_injection.py` (live mtime, final restore) | 19:38:37 | 18:38:37Z |

- Freeze record `evidence/oracle_freeze.json` is present; its `oracle_sha256`
  `b08b51df…aae5851` re-computes to the actual sha256 of `oracle.md` (exact match); both
  `before_sha256` pins inside it equal this reviewer's independent re-hashes of the two
  `before/*.orig` copies (exact match); it asserts `both_files_untouched_at_freeze: true`,
  `edits_applied_at_freeze: false`, empty scoped porcelain, HEAD `4b1c690b`.
- **No byte of either target file was written before the freeze instant**: first target
  mtime 18:34:01Z, freeze 18:33:14.8Z — the freeze rule as written in oracle.md holds and
  is confirmed by an independent clock reading, not solely by the card's own record.
- **Correction 1 (briefing data belongs to a sibling card):** the cited
  "oracle 19:38:36.358 = earliest, binding +0.6s" is NOT this card's measurement. Those
  exact values match `PROMOTION-EXEC/a20260922-01` (oracle.md C=19:38:36.3583778,
  binding.json C=19:38:36.9710668 → +0.61s). GATE-OQ-FIX's own freeze is 19:33:04 /
  19:33:15 local. The parent instruction conflated the two attempts; GATE-OQ-FIX passes on
  its own numbers.
- **Correction 2 ("oracle = earliest file in the attempt" is literally false here):**
  `before/pre_push_gate.py.orig` and `before/test_fc1105_fault_injection.py.orig` were
  created 2 min 25 s BEFORE `oracle.md` (C1 snapshot step, 18:30:39Z). Those are read-only
  copies — copying a snapshot modifies no target byte — so the substantive freeze property
  (finding above) is intact. Flagged so the parent does not repeat the "earliest file"
  formulation against this attempt.

### F-2 — The two edits are surgical: VERIFIED

- `changes.diff` sha256 re-computed = `e821500800ee5814fe71bed1c0ec434b14a3f73b2558ee0baf76c3053243951b`
  (matches the expected `e8215008…` pin and `final_deliverable_hashes.json`).
- Exactly **2** `diff --git` headers, no third file, no mode/rename/hunk noise:
  1. `tools/pre_push_gate.py` — +1/−0. Hunk header `@@ … @@ def _real_data() -> int`;
     the single added line is `        timeout=1800,` inside `_real_data()`'s `>_run(...)`
     call, between the label argument and the closing paren. Diff index line
     `483486bd..9004104d`.
  2. `tests/test_fc1105_fault_injection.py` — +1/−1. Line 60 in the `_t2()` helper:
     `timeout=120,` → `timeout=300,`. Diff index line `59d8a3c8..787141fd`.
- **`_run` default intact**: live `tools/pre_push_gate.py` L73 still reads
  `def _run(cmd, label, timeout: int = 1200, *, blocking: bool = True)`.
- **No other call site changed**: line-level `Compare-Object` of `before/*.orig` vs live —
  gate 281→282 lines with exactly one added object (`timeout=1800,`); test 169→169 lines
  with exactly one swapped object (120→300 line). The remaining timeout-bearing lines in
  the live gate (L83 `timeout=timeout` internal pass-through, L238 pytest `--timeout=180`)
  are unchanged, and test L158's pre-existing `timeout=60` is byte-identical to the
  before-copy (also side-checked in `evidence/json_validation.txt`).
- **Live re-hashes**: `tools/pre_push_gate.py` = `3df161a7ceea17de95b36845bdb3c4cee729dca215c56853868780dce7331484`
  ✓ and `tests/test_fc1105_fault_injection.py` = `98ddcdc70b208a35b87b89d83870fe8985156e94ea6596dd6c2b02e6335f8e62`
  ✓ — both match `binding.json` `hash_anchors_after`, `handoff.json`, `final_state_verification.json`
  and `final_deliverable_hashes.json`.
- `evidence/git_diff_final_after_mutation_restore.txt` (git's own final diff) re-hashes to
  the SAME `e8215008…` value as `changes.diff` — the recorded diff is the post-restore
  worktree state byte-for-byte.

### F-3 — Before-pins and the batch-1..3 push-pin: VERIFIED

- `before/pre_push_gate.py.orig` sha256 re-computed = `cf09ade8164e89d79237ff5A8409496AB1AE2A9C5F3EE2C253CCAD20EF06DF0B` (case-normalized: `cf09ade8…6df0b`) ✓; the
  test before-copy = `0bcd7ac81dba2c03362c9d0fa21ef59188f096f872b49e6efffc9cb028a0856e` ✓.
- **`cf09ade8…` IS the batch-1..3 push-pinned gate hash (confirmed):** the before-copy's
  git blob (`git hash-object` on the copy) = `483486bdd14084f573c0c64f2996c8ae7c4b81d4`,
  and `git rev-parse <tip>:tools/pre_push_gate.py` returns the identical blob
  `483486bd…` at `6f74b056` (batch-1 tip), `3861f08d` (batch-2), `17565057` (batch-3a),
  `60489e34` (batch-3b), `4b1c690b` (batch-3c) and current HEAD; blob size 11632 = file
  size; HEAD == origin/main == `4b1c690b`. The pre-batch tip `ab20cebe` carries a
  DIFFERENT gate blob (`b5725cb6…`), exactly as expected because 600→1200 landed in
  batch-1. So the card entered on precisely the content those batches pushed.
  (Method note: content was compared via `git rev-parse`/`hash-object <file>`, never via a
  `git show |` string pipeline, which is encoding-unsafe for this non-ASCII file.)

### F-4 — Claims vs evidence (integrity smokes): VERIFIED — honest, not deleted

- `compileall` rc=0 recorded in the `commands.json` ledger with raw outputs present
  (`_ca_stdout.txt` 0 B, `_ca_stderr.txt` 0 B — quiet success); `ruff` rc=0 with raw
  `_ruff_stdout.txt` = "All checks passed!"; ast retry rc=0 "AST OK: both files parse" in
  `ast_and_help_smoke.txt`; `--help` rc=0 with full usage printed and the boundary note
  (argparse answers before any gate step) — no gate step output appears anywhere, i3 held.
- **The disclosed first-attempt ast rc=1 is PRESENT and annotated (honesty, not deletion):**
  raw `evidence/_ast_stderr.txt` retains the bare-`import` SyntaxError, and
  `ast_compileall_ruff.txt` carries the appended disclosure (Start-Process ArgumentList
  quoting artifact; retry rc=0; compileall/ruff of that unit valid). `commands.json` C7 and
  `handoff.json` C7 both record `raw_rc: 1` with the note rather than smoothing it to 0.
- Additional honesty signal: `json_validation.txt` discloses a first-attempt pwsh JSON
  validation FAILURE (GBK read-side quote-swallowing) as "VOID AS A FILE VERDICT" before the
  authoritative python pass — failure disclosed, not hidden.
- Arithmetic spot-checks (re-computed): 1200−1182.3 = 17.7 s (≈1.48% of cap); 1800−1182.3
  = 617.7 s; 1800/1182.3 = 1.522 (+52.2% headroom); 1800/691.71 = 2.60 (2.6×);
  300/44.00 = 6.82 (6.8×); 300/120 = 2.5; 120/44 = 2.73 (≥2.7× inflation already observed).
  The statements in `decision.md`/`oracle.md` §6 re-compute exactly.

### F-5 — The two f2 runs and the mutation cross-check: VERIFIED

- `f2_standalone_timeout300.txt`: rc=0, raw `1 passed in 59.69s`; wall_s 79.4 equals the
  recorded window 18:35:34.9208963Z→18:36:54.2853784Z (79.36 s) ✓; ambient python 2→2,
  "no burners started by this card"; test-state sha recorded as `98ddcdc7…` ✓.
- `f2_mutation_120_rerun.txt`: rc=0, raw `1 passed in 59.45s`; wall 67.6 s equals window
  18:37:11.8158024Z→18:38:19.4359784Z (67.62 s) ✓; `mutation_state_sha256` =
  `0bcd7ac8…0856e` equals the before-hash AND equals this reviewer's independent re-hash of
  the before-copy → the claim `mutation_state_equals_before_hash: True` is a true statement
  (cross-check file checked against the actual bytes); its HONEST READING header matches the
  pre-registered oracle §5.5 wording (pass at BOTH 120 and 300 ⇒ standalone cannot
  distinguish ⇒ NOT load-proven standalone).
- Final state restored and re-verified by this reviewer now: gate `3df161a7…`, test
  `98ddcdc7…`; `final_state_verification.json` agrees (`timeout=300 restored`, mutation
  fully undone).

### F-6 — No load faking (0 burners): VERIFIED by spot-check

- Ambient counts recorded on each ambient-bearing evidence artifact: 2 at freeze
  (`oracle_freeze.json`), 2/2 around the timeout-300 run, 2/2 around the mutation run.
- The full `commands.json` ledger contains no burner/spammer/load-inducing command; the
  sole subprocesses evidenced are the two exact-node pytest runs, compileall/ruff/ast, and
  `--help`.
- Repo-root `.tmp-r41-mutation/` (a possible ambient suspect) predates this card —
  created 2026-09-20 18:31 local — and is unrelated to this attempt.
- The claimed "0 burners" is consistent with each observable; nothing in evidence suggests
  induced, faked or inflated load in either direction.

### F-7 — Honest-uncertainty parity: CORE VERIFIED

`handoff.json` carries: `status: review_pending`; `reviewer_status.implementer_signed:
false` with "implementer never signs acceptance"; `qualification_state`
`disclosure_adaptation: "unmapped"`, `accuracy: "unproven"`; `reviewer_status.not_granted`
includes **"load-proof of either fix (stays owed to batch-4 push)"** (the `load-proof
not_granted` entry, verbatim); U-1 present with the correct direction (standalone passes at
BOTH 120 and 300 ⇒ cannot claim load-proof; 300 = ~6.8× the 44.00 s baseline; 2.5× the
failed value) and U-2 present (1800 never live-GREEN-proven here; worst 1182.3 s → 617.7 s
margin / +52.2% headroom vs 17.7 s / +1.5% at 1200). U-3 plus
`open_questions_disposition` carry OQ-03 as `carried_open` / "not in this card's
authorization" — OQ-03 untouched ✓.

### F-8 — Minor, non-blocking: two U-items do not carry three of the enumerated figures

The briefing specified U-1 must carry "failure needed ≥2.7× inflation" and U-2 must carry
"2.6× normal 691.71 s" and "bounded". Those clauses are NOT in `handoff.json` (greps for
`2.7`, `691`, `2.6`, `bounded` return no hit there). They DO exist inside the same card:
≥2.7× in `decision.md` Fix-2 §2 and oracle §6 (`120/44 ≈ 2.7×`); 2.6×/691.71 s in
`decision.md` Fix-1 §3 and oracle §6; "bounded" in `decision.md` Fix-1 §5 / Fix-2 §3 and
oracle §6. Substance and direction of the honest uncertainty are fully carried; the gap is
merely which deliverable file holds which figure, and no overclaim exists anywhere. Treated as
non-blocking. If the parent wants literal handoff parity, the remedy is a one-line append to
U-1/U-2 (no re-verification cycle needed).

### F-9 — Boundaries: VERIFIED (exactly 2 production files touched by this card)

- mtime scan of `tools/` + `tests/` for LastWriteTime in the card's window 19:30–19:47
  local returns: `tools/pre_push_gate.py` (19:34:01) and
  `tests/test_fc1105_fault_injection.py` (19:38:37) — exactly the two authorized files —
  plus `__pycache__` `.pyc` byproducts of compileall/pytest (untracked/ignored; they do not
  appear in `git status --porcelain`).
- The five ` M scripts/*.py` entries seen in `git status --porcelain` (incl. CW
  `scripts/company_wiki_source.py`) each carry mtimes BEFORE the window opened:
  2026-09-21 21:14/21:21/21:29/21:32 and 2026-09-22 10:36 local — not written by this
  card. `.planning/.../progress.md` is in-window (18:36:25Z) but disclosed by the card as
  parallel-card/lifecycle-written, and this card's ledger contains no command that writes it.
- `commands.json` records solely read-only git verbs (`status`, `diff`, `numstat`,
  `rev-parse`, `reflog`, `show`); no add/commit/push/stash/checkout/reset/restore. External
  corroboration by this reviewer: reflog has **zero** entries during 19:30–19:47 (last
  commit 14:03 local, batch-3c), the index is empty (staged set = 0 paths), and
  HEAD == origin/main == `4b1c690b` now equals the freeze-time value.
- `handoff.json` `changed_paths` = exactly the two files; its
  `changed_paths_statement` confines the remaining writes to this attempt directory — consistent
  with the file inventory (24 files, all inside the attempt dir except the two targets).

### F-10 — Commit-scope warning: CONSISTENT with observable state

`handoff.json` `git_writes.commit_scope_for_parent` instructs: commit EXACTLY
`tools/pre_push_gate.py` + `tests/test_fc1105_fault_injection.py`, with an explicit
"do NOT `git add -A`" because the shared worktree carries unrelated modifications; the
`shared_workspace_disclosure.observed_not_mine` list names the 5 scripts/CW files (with
their pre-window mtimes), `progress.md`, and the untracked `PROMOTION-EXEC/` +
`B3-PREREQ/.../iso/` dirs. This reviewer's own read-only `git status --porcelain` shows
precisely that set — the warning is consistent with what is actually on disk.
Wording note: the card hedges attribution as "parallel section-18 cards AND pre-existing
drift", while the parent briefing states the scripts/CW changes "belong to the parallel
PROMOTION-EXEC card (mtimes = source-preserved copies)". The card's hedged wording is the
weaker/safer claim, so there is no conflict to resolve here; PROMOTION-EXEC itself is NOT
reviewed in this review (explicitly out of scope).

### F-11 — Deliverable pins and given inputs: RE-VERIFIED

- 14/14 deliverable sha256 values recorded in `evidence/final_deliverable_hashes.json`
  re-computed against the current files: 0 mismatches (oracle, binding, commands, decision,
  changes.diff, handoff, and 8 evidence files).
- The given inputs (not re-timed, but spot-corroborated read-only at their cited sources in
  `GATE-TIMEOUT-1200/a20260922-01`): `gate_green_1200.txt` L66 "1 failed, 63 passed, 1
  xfailed … in 1159.84s"; real-data wall 1182.3 s in `commands.json` L63; `"real_data":
  691.71` in G2 `per_step_wall_s`; `1 passed in 44.00s` in
  `evidence/f2_standalone_lightload.txt` L2; f2 FAILED line at L65.
- Oracle pre-registration quality note (observation, not a violation): oracle §5 named
  planned artifacts `evidence/compileall.txt` / `ast_check.txt` / `help_smoke.txt` /
  `ruff_two_files.txt`; the actual capture consolidated them into
  `ast_compileall_ruff.txt` + `ast_and_help_smoke.txt` (+ raw `_ca_*`/`_ruff_*`/`_ast_*`
  parts), and `handoff.json` evidence_paths point at the actual names. Substance of each
  pre-registered check is present; merely the filenames differ from the freeze-time plan.

---

## Unverified / not reviewed (explicit list)

1. **Full gate run — never executed** by the card nor by this review (card boundary i3 and
   this review's boundary). Consequently: no live RED/GREEN of any gate step here.
2. **Load-side behavior of both fixes** — `timeout=1800` under real ambient load and f2
   inside a loaded real-data suite are NOT demonstrated (U-1/U-2; `load-proof` stays
   `not_granted`). Owed to batch-4's live push.
3. **PROMOTION-EXEC card and its scripts/CW modifications** — out of scope; this review merely
   confirmed that GATE-OQ-FIX's boundary claim and warning are consistent with observable
   mtimes/status, not that PROMOTION-EXEC actually owns those changes.
4. **Completeness of `commands.json`** — an absent-command claim can never be proven from
   inside; corroborated solely by reflog/index/HEAD/mtime evidence listed in F-9.
5. **Given inputs 1182.3 s / 691.71 s / 44.00 s** — spot-corroborated at source but not
   independently re-timed (oracle §2 designates them already-confirmed).
6. **Remote state** (GitHub Actions runs, `origin/main` beyond equality at review time) —
   no network access used; not checked.
7. **OQ-03 substance** (GBK UnicodeDecodeError reader-thread warnings) — untouched by this
   card, remains registered-open, not reviewed here.
8. REM-79 checker used here is the frozen v1.2.0-correction2 copy under
   `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/`; the repository-root
   `tools/check_domain_assertions.py` named in that card's handoff is NOT present in the
   live tree (Test-Path false) — noted for the parent, not investigated further.

## REM-79 self-check (mechanized, on this report text)

`check_domain_assertions.py` v1.2.0-correction2 (lexicon v2 frozen), read-only, run over
`reviewer_report.md` before pinning: **0 violations, exit 0.**

## Scope note (conditions of this acceptance)

`accepted_scoped` grants exactly this: the two edits as written are surgical, authorized
(§十八 B), and evidence-backed, with honest uncertainty preserved. It grants NO
load-proof, NO accuracy, NO disclosure mapping. Specifically:

- **OQ-01 / OQ-02 load-side GREEN is owed by batch-4's live push** (real-data step
  completes <1800 s under that push's ambient load; `test_f2_missing_samples_fails` passes
  inside the loaded real-data suite) — per oracle §5.6 and §十八 execution order.
- **OQ-03 remains registered-open** (out of this card's authorization).
- `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`; commit/push of the
  two files remains the parent's reserved action (§十八 iii).
- F-8 is recorded as a non-blocking documentation gap, not a condition of acceptance.

— independent reviewer, 2026-09-22, sample-based verification, no full gate run.
