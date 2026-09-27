"""Round-2 pin recheck for WC-4 (reviewer finding F-03).

Recomputes, point in time, every one of the 19 binding.json pins (sha256 +
bytes) and re-locates every verbatim line captured in
evidence/pins_freeze.txt inside the current file, reporting the line number
now vs. the frozen one.

Nothing is written outside the attempt directory; binding.json and
evidence/pins_freeze.txt are read only (F-03 says: record the drift, never
rewrite the pin table).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
BINDING = ATTEMPT / "binding.json"
FREEZE = ATTEMPT / "evidence" / "pins_freeze.txt"
OUT = ATTEMPT / "evidence" / "rgm2" / "pins_r2.json"

SECTION = re.compile(r"^===== (\S+) :: (.+?) :: (.*?) =====$")
# pins_freeze.txt right-aligns the line number in a 5-wide field: " 1655:",
# "  104:", "   64:"
LINENO = re.compile(r"^ *(\d+): (.*)$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_freeze() -> dict[str, dict]:
    sections: dict[str, dict] = {}
    current = None
    for raw in FREEZE.read_text(encoding="utf-8").splitlines():
        head = SECTION.match(raw)
        if head:
            current = head.group(1)
            sections[current] = {
                "path": head.group(2),
                "header": head.group(3),
                "lines": {},
            }
            continue
        if current is None:
            continue
        entry = LINENO.match(raw)
        if entry:
            sections[current]["lines"][int(entry.group(1))] = entry.group(2)
    return sections


def main() -> int:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    frozen = parse_freeze()
    results = []
    for pin in binding["pins"]:
        path = Path(pin["path"])
        exists = path.exists()
        data = path.read_bytes() if exists else b""
        entry = {
            "id": pin["id"],
            "path": pin["path"],
            "pin_sha256": pin["sha256"],
            "now_sha256": sha(data) if exists else None,
            "sha_match": exists and sha(data) == pin["sha256"],
            "pin_bytes": pin["bytes"],
            "now_bytes": len(data) if exists else None,
            "bytes_match": exists and len(data) == pin["bytes"],
        }
        sec = frozen.get(pin["id"])
        if sec and sec["lines"]:
            text = data.decode("utf-8", "replace") if exists else ""
            now_lines = text.splitlines()
            located = []
            for frozen_no, verbatim in sec["lines"].items():
                hits = [i + 1 for i, line in enumerate(now_lines) if line == verbatim]
                # blank/short verbatim lines occur many times; the hit nearest
                # the frozen line number is the meaningful one
                best = min(hits, key=lambda h: (abs(h - frozen_no), h)) if hits else None
                blank = verbatim.strip() == ""
                located.append({
                    "frozen_line": frozen_no,
                    "verbatim_found_at": hits[:20],
                    "verbatim_hit_count": len(hits),
                    "verbatim_match": bool(hits),
                    # a blank verbatim line matches many places, so its "delta"
                    # is not meaningful - excluded from line_deltas
                    "blank_verbatim": blank,
                    "delta": None if (blank or best is None) else best - frozen_no,
                })
            entry["frozen_line_count"] = len(sec["lines"])
            entry["verbatim_all_found"] = all(x["verbatim_match"] for x in located)
            entry["line_deltas"] = sorted(
                {x["delta"] for x in located if x["delta"] is not None})
            entry["located"] = located
        results.append(entry)

    drift = [r for r in results if not r["sha_match"]]
    payload = {
        "card": "WC-4 = F12-RC120",
        "round": "r2",
        "finding": "F-03 (P3): binding 19 pins - 9 DRIFT / 10 MATCH at review time",
        "pins_total": len(results),
        "sha_match_now": len(results) - len(drift),
        "sha_drift_now": len(drift),
        "drift_ids": [r["id"] for r in drift],
        "pins": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"total={payload['pins_total']} match={payload['sha_match_now']} "
          f"drift={payload['sha_drift_now']}")
    for r in drift:
        print(f"  DRIFT {r['id']}: {r['pin_bytes']}/{r['pin_sha256'][:16]} -> "
              f"{r['now_bytes']}/{str(r['now_sha256'])[:16]} "
              f"verbatim_all_found={r.get('verbatim_all_found')} "
              f"line_deltas={r.get('line_deltas')}")
    for r in results:
        if r["sha_match"]:
            print(f"  MATCH {r['id']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
