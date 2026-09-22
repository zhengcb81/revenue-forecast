# decision.md — PROMOTION-PREP a20260922-01

## Decision
Produce a read-only promotion execution manifest (source→target with LIVE hashes, card
conditions, verification citations) for third-batch items B-1..B-6. NO promotion, NO tests,
NO git writes, NO production writes. Complete TABLE > exhaustive cells (parent directive).

## What was done
1. Froze oracle.md + handoff.json skeleton on first call (status=review_pending,
   disclosure_adaptation=unmapped, accuracy=unproven, implementer_signed=false).
2. Read only §十七 B-table of OWNER_DECISIONS.md.
3. Per item: grepped card carriers (binding.json pins, changes.diff '^diff/---' headers,
   handoff scope/gaps/conditions lines) — never full-read large files.
4. LIVE-hashed every cited source and target; appended each manifest block immediately.
5. Skipped `git apply --check` per step 5 → all rows marked UNRESOLVED-verification;
   hashes first, diffs second, ordering notes last.
6. Minimal binding.json / decision.md / commands.json / recovery/README.md written.

## Key judgements
- B-3 source = I-14-D `iso/product_narrow_r6` (r7 = record-fix only; r6 grants stand).
- B-4 targets = CW conftest.py + tests/contract/test_short_basetemp_convention.py, both
  ABSENT live ⇒ new-file semantics; R1 supersedes I-14-F originals (byte ladder measured).
- B-6a I-14-F must NOT be promoted (superseded by R1); B-6b natural_window production
  target UNRESOLVED (not found in either repo); B-6c carries E1E7-registered E-flips.
- Every hash in the manifest was measured in this attempt; hint values were treated as
  claims and re-verified (B-5 before-hints and B-1 pins matched live; B3 prod matched).

## Not decided here
Any promotion, execution authorization (E-4), register closure, or acceptance — all remain
owner/independent-reviewer calls. This card signs nothing.
