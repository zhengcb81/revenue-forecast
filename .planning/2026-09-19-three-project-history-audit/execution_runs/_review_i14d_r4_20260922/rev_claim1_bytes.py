"""Claim 1: byte-level diff r4 vs r3, and inverse reconstruction.

Reads bytes only (never text mode). Reports every maximal differing region,
with byte offsets, and then attempts to invert each region back to r3.
"""
import hashlib
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
REL = "src/company_wiki/source_catalog/observability.py"

r3 = (ATT / "iso/product_narrow_r3" / REL).read_bytes()
r4 = (ATT / "iso/product_narrow_r4" / REL).read_bytes()
base = (ATT / "iso/product_base" / REL).read_bytes()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


print("r3 bytes", len(r3), sha(r3))
print("r4 bytes", len(r4), sha(r4))
print("base bytes", len(base), sha(base))
print()

# --- maximal differing regions, aligned from the start (no common prefix/suffix trim issues) ---
# First: common prefix / suffix lengths.
i = 0
while i < min(len(r3), len(r4)) and r3[i] == r4[i]:
    i += 1
j = 0
while j < min(len(r3), len(r4)) - i and r3[len(r3) - 1 - j] == r4[len(r4) - 1 - j]:
    j += 1

print(f"common prefix = {i} bytes")
print(f"common suffix = {j} bytes")
print(f"r3 middle = {r3[i:len(r3)-j]!r}  ({len(r3)-j-i} bytes)")
print(f"r4 middle = {r4[i:len(r4)-j]!r}  ({len(r4)-j-i} bytes)")
print()

# --- enumerate ALL maximal differing regions using difflib-free exact scan ---
# Use a simple approach: walk both byte strings with an LCS-free "same length" assumption
# is unsafe; instead use difflib.SequenceMatcher on bytes.
import difflib

sm = difflib.SequenceMatcher(a=r3, b=r4, autojunk=False)
regions = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal":
        regions.append((tag, i1, i2, j1, j2))
        print(f"[{tag}] r3[{i1}:{i2}]={r3[i1:i2]!r}  ->  r4[{j1}:{j2}]={r4[j1:j2]!r}")

print()
print(f"number of non-equal opcode regions = {len(regions)}")

# --- report line numbers of each region (1-based) in r3 and r4 ---
def line_of(data: bytes, off: int) -> int:
    return data.count(b"\n", 0, off) + 1


for tag, i1, i2, j1, j2 in regions:
    print(f"  region r3 line {line_of(r3, i1)}  ->  r4 line {line_of(r4, j1)}")

# --- inverse reconstruction: apply the reverse edits to r4 to get r3 ---
# do it by rebuilding: take r4, and for each region replace r4[j1:j2] with r3[i1:i2]
# (process from the end so offsets stay valid)
rebuilt = bytearray(r4)
for tag, i1, i2, j1, j2 in reversed(regions):
    rebuilt[j1:j2] = r3[i1:i2]
rebuilt = bytes(rebuilt)
print()
print("inverse reconstruction == r3 byte for byte:", rebuilt == r3)
print("inverse reconstruction sha256:", sha(rebuilt))
print("r3 sha256                    :", sha(r3))
if rebuilt != r3:
    # locate first difference
    for k in range(min(len(rebuilt), len(r3))):
        if rebuilt[k] != r3[k]:
            print("first diff at byte", k, repr(rebuilt[k-20:k+20]), "vs", repr(r3[k-20:k+20]))
            break
    print("len rebuilt", len(rebuilt), "len r3", len(r3))

# --- line-ending census ---
for name, b in (("r3", r3), ("r4", r4), ("base", base)):
    print(f"{name}: CR={b.count(bytes([13]))} LF={b.count(bytes([10]))} CRLF={b.count(b'\\r\\n')} "
          f"bare-CR={b.count(bytes([13])) - b.count(b'\\r\\n')} "
          f"CRCR={b.count(bytes([13,13]))}")

# --- line 319 area: confirm \r?\n still present ---
lines4 = r4.split(b"\n")
for n in (316, 317, 318, 319, 320, 321, 322, 323, 324):
    if 1 <= n <= len(lines4):
        print(f"r4 line {n}: {lines4[n-1]!r}")
