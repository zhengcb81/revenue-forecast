"""Responsiveness (every predicate fed a mutated input) + derivation-by-analogy.

Nothing here writes to the attempt.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
S = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r4_20260922")
MEAS = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_r4_measure_20260922")
PY = str(ATT / "iso/venv/Scripts/python.exe")
REL = "src/company_wiki/source_catalog/observability.py"

results = []


def check(name, real_value, mutation_fn, predicate):
    """predicate(value) must be True on the real value and False on the mutation."""
    real = predicate(real_value)
    try:
        mutated = mutation_fn()
        mut = predicate(mutated)
    except Exception as exc:  # noqa
        mut = f"ERR {exc}"
    results.append((name, real, mut, real and mut is False))
    print(f"{name:52s} real={real!s:6s} mutated={mut!s:6s} responsive={real and mut is False}")


def sha(b):
    return hashlib.sha256(b).hexdigest()


r4b = (ATT / "iso/product_narrow_r4" / REL).read_bytes()
r3b = (ATT / "iso/product_narrow_r3" / REL).read_bytes()
baseb = (ATT / "iso/product_base" / REL).read_bytes()

print("=" * 100)
print("RESPONSIVENESS")
print("=" * 100)

# 1. sha256 of the r4 product copy
check("sha256(r4 product copy) == pin",
      r4b,
      lambda: r4b[:100] + bytes([r4b[100] ^ 1]) + r4b[101:],
      lambda b: sha(b) == "15446f4da6ba256f039e684eaa4bd0c6f45889dc86a624717c6a0ec836e3f2a1")

# 2. byte-region count == 4 (real: r3 vs r4). mutation: r3 vs r3 -> 0
def region_count(a, b):
    import difflib
    return len([o for o in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if o[0] != "equal"])


check("diff regions(r3, r4) == 4",
      (r3b, r4b),
      lambda: (r3b, r3b),                    # identical input -> 0 regions
      lambda p: region_count(*p) == 4)

# 3. inverse reconstruction == r3
def invert(a, b):
    import difflib
    ops = [o for o in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if o[0] != "equal"]
    out = bytearray(b)
    for tag, i1, i2, j1, j2 in reversed(ops):
        out[j1:j2] = a[i1:i2]
    return bytes(out)


check("invert(r3, r4) == r3 byte-for-byte",
      (r3b, r4b),
      lambda: (r3b, r4b[:100] + bytes([r4b[100] ^ 1]) + r4b[101:]),
      lambda p: invert(*p) == r3b)

# 4. recorded r4 oracle run reproduces
rec = json.loads((MEAS / "oracle_r4_harness.json").read_text(encoding="utf-8"))
mine = json.loads((S / "oracle_r4_on_r4.json").read_text(encoding="utf-8"))


def rows_match(a, b):
    ra, rb = {r["id"]: r for r in a["rows"]}, {r["id"]: r for r in b["rows"]}
    return set(ra) == set(rb) and all(ra[k] == rb[k] for k in ra)


check("recorded r4 oracle run == my re-run",
      (rec, mine),
      lambda: (rec, {**mine, "rows": [{**mine["rows"][0], "out": "MUTATED"}] + mine["rows"][1:]}),
      lambda p: rows_match(*p))

# 5. the 28 r3 oracle rows identical on r3 vs r4 tree
o3 = json.loads((S / "r3oracle_on_r3.json").read_text(encoding="utf-8"))
o4 = json.loads((S / "r3oracle_on_r4.json").read_text(encoding="utf-8"))
ob = json.loads((S / "oracle_r4_on_base.json").read_text(encoding="utf-8"))
check("28 r3 oracle rows identical on r3 vs r4 tree",
      (o3, o4),
      lambda: (o3, ob),                      # base tree as the mutation
      lambda p: rows_match(*p))

# 6. over-redaction rows == 9
rr4 = json.loads((S / "r3rule_on_r4.json").read_text(encoding="utf-8"))
rb_ = json.loads((S / "r3rule_on_r3.json").read_text(encoding="utf-8"))
check("over_redaction rows == 9 on the r4 tree",
      rr4,
      lambda: {**rr4, "over_redaction_rows": rr4["over_redaction_rows"][:8]},
      lambda d: len(d["over_redaction_rows"]) == 9)

# 7/8/9. the three leak sets
p4 = json.loads((S / "probe_product_narrow_r4.json").read_text(encoding="utf-8"))
p3 = json.loads((S / "probe_product_narrow_r3.json").read_text(encoding="utf-8"))
check("Q_leaks(r4) == ['Q-scheme-with-q']",
      p4, lambda: p3, lambda d: d["Q_leaks"] == ["Q-scheme-with-q"])
check("CH_leaks(r4) == the two newline chars only",
      p4, lambda: p3,
      lambda d: sorted(d["CH_leaks"]) == sorted(['CH-0a-"', "CH-0a-'", 'CH-0d-"', "CH-0d-'"]))
check("NL_leaks(r4) == []",
      p4, lambda: p3, lambda d: d["NL_leaks"] == [])

# 10. measure_r4 idempotence
check("measure_r4 rerun == recorded r4_measurement.json",
      (MEAS / "r4_measurement.json").read_bytes(),
      lambda: (S / "r4_measurement.json").read_bytes()[:50] + b"X" +
              (S / "r4_measurement.json").read_bytes()[51:],
      lambda b: b == (MEAS / "r4_measurement.json").read_bytes())

# 11. append prefix hash
om = (ATT / "oracle.md").read_bytes()
check("oracle.md prefix[:27119] == registered before_sha256",
      om,
      lambda: om[:100] + bytes([om[100] ^ 1]) + om[101:],
      lambda b: sha(b[:27119]) == "e85cb05bc278ce4b5281f84fe7bc75330f247a73a14e040ce16347428ac2015a")

# 12. the grep instrument that found 0 r4 ids in the r3 harnesses
o_src = (ATT / "harness/run_i14d_oracle.py").read_text(encoding="utf-8")
check("grep 'N5l|N5m|N5n|N5o|question-mark|nonletter' finds 0 in the r3 oracle harness",
      o_src,
      lambda: o_src + "\n# N5l-auth-dq-question-mark\n",
      lambda t: len(re.findall(r"N5l|N5m|N5n|N5o|question-mark|nonletter", t)) == 0)

print()
print(f"responsive: {sum(1 for r in results if r[3])}/{len(results)}")

print()
print("=" * 100)
print("DERIVATION BY ANALOGY of the four new oracle rows")
print("=" * 100)
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"

cases = {r["id"]: r for r in rec["rows"]}
pairs = [
    # new row                     pre-existing frozen row it is derived from   substitution
    ("N5l-auth-dq-question-mark", "N5k-auth-quoted-continuation", "insert '?x' inside the double quotes"),
    ("N5m-auth-sq-question-mark", "N5k-auth-quoted-continuation", "same shape, single quotes"),
    ("N5n-auth-nonletter-scheme-marker", "N5c-auth-scheme-lf-secret", "replace scheme 'Bearer' with '2foo'"),
    ("N5o-auth-nonletter-scheme-secret", "N5c-auth-scheme-lf-secret", "replace scheme 'Bearer' with '!foo'"),
]
for new_id, base_id, why in pairs:
    n, b = cases[new_id], cases[base_id]
    same_expect = n["expected"] == b["expected"]
    same_len = n["expect_len"] == b["expect_len"]
    print(f"{new_id}")
    print(f"   derives from {base_id} ({why})")
    print(f"   input  new = {n['in']!r}")
    print(f"   input  old = {b['in']!r}")
    print(f"   expected identical to the pre-existing frozen row: {same_expect}  ({b['expected']!r})")
    print(f"   declared len identical: {same_len}  ({n['expect_len']} vs {b['expect_len']})")
    print(f"   credential/marker absent from expected: "
          f"{S39 not in n['expected'] and M not in n['expected']}")
    print()
