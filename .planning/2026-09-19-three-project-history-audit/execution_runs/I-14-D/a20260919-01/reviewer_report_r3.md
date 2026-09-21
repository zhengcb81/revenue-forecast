# I-14-D — INDEPENDENT REVIEWER REPORT (r3)

Card: **I-14-D** (narrow the redactor's greedy bare-value semantics; r3 generalises the
auth newline-split branch to one RFC-7235 scheme token)
Attempt: `execution_runs/I-14-D/a20260919-01`
Revision under review: **r3** — `iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py`,
sha256 `a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda`, 42839 bytes
Reviewer: **independent** — not the author of the r3 code, the r3 measurement, or the r3 record.
Posture: read-only w.r.t. the attempt. The only file this review writes into the attempt is this
report. All reviewer instruments and outputs live outside it, under
`execution_runs/_review_i14d_r3_20260922/scratch/`. No file was deleted, moved or cleaned up.
Date of review: 2026-09-22.

---

## 0. VERDICT

**`changes_required` — the r3 revision is NOT accepted.**

The generalisation F-REV-R2-01 asked for is real and is landed: the nine-word enumeration is gone,
one RFC-7235 scheme token is consumed, the break is a run, and the quoted form is tried after the
break. The r2 reviewer's own C1–C12 matrix reproduces as claimed (r3 leaks only C10), the residual
is registered on both instruments with the 39-char non-marker credential, the over-redaction family
is registered as 9 rows, the three false base-tree claims are corrected by appended corrections with
the original bytes kept, the design trade-off reproduces under my own reconstruction, the card is
still `review_pending`, and every registered hash reproduces.

**The finding is that the branch r3 added has a one-character defect that leaves a credential in the
clear, and the record asserts the opposite.** The after-break quoted alternatives are written
`\"[^\"\r?\n]*\"` and `'[^'\r?\n]*'`. Inside a character class `?` is a **literal member of the
negated set**, not the optional-`\r` metacharacter used two lines above in `_QUOTED_VALUE`
(`\"[^\"\r\n]*\"`). So a quoted credential continuation containing `?` is not matched by that
alternative, and because a leading `"` is also a delimiter for `_AUTH_BARE_VALUE`, the whole
scheme-split alternative fails and the credential survives:

```
redact_text('Authorization: Bot\n"ghp_ZQ7ReviewerFakeCredential0123456789?x"')
  -> 'Authorization: <redacted>\n"ghp_ZQ7ReviewerFakeCredential0123456789?x"'      # credential persists
```

This is unregistered — no oracle row and no rule-table row covers it — while `oracle.md` C3.4, the
source comment (observability.py:303-304) and `handoff_r3.json`
(`credential_leaks_is_sound_again: true`) all assert the branch is fail-closed for exactly this
shape. That is the same structural defect F-REV-R2-01 named: a measured instance closed, a residual
class left open, and the exit criterion offered as sound. See **F-REV-R3-01**. The cause is proven by
correcting the single character **in memory** and watching the leak close (nothing on disk was
touched).

**Scope this verdict covers.** The r3 product copy `iso/product_narrow_r3/src` at the byte-pin above;
the two harnesses at their byte-pins; the r3 generation carriers (`oracle.md`, `fix_record.md`,
`binding.json`, `review.md`, `handoff_r3.json`); the two prior verification directories; and the
recorded r3 runs `scratch/oracle_r3.json` / `scratch/rule_r3.json`. All were re-measured by me.

**Scope this verdict does NOT cover.** (a) The r2 generation's own correctness, except where r3
inherits it — I re-ran r2 only as a comparison arm. (b) The copied pytest suites and the real
worker/CLI exit: I did **not** re-run `harness/tests/test_i14c_real_exit_redaction.py`,
`harness/tests/test_i14d_single_token.py`, `run_exit_probe.py` or `run_real_cli_exit.py` (see
UNVERIFIED). (c) Promotion, `disclosure_adaptation`, accuracy or any mapping question — not
requested and not tested. (d) The r2 reviewer's RULING 1 rewrite (I did not re-litigate it).
(e) The four mutation trees M1–M3 beyond the single M4 arm I needed for the leak direction.
(f) Whether any *downstream* consumer of the redactor's output depends on the deleted diagnostic key.

---

## 1. THE NINE CLAIMS

### Claim 1 — the generalisation is real — **CONFIRMED**

Read from the bytes, not the comment:

* `observability.py:317` — `_AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*"`. Every
  RFC-7230 `tchar` is present exactly once, `-` is last so it is literal, and the class is prefixed
  with `[A-Za-z]`. (The *leading-letter* restriction is narrower than the ABNF the comment cites —
  see F-REV-R3-05 — but the class itself is as claimed.)
* `observability.py:318-320` — `_AUTH_SCHEME_SPLIT` references `_AUTH_SCHEME_TOKEN`, then `[ \t]*`,
  then `(?:(?:\r?\n)[ \t]*)+` (a **run**, not exactly one break), then
  `(?: _AUTH_BARE_VALUE + | \"[^\"\r?\n]*\" | '[^'\r?\n]*' )` — the quoted alternatives are present
  inside the split.
* The nine-word enumeration is **gone**: `"bearer|token|basic"` occurs 0 times in the r3 file; the
  full enumeration string `(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)` is present in
  the r2 file and absent from r3.
* The value group is `_QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE`.

Measurement: `rev_bytes.py` (section "nine_word_enumeration" / "scheme_token_line" /
"break_run_literal_present" / "after_break_dq_class"), and the r2→r3 `diff -u` below (1 hunk, 1 file).

### Claim 2 — the class is closed, not just the instance — **CONFIRMED** (by the claim's own test)

