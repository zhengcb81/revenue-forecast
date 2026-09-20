"""I-14-C r5: prove the deliverable diff is consumable by ``git apply`` (F-I14C-R4-04).

Round trip:

1. copy ``iso/product`` (pristine) into a scratch directory and ``git init`` it with
   ``core.autocrlf=false`` so the working tree bytes are the bytes git stores;
2. commit that as the "before" state;
3. ``git apply -p1 r5-changes.diff`` inside the repository;
4. sha256 the three modified files and compare with ``iso/product_fixed``.

Exit 0 only when all three files are byte-identical to the fixed tree, 3 otherwise.  The
reason the earlier difflib patch failed is recorded here as a checked precondition: the patch
must start with ``--- a/…`` / ``+++ b/…`` POSIX paths and apply cleanly with ``-p1``.

    python verify_git_apply.py --repo <scratch> --before <iso/product> --after <iso/product_fixed> \
        --diff <attempt>/r5-changes.diff --out <attempt>/r5/git_apply_verification.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
from pathlib import Path

FILES = (
    "src/company_wiki/source_catalog/worker.py",
    "src/company_wiki/source_catalog/observability.py",
    "src/company_wiki/source_catalog/cli.py",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _force_rmtree(path: Path) -> None:
    """git marks loose objects read-only; Windows then refuses to delete them."""

    def onerror(func, target, _exc):  # noqa: ANN001 - shutil callback signature
        try:
            Path(target).chmod(stat.S_IWRITE | stat.S_IREAD)
            func(target)
        except Exception:  # noqa: BLE001 - best effort cleanup
            pass

    if path.exists():
        shutil.rmtree(path, onerror=onerror)


def run(argv: list[str], cwd: Path) -> dict[str, object]:
    proc = subprocess.run(
        argv, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return {"argv": argv, "rc": proc.returncode, "stdout": proc.stdout.strip()[-400:],
            "stderr": proc.stderr.strip()[-800:]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    before = Path(args.before).resolve()
    after = Path(args.after).resolve()
    diff = Path(args.diff).resolve()

    _force_rmtree(repo)
    shutil.copytree(before, repo)

    steps: list[dict[str, object]] = [
        run(["git", "init", "-q", "."], repo),
        run(["git", "config", "core.autocrlf", "false"], repo),
        run(["git", "config", "core.safecrlf", "false"], repo),
        run(["git", "add", "-A"], repo),
        run(["git", "-c", "user.email=i14c@local", "-c", "user.name=i14c",
             "commit", "-q", "-m", "before"], repo),
    ]
    head = diff.read_text(encoding="utf-8", errors="replace").splitlines()[:3]
    steps.append(run(["git", "apply", "--check", "-p1", str(diff)], repo))
    steps.append(run(["git", "apply", "-p1", str(diff)], repo))

    comparison: dict[str, dict[str, object]] = {}
    for rel in FILES:
        applied = repo / rel
        target = after / rel
        applied_hash = sha256(applied) if applied.is_file() else None
        target_hash = sha256(target)
        comparison[Path(rel).name] = {
            "applied_sha256": applied_hash,
            "target_sha256": target_hash,
            "identical": applied_hash == target_hash,
        }

    payload: dict[str, object] = {
        "script": "harness/verify_git_apply.py",
        "diff": str(diff),
        "diff_bytes": diff.stat().st_size,
        "diff_head": head,
        "posix_paths_only": all(
            line.startswith("--- a/") or line.startswith("+++ b/") or not line.startswith(("---", "+++"))
            for line in diff.read_text(encoding="utf-8", errors="replace").splitlines()
        ),
        "repo": str(repo),
        "steps": steps,
        "applied_vs_target": comparison,
        "GIT_APPLY_REPRODUCES_T4": all(bool(v["identical"]) for v in comparison.values()),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"diff bytes={payload['diff_bytes']} posix_paths_only={payload['posix_paths_only']}")
    for name, info in comparison.items():
        print(f"{name}: identical={info['identical']} {info['applied_sha256']}")
    print(f"GIT_APPLY_REPRODUCES_T4={payload['GIT_APPLY_REPRODUCES_T4']}")
    return 0 if payload["GIT_APPLY_REPRODUCES_T4"] else 3


if __name__ == "__main__":
    sys.exit(main())
