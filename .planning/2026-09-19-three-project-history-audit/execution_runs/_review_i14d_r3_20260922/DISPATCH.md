# Independent review dispatch — `I-14-D`, revision r3

**Reviewer**: an independent subagent, not the author of any of this. Read this file first;
it is written to be self-contained, so you do not need the dispatcher's session.

**Your verdict is yours.** Nothing here asks you to agree with anything. The r2 reviewer
returned `changes_required` on a revision that its own author believed was complete; the
most useful thing you can do is find out whether the same is true again.

---

## 1. What you are reviewing

`I-14-D` is a product-level fix in `company-wiki`'s redactor
(`company_wiki/source_catalog/observability.py`). Its history inside this attempt:

| revision | what it was | reviewer verdict |
|---|---|---|
| r1 | the original narrowing | `changes_required` — BLOCKER `F-REV-D-01`: the auth path persisted a credential in plaintext when a line break separated the scheme word from the secret |
| r2 | added `_AUTH_SCHEME_SPLIT`, a **nine-word enumeration** of scheme words | `changes_required` — BLOCKER `F-REV-R2-01`: the fix closed the measured **instance**, not the **class**; every scheme word outside the nine still leaked |
| **r3** | generalises that branch to **one RFC-7235 scheme token** + a run of line breaks + the quoted form after the break | **not yet reviewed — this is your job** |

## 2. Where everything is

All paths are relative to
`C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01\`
(referred to below as `<attempt>`).

**The Python interpreter to use.** `<attempt>\iso\venv\Scripts\python.exe`
(python 3.13.9, PyYAML 6.0.3). The global interpreter lacks PyYAML and the harnesses will
correctly return `rc=2 cannot_adjudicate` if you use it — that is the harness behaving
properly, not a defect, but it will waste your time.

| what | where |
|---|---|
| the r1 reviewer's report | `<attempt>/reviewer_report.md` (37659 B, sha256 `499d91ac…`) |
| **the r2 reviewer's report — your starting point** | `<attempt>/reviewer_report_r2.md` (39824 B, sha256 `58f92dd7e3a3f66639dbdab4743455a878c4122500ac2d8d132e2eae2bee6c2c`) |
| the r3 product copy | `<attempt>/iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py` (42839 B, sha256 `a551cc45…`) |
| the pre-fix base copy | `<attempt>/iso/product_base/src/...` |
| the r2 copy (for comparison) | `<attempt>/iso/product_narrow/src/...` |
| the frozen oracle harness | `<attempt>/harness/run_i14d_oracle.py` (11043 B, `f7c94c60…`) |
| the rule table harness | `<attempt>/harness/run_rule_table_i14d.py` (19378 B, `01a3187e…`) |
| the tree-mutation tool | `<attempt>/harness/apply_i14d_narrow.py` (19773 B, `8204b2f9…`) |
| the r3 carrier you are reviewing | `<attempt>/handoff_r3.json` (9788 B) |
| the r3 corrections | `<attempt>/oracle.md` CORRECTION 3, `<attempt>/fix_record.md` CORRECTION 3, `<attempt>/binding.json` key `r3_corrections`, `<attempt>/review.md` section `## r3` |
| prior independent verification | `../_verify_20260922_i14d_r3/` (8 propositions, 7 negative controls) |
| prior design-space reproduction | `../_r3_design_reprobe_20260922/` |

**Important about the two prior verification directories.** They were produced by the same
party that wrote the r3 carrier. Treat them as *inputs to be checked*, not as evidence that
anything is true. If they are sound, say so and say why; if their predicates are vacuous,
that is a finding.

## 3. The claims you are asked to test

Each is falsifiable. Report each as CONFIRMED / REFUTED / UNVERIFIABLE with the measurement.

1. **The generalisation is real.** `_AUTH_SCHEME_SPLIT` now consumes one RFC-7235 scheme
   token (class `[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*`), a **run** of line breaks, and the
   quoted form is tried after the break. The nine-word enumeration is gone. Check the bytes;
   do not take the comment block's word for it.
