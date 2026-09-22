# Parent adjudication of round-1 live scan (transcribed, 2026-09-22)

Source: parent agent session-bfecd191-fbc3-4a66-8ed1-6562479bf102 message to this
attempt (transcribed here verbatim-in-substance so the ruling survives independent
of the session transcript). This is the OWNER's ruling on the 214 round-1
detections in `evidence/live/findings_file_line_list.txt`; this attempt does not
adjudicate plan-file text itself.

## Ruling

1. **True positives = 0 lines** (domain of the ruling: one line-by-line reading of
   all 214 detections, performed by the parent).
   Every line's universal marker either
   - (a) already carries a same-line count/subject/enum qualifier (e.g.
     三个请求全部 / 八代全部 / 11 条 case 全部 / 四前提全部 / 六项负控全部 /
     剩余 ≈24 张卡全部 — semantically already the REM-79 scoped form), or
   - (b) is an existential negation (没有 PyYAML / 没有卡内裁决区) — the
     known-false-positive shape declared in oracle.md §10, or
   - (c) is an identifier / frozen-quote match (`fix_A_only` 的 `_only` 后缀;
     quotation of frozen rule text such as "every case's...").
2. **Conclusion: the 214 are dominated by lexicon gaps, not text defects in the
   plan files.** Neither side edits files to suit the checker: this attempt is
   forbidden to touch plan files, and the owner will not reshape prose to satisfy
   a checker. The correct path is the protocol path — an appended oracle
   correction.
3. **Instruction:** append oracle CORRECTION 1 (append-only, prefix-proven),
   adding same-line domain patterns:
   - **D8 counting qualifier**: numeral+classifier (三个/八条/11 条/≈24 张/四张卡…)
     co-occurring with the universal ⇒ domain satisfied;
   - **D9 subject/enumeration qualifier**: the universal's subject carries a
     limiting modifier (剩余…卡全部 / 新实施计划仍全部待实施) or the universal is
     followed by an explicit enumeration (全部 M01–M31 + I-00…) ⇒ domain satisfied;
   - **D10 registration** of the third known false-positive class: identifier-internal
     `only` (`fix_A_only`) and quoted frozen-rule lines — the implementer chooses
     the handling rule (skip-with-annotation vs keep-flagged) and must state the
     reasoning inside the correction.
4. After the correction: re-run GREEN + the live scan; report the new detection
   count (expected: large drop) plus an old/new diff
   (`evidence/live/round2_diff.txt`): lines GONE from the 214 = D8/D9 hits;
   lines REMAINING = the narrowed true-positive candidate set for the owner to
   re-adjudicate. RED need not be redone (adding domain patterns loosens the
   domain decision, not the detection surface) — but the correction must argue
   this explicitly, because the frozen contract forbids silent widening.
5. Re-run any mutation whose expectation depends on the changed domain patterns
   (re-running all three preferred).
6. Carry into evidence + handoff: the round-1 214 list, this ruling's key points
   (true-positive 0 + the three false-positive classes), CORRECTION 1, and
   round2_diff.

## Status of the delivered core (parent's words)

The core delivery (RED domain-blind arm must fail; GREEN exact 4/0; 3 mutations
pass; oracle self-scan 0 violations; freeze pins re-verified PIN-OK by the
parent) is **quality-confirmed**. This instruction is a closing enhancement, not
a reversal.
