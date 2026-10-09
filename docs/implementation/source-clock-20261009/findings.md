# Findings

Approved input: CWP phase6/asof_clock_diagnosis/W01_source_clock.md and INTERFACE.md.

Exact fixed71 evidence: three markets BLOCKED with source capture is outside as_of_date; raw byte replay passed. Adapter uses original retrieved_at or current read_at then applies historical asof ceiling; duplicate reader/adapter/capture/claim gates, and auto narrative claim writes verified_date=as_of. CWP existing qualify_source has publication-only cutoff semantics. Original retrieval is provenance, current read/capture/check is actual event, information availability is historical eligibility.

Current SourceRef2.0/read receipt2.1/capture1.0, canonical forecast3.7 opt-in3.8, RF skill4.1.0. Optional receipt2.2 adds only top-level availability_evidence; default2.1 and manifest fields unchanged. Producer implementation belongs MAIN. No raw proof invented; missing real proof remains unknown gap.

Formal release: engine4.1.1/source-clock/1, schemas3.7/3.8 unchanged. The fixed-cutoff qualification uses known exact-version publication first; unknown requires opt-in public2.2 reliable availability. SourceRecord optional proof must match public2.2 receipt/ref/manifest/exact SHA, not a researcher-authored bare date. Actual original retrieval/current read/current capture/claim verification remain distinct events. Captured_date follows current real read_at, not original retrieved_at or historical asof.

Remaining-deadline defect was in the owned source_preparation.py raw and narrative public reads (`min(timeout,30)`). source_narrative_context already forwarded an explicit caller timeout; the bounded transport already rejects invalid/nonfinite timeouts and kills timed-out process trees. Fixing orchestration removes the cap and shares one monotonic deadline across upstream stages, without rewriting transport or CWP producer.

Receipt2.2 transport defaults2.1 unchanged. RF explicit configuration is source_reader_receipt_version="2.2" or CLI --source-reader-receipt-version 2.2; standard reader translates to --include-availability-evidence. MAIN producer dependency ea76998c/CI37888084960. Current producer emits prior_verified_capture only after verifying existing exact-version canonical DownloadReceipt provenance; unsupported/naked/local-only proof returns null. No actual unknown-source historical proof was manufactured in this package. Unknown protocol cases are synthetic unit fixtures, not actual-company PASS.
