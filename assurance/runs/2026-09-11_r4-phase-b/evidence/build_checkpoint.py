"""Regenerate checkpoint.json for the R4 phase-B run directory.

Same rationale as the phase-A generator: A-DR-09 found hand-written checkpoints
drift from the other ledgers, so the produced-file hashes are computed here and
merged with an explicit ledger block. The byte-stability policy of
`../2026-09-11_r4-phase-a/.gitattributes` does NOT apply to this directory: each run
directory carries its own `.gitattributes` (see the one next to this file).

Usage:  python evidence/build_checkpoint.py [--reviewed-commit <sha>|--verify-only]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path.home() / "Projects" / "revenue-forecast"
WIKI = Path.home() / "Projects" / "company-wiki"
FILING = Path.home() / "Projects" / "filing-fetch"

EXCLUDE_NAMES = {"checkpoint.json"}  # self-hash is circular; disclosed in `exclusions` below
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def head(repo: Path) -> str:
    return subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True).stdout.strip()


def dirty(repo: Path) -> int:
    out = subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True).stdout
    return len([line for line in out.splitlines() if line.strip()])


def produced_files() -> dict:
    files: dict[str, dict] = {}
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(RUN)
        if rel.name in EXCLUDE_NAMES or any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        files[rel.as_posix()] = {"sha256": sha256(path), "size": path.stat().st_size}
    return files


def verify_blobs(files: dict, source: str = "index", revision: str | None = None) -> dict:
    """Compare each recorded digest with the blob stored for that path.

    Hardened after B-DR3-05 (the earlier version could pass vacuously):
      * when `revision` is given the comparison is made against THAT commit
        (`git show <rev>:<path>`), and a revision that does not resolve is an error -
        this is what actually binds `reviewed_commit`;
      * without it the caller gets index/HEAD behaviour and the result says which
        revision was compared.
    """
    run_rel = RUN.relative_to(REVENUE).as_posix()
    head_rev = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                               "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    tree = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE), "write-tree"],
                          capture_output=True, text=True).stdout.strip()
    if revision:
        ok = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                             "rev-parse", "--verify", f"{revision}^{{commit}}"],
                            capture_output=True, text=True)
        if ok.returncode != 0:
            return {"checked": 0, "source": f"commit:{revision}", "all_match": False,
                    "error": f"reviewed_commit {revision!r} does not resolve to a commit",
                    "blob_mismatches": []}
        spec_prefix, compared = revision, ok.stdout.strip()
    else:
        spec_prefix = None
        compared = tree if source == "index" else head_rev
    mismatched = []
    for rel, meta in files.items():
        spec = (f"{spec_prefix}:{run_rel}/{rel}" if spec_prefix
                else (f":{run_rel}/{rel}" if source == "index" else f"HEAD:{run_rel}/{rel}"))
        proc = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                               "show", spec], capture_output=True)
        if proc.returncode != 0:
            mismatched.append({"path": rel, "reason": "not in the compared revision",
                               "detail": proc.stderr.decode(errors="replace").strip()[:120]})
            continue
        if hashlib.sha256(proc.stdout).hexdigest() != meta["sha256"]:
            mismatched.append({"path": rel, "reason": "stored digest != recorded digest",
                               "blob_bytes": len(proc.stdout), "recorded_bytes": meta["size"]})
    return {
        "checked": len(files), "source": f"commit:{revision}" if revision else source,
        "compared_revision": compared, "head_revision": head_rev, "index_tree": tree,
        "blob_mismatches": mismatched, "all_match": not mismatched,
        "proves": "recorded digest == stored blob at the reported revision",
        "does_not_prove": ["manifest completeness (see the completeness block)",
                           "that the working tree equals the compared revision"],
    }


def completeness(files: dict) -> dict:
    """Assert that the manifest lists EVERY file in the run directory (B-DR2-09).

    Without this, a stale or partial manifest still "verifies" because verification only
    walks the manifest, never the directory.
    """
    on_disk = set()
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(RUN)
        if rel.name in EXCLUDE_NAMES or any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        on_disk.add(rel.as_posix())
    listed = set(files)
    return {
        "files_on_disk": len(on_disk),
        "files_listed": len(listed),
        "unlisted": sorted(on_disk - listed),
        "phantom": sorted(listed - on_disk),
        "excluded_by_design": sorted(EXCLUDE_NAMES),
        "note": ("files_on_disk counts manifest-eligible files; checkpoint.json is excluded because a "
                 "file cannot hash itself. This is a same-process comparison, so it cannot detect a file "
                 "created after generation - --verify-only re-runs it, and that is where a late file shows "
                 "up as `unlisted` (exactly what happened when B.DR-rev3 wrote its record)."),
        "complete": on_disk == listed,
    }


def commit_anchor() -> dict:
    head = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                           "rev-parse", "HEAD"], capture_output=True, text=True)
    tree = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                           "write-tree"], capture_output=True, text=True)
    return {"head": head.stdout.strip() or "unknown",
            "index_tree": tree.stdout.strip() or "unknown",
            "note": ("anchor for the tree this checkpoint was generated from; the commit that "
                     "publishes this file does not exist yet (that is what reviewed_commit names)")}


LEDGER = {
    "run_id": "2026-09-11_r4-phase-b",
    "phase": "B (position-transparent index and read-only access) - DESIGN ONLY",
    "step": "B design v0.1.5 - four B.DR rounds corrected in place; S-1..S-6 decided by the owner, S-7 raised",
    "last_completed_step": (
        "B run directory created; b-design v0.1 (B01-B07) submitted to B.DR; B.DR returned "
        "rejected with 1 P0 + 7 P1 + 9 P2 + 3 P3 (8 of 17 claims did not reproduce); phase-A "
        "A07 returned accepted_with_findings and A08 rejected; all twenty B findings and the "
        "phase-A findings corrected in place (A contracts -> v0.4.1, B design -> v0.1.1)"
    ),
    "current_gate": (
        "S-1..S-6 are decided (owner 2026-09-12); S-7 (may the complexity ratchet table be edited if a "
        "step cannot stay complexity-neutral?) is the only open boundary question. Implementation itself "
        "still awaits the owner's go-ahead (handbook section 1 item 5)."
    ),
    "pending_review": [
        {
            "gate": "B.DR rev5",
            "scope": "B design v0.1.5",
            "status": "pending",
            "reviewer": "independent subagent (non-author) - must differ from rev1-rev4 sessions",
        },
        {
            "gate": "B.DR rev4",
            "scope": "B design v0.1.4",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 2, "P2": 6, "P3": 3},
            "note": "reviewer stated the defects are text/landing level and one editing pass converges them; no architectural rework required",
            "record": "reviews/B.DR-rev4.json",
            "reviewer_self_reported_id": "1f962189-34f4-45aa-bd5c-2418ffa048bc",
        },
        {
            "gate": "B.DR rev3",
            "scope": "B design v0.1.2",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 3, "P2": 7, "P3": 1},
            "round1_closure": "14 of 20 closed",
            "round2_closure": "6 of 15 closed",
            "record": "reviews/B.DR-rev3.json",
            "reviewer_self_reported_id": "ba59c7cd-f239-4b80-954f-b42a0002198d",
        },
        {
            "gate": "B.DR rev2",
            "scope": "B design v0.1.1",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 3, "P2": 9, "P3": 3},
            "round1_closure": "7 of 20 closed",
            "record": "reviews/B.DR-rev2.json",
            "reviewer_self_reported_id": "92aeb4c7-6cb2-4410-bbc0-849c1ce641b6",
        },
        {
            "gate": "B.DR rev1",
            "scope": "B design v0.1",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P0": 1, "P1": 7, "P2": 9, "P3": 3},
            "record": "reviews/B.DR.json",
            "reviewer_self_reported_id": "7ad6f0f0-717a-4b25-a1bf-b3604b8953fe",
        },
    ],
    "reviewer_assignments": {
        "note": ("recorded by the authoring session from outside the reviewer session; still only "
                 "process evidence - an operator-held assignment record is required (gate G6)"),
        "B.DR_rev1": {"reviewer_session_id": "7ad6f0f0-717a-4b25-a1bf-b3604b8953fe", "record": "reviews/B.DR.json"},
    },
    "authorization_needed": [
        "OWNER: approve the B DEV work package and file scope (file-scope.md) before any product file is touched - handbook section 1 item 5",
        "OWNER: confirm the A05 sample list and the read-only command manifest (gate G7 + G4 for behaviour beyond --help)",
        "OWNER/OPERATOR: isolated copy for behavioural probes (gate G8) - see findings F-B00-3 for a two-level proposal",
        "OPERATOR: independent boundary observation and reviewer assignment records (G5/G6)",
    ],
    "gate_status": {
        "B.DR": "rev1/rev2/rev3/rev4 all rejected; v0.1.5 is the single-pass convergence of rev4's 11 findings (text and landing defects; the reviewer stated no architectural rework is needed)",
        "B.VR": "protocol ready (b-vr-protocol.md); L1 mechanism layer unblocked by S-5, L2 real-byte layer still needs G8",
        "B.AR": "not started",
        "S-1_test_files": "APPROVED (F10/F11)",
        "S-2_R1_R4_out_of_B": "DECIDED - R-1/R-4 stay outside B as separate work packages",
        "S-3_export_path": "DECIDED - export_policy_2x untouched, payload hash frozen",
        "S-4_consumer_side": "DECIDED - belongs to phase C, B does not sign it",
        "S-5_isolated_copy": "DECIDED - two levels; L1 can start now",
        "S-6_fourth_round": "done (rev4) - a fifth round is now suggested by that reviewer",
        "S-7_ratchet_edit": "OPEN - see b-design section B0x",
        "implementation_go_ahead": "NOT GRANTED - handbook section 1 item 5",
    },
    "actual_side_effects": (
        "This run: documentation and read-only inspection only - no CLI of any kind was executed here, no "
        "data command, no network, no product/config/DB/task/worker change. ACTUAL, not future tense "
        "(B-DR3-11/B-DR4-04): the run directory HAS been pushed - origin/main = 910c957 at review time - "
        "and every push ran revenue-forecast's mandatory pre-push gate, whose real-data suite opens the "
        "production catalog READ-ONLY and advances -shm (attributed in ../2026-09-11_r4-phase-a/"
        "boundary-audit.md). The A06-D0 baseline run (pytest, CI-equivalent subset) also opened the "
        "production catalog read-only at 08:11:45 and 08:13:46 on 2026-09-12. Main DB and -wal are never "
        "changed. An independent observation artefact for 'no CLI executed' still does not exist (G5)."
    ),
    "failed_or_unknown": [
        "S-7 is open: if a step cannot stay complexity-neutral, editing the ratchet table would conflict with F10 (new files only)",
        "the L01-L12 mechanism-layer baseline exists as A06-D0 (787 unit + 1748 contract passed / 7 skipped), but no B-side run has happened yet - implementation is not authorized",
        "B05's provenance shape is now additive under a reserved key, but the json_extract regression assertion can only be proved when the tests run (needs implementation)",
        "N-1 support is undefined on both sides and is therefore registered as a cross-repo protocol item, no longer part of B07's completion",
        "handbook section 3 run structure is still partial: card.json, baseline.json, data-manifest.json, requirements.csv and oracle/ are absent",
        "G5/G6/G7/G8 remain owner/operator items",
        "revenue-forecast dirty=0 is incomplete: three .tmp-zr408-unit* directories are unreadable (permission denied), so git cannot enumerate them",
    ],
    "next_step": (
        "Send v0.1.5 to B.DR rev5 (fresh session). S-7 is the only open boundary question; implementation "
        "still awaits the owner's go-ahead, after which the suggested order is B02 -> B04 -> B05 -> B01 "
        "-> B03 -> B06 -> B07, each step with its own commit, ratchet run and review."
    ),
    "inputs": {
        "note": ("phase A froze the product inputs at wiki 7d4852f; the phase-A run directory "
                 "records the twelve hashes and the drift of the two planning-ledger commits"),
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewed-commit", default=None,
                        help="REQUIRED to write: the commit carrying the reviewed corrections "
                             "(B-DR2-09 made this mandatory instead of a PENDING placeholder)")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)

    if args.verify_only:
        existing = json.loads((RUN / "checkpoint.json").read_text(encoding="utf-8"))
        result = verify_blobs(existing["produced_files"], source="head",
                              revision=existing.get("reviewed_commit"))
        result["completeness"] = completeness(existing["produced_files"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        ok = (result["all_match"] and result["completeness"]["complete"]
              and "error" not in result)
        return 0 if ok else 1

    if not args.reviewed_commit:
        print("ERROR: --reviewed-commit is required (B-DR2-09/B-DR3-05).")
        return 2
    resolved = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                               "rev-parse", "--verify", f"{args.reviewed_commit}^{{commit}}"],
                              capture_output=True, text=True)
    if resolved.returncode != 0:
        print(f"ERROR: --reviewed-commit {args.reviewed_commit!r} is not an existing commit "
              f"(B-DR3-05: the stamp must name a real revision).")
        return 2

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = resolved.stdout.strip()
    ledger["commit_anchor"] = commit_anchor()
    ledger["produced_files"] = produced_files()
    ledger["produced_files_verification"] = verify_blobs(ledger["produced_files"], source="index")
    ledger["produced_files_completeness"] = completeness(ledger["produced_files"])
    ledger["generated_at_utc"] = datetime.now(UTC).isoformat()
    if not ledger["produced_files_completeness"]["complete"]:
        print("ERROR: manifest is not complete (B-DR3-05/B-DR4-05): "
              f"unlisted={ledger['produced_files_completeness']['unlisted']}")
        return 3
    if not ledger["produced_files_verification"]["all_match"]:
        print("ERROR: staged blobs do not match the recorded digests (B-DR4-05: the write path now "
              "asserts this instead of writing regardless): "
              f"{ledger['produced_files_verification']['blob_mismatches'][:3]}")
        return 4
    out = RUN / "checkpoint.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(ledger['produced_files'])} files; "
          f"blob all_match={ledger['produced_files_verification']['all_match']}; "
          f"complete={ledger['produced_files_completeness']['complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
