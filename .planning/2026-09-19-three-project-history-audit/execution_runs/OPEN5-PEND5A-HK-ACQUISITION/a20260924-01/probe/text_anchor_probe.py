"""Readability probe for TEXT/HTML artifacts (non-PDF): count HK anchor words.

Usage: python -B text_anchor_probe.py <text_file> <out_json>

Output JSON: {file, sha256, bytes, decoded_chars, replacement_chars,
  anchors: {word: {count, first_line, first_char_offset, first_byte_offset, context}},
  anchors_hit_count, anchors_total_occurrences}
Line numbers and byte offsets refer to the raw saved file bytes (UTF-8 assumed).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    path, out_json = sys.argv[1], sys.argv[2]
    with open(path, "rb") as fh:
        data = fh.read()
    text = data.decode("utf-8", "replace")
    anchors = {}
    for word in ANCHORS:
        count = text.count(word)
        entry = {"count": count, "first_line": None, "first_char_offset": None,
                 "first_byte_offset": None, "context": None}
        if count:
            idx = text.find(word)
            entry["first_line"] = text[:idx].count("\n") + 1
            entry["first_char_offset"] = idx
            entry["first_byte_offset"] = len(text[:idx].encode("utf-8"))
            line_start = text.rfind("\n", 0, idx) + 1
            line_end = text.find("\n", idx)
            if line_end == -1:
                line_end = len(text)
            entry["context"] = text[line_start:line_end][:200]
        anchors[word] = entry
    result = {
        "probe_utc": utc_now(),
        "file": path,
        "file_sha256": hashlib.sha256(data).hexdigest(),
        "file_bytes": len(data),
        "decoded_chars": len(text),
        "replacement_chars": text.count("�"),
        "anchors": anchors,
        "anchors_hit_count": sum(1 for w in ANCHORS if anchors[w]["count"] > 0),
        "anchors_total_occurrences": sum(anchors[w]["count"] for w in ANCHORS),
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"hits": result["anchors_hit_count"],
                      "counts": {w: anchors[w]["count"] for w in ANCHORS},
                      "file": path}, ensure_ascii=False))
    return 0 if result["anchors_hit_count"] >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
