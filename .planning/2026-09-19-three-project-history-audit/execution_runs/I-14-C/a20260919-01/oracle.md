# I-14-C oracle — frozen BEFORE any run of this attempt

Status: FROZEN at 2026-09-19, written before `before/` and `after/` exist.
Author: implementer (not the reviewer). The implementer never writes "accepted".

## 0. What the audit actually complained about

`PLAN/audit_report.md` row "section 查询、prune、日志脱敏等" and
`reviews/wiki_legacy/exception_event_probe.json` both show that the ONLY evidence for the
redaction claim was:
- the helper `observability._redact_detail` exercised on path-like `detail`, and
- `worker._write_unhandled_exception_event` invoked **directly** (`method_only: true`).

Nothing ever checked the **real exception exit**: the three `except BaseException` /
`except RuntimeError` handlers that call that method, the event JSONL they persist, the
re-raise, the Python traceback on stderr, and the CLI's generic handler that prints
`error_taxonomy.structured_error(exc)` to stderr.

This card does NOT re-run the worker and does NOT touch production logs.

## 1. Synthetic values (no real secret can be read)

The only credential-shaped values used are these literals, and nothing else:

```
SYNTHETIC_AUDIT_TOKEN            <- bare marker, must appear in NO output
Authorization: Bearer SYNTHETIC_AUDIT_TOKEN
token=SYNTHETIC_AUDIT_TOKEN
api_key=SYNTHETIC_AUDIT_TOKEN
password=SYNTHETIC_AUDIT_TOKEN
```

They are non-secret placeholders. The card's point is the *form*, not the value.

## 2. Frozen redaction contract (the rule that is being frozen)

R1. Credential-shaped **values** must be replaced by the marker `<redacted>`:
    - `Authorization: <scheme> <value>` (scheme optional, case-insensitive, value may be quoted)
    - `Bearer <value>`
    - `<key> = <value>` / `<key>: <value>` / `<key>=<value>` where `<key>` in
      {`token`, `access_token`, `refresh_token`, `api_key`, `apikey`, `secret`,
      `client_secret`, `password`, `passwd`, `authorization`} (case-insensitive)
R2. Redaction is applied to the **real exit**, not to a helper in isolation. "Real exit"
    for this card means all three of:
    (a) the JSONL event line written by `SourceCatalogWorker._write_process_event`
        at each of worker.py:949 / :975 / :1042,
    (b) the process-level stdout/stderr produced when the exception is re-raised and when
        `error_taxonomy.structured_error` is printed by cli.py:1551-1558,
    (c) the `cause` chain reachable through `BaseException.__cause__` /
        `__context__` (nested cause is inspected even though only the top message is persisted).
R3. Ordering: **redact first, truncate second**. Truncation must never be the mechanism
    that "protects" a value, because truncating first can cut a credential in half and
    still leave a readable prefix in the log.
R4. Non-sensitive diagnostics must SURVIVE unchanged: `exception_type`, `stage`,
    `error code`, `request_id`, and any message text that contains no credential shape.
    A normal exception must not be swallowed: it must still be re-raised, still write
    `unhandled_exception` before `process_exiting`, and still keep its type.
R5. Coverage is NOT claimed for unknown secret forms. Values with no credential-like key
    next to them are documented as out of scope.

## 3. Cases and frozen expectations

