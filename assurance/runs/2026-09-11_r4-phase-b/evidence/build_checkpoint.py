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
    "phase": ("B (position-transparent index and read-only access) - B01-B10 IMPLEMENTED, PUSHED, "
              "REVIEWED AND DISPOSED OF, plus all four registered residuals R3 (fifth root inside "
              "an isolated catalog), R4 (cross-repo reuse through the filing-fetch entry point, "
              "read-only), R5 (the three dropbox_stock bytes) and R6 (the residual-risk register "
              "entry). B05, B08 (G8 level 2), B09/B.AR, B10, R3, R4, R5 and R6 are all closed; the "
              "only open items need the owner's go-ahead (see failed_or_unknown)"),
    "step": ("R4 (cross-repo end-to-end reuse, read-only) and R5 (dropbox_stock byte "
             "verification) closed on 2026-09-18, after R3 (fifth root by CONFIG ONLY inside an "
             "isolated catalog) earlier the same day, and after the owner-instructed product-fix "
             "batch of that day; a follow-up increment on 2026-09-19 then closed the last two "
             "sites the owner's ruling (4) named - the SECOND of the two fetchall calls and the "
             "record-transaction guard, the latter now DRIVEN by fault injection rather than "
             "inferred from its siblings. The preceding step B10 (single read chain) "
             "closed on 2026-09-17 after four review rounds: increment 1 (registry + v1 adapters "
             "+ gate) = accepted_with_findings; batches 1-2 (seven readers converged, "
             "metadata_state added) = REJECT then disposed; the r2 dispositions = REJECT then "
             "disposed; and the final verification = APPROVE_WITH_FINDINGS, whose one live P2 "
             "(the MAIN-path manifest parse) and four evidence problems are disposed of in "
             "company-wiki c4f5b8a / revenue-forecast 65cc18d. The chain now has ONE parse "
             "implementation (store.metadata_state / metadata_object), one declared non-chain "
             "reader (section_query, whose contract is a named error), two count-based ratchets "
             "(CONFIRMED_DIRECT_READERS = 1 entry; COLUMN_VALUE_HANDOFFS = 12 scopes / 15 sites) "
             "plus a hard zero for the rest of the product package, and measured gate boundaries "
             "written into the product"),
    "last_completed_step": (
        "The 2026-09-19 follow-up increment (company-wiki f39bd5a, remote CI run 35430114632) "
        "closed the LAST TWO sites the owner's ruling (4) named, and corrected two of the "
        "author's own record defects. (a) The SECOND of the two fetchall calls "
        "(backfill_text_fingerprints' locations read) was still unguarded after the 2026-09-18 "
        "batch, so one failing statement escaped the whole backfill batch and starved every "
        "document behind it; it now records a named per-document outcome - a READ failure says "
        "nothing about the document, so it is retryable with backoff and becomes terminal only "
        "once retry_limit is spent. (b) The record-transaction guard was the one member of the "
        "family justified only by 'the same shape as its siblings', which is a reading rather "
        "than a proof; it now has an unambiguous fault injection (the switch is armed after "
        "seeding, and normalize_catalog opens exactly one store.transaction() per document) and "
        "its own mutant. Registered limits: the recording call itself is not guarded (a "
        "database that cannot accept the outcome row is a hard stop), and the two BATCH-level "
        "reads outside the loop stay fatal because they cannot be attributed to one document. "
        "Measured: mutant matrix 17/17 KILLED with the repository untouched, every mutant "
        "red-before-green inside its temporary copy; contract 1939 passed + 8 skipped, unit 799 "
        "passed, coverage AND complexity ratchets 2 passed. Two record defects were corrected "
        "rather than carried: the 2026-09-18 coverage anchor was the raw sha256 of a working-"
        "tree file that was NOT retained (and coverage.json embeds a timestamp, so a raw hash "
        "is not reproducible), and the mutation matrix had declared one mutant id TWICE while an "
        "ambiguous anchor would have mutated whichever copy came first - the harness now refuses "
        "both plus a no-op replacement, and the one-off audit scripts were deleted so the record "
        "does not carry two drifting copies of the same check. The full suite was 1 failed / "
        "2870 passed / 8 skipped: the single failure is an EXISTING real-root journey case whose "
        "write oracle digests the st_size of a live root's top-level children, and a 240 s "
        "read-only watch caught five of those directories flipping 4096 -> 0 on their own with "
        "mtime_ns unchanged (the cloud-placeholder signature of the same family as R5's "
        "F-BAR-13); the case passes when re-run alone on the identical tree, and it is one of "
        "the files CI's contract step excludes while the coverage step tolerates failures. "
        "Fixing that pre-existing oracle is outside this step's authorization. Earlier in the "
        "same owner batch, the 2026-09-18 product fixes (company-wiki "
        "24e1c2f) - F-BAR-10 (an adapter-declared root is scanned through its adapter regardless "
        "of the activation snapshot, with ScanReport.strategy making the dispatch observable), "
        "F-BAR-11 (the byte entry point honours the same reusable-root policy the decision path "
        "uses, keyed on the SAME value - the location's root_id - after the review showed the "
        "two keys could disagree under nested roots), F-BAR-12 (additive bundle_usable / "
        "bundle_valid_handle_count / bundle_invalid_roles, envelope schema still 1.0), F-BAR-14 "
        "(the sidecar adapter no longer narrows the declared metadata: form_type, company_name, "
        "source_title, both date spellings and an INT fiscal_year pass through, while the legacy "
        "acquisition/dayu_meta containers stay unborrowed per FC-502) and the whole F-B10R2 "
        "family on BOTH sides - the four in-package column parses (activation / "
        "assertion_service / remediation / scanner) now refuse BY NAME, and normalize_catalog's "
        "handler ingests, per-document read, artifact write and record transaction are "
        "per-document failures, proven behaviourally (pre-fix copy escapes at normalizer.py:1859 "
        "and starves the healthy row; post-fix it does not), plus the two scripts/ readers "
        "converged with the ratchet upgraded to a hard zero. Measured: mutation matrix 15/15 "
        "KILLED at that point (17/17 after the 2026-09-19 increment) with the repository "
        "untouched, full suite 2868 passed / 8 skipped / 0 failed at that point, "
        "coverage AND complexity ratchets 4 passed (then anchored to the raw sha256 8cf4a793... of "
        "a coverage.json that was NOT retained - corrected on 2026-09-19, see the failed_or_unknown "
        "entry F-COV-01), "
        "local CI unit 799 / contract 1936 passed + 8 skipped, remote CI green on company-wiki "
        "24e1c2f (run 35408350167) and revenue-forecast eab6328 (run 35408584197). The batch's "
        "independent review B.VR-ba1 = approve_with_findings (1xP1/5xP2/2xP3) is disposed of in "
        "full, including the P1 that was the author's own bookkeeping (a stale mutation anchor "
        "made '8/8' irreproducible) and two gate failures the author introduced while disposing "
        "of it (the frozen complexity table, and a handoff 'moved' instead of converged). Earlier: "
        "R4/R5/R3, and the B10 dispositions (c4f5b8a / 65cc18d) that routed the main-path manifest "
        "parse through a never-raising helper - pinned by tests/unit/test_b10_manifest_abort_paths.py "
        "and mutants M11/M12. B05 closed with two review rounds (a live P0 in the author's own "
        "fix), B08 level 2 closed with a byte-identical probe re-run plus an audit-hook tripwire, "
        "and B09/B.AR closed with the read-only manifest run plus an independently reproduced "
        "identity/hash re-derivation - carrying an adjudicated OVERREACH on the manifest's own "
        "bounds"
    ),
    "current_gate": (
        "No author-owned gate remains open: B01-B10 plus R3, R4, R5 and R6 are all delivered, "
        "independently reviewed and disposed of, and the owner's four rulings of 2026-09-18 are "
        "executed (the product fixes and the whole F-B10R2 family on both sides, including the "
        "second fetchall and a record-transaction guard that is now driven rather than inferred). "
        "What remains needs the OWNER and is listed in failed_or_unknown / authorization_needed: "
        "the five sibling atomic-write loops that are not per-document sites, untracking the "
        "coverage build outputs, F-BAR-12's other half (a normalize/summarize re-run, i.e. a "
        "production write), and whether the gate's syntactic ratchets should become a dataflow "
        "check. Two items were closed by owner DECISION rather than by work: the "
        "four-production-roots-plus-fifth-root coexistence in the production catalog (not "
        "verified, on purpose) and the R6 hardening of the zero-write claim (not done, on purpose)"
    ),
    "pending_review": [
        {
            "gate": "B.VR-r5 (R5)",
            "scope": ("revenue-forecast: the three dropbox_stock documents B.AR skipped, verified "
                      "with the owner's accepted hydration"),
            "status": "closed",
            "verdict": "approve_with_findings",
            "findings": {"P0": 0, "P1": 1, "P2": 1, "P3": 3},
            "note": ("the fifth independent session confirmed the target set (ids, paths and "
                     "digests against the ratified A05 evidence), walked 5,000 files of the "
                     "Dropbox tree to show the author's Python blindness is CONDITIONAL (both "
                     "instruments agree outside it), and refuted one claim of the author's own: "
                     "'data locality is undeterminable' was an UNDER-claim - it read "
                     "AllocationSize via a zero-access handle and measured that the bytes were "
                     "already locally resident, so the accepted hydration never happened. It "
                     "also caught a missing NTFS ChangeTime in the state fingerprint, a stale "
                     "git head in three documents, and two stale wording/field references. All "
                     "five disposed of in evidence/b-vr-r5-disposition.md, with the harness "
                     "re-run afterwards (8/8 invariants, --verify 3/3)"),
            "record": "reviews/B.VR-r5.json",
            "reviewer_self_reported_id": "independent read-only subagent (no id self-reported)",
        },
        {
            "gate": "B.VR-r4 (R4)",
            "scope": ("revenue-forecast: the cross-repo reuse call through the REAL consumer entry "
                      "point (filing-fetch), read-only"),
            "status": "closed",
            "verdict": "approve_with_findings",
            "findings": {"P0": 0, "P1": 0, "P2": 4, "P3": 4},
            "note": ("the fourth independent session re-ran all four legs with BYTE-IDENTICAL "
                     "stdout, re-hashed the canonical PDF itself (4,172,424 B / e39fbf9c...), and "
                     "found that three supporting legs were defective: the write-surface table's "
                     "only 'REACHED' row was false (the resolve path uses the READ-ONLY reader, "
                     "mode=ro + PRAGMA query_only=ON, so no writable store is ever constructed - "
                     "the A05/A06 analogy was wrong), no_download_requested was VACUOUS (it read a "
                     "key summarise() never emits), the pause-file row's reason was wrong "
                     "(--no-pause-worker is inert because the scope is only built under "
                     "allow_download), plus a stale ran_at/-shm pair, a stale head, and three "
                     "over-wide 'unchanged' claims. All eight disposed of in "
                     "evidence/b-vr-r4-disposition.md; the harness now carries 11/11 invariants "
                     "including pyc-cache and per-leg download checks"),
            "record": "reviews/B.VR-r4.json",
            "reviewer_self_reported_id": "independent read-only subagent (no id self-reported)",
        },
        {
            "gate": "B.VR-r3 (R3)",
            "scope": ("revenue-forecast 3825db2: the fifth root registered by CONFIG ONLY inside an "
                      "isolated catalog + the query -> open -> consumer minimal read"),
            "status": "closed",
            "verdict": "approve_with_findings",
            "findings": {"P0": 0, "P1": 0, "P2": 3, "P3": 3},
            "note": ("the fourth independent session re-ran all three harness modes (main / --mutations / "
                     "--verify), reproduced every recorded number, re-hashed the fixture files on disk to "
                     "confirm the open leg really returned the bytes on disk, and re-confirmed the "
                     "production triple and all three HEADs. C1-C4 and C6 confirmed, C5 partly. Its three "
                     "P2s were all the author's: the deny claim was written wider than the evidence (the "
                     "deny binds the resolver decision, while the byte primitive still serves that root's "
                     "bytes - now MEASURED in deny.byte_entry_point and narrowed in the L04 table, plus "
                     "registered as F-BAR-11); the authorisation basis existed only inside the artefact it "
                     "authorised (now owner-scope-decisions-2026-09-18.md, and the author's own one-day "
                     "date error 09-17 -> 09-18 is corrected); and the new evidence file announced two "
                     "ledger edits in the completed voice before making them (all three ledgers are now "
                     "actually edited). All six disposed of in evidence/b-vr-r3-disposition.md"),
            "record": "reviews/B.VR-r3.json",
            "reviewer_self_reported_id": "independent read-only subagent (no id self-reported)",
        },
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
            "gate": "B.VR (B01)",
            "scope": ("company-wiki 0e28d99 (resolver reuse alignment + 6 cases) and the FC-1001 strict xfail "
                      "in revenue-forecast b6d1fdc"),
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P1": 1, "P2": 3, "P3": 2},
            "note": ("reproduced every measured number and the FC-1001 justification with a real pre-change "
                     "tree, and found one P1 in the AUTHOR'S OWN acceptance: the frozen 'cross-repo' hash was "
                     "the resolver-side export, not the policy_2x payload filing-fetch consumes, and a "
                     "kind-only revert of that copy left all six cases green while turning the consumer "
                     "fail-open. Two P2s were real defects as well (a case-variant declared kind was "
                     "downgraded to derived, and config admission accepted quoted booleans so a declared "
                     "false read as reusable). All six are disposed of in be2e4ed, each with a mutation that "
                     "now fails; the dispositions are tabulated in evidence/b01-review-disposition.md"),
            "record": "reviews/B.VR-b01.json",
        },
        {
            "gate": "B.VR (B03, to be run)",
            "scope": "company-wiki 5ab0779: resolver.read_verified_bytes + ByteReadResult, 13 acceptance cases",
            "status": "pending",
            "reviewer": ("independent subagent (non-author), one round per step: does the entry point really "
                         "return only bytes that were digested as returned (TOCTOU), are all refusals inside "
                         "the contract's five values, can the mid-read check be defeated, and is the "
                         "unimplemented snapshot tier honestly registered rather than implied"),
            "note": ("same round samples the B01 dispositions (be2e4ed); evidence: "
                     "evidence/b03-implementation.md, evidence/b03-plan.md, findings F-B01-8"),
        },
        {
            "gate": "B.VR (B05)",
            "scope": "company-wiki 6909e78 + bdd99dc + 9db3394: merge extraction, reserved r4_provenance with read-modify-write, per-column rules, read-side blocked; 6 F10 cases",
            "status": "closed",
            "verdict": "rejected",
            "findings": {"P1": 2, "P2": 5, "P3": 3},
            "note": ("reproduced the author's numbers and the whole column-rule matrix, and confirmed the "
                     "core fix (pre-B05 dropped other modules' keys; post-B05 only adds the reserved one). "
                     "It falsified two things: conflict preservation depended on scan order (and a later "
                     "agreeing capture erased the candidates), and a declared value could be overwritten "
                     "silently because declaration was recomputed from the stored container instead of "
                     "being bound to the value. Both P1s are fixed in b6a8442 with regression cases; the "
                     "remaining P2/P3 items are tracked in evidence/b05-review-disposition.md, and the "
                     "response-level blocked question became scope item S-13 for the owner"),
            "rework": ("completed rather than re-reviewed (section 11): the P2s are fixed in 9826b3c "
                       "(declaration must match the value the scanner actually consumed; agreeing captures "
                       "accumulate as sources and keep their attribution), B-VR05-03 was resolved by the "
                       "owner (S-13 -> B06/B07), and B-VR05-09/-10 are registered follow-ups; the next "
                       "step's review samples these fixes instead of opening a second full round"),
            "record": "reviews/B.VR-b05.json",
        },
        {
            "gate": "B.VR (B04, focused)",
            "scope": "company-wiki bc3590f: tests/contract/test_r4b04_reference_stability.py (4 cases) + findings",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P2": 2, "P3": 4},
            "note": ("reproduced every number (4/69/ruff, hashes, anchors, one new test file) and ran its "
                     "own mutation matrix (M3/M4/M5/M6/M7 killed); it corrected two of the author's "
                     "statements - F-B04-1 overstated the loss (a metadata-level handle lookup still "
                     "answers; with a second copy the old reference still resolves) and L03's protection "
                     "comes from the pre-B02 provider_document_id gate, not from B02's source-group "
                     "restriction - and it found F-B04-2 (moving the PDF without its sidecar drops the "
                     "document out of the candidate slice, answering MISSING with an empty trace). All six "
                     "findings are addressed in the run directory, including a new author-side mutation "
                     "harness and a capture bound to the reviewed commit."),
            "record": "reviews/B.VR-b04.json",
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
        {
            "gate": "B.VR (B05 malformed shared column)",
            "scope": "company-wiki 74ffeeb..41fdfe1 (read side of documents.metadata_json)",
            "status": "closed",
            "verdict": "rejected_then_verified",
            "findings": {"P0": 1, "P1": 3, "P2": 2},
            "note": ("round 1 found a LIVE P0 in the author's own fix: the SQL json_extract ran before "
                     "the Python guard, so a malformed row raised OperationalError; round 1's P1s "
                     "(RecursionError escaping both guards, the driver-level decode failure) were real "
                     "too. All disposed of; the verification round confirmed 15/15 mutants and the "
                     "shadowing bug the author had introduced and reverted"),
            "records": ["reviews/B.VR-b05malformed.json", "reviews/B.VR-b05malformed-verify.json"],
            "disposition": "evidence/b-vr-b05malformed-disposition.md",
        },
        {
            "gate": "B.VR (B08, G8 level 2)",
            "scope": "isolated root referencing a REAL filing directory read-only",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P2": 2, "P3": 5},
            "note": ("its strongest result is a byte-identical re-run of the probe plus an "
                     "add-audit-hook tripwire around a full build and probe (production catalog open "
                     "count 0). It caught two P2s in the author's work: the tamper case is not a "
                     "content test (the wrong digest is refused at the handle version-pin gate before "
                     "any file is opened) and _real_root_state only covered direct files. Both fixed"),
            "record": "reviews/B.VR-b08l2.json",
            "disposition": "evidence/b-vr-b08l2-disposition.md",
        },
        {
            "gate": "B.AR / B09",
            "scope": "approved READ-ONLY manifest commands + identity/hash re-derivation from the originals",
            "status": "closed_with_overreach",
            "verdict": "approve_with_findings_plus_authorization_overreach",
            "findings": {"P1": 1, "P2": 4, "P3": 3},
            "note": ("it confirmed the evidence was not tampered with (8/8 side-file hashes, its own "
                     "read-only re-run reproducing 9/10 commands byte-for-byte) and that the executed "
                     "set was NOT the manifest as written: an extra command, --limit 100 against the "
                     "manifest's own <= 50, 102 invocations against budget 25, 85 non-zero retries "
                     "against the stop rule, and approval.by = null (never approved in writing). The "
                     "owner delegated the adjudication to the authoring session, which RATIFIED the "
                     "read-only reading, kept the overreach on the record, and turned the bounds into "
                     "mechanical refusals with a 5/5 selftest plus a machine-checkable compliance read"),
            "record": "reviews/B.VR-bar.json",
            "disposition": "evidence/b-vr-bar-disposition.md",
            "adjudication": "owner-authorisation-and-my-adjudication-2026-09-16.md",
        },
        {
            "gate": "B.VR (B10 increment 1)",
            "scope": "company-wiki b829b03/c4a69e0/d92bb33 (read-chain registry + v1 adapter + gate)",
            "status": "closed",
            "verdict": "accepted_with_findings",
            "findings": {"P1": 1, "P2": 2, "P3": 4},
            "note": ("the P1 was a false declaration in the author's own registry: reader.bundle was "
                     "registered as claim-level/'never opens a file' while it hashes artifact files "
                     "through artifact_handle.validate_artifact. It also measured eight gate-bypass "
                     "shapes, which drove the second ratchet and the count-based ratchets"),
            "record": "reviews/B.VR-b10.json",
            "disposition": "evidence/b-vr-b10-disposition.md",
        },
        {
            "gate": "B.VR (B10 batches 1-2)",
            "scope": "company-wiki 326383d/5ec18a5 (seven readers converged + metadata_state)",
            "status": "closed",
            "verdict": "rejected_then_disposed",
            "findings": {"P0": 1, "P1": 2, "P2": 2, "P3": 2},
            "note": ("the P0 was real and was the author's own misfiling: the metadata parse in "
                     "normalize_catalog is NOT inside the per-document try (AST: the only Try covers "
                     "1665-1679), so one malformed column aborted the whole run - and the author had "
                     "registered that unguarded crash path as a deliberate non-chain reader, WITH a "
                     "test pinning the false declaration. A P1 followed (degrading silently recorded "
                     "an identity verdict with no evidence). All disposed of"),
            "record": "reviews/B.VR-b10-r2.json",
            "note_2": ("its partial work also exposed two holes the author then fixed: count-less "
                       "ratchets let a second reader inside a baselined scope pass, and the harness "
                       "recorded a mutant-induced SyntaxError as an assertion kill"),
        },
        {
            "gate": "B.VR (B10 r2 dispositions)",
            "scope": "company-wiki f92fc71 (P0 fix + true declaration + visible degradation)",
            "status": "closed",
            "verdict": "rejected_then_disposed",
            "findings": {"P2": 1, "P3": 5},
            "note": ("it verified all three core fixes as FIXED with its own AST map, its own "
                     "before/after driver and a re-applied mutant, then rejected on one live P2 (the "
                     "SAME defect shape on the sibling normalization_metadata_json column) plus stale "
                     "counts/reasons in the record. Both were disposed of; the P2 fix carries a "
                     "pre-fix reading taken against a mutated temp copy via the probe's B10_WIKI_SRC "
                     "override"),
            "record": "reviews/B.VR-b10-r3.json",
        },
        {
            "gate": "B.VR (B10 r3 dispositions, final verification)",
            "scope": "company-wiki 396c5d6 (sibling-column abort fix + evidence corrections)",
            "status": "closed",
            "verdict": "approve_with_findings",
            "findings": {"P2": 1, "P3": 5},
            "note": ("it independently verified the sibling-column fix as FIXED (its own real-.docx "
                     "parse failure plus a reverted copy: escaped=true at 1727 with zero "
                     "normalized.md, and the healthy document behind it starved), re-confirmed the "
                     "three core fixes and the baseline counts key for key, and reproduced the "
                     "recorded regression numbers exactly. It then found a live P2 of the same "
                     "family that needed no parser failure to fire (the MAIN-path manifest parse) "
                     "and four evidence problems (a probe verdict reading that isolates nothing, "
                     "stale/unanchored citations, an over-claimed 'all fixed', and a mislabelled "
                     "phase-3 failure). All disposed of in c4f5b8a/65cc18d"),
            "record": "reviews/B.VR-b10-r4.json",
        },
    ],
    "reviewer_assignments": {
        "note": ("recorded by the authoring session from outside the reviewer session; still only "
                 "process evidence - an operator-held assignment record is required (gate G6)"),
        "B.DR_rev1": {"reviewer_session_id": "7ad6f0f0-717a-4b25-a1bf-b3604b8953fe", "record": "reviews/B.DR.json"},
    },
    "authorization_needed": [
        "OWNER: whether the five remaining sibling _atomic_write loops should get the same per-document guard treatment, although they are NOT per-document sites (summarizer.py:225, section_extractor.py:374/397, llm_summarizer.py:496, focus_cleanup.py:467/519/588/646, service.py:1367)",
        "OWNER: whether to untrack the build outputs coverage.json / .coverage - they are tracked today, so every coverage measurement leaves the tree dirty (measured cause of one false 'git_status_identical' alert in this run's own harness)",
        "OWNER: F-BAR-12's other half - repairing the derived artifacts of an already-reused document needs an approved normalize/summarize RE-RUN, i.e. a WRITE to the production catalog; the share of documents in that state is still NOT quantified",
        "OWNER: whether the gate's syntactic ratchets should become a dataflow check, given the four measured bypass shapes recorded in GATE_BOUNDARIES",
        "OPERATOR: reviewer assignment records remain process evidence only (gate G6); the operator-held record is still outstanding",
        "CLOSED BY OWNER DECISION on 2026-09-18 and therefore NOT outstanding: fixing F-BAR-10/F-BAR-11/F-BAR-12 and the F-B10R2 family with the two scripts/ readers (done), verifying the four-production-roots-plus-fifth-root coexistence inside the PRODUCTION catalog (declined), and hardening the R6 zero-write claim beyond metadata observation (declined)",
        "NO OWNER RULING IS OUTSTANDING for phase B's code: S-10/S-11/S-12/S-13 were approved as recommended on 2026-09-12, the G8 two-level decision and the read-only manifest were approved on 2026-09-13, the adjudication of the A05 overreach was delegated to the authoring session on 2026-09-16, the residual work packages R3/R4/R5 were chosen by the owner on 2026-09-18, and the four product/runtime rulings of 2026-09-18 are executed",
    ],
    "gate_status": {
        "B.DR": ("rev1-rev6 all rejected; v0.1.6 was the correction pass and v0.1.7 only back-fills the B02 "
                 "implementation record (no design change); the ratchet table stays frozen (S-7)"),
        "B.VR": ("rev1 = rejected (2xP1/2xP2/3xP3); rev2/rev3/rev4 = accepted_with_findings and each round "
                 "falsified one of the author's justification sentences, now single-sourced; B02 closed by "
                 "the author's documented decision (no fifth prose-only round); B04 = accepted_with_findings "
                 "(all six findings addressed); B05 = rejected (2xP1/5xP2/3xP3) with the P1s and P2s fixed "
                 "and the residuals registered, then a verification round = rejected with a LIVE P0 in the "
                 "author's own fix (the SQL filter ran before the Python guard), disposed of; B01/B03/B06/"
                 "B07 = accepted_with_findings, all disposed of; B08 = accepted_with_findings (7 findings, "
                 "disposed of) after a byte-identical probe re-run and an audit-hook tripwire; B10 = four "
                 "rounds: accepted_with_findings (increment 1), REJECT (batches 1-2: a P0 that was the "
                 "author's own misfiled crash path plus a false declaration the author's test had PINNED), "
                 "REJECT (r2 dispositions: one live P2 of the same family), and finally "
                 "APPROVE_WITH_FINDINGS (r3 dispositions) - all findings disposed of"),
        "R4": ("DELIVERED 2026-09-18 and independently reviewed (B.VR-r4 = approve_with_findings "
               "0xP0/0xP1/4xP2/4xP3, all eight disposed of). The REAL consumer entry point was run "
               "read-only: filing-fetch/scripts/fetch_filing.py --no-pause-worker without "
               "--allow-download, so the wiki action is `resolve`. L1/L2 exit 0 capture_ready with "
               "the canonical path of the Alibaba annual, content_sha256 e39fbf9c... (the digest "
               "B08 level 2 derived from the real bytes) and 4,172,424 bytes; the wiki side said "
               "outcome reused_existing, qualification.label verified_input and policy_hash "
               "c773099b... (same as runtime-policy show in A06-2). Controls: FY2019 -> not_found, "
               "unknown company -> identity_error. 11/11 invariants; out of 12,476 catalog-dir "
               "entries exactly one changed (catalog.sqlite3-shm mtime at the same 32,768 bytes, "
               "recorded and NOT attributed). The write surface was read out of the code first and "
               "then CORRECTED by the review: the resolve path passes the READ-ONLY reader "
               "(cli.py:1193; reader.py:165/188), so no mkdir/WAL/migration/commit occurs, and the "
               "worker-pause scope is never built on the reuse branch (--no-pause-worker is inert). "
               "Product boundary registered: F-BAR-12 (a reused document's derived artifacts are "
               "not reusable)"),
        "R5": ("DELIVERED 2026-09-18 and independently reviewed (B.VR-r5 = approve_with_findings "
               "0xP0/1xP1/1xP2/3xP3, all five disposed of). The three dropbox_stock documents B.AR "
               "skipped were located through the ratified A05 output (no new production read) and "
               "their bytes verify 3/3 (543/567/567) - all three are *.source.json SIDECARS indexed "
               "as annual_report documents, i.e. the F-BAR-1 family. The owner accepted hydration; "
               "measurement then showed NONE took place (AllocationSize 4096 before the read while "
               "EndOfFile is 543/567), so the authorisation was not used. Two instrument defects "
               "were found and corrected inside the step: Python's st_file_attributes cannot see "
               "the cloud state inside the Dropbox tree (0x20 vs PowerShell 0x420 and fsutil's "
               "reparse tag 0x9000601a), and the author's 'locality is undeterminable' was an "
               "UNDER-claim that GetFileInformationByHandleEx answers"),
        "R6": ("REGISTERED 2026-09-18 in risk-and-stop-rules.md section 7: every zero-write claim in "
               "this run is bounded to METADATA observation (size, mtime_ns, -wal/-shm, repo "
               "worktree, src tree fingerprint) - a write that preserves size and mtime is "
               "invisible to it, and this host offers no OS-level write observer. The two candidate "
               "strengthenings (a full-file sha256 of the 46.3 GiB production DB; USN/ETW write "
               "auditing) are registered with their costs and limits and were NOT performed"),
        "R3": ("DELIVERED 2026-09-18 (revenue-forecast 3825db2) and independently reviewed: the fifth root "
               "joins by CONFIG ONLY inside an isolated catalog (r4_fifth_root, kind directory + the "
               "registered sidecar_filing_v1 adapter + read_only + reusable_for_filing, priority 50; the "
               "scanner's own INSERT wrote the roots row with no product-code change). Measured: query 2 "
               "documents, resolve(mode=exact) reused_exact twice with capture_ready [true], "
               "read_verified_bytes verified twice (59 B, sha256 = the file on disk), "
               "query_filing_candidates 2 rows; unregistered adapter CFG-01 fail-closed, unknown root id "
               "refused on both branches, deny -> missing. Invariants 7/7, --verify 4/4, mutation 5/5 "
               "KILLED, local CI unit 799 / contract 1905 passed + 8 skipped. Review B.VR-r3 = "
               "approve_with_findings (0xP0/0xP1/3xP2/3xP3), all six disposed of. It is NOT a production "
               "registration: the production catalog was never written (49,677,344,768 B and its mtime_ns "
               "unchanged), so the four-real-roots-plus-fifth coexistence remains unverified. The two "
               "boundaries it measured are registered, not fixed: F-BAR-10 and F-BAR-11"),
        "B.AR": ("EXECUTED and reviewed: the read-only manifest run (10 commands / 102 invocations) plus an "
                 "independent identity/hash re-derivation from the originals (6/6 digests, 18/18 derived "
                 "artifacts, 8/12 documents confirmed against the exchange registry snapshots). Its review "
                 "returned APPROVE_WITH_FINDINGS with authorization OVERREACH: the executed set was not the "
                 "manifest as written (an extra command, --limit 100 against <=50, 102 invocations against "
                 "budget 25, 85 retries against the stop rule, and approval.by = null). The owner delegated "
                 "the adjudication to the authoring session, which ratified the read-only reading, kept the "
                 "overreach on the record, and turned the bounds into mechanical refusals (5/5 selftest) "
                 "plus a machine-checkable compliance read. Unfinished by AUTHORIZATION, not by choice: "
                 "the fifth-root half was later DELIVERED inside an isolated catalog (see R3 below, "
                 "owner's choice of 2026-09-18); a cross-repo end-to-end call still needs an approved "
                 "command; the cloud-synced sample was deliberately not hashed (reading a placeholder "
                 "hydrates it)"),
        "G7": ("read-only manifest commands: APPROVED by the owner's in-session instruction, executed, and "
               "the over-budget/extra-command part ADJUDICATED (ratified with the violation on the record) "
               "after the independent review refused to treat it as compliant"),
        "G8": ("two levels, both EXERCISED: level 1 = a temp isolated catalog; level 2 = an isolated root "
               "referencing a REAL filing directory read-only, with 4,172,424 verified bytes, a tamper "
               "probe returning zero bytes, and before/after evidence that the real files and the "
               "production catalog metadata did not move. Residual risk stated by the review: a "
               "size- and mtime-preserving write to the production catalog would be invisible to a "
               "metadata-only rule"),
        "B01": ("implemented as 0e28d99 and REVIEWED (accepted_with_findings); dispositions in be2e4ed. The "
                "resolver calls policy._effective_reusable instead of keeping a kind-only copy, candidate "
                "selection requires membership (no empty-set escape), config admission refuses quoted "
                "booleans (CFG-08) and the declaration test normalises document_kind the way the classifier "
                "does. Production blast radius is none (every shipped root was already effectively reusable). "
                "Residual: the policy_2x copy of the rule cannot be removed (S-3 freezes the export path), so "
                "agreement is asserted by a case instead of guaranteed by one implementation - and the "
                "consumer-side hash that filing-fetch pins is now frozen in addition to the resolver-side one"),
        "B03": ("implemented as 5ab0779: read_verified_bytes reads a version ONCE, digests exactly the buffer "
                "it returns and refuses everything else inside the contract's five error values, closing the "
                "byte-level hard gate S-10 deferred to the read path. Registered limits: the design's middle "
                "tier (read an EXISTING controlled snapshot) has no object to read in this repository, so it "
                "is unimplemented and bytes_source='snapshot' stays unreachable; ACL denial was not "
                "synthesised separately; the cloud-placeholder case uses synthetic stat attributes; the "
                "symlink case skips on this host; consumers that still open canonical_path themselves are "
                "B07's to wire"),
        "B04": ("implemented as acceptance + findings with NO product change and reviewed (B.VR b04 = "
                "accepted_with_findings, 2xP2 + 4xP3 addressed). Design goal 1-2 verified; goal 3 is "
                "CONDITIONAL: a same-path overwrite destroys the old bytes, and with a second copy the old "
                "reference still resolves. The owner chose option (iii), the contract-level known "
                "limitation (S-12), recorded in the run directory only; F-B04-2 registers the silent "
                "MISSING when only the PDF is moved without its sidecar"),
        "B05": ("implemented and then rejected by its own review; the P1s and P2s are fixed with regression "
                "cases and the read side exposes provenance/conflicts/metadata_status. The response-level "
                "blocked verdict is NOT in B05 (owner S-13 assigns it to B06/B07). Residuals: B-VR05-09 "
                "(wording) and B-VR05-10 (field names appear in provenance; a low-entropy value's 12-hex "
                "hash can be brute-forced) - registered, not silently dropped"),
        "S-1_test_files": "APPROVED (F10/F11); F10 landing used by the four new contract files (6+30+4+9 cases)",
        "S-2_R1_R4_out_of_B": "DECIDED - R-1/R-4 stay outside B as separate work packages",
        "S-3_export_path": "DECIDED - export_policy_2x untouched, payload hash frozen (B-payload-hash still NOT executed)",
        "S-4_consumer_side": "DECIDED - belongs to phase C, B does not sign it",
        "S-5_isolated_copy": "DECIDED - two levels; L1 can start now",
        "S-6_fourth_round": "done - five review rounds were run in total (rev4 then rev5/rev6)",
        "S-7_ratchet_edit": "DECIDED - NOT allowed; table unchanged and asserted by test_r4b02_complexity_ratchet_table_is_not_edited",
        "S-8_N1": "DECIDED - N-1 stays outside B, registered as a cross-repo protocol item",
        "S-10_byte_hard_gate": ("APPROVED as recommended (owner 2026-09-12): B02 implements the segment-3 hash "
                                "equality as a preference with per-candidate diagnostics; the byte-level hard "
                                "gate ('serve verified bytes or fail explicitly') belongs to B03's read path. "
                                "The authoritative a-d difference list lives in evidence/b02-implementation.md "
                                "section 3 and nowhere else"),
        "S-11_budget_status": ("APPROVED as recommended: budget exhaustion maps onto the pre-B02 row plus a "
                               "trace entry, no sixth status value; the counters reset per request and "
                               "cancellation stays sticky"),
        "S-12_same_path_overwrite": ("APPROVED as recommended: option (iii), a contract-level known limitation "
                                     "(the old bytes are physically destroyed by an in-place overwrite); a "
                                     "byte-snapshot remedy would be a separate work package. Recorded in the run "
                                     "directory only, per the owner's instruction not to touch the frozen "
                                     "phase-A artifacts"),
        "S-13_response_blocked": ("APPROVED as recommended: the response-level blocked verdict moves into B06/B07; "
                                  "B05's scope was NOT widened, it delivers the field-level facts and the "
                                  "read-side metadata_status"),
        "BAR_increment_2026-09-19": ("DELIVERED as company-wiki f39bd5a under the owner's ruling (4) and "
                                    "verified the same way as its predecessors: the second fetchall gets a "
                                    "named retryable per-document outcome, the record-transaction guard is "
                                    "driven by an unambiguous fault injection instead of being inferred "
                                    "from its siblings, every mutant is red-before-green in a temporary "
                                    "copy, the matrix is 17/17 KILLED with the repository untouched, "
                                    "contract 1939 passed + 8 skipped, unit 799 passed, and the FC-1204 "
                                    "coverage + complexity ratchets pass on a fresh measurement whose "
                                    "module numbers are recorded (normalizer.py 60.5 against a frozen 53). "
                                    "Two of the author's own record defects were corrected here rather "
                                    "than carried forward (F-COV-01, and a duplicated mutant id with an "
                                    "ambiguous-anchor class behind it), and one pre-existing live-data "
                                    "flake was measured and registered without being fixed (F-ZR409-01). "
                                    "Independent review: see pending_review"),
        "implementation_go_ahead": ("GRANTED (owner 2026-09-12, second batch); B02, B04, B05 and B01 have landed "
                                    "and B01 is the next review round"),
    },
    "actual_side_effects": (
        "Unlike the design-only rounds, this run has MODIFIED PRODUCT FILES in company-wiki: "
        "src/company_wiki/source_catalog/service.py, src/company_wiki/source_catalog/scanner.py (the B05 merge "
        "path), src/company_wiki/source_catalog/resolver.py, plus four new files under tests/contract/ "
        "(test_r4b02_candidate_selection.py, test_r4b04_reference_stability.py, "
        "test_r4b05_metadata_provenance.py, test_r4b01_field_owner_alignment.py) - all inside the authorized "
        "file scope (F1/F2/F3/F10) and pushed (cab1fd6 ... 9826b3c, then 0e28d99 for B01). Executed locally: "
        "pytest (including the full suite with coverage), ruff, git worktree, read-only probes over synthetic "
        "tmp fixtures (including evidence/b01_fc1001_probe.py, which builds the FC-1001 lake in a temp "
        "directory to explain the F-B01-7 gate failure), and mutation harnesses that restore the product files "
        "to the same digest. DECLARED, not evidenced (G5 closed 2026-09-15 by an independent read-only "
        "observation, reviews/G5-boundary-observation.json): no CLI of the product was executed by the "
        "authoring session, and no network/download/LLM egress, task registration, worker action or "
        "deletion was performed. This host keeps no launch log, so that half is UNFALSIFIABLE - no "
        "read-only instrument can confirm or refute it - and it is recorded as a declaration rather than "
        "a result. EVIDENCED: no persisted write to the production catalog - catalog.sqlite3 "
        "(49,677,344,768 B) still carries its 2026-09-08 22:23:21 mtime and -wal is 0 bytes (main DB "
        "independently re-confirmed 2026-09-15). NOT evidenced either way: whether a session opened the "
        "catalog read-only, because -shm moves on this host with no session acting (the observer measured "
        ">=4 advances in 2.5 minutes while running only Get-Item, and the OS refused to hash -wal/-shm "
        "because another process held the catalog open), so -shm movement reproduces mechanically but "
        "cannot attribute. Known opens inside the window: the mandatory pre-push gate of every push (its "
        "real-data suite opens the production catalog READ-ONLY), the 22:00 daily task, and several "
        "pre-existing wiki tests. At the time of writing that gate was RED for the F-B01-7 reason, so the "
        "B01 run-directory commits were local; the owner later resolved that blocker (decision A) and "
        "every commit of this run is pushed - never with --no-verify. Several pre-existing wiki tests "
        "also open the production catalog read-only when the suite runs (known limitation, attributed in "
        "phase A)."
    ),
    "failed_or_unknown": [
        "BLOCKER (F-B01-7): after B01 landed, revenue-forecast's pre-push gate (real-data suite) is RED on tests/test_fc1001_isolated_lake.py::test_corruption_variants_fail_closed[sidecar_missing]. Root cause located with a six-way probe (evidence/b01_fc1001_probe.py): that case NEVER passed for the reason it names - the rejection came from the resolver's old kind-only reuse gate under the case's inline synthetic config (default reusable_root_kinds=['company_raw'] against a 'directory' root), and under the production-shaped config the same document resolves BOTH before and after B01 (matches=1), including after a re-scan and with sidecar_suffixes declared. So B01 removed an incidental cover, not an identity check (the entity gate still rejects as before), and the case's fail-closed expectation has never held in production - the real gap it exposes (a document whose sidecar is missing must not default to a trusted filing) belongs to B06 by the design text. The fix is a one-case correction in revenue-forecast, which is OUTSIDE phase B's file scope, so it is with the owner (options A-D in findings F-B01-7). Until then the revenue-side commits stay local; the gate was NOT bypassed",
        "B03/B06/B07 are still design-only: the byte-level hard gate ('serve verified bytes or fail explicitly') does not exist yet, so a preferred copy whose bytes drifted is served on the catalog's claim (S-10's other half, assigned to B03), and no response-level blocked verdict exists yet (S-13, assigned to B06/B07)",
        "B-payload-hash is now EXECUTABLE and PASSES (findings F-B07-1): the gate's stated blocker ('reading the value needs an unapproved CLI') is false - cli._policy_export_payload is a pure function - so evidence/b07_payload_baseline.py compares the payload byte for byte between a read-only worktree of the phase-A frozen revision 7d4852f and the current tree with a FIXED project_root, and the two are identical (canonical_sha256 bd1a359f... on both sides, 1216 bytes). The absolute hash remains machine-scoped (it embeds each root's absolute path_ref - F-B01-9), so what is portable is the comparison, not the value; B07 re-runs the script to confirm",
        "the L01-L12 mechanism-layer baseline exists as A06-D0 (787 unit + 1748 contract passed / 7 skipped); the B-side cases cover L01-L04 plus budget/cancel/no-network, the review regressions and the B01 alignment property, not the whole matrix",
        "B01's residual: the resolver imports the private policy function _effective_reusable - recorded in F-B01-6; promoting it to a public API would touch the export payload, and B-payload-hash is not executable",
        "B05's residuals: B-VR05-09 (flat-shape wording, 35 vs 30 complexity) and B-VR05-10 ('no raw text' holds for values only - injected canary key NAMES appear as fields - and a low-entropy value's 12-hex hash is brute-forceable)",
        "N-1 support is undefined on both sides and is therefore registered as a cross-repo protocol item, no longer part of B07's completion",
        "handbook section 3 run structure is still partial: card.json, baseline.json, data-manifest.json, requirements.csv and oracle/ are absent",
        "G5/G6/G7/G8 remain owner/operator items",
        "revenue-forecast dirty=0 is incomplete: three .tmp-zr408-unit* directories are unreadable (permission denied), so git cannot enumerate them",
        "test_dbx05_symlink_escape_rejected skips on this host (symlinks not supported), so the symlink-escape control did not run here",
        "the current acceptance cases run on tmp fixtures; the real four-root and cloud-placeholder behaviour still needs the isolated copy (G8)",
        "R3's two product boundaries were FIXED on 2026-09-18 under the owner's ruling (F-BAR-10: an adapter-declared root is scanned through its adapter regardless of the activation snapshot, with ScanReport.strategy making the dispatch observable, so .source.json sidecars are no longer indexed as documents on such a root; F-BAR-11: the byte entry point now honours the same reusable-root policy as the decision path, keyed on the SAME value - the location's root_id). The original measurements stay in this record as the pre-fix state: with no runtime_policy.json a declared root was walked by the v1 path (mutant M5), and read_verified_bytes served a reusable_for_filing: false root's bytes because it gated on containment only",
        "the F-B10R2 family's own remaining limits, registered rather than silently closed (2026-09-19): in backfill_text_fingerprints the recording call (record_fingerprint_outcome) is NOT guarded, because a database that cannot accept the outcome row is a hard stop and swallowing it would drop the record silently; and the two BATCH-level reads that sit outside the loop (select_fingerprint_batch, fingerprint_status) stay fatal by design, since they cannot be attributed to one document",
        "the mutation matrix itself carried two author bookkeeping defects found and fixed on 2026-09-19: one mutant id was declared TWICE (a duplicated dict key silently drops the earlier definition, so the count still looked right) and an anchor appearing more than once would have mutated whichever copy came first. barfix_mutations.py now refuses both, plus a replacement text that is already present (a no-op mutant); the one-off audit scripts written for this were deleted so the record does not carry two drifting copies of the same check",
        "R3 does NOT cover the coexistence of the four production roots with a fifth root in the production catalog: the isolated catalog is empty by construction, so the four-root legs still rest on the earlier B.AR evidence, not on this run",
        "R6 (registered 2026-09-18, risk-and-stop-rules.md section 7): every zero-write claim in this run is bounded to METADATA observation (size, mtime_ns, -wal/-shm, repo worktree, src tree fingerprint) - a write that preserves size and mtime is invisible to it, and this host offers no OS-level write observer. The owner declined to harden it on 2026-09-18, so it stands as registered, not as an outstanding action",
        "F-COV-01 (the author's own record defect, corrected 2026-09-19): the 2026-09-18 coverage evidence anchored the RAW sha256 (8cf4a793..., 1,138,137 B) of a working-tree coverage.json that was not retained anywhere - the repository's tracked copy is the 1,014,394 B file from 2026-08-17 - and coverage.py embeds meta.timestamp and meta.version, so a raw file hash is not reproducible even when the measurement is identical. Replaced by two anchors plus the retained file: raw sha256 ae00af2e... (1,138,400 B, 95 files), measurement_sha256 e223dab3... over the canonical JSON of files + totals only (recomputable by evidence/coverage_anchor.py), and the measured report itself stored as evidence/barfix6-coverage.json. Any earlier citation of the 8cf4a793... anchor should be read as superseded",
        "F-ZR409-01 (an EXISTING case's host sensitivity, measured, registered and NOT fixed - fixing it is outside the step's authorization): tests/contract/test_zr409_fourth_root_real_journeys.py::test_c2_journey_dayu_only_real_sample compares two (name, size, mtime_ns) fingerprints of the LIVE dayu_portfolio root taken milliseconds apart, and st_size of a top-level child on this host is not stable: a 240 s read-only watch (49 samples, evidence/zr409-live-root-watch.json) caught five child directories flipping 4096 -> 0 with mtime_ns unchanged, the cloud-placeholder signature of the same family as R5's F-BAR-13. It failed once inside the full-suite coverage run on 2026-09-19 and passed when re-run alone on the identical tree; the production DB's size and mtime_ns were unchanged throughout. CI's contract step excludes this file and the coverage step tolerates failures, so the gate is unaffected - but the case is a real flake against live data, and it must NOT be read as evidence about the 2026-09-19 code change, which touches only the backfill path that this case never enters",
        "R4/R5's own narrower claims, now scoped in the prose rather than left to read wider: the `companies` digest is relative path + size for files only (a same-size overwrite or a new empty directory would not appear); `repos_unchanged_during_run` compares `git status --porcelain` (the harness's own five evidence files are untracked, so a content rewrite of one would not appear - the pyc caches are digested separately and the wiki children now run with PYTHONDONTWRITEBYTECODE=1); the catalog-dir -shm movement is recorded and NOT attributed",
        "two instrument defects were found inside R5 and corrected there (Python's st_file_attributes is blind to the cloud state inside the Dropbox tree; the author's 'locality is undeterminable' was an under-claim). Both are now measured facts in the record, but a reviewer should treat any EARLIER statement of those two as withdrawn",
        "F-BAR-12 (registered, not fixed): a document reused through the cross-repo path reports bundle_status available while valid_handles is empty, because its derived artifacts are unusable (normalized: artifact_status_not_completed; summary: artifact_source_sha_missing). The share of the production catalog in that state is NOT quantified",
    ],
    "next_step": (
        "The owner's four rulings of 2026-09-18 are EXECUTED, which is what shrank this list: "
        "(1) 'fix' = the three measured product boundaries F-BAR-10 / F-BAR-11 / F-BAR-12 plus "
        "the newly found F-BAR-14 - delivered; (2) 'do not verify' = the coexistence of the four "
        "production roots WITH a fifth root in the PRODUCTION catalog - closed by owner "
        "decision, deliberately NOT verified (no 46.3 GiB copy, no production write); (3) 'do "
        "not harden' = R6, the zero-write claim beyond metadata observation - closed by owner "
        "decision, the registered bound stands; (4) 'fix' = the F-B10R2-MISSINGFILE family plus "
        "the two scripts/ readers - delivered, and completed on 2026-09-19 with the SECOND of "
        "the two fetchall calls and with the record-transaction guard now DRIVEN by fault "
        "injection instead of justified by its siblings' shape (the earlier 'the probe covers "
        "it' statement was corrected: the probe drives the generic handler's ingest, a "
        "different site). What still needs the OWNER before anything moves: (A) whether the "
        "same per-document guard shape should be given to the five remaining sibling "
        "_atomic_write loops, which are NOT per-document sites (summarizer.py, "
        "section_extractor.py, llm_summarizer.py, focus_cleanup.py, service.py); (B) whether to "
        "UNTRACK the build outputs coverage.json / .coverage, which every coverage measurement "
        "rewrites - they are tracked today, so every run leaves the tree dirty; (C) F-BAR-12's "
        "other half: a reused document's derived artifacts are still unusable, and repairing "
        "them needs an approved normalize/summarize RE-RUN, i.e. a production write; (D) "
        "whether the gate's syntactic ratchets should become a dataflow check, given the four "
        "measured bypass shapes recorded in GATE_BOUNDARIES. OPERATOR: the G5/G6 records remain "
        "operator items. A further B10 increment requires no owner input but also no further "
        "value: the chain is single, declared and gated"
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
