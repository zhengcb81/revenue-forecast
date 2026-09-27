#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPEN5-S5-IND-RULING · S5 行业半区四点裁定 + 红绿变异
- oracle.md 已先冻结（sha256 549cadfe…）；本脚本只读输入，输出只落本目录 _work/（baseline 另写 ind_ruling.json）
- 用法: python -B s5_ind_grade.py [baseline|m1_weak|m2_origin|m3_nourl|m4_noseg|m5_langconflict]
- rc: 0=判定通过且与冻结期望全等 / 2=触发 oracle §4.7 blocked / 3=与冻结期望不符（判据空转或漏判）
"""
import datetime
import hashlib
import json
import os
import re
import sys

PLAN = ".planning/2026-09-19-three-project-history-audit"
R = os.path.join(PLAN, "execution_runs")
HERE = os.path.join(R, "OPEN5-S5-IND-RULING", "a20260926-01")
WORK = os.path.join(HERE, "_work")
EX = os.path.join(WORK, "extract")

ENV_RULING = os.path.join(R, "I11A-OPEN5-ENVOWNER", "a20260924-01", "ruling.md")
IND_RULING = os.path.join(R, "I11A-OPEN-IND", "a20260924-01", "ruling.md")
ACCT_DIR = os.path.join(R, "OPEN5-S5-ACCT-GRADING", "a20260926-01")
S4_DIR = os.path.join(R, "OPEN5-S4-DUAL-PATH-VERIFY", "a20260926-01")
S3_PROV = os.path.join(R, "OPEN5-S3-REACQUISITION", "a20260925-01", "provenance.json")
S3_REPORT = os.path.join(R, "OPEN5-S3-REACQUISITION", "a20260925-01", "reacquisition_report.md")
PEND5A = os.path.join(R, "OPEN5-PEND5A-HK-ACQUISITION", "a20260924-01")
OWNER = os.path.join(PLAN, "OWNER_DECISIONS.md")
CORPUS = os.path.join(PEND5A, "corpus")

MODES = ("baseline", "m1_weak", "m2_origin", "m3_nourl", "m4_noseg", "m5_langconflict")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def line(path, n):
    return read_lines(path)[n - 1]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(path, "r", encoding="utf-8") as f:  # 写后重解析
        json.load(f)


def fnum(s):
    return float(str(s).replace(",", ""))


def norm_ws(s):
    return re.sub(r"\s+", " ", s)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if mode not in MODES:
        print("unknown mode", mode)
        return 3
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ---------------- 逐字引文（从源文件按行取，杜绝转述误差）----------------
    quotes = {
        "ENVOWNER_L165": line(ENV_RULING, 165),
        "ENVOWNER_L166": line(ENV_RULING, 166),
        "ENVOWNER_L174": line(ENV_RULING, 174),
        "ENVOWNER_L179": line(ENV_RULING, 179),
        "IND_L227": line(IND_RULING, 227),
        "IND_L231": line(IND_RULING, 231),
        "IND_L232": line(IND_RULING, 232),
        "IND_L233": line(IND_RULING, 233),
        "IND_L234": line(IND_RULING, 234),
        "IND_L240": line(IND_RULING, 240),
        "IND_L241": line(IND_RULING, 241),
        "IND_L261": line(IND_RULING, 261),
        "IND_L360": line(IND_RULING, 360),
        "OWNER_L502": line(OWNER, 502),
        "OWNER_L504": line(OWNER, 504),
    }
    acct_report_lines = read_lines(os.path.join(ACCT_DIR, "s5_acct_report.md"))
    quotes["ACCT_S6_items_1_7"] = acct_report_lines[175:182]
    s4_report_lines = read_lines(os.path.join(S4_DIR, "s4_report.md"))
    quotes["S4_REQUEST_L197_L200"] = s4_report_lines[196:200]

    # ---------------- 判据源行存在性检查（§4.7-3）----------------
    source_checks = {
        "ENVOWNER_L166_has_S5": "行业复裁 + 会计定级" in quotes["ENVOWNER_L166"] and "_PLACEHOLDER" in quotes["ENVOWNER_L166"],
        "ENVOWNER_L179_has_boundary": "S3/S4/S5 走完之前" in quotes["ENVOWNER_L179"],
        "IND_L234_has_4_rule": "永不冒充本地可核" in quotes["IND_L234"],
        "IND_L240_has_no_enable": "C 表不启用" in quotes["IND_L240"],
        "IND_L241_has_segment_revenue": "①类可读原文且含分部收入" in quotes["IND_L241"],
        "IND_L360_has_semantics": "external_retrieval_not_local" in quotes["IND_L360"],
        "IND_L261_has_no_silent_replace": "静默顶替本地原件" in quotes["IND_L261"],
        "OWNER_L504_has_acct_authority": "证据等级由会计面定" in quotes["OWNER_L504"],
    }

    # ---------------- 输入：JSON 载体 ----------------
    p5a_prov = load_json(os.path.join(PEND5A, "provenance.json"))
    p5a_hand = load_json(os.path.join(PEND5A, "handoff.json"))
    s3_prov = load_json(S3_PROV)
    s4 = load_json(os.path.join(S4_DIR, "dual_path_verify.json"))
    acct = load_json(os.path.join(ACCT_DIR, "acct_grading.json"))
    acct_hand = load_json(os.path.join(ACCT_DIR, "handoff.json"))
    extract = load_json(os.path.join(WORK, "s5_ind_extract.json"))

    ext = {e["id"]: e for e in p5a_prov["external_evidence"]}
    s3_in = {e["id"]: e for e in s3_prov["entries"] if e.get("id") in ("in-02", "in-03")}

    # ---------------- 语料字节 sha 复算（§4.7-3）----------------
    paths = {
        "attempt04": os.path.join(CORPUS, "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf"),
        "attempt08": os.path.join(CORPUS, "attempt08_irmi_xiaomi_ar2025_en.pdf"),
        "attempt07": os.path.join(CORPUS, "attempt07_rjina_xiaomi_ar2025_zh_proxy.txt"),
        "origin_copy": os.path.join(CORPUS, "attempt01_hkexnews_xiaomi_ar2025_zh.pdf"),
    }
    sha = {k: sha256_file(v) for k, v in paths.items()}
    sha_chain = {}
    for src, ext_id, s3_id in (("attempt04", "ext-04", "in-02"), ("attempt08", "ext-08", "in-03")):
        registered = {
            "pend5a": ext[ext_id]["sha256"],
            "s3": s3_in[s3_id]["sha256"],
            "s4": s4["provenance_review"]["own_provenance"]["substitute_" + src]["sha256"],
            "acct_g2": acct["step1_g2_g3"]["g2_resolution"]["by_source"][src]["G2c_sha256"]
            ["sha256_registered_pend5a"],
            "recomputed": sha[src],
        }
        registered["all_equal"] = len(set(registered.values())) == 1
        sha_chain[src] = registered

    # ---------------- 自抽文本（用于 J3-2 与变异）----------------
    zh_text = open(os.path.join(EX, "s5_ind_attempt04_fitz.txt"), encoding="utf-8").read()
    en_text = open(os.path.join(EX, "s5_ind_attempt08_fitz.txt"), encoding="utf-8").read()
    mut_notes = []

    if mode == "m3_nourl":
        # 剥离 attempt04 的 URL（模拟 G2a 缺失）—— 不改任何前站文件，只在内存里改本次输入
        ext["ext-04"] = dict(ext["ext-04"], url=None)
        mut_notes.append("mutated in-memory: attempt04 url := None (模拟 G2a 缺失)")
    if mode == "m4_noseg":
        # 抹去①件正文中全部分部收入披露锚（模拟 L241 正向条件不成立）
        for t in ("分部收入", "分部收益", "手機×AIoT", "業務分部", "Segment-wise", "segment revenue",
                  "revenue of our"):
            zh_text = zh_text.replace(t, "████")
            en_text = en_text.replace(t, "████")
        mut_notes.append("mutated in-memory: all segment-revenue anchors masked in attempt04/attempt08 texts")
    if mode == "m5_langconflict":
        en_text, nsub = re.subn(r"(Total revenue\s+)457,286\.7", r"\g<1>457,286.9", en_text, count=1)
        mut_notes.append("mutated in-memory: attempt08 'Total revenue 457,286.7' -> 457,286.9 (substitutions=%d)" % nsub)

    nz, ne = norm_ws(zh_text), norm_ws(en_text)

    # ---------------- J3-2 跨语言共享数值（6 对）----------------
    pair_defs = [
        # (name, zh 正则, en 正则, zh 除数(單位換算：億元→billion), en 除数)
        ("total_revenue_bn", r"集團總收入為人民幣([\d,]+)億元", r"total revenue was\s*RMB([\d.]+)\s*billion", 10.0, 1.0),
        ("segment_revenue_bn", r"AIoT」分部收入為人民幣\s*([\d,]+)\s*億元",
         r"smartphone × AIoT segment reached RMB([\d.]+)\s*billion", 10.0, 1.0),
        ("segment_table_mn", r"手機×AIoT ([\d,]+\.\d) 76\.8%", r"Smartphone × AIoT ([\d,]+\.\d) 76\.8%", 1.0, 1.0),
        ("total_table_mn", r"總收入 ([\d,]+\.\d) 100\.0%", r"Total revenue ([\d,]+\.\d) 100\.0%", 1.0, 1.0),
        ("yoy_pct", r"比增長([\d.]+)%", r"increase of ([\d.]+)%", 1.0, 1.0),
        ("segment_gm_pct", r"分部毛利率達到歷史新高的([\d.]+)%", r"segment reached a record high of ([\d.]+)%", 1.0, 1.0),
    ]
    pairs = []
    for name, pzh, pen, div_zh, div_en in pair_defs:
        mzh, men = re.search(pzh, nz), re.search(pen, ne)
        vzh = fnum(mzh.group(1)) / div_zh if mzh else None
        ven = fnum(men.group(1)) / div_en if men else None
        if vzh is None or ven is None:
            status = "unmatched"
        elif abs(vzh - ven) <= 1e-6:
            status = "equal"
        else:
            status = "conflict"
        pairs.append({"pair": name, "zh_value": vzh, "en_value": ven, "status": status})
    n_equal = sum(1 for p in pairs if p["status"] == "equal")
    n_conflict = sum(1 for p in pairs if p["status"] == "conflict")

    # ---------------- J1-1 owner 解锁链 ----------------
    auth = p5a_hand.get("authorized_by", "")
    j1_1 = {
        "owner_authorization_found": ("§二十六" in auth and "授权" in auth),
        "station_delivered": str(p5a_hand.get("result", "")).startswith("delivered"),
        "authorized_by_verbatim": auth,
        "source": "execution_runs/OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/handoff.json authorized_by / result",
    }
    j1_1["ok"] = j1_1["owner_authorization_found"] and j1_1["station_delivered"]

    # ---------------- J1-2 S3 / S4 站点结论 ----------------
    s3_report_text = open(S3_REPORT, encoding="utf-8").read()
    j1_2 = {
        "s3_pathA_5of5_recorded": "5/5 锚词" in s3_report_text,
        "s3_B1_0of5_recorded": "B1（原文件文字层，全 415 页） | **0/5**" in s3_report_text or "0/5" in s3_report_text,
        "s4_consistency_result": s4.get("consistency_result"),
        "s4_u1": s4["faces"]["U1_origin_HK-XIAOMI-AR2025"]["verdict"],
        "s4_u2": s4["faces"]["U2_substitute_attempt04"]["verdict"],
        "s4_u3": s4["faces"]["U3_substitute_attempt08"]["verdict"],
    }
    j1_2["ok"] = (j1_2["s3_pathA_5of5_recorded"] and j1_2["s3_B1_0of5_recorded"]
                  and j1_2["s4_consistency_result"] == "NOT_USABLE"
                  and j1_2["s4_u1"] == "NOT_USABLE" and j1_2["s4_u2"] == "CONSISTENT"
                  and j1_2["s4_u3"] == "CONSISTENT")

    # ---------------- J1-3 ①三条件 + ④三件套 + 含分部收入 ----------------
    dt = extract["document_type"]
    src_cond = {}
    for src, ext_id in (("attempt04", "ext-04"), ("attempt08", "ext-08")):
        e = ext[ext_id]
        locatable = False
        if src == "attempt04":
            locatable = extract["segment_revenue_disclosure"]["attempt04"]["evidence"] is not None
            period_ok = dt["attempt04_has_period_verbatim"] and dt["attempt04_has_results_announcement_title"]
            period_evidence = "标题逐字「截至2025年12月31日止年度…全年業績公告」"
        else:
            locatable = extract["segment_revenue_disclosure"]["attempt08"]["evidence"] is not None
            period_ok = dt["attempt08_has_annual_report_title"] and dt["attempt08_has_period_marker"]
            period_evidence = "封面逐字「2025 ANNUAL REPORT」"
        url = e.get("url")
        if mode == "m3_nourl" and src == "attempt04":
            url = None
        entry = {
            "c1_locatable": locatable,
            "c1_evidence": extract["segment_revenue_disclosure"][src]["evidence"],
            "c2_sha256_equal": sha_chain[src]["all_equal"],
            "c2_sha_chain": sha_chain[src],
            "c3_period_same": period_ok,
            "c3_period_evidence": period_evidence,
            "r4_url": bool(url),
            "r4_url_value": url,
            "r4_retrieved_utc": e.get("retrieved_utc"),
            "r4_utc_matches_mtime": e.get("retrieved_utc") == extract["inputs"][src]["mtime_utc"],
            "r4_sha256": e.get("sha256"),
            "segment_revenue_anchors": extract["segment_revenue_disclosure"][src]["anchors_hit"],
            "readable_anchor_hits": (extract["anchors"]["attempt04_fitz_zh"]["hit_words"] if src == "attempt04"
                                     else extract["anchors"]["attempt08_fitz_en"]["hit_words"]),
        }
        entry["c1_4_conditions_ok"] = all([entry["c1_locatable"], entry["c2_sha256_equal"],
                                           entry["c3_period_same"], entry["r4_url"],
                                           entry["r4_retrieved_utc"], entry["r4_sha256"]])
        entry["contains_segment_revenue"] = (len(entry["segment_revenue_anchors"]) > 0
                                             if mode != "m4_noseg" else False)
        entry["tier_1_ok"] = entry["c1_4_conditions_ok"] and entry["contains_segment_revenue"]
        src_cond[src] = entry
    l241_ok = any(v["tier_1_ok"] for v in src_cond.values())

    j1_3 = {"per_source": src_cond, "l241_antecedent_met": l241_ok,
            "reading": "α（l240 的『读不出原文』= 新 attempt 产不出任何可读原文文本；S3 路径 A 5/5 + 两件①替代件可读 ⇒ 不成立）"}

    # ---------------- attempt07：③ 判定 ----------------
    tier_filter = True if mode != "m1_weak" else False
    require_readable = True if mode != "m1_weak" else False
    a07 = {
        "provenance_class": ext["ext-07"]["provenance_class"],
        "is_third_party_proxy": "third_party_proxy" in ext["ext-07"]["provenance_class"],
        "anchor_hits_zh": extract["anchors"]["attempt07_proxy_zh"]["hit_words"],
        "tier": "③",
        "external_flag": ext["ext-07"]["external_retrieval_not_local"],
    }
    a07["tier_filter_enforced"] = tier_filter
    a07["tier_effective"] = "③（secondary_lead_only，按定义不可进参数/命题）" if tier_filter \
        else "①(MUTANT, tier_filter=off)"
    a07["readable_ok"] = (a07["anchor_hits_zh"] >= 3) or (not require_readable)
    # 基线：③ = 仅线索 ⇒ 行业面不可采；变异 M1：关掉分类与可读性闸门后必须翻转为可采
    a07["industry_admissible"] = bool((not tier_filter) and a07["readable_ok"])

    # ---------------- origin 排除 ----------------
    exclude_origin = mode != "m2_origin"
    origin = {
        "source": "HK-XIAOMI-AR2025",
        "excluded": exclude_origin,
        "graded": not exclude_origin,
        "level": None if exclude_origin else "E1/S1 (MUTANT — 测试产物，非结论)",
        "admissible": False,
        "s4_consistency_result": s4.get("consistency_result"),
        "rule": "ENVOWNER L165 + S4 NOT_USABLE + oracle §4.5/§4.6",
    }

    # ---------------- J4 G3 口径 ----------------
    g3 = {
        "side_A_false": {"pend5a_ext04": ext["ext-04"]["external_retrieval_not_local"],
                         "pend5a_ext08": ext["ext-08"]["external_retrieval_not_local"],
                         "s3_in02": s3_in["in-02"]["external_retrieval_not_local"],
                         "s3_in03": s3_in["in-03"]["external_retrieval_not_local"]},
        "side_B_true": {"s4_attempt04": s4["provenance_review"]["own_provenance"]["substitute_attempt04"][
                            "external_retrieval_not_local"],
                        "s4_attempt08": s4["provenance_review"]["own_provenance"]["substitute_attempt08"][
                            "external_retrieval_not_local"],
                        "ind_L234_4_row": "external_retrieval_not_local" in quotes["IND_L234"],
                        "ind_L360": "external_retrieval_not_local" in quotes["IND_L360"]},
        "adopted": "B（true）",
        "both_sides_back_written": False,
    }
    g3["side_A_is_false"] = all(v is False for v in g3["side_A_false"].values())
    g3["side_B_is_true"] = all(v is True for v in g3["side_B_true"].values())
    g4_ok = g3["side_A_is_false"] and g3["side_B_is_true"]

    # ---------------- J2/J3 内容清单判定（按冻结 oracle 的 A1..A7）----------------
    inv = extract["attempt04_inventory"]
    inv08 = extract["attempt08_inventory"]
    attempt04_usable = {
        "A1_分部收入水平与增速": inv["A1_segment_revenue_level_growth"]["present"],
        "A2_分部毛利率与毛利": inv["A2_segment_gross_margin"]["present"],
        "A3_总收入与增速": inv["A3_total_revenue_growth"]["present"],
        "A4a_分部加总=合并总收入恒等式": inv["A4_segment_note_reconciliation"]["present"],
        "A5a_公告自述审核状态": inv["A5_audit_opinion"]["present"],
        "A6b_分部存货与按性质开支": inv["A6_five_year_and_notes"]["present"],
    }
    a4b_evidence = {
        "en_ar_states_no_segment_assets": "no separate segment assets" in ne,
        "zh_announcement_segment_assets_anchor_hits":
            inv["A4_segment_note_reconciliation"]["hits"]["分部資產"]["count"],
        "ruling": "缺 ⇒ 禁止（fail-closed：两个来源都明示/实测不含分部资产与负债划分）",
    }
    attempt04_forbidden = {
        "A4b_分部资产与负债划分": True,
        "A5b_审计意见与核数师报告逐字": (inv["A5_audit_opinion"]["hits"]["核數師報告"]["count"] == 0
                                     and inv["A5_audit_opinion"]["hits"]["無保留意見"]["count"] == 0),
        "A6a_五年财务摘要与跨期多年序列": inv["A6_five_year_and_notes"]["hits"]["財務摘要"]["count"] == 0,
        "A7_年报本体页码与锚文本": inv["A7_annual_report_body_marker"]["present"] is False,
        "A8_年报刊发日(2026-04-28)之后才披露的内容": True,
    }
    seg_identity = {"lhs": 351217174, "rhs": 106069513, "total": 457286687,
                    "equal": 351217174 + 106069513 == 457286687}

    # ---------------- J3 语言面 ----------------
    zh_hit = extract["anchors"]["attempt08_fitz_zh"]["hit_words"]
    en_hit_fitz = extract["anchors"]["attempt08_fitz_en"]["hit_words"]
    en_hit_pm = extract["anchors"]["attempt08_pdfminer_en"]["hit_words"]
    j3_1 = {"zh_anchor_hits": zh_hit, "zh_registered_as": "0/5（会计面 usable=[en]）",
            "zh_matches_registration": zh_hit == 0,
            "en_anchor_hits_fitz": en_hit_fitz, "en_anchor_hits_pdfminer": en_hit_pm,
            "en_threshold_ge4": min(en_hit_fitz, en_hit_pm) >= 4}
    j3_2 = {"pairs": pairs, "equal": n_equal, "conflict": n_conflict,
            "require_ge2_equal_and_0_conflict": (n_equal >= 2 and n_conflict == 0)}

    # ---------------- blocked 触发（oracle §4.7）----------------
    blocked = []
    if not all(source_checks.values()):
        blocked.append("§4.7-3 判据源行缺失: " + json.dumps(source_checks, ensure_ascii=False))
    if not j1_1["ok"]:
        blocked.append("§4.7-2 owner 解锁链不可核")
    if not j1_2["ok"]:
        blocked.append("§4.7-2 S3/S4 站点结论不可核")
    for src in ("attempt04", "attempt08"):
        if not sha_chain[src]["all_equal"]:
            blocked.append("§4.7-3 %s sha256 登记与复算不全等" % src)
        if not src_cond[src]["c1_4_conditions_ok"]:
            blocked.append("§4.7-1/§4.7-7 %s ①三条件或④三件套不满足（url=%s utc=%s sha=%s 定位=%s 期间=%s）"
                           % (src, src_cond[src]["r4_url"], bool(src_cond[src]["r4_retrieved_utc"]),
                              src_cond[src]["r4_sha256"] is not None, src_cond[src]["c1_locatable"],
                              src_cond[src]["c3_period_same"]))
    if not l241_ok:
        blocked.append("§4.7-1 J1-3 不成立：无①类通过三条件且含分部收入的来源 ⇒ C 表不启用（IND L241 正向条件不成立）")
    if not j3_1["en_threshold_ge4"]:
        blocked.append("§4.7-4 attempt08 英文锚词 <4/5")
    if not j3_2["require_ge2_equal_and_0_conflict"]:
        blocked.append("§4.7-4 跨语言数值比对失败：equal=%d conflict=%d" % (n_equal, n_conflict))
    if not g4_ok:
        blocked.append("§4.7-5 G3 两侧口径实测与冻结描述不符")
    if s4.get("consistency_result") != "NOT_USABLE":
        blocked.append("§4.7-6 纪律违例：S4 consistency_result 被改动")
    if acct_hand.get("hk_parameters_released") is not False:
        blocked.append("§4.7-6 纪律违例：会计半区 hk_parameters_released 非 false")
    if origin["graded"] and exclude_origin:
        blocked.append("§4.7-6 纪律违例：origin 在排除规则下仍被赋级")

    verdict = "blocked" if blocked else "PASS"
    c_table_adopted = (not blocked) and j1_1["ok"] and j1_2["ok"] and l241_ok
    industry_face = "PASS（四点全部裁定成立）" if verdict == "PASS" else "BLOCKED"

    # ---------------- 结果对象 ----------------
    result = {
        "mode": mode,
        "generated_utc": now,
        "oracle_sha256": sha256_file(os.path.join(HERE, "oracle.md")),
        "verdict": verdict,
        "industry_face": industry_face,
        "c_table_adopted": c_table_adopted,
        "blocked_reasons": blocked,
        "source_line_checks": source_checks,
        "j1_1_owner_unlock": j1_1,
        "j1_2_stations": j1_2,
        "j1_3_l241": j1_3,
        "j3_1_language_face": j3_1,
        "j3_2_cross_language_values": j3_2,
        "j4_g3": g3,
        "sha_chain": sha_chain,
        "attempt04_usable_for": attempt04_usable,
        "attempt04_not_usable_for": attempt04_forbidden,
        "attempt04_a4b_evidence": a4b_evidence,
        "document_type_measured": extract["document_type"],
        "attempt04_segment_identity": seg_identity,
        "attempt07": a07,
        "origin": origin,
        "hk_parameters_released": False,
        "placeholder_maintained": True,
        "mutations_applied": mut_notes,
        "quotes": quotes,
    }

    dump_json(os.path.join(WORK, "measure_%s.json" % mode), result)

    # ---------------- 与冻结期望比对 → rc ----------------
    rc = 0
    expect_met = True
    detail = {}
    if mode == "baseline":
        expect = {
            "verdict_PASS": verdict == "PASS",
            "c_table_adopted": c_table_adopted is True,
            "attempt04_tier1_ok": src_cond["attempt04"]["tier_1_ok"],
            "attempt08_tier1_ok": src_cond["attempt08"]["tier_1_ok"],
            "attempt07_not_admissible": a07["industry_admissible"] is False,
            "origin_excluded": origin["excluded"] and origin["level"] is None,
            "g3_adopted_B": g3["adopted"].startswith("B"),
            "hk_false": result["hk_parameters_released"] is False,
        }
        expect_met = all(expect.values())
        detail = expect
    elif mode == "m1_weak":
        expect_met = a07["industry_admissible"] is True and verdict == "PASS"
        detail = {"should_pass_flip": a07["industry_admissible"], "verdict": verdict}
    elif mode == "m2_origin":
        expect_met = origin["graded"] is True and origin["level"] is not None and verdict == "PASS"
        detail = {"origin_grade_flip": origin["graded"], "level": origin["level"]}
    elif mode == "m3_nourl":
        expect_met = verdict == "blocked"
        detail = {"verdict": verdict, "reasons": blocked}
    elif mode == "m4_noseg":
        expect_met = verdict == "blocked" and c_table_adopted is False
        detail = {"verdict": verdict, "c_table_adopted": c_table_adopted}
    elif mode == "m5_langconflict":
        expect_met = verdict == "blocked" and n_conflict > 0
        detail = {"verdict": verdict, "conflicts": n_conflict, "pairs": pairs}

    if verdict == "blocked" and mode in ("m3_nourl", "m4_noseg", "m5_langconflict"):
        rc = 2 if expect_met else 3
    elif not expect_met:
        rc = 3
    else:
        rc = 0

    dump_json(os.path.join(WORK, "expect_%s.json" % mode),
              {"mode": mode, "rc": rc, "expectation_met": expect_met, "detail": detail})

    # ---------------- baseline：写 ind_ruling.json ----------------
    if mode == "baseline":
        ruling = build_ruling(result, quotes, now)
        dump_json(os.path.join(HERE, "ind_ruling.json"), ruling)
        print("wrote ind_ruling.json")

    print(json.dumps({"mode": mode, "verdict": verdict, "c_table_adopted": c_table_adopted,
                      "rc": rc, "expect_met": expect_met,
                      "equal_pairs": n_equal, "conflicts": n_conflict}, ensure_ascii=False))
    return rc


def build_ruling(res, quotes, now):
    """四点逐条 + 依据 + C 表登记 + 与会计面衔接。"""
    src = res["j1_3_l241"]["per_source"]
    accounting_levels = {
        "attempt04": {"c_table": "① + ④", "e_level": "E1", "s_tier": "S1",
                      "usable_faces": ["zh-Hant"], "admissible": True,
                      "document_type": "全年业绩公告（results announcement，非年度报告）", "period": "FY2025"},
        "attempt08": {"c_table": "① + ④", "e_level": "E1", "s_tier": "S1",
                      "usable_faces": ["en"], "admissible": True,
                      "document_type": "年度报告英文版（annual report, EN）", "period": "FY2025"},
        "attempt07": {"c_table": "③", "e_level": "E3", "s_tier": "S0",
                      "usable_faces": [], "admissible": False,
                      "document_type": "third_party_proxy_render", "period": "FY2025"},
    }
    industry_confirm = {
        "attempt04": {"confirmed": src["attempt04"]["tier_1_ok"], "c_table_adopted": "① + ④",
                      "evidence_class": "company_primary_disclosure",
                      "industry_scope_note": "同期间发行人原文披露；①④叠加（①=来源级别，④=取回路径外部身份）",
                      "must_label": ["document_type=全年业绩公告（非年度报告）", "period=FY2025",
                                     "period_mismatch_risk=false", "external_retrieval_not_local=true",
                                     "language_face=zh-Hant"]},
        "attempt08": {"confirmed": src["attempt08"]["tier_1_ok"], "c_table_adopted": "① + ④",
                      "evidence_class": "company_primary_disclosure",
                      "industry_scope_note": "年报本体英文版；①④叠加；语言面仅 en（中文锚词0/5）",
                      "must_label": ["document_type=年度报告英文版", "period=FY2025",
                                     "period_mismatch_risk=false", "external_retrieval_not_local=true",
                                     "language_face=en"]},
        "attempt07": {"confirmed": not res["attempt07"]["industry_admissible"], "c_table_adopted": "③",
                      "evidence_class": "secondary_lead_only",
                      "industry_scope_note": "第三方代理渲染件，且正文中文锚词 0/5（不可读）⇒ 双重不可采",
                      "must_label": ["document_type=third_party_proxy_render",
                                     "external_retrieval_not_local=true", "lead_only=true"]},
        "HK-XIAOMI-AR2025 (origin)": {"confirmed": None, "c_table_adopted": None,
                                      "evidence_class": None,
                                      "industry_scope_note": "排除在定级外（S4 NOT_USABLE + L165），不赋级",
                                      "must_label": ["graded=false", "level=null", "admissible=false"]},
    }

    points = [
        {
            "id": "P1",
            "topic": "C 表是否启用（IND L240/L241 裁定权在行业面）+ attempt04/08/07 定级会签",
            "verdict": "启用（限定效力范围）；三件来源定级逐条会签：attempt04 承认 ①+④、attempt08 承认 ①+④、attempt07 承认 ③（= 不可采）",
            "c_table_adopted": res["c_table_adopted"],
            "conditions": {
                "J1-1_owner_unlock": res["j1_1_owner_unlock"]["ok"],
                "J1-2_S3_S4_done": res["j1_2_stations"]["ok"],
                "J1-3_L241_antecedent": res["j1_3_l241"]["l241_antecedent_met"],
                "J1-4_L240_reading": res["j1_3_l241"]["reading"],
            },
            "basis_verbatim": {
                "IND_L240": quotes["IND_L240"],
                "IND_L241": quotes["IND_L241"],
                "IND_L227": quotes["IND_L227"],
                "IND_L231": quotes["IND_L231"],
                "IND_L233": quotes["IND_L233"],
                "IND_L234": quotes["IND_L234"],
            },
            "measured": {
                "attempt04_1_conditions": res["j1_3_l241"]["per_source"]["attempt04"],
                "attempt08_1_conditions": res["j1_3_l241"]["per_source"]["attempt08"],
                "attempt07": res["attempt07"],
                "s3_s4": res["j1_2_stations"],
            },
            "scope_limits": [
                "仅解除 IND B-1 中「①类替代件缺位 ⇒ 零产出」那一层；B-3（不接受二手补位）/ B-4（不接受行业常识补位）继续有效",
                "origin 本体不因启用而可引用（L165 + S4 NOT_USABLE 维持）",
                "参数不放行（L166「通过后才谈」+ L179 + ENVOWNER §⑦）",
                "④ 标记的件永不冒充本地原件/origin",
            ],
            "reading_divergence": {
                "adopted": "α",
                "alpha": "L240 的『读不出原文』= 新 attempt 产不出任何可读原文文本 ⇒ 实测 S3 路径 A 5/5 + 两件①替代件可读 ⇒ 不成立",
                "beta_not_adopted": "『原文』仅指 origin 本体字节（B1 仍 0/5、U1 NOT_USABLE）⇒ 若采 β 则 C 表不启用",
                "why_alpha": "IND L227 明写 C 表是『替代来源……供 owner 解锁后使用』；β 会使替代来源表永无适用场景，与表自身用途矛盾；L241 用『出现①类可读原文』措辞，开关挂在替代件上",
                "registered_for_owner": "该解释分歧显式登记给 owner/编排层；无论采 α 还是 β，hk_parameters_released 均保持 false、origin 均保持排除",
            },
        },
        {
            "id": "P2",
            "topic": "attempt04 文件类型用途（全年业绩公告 FY2025，非年报）",
            "verdict": "承认其为同期间公司原文披露，但用途按内容清单裁：可用 A1/A2/A3/A4a/A5a/A6b；不可用 A4b/A5b/A6a/A7",
            "measured_document_type": res["document_type_measured"],
            "usable_for": res["attempt04_usable_for"],
            "not_usable_for": res["attempt04_not_usable_for"],
            "a4b_evidence": res["attempt04_a4b_evidence"],
            "must_label": ["document_type=全年业绩公告（results announcement，非年度报告）",
                           "period=FY2025", "publication=2026-03-24（早于年报 2026-04-28）",
                           "external_retrieval_not_local=true", "language_face=zh-Hant"],
            "basis": [
                "IND L231 ① 明列『全年业绩公告』为①类来源，但要求『必须标注文件类型与期间』",
                "自抽实测：标题逐字『截至2025年12月31日止年度之全年業績公告』；『年度報告』锚 0 命中；59 页 vs 年报 415 页",
                "自抽实测：分部资料及收入附注在 p49（分部收入/销售成本/毛利 + 總計列），p50 地区收入 + 可报告分部存货",
                "自抽实测：核數師報告 0 命中、無保留意見 0 命中；僅有『經審核合併業績』自述与核數師『數字一致』程序",
                "自抽实测：財務摘要 0 命中（『五年』4 次命中均为营销表述『五年排名全球前三』）",
            ],
            "arithmetic_identity_check": res["attempt04_segment_identity"],
        },
        {
            "id": "P3",
            "topic": "attempt08 英文面在港股命题中的可用范围（中文锚词 0/5）",
            "verdict": "承认会计面 usable=[\"en\"]；英文面可用于数值型/年报本体命题，禁止用于中文原文逐字与中文锚词类命题",
            "measured": res["j3_1_language_face"],
            "cross_language_check": res["j3_2_cross_language_values"],
            "usable_scope": [
                "需要年报本体页/表定位的命题（五年财务摘要、审计意见、分部附注在 EN 年报中均可定位）",
                "数值型港股份部命题（收入/毛利/占比/增速）——须标 language_face=en 并用英文原文逐字引文",
                "与 attempt04 中文件的数值交叉验证（本工位实测 6 对共享数值，equal=%d / conflict=%d）"
                % (res["j3_2_cross_language_values"]["equal"], res["j3_2_cross_language_values"]["conflict"]),
            ],
            "prohibited": [
                "任何要求中文原文逐字引文 / 中文锚词命中的命题（中文 0/5）",
                "任何『中文年报原文已核』的口径声明",
                "翻译敏感的定义性表述（分部名称、会计政策措辞）未经 attempt04 中文件对照单独成立",
                "英文面冒充中文面（与④『永不冒充本地』同构：en 面不得冒充 zh 原文面）",
            ],
            "basis_verbatim": {"IND_L231": quotes["IND_L231"], "ENVOWNER_L179": quotes["ENVOWNER_L179"]},
        },
        {
            "id": "P4",
            "topic": "G3 口径会签（会计 true vs PEND-5a/S3 false）",
            "verdict": "按 IND L234/L360 裁口径 B（external_retrieval_not_local=true）为准；两边都不回改，只登记分歧",
            "measured": res["j4_g3"],
            "basis_verbatim": {"IND_L234": quotes["IND_L234"], "IND_L360": quotes["IND_L360"],
                               "IND_L261": quotes["IND_L261"]},
            "both_sides_back_written": False,
            "divergence_registered": "口径 A（false=非第三方代理，PEND-5a ext-04/ext-08 + S3 in-02/in-03）vs 口径 B（true=外部取回件永不冒充本地，④/OPEN-11 L360/S4 own_provenance）；本工位采 B",
        },
    ]

    return {
        "card": "OPEN-5",
        "step": "S5（行业半区 · 行业复裁）",
        "attempt": "OPEN5-S5-IND-RULING/a20260926-01",
        "role": "industry_reviewer_s5",
        "generated_utc": now,
        "oracle": {"file": "oracle.md", "sha256": res["oracle_sha256"],
                   "frozen_before_judging": True, "modified_by_this_round": False},
        "authorization": {
            "S5_definition_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L166",
                "quote": quotes["ENVOWNER_L166"].strip(),
            },
            "boundary_verbatim": {"source": "同文件 L179", "quote": quotes["ENVOWNER_L179"].strip()},
            "owner_rule_verbatim": {"source": "OWNER_DECISIONS.md L504", "quote": quotes["OWNER_L504"].strip()},
            "owner_authorization_for_retrieval": res["j1_1_owner_unlock"]["authorized_by_verbatim"],
        },
        "points": points,
        "c_table_adopted": res["c_table_adopted"],
        "c_table_registration": {
            "rule": "IND C 表（I11A-OPEN-IND L227–L234）+ oracle §4.5",
            "attempt04": "① + ④",
            "attempt08": "① + ④",
            "attempt07": "③（仅线索，不可采）",
            "attempt02_or_regulator_rows": "② 本轮零登记",
            "origin": "不登记（排除在定级外）",
        },
        "attempt_levels_confirmed": {
            "source_of_levels": "会计面 OPEN5-S5-ACCT-GRADING/a20260926-01（证据等级由会计面认定，本工位只读引用、不改）",
            "accounting_levels": accounting_levels,
            "industry_confirmation": industry_confirm,
            "all_three_confirmed": bool(src["attempt04"]["tier_1_ok"] and src["attempt08"]["tier_1_ok"]
                                        and not res["attempt07"]["industry_admissible"]),
        },
        "accounting_face_linkage": {
            "agreed": [
                "attempt04 = ①+④ / E1 / S1 / usable=[zh-Hant]（行业面承认来源等级与语言面）",
                "attempt08 = ①+④ / E1 / S1 / usable=[en]（行业面承认，并加英文面用途限制）",
                "attempt07 = ③ / E3 / S0 不可采（行业面承认，并加『正文 0/5 不可读』的第二条不可采理由）",
                "origin 排除在定级外（level=null）",
                "G3 按④裁 true（与会计半区 §1.2 判定一致）",
                "hk_parameters_released=false（与会计半区 §4 结论一致）",
            ],
            "divergences": [
                "无实质分歧；行业面在会计面等级之上**追加用途/语言面限制**（更严，非更松）："
                "attempt04 禁 A4b/A5b/A6a/A7；attempt08 禁中文原文面；attempt07 增列『不可读』为第二条不可采理由",
                "解释分歧登记：C 表启用的 L240/L241 读法（α/β）由行业面采 α 并显式登记 β（会计面 §6-2 明文留待行业面裁）",
            ],
            "not_signed_for_accounting": [
                "未改 E1/E3/S1/S0、未改 usable_faces、未改 admissible、未重做会计四步",
                "未回改会计半区任何字节（sha 见 read_only_attestation）",
            ],
        },
        "s4_read_only": {
            "consistency_result": res["origin"]["s4_consistency_result"],
            "changed_by_this_station": False,
            "numeric_conflict_changed": False,
            "used_as": "U2/U3 = CONSISTENT 作 E1f 路径①引用；U1 = NOT_USABLE 只读接受",
        },
        "origin": res["origin"],
        "hk_parameters_released": False,
        "placeholder_maintained": True,
        "low_base_high": [None, None, None],
        "open5_released": False,
        "accept_produced": False,
        "releases_nothing": True,
        "industry_face_status": res["industry_face"],
        "fail_condition": "任一面未过 ⇒ 港股参数继续 _PLACEHOLDER（本次两面均过 ⇒ 只是『可谈』，仍不放行）",
        "mutations": {
            "script": "_work/s5_ind_grade.py",
            "modes": ["baseline", "m1_weak", "m2_origin", "m3_nourl", "m4_noseg", "m5_langconflict"],
            "results": "见 _work/expect_*.json 与 s5_ind_report.md §红绿变异",
        },
        "read_only_attestation": {
            "inputs": ["IN-01 ENVOWNER ruling", "IN-02 IND ruling", "IN-03 会计半区交付", "IN-04 S4",
                       "IN-05 S3 provenance", "IN-06 PEND-5a", "IN-07 corpus 字节", "IN-08 S3 report",
                       "IN-09 OWNER_DECISIONS", "IN-10 本工位自抽工件"],
            "sha256": {
                "acct_grading.json": sha256_file(os.path.join(ACCT_DIR, "acct_grading.json")),
                "s5_acct_report.md": sha256_file(os.path.join(ACCT_DIR, "s5_acct_report.md")),
                "acct_handoff.json": sha256_file(os.path.join(ACCT_DIR, "handoff.json")),
                "s4_dual_path_verify.json": sha256_file(os.path.join(S4_DIR, "dual_path_verify.json")),
                "s4_s4_report.md": sha256_file(os.path.join(S4_DIR, "s4_report.md")),
                "s3_provenance.json": sha256_file(S3_PROV),
                "pend5a_provenance.json": sha256_file(os.path.join(PEND5A, "provenance.json")),
                "attempt04_pdf": sha256_file(os.path.join(CORPUS, "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf")),
                "attempt08_pdf": sha256_file(os.path.join(CORPUS, "attempt08_irmi_xiaomi_ar2025_en.pdf")),
            },
            "back_written_to_prior_stations": False,
        },
        "network_used": False,
        "git_write_ops": 0,
        "git_status_used": False,
        "writes_outside_planning": 0,
    }


if __name__ == "__main__":
    sys.exit(main())
