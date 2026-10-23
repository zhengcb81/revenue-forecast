import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
lines = []

# ---- FIX-6 regression: inputs ----
main_in = (W / "delivery/w09/forecast/main-input.json").read_text(encoding="utf-8")
stress_in = (W / "delivery/w09/forecast/stress-input.json").read_text(encoding="utf-8")
mi = json.loads(main_in)
si = json.loads(stress_in)

# union coverage from ledger
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
lines.append("rows: %d, expected_union: %s, actual: %s, duplicates: %s" % (
    len(cc["rows"]), cc["expected_union_count"], cc["actual_union_count"], cc["duplicate_rows"]))
lines.append("old_role_counts: %s" % json.dumps(cc["old_role_counts"]))
lines.append("new_role_counts: %s" % json.dumps(cc["new_role_counts"]))
ids = [r["claim_id"] for r in cc["rows"]]
lines.append("unique claim ids: %d" % len(set(ids)))

# independently recompute old/new role counts from the ledger rows themselves
from collections import Counter
old_c = Counter(r.get("old_role") for r in cc["rows"])
new_c = Counter(r.get("new_role") for r in cc["rows"])
lines.append("recomputed old roles from rows: %s" % json.dumps(dict(old_c)))
lines.append("recomputed new roles from rows: %s" % json.dumps(dict(new_c)))

# verify against sealed input: old roles
sealed_in = json.loads((RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json").read_text(encoding="utf-8"))
sealed_claims = {c["claim_id"]: c for c in sealed_in.get("evidence_claims", [])}
new_claims_main = {c["claim_id"]: c for c in mi.get("evidence_claims", [])}
new_claims_stress = {c["claim_id"]: c for c in si.get("evidence_claims", [])}
lines.append("sealed input evidence_claims: %d" % len(sealed_claims))
lines.append("new main evidence_claims: %d" % len(new_claims_main))
lines.append("new stress evidence_claims: %d" % len(new_claims_stress))

# old role counts re-derived from sealed input
sealed_roles = Counter(c.get("evidence_role") for c in sealed_in.get("evidence_claims", []))
lines.append("sealed input role counts: %s" % json.dumps(dict(sealed_roles)))
new_roles = Counter(c.get("evidence_role") for c in mi.get("evidence_claims", []))
lines.append("new main input role counts: %s" % json.dumps(dict(new_roles)))

# union coverage: every sealed claim id present in ledger rows
sealed_union_ids = set(sealed_claims)
ledger_ids = set(ids)
lines.append("sealed ids not in ledger rows: %s" % json.dumps(sorted(sealed_union_ids - ledger_ids)))
lines.append("ledger ids not in sealed input: %s" % json.dumps(sorted(ledger_ids - sealed_union_ids)))

# 18 price negative controls: old and new role from ledger
pnc = cc["price_negative_control"]
bad_pnc = []
for r in cc["rows"]:
    if r["claim_id"] in pnc["claim_ids"]:
        if r.get("old_role") != "conversion_assumption" or r.get("new_role") != "conversion_assumption":
            bad_pnc.append(r["claim_id"])
        # also verify against inputs
        sc = sealed_claims.get(r["claim_id"])
        nc = new_claims_main.get(r["claim_id"])
        if sc is not None and sc.get("evidence_role") != "conversion_assumption":
            bad_pnc.append("sealed:" + r["claim_id"])
        if nc is not None and nc.get("evidence_role") != "conversion_assumption":
            bad_pnc.append("new:" + r["claim_id"])
lines.append("price negative control claim ids: %d; violations: %d %s" % (len(pnc["claim_ids"]), len(bad_pnc), json.dumps(bad_pnc)))

# unknown_mechanism_no_role_fix absent from both inputs
lines.append("'unknown_mechanism_no_role_fix' in main-input: %s" % ("unknown_mechanism_no_role_fix" in main_in))
lines.append("'unknown_mechanism_no_role_fix' in stress-input: %s" % ("unknown_mechanism_no_role_fix" in stress_in))

# RPO: management_guidance / value_range / value 42207.0646
def find_params(obj):
    return obj.get("parameters", []) if isinstance(obj, dict) else []

rpo_main = [p for p in mi.get("parameters", []) if "rpo" in str(p.get("parameter_id", "")).lower()]
lines.append("rpo params in main input: " + json.dumps([{k: p.get(k) for k in ("parameter_id", "kind", "value", "support_type")} for p in rpo_main], ensure_ascii=False)[:800])
for p in rpo_main:
    claim_ids = p.get("supporting_claim_ids") or p.get("evidence_claim_ids") or []
    for cid in claim_ids:
        c = new_claims_main.get(cid)
        if c:
            lines.append("  rpo claim %s role=%s" % (cid, c.get("evidence_role")))
rpo_stress = [p for p in si.get("parameters", []) if "rpo" in str(p.get("parameter_id", "")).lower()]
for p in rpo_stress:
    if p.get("parameter_id") == "rpo_expected_2026_opening_cohort":
        lines.append("rpo param in stress input: kind=%s value=%s" % (p.get("kind"), json.dumps(p.get("value"))))
# also search raw text for 42207.0646
lines.append("'42207.0646' in main-input: %s" % ("42207.0646" in main_in))
lines.append("'42207.0646' in stress-input: %s" % ("42207.0646" in stress_in))

(OUTDIR / "f6a_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
