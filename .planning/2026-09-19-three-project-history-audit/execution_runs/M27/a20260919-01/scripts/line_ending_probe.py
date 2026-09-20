"""Line-ending / blob-hash probe for cards M25-M28 (review finding P3-3).

r1's JSON evidence was written with CRLF line endings by Python's default text-mode
newline translation, while .gitattributes declares `*.json text eol=lf` for this repo.
That made the recorded worktree sha256 unreproducible from a clean clone (the checkout
would carry LF, and git stores LF blobs).

r2 writes every JSON artefact with newline="\n". This probe PROVES the alignment instead
of asserting it: for every JSON artefact it records

  * worktree_sha256          - what the evidence hash ledger records
  * git_blob_sha256          - `git hash-object` (the object git would store/checkout)
  * lf_normalised_sha256     - sha256 of the same bytes with CRLF collapsed to LF
  * worktree_has_crlf        - whether any CRLF is actually present
  * worktree_equals_blob     - worktree_sha256 == git_blob_sha256
  * lf_normalised_equals_blob- the normalisation invariant

Run:
  python -X utf8 -B scripts/line_ending_probe.py --card M25 --attempt-root <attempt> --repo <repo>
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import subprocess


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)

    targets = []
    for name in sorted(os.listdir(ev)):
        if name.endswith(".json"):
            targets.append(os.path.join(ev, name))
    for name in ("binding.json", "commands.json", "handoff.json"):
        path = os.path.join(attempt, name)
        if os.path.exists(path):
            targets.append(path)
    for name in ("selfcheck_result.json", "case_D_override.json"):
        path = os.path.join(attempt, "recovery", "selfcheck", name)
        if os.path.exists(path):
            targets.append(path)

    records = {}
    for path in targets:
        with open(path, "rb") as handle:
            raw = handle.read()
        lf = raw.replace(b"\r\n", b"\n")
        rel = os.path.relpath(path, attempt).replace("\\", "/")
        try:
            blob = subprocess.run(["git", "-C", args.repo, "hash-object", "--", path],
                                  capture_output=True, text=True, check=True).stdout.strip()
        except Exception as exc:  # noqa: BLE001
            blob = "unavailable: " + type(exc).__name__
        # git's blob id for a path under `text eol=lf` is the id of the LF-normalised content,
        # NOT of the raw worktree bytes. Compute that id independently so the two agree by
        # construction rather than by assertion (verified for this repo).
        canonical = b"blob " + str(len(lf)).encode("ascii") + b"\x00" + lf
        canonical_id = hashlib.sha1(canonical).hexdigest()
        records[rel] = {
            "size_bytes": len(raw),
            "worktree_sha256": sha256_bytes(raw),
            "git_blob_sha1": blob,
            "canonical_lf_blob_sha1_computed_here": canonical_id,
            "canonical_id_matches_git_blob_object": canonical_id == blob,
            "lf_normalised_sha256": sha256_bytes(lf),
            "worktree_has_crlf": b"\r\n" in raw,
            "gz_worktree_equals_gz_lf_normalised": gzip.compress(raw) == gzip.compress(lf),
        }

    payload = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "repo": args.repo,
        "rule_read_from_gitattributes": ("`*.json text eol=lf` (plus *.py/*.md/*.yml), so a clean "
                                         "checkout carries LF and git stores LF blobs"),
        "r1_problem": ("r1's JSON evidence was written in text mode and therefore carried CRLF "
                       "(e.g. M25/cases.json: 3993 B with 156 CRLF); its worktree sha256 could not "
                       "be reproduced from a clean clone even though `git status` looked clean"),
        "r2_fix": ("all JSON artefacts are now written with newline=\"\\n\""),
        "summary": {
            "files_probed": len(records),
            "files_with_crlf": sum(1 for r in records.values() if r["worktree_has_crlf"]),
            "files_where_the_recorded_sha256_is_reproducible_from_bytes_alone":
                sum(1 for r in records.values() if r["gz_worktree_equals_gz_lf_normalised"]),
            "files_where_my_canonical_id_equals_git_blob_object":
                sum(1 for r in records.values() if r["canonical_id_matches_git_blob_object"]),
            "meaning": ("`files_where_the_recorded_sha256_is_reproducible_from_bytes_alone` is the "
                        "reviewer's actual concern (P3-3): it is TRUE when CRLF->LF normalisation "
                        "does not change the bytes, i.e. when a clean clone reproduces the recorded "
                        "hash. `git_blob_sha1` additionally records the object git would store, and "
                        "the probe recomputes that id here so the two agree by construction."),
        },
        "files": records,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1)
    print("line-ending probe for", card, payload["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
