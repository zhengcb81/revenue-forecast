"""Scratch: repair lines 237-238 of apply_i14d_narrow.py (0-based 236, 237).

The intended emitted product source line is:

    r"(?:' + _AUTHJOIN_CLASS + r'[ \t]*\r?\n[ \t]*)*"

as an ELEMENT of the template list, i.e. the file line is that text inside single
quotes, with every backslash doubled.  Everything below is built from chr() codes so
this repair has no quoting of its own; the result is compiled before it is written.
"""
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
Q = chr(34)
S = chr(39)
B = chr(92)          # a single backslash character
T2 = B + B + "t"     # the FILE text for a product \t
R2 = B + B + "r?" + B + B + "n"   # the FILE text for a product \r?\n

line237 = (S + " " * 22 + "r" + Q + "(?:" + S + " + _AUTHJOIN_CLASS + " + S + "r"
           + Q + "*[" + T2 + "]*" + R2 + "[" + T2 + "]*)*" + Q + S + ",")
line238 = ("    + " + S + "|" + B + S + "[^" + B + S + B + B + "r" + B + B + "n]*"
           + B + S + ")" + Q + ")" + S + ",")

lines = P.read_text(encoding="utf-8").split("\n")
old237, old238 = lines[236], lines[237]
print("before 237:", repr(old237))
print("  new  237:", repr(line237))
print("before 238:", repr(old238))
print("  new  238:", repr(line238))

# the whole list must compile after substitution
probe = lines[:]
probe[236], probe[237] = line237, line238
compile("\n".join(probe), "<probe>", "exec")
print("edited module compiles OK")

lines[236], lines[237] = line237, line238
P.write_text("\n".join(lines), encoding="utf-8")
print("written")

import importlib.util
spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("module imports OK; emitted r3 tail:")
for ln in m.AUTHSCHEME3_NEW[-4:]:
    print("   ", ln)
