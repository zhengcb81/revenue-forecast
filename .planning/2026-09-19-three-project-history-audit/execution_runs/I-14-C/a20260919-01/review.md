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
| pass 1 (12 runs each, interleaved) | 1/12 failed | 2/12 failed |
| pass 2 (12 runs each, interleaved) | 5/12 failed | 3/12 failed |
| pooled (24 runs each) | **6/24 failed** | **5/24 failed** |

Every failure is the same `assert 3 == 2` on `child_started`, and **the tree with more failures
flips between passes** (and flipped the other way in the preceding pass: T0 2/12 vs T4 4/12) —
which is exactly what a noise-dominated ~25 % flake looks like. So the node is timing-flaky in
the product's own test at roughly that rate on both trees, and the card cannot have caused it:
the only `worker.py` hunks in this diff are the `observability` import line and
`_write_unhandled_exception_event` (see `r5-changes.diff`), neither of which is on that node's
path. Evidence: `r5/flake-evidence/summary.json` and
`r5/flake-evidence/frequency-child_without_runtime.json`.

### The compat suite does not fail with a stable set — so the criterion is the union plus T0 evidence

r4's compat control claimed "both trees: 4 failed / 27 passed with the IDENTICAL failure set".
r5 ran the same suite five times (twice on T0, twice on T4, plus the plain delivered run). In the
final recorded pass every one of the five runs failed exactly 4 of 31, and the four stable node
ids were the same on both trees:

| run | failing node ids |
|---|---|
| T0-1, T0-2, T4-1, T4-2 (4 each) | `read_desired_state…`, `stderr_exit_zero…`, `stale_child_heartbeat…`, `logon_wrapper…quoted_paths` |
| T4 plain (4) | the same four |
| an earlier pass (not the recorded one) | counts 3, 4, 4, 5, 5 — the extra/missing node was always `child_without_runtime…` |

So in this pass the T0 and T4 unions *are* equal; but an earlier pass produced a T4-only node
(`test_child_without_runtime_session_is_terminated_and_restarted`) purely because the flaky nodes
drop in and out. Two runs per tree are far too few samples for a ~25 % flake, so
`harness/analyze_compat_control.py` (`r5/compat-control-analysis.json`) checks every T4-only node
against the dedicated interleaved T0 evidence instead of trusting the union: that node fails on
the **pristine T0 tree in 6 of 24 runs** with the identical `assert 3 == 2` on `child_started`.
Recorded verdict: *"no card-specific compat failure: every T4 failure also occurs on T0"*,
`unproven_t4_only_nodes` empty, rc 0.

Three notes for the reviewer: (1) the per-run count `4 failed / 27 passed` should not be quoted
as a fixed expectation — the flake band observed at r5 is 3–5 failures; (2) two of the varying
nodes are restart-timing nodes and one of the stable four is the path-length node above, i.e. the
same environment classes; (3) no compat failure has a fixed-tree-only signature in any pass.

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
| #7 controlled cwd scan | partially addressed: the flake evidence captures the deep-vs-short basetemp comparison on both trees |
| #8 venv contents unverified | **fixed**: venv evidence added to `r5/final_hashes.json` |
| #9 no product-side timeout wrapper exists | unchanged by design; C12 remains a hard precondition (C9: the test is not promoted) |

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
| product contract tests on `iso/product_fixed/src` | 28 passed / 3 failed — the same 3 pre-existing failures |

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
