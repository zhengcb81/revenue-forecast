"""I-14-E-APPLY: prove the production repos were NOT written in place.

Records, for the three production trees this card could conceivably have touched:
  * the hash of the SUT test file and both launcher scripts
  * ``git status --porcelain`` for the whole company-wiki checkout
  * a recursive content hash of the directories that hold the anchors

Run once BEFORE the campaign (``--snapshot``) and once AFTER (``--verify``); the
verify pass fails loudly if any recorded value moved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
HOME = Path(os.environ["USERPROFILE"])

TREES = {
    "company-wiki": HOME / "Projects" / "company-wiki",
    "revenue-forecast": HOME / "Projects" / "revenue-forecast",
    "daily-news": HOME / "Projects" / "daily-news",
}
# directories that actually contain the anchors this card is about
SCAN_DIRS = {
    "company-wiki": ["tests/contract", "scripts"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hashes(root: Path, rels: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in rels:
        base = root / rel
        if not base.exists():
            out[rel] = "<missing>"
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                out[str(path.relative_to(root)).replace("\\", "/")] = sha256(path)
    return out


def git_status(root: Path) -> dict:
    if not (root / ".git").exists():
        return {"git": False}
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          capture_output=True, text=True)
    branch = subprocess.run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True)
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                            capture_output=True, text=True)
    return {"git": True, "head": head.stdout.strip(), "branch": branch.stdout.strip(),
            "porcelain_lines": len([ln for ln in status.stdout.splitlines() if ln.strip()]),
            "porcelain_sha256": hashlib.sha256(status.stdout.encode()).hexdigest(),
            "porcelain_head20": status.stdout.splitlines()[:20]}


def snapshot() -> dict:
    payload = {"card": "I-14-E-APPLY", "attempt": "a20260921-01",
               "taken_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "trees": {}}
    for name, root in TREES.items():
        entry: dict = {"path": str(root), "exists": root.exists()}
        if root.exists():
            entry["git"] = git_status(root)
            if name in SCAN_DIRS:
                hashes = tree_hashes(root, SCAN_DIRS[name])
                entry["scanned_files"] = len(hashes)
                entry["content_sha256"] = hashlib.sha256(
                    json.dumps(hashes, sort_keys=True).encode()).hexdigest()
                entry["hashes"] = hashes
        payload["trees"][name] = entry
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    before_dir = ATT / "before"
    after_dir = ATT / "after"
    before_dir.mkdir(parents=True, exist_ok=True)
    after_dir.mkdir(parents=True, exist_ok=True)
    snap_path = before_dir / "production_readonly_snapshot.json"
    verify_path = after_dir / "final_hashes.json"

    if args.snapshot:
        payload = snapshot()
        payload["purpose"] = ("production repos read-only: this snapshot is taken before the "
                             "campaign and re-verified after it (after/final_hashes.json)")
        snap_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                             encoding="utf-8")
        print(f"snapshot -> {snap_path}")
        for name, entry in payload["trees"].items():
            extra = (f" scanned={entry.get('scanned_files')} "
                     f"content={str(entry.get('content_sha256'))[:16]}"
                     if "content_sha256" in entry else "")
            print(f"  {name}: exists={entry['exists']}{extra}")
        return 0

    if args.verify:
        if not snap_path.exists():
            print("no snapshot; run --snapshot first")
            return 1
        before = json.loads(snap_path.read_text(encoding="utf-8"))
        after = snapshot()
        diffs: list[str] = []
        for name, entry_b in before["trees"].items():
            entry_a = after["trees"][name]
            if entry_b.get("content_sha256") != entry_a.get("content_sha256"):
                diffs.append(f"{name}: scanned content changed")
                hb, ha = entry_b.get("hashes", {}), entry_a.get("hashes", {})
                for key in sorted(set(hb) | set(ha)):
                    if hb.get(key) != ha.get(key):
                        diffs.append(f"  {name}/{key}: {hb.get(key)} -> {ha.get(key)}")
            if (entry_b.get("git", {}).get("head") != entry_a.get("git", {}).get("head")
                    or entry_b.get("git", {}).get("porcelain_sha256")
                    != entry_a.get("git", {}).get("porcelain_sha256")):
                diffs.append(
                    f"{name}: git state changed "
                    f"(head {entry_b.get('git', {}).get('head')} -> "
                    f"{entry_a.get('git', {}).get('head')}, "
                    f"porcelain {entry_b.get('git', {}).get('porcelain_lines')} lines -> "
                    f"{entry_a.get('git', {}).get('porcelain_lines')} lines)")
        payload = {
            "card": "I-14-E-APPLY", "attempt": "a20260921-01",
            "verified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "claim": "the production repos were not written in place by this attempt",
            "production_readonly_holds": not diffs,
            "diffs": diffs,
            "before": before,
            "after": after,
        }
        verify_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                               encoding="utf-8")
        print(f"verify -> {verify_path}")
        print(f"production_readonly_holds = {payload['production_readonly_holds']}")
        for line in diffs:
            print("  DIFF:", line)
        return 0 if not diffs else 2

    parser.error("pass --snapshot or --verify")
    return 1


if __name__ == "__main__":
    sys.exit(main())
