# I-14-D — INDEPENDENT REVIEW

Status: **revision r2 submitted, RE-REVIEW REQUIRED.** The implementer does not write an
acceptance verdict, and the r1 verdict (`changes_required`) is not inherited.

## Verdict history

| round | reviewer verdict | artifact |
|---|---|---|
| r1 | **`changes_required`** — BLOCKER F-REV-D-01 (credential-persistence regression on the auth path), 5 further findings, 3 rulings | `reviewer_report.md`, sha256 `499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b`, 37659 B (recomputed by this attempt; matches the carrier's pin) |
| r2 | *pending* | this attempt after the fix |

The implementer's claims live in `oracle.md` (frozen, with CORRECTION 1 and
CORRECTION 2 appended), `decision.md` (D1-r2), `fix_record.md` (the point-by-point
answer to the BLOCKER), `commands.json` (raw rcs) and `handoff.json`.

## What changed since the r1 review (round 2)

1. **F-REV-D-01 fixed** with the reviewer's own RULING 2 mechanism
   (`_AUTH_SCHEME_SPLIT`, scheme-aware, fail closed). Both halves of the card's exit
   clause now hold on the same input at the real worker exit:
   `"Authorization: Bearer\n<secret>\ndoc=17"` persists as
   `"Authorization: <redacted>\ndoc=17"`. See `fix_record.md` §2–§3.
2. **New coverage in the leak direction**, which is what the r1 criterion was blind to:
   oracle N5c/N5d/N5e; rule table `cred-auth-split-*` ×7 (including a row carrying a
   39-char **non-marker** credential); copied-suite `FIDELITY_CASES` +4 auth
   newline-split rows; a new end-to-end case in the implementer's suite; and a fourth
   mutation **M4** whose `observability.py` hash is byte-identical to the pre-fix tree,
   i.e. the leak re-opened by construction — detected by all four instruments.
3. **RULING 1 rewrite landed** — 1 renamed nodeid (loop inverted, `34 → 98`), 3 changed
   `FIDELITY_CASES` expectations, 4 required new auth rows, 2 stale comments rewritten.
   The copied suite is therefore **no longer byte-identical to I-14-C's**
   (`672b88de…` is the restore point). This is the one separation-of-duties change in
   the attempt: see the disclosure in `fix_record.md` §6 and `binding.json`.
4. **Counts moved and were regenerated mechanically**: rule table 48 → **55**, oracle
   17 → **20**, `FIDELITY_CASES` 28 → **32**, total nodeids 103 → **111**
   (`r5/counts.json`, `after/counts.json`).
5. **N13's auth-path note re-labelled** from "declared residual" to the
   F-REV-D-01 credential-leak regression (`oracle.md` CORRECTION 2 §C2.3). The
   assignment-path residual keeps its accepted-as-declared status (RULING 3).
6. **Recorded, deliberately NOT fixed**: F-REV-D-02 (`_VALUE` dead code ⇒ promotion
   hazard; the assignment-path mechanism is the scanner loop alone), F-REV-D-03
   (`token2`/`secret2` atom-table gap now observable), F-REV-D-04 (value-less
   `Authorization:` + newline), F-REV-D-06 (residual-key reporting — clarified),
   F-REV-D-07 (external HEAD drift). F-REV-D-05's untrue binding sentence was removed.

## What to review (suggested order)

1. `reviewer_report.md` → `fix_record.md`: confirm each finding is answered and that
   nothing in the report was silently reinterpreted.
2. Re-derive the three new numbers by hand (N5c 32, N5d 25, N5e 25) and check they
   FAIL on `iso/product_base` **and** on `iso/product_mut_authsplit`.
3. Re-run: `harness/run_i14d_oracle.py` (20 cases, narrow rc 0 / base rc 3),
   `harness/run_rule_table_i14d.py` (55 rows, `credential_leaks` and
   `credential_secret_leaks` both empty on narrow, rc 0), the copied suite with
   `I14C_PRODUCT_SRC=iso/product_narrow/src` (expect **86 passed**), the new suite
   (`25 passed`), and `harness/run_exit_probe.py` (E6 must persist
   `"Authorization: <redacted>\ndoc=17"` with zero persisted-or-printed hits).
   `iso/venv` is self-contained and the guard accepts a declared non-product scratch
   root through `I14C_RUN_ROOT`, so all of it runs from any directory.
