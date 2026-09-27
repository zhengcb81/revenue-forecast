"""I-14-E-TESTSIDE: byte-level inventory for the boundary self-proof.

Usage:
    python hashes.py before   -> before/hashes_before.json
    python hashes.py after    -> after/hashes_after.json
    python hashes.py check    -> after/boundary_check.json (compares before vs after)

Scope of every inventory (identical on both sides, so the comparison is stable):
  * every file below the root, EXCEPT directories named ``__pycache__`` and
    files ending in ``.pyc`` / ``.pyo`` (derived artefacts of *other*
    sessions' runs, not product bytes).

Inventories produced:
  * real production repo  ``company-wiki/{src,scripts,tests}`` + ``pytest.ini``
    + root ``conftest.py``  (the read-only source; must be byte-identical)
  * the attempt's iso copy ``iso/{src,scripts,tests,config}`` + ``iso/pytest.ini``
    + ``iso/conftest.py``
    - ``iso/src`` and ``iso/scripts`` MUST be byte-identical before/after
    - ``iso/tests`` MUST equal the real repo BEFORE the fix and differ only in
      ``tests/**`` files AFTER the fix (see changes.diff)
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RF = ATTEMPT.parents[4]                     # .../revenue-forecast
CW = RF.parent / "company-wiki"             # real production repo (read-only)
CARD = "I-14-E-TESTSIDE"
ATTEMPT_ID = "a20260924-01"

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIX = {".pyc", ".pyo"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not root.exists():
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if Path(name).suffix in SKIP_SUFFIX:
                continue
            fp = Path(dirpath) / name
            rel = fp.relative_to(root).as_posix()
            out[rel] = {"sha256": sha256(fp), "bytes": fp.stat().st_size}
    return out


def manifest(files: dict[str, dict]) -> str:
    blob = "\n".join(f"{k} {v['sha256']} {v['bytes']}" for k, v in sorted(files.items()))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def targets() -> dict[str, dict[str, dict]]:
    return {
        "CW/src": inventory(CW / "src"),
        "CW/scripts": inventory(CW / "scripts"),
        "CW/tests": inventory(CW / "tests"),
        "CW/pytest.ini": {"pytest.ini": _file(CW / "pytest.ini")},
        "CW/conftest.py": {"conftest.py": _file(CW / "conftest.py")},
        "iso/src": inventory(ATTEMPT / "iso" / "src"),
        "iso/scripts": inventory(ATTEMPT / "iso" / "scripts"),
        "iso/tests": inventory(ATTEMPT / "iso" / "tests"),
        "iso/config": inventory(ATTEMPT / "iso" / "config"),
        "iso/pytest.ini": {"pytest.ini": _file(ATTEMPT / "iso" / "pytest.ini")},
        "iso/conftest.py": {"conftest.py": _file(ATTEMPT / "iso" / "conftest.py")},
    }


def _file(path: Path) -> dict:
    return {"sha256": sha256(path), "bytes": path.stat().st_size} if path.is_file() else {}


def git_readonly(repo: Path) -> dict:
    """Read-only git facts (no index/worktree writes of any kind)."""
    def run(*args: str) -> str:
        r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=str(repo),
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, encoding="utf-8", errors="replace")
        return r.stdout.strip()
    try:
        return {
            "head": run("rev-parse", "HEAD"),
            "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "porcelain_line_count": len([l for l in run("status", "--porcelain").splitlines() if l]),
        }
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


def build(phase: str) -> dict:
    inv = targets()
    payload = {
        "card": CARD,
        "attempt": ATTEMPT_ID,
        "phase": phase,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inventory_rules": {
            "excluded_dirs": sorted(SKIP_DIRS),
            "excluded_suffixes": sorted(SKIP_SUFFIX),
            "note": "identical rule on the before and after side, so the comparison is "
                    "stable; product bytes are never excluded",
        },
        "roots": {
            "CW": str(CW),
            "iso": str(ATTEMPT / "iso"),
        },
        "files": inv,
        "manifests": {k: manifest(v) for k, v in inv.items()},
        "file_counts": {k: len(v) for k, v in inv.items()},
        "bytes_totals": {k: sum(f["bytes"] for f in v.values()) for k, v in inv.items()},
        "git_company_wiki": git_readonly(CW),
        "git_revenue_forecast": git_readonly(RF),
    }
    return payload


def check() -> dict:
    before = json.loads((ATTEMPT / "before" / "hashed_before.json").read_text(encoding="utf-8"))
    after = json.loads((ATTEMPT / "after" / "hashed_after.json").read_text(encoding="utf-8"))
    must_equal = ["CW/src", "CW/scripts", "CW/tests", "CW/pytest.ini", "CW/conftest.py",
                  "iso/src", "iso/scripts", "iso/config", "iso/pytest.ini", "iso/conftest.py"]
    checks = {}
    all_equal = True
    for key in must_equal:
        b = before["manifests"].get(key)
        a = after["manifests"].get(key)
        eq = b is not None and b == a
        all_equal &= eq
        checks[key] = {"before_manifest": b, "after_manifest": a, "equal": eq,
                       "files_before": before["file_counts"].get(key),
                       "files_after": after["file_counts"].get(key)}
    # iso/tests: was a faithful copy before, and after the fix differs ONLY under tests/**
    iso_tests_equal_before = before["manifests"]["iso/tests"] == before["manifests"]["CW/tests"]
    checks["iso/tests_copy_was_faithful"] = {
        "before_iso_tests == before_CW/tests": iso_tests_equal_before,
        "before_manifest": before["manifests"]["iso/tests"],
        "cw_manifest": before["manifests"]["CW/tests"],
    }
    checks["iso/tests_changed"] = {
        "changed": before["manifests"]["iso/tests"] != after["manifests"]["iso/tests"],
        "before_manifest": before["manifests"]["iso/tests"],
        "after_manifest": after["manifests"]["iso/tests"],
    }
    # per-file diff of iso/tests, so the "only tests/**" claim is machine-checked
    b_files = before["files"]["iso/tests"]
    a_files = after["files"]["iso/tests"]
    changed = sorted(k for k in set(b_files) | set(a_files)
                     if b_files.get(k) != a_files.get(k))
    checks["iso/tests_changed_files"] = changed
    # the inventory root is iso/tests, so every entry is a tests/** path by
    # construction (no ".." escapes); the "changes.diff touches only tests/**"
    # claim itself is checked by harness/make_diff.py against the real repo.
    checks["iso/tests_changed_files_all_under_tests"] = all(
        not c.startswith("../") for c in changed)
    payload = {
        "card": CARD,
        "attempt": ATTEMPT_ID,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "before_source": "before/hashed_before.json",
        "after_source": "after/hashed_after.json",
        "all_required_equal": all_equal,
        "checks": checks,
        "git_diff_non_planning": _non_planning_diff(RF),
        "git_company_wiki_porcelain_after": after["git_company_wiki"],
        "git_company_wiki_porcelain_before": before["git_company_wiki"],
        "verdict": ("BOUNDARY_OK" if all_equal and iso_tests_equal_before
                    and checks["iso/tests_changed"]["changed"] else "BOUNDARY_BREACH"),
    }
    return payload


def _non_planning_diff(repo: Path) -> dict:
    r = subprocess.run(["git", "-c", "core.quotepath=false", "diff", "HEAD", "--name-only"],
                       cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       text=True, encoding="utf-8", errors="replace")
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    non = [l for l in lines if not l.startswith(".planning")]
    return {"total_lines": len(lines), "non_planning_count": len(non),
            "non_planning_paths": non}


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else "before"
    if phase == "before":
        payload = build("before")
        out = ATTEMPT / "before" / "hashed_before.json"
    elif phase == "after":
        payload = build("after")
        out = ATTEMPT / "after" / "hashed_after.json"
    elif phase == "check":
        payload = check()
        out = ATTEMPT / "after" / "boundary_check.json"
        # the card and the parent both name the consolidated proof
        # ``before/final_hashes.json``; write the identical payload there too.
        for alias in (ATTEMPT / "before" / "final_hashes.json",
                      ATTEMPT / "after" / "final_hashes.json"):
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    else:
        raise SystemExit(f"unknown phase {phase!r}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    if phase == "check":
        print(json.dumps({"verdict": payload["verdict"],
                          "all_required_equal": payload["all_required_equal"],
                          "git_diff_non_planning": payload["git_diff_non_planning"],
                          "iso_tests_changed_files": payload["checks"]["iso/tests_changed_files"]},
                         indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"phase": phase, "manifests": payload["manifests"],
                          "file_counts": payload["file_counts"]}, indent=2, ensure_ascii=False))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
