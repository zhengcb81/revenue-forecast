"""OPEN5-S3-REACQUISITION · Path A (OCR re-acquisition), DEC-8 / S3.

Fresh attempt: render sampled pages of the HK original (read-only) with
pypdfium2, OCR with rapidocr (engine reused read-only from PEND-5b venv),
then run the frozen anchor probe.

EVERY text field produced here is an `ocr_reconstruction` (image-to-text
rebuild) — NEVER origin text.

Usage:
  s3_pathA_ocr.py --pdf <path> --expect-sha <sha256> --pages 1,2,... \
                  --renders <dir> --textdir <dir> --out <out.json> \
                  --anchors 小米,收入,年度報告,分部,毛利 --dpi 200
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


def ocr_lines(engine, img_path: str):
    res = engine(img_path)
    txts = getattr(res, "txts", None)
    if txts is not None:
        return [str(t) for t in txts], getattr(res, "scores", None)
    out = []
    for item in res or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            v = item[1]
            out.append(str(v[0]) if isinstance(v, (list, tuple)) else str(v))
    return out, None


def anchor_hits_with_offsets(text: str, lines: list[str], anchors: list[str]) -> dict:
    """For each anchor: list of {line_no (1-based), byte_start, byte_end, line}."""
    result: dict[str, list] = {}
    # byte offset of each line start inside the joined reconstruction
    offsets, pos = [], 0
    for ln in lines:
        offsets.append(pos)
        pos += len(ln.encode("utf-8")) + 1  # +1 for the "\n" joiner
    for a in anchors:
        hits = []
        for i, ln in enumerate(lines):
            start = ln.find(a)
            if start >= 0:
                b0 = offsets[i] + len(ln[:start].encode("utf-8"))
                hits.append(
                    {
                        "line_no": i + 1,
                        "byte_start": b0,
                        "byte_end": b0 + len(a.encode("utf-8")),
                        "line": ln[:200],
                    }
                )
        result[a] = hits
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--expect-sha", required=True)
    ap.add_argument("--pages", required=True)
    ap.add_argument("--renders", required=True)
    ap.add_argument("--textdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--anchors", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--label", default="s3_pathA")
    args = ap.parse_args()

    pages = [int(x) for x in args.pages.split(",") if x.strip()]
    anchors = [a for a in args.anchors.split(",") if a]

    os.makedirs(args.renders, mode=0o777, exist_ok=True)
    os.makedirs(args.textdir, mode=0o777, exist_ok=True)

    pdf_sha = sha256_file(args.pdf)
    sha_ok = pdf_sha == args.expect_sha

    out = {
        "label": args.label,
        "path": "A_ocr_reconstruction",
        "attempt": "OPEN5-S3-REACQUISITION/a20260925-01",
        "pdf": args.pdf,
        "pdf_bytes": os.path.getsize(args.pdf),
        "pdf_sha256": pdf_sha,
        "pdf_sha_matches_expected": sha_ok,
        "dpi": args.dpi,
        "anchors": anchors,
        "started_utc": utc_now(),
        "ocr_reconstruction": True,
        "external_retrieval_not_local": False,
        "retrieval_method": "local_readonly_render_ocr_of_origin_bytes",
        "renderer": None,
        "ocr_engine": None,
        "page_count": None,
        "pages": [],
        "anchor_hit_pages": {},
        "text_layer_anchor_hit_pages": {},
        "totals": {},
        "rc": 1,
    }
    if not sha_ok:
        out["fatal"] = f"sha mismatch: {pdf_sha} != {args.expect_sha}"

    import pypdfium2 as pdfium  # noqa: PLC0415
    from importlib.metadata import version as _v  # noqa: PLC0415

    out["renderer"] = "pypdfium2 " + _v("pypdfium2")
    out["ocr_engine"] = "rapidocr " + _v("rapidocr") + " + onnxruntime " + _v("onnxruntime")

    if not sha_ok:
        # fail-closed: do not touch a file whose identity is not the frozen baseline
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("FATAL sha mismatch; no OCR performed", flush=True)
        return 2

    from rapidocr import RapidOCR  # noqa: PLC0415

    engine = RapidOCR()
    doc = pdfium.PdfDocument(args.pdf)
    out["page_count"] = len(doc)

    t_all = time.time()
    for pno in pages:
        rec = {"page": pno, "ocr_reconstruction": True}
        t0 = time.time()
        page = doc[pno - 1]
        # origin text layer on the same page (contrast only, never counted for A)
        try:
            tp = page.get_textpage()
            tl = tp.get_text_range() or ""
        except Exception as e:  # noqa: BLE001
            tl = ""
            rec["text_layer_error"] = f"{type(e).__name__}: {e}"
        rec["text_layer_chars"] = len(tl)
        rec["text_layer_sha256"] = hashlib.sha256(tl.encode("utf-8")).hexdigest()
        rec["text_layer_anchors"] = {a: (a in tl) for a in anchors}
        rec["text_layer_excerpt"] = tl[:300]
        tl_path = os.path.join(args.textdir, f"{args.label}_p{pno:04d}.origin_textlayer.txt")
        with open(tl_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(tl)
        rec["text_layer_file"] = tl_path
        rec["text_layer_file_sha256"] = sha256_file(tl_path)

        png = os.path.join(args.renders, f"{args.label}_p{pno:04d}.png")
        bitmap = page.render(scale=args.dpi / 72.0)
        img = bitmap.to_pil()
        img.save(png)
        rec["render_ms"] = int((time.time() - t0) * 1000)
        rec["png"] = png
        rec["png_bytes"] = os.path.getsize(png)
        rec["png_sha256"] = sha256_file(png)
        rec["img_size"] = [img.size[0], img.size[1]]

        t1 = time.time()
        try:
            lines, scores = ocr_lines(engine, png)
        except Exception as e:  # noqa: BLE001
            rec["ocr_error"] = f"{type(e).__name__}: {e}"
            lines, scores = [], None
        rec["ocr_ms"] = int((time.time() - t1) * 1000)
        text = "\n".join(lines)
        txt_path = os.path.join(args.textdir, f"{args.label}_p{pno:04d}.ocr.txt")
        with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        rec["ocr_text_file"] = txt_path
        rec["ocr_text_file_sha256"] = sha256_file(txt_path)
        rec["ocr_chars"] = len(text)
        rec["ocr_lines"] = len(lines)
        rec["ocr_anchors"] = {a: (a in text) for a in anchors}
        rec["ocr_anchor_hits"] = {
            a: h for a, h in anchor_hits_with_offsets(text, lines, anchors).items() if h
        }
        rec["ocr_excerpt"] = text[:600]
        if scores:
            try:
                rec["ocr_score_mean"] = round(sum(float(s) for s in scores) / len(scores), 4)
            except Exception:  # noqa: BLE001
                pass
        out["pages"].append(rec)
        print(
            f"[{args.label}] p{pno}: render={rec['render_ms']}ms ocr={rec.get('ocr_ms')}ms "
            f"chars={rec['ocr_chars']} hits={sorted(k for k, v in rec['ocr_anchors'].items() if v)} "
            f"origin_tl_hits={sorted(k for k, v in rec['text_layer_anchors'].items() if v)}",
            flush=True,
        )

    doc.close()
    out["finished_utc"] = utc_now()
    out["totals"]["wall_ms"] = int((time.time() - t_all) * 1000)
    out["totals"]["pages"] = len(pages)
    out["totals"]["ocr_chars"] = sum(p.get("ocr_chars", 0) for p in out["pages"])
    out["totals"]["ocr_errors"] = sum(1 for p in out["pages"] if p.get("ocr_error"))
    for a in anchors:
        out["anchor_hit_pages"][a] = [p["page"] for p in out["pages"] if p["ocr_anchors"].get(a)]
        out["text_layer_anchor_hit_pages"][a] = [
            p["page"] for p in out["pages"] if p.get("text_layer_anchors", {}).get(a)
        ]
    out["anchor_words_hit"] = sorted(a for a in anchors if out["anchor_hit_pages"][a])
    out["anchor_words_hit_count"] = len(out["anchor_words_hit"])
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
