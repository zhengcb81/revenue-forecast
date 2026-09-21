"""Reviewer's own differential probe for the r3 auth-newline-split branch.

Written from the r2 reviewer's printed matrix (reviewer_report_r2.md section 2.3) --
NOT derived from the attempt's harness or from authsplit_probe.py.  Imports only
redact_text from a tree's src, one tree per process invocation.

Extra rows (X*) are shapes the attempt's own matrices do not contain; they exist to test
the regex bytes rather than the record's description of them.

Run:
  python rev_probe.py --src <tree>/src --label <label> --out <json>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

S = "ghp_ZQ7ReviewerFakeCredential0123456789"   # 39 chars, the r2 reviewer's credential
M = "SYNTHETIC_AUDIT_TOKEN"                     # 21 chars, the attempt's marker
R = "<redacted>"

# (id, kind, input)  -- C* are the r2 reviewer's matrix verbatim
CASES = [
    ("C1", "c-matrix", "Authorization: Negotiate\n" + S + "\ndoc=17"),
    ("C2", "c-matrix", "Authorization: AWS4-HMAC-SHA256\n" + S + "\ndoc=17"),
    ("C3", "c-matrix", "Authorization: SCRAM-SHA-256\n" + S + "\ndoc=17"),
    ("C4", "c-matrix", "Authorization: Hawk\n" + S + "\ndoc=17"),
    ("C5", "c-matrix", "Authorization: Bot\n" + S + "\ndoc=17"),
    ("C6", "c-matrix", "Authorization: Mutual\n" + S + "\ndoc=17"),
    ("C7", "c-matrix", "Authorization: vapid\n" + S + "\ndoc=17"),
    ("C8", "c-matrix", "Authorization: HOBA\n" + S + "\ndoc=17"),
    ("C9", "c-matrix", "Authorization: Zzz\n" + S + "\ndoc=17"),
    ("C10", "c-matrix", "Authorization: Bearer abc\n" + S),
    ("C11", "c-matrix", "Authorization: Bearer\n\n" + S),
    ("C12", "c-matrix", 'Authorization: Bearer\n"' + S + '"'),
    # marker form of the same family (the card's own negative clause)
    ("C1m", "c-matrix", "Authorization: Negotiate\n" + M + "\ndoc=17"),
    ("C9m", "c-matrix", "Authorization: Zzz\n" + M + "\ndoc=17"),
    # ---- X rows: byte-level probes of the landed regex ----
    # X1: quoted continuation whose value contains '?'.  In `[^\"\r?\n]` the '?' is a
    # LITERAL member of the negated class (not the optional-\r metacharacter), so a
    # quoted secret containing '?' after a break is not matched by that alternative.
    ("X1-quoted-with-question", "x-probe", 'Authorization: Bot\n"' + S + "?x\""),
    # X2: control for X1 -- same shape, no '?' in the value.
    ("X2-quoted-no-question", "x-probe", 'Authorization: Bot\n"' + S + '"'),
    # X3: the '_QUOTED_VALUE' path on the same line (no break) with '?' -- unchanged
    # by r3, included so X1's difference is attributable to the after-break class only.
    ("X3-sameline-quoted-question", "x-probe", 'Authorization: Bot "' + S + "?x\""),
    # X4: scheme token of length 1 (the class requires a leading letter)
    ("X4-one-letter-scheme", "x-probe", "Authorization: A\n" + S),
    # X5: scheme token containing '|' (kept inside the class by the r3 comment)
    ("X5-pipe-in-scheme", "x-probe", "Authorization: a|b\n" + S),
    # X6: three line breaks (run of breaks, not exactly two)
    ("X6-three-breaks", "x-probe", "Authorization: Bot\n\n\n" + S),
    # X7: CRLF break
    ("X7-crlf", "x-probe", "Authorization: Bot\r\n" + S),
    # X8: break run then indentation then quoted secret
    ("X8-indent-quoted", "x-probe", 'Authorization: Bot\n   "' + S + '"'),
    # X9: a scheme-looking word with no credential after the break (over-redaction)
    ("X9-scheme-then-key", "x-probe", "Authorization: Bearer\ndoc=17"),
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    sys.path.insert(0, str(Path(a.src).resolve()))
    from company_wiki.source_catalog.observability import redact_text

    rows = []
    for cid, kind, text in CASES:
        out = redact_text(text)
        rows.append({
            "id": cid, "kind": kind, "in": text, "out": out,
            "secret_survives": S in out,
            "marker_survives": M in out,
            "any_credential_survives": (S in out) or (M in out),
        })
    leaks = [r["id"] for r in rows if r["any_credential_survives"]]
    matrix_leaks = [r["id"] for r in rows if r["kind"] == "c-matrix"
                    and r["any_credential_survives"]]
    x_leaks = [r["id"] for r in rows if r["kind"] == "x-probe"
               and r["any_credential_survives"]]
    report = {"label": a.label, "src": a.src, "rows": rows,
              "c_matrix_leaking": matrix_leaks, "x_probe_leaking": x_leaks,
              "all_leaking": leaks}
    Path(a.out).write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(a.label, "| c-matrix leaking:", matrix_leaks, "| x-probe leaking:", x_leaks)
    for r in rows:
        if r["any_credential_survives"]:
            print("   LEAK", r["id"], repr(r["out"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