The r2 reviewer's C1–C12 matrix, re-implemented by me from `reviewer_report_r2.md` §2.3, run on all
four trees (`rev_probe.py`):

| tree | c-matrix leaking |
|---|---|
| `product_base` | `C12` only (pre-existing) |
| `product_narrow` (r2) | `C1 C2 C3 C4 C5 C6 C7 C8 C9 C10 C11 C12` |
| **`product_narrow_r3`** | **`C10` only** |

So the operative claim — *r3 should leak only C10* — holds. Note one imprecision in the claim as
dispatched: r2 leaked **C1–C12**, not C1–C11 (C12 also leaked on `product_base`, which the r2 report
itself records as "pre-existing"). The r3 marker forms of the same family (`Authorization: Negotiate\n`
+ `SYNTHETIC_AUDIT_TOKEN`, `Authorization: Zzz\n` + marker) are also closed, which is the card's own
negative clause.

Two residual classes sit outside this matrix; both are reported as findings, not folded in here:
the `?`-in-a-quoted-continuation leak (F-REV-R3-01) and non-letter-initial schemes (F-REV-R3-05).

### Claim 3 — the residual is registered, not hidden — **REFUTED**

The *registration* half is confirmed by measurement:

* oracle rows `R3a-two-token-then-wrap` and `R3b-quoted-two-token` are `kind: registered_open`, and
  both declarations carry the 39-char credential
  `ghp_ZQ7ReviewerFakeCredential0123456789` — R3a input `Authorization: Bearer abc\n<S39>`,
  declared residual `Authorization: <redacted>\n<S39>`; R3b the quoted two-token form.
  `registered_open_confirmed` == `registered_open` == both ids.
* the rule table's `registered_open_rows` is the same pair (`open-two-token-then-wrap`,
  `open-quoted-two-token`), and `registered_open_leaking` is that same set.

The *operative* half — **"no unregistered leak exists"**, i.e. that `credential_leaks == []` is
sound again — is **false**. `credential_leaks` is `[]` only because it is filtered to `kind:
credential` and no row covers a quoted continuation containing `?`:

```
redact_text('Authorization: Bot\n"<39-char credential>?x"')  -> credential persists
```

`rev_probe.py` row `X1-quoted-with-question`; bounded by `rev_charsweep.py` (over all printable ASCII
plus 5 control chars, the **only** characters that leave a quoted continuation unredacted on r3 are
`?`, `\n`, `\r`); cause proven by `rev_bound.py` section D. See F-REV-R3-01.

### Claim 4 — the rule table's `verdict: "negative"` is correct and not a failure — **CONFIRMED**

Read against `run_rule_table_i14d.py:278-314`:

```python
leaks        = [r["id"] for r in credentials if r["marker_survives"]]      # kind == "credential"
secret_leaks = [r["id"] for r in rows        if r["secret_survives"]]      # ALL rows
negative = ((not fidelity_ok) or bool(leaks) or bool(secret_leaks) or bool(touched))
```

So the verdict *is* computed over all rows' secret survival, and on r3 the only rows where the
credential survives are the two `registered_open` rows. Measured on the r3 tree:

```
credential_leaks        = []
credential_secret_leaks = ['open-two-token-then-wrap', 'open-quoted-two-token']
registered_open_rows    = ['open-two-token-then-wrap', 'open-quoted-two-token']   (identical)
touched_but_should_not_be = []
fidelity_ok             = True
verdict                 = "negative"          (harness rc = 3)
```

The claim's reading is accurate. **Design consequence, recorded (F-REV-R3-09, INFO):** because
`secret_leaks` spans all rows and a `registered_open` row is by construction a row whose credential
survives, this harness can no longer return `rc 0` on any tree that carries a registered residual.
The top-level `verdict` field has therefore stopped being usable as a pass/fail signal; a reader must
consult `credential_leaks` and `registered_open_rows`. The record discloses this, so it is a note,
not a defect.

### Claim 5 — the over-redaction cost is registered — **CONFIRMED**

* Rule-table kind census, read from the table source and from the run: `over_redaction` = **9** rows
  (`over-auth-scheme-then-key`, `-reqid`, `-stage`, `over-auth-token-then-keys`, `over-auth-crlf-then-key`,
  `over-auth-obsfold-then-key`, `over-proxy-auth-then-key`, `over-auth-scheme-then-marker`,
  `over-auth-generic-then-key`).
* `over_redaction_touched` is **the same 9 ids** — every row asserts the loss exactly, so the rows are
  `fidelity_ok` and the cost is a measured fact rather than an invisible one.
* `oracle.md` C3.4 states the branch is fail-closed in **both** directions and records the measured
  cost (`Authorization: Bearer\ndoc=17` → `Authorization: <redacted>`), attributing it to F-REV-R2-02.
  Verified by reading C3.4.

### Claim 6 — the three false base-tree claims are corrected, and were false — **CONFIRMED**

My re-run of the frozen oracle against `iso/product_base` (28 cases, `rev`-independent invocation of
`harness/run_i14d_oracle.py`):

```
N5c-auth-scheme-lf-secret      pass = False
N5d-auth-scheme-obsfold        pass = True
N5e-auth-token-key-lf-secret   pass = True
```

Only **N5c** fails on the base tree; N5d/N5e pass there because the greedy swallow happens to produce
the expected string. All three fail on M4 (`product_mut_authsplit`: all three `pass = False`), which
is the arm that matters. So all three original statements were false in their base-tree half:

