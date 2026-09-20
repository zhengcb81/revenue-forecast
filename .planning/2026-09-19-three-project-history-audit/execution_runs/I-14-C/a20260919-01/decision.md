# I-14-C decision.md

Status: **decision recorded for one scope question; everything else is implementer-level and
was resolved inside the frozen oracle.** The implementer does not self-accept.

## D1-r2 (supersedes the r1 D1 resolution after review)

The r1 review (F-I14C-03) demonstrated that the r1 fix did **not** cover the real CLI exit:
`cli.py:866 config_path = args.config.resolve(strict=True)` sits **outside** `main`'s
`try/except`, so an unreadable `--config` escaped as a bare interpreter traceback (captured
by the launcher into `worker_stderr-*.log`) with the marker intact. The reviewer offered two
options; **option ① was taken**: the pre-`try` exits are now inside the redacting handler.

### What changed in T2 and why it is still "the exception exit"

`cli.py` gained a module-level helper and a small `try` around the three pre-`try` setup
lines (T0-relative lines 866-868). `main`'s existing `except Exception` now calls the same
helper, so there is exactly one error-envelope implementation. This is inside
"允许改异常出口": no command semantics changed, and the envelope keeps its exact keys.

### Residuals this decision does NOT close (named carries)

1. **argparse errors** (`_parser().parse_args`, T0 line 865) go through argparse's own
   `error()` → `SystemExit(2)`, a `BaseException` that never reaches `except Exception`.
   argparse echoes argv, so a secret passed as an argv value is printed. Measured: E5c,
   `returncode=2`, `marker_hits.stderr=1`. Fixing it means replacing the parser's error
   surface — carried, not fixed.
2. **A marker that is not credential-shaped** (e.g. a bare token used as a path component)
   still survives in the envelope. Measured: E5b, `marker_hits.stderr=1` in T2. This is
   exactly oracle R5. The fix does buy the envelope instead of a bare traceback.
3. **Interpreter-level tracebacks from `BaseException`** that bypass `main` are still
   unsanitised (no `sys.excepthook` exists in the product).
4. **`_write_process_event` is not a general gateway** — only the exception exit is gated.
5. **`error_taxonomy.structured_error` still returns raw `str(exc)`.** Real in-repo
   consumer: `identity_cli.py:70-73` prints it as-is.
6. **`store._redact_message`** (`store.py:1480-1487`) documents "sanitize" but only strips
   and truncates to 200 chars.

### Compatibility impact

`worker_process_events.jsonl` gains one additive field (`cause_types`); nothing renamed or
removed, so an N-1 reader keeps working. The CLI's stderr envelope keeps its keys/shape; only
the `error` string can now contain `<redacted>`. `error_taxonomy.structured_error` itself is
untouched, so its cross-repo contract (filing-fetch) is unchanged — at the cost of carrying
finding 5 for any consumer that calls it directly.

### Recovery rule

Revert = apply the inverse of `r2-changes.diff` (or re-materialise `iso/product`), all
hash-verified; `iso/product`, `iso/product_r1`, `iso/product_fixed`, `iso/product_swapped`
are kept so before/after/control can be re-run at any time. Synthetic logs stay in this
attempt dir per the card's recovery clause.

### Rejected alternatives (r1 four, plus one)

1. *Only redact in `worker._write_unhandled_exception_event`* — leaves the stderr leak open.
2. *Make the worker raise a redacted exception copy* — mutates exception identity for every
   downstream consumer and can break `error_taxonomy` classification (which reads `str(exc)`).
3. *Install a `sys.excepthook`* — new global mechanism, needs its own design + reviewer.
4. *Redact every string inside `_write_process_event`* — would also rewrite `catalog_dir`
   and `reason`, changing a persisted diagnostic contract for no security gain on this path.
5. **(new in r2, reason corrected in r3)** *Widen the credential rule's separator to bare
   whitespace so `--api-key <value>` is covered* — rejected because **the flag form needs new
   separator semantics whose false-positive cost on ordinary `key value` prose exceeds its
   benefit**, not for the reason first written here. The r2 wording claimed widening would
   redact `token expired for doc-1`; the r3 review measured that claim and it is **wrong** —
   the colon-less form is unchanged in both trees (`r3/diagnostics_product_r1.json`,
   `r3/diagnostics_product_fixed.json`), while `token: expired` is redacted and already was in
   r1. The flag form stays a measured residual (`run_diagnostic_table.py` → `res-flag`;
   `run_rule_table.py` NOT_REDACTED entry). This is the third correction recorded in this
   attempt rather than edited away.

