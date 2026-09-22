"""Scratch: minimal reproduction of the C10/C11 miss."""
import re

J = r'[^\s,;&\"\x27|]'
T = r'[A-Za-z][A-Za-z0-9!#$%&' + "\x27" + r'*+.^_`|~-]*'
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"

variants = {
    "A current": r"(?:" + T + r")[ \t]*(?:" + J + r"[ \t]*\r?\n[ \t]*)*(?:" + J + r"+)",
    "B lead-nl": r"(?:" + T + r")[ \t]*(?:\r?\n[ \t]*)(?:" + J + r"[ \t]*\r?\n[ \t]*)*(?:" + J + r"+)",
    "C no-class": r"(?:" + T + r")[ \t]*(?:abc[ \t]*\r?\n[ \t]*)*(?:" + J + r"+)",
    "D simple":  r"(?:" + T + r")[ \t]*(?:" + J + r"*[ \t]*\r?\n[ \t]*)*(?:" + J + r"+)",
}

for name, pat in variants.items():
    p = re.compile(pat)
    print("==", name)
    print("   ", pat)
    for t in ["Bearer abc\n" + SEC, "Bearer\n" + SEC, "Bearer\n\n" + SEC]:
        m = p.match(t)
        print("   ", repr(t[:16]), "->", repr(m.group(0)) if m else None)
    print("    J+ vs 'abc'   :", re.match(J + "+", "abc"))
    print("    grp vs 'abc\\n':", re.match(r"(?:" + J + r"[ \t]*\r?\n[ \t]*)*", "abc\n"))
