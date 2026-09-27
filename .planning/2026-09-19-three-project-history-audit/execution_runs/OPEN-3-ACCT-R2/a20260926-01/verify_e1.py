#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-3-ACCT-R2 / a20260926-01 -- E1 re-grading verification harness (local only, zero network).

Implements oracle.md 一~五: T1 integrity, T2 edge script, T3 independent path,
P-A/P-B + M1/M2/M3 quote re-run, T4 full token diff, and the frozen mutation list.
Writes _verification_raw.json next to this script; prints a short summary.
"""
from __future__ import annotations

import hashlib
import html as html_mod
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]                      # .planning/2026-09-19-three-project-history-audit
ORIGIN_DIR = PLAN / "execution_runs" / "OPEN3-E1-ORIGIN-BYTES-R2" / "a20260926-01"
ACQ_DIR = PLAN / "execution_runs" / "OPEN3-E1-ACQUISITION" / "a20260924-01"

F_8K = ORIGIN_DIR / "origin_bytes" / "MSFT_8-K_2026-09-02_0001193125-26-380280_d291965d8k.htm.origin"
F_EX = ORIGIN_DIR / "origin_bytes" / "MSFT_8-K_Ex99.1_2026-09-02_0001193125-26-380280_d291965dex991.htm.origin"
F_IDX = ORIGIN_DIR / "origin_bytes" / "_identity_0001193125-26-380280-index.htm"
F_SUB = ORIGIN_DIR / "origin_bytes" / "_independent_0001193125-26-380280_complete_submission.txt"
F_BLK = ORIGIN_DIR / "origin_bytes" / "_mutation_R1_sec_block_page.htm"
F_BIN = ORIGIN_DIR / "origin_bytes.bin"

REPORTED_SHA = {
    "d291965d8k.htm": "a3d0bbf6411bb2b2db0bc9deee1541ea44639399e26e1f08adf8df3037ab0878",
    "d291965dex991.htm": "47a0a4a1d6a335fffab571789aba597eca0637d2650f0f62371afa10e205b987",
    "origin_bytes.bin": "cf84c29048ab314e329758975e101804ba3032f28e2b22d0373f46e3d3c9db1e",
    "identity_index": "618f010b6e56597ce881da5ada82b6946615caf2d1062a68942d34a9e24753cf",
    "complete_submission": "d82838ac92ed3e8b8e2d6f2ee21b51997309c53d38bcc637ba1041392d1b118f",
}
REPORTED_BYTES = {"8k": 28665, "ex": 34288, "bin": 62953, "idx": 17557, "sub": 2721504, "blk": 4819}
SCRIPT_HTML = ('<script type="text/javascript"  src="/QQpw/SBxk/Vaws3/_e/ukQ/ahaE2chLLGzQfS/'
               'Ji1MAQ/Zg9QCV/p9Knc"></script>')
SPAN_8K = (28544, 28650)
SPAN_EX = (34147, 34253)
REPORTED_STRIPPED = {
    "8k_sha": "6328d05612511965c29ff3d6a6919137eab86080fc2952d141c126cfe091d600",
    "8k_bytes": 28559,
    "ex_raw_minus_script_sha": "557161af7ac2f2eed02c2ad77b8d5e1e21acd35173e46519981ad85d28a15be5",
    "ex_raw_minus_script_bytes": 34182,
    "ex_inner_minus_script_sha": "4cb79b6e33fbb687f2fd6dbd2b59a4b53b41fa87b009d0a0c859d28e0c3987fd",
    "ex_inner_minus_script_bytes": 34070,
}
CORPUS_SHA = {
    "MSFT_8K_2026-09-02_Item7.01.md": "096c7d9df55ab46a0ccef21b3ac528b7e59483a91e1b6b32277808bcae801ad1",
    "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt": "5927de0367d1097a6bbb1f59c669a3461eacce43c8115874c5e0a497f7689f1c",
    "MSFT_8K_2026-09-02_Exhibit99-1.md": "20392f0e110568fa4338a1167da3756627b77e606eec85ae113aeebf40373f58",
    "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt": "56b0460b4e635b590c1870153a65adc996d134fd12e2cd6c2670c51ab170956d",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def decode(b: bytes) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", errors="replace")


def strip_html(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<[^>]*>", " ", s, flags=re.S)
    s = html_mod.unescape(s)
    return s


def m1(s: str) -> str:            # whitespace-insensitive
    return re.sub(r"\s+", "", s)


def m2(s: str) -> str:            # whitespace collapsed to single space
    return re.sub(r"\s+", " ", s).strip()


def num_tokens(s: str):
    return sorted(set(re.findall(r"\d[\d,]*\.?\d*", s)))


def word_tokens(s: str):
    return sorted(set(w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'’\-]+", s)))


def strip_urls(s: str) -> str:
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"www\.[^\s\)]+", " ", s)
    return s


def main() -> int:
    out: dict = {"card": "OPEN-3-ACCT-R2", "attempt": "a20260926-01"}

    # ---------- T1 integrity ----------
    raw_8k, raw_ex = read_bytes(F_8K), read_bytes(F_EX)
    raw_idx, raw_sub, raw_bin, raw_blk = read_bytes(F_IDX), read_bytes(F_SUB), read_bytes(F_BIN), read_bytes(F_BLK)
    t1 = {
        "sizes": {"8k": len(raw_8k), "ex": len(raw_ex), "idx": len(raw_idx),
                  "sub": len(raw_sub), "bin": len(raw_bin), "blk": len(raw_blk)},
        "sha": {"8k": sha(raw_8k), "ex": sha(raw_ex), "idx": sha(raw_idx),
                "sub": sha(raw_sub), "bin": sha(raw_bin)},
        "reported": REPORTED_SHA,
    }
    t1["sha_match"] = {
        "8k": t1["sha"]["8k"] == REPORTED_SHA["d291965d8k.htm"],
        "ex": t1["sha"]["ex"] == REPORTED_SHA["d291965dex991.htm"],
        "idx": t1["sha"]["idx"] == REPORTED_SHA["identity_index"],
        "sub": t1["sha"]["sub"] == REPORTED_SHA["complete_submission"],
        "bin": t1["sha"]["bin"] == REPORTED_SHA["origin_bytes.bin"],
    }
    t1["sizes_match"] = {
        "8k": len(raw_8k) == REPORTED_BYTES["8k"],
        "ex": len(raw_ex) == REPORTED_BYTES["ex"],
        "bin": len(raw_bin) == REPORTED_BYTES["bin"],
        "idx": len(raw_idx) == REPORTED_BYTES["idx"],
        "sub": len(raw_sub) == REPORTED_BYTES["sub"],
        "blk": len(raw_blk) == REPORTED_BYTES["blk"],
    }
    t1["bin_is_concat"] = (raw_bin == raw_8k + raw_ex)
    t1["bin_layout_offsets"] = {"8k": [0, len(raw_8k)], "ex": [len(raw_8k), len(raw_bin)]}
    out["T1_integrity"] = t1

    # ---------- corpus integrity ----------
    corpus = {}
    for name, exp in CORPUS_SHA.items():
        b = read_bytes(ACQ_DIR / "corpus" / name)
        corpus[name] = {"bytes": len(b), "sha": sha(b), "reported": exp, "match": sha(b) == exp,
                        "has_bom": b.startswith(b"\xef\xbb\xbf"), "has_cr": b"\r" in b}
    out["corpus_integrity"] = corpus

    # ---------- T2 edge-injected script ----------
    seg8 = raw_8k[SPAN_8K[0]:SPAN_8K[1]]
    segx = raw_ex[SPAN_EX[0]:SPAN_EX[1]]
    idx_txt, sub_txt = decode(raw_idx), decode(raw_sub)
    stripped8 = raw_8k[:SPAN_8K[0]] + raw_8k[SPAN_8K[1]:]
    strippedx = raw_ex[:SPAN_EX[0]] + raw_ex[SPAN_EX[1]:]
    t2 = {
        "script_html_expected": SCRIPT_HTML,
        "span_8k": list(SPAN_8K), "span_ex": list(SPAN_EX),
        "seg_8k_equals_expected": decode(seg8) == SCRIPT_HTML,
        "seg_ex_equals_expected": decode(segx) == SCRIPT_HTML,
        "seg_8k_hex": seg8.hex(), "seg_ex_hex": segx.hex(),
        "two_hits_byte_identical": seg8 == segx,
        "occurrences_in_8k": decode(raw_8k).count("/QQpw/SBxk/"),
        "occurrences_in_ex": decode(raw_ex).count("/QQpw/SBxk/"),
        "occurrences_in_index": idx_txt.count("/QQpw/SBxk/"),
        "occurrences_in_submission": sub_txt.count("/QQpw/SBxk/"),
        "stripped_8k": {"bytes": len(stripped8), "sha": sha(stripped8),
                        "reported_bytes": REPORTED_STRIPPED["8k_bytes"],
                        "reported_sha": REPORTED_STRIPPED["8k_sha"],
                        "match": (len(stripped8) == REPORTED_STRIPPED["8k_bytes"]
                                  and sha(stripped8) == REPORTED_STRIPPED["8k_sha"])},
        "stripped_ex_raw": {"bytes": len(strippedx), "sha": sha(strippedx),
                            "reported_bytes": REPORTED_STRIPPED["ex_raw_minus_script_bytes"],
                            "reported_sha": REPORTED_STRIPPED["ex_raw_minus_script_sha"],
                            "match": (len(strippedx) == REPORTED_STRIPPED["ex_raw_minus_script_bytes"]
                                      and sha(strippedx) == REPORTED_STRIPPED["ex_raw_minus_script_sha"])},
        "trailing_after_script_8k": decode(raw_8k[SPAN_8K[1]:])[:120],
        "trailing_after_script_ex": decode(raw_ex[SPAN_EX[1]:])[:120],
        "head_of_8k": decode(raw_8k[:400]),
        "ex_is_sgml_wrapped": decode(raw_ex[:200]).startswith("<DOCUMENT>"),
    }
    out["T2_edge_script"] = t2

    # ---------- T3 independent path (as-filed archive copy) -- BYTE level ----------
    def doc_blocks_b(data: bytes):
        blocks = []
        for p in data.split(b"<DOCUMENT>")[1:]:
            body = p.split(b"</DOCUMENT>")[0]
            fn = None
            m = re.search(rb"<FILENAME>([^\r\n<]+)", body)
            if m:
                fn = m.group(1).decode("ascii", "replace").strip()
            if b"<TEXT>" in body:
                inner = body.split(b"<TEXT>", 1)[1]
                inner = inner.rsplit(b"</TEXT>", 1)[0] if b"</TEXT>" in inner else inner
            else:
                inner = body
            blocks.append((fn, inner))
        return blocks

    blocks = doc_blocks_b(raw_sub)
    t3 = {"archive_files": [fn for fn, _ in blocks]}

    def find_block_b(fn_key: str) -> bytes:
        for fn, inner in blocks:
            if fn and fn_key in fn:
                return inner
        return b""

    def normalize_archive_b(inner: bytes) -> bytes:
        """Strip ONLY the literal <XBRL> wrapper markers EDGAR adds around the
        inline-XBRL primary document; touch nothing else (no rstrip)."""
        if inner.startswith(b"\n<XBRL>\n"):
            inner = inner[len(b"\n<XBRL>\n"):]
        elif inner.startswith(b"<XBRL>\n"):
            inner = inner[len(b"<XBRL>\n"):]
        if inner.endswith(b"</XBRL>\n"):
            inner = inner[: -len(b"</XBRL>\n")]
        return inner

    arch8 = find_block_b("d291965d8k.htm")
    archx = find_block_b("d291965dex991.htm")
    t3["found_8k_block"] = bool(arch8)
    t3["found_ex_block"] = bool(archx)

    cand8 = normalize_archive_b(arch8)
    t3["8k"] = {
        "origin_stripped_bytes": len(stripped8), "origin_stripped_sha": sha(stripped8),
        "archive_block_inner_bytes": len(arch8),
        "archive_inner_bytes": len(cand8), "archive_inner_sha": sha(cand8),
        "byte_identical": stripped8 == cand8,
        "reported_archive_inner_bytes": REPORTED_STRIPPED["8k_bytes"],
        "reported_archive_inner_sha": REPORTED_STRIPPED["8k_sha"],
        "match_reported": (len(cand8) == REPORTED_STRIPPED["8k_bytes"]
                           and sha(cand8) == REPORTED_STRIPPED["8k_sha"]),
        "occurs_byte_exact_in_submission": raw_sub.find(stripped8) >= 0,
        "occurrence_offset": raw_sub.find(stripped8),
    }
    # origin EX99.1 is SGML-wrapped: inner between <TEXT> and </TEXT> (bytes)
    if b"<TEXT>" in raw_ex:
        ex_inner_bytes = raw_ex.split(b"<TEXT>", 1)[1]
        ex_inner_bytes = ex_inner_bytes.rsplit(b"</TEXT>", 1)[0] if b"</TEXT>" in ex_inner_bytes else ex_inner_bytes
    else:
        ex_inner_bytes = raw_ex
    ex_inner_stripped = ex_inner_bytes.replace(segx, b"", 1)
    candx = normalize_archive_b(archx)
    t3["ex"] = {
        "origin_inner_bytes": len(ex_inner_bytes),
        "origin_inner_minus_script_bytes": len(ex_inner_stripped),
        "origin_inner_minus_script_sha": sha(ex_inner_stripped),
        "reported_bytes": REPORTED_STRIPPED["ex_inner_minus_script_bytes"],
        "reported_sha": REPORTED_STRIPPED["ex_inner_minus_script_sha"],
        "archive_block_inner_bytes": len(archx),
        "archive_inner_bytes": len(candx), "archive_inner_sha": sha(candx),
        "byte_identical": ex_inner_stripped == candx,
        "match_reported": (len(ex_inner_stripped) == REPORTED_STRIPPED["ex_inner_minus_script_bytes"]
                           and sha(ex_inner_stripped) == REPORTED_STRIPPED["ex_inner_minus_script_sha"]),
        "occurs_byte_exact_in_submission": raw_sub.find(ex_inner_stripped) >= 0,
        "occurrence_offset": raw_sub.find(ex_inner_stripped),
    }
    out["T3_independent_path"] = t3

    # ---------- quotes: load from acquisition provenance ----------
    acq = json.loads((ACQ_DIR / "provenance.json").read_text(encoding="utf-8"))
    quotes = acq["verbatim_quotes"]

    corpus_8k_md = read_bytes(ACQ_DIR / "corpus" / "MSFT_8K_2026-09-02_Item7.01.md")
    corpus_ex_md = read_bytes(ACQ_DIR / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.md")
    corpus_8k_b = read_bytes(ACQ_DIR / "corpus" / "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt")
    corpus_ex_b = read_bytes(ACQ_DIR / "corpus" / "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt")

    origin_text = {"8k": strip_html(decode(raw_8k)), "ex": strip_html(decode(raw_ex))}

    # P-A: byte span in corpus path A
    pa = []
    for q in quotes:
        data = corpus_8k_md if "Item7.01" in q["file"] else corpus_ex_md
        a, b = q["byte_span"]
        slice_ = data[a:b].decode("utf-8")
        pa.append({"id": q["id"], "span": [a, b], "exact": slice_ == q["text"],
                   "slice_len": len(slice_), "quote_len": len(q["text"])})
    out["P_A_corpus_pathA_exact"] = pa

    # P-B: path B whitespace-insensitive
    pb = []
    for q in quotes:
        data = corpus_8k_b if "Item7.01" in q["file"] else corpus_ex_b
        pb.append({"id": q["id"], "m1_hit": m1(q["text"]) in m1(decode(data))})
    out["P_B_corpus_pathB_m1"] = pb

    # ---------- M1/M2/M3 on origin carriers ----------
    rows = []
    for q in quotes:
        which = "8k" if "Item7.01" in q["file"] else "ex"
        t = origin_text[which]
        t_m1, t_m2 = m1(t), m2(t)
        r = {
            "id": q["id"], "carrier": which,
            "M1_ws_insensitive": m1(q["text"]) in t_m1,
            "M2_ws_collapsed": m2(q["text"]) in t_m2,
            "M3_ws_strict": q["text"] in t,
            "quote_len": len(q["text"]),
        }
        # raw ascii anchor check (origin carrier, byte level)
        anc = None
        anchor = None
        # anchors as recorded by R2 provenance for these quotes
        rows.append(r)
    out["M_quotes_on_origin"] = rows
    out["M_summary"] = {
        "M1": sum(r["M1_ws_insensitive"] for r in rows),
        "M2": sum(r["M2_ws_collapsed"] for r in rows),
        "M3": sum(r["M3_ws_strict"] for r in rows),
        "total": len(rows),
    }

    # raw ASCII anchor byte spans (R2 provenance) re-checked on origin carriers
    r2prov = json.loads((ORIGIN_DIR / "provenance.json").read_text(encoding="utf-8"))
    anchors = []
    for doc in r2prov["documents"]:
        q = doc["verbatim_quote"]
        data = raw_8k if "8-K 2026" in doc["document"] and "Exhibit" not in doc["document"] else raw_ex
        a, b = q["raw_anchor_span"]
        anchors.append({
            "document": doc["document"][:40],
            "span": [a, b],
            "slice_equals_raw_ascii_anchor": decode(data[a:b]) == q["raw_ascii_anchor"],
            "slice": decode(data[a:b]),
        })
    out["R2_anchor_spans_recheck"] = anchors

    # ---------- Q1(a) localisation: (1) space difference ----------
    def ctx(s: str, needle: str, before=90, after=140):
        i = s.find(needle)
        return s[max(0, i - before): i + after] if i >= 0 else None

    q1_corpus_slice = corpus_8k_md[quotes[0]["byte_span"][0]:quotes[0]["byte_span"][1]].decode("utf-8")
    out["Q1a_localisation"] = {
        "corpus_repr": repr(q1_corpus_slice),
        "origin_repr": repr(ctx(origin_text["8k"], "reportable segments:")),
        "corpus_has_space_after_1": "(1) Agents" in q1_corpus_slice,
        "corpus_has_nospace_after_1": "(1)Agents" in q1_corpus_slice,
        "origin_has_space_after_1": "(1) Agents" in m2(origin_text["8k"]),
        "origin_has_nospace_after_1": "(1)Agents" in m2(origin_text["8k"]),
        "origin_raw_html_repr": repr(ctx(decode(raw_8k), "(1)")),
        "normalized_equal_after_removing_all_ws": m1(q1_corpus_slice) == m1(q1_corpus_slice),
    }
    # exact diff of the Q1 sentence between corpus and origin (whitespace-collapsed)
    corr_sent = m2(q1_corpus_slice)
    org_sent = m2(ctx(origin_text["8k"], "reportable segments:") or "")
    out["Q1a_localisation"]["corpus_sentence"] = corr_sent
    out["Q1a_localisation"]["origin_sentence"] = org_sent

    # ---------- T4 full token diff origin <-> 4 corpus files ----------
    def toks(s: str):
        s = strip_urls(s)
        return {"numbers": set(num_tokens(s)), "words": set(word_tokens(s))}

    t4 = {}
    pairs = [
        ("8k", "MSFT_8K_2026-09-02_Item7.01.md", corpus_8k_md),
        ("8k", "MSFT_8K_2026-09-02_Item7.01.verify-w3c-html2txt.txt", corpus_8k_b),
        ("ex", "MSFT_8K_2026-09-02_Exhibit99-1.md", corpus_ex_md),
        ("ex", "MSFT_8K_2026-09-02_Exhibit99-1.verify-w3c-html2txt.txt", corpus_ex_b),
    ]
    for side, name, data in pairs:
        o = toks(origin_text[side])
        c = toks(decode(data))
        only_o_n = sorted(o["numbers"] - c["numbers"])
        only_c_n = sorted(c["numbers"] - o["numbers"])
        only_o_w = sorted(o["words"] - c["words"])
        only_c_w = sorted(c["words"] - o["words"])
        t4[name] = {
            "origin_numbers": len(o["numbers"]), "corpus_numbers": len(c["numbers"]),
            "only_in_origin_numbers": only_o_n, "only_in_corpus_numbers": only_c_n,
            "origin_words": len(o["words"]), "corpus_words": len(c["words"]),
            "only_in_origin_words": only_o_w, "only_in_corpus_words": only_c_w,
        }
    out["T4_token_diff"] = t4

    # ---------- mutations (oracle §5.1) ----------
    registry = {
        REPORTED_SHA["d291965d8k.htm"], REPORTED_SHA["d291965dex991.htm"],
        REPORTED_SHA["identity_index"], REPORTED_SHA["complete_submission"],
        REPORTED_SHA["origin_bytes.bin"],
    }

    def carrier_check(data: bytes, expected_sha: str | None = None) -> list[str]:
        fails = []
        h = sha(data)
        if h not in registry:
            fails.append(f"sha_not_in_origin_registry({h[:16]})")
        if expected_sha and h != expected_sha:
            fails.append("sha_mismatch_vs_registered")
        return fails

    def quote_check(data: bytes, quote_text: str, which: str = "8k") -> dict:
        t = strip_html(decode(data))
        return {"M1": m1(quote_text) in m1(t), "M2": m2(quote_text) in m2(t), "M3": quote_text in t}

    muts = []
    # G1 green (oracle §5.1 literal wording: real 8-K origin + real Q1, full M1/M2/M3)
    g1_f = carrier_check(raw_8k, REPORTED_SHA["d291965d8k.htm"])
    g1_q = quote_check(raw_8k, quotes[0]["text"])
    g1_pass = (not g1_f) and all(g1_q.values())
    muts.append({"id": "G1", "name": "真实 8-K origin + 真实 Q1（M1∧M2∧M3 全套）", "expected": "green",
                 "observed_pass": g1_pass, "carrier_fails": g1_f, "quote": g1_q, "rc": 0 if g1_pass else 1})
    # G1b green: the acceptance rule actually frozen in oracle §一/Q1④ =
    # registered origin sha + all 8 quotes M1-hit on their own carrier + P-A 8/8 exact
    g1b_carrier_ok = (not carrier_check(raw_8k, REPORTED_SHA["d291965d8k.htm"])
                      and not carrier_check(raw_ex, REPORTED_SHA["d291965dex991.htm"]))
    g1b_quotes = {r["id"]: r["M1_ws_insensitive"] for r in rows}
    g1b_pa = all(r["exact"] for r in pa)
    g1b_pass = g1b_carrier_ok and all(g1b_quotes.values()) and g1b_pa
    muts.append({"id": "G1b", "name": "验收规则（登记 sha + 8/8 M1 + P-A 8/8 逐字）", "expected": "green",
                 "observed_pass": g1b_pass, "carrier_ok": g1b_carrier_ok,
                 "quotes_m1": g1b_quotes, "P_A_8of8": g1b_pa, "rc": 0 if g1b_pass else 1})
    # R1 block page
    r1_f = carrier_check(raw_blk, REPORTED_SHA["d291965d8k.htm"])
    r1_q = quote_check(raw_blk, quotes[0]["text"])
    r1_red = bool(r1_f) and not all(r1_q.values())
    muts.append({"id": "R1", "name": "SEC 拦截页冒充 8-K origin", "expected": "red",
                 "observed_pass": r1_red, "carrier_fails": r1_f, "quote": r1_q, "rc": 0 if r1_red else 1})
    # R2 index
    r2_f = carrier_check(raw_idx, REPORTED_SHA["d291965d8k.htm"])
    r2_q = quote_check(raw_idx, quotes[0]["text"])
    r2_red = bool(r2_f) and not all(r2_q.values())
    muts.append({"id": "R2", "name": "EDGAR index 件冒充 8-K origin", "expected": "red",
                 "observed_pass": r2_red, "carrier_fails": r2_f, "quote": r2_q, "rc": 0 if r2_red else 1})
    # R3 corpus md as origin
    r3_f = carrier_check(corpus_8k_md, REPORTED_SHA["d291965d8k.htm"])
    r3_red = bool(r3_f)
    muts.append({"id": "R3", "name": "corpus 转写件冒充 origin 载体", "expected": "red",
                 "observed_pass": r3_red, "carrier_fails": r3_f, "rc": 0 if r3_red else 1})
    # R4 one byte flipped
    b4 = bytearray(raw_8k)
    b4[1000] ^= 0x01
    r4_f = carrier_check(bytes(b4), REPORTED_SHA["d291965d8k.htm"])
    r4_red = bool(r4_f)
    muts.append({"id": "R4", "name": "origin 拷贝翻转 1 字节", "expected": "red",
                 "observed_pass": r4_red, "carrier_fails": r4_f,
                 "flipped_offset": 1000, "rc": 0 if r4_red else 1})
    # R5 number mutated in quote
    q6 = quotes[5]["text"]
    q6_mut = q6.replace("$268,127", "$268,126")
    r5_q = quote_check(raw_ex, q6_mut)
    r5_red = not any(r5_q.values())
    muts.append({"id": "R5", "name": "引文改一个数字 ($268,127→$268,126)", "expected": "red",
                 "observed_pass": r5_red, "quote": r5_q, "rc": 0 if r5_red else 1})
    # R6 word mutated
    q4 = quotes[3]["text"]
    q4_mut = q4.replace("Agents", "Agent", 1)
    r6_q = quote_check(raw_ex, q4_mut)
    r6_red = not any(r6_q.values())
    muts.append({"id": "R6", "name": "引文改一个词 (Agents→Agent)", "expected": "red",
                 "observed_pass": r6_red, "quote": r6_q, "rc": 0 if r6_red else 1})
    # R7 whitespace-only mutation: remove one space from Q1
    q1 = quotes[0]["text"]
    q1_ws = q1.replace("(1)Agents", "(1) Agents", 1)
    r7_q = quote_check(raw_8k, q1_ws)
    r7_designed = (r7_q["M1"] is True) and (r7_q["M2"] is False)
    muts.append({"id": "R7", "name": "仅空白变异（补一个空格）", "expected": "M1绿/M2红（已知盲区登记）",
                 "observed_pass": r7_designed, "quote": r7_q, "rc": 0 if r7_designed else 1})

    out["mutations"] = muts
    reds = [m for m in muts if m["expected"] == "red"]
    greens = [m for m in muts if m["expected"] == "green"]
    by_id = {m["id"]: m for m in muts}
    out["mutation_summary"] = {
        "green_pass": sum(m["observed_pass"] for m in greens), "green_total": len(greens),
        "red_pass": sum(m["observed_pass"] for m in reds), "red_total": len(reds),
        "G1_literal_rc": by_id["G1"]["rc"],
        "G1_literal_reason": "M2/M3 拒绝 Q1 —— 因 origin 用 &#160;(NBSP)、语料用无空格，正是待裁的 Q2(a)",
        "G1b_rc": by_id["G1b"]["rc"],
        "r7_as_designed": by_id["R7"]["observed_pass"],
        "discrimination_ok": (by_id["G1b"]["observed_pass"]
                              and sum(m["observed_pass"] for m in reds) == len(reds)),
        "discrimination_ok_literal_G1": (by_id["G1"]["observed_pass"]
                                         and sum(m["observed_pass"] for m in reds) == len(reds)),
    }

    (HERE / "_verification_raw.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- concise stdout ----------
    print("T1 sha_match:", t1["sha_match"])
    print("T1 sizes_match:", t1["sizes_match"], "bin_is_concat:", t1["bin_is_concat"])
    print("corpus sha match:", {k: v["match"] for k, v in corpus.items()})
    print("T2 two_hits_identical:", t2["two_hits_byte_identical"],
          "| 8k/ex/index/sub occ:", t2["occurrences_in_8k"], t2["occurrences_in_ex"],
          t2["occurrences_in_index"], t2["occurrences_in_submission"])
    print("T2 stripped 8k match:", t2["stripped_8k"]["match"],
          "| stripped ex match:", t2["stripped_ex_raw"]["match"])
    print("T3 8k byte_identical:", t3["8k"]["byte_identical"], t3["8k"])
    print("T3 ex byte_identical:", t3["ex"]["byte_identical"], t3["ex"])
    print("P-A exact:", sum(r["exact"] for r in pa), "/", len(pa))
    print("P-B m1:", sum(r["m1_hit"] for r in pb), "/", len(pb))
    print("M summary (M1/M2/M3):", out["M_summary"])
    for r in rows:
        print("   ", r)
    print("anchors:", [(a["slice_equals_raw_ascii_anchor"], a["span"]) for a in anchors])
    print("Q1a:", json.dumps(out["Q1a_localisation"], ensure_ascii=False)[:1200])
    print("mutations:", [(m["id"], m["observed_pass"], m["rc"]) for m in muts],
          "discrimination_ok=", out["mutation_summary"]["discrimination_ok"])
    print("wrote", HERE / "_verification_raw.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
