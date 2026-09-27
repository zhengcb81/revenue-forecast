"""WC-1 / I-14-D-R8: PURE ARITHMETIC for the frozen oracle expectations.

Computes the `expect_len` cells of every NEW oracle row from string literals
ONLY.  This script never imports, reads, or executes the code under test; it
runs BEFORE the oracle freeze so the frozen numbers are arithmetic, not
observation.  Run:  python -B freeze_arithmetic.py
"""

from __future__ import annotations

M = "SYNTHETIC_AUDIT_TOKEN"
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
R = "<redacted>"

NEW_ROWS = [
    # REM-06 (WC-1 1): digit-suffixed credential keys
    ("N14-digit-token2-pair", "token=" + M + " token2=" + S39 + " b=2",
     "token=" + R + " token2=" + R + " b=2"),
    ("N15-digit-secret2", "secret2=" + S39, "secret2=" + R),
    ("N16-digit-password2", "password2=" + M, "password2=" + R),
    ("N17-digit-api-key2", "api_key2=" + M, "api_key2=" + R),
    ("N18-digit-env-secret2", "export SECRET2=" + S39, "export SECRET2=" + R),
    # REM-06 over-redaction pricing (must stay untouched)
    ("N19-untouched-oauth2", "oauth2=abc123 request_id=req-1",
     "oauth2=abc123 request_id=req-1"),
    ("N20-untouched-monkey2", "monkey2=banana", "monkey2=banana"),
    ("N21-untouched-secretary2", "secretary2=alice", "secretary2=alice"),
    ("N22-untouched-tokenizer2", "tokenizer2=whitespace", "tokenizer2=whitespace"),
    # F-REV-R3-05 (WC-1 2): the six after-break value-delimiter forms
    ("N23-auth-break-comma", "Authorization: Bot\n," + S39, "Authorization: " + R),
    ("N24-auth-break-semicolon", "Authorization: Bot\n;" + S39, "Authorization: " + R),
    ("N25-auth-break-ampersand", "Authorization: Bot\n&" + S39, "Authorization: " + R),
    ("N26-auth-break-pipe", "Authorization: Bot\n|" + S39, "Authorization: " + R),
    ("N27-auth-break-dquote", 'Authorization: Bot\n"' + S39, "Authorization: " + R),
    ("N28-auth-break-squote", "Authorization: Bot\n'" + S39, "Authorization: " + R),
    # F-REV-R3-05 scope guard: the SINGLE-line delimiter form must NOT change
    ("N29-auth-sameline-comma-kept", "Authorization: Bot," + S39,
     "Authorization: " + R + "," + S39),
    # F-REV-R5-08 (WC-1 3): registered_open declaration, length not pinned
    ("R3c-two-token-then-wrap-marker", "Authorization: Bearer abc\n" + M,
     "Authorization: " + R + "\n" + M),
]


def main() -> int:
    print("row_id | in_len | out_len (expect_len) | expected repr")
    for row_id, text, expected in NEW_ROWS:
        print(f"{row_id} | {len(text)} | {len(expected)} | {expected!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
