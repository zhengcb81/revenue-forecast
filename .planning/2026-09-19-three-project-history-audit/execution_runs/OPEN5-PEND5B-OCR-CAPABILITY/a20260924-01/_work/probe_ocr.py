"""OPEN5-PEND5B-OCR-CAPABILITY probe: render PDF pages -> PNG -> OCR -> anchors.

Usage:
  probe_ocr.py --pdf <path> --pages 1,40,53 --outdir <dir> --out <out.json>
               --anchors 小米,收入 --dpi 200 --label <tag> [--text-layer]

Every OCR text field produced here is an `ocr_reconstruction` (image-to-text
rebuild), NEVER origin text. The `--text-layer` flag additionally records what
the PDF text layer itself yields for the same pages (for contrast only).
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


def make_engine():
    from rapidocr import RapidOCR  # noqa: PLC0415

    return RapidOCR()


def ocr_texts(engine, img_path: str):
    """Return list of recognized text lines, adapting to rapidocr API shape."""
    res = engine(img_path)
    txts = getattr(res, "txts", None)
    if txts is not None:
        return [str(t) for t in txts], getattr(res, "scores", None)
    # raw sequence fallback: items like [box, (text, score)] or [box, text, score]
    out = []
    for item in res or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            v = item[1]
            if isinstance(v, (list, tuple)):
                out.append(str(v[0]))
            else:
                out.append(str(v))
    return out, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--pages", required=True, help="comma-separated 1-based pages")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--anchors", required=True, help="comma-separated anchors")
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--label", default="probe")
    ap.add_argument("--text-layer", action="store_true")
    args = ap.parse_args()

    pages = [int(x) for x in args.pages.split(",") if x.strip()]
    anchors = [a for a in args.anchors.split(",") if a]

    # explicit short-ish dirs, created with normal modes (never mkdtemp)
    os.makedirs(args.outdir, mode=0o777, exist_ok=True)

    out = {
        "label": args.label,
        "pdf": args.pdf,
        "pdf_bytes": os.path.getsize(args.pdf),
        "pdf_sha256": sha256_file(args.pdf),
        "dpi": args.dpi,
        "anchors": anchors,
        "started_utc": utc_now(),
        "ocr_reconstruction": True,
        "renderer": None,
        "ocr_engine": None,
        "pages": [],
        "anchor_hit_pages": {},
        "text_layer_anchor_hit_pages": {},
        "totals": {},
    }

    import pypdfium2 as pdfium  # noqa: PLC0415

    from importlib.metadata import version as _dist_version  # noqa: PLC0415

    out["renderer"] = "pypdfium2 " + _dist_version("pypdfium2")
    out["ocr_engine"] = "rapidocr " + _dist_version("rapidocr") + " + onnxruntime " + _dist_version(
        "onnxruntime"
    )

    engine = make_engine()
    doc = pdfium.PdfDocument(args.pdf)
    out["page_count"] = len(doc)

    t_all0 = time.time()
    for pno in pages:
        rec = {"page": pno}
        t0 = time.time()
        page = doc[pno - 1]
        if args.text_layer:
            try:
                tp = page.get_textpage()
                tl = tp.get_text_range() or ""
            except Exception as e:  # noqa: BLE001
                tl = ""
                rec["text_layer_error"] = f"{type(e).__name__}: {e}"
            rec["text_layer_chars"] = len(tl)
            rec["text_layer_sha256"] = hashlib.sha256(tl.encode("utf-8")).hexdigest()
            rec["text_layer_anchors"] = {a: (a in tl) for a in anchors}
            rec["text_layer_excerpt"] = tl[:400]
        png = os.path.join(args.outdir, f"{args.label}_p{pno:04d}.png")
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
            txts, scores = ocr_texts(engine, png)
        except Exception as e:  # noqa: BLE001
            rec["ocr_error"] = f"{type(e).__name__}: {e}"
            txts, scores = [], None
        rec["ocr_ms"] = int((time.time() - t1) * 1000)
        text = "\n".join(txts)
        rec["ocr_reconstruction"] = True
        rec["ocr_chars"] = len(text)
        rec["ocr_lines"] = len(txts)
        rec["ocr_anchors"] = {a: (a in text) for a in anchors}
        # bounded excerpt (max 600 chars) for reporting; still ocr_reconstruction
        rec["ocr_excerpt"] = text[:600]
        if scores:
            try:
                rec["ocr_score_mean"] = round(sum(float(s) for s in scores) / len(scores), 4)
            except Exception:  # noqa: BLE001
                pass
        out["pages"].append(rec)
        print(
            f"[{args.label}] page {pno}: render={rec['render_ms']}ms "
            f"ocr={rec.get('ocr_ms')}ms chars={rec['ocr_chars']} "
            f"anchors={ {k: v for k, v in rec['ocr_anchors'].items() if v} }",
            flush=True,
        )

    doc.close()
    out["finished_utc"] = utc_now()
    out["totals"]["wall_ms"] = int((time.time() - t_all0) * 1000)
    out["totals"]["pages"] = len(pages)
    out["totals"]["ocr_chars"] = sum(p.get("ocr_chars", 0) for p in out["pages"])
    for a in anchors:
        out["anchor_hit_pages"][a] = [p["page"] for p in out["pages"] if p["ocr_anchors"].get(a)]
        if args.text_layer:
            out["text_layer_anchor_hit_pages"][a] = [
                p["page"] for p in out["pages"] if p.get("text_layer_anchors", {}).get(a)
            ]

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", mode=0o777, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # re-parse check
    with open(args.out, "r", encoding="utf-8") as f:
        json.load(f)
    print("wrote", args.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
