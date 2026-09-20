# Independent Review — I-06-B / a20260919-01

Reviewer: independent (adversarial, did NOT write the card)
Date: 2026-09-20
Method: recompute everything from bytes, never trust implementer's summary

---

## 1. Verdict

**`changes_required`**

Reason: The evidence JSON file `after/review-input-and-evidence.json` contains an incorrect SHA-256 hash for the INJECT_TEXT sample. The implementer recorded `a8e0f0b0c639b0ed8cc2d90f7d20ef3b9378c9d819a909a81c71c31e8a325d6d` but the actual hash is `0acd9f4fb2d7edc665d2ffd9d4b5471c928ea4457ee4314b25457234310b75dc`. The card explicitly requires "证据包含实际读取 bytes hash" — this contract is violated. The harness code itself is correct; only the manually-written evidence file has the wrong value.

---

## 2. Recomputation Log

### 2.1 Production Source Hashes (from disk, independent)

| File | Expected (binding.json) | Actual (Get-FileHash SHA256) | Status |
|---|---|---|---|
| CW/prompt_injection.py | `7b22f239...9618` | `7b22f239...9618` | MATCH |
| CW/prompt_injection_guard.py | `f900a13d...9c08` | `f900a13d...9c08` | MATCH |
| CW/processing_demand.py | `90f232ed...888b` | `90f232ed...888b` | MATCH |
| CW/test_prompt_injection_guard.py | `c05e25fb...9bae` | `c05e25fb...9bae` | MATCH |
| RF/source_preparation.py | `5ec16eaf...ce46` (pre-bind) | `8070d60d...13e7` (current) | DRIFT (documented: changed by another card) |

**Conclusion**: All 4 CW production files unchanged. RF drift is external and documented.

### 2.2 Sample Text SHA-256 (independent, Python hashlib)

| Text | Expected (harness) | Actual (hashlib.sha256) | Status |
|---|---|---|---|
| CLEAN_TEXT | `58e517ac...3994` | `58e517ac...3994` | MATCH |
| INJECT_TEXT | (evidence JSON says `a8e0f0b0...5d6d`) | `0acd9f4f...75dc` | **MISMATCH** |
| STALE_TEXT | `dbace6f2...f89a` | `dbace6f2...f89a` | MATCH |

The harness code (`w06b_review_harness.py` line 239) computes `inject_hash = sha256_text(INJECT_TEXT)` which yields `0acd9f4f...`. The evidence JSON file has a wrong value.

### 2.3 RULESET_HASH (independent)

Computed from `json.dumps([list(item) for item in _RULESET_PATTERNS], ensure_ascii=False, sort_keys=True)`:
- Result: `19ace502ee7c13027f43ee82d33944fec84c1296976bc86ce6c8d5869abb962b`
- Matches production code and all test results. ✓

### 2.4 Idempotency Keys (independent)

| Key | Inputs | Expected (run1) | Actual (independent) | Status |
|---|---|---|---|---|
| key_a | entity=翡翠矿业, as_of_date=2026-09-19 | `1601c425...ff6d` | `1601c425...ff6d` | MATCH |
| key_b | entity=紫金矿业, as_of_date=2026-09-19 | `cf51e6f3...882c` | `cf51e6f3...882c` | MATCH |
| key_c | entity=翡翠矿业, as_of_date=2027-03-31 | `f0e10abf...ee47` | `f0e10abf...ee47` | MATCH |
| payload_a | (req_a dict) | `53a23a68...cd31` | `53a23a68...cd31` | MATCH |
| payload_b | (req_b dict) | `6c2941da...268` | `6c2941da...1268` | MATCH |

All keys deterministically derived. Different entity → different key. Different as_of_date → different key. Same key + different payload → fail-closed rejection verified.

### 2.5 Pattern Matching (independent regex verification)

INJECT_TEXT matches:
- `ignore_previous_instructions`: "ignore all previous instructions" ✓
- `exfiltration`: "send data to https://" ✓
- `system_prompt_override`: no match ✓ (not present in INJECT text)
- `prompt_leak_request`: no match ✓
- `instruction_injection`: no match ✓ (uses "ignore" not "disregard")

CLEAN_TEXT: no patterns match ✓

### 2.6 Independent Harness Run

```
Command: iso/venv/Scripts/python.exe -X utf8 -B scripts/w06b_review_harness.py reviewer_run
Exit code: 0
Result: 14/14 PASS
```

All 14 cases reproduced identically.

---

## 3. Numbered Findings

