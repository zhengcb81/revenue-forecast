import json
import re

base = ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/_work/extract/"
en = open(base + "s5_ind_attempt08_fitz.txt", encoding="utf-8").read()
zh = open(base + "s5_ind_attempt04_fitz.txt", encoding="utf-8").read()
out = {}
for pat in ["opinion", "Opinion", "PricewaterhouseCoopers", "Independent Auditor", "auditor’s report",
            "Auditor's Report", "Report of the Independent", "Five-year", "Five Year", "FIVE-YEAR",
            "financial summary", "Financial Summary", "FINANCIAL SUMMARY", "subsequent event",
            "Segment assets", "segment liabilities", "inventory"]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), en)]
    out["EN::" + pat] = {"count": len(idxs), "snips": [en[max(0, i - 90):i + 110].replace("\n", " ") for i in idxs[:2]]}

# arithmetic identity check from attempt04 segment note (RMB'000)
a = 351217174
b = 106069513
t = 457286687
out["attempt04_segment_sum_identity"] = {"lhs": a, "rhs": b, "sum": a + b, "total": t, "equal": (a + b) == t}

# presence checks used by J3-2 pair extractors
norm_zh = re.sub(r"\s+", " ", zh)
norm_en = re.sub(r"\s+", " ", en)
pairs = {
    "zh_total_bn": r"集團總收入為人民幣([\d,]+)億元",
    "zh_seg_bn": r"AIoT」分部收入為人民幣\s*([\d,]+)\s*億元",
    "zh_seg_table": r"手機×AIoT ([\d,]+\.\d) 76\.8%",
    "zh_total_table": r"總收入 ([\d,]+\.\d) 100\.0%",
    "zh_yoy": r"比增長([\d.]+)%",
    "zh_gm": r"分部毛利率達到歷史新高的([\d.]+)%",
    "en_total_bn": r"total revenue was\s*RMB([\d.]+)\s*billion",
    "en_seg_bn": r"smartphone × AIoT segment reached RMB([\d.]+)\s*billion",
    "en_seg_table": r"Smartphone × AIoT ([\d,]+\.\d) 76\.8%",
    "en_total_table": r"Total revenue ([\d,]+\.\d) 100\.0%",
    "en_yoy": r"increase of ([\d.]+)%",
    "en_gm": r"segment reached a record high of ([\d.]+)%",
}
res = {}
for k, pat in pairs.items():
    src = norm_zh if k.startswith("zh") else norm_en
    m = re.search(pat, src)
    res[k] = m.group(1) if m else None
out["pair_extractor_check"] = res

with open(base + "../probe_en_audit.out.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
print("ok", res, out["attempt04_segment_sum_identity"])
