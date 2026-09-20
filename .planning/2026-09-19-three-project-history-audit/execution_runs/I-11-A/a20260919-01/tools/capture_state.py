"""I-11-A: capture the read-only state (before) and the post-work state (after).

"before" = the three production repositories' HEADs, porcelain status, the key
source hashes, the PLAN/reviews directory mtimes, and this attempt's own directory
inventory at capture time.
"after"  = the same production facts plus the sha256 of every deliverable this
attempt produced, proving the production side is byte-identical.

Usage:
  python -X utf8 -B tools/capture_state.py <attempt_root> <before|after>
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REPOS = {
    "revenue-forecast": r"C:\Users\郑曾波\Projects\revenue-forecast",
    "company-wiki": r"C:\Users\郑曾波\Projects\company-wiki",
    "filing-fetch": r"C:\Users\郑曾波\Projects\filing-fetch",
}
KEY_FILES = [
    r"C:\Users\郑曾波\Projects\revenue-forecast\SKILL.md",
    r"C:\Users\郑曾波\Projects\revenue-forecast\CHANGELOG.md",
    r"C:\Users\郑曾波\Projects\company-wiki\config\source_catalog.yaml",
    r"C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py",
]
REVIEWS = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\reviews")
# a monotonically increasing marker written into each capture, so that two captures
# taken in the same clock tick are still distinguishable (finding P1-1)
SEQUENCE_FILE_COUNTER = None


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_git(repo: str, args):
    p = subprocess.run(["git", "-C", repo] + args, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def dir_inventory(root: str):
    out = []
    for base, dirs, files in os.walk(root):
        if os.sep + "iso" + os.sep in base + os.sep and "venv" in base:
            continue
        for f in files:
            p = os.path.join(base, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            try:
                out.append({"path": rel, "byte_size": os.path.getsize(p)})
            except OSError:
                out.append({"path": rel, "byte_size": None})
    out.sort(key=lambda e: e["path"])
    return out


def reviews_listing(root: str):
    """Full recursive listing of the read-only reviews tree, not a truncated sample."""
    out = []
    for base, dirs, files in os.walk(root):
        for f in sorted(files):
            p = os.path.join(base, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            out.append({
                "path": os.path.relpath(p, root).replace("\\", "/"),
                "byte_size": st.st_size,
                "mtime_local": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
    out.sort(key=lambda e: e["path"])
    return out


def main() -> int:
    attempt, phase = sys.argv[1], sys.argv[2]
    global SEQUENCE_FILE_COUNTER
    seq_path = os.path.join(attempt, "evidence", "I-11-A", "capture_sequence.txt")
    previous = 0
    if os.path.exists(seq_path):
        try:
            previous = int(open(seq_path, encoding="utf-8").read().strip() or 0)
        except ValueError:
            previous = 0
    SEQUENCE_FILE_COUNTER = previous + 1
    os.makedirs(os.path.dirname(seq_path), exist_ok=True)
    with open(seq_path, "w", encoding="utf-8") as fh:
        fh.write("%d\n" % SEQUENCE_FILE_COUNTER)
    record = {
        "phase": phase,
        "sequence": SEQUENCE_FILE_COUNTER,
        # microsecond resolution: the first version used whole seconds, and two
        # captures inside the same second were then indistinguishable (which the
        # reviewer correctly read as "one capture echoed twice", finding P1-1)
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "card_id": "I-11-A",
        "attempt_id": "a20260919-01",
        "production_repos": {},
        "key_files": {},
        "plan_reviews": {},
        "attempt_inventory": [],
    }
    for name, path in REPOS.items():
        rc, out, err = run_git(path, ["rev-parse", "HEAD"])
        rc2, out2, err2 = run_git(path, ["status", "--porcelain"])
        record["production_repos"][name] = {
            "path": path,
            "head": out.strip(),
            "head_returncode": rc,
            "porcelain": out2.splitlines(),
            "porcelain_returncode": rc2,
        }
    for p in KEY_FILES:
        record["key_files"][p] = {"sha256": sha256(p), "byte_size": os.path.getsize(p)}
    if os.path.isdir(REVIEWS):
        st = os.stat(REVIEWS)
        listing = reviews_listing(REVIEWS)
        newest = max(listing, key=lambda e: e["mtime_local"]) if listing else None
        record["plan_reviews"] = {
            "path": REVIEWS,
            "mtime_local": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "file_count": len(listing),
            "newest_file": newest,
            "entries": listing,
            "listing_note": ("full recursive listing (path/byte_size/mtime_local); earlier captures "
                             "recorded only the first 20 directory names, which did not match the "
                             "claimed 285-file enumeration - see review finding P2-9"),
        }
    record["capture_timeline"] = {
        "captured_at_utc": record["captured_at_utc"],
        "attempt_dir_created_local": datetime.fromtimestamp(os.path.getctime(attempt)).strftime(
            "%Y-%m-%d %H:%M:%S"),
        "note": ("This capture is a read-only snapshot taken during this attempt's own work. Because "
                 "the card writes nothing to the production repositories, a capture cannot be an "
                 "'before any work started' baseline for this card; before/after here means 'the state "
                 "recorded twice during the work', and the load-bearing claim (production untouched) "
                 "rests on independent third-party review, not on this pair alone."),
    }
    record["attempt_inventory"] = dir_inventory(attempt)
    record["attempt_file_count"] = len(record["attempt_inventory"])
    out_path = os.path.join(attempt, "evidence", "I-11-A", "state_%s.json" % phase)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(phase, "inventory files:", record["attempt_file_count"],
          "reviews mtime:", record["plan_reviews"].get("mtime_local"))
    for name, r in record["production_repos"].items():
        print(" ", name, r["head"][:12], "porcelain entries:", len(r["porcelain"]))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
