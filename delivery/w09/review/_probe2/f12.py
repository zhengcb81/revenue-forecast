import json
from pathlib import Path
from collections import Counter

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
lines = []

sealed_in = json.loads((RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json").read_text(encoding="utf-8"))
mi = json.loads((W / "delivery/w09/forecast/main-input.json").read_text(encoding="utf-8"))
old_roles = Counter(c.get("evidence_role") for c in sealed_in["evidence_claims"])
new_roles = Counter(c.get("evidence_role") for c in mi["evidence_claims"])
lines.append("sealed input roles: %s" % json.dumps(dict(old_roles)))
lines.append("new main roles:     %s" % json.dumps(dict(new_roles)))
delta = {}
for k in set(old_roles) | set(new_roles):
    d = new_roles.get(k, 0) - old_roles.get(k, 0)
    if d:
        delta[k] = d
lines.append("delta: %s" % json.dumps(delta))
lines.append("expected delta from documented changes: mechanism_direction -5 (3 rebase->conversion + 2 unknown->history_base), conversion_assumption +3, history_base +1 (2 in, 1 RPO out), value_range +1 (RPO)")
lines.append("consistent: %s" % (delta == {"mechanism_direction": -5, "conversion_assumption": 3, "history_base": 1, "value_range": 1}))

cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
oour_roles = [(r["claim_id"], r.get("old_role"), r.get("new_role")) for r in cc["out_of_union_repairs"]["rows"]]
lines.append("oour rows old->new roles: %s" % json.dumps(oour_roles))
lines.append("oour rows all keep mechanism_direction: %s" % all(o == "mechanism_direction" and n == "mechanism_direction" for _, o, n in oour_roles))

# 3 biology rebase rows: old mechanism -> new conversion
rebase_ids = [r["claim_id"] for r in cc["rows"] if "rebase" in r["claim_id"] and "biology" in r["claim_id"]]
lines.append("biology rebase rows: %s" % json.dumps(rebase_ids))
for r in cc["rows"]:
    if r["claim_id"] in rebase_ids:
        lines.append("  %s: %s -> %s" % (r["claim_id"], r.get("old_role"), r.get("new_role")))
# 2 unknown rows
for r in cc["rows"]:
    if r["claim_id"] in ("claim_driver_other", "claim_driver_discontinued"):
        lines.append("  %s: %s -> %s" % (r["claim_id"], r.get("old_role"), r.get("new_role")))

(OUTDIR / "f12_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
