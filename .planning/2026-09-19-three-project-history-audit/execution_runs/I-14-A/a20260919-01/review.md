# I-14-A review.md

> ## PENDING independent review
> Written by the **implementer**. Nothing here is an acceptance. No card status is signed by this
> file. The independent reviewer must re-derive at least one oracle value, re-run the counterexamples
> against both tools, and decide D1 (and confirm D2/D3).
>
> **Card pass would only prove the meter.** It would not qualify the production SLO — that needs
> I-16's real measurement and I-14-B's natural-time observation (oracle.md M9).

## What this attempt delivers

- `oracle.md` — frozen before any run: measurement rules M1–M9, four fixtures F1–F4, counterexamples
  E1a–E7b, an exit-code contract, and an errata section recording two expectation corrections that
  were made **before** the run that produced them.
- `iso/slo_probe_patched.py` — the isolated fix (`changes.diff`, 1 file, product tree untouched).
- `harness/` — the case runner + verifier (`run_probe_cases.py`), the bundle control
  (`run_bundle_control.py`), the fixture spec and the pytest suite.
- `before/` — the RED baseline: the unmodified tool on the same fixtures, plus the audit-row
  reproduction with its raw return codes.
- `after/` — every case's report, verdict, raw return code, stdout and stderr; the summary and the
  final integrity snapshot.

## The audit row, reproduced as a falsifiable fact (not prose)

`PLAN/audit_report.md:60` says the probe ignores the child return code and samples RSS after the child
exited. Both were reproduced:

| what | how it was shown | file |
|---|---|---|
| rc ignored | the unmodified tool, against a stand-in resolver root, spawned resolve children that **all failed**; it still exited **0** with `breaches: []`, exact p95 ≈ 0.047 s, latest p95 ≈ 0.054 s | `before/cmd-E5/report.json` |
| the failure mode is not hypothetical | the probe's resolve argv omits `--as-of-date`, which `cli.py:411` requires, so the child exits 2 through argparse; in this isolated root it fails earlier still (the venv has no `company_wiki`), so `stderr` is non-empty and unread | `before/cmd-E5/report.json`, `binding.json:ground_truth_facts_the_oracle_used` |
| bundle carried no information | `bundle_proxy` percentiles are **numerically identical** to `exact` in the baseline report — the literal alias `bundle = exact[:]` | `before/cmd-E5/report.json` |
| RSS was the probe's own | baseline `peak_rss_gb 0.022`, `peak_rss_source` absent (field does not exist in the old report) while the resolve children were already reaped | `before/cmd-E5/report.json` |
| the same suite is red on the old tool | 10 failed / 2 passed / 1 skipped | `before/cmd-SUITE/stdout.txt` |

## Frozen rules → measured result

| rule | counterexample | patched raw rc | measured |
|---|---|---|---|
| M5 / E1a: a non-zero rc is never a success sample | F1 prints a success-shaped envelope then exits 7 | **4** | `calls.failed = 6`, `failed_kinds = {subprocess_rc: 6}`, `raw_returncode = 7`, `exact.succeeded_count = 0` |
| M5 / E1b: rc 0 with a failed business status is a failure | F2 prints `{"status":"failed"}` and exits 0 | **4** | `calls.failed = 6`, `failed_kinds = {business_status: 6}`, `raw_returncode = 0` |
| M3 / E1c: RSS sampled while the child is alive, keyed to it | F3 allocates 256 MB and holds it 1.6 s | **2** | `peak_rss_gb 0.267`, `peak_rss_source live_sample`, `rss_sample_count_min 22`, `peak_tree_pids [popen_pid, fixture_pid]`, `rss_sample_window_seconds 1.69` |
| M6 / E2: no sample is `null`, never 0.0, never green | same F3 with `--rss-sampler none` | **2** | `peak_rss_gb null`, `peak_rss_source sampler_disabled`, breach `peak RSS not measured (sampler_disabled) — an unmeasured RSS can never be reported as within budget` |
| M1/M2/M4: three windows reported separately | any case | — | `windows.command_total_seconds`, `windows.slo_window_seconds`, `windows.rss_sample_window_seconds_max`, `windows.quick_check_seconds`, plus `quick_check_included_in_slo_window: false` and its own `raw_returncode`/`result: ok` |
| clause 6a / E4: catalog/config mismatch refused | config names another catalog dir | **3** | `error catalog_config_mismatch`, `measured false`, **0** resolve calls spawned |
| clause 6a / E4b: consistent binding accepted | unquoted config pointing at the fixture catalog | **2** | 6 resolve calls ran |
| clause 6b / E7: bundle not granted by copied exact | no `--bundle-measurement` | **2** | `bundle.measured false`, `basis unmeasured`, breach `bundle: basis=unmeasured — bundle SLO is NOT qualified` |
| clause 4 / M8: budgets untouched | — | — | `budgets == {"exact_p95":5.0,"latest_p95":5.0,"bundle_p95":5.0,"peak_rss_gb":2.0}` in every case; `E6` recomputes the percentile rule independently |

