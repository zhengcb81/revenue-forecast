"""Deterministic assembly of review.md = (r2 base recovered from git) + (reviewer block).

Why this exists
---------------
`review.md` is APPEND-ONLY from the r2 acceptance onward. The doc generator
(`write_docs.py`) used to rewrite it, which truncated the reviewer block; it now writes the base
to `review_base.md` instead and leaves `review.md` alone. To keep the append PROVABLE and
REPRODUCIBLE, this script rebuilds `review.md` from a byte-exact base:

  * M25's base is still on disk and still hashes to the reviewer's declared prefix;
  * the other three bases were overwritten once by the doc generator, but they are recoverable
    byte-exactly from git (the plan commit that contains the r2 state). Each recovered base is
    VERIFIED against the reviewer's declared prefix hash before anything is written.

The block itself is produced by the same code path as `apply_review_r3.py` (imported), so the
bytes are identical to the original append. Nothing frozen is touched.

Run:
  python -X utf8 -B scripts/reassemble_review.py --card M26 --attempt-root <attempt> --repo <repo>
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

PLAN_REL = ".planning/2026-09-19-three-project-history-audit/execution_runs/%s/a20260919-01/review.md"


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def load_apply_module(attempt):
    path = os.path.join(attempt, "scripts", "apply_review_r3.py")
    spec = importlib.util.spec_from_file_location("apply_review_r3_loaded", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    review_path = os.path.join(attempt, "review.md")
    base_path = os.path.join(attempt, "review_base.md")

    module = load_apply_module(attempt)
    fill = module.FILL[card]
    block = module.BLOCK_TEMPLATE
    for key, value in (
        ("<CARD>", card), ("<MODEL>", fill["model"]),
        ("<EXPECTED_GUARD_MESSAGE>", fill["expected_guard_message"]),
        ("<POSITIVE>", fill["positive"]), ("<CONTINUITY>", fill["continuity"]),
        ("<DEFAULTS>", fill["defaults"]), ("<DEFAULTS_NOTE>", fill["defaults_note"]),
        ("<IN_SHA>", fill["in_sha"]), ("<OR_SHA>", fill["or_sha"]),
        ("<CASES_SHA>", fill["cases_sha"]), ("<RR_SHA>", fill["rr_sha"]),
        ("<PREFIX_SHA>", fill["prefix_sha"]), ("<PREFIX_SIZE>", str(fill["prefix_size"])),
    ):
        block = block.replace(key, value)
    append_bytes = block.encode("utf-8")
    append_sha = sha256_bytes(append_bytes)

    # 1. prefer an on-disk base that matches the declared prefix
    base_source = None
    base_bytes = None
    if os.path.exists(base_path):
        with open(base_path, "rb") as handle:
            candidate = handle.read()
        if sha256_bytes(candidate) == fill["prefix_sha"] and len(candidate) == fill["prefix_size"]:
            base_bytes = candidate
            base_source = "review_base.md on disk"

    # 2. otherwise recover the base byte-exactly from git
    if base_bytes is None:
        rel = PLAN_REL % card
        recovered = subprocess.run(["git", "-C", args.repo, "cat-file", "-p", "HEAD:" + rel],
                                   capture_output=True, check=True).stdout
        if sha256_bytes(recovered) != fill["prefix_sha"] or \
                len(recovered) != fill["prefix_size"]:
            print("REFUSING: the git-recovered base does not match the reviewer's declared prefix")
            print("  declared", fill["prefix_sha"], fill["prefix_size"], "B")
            print("  recovered", sha256_bytes(recovered), len(recovered), "B")
            return 1
        base_bytes = recovered
        base_source = "git HEAD:%s" % rel

    # 3. verify the CURRENT on-disk review.md is either the base or base+block (no third state)
    with open(review_path, "rb") as handle:
        current = handle.read()
    if current == base_bytes:
        current_state = "base-only (append missing)"
    elif current == base_bytes + append_bytes:
        current_state = "base+block (already assembled correctly)"
    else:
        current_state = "OTHER (will be replaced by the canonical base+block)"

    canonical = base_bytes + append_bytes
    canonical_sha = sha256_bytes(canonical)
    prefix_ok = canonical.startswith(base_bytes)

    with open(review_path, "wb") as handle:
        handle.write(canonical)

    print("reassembled review.md for", card)
    print("  base source:", base_source, "| base sha256 =", fill["prefix_sha"],
          "| size", len(base_bytes), "B")
    print("  state before this run:", current_state)
    print("  block bytes sha256 =", append_sha, "| block size", len(append_bytes))
    print("  review.md now =", canonical_sha, "| size", len(canonical), "B")
    print("  canonical has the base as an exact prefix:", prefix_ok)
    start_line = base_bytes.count(b"\n") + 1
    end_line = canonical.count(b"\n") + (0 if canonical.endswith(b"\n") else 1)

    import json
    record_path = os.path.join(attempt, "evidence", card, "append_record_r3.json")
    with open(record_path, "r", encoding="utf-8") as handle:
        record = json.load(handle)
    record["reassembly_r3"] = {
        "why": ("the doc generator once rewrote review.md and truncated the reviewer block; the "
                "base was recovered byte-exactly and the append replayed deterministically"),
        "base_source": base_source,
        "base_sha256": fill["prefix_sha"],
        "base_size_bytes": len(base_bytes),
        "block_sha256": append_sha,
        "block_size_bytes": len(append_bytes),
        "review_md_sha256_after_reassembly": canonical_sha,
        "review_md_size_bytes_after_reassembly": len(canonical),
        "state_of_review_md_before_reassembly": current_state,
        "canonical_has_base_as_exact_prefix": prefix_ok,
        "appended_block_lines": [start_line, end_line],
        "generator_fix": ("write_docs.py now writes the base to review_base.md ONLY and leaves "
                          "review.md alone; review.md is assembled by apply_review_r3.py / this "
                          "script, so the append cannot be truncated again"),
        "frozen_artefacts_touched": False,
    }
    with open(record_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)
    print("  append_record_r3.json updated with reassembly_r3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
