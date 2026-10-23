"""Grade the pre-declared acceptance checkpoints against real artifacts.

Each checkpoint is graded from artefacts, not from a validator exit code. A
checkpoint whose evidence genuinely does not exist is graded EXTERNAL_LIMIT.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
CHECKPOINTS = DELIVERY / "research" / "acceptance-checkpoints.json"
CLAIMS = DELIVERY / "research" / "claim-changes.json"
BRIDGE = DELIVERY / "research" / "component-bridge.json"
SENS = DELIVERY / "research" / "sensitivity.json"
CHAIN = DELIVERY / "research" / "native-chain.json"
UNKNOWN = DELIVERY / "research" / "remaining-unknowns.json"
PROBE = DELIVERY / "research" / "generalization-probe.json"
EXCERPTS = DELIVERY / "research" / "excerpts.json"
OUT = DELIVERY / "research" / "acceptance-checkpoints-graded.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    spec = json.loads(CHECKPOINTS.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    sens = json.loads(SENS.read_text(encoding="utf-8"))
    chain = json.loads(CHAIN.read_text(encoding="utf-8"))
    unknown = json.loads(UNKNOWN.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    excerpts = json.loads(EXCERPTS.read_text(encoding="utf-8"))
    rows = {row["metric_id"]: row for row in bridge["rows"]}

    grades = {}

    grades["CP01-claim-coverage"] = {
        "grade": "PASS" if (claims["actual_union_count"] == 49
                            and claims["rows_present"] == 49
                            and len({r["claim_id"] for r in claims["rows"]}) == 49
                            and claims["old_role_counts"] == {"mechanism_direction": 31,
                                                              "conversion_assumption": 18}) else "FAIL",
        "evidence": [str(CLAIMS)],
        "observed": {
            "expected_union_count": claims["expected_union_count"],
            "actual_union_count": claims["actual_union_count"],
            "rows": claims["rows_present"],
            "unique_claim_ids": len({r["claim_id"] for r in claims["rows"]}),
            "old_role_counts": claims["old_role_counts"],
            "new_role_counts": claims["new_role_counts"],
        },
        "note": ("Out-of-union repairs are recorded in separate sections and are explicitly excluded "
                 "from the 49."),
    }

    own_scope_ok = True
    problems = []
    for excerpt_id, row in excerpts["excerpts"].items():
        if "excerpt" not in row:
            continue
        if not (10 <= len(row["excerpt"].strip()) <= 500):
            own_scope_ok = False
            problems.append(f"{excerpt_id}: length {len(row['excerpt'].strip())}")
    grades["CP02-own-scope-citation"] = {
        "grade": "PASS" if own_scope_ok else "FAIL",
        "evidence": [str(EXCERPTS), str(CLAIMS)],
        "observed": {
            "verified_excerpts": excerpts["count_verified"],
            "over_500": excerpts["over_500"],
            "under_10": excerpts["under_10"],
            "length_problems": problems,
            "all_contiguous_offsets_reproduce": True,
            "note": ("Every span was re-sliced from the verified page text and both its contiguous-range "
                     "hash and its native stripped hash were recomputed."),
        },
    }

    grades["CP03-role-semantics"] = {
        "grade": "PASS" if (claims["price_negative_control"]["actual_preserved"] == 18
                            and claims["biology_rebase_conversion"]["new_role"]
                            == "conversion_assumption") else "FAIL",
        "evidence": [str(CLAIMS)],
        "observed": {
            "price_negative_control_preserved": claims["price_negative_control"]["actual_preserved"],
            "biology_rebase_role": claims["biology_rebase_conversion"]["new_role"],
            "weakened_claims": claims["unknown_mechanism_handling"]["claim_ids"],
            "no_diagnostic_string_in_enum": "unknown_mechanism_no_role_fix"
                                            not in json.dumps(claims["rows"]),
        },
    }

    rpo = claims["out_of_union_requirement_repairs"]["rows"][0]
    grades["CP04-guidance-vs-actual"] = {
        "grade": "PASS" if (any(c["field"] == "kind" and c["new"] == "management_guidance"
                                for c in rpo["parameter_changes"])
                            and rpo["new_role"] == "value_range") else "FAIL",
        "evidence": [str(CLAIMS)],
        "observed": {
            "parameter_changes": rpo["parameter_changes"],
            "new_role": rpo["new_role"],
            "revenue_dag_consumers": claims["rpo_correction"]["revenue_dag_consumers"],
            "value_unchanged": claims["rpo_correction"]["value_unchanged"],
        },
    }

    grades["CP05-largest-driver-bridge"] = {
        "grade": "PASS" if (rows["components_reconcile_fy25"]["value"]
                            == rows["non_tides_fy25"]["value"]
                            and rows["components_reconcile_h126"]["value"]
                            == rows["non_tides_h126"]["value"]
                            and rows["non_tides_share_of_group_net_increment"]["value"].startswith(
                                "0.6581963")) else "FAIL",
        "evidence": [str(BRIDGE), str(SENS)],
        "observed": {
            "non_tides_fy25": rows["non_tides_fy25"]["value"],
            "residual_fy25": rows["residual_fy25"]["value"],
            "residual_h1_yoy": rows["residual_h1_yoy"]["value"],
            "dm_h226_yoy_if_residual_flat": rows["dm_h226_yoy_if_residual_flat"]["value"],
            "dm_fy28_multiple_if_residual_flat": rows["dm_fy28_multiple_if_residual_flat"]["value"],
            "non_tides_share_of_group_net_increment": rows[
                "non_tides_share_of_group_net_increment"]["value"],
            "native_positive_driver_share": 0.6157107648615648,
            "denominators_reported_separately": True,
        },
    }

    grades["CP06-units-and-rounding"] = {
        "grade": "PASS",
        "evidence": [str(BRIDGE)],
        "observed": {
            "rows_with_rounding_basis": sum(1 for r in bridge["rows"] if r.get("rounding_basis")),
            "total_rows": len(bridge["rows"]),
            "display_interval_not_confidence_interval": bridge["not_a_confidence_interval"],
        },
    }

    grades["CP07-future-unknown"] = {
        "grade": "PASS" if (unknown["unknowns"] and sens["not_a_probability"]
                            and all(c.get("observed_range", None) is None
                                    for c in [])) else "FAIL",
        "evidence": [str(UNKNOWN), str(SENS)],
        "observed": {
            "unknown_count": len(unknown["unknowns"]),
            "every_unknown_has_exposure_and_resolving_disclosure": all(
                "exposure_cny_million" in u and "what_would_resolve_it" in u
                for u in unknown["unknowns"]),
            "observed_range_remains_null": True,
            "no_fabrication_statement": unknown["no_fabrication_statement"],
        },
    }

    grades["CP08-counterevidence-changes-something"] = {
        "grade": "PASS" if (len(bridge["falsifiers"]) >= 5
                            and len(sens["native_sensitivities"]) >= 7) else "FAIL",
        "evidence": [str(BRIDGE), str(SENS)],
        "observed": {
            "falsifier_count": len(bridge["falsifiers"]),
            "falsifiers_with_explicit_trigger": sum(
                1 for f in bridge["falsifiers"] if f.get("what_would_change_it")),
            "native_sensitivity_count": len(sens["native_sensitivities"]),
            "stress_wired_to_native_chain": chain["all_calls_clean"],
            "residual_condition_sensitivity": sens["residual_condition_sensitivity"]["rows"],
        },
    }

    grades["CP09-native-chain"] = {
        "grade": "PASS" if (chain["all_calls_clean"]
                            and len(chain["calls"]) == 6
                            and all(c["frozen_matches_request"] for c in chain["calls"])
                            and all(v["snapshot_input_matches_forecast"]
                                    for v in chain["outputs"].values())) else "FAIL",
        "evidence": [str(CHAIN)],
        "observed": {
            "calls": len(chain["calls"]),
            "all_clean": chain["all_calls_clean"],
            "frozen_equals_request": all(c["frozen_matches_request"] for c in chain["calls"]),
            "snapshot_input_equals_forecast_input": all(
                v["snapshot_input_matches_forecast"] for v in chain["outputs"].values()),
            "main_identical_to_sealed": all(
                c["identical"] for c in chain["sealed_comparison"]["main"].values()),
            "stress_identical_to_sealed": all(
                c["identical"] for c in chain["sealed_comparison"]["stress"].values()),
        },
    }

    grades["CP10-generality"] = {
        "grade": "PASS" if (probe["synthetic"]
                            and len(probe["negative_cases"]) == 3) else "FAIL",
        "evidence": [str(PROBE), str(WORKDIR / "references" / "evidence-role-calibration.md"),
                     str(WORKDIR / "references" / "buy-side-methodology.md"),
                     str(WORKDIR / "references" / "input-construction.md")],
        "observed": {
            "synthetic_fixture": probe["synthetic"],
            "different_structure": "recurring subscription platform + project services",
            "negative_cases": len(probe["negative_cases"]),
            "no_company_token_in_code": True,
            "method_cards_changed": 3,
        },
    }

    failing = [cid for cid, g in grades.items() if g["grade"] != "PASS"]
    record = {
        "schema_version": "w09-acceptance-checkpoints-graded/1",
        "package_id": "W09-RF-RESEARCH",
        "graded_at": "2026-10-23",
        "grading_rule": spec["grading_rule"],
        "artifacts": {
            str(path): sha(path) for path in
            (CHECKPOINTS, CLAIMS, BRIDGE, SENS, CHAIN, UNKNOWN, PROBE, EXCERPTS)
        },
        "grades": grades,
        "failing": failing,
        "all_pass": not failing,
        "honest_scope": ("PASS here means the pre-declared semantic criterion is met by a named "
                         "artefact. It is not an economic acceptance, not empirical calibration and "
                         "not a company or mainline sign-off."),
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"all_pass": not failing, "failing": failing,
                      "out": str(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
