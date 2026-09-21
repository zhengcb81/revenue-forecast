# I-14-D oracle — FROZEN before the first run of this attempt

Status: FROZEN 2026-09-19 (UTC), written before `before/` and `after/` received any
run output and before `iso/product_narrow` was edited.
Author: implementer (never the reviewer). The implementer does not self-accept.

Every expected string/length below was **computed by hand from the frozen semantics
text** (card I-14-D + I-14-C `decision.md` §C13 + the r5-final redactor source, which
was read but not executed). No `expected` value was produced by calling the function
under test. The reviewer is asked to re-derive each number (card exit clause:
"E4b 新基线经独立 reviewer 复算").

## 0. Scope

Parent: I-14. Source: I-14-C r5 `decision.md` §C13 (defect measured in
F-I14C-R4-02, frozen unchanged there because it derived E4b's 193-char baseline).
This card narrows the bare-value greedy semantics to a single token on the
assignment path and removes the cross-line swallow on the authorization path.

Trees (all attempt-local copies; production repos stay READ-ONLY):

| tree | content |
|---|---|
| `iso/product_base` | byte copy of I-14-C r5-final `iso/product_fixed` (T4). `observability.py` sha256 `c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c`, `worker.py` `120561f5…`, `cli.py` `4087c172…` — all three verified equal to I-14-C `r5/final_hashes.json` before this attempt ran anything. |
| `iso/product_narrow` | `product_base` + this card's narrowing (the fix under review) |
| `iso/product` | byte copy of I-14-C's pristine T0 tree (needed by the copied suite's E5a/E5b before-arm; unchanged here) |
| `iso/product_swapped` | byte copy of I-14-C's order-swap control (needed by the copied suite's control test; unchanged here) |
| `iso/product_mut_greedy` | mutation M1 (below) |
| `iso/product_mut_authnl` | mutation M2 (below) |
| `iso/product_mut_auth1` | mutation M3 (below) |