4. Mutations: `mutations/mutation_matrix.json` plus the four standing trees
   (`product_mut_greedy`, `_mut_authnl`, `_mut_auth1_r2`, `_mut_authsplit`); rebuild any
   of them with `harness/apply_i14d_narrow.py --op <narrow|authsplit|mut_greedy|
   mut_authnl|mut_auth1_r2|mut_authsplit|reverse_authsplit>`.
5. Round-trips: `changes.diff` (base → r2 narrow, 5101 B) and
   `changes_r2_authsplit.diff` (pre-r2 → r2, 1786 B, the whole fix);
   `after/git_apply_verification.json` (GIT_APPLY_REPRODUCES true) and
   `recovery/recovery_verification_r2.json` (reverse-apply reproduces
   `iso/product_base` across all 152 non-`__pycache__` source files).
6. Judge the disclosed clause-5 transcription (item 3 above) and the disposition of
   F-REV-D-02/03/04 — whether they belong on a follow-up card or must block this one.
7. Scope/authorization notes: `decision.md` D1-r2, the declared residual N13, and
   `r5/README.txt` explaining the counts-shim directory.


---

## r3 (2026-09-22) — the status line at the top of this file is SUPERSEDED by this section

**Status: revision r3 submitted, RE-REVIEW REQUIRED.** The implementer writes no verdict here;
the r2 verdict below is the reviewer's and is not inherited by r3.

### Verdict history, continued

| round | reviewer verdict | artifact |
|---|---|---|
| r2 | **`changes_required`** — one BLOCKER-class residual (`F-REV-R2-01`: the fix closed the measured *instance*, not the *class*), plus `F-REV-R2-02` (MEDIUM), `F-REV-R2-03` (LOW), `F-REV-R2-04` (INFO) | `reviewer_report_r2.md`, 39824 B, sha256 `58f92dd7e3a3f66639dbdab4743455a878c4122500ac2d8d132e2eae2bee6c2c` — both recomputed from disk when this section was written |
| r3 | *pending* | this attempt after the r3 revision |

### What r3 changed

`_AUTH_SCHEME_SPLIT` was generalised from a nine-word enumeration of scheme words to one
RFC-7235 scheme token, with a run of line breaks and the quoted form tried after the break
(`iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py:317-323`).
The residual that the generalised branch cannot close is **registered** rather than hidden
(oracle rows `R3a`/`R3b`; rule-table kind `registered_open`). The over-redaction cost is
**registered** as 9 rule-table rows of kind `over_redaction`.

### What r3 did NOT do

No verdict is expressed. `status` is unchanged: the card remains `review_pending` until an
independent reviewer rules. The three documentary items the r2 review raised are landed as
appended corrections (`oracle.md` CORRECTION 3, `fix_record.md` CORRECTION 3, `binding.json`
`r3_corrections`), not as rewrites.


---

## r3 verdict (2026-09-22) — the independent reviewer returned `changes_required`

**Verdict: `changes_required` — the r3 revision is NOT accepted.** The verdict is the reviewer's;
this attempt states none of its own.

**Carrier**: `reviewer_report_r3.md`, 44008 B, sha256 `c617c43a7f674b6b9098a252c10aa354f3634d4c345aa5133d75287e26aa003b` — recomputed from the bytes
when this section was written. The report was written to this attempt as a FILE before this section
landed, per the process requirement this project established after losing a reviewer report that
existed only in a chat message.

### What the reviewer CONFIRMED (7 of the 9 claims)

The generalisation F-REV-R2-01 asked for is real and landed (the nine-word enumeration is gone, one
RFC-7235 scheme token is consumed, the break is a run, the quoted form is tried after the break); the
r2 reviewer's own C1-C12 matrix reproduces with r3 leaking only C10; the residual is registered on
both instruments with the 39-char non-marker credential; the over-redaction family is registered as 9
rows; the three false base-tree claims were false and are corrected by appended corrections with the
original bytes kept; the design trade-off reproduces under the reviewer's own reconstruction; and no
verdict was pre-empted.

