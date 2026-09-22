"""Scratch: author the FINAL r3 block template (comments + definition source lines).

Shape (the r2 branch with the nine-word enumeration replaced by one RFC-7235 token,
a run of line breaks, and a quoted continuation):

    _AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ \t]*"
                          r"(?:\r?\n[ \t]*)+"
                          r"(?:" + _AUTH_BARE_VALUE + r"|\"[^\"\r\n]*\"|'[^'\r\n]*')")

Measured against the reviewer's 12 residual variants and against every row of this
attempt's own oracle and rule table: closes C1-C9 and C12 (the whole non-enumerated
scheme family, which is F-REV-R2-01), keeps every existing expectation, and leaves
exactly two variants open (C10 two-token-then-wrap, C11 blank-line).  Those two are
mutually exclusive with `doc=17` surviving `Authorization: Bearer <M>\ndoc=17\nstage=…`
in the assignment path: a sweep over the whole design space (star/optional/one-token
pre-break groups x single/run line breaks x token/quoted/break-run tails) found no
shape that closes them without deleting that diagnostic.  They are therefore
REGISTERED rather than silently left out.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
FL = " " * 22

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
    "# reached through the same break run - is redacted.  The break and any",
    "# indentation stay OUTSIDE the match, so the diagnostic keys on the following",
    "# lines survive (the C13 half this card fixes).",
    "# The value delimiters are the same class `_AUTH_BARE_VALUE` uses.  Measured as",
    "# review findings F-REV-D-01 / F-REV-R2-01: without this branch the full",
    "# credential is persisted in the append-only event log.",
    "# Deliberate, registered cost (F-REV-R2-02): it cannot tell a wrapped credential",
    "# from a diagnostic key, so `Authorization: Bearer` + newline DELETES `doc=17`.",
    "# Two shapes stay OPEN and are registered in the oracle and the rule table: the",
    "# two-token value that then wraps (`Authorization: Bearer abc` + newline + secret)",
    "# and the blank-line form.  Closing either one requires the scheme's own line to",
    "# be consumed as a token run, which deletes `doc=17` from",
    "# `Authorization: Bearer <marker>` + newline + `doc=17` + newline + `stage=…` -",
    "# measured, not assumed; see r3_fix_record.md.",
]
TOK = '_AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&' + S + '*+.^_`|~-]*"'
L1 = ('_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ @T@]*"')
L2 = (FL + 'r"(?:(?<N>@N@)[ @T@]*)+"')
L3 = (FL + 'r"(?:" + _AUTH_SCHEME_DELIMS + r"|\\"[^\\"@N@]*\\"|\'[^\'@N@]*\')")')

lines = COMMENT + [TOK, L1, L2, L3]
out = HERE / "r3_block_template.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "with", len(lines), "lines")
for ln in lines[-3:]:
    print(ln)
