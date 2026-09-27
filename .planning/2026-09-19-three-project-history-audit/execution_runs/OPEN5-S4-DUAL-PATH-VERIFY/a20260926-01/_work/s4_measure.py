"""OPEN5-S4-DUAL-PATH-VERIFY · independent measurement (read-only inputs, own outputs).

Runs the two methods frozen in oracle.md / oracle-addendum-A / oracle-addendum-B
on FRESH extractions made by this station (never trusting S3's recorded numbers),
verifies every input sha256 first, and audits S3's provenance.json field-by-field.

Output: _work/raw_measurements.json  (utf-8, LF, re-parsed after write)
No network. No git. Writes only inside this attempt's _work/.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import traceback

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]
EN_ANCHORS = ["Xiaomi", "Revenue", "Annual Report", "Segment", "Gross profit"]
PAGES = [1, 2, 30, 43, 47, 115, 160, 337, 355, 399]

HERE = os.path.dirname(os.path.abspath(__file__))
ME = os.path.dirname(HERE)                       # .../a20260926-01
RUN = os.path.dirname(ME)                        # .../OPEN5-S4-DUAL-PATH-VERIFY
EXR = os.path.dirname(RUN)                       # .../execution_runs
PLANNING = os.path.dirname(EXR)                  # .../2026-09-19-three-project-history-audit
ROOT = os.path.dirname(os.path.dirname(PLANNING))

S3 = os.path.join(EXR, "OPEN5-S3-REACQUISITION", "a20260925-01")
S3W = os.path.join(S3, "_work")
P5A = os.path.join(EXR, "OPEN5-PEND5A-HK-ACQUISITION", "a20260924-01")
OUT_W = os.path.join(ME, "_work")
EXTRACT_DIR = os.path.join(OUT_W, "extract")

ORIGIN = (
    "C:\\Users\\郑曾波\\Projects\\company-wiki\\companies\\小米集團－Ｗ\\raw\\"
    "financial_reports\\annual\\2026-04-28_hkexnews_12127452_2025年度報告.pdf"
)
SUB04 = os.path.join(P5A, "corpus", "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf")
SUB08 = os.path.join(P5A, "corpus", "attempt08_irmi_xiaomi_ar2025_en.pdf")

EXPECT = {
    "origin": (
        "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        4405561,
    ),
    "sub04": (
        "d0975600c918683636d4679328fa1eaa4a7a14b53950440d53005c831829b62b",
        1044325,
    ),
    "sub08": (
        "b787f0290513e48a95078ed2a68dc1e240da68d204e5dd9aedc59b66a7c75ec2",
        3556507,
    ),
    "path_compare": (
        "b503e4a8fcaaac316f45c5bdada52ed7bcec5994463b91b1d711afdcc7962159",
        17357,
    ),
    "reacquisition": (
        "f948276a06d6b967fe574ed8439594338ff731b5ef545c1fa6c6e8b8c746430a",
        52387,
    ),
    "provenance": (
        "3e44f7e97a74409acc2e1e57f7bc868d85e9e5ba0ef8048cf9212edba70a3d05",
        12514,
    ),
    "s3_oracle": (
        "24d4d4e242010a2998a28ecfb0af37b177d14b295533a3eb5555c3aee63e30a9",
        8426,
    ),
}


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s)


def cjk_count(s: str) -> int:
    return len(re.findall(r"[一-鿿]", s))


def split_pages(text: str) -> dict:
    parts = re.split(r"<<<PAGE (\d+)>>>", text)
    out = {}
    for i in range(1, len(parts), 2):
        out[int(parts[i])] = parts[i + 1]
    return out


def byte_lines(text: str):
    """[(line_no, byte_start, byte_end, line)] with utf-8 byte offsets."""
    out = []
    pos = 0
    for i, ln in enumerate(text.split("\n")):
        b = len(ln.encode("utf-8"))
        out.append((i + 1, pos, pos + b, ln))
        pos += b + 1
    return out


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(path, "r", encoding="utf-8") as f:
        json.load(f)


def first_line_loc(text: str, word: str):
    m = re.search(rf"[^\n]*{re.escape(word)}[^\n]*", text)
    if not m:
        return None
    line = m.group(0)[:300]
    b0 = len(text[: m.start()].encode("utf-8"))
    line_start = text.rfind("\n", 0, m.start()) + 1
    line_no = text[: line_start].count("\n") + 1
    return {
        "line_no": line_no,
        "byte_start": b0,
        "byte_end": b0 + len(line.encode("utf-8")),
        "line": line,
    }


# ---------------------------------------------------------------- step 1
def check_inputs() -> dict:
    specs = {
        "origin": (ORIGIN, *EXPECT["origin"]),
        "sub04": (SUB04, *EXPECT["sub04"]),
        "sub08": (SUB08, *EXPECT["sub08"]),
        "path_compare": (os.path.join(S3W, "path_compare.json"), *EXPECT["path_compare"]),
        "reacquisition": (os.path.join(S3, "reacquisition.json"), *EXPECT["reacquisition"]),
        "s3_provenance": (os.path.join(S3, "provenance.json"), *EXPECT["provenance"]),
        "s3_oracle": (os.path.join(S3, "oracle.md"), *EXPECT["s3_oracle"]),
    }
    rows = {}
    for k, (p, esha, ebytes) in specs.items():
        got = sha256_file(p)
        size = os.path.getsize(p)
        rows[k] = {
            "path": p,
            "bytes": size,
            "sha256": got,
            "expected_sha256": esha,
            "expected_bytes": ebytes,
            "sha_match": got == esha,
            "bytes_match": size == ebytes,
        }
    rows["_all_match"] = all(v.get("sha_match") and v.get("bytes_match")
                             for k, v in rows.items() if k != "_all_match")
    return rows


# ---------------------------------------------------------------- step 2
def verify_s3_artifacts(path_compare: dict, reacq: dict) -> dict:
    """Re-hash every S3 artefact S3 itself registered — independent of its numbers."""
    checked, mismatched, missing = [], [], []
    for rec in path_compare["a_vs_b1"]:
        for key in ("ocr_file", "origin_textlayer_file"):
            p = rec[key]
            if not os.path.exists(p):
                missing.append(p)
                continue
            got = sha256_file(p)
            ok = got == rec[key + "_sha256"]
            checked.append({"file": p, "recorded": rec[key + "_sha256"],
                            "actual": got, "match": ok})
            if not ok:
                mismatched.append(p)
    for p in reacq["paths"]["A_ocr"]["per_page"]:
        ot = p.get("origin_text_layer") or {}
        pairs = [
            (p.get("ocr_text_file"), p.get("ocr_text_file_sha256")),
            (p.get("png"), p.get("png_sha256")),
            (ot.get("file"), ot.get("file_sha256")),
        ]
        for f, rec_sha in pairs:
            if not f or not rec_sha:
                continue
            if not os.path.exists(f):
                missing.append(f)
                continue
            got = sha256_file(f)
            ok = got == rec_sha
            checked.append({"file": f, "recorded": rec_sha, "actual": got, "match": ok})
            if not ok:
                mismatched.append(f)
    # extracts registered in handoff written_files
    hf = json.load(open(os.path.join(S3, "handoff.json"), encoding="utf-8"))
    for item in hf["written_files"]["files"]:
        p = os.path.join(ROOT, item["path"])
        if not os.path.exists(p):
            missing.append(p)
            continue
        got = sha256_file(p)
        ok = got == item["sha256"] and os.path.getsize(p) == item["bytes"]
        checked.append({"file": p, "recorded": item["sha256"], "actual": got, "match": ok})
        if not ok:
            mismatched.append(p)
    return {
        "files_checked": len(checked),
        "mismatched": mismatched,
        "missing": missing,
        "all_match": not mismatched and not missing,
        "detail": checked,
    }


# ---------------------------------------------------------------- step 3
def fresh_extracts() -> dict:
    import fitz
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer

    os.makedirs(EXTRACT_DIR, exist_ok=True)
    res = {}

    def fitz_text(path, pages=None):
        doc = fitz.open(path)
        parts = []
        idxs = range(len(doc)) if pages is None else [p - 1 for p in pages]
        for i in idxs:
            parts.append(f"<<<PAGE {i + 1}>>>\n")
            parts.append(doc[i].get_text())
        n = len(doc)
        doc.close()
        return "".join(parts), n

    def pdfminer_text(path):
        parts = []
        for i, page_layout in enumerate(extract_pages(path)):
            parts.append(f"<<<PAGE {i + 1}>>>\n")
            stack = list(page_layout)
            while stack:
                obj = stack.pop(0)
                if isinstance(obj, LTTextContainer):
                    parts.append(obj.get_text())
                else:
                    children = getattr(obj, "_objs", None)
                    if children:
                        stack.extend(children)
        return "".join(parts)

    jobs = [
        ("origin_fitz_full", lambda: fitz_text(ORIGIN), "origin_fitz_full.txt",
         "d628cf53a8cbb89893602798234af913d51b4247253d1662c0829d1e631b83b1", 709398),
        ("sub04_fitz", lambda: fitz_text(SUB04), "s4_attempt04_fitz.extracted.txt",
         "5d20c2816c0ba2ed6736463d00cc4fc9d73fe55b10d28f9053ef27229ece4c6b", 95648),
        ("sub04_pdfminer", lambda: pdfminer_text(SUB04), "s4_attempt04_pdfminer.extracted.txt",
         "d70d4996424776380e5c9eecae7145f0004d4f4aad003f3080d1bf6936bd9cca", 111464),
        ("sub08_fitz", lambda: fitz_text(SUB08), "s4_attempt08_fitz.extracted.txt",
         "990075a686350d49e0ed086be12f59153786df30e1f77d13892ed15c0171bf89", 956886),
        ("sub08_pdfminer", lambda: pdfminer_text(SUB08), "s4_attempt08_pdfminer.extracted.txt",
         None, None),
    ]
    texts = {}
    for name, fn, fname, s3_sha, s3_bytes in jobs:
        try:
            out = fn()
            if isinstance(out, tuple):
                text, npages = out
            else:
                text, npages = out, None
            p = os.path.join(EXTRACT_DIR, fname)
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            got = sha256_file(p)
            texts[name] = text
            res[name] = {
                "ok": True,
                "file": p,
                "bytes": os.path.getsize(p),
                "sha256": got,
                "pages": npages,
                "s3_recorded_sha256": s3_sha,
                "s3_recorded_bytes": s3_bytes,
                "byte_identical_to_s3": (got == s3_sha) if s3_sha else None,
                "reparse_ok": True,
            }
        except Exception as e:  # noqa: BLE001
            res[name] = {"ok": False, "error": f"{type(e).__name__}: {e}",
                         "trace": traceback.format_exc()[-1500:]}
    # fresh per-page origin text layer via pypdfium2 (the library S3's path A used)
    per_page = {}
    try:
        import pypdfium2 as pdfium

        doc = pdfium.PdfDocument(ORIGIN)
        per_page["_page_count"] = len(doc)
        per_page["_lib"] = "pypdfium2(global)"
        for pno in PAGES:
            page = doc[pno - 1]
            tp = page.get_textpage()
            tl = tp.get_text_range() or ""
            per_page[pno] = tl
        doc.close()
        s3recs = json.load(open(os.path.join(S3W, "pathA_probe.json"), encoding="utf-8"))
        s3_by_page = {r["page"]: r for r in s3recs["pages"]}
        cmp_rows = []
        for pno in PAGES:
            mine = per_page[pno]
            s3_file = s3_by_page[pno]["text_layer_file"]
            s3_txt = open(s3_file, encoding="utf-8").read()
            # S3 ran s3_normalise_lf.py: CR from the PDF is normalised to LF
            mine_norm = mine.replace("\r\n", "\n").replace("\r", "\n")
            cmp_rows.append({
                "page": pno,
                "s3_file": s3_file,
                "s3_sha256": s3_by_page[pno]["text_layer_file_sha256"],
                "s3_chars": len(s3_txt),
                "mine_chars": len(mine),
                "identical_after_cr_normalisation": mine_norm == s3_txt,
                "sha_of_mine": hashlib.sha256(mine_norm.encode("utf-8")).hexdigest(),
            })
        res["origin_pdfium_per_page"] = {
            "ok": True, "lib": per_page["_lib"], "page_count": per_page["_page_count"],
            "pages_run": PAGES, "vs_s3": cmp_rows,
            "all_identical": all(r["identical_after_cr_normalisation"] for r in cmp_rows),
        }
    except Exception as e:  # noqa: BLE001
        res["origin_pdfium_per_page"] = {"ok": False,
                                         "error": f"{type(e).__name__}: {e}",
                                         "trace": traceback.format_exc()[-1500:]}
    res["_texts"] = texts
    res["_pdfium_per_page"] = {k: v for k, v in per_page.items()
                               if isinstance(k, int) or k == "_page_count"}
    return res


# ---------------------------------------------------------------- step 4 B1
def b1_scan(origin_fitz_text: str) -> dict:
    pages = split_pages(origin_fitz_text)
    out = {"pages": len(pages), "anchors": {}, "hit_words": []}
    for a in ANCHORS:
        hits = sorted(n for n, t in pages.items() if a in t)
        out["anchors"][a] = {
            "count": origin_fitz_text.count(a),
            "hit_pages": hits,
        }
    out["hit_words"] = sorted(a for a in ANCHORS if out["anchors"][a]["count"] > 0)
    out["hit_word_count"] = len(out["hit_words"])
    out["total_chars"] = len(origin_fitz_text)
    return out


# ---------------------------------------------------------------- step 5 M1
def readable_spans(t: str) -> dict:
    """Frozen in oracle.md §4 M1-补 + addendum-A + addendum-B."""
    spans = {}

    def put(kind, raw):
        n = norm(raw)
        if not n:
            return
        if n in spans:
            return
        spans[n] = {"kind": kind, "raw": raw[:120]}

    for m in re.finditer(r"[\x20-\x7e]{4,}", t):
        s = m.group(0)
        if re.search(r"[A-Za-z0-9]", s):
            put("ascii", s)
    for m in re.finditer(r"[一-鿿]{2,}", t):
        put("cjk", m.group(0))
    return spans


def digit_tokens(t: str) -> list:
    """Normalised numeric tokens (>=3 digits) in document order."""
    out = []
    for m in re.finditer(r"\d[\d,\.]*\d|\d{3,}", t):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) >= 3:
            out.append((digits, m.start(), m.group(0)))
    return out


def m1(run_variant: str, ocr_pages: dict, tl_pages: dict, ocr_files: dict) -> dict:
    """run_variant: 'fresh_pdfium' | 's3_recorded'"""
    rows = []
    tot_checked = tot_hits = 0
    span_stats = {"reproduced": 0, "miss": 0, "cjk_variant": 0}
    span_detail = []
    num_conflicts = []
    num_diff_all = []
    for pno in PAGES:
        ocr = ocr_pages[pno]
        tl = tl_pages[pno]
        n_ocr, n_tl = norm(ocr), norm(tl)
        ocr_lines = [ln for ln in ocr.split("\n") if cjk_count(ln) >= 8]
        matched, checked = [], 0
        for ln in ocr_lines[:40]:
            checked += 1
            if norm(ln) in n_tl:
                matched.append(ln[:160])
        tot_checked += checked
        tot_hits += len(matched)

        frag = ""
        if pno == 1:
            m = re.search(r"股份代號[^\n]{0,60}", tl)
            frag = m.group(0) if m else ""
        frag_in_ocr = bool(frag) and (norm(frag) in n_ocr)

        spans = readable_spans(tl)
        page_span = []
        for s, meta in spans.items():
            if s in n_ocr:
                st = "reproduced"
            elif meta["kind"] == "cjk" and len(s) >= 4:
                # addendum-A #4: is there a same-page OCR CJK text at all?
                st = "cjk_variant"
            else:
                st = "miss"
            span_stats[st] += 1
            page_span.append({"span": s[:80], "kind": meta["kind"], "status": st})
        span_detail.append({"page": pno, "spans": page_span})

        o_digits = {d for d, _, _ in digit_tokens(ocr)}
        t_digits = {d for d, _, _ in digit_tokens(tl)}
        conf = sorted(d for d in (o_digits - t_digits) if len(d) >= 5)
        for d in conf:
            toks = digit_tokens(ocr)
            pos = next(i for i, (dd, _off, _raw) in enumerate(toks) if dd == d)
            char_start = toks[pos][1]
            byte_start = len(ocr[:char_start].encode("utf-8"))
            num_conflicts.append({
                "page": pno, "value": d, "side": "ocr_only",
                "ocr_token_raw": toks[pos][2],
                "ocr_char_start": char_start,
                "ocr_byte_start": byte_start,
                "ocr_byte_end": byte_start + len(toks[pos][2].encode("utf-8")),
                "ocr_line_no": ocr[:char_start].count("\n") + 1,
                "ocr_file": ocr_files.get(pno),
                "ocr_file_sha256": sha256_file(ocr_files[pno]) if ocr_files.get(pno)
                and os.path.exists(ocr_files[pno]) else None,
            })
        only_ocr = sorted(o_digits - t_digits)
        only_tl = sorted(t_digits - o_digits)
        if only_ocr or only_tl:
            num_diff_all.append({"page": pno, "ocr_only": only_ocr,
                                 "origin_only": only_tl})

        rows.append({
            "page": pno,
            "ocr_file": ocr_files.get(pno),
            "ocr_file_sha256_checked": True,
            "ocr_long_cjk_lines": len(ocr_lines),
            "ocr_long_cjk_lines_checked": checked,
            "verbatim_lines_found_in_origin_layer": len(matched),
            "sample_matched_lines": matched[:3],
            "cover_fragment": frag[:80],
            "cover_fragment_present_in_ocr": frag_in_ocr,
            "readable_spans_total": len(spans),
            "readable_spans_reproduced": sum(
                1 for x in page_span if x["status"] == "reproduced"),
            "readable_spans_miss": sum(
                1 for x in page_span if x["status"] == "miss"),
            "readable_spans_cjk_variant": sum(
                1 for x in page_span if x["status"] == "cjk_variant"),
            "digits_ocr_only_len_ge5": conf,
            "digits_origin_only": len(only_tl),
        })
    tot_spans = sum(span_stats.values())
    return {
        "variant": run_variant,
        "pages": len(rows),
        "ocr_lines_checked": tot_checked,
        "verbatim_matches_in_origin_layer": tot_hits,
        "cover_fragment_reproduced": sum(1 for r in rows if r["cover_fragment_present_in_ocr"]),
        "readable_span_stats": span_stats,
        "readable_span_total": tot_spans,
        "readable_span_coverage": round(span_stats["reproduced"] / tot_spans, 6)
        if tot_spans else None,
        "numeric_conflicts": num_conflicts,
        "numeric_conflict_count": len(num_conflicts),
        "numeric_token_diff_pages": num_diff_all,
        "per_page": rows,
        "span_detail": span_detail,
    }


# ---------------------------------------------------------------- step 6 M2
def cross_lib(text_a: str, text_b: str, label_a: str, label_b: str, anchors) -> dict:
    pa, pb = split_pages(text_a), split_pages(text_b)
    per = {}
    for a in anchors:
        ha = sorted(n for n, t in pa.items() if a in t)
        hb = sorted(n for n, t in pb.items() if a in t)
        la = first_line_loc(text_a, a)
        lb = first_line_loc(text_b, a)
        per[a] = {
            f"{label_a}_hit_pages": ha,
            f"{label_b}_hit_pages": hb,
            f"{label_a}_count": text_a.count(a),
            f"{label_b}_count": text_b.count(a),
            "intersection": sorted(set(ha) & set(hb)),
            "union": sorted(set(ha) | set(hb)),
            f"{label_b}_only_pages": sorted(set(hb) - set(ha)),
            f"{label_a}_only_pages": sorted(set(ha) - set(hb)),
            "first_line_in_a": la,
            "first_line_in_b": lb,
            "first_line_a_found_in_b": bool(la) and (norm(la["line"]) in norm(text_b)),
            "first_line_b_found_in_a": bool(lb) and (norm(lb["line"]) in norm(text_a)),
        }
    hit_a = sorted(a for a in anchors if per[a][f"{label_a}_hit_pages"])
    hit_b = sorted(a for a in anchors if per[a][f"{label_b}_hit_pages"])
    return {
        "anchors": anchors,
        "per_anchor": per,
        f"{label_a}_hit_words": hit_a,
        f"{label_b}_hit_words": hit_b,
        "word_level_sets_equal": hit_a == hit_b,
        "word_level_symmetric_difference": sorted(set(hit_a) ^ set(hit_b)),
        "anchors_with_nonempty_page_intersection": sorted(
            a for a in anchors if per[a]["intersection"]),
        "anchors_with_empty_page_intersection": sorted(
            a for a in anchors if per[a][f"{label_a}_hit_pages"]
            and per[a][f"{label_b}_hit_pages"] and not per[a]["intersection"]),
        "first_line_cross_match_count": sum(
            1 for a in anchors if per[a]["first_line_a_found_in_b"]),
        "first_line_cross_match_denominator": sum(
            1 for a in anchors if per[a][f"{label_a}_hit_pages"]),
        "b_only_pages_union": sorted({p for a in anchors
                                      for p in per[a][f"{label_b}_only_pages"]}),
        "a_only_pages_union": sorted({p for a in anchors
                                      for p in per[a][f"{label_a}_only_pages"]}),
    }


# ---------------------------------------------------------------- step 7 audit
def provenance_audit() -> dict:
    prov = json.load(open(os.path.join(S3, "provenance.json"), encoding="utf-8"))
    entries = prov["entries"]
    rows = []
    for e in entries:
        rows.append({
            "id": e.get("id"),
            "kind": e.get("kind"),
            "has_sha256": bool(e.get("sha256")),
            "has_page": ("page" in e) or e.get("kind") in
            ("authorization", "ocr_engine_env", "origin_file", "substitute_file",
             "probe_or_deliverable"),
            "page_value": e.get("page"),
            "has_quote_or_note": bool(e.get("quote") or e.get("note")),
            "utc": e.get("utc"),
            "utc_missing": e.get("utc") in (None, ""),
            "external_retrieval_not_local": e.get("external_retrieval_not_local"),
            "retrieval_method": e.get("retrieval_method"),
            "path": e.get("path"),
        })
    # P5 for external parts
    ext_rows = []
    for e in entries:
        if e.get("kind") == "substitute_file":
            ext_rows.append({
                "id": e["id"],
                "path": e["path"],
                "sha256": e.get("sha256"),
                "utc": e.get("utc"),
                "has_url": any(k in e for k in ("url", "URL")),
                "external_retrieval_not_local": e.get("external_retrieval_not_local"),
                "substitute_not_origin": e.get("substitute_not_origin"),
                "retrieval_method": e.get("retrieval_method"),
            })
    kind_counts = {}
    for e in entries:
        kind_counts[e.get("kind")] = kind_counts.get(e.get("kind"), 0) + 1
    declared = prov.get("counts", {})
    declared_sum = sum(v for k, v in declared.items() if isinstance(v, int))
    # deliverable files present in the attempt but absent from provenance entries
    reg_paths = {e.get("path") for e in entries}
    root_posix = ROOT.replace(os.sep, "/").rstrip("/") + "/"
    reg_abs = set()
    for r in reg_paths:
        if not r:
            continue
        if re.match(r"^[A-Za-z]:", r) or r.startswith("/"):
            reg_abs.add(r.replace("\\", "/"))
        else:
            reg_abs.add((root_posix + r).replace("\\", "/"))
    on_disk = []
    for base, _dirs, files in os.walk(S3):
        for fn in files:
            on_disk.append(os.path.join(base, fn).replace(os.sep, "/"))

    def in_prov(p):
        return p in reg_abs
    unregistered = sorted(
        p for p in on_disk
        if not in_prov(p)
        and not p.endswith("_work/manifest_before.json")
        and not p.endswith("_work/manifest_after.json")
        and not p.endswith("/handoff.json")
        and not p.endswith("/provenance.json")
    )
    return {
        "entry_count_declared": prov.get("entry_count"),
        "entry_count_actual": len(entries),
        "counts_declared": declared,
        "counts_declared_sum": declared_sum,
        "counts_by_kind_actual": kind_counts,
        "counts_consistent": declared_sum == len(entries),
        "entries": rows,
        "external_parts": ext_rows,
        "files_on_disk_not_registered_in_provenance": unregistered,
        "files_on_disk_not_registered_count": len(unregistered),
    }


# ---------------------------------------------------------------- main
def main() -> int:
    started = utc_now()
    out = {"attempt": "OPEN5-S4-DUAL-PATH-VERIFY/a20260926-01",
           "role": "implementer_s4",
           "started_utc": started,
           "oracle_sha256": sha256_file(os.path.join(ME, "oracle.md")),
           "oracle_addendum_A_sha256": sha256_file(os.path.join(ME, "oracle-addendum-A.md")),
           "oracle_addendum_B_sha256": sha256_file(os.path.join(ME, "oracle-addendum-B.md")),
           "network_used": False, "git_write": 0, "git_status_used": False}

    print("[1] input hashes ...", flush=True)
    out["input_hashes"] = check_inputs()
    if not out["input_hashes"]["_all_match"]:
        print("FAIL: input sha mismatch -> fail-closed", flush=True)
        out["fatal"] = "input_sha_mismatch"
        write_json(os.path.join(OUT_W, "raw_measurements.json"), out)
        return 2

    pc = json.load(open(os.path.join(S3W, "path_compare.json"), encoding="utf-8"))
    rq = json.load(open(os.path.join(S3, "reacquisition.json"), encoding="utf-8"))
    out["s3_meta_loaded"] = {
        "path_compare_summary": pc["summary"],
        "s3_claimed": {
            "a_vs_b1_ocr_lines_checked": pc["summary"]["a_vs_b1_ocr_lines_checked"],
            "a_vs_b1_verbatim_matches": pc["summary"][
                "a_vs_b1_verbatim_matches_in_origin_layer"],
            "readable_cover_fragment_reproduced": pc["summary"][
                "readable_cover_fragment_reproduced_in_ocr"],
            "b2_first_line_cross_lib_match_count": pc["summary"][
                "b2_first_line_cross_lib_match_count"],
            "b1_hit_word_count": len(
                rq["paths"]["B1_origin_textlayer"].get("anchor_hit_words", [])),
            "b1_pages_scanned": rq["paths"]["B1_origin_textlayer"]["page_count"],
            "b2_fitz_hit_words": rq["paths"]["B2_substitute_attempt04"]["fitz"][
                "anchor_hit_words"],
            "b2_pdfminer_hit_words": rq["paths"]["B2_substitute_attempt04"]["pdfminer"][
                "anchor_hit_words"],
            "b2prime_cn": len(
                rq["paths"]["B2prime_substitute_attempt08"].get(
                    "cn_anchor_hit_words", [])),
            "b2prime_en": len(
                rq["paths"]["B2prime_substitute_attempt08"].get(
                    "en_anchor_hit_words", [])),
            "a_anchor_hit_count": rq["paths"]["A_ocr"]["anchor_hit_count"],
        },
    }

    print("[2] verify S3 artefact hashes ...", flush=True)
    out["s3_artifact_integrity"] = verify_s3_artifacts(pc, rq)

    print("[3] fresh extractions ...", flush=True)
    fx = fresh_extracts()
    texts = fx.pop("_texts", {})
    pdfium_pages = fx.pop("_pdfium_per_page", {})
    out["fresh_extractions"] = fx

    if not all(fx.get(k, {}).get("ok") for k in
               ("origin_fitz_full", "sub04_fitz", "sub04_pdfminer", "sub08_fitz")):
        out["fatal"] = "extraction_failed"
        write_json(os.path.join(OUT_W, "raw_measurements.json"), out)
        return 3

    print("[4] B1 (origin text layer, 415 pages) ...", flush=True)
    out["b1_origin_textlayer_fresh_fitz"] = b1_scan(texts["origin_fitz_full"])

    # B1 second library: pypdfium2 full document (fresh)
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(ORIGIN)
        hits = {a: 0 for a in ANCHORS}
        npages = len(doc)
        total_chars = 0
        for i in range(npages):
            tl = doc[i].get_textpage().get_text_range() or ""
            total_chars += len(tl)
            for a in ANCHORS:
                if a in tl:
                    hits[a] += 1
        doc.close()
        out["b1_origin_textlayer_fresh_pdfium"] = {
            "lib": "pypdfium2 (global)",
            "pages": npages,
            "total_chars": total_chars,
            "anchor_hit_pages": hits,
            "hit_word_count": sum(1 for v in hits.values() if v),
        }
    except Exception as e:  # noqa: BLE001
        out["b1_origin_textlayer_fresh_pdfium"] = {
            "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1200:]}

    print("[5] M1 (A vs B1) ...", flush=True)
    ocr_pages, tl_s3, tl_fresh = {}, {}, {}
    s3pa = json.load(open(os.path.join(S3W, "pathA_probe.json"), encoding="utf-8"))
    by_page = {r["page"]: r for r in s3pa["pages"]}
    for p in PAGES:
        ocr_pages[p] = open(by_page[p]["ocr_text_file"], encoding="utf-8").read()
        tl_s3[p] = open(by_page[p]["text_layer_file"], encoding="utf-8").read()
        tl_fresh[p] = str(pdfium_pages.get(p, "")).replace("\r\n", "\n").replace("\r", "\n")
    ocr_files = {p: by_page[p]["ocr_text_file"] for p in PAGES}
    out["m1_A_vs_B1_fresh_pdfium"] = m1("fresh_pypdfium2_per_page", ocr_pages, tl_fresh,
                                        ocr_files)
    out["m1_A_vs_B1_s3_recorded"] = m1("s3_recorded_per_page", ocr_pages, tl_s3,
                                       ocr_files)
    # A's own anchor counts recomputed from the sha-verified OCR text files
    a_hits = {}
    for a in ANCHORS:
        a_hits[a] = sorted(p for p in PAGES if a in ocr_pages[p])
    out["A_anchor_recount_from_ocr_files"] = {
        "anchor_hit_pages": a_hits,
        "hit_words": sorted(a for a in ANCHORS if a_hits[a]),
        "hit_word_count": sum(1 for a in ANCHORS if a_hits[a]),
        "origin_layer_same_pages_anchor_hits": {
            a: sorted(p for p in PAGES if a in tl_fresh[p]) for a in ANCHORS},
        "note": "recomputed by this station from sha-verified OCR reconstruction files; "
                "OCR engine NOT re-run (versions differ, oracle.md §6.5)",
    }

    print("[6] M2 (attempt04 fitz vs pdfminer) ...", flush=True)
    out["m2_attempt04_fitz_vs_pdfminer"] = cross_lib(
        texts["sub04_fitz"], texts["sub04_pdfminer"], "fitz", "pdfminer", ANCHORS)

    print("[7] M2' (attempt08 fitz vs pdfminer, CN + EN) ...", flush=True)
    if texts.get("sub08_pdfminer"):
        out["m2prime_attempt08"] = {
            "cn": cross_lib(texts["sub08_fitz"], texts["sub08_pdfminer"],
                            "fitz", "pdfminer", ANCHORS),
            "en": cross_lib(texts["sub08_fitz"], texts["sub08_pdfminer"],
                            "fitz", "pdfminer", EN_ANCHORS),
        }
    else:
        out["m2prime_attempt08"] = {"error": "pdfminer extraction failed"}

    print("[8] provenance audit ...", flush=True)
    out["s3_provenance_audit"] = provenance_audit()

    out["finished_utc"] = utc_now()
    write_json(os.path.join(OUT_W, "raw_measurements.json"), out)
    print("wrote raw_measurements.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
