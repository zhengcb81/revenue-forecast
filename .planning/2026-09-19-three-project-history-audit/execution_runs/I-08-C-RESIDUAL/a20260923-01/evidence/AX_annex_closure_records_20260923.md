# AX annex closure records — dated 2026-09-23 (I-08-C-RESIDUAL / a20260923-01)

Author: closure agent (not a reviewer verdict). Each section is the dated
append/annotation that discharges the item's demanded record; measurement domain =
current on-disk bytes + this attempt's `evidence/*.json` runs (c8/c9/c10).

## AX-1 — F4/F5 (the conditions block's two evidence-completeness defects) — DISCHARGED

Condition text (reviewer_report.md §9.5, verbatim): *"F4/F5 — preserve raw run outputs
under distinct labels, and give `decision.md` a freeze-time hash, in the next attempt's
protocol."*

- The "next attempt" is this one. Protocol compliance here: every judged run has its own
  distinct raw label under `evidence/` (`c0_…`, `c1_…` … `c12_…`, `E_L2_run_fixed.*`,
  `E_L2_run_m6.*`, including the preserved first `c9_…` run and its refined `c9b_…`
  re-run — no output overwritten); `handoff.json` records every deliverable hash at
  handoff (freeze-time hashing applied to all deliverables, incl. `decision.md`).
- Fresh re-verification of the F4 historical question (`evidence/AX1_f4f5_checks.json`):
  the surviving `before/b1_unfixed.stdout.txt` (`58863ffb…`, 30580 B, UTF-16) **decodes
  to the r1 RED run "10 failed, 2 passed in …"** (2 `PASSED`, 10 `FAILED` node lines).
  This re-confirms the register §22/补1 erratum (F-REV-B1P-01): the reviewer's F4 claim
  "the r1 RED run's raw output is not independently auditable" was FALSE as to stdout —
  the true permanent historical gap is only the r1 TEST FILE (18236 B / `e6c0949c…`).
- F5's substantive protection re-verified: B1-PREREQ `freeze.json` 24-entry hash chain
  present (chain head recorded) + `SHA256SUMS.txt` (31 lines) + `SHA256SUMS_r2.txt`
  (23 lines). One measured note: the literal marker "hash-pin" was NOT found in the B1
  oracle text by my scan needle (`b1prereq_oracle_hash_pin_policy_present: false`) —
  the future-freeze policy wording there differs from my needle; recorded as measured,
  not smoothed over.

## AX-2 — F6 (disclosed residual) — PERMANENT LIMITATION RECORD (no action)

Condition text (verbatim, §6 F6): *"F6 (INFORMATIONAL, disclosed residual) —
`result_sha256` is provably unbindable and remains unbound … **No action required**, but
the r3 text should stop listing `result_sha256` as a record field (F1) so the residual is
unambiguous."*

Recorded status: **permanent, provable limitation — no action**, now unambiguous because
L1's corrected source-of-truth (oracle.md §2.1) states the field set without
`result_sha256` and pins it in the request to the sentinel. Clarification carried from
the parent's F6 ruling (REMEDIATION_REGISTER.md §26 ruling 3): rewrite **with consistent
recomputation** ⇒ both layers ACCEPTED (the original F6 measurement, unchanged, no
erratum); rewrite **without** recomputation ⇒ receipt ACCEPTED / forecast REJECTED
(`revenue_report.py:343-347+507-509`) — a strengthening, not a correction.

## AX-3 — F7 (adjudication residual) — STATUS RECORD + (a)/(b)/(c) DECISION

Condition text (verbatim, §9.4): *"F7 — record REM-02 as a documented limitation with
the caller-side trap still open, and decide (a)/(b)/(c). Do not describe REM-02 as fully
closed while the only runtime artefact is a class nobody raises."*

