import json
import os

PLAN = ".planning/2026-09-19-three-project-history-audit"
R = PLAN + "/execution_runs"
out = []


def p(*a):
    out.append(" ".join(str(x) for x in a))


p5a = json.load(open(R + "/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/provenance.json", encoding="utf-8"))
p("PEND5A prov top:", list(p5a.keys()))
if "external_evidence" in p5a:
    p("external_evidence[0] keys:", list(p5a["external_evidence"][0].keys()))

s3 = json.load(open(R + "/OPEN5-S3-REACQUISITION/a20260925-01/provenance.json", encoding="utf-8"))
p("S3 prov top:", list(s3.keys()))
for k in s3:
    v = s3[k]
    p(" ", k, type(v).__name__, (list(v.keys())[:8] if isinstance(v, dict) else ""))

s4 = json.load(open(R + "/OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/dual_path_verify.json", encoding="utf-8"))
pr = s4.get("provenance_review", {})
p("s4 provenance_review keys:", list(pr.keys()))
op = pr.get("own_provenance", {})
p("own_provenance keys:", list(op.keys()))
p("substitute_attempt04 keys:", list(op.get("substitute_attempt04", {}).keys()))

acct = json.load(open(R + "/OPEN5-S5-ACCT-GRADING/a20260926-01/acct_grading.json", encoding="utf-8"))
p("acct top:", list(acct.keys()))
g2 = acct.get("step1_g2_g3", {}).get("g2_resolution", {})
p("g2 keys:", list(g2.keys()))
bs = g2.get("by_source", {})
p("by_source keys:", list(bs.keys()))
a4 = bs.get("attempt04", {})
p("attempt04 keys:", list(a4.keys()))
p("G2c keys:", list(a4.get("G2c_sha256", {}).keys()) if isinstance(a4.get("G2c_sha256"), dict) else None)
p("g3 station_records:", list(acct.get("step1_g2_g3", {}).get("g3_resolution", {}).keys()))

base = R + "/OPEN5-S5-IND-RULING/a20260926-01/_work/"
with open(base + "probe_json.out.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("ok")
