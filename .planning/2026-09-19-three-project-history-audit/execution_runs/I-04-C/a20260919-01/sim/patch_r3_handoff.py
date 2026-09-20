"""r3 handoff patch: revision, true counts, carries and the downstream binding note.

Only handoff.json is rewritten; everything else stays as produced by the r3 runs.
"""

from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ATTEMPT, "handoff.json")


def main():
    with open(PATH, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    data["revision"] = ("v1.3 (r3: the round-2 review returned accepted_scoped with 3 "
                        "still-required items; all three are disposed)")
    data["reviewer_status"] = (
        "Round 1 = changes_required -> r2 revision -> Round 2 = ACCEPTED_SCOPED with 3 "
        "still-required items (error-code/timeout case; queue-crosses-budget boundary + "
        "queue cost; stale text and F-LK2 numbers) -> r3 revision (this package). The "
        "implementer wrote no verdict; review.md section 5 stays empty for the reviewer.")

    data["r3_dispositions"] = {
        "still_required_1_error_code": (
            "DISPOSED: FileLock now takes a `code` parameter; lease_lock() passes "
            "`lease_lock_timeout`, so the request phase reports code/action "
            "lease_lock_timeout and the cleanup phase reports "
            "cleanup_status=failed:lease_lock_timeout (sim/kernel.py). Four real timeout "
            "cases added: F-T1 (request phase, external holder really holds the lock), "
            "F-T2 (budget 0 => the lock is never attempted), F-T3 (cleanup phase), "
            "F-T4 (queue crosses the budget). The three doc sites (ADR-2, T13/code table, "
            "oracle sections) were already frozen with lease_lock_timeout and now match "
            "the implementation."),
        "still_required_2_queue_boundary": (
            "DISPOSED: F-T4 is the deterministic queue-crosses-budget case (6 enter-only "
            "participants, injected critical-section hold H=0.4 s, lock budget 1.0 s => 4 "
            "participants fail closed with lease_lock_timeout and zero writes; the winners' "
            "set equals the refcount set; no dangling lease or obligation afterwards). The "
            "(N-1)*H model and the fact that queueing consumes the download budget are now "
            "in decision.md ADR-2/section 14 F-I04C-12 and oracle.md R3-2, and F-T4 reports "
            "`budget_consumed_by_queueing`."),
        "still_required_3_hygiene": (
            "DISPOSED: decision.md ADR-6 table and section 6 summary now use "
            "lock_budget_for(x)=min(x,60); the section 10 ADR-10 row is marked superseded by "
            "the section 12 R1-R5 table; the claim 'never leaves a paused worker with nobody "
            "obliged' is formally withdrawn (R5 allows that fail-closed terminal state); "
            "oracle.md section 0 says the generation is a per-file counter (not monotonic) "
            "and section 7 uses min(phase budget, 60); the F-LK2 numbers are unified to the "
            "measured group finals [16,35,10,56,18] => lost [184,165,190,144,182] from "
            "evidence/lock-and-legacy.txt. Applied by sim/patch_r3_docs.py."),
        "OPEN-3_adopted": (
            "ADOPTED as advised: LOCK_MAX_SECONDS=60 is kept but renamed to 'the waiting cap "
            "constant introduced by this card'; it is not a new budget (the request-phase "
            "budget is normally 900 s), its real effect is to cap the cleanup segment "
            "(C up to 85 s) and short deadlines, and a non-positive budget refuses to wait "
            "(proven by F-T2). Listed for the owner together with 'may worker-pause stay "
            "inside the lock?'."),
    }

    data["true_counts"] = {
        "protocol_suite": "cases_in_log=28 pass=28 fail=0 harness_error=0 failing_checks=0 (evidence/failures.txt)",
        "lock_and_legacy_suite": "cases_in_log=7 pass=7 fail=0 harness_error=0 failing_checks=0 (evidence/lock-and-legacy-failures.txt)",
        "static_adr11": "S1-S4 all PASS (evidence/static-adr11.txt)",
        "superseded_counts": "v1 '10 PASS / 6 failing' and the v1.2 '24 PASS' figures are superseded by the r3 counts above; review.md section 2(a) keeps the original wrong sentence with its correction",
        "F_LK2": "5 runs, finals [16, 35, 10, 56, 18], lost [184, 165, 190, 144, 182] (final evidence round); reviewer rerun 34/200; an earlier round even produced 261/200 because the unlocked write is itself non-atomic -- QUALITATIVE only",
    }

    data["results"]["protocol_passed"] = [
        "F-L1", "F-L2a", "F-L2b", "F-L2c", "F-L2c-dead", "F-L2d", "F-L3", "F-L4a", "F-L4b",
        "F-L4c", "F-L4d", "F-L4e", "F-W1", "F-W2", "F-W4", "F-W4b", "F-W5", "V4-a", "V4-e",
        "V4-f", "F-W7", "F-L2e-stale", "F-L2e-fixed", "F-GEN", "F-T1", "F-T2", "F-T3", "F-T4",
    ]
    data["results"]["lock_atomicity"]["F-LK2_unlocked"] = data["true_counts"]["F_LK2"]
    data["results"]["lock_atomicity"]["F_LK3_holder_crash"] = (
        "parent reacquired in 0.0004 s after the holder died with exit 90; no cleanup action "
        "needed (re-verified in the r3 run)")
    data["results"]["lock_timeout_boundary"] = {
        "F-T1": "request phase, external process really holds the lease lock, request_budget=0.05 => code/action lease_lock_timeout, zero writes, zero CLI, state file byte-identical, wait bounded",
        "F-T2": "request_budget=0 => same fail-closed outcome and the lock is never even attempted (no lock_acq journal entry)",
        "F-T3": "cleanup phase => action release_fail_closed with cleanup_status=failed:lease_lock_timeout, obligation and owner evidence preserved, worker still paused",
        "F-T4": "queue crosses the budget (H=0.4 s, budget 1.0 s, 6 participants) => 4 participants fail closed with lease_lock_timeout and zero writes; successful set == refcount set; no dangling lease or obligation at the end",
    }
    data["results"]["queue_cost"] = (
        "queue wait ~ (N-1)*H; F-T4 reports budget_consumed_by_queueing (P0 0.000 s, P2 0.571 s); "
        "F-L2d's 8-way run reported max_lock_wait 9.87 s and a 13.2 s phase wall")

    data["not_granted"] = [
        "production implementation (this is a design card; I-04-D ports it)",
        "real provider / real worker / real wiki concurrency",
        "the DECLARED liveness model's equivalence to a real OS probe (see the I-04-D preconditions)",
        "POSIX (fcntl.flock) and SMB/NFS lock semantics (never exercised)",
        "real PID-reuse detection via GetProcessTimes (never exercised)",
        "multi-threaded scopes inside one process",
        "any claim that a user pause issued during our scope is protected (see O-2 / F-L4a LIMITATION)",
        "the transferred-owner invariant in ADR-10e has NOT been proven under a concurrent "
        "release; it is an obligation for I-04-D (see carries)",
    ]

    data["open_questions"] = [
        "OPEN-3 (owner): confirm the naming of LOCK_MAX_SECONDS=60 as 'the waiting cap constant "
        "introduced by this card' (it is not a new budget; it caps the cleanup segment and short "
        "deadlines and refuses to wait at <=0), and decide whether worker-pause may stay inside "
        "the lock (this card keeps it inside: otherwise two participants could both believe they "
        "are the first pauser)",
        "O-1: with no next participant a crashed obligation leaves the worker paused; recovery "
        "needs a later acquire or a human; I-04-D must ship the manual release steps",
        "O-2 / F-L4a: with the current company-wiki API a user pause issued during our scope is "
        "indistinguishable and our cycle close resumes it; needs a wiki-side pause-origin signal",
        "O-5: unique .tmp name for the refcount write (I-04-D minimal change)",
        "O-9: the DECLARED liveness model must be replaced by the real probe (or lifetime mode) "
        "before I-04-D can claim any concurrency qualification",
    ]

    data["carries"] = [
        "I-04-D MANDATORY PRECONDITION (O-9): rerun every concurrent case with the real OS probe "
        "or in lifetime mode; the DECLARED liveness model used here is a simulation input and its "
        "equivalence to a real probe is NOT granted",
        "I-04-D: ship the manual release guidance for the R5 terminal state (paused with no "
        "attributable obligation): a doctor/stderr instruction plus the raw owner record it must "
        "print, so a human can resolve it without guessing",
        "I-04-D: keep ADR-10e as an explicit invariant -- after an ownership transfer the owner "
        "record must still be provably dead-able; a transfer that points at a lease which is "
        "about to exit is a protocol defect and must fail closed (R5)",
        "I-04-D (O-2): if the owner wants user pauses protected, company-wiki must expose a "
        "pause-origin signal (pause_origin); until then the F-L4a LIMITATION stands",
        "I-04-D: unique .tmp name for the refcount write (O-5)",
        "I-04-E: the product envelope still lacks probe elapsed and the cleanup PHASE wall clock",
        "standing rule: the cleanup PHASE wall clock is reported, never bounded by an acceptance cap",
        "DOWNSTREAM BINDING: revenue-forecast HEAD moved 4753fda -> 7d7ea1e; any downstream card "
        "bound to 4753fda must be REBOUND before it runs",
        "any change to the I-04-A frozen values (C, epsilon, B) requires returning to I-04-A",
    ]

    data["next_action"] = (
        "Round-3 confirmation by the reviewer (three still-required items disposed, see "
        "review.md section 6). Then I-04-D ports the protocol and MUST carry: (1) O-9 real-probe "
        "or lifetime rerun of every concurrent case; (2) the R5 terminal state manual-release "
        "guidance (doctor/stderr + the raw owner record it must print); (3) the ADR-10e invariant "
        "'a transferred owner must remain provably dead-able'; (4) O-2 pause-origin signal from "
        "company-wiki if user pauses are to be protected; (5) the OPEN-3 decision (60 s waiting "
        "cap naming, and whether worker-pause may stay inside the lock). Also rebind any "
        "downstream card pinned to revenue-forecast 4753fda: HEAD is now 7d7ea1e.")

    with open(PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1, sort_keys=True)
    print("handoff.json updated: revision, r3 disclosures, counts, not_granted, carries, next_action")
    return 0


if __name__ == "__main__":
    sys.exit(main())