Markers (synthetic only, no real secret):
`M  = "SYNTHETIC_AUDIT_TOKEN"` (21 chars, same literal as I-14-C)
`RM = "ZQ7_REVIEWER_MARKER_9f3c"` (24 chars, the I-14-C reviewer's marker)

## 1. The narrowed semantics (frozen definition of "single token")

Bare (unquoted) values:

- **Assignment path** (`key=value`, `key: value`, key in the credential atom
  tables): the value is **ONE token** — a run of characters none of which is
  whitespace or one of `, ; & " ' |`. It stops at ANY whitespace, **including
  newlines**. (Card clause 2: "裸值只吃单个 token（遇空白即停）".)
- **Authorization/bearer path**: the value is a quoted string, or a run of tokens
  joined by **inline whitespace only** (`[ \t]+`, never `\n`/`\r`). The run may
  start with one scheme word (`Bearer`, `token`, …), which is why the old rule was
  multi-word; the line bound is what removes the C13 swallow on this path. A value
  may no longer cross a newline.
- Quoted values are unchanged (same-line quoted string, fully redacted).
- Truncation stays second: `redact_and_truncate` = `redact_text` then `[:200]`.

## 2. Hand-computed expectations (the numbers the reviewer must re-derive)

### N1 — C13 headline (assignment path, multi-line diagnostics survive) — NARROW-MUST

Input `T1 = "upload failed for token=" + M + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"`

| quantity | hand computation | value |
|---|---|---|
| `len(T1)`, M=21 | 24 + 21 + 64 | **109** |
| `len(T1)`, RM=24 | 24 + 24 + 64 | **112** (reproduces I-14-C's frozen input length) |
| current (greedy) output | `"upload failed for token=<redacted>"` | **34** chars, all four diagnostic keys lost (I-14-C F-I14C-R4-02) |
| **narrow output** | `"upload failed for token=<redacted>" + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"` | **98** chars = 24 + 10 + 64 |
| narrow, with RM | same string, marker swapped | **98** as well (24-char marker also collapses into the one `<redacted>`) |

`doc=17`, `stage=summarize`, `code=llm_global_failure`, `request_id=req-1` must all
be present in the narrow output. The output length 98 ≪ 200 proves this is not a
truncation artefact. With RM the pair (112 in → 98 out) replaces the frozen
(112 in → 34 out).

### N2 — middle-line greedy entry (assignment path) — NARROW-MUST

`"a=1 token=" + M + " b=2"` (35 chars) → `"a=1 token=<redacted> b=2"` (24 chars).
`b=2` survives. (This rewrites I-14-C's rule-table expectation
`cred-line-middle-greedy-value`, which encoded the old greedy semantics.)

### N3 — value ends exactly at the newline — NARROW-MUST

`"token=" + M + "\nnext=1"` (34 chars) → `"token=<redacted>\nnext=1"` (23 chars).
`next=1` survives. (Rewrites I-14-C's `cred-multiline-then-key` expectation
`"token=<redacted>"`, which deleted `next=1`.)

### N4 — E4b truncation boundary, the new baseline (real exit) — NARROW-MUST

Scenario `truncation-boundary` (I-14-C `drive_real_exit.py`, unchanged):
`S = "start-" + "x"*170 + " token=" + M + " " + "y"*120`.

| quantity | hand computation | value |
|---|---|---|
| `len(S)` | 6+170+7+21+1+120 | **325** |
| greedy redaction (current) | 325 − (21+1+120) + 10 | **193** — exactly I-14-C's frozen E4b baseline (193 < 200, no truncation) |
| **narrow `redact_text(S)`** | 325 − 21 + 10 = 177 + 7 + 10 + 1 + 120 | **314** |
| **narrow `redact_and_truncate(S)`** (what the event persists) | 314 cut at 200 | **200** — the cap applies for the first time in E4b's history |
| prefix | `"start-"+x*170+" token=<redacted>"` occupies chars 1..193 | the last 7 persisted chars are `yyyyyyy` |
| guards | `M` absent, `M[:8]` absent, `len ≤ 200` | hold in both orders (E4b stays a non-load-bearing regression guard) |

**The E4b guarantee is not broken; the E4b baseline number moves 193 → 314
(pre-truncation) / 200 (persisted).** That move is the expected, card-mandated
consequence (card clause 3), and the new number is frozen here for independent
re-derivation.

### N5 — authorization path no longer swallows across the newline — NARROW-MUST

`"Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"` (66 chars) →
`"Authorization: <redacted>\ndoc=17\nstage=summarize"` (48 chars).
`doc=17` and `stage=summarize` survive.

### N5b — authorization same-line tail still consumed (deliberate keep)

`"Authorization: Bearer " + M + " rejected by provider"` → `"Authorization: <redacted>"`.
The I-14-C E1 baseline (`len 25`, envelope unchanged) is preserved on single-line
inputs; only the cross-line swallow is removed.

### N6..N9 — unchanged family (KEEP-MUST: identical to I-14-C's frozen outputs)

- N6 `"password: '" + M + "'"` → `"password: <redacted>"` (20)
- N7 no-credential texts byte-identical: `"monkey=banana doc=1\nstage=x"`,
  `"stage=summarize code=llm_global_failure request_id=req-SYNTH-0001"` (66),
  `"url=https://example/x?page=2"`
- N8 declared residual `digest=`: `"upload failed for digest=" + M` → unchanged (marker survives)
- N9 declared residual flag form: `"--api-key " + M` → unchanged (marker survives)
- N10 semicolon-bounded: `"a=1 token=" + M + "; b=2"` → `"a=1 token=<redacted>; b=2"` (unchanged from I-14-C)
- N11 `&`-bounded: `"GET /x?token=" + M + "&page=2"` → `"GET /x?token=<redacted>&page=2"` (unchanged)
- N12 no-tail event: `"upload failed for token=" + M` → `"upload failed for token=<redacted>"` (34) — the I-14-C E2b length baseline is unchanged

### N13 — NEW declared residual of the narrowing (registered, not hidden)

A bare secret containing whitespace is redacted **only up to its first token**:
`"password: iron steel"` → `"password: <redacted> steel"`.
(`steel` survives; quoting — `"password: 'iron steel'"` — still gives full coverage.)
The analogous auth-path case: a secret split across a newline loses only its
continuation (`"Authorization: Bearer ab\ncd"` → `"Authorization: <redacted>\ncd"`).
This is the accepted cost of the card's narrowing; it is a **residual entry in the
updated rule table**, not a pass.

## 3. RED→GREEN definition for this card

- **RED (before the edit, on `iso/product_base`)**: every NARROW-MUST case
  (N1, N2, N3, N4-as-314/200, N5, N13-inverse) FAILS — i.e. the frozen new oracle
  is load-bearing. KEEP-MUST cases pass on the base tree (the I-14-C behaviour is
  intact there), and `harness/run_exit_probe.py` on the base tree reproduces
  I-14-C's r5 length row exactly (…, E4b 193, …).
- **GREEN (after the edit, on `iso/product_narrow`)**: all NARROW-MUST and
  KEEP-MUST cases pass; the updated rule table exits 0.
- **The copied I-14-C suite** (`harness/tests/test_i14c_real_exit_redaction.py`,
  byte-identical, sha256 `672b88de585046759f4ef29ce008fdbff9fa76404446ff7ae7317ddf539cce15`)
  is run UNCHANGED on the narrow tree. Its **only** allowed failures are the four
  nodeids that assert the OLD greedy semantics:
  `test_f08_c13_multiline_loss_is_frozen_not_hidden` and the three `FIDELITY_CASES`
  parameters `a=1 token=…  b=2`, `upload failed for token=… doc=17\n…`,
  `token=…\nnext=1`. All other 78 cases must pass. Per card clause 5, those four
  are rewritten by the REVIEWER against this oracle; the implementer does not edit
  them.

## 4. Mutation proof (each mutation is a tree copy; the narrow tree itself is never mutated)

- **M1 `iso/product_mut_greedy`**: narrow tree with ONLY the scanner loop restored
  to the r1 multi-word continuation. Expect: N1/N2/N3 RED again, rule-table entries
  `cred-line-middle-single-token`, `cred-multiline-swallow`, `cred-multiline-then-key`,
  `cred-partial-multiword-secret` fidelity-fail, E4b length back to 193/193.
  N5 stays GREEN (auth fix intact) — proves the scanner narrowing is what fixes the
  assignment path and is what moves E4b.
- **M2 `iso/product_mut_authnl`**: narrow tree with ONLY the auth token join
  `[ \t]+` changed back to `\s+`. Expect: N5 RED again, rule-table
  `cred-auth-multiline-swallow` fidelity-fail; all assignment-path cases stay GREEN,
  E4b stays 200 — proves the auth line-bound is load-bearing for the auth half of C13.
- **M3 `iso/product_mut_auth1`**: narrow tree with the auth value reduced to a
  strict single token (scheme word no longer consumed). Expect:
  `cred-header-bearer` and `cred-header-scheme` LEAK the marker (rule table exits 3
  with non-empty `credential_leaks`) — proves a naive "single token everywhere" is
  WRONG, which is why the card's narrowing keeps the one-word scheme accommodation.

## 5. Persistence / side effects / isolation

- Only this attempt dir is written. Runs execute with cwd inside the attempt; the
  copied harness's guard (`run_guard.py`, unchanged) refuses product paths.
- The real-exit cases import the product's own test doubles from
  `CW/tests/contract/` READ-ONLY (same as I-14-C) and never touch the live catalog.
- No network. No production repo is written; `company-wiki`,
  `revenue-forecast`, `filing-fetch` stay read-only. I-14-C's attempt directory is
  never modified (only read as the source of frozen copies).
- Recovery: apply the inverse of `changes.diff` to `iso/product_narrow` and require
  byte-identity with `iso/product_base` (proven in `recovery/`). The redactor is a
  pure function, so crash-restart evidence is NA.

## 6. Exit criteria (card, restated)

1. 裸值不再跨行吞掉后续诊断键 — N1/N3/N5 GREEN, and M1/M2 show each half is
   load-bearing.
2. 纯合成 marker 必须仍被脱敏 — rule table `credential_leaks == []`, copied-suite
   marker tests GREEN (only the four named nodeids RED).
3. E4b 新基线（314 pre-truncation / 200 persisted）经独立 reviewer 复算 — this
   oracle freezes the hand computation; reviewer re-derives.
4. rule table `cred-multiline-swallow` 系列按新语义更新 — updated expectations are
   the frozen N1/N2/N3 strings, never "turn a failure green": on the BASE tree those
   updated expectations FAIL (RED), which is what makes the update semantic.
5. The frozen I-14-C C13 test keeps its RED state at handoff; its rewrite belongs
   to the reviewer (card clause 5).


---

# CORRECTION 1 (2026-09-19, appended after the first A5 run; original bytes above unchanged)

Section N4, last row of the hand computation, contained an off-by-one: I wrote
"the last 7 persisted chars are `yyyyyyy`". Wrong: char 194 of the persisted
message is the SPACE that separated the value from the y-run, so chars 195..200
are the first **6** y's. The persisted tail is `" yyyyyy"` (space + 6 y's).
Everything else in N4 is confirmed by the A3/A5 runs exactly as frozen:
len(S) 325, greedy 193, narrow pre-truncation 314, persisted 200, prefix
`"start-"+x*170+" token=<redacted>"` occupying chars 1..193, marker and M[:8]
absent. The A5 failure this explains was a transcription error of the frozen
text into the test, not a redactor defect; the probe (A3) had already shown the
true tail (`...cted> yyyyyy`).


---

# CORRECTION 2 (2026-09-21, appended after the independent review; original bytes above unchanged)

The independent reviewer's report is byte-pinned in `reviewer_report.md`
(sha256 `499d91ac…`, 37659 bytes). Verdict: **CHANGES_REQUIRED** — one BLOCKER
(**F-REV-D-01**, credential-persistence regression on the authorization path) plus
five recorded findings and two rulings. This correction records what the review
overturned, and what section 1/2 of this oracle now means. Nothing above is edited;
everything below is additive.

## C2.1 The exit criterion was UNSOUND on the auth path (why this oracle missed it)

Section 2's N5 froze the auth value as a run of tokens joined by inline whitespace
only. That closes C13 — a value can no longer cross a newline — but it also means
that when a line break separates the **scheme word** from the **secret**, the rule
consumes the scheme word alone and the next line is never seen:

* `"Authorization: Bearer\n<SECRET>\ndoc=17"` — the r1 greedy rule persisted
  `"Authorization: <redacted>"` (secret gone, diagnostics gone);
* the r1 tree (this card, before the fix) persisted
  `"Authorization: <redacted>\n<SECRET>\ndoc=17"` — **the full credential written to
  the append-only event log** (diagnostics kept).

The secret's line has no `key=` prefix, so `_redact_assignments` cannot see it
either. The reviewer confirmed this helper-level across 10 variants (LF, CRLF,
RFC-7230 obs-fold, no-space, embedded, `token` scheme, `basic` scheme, marker and a
real-shaped 39-char credential) **and end-to-end through the real worker exit**
(`worker.py` → `redact_and_truncate`). Section 2's N5, N5b, the updated rule table's
48 rows, the copied suite's auth rows and mutations M1/M2/M3 were all blind to it:
no row exercised `scheme␊secret`, and the section 4 mutation plan only tested
whether the line bound *carries* the C13 fix (M2) or whether a *different* candidate
rule leaks (M3).

Consequence for section 6 exit criterion 2: `credential_leaks == []` was **not
sufficient evidence** on the auth path. That is now fixed, and the criterion is
strengthened so this class of blind spot cannot recur (see C2.3).

## C2.2 The auth newline-split family, frozen (new oracle rows N5c/N5d/N5e)

Semantics frozen by the reviewer's RULING 2 and implemented as
`_AUTH_SCHEME_SPLIT`: **after a *known* scheme word** (`bearer`, `token`, `basic`,
`digest`, `oauth`, `jwt`, `apikey`, `api_key`, `sso`) **and exactly one line break,
the first token is redacted (fail closed)**, and the line break plus any indentation
stay OUTSIDE the match. Hand-computed expectations, all three added to
`harness/run_i14d_oracle.py` as NARROW-MUST:

| id | input (M = 21-char marker) | narrow output | len |
|---|---|---|---|
| N5c | `"Authorization: Bearer\n" + M + "\ndoc=17"` | `"Authorization: <redacted>\ndoc=17"` | 32 |
| N5d | `"Authorization: Bearer\n  " + M` (obs-fold) | `"Authorization: <redacted>"` | 25 |
| N5e | `"authorization: token\n" + M` | `"authorization: <redacted>"` | 25 |

N5c is the pair the card's two clauses have to satisfy **together** (secret gone,
`doc=17` kept); N5d/N5e cover the indented continuation and the second key
alternative. On the pre-fix base tree all three FAIL, and on M4 (below) all three
fail again — so they are load-bearing in the leak direction, which the first pass's
oracle was not.

