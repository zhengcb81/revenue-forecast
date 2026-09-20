# I-14-C review.md

> ## PENDING independent review
> This section is written by the **implementer**. Nothing here is an acceptance.
> A separate session must independently re-derive at least one oracle value and attack the
> cases listed under "reviewer: attack first". The implementer has not signed this card.
>
> **r2 status (legacy note):** the original r2 review returned `changes_required`; those items
> were addressed, then superseded by r3 and r4. Kept only so the history stays readable.

> **r4 status: F-I14C-08 fixed and the missing output-fidelity criterion is now in place;
> still PENDING independent review.** The r3 tree duplicated the key in the output
> (`tokentoken=<redacted>`). The fix and the exact-output assertions live in the r4 tree
> `iso/product_fixed` (hashes in `r4/final_hashes.json`); the r3 tree is preserved as the
> specimen `iso/product_r3/` so the new criterion can be shown to catch it, and the r2 tree
> as `iso/product_r2/`. The r1 after-tree remains withdrawn.
>
> **r3 status (superseded):** F-I14C-07 fixed; the r2 tree is superseded and its numbers are
> kept only for the regression comparison.
>
> **r2 status (superseded):** the r1 `changes_required` items were addressed at the time.
> The r1 implementation was withdrawn by the reviewer (product tree restored to HEAD); from
> r2 onward the fix exists only under `iso/`.

> **r5 status: all six r5 action items closed; still PENDING independent review.**
> The r4 review returned `changes_required` for a narrow scope and stated that **F-I14C-08
> itself can be closed** (its basis is recorded below and in `handoff.json`). Every number in
> this section comes from `r5/counts.json` or a captured command output; the r1/r2/r3/r4
> trees remain as specimens. The r4 review's own "unable to verify" list is answered in
> "r5 — what the reviewer could not verify" below, including the two items this round changed
> so that they CAN be verified next time.

## r5 — disposition of the r4 review findings

### F-I14C-R4-01 (P3, pair count wrong in five places) — FIXED, mechanically

`harness/report_counts.py` now derives every reportable number from the artefacts themselves
and writes `r5/counts.json`: rule table **44** entries (32 credential / 9 untouched /
3 residual), diagnostic corpus **30**, `FIDELITY_CASES` **28**, `exact_nodeids` **28**, total
collected **82** — the two independently derived pair counts agree, and the script exits 3 if
they ever disagree. The wrong "23" is corrected in all five places
(`harness/tests/test_i14c_real_exit_redaction.py:219` block → points at `counts.json`,
`review.md:76`, `decision.md:114`, `handoff.json:8/103`, `commands.json`
`CMD-I14C-R4-SUITE.purpose`), each with a note that r4's own value was 24 and r5's is 28.
My first r5 draft of the C13 test also hard-coded the reviewer's `112` against this attempt's
shorter marker and went red — same failure mode, now replaced by computed lengths.

### F-I14C-R4-02 (P2, C13 understated by ~an order of magnitude) — FIXED

Reproduced independently with this attempt's marker and with the reviewer's:
`'upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure
request_id=req-1'` → `'upload failed for token=<redacted>'`; the reviewer's 24-char marker
gives exactly **112 chars in, 34 out**, and `doc=17`, `stage=summarize`,
`code=llm_global_failure`, `request_id=req-1` are all gone. The cause is the value's stop set
(`,;&"'|` + whitespace): an unquoted value **crosses the newline** and keeps consuming. It is
not truncation (34 ≪ 200) and **not introduced by r3/r4** — `iso/product_r2` behaves the same.

- The consequence text is corrected in four places: `oracle.md` §R5 addendum, the carries
  list in this file (C13), `decision.md` D3-r4/D4-r5, and `handoff.json` `open_questions` +
  `r4_disposition.C13`.
- The blind direction is closed with explicit expectations frozen as CURRENT behaviour:
  rule table `cred-multiline-swallow`, `cred-multiline-stopped-by-semicolon`,
  `cred-multiline-then-key`; diagnostic corpus `cred-multiline-swallow` plus
  `diag-multiline-no-credential`; `FIDELITY_CASES` gains three multi-line pairs (the swallow,
  the `;`-protected tail, and the plain `token=<marker>\nnext=1` case) and one untouched
  multi-line diagnostic. `test_f08_c13_multiline_loss_is_frozen_not_hidden` asserts the loss
  explicitly (and would go red if the behaviour changed without the text being updated).
- No code change was needed and **E4b's 193 baseline is untouched** (the greedy value is what
  produces it), as the reviewer required.

### F-I14C-R4-03 (P3, flake claims unverifiable) — FIXED, and the retracted claim replaced

`harness/run_flake_evidence.py` now writes stdout, the raw return code and a verdict per run.
The captured result **contradicts** the r4 sentence, which is therefore retracted:

| node | basetemp (cwd length) | T0 pristine | T4 fixed |
|---|---|---|---|
| `child_without_runtime_session...` | deep attempt path, cwd 167 chars | **failed 3/3** | **failed 3/3** |
| `logon_wrapper_detaches_a_live_supervisor_with_quoted_paths` | deep attempt path, cwd 166 chars | **failed 3/3** | **failed 3/3** |
| `child_without_runtime_session...` | short `%TEMP%\i14c-flake-short`, cwd 75 chars | **passed 3/3** | **passed 3/3** |
| `logon_wrapper_detaches_a_live_supervisor_with_quoted_paths` | short `%TEMP%\i14c-flake-short`, cwd 74 chars | **passed 3/3** | **passed 3/3** |

Both placements are regenerable by the same script (`--basetemp-root` / `--out-root`), so this
table is not a one-off observation: the deep path fails 12/12 on both trees with
`WinError 206 文件名或扩展名太长` (path too long) and a downstream `FileNotFoundError` for
`worker_launcher_events.jsonl`, and the short path passes 12/12 on both trees.

The two failure signatures are different and both are environmental. At the deep basetemp the
failure is the path limit itself (`WinError 206`, then a `FileNotFoundError` for
`worker_launcher_events.jsonl`). At the short basetemp the failure is timing:
`assert len([e for e in events if e["status"] == "child_started"]) == 2` with **`assert 3 == 2`** —
a third `child_started` event, i.e. the supervisor restarted the child one extra time.

That timing failure is what motivated a proper measurement, because during the investigation an
ad-hoc short-basetemp capture happened to show it on T4 in 2 of 3 runs and never on T0, which
would have looked like a card-caused regression. It is not: a first frequency pass
(`harness/run_flake_frequency.py`, 12 runs per tree, short basetemp `%TEMP%\i14c-flake-freq`) gave
T0 6/12 vs T4 5/12 and an immediate re-run of the same command gave T0 0/12 vs T4 7/12 — the 2-of-3
observation was noise, and the ordering (all T0 runs, then all T4 runs) let machine-load drift
masquerade as a tree difference. The script therefore now **interleaves** (one T0 run, one T4 run,
repeating) and reports each pass separately. Final recorded run
(`r5/flake-evidence/frequency-child_without_runtime.json`):

| pass | T0 pristine | T4 fixed |
|---|---|---|
| pass 1 (12 runs each, interleaved) | 3/12 failed | 2/12 failed |
| pass 2 (12 runs each, interleaved) | 3/12 failed | 4/12 failed |
| pooled (24 runs each) | **6/24 failed** | **6/24 failed** |

Every failure is the same `assert 3 == 2` on `child_started`, and **the tree with more failures
flips between passes** (and flipped the other way in a preceding pass: T0 2/12 vs T4 4/12) —
which is exactly what a noise-dominated ~25 % flake looks like. Pooled over 24 interleaved runs
per tree the two trees are indistinguishable (6 vs 6). So the node is timing-flaky in the
product's own test at roughly that rate on both trees, and the card cannot have caused it:
the only `worker.py` hunks in this diff are the `observability` import line and
`_write_unhandled_exception_event` (see `r5-changes.diff`), neither of which is on that node's
path. Evidence: `r5/flake-evidence/summary.json` and
`r5/flake-evidence/frequency-child_without_runtime.json`.

### The compat suite does not fail with a stable set — so the criterion is the union plus T0 evidence

r4's compat control claimed "both trees: 4 failed / 27 passed with the IDENTICAL failure set".
r5 ran the same suite five times (twice on T0, twice on T4, plus the plain delivered run). In the
final recorded pass the four control runs each failed exactly 4 of 31 with the same four node
ids on both trees, and the plain T4 run failed 3:

| run | count | failing node ids |
|---|---|---|
| T0-1, T0-2, T4-1, T4-2 | 4 each | `read_desired_state…`, `stderr_exit_zero…`, `stale_child_heartbeat…`, `logon_wrapper…quoted_paths` |
| T4 plain | 3 | the same minus `logon_wrapper…quoted_paths` |
| an earlier pass (not the recorded one) | 3, 4, 4, 5, 5 | the extra/missing node was always `child_without_runtime…` |

So the unions are equal in the recorded pass, and the counts are not stable across passes — the
flake band observed at r5 is 3–5 failures out of 31. `harness/analyze_compat_control.py`
(`r5/compat-control-analysis.json`) therefore does not rest on the union alone: it also checks
every node that failed *only* on T4 in the current pass against the dedicated interleaved T0
frequency evidence, which is how the earlier pass's T4-only node was resolved (it fails on the
pristine T0 tree in 6 of 24 runs with the identical `assert 3 == 2` on `child_started`). Recorded
verdict: *"no card-specific compat failure: every T4 failure also occurs on T0"*,
`unproven_t4_only_nodes` empty, `only_on_T4` empty, rc 0.

Notes for the reviewer: (1) `4 failed / 27 passed` must not be quoted as a fixed expectation —
the observed band is 3–5; (2) two of the varying nodes are restart-timing nodes and the one that
comes and goes in the plain run is the path-length node above, i.e. the same environment classes;
(3) no compat failure had a fixed-tree-only signature in any pass.

### F-I14C-R4-04 (P3, patch not consumable) — FIXED and verified by `git apply`

`harness/make_posix_diff.py` now produces the patch the way git itself would (scratch repo,
`core.autocrlf=false`), giving `--- a/src/...` / `+++ b/src/...` with no backslashes:
`r5-changes.diff`, 6 hunks, 15,083 bytes. Verified: `git apply --check -p1` and
`git apply -p1` inside a scratch repo return 0 and the three files become **byte-identical**
to `iso/product_fixed` (`r5/git_apply_verification.json`, `GIT_APPLY_REPRODUCES_T4 true`).
Note for the reviewer: `git apply` outside a repository reports "Skipped patch" for these
files (whitespace/non-repo handling); run it inside a repo or with `git apply --directory`.
One prerequisite was found and fixed: `iso/product_fixed/.../observability.py` was LF while its
pristine counterpart is CRLF, which made the patch a whole-file rewrite; normalising the line
endings reduced it to a single hunk. Only that file was affected, and the content is unchanged
(the post-normalisation suite is still 82 passed).

### F-I14C-R4-05 (P3, diagnostic table had no helper fallback) — FIXED

`run_diagnostic_table.py` now mirrors `run_rule_table.py`: a missing helper writes
`helper_present: false`, `verdict: cannot_adjudicate` and exits **2**. Verified on the pristine
tree: diagnostics on `iso/product` → rc=2, `helper_present false` (no traceback).

### F-I14C-R4-06 (P3, exit-code drift) — FIXED by adopting the `run_card.py` convention

Both tables now use `0 = pass`, `2 = cannot adjudicate` (helper absent), `3 = negative verdict`
(fidelity failure, credential leak, or a NEW over-redaction). Registered over-redaction
(`known_over_redaction`) is what the diagnostic table measures and does not by itself make the
verdict negative. Re-run results:

| tree | rule rc | diag rc | note |
|---|---|---|---|
| T0 pristine | 2 | 2 | helper absent |
| T1 (r1) | **3** | **3** | 11 leaks / 4 leaks |
| T2 (r2) | 0 | 0 | pass |
| T3 (r3 specimen) | **3** | **3** | 0 leaks, 27 / 13 fidelity failures |
| T4 (r5) | 0 | 0 | pass |

### F-I14C-R4-07 (P3, hash snapshot gaps) — FIXED

`r5/final_hashes.json` restores the attempt-directory porcelain summary (both the entry set and
a per-directory roll-up) and adds hashes for `iso/product_r3` (the r3 comparison tree) and for
the `iso/venv` evidence (`python.exe`, `pyvenv.cfg`, the three installed distributions'
`RECORD` files and a `pip list` capture) so the binding's `pytest==9.1.1` / `pyyaml==6.0.3` /
`requests==2.34.2` claims are checkable.

### F-I14C-08 — CLOSED (the r4 review's own basis, recorded as required)

