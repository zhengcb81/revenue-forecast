#!/usr/bin/env python
"""I-10-A harness: decode the Xiaomi report's Identity-H glyph stream.

The source PDF's body fonts are TrueType subsets (Type0/Identity-H) whose text
shows as glyph ids; no ToUnicode CMap exists (pdfminer emits raw (cid:NNNN),
PyMuPDF's normal extraction guesses wrong BMP codepoints — both measured and
recorded in decision.md). The embedded subset fonts retain their own `cmap`
(unicode -> glyph) tables, so the inverse (glyph -> unicode) is a self-contained,
byte-verifiable decoder — no network, no external tables, no OCR.

Method: page.get_texttrace() yields per-char glyph ids + the owning font xref;
each glyph is mapped back to Unicode through that font's inverted sfnt `cmap`.
Glyphs missing from a cmap are emitted as <<GID:N>> and counted honestly.

Output: page-marked text (<<<PAGE n>>> convention) + a manifest with font xrefs,
cmap sizes, unmapped counts and hashes. Reads the PDF read-only (hash-verified).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
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


def parse_cmap_table(font_bytes: bytes) -> dict[int, str]:
    """Parse the sfnt `cmap` table into {glyph_id: unicode_char} (inverse of the
    best unicode->glyph subtable; first-seen unicode wins for shared glyphs)."""
    num_tables = struct.unpack(">H", font_bytes[4:6])[0]
    cmap_off = cmap_len = None
    for i in range(num_tables):
        rec = font_bytes[12 + 16 * i: 28 + 16 * i]
        tag, _, off, length = struct.unpack(">4sIII", rec)
        if tag == b"cmap":
            cmap_off, cmap_len = off, length
            break
    if cmap_off is None:
        return {}
    data = font_bytes[cmap_off: cmap_off + cmap_len]
    n_sub = struct.unpack(">H", data[2:4])[0]
    subs = []
    for i in range(n_sub):
        plat, enc, off = struct.unpack(">HHI", data[4 + 8 * i: 12 + 8 * i])
        subs.append((plat, enc, off))

    def prio(item):
        plat, enc, _ = item
        return (
            0 if (plat, enc) == (3, 10) else
            1 if (plat, enc) == (3, 1) else
            2 if plat == 0 else 3
        )

    for _, _, off in sorted(subs, key=prio):
        glyph_to_uni: dict[int, str] = {}
        fmt = struct.unpack(">H", data[off: off + 2])[0]
        if fmt == 4:
            segX2 = struct.unpack(">H", data[off + 6: off + 8])[0]
            seg = segX2 // 2
            end_off = off + 14
            start_off = end_off + segX2 + 2
            delta_off = start_off + segX2
            range_off = delta_off + segX2
            for s in range(seg):
                end = struct.unpack(">H", data[end_off + 2 * s: end_off + 2 * s + 2])[0]
                start = struct.unpack(">H", data[start_off + 2 * s: start_off + 2 * s + 2])[0]
                delta = struct.unpack(">h", data[delta_off + 2 * s: delta_off + 2 * s + 2])[0]
                ro = struct.unpack(">H", data[range_off + 2 * s: range_off + 2 * s + 2])[0]
                if start == 0xFFFF:
                    continue
                for cp in range(start, min(end, 0xFFFE) + 1):
                    if ro == 0:
                        gid = (cp + delta) & 0xFFFF
                    else:
                        gi = range_off + 2 * s + ro + 2 * (cp - start)
                        gid = struct.unpack(">H", data[gi: gi + 2])[0]
                        if gid:
                            gid = (gid + delta) & 0xFFFF
                    if gid and gid not in glyph_to_uni:
                        glyph_to_uni[gid] = chr(cp)
        elif fmt == 12:
            n_groups = struct.unpack(">I", data[off + 12: off + 16])[0]
            for g in range(n_groups):
                s, e, gi = struct.unpack(">III", data[off + 16 + 12 * g: off + 28 + 12 * g])
                for k, cp in enumerate(range(s, e + 1)):
                    gid = gi + k
                    if gid and gid not in glyph_to_uni:
                        glyph_to_uni[gid] = chr(cp)
        elif fmt == 6:
            first, count = struct.unpack(">HH", data[off + 6: off + 10])
            for k in range(count):
                gid = struct.unpack(">H", data[off + 10 + 2 * k: off + 12 + 2 * k])[0]
                if gid and gid not in glyph_to_uni:
                    glyph_to_uni[gid] = chr(first + k)
        if glyph_to_uni:
            return glyph_to_uni
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", default="all")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    out = Path(args.out)
    raw_hash_before = sha256_of(pdf)
    doc = pymupdf.open(pdf)
    page_nums = (
        list(range(1, doc.page_count + 1))
        if args.pages == "all"
        else [int(x) for x in args.pages.split(",") if x.strip()]
    )

    glyph_maps: dict[int, dict[int, str]] = {}
    font_meta: dict[int, dict] = {}
    master_map: dict[int, str] = {}
    master_xref = 0

    def ensure_font(xref: int) -> None:
        nonlocal master_map, master_xref
        if xref in glyph_maps:
            return
        try:
            name, ext, ftype, buf = doc.extract_font(xref)
            gmap = parse_cmap_table(buf) if buf else {}
        except Exception as exc:  # honest fallback
            name, ext, ftype, gmap = f"err:{exc}", "", "", {}
        glyph_maps[xref] = gmap
        font_meta[xref] = {
            "name": name,
            "ext": ext,
            "type": ftype,
            "cmap_glyphs": len(gmap),
        }
        if len(gmap) > len(master_map):
            master_map, master_xref = gmap, xref

    # pre-scan: find the richest embedded cmap (HYQiHei-FES keeps the family's
    # full glyph table while the other subsets were stripped); glyph ids are
    # shared across the family subsets (verified against the cover page's clean
    # text: 股=20579, 份=7871, 幣=11813, 港=15857 …). FES lives on the cover
    # pages, so scan the opening pages first regardless of --pages selection.
    scan_order = list(range(1, min(8, doc.page_count) + 1)) + page_nums
    for pno in scan_order:
        for f in doc[pno - 1].get_fonts(full=True):
            ensure_font(f[0])
        if len(master_map) > 20000:
            break

    chunks: list[str] = []
    unmapped_total = 0
    mapped_total = 0
    for pno in page_nums:
        page = doc[pno - 1]
        chunks.append(f"<<<PAGE {pno}>>>")
        name_to_xref: dict[str, int] = {}
        for f in page.get_fonts(full=True):
            xref, name = f[0], f[3]
            base = name.split("+")[-1]
            name_to_xref[base] = xref
            name_to_xref[name] = xref
        for item in page.get_texttrace():
            if item.get("type") not in (0, "text"):
                continue
            fname = item.get("font", "")
            xref = name_to_xref.get(fname, 0)
            if xref:
                ensure_font(xref)
            line_parts: list[str] = []
            is_cjk_family = "HYQiHei" in fname or "QiHei" in fname
            for ch in item.get("chars", []):
                gid = int(ch[1])  # texttrace char tuple = (unicode_guess, glyph_id, origin, bbox)
                guess = ch[0]
                uni = None
                if is_cjk_family:
                    gmap = glyph_maps.get(xref, {}) or master_map
                    uni = gmap.get(gid) or master_map.get(gid)
                if uni is None and isinstance(guess, int) and 0x20 <= guess < 0x2030:
                    # latin/numeral fonts (DIN): the first element is the true unicode
                    uni = chr(guess)
                if uni is None:
                    uni = master_map.get(gid)
                if uni is None:
                    line_parts.append(f"<<GID:{gid}>>")
                    unmapped_total += 1
                else:
                    line_parts.append(uni)
                    mapped_total += 1
            text = "".join(line_parts).strip()
            if text:
                chunks.append(text)
    doc.close()

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(chunks) + "\n", encoding="utf-8", newline="\n")
    raw_hash_after = sha256_of(pdf)
    manifest = {
        "pdf": str(pdf),
        "pdf_sha256_before": raw_hash_before,
        "pdf_sha256_after": raw_hash_after,
        "pdf_unchanged": raw_hash_before == raw_hash_after,
        "method": "inverse of each embedded subset font's own sfnt cmap (font bytes extracted from the untouched PDF); glyph ids via pymupdf get_texttrace",
        "fonts": {str(k): v for k, v in font_meta.items()},
        "mapped_glyphs": mapped_total,
        "unmapped_glyphs": unmapped_total,
        "out_sha256": sha256_of(out),
    }
    Path(str(out) + ".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({"mapped": mapped_total, "unmapped": unmapped_total, "fonts": len(font_meta)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
