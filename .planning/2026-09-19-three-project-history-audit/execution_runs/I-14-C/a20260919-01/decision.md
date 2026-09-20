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
5. **(new)** *Widen the credential rule's separator to bare whitespace so `--api-key <value>`
   is covered* — rejected: it would redact ordinary diagnostics such as
   `"token expired for doc-1"`, which oracle R4 forbids. The flag form is carried as a
   measured residual instead (`harness/run_rule_table.py` NOT_REDACTED list).

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
