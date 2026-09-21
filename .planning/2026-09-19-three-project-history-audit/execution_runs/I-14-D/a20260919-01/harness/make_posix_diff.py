"""I-14-C r5: emit a patch that a PLAIN `git apply -p1` consumes.

F-I14C-R4-04: the r4 diff was produced by `git diff --no-index` on Windows, which wrote
backslashes into the blob paths (`a/product\\src/...`) so `git apply --directory=product`
failed.  A hand-written difflib patch with `a/src/...` headers is not enough either: the
trees here mix CRLF and LF, and git skips hunks whose context bytes do not match.

Correct approach: let git itself produce the patch, in an isolated scratch repository whose
byte content is exactly the two trees, with autocrlf disabled so no newline translation is
applied on either side.

  1. temp repo; commit a copy of <before>/src
  2. overwrite with <after>/src
  3. `git -c core.autocrlf=false diff` -> POSIX paths, correct line-ending bytes

Nothing under the product checkouts is touched: both trees are attempt-local copies.

    python make_posix_diff.py --before <iso>/product --after <iso>/product_fixed \
        --out <attempt>/r5-changes.diff --scratch <attempt>/r5/diff-repo
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

TARGETS = (
    "src/company_wiki/source_catalog/worker.py",
    "src/company_wiki/source_catalog/observability.py",
    "src/company_wiki/source_catalog/cli.py",
)


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=str(cwd), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)


def _force_rmtree(path: Path) -> None:
    """git marks loose objects read-only on Windows; clear the bit before unlinking."""
    import os
    import stat

    def on_error(func, target, _exc):
        try:
            os.chmod(target, stat.S_IWRITE)
            func(target)
        except OSError:
            pass

    if path.exists():
        shutil.rmtree(path, onerror=on_error)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--scratch", required=True)
    args = parser.parse_args(argv)

    before = Path(args.before).resolve()
    after = Path(args.after).resolve()
    scratch = Path(args.scratch).resolve()
    out = Path(args.out)

    if scratch.exists():
        _force_rmtree(scratch)
    scratch.mkdir(parents=True)
    shutil.copytree(before / "src", scratch / "src")
    for cache in scratch.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)

    report: dict = {"before": str(before), "after": str(after), "scratch": str(scratch),
                    "steps": []}
    for step in (["git", "init", "-q", "."],
                 ["git", "config", "core.autocrlf", "false"],
                 ["git", "config", "core.safecrlf", "false"],
                 ["git", "add", "-A"],
                 ["git", "-c", "user.email=i14c@local", "-c", "user.name=i14c",
                  "commit", "-q", "-m", "before"]):
        proc = _run(step, scratch)
        report["steps"].append({"argv": step, "rc": proc.returncode,
                                "stderr": proc.stderr.decode("utf-8", "replace")[:200]})
        if proc.returncode != 0:
            print(json.dumps(report, indent=2, ensure_ascii=True))
            return 1

    _force_rmtree(scratch / "src")
    shutil.copytree(after / "src", scratch / "src")
    for cache in scratch.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)

    proc = _run(["git", "-c", "core.autocrlf=false", "diff", "--no-color",
                 "--src-prefix=a/", "--dst-prefix=b/"], scratch)
    if proc.returncode != 0:
        report["diff_stderr"] = proc.stderr.decode("utf-8", "replace")
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return 1
    patch = proc.stdout.decode("utf-8")
    out.write_text(patch, encoding="utf-8", newline="")

    report["out"] = str(out)
    report["bytes"] = out.stat().st_size
    report["files"] = [rel for rel in TARGETS if f"b/{rel}" in patch]
    report["hunks"] = sum(1 for line in patch.splitlines() if line.startswith("@@"))
    report["posix_paths_only"] = all(
        "\\" not in line for line in patch.splitlines()
        if line.startswith(("--- ", "+++ ", "diff --git")))
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["posix_paths_only"] and report["files"] else 1


if __name__ == "__main__":
    sys.exit(main())
