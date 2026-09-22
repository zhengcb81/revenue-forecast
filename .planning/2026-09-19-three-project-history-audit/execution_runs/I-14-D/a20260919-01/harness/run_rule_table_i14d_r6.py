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

r2 (review F-REV-D-01 / reviewer RULING 2) adds the `cred-auth-split-*` family:
a KNOWN scheme word followed by a line break puts the secret on a line that has
no `key=` prefix, so the pre-r2 rule persisted it in plaintext.  Each row asserts
the marker is ABSENT; the shared secret here is the 39-char credential the
reviewer measured with (`authsplit_probe.py` carries that exact string).

    python run_rule_table_i14d.py --src <iso>/<tree>/src --label <tree> --out <json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"
# the reviewer's own synthetic 39-char secret (no whitespace); kept separate from
# MARKER so a row can distinguish "the marker leaked" from "a real credential leaked"
REVIEWER_SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"

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
    # r2 / F-REV-D-01 NEW: a KNOWN scheme word followed by a line break.  The secret
    # sits on a line with no `key=` prefix, so before this fix the rule table's
    # `credential_leaks` list was structurally blind to it.  Redacted = closed.
    ("cred-auth-split-bearer-lf", "Authorization: Bearer\n" + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-auth-split-bearer-crlf", "Authorization: Bearer\r\n" + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-auth-split-bearer-obsfold", "Authorization: Bearer\n  " + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-auth-split-bearer-nospace", "Authorization:Bearer\n" + MARKER,
     "Authorization:" + R, "credential"),
    ("cred-auth-split-token-scheme", "authorization: token\n" + MARKER,
     "authorization: " + R, "credential"),
    # ... and the same shape with a REAL-looking credential instead of the marker:
    # a marker-only table cannot see a rule that redacts the marker but not a
    # 39-char token, so this row is the one that would have caught F-REV-D-01.
    ("cred-auth-split-bearer-real-secret", "Authorization: Bearer\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    # ... plus the diagnostics-kept form: the card's goal and its negative clause
    # must hold TOGETHER on this input, which is what the r1 tree could not do.
    ("cred-auth-split-keeps-diagnostics", "Authorization: Bearer\n" + MARKER
     + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize", "credential"),
    # a rejected key must not eat the pair that follows it (declared r3 behaviour)
    ("cred-after-url", "url=https://example/x?token=" + MARKER,
     "url=https://example/x?token=" + R, "credential"),
    ("cred-after-flag", "cmd: --token=" + MARKER, "cmd: --token=" + R, "credential"),
    # I-14-D NEW: quoting still gives full multi-word coverage.
    ("cred-quoted-multiword-full", "password: 'iron steel'",
     "password: " + R, "credential"),

    # ---- r3 / F-REV-R2-01: schemes OUTSIDE the r2 nine-word enumeration --------
    # The r2 branch enumerated nine scheme words, so its coverage was exactly as wide
    # as the list; these rows are the ones that would have caught F-REV-R2-01, and two
    # of them carry a 39-char NON-marker credential rather than the marker, because a
    # marker-only table cannot distinguish "redacts the marker" from "redacts a
    # credential".
    ("cred-auth-generic-negotiate-marker", "Authorization: Negotiate\n" + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-negotiate-real-secret",
     "Authorization: Negotiate\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-aws4-real-secret",
     "Authorization: AWS4-HMAC-SHA256\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-scram-marker", "Authorization: SCRAM-SHA-256\n" + MARKER,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-hawk-real-secret",
     "Authorization: Hawk\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-bot-real-secret", "Authorization: Bot\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-mutual-real-secret",
     "Authorization: Mutual\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-vapid-real-secret", "Authorization: vapid\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-hoba-real-secret", "Authorization: HOBA\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-unknown-word", "Authorization: Zzz\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-generic-keeps-diagnostics",
     "Authorization: Negotiate\n" + REVIEWER_SECRET + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize", "credential"),
    # ... the blank-line shape (one break RUN) and the quoted continuation:
    ("cred-auth-blank-line-secret", "Authorization: Hawk\n\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-quoted-continuation", 'Authorization: Bot\n"' + REVIEWER_SECRET + '"',
     "Authorization: " + R, "credential"),

    # ---- r3 / F-REV-R2-02: OVER-REDACTION, registered so it is measured --------
    # The branch cannot tell a wrapped credential from a diagnostic key, so the first
    # token after a scheme word and a line break is DELETED.  This is the fail-closed
    # direction and it was disclosed in decision.md, but until r3 no row measured it:
    # every matrix row put a credential after the scheme word, so `fidelity_drift []`
    # could not see the cost.  These rows assert the cost exactly.
    ("over-auth-scheme-then-key", "Authorization: Bearer\ndoc=17",
     "Authorization: " + R, "over_redaction"),
    ("over-auth-scheme-then-reqid", "Authorization: Bearer\nrequest_id=req-1",
     "Authorization: " + R, "over_redaction"),
    ("over-auth-scheme-then-stage", "Authorization: Bearer\nstage=summarize",
     "Authorization: " + R, "over_redaction"),
    ("over-auth-token-then-keys", "Authorization: token\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\nstage=summarize", "over_redaction"),
    ("over-auth-crlf-then-key", "Authorization: Bearer\r\ndoc=17",
     "Authorization: " + R, "over_redaction"),
    ("over-auth-obsfold-then-key", "Authorization: Bearer\n  doc=17",
     "Authorization: " + R, "over_redaction"),
    ("over-proxy-auth-then-key", "proxy-authorization: Bearer\ndoc=17",
     "proxy-authorization: " + R, "over_redaction"),
    ("over-auth-scheme-then-marker", "Authorization: Bearer\n" + MARKER,
     "Authorization: " + R, "over_redaction"),
    ("over-auth-generic-then-key", "Authorization: Negotiate\ndoc=17",
     "Authorization: " + R, "over_redaction"),

    # ---- r3 REGISTERED OPEN RESIDUAL ------------------------------------------
    # A two-token value that then wraps is the ONE shape the generalized branch cannot
    # reach without deleting `doc=17` from `cred-auth-split-keeps-diagnostics`; it is
    # registered here as kind `registered_open` so `credential_leaks` cannot silently
    # absorb it (that list is filtered to kind `credential`).
    ("open-two-token-then-wrap", "Authorization: Bearer abc\n" + REVIEWER_SECRET,
     "Authorization: " + R + "\n" + REVIEWER_SECRET, "registered_open"),
    ("open-quoted-two-token", 'Authorization: Bearer abc "' + REVIEWER_SECRET + '"',
     "Authorization: " + R + ' "' + REVIEWER_SECRET + '"', "registered_open"),
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
    # ---- r4 (F-REV-R3-01 and F-REV-R3-04) -------------------------------------------
    ("cred-auth-dq-question-mark", 'Authorization: Bot\n"' + REVIEWER_SECRET + '?x"',
     "Authorization: " + R, "credential"),
    ("cred-auth-sq-question-mark", "Authorization: Bot\n'" + REVIEWER_SECRET + "?x'",
     "Authorization: " + R, "credential"),
    ("cred-auth-nonletter-digit", "Authorization: 2foo\n" + REVIEWER_SECRET + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", "credential"),
    ("cred-auth-nonletter-bang", "Authorization: !foo\n" + MARKER + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", "credential"),
    # ---- r5 (F-REV-R4-05) -----------------------------------------------------------
    ("cred-auth-nontchar-question", "Authorization: Bo?t\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-nontchar-slash", "Authorization: Bo/t\n" + REVIEWER_SECRET + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", "credential"),
    ("cred-auth-nontchar-colon", "Authorization: Bo:t\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-nontchar-equals", "Authorization: Bo=t\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    # ---- r6 (F-REV-R5-01) -----------------------------------------------------------
    ("cred-auth-ampersand", "Authorization: Bo&t\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-apostrophe", "Authorization: Bo't\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-pipe", "Authorization: Bo|t\n" + REVIEWER_SECRET,
     "Authorization: " + R, "credential"),
    ("cred-auth-ampersand-with-key", "Authorization: Bo&t\n" + REVIEWER_SECRET + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", "credential"),
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
            # r2: the marker is 21 chars; a rule can be blind to a credential that is
            # not the marker.  This is the fact that would have caught F-REV-D-01.
            "secret_survives": REVIEWER_SECRET in out,
        })

    credentials = [r for r in rows if r["kind"] == "credential"]
    untouched = [r for r in rows if r["kind"] == "untouched"]
    residuals = [r for r in rows if r["kind"] == "residual"]
    over = [r for r in rows if r["kind"] == "over_redaction"]
    opened = [r for r in rows if r["kind"] == "registered_open"]
    leaks = [r["id"] for r in credentials if r["marker_survives"]]
    secret_leaks = [r["id"] for r in rows if r["secret_survives"]]
    touched = [r["id"] for r in untouched if r["out"] != r["in"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "entries": len(rows),
        "credential_leaks": leaks,
        "credential_secret_leaks": secret_leaks,
        "touched_but_should_not_be": touched,
        # F-REV-D-06: the old key name under-reported the residual inventory (it was
        # filtered on `marker_survives`, so the marker-free residual row was invisible).
        # Both facts are now emitted under names that say what they measure.
        "residuals_with_marker_surviving": [r["id"] for r in residuals
                                            if r["marker_survives"]],
        "residual_rows": [r["id"] for r in residuals],
        # r3 / F-REV-R2-02: the over-redaction family is now REGISTERED, so the cost of
        # the fail-closed branch is a measured fact instead of an invisible one.  These
        # rows assert the loss exactly, so they are `fidelity_ok` and do not affect the
        # verdict; what changes is that the record can no longer claim
        # `fidelity_drift == []` while the branch deletes a diagnostic key.
        "over_redaction_rows": [r["id"] for r in over],
        "over_redaction_touched": [r["id"] for r in over if r["out"] != r["in"]],
        # r3 / F-REV-R2-01: the shape the generalized branch cannot close.  Kept in its
        # own kind so it can never be absorbed into an empty `credential_leaks`.
        "registered_open_rows": [r["id"] for r in opened],
        "registered_open_leaking": [r["id"] for r in opened
                                    if r["marker_survives"] or r["secret_survives"]],
        "fidelity_failures": [{"id": r["id"], "expected": r["expected"], "out": r["out"]}
                              for r in rows if not r["fidelity_ok"]],
        "fidelity_ok": all(r["fidelity_ok"] for r in rows),
        "rows": rows,
    }
    negative = ((not report["fidelity_ok"]) or bool(leaks) or bool(secret_leaks)
                or bool(touched))
    report["verdict"] = "negative" if negative else "pass"
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "entries", "credential_leaks",
                       "credential_secret_leaks", "touched_but_should_not_be",
                       "residuals_with_marker_surviving", "residual_rows",
                       "over_redaction_rows", "over_redaction_touched",
                       "registered_open_rows", "registered_open_leaking",
                       "fidelity_ok", "verdict")}, ensure_ascii=True, indent=2))
    for failure in report["fidelity_failures"]:
        print("FIDELITY-FAIL", failure["id"], "expected", repr(failure["expected"]),
              "got", repr(failure["out"]))
    # Exit-code convention (run_card.py / I-14-C r5): 0 = pass, 2 = cannot
    # adjudicate, 3 = adjudication is NEGATIVE.
    return 0 if not negative else 3


if __name__ == "__main__":
    sys.exit(main())
