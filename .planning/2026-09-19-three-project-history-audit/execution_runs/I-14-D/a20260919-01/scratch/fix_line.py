"""Scratch: one deterministic fix of the doubled backslash in the r3 template line.

The intended emitted product source line is:

    '                      r"(?:' + _AUTHJOIN_CLASS + r'[ \t]*\r?\n[ \t]*)*"'

whose Python-literal spelling inside apply_i14d_narrow.py is

    '                      r"(?:' + _AUTHJOIN_CLASS + r'[ \\t]*\\r?\\n[ \\t]*)*"'

i.e. exactly ONE backslash before each `t`/`r?`/`n` in the file.  This script rewrites
that one line by construction (no hand escaping) and proves it changed.
"""
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
B = chr(92)
Q = chr(34)
S = chr(39)

# the file text for the line, built from named pieces (one backslash each)
target_file_text = (
    "'                      r" + Q + "(?:" + S + " + _AUTHJOIN_CLASS + r"
    + S + "[" + B + "t]*" + B + "r?" + B + "n[" + B + "t]*)*" + Q + "'"
)
# the same line WITHOUT the extra backslash (the current, broken state)
broken_file_text = target_file_text.replace(B + "t", B + B + "t").replace(
    B + "r?", B + B + "r?").replace(B + "n[", B + B + "n[")

raw = P.read_text(encoding="utf-8")
lines = raw.split("\n")
hits_target = [i for i, ln in enumerate(lines) if ln.strip() == target_file_text.strip()]
hits_broken = [i for i, ln in enumerate(lines) if ln.strip() == broken_file_text.strip()]
print("target line already present at:", hits_target)
print("broken line present at:", hits_broken)

if hits_target and not hits_broken:
    print("nothing to do")
elif len(hits_broken) == 1:
    lines[hits_broken[0]] = target_file_text
    P.write_text("\n".join(lines), encoding="utf-8")
    print("rewrote line", hits_broken[0] + 1)
else:
    raise SystemExit("FIX-REFUSED: cannot identify exactly one line to rewrite")

# prove it
raw2 = P.read_text(encoding="utf-8")
lines2 = raw2.split("\n")
print("now target at:", [i for i, ln in enumerate(lines2) if ln.strip() == target_file_text.strip()])
print(repr(target_file_text))
