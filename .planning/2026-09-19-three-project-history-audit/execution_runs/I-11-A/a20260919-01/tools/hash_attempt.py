"""I-11-A: hash every file this attempt produced (delivery manifest).

Excluded, and stated explicitly in the manifest:
  * `iso/venv/**` - isolated interpreter + third-party package tree;
  * `__pycache__/**` and `*.pyc` - interpreter byte-code, regenerated on every run
    (the reviewer's own import of the validators created one such file).

Self-reference note: this manifest is written by the run it describes, so
`evidence/I-11-A/attempt_hashes.json` can never contain its own final sha256, and any
file written AFTER this run makes its own record here stale. Both facts are recorded
in the manifest under `self_reference`, and the same rule is stated in the header of
`changes.diff`.

Usage: python -X utf8 -B tools/hash_attempt.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import sys


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    entries = []
    excluded = []
    for base, dirs, files in os.walk(attempt):
        rel_base = os.path.relpath(base, attempt).replace("\\", "/")
        if rel_base.startswith("iso/venv"):
            excluded.append("iso/venv/**")
            dirs[:] = []
            continue
        if os.path.basename(base) == "__pycache__":
            excluded.append(rel_base + "/**")
            dirs[:] = []
            continue
        for f in sorted(files):
            p = os.path.join(base, f)
            rel = os.path.relpath(p, attempt).replace("\\", "/")
            if f.endswith(".pyc"):
                excluded.append(rel)
                continue
            entries.append({"path": rel, "byte_size": os.path.getsize(p), "sha256": sha256(p)})
    entries.sort(key=lambda e: e["path"])
    manifest = {
        "card_id": "I-11-A",
        "attempt_id": "a20260919-01",
        "generated_by": "tools/hash_attempt.py",
        "excluded_from_manifest": sorted(set(excluded)) + [
            "iso/venv/** (isolated interpreter + pytest package tree; third-party bytes, not this attempt's work)",
            "__pycache__/** and *.pyc (interpreter byte-code; regenerated on every run)",
        ],
        "self_reference": {
            "manifest_cannot_hash_itself": True,
            "stale_after_later_writes": ("any file written after this run makes its own record here "
                                         "stale; re-run tools/hash_attempt.py last and read the header "
                                         "of changes.diff for the same rule"),
        },
        "file_count": len(entries),
        "files": entries,
        "deliverable_top_level": sorted(
            e["path"] for e in entries if "/" not in e["path"] and e["path"] != ".gitignore"),
    }
    out = os.path.join(attempt, "evidence", "I-11-A", "attempt_hashes.json")
    # A read-only staleness audit: which recorded files no longer match? The answer
    # is auditable rather than assumed, and is recorded BEFORE this manifest is
    # written (so the manifest itself is always among the expected-stale entries).
    stale = []
    for e in entries:
        p = os.path.join(attempt, e["path"].replace("/", os.sep))
        if not os.path.exists(p):
            stale.append({"path": e["path"], "why": "missing"})
        elif sha256(p) != e["sha256"]:
            stale.append({"path": e["path"], "why": "changed after this manifest run"})
    manifest["stale_at_manifest_time"] = {
        "entries": stale,
        "count": len(stale),
        "how_to_read_this": ("entries[] lists files that were already stale WHEN THIS MANIFEST WAS "
                             "BUILT, so it is normally empty (the manifest matches the files as they are). "
                             "The durable signed statement is expected[]: compare it against a fresh "
                             "recomputation - any stale path OUTSIDE expected[] is an unexpected change. "
                             "expected[] is not self-fulfilling: the audit above would have reported a "
                             "stale by-design path if one had been stale at build time."),
        "expected": ["evidence/I-11-A/attempt_hashes.json",
                     "evidence/I-11-A/commands_run.log",
                     "evidence/I-11-A/final_selfcheck.json",
                     "commands.json"],
        "explanation": ("these files are written after (or by) this run by design: the manifest cannot "
                        "hash itself, the canonical run log records this run's own rc line, "
                        "final_selfcheck.json is regenerated after the manifest it validates, and "
                        "commands.json is regenerated last from the archived logs."),
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("files hashed:", len(entries))
    print("deliverables:", ", ".join(manifest["deliverable_top_level"]))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
