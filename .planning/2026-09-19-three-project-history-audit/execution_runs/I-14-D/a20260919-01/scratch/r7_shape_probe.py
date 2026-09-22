"""r7 record-fix probe (READ-ONLY): exact redact_text outputs for the four
F-REV-R6-01 shapes being registered, on the r6 tree and on product_base.

Hand-derived expectations (r6 semantics: the auth branch consumes the scheme
word + one break run + ONE following token; the pre-break value token stops at
the first whitespace, and a control whitespace at that position terminates the
value WITHOUT letting the break-run consume the next line):

  A1  Authorization: Bearer\nfoo\n<39>\n<marker>
      -> Authorization: <redacted>\n<39>\n<marker>            (87 chars)
  Bcr Authorization: Bo\rt\n<marker>\n<39>
      -> Authorization: <redacted>\rt\n<marker>\n<39>         (89 chars)
  Bvt / Bff: same with \v / \f.

Cross-checks of shapes the r6 reviewer measured (report sections 2.4/2.5):
  X1  Authorization: Bearer\nfoo\n<marker> -> Authorization: <redacted>\n<marker>
  Xcr Authorization: Bo\rt\n<marker>       -> Authorization: <redacted>\rt\n<marker>

product_base (reviewer-measured): every one of these -> "Authorization: <redacted>".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
M = "SYNTHETIC_AUDIT_TOKEN"
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"

INPUTS = {
    "A1-line3-bare-secret-then-marker":
        "Authorization: Bearer\nfoo\n" + S39 + "\n" + M,
    "Bcr-prebreak-cr": "Authorization: Bo\rt\n" + M + "\n" + S39,
    "Bvt-prebreak-vt": "Authorization: Bo\vt\n" + M + "\n" + S39,
    "Bff-prebreak-ff": "Authorization: Bo\ft\n" + M + "\n" + S39,
    "X1-reviewer-marker-line3": "Authorization: Bearer\nfoo\n" + M,
    "Xcr-reviewer-cr-marker": "Authorization: Bo\rt\n" + M,
}

TREES = ["product_narrow_r6", "product_base"]


def load(src: Path):
    for m in [k for k in list(sys.modules) if k.startswith("company_wiki")]:
        del sys.modules[m]
    sys.path.insert(0, str(src))
    from company_wiki.source_catalog.observability import redact_text
    return redact_text


def main() -> int:
    result = {}
    for tree in TREES:
        fn = load(A / "iso" / tree / "src")
        result[tree] = {
            name: {"in": text, "out": fn(text), "out_len": len(fn(text))}
            for name, text in INPUTS.items()
        }
    out = A / "scratch" / "r7_shape_probe.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    for tree, rows in result.items():
        print("==", tree)
        for name, r in rows.items():
            print(f"  {name}\n    in : {r['in']!r}\n    out: {r['out']!r}  ({r['out_len']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
