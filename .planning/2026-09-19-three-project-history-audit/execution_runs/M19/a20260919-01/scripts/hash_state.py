"""Capture the repository state (git status + source hashes) before and after the card run.

Read-only: `git status --porcelain` and file hashing only.  No git add/commit/restore/stash.

Usage:
  python -X utf8 -B hash_state.py --out <attempt>/before [--phase before|after]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

REPOS = {
    "revenue-forecast": r"C:\Users\郑曾波\Projects\revenue-forecast",
    "company-wiki": r"C:\Users\郑曾波\Projects\company-wiki",
    "filing-fetch": r"C:\Users\郑曾波\Projects\filing-fetch",
}
WATCHED = ("scripts/model_registry.py", "scripts/model_extensions.py", "scripts/forecast/segments.py")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="directory to write into (before/ or after/)")
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    summary = {"attempt_root": os.path.abspath(args.attempt_root), "repos": {}}
    for name, root in REPOS.items():
        entry = {"path": root, "exists": os.path.isdir(root)}
        if entry["exists"]:
            try:
                completed = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                                           capture_output=True, text=True,
                                           encoding="utf-8", errors="replace")
                text = completed.stdout or ""
                entry["git_status_porcelain_returncode"] = completed.returncode
                entry["git_status_porcelain_lines"] = len(text.splitlines())
                status_path = os.path.join(args.out, "git_status_%s.txt" % name)
                with open(status_path, "w", encoding="utf-8") as handle:
                    handle.write(text)
                entry["git_status_path"] = os.path.abspath(status_path)
                entry["git_status_sha256"] = sha256(status_path)
            except Exception as exc:  # noqa: BLE001
                entry["git_status_error"] = "%s: %s" % (type(exc).__name__, exc)
        if name == "revenue-forecast":
            entry["watched_hashes"] = {}
            for rel in WATCHED:
                path = os.path.join(root, rel)
                if os.path.isfile(path):
                    entry["watched_hashes"][rel] = sha256(path)
        summary["repos"][name] = entry

    hashes_path = os.path.join(args.out, "source_hashes.txt")
    with open(hashes_path, "w", encoding="utf-8") as handle:
        for name, entry in summary["repos"].items():
            handle.write("# %s %s\n" % (name, entry["path"]))
            for rel, digest in sorted(entry.get("watched_hashes", {}).items()):
                handle.write("%s  %s\n" % (digest, rel))
    summary["source_hashes_path"] = os.path.abspath(hashes_path)
    summary["source_hashes_sha256"] = sha256(hashes_path)

    json_path = os.path.join(args.out, "state.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=1)

    for name, entry in summary["repos"].items():
        print(name, "dirty_lines", entry.get("git_status_porcelain_lines"),
              "watched", entry.get("watched_hashes"))
    print("written", json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