Same-line controls are unchanged by the fix (verified): `"Authorization: Bearer " + M`
→ 25 chars, `"Authorization: Bearer\t" + M` → 25 chars, `"Authorization: Bearer " + M
+ "\ndoc=17\nstage=summarize"` → 48 chars (N5).

## C2.3 N13's auth-path note was MIS-CLASSIFIED — it is a credential-leak regression

Section 2 N13 said the auth-path analogue of the multiword residual "loses only its
continuation" (`"Authorization: Bearer ab\ncd"` → `"Authorization: <redacted>\ncd"`)
and classified it with the assignment-path residual. **That classification is wrong
and is withdrawn.** With a real wrapped header the whole credential survives where the
pre-fix tree redacted it, which is a regression, not a residual: different class,
different severity, and it sat inside the card's own negative clause (纯合成 marker
必须仍被脱敏). It is re-labelled here as **F-REV-D-01, credential-leak regression**, and
it now has rule-table rows (`cred-auth-split-*`, 7 rows including one carrying a
39-char non-marker credential rather than the marker) and oracle rows N5c/N5d/N5e.

The **assignment-path** N13 residual itself (`"password: iron steel"` →
`"password: <redacted> steel"`) stands unchanged and **accepted** by the reviewer
(RULING 3); the two must not be merged in the record.

