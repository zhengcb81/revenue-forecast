"""I-14-D-R2 gate-0 / defect self-probe: exercise the authorization path family.

    python probe_dfamily.py --src <tree>/src --label <label> [--out <json>]

D1..D9 are transcribed from execution_runs/I-14-D/a20260919-01/reviewer_report.md
L233-L243 (the F-REV-D-01 measurement table).  SECRET is the reviewer's synthetic
credential `ghp_ZQ7ReviewerFakeCredential0123456789` (39 chars, no whitespace).

`secret_absent` is the pass condition for every row: the credential must never be
written to the persisted `message_redacted` field.  `diagnostics_kept` records
whether `doc=17` survived (the C13 half of the card's exit clause).

Exit codes: 0 = no leak in any row, 3 = at least one row leaks (defect present).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"

# (id, input) - verbatim from reviewer_report.md L233-L243
ROWS = [
    ("D1", "Authorization: Bearer\n" + SECRET + "\ndoc=17"),
    ("D2", "Authorization: Bearer \n" + SECRET),
    ("D3", "Authorization:Bearer\n" + SECRET),
    ("D4", "authorization: token\n" + SECRET),
    ("D5", "Authorization: Bearer\r\n" + SECRET),
    ("D6", "Authorization: Bearer\n  " + SECRET),
    ("D7", "stage=summarize Authorization: Bearer\n" + SECRET + "\nrequest_id=req-1"),
    ("D8", "Authorization: Bearer\t" + SECRET),
    ("D9", "Authorization: Bearer " + SECRET),
    # R2 new case required by the dispatch (green criterion): the full persisted
    # event shape that F-REV-D-01 measured end-to-end through worker.py:1066.
    ("R2-core", "Authorization: Bearer\n" + SECRET + "\ndoc=17"),
    ("R2-core-marker", "Authorization: Bearer\nSYNTHETIC_AUDIT_TOKEN\ndoc=17"),
]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", default=None)
    args = p.parse_args(argv)

    sys.path.insert(0, str(Path(args.src).resolve()))
    try:
        from company_wiki.source_catalog.observability import (
            redact_and_truncate,
            redact_text,
        )
    except ImportError as exc:
        report = {"label": args.label, "src": args.src, "helper_present": False,
                  "verdict": "cannot_adjudicate",
                  "import_error": f"{type(exc).__name__}: {exc}"}
        if args.out:
            Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                      encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2

    rows = []
    for rid, text in ROWS:
        out = redact_text(text)
        persisted = redact_and_truncate(text)
        secret_in_out = SECRET in out
        marker_in_out = "SYNTHETIC_AUDIT_TOKEN" in out
        rows.append({
            "id": rid,
            "in": text,
            "redact_text": out,
            "persisted": persisted,
            "secret_absent": (not secret_in_out) and (not marker_in_out),
            "doc17_kept": "doc=17" in out,
            "leak": secret_in_out or marker_in_out,
        })

    leaks = [r["id"] for r in rows if r["leak"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "rows": rows,
        "leak_rows": leaks,
        "leak_count": len(leaks),
        "verdict": "DEFECT_PRESENT" if leaks else "NO_LEAK",
    }
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
    for r in rows:
        print(f"{r['id']:>14} leak={str(r['leak']):5} -> {r['redact_text']!r}")
    print(f"LEAK_ROWS={leaks} verdict={report['verdict']}")
    return 3 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
