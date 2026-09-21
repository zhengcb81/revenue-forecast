"""Bound the r3 after-break leak class, and prove the cause in memory.

A. after-break UNQUOTED continuation: sweep every printable char.
B. values whose FIRST char after the break is a delimiter (, ; & | " ').
C. same-line quoted value with and without '?' -- separates "the '?' is the cause"
   from "a two-token same-line value is the registered-open shape".
D. CAUSE PROOF: rebind the module's compiled _AUTH_PATTERN to a copy in which ONLY
   the after-break quoted class is corrected (`[^\"\\r?\\n]` -> `[^\"\\r\\n]`) and
   re-run the leaking rows.  Nothing on disk is touched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

S = "ghp_ZQ7ReviewerFakeCredential0123456789"
CH = [chr(c) for c in range(0x20, 0x7F)] + ["\t", "\r", "\n", "\x0b", "\x0c"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    sys.path.insert(0, str(Path(a.src).resolve()))
    from company_wiki.source_catalog import observability as ob
    rt = ob.redact_text

    # A. unquoted continuation sweep
    unquoted_leaks = {}
    for c in CH:
        text = "Authorization: Bot\n" + S + c + "x"
        out = rt(text)
        if S in out:
            unquoted_leaks[repr(c)] = out

    # B. delimiter-initial value after the break
    delim = {}
    for c in [",", ";", "&", "|", '"', "'"]:
        text = "Authorization: Bot\n" + c + S
        out = rt(text)
        delim[repr(c)] = {"out": out, "leaks": S in out}

    # C. same-line quoted, with and without '?'
    sameline = {}
    for tag, text in (("no_q", 'Authorization: Bot "' + S + '"'),
                      ("with_q", 'Authorization: Bot "' + S + '?x"')):
        out = rt(text)
        sameline[tag] = {"out": out, "leaks": S in out}

    # D. cause proof: correct ONLY the after-break quoted class, in memory
    landed = ob._AUTH_PATTERN.pattern
    fixed = landed.replace(r'\"[^\"\r?\n]*\"', r'\"[^\"\r\n]*\"').replace(
        r"'[^'\r?\n]*'", r"'[^'\r\n]*'")
    changed = (fixed != landed)
    before_rows, after_rows = {}, {}
    probes = {
        "X1-dq-question": 'Authorization: Bot\n"' + S + '?x"',
        "X1-sq-question": "Authorization: Bot\n'" + S + "?x'",
        "N5k-control": 'Authorization: Bot\n"' + S + '"',
    }
    for k, text in probes.items():
        before_rows[k] = rt(text)
    ob._AUTH_PATTERN = re.compile(fixed)
    for k, text in probes.items():
        after_rows[k] = rt(text)
    ob._AUTH_PATTERN = re.compile(landed)   # restore in memory

    out = {
        "src": a.src,
        "A_unquoted_continuation_leaking_chars": sorted(unquoted_leaks),
        "A_unquoted_leaking_count": len(unquoted_leaks),
        "A_examples": dict(list(unquoted_leaks.items())[:3]),
        "B_delimiter_initial_value": delim,
        "C_sameline_quoted": sameline,
        "D_cause_proof": {
            "pattern_actually_changed": changed,
            "landed_after_break_quoted_class": r'\"[^\"\r?\n]*\"',
            "corrected_class": r'\"[^\"\r\n]*\"',
            "before_correction": before_rows,
            "after_correction": after_rows,
            "leaks_before": [k for k, v in before_rows.items() if S in v],
            "leaks_after": [k for k, v in after_rows.items() if S in v],
        },
    }
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("A unquoted leaking chars:", sorted(unquoted_leaks))
    print("B:", json.dumps(delim, ensure_ascii=False))
    print("C:", json.dumps(sameline, ensure_ascii=False))
    print("D changed:", changed, "leaks_before:", out["D_cause_proof"]["leaks_before"],
          "leaks_after:", out["D_cause_proof"]["leaks_after"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
