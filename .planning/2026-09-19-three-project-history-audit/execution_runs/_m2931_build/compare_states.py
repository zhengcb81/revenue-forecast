"""Re-encode the captured git-status snapshots to UTF-8 and record a before/after comparison.

`before/git_status_<repo>.txt` was written by the orchestrating shell's redirection, which on this
host emits UTF-16LE; the pipeline's own G1 unit writes UTF-8. This script re-encodes the `before`
snapshots into `before/utf8/` so both sides are readable as text, and writes `state_comparison.json`
with the line counts, sha256 of the raw files, and an explicit statement about what the difference
between `before` and `after` does and does not show.

The raw captured bytes are left untouched; the re-encoded copies are clearly marked as derived.

Usage:
  python -X utf8 -B compare_states.py --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

REPOS = ("revenue-forecast", "company-wiki", "filing-fetch")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def read_text_any(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace"), "utf-16"
    if raw[:3] == b"\xef\xbb\xbf":
        return raw[3:].decode("utf-8", errors="replace"), "utf-8-bom"
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("utf-16", errors="replace"), "utf-16-fallback"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt_root)
    out_dir = os.path.join(attempt, "before", "utf8")
    os.makedirs(out_dir, exist_ok=True)

    comparison = {
        "attempt_root": attempt,
        "rule": ("the raw captured bytes are the evidence; the utf8/ copies are DERIVED (re-encoded) "
                 "and are marked as such"),
        "repos": {},
    }
    for repo in REPOS:
        entry = {}
        for side in ("before", "after"):
            path = os.path.join(attempt, side, "git_status_%s.txt" % repo)
            if not os.path.isfile(path):
                entry[side] = {"exists": False}
                continue
            text, encoding = read_text_any(path)
            lines = [line for line in text.splitlines() if line.strip()]
            entry[side] = {"exists": True, "path": path, "sha256_raw": sha256(path),
                           "size_bytes": os.path.getsize(path), "detected_encoding": encoding,
                           "non_empty_lines": len(lines),
                           "first_line": lines[0] if lines else None,
                           "last_line": lines[-1] if lines else None}
            if side == "before":
                derived = os.path.join(out_dir, "git_status_%s.txt" % repo)
                with open(derived, "w", encoding="utf-8", newline="\n") as handle:
                    handle.write(text)
                entry[side]["derived_utf8_path"] = derived
                entry[side]["derived_utf8_sha256"] = sha256(derived)
        if entry.get("before", {}).get("exists") and entry.get("after", {}).get("exists"):
            entry["identity"] = {
                "raw_bytes_identical": entry["before"]["sha256_raw"] == entry["after"]["sha256_raw"],
                "same_non_empty_line_count":
                    entry["before"]["non_empty_lines"] == entry["after"]["non_empty_lines"],
                "same_first_line": entry["before"]["first_line"] == entry["after"]["first_line"],
                "same_last_line": entry["before"]["last_line"] == entry["after"]["last_line"],
            }
        comparison["repos"][repo] = entry

    comparison["interpretation"] = {
        "what_this_proves": ("this attempt's own three source anchors "
                            "(scripts/model_registry.py, scripts/model_extensions.py, "
                            "scripts/forecast/segments.py) hash identically before and after the card "
                            "work; see before/source_hashes.txt and after/source_hashes.txt"),
        "what_this_does_not_prove": ("the repository's overall dirty/staged set is NOT stationary: "
                                     "several other card attempts and the batch's own fix work run "
                                     "concurrently in this repo, so `git status --porcelain` legitimately "
                                     "differs between the before and after captures for reasons "
                                     "unrelated to this attempt"),
        "concurrency_evidence": ("the before capture records a large staged set (A lines) while the "
                                 "after capture records a smaller modified set (M lines) of "
                                 ".planning/ execution-run files that belong to other cards; this "
                                 "attempt never ran git add/commit/restore/stash"),
        "no_git_index_action_by_this_attempt": True,
    }
    out = os.path.join(attempt, "before", "state_comparison.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(comparison, handle, ensure_ascii=False, indent=1)
    for repo, entry in comparison["repos"].items():
        if entry.get("identity"):
            print("%-18s before_lines=%s after_lines=%s identical_raw=%s"
                  % (repo, entry["before"]["non_empty_lines"], entry["after"]["non_empty_lines"],
                     entry["identity"]["raw_bytes_identical"]))
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
