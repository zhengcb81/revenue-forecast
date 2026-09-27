import json
import re

base = ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/_work/"
en = open(base + "extract/s5_ind_attempt08_fitz.txt", encoding="utf-8").read()
zh = open(base + "extract/s5_ind_attempt04_fitz.txt", encoding="utf-8").read()

frags = {
    "EN_five_year": [m.start() for m in re.finditer("FIVE-YEAR", en)][:3],
    "EN_opinion": [m.start() for m in re.finditer("Opinion", en)][:3],
    "EN_auditors_report": [m.start() for m in re.finditer("auditor.s report", en)][:3],
    "EN_no_segment_assets": [m.start() for m in re.finditer("no separate segment assets", en)][:2],
}
out = {}
for k, idxs in frags.items():
    out[k] = [en[max(0, i - 40):i + 70].replace("\n", " ") for i in idxs]
zh_frags = ["截至2025年12月31日止年度的經審核合併業績", "羅兵咸永道會計師事務所", "概無任何重大分部間銷售",
            "根據國際審計準則進行審核", "數字一致"]
for f in zh_frags:
    out["ZH::" + f] = {"count": zh.count(f), "in_report_src": f}
with open(base + "verify_frag_src.json", "w", encoding="utf-8", newline="\n") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=1))
print("ok")