* `oracle.md:272` still reads *"On the pre-fix base tree all three FAIL"* — original bytes kept.
* `fix_record.md:86` still reads *"All three FAIL on the base tree, on M4, and pass on the fixed tree."* — original bytes kept.
* `after/r2_summary.json → oracle.narrow_must_failed_base` still lists `N5c` **and** `N5e` (over-reports
  by one, omits `N5d`) — file not edited (mtime 2026-09-21 21:21, unchanged).

**Nothing was rewritten.** I recomputed the registered pre-correction hashes as *prefix* hashes of the
files on disk:

| carrier | before bytes | sha256 of `file[:before_bytes]` == registered before-sha? |
|---|---|---|
| `oracle.md` | 21799 | **yes** (`f188e853…`) |
| `fix_record.md` | 10352 | **yes** (`68fb5800…`) |
| `review.md` | 4938 | **yes** (`14b8628d…`) |
| `binding.json` | 10139 | no — see below |

`binding.json` is not a byte-prefix, because the append inserts `,\n  "r3_corrections": {…}` **before**
the closing brace. I reconstructed the pre-state exactly: `raw[:10136] + b"\n}\n"` is 10139 bytes and
hashes to the registered `5fd462c93197d5d7b602a03b2ba81841917bab845aa609854e4db98c10e2d9eb`.
So every byte of the r2 file is present, in order, and unchanged; only the closing brace moved.
This also disposes of the handoff's phrase "all_four_are_prefix_preserving_appends" as imprecise for
this one file (F-REV-R3-08, INFO). Mtimes corroborate that `handoff.json`, `decision.md`,
`commands.json`, `changes.diff`, `changes_r2_authsplit.diff`, `after/r2_summary.json` and
`after/final_hashes.json` were not touched by the r3 generation (all still 2026-09-21 21:13–21:23;
the r3 writes are the four carriers + `handoff_r3.json` at 2026-09-22 00:28).

### Claim 7 — the design trade-off is honestly stated — **CONFIRMED**

I rebuilt the `token-run` candidate myself from the product's own constants (not from the reproducer's
source) and measured it on the same case sets (`rev_claim7.py`; my reconstruction of the landed
pattern is byte-identical to the module's, `builder_is_faithful: true`):

| candidate | oracle failures | rule failures | reviewer matrix leaking |
|---|---|---|---|
| landed r3 | 0 | 0 | `C10` |
| **token-run** | 2 | 2 | **none** |
| r2-enumeration | 6 | 14 | `C1`–`C12` |

`token-run` closes C10, C11 and C12 — and its cost is exactly:

* **genuine over-redaction regressions (2 distinct shapes, measured on 2 instruments each):**
  `N5-auth-multiline` (oracle) / `cred-auth-multiline-swallow` (rule table) — the same input
  `Authorization: Bearer <marker>\ndoc=17\nstage=summarize`; `doc=17` is deleted
  (`doc17_deleted: true`); and `OR1 Authorization: Bearer\ndoc=17` → `Authorization: <redacted>`.
* **registration rows that would need re-registering (2):** `R3a-two-token-then-wrap` (oracle) /
  `open-two-token-then-wrap` (rule table) — the same input; they go red because the leak they declare
  is closed, which is the registration working.

So "the cost is 2 genuine regressions plus 2 registered rows" is accurate, and the four red rows are
two distinct shapes each measured twice, not four independent costs. I also confirmed the claim is
*bounded* to the tested candidate family: `mandatory-token` closes C10 but not C11 and costs
`N5-auth-multiline`/`N5j`/`R3a`; `optional-run` closes nothing. The reproducer's own disclosure that
only `r3-chosen` uses the product's split verbatim, and the rest are its reconstructions, is honest
and I confirmed the reconstruction reproduces the same numbers.

I also re-ran the reproducer as a patched copy: its output is **byte-identical** to the recorded
`r3_design_space_reprobe.json`, so that artefact is genuinely idempotent.

### Claim 8 — the carrier does not overstate — **REFUTED**

Two sentences in `handoff_r3.json` claim more than the measurements support.

**(a) `credential_leaks_is_sound_again: true`** (under `the_r2_review_items →
residual_registration`) rests on the stated reason that "what survives is enumerated, not omitted"
(that phrasing is in `oracle.md` C3.3, which the handoff echoes). It is not: the `?`-containing
quoted continuation survives and is enumerated nowhere (F-REV-R3-01).

**(b) "8 propositions, 7 negative controls, overall PASS, idempotent"** — the cited
`_verify_20260922_i14d_r3/i14d_r3_state_verification.json`. I re-ran that script as a patched copy
with its output redirected into my scratch (`scratch/verify_rerun/verify_i14d_r3_state.py`):

```
P-1 True  P-2 True  P-3 True  P-4 True  P-5 True  P-6 True  P-7 False  P-8 False
negative controls all correctly red = True
overall = FAIL        (rc 1)
```

P-7 (`handoff_predates_the_r3_artifacts`) and P-8 (`attempt_untouched`, 9 pinned hashes) are now red
because the r3 carriers were appended after the verification ran — the verification's own pins are the
*pre-correction* hashes. The PASS was a true snapshot at 2026-09-22 00:16; it is **not** reproducible
against the tree as delivered, so calling it "idempotent" and citing "overall PASS" as
`independent_evidence` for r3 overstates it. (The verification is nevertheless *useful* and its
substance holds: P-1–P-6 are exactly the propositions that matter for r3, and I reproduced P-1, P-2,
P-3, P-4, P-5 independently.) See F-REV-R3-02.

Also imprecise, but not overstated in the same way: "the value group is `_QUOTED_VALUE |
_AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE`, so the quoted form is tried first and is reached through the
break" describes the wrong constant — the quoted continuation is matched by the alternative *inside*
`_AUTH_SCHEME_SPLIT`, where the bare form is tried **first** and the quoted form second; the
top-level `_QUOTED_VALUE` cannot match a value that begins with the scheme word (F-REV-R3-06, INFO).

### Claim 9 — no verdict was pre-empted — **CONFIRMED**

* `handoff_r3.json`: `"status": "review_pending"`, `"it_states_no_verdict": true`,
  `"verdict_expressed": false`, and it says of itself "it does not say the card is accepted".
* `handoff.json` (r2 generation) still `review_pending`.
* `review.md` §r3: "No verdict is expressed. `status` is unchanged: the card remains
  `review_pending` until an independent reviewer rules."
* No record says r3 is accepted. `accepted_scoped` occurs only in `binding.json:19` (about I-14-C's
  r5 status) and in `reviewer_report_r2.md` (in the r2 reviewer's "why not accepted_scoped"
  reasoning). `binding.json`'s `verdict` key is `changes_required` (the r1 verdict).
* `task_plan.md:1401` lists `I-14-D(r3 …)` under `review_pending`; `task_plan.md:1699` — "卡仍
  `review_pending`，本卡不代其收口"; `task_plan.md:1501` records no status transitions.

---

## 2. THE TWO PRIOR VERIFICATION DIRECTORIES — CHECKED, NOT TRUSTED

Both were produced by the same party that wrote the r3 carrier, so I treated them as inputs.

**`_verify_20260922_i14d_r3/`** — sound in substance, but its PASS is a snapshot. P-1 (the recorded
runs reproduce) I re-derived independently: 28 oracle rows and 79 rule-table rows, ids in the same
order, **0 field differences**. P-2 (generalisation) I re-derived from the bytes. P-3 (residual
registered) and P-4 (9 over-redaction rows) I re-derived from the runs. P-5 (the false base-tree
claim, and the base re-run) I re-derived. P-6 asserted the two *unlanded* items at the time (that
`oracle.md` C2.2 did not state both directions, and that `binding.json` still carried the imprecise
parenthetical) — both were true then and are still true of those two exact sites, because the
corrections were appended elsewhere rather than rewritten. P-7/P-8 are red on the delivered tree
(F-REV-R3-02). The script's two self-recorded predicate errors (a transposed `+)"` and a
whitespace-sensitive substring search over hard-wrapped prose) are honestly recorded and I confirmed
both classifications: they were predicate errors, not data defects.

