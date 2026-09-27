"""Readability probe P1: run tools/pdf_text.py (pure stdlib) over a saved PDF
and count HK anchor words in the extracted body text.

Usage:
    python -B anchor_probe.py <pdf> <pdf_text_tool.py> <out_json> [max_pages]

Outputs JSON:
    {pdf, sha256, bytes, tool, argv, rc, stdout_tail, classic_pages,
     pages_probed, extract_txt, extract_bytes, extract_sha256,
     total_chars, anchors: {word: {count, first_line, first_char_offset,
     first_byte_offset, context}}}
The full extracted text is written next to <out_json> as <out_json>.extracted.txt
(LF, UTF-8, no BOM) so line numbers / byte ranges in the report are reproducible.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    pdf, tool, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
    max_pages = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    with open(pdf, "rb") as fh:
        data = fh.read()
    pdf_sha = hashlib.sha256(data).hexdigest()

    # page count via the tool's own module (read-only import, -B => no pycache)
    import importlib.util

    spec = importlib.util.spec_from_file_location("pdf_text_tool", tool)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    page_nums = mod.classic_page_numbers(mod.Pdf(data))
    total = len(page_nums)
    n = total if (max_pages <= 0 or max_pages > total) else max_pages
    pages_arg = ",".join(str(i) for i in range(1, n + 1))

    tmp_json = out_json + ".pages.json"
    argv = [sys.executable, "-B", "-X", "utf8", tool, pdf, pages_arg, tmp_json]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
    rc = proc.returncode

    extract_path = os.path.splitext(out_json)[0] + ".extracted.txt"
    pages_text = []
    if os.path.exists(tmp_json):
        with open(tmp_json, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        pages_text = payload.get("pages", [])

    # canonical extracted text: one block per page, page marker lines included
    blocks = []
    for p in pages_text:
        blocks.append("=== PDF_PAGE %d (obj %d) ===\n%s" % (p.get("pdf_page", -1), p.get("page_object", -1), p.get("text", "")))
    full = "\n".join(blocks)
    with open(extract_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(full)
        if full and not full.endswith("\n"):
            fh.write("\n")
    with open(extract_path, "rb") as fh:
        extract_bytes = fh.read()

    lines = full.split("\n")
    anchors = {}
    for word in ANCHORS:
        count = full.count(word)
        entry = {"count": count, "first_line": None, "first_char_offset": None,
                 "first_byte_offset": None, "context": None}
        if count:
            idx = full.find(word)
            line_no = full[:idx].count("\n") + 1
            line_start = full.rfind("\n", 0, idx) + 1
            line_end = full.find("\n", idx)
            if line_end == -1:
                line_end = len(full)
            entry["first_line"] = line_no
            entry["first_char_offset"] = idx
            entry["first_byte_offset"] = len(full[:idx].encode("utf-8"))
            entry["context"] = full[line_start:line_end][:160]
        anchors[word] = entry

    result = {
        "probe_utc": utc_now(),
        "pdf": pdf,
        "pdf_sha256": pdf_sha,
        "pdf_bytes": len(data),
        "tool": tool,
        "argv": argv,
        "rc": rc,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
        "classic_pages": total,
        "pages_probed": n,
        "extract_txt": extract_path,
        "extract_bytes": len(extract_bytes),
        "extract_sha256": hashlib.sha256(extract_bytes).hexdigest(),
        "extract_line_count": len(lines),
        "total_chars": len(full),
        "anchors": anchors,
        "anchors_hit_count": sum(1 for w in ANCHORS if anchors[w]["count"] > 0),
        "anchors_total_occurrences": sum(anchors[w]["count"] for w in ANCHORS),
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    try:
        os.remove(tmp_json)
    except OSError:
        pass
    print(json.dumps({"rc": rc, "pages_probed": n, "classic_pages": total,
                      "anchors": {w: anchors[w]["count"] for w in ANCHORS},
                      "hit_words": result["anchors_hit_count"],
                      "extract": extract_path}, ensure_ascii=False))
    return 0 if result["anchors_hit_count"] >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
