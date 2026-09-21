"""I-14-D r2: helper-level leak/closure probe for the auth newline-split family.

This is EVIDENCE COLLECTION, not an oracle: it prints raw input/output pairs and a
per-row SECRET_LEAKS fact for the family the reviewer measured as F-REV-D-01.  It
asserts nothing on the redactor's behalf; the frozen expectations live in
`run_i14d_oracle.py` (N5c/N5d) and `run_rule_table_i14d.py` (cred-auth-split-*).

    python authsplit_probe.py --src <iso>/<tree>/src --label <label> --out <json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# the reviewer's own synthetic secret: 39 chars, no whitespace
SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

# (id, input, expected, reviewer_prediction) — the reviewer's D1..D9 family verbatim,
# plus the marker form.  `expected` is the frozen post-fix output this attempt asserts
# (also carried as oracle N5c/N5d and rule-table cred-auth-split-* rows);
# `reviewer_prediction` is what the reviewer's report table (F-REV-D-01) listed for the
# pre-fix tree, kept so a divergence between the two can never be silently dropped.
SECRET_TAIL_LF = "\n" + SECRET
CASES = [
    ("D1-bearer-lf", "Authorization: Bearer\n" + SECRET + "\ndoc=17",
     "Authorization: <redacted>\ndoc=17", "Authorization: <redacted>\n<SECRET>\ndoc=17"),
    ("D2-bearer-space-lf", "Authorization: Bearer \n" + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted> \n<SECRET>"),
    ("D3-bearer-nospace-lf", "Authorization:Bearer\n" + SECRET,
     "Authorization:<redacted>", "Authorization:<redacted>\n<SECRET>"),
    ("D4-token-scheme-lf", "authorization: token\n" + SECRET,
     "authorization: <redacted>", "authorization: <redacted>\n<SECRET>"),
    ("D5-bearer-crlf", "Authorization: Bearer\r\n" + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted>\r\n<SECRET>"),
    ("D6-bearer-obsfold", "Authorization: Bearer\n  " + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted>\n  <SECRET>"),
    ("D7-embedded", "stage=summarize Authorization: Bearer\n" + SECRET
     + "\nrequest_id=req-1",
     "stage=summarize Authorization: <redacted>\nrequest_id=req-1",
     "stage=summarize Authorization: <redacted>\n<SECRET>\nrequest_id=req-1"),
    ("D8-bearer-tab-sameline", "Authorization: Bearer\t" + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted>"),
    ("D9-bearer-space-sameline", "Authorization: Bearer " + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted>"),
    ("D10-basic-lf", "Authorization: Basic\n" + SECRET,
     "Authorization: <redacted>", "Authorization: <redacted>\n<SECRET>"),
    ("M1-marker-bearer-lf", "Authorization: Bearer\n" + M,
     "Authorization: <redacted>", "Authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN"),
    ("M2-marker-token-lf", "authorization: token\n" + M,
     "authorization: <redacted>", "authorization: <redacted>\nSYNTHETIC_AUDIT_TOKEN"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(args.src).resolve()))
    try:
        from company_wiki.source_catalog.observability import (
            redact_and_truncate, redact_text)
    except ImportError as exc:
        report = {"label": args.label, "src": args.src, "helper_present": False,
                  "verdict": "cannot_adjudicate",
                  "import_error": f"{type(exc).__name__}: {exc}"}
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2

    rows = []
    for case_id, text, expected, reviewer_prediction in CASES:
        secret = M if case_id.startswith("M") else SECRET
        out = redact_text(text)
        persisted = redact_and_truncate(text)
        rows.append({
            "id": case_id,
            "in": text,
            "out": out,
            "expected": expected,
            "reviewer_prediction": reviewer_prediction,
            "matches_expected": out == expected,
            "persisted": persisted,
            "out_len": len(out),
            "secret_len": len(secret),
            "secret_survives": secret in out,
            "secret_survives_persisted": secret in persisted,
            "diagnostics_kept": "doc=17" in out,
        })

    leaks = [r["id"] for r in rows if r["secret_survives"]]
    drift = [r["id"] for r in rows if not r["matches_expected"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "cases": len(rows),
        "credential_leaks": leaks,
        "leak_count": len(leaks),
        "fidelity_drift": drift,
        "rows": rows,
        "verdict": ("LEAK" if leaks else "FIDELITY-DRIFT" if drift else "closed"),
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "cases", "credential_leaks", "leak_count",
                       "fidelity_drift", "verdict")},
                     ensure_ascii=True, indent=2))
    for row in rows:
        print(("LEAK " if row["secret_survives"] else
               "DRIFT" if not row["matches_expected"] else "ok   ") + row["id"],
              "->", repr(row["out"]))
    return 0 if not leaks and not drift else 3


if __name__ == "__main__":
    sys.exit(main())