`handoff.json` records: **closed on the strength of the independent review's mutation proof and
its self-chosen marker reproduction**, not on the implementer's summary. The reviewer
independently reproduced `token=<their own marker>` → `tokentoken=<redacted>` on
`iso/product_r3` and → `token=<redacted>` on the fixed tree; injected the defect into a
byte-copy of the fixed tree and observed both tables exit negative (2 under the old scheme)
with 24 / 12 fidelity failures while `credential_leaks` stayed **0** — i.e. the criterion, not
the old leak check, is what catches it. This attempt did not re-litigate that; it only
re-ran the same tables on the line-ending-normalised tree (27 / 13 failures, still 0 leaks).

### r5 — what the reviewer could not verify, and what changed to fix that

| reviewer item | r5 action |
|---|---|
| #1 the 17 subprocess-backed cases could not be run outside `execution_runs` (driver refused with 97) | **fixed**: the guard now refuses product paths unconditionally and otherwise accepts a declared scratch root; the test helpers declare the pytest basetemp, so **the full 82-case suite runs from `%TEMP%` with no env var at all** (`r5/cmd-r5-outside-execution-runs.txt`, 82 passed). Refusals re-tested: product src, `.source_catalog`, revenue-forecast outside `.planning`, undeclared TEMP → 97 each; declared TEMP + product path → 97 |
| #2 flake conclusions unverifiable | **fixed**: `r5/flake-evidence/` with per-run stdout/rc/verdict, and the r4 claim retracted |
| #3 34/20/193 baselines not re-run | still only self-produced; the probe evidence is now `r5/probe_results_r5-after.json` and the lengths are re-derived on the normalised tree |
| #4 other bench shapes not re-computed | unchanged; the reviewer's one-shape spot check agreed with the order of magnitude |
| #5 `2f5c5740…` provenance | stays "untraceable" (F-I14C-04) |
| #6 `iso/product_r3` provenance | unchanged; it is now additionally hashed in `r5/final_hashes.json` |
| #7 controlled cwd scan | **fixed**: `r5/flake-evidence/summary.json` (deep, cwd 166/167 chars), `short-basetemp/summary.json` (short, cwd 74/75) and `frequency-child_without_runtime.json` (24 interleaved runs per tree) together separate the path-length limit from the timing flake on both trees |
| #8 venv contents unverified | **fixed**: venv evidence added to `r5/final_hashes.json` (`python.exe`, `pyvenv.cfg`, the three `RECORD` files, captured `pip list`) |
| #9 no product-side timeout wrapper exists | unchanged by design; C12 remains a hard precondition (C9: the test is not promoted) |
| #10 (r5's own) are the r5 commands reproducible in one pass? | **yes**: `harness/run_r5_commands.py` executed all 29 invocations in a single pass and recorded every raw rc in `r5/commands-r5-rc.json` with `all_as_expected=true`; `harness/sync_commands_json.py` folded them into `commands.json` mechanically, so no return code in the ledger was typed by hand |
| #11 (r5's own) is the flake/attribution reasoning stable? | **yes, and it is stated as a band, not a point**: the compat failure count moves in a 3–5 band and the T0/T4 frequency difference flips between passes; the analysis therefore checks T4-only nodes against interleaved T0 evidence instead of trusting one comparison |

## r4 — disposition of the r3 review findings

### F-I14C-08 (P1, new in r3) — FIXED, and the process gap that allowed it is closed

- **Root cause** confirmed exactly as reported:
  `iso/product_fixed/src/company_wiki/source_catalog/observability.py:378` (r3 numbering)
  appended `text[cursor:index]` **after** the character loop had already emitted the key, so
  the key appeared twice. Removed; the loop now emits only the separator, the whitespace after
  it and `REDACT` (the code comment names F-I14C-08 so it cannot silently return).
  The specimen `iso/product_r3/` reproduces the reported outputs verbatim
  (`token=` → `tokentoken=<redacted>`, `GITHUB_TOKEN=` → `GITHUB_TOKENGITHUB_TOKEN=<redacted>`,
  `password: '…'` → `passwordpassword: <redacted>`, `db.passwd=` → `db.passwdpasswd=<redacted>`).
- **The real defect was my criterion, not only the code.** Every r2/r3 check asked only "is
  the marker gone?" / "did the text change?", so a mangled key passed:
  `rule_table` 0 leaks, `diagnostics` 0 over-redaction, 50 suite tests green, E5a stderr 0 hits.
  Now both tables and the suite pin an **exact expected output per entry**, and the table
  scripts **exit 2** on any fidelity failure, so "0 leaks" can no longer be reported without
  also passing fidelity:

  | tree | rule table rc | credential leaks | fidelity failures |
  |---|---|---|---|
  | T0 pristine | 0 (helper absent — reported as such, not as a leak) | n/a | n/a |
  | T1 (r1) | **2** | 11 | 11 |
  | T2 (r2) | 0 | 0 | 0 |
  | **T3 (r3, duplicate key)** | **2** | **0** | **24** |
  | **T4 (r4, the fix)** | **0** | **0** | **0** |

  The 41-entry fidelity table is the evidence that the new criterion is load-bearing: the r3
  specimen shows `0 leaks` **and** 24 fidelity failures, i.e. exactly the blindness the
  reviewer identified.
- **Diagnostic table** (`run_diagnostic_table.py`, now also fidelity-checked, rc 2 on any
  mismatch) with the four C11 over-redactions classified as `known_over_redaction`
  (expected = the measured redacted form) and a `new_over_redaction` list for strict
  diagnostic entries:

  | tree | rc | leaks | known over-redacted | NEW over-redaction | fidelity |
  |---|---|---|---|---|---|
  | T1 (r1) | 2 | 4 | 3 | 0 | 5 failures |
  | T2 (r2) | 0 | 0 | 4 | 0 | OK |
  | T3 (r3 spec.) | 2 | 0 | 4 | 0 | 12 failures |
  | T4 (r4) | 0 | 0 | 4 | 0 | OK |
- **Baselines restored at the real exits** (`r4/probe_results_r4-after.json`):

  | case | r2 | r3 (defect) | **r4** |
  |---|---|---|---|
  | E2b `message_redacted` | `upload failed for token=<redacted>` (34) | `…tokentoken=<redacted>` (39) | **`upload failed for token=<redacted>` (34)** |
  | E4a | `password: <redacted>` (20) | `passwordpassword: <redacted>` (28) | **`password: <redacted>` (20)** |
  | E4b | len 193 | len 198 | **len 193** |

  and E5a's envelope again identifies the file: `…\config\token=<redacted>'` with no
  `tokentoken` (`r4/cli-r4-E5a/stderr.txt`), stderr marker hits 0, `catalogs_created == []`.
- **New tests**: `test_f08_output_fidelity_exact` (**24** exact pairs at r4 — corrected here by
  F-I14C-R4-01 from the "23" this line used to say; r5 extends the block to 28, see
  `r5/counts.json`),
  `test_f08_persisted_event_keeps_the_key_verbatim` (event string + the 34 length),
  `test_f08_e5a_envelope_still_identifies_the_config_file`
  (`harness/tests/test_i14c_real_exit_redaction.py:218-292`). Suite on r4: **76 passed**
  (was 50).

### C12 raised from advice to a hard precondition (reviewer item 4)

The reviewer's independent runs hung twice on `-k f07` against `iso/product_r2` (>90 s, then
>300 s killed), reproducing what this attempt measured (>60 s, killed). Confirmed consequence:
the 5 s assertion fires only **after** `redact_text` returns, so a blocking implementation
hangs the session instead of failing.

**Hard precondition for promotion** (not a recommendation): the promoted test MUST add
`pytest-timeout` with a per-test cap, or run the call in a subprocess with a hard timeout, so a
super-linear regressor produces a FAILURE. Until then the case stays in the harness, where
`harness/bench_redact.py` (20 s per-case subprocess cap) is the discriminator.

### C13 registered (found by the new fidelity table itself)

`"a=1 token=<marker> b=2"` → `a=1 token=<redacted>`: the value is the whole space/tab
separated run, not one token — the r1 `_BARE_VALUE` semantics (`X+(?:\s+X+)*`), which the
scanner reproduces. Consequence: **prose after a credential on the same line is redacted too**
(diagnostic loss, not a leak).

- **Kept deliberately**, for two reasons: (a) the reviewer's E4b acceptance number (193) is
  computed from that greedy behaviour, and (b) a quoted value already takes precedence and real
  credential values do not contain spaces.
- Narrowing it to a single token would change the E4b baseline and the observable envelope
  width, so it needs its own oracle; registered rather than changed. Frozen in the tables as
  `cred-line-middle-greedy-value` (expected `a=1 token=<redacted>`) plus
  `cred-line-middle-trailing-punct` (`…; b=2` survives, because `;` is a value delimiter).

### Carries C1–C12 retained; C8/C10/C11 unchanged (reviewer item 5)

C8's corrected reason stands; C10 (JSON quoted-key) and C11 (4 over-redactions incl. the
r2-new `pwd=`) are unchanged and still measured. C12 is now a promotion precondition and C13
is new.

### Reviewer item 6 — semantics do not need reverting

The reviewer compared r2 and r3 on five shapes and found the redaction verdicts identical, with
every observable difference caused by the duplicate-key defect. r4 keeps the scanner (no
revert) and re-freezes it **with the fidelity assertions**, which is the basis the reviewer
asked for to distinguish "improved" from "broken": T2 and T4 are fidelity-clean and leak-free;
T3 is red on fidelity only; T1 is red on leaks.

### Reviewer item 7 — workspace-level footprint attribution (recorded)

`catalog.sqlite3-shm` was touched at **02:33:45** and **03:08:06**; both are attributed to
**concurrently running other cards** (I-04-C / I-05-A / I-07-A / I-08-B / M05–M08), **not to
I-14-C**, and no write was committed. Measured state after all r4 work:

| artifact | value |
|---|---|
| `catalog.sqlite3` | 49,677,344,768 bytes, mtime 2026-09-19T06:31:35.406919Z (pre-dates every shm touch → no write since) |
| `catalog.sqlite3-wal` | 0 bytes (no uncommitted transaction) |
| `catalog.sqlite3-shm` | 32,768 bytes, mtime 2026-09-20T02:25:33.257649Z (another concurrent touch; the 02:33:45 / 03:08:06 entries are the reviewer's observations) |
| `worker_control.json` | sha256 `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd` (unchanged, `desired_state: paused`) |

I-14-C's own r4 runs never open a production catalog: every run's `result.json` records
`catalogs_created == []`, and the E5 harness fails at config resolution inside the attempt dir.

### Product contract tests on r4 — the failure set is environment-dependent, not card-caused

Full-file compat runs (worker bootstrap + observability, against `iso/product_fixed/src`):

| tree | runs | result |
|---|---|---|
| T0 pristine | 2 | 4 failed / 27 passed — {read_desired_state, stderr_exit_zero, stale_child_heartbeat, logon_wrapper_quoted_paths} |
| T4 (r4) | 2 | **4 failed / 27 passed — the identical set** |

The fourth entry (`test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`) is
**cwd-dependent**: it passes in some cwds (the r2/r3 compat runs) and fails in others, and it
fails identically on the pristine tree, so it is not caused by this card. The observability
tests pass in every run. Evidence: `r4/compat-control-*`.

## r3 — disposition of the r2 review findings

The r2 review confirmed F-I14C-02/03/04/05/06 closed and opened one new P2 regression.

### F-I14C-07 (P2, new regression) — FIXED, with the design chosen by measurement

- **Regression reproduced** (`r3/bench_T2-r2-regressed.json` via `harness/bench_redact.py`,
  20 s per-case subprocess cap). The regressed r2 tree is preserved as the specimen
  `iso/product_r2/` (observability.py `af0a90a1…`). Seconds, r1 control included:

  | shape | k | T1 (r1) | T2 (r2 nested star) | **T3 (r3 scanner)** |
  |---|---|---|---|---|
  | `"a_"*k+"="` | 200 | 0.0000 | 0.0036 | **0.0001** |
  | " | 500 | 0.0000 | 0.0266 | **0.0006** |
  | " | 1000 | 0.0001 | 0.0873 | **0.0007** |
  | " | 2000 | 0.0001 | 0.3551 | **0.0014** |
  | " | 4000 | 0.0003 | 1.4784 | **0.0026** |
  | " | 8000 | 0.0008 | 10.5557 | **0.0054** |
  | " | 16000 | 0.0011 | **TIMEOUT** | **0.0103** |
  | " | 40000 | 0.0028 | **TIMEOUT** | **0.0253** |
  | `"a-"*k+"="` | 40000 | 0.0128 | TIMEOUT | **0.0271** |
  | `("a_"*k)[:-1]` (no separator) | 40000 | 0.0027 | TIMEOUT | **0.0108** |
  | `("a_"*k)+'="'+b*200` | 40000 | 0.0028 | TIMEOUT | **0.0255** |
  | `"k="*k` | 40000 | 0.0128 | 0.0120 | **0.0619** |
  | `"authorization: "*k` | 40000 | 0.0217 | 0.0159 | **0.0191** |
  | `"bearer "*k` | 40000 | 0.0171 | 0.0156 | **0.0146** |

  Full 10-shape × 8-k matrix: `r3/timing_three_way.json`. r2 grows ~×4 per doubling and hits
  the cap at 16000 on four shapes; r3 is linear, worst case 0.0619 s at k=40000.
- **Choice and why — option (a) as literally worded does NOT fix it, measured**:
  `r3/variants.json` compares four implementations on the same shapes.
  `A1-candidate+python` (`[A-Za-z0-9_-]+` + Python validation) is **also quadratic**
  (8000 → 2.66 s, 16000/40000 → TIMEOUT) because the key quantifier still backtracks once
  per start position when the value cannot match. `B-bounded` (`{0,8}`) is linear
  (40000 → 0.065 s) but silently stops covering keys with more than 8 qualifier segments — a
  coverage cliff in a security path. Option (c) leaves the regex super-linear just below any
  cap and changes what is redacted for over-cap input. **Chosen: a single-pass scanner**
  (`A2-scanner`), linear on every shape.
- **Implementation**: `iso/product_fixed/src/company_wiki/source_catalog/observability.py` —
  `_redact_assignments()` (~line 330) visits each `:`/`=` once, walks back over the key, and
  validates with `key_is_credential()` (~line 246) against `_SINGLE_ATOMS` (~206) /
  `_PAIR_ATOMS` (~220); `_find_closing_quote()` (~404) preserves the quoted-value semantics.
  The `authorization`/`bearer` pattern stays a regex because its keys are fixed literals with
  no nesting over the key, and its cost is in the table above.
- **Declared behavioural change** (not requested; measured as an improvement): a rejected key
  no longer consumes the whole `key=value` span, so a later genuine pair is still redacted
  (`url=https://x?token=…`, `cmd: --token=…`). Frozen in
  `test_f07_rejected_key_does_not_swallow_a_later_pair`
  (`harness/tests/test_i14c_real_exit_redaction.py:203-215`) together with the unchanged
  cases (`url=…?page=2`, `digest=<marker>`).
