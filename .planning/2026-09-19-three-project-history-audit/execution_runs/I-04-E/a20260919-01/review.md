# Independent Review: I-04-E — Preserve nested errors and real side-effect counts

**Reviewer**: Independent (adversarial), MiMo-v2.5-pro subagent  
**Date**: 2026-09-19  
**Attempt**: a20260919-01  
**Verdict**: `changes_required`

---

## 1. Recomputation Log

### 1.1 Production Hash Verification (from disk, NOT trusted from handoff)

| File | Expected Hash | Actual Hash (Get-FileHash SHA256) | Match |
|------|---------------|-----------------------------------|-------|
| `C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py` | `046CC7DC4E3FF2F4F59BE05DEF8961A85A12E6290ADEF43A3C53103C63B9D088` | `046CC7DC4E3FF2F4F59BE05DEF8961A85A12E6290ADEF43A3C53103C63B9D088` | ✅ |
| `C:\Users\郑曾波\Projects\filing-fetch\scripts\filing_contracts.py` | `2D1B2E3374F1D0C255F94303D208F8657F54C9C32B3428E424F43E6A81DDC457` | `2D1B2E3374F1D0C255F94303D208F8657F54C9C32B3428E424F43E6A81DDC457` | ✅ |

**Conclusion**: Production repos are UNTOUCHED. Zero-write constraint satisfied.

### 1.2 ISO Hash Verification (from disk)

| File | Expected (handoff.json) | Actual (Get-FileHash SHA256) | Match |
|------|-------------------------|------------------------------|-------|
| `iso/.../fetch_filing.py` | `ae34814a400aff67239876fa8a3a507f1fd3eb46f157683cc3daa3f9f9602d76` | `AE34814A400AFF67239876FA8A3A507F1FD3EB46F157683CC3DAA3F9F9602D76` | ✅ |
| `iso/.../filing_contracts.py` | `3129e84e43668d1b443734427ad3be6db83aa24d587d2a1c0886653195c3d74e` | `3129E84E43668D1B443734427AD3BE6DB83AA24D587D2A1C0886653195C3D74E` | ✅ |
| `iso/.../test_i04e_envelope_counting.py` | `b2807c497d3c63e3a1ed8ce64369583f71786f311f7ceac5cd6fbe6e09ded711` | `B2807C497D3C63E3A1ED8CE64369583F71786F311F7CEAC5CD6FBE6E09DED711` | ✅ |

### 1.3 Test Execution (independent, from iso/ venv)

| Suite | Expected | Actual | Match |
|-------|----------|--------|-------|
| New I-04-E tests (23) | 23 passed | 23 passed (0.15s) | ✅ |
| Combined (existing + new) | 139 passed, 1 deselected | 139 passed, 1 failed (pre-existing e2e test `test_cli_stdin_accepts_utf8_chinese_query` — requires `e2e_support` module not present in iso; implementer correctly deselected) | ✅ |

### 1.4 Code Change Verification (line-by-line from disk)

**filing_contracts.py changes** (read from iso file):
- ✅ Line 56-57: `request_id: str | None = None` and `cause_chain: list[dict[str, str]] | None = None` params added to `FilingFetchError.__init__`
- ✅ Line 87-94: `self.request_id = request_id` and `self.cause_chain = cause_chain if cause_chain is not None else []` in constructor body
- ✅ Lines 96-123: `error_envelope()` method added — builds full structured dict BEFORE truncating human message at `max_human_message` (default 2000)

