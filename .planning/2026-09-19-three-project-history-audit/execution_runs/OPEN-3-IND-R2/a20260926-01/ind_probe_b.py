#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-3-IND-R2 / a20260926-01 -- supplementary probe B (local only, zero network).
B1 signature-page presence variants; B2 entity-decoded quote re-run (m0/m1/m2/m3);
B3 EX99.1 bridge-table scan; B4 Q1 whitespace family table. Appends _probe_raw_b.json.
"""
from __future__ import annotations
import html as H, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
ORIG = PLAN / "execution_runs" / "OPEN3-E1-ORIGIN-BYTES-R2" / "a20260926-01"
ACQ = PLAN / "execution_runs" / "OPEN3-E1-ACQUISITION" / "a20260924-01"

F_8K = ORIG / "origin_bytes" / "MSFT_8-K_2026-09-02_0001193125-26-380280_d291965d8k.htm.origin"
F_EX = ORIG / "origin_bytes" / "MSFT_8-K_Ex99.1_2026-09-02_0001193125-26-380280_d291965dex991.htm.origin"
F_SUB = ORIG / "origin_bytes" / "_independent_0001193125-26-380280_complete_submission.txt"
CA8K = ACQ / "corpus" / "MSFT_8K_2026-09-02_Item7.01.md"
CB8K = ACQ / "corpus" / "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt"
CAEX = ACQ / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.md"
CBEX = ACQ / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt"

rd = lambda p: Path(p).read_bytes()
b8k, bex, bsub = rd(F_8K), rd(F_EX), rd(F_SUB)
ca8k, cb8k, caex, cbex = rd(CA8K), rd(CB8K), rd(CAEX), rd(CBEX)
out = {}

def hits(d, pat):
    r, i = [], 0
    while True:
        j = d.find(pat, i)
        if j < 0: break
        r.append(j); i = j + 1
    return r

def ctx(d, pos, b=110, f=150):
    return d[max(0, pos-b):pos+f].decode("utf-8", "replace").replace("\n", "\\n")

# ---- B1 signature page ----
b1 = {}
for name, d in [("origin_8k", b8k), ("asfiled_submission", bsub), ("corpusA_8k", ca8k), ("corpusB_8k", cb8k)]:
    e = {}
    for pat in [b"Jolla", b"Alice", b"/s/", b"SIGNATURES", b"Signature", b"Chief Accounting Officer", b"Date: September"]:
        hs = hits(d, pat)
        e[pat.decode()] = {"count": len(hs), "first": hs[0] if hs else None,
                           "ctx": ctx(d, hs[0]) if hs else None}
    b1[name] = e
out["B1_signature_variants"] = b1

# ---- B2 entity-decoded quote re-run ----
def dec(b): return H.unescape(b.decode("utf-8", "replace"))
def m0(s): return s
def m1(s): return re.sub(r"\s+", "", s)
def m2(s): return re.sub(r"\s+", " ", s).strip()
def m3(s): return s
prov = json.loads((ACQ / "provenance.json").read_text(encoding="utf-8"))
quotes = prov.get("verbatim_quotes", prov.get("quotes", []))
rows = []
for q in quotes:
    text = q.get("text", "")
    doc = "8k" if q.get("id") in ("Q1", "Q2", "Q3") else "ex"
    raw = b8k if doc == "8k" else bex
    carrier = dec(raw)
    rows.append({
        "id": q.get("id"), "doc": doc,
        "m0_exact_on_decoded": m0(text) in carrier,
        "m1_nows_on_decoded": m1(text) in m1(carrier),
        "m2_wscollapsed_on_decoded": m2(text) in m2(carrier),
        "m3_strict_on_decoded": m3(text) in carrier,
        "corpusA_exact": text in dec(ca8k if doc == "8k" else caex),
    })
out["B2_quotes_decoded"] = {"rows": rows,
    "totals": {k: sum(r[k] for r in rows) for k in ("m0_exact_on_decoded","m1_nows_on_decoded","m2_wscollapsed_on_decoded","m3_strict_on_decoded","corpusA_exact")},
    "total": len(rows)}

# ---- B3 EX99.1 bridge scan ----
b3 = {}
dex = dec(bex)
for pat in ["transition to two reporting", "recast", "reclassif", "bridge", "previously reported",
            "as restated", "As Restated", "Segment History", "reportable segment", "basis of presentation",
            "reflect the new", "aligned to", "mapped"]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), dex)]
    b3[pat] = {"count": len(idxs),
               "ctxs": [dex[max(0,i-70):i+130].replace("\n"," ") for i in idxs[:4]]}
# all old-segment-name occurrences contexts
old = {}
for pat in ["Productivity and Business Processes", "Intelligent Cloud", "More Personal Computing"]:
    idxs = [m.start() for m in re.finditer(re.escape(pat), dex)]
    old[pat] = {"count": len(idxs), "ctxs": [dex[max(0,i-60):i+110].replace("\n"," ") for i in idxs[:6]]}
out["B3_ex991_bridge_scan"] = {"patterns": b3, "old_segment_names": old}

# ---- B4 Q1 whitespace family (decoded) ----
b4 = {}
for name, d in [("origin_8k", dec(b8k)), ("asfiled_submission", dec(bsub)),
                ("corpusA_8k", dec(ca8k)), ("corpusB_8k", dec(cb8k))]:
    form = {}
    for label, pat in [("nbsp_u00a0", "(1)\u00a0"), ("plain_space", "(1) "), ("no_space", "(1)A")]:
        form[label] = d.count(pat)
    i = d.find("two reportable segments")
    form["ctx"] = d[i:i+150].replace("\n", "\\n") if i >= 0 else None
    b4[name] = form
out["B4_q1_whitespace_decoded"] = b4

(HERE / "_probe_raw_b.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"))
print(json.dumps({
    "B1": {k: {p: v[p]["count"] for p in v} for k, v in b1.items()},
    "B2_totals": out["B2_quotes_decoded"]["totals"],
    "B2_rows": [{kk: r[kk] for kk in ("id","m1_nows_on_decoded","m2_wscollapsed_on_decoded","m3_strict_on_decoded")} for r in rows],
    "B3_transition_ctx": b3["transition to two reporting"]["ctxs"][:2],
    "B3_asrestated": {k: b3[k]["count"] for k in ("as restated","As Restated","Segment History","reportable segment","recast","reclassif","bridge","previously reported")},
    "B3_old_counts": {k: v["count"] for k, v in old.items()},
    "B4": b4,
}, ensure_ascii=False, indent=1))