## C2.4 The four frozen nodeids (REVIEWER RULING 1) — rewrite landed, count moved

Per RULING 1, and conditional on fixing the BLOCKER (now fixed), the reviewer's own
rewrite is applied to the copied suite:

* `test_f08_c13_multiline_loss_is_frozen_not_hidden` → renamed
  `test_f08_c13_multiline_diagnostics_survive`, loop INVERTED (`doc=17`,
  `stage=summarize`, `code=llm_global_failure`, `request_id=req-1` must now be IN the
  output), `len(out) == 34` → `== 98`, plus `len(out) < 200` / `> 90`, marker absent,
  and the two input lengths kept (112 for the 24-char reviewer marker, 109 for the
  21-char marker);
* the three `FIDELITY_CASES` parameters take the narrowed expectations;
* the stale "greedy value (r1 `_BARE_VALUE` semantics, kept - see carry C13)" and
  "Frozen as CURRENT BEHAVIOUR" comments are rewritten to the narrowed semantics;
* the reviewer's **required addition**: new `FIDELITY_CASES` rows for
  `Authorization: Bearer\n<marker>`, `…\r\n<marker>`, obs-fold `…\n  <marker>` and
  `authorization: token\n<marker>`, each asserting the marker is ABSENT.

Because rows were added, the section 6 criterion "the copied suite's only failures
are the four named nodeids" is superseded: after the rewrite the copied suite is
**86 passed / 0 failed** on the fixed tree, and `r5/counts.json` was regenerated from
the tables (`fidelity_cases` 28 → **32**). All previously published counts that moved
are restated in `handoff.json`.

