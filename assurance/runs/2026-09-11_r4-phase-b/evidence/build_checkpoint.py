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
    "phase": ("B (position-transparent index and read-only access) - IMPLEMENTATION IN PROGRESS: "
              "B02 landed; B01/B03-B07 still design-only"),
    "step": ("B04 implemented (acceptance + finding, NO product change): a move keeps the reference, and the "
             "same-path overwrite case is pinned and registered as F-B04-1 (out of the allowed file set)"),
    "last_completed_step": (
        "B02 closed after five revisions under four independent reviews (see the review entries below; all "
        "counter-examples fixed, mutants M5/M6/M7 killed, CI green on every step commit). "
        "B04 then implemented as acceptance plus a registered finding, with NO product change - the design "
        "goal already held after B02, so per the step's own plan the deliverable is verification, not code: "
        "new file company-wiki/tests/contract/test_r4b04_reference_stability.py (4 cases) proves that a move "
        "within a root keeps document_id/source_id/content_sha256 while the locator changes and the old row "
        "is marked missing, that location_id is only a derived locator, and that a vanished version is "
        "answered MISSING rather than substituted by another revision. Measured: 4 passed, the combined "
        "B04+B02+gates+ratchet set 69 passed, ruff clean. The pinned gap (scanner.py:1123 re-points the "
        "location row when the same relative path holds a new revision, so the superseded revision loses "
        "its only locator) is registered as finding F-B04-1 with three candidate remedies, all of which "
        "touch files outside this step's allowed set (write face / DDL / another work package)."
    ),
    "current_gate": (
        "B04 independent review (focused: the four acceptance cases and the F-B04-1 registration), then "
        "B05 -> B01 -> B03 -> B06 -> B07. The owner still owes two rulings on B02, both stated as a single "
        "authoritative difference list (evidence/b02-implementation.md section 3): S-10 (the claim-trusted "
        "row and its four differences from pre-B02) and S-11 (budget exhaustion maps to that row instead of "
        "the design's blocked, because ResolutionStatus has exactly five values)."
    ),
    "pending_review": [
        {
            "gate": "B.DR rev6",
            "scope": "B design v0.1.5",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 3, "P2": 6, "P3": 4},
            "note": ("also falsified the first two-sided claim audit: it asserted verification without "
                     "patterns/commands/output; replaced by evidence/claim_fact_audit.py, which is "
                     "re-runnable and searches the whole run directory"),
            "record": "reviews/B.DR-rev6.json",
            "reviewer_self_reported_id": "394101b5-bbc0-428e-a490-758a2fd5390d",
        },
        {
            "gate": "B.VR (B04, focused)",
            "scope": "company-wiki/tests/contract/test_r4b04_reference_stability.py (4 cases) + finding F-B04-1",
            "status": "pending",
            "reviewer": ("independent subagent (non-author) - must differ from the four B02 reviewer sessions; "
                         "the questions are whether the four cases really pin the claimed behaviour (including "
                         "the pinned scanner re-point) and whether 'no product change' is the right call "
                         "rather than a gap in the step"),
            "note": "evidence: evidence/b04-implementation.md, evidence/b04-test-run.txt, findings.md F-B04-1",
        },
        {
            "gate": "B02 closure decision (author, 2026-09-12)",
            "scope": "wiki 1d8b1f7 (rev5, text-only) on top of the four reviewed revisions",
            "status": "closed",
            "verdict": "no further review round requested",
            "note": ("The behavioural surface converged under four independent rounds (all four historical "
                     "counter-examples fixed, mutants M5/M6/M7 killed, mutation harness restores the file "
                     "byte-identically, CI green on every step commit). rev5 changes words only: the "
                     "difference list moved to one authoritative place and the two-sided audit - now also "
                     "searching the three product files - enforces it (32/32). A fifth prose-only round "
                     "would add no behavioural evidence, so B02 is closed here; the next independent "
                     "review (B04) is asked to re-check the single-source rule as part of its own scope, "
                     "and the owner still rules on S-10/S-11 using the authoritative list."),
        },
        {
            "gate": "B.VR rev3 (B02 rev3)",
            "scope": "company-wiki 182846b",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P2": 1, "P3": 6},
            "note": ("confirmed all four earlier counter-examples fixed and reproduced every measured "
                     "number; rev3 falsified the (now-retired) claim that the trust level was equivalent "
                     "to pre-B02 and found three surviving mutants; all seven findings addressed in rev4"),
            "record": "reviews/B.VR-b02-rev3.json",
        },
        {
            "gate": "B.VR rev4 (B02 rev4, focused)",
            "scope": "company-wiki da5e0f5",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P2": 1, "P3": 3},
            "note": ("the corrected wording had reached only four of the nine places that restated it, "
                     "and two further differences (c: the local probe; d: verified-copy preference) were "
                     "missing from the list; all four findings addressed in rev5, which moved the list to "
                     "one authoritative place and taught the audit to search the product files"),
            "record": "reviews/B.VR-b02-rev4.json",
        },
        {
            "gate": "B.VR rev2 (B02 rev2)",
            "scope": "company-wiki 350b67a",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P2": 2, "P3": 3},
            "note": ("rev2 confirmed both rev1 P1s genuinely fixed; it found that the claim-trusted "
                     "fallback short-circuited the walk and that the then-current justification for the "
                     "S-10 deviation was false; all five addressed in rev3"),
            "record": "reviews/B.VR-b02-rev2.json",
        },
        {
            "gate": "B.VR rev1 (B02)",
            "scope": "company-wiki cab1fd6",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 2, "P2": 2, "P3": 3},
            "note": ("reproduced the author's numbers digit-for-digit AND found two real defects the author "
                     "had missed; both fixed in 350b67a, each with a regression case"),
            "record": "reviews/B.VR-b02.json",
        },
        {
            "gate": "B.DR rev5",
            "scope": "B design v0.1.4",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 2, "P2": 4, "P3": 5},
            "note": "corrected as v0.1.6 (see findings F-B01-5); rev6 then rejected v0.1.5's successor as well",
            "record": "reviews/B.DR-rev5.json",
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
        "OWNER: rule on S-10 (B02 implements segment-3 hash equality as a preference, not a hard gate) - see evidence/b02-implementation.md section 3",
        "OWNER: confirm the A05 sample list and the read-only command manifest (gate G7 + G4 for behaviour beyond --help)",
        "OWNER/OPERATOR: isolated copy for behavioural probes (gate G8) - see findings F-B00-3 for a two-level proposal",
        "OPERATOR: independent boundary observation and reviewer assignment records (G5/G6)",
    ],
    "gate_status": {
        "B.DR": ("rev1-rev6 all rejected; v0.1.6 was the correction pass and v0.1.7 only back-fills the B02 "
                 "implementation record (no design change); the ratchet table stays frozen (S-7)"),
        "B.VR": ("rev1 = rejected (2xP1/2xP2/3xP3); rev2/rev3/rev4 = accepted_with_findings and each round "
                 "falsified one of the author's justification sentences, now single-sourced; B02 closed by "
                 "the author's documented decision (no fifth prose-only round); B04 review pending. "
                 "Protocol ready (b-vr-protocol.md); L1 mechanism layer unblocked by S-5, L2 real-byte layer "
                 "still needs G8"),
        "B.AR": "not started",
        "B04": ("implemented as acceptance + finding F-B04-1 with NO product change (the design goal already "
                "held after B02); review pending"),
        "S-1_test_files": "APPROVED (F10/F11); F10 landing used by tests/contract/test_r4b02_candidate_selection.py (23 cases)",
        "S-2_R1_R4_out_of_B": "DECIDED - R-1/R-4 stay outside B as separate work packages",
        "S-3_export_path": "DECIDED - export_policy_2x untouched, payload hash frozen (B-payload-hash still NOT executed)",
        "S-4_consumer_side": "DECIDED - belongs to phase C, B does not sign it",
        "S-5_isolated_copy": "DECIDED - two levels; L1 can start now",
        "S-6_fourth_round": "done - five review rounds were run in total (rev4 then rev5/rev6)",
        "S-7_ratchet_edit": "DECIDED - NOT allowed; table unchanged and asserted by test_r4b02_complexity_ratchet_table_is_not_edited",
        "S-8_N1": "DECIDED - N-1 stays outside B, registered as a cross-repo protocol item",
        "S-10_byte_hard_gate": ("OPEN - non-preferred copies are hard-gated; the preferred copy keeps the "
                                "pre-B02 claim-trust level and B03 owns the read-path gate"),
        "S-11_budget_status": "OPEN - budget exhaustion maps to that trust level, not to a sixth status value",
        "implementation_go_ahead": "GRANTED (owner 2026-09-12, second batch); B02 landed and revised, B04 next",
    },
    "actual_side_effects": (
        "Unlike the design-only rounds, this run has now MODIFIED PRODUCT FILES in company-wiki: "
        "src/company_wiki/source_catalog/service.py, src/company_wiki/source_catalog/resolver.py and the new "
        "tests/contract/test_r4b02_candidate_selection.py - all inside the authorized file scope (F1/F2/F10) "
        "and pushed as cab1fd6. Executed locally: pytest (including the full suite with coverage), ruff, "
        "git worktree, and read-only probes over synthetic tmp fixtures. NOT executed: any network/download/"
        "LLM egress, any product-data write, any DB write, task registration, worker action or deletion; no "
        "behavioural probe against the production catalog. The run directory HAS been pushed "
        "(origin/main = 2ced153) and every push ran revenue-forecast's mandatory pre-push gate, whose "
        "real-data suite opens the production catalog READ-ONLY and advances -shm (attributed in "
        "../2026-09-11_r4-phase-a/boundary-audit.md). Several pre-existing wiki tests also open the "
        "production catalog read-only when the suite runs (known limitation, attributed in phase A)."
    ),
    "failed_or_unknown": [
        "B03-B07 are still design-only: the byte-level hard gate ('serve verified bytes or fail explicitly') does not exist yet, so a preferred copy whose bytes drifted is served on the catalog's claim (S-10's other half)",
        "B-payload-hash has never been executed (no frozen baseline in the package and the value needs a CLI that is not approved) - B02 only claims that no SourceHandle field was added",
        "the L01-L12 mechanism-layer baseline exists as A06-D0 (787 unit + 1748 contract passed / 7 skipped); the B-side cases added by B02 cover L01-L04 plus budget/cancel/no-network and the seven review regressions, not the whole matrix",
        "B05's provenance shape is now additive under a reserved key, but the json_extract regression assertion can only be proved when the tests run (needs implementation)",
        "N-1 support is undefined on both sides and is therefore registered as a cross-repo protocol item, no longer part of B07's completion",
        "handbook section 3 run structure is still partial: card.json, baseline.json, data-manifest.json, requirements.csv and oracle/ are absent",
        "G5/G6/G7/G8 remain owner/operator items",
        "revenue-forecast dirty=0 is incomplete: three .tmp-zr408-unit* directories are unreadable (permission denied), so git cannot enumerate them",
        "test_dbx05_symlink_escape_rejected skips on this host (symlinks not supported), so the symlink-escape control did not run here",
        "the reviewer could not verify S-9's 61.3% counterfactual, the historical first-round FC-1201 failure claim, B-payload-hash, or any real cloud-placeholder layer (recorded in reviews/B.VR-b02.json limitations)",
    ],
    "next_step": (
        "Send B02 rev2 to a fresh independent B.VR session (the rev1 reviewer's own counter-examples are "
        "now regression cases; ask the new reviewer to re-run them), then continue with B04 -> B05 -> B01 "
        "-> B03 -> B06 -> B07, each step as its own commit with the ratchet/coverage rerun and its own "
        "independent review. The owner still owes two rulings: S-10 and S-11."
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
        "note": ("per-file versions matter: root-contract is v0.4.2 while operation-contract and "
                 "identity-contract are v0.4.1, and owner-rulings was corrected in place; the A-side "
                 "checkpoint records the per-file digests"),
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