**`_r3_design_reprobe_20260922/`** — sound. Its output is byte-identical on re-run, its
`r3-chosen` arm uses the product's own split verbatim (`builder_is_faithful: true`,
`reproduces_the_landed_pattern: true`, `landed_pattern_difference: []`), and I independently
reproduced its `token-run` (oracle 2 / rule 2 / no leaks) and `r2-enumeration` (6 / 14 / C1–C12)
numbers. Its disclosure that the four non-chosen candidates are reconstructions is the right
disclosure. One caveat it does *not* state: the `r3-chosen` arm is measured by rebinding the module's
own pattern, so it cannot detect a defect *inside* that pattern — which is exactly where F-REV-R3-01
lives. A design-space reproduction that only varies the split group cannot see a byte error in the
split group.

---

## 3. FINDINGS

### F-REV-R3-01 — **BLOCKER: the after-break quoted alternatives exclude the literal `?`, so a quoted credential continuation containing `?` is persisted, and the record claims the branch is fail-closed**

`observability.py:320`:

```
_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ \t]*"
                      r"(?:(?:\r?\n)[ \t]*)+"
                      r"(?:" + _AUTH_BARE_VALUE + r"+|\"[^\"\r?\n]*\"|'[^'\r?\n]*')")
```

In a character class, `?` is a literal member of the negated set. The intended class is the one
`_QUOTED_VALUE` uses two lines above (`observability.py:285`,
`_QUOTED_VALUE = r"\"[^\"\r\n]*\"|'[^'\r\n]*'"`). Consequence: the quoted alternative cannot match a
value containing `?`; `_AUTH_BARE_VALUE` cannot match it either (a leading `"` is a delimiter); so the
whole `_AUTH_SCHEME_SPLIT` alternative fails and only the scheme word is redacted.

```
redact_text('Authorization: Bot\n"ghp_ZQ7ReviewerFakeCredential0123456789?x"')
  -> 'Authorization: <redacted>\n"ghp_ZQ7ReviewerFakeCredential0123456789?x"'
```

Measured:

* **Leak:** `rev_probe.py` rows `X1-quoted-with-question` (double- and single-quoted forms).
* **Bounded:** `rev_charsweep.py` — over every printable ASCII char plus `\t \r \n \x0b \x0c`, the
  only characters that leave a quoted continuation unredacted on r3 are `?`, `\n`, `\r`. On
  `product_base` essentially every character leaks, so r3 closed the family for everything except `?`.
* **Cause proven in memory, nothing on disk touched:** `rev_bound.py` section D replaces only
  `\"[^\"\r?\n]*\"` → `\"[^\"\r\n]*\"` (and the single-quoted twin) in the compiled pattern and
  re-runs: `leaks_before = ['X1-dq-question', 'X1-sq-question']`, `leaks_after = []`, with the N5k
  control staying closed. `pattern_actually_changed: true`.

**Why it is BLOCKER-class.** `oracle.md` C3.4 states the leak direction as *"after a scheme token and
one or more line breaks, the next token — or a quoted string reached through the same break run — is
redacted"*; the source comment (`observability.py:303-304`) says *"Fail CLOSED: after a scheme token
and one or more line breaks (a blank line included), the next token - or a quoted string, reached
through the same break run - is redacted"*; and `handoff_r3.json` claims
`credential_leaks_is_sound_again: true` on the ground that what survives is enumerated. All three are
false for this input, and no oracle row and no rule-table row registers it. That is exactly the
structural defect F-REV-R2-01 named: the measured instance is closed, a residual class is open, and
`credential_leaks == []` is offered as exit-criterion evidence again.