### What the reviewer REFUTED (2 of the 9)

* **Claim 3 — "the residual is registered, not hidden" — REFUTED.** A leak exists that is enumerated
  nowhere.
* **Claim 8 — "the carrier does not overstate" — REFUTED.** See F-REV-R3-02.

### The BLOCKER — F-REV-R3-01

The after-break quoted alternatives are written `\"[^\"\r?\n]*\"` and `'[^'\r?\n]*'`. **Inside a
character class `?` is a literal member of the negated set**, not the optional-`\r` metacharacter that
`_QUOTED_VALUE` uses two lines above (`\"[^\"\r\n]*\"`). A quoted credential continuation containing
`?` is therefore not matched by that alternative, and because a leading `"` is also a delimiter for
`_AUTH_BARE_VALUE`, the whole scheme-split alternative fails and the credential survives:

```
redact_text('Authorization: Bot\n"<39-char credential>?x"')
  -> 'Authorization: <redacted>\n"<39-char credential>?x"'    # credential persists
```

This was reproduced independently outside the review as well. It is **unregistered** — no oracle row
and no rule-table row covers it — while `oracle.md` C3.4, the source comment and `handoff_r3.json`'s
`credential_leaks_is_sound_again: true` all assert the branch is fail-closed for exactly this shape.
That is the same structural defect F-REV-R2-01 named: a measured instance closed, a residual class
left open, and the exit criterion offered as sound. The cause is proven by correcting the single
character **in memory** and watching the leak close; nothing on disk was touched.

### The remaining findings (registered, not reproduced here)

`F-REV-R3-02` (MEDIUM) the carrier cites a verification whose overall verdict does not reproduce;
`F-REV-R3-03` (LOW) the source comment's explanation of why the branch is safe is false and
contradicts the next paragraph; `F-REV-R3-04` (LOW) the scheme class requires a leading letter, which
is narrower than the ABNF it cites and is a persistence regression against `product_base` for
non-letter-initial schemes; `F-REV-R3-05` (LOW) a value whose first character after the break is a
value delimiter is not redacted (bounded, non-regressive); `F-REV-R3-06` to `F-REV-R3-10` (INFO).

### Scope the verdict does NOT cover (the reviewer's own words)

The r2 generation's own correctness beyond what r3 inherits; the copied pytest suites and the real
worker/CLI exit, which the reviewer did not re-run; promotion, `disclosure_adaptation`, accuracy or any
mapping question; the r2 reviewer's RULING 1 rewrite; the mutation trees M1-M3 beyond the single M4 arm
used for the leak direction; and whether any downstream consumer depends on the deleted diagnostic key.

**Status: `review_pending`.** r3 is not accepted. A fix for F-REV-R3-01 belongs to a new revision
(r4), not to this one.


---

## r4 (2026-09-22) — submitted, RE-REVIEW REQUIRED

**Status: revision r4 submitted.** The implementer writes no verdict here.

### What r4 changed

Two code fixes, both from the r3 review, plus the rows that register them:

| finding | fix | site |
|---|---|---|
| `F-REV-R3-01` (BLOCKER) | the optional-CR form inside the after-break character classes is replaced by `\r\n` — exactly two bytes | `observability.py:320` |
| `F-REV-R3-04` (LOW) | the scheme token class is widened from `[A-Za-z]…*` to the full RFC 7230 tchar | `observability.py:317` |

Four new frozen oracle rows (`N5l`-`N5o`) and four new rule-table rows register both families.
r4 has its **own** harness files; the r3 harnesses are byte-identical to their pins.

### What r4 did NOT do

