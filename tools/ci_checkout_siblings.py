"""FC-1101: manifest-driven sibling checkout for CI.

Replaces hardcoded sibling pins (revenue quality.yml ad62592/77669ae,
filing quality.yml a42bb40) with the compatibility manifest's
``current_triplet`` — CI never clones floating main and never hardcodes a
commit outside the manifest.

Usage (from a workflow):
    python tools/ci_checkout_siblings.py --manifest <path to current.json>
        [--sibling-root <dir>] [--skip <repo> ...]

The sibling layout mirrors the local dev layout (repos as siblings of the
checkout), so the same tests run identically in CI and locally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run(args: list[str], *, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def checkout_siblings(
    manifest: dict,
    checkout_root: Path,
    *,
    skip: tuple[str, ...] = (),
) -> None:
    remotes = manifest["remotes"]
    triplet = manifest["current_triplet"]
    for repo in ("revenue", "filing", "wiki"):
        if repo in skip:
            continue
        dest = checkout_root / repo.replace("revenue", "revenue-forecast").replace(
            "filing", "filing-fetch").replace("wiki", "company-wiki")
        commit = triplet[repo]
        if dest.is_dir():
            _run(["git", "-C", str(dest), "fetch", "--quiet", "--depth", "1",
                  "origin", commit], cwd=dest)
            _run(["git", "-C", str(dest), "checkout", "--quiet", commit], cwd=dest)
        else:
            _run(["git", "clone", "--quiet", remotes[repo], str(dest)], cwd=checkout_root)
            _run(["git", "-C", str(dest), "checkout", "--quiet", commit], cwd=dest)
        print(f"checked out {repo} @ {commit[:12]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sibling-root", type=Path, default=None,
                        help="dir to hold siblings (default: manifest parent / ..)")
    parser.add_argument("--skip", nargs="*", default=(),
                        help="repos to skip (e.g. revenue when running in it)")
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    root = args.sibling_root or args.manifest.resolve().parents[1]  # repo root
    checkout_siblings(manifest, root, skip=tuple(args.skip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