**fetch_filing.py changes** (read from iso file):
- ✅ Lines 45-62: `_build_cause_chain()` — extracts `__cause__` recursively with cycle detection
- ✅ Lines 284-326: `_classify_wiki_error()` — now recognizes `upstream_error` (line 319), uses `_try_parse_stderr_json`
- ✅ Lines 329-352: `_try_parse_stderr_json()` — tries full text, then first line only for JSON-at-start-with-trailing-text
- ✅ Lines 355-368: `_extract_upstream_request_id()` — extracts request_id from parsed stderr
- ✅ Lines 371-398: `_extract_upstream_cause_chain()` — extracts nested cause chain from stderr
- ✅ Lines 255-274: `_run_company_wiki_json()` — parses FULL stderr JSON BEFORE truncating human message (line 260-266: classify + extract request_id + extract cause_chain, THEN truncate at line 266)
- ✅ Lines 1184-1224: `_close_gap_and_return_handle()` — preserves original cause/status/retryability instead of wrapping as `gap_not_closed`
- ✅ Lines 732-746: `_normalize_stats()` — initializes `_seen_request_ids` dedup set
- ✅ Lines 749-787: `_record_download_events()` — dedup keys via `_seen_request_ids`, refuses to write 0 for unknown counts
- ✅ Lines 986-1003: `resolve_filing()` — records download events on failure path (before handle validation)
- ✅ Lines 1345-1368: `main()` — uses `exc.error_envelope()` method

### 1.5 Mutation Proof (independently executed)

| Mutation | Action | Test | Expected | Actual | Result |
|----------|--------|------|----------|--------|--------|
| M1 | Remove `cause_chain` from `FilingFetchError.__init__` | `test_fe1_db_lock_retryable_envelope` | FAIL | FAIL | ✅ PASS |
| M2 | Revert close-gap handler to `gap_not_closed` | `test_close_gap_timeout_preserved` | FAIL | **PASS** | ❌ **See P1** |
| M3 | Remove failure-path download event recording | `test_failure_path_preserves_download_events` | FAIL | **PASS** | ❌ **See P2** |
| M4 | Remove `_seen_request_ids` dedup set | `test_fe4_dedup_prevents_double_count` | FAIL | FAIL | ✅ PASS |
| M5 | Write 0 for missing `download_events` | `test_fe5_missing_download_events_not_written_as_zero` | FAIL | FAIL | ✅ PASS |
| M6 | Remove `_try_parse_stderr_json` first-line fallback | `test_envelope_full_structure_parsed_before_truncation` | FAIL | FAIL | ✅ PASS |
| M7 | Remove `upstream_error` from `_classify_wiki_error` | `test_fe2_403_does_not_masquerade_as_catalog_lock` | FAIL | FAIL | ✅ PASS |

---

## 2. Findings

### P1 — M2 mutation proof broken: `test_close_gap_timeout_preserved` replicates logic inline

**Severity**: Medium  
**File**: `iso/filing-fetch/tests/test_i04e_envelope_counting.py`, lines 431-446  
**Observed**: The test replicates the close-gap handler's status-to-code derivation logic INLINE (lines 439-445) rather than calling `_close_gap_and_return_handle`. When the actual function is mutated to always return `gap_not_closed`, this test still passes because it tests its own copy of the logic.  
**Why it matters**: The mutation proof for M2 is invalid. Someone could revert the close-gap handler to the old `gap_not_closed` wrapping and this test would not catch it. The test verifies the LOGIC is correct but not that the PRODUCTION CODE uses that logic.  
**Minimum fix**: Replace the inline logic replication with a test that calls the actual `_close_gap_and_return_handle` function (or the relevant code path) using a mock subprocess that returns a non-completed status with `error_code`/`retryable` fields. Verify the resulting `FilingFetchError` carries the upstream code, not `gap_not_closed`.

### P2 — M3 mutation proof broken: `test_failure_path_preserves_download_events` replicates logic inline

**Severity**: Medium  
**File**: `iso/filing-fetch/tests/test_i04e_envelope_counting.py`, lines 526-560  
**Observed**: The test manually extracts the early envelope (lines 542-544) and calls `_record_download_events` directly (lines 552-557) instead of calling `resolve_filing`. When `resolve_filing` is mutated to remove the failure-path recording, this test still passes because it does the recording itself.  
**Why it matters**: The mutation proof for M3 is invalid. Someone could remove the failure-path download event recording from `resolve_filing` and this test would not catch it.  
**Minimum fix**: Replace the inline logic with a test that calls `resolve_filing` directly with a mocked subprocess that returns a resolution with `download_events=1` but triggers a handle validation failure. Verify `stats["downloads"] == 1` after the call.

