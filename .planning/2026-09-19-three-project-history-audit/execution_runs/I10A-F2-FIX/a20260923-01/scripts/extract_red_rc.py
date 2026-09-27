import json, sys, time
from pathlib import Path
att = Path(sys.argv[1])
cases = ["ZJ-MIN-M09", "ZJ-SMT-M09", "XM-PHONE-M03", "XM-EV-M03"]
arms = ["normal", "red_conv", "mut_swap_ids", "mut_swap", "mut_omit_optional"]
table, rows = {}, []
for arm in arms:
    table[arm] = {}
    for case in cases:
        p = att / "evidence" / "probe_before" / case / arm / "probe_result.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        table[arm][case] = d["raw_rc"]
        rows.append({"case": case, "arm": arm, "raw_rc": d["raw_rc"],
                     "source": str(p.relative_to(att)).replace("\\", "/")})
out = att / "evidence" / "rc_red.json"
out.write_text(json.dumps({
    "artifact": "probe_batch_rc", "tag": "red_pre_freeze",
    "note": "RED arm: measured pre-freeze on pristine iso (oracle section 4); extracted from the frozen probe_before payloads, not re-run (the fix is already applied to iso).",
    "read_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "table": table, "rows": rows}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(table))
