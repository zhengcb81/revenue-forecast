"""Locate verbatim quote lines in an extracted-text artifact.

Usage: python -B quote_locator.py <extract_txt> <line_numbers_comma> <out_json>

Emits for each line: {line, byte_start, byte_end, bytes, text}
(byte offsets are UTF-8 offsets inside the saved extract file, so quotes in
the acquisition report are reproducible byte-for-byte).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    path, lines_arg, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8")
    lines = text.split("\n")
    offsets = []
    running = 0
    for ln_text in lines:
        offsets.append(running)
        running += len(ln_text.encode("utf-8")) + 1  # +1 for the LF separator
    wanted = [int(x) for x in lines_arg.split(",") if x.strip()]
    out = []
    for ln in wanted:
        idx = ln - 1
        if 0 <= idx < len(lines):
            out.append({"line": ln, "byte_start": offsets[idx],
                        "byte_end": offsets[idx] + len(lines[idx].encode("utf-8")),
                        "bytes": len(lines[idx].encode("utf-8")), "text": lines[idx]})
    payload = {
        "located_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file": path,
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "file_bytes": len(raw),
        "quotes": out,
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"file": path, "quotes": len(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
