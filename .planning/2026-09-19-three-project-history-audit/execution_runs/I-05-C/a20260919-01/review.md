# I-05-C Review — Verdict Record

Provenance note: the independent reviewer signed the verdict `accepted_scoped` for
I-05-C a20260919-01 (relay recorded 2026-09-20). No separate reviewer report file was
archived in this attempt directory, so this file is the carrier-landing transcription
of the signed verdict and its carried findings; it is written by the carrier-landing
executor, not by the reviewer, and the implementer does not sign acceptance (see P3-3).

## Paste-Ready Verdict Block

```
<!-- REVIEW: I-05-C a20260919-01 -->
<!-- prefix-hash: 4d5cf8c9 (first 8 hex of sha256 over this block's body) -->
<!-- reviewer: independent (not the implementer) -->
<!-- date: 2026-09-20 -->

Verdict: accepted_scoped

Summary:
- Core claim verified: W05C minimal production contract — active DAG D-W05 applied
  (summary→[normalized]; historical markdown compatibility-only), select_artifact_roles
  scoped to requested missing roles + non-reusable ancestors (producer_events excludes
  unrequested downstream dependents), invocation tracking via InvocationTracker at the
  actual call boundary (call counts never inferred from artifact INSERT counts).
- 19/19 W05C tests pass with proven RED→GREEN mutation (initial run: 9 RED / 10 GREEN);
  20/20 I-05-B regression and 11/11 FC-904 regression pass (commands.json, raw_exit_codes
  all 0).
- Requested-role DAG matrix proven: request-only sections/summary do not produce
  unrequested consumer_analysis (requested-role-dag-matrix.json).
- Retry count diverges from artifact count: 2 calls/1 insert, 3 calls/0 inserts,
  4 calls/1 insert (retry-count-vs-artifact-count.json).
- Second reuse proven: re-request of valid artifacts = 0 producer calls
  (second-reuse.json).
- Production repos read-only during the attempt; only CW artifact_dag.py and RF
  scripts/company_wiki_source.py changed within card scope (changes.diff,
  after/source_hashes.json).

Findings (carried):
- P2-1: produce_for_demand is mock-only in tests; D-W05 producer-entry approval
  (2026-09-20) authorizes the real implementation wired to existing CW producers via
  service.py (CatalogConfig/CatalogStore), but it is not yet implemented (GAP-1)
- P2-2: consumer_analysis producer absent; W05C-N3 proves missing/unsupported handling
  only, real LLM capability unverified; the role stays explicitly blocked on the RF
  consumer_analysis owner supplying an entry — no green sample may be fabricated (GAP-2)
- P3-1: InvocationTracker event schema (role/producer_name/call_status/attempt_number/
  error/artifact_id) still needs reviewer approval for production persistence (GAP-3)
- P3-2: Shared audit-harness limitation carried from plan findings.md P2-1:
  scripts/run_card.py never validates cases.json `expected`, so negative-case expected
  fields are unconstrained text; registered as known shared-harness limitation, frozen
  attempts not re-opened
- P3-3: Evidence provenance: the reviewer's full report is not archived in this attempt
  directory; review.md is the carrier-landing transcription of the owner-relayed signed
  verdict

Unverified:
- Real produce_for_demand production path (CatalogConfig/CatalogStore integration) — P2-1
- Real LLM capability for consumer_analysis — P2-2
- InvocationTracker schema production persistence — P3-1
```

Carrier-landing note: this verdict lands in `handoff.json` (status=accepted_scoped,
status_before_bookkeeping_fix=review_pending, status_authority block) and in
`evidence/I-05-C/qualification.json` (formula.state=accepted_scoped,
disclosure_adaptation=unmapped, accuracy=unproven). All carried findings are
append-only; no frozen artifact is touched by this landing.
