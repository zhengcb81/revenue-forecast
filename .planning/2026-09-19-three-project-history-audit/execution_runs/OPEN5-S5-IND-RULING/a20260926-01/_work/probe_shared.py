import json
import re

base = ".planning/2026-09-19-three-project-history-audit/execution_runs/OPEN5-S5-IND-RULING/a20260926-01/_work/extract/"
en = open(base + "s5_ind_attempt08_fitz.txt", encoding="utf-8").read()
zh = open(base + "s5_ind_attempt04_fitz.txt", encoding="utf-8").read()
out = {}
for pat in ["RMB457.3", "RMB351.2", "21.7", "margin", "25.0%", "Auditor", "39.2", "351,217.2", "106,069.5", "5.4%"]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), en)]
    out["EN::" + pat] = {"count": len(idxs), "snips": [en[max(0, i - 80):i + 100].replace("\n", " ") for i in idxs[:2]]}
for pat in ["審核", "核數師", "未經審核", "351,217.2", "106,069.5", "4,573", "21.7%", "對賬", "抵銷", "分部資料"]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), zh)]
    out["ZH::" + pat] = {"count": len(idxs), "snips": [zh[max(0, i - 80):i + 100].replace("\n", " ") for i in idxs[:2]]}
with open(base + "../probe_shared.out.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=1))
print("ok", {k: v["count"] for k, v in out.items()})