**Recorded mitigating fact, so the severity is not inflated.** This is **not** a regression relative
to the card's starting tree: `product_base` persists the same input (it leaks the family for every
character). The r2 BLOCKER had both legs — a regression relative to `product_base` *and* an
unregistered class. This finding has the second leg only.

**Cheapest correct fix.** Correct the two after-break quoted classes to `[^\"\r\n]` / `[^'\r\n]`
(one line, `observability.py:320`), and register the shape on both instruments with the non-marker
credential — or, if the owner prefers, register it explicitly as open alongside R3a/R3b. Either way
the C3.4 / source-comment "fail closed" sentence and `credential_leaks_is_sound_again` must be
restated to match the measurement.

Reproduce:
```
"$PY" -B "$S/rev_probe.py"     --src "$A/iso/product_narrow_r3/src" --label r3 --out "$S/probe_product_narrow_r3.json"
"$PY" -B "$S/rev_charsweep.py" --src "$A/iso/product_narrow_r3/src" --label r3 --out "$S/charsweep_product_narrow_r3.json"
"$PY" -B "$S/rev_bound.py"     --src "$A/iso/product_narrow_r3/src" --out "$S/bound_r3.json"
```

### F-REV-R3-02 — **MEDIUM: the carrier cites a verification whose overall verdict does not reproduce against the delivered tree**

`handoff_r3.json.who_wrote_it_and_on_what_basis.independent_evidence[0]` cites
`i14d_r3_state_verification.json` as "8 propositions, 7 negative controls, overall PASS, idempotent".
Re-running the same script (patched copy, output redirected to my scratch) gives **overall = FAIL**
with `P-7` and `P-8` red; only 6 of 8 propositions hold. The PASS was a snapshot taken before the r3
corrections were appended, and its own P-8 pins are the pre-correction hashes. "Idempotent" is
therefore false for this artefact — unlike the design-space reproduction, which I confirmed is
byte-identical on re-run. The fix is a one-line qualification in the carrier, not a code change.

Reproduce:
```
"$PY" -B "$S/verify_rerun/verify_i14d_r3_state.py"     # prints P-7/P-8 False, overall = FAIL, rc 1
"$PY" -B "$S/reprobe_rerun/r3_design_space_reprobe.py" # byte-identical to the recorded JSON
```

### F-REV-R3-03 — **LOW: the source comment's explanation of why the branch is safe is false, and contradicts the next paragraph**

`observability.py:304-306` says *"The breaks and any indentation stay OUTSIDE the match, so the
diagnostic keys on the following lines survive (the C13 half this card fixes)."* The breaks do **not**
stay outside the match. Measured match spans (`rev_claim7.py`, `match_span_test`):

```
input   Authorization: Bearer\ndoc=17
match0  'Authorization: Bearer\ndoc=17'          # the break IS inside the match
value   'Bearer\ndoc=17'                          # and inside the value group
out     'Authorization: <redacted>'               # doc=17 deleted
input   Authorization: Bearer\n  doc=17
value   'Bearer\n  doc=17'                        # the indentation too
```

Six lines further down the same comment says the opposite — *"`Authorization: Bearer` + newline
DELETES `doc=17`"* — which is the correct statement and is what the registered `over_redaction` rows
assert. `oracle.md` C3.4 records the cost correctly, so the record as a whole is not misleading; the
source comment is. This is the r2-era sentence carried over unchanged into r3 (visible as a context
line in the r2→r3 diff), and it is owed a correction alongside the dangling-reference fix the handoff
already admits.

Reproduce: `"$PY" -B "$S/rev_claim7.py"` (section `match_span_test`).

### F-REV-R3-04 — **LOW: the scheme token class requires a leading letter, which is narrower than the ABNF the comment cites, and is a persistence regression against `product_base` for non-letter-initial schemes**

The comment justifies `[A-Za-z]` with *"`scheme = 1*<any CHAR except CTLs or separators>`, which
always begins with a letter"*. That production is RFC 7230's `token` (`1*tchar`), and RFC 7235 defines
`auth-scheme = token`; `tchar` includes DIGIT and `! # $ % & ' * + - . ^ _ \` | ~`, so the production
does **not** require a leading letter. Measured (`rev_bytes.py`, `non_letter_initial_scheme`):

```
Authorization: 2foo\n<39-char credential>  -> credential persists   (base: redacted)
Authorization: !foo\n<39-char credential>  -> credential persists   (base: redacted)
Authorization: afoo\n<39-char credential>  -> Authorization: <redacted>
```

My 85,800-input differential fuzz (`rev_regression_fuzz.py`) found 12,096 inputs that leak on r3 but
not on base; after removing the assignment-path N13 residual (reviewer-accepted, RULING 3) and the
registered two-token-then-wrap shape, the auth-path remainder is **1,764 inputs, all of them
non-letter-initial schemes** (`rev_reg_auth.py`). r3 leaks **nothing** that r2 did not
(`r3_regressions_vs_r2_count = 0`).

**Mitigating, and why this is LOW and not blocking:** the r2 reviewer's own remedy prescribed this
exact class ("replace the enumerated group with `[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*`"), and no
registered auth scheme begins with a non-letter. So this is a residual scope note plus an inaccurate
ABNF justification, not a defect the author introduced.

Reproduce: `"$PY" -B "$S/rev_regression_fuzz.py" --run` then `"$PY" -B "$S/rev_reg_auth.py"`.

