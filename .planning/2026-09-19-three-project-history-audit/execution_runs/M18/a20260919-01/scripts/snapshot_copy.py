"""Materialise the read-only isolated snapshot of the two product modules.

Copies scripts/model_registry.py and scripts/model_extensions.py from the
production repository (read-only) into <attempt>/iso/checkout_scripts and then
VERIFIES that each copy is byte-identical to the production file it came from.

Usage:
  python -X utf8 -B snapshot_copy.py --production-root <repo> --dest <iso/checkout_scripts>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil

FILES = ("model_registry.py", "model_extensions.py")
ANCHORED_PRODUCTION_HASHES = {
    "model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production-root", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--record", default=None)
    args = parser.parse_args()

    os.makedirs(args.dest, exist_ok=True)
    record = {"production_root": os.path.abspath(args.production_root),
              "dest": os.path.abspath(args.dest), "files": {}}
    ok = True
    for name in FILES:
        source = os.path.join(args.production_root, "scripts", name)
        target = os.path.join(args.dest, name)
        shutil.copyfile(source, target)
        production_hash = sha256(source)
        copy_hash = sha256(target)
        matches_anchor = production_hash == ANCHORED_PRODUCTION_HASHES[name]
        identical = production_hash == copy_hash
        ok = ok and matches_anchor and identical
        record["files"][name] = {
            "production_path": os.path.abspath(source),
            "copy_path": os.path.abspath(target),
            "production_sha256": production_hash,
            "copy_sha256": copy_hash,
            "anchored_sha256": ANCHORED_PRODUCTION_HASHES[name],
            "production_matches_anchor": matches_anchor,
            "copy_is_byte_identical_to_production": identical,
        }
        print(name, production_hash, "identical_to_copy", identical, "matches_anchor", matches_anchor)
    record["all_ok"] = ok
    if args.record:
        os.makedirs(os.path.dirname(os.path.abspath(args.record)), exist_ok=True)
        with open(args.record, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=1)
        print("record ->", os.path.abspath(args.record))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
