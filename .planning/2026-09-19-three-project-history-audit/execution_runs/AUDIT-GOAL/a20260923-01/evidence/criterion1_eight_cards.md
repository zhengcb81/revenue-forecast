# Evidence: Criterion ① — 8 in-flight cards → 8 attempt dirs, closure + landing trio

Measured independently by AUDIT-GOAL on 2026-09-23 (read-only). All hashes below were
re-computed by the auditor with `Get-FileHash -Algorithm SHA256` (PowerShell) against the
bytes on disk; "pin_match=True" means the recomputed digest equals the recorded sidecar pin.

| # | goal item | card / attempt dir | handoff status carrier | reviewer verdict (independent reviewer) | review.md | handoff | qualification.json | sidecar pin re-hash |
|---|---|---|---|---|---|---|---|---|
| 1 | GATE-TIMEOUT-1200 | GATE-TIMEOUT-1200\a20260922-01 | handoff.json `status=accepted_scoped` | reviewer_report.md L6 `- **Verdict: accepted_scoped**` | yes (9432 B) | yes | evidence\GATE-TIMEOUT-1200\qualification.json (15182 B) | `2a66abae6f04…` pin_match=True |
| 2 | DW15-prune-repair | DW15-prune-repair\a20260922-01 | handoff.json `status=accepted_scoped` | reviewer_report.md `## RULING (reviewer, three-state): accepted_scoped` | yes (3445 B) | yes | evidence\DW15-prune-repair\qualification.json (4202 B) | `a9b9076f731b…` pin_match=True |
| 3 | B5-fix-g1a-g3 | B5-fix-g1a-g3\a20260922-01 | handoff.json `status=accepted_scoped` | reviewer_report.md `- **Verdict**: **accepted_scoped**` | yes (8073 B) | yes | evidence\B5-fix\qualification.json (11354 B; note dir name `B5-fix`) | `69ea3b033d22…` pin_match=True |
| 4 | I-08-C oracle 重冻 | I-08-C\a20260919-01 | handoff.json `status=accepted_scoped` | reviewer_report_r2.md `## VERDICT: accepted_scoped` (scope explicitly includes "the append-only oracle re-freeze (revision r4)") | yes (17098 B) | yes | evidence\I-08-C\qualification.json (5882 B) | `ee5046a5bafb…` pin_match=True |
| 5 | I-14-F-R1 150/60 | I-14-F-R1\a20260922-01 | handoff.json `status=accepted_scoped` | reviewer_report.md `## VERDICT: **accepted_scoped**` (applies owner §16 E-1 「E-1: 150/60」) | yes (6029 B) | yes | evidence\I-14-F-R1\qualification.json (7969 B) | `8ce87ef6d310…` pin_match=True (rich-format sidecar: `sha256: 8ce87ef6d31087da65e556be4736a8c8f7734594575cf868149df383e5f62a1c`, 15841 B report = recomputed digest exactly) |
| 6 | INVEST-CORE 护栏 | INVEST-CORE-ATTEST-GATE\a20260922-01 | handoff.json `status=accepted_scoped` | reviewer_report.md `## VERDICT … three-state: accepted_scoped` (reviewer independently re-executed RED 7 failed/3 passed, GREEN 10 passed, mutation M1) | yes (12968 B) | yes | evidence\INVEST-CORE-ATTEST-GATE\qualification.json (18727 B) | `09b4e13ec1bd…` pin_match=True |
| 7 | I-14-E-APPLY 重跑 | I-14-E-APPLY\a20260921-01 | handoff.json `status=accepted_scoped` | reviewer_report.md `- **Verdict**: **accepted_scoped**** (Q1 ruled option (ii); scope language required) | yes (5358 B) | yes | evidence\I-14-E-APPLY\qualification.json (3220 B) | `feaec562df3f…` pin_match=True |
| 8 | I-14-D r6 复审回收 | I-14-D\a20260919-01 | handoff_r6.json `status=accepted_scoped` (`status_before_bookkeeping_fix=review_pending`; top-level handoff.json stays historical `review_pending` by append-only design) | reviewer_report_r7.md `## 0. VERDICT` L11 **`accepted_scoped`** (r6 report was `changes_required` with §9 fix list; r7 confirms the 4 fix items done) | yes (31094 B) | handoff.json + handoff_r3..r6.json | evidence\I-14-D\qualification.json (12090 B) | `cc6da8d3878d…` pin_match=True; r6 report `f1c9761d8067…` pin_match=True |

## Independent hash chains re-measured for I-14-D (deepest of the 8)

- reviewer_report.md (r1) recomputed = `499d91acf06a67e2f7dd06d4a5af6569b5b92a6e4b3b77adda57b739eaa03d2b` = the digest quoted in review.md L10 (match).
- reviewer_report_r6.md recomputed = `f1c9761d80679fb9f0258ac7eb786557fc9296762764183883e1f7b22262a74f` = its sidecar (match).
- reviewer_report_r7.md recomputed = `cc6da8d3878dbd942bc6d47bdd750913d1c0646742e22c737ffe73191f610076` = sidecar AND = handoff_r6.json status_authority.sha256 (match).
- review.md append-only proof re-measured by auditor (byte-prefix SHA-256):
  - first 26172 B → `163cb939a11da0f245823ad24bb3ad1949890c02afced41ea53308343a58f373` = claimed post-r7-append pin (MATCH)
  - first 22100 B → `8a2ff101b5501a9de93651ff1988fab339d76af779982cbe1c398b734fc28ae7` = claimed r6 pin (MATCH)
  - current file = 31094 B / 416 lines; the post-r7 append is the `## r7 verdict` block at L397–L416 (transcription-only, unsigned).
- review.md L412 discloses carried NOT-closed items (`F-REV-R3-02/03/05/06..10`, `F-REV-R4-02`, `F-REV-R5-03..08` "registered-unaddressed") — routed, not silently dropped.

## Verdict for criterion ①

All 8 goal items map 1:1 to 8 attempt dirs; every one carries an independent-reviewer
`accepted_scoped` verdict (item 8's verdict is the r7 carrier; the r6 round verdict was
`changes_required` and its §9 fix list is registered as fixed in the r7 record), a review.md,
a handoff carrier and a qualification.json, with all 8 reviewer-report pins re-verified
byte-exact by the auditor. Note: for item 8 the acceptance carrier is `handoff_r6.json`;
the top-level `handoff.json` remains the historical `review_pending` record by declared
append-only design (status_authority documents the supersession).
