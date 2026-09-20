# I-09-B Independent Review Verdict

- **card_id**: I-09-B
- **attempt_id**: a20260919-01
- **reviewer**: independent (not the implementer)
- **verdict**: `accepted_scoped`
- **verdict_timestamp**: 2026-09-19T00:00:00Z
- **reviewer_signed**: true
- **implementer_signed**: false (carrier-landing executor never self-signs)

## Scope of Acceptance

The reviewer accepts the implementation as scoped, with the following observations:

### Verified Correct
1. **Prepare/commit split**: `run_forecast()` correctly accepts `_defer_registration=True` and skips `register_publication()` when set.
2. **commit_status()**: Correctly checks if a publication_id has a committed row with all members verified.
3. **commit_publication()**: Correctly computes publication_id, verifies member existence/hashes, checks idempotency, performs single registry append.
4. **New registry fields**: `publication_id`, `state`, `members`, `member_sha256`, `attempt_seq`, `supersedes` — all additive (old rows stay readable).
5. **CLI stdout-only rejection**: Formal mode without `--output` is correctly rejected (I09-E08).
6. **test_c2 updated**: Reflects prepare/commit split — output file IS written (orphan), but commit fails and `is_registered` returns False.
7. **conftest.py/monkeypatch scope**: Correct — no scope issues detected.

### Carried Findings (informational)

| ID | Finding | Severity |
|---|---|---|
| F-01 | `supersedes` field always None in current implementation | info |
| F-02 | OPEN-I09A-4 directory fail-closed not hard rejection (documented, test verifies corruption detection) | info |
| F-03 | conftest.py/monkeypatch scope correct | info |
| F-04 | 14 OPEN items carried forward (5 from I-09-A, 9 from I-08-B) — all unadjudicated | info |

### Known Limitations (carried, not blocking)
- OPEN-I09A-1 through OPEN-I09A-6: ALL still unadjudicated
- OPEN-D1 through OPEN-D7: ALL still unadjudicated
- E31 compensation line: implemented but NOT tested under real kill/recovery (I-09-C scope)
- Cross-process commit lock not implemented (I-09-C scope)
- Cross-repo consumers of commit_status not verified
- `publication_id` computation uses simplified identity_payload

### Scope Boundary
- All changes confined to `iso/rf/` — production tree was NOT written to
- 48 → 59 tests passed, 0 new failures, 11 new tests added

## Verdict Rationale

The implementation correctly delivers the prepare/commit split protocol as designed in I-09-A. The scope is clear: this card earns `accepted_scoped` for its implementation quality, not for transaction-fault resilience (I-09-C scope). The 14 OPEN items are faithfully carried forward without premature closure.
