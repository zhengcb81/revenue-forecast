# -*- coding: utf-8 -*-
"""I-13-BC read-only verifier (green + red arms). Invariants J1..J6 frozen in oracle.md §6.
Exit codes: 0=ALL_INVARIANTS_OK; 1=harness failure; 3=invariant violation (named)."""
import argparse
import hashlib
import json
import os
import sys

BANNED_REDLINE_TOKENS = [
    "124,248.63", "124248.63", "38,175.95", "38175.95",
    "118,036.2", "118036.2", "130,461.06", "130461.06",
    "134,919.5", "134919.5", "113,577.74", "113577.74",
    "10,670.89", "10670.89",
]
REDCONTEXT_OK = ["registered_not_consumed", "只登记", "禁消费", "存档", "红线", "registered_value_note"]
PASS_LIKE_ROW_STATUS = {"pass", "qualified", "ready", "buy_side_review_ready", "pass_qualified", "verified"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()
    root, plan = args.root, args.plan

    names = ["reviewer_answers.json", "final_scorecard.json", "handoff.json", "verification.json"]
    missing = [n for n in names if not os.path.isfile(os.path.join(root, n))]
    if missing or not os.path.isfile(os.path.join(root, "oracle.md")):
        print("HARNESS: missing files: %s" % (missing + (["oracle.md"] if not os.path.isfile(os.path.join(root, "oracle.md")) else [])))
        return 1
    try:
        ra = json.load(open(os.path.join(root, "reviewer_answers.json"), encoding="utf-8"))
        fs = json.load(open(os.path.join(root, "final_scorecard.json"), encoding="utf-8"))
        ho = json.load(open(os.path.join(root, "handoff.json"), encoding="utf-8"))
        vf = json.load(open(os.path.join(root, "verification.json"), encoding="utf-8"))
    except Exception as e:
        print("HARNESS: json parse failure: %r" % e)
        return 1

    viol = {}  # J -> list of reasons

    def v(j, msg):
        viol.setdefault(j, []).append(msg)

    # ---- J1 release/authority lock ----
    if ho.get("params_released") is not False:
        v("J1", "handoff.params_released != false")
    if ho.get("implementer_signed") is not False:
        v("J1", "handoff.implementer_signed != false")
    if ho.get("releases_nothing") is not True:
        v("J1", "handoff.releases_nothing != true")
    if ho.get("status") != "review_pending":
        v("J1", "handoff.status != review_pending")
    if ho.get("gate0_passed") is not True:
        v("J1", "handoff.gate0_passed != true")
    if ho.get("git_diff_non_planning") != 0:
        v("J1", "handoff.git_diff_non_planning != 0")
    if ho.get("open2_ban_observed") is not True:
        v("J1", "handoff.open2_ban_observed != true")
    if ho.get("role") != "implementer_i13bc":
        v("J1", "handoff.role != implementer_i13bc")
    dep = fs.get("qualification_statuses", {}).get("deployment_usable", {})
    if dep.get("status") is not False:
        v("J1", "final_scorecard.qualification_statuses.deployment_usable.status != false")
    if fs.get("classification") == "buy_side_review_ready":
        v("J1", "classification must not be buy_side_review_ready in this unit")

    # ---- J2 three-column independence (one column PASS must never mask another) ----
    rows = fs.get("per_model_columns", {}).get("rows", [])
    if len(rows) < 8:
        v("J2", "per_model_columns.rows < 8")
    if fs.get("per_model_columns", {}).get("one_column_pass_never_masks_another") is not True:
        v("J2", "one_column_pass_never_masks_another != true")
    if fs.get("per_model_columns", {}).get("rows_claiming_formal_delivery") != 0:
        v("J2", "rows_claiming_formal_delivery != 0")
    for r in rows:
        mid = r.get("model_id", "?")
        for col in ("formula", "disclosure", "accuracy"):
            c = r.get(col)
            if not isinstance(c, dict) or not str(c.get("status", "")).strip() or not str(c.get("detail", "")).strip():
                v("J2", "row %s column %s empty" % (mid, col))
        acc = (r.get("accuracy") or {}).get("status", "")
        if acc != "unproven":
            v("J2", "row %s accuracy.status != unproven (accuracy column must stay unproven; masking forbidden)" % mid)
        if str(r.get("row_status", "")).strip().lower() in PASS_LIKE_ROW_STATUS:
            v("J2", "row %s row_status pass-like despite unproven accuracy / non-granted columns" % mid)
        disc = str((r.get("disclosure") or {}).get("status", ""))
        form = str((r.get("formula") or {}).get("status", ""))
        if disc in ("not_granted", "not_granted_missing_split", "not_registered_in_read_face") and str(r.get("row_status", "")).strip().lower() in PASS_LIKE_ROW_STATUS:
            v("J2", "row %s formula/mapping PASS masks disclosure=%s" % (mid, disc))
        if ("declined" in form or "not_executable" in form) and str(r.get("row_status", "")).strip().lower() in PASS_LIKE_ROW_STATUS:
            v("J2", "row %s row_status masks formula=%s" % (mid, form))

    # ---- J3 open2 red-line ban ----
    for n in names:
        txt = open(os.path.join(root, n), encoding="utf-8").read()
        if "consumed_for_forecast" in txt:
            v("J3", "%s contains consumed_for_forecast" % n)
        for i, line in enumerate(txt.splitlines(), 1):
            if any(tok in line for tok in BANNED_REDLINE_TOKENS):
                if not any(mk in line for mk in REDCONTEXT_OK):
                    v("J3", "%s L%d red-line token outside registered_not_consumed context" % (n, i))
    if ho.get("params_released") is not False:
        v("J3", "params_released must stay false")
    if ra.get("red_line_registration", {}).get("open2_ban_observed") is not True:
        v("J3", "reviewer_answers.red_line_registration.open2_ban_observed != true")

    # ---- J4 stage-B completeness + zero fabrication ----
    qs = ra.get("five_questions", [])
    if len(qs) != 5:
        v("J4", "five_questions != 5")
    for q in qs:
        if not str(q.get("answer", "")).strip():
            v("J4", "%s answer empty" % q.get("id"))
        if q.get("answerability") not in ("answerable", "partial", "not_answerable"):
            v("J4", "%s answerability invalid" % q.get("id"))
        if not q.get("evidence_refs"):
            v("J4", "%s evidence_refs empty" % q.get("id"))
    ids = [q.get("id") for q in qs]
    if ids != ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        v("J4", "question ids not Q1..Q5")
    q3 = next((q for q in qs if q.get("id") == "Q3"), {})
    if q3.get("answerability") != "not_answerable":
        v("J4", "Q3 must stay not_answerable (no contribution decomposition exists)")
    if q3.get("interaction_allocation") != "none":
        v("J4", "Q3 interaction_allocation != none")
    if q3.get("numeric_contribution_shares") != []:
        v("J4", "Q3 numeric_contribution_shares must be empty (no arbitrary interaction allocation)")
    ec = ra.get("action3_expectation_comparison", {})
    if ec.get("consensus_availability") != "unavailable":
        v("J4", "consensus_availability != unavailable")
    if ec.get("consensus_numbers") != [] or ec.get("market_implied_numbers") != []:
        v("J4", "consensus/market-implied numbers must be empty (no fabricated figures)")
    dc = ra.get("action2_verification", {}).get("driver_contributions", {})
    if dc.get("interaction_allocation") != "none" or dc.get("numeric_contribution_shares") != [] or dc.get("review_result") != "not_available":
        v("J4", "driver_contributions must stay not_available/none/[]")
    ad = ra.get("accounting_distinctions", {})
    if ad.get("scenario_is_probability") is not False:
        v("J4", "scenario_is_probability != false")
    if ad.get("probability_claims_count") != 0:
        v("J4", "probability_claims_count != 0")
    for k in ("production_vs_sales", "gross_vs_net"):
        if ad.get(k, {}).get("never_mixed") is not True:
            v("J4", "%s.never_mixed != true" % k)
    for sname in ("STOP_INVESTOR_USE", "STOP_ACCOUNTING"):
        se = ra.get("stage_b_stop_evaluation", {}).get(sname, {})
        if not isinstance(se.get("triggered"), bool):
            v("J4", "stage_b_stop_evaluation.%s.triggered missing" % sname)
    if not ra.get("gap_routing") or not all(g.get("not_fabricated") is True for g in ra.get("gap_routing", [])):
        v("J4", "gap_routing missing or contains fabricated gap")

    # ---- J5 classification mechanical consistency ----
    ci = fs.get("classification_inputs", {})
    hb = ci.get("hard_blocks_dispositions", {})
    if not hb:
        v("J5", "hard_blocks_dispositions missing")
    established = [k for k, x in hb.items() if not str(x).startswith("not_established")]
    zeros = ci.get("zeros_present")
    ones = ci.get("dimensions_with_score_1")
    if established or (zeros or 0) > 0:
        derived = "blocked"
    elif (ones or 0) > 0:
        derived = "research_draft_needs_review"
    else:
        derived = "buy_side_review_ready"
    if fs.get("classification") != derived:
        v("J5", "classification=%s but rule-derived=%s" % (fs.get("classification"), derived))
    if derived != "buy_side_review_ready" and fs.get("classification") == "buy_side_review_ready":
        v("J5", "ready claimed without all-2 dims + independent signature")
    qs3 = fs.get("qualification_statuses", {})
    vals = [str(qs3.get("research_reviewable", {}).get("status")), str(qs3.get("deployment_usable", {}).get("status")), str(qs3.get("forecast_accuracy", {}).get("status"))]
    if any(x in ("None", "") for x in vals):
        v("J5", "qualification_statuses incomplete")
    if qs3.get("forecast_accuracy", {}).get("status") != "unproven":
        v("J5", "forecast_accuracy must stay unproven")
    if qs3.get("research_reviewable", {}).get("status") == "buy_side_review_ready":
        v("J5", "research_reviewable may not claim ready")
    if len(set(vals)) < 3:
        v("J5", "qualification statuses must stay distinct (not substitute each other)")
    rp = fs.get("stop_conditions_evaluated", {}).get("ready_prohibition", {})
    if rp.get("applied") is not True:
        v("J5", "ready_prohibition.applied != true")
    if fs.get("stop_conditions_evaluated", {}).get("host_receipt_written") is not False:
        v("J5", "host_receipt_written must be false")

    # ---- J6 upstream sha recompute ----
    ups = vf.get("upstream_inputs", [])
    if len(ups) < 10:
        v("J6", "upstream_inputs < 10 items")
    for u in ups:
        p = os.path.join(plan, u.get("path", "").replace("/", os.sep))
        if not os.path.isfile(p):
            v("J6", "upstream missing: %s" % u.get("path"))
            continue
        if sha256_file(p) != u.get("sha256"):
            v("J6", "upstream sha mismatch: %s" % u.get("path"))
        if os.path.getsize(p) != u.get("bytes"):
            v("J6", "upstream bytes mismatch: %s" % u.get("path"))
    shas = {u.get("sha256") for u in ups}
    if "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28" not in shas:
        v("J6", "sealed f2178768 not covered")
    if "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff" not in shas:
        v("J6", "store b2063ac8 not covered")

    if viol:
        for j in sorted(viol):
            for m in viol[j]:
                print("%s: %s" % (j, m))
        print("INVARIANT_VIOLATIONS=%s" % ",".join(sorted(viol)))
        return 3
    print("ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
