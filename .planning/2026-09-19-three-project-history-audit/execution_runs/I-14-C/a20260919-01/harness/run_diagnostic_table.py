"""I-14-C r3/r4: over-redaction table WITH OUTPUT FIDELITY, one tree at a time.

The r2 report claimed "0 over-redaction", but that only covered the five guard strings in
the rule table.  This probe measures a wider diagnostic corpus so the real scope of
over-redaction is visible, and it is run against the r1 tree as well so each entry can be
labelled pre-existing (r1) or newly introduced (r2/r3).

r4 (F-I14C-08): every entry now carries a hand-written exact expected output, so a redactor
that mangles the key (`tokentoken=<redacted>`) can no longer pass.  The process exits 2 on
any fidelity failure.

    python run_diagnostic_table.py --src <iso>/<tree>/src --label <tree> --out <json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER = "SYNTHETIC_AUDIT_TOKEN"

# (id, text, kind)
#   credential  -> MUST be redacted
#   diagnostic  -> ordinary diagnostic text; redacting it is over-redaction
#   residual    -> known-not-covered: the marker is expected to survive
# Every entry carries a hand-written exact expected output (never produced by calling the
# product); `<R>` means `<redacted>`.
R = "<redacted>"
CORPUS = [
    ("cred-env-github", "GITHUB_TOKEN=" + MARKER, "GITHUB_TOKEN=" + R, "credential"),
    ("cred-env-slack", "SLACK_BOT_TOKEN=" + MARKER, "SLACK_BOT_TOKEN=" + R, "credential"),
    ("cred-env-aws-secret", "AWS_SECRET_ACCESS_KEY=" + MARKER,
     "AWS_SECRET_ACCESS_KEY=" + R, "credential"),
    ("cred-env-aws-keyid", "AWS_ACCESS_KEY_ID=" + MARKER,
     "AWS_ACCESS_KEY_ID=" + R, "credential"),
    ("cred-query-token", "GET /x?token=" + MARKER + "&page=2",
     "GET /x?token=" + R + "&page=2", "credential"),
    ("cred-header-bearer", "Authorization: Bearer " + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-header-bare", "Authorization: " + MARKER, "Authorization: " + R, "credential"),
    ("cred-quoted", "password: '" + MARKER + "'", "password: " + R, "credential"),
    ("cred-api-key", "api_key=" + MARKER, "api_key=" + R, "credential"),
    ("cred-client-secret", "client_secret=" + MARKER, "client_secret=" + R, "credential"),
    # C13 multi-line (r5): the value crosses the newline and deletes the rest of the block
    ("cred-multiline-swallow", "upload failed for token=" + MARKER
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1",
     "upload failed for token=" + R, "credential"),
    ("diag-stage", "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", "diagnostic"),
    ("diag-multiline-no-credential",
     "stage=summarize\ncode=llm_global_failure\nrequest_id=req-1",
     "stage=summarize\ncode=llm_global_failure\nrequest_id=req-1", "diagnostic"),
    ("diag-doc", "document not in catalog: doc-1",
     "document not in catalog: doc-1", "diagnostic"),
    ("diag-count", "files_seen=0 completed_with_errors=1",
     "files_seen=0 completed_with_errors=1", "diagnostic"),
    ("diag-elapsed", "elapsed_seconds=12.5 retries=3",
     "elapsed_seconds=12.5 retries=3", "diagnostic"),
    ("diag-http", "GET /v1/status returned 503",
     "GET /v1/status returned 503", "diagnostic"),
    ("diag-key", "key=value", "key=value", "diagnostic"),
    # C11 registered over-redactions: expected output is the measured redacted form, so the
    # fidelity criterion still bites on everything else.  `ideal` is the input.
    ("diag-pwd-dir", "pwd=/home/user/project", "pwd=" + R, "known_over_redaction"),
    ("diag-token-expired", "token: expired", "token: " + R, "known_over_redaction"),
    ("diag-secret-rotated", "secret: rotated at 2026-09-19",
     "secret: " + R, "known_over_redaction"),
    ("diag-password-prompt", "password: ********", "password: " + R,
     "known_over_redaction"),
    ("diag-monkey", "monkey=banana", "monkey=banana", "diagnostic"),
    ("diag-oauth", "oauth=abc123", "oauth=abc123", "diagnostic"),
    ("diag-secretary", "secretary=alice", "secretary=alice", "diagnostic"),
    ("diag-tokenizer", "tokenizer=whitespace", "tokenizer=whitespace", "diagnostic"),
    ("diag-keyboard", "keyboard=us", "keyboard=us", "diagnostic"),
    ("res-digest", "upload failed for digest=" + MARKER,
     "upload failed for digest=" + MARKER, "residual"),
    ("res-flag", "--api-key " + MARKER, "--api-key " + MARKER, "residual"),
    ("res-json-quoted", '{"api_key": "' + MARKER + '"}',
     '{"api_key": "' + MARKER + '"}', "residual"),
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
        # F-I14C-R4-05: same fallback as run_rule_table.py - a missing helper is "cannot
        # adjudicate" (2), not a traceback.
        report = {"label": args.label, "src": args.src, "helper_present": False,
                  "verdict": "cannot_adjudicate",
                  "import_error": f"{type(exc).__name__}: {exc}"}
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2

    rows = []
    for case_id, text, expected, kind in CORPUS:
        out = redact_text(text)
        rows.append({"id": case_id, "kind": kind, "in": text, "expected": expected,
                     "out": out, "fidelity_ok": out == expected,
                     "changed": out != text, "marker_survives": MARKER in out})
    diagnostics = [r for r in rows if r["kind"] == "diagnostic"]
    known = [r for r in rows if r["kind"] == "known_over_redaction"]
    # "over-redaction" for the known entries is out != in; any STRICT diagnostic entry that
    # changed is a NEW over-redaction and must be empty.
    leaks = [r["id"] for r in rows
             if r["kind"] == "credential" and r["marker_survives"]]
    new_over = [r["id"] for r in diagnostics if r["changed"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "rows": rows,
        "credential_leaks": leaks,
        "over_redacted": [r["id"] for r in known if r["changed"]],
        "new_over_redaction": new_over,
        "diagnostic_corpus_size": len(diagnostics),
        "residuals_confirmed": [r["id"] for r in rows
                                if r["kind"] == "residual" and r["marker_survives"]],
        "fidelity_failures": [{"id": r["id"], "expected": r["expected"], "out": r["out"]}
                              for r in rows if not r["fidelity_ok"]],
        "fidelity_ok": all(r["fidelity_ok"] for r in rows),
    }
    negative = (not report["fidelity_ok"]) or bool(leaks) or bool(new_over)
    report["verdict"] = "negative" if negative else "pass"
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "credential_leaks", "over_redacted",
                       "new_over_redaction", "diagnostic_corpus_size",
                       "residuals_confirmed", "fidelity_ok", "verdict")},
                     ensure_ascii=True, indent=2))
    for failure in report["fidelity_failures"]:
        print("FIDELITY-FAIL", failure["id"], "expected", repr(failure["expected"]),
              "got", repr(failure["out"]))
    # REGISTERED over-redaction (the `known_over_redaction` class) is what this table
    # measures and does not by itself make the verdict negative; a NEW over-redaction does.
    # Exit-code convention (F-I14C-R4-06): 0 = pass, 2 = cannot adjudicate, 3 = negative.
    return 0 if not negative else 3


if __name__ == "__main__":
    sys.exit(main())
