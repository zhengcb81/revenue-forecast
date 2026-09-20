# I-05-B Independent Review — a20260919-01

Reviewer: independent (not the implementer)
Date: 2026-09-19
Card: I-05-B — 把工件选择与实际读取分开，消费者读取已验证字节

---

## 1. Verdict

**accepted_scoped**

Core claim verified: `verify_artifact_reads()` performs real file I/O, computes SHA256
from the actual buffer, and returns verified/failed events independent of the
selection plan. The separation of `artifact_read` (plan) from `artifact_read_events`
(IO proof) is correctly implemented. Two P3 findings on documentation accuracy; one
P2 finding on incomplete N3 negative-case test coverage for path-containment
scenarios (denied root, offline placeholder, out-of-bounds) required by the card
spec.

---

## 2. Recomputation Log

### 2.1 Production File SHA256 Verification

Recomputed from disk using `Get-FileHash -Algorithm SHA256`:

| File | Before (binding.json) | After (binding.json) | Actual (disk) | Match |
|------|----------------------|---------------------|---------------|-------|
| RF:scripts/company_wiki_source.py | `aeeb7b2a...039ff0` | `A55602E5...2E94AE` | `A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE` | ✅ |
| RF:scripts/source_preparation.py | `5ec16eaf...bce46` | `8070D60D...D131E7` | `8070D60DF1D730A400F76D7031011F8D0F51EA73DCAB224AA0D4A9524ED131E7` | ✅ |
| CW:src/.../resolver.py | `783460a9...be21a` | `783460a9...be21a` | `783460A9F21679B439073FC6B82F4D5A43F583423D59E9EE627B0C9F149BE21A` | ✅ |
| CW:src/.../artifact_handle.py | `3cc8fbf4...7b99` | `3cc8fbf4...7b99` | `3CC8FBF4F65380D17E2F0140390EF346F7CC17504854FF04B3DDF46498317B99` | ✅ |

**CW files unchanged** (zero-write confirmed): resolver.py and artifact_handle.py match their anchored "before" hashes exactly.

**RF files modified** as permitted by the card scope:
- `company_wiki_source.py`: new `verify_artifact_reads()` function added (lines 195-298)
- `source_preparation.py`: calls `verify_artifact_reads()` and adds `artifact_read_events`/`artifact_failed_events` to receipt (lines 141-146, 182-183)

### 2.2 ISO ↔ Production Parity

| File | ISO Hash | PROD Hash | Match |
|------|----------|-----------|-------|
| company_wiki_source.py | `A55602E5...` | `A55602E5...` | ✅ |
| source_preparation.py | `8070D60D...` | `8070D60D...` | ✅ |
| artifact_handle.py | `3CC8FBF4...` | `3CC8FBF4...` | ✅ |

ISO checkout copies are identical to production files.

### 2.3 Sentinel File Verification

Recomputed from disk:

| Sentinel | Content | Size | SHA256 (disk) | SHA256 (sentinel-consumption.json) | Match |
|----------|---------|------|---------------|-------------------------------------|-------|
| ALPHA | `ALPHA=17` | 8 | `2FE1261E53F43F55014E7F8D47D16A62838A817E138F7DC5E5E28A11D8AA97E1` | `2FE1261E...D8AA97E1` | ✅ |
| BETA | `BETA=29` | 7 | `74A4CCE33AC6CB10D0373621A883E35810514063FF645473AEDC2320217BF649` | `74A4CCE3...217BF649` | ✅ |
| GAMMA | `GAMMA=31` | 8 | `616F13941CA444660F2FBFA62935FB879939A765B6FCFCE93CFF9C46E5B5E9CF` | `616F1394...E5B5E9CF` | ✅ |
| alpha2 | `ALPHA=17` | 8 | `2FE1261E53F43F55014E7F8D47D16A62838A817E138F7DC5E5E28A11D8AA97E1` | (not in JSON) | ✅ (same as ALPHA) |

All sentinel files are real files on disk. SHA256 values match exactly.

### 2.4 Test File Hash Verification

| File | Expected | Actual | Match |
|------|----------|--------|-------|
| test_w05b_verified_artifact_read.py (iso) | `F9845F170E0EFF4B705993A3659CC0D88EE7C476AE019641B712E4968DF9595D` | `F9845F170E0EFF4B705993A3659CC0D88EE7C476AE019641B712E4968DF9595D` | ✅ |
| test_fc904_artifact_selection.py (iso) | `ED8D6B4BD76DBE17DCAB1BB0E9D75B8E57651BA274F32411CF69F8892ADDBC6B` | `ED8D6B4BD76DBE17DCAB1BB0E9D75B8E57651BA274F32411CF69F8892ADDBC6B` | ✅ |

