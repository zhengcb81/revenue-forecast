"""Scratch: fix the placeholder-resolution line of apply_i14d_narrow.py."""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
Q = chr(34)
S = chr(39)

good = ("    ln.replace(" + Q + "_AUTH_SCHEME_DELIMS" + Q + ", " + Q + "_AUTHJOIN_CLASS"
        + Q + ")" + chr(10)
        + "      .replace(" + Q + "@T@" + Q + ", _AUTHSCHEME3_PLACEHOLDERS[" + Q
        + "@T@" + Q + "])" + chr(10)
        + "      .replace(" + Q + "@N@" + Q + ", _AUTHSCHEME3_PLACEHOLDERS[" + Q
        + "@N@" + Q + "])")

lines = P.read_text(encoding="utf-8").split("\n")
idx = next(k for k, ln in enumerate(lines) if ln.strip().startswith("ln.replace("))
print("old:", repr(lines[idx]))
lines[idx] = good
src = "\n".join(lines)
compile(src, "<probe>", "exec")
print("compiles OK")
P.write_text(src, encoding="utf-8")

spec = importlib.util.spec_from_file_location("applymod", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("imports OK; emitted r3 definition:")
for ln in m.AUTHSCHEME3_NEW[-4:]:
    print("   ", ln)
print("ops:", sorted(m.OPS))
