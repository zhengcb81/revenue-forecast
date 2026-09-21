"""Responsiveness self-check: feed every reviewer predicate a mutated input.

A predicate that cannot fail is not a predicate.  Each check below is called twice --
once on the real data and once on a deliberately mutated copy held in memory -- and the
result is recorded.  Nothing on disk is touched.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")

results = {}


def rec(name, real, mutated, mutated_expect_red=True):
    results[name] = {
        "real_holds": real,
        "mutated_holds": mutated,
        "mutated_is_red": (mutated is False) if mutated_expect_red else (mutated is True),
        "responsive": (real is True) and ((mutated is False) if mutated_expect_red
                                          else (mutated is True)),
    }


# 1. hash predicate
def sha_ok(raw: bytes, want: str) -> bool:
    return hashlib.sha256(raw).hexdigest() == want


raw = (ATT / "oracle.md").read_bytes()
want = "e85cb05bc278ce4b5281f84fe7bc75330f247a73a14e040ce16347428ac2015a"
mut = bytearray(raw); mut[0] ^= 1
rec("sha256_of_oracle_md", sha_ok(raw, want), sha_ok(bytes(mut), want))

# 2. prefix-preservation predicate
def prefix_ok(raw: bytes, n: int, want: str) -> bool:
    return hashlib.sha256(raw[:n]).hexdigest() == want


raw = (ATT / "fix_record.md").read_bytes()
mut = bytearray(raw); mut[100] ^= 1
rec("prefix_preserved_fix_record_md",
    prefix_ok(raw, 10352, "68fb580001b2e798376a16b5c964fd47e08d0974555f07f37587d7c536d4055a"),
    prefix_ok(bytes(mut), 10352, "68fb580001b2e798376a16b5c964fd47e08d0974555f07f37587d7c536d4055a"))

# 3. C-matrix predicate: "only C10 leaks"
def c_matrix_pred(probe_json: dict) -> bool:
    return probe_json["c_matrix_leaking"] == ["C10"]


r3 = json.loads((HERE / "probe_product_narrow_r3.json").read_text(encoding="utf-8"))
r2 = json.loads((HERE / "probe_product_narrow.json").read_text(encoding="utf-8"))
rec("c_matrix_only_C10_leaks", c_matrix_pred(r3), c_matrix_pred(r2))

# 4. "no unregistered leak in the after-break quoted family"
def no_question_leak(leaking_chars: list) -> bool:
    return "?" not in leaking_chars


cs_r3 = json.loads((HERE / "charsweep_product_narrow_r3.json").read_text(encoding="utf-8"))
# NOTE ON THE FIRST CONTROL ATTEMPT: feeding the BASE tree's sweep left the predicate
# TRUE as well, because the base tree leaks '?' too -- so the control did not move the
# predicate.  That is a badly-chosen control, not a dead predicate: the predicate can
# only go red when '?' is in the leaking set.  The control is therefore the minimal
# mutation that makes it false, `["?"]`.
rec("no_question_mark_leak", no_question_leak(cs_r3["double_quote_leaking_chars"]),
    no_question_leak(["?"]))

# 5. registration predicate: credential_leaks empty AND secret_leaks == registered_open
def reg_pred(rep: dict) -> bool:
    return (rep["credential_leaks"] == []
            and set(rep["credential_secret_leaks"]) == set(rep["registered_open_rows"]))


rule_r3 = json.loads((HERE / "rule_product_narrow_r3.json").read_text(encoding="utf-8"))
rule_base = json.loads((HERE / "rule_product_base.json").read_text(encoding="utf-8"))
mut_rule = json.loads(json.dumps(rule_r3))
mut_rule["credential_leaks"] = ["synthetic-unregistered-leak"]
rec("registration_sound_on_r3", reg_pred(rule_r3), reg_pred(mut_rule))
rec("registration_sound_pred_vs_base_tree", reg_pred(rule_r3), reg_pred(rule_base))

# 6. recorded-vs-rerun predicate
def repro_pred(a: dict, b: dict) -> bool:
    ra, rb = a.get("rows", []), b.get("rows", [])
    return (len(ra) == len(rb)
            and [x.get("id") for x in ra] == [x.get("id") for x in rb]
            and all(x.get(k) == y.get(k) for x, y in zip(ra, rb) for k in set(x) | set(y)))


rec_a = json.loads((ATT / "scratch/oracle_r3.json").read_text(encoding="utf-8"))
re_a = json.loads((HERE / "oracle_product_narrow_r3.json").read_text(encoding="utf-8"))
mut_a = json.loads(json.dumps(re_a)); mut_a["rows"][3]["out"] = "MUTATED"
rec("recorded_oracle_reproduces", repro_pred(rec_a, re_a), repro_pred(rec_a, mut_a))

# 7. base-tree predicate: only N5c fails on base
def base_pred(rows: list) -> bool:
    n5 = {r["id"]: r["pass"] for r in rows if r["id"].startswith(("N5c", "N5d", "N5e"))}
    return (n5.get("N5c-auth-scheme-lf-secret") is False
            and n5.get("N5d-auth-scheme-obsfold") is True
            and n5.get("N5e-auth-token-key-lf-secret") is True)


base_rows = json.loads((HERE / "oracle_product_base.json").read_text(encoding="utf-8"))["rows"]
mut_rows = json.loads(json.dumps(base_rows))
for r in mut_rows:
    if r["id"].startswith("N5d"):
        r["pass"] = False
rec("only_N5c_fails_on_base", base_pred(base_rows), base_pred(mut_rows))

# 8. verdict-is-negative reading
def neg_pred(rep: dict) -> bool:
    return rep["verdict"] == "negative" and rep["credential_leaks"] == [] and not rep["touched_but_should_not_be"]


mut2 = json.loads(json.dumps(rule_r3)); mut2["verdict"] = "pass"
rec("rule_verdict_is_negative", neg_pred(rule_r3), neg_pred(mut2))

# 9. append-fidelity predicate for binding.json (pure insertion before the final brace)
def binding_reconstructs(raw_b: bytes, before_sha: str, before_bytes: int) -> bool:
    i = raw_b.find(b'\n  "r3_corrections"')
    if i < 0:
        return False
    for cut, tail in ((i - 1, b'\n}\n'),):
        cand = raw_b[:cut] + tail
        if len(cand) == before_bytes and hashlib.sha256(cand).hexdigest() == before_sha:
            return True
    return False


braw = (ATT / "binding.json").read_bytes()
# NOTE ON THE FIRST CONTROL ATTEMPT: mutating a byte inside the APPENDED block left the
# predicate TRUE, because the reconstruction discards everything from the insertion point
# onward.  That is the predicate's domain, not a dead predicate: it asserts the
# PRE-EXISTING content is intact.  The control must therefore mutate a byte inside the
# prefix region (before the insertion point).
i_ins = braw.find(b'\n  "r3_corrections"')
bmut = bytearray(braw); bmut[200] ^= 0x01
bmut = bytes(bmut)
rec("binding_json_pure_insertion",
    binding_reconstructs(braw, "5fd462c93197d5d7b602a03b2ba81841917bab845aa609854e4db98c10e2d9eb", 10139),
    binding_reconstructs(bmut, "5fd462c93197d5d7b602a03b2ba81841917bab845aa609854e4db98c10e2d9eb", 10139))
results["binding_json_pure_insertion"]["insertion_point_byte"] = i_ins
results["binding_json_pure_insertion"]["control_byte_mutated"] = 200

results["all_responsive"] = all(v["responsive"] for v in results.values() if isinstance(v, dict))
(HERE / "responsiveness.json").write_text(json.dumps(results, indent=1, ensure_ascii=False),
                                         encoding="utf-8")
print(json.dumps(results, indent=1, ensure_ascii=False))