## C2.5 Mutation plan: M4 added (this is the arm that was missing)

The first pass's plan could not detect that the *chosen* rule leaks. RULING 2's
family is now covered by a fourth specimen, derived from the r2 tree by a single
localized edit:

| id | specimen | tree | expected |
|---|---|---|---|
| M1 | scanner loop un-narrowed | `iso/product_mut_greedy` | assignment-path C13 family RED |
| M2 | auth join `[ \t]+` → `\s+` | `iso/product_mut_authnl` | auth line-bound is load-bearing |
| M3 | auth value = strict single token | `iso/product_mut_auth1_r2` | naive narrowing LEAKS |
| **M4** | **`_AUTH_SCHEME_SPLIT` removed from the value group** | **`iso/product_mut_authsplit`** | **the r2 fix LEAKS in the newline-split direction** |

M4 collapses byte-for-byte onto the pre-r2 narrow tree
(`observability.py` sha256 `e8abd522…`), so it is exactly "the r2 tree as if the fix
had never been written" — it is F-REV-D-01 re-opened by construction, and it is the
arm that proves the new rows are load-bearing.

## C2.6 Recorded, deliberately NOT fixed (reviewer's instruction)

* **F-REV-D-02 (MEDIUM)** — `_VALUE` is dead code in both trees; the headline
  `_BARE_VALUE` narrowing has no runtime effect. The assignment-path change is the
  scanner-loop hunk alone (M1 shows the loop is what moves E4b). **Promotion hazard:**
  a promoter who tidies the dead constant and believes the fix is intact is wrong.
  Recorded in `decision.md`; not touched here.