### F-REV-R3-05 — **LOW: a value whose first character after the break is a value delimiter is not redacted (bounded, non-regressive)**

`Authorization: Bot\n,<secret>`, `\n;<secret>`, `\n&<secret>`, `\n|<secret>`, `\n"<secret>`,
`\n'<secret>` all leave the credential in the clear (`rev_bound.py` section B). This follows from the
declared value-delimiter class — such a run is not a "token" — and `product_base` behaves the same
way, so it is not a regression and not a contradiction of the comment. Recorded for completeness and
for whoever writes the next row set.

### F-REV-R3-06 — **INFO: the "quoted form is tried first" mechanism sentence describes the wrong constant**

`handoff_r3.json.what_changed.product_copy.lines["323"]` and `oracle.md` C3.1 both say the value
group `_QUOTED_VALUE | _AUTH_SCHEME_SPLIT | _AUTH_BARE_VALUE` means "the quoted form is tried first
and is reached through the break". The quoted continuation is matched by the alternative *inside*
`_AUTH_SCHEME_SPLIT`, where the order is bare → double-quoted → single-quoted; the top-level
`_QUOTED_VALUE` cannot match a value that begins with the scheme word. The behaviour claim (a quoted
continuation is redacted) is true for `?`-free values and false otherwise — F-REV-R3-01.

### F-REV-R3-07 — **INFO: `both_marker_and_non_marker` promises two things; the registered-open rows deliver one**

`handoff_r3.json.the_r2_review_items.residual_registration.both_marker_and_non_marker` explains only
the 39-char credential. Measured: `open-two-token-then-wrap` and `open-quoted-two-token` each contain
`ghp_ZQ7ReviewerFakeCredential0123456789` and **neither** contains `SYNTHETIC_AUDIT_TOKEN`
(`rev_bytes.py`, `registered_open_rows_carry_marker`). The r2 remedy asked for rows "using both the
marker and a non-marker credential"; for F-REV-R2-01's *main* family that is satisfied (there are
marker rows and non-marker rows), but for the *residual* specifically only the non-marker credential
is registered. Since the shape is literal-independent and the non-marker credential is the stronger
instrument, the substance is met; the key name over-promises.

### F-REV-R3-08 — **INFO: the r3 source delta has no registered diff and no invertibility test, and `binding.json`'s append is not literally prefix-preserving**

* r2 registered `changes_r2_authsplit.diff` (1786 B) and an exact inverse
  (`reverse_authsplit` → the pre-r2 tree byte-for-byte). The r3 delta has no diff artefact and no
  reverse op: `find . -name "*.diff"` returns only `changes.diff` and `changes_r2_authsplit.diff`.
  I produced the r3 delta myself (`diff -u` r2 → r3 `observability.py`: **1 hunk, 1 file**), so the
  change is small and reviewable, but the r3 generation's reproducibility is weaker than r2's on this
  axis, and `after/` contains no r3 outputs at all.
* `generation_carriers.all_four_are_prefix_preserving_appends: true` is imprecise for `binding.json`:
  the append is an insertion before the closing brace, so the pre-state is not a byte-prefix. I
  reconstructed the pre-state exactly (`raw[:10136] + b"\n}\n"` = 10139 B = `5fd462c9…`), so no byte
  was rewritten. The handoff's separate claim `all_other_keys_identical_and_in_order: true` is
  **CONFIRMED**.
* `after/final_hashes.json` still registers the r2-generation hashes for `oracle.md`, `fix_record.md`
  and `binding.json` (21799/10352/10139 B) and has no `review.md` entry, so a verifier who trusts that
  file will see three mismatches. The handoff discloses this ("deliberately NOT edited") and I agree
  with the reason; recorded so the next reader is not surprised.

### F-REV-R3-09 — **INFO: the rule-table harness can no longer return `rc 0` while a registered residual exists**

Follows from Claim 4's verified reading: `secret_leaks` spans all rows, so a `registered_open` row
whose credential survives pins `verdict` to `"negative"` and the process to `rc 3` on every tree that
carries one. The r3 run is `rc 3`, as is the base tree's and M4's. The record discloses and explains
this; the practical consequence is that the harness's top-level verdict is no longer a pass signal and
any downstream automation keying on `rc 0` will now read "negative" for a *correct* tree.

### F-REV-R3-10 — **INFO: the byte-pin table does not cover the r3 generation's own carriers**

`handoff_r3.json` registers hashes for the product copy, the three harnesses and the two recorded
runs, and `self_reference_note` says it does not register its own hash. There is no single byte-pin
file for the r3 generation (the r2 generation had `after/final_hashes.json`). I recomputed all 21
registered values anyway — 20 attempt-internal plus the production anchor
`scripts/model_registry.py = 9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f /
26446 B`, unchanged — and **all 21 reproduce, 0 mismatches**.

---

## 4. UNVERIFIED

1. **The copied pytest suite and the new suite were not re-run.**
   `harness/tests/test_i14c_real_exit_redaction.py`, `harness/tests/test_i14d_single_token.py`,
   `harness/run_exit_probe.py` and `harness/run_real_cli_exit.py` were not executed by me. The r2
   review ran them (86 passed / 0 failed; 25 passed) and r3 added no rows to either file, so their r2
   numbers should still hold — but I did not confirm that, and in particular I did not check whether
   either suite contains a row that would have caught F-REV-R3-01 (I read the two tables' row sets in
   the harnesses, which do not).
2. **The real worker / CLI exit was not exercised.** No `worker.py` → `redact_and_truncate` run and no
   E5a/E5b/E5c CLI run. So F-REV-R3-01 is measured at the helper level only; I did not demonstrate the
   `?`-containing credential reaching a persisted event log end-to-end.