## Suite

- patched tool: **12 passed, 1 skipped**, rc 0 (`after/cmd-SUITE/stdout.txt`)
- unmodified tool, same suite: **10 failed, 2 passed, 1 skipped**, rc 1 (`before/cmd-SUITE/stdout.txt`)
- the whole sweep repeated three more times: rc 0 each (`harness/scratch/repeat1..3.json`)

## Independent-oracle discipline

- Expectations live in `harness/fixture_spec.py` and were written from the card text and a source read
  **before** any run. `run_probe_cases.py` verifies a report produced by a **subprocess**; it never
  imports the meter, so the meter cannot satisfy its own check.
- `E6` compares `BUDGETS` to a literal and recomputes the percentile rule with a separate one-liner
  process — no expected value is produced by the function under test.
- The fixtures are ordinary child processes; nothing mocks `subprocess`, so the rc/business/RSS paths
  under test are the real ones.
- Two expectations were corrected **before** the run that produced them and the correction is recorded
  in `oracle.md` §6 with the measurement that forced it (`popen.pid != child pid`; F4's first-sample
  behaviour). No expectation was weakened: the pid rule became stricter, the sample-count floor rose
  from 1 to 10.

## Scope / safety statement

- Product code changed: **none**. `git status --porcelain -- tools` is empty and
  `git hash-object tools/slo_probe.py` equals `git rev-parse HEAD:tools/slo_probe.py`
  (`after/snapshot.json`).
- Production catalog: **never opened** by this card; only its `(bytes, mtime, -wal/-shm)` identity was
  recorded (`after/snapshot.json:production_catalog_identity`, `opened_by_this_card: false`).
- Worker/scheduler: never started, stopped or signalled. Network: no card command used it.
- No `git add/commit/restore/stash` in any product repo.

## Open gaps / not verified

1. **D1 is unsigned.** The ops reviewer must accept or replace the RSS method, the 50 ms interval and
   the error rule.
2. **D2's parser is small by design.** It fails closed, but a reviewer may prefer importing the
   product's own loader — that would put a product import inside the meter, which is why it was not
   done here.
3. **No real bundle latency was measured.** The structural fix and the unmeasured-bundle breach are
   proven; a genuine bundle-consumption number is production measurement (I-16).
4. **The meter was never pointed at the production catalog.** p95/RSS numbers in this attempt are
   fixture numbers; they say nothing about production performance, and no production SLO claim is made.
5. **The patched tool is not installed.** Promoting it into `RF/tools/` (and its test into
   `RF/tools/tests/`) is a separate, reviewer-approved change; the existing test file's three
   assertions were not modified.
6. **`quick_check` is measured on a tiny fixture catalog.** Its window is correctly separated, but the
   minutes-scale production behaviour is only documented (`RF/tools/release_readiness.py:61-65`), not
   exercised — deliberately, since that would be a production load.
7. **The probe still cannot report a business status for a resolver that prints no JSON.** `_business_status`
   requires a first-line envelope with an explicit `status`; a real resolver that prints plain text
   would be recorded as `business_unparseable`. This is a deliberate fail-closed choice and needs the
   reviewer to confirm it matches the real CLI's stdout contract.

---

## r2 — disposition of the independent review's findings (APPEND-ONLY)

The independent review returned **accepted_scoped for the isolated measurement fix itself**, with
**promotion blocked until D1 is signed**. It independently re-ran `--all` (per-case raw rc identical:
E1a/E1b = 4; E1c/E2/E3/E7 = 2; binding mismatch 3; binding consistent 2; percentile 0), the pytest
suite (patched 12P/1S; unmodified 10F/2P/1S), regenerated `changes.diff` (identical), and confirmed
`hash-object tools/slo_probe.py == HEAD:tools/slo_probe.py`. Five corrections were raised; the
implementer changed **no** implementation code (the tool stays byte-identical to the version the
reviewer verified) and did not push back on any of them.

