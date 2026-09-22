"""I-14-D: run the FROZEN new-oracle cases (hand-written expected strings).

Every expected value here was hand-computed in oracle.md section 2 BEFORE this
attempt ran anything; nothing is derived from the function under test.

r2 (review F-REV-D-01 / reviewer RULING 2) adds N5c/N5d, the auth newline-split
family the pre-fix rule left in the clear.  They are hand-computed too: the
`_AUTH_SCHEME_SPLIT` alternative consumes the scheme word, the line break and the
secret token but NOT the break or the indentation, so those stay in the output.

    python run_i14d_oracle.py --src <iso>/<tree>/src --label <label> --out <json>

Exit codes (run_card.py convention): 0 = pass, 2 = cannot adjudicate (helper
absent), 3 = negative verdict (at least one case mismatched).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

M = "SYNTHETIC_AUDIT_TOKEN"            # 21 chars, this attempt's marker
RM = "ZQ7_REVIEWER_MARKER_9f3c"        # 24 chars, the I-14-C reviewer's marker
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"   # 39 chars, the reviewer's credential
R = "<redacted>"

C13_TAIL = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"

# (id, kind, input, expected, must_contain, expect_len, residual)
#
# `residual` is the r3 addition: the expected string when the semantics deliberately
# leave the credential in place (an OPEN leak the record registers rather than hides).
# Empty string means "the case must not leak"; anything else is checked instead of the
# marker-absent guard, so an open leak is a PASS only when it leaks exactly what the
# record says it leaks.
CASES = [
    # ---- NARROW-MUST: RED on product_base, GREEN on product_narrow ------------
    ("N1-mine", "narrow_must",
     "upload failed for token=" + M + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98, ""),
    ("N1-reviewer", "narrow_must",
     "upload failed for token=" + RM + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98, ""),
    ("N2-middle-line", "narrow_must",
     "a=1 token=" + M + " b=2",
     "a=1 token=" + R + " b=2",
     ["b=2"], 24, ""),
    ("N3-newline-then-key", "narrow_must",
     "token=" + M + "\nnext=1",
     "token=" + R + "\nnext=1",
     ["next=1"], 23, ""),
    ("N5-auth-multiline", "narrow_must",
     "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize",
     ["doc=17", "stage=summarize"], 48, ""),
    # r2 / F-REV-D-01: the scheme word and the secret are on DIFFERENT lines.  The
    # secret's line has no `key=` prefix, so this is the family the frozen oracle,
    # the rule table and M1..M3 all missed.  Fail closed: redact the first token
    # after the break, keep the break and the diagnostics.
    ("N5c-auth-scheme-lf-secret", "narrow_must",
     "Authorization: Bearer\n" + M + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    # ... obs-fold variant (RFC 7230 folded header: the continuation is indented).
    # r3 consumes the indentation along with the token, so the output is the bare
    # redaction (r2 left `\n  ` outside the match; both keep the secret out).
    ("N5d-auth-scheme-obsfold", "narrow_must",
     "Authorization: Bearer\n  " + M,
     "Authorization: " + R,
     [], 25, ""),
    # ... and the same hole reachable through the `authorization: <scheme>` key
    # alternative (scheme word `token`) rather than the `bearer` key alternative.
    ("N5e-auth-token-key-lf-secret", "narrow_must",
     "authorization: token\n" + M,
     "authorization: " + R,
     [], 25, ""),
    # ---- r3 / F-REV-R2-01: the residual the re-review measured ------------------
    # A scheme word OUTSIDE the r2 nine-word enumeration.  The pre-break token is now
    # one RFC-7235 scheme token, so these close where r2 persisted the credential.
    ("N5f-auth-generic-scheme-marker", "narrow_must",
     "Authorization: Negotiate\n" + M + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    ("N5g-auth-generic-scheme-secret", "narrow_must",
     "Authorization: AWS4-HMAC-SHA256\n" + S39 + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    ("N5h-auth-unknown-word-secret", "narrow_must",
     "Authorization: Zzz\n" + S39 + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    ("N5i-auth-scram-scheme-marker", "narrow_must",
     "Authorization: SCRAM-SHA-256\n" + M + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    # ... the blank-line shape (one break RUN, not exactly one break):
    ("N5j-auth-blank-line-secret", "narrow_must",
     "Authorization: Hawk\n\n" + S39,
     "Authorization: " + R,
     [], 25, ""),
    # ... and the quoted continuation after the break:
    ("N5k-auth-quoted-continuation", "narrow_must",
     'Authorization: Bot\n"' + S39 + '"',
     "Authorization: " + R,
     [], 25, ""),
    # ---- r3 REGISTERED OPEN RESIDUAL ------------------------------------------
    # A TWO-token value that then wraps.  Closing this needs the scheme's own line
    # consumed as a token run, which deletes `doc=17` from N5 above - measured across
    # the whole design space (r3_fix_record.md).  Registered, not hidden: the case
    # PASSES by leaking exactly this string, and the rule table carries the same row.
    ("R3a-two-token-then-wrap", "registered_open",
     "Authorization: Bearer abc\n" + S39,
     "Authorization: " + R + "\n" + S39,
     [S39], None,
     "Authorization: " + R + "\n" + S39),
    # ... and a quoted two-token value, which the same branch consumes wholly:
    ("R3b-quoted-two-token", "registered_open",
     'Authorization: Bearer abc "' + S39 + '"',
     "Authorization: " + R + ' "' + S39 + '"',
     [S39], None,
     "Authorization: " + R + ' "' + S39 + '"'),
    ("N13-partial-multiword-residual", "narrow_must",
     "password: iron steel",
     "password: " + R + " steel",
     ["steel"], 26, ""),
    # ---- KEEP-MUST: GREEN on both trees (I-14-C behaviour preserved) ----------
    ("N5b-auth-sameline-kept", "keep_must",
     "Authorization: Bearer " + M + " rejected by provider",
     "Authorization: " + R, [], 25, ""),
    ("N6-quoted", "keep_must",
     "password: '" + M + "'", "password: " + R, [], 20, ""),
    ("N7a-untouched-monkey", "keep_must",
     "monkey=banana doc=1\nstage=x", "monkey=banana doc=1\nstage=x", [], None, ""),
    ("N7b-untouched-diagnostics", "keep_must",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", [], None, ""),
    ("N7c-untouched-url", "keep_must",
     "url=https://example/x?page=2", "url=https://example/x?page=2", [], None, ""),
    ("N8-residual-digest", "keep_must",
     "upload failed for digest=" + M, "upload failed for digest=" + M, [], None, ""),
    ("N9-residual-flag", "keep_must",
     "--api-key " + M, "--api-key " + M, [], None, ""),
    ("N10-semicolon-bounded", "keep_must",
     "a=1 token=" + M + "; b=2", "a=1 token=" + R + "; b=2", ["b=2"], None, ""),
    ("N11-ampersand-bounded", "keep_must",
     "GET /x?token=" + M + "&page=2", "GET /x?token=" + R + "&page=2",
     ["&page=2"], None, ""),
    ("N12-no-tail-event", "keep_must",
     "upload failed for token=" + M, "upload failed for token=" + R, [], 34, ""),
    ("N13b-quoted-multiword-full", "keep_must",
     "password: 'iron steel'", "password: " + R, [], None, ""),
    # ---- r4 (F-REV-R3-01 and F-REV-R3-04) -------------------------------------------
    # F-REV-R3-01: the after-break quoted alternatives carried the optional-CR form INSIDE
    # a character class, where '?' is a literal member of the negated set, so a quoted
    # continuation containing '?' was not matched at all.  Both quote styles, both
    # credentials, hand-computed: the whole quoted value is consumed and replaced.
    ("N5l-auth-dq-question-mark", "narrow_must",
     'Authorization: Bot\n"' + S39 + '?x"', "Authorization: " + R, [], 25, ""),
    ("N5m-auth-sq-question-mark", "narrow_must",
     "Authorization: Bot\n'" + S39 + "?x'", "Authorization: " + R, [], 25, ""),
    # F-REV-R3-04: the scheme token class required a leading letter, which is narrower than
    # the RFC 7230 tchar production it cites; a non-letter-initial scheme leaked where the
    # pre-fix base tree redacted.  The class is now the full tchar.
    ("N5n-auth-nonletter-scheme-marker", "narrow_must",
     "Authorization: 2foo\n" + M + "\ndoc=17", "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    ("N5o-auth-nonletter-scheme-secret", "narrow_must",
     "Authorization: !foo\n" + S39 + "\ndoc=17", "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    # ---- r5 (F-REV-R4-05) -----------------------------------------------------------
    # A token containing a NON-tchar character is still a token: `?`, `/`, `:` and `=`
    # are not in the RFC 7230 tchar set, so the r4 pre-break class did not match them and
    # the credential on the next line survived, where the pre-fix base tree redacted it.
    # The pre-break token is now the value-token class this pattern already uses.
    ("N5p-auth-nontchar-question-marker", "narrow_must",
     "Authorization: Bo?t\n" + M, "Authorization: " + R, [], 25, ""),
    ("N5q-auth-nontchar-slash-secret", "narrow_must",
     "Authorization: Bo/t\n" + S39 + "\ndoc=17", "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
    ("N5r-auth-nontchar-colon-marker", "narrow_must",
     "Authorization: Bo:t\n" + M, "Authorization: " + R, [], 25, ""),
    ("N5s-auth-nontchar-equals-marker", "narrow_must",
     "Authorization: Bo=t\n" + M, "Authorization: " + R, [], 25, ""),
    # ---- r6 (F-REV-R5-01) -----------------------------------------------------------
    # The r5 class was a SWAP: it closed `?` and re-opened `&`, `'` and `|`, which r4 had
    # redacted.  The pre-break token is now ANY NON-WHITESPACE RUN, which closes every
    # character r4 or r5 closed and every character either of them leaked, except the space
    # (a space here means a multi-token value, i.e. the registered OPEN shape).
    ("N5t-auth-ampersand-marker", "narrow_must",
     "Authorization: Bo&t\n" + M, "Authorization: " + R, [], 25, ""),
    ("N5u-auth-apostrophe-marker", "narrow_must",
     "Authorization: Bo't\n" + M, "Authorization: " + R, [], 25, ""),
    ("N5v-auth-pipe-marker", "narrow_must",
     "Authorization: Bo|t\n" + M, "Authorization: " + R, [], 25, ""),
    ("N5w-auth-ampersand-secret", "narrow_must",
     "Authorization: Bo&t\n" + S39 + "\ndoc=17", "Authorization: " + R + "\ndoc=17",
     ["doc=17"], 32, ""),
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
        return 2

    rows = []
    for case_id, kind, text, expected, contains, expect_len, residual in CASES:
        out = redact_text(text)
        checks = {
            "exact_ok": out == expected,
            "contains_ok": all(c in out for c in contains),
            "len_ok": (expect_len is None) or (len(out) == expect_len),
        }
        if residual:
            # registered OPEN leak: the credential is EXPECTED to survive, and the
            # only acceptable survival is the one this record names.
            checks["residual_is_declared"] = out == residual
            checks["exact_ok"] = True          # the declared residual IS the expectation
        rows.append({
            "id": case_id, "kind": kind, "in": text, "expected": expected, "out": out,
            "out_len": len(out), "expect_len": expect_len,
            "declared_residual": residual or None, **checks,
            "pass": all(checks.values()),
        })

    failures = [r["id"] for r in rows if not r["pass"]]
    narrow_fail = [r["id"] for r in rows
                   if r["kind"] == "narrow_must" and not r["pass"]]
    keep_fail = [r["id"] for r in rows if r["kind"] == "keep_must" and not r["pass"]]
    open_rows = [r["id"] for r in rows if r["kind"] == "registered_open"]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "cases": len(rows),
        "narrow_must_failed": narrow_fail,
        "keep_must_failed": keep_fail,
        "registered_open": open_rows,
        "registered_open_confirmed": [r["id"] for r in rows
                                      if r["kind"] == "registered_open" and r["pass"]],
        "all_failed": failures,
        "rows": rows,
        "verdict": ("pass" if not failures else
                    "RED-as-expected-pre-fix" if not keep_fail else
                    "negative"),
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("label", "cases", "narrow_must_failed", "keep_must_failed",
                       "registered_open", "registered_open_confirmed",
                       "verdict")}, ensure_ascii=True, indent=2))
    for r in rows:
        if not r["pass"]:
            print("ORACLE-FAIL", r["id"], "expected", repr(r["expected"]),
                  "got", repr(r["out"]))
    return 0 if not failures else 3


if __name__ == "__main__":
    sys.exit(main())