## D2-r3 (F-I14C-07: the redactor must be linear)

The r2 fix introduced a quadratic rule in `observability._CREDENTIAL_KEY`
(`(?:[A-Za-z0-9]+[_-])*<atom>(?:[_-][A-Za-z0-9]+)*`), and `redact_and_truncate` feeds it the
**whole untruncated exception message**. Measured: 20 s per-case cap exceeded at 16000
segments.

**Chosen: option (a)'s INTENT, implemented as a single-pass scanner.** Note the reviewer's
literal wording of (a) was measured first and does **not** fix it: a key-candidate regex
`[A-Za-z0-9_-]+` still backtracks once per start position when the value cannot match
(`r3/variants.json`: 8000 → 2.66 s, 16000/40000 → TIMEOUT). Option (b) `{0,8}` is linear but
silently drops coverage for keys with more than 8 qualifier segments — a coverage cliff in a
security path, the same class of failure this card exists to remove. Option (c) leaves the
regex super-linear just below any cap and changes the redaction semantics of over-cap input.
`A2-scanner` is linear on all ten adversarial shapes (`r3/timing_three_way.json`, worst case
0.0619 s at k=40000).

Cost of the choice, declared: a hand-written scanner is more code than one regex (about 70
lines), so it is pinned by the same frozen rule table (20 positives + 8 guards: 0 leaks /
0 over-redaction), by a 15-entry diagnostic corpus, and by the full exit suite (50 passed).
The `authorization`/`bearer` regex is retained because its keys are fixed literals with no
nesting over the key, and its timing is measured as well.

Also declared: the scanner changes one behaviour — a rejected key no longer consumes the
whole `key=value` span, so a genuine pair later in the same text is now redacted
(`url=https://x?token=…`, `cmd: --token=…`). This is an improvement, not a regression, and
it is frozen by a test together with the cases that must stay untouched.

## D3-r4 (F-I14C-08: correctness criteria must include output fidelity)

The r3 scanner wrote the key twice (`tokentoken=<redacted>`). The code defect was one line,
but it survived every r2/r3 check — rule table "0 leaks", diagnostics "0 over-redaction",
50 green suite tests, E5a stderr 0 hits — because **every criterion asked only whether the
marker had disappeared, never whether the output was still faithful to the input**.

**Decision: output fidelity is now part of the acceptance criteria, not an optional extra.**

- `harness/run_rule_table.py` and `harness/run_diagnostic_table.py` carry a hand-written exact
  expected output for every entry and **exit 2** on any mismatch, so a run can no longer report
  "0 leaks" without also passing fidelity. On the r3 specimen this yields `0 leaks` **and 24
  fidelity failures** — the exact blindness is now visible.
- The suite adds `test_f08_output_fidelity_exact` (**24** exact pairs at r4 — this line said
  "23" until F-I14C-R4-01; r5 extends the block to 28, `r5/counts.json`) plus two real-exit
  fidelity cases (event string + length; E5a envelope must still identify the config file).
- Consequence for the reviewer: "the marker is gone" is no longer sufficient evidence for any
  redaction claim in this card.

**C12 is a hard precondition.** The r4 review retested and the F-07 case hangs (>90 s, then
>300 s killed) instead of failing when the redactor blocks, because the 5 s assertion runs
after the call returns. The promoted product test **must** add `pytest-timeout` or run the call
in a subprocess with a hard timeout. This is not advice: the case stays in the harness until
that wrapper exists (the harness's own discriminator is `harness/bench_redact.py`, which caps
each measurement at 20 s in a subprocess).

### C13 (corrected at r5 — the consequence was understated by ~an order of magnitude)

