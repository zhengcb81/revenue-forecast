import json
import re

base = ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/_work/extract/"
zh = open(base + "s5_ind_attempt04_fitz.txt", encoding="utf-8").read()
en = open(base + "s5_ind_attempt08_fitz.txt", encoding="utf-8").read()

# split attempt04 by page
pages = re.split(r"=== page (\d+) ===", zh)
pagemap = {}
for i in range(1, len(pages), 2):
    pagemap[int(pages[i])] = pages[i + 1]

out = {}
# locate segment note pages in attempt04
seg_pages = [p for p, t in pagemap.items() if "分部資料" in t or "可報告分部" in t]
out["attempt04_segment_note_pages"] = seg_pages
out["attempt04_segment_note_text"] = {p: pagemap[p][:1500] for p in seg_pages}

# pages containing 對賬/抵銷 within segment note context
out["attempt04_last_pages_keys"] = sorted(pagemap)[-12:]
out["attempt04_p49_52_len"] = {p: len(pagemap.get(p, "")) for p in range(48, 60)}

# audit-related sentences in attempt04
aud = [m.start() for m in re.finditer("審核", zh)]
out["attempt04_audit_sentences"] = list({zh[max(0, i - 60):i + 80].replace("\n", " ") for i in aud})[:6]

# does attempt04 contain a full income statement / balance sheet / cash flow?
out["attempt04_statement_presence"] = {k: zh.count(k) for k in
                                       ["合併收益表", "合併財務狀況表", "合併現金流量表", "綜合收益表", "資產負債表",
                                        "現金流量表", "權益變動表", "核數師報告", "財務報表附註", "會計政策"]}

# attempt08 segment note / reconciliation context
rec = [m.start() for m in re.finditer("reconciliation", en)]
out["attempt08_reconciliation_snips"] = [en[max(0, i - 120):i + 160].replace("\n", " ") for i in rec]
sa = [m.start() for m in re.finditer("segment assets", en)]
out["attempt08_segment_assets_snips"] = [en[max(0, i - 120):i + 160].replace("\n", " ") for i in sa]

with open(base + "../probe_inventory.out.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
print("ok", seg_pages, out["attempt04_statement_presence"])
