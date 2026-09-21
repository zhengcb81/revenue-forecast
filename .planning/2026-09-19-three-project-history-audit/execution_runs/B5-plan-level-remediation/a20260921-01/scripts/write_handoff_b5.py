"""Generate handoff.json for B5+B6. Runs only after all six batch evidence.json exist.

status is review_pending by construction: the implementer never signs acceptance.
"""
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
START_HERE = os.path.join(PLAN, "execution_v2", "START_HERE.md")

PRE_SHA = "1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835"
POST_SHA = "e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557"
REF_SHA = "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252"

BATCHES = [("M05-M08", "M05", ["M05", "M06", "M07", "M08"]),
           ("M09-M12", "M09", ["M09", "M10", "M11", "M12"]),
           ("M13-M16", "M13", ["M13", "M14", "M15", "M16"]),
           ("M21-M24", "M21", ["M21", "M22", "M23", "M24"]),
           ("M25-M28", "M25", ["M25", "M26", "M27", "M28"]),
           ("M29-M31", "M29", ["M29", "M30", "M31"])]

# measured by scripts/ast_gate_scan.py (self-tested against M17-M20 positive / M29-M31 negative)
ALREADY_GATED = {"M09-M12", "M21-M24"}


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def entry(relp, desc):
    p = os.path.join(ATT, relp)
    return {"path": relp, "description": desc,
            "bytes": os.path.getsize(p) if os.path.exists(p) else None,
            "sha256": sha_file(p) if os.path.exists(p) else None}


batch_ev = {}
missing = []
for label, rep, cards in BATCHES:
    p = os.path.join(ATT, label, "evidence.json")
    if os.path.exists(p):
        batch_ev[label] = json.load(open(p, encoding="utf-8"))
    else:
        missing.append(label)
if missing:
    print("NOT READY - missing:", missing)
    sys.exit(3)

propagation = {}
for label, rep, cards in BATCHES:
    ev = batch_ev[label]
    arms = ev.get("arms", {})
    rollup = ev.get("arm_rollup") or {}

    def rc(k):
        """Two batch evidence schemas are in use: flat {arm: {rc: N}}, and per-card nested
        {arm: {CARD: {raw_rc_from_process: N}}} with an `arm_rollup` summary. Read both; return a
        value only when every card agrees."""
        a = arms.get(k)
        if isinstance(a, dict):
            if isinstance(a.get("rc"), int):
                return a["rc"]
            vals = [c.get("raw_rc_from_process") for c in a.values() if isinstance(c, dict)]
            vals = [x for x in vals if isinstance(x, int)]
            if vals and len(set(vals)) == 1:
                return vals[0]
        r = rollup.get(k)
        if isinstance(r, dict):
            vals = [x for x in (r.get("rc_values") or []) if isinstance(x, int)]
            if vals and len(set(vals)) == 1:
                return vals[0]
        return None

    def per_card(k):
        a = arms.get(k)
        if isinstance(a, dict) and not isinstance(a.get("rc"), int):
            out = {c: d.get("raw_rc_from_process") for c, d in a.items() if isinstance(d, dict)}
            return out or None
        return None

    propagation[label] = {
        "cards": cards,
        "runner_before": (ev.get("runner_before") or {}).get("sha256"),
        "runner_after": (ev.get("runner_after") or {}).get("sha256"),
        "already_gated_before_this_card": label in ALREADY_GATED,
        "arms_rc": {"E": rc("E"), "F": rc("F"), "B": rc("B"), "G": rc("G")},
        "arms_per_card": {k: per_card(k) for k in ("E", "F", "B", "G")},
        "arms_expected": {"E": 0, "F": 3, "B": "measured (unconstrained)", "G": 2},
        # arm B is a MEASUREMENT, not an expectation: only E/F/G are checked
        "arms_match": (rc("E") == 0 and rc("F") == 3 and rc("G") == 2),
        "arm_b_measured_rc": rc("B"),
        "historical_runner_already_gated_field": ev.get("historical_runner_already_gated"),
        "arm_card_matrix": ev.get("arm_card_matrix"),
        "mutated_case": (arms.get("F") or {}).get("mutated_case") if isinstance(arms.get("F"), dict) else None,
        "unmet_prerequisites": ev.get("unmet_prerequisites", []),
        "open_issues_count": len(ev.get("open_issues") or []),
        "boundaries_respected": ev.get("boundaries_respected"),
        "historical_writes": ev.get("historical_writes"),
    }

