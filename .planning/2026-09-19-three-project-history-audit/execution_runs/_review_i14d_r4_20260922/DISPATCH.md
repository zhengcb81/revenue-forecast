# Independent review dispatch — `I-14-D`, revision r4

**Reviewer**: an independent subagent, not the author of any of this. Read this file first; it
is self-contained, so you do not need the dispatcher's session.

**Your verdict is yours.** Nothing here asks you to agree with anything. Two previous reviewers
of this card each returned `changes_required` on a revision whose author believed it was
complete. The most useful thing you can do is find out whether that is true a third time.

---

## 1. What you are reviewing

`I-14-D` is a product-level fix in `company-wiki`'s redactor
(`company_wiki/source_catalog/observability.py`). Its history inside this attempt:

| rev | what it was | verdict |
|---|---|---|
| r1 | the original narrowing | `changes_required` — BLOCKER `F-REV-D-01` |
| r2 | added a **nine-word enumeration** of scheme words | `changes_required` — BLOCKER `F-REV-R2-01` (closed the instance, not the class) |
| r3 | generalised to **one RFC-7235 scheme token** + a run of line breaks | `changes_required` — BLOCKER `F-REV-R3-01` (a one-character defect) |
| **r4** | **two fixes**, below | **not yet reviewed — this is your job** |

**r4's two fixes, both from the r3 review:**

* **`F-REV-R3-01` (BLOCKER)** — the after-break quoted alternatives carried the optional-CR form
  **inside a character class** (`\"[^\"\r?\n]*\"`), where `?` is a literal member of the negated
  set rather than a quantifier, so a quoted credential continuation containing `?` was not
  matched at all. r4 writes `\r\n`. **Two bytes changed.**
* **`F-REV-R3-04` (LOW)** — the scheme token class was `[A-Za-z][A-Za-z0-9!#$%&'*+.^_\`|~-]*`,
  which requires a leading letter; the RFC 7230 `token` production it cites does not. r4 uses
  the full tchar class `[A-Za-z0-9!#$%&'*+.^_\`|~-]+`.

## 2. Where everything is

`<attempt>` = `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01`

**Interpreter**: `<attempt>\iso\venv\Scripts\python.exe` (python 3.13.9, PyYAML 6.0.3). The
global interpreter lacks PyYAML and the harnesses will correctly return `rc=2 cannot_adjudicate`
if you use it.

| what | where |
|---|---|
| the r3 review you are answering | `<attempt>/reviewer_report_r3.md` (44008 B, sha256 `c617c43a7f674b6b9098a252c10aa354f3634d4c345aa5133d75287e26aa003b`) |
| **the r4 product copy** | `<attempt>/iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py` (42829 B, sha256 `15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1`) |
| the r3 copy (the pre-image) | `<attempt>/iso/product_narrow_r3/src/...` (42839 B, `a551cc45…`) |
| the pre-fix base copy | `<attempt>/iso/product_base/src/...` |
| **the r4 harnesses** | `<attempt>/harness/run_i14d_oracle_r4.py` (12316 B, `240d181c…`), `<attempt>/harness/run_rule_table_i14d_r4.py` (20006 B, `610ce4b8…`) |
| the r3 harnesses (must be UNCHANGED) | `<attempt>/harness/run_i14d_oracle.py` (`f7c94c60…`), `<attempt>/harness/run_rule_table_i14d.py` (`01a3187e…`) |
| **the r4 carrier** | `<attempt>/handoff_r4.json` (6606 B) |
| the r4 corrections | `<attempt>/oracle.md` CORRECTION 4; `<attempt>/review.md` section `## r4` |
| the r4 measurement | `../_r4_measure_20260922/` (`measure_r4.py`, `r4_measurement.json`, `oracle_r4_harness.json`, `rule_r4_harness.json`) |
| the r3 verification (prior, by the same party as the carrier) | `../_verify_20260922_i14d_r3/` |

Treat anything produced by the party that wrote the carrier as an **input to be checked**, not
as evidence that something is true.

## 3. The claims you are asked to test

Report each as CONFIRMED / REFUTED / UNVERIFIABLE with the measurement.

