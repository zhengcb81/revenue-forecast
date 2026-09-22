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


# CORRECTION 4 (2026-09-22, appended for the r4 revision; original bytes above unchanged)

Appended, not a rewrite. This answers the two code findings of the r3 independent review:
**F-REV-R3-01** (BLOCKER) and **F-REV-R3-04** (LOW).

## C4.1 F-REV-R3-01 — the two `?` characters are gone (BLOCKER)

The r3 after-break quoted alternatives carried the optional-CR form **inside a character
class**, where `?` is a literal member of the negated set rather than a quantifier:

```
r3, line 320   r"(?:" + _AUTH_BARE_VALUE + r"+|\"[^\"\r?\n]*\"|'[^'\r?\n]*')"
                                          ^^^^^^^^^^^^        ^^^^^^^^^^
r4, line 320   r"(?:" + _AUTH_BARE_VALUE + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')"
```

Line 319's `\r?\n` is **correct and untouched**: it sits in `(?:\r?\n)`, outside any
character class, where `?` really is the quantifier. Exactly two bytes changed.

## C4.2 F-REV-R3-04 — the scheme token class is now the full RFC 7230 tchar

r3 used `[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*`. The comment justified the leading letter with
"`scheme = 1*<any CHAR except CTLs or separators>`, which always begins with a letter" — but
that production is RFC 7230's `token` (`1*tchar`), and `tchar` includes DIGIT and the specials,
so it does **not** require a leading letter. The r3 review measured the consequence: a
non-letter-initial scheme leaked where the pre-fix base tree redacted.

r4 uses the full tchar class:

```
r3, line 317   _AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
r4, line 317   _AUTH_SCHEME_TOKEN = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
```

This is not a departure from the r2 remedy: that remedy asked for "an HTTP `token`", and the
full tchar class is what an HTTP token is.

## C4.3 New frozen rows (hand-computed before the run, as section 2 requires)

| id | kind | input | expected | len |
|---|---|---|---|---|
| `N5l-auth-dq-question-mark` | narrow_must | `Authorization: Bot\n"<39-char credential>?x"` | `Authorization: <redacted>` | 25 |
| `N5m-auth-sq-question-mark` | narrow_must | `Authorization: Bot\n'<39-char credential>?x'` | `Authorization: <redacted>` | 25 |
| `N5n-auth-nonletter-scheme-marker` | narrow_must | `Authorization: 2foo\nSYNTHETIC_AUDIT_TOKEN\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |
| `N5o-auth-nonletter-scheme-secret` | narrow_must | `Authorization: !foo\n<39-char credential>\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |

## C4.4 The r4 harness is a NEW FILE, and the r3 one is untouched

r4's rows live in `harness/run_i14d_oracle_r4.py` and `harness/run_rule_table_i14d_r4.py`.
The r3 harnesses (`run_i14d_oracle.py` `f7c94c60…`, `run_rule_table_i14d.py` `01a3187e…`) are
**byte-identical to what the r3 carrier pins**.

Why this matters: adding rows to the r3 files in place would invalidate both pins AND silently
change what "reproducing the r3 run" means — the r3 tree would then fail rows that did not exist
when it was measured. (The r2 -> r3 step extended in place, so the r2 generation's reproduction
basis is already gone; that is registered rather than repeated.)

## C4.5 Measured result

`iso/product_narrow_r4/src/.../observability.py` = 42829 B, sha256
`15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1`.
The tree differs from r3 in **exactly four byte regions**; inverting those regions reproduces r3
byte for byte, line endings included (CR 897 in both).

```
oracle, 32 cases      verdict pass       narrow_must_failed []   keep_must_failed []
rule table, 83 rows   credential_leaks []   touched_but_should_not_be []   fidelity_ok true
```

Both fixes measured separately: `fix_A_only` closes the `?` leak and leaves the non-letter
family leaking; `fix_A_and_B` leaves only the registered `C10` residual. **Neither changes any
pre-existing row and neither changes the over-redaction family.**


# CORRECTION 5 (2026-09-22, appended for the r5 revision; original bytes above unchanged)

Appended, not a rewrite. This answers the four findings of the r3... correction: the r4
independent review. Three are fixed here; one is corrected in place in this section.

## C5.1 F-REV-R4-05 — the pre-break token is now the VALUE-token class

r4 restricted the pre-break token to the RFC 7230 tchar set. A token containing a **non-tchar
character** is still a token, so `Authorization: Bo?t` + newline + credential persisted the
credential, where the pre-fix base tree redacted it — 31 unregistered, base-regressive shapes.

```
r4, line 317   _AUTH_SCHEME_TOKEN = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
r5, line 317   _AUTH_PREBREAK_TOKEN = r"[^\s,;&\"'|]+"
```

