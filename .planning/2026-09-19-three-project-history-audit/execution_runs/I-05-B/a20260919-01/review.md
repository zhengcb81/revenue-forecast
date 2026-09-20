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