1. **The two fixes are what the carrier says.** Byte-level: r4 differs from r3 in exactly the
   four byte regions the carrier names, and **inverting those regions reproduces r3 byte for
   byte, line endings included**. `observability.py:319`'s `\r?\n` is deliberately untouched —
   confirm it is still there and confirm why that is correct.
2. **The `?` leak is closed.** Both quote styles, both credentials. And check the leak is
   closed **at the class level**, not just for the two strings the rows name — the r3 review
   found the r2 fix had closed only the measured instance, and that is the failure mode this
   card keeps repeating.
3. **The non-letter-scheme family is closed**, and this is a **regression the r3 review
   measured** — so compare against `product_base`, not only against r3.
4. **The new rows are registered and their expectations are sound.** Four oracle rows
   (`N5l`-`N5o`) and four rule-table rows. **Disclosure you should act on**: their expected
   strings were *observed from the r4 tree and then frozen*, which is weaker than the
   hand-computation the oracle's own section 2 requires. CORRECTION 4 C4.3 gives a derivation
   for each. **Test whether they are in fact derivable from the specification independently of
   the code.** If they are, say so and say why; if they are not, that is a finding.
5. **No regression in the pre-existing rows.** The 28 r3 oracle rows and the 79 r3 rule-table
   rows must be **unchanged** on the r4 tree. Compare row by row.
6. **The over-redaction family is unchanged**, and still registered as 9 rows.
7. **The generation isolation is real.** The r3 harnesses are byte-identical to the pins in the
   r3 carrier (`f7c94c60…`, `01a3187e…`); the r4 rows live only in the new files. Explain why
   that matters and whether r4 got it right.
8. **The carrier does not overstate.** This is the finding the r3 review raised
   (`F-REV-R3-02`): the r3 carrier cited a verification as "overall PASS, idempotent" that no
   longer reproduces. Read `handoff_r4.json` and say whether any sentence claims more than the
   measurements support. Note that this is the **newest** artefact and has had the least
   scrutiny.
9. **The three self-inflicted errors are honestly recorded**: a text-mode round trip that
   doubled every carriage return in the r4 tree while leaving the content correct; a state leak
   between measurement candidates; a second text-mode round trip in the harness build. Check
   that the record is accurate and that the fixes actually address the causes.
10. **What r4 did NOT do is honestly scoped.** `F-REV-R3-02`, `-03`, `-05`, `-06` to `-10` are
    not addressed. Confirm they are registered rather than quietly dropped.
11. **No verdict was pre-empted.** The card must still be `review_pending` and no record may
    already say "accepted".

## 4. Techniques this project requires, and why

* **Recompute every hash from the bytes.** A hand-written hash looks identical to a real one.
* **Classify a red before believing it.** When a check fails, ask first whether the *data* is
  wrong or the *predicate* is. This project's logs are full of instruments that were off by one
  byte, one character, or one unit — including three in the round that produced r4.
* **A predicate that cannot fail is not a predicate.** Feed each check a mutated input in memory
  and confirm it goes red. Report which of your checks you tested this way.
* **Write bytes, never through text mode, when line endings matter.** This bit the r4 author
  twice; the files here have registered sha256 values, so their line endings are part of their
  identity.
* **Do not edit anything under the attempt.** You are a reader. Write only your report, and any
  scratch outputs, OUTSIDE it — use the sibling directory `..\_review_i14d_r4_20260922\`.
* **Never delete, move or clean up any file.** This is absolute.

## 5. Required output

Write your full report to `<attempt>/reviewer_report_r4.md` — **as a FILE**, not only as a
message back. A verdict that exists only in a chat message has no byte-fixed carrier, and this
project has already lost one report that way.

It must contain:

1. a **VERDICT** line (`accepted_scoped` / `changes_required` / `cannot_adjudicate`), the scope
   it covers, and explicitly what it does **not** cover;
2. each of the eleven claims above marked CONFIRMED / REFUTED / UNVERIFIABLE with the measurement;
3. a **FINDINGS** section with a severity per finding and a reproducible command;
4. an **UNVERIFIED** section;
5. a **HOW TO REPRODUCE** section with the exact commands;
6. a note on which of your own checks you confirmed are responsive.

Then report back in under 300 words: your verdict, the confirmed/refuted/unverifiable counts,
any blocking finding, and the sha256 and byte size of the file you wrote.
