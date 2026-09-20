"""I-14-C r4: rule table WITH OUTPUT FIDELITY.

r3 lesson (F-I14C-08): the r2/r3 tables only asked "did the marker disappear?" and "did the
text change?".  A redactor that emits `tokentoken=<redacted>` passes both.  This version
freezes an EXACT expected output for every entry, so the criteria are now:

  1. credential entries: the marker must be gone AND the output must equal `expected`
     character for character (the value replaced, everything else byte-identical);
  2. untouched entries: the output must equal the input exactly;
  3. residual entries: the marker is expected to survive and the output must equal `expected`
     (which for residuals is the input).

The process exits 2 if any entry fails, so a run cannot report "0 leaks" without also
passing fidelity.  `<R>` in the table means `<redacted>`.

Run against `iso/product_r1` it must reproduce the F-I14C-02 leak; against the pristine
`iso/product` tree the helper does not exist at all, which is reported as "helper absent"
rather than as a leak.

    python run_rule_table.py --src <iso>/<tree>/src --label <tree> --out <json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"

# (id, input, expected output, kind)
TABLE = [
    ("cred-header-bearer", "Authorization: Bearer " + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-header-space", "Authorization Bearer " + MARKER,
     "Authorization Bearer " + R, "credential"),
    ("cred-header-scheme", "authorization: token " + MARKER,
     "authorization: " + R, "credential"),
    ("cred-header-bare", "Authorization: " + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-header-quoted", 'Authorization: "Bearer ' + MARKER + '"',
     "Authorization: " + R, "credential"),
    ("cred-query", "GET /x?token=" + MARKER + "&page=2",
     "GET /x?token=" + R + "&page=2", "credential"),
    ("cred-token", "token=" + MARKER, "token=" + R, "credential"),
    ("cred-api-key", "api_key=" + MARKER, "api_key=" + R, "credential"),
    ("cred-apikey", "apikey=" + MARKER, "apikey=" + R, "credential"),
    ("cred-password-quoted", "password: '" + MARKER + "'",
     "password: " + R, "credential"),
    ("cred-private-key", "private_key=" + MARKER, "private_key=" + R, "credential"),
    ("cred-auth-token", "auth_token=" + MARKER, "auth_token=" + R, "credential"),
    # F-I14C-02 env-var family: the key must survive verbatim (F-I14C-08 regression guard)
    ("cred-env-github", "GITHUB_TOKEN=" + MARKER, "GITHUB_TOKEN=" + R, "credential"),
    ("cred-env-my", "my_access_token=" + MARKER, "my_access_token=" + R, "credential"),
    ("cred-env-slack", "SLACK_BOT_TOKEN=" + MARKER, "SLACK_BOT_TOKEN=" + R, "credential"),
    ("cred-env-aws-secret", "AWS_SECRET_ACCESS_KEY=" + MARKER,
     "AWS_SECRET_ACCESS_KEY=" + R, "credential"),
    ("cred-env-export", "export GITHUB_TOKEN=" + MARKER,
     "export GITHUB_TOKEN=" + R, "credential"),
    ("cred-env-gh", "GH_TOKEN=" + MARKER, "GH_TOKEN=" + R, "credential"),
    ("cred-env-aws-keyid", "AWS_ACCESS_KEY_ID=" + MARKER,
     "AWS_ACCESS_KEY_ID=" + R, "credential"),
    ("cred-env-aws-keyid2", "AWS_SECRET_ACCESS_KEY_ID=" + MARKER,
     "AWS_SECRET_ACCESS_KEY_ID=" + R, "credential"),
    ("cred-client-secret", "client_secret=" + MARKER, "client_secret=" + R, "credential"),
    ("cred-my-password", "MY_APP_PASSWORD=" + MARKER,
     "MY_APP_PASSWORD=" + R, "credential"),
    ("cred-dotted", "db.passwd=" + MARKER, "db.passwd=" + R, "credential"),
    ("cred-in-prose", "upload failed for token=" + MARKER,
     "upload failed for token=" + R, "credential"),
    ("cred-space-around", "token = " + MARKER, "token = " + R, "credential"),
    # The value is the whole space/tab separated run, NOT one token: that is the r1
    # `_BARE_VALUE` semantics (`X+(?:\s+X+)*`), kept deliberately because
    #   (a) the reviewer's E4b length baseline (193) is computed from it, and
    #   (b) a quoted value still has precedence.
    # C13 (corrected in r5, F-I14C-R4-02): because `\s` includes newlines, the value does
    # not stop at the end of the line - it deletes THE WHOLE REMAINING DIAGNOSTIC BLOCK,
    # e.g. `... token=<secret> doc=17\nstage=summarize code=... request_id=...` (112 chars)
    # collapses to `... token=<redacted>` (34 chars).  Not a truncation artefact and not
    # introduced by r3/r4 (r1 has the same `_BARE_VALUE`).  Narrowing it would move the E4b
    # baseline, so it is frozen here with the real consequence visible.
    ("cred-line-middle-greedy-value", "a=1 token=" + MARKER + " b=2",
     "a=1 token=" + R, "credential"),
    ("cred-line-middle-trailing-punct", "a=1 token=" + MARKER + "; b=2",
     "a=1 token=" + R + "; b=2", "credential"),
    # C13 multi-line cases: the direction the r4 criterion was blind to
    ("cred-multiline-swallow", "upload failed for token=" + MARKER
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1",
     "upload failed for token=" + R, "credential"),
    ("cred-multiline-stopped-by-semicolon", "failed for token=" + MARKER
     + "; see log\nstage=summarize code=llm_global_failure",
     "failed for token=" + R + "; see log\nstage=summarize code=llm_global_failure",
     "credential"),
    ("cred-multiline-then-key", "token=" + MARKER + "\nnext=1",
     "token=" + R, "credential"),
    # a rejected key must not eat the pair that follows it (declared r3 behaviour)
    ("cred-after-url", "url=https://example/x?token=" + MARKER,
     "url=https://example/x?token=" + R, "credential"),
    ("cred-after-flag", "cmd: --token=" + MARKER, "cmd: --token=" + R, "credential"),
    # must NOT be touched
    ("untouched-monkey", "monkey=banana", "monkey=banana", "untouched"),
    ("untouched-oauth", "oauth=abc123", "oauth=abc123", "untouched"),
    ("untouched-secretary", "secretary=alice", "secretary=alice", "untouched"),
    ("untouched-tokenizer", "tokenizer=whitespace", "tokenizer=whitespace", "untouched"),
    ("untouched-keyboard", "keyboard=us", "keyboard=us", "untouched"),
    ("untouched-key", "key=value", "key=value", "untouched"),
    ("untouched-url", "url=https://example/x?page=2",
     "url=https://example/x?page=2", "untouched"),
    ("untouched-doc", "document not in catalog: doc-1",
     "document not in catalog: doc-1", "untouched"),
    ("untouched-stage", "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", "untouched"),
    # declared residuals
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
        report = {"label": args.label, "src": args.src, "helper_present": False,
                  "verdict": "cannot_adjudicate",
                  "import_error": f"{type(exc).__name__}: {exc}"}
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        # 2 = harness/bookkeeping could not produce a verdict (run_card.py convention)
        return 2

    rows = []
    for case_id, text, expected, kind in TABLE:
        out = redact_text(text)
        rows.append({
            "id": case_id, "kind": kind, "in": text, "expected": expected, "out": out,
            "fidelity_ok": out == expected,
            "marker_survives": MARKER in out,
        })

    credentials = [r for r in rows if r["kind"] == "credential"]
    untouched = [r for r in rows if r["kind"] == "untouched"]
    residuals = [r for r in rows if r["kind"] == "residual"]
    leaks = [r["id"] for r in credentials if r["marker_survives"]]
    touched = [r["id"] for r in untouched if r["out"] != r["in"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "entries": len(rows),
        "credential_leaks": leaks,
        "touched_but_should_not_be": touched,
        "residuals_confirmed": [r["id"] for r in residuals if r["marker_survives"]],
        "fidelity_failures": [{"id": r["id"], "expected": r["expected"], "out": r["out"]}
                              for r in rows if not r["fidelity_ok"]],
        "fidelity_ok": all(r["fidelity_ok"] for r in rows),
        "rows": rows,
    }
    negative = (not report["fidelity_ok"]) or bool(leaks) or bool(touched)
    report["verdict"] = "negative" if negative else "pass"
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "entries", "credential_leaks",
                       "touched_but_should_not_be", "residuals_confirmed",
                       "fidelity_ok", "verdict")}, ensure_ascii=True, indent=2))
    for failure in report["fidelity_failures"]:
        print("FIDELITY-FAIL", failure["id"], "expected", repr(failure["expected"]),
              "got", repr(failure["out"]))
    # Exit-code convention (aligned with run_card.py after F-I14C-R4-06):
    #   0 = pass, 2 = cannot adjudicate, 3 = adjudication is NEGATIVE.
    # A rule being broken (leak / mangled output) is a negative verdict, not "no verdict":
    # the earlier 0/2-only scheme mixed "red" with "could not measure".
    return 0 if not negative else 3


if __name__ == "__main__":
    sys.exit(main())
