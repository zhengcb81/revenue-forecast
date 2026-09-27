#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-E read-only verifier. Exit codes (self-described exit_code_legend):
0 = all invariants E1..E10 OK; 1 = harness failure; 2 = no verdict (unused);
3 = named invariant violation. Usage: python _verify.py [--root <attempt_dir>]
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD = "I-12-E"

UPSTREAM = [
    ("U1", "execution_v2/card_I-12-E.md", "3c7d6da514dc9897bd7575a2e8e883bd9f883be89d1bdda6075d23a7f1ed497b"),
    ("U2", "execution_v2/card_I-12-D.md", "c6595cef4b3523c4fd4a879cd8f4106675130463f5573d09efb812fc6dbd4f69"),
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
    ("U12", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/exclusions.jsonl",
     "a4940267efc9683793baef0f52668e93b657c8c6ccd756b6349224e5275d3e93"),
    ("U13", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/forecast_manifest.json",
     "03cdb01c71b232b8797e2eedf1503d3d8b0b5407a6c93cf7cb9e0384da26922a"),
    ("U14", "execution_runs/I-12-C/a20260926-01/evidence/I-12-C/unblind_receipt.json",
     "99ed0139434a2777f4ede1454782fb83c60f315c3d83e00e1c8b175324e991f1"),
    ("U15", "execution_runs/I-12-D/a20260926-01/evidence/I-12-D/metric_oracle_result.json",
     "0d64d62e0f60df0a253bea58b9cb0841b0377198631cccdc7a0109e7366e83ca"),
    ("U16", "execution_runs/I-12-D/a20260926-01/evidence/I-12-D/metrics_by_stratum.json",
     "ad14f515bcb4f796bf063957a5a005f26b08babea312b94a6367de98b3392e2e"),
    ("U17", "execution_runs/I-12-D/a20260926-01/evidence/I-12-D/paired_comparison.json",
     "5709203bac2753c37fe6c56853f4f6d875d5149a1fd56edc993f275ce6e2e0d5"),
    ("U18", "execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json",
     "373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522"),
    ("U19", "execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md",
     "a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb"),
    ("U20", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"),
    ("U21", "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"),
]
BANNED = ["124248.63", "124,248.63", "38175.95"]
SCOPE_KEYS = ["dataset", "model_version", "industry", "lifecycle", "disclosure_quality", "horizon"]
TAX_CATS = ["data", "definition", "driver", "timing", "structure", "random"]
LIMIT_TOKENS = ["unproven", "inconclusive", "descriptive_only", "STOP_CLAIM", "STOP_RELEASE_WORDING",
                "小米", "生命周期", "微软", "n=0", "accuracy_improvement_claimed=false",
                "no_cross_column_pass_override=true"]
CLAIM_PHRASES = ["准确性已证明", "已证明准确率", "accuracy improved", "显著更准确", "准确率已提升"]

failures = []


def fail(eid, msg):
    failures.append("%s: %s" % (eid, msg))


def ok(eid, msg):
    print("CHECK %s OK :: %s" % (eid, msg))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def loadj(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    args = ap.parse_args()
    root = args.root
    ev = os.path.join(root, "evidence", CARD)

    try:
        qual = loadj(os.path.join(ev, "accuracy_qualification.json"))
        tax = loadj(os.path.join(ev, "error_taxonomy.json"))
        with open(os.path.join(ev, "limitations.md"), "r", encoding="utf-8") as f:
            lim = f.read()
        with open(os.path.join(ev, "independent_statistical_review.md"), "r", encoding="utf-8") as f:
            isr = f.read()
    except Exception as exc:
        print("HARNESS FAILURE (rc=1): %s" % exc)
        return 1

    # ---- E1 verdict discipline ----------------------------------------
    pr = qual.get("premise", {})
    if pr.get("thresholds_approved_before_results") is not False:
        fail("E1", "premise.thresholds_approved_before_results must be false")
    if pr.get("all_results_visible") is not False:
        fail("E1", "premise.all_results_visible must be false")
    if pr.get("met_count") != "0/2":
        fail("E1", "premise.met_count must be 0/2")
    if qual.get("threshold_state") != "unsigned":
        fail("E1", "threshold_state must be unsigned")
    if len(qual.get("thresholds_unsigned") or []) < 6:
        fail("E1", "must register >=6 unsigned threshold items")
    comps = qual.get("comparisons") or []
    if len(comps) != 6:
        fail("E1", "expected 6 pre-registered comparisons, got %d" % len(comps))
    for c in comps:
        if c.get("verdict") not in ("inconclusive",):
            fail("E1", "comparison %s verdict=%r must be inconclusive (thresholds unsigned)"
                 % (c.get("comparison_id"), c.get("verdict")))
        if c.get("threshold_state") != "unsigned":
            fail("E1", "comparison %s threshold_state must be unsigned" % c.get("comparison_id"))
        if c.get("verdict_is_fail_closed_default_not_professional_determination") is not True:
            fail("E1", "comparison %s must declare fail-closed default" % c.get("comparison_id"))
        if c.get("judge_authority") != "统计reviewer + 行业reviewer（not_assigned）":
            fail("E1", "comparison %s judge authority wrong" % c.get("comparison_id"))
        if "负 skill" not in str(c.get("negative_skill_rule", "")):
            fail("E1", "comparison %s must carry negative-skill preservation rule" % c.get("comparison_id"))
        if "失败层" not in str(c.get("failed_strata_rule", "")):
            fail("E1", "comparison %s must carry failed-strata preservation rule" % c.get("comparison_id"))
        if c.get("n_scorable") != 0:
            fail("E1", "comparison %s n_scorable must be 0" % c.get("comparison_id"))
    cc = qual.get("comparison_counts") or {}
    if cc.get("supported") != 0 or cc.get("unsupported") != 0 or cc.get("inconclusive") != len(comps):
        fail("E1", "comparison_counts must be supported=0/unsupported=0/inconclusive=%d" % len(comps))
    ja = qual.get("judge_authority", {})
    if ja.get("assigned") is not False or ja.get("implementer_did_not_determine") is not True:
        fail("E1", "judge authority must be unassigned and implementer must not determine")
    npres = qual.get("negative_and_failed_preservation", {})
    if npres.get("negative_skill_preserved_rule") is not True or npres.get("failed_strata_preserved_rule") is not True:
        fail("E1", "negative skill / failed strata preservation rules must be true")
    stops = qual.get("stops", {})
    if stops.get("STOP_CLAIM", {}).get("triggered") is not False:
        fail("E1", "STOP_CLAIM must be registered as not triggered")
    if stops.get("STOP_RELEASE_WORDING", {}).get("triggered") is not False:
        fail("E1", "STOP_RELEASE_WORDING must be registered as not triggered")
    if not failures:
        ok("E1", "premise 0/2 recorded; 6/6 comparisons inconclusive (fail-closed default, unsigned thresholds)")

    # ---- E2 scope limitation + uncovered strata ------------------------
    sl = qual.get("scope_limitation", {})
    for k in SCOPE_KEYS:
        if k not in sl:
            fail("E2", "scope_limitation missing key %s" % k)
    un = qual.get("uncovered_strata") or []
    if len(un) < 3:
        fail("E2", "need >=3 uncovered strata, got %d" % len(un))
    for u in un:
        if u.get("state") != "unproven":
            fail("E2", "uncovered stratum %s must be unproven" % u.get("stratum"))
    text = json.dumps(qual, ensure_ascii=False)
    if '"state": "proven"' in text or '"state":"proven"' in text:
        fail("E2", "no stratum may be marked proven")
    if not sl.get("no_generalization"):
        fail("E2", "no_generalization must be set")
    if not failures:
        ok("E2", "6 scope keys + %d uncovered strata all unproven + no generalization" % len(un))

    # ---- E3 three columns ---------------------------------------------
    tc = qual.get("three_column", {})
    for k in ("formula_qualification", "disclosure_adaptation", "accuracy"):
        if k not in tc:
            fail("E3", "three_column missing %s" % k)
    if tc.get("no_cross_column_pass_override") is not True:
        fail("E3", "no_cross_column_pass_override must be true")
    acc = tc.get("accuracy", {})
    if acc.get("state") != "unproven":
        fail("E3", "accuracy column state must be unproven")
    if tc.get("accuracy_improvement_claimed") is not False:
        fail("E3", "accuracy_improvement_claimed must be false")
    if tc.get("formula_qualification", {}).get("formula_pass_does_not_imply_accuracy") is not True:
        fail("E3", "formula pass must not imply accuracy")
    if tc.get("disclosure_adaptation", {}).get("disclosure_signing_does_not_imply_accuracy") is not True:
        fail("E3", "disclosure signing must not imply accuracy")
    if len(tc.get("override_examples_forbidden") or []) < 3:
        fail("E3", "must list >=3 forbidden override examples")
    if not failures:
        ok("E3", "three columns present, no cross-column PASS override, accuracy=unproven")

    # ---- E4 error taxonomy --------------------------------------------
    cats = tax.get("categories", {})
    for c in TAX_CATS:
        if c not in cats:
            fail("E4", "taxonomy missing category %s" % c)
        elif not cats[c]:
            fail("E4", "category %s has no items" % c)
        else:
            for it in cats[c]:
                if not it.get("source_ref"):
                    fail("E4", "item %s in %s lacks source_ref" % (it.get("id"), c))
    if tax.get("category_ids") != TAX_CATS:
        fail("E4", "category_ids must be the six frozen categories in order")
    qs = tax.get("follow_up_questions") or []
    if len(qs) < 3:
        fail("E4", "need >=3 follow-up questions, got %d" % len(qs))
    if tax.get("forecast_fixed_this_round") is not False:
        fail("E4", "forecast_fixed_this_round must be false")
    if tax.get("no_prediction_changes") is not True:
        fail("E4", "no_prediction_changes must be true")
    if not failures:
        ok("E4", "6 categories/%d items with source refs, %d follow-up questions, no forecast fix"
           % (sum(len(v) for v in cats.values()), len(qs)))

    # ---- E5 limitations -------------------------------------------------
    for t in LIMIT_TOKENS:
        if t not in lim:
            fail("E5", "limitations.md missing token %r" % t)
    for p in CLAIM_PHRASES:
        if p in lim:
            fail("E5", "limitations.md contains a positive accuracy claim: %r" % p)
    if not failures:
        ok("E5", "limitations carry scope gaps / negative results / uncertainty, no accuracy claim")

    # ---- E6 independent statistical review status -----------------------
    for t in ("false", "unsigned", "实现者不自签", "ACCEPT"):
        if t not in isr:
            fail("E6", "independent_statistical_review.md missing %r" % t)
    if "statistical_reviewer_assigned" not in isr:
        fail("E6", "must state statistical reviewer assignment status")
    if "不是复审意见" not in isr:
        fail("E6", "must declare the file is not a review opinion/signature")
    if not failures:
        ok("E6", "independent statistical review status recorded as unsigned/not-assigned, not a signature")

    # ---- E7 redline / release / signature -------------------------------
    for dirpath, _d, files in os.walk(ev):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            for b in BANNED:
                if b in txt:
                    fail("E7", "OPEN-2 redline literal %r consumed in %s" % (b, os.path.relpath(p, root)))
    hp = os.path.join(root, "handoff.json")
    if os.path.exists(hp):
        ho = loadj(hp)
        if ho.get("params_released") is not False or ho.get("implementer_signed") is not False:
            fail("E7", "handoff params_released/implementer_signed must be false")
        if ho.get("open2_ban_observed") is not True:
            fail("E7", "handoff open2_ban_observed must be true")
    if not failures:
        ok("E7", "no OPEN-2 literal in evidence; no parameter released; no self-signature")

    # ---- E8 upstream consistency ---------------------------------------
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
            fail("E8", m)
    else:
        ok("E8", "upstream 21/21 sha256 recomputed and matched")

    # ---- E9 seal / store ------------------------------------------------
    seal_p = os.path.join(PLAN_ROOT, "execution_runs", "I-11-A", "a20260919-01", "evidence", "I-11-A", "hypotheses.json")
    store_p = os.path.join(PLAN_ROOT, "execution_runs", "OPEN2-C2-REGISTRATION", "a20260926-01", "hypotheses_v3.json")
    if sha256(seal_p) != UPSTREAM[19][2] or os.path.getsize(seal_p) != 51697:
        fail("E9", "sealed hypotheses changed")
    if sha256(store_p) != UPSTREAM[20][2] or os.path.getsize(store_p) != 61231:
        fail("E9", "store hypotheses_v3 changed")
    if not failures:
        ok("E9", "sealed f2178768… 51,697B and store b2063ac8… 61,231B unchanged")

    # ---- E10 handoff shape ----------------------------------------------
    if os.path.exists(hp):
        ho = loadj(hp)
        for key, exp in (("status", "review_pending"), ("gate0_passed", True),
                         ("releases_nothing", True), ("git_diff_non_planning", 0)):
            if ho.get(key) != exp:
                fail("E10", "handoff.%s=%r expected %r" % (key, ho.get(key), exp))
        wf = ho.get("written_files", {})
        for ev_file in ("accuracy_qualification.json", "limitations.md", "error_taxonomy.json",
                        "independent_statistical_review.md"):
            if not any(ev_file in k for k in wf.keys()):
                fail("E10", "written_files missing %s" % ev_file)
        if not failures:
            ok("E10", "handoff shape OK (status=review_pending, gate0, releases_nothing, git_diff=0, 4 evidence)")
    else:
        print("CHECK E10 SKIP :: handoff.json not yet written (pre-finalization run)")

    if failures:
        for f_ in failures:
            print("FAIL %s" % f_)
        print("RESULT INVARIANT_VIOLATION count=%d" % len(failures))
        return 3
    print("RESULT ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