all_arms_ok = all(v["arms_match"] for v in propagation.values())
all_boundaries = all(v["boundaries_respected"] is not False for v in propagation.values())

handoff = {
    "card": "B5+B6",
    "title": "REM-21 cross-batch runner propagation / REM-22 rc code table freeze",
    "attempt": "a20260921-01",
    "attempt_root": ATT,
    "status": "review_pending",
    "implementer_signed": False,
    "implementer_never_signs_acceptance": True,
    "authority": {
        "document": "OWNER_DECISIONS.md",
        "sections": ["13 T1-8 (REM-21, TIER-1)", "13 T1-19 (REM-22, TIER-1)"],
        "tier": "TIER-1",
        "owner_authorized_form_REM_21": "propagate the exact-type-name comparison; only each batch's own copy; "
                                        "before/ keeps the old version; do NOT retro-change historical rc; "
                                        "do NOT touch frozen evidence; add a mutation arm per batch",
        "owner_authorized_form_REM_22": "freeze one rc code table into START_HERE.md; each batch carries a "
                                        "self-describing exit_code_legend; historical rc is not rewritten",
    },
    "summary": {
        "REM_22": "START_HERE.md already carried the frozen table (written before this card, verified by "
                  "T1-19/a20260920-01). This card APPENDED a measured registry of the real per-batch rc "
                  "codes with file:line evidence, the legacy deviation mapping, and one normative "
                  "ambiguity. Pure append: +74/-0 lines, frozen text intact.",
        "REM_21": "Exact-type-name per-case enforcement propagated into the copies of 6 batches. Measured "
                  "result: 4 batches genuinely lacked the gate (M05-M08, M13-M16, M25-M28, M29-M31) and "
                  "2 already had it (M09-M12, M21-M24); the latter received prerequisite 3 (the rc=2 "
                  "declaration-usability precedence) and the required counters, not a gate fix.",
        "prerequisites_all_four": "satisfied; none unmet",
    },
    "deliverables": [
        entry("oracle.md", "frozen expectations, with an appended Erratum 1 for the falsified arm-B prediction"),
        entry("binding.json", "pre-run binding: repos, anchors, per-batch interpreters/code roots, hashes"),
        entry("commands.json", "every unit with its real raw rc and the frozen exit_code_legend"),
        entry("changes.diff", "START_HERE.md append + the six runner diffs (regenerated from byte copies)"),
        entry("decision.md", "decision record incl. the corrected REM-21 scope (D-9)"),
        entry("PROPAGATION_CONTRACT.md", "the normative contract fixed before the batch workers were dispatched"),
    ],
    "evidence": {
        "start_here_append_proof": entry("evidence/start_here_append_proof.json",
                                         "APPEND_ONLY=true, difflib ['equal','insert'], +74/-0"),
        "boundary_verification": entry("evidence/boundary_verification.json",
                                       "68/68 runner copies and 31/31 cases.json unchanged; 0 of 37,323 historical files touched"),
        "ast_gate_analysis": entry("evidence/ast_gate_analysis.json",
                                   "AST analysis with positive control M17-M20 and negative control M29-M31; self-test PASS"),
        "b5_scan": entry("evidence/b5_scan.json", "8 runners + all 31 frozen cases.json (347 cases)"),
        "rc_return_paths": entry("evidence/rc_return_paths.json", "real rc branches per batch"),
        "batch_invocations": entry("evidence/batch_invocations.json", "bound B-unit argv per batch"),
    },
    "propagation": propagation,
    "key_findings": [
        "F-B5-1 (premise overstated): OWNER_DECISIONS 7.2 / 13 T1-8 call M17-M20 the ONLY batch that compares "
        "cases.json[*].expected. Measured: M09-M12 (run_card.py:427 + :430-431) and M21-M24 (:304 + :312-313) "
        "ALREADY gate the verdict on the exact exception type name. Of the six authorized batches only four "
        "(M05-M08, M13-M16, M25-M28, M29-M31) genuinely lacked the gate. The ruling's COUNT of four matches the "
        "measured non-complying count; its implied batch LABELS do not.",
        "F-B5-2 (ghost reference hash): the runner sha256 5307d2cc… quoted in 7.2 / 13 T1-8 does not correspond "
        "to any file on this machine (all 68 copies re-hashed). It is an r2-generation value (M17 review.md:162/"
        "339/348) superseded by the same reviewer's r3 verdict (review.md:409, :422, :518) and by the four cards' "
        "own evidence, which all record 94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252. "
        "Kept as a superseded value; nothing was rewritten.",
        "F-B5-3 (rc deviation set is larger than the brief says): the brief names M05-M08 as using 2=harness. "
        "Measured, M01-M04 and M21-M24 also emit NO rc=1 at all (0/2/3 only), so the cross-batch aggregation "
        "hazard covers three batches, not one. M25-M28 in contrast ALREADY has a real rc=1 (run_card.py:168, :466) "
        "and already matches the frozen table.",
        "F-B5-4 (normative ambiguity, registered not rewritten): the frozen rc=2 gloss 'a negative case correctly "
        "rejected' is a per-CASE statement inside a per-RUN code table; the reference runner emits rc=0 when all "
        "negatives are correctly rejected. Aggregators must not read 'correctly rejected' as rc=2.",
        "F-B5-5 (orchestrator self-caught defect): this card's first-pass scan flag "
        "`compares_raised_to_expected` returned false for all 8 batches, including the reference M17-M20 which "
        "provably compares - a guard indistinguishable from a correct discriminator until tested against a "
        "positive control. Replaced by an AST analysis that self-tests against M17-M20 (true) and M29-M31 (false).",
        "F-B5-6 (M25-M28: a THIRD arm-B behaviour, and a partial gate): the historical M25-M28 runner reacts to a "
        "single-case `expected` mutation by ABORTING with rc=1 - its whole-set `case_contract` gate "
        "(run_card_before.py:140-168, `wrong_declaration` -> `return 1`), not rc=0 and not rc=3. Consequences: "
        "(a) that set-level gate is only PARTIALLY effective - it catches a one-case mutation but is blind to a "
        "blanket one (M29-M31's H_blanket arm, all 11 declarations -> 'ImportError', still measured rc=0 on that "
        "generation); (b) under the frozen rc table a declaration mismatch is 'judgement did not hold' (rc=3), "
        "not 'harness failure' (rc=1), so the historical classification is arguably wrong - registered, not "
        "retro-changed.",
        "F-B5-7 (anchor conflict inside a frozen artifact; reported, NOT rewritten): M25-M28's FROZEN "
        "cases.json carries a `case_contract.rule` string stating that a differing `expected` makes the harness "
        "'refuse to issue a verdict (rc=1)'. That frozen text conflicts BOTH with the frozen rc table (a "
        "declaration mismatch is rc=3) AND with REM-21's mandatory per-case form. Resolving it would require "
        "editing a frozen artifact, which T1-11 forbids; it is recorded here for reviewer/owner adjudication.",
        "F-B5-8 (mutation-target ambiguity in the contract, immaterial): the contract's rule 'the first negative "
        "case (lowest id)' is self-contradictory where ids mix a hyphen with letters, because ASCII '-' (0x2D) < "
        "'0' < 'A', so `sorted(ids)[0]` is CONT-BREAK while file order gives NEG-CARD. Batches that tested both "
        "readings (M21-M24 arms F2/B2) measured IDENTICAL rc, so the ambiguity cannot change any result.",
        "F-B5-9 (a second correction to the frozen rc registry; appended as START_HERE 'append 2'): the earlier "
        "frozen section states that a missing cases.json `expected` currently classifies as rc=3. MEASURED on the "
        "unpatched runners: deleting the key produced NEITHER rc=2 NOR rc=3 but an UNCAUGHT KeyError (the code "
        "used the hard subscript case['expected']) -> raw rc=1, with no evidence file written at all (M09-M12; "
        "M05-M08 identical crash). So the historical classification is rc=1, which the frozen table's own rc=1 "
        "criterion ('expectation file missing') actually covers. Registered append-only; nothing rewritten.",
        "F-B5-10 (arm B spans ALL FOUR rc values): measured 0 (M05-M08, M29-M31 - the true 'fabricated green'), "
        "1 (M25-M28 - whole-set case_contract abort), 2 (M13-M16 - set-level blanket comparison that never reads "
        "the raised exception) and 3 (M09-M12, M21-M24 - already per-case exact-name gated). Any cross-batch "
        "aggregation that assumes a single arm-B behaviour would be wrong on four of the six batches.",
    ],
    "boundaries": {
        "historical_artifacts_modified": [],
        "historical_runner_copies_verified_unchanged": 68,
        "historical_cases_json_verified_unchanged": 31,
        "historical_files_modified_after_card_start": 0,
        "historical_files_scanned_for_mtime": 37323,
        "historical_rc_values_rewritten": 0,
        "frozen_evidence_modified": False,
        "production_repo_writes": 0,
        "production_anchors": {
            "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "other_cards_attempts_modified": [],
        "status_transitions_performed": 0,
        "signatures_forged": False,
        "miniconda_python_used_for_card_runners": False,
    },
    "reviewer_must_do": [
        "Independently re-read each of the six patched runners and confirm the comparison is EXACT type-name "
        "equality and never isinstance (the ValueError decoy is the discriminating probe).",
        "Re-run at least one arm per batch from your own copy and confirm the raw rc; do not accept this card's "
        "recorded rc.",
        "Adjudicate F-B5-1: whether the two already-gating batches should keep the added prerequisite-3 changes "
        "or be reverted to byte-identical historical copies.",
        "Adjudicate F-B5-2: whether the superseded 5307d2cc… needs any further archaeology.",
        "Adjudicate F-B5-4: whether the frozen rc=2 wording requires an owner desambiguation.",
        "Confirm the START_HERE.md append is a pure append by your own two-route test.",
        "Confirm nothing under the historical M-card trees was written (this card reports 0 of 37,323).",
    ],
    "next_action": (
        "Independent reviewer: adjudicate the six patched runner copies and the two corrections "
        "(F-B5-1 scope, F-B5-2 ghost hash) recorded in decision.md D-9 and D-3. The first unfinished card "
        "action is the reviewer signature; the implementer must not self-sign."),
    "all_arms_as_expected": all_arms_ok,
    "all_boundaries_respected": all_boundaries,
}

with open(os.path.join(ATT, "handoff.json"), "w", encoding="utf-8") as fh:
    json.dump(handoff, fh, indent=1, ensure_ascii=False)

print("wrote handoff.json  status=review_pending")
for label, v in propagation.items():
    print("  %-8s already_gated=%-5s arms=%s match=%s boundary=%s"
          % (label, v["already_gated_before_this_card"], v["arms_rc"], v["arms_match"],
             v["boundaries_respected"]))
print("all_arms_as_expected =", all_arms_ok)
print("all_boundaries_respected =", all_boundaries)