3. **M1/M2/M3 were not re-run.** I used only M4 (`product_mut_authsplit`) as the leak-direction arm.
   The r2 review's M1–M3 results are carried, not re-measured.
4. **The r3 generation has no diff artefact, so I could not verify its invertibility** the way the r2
   review verified r2's. I substituted a `diff -u` of the two trees (1 hunk, 1 file) and confirmed the
   r2 tree differs from the r3 tree in exactly one file.
5. **Performance / ReDoS linearity was not re-timed**, and the F07 deadline assertion was not
   re-measured. The r3 change adds a nested quantifier over a bounded character class
   (`(?:(?:\r?\n)[ \t]*)+` after a token) — I did not measure its worst case.
6. **The four mutation trees' `binding.json`/`after/` bookkeeping for the r3 generation** was not
   audited: `binding.json`'s `allowed_product_edits` still describes the r2 edits and does not mention
   `iso/product_narrow_r3` or the r3 harness changes, which I noted but did not treat as a finding
   because `r3_corrections` is scoped to F-REV-R2-04 only.
7. **`scratch/` was not audited.** The r3 iteration's ~30 scratch scripts are stale by the reproducer's
   own account (they unpack `oracle.CASES` as a 6-tuple); I did not run them and did not check whether
   any of them registers the `?` shape.
8. **The downstream consequence of the over-redaction family** (whether any consumer depends on the
   deleted diagnostic key) was not investigated.

---

## 5. HOW TO REPRODUCE

```
A = <attempt> = .../execution_runs/I-14-D/a20260919-01
S = .../execution_runs/_review_i14d_r3_20260922/scratch
PY = "$A/iso/venv/Scripts/python.exe"          # python 3.13.9, PyYAML 6.0.3
```
Every command below ran with `PYTHONDONTWRITEBYTECODE=1` and `-B`. Nothing was written into the
attempt except `reviewer_report_r3.md`.

```bash
# 0. byte pins: 21 registered hashes recomputed from the bytes -> 0 mismatches
"$PY" -B "$S/rev_hashcheck.py"
sha256sum "C:/Users/郑曾波/Projects/revenue-forecast/scripts/model_registry.py"

# 1. append fidelity of the four generation carriers (prefix hashes + binding.json reconstruction)
"$PY" -B "$S/rev_append_check.py"

# 2. the two frozen harnesses, four trees each
for t in product_narrow_r3 product_narrow product_base product_mut_authsplit; do
  "$PY" -B "$A/harness/run_i14d_oracle.py"     --src "$A/iso/$t/src" --label "$t" --out "$S/oracle_$t.json"
  "$PY" -B "$A/harness/run_rule_table_i14d.py" --src "$A/iso/$t/src" --label "$t" --out "$S/rule_$t.json"
done
# rc: oracle 0 / 3 / 3 / 3 ; rule table 3 / 3 / 3 / 3

# 3. my own C1-C12 matrix + extra byte probes
for t in product_narrow_r3 product_narrow product_base product_mut_authsplit; do
  "$PY" -B "$S/rev_probe.py" --src "$A/iso/$t/src" --label "$t" --out "$S/probe_$t.json"
done

# 4. bound and prove the cause of F-REV-R3-01 (in-memory only)
"$PY" -B "$S/rev_charsweep.py" --src "$A/iso/product_narrow_r3/src" --label r3   --out "$S/charsweep_product_narrow_r3.json"
"$PY" -B "$S/rev_charsweep.py" --src "$A/iso/product_base/src"      --label base --out "$S/charsweep_product_base.json"
"$PY" -B "$S/rev_bound.py"     --src "$A/iso/product_narrow_r3/src" --out "$S/bound_r3.json"

# 5. recorded runs reproduce + match-span test + the token-run candidate (Claim 7)
"$PY" -B "$S/rev_claim7.py"

# 6. byte-level and registration census
"$PY" -B "$S/rev_bytes.py"

# 7. differential regression fuzz, 85,800 inputs, three trees in separate processes
"$PY" -B "$S/rev_regression_fuzz.py" --run
"$PY" -B "$S/rev_reg_auth.py"

# 8. the two prior verification artefacts, re-run as patched copies
"$PY" -B "$S/verify_rerun/verify_i14d_r3_state.py"        # P-7/P-8 red, overall FAIL, rc 1
"$PY" -B "$S/reprobe_rerun/r3_design_space_reprobe.py"    # byte-identical to the recorded JSON

# 9. responsiveness self-check (every predicate fed a mutated input)
"$PY" -B "$S/rev_responsive.py"

# 10. the r2 -> r3 source delta (no diff artefact is registered for r3)
diff -u "$A/iso/product_narrow/src/company_wiki/source_catalog/observability.py" \
        "$A/iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py"     # 1 hunk
```

Reviewer artefacts written (all outside the attempt):
`$S/{hashcheck,append_fidelity,oracle_*,rule_*,probe_*,charsweep_*,bound_r3,claim7_measure,
bytes_and_registration,regression_fuzz,regression_authpath,responsiveness}.json` plus the scripts
named above and the two patched verification copies.

---

## 6. RESPONSIVENESS OF MY OWN CHECKS

Ten of my predicates were called twice — once on the real data and once on a mutated input held in
memory — and recorded in `$S/responsiveness.json`; **all ten go red on the mutation**. The mutations:

