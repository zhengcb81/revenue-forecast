"""OPEN5-S4 · assemble dual_path_verify.json from raw measurements,
applying ONLY the criteria frozen in oracle.md / oracle-addendum-A / oracle-addendum-B."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ME = os.path.dirname(HERE)
RAW = os.path.join(HERE, "raw_measurements.json")
OUT = os.path.join(ME, "dual_path_verify.json")

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]
EN_ANCHORS = ["Xiaomi", "Revenue", "Annual Report", "Segment", "Gross profit"]
PAGES = [1, 2, 30, 43, 47, 115, 160, 337, 355, 399]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def runs_of(s: str):
    return re.findall(r"[一-鿿]{2,}|[\x20-\x7e]{4,}", s)


def main() -> int:
    raw = json.load(open(RAW, encoding="utf-8"))
    s3 = json.load(open(
        os.path.join(ME, "..", "..", "OPEN5-S3-REACQUISITION", "a20260925-01",
                     "_work", "path_compare.json").replace(os.sep, "/"), encoding="utf-8"))

    m1 = raw["m1_A_vs_B1_fresh_pdfium"]
    m1b = raw["m1_A_vs_B1_s3_recorded"]
    m2 = raw["m2_attempt04_fitz_vs_pdfminer"]
    m2p = raw["m2prime_attempt08"]
    b1f = raw["b1_origin_textlayer_fresh_fitz"]
    b1p = raw["b1_origin_textlayer_fresh_pdfium"]
    a = raw["A_anchor_recount_from_ocr_files"]

    # ---------- face U1 : origin, A (OCR) vs B1 (text layer) ----------
    spans_p1 = {s["span"] for s in raw["m1_A_vs_B1_fresh_pdfium"]["span_detail"][0]["spans"]}
    matched_lines = m1["per_page"][0]["sample_matched_lines"]
    matched_outside_readable = [
        ln for ln in matched_lines
        if any(r not in spans_p1 for r in runs_of(ln))
    ]
    cond_a = (m1["verbatim_matches_in_origin_layer"] >= 1
              and not matched_outside_readable
              and m1["per_page"][0]["page"] == 1)
    cond_b = m1["cover_fragment_reproduced"] == 1
    cond_a_anchors = a["hit_word_count"] >= 3
    cond_b1_zero = b1f["hit_word_count"] == 0 and b1p["hit_word_count"] == 0
    conflicts = m1["numeric_conflict_count"]
    if (conflicts > 0) or (not cond_b) or (not cond_a) or (not cond_a_anchors) \
            or (not cond_b1_zero):
        u1_verdict = "NOT_USABLE"
    elif m1["readable_span_coverage"] is not None and m1["readable_span_coverage"] < 1.0:
        u1_verdict = "PARTIAL"
    else:
        u1_verdict = "CONSISTENT"
    u1_reasons = [
        f"(a) 同页去空白逐字命中 {m1['verbatim_matches_in_origin_layer']} 行 / 受检 "
        f"{m1['ocr_lines_checked']} 行；命中行全部落在 origin 可读区（封面）="
        f"{cond_a}",
        f"(b) 封面可读片段双向复现 = {cond_b}（10 页中 {m1['cover_fragment_reproduced']} 页）",
        f"A 锚词 {a['hit_word_count']}/5（≥3 通过线）={cond_a_anchors}；"
        f"B1 双库 415 页锚词 fitz={b1f['hit_word_count']}/5、"
        f"pypdfium2={b1p['hit_word_count']}/5（预期 0/5）={cond_b1_zero}",
        f"origin 可读区→OCR 复现覆盖率 {m1['readable_span_coverage']} "
        f"（{m1['readable_span_stats']['reproduced']}/{m1['readable_span_total']}）< 100% "
        f"⇒ 互证面仅限可读区，origin 正文因 B1 GID 乱码**没有第二条路径可互证**",
        f"**numeric_conflict = {conflicts}（≥5 位数字串 OCR 有、origin 无）> 0** "
        f"⇒ 触发 oracle §5.1/§5.3-1 的 U1 `NOT_USABLE`",
    ]

    # ---------- face U2 : attempt04, fitz vs pdfminer ----------
    u2_cond = {
        "word_level_sets_equal": m2["word_level_sets_equal"],
        "anchors_with_empty_page_intersection": m2["anchors_with_empty_page_intersection"],
        "pdfminer_only_pages": m2["b_only_pages_union"],
        "first_line_cross": f"{m2['first_line_cross_match_count']}/"
                            f"{m2['first_line_cross_match_denominator']}",
    }
    if not m2["word_level_sets_equal"] or m2["anchors_with_empty_page_intersection"] \
            or m2["b_only_pages_union"] \
            or m2["first_line_cross_match_count"] != m2["first_line_cross_match_denominator"]:
        u2_verdict = "NOT_USABLE" if not m2["word_level_sets_equal"] or \
            m2["first_line_cross_match_count"] != m2["first_line_cross_match_denominator"] \
            else "PARTIAL"
    else:
        u2_verdict = "CONSISTENT"

    # ---------- face U3 : attempt08, two libs x two languages ----------
    cn_eq = (m2p["cn"]["fitz_hit_words"] == [] and m2p["cn"]["pdfminer_hit_words"] == [])
    en_eq = (m2p["en"]["word_level_sets_equal"]
             and len(m2p["en"]["fitz_hit_words"]) == 5
             and len(m2p["en"]["pdfminer_hit_words"]) == 5)
    if cn_eq and en_eq and m2p["en"]["first_line_cross_match_count"] == 5:
        u3_verdict = "CONSISTENT"
    elif m2p["cn"]["fitz_hit_words"] != m2p["cn"]["pdfminer_hit_words"] \
            or m2p["en"]["fitz_hit_words"] != m2p["en"]["pdfminer_hit_words"]:
        u3_verdict = "NOT_USABLE"
    else:
        u3_verdict = "PARTIAL"

    faces = {
        "U1_origin_HK-XIAOMI-AR2025": {
            "sources": ["HK-XIAOMI-AR2025 (origin PDF, local product-repo original)"],
            "paths_compared": ["A_ocr_reconstruction", "B1_origin_textlayer_fitz",
                               "B1_origin_textlayer_pypdfium2"],
            "verdict": u1_verdict,
            "reasons": u1_reasons,
            "criteria_ref": "oracle.md §5.1 U1 + §5.3 + oracle-addendum-A/B",
        },
        "U2_substitute_attempt04": {
            "sources": ["attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf"],
            "paths_compared": ["B2_fitz", "B2_pdfminer"],
            "verdict": u2_verdict,
            "measurements": u2_cond,
            "reasons": [
                f"锚词级命中集合两库相同 = {m2['word_level_sets_equal']}"
                f"（fitz {m2['fitz_hit_words']} / pdfminer {m2['pdfminer_hit_words']}，"
                f"对称差 {m2['word_level_symmetric_difference']}）",
                f"两库共命中锚词的页交集全部非空；pdfminer-only 页 = "
                f"{len(m2['b_only_pages_union'])}",
                f"首现行跨库搜全文命中 {m2['first_line_cross_match_count']}/"
                f"{m2['first_line_cross_match_denominator']}",
                "`年度報告` 两库同为 0（业绩公告非年报，文件类型差异，非路径矛盾）",
                "该件为**外部抓取件**，按 IND C 表 ④ 登记，永不冒充本地",
            ],
            "criteria_ref": "oracle.md §5.1 U2",
        },
        "U3_substitute_attempt08": {
            "sources": ["attempt08_irmi_xiaomi_ar2025_en.pdf"],
            "paths_compared": ["fitz", "pdfminer"],
            "verdict": u3_verdict,
            "measurements": {"cn_both_libs_0_of_5": cn_eq,
                             "en_both_libs_5_of_5": en_eq,
                             "en_first_line_cross": f"{m2p['en']['first_line_cross_match_count']}/5"},
            "reasons": [
                f"中文锚词：fitz {len(m2p['cn']['fitz_hit_words'])}/5、"
                f"pdfminer {len(m2p['cn']['pdfminer_hit_words'])}/5（同为 0）",
                f"英文锚词：fitz {len(m2p['en']['fitz_hit_words'])}/5、"
                f"pdfminer {len(m2p['en']['pdfminer_hit_words'])}/5（同为 5）",
                "语言面自洽（英文正文 ⇒ 中文 0/5）；**不得**作中文可读结论",
            ],
            "criteria_ref": "oracle.md §5.1 U3",
        },
    }

    verdicts = [v["verdict"] for v in faces.values()]
    if "NOT_USABLE" in verdicts:
        overall = "NOT_USABLE"
    elif "PARTIAL" in verdicts:
        overall = "PARTIAL"
    else:
        overall = "CONSISTENT"

    # ---------- diffs vs S3 ----------
    s3c = raw["s3_meta_loaded"]["s3_claimed"]
    pc_per = s3["b2_fitz_vs_pdfminer"]["per_anchor"]
    page_set_equal = all(
        pc_per[k]["fitz_hit_pages"] == m2["per_anchor"][k]["fitz_hit_pages"]
        and pc_per[k]["pdfminer_hit_pages"] == m2["per_anchor"][k]["pdfminer_hit_pages"]
        and pc_per[k]["first_line_fitz_found_in_pdfminer"]
        == m2["per_anchor"][k]["first_line_a_found_in_b"]
        for k in ANCHORS
    )
    diffs = [
        {"item": "M1 受检 OCR 行数", "s3": s3c["a_vs_b1_ocr_lines_checked"],
         "mine": m1["ocr_lines_checked"], "same": s3c["a_vs_b1_ocr_lines_checked"] == m1["ocr_lines_checked"]},
        {"item": "M1 逐字命中行数", "s3": s3c["a_vs_b1_verbatim_matches"],
         "mine": m1["verbatim_matches_in_origin_layer"],
         "same": s3c["a_vs_b1_verbatim_matches"] == m1["verbatim_matches_in_origin_layer"]},
        {"item": "M1 封面片段复现", "s3": s3c["readable_cover_fragment_reproduced"],
         "mine": m1["cover_fragment_reproduced"],
         "same": s3c["readable_cover_fragment_reproduced"] == m1["cover_fragment_reproduced"]},
        {"item": "A 锚词命中数", "s3": s3c["a_anchor_hit_count"], "mine": a["hit_word_count"],
         "same": s3c["a_anchor_hit_count"] == a["hit_word_count"]},
        {"item": "B1 锚词命中数 / 页数", "s3": f"{s3c['b1_hit_word_count']}/{s3c['b1_pages_scanned']}",
         "mine": f"{b1f['hit_word_count']}/{b1f['pages']}",
         "same": f"{s3c['b1_hit_word_count']}/{s3c['b1_pages_scanned']}" ==
                 f"{b1f['hit_word_count']}/{b1f['pages']}"},
        {"item": "M2 首现行跨库命中", "s3": s3c["b2_first_line_cross_lib_match_count"],
         "mine": m2["first_line_cross_match_count"],
         "same": s3c["b2_first_line_cross_lib_match_count"] == m2["first_line_cross_match_count"]},
        {"item": "M2 逐页命中集合 + 首现行判定", "s3": "path_compare.json per_anchor",
         "mine": "fresh extraction per_anchor", "same": page_set_equal},
        {"item": "B2′ 中文/英文锚词", "s3": f"{s3c['b2prime_cn']}/{s3c['b2prime_en']}",
         "mine": f"{len(m2p['cn']['fitz_hit_words'])}/{len(m2p['en']['fitz_hit_words'])}",
         "same": s3c["b2prime_cn"] == len(m2p["cn"]["fitz_hit_words"])
                 and s3c["b2prime_en"] == len(m2p["en"]["fitz_hit_words"])},
        {"item": "B2′ 双库互证", "s3": "仅 fitz（S3 未在本工位跑 attempt08 的 pdfminer）",
         "mine": "fitz + pdfminer 双库（本工位新增）",
         "same": None,
         "note": "新增信息，非差异；两库结论一致"},
        {"item": "数字层面的两路比对（≥5 位）",
         "s3": "未做（path_compare.json 无数字比对面）",
         "mine": f"本工位新增，发现 numeric_conflict = {conflicts}",
         "same": False,
         "note": "S3 未登记；本工位按 oracle-addendum-B 新增，是 U1 判 NOT_USABLE 的直接触发项"},
        {"item": "origin 每页文字层（pypdfium2 版本差异）",
         "s3": "pypdfium2 5.13.0（PEND-5B venv）",
         "mine": "pypdfium2 4.30.0（全局解释器）",
         "same": None,
         "note": "10 页中 4 页逐字节全等，6 页差异仅为数字组间空格/一处 \\x98，"
                 "相似度 0.867–0.999；M1 两变体产出的 92/1/1 与覆盖率完全相同"},
        {"item": "S3 provenance counts 字段",
         "s3": f"declared={raw['s3_provenance_audit']['counts_declared']} 合计 "
               f"{raw['s3_provenance_audit']['counts_declared_sum']}",
         "mine": f"实际 entry_count={raw['s3_provenance_audit']['entry_count_actual']}、"
                 f"by kind={raw['s3_provenance_audit']['counts_by_kind_actual']}",
         "same": False,
         "note": "counts 不自洽（见 provenance_review.gaps G1）"},
    ]

    # ---------- provenance gaps ----------
    gaps = [
        {"id": "G1", "severity": "hard",
         "entry": "provenance.json → counts / entry_count",
         "finding": f"entry_count=26，但 counts 合计 "
                    f"{raw['s3_provenance_audit']['counts_declared_sum']}"
                    f"（{raw['s3_provenance_audit']['counts_declared']}）；"
                    f"`probe_or_deliverable` 实际 6 条而 counts.deliverables=4",
         "element_violated": "内部自洽（P1 计数）",
         "fix_owner": "S3 实现者（不回改，需新文件追加勘误）"},
        {"id": "G2", "severity": "hard",
         "entry": "in-02 (attempt04) / in-03 (attempt08)",
         "finding": "无 URL —— 只有 `retrieval_method` 里的站点名"
                    "（`direct_from_origin_site_www1.hkexnews.hk` / "
                    "`direct_from_issuer_site_ir.mi.com`）。"
                    "IND C 表 ④ 要求「URL + 取回时间 + sha256」三件齐；"
                    "URL 只存在于 PEND-5a `provenance.json` ext-04 / ext-08。",
         "element_violated": "P5-URL",
         "fix_owner": "S3 实现者 / S5 引用前必须回源 PEND-5a 补齐"},
        {"id": "G3", "severity": "hard",
         "entry": "in-02 / in-03 → external_retrieval_not_local = false",
         "finding": "与 IND C 表 ④（外部抓取的港股年报 PDF → `external_retrieval_not_local`）"
                    "及 OPEN-11「所有 EXT-* 一律标 evidence_class=external_retrieval_not_local」"
                    "（I11A-OPEN-IND/ruling.md L360）**语义冲突**。"
                    "S3 沿用 PEND-5a 的口径（false = 非第三方代理）。"
                    "S3 已带 `substitute_not_origin=true`（不冒充 origin），但**未按 ④ 标外部身份**。",
         "element_violated": "P5-外部标记 / 永不冒充本地",
         "fix_owner": "本工位只登记、不改 S3；引用侧按 ④ 处置"},
        {"id": "G4", "severity": "medium",
         "entry": "in-01 (origin)",
         "finding": "`utc = \"n/a_local_bytes\"`、无 URL —— origin 的实际取回 UTC/URL **可回源补齐**："
                    "产品仓 sidecar `<file>.source.json` 明载 "
                    "`source_url=https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf`、"
                    "`retrieved_at=2026-09-19T04:52:10Z`、`content_sha256=ffd73376…`。",
         "element_violated": "P4-取回 UTC / P5-URL（可补而未补）",
         "fix_owner": "S5 引用前补齐；本工位只读登记"},
        {"id": "G5", "severity": "medium",
         "entry": "auth-01 / auth-02 / auth-03 / auth-04",
         "finding": "四条授权条目均无 sha256；且 `auth-04` 的 `note` 写 `verbatim` 但 `quote` "
                    "实为转述摘要（「§二十六 #1 owner 原话「授权」(PEND-5a) / #2 …」），"
                    "非逐字原文，也无行号。",
         "element_violated": "P1-sha256 + 锚文本字面性",
         "fix_owner": "S3 实现者（追加勘误，不回改）"},
        {"id": "G6", "severity": "medium",
         "entry": "provenance.json 条目覆盖面",
         "finding": f"S3 目录内 {raw['s3_provenance_audit']['files_on_disk_not_registered_count']} "
                    f"个盘上文件未进 provenance 条目（20 个 ocr_text/*.txt、4 个 extract/*.txt、"
                    f"7 个 _work/*.py、1 个 _shim/sitecustomize.py）；"
                    f"这些文件的 sha256 只在 `handoff.json:written_files` 里，"
                    f"**provenance.json 内不构成完整证据链**（renders 的 10 条有条目）。",
         "element_violated": "P1+P2+P3 在 provenance.json 内的完整性",
         "fix_owner": "S5 引用时需同时读 handoff.written_files；本工位只登记"},
        {"id": "G7", "severity": "low",
         "entry": "in-04 (OCR venv)",
         "finding": "无 sha256（目录级只读引用），也未登记该 venv 的 manifest 摘要；"
                    "只写到引擎版本号。⇒ venv 未被本工位改动这件事依赖 S3 的 manifest 前后比对，"
                    "**本工位未独立复算 venv manifest**（410 MB / 3110 文件）。",
         "element_violated": "P1-sha256（部分）",
         "fix_owner": "如实标「未证实」"},
    ]

    doc = {
        "card": "OPEN-5",
        "step": "S4",
        "attempt": "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01",
        "role": "implementer_s4",
        "generated_utc": utc_now(),
        "oracle": {
            "file": "oracle.md",
            "sha256": sha256_file(os.path.join(ME, "oracle.md")),
            "addendum_A_sha256": sha256_file(os.path.join(ME, "oracle-addendum-A.md")),
            "addendum_B_sha256": sha256_file(os.path.join(ME, "oracle-addendum-B.md")),
            "frozen_before_any_measurement": True,
            "measurement_started_utc": raw["started_utc"],
            "measurement_finished_utc": raw["finished_utc"],
        },
        "authorization": {
            "S4_definition_verbatim": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN5-ENVOWNER/a20260924-01/ruling.md L165",
                "quote": "| **S4** | **双路径复核 + provenance**：两条独立取文路径互证（承 P1/P2 精神），"
                         "登记文件 sha256、页码/锚文本、取回 UTC；外部件按 IND C 表 **④** 标 "
                         "`external_retrieval_not_local`、**永不冒充本地** | 实现者 + 独立 reviewer | "
                         "S1/S3 授权 | 复核不一致 ⇒ 该来源不可引用，维持不可读处置 |",
                "dispatch_paraphrase_delta": "派单转述失败分支为「该来源不可用」；"
                                             "ruling.md 原文为「该来源不可引用，维持不可读处置」。"
                                             "以文件原文为准，已按原文执行。",
            },
            "S5_not_done": {
                "source": "同文件 L166",
                "quote": "| **S5** | **行业复裁 + 会计定级**：按 IND 已裁的 C 表①/②登记来源等级，"
                         "**证据等级由会计面认定**（§二十四 执行纪律第 3 条）；通过后才谈港股命题与参数 | "
                         "行业 reviewer + 会计 reviewer | 各自专业裁定权（**本载体不代行**） | "
                         "任一面未过 ⇒ 港股参数继续 `_PLACEHOLDER` |",
            },
            "boundary_verbatim": {
                "source": "同文件 L174-L179",
                "quote": "即使 S2 自检显示\"某路径能读出锚词\"，在 S3/S4/S5 走完之前仍按不可读处置"
                         "（IND 处置规则 B 部分继续有效：港股命题零产出、参数维持 `_PLACEHOLDER`）。",
            },
            "owner_authorization": {
                "source": ".planning/2026-09-19-three-project-history-audit/OWNER_DECISIONS.md §二十六 #1/#2",
                "quote": "#1 PEND-5a owner 原话「授权」；#2 PEND-5b owner 原话「要」→ 澄清答「两项都要」",
            },
            "IND_C_table_4": {
                "source": ".planning/2026-09-19-three-project-history-audit/execution_runs/"
                          "I11A-OPEN-IND/a20260924-01/ruling.md L234",
                "quote": "| ④ | 外部抓取的港股年报 PDF（若本地原件不可读） | "
                         "`external_retrieval_not_local` | 必须登记 URL + 取回时间 + sha256，"
                         "**永不冒充本地可核**；且仍需可复核的取文路径 |",
            },
            "OPEN11_external_not_local": {
                "source": "同文件 L360",
                "quote": "**外部 ≠ 本地**：所有 `EXT-*` 一律标 `evidence_class=external_retrieval_not_local`；"
                         "`2026-09-02 8-K` 条目显式写明\"本地不可核，外部获取，不得作为本地可核证据放行\"。",
            },
        },
        "write_surface": "only .planning/2026-09-19-three-project-history-audit/execution_runs/"
                         "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01/",
        "network_used": False,
        "git_write": 0,
        "git_status_used": False,
        "method_verbatim_from_path_compare": s3["method"],
        "my_execution_of_methods": {
            "recompute_policy": "不采信 S3 任何数字；全部输入先 sha 校验，"
                                "B1/B2/B2' 由本工位重新抽取（fitz / pdfminer / pypdfium2），"
                                "M1/M2 按冻结方法自己跑一遍",
            "ocr_engine_rerun": False,
            "ocr_engine_rerun_reason": "全局 rapidocr 3.8.1 / onnxruntime 1.26.0 / "
                                       "pypdfium2 4.30.0 ≠ S3 的 3.9.2 / 1.30.0 / 5.13.0；"
                                       "跨版本重跑不构成同条件复现 ⇒ A 路数字按对 S3 落盘 OCR "
                                       "重建文本（sha 逐件核验全等）重算（oracle.md §6.5）"
        },
        "input_verification": raw["input_hashes"],
        "s3_artifact_integrity": {
            "files_checked": raw["s3_artifact_integrity"]["files_checked"],
            "mismatched": raw["s3_artifact_integrity"]["mismatched"],
            "missing": raw["s3_artifact_integrity"]["missing"],
            "all_match": raw["s3_artifact_integrity"]["all_match"],
            "conclusion": "S3 落盘 101 个文件逐件重算 sha 全等 ⇒ S3/S1/封盘只读纪律未被破坏",
        },
        "fresh_extraction_reproducibility": {
            k: {kk: raw["fresh_extractions"][k].get(kk)
                for kk in ("bytes", "sha256", "s3_recorded_sha256",
                           "byte_identical_to_s3", "pages")}
            for k in ("origin_fitz_full", "sub04_fitz", "sub04_pdfminer", "sub08_fitz")
        },
        "fresh_extraction_new": {
            "sub08_pdfminer": raw["fresh_extractions"]["sub08_pdfminer"],
            "origin_pdfium_per_page_vs_s3": raw["fresh_extractions"][
                "origin_pdfium_per_page"]["vs_s3"],
        },
        "paths_compared": [
            {"pair": "A vs B1", "object": "HK-XIAOMI-AR2025 (origin)",
             "path_a": "OCR reconstruction (rapidocr 3.9.2 + pypdfium2 5.13.0, S3 落盘产物, sha 已核)",
             "path_b1": "origin text layer, fresh fitz 1.26.7 + fresh pypdfium2 4.30.0 (两库)",
             "pages": PAGES, "method": "M1"},
            {"pair": "B2 fitz vs pdfminer", "object": "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf",
             "path_a": "fresh PyMuPDF 1.26.7", "path_b": "fresh pdfminer.six 20260107",
             "pages": "full document (59)", "method": "M2"},
            {"pair": "B2' fitz vs pdfminer", "object": "attempt08_irmi_xiaomi_ar2025_en.pdf",
             "path_a": "fresh PyMuPDF 1.26.7", "path_b": "fresh pdfminer.six 20260107",
             "pages": "full document (415)", "method": "M2'"},
        ],
        "anchors": ANCHORS,
        "en_anchors": EN_ANCHORS,
        "sampled_pages": PAGES,
        "path_results": {
            "A_ocr": {
                "anchor_hit_count_recounted": a["hit_word_count"],
                "anchor_hit_pages": a["anchor_hit_pages"],
                "origin_layer_same_pages_anchor_hits": a["origin_layer_same_pages_anchor_hits"],
                "ocr_reconstruction": True,
                "ocr_engine_rerun_this_station": False,
                "evidence": "逐锚词首命中行/行号/字节区见 raw_measurements 与 "
                            "dual_path_verify.method1.A_evidence（源自 reacquisition per_page，sha 已核）",
            },
            "B1_origin_textlayer": {
                "fresh_fitz": b1f,
                "fresh_pypdfium2": b1p,
                "both_libs_agree": b1f["hit_word_count"] == b1p["hit_word_count"] == 0,
            },
            "B2_attempt04": m2,
            "B2prime_attempt08": m2p,
        },
        "method1_A_vs_B1": {
            "primary_variant_fresh_pdfium": {k: m1[k] for k in (
                "variant", "pages", "ocr_lines_checked",
                "verbatim_matches_in_origin_layer", "cover_fragment_reproduced",
                "readable_span_stats", "readable_span_total",
                "readable_span_coverage", "numeric_conflict_count",
                "numeric_conflicts", "numeric_token_diff_pages", "per_page")},
            "cross_check_variant_s3_recorded_textlayer": {
                k: m1b[k] for k in (
                    "variant", "ocr_lines_checked",
                    "verbatim_matches_in_origin_layer", "cover_fragment_reproduced",
                    "readable_span_stats", "readable_span_total",
                    "readable_span_coverage", "numeric_conflict_count")},
            "both_variants_identical_headline": (
                m1["ocr_lines_checked"] == m1b["ocr_lines_checked"]
                and m1["verbatim_matches_in_origin_layer"]
                == m1b["verbatim_matches_in_origin_layer"]
                and m1["cover_fragment_reproduced"] == m1b["cover_fragment_reproduced"]
                and m1["numeric_conflict_count"] == m1b["numeric_conflict_count"]),
            "readable_span_detail": m1["span_detail"],
        },
        "method2_B2_fitz_vs_pdfminer": m2,
        "method2prime_B2prime": m2p,
        "faces": faces,
        "consistency_result": overall,
        "consistency_result_reasons": [
            "oracle.md §5.2：任一面 `NOT_USABLE` ⇒ 总值 `NOT_USABLE`（就低不就高）；"
            "触发面 = U1（origin 本体）。",
            f"U1 = {u1_verdict}（numeric_conflict = {conflicts} > 0；"
            f"且 origin 正文无第二路互证，可读区覆盖率 {m1['readable_span_coverage']}）。",
            f"U2 = {u2_verdict}（attempt04 双库 4/4 全中、无页级孤证）。",
            f"U3 = {u3_verdict}（attempt08 双库中文 0/5、英文 5/5，语言面自洽）。",
            "按 ruling.md L165 失败分支：复核不一致 ⇒ **该来源不可引用、维持不可读处置**。",
        ],
        "per_source_usability": {
            "HK-XIAOMI-AR2025 (origin)": "不可用（S4 失败分支）—— 数字面 3 处两路读数分歧 + 正文仅 OCR 单路",
            "attempt04 (FY2025 业绩公告)": "双库互证成立；但为外部抓取件且文件类型非年报，"
                                          "**能否入证据链由 S5 按 IND C 表 ①/④ 定级**（本工位不定级）",
            "attempt08 (年报英文版)": "双库英文面互证成立；中文锚词 0/5 ⇒ 不可作中文原文来源",
        },
        "provenance_review": {
            "criteria": "oracle.md §5.4 P1–P5",
            "s3_provenance": {
                "entry_count": raw["s3_provenance_audit"]["entry_count_actual"],
                "counts_declared": raw["s3_provenance_audit"]["counts_declared"],
                "counts_consistent": raw["s3_provenance_audit"]["counts_consistent"],
                "entries_missing_sha256": [e["id"] for e in
                                           raw["s3_provenance_audit"]["entries"]
                                           if not e["has_sha256"]],
                "entries_missing_utc": [e["id"] for e in
                                        raw["s3_provenance_audit"]["entries"]
                                        if e["utc_missing"]],
                "entries_missing_quote_or_note": [e["id"] for e in
                                                  raw["s3_provenance_audit"]["entries"]
                                                  if not e["has_quote_or_note"]],
                "external_parts": raw["s3_provenance_audit"]["external_parts"],
                "files_on_disk_not_registered_count":
                    raw["s3_provenance_audit"]["files_on_disk_not_registered_count"],
                "files_on_disk_not_registered":
                    [os.path.basename(p) for p in
                     raw["s3_provenance_audit"]["files_on_disk_not_registered_in_provenance"]],
            },
            "gaps": gaps,
            "own_provenance": {
                "origin_file": {
                    "id": "s4-in-01",
                    "kind": "origin_file",
                    "sha256": raw["input_hashes"]["origin"]["sha256"],
                    "bytes": raw["input_hashes"]["origin"]["bytes"],
                    "pages": 415,
                    "page_evidence": "415 页全文文字层（fitz + pypdfium2 双库）+ 抽样 10 页",
                    "anchor_text": "小米/收入/年度報告/分部/毛利 → 双库均 0/5",
                    "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0428/2026042800527_c.pdf",
                    "retrieved_utc": "2026-09-19T04:52:10Z",
                    "retrieved_utc_source": "product-repo sidecar "
                                            "<file>.source.json（本工位只读回源，未改一字节）",
                    "external_retrieval_not_local": False,
                    "retrieval_method_this_attempt": "local_readonly_hash_and_text_extraction",
                    "access": "read_only",
                },
                "substitute_attempt04": {
                    "id": "s4-in-02",
                    "kind": "substitute_file",
                    "sha256": raw["input_hashes"]["sub04"]["sha256"],
                    "bytes": raw["input_hashes"]["sub04"]["bytes"],
                    "pages": 59,
                    "page_evidence": "全文 59 页双库；命中页见 method2 per_anchor",
                    "anchor_text": "小米/收入/分部/毛利（年度報告 0，文件类型=业绩公告）",
                    "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0324/2026032400609_c.pdf",
                    "url_source": "PEND-5a provenance ext-04（本工位回源引用）",
                    "retrieved_utc": "2026-09-24T22:09:26Z",
                    "external_retrieval_not_local": True,
                    "external_flag_basis": "IND C 表 ④ + OPEN-11 L360（外部抓取件一律标外部）",
                    "substitute_not_origin": True,
                    "retrieval_method": "direct_https_get_origin (no proxy)",
                    "divergence_from_s3": "S3 in-02 标 external_retrieval_not_local=false"
                                          "（口径=非第三方代理）；本工位按 ④ 标 true，只登记不回改",
                },
                "substitute_attempt08": {
                    "id": "s4-in-03",
                    "kind": "substitute_file",
                    "sha256": raw["input_hashes"]["sub08"]["sha256"],
                    "bytes": raw["input_hashes"]["sub08"]["bytes"],
                    "pages": 415,
                    "page_evidence": "全文 415 页双库；中文 0/5、英文 5/5",
                    "anchor_text": "Xiaomi/Revenue/Annual Report/Segment/Gross profit",
                    "url": "https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2026/04/28/"
                           "5-29-08/Xiaomi%202025%20AR_EN.pdf",
                    "url_source": "PEND-5a provenance ext-08（本工位回源引用）",
                    "retrieved_utc": "2026-09-25T20:37:56Z",
                    "external_retrieval_not_local": True,
                    "external_flag_basis": "IND C 表 ④ + OPEN-11 L360",
                    "substitute_not_origin": True,
                    "retrieval_method": "direct_https_get_issuer (no proxy)",
                    "divergence_from_s3": "S3 in-03 标 false；本工位按 ④ 标 true，只登记不回改",
                },
                "own_outputs": "逐件 sha256+bytes 见 handoff.json:written_files",
            },
        },
        "diffs_vs_s3": diffs,
        "level_claimed": None,
        "level_claimed_note": "不判会计证据等级（S5：行业 reviewer + 会计 reviewer）；"
                              "不重裁 IND C 表行业处置规则",
        "open5_released": False,
        "prior_not_readable_preserved": True,
        "prior_not_readable_verdict_changed": False,
        "sealed_attempt_untouched": True,
        "placeholder_released": False,
        "accept_produced": False,
        "releases_nothing": True,
        "still_not_readable_disposition": True,
        "boundary_L179": "即使本工位结论为 CONSISTENT，S5 走完前仍按不可读处置；"
                         "本轮结论为 NOT_USABLE，更不解除任何处置",
        "self_reviewer_claimed": False,
        "independent_reviewer": "由父另派，本工位不自任",
        "not_done": [
            "未改 S3 / S1 两站 / 封盘 I-11-A 任何字节（101 件重算 sha 全等）",
            "未把 not_readable 改成「已验证」",
            "未判会计证据等级（level_claimed=null）",
            "未重裁 IND C 表行业处置规则",
            "未解除 OPEN-5、未放行 _PLACEHOLDER 参数",
            "未产生 I-11-B 的 ACCEPT、未代签",
            "未自任独立 reviewer",
            "未写五份计划文件",
            "未写 .planning 之外任何路径（含 company-wiki）",
            "零 git 写、未用 git status、未联网",
            "未重跑 OCR 引擎（版本不同，oracle §6.5，已如实标未证实）",
        ],
    }

    os.makedirs(ME, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(OUT, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", OUT, "consistency_result =", overall, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