2. **The class is closed, not just the instance.** Re-run the r2 reviewer's own C1-C12
   matrix (`reviewer_report_r2.md` section 2.3) against the r3 tree. r2 leaked C1-C11; r3
   should leak only C10.
3. **The residual is registered, not hidden.** Oracle rows `R3a-two-token-then-wrap` and
   `R3b-quoted-two-token` are kind `registered_open` and their declarations carry the
   **39-character non-marker credential**. The rule table's `registered_open_rows` is the
   same pair. Verify that `credential_leaks == []` is therefore sound again — i.e. that no
   *unregistered* leak exists.
4. **The rule table's `verdict: "negative"` is correct and not a failure.** The verdict is
   computed over all rows' secret survival, and the only rows where the credential survives
   are the two registered-open ones. Confirm this reading against `run_rule_table_i14d.py`.
5. **The over-redaction cost is registered.** 9 rule-table rows of kind `over_redaction`,
   with `over_redaction_touched` equal to the same set. And `oracle.md` C3.4 states the
   branch is fail-closed in **both** directions.
6. **The three false base-tree claims are corrected, and were false.** `oracle.md` line 272
   and `fix_record.md` line 86 said all three of N5c/N5d/N5e fail on the base tree;
   `after/r2_summary.json`'s `narrow_must_failed_base` lists N5c and N5e. Re-run the oracle
   against `iso/product_base` and report which of the three actually fail. The corrections
   are appended and the original bytes are kept — verify that nothing was rewritten.
7. **The design trade-off is honestly stated.** The source comment claims that closing the
   two-token-then-wrap shape needs the scheme's line consumed as a token run, which deletes
   `doc=17`. The prior reproduction says this is true and that the cost is 2 genuine
   regressions plus 2 registered rows. Test it yourself.
8. **The carrier does not overstate.** Read `handoff_r3.json` and say whether any sentence
   claims more than the measurements support. This is the newest artefact and the one with
   the least scrutiny behind it.
9. **No verdict was pre-empted.** The card must still be `review_pending` and no record may
   already say "accepted". Check.

## 4. Techniques this project requires, and why

* **Recompute every hash from the bytes.** A hand-written hash looks identical to a real one.
  If a registered value does not match, say which, and do not assume the file is corrupt —
  check whether the *registration* is wrong.
* **Classify a red before believing it.** When a check fails, first ask whether the data is
  wrong or the *predicate* is wrong. Both happen here constantly; the project's own logs
  record several instruments that were off by one byte, one character, or one unit.
* **A predicate that cannot fail is not a predicate.** If you write a check, feed it a
  mutated input in memory and confirm it goes red. Report which of your checks you tested
  this way.
* **Do not edit anything under the attempt.** You are a reader. Write only your report.
* **No file may be deleted, moved or cleaned up.** This is absolute.

## 5. Required output

Write your full report to:

```
<attempt>/reviewer_report_r3.md
```

Write it there **as a file** — not only as a message back to the dispatcher. A verdict that
exists only in a chat message has no byte-fixed carrier, and this project has already
recorded one instance of a reviewer report being lost that way.

Your report must contain:

1. a **VERDICT** line, one of `accepted_scoped` / `changes_required` / `cannot_adjudicate`,
   plus the scope the verdict covers and, explicitly, what it does **not** cover;
2. for each of the nine claims above: CONFIRMED / REFUTED / UNVERIFIABLE, with the measurement;
3. a **FINDINGS** section, each with a severity and a reproducible command;
4. an **UNVERIFIED** section — what you could not test and why;
5. a **HOW TO REPRODUCE** section with the exact commands you ran;
6. a note on which of your own checks you confirmed are responsive.

Then report back to the dispatcher, in under 300 words: your verdict, the count of
confirmed/refuted/unverifiable claims, any finding you consider blocking, and the sha256
and byte size of the file you wrote.
