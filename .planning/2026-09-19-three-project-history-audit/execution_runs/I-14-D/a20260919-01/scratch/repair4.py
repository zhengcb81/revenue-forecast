"""Scratch: last repair of the r3 template lines 237-238, then import the module.

Two textual defects are fixed in one pass:
  * `'r"*[` became `' + 'r"*[` earlier, i.e. a literal `'` was inserted where a
    concatenation was needed;
  * the continuation line lost its leading indentation.

Everything is built from chr() codes, the result is compiled before it is written, and
the module is imported afterwards to prove the emitted block is executable.
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

lines = P.read_text(encoding="utf-8").split("\n")
# normalise: the malformed concatenation is `+ 'r"` written as `+ ' + 'r"`
lines[236] = line237
lines[237] = line238

compile("\n".join(lines), "<probe>", "exec")
print("edited module compiles OK")
P.write_text("\n".join(lines), encoding="utf-8")
print("written")

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("module imports OK; emitted r3 tail:")
for ln in m.AUTHSCHEME3_NEW[-4:]:
    print("   ", ln)
