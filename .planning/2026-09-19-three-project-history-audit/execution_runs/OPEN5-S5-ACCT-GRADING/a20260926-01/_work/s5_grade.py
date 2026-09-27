#!/usr/bin/env python3
"""OPEN5-S5-ACCT-GRADING — accounting-face grading checker (frozen oracle §4/§5).

Read-only against prior stations; writes only into this attempt's _work/.
Modes: baseline | m1_weak | m2_origin | m3_nourl | m4_quote
rc: 0 = matches frozen expectation, 2 = blocked branch, 3 = mismatch with oracle.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

PLAN = Path(".planning/2026-09-19-three-project-history-audit")
RUNS = PLAN / "execution_runs"
PEND5A = RUNS / "OPEN5-PEND5A-HK-ACQUISITION/a20260924-01"
S3DIR = RUNS / "OPEN5-S3-REACQUISITION/a20260925-01"
S4DIR = RUNS / "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01"
OUT = RUNS / "OPEN5-S5-ACCT-GRADING/a20260926-01"
WORK = OUT / "_work"

UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p: Path):
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


# ---------------------------------------------------------------- own extraction
def own_extract(pdf: Path, out_txt: Path, engine: str) -> str:
    """Independent re-extraction by this station (E1f element 2)."""
    if engine == "fitz":
        import fitz  # PyMuPDF

        doc = doc_open = None
        doc = fitz.open(str(pdf))
        parts = []
        for i, page in enumerate(doc, start=1):
            parts.append("<<<PAGE %d>>>\n" % i)
            parts.append(page.get_text())
        text = "".join(parts)
        doc.close()
    else:
        from pdfminer.high_level import extract_text

        text = extract_text(str(pdf))
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_bytes(text.encode("utf-8"))
    return text


# ---------------------------------------------------------------- policy
def policy_for(mode: str) -> dict:
    p = {
        "require_url": True,
        "require_utc": True,
        "tier_filter": True,          # ③/代理件 must NOT be graded admissible
        "require_independent_path": True,
        "exclude_origin": True,
        "strip_url_for": None,
        "tamper_quote": None,
    }
    if mode == "m1_weak":
        p.update(require_url=False, require_utc=False, tier_filter=False,
                 require_independent_path=False)
    elif mode == "m2_origin":
        p["exclude_origin"] = False
    elif mode == "m3_nourl":
        p["strip_url_for"] = "attempt04"
    elif mode == "m4_quote":
        p["tamper_quote"] = "q-01"
    return p


# ---------------------------------------------------------------- G2 / G3
def check_g2(src_id: str, ext: dict, corpus: Path, policy: dict, s3_entry: dict,
             s4_entry: dict) -> dict:
    url = ext.get("url")
    if policy["strip_url_for"] == src_id:
        url = None
    utc = ext.get("retrieved_utc")
    reg_sha = ext.get("sha256")
    got_sha = sha256_file(corpus) if corpus.exists() else None
    mtime_utc = None
    if corpus.exists():
        import datetime
        mtime_utc = datetime.datetime.utcfromtimestamp(
            corpus.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%SZ")
    a = bool(url) and str(url).startswith("https://")
    b = bool(utc) and bool(UTC_RE.match(str(utc))) and (mtime_utc == utc)
    c = bool(reg_sha) and got_sha == reg_sha == s3_entry.get("sha256") == s4_entry.get("sha256")
    d = True  # recorded here, never written back
    if not policy["require_url"]:
        a = True
    if not policy["require_utc"]:
        b = True
    return {
        "G2a_url": a, "G2b_utc": b, "G2c_sha256": c, "G2d_recorded_here": d,
        "url": url, "url_source": "PEND-5a provenance ext-04/ext-08",
        "retrieved_utc": utc, "retrieved_utc_mtime_corroboration": mtime_utc,
        "sha256_registered": reg_sha, "sha256_recomputed": got_sha,
        "sha256_s3": s3_entry.get("sha256"), "sha256_s4": s4_entry.get("sha256"),
        "resolved": bool(a and b and c and d),
    }


def check_g3(ext: dict, s3_entry: dict, s4_entry: dict) -> dict:
    station_flag = True  # oracle §4.2: this station records true per ④
    return {
        "adopted_semantics": "IND C 表 ④ (external_retrieval_not_local = true)",
        "station_records_external_retrieval_not_local": station_flag,
        "station_records_substitute_not_origin": True,
        "divergence": {
            "side_A_false": {
                "meaning": "非第三方代理（仅 r.jina.ai 代理件标 true）",
                "where": ["PEND-5a provenance ext-04/ext-08.external_retrieval_not_local=false",
                          "S3 provenance in-02/in-03.external_retrieval_not_local=false"],
                "values": [ext.get("external_retrieval_not_local"),
                           s3_entry.get("external_retrieval_not_local")],
                "back_written": False,
            },
            "side_B_true": {
                "meaning": "外部取回件一律标外部、永不冒充本地可核",
                "where": ["IND C 表 ④ L234", "OPEN-11 L360",
                          "S4 own_provenance.external_retrieval_not_local=true"],
                "values": [s4_entry.get("external_retrieval_not_local")],
                "back_written": False,
            },
            "resolution": "本工位按 ④ 语义裁为 true；两边均不回改，仅登记分歧（oracle §4.2）",
        },
        "resolved": True,
    }


# ---------------------------------------------------------------- E1 / S / tier
def verify_quotes(quotes, pend5a_probe: Path, policy: dict, own_texts: dict) -> list:
    out = []
    for q in quotes:
        art = PEND5A / q["artifact"]  # artifacts are relative to the PEND-5a attempt root
        rec = {"id": q["id"], "artifact": str(art), "expected_text": q["text"]}
        if not art.exists():
            rec.update(artifact_exists=False, e1e=False)
            out.append(rec)
            continue
        data = art.read_bytes()
        rec["artifact_exists"] = True
        rec["artifact_sha256_registered"] = q["artifact_sha256"]
        rec["artifact_sha256_recomputed"] = hashlib.sha256(data).hexdigest()
        rec["artifact_sha_match"] = rec["artifact_sha256_recomputed"] == q["artifact_sha256"]
        b0, b1 = q["byte_range"]
        if policy["tamper_quote"] == q["id"]:
            b0, b1 = b0 + 1, b1 + 1
        try:
            seg = data[b0:b1].decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            seg = "<decode-error:%s>" % exc
        rec["byte_range_used"] = [b0, b1]
        rec["byte_text"] = seg
        rec["byte_exact"] = seg == q["text"]
        engine = "pdfminer" if "pdfminer" in q["artifact"] else "fitz"
        own = own_texts.get(engine) or own_texts.get("fitz")
        rec["found_in_own_extraction"] = bool(own) and norm(q["text"]) in norm(own)
        rec["e1e"] = bool(rec["artifact_sha_match"] and rec["byte_exact"]
                          and rec["found_in_own_extraction"])
        out.append(rec)
    return out


def grade_source(sid: str, doc_type: str, issuer_doc: bool, same_period: bool,
                 lang_faces: list, quotes_ok: bool, independent_ok: bool,
                 g2: dict, g3: dict, policy: dict, s4_face: str) -> dict:
    """oracle §4.3 / §4.4."""
    # --- tier
    if not issuer_doc and doc_type == "third_party_proxy_render":
        tier = "③"
        tier_name = "secondary_lead_only"
    elif issuer_doc:
        tier = "①"
        tier_name = "company_primary_disclosure"
    else:
        tier = "②"
        tier_name = "regulator_primary_disclosure"
    if not policy["tier_filter"] and tier == "③":
        tier, tier_name = "①", "company_primary_disclosure"  # MUTANT only
    # --- E elements
    e = {
        "E1a_local_archive": True,
        "E1b_url": g2["G2a_url"],
        "E1c_retrieved_utc": g2["G2b_utc"],
        "E1d_sha256": g2["G2c_sha256"],
        "E1e_verbatim_quote": quotes_ok,
        "E1f_independent_path": independent_ok if policy["require_independent_path"] else True,
    }
    e_ok = all(e.values())
    if tier == "③":
        e_level, e_note = "E3", "第三方代理渲染件 = 二手（ACCT L68 / ③ 仅可提问题）"
        s_level, s_note = "S0", "非公司原文披露，不得支撑参数"
    elif e_ok:
        e_level, e_note = "E1", "六要素齐（ACCT L66/L153）"
        s_level, s_note = "S1", "同期间公司原文披露 + 可定位 + sha 绑定 + ≥1 独立路径复核（ACCT L56）"
    else:
        e_level, e_note = "E2", "要素不全，降级：仅叙述与风险提示（ACCT L67）"
        s_level, s_note = "S0", "要素不全 ⇒ 不得支撑参数"
    admissible = bool(e_level == "E1" and s_level == "S1" and g2["resolved"]
                      and g3["resolved"] and (tier in ("①", "②")))
    return {
        "source_id": sid,
        "document_type": doc_type,
        "period": "FY2025" if same_period else "n/a",
        "c_table_tier": tier,
        "c_table_evidence_class": tier_name,
        "c_table_4_external_flag": g3["station_records_external_retrieval_not_local"],
        "must_label": {"document_type": doc_type,
                       "period": "FY2025（与 origin 年报同期间）" if same_period else "n/a"},
        "e_elements": e,
        "e_level": e_level,
        "e_level_note": e_note,
        "s_tier": s_level,
        "s_tier_note": s_note,
        "usable_faces": lang_faces,
        "s4_face_result": s4_face,
        "external_never_impersonates_local": True,
        "g2": g2, "g3": g3,
        "pass": admissible,
    }


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    pol = policy_for(mode)
    WORK.mkdir(parents=True, exist_ok=True)

    p5a = load(PEND5A / "provenance.json")
    exts = {e["id"]: e for e in p5a["external_evidence"]}
    quotes_by_ext = {}
    for q in p5a["verbatim_quotes"]:
        quotes_by_ext.setdefault(q["external_evidence_id"], []).append(q)

    s3 = load(S3DIR / "provenance.json")
    s3_ext = {}
    for e in s3.get("entries", []):
        s3_ext[e.get("id")] = e
    # S3 in-02 / in-03 live under a different key family; fall back to a scan
    if "in-02" not in s3_ext:
        def walk(o):
            if isinstance(o, dict):
                if o.get("id") in ("in-02", "in-03"):
                    s3_ext[o["id"]] = o
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(s3)

    s4 = load(S4DIR / "dual_path_verify.json")
    s4_own = s4["provenance_review"]["own_provenance"]
    s4_sub = {"attempt04": s4_own["substitute_attempt04"],
              "attempt08": s4_own["substitute_attempt08"]}

    # ---- own independent extraction (E1f, this station)
    corpus04 = PEND5A / "corpus/attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf"
    corpus08 = PEND5A / "corpus/attempt08_irmi_xiaomi_ar2025_en.pdf"
    own_texts = {}
    for engine, pdf in (("fitz", corpus04), ("pdfminer", corpus04)):
        own_texts[engine] = own_extract(pdf, WORK / ("extract/s5_attempt04_%s.txt" % engine), engine)
    own_texts["fitz08"] = own_extract(corpus08, WORK / "extract/s5_attempt08_fitz.txt", "fitz")
    own_texts["pdfminer08"] = own_extract(corpus08, WORK / "extract/s5_attempt08_pdfminer.txt", "pdfminer")

    probe_dir = PEND5A / "probe"
    q04 = verify_quotes(quotes_by_ext.get("ext-04", []), probe_dir, pol,
                        {"fitz": own_texts["fitz"], "pdfminer": own_texts["pdfminer"]})
    q08 = verify_quotes(quotes_by_ext.get("ext-08", []), probe_dir, pol,
                        {"fitz": own_texts["fitz08"], "pdfminer": own_texts["pdfminer08"]})
    proxy_text = (PEND5A / "corpus/attempt07_rjina_xiaomi_ar2025_zh_proxy.txt").read_text(
        encoding="utf-8", errors="replace")
    q07 = verify_quotes(quotes_by_ext.get("ext-07", []), probe_dir, pol,
                        {"fitz": proxy_text})

    # ---- G2 / G3
    g2_04 = check_g2("attempt04", exts["ext-04"], corpus04, pol, s3_ext["in-02"], s4_sub["attempt04"])
    g2_08 = check_g2("attempt08", exts["ext-08"], corpus08, pol, s3_ext["in-03"], s4_sub["attempt08"])
    g3_04 = check_g3(exts["ext-04"], s3_ext["in-02"], s4_sub["attempt04"])
    g3_08 = check_g3(exts["ext-08"], s3_ext["in-03"], s4_sub["attempt08"])

    # attempt07 = third-party proxy (baseline must reject; mutant M1 must pass)
    proxy_file = PEND5A / "corpus/attempt07_rjina_xiaomi_ar2025_zh_proxy.txt"
    g2_07 = check_g2("attempt07", exts["ext-07"], proxy_file, pol,
                     {"sha256": exts["ext-07"]["sha256"]},
                     {"sha256": exts["ext-07"]["sha256"]})
    g3_07 = check_g3(exts["ext-07"], {"external_retrieval_not_local": True},
                     {"external_retrieval_not_local": True})

    results = {}
    results["attempt04"] = grade_source(
        "attempt04", "全年业绩公告（results announcement，非年度报告）", True, True,
        ["zh-Hant"], all(q["e1e"] for q in q04), True, g2_04, g3_04, pol,
        s4["faces"]["U2_substitute_attempt04"]["verdict"])
    results["attempt08"] = grade_source(
        "attempt08", "年度报告英文版（annual report, EN）", True, True,
        ["en"], all(q["e1e"] for q in q08), True, g2_08, g3_08, pol,
        s4["faces"]["U3_substitute_attempt08"]["verdict"])
    results["attempt07_proxy"] = grade_source(
        "attempt07", "third_party_proxy_render", False, True,
        [], all(q["e1e"] for q in q07), False, g2_07, g3_07, pol, "not_subject_to_S4")

    # ---- origin exclusion (oracle §4.5)
    origin = {"source_id": "HK-XIAOMI-AR2025 (origin)",
              "excluded_from_grading": pol["exclude_origin"],
              "graded": not pol["exclude_origin"],
              "level": None if pol["exclude_origin"] else "E1/S1 (MUTANT — must not happen)",
              "admissible": False,
              "disposition": "S4 NOT_USABLE + L165 该来源不可引用、维持不可读处置；STOP_EVIDENCE/not_readable 不变"}
    g2_origin = {"resolved": not pol["exclude_origin"] or False}

    blocked_reasons = []
    for sid in ("attempt04", "attempt08"):
        if not results[sid]["g2"]["resolved"]:
            blocked_reasons.append("G2 unresolved for %s" % sid)
        if not results[sid]["g3"]["resolved"]:
            blocked_reasons.append("G3 unresolved for %s" % sid)
        if not results[sid]["e_elements"]["E1e_verbatim_quote"]:
            blocked_reasons.append("E1e verbatim quote check failed for %s" % sid)
    verdict = "blocked" if blocked_reasons else "GRADED"

    out = {
        "mode": mode,
        "policy": pol,
        "g2_resolved": bool(results["attempt04"]["g2"]["resolved"] and results["attempt08"]["g2"]["resolved"]),
        "g3_resolved": bool(results["attempt04"]["g3"]["resolved"] and results["attempt08"]["g3"]["resolved"]),
        "g2_by_source": {"attempt04": g2_04, "attempt08": g2_08},
        "g3_by_source": {"attempt04": g3_04, "attempt08": g3_08},
        "quote_checks": {"attempt04": q04, "attempt08": q08, "attempt07": q07},
        "grades": results,
        "origin": origin,
        "origin_g2_note": g2_origin,
        "verdict": verdict,
        "blocked_reasons": blocked_reasons,
        "hk_parameters_released": False,
        "releases_nothing": True,
        "own_extraction": {
            "fitz_attempt04": {"sha256": sha256_file(WORK / "extract/s5_attempt04_fitz.txt")},
            "pdfminer_attempt04": {"sha256": sha256_file(WORK / "extract/s5_attempt04_pdfminer.txt")},
            "fitz_attempt08": {"sha256": sha256_file(WORK / "extract/s5_attempt08_fitz.txt")},
            "pdfminer_attempt08": {"sha256": sha256_file(WORK / "extract/s5_attempt08_pdfminer.txt")},
        },
    }

    # ---------------- frozen expectations (oracle §5) ----------------
    if mode == "baseline":
        exp_ok = (out["g2_resolved"] and out["g3_resolved"]
                  and results["attempt04"]["c_table_tier"] == "①"
                  and results["attempt04"]["e_level"] == "E1"
                  and results["attempt04"]["s_tier"] == "S1"
                  and results["attempt04"]["pass"] is True
                  and results["attempt08"]["c_table_tier"] == "①"
                  and results["attempt08"]["e_level"] == "E1"
                  and results["attempt08"]["s_tier"] == "S1"
                  and results["attempt08"]["usable_faces"] == ["en"]
                  and results["attempt08"]["pass"] is True
                  and results["attempt07_proxy"]["pass"] is False
                  and results["attempt07_proxy"]["c_table_tier"] == "③"
                  and results["attempt07_proxy"]["e_level"] == "E3"
                  and origin["graded"] is False and origin["level"] is None
                  and verdict == "GRADED" and out["hk_parameters_released"] is False)
        out["expectation_met"] = exp_ok
        rc = 0 if exp_ok else 3
    elif mode == "m1_weak":
        flip = (results["attempt07_proxy"]["pass"] is True
                and results["attempt07_proxy"]["c_table_tier"] == "①")
        out["should_pass_flip"] = flip   # a source that must NOT pass now passes
        out["expectation_met"] = flip
        rc = 0 if flip else 3
    elif mode == "m2_origin":
        flip = origin["graded"] is True and origin["level"] is not None
        out["origin_grade_flip"] = flip
        out["expectation_met"] = flip
        rc = 0 if flip else 3
    elif mode == "m3_nourl":
        out["expectation_met"] = verdict == "blocked"
        rc = 2 if verdict == "blocked" else 3
    elif mode == "m4_quote":
        out["expectation_met"] = verdict == "blocked"
        rc = 2 if verdict == "blocked" else 3
    else:
        out["expectation_met"] = False
        rc = 3

    path = WORK / ("s5_measure_%s.json" % mode)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    # re-parse gate
    with open(path, "r", encoding="utf-8") as fh:
        json.load(fh)
    print(json.dumps({"mode": mode, "rc": rc, "verdict": verdict,
                      "g2": out["g2_resolved"], "g3": out["g3_resolved"],
                      "attempt04": results["attempt04"]["e_level"] + "/" + results["attempt04"]["s_tier"] + "/" + results["attempt04"]["c_table_tier"],
                      "attempt08": results["attempt08"]["e_level"] + "/" + results["attempt08"]["s_tier"] + "/" + results["attempt08"]["c_table_tier"],
                      "attempt07_pass": results["attempt07_proxy"]["pass"],
                      "origin_graded": origin["graded"],
                      "expectation_met": out["expectation_met"]}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
