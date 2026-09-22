"""Scratch: build + verify the exact r3 source lines for _AUTH_SCHEME_SPLIT."""
B = chr(92)   # backslash
Q = chr(34)   # "
S = chr(39)   # '
T = B + "t"   # the two characters  \t
R = B + "r?" + B + "n"   # the six characters  \r?\n
J = "@J@"     # placeholder for the name _AUTHJOIN_CLASS
SP = " "      # a single space

L1 = '_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[' + SP + T + ']*"'
L2 = ('                      r"(?:' + R + "[" + SP + T + "]*)(?:" + J
      + "[" + SP + T + "]*" + R + "[" + SP + T + "]*)*\"")
L3 = ('                      r"(?:" + ' + J + ' + r"+|' + B + Q + '[^' + B + Q
      + B + "r" + B + "n]*" + B + Q + "|" + S + "[^" + S + B + "r" + B + "n]*"
      + S + ')"' + ")")

TOKEN_LINE = '_AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&' + S + '*+.^_`|~-]*"'

print("=== emitted r3 definition (as it will appear in the product file) ===")
for ln in (L1, L2, L3):
    print(ln)
print()
print("=== repr (what the template list must hold) ===")
for ln in (L1, L2, L3):
    print(repr(ln))
print()

src = "\n".join([TOKEN_LINE, L1.replace(J, "_AUTHJOIN_CLASS"),
                 L2.replace(J, "_AUTHJOIN_CLASS"), L3.replace(J, "_AUTHJOIN_CLASS")])
print("=== assembled source that must compile ===")
print(src)
compile(src, "<x>", "exec")
ns = {"_AUTHJOIN_CLASS": r'[^\s,;&\"' + S + r'|]'}
exec(src, ns)
print()
print("_AUTH_SCHEME_SPLIT =", repr(ns["_AUTH_SCHEME_SPLIT"]))
print("expected           =", repr(r"(?:[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*)[ \t]*(?:\r?\n[ \t]*)(?:[^\s,;&\"'|][ \t]*\r?\n[ \t]*)*(?:[^\s,;&\"'|]+|\"[^\"\r\n]*\"|'[^'\r\n]*')"))
