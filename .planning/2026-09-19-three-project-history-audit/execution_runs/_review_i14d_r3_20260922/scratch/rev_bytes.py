"""Remaining byte-level and registration checks for the r3 review."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
HERE = Path(__file__).resolve().parent
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"

out = {}

r3 = (ATT / "iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py").read_text(encoding="utf-8")
r2 = (ATT / "iso/product_narrow/src/company_wiki/source_catalog/observability.py").read_text(encoding="utf-8")
base = (ATT / "iso/product_base/src/company_wiki/source_catalog/observability.py").read_text(encoding="utf-8")

NINE = "(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"
out["nine_word_enumeration"] = {
    "present_in_r3": NINE in r3,
    "present_in_r2": NINE in r2,
    "present_in_base": NINE in base,
    "bare_list_bearer_token_basic_in_r3": "bearer|token|basic" in r3,
}
out["scheme_token_line"] = [l for l in r3.splitlines() if l.startswith("_AUTH_SCHEME_TOKEN")]
out["scheme_split_lines"] = [l for l in r3.splitlines() if l.strip().startswith(('_AUTH_SCHEME_SPLIT', 'r"(?:(?:', 'r"(?:' + "_AUTH_BARE"))][:6]
out["value_group_line"] = [l for l in r3.splitlines() if "bearer" in l and "_QUOTED_VALUE" in l]
out["break_run_literal_present"] = r"(?:(?:\r?\n)[ \t]*)+" in r3
# the after-break quoted classes, as bytes
out["after_break_dq_class"] = r'\"[^\"\r?\n]*\"' in r3
out["after_break_dq_class_correct_form_absent"] = r'\"[^\"\r\n]*\"' not in r3.split("_AUTH_SCHEME_SPLIT")[1][:200]
out["quoted_value_definition_line"] = [l for l in r3.splitlines() if l.startswith("_QUOTED_VALUE")]

# dangling reference
out["dangling_reference"] = {
    "sentence_present_in_r3_source": "see r3_fix_record.md" in r3,
    "r3_fix_record_md_exists": (ATT / "r3_fix_record.md").exists(),
}

# final_hashes.json: does it still carry the r2-generation hashes for the four carriers?
fh = json.loads((ATT / "after/final_hashes.json").read_text(encoding="utf-8"))
def find_keys(d, needle):
    hits = {}
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "/" + str(i))
        else:
            if needle in path:
                hits[path] = o
    walk(d, "")
    return hits
out["final_hashes_entries"] = {n: find_keys(fh, n) for n in
                               ("oracle.md", "fix_record.md", "binding.json", "review.md")}

# rule-table kind census straight from the source table
spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
    "rt", ATT / "harness/run_rule_table_i14d.py")
rt = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
spec.loader.exec_module(rt)
kinds = {}
for cid, text, exp, kind in rt.TABLE:
    kinds.setdefault(kind, []).append(cid)
out["rule_table_kind_census"] = {k: {"count": len(v), "ids": v} for k, v in kinds.items()}
out["rule_table_total"] = len(rt.TABLE)
out["registered_open_rows_carry_nonmarker"] = {
    cid: (S39 in text and S39 in exp) for cid, text, exp, kind in rt.TABLE
    if kind == "registered_open"}
out["registered_open_rows_carry_marker"] = {
    cid: (rt.MARKER in text) for cid, text, exp, kind in rt.TABLE if kind == "registered_open"}

# oracle census
spec2 = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
    "or", ATT / "harness/run_i14d_oracle.py")
oracle = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec2)
spec2.loader.exec_module(oracle)
okinds = {}
for cid, kind, text, expected, contains, elen, residual in oracle.CASES:
    okinds.setdefault(kind, []).append(cid)
out["oracle_kind_census"] = {k: {"count": len(v), "ids": v} for k, v in okinds.items()}
out["oracle_total"] = len(oracle.CASES)
out["oracle_registered_open_declarations"] = {
    cid: {"input": text, "expected": exp, "residual": res}
    for cid, kind, text, exp, contains, elen, res in oracle.CASES if kind == "registered_open"}

# digit-initial / symbol-initial scheme (the class requires a leading letter)
sys.path.insert(0, str((ATT / "iso/product_narrow_r3/src").resolve()))
from company_wiki.source_catalog.observability import redact_text
out["non_letter_initial_scheme"] = {
    tag: {"out": redact_text(t), "leaks": S39 in redact_text(t)}
    for tag, t in (("digit", "Authorization: 2foo\n" + S39),
                   ("bang", "Authorization: !foo\n" + S39),
                   ("letter", "Authorization: afoo\n" + S39))}

(HERE / "bytes_and_registration.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(out, indent=1, ensure_ascii=False))
