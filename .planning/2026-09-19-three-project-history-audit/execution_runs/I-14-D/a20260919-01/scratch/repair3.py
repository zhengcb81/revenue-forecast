"""Scratch: finish the r3 template repair.

Line 237 (file numbering) must be a single list element whose expression continues on
line 238.  Both lines are rebuilt from chr() codes and the whole module is compiled
before anything is written.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
Q = chr(34)
S = chr(39)
B = chr(92)
T2 = B + B + "t"
R2 = B + B + "r?" + B + B + "n"

line237 = (S + " " * 22 + "r" + Q + "(?:" + S + " + _AUTHJOIN_CLASS + " + S + "r"
           + Q + "*[" + T2 + "]*" + R2 + "[" + T2 + "]*)*" + Q + S + ",")
line238 = ("    + " + S + "|" + B + S + "[^" + B + S + B + B + "r" + B + B + "n]*"
           + B + S + ")" + Q + ")" + S + ",")
assign = "AUTHSCHEME3_NEW = list(AUTHSCHEME3_NEW_TEMPLATE)"

lines = P.read_text(encoding="utf-8").split("\n")
lines[236], lines[237] = line237, line238

# drop the duplicate assignment (the template list is closed on the line before it)
dupes = [i for i, ln in enumerate(lines) if ln.strip() == assign]
print("assignment lines at (0-based):", dupes)
if len(dupes) == 2:
    del lines[dupes[0]]

compile("\n".join(lines), "<probe>", "exec")
print("edited module compiles OK")
P.write_text("\n".join(lines), encoding="utf-8")

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("module imports OK; emitted r3 tail:")
for ln in m.AUTHSCHEME3_NEW[-5:]:
    print("   ", ln)
