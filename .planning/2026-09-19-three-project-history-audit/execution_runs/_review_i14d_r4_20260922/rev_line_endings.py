"""Line-ending census, done right this time: count real CR, LF, CRLF byte pairs."""
import hashlib
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")

CR = bytes([13])
LF = bytes([10])
CRLF = bytes([13, 10])
CRCR = bytes([13, 13])


def census(b: bytes) -> str:
    cr = b.count(CR)
    lf = b.count(LF)
    crlf = b.count(CRLF)
    crcr = b.count(CRCR)
    bare_cr = cr - crlf
    bare_lf = lf - crlf
    return (f"bytes={len(b):6d} CR={cr:6d} LF={lf:6d} CRLF={crlf:6d} bareCR={bare_cr:6d} "
            f"bareLF={bare_lf:6d} CRCR={crcr:6d}")


print("=== single files ===")
for rel in [
    "iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py",
    "iso/product_narrow_r4/src/company_wiki/source_catalog/observability.py",
    "iso/product_base/src/company_wiki/source_catalog/observability.py",
]:
    p = ATT / rel
    b = p.read_bytes()
    print(f"{rel}\n   {census(b)}\n   sha256={hashlib.sha256(b).hexdigest()}")

print()
print("=== whole r4 tree: any file with CRCR (doubled CR)? ===")
r4tree = ATT / "iso/product_narrow_r4"
bad = []
nfiles = 0
for p in sorted(r4tree.rglob("*")):
    if p.is_file():
        nfiles += 1
        b = p.read_bytes()
        if CRCR in b:
            bad.append((str(p.relative_to(ATT)), b.count(CRCR)))
print(f"files scanned = {nfiles}")
print(f"files containing CRCR = {len(bad)}")
for name, n in bad:
    print(f"   {name}: CRCR x{n}")

print()
print("=== whole r3 tree for comparison ===")
r3tree = ATT / "iso/product_narrow_r3"
bad3 = []
n3 = 0
for p in sorted(r3tree.rglob("*")):
    if p.is_file():
        n3 += 1
        b = p.read_bytes()
        if CRCR in b:
            bad3.append((str(p.relative_to(ATT)), b.count(CRCR)))
print(f"files scanned = {n3}")
print(f"files containing CRCR = {len(bad3)}")
for name, n in bad3:
    print(f"   {name}: CRCR x{n}")

print()
print("=== diff of file lists r3 vs r4 ===")
def listing(root):
    return sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file())
l3, l4 = listing(r3tree), listing(r4tree)
print("only in r3:", set(l3) - set(l4))
print("only in r4:", set(l4) - set(l3))
print("common files with different bytes:")
for f in sorted(set(l3) & set(l4)):
    a = (r3tree / f).read_bytes()
    b = (r4tree / f).read_bytes()
    if a != b:
        print(f"   {f}: r3 {len(a)}B {hashlib.sha256(a).hexdigest()[:12]}  r4 {len(b)}B {hashlib.sha256(b).hexdigest()[:12]}")
