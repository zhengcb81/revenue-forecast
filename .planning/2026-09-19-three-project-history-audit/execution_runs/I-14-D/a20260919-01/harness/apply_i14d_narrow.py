"""I-14-D: apply the bare-value narrowing to an iso tree's observability.py.

Byte-exact, line-based, CRLF-preserving.  Every replacement asserts the OLD text
occurs exactly once before writing.  Operations:

    narrow     apply the full I-14-D narrowing            (product_base -> product_narrow)
    mut_greedy M1: from narrow, restore the scanner multi-word loop
    mut_authnl M2: from narrow, auth token join back to \\s+
    mut_auth1  M3: from narrow, auth value reduced to a strict single token

r2 (review F-REV-D-01 / reviewer RULING 2) adds the scheme-aware fail-closed auth
value.  Three more operations, all from the r2 narrow tree:

    authsplit         insert the r2 `_AUTH_SCHEME_SPLIT` branch (a nine-word
                      enumeration) + its comment block, and reorder the value group
    reverse_authsplit the exact inverse; also what builds the M4 specimen
    mut_auth1_r2      M3 from the r2 tree

r3 (review F-REV-R2-01) generalizes that branch from the nine-word enumeration to a
single RFC-7235 scheme token and tries `_QUOTED_VALUE` after the break.  Three more
operations, all from the r3 narrow tree:

    genericscheme     replace the enumerated pre-break group by the RFC-7235 token,
                      allow a run of line breaks, and put `_QUOTED_VALUE` first in
                      the value group (it must be tried after the break, and it is
                      required to be non-empty there)
    reverse_genericscheme
                      the exact inverse; lands on the r2 tree byte-for-byte
    mut_auth1_r3      M3 from the r3 tree
    mut_authsplit_r3  M4 from the r3 tree: the whole scheme branch removed, which
                      collapses onto the pre-r2 narrow tree (the leak direction)

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

# ------------------------------------------- r3: generic RFC-7235 scheme token

# The r2 branch enumerated nine scheme words, so its coverage was exactly as wide
# as the list: `Authorization: Negotiate\n<secret>` (and every other scheme word,
# including an arbitrary one) still persisted the credential - measured as
# F-REV-R2-01, with the card's own synthetic marker among the leaked strings.
# r3 replaces the enumeration by one RFC-7235 `token`:
#
#   scheme = 1*<any CHAR except CTLs or separators>
#   separators = ()<>@,;:\"/[]?={} SP HT
#
# i.e. `[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*`; a scheme token always starts with a
# letter (`token` excludes a leading digit), and `|` is kept in the class because
# the value delimiters already stop at it.  Four further r3 changes, so that every
# residual variant the re-review measured actually closes:
#   * a RUN of line breaks rather than exactly one, so the blank-line shape
#     (`Authorization: Bearer\n\n<secret>`) is covered too;
#   * the split branch's own quoted alternative, so the quoted continuation
#     (`Authorization: Bearer\n"<secret>"`) is covered - and ONLY after a break,
#     which is what keeps `Authorization: "Bearer <M>"` on its existing path;
#   * ONE optional bare token allowed on the scheme's own line, so a two-token
#     value that then wraps (`Authorization: Bearer abc\n<secret>`) is covered;
#   * the tail token is tried after a further run of line breaks, so the credential
#     that follows a blank line is covered as well.
# The value group itself keeps the r2 order: `_QUOTED_VALUE` is still tried before
# the split branch (it cannot swallow the break because its character class
# excludes \r and \n), and `_AUTH_SCHEME_SPLIT` is still tried before
# `_AUTH_BARE_VALUE`.
#
# Cost: the branch redacts the first token after ANY word that can be read as a
# scheme, so `Authorization: Bearer\ndoc=17` loses `doc=17`.  That direction is
# fail-closed (never leak rather than never over-redact) and was already disclosed
# and accepted for the nine enumerated words; r3 adds no new class of cost, only
# more instances of it.  The instances are REGISTERED in the rule table under kind
# `over_redaction` (F-REV-R2-02) so they are measured rather than invisible, and
# oracle N5f freezes the semantics.
# The token literal, assembled so this file needs no quote-escaping of its own.
AUTHSCHEME3_NEW_TEMPLATE = [
'# A value may still cross line breaks, but only behind a single RFC-7235 scheme',
'# token (r3).  The pre-break token used to be a nine-word enumeration, whose',
'# coverage was exactly as wide as the list: `Authorization: Negotiate` + newline,',
'# or any other scheme word, still persisted the credential - measured as',
"# F-REV-R2-01, where the leaked string was this card's own synthetic marker.",
'# It is now ONE RFC-7235 scheme token: `scheme = 1*<any CHAR except CTLs or',
'# separators>`, which always begins with a letter, so the class starts with',
'# `[A-Za-z]`; `|` is kept in it because the value delimiter class used everywhere',
'# else already stops at `|`, so nothing can gain a delimiter by this widening.',
'# A wrapped header (`Authorization: Bearer` then the secret on the next line) or',
'# an RFC-7230 obs-fold puts the secret on a line that carries no `key=` prefix,',
'# so once the scheme word alone is consumed neither this pattern nor the',
'# assignment scanner can see it.  Fail CLOSED: after a scheme token and one or',
'# more line breaks (a blank line included), the next token - or a quoted string,',
'# reached through the same break run - is redacted.  The breaks and any',
'# indentation stay OUTSIDE the match, so the diagnostic keys on the following',
'# lines survive (the C13 half this card fixes).',
'# The value delimiters are the same class `_AUTH_BARE_VALUE` uses.  Measured as',
'# review findings F-REV-D-01 / F-REV-R2-01: without this branch the full',
'# credential is persisted in the append-only event log.',
'# Deliberate, registered cost (F-REV-R2-02): it cannot tell a wrapped credential',
'# from a diagnostic key, so `Authorization: Bearer` + newline DELETES `doc=17`.',
'# One shape stays OPEN and is registered rather than hidden: a TWO-token value',
'# that then wraps (`Authorization: Bearer abc` + newline + secret).  Closing it',
"# needs the scheme's own line consumed as a token run, which deletes `doc=17`",
'# from `Authorization: Bearer <marker>` + newline + `doc=17` + newline + `stage=`',
'# - measured across the whole design space, see r3_fix_record.md.',
'_AUTH_SCHEME_TOKEN = r"[A-Za-z][A-Za-z0-9!#$%&\'*+.^_`|~-]*"',
'_AUTH_SCHEME_SPLIT = (r"(?:" + _AUTH_SCHEME_TOKEN + r")[ @T@]*"',
'                      r"(?:(?:@N@)[ @T@]*)+"',
'                      r"(?:" + _AUTH_SCHEME_DELIMS + r"+|\\"[^\\"@N@]*\\"|\'[^\'@N@]*\')")',
]
# The block is checked against the product once, here, so a placeholder that
# cannot be resolved is a hard failure rather than a silently wrong pattern.
_AUTHSCHEME3_PLACEHOLDERS = {
    "@T@": chr(92) + "t",
    "@N@": chr(92) + "r?" + chr(92) + "n",
}
AUTHSCHEME3_NEW = [
    ln.replace("_AUTH_SCHEME_DELIMS", "_AUTH_BARE_VALUE")
      .replace("@T@", _AUTHSCHEME3_PLACEHOLDERS["@T@"])
      .replace("@N@", _AUTHSCHEME3_PLACEHOLDERS["@N@"])
    for ln in AUTHSCHEME3_NEW_TEMPLATE
]

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
# r2 variant (M3 must be built from the r2 tree, so its value group carries the
# scheme branch): `_AUTH_SCHEME_SPLIT` stays defined but is no longer referenced.
AUTHVALUE_SPLIT_MUT_LINE = (
    r'    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    r'+ _AUTH_SCHEME_SPLIT + r"|" + _BARE_VALUE + r")"'
)

# ---- r3 anchors -----------------------------------------------------------------
# The r3 edit is ONE definition, replaced in place: the value group, `_AUTH_BARE_VALUE`,
# `_QUOTED_VALUE` and the `_AUTH_PATTERN` line are all untouched, so the deliverable
# delta stays a single localized hunk (the re-review's "same shape as the current
# branch").  `_AUTHJOIN_CLASS` is reused, so the char class cannot drift from the value
# delimiters.
AUTHSCHEME_R2 = AUTHSCHEME_NEW                    # the r2 definition + its comments
AUTHSCHEME_R3 = AUTHSCHEME3_NEW                   # the r3 definition + its comments
AUTHSCHEME_R2_BLOCK = AUTHSCHEME_R2
AUTHSCHEME_R3_BLOCK = AUTHSCHEME_R3

# M3-r3: the r3 value group with `_AUTH_BARE_VALUE` swapped for the strict single
# token, i.e. the naive narrowing applied to the r3 tree.
AUTHVALUE_R3_LINE = (
    r'    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    r'+ _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"'
)
AUTHVALUE_R3_MUT_LINE = (
    r'    + _LEFT_ANCHOR + r"bearer\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    r'+ _AUTH_SCHEME_SPLIT + r"|" + _BARE_VALUE + r")"'
)

OPS = {
    # op -> list of (old_block, new_block) line-sequence replacements
    "narrow": [(COMMENT_OLD, COMMENT_NEW), (SCANNER_OLD, SCANNER_NEW)],
    "reverse": [(COMMENT_NEW, COMMENT_OLD), (SCANNER_NEW, SCANNER_OLD)],
    "mut_greedy": [(SCANNER_NEW, SCANNER_OLD)],
    "mut_authnl": [(block(AUTHJOIN_NARROW_LINE), block(AUTHJOIN_MUT_LINE))],
    "mut_auth1": [(block(AUTHVALUE_NARROW_LINE), block(AUTHVALUE_MUT_LINE))],
    # `authsplit` = the r2 fix; `reverse_authsplit` = its exact inverse (byte-identical
    # to the pre-r2 tree, `observability.py` sha256 e8abd522...); `mut_authsplit` is the
    # same end state reached by separate ops, so the M4 specimen and the "as if the fix
    # had never been written" tree are provably the same tree.
    "authsplit": [
        (AUTHPATTERN_HEAD, AUTHSCHEME_INSERT),
        (AUTHVALUE_NARROW_OLD, AUTHVALUE_NARROW_NEW),
    ],
    "reverse_authsplit": [
        (AUTHSCHEME_INSERT, AUTHPATTERN_HEAD),
        (AUTHVALUE_NARROW_NEW, AUTHVALUE_NOSCHEME),
    ],
    # r2 version of M3, for trees that already carry the scheme branch: `_AUTH_SCHEME_SPLIT`
    # stays defined but is no longer referenced, which is the naive-narrowing specimen.
    "mut_auth1_r2": [(AUTHVALUE_NARROW_NEW, block(AUTHVALUE_SPLIT_MUT_LINE))],
    "mut_authsplit": [
        (AUTHSCHEME_INSERT, AUTHPATTERN_HEAD),
        (AUTHVALUE_NARROW_NEW, AUTHVALUE_NOSCHEME),
    ],
    # ---- r3 / review F-REV-R2-01: generalize the pre-break token -----------------
    # `genericscheme` is the r3 fix (r2 tree -> r3 tree); `reverse_genericscheme` is its
    # exact inverse (r3 tree -> the r2 tree byte-for-byte).  Both act on one block, so
    # the fix and its inverse are the same text read in opposite directions - the same
    # construction r2 used, and what makes the mutation arm provable.
    "genericscheme": [(AUTHSCHEME_R2_BLOCK, AUTHSCHEME_R3_BLOCK)],
    "reverse_genericscheme": [(AUTHSCHEME_R3_BLOCK, AUTHSCHEME_R2_BLOCK)],
    # M3-r3: naive single-token narrowing, derived from the r3 tree.
    "mut_auth1_r3": [(block(AUTHVALUE_R3_LINE), block(AUTHVALUE_R3_MUT_LINE))],
    # M4-r3: the WHOLE scheme branch removed again (definition + comments, and the
    # value group back to the pre-r2 form).  This collapses onto the pre-r2 narrow
    # tree: it is "the r3 tree as if no scheme branch had ever been written", which is
    # the leak direction F-REV-D-01 and F-REV-R2-01 both live in.
    "mut_authsplit_r3": [
        (AUTHSCHEME_R3_BLOCK, []),
        (AUTHVALUE_R3_LINE, AUTHVALUE_NOSCHEME),
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
