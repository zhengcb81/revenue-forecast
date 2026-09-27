"""I-14-D-R2: run the FROZEN oracle of this round (oracle.md sha256 71cbff49…).

    python run_oracle_r2.py --src <tree>/src --label <label> --out <json>

Section 4 (inherited, byte-for-byte the r1-frozen 17 cases + the E4b baseline) is
unchanged by this round.  Section 3 (NEW, authorization path) is the fix criterion
of reviewer_report.md L25-L30 / RULING 2.  Every expected string was hand-derived
in oracle.md §3.1 and §4 before any post-fix tree existed.

Exit codes: 0 = all criteria pass, 2 = cannot adjudicate, 3 = at least one failed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

M = "SYNTHETIC_AUDIT_TOKEN"            # 21 chars
RM = "ZQ7_REVIEWER_MARKER_9f3c"        # 24 chars (I-14-C reviewer marker)
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"   # 39 chars (reviewer's credential)
R = "<redacted>"
C13_TAIL = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"

# ---------------------------------------------------------------- section 4 ---
# (id, kind, input, expected, must_contain, expect_len)  -- inherited, unchanged
A_CASES = [
    ("A1-N1-mine", "narrow_must",
     "upload failed for token=" + M + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98),
    ("A2-N1-reviewer", "narrow_must",
     "upload failed for token=" + RM + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98),
    ("A3-N2-middle-line", "narrow_must",
     "a=1 token=" + M + " b=2", "a=1 token=" + R + " b=2", ["b=2"], 24),
    ("A4-N3-newline-then-key", "narrow_must",
     "token=" + M + "\nnext=1", "token=" + R + "\nnext=1", ["next=1"], 23),
    ("A5-N5-auth-multiline", "narrow_must",
     "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize",
     ["doc=17", "stage=summarize"], 48),
    ("A6-N13-partial-multiword-residual", "narrow_must",
     "password: iron steel", "password: " + R + " steel", ["steel"], 26),
    ("A7-N5b-auth-sameline-kept", "keep_must",
     "Authorization: Bearer " + M + " rejected by provider",
     "Authorization: " + R, [], 25),
    ("A8-N6-quoted", "keep_must",
     "password: '" + M + "'", "password: " + R, [], 20),
    ("A9-N7a-untouched-monkey", "keep_must",
     "monkey=banana doc=1\nstage=x", "monkey=banana doc=1\nstage=x", [], None),
    ("A10-N7b-untouched-diagnostics", "keep_must",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", [], None),
    ("A11-N7c-untouched-url", "keep_must",
     "url=https://example/x?page=2", "url=https://example/x?page=2", [], None),
    ("A12-N8-residual-digest", "keep_must",
     "upload failed for digest=" + M, "upload failed for digest=" + M, [], None),
    ("A13-N9-residual-flag", "keep_must",
     "--api-key " + M, "--api-key " + M, [], None),
    ("A14-N10-semicolon-bounded", "keep_must",
     "a=1 token=" + M + "; b=2", "a=1 token=" + R + "; b=2", ["b=2"], None),
    ("A15-N11-ampersand-bounded", "keep_must",
     "GET /x?token=" + M + "&page=2", "GET /x?token=" + R + "&page=2",
     ["&page=2"], None),
    ("A16-N12-no-tail-event", "keep_must",
     "upload failed for token=" + M, "upload failed for token=" + R, [], 34),
    ("A17-N13b-quoted-multiword-full", "keep_must",
     "password: '" + M + "'", "password: " + R, [], None),
]

# A0 - E4b truncation baseline (oracle.md §4 A0)
E4B = {
    "text": "start-" + "x" * 170 + " token=" + M + " " + "y" * 120,
    "in_len": 325,
    "redact_text_len": 314,
    "persisted_len": 200,
    "persisted_tail_after_193": " yyyyyy",
}

# ---------------------------------------------------------------- section 3 ---
# NEW: authorization path.  "auth_must" rows are RED on product_pre (the defect)
# and GREEN on product_post.  "auth_keep" rows are green on both.
P_CASES = [
    ("P1-bearer-lf-secret-doc17", "auth_must",
     "Authorization: Bearer\n" + M + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", ["doc=17"], 32),
    ("P2-s39-lf-secret-doc17", "auth_must",
     "Authorization: Bearer\n" + S39 + "\ndoc=17",
     "Authorization: " + R + "\ndoc=17", ["doc=17"], 32),
    ("P3-bearer-space-lf", "auth_must",
     "Authorization: Bearer \n" + S39, "Authorization: " + R, [], 25),
    ("P4-nospace-colon", "auth_must",
     "Authorization:Bearer\n" + S39, "Authorization:" + R, [], 24),
    ("P5-lowercase-token-key", "auth_must",
     "authorization: token\n" + S39, "authorization: " + R, [], 25),
    ("P6-crlf", "auth_must",
     "Authorization: Bearer\r\n" + S39, "Authorization: " + R, [], 25),
    ("P7-obsfold", "auth_must",
     "Authorization: Bearer\n  " + S39, "Authorization: " + R, [], 25),
    ("P8-midline", "auth_must",
     "stage=summarize Authorization: Bearer\n" + S39 + "\nrequest_id=req-1",
     "stage=summarize Authorization: " + R + "\nrequest_id=req-1",
     ["request_id=req-1"], 58),
    ("P9-tab-sep", "auth_keep",
     "Authorization: Bearer\t" + S39, "Authorization: " + R, [], 25),
    ("P10-sameline", "auth_keep",
     "Authorization: Bearer " + S39, "Authorization: " + R, [], 25),
]

# P11 (oracle.md §3.2, the "落盘" criterion) is evaluated on the P1/P2 rows by
# _check's persisted_* fields, and end-to-end (event JSON written to disk and read
# back) by harness/persist_probe.py.


def _check(text, expected, contains, expect_len, kind, redact_text,
           redact_and_truncate):
    out = redact_text(text)
    # oracle.md §3.2: the "secret_absent" guard is stated for the AUTH rows
    # ("Universal auth guard (applies to every auth_must row)").  Section 4's
    # inherited rows are judged by their own exact/contains/len expectations only:
    # several of them (A12 digest, A13 flag) frozen-ly EXPECT the marker to survive,
    # so applying a global no-secret guard there would be a NEW criterion.
    is_auth = kind.startswith("auth")
    checks = {
        "exact_ok": out == expected,
        "contains_ok": all(c in out for c in contains),
        "len_ok": expect_len is None or len(out) == expect_len,
        "secret_absent": (not is_auth) or ((M not in out) and (S39 not in out)),
    }
    persisted = redact_and_truncate(text)
    checks["persisted_secret_absent"] = (
        (not is_auth) or ((M not in persisted) and (S39 not in persisted)))
    # oracle.md §3.2 P11: the persisted event must carry `<redacted>` - but only for
    # the cases whose expected output contains a redaction.  The inherited
    # "untouched"/residual rows (A9..A13) expect NO redaction at all, and that is
    # their frozen behaviour, so asserting a `<redacted>` there would be a NEW
    # criterion, which this round is not allowed to add to section 4.
    checks["persisted_has_redacted"] = (R not in expected) or (R in persisted)
    checks["persisted_le_200"] = (not is_auth) or (len(persisted) <= 200)
    return out, persisted, checks


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out", required=True)
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
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                                  encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 2

    rows = []
    for sec, cases in (("A_inherited", A_CASES), ("B_auth_new", P_CASES)):
        for cid, kind, text, expected, contains, expect_len in cases:
            out, persisted, checks = _check(text, expected, contains, expect_len,
                                            kind, redact_text, redact_and_truncate)
            rows.append({"section": sec, "id": cid, "kind": kind, "in": text,
                         "expected": expected, "out": out, "out_len": len(out),
                         "expect_len": expect_len, "persisted": persisted, **checks,
                         "pass": all(checks.values())})

    # A0 - E4b
    e4b_out = redact_text(E4B["text"])
    e4b_persisted = redact_and_truncate(E4B["text"])
    e4b_checks = {
        "in_len_ok": len(E4B["text"]) == E4B["in_len"],
        "redact_text_len_ok": len(e4b_out) == E4B["redact_text_len"],
        "persisted_len_ok": len(e4b_persisted) == E4B["persisted_len"],
        "tail_ok": e4b_persisted[193:] == E4B["persisted_tail_after_193"],
        "marker_absent": M not in e4b_persisted and M[:8] not in e4b_persisted,
    }
    rows.append({"section": "A_inherited", "id": "A0-E4b-baseline", "kind": "narrow_must",
                 "in": E4B["text"], "expected": {"redact_text_len": 314,
                                                  "persisted_len": 200,
                                                  "tail_after_193": " yyyyyy"},
                 "out": {"redact_text_len": len(e4b_out),
                         "persisted_len": len(e4b_persisted),
                         "tail_after_193": e4b_persisted[193:]},
                 **e4b_checks, "pass": all(e4b_checks.values())})

    failures = [r["id"] for r in rows if not r["pass"]]
    a_fail = [r["id"] for r in rows if r["section"] == "A_inherited" and not r["pass"]]
    b_fail = [r["id"] for r in rows if r["section"] == "B_auth_new" and not r["pass"]]
    leak_rows = [r["id"] for r in rows
                 if r["section"] == "B_auth_new" and not r.get("secret_absent", True)]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "cases": len(rows),
        "inherited_failed": a_fail,
        "auth_new_failed": b_fail,
        "auth_leak_rows": leak_rows,
        "all_failed": failures,
        "verdict": ("pass" if not failures else
                    "RED-auth-only" if not a_fail else
                    "RED-inherited-regression"),
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=True),
                              encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("label", "cases", "inherited_failed",
                                             "auth_new_failed", "auth_leak_rows",
                                             "verdict")},
                     ensure_ascii=True, indent=2))
    for r in rows:
        if not r["pass"]:
            print("ORACLE-FAIL", r["id"], "expected", repr(r["expected"]),
                  "got", repr(r["out"]))
    return 0 if not failures else 3


if __name__ == "__main__":
    sys.exit(main())
