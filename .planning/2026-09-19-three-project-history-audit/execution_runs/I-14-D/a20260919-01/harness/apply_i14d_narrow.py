"""I-14-D: apply the bare-value narrowing to an iso tree's observability.py.

Byte-exact, line-based, CRLF-preserving.  Every replacement asserts the OLD text
occurs exactly once before writing.  Operations:

    narrow     apply the full I-14-D narrowing            (product_base -> product_narrow)
    mut_greedy M1: from narrow, restore the scanner multi-word loop
    mut_authnl M2: from narrow, auth token join back to \\s+
    mut_auth1  M3: from narrow, auth value reduced to a strict single token

r2 (review F-REV-D-01 / reviewer RULING 2) adds the scheme-aware fail-closed auth
value.  Three more operations, all from the r2 narrow tree:

    mut_authsplit M4: remove the `_AUTH_SCHEME_SPLIT` branch from the auth value
                      group (and its comment block).  This is the tree that
                      re-opens the auth newline-split credential leak, so the
                      M4 arm covers the LEAK direction the M1/M2/M3 plan missed.
    authsplit / collapse_authsplit
                      the two halves of that edit, kept separate so the fix and
                      its mutant are built from the same text (see OPS).

    python apply_i14d_narrow.py --op narrow --tree <iso>/<tree>
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REL = Path("src") / "company_wiki" / "source_catalog" / "observability.py"

# ---------------------------------------------------------------- blocks (text)


def block(s: str) -> list[str]:
    return s.split("\n")


COMMENT_OLD = block(
"""# A value is the whole rest of the field: a quoted string, or every space/tab
# separated token up to the next punctuation delimiter.  The multi-word form is
# required by real shapes such as ``Authorization: Bearer <secret>`` and
# ``Authorization: token <secret>`` - a single-token rule would redact only the
# scheme and leave the secret in place.
_QUOTED_VALUE = r"\\"[^\\"\\r\\n]*\\"|'[^'\\r\\n]*'"
_BARE_VALUE = r"[^\\s,;&\\"'|]+(?:\\s+[^\\s,;&\\"'|]+)*"
_VALUE = r"(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"

_AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + _LEFT_ANCHOR + r"authorization\\s*[:=]\\s*|"
    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"
)""")

COMMENT_NEW = block(
"""# A value is a quoted string, or - since I-14-D narrowed the r1 greedy rule - a
# BOUNDED run of non-delimiter tokens (delimiters: any whitespace, , ; & " ' |):
#   _BARE_VALUE      ONE token: the assignment scanner stops at ANY whitespace,
#                    including newlines (C13: the r1 rule crossed newlines and
#                    deleted the whole remaining diagnostic block, 112 in -> 34 out).
#   _AUTH_BARE_VALUE the authorization/bearer value: tokens joined by INLINE
#                    whitespace only, so it still carries one scheme word
#                    ("Bearer <secret>", "token <secret>") but can no longer
#                    swallow a multi-line diagnostic block either.
# Declared residual: a bare secret containing whitespace is redacted only up to
# its first token ("password: iron steel" -> "password: <redacted> steel");
# quote the value ("password: 'iron steel'") for full coverage.
_QUOTED_VALUE = r"\\"[^\\"\\r\\n]*\\"|'[^'\\r\\n]*'"
_BARE_VALUE = r"[^\\s,;&\\"'|]+"
_VALUE = r"(?P<value>" + _QUOTED_VALUE + r"|" + _BARE_VALUE + r")"
_AUTH_BARE_VALUE = r"[^\\s,;&\\"'|]+(?:[ \\t]+[^\\s,;&\\"'|]+)*"

_AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + _LEFT_ANCHOR + r"authorization\\s*[:=]\\s*|"
    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" + _AUTH_BARE_VALUE + r")"
)""")

SCANNER_OLD = block(
"""            value_end = value_start
            while True:
                while (value_end < length
                       and text[value_end] not in _VALUE_STOP_CHARS
                       and not text[value_end].isspace()):
                    value_end += 1
                if value_end == value_start:
                    break                          # no value at all: leave the text alone
                lookahead = value_end
                while lookahead < length and text[lookahead].isspace():
                    lookahead += 1
                if (lookahead < length
                        and text[lookahead] not in _VALUE_STOP_CHARS
                        and not text[lookahead].isspace()):
                    value_end = lookahead              # multi-word value, as before
                else:
                    break""")

SCANNER_NEW = block(
"""            # I-14-D (C13 narrowing): the value is ONE token.  It stops at any
            # whitespace INCLUDING newlines, so a diagnostic key after the
            # credential (`doc=17`, `stage=...` on the next line) survives.
            # value_end == value_start after the loop means "no value at all";
            # the `value_end <= value_start` guard below leaves the text alone,
            # exactly as before.
            value_end = value_start
            while (value_end < length
                   and text[value_end] not in _VALUE_STOP_CHARS
                   and not text[value_end].isspace()):
                value_end += 1""")

# ------------------------------------------------ r2: scheme-aware fail-closed

# the redactor's char class contains a backslash-quote then a BARE single quote
# ([^\s,;&\"'|]) - compose the line so the quote stays bare (a raw \' would add
# an extra backslash).
_AUTHJOIN_CLASS = r'[^\s,;&\"' + "'" + r'|]'

# The comment + definition block inserted ahead of _AUTH_PATTERN.  It has to sit
# between `_AUTH_BARE_VALUE` and `_AUTH_PATTERN` (not before the former) because
# the M2 anchor is the `_AUTH_BARE_VALUE` line itself and must keep matching.
AUTHSCHEME_NEW = [
    "# A value may still cross ONE line break, but only behind a *known* scheme word.",
    "# A wrapped header (`Authorization: Bearer` then the secret on the next line) or",
    "# an RFC-7230 obs-fold puts the secret on a line that carries no `key=` prefix,",
    "# so once the scheme word alone is consumed neither this pattern nor the",
    "# assignment scanner can see it.  Fail CLOSED: after a known scheme word and",
    "# exactly one line break, the first token is redacted.  The break and any",
    "# indentation stay OUTSIDE the match, so the diagnostic keys on the following",
    "# lines survive (the C13 half this card fixes).  The value delimiters are the",
    "# same as _AUTH_BARE_VALUE.  Measured as review finding F-REV-D-01: without",
    "# this branch the full credential is persisted in the append-only event log.",
    '_AUTH_SCHEME_SPLIT = (r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"',
    '                      r"[ \\t]*\\r?\\n[ \\t]*' + _AUTHJOIN_CLASS + '+")',
]

# NB: the tree keeps `_AUTH_PATTERN`'s value group on ONE physical line, so the
# anchors below are single-element blocks (the implicit string concatenation is
# only how this file spells that long line).
AUTHVALUE_NARROW_OLD = [
    '    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    '+ _AUTH_BARE_VALUE + r")"',
]

AUTHVALUE_NARROW_NEW = [
    '    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    '+ _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"',
]

# the value group with the scheme branch removed again (M4 specimen)
AUTHVALUE_NOSCHEME = AUTHVALUE_NARROW_OLD

# Insertion pair for the new block.  The anchor is the `_AUTH_PATTERN = re.compile(`
# line (unique in the file); the block is inserted AHEAD of it, after the blank line
# that already separates it from `_AUTH_BARE_VALUE`.  That keeps the file's blank-line
# layout and leaves every other op's anchors - in particular M2's `_AUTH_BARE_VALUE`
# line - exactly where they were.
AUTHPATTERN_HEAD = ["_AUTH_PATTERN = re.compile("]
AUTHSCHEME_INSERT = AUTHSCHEME_NEW + AUTHPATTERN_HEAD

AUTHJOIN_NARROW_LINE = (
    r'_AUTH_BARE_VALUE = r"' + _AUTHJOIN_CLASS
    + r'+(?:[ \t]+' + _AUTHJOIN_CLASS + r'+)*"')
AUTHJOIN_MUT_LINE = (
    r'_AUTH_BARE_VALUE = r"' + _AUTHJOIN_CLASS
    + r'+(?:\s+' + _AUTHJOIN_CLASS + r'+)*"')
AUTHVALUE_NARROW_LINE = (
    r'    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    r'+ _AUTH_BARE_VALUE + r")"'
)
AUTHVALUE_MUT_LINE = (
    r'    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    r'+ _BARE_VALUE + r")"'
)

OPS = {
    # op -> list of (old_block, new_block) line-sequence replacements
    "narrow": [(COMMENT_OLD, COMMENT_NEW), (SCANNER_OLD, SCANNER_NEW)],
    "reverse": [(COMMENT_NEW, COMMENT_OLD), (SCANNER_NEW, SCANNER_OLD)],
    "mut_greedy": [(SCANNER_NEW, SCANNER_OLD)],
    "mut_authnl": [(block(AUTHJOIN_NARROW_LINE), block(AUTHJOIN_MUT_LINE))],
    "mut_auth1": [(block(AUTHVALUE_NARROW_LINE), block(AUTHVALUE_MUT_LINE))],
    # r2 fix (reviewer RULING 2) and its mutant specimen.  `authsplit` inserts the
    # `_AUTH_SCHEME_SPLIT` block (the M2 `_AUTH_BARE_VALUE` anchor is untouched) and
    # then re-orders the value group.  `collapse_authsplit` only undoes the second
    # half, which leaves an unused-but-defined constant and re-opens the leak: it is
    # a knife-edge specimen, NOT used by the mutation plan.  `mut_authsplit` undoes
    # both halves, i.e. it is the r2 tree as if the fix had never been written.
    "authsplit": [
        (AUTHPATTERN_HEAD, AUTHSCHEME_INSERT),
        (AUTHVALUE_NARROW_OLD, AUTHVALUE_NARROW_NEW),
    ],
    "collapse_authsplit": [(AUTHVALUE_NARROW_NEW, AUTHVALUE_NOSCHEME)],
    "mut_authsplit": [
        (AUTHSCHEME_INSERT, AUTHPATTERN_HEAD),
        (AUTHVALUE_NARROW_NEW, AUTHVALUE_NOSCHEME),
    ],
}


def apply_op(lines: list[str], op: str) -> list[str]:
    eol = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
    for old_block, new_block in OPS[op]:
        old = [ln + eol for ln in old_block]
        new = [ln + eol for ln in new_block]
        n = len(old)
        hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == old]
        if len(hits) != 1:
            raise SystemExit(
                f"PATCH-REFUSED: {op}: anchor block matches {len(hits)} times "
                f"(need exactly 1); tree does not have the expected pre-image")
        i = hits[0]
        lines = lines[:i] + new + lines[i + n:]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--op", required=True, choices=sorted(OPS))
    parser.add_argument("--tree", required=True)
    args = parser.parse_args()

    path = Path(args.tree) / REL
    raw = path.read_bytes()
    if raw.count(b"\r\n") != raw.count(b"\n"):
        raise SystemExit("PATCH-REFUSED: mixed line endings, refusing to guess")
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    patched = apply_op(lines, args.op)
    out = "".join(patched).encode("utf-8")
    path.write_bytes(out)
    print(f"op={args.op} tree={args.tree}")
    print(f"observability.py sha256: {hashlib.sha256(out).hexdigest()}")
    print(f"bytes: {len(out)} (was {len(raw)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
