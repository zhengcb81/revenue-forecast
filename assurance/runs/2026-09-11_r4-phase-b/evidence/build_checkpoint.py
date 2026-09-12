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

EXCLUDE_NAMES = {"checkpoint.json"}
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


def verify_blobs(files: dict, source: str = "index") -> dict:
    """Compare each recorded digest with the stored blob, and say what that proves.

    B-DR-16: `--verify-only` anchors the RUNTIME revision (index or HEAD) and cannot bind
    `reviewed_commit`; it also cannot prove the manifest is complete. Both limits are
    reported in the result instead of being left implicit, and the compared revision is
    echoed back so a reader can tell which tree was checked.
    """
    run_rel = RUN.relative_to(REVENUE).as_posix()
    tree = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE), "write-tree"],
                          capture_output=True, text=True)
    head_rev = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                               "rev-parse", "HEAD"], capture_output=True, text=True)
    revision = (tree.stdout.strip() if source == "index" else head_rev.stdout.strip()) or "unknown"
    mismatched = []
    for rel, meta in files.items():
        spec = f":{run_rel}/{rel}" if source == "index" else f"HEAD:{run_rel}/{rel}"
        proc = subprocess.run(
            ["git", "-c", "safe.directory=*", "-C", str(REVENUE), "show", spec],
            capture_output=True)
        if proc.returncode != 0:
            mismatched.append({"path": rel, "reason": f"not in {source}",
                               "detail": proc.stderr.decode(errors="replace").strip()[:120]})
            continue
        if hashlib.sha256(proc.stdout).hexdigest() != meta["sha256"]:
            mismatched.append({"path": rel, "reason": f"{source} digest != recorded digest",
                               "blob_bytes": len(proc.stdout), "recorded_bytes": meta["size"]})
    return {
        "checked": len(files), "source": source, "source_revision": revision,
        "head_revision": head_rev.stdout.strip() or "unknown",
        "blob_mismatches": mismatched, "all_match": not mismatched,
        "proves": "recorded digest == stored blob at the reported revision",
        "does_not_prove": ["manifest completeness",
                           "that reviewed_commit equals the compared revision"],
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
    "step": "B design v0.1.1 corrections applied after B.DR rev1 = rejected",
    "last_completed_step": (
        "B run directory created; b-design v0.1 (B01-B07) submitted to B.DR; B.DR returned "
        "rejected with 1 P0 + 7 P1 + 9 P2 + 3 P3 (8 of 17 claims did not reproduce); phase-A "
        "A07 returned accepted_with_findings and A08 rejected; all twenty B findings and the "
        "phase-A findings corrected in place (A contracts -> v0.4.1, B design -> v0.1.1)"
    ),
    "current_gate": "B.DR rev2 (re-review of the corrected design on a new frozen commit)",
    "pending_review": [
        {
            "gate": "B.DR rev2",
            "scope": "B phase design package v0.1.1",
            "status": "pending",
            "reviewer": "independent subagent (non-author) - must be a different session from rev1",
        },
        {
            "gate": "B.DR rev1",
            "scope": "B phase design package v0.1",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P0": 1, "P1": 7, "P2": 9, "P3": 3},
            "claims_not_reproduced": 8,
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
        "B.DR": "submitted (independent design review)",
        "B.VR": "blocked: needs the isolated environment (G8)",
        "B.AR": "blocked: needs G8 + the confirmed real-corpus sample list (G7)",
        "A07_A08": "not started (phase-A VR/AR of the contracts and baseline)",
        "D_SAFE_cross": "not started; B only aligns with it (no delete/write paths touched)",
    },
    "actual_side_effects": (
        "This run: documentation and read-only inspection only - no CLI of any kind was executed "
        "in this run, no data command, no network, no product/config/DB/task/worker change. "
        "DISCLOSED rather than asserted (B-DR-17): 'no CLI executed' is an author statement with "
        "no independent observation artefact behind it; pushing this run directory triggers "
        "revenue-forecast's mandatory pre-push gate, whose real-data suite opens the production "
        "catalog READ-ONLY and advances -shm (attributed in "
        "../2026-09-11_r4-phase-a/boundary-audit.md). Main DB and -wal are never changed."
    ),
    "failed_or_unknown": [
        "no B step can be marked implemented: implementation needs the owner-approved DEV work package (handbook section 1 item 5 + section 3)",
        "B08/B09 need the isolated copy (G8) and the confirmed sample list (G7)",
        "the L01-L12 mechanism-layer baseline (A06) does not exist yet, so 'B fixed it' cannot be verified independently until it does",
        "B05's provenance persistence is deliberately NOT designed here (it would need store.py DDL/migrations, which are out of the proposed file scope) - registered as a separate work package if the owner wants persistence",
        "A-AR-02's bridge table (E01-E13 / U117 / FC903 / CL-AC -> L/P/O/M) for the 13 unassignable goal rows is still outstanding",
        "R-3's narrowed scope (admission loader only) awaits the owner's explicit re-confirmation",
        "handbook section 3 run structure is partial: card.json, baseline.json, data-manifest.json, requirements.csv and reviews/ (beyond the review records) are not created",
    ],
    "next_step": (
        "Collect the B.DR verdict, correct the design in place, then (in parallel) start A07/A08 "
        "on the frozen phase-A contracts and prepare the A06 mechanism-layer baseline. Product "
        "changes wait for the owner's approval of file-scope.md."
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
        result = verify_blobs(existing["produced_files"], source="head")
        result["completeness"] = completeness(existing["produced_files"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_match"] and result["completeness"]["complete"] else 1

    if not args.reviewed_commit:
        print("ERROR: --reviewed-commit is required (B-DR2-09). Generate after committing the "
              "corrections, then commit the rebuilt checkpoint as the stamp commit.")
        return 2

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = args.reviewed_commit
    ledger["commit_anchor"] = commit_anchor()
    ledger["produced_files"] = produced_files()
    ledger["produced_files_verification"] = verify_blobs(ledger["produced_files"], source="index")
    ledger["produced_files_completeness"] = completeness(ledger["produced_files"])
    ledger["generated_at_utc"] = datetime.now(UTC).isoformat()
    out = RUN / "checkpoint.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(ledger['produced_files'])} files; "
          f"blob all_match={ledger['produced_files_verification']['all_match']}; "
          f"complete={ledger['produced_files_completeness']['complete']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
