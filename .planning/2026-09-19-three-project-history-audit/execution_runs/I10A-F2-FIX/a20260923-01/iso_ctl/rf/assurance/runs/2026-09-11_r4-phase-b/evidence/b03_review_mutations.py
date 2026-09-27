"""B.VR(B03) independent mutation check of the NEW B03 acceptance file.

The author shipped no mutation evidence for B03 (the B01/B02 harnesses cover
other steps), so this measures the teeth of the 13 cases myself.  The product
repo is NEVER modified: everything runs in a throwaway copy of src/ + tests/
under %TEMP%.

Usage: python b03_review_mutations.py <out.json>
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RESOLVER_REL = Path("src/company_wiki/source_catalog/resolver.py")
TEST_REL = "tests/contract/test_r4b03_stable_bytes.py"

# (id, old, new, what it breaks)
MUTANTS = [
    (
        "M1_serve_on_claim",
        "    if not expected_sha256 or computed != expected_sha256:",
        "    if False:",
        "the digest gate itself: the buffer is returned even when its digest "
        "differs from the requested version",
    ),
    (
        "M2_recheck_off",
        "    if int(after.st_size) != size or int(after.st_mtime_ns) != int(before.st_mtime_ns):",
        "    if False:",
        "the size+mtime re-check after the read",
    ),
    (
        "M3_containment_off",
        "    target = os.path.normcase(os.path.realpath(path))",
        "    target = os.path.normcase(os.path.realpath(path))\n    return True",
        "the out-of-root locator refusal",
    ),
    (
        "M4_inloop_cancel_off",
        "                if budget is not None and budget.cancelled:",
        "                if False:",
        "the in-loop (mid-read) cancellation check",
    ),
    (
        "M5_hydration_off",
        "    if _needs_hydration(before):",
        "    if False:",
        "the cloud-placeholder refusal",
    ),
]


def copy_tree(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("src", "tests"):
        shutil.copytree(WIKI / name, dest / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copy2(WIKI / "pytest.ini", dest / "pytest.ini")


def run_tests(root: Path) -> dict:
    import os

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_REL, "-q", "-p", "no:randomly",
         "--tb=no", "-rf"],
        cwd=root, capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=env,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    failed = [
        line.split("::", 1)[-1].strip()
        for line in out.splitlines()
        if line.startswith("FAILED ")
    ]
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    return {"returncode": proc.returncode, "failed": failed, "tail": tail[-160:]}


def _path_env() -> str:
    import os

    return os.environ.get("PATH", "")


def _sysroot() -> str:
    import os

    return os.environ.get("SYSTEMROOT", r"C:\Windows")


def main(argv):
    out_path = Path(argv[1]) if len(argv) > 1 else Path(tempfile.gettempdir()) / "b03_review_mutations.json"
    root = Path(tempfile.mkdtemp(prefix="bvr03-mut-"))
    copy_tree(root)
    resolver = root / RESOLVER_REL
    original = io.open(resolver, encoding="utf-8", newline="").read()

    results = []
    baseline = run_tests(root)
    results.append({"id": "baseline", "status": "n/a", "result": baseline})

    for mid, old, new, breaks in MUTANTS:
        text = original
        if old not in text:
            results.append({"id": mid, "status": "pattern_missing", "breaks": breaks})
            continue
        io.open(resolver, "w", encoding="utf-8", newline="").write(
            text.replace(old, new, 1)
        )
        outcome = run_tests(root)
        io.open(resolver, "w", encoding="utf-8", newline="").write(original)
        results.append(
            {
                "id": mid,
                "status": "killed" if outcome["failed"] else "SURVIVED",
                "breaks": breaks,
                "killed_by": outcome["failed"],
                "result": outcome,
            }
        )

    # the copy must be disposed of with the original content back
    restored = io.open(resolver, encoding="utf-8", newline="").read() == original
    payload = {
        "probe": "b03_review_mutations",
        "wiki_head": subprocess.run(
            ["git", "-C", str(WIKI), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        ).stdout.strip(),
        "product_repo_untouched": True,
        "isolated_copy": str(root),
        "copy_restored": restored,
        "results": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    for row in results:
        print(row["id"], "->", row.get("status"), row.get("killed_by", ""))
    print(f"wrote {out_path}")
    shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
