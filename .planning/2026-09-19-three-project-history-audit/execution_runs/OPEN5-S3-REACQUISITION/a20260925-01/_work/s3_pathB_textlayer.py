"""OPEN5-S3-REACQUISITION · Path B (text-layer / readable-substitute re-check).

B1  : origin text layer of the HK original — PyMuPDF full 415-page scan + the
      same sampled pages — recorded as CONTRAST only (RC-1 predicts 0 hits).
B2  : PEND-5a local substitutes (attempt04 hkexnews FY2025 results announcement)
      extracted by TWO independent libraries (PyMuPDF, pdfminer.six).
B2' : attempt08 (annual report EN) — Chinese anchors + English anchors.

All output is TEXT-LAYER extraction (not OCR, not a rebuild); substitutes are
marked `substitute_not_origin`. Inputs are READ-ONLY.

Usage:
  s3_pathB_textlayer.py --origin <pdf> --attempt04 <pdf> --attempt08 <pdf> \
                        --expect-origin-sha <sha> --pages 1,2,... \
                        --extractdir <dir> --out <out.json> --anchors a,b,... \
                        --en-anchors a,b,...
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import time


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_all(text: str, word: str) -> int:
    return text.count(word)


def locate(text: str, word: str) -> dict | None:
    """First occurrence: page (from `<<<PAGE n>>>` markers), line no, byte range."""
    idx = text.find(word)
    if idx < 0:
        return None
    prefix = text[:idx]
    page = None
    marker = "<<<PAGE "
    pos = 0
    while True:
        p = text.find(marker, pos)
        if p < 0 or p > idx:
            break
        end = text.find(">>>", p)
        page = int(text[p + len(marker) : end])
        pos = end
    line_no = prefix.count("\n") + 1
    b0 = len(prefix.encode("utf-8"))
    line_start = text.rfind("\n", 0, idx) + 1
    line_end = text.find("\n", idx)
    if line_end < 0:
        line_end = len(text)
    return {
        "page": page,
        "line_no": line_no,
        "byte_start": b0,
        "byte_end": b0 + len(word.encode("utf-8")),
        "line": text[line_start:line_end][:300],
    }


def write_extract(path: str, text: str) -> dict:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", mode=0o777, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(path, "r", encoding="utf-8") as f:
        f.read()
    return {"file": path, "bytes": os.path.getsize(path), "sha256": sha256_file(path)}


def fitz_extract(path: str, pages: list[int] | None = None) -> str:
    import fitz  # noqa: PLC0415

    doc = fitz.open(path)
    parts = []
    idxs = range(len(doc)) if pages is None else [p - 1 for p in pages]
    for i in idxs:
        parts.append(f"<<<PAGE {i + 1}>>>\n")
        parts.append(doc[i].get_text())
    doc.close()
    return "".join(parts)


def pdfminer_extract(path: str) -> str:
    """Single pass with `<<<PAGE n>>>` markers so page attribution matches fitz."""
    from pdfminer.high_level import extract_pages  # noqa: PLC0415
    from pdfminer.layout import LTTextContainer  # noqa: PLC0415

    parts: list[str] = []
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


def anchor_summary(text: str, anchors: list[str]) -> dict:
    per = {}
    for a in anchors:
        pages = set()
        pos = 0
        while True:
            i = text.find(a, pos)
            if i < 0:
                break
            pre = text[:i]
            m = None
            p = 0
            while True:
                q = text.find("<<<PAGE ", p)
                if q < 0 or q > i:
                    break
                m = int(text[q + 8 : text.find(">>>", q)])
                p = text.find(">>>", q)
            if m:
                pages.add(m)
            pos = i + len(a)
        loc = locate(text, a)
        per[a] = {
            "count": count_all(text, a),
            "hit_pages": sorted(pages),
            "first_hit": loc,
        }
    return per


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", required=True)
    ap.add_argument("--attempt04", required=True)
    ap.add_argument("--attempt08", required=True)
    ap.add_argument("--expect-origin-sha", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--extractdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--en-anchors", default="")
    args = ap.parse_args()

    pages = [int(x) for x in args.pages.split(",") if x.strip()]
    anchors = [a for a in args.anchors.split(",") if a]
    en_anchors = [a for a in args.en_anchors.split(",") if a]

    os.makedirs(args.extractdir, mode=0o777, exist_ok=True)
    out: dict = {
        "label": "s3_pathB",
        "path": "B_text_layer_and_substitute",
        "attempt": "OPEN5-S3-REACQUISITION/a20260925-01",
        "started_utc": utc_now(),
        "anchors": anchors,
        "en_anchors": en_anchors,
        "retrieval_method": "local_readonly_reuse_of_prior_attempt_bytes",
        "external_retrieval_not_local": False,
        "inputs": [],
        "b1_origin_textlayer": {},
        "b2_attempt04": {},
        "b2prime_attempt08": {},
        "rc": 1,
    }

    origin_sha = sha256_file(args.origin)
    out["inputs"].append(
        {
            "role": "origin_HK-XIAOMI-AR2025",
            "path": args.origin,
            "bytes": os.path.getsize(args.origin),
            "sha256": origin_sha,
            "matches_frozen_baseline": origin_sha == args.expect_origin_sha,
            "access": "read_only",
            "retrieved_utc": "n/a_local_bytes",
        }
    )
    for role, p, rutc in [
        (
            "substitute_attempt04_hkexnews_fy2025_results_zh",
            args.attempt04,
            "2026-09-24T22:09:26Z",
        ),
        (
            "substitute_attempt08_irmi_xiaomi_ar2025_en",
            args.attempt08,
            "2026-09-25T20:37:56Z",
        ),
    ]:
        out["inputs"].append(
            {
                "role": role,
                "path": p,
                "bytes": os.path.getsize(p),
                "sha256": sha256_file(p),
                "access": "read_only_reuse_of_OPEN5-PEND5A-HK-ACQUISITION/a20260924-01/corpus",
                "retrieved_utc": rutc,
                "retrieval_method_per_prior_station": "direct_from_origin_site_www1.hkexnews.hk"
                if "attempt04" in role
                else "direct_from_issuer_site_ir.mi.com",
                "external_retrieval_not_local": False,
                "substitute_not_origin": True,
            }
        )

    if origin_sha != args.expect_origin_sha:
        out["fatal"] = f"origin sha mismatch {origin_sha}"
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("FATAL origin sha mismatch", flush=True)
        return 2

    # ---------------- B1: origin text layer ----------------
    t0 = time.time()
    b1: dict = {"external_retrieval_not_local": False, "note": "contrast only; never counts as readable"}
    import fitz  # noqa: PLC0415

    doc = fitz.open(args.origin)
    b1["page_count"] = len(doc)
    full_parts = []
    sample_pages = {}
    for i in range(len(doc)):
        txt = doc[i].get_text()
        full_parts.append(f"<<<PAGE {i + 1}>>>\n")
        full_parts.append(txt)
        if i + 1 in pages:
            sample_pages[i + 1] = {
                "chars": len(txt),
                "sha256": hashlib.sha256(txt.encode("utf-8")).hexdigest(),
                "anchors": {a: (a in txt) for a in anchors},
                "excerpt": txt[:300],
            }
    doc.close()
    full = "".join(full_parts)
    ex = write_extract(os.path.join(args.extractdir, "origin_fitz_full.txt"), full)
    b1["fitz"] = {
        "engine": "PyMuPDF",
        "full_doc_chars": len(full),
        "full_doc_extract": ex,
        "anchors": anchor_summary(full, anchors),
        "sample_pages": sample_pages,
        "hit_pages_union": sorted(
            {p for a in anchors for p in anchor_summary(full, anchors)[a]["hit_pages"]}
        ),
    }
    b1["fitz"]["engine"] = "PyMuPDF"
    b1["seconds"] = round(time.time() - t0, 3)
    out["b1_origin_textlayer"] = b1

    # ---------------- B2: attempt04 via two independent libs ----------------
    t0 = time.time()
    res4: dict = {"substitute_not_origin": True, "anchors": anchors}
    fitz_txt = fitz_extract(args.attempt04)
    ex4f = write_extract(os.path.join(args.extractdir, "attempt04_fitz.extracted.txt"), fitz_txt)
    res4["fitz"] = {
        "engine": "PyMuPDF",
        "chars": len(fitz_txt),
        "extract": ex4f,
        "anchors": anchor_summary(fitz_txt, anchors),
        "hit_words": [a for a in anchors if fitz_txt.count(a) > 0],
    }
    pm_txt = pdfminer_extract(args.attempt04)
    ex4p = write_extract(os.path.join(args.extractdir, "attempt04_pdfminer.extracted.txt"), pm_txt)
    res4["pdfminer"] = {
        "engine": "pdfminer.six",
        "chars": len(pm_txt),
        "extract": ex4p,
        "anchors": anchor_summary(pm_txt, anchors),
        "hit_words": [a for a in anchors if pm_txt.count(a) > 0],
    }
    res4["both_libs_hit_words_agree"] = sorted(res4["fitz"]["hit_words"]) == sorted(
        res4["pdfminer"]["hit_words"]
    )
    res4["seconds"] = round(time.time() - t0, 3)
    out["b2_attempt04"] = res4

    # ---------------- B2': attempt08 EN ----------------
    t0 = time.time()
    res8: dict = {"substitute_not_origin": True}
    txt8 = fitz_extract(args.attempt08)
    ex8 = write_extract(os.path.join(args.extractdir, "attempt08_fitz.extracted.txt"), txt8)
    res8["fitz"] = {
        "engine": "PyMuPDF",
        "chars": len(txt8),
        "extract": ex8,
        "cn_anchors": anchor_summary(txt8, anchors),
        "cn_hit_words": [a for a in anchors if txt8.count(a) > 0],
        "en_anchors": anchor_summary(txt8, en_anchors),
        "en_hit_words": [a for a in en_anchors if txt8.count(a) > 0],
    }
    res8["seconds"] = round(time.time() - t0, 3)
    out["b2prime_attempt08"] = res8

    out["finished_utc"] = utc_now()
    out["rc"] = 0
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", mode=0o777, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.out, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", args.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