**The value's stop set is `,;&"'|` plus whitespace, and an unquoted value CROSSES NEWLINES.**
So the value is not "the whole space/tab separated run" — it is everything up to the next
comma/semicolon/quote/pipe, however many lines that spans. Measured (F-I14C-R4-02):

| input | output |
|---|---|
| `a=1 token=<marker> b=2` | `a=1 token=<redacted>` |
| `'upload failed for token=<marker> doc=17\nstage=summarize code=llm_global_failure request_id=req-1'` | `'upload failed for token=<redacted>'` (reviewer's 24-char marker: **112 chars in → 34 out**; `doc=17`, `stage=summarize`, `code=llm_global_failure`, `request_id=req-1` all lost) |

It is **not truncation** (34 ≪ 200, the truncation cap) and **not r3/r4-introduced**:
`iso/product_r2` reproduces it identically, i.e. it is inherited from r1's `_BARE_VALUE`
(`X+(?:\s+X+)*`, whose `\s` matches `\n`).

**Decision: registered and frozen, not changed.** No code change was made, because (a) E4b's
193-char acceptance length is derived from exactly this behaviour, and (b) narrowing the value
to a single token changes the E4b baseline and the envelope width, so it needs its own oracle
and its own card. What r5 adds is that the loss is now **explicit and asserted** rather than
invisible: rule table `cred-multiline-swallow` / `cred-multiline-stopped-by-semicolon` /
`cred-multiline-then-key`, diagnostic corpus `cred-multiline-swallow` +
`diag-multiline-no-credential`, three multi-line `FIDELITY_CASES` pairs and one untouched
multi-line diagnostic, and `test_f08_c13_multiline_loss_is_frozen_not_hidden`. If anyone
narrows the value later, that test fails and the oracle has to be rewritten — which is the
point of freezing it.

## D4-r5 (r4 review's five mechanical findings: exit codes, guard, hashes, counts, guard scope)

Four of the six r5 items are mechanical and were fixed by making the harness *derive* what it
previously asserted by hand. Two of them are decisions, recorded here.

**(1) Exit-code convention adopted from `run_card.py`: `0 = pass`, `2 = cannot adjudicate`,
`3 = negative verdict`.** Both tables now follow it. `2` is reserved for "the thing under test
could not be exercised" (helper absent / tree not importable) and never means "fine"; `3` means
a measured negative (credential leak, fidelity failure, or a **new** over-redaction). Registered
pre-existing over-redactions (`known_over_redaction`: `pwd=`, `token: expired`, `secret:
rotated`, `password: ********`) are what the diagnostic corpus *measures* and do not by
themselves make a verdict negative — otherwise the corpus could never report a green baseline
and the F-I14C-08 defect would have been invisible again. Consequence on the five trees:

| tree | rule rc | diag rc | reading |
|---|---|---|---|
| T0 pristine | 2 | 2 | cannot adjudicate (no helper) |
| T1 (r1) | 3 | 3 | 11 leaks / 4 leaks — negative |
| T2 (r2) | 0 | 0 | pass (with 11 fidelity failures hidden by the old scheme; see D3-r4) |
| T3 (r3 specimen) | 3 | 3 | **0 leaks but 27 / 13 fidelity failures** — negative |
| T4 (r5 fixed) | 0 | 0 | pass |

**(2) The guard is a scope guard, not an evidence guard.** `harness/run_guard.py` refuses any
product path *unconditionally* (`company-wiki`/`revenue-forecast`/`filing-fetch` sources,
`.source_catalog`, the production catalog file) and otherwise accepts any scratch root declared
via `I14C_RUN_ROOT`; the test helpers declare the pytest basetemp. Reason for the change: the
r4 review could not run the 17 subprocess-backed cases at all, because the guard rejected a
`%TEMP%` basetemp and its driver exited 97 — an evidence guard that *prevents independent
verification* is worse than the risk it mitigates, and the risk it actually mitigates (writing
into the three production repositories) is fully preserved by the unconditional product-path
refusal. Re-tested refusals: product src → 97; `.source_catalog` → 97; revenue-forecast outside
`.planning` → 97; undeclared `%TEMP%` → 97; declared `%TEMP%` **plus** a product path → 97.
The full 82-case suite now runs both inside the attempt directory and from `%TEMP%` with no
environment variable set (`r5/cmd-r5-outside-execution-runs.txt`).

**(3) Derived counts are the single source of truth.** `harness/report_counts.py` computes the
rule-table entry count, the diagnostic-corpus count, `len(FIDELITY_CASES)`, the collected
nodeid count and the fidelity nodeid count from the source files and writes `r5/counts.json`;
it exits 3 if the two independently derived pair counts disagree. All prose numbers in this
attempt now cite that file (`rule_table_entries 44`, `diagnostics 30`, `fidelity_cases 28`,
`exact_nodeids 28`, `total_nodeids 82`). The hand-written "23" was wrong in five places even
though the code said 24 — the lesson recorded in D3-r4, applied to prose.

## D1-r1 (historical; kept for the record)

**Question.** The card's allowlist is `_write_unhandled_exception_event` + "the existing
redactor and the associated isolation tests". The empirical counterexample (CMD-I14C-B2)
shows the marker leaks on **two** surfaces, not one:

| surface | who writes it | in the card's allowlist? |
|---|---|---|
| `worker_process_events.jsonl` `unhandled_exception.message_redacted` | `worker._write_unhandled_exception_event` | yes, explicitly |
| stderr envelope `{"error": str(exc), ...}` | `cli.py:1551-1558` via `error_taxonomy.structured_error` | not named; the card says "允许改异常出口" |

**Chosen option.** Edit `cli.py`'s generic `except Exception` block (the real user-visible
exception exit, and the only writer of the worker's stderr log —
`scripts/source_catalog_worker.ps1` redirects the child's stderr into
`worker_stderr-<tag>.log`), redacting the envelope there. Do **not** touch
`error_taxonomy.structured_error` itself.

**Why.** `error_taxonomy.structured_error` is a shared, versioned producer
(`ERROR_TAXONOMY_VERSION = "1.0"`) consumed by filing-fetch; changing its output shape or
content is a cross-repo contract change and belongs to an owner card, not to I-14-C. The
CLI's except-block *is* "the exception exit" the card names, so redacting there is inside
the card's intent, and it fixes the actual stderr leak.

**Counterexample against the chosen option.** A consumer that imports
`error_taxonomy.structured_error` directly (instead of going through the CLI) still gets
the raw value. Evidence: the before-pass `E2b-residual` stderr line was produced through the
CLI path; the harness `drive_real_exit.py --cli-exit` reproduces the CLI's own two lines
(`structured_error` then `redact_text`) precisely so that this residual is visible rather
than papered over. Residual recorded in review.md as an open gap; the fix belongs to a
follow-up card that owns `error_taxonomy.py`.

**Compatibility impact.** `worker_process_events.jsonl` gains one additive field
(`cause_types`); nothing is renamed or removed, so an N-1 reader keeps working.
`cli.py`'s stderr envelope keeps its exact keys and shape.

**Recovery rule.** Revert = re-apply the inverse of `changes.diff` (or `git apply -R`);
the pre-image bytes are reconstructed deterministically by `harness/build_prefix_tree.py`
and hash-verified, so recovery can be proven, not just asserted. Synthetic logs stay in
this attempt dir per the card's recovery clause.

**Rejected alternatives.**
1. *Only redact in `worker._write_unhandled_exception_event`* — leaves the stderr leak
   open; fails the card's requirement that the marker not appear on stderr.
2. *Make the worker raise a redacted exception copy* — mutates exception identity for every
   downstream consumer and could break `error_taxonomy` classification (which reads
   `str(exc)`); too broad for one card.
3. *Install a `sys.excepthook`* — no such hook exists anywhere in the product today; adding
   a global hook is a new safety mechanism and needs its own design + reviewer.
4. *Redact every string inside `_write_process_event`* — would also rewrite `catalog_dir`
   and `reason`, changing a persisted diagnostic contract for no security gain on this path.

## NA items

- No schema/migration/transaction decision is needed: nothing persisted changes shape
  except the additive `cause_types` field.
- No statistical/threshold decision is needed.
- `store._redact_message` is **NA for this card**: it is named `_redact_message` but only
  strips/truncates to 200 chars; it feeds `document_fingerprint_state`, whose writer is the
  normalizer, not the exception exit this card is about. It is recorded as a separate open
  gap rather than silently changed (changing it would move `normalizer` behaviour, outside
  this card's allowlist).
