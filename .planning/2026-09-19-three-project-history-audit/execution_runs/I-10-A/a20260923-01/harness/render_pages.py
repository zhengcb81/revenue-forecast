#!/usr/bin/env python
"""I-10-A harness: render selected PDF pages to PNG for verbatim visual reading.

The Xiaomi source's embedded subset fonts carry no ToUnicode CMap (proven by both
PyMuPDF's glyph-id guessing and pdfminer's raw `(cid:NNNN)` output), so its text
layer cannot yield verbatim quotes. Pages are instead rendered deterministically
from the untouched raw bytes (PyMuPDF, vendored) so a human/independent reviewer
can transcribe and verify 原文 with native page numbers. Each PNG gets a sidecar
hash record; the raw's hash is re-verified around rendering.

Writes only the PNGs + manifest under --out-dir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "iso" / "vendor"))

import pymupdf  # noqa: E402


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--pages", required=True, help="comma-separated 1-based page numbers")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--zoom", type=float, default=2.0)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    before = sha256_of(pdf)
    doc = pymupdf.open(pdf)
    records = []
    for num in [int(x) for x in args.pages.split(",") if x.strip()]:
        page = doc[num - 1]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom))
        name = f"{args.tag}_p{num:03d}.png"
        target = out / name
        pix.save(target)
        records.append(
            {
                "pdf_page": num,
                "png": name,
                "png_sha256": sha256_of(target),
                "png_bytes": target.stat().st_size,
                "width": pix.width,
                "height": pix.height,
                "zoom": args.zoom,
            }
        )
    doc.close()
    after = sha256_of(pdf)
    manifest = {
        "pdf": str(pdf),
        "pdf_sha256_before": before,
        "pdf_sha256_after": after,
        "pdf_unchanged_by_rendering": before == after,
        "renderer": f"pymupdf {pymupdf.__version__} (vendored iso/vendor)",
        "render_purpose": "verbatim visual transcription source for disclosure_mapping quotes (text layer unusable: no ToUnicode CMap)",
        "pages": records,
    }
    (out / f"{args.tag}_render_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({"rendered": [r["pdf_page"] for r in records], "raw_unchanged": before == after}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
