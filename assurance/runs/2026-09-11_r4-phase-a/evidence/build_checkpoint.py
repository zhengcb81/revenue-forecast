"""Regenerate checkpoint.json for the R4 phase-A run directory.

Why a generator: A-DR-09 found the hand-written checkpoint inconsistent with
task_plan.md/progress.md and carrying a stale HEAD/dirty pair, and A-DR-11 found
the produced-file list incomplete. Computing every produced-file hash here (and
merging it with an explicit ledger block) removes both classes of drift.

Usage:  python evidence/build_checkpoint.py
Writes: checkpoint.json (run-directory root, i.e. this file's parent's parent)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
WIKI = Path.home() / "Projects" / "company-wiki"
REVENUE = Path.home() / "Projects" / "revenue-forecast"
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


def completeness(files: dict) -> dict:
    """Assert the manifest lists EVERY file in the run directory (B-DR2-09).

    Verification otherwise only walks the manifest and therefore cannot notice an
    unlisted file (the gap the reviewer named).
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
    return {"files_on_disk": len(on_disk), "files_listed": len(listed),
            "unlisted": sorted(on_disk - listed), "phantom": sorted(listed - on_disk),
            "complete": on_disk == listed}


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
    """Compare every recorded digest with the blob git stores for that path.

    B-DR-16 limitation, stated here rather than hidden: this proves "recorded digest
    == blob at <source>", NOT that the manifest is complete, and it anchors the
    RUNTIME revision (index or HEAD) - it does not bind `reviewed_commit`. The
    revision actually compared is reported in the result so a reader can tell which
    tree was checked.
    """
    run_rel = RUN.relative_to(REVENUE).as_posix()
    revisions = {}
    for label, args in (("index", ["git", "-C", str(REVENUE), "write-tree"]),
                        ("head", ["git", "-C", str(REVENUE), "rev-parse", "HEAD"])):
        proc = subprocess.run([*args[:1], "-c", "safe.directory=*", *args[1:]],
                              capture_output=True, text=True)
        revisions[label] = proc.stdout.strip() if proc.returncode == 0 else "unknown"
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
        "checked": len(files),
        "source": source,
        "source_revision": revisions.get(source, "unknown"),
        "head_revision": revisions.get("head", "unknown"),
        "blob_mismatches": mismatched,
        "all_match": not mismatched,
        "proves": "recorded digest == stored blob at the reported revision",
        "does_not_prove": ["manifest completeness", "that reviewed_commit equals the compared revision"],
    }


