"""Scratch: read the authored product lines, verify semantics, print their reprs."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = chr(92)
src = (HERE / "emitted_r3_product.txt").read_text(encoding="utf-8")
print("=== authored source ===")
print(src)
ns = {}
exec(src, ns)
print("_AUTH_SCHEME_SPLIT =", ns["_AUTH_SCHEME_SPLIT"])
expected = (r"(?:[A-Za-z][A-Za-z0-9!#$%&" + chr(39) + r"*+.^_`|~-]*)[ " + B + "t]*(?:"
            + ns["_AUTHJOIN_CLASS"] + r"*[ " + B + "t]*" + B + "r?" + B + "n[ "
            + B + "t]*)*(?:" + ns["_AUTHJOIN_CLASS"] + r"+|\"[^\""
            + B + "r" + B + "n]*\"|'[^'" + B + "r" + B + "n]*')")
print("MATCH:", ns["_AUTH_SCHEME_SPLIT"] == expected)
print()
print("=== repr of each line (what the harness list must hold) ===")
for ln in src.splitlines():
    print(repr(ln))