The constant is **renamed**: after this change it is not an RFC scheme token, and a name that
outlives its meaning is how the previous comment block went wrong.

**Priced before it was taken** (`_r5_measure_20260922/measure_r5.py`): widening to the value
token closes the whole family at **zero cost** — oracle 0 failures, rule table 0 failures, and
the over-redaction family **unchanged** (`Authorization: Bearer` + newline still deletes
`doc=17`; `Authorization: 2024-01-01` + newline is redacted in both).

## C5.2 New frozen rows (hand-derived before the run)

For `Authorization: <token>` + newline + `<credential>`, the key group consumes
`Authorization: `, the split consumes the token plus the break run, and the tail consumes the
credential, so the whole match becomes `<redacted>`. Where a `doc=17` line follows, the break
before it is **not** part of the match, so `doc=17` survives.

| id | kind | input | expected | len |
|---|---|---|---|---|
| `N5p-auth-nontchar-question-marker` | narrow_must | `Authorization: Bo?t\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |
| `N5q-auth-nontchar-slash-secret` | narrow_must | `Authorization: Bo/t\n<39-char credential>\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |
| `N5r-auth-nontchar-colon-marker` | narrow_must | `Authorization: Bo:t\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |
| `N5s-auth-nontchar-equals-marker` | narrow_must | `Authorization: Bo=t\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |

## C5.3 **C4.5 ABOVE IS SUPERSEDED — it claimed more than its measurement supports** (F-REV-R4-06)

C4.5 says: *"Both fixes measured separately: ... `fix_A_and_B` leaves only the registered `C10`
residual."*

**That is false as written.** It is true **only of the 19-probe set that section reports**, and
the sentence does not say so. The r4 reviewer measured 31 further shapes of the F-REV-R4-05
family that also persisted a credential. **第 C4.5 节该句已过时，以本节为准。**

The corrected form, with its domain attached:

> On the 19 probes reported in C4.5, `fix_A_and_B` leaves only the registered `C10` residual.
> It is **not** a statement about the family in general; the general statement is now measured
> in C5.6 below, on a 36-row oracle and an 87-row rule table.

**This is `F-REV-R3-02` recurring one generation later.** The lesson, recorded because it has
now cost two generations: **a conclusion sentence must carry its measurement set inside the
sentence.** An unqualified negative claim is to be treated as unverified.

## C5.4 F-REV-R4-01 — the source comment now says what the code does

The comment block was byte-identical to r3 and still asserted *"`scheme = 1*<any CHAR except
CTLs or separators>`, which always begins with a letter"* — a claim the r3 review had already
falsified — and it contradicted r4:317, which had widened the class. It also ended by pointing
at `r3_fix_record.md`, a file that does not exist.

r5 rewrites the block: it names the three widenings and the finding behind each, states that no
RFC scheme production is claimed any more, corrects the "breaks stay OUTSIDE the match" claim
(they are consumed; the indentation and the following lines are not), and replaces the dangling
reference with a pointer to `_r3_design_reprobe_20260922/` — while saying explicitly that
`r3_fix_record.md` was never written and is **not** substituted for.

## C5.5 F-REV-R4-02 — the r4 measurement record contradicts itself: registered, not edited

`_r4_measure_20260922/measure_r4.py`'s docstring and `r4_measurement.json`'s key
`fix_b_measured_but_not_applied` say fix B is not in the tree; the same file's `main()` says the
opposite. **The r4 measurement record is NOT edited here**: its hashes are pinned by the r4
carrier, and rewriting them would erase the generation boundary. The correction is registered
here and in the remediation register; a corrected restatement lives in `_r5_measure_20260922/`.

## C5.6 The r5 measurement

`iso/product_narrow_r5/src/.../observability.py` = 43362 B, sha256
`ca13fb81aa2a1234ba760f49576a6409bbd3b1397f921f2e73311f90a263fc45`. It differs from r4 in the
comment block and two code lines; **inverting those regions reproduces r4 byte for byte** and
the file stays uniformly CRLF (CR 904 = LF 904).

```
oracle, 36 cases      verdict pass       narrow_must_failed []   keep_must_failed []
rule table, 87 rows   credential_leaks []   touched_but_should_not_be []   fidelity_ok true
```

**Domain of that statement**: the 36 frozen oracle cases and the 87 rule-table rows in
`harness/run_i14d_oracle_r5.py` and `harness/run_rule_table_i14d_r5.py`. It is **not** a claim
about all inputs. The F-REV-R4-05 family is closed **on the four shapes registered in C5.2**;
the registered `C10` residual remains by design.


# CORRECTION 6 (2026-09-22, appended for the r6 revision; original bytes above unchanged)

Appended, not a rewrite. This answers the two MEDIUM findings of the r5 independent review.

## C6.1 F-REV-R5-01 — the pre-break token is now ANY NON-WHITESPACE RUN

r5's class was a **swap, not a widening**. The r5 review swept every printable character at the
pre-break position and measured `r4 \ r5 = ['&', "'", '|']`: `Authorization: Bo&t` + newline +
the card's marker **redacted on r4 and persisted on r5**. The hole had been moved, not removed.

```
r5, line 324   _AUTH_PREBREAK_TOKEN = r"[^\s,;&\"'|]+"
r6, line 329   _AUTH_PREBREAK_TOKEN = r"[^\s]+"
```

**Judged by BOTH differences, which is the criterion r5's failure produced.** Every widening
before r6 was checked by "does the character that was pointed at now pass" — only one of the two
differences that matter. Swept over every printable ASCII at this position:

| candidate | oracle failures | rule-table failures | single characters still leaking |
|---|---|---|---|
| r5's value-token class | 0 | 0 | `' '`, `'"'`, `&`, `'`, `,`, `;`, `\|` |
| r4's tchar class | 4 | 4 | 16 characters |
| **`[^\s]+`** | **0** | **0** | **`' '` only** |