LEDGER = {
    "run_id": "2026-09-11_r4-phase-a",
    "phase": "A",
    "step": "A v0.4.1 corrections applied after the A07/A08 (and B.DR) reviews",
    "last_completed_step": (
        "A01 baseline map v0.4.1; A02 root-contract v0.4.1; A03 operation-contract v0.4.1; "
        "A04 identity-contract v0.4.1; A.DR rev1/rev2/rev3 rounds; owner six rulings recorded; "
        "A07=A.VR accepted_with_findings (22 negative cases + a five-value error model) and "
        "A08=A.AR rejected (117-row mapping produced) - all their document findings corrected "
        "in v0.4.1, including the corroborated P0 that export_policy_2x IS in production use"
    ),
    "current_gate": (
        "A07/A08 corrections applied; the A package is resubmitted for re-review "
        "(A.VR-rev2), and the R-3 scope narrowing to the admission loader only is flagged for "
        "the owner's explicit re-confirmation (the export path stays in production)."
    ),
    "pending_review": [
        {
            "gate": "A.VR-rev2",
            "scope": "the v0.4.1 contract corrections",
            "status": "pending",
            "reviewer": "independent subagent (non-author)",
        },
        {
            "gate": "A08 (A.AR)",
            "scope": "implementation readiness + the 117-row goal mapping",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P0": 1, "P1": 2, "P2": 2, "P3": 2},
            "record": "reviews/A.AR.json",
            "reviewer_self_reported_id": "b17b1524-2114-4dfa-ab3e-fc8e0a030a1c",
            "note": ("the single P0 is the same fact as B.DR-01; A-AR-02's bridge table "
                     "(E01-E13 / U117 / FC903 / CL-AC -> L/P/O/M) is registered as outstanding"),
        },
        {
            "gate": "A07 (A.VR)",
            "scope": "identity/bytes/provenance contracts, preview licence boundary, negative cases",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P0": 0, "P1": 6, "P2": 3, "P3": 2},
            "record": "reviews/A.VR.json",
            "reviewer_self_reported_id": "2c26659c-ec0c-4696-ae29-022b750b0e11",
            "deliverables_absorbed": ["22 negative cases VR-N01..VR-N22", "five-value error model in A03 section 2.4"],
        },
    ],
    "reviewer_assignments": {
        "note": (
            "Recorded by the authoring session from outside the reviewer sessions (A-DR-16 asks "
            "for exactly this), but process evidence only: an operator-held assignment record is "
            "still required to make independence institutionally auditable (gate G6)."
        ),
        "rev1": {"reviewer_session_id": "7cd316cc-50bc-44d5-9574-180030d9ee09", "assigned_by": "authoring session (subagent spawn)", "record": "reviews/A.DR.json"},
        "rev2": {"reviewer_session_id": "b31cbc67-7142-495a-a9db-8886c700ed8f", "assigned_by": "authoring session (subagent spawn)", "record": "reviews/A.DR-rev2.json"},
        "rev3": {"reviewer_session_id": "70b62d2f-920e-463c-aeb5-dcfc3ebc5f11", "assigned_by": "authoring session (subagent spawn)", "record": "reviews/A.DR-rev3.json"},
    },
    "authorization_record": {
        "record_type": "session-transcript quote; no separately signed artefact exists (A-DR2-11)",
        "granted_by": "repository owner (human)",
        "granted_at_local": "2026-09-11 (evening, before 21:00)",
        "verbatim": "1，授权，2，尽快开门，3，可以",
        "author_interpretation": "(1) authorise the A-phase precise DEV/data-read permission; (2) open the gate as soon as possible; (3) approve the remaining items (--help-only command manifest, VR reviewer assignment)",
        "scope_granted": ["A-phase read-only design work (A01-A04)", "--help-only command manifest execution", "VR reviewer assignment"],
        "scope_not_granted": ["product/config/database writes", "any command beyond --help (including --dry-run and data commands)", "network downloads, LLM egress, task registration, worker resume, deletion"],
        "author_session_id": "session-bfecd191-fbc3-4a66-8ed1-6562479bf102 (DSH_SESSION_ID, runtime-managed)",
    },
    "actual_side_effects": (
        "Inside this run: documentation and read-only inspection only - no CLI of any kind, no "
        "data command, no network, no product/config/DB/task/worker change. The three review "
        "records (A.DR*, A.VR, A.AR) are the reviewers' own writes inside reviews/. "
        "DISCLOSED (B-DR-17): 'no CLI was executed' is an author statement with no independent "
        "observation artefact behind it, and the -shm mtime advanced at 07:48 on 2026-09-12, "
        "which the reviewer correctly attributed to the pre-push gate of this run's own push "
        "(revenue #145) rather than to the authoring actions; main DB and -wal unchanged. "
        "See boundary-audit.md for the full opener inventory (daily task, push gate, manual gate)."
    ),
    "failed_or_unknown": [
        "boundary independence is NOT independently observed: object-access auditing / handle-level evidence needs an operator (gate G5); the author does not self-certify it, even though the -shm attribution is resolved by CI timestamps + gate code",
        "reviewer independence is NOT externally stamped (gate G6, A-DR-16)",
        "A-AR-02: 13 of the 117 goal rows cannot be assigned to any L/P/O/M group (CA-001..004, ZR-001..004, ZR-1002/1003, ZR-307, ZR-404/405) and 13 matrix ids have no directly linked row - the bridge table (E01-E13 / U117 / FC903 / CL-AC -> L/P/O/M) is outstanding",
        "R-3's narrowed scope (admission loader only) needs the owner's explicit re-confirmation, because the widening was based on a factual error; the export path stays in production",
        "A05 has not selected real samples (rules only) and the bounded read-only manifest is unapproved (G4/G7)",
        "A06 has produced no baseline results yet, so 'B fixed it' cannot be verified independently until it exists (G8)",
        "behavioural probes still have no isolated copy (G8), and the CI-excluded local-only wiki tests (ci.yml:51-58) have no enforced surface (D07 gap)",
        "handbook section 3 run structure is still partial: card.json, baseline.json, data-manifest.json and requirements.csv are absent (registered)",
    ],
    "authorization_needed": [
        "GRANTED 2026-09-11: A-phase precise DEV/data-read permission; --help-only command manifest; VR reviewer assignment",
        "DECIDED 2026-09-11: the six open questions (G2) - see owner-rulings-2026-09-11.md",
        "STILL NEEDED: an isolated catalog copy (or an operator-run equivalent) before any behavioural probe",
        "STILL NEEDED: operator action for G5/G6 (independent boundary observation, external reviewer stamp)",
        "STILL NEEDED (later, for B/C): a precise DEV work package per remediation item before any product code change",
    ],
    "gate_status": {
        "G1_A_DR": "closed (rev1/rev2 rejected, rev3 accepted_with_findings)",
        "G2_owner_rulings": "DECIDED 2026-09-11; R-3 scope narrowed 2026-09-12 after the corroborated P0 (admission loader only; export_policy_2x stays) - flagged for the owner's explicit re-confirmation",
        "G3_input_manifest": "done (inputs.json)",
        "G4_command_manifest": "partial: --help manifest approved and executed; the bounded read-only manifest for A05/A06 is written and awaiting approval",
        "G5_independent_boundary_observation": "pending operator action",
        "G6_reviewer_independence_stamp": "pending operator action",
        "G7_A05_sample_list": "pending (selection rules ready in a05-corpus-sample-plan.md)",
        "G8_isolated_copy": "pending",
        "A07_A_VR": "closed: accepted_with_findings; findings corrected in v0.4.1",
        "A08_A_AR": "closed: rejected; the 117-row mapping was produced, the bridge table is outstanding",
    },
    "next_step": (
        "A02 is frozen. Remaining work needs owner/operator input, not more authoring: the A05 "
        "real-corpus sample list (G7), an isolated catalog copy for behavioural probes (G8), and "
        "the operator-held records for G5/G6. The five remediation items from the rulings "
        "(R-1..R-4, R-6) enter the B/C scope and require a precise DEV work package before any "
        "product code changes."
    ),
    "worker_desired_state_note": "not used as process-liveness evidence",
    "catalog_size_bytes": 49677344768,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reviewed-commit",
        default=None,
        help=("revenue-forecast commit that contains this run directory's v0.2 corrections; "
              "stamped in the immediate follow-up commit because a commit cannot contain "
              "its own hash"),
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help=("do not write anything: re-check the EXISTING checkpoint.json produced_files "
              "against the committed blobs (source=head) and print the result; exit 1 on any "
              "mismatch. Run this after committing."),
    )
    args = parser.parse_args(argv)

    if args.verify_only:
        existing = json.loads((RUN / "checkpoint.json").read_text(encoding="utf-8"))
        result = verify_blobs(existing["produced_files"], source="head")
        result["completeness"] = completeness(existing["produced_files"])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_match"] and result["completeness"]["complete"] else 1

    if not args.reviewed_commit:
        print("ERROR: --reviewed-commit is required (B-DR2-09): commit the corrections first, "
              "then rebuild and commit the checkpoint as the stamp commit.")
        return 2

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = args.reviewed_commit
    ledger["commit_anchor"] = {
        "head": subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                               "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "index_tree": subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REVENUE),
                                     "write-tree"], capture_output=True, text=True).stdout.strip(),
        "note": "anchor for the tree this checkpoint was generated from",
    }
    ledger["reviewed_commit_note"] = (
        "`reviewed_commit` carries the reviewed corrections (documents, evidence and ledgers). "
        "The stamp that records this value necessarily lands in the immediately following commit "
        "(d152833/3e0c8f3 for v0.2, 34b2291 for v0.3), which changes only checkpoint.json - so "
        "the reviewer should read reviewed_commit for the contracts and the tip commit for the "
        "ledger stamp. A commit cannot contain its own hash, which is exactly the staleness "
        "A-DR-09 flagged; recording both removes the ambiguity instead of hiding it."
    )
    ledger["inputs_note"] = (
        "revenue-forecast `dirty` is the working-tree count at generation time; it is non-zero "
        "only when this file is regenerated before the corrections are committed. `reviewed_commit` "
        "is the clean tree the reviewer reads, and every commit in this run touches only "
        "assurance/runs/2026-09-11_r4-phase-a/, so the twelve product input hashes frozen in "
        "baseline-map.md section 0 and inputs.json stay byte-accurate (independently re-derived "
        "by A.DR rev1 and rev2: 12/12 HASH_OK). company-wiki moved from the A01 freeze 7d4852f to "
        "478bb92 (planning ledger edits only) and then to ca63ff2 (one ledger sentence), i.e. "
        "no product code or config is touched in any repository; the drift and its scope are "
        "recorded in baseline-map.md section 0 (A-DR2-08)."
    )
    ledger["produced_files"] = produced_files()
    ledger["produced_files_note"] = (
        "Computed by evidence/build_checkpoint.py over the whole run directory; checkpoint.json "
        "itself is excluded (it cannot hash itself). The A.DR review records are included because "
        "the reviewers wrote them inside this run directory. SHA-256 is taken over the RAW "
        "working-tree bytes; because a commit cannot contain its own hash, the recorded digest "
        "for checkpoint.json would be circular and is therefore omitted - verify it with "
        "`git hash-object` instead."
    )
    ledger["produced_files_verification"] = verify_blobs(ledger["produced_files"], source="index")
    ledger["produced_files_completeness"] = completeness(ledger["produced_files"])
    ledger["produced_files_verification"]["post_commit_recheck"] = (
        "Run `python evidence/build_checkpoint.py --verify-only` after committing: it re-checks "
        "every recorded digest against `git cat-file blob HEAD:<path>`. Build time can only "
        "check the staged blob, because the commit that carries this file does not exist yet."
    )
    ledger["generated_at_utc"] = datetime.now(UTC).isoformat()
    out = RUN / "checkpoint.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(ledger['produced_files'])} produced files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
