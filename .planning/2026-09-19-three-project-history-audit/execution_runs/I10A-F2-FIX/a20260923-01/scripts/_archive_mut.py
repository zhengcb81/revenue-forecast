"""Archive the superseded (text-mode) mutation-arm record and explain why."""
from __future__ import annotations

import json
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
old = ATT / "evidence" / "mut_arm.json"
if old.exists():
    doc = json.loads(old.read_text(encoding="utf-8"))
    doc["superseded"] = (
        "r1 events were produced by the text-mode version of mutate_guard.py: the "
        "sha256 values were computed over the in-memory (LF) content while the "
        "on-disk file temporarily carried CRLF translation from Path.write_text(). "
        "The delivered file was normalized back to the byte-exact frozen fixed sha "
        "9eecf260bfb22f1a5b3114a956cdf633328d620e1957a58de6806ab0214dcca9 (15969 B) "
        "and the whole mutation arm was re-run with byte-exact read_bytes/write_bytes. "
        "Kept for honesty; evidence/mut_arm.json is the authoritative record."
    )
    doc["superseded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (ATT / "evidence" / "mut_arm_superseded_r1.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    old.unlink()
    print("archived")
else:
    print("nothing to archive")