| predicate | real | mutation that turned it red |
|---|---|---|
| `sha256_of_oracle_md` | holds | one byte flipped in `oracle.md` |
| `prefix_preserved_fix_record_md` | holds | one byte flipped at offset 100 of `fix_record.md` |
| `c_matrix_only_C10_leaks` | holds | **the r2 tree** (leaks C1–C12) |
| `no_question_mark_leak` | holds | `["?"]` fed directly |
| `registration_sound_on_r3` | holds | `credential_leaks = ["synthetic-unregistered-leak"]` |
| `registration_sound_pred_vs_base_tree` | holds | **the base-tree rule run** |
| `recorded_oracle_reproduces` | holds | one row's `out` set to `"MUTATED"` |
| `only_N5c_fails_on_base` | holds | N5d forced to `pass = False` |
| `rule_verdict_is_negative` | holds | `verdict` set to `"pass"` |
| `binding_json_pure_insertion` | holds | one byte flipped inside the pre-existing region |

**Two of my first controls were wrong and I classified them rather than believing the red.** Both
reported "not responsive" on the first run:

* `no_question_mark_leak` was fed the **base tree's** char sweep, which also leaks `?`, so the
  predicate could not move. The predicate's domain is "is `?` in the leaking set"; the correct
  minimal mutation is `["?"]`. Predicate error, not a dead check.
* `binding_json_pure_insertion` was fed a mutation **inside the appended block**, which the
  reconstruction discards by construction. The predicate asserts the *pre-existing* content is
  intact, so the control must mutate before the insertion point (byte 10137). Predicate error again.

**Two further responsiveness facts worth recording.** (a) The oracle's `registered_open` rows are
tested by `residual_is_declared` (`out == residual`), not by `exact_ok` (which the harness forces to
`True` for those rows); that predicate *is* load-bearing, and the token-run candidate in Claim 7
turned `R3a-two-token-then-wrap` red through it — so it can fail. (b) The prior verification
script's own P-7/P-8 are responsive in the opposite direction from what its author intended: they are
red *now*, which is what proves the verification was read-only when it ran.

---

## 7. ADJUDICATION

**Does r3 close F-REV-R2-01? Almost — it closes the class the r2 reviewer named and leaves a
one-character hole inside the branch it added.**

* **Closed, and verified by me:** the nine-word enumeration is gone; the pre-break token is one
  RFC-7235 scheme token; the break is a run; C1–C12 leaks only C10 on r3 where r2 leaked C1–C12; the
  r3 marker forms are closed; the two-token-then-wrap residual is registered on both instruments with
  a 39-char non-marker credential and confirmed to leak exactly what it declares; 9 over-redaction
  rows assert the cost exactly; the three false base-tree claims are corrected by append with the
  original bytes kept and reconstructible; the design trade-off reproduces under my own
  reconstruction and its cost is correctly classified; the card is still `review_pending` with no
  verdict expressed; and all 21 registered hashes reproduce.
* **Open (F-REV-R3-01):** a quoted credential continuation containing `?` is persisted, because the
  after-break quoted classes carry a literal `?` where `_QUOTED_VALUE` correctly has `\r\n`. The leak
  is bounded to exactly that character, is proven by a one-character in-memory correction, and is
  **not** registered anywhere — while `oracle.md` C3.4, the source comment and
  `handoff_r3.json.credential_leaks_is_sound_again` all assert the branch is fail-closed for that
  shape. This is not a regression against `product_base`.
* **Also requiring change (documentation, non-blocking):** the carrier's citation of the state
  verification as "overall PASS, idempotent" (F-REV-R3-02); the false "breaks stay OUTSIDE the match"
  sentence in the source comment (F-REV-R3-03); and the imprecisions at F-REV-R3-06/-07/-08.
* **Why not `accepted_scoped`:** the r2 review made `credential_leaks == []` conditional on the
  residual being *enumerated*, and r3's own record now offers that field as sound evidence for a
  class in which one shape still leaks unenumerated. Accepting would repeat the r2 defect at one
  character's scale. If the owner prefers to accept it deliberately, the honest form is an explicit
  registration of the `?` shape alongside R3a/R3b plus a restatement of the fail-closed sentence —
  not an unqualified `credential_leaks_is_sound_again: true`.
* **Why not `cannot_adjudicate`:** every claim was measurable with the attempt's own interpreter and
  its own harnesses; nothing I needed was missing.

**Cheapest path to green.** (1) `observability.py:320`: `[^\"\r?\n]` → `[^\"\r\n]` and
`[^'\r?\n]` → `[^'\r\n]`. (2) Add one oracle row and one rule-table row for the quoted continuation
containing `?`, carrying the 39-char non-marker credential. (3) Correct `oracle.md` C3.4 / the source
comment sentence about the quoted form, and the "breaks stay OUTSIDE the match" sentence. (4) Qualify
the carrier's citation of the state verification. (5) Re-run the oracle, the rule table, the probe
and the two suites. (6) Optional but cheap: correct the comment's ABNF justification for the leading
letter and register the r3 diff.

**What this review grants:** a byte-pinned, independently re-derived confirmation that the r3
generalisation is real, that the r2 reviewer's own C1–C12 matrix now leaks only C10, that the
residual and the over-redaction cost are registered with the right credentials and the right row
counts, that the three false base-tree claims were indeed false and are corrected without rewriting
a byte, that the design trade-off reproduces under an independent reconstruction, and that the card
was not pre-empted. **What it does not grant:** acceptance, or the soundness of
`credential_leaks == []` as evidence for the class, until F-REV-R3-01 is closed or registered.

---

*Reviewer's note on process: this review wrote exactly one file into the attempt
(`reviewer_report_r3.md`) and deleted, moved or cleaned up nothing. All instruments and outputs live
under `execution_runs/_review_i14d_r3_20260922/`. The two in-memory pattern substitutions used to
prove F-REV-R3-01 and to measure Claim 7 were rebound on the imported module object and restored;
no source file on disk was edited.*
