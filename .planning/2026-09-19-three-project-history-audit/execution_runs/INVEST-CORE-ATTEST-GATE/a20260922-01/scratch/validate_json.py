"""Validate this attempt's hand-written JSON deliverables as strict UTF-8 JSON.

Exit 0 = all parse. Prints the first invalid JSON escape if any fails.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FILES = ["handoff.json", "commands.json", "binding.json"]

failed = False
for name in FILES:
    path = BASE / name
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        print(f"JSON OK: {name} (top-level keys: {len(data)})")
    except Exception as exc:  # noqa: BLE001 - report everything
        failed = True
        print(f"JSON FAIL: {name} -> {exc}")
        src = open(path, encoding="utf-8").read()
        match = re.search(r'(?<!\\)\\(?![\\\"/bfnrtu])', src)
        if match:
            start = max(0, match.start() - 70)
            print("    invalid escape at", match.start(), ":", repr(src[start : match.start() + 50]))
sys.exit(1 if failed else 0)
