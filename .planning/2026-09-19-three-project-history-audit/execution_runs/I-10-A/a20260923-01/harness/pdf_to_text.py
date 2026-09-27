#!/usr/bin/env python
"""I-10-A harness: PDF -> text with native page markers (CJK-capable).

Replaces the poppler/pdftotext attempt whose build lacks the Adobe-GB1/Adobe-CNS1
character collections (it extracted 0 CJK characters from both Chinese PDFs —
evidence kept under command_runs/CMD-I10A-EXTRACT-{CN,HK}/ and in run_log.jsonl).

Uses vendored PyMuPDF (iso/vendor, copied read-only from the machine's Miniconda
site-packages WITHOUT running the forbidden global interpreter; see decision.md).
Output format: a marker line `<<<PAGE n>>>` (1-based PDF page number) followed by
that page's text lines. Quotes in disclosure_mapping.json cite these page numbers.
A sidecar `<out>.manifest.json` records input/output hashes so every quote is
byte-verifiable against the untouched raw.
"""
from __future__ import annotations

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
    if len(sys.argv) != 3:
        print("usage: pdf_to_text.py <in.pdf> <out.txt>", file=sys.stderr)
        return 1
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    src_hash_before = sha256_of(src)
    doc = pymupdf.open(src)
    chunks = []
    for index, page in enumerate(doc, start=1):
        chunks.append(f"<<<PAGE {index}>>>")
        text = page.get_text("text")
        chunks.append(text.rstrip("\n"))
    doc.close()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(chunks) + "\n", encoding="utf-8", newline="\n")
    src_hash_after = sha256_of(src)
    manifest = {
        "input": str(src),
        "input_sha256_before": src_hash_before,
        "input_sha256_after": src_hash_after,
        "input_unchanged_by_extraction": src_hash_before == src_hash_after,
        "input_bytes": src.stat().st_size,
        "output": str(dst),
        "output_sha256": sha256_of(dst),
        "output_bytes": dst.stat().st_size,
        "pages": len(chunks) // 2,
        "tool": f"pymupdf {pymupdf.__version__} (vendored at iso/vendor, read-only copy; global interpreter not used)",
    }
    sidecar = Path(str(dst) + ".manifest.json")
    sidecar.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("pages", "output_sha256", "input_unchanged_by_extraction")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
