#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-B read-only verifier. Exit codes (self-described exit_code_legend):
0 = all invariants J1..J9 OK; 1 = harness failure (missing/parse); 2 = no verdict (unused);
3 = named invariant violation (negative control correctly rejected).
Usage: python _verify.py [--root <attempt_dir>]
"""
import argparse
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

UPSTREAM = [
    ("U1", "execution_v2/card_I-12-B.md", "f61906a9900a9ddab8f32284937728bede34f95c219112dd3486c2bf9fae695b"),
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
    ("U11", "execution_runs/I-12-A/a20260926-01/handoff.json",
     "7bf747b15bf97032f75f9377a9c7bf1c2c023c54c272975cc8b30450ef11c714"),
    ("U12", "execution_runs/I-07-E/a20260926-01/calibration_validation_summary.md",
     "a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb"),
    ("U13", "execution_runs/I-07-E/a20260926-01/verification.json",
     "237bc2d394ec5726c05adc00f6b7de2b88e302aafe658300f64fbac5dd25671c"),
    ("U14", "execution_runs/I-07-E/a20260926-01/handoff.json",
     "8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04"),
    ("U15", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json",
     "3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf"),
    ("U16", "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"),
    ("U17", "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"),
]

BANNED = ["124248.63", "124,248.63", "38175.95"]
SID_RE = re.compile(r"^SMP-([A-Z]+-[A-Z]+)_([A-Z0-9]+)_(\d{8})_(FY\d{4})$")

failures = []


def fail(jid, msg):
    failures.append("%s: %s" % (jid, msg))


def ok(jid, msg):
    print("CHECK %s OK :: %s" % (jid, msg))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    args = ap.parse_args()
    root = args.root
    ev = os.path.join(root, "evidence", "I-12-B")

    try:
        manifest = read_jsonl(os.path.join(ev, "sample_manifest.jsonl"))
        excl = read_jsonl(os.path.join(ev, "exclusions.jsonl"))
        srcs = read_jsonl(os.path.join(ev, "source_vintages.jsonl"))
        with open(os.path.join(ev, "actuals_policy_application.json"), "r", encoding="utf-8") as f:
            actuals = json.load(f)
        with open(os.path.join(ev, "split_manifest.json"), "r", encoding="utf-8") as f:
            split = json.load(f)
    except Exception as exc:  # harness failure
        print("HARNESS FAILURE (rc=1): %s" % exc)
        return 1

    # ---- J1 sample_id uniqueness / derivation / count ------------------
    ids = [r.get("sample_id") for r in manifest]
    if len(manifest) != 7:
        fail("J1", "manifest lines=%d expected 7" % len(manifest))
    if len(set(ids)) != len(ids):
        fail("J1", "duplicate sample_id detected")
    for r in manifest:
        m = SID_RE.match(r.get("sample_id") or "")
        if not m:
            fail("J1", "malformed sample_id %r" % r.get("sample_id"))
            continue
        ent, seg, org, hor = m.group(1), m.group(2), m.group(3), m.group(4)
        if (r.get("entity"), r.get("segment_code")) != (ent, seg):
            fail("J1", "id/entity-segment mismatch %s" % r["sample_id"])
        if r.get("origin", "").replace("-", "") != org:
            fail("J1", "id/origin mismatch %s" % r["sample_id"])
        if r.get("horizon_fy") != hor:
            fail("J1", "id/horizon mismatch %s" % r["sample_id"])
        if not r.get("included", False):
            fail("J1", "non-included row inside sample_manifest %s" % r["sample_id"])
    if not failures:
        ok("J1", "7 unique sample_id, all derived from entity/segment/origin/horizon")

    # ---- J2 counting conservation -------------------------------------
    summary = [r for r in excl if r.get("record_type") == "conservation_summary"]
    row_exc = [r for r in excl if r.get("record_type") == "exclusion" and r.get("universe") == "row"]
    ent_exc = [r for r in excl if r.get("record_type") == "exclusion" and r.get("universe") == "entity"]
    if len(summary) != 1:
        fail("J2", "conservation_summary rows=%d expected 1" % len(summary))
    else:
        s = summary[0]
        checks = [
            ("entities_total", s.get("entities_total"), 3),
            ("entities_included", s.get("entities_included"), 2),
            ("entities_excluded", s.get("entities_excluded"), 1),
            ("candidate_rows", s.get("candidate_rows"), 9),
            ("included_rows", s.get("included_rows"), len(manifest)),
            ("excluded_rows", s.get("excluded_rows"), len(row_exc)),
            ("manifest_lines", s.get("manifest_lines"), len(manifest)),
            ("exclusion_row_lines", s.get("exclusion_row_lines"), len(row_exc)),
        ]
        for name, got, exp in checks:
            if got != exp:
                fail("J2", "%s=%r expected %r" % (name, got, exp))
        if s.get("entities_total") != s.get("entities_included") + s.get("entities_excluded"):
            fail("J2", "identity_1 broken")
        if s.get("candidate_rows") != s.get("included_rows") + s.get("excluded_rows"):
            fail("J2", "identity_2 broken")
        if s.get("candidate_rows") != s.get("manifest_lines") + s.get("excluded_rows"):
            fail("J2", "identity_2b broken (manifest vs candidate)")
        if "missing_count = 0" not in str(s.get("identity_3", "")):
            fail("J2", "identity_3 must declare missing_count = 0")
    if len(row_exc) != 2:
        fail("J2", "row-level exclusions=%d expected 2" % len(row_exc))
    if len(ent_exc) != 1:
        fail("J2", "entity-level exclusions=%d expected 1" % len(ent_exc))
    xm = [r for r in ent_exc if r.get("entity") == "HK-XIAOMI"]
    if not xm:
        fail("J2", "HK-XIAOMI entity exclusion missing")
    elif xm[0].get("reason_codes") != ["gap-U1 evidence_unreadable", "gap-U2 publish_date_unregistered"]:
        fail("J2", "Xiaomi reason_codes changed")
    if not failures:
        ok("J2", "conservation 3=2+1 / 9=7+2; Xiaomi exclusion intact")

    # ---- J3 available_at <= origin ------------------------------------
    for s in srcs:
        cls = s.get("class")
        if cls in ("information_input",):
            if s.get("available_at") is None:
                if s.get("state") != "quarantined_unavailable" or s.get("quarantine") is not True:
                    fail("J3", "source %s has null available_at but is not quarantined" % s.get("doc_id"))
                if s.get("used_by_samples"):
                    fail("J3", "quarantined source %s referenced by samples" % s.get("doc_id"))
                if s.get("check") != "fail":
                    fail("J3", "quarantined source %s check=%r expected fail" % (s.get("doc_id"), s.get("check")))
            else:
                if not (s.get("available_at") <= s.get("origin")):
                    fail("J3", "source %s available_at %s > origin %s" % (s.get("doc_id"), s.get("available_at"), s.get("origin")))
                if s.get("check", "").startswith("fail"):
                    fail("J3", "source %s check=fail but used" % s.get("doc_id"))
                if not s.get("available_at_le_origin"):
                    fail("J3", "source %s available_at_le_origin not true" % s.get("doc_id"))
        else:
            if not s.get("exemption_reason"):
                fail("J3", "non-information input %s lacks exemption_reason" % s.get("doc_id"))
    for r in manifest:
        if not r.get("available_at_le_origin"):
            fail("J3", "sample %s available_at_le_origin=false (future leakage form)" % r["sample_id"])
        if not (r.get("available_at") <= r.get("origin")):
            fail("J3", "sample %s available_at>origin" % r["sample_id"])
    if not failures:
        ok("J3", "available_at<=origin 7/7 + 2 inputs; Xiaomi quarantined; protocol inputs exempted with reason")

    # ---- J4 vintage separation ----------------------------------------
    bad = [r["sample_id"] for r in manifest if r.get("vintage_class") != "true_vintage"]
    if bad:
        fail("J4", "non-true_vintage rows: %s" % bad)
    recon = [r["sample_id"] for r in manifest if r.get("vintage_class") == "reconstructed"]
    if recon:
        fail("J4", "reconstructed rows mixed into primary pool: %s" % recon)
    if not failures:
        ok("J4", "7/7 true_vintage; reconstructed=0 (no merge)")

    # ---- J5 sealing / split -------------------------------------------
    for r in manifest:
        if r.get("actual_value") is not None:
            fail("J5", "target actual present for %s" % r["sample_id"])
        if r.get("scorable") is not False:
            fail("J5", "scorable!=false for %s" % r["sample_id"])
    seal = actuals.get("sealing", {})
    if seal.get("target_period_actuals_seen_by_this_station") is not False:
        fail("J5", "target_period_actuals_seen_by_this_station must be false")
    if seal.get("unseal_gate_currently_satisfied") is not False:
        fail("J5", "unseal_gate_currently_satisfied must be false")
    if seal.get("test_results_unsealed") is not False or seal.get("accuracy_results_read") is not False:
        fail("J5", "test results must stay sealed / unread")
    if actuals.get("counts", {}).get("scorable_samples") != 0:
        fail("J5", "scorable_samples must be 0")
    for hz in actuals.get("application_per_sample", []):
        if hz.get("horizon_elapsed") is not False or hz.get("actual_value") is not None:
            fail("J5", "horizon row not fail-closed: %s" % hz.get("sample_id"))
    if actuals.get("stop_registration", {}).get("limited", {}).get("triggered") is not True:
        fail("J5", "limited stop not recorded")
    if actuals.get("stop_registration", {}).get("STOP_DATASET", {}).get("triggered") is not False:
        fail("J5", "STOP_DATASET must not be triggered")
    if split.get("design_field_status") != "PENDING" or split.get("state") != "PENDING_unsigned_split_not_assigned":
        fail("J5", "split must stay PENDING_unsigned")
    counts = split.get("counts", {})
    for k in ("train", "tune", "validation", "final_test"):
        if counts.get(k) != 0:
            fail("J5", "split %s=%r expected 0 (no self-chosen cut)" % (k, counts.get(k)))
    if counts.get("unassigned") != len(manifest):
        fail("J5", "unassigned %r != manifest %d" % (counts.get("unassigned"), len(manifest)))
    if not failures:
        ok("J5", "actuals sealed/zero, gate unsatisfied, split PENDING with 0 assignments")

    # ---- J6 redline / release / signature ------------------------------
    for dirpath, _dirs, files in os.walk(ev):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            for b in BANNED:
                if b in txt:
                    fail("J6", "OPEN-2 redline literal %r consumed in evidence file %s" % (b, os.path.relpath(p, root)))
    hp = os.path.join(root, "handoff.json")
    if os.path.exists(hp):
        with open(hp, "r", encoding="utf-8") as f:
            ho = json.load(f)
        if ho.get("params_released") is not False:
            fail("J6", "handoff.params_released must be false")
        if ho.get("implementer_signed") is not False:
            fail("J6", "handoff.implementer_signed must be false")
        if ho.get("open2_ban_observed") is not True:
            fail("J6", "handoff.open2_ban_observed must be true")
    if not failures:
        ok("J6", "no OPEN-2 literal in evidence; params_released=false; implementer_signed=false")

    # ---- J7 upstream consistency --------------------------------------
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
            fail("J7", m)
    else:
        ok("J7", "upstream 17/17 sha256 recomputed and matched")

    # ---- J8 seal / store zero byte ------------------------------------
    seal_p = os.path.join(PLAN_ROOT, "execution_runs", "I-11-A", "a20260919-01", "evidence", "I-11-A", "hypotheses.json")
    store_p = os.path.join(PLAN_ROOT, "execution_runs", "OPEN2-C2-REGISTRATION", "a20260926-01", "hypotheses_v3.json")
    if sha256(seal_p) != UPSTREAM[15][2] or os.path.getsize(seal_p) != 51697:
        fail("J8", "sealed hypotheses changed")
    if sha256(store_p) != UPSTREAM[16][2] or os.path.getsize(store_p) != 61231:
        fail("J8", "store hypotheses_v3 changed")
    if not failures:
        ok("J8", "sealed f2178768… 51,697B and store b2063ac8… 61,231B unchanged")

    # ---- J9 handoff shape ---------------------------------------------
    if os.path.exists(hp):
        with open(hp, "r", encoding="utf-8") as f:
            ho = json.load(f)
        for key, exp in (("status", "review_pending"), ("gate0_passed", True),
                         ("releases_nothing", True), ("git_diff_non_planning", 0)):
            if ho.get(key) != exp:
                fail("J9", "handoff.%s=%r expected %r" % (key, ho.get(key), exp))
        wf = ho.get("written_files", {})
        for ev_file in ("sample_manifest.jsonl", "exclusions.jsonl", "source_vintages.jsonl",
                        "actuals_policy_application.json", "split_manifest.json"):
            if not any(ev_file in k for k in wf.keys()):
                fail("J9", "written_files missing %s" % ev_file)
        if not failures:
            ok("J9", "handoff shape OK (status=review_pending, gate0, releases_nothing, git_diff=0)")
    else:
        print("CHECK J9 SKIP :: handoff.json not yet written (pre-finalization run)")

    if failures:
        for f_ in failures:
            print("FAIL %s" % f_)
        print("RESULT INVARIANT_VIOLATION count=%d" % len(failures))
        return 3
    print("RESULT ALL_INVARIANTS_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
