"""Byte-lock / content-pin pre-check for the three REST-B target files.

Scans the test surface (tests/, tools/) for:
  1. full or 8-char-prefix sha256 literals of the three files' current bytes
  2. any read of the three file NAMES (source-text reads, byte reads, hashes)
  3. any sha256/file-hashing call that targets scripts/ files at all
Reports every hit with file:line so the byte-lock verdict is auditable.
Usage: python -B bytelock_scan.py
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TARGETS = {
    "scripts/model_registry.py": "62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081",
    "scripts/revenue_core.py": "8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883",
    "scripts/revenue_publication.py": "bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0",
}

# live re-measure (prove the pins above == production bytes right now)
print("== live production hashes ==")
for rel in TARGETS:
    data = (RF / rel).read_bytes()
    print(f"  {rel:35s} {hashlib.sha256(data).hexdigest()}  {len(data)} B")

print("\n== 1. sha literals of these files anywhere in tests/ + tools/ ==")
hits = 0
for root in ("tests", "tools"):
    for p in sorted((RF / root).rglob("*")):
        if not p.is_file() or p.suffix not in {".py", ".json", ".yaml", ".yml", ".md", ".txt", ".cfg", ".ini"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        low = text.lower()
        for rel, sha in TARGETS.items():
            for needle in (sha, sha[:8], sha[:12]):
                if needle.lower() in low:
                    hits += 1
                    ln = low.splitlines().index(low.splitlines().__iter__().__next__()) if False else None
                    for i, line in enumerate(low.splitlines(), 1):
                        if needle.lower() in line:
                            print(f"  HIT {p.relative_to(RF)}:{i}  file={rel}  needle={needle[:12]}")
print(f"  total sha-literal hits = {hits}")

print("\n== 2. reads/references of the three file NAMES in tests/ + tools/ ==")
name_re = re.compile(r"model_registry\.py|revenue_core\.py|revenue_publication\.py")
refs = 0
for root in ("tests", "tools"):
    for p in sorted((RF / root).rglob("*.py")):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            if name_re.search(line):
                refs += 1
                print(f"  {p.relative_to(RF)}:{i}: {line.strip()[:160]}")
print(f"  total name references = {refs}")

print("\n== 3. sha256-of-file calls in tests/ + tools/ (context lines) ==")
sha_re = re.compile(r"sha256\(|file_digest|blake2|md5\(")
ctx = 0
for root in ("tests", "tools"):
    for p in sorted((RF / root).rglob("*.py")):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(lines, 1):
            if sha_re.search(line):
                ctx += 1
                print(f"  {p.relative_to(RF)}:{i}: {line.strip()[:160]}")
print(f"  total hashing-call lines = {ctx}")
