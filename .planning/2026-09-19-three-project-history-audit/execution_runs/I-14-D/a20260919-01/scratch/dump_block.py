"""Scratch: dump the r3 block generate by apply_i14d_narrow.py and exec it."""
import importlib.util
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("applymod", A / "harness" / "apply_i14d_narrow.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print("=== generated r3 block (last 5 source lines) ===")
for ln in m.AUTHSCHEME3_NEW[-5:]:
    print(repr(ln))

print()
print("=== can the emitted block be exec'd as product source? ===")
# the token literal is a COMMENT in the emitted source (documentation only, exactly as
# the r2 block documented its enumeration), so the check supplies it the way the
# product file would if it were uncommented.
ns = {"_AUTHJOIN_CLASS": m._AUTHJOIN_CLASS,
      "_AUTH_SCHEME_TOKEN": r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"}
src = "\n".join(m.AUTHSCHEME3_NEW)
out = Path(__file__).resolve().parent / "emitted_block_r3.txt"
out.write_text(src, encoding="utf-8")
print("wrote", out)
compile(src, "<emitted>", "exec")
exec(src, ns)
print("compile+exec OK")
print("_AUTH_SCHEME_SPLIT =", repr(ns["_AUTH_SCHEME_SPLIT"]))
print()
print("=== r2 definition for comparison ===")
print(repr(m.AUTHSCHEME_NEW[-2]))
print()
print("=== line counts ===")
print("r2 block lines:", len(m.AUTHSCHEME_NEW))
print("r3 block lines:", len(m.AUTHSCHEME3_NEW))
print("ops:", sorted(m.OPS))
