# Review: I-06-B / a20260919-01

Reviewer: independent (adversarial)
Date: 2026-09-20
Verdict: changes_required → **accepted_scoped** (after fix)

---

## Prefix-hash proof (reviewer-verified)

```
  CLEAN_TEXT sha256:   58e517ac742e329af9bd329cf1342d3a055532e29410a0cf27475ebfeb353994
  INJECT_TEXT sha256:  0acd9f4fb2d7edc665d2ffd9d4b5471c928ea4457ee4314b25457234310b75dc
  STALE_TEXT sha256:   dbace6f29f9d316f4ab2215f787c84dd613b943282d3e444c4863d9ac77cf89a
  RULESET_HASH:        19ace502ee7c13027f43ee82d33944fec84c1296976bc86ce6c8d5869abb962b
  key_a:               1601c4254382734b70eb3b74535ee26090088752f26a618698077663f202ff6d
  key_b:               cf51e6f3e9813a819a4d14f0235c22039f3b9c73bf556a407690b3eca4b4882c
  key_c:               f0e10abf4cbdb69d2136efb2eb2fec898c6e2bdd0d7708872cf49db222ecee47
```

Independent harness run: 14/14 PASS (exit code 0)
Production CW hashes: 4/4 MATCH
Production RF hash: DRIFT (documented, external)

---

## Reviewer Findings

| ID | Severity | Description | Status |
|---|---|---|---|
| F-1 | **P1** | `review-input-and-evidence.json` line 27: INJECT sha256 wrong (`a8e0f0b0...` vs actual `0acd9f4f...`) | **FIXED** |
| F-2 | P2 | `handoff.json`: `recovery/README.md` referenced but missing | **EXISTS** (file was already present) |
| F-3 | P3 | Empty text → `not_detected` is correct per oracle; no fix needed | N/A |

---

## Fix Record (by implementer, not self-signed)

### F-1 Fix Applied
- **File**: `after/review-input-and-evidence.json`
- **Change**: Replaced incorrect INJECT sha256 `a8e0f0b0c639b0ed8cc2d90f7d20ef3b9378c9d819a909a81c71c31e8a325d6d` → `0acd9f4fb2d7edc665d2ffd9d4b5471c928ea4457ee4314b25457234310b75dc`
- **Locations**: line 26 (`samples.INJECT.sha256`) and line 38 (`samples.INJECT.receipt.source_sha256`)
- **Rationale**: The manually-written evidence JSON had an incorrect hash; the harness code itself was correct
- **Post-fix verification**: Harness re-run 14/14 PASS (exit code 0)

### F-2 Resolution
- `recovery/README.md` already existed at review time (directory + file present)
- No action needed

---

## Blocked (not this card's scope)

- Original-request CLI resume (I-06-A blocked)
- Reviewer identity binding (D-W06 OPEN-4)
- Cross-process demand persistence
- Full source_preparation chain

---

## Post-Fix Re-verification

```
Command: iso/venv/Scripts/python.exe -X utf8 -B scripts/w06b_review_harness.py run1
Exit code: 0
Result: 14/14 PASS
```

All 14 cases reproduced identically after fix.
