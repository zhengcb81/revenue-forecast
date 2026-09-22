"""Scratch: debug the parenthesis balance of the three generated source lines."""
from pathlib import Path

import lines3  # noqa: F401  (imports the module, printing its own output first)

src = "\n".join([lines3.L1, lines3.L2, lines3.L3])
src = src.replace("_AUTH_SCHEME_DELIMS", "_DELIM")
src = src.replace("@T@", chr(92) + "t").replace("@N@", chr(92) + "r?" + chr(92) + "n")
print()
print("=== lines with index ===")
for i, ln in enumerate(src.split("\n")):
    print(i, repr(ln))
print()
Q = chr(34)
depth = 0
instr = None
for i, ln in enumerate(src.split("\n")):
    for ch in ln:
        if instr:
            if ch == instr:
                instr = None
            continue
        if ch in (Q, chr(39)):
            instr = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    print(f"line {i}: depth after = {depth}  instr={instr}")
print()
out = Path(__file__).resolve().parent / "resolved3.txt"
out.write_text(src, encoding="utf-8")
print("wrote", out)
ns = {"_DELIM": lines3.J}
exec(src, ns)
print("exec OK:", ns["_AUTH_SCHEME_SPLIT"])