1. **Status recorded (verbatim demanded string): REM-02 = "documented limitation,
   consumer-side guardrail not yet in place"** — NOT "closed". (Consistent with the
   parent's REM-46 ruling: "已裁定可接受；残留（无运行时信号）须跟踪为'已文档化限制、
   消费侧护栏未就位'".)
2. **Decision (a)/(b)/(c) = (a) + follow-up item (c)**, adopting the reviewer's own
   recommendation ("My recommendation: (a) plus a follow-up item"):
   - **(a) chosen**: bump `publication_receipt.receipt_schema_version` so consumers must
     opt in to the `publication_attestation` contract (the I-08-A OPEN-D4 question).
   - **(b) rejected**: a one-time `warnings.warn(..., PublicationReceiptOnlyWarning)`
     contradicts the frozen design decision (B1 oracle r1 §3.5(c): no runtime warning,
     frozen before any run) and the clean-run expectations of `test_zr701`/`test_zr705`.
     Measured limitation of this very rationale (honest): my scan found **no explicit
     warnings-related assertion** in those two test files (`evidence/c9b_…`, run-1
     `asserts_clean=false`); the (b)-cost therefore rests on the frozen design decision
     and warning-strict run configurations, and is NOT independently re-verified here.
   - **(c) folded in as the follow-up item**: a follow-up card that renames/deprecates
     `validate_publication_receipt` remains the tracked consumer-side guardrail.
   - Implementation of (a)/(c) is a publication-contract change ⇒ professional review
     per START_HERE.md 「必须交专业审查的边界」 + product-card track. Until then the
     caller-side trap is OPEN by explicit record (marker class exported, never raised —
     re-measured `warn_call_sites=[]` on the promoted bytes).
   Authority: reviewer F7 recommendation + owner 「发现的缺陷都要全部修复」/「fail的全部
   要修复」 chain + REM-46's tracking requirement. This record decides the disposition
   and the tracked label; it does not implement the schema bump.

## AX-4 — §3.2 residual (input-document re-anchoring) — ACCEPTED-BY-DESIGN RECORD

Condition text (verbatim, §3.2): *"Residual (recorded, not a defect of this card): an
attacker who edits the embedded `input_document` *and* re-anchors `input_sha256` presents
a hash-consistent artifact whose only remaining anchor is the caller's own copy of the
original input — `validate_published_forecast(result, original_input)` and
`verify_input_binding` reject it. That is the pre-existing input-binding contract, not
something REM-03 weakened …"*

Recorded status: **accepted-by-design limitation of the pre-existing input-binding
contract — no action**; explicitly not a defect of the B1 card and not reopened here.
Carried verbatim into this attempt's handoff `carried_findings`.

## AX-5 — AUDIT-DESIGN D1b/D1c (B1 evidence-entry naming) — APPEND-ONLY ERRATUM

Erratum (per AUDIT-DESIGN addendum A4 disposition "追加式勘误该 evidence 条目或如实标注
'未产出'，不得事后补文件冒充当时证据"):

- `B1-I08C-product-fixes/a20260921-01/commands.json:27,35` register
  `before/production_anchors.txt` as argv output and as an evidence artifact.
  **Fresh fs-scan (`evidence/AX5_d1b_fsscan.json`) re-confirms: that file was NEVER
  produced** — 0 hits in the whole plan tree and in the RF repo; only the `.json`
  sibling (`before/production_anchors.json`) exists.
- Corrected evidence entry (this record is the append-only erratum carrier; B1's sealed
  `commands.json` is NOT edited): `before/production_anchors.txt` = **未产出（仅 .json）**.
  The file is NOT fabricated after the fact. `commands.json:38`'s own near-confession
  ("the anchors were first captured by an inline hashing step whose raw output is
  before/production_anchors.json") is consistent with this reading.
- D1c naming family (same disposition shape, routed to BOOKKEEP-REPAIR per register §74):
  `B1-PREREQ oracle.md`'s `evidence/final_integrity_check.txt` vs actual
  `final_integrity_check.stdout.txt` etc. — registered as name-drift, substance present.
