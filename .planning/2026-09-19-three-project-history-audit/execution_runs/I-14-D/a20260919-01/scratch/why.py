"""Scratch: why does the scheme token swallow '\n'?"""
import re

T = "[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
print("T matches 'Bearer\\nabc':", repr(re.match(T, "Bearer\nabc").group(0)))
print("T matches 'Bearer abc':", repr(re.match(T, "Bearer abc").group(0)))
print("full T:", T)
print()
TE = re.compile(T)
for s in ("Bearer\nabc", "Bearer abc", "Bearer", "BearerX"):
    m = TE.match(s)
    print(f"  {s!r:20s} -> {m.group(0)!r}" if m else f"  {s!r:20s} -> None")
print()
# the character class as written, expanded
print("class chars:", T[9:-2])