### F-1 [P1] Wrong INJECT_TEXT sha256 in evidence JSON

- **File**: `after/review-input-and-evidence.json`, line 27
- **Field**: `samples.INJECT.sha256`
- **Observed**: `a8e0f0b0c639b0ed8cc2d90f7d20ef3b9378c9d819a909a81c71c31e8a325d6d`
- **Expected**: `0acd9f4fb2d7edc665d2ffd9d4b5471c928ea4457ee4314b25457234310b75dc`
- **Why it matters**: The card's exit criteria require "证据包含实际读取 bytes hash". An evidence file with a wrong hash violates the traceability contract. While the harness code itself computes the correct hash, the manually-written evidence JSON is the auditor-facing artifact.
- **Minimum fix**: Change line 27 of `review-input-and-evidence.json` from `a8e0f0b0...` to `0acd9f4f...`.

### F-2 [P2] Missing recovery/README.md

- **File**: `handoff.json`, line 126 (evidence_paths)
- **Observed**: `recovery/README.md` listed in evidence_paths but the `recovery/` directory does not exist
- **Why it matters**: Minor — the reference is to a non-existent file. Does not affect functional correctness.
- **Minimum fix**: Remove `recovery/README.md` from evidence_paths, or create the file.

### F-3 [P3] N1b empty text → not_detected is semantically correct but could be surprising

- **File**: `scripts/w06b_review_harness.py`, line 325-330
- **Observed**: `scan_text("")` returns `status="not_detected"` (empty text has no patterns to match)
- **Why it matters**: This is correct behavior — no injection patterns found in empty text. The oracle (§3.3) says "scan_text(FAIL_TEXT) (空字符串) returns ScanResult(status='not_detected')" which matches. But a consumer should still block on empty text via a separate "no content" check, not rely on scan_text alone.
- **Minimum fix**: None needed for this card. The oracle correctly documents this as expected behavior.

---

## 4. Unverified List

| Item | Why unverified |
|---|---|
| Full original-request CLI resume | Blocked by I-06-A (D-W06 unsigned); persistent demand store doesn't exist |
| Cross-process demand persistence | DemandQueue is pure memory; no DB-backed store exists |
| Reviewer identity binding | D-W06 OPEN-4 unsigned; reviewer is free-form string |
| detected_and_ignored attribution policy | D-W06 OPEN-6 unsigned |
| Full source_preparation chain | Requires real CW catalog DB + filing-fetch + network |
| Production CatalogStore integration | Harness uses isolated sqlite3, not production store |

---

## 5. Paste-Ready Verdict Block

```
## Review: I-06-B / a20260919-01

Reviewer: independent (adversarial)
Date: 2026-09-20
Verdict: changes_required

Prefix-hash proof:
  CLEAN_TEXT sha256:   58e517ac742e329af9bd329cf1342d3a055532e29410a0cf27475ebfeb353994
  INJECT_TEXT sha256:  0acd9f4fb2d7edc665d2ffd9d4b5471c928ea4457ee4314b25457234310b75dc
  STALE_TEXT sha256:   dbace6f29f9d316f4ab2215f787c84dd613b943282d3e444c4863d9ac77cf89a
  RULESET_HASH:        19ace502ee7c13027f43ee82d33944fec84c1296976bc86ce6c8d5869abb962b
  key_a:               1601c4254382734b70eb3b74535ee26090088752f26a618698077663f202ff6d
  key_b:               cf51e6f3e9813a819a4d14f0235c22039f3b9c73bf556a407690b3eca4b4882c
  key_c:               f0e10abf4cbdb69d2136efb2eb2fec898c6e2bdd0d7708872cf49db222ecee47

Independent harness run: 14/14 PASS (exit code 0)
Production CW hashes: 4/4 MATCH
Production RF hash: DRIFT (documented, external)

Findings:
  F-1 [P1] review-input-and-evidence.json line 27: INJECT sha256 wrong
          (a8e0f0b0... vs actual 0acd9f4f...). Fix required.
  F-2 [P2] handoff.json: recovery/README.md referenced but missing.
  F-3 [P3] Empty text → not_detected is correct per oracle; no fix needed.

Blocked (not this card's scope):
  - Original-request CLI resume (I-06-A blocked)
  - Reviewer identity binding (D-W06 OPEN-4)
  - Cross-process demand persistence
  - Full source_preparation chain

Action required: Fix F-1 (correct INJECT sha256 in evidence JSON) before accepted_scoped.
```
