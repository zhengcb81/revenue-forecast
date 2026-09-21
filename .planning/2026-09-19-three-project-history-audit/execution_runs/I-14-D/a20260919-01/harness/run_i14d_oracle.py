"""I-14-D: run the FROZEN new-oracle cases (hand-written expected strings).

Every expected value here was hand-computed in oracle.md section 2 BEFORE this
attempt ran anything; nothing is derived from the function under test.

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
R = "<redacted>"

C13_TAIL = " doc=17\nstage=summarize code=llm_global_failure request_id=req-1"

# (id, kind, input, expected, must_contain, expect_len)
CASES = [
    # ---- NARROW-MUST: RED on product_base, GREEN on product_narrow ------------
    ("N1-mine", "narrow_must",
     "upload failed for token=" + M + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98),
    ("N1-reviewer", "narrow_must",
     "upload failed for token=" + RM + C13_TAIL,
     "upload failed for token=" + R + C13_TAIL,
     ["doc=17", "stage=summarize", "code=llm_global_failure", "request_id=req-1"], 98),
    ("N2-middle-line", "narrow_must",
     "a=1 token=" + M + " b=2",
     "a=1 token=" + R + " b=2",
     ["b=2"], 24),
    ("N3-newline-then-key", "narrow_must",
     "token=" + M + "\nnext=1",
     "token=" + R + "\nnext=1",
     ["next=1"], 23),
    ("N5-auth-multiline", "narrow_must",
     "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize",
     ["doc=17", "stage=summarize"], 48),
    ("N13-partial-multiword-residual", "narrow_must",
     "password: iron steel",
     "password: " + R + " steel",
     ["steel"], 26),
    # ---- KEEP-MUST: GREEN on both trees (I-14-C behaviour preserved) ----------
    ("N5b-auth-sameline-kept", "keep_must",
     "Authorization: Bearer " + M + " rejected by provider",
     "Authorization: " + R, [], 25),
    ("N6-quoted", "keep_must",
     "password: '" + M + "'", "password: " + R, [], 20),
    ("N7a-untouched-monkey", "keep_must",
     "monkey=banana doc=1\nstage=x", "monkey=banana doc=1\nstage=x", [], None),
    ("N7b-untouched-diagnostics", "keep_must",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
     "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001", [], None),
    ("N7c-untouched-url", "keep_must",
     "url=https://example/x?page=2", "url=https://example/x?page=2", [], None),
    ("N8-residual-digest", "keep_must",
     "upload failed for digest=" + M, "upload failed for digest=" + M, [], None),
    ("N9-residual-flag", "keep_must",
     "--api-key " + M, "--api-key " + M, [], None),
    ("N10-semicolon-bounded", "keep_must",
     "a=1 token=" + M + "; b=2", "a=1 token=" + R + "; b=2", ["b=2"], None),
    ("N11-ampersand-bounded", "keep_must",
     "GET /x?token=" + M + "&page=2", "GET /x?token=" + R + "&page=2",
     ["&page=2"], None),
    ("N12-no-tail-event", "keep_must",
     "upload failed for token=" + M, "upload failed for token=" + R, [], 34),
    ("N13b-quoted-multiword-full", "keep_must",
     "password: 'iron steel'", "password: " + R, [], None),
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
    for case_id, kind, text, expected, contains, expect_len in CASES:
        out = redact_text(text)
        checks = {
            "exact_ok": out == expected,
            "contains_ok": all(c in out for c in contains),
            "len_ok": (expect_len is None) or (len(out) == expect_len),
        }
        rows.append({
            "id": case_id, "kind": kind, "in": text, "expected": expected, "out": out,
            "out_len": len(out), "expect_len": expect_len, **checks,
            "pass": all(checks.values()),
        })

    failures = [r["id"] for r in rows if not r["pass"]]
    narrow_fail = [r["id"] for r in rows
                   if r["kind"] == "narrow_must" and not r["pass"]]
    keep_fail = [r["id"] for r in rows if r["kind"] == "keep_must" and not r["pass"]]
    report = {
        "label": args.label,
        "src": args.src,
        "helper_present": True,
        "cases": len(rows),
        "narrow_must_failed": narrow_fail,
        "keep_must_failed": keep_fail,
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
                       "verdict")}, ensure_ascii=True, indent=2))
    for r in rows:
        if not r["pass"]:
            print("ORACLE-FAIL", r["id"], "expected", repr(r["expected"]),
                  "got", repr(r["out"]))
    return 0 if not failures else 3


if __name__ == "__main__":
    sys.exit(main())
