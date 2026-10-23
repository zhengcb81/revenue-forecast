"""Build the W09 shared-condition stress input from the repaired main input.

Design (pre-declared in research/acceptance-checkpoints.json and the memo):
one common operating shock - a single qualification/acceptance disruption that
pushes one quarter of an explicitly assumed Q4 delivery cohort across the fiscal
boundary, with a conditional catch-up fraction - applied once to each of the two
mutually exclusive Chemistry pools (TIDES and non-TIDES). The same event, the
same exposure fraction, the same boundary indicator, the same catch-up fraction
and the same FX chain are used for every segment, so the shock is not
double-counted and is not a renamed copy of the base input.

The stress input inherits every repaired citation/role/rationale from
forecast/main-input.json; it does not re-introduce the sealed page-prefix
excerpts.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
SEALED_STRESS = (RUN / "execution_replays/r1-remediation-01/phase_b/forecast"
                 / "final3-shared-stress-input.json")
MAIN = WORKDIR / "delivery" / "w09" / "forecast" / "main-input.json"
OUT = WORKDIR / "delivery" / "w09" / "forecast" / "stress-input.json"
NEW_VERSION = "w09-rf-research-20261023-stress-v1"

H1 = "urn:company-wiki:source:sha256:d0dba19ede6e35ae3e127a1da91a42f04262e90d14efeb847bdfbff9b6354a5f"

EVENT_RATIONALE = (
    "One joint acceptance/qualification disruption, applied once to each of the two mutually exclusive "
    "Chemistry pools (TIDES 3,000 and non-TIDES 6,000 CNY million of an explicitly assumed 9,000 CNY "
    "million Q4 delivery cohort; the cohort is a stated condition, below the modelled H2 amounts, not "
    "annual/4 and not an observed customer concentration). 50% of the cohort shifts one quarter across "
    "the FY boundary, of which 80% is recognised in Q1 FY2027 and 20% is cancelled. Funding or capacity "
    "alone is not recognised revenue; contract performance and control transfer remain necessary. The "
    "same exposure, boundary indicator, catch-up fraction and FX chain are shared, so the shock is "
    "counted once.")


def build() -> dict:
    main = json.loads(MAIN.read_text(encoding="utf-8"))
    sealed_stress = json.loads(SEALED_STRESS.read_text(encoding="utf-8"))
    data = deepcopy(main)
    data["forecast_version"] = NEW_VERSION

    params = {p["parameter_id"]: p for p in data["parameters"]}
    claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    # Copy the sealed stress-only parameter/claim machinery, then re-point the
    # base path references at the repaired main input's own parameters.
    sealed_params = {p["parameter_id"]: p for p in sealed_stress["parameters"]}
    sealed_claims = {c["claim_id"]: c for c in sealed_stress["evidence_claims"]}
    for pid, parameter in sealed_params.items():
        if not pid.startswith("shared_"):
            continue
        params[pid] = deepcopy(parameter)
    for cid, claim in sealed_claims.items():
        if not cid.startswith("claim_shared_"):
            continue
        claim = deepcopy(claim)
        claim["verified_by"] = "W09 shared-condition stress declaration (no new original read)"
        claim["verified_date"] = "2026-10-23"
        claims[cid] = claim

    # Rewire the two mutually exclusive Chemistry pools to the shared_* rates.
    # The other segments are not part of the shared event and keep their own
    # parameters, so the shock is not silently spread across unrelated
    # businesses.
    for segment in data["segments"]:
        for scenario, block in segment["scenarios"].items():
            block["driver_parameter_ids"]["growth_rate"] = [
                (f"shared_{pid}" if pid.startswith(("tides_", "non_tides_")) else pid)
                for pid in block["driver_parameter_ids"]["growth_rate"]]

    data["parameters"] = list(params.values())
    data["evidence_claims"] = list(claims.values())

    # Declare the stress event in the existing typed inventory.
    research = data["operating_research"]
    research["inventory"] = [row for row in research["inventory"]
                             if row["item_id"] != "shared_acceptance_stress_event"]
    research["inventory"].append({
        "item_id": "shared_acceptance_stress_event",
        "topic": "shared_bottleneck",
        "disposition": "modeled",
        "rationale": EVENT_RATIONALE,
        "claim_ids": ["claim_shared_q4_acceptance_exposure"],
        "parameter_ids": ["shared_q4_acceptance_exposure", "shared_q4_to_q1_boundary",
                          "shared_2027_catchup_fraction"],
        "driver_ids": [],
        "recognition_note": ("Q4 to next Q1 exactly once. The assumed cohort is a point-acceptance "
                             "subset, not all Chemistry timing and not an observed customer split. A "
                             "funding shock can delay delivery, but financing amounts are excluded from "
                             "revenue."),
        "included_in": None,
    })
    return data


def main() -> int:
    data = build()
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT),
                      "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
                      "version": data["forecast_version"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
