#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-D read-only verifier. Exit codes (self-described exit_code_legend):
0 = all invariants D1..D10 OK; 1 = harness failure; 2 = no verdict (unused);
3 = named invariant violation. Usage: python _verify.py [--root <attempt_dir>]
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD = "I-12-D"

UPSTREAM = [
    ("U1", "execution_v2/card_I-12-D.md", "c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69"),
    ("U2", "execution_v2/card_I-12-C.md", "49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91"),
    ("U3", "execution_v2/research_cards.json", "4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263"),
    ("U4", "execution_v2/common_research_cards.md", "2c6fad2cfba4e096b0f6ed5436158666fdd51265fbc87ad65227f943f27f484b"),
    ("U5", "execution_v2/START_HERE.md", "5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318"),
    ("U6", "execution_v2/review_and_handoff.md", "602cce399cace78abb8b369ed36ed6e12540361393d636979a12df51e6ff12b9"),
    ("U7", "OWNER_DECISIONS.md", "17c0db1dbdbb96b58c4798b724095e1285b787e78ddb19f4a6be6fea77a0ba8d"),
    ("U8", "execution_runs/I-12-A/a20260926-01/evidence/I-12-A/evaluation_design.json",
     "203dd4a8a138b6456de2b9f7e6b7e34855d137b8d2324caea21185fbb136f2c0"),
    ("U9", "execution_runs/I-12-A/a20260926-01/evidence/I-12-A/professional_approval.json",
     "0befb15460985140476e953e070531592fdbac6d30986e7d163e82637be36bb1"),
    ("U10", "execution_runs/I-12-A/a20260926-01/evidence/I-12-A/design_manifest.json",
     "ad46a6e69dc9fc5c826cf71bb91102e9c86e6d5506e8c9b2c525a73be7fb7178"),
    ("U11", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/sample_manifest.jsonl",
     "679a7a496e87ed953311d8d8139b47576ab84ddf7f0f0a4238991695d4ef0702"),
    ("U12", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/actuals_policy_application.json",
     "998823537e8f493545562a05b1e0308f1865b0231ddb44b1bfc9fee5a7ac3942"),
    ("U13", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_vintages.jsonl",
     "42daea726d9d1d0c5e538881d5f31c663b3a5619a3f2d6dd7350e48a5965cf1f"),
    ("U14", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/baseline_vintages.jsonl",
     "043f31c9441030a003b5d2cba3286676d35fff30a801909e08b255c3f17a2cbc"),
    ("U15", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_manifest.json",
     "03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a"),
    ("U16", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/unblind_receipt.json",
     "99ed0139434a2777f4ede1454782fb83c60f315c3d83e00e1c8b175324e991f1"),
    ("U17", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"),
    ("U18", "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"),
]
BANNED = ["124248.63", "124,248.63", "38175.95"]
REQUIRED_CSV = ["sample_id", "entity", "segment_code", "origin", "horizon_fy", "model_version",
                "actual", "forecast_base", "baseline_primary", "signed_error", "abs_error",
                "baseline_abs_error", "scorable", "exclusion_reason"]

failures = []


def fail(did, msg):
    failures.append("%s: %s" % (did, msg))


def ok(did, msg):
    print("CHECK %s OK :: %s" % (did, msg))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def loadj(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def frac_eq(a, b):
    return Fraction(a["numerator"], a["denominator"]) == b


def independent_recompute(fx):
    n = len(fx["actual"])
    signed = [fx["forecast"][i] - fx["actual"][i] for i in range(n)]
    aerr = [abs(x) for x in signed]
    aerr_sum = sum(aerr)
    den = sum(abs(x) for x in fx["actual"])
    berr = [abs(fx["baseline"][i] - fx["actual"][i]) for i in range(n)]
    berr_sum = sum(berr)
    widths = [fx["high"][i] - fx["low"][i] for i in range(n)]
    return {
        "signed": signed, "aerr": aerr, "aerr_sum": aerr_sum, "den": den,
        "MAE": Fraction(aerr_sum, n), "WAPE": Fraction(aerr_sum, den),
        "Bias_U": Fraction(sum(signed), n), "NormalizedBias": Fraction(sum(signed), den),
        "berr": berr, "berr_sum": berr_sum,
        "skill": Fraction(1, 1) - Fraction(aerr_sum, berr_sum),
        "contained": [fx["low"][i] <= fx["actual"][i] <= fx["high"][i] for i in range(n)],
        "widths": widths, "mean_width": Fraction(sum(widths), n),
        "normalized_width": Fraction(sum(widths), den),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    args = ap.parse_args()
    root = args.root
    ev = os.path.join(root, "evidence", CARD)

    try:
        oracle = loadj(os.path.join(ev, "metric_oracle_result.json"))
        negs = loadj(os.path.join(ev, "metric_negative_results.json"))
        mbstr = loadj(os.path.join(ev, "metrics_by_stratum.json"))
        paired = loadj(os.path.join(ev, "paired_comparison.json"))
        interval = loadj(os.path.join(ev, "interval_diagnostics.json"))
        with open(os.path.join(PLAN_ROOT, "execution_v2", "research_cards.json"), "r", encoding="utf-8") as f:
            cards = json.load(f)
        with open(os.path.join(ev, "sample_errors.csv"), "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        with open(os.path.join(ev, "metric_reproduction.md"), "r", encoding="utf-8") as f:
            repro = f.read()
    except Exception as exc:
        print("HARNESS FAILURE (rc=1): %s" % exc)
        return 1

    # ---- D1 oracle result vs frozen fixture + independent recompute ----
    fx = cards["metric_numeric_oracle"]
    if oracle.get("synthetic") is not True:
        fail("D1", "synthetic must be true")
    if oracle.get("qualification") != "metric_implementation_only_not_accuracy_evidence":
        fail("D1", "qualification string must be the frozen one")
    if oracle.get("verdict") != "PASS_metric_implementation_qualified_only":
        fail("D1", "verdict must be PASS_metric_implementation_qualified_only")
    if oracle.get("all_expected_pass") is not True:
        fail("D1", "all_expected_pass must be true")
    comps = oracle.get("expected_comparisons") or {}
    if set(comps) != set(fx["expected"]):
        fail("D1", "expected_comparisons keys != fixture expected keys")
    for k, v in comps.items():
        if v.get("pass") is not True:
            fail("D1", "comparison %s not passed" % k)
    # independent recompute of the numbers themselves
    rc = independent_recompute(fx)
    comp = oracle.get("computed") or {}
    checks = [
        ("signed_errors", comp.get("signed_errors") == rc["signed"]),
        ("absolute_errors", comp.get("absolute_errors") == rc["aerr"]),
        ("absolute_error_sum", comp.get("absolute_error_sum") == rc["aerr_sum"]),
        ("MAE", comp.get("MAE", {}).get("defined") and frac_eq(comp["MAE"], rc["MAE"])),
        ("WAPE", comp.get("WAPE", {}).get("defined") and frac_eq(comp["WAPE"], rc["WAPE"])),
        ("Bias_U", comp.get("Bias_U", {}).get("defined") and frac_eq(comp["Bias_U"], rc["Bias_U"])),
        ("NormalizedBias", comp.get("NormalizedBias", {}).get("defined") and frac_eq(comp["NormalizedBias"], rc["NormalizedBias"])),
        ("baseline_absolute_errors", comp.get("baseline_absolute_errors") == rc["berr"]),
        ("baseline_absolute_error_sum", comp.get("baseline_absolute_error_sum") == rc["berr_sum"]),
        ("skill_vs_baseline", comp.get("skill_vs_baseline", {}).get("defined") and frac_eq(comp["skill_vs_baseline"], rc["skill"])),
        ("contained", comp.get("contained") == rc["contained"]),
        ("widths", comp.get("widths") == rc["widths"]),
        ("mean_width", comp.get("mean_width", {}).get("defined") and frac_eq(comp["mean_width"], rc["mean_width"])),
        ("normalized_width", comp.get("normalized_width", {}).get("defined") and frac_eq(comp["normalized_width"], rc["normalized_width"])),
    ]
    for name, good in checks:
        if not good:
            fail("D1", "independent recompute mismatch for %s" % name)
    sub = oracle.get("probabilistic_interval_subcase") or {}
    if sub.get("computed") is not False or sub.get("precondition_met") is not False:
        fail("D1", "probabilistic subcase must stay uncomputed (precondition unmet)")
    if oracle.get("fixture_source", {}).get("sha256") != "4a22e26608d421799e2b8adde0d0424fa48a634509a0559c51d279e06d918263":
        fail("D1", "fixture sha must match research_cards.json")
    if not failures:
        ok("D1", "oracle matches frozen fixture expectations AND independent rational recompute (14 metrics)")

    # ---- D2 negatives --------------------------------------------------
    if negs.get("frozen_negative_cases_count") != 3:
        fail("D2", "frozen_negative_cases_count must be 3")
    if negs.get("all_pass") is not True:
        fail("D2", "all_pass must be true")
    if negs.get("stop_triggered") is not False:
        fail("D2", "STOP_METRICS must not be triggered")
    cases = {c["case"]: c for c in negs.get("cases", [])}
    if set(cases) != {"N1_zero_denominator", "N2_sample_id_misalignment", "N3_baseline_loss_zero",
                      "E1_high_below_low", "E2_interval_score_gated"}:
        fail("D2", "case set mismatch: %s" % sorted(cases))
    for name, c in cases.items():
        if c.get("pass") is not True:
            fail("D2", "case %s not passed" % name)
    n1 = cases.get("N1_zero_denominator", {}).get("observed", {})
    if n1.get("WAPE", {}).get("defined") is not False or n1.get("WAPE", {}).get("reason") != "zero_denominator":
        fail("D2", "N1 WAPE must be undefined/zero_denominator")
    if n1.get("NormalizedBias", {}).get("reason") != "zero_denominator":
        fail("D2", "N1 NormalizedBias reason")
    if n1.get("normalized_width", {}).get("reason") != "zero_denominator":
        fail("D2", "N1 normalized_width reason")
    if n1.get("MAE", {}).get("defined") is not True:
        fail("D2", "N1 MAE must stay defined")
    if not (cases.get("N1_zero_denominator", {}).get("checks", {}).get("no_epsilon_used")):
        fail("D2", "N1 must show no epsilon used")
    n2 = cases.get("N2_sample_id_misalignment", {}).get("observed", {})
    if n2.get("status") != "rejected" or n2.get("reason") != "sample_id_misalignment":
        fail("D2", "N2 must be rejected for sample_id_misalignment")
    n3 = cases.get("N3_baseline_loss_zero", {}).get("observed", {})
    if n3.get("skill_vs_baseline", {}).get("defined") is not False:
        fail("D2", "N3 skill must be undefined")
    if not (cases.get("E2_interval_score_gated", {}).get("checks", {}).get("interval_score_rejected")):
        fail("D2", "E2 interval_score must be rejected")
    if not failures:
        ok("D2", "3 frozen negatives + 2 extended controls all pass; zero denominator undefined, no epsilon")

    # ---- D3 sample_errors.csv -----------------------------------------
    if len(rows) != 1:
        fail("D3", "sample_errors.csv must be header-only (0 data rows), got %d lines" % len(rows))
    header = rows[0] if rows else []
    for col in REQUIRED_CSV:
        if col not in header:
            fail("D3", "missing column %s" % col)
    if not failures:
        ok("D3", "sample_errors.csv header-only with full per-sample column structure (0 rows, no averages-only)")

    # ---- D4 metrics_by_stratum ----------------------------------------
    if mbstr.get("state") != "descriptive_only":
        fail("D4", "state must be descriptive_only")
    if mbstr.get("significance_claimed") is not False or mbstr.get("accuracy_improvement_claimed") is not False:
        fail("D4", "must not claim significance / accuracy improvement")
    cnt = mbstr.get("counts", {})
    if cnt.get("scorable_samples") != 0 or cnt.get("epsilon_substitutions") != 0:
        fail("D4", "counts must show scorable=0 and epsilon=0")
    if cnt.get("missing_pairs") != 7:
        fail("D4", "missing_pairs must be 7")
    for s in mbstr.get("strata", []):
        if s.get("n_scorable") != 0:
            fail("D4", "stratum %s n_scorable must be 0" % s.get("stratum_id"))
        if "n_companies" not in s or "n_origins" not in s:
            fail("D4", "stratum %s missing n_companies/n_origins" % s.get("stratum_id"))
        for m in ("MAE", "WAPE", "skill_vs_baseline"):
            if s.get("metrics", {}).get(m, {}).get("defined") is not False:
                fail("D4", "stratum %s metric %s must be undefined" % (s.get("stratum_id"), m))
    if not any(s.get("axis") == "industry" and s.get("unproven") for s in mbstr.get("strata", [])):
        fail("D4", "industry stratum must be marked unproven")
    if not any(s.get("axis") == "lifecycle" and s.get("unproven") for s in mbstr.get("strata", [])):
        fail("D4", "lifecycle stratum must be marked unproven")
    if not failures:
        ok("D4", "7 strata with n_companies/n_origins, all n_scorable=0, descriptive_only, no significance")

    # ---- D5 paired comparison -----------------------------------------
    if paired.get("n_pairs") != 0:
        fail("D5", "n_pairs must be 0")
    if paired.get("state") != "blocked_no_scorable_samples":
        fail("D5", "state must be blocked_no_scorable_samples")
    if paired.get("uncertainty_interval") is not None:
        fail("D5", "uncertainty_interval must be null")
    if paired.get("interval_method_not_approved") is not True:
        fail("D5", "interval_method_not_approved must be true")
    if paired.get("significance_claimed") is not False:
        fail("D5", "must not claim significance")
    if paired.get("cluster_unit") != "entity" or paired.get("block_unit") != "origin":
        fail("D5", "cluster/block units must stay entity/origin")
    if len(paired.get("interval_method_pending_items") or []) < 5:
        fail("D5", "must register >=5 pending method items")
    if not failures:
        ok("D5", "n_pairs=0, interval=null with >=5 unsigned items, cluster=entity/block=origin")

    # ---- D6 interval diagnostics ---------------------------------------
    if interval.get("probabilistic_claim_made") is not False:
        fail("D6", "probabilistic_claim_made must be false")
    if interval.get("interval_score", {}).get("enabled") is not False:
        fail("D6", "interval_score must be disabled (no nominal coverage)")
    if interval.get("pinball", {}).get("enabled") is not False:
        fail("D6", "pinball must be disabled")
    ci = interval.get("confidence_intervals", {})
    if ci.get("computed") is not False:
        fail("D6", "confidence intervals must not be computed while thresholds unsigned")
    if len(ci.get("pending_items") or []) < 5:
        fail("D6", "must register >=5 pending CI items")
    if ci.get("no_seed_fixed_by_implementer") is not True:
        fail("D6", "implementer must not fix a seed")
    if interval.get("n_scorable") != 0:
        fail("D6", "n_scorable must be 0")
    if not failures:
        ok("D6", "no probabilistic claim; interval_score/pinball disabled; CI unsigned (no seed picked)")

    # ---- D7 reproduction note -----------------------------------------
    for token in ("40/3", "40/300", "70/3", "descriptive_only",
                  "n=3只验证指标实现，不能证明模型准确性改善、覆盖校准或统计显著性。",
                  "sample_errors.csv"):
        if token not in repro:
            fail("D7", "metric_reproduction.md missing %r" % token)
    if not failures:
        ok("D7", "reproduction note carries hand arithmetic, rerun command and verbatim limitation")

    # ---- D8 redline / release / signature ------------------------------
    for dirpath, _d, files in os.walk(ev):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            for b in BANNED:
                if b in txt:
                    fail("D8", "OPEN-2 redline literal %r consumed in %s" % (b, os.path.relpath(p, root)))
    hp = os.path.join(root, "handoff.json")
    if os.path.exists(hp):
        ho = loadj(hp)
        if ho.get("params_released") is not False or ho.get("implementer_signed") is not False:
            fail("D8", "handoff params_released/implementer_signed must be false")
        if ho.get("open2_ban_observed") is not True:
            fail("D8", "handoff open2_ban_observed must be true")
    if not failures:
        ok("D8", "no OPEN-2 literal in evidence; no parameter released; no self-signature")

    # ---- D9 upstream + seal/store --------------------------------------
    mism = []
    for uid, rel, exp in UPSTREAM:
        p = os.path.join(PLAN_ROOT, rel.replace("/", os.sep))
        if not os.path.exists(p):
            mism.append("%s MISSING %s" % (uid, rel))
            continue
        got = sha256(p)
        if got != exp:
            mism.append("%s %s got %s expected %s" % (uid, rel, got, exp))
    if mism:
        for m in mism:
            fail("D9", m)
    seal_p = os.path.join(PLAN_ROOT, "execution_runs", "I-11-A", "a20260919-01", "evidence", "I-11-A", "hypotheses.json")
    store_p = os.path.join(PLAN_ROOT, "execution_runs", "OPEN2-C2-REGISTRATION", "a20260926-01", "hypotheses_v3.json")
    if sha256(seal_p) != UPSTREAM[16][2] or os.path.getsize(seal_p) != 51697:
        fail("D9", "sealed hypotheses changed")
    if sha256(store_p) != UPSTREAM[17][2] or os.path.getsize(store_p) != 61231:
        fail("D9", "store hypotheses_v3 changed")
    if not failures:
        ok("D9", "upstream 18/18 sha256 matched; sealed f2178768… / store b2063ac8… unchanged")

    # ---- D10 handoff shape ---------------------------------------------
    if os.path.exists(hp):
        ho = loadj(hp)
        for key, exp in (("status", "review_pending"), ("gate0_passed", True),
                         ("releases_nothing", True), ("git_diff_non_planning", 0)):
            if ho.get(key) != exp:
                fail("D10", "handoff.%s=%r expected %r" % (key, ho.get(key), exp))
        wf = ho.get("written_files", {})
        for ev_file in ("sample_errors.csv", "metrics_by_stratum.json", "paired_comparison.json",
                        "interval_diagnostics.json", "metric_reproduction.md",
                        "metric_oracle_result.json", "metric_negative_results.json"):
            if not any(ev_file in k for k in wf.keys()):
                fail("D10", "written_files missing %s" % ev_file)
        if not failures:
            ok("D10", "handoff shape OK (status=review_pending, gate0, releases_nothing, git_diff=0, 7 evidence)")
    else:
        print("CHECK D10 SKIP :: handoff.json not yet written (pre-finalization run)")

    if failures:
        for f_ in failures:
            print("FAIL %s" % f_)
        print("RESULT INVARIANT_VIOLATION count=%d" % len(failures))
        return 3
    print("RESULT ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
