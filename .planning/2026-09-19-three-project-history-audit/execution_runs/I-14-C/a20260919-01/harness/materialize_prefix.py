"""I-14-C: materialise the PRE-FIX product modules read-only, for a controlled before-pass.

Uses ``git show HEAD:<path>`` (read-only plumbing; it does NOT touch the index,
the worktree or the user's dirty files) to reconstruct the exact committed bytes
of the three modules this card edits, then verifies each reconstructed file
against the sha256 recorded in binding.json.

    python materialize_prefix.py --cw <company-wiki> --out <attempt>/before/prefix_src
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MODULES = {
    "src/company_wiki/source_catalog/worker.py":
        "e83179915333eb472807b15a0580d93dcf280caadc31b0099988a3b744c469c6",
    "src/company_wiki/source_catalog/observability.py":
        "a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a",
    "src/company_wiki/source_catalog/cli.py":
        "2f5c5740343697078d1e69b3a6a9ef9b0809277799c2d9c28a2d3e4048c4d512",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cw", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rev", default="HEAD")
    args = parser.parse_args(argv)

    cw = Path(args.cw)
    out = Path(args.out)
    rows = []
    ok = True
    for rel, expected in MODULES.items():
        proc = subprocess.run(
            ["git", "-C", str(cw), "show", f"{args.rev}:{rel}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            rows.append({"path": rel, "status": "git-show-failed",
                         "rc": proc.returncode,
                         "stderr": proc.stderr.decode("utf-8", "replace")})
            ok = False
            continue
        data = proc.stdout
        digest = hashlib.sha256(data).hexdigest()
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({
            "path": rel,
            "status": "ok" if digest == expected else "HASH-MISMATCH",
            "sha256": digest,
            "expected_sha256": expected,
            "bytes": len(data),
            "target": str(target),
        })
        ok = ok and digest == expected
    report = {"rev": args.rev, "all_hashes_match": ok, "files": rows}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
