"""Categorise the r3-vs-base fuzz regressions by the dimension that causes them."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rev_regression_fuzz as F  # noqa: E402

HERE = Path(__file__).resolve().parent
inputs = F.build_inputs()
leak = {t: set(json.loads((HERE / ("fuzz_%s.json" % t)).read_text(encoding="utf-8"))["leaks"])
        for t in F.TREES}
reg = sorted(leak["product_narrow_r3"] - leak["product_base"])

# rebuild the tuple for each index
tuples = [(p, s, sep, v, suf)
          for p in F.PREFIX for s in F.SCHEME for sep in F.SEP
          for v in F.VALUE for suf in F.SUFFIX]

by_scheme = Counter(tuples[i][1] for i in reg)
by_prefix = Counter(tuples[i][0] for i in reg)
by_sep = Counter(tuples[i][2] for i in reg)
by_value = Counter(tuples[i][3] for i in reg)

# does every regression have a scheme whose first char is not a letter?
non_letter = [i for i in reg if not (tuples[i][1][:1].isalpha())]
letter = [i for i in reg if tuples[i][1][:1].isalpha()]
# a second cut: does the shape have a break between scheme and value at all?
no_break = [i for i in reg if "\n" not in tuples[i][2] and "\r" not in tuples[i][2]]

report = {
    "regression_count": len(reg),
    "by_scheme": dict(by_scheme),
    "by_prefix": dict(by_prefix),
    "by_sep": dict(by_sep),
    "by_value": dict(by_value),
    "regressions_whose_scheme_does_not_start_with_a_letter": len(non_letter),
    "regressions_whose_scheme_starts_with_a_letter": len(letter),
    "letter_scheme_examples": [inputs[i] for i in letter[:10]],
    "regressions_with_no_line_break_in_the_separator": len(no_break),
    "no_break_examples": [inputs[i] for i in no_break[:6]],
    "distinct_regression_shapes": len({(tuples[i][1], tuples[i][2], tuples[i][3])
                                       for i in reg}),
}
(HERE / "regression_categorised.json").write_text(
    json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=1, ensure_ascii=False))
