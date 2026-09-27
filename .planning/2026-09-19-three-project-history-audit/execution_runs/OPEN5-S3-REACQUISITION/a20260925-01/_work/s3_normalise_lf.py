"""OPEN5-S3-REACQUISITION · LF-normalise the 10 origin text-layer dumps.

The pdfium `get_text_range()` output embeds CR characters from the source PDF.
Written files must be UTF-8 (no BOM) + pure LF (discipline §6), so the dumps are
normalised here while the RAW string sha256 (computed by the probe itself) is
kept untouched as `text_layer_sha256` for byte-level reproducibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patha", required=True)
    args = ap.parse_args()

    with open(args.patha, "r", encoding="utf-8") as f:
        pa = json.load(f)

    changed = []
    for rec in pa["pages"]:
        p = rec["text_layer_file"]
        with open(p, "rb") as f:
            raw = f.read()
        txt = raw.decode("utf-8")
        norm = txt.replace("\r\n", "\n").replace("\r", "\n")
        if norm != txt:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(norm)
            rec["text_layer_file_sha256"] = sha256_file(p)
            rec["text_layer_file_lf_normalised"] = True
            rec["text_layer_file_raw_string_sha256_retained"] = True
            changed.append(os.path.basename(p))

    pa["text_layer_dump_lf_normalised"] = True
    pa["text_layer_dump_note"] = (
        "origin text-layer dumps are LF-normalised for the written-file discipline; "
        "text_layer_sha256 per page is the sha256 of the RAW extracted string "
        "(reproducible by re-running the probe)"
    )
    with open(args.patha, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pa, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with open(args.patha, "r", encoding="utf-8") as f:
        json.load(f)
    print(json.dumps({"normalised": changed, "count": len(changed)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
