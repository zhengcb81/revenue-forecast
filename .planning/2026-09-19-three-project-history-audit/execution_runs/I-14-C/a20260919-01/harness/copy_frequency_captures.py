"""I-14-C r5 (F-I14C-R5-03): land the frequency measurement's per-run stdout inside the attempt.

The reviewer's finding: the 48 rows of ``r5/flake-evidence/frequency-child_without_runtime.json``
carry only ``tail``/``assertion``/``verdict``/``returncode``, while the deep/short basetemp runs
have full per-run captures, so "every failure is the same ``assert 3 == 2``" could only be
partially checked.

This script copies each run's FULL stdout from the scratch basetemp root into
``r5/flake-evidence/frequency-captures/`` and APPENDS a ``captures`` block to the JSON:

* the 48 existing rows are never modified (the reviewer recomputed its numbers from them, so they
  must stay exactly as reviewed);
* every copied file is hashed and the copy is verified byte-for-byte against the source;
* the source scratch root is left in place (nothing is deleted or moved).

``harness/run_flake_frequency.py`` now writes these captures itself, so future runs need no copy
step; this is the backfill for the recorded run.

    python copy_frequency_captures.py --attempt <attempt> \
        --source %TEMP%/i14c-flake-freq --json r5/flake-evidence/frequency-child_without_runtime.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--capture-dir", default="r5/flake-evidence/frequency-captures")
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    source = Path(os.path.expandvars(args.source))
    json_path = attempt / args.json if not Path(args.json).is_absolute() else Path(args.json)
    capture_dir = attempt / args.capture_dir
    capture_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    rows = payload["results"]

    copied: list[dict] = []
    missing: list[str] = []
    for row in rows:
        run_dir = Path(row["cwd"])
        source_stdout = run_dir / "stdout.txt"
        if not source_stdout.is_file():
            missing.append(str(source_stdout))
            continue
        name = f"p{row['pass']}-{row['tree']}-{payload['node']}-{row['run']}.txt"
        target = capture_dir / name
        shutil.copyfile(source_stdout, target)
        source_hash = sha256_file(source_stdout)
        target_hash = sha256_file(target)
        copied.append({
            "pass": row["pass"],
            "tree": row["tree"],
            "run": row["run"],
            "verdict": row["verdict"],
            "source": str(source_stdout),
            "capture": str(target.relative_to(attempt)),
            "sha256": target_hash,
            "bytes": target.stat().st_size,
            "copy_verified": source_hash == target_hash,
            "assertion_lines": [
                line.strip()[:200]
                for line in target.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.startswith("E   AssertionError") or line.startswith("E   Failed")
            ],
        })

    payload["captures"] = {
        "added_by": "harness/copy_frequency_captures.py (F-I14C-R5-03 backfill)",
        "source_root": str(source),
        "source_root_left_in_place": True,
        "rows_modified": False,
        "rows_note": (
            "the 48 rows above are unchanged from the reviewed run; the captures below were "
            "copied from the scratch basetemp root afterwards, and harness/run_flake_frequency.py "
            "now writes them itself"
        ),
        "capture_dir": args.capture_dir,
        "copied": len(copied),
        "missing": missing,
        "all_copies_verified": all(bool(item["copy_verified"]) for item in copied) and not missing,
        "files": copied,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    failures = [item for item in copied if item["verdict"] == "failed"]
    distinct_assertions = sorted({a for item in failures for a in item["assertion_lines"]})
    print(f"copied={len(copied)} missing={len(missing)} "
          f"all_copies_verified={payload['captures']['all_copies_verified']}")
    print(f"failed rows with a capture: {len(failures)}")
    print(f"distinct assertion lines across all failures: {distinct_assertions}")
    return 0 if payload["captures"]["all_copies_verified"] else 3


if __name__ == "__main__":
    sys.exit(main())