| # | sev | the finding | file:line | disposition |
|---|---|---|---|---|
| F-I14A-01 | medium | the default invocation is never green, because an unmeasured bundle always breaches | `iso/slo_probe_patched.py:628` (breach text `:629`), replacing `iso/tool_prod/slo_probe.py:112` (`bundle = exact[:]`) | **ACCEPTED, written into the signature checklist.** Recorded in `decision.md` D1 (term 3) and D3, in `handoff.json.blocked_by` / `next_action`, and in `after/r2_review_evidence.md`. The signer must explicitly accept that every default run exits 2 until a real bundle measurement exists; otherwise the I-16 gate alarms forever or is misread as a broken probe. |
| F-I14A-02 | low-med | the E5 baseline does not prove "every resolve child failed"; the stderr is a parent-side `UnicodeDecodeError` | `iso/tool_prod/slo_probe.py:57` (`subprocess.run(..., capture_output=True, text=True, ...)`, result discarded; `returncode` appears nowhere in `_resolve`); evidence `before/cmd-E5b/stderr.txt` (`subprocess.py:1615 in _readerthread`, 6 occurrences) | **ACCEPTED, conclusion downgraded** to "rc unobservable / unobserved". The `UnicodeDecodeError` is registered as **new, strengthening** evidence: the channel that would carry the child's failure cannot even decode this host's GBK stderr, the exception dies in the reader thread, and the probe still exits 0 with `breaches: []`. The "`--as-of-date` is required" fact (`CW/src/company_wiki/source_catalog/cli.py:411`) stays as the reviewer independently confirmed it. |
| F-I14A-03 | low | the peak is a tree sum and therefore a fixed overestimate | the sampler's `measured`/`total` accumulation in `iso/slo_probe_patched.py`; the peak block in `stop()` | **ACCEPTED.** Added to `oracle.md` §9.4 as amendments to M3/M7: ≈11 MB launcher overhead measured (0.267 GB summed tree vs 256 MB declared), `peak_pid` null on 6/6 E1c calls, `peak_tree_pids` carries the full pid set. |
| F-I14A-04 | low | oracle §4 said `calls.failed == 1`; the harness runs 6 calls | `harness/fixture_spec.py` case expectations; `harness/run_probe_cases.py` (`--samples 3`) | **ACCEPTED.** Corrected in `oracle.md` §9.2. Only the oracle's arithmetic was wrong — the measured values were already 6/6 and no expectation was relaxed. |
| F-I14A-05 | low | the `catalog_dir` parser's boundaries were undocumented | `config_catalog_dir()` / `check_catalog_binding()` in `iso/slo_probe_patched.py` | **ACCEPTED.** `oracle.md` §9.3 and `decision.md` D2 now list exactly what it parses and what it refuses (no block scalars, inline maps, anchors or escapes; residual `${` ⇒ `ValueError` ⇒ exit 3, fail-closed). |

### Ownership recorded (not self-assigned)

| decision | owner | state |
|---|---|---|
| D1 | ops reviewer — **not the author of this probe** | UNSIGNED ⇒ **promotion is forbidden** |
| D2 | production SLO / probe owner | awaiting confirmation |
| D3 | I-16 | awaiting decision |

`iso/slo_probe_patched.py` remains sha256
`14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e` — unchanged by this pass, so the
reviewer's re-runs stay valid. New evidence from this pass:
`before/cmd-E5b/{report.json,stderr.txt,stdout.json}` and `after/r2_review_evidence.md`. No card
command's expected return code changed.

## reviewer: attack first

1. Re-derive one frozen case by hand from `after/<case>/report.json`: recompute `exact.p95` from the
   `per_call` latencies (rule: `sorted[int(n*0.95)]`, floor) and check it equals the reported p95.
2. Confirm F1 and F2 fail **independently**: make F1's rc 0 and show E1a's verdict is still red for the
   business reason, then the reverse. A single mechanism that covers both would be a weaker fix.
3. Confirm the RSS sample really lies inside the child's life: compare `peak_sample_age_seconds`,
   `rss_sample_window_seconds` and `child_exit_monotonic`, and confirm the fixture's own `os.getpid()`
   appears in `rss_sampled_pids` (the sampler must be reading the script process, not just the launcher).
