"""BLOCKED6C oracle section 6: the L271 counterexample monitor (read-only).

Quantifies how many historical thresholds the BLOCKED-6c patch would judge
UNUSABLE, under two frozen readings (U-PRIMARY, the card's main rule, and
U-LITERAL, the A-6.1 literal counterfactual), at record level and at
de-duplicated-underlying level, and evaluates the three frozen trigger lines
T1 / T2 / T3. Any trigger hit under U-PRIMARY => L271_trigger_fired = true.

Nothing here writes to any corpus file; every input is opened read-only and its
sha256 is checked against the frozen table in oracle.md section 1.

Usage:
  python -X utf8 -B tools/l271_monitor.py --planning-root <dir> --out <json>
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (id, relative path under planning root, sha256 from oracle.md section 1)
CORPUS = [
    ("v1_hypotheses",
     "execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28"),
    ("v2_hypotheses",
     "execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json",
     "32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859"),
    ("v3_hypotheses",
     "execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff"),
    ("v4_hypotheses",
     "execution_runs/HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json",
     "ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654"),
    ("tolerance_table",
     "execution_runs/OPEN6-TOLERANCE-TABLE/a20260925-01/tolerance_table.json",
     "1da977bfe05e23545363f123bb1f00e1b21e153849173e5ec9ed9bd8ec315573"),
    ("tolerance_signed",
     "execution_runs/OPEN6B-TOLERANCE-RULING/a20260926-01/tolerance_signed.json",
     "3ad403ba75cf545721b0ba4fa32345d5ecae00c1802e4ca39feb5f19d5f747e8"),
]

HYP_FILES = {"v1_hypotheses", "v2_hypotheses", "v3_hypotheses", "v4_hypotheses"}

A62_USABLE_BASES = {"arithmetic_identity", "disclosure_definition"}


def load_patched():
    path = os.path.join(RUN, "iso_patched", "tools", "validate_hypotheses.py")
    spec = importlib.util.spec_from_file_location("vh_patched_l271", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def as_record(mod, cid, item, kind):
    """Normalise any corpus item to the hypothesis shape the patch judges."""
    if kind == "hypothesis":
        return item
    # tolerance row / signed threshold: only the threshold-bearing fields matter
    return {
        "hypothesis_id": item.get("threshold_id") or item.get("row_id"),
        "state": item.get("hypothesis_state"),
        "reviewer": item.get("reviewer"),
        "decision": item.get("decision"),
        "falsifier": {
            "threshold_basis": item.get("threshold_basis"),
            "threshold_review_status": item.get("threshold_review_status"),
        } if "threshold_review_status" in item else {
            "threshold_basis": item.get("threshold_basis"),
        },
        "_source_kind": kind,
    }


def judge(mod, h):
    """U-PRIMARY (oracle 3.3) PLUS the host-document union (B6C-G1/G2/G3).

    This is exactly `threshold_reviewability()` from the patched validator: the
    four U-PRIMARY reasons plus `approved_without_review`, which is the B6C-G3
    host rejection, and `unknown_status`/`reviewed_unsealed`, which are the
    B6C-G1/B6C-G2 host rejections. One function, one union, no double counting.
    """
    r = dict(mod.threshold_reviewability(h))
    fz = h.get("falsifier", {}) or {}
    present, raw, eff = mod.threshold_review_status_of(fz)
    basis = fz.get("threshold_basis")
    literal_reasons = []
    if eff != "reviewed":
        literal_reasons.append("literal_not_reviewed")
    if present and raw not in mod.THRESHOLD_REVIEW_STATUSES:
        literal_reasons.append("unknown_status")
    if basis not in mod.THRESHOLD_BASES:
        literal_reasons.append("unknown_basis")
    r["literal_usable"] = not literal_reasons
    r["literal_reasons"] = literal_reasons
    r["a62_says_usable"] = basis in A62_USABLE_BASES
    return r


def aggregate(judgements):
    usable = [j for j in judgements if j["usable"]]
    unusable = [j for j in judgements if not j["usable"]]
    lit_unusable = [j for j in judgements if not j["literal_usable"]]
    a62 = [j for j in judgements if j["a62_says_usable"]]
    reasons = {}
    for j in unusable:
        for rs in j["reasons"]:
            reasons[rs] = reasons.get(rs, 0) + 1
    return {
        "N": len(judgements),
        "U_primary": len(unusable),
        "usable_primary": len(usable),
        "U_primary_pct": round(100.0 * len(unusable) / len(judgements), 1) if judgements else 0.0,
        "U_primary_reasons": reasons,
        "A62_usable_records": len(a62),
        "U_newly": sum(1 for j in a62 if not j["usable"]),
        "U_newly_ids": sorted({j["hypothesis_id"] for j in a62 if not j["usable"]}),
        "U_literal": len(lit_unusable),
        "U_literal_pct": round(100.0 * len(lit_unusable) / len(judgements), 1) if judgements else 0.0,
        "U_newly_literal": sum(1 for j in a62 if not j["literal_usable"]),
        "usable_by_basis": {
            b: sum(1 for j in usable if j["threshold_basis"] == b)
            for b in sorted(A62_USABLE_BASES | {"professional_judgement_required"})
        },
        "usable_by_basis_literal": {
            b: sum(1 for j in judgements
                   if j["literal_usable"] and j["threshold_basis"] == b)
            for b in sorted(A62_USABLE_BASES | {"professional_judgement_required"})
        },
        "unusable_detail": [
            {"hypothesis_id": j["hypothesis_id"], "threshold_basis": j["threshold_basis"],
             "state": j["state"], "defaulted": j["defaulted"],
             "effective_status": j["threshold_review_status_effective"],
             "reasons": j["reasons"], "literal_usable": j["literal_usable"]}
            for j in unusable
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planning-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    mod = load_patched()
    corpus = []
    per_file_judgements = {}
    all_judgements = []
    for cid, rel, want_sha in CORPUS:
        path = os.path.join(args.planning_root, rel)
        raw = open(path, "rb").read()
        got_sha = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw.decode("utf-8"))
        if cid == "tolerance_table":
            items, kind = data["rows"], "tolerance_row"
        elif cid == "tolerance_signed":
            items, kind = data["thresholds"], "signed_threshold"
        else:
            items, kind = data, "hypothesis"
        judgements = []
        for item in items:
            rec = as_record(mod, cid, item, kind)
            j = judge(mod, rec)
            j["corpus"] = cid
            judgements.append(j)
        per_file_judgements[cid] = judgements
        all_judgements.extend(judgements)
        by_basis = {}
        for j in judgements:
            b = j["threshold_basis"]
            by_basis[b] = by_basis.get(b, 0) + 1
        corpus.append({
            "id": cid,
            "path": rel.replace("\\", "/"),
            "sha256_expected": want_sha,
            "sha256_actual": got_sha,
            "sha256_match": got_sha == want_sha,
            "bytes": len(raw),
            "records": len(judgements),
            "by_threshold_basis": by_basis,
            "threshold_review_status_carried": sum(
                1 for j in judgements if j["threshold_review_status_present"]),
            "host_state_approved_frozen": sum(
                1 for j in judgements if j["state"] == "approved_frozen"),
        })

    # ---- de-duplicated underlying level ------------------------------------
    distinct = {}
    for j in all_judgements:
        key = j["hypothesis_id"]
        if key not in distinct:
            distinct[key] = j
        else:
            # conservative union: unusable in ANY version => unusable underlying
            keep = distinct[key]
            if keep["usable"] and not j["usable"]:
                distinct[key] = j
            keep_lit = distinct[key]
            if keep_lit["literal_usable"] and not j["literal_usable"]:
                distinct[key]["literal_usable"] = False
                distinct[key]["literal_reasons"] = sorted(
                    set(keep_lit["literal_reasons"]) | set(j["literal_reasons"]))
    distinct_judgements = list(distinct.values())

    record_agg = aggregate(all_judgements)
    distinct_agg = aggregate(distinct_judgements)

    # ---- trigger lines ------------------------------------------------------
    t1_files = {}
    t1_hit = False
    for cid in sorted(HYP_FILES):
        js = per_file_judgements[cid]
        usable = [j for j in js if j["usable"]]
        usable_lit = [j for j in js if j["literal_usable"]]
        entry = {
            "usable_total": len(usable),
            "usable_arithmetic_identity": sum(
                1 for j in usable if j["threshold_basis"] == "arithmetic_identity"),
            "usable_disclosure_definition": sum(
                1 for j in usable if j["threshold_basis"] == "disclosure_definition"),
            "usable_total_literal": len(usable_lit),
            "usable_arithmetic_identity_literal": sum(
                1 for j in usable_lit if j["threshold_basis"] == "arithmetic_identity"),
            "usable_disclosure_definition_literal": sum(
                1 for j in usable_lit if j["threshold_basis"] == "disclosure_definition"),
        }
        entry["startup_blocked"] = (
            entry["usable_total"] == 0
            or entry["usable_arithmetic_identity"] == 0
            or entry["usable_disclosure_definition"] == 0)
        entry["startup_blocked_literal"] = (
            entry["usable_total_literal"] == 0
            or entry["usable_arithmetic_identity_literal"] == 0
            or entry["usable_disclosure_definition_literal"] == 0)
        t1_hit = t1_hit or entry["startup_blocked"]
        t1_files[cid] = entry
    t1_hit_literal = any(e["startup_blocked_literal"] for e in t1_files.values())

    def t2(agg):
        return agg["U_primary"] >= 0.75 * agg["N"], {
            "U": agg["U_primary"], "N": agg["N"],
            "pct": agg["U_primary_pct"], "threshold_pct": 75.0,
            "threshold_U_min": int(0.75 * agg["N"])}

    def t3(agg):
        return agg["U_newly"] >= 0.5 * agg["A62_usable_records"], {
            "U_newly": agg["U_newly"], "A62_usable": agg["A62_usable_records"],
            "threshold_U_newly_min": 0.5 * agg["A62_usable_records"]}

    t2_rec, t2_rec_d = t2(record_agg)
    t2_dis, t2_dis_d = t2(distinct_agg)
    t3_rec, t3_rec_d = t3(record_agg)
    t3_dis, t3_dis_d = t3(distinct_agg)

    t2_lit = (record_agg["U_literal"] >= 0.75 * record_agg["N"]
              or distinct_agg["U_literal"] >= 0.75 * distinct_agg["N"])
    t3_lit = (record_agg["U_newly_literal"] >= 0.5 * record_agg["A62_usable_records"]
              or distinct_agg["U_newly_literal"] >= 0.5 * distinct_agg["A62_usable_records"])

    fired = bool(t1_hit or t2_rec or t2_dis or t3_rec or t3_dis)
    fired_literal = bool(t1_hit_literal or t2_lit or t3_lit)

    report = {
        "monitor": "BLOCKED6C L271 counterexample monitor (oracle.md section 6)",
        "l271_quote": ("校验器新增 threshold_review_status 后出现大批历史阈值被判不可用、"
                       "导致 I-11-C 完全无法启动 ⇒ A-6.1 的实施方式需按实际情况重议，"
                       "但『未审定不得当已审定』这一实质不因此改变。"),
        "readings": {
            "U_PRIMARY": ("oracle 3.3: unusable = unknown_basis | unknown_status | "
                          "reviewed_unsealed | judgement_not_reviewed, UNION the "
                          "host document failing B6C-G1/G2/G3"),
            "U_LITERAL": ("A-6.1 item 1 literal reading: any effective status other "
                          "than reviewed => unusable (counterfactual, measured only)"),
        },
        "corpus": corpus,
        "corpus_sha256_all_match": all(c["sha256_match"] for c in corpus),
        "record_level": record_agg,
        "distinct_underlying_level": distinct_agg,
        "distinct_ids": sorted(distinct),
        "triggers": {
            "T1": {"rule": ("any of the 4 hypotheses files has usable_total==0 or "
                            "usable arithmetic==0 or usable disclosure==0"),
                   "per_file": t1_files, "hit": t1_hit, "hit_literal": t1_hit_literal},
            "T2_record": dict(t2_rec_d, hit=t2_rec),
            "T2_distinct": dict(t2_dis_d, hit=t2_dis),
            "T3_record": dict(t3_rec_d, hit=t3_rec),
            "T3_distinct": dict(t3_dis_d, hit=t3_dis),
            "T2_literal_hit": t2_lit,
            "T3_literal_hit": t3_lit,
        },
        "L271_trigger_fired": fired,
        "L271_trigger_fired_literal_A61_reading": fired_literal,
        "fail_closed": {
            "first_rule": "any L271 trigger hit => this card is blocked",
            "fired": fired,
        },
        "notes": [
            "Read-only monitor: no corpus file was modified.",
            "De-duplicated level keys on hypothesis_id/threshold_id; a threshold "
            "unusable in ANY version counts as unusable (conservative union).",
            "Tolerance-table rows and signed thresholds are never validated by "
            "tools/validate_hypotheses.py, so they cannot be rejected by "
            "B6C-G1/G2/G3; they still carry no threshold_review_status field.",
        ],
    }
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")

    print("corpus sha256 all match: %s" % report["corpus_sha256_all_match"])
    print("record level   N=%d U=%d (%.1f%%) U_newly=%d A62_usable=%d"
          % (record_agg["N"], record_agg["U_primary"], record_agg["U_primary_pct"],
             record_agg["U_newly"], record_agg["A62_usable_records"]))
    print("distinct level N=%d U=%d (%.1f%%) U_newly=%d A62_usable=%d"
          % (distinct_agg["N"], distinct_agg["U_primary"], distinct_agg["U_primary_pct"],
             distinct_agg["U_newly"], distinct_agg["A62_usable_records"]))
    print("U-LITERAL      record %d/%d  distinct %d/%d"
          % (record_agg["U_literal"], record_agg["N"],
             distinct_agg["U_literal"], distinct_agg["N"]))
    for cid in sorted(t1_files):
        e = t1_files[cid]
        print("T1 %-16s usable=%d ar=%d dj=%d blocked=%s | literal usable=%d ar=%d dj=%d blocked=%s"
              % (cid, e["usable_total"], e["usable_arithmetic_identity"],
                 e["usable_disclosure_definition"], e["startup_blocked"],
                 e["usable_total_literal"], e["usable_arithmetic_identity_literal"],
                 e["usable_disclosure_definition_literal"], e["startup_blocked_literal"]))
    print("T2 record hit=%s (%s) distinct hit=%s (%s)" % (t2_rec, t2_rec_d, t2_dis, t2_dis_d))
    print("T3 record hit=%s (%s) distinct hit=%s (%s)" % (t3_rec, t3_rec_d, t3_dis, t3_dis_d))
    print("L271_trigger_fired=%s  literal_A61=%s" % (fired, fired_literal))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
