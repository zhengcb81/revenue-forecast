import sys, json, copy
from pathlib import Path
sys.path.insert(0, str(Path("scripts").resolve()))
sys.path.insert(0, str(Path("tests").resolve()))
from research.evidence_roles import analyze_operating_research
from revenue_core import validate_document
from test_research_evidence_roles import calibrated_document

def obs_by_claim(d, claim_id):
    return next(o for o in d["operating_research"]["observations"] if o["claim_id"] == claim_id)

def conv_obs(d):
    return [o for o in d["operating_research"]["observations"] if o["observation_kind"] == "conversion"]

def run(label, d):
    diag = analyze_operating_research(d, validate_document(d))
    cal = diag["calibrations"][0]
    obs_status = {o["claim_id"].replace("claim_parameter_",""): o["binding_status"] for o in diag["evidence_roles"]}
    print(label, "| adequacy:", cal["adequacy_status"], "| reasons:", cal["reasons"])
    print("   binding:", obs_status)
    print("   magnitude:", diag["magnitude_adequacy"]["supported_parameter_ids"])

# Baseline valid fixture
d0 = calibrated_document()
run("BASELINE(valid)", copy.deepcopy(d0))

# Counterexample 1: three conversion observations scope -> unrelated business scope
d1 = copy.deepcopy(d0)
for o in conv_obs(d1):
    o["scope"] = "Unrelated Business Line"
run("CE1 conv scope->unrelated", d1)

# Counterexample 2: three conversion observations period -> FY2031
d2 = copy.deepcopy(d0)
for o in conv_obs(d2):
    o["period"] = "FY2031"
run("CE2 conv period->FY2031", d2)

# Counterexample 3: range endpoints observations + calibration scope -> unrelated product
d3 = copy.deepcopy(d0)
for o in d3["operating_research"]["observations"]:
    if o["observation_kind"] == "quantitative_reference":
        o["scope"] = "Unrelated Product X"
d3["operating_research"]["calibrations"][0]["scope"] = "Unrelated Product X"
run("CE3 range+cal scope->unrelated", d3)
