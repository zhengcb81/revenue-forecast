# I-14-D decision.md

Status: **D1 was OVERTURNED by the independent reviewer and is replaced by D1-r2
(reviewer RULING 2); everything else is implementer-level and was resolved inside the
frozen oracle.** The implementer does not self-accept; `handoff.json` status stays
`review_pending`.

---

## D1-r2 — the authorization/bearer path: scheme-aware, fail-closed (SUPERSEDES D1)

### What the review found (F-REV-D-01, BLOCKER)

D1 chose "the auth value is a run of tokens joined by inline whitespace only". That
closes C13 (a value cannot cross a newline) but it also consumes the **scheme word
alone** when a line break separates scheme from secret, and the secret's line has no
`key=` prefix for the assignment scanner to find. Measured on the r1 tree:

`"Authorization: Bearer\n<SECRET>\ndoc=17"` → `"Authorization: <redacted>\n<SECRET>\ndoc=17"`
— **the full credential persisted in the append-only event log.** The r1 tree did
keep `doc=17`; the pre-fix tree redacted the secret and deleted `doc=17`. So r1 traded
"diagnostics deleted" for "credential written to the log", which violates the card's
own negative clause. Confirmed by the reviewer helper-level across 10 variants and
end-to-end through `worker.py`'s `redact_and_truncate` exit; reproduced in this attempt
before fixing (`before/authsplit_probe_base.json` vs the pre-fix probe in `handoff.json`).

### The decision now in force

**After a *known* scheme word (`bearer`, `token`, `basic`, `digest`, `oauth`, `jwt`,
`apikey`, `api_key`, `sso`) and exactly one line break, the first token is redacted
(fail closed).** The break and any indentation stay outside the match, so the
diagnostic keys on the following lines survive.

* Mechanism: `_AUTH_SCHEME_SPLIT`, placed first in the value alternation (after the
  quoted form), `iso/product_narrow` only.
* Both halves of the exit clause now hold **on the same input**:
  `"Authorization: <redacted>\ndoc=17"` (32 chars), verified at the real exit.
* Same-line behaviour is byte-identical to r1 and to I-14-C's frozen expectations
  (`cred-header-*`, `cred-auth-sameline-tail-kept`, the E1 25-char baseline, oracle
  N5/N5b) — the change is confined to the `scheme␊secret` family.
* Cost: a *known* scheme word followed by a line break now always redacts the next
  token, i.e. `"Authorization: Bearer\ndoc=17"` would over-redact `doc=17` the way the
  base tree did. That is the fail-closed direction the reviewer chose, and it is why
  the accepted alternative ("redact the first token only if the matched value is
  exactly a known scheme word") was NOT taken: it needs the same branch with more
  state.

### Rejected alternatives, re-stated after the review

1. *r1's line-bounded token run without the scheme branch* — **rejected as
   credential-persisting** (F-REV-D-01; M4 re-opens it by construction).
2. *Strict single token everywhere + scheme word moved into the KEY* — still rejected;
   it has the same hole in any line-bounded reading of its optional scheme group, and
   it rewrites five frozen I-14-C envelopes for no benefit. M3 (`product_mut_auth1_r2`)
   shows a scheme-ignoring single token **leaks** 8 auth rows and both same-line
   controls.
3. *Leave the auth regex untouched* — still rejected: C13 stays open on the auth path
   (M2 shows the line bound is load-bearing for that half).

## Recorded, NOT fixed (reviewer's instruction) — promotion hazards

* **F-REV-D-02 (MEDIUM, promotion hazard).** `_VALUE` is **dead code** in both trees:
  `_AUTH_PATTERN` inlines its pieces and the assignment scanner is hand-written. So the
  headline "narrow `_BARE_VALUE`" edit has **no runtime effect**; the assignment-path
  behaviour change comes **entirely** from the scanner-loop hunk (M1 proves the loop is
  what moves E4b). Consequence for promotion: a future reader could delete the dead
  constant believing the fix is intact, or promote the constant without the loop. This
  is recorded here so the promoter sees it; the constant is deliberately left untouched
  so the diff stays exactly what the reviewer measured. The same dead-constant pattern
  in `_AUTH_PATTERN` is where F-REV-D-01 hid — the branch was chosen by alternation
  order, not by anything that recognized a scheme.
* **F-REV-D-03 (MEDIUM).** The narrowing unmasks a pre-existing atom-table gap:
  `redact_text("token=<A> token2=<B>")` leaves `<B>` in the clear, because
  `token2`/`secret2`/`password2`/`api_key2` are not credential keys (`refresh_token`,
  `access_token`, `token_2` do work). The greedy swallow used to delete it by accident.
  Needs its own rule-table row and a follow-up card; not fixed on this card.
* **F-REV-D-04 (LOW).** A value-less header still swallows the next token:
  `"Authorization:\ndoc=17\nstage=summarize"` loses `doc=17` on the narrow tree too
  (one of the two keys now survives, so the narrowing improves it). Open C13 sub-case.
* **F-REV-D-05 (LOW).** `binding.json` claimed `harness/tests/conftest.py` carried a
  one-line tree-pointing change; it is byte-identical to I-14-C's (`783b1774…`, 275 B).
  Documentation corrected in `binding.json`; the file itself is untouched.
* **F-REV-D-07 (INFO).** External `revenue-forecast` HEAD drift since the r1 binding.

## Separation of duties — disclosed change

Card clause 5 makes the rewrite of the 4 frozen greedy-semantics nodeids the
**reviewer's** act, and the r1 pass left them byte-identical. The re-review
instruction for this fix directed the implementer to land the reviewer's RULING 1
rewrite now that its condition (the BLOCKER) is fixed. It is therefore applied as a
**transcription of the reviewer's text** — no expectation in it was authored here —
and it is disclosed in `fix_record.md` §6, `handoff.json` and `oracle.md`
CORRECTION 2 §C2.4, with the r1 byte-state (`672b88de…`) named so it can be restored
or re-authored. The copied suite is consequently **no longer byte-identical to
I-14-C's**.

## NA items

- No schema/migration/transaction decision: nothing persisted changes shape
  (`message_redacted` values change content/length exactly as the card intends).
- No statistical/threshold decision. The E4b baseline move (193 → 314 pre-truncation
  / 200 persisted) is a hand-computed consequence of the frozen semantics, frozen in
  oracle.md §N4 and re-derived by the reviewer — not a threshold choice. The r2 fix
  does not move it (E4b persists 200 with the same tail).
- No cross-repo contract change: `error_taxonomy.structured_error` is untouched; only
  the redactor's value semantics change, inside the card's allowlist ("the existing
  redactor", same scope wording I-14-C used).