E1 — real-exit counterexample (pre-fix expectation = LEAK, post-fix = CLOSED).
  Input: stub session that raises `RuntimeError("Authorization: Bearer SYNTHETIC_AUDIT_TOKEN ...")`
  driven through the **unmodified** `run_forever(control=...)` path, in a subprocess whose
  cwd is this attempt dir and whose state_path is under the attempt dir.
  Pre-fix expectation (must be reproduced, not assumed):
    - `worker_process_events.jsonl` line `unhandled_exception` contains `SYNTHETIC_AUDIT_TOKEN`
      (bare marker grep hit),
    - stderr contains `SYNTHETIC_AUDIT_TOKEN`,
    - events order is `process_starting`, `session_opened`, `unhandled_exception`, `process_exiting`.
  Post-fix expectation:
    - `grep SYNTHETIC_AUDIT_TOKEN` returns **0 hits** in stdout, in stderr and in the JSONL,
    - the marker `<redacted>` IS present in the event (proves redaction ran, not that the
      field was dropped),
    - `exception_type == "RuntimeError"`, event order unchanged, exception still re-raised
      (subprocess return code stays 3, i.e. the harness's own "re-raised" sentinel).
E2a — real exit with NESTED CAUSE:
  `raise RuntimeError("stage=summarize code=llm_global_failure request_id=req-SYNTH-0001")
   from ValueError("Authorization: Bearer SYNTHETIC_AUDIT_TOKEN")`
  Expectation: no marker anywhere; `cause_types == ["ValueError"]`;
  `message_redacted` still contains `stage=summarize`, `code=llm_global_failure`,
  `request_id=req-SYNTH-0001`.
E2b — UNKNOWN KEY with a sensitive value:
  message `upload failed for token=SYNTHETIC_AUDIT_TOKEN` and separately
  `digest=SYNTHETIC_AUDIT_TOKEN` (a key NOT in the R1 key set).
  Expectation: the `token=` form is redacted; the `digest=` form is **allowed to remain**
  and that residual is recorded in oracle-residuals, NOT hidden. Negative expectation is
  frozen explicitly so the implementer cannot silently widen the rule and claim coverage.
E3 — trivial / no-secret exception:
  `KeyError("document not in catalog: doc-1")`
  Expectation: redaction is a no-op (`message_redacted` == the original text modulo
  truncation), event still written, still re-raised, `exception_type == "KeyError"`,
  nothing swallowed.
E4 — truncation boundary:
  message of 300 chars where the credential sits at char ~180 and the message exceeds 200.
  Expectation: `len(message_redacted) <= 200` AND no partial credential prefix present
  (this is what R3 buys; pre-fix the 200-char cut lands inside the token).
E-N1 — helper-in-isolation is NOT accepted as evidence:
  a case that calls `_write_unhandled_exception_event(exc)` directly is included and is
  marked `helper_only`; it must not be the only green case. The card's own exit criterion
  is about the real exit, so the E1/E2 real-exit cases are the acceptance cases.
E-N2 — negative binding case: a run whose cwd is the company-wiki repo root is refused by
  the harness (returns exit code 97 with `BINDING-REFUSED`) and performs no work.

## 4. Persistence / side-effect expectations

- Only the attempt dir is written. `state_path` is `<attempt>/scratch/worker_state.json`,
  so `worker_process_events.jsonl` lands in `<attempt>/scratch/`.
- No catalog database is created; no scan/normalize/summarize is called; the stub session
  means `_run_cycle_guarded` never reaches a real service.
- No network. No environment variable value is read or printed.

## 5. Exit criteria for this card (as written on the card, restated)

Pass requires: the real exit does not leak the synthetic marker **and** stays diagnosable;
plus the explicit statement that not all unknown secret forms are covered.
Recovery: withdraw the isolated implementation and keep the synthetic logs.


---

# R2 addendum — FROZEN 2026-09-19, before any r2 run

The independent review returned I-14-C = `changes_required` (3xP1). This addendum freezes the
corrected requirement and the new cases **before** the r2 runs. It does not rewrite any
previously frozen expectation; where an earlier expectation was wrong, that is recorded as
such rather than edited away.

## A1. Corrected redaction rule (supersedes R1's key expression only)

The left anchor in R1 was `\b(?:<keys>)\b`. `\b` requires a transition between a word
character and a non-word character, and `_` **is** a word character, so
`GITHUB_TOKEN=…`, `my_access_token=…`, `SLACK_BOT_TOKEN=…`, `AWS_SECRET_ACCESS_KEY=…` were
never matched. Frozen correction:

- left anchor becomes `(?<![A-Za-z0-9])` (so `_`, `-`, `.`, path separators, whitespace and
  string start are all valid boundaries);
- the key expression becomes
  `(?:[A-Za-z0-9]+[_-])*(?:token|secret|password|passwd|pwd|apikey|api[_-]?key|access[_-]?key|private[_-]?key|auth[_-]?token|client[_-]?secret|credential|passphrase)`
  so env-var style names are covered as `<qualifier>_…_<atom>`;
- the same left anchor is applied to the `authorization` / `bearer` alternative for
  consistency;
- explicitly still NOT covered (carry, unchanged): a marker with no credential-like key
  anywhere near it, e.g. a plain path component `…\SYNTHETIC_AUDIT_TOKEN.yaml`.

Frozen negatives that must NOT start matching (over-redaction check): `monkey=`, `oauth=`,
`secretary=`, `tokenizer=`, `keyboard=`, and the diagnostic string
`stage=summarize code=llm_global_failure request_id=req-SYNTH-0001`.

## A2. R3 restated — redact-before-truncate must be *load-bearing*

The r1 E4 case did not prove R3: an unquoted value still matches the bare-value alternative
after truncation, so swapping the order kept E4 green. Frozen restatement:

- **R3'** a truncated message must not expose a partial credential **including when the value
  is quoted**, because a quote-delimited value that has been cut open no longer matches the
  quoted alternative and its leading quote excludes it from the bare-value alternative.
- **E4a (load-bearing)**: message `password: "` + `Q`*300 + `"`, truncated at 200.
  Normal order (`redact` then `truncate`): **0** secret characters survive; the event shows
  `password: <redacted>`. Swapped order (`truncate` then `redact`): the frozen expectation is
  that secret characters DO survive, and the measured count is recorded (reviewer measured
  189; this attempt must reproduce and record its own number, not inherit it).
- **E4b (kept, explicitly labelled non-load-bearing)**: the r1 unquoted case. It must stay
  green in **both** orders; it is retained only as a regression guard.

## A3. New case E5 — the REAL CLI must be executed

The r1 "CLI exit" was a harness-local re-implementation (`drive_real_exit.py` printed the two
lines by hand) and hard-coded `from … import redact_text`, which in the pre-fix tree raised
`ImportError` and produced a traceback artifact. Frozen correction:

- the `--cli-exit` branch of the driver must import the redactor **defensively** (absent
  helper => leave the message as-is), so before/after are comparable and no ImportError can
  be counted as a leak;
- **E5** drives the product's own entry point
  `python -m company_wiki.source_catalog.cli --config <path> status` as a subprocess, with a
  missing config path so that no catalog is ever created or opened:
  - **E5a**: the missing file name is credential-shaped
    (`…\config\token=SYNTHETIC_AUDIT_TOKEN.yaml`).
    Pre-fix: `cli.py:866 args.config.resolve(strict=True)` is **outside** the try, so a bare
    interpreter traceback reaches stderr with the marker. Post-fix: the resolution is inside
    the redacting handler, exit code 1, structured envelope, **0 marker hits**.
  - **E5b**: the missing file name is a bare marker (`…\config\SYNTHETIC_AUDIT_TOKEN.yaml`).
    Pre-fix: bare traceback with the marker. Post-fix: redacted-handler envelope **but the
    marker survives as a path component** — that is the declared R5 limit, frozen here as a
    named residual carry, not as a pass.
  - Both cases must prove `catalog.sqlite3` was NOT created anywhere under the scratch
    project root, and the production catalog must remain untouched.
  - **E5c (measure, may end as a carry)**: an argparse failure
    (`--config <marker>.yaml --definitely-not-a-flag`) — argparse echoes argv on its own
    error path, which is not the `except Exception` handler. The measured result is recorded;
    fixing the parser's error surface is out of this card's allowlist.

## A4. Accounting rules for the before/after tables

- hits are reported **per file** (`stdout`, `stderr`, `worker_process_events.jsonl`) and
  never as a single combined number;
- an artifact hit (e.g. an `ImportError` traceback caused by the harness, not by the product)
  must be listed separately from a product leak;
- the r1 table is corrected retrospectively, not deleted.

## A5. Isolation (frozen)

All product-code copies live under `iso/`:
`iso/product` = pristine HEAD tree (T0), `iso/product_fixed` = T0 + fix (T2),
`iso/product_swapped` = T2 with only `redact_and_truncate`'s two operations exchanged
(order-swap control for E4a). The production tree is read-only from here on; every run uses
`--src iso/<tree>/src`. Any assignment (not copy) of a real product file is a card failure.

---

# R3 addendum

## Provenance of the r3 expectations

Unlike r1/r2, the r3 expectations were **not invented by the implementer**: they are the
r2 review's own wording, received before any r3 run. Quoted verbatim from the review
message:

- F-I14C-07: `_CREDENTIAL_KEY` is "~O(n²)"; pick one of (a) linear candidate + atom-table
  validation in Python, (b) `{0,8}` bounds, (c) a hard input cap; and whichever is chosen
  must add "长 `_` 分隔串" cases covering the chosen boundary (k=1000/2000/40000) that
  assert a bounded return time, give a k=200…40000 timing table with the r1 control, and
  confirm E4a/E4b/E5a stay green;
- C8's stated reason is wrong and must be rewritten;
- the over-redaction table must gain `pwd=` and distinguish r2-new from r1-existing;
- C10 (JSON quoted-key form `{"key": "value"}`) is to be registered as pre-existing.
  Registered: `r3/diagnostics_*.json` → `residuals_confirmed` contains `res-json-quoted`
  in all three trees, i.e. the marker survives `{"api_key": "<marker>"}`.

## Items the implementer chose AFTER measuring (declared, not pre-frozen)

1. **The design.** Option (a) as literally worded was measured first and is **also
   quadratic** (`[A-Za-z0-9_-]+` still backtracks once per start position when the value
   cannot match: `r3/variants.json` → A1 8000 segments = 2.66 s, 16000/40000 = TIMEOUT).
   Option (b) `{0,8}` is linear (40000 = 0.065 s) but silently stops covering keys with
   more than 8 qualifier segments. Option (c) leaves the regex super-linear just below any
   cap. Chosen: a **single-pass scanner** (variant A2), measured linear on every shape
   (`r3/bench_T2-r3-scanner.json`, worst case 0.0619 s at k=40000). The scanner keeps the
   reviewer's intent — no nesting-dependent quantifier sees the message, and the atom
   decision is an explicit Python table lookup.
2. **Deadline = 5.0 s** for the new cases (`F07_DEADLINE_SECONDS`). Chosen after measuring
   (r3 worst case 0.062 s, r2 >20 s), i.e. it is a regression detector, not a frozen
   service-level objective.
3. **Declared behavioural change:** a rejected key no longer consumes the whole
   `key=value` span, so a genuine credential later in the same text is now redacted
   (`url=https://x?token=…`, `cmd: --token=…`). This was NOT requested; it is a
   consequence of the scanner and is measured as an improvement against the r1/r2 regex,
   with the "no credential inside the rejected key" cases asserted unchanged.

---

# R4 addendum

Expectations again come from the r3 review message (received before any r4 run), not from the
implementer: fix the duplicated key; add an OUTPUT FIDELITY assertion to both tables so that
"value replaced, everything else byte-identical" is part of the criteria and a mangled key
cannot pass; restore the probe baselines (E2b len 34, E4a len 20, E4b len 193) and make the
E5a envelope identify the file again; raise C12 to a hard promotion precondition; register C13
if the fidelity table exposes one.

Frozen before the r4 runs:

- **Fidelity is exact, not approximate.** Every credential entry must equal `expected`
  character for character; every untouched entry must equal its input; residuals must equal
  `expected`. The table scripts exit 2 on any mismatch, so a green "0 leaks" line is impossible
  without fidelity.
- **C13 (new, discovered by the table while writing it):** `"a=1 token=<marker> b=2"` is
  expected to become `"a=1 token=<redacted>"`, because the value is the whole space/tab
  separated run (r1 `_BARE_VALUE` semantics). This is frozen as the accepted behaviour rather
  than "fixed", because the reviewer's E4b acceptance length (193) is derived from it.
- **Flake control:** a compat failure that reproduces identically on the pristine T0 tree is
  environment-dependent, not card-caused; both trees must be run from the same cwd pattern
  before any such claim is made.

Declared after measurement (not pre-frozen): the 5 s F-07 deadline stays as it is, and the
`iso/product_r3` specimen exists only so the fidelity criterion can be shown to catch F-I14C-08.

---

# R5 addendum

**No new expectation was invented at r5.** Every r5 expectation is either (a) the r4 review's
own wording, (b) already-frozen behaviour that had to be written down because the review exposed
it, or (c) mechanically derived. The freeze is recorded here because two of the corrections
change what a green run means.

Frozen before the r5 runs (from the r4 review message, received before any r5 command):

1. **Exit-code convention:** `0 = pass`, `2 = cannot adjudicate` (helper absent / tree not
   importable — never "fine"), `3 = negative verdict` (credential leak, fidelity failure, or a
   **new** over-redaction). Registered pre-existing over-redactions are measured, not verdicts.
2. **Fidelity stays exact and extends to multi-line input.** Every `FIDELITY_CASES` pair must
   match character for character, including pairs whose input contains `\n`.
3. **C13's real consequence is frozen as CURRENT behaviour, with the loss asserted:** an
   unquoted credential value runs to the next `,;&"'|` or whitespace *including across
   newlines*, so `token=<marker> doc=17\nstage=…` loses everything after the value. Frozen
   because E4b's 193-char baseline derives from it; **not** fixed, and not to be "tidied up"
   without a new oracle.
4. **Flake claims require captured per-run evidence and both trees from the same cwd pattern**;
   a claim without captured output is retracted, not restated.
5. **Patch consumability:** the deliverable diff must apply with `git apply` and reproduce the
   fixed tree byte for byte; a diff that only `difflib` can consume is not a deliverable.

Derived after measurement (declared, not pre-frozen):

- `r5/counts.json` is the source of truth for every count in this attempt (rule table 44,
  diagnostics 30, `FIDELITY_CASES` 28, collected nodeids 82); prose numbers must cite it.
- The F-07 deadline stays 5.0 s and C12 stays a hard precondition: the F-07 case is **not**
  promoted to the product test until `pytest-timeout` or a subprocess wrapper exists, because
  the assertion fires only after the call returns.
- The C13 magnitudes are as measured with two independent markers (this attempt's 21-char
  marker and the review's 24-char `ZQ7_REVIEWER_MARKER_9f3c` → 112 in / 34 out); a length
  difference between markers is not a discrepancy.