### P3 — `test_fe4_different_request_ids_count_independently` assertion is misleading

**Severity**: Low  
**File**: `iso/filing-fetch/tests/test_i04e_envelope_counting.py`, lines 276-298  
**Observed**: The test comment says "Different request_ids: both counted" but the assertion is `assertEqual(stats["downloads"], 1)`. The `_record_download_events` function uses `stats["downloads"] = events` (SET, not ADD), so the second recording overwrites the first. Since `download_events` is always 0 or 1 per the schema, this is functionally correct, but the comment is misleading.  
**Why it matters**: A future reader might expect cumulative counting (sum) based on the comment, but the implementation does latest-value-wins.  
**Minimum fix**: Update the comment to clarify that `stats["downloads"]` tracks the latest resolution's download flag, not a cumulative sum. Or change the assertion to match the "both counted" intent if cumulative counting is desired.

---

## 3. Unverified Items

1. **I-02 error taxonomy**: I-02 has no execution runs. The error taxonomy used here (`db_timeout`, `catalog_locked`, `catalog_busy`, `worker_paused`, `upstream_error`, `fatal`) is derived from existing production code. Cannot verify completeness against I-02 expectations.
2. **I-03-D wiki canonical error/event**: I-03-D not executed. Cannot verify the close-gap CLI response format matches what `_close_gap_and_return_handle` expects.
3. **Real provider testing**: No real provider calls were made. The card requires "真实provider未测必须继续未测" — this is correctly noted as untested.
4. **Close-gap CLI output format**: The implementation assumes the close-gap CLI returns `error_code`, `retryable`, `request_id` fields. Cannot verify against real CLI output.
5. **E2e test `test_cli_stdin_accepts_utf8_chinese_query`**: Requires `e2e_support` module not present in iso. Correctly deselected by implementer.

---

## 4. Verdict Block (paste-ready for review.md)

```
<!-- REVIEW: I-04-E a20260919-01 -->
<!-- prefix-hash: 7a3f... (SHA-256 of this block's content minus this line) -->
<!-- reviewer: independent MiMo-v2.5-pro subagent -->
<!-- date: 2026-09-19 -->

## Verdict: `changes_required`

### Production zero-write: ✅ VERIFIED
- fetch_filing.py: `046CC7DC4E3FF2F4F59BE05DEF8961A85A12E6290ADEF43A3C53103C63B9D088` (unchanged)
- filing_contracts.py: `2D1B2E3374F1D0C255F94303D208F8657F54C9C32B3428E424F43E6A81DDC457` (unchanged)

### Test counts: ✅ VERIFIED
- 23 new I-04-E tests: 23 passed (independently re-run)
- 116 existing tests: 116 passed (1 pre-existing e2e test correctly deselected)
- Combined: 139 passed, 1 deselected

### Code changes: ✅ VERIFIED (11 changes in fetch_filing.py, 2 in filing_contracts.py)
All claimed functions exist at the claimed locations with the claimed behavior.

### Mutation proof: ❌ 2 OF 7 BROKEN
- M1: ✅ Verified (cause_chain removal caught)
- M2: ❌ NOT CAUGHT — test replicates logic inline, doesn't call actual function
- M3: ❌ NOT CAUGHT — test replicates logic inline, doesn't call actual function
- M4: ✅ Verified (dedup removal caught)
- M5: ✅ Verified (zero-write caught)
- M6: ✅ Verified (first-line fallback removal caught)
- M7: ✅ Verified (upstream_error removal caught)

### Required changes before acceptance:
1. **P1** (Medium): Replace `test_close_gap_timeout_preserved` with a test that calls the actual close-gap handler path, not inline logic replication.
2. **P2** (Medium): Replace `test_failure_path_preserves_download_events` with a test that calls `resolve_filing` directly, not inline logic replication.
3. **P3** (Low): Fix misleading comment in `test_fe4_different_request_ids_count_independently`.

### Scope: `changes_required` — implementation is sound, but mutation proof for M2/M3 is invalid.
```
