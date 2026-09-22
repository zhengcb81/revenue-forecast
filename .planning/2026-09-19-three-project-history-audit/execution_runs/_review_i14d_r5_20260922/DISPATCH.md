# Independent review dispatch — `I-14-D`, revision r5

**Reviewer**: an independent subagent, not the author of any of this. Read this file first; it
is self-contained, so you do not need the dispatcher's session.

**Your verdict is yours.** Nothing here asks you to agree with anything. Three previous
reviewers of this card each returned `changes_required`. The most useful thing you can do is
find out whether that is true a fourth time — and note that the last one returned
`changes_required` while **confirming every single claim it was asked to test**, because what
failed was the *record*, not the *fix*.

---

## 1. What you are reviewing

`I-14-D` is a product-level fix in `company-wiki`'s redactor
(`company_wiki/source_catalog/observability.py`). Its history:

| rev | what it was | verdict |
|---|---|---|
| r1 | the original narrowing | `changes_required` — `F-REV-D-01` |
| r2 | a nine-word enumeration of scheme words | `changes_required` — `F-REV-R2-01` (instance closed, class open) |
| r3 | one RFC-7235 scheme token + a run of breaks | `changes_required` — `F-REV-R3-01` (a one-character defect) |
| r4 | fixed the `?`; widened to the full RFC 7230 tchar class | `changes_required` — **all 11 claims CONFIRMED**, but `F-REV-R4-05` (an unregistered family) and `F-REV-R4-06` (the record overstated) |
| **r5** | **widened the pre-break token to the VALUE-token class, rewrote the comment block, corrected the overstated sentence** | **not yet reviewed — this is your job** |

## 2. Where everything is

`<attempt>` = `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01`

**Interpreter**: `<attempt>\iso\venv\Scripts\python.exe` (python 3.13.9, PyYAML 6.0.3). The
global interpreter lacks PyYAML and the harnesses will correctly return `rc=2 cannot_adjudicate`
if you use it.

| what | where |
|---|---|
| the r4 review you are answering | `<attempt>/reviewer_report_r4.md` (51860 B, `f27a85a5…`) |
| **the r5 product copy** | `<attempt>/iso/product_narrow_r5/src/company_wiki/source_catalog/observability.py` (43362 B, `ca13fb81…`) |
| **the exact bytes of every generation** | `../_bookkeeping_20260922_round74/i14d_{base,r2,r3,r4,r5}_observability.py` — the `iso/` trees are gitignored, so these versioned copies are the only clone-checkable ones |
| the r4 copy (the pre-image) | `<attempt>/iso/product_narrow_r4/src/...` |
| **the r5 harnesses** | `<attempt>/harness/run_i14d_oracle_r5.py` (13293 B, `38a22101…`), `<attempt>/harness/run_rule_table_i14d_r5.py` (20600 B, `1e51373a…`) |
| the r3 and r4 harnesses (must be UNCHANGED) | `run_i14d_oracle.py` `f7c94c60…`, `run_rule_table_i14d.py` `01a3187e…`, `run_i14d_oracle_r4.py` `240d181c…`, `run_rule_table_i14d_r4.py` `610ce4b8…` |
| **the r5 carrier** | `<attempt>/handoff_r5.json` (6960 B) |
| the r5 corrections | `<attempt>/oracle.md` CORRECTION 5; `<attempt>/review.md` section `## r5` |
| the r5 measurement | `../_r5_measure_20260922/` |

Treat anything produced by the party that wrote the carrier as an **input to be checked**.

## 3. The claims you are asked to test

Report each as CONFIRMED / REFUTED / UNVERIFIABLE with the measurement.

1. **The widening is real and byte-correct.** r5 differs from r4 in the comment block and two
   code lines; inverting those regions reproduces r4 byte for byte; the file stays uniformly
   CRLF. Confirm the constant is renamed and that nothing else moved.
2. **The F-REV-R4-05 family is closed** — `Authorization: <non-tchar-token>` + newline +
   credential. Test it **at the class level, not on the four registered shapes**: sweep the
   complement of the new class at the scheme position. The last two generations each closed a
   branch and left the family open; do not accept four shapes as evidence for a family.
