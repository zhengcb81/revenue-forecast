# RF source clock — implemented interface

Implementation: a001995a26a6b9b1a294ae62bb4fe57eeac6ca51; base e688b0a2; engine **4.1.1**, policy **source-clock/1**. Scope is source information eligibility and actual event responsibility, not a fresh research conclusion.

## Pure policy and consumers

`scripts/contracts/source_clock.py` performs no IO, wall-clock lookup, source access, DB or signature issuance.

```python
qualify_source_information(*, source_sha256: str | None,
    published_date: str | None, as_of: date,
    availability_evidence: dict | None = None) -> InformationEligibility
source_information_eligibility(source: dict, as_of: date) -> InformationEligibility
validate_source_events(*, eligibility: InformationEligibility,
    original_retrieved_at=None, current_read_at=None, capture_date=None,
    claim_verified_date=None, host_timestamp=None) -> None
```

`InformationEligibility` is an immutable validation-local fact (`available_by`, `basis`, `source_sha256`, `published_date`), not persistent research state. Known publication after as-of is refused even when an earlier proof is supplied. Known publication at/before as-of permits real later retrieval/read/capture/check. Unknown publication needs reliable exact-SHA availability at/before as-of; it stays null and cannot be manufactured from mtime/retrieved_at. Raw changes cannot retain an old proof.

Named refusals: `source_publication_after_asof`, `source_availability_unknown`, `source_availability_after_asof`, `source_availability_version_mismatch`, `source_availability_invalid`, `source_clock_invalid_date`, `source_clock_conflict`. Conflicts include the field names and actual values. UTC full read timestamps remain required; date-only historical host receipts remain readable. Capture/access day must match the bound actual read/host event; claim verification cannot precede its bound capture. Original retrieval is retained separately; original retrieval later than current read or before known publication is refused as a contradiction.

Boundaries:

- `company_wiki_source_reader_v2`: strict public binary bytes/receipt/manifest, information qualification and actual-event consistency.
- `company_wiki_source_v2`: actual `read_at` sets the new capture/access date and full host timestamp. Original `manifest.retrieved_at` stays original/null.
- `contracts.document.validate_sources`, `contracts.evidence.validate_source_capture`, `contracts.document.validate_evidence_claims`: the same policy for source/capture/claim. No future-actual/backtest eligibility is removed.
- `source_narrative_context.consume_narrative_input`: new automatic claims use the actual UTC narrative read/check date; deep-copy input, one reader invocation, source/locator/SHA/role/formula dependencies preserved.
- `research.input_evidence._bind_narrative_span`: narrative source capture uses actual read; existing narrative protocol has no prior availability DTO, so unknown publication remains a named gap.
- Explicit offline `company_wiki_source` legacy helper applies known-publication eligibility and retains recorded historical capture events; it does not invent a new read event or become production fallback.

## Optional 2.2 public proof capability

Default source receipt **2.1** and SourceRef **2.0** remain unchanged. RF entry points `prepare_source_result`, `prepare_source`, `prepare_registered_source_result`, `_prepare_source_ref_v2`, and `open_source_version_v2` accept `source_reader_receipt_version="2.1" | "2.2"`. CLI: `--source-reader-receipt-version 2.2`. Invalid capability is refused before FF/upstream; no exception-based upgrade/retry.

The declared 2.2 reader invocation adds public producer `--include-availability-evidence`. Bare receipt gets exactly one extra field `availability_evidence`; manifest fields and the `(body, bare_receipt, manifest)` return remain unchanged. Unsolicited 2.2 under default2.1, unknown schema and extra fields are refused. Non-null proof is retained unchanged in the source plus existing trace; the source proof must match its public2.2 receipt/ref/manifest/current raw SHA.

```json
{"schema_version":"source-availability-evidence/1",
 "source_sha256":"<exact raw SHA>","available_by":"<ISO date>",
 "basis":"prior_verified_capture | primary_archive",
 "evidence_ref":"<pathless existing proof ref>","locator":"<existing proof fields>"}
```

**Producer dependency:** MAIN CWP ea76998c (CI37888084960), exclusive `source_availability.py` + `source_reader_cli.py`. Current actual resolver returns `prior_verified_capture` only from verified canonical DownloadReceipt `.source.json`; `primary_archive` is an interface enum, not an implemented resolver/claimed actual proof in this package. Naked sidecar, local possession or unrecognized archive stays null. RF only structurally validates and consumes the declared public producer; it does not open provenance paths or manufacture credentials. This package's unknown+proof cases are synthetic responsibility fixtures; the real three-company validation uses known publication/default2.1.

## Bounded caller deadline

`source_preparation.py` owns one finite positive monotonic caller budget. FF, exact raw open and optional narrative read receive the **remaining** time; the old hard `min(timeout,30)` caps are removed. Expiration is refused before the next stage (`source_preparation_deadline_exhausted`); zero/nonfinite budgets are refused before upstream. `source_narrative_context` already forwards its explicit caller budget. The existing bounded transport still enforces timeout and process-tree teardown. No batch/model restart, retry, unbounded timeout or CWP change is added.

## Emit / validate matrix

| Schema | New formal emit | Existing output/snapshot metadata | Semantics reproduction |
| --- | --- | --- | --- |
| 3.7, opt-in3.8 | 4.1.1 | documented4.1.0 or4.1.1; unknown refused | 4.1.0 frozen behavior uses pinned e688b0a2 runtime; 4.1.1 uses source-clock/1 |
| Prior schemas | prior existing registry unchanged | prior documented emit matrix unchanged | pinned emitting runtime where required |

A documented old metadata pair does not relabel an old artifact as newly validated. No frozen input/capture/claim/output/snapshot byte is rewritten. New semantic repair is a new engine. Five original full-result golden hashes retain their4.1.0 meaning; the old lock runs with its pinned runtime, rather than rebaselining all goldens. The actual audit reproduced all five original hashes and compared current nonmetadata fields exactly (unchanged).
