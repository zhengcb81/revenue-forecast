# I-09-B Carried Findings (append-only)

## Registered by carrier-landing executor

### F-01: supersedes field always None (info)
- **Card**: I-09-B
- **Severity**: info
- **Description**: The `supersedes` field in the registry is always None in the current implementation. This is by design — no supersession logic has been implemented yet.
- **Status**: carried forward

### F-02: OPEN-I09A-4 directory fail-closed not hard rejection (info)
- **Card**: I-09-B
- **Severity**: info
- **Description**: The directory-valued registry check was NOT implemented as a hard rejection (would break conftest.py test pattern). Instead documented as a test showing that nested-file corruption is detected by the chain hash.
- **Status**: carried forward

### F-03: conftest.py/monkeypatch scope correct (info)
- **Card**: I-09-B
- **Severity**: info
- **Description**: The conftest.py monkeypatch scope is correct — no scope issues detected in the test fixtures.
- **Status**: carried forward

### F-04: 14 OPEN items carried forward (info)
- **Card**: I-09-B
- **Severity**: info
- **Description**: 14 OPEN items are carried forward unresolved: 5 from I-09-A (OPEN-I09A-1, -2, -3, -5, -6) and 9 from I-08-B (E31, OPEN-D1, -D2, -D3, -D5, -D6, -D7, UNRESOLVED-BY-DESIGN registry anchor field names).
- **Status**: carried forward
