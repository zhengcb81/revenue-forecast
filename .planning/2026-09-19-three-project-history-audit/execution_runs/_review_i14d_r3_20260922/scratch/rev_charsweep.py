"""Character sweep of the r3 after-break QUOTED alternative.

The landed group is:
    _AUTH_SCHEME_TOKEN [ \t]* (?:(?:\r?\n)[ \t]*)+ (?: _AUTH_BARE_VALUE+ | \"[^\"\r?\n]*\" | '[^'\r?\n]*' )

Inside a character class `[^\"\r?\n]`, the `?` is a LITERAL member of the negated set, not
the optional-`\r` metacharacter the author evidently meant (`_QUOTED_VALUE` two lines up is
`\"[^\"\r\n]*\"`).  If that is the cause, exactly the inputs whose quoted continuation
contains `?` must leak, and nothing else.

This sweeps every printable ASCII character (and a couple of controls) through
    Authorization: Bot\n"<39-char credential><C>x"
and reports which ones leave the credential in the clear.

Run:  python rev_charsweep.py --src <tree>/src --label <l> --out <json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

S = "ghp_ZQ7ReviewerFakeCredential0123456789"
CHARS = [chr(c) for c in range(0x20, 0x7F)] + ["\t", "\r", "\n", "\x0b", "\x0c"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    sys.path.insert(0, str(Path(a.src).resolve()))
    from company_wiki.source_catalog.observability import redact_text

    leaks_dq, leaks_sq = {}, {}
    for c in CHARS:
        for q, store in (('"', leaks_dq), ("'", leaks_sq)):
            text = "Authorization: Bot\n" + q + S + c + "x" + q
            out = redact_text(text)
            if S in out:
                store[repr(c)] = out
    report = {
        "label": a.label, "src": a.src,
        "double_quote_leaking_chars": sorted(leaks_dq),
        "double_quote_leaking_count": len(leaks_dq),
        "single_quote_leaking_chars": sorted(leaks_sq),
        "single_quote_leaking_count": len(leaks_sq),
        "examples": {k: v for k, v in list(leaks_dq.items())[:4]},
    }
    Path(a.out).write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(a.label, "| dq leaking chars:", sorted(leaks_dq))
    print(a.label, "| sq leaking chars:", sorted(leaks_sq))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
