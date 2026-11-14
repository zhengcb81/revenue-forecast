"""Record the verified round-4 delta in the handoff."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    path = ROOT / "handoff.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["review"]["round4"] = {
        "verdict": "PASS",
        "open_p1": 0,
        "open_p2": 0,
        "open_p3": 4,
        "verified_content_commit": payload["head_commit"],
        "note": (
            "final delta check: the pinned commit resolves, its snapshot blob hashes to the recorded "
            "4798e682..., the input blob still hashes to d82f9b45... and still validates, and every "
            "changed file in d347c4ab..HEAD is inside .planning/rf-input-prep-01/. The four remaining "
            "P3s are the disclosed limitations (empty publication audit artifact, catalog admission "
            "NOT_RUN, Alibaba NOT_RUN, management-target ledger NOT_RUN)."
        ),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload["review"]["round4"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