3. **The widening introduced no new leak family of its own.** Widening a class is the same move
   that has been made four times; ask what the *new* class fails to match, and where.
4. **The four new rows are registered and their expectations derivable.** `N5p`-`N5s` and the
   four rule-table rows. **Disclosure to act on**: as with r4, their expected strings were
   observed from the tree and then frozen. CORRECTION 5 C5.2 gives a derivation. Test whether
   they are derivable from the specification independently of the code.
5. **No regression.** The 32 r3+r4 oracle rows and the 83 r3+r4 rule-table rows must be
   unchanged on the r5 tree. Compare row by row.
6. **The over-redaction family is unchanged**, and the registered `C10` residual remains by
   design.
7. **The comment block now says what the code does** (`F-REV-R4-01`). Check every factual claim
   in it against the code and against the findings it cites. A comment that is merely *newer* is
   not thereby *true*.
8. **The correction of the overstated sentence is adequate** (`F-REV-R4-06`). It appeared in
   three carriers: `oracle.md` C4.5, `REMEDIATION_REGISTER.md` section 16, `task_plan.md` Round
   72. Verify all three are corrected, and that the corrected form **carries its domain**.
9. **THE ONE TO TRY HARDEST ON — does r5's own record overstate anywhere?** This species has now
   recurred twice (`F-REV-R3-02` then `F-REV-R4-06`), and the rule adopted is: *a conclusion
   sentence must carry its measurement set inside the sentence, and an unqualified negative
   claim is to be treated as unverified.* Read `handoff_r5.json`, `oracle.md` C5 and `review.md`
   `## r5` and say whether every claim has its domain attached. **This is the newest artefact
   and the one with the least scrutiny behind it.**
10. **The finding about this repository is correct.** The `iso/` trees are gitignored by policy,
    so the product trees were never versioned while their hashes were registered in committed
    carriers. Check that claim (including for r2 and r3, which nobody had noticed), check that
    the rescued copies match the carriers one for one, and say whether the remedy is adequate.
11. **Generation isolation still holds.** r3 and r4 harnesses byte-identical to their pins; r5
    rows only in the new files.
12. **What r5 did NOT do is honestly scoped.** `F-REV-R3-02`, `-03`, `-05`, `-06` to `-10` are
    registered and unaddressed; `F-REV-R4-02` is registered but deliberately not edited.
13. **No verdict was pre-empted.** The card must still be `review_pending`.

## 4. Techniques this project requires, and why

* **Recompute every hash from the bytes.** A hand-written hash looks identical to a real one.
* **Classify a red before believing it.** Ask first whether the *data* is wrong or the
  *predicate* is. This project's logs are full of instruments off by one byte, one character, or
  one unit — including several in the rounds that produced r4 and r5.
* **A predicate that cannot fail is not a predicate.** Feed each check a mutated input in memory
  and confirm it goes red. Report which you tested this way.
* **Write bytes, never through text mode, when line endings matter** — and here they do, because
  the trees' sha256 values are registered. This bit the r4 and r5 authors repeatedly.
* **An unqualified negative claim is unverified.** If you cannot attach a domain to a claim,
  say so rather than confirming it.
* **Do not edit anything under the attempt.** Write only your report and scratch outputs, and
  put the scratch OUTSIDE it, in the sibling directory `..\_review_i14d_r5_20260922\`.
* **Never delete, move or clean up any file.** This is absolute.

## 5. Required output

Write your full report to `<attempt>/reviewer_report_r5.md` — **as a FILE**, not only as a
message back. A verdict that exists only in a chat message has no byte-fixed carrier, and this
project has already lost one report that way.

It must contain:

1. a **VERDICT** line (`accepted_scoped` / `changes_required` / `cannot_adjudicate`), the scope
   it covers, and explicitly what it does **not** cover;
2. each of the thirteen claims marked CONFIRMED / REFUTED / UNVERIFIABLE with the measurement;
3. a **FINDINGS** section with a severity per finding and a reproducible command;
4. an **UNVERIFIED** section;
5. a **HOW TO REPRODUCE** section with the exact commands;
6. a note on which of your own checks you confirmed are responsive.

Then report back in under 300 words: your verdict, the confirmed/refuted/unverifiable counts,
any blocking finding, and the sha256 and byte size of the file you wrote.
