"""OPEN5-S3-REACQUISITION · S4 input: dual-path comparison scaffold.

Records (1) Path A (OCR) vs Path B1 (origin text layer) on the SAME pages,
and (2) Path B2 fitz vs pdfminer on the substitute — i.e. "同页同段文本是否一致"
inputs + method, WITHOUT issuing the S4 verdict (S4 is a later station).

Output: path_compare.json (utf-8, LF, re-parsed after write).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import sys

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s: str) -> str:
    """Whitespace-insensitive normalisation (no language rewriting)."""
    return re.sub(r"\s+", "", s)


def split_pages(text: str) -> dict[int, str]:
    parts = re.split(r"<<<PAGE (\d+)>>>", text)
    out: dict[int, str] = {}
    for i in range(1, len(parts), 2):
        out[int(parts[i])] = parts[i + 1]
    return out


def cjk_runs(s: str) -> list[str]:
    return re.findall(r"[一-鿿]{4,}", s)


def cjk_count(s: str) -> int:
    return len(re.findall(r"[一-鿿]", s))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patha", required=True, help="pathA_probe.json")
    ap.add_argument("--extractdir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.patha, "r", encoding="utf-8") as f:
        pa = json.load(f)

    out: dict = {
        "attempt": "OPEN5-S3-REACQUISITION/a20260925-01",
        "generated_utc": utc_now(),
        "role": "s4_input_only_no_verdict",
        "method": {
            "A_vs_B1": (
                "Same sampled pages: normalise (whitespace-stripped) both the OCR "
                "reconstruction and the origin text layer; check (a) whether any full "
                "OCR line (>=8 CJK chars) occurs verbatim in the origin layer "
                "(expected: no — origin layer is GID-garbled), and (b) whether the "
                "readable cover fragment present in the origin layer also appears in "
                "the OCR text (expected: yes — readable-in-both cross-check)."
            ),
            "B2_fitz_vs_pdfminer": (
                "Same substitute file: for every anchor, take the first-hit line of "
                "library 1 (normalised) and search it in library 2's normalised "
                "text; also compare per-page anchor presence sets."
            ),
            "sha_of_inputs": "every input file's sha256 recorded below",
        },
        "a_vs_b1": [],
        "b2_fitz_vs_pdfminer": {},
        "summary": {},
    }

    # ------------- A (OCR) vs B1 (origin text layer), same pages -------------
    readable_cover_seen = 0
    line_verbatim_matches = 0
    line_checks = 0
    for rec in pa["pages"]:
        pno = rec["page"]
        ocr_txt = io.open(rec["ocr_text_file"], encoding="utf-8").read()
        tl_txt = io.open(rec["text_layer_file"], encoding="utf-8").read()
        n_ocr, n_tl = norm(ocr_txt), norm(tl_txt)
        ocr_lines = [ln for ln in ocr_txt.splitlines() if cjk_count(ln) >= 8]
        matched, checked = [], 0
        for ln in ocr_lines[:40]:
            checked += 1
            if norm(ln) in n_tl:
                matched.append(ln[:120])
        line_checks += checked
        line_verbatim_matches += len(matched)
        # readable-fragment cross check (origin layer readable spans)
        frag = None
        if pno == 1:
            m = re.search(r"股份代號[^\n]{0,60}", tl_txt)
            frag = m.group(0) if m else None
        frag_in_ocr = bool(frag) and (norm(frag) in n_ocr)
        if frag_in_ocr:
            readable_cover_seen += 1
        out["a_vs_b1"].append(
            {
                "page": pno,
                "ocr_file": rec["ocr_text_file"],
                "ocr_file_sha256": rec["ocr_text_file_sha256"],
                "ocr_reconstruction": True,
                "origin_textlayer_file": rec["text_layer_file"],
                "origin_textlayer_file_sha256": rec["text_layer_file_sha256"],
                "ocr_anchor_hits": sorted(k for k, v in rec["ocr_anchors"].items() if v),
                "origin_anchor_hits": sorted(
                    k for k, v in rec["text_layer_anchors"].items() if v
                ),
                "ocr_long_cjk_lines_checked": checked,
                "verbatim_lines_found_in_origin_layer": len(matched),
                "sample_matched_lines": matched[:3],
                "origin_readable_fragment": (frag or "")[:80],
                "fragment_present_in_ocr": frag_in_ocr,
            }
        )

    # ------------- B2: fitz vs pdfminer on the substitute -------------
    fitz_txt = io.open(
        os.path.join(args.extractdir, "attempt04_fitz.extracted.txt"), encoding="utf-8"
    ).read()
    pm_txt = io.open(
        os.path.join(args.extractdir, "attempt04_pdfminer.extracted.txt"), encoding="utf-8"
    ).read()
    fp, pp = split_pages(fitz_txt), split_pages(pm_txt)
    per_anchor = {}
    for a in ANCHORS:
        f_hit_pages = sorted(n for n, t in fp.items() if a in t)
        p_hit_pages = sorted(n for n, t in pp.items() if a in t)
        first_line = None
        m = re.search(rf"[^\n]*{re.escape(a)}[^\n]*", fitz_txt)
        if m:
            first_line = m.group(0)[:300]
        per_anchor[a] = {
            "fitz_hit_pages": f_hit_pages,
            "pdfminer_hit_pages": p_hit_pages,
            "page_set_intersection": sorted(set(f_hit_pages) & set(p_hit_pages)),
            "page_set_union": sorted(set(f_hit_pages) | set(p_hit_pages)),
            "first_line_fitz": first_line,
            "first_line_fitz_found_in_pdfminer": bool(first_line)
            and (norm(first_line) in norm(pm_txt)),
            "first_line_pdfminer": (
                (re.search(rf"[^\n]*{re.escape(a)}[^\n]*", pm_txt).group(0)[:300])
                if re.search(rf"[^\n]*{re.escape(a)}[^\n]*", pm_txt)
                else None
            ),
        }
    out["b2_fitz_vs_pdfminer"] = {
        "substitute": "attempt04_hkexnews_xiaomi_fy2025_results_zh.pdf",
        "substitute_not_origin": True,
        "fitz_sha256": sha256_file(os.path.join(args.extractdir, "attempt04_fitz.extracted.txt")),
        "pdfminer_sha256": sha256_file(
            os.path.join(args.extractdir, "attempt04_pdfminer.extracted.txt")
        ),
        "per_anchor": per_anchor,
    }

    out["summary"] = {
        "a_vs_b1_pages": len(out["a_vs_b1"]),
        "a_vs_b1_ocr_lines_checked": line_checks,
        "a_vs_b1_verbatim_matches_in_origin_layer": line_verbatim_matches,
        "readable_cover_fragment_reproduced_in_ocr": readable_cover_seen,
        "b2_anchors_with_both_libs_hit": sorted(
            a
            for a, v in per_anchor.items()
            if v["fitz_hit_pages"] and v["pdfminer_hit_pages"]
        ),
        "b2_first_line_cross_lib_match_count": sum(
            1 for v in per_anchor.values() if v["first_line_fitz_found_in_pdfminer"]
        ),
        "verdict_left_to": "S4 (dual-path review station) — this file only stages inputs",
    }

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
