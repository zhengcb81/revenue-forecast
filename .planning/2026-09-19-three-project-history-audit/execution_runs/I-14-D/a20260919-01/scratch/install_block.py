"""Scratch: replace the r3 template region of apply_i14d_narrow.py with the FINAL block.

The region runs from the `AUTHSCHEME3_TOKEN_LINE = (` line to the line before
`# Insertion pair for the new block.`.  The replacement is built from chr() codes and
compiles + imports before it is written.
"""
import importlib.util
from pathlib import Path

A = Path(__file__).resolve().parents[1]
P = A / "harness" / "apply_i14d_narrow.py"
B = chr(92)
Q = chr(34)
S = chr(39)
FL = " " * 22

START = "AUTHSCHEME3_TOKEN_LINE = ("
END = "# Insertion pair for the new block."

COMMENT = [
    "# A value may still cross line breaks, but only behind a single RFC-7235 scheme",
    "# token (r3).  The pre-break token used to be a nine-word enumeration, whose",
    "# coverage was exactly as wide as the list: `Authorization: Negotiate` + newline,",
    "# or any other scheme word, still persisted the credential - measured as",
    "# F-REV-R2-01, where the leaked string was this card's own synthetic marker.",
    "# It is now ONE RFC-7235 scheme token: `scheme = 1*<any CHAR except CTLs or",
    "# separators>`, which always begins with a letter, so the class starts with",
    "# `[A-Za-z]`; `|` is kept in it because the value delimiter class used everywhere",
    "# else already stops at `|`, so nothing can gain a delimiter by this widening.",
    "# A wrapped header (`Authorization: Bearer` then the secret on the next line) or",
    "# an RFC-7230 obs-fold puts the secret on a line that carries no `key=` prefix,",
    "# so once the scheme word alone is consumed neither this pattern nor the",
    "# assignment scanner can see it.  Fail CLOSED: after a scheme token and one or",
    "# more line breaks (a blank line included), the next token - or a quoted string,",
    "# reached through the same break run - is redacted.  The breaks and any",
    "# indentation stay OUTSIDE the match, so the diagnostic keys on the following",
    "# lines survive (the C13 half this card fixes).",
    "# The value delimiters are the same class `_AUTH_BARE_VALUE` uses.  Measured as",
    "# review findings F-REV-D-01 / F-REV-R2-01: without this branch the full",
    "# credential is persisted in the append-only event log.",
    "# Deliberate, registered cost (F-REV-R2-02): it cannot tell a wrapped credential",
    "# from a diagnostic key, so `Authorization: Bearer` + newline DELETES `doc=17`.",
    "# One shape stays OPEN and is registered rather than hidden: a TWO-token value",
    "# that then wraps (`Authorization: Bearer abc` + newline + secret).  Closing it",
    "# needs the scheme's own line consumed as a token run, which deletes `doc=17`",
    "# from `Authorization: Bearer <marker>` + newline + `doc=17` + newline + `stage=`",
    "# - measured across the whole design space, see r3_fix_record.md.",
]

# the emitted block: the token, then the generalized split definition
TOK = "_AUTH_SCHEME_TOKEN = r" + Q + "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*" + Q
L1 = '_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ @T@]*"'
L2 = FL + 'r"(?:(?:@N@)[ @T@]*)+"'
L3 = FL + 'r"(?:" + _AUTHJOIN_CLASS + r"+|\\"[^\\"@N@]*\\"|\'[^\'@N@]*\')")'

BLOCK = [repr(ln) + "," for ln in COMMENT]
BLOCK.append(repr(TOK) + ",")
BLOCK.append(repr(L1) + ",")
BLOCK.append(repr(L2) + ",")
BLOCK.append(repr(L3) + ",")
NEW_REGION = [
    "AUTHSCHEME3_NEW_TEMPLATE = [",
    *BLOCK,
    "]",
    "# The block is checked against the product once, here, so a placeholder that",
    "# cannot be resolved is a hard failure rather than a silently wrong pattern.",
    "_AUTHSCHEME3_PLACEHOLDERS = {",
    '    "@T@": chr(92) + "t",',
    '    "@N@": chr(92) + "r?" + chr(92) + "n",',
    "}",
    "AUTHSCHEME3_NEW = [",
    "    ln.replace(_AUTH_SCHEME_DELIMS, \"_AUTHJOIN_CLASS\")"
    ".replace(\"@T@\", _AUTHSCHEME3_PLACEHOLDERS[\"@T@\"])"
    ".replace(\"@N@\", _AUTHSCHEME3_PLACEHOLDERS[\"@N@\"])",
    "    for ln in AUTHSCHEME3_NEW_TEMPLATE",
    "]",
    "",
]

lines = P.read_text(encoding="utf-8").split("\n")
i = next(k for k, ln in enumerate(lines) if ln.startswith(START))
j = next(k for k, ln in enumerate(lines) if ln.startswith(END))
print(f"replacing lines {i + 1}..{j} ({j - i} lines)")
lines[i:j] = NEW_REGION
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
