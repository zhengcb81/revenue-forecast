"""Line-level diff r4 -> r5 using difflib, plus region analysis. Read-only."""
import difflib, hashlib, os

ATT = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01"
R4 = os.path.join(ATT, r"iso\product_narrow_r4\src\company_wiki\source_catalog\observability.py")
R5 = os.path.join(ATT, r"iso\product_narrow_r5\src\company_wiki\source_catalog\observability.py")

def lines(p):
    with open(p, "rb") as f:
        b = f.read()
    # split on CRLF keeping terminators
    out = []
    i = 0
    while i < len(b):
        j = b.find(b"\r\n", i)
        if j < 0:
            out.append(b[i:]); break
        out.append(b[i:j+2]); i = j+2
    return out

a = lines(R4); b = lines(R5)
print("r4 lines:", len(a), " r5 lines:", len(b))

sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
print()
print("== opcodes (non-equal) ==")
changed_r4 = set(); changed_r5 = set()
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    print(f"{tag}: r4[{i1+1}..{i2}] r5[{j1+1}..{j2}]")
    for k in range(i1, i2):
        changed_r4.add(k+1)
        print(f"   -r4 {k+1:4d}: {a[k][:150]!r}")
    for k in range(j1, j2):
        changed_r5.add(k+1)
        print(f"   +r5 {k+1:4d}: {b[k][:150]!r}")

print()
print("r4 changed line numbers:", sorted(changed_r4))
print("r5 changed line numbers:", sorted(changed_r5))

# Are all r4-changed lines within the comment block + the two code lines?
print()
print("r4 comment block: which lines are pure-comment (start with #) in r4?")
for k in sorted(changed_r4):
    t = a[k-1].decode("utf-8", "replace")
    print(f"  r4 {k}: comment={t.lstrip().startswith('#')} code={not t.lstrip().startswith('#')} :: {t.rstrip()[:110]}")
print()
for k in sorted(changed_r5):
    t = b[k-1].decode("utf-8", "replace")
    print(f"  r5 {k}: comment={t.lstrip().startswith('#')} code={not t.lstrip().startswith('#')} :: {t.rstrip()[:110]}")

# byte-region check restricted to the true middle
r4b = b"".join(a); r5b = b"".join(b)
p = 0
while r4b[p] == r5b[p]:
    p += 1
s = 0
while r4b[len(r4b)-1-s] == r5b[len(r5b)-1-s]:
    s += 1
print()
print(f"first differing byte offset {p} (r4 line {r4b.count(chr(10).encode(),0,p)+1}), "
      f"r4 tail-suffix {s} bytes, r4 mid {len(r4b)-p-s} B, r5 mid {len(r5b)-p-s} B")
