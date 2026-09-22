"""Scratch: build and verify the three _AUTH_SCHEME_SPLIT source lines only."""
B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
FL = " " * 22
DQ = B + Q
SQ = S

L1 = ("_AUTH_SCHEME_SPLIT = (r" + Q + "(?:" + Q + " + _AUTH_SCHEME_TOKEN + r" + Q
      + ")[ @T@]*" + Q)
L2 = (FL + "r" + Q + "(?:(?:" + Q + " + _AUTH_SCHEME_DELIMS + r" + Q
      + ")[ @T@]*@N@[ @T@]*)*" + Q)
body = ("(?:(?:" + Q + " + _AUTH_SCHEME_DELIMS + r" + Q + ")+|" + DQ + "[^" + DQ
        + "@N@]*" + DQ + "|" + SQ + "[^" + SQ + "@N@]*" + SQ)
L3 = FL + "r" + Q + body + ")" + Q

print("L1:", L1)
print("L2:", L2)
print("L3:", L3)
print()
resolved = "\n".join([L1, L2, L3]).replace("_AUTH_SCHEME_DELIMS", "_DELIM")
resolved = resolved.replace("@T@", B + "t").replace("@N@", B + "r?" + B + "n")
print("--- resolved source ---")
print(resolved)
ns = {"_DELIM": J}
exec(resolved, ns)
print("exec OK")
got = ns["_AUTH_SCHEME_SPLIT"]
want = (r"(?:[A-Za-z][A-Za-z0-9!#$%&" + S + r"*+.^_`|~-]*)[ " + B + "t]*(?:(?:"
        + J + r")[ " + B + "t]*" + B + "r?" + B + "n[ " + B + "t]*)*(?:(?:" + J
        + r")+|\"[^\"" + B + "r" + B + "n]*\"|'[^'" + B + "r" + B + "n]*')")
print("SEMANTICS MATCH:", got == want)
print("got =", repr(got))
