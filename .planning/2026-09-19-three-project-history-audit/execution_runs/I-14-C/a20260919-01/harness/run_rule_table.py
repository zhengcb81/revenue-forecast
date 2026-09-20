"""I-14-C r2: run ONLY the frozen rule table against each iso tree.

This isolates F-I14C-02 (env-var style keys).  Run against `iso/product_r1` it must
reproduce the leak the reviewer reported; against `iso/product_fixed` it must be green;
against `iso/product` (pristine) the helper does not exist at all, which is reported as
"helper absent" rather than as a leak.

    python run_rule_table.py --src <iso>/<tree>/src --label <label>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER = "SYNTHETIC_AUDIT_TOKEN"

POSITIVES = [
    "Authorization: Bearer " + MARKER,
    "Authorization Bearer " + MARKER,
    "authorization: token " + MARKER,
    "Authorization: " + MARKER,
    'Authorization: "Bearer ' + MARKER + '"',
    "GET /x?token=" + MARKER + "&page=2",
    "token=" + MARKER,
    "api_key=" + MARKER,
    "password: '" + MARKER + "'",
    # F-I14C-02 shapes
    "GITHUB_TOKEN=" + MARKER,
    "my_access_token=" + MARKER,
    "SLACK_BOT_TOKEN=" + MARKER,
    "AWS_SECRET_ACCESS_KEY=" + MARKER,
    "export GITHUB_TOKEN=" + MARKER,
    "GH_TOKEN=" + MARKER,
    "AWS_ACCESS_KEY_ID=" + MARKER,
    "AWS_SECRET_ACCESS_KEY_ID=" + MARKER,
    "client_secret=" + MARKER,
    "MY_APP_PASSWORD=" + MARKER,
    "db.passwd=" + MARKER,
]

# must NOT be redacted (over-redaction guard) and the declared residual
NOT_REDACTED = [
    "monkey=banana",
    "oauth=abc123",
    "secretary=alice",
    "tokenizer=whitespace",
    "keyboard=us",
    "document not in catalog: doc-1",
    "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
    "upload failed for digest=" + MARKER,      # declared residual (unknown key)
    "--api-key " + MARKER,                     # declared residual (flag form)
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(args.src).resolve()))
    try:
        from company_wiki.source_catalog.observability import redact_text
    except ImportError as exc:
        report = {"label": args.label, "src": args.src, "helper_present": False,
                  "import_error": f"{type(exc).__name__}: {exc}"}
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0

    rows = []
    leaks = []
    for text in POSITIVES:
        out = redact_text(text)
        leaked = MARKER in out
        rows.append({"kind": "positive", "in": text, "out": out, "leaked": leaked})
        if leaked:
            leaks.append(text)
    for text in NOT_REDACTED:
        out = redact_text(text)
        changed = out != text
        rows.append({"kind": "must-not-redact", "in": text, "out": out,
                     "changed": changed})
    over = [r["in"] for r in rows if r["kind"] == "must-not-redact" and r["changed"]]

    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "positives": len(POSITIVES),
        "leaks": leaks,
        "leak_count": len(leaks),
        "over_redaction": over,
        "over_redaction_count": len(over),
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "helper_present", "positives", "leak_count",
                       "leaks", "over_redaction_count", "over_redaction")},
                     ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
