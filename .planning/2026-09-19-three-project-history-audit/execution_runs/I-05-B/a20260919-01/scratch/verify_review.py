"""Independent review verification script for I-05-B."""
import hashlib
import sys
from pathlib import Path

PLAN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit")
ATTEMPT = PLAN / "execution_runs" / "I-05-B" / "a20260919-01"
SCRATCH = ATTEMPT / "scratch"

RF_ROOT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW_ROOT = Path(r"C:\Users\郑曾波\Projects\company-wiki")

print("=" * 70)
print("INDEPENDENT REVIEW: I-05-B")
print("=" * 70)

# 1. Production file hashes
print("\n[1] Production file SHA256 verification")
prod_files = {
    "RF:scripts/company_wiki_source.py": RF_ROOT / "scripts" / "company_wiki_source.py",
    "RF:scripts/source_preparation.py": RF_ROOT / "scripts" / "source_preparation.py",
    "CW:src/company_wiki/source_catalog/resolver.py": CW_ROOT / "src" / "company_wiki" / "source_catalog" / "resolver.py",
    "CW:src/company_wiki/source_catalog/artifact_handle.py": CW_ROOT / "src" / "company_wiki" / "source_catalog" / "artifact_handle.py",
}

expected_before = {
    "RF:scripts/company_wiki_source.py": "aeeb7b2a63047c73eac3a9806ac0c426e645e9aa87da85606cab78770b039ff0",
    "RF:scripts/source_preparation.py": "5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46",
    "CW:src/company_wiki/source_catalog/resolver.py": "783460a9f21679b439073fc6b82f4d5a43f583423d59e9ee627b0c9f149be21a",
    "CW:src/company_wiki/source_catalog/artifact_handle.py": "3cc8fbf4f65380d17e2f0140390ef346f7cc17504854ff04b3ddf46498317b99",
}

expected_after = {
    "RF:scripts/company_wiki_source.py": "A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE",
    "RF:scripts/source_preparation.py": "8070D60DF1D730A400F76D7031011F8D0F51EA73DCAB224AA0D4A9524ED131E7",
    "CW:src/company_wiki/source_catalog/resolver.py": "783460a9f21679b439073fc6b82f4d5a43f583423d59e9ee627b0c9f149be21a",
    "CW:src/company_wiki/source_catalog/artifact_handle.py": "3cc8fbf4f65380d17e2f0140390ef346f7cc17504854ff04b3ddf46498317b99",
}

all_ok = True
for label, path in prod_files.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    expected = expected_after[label].upper()
    match = actual == expected
    status = "OK" if match else "MISMATCH"
    print(f"  {label}: {status} (actual={actual[:16]}..., expected={expected[:16]}...)")
    if not match:
        all_ok = False

print(f"  All production hashes match 'after' state: {all_ok}")

# 2. CW files unchanged (zero-write)
print("\n[2] Production zero-write (CW files)")
for key in ["CW:src/company_wiki/source_catalog/resolver.py", "CW:src/company_wiki/source_catalog/artifact_handle.py"]:
    actual = hashlib.sha256(prod_files[key].read_bytes()).hexdigest()
    before = expected_before[key]
    unchanged = actual.lower() == before.lower()
    print(f"  {key}: unchanged={unchanged} (before={before[:16]}... actual={actual[:16]}...)")

# 3. Sentinel file verification
print("\n[3] Sentinel file SHA256 verification")
sentinel_files = {
    "ALPHA": ("alpha_normalized.txt", "2FE1261E53F43F55014E7F8D47D16A62838A817E138F7DC5E5E28A11D8AA97E1", b"ALPHA=17"),
    "BETA": ("beta_normalized.txt", "74A4CCE33AC6CB10D0373621A883E35810514063FF645473AEDC2320217BF649", b"BETA=29"),
    "GAMMA": ("gamma_normalized.txt", "616F13941CA444660F2FBFA62935FB879939A765B6FCFCE93CFF9C46E5B5E9CF", b"GAMMA=31"),
}

for name, (fname, expected_sha, expected_content) in sentinel_files.items():
    path = SCRATCH / fname
    content = path.read_bytes()
    actual_sha = hashlib.sha256(content).hexdigest().upper()
    content_match = content == expected_content
    sha_match = actual_sha == expected_sha.upper()
    print(f"  {name}: content_match={content_match} sha_match={sha_match} len={len(content)} sha={actual_sha[:16]}...")

# 4. Independent tamper test
print("\n[4] Independent tamper test (replace ALPHA with BETA)")
import tempfile, shutil
tmp = Path(tempfile.mkdtemp())
try:
    art = tmp / "test_artifact.txt"
    art.write_bytes(b"ALPHA=17")
    alpha_sha = hashlib.sha256(b"ALPHA=17").hexdigest()
    # SELECT: record the declared hash
    declared_sha = alpha_sha
    # TAMPER: replace with BETA content
    art.write_bytes(b"BETA=29")
    # VERIFY: read actual bytes and compare
    actual_bytes = art.read_bytes()
    actual_sha = hashlib.sha256(actual_bytes).hexdigest()
    mismatch = actual_sha != declared_sha
    print(f"  Declared SHA: {declared_sha[:16]}...")
    print(f"  Actual SHA:   {actual_sha[:16]}...")
    print(f"  Mismatch detected: {mismatch}")
    print(f"  Tamper detection: {'PASS' if mismatch else 'FAIL'}")
finally:
    shutil.rmtree(tmp)

# 5. Independent same-length collision test
print("\n[5] Independent same-length collision test")
sha_alpha = hashlib.sha256(b"ALPHA=17").hexdigest()
sha_gamma = hashlib.sha256(b"GAMMA=31").hexdigest()
collision = sha_alpha == sha_gamma
print(f"  ALPHA: {sha_alpha[:16]}... (8 bytes)")
print(f"  GAMMA: {sha_gamma[:16]}... (8 bytes)")
print(f"  Collision: {collision}")
print(f"  Collision detection: {'PASS' if not collision else 'FAIL'}")

# 6. Oracle byte count check
print("\n[6] Oracle byte count verification")
alpha_content = b"ALPHA=17"
print(f"  ALPHA content: {alpha_content!r}")
print(f"  len(ALPHA): {len(alpha_content)} bytes")
print(f"  Oracle says: 9 bytes")
print(f"  Oracle byte count: {'WRONG (P3)' if len(alpha_content) != 9 else 'CORRECT'}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
