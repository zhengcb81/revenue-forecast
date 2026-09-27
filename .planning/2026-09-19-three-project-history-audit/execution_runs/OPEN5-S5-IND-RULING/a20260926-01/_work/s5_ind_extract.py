#!/usr/bin/env python3
# OPEN5-S5-IND-RULING · 行业面自抽测量（oracle 冻结后执行；只读输入，输出只落本目录 _work/）
import hashlib
import json
import os
import re
import sys

PLAN = os.path.join(".planning", "2026-09-19-three-project-history-audit")
RUNS = os.path.join(PLAN, "execution_runs")
PEND5A = os.path.join(RUNS, "OPEN5-PEND5A-HK-ACQUISITION", "a20260924-01")
CORPUS = os.path.join(PEND5A, "corpus")
HERE = os.path.join(RUNS, "OPEN5-S5-IND-RULING", "a20260926-01")
WORK = os.path.join(HERE, "_work")
EXTRACT = os.path.join(WORK, "extract")

ZH_ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]
EN_ANCHORS = ["Xiaomi", "Revenue", "Annual Report", "Segment", "Gross profit"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_lf(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def extract_fitz(pdf_path, out_txt):
    import fitz
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, start=1):
        pages.append("\n=== page %d ===\n" % i)
        pages.append(page.get_text())
    text = "".join(pages)
    n_pages = doc.page_count
    doc.close()
    write_lf(out_txt, text)
    return text, n_pages


def extract_pdfminer(pdf_path, out_txt):
    from pdfminer.high_level import extract_text
    text = extract_text(pdf_path)
    write_lf(out_txt, text)
    return text


def counts(text, anchors):
    return {a: text.count(a) for a in anchors}


def hit_words(d):
    return sum(1 for v in d.values() if v > 0)


def find_windows(text, label_zh, label_en, span=90, limit=4):
    """Return up to `limit` windows around zh/en label occurrences with numbers in them."""
    out = []
    for label in [label_zh, label_en]:
        if not label:
            continue
        for m in re.finditer(re.escape(label), text, flags=0):
            seg = text[m.start(): m.start() + span]
            nums = re.findall(r"\d[\d,]*(?:\.\d+)?", seg)
            nums = [n for n in nums if len(n.replace(",", "").replace(".", "")) >= 2]
            if nums:
                out.append({"label": label, "window": seg.replace("\n", " ")[:span], "numbers": nums[:6]})
            if len(out) >= limit:
                return out
    return out


def norm_nums(nums):
    return sorted({n.replace(",", "") for n in nums})


def main():
    os.makedirs(EXTRACT, exist_ok=True)
    result = {"generated_note": "industry-face own extraction (post-oracle-freeze)", "inputs": {}}

    p04 = os.path.join(CORPUS, "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf")
    p08 = os.path.join(CORPUS, "attempt08_irmi_xiaomi_ar2025_en.pdf")
    p07 = os.path.join(CORPUS, "attempt07_rjina_xiaomi_ar2025_zh_proxy.txt")
    p01 = os.path.join(CORPUS, "attempt01_hkexnews_xiaomi_ar2025_zh.pdf")

    # ---- sha256 of corpus bytes (J1-3 / §4.7-3) ----
    for tag, p in (("attempt04", p04), ("attempt08", p08), ("attempt07", p07), ("attempt01_origin_copy", p01)):
        result["inputs"][tag] = {
            "path": p.replace("\\", "/"),
            "bytes": os.path.getsize(p),
            "sha256": sha256_file(p),
            "mtime_utc": __import__("datetime").datetime.utcfromtimestamp(os.path.getmtime(p)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
        }

    # ---- attempt04 : fitz (主) + pdfminer (独立路径) ----
    t04, n04 = extract_fitz(p04, os.path.join(EXTRACT, "s5_ind_attempt04_fitz.txt"))
    t04b = extract_pdfminer(p04, os.path.join(EXTRACT, "s5_ind_attempt04_pdfminer.txt"))
    # ---- attempt08 : fitz (主) + pdfminer (独立路径) ----
    t08, n08 = extract_fitz(p08, os.path.join(EXTRACT, "s5_ind_attempt08_fitz.txt"))
    t08b = extract_pdfminer(p08, os.path.join(EXTRACT, "s5_ind_attempt08_pdfminer.txt"))
    # ---- attempt07 : 第三方代理渲染文本（直接读） ----
    with open(p07, "r", encoding="utf-8", errors="replace") as f:
        t07 = f.read()

    c04_zh = counts(t04, ZH_ANCHORS)
    c04_zh_pm = counts(t04b, ZH_ANCHORS)
    c08_zh = counts(t08, ZH_ANCHORS)
    c08_en = counts(t08, EN_ANCHORS)
    c08_en_pm = counts(t08b, EN_ANCHORS)
    c07_zh = counts(t07, ZH_ANCHORS)

    result["anchors"] = {
        "attempt04_fitz_zh": {**c04_zh, "hit_words": hit_words(c04_zh), "total_chars": len(t04),
                              "cjk": len(re.findall(r"[\u4e00-\u9fff]", t04))},
        "attempt04_pdfminer_zh": {**c04_zh_pm, "hit_words": hit_words(c04_zh_pm), "total_chars": len(t04b)},
        "attempt08_fitz_zh": {**c08_zh, "hit_words": hit_words(c08_zh), "total_chars": len(t08),
                              "cjk": len(re.findall(r"[\u4e00-\u9fff]", t08))},
        "attempt08_fitz_en": {**c08_en, "hit_words": hit_words(c08_en)},
        "attempt08_pdfminer_en": {**c08_en_pm, "hit_words": hit_words(c08_en_pm)},
        "attempt07_proxy_zh": {**c07_zh, "hit_words": hit_words(c07_zh), "total_chars": len(t07),
                               "cjk": len(re.findall(r"[\u4e00-\u9fff]", t07))},
        "pages": {"attempt04": n04, "attempt08": n08},
    }

    # ---- 文件类型识别（J2 步骤 1）----
    result["document_type"] = {
        "attempt04_has_results_announcement_title": "全年業績公告" in t04,
        "attempt04_has_period_verbatim": "截至2025年12月31日止年度" in t04,
        "attempt04_has_annual_report_title": bool(re.search(r"年度報告（?", t04[:4000])),
        "attempt04_title_snippet": t04[:300].replace("\n", " "),
        "attempt08_has_annual_report_title": bool(
            re.search(r"Annual Report", t08[:8000], flags=re.I)),
        "attempt08_has_period_marker": bool(re.search(r"2025", t08[:8000])),
        "attempt08_title_snippet": t08[:400].replace("\n", " "),
    }

    # ---- J2 内容清单（A1..A7 逐类 presence + 首个命中位置）----
    inv_specs = {
        "A1_segment_revenue_level_growth": ["分部收入", "分部收益", "手機×AIoT", "業務分部"],
        "A2_segment_gross_margin": ["分部毛利率", "毛利率", "毛利"],
        "A3_total_revenue_growth": ["總收入", "總收入為人民幣", "收入為人民幣", "同比增長"],
        "A4_segment_note_reconciliation": ["分部資料", "可報告分部", "分部附註", "對賬", "分部資產", "reconciliation",
                                           "Segment Information"],
        "A5_audit_opinion": ["核數師報告", "無保留意見", "獨立核數師", "審核報告", "Report of Independent Auditor",
                             "unqualified opinion"],
        "A6_five_year_and_notes": ["五年", "財務摘要", "存貨明細", "Five-year", "五年財務"],
        "A7_annual_report_body_marker": ["年度報告", "Annual Report", "415"],
    }
    inventory = {}
    for key, needles in inv_specs.items():
        entry = {"needles": needles, "hits": {}}
        for nd in needles:
            c = t04.count(nd)
            pos = t04.find(nd)
            pg = None
            if pos >= 0:
                m = re.search(r"=== page (\d+) ===", t04[:pos])
                if m:
                    pg = int(m.group(1))
            entry["hits"][nd] = {"count": c, "first_page": pg,
                                 "window": (t04[pos:pos + 120].replace("\n", " ") if pos >= 0 else None)}
        entry["present"] = any(v["count"] > 0 for v in entry["hits"].values())
        inventory[key] = entry
    result["attempt04_inventory"] = inventory

    # attempt08 (EN 年报) 的对应内容清单 —— 供 A4/A5/A6 是否"换源可用"登记
    inv08 = {}
    for key, needles in {
        "A4_segment_note_reconciliation": ["Segment Information", "reconciliation", "Reportable segment",
                                            "segment assets"],
        "A5_audit_opinion": ["Independent Auditor", "unqualified opinion", "Auditor's Report"],
        "A6_five_year_and_notes": ["Five-year", "inventor", "Five year"],
    }.items():
        inv08[key] = {nd: t08.count(nd) for nd in needles}
    result["attempt08_inventory"] = inv08

    # ---- J3-2 跨语言共享数值窗口 ----
    windows = {}
    windows["total_revenue"] = find_windows(t04, "總收入", "total revenue", span=110)
    windows["yoy_growth"] = find_windows(t04, "同比增長", "year-over-year", span=90)
    windows["segment_revenue"] = find_windows(t04, "分部收入", "Segment-wise", span=120)
    windows["gross_margin"] = find_windows(t04, "毛利率", "gross margin", span=90)

    windows08 = {}
    windows08["total_revenue"] = find_windows(t08, "總收入", "total revenue", span=110)
    windows08["yoy_growth"] = find_windows(t08, "同比增長", "year-over-year", span=90)
    windows08["segment_revenue"] = find_windows(t08, "分部收入", "Segment-wise", span=120)
    windows08["gross_margin"] = find_windows(t08, "毛利率", "gross margin", span=90)
    result["shared_value_windows"] = {"attempt04": windows, "attempt08": windows08}

    # 显式共享标量（两文本中都必须出现的归一化数字）
    scalars = ["25.0", "21.7", "457.3", "3,512", "3512", "1,007,261"]
    result["shared_scalar_presence"] = {
        s: {"attempt04": s in t04 or s.replace(",", "") in t04.replace(",", ""),
            "attempt08": s in t08 or s.replace(",", "") in t08.replace(",", "")}
        for s in scalars
    }

    # 分部收入披露的存在性（J1-3）
    result["segment_revenue_disclosure"] = {
        "attempt04": {
            "anchors_hit": [a for a in ["分部收入", "分部收益", "手機×AIoT"] if a in t04],
            "evidence": next((w for w in windows["segment_revenue"] if "分部" in w["label"]), None),
        },
        "attempt08": {
            "anchors_hit": [a for a in ["Segment-wise", "segment revenue", "revenue of our"] if a in t08],
            "evidence": next((w for w in windows08["segment_revenue"]), None),
        },
    }

    out = os.path.join(WORK, "s5_ind_extract.json")
    write_lf(out, json.dumps(result, ensure_ascii=False, indent=2))
    print("wrote", out)
    print(json.dumps({k: result[k] for k in ("anchors", "document_type", "segment_revenue_disclosure")},
                     ensure_ascii=False)[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
