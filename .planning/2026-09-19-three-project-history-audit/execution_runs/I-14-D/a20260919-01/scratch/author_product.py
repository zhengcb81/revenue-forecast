"""Scratch: author the exact emitted r3 product source lines, byte by byte.

The product line needs, literally:
    _AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
    _AUTHJOIN_CLASS = r'[^\s,;&\"'|]'
    _AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ \t]*"
                          r"(?:" + _AUTHJOIN_CLASS + r"*[ \t]*\r?\n[ \t]*)*"
                          r"(?:" + _AUTHJOIN_CLASS + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")

This writes those lines to scratch/emitted_r3_product.txt for inspection.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = chr(92)
Q = chr(34)
S = chr(39)
SP = " "
T = B + "t"
RN = B + "r?" + B + "n"
J = "[^" + B + "s,;&" + B + Q + S + "|]"

lines = [
    "_AUTH_SCHEME_TOKEN = r" + Q + "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*" + Q,
    "_AUTHJOIN_CLASS = r" + S + J + S,
    '_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[' + SP + T + ']*"',
    "                      r\"(?:\" + _AUTHJOIN_CLASS + r\"*[" + SP + T + "]*"
    + RN + "[" + SP + T + "]*)*\"",
    "                      r\"(?:\" + _AUTHJOIN_CLASS + r\"+|" + B + Q + "[^" + B + Q
    + B + "r" + B + "n]*" + B + Q + "|" + S + "[^" + S + B + "r" + B + "n]*" + S
    + ")\")",
]
out = HERE / "emitted_r3_product.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out)
for ln in lines:
    print(ln)
print()
ns = {}
exec("\n".join(lines), ns)
print("_AUTH_SCHEME_SPLIT =", repr(ns["_AUTH_SCHEME_SPLIT"]))
expected = (r"(?:[A-Za-z][A-Za-z0-9!#$%&" + S + r"*+.^_`|~-]*)[ " + T + "]*(?:"
            + J + r"*[ " + T + r"]*" + RN + r"[ " + T + r"]*)*(?:" + J
            + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
print("expected           =", repr(expected))
print("MATCH:", ns["_AUTH_SCHEME_SPLIT"] == expected)
