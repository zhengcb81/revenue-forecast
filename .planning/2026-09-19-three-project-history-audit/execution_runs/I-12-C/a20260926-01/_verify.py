#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-C read-only verifier. Exit codes (self-described exit_code_legend):
0 = all invariants K1..K9 OK; 1 = harness failure; 2 = no verdict (unused);
3 = named invariant violation. Usage: python _verify.py [--root <attempt_dir>]
"""
import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD = "I-12-C"

UPSTREAM = [
    ("U1", "execution_v2/card_I-12-C.md", "49dbb572c7fc996721c1f096fc1743df67974c9020c4faf226a123929d0a6d91"),
    ("U2", "execution_v2/card_I-12-B.md", "f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b"),
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
    ("U13", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/source_vintages.jsonl",
     "9f9d263f535e5bf3b421f2e0242eb853012708a243503edd4e64daf1529b6e56"),
    ("U14", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/actuals_policy_application.json",
     "998823537e8f493545562a05b1e0308f1865b0231ddb44b1bfc9fee5a7ac3942"),
    ("U15", "execution_runs/I-12-B/a20260926-01/evidence/I-12-B/split_manifest.json",
     "3a42cc85ce71ec4eb9aa5595948237e7ea3d62fdc6d3844c2e7bab05d11eddb7"),
    ("U16", "execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/disclosure_adaptation_v2.json",
     "373c162197203da31d68b4273adb27d5c2ba68936bcdf4100e669c23fea9d522"),
    ("U17", "execution_runs/I-10-A/a20260923-01/evidence/I-10-A/disclosure_qualification.json",
     "6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb"),
    ("U18", "execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md",
     "a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb"),
    ("U19", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json",
     "3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf"),
    ("U20", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"),
    ("U21", "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"),
]

BANNED = ["124248.63", "124,248.63", "38175.95"]

BASE = {  # (entity, segment) -> (base_value, prev_value, h)
    ("CN-ZIJIN", "MINERAL"): (109977556345, 74089365354, 2),
    ("CN-ZIJIN", "SMELT"): (165858644874, 181141823725, 2),
    ("CN-ZIJIN", "TRADE"): (29212610830, 29386475085, 2),
    ("CN-ZIJIN", "OTHER"): (44030270803, 19022292989, 2),
    ("US-MSFT", "PBP"): (139996, 120810, 1),
    ("US-MSFT", "IC"): (137791, 106265, 1),
    ("US-MSFT", "MPC"): (54052, 54649, 1),
}

failures = []


def fail(kid, msg):
    failures.append("%s: %s" % (kid, msg))


def ok(kid, msg):
    print("CHECK %s OK :: %s" % (kid, msg))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_jsonl(p):
    rows = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load(p, store, key, kid):
    try:
        with open(p, "r", encoding="utf-8") as f:
            store[key] = json.load(f)
        return True
    except Exception as exc:
        fail(kid, "cannot read %s: %s" % (os.path.basename(p), exc))
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    args = ap.parse_args()
    root = args.root
    ev = os.path.join(root, "evidence", CARD)

    try:
        fv = read_jsonl(os.path.join(ev, "forecast_vintages.jsonl"))
        bv = read_jsonl(os.path.join(ev, "baseline_vintages.jsonl"))
        up = read_jsonl(os.path.join(PLAN_ROOT, "execution_runs", "I-12-B", "a20260926-01",
                                     "evidence", "I-12-B", "sample_manifest.jsonl"))
    except Exception as exc:
        print("HARNESS FAILURE (rc=1): %s" % exc)
        return 1
    objs = {}
    for name, kid in (("forecast_manifest.json", "K3"), ("unblind_receipt.json", "K4")):
        if not load(os.path.join(ev, name), objs, name, kid):
            print("HARNESS FAILURE (rc=1)")
            return 1
    man = objs["forecast_manifest.json"]
    rec = objs["unblind_receipt.json"]

    up_ids = [r["sample_id"] for r in up]

    # ---- K1 forecast freeze surface -----------------------------------
    if len(fv) != 7:
        fail("K1", "forecast_vintages rows=%d expected 7" % len(fv))
    if [r.get("sample_id") for r in fv] != up_ids:
        fail("K1", "forecast sample_ids not aligned with upstream B manifest")
    for r in fv:
        fc = r.get("forecast") or {}
        if any(fc.get(k) is not None for k in ("low", "base", "high")):
            fail("K1", "forecast value present for %s while params_released=false" % r.get("sample_id"))
        if r.get("forecast_value_state") != "not_produced_params_not_released":
            fail("K1", "forecast_value_state wrong for %s" % r.get("sample_id"))
        if "params_released=false" not in str(r.get("reason", "")):
            fail("K1", "reason must state params_released=false for %s" % r.get("sample_id"))
        if r.get("model_version") is not None:
            fail("K1", "model_version must be null for %s" % r.get("sample_id"))
        if r.get("scorable") is not False:
            fail("K1", "scorable must be false for %s" % r.get("sample_id"))
        if r.get("reconstructed") is not False:
            fail("K1", "reconstructed must be false for %s" % r.get("sample_id"))
    if not failures:
        ok("K1", "7/7 null forecasts with params_released=false reason; no model_version; not scorable")

    # ---- K2 baselines --------------------------------------------------
    prim = [r for r in bv if r.get("kind") == "primary_baseline"]
    sec = [r for r in bv if r.get("kind") == "secondary_baseline"]
    if len(prim) != 7 or len(sec) != 7 or len(bv) != 14:
        fail("K2", "baseline rows primary=%d secondary=%d total=%d expected 7/7/14" % (len(prim), len(sec), len(bv)))
    seen = {}
    for r in bv:
        sid = r.get("sample_id")
        seen.setdefault((sid, r.get("kind")), 0)
        seen[(sid, r.get("kind"))] += 1
        if r.get("is_released_parameter") is not False:
            fail("K2", "is_released_parameter must be false for %s" % r.get("baseline_id"))
        if r.get("params_released") is not False:
            fail("K2", "params_released must be false for %s" % r.get("baseline_id"))
        if r.get("available_at_le_origin") is not True:
            fail("K2", "%s fails available_at<=origin" % r.get("baseline_id"))
        if r.get("future_information_used") is not False:
            fail("K2", "%s declares future information" % r.get("baseline_id"))
    for sid in up_ids:
        if seen.get((sid, "primary_baseline"), 0) != 1:
            fail("K2", "primary baseline count wrong for %s" % sid)
        if seen.get((sid, "secondary_baseline"), 0) != 1:
            fail("K2", "secondary baseline count wrong for %s" % sid)
    for r in prim:
        sid = r["sample_id"]
        s = next(x for x in up if x["sample_id"] == sid)
        key = (s["entity"], s["segment_code"])
        exp = BASE.get(key)
        if exp is None:
            fail("K2", "no frozen base value for %s" % str(key))
            continue
        if r.get("value") != exp[0]:
            fail("K2", "primary value for %s = %r expected %r" % (sid, r.get("value"), exp[0]))
        if r.get("base_period") not in ("FY2025", "FY2026"):
            fail("K2", "base_period unexpected for %s" % sid)
    for r in sec:
        sid = r["sample_id"]
        s = next(x for x in up if x["sample_id"] == sid)
        key = (s["entity"], s["segment_code"])
        exp = BASE.get(key)
        if exp is None:
            continue
        b, p, h = exp
        want = Fraction(b, 1) * (Fraction(b, p) ** h)
        got = r.get("value_exact") or {}
        if got.get("numerator") != want.numerator or got.get("denominator") != want.denominator:
            fail("K2", "secondary exact value wrong for %s: %r expected %d/%d"
                 % (sid, got, want.numerator, want.denominator))
        fi = r.get("formula_inputs") or {}
        if fi.get("h") != h or fi.get("R_base") != b or fi.get("R_prev") != p:
            fail("K2", "formula_inputs wrong for %s" % sid)
    seas = (man.get("baselines") or {}).get("seasonal_same_quarter") or {}
    if seas.get("state") != "not_applicable":
        fail("K2", "seasonal_same_quarter must be not_applicable")
    if not failures:
        ok("K2", "14 baselines (7 primary exact + 7 secondary rational); seasonal not_applicable; no released parameter")

    # ---- K3 forecast manifest -----------------------------------------
    if man.get("freeze_before_unblind") is not True:
        fail("K3", "freeze_before_unblind must be true")
    if man.get("actuals_read_by_this_station") is not False or man.get("target_period_actuals_read") is not False:
        fail("K3", "actuals must be unread by this station")
    if man.get("low_high_semantics") != "scenario_band_not_probabilistic":
        fail("K3", "low/high semantics must stay scenario band")
    if man.get("version") != "v1":
        fail("K3", "manifest version must be v1")
    if (man.get("rerun_policy") or {}).get("reruns_performed") != 0:
        fail("K3", "reruns_performed must be 0")
    ih = man.get("input_hashes") or {}
    for name in ("forecast_vintages.jsonl", "baseline_vintages.jsonl"):
        p = os.path.join(ev, name)
        if ih.get("evidence/%s/%s" % (CARD, name)) != sha256(p):
            fail("K3", "input_hashes mismatch for %s" % name)
    qc = man.get("disclosure_qualification_counts") or {}
    if qc != {"signed": 2, "stop": 2, "uncovered": 3}:
        fail("K3", "disclosure_qualification_counts=%r expected {2,2,3}" % qc)
    cnt = man.get("counts") or {}
    if cnt.get("forecast_values_frozen") != 0 or cnt.get("scorable_samples") != 0:
        fail("K3", "counts must show 0 forecast values / 0 scorable")
    if (man.get("stop_registration") or {}).get("stop_2_model_adaptation", {}).get("triggered") is not True:
        fail("K3", "STOP_MODEL_ADAPTATION must be registered as triggered (MSFT)")
    if (man.get("stop_registration") or {}).get("stop_1_ordering", {}).get("triggered") is not False:
        fail("K3", "stop_1 (ordering) must not be triggered")
    if not failures:
        ok("K3", "manifest frozen v1 before unblind; input hashes match; qual 2/2/3; STOP registrations correct")

    # ---- K4 unblind receipt -------------------------------------------
    if rec.get("issued") is not False or rec.get("issued_by") is not None:
        fail("K4", "receipt must be unissued and issued_by null (implementer must not issue)")
    if rec.get("this_station_cannot_issue") is not True:
        fail("K4", "this_station_cannot_issue must be true")
    if len(rec.get("preconditions_unmet") or []) < 4:
        fail("K4", "preconditions_unmet must list >=4 unmet conditions")
    if (rec.get("sample_scope") or {}).get("scorable_samples") != 0:
        fail("K4", "scorable_samples must be 0")
    if (rec.get("exposure") or {}).get("target_period_actuals_seen") is not False:
        fail("K4", "exposure.target_period_actuals_seen must be false")
    if rec.get("state") != "not_issued":
        fail("K4", "state must be not_issued")
    fm = rec.get("forecast_manifest") or {}
    if fm.get("sha256") != sha256(os.path.join(ev, "forecast_manifest.json")):
        fail("K4", "receipt->manifest sha mismatch")
    if not failures:
        ok("K4", "unblind receipt not issued by this station; >=4 unmet preconditions; manifest sha chained")

    # ---- K5 redline / release / signature ------------------------------
    for dirpath, _d, files in os.walk(ev):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            for b in BANNED:
                if b in txt:
                    fail("K5", "OPEN-2 redline literal %r consumed in %s" % (b, os.path.relpath(p, root)))
    decl = man.get("declarations") or {}
    if decl.get("params_released") is not False or decl.get("implementer_signed") is not False:
        fail("K5", "manifest declarations must keep params_released=false / implementer_signed=false")
    if decl.get("open2_ban_observed") is not True:
        fail("K5", "open2_ban_observed must be true")
    hp = os.path.join(root, "handoff.json")
    if os.path.exists(hp):
        with open(hp, "r", encoding="utf-8") as f:
            ho = json.load(f)
        if ho.get("params_released") is not False or ho.get("implementer_signed") is not False:
            fail("K5", "handoff params_released/implementer_signed must be false")
        if ho.get("open2_ban_observed") is not True:
            fail("K5", "handoff open2_ban_observed must be true")
    if not failures:
        ok("K5", "no OPEN-2 literal in evidence; no parameter released; no self-signature")

    # ---- K6 upstream consistency --------------------------------------
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
            fail("K6", m)
    else:
        ok("K6", "upstream 21/21 sha256 recomputed and matched")

    # ---- K7 seal / store ----------------------------------------------
    seal_p = os.path.join(PLAN_ROOT, "execution_runs", "I-11-A", "a20260919-01", "evidence", "I-11-A", "hypotheses.json")
    store_p = os.path.join(PLAN_ROOT, "execution_runs", "OPEN2-C2-REGISTRATION", "a20260926-01", "hypotheses_v3.json")
    if sha256(seal_p) != UPSTREAM[19][2] or os.path.getsize(seal_p) != 51697:
        fail("K7", "sealed hypotheses changed")
    if sha256(store_p) != UPSTREAM[20][2] or os.path.getsize(store_p) != 61231:
        fail("K7", "store hypotheses_v3 changed")
    if not failures:
        ok("K7", "sealed f2178768… 51,697B and store b2063ac8… 61,231B unchanged")

    # ---- K8 run logs ---------------------------------------------------
    rl_p = os.path.join(ev, "run_logs.json")
    if os.path.exists(rl_p):
        with open(rl_p, "r", encoding="utf-8") as f:
            rl = json.load(f)
        if rl.get("model_runs") != []:
            fail("K8", "model_runs must be [] (no bound model command)")
        if not rl.get("model_run_reason"):
            fail("K8", "model_run_reason missing")
        if rl.get("network_used") is not False or rl.get("git_used") is not False:
            fail("K8", "network_used/git_used must be false")
        for c in rl.get("commands", []):
            wd = str(c.get("cwd", ""))
            if not wd.replace("/", "\\").endswith("I-12-C\\a20260926-01") and \
               not wd.replace("/", "\\").endswith("I-12-C/a20260926-01"):
                fail("K8", "command %s cwd outside attempt dir: %s" % (c.get("id"), wd))
        if not failures:
            ok("K8", "run_logs: 0 model runs, commands confined to attempt dir, no network/git")
    else:
        print("CHECK K8 SKIP :: run_logs.json not yet written (pre-finalization run)")

    # ---- K9 handoff shape ---------------------------------------------
    if os.path.exists(hp):
        with open(hp, "r", encoding="utf-8") as f:
            ho = json.load(f)
        for key, exp in (("status", "review_pending"), ("gate0_passed", True),
                         ("releases_nothing", True), ("git_diff_non_planning", 0)):
            if ho.get(key) != exp:
                fail("K9", "handoff.%s=%r expected %r" % (key, ho.get(key), exp))
        wf = ho.get("written_files", {})
        for ev_file in ("forecast_vintages.jsonl", "baseline_vintages.jsonl", "forecast_manifest.json",
                        "run_logs.json", "unblind_receipt.json"):
            if not any(ev_file in k for k in wf.keys()):
                fail("K9", "written_files missing %s" % ev_file)
        if not failures:
            ok("K9", "handoff shape OK (status=review_pending, gate0, releases_nothing, git_diff=0)")
    else:
        print("CHECK K9 SKIP :: handoff.json not yet written (pre-finalization run)")

    if failures:
        for f_ in failures:
            print("FAIL %s" % f_)
        print("RESULT INVARIANT_VIOLATION count=%d" % len(failures))
        return 3
    print("RESULT ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
