import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
lines = []
lines.append("== out_of_union_repairs structure ==")
oour = cc.get("out_of_union_repairs", {})
lines.append("keys: " + ", ".join(oour.keys()))
lines.append("count field: " + json.dumps({k: v for k, v in oour.items() if not isinstance(v, list) and not isinstance(v, dict)}))
for i, r in enumerate(oour.get("rows", [])):
    if isinstance(r, dict):
        lines.append("oour[%d] keys: %s" % (i, ", ".join(r.keys())))
        lines.append("oour[%d]: %s" % (i, json.dumps({k: r[k] for k in r if k in ("claim_id", "excerpt_id", "physical_page", "contiguous_span", "new_source_id", "resolution", "kind")}, ensure_ascii=False)))
    else:
        lines.append("oour[%d] NON-DICT: %r" % (i, r))
lines.append("")
lines.append("== out_of_union_requirement_repairs ==")
oourr = cc.get("out_of_union_requirement_repairs", {})
lines.append("keys: " + ", ".join(oourr.keys()))
lines.append("count field: " + json.dumps({k: v for k, v in oourr.items() if not isinstance(v, list) and not isinstance(v, dict)}))
for i, r in enumerate(oourr.get("rows", [])):
    if isinstance(r, dict):
        lines.append("oourr[%d]: %s" % (i, json.dumps(r, ensure_ascii=False)[:2000]))
    else:
        lines.append("oourr[%d] NON-DICT: %r" % (i, r))
lines.append("")
lines.append("== summary fields ==")
for k in ("expected_union_count", "actual_union_count", "rows_present", "duplicate_rows", "old_role_counts", "new_role_counts"):
    lines.append("%s: %s" % (k, json.dumps(cc.get(k), ensure_ascii=False)))
lines.append("price_negative_control: " + json.dumps(cc.get("price_negative_control"), ensure_ascii=False)[:800])
lines.append("unknown_mechanism_handling: " + json.dumps(cc.get("unknown_mechanism_handling"), ensure_ascii=False)[:1200])
lines.append("rpo_correction: " + json.dumps(cc.get("rpo_correction"), ensure_ascii=False)[:1500])
(OUTDIR / "f1c_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
