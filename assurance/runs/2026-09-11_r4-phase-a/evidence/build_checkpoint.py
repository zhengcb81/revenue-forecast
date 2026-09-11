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


def verify_blobs(files: dict, source: str = "index") -> dict:
    """Prove that each recorded sha256 equals the blob that will be/was committed.

    A-DR2-01: four files were committed before the run directory's .gitattributes
    existed, so core.autocrlf stored them as LF while the hashes were computed on a
    CRLF working tree. The recorded digest must therefore be checked against the
    repository blob, not only against the working tree.

    source="index" -> `git show :<path>` (what the pending commit will publish); this
    is what build time can check, because a commit cannot contain its own verification.
    source="head"  -> `git cat-file blob HEAD:<path>` (post-commit re-check).
    """
    run_rel = RUN.relative_to(REVENUE).as_posix()
    mismatched = []
    for rel, meta in files.items():
        spec = (f":{run_rel}/{rel}" if source == "index"
                else f"HEAD:{run_rel}/{rel}")
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
        "blob_mismatches": mismatched,
        "method": (f"sha256 of the indicated blob compared with produced_files[rel].sha256 "
                   f"(source={source})"),
        "all_match": not mismatched,
    }


LEDGER = {
    "run_id": "2026-09-11_r4-phase-a",
    "phase": "A",
    "step": "A.DR rev3 closed (accepted_with_findings); v0.3.1 text corrections applied",
    "last_completed_step": (
        "A01 baseline map v0.3; A02 root-contract v0.3; A03 operation-contract v0.3; "
        "A04 identity-contract v0.3; A.DR rev1 rejected (8P1/5P2/3P3) -> v0.2; A.DR rev2 "
        "rejected (1P1/7P2/3P3, 10/16 round-1 findings closed) -> v0.3 (blob renormalisation + "
        "attribution propagation + citation precision); A.DR rev3 accepted_with_findings "
        "(0 P0/P1, 5 P2 + 8 P3) -> v0.3.1 text corrections in this commit"
    ),
    "current_gate": (
        "A.DR rev3 closed with accepted_with_findings; the package is usable as the B/C baseline "
        "ONLY after the six owner rulings (G2). A02 must not be frozen before G2."
    ),
    "pending_review": [
        {
            "gate": "A.DR rev3",
            "scope": "A01-A04 v0.3 and the run ledgers",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P0": 0, "P1": 0, "P2": 5, "P3": 8},
            "round1_closure": "11 of 16 closed (open: A-DR-06/08/09/13/16)",
            "round2_closure": "5 of 11 closed (open: A-DR2-02/04/05/08/10/11)",
            "record": "reviews/A.DR-rev3.json",
            "reviewer_self_reported_id": "70b62d2f-920e-463c-aeb5-dcfc3ebc5f11",
            "note": ("the reviewer asked for ten pure-text corrections and explicitly said no probe "
                     "re-run is needed; those corrections land in this commit, so no rev4 round is "
                     "scheduled"),
        },
        {
            "gate": "A.DR rev2",
            "scope": "A01-A04 v0.2 and the run ledgers",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 1, "P2": 7, "P3": 3, "P0": 0},
            "round1_closure": "10 of 16 closed; A-DR-01/06/08/10/13/16 not closed",
            "record": "reviews/A.DR-rev2.json",
            "reviewer_self_reported_id": "b31cbc67-7142-495a-a9db-8886c700ed8f",
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
        "R4 A-phase actions: 52 x `python -B -m company_wiki.source_catalog.cli <cmd> [sub] "
        "--help` (run three times across the correction rounds; every invocation rc=0) plus "
        "read-only file/git inspection - none of which opens the catalog (catalog.sqlite3, -shm "
        "and -wal all unchanged across each run; wiki's CI-equivalent gate was separately shown "
        "not to touch it either). No data command, no --dry-run, no network download, no "
        "config/DB/task/worker change in any repository. "
        "DISCLOSED: the session ALSO pushed to GitHub - revenue 10 times (#134 20:19:41 through "
        "#142 22:28:17) and company-wiki 3 times (#100 20:17:26, #101 22:08:58, #102 22:25:06), "
        "all CI-success - and this repo's mandatory pre-push gate runs its real-data suite "
        "against the PRODUCTION catalog read-only (tools/pre_push_gate.py:184-199), while a "
        "manual gate run opens it too. That explains every observed catalog.sqlite3-shm advance: "
        "21:18:15 and 21:26:47 (#139/#140 gates), 22:05:03 (manual gate), 22:10:11 (#141 gate), "
        "22:26:59 (#142 gate), plus 22:00:02/22:00:18 (the daily task). The v0.1 statement that "
        "no code path touching the catalog was executed was therefore too strong and is "
        "retracted; the reads were read-only throughout (main DB and -wal never changed). "
        "A 99-sample/1491.5 s passive observation found zero -shm transitions. See "
        "boundary-audit.md and F-A01-8."
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
        "handbook section 3's run structure is ALSO partial and was missing from the earlier list (A-DR2-11/A-DR3-10): card.json, baseline.json, data-manifest.json and requirements.csv are not provided (command-manifest.json and inputs.json are the nearest equivalents; baseline-map.md is prose, not baseline.json)",
        "no separately signed owner-authorization artefact exists - authorization_record is a transcript quote (A-DR2-11)",
    ],
    "authorization_needed": [
        "GRANTED 2026-09-11: A-phase precise DEV/data-read permission; --help-only command manifest; VR reviewer assignment",
        "STILL NEEDED: owner rulings on the six open questions (gate G2)",
        "STILL NEEDED: an isolated catalog copy (or an operator-run equivalent) before any behavioural probe",
        "STILL NEEDED: operator action for G5/G6 (independent boundary observation, external reviewer stamp)",
    ],
    "gate_status": {
        "G1_A_DR": "closed: rev1 rejected, rev2 rejected, rev3 accepted_with_findings (0 P0/P1); v0.3.1 text corrections applied, no rev4 scheduled",
        "G2_owner_rulings": "pending (6 items) - A02 must not be frozen before this",
        "G3_input_manifest": "done (inputs.json)",
        "G4_command_manifest": "partial: --help manifest approved and executed; behavioural-probe manifest not submitted",
        "G5_independent_boundary_observation": "pending operator action",
        "G6_reviewer_independence_stamp": "pending operator action",
        "G7_A05_sample_list": "pending",
        "G8_isolated_copy": "pending",
    },
    "next_step": (
        "Hand the six owner rulings (G2) and the A05 real-corpus sample list (G7) to the owner; "
        "arrange the operator actions for G5/G6 and the isolated copy for G8. Do not freeze A02 "
        "or start B/C work before G2."
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
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_match"] else 1

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = args.reviewed_commit or "PENDING (stamped in the follow-up commit)"
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
