# AFTER fix cycle: the two mismatches found by the first AFTER run

Honest record. The first AFTER run (same command as `after/cmd-CASES`, same frozen
cases and expectations) reported `runner rc=1`, `mismatch_count=3`,
`accepted_ineligible_count=0`:

| case | field | expected | got |
|---|---|---|---|
| C1 | refusals | `R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT` | `R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-SAME-INSTANT` (missing `R-FUTURE-CLOCK`) |
| L2 | refusals | `R-LABEL-ANCHOR` | `R-LABEL-ANCHOR, R-SAME-INSTANT` (spurious) |
| L2b | refusals | `R-LABEL-ANCHOR, R-POSTHOC-CAPTURE` | `R-LABEL-ANCHOR, R-POSTHOC-CAPTURE, R-SAME-INSTANT` (spurious) |

Root causes and the fixes (implementation changed, oracle NOT changed):

1. **C1 / missing `R-FUTURE-CLOCK`.** The counting loop short-circuited on the
   first violated judgement (`continue` after the empty-hash check), so the
   future-clock judgement was never reached for C1's entries. A report must name
   *every* raw-record violation, not the first one hit. Fix: judgement detection
   is now evaluated per entry and independently of whether the entry is counted
   (`_eligible`), and each judgement keeps its own single marked `if` line so the
   mutation proof can still revert exactly one judgement.
2. **L2/L2b / spurious `R-SAME-INSTANT`.** Duplicate-instant detection compared the
   union of `sampled_at` and `captured_at`; with a legitimate zero-second capture
   latency every label produced two identical stamps. "One instant is not a
   chain" is about the *sample* instants. Fix: the duplicate check uses
   `sampled_at` only; the future-clock check still covers sampled and captured
   stamps.

Note on evidence hygiene: the intermediate report file was overwritten in place by
the corrected re-run of the same command in the same directory, so only this
narrative plus the final `cases_report.json` survive. It is recorded here rather
than reconstructed as a file, because reconstructing it would be fabrication.
