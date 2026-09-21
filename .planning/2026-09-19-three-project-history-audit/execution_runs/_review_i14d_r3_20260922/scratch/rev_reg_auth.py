"""Isolate the auth-path single-token regressions from the fuzz, excluding the known
and reviewer-accepted N13 assignment-path residual (a bare multi-token value)."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rev_regression_fuzz as F  # noqa: E402

S = F.S39
M = F.M
DQ = '"'
SQ = "'"
inputs = F.build_inputs()
tuples = [(p, s, sep, v, suf) for p in F.PREFIX for s in F.SCHEME for sep in F.SEP
          for v in F.VALUE for suf in F.SUFFIX]
leak = {t: set(json.loads((HERE / ("fuzz_%s.json" % t)).read_text(encoding="utf-8"))["leaks"])
        for t in F.TREES}
reg = sorted(leak["product_narrow_r3"] - leak["product_base"])

AUTH = {"Authorization: ", "authorization:", "Authorization:Bearer",
        "proxy-authorization: ", "authorization = ", "Authorization: Bearer ", "bearer\t",
        "Bearer "}
SINGLE = {S, M, DQ + S + DQ, SQ + S + SQ, S + "?x", DQ + S + '?x' + DQ, DQ + S + 'x' + DQ,
          S + "|x", S + ";x", "x" + S}

auth_reg = [i for i in reg if tuples[i][0] in AUTH and tuples[i][3] in SINGLE]
out = {
    "auth_path_single_token_regressions": len(auth_reg),
    "by_prefix": dict(Counter(tuples[i][0] for i in auth_reg)),
    "by_scheme": dict(Counter(tuples[i][1] for i in auth_reg)),
    "by_sep": dict(Counter(tuples[i][2] for i in auth_reg)),
    "by_value": dict(Counter(tuples[i][3] for i in auth_reg)),
    "scheme_first_char_not_a_letter": sum(1 for i in auth_reg if not tuples[i][1][:1].isalpha()),
    "examples": [inputs[i] for i in auth_reg[:8]],
}
rest = [i for i in auth_reg if tuples[i][1][:1].isalpha()]
out["letter_initial_scheme_regressions"] = len(rest)
out["letter_initial_examples"] = [inputs[i] for i in rest[:12]]
out["letter_initial_by_sep"] = dict(Counter(tuples[i][2] for i in rest))
out["letter_initial_by_value"] = dict(Counter(tuples[i][3] for i in rest))
out["letter_initial_by_scheme"] = dict(Counter(tuples[i][1] for i in rest))
# split by whether the separator contains a line break
brk = [i for i in rest if "\n" in tuples[i][2]]
nob = [i for i in rest if "\n" not in tuples[i][2]]
out["letter_initial_with_break"] = len(brk)
out["letter_initial_without_break"] = len(nob)
out["without_break_examples"] = [inputs[i] for i in nob[:12]]
out["without_break_by_value"] = dict(Counter(tuples[i][3] for i in nob))
out["without_break_by_prefix"] = dict(Counter(tuples[i][0] for i in nob))
out["without_break_by_scheme"] = dict(Counter(tuples[i][1] for i in nob))
(HERE / "regression_authpath.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                               encoding="utf-8")
print(json.dumps(out, indent=1, ensure_ascii=False))
