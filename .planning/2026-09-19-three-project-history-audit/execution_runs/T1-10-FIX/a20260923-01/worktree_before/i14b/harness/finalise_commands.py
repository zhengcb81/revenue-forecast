"""Normalise commands.json after the r2 edit: validate JSON, fold the r2 return
codes into the top-level raw/expected maps, and re-dump deterministically.

Usage:
  <iso-python> -X utf8 -B harness/finalise_commands.py
"""

from __future__ import annotations

import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
PATH = ATTEMPT / "commands.json"

R2_RC = {
    "CMD-I14B-R2-ARCHIVE": 0,
    "CMD-I14B-R2-FREEZE": 0,
    "CMD-I14B-R2-CASES-before-r1sut": 1,
    "CMD-I14B-R2-CASES-before-baseline": 1,
    "CMD-I14B-R2-CASES-after": 0,
    "CMD-I14B-R2-SUITE-before": 1,
    "CMD-I14B-R2-SUITE-after": 0,
    "CMD-I14B-R2-SUITE-r1suite-vs-r2sut": 0,
    "CMD-I14B-R2-REPEAT-1": 0,
    "CMD-I14B-R2-REPEAT-2": 0,
    "CMD-I14B-R2-REPEAT-3": 0,
    "CMD-I14B-R2-MUTATE": 0,
    "CMD-I14B-R2-TOLERANCE-SWEEP": 0,
    "CMD-I14B-R2-CALENDAR-MAP": 0,
    "CMD-I14B-R2-MAKE-DIFF": 0,
    "CMD-I14B-R2-SNAPSHOT": 0,
}


def main() -> int:
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    doc.setdefault("raw_exit_codes", {}).update(R2_RC)
    doc.setdefault("expected_exit_codes", {}).update(R2_RC)
    doc["r2_raw_exit_codes_all_match_expected"] = all(
        c["raw_returncode"] == c["expected_returncode"]
        for c in doc["r2_commands"]
        if isinstance(c.get("raw_returncode"), int)
    )
    PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "valid_json": True,
        "r1_commands": len(doc.get("commands", [])),
        "r2_commands": len(doc.get("r2_commands", [])),
        "r2_all_rc_match": doc["r2_raw_exit_codes_all_match_expected"],
        "keys": len(doc),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