* **F-REV-D-03 (MEDIUM)** — the narrowing unmasks an atom-table gap:
  `token=<A> token2=<B>` leaves `<B>` in the clear (`token2`/`secret2`/`password2`/
  `api_key2` are not credential keys). Pre-existing, previously masked by the greedy
  swallow. Needs a rule-table row and a follow-up card; not fixed here.
* **F-REV-D-04 (LOW)** — a value-less `Authorization:` followed by a newline still
  takes the next token as its value. The narrowing improves it (one of two keys now
  survives) but does not close it. Open C13 sub-case.
* **F-REV-D-05 (LOW)** — `binding.json → allowed_product_edits` claimed
  `harness/tests/conftest.py` carries a one-line tree-pointing change; it is
  byte-identical to I-14-C's (`783b1774…`). Corrected in `binding.json` (documentation
  fix only, explicitly permitted by the reviewer); the file itself is untouched.
* **F-REV-D-06 (LOW)** — `residuals_confirmed` (3) vs `rule_kinds.residual` (4).
  The key is renamed `residuals_with_marker_surviving` and the full residual list is
  emitted as `residual_rows`, because a key name that under-reports an inventory is
  the same failure mode this card exists to avoid.
* **F-REV-D-07 (INFO)** — external drift: `revenue-forecast` HEAD moved under the
  attempt (other cards' carriers), so `binding.json`'s recorded HEAD is stale. Not
  this attempt's doing; noted, not "fixed".



# CORRECTION 3 (2026-09-22, appended for the r3 revision; original bytes above unchanged)

Appended, not a rewrite: every byte above this line belongs to the r2 generation and is left
exactly as it was. This section answers the three items the r2 independent review left open
(F-REV-R2-01 / F-REV-R2-02 / F-REV-R2-03) and names the lines above that it supersedes.

## C3.1 The auth newline-split branch is GENERALISED (F-REV-R2-01, the r2 BLOCKER)

The r2 branch consumed a **nine-word enumeration** of scheme words. Its coverage was exactly as
wide as the list: `Authorization: Negotiate` + newline, `AWS4-HMAC-SHA256`, `SCRAM-SHA-256`,
`Hawk`, `Bot`, `Mutual`, `vapid`, `HOBA`, or any arbitrary word still persisted the credential —
measured by the reviewer as C1-C9 of `reviewer_report_r2.md` section 2.3, and by this attempt as
its own synthetic marker surviving in the append-only event log.

The r3 branch consumes **one RFC-7235 scheme token** and a **run** of line breaks, and tries the
quoted form after the break. Landed at
`iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py`:

```
:317  _AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
:318  _AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ \t]*"
:319                        r"(?:(?:\r?\n)[ \t]*)+"
:320                        r"(?:" + _AUTH_BARE_VALUE + r"+|\"[^\"\r?\n]*\"|'[^'\r?\n]*')")
:323  the value group is _QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE,
      i.e. _QUOTED_VALUE is tried FIRST, so a quoted continuation is reached through the break
```

The nine-word enumeration is gone. `|` is kept inside the token class because the value
delimiter class used everywhere else already stops at `|`, so nothing gains a delimiter by the
widening.

## C3.2 New frozen rows (hand-computed, as section 2 above requires)

| id | kind | input | expected | len | contains |
|---|---|---|---|---|---|
| `N5f-auth-generic-scheme-marker` | narrow_must | `Authorization: Negotiate\nSYNTHETIC_AUDIT_TOKEN\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 | `doc=17` |
| `N5g-auth-generic-scheme-secret` | narrow_must | `Authorization: AWS4-HMAC-SHA256\n<39-char credential>\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 | `doc=17` |
| `N5h-auth-unknown-word-secret` | narrow_must | `Authorization: Zzz\n<39-char credential>\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 | `doc=17` |
| `N5i-auth-scram-scheme-marker` | narrow_must | `Authorization: SCRAM-SHA-256\nSYNTHETIC_AUDIT_TOKEN\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 | `doc=17` |
| `N5j-auth-blank-line-secret` | narrow_must | `Authorization: Hawk\n\n<39-char credential>` | `Authorization: <redacted>` | 25 | — |
| `N5k-auth-quoted-continuation` | narrow_must | `Authorization: Bot\n"<39-char credential>"` | `Authorization: <redacted>` | 25 | — |

`<39-char credential>` is `ghp_ZQ7ReviewerFakeCredential0123456789`, the string the r2 reviewer
measured with. `N5j` is the blank-line variant; `N5k` is the quoted continuation the reviewer's
C12 asked for.

## C3.3 The residual is REGISTERED, not hidden (required by F-REV-R2-01)

| id | kind | input | declared residual |
|---|---|---|---|
| `R3a-two-token-then-wrap` | registered_open | `Authorization: Bearer abc\n<39-char credential>` | `Authorization: <redacted>\n<39-char credential>` |
| `R3b-quoted-two-token` | registered_open | `Authorization: Bearer abc "<39-char credential>"` | `Authorization: <redacted> "<39-char credential>"` |

Both rows carry the credential in the declaration, so the oracle confirms the survival rather
than merely tolerating it. The rule table registers the same pair as kind `registered_open`, and
`credential_leaks == []` is therefore sound again: what survives is enumerated, not omitted.

## C3.4 C2.2 restated — the branch is fail-closed in BOTH directions (F-REV-R2-02)

C2.2 above states the leak direction. It is now stated in both:

* **leak direction**: after a scheme token and one or more line breaks, the next token — or a
  quoted string reached through the same break run — is redacted;
* **over-redaction direction**: the branch cannot tell a wrapped credential from a diagnostic
  key, so `Authorization: Bearer` + newline **DELETES** the following key. Measured:
  `Authorization: Bearer\ndoc=17` becomes `Authorization: <redacted>`. This is deliberate and
  fail-closed (never leak rather than never over-redact).

The cost is **registered**, not merely described: the rule table carries **9** rows of kind
`over_redaction`, each asserting the loss exactly, so a record can no longer claim
`fidelity_drift == []` while the branch deletes a diagnostic key.

## C3.5 Line 272 above is SUPERSEDED (F-REV-R2-03)

Line 272 reads: *"On the pre-fix base tree all three FAIL, and on M4 (below) all three fail
again"*. **The base-tree half is false.** Measured on `iso/product_base`:

```
N5c-auth-scheme-lf-secret      pass=False
N5d-auth-scheme-obsfold        pass=True
N5e-auth-token-key-lf-secret   pass=True
```

Only `N5c` fails on the base tree; `N5d`/`N5e` **pass** there, because the greedy swallow happens
to produce the expected string. All three fail only on **M4**, which is the arm that matters —
so the sentence is true of M4 and false of the base tree. **第 272 行已过时，以本节为准。**