`[^\s]+` closes **every character r4 or r5 closed and every character either of them leaked,
except the space** — and a space here means the value is a multi-token run, which is the
registered OPEN shape, not a token-class question.

Per-character, on `Authorization: Bo<c>t` + newline + the marker:

```
r4   ? LEAK   & ok    ' ok    | ok    / LEAK   : LEAK   @ LEAK
r5   ? ok     & LEAK  ' LEAK  | LEAK  / ok     : ok     @ ok
r6   ? ok     & ok    ' ok    | ok    / ok     : ok     @ ok
```

## C6.2 New frozen rows (hand-derived before the run)

| id | kind | input | expected | len |
|---|---|---|---|---|
| `N5t-auth-ampersand-marker` | narrow_must | `Authorization: Bo&t\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |
| `N5u-auth-apostrophe-marker` | narrow_must | `Authorization: Bo't\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |
| `N5v-auth-pipe-marker` | narrow_must | `Authorization: Bo\|t\nSYNTHETIC_AUDIT_TOKEN` | `Authorization: <redacted>` | 25 |
| `N5w-auth-ampersand-secret` | narrow_must | `Authorization: Bo&t\n<39-char credential>\ndoc=17` | `Authorization: <redacted>\ndoc=17` | 32 |

## C6.3 **C5.1 ABOVE IS SUPERSEDED — it claimed more than its measurement supports** (F-REV-R5-02)

C5.1 says the widening "**closes the whole family** at **zero cost**".

**That is false as written.** It is priced by `measure_r5.py`'s **19 probes, of which 4 are
members of that family**, against a family the r5 reviewer measured at **31 base-regressive
shapes** — and the sweep in C6.1 shows the r5 class still leaked seven characters. **第 C5.1 节
该句已过时，以本节为准。**

The corrected form, with its domain attached:

> On the 19 probes reported in C5.1, the r5 class closed the shapes those probes contain. It did
> **not** close the family: on a full printable sweep at that position, seven single characters
> still let the credential through, and three of them (`&`, `'`, `|`) had been closed by r4.

**This is the third generation of the same species**: r3's carrier cited a verification that no
longer reproduced; r4's record turned a 19-probe result into a general claim; r5's record turned
a 19-probe result, four of them family members, into "closes the whole family" — **written one
paragraph above C5.3, which declares the structurally identical C4.5 sentence false.**

**A rule that lives only in prose has now been falsified three times.** The response is a
mechanism, not another sentence: **any claim of the form only / all / none / whole family / zero
cost must carry a parseable domain field on the same line, and the script that generates a
carrier must assert that the field exists.** Registered as REM-78.

## C6.4 The r6 measurement, with its domain

`iso/product_narrow_r6/src/.../observability.py` = 43746 B, sha256
`2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464`. It differs from r5 in the
class line and the comment block; **inverting those regions reproduces r5 byte for byte** and the
file stays uniformly CRLF (CR 909 = LF 909).

```
oracle, 40 cases      verdict pass       narrow_must_failed []   keep_must_failed []
rule table, 91 rows   credential_leaks []   touched_but_should_not_be []   fidelity_ok true
```

**Domain**: the 40 frozen oracle cases and the 91 rule-table rows in
`harness/run_i14d_oracle_r6.py` and `harness/run_rule_table_i14d_r6.py`, **plus** the printable
sweep in C6.1. It is **not** a claim about all inputs: the registered `C10` residual (a
multi-token value that then wraps) remains by design, and the space is the character that
separates it from the rest.

## C6.5 Generation isolation

r6 has its **own** harness files; the r3, r4 and r5 harnesses are byte-identical to their pins.
