"""I-14-D r2 scratch: build a prototype tree from iso/product_narrow + Ruling 2.

NOT part of the deliverable.  It exists so the Ruling-2 regex can be measured on a
byte-copy before the real tree is touched, and so the exact replacement strings used
by harness/apply_i14d_narrow.py's new ops can be diffed against the tree first.

    python build_authsplit_proto.py --src <tree>/src --out <scratch>/proto-src
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

REL = Path("company_wiki") / "source_catalog" / "observability.py"

# --- the exact new source lines (LF; the writer re-applies the tree's CRLF) -----

AUTH_BARE_OLD = (
    '_AUTH_BARE_VALUE = r"[^\\s,;&\\"\'|]+(?:[ \\t]+[^\\s,;&\\"\'|]+)*"'
)

AUTH_SCHEME_NEW = [
    '# A *known* scheme word followed by ONE line break is still a credential: the',
    '# secret of a header that wrapped (or a folded header) sits on the next line',
    '# with no `key=` prefix, so neither this pattern nor the assignment scanner can',
    '# see it.  Fail CLOSED: once a known scheme word is followed by a line break,',
    '# the first token after the break is redacted (line breaks and indentation stay',
    '# outside the match, so the diagnostic keys on the following lines survive).',
    '# Delimiters are the same as _AUTH_BARE_VALUE.  Measured by the r1 reviewer as',
    '# F-REV-D-01: without this branch a wrapped credential persisted in plaintext.',
    r'_AUTH_SCHEME_SPLIT = r"(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"',
    r'    r"[ \t]*\r?\n[ \t]*[^\s,;&\"'|]+"',
]

AUTH_VALUE_OLD = (
    '    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    '+ _AUTH_BARE_VALUE + r")"'
)
AUTH_VALUE_NEW = (
    '    + _LEFT_ANCHOR + r"bearer\\s+)(?P<value>" + _QUOTED_VALUE + r"|" '
    '+ _AUTH_SCHEME_SPLIT + r"|" + _AUTH_BARE_VALUE + r")"'
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    src = Path(args.src).resolve()
    out = Path(args.out)
    rel = REL if (src / REL).is_file() else Path("src") / REL
    path = src / rel
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"

    if AUTH_BARE_OLD not in text:
        raise SystemExit("PROTO-REFUSED: _AUTH_BARE_VALUE line not found")
    if AUTH_VALUE_OLD not in text:
        raise SystemExit("PROTO-REFUSED: auth value-group line not found")
    if "_AUTH_SCHEME_SPLIT" in text:
        raise SystemExit("PROTO-REFUSED: tree already carries _AUTH_SCHEME_SPLIT")

    insert = eol.join(AUTH_SCHEME_NEW) + eol
    text = text.replace(AUTH_BARE_OLD + eol, AUTH_BARE_OLD + eol + insert, 1)
    text = text.replace(AUTH_VALUE_OLD, AUTH_VALUE_NEW, 1)

    encoded = text.encode("utf-8")
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(encoded)
    print(f"proto: {dest}")
    print(f"sha256: {hashlib.sha256(encoded).hexdigest()}")
    print(f"bytes: {len(encoded)} (was {len(raw)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