### 2.5 Test Execution (Independent Re-run)

**20 new tests** — `test_w05b_verified_artifact_read.py`:
```
20 passed in 0.90s
```

All 20 tests pass independently:
- W05B-P1 (4 tests): positive read verification ✅
- W05B-P2 (1 test): raw-only no parser forced ✅
- W05B-N1 (3 tests): selection without read ✅
- W05B-N2 (3 tests): tamper between select and read ✅
- W05B-N3 (5 tests): missing/malformed security ✅
- W05B-N4 (1 test): source binding separation ✅
- Integration (1 test): receipt structure ✅
- RaceCondition (2 tests): TOCTOU detection ✅

**11 regression tests** — `test_fc904_artifact_selection.py`:
```
11 passed in 0.55s
```

No regression in existing FC-904 tests.

### 2.6 Independent Tamper Test (Manual Re-run)

Wrote a standalone Python script that:
1. Created file with `b"ALPHA=17"`, recorded SHA256
2. Overwrote with `b"BETA=29"`, computed new SHA256
3. Compared: `2fe1261e... != 74a4cce3...` → **Mismatch detected** ✅
4. Same-length test: `b"ALPHA=17"` (8 bytes) vs `b"GAMMA=31"` (8 bytes): `2fe1261e... != 616f1394...` → **Collision detection works** ✅

### 2.7 Key Claim Verification

**Claim: "separate artifact selection from actual verified read"**

Verified by reading production code:
- `select_artifact_roles()` (line 147): returns `(artifact_read, producer_events)` — PLAN only, no file I/O ✅
- `verify_artifact_reads()` (line 195): calls `path.read_bytes()` (line 263), `hashlib.sha256(actual_bytes).hexdigest()` (line 274), compares declared vs actual (line 275) — REAL IO ✅
- `artifact_read` in receipt = PLAN from `select_artifact_roles` ✅
- `artifact_read_events` in receipt = IO PROOF from `verify_artifact_reads` ✅
- The two are distinct keys in the receipt dict (lines 180-183 of source_preparation.py) ✅

### 2.8 Owner Rulings Verification

**W05-1 (选 A): source-window binding only, no per-slice hash depth**
- `verify_artifact_reads` reads the whole artifact file and verifies `content_sha256` ✅
- No per-section/per-slice hash drilling ✅
- Source-window binding via `source_sha256` from bundle source ✅

**W05-2 (选 A): as_of_date mandatory = published_date**
- decision.md states: "when `as_of_date` is absent or empty, it falls back to `published_date`"
- Actual code (source_preparation.py:165): `as_of_date=str(request.get("as_of_date", ""))` — no fallback to `published_date`
- See Finding P3-1 below.

---

## 3. Findings

### P3-1: W05-2 `as_of_date` fallback not implemented (documentation mismatch)

**File**: `decision.md` lines 23-28, `source_preparation.py` line 165

**Observed**: decision.md claims "when `as_of_date` is absent or empty from the request, it falls back to the handle's `published_date`". The actual code passes `as_of_date=str(request.get("as_of_date", ""))` with no fallback. An empty string would fail `_iso_date()` validation.

**Why it matters**: The decision document describes intended behavior that doesn't exist in code. This doesn't break the current card (tests always provide `as_of_date` explicitly), but creates a documentation debt.

**Minimum fix**: Either add the fallback in `prepare_source`:
```python
as_of_date_val = request.get("as_of_date") or handle.get("published_date") or ""
```
or correct the decision.md to state that `as_of_date` is required by the caller with no automatic fallback (caller must provide it).

### P3-2: Oracle.md byte count error for ALPHA sentinel

**File**: `oracle.md` line 18

**Observed**: Oracle states `bytes_read=9 (len of b"ALPHA=17\n")` but the actual sentinel file contains `b"ALPHA=17"` (8 bytes, no trailing newline).

**Why it matters**: Factual error in the frozen oracle. The test file correctly uses `ALPHA_BODY = b"ALPHA=17"` (8 bytes) and asserts `bytes_read == len(ALPHA_BODY)` which is 8. The oracle was written assuming a newline that doesn't exist.

