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
              "B02, B04, B05, B01 (reviewed) and B03 landed; B06/B07 still design-only"),
    "step": ("B01's review came back accepted_with_findings (1xP1/3xP2/2xP3) and every P1/P2 is disposed of in "
             "be2e4ed - the P1 was the author's own acceptance defect (it froze the resolver-side policy export "
             "and called it cross-repo, while filing-fetch consumes the policy_2x payload) and the P2s include a "
             "real fail-open in config admission (a quoted boolean was admitted and read as reusable). B03 then "
             "landed as 5ab0779: SourceResolver.read_verified_bytes serves a version's bytes or fails "
             "explicitly, which closes the byte-level hard gate that decision S-10 deferred to the read path"),
    "last_completed_step": (
        "B04 closed after its focused review (all six findings addressed, plus an author-side mutation "
        "harness). B05 implemented in three commits, rejected by its own review, and its P1s and P2s fixed "
        "(b6a8442, 9826b3c) with the two residual items registered. B01 then landed (0e28d99), was reviewed "
        "independently (accepted_with_findings) and its findings were disposed of in be2e4ed: (a) P1 "
        "B-VR01-01 - the frozen cross-repo hash was the WRONG artifact (export_policy v1 instead of the "
        "policy_2x payload filing-fetch pins); both are now frozen with their roles and a new case compares "
        "the consumer payload's reusable set with the resolver's OBSERVED behaviour on configs where an "
        "explicit flag contradicts the kind list, which a kind-only revert of the policy_2x copy now fails; "
        "(b) P2 - the record's causal sentence was false and is corrected to the measured mutation result; "
        "(c) P2 - the B05 declaration test did not normalise the way the classifier does, so a "
        "case-variant declared kind was downgraded to derived and manufactured a conflict (fixed per column: "
        "document_kind casefolds, free-text and date columns stay exact); (d) P2 - config admission accepted "
        "quoted booleans, so reusable_for_filing \"false\" was read as reusable (fail-open) and \"true\" "
        "skipped CFG-05/CFG-07 (fixed as CFG-08, in its own function because the frozen complexity entry for "
        "config.py caught the inline version at 50 > 46); (e) P3 - the empty-set escape in the candidate "
        "filter is gone, so an omitted or empty set means 'nothing qualifies'; (f) P3 - record precision. "
        "B03 then landed as 5ab0779: read_verified_bytes reads the file ONCE, digests exactly the buffer it "
        "returns, and refuses everything else inside the contract's five error values (out-of-root locator "
        "-> not_found before any read; cloud placeholder never hydrated; unreadable/interrupted/changed "
        "mid-read; the size ceiling; cancellation sticky) with the bytes and their evidence returned "
        "together. Measured: B01 acceptance 9 cases, B05 acceptance 10 cases, B03 acceptance 13 cases plus "
        "one host-limited skip, unit + contract neighbourhood 816 passed, ruff clean, both FC-1204 ratchet "
        "tables green, wiki pre-push gate green on both pushes."
    ),
    "current_gate": (
        "B03's independent review (one round per step, section 11), which also samples the B01 dispositions; "
        "then B06 -> B07. B06 must deliver both the response-level blocked verdict (S-13) and the "
        "sidecar/identity rule that F-B01-7 shows is missing; B07 owns the versioned read contract, "
        "including wiring consumers to read_verified_bytes instead of their own open() calls. No owner ruling "
        "is outstanding: S-10/S-11/S-12/S-13 were approved as recommended on 2026-09-12, and the working "
        "mode is the simplified one (only scope or risk questions go back to the owner)."
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
    ],
    "reviewer_assignments": {
        "note": ("recorded by the authoring session from outside the reviewer session; still only "
                 "process evidence - an operator-held assignment record is required (gate G6)"),
        "B.DR_rev1": {"reviewer_session_id": "7ad6f0f0-717a-4b25-a1bf-b3604b8953fe", "record": "reviews/B.DR.json"},
    },
    "authorization_needed": [
        "OWNER/OPERATOR: isolated copy for behavioural probes (gate G8) - see findings F-B00-3 for a two-level proposal",
        "OPERATOR: independent boundary observation and reviewer assignment records (G5/G6)",
        "OWNER: confirm the A05 sample list and the read-only command manifest (gate G7 + G4 for behaviour beyond --help)",
        "NO OWNER RULING IS OUTSTANDING for phase B: S-10/S-11/S-12/S-13 were approved as recommended on 2026-09-12 and the simplified working mode (section 11) is in force - only scope and risk questions go back to the owner from here",
    ],
    "gate_status": {
        "B.DR": ("rev1-rev6 all rejected; v0.1.6 was the correction pass and v0.1.7 only back-fills the B02 "
                 "implementation record (no design change); the ratchet table stays frozen (S-7)"),
        "B.VR": ("rev1 = rejected (2xP1/2xP2/3xP3); rev2/rev3/rev4 = accepted_with_findings and each round "
                 "falsified one of the author's justification sentences, now single-sourced; B02 closed by "
                 "the author's documented decision (no fifth prose-only round); B04 = accepted_with_findings "
                 "(all six findings addressed); B05 = rejected (2xP1/5xP2/3xP3) with the P1s and P2s fixed "
                 "and the residuals registered (no second round, section 11); B01 = implemented and awaiting "
                 "its one review round. Protocol ready (b-vr-protocol.md); L1 mechanism layer unblocked by "
                 "S-5, L2 real-byte layer still needs G8"),
        "B.AR": "not started",
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
        "to the same digest. NOT executed: any network/download/LLM egress, any product-data write, any DB "
        "write, task registration, worker action or deletion; no behavioural probe against the production "
        "catalog. The run directory IS pushed (origin/main) and every push ran revenue-forecast's mandatory "
        "pre-push gate, whose real-data suite opens the production catalog READ-ONLY and advances -shm "
        "(attributed in ../2026-09-11_r4-phase-a/boundary-audit.md); that gate is currently RED for the "
        "F-B01-7 reason, so the B01 run-directory commits remain LOCAL and no push was attempted with "
        "--no-verify. Several pre-existing wiki tests also open the production catalog read-only when the "
        "suite runs (known limitation, attributed in phase A)."
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
    ],
    "next_step": (
        "Resolve the F-B01-7 blocker with the owner (authorise the one-case correction in "
        "revenue-forecast's tests/test_fc1001_isolated_lake.py and register the sidecar-missing rule as a "
        "B06 acceptance item, or defer), then push the revenue-side commits. Then run B01's one independent "
        "review round (section 11), which also samples the B05 P2 fixes; then implement B03 (stable read "
        "bytes: a fixed handle or a controlled snapshot, streaming hashing, and the TOCTOU/"
        "cloud-placeholder/bad-byte/interruption cases) - B03 carries the byte-level hard gate deferred by "
        "S-10 - and then B06, which must deliver both the response-level blocked verdict (S-13) and the "
        "sidecar/identity rule that F-B01-7 shows is missing, then B07. Each step: F10 cases, one commit, "
        "the ratchet/coverage rerun, one independent review and one implementation record."
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
