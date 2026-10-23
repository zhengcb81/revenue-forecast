import hashlib, json
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"

pages = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json").read_text(encoding="utf-8"))
addendum = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json").read_text(encoding="utf-8"))
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))

index = {}
for source in list(pages["sources"]) + list(addendum["sources"]):
    for page in source["pages"]:
        index[(source["source_ref"]["source_id"], page["pdf_page"])] = page


def raw_sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


lines = []
groups = [
    ("rows", cc["rows"]),
    ("out_of_union_repairs.rows", cc.get("out_of_union_repairs", {}).get("rows", [])),
    ("out_of_union_requirement_repairs.rows", cc.get("out_of_union_requirement_repairs", {}).get("rows", [])),
]
total_with_hash = 0
mismatch = 0
missing_page = []
per_group = {}
for gname, rows in groups:
    g_total = 0
    g_bad = 0
    for row in rows:
        if not isinstance(row, dict):
            lines.append("NON-DICT ROW in %s: %r" % (gname, row))
            continue
        if "contiguous_range_sha256" not in row or row.get("contiguous_range_sha256") is None:
            continue
        total_with_hash += 1
        g_total += 1
        key = (row.get("new_source_id"), row.get("physical_page"))
        if key not in index:
            missing_page.append((gname, row.get("claim_id"), key))
            continue
        text = index[key]["text"]
        span = row.get("contiguous_span")
        if span is None:
            lines.append("NO SPAN in %s: %s" % (gname, row.get("claim_id")))
            continue
        sl = text[span[0]:span[1]]
        got = raw_sha256(sl)
        if got != row["contiguous_range_sha256"]:
            g_bad += 1
            mismatch += 1
            lines.append("MISMATCH %s %s: stored=%s recomputed=%s span=%r" % (
                gname, row.get("claim_id"), row["contiguous_range_sha256"][:16], got[:16], span))
    per_group[gname] = (g_total, g_bad)

lines.append("rows with contiguous_range_sha256 checked: %d, mismatches: %d, missing pages: %d" % (total_with_hash, mismatch, len(missing_page)))
lines.append("per-group (checked, bad): " + json.dumps(per_group))
lines.append("group sizes: rows=%d oour=%d oourr=%d" % (len(cc["rows"]), len(cc.get("out_of_union_repairs", {}).get("rows", [])), len(cc.get("out_of_union_requirement_repairs", {}).get("rows", []))))
lines.append("unchanged_claim_ids: %d" % len(cc.get("unchanged_claim_ids", [])))

# also verify the excerpt template hashes referenced by rows: row.excerpt_id -> excerpts.json record
excerpts = json.loads((W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8"))
bad_tpl = 0
tpl_checked = 0
for gname, rows in groups:
    for row in rows:
        if not isinstance(row, dict):
            continue
        eid = row.get("excerpt_id")
        if not eid or eid not in excerpts["excerpts"]:
            continue
        tpl = excerpts["excerpts"][eid]
        if "excerpt" not in tpl:
            lines.append("row %s references template %s with no excerpt text" % (row.get("claim_id"), eid))
            continue
        tpl_checked += 1
        # row's own re-sliced span must equal the template text and hashes must be consistent
        key = (row.get("new_source_id"), row.get("physical_page"))
        if key in index and row.get("contiguous_span"):
            sl = index[key]["text"][row["contiguous_span"][0]:row["contiguous_span"][1]]
            if sl != tpl["excerpt"]:
                bad_tpl += 1
                lines.append("ROW/TEMPLATE TEXT MISMATCH %s (%s)" % (row.get("claim_id"), eid))
        if row.get("contiguous_range_sha256") and row["contiguous_range_sha256"] != tpl.get("contiguous_range_sha256"):
            bad_tpl += 1
            lines.append("ROW/TEMPLATE HASH MISMATCH %s (%s): row=%s tpl=%s" % (row.get("claim_id"), eid, row["contiguous_range_sha256"][:16], str(tpl.get("contiguous_range_sha256"))[:16]))
        if row.get("new_excerpt_sha256") and row["new_excerpt_sha256"] != tpl.get("excerpt_sha256"):
            bad_tpl += 1
            lines.append("ROW/TEMPLATE EXCERPT_SHA MISMATCH %s (%s)" % (row.get("claim_id"), eid))
lines.append("rows cross-checked vs excerpt templates: %d, inconsistencies: %d" % (tpl_checked, bad_tpl))

(OUTDIR / "f1b_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
