#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-3-IND-R2 / a20260926-01 -- industry-side independent probe (local only, zero network).
Implements oracle.md 3 (G1-G5, R1-R4) + Q1 segment-set byte-region localisation.
Reads only; writes _probe_raw.json next to this script.
"""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
ORIG = PLAN / "execution_runs" / "OPEN3-E1-ORIGIN-BYTES-R2" / "a20260926-01"
ACQ = PLAN / "execution_runs" / "OPEN3-E1-ACQUISITION" / "a20260924-01"
ACCT = PLAN / "execution_runs" / "OPEN-3-ACCT-R2" / "a20260926-01"
IND = PLAN / "execution_runs" / "I11A-OPEN-IND" / "a20260924-01"

F_8K = ORIG / "origin_bytes" / "MSFT_8-K_2026-09-02_0001193125-26-380280_d291965d8k.htm.origin"
F_EX = ORIG / "origin_bytes" / "MSFT_8-K_Ex99.1_2026-09-02_0001193125-26-380280_d291965dex991.htm.origin"
F_IDX = ORIG / "origin_bytes" / "_identity_0001193125-26-380280-index.htm"
F_SUB = ORIG / "origin_bytes" / "_independent_0001193125-26380280_complete_submission.txt"
F_SUB = ORIG / "origin_bytes" / "_independent_0001193125-26-380280_complete_submission.txt"
F_BIN = ORIG / "origin_bytes.bin"
C_A8K = ACQ / "corpus" / "MSFT_8K_2026-09-02_Item7.01.md"
C_B8K = ACQ / "corpus" / "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt"
C_AEX = ACQ / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.md"
C_BEX = ACQ / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt"

REPORTED = {
    "d291965d8k.htm": ("a3d0bbf6411bb2b2db0bc9deee1541ea44639399e26e1f08adf8df3037ab0878", 28665),
    "d291965dex991.htm": ("47a0a4a1d6a335fffab571789aba597eca0637d2650f0f62371afa10e205b987", 34288),
    "origin_bytes.bin": ("cf84c29048ab314e329758975e101804ba3032f28e2b22d0373f46e3d3c9db1e", 62953),
    "index": ("618f010b6e56597ce881da5ada82b6946615caf2d1062a68942d34a9e24753cf", 17557),
    "submission": ("d82838ac92ed3e8b8e2d6f2ee21b51997309c53d38bcc637ba1041392d1b118f", 2721504),
}
CORPUS_SHA = {
    "MSFT_8K_2026-09-02_Item7.01.md": "096c7d9df55ab46a0ccef21b3ac528b7e59483a91e1b6b32277808bcae801ad1",
    "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt": "5927de0367d1097a6bbb1f59c669a3461eacce43c8115874c5e0a497f7689f1c",
    "MSFT_8K_2026-09-02_Exhibit99-1.md": "20392f0e110568fa4338a1167da3756627b77e606eec85ae113aeebf40373f58",
    "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt": "56b0460b4e635b590c1870153a65adc996d134fd12e2cd6c2670c51ab170956d",
}
SCRIPT_HTML = ('<script type="text/javascript"  src="/QQpw/SBxk/Vaws3/_e/ukQ/ahaE2chLLGzQfS/'
               'Ji1MAQ/Zg9QCV/p9Knc"></script>')

def sha(b): return hashlib.sha256(b).hexdigest()
def rd(p): return Path(p).read_bytes()

out = {}

# ---------- T0 integrity ----------
files = {
    "origin_8k": F_8K, "origin_ex991": F_EX, "origin_index": F_IDX,
    "origin_submission": F_SUB, "origin_bin": F_BIN,
    "corpusA_8k": C_A8K, "corpusB_8k": C_B8K, "corpusA_ex": C_AEX, "corpusB_ex": C_BEX,
    "acct_ruling": ACCT / "ruling_acct_r2.md", "acct_handoff": ACCT / "handoff.json",
    "ind_ruling": IND / "ruling.md",
}
integ = {}
for k, p in files.items():
    b = rd(p)
    integ[k] = {"path": str(p.relative_to(PLAN)), "bytes": len(b), "sha256": sha(b)}
# checks vs reported
checks = {
    "origin_8k": REPORTED["d291965d8k.htm"], "origin_ex991": REPORTED["d291965dex991.htm"],
    "origin_bin": REPORTED["origin_bytes.bin"], "origin_index": REPORTED["index"],
    "origin_submission": REPORTED["submission"],
}
integrity_match = {}
for k, (h, n) in checks.items():
    integrity_match[k] = (integ[k]["sha256"] == h and integ[k]["bytes"] == n)
for k, h in CORPUS_SHA.items():
    key = [x for x in integ if Path(integ[x]["path"]).name == k][0]
    integrity_match["corpus:" + k] = integ[key]["sha256"] == h
out["T0_integrity"] = {"files": integ, "match_reported": integrity_match,
                       "all_match": all(integrity_match.values())}

b8k, bex, bsub = rd(F_8K), rd(F_EX), rd(F_SUB)
ca8k, cb8k, caex, cbex = rd(C_A8K), rd(C_B8K), rd(C_AEX), rd(C_BEX)

def hits(data: bytes, pat: bytes):
    res, i = [], 0
    while True:
        j = data.find(pat, i)
        if j < 0: break
        res.append(j); i = j + 1
    return res

def ctx(data: bytes, pos, back=90, fwd=90):
    s = data[max(0, pos-back): pos+fwd]
    return s.decode("utf-8", "replace").replace("\n", "\\n")

# ---------- G1 word divergence ----------
g1 = {}
for name, data in [("origin_8k", b8k), ("origin_ex991", bex), ("asfiled_submission", bsub),
                   ("corpusA_8k", ca8k), ("corpusB_8k", cb8k), ("corpusA_ex", caex), ("corpusB_ex", cbex),
                   ("origin_index", rd(F_IDX))]:
    ha = hits(data, b"amplifying"); hb = hits(data, b"amplifies")
    entry = {"amplifying_offsets": ha, "amplifies_offsets": hb}
    if ha: entry["amplifying_ctx"] = ctx(data, ha[0])
    if hb: entry["amplifies_ctx"] = ctx(data, hb[0])
    # agency/ambition context
    ag = hits(data, b"agency")
    entry["agency_count"] = len(ag)
    if ag: entry["agency_ctx"] = ctx(data, ag[0], 140, 140)
    g1[name] = entry
out["G1_word_amplifying_vs_amplifies"] = g1

# ---------- G2 signature page ----------
g2 = {}
for name, data in [("origin_8k", b8k), ("asfiled_submission", bsub), ("corpusA_8k", ca8k), ("corpusB_8k", cb8k),
                   ("origin_ex991", bex)]:
    sig = hits(data, b"/s/ Alice L. Jolla")
    dt = hits(data, b"Date: September 2, 2026")
    cov = hits(data, b"Cover Page Interactive Data File")
    g2[name] = {"sig_jolla_offsets": sig, "date_sep2_offsets": dt, "cover_page_offsets": cov,
                "sig_ctx": ctx(data, sig[0], 120, 160) if sig else None}
out["G2_signature_page"] = g2

# ---------- G3 Q1 NBSP / whitespace form ----------
g3 = {}
for name, data in [("origin_8k", b8k), ("asfiled_submission", bsub), ("corpusA_8k", ca8k), ("corpusB_8k", cb8k)]:
    form = {}
    for label, pat in [("nbsp_entity", b"(1)&#160;"), ("nbsp_utf8", b"(1)\xc2\xa0"),
                       ("plain_space", b"(1) "), ("no_space", b"(1)A")]:
        form[label] = len(hits(data, pat))
    i = data.find(b"two reportable segments")
    form["sentence_ctx"] = ctx(data, i, 20, 180) if i >= 0 else None
    g3[name] = form
out["G3_q1_whitespace_form"] = g3

# ---------- G4 edge injected script ----------
g4 = {}
for name, data in [("origin_8k", b8k), ("origin_ex991", bex), ("asfiled_submission", bsub), ("origin_index", rd(F_IDX))]:
    g4[name] = {"script_offsets": hits(data, SCRIPT_HTML.encode()), "script_tag_any": len(re.findall(rb"<script", data))}
out["G4_edge_injected_script"] = g4
# stripped shas (independent recompute)
def strip_script(b):
    return b.replace(SCRIPT_HTML.encode(), b"")
out["G4_stripped_recompute"] = {
    "8k_stripped": {"bytes": len(strip_script(b8k)), "sha256": sha(strip_script(b8k))},
    "ex_raw_stripped": {"bytes": len(strip_script(bex)), "sha256": sha(strip_script(bex))},
}

# ---------- G5 / Q1 segment set anchors on origin ----------
anchors = {
    "two_segment_names_8k": b"Agents and Infra and (2)",
    "beginning_fy2027_8k": b"Beginning in fiscal year 2027",
    "restated_stmt_8k": b"historical data on a basis consistent with the updated reporting structure",
    "item901_ex991_8k": b"Investor Presentation",
    "q4_transition_ex": b"to two segments: Agents and Infra and Devices and Consumer",
    "q5_fy27_ex": b"We will transition to two reporting segments for FY27",
    "q6_revenue_row_ex": b"61,672",
    "q6_full_ex": b"61,672",
    "q6_aif_fy26_ex": b"268,127",
    "q7_aif_outlook_ex": b"75.15",
    "q7_aif_outlook2_ex": b"75.75",
    "q7_dc_outlook_ex": b"14.7 to $15.2",
    "segment_history_as_rested": b"Segment History as Restated",
    "old_pbp_ex": b"Productivity and Business Processes",
    "old_ic_ex": b"Intelligent Cloud",
    "old_mpc_ex": b"More Personal Computing",
    "total_fy26_ex": b"331,839",
    "microsoft_cloud_ex": b"Microsoft Cloud",
}
seg = {}
for label, pat in anchors.items():
    d = bex if label.endswith("_ex") or "ex" == label[-2:] else b8k
    if label in ("two_segment_names_8k", "beginning_fy2027_8k", "restated_stmt_8k", "item901_ex991_8k"):
        d = b8k
    if label.startswith("q6") or label.startswith("q7") or label in ("segment_history_as_rested","old_pbp_ex","old_ic_ex","old_mpc_ex","total_fy26_ex","microsoft_cloud_ex","q4_transition_ex","q5_fy27_ex"):
        d = bex
    hs = hits(d, pat)
    seg[label] = {"count": len(hs), "first_offset": hs[0] if hs else None,
                  "ctx": ctx(d, hs[0], 60, 140) if hs else None}
out["G5_segment_set_anchors"] = seg

# exact q6/q7 byte spans (whitespace-collapsed search on raw ex bytes)
def find_span(data, needle):
    idx = data.find(needle)
    return [idx, idx + len(needle)] if idx >= 0 else None
q6_pat = b"$61,672 $64,441 $67,438 $74,576 $268,127"
q7a = b"$75.15 to $75.75 billion"
q7b = b"$14.7 to $15.2 billion"
out["G5_precise_spans_on_origin_ex991"] = {
    "q6_restated_row": {"pattern": q6_pat.decode(), "span": find_span(bex, q6_pat)},
    "q7_aif_outlook": {"pattern": q7a.decode(), "span": find_span(bex, q7a)},
    "q7_dc_outlook": {"pattern": q7b.decode(), "span": find_span(bex, q7b)},
}
# same anchors on corpora (were they preserved?)
out["G5_anchor_presence_in_corpora"] = {
    name: {
        "q6_row": len(hits(data, b"61,672 64,441 67,438 74,576 268,127")) + len(hits(data, b"61,672 $64,441")),
        "q6_any_61672": len(hits(data, b"61,672")),
        "q7_7515": len(hits(data, b"75.15")),
        "q7_14_7_15_2": len(hits(data, b"14.7 to $15.2")) + len(hits(data, b"14.7 to 15.2")),
    } for name, data in [("corpusA_ex", caex), ("corpusB_ex", cbex)]
}

# ---------- 8 quotes re-run on origin carrier (from acquisition provenance) ----------
prov = json.loads((ACQ / "provenance.json").read_text(encoding="utf-8"))
quotes = prov.get("verbatim_quotes", prov.get("quotes", []))
def m1(s): return re.sub(rb"\s+", b"", s)
def m2(s): return re.sub(rb"\s+", b" ", s).strip()
qr = []
for q in quotes:
    text = q.get("text", "")
    tb = text.encode("utf-8")
    doc = "8k" if "Item7.01" in str(q.get("file", q.get("path", ""))) or q.get("id") in ("Q1","Q2","Q3") else "ex"
    carrier = b8k if doc == "8k" else bex
    row = {"id": q.get("id"), "doc": doc,
           "exact_hit": carrier.find(tb) >= 0,
           "m1_hit": m1(tb) in m1(carrier),
           "m2_hit": m2(tb) in m2(carrier),
           "text_head": text[:90]}
    i = carrier.find(tb)
    if i >= 0: row["origin_span"] = [i, i + len(tb)]
    qr.append(row)
out["quotes_rerun_on_origin"] = {
    "rows": qr,
    "exact": sum(r["exact_hit"] for r in qr), "m1": sum(r["m1_hit"] for r in qr),
    "m2": sum(r["m2_hit"] for r in qr), "total": len(qr),
}

# ---------- R mutations ----------
r = {}
b8k_mut = bytearray(b8k); b8k_mut[1000] = b8k_mut[1000] ^ 0x01
r["R4_byte_flip_sha_mismatch"] = sha(bytes(b8k_mut)) != sha(b8k)
r["R2_quote_digit_change"] = bex.find(b"$268,126") < 0
r["R1_corpus_md_is_not_origin"] = sha(caex) not in {REPORTED["d291965dex991.htm"][0], REPORTED["d291965d8k.htm"][0]}
q1_sent = None
i = ca8k.find(b"two reportable segments")
if i >= 0:
    q1_sent = ca8k[i:i+160]
r["R3_whitespace_mutation_m1_vs_m2"] = {
    "corpus_q1_head": q1_sent.decode("utf-8", "replace") if q1_sent else None,
    "m1_on_origin_q1": m1(b"(1)\xc2\xa0Agents and Infra and (2)\xc2\xa0Devices and Consumer") in m1(b8k),
    "m2_on_origin_q1": m2(b"(1)\xc2\xa0Agents and Infra and (2)\xc2\xa0Devices and Consumer") in m2(b8k),
}
out["R_mutations"] = r

# ---------- C5-direction: family split table ----------
out["c5_direction_evidence_table"] = {
    "word_amplifying": {k: {"amplifying": len(v["amplifying_offsets"]), "amplifies": len(v["amplifies_offsets"])}
                        for k, v in g1.items()},
    "family_origin_r2_session": ["origin_8k", "origin_ex991", "asfiled_submission"],
    "family_corpus_worker_transcription": ["corpusA_8k", "corpusB_8k", "corpusA_ex", "corpusB_ex"],
    "third_family_ind_side_artifacts_covering_dispute": "see ruling (grep of I11A-OPEN-IND/I11A-OPEN11-IND provenance: 0 hits for amplif/agency/ambition/Jolla)",
}
out["probe_meta"] = {"zero_network": True, "writes": "_probe_raw.json only",
                     "python_stdlib_only": True}

(HERE / "_probe_raw.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8"))
print(json.dumps({
    "all_integrity_match": out["T0_integrity"]["all_match"],
    "G1": out["c5_direction_evidence_table"]["word_amplifying"],
    "G2_sig": {k: len(v["sig_jolla_offsets"]) for k, v in g2.items()},
    "G3": {k: v for k, v in g3.items()},
    "G4_script": {k: v["script_offsets"] for k, v in g4.items()},
    "quotes": {k: out["quotes_rerun_on_origin"][k] for k in ("exact", "m1", "m2", "total")},
    "spans": out["G5_precise_spans_on_origin_ex991"],
    "R": r,
}, ensure_ascii=False, indent=1))
