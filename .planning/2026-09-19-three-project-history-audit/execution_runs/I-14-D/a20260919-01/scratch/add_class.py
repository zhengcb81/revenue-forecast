"""Scratch: add the product's delimiter-class line ahead of the split definition.

The emitted split definition references `_AUTHJOIN_CLASS` by name, and the product file
defines that constant further down, so the r3 block must define it first.  This inserts a
literal-assignment line (built from chr() codes) before the split line and re-checks that
the module compiles and imports.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
B = chr(92)
Q = chr(34)
S = chr(39)

lines = P.read_text(encoding="utf-8").split("\n")
idx = next(k for k, ln in enumerate(lines)
           if "_AUTH_SCHEME_SPLIT = (r" in ln and ln.strip().startswith("'"))
print("target line", idx + 1, ":", repr(lines[idx]))

# the emitted product source line, as a template element
emit = ("_AUTHJOIN_CLASS = " + Q + "[^" + B + "s,;&" + B + Q + S + "|]" + Q
        + "   # the scanner's value delimiter class")
new_line = "    " + repr(emit) + ","
lines.insert(idx, new_line)
print("inserted:", repr(new_line))

src = "\n".join(lines)
compile(src, "<probe>", "exec")
print("compiles OK")
P.write_text(src, encoding="utf-8")

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("imports OK; emitted r3 definition now:")
for ln in m.AUTHSCHEME3_NEW[-5:]:
    print("   ", ln)
