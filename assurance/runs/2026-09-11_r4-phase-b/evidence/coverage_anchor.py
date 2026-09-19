"""Anchor an FC-1204 coverage measurement by CONTENT, not by the report file's own hash.

Why this exists (2026-09-19, after the B.VR-ba1 F-BA1-05 disposition was itself found wanting):
`coverage.json` carries `meta.timestamp` and `meta.version`, so its RAW sha256 changes on every
run even when the measurement is identical - and the repository's tracked copy is rewritten by
any coverage run.  The 2026-09-18 record anchored raw sha256
`8cf4a79333019bc0747b328f214575484c19262b5bc9324f66e3768494e8d947` (1,138,137 B) of a
working-tree file that was NOT retained, so nothing in the record can be re-checked against it.

This script produces two anchors and makes the difference explicit:

* `raw_sha256` - the report file exactly as coverage.py wrote it (with its timestamp);
* `measurement_sha256` - sha256 over the canonical JSON of `files` + `totals` ONLY, which is
  what a re-run can reproduce, and which is what the record cites.

Usage::

    python coverage_anchor.py [PATH-TO-coverage.json] [--expect MEASUREMENT_SHA256]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[3] / "coverage.json"


def anchors(path: Path) -> dict:
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    measurement = {
        "files": payload.get("files", {}),
        "totals": payload.get("totals", {}),
    }
    canonical = json.dumps(measurement, sort_keys=True, separators=(",", ":"))
    return {
        "path": str(path),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_byte_size": len(raw),
        "report_timestamp": (payload.get("meta") or {}).get("timestamp"),
        "report_version": (payload.get("meta") or {}).get("version"),
        "measurement_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "files": len(payload.get("files", {})),
        "percent_covered": (payload.get("totals") or {}).get("percent_covered"),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT)
    parser.add_argument("--expect", default=None,
                        help="expected measurement_sha256; a mismatch exits 1")
    args = parser.parse_args(argv)
    if not args.path.is_file():
        raise SystemExit(f"no coverage report at {args.path}")
    found = anchors(args.path)
    print(json.dumps(found, indent=2, ensure_ascii=True))
    if args.expect is not None and found["measurement_sha256"] != args.expect:
        print(f"MISMATCH: expected {args.expect}", file=sys.stderr)
        return 1
    if args.expect is not None:
        print("measurement digest matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
