# I-14-C review.md

> ## PENDING independent review
> This section is written by the **implementer**. Nothing here is an acceptance.
> A separate session must independently re-derive at least one oracle value and attack the
> cases listed under "reviewer: attack first". The implementer has not signed this card.
>
> **r2 status: `changes_required` items addressed; still PENDING independent review.**
> The r1 implementation was withdrawn by the reviewer (product tree restored to HEAD); the
> fix now lives only in `iso/product_fixed` + `r2-changes.diff`. See "## r2" below for the
> per-item disposition with file:line.

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
