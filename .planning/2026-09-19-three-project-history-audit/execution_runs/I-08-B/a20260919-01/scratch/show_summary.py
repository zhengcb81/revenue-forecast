"""Print the bound-command return-code table (raw vs expected)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

attempt = Path(sys.argv[1])
data = json.loads((attempt / "after" / "c12_command_summary.json").read_text(encoding="ascii"))
width = max(len(row["id"]) for row in data)
for row in data:
    print(
        f"{row['id']:<{width}}  raw={row['raw_returncode']:>2}  "
        f"expected={row['expected_returncode']:>2}  {row['verdict']}  {row['evidence']}"
    )
mismatches = [row for row in data if row["verdict"] != "match"]
print()
print(f"commands: {len(data)}  mismatches: {len(mismatches)}")
for row in mismatches:
    print("  !", row["id"], row["raw_returncode"], row["expected_returncode"])