`F-REV-R3-02` (the r3 carrier's overstatement), `F-REV-R3-03`, `F-REV-R3-05` and `F-REV-R3-06`
to `F-REV-R3-10` are **not** addressed here; they are registered in the remediation register.
The r3 carrier `handoff_r3.json` is left exactly as it was — its overstatement is a historical
record of what was claimed at the time, and the correction belongs to this generation.

### Two self-inflicted errors, recorded rather than quietly fixed

1. **The r4 product tree was corrupted by a text-mode round trip.** `Path.read_text`/`write_text`
   doubled every carriage return (CR 897 -> 1794, i.e. `\r\r\n`) while leaving the content
   correct, so a diff with `\r` stripped showed only the intended changes. Rebuilt on bytes, with
   the inverse reconstruction as the proof.
2. **The first r4 measurement leaked state between candidates.** The candidate that rebinds the
   module's global pattern ran first, so the "tree as it stands" candidate read that same rebound
   pattern — and the report said fix B changed nothing when in fact it closes the non-letter
   family. The import-time pattern is now captured before any candidate runs.


---

## r4 verdict (2026-09-22) — the independent reviewer returned `changes_required`, with all eleven claims CONFIRMED

**Verdict: `changes_required` — the r4 revision is not accepted as delivered.** The verdict is
the reviewer's; this attempt states none of its own.

**Carrier**: `reviewer_report_r4.md`, 51860 B, sha256 `f27a85a51596075b795d885a5ca5120bcd4ccbf057ce9c3d9f9075ff9d294bc6` — recomputed from the bytes
when this section was written. The report was written to this attempt as a FILE before this
section landed.

### The unusual shape of this verdict, stated plainly

**All eleven claims the reviewer was asked to test came back CONFIRMED, and none were refuted.**
The fixes are real: r4 differs from r3 in exactly the four byte regions the carrier names, and
inverting those regions reproduces r3 byte for byte; the `?` leak is closed **at the class
level** (the after-break quoted alternatives are now byte-identical to `_QUOTED_VALUE`, and a
200-probe character sweep leaves only `\n`/`\r`); the non-letter family is closed and r4 beats
`product_base` (0 leaks against 3); all eight new rows go red on the r3 tree; no pre-existing row
moved; every registered hash reproduces.

**The verdict is nevertheless `changes_required`, because what fails is not the fix but the
record and the registration.** Two MEDIUM and two LOW findings:

* **`F-REV-R4-05` (MEDIUM)** — an **unregistered** credential-persistence family:
  `Authorization: <non-tchar-token>\n<credential>`. `redact_text('Authorization: Bo?t\n<the
  card's own marker>')` persists the marker on r4, while `product_base` redacts it. 31
  unregistered base-regressive shapes. **Reproduced independently outside the review as well.**
  Not introduced by r4 (r2 and r3 leak it too, and r4 strictly reduces the family), but it is
  unregistered, and this card's whole history is about unregistered families.
* **`F-REV-R4-06` (MEDIUM)** — **the record overstates.** `oracle.md` C4.5 says "`fix_A_and_B`
  leaves only the registered `C10` residual". That is true **only of the 19-probe measurement
  set** the section reports; as written it is a general claim, and it is false. The same sentence
  is repeated in the remediation register and in task_plan.md Round 72. **This is the
  `F-REV-R3-02` species recurring** — the previous reviewer raised exactly this about the r3
  carrier, and it has happened again one generation later.
* **`F-REV-R4-01` (LOW)** — the source comment at `observability.py:295-298` is byte-identical to
  r3: it still asserts the false "always begins with a letter" ABNF, and it now contradicts line
  317, which the fix widened.
* **`F-REV-R4-02` (LOW)** — `measure_r4.py`'s docstring and `r4_measurement.json`'s key
  `fix_b_measured_but_not_applied` say fix B is not in the tree; the same file's `main()` says
  the opposite. The measurement record contradicts itself.

### Scope the verdict covers, and what it does not

It covers the r4 product copy, both r4 harnesses, the r3 harnesses' byte-pins, the r4 carriers,
and the r4 measurement directory. It does not cover the copied pytest suites, the real worker or
CLI exit, promotion, or any mapping question.

**Status: `review_pending`.** A fix for `F-REV-R4-05` and a correction of `F-REV-R4-06` belong
to a new revision (r5), not to edits of r4.


---

## r5 (2026-09-22) — submitted, RE-REVIEW REQUIRED

**Status: revision r5 submitted.** The implementer writes no verdict here.

### What r5 changed

| finding | response | site |
|---|---|---|
| `F-REV-R4-05` (MEDIUM) | **fixed**: the pre-break token widened from the RFC 7230 tchar class to the value-token class; the constant renamed `_AUTH_PREBREAK_TOKEN` | `observability.py:317` |
| `F-REV-R4-01` (LOW) | **fixed**: the comment block rewritten to say what the code does, the false "always begins with a letter" claim removed, and the dangling `r3_fix_record.md` reference replaced with a pointer that says the file was never written | `observability.py:290-325` |
| `F-REV-R4-06` (MEDIUM) | **corrected by supersession**: `oracle.md` CORRECTION 5 C5.3 states that C4.5's sentence is false as written, gives the corrected form with its domain, and records that this is `F-REV-R3-02` recurring | `oracle.md` C5.3 |
| `F-REV-R4-02` (LOW) | **registered, not edited**: the r4 measurement record's hashes are pinned by the r4 carrier, so it is left as it is and the contradiction is registered | `oracle.md` C5.5 |

Four new frozen oracle rows (`N5p`-`N5s`) and four new rule-table rows register the family. r5
has its **own** harness files; the r3 and r4 harnesses are byte-identical to their pins.

### What r5 did NOT do

`F-REV-R3-02`, `-03`, `-05`, `-06` to `-10` remain registered and unaddressed. The r4 carrier
`handoff_r4.json` is left exactly as it was.

### One self-inflicted error, recorded

The first r5 tree build matched the comment block at **zero sites** because the templates were
written with LF while the file is CRLF. The build was made line-ending aware and the result is
proved by inverting the replacements. Separately, the first version of the build's own check
asserted "the CR count is unchanged", which went red on a correct rebuild — the comment block
legitimately grows, so the count must grow with it; the check is now "the file stays uniformly
CRLF".


---

## r5 verdict (2026-09-22) — the independent reviewer returned `changes_required`; 11 of 13 claims confirmed, 2 refuted

**Verdict: `changes_required`.** The verdict is the reviewer's; this attempt states none of its own.

**Carrier**: `reviewer_report_r5.md`, 49279 B, sha256 `9f8fdba98c473ec9510d53e4a605fba4072cf8e276485c5c091f83e7683311d5` — recomputed from the bytes
when this section was written.

### The two refuted claims, and the two MEDIUM findings

* **Claim 2 refuted / `F-REV-R5-01` (MEDIUM) — the new class is a SWAP, not a widening.**
  Sweeping all printable characters at the pre-break position gives `r4 \ r5 = ['&', "'", '|']`.
  `Authorization: Bo&t` + newline + the card's marker **redacts on r4 and persists on r5**; six
  credential-persistence shapes that r4 redacted are re-opened, and none is registered. Not
  base-regressive (`product_base` leaks them too), hence MEDIUM rather than BLOCKER.
  **Reproduced independently outside the review as well.**
  ⇒ **Claim 2's "the family is closed" holds only for r4's leak set**, which is exactly why
  Claim 3 fails: the widening moved the hole rather than removing it.

* **Claim 9 refuted / `F-REV-R5-02` (MEDIUM) — r5's own record overstates, one paragraph above
  the correction that declares the structurally identical sentence false.** `oracle.md` C5.1
  says the widening "**closes the whole family** at **zero cost**". It is priced by
  `measure_r5.py`'s 19 probes, of which **4** are family members, against a family of **31
  base-regressive shapes**. This is the `F-REV-R4-06` species — a universal carried on a
  measurement set that does not contain its own counterexamples — recurring **one paragraph
  above C5.3**, which declares C4.5's structurally identical sentence false.

Non-blocking: `F-REV-R5-03`, `-04`, `-05` (LOW) and `-06`, `-07`, `-08` (INFO).

### What held

All 24 registered hashes reproduce from bytes; the r3 and r4 harnesses are byte-identical to
their pins; generation isolation holds; the over-redaction family and the registered `C10`
residual are unchanged; five of the reviewer's negative controls went red; the attempt was left
untouched.

**Status: `review_pending`.** A fix for `F-REV-R5-01` and a correction of `F-REV-R5-02` belong
to a new revision (r6), not to edits of r5.
