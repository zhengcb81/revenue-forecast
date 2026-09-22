"""Sweep the PRE-BREAK token in `Authorization: <T>\\n<cred>` and compare trees.

This isolates a family the `?`-in-quotes probe surfaced as a side effect:
a pre-break word that is NOT a valid RFC-7230 tchar token.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

TCHAR = set("!#$%&'*+-.^_`|~0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def probes():
    out = []
    # one non-tchar char inserted into an otherwise-valid scheme word
    for code in range(0x20, 0x7F):
        ch = chr(code)
        if ch in TCHAR:
            continue
        out.append((f"pre-B{code:02x}", f"Authorization: Bo{ch}t\n{S39}"))
    # a single-token pre-break word that is wholly non-tchar
    for ch in "?/:@()[]{}=<>+*,;&\"'|\\~":
        out.append((f"pre-only-{ord(ch):02x}", f"Authorization: {ch}\n{S39}"))
    # controls: valid tchar schemes of the same length
    out.append(("pre-ctrl-Bot", f"Authorization: Bot\n{S39}"))
    out.append(("pre-ctrl-Boat", f"Authorization: Boat\n{S39}"))
    out.append(("pre-ctrl-two-token", f"Authorization: Bearer abc\n{S39}"))
    # marker variants of the same shape
    out.append(("pre-mark-question", f"Authorization: Bo?t\n{M}"))
    out.append(("pre-mark-slash", f"Authorization: Bo/t\n{M}"))
    out.append(("pre-mark-plain", f"Authorization: Bot\n{M}"))
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tree", required=True)
    a = p.parse_args()

    sys.path.insert(0, str(Path(a.src).resolve()))
    from company_wiki.source_catalog.observability import redact_text  # noqa

    rows = []
    for pid, text in probes():
        out = redact_text(text)
        rows.append({"id": pid, "in": text, "out": out,
                     "leaks": (S39 in out) or (M in out)})
    leaks = [r["id"] for r in rows if r["leaks"]]
    rep = {"tree": a.tree, "rows": rows, "leaks": leaks}
    Path(a.out).write_text(json.dumps(rep, indent=1, ensure_ascii=True), encoding="utf-8")
    print(f"--- {a.tree}: {len(leaks)} leak(s) of {len(rows)} ---")
    for r in rows:
        if r["leaks"]:
            print(f"  LEAK {r['id']:16s} in={r['in']!r}")
            print(f"       out={r['out']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
