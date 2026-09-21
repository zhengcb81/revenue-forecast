"""I-14-D: rule table WITH OUTPUT FIDELITY, updated to the narrowed semantics.

Derived from I-14-C's harness/run_rule_table.py (sha256
10b406d7e9ae359228bf8f1e1ab18dfc01f54b291d64cf75cc1659c71c5c3e6a).  Per card
clause 4, the `cred-multiline-swallow` family's expectations are updated to the
NEW semantics (semantic expectations, not green-washing): on the pre-fix tree
these updated rows FAIL, which is what makes the update load-bearing.

Changes vs I-14-C's table (everything else is byte-for-byte the same content):
  * cred-line-middle-greedy-value  -> cred-line-middle-single-token, expected
    output keeps ` b=2` (was: whole tail swallowed).
  * cred-multiline-swallow         -> expected keeps doc=17 / stage / code /
    request_id (was: `"upload failed for token=" + R`).
  * cred-multiline-then-key        -> expected keeps `\\nnext=1`.
  * NEW cred-auth-multiline-swallow (auth path C13 half).
  * NEW cred-auth-sameline-tail-kept (documents the deliberate same-line keep).
  * NEW cred-partial-multiword-secret (the narrowing's declared residual).
  * NEW cred-quoted-multiword-full (quoting still gives full coverage).

    python run_rule_table_i14d.py --src <iso>/<tree>/src --label <tree> --out <json>
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
    # I-14-D: the value is ONE token (was cred-line-middle-greedy-value under r1
    # semantics, which expected the whole ` b=2` tail to be swallowed).
    ("cred-line-middle-single-token", "a=1 token=" + MARKER + " b=2",
     "a=1 token=" + R + " b=2", "credential"),
    ("cred-line-middle-trailing-punct", "a=1 token=" + MARKER + "; b=2",
     "a=1 token=" + R + "; b=2", "credential"),
    # I-14-D: the multi-line diagnostic block SURVIVES (was the C13 swallow,
    # frozen by I-14-C with expected `"upload failed for token=" + R`).
    ("cred-multiline-swallow", "upload failed for token=" + MARKER
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1",
     "upload failed for token=" + R
     + " doc=17\nstage=summarize code=llm_global_failure request_id=req-1",
     "credential"),
    ("cred-multiline-stopped-by-semicolon", "failed for token=" + MARKER
     + "; see log\nstage=summarize code=llm_global_failure",
     "failed for token=" + R + "; see log\nstage=summarize code=llm_global_failure",
     "credential"),
    # I-14-D: `next=1` survives the newline (was `"token=" + R`).
    ("cred-multiline-then-key", "token=" + MARKER + "\nnext=1",
     "token=" + R + "\nnext=1", "credential"),
    # I-14-D NEW: the auth path can no longer swallow across the newline either.
    ("cred-auth-multiline-swallow", "Authorization: Bearer " + MARKER
     + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize", "credential"),
    # I-14-D NEW: single-line auth tails are still consumed (I-14-C E1 baseline kept).
    ("cred-auth-sameline-tail-kept", "Authorization: Bearer " + MARKER
     + " rejected by provider", "Authorization: " + R, "credential"),
    # a rejected key must not eat the pair that follows it (declared r3 behaviour)
    ("cred-after-url", "url=https://example/x?token=" + MARKER,
     "url=https://example/x?token=" + R, "credential"),
    ("cred-after-flag", "cmd: --token=" + MARKER, "cmd: --token=" + R, "credential"),
    # I-14-D NEW: quoting still gives full multi-word coverage.
    ("cred-quoted-multiword-full", "password: 'iron steel'",
     "password: " + R, "credential"),
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
    # I-14-D NEW residual: a bare secret containing whitespace is redacted only
    # up to its first token - the accepted cost of the narrowing (quote it for
    # full coverage).  Registered per oracle N13, never hidden.
    ("res-partial-multiword-secret", "password: iron steel",
     "password: " + R + " steel", "residual"),
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
    # Exit-code convention (run_card.py / I-14-C r5): 0 = pass, 2 = cannot
    # adjudicate, 3 = adjudication is NEGATIVE.
    return 0 if not negative else 3


if __name__ == "__main__":
    sys.exit(main())
