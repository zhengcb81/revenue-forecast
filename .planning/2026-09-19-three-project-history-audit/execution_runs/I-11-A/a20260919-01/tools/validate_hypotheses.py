"""I-11-A: validate hypotheses.json against the oracle rules and run the frozen
counterexample suite (oracle section 7). Writes validation_report.json.

Rule: the positive case must pass, and every counterexample must be REJECTED with
its fixed error code. A counterexample that passes (i.e. is accepted) fails this run.

Usage:
  python -X utf8 -B tools/validate_hypotheses.py <attempt_root> <out.json> <ascii_log.txt>
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import sys

# --- frozen registry copied from execution_v2/model_cards.md (model_id -> required/optional drivers)
REGISTERED = {
    "direct_growth": ["growth_rate"],
    "direct_revenue": ["revenue"],
    "unit_sales": ["units", "unit_revenue", "timing_factor", "other_revenue"],
    "capacity_utilization": ["capacity", "utilization", "yield", "unit_revenue", "timing_factor", "other_revenue"],
    "subscription": ["average_customers", "revenue_per_customer", "timing_factor", "usage_revenue"],
    "usage_platform": ["eligible_activity", "monetization_rate", "fixed_revenue"],
    "services": ["billable_capacity", "utilization", "billing_rate", "timing_factor", "other_revenue"],
    "project_backlog": ["opening_backlog", "bookings", "cancellations", "contract_changes",
                        "closing_backlog", "backlog_remeasurements"],
    "resource": ["saleable_volume", "realized_price", "other_revenue"],
    "reserve_depletion": ["opening_reserves", "additions", "depletion", "closing_reserves",
                          "recovery_rate", "realized_price", "other_revenue", "reserve_revisions"],
    "infrastructure": ["billable_volume", "tariff", "other_revenue"],
    "bank_revenue": ["average_earning_assets", "asset_yield", "average_interest_bearing_liabilities",
                     "funding_cost", "fee_revenue", "other_revenue"],
    "asset_management": ["average_aum", "management_fee_rate", "performance_fee_revenue", "other_revenue"],
    "retail_franchise": ["average_owned_stores", "revenue_per_owned_store", "franchise_system_sales",
                         "recognized_fee_rate", "supply_revenue"],
    "transport": ["capacity", "utilization", "yield", "ancillary_revenue"],
    "real_estate_rental": ["average_occupied_area", "rent_per_area", "other_revenue"],
    "licensing_commercial": ["treated_units", "net_revenue_per_unit", "milestone_revenue",
                             "royalty_revenue", "service_revenue"],
    "advertising": ["eligible_impressions", "fill_rate", "revenue_per_thousand_impressions", "other_revenue"],
    "gaming": ["active_users", "payer_conversion", "revenue_per_payer", "other_revenue"],
    "cohort_subscription": ["opening_customers", "new_customers", "churned_customers",
                            "ending_customers", "revenue_per_customer", "timing_factor",
                            "usage_revenue", "new_customer_revenue_fraction", "churned_customer_lost_fraction"],
    "delivery_pipeline": ["opening_orders", "new_orders", "cancellations", "deliveries",
                          "ending_orders", "unit_revenue", "timing_factor", "other_revenue"],
    "milestone_royalty": ["eligible_sales", "royalty_rate", "milestone_revenue", "service_revenue"],
    "insurance_service": ["coverage_units", "revenue_per_coverage_unit", "timing_factor", "other_revenue"],
    "subscription_arr_bridge": ["opening_arr", "expansion_arr", "new_arr", "closing_arr",
                                "gross_retention_rate", "lost_arr_revenue_fraction",
                                "expansion_revenue_fraction", "new_arr_revenue_fraction", "usage_revenue"],
    "installed_base_aftermarket": ["opening_installed_units", "new_installed_units", "retired_units",
                                   "closing_installed_units", "new_unit_revenue_fraction",
                                   "retirement_lost_fraction", "attach_rate", "annual_revenue_per_attached_unit"],
    "store_cohorts": ["opening_stores", "new_stores", "closed_stores", "closing_stores",
                      "new_store_revenue_fraction", "closure_lost_fraction", "new_store_productivity",
                      "annual_revenue_per_mature_store"],
    "renewable_generation": ["average_commissioned_mw", "period_hours", "pre_curtailment_capacity_factor",
                             "curtailment_rate", "contracted_share", "contract_price_per_mwh",
                             "merchant_price_per_mwh", "other_revenue"],
    "aum_fee_bridge": ["opening_aum", "inflows", "outflows", "market_change", "closing_aum",
                       "inflow_revenue_fraction", "outflow_lost_fraction",
                       "market_change_revenue_fraction", "management_fee_rate",
                       "recognized_performance_fees"],
    "commercial_launch": ["eligible_units", "annual_supply_capacity", "adoption_rate",
                          "commercial_year_fraction", "net_revenue_per_unit"],
    "finite_adoption": ["opening_unserved_market", "new_eligible_units", "removed_eligible_units",
                        "adopted_units", "closing_unserved_market", "net_revenue_per_unit"],
    "inventory_sellthrough": ["opening_inventory", "saleable_production", "purchased_units",
                              "scrapped_units", "sold_units", "closing_inventory", "net_revenue_per_unit"],
}

SOURCE_TYPES = {"company_disclosure", "independent_observation", "management_target",
                "analyst_assumption", "synthetic"}
LOCATION_BASES = {"pdf_leaf_1based", "table_index_0based"}
# groups that are declared management-target groups; a management_target must live
# in one of these and a company_disclosure must not
MGMT_GROUPS = {"ZIJIN-MGMT-PLAN-2026"}
# reviewer strings that identify the card implementer (I-11-A has no independent
# reviewer, so these must never appear on an approved_frozen proposition)
IMPLEMENTER_MARKERS = {"本卡实现者", "implementer", "I-11-A implementer", "弱模型"}
STATES = {"unquantified", "pending_professional_decision", "approved_frozen",
          "STOP_EVIDENCE", "STOP_DISCLOSURE_ADAPTATION"}
REQUIRED_TOP = [
    "hypothesis_id", "claim", "state", "state_reason", "source", "observation",
    "mechanism_chain", "parameter_mapping", "calibration", "dependency_control",
    "double_count_exclusion", "falsifier", "falsifier_candidates", "refuted_by",
    "alternative_explanations", "independent_contract_claims", "machine_verifiable",
    "evidence_path", "page_index_basis", "anchor_text", "reviewer",
]
FALSIFIER_KEYS = ["observable", "threshold", "threshold_basis", "observation_date",
                  "source_route", "revert_rule"]


def _norm(s: str) -> str:
    out = []
    for ch in str(s):
        if ch.isspace() or ch == ",":
            continue
        out.append("-" if ch in "−–—" else ch)
    return "".join(out)


def validate(hypotheses, source_map, attempt, doc_texts):
    errors = []
    seen_params = {}
    for i, h in enumerate(hypotheses):
        hid = h.get("hypothesis_id", "index-%d" % i)

        def err(code, detail):
            errors.append({"hypothesis_id": hid, "code": code, "detail": detail})

        for field in REQUIRED_TOP:
            if field not in h:
                err("E_EMPTY_FIELD", "missing top-level field %s" % field)
        for field in ("hypothesis_id", "claim", "state", "state_reason"):
            if not h.get(field):
                err("E_EMPTY_FIELD", "empty %s" % field)
        if not isinstance(h.get("source"), dict) or not h.get("source"):
            err("E_EMPTY_FIELD", "source empty")
        if not isinstance(h.get("observation"), dict) or not h["observation"].get("raw_value"):
            err("E_EMPTY_FIELD", "observation.raw_value empty")
        if not h.get("mechanism_chain") or len(h["mechanism_chain"]) < 3:
            err("E_EMPTY_FIELD", "mechanism_chain needs >=3 links")
        if h.get("state") not in STATES:
            err("E_EMPTY_FIELD", "state not in closed set: %s" % h.get("state"))

        src = h.get("source", {})
        st = src.get("source_type")
        if st not in SOURCE_TYPES:
            err("E_SOURCE_TYPE_CLOSED", "source_type=%r" % st)
        if st == "synthetic":
            err("E_SOURCE_TYPE_CLOSED", "synthetic is forbidden in hypotheses.json")
        if src.get("page_index_basis") not in LOCATION_BASES:
            err("E_BAD_PAGE_BASIS", "page_index_basis=%r not in %s"
                % (src.get("page_index_basis"), sorted(LOCATION_BASES)))
        for f in ("doc_id", "doc_sha256", "strategy", "page_index_basis", "page_span",
                  "anchor_text", "published_at", "available_at", "as_of",
                  "independence_group"):
            if not src.get(f):
                err("E_EMPTY_FIELD", "source.%s empty" % f)
        if st == "management_target":
            group = src.get("independence_group")
            if group not in MGMT_GROUPS:
                err("E_MGMT_TARGET_INDEPENDENT",
                    "management_target must carry a declared management-target independence_group, got %r" % group)
            for other in hypotheses:
                if other is h:
                    continue
                osrc = other.get("source", {})
                if osrc.get("independence_group") != group:
                    continue
                # the same management-target group may cover several propositions
                # about the same target document, but it must never mix kinds and
                # never be shared with a different document
                if osrc.get("source_type") != "management_target":
                    err("E_MGMT_TARGET_INDEPENDENT",
                        "group %s mixes a management_target with %s" % (group, osrc.get("source_type")))
                if osrc.get("doc_id") != src.get("doc_id"):
                    err("E_MGMT_TARGET_INDEPENDENT",
                        "group %s is shared by different documents" % group)
            if not h.get("calibration", {}).get("management_target_is_not_independent"):
                err("E_MGMT_TARGET_INDEPENDENT",
                    "calibration.management_target_is_not_independent must be true")
        elif st == "company_disclosure":
            if src.get("independence_group") in MGMT_GROUPS:
                err("E_MGMT_TARGET_INDEPENDENT",
                    "company_disclosure uses the management-target group %s"
                    % src.get("independence_group"))

        pm = h.get("parameter_mapping", {})
        model = pm.get("model_id")
        driver = pm.get("driver_name")
        if model not in REGISTERED:
            err("E_UNKNOWN_MODEL", "model_id=%r" % model)
        elif driver not in REGISTERED[model]:
            err("E_UNKNOWN_DRIVER", "driver %r not in model %s" % (driver, model))
        params = [pm.get("parameter_id")] + [p.get("parameter_id")
                                             for p in h.get("additional_parameters", [])]
        for p in params:
            if not p:
                err("E_EMPTY_FIELD", "parameter_id empty")
                continue
            if p in seen_params:
                prev = seen_params[p]
                if (prev["model_id"], prev["driver_name"], prev["effective_period"]) != \
                        (model, driver, pm.get("effective_period")):
                    err("E_DUPLICATE_PARAMETER",
                        "parameter_id %s reused with a different driver/period" % p)
            else:
                seen_params[p] = {"model_id": model, "driver_name": driver,
                                  "effective_period": pm.get("effective_period")}
        for f in ("unit", "original_value", "effective_period", "conversion_formula"):
            if not pm.get(f):
                err("E_EMPTY_FIELD", "parameter_mapping.%s empty" % f)

        fz = h.get("falsifier", {})
        for k in FALSIFIER_KEYS:
            if not fz.get(k):
                err("E_MISSING_FALSIFIER", "falsifier.%s empty" % k)
        if not h.get("refuted_by"):
            err("E_MISSING_REFUTED_BY", "refuted_by empty")
        if not h.get("double_count_exclusion"):
            err("E_NO_DOUBLE_COUNT_RULE", "double_count_exclusion empty")

        # source hash must match the real file
        expected_hash = source_map["documents"]
        match = [d for d in expected_hash if d["doc_id"] == src.get("doc_id")]
        if not match or match[0]["doc_sha256"] != src.get("doc_sha256"):
            err("E_SOURCE_HASH_MISMATCH", "doc_sha256 does not match source_map")

        # anchor text must occur in the extraction output
        corpus = doc_texts.get(src.get("doc_id"), "")
        if src.get("anchor_text") and _norm(src["anchor_text"]) not in _norm(corpus):
            err("E_ANCHOR_NOT_FOUND", "anchor_text not found in extraction output")

        # every cited value of this document must occur in the extraction output
        for d in match:
            for cv in d["cited_values"]:
                if _norm(cv["raw"]) not in _norm(corpus):
                    err("E_LISTED_VALUE_NOT_IN_EVIDENCE",
                        "cited value %s not found in %s" % (cv["raw"], d["extraction_output_path"]))
            # narrative facts are checked against the text extracted from the raw
            # document bytes (not against the table parse)
            npath = d.get("narrative_text_path")
            ncorpus = doc_texts.get(d["doc_id"] + "::narrative", "") if npath else ""
            for cv in d.get("narrative_facts", []):
                if _norm(cv["raw"]) not in _norm(ncorpus):
                    err("E_LISTED_VALUE_NOT_IN_EVIDENCE",
                        "narrative fact %r not found in %s" % (cv["raw"], npath))

        if h.get("state") == "approved_frozen":
            rev = str(h.get("reviewer", ""))
            if rev in IMPLEMENTER_MARKERS or not rev:
                err("E_STATE_APPROVED_BY_IMPLEMENTER",
                    "approved_frozen requires a named independent reviewer, got %r" % rev)
    return errors


def make_counterexamples(hypotheses):
    """Frozen counterexample suite from oracle section 7.

    Each case starts from a deep copy of ONE proposition that passes the positive
    case by itself, so the only expected error code is the injected one. Cases are
    therefore never "rejected" merely because a sibling proposition is broken.
    """
    cases = []
    # pick a minimal single-proposition base that is valid on its own:
    # H-CN-ZIJIN-SEG-01 (its cited values all live on pages 44/327/328 and its
    # anchor text is present).
    base = next(h for h in hypotheses if h["hypothesis_id"] == "H-CN-ZIJIN-SEG-01")
    base = [base]

    def patch(mutator, code, note):
        h = copy.deepcopy(base[0])
        mutator(h)
        cases.append((code, note, [h]))

    def set_empty(h):
        h["claim"] = ""

    patch(set_empty, "E_EMPTY_FIELD", "empty claim")
    patch(lambda h: h["source"].update({"source_type": "synthetic"}), "E_SOURCE_TYPE_CLOSED",
          "synthetic source type")
    patch(lambda h: h["source"].update({"page_index_basis": "printed_page_1based"}),
          "E_BAD_PAGE_BASIS", "printed page basis instead of pdf leaf")
    patch(lambda h: h["source"].update({"source_type": "management_target",
                                        "independence_group": "ZIJIN-AR2025"}),
          "E_MGMT_TARGET_INDEPENDENT", "management target shares the disclosure group")
    patch(lambda h: h["parameter_mapping"].update({"model_id": "not_a_model"}), "E_UNKNOWN_MODEL",
          "unregistered model_id")
    patch(lambda h: h["parameter_mapping"].update({"driver_name": "brand_strength"}),
          "E_UNKNOWN_DRIVER", "driver not in the model card")
    patch(lambda h: h["falsifier"].update({"threshold": None}), "E_MISSING_FALSIFIER",
          "falsifier threshold removed")
    patch(lambda h: h.update({"refuted_by": []}), "E_MISSING_REFUTED_BY", "refuted_by removed")
    patch(lambda h: h.update({"double_count_exclusion": ""}), "E_NO_DOUBLE_COUNT_RULE",
          "double count rule removed")
    patch(lambda h: h["source"].update({"doc_sha256": "0" * 64}), "E_SOURCE_HASH_MISMATCH",
          "wrong document hash")
    patch(lambda h: h["source"].update({"anchor_text": "这段文字不在原文中"}), "E_ANCHOR_NOT_FOUND",
          "anchor text absent from the filing")
    patch(lambda h: h.update({"state": "approved_frozen", "reviewer": "本卡实现者"}),
          "E_STATE_APPROVED_BY_IMPLEMENTER", "implementer tries to self-approve")
    # duplicate parameter across two propositions
    h_a = copy.deepcopy(base[0])
    h_b = copy.deepcopy(base[0])
    h_b["hypothesis_id"] = "CE-DUP"
    h_b["parameter_mapping"]["driver_name"] = "other_revenue"
    h_b["parameter_mapping"]["parameter_id"] = h_a["parameter_mapping"]["parameter_id"]
    h_b["additional_parameters"] = []
    cases.append(("E_DUPLICATE_PARAMETER", "same parameter_id, different driver",
                  [h_a, h_b]))
    # cited value that is not in the evidence (checked against a fabricated
    # source_map entry so the proposition itself stays valid)
    h_c = copy.deepcopy(base[0])
    h_c["hypothesis_id"] = "CE-VALUE"
    h_c["source"]["doc_id"] = "CE-DOC"
    h_c["source"]["doc_sha256"] = "f" * 64
    h_c["source"]["anchor_text"] = "counterexample value"
    h_c["anchor_text"] = "counterexample value"
    cases.append(("E_LISTED_VALUE_NOT_IN_EVIDENCE", "cited value absent from evidence",
                  [h_c]))
    return cases


def main() -> int:
    attempt, out_path, ascii_log = sys.argv[1], sys.argv[2], sys.argv[3]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    hypotheses = json.load(open(os.path.join(ev, "hypotheses.json"), encoding="utf-8"))
    source_map = json.load(open(os.path.join(ev, "source_map.json"), encoding="utf-8"))
    doc_texts = {}
    for d in source_map["documents"]:
        p = os.path.join(attempt, d["extraction_output_path"])
        doc_texts[d["doc_id"]] = open(p, encoding="utf-8").read()
        npath = d.get("narrative_text_path")
        if npath:
            doc_texts[d["doc_id"] + "::narrative"] = open(
                os.path.join(attempt, npath), encoding="utf-8").read()

    positive_errors = validate(hypotheses, source_map, attempt, doc_texts)
    ce_results = []
    for code, note, patched in make_counterexamples(hypotheses):
        if code == "E_LISTED_VALUE_NOT_IN_EVIDENCE":
            sm = copy.deepcopy(source_map)
            sm["documents"].append({
                "doc_id": "CE-DOC", "doc_sha256": "f" * 64,
                "extraction_output_path": "evidence/I-11-A/hypotheses.json",
                "cited_values": [{"key": "ce", "raw": "999,999,999", "page": 1,
                                  "raw_label": "counterexample value"}],
                "narrative_facts": [],
            })
            errs = validate(patched, sm, attempt, doc_texts)
        else:
            errs = validate(patched, source_map, attempt, doc_texts)
        got = sorted({e["code"] for e in errs})
        ce_results.append({
            "expected_code": code,
            "note": note,
            "observed_codes": got,
            "rejected": code in got,
        })

    states = {}
    for h in hypotheses:
        states[h["state"]] = states.get(h["state"], 0) + 1
    source_types = {}
    groups = {}
    threshold_bases = {}
    for h in hypotheses:
        st = h["source"]["source_type"]
        source_types[st] = source_types.get(st, 0) + 1
        g = h["source"]["independence_group"]
        groups[g] = groups.get(g, 0) + 1
        tb = h["falsifier"].get("threshold_basis", "?")
        threshold_bases[tb] = threshold_bases.get(tb, 0) + 1

    report = {
        "attempt_id": "a20260919-01",
        "generated_by": "tools/validate_hypotheses.py",
        "oracle_sections": ["3.1 O-8", "3.2 O-9", "3.3 O-10/O-11", "3.4 O-12/O-13",
                            "3.5 O-14", "4 O-15/O-16", "7 counterexamples"],
        "counts": {
            "hypotheses": len(hypotheses),
            "states": states,
            "source_types": source_types,
            "independence_groups": groups,
            "threshold_bases": threshold_bases,
            "refuted_by_total": sum(len(h["refuted_by"]) for h in hypotheses),
            "falsifier_candidates_total": sum(len(h["falsifier_candidates"]) for h in hypotheses),
            "parameters": sum(1 + len(h.get("additional_parameters", [])) for h in hypotheses),
            "cited_values_total": source_map["counts"]["cited_values_total"],
            "documents": source_map["counts"]["documents"],
            "sources_not_readable": source_map["counts"]["sources_not_readable"],
        },
        "positive_case": {"propositions_checked": len(hypotheses),
                          "errors": positive_errors,
                          "verdict": "pass" if not positive_errors else "fail"},
        "counterexamples": ce_results,
        "counterexample_summary": {
            "cases": len(ce_results),
            "rejected_as_expected": sum(1 for c in ce_results if c["rejected"]),
            "accepted_by_mistake": sum(1 for c in ce_results if not c["rejected"]),
        },
        "qualification_boundary": {
            "formula": "not_applicable_here (no model is executed by this card)",
            "disclosure_adaptation": "not_granted by this card (I-10-A owns it)",
            "accuracy": "not_granted by this card (I-12 owns it)",
        },
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    lines = ["positive case: %s (%d errors)" % (report["positive_case"]["verdict"],
                                                len(positive_errors))]
    for e in positive_errors:
        lines.append("   %s %s: %s" % (e["hypothesis_id"], e["code"], e["detail"]))
    for c in ce_results:
        lines.append("counterexample %-34s rejected=%s observed=%s"
                     % (c["expected_code"], c["rejected"], ",".join(c["observed_codes"])))
    lines.append(json.dumps(report["counts"], ensure_ascii=True, sort_keys=True))
    lines.append(json.dumps(report["counterexample_summary"], sort_keys=True))
    with open(ascii_log, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("wrote", out_path)
    ok = (not positive_errors) and report["counterexample_summary"]["accepted_by_mistake"] == 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