**Minimum fix**: Correct oracle.md line 18: `bytes_read=8 (len of b"ALPHA=17")`.

### P2-1: N3 negative cases incomplete (denied root, placeholder, out-of-bounds)

**File**: `test_w05b_verified_artifact_read.py` class `TestW05BN3NegativeSecurity`

**Observed**: Card spec (lines 35-36, 47-48) and oracle (lines 54-64) require testing: denied root, offline placeholder, out-of-bounds path, and missing file. The test class covers: missing file, no bundle, malformed bundle, missing role, empty path. It does NOT cover:
- `denied root`: artifact path inside a denied root → should return `artifact_path_outside_allowed_root`
- `offline placeholder`: cloud placeholder not hydrated → should return `placeholder_not_hydrated`
- `out-of-bounds path`: path traversal outside allowed roots → should return `artifact_path_outside_allowed_root`

**Why it matters**: The `verify_artifact_reads` function itself doesn't perform path-containment checks (it relies on `validate_artifact` upstream). The card's "固定样本" explicitly requires these tests. Without them, there's no proof that path-containment violations are caught at the verify layer.

**Minimum fix**: Add test cases for at least denied root and out-of-bounds paths. If `verify_artifact_reads` is expected to delegate containment to `validate_artifact`, document this boundary explicitly in the function docstring and add integration tests proving `validate_artifact` rejects those cases before `verify_artifact_reads` is called.

---

## 4. Unverified List

1. **R4 deny-fix preservation in resolver.py**: The card references `test_r4bar11_deny_binds_the_byte_entry.py` in CW tests. I verified resolver.py hash is unchanged (zero-write), but I did NOT re-run the CW contract test suite to confirm R4 deny-fix still passes. The file wasn't modified, so this is low-risk.

2. **Path-containment enforcement**: `verify_artifact_reads` does not check `allowed_roots` or perform path-containment validation. The handoff.json notes this as an open question: "verify_artifact_reads does not check allowed_roots (relies on validate_artifact upstream)". I cannot verify that `validate_artifact` is always called before `verify_artifact_reads` in production code paths.

3. **W05-2 `as_of_date` fallback**: The decision.md describes behavior that doesn't exist in code. I cannot verify whether this is a documentation error or a missing implementation, because the card's test scope doesn't test the fallback path.

---

## 5. Paste-Ready Verdict Block

```
<!-- REVIEW: I-05-B a20260919-01 -->
<!-- prefix-hash: 00651ab5 (first 8 hex of sha256 over this block's body) -->
<!-- reviewer: independent (not the implementer) -->
<!-- date: 2026-09-19 -->

Verdict: accepted_scoped

Summary:
- Core claim verified: verify_artifact_reads() performs real file I/O and SHA256
  computation; artifact_read_events is independent from artifact_read (plan).
- 20 new tests pass (independently re-run); 11 regression tests pass.
- Sentinel files ALPHA/BETA/GAMMA are real on disk; SHA256 values match.
- Production CW files zero-write confirmed (hashes unchanged).
- Production RF files modified as permitted by card scope.
- Owner ruling W05-1 applied correctly (source-window binding only).
- Owner ruling W05-2: decision.md describes fallback not present in code (P3).

Findings:
- P2-1: N3 negative cases incomplete (denied root, placeholder, out-of-bounds not tested)
- P3-1: W05-2 as_of_date fallback described in decision.md but not implemented
- P3-2: Oracle.md ALPHA byte count wrong (says 9, actual is 8)

Unverified:
- R4 deny-fix preservation in CW resolver.py (file unchanged, tests not re-run)
- Path-containment enforcement boundary between validate_artifact and verify_artifact_reads
- W05-2 fallback behavior (not in scope of this card's tests)

Production hash proof:
  RF:company_wiki_source.py  A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE
  RF:source_preparation.py   8070D60DF1D730A400F76D7031011F8D0F51EA73DCAB224AA0D4A9524ED131E7
  CW:resolver.py             783460A9F21679B439073FC6B82F4D5A43F583423D59E9EE627B0C9F149BE21A (unchanged)
  CW:artifact_handle.py      3CC8FBF4F65380D17E2F0140390EF346F7CC17504854FF04B3DDF46498317B99 (unchanged)

Test proof:
  20 passed in 0.90s (test_w05b_verified_artifact_read.py)
  11 passed in 0.55s (test_fc904_artifact_selection.py, regression)
<!-- end REVIEW -->
```