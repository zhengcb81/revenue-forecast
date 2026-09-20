"""F-M08-04 follow-up: make the recorded card quotation byte-exact.

The r2 correction replaced a wrong quotation (a symbolic formula presented as if it were
printed on L42) with the arithmetic that IS printed -- but the transcribed string dropped
the backticks around the expected output. card_conflict.json is attempt-local, so the
quotation is made byte-exact against card_M08.md itself, with the card's hash recorded.

card_M08.md is owner territory and is read only; it is not modified.

Usage: <iso venv python> -X utf8 -B f04_fix_quote.py [--apply] > f04_fix_quote.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARD = ("C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
        "2026-09-19-three-project-history-audit/execution_v2/card_M08.md")
APPLY = "--apply" in sys.argv
LINE = 42


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> int:
    print("== F-M08-04 follow-up: byte-exact card quotation ==")
    print(f"apply={APPLY}")
    card_raw = open(CARD, "rb").read()
    card_sha = hashlib.sha256(card_raw).hexdigest()
    lines = card_raw.decode("utf-8").split("\n")
    exact = lines[LINE - 1].rstrip("\r")
    print(f"   card_M08.md sha256={card_sha}")
    print(f"   L{LINE} byte-exact = {exact!r}")
    print(f"   L{LINE} sha256 = {hashlib.sha256(exact.encode('utf-8')).hexdigest()}")

    cf_path = os.path.join(BASE, "M08", "a20260919-01", "evidence", "M08",
                           "card_conflict.json")
    before = sha_file(cf_path)
    cf = json.load(open(cf_path, encoding="utf-8"))
    old = cf["conflicting_texts"]["card"]["text_actually_printed_at_L42"]
    print(f"   card_conflict.json before sha256={before}")
    print(f"   recorded quote (r2)     = {old!r}")
    same = old == exact
    print(f"   already byte-exact={same}")
    print(f"   difference: recorded dropped the backticks around the expected output "
          f"({chr(96)}[50]{chr(96)} vs [50])" if not same else "   no difference")

    cf["conflicting_texts"]["card"]["text_actually_printed_at_L42"] = exact
    cf["conflicting_texts"]["card"]["text_actually_printed_at_L42_sha256"] = \
        hashlib.sha256(exact.encode("utf-8")).hexdigest()
    cf["conflicting_texts"]["card"]["card_M08_md_path"] = CARD.replace("/", "\\")
    cf["conflicting_texts"]["card"]["card_M08_md_sha256"] = card_sha
    cf["conflicting_texts"]["card"]["card_M08_md_line"] = LINE
    cf["quotation_correction_r3"] = {
        "finding": "F-M08-04 follow-up",
        "field": "conflicting_texts.card.text_actually_printed_at_L42",
        "was_r2": old,
        "now": exact,
        "why": "the r2 transcription dropped the backticks around the expected output, so "
               "the quotation was still not byte-exact. The r3 value is byte-identical to "
               "card_M08.md L42 (card sha256 recorded above). The card itself is owner "
               "territory and was NOT modified.",
        "index_observation_for_the_owner": (
            "all four index copies print the identical reading-A rendering "
            "'100+40-5-10-15-60=50': card_M08.md:42, model_cards.md:552, "
            "model_cards.json:1930, dispatch.json:5755. The string quoted by the finding "
            "('100+40-5-10+-15-60') appears nowhere. Under reading C the signed rendering "
            "would be '100+40-5+-10+-15-60', which is the sign-presentation correction the "
            "owner has to make (the answer 50 is unchanged)."
        ),
    }
    out = (json.dumps(cf, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    after = hashlib.sha256(out).hexdigest()
    print(f"   card_conflict.json after  sha256={after}")
    if APPLY:
        open(cf_path, "wb").write(out)
        got = sha_file(cf_path)
        print(f"   APPLIED -> {got} match={got == after}")
        assert got == after
    with open(os.path.join(HERE, "f04_fix_quote.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "card_conflict_json": {"path": "evidence/M08/card_conflict.json",
                                   "sha256_before": before, "sha256_after": after},
            "card_M08_md": {"path": CARD, "sha256": card_sha, "line": LINE,
                            "byte_exact_line": exact},
            "quotation_was_byte_exact_before_r3": same,
        }, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("   wrote f04_fix_quote.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
