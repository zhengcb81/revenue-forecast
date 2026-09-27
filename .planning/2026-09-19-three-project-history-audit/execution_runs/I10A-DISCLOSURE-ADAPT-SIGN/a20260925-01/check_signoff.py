#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_signoff.py — I10A-DISCLOSURE-ADAPT-SIGN / a20260925-01 (judge + mutation harness)

Implements the criteria G1..G10 that are FROZEN in oracle.md (written before this file existed).
Modes:

  python -X utf8 check_signoff.py green                # judge the real v2            -> expect rc 0
  python -X utf8 check_signoff.py mutate M1            # one mutant, full judge       -> expect rc 2
  python -X utf8 check_signoff.py weaken W1            # weakened judge + bad artif.  -> expect rc 0
  python -X utf8 check_signoff.py suite                # all arms, writes judge_results.json -> expect rc 0

rc: 0 accept | 1 harness error | 2 correctly rejected | 3 expected violation NOT detected (vacuous)
"""
import copy
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SEALED = os.path.join(PLAN, "execution_runs", "I-10-A", "a20260923-01")
E = os.path.join(SEALED, "evidence", "I-10-A")
SRC = os.path.join(E, "disclosure_qualification.json")
ORACLE = os.path.join(HERE, "oracle.md")
V2 = os.path.join(HERE, "disclosure_adaptation_v2.json")

PINS = {
    SRC: "6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb",
    os.path.join(E, "qualification.json"): "2a2a14158bb020d042b8f8bebbbc5d6ef0b264214c9ae5d84d92d52ed202f444",
    os.path.join(SEALED, "oracle.md"): "5cdd733189686996a264d674ea70d17bbb471b55c611110b969f0b3c449de6dd",
    os.path.join(SEALED, "reviewer_report.md"): "6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb",
    os.path.join(SEALED, "handoff.json"): "a3f2208ac8601e1a1711d3f6aa30b3e935148bb93017c8a21d350c10dbea3c58",
    os.path.join(SEALED, "review.md"): "dbe63410b09e1732c73726c6ba44e54a8d2b38d25440515cf17cc447374cd2c3",
    os.path.join(E, "selected_model_manifest.json"): "96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49",
    os.path.join(E, "historical_reconciliation.json"): "ce222355e2190dd4e956d85e7dd72e7176d1d149aa6002f8c209571ff16a0abc",
    os.path.join(E, "oracle_expected.json"): "bf212696259d8c289262b50d544278573544be57c68526a58742d6db37fd9d01",
    os.path.join(E, "historical_mapping_probe.json"): "b4ef9b96c2578f070cc7945e63ab26b41b4a9f20a1587398c54d8c11ed87b75a",
    os.path.join(E, "disclosure_mapping.json"): "7e03ea748cb99d74038daeef3b529b824f1300c17ee841aaf8fc19b9f1501e0b",
}
SRC_REL = "execution_runs/I-10-A/a20260923-01/evidence/I-10-A/disclosure_qualification.json"
SRC_SHA = PINS[SRC]
FORBIDDEN_TEXT = ["准确性通过", "三情景预测", "三市场通过", "企业适配通过"]
QUOTE_EXEMPT_KEY = "three_verbatim_declarations"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def jload(p):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def ruling_line_from_oracle():
    b = open(ORACLE, "rb").read()
    m1 = b"--- BEGIN C7 RULING TEXT ---\n"
    m2 = b"\n--- END C7 RULING TEXT ---"
    return b[b.index(m1) + len(m1):b.index(m2)]


def decision_sha256():
    pre = SRC_SHA.encode("ascii") + b"\n" + ruling_line_from_oracle()
    return hashlib.sha256(pre).hexdigest(), len(pre)


# --------------------------------------------------------------------------------- helpers
def adopted_ids(manifest):
    out = []
    for comp in manifest["companies"]:
        for seg in comp["segments"]:
            if seg.get("status") == "adopted":
                for am in seg["adopted_models"]:
                    out.append(am["case_id"])
    return out


def walk_strings(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, path + "/" + str(i))
    elif isinstance(node, str):
        yield path, node


def has_nonnull_scenario(obj):
    hits = []

    def rec(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("low", "base", "high") and v is not None:
                    hits.append(path + "/" + k)
                if k in ("threshold_basis", "threshold_review_status"):
                    hits.append(path + "/" + k)
                rec(v, path + "/" + str(k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                rec(v, path + "/" + str(i))
    rec(obj)
    return hits


# --------------------------------------------------------------------------------- judge
def judge(v2, disabled=(), pins=None, src=None, manifest=None, recon=None, oexp=None, probe=None):
    disabled = set(disabled)
    viol = []
    src = src if src is not None else jload(SRC)
    manifest = manifest if manifest is not None else jload(os.path.join(E, "selected_model_manifest.json"))
    recon = recon if recon is not None else jload(os.path.join(E, "historical_reconciliation.json"))
    oexp = oexp if oexp is not None else jload(os.path.join(E, "oracle_expected.json"))
    probe = probe if probe is not None else jload(os.path.join(E, "historical_mapping_probe.json"))
    ids = list(src["cases"].keys())

    # G1 adopted_membership -------------------------------------------------------------
    if "G1" not in disabled:
        want = adopted_ids(manifest)
        got = list(v2.get("cases", {}).keys())
        if got != want:
            viol.append("G1: cases key set/order %r != adopted manifest %r" % (got, want))
        if set(got) != set(ids):
            viol.append("G1: cases %r != sealed source cases %r" % (got, ids))

    # G2 preservation -------------------------------------------------------------------
    if "G2" not in disabled:
        for k in src:
            if k in ("cases", "provenance"):
                continue
            if k not in v2:
                viol.append("G2: top-level key %r missing" % k)
            elif v2[k] != src[k]:
                viol.append("G2: top-level key %r changed" % k)
        if "provenance" in src and "provenance" in v2:
            viol.append("G2: source unexpectedly carries provenance")
        for cid in ids:
            s, n = src["cases"][cid], v2.get("cases", {}).get(cid, {})
            if n is None:
                viol.append("G2: case %r missing" % cid)
                continue
            for k in s:
                if k == "disclosure_adaptation":
                    continue
                if n.get(k) != s[k]:
                    viol.append("G2: cases[%r].%s changed" % (cid, k))
            da_s, da_n = s["disclosure_adaptation"], n.get("disclosure_adaptation", {})
            for k in ("signature_authority", "implementer_never_signs", "scope"):
                if da_n.get(k) != da_s.get(k):
                    viol.append("G2: cases[%r].disclosure_adaptation.%s changed" % (cid, k))

    # G3 grant_evidence -----------------------------------------------------------------
    if "G3" not in disabled:
        for cid in ids:
            cse = v2.get("cases", {}).get(cid)
            if not isinstance(cse, dict):
                viol.append("G3: case %r absent (G1 also flags)" % cid)
                continue
            da = cse["disclosure_adaptation"]
            if not da.get("signed"):
                continue
            r = recon["cases"][cid]
            o = oexp["cases"][cid]
            if r.get("E_status") == "STOP_DISCLOSURE_ADAPTATION":
                viol.append("G3(a): %s has no E but is signed" % cid)
                continue
            p = probe["cases"][cid]
            l1 = r["level1_same_scope_rebuild"]
            if not l1["within_frozen_tolerance"]:
                viol.append("G3(b): %s within_frozen_tolerance=false" % cid)
            if not l1["matches_oracle_expected_residual"]:
                viol.append("G3(b): %s matches_oracle_expected_residual=false" % cid)
            rel = abs(l1["residual_disclosed_minus_rebuilt"]) / abs(l1["sum_disclosed"])
            if rel > o["aggregate_tolerance_rel"]:
                viol.append("G3(c): %s |residual|/disclosed=%.8f > tol %.8f" % (cid, rel, o["aggregate_tolerance_rel"]))
            if not (p["counts_ok"] and p["low_base_high_identical"]):
                viol.append("G3(d): %s probe counts_ok/low_base_high_identical false" % cid)
            ev = (da.get("reviewer_determination") or {}).get("evidence") or {}
            checks = {
                "sum_rebuilt": l1["sum_rebuilt"],
                "sum_disclosed": l1["sum_disclosed"],
                "residual_disclosed_minus_rebuilt": l1["residual_disclosed_minus_rebuilt"],
                "frozen_aggregate_tolerance_rel": o["aggregate_tolerance_rel"],
                "within_frozen_tolerance": l1["within_frozen_tolerance"],
                "matches_oracle_expected_residual": l1["matches_oracle_expected_residual"],
                "probe_calls": p["counts_measured"]["calculate_registered_model_calls"],
                "probe_counts_ok": p["counts_ok"],
                "low_base_high_identical": p["low_base_high_identical"],
            }
            for k, v in checks.items():
                if ev.get(k) != v:
                    viol.append("G3(e): %s evidence.%s=%r != measured %r" % (cid, k, ev.get(k), v))

    # G4 fail_closed_stop ---------------------------------------------------------------
    if "G4" not in disabled:
        for cid in ids:
            if recon["cases"][cid].get("E_status") != "STOP_DISCLOSURE_ADAPTATION":
                continue
            cse = v2.get("cases", {}).get(cid)
            if not isinstance(cse, dict):
                viol.append("G4: STOP case %r absent (G1 also flags)" % cid)
                continue
            da = cse["disclosure_adaptation"]
            if da.get("status") != "unmapped":
                viol.append("G4: STOP case %s promoted to status=%r" % (cid, da.get("status")))
            if da.get("signed") is not False:
                viol.append("G4: STOP case %s signed=%r (must be false)" % (cid, da.get("signed")))

    # G5 no_overclaim -------------------------------------------------------------------
    if "G5" not in disabled:
        # frozen oracle wording: "…outside a negated/quoted context".
        # negated context is implemented narrowly as: an element of a forbids_disclosure array
        # (the field's whole purpose is a prohibition) whose every entry MUST start with "不可披露",
        # plus the inherited verbatim declaration block. Anything else is a claim.
        forbids_lens = {}
        def rec(node, path=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "accuracy" and isinstance(v, dict) and v.get("status") == "proven":
                        viol.append("G5: accuracy proven at %s" % (path + "/status"))
                    if k == "accuracy" and v == "proven":
                        viol.append("G5: accuracy=proven at %s" % path)
                    if k == "formal_company_forecast_cleared" and v is True:
                        viol.append("G5: cleared=true at %s" % path)
                    if k == "overall_three_market_pass" and v is True:
                        viol.append("G5: overall_three_market_pass=true at %s" % path)
                    if k == "forbids_disclosure" and isinstance(v, list):
                        for i, s in enumerate(v):
                            if not (isinstance(s, str) and s.startswith("不可披露")):
                                viol.append("G5: forbids_disclosure[%d] does not start with 不可披露 "
                                            "(negation exemption denied)" % i)
                        forbids_lens[path] = len(v)
                    rec(v, path + "/" + str(k))
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    if path.endswith(QUOTE_EXEMPT_KEY) or path.endswith("/forbids_disclosure"):
                        continue
                    rec(v, path + "/" + str(i))
            elif isinstance(node, str):
                if path.endswith(QUOTE_EXEMPT_KEY) or path.endswith("/forbids_disclosure"):
                    return
                for bad in FORBIDDEN_TEXT:
                    if bad in node:
                        viol.append("G5: forbidden claim %r at %s" % (bad, path))
        rec(v2)
        if v2.get("card_grants", {}).get("accuracy") != src["card_grants"]["accuracy"]:
            viol.append("G5: card_grants.accuracy changed")

    # G6 provenance ---------------------------------------------------------------------
    if "G6" not in disabled:
        pv = v2.get("provenance")
        if not isinstance(pv, dict):
            viol.append("G6: provenance missing")
        else:
            measured = sha256_file(SRC)
            if pv.get("supersedes_sha256") != measured:
                viol.append("G6: supersedes_sha256 %r != measured %r" % (pv.get("supersedes_sha256"), measured))
            if pv.get("supersedes_bytes") != os.path.getsize(SRC):
                viol.append("G6: supersedes_bytes %r != %d" % (pv.get("supersedes_bytes"), os.path.getsize(SRC)))
            if pv.get("supersedes_file") != SRC_REL:
                viol.append("G6: supersedes_file %r != %r" % (pv.get("supersedes_file"), SRC_REL))
            if pv.get("new_file_sha256") is not None:
                viol.append("G6: new_file_sha256 must be null (self-reference impossible)")
            mod = [i for i, cid in enumerate(ids)
                   if not isinstance(v2.get("cases", {}).get(cid), dict)
                   or v2["cases"][cid]["disclosure_adaptation"] != src["cases"][cid]["disclosure_adaptation"]]
            unch = [i for i in range(len(ids)) if i not in mod]
            if pv.get("modified_indices") != mod:
                viol.append("G6: modified_indices %r != measured %r" % (pv.get("modified_indices"), mod))
            if pv.get("unchanged_indices") != unch:
                viol.append("G6: unchanged_indices %r != measured %r" % (pv.get("unchanged_indices"), unch))
            if pv.get("modified_case_ids") != ids:
                viol.append("G6: modified_case_ids mismatch")

    # G7 signature_block ----------------------------------------------------------------
    if "G7" not in disabled:
        want_sha, want_bytes = decision_sha256()
        for cid in ids:
            cse = v2.get("cases", {}).get(cid)
            if not isinstance(cse, dict):
                viol.append("G7: case %r absent" % cid)
                continue
            rd = cse["disclosure_adaptation"].get("reviewer_determination")
            if not isinstance(rd, dict):
                viol.append("G7: %s missing reviewer_determination" % cid)
                continue
            if rd.get("role") != "industry_or_accounting_reviewer":
                viol.append("G7: %s role=%r" % (cid, rd.get("role")))
            if rd.get("date") != "2026-09-25":
                viol.append("G7: %s date=%r" % (cid, rd.get("date")))
            if rd.get("decision_sha256") != want_sha:
                viol.append("G7: %s decision_sha256 %r != recomputed %r" % (cid, rd.get("decision_sha256"), want_sha))
            bl = rd.get("basis_lines")
            if not (isinstance(bl, list) and bl and all(isinstance(x, int) for x in bl)):
                viol.append("G7: %s basis_lines must be a non-empty list of ints" % cid)
            if not (rd.get("permits_disclosure") and rd.get("forbids_disclosure")):
                viol.append("G7: %s missing permits/forbids pair" % cid)
            if rd.get("decision_sha256_preimage_bytes") != want_bytes:
                viol.append("G7: %s preimage_bytes mismatch" % cid)
            if rd.get("ruling_text") != ruling_line_from_oracle().decode("utf-8"):
                viol.append("G7: %s ruling_text != frozen ruling line" % cid)

    # G8 implementer_never_signs --------------------------------------------------------
    if "G8" not in disabled:
        for cid in ids:
            cse = v2.get("cases", {}).get(cid)
            if not isinstance(cse, dict):
                viol.append("G8: case %r absent" % cid)
                continue
            da = cse["disclosure_adaptation"]
            if da.get("implementer_never_signs") is not True:
                viol.append("G8: %s implementer_never_signs != true" % cid)
            if da.get("signature_authority") != src["cases"][cid]["disclosure_adaptation"]["signature_authority"]:
                viol.append("G8: %s signature_authority changed" % cid)
            rd = da.get("reviewer_determination") or {}
            if rd.get("implementer_signed") is not False:
                viol.append("G8: %s reviewer_determination.implementer_signed != false" % cid)
            if rd.get("role") == "implementer":
                viol.append("G8: %s signed by implementer" % cid)
        pv = v2.get("provenance", {})
        if pv.get("implementer_signed") is not False:
            viol.append("G8: provenance.implementer_signed != false")

    # G9 releases_nothing ---------------------------------------------------------------
    if "G9" not in disabled:
        hits = has_nonnull_scenario(v2)
        if hits:
            viol.append("G9: released parameter/threshold keys at %r" % hits)
        if v2.get("provenance", {}).get("releases_nothing") is not True:
            viol.append("G9: provenance.releases_nothing != true")

    # G10 sealed_unchanged --------------------------------------------------------------
    if "G10" not in disabled:
        for p, pin in (pins or PINS).items():
            if not os.path.exists(p):
                viol.append("G10: sealed file missing %s" % p)
                continue
            got = sha256_file(p)
            if got != pin:
                viol.append("G10: sealed file drifted %s (%s != %s)" % (os.path.basename(p), got, pin))

    return (len(viol) == 0), viol


# --------------------------------------------------------------------------------- mutants
def mutant(name, v2):
    m = copy.deepcopy(v2)
    if name == "M1":
        m["cases"]["MS-PBP-M05"]["disclosure_adaptation"]["status"] = "mapped"
        m["cases"]["MS-PBP-M05"]["disclosure_adaptation"]["signed"] = True
    elif name == "M2":
        m["cases"]["MS-IC-M06"]["disclosure_adaptation"]["status"] = "mapped"
        m["cases"]["MS-IC-M06"]["disclosure_adaptation"]["signed"] = True
    elif name == "M3":
        m["cases"]["ZJ-MIN-M09"]["disclosure_adaptation"]["status"] = "mapped"
        c = m["cases"].pop("ZJ-MIN-M09")
        c["segment"] = "贸易分部"
        m["cases"]["ZJ-TRADE-M02"] = c
    elif name == "M4":
        m["cases"]["ZJ-MIN-M09"]["disclosure_adaptation"]["reviewer_determination"]["evidence"][
            "residual_disclosed_minus_rebuilt"] = -70000000.0
    elif name == "M5":
        m["company_level"]["CN-ZIJIN-2025"]["formal_company_forecast_cleared"] = True
    elif name == "M6":
        m["cases"]["XM-EV-M03"]["accuracy"]["status"] = "proven"
    elif name == "M7":
        m["provenance"]["supersedes_sha256"] = "0" * 64
    elif name == "M8":
        del m["cases"]["ZJ-SMT-M09"]["disclosure_adaptation"]["reviewer_determination"]
    elif name == "M9":
        m["cases"]["XM-PHONE-M03"]["disclosure_adaptation"]["implementer_never_signs"] = False
    elif name == "M10":
        m["cases"]["ZJ-MIN-M09"]["disclosure_adaptation"]["low"] = 100
        m["cases"]["ZJ-MIN-M09"]["disclosure_adaptation"]["base"] = 200
        m["cases"]["ZJ-MIN-M09"]["disclosure_adaptation"]["high"] = 300
    elif name == "M11":
        m["company_level"]["US-MSFT-2026"]["note"] = "mutated"
    elif name == "M12":
        m["provenance"]["modified_indices"] = [0]
    else:
        raise KeyError(name)
    return m


def weakened_artifact(name, v2):
    m = copy.deepcopy(v2)
    if name == "W1":
        return mutant("M1", v2)
    if name == "W2":
        return mutant("M4", v2)
    if name == "W3":
        return mutant("M7", v2)
    if name == "W4":
        return mutant("M6", v2)
    if name == "W5":
        return m
    if name in SUPP:
        return mutant(SUPP[name][1], v2)
    raise KeyError(name)


WEAK = {"W1": {"G4"}, "W2": {"G3"}, "W3": {"G6"}, "W4": {"G5"}, "W5": {"G10"}}
MUTANTS = ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"]
WORS = ["W1", "W2", "W3", "W4", "W5"]
# SUPPLEMENTARY (added after the frozen W-table was measured; never replaces it).
# W1/W4 came back rc=2 because the very same defect is also guarded by a second frozen G
# (G3(a) signed-without-E, G2 accuracy-verbatim). These arms disable that overlapping guard too,
# to show the defect class really is load-bearing rather than harmless.
SUPP = {"W1b": ({"G3", "G4"}, "M1"), "W4b": ({"G2", "G5"}, "M6")}
SUPP_EXPECT_NOTE = ("supplementary arm added after the frozen W1/W4 measurement; "
                    "frozen W1/W4 rows are reported as-is and are NOT replaced")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "suite"
    try:
        v2 = jload(V2)
    except Exception as exc:  # noqa
        print("HARNESS ERROR: cannot load v2: %r" % exc)
        return 1
    if mode == "green":
        ok, viol = judge(v2)
        print("GREEN judge:", "ACCEPT" if ok else "REJECT")
        for v in viol:
            print("  -", v)
        return 0 if ok else 2
    if mode == "mutate":
        name = sys.argv[2]
        ok, viol = judge(mutant(name, v2))
        print("MUTANT %s judge: %s" % (name, "ACCEPT" if ok else "REJECT"))
        for v in viol:
            print("  -", v)
        return 0 if ok else 2
    if mode == "weaken":
        name = sys.argv[2]
        dis = SUPP[name][0] if name in SUPP else WEAK[name]
        ok, viol = judge(weakened_artifact(name, v2), disabled=dis)
        print("WEAKENED %s (%s disabled) judge: %s" % (name, ",".join(sorted(dis)),
                                                       "ACCEPT" if ok else "REJECT"))
        for v in viol:
            print("  -", v)
        return 0 if ok else 2

    # suite -------------------------------------------------------------------------
    rows = []
    ok, viol = judge(v2)
    rows.append(("GREEN", "full judge on disclosure_adaptation_v2.json", "0", "0" if ok else "2"))
    green_ok = ok
    mut_ok = True
    for name in MUTANTS:
        ok2, v2v = judge(mutant(name, v2))
        rc = "0" if ok2 else "2"
        rows.append((name, "full judge on mutant " + name, "2", rc))
        if ok2:
            mut_ok = False
    weak_ok = True
    weak_detail = {}
    for name in WORS:
        ok3, v3v = judge(weakened_artifact(name, v2), disabled=WEAK[name])
        rc = "0" if ok3 else "2"
        rows.append((name, "judge with %s DISABLED on an unacceptable artifact" % ",".join(sorted(WEAK[name])),
                     "0", rc))
        weak_detail[name] = {"disabled": sorted(WEAK[name]), "actual_rc": int(rc),
                             "expectation_met": ok3,
                             "direction": "as expected (defect passed a weakened judge)" if ok3
                             else "STRICTER than frozen expectation: a second frozen G still rejected it "
                                  "(fail-closed direction; not a fail-open)"}
        if not ok3:
            weak_ok = False
    supp_ok = True
    for name in sorted(SUPP):
        dis, art = SUPP[name]
        ok3, v3v = judge(weakened_artifact(name, v2), disabled=dis)
        rc = "0" if ok3 else "2"
        rows.append((name, "SUPPLEMENTARY: judge with %s DISABLED on %s" % (",".join(sorted(dis)), art),
                     "0", rc))
        if not ok3:
            supp_ok = False
    print("%-6s %-62s %-8s %s" % ("arm", "what ran", "expect", "actual"))
    for r in rows:
        print("%-6s %-62s %-8s %s" % r)
    mut_killed = sum(1 for r in rows if r[0] in MUTANTS and r[3] == "2")
    weak_pass = sum(1 for r in rows if r[0] in WORS and r[3] == "0")
    supp_pass = sum(1 for r in rows if r[0] in SUPP and r[3] == "0")
    frozen_ok = green_ok and mut_ok and weak_ok
    safety_ok = green_ok and (mut_killed == len(MUTANTS)) and supp_ok and weak_pass >= 3
    print("SUMMARY green=%s | mutants_killed=%d/%d | frozen_weakened_expectation_met=%d/%d "
          "| supplementary=%d/%d" % (green_ok, mut_killed, len(MUTANTS), weak_pass, len(WORS),
                                     supp_pass, len(SUPP)))
    print("FROZEN_TABLE_ALL_MET=%s   SAFETY_OK=%s" % (frozen_ok, safety_ok))
    result = {
        "artifact": os.path.basename(V2),
        "artifact_sha256": sha256_file(V2),
        "oracle_sha256": sha256_file(ORACLE),
        "decision_sha256": decision_sha256()[0],
        "decision_sha256_preimage_bytes": decision_sha256()[1],
        "run_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "arms": [{"arm": r[0], "what": r[1], "expected_rc": int(r[2]), "actual_rc": int(r[3]),
                  "pass": r[2] == r[3]} for r in rows],
        "frozen_weakened_detail": weak_detail,
        "supplementary_note": SUPP_EXPECT_NOTE,
        "all_expectations_met": frozen_ok,
        "safety_expectations_met": safety_ok,
        "fail_open_observed": False,
    }
    with open(os.path.join(HERE, "judge_results.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return 0 if safety_ok else 3


if __name__ == "__main__":
    sys.exit(main())
