"""Count ENGLISH anchor words inside an already-extracted text file (independent path check).

Usage: python -B en_text_count.py <text_file> <out_json>
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys

ANCHORS = ["Xiaomi", "Revenue", "Annual Report", "Segment", "Gross profit"]


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    path, out_json = sys.argv[1], sys.argv[2]
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8", "replace")
    anchors = {}
    for w in ANCHORS:
        n = text.count(w)
        entry = {"count": n, "first_line": None, "first_byte_offset": None, "context": None}
        if n:
            idx = text.find(w)
            entry["first_line"] = text[:idx].count("\n") + 1
            entry["first_byte_offset"] = len(text[:idx].encode("utf-8"))
            ls = text.rfind("\n", 0, idx) + 1
            le = text.find("\n", idx)
            entry["context"] = text[ls:le if le != -1 else len(text)][:200]
        anchors[w] = entry
    zh = {w: {"count": text.count(w)} for w in ["小米", "收入", "年度報告", "分部", "毛利"]}
    result = {
        "probe_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file": path,
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "file_bytes": len(raw),
        "total_chars": len(text),
        "en_anchors": anchors,
        "en_hit_count": sum(1 for w in ANCHORS if anchors[w]["count"] > 0),
        "zh_anchors": zh,
        "zh_hit_count": sum(1 for w in zh if zh[w]["count"] > 0),
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"en_hits": result["en_hit_count"],
                      "en_counts": {w: anchors[w]["count"] for w in ANCHORS},
                      "zh_hits": result["zh_hit_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
