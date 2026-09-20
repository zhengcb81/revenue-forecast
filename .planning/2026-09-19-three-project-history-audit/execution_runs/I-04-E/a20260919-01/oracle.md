# Oracle: I-04-E — Preserve nested errors and real side-effect counts

Frozen BEFORE implementation. All expectations hand-derived from reading production code.

## 0. Baseline

- iso/fetch_filing.py sha256: 046CC7DC4E3FF2F4F59BE05DEF8961A85A12E6290ADEF43A3C53103C63B9D088 (48392 bytes)
- iso/filing_contracts.py sha256: 2D1B2E3374F1D0C255F94303D208F8657F54C9C32B3428E424F43E6A81DDC457 (22631 bytes)
- Python: 3.13.9, pytest 9.1.1
- Frozen: 2026-09-19

## 1. Machine envelope contract

### P1: Full structure parsed before truncating human message
- **Input**: company-wiki exits non-zero with stderr = JSON `{"error_type":"db_timeout","error":"<3000 char message>","request_id":"R1","stage":"resolve"}` + trailing padding to >2000 chars
- **Expected**: FilingFetchError.code == "db_timeout", .stage == "resolve", .retryable == True. The error message MAY be truncated for human display, but the structured fields are extracted from the full stderr before any truncation.
- **Invariant**: `error_code` in the JSON envelope matches the upstream `error_type`, not a derived/compressed code.

### P2: Long stderr with JSON at the start
- **Input**: stderr = `{"error_type":"catalog_locked","request_id":"R2","stage":"identify"}\n` + 3000 chars of traceback
- **Expected**: code == "catalog_locked", retryable == True. The trailing traceback does not cause misclassification.

### P3: Unknown/malformed stderr
- **Input**: stderr = "not json at all"
- **Expected**: code == "fatal", retryable == False (fail closed)

## 2. close-gap non-completed exit preserves original cause

### P4: close-gap returns status=failed with retryable upstream error
- **Input**: close-gap CLI returns `{"status":"failed","reason":"provider_refused","error_code":"upstream_error","retryable":true,"stage":"close-gap","request_id":"R3"}`
- **Expected**: FilingFetchError.code == "upstream_error", .retryable == True, .stage == "close-gap". NOT wrapped as "gap_not_closed".

### P5: close-gap returns status=timeout
- **Input**: close-gap CLI returns `{"status":"timeout","reason":"deadline_exceeded"}`
- **Expected**: FilingFetchError preserves the timeout status. code reflects the upstream cause, not a generic "gap_not_closed".

## 3. Real side-effect counting at each subcall

### P6: Failure path also records download events
- **Input**: resolve returns a handle with resolution_envelope.download_events=1, then handle validation fails
- **Expected**: stats["downloads"] == 1 even on the failure path. Currently only recorded on success.

### P7: Dedup prevents double-counting on retry
- **Input**: First attempt gets download_events=1 from envelope, fails. Retry gets same envelope.
- **Expected**: stats["downloads"] == 1 (not 2). Dedup key is the request_id from the envelope.

### P8: Unknown download count not written as 0
- **Input**: Handle has no resolution_envelope (N-1 wiki)
- **Expected**: stats["downloads"] is NOT set to 0. It remains at its previous value or is marked as unknown.

## 4. Four required fixtures

### F-E1: DB lock retryable (nested error, cause >2000 chars)
- **Input**: `db_timeout` error with `request_id=R1`, cause message >2000 chars
- **Expected machine envelope**: `{"error_code":"db_timeout","retryable":true,"stage":"resolve","request_id":"R1"}`. Human message may be truncated. Retryable=True.
- **Retry behavior**: auto-retried by `_run_company_wiki_json_retry` (db_timeout is in _CATALOG_RETRY_CODES)

### F-E2: HTTP 403 with upstream retryable=true
- **Input**: Provider returns 403. Upstream marks retryable=true. Freeze policy prohibits auto-retry this attempt.
- **Expected**: error_code preserved as upstream code, retryable=true. NOT rewritten to retryable=false. Auto-retry count=0 for this attempt (freeze policy), upstream call count=1.
- **Also**: local request schema error has independent code and stage, does NOT masquerade as catalog lock.

### F-E3: fetch=1/raw=1/register=0 partial failure
- **Input**: Download succeeds (fetch=1, raw_saved=1), registration fails (register=0). Same event envelope read again.
- **Expected**: Failure result reports already-occurred side effects. Cumulative does NOT double. Does NOT return capture_ready.

### F-E4: Retry after partial failure, only registration succeeds
- **Input**: After F-E3 failure, retry. Only registration succeeds. Existing file from prior attempt.
- **Expected**: Both attempts report new fetch=0 (no re-download). Partial failure recovery preserves same raw hash. Call counts reconcile with process spy.

### F-E5: Non-JSON/unknown error or missing event count
- **Input**: Unknown error format, or event count field missing
- **Expected**: Explicit protocol failure / count unknown. Does NOT fabricate structure or 0. Does NOT auto-retry loosely.

## 5. Exit code table

| Case | Expected exit code | Expected business result |
|------|-------------------|-------------------------|
| F-E1 (db_timeout) | 2 | error envelope with code=db_timeout, retryable=true |
| F-E2 (403) | 2 | error envelope with upstream code, retryable=true |
| F-E2 (schema) | 2 | error envelope with code=request_error, retryable=false |
| F-E3 (partial) | 2 | error envelope with side-effect counts, not capture_ready |
| F-E4 (recovery) | 0 | capture_ready with reconciled counts |
| F-E5 (unknown) | 1 or 2 | explicit unknown, no fabricated fields |

## 6. Mutation queue (for future proof)

- M1: Remove cause chain preservation -> F-E1 loses nested error info
- M2: Remove close-gap status preservation -> F-E2/F-E4 use generic gap_not_closed
- M3: Count downloads only on success -> F-E3 loses side-effect evidence
- M4: Allow double-counting on retry -> F-E4 counts inflated
- M5: Write 0 for unknown downloads -> F-E5 fabricates evidence
