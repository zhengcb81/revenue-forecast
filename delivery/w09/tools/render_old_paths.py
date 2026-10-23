"""Render the old sealed forecast paths as readable text."""

from __future__ import annotations

import json
from pathlib import Path

SCRATCH = Path(__file__).resolve().parents[1] / "research" / "scratch"


def main() -> int:
    data = json.loads((SCRATCH / "old_paths.json").read_text(encoding="utf-8"))
    lines = []
    for scenario, block in data["scenarios"].items():
        lines.append(f"== {scenario} segment_subtotal {block['segment_subtotal']}")
        for name, path in block["segments"].items():
            lines.append(f"  {name}: {json.dumps(path, ensure_ascii=False)}")
    (SCRATCH / "old_paths.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