- **New cases** (`harness/tests/test_i14c_real_exit_redaction.py:172-201`): k=1000/2000/40000
  over four adversarial shapes with a 5.0 s deadline, asserting the text is unchanged, plus
  `test_f07_auth_regex_path_stays_linear` at k=20000. The deadline is a regression detector
  (r3 worst case 0.062 s vs r2 >20 s), not a service objective — recorded in `oracle.md`
  § R3 addendum.
- **The new case can actually go red** — demonstrated, not asserted: running only
  `test_f07_long_separator_run_finishes_within_the_deadline` against the regressed tree
  (`I14C_PRODUCT_SRC=iso/product_r2/src`) was **still running after 60 s and had to be
  killed** (`r3/cmd-f07-vs-r2/stdout.txt`).
  **Honest limitation of that case**: the 5 s assertion fires only *after* `redact_text`
  returns, so a full hang presents as a hung test session rather than a clean failure. The
  subprocess-capped `harness/bench_redact.py` is therefore the real discriminator, and if
  this test is promoted into the product repo it should wrap the call in a
  subprocess/timeout (or add `pytest-timeout`) so it fails fast. Recorded as carry **C12**.

### Regression check on r3 (nothing self-harmed)

| check | result |
|---|---|
| rule table (20 positives + 8 guards), `run_rule_table.py` | rc=0, **0 leaks, 0 over-redaction** |
| full suite, `pytest harness/tests/test_i14c_real_exit_redaction.py` | **rc=0, 50 passed** |
| probe per file, `run_exit_probe.py --label r3-after` | E1/E2a/E2a-deep/E2b/E3/**E4a**/**E4b**/E1-no-cli = 0/0/0; E2b-residual 1/1 by design |
| **E5a** real CLI, `run_real_cli_exit.py --shape E5a` | rc=1, `stderr hits 0`, envelope, `traceback False`, `catalogs_created 0` |
| E5b / E5c | unchanged carries (1 hit each, as declared) |
| E4a order-swap control | still leaks → R3 remains load-bearing |
| product contract tests on `iso/product_fixed/src` | 28 passed / 3 failed — the same 3 pre-existing failures (r3 measurement; **superseded in r5**: the count is not stable run to run, it moves in a 3–5 band — see the r5 compat section) |

### C8 reason corrected (reviewer item 1)

The r2 reason ("widening to whitespace would redact `token expired for doc-1`") was
**wrong**: `r3/diagnostics_product_r1.json` and `…_product_fixed.json` show the colon-less
form is unchanged in **both** trees; what is redacted is `token: expired`, already redacted
in **r1**. Rewritten in `decision.md` rejected-alternative 5 as: *the flag form needs new
separator semantics whose false-positive cost on ordinary `key value` prose exceeds its
benefit*.

### Over-redaction table, honest scope (reviewer item 2)

`harness/run_diagnostic_table.py` runs a 15-entry diagnostic corpus against each tree
(`r3/diagnostics_*.json`):

| entry | r1 | r2 | r3 | classification |
|---|---|---|---|---|
| `token: expired` | redacted | redacted | redacted | **pre-existing (r1) over-redaction** |
| `secret: rotated at …` | redacted | redacted | redacted | pre-existing (r1) |
| `password: ********` | redacted | redacted | redacted | pre-existing (r1) |
| `pwd=/home/user/project` | untouched | **redacted** | **redacted** | **r2-new over-redaction** |
| `key=value`, `stage=…`, `files_seen=0 …`, `elapsed_seconds=…`, `GET /v1/status returned 503`, `document not in catalog: doc-1`, `monkey=`, `oauth=`, `secretary=`, `tokenizer=`, `keyboard=` | untouched | untouched | untouched | no over-redaction |

So "0 over-redaction" holds only for the 5 guards in the rule table; the diagnostic corpus
shows **4** over-redactions, 3 pre-existing and 1 new in r2 (`pwd=`). `pwd` is **kept**
deliberately (password parameter in Oracle/SQL\*Plus-style connection strings) and registered
rather than removed — the tradeoff is explicit instead of hidden behind a "0" claim.

### C10 registered (reviewer item 3)

`{"api_key": "<marker>"}` — the JSON quoted-key form — is **not** covered. Measured as
surviving in all three trees (`r3/diagnostics_*.json` → `residuals_confirmed` includes
`res-json-quoted`). Pre-existing, not a regression.

### Carries after r3