4. Try to make the no-sample branch read as green: run `--rss-sampler none` and check that the verdict is
   non-zero **because** of the RSS dimension, not incidentally for another reason.
5. Check that no budget moved: diff `iso/tool_prod/slo_probe.py` against `iso/slo_probe_patched.py` and
   confirm the `BUDGETS` block is byte-identical.
6. Decide D1, and confirm or reject D2/D3.

---

## r2 — disposition of the independent review's findings (APPEND-ONLY)

The independent review returned **accepted_scoped for the isolated measurement fix itself**, with
**promotion blocked until D1 is signed**. It independently re-ran `--all` (per-case raw rc identical:
E1a/E1b = 4; E1c/E2/E3/E7 = 2; binding mismatch 3; binding consistent 2; percentile 0), the pytest suite
(patched 12P/1S; unmodified 10F/2P/1S), regenerated `changes.diff` (identical), and confirmed
`hash-object tools/slo_probe.py == HEAD:tools/slo_probe.py`. Five corrections were raised; the
implementer changed **no** implementation code and did not push back on any of them.

| # | sev | the finding | file:line | disposition |
|---|---|---|---|---|
| F-I14A-01 | medium | the default invocation is never green, because an unmeasured bundle always breaches | `iso/slo_probe_patched.py:628` (breach text `:629`), replacing `iso/tool_prod/slo_probe.py:112` (`bundle = exact[:]`) | **ACCEPTED, written into the signature checklist.** Recorded in `decision.md` D1 (term 3) and D3, in `handoff.json.blocked_by` / `next_action`, and in `after/r2_review_evidence.md`. The signer must explicitly accept that every default run exits 2 until a real bundle measurement exists; otherwise the I-16 gate alarms forever or is misread as a broken probe. |
| F-I14A-02 | low-med | the E5 baseline does not prove "every resolve child failed"; the stderr is a parent-side `UnicodeDecodeError` | `iso/tool_prod/slo_probe.py:57` (`subprocess.run(..., capture_output=True, text=True, ...)`, result discarded; `returncode` appears nowhere in `_resolve`); evidence `before/cmd-E5b/stderr.txt` (`subprocess.py:1615 in _readerthread`, 6 occurrences) | **ACCEPTED, conclusion downgraded** to "rc unobservable / unobserved". The `UnicodeDecodeError` is registered as **new, strengthening** evidence: the channel that would carry the child's failure cannot even decode this host's GBK stderr, the exception dies in the reader thread, and the probe still exits 0 with `breaches: []`. The "`--as-of-date` is required" fact (`CW/src/company_wiki/source_catalog/cli.py:411`) stays as the reviewer independently confirmed it. |
| F-I14A-03 | low | the peak is a tree sum and therefore a fixed overestimate | the sampler's `measured`/`total` accumulation in `iso/slo_probe_patched.py`; the peak block in `stop()` | **ACCEPTED.** Added to `oracle.md` §9.4 as amendments to M3/M7: ≈11 MB launcher overhead measured (0.267 GB summed tree vs 256 MB declared), `peak_pid` null on 6/6 E1c calls, `peak_tree_pids` carries the full pid set. |
| F-I14A-04 | low | oracle §4 said `calls.failed == 1`; the harness runs 6 calls | `harness/fixture_spec.py` case expectations; `harness/run_probe_cases.py` (`--samples 3`) | **ACCEPTED.** Corrected in `oracle.md` §9.2. Only the oracle's arithmetic was wrong — the measured values were already 6/6 and no expectation was relaxed. |
| F-I14A-05 | low | the `catalog_dir` parser's boundaries were undocumented | `config_catalog_dir()` / `check_catalog_binding()` in `iso/slo_probe_patched.py` | **ACCEPTED.** `oracle.md` §9.3 and `decision.md` D2 now list exactly what it parses and what it refuses (no block scalars, inline maps, anchors or escapes; residual `${` ⇒ `ValueError` ⇒ exit 3, fail-closed). |

### Ownership recorded (not self-assigned)

| decision | owner | state |
|---|---|---|
| D1 | ops reviewer — **not the author of this probe** | UNSIGNED ⇒ **promotion is forbidden** |
| D2 | production SLO / probe owner | awaiting confirmation |
| D3 | I-16 | awaiting decision |

