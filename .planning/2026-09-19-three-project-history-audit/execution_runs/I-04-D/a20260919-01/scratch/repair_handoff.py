"""Repair handoff.json: the appended markdown must live INSIDE the JSON object.

The r2 correction block was appended after the closing brace, which makes the file
unparseable.  The block is moved verbatim into a new key (nothing is deleted), the
file is re-read with json.load, and the pointer/hash of the block are recorded.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

A = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = A / "handoff.json"
RECOVERY = A / "recovery" / "r2_corrections.md"
REVALIDATION = A / "after" / "handoff_json_revalidation.txt"

original_bytes = HANDOFF.read_bytes()
original_sha = hashlib.sha256(original_bytes).hexdigest()
text = original_bytes.decode("utf-8")

marker = "\n## r2 更正（追加；不得改写上文既有字节）"
index = text.find(marker)
report: list[str] = [
    "handoff.json repair report",
    f"path                : {HANDOFF}",
    f"bytes before        : {len(original_bytes)}",
    f"sha256 before       : {original_sha}",
    f"marker offset        : {index}",
]
if index < 0:
    report.append("NO APPENDED MARKDOWN FOUND - nothing to move")
    REVALIDATION.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    raise SystemExit(0)

json_part = text[:index]
appendix = text[index:]
report.append(f"json part bytes      : {len(json_part.encode('utf-8'))}")
report.append(f"appendix bytes       : {len(appendix.encode('utf-8'))}")

# 1. remove the marker line itself from the appendix file's title
appendix_body = appendix.lstrip("\n")
RECOVERY.write_text(appendix_body, encoding="utf-8")
appendix_sha = hashlib.sha256(RECOVERY.read_bytes()).hexdigest()
report.append(f"appendix -> {RECOVERY.relative_to(A).as_posix()}")
report.append(f"appendix sha256      : {appendix_sha}")

# 2. re-parse the JSON part and add the pointer keys
payload = json.loads(json_part)
payload["r2_corrections_pointer"] = "recovery/r2_corrections.md"
payload["r2_corrections_sha256"] = appendix_sha
payload["r2_corrections_note"] = (
    "r2 追加更正原文逐字保存在 pointer 指向的文件中；本键只做指针，正文未改一字。"
    " 原实现曾把该段 markdown 追加在 JSON 对象闭合之后，使本文件不可解析——已修复。"
)
payload["r2_handoff_repair"] = {
    "defect": "markdown was appended after the closing brace -> handoff.json was not valid JSON",
    "bytes_before": len(original_bytes),
    "sha256_before": original_sha,
    "bytes_moved_out": len(appendix.encode("utf-8")),
    "moved_to": "recovery/r2_corrections.md",
    "moved_sha256": appendix_sha,
    "content_preserved": "verbatim, nothing deleted",
}
HANDOFF.write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")

new_bytes = HANDOFF.read_bytes()
new_sha = hashlib.sha256(new_bytes).hexdigest()
report.append(f"bytes after         : {len(new_bytes)}")
report.append(f"sha256 after        : {new_sha}")

# 3. re-read and validate
reloaded = json.loads(HANDOFF.read_text(encoding="utf-8"))
report.append(f"json.load after     : OK, top-level keys = {len(reloaded)}")
report.append(f"pointer key present : {'r2_corrections_pointer' in reloaded}")
REVALIDATION.write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
