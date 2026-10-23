import json
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
mi = json.loads((W / "delivery/w09/forecast/main-input.json").read_text(encoding="utf-8"))
si = json.loads((W / "delivery/w09/forecast/stress-input.json").read_text(encoding="utf-8"))
lines = []

claims = {c["claim_id"]: c for c in mi["evidence_claims"]}
# find the RPO expected claim and its role
for c in mi["evidence_claims"]:
    if "rpo" in c["claim_id"].lower() or "rpo" in json.dumps(c.get("parameters", []) if isinstance(c.get("parameters"), list) else []).lower():
        pass
# RPO expected claim id from ledger: claim_rpo_expected_2026_opening_cohort
for cid in ["claim_rpo_expected_2026_opening_cohort"]:
    c = claims.get(cid)
    lines.append("%s in main input: %s" % (cid, c is not None))
    if c:
        lines.append("  role=%s support_type=%s" % (c.get("evidence_role"), c.get("support_type")))
        lines.append("  keys: %s" % ", ".join(c.keys()))
        lines.append("  excerpt head: %s" % str(c.get("excerpt", ""))[:80])
# parameters: find rpo_expected_2026_opening_cohort full record
for p in mi["parameters"]:
    if p.get("parameter_id") == "rpo_expected_2026_opening_cohort":
        lines.append("RPO param full: " + json.dumps(p, ensure_ascii=False)[:1500])
sclaims = {c["claim_id"]: c for c in si["evidence_claims"]}
c = sclaims.get("claim_rpo_expected_2026_opening_cohort")
lines.append("RPO claim in stress input: %s role=%s" % (c is not None, c.get("evidence_role") if c else None))

# RPO DAG consumers: search parameters whose formula/inputs reference rpo_expected
consumers = []
for p in mi["parameters"]:
    blob = json.dumps(p)
    if "rpo_expected_2026_opening_cohort" in blob and p.get("parameter_id") != "rpo_expected_2026_opening_cohort":
        consumers.append(p.get("parameter_id"))
lines.append("parameters referencing rpo_expected (other than itself): %s" % json.dumps(consumers))
for sec in ("segments", "growth_driver_tree", "sensitivity_tests"):
    if sec in mi:
        blob = json.dumps(mi[sec])
        lines.append("'%s' mentions rpo_expected: %s" % (sec, "rpo_expected_2026_opening_cohort" in blob))

(OUTDIR / "f6b_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
