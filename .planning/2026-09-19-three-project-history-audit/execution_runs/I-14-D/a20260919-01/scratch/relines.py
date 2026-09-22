"""Scratch: final structural fix of the r3 template block.

`_AUTH_SCHEME_SPLIT` is defined in `_AUTH_SCHEME_SPLIT_SRC`, a list whose THREE
elements are the three source lines of that definition; the template element is then
its first line (quoted) followed by the other two (unquoted continuations).  Built
entirely from chr() codes; compiled, imported and exec'd before writing.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
Q = chr(34)
S = chr(39)
B = chr(92)
SP = " "
FL = SP * 22
NAME = "_AUTH_SCHEME_DELIMS"

FT = "[" + SP + B + B + "t]*"
FRN = B + B + "r?" + B + B + "n"
FJQ = B + B + Q
FDQ = FJQ + "[^" + FJQ + B + B + "r" + B + B + "n]*" + FJQ
FSQ = S + "[^" + S + B + B + "r" + B + B + "n]*" + S

src1 = ('_AUTH_SCHEME_SPLIT = (r' + Q + '(?:' + Q + ' + _AUTH_SCHEME_TOKEN + r' + Q
        + ')' + FT + Q)
src2 = (FL + 'r' + Q + '(?:(?:' + Q + ' + ' + NAME + ' + r' + Q + ')' + FT + FRN
        + FT + ')*' + Q)
src3 = (FL + 'r' + Q + '(?:(?:' + Q + ' + ' + NAME + ' + r' + Q + ')+|' + FDQ + '|'
        + FSQ + ')' + Q + ')' + Q + ')')

new_lines = [
    '# the r3 definition, one element per source line, so the template below can carry',
    '# it verbatim (any edit here must keep the three-line shape).',
    '_AUTH_SCHEME_SPLIT_SRC = [',
    '    ' + repr(src1) + ',',
    '    ' + repr(src2) + ',',
    '    ' + repr(src3) + ',',
    ']',
    '# the template element for those three lines: first line quoted (the element), the',
    '# other two as unquoted concatenations that complete that element.',
    '    ' + repr(src1) + ',',
    '    ' + src2,
    '    + ' + repr(src3) + ',',
]

lines = P.read_text(encoding="utf-8").split("\n")
print("replacing lines 237..239:")
for i in (236, 237, 238):
    print("   ", i + 1, repr(lines[i]))
lines[236:239] = new_lines
for ln in new_lines:
    print("   +", repr(ln))

compile("\n".join(lines), "<probe>", "exec")
print("edited module compiles OK")
P.write_text("\n".join(lines), encoding="utf-8")

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("module imports OK; emitted r3 tail:")
for ln in m.AUTHSCHEME3_NEW[-6:]:
    print("   ", ln)
ns = {"_AUTH_SCHEME_TOKEN": r"[A-Za-z][A-Za-z0-9!#$%&" + S + r"*+.^_`|~-]*",
      NAME: r'[^\s,;&\"' + S + r'|]'}
exec("\n".join(m.AUTHSCHEME3_NEW[-5:]), ns)
print()
print("emitted SPLIT =", ns["_AUTH_SCHEME_SPLIT"])
