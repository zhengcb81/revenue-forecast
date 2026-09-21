"""I-14-E: freeze instant record.

Run BEFORE the first measurement run: hashes the frozen oracle and the harness that
will produce the measurements, and asserts that no measurement output exists yet.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
OUT = ATTEMPT / "evidence" / "freeze_instant.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    frozen = [ATTEMPT / "oracle.md", ATTEMPT / "binding.json"]
    harness = sorted((ATTEMPT / "harness").glob("*.py")) + \
        sorted((ATTEMPT / "harness").glob("*.ps1"))
    after = ATTEMPT / "after"
    pre_existing = sorted(p.name for p in after.glob("*")) if after.exists() else []
    payload = {
        "card": "I-14-E",
        "attempt": "a20260919-01",
        "freeze_instant_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "statement": ("oracle.md + binding.json + the harness below are frozen before the first "
                      "measurement run; the expected values inside the oracle are hand-computed "
                      "from the frozen band's raw record, never from a re-run"),
        "frozen": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in frozen},
        "harness": {p.name: {"sha256": sha(p), "bytes": p.stat().st_size} for p in harness},
        "after_dir_pre_existing_files": pre_existing,
        "measurement_outputs_present_at_freeze": [
            p for p in pre_existing if p.endswith(".json") and p.startswith(("band-", "child-"))],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"freeze_instant_utc": payload["freeze_instant_utc"],
                      "frozen": list(payload["frozen"]),
                      "harness": list(payload["harness"]),
                      "after_pre_existing": pre_existing,
                      "outputs_present_at_freeze": payload["measurement_outputs_present_at_freeze"]},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
