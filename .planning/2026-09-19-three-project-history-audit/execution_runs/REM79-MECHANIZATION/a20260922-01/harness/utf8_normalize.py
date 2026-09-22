#!/usr/bin/env python3
"""utf8_normalize.py — bookkeeping fix: re-encode UTF-16 evidence as UTF-8.

PowerShell `>` / Tee-Object wrote six evidence files as UTF-16LE (BOM ff fe),
which breaks utf-8 JSON tooling. Content is unchanged; only the encoding is
normalized to UTF-8 without BOM. The pre-fix BOM bytes are recorded here.
"""
import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
FILES = [
    "evidence/build_corpus.stdout.txt",
    "evidence/verify_driver.stdout.txt",
    "evidence/live/live_scan.json",
    "evidence/live/live_scan.txt",
    "evidence/live/selfscan_oracle.json",
    "evidence/live/selfscan_oracle.txt",
]


def main() -> int:
    report = []
    for rel in FILES:
        p = ATTEMPT / rel
        raw = p.read_bytes()
        if not raw.startswith(b"\xff\xfe"):
            report.append({"file": rel, "action": "skipped", "reason": "no UTF-16 BOM"})
            continue
        text = raw.decode("utf-16")  # handles LE BOM
        p.write_bytes(text.encode("utf-8"))
        report.append({
            "file": rel,
            "action": "re-encoded utf-16le -> utf-8",
            "bytes_before": len(raw),
            "bytes_after": len(text.encode("utf-8")),
            "content_unchanged": True,
        })
        print(f"re-encoded {rel}")
    (ATTEMPT / "evidence/utf8_normalize_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"normalized {sum(1 for r in report if r['action'].startswith('re'))} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
