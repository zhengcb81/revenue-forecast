"""Addendum: (a) a load-bearing responsiveness test for the inversion,
(b) byte-identity of the after-break quoted classes with _QUOTED_VALUE,
(c) the class-level closure stated as a set equality.
"""
import hashlib
import re
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
S = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r4_20260922")
REL = "src/company_wiki/source_catalog/observability.py"

r3b = (ATT / "iso/product_narrow_r3" / REL).read_bytes()
r4b = (ATT / "iso/product_narrow_r4" / REL).read_bytes()


def sha(b):
    return hashlib.sha256(b).hexdigest()


import difflib

ops = [o for o in difflib.SequenceMatcher(a=r3b, b=r4b, autojunk=False).get_opcodes() if o[0] != "equal"]
print(f"differing regions: {len(ops)}")


def invert(a, b, subset):
    out = bytearray(b)
    for tag, i1, i2, j1, j2 in reversed(subset):
        out[j1:j2] = a[i1:i2]
    return bytes(out)


full = invert(r3b, r4b, ops)
print(f"invert(ALL 4 regions) == r3 : {full == r3b}")
for k in range(len(ops)):
    sub = [o for i, o in enumerate(ops) if i != k]
    got = invert(r3b, r4b, sub)
    print(f"invert(drop region {k}) == r3 : {got == r3b}   <-- must be False (this is the responsive control)")

print()
print("=" * 90)
print("CLASS-LEVEL CLOSURE: after-break quoted classes vs _QUOTED_VALUE")
print("=" * 90)
r4text = r4b.decode("utf-8")
r3text = r3b.decode("utf-8")
r4lines = r4text.split("\r\n")
r3lines = r3text.split("\r\n")


def find_line(lines, prefix):
    for ln in lines:
        if ln.startswith(prefix):
            return ln
    return None


q_line = find_line(r4lines, "_QUOTED_VALUE = ")
quoted = q_line.split('r"', 1)[1].rsplit('"', 1)[0]
print(f"_QUOTED_VALUE (r4)              = {quoted!r}")

l320 = find_line(r4lines, '                      r"(?:" + _AUTH_BARE_VALUE')
after = l320.split('r"+|', 1)[1].rsplit(")", 2)[0]
print(f"line 320 after-break literal    = {l320!r}")
print(f"line 320 quoted alternatives    = {after!r}")
print(f"byte-identical to _QUOTED_VALUE's? {after == quoted}")

l320_r3 = find_line(r3lines, '                      r"(?:" + _AUTH_BARE_VALUE')
after3 = l320_r3.split('r"+|', 1)[1].rsplit(")", 2)[0]
print()
print(f"r3 line 320 quoted alternatives = {after3!r}")
print(f"r3 identical to _QUOTED_VALUE's? {after3 == quoted}   <-- must be False")

print()
print("=" * 90)
print("CLASS-LEVEL CLOSURE stated as a set equality (from the char sweep)")
print("=" * 90)
p4 = __import__("json").loads((S / "probe_product_narrow_r4.json").read_text(encoding="utf-8"))
p3 = __import__("json").loads((S / "probe_product_narrow_r3.json").read_text(encoding="utf-8"))
base = __import__("json").loads((S / "probe_product_base.json").read_text(encoding="utf-8"))


def leaking_chars(d):
    out = set()
    for r in d["rows"]:
        if r["family"] == "CH" and r["leaks_secret"]:
            out.add(int(r["id"].split("-")[1], 16))
    return out


c4, c3, cb = leaking_chars(p4), leaking_chars(p3), leaking_chars(base)
print(f"chars leaking in a quoted continuation:")
print(f"  r4   : {sorted(hex(c) for c in c4)}")
print(f"  r3   : {sorted(hex(c) for c in c3)}")
print(f"  base : {len(cb)} chars (all printable + controls)")
print(f"  r3 \\ r4 = {sorted(hex(c) for c in (c3 - c4))}   <-- the leak r4 closed")
print(f"  r4 \\ r3 = {sorted(hex(c) for c in (c4 - c3))}   <-- must be empty: no new leak")
