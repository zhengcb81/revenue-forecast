"""Byte-level diff r4 -> r5, and the inversion test. Read-only."""
import hashlib, os, sys

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
R4 = os.path.join(ATT, r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py")
R5 = os.path.join(ATT, r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py")
BK4 = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_bookkeeping_20260922_round74\i14d_r4_observability.py"
BK5 = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_bookkeeping_20260922_round74\i14d_r5_observability.py"

def rd(p):
    with open(p, "rb") as f:
        return f.read()

r4 = rd(R4); r5 = rd(R5)
print("r4 bytes", len(r4), hashlib.sha256(r4).hexdigest())
print("r5 bytes", len(r5), hashlib.sha256(r5).hexdigest())
print("bookkeeping r4 == tree r4:", rd(BK4) == r4)
print("bookkeeping r5 == tree r5:", rd(BK5) == r5)
print()

def regions(a, b):
    """maximal differing byte runs (common prefix/suffix trimmed per run)."""
    n = min(len(a), len(b))
    out = []
    i = 0
    while i < n:
        if a[i] == b[i]:
            i += 1
            continue
        j = i
        while j < n and a[j] != b[j]:
            j += 1
        out.append((i, j))
        i = j
    if len(a) != len(b):
        out.append((n, max(len(a), len(b))))
    return out

# First: exact equality check on the common prefix
p = 0
while p < min(len(r4), len(r5)) and r4[p] == r5[p]:
    p += 1
s = 0
while s < min(len(r4), len(r5)) - p and r4[len(r4)-1-s] == r5[len(r5)-1-s]:
    s += 1
print(f"common prefix len {p}, common suffix len {s}")
print(f"r4 middle = {len(r4)-p-s} bytes, r5 middle = {len(r5)-p-s} bytes")

def lineno(data, off):
    return data.count(b"\n", 0, off) + 1

print()
print("== differing byte regions (r4 vs r5) ==")
rs = regions(r4, r5)
print("count:", len(rs))
for (i, j) in rs:
    print(f"\n--- region @r4off {i}..{j} (len {j-i})  r4 line {lineno(r4,i)}  r5 line {lineno(r5,i)} ---")
    print("  r4 bytes:", repr(r4[i:j])[:400])
    print("  r5 bytes:", repr(r5[i:j])[:400])

# Inversion test: rebuild r4 from r5 by substituting the r5 sides with the r4 sides.
# (Regions must be aligned; because lengths differ we rebuild by walking.)
if len(rs) == 1:
    i, j = rs[0]
    inv = r5[:i] + r4[i:j] + r5[j:]
else:
    # general: splice using a diff of aligned regions; do it via the prefix/middle/suffix
    inv = r5[:p] + r4[p:len(r4)-s] + r5[len(r5)-s:]
print()
print("inversion reproduces r4 byte for byte:", inv == r4)
print("inverted sha256:", hashlib.sha256(inv).hexdigest())

# Uniform CRLF
for name, d in (("r4", r4), ("r5", r5)):
    CR = d.count(bytes([13])); LF = d.count(bytes([10])); CRLF = d.count(bytes([13, 10]))
    print(f"{name}: CR={CR} LF={LF} CRLF={CRLF} loneCR={CR-CRLF} loneLF={LF-CRLF}")

# constant rename
print()
print("r4 has _AUTH_SCHEME_TOKEN:", b"_AUTH_SCHEME_TOKEN" in r4)
print("r5 has _AUTH_SCHEME_TOKEN:", b"_AUTH_SCHEME_TOKEN" in r5)
print("r4 has _AUTH_PREBREAK_TOKEN:", b"_AUTH_PREBREAK_TOKEN" in r4)
print("r5 has _AUTH_PREBREAK_TOKEN:", b"_AUTH_PREBREAK_TOKEN" in r5)
