"""Scratch: replace the r3 template region of apply_i14d_narrow.py, deterministically.

Only the single `AUTHSCHEME3_NEW_TEMPLATE = [ ... ]` literal is rewritten.  Each element
is authored as a pair (file-text prefix, product fragment) and assembled with chr()
codes, so no escaping is done by hand.  The module is compiled and imported BEFORE the
file is written, and the emitted product source is exec'd afterwards.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
B = chr(92)      # backslash
S = chr(39)      # '
Q = chr(34)      # "

# --- one entry per emitted product source line -----------------------------------
# `text` is the file text; `frag` is the product fragment it must produce.
ENTRIES = []


def add(py_repr: str, frag: str) -> None:
    """py_repr is the Python literal for this element; frag is the intended text."""
    ENTRY = ("    " + py_repr + ",")
    ENTRY_FRAG = frag
    ENTRIES.append((ENTRY, ENTRY_FRAG))


def q(x: str) -> str:
    """A single-quoted Python literal for x (x must not contain a single quote)."""
    assert S not in x, x
    return S + x + S


FL = " " * 22                    # continuation indent inside the product file
BT = B + "t"                     # product-side \t (2 chars)
RN = B + "r?" + B + "n"          # product-side \r?\n (6 chars)
# file-side spellings (doubled backslashes because the harness literal is not raw)
BTF = B + B + "t"
RNF = B + B + "r?" + B + B + "n"

add(q("_AUTH_SCHEME_TOKEN = r" + Q + "[A-Za-z][A-Za-z0-9!#$%&" + S
      + "*+.^_`|~-]*" + Q), "_AUTH_SCHEME_TOKEN = ...")
add(q("_AUTHJOIN_CLASS = ") + " + repr(_AUTHJOIN_CLASS) + " + q("   # the scanner's delimiter class"),
    "_AUTHJOIN_CLASS = ...")
add(q("_AUTH_SCHEME_SPLIT = (r" + Q + "(?:" + Q + " + _AUTH_SCHEME_TOKEN + r" + Q
      + ")[ " + BTF + "]*" + Q),
    "_AUTH_SCHEME_SPLIT = (r\"(?:\" + _AUTH_SCHEME_TOKEN + r\")[ " + BT + "]*\"")
add(q(FL + "r" + Q + "(?:" + Q + " + _AUTHJOIN_CLASS + " + S + "r" + Q + "*["
      + BTF + "]*" + RNF + "[" + BTF + "]*)*" + Q) + " + " + S + ",",
    FL + "r\"(?:\" + _AUTHJOIN_CLASS + r\"*[ " + BT + "]*" + RN + "[ " + BT + "]*)*\"")

print("entries:")
for e, f in ENTRIES:
    print("   ", e)
print()
print("fragments:")
for _e, f in ENTRIES:
    print("   ", f)
