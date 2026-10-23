import hashlib, json
from pathlib import Path

W = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
OUTDIR = W / "delivery" / "w09" / "review" / "_probe2"

pages = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/verified-source-pages.json").read_text(encoding="utf-8"))
addendum = json.loads((RUN / "execution_replays/r1-remediation-02/phase_b/research/source-page-addendum-20261023.json").read_text(encoding="utf-8"))
excerpts = json.loads((W / "delivery/w09/research/excerpts.json").read_text(encoding="utf-8"))

index = {}
for source in list(pages["sources"]) + list(addendum["sources"]):
    for page in source["pages"]:
        index[(source["source_ref"]["source_id"], page["pdf_page"])] = page


def raw_sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


lines = []

# --- FIX-1 part A: split spans carry their OWN contiguous hash ---
for eid in ["chemistry_dm_operating", "chemistry_r_operating"]:
    r = excerpts["excerpts"][eid]
    page_text = index[(r["source_id"], r["pdf_page"])]["text"]
    sl = page_text[r["start_char_inclusive"]:r["end_char_exclusive"]]
    lines.append(
        "%s: stored=%s recomputed=%s match=%s span=(%d,%d) excerpt_eq_slice=%s"
        % (eid, r["contiguous_range_sha256"][:16], raw_sha256(sl)[:16],
           raw_sha256(sl) == r["contiguous_range_sha256"],
           r["start_char_inclusive"], r["end_char_exclusive"], sl == r["excerpt"])
    )
lines.append("expected dm d26e03ca..., expected r d4d7df24...")
parent = excerpts["excerpts"]["chemistry_non_tides_operating"]
lines.append("parent record keys (excerpt removed): " + ", ".join(sorted(parent.keys())))
lines.append("parent split_into: " + json.dumps(parent.get("split_into")))

# --- inspect claim-changes structure ---
cc = json.loads((W / "delivery/w09/research/claim-changes.json").read_text(encoding="utf-8"))
lines.append("claim-changes top keys: " + ", ".join(cc.keys()))
sample = cc["rows"][0]
lines.append("sample row keys: " + ", ".join(sample.keys()))
lines.append("sample row: " + json.dumps(sample, ensure_ascii=False)[:1500])

(OUTDIR / "f1a_out.txt").write_text("\n".join(lines), encoding="utf-8")
print("ok")
