import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
ex = json.loads((W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8"))
lines = []
lines.append("top keys: %s" % ", ".join(ex.keys()))
lines.append("count fields: " + json.dumps({k: ex[k] for k in ex if k.startswith("count_")}))
lines.append("purpose: " + ex.get("purpose", ""))
lines.append("n excerpt templates: %d" % len(ex["excerpts"]))
lines.append("excerpt ids: " + ", ".join(sorted(ex["excerpts"].keys())))
# FIX-4 semantics: template vs claim/proposal counts
lines.append("count_excerpt_templates_verified == 22 (with excerpt field): %d" % ex["count_excerpt_templates_verified"])
lines.append("over_500: %s ; under_10: %s" % (json.dumps(ex["over_500"]), json.dumps(ex["under_10"])))
# check chemistry spans recorded in excerpts for dm/r
for eid in ("chemistry_dm_operating", "chemistry_r_operating", "chemistry_non_tides_operating"):
    r = ex["excerpts"][eid]
    lines.append("%s: span=(%s,%s) contig_sha=%s len=%s" % (
        eid, r.get("start_char_inclusive"), r.get("end_char_exclusive"),
        r.get("contiguous_range_sha256", "")[:16], len(r.get("excerpt", "")) if "excerpt" in r else "no-excerpt"))

# FIX-6: excerpts self-check - re-verify EVERY template's hash from page text (already done for ledger rows; do templates)
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
pages = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json").read_text(encoding="utf-8"))
addendum = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json").read_text(encoding="utf-8"))
index = {}
for source in list(pages["sources"]) + list(addendum["sources"]):
    for page in source["pages"]:
        index[(source["source_ref"]["source_id"], page["pdf_page"])] = page

def raw_sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

bad = 0
checked = 0
for eid, r in ex["excerpts"].items():
    if "excerpt" not in r:
        continue
    checked += 1
    page_text = index[(r["source_id"], r["pdf_page"])]["text"]
    sl = page_text[r["start_char_inclusive"]:r["end_char_exclusive"]]
    if raw_sha256(sl) != r["contiguous_range_sha256"]:
        bad += 1
        lines.append("TEMPLATE MISMATCH %s" % eid)
    if sl != r["excerpt"]:
        bad += 1
        lines.append("TEMPLATE TEXT MISMATCH %s" % eid)
    if hashlib.sha256(r["excerpt"].strip().encode("utf-8")).hexdigest() != r["excerpt_sha256"]:
        bad += 1
        lines.append("TEMPLATE EXCERPT_SHA MISMATCH %s" % eid)
lines.append("templates fully re-verified from page bytes: %d, bad: %d" % (checked, bad))

(OUTDIR / "f4_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
