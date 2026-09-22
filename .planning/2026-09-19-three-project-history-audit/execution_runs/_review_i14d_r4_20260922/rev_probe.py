"""Class-level probes for the r4 fixes.

Runs each tree in its OWN subprocess so no module state can leak between trees.

Probe families:
  Q  - the `?` family: quoted continuation carrying `?` in many positions/shapes
  CH - character sweep: every printable ASCII + a few controls inside the quotes
  NL - the non-letter-scheme family, swept over every tchar first character
  CTL- the pre-existing controls that must not move

Usage: python rev_probe.py --src <tree>/src --label <l> --out <json> --tree <tag>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"

# tchar per RFC 7230: "!" / "#" / "$" / "%" / "&" / "'" / "*" / "+" / "-" / "." /
#                    "^" / "_" / "`" / "|" / "~" / DIGIT / ALPHA
TCHAR = "!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
NON_LETTER_TCHAR = "!#$%&'*+-.^_`|~0123456789"


def build_probes():
    q = []
    # both quote styles, both credentials, ? in several positions / multiplicities
    for qs, qe, name in (('"', '"', "dq"), ("'", "'", "sq")):
        for cred, cname in ((S39, "sec"), (M, "mark")):
            q.append((f"Q-{name}-{cname}-plain", f"Authorization: Bot\n{qs}{cred}{qe}"))
            q.append((f"Q-{name}-{cname}-q-tail", f"Authorization: Bot\n{qs}{cred}?x{qe}"))
            q.append((f"Q-{name}-{cname}-q-head", f"Authorization: Bot\n{qs}?{cred}{qe}"))
            q.append((f"Q-{name}-{cname}-q-mid", f"Authorization: Bot\n{qs}{cred[:20]}?{cred[20:]}{qe}"))
            q.append((f"Q-{name}-{cname}-qq", f"Authorization: Bot\n{qs}{cred}??{qe}"))
            q.append((f"Q-{name}-{cname}-q-only", f"Authorization: Bot\n{qs}?{qe}"))
            q.append((f"Q-{name}-{cname}-q-url", f"Authorization: Bot\n{qs}https://x/y?a=b {cred}{qe}"))
    # the scheme itself carrying ? is NOT a tchar -> not a scheme token (registered shape)
    q.append(("Q-scheme-with-q", f"Authorization: Bo?t\n{S39}"))
    return q


def char_sweep():
    chars = [chr(c) for c in range(0x20, 0x7F)]
    chars += ["\t", "\n", "\r", "\x0b", "\x0c"]
    out = []
    for ch in chars:
        for qs, qe in (('"', '"'), ("'", "'")):
            out.append((f"CH-{ord(ch):02x}-{qs}", f"Authorization: Bot\n{qs}{S39}{ch}x{qe}"))
    return out


def nonletter_sweep():
    out = []
    for ch in NON_LETTER_TCHAR:
        out.append((f"NL-digit-or-sym-{ord(ch):02x}", f"Authorization: {ch}foo\n{S39}\ndoc=17"))
    out.append(("NL-letter", f"Authorization: afoo\n{S39}\ndoc=17"))
    out.append(("NL-lead-digit-only", f"Authorization: 9\n{S39}\ndoc=17"))
    out.append(("NL-lead-bang-only", f"Authorization: !\n{S39}\ndoc=17"))
    out.append(("NL-lead-underscore", f"Authorization: _foo\n{S39}\ndoc=17"))
    return out


def controls():
    """Pre-existing rows / shapes that must not change."""
    return [
        ("CTL-N5k", f'Authorization: Bot\n"{S39}"'),
        ("CTL-N5c", f"Authorization: Bearer\n{M}\ndoc=17"),
        ("CTL-N5", f"Authorization: Bearer {M}\ndoc=17\nstage=summarize"),
        ("CTL-N5j", f"Authorization: Hawk\n\n{S39}"),
        ("CTL-over1", "Authorization: Bearer\ndoc=17"),
        ("CTL-over2", "Authorization: Bearer\nrequest_id=req-1"),
        ("CTL-C10", f"Authorization: Bearer abc\n{S39}"),
        ("CTL-C11", f"Authorization: Bearer\n\n{S39}"),
        ("CTL-C12", f'Authorization: Bearer\n"{S39}"'),
        ("CTL-N13", "password: iron steel"),
        ("CTL-url", "url=https://example/x?page=2"),
        ("CTL-untouched", "monkey=banana doc=1\nstage=x"),
        ("CTL-cred-basic", f"Authorization: Bearer {M}"),
    ]


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
    for fam, probes in (("Q", build_probes()), ("CH", char_sweep()),
                        ("NL", nonletter_sweep()), ("CTL", controls())):
        for pid, text in probes:
            out = redact_text(text)
            rows.append({
                "family": fam, "id": pid, "in": text, "out": out,
                "leaks_secret": S39 in out,
                "leaks_marker": M in out,
            })

    q_leaks = [r["id"] for r in rows if r["family"] == "Q" and (r["leaks_secret"] or r["leaks_marker"])]
    ch_leaks = [r["id"] for r in rows if r["family"] == "CH" and (r["leaks_secret"] or r["leaks_marker"])]
    nl_leaks = [r["id"] for r in rows if r["family"] == "NL" and (r["leaks_secret"] or r["leaks_marker"])]
    rep = {
        "tree": a.tree, "label": a.label, "src": a.src, "rows": rows,
        "Q_leaks": q_leaks, "CH_leaks": ch_leaks, "NL_leaks": nl_leaks,
        "counts": {"Q": len(build_probes()), "CH": len(char_sweep()),
                   "NL": len(nonletter_sweep()), "CTL": len(controls())},
    }
    Path(a.out).write_text(json.dumps(rep, indent=1, ensure_ascii=True), encoding="utf-8")
    print(f"--- {a.tree} ---")
    print(f"Q  leaks ({len(q_leaks)}): {q_leaks}")
    print(f"CH leaks ({len(ch_leaks)}): {ch_leaks}")
    print(f"NL leaks ({len(nl_leaks)}): {nl_leaks}")
    for r in rows:
        if r["family"] == "CTL":
            print(f"  {r['id']:22s} {r['out']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