`iso/slo_probe_patched.py` remains sha256
`14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e` — unchanged by this pass, so the
reviewer's re-runs stay valid. New evidence from this pass:
`before/cmd-E5b/{report.json,stderr.txt,stdout.json}` and `after/r2_review_evidence.md`. No card
command's expected return code changed.

---

## r2 re-read — disposition of P4/P5 and the reviewer's un-verified list (APPEND-ONLY)

The r2 re-read **confirmed accepted_scoped** for the isolated measurement fix (implementation code
unchanged; none of the five corrections written up as "fixed"; D1/D2/D3 none self-closed) and raised two
**document-only** defects, both fixed. Nothing here changes a result, a budget or an exit code.

| # | sev | the finding | file:line | disposition |
|---|---|---|---|---|
| P4 | medium (doc) | `after/summary.json:r2_new_hashes` cited `handoff.json` as `ee4df40e…5a1f` and `binding.json` as `4181048b…33cf`, but both files were edited 66–78 s **after** the hash was taken, so the citations were dead on arrival (measured then: `2d955e3a…88b6` / `d713c6c3…4080`). The reviewer confirmed the content change was append-only — a stale hash chain, not a content rewrite. | `after/summary.json:r2_new_hashes` written 03:14:12; `binding.json` 03:15:18; `handoff.json` 03:15:30 | **FIXED.** The block is recomputed and now carries `captured_at_utc` plus an explicit `self_invalidating: true` marker for entries whose value cannot be stable inside the file that cites it. Rule adopted: **a hash citation names the file and its capture time**; a value taken before a later edit must never be presented as current. |
| P5 | low (doc) | `after/r2_review_evidence.md:12` presented the 40-character prefix `f051feec00658bb5fefee8d2ab3c4a34643199d5` as the sha256 of `iso/tool_prod/slo_probe.py`; it is neither a sha256 nor a git blob id. | `after/r2_review_evidence.md` hash table | **FIXED.** Full value restored: `f051feec00658bb5fefee8d2c2c7630e0bd348b5384ae80f0c882c822f48059`; the table preamble now states the file+capture-time rule. |

### D1/D2/D3 — unchanged and still unsigned

Ownership stands: **D1 → an ops reviewer who is not this probe's author; D2 → the production SLO /
probe owner; D3 → I-16.** Until D1 is signed, `iso/slo_probe_patched.py` must **not** enter
`RF/tools/`; and before I-16's production measurement a bundle measurement file must be supplied, or the
default invocation will always exit 2 (the F-I14A-01 contract change, still awaiting signature).

### Reviewer's un-verified list — carried forward verbatim, NOT treated as proven

