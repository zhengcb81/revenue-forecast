# Frozen optional interface (RED contract)

Existing span binding fields unchanged. Optional nested field:

```json
{"summary_use":{"schema_version":"revenue-summary-use-binding/1","summary_claim_id":"actual-id-from-context","research_reason":"A real bounded research explanation"}}
```

The nested object has exactly these3fields. Text/hash/quality/used status/parameter metadata cannot be supplied in it. Non-empty trimmed reason is at most2048characters. Selected claim ID must be unique in the once-read verified context.

Only an actual successful span/claim/used-parameter/formula dependency can add receipt.summary_use. It has schema revenue-summary-use/1, status used_in_parameter_rationale, actual narrative_ref, claims_sha256, original quality/selection/draft status, optional assessment hash and semantic/subfact observations, and entries. Entry derives summary claim ID/hash/type/modality/needs_review/support/context, captured source reference, original selected span, RF claim/parameter/formula refs, closed citation identity, and the supplied research reason. No summary.text is put into RF evidence excerpt.

Summary support/context must equal the chosen existing citation_view partition, with all IDs transported and same captured parent. Ungrouped single-support/no-context may use the existing standalone case; legacy group-only/multi-span without partition is named closure unavailable. These are scope-proof errors, not coverage or review-status permission gates. Partial/needs_review is retained, not a blocker.

Without nested summary_use, old binding/receipt bytes and evidence claim shape are unchanged; read-only/empty bindings never create summary-use or used status.
