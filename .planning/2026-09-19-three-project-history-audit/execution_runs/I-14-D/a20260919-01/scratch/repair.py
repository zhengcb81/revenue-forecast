"""Scratch: repair the damaged lines of the r3 template in apply_i14d_narrow.py.

Rewrites the two lines that a bad edit merged/duplicated, then proves the module
imports.  Every string here is built from chr() codes, so the repair itself needs no
quoting of its own.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
Q = chr(34)
S = chr(39)
B = chr(92)

# the intended single statement, as file text.  A raw string in the product needs the
# TWO characters backslash-t, so the file must hold `\t` written as an escaped
# backslash (B+B) followed by t; the same for `\r?\n`.
T2 = B + B + "t"
R2 = B + B + "r?" + B + B + "n"
line237 = (
    S + " " * 22 + "r"
    + Q + "(?:" + S + " + _AUTHJOIN_CLASS + r"
    + Q + "*[" + T2 + "]*" + R2 + "[" + T2 + "]*)*"
    + Q + S + ","
)
print("reconstructed line 237 =", repr(line237))
# sanity: it must itself be valid Python source for a one-element list
compile("[\n" + line237 + "\n]", "<probe>", "exec")
print("reconstructed line compiles OK")
assign_line = "AUTHSCHEME3_NEW = list(AUTHSCHEME3_NEW_TEMPLATE)"

lines = P.read_text(encoding="utf-8").split("\n")
print("line 237 has two statements:", lines[236].count("r" + Q + "(?:" + S) == 2)
print("line 240 is the stale duplicate:", lines[239].strip() == assign_line)
print("line 247 is the kept assignment:", lines[246].strip() == assign_line)

lines[236] = line237
del lines[239]      # remove the stale earlier duplicate; the later one stays
P.write_text("\n".join(lines), encoding="utf-8")
print("repaired; short of two lines ->", len(lines))

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("module imports OK")
print("last 4 emitted r3 lines:")
for ln in m.AUTHSCHEME3_NEW[-4:]:
    print("   ", ln)