1. the per-root location counts were not recomputed row by row by the reviewer;
2. only the first row of the r2 census top-5 was checked;
3. the US-MSFT raw artifact was not re-hashed by the reviewer;
4. the resolve path remains unmeasurable in isolation (no live resolve was run);
5. the `state.json` sub-fields were not checked field by field;
6. the r2-produced evidence cannot be externally anchored (it is this attempt's own output);
7. the substantive merits of D1 are outside the reviewer's scope;
8. the r1 re-run conclusions remain valid only because the tool's bytes did not change.

### Limited reservation accepted (not blocking)

`after/snapshot.json` was captured at `2026-09-20T02:14:43Z`, before the parent agent deleted the leaked
`git_filing-fetch.txt`, so its `porcelain["filing-fetch"] = ["?? git_filing-fetch.txt"]` is **stale but
conservative** while `porcelain_product_only["filing-fetch"]` is correctly empty — not a fabricated
value. It was not refreshed: a re-run would be a new command and the recorded value is already the
stricter one.

### Cross-card carry-forward

I-07-B must bind a **production-isomorphic (or table-filtered)** catalog;
`iso/catalog/catalog.sqlite3` is a 5-table minimal schema and **must not** be reused. The prohibition is
recorded in both `I-07-A/.../state_matrix.json:isolated_catalog_prohibition` and
`I-07-A/.../handoff.json.blocked_by`.

---


> **Attribution marker, added by the independent reviewer on 2026-09-20 (APPEND-ONLY; nothing
> above or below was reworded).** The block that starts at `## r3 re-read …` was **not written by
> this reviewer**, and this reviewer is **not the author** of the verdict sentence at line 235
> ("The r3 re-read **confirmed accepted_scoped**"). No reviewer-authored r3 block existed at the
> time this marker was added; the reviewer's own record of the r3 findings is appended as a new
> section at the end of this file, and the per-item evidence is stated there. `handoff.json`'s
> `reviewer_status_source` (which cites `review.md:233-263` as reviewer-authored) is inaccurate on
> that point.
## r3 re-read — P4/P5 closed, N2 fixed, and one reviewer error NOT carried forward (APPEND-ONLY)

The r3 re-read **confirmed accepted_scoped** for this card, closed P4 and P5, and **withdrew its own
mid-course P4 misjudgement** (it had read this host's UTC+0 local clock as a stale timestamp). Two
low-risk residues remained; the relevant one is fixed here. Nothing in this section touches a result, a
budget or an exit code, and the fixture runner carries no round-3 residue.

| # | residue | disposition |
|---|---|---|
| **N2** | `after/summary.json:r2_new_hashes.captured_at_utc` was a **naive local time** carrying a hand-written `+00:00` label. It was correct only by accident on this host: `datetime.now().isoformat()` returns local wall-clock, and the interpreter's own zone table here already disagreed with the system clock (local 03:49 vs UTC 02:49 while `time.timezone` reported 0), so the value was not merely fragile — it was already an hour off. | **FIXED.** Now `datetime.now(timezone.utc).isoformat()`, the same construction `after/snapshot.json` uses. The pre-fix value `2026-09-20T02:44:48.028154+00:00` is **retained, not deleted**, under `corrected_for_review_finding_N2` together with why it was invalid and the verified fix. The whole `values` block was recomputed in the same write so hashes and capture stamp belong to one moment, and the paths are declared attempt-root-relative. |
| N1 | the word "six" at `oracle.md:211` / `review.md:133` (I-07-A) counts **findings**, not dimensions, and was not covered by that oracle's §8 table | **FIXED in the I-07-A attempt** — a third row was added to `oracle.md` §8 stating that "six" there means findings (F-I07A-01…06) and that for any dimension question §8 and `dimension_alignment` (7 plan rows / 8 families / 29 cells) are authoritative. Recorded here because the two attempts are read together. |

### Reviewer error explicitly NOT carried forward

A re-read reported `company-wiki` porcelain as **completely empty**, including ` M CLAUDE.md` and
` M README.md`. **That is wrong.** Measured here: `git -C company-wiki status --porcelain` returns
exactly two lines — ` M CLAUDE.md`, ` M README.md` (sha256 `963869fa08…` / `302bd10b38…`, mtime
2026-09-19 11:20, both differing from their HEAD blobs). The user's pre-existing edits are still present
and were **not** reverted. No conclusion depends on it (neither file is in this card's anchor set, and
`-- src config scripts tests` is empty), but the record must read "only the two pre-existing ` M`
entries", never "completely empty".

### Repository head pointer

This attempt captured `revenue-forecast HEAD = 7d7ea1edc5e0371ffefee0d2ab3c4a34643199d5`. The
orchestration layer has since advanced it to `1ac01f029c16b90adba92dd0f1bc3a1825ff9552`. That commit
touches only `.planning/` (49 files); `tools/slo_probe.py` keeps blob id
`413aad5f788732520ace76acbaebcf06633f34d5` at both HEADs and in the worktree — the fact this card's RED
baseline rests on — and `7d7ea1ed` is its ancestor. The captured snapshot is correct for its capture
time and was deliberately not rewritten. Also recorded in `handoff.json:head_pointer_note` and
`recovery/README.md`.

---

## r4 — reviewer's own attestation: r3 re-read NOT authored by me, with the scope I can actually claim (APPEND-ONLY)

**Written and appended by the independent reviewer on 2026-09-20.** Nothing above this section was
edited, reworded or deleted; this section is a pure append, and the attribution marker inserted at the
`## r3 re-read` boundary is a pure insertion.

### 1. Can I claim the `## r3 re-read …` block (this file, lines 233–263 before this append)?

**No.** That block was **not written by me**, I did not author the sentence *"The r3 re-read **confirmed
accepted_scoped** for this card"*, and I cannot sign it as my r3 block. My r3 findings reached the
parent agent as a report, not as text in this file; the block appears to have been transcribed from
that report by a bookkeeping pass. Its substance happens to correspond to what I reported, and I have
re-derived its checkable claims below — but **"I can reproduce the claims" is not "I wrote the
verdict"**, and the difference is the whole point of an independent review.

Consequently, `handoff.json:reviewer_status_source` — which cites `review.md: :3 / :156 / :189 /
:233-263` as reviewer-authored sections — is **not accurate for `:233-263`**. The reviewer-authored
sections are the `PENDING independent review` preamble, the r2 block (`## r2 — disposition …`), and
this section. A successor must not cite `:233-263` as the independent reviewer's own words unless the
reviewer appends them.

### 2. What I re-verified, now, by command

Verification object and time anchor: attempt `I-14-A/a20260919-01`, read-only, at
**2026-09-20 ~04:20 local (UTC+0 on this host)**. Frozen card text `card_I-14-A.md` sha256
`1376a60a6a7e468b5532e32a6e98a57ea9034fbdb3aab5d923ea3aca50b7c35d` — matches the anchor recorded in
this attempt's own `after/snapshot.json`, so the card text I re-read is the frozen one.

| claim in `:233-263` | what I measured now | verdict |
|---|---|---|
| P5 closed | `after/r2_review_evidence.md` sha256 `a7a51fbb9498a8fab83cd6ca90af5f474bb6e541845262109a8279d34e374f37`; its `iso/tool_prod/slo_probe.py` row now carries the full `f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059`, and the bogus 40-char prefix is absent | **reproduced** |
| N2 fixed | `after/summary.json:r2_new_hashes.captured_at_utc` = `2026-09-20T02:51:24.711059+00:00` — a genuinely offset-aware stamp (the pre-fix value `…02:44:48.028154+00:00` is retained under `corrected_for_review_finding_N2` with its invalidity reason) | **reproduced** |
| N1 closed | `I-07-A/oracle.md` §8 now has a **third** row covering `oracle.md:211` / `review.md:133` ("six" counts findings, not dimensions); file sha256 `a279bccb009c1e4f68494a2eb3e0765c2354cb0f2c673a95e78432937f9bf8e1`; the frozen region through line 245 is untouched (`F-I07A`/`r2`/`r3` occurrences inside it: 0) | **reproduced** |
| "no round-3 residue in the fixture runner" | `harness/**`, `iso/fixtures/**`, `harness/tests/**` contain no `r3` / `round-3` / `round3` / `N2` / `P4` marker | **reproduced** |
| reviewer error not carried forward | `git -C company-wiki status --porcelain` returns **exactly two lines**: ` M CLAUDE.md`, ` M README.md` (on-disk sha256 `963869fa08c042306b3baf12b56f3ecfdb592cd88b4e619565e97dccb64c23be` / `302bd10b386b4aad425b812edd2cbbf05f4d7d12a28865404172eae2f1858512`, mtime 2026-09-19 11:20, both differing from their HEAD blobs). **The r3 `:247-253` correction is right and my own r3 report was wrong** — see §3 | **reproduced** |
| frozen bytes unchanged | `iso/slo_probe_patched.py` `14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e`; `changes.diff` `fcb9ae658c9c261bf4dc06c1f9523dad5fdefccae0b4161a50909870d01a7aee`; `iso/tool_prod/slo_probe.py` `f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059`; production `RF/tools/slo_probe.py` same sha256 with `git hash-object` == `git rev-parse HEAD:tools/slo_probe.py` == `413aad5f788732520ace76acbaebcf06633f34d5` | **reproduced** |

### 3. My own error, retracted in writing

In my r3 report I stated that `company-wiki` porcelain was **completely empty**. That was wrong, and
the cause was my own command: a PowerShell subexpression using a non-existent `-NoNewline` parameter
on `Out-String` failed, the failure was swallowed inside a string interpolation, and I read the empty
rendering as command output. The same broken command produced my (correct, but accidentally obtained)
`revenue-forecast -- tools` reading; I have since re-run both cleanly: `-- tools` exits 0 with no
output, and company-wiki has exactly the two pre-existing ` M` entries. **Withdrawn: "completely
empty". Correct: "only the two pre-existing ` M CLAUDE.md` / ` M README.md` entries".**

### 4. One assertion in `:233-263` that I could NOT reproduce

`:242` asserts that "the whole `values` block was recomputed in the same write so hashes and capture
stamp belong to one moment". Measured now: **11 of the 12 cited entries match the live files, and one
does not** — `handoff.json` is cited as `c5ba34d716f3cd1cdb0722c8d736b86b302949d0e2c3d9db4e110d6cf012a0c3`
while the file is now `6722ab34e91defae3fdcbb256eae5f6afd83d0fe5ab35f841d20dc62ca06cac0` (20445 B,
mtime 2026-09-20 04:17:53, i.e. **edited after the 02:51:24 capture**). Because the record had to be
extended again after the capture, the citation went stale a second time; the defect class the r2 re-read
raised (P4) is therefore **live again in its narrowest form**, exactly as its own rule predicts — the
rule is right, but it needs to be applied at hand-off time, after the last write, not before it. Also
verified: `handoff.json` contains **no** citation of its own hash (12 distinct 64-hex strings, none of
them self), so the earlier "self-citation removed" statement holds; the stale value is summary.json's.

### 5. Conclusion, and the scope I am NOT granting

**`accepted_scoped` — for the isolated measurement fix only**, and limited to the exact card scope:
`AF-I14A` — the three fixtures behave as frozen, command-total / business-latency / RSS-sampling windows
are reported separately, success latency and failure rate are reported separately, and budgets are
untouched. Earlier rounds' findings stand as recorded (F-I14A-01..05 and P4/P5 closed or registered as
limits/contract changes, none written up as "fixed"). `card_I-14-A.md` claims **nothing** about
production SLOs, the production catalog, bundle-consumption latency, resolve behaviour, or prediction
accuracy; the bookkeeping fields are therefore qualified as follows and must not be asserted as
reviewed: **`disclosure_adaptation` = unmapped** (this card never touched the log-redaction clause —
that is I-14-C) and **`accuracy` = unproven** (no prediction, no accuracy claim, no basis for one).

**This card's verdict remains `review_pending` as a card status**: `accepted_scoped` here is the
reviewer's qualification of the isolated fix, not a promotion and not a card closure. **D1/D2/D3 remain
unsigned** — D1 → an ops reviewer who is not the author of this probe; D2 → the production SLO / probe
owner; D3 → I-16 — and the promotion prohibition stands: `iso/slo_probe_patched.py` must not enter
`RF/tools/` until D1 is signed, and before I-16's production measurement a bundle measurement file must
be supplied or the default invocation exits 2.

### 6. Not verified by me (coverage ends at the measurements above)

1. Everything in my r1/r2/r3 "not verified" lists, which remain carried forward in this file and in
   `handoff.json:reviewer_unverified_list_carried_forward`.
2. This append covers **only** the claims listed in §2 and the counter-claim in §4. Any other statement
   inside `:233-263` is someone else's text and is **not endorsed by this signature**.
3. The r1 re-runs (`--all`, the pytest suite, `changes.diff` regeneration) were **not** repeated in this
   append; they remain valid only because the tool and diff bytes above are unchanged by hash.
4. I did not observe any writing command of this round, so I cannot attest to *when* or *by which
   process* `:233-263` was produced; I can only attest that it was not me.

**Appended by the independent reviewer on 2026-09-20.** Coverage of this append ends at the
measurements listed in §2 and §4.


### 7. Line-number clarification for this append (added immediately after §1–§6; APPEND-ONLY)

Adding the attribution marker shifted every line below it, so the numbers quoted in §1 and §2 must be
read with both frames:

| content | line numbers in the 263-line revision I read (before this append) | line numbers now (367 lines) |
|---|---|---|
| `## r3 re-read …` heading | 233 | **240** |
| "The r3 re-read **confirmed accepted_scoped** for this card" | 235 | **242** |
| the N2 row that asserts the `values` block was recomputed in one write | 242 | **249** |
| "Reviewer error explicitly NOT carried forward" (company-wiki porcelain) | 245 | **252** |
| the company-wiki measurement lines | 247–253 | 254–260 |
| repository head-pointer subsection | 255–263 | 262–270 |
| attribution marker (inserted by me) | — | 233–238 |
| this r4 attestation | — | 276–367 |

The sentence I decline to own is, verbatim: `The r3 re-read **confirmed accepted_scoped** for this card,
closed P4 and P5, and **withdrew its own mid-course P4 misjudgement**`. It is at line 242 now and was at
line 235 in the revision I read; either frame identifies the same sentence, and in neither frame did I
write it.
