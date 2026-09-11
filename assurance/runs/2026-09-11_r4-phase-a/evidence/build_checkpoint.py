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


LEDGER = {
    "run_id": "2026-09-11_r4-phase-a",
    "phase": "A",
    "step": "A.DR rev2 (re-review of the corrected A01-A04 contracts)",
    "last_completed_step": (
        "A01 baseline map v0.2; A02 root-contract v0.2; A03 operation-contract v0.2; "
        "A04 identity-contract v0.2; A.DR rev1 closed with verdict rejected and all "
        "16 findings corrected in place; inputs.json and boundary-audit.md added; "
        "--help manifest re-run with catalog-family snapshot coverage (52 x rc=0)"
    ),
    "current_gate": "A.DR rev2 package (A01-A04 v0.2 + inputs.json + boundary-audit.md) ready for an independent reviewer",
    "pending_review": [
        {
            "gate": "A.DR rev2",
            "scope": "A01-A04 v0.2 and the run ledgers",
            "status": "pending",
            "reviewer": "independent subagent (non-author)",
            "assignment_stamp": (
                "NOT YET STAMPED EXTERNALLY (A-DR-16): the reviewer identity must be written "
                "into this checkpoint by the orchestrator/operator from outside the reviewer "
                "session; a reviewer self-reported id does not make independence auditable"
            ),
        },
        {
            "gate": "A.DR rev1",
            "scope": "A01-A04 v0.1 and the run ledgers",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 8, "P2": 5, "P3": 3, "P0": 0},
            "record": "reviews/A.DR.json",
            "reviewer_self_reported_id": "7cd316cc-50bc-44d5-9574-180030d9ee09",
            "closed_at_utc": "2026-09-11T20:23:44Z",
        },
    ],
    "actual_side_effects": (
        "R4 A-phase actions: 52 x `python -B -m company_wiki.source_catalog.cli <cmd> [sub] "
        "--help` (re-run once with the extended snapshot; every invocation rc=0) plus read-only "
        "file/git inspection - none of which opens the catalog (catalog.sqlite3, -shm and -wal "
        "all unchanged across the run; wiki's CI-equivalent gate was separately shown not to "
        "touch it either). No data command, no --dry-run, no network, no config/DB/task/worker "
        "change in any repository. "
        "DISCLOSED: the session ALSO pushed to GitHub five times tonight, and this repo's "
        "mandatory pre-push gate runs its real-data suite against the PRODUCTION catalog "
        "read-only (tools/pre_push_gate.py:184-199). That is what advanced catalog.sqlite3-shm "
        "at 21:18:15 and 21:26:47 (gate runs preceding pushes #139 21:19:16 and #140 21:27:44; "
        "reproduced by the manual gate at 22:05:03). The v0.1 statement that no code path "
        "touching the catalog was executed was therefore too strong and is retracted; the "
        "reading was read-only throughout (main DB and -wal never changed). "
        "A 99-sample/1500 s passive observation found zero -shm transitions, and the 22:00 daily "
        "task touched it at 22:00:02/22:00:18 as expected. See boundary-audit.md and F-A01-8."
    ),
    "failed_or_unknown": [
        "boundary independence is NOT independently observed: object-access auditing / handle-level evidence needs an operator (gate G5); the author does not self-certify it, even though the -shm attribution is now resolved by CI timestamps + gate code",
        "reviewer independence is NOT externally stamped (gate G6, A-DR-16)",
        "six owner rulings are required before A02 can be frozen (gate G2): symlink_policy (declared but never read), reusable_for_filing (explicit false is fail-open), convergence of the two divergent root-admission implementations, privacy_class defaulting to public, an owner for identity rule R6, and whether A04 R4's strict reading covers location-representation",
        "A02 section 4 items 1-2 and A04 V1/V2/V4 remain VR items needing an isolated copy (production catalog is 49,677,344,768 bytes; behavioural probes are forbidden on it)",
        "behavioural probes (--dry-run / read-only data commands) have no approved command manifest yet (gate G4)",
        "A05 real-corpus sample list not yet submitted for per-item confirmation (gate G7)",
        "A06 L01-L12 baseline and read-only trace not started",
        "A03 section 2.3 items 3-5 and A04 V3's data-side half stay open pending VR",
        "the execution-plan section 50 minimum-artifact list is still partial: results/, oracle/, tests/, rollback-contract.json and outcomes.json belong to later phases and are not created; reviews/ now exists",
    ],
    "authorization_needed": [
        "GRANTED 2026-09-11: A-phase precise DEV/data-read permission; --help-only command manifest; VR reviewer assignment",
        "STILL NEEDED: owner rulings on the six open questions (gate G2)",
        "STILL NEEDED: an isolated catalog copy (or an operator-run equivalent) before any behavioural probe",
        "STILL NEEDED: operator action for G5/G6 (independent boundary observation, external reviewer stamp)",
    ],
    "gate_status": {
        "G1_A_DR": "rev1 rejected; corrections complete; rev2 pending",
        "G2_owner_rulings": "pending (6 items)",
        "G3_input_manifest": "done (inputs.json)",
        "G4_command_manifest": "partial: --help manifest approved and executed; behavioural-probe manifest not submitted",
        "G5_independent_boundary_observation": "pending operator action",
        "G6_reviewer_independence_stamp": "pending operator action",
        "G7_A05_sample_list": "pending",
        "G8_isolated_copy": "pending",
    },
    "next_step": (
        "Commit the v0.2 corrections and boundary evidence, spawn A.DR rev2 (independent, "
        "non-author), then put the six owner rulings and the A05 sample list to the owner."
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
    args = parser.parse_args(argv)

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = args.reviewed_commit or "PENDING (stamped in the follow-up commit)"
    ledger["inputs_note"] = (
        "revenue-forecast: `head` is the tree the reviewer reads and `dirty` is its "
        "working-tree count at generation time (non-zero only because the corrections were "
        "still uncommitted when this file was generated; see `reviewed_commit`). Every commit "
        "made in this run touches only assurance/runs/2026-09-11_r4-phase-a/, so the twelve "
        "product input hashes frozen in baseline-map.md section 0 and inputs.json stay "
        "byte-accurate (independently re-derived by A.DR rev1: 12/12 HASH_OK). company-wiki "
        "carries two doc-only edits outside this run directory (PLANNING_STATUS.md and the "
        "audit plan's progress.md/task_plan.md) plus PLANNING_STATUS.md's own entry; no product "
        "code or config is touched in any repository."
    )
    ledger["produced_files"] = produced_files()
    ledger["produced_files_note"] = (
        "Computed by evidence/build_checkpoint.py over the whole run directory; checkpoint.json "
        "itself is excluded (it cannot hash itself). The A.DR review file is included because "
        "the reviewer wrote it inside this run directory."
    )
    ledger["generated_at_utc"] = datetime.now(UTC).isoformat()
    out = RUN / "checkpoint.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(ledger['produced_files'])} produced files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