C1 `digest=` · C2 `store._redact_message` · C3 `error_taxonomy.structured_error` +
`identity_cli.py:70-73` · C4 BaseException/interpreter traceback · C5 `_write_process_event`
not a gateway · C6 argparse (`cli.py:865`) · C7 non-credential-shaped marker · C8
`--api-key <value>` (reason corrected) · C9 acceptance test not promoted · **C10 JSON
quoted-key form** · **C11 four known over-redactions (`pwd=`, `token: expired`,
`secret: rotated`, `password: ********`)** · **C12 the F-07 deadline assertion only fires
after the call returns — a HARD precondition for promotion: add `pytest-timeout` or wrap the
call in a subprocess, otherwise a regressor hangs instead of failing** · **C13 the value is
the whole space/tab separated run, so prose after a credential on the same line is redacted
too (kept; E4b's 193 baseline depends on it)**.

## r2 — disposition of the r1 review findings

Frozen expectations for this round are in `oracle.md` § "R2 addendum" (written before any r2
run). Trees: `iso/product` = T0 pristine HEAD · `iso/product_r1` = T1 (`changes.diff`
applied, hash-verified by `harness/apply_card_diff.py`) · `iso/product_fixed` = T2 (the fix
under review) · `iso/product_swapped` = T3 (T2 with only `redact_and_truncate`'s two
operations exchanged). Production tree: read-only throughout.

### F-I14C-02 (P1, env-var keys) — FIXED, reproduced before/after

- Root cause confirmed exactly as reported: `\b` cannot match inside `GITHUB_TOKEN` /
  `my_access_token` because `_` is a word character.
- Fix: `iso/product_fixed/src/company_wiki/source_catalog/observability.py:203`
  (`_LEFT_ANCHOR = r"(?<![A-Za-z0-9])"`) applied at both `_AUTH_PATTERN` (line ~232) and
  `_CREDENTIAL_KEY` (line ~227); key expression is now
  `(?:[A-Za-z0-9]+[_-])*<atom>(?:[_-][A-Za-z0-9]+)*` so env-var names are covered, including
  the `<atom>_<suffix>` shape (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY_ID`).
- Reproduced on the r1 code: `harness/run_rule_table.py` against `iso/product_r1` →
  **9 of 20 positives leak** (`r2/rule_table_product_r1.json`): GITHUB_TOKEN,
  my_access_token, SLACK_BOT_TOKEN, AWS_SECRET_ACCESS_KEY, export GITHUB_TOKEN, GH_TOKEN,
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY_ID, MY_APP_PASSWORD.
- Fixed on T2: same table → **0 leaks, 0 over-redaction**
  (`r2/rule_table_product_fixed.json`). Pristine T0 reports `helper_present: false` (reported
  as "helper absent", not as a leak).
- All the reported shapes are now frozen positives in the rule table:
  `harness/tests/test_i14c_real_exit_redaction.py:206-222`.
- One self-invented positive was reclassified rather than satisfied by widening the rule:
  `--api-key <value>` (space-separated flag form) is now a **declared residual**
  (`test_i14c_real_exit_redaction.py:224`), with the reason recorded in `decision.md`
  rejected-alternative 5. Over-redaction guards `monkey=`, `oauth=`, `secretary=`,
  `tokenizer=`, `keyboard=` all still pass.

### F-I14C-03 (P1, the real CLI was never executed) — FIXED via reviewer option ①

- Root cause confirmed: T0 `cli.py:866 args.config.resolve(strict=True)` is outside
  `main`'s `try` (which starts at T0 line 951), so it escaped as a bare interpreter
  traceback.
- Fix: `iso/product_fixed/src/company_wiki/source_catalog/cli.py:860-873` adds
  `emit_redacted_error(exc)`; lines 874-887 wrap the three pre-`try` setup lines in a
  `try/except Exception` that calls it; `main`'s existing handler (now line ~1590) calls the
  same helper. One envelope implementation, no command semantics changed.
- **The real CLI is now executed** as a subprocess by `harness/run_real_cli_exit.py`:
  `python -m company_wiki.source_catalog.cli --config <missing path> status`, with a missing
  config path so no catalog is created or opened (`catalogs_created == []` in every case).
- E5a (credential-shaped missing file name `token=SYNTHETIC_AUDIT_TOKEN.yaml`):
  T0 → `returncode=1`, `bare_traceback_on_stderr=true`, `stderr marker hits=1`;
  T2 → `returncode=1`, `bare_traceback_on_stderr=false`,
  `structured_envelope_on_stderr=true`, **`stderr marker hits=0`**.
  Same for T1 (unchanged by the r1 fix).
- E5b (bare marker as a plain path component): T2 still shows `stderr marker hits=1` **by
  declaration** — a non-credential-shaped value is oracle R5's stated limit. Carried by name
  (see below), not claimed as covered.
- E5c (argparse failure): `returncode=2`, `stderr marker hits=1` on **all** trees including
  T2. argparse's own error path is a `SystemExit`, not the `except Exception` handler.
  **Carried by name.**
- The r1 artifact is also removed at its source: `harness/drive_real_exit.py:120-146` now
  imports the redactor defensively, so the pre-fix tree no longer produces an `ImportError`
  traceback that could be miscounted as a leak.

### F-I14C-04 (P2, the cli.py pre-image claim) — CORRECTED

- Corrected in `binding.json` (`source_anchors_sha256_verified_this_attempt` →
  `CW/src/company_wiki/source_catalog/cli.py`): pre-image is HEAD-CRLF
  `fad88c60294a7fb7fa87bbdbe2bbd7effe3ce1a2dbcc11fce96cd44afb36344b` / 65694 bytes;
  HEAD-LF is `5f182e36…` / 64126 bytes. The claim "HEAD is not the pre-image" was **wrong**
  and is marked as such; `porcelain_before` was clean for all three files.
- `2f5c5740…` / 65553 is recorded as **来源不可考**. It is not HEAD-LF, not HEAD-CRLF, not
  the r1-fixed file. The only arithmetic observation: 65553 = 64126 + 1427, i.e. it would be
  the HEAD content with exactly 1427 of 1568 line breaks converted to CRLF. Recorded as an
  unproven hypothesis, not as an explanation.
- Consequence: none for the runs. Every before/after tree was built by content splice with a
  recorded-hash check (`harness/apply_card_diff.py`, `harness/reverse_card_diff.py`), never
  from HEAD position, and the T0/T1/T2 hashes are in `r2/final_hashes.json`.
- This is the second hash correction in this attempt (the first was `error_taxonomy.py`,
  open gap 6 in the r1 section). Both are recorded rather than edited away.

### F-I14C-05 (P2, R3 was not load-bearing) — FIXED, with the control kept

- The reviewer was right: the r1 unquoted E4 passes under both orders, because a truncated
  unquoted value still matches the bare-value alternative.
- R3 restated as R3' in `oracle.md` § R2 addendum A2; the load-bearing shape is a **quoted**
  value the 200-char cut leaves unterminated (its leading quote excludes it from the
  bare-value alternative).
- E4a is now that shape: `harness/drive_real_exit.py` scenario
  `quoted-truncation-boundary` = `password: "` + 300×`Q` + `"`;
  test `test_e4a_quoted_value_truncation_never_leaks_LOAD_BEARING`
  (`harness/tests/test_i14c_real_exit_redaction.py:139-152`).
- Measured (`r2/probe_results_*.json`, per-case secret = a 20×`Q` probe string):

  | tree | E4a hits in the JSONL event |
  |---|---|
  | T0 (no redactor) | 9 |
  | T2 (redact → truncate) | **0** |
  | T3 (truncate → redact, the order swap) | **9** |

  i.e. 9 × 20 = 180 secret characters inside the 200-char window survive the swap, matching
  the reviewer's independent count of 189 characters for this shape. The control is a real
  test, `test_e4a_order_swap_control_leaks` (same file, line ~155), which asserts the swap
  DOES leak — it fails if E4a ever stops being load-bearing.
- E4b (the r1 unquoted case) is kept, explicitly labelled non-load-bearing, as a regression
  guard.

### F-I14C-06 (P3, accounting) — CORRECTED

- The r1 "E1 before = 2 hits" mixed one real leak (the JSONL event) with one `ImportError`
  artifact (the harness's own hard-coded `from … import redact_text` against the pre-fix
  tree). The driver is fixed as described under F-I14C-03, so the r2 counts are all genuine.
- r2 per-file table (`r2/probe_results_r2-before.json` vs `…-after.json`), secret per case:

  | case | before: event / stderr / stdout | after: event / stderr / stdout |
  |---|---|---|
  | E1 `Authorization: Bearer <marker>` | 1 / 1 / 0 | 0 / 0 / 0 |
  | E2a marker only in the cause | 0 / 0 / 0 | 0 / 0 / 0 |
  | E2a-deep two-level cause | 0 / 0 / 0 | 0 / 0 / 0 |
  | E2b `token=<marker>` | 1 / 1 / 0 | 0 / 0 / 0 |
  | E2b-residual `digest=<marker>` | 1 / 1 / 0 | 1 / 1 / 0 (declared residual) |
  | E3 no-secret | 0 / 0 / 0 | 0 / 0 / 0 |
  | E4a quoted truncation | 9 / 15 / 0 | 0 / 0 / 0 |
  | E4b unquoted truncation | 0 / 1 / 0 | 0 / 0 / 0 |
  | E1-no-cli (re-raise only) | 1 / 0 / 0 | 0 / 0 / 0 |

  E2a/E2a-deep are 0 in **both** trees: only the top message is persisted, and those top
  messages carry no marker. The r1 "1 hit"/"2 hits" for them were entirely the ImportError
  artifact — that is the corrected accounting, and it means the r1 claim that E2a
  "reproduced a leak" was overstated.

### Suite results (r2)

| run | command | result |
|---|---|---|
| before, T0 | `pytest … test_i14c_real_exit_redaction.py` (`I14C_PRODUCT_SRC=iso/product/src`) | **rc=1, 35 failed / 9 passed**; rule-table failures are `ImportError` (helper absent) and are listed separately from leaks |
| after, T2 | same suite, default `PRODUCT_SRC=iso/product_fixed/src` | **rc=0, 45 passed** |
| rule table, T1 | `run_rule_table.py --src iso/product_r1/src` | **9 leaks** (F-I14C-02 reproduction) |
| rule table, T2 | `run_rule_table.py --src iso/product_fixed/src` | **0 leaks, 0 over-redaction** |
| real CLI E5a/E5b/E5c | `run_real_cli_exit.py` on T0/T1/T2 | as tabulated above |
| backward compat, T2 | product `test_source_catalog_worker_bootstrap.py` + `test_observability.py` against `iso/product_fixed/src` | **rc=1, 28 passed / 3 failed** — the same 3 pre-existing environment/timing failures reproduced on T0 in r1 |

Evidence: `r2/cmd-r2-before/`, `r2/cmd-r2-after/`, `r2/cmd-compat/`, `r2/rule_table_*.json`,
`r2/probe_results_*.json`, `r2/cli-*/result.json`, `r2/final_hashes.json`.

### Carries registered by name (all verified by the reviewer, none fixed)

| id | carry | location | evidence |
|---|---|---|---|
| C1 | unknown key `digest=<marker>` still leaks | `observability.py` `_CREDENTIAL_KEY` | `r2/probe_results_r2-after.json` E2b-residual |
| C2 | `_redact_message` documents "sanitize" but only strips + truncates to 200 | `store.py:1480-1487` | read-only |
| C3 | `structured_error` returns raw `str(exc)`; real in-repo consumer prints it | `error_taxonomy.py:97-105`; consumer `identity_cli.py:70-73` | read-only |
| C4 | `BaseException` / interpreter-level traceback bypasses the handler | no `sys.excepthook` in the product | `decision.md` D1-r2 residual 3 |
| C5 | `_write_process_event` is not a general gateway (only the exception exit is gated) | `worker.py:1061+` | `decision.md` D1-r2 residual 4 |
| C6 | argparse error path echoes argv (E5c: rc=2, 1 stderr hit on every tree) | `cli.py:865` + `_parser()` | `r2/cli-product_fixed-E5c/result.json` |
| C7 | non-credential-shaped marker in a path still appears in the envelope (E5b) | oracle R5 limit | `r2/cli-product_fixed-E5b/result.json` |
| C8 | space-separated flag form `--api-key <value>` is not covered | rule design choice | `r2/rule_table_product_fixed.json` |
| C9 | the product's own prune test still encodes the wrong oracle (I-15-A's card) | `tests/contract/test_source_catalog_prune_retired.py` | I-15-A review |

### Reviewer test footprint (recorded, attributed, not repeated)

The reviewer's own use of the real CLI opened the **production catalog**: per the review
report, `catalog.sqlite3-shm` was touched at 01:43:06, the DB size/mtime did not change,
`-wal` was 0, no write was committed, and the processes were killed by 01:45. This attempt
does not repeat that: the E5 harness uses a **missing** config path inside the attempt dir,
so `run_real_cli_exit.py` records `catalogs_created == []` for every case and never opens the
production catalog. Recorded here so the footprint is visible in the card's own evidence.

Measured after all r2 work, for the record:

| artifact | value |
|---|---|
| `catalog.sqlite3` size | 49,677,344,768 (identical to the I-00-A baseline) |
| `catalog.sqlite3` mtime | 2026-09-19T06:31:35.4069191Z (older than the shm touch below → no write after it) |
| `catalog.sqlite3-wal` | 0 bytes (no uncommitted transaction) |
| `catalog.sqlite3-shm` | 32,768 bytes, mtime 2026-09-20T00:43:06.4941964Z — this is the reviewer's reported 01:43:06 touch |
| `worker_control.json` sha256 | `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd` (unchanged, `desired_state: paused`) |

### r2 isolation proof (the requirement that product copies live under `iso/`)

```
iso/venv/                 iso/ 解释器 (pytest 9.1.1 + pyyaml 6.0.3 + requests 2.34.2)
iso/product/              T0  pristine HEAD tree (module hashes == production)
iso/product_r1/           T1  T0 + changes.diff  (rebuild verified by apply_card_diff.py)
iso/product_fixed/        T2  T0 + r2 fixes      (the fix under review)
iso/product_swapped/      T3  T2 with only redact_and_truncate swapped (E4a control)
```

Every r2 run used `--src <attempt>/iso/<tree>/src` or `PYTHONPATH=<attempt>/iso/<tree>/src`;
no run read or wrote `C:\Users\...\company-wiki\src`. The production `git status --porcelain`
is ` M CLAUDE.md` / ` M README.md` only — the two pre-existing user edits — at the end of r2.


## What was done

I-14-C exists because the audit found the redaction claim rested on a *helper in isolation*.
`reviews/wiki_legacy/exception_event_probe.json` says so in its own words
(`"method_only": true`) and the only product test that touches the exit

> **NOTE (r2):** everything from here to the end of this section describes the **r1**
> attempt. Its numbers were partly contaminated by the harness `ImportError` artifact
> (F-I14C-06) and its "after" tree has since been withdrawn by the reviewer. Read the r2
> section above as the authoritative accounting; the r1 text is kept for traceability.
(`test_source_catalog_worker_bootstrap.py:288`) asserts on the **key name and length** of
`message_redacted` (`0 < len(msg) <= 200`) — a 200-char cut, not redaction.

This attempt (a) froze the requirement in `oracle.md` before any run, (b) reproduced the
leak through the real exit, (c) made a minimal change, (d) re-ran the same cases.

## Change summary (see `changes.diff`, 3 files, +110/-3)

- `CW:src/company_wiki/source_catalog/observability.py` — added `redact_text`,
  `redact_and_truncate`, `exception_cause_types`, `MAX_REDACTED_MESSAGE_CHARS` next to the
  existing `REDACT` / `_PATH_PATTERN` redaction. Rule is key-driven:
  `Authorization:`/`Bearer` plus a fixed credential-key set.
- `CW:src/company_wiki/source_catalog/worker.py` — `_write_unhandled_exception_event` now
  runs the message through `redact_and_truncate` (**redact first, truncate second**) and
  adds `cause_types` (type names only). Import added.
- `CW:src/company_wiki/source_catalog/cli.py` — the generic `except Exception` exit redacts
  the `error` field of the `structured_error` envelope before printing to stderr.

No file outside these three was written. `store.py`, `error_taxonomy.py`, `normalizer.py`,
all schemas and all production config/policy/worker_control are untouched.

## Evidence: before vs after, same cases, same harness

`harness/build_prefix_tree.py` rebuilds the pre-image of exactly the three edited modules
from `changes.diff` (the diff's '-' side), verifies each reconstruction against the hash
recorded before any edit, and refuses if the diff is stale or the file drifted. `HEAD` was
**not** usable as the pre-image: the committed `worker.py` is 46991 bytes vs 48075 in the
pre-edit worktree, i.e. these modules already carried uncommitted changes.

| case | before (pass1-prefix) | after (pass2-after) | expectation |
|---|---|---|---|
| E1 `Authorization: Bearer <marker>` + CLI exit | rc=1, **2 hits** | rc=3, 0 hits | closed |
| E2a marker only in the cause | rc=1, **1 hit** (stderr) | rc=3, 0 hits | closed |
| E2a-deep two-level cause | rc=1, **2 hits** | rc=3, 0 hits | closed |
| E2b `token=<marker>` | rc=1, **2 hits** | rc=3, 0 hits | closed |
| E4 credential straddling the 200-char cut | rc=1, **1 hit** + partial prefix `SYNTHETIC_AUDIT_T` | rc=3, 0 hits, len 193 | closed |
| E1-no-cli (re-raise path only) | rc=3, **1 hit** | rc=3, 0 hits | closed |
| E3 plain `KeyError`-style message | rc=1, 0 hits | rc=3, 0 hits, text unchanged | no regression |
| E2b-residual `digest=<marker>` (key outside the frozen set) | 2 hits | **2 hits, by design** | reserved, not hidden |

> **r2 correction to the table above (F-I14C-06):** the r1 "2 hits" entries each combined one
> genuine JSONL-event leak with one harness `ImportError` artifact on stderr, and the
> E2a/E2a-deep "1 hit"/"2 hits" were **entirely** artifacts. The driver is fixed and the r2
> per-file table above replaces this one. E4 here is the unquoted shape, renamed E4b in r2
> because it does not prove the redact-before-truncate ordering (F-I14C-05).

The before-pass pytest run of the same suite (`before/cmd-B1/stdout.txt`):
**21 failed / 2 passed**, and pytest's own traceback shows the raw marker inside the
persisted JSONL event — i.e. the counterexample is the real exit, not a helper.

The after-pass (`after/cmd-A4/stdout.txt`): **23 passed**, including
`test_real_exit_redacts_instead_of_dropping_the_field` (proves `<redacted>` is present, so
"the field was silently dropped" cannot be mistaken for a fix),
`test_real_exit_keeps_nonsensitive_diagnostics` (stage/code/request_id survive;
`cause_types == ["ValueError"]`) and `test_event_order_is_preserved_on_the_unhandled_path`
(`process_starting → session_opened → unhandled_exception → process_exiting`).

Backward compatibility (`after/cmd-A5`, `before/cmd-B2`): 28 passed / 3 failed with the fix,
and **the same 3 failed on the pre-image** — `test_read_desired_state_…` and
`test_stderr_exit_zero_…` fail with `FileNotFoundError` under this GBK-console/isolated
tmp environment, and `test_stale_child_heartbeat_…` is a timing assertion
(`session_start_timeout` vs `heartbeat_timeout`). None of the three touches redaction, and
the card's own exit-path test (`test_run_forever_writes_unhandled_exception_event_with_exception_type`)
passes in both passes.

## Fresh negative case the implementer did NOT use while writing the fix

Per review_and_handoff §5, a case reserved for the reviewer, expectation recorded **before**
looking at the result: `"x-api-key: mk-<marker>"` and `"Authorization: ApiKey <marker>"`
(colon form with a scheme not in {Bearer, token}) must both be redacted, because the frozen
rule redacts everything after `authorization:`/`bearer`. A third reserved case,
`"Bearer <marker>"` inside a *list* repr, e.g.
`"retries=[Bearer <marker>]"`, is expected to be redacted too (the `bearer` alternative has
no anchoring requirement).

## Open gaps / not verified

1. **Residual leak for unknown keys.** `digest=<marker>` survives (3 hits in
   `after/runs-pass2-after/E2b-residual`). This is the card's explicit "不声称覆盖全部未知
   secret 形式" clause, recorded rather than hidden. Anyone who wants content-independent
   redaction needs a different design (entropy/shape detection) and a separate oracle.
2. **`error_taxonomy.structured_error` still returns raw `str(exc)`.** A consumer that calls
   it directly (not through the CLI) still gets the unredacted value. See decision.md D1.
3. **`store._redact_message` is truncate-only** despite its name — flag `counterexample`
   for the normalizer owner.
4. **No product test was added.** The card allows editing "associated isolation tests", but
   the acceptance test above lives only in `harness/tests/`. Promotion into
   `CW/tests/contract/test_source_catalog_worker_bootstrap.py` (or a new
   `test_i14c_redaction.py`) is left as the next action, deliberately, so the reviewer can
   judge the test text before it enters the product repo.
5. **Bookkeeping discrepancy, unexplained.** The byte count recorded for `cli.py` at the
   start of this attempt (65553) does not match the CRLF form of its reconstructed pre-image
   (65694) even though the *digest* of that form matches the digest recorded in the same
   pass. `worker.py` and `observability.py` have no such mismatch. The before/after runs do
   not depend on the byte count (the hash is what is verified), but the discrepancy is left
   visible here instead of being smoothed over.
6. **One hash in `binding.json` was wrong and has been corrected.** The value first recorded
   for `CW/src/company_wiki/source_catalog/error_taxonomy.py` (`c0e8bd15…`) was never computed
   in this attempt. The verified value is
   `14e09c3d41c8584cb59c05ac47ef31c5d4a1e34103c70fb8f4e95e83588c5183` (4295 bytes; both
   `Get-FileHash` and `hashlib` agree, and `git hash-object` equals
   `HEAD:e3bee2c7d0a0fd468335ce0d9680179727b7d284`), so the file is genuinely unmodified and
   `binding.json` now records that with an explicit correction note. The reviewer should treat
   any other unaudited hash in the attempt's first binding pass with the same suspicion —
   every hash printed in the final report was recomputed at the end of the attempt.
7. **`_write_process_event` is not a general gateway.** Only the exception exit is gated;
   other `**extra` fields are not redacted. Scope decision recorded in decision.md D1
   (rejected alternative 4).
8. **Not covered:** `BaseException` subclasses that bypass `cli.py`'s `except Exception`
   (e.g. `KeyboardInterrupt`) still print a raw traceback to the launcher's stderr log; the
   worker's own `except BaseException` writes the redacted event but does not sanitise the
   interpreter-level traceback.

## reviewer: attack first (r2 — these supersede the r1 list below)

1. **F-I14C-02**: run `harness/run_rule_table.py --src iso/product_r1/src` yourself and
   confirm the leak count is 9, then against `iso/product_fixed/src` and confirm 0 leaks with
   0 over-redaction. Then try to break the *fixed* rule: propose a credential-shaped key the
   new expression still misses (candidates the implementer checked and believes covered:
   `AWS_SESSION_TOKEN`, `X-API-KEY`, `my_secret_v2`, `OpenAI_API_KEY`; candidates believed
   NOT covered: `--api-key <value>`, `Authorization` with no separator, a bare marker).
2. **F-I14C-03**: run `harness/run_real_cli_exit.py --shape E5a --src iso/product_fixed/src`
   and check `stderr marker hits == 0` and `catalogs_created == []`. Then attack the fix's
   completeness: is there any other statement in `main()` **above** the new `try` that can
   raise with attacker-influenced text? (Candidates: `sys.stdout.reconfigure`, the
   `argparse` call at T0 line 865 — the latter is carry C6.)
3. **F-I14C-05**: confirm the control tree really is a one-function difference —
   `diff iso/product_fixed/src/company_wiki/source_catalog/observability.py
   iso/product_swapped/src/company_wiki/source_catalog/observability.py` must show only
   `redact_and_truncate`. If it shows anything else, the control is invalid.
4. **F-I14C-04**: try to trace `2f5c5740…/65553` yourself (any blob in the object database,
   any stash/reflog, any CRLF/LF mix). If you can explain it, replace the
   "来源不可考" note with the evidence; if not, leave it as-is rather than deleting it.
5. **Accounting**: verify that no r2 number is read off a single combined total — every claim
   above is per file and the before-run rule-table failures are `ImportError`, not leaks.
6. **Residual honesty**: confirm the review/handoff text nowhere claims the stderr
   requirement is fully met — C6 (argparse) and C7 (non-credential-shaped marker) must be
   visible as open carries, and the I-15-A card must still read `blocked`.

## reviewer: attack first (r1, kept for traceability)

- Re-derive E4 by hand: build a message where the credential starts at char 190 and
  confirm the post-fix output has neither the marker nor a prefix of it. Then build one
  where the credential is split by a newline (`"token=\n<marker>"`) and report whether the
  frozen rule covers it — the implementer believes it does **not** and that this is an
  acceptable, disclosed limit.
- Check that `redact_and_truncate` redaction-before-truncation is what actually runs
  (swap the order in a scratch copy and confirm the E4 test goes red) — this is the one
  ordering claim that would silently regress. **(r2 note: the reviewer did exactly this and
  found the r1 E4 not load-bearing; E4a now is, see F-I14C-05.)**
- Confirm no candidate file other than the three diffed modules changed under
  `CW/src` (compare against `iso/product/src`, a full pristine copy).
- Confirm the CLI stderr redaction is not simply a duplicate of the worker redaction
  masking a second leak: `r2/probe_results_r2-after.json` E1 must show the envelope with
  `<redacted>` **and** `error_type`/`retryable`/`status` intact.


# r5 — INDEPENDENT REVIEW (round 5)

# I-14-C r5 独立定点复核报告（adversarial, 全程只读生产仓库）

- 复核人：独立 reviewer（第 5 轮，非实现者）
- 被复核对象：`PLAN\execution_runs\I-14-C\a20260919-01`（r5，2026-09-20 03:4x–04:4x）
- 复核窗口：本窗口 `REVIEWDIR=C:\Users\郑曾波\AppData\Local\Temp\i14c-r5-review-20260920-044801`，建立于 2026-09-20T03:48:01Z
- 解释器：`<attempt>\iso\venv\Scripts\python.exe`（3.13.9；未使用全局 Miniconda python）
- 生产仓库：`company-wiki` / `filing-fetch` / `revenue-forecast` 只读
- 所有结论均由本人重跑命令取得；未采信实现者任何结论性陈述

---

## VERDICT: `accepted_scoped`

**范围（与我第 4 轮口径一致）**：I-14-C 的**证据与判据**在这一轮成立 ——
(a) F-I14C-08 的关闭依据经本人第 4 轮独立复现并**在本轮以逐字符精确判据再次验证**；
(b) r4 review 的 **6 项整改全部逐条对号关闭**；
(c) r5 新增的**全部数字来自机械推导**，我独立重算**逐项相符**；
(d) 验收测试**仍未产品化**（C12 硬前置）——这是本卡**明示未做**的部分，不构成对本判定的否定，但 `accepted_scoped` **不等于批准促销**。

**本轮唯一"新"结论**：r5 把 r4 遗留的两条**"reviewer 无法验证"**通道真正打开了 ——
① 全部 82 个用例现在可由 reviewer 在自己目录内独立跑通（我实测 3 次：82 passed / 22.1 s、21.4 s、22.0 s，其中一次**完全不设** `I14C_RUN_ROOT`）；
② `r5-changes.diff` 可由**标准 `git apply`** 消费并**字节复原** T4（我实测 `--check` 与 `-p1` 均 rc=0，三文件 sha256 全等；且在**不设任何本地 git 配置覆盖**时同样成立）。

**3 项 P3/P4 文档级瑕疵**（见发现 1–3）**不阻塞本判定**，但建议在下一轮随其他改动一并清理：其中发现 1（`oracle.md` 的 r4 段被就地编辑而非追加）触到我上轮设定的"只许追加/不得改冻结件"边界 —— 我逐行核对后确认**冻结语义未被改动**，故不升级为阻断项。

---

## 一、请重点复核的 7 项 —— 逐项结论

### 1. F-I14C-08 关闭依据与保真断言 ✅ **全部成立**

**(1a) `iso/product_r3` 确实"0 泄漏但保真失败"，T4 确实 0/0。** 本人用**自己的命令**重跑十次表调用（5 树 × 2 表）：

```
run_rule_table.py       product        rc=2 verdict=cannot_adjudicate  leakers=0 fidfail=n/a entries=
run_rule_table.py       product_r1     rc=3 verdict=negative           leakers=11 fidfail=11 entries=44
run_rule_table.py       product_r2     rc=0 verdict=pass               leakers=0 fidfail=n/a entries=44
run_rule_table.py       product_r3     rc=3 verdict=negative           leakers=0  fidfail=27 entries=44
run_rule_table.py       product_fixed  rc=0 verdict=pass               leakers=0 fidfail=n/a entries=44
run_diagnostic_table.py product        rc=2 verdict=cannot_adjudicate  leakers=0 fidfail=n/a
run_diagnostic_table.py product_r1     rc=3 verdict=negative           leakers=4  fidfail=5
run_diagnostic_table.py product_r2     rc=0 verdict=pass               leakers=0 fidfail=n/a
run_diagnostic_table.py product_r3     rc=3 verdict=negative           leakers=0  fidfail=13
run_diagnostic_table.py product_fixed  rc=0 verdict=pass               leakers=0 fidfail=n/a
```

**T3 标本：`credential_leaks = 0` 且 `fidelity_failures = 27`（规则表）/ `13`（诊断表），rc=3 —— 与实现者自述逐字相符。T4：rc=0、0 泄漏、0 保真失败。** 负例全部如声明为负：T0 → rc=2（`cannot_adjudicate`，helper 缺失），T1 → rc=3。

**(1b) 保真判据确为逐字符精确 —— 用"仅差一个字符"的注入证明。** 我在 `%TEMP%` 自建两个变异体：

```
=== 变异 A：把 REDACT 由 '<redacted>' 改成 '<redacted>!'（每条凭据输出仅多 1 个字符）===
run_rule_table.py:       rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=32
   FIDELITY-FAIL cred-header-bearer expected='Authorization: <redacted>' got='Authorization: <redacted>!'
run_diagnostic_table.py: rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=15

=== 变异 B：把 ';' 从值终止集合中移除（精确命中 1 条规则表项 + 1 条新增多行项）===
run_rule_table.py:       rc=3 verdict=negative leaks=0 touched=0 new_over=0 fidelity_failures=2
   FIDELITY-FAIL cred-line-middle-trailing-punct expected='a=1 token=<redacted>; b=2' got='a=1 token=<redacted>'
   FIDELITY-FAIL cred-multiline-stopped-by-semicolon expected='failed for token=<redacted>; see log\nstage=summarize code=llm_global_failure' got='failed for token=<redacted>'
run_diagnostic_table.py: rc=0 verdict=pass     leaks=0 touched=0 new_over=0 fidelity_failures=0
```

变异 A **1 个字符的差异**即触发 rc=3 与 32 条失败；变异 B 说明判据是**逐条目**生效的（只命中受影响的两条，其余全绿）。**判据不是装饰性的，也不是"整表通过/整表失败"的粗门。**

**(1c) C13 的现状冻结确实显式化了（这正是我上轮 P2 的要求）。** 我从 `FIDELITY_CASES` 中提取到 **4 条含换行的用例**：

```
15: in='upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure request_id=req-1'
    expected='upload failed for token=<redacted>'
16: in='failed for token=<marker>; see log\nstage=summarize code=llm_global_failure'
    expected='failed for token=<redacted>; see log\nstage=summarize code=llm_global_failure'
17: in='token=<marker>\nnext=1'
    expected='token=<redacted>'
25: in='stage=summarize\ncode=llm_global_failure\nrequest_id=req-1'   (原样保留)
```

并用**我自己的 marker** 复算损失量，同时确认**不是截断造成的**：

```
product_r2     in_len=112 out_len=34  trunc_artifact=False  out='upload failed for token=<redacted>'
product_r3     in_len=112 out_len=39  trunc_artifact=False  out='upload failed for tokentoken=<redacted>'
product_fixed  in_len=112 out_len=34  trunc_artifact=False  out='upload failed for token=<redacted>'
```

新增测试 `test_f08_c13_multiline_loss_is_frozen_not_hidden` 同时用**本 attempt 的 marker 与我的 `ZQ7_REVIEWER_MARKER_9f3c`** 两种长度断言，且长度**由输入计算**而非硬编码（该测试文档自陈：r5 初稿硬编码我上轮的 112 并因此发红 —— 同一类"手打数字"失败，已被替换为计算值；这一自我披露是可信度的加分项）。

**(1d) 残余/极限形状与我上轮独立测得的完全一致**：`digest=`、`--api-key <v>`、JSON 引号键、裸 marker 仍存活（4 条已声明残留）；`monkey=` / `key=value` 未被触碰。

### 2. `r5-changes.diff` 的可用性 ✅ **可被标准 `git apply` 消费并字节复原 T4；r4 的反斜杠缺陷未回归**

本人的独立复现（自建 `%TEMP%` 仓库，不读实现者脚本）：

```
diff bytes=15083 header_lines=9
header lines containing a backslash: 0
POSIX_PATHS_ONLY = True
hunks = 6
git apply --check -p1 rc=0
git apply -p1       rc=0
  IDENTICAL worker.py:        applied=120561f5994e0ae0(48607B) T4=120561f5994e0ae0(48607B)
  IDENTICAL observability.py: applied=c5608c4b45a55cce(40060B) T4=c5608c4b45a55cce(40060B)
  IDENTICAL cli.py:           applied=4087c17230fc8ca7(66441B) T4=4087c17230fc8ca7(66441B)
  files in applied src tree that differ from T4: 0
GIT_APPLY_REPRODUCES_T4 = True
```

**加强验证**：我把 `core.autocrlf` / `core.safecrlf` 的**本地覆盖全部省略**（该机 global 配置三项均未设置，rc=1）后**重做一次**，结果相同：

```
global git config: core.autocrlf='' core.safecrlf='' core.eol=''   (all unset)
git apply --check -p1 rc=0 ; git apply -p1 rc=0 ; 三文件 IDENTICAL
ROBUST_WITHOUT_LOCAL_OVERRIDES = True
```

即补丁的可用性**不依赖** `core.autocrlf=false` 这类前置设置。头部形如 `diff --git a/src/... b/src/...`，**无反斜杠**（r4 缺陷未回归）。

### 3. `counts.json` 作为数字唯一来源 ✅ **独立重算逐项相符；自我校验确实存在且会发红**

我导入三张表（`run_rule_table.TABLE`、`run_diagnostic_table.CORPUS`、`test_i14c_real_exit_redaction.FIDELITY_CASES`）并用**独立调用 pytest `--collect-only`** 取节点数：

```
key                          mine                                       counts.json                                match
rule_table_entries           44                                         44                                         True
rule_table_by_kind           {'credential': 32, 'untouched': 9, 'residual': 3}  同                                  True
diagnostic_corpus_entries    30                                         30                                         True
diagnostic_corpus_by_kind    {'credential':11,'diagnostic':12,'known_over_redaction':4,'residual':3}  同         True
diagnostic_strict_entries    12                                         12                                         True
fidelity_cases               28                                         28                                         True
fidelity_unique_inputs       28                                         28                                         True
fidelity_unique_pairs        28                                         28                                         True
exact_nodeids                28                                         28                                         True
total_nodeids_collected      82                                         82                                         True
pytest_collect_returncode    0                                          0                                          True
pytest_collect_tail          82 tests collected in 0.05s                同                                         True
COUNTS_AGREE = True
rule_table_by_kind sums to entries: True
diag by_kind sums to entries: True
fidelity_cases == exact_nodeids: True
```

**自我校验确实存在**：`harness/report_counts.py` 末行

```python
# the nodeid count and the table length must agree; if not, one of them is wrong
return 0 if exact_nodeids == counts["fidelity_cases"] else 3
```

两处推导**彼此独立**：`fidelity_cases` 来自 `len(FIDELITY_CASES)`（模块导入），`exact_nodeids` 来自**调用 pytest 子进程**解析 `--collect-only` 输出（`"test_f08_output_fidelity_exact["` 行计数）。二者不等即 rc=3。另有 `test_f08_fidelity_pair_count_matches_the_mechanical_count` 在套件内同时断言 `counts["fidelity_cases"] == len(FIDELITY_CASES)` 与 `== counts["exact_nodeids"]`，使"手打数字"在**测试层**也无法存活。

### 4. 抖动结论按"区间 + 反证"阅读 ✅ **逐次捕获证据存在；cwd 长度是唯一受控变量**

**(4a) 深层/短路径的逐次捕获**（12 次运行，每次都有 rc + 完整 stdout + 分类判定）：

```
=== 深路径 basetemp（attempt 内），cwd 166/167 字符 ===
T0 child_without_runtime  run1/2/3  rc=1 failed cwd_len=167
T0 logon_wrapper_quoted   run1/2/3  rc=1 failed cwd_len=166
T4 child_without_runtime  run1/2/3  rc=1 failed cwd_len=167
T4 logon_wrapper_quoted   run1/2/3  rc=1 failed cwd_len=166
失败原文（T4 例）：FileNotFoundError: [WinError 206] 文件名或扩展名太长 ...
                 FileNotFoundError: [Errno 2] ... worker_launcher_events.jsonl
=== 短路径 basetemp（%TEMP%\i14c-flake-short），cwd 74/75 字符 ===
T0 child_without_runtime  run1/2/3  rc=0 passed cwd_len=75
T0 logon_wrapper_quoted   run1/2/3  rc=0 passed cwd_len=74
T4 child_without_runtime  run1/2/3  rc=0 passed cwd_len=75
T4 logon_wrapper_quoted   run1/2/3  rc=0 passed cwd_len=74
```

**唯一受控变量确为 cwd 长度**（166/167 vs 74/75），两棵树在**同一 basetemp 模式**下运行 —— 满足我上轮"两树须在同一 cwd 模式运行"的要求。

**(4b) "失败更多的那棵树在两轮间翻转"确有逐次捕获。** 我直接从 48 行结果重算（不读其汇总字段）：

```
n result rows = 48
交错顺序（前 8 行）：T0 pass1 run1 / T4 pass1 run1 / T0 pass1 run2 / T4 pass1 run2 ...
per (pass, tree):
  pass=1 tree=T0 failed=3/12
  pass=1 tree=T4 failed=2/12      -> pass1 worse = T0
  pass=2 tree=T0 failed=3/12
  pass=2 tree=T4 failed=4/12      -> pass2 worse = T4
  TOTAL T0 failed=6/24   T4 failed=6/24
FLIP = True
```

**翻转成立，且两轮合计 6/24 完全相同** —— 这正是"负载相关噪声"而非"树差异"的签名。

**(4c) 未能完全独立验证的一点**：`frequency-child_without_runtime.json` 的 48 行**只保存** `pass/tree/run/cwd/returncode/verdict/assertion/tail`，**不含每次运行的完整 stdout 文件**（其 `cwd` 指向 `%TEMP%\i14c-flake-freq\...`，该目录**仍在**、含 652 个文件，但不是本 attempt 内证据）。"每次失败都是同一条 `assert 3 == 2` on `child_started`"这一细节，我读的是 `review.md` 的陈述与 48 行的 `tail` 尾行，**未逐次打开原始输出核对**。深层/短路径那 12 次**是**完整捕获的，故关键的结构性结论（cwd 长度决定）**有完整证据**；频率层面的单次失败文本为**部分采信**。
（另：`frequency-logon_wrapper*.json` 不存在 —— 频率测量只对 `child_without_runtime` 做了，与"该节点才是 ~25% 抖动源"的结论自洽。）

### 5. guard 矩阵 ✅ **8/8 符合预期；"即使声明 scratch 根，生产路径仍 97"可复现**

存储证据 `r5/guard/matrix.json`：

```
n_cases = 8   all_as_expected = True
  declared-temp            real-driver              rc=3    expected=3        True
  attempt                  real-driver              rc=3    expected=3        True
  temp-undeclared          real-driver              rc=97   expected=97       True
  temp-plus-product        in-process-guard-probe   rc=0    expected allowed=false  True
  product-src-company-wiki in-process-guard-probe   rc=0    expected allowed=false  True
  product-source-catalog   in-process-guard-probe   rc=0    expected allowed=false  True
  product-revenue-forecast-outside-planning  in-process  allowed=false            True
  product-revenue-with-declared-root         in-process  allowed=false            True
```

**本人的独立反证（自带命令，不跑其脚本）**：

```
sys.path.insert(...harness); from run_guard import guard_run_dir
company-wiki src        -> BINDING-REFUSED (path is inside a product checkout) -> None
company-wiki\.source_catalog -> BINDING-REFUSED (path contains .source_catalog (a live catalog directory)) -> None
revenue-forecast\scripts -> BINDING-REFUSED (path is inside the revenue-forecast checkout but outside .planning) -> None
<my %TEMP% scratch>\ok\run -> <accepted>
```

并直接验证**驱动进程**层：run dir 在 `%TEMP%` 且**未声明** root → `returncode=97`、`run dir created: False`；声明我的 scratch root 后 → `returncode=3`（RE-RAISED）、目录被创建。**"声明 scratch 根也救不了生产路径"这一反证成立。**

### 6. 新增/改写 harness 脚本未越界 ✅

- **生产三仓零写入**：`company-wiki` porcelain 仅 ` M CLAUDE.md` / ` M README.md`（本卡之前就存在的用户改动）；`-- src tests scripts` 范围 porcelain **为空**；`filing-fetch` porcelain **为空**；`revenue-forecast` 的改动全部落在 `.planning/` 内。
- **生产模块仍等于 HEAD**（`git hash-object` 走过滤器）：`worker.py 5d700302…` = `HEAD:…`，`observability.py d9ce30df…` = HEAD，`cli.py c5038a9d…` = HEAD，`store.py 6ce3ff74…` = HEAD，`error_taxonomy.py e3bee2c7…` = HEAD。
- **`PLAN\reviews` 未被写**：`reviews` 目录 mtime = 2026/9/19 9:14:20（我第 4 轮记录为 10:05 的**父目录** `audit_report.md`/`delivery_validation.json` 亦未变），本轮与上轮观测一致。
- **`r5` 的 19 个子目录全部位于 attempt 内**（outside-attempt = 0）。
- **脚本静态审计**：r5 `harness\*.py` 中涉及生产路径的只有 `report_final_hashes.py` 的**只读** `CATALOG = Path(...catalog.sqlite3)`（仅 `stat()`），`run_guard_matrix.py` 的**只读**常量 `PRODUCT_ONE`/`TESTS`；两个驱动（`drive_real_exit.py:87`、`run_real_cli_exit.py:49`）均已改为调用 `guard_run_dir()`。

### 7. r4 的 6 项整改是否真的关闭 ✅ **逐条对号，全部关闭**

| r4 发现 | r5 整改 | 我的独立验证 |
|---|---|---|
| **R4-01** 计数错（23 vs 24，5 处） | `report_counts.py` 机械推导 + `counts.json` | ✅ 独立重算 44/30/28/82 全等；`exact_nodeids==fidelity_cases` 自校验存在且 rc=3 路径存在；套件内另有 pair-count 断言 |
| **R4-02** C13 后果低估一个数量级 | 4 处改写描述 + 3 条多行 fidelity 对 + 4 条表项 + 专门测试 | ✅ 我用自选 marker 复算 112→34；4 条多行用例已提取；`test_f08_c13_multiline_loss_is_frozen_not_hidden` 存在且按两种 marker 长度断言 |
| **R4-03** flake 声称无证据 | `run_flake_evidence.py` 逐次落盘 + `run_flake_frequency.py` 交错测量 | ✅ 12 次深/短路径捕获完整；48 行交错频率数据可重算翻转（6/24 各）；r4 的"3/3 passed"声称**已撤回** |
| **R4-04** 补丁不可 `git apply` | `make_posix_diff.py` 重新生成（POSIX 路径） | ✅ 我自建仓库 `--check`/`-p1` rc=0、三文件字节相同；无本地配置覆盖时同样成立 |
| **R4-05** 诊断表无 helper 兜底 | 与规则表对齐（`cannot_adjudicate` + rc=2） | ✅ T0 诊断表现返回 rc=2 / `verdict=cannot_adjudicate`，**无 traceback** |
| **R4-06** 退出码口径漂移（3 未被使用） | 两表改用 `0/2/3` | ✅ 实测 T1/T3 规则表 rc=3、T0 rc=2、T2/T4 rc=0；T1/T3 诊断表 rc=3 |
| **R4-07** hash 快照不全 | `attempt_porcelain` + `iso_venv` + `r4_reference` + 富条目（raw/LF/blob/`ls-files --eol`） | ✅ 见 §G：87 项检查全部通过（含 2 项为元数据键的伪失配，已排除） |

---

## 二、编号发现

### F-I14C-R5-01（P3，冻结件完整性：`oracle.md` r4 段被就地编辑，非纯追加）
**我上轮为 `oracle.md` 建立的性质是"逐字节追加"，本轮不成立。**

```
current oracle.md: bytes=18776 lines=315 sha=edbd0a93da9a197c
R5 addendum starts at line 282; bytes before it = 16465
r2 recorded prefix match:  None
r3 recorded prefix match:  None
r4 recorded prefix match:  None
longest prefix equal to r4 hash: None
```

r4 记录的长度为 16462 B，R5 之前的部分现为 16465 B —— **净增 3 字节，且三个历史 hash 全部不再是前缀**，证明 r4 段（或更早章节）被就地编辑过。

**逐行核对后的定性**：
- **章节结构未变**：`## 0.` … `## 5.`、`# R2 addendum`、`# R3 addendum`、`# R4 addendum`、`# R5 addendum` 全部在，行号与我第 4 轮读取时**逐条一致**（R3 addendum = 213，R4 addendum = 254，E4/N1/N2 在 95/99/103，`## 4.` = 106，`## 5.` = 114）。
- **r4 段的冻结语义未改**：第 265–272 行仍是"Fidelity is exact…The table scripts exit 2 on any mismatch"与"C13 … `a=1 token=<marker> b=2` … E4b acceptance length (193) is derived from it"，与我上轮读取**逐字相同**。
- **唯一的实质变化**：R4 段"exit 2 on any mismatch"这一句在 r5 已被 `# R5 addendum` 第 291–293 行的新约定（`0/2/3`）**显式取代**，且 R5 附录明确写了取代关系 —— 也就是说，被改的（若有）不是冻结结论本身，而是被**后置附录正确标注为 superseded** 的部分。
- **实现者未披露这 3 字节的差异**：`review.md` / `handoff.json` / `decision.md` / `oracle.md` 中检索 `append-only|3 bytes|rewrote` 均**无命中**。

**影响**：不改变任何判据或结论（冻结语义完好、R5 附录正确标注取代关系），但**上轮明确要求的"只许追加/不得改冻结件"边界被越过且未披露**。若下一轮继续沿用"前缀 hash 证明"作为冻结完整性的证明方式，这条通道将不再可用。
**最小修法**：仅在 `review.md` 的 r5 节追加一句事实说明（"`oracle.md` 的 r4 段在本轮被就地编辑，净增 3 字节，三个历史前缀 hash 不再匹配；冻结语义经逐行核对未变，R5 附录已标注取代关系；本轮未保留 r4 副本，故无法给出逐字节 delta"）。**只许追加，不得再改 oracle.md 既有字节。**

### F-I14C-R5-02（P4，`handoff.json` 对 short-basetemp 的表述与两份并存记录不一致）
`handoff.json` 写：`short basetemp -> T0 6/6 passed, T4 4/6 with assert 3 == 2 on child_started`。
但 `r5/flake-evidence/short-basetemp/` 内**并存两份互相矛盾的记录**：

```
short-basetemp\stdout.txt      (827 B, 无 cwd_len 字段)
  T0/child_without_runtime run1/2/3 rc=0 passed
  T0/logon_wrapper_quoted  run1/2/3 rc=0 passed
  T4/child_without_runtime run1 rc=1 failed / run2 rc=1 failed / run3 rc=0 passed   <-- T4 1/3 失败
  T4/logon_wrapper_quoted  run1/2/3 rc=0 passed

short-basetemp.stdout.txt      (另一次调用，带 cwd_len)
  T0 全部 rc=0 passed（cwd_len 75/74）
  T4 全部 rc=0 passed（cwd_len 75/74）

short-basetemp\summary.json + 12 个 per-run .txt 捕获
  T0 3/3 passed, T4 3/3 passed（与 review.md 表格一致）
```

即：**`handoff.json` 引述的是那个已被取代的 ad-hoc 观测**（且其"4/6"与文件里的"2 of 3"也不吻合），而 `summary.json` 与 12 份逐次捕获是**全绿**的另一次运行。
**缓解事实**：`review.md:71-118` 对这段历史**记录得完整且正确** —— 明确写了"an ad-hoc short-basetemp capture happened to show it on T4 in 2 of 3 runs and never on T0, which would have looked like a card-caused regression. It is not"，并给出两次频率预跑的 T0 6/12 vs T4 5/12 与 T0 0/12 vs T4 7/12、以及为何改为交错测量。**关键结论（抖动是负载相关、非树差异）表述无误且证据充分。**
**最小修法**：把 `handoff.json` 那一句改为指向 `review.md` 的叙述（或删去具体分数，改为"short basetemp 下该节点仍以 ~1/4 概率抖动，见 review.md"）。**只许追加/替换该字段值，不得改其他已冻结字段。**

### F-I14C-R5-03（P4，频率证据未落逐次原始输出）
`r5/flake-evidence/frequency-child_without_runtime.json` 的 48 行**只有** `pass/tree/run/cwd/returncode/verdict/assertion/tail`，没有像深/短路径那样为每次运行保存 stdout 文件；其 `cwd` 指向 `%TEMP%\i14c-flake-freq\`（该目录仍在，652 个文件）。因此"每次失败都是同一条 `assert 3 == 2`"**只能靠 `tail` 与 `review.md` 采信**，不能像深路径那样逐次复核。
**最小修法**：下一轮把 `--capture-per-run` 语义（深路径已有）也对频率测量打开，或把 `%TEMP%\i14c-flake-freq` 的 tail 汇总**复制进 attempt**（不删原目录）。

---

## 三、必做验证的命令与原始输出（索引）

| # | 项 | 命令要点 | 结果 |
|---|---|---|---|
| A | 十次表调用（5 树×2 表） | `python harness/run_rule_table.py --src iso/<tree>/src --label REVIEW-<tree> --out ...` | rc 2/3/0/3/0 与 2/3/0/3/0；T3 = 0 泄漏 + 27/13 保真失败 |
| B | 逐字符精确性 | scratch 注入 `<redacted>`→`<redacted>!`；注入移除 `;` 终止符 | rc=3 / 32 与 15 条失败；rc=3 / 2 条失败 |
| C | 计数重算 | 导入三表 + 独立 `pytest --collect-only` | 44/30/28/82 全部相等；自校验 `return 3` 存在 |
| D | 退出码口径 | 受控于 `negative = (not fidelity_ok) or leaks or touched/new_over` | 与 `run_card.py` 的 `0/2/3` 一致，r4 漂移已修 |
| E | 套件复跑 | `pytest ... --basetemp=<review scratch>` ×3 | **82 passed** in 22.1s / 21.4s / 22.0s（其一 `I14C_RUN_ROOT` 完全未设） |
| F | 方向性（未新增过redaction） | 见 §A 表与残留集合 | 残留集合仍为 `digest=` / `--api-key` / JSON 引号键 / 裸 marker |
| G | 全量 hash | 重算 `final_hashes.json` 全部条目 + 生产 blob vs HEAD | **87 项检查，0 处真实失配** |
| H | 生产不可变 | `git hash-object` vs `HEAD:`、porcelain、`src/tests/scripts` 范围 | 三仓零写入；5 个模块 blob = HEAD |
| I | iso-only | r5 全部子目录归属 | 19/19 在 attempt 内 |
| J | oracle/review 追加性 | 前缀 hash 搜索（r2/r3/r4） | **均不再匹配 → `oracle.md` 被就地编辑（发现 1）** |
| K | 诚实性 | `handoff.json.status` / `blocked_by` / carry 可见性 | `review_pending`、`blocked_by=[]`、19 条 open_questions、C1–C13 全部在册 |

### G 项明细（hash）

```
### r5_documents        OK binding.json / oracle.md / commands.json / decision.md / review.md / handoff.json
                        OK changes.diff / r2-changes.diff / r3-changes.diff / r4-changes.diff / r5-changes.diff
### r5_harness          OK 23 个脚本全部相符（含 run_rule_table.py 10b406d7…、run_guard.py 05ee904c…、
                        run_r5_commands.py 1223fd13…、tests/test_i14c_real_exit_redaction.py 672b88de…）
### iso_trees           OK 6 树 × 8 模块 = 48 项全部相符
                        （product_fixed/observability.py c5608c4b…；product_r3/observability.py 28b1dd56…）
### production_modules  OK 8 模块 raw_sha256 全部相符（worker e8317991… / observability a73826aa… / cli fad88c60…）
### T4 LF 形式          OK product_fixed/observability.py lf=049f5d5b… == r4 pin（内容未变，仅行尾归一）
### production blobs    OK worker 5d700302… / observability d9ce30df… / cli c5038a9d… / store 6ce3ff74… /
                        error_taxonomy e3bee2c7… 全部 == HEAD
### production_catalog  OK size=49677344768 wal=0 shm=32768
### worker_control      OK 9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd
HASH_CHECKS total=87 mismatches=2   <- 这 2 项是 production_modules 下的 core_autocrlf / note 元数据键，
                                       被我的通用遍历误当 hash（我的脚本问题），排除后 0 处失配
```

**r5 的 hash 账本是本卡至今最完整的一次**：每条生产模块同时给出 `raw_sha256`、`lf_normalised_sha256`、`git_blob_hash_HEAD`、`git_hash_object_filtered`、`git_hash_object_no_filters`、`git_ls_files_eol`、`worktree_matches_HEAD_blob_after_filters`。我逐项复算，并独立确认 **CR/LF 计数与声明相符**：

```
worker.py        48075 B  crlf=1084 lone_lf=0   raw=e8317991…
observability.py 30087 B  crlf= 625 lone_lf=0   raw=a73826aa…
cli.py           65694 B  crlf=1568 lone_lf=0   raw=fad88c60…
iso/product 三模块与生产 **字节相同**（byte-identical: True）
```

r4 遗留的"CRLF sha256 vs HEAD blob"口径矛盾**确已解决**，且解释正确（`core.autocrlf=true` ⇒ 工作树 CRLF / blob LF；`hash-object`（带过滤器）等于 HEAD blob，`--no-filters` 不等于）。

### 行尾归一化：一处诚实的、可核验的变更
`iso/product_fixed/observability.py` 的 CRLF 形式由 r4 的 `6b6ce5…`（40060 B，LF 形 `049f5d5b…`）变为 r5 的 `c5608c4b…`（40060 B，LF 形仍为 `049f5d5b…`）。**内容未变，只有行尾由混合变为统一 CRLF。** 依据：

```
product_fixed observability.py 40060 B  crlf=864 lone_lf=0
T4 LF-normalised = 049f5d5b27fd37bc18770b903015184c11d60022f6d0dee37e0d786c52ad22cf  == r4 pin  ✓
r5-changes.diff 施加后三文件与 T4 字节相同（§J）
```

实现者在 `handoff.json` 的 `F-I14C-R4-04` 条目中**主动披露**了这一点及其动机（"iso/product_fixed observability.py was LF while T0 is CRLF, which had made the patch a whole-file rewrite; after normalisation it is 1 hunk and the suite is still 82 passed"）。**这是正确做法**，且我确认归一化后判据未松（T3 仍 27/13 保真失败，T4 仍 0/0）。

---

## 四、本人**未能验证**的部分（明确列出）

1. **频率测量 48 次运行的逐次原始输出 —— 未验证。** 只保存 `tail`（发现 3）。结构性结论（cwd 长度、翻转、6/24）我已从 48 行数据独立重算确认；"每次失败都是同一条断言"为部分采信。
2. **`oracle.md` 的具体逐字节 delta —— 无法取得。** 三个历史版本均无副本（attempt 内无备份；git 中该文件已被提交为 r5 版本，`HEAD` blob = 当前 worktree = `94b4e8fe…`），故只能给"净增 3 字节 + 前缀不再匹配 + 行号/语义逐条比对通过"这一层结论，**无法列出被改的具体字节**。
3. **短 basetemp 那次 ad-hoc 观测的原始输出 —— 未留存/未能核对。** `handoff.json` 引述 T4 4/6，现存 `short-basetemp\stdout.txt` 显示 T4 1/3 失败，`summary.json` 显示全绿；三者无法互相推出，我无法判定 `handoff.json` 的数字具体来自哪一次运行。
4. **`compat` 的 5 次运行中的"更早一轮"（3,4,4,5,5）—— 未验证**（`review.md` 明示"not the recorded one"，其原始输出不在 r5 证据内）。
5. **`iso_venv` 的 dist-info RECORD hash 与 `python.exe` sha256 —— 未逐一复算**（`r5/final_hashes.json` 已记录；我只确认解释器版本 3.13.9 与 `sys.prefix` 指向 attempt 级 venv，并读到 `iso-venv-pip-list.txt` 的 pytest 9.1.1 / PyYAML 6.0.3 / requests 2.34.2）。
6. **`2f5c5740…/65553` 的来源 —— 仍未追溯**（r1 遗留"来源不可考"；不影响 r5 任何结论）。
7. **bench 其他 9 种形状的秒数 —— 未重算**（我第 4 轮只重算 `underscore-segments`；本轮未重跑 bench，`bench_redact.py` 哈希未变）。
8. **产品 `revenue-forecast` 工作树在 `04:35:31–04:40:53` 被重置并恢复这一事件 —— 未独立复核。** 我按你给的环境事实记录，并据此限定：**本报告 §H 的全部"生产零写入"结论，观测时点为本复核窗口（2026-09-20 03:48Z 起）**；`company-wiki` 三仓在该窗口内确为零写入。该事件的影响范围我只做了"当前状态核对"（8 个受影响文件我未逐条复算，仅核对本卡相关模块）。
9. **`sync_commands_json.py` 的"29 条旧条目保留 + 16 条 r5 条目追加"—— 未逐条 diff**（我确认了 `r5/commands.json.before-r5-append` 存在、`commands-r5-rc.json` 内 29 条 r5 调用 `all_as_expected=true`）。

---

## 五、对三个明确问题的回答

### 1. 判定
**`accepted_scoped`** —— 范围与第 4 轮口径一致：**证据与判据成立**；**不含产品化授权**。C12 仍为促销硬前置（实现者亦自述如此）。

### 2. 若拒，最小修法（**本判定非拒**，但以下 3 项建议在下一轮顺带清理；均**只许追加/不得改冻结件**）
- **发现 1（建议优先）**：在 `review.md` r5 节**追加**一句，披露 `oracle.md` r4 段被就地编辑、净增 3 字节、历史前缀 hash 失效、冻结语义经核对未变、且无逐字节 delta 可给。**不得再改 `oracle.md` 既有字节。**
- **发现 2**：把 `handoff.json` 中 `short basetemp -> T0 6/6 passed, T4 4/6 …` 一句**替换为指向 `review.md` 的叙述**（或删去具体分数）。仅动该字段值。
- **发现 3**：下一轮为频率测量打开逐次 stdout 捕获（深路径已有该能力），或把 `%TEMP%\i14c-flake-freq` 的 tail 汇总复制进 attempt（**不删原目录**）。

### 3. 四个待 owner 裁定的开放问题 —— **均不阻塞我的判定**
- **C13 是否单独立卡**：不阻塞。C13 已按我上轮要求"保留现状 + 显式冻结 + 描述更正"完成；是否需要一张卡把它改成单 token 语义，是**范围与风险偏好**问题（会移动 E4b 的 193 基线与 envelope 宽度），属 owner 决策，我**不代为裁定**。
- **~25% 抖动是否另立卡修产品测试时序假设**：不阻塞本卡。抖动已定量（T0 6/24、T4 6/24、翻转、两轮翻转），且已证明**非本卡所致**（唯一 diff 的两处 `worker.py` 改动不在该节点路径上；我复核了 `r5-changes.diff` 的 worker.py 3 个 hunk：import 行 + `_write_unhandled_exception_event`）。是否修产品测试时序，属 owner 决策。
- **深层 cwd 的 WinError 206 是否在产品侧改为短路径 basetemp 约定**：不阻塞本卡。这是**环境/测试约定**问题（166/167 字符即触 Windows 路径上限），本卡已把它测成"两树同因失败"。属 owner 决策。
- **C12 的具体形式（`pytest-timeout` 依赖新增 vs 子进程包裹）**：不阻塞本判定，但**阻塞促销**。我上轮与本轮均实测该用例在阻塞实现下**挂死**（>90 s）；本卡不授权改产品测试，故必须由下一轮产品侧实现落地其一。属 owner 决策（但任一形式都必须实测"阻塞 ⇒ FAIL"）。

---

## 六、给下一轮的最小行动清单
1. **P3-必做（文档诚实性）**：发现 1 —— 在 `review.md` 追加 `oracle.md` 编辑事实的披露（只追加）。
2. **P4**：发现 2 —— 修正 `handoff.json` 对 short-basetemp 的表述。
3. **P4**：发现 3 —— 频率证据补逐次捕获。
4. **C12（促销硬前置）**：产品侧 `pytest-timeout` 或子进程硬超时包裹 + "阻塞 ⇒ FAIL"实测。
5. 保持 `handoff.json` 对 stderr 要求的限定表述（"fully met only for credential-shaped markers on exits reachable through `main()`'s handler; C6/C7 are the named residuals"）**不得放宽**。

---

## 附：本轮可复算脚本（均在 `%TEMP%\i14c-r5-review-20260920-044801\`）
`inv.py`（树清单）· `g_hashes.py`（全量 hash 重算）· `ja_gitapply.py` / `gitapply2.py`（`git apply` 复现，含无本地配置覆盖）·
`fidelity_exact.py`（1 字符 / 单条目注入）· `counts.py`（计数重算 + 多行用例提取）·
`eol.py`（行尾组成分析）· `prodcheck.py`（生产 vs iso 字节比对）· `appendonly.py` / `oracle_diff.py`（追加性）·
`guard2.py`（guard 反证 + 驱动层 97）· `probe.py`（用自选 marker 的独立探针）。
原始输出：`RT_*.json` / `RT_*.stdout.txt`（十次表调用）、`mut-one-char-*.json`、`mut-one-entry-*.json`、`gitapply_result.json`、`pytest-*/`（三次套件复跑）。
---

## 转录与三项发现处置（implementer 追加，2026-09-20；本节之前的所有字节未被改动）

### 0. 转录证明（只追加）

| 项 | 值 |
|---|---|
| `review.md` 追加前 sha256 | `337a91f55ecf70f9d3772b8a812a6a7dc4bbdb43a925d23c499143a273edd32f` |
| `review.md` 追加前字节数 | `55673`（末字节 LF，全文纯 LF：CR=0、LF=822） |
| reviewer 原文（`REPORT.md`）字节数 / sha256 | `34121` / `8e2523947da8c3e7e86aa5e5834ef893b71634879ba1404f217695d251569051` |
| 转录方式 | 二进制追加：`# r5 — INDEPENDENT REVIEW (round 5)` 标题 + reviewer 原文逐字节，一字未改，未做行尾转换（原文亦为纯 LF） |
| 追加后 `review.md` sha256 / 字节数 | 见 `evidence/I-14-C/verdict_transcription_r5.json`（追加后写入，避免自引用） |
| 前缀校验 | 追加后文件前 `55673` 字节的 sha256 == `337a91f5…`，即既有字节逐字节未变 |

### 1. F-I14C-R5-01（`oracle.md` 就地编辑）—— 按 reviewer 要求披露

`oracle.md` 在 r5 的编辑**不是纯追加**：R5 附录之前的净增 **3 字节**（16462 → 16465），
r2/r3/r4 三次记录的前缀 hash **均已不再匹配**；经 reviewer 逐行核对，章节结构与行号未变、
r4 段的冻结语义（含 C13 条目与 E4b-193 的推导）逐字完好，且 R5 附录已明确标注新的 `0/2/3`
口径**取代** r4 段的 `exit 2 on any mismatch`。本轮**未保留 r4 副本**，因此**无法给出逐字节
delta**。自本节起，`oracle.md` 的既有字节冻结，不再修改；“前缀 hash”这一证明通道对本文件
不再可用，后续以显式 supersede 标注取代。

### 2. F-I14C-R5-02（`handoff.json` 的 short-basetemp 分数）—— 已删除分数、改为指向本文件

`handoff.json` 的 `r5_disposition.F-I14C-R4-03_flake_claims` 与 `open_questions` 中原引述的
“T0 6/6 passed, T4 4/6”已删除：该数字来自**已被取代的 ad-hoc 观测**，且与存留文件
（`r5/flake-evidence/short-basetemp/stdout.txt` 显示 T4 3 次中 1 次失败）互相矛盾。字段现改为
“short basetemp 下该节点仍以约 1/4 概率在两棵树上抖动，见 `review.md` 的 F-I14C-R4-03 叙述”。
`short-basetemp/` 下并存的两份记录未被删除，作为该轮历史的证据保留。

### 3. F-I14C-R5-03（频率测量缺逐次原始输出）—— 已补齐，并就地更正一句话

48 次运行的**完整 stdout** 已从原 scratch 根 `%TEMP%\i14c-flake-freq`（**原样保留、未删**）
复制进 `r5/flake-evidence/frequency-captures/`（48/48，逐份 sha256 校验通过、
`all_copies_verified=true`；见 `frequency-child_without_runtime.json` 新增的 `captures` 块及
`harness/copy_frequency_captures.py`）。**48 行既有数据一字未改**（reviewer 是据此重算的），
`harness/run_flake_frequency.py` 现已自带逐次捕获，后续运行无需补录。

**就地更正（本次逐份核对后才发现）**：此前“每次失败都是同一条 `assert 3 == 2`”的说法**不准确**。
48 份原始输出显示失败共 12 次，断言**表达式相同**（`len([e for e in events if e["status"] ==
"child_started"]) == 2`），但**观测值有两种**：`assert 3 == 2` **10 次**、`assert 4 == 2`
**2 次**（均在 pass2/T4：run1、run5）。因此正确表述是：**同一断言、同一失败机制（监督进程
多重启 1–2 次），观测计数为 3 或 4**；这**不改变**结构性结论（负载相关抖动、两树同因、
翻转成立：p1-T0 3 vs p1-T4 2、p2-T0 3 vs p2-T4 4、合计 6/24 对 6/24），但 reviewer 标注为
“部分采信”的那一条细节，现以更正后的口径**完全可核验**。reviewer 原文与本更正并存，不改前者。

### 4. 载体（非自签；照抄 reviewer 口径）

- `handoff.json.status` = `accepted_scoped`；`evidence/I-14-C/qualification.json` 的
  `formula.state` = `accepted_scoped`。
- 范围：**r5 时点的“证据与判据”成立**（F-I14C-08 关闭依据 + r4 六项整改 + 机械计数 +
  可复跑性）；**不是产品化授权**：`not_an_authorisation_to_promote = true`。
- 硬前置与未做项原样保留：**C12 仍是促销硬前置**（F-07 用例在 redactor 阻塞时挂起 >90 s，
  必须由产品侧 `pytest-timeout` 或子进程硬超时落地，并交付“阻塞 ⇒ FAILS”实测），
  **验收测试仍未提升**（C9）。
- `implementer_signed: false`、`implementer_never_signs_acceptance: true`、
  `authority: "acceptance was written by an independent reviewer, not by the implementer"`；
  `disclosure_adaptation` / `accuracy` **未动**。
- 四个待 owner 项（C13 是否立卡 / ~25% 抖动是否立卡 / 深路径 `WinError 206` 是否改为短
  basetemp 约定 / C12 的具体形式）已**原样承接**进 `handoff.json.open_questions`，
  实现者**未自决**。

### 5. 封盘

本文件在该节写入后不再修改；`oracle.md` 既有字节冻结；生产三仓零写入；未执行任何 git 写命令；
`PLAN\reviews` 未写。