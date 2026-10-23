import json, hashlib
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"
PAGES = RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json"
ADDENDUM = RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json"
BINDINGS = RUN / "execution_replays/r1-remediation-02/phase_b/research/w09-preparation/claim-scope-bindings.json"

def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def raw_sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

lines = []
# card-expected SHAs for the read-only inputs used in re-slicing
lines.append("verified-source-pages.json sha=%s expected=66dced5b... match=%s" % (sha_file(PAGES)[:16], sha_file(PAGES).startswith("66dced5b")))
lines.append("source-page-addendum-20261023.json sha=%s expected=993cc92c... match=%s" % (sha_file(ADDENDUM)[:16], sha_file(ADDENDUM).startswith("993cc92c")))
lines.append("claim-scope-bindings.json sha=%s expected=7e7dd04e... match=%s" % (sha_file(BINDINGS)[:16], sha_file(BINDINGS).startswith("7e7dd04e")))

ex = json.loads((W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8"))
lines.append("excerpts.source_pages_sha256 matches on-disk pages file: %s" % (ex["source_pages_sha256"] == sha_file(PAGES)))
lines.append("excerpts.proposal_sha256 matches on-disk bindings file: %s" % (ex["proposal_sha256"] == sha_file(BINDINGS)))

pages = json.loads(PAGES.read_text(encoding="utf-8"))
addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
index = {}
for source in list(pages["sources"]) + list(addendum["sources"]):
    for page in source["pages"]:
        index[(source["source_ref"]["source_id"], page["pdf_page"])] = page

# parent record: hash must equal its own span (657..1250)
parent = ex["excerpts"]["chemistry_non_tides_operating"]
pt = index[(parent["source_id"], parent["pdf_page"])]["text"]
psl = pt[parent["start_char_inclusive"]:parent["end_char_exclusive"]]
lines.append("parent chemistry_non_tides_operating: recorded=%s recomputed(657:1250)=%s match=%s" % (
    parent["contiguous_range_sha256"][:16], raw_sha256(psl)[:16], raw_sha256(psl) == parent["contiguous_range_sha256"]))

# which ledger rows reference the two split templates (the MAJOR-1 ten rows)
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
dm_rows = [r["claim_id"] for r in cc["rows"] if r.get("excerpt_id") == "chemistry_dm_operating"]
r_rows = [r["claim_id"] for r in cc["rows"] if r.get("excerpt_id") == "chemistry_r_operating"]
lines.append("rows using chemistry_dm_operating (%d): %s" % (len(dm_rows), json.dumps(dm_rows)))
lines.append("rows using chemistry_r_operating (%d): %s" % (len(r_rows), json.dumps(r_rows)))
lines.append("total rows referencing a split template: %d" % (len(dm_rows) + len(r_rows)))
# confirm none reference the parent
par_rows = [r["claim_id"] for r in cc["rows"] if r.get("excerpt_id") == "chemistry_non_tides_operating"]
lines.append("rows still referencing parent template: %s" % json.dumps(par_rows))

# per-row hash spot-check for the MAJOR-1 affected rows (re-slice + full 64-char compare)
bad = 0
for r in cc["rows"]:
    if r.get("excerpt_id") in ("chemistry_dm_operating", "chemistry_r_operating"):
        text = index[(r["new_source_id"], r["physical_page"])]["text"]
        sl = text[r["contiguous_span"][0]:r["contiguous_span"][1]]
        if raw_sha256(sl) != r["contiguous_range_sha256"]:
            bad += 1
        tpl = ex["excerpts"][r["excerpt_id"]]
        if sl != tpl["excerpt"]:
            bad += 1
lines.append("MAJOR-1 affected rows re-sliced full-64 compare, bad=%d" % bad)

# verify_excerpts.py self-check coverage analysis (static): the assert loop runs before testing_h1_own is created
ve = (W / "delivery/w09/tools/verify_excerpts.py").read_text(encoding="utf-8")
i_selfcheck = ve.find("Self-check: every recorded contiguous-range hash")
i_testing = ve.find('rows["testing_h1_own"]')
lines.append("verify_excerpts.py: self-check loop at char %d; testing_h1_own created at char %d; self-check BEFORE testing_h1_own: %s" % (
    i_selfcheck, i_testing, i_selfcheck < i_testing))
lines.append("=> in-code self-check covers the 21 templates defined at that point (19 proposals + 2 splits); testing_h1_own is added afterwards and only length-checked in code")
tpl = ex["excerpts"]["testing_h1_own"]
text = index[(tpl["source_id"], tpl["pdf_page"])]["text"]
sl = text[tpl["start_char_inclusive"]:tpl["end_char_exclusive"]]
lines.append("testing_h1_own independent re-check: contig match=%s text match=%s span=(%d,%d)" % (
    raw_sha256(sl) == tpl["contiguous_range_sha256"], sl == tpl["excerpt"], tpl["start_char_inclusive"], tpl["end_char_exclusive"]))

# ledger rows count with excerpt_id and with contiguous_range_sha256
n_eid = sum(1 for r in cc["rows"] if r.get("excerpt_id"))
n_hash = sum(1 for r in cc["rows"] if r.get("contiguous_range_sha256"))
lines.append("rows with excerpt_id: %d / 49; rows with contiguous_range_sha256: %d / 49" % (n_eid, n_hash))

(OUTDIR / "f7_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
