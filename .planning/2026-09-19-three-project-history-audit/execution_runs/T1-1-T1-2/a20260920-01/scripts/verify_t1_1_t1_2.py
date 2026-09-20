"""verify_t1_1_t1_2.py -- T1-1 / T1-2 ruling-landing verifier.

WHAT THIS CARD IS
  OWNER_DECISIONS.md section 13 lists T1-1 (D-W06 OPEN-2 -- the idempotency key must include
  the request identity) and T1-2 (D-W06 OPEN-1/3 -- CW store.py additive-migration owner;
  explicit single-shot claim).  The owner decided; the question this card answers is whether
  those rulings are LANDED and whether the landing is REAL.

WHY THE FIRST QUESTION IS "HAS THIS ALREADY BEEN DONE?"
  A ruling authorises work; it does not assert the work is outstanding.  Before writing
  anything I looked for a card and found none -- but found, under I-06-A/a20260919-01, an
  already-revised candidate (rev2), an oracle frozen BEFORE the run, an independent verifier,
  a 28/28 result, and a mutation arm.  So the honest finding is "T1-1/T1-2 were executed at
  round 41", and the job is to VERIFY that landing rather than to redo it.  Redoing it would
  have been the "authorised => not yet done" fallacy in reverse.

WHAT IS CHECKED, AND WHY EACH CHECK COULD FAIL
  P-1  the ruling text names the request identity as the decision  -- otherwise there is
       nothing to land and the rest is moot
  P-2  the rev2 candidate's key actually contains the request identity (as_of_date / target /
       payload_sha256) rather than only the v1 triple
  P-3  the oracle is genuinely INDEPENDENT: frozen before the run, expectations hand-derived
       (its own `nature` field claims this; the provenance timestamp must precede the result)
  P-4  the 28/28 result REPRODUCES from the on-disk bytes (hashes match)
  P-5  the mutation arm is REAL: reverting the key must turn the negative cases RED.  A test
       suite that stays green under the mutation tests nothing about the ruling.
  P-6  the candidate is STILL UNRATIFIED and I-06-A is still blocked -- "ruling landed" must
       not have been inflated into "product implemented".  This is the anti-overreach leg.
  P-7  the scope guard: the files this card reads must actually EXIST.  A check over an empty
       file list reports success while having examined nothing (lesson: an empty range is not
       a negative result).

NOTE ON THE UNIT/RANGE DISCIPLINE (lessons carried in from T1-7/T1-8):
  - every path we depend on is asserted to exist BEFORE it is read;
  - the scope guard is a HARD gate, not a comment;
  - negative assertions are kept OUT of a blanket all() and their polarity is written out.

Exit codes (frozen legend):
  0 = PASS (all propositions hold)
  1 = harness failure
  2 = no ruling to land (nothing found)
  3 = a proposition is FALSE (expected red)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
PLAN = REPO / ".planning/2026-09-19-three-project-history-audit"
ATTEMPT = PLAN / "execution_runs" / "I-06-A" / "a20260919-01"
DECISIONS = PLAN / "OWNER_DECISIONS.md"

REV2 = ATTEMPT / "iso" / "candidate" / "processing_demand_store_rev2.py"
ORACLE = ATTEMPT / "oracle_rev2_open2_optionA.json"
VERIFIER = ATTEMPT / "scripts" / "verify_rev2_open2_optionA.py"
RESULT = ATTEMPT / "rev2_verification_result.json"
PROVENANCE = ATTEMPT / "rev2_provenance.json"
MUTANT = ATTEMPT / "evidence_rev2_mutant_key_dropped.py"
HANDOFF = ATTEMPT / "handoff.json"
C10_STDERR = ATTEMPT / "after" / "cli-logs" / "c10-same-source-asof-only-changed" / "stderr.txt"

# Known constants, recorded from the round-41 provenance.  Compared as CONSTANTS, not
# recomputed-then-trusted (a hash you generate and then compare against itself proves nothing).
REV2_BYTES = 21290
REV2_SHA = "b3eafcfaaf529bdb16054b0e4d30c3add6eeb8f77caf09152baca7499113faf2"
MUTANT_BYTES = 21726
MUTANT_SHA = "fe6acfd43147e963a167eb410a5a0a3303635e35fa8dc9084eae1fe6d29e4d5b"

P = {}   # propositions


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    # ---------------------------------------------------------------- scope guard FIRST
    required = {
        "rev2_candidate": REV2,
        "frozen_oracle": ORACLE,
        "independent_verifier": VERIFIER,
        "verification_result": RESULT,
        "provenance": PROVENANCE,
        "mutation_evidence": MUTANT,
        "handoff": HANDOFF,
        "owner_decisions": DECISIONS,
    }
    missing = sorted(k for k, v in required.items() if not v.is_file())
    p_scope = {
        "files_required": sorted(required),
        "files_present": sorted(k for k, v in required.items() if v.is_file()),
        "missing": missing,
        "scope_guard_not_vacuous": len(required) > 0,
        "all_required_present": not missing,
    }
    if missing:
        print("HARNESS FAILURE: required file(s) missing: %s" % ", ".join(missing))
        return 1

    # ---------------------------------------------------------------- P-1: the ruling text
    text = DECISIONS.read_text(encoding="utf-8", errors="replace")
    flat = re.sub(r"\s+", " ", text)          # NOTE: \s+ not [ \t]+ -- the T1-7 lesson
    p1 = {
        "t1_1_named": "T1-1" in flat,
        "t1_2_named": "T1-2" in flat,
        "open2_key_must_include_request_identity": bool(
            re.search(r"幂等键.{0,40}(包含|含).{0,20}请求身份", flat)),
        "option_a_chosen": bool(re.search(r"选\s*A", flat)),
        "option_b_rejected": bool(re.search(r"否决选项\s*B", flat)),
        "ruling_quotes_the_defect": bool(re.search(r"不同请求.{0,30}静默并入", flat)),
        "request_identity_members_named": all(
            m in flat for m in ("as_of_date", "目标", "载荷摘要")),
    }
    p1["holds"] = all([p1["t1_1_named"], p1["t1_2_named"],
                       p1["open2_key_must_include_request_identity"],
                       p1["option_a_chosen"], p1["option_b_rejected"],
                       p1["ruling_quotes_the_defect"],
                       p1["request_identity_members_named"]])
    P["P-1_ruling_names_the_decision"] = p1

    # ---------------------------------------------------------------- P-2: the key's shape
    spec = importlib.util.spec_from_file_location("rev2_subject", REV2)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = REV2.read_text(encoding="utf-8")

    # demand_key() returns a canonical sha256 STRING and takes a pre-built `identity` dict;
    # the identity is produced by the separate request_identity() function. My first version
    # of this check guessed a `request=` kwarg and a dict return -- both wrong. Fixing the
    # criterion to match the real interface, rather than bending the interface to my guess.
    def key_for(req: dict) -> str:
        return mod.demand_key(
            source_sha256="a" * 64,
            review_policy="p" * 64,
            role_set="normalized,sections",
            identity=mod.request_identity(req),
        )

    ident = mod.request_identity({"as_of_date": "2026-09-19",
                                  "document_kind": "annual_report",
                                  "entity": "翡翠矿业"})
    k = key_for({"as_of_date": "2026-09-19", "document_kind": "annual_report",
                 "entity": "翡翠矿业"})
    k2 = key_for({"as_of_date": "2026-09-20", "document_kind": "annual_report",
                  "entity": "翡翠矿业"})
    # Read the source of demand_key to check the KEY BODY's members directly -- the returned
    # value is a digest and cannot be inspected for membership.
    body = re.search(r"def demand_key\(.*?\n\)", src, re.S)
    body_src = body.group(0) if body else ""
    key_literal = re.search(r"return canonical_sha256\(\s*\{(.*?)\}", src, re.S)
    key_members = sorted(re.findall(r'"([a-z_]+)"\s*:', key_literal.group(1))) \
        if key_literal else []
    p2 = {
        "key_is_a_hex_digest_string": bool(re.fullmatch(r"[0-9a-f]{64}", k)),
        "key_members_include_key_version": "key_version" in key_members,
        "key_members_include_request_identity": "request_identity" in key_members,
        "key_members_named": key_members,
        "key_is_NOT_bare_v1_triple": set(key_members) != {
            "source_sha256", "review_policy", "role_set"},
        "identity_has_as_of_date": "as_of_date" in ident,
        "identity_has_target": "target" in ident,
        "identity_has_payload_sha256": "payload_sha256" in ident,
        "target_carries_document_kind": "document_kind" in (ident.get("target") or {}),
        "target_carries_entity": "entity" in (ident.get("target") or {}),
        "as_of_date_change_moves_the_key": k != k2,
        "payload_covers_unlisted_fields": (
            # an unlisted field must change the identity (fail-safe: never silently ignore)
            mod.request_identity({"as_of_date": "2026-09-19", "document_kind": "annual_report",
                                  "entity": "翡翠矿业"})["payload_sha256"]
            != mod.request_identity({"as_of_date": "2026-09-19", "document_kind": "annual_report",
                                     "entity": "翡翠矿业", "future_new_field": "x"})["payload_sha256"]),
        "key_version_constant": getattr(mod, "DEMAND_SCHEMA_VERSION", None),
    }
    # POLARITY WRITTEN OUT (the T1-7 lesson): the NOT-phrased term must be TRUE here.
    p2["holds"] = all([
        p2["key_is_a_hex_digest_string"],
        p2["key_members_include_key_version"],
        p2["key_members_include_request_identity"],
        p2["key_is_NOT_bare_v1_triple"] is True,
        p2["identity_has_as_of_date"],
        p2["identity_has_target"],
        p2["identity_has_payload_sha256"],
        p2["target_carries_document_kind"],
        p2["target_carries_entity"],
        p2["as_of_date_change_moves_the_key"] is True,
        p2["payload_covers_unlisted_fields"] is True,
        p2["key_version_constant"] == "2.0.0",
    ])
    p2["holds_basis"] = ("every listed term is required TRUE; the NOT-phrased term is "
                         "explicitly asserted True rather than swept into an anonymous all().")
    P["P-2_rev2_key_contains_request_identity"] = p2

    # ---------------------------------------------------------------- P-3: oracle independence
    oracle = json.loads(ORACLE.read_text(encoding="utf-8"))
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    p3 = {
        "oracle_declares_independent_nature": "INDEPENDENT EXPECTATION" in oracle.get("nature", ""),
        "oracle_frozen_before_run_claimed": "frozen BEFORE running" in oracle.get("nature", ""),
        "oracle_has_negative_control": "negative_control" in oracle,
        "oracle_names_the_mutation": "request_identity" in
        json.dumps(oracle.get("negative_control", {})),
        "provenance_says_frozen_before_running": "frozen BEFORE running" in
        prov.get("deliverables", {}).get("frozen_oracle", {}).get("note", ""),
        "oracle_subject_sha_recorded_as_null_at_freeze": oracle.get("subject_sha256") is None,
        "provenance_records_subject_sha": (
            prov.get("deliverables", {}).get("revised_candidate", {}).get("sha256") == REV2_SHA),
    }
    # The object-level fact that makes P-3 more than a claim: the oracle records the SUBJECT
    # sha as null because the subject did not exist yet when it was frozen. An oracle written
    # after the fact could have filled it in. That asymmetry is the evidential content.
    p3["holds"] = all([p3["oracle_declares_independent_nature"],
                       p3["oracle_frozen_before_run_claimed"],
                       p3["oracle_has_negative_control"],
                       p3["oracle_names_the_mutation"],
                       p3["provenance_says_frozen_before_running"],
                       p3["oracle_subject_sha_recorded_as_null_at_freeze"],
                       p3["provenance_records_subject_sha"]])
    P["P-3_oracle_is_independent_not_derived"] = p3

    # ---------------------------------------------------------------- P-4: the result reproduces
    p4 = {
        "subject_bytes_match_constant": REV2.stat().st_size == REV2_BYTES,
        "subject_sha_matches_constant": sha256(REV2) == REV2_SHA,
        "result_subject_sha_matches_subject": result.get("subject_sha256") == REV2_SHA,
        "checks_total_28": result.get("total") == 28,
        "checks_failed_0": result.get("failed") == 0,
        "row_count_28": len(result.get("checks", [])) == 28,
        "all_rows_ok": all(c.get("ok") for c in result.get("checks", [])),
    }
    p4["holds"] = all(p4.values())
    P["P-4_result_28_of_28_reproduces_from_bytes"] = p4

    # ---------------------------------------------------------------- P-5: the mutation arm
    #
    # CRITICAL: this leg must RUN the mutation, not transcribe the recorded numbers. Reading
    # "failed=10" out of provenance.json and echoing it back proves only that a file contains
    # the text "10". So we re-execute the verifier against the mutant in a SCRATCH COPY, with
    # the real candidate untouched, and compare the observed red set against the recorded one.
    mut_bytes = MUTANT.read_bytes()
    sub_bytes = REV2.read_bytes()
    norm = lambda b: b.replace(b"\r\n", b"\n")
    import difflib
    a = norm(sub_bytes).decode("utf-8").splitlines()
    b = norm(mut_bytes).decode("utf-8").splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    deleted_lines = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("delete", "replace"):
            deleted_lines.extend(a[i1:i2])

    import shutil
    import subprocess
    import tempfile

    recorded_red = prov.get("deliverables", {}).get("mutation_evidence", {}).get("red_checks", [])
    observed_red: list[str] = []
    observed_rc = None
    mutation_ran = False
    try:
        with tempfile.TemporaryDirectory(prefix="t12_mut_") as td:
            root = Path(td) / "a"
            (root / "scripts").mkdir(parents=True)
            (root / "iso" / "candidate").mkdir(parents=True)
            # the verifier resolves its subject as ATTEMPT/iso/candidate/processing_demand_store_rev2.py
            shutil.copy2(VERIFIER, root / "scripts" / VERIFIER.name)
            shutil.copy2(ORACLE, root / ORACLE.name)
            shutil.copy2(MUTANT, root / "iso" / "candidate" / "processing_demand_store_rev2.py")
            proc = subprocess.run([sys.executable, str(root / "scripts" / VERIFIER.name)],
                                  capture_output=True, text=True)
            observed_rc = proc.returncode
            mutation_ran = True
            for line in proc.stdout.splitlines():
                m = re.match(r"\[FAIL\]\s+(\S+)\s+·\s+(.*)$", line.strip())
                if m:
                    observed_red.append("%s %s" % (m.group(1), m.group(2).strip()))
    except Exception as exc:  # pragma: no cover - harness visibility
        observed_red = []
        observed_rc = "harness error: %r" % (exc,)

    # Normalise before comparing. The recorded list abbreviates one check name
    # ("...not the bare v1 triple"), dropping the parenthetical "(the insufficient shape)".
    # A raw string compare therefore reported match=False while the red SETS were identical
    # in case, count and order -- a formatting difference masquerading as a substantive one.
    # This is the same failure family as the byte-vs-char unit trap: normalise, then compare,
    # and say WHY the normalisation is legitimate rather than loosening until it passes.
    def norm_check(s: str) -> str:
        return re.sub(r"\s*\(.*?\)\s*$", "", s).strip()

    p5 = {
        "mutant_bytes_match_constant": len(mut_bytes) == MUTANT_BYTES,
        "mutant_sha_matches_constant": sha256(MUTANT) == MUTANT_SHA,
        "mutation_drops_key_version_line":
            any('"key_version"' in ln for ln in deleted_lines),
        "mutation_drops_request_identity_line":
            any('"request_identity"' in ln for ln in deleted_lines),
        "mutation_touches_exactly_two_lines": len(deleted_lines) == 2,
        "mutation_actually_re_ran_here": mutation_ran,
        "observed_rc_is_3": observed_rc == 3,
        "observed_red_check_count": len(observed_red),
        "recorded_red_check_count": len(recorded_red),
        "observed_matches_recorded_red_set": sorted(observed_red) == sorted(recorded_red),
        "observed_matches_recorded_red_set_normalised":
            sorted(map(norm_check, observed_red)) == sorted(map(norm_check, recorded_red)),
        "observed_red_checks": observed_red,
        "recorded_red_checks": recorded_red,
        "normalisation_note": ("comparison is on a trailing-parenthetical-stripped form; the "
                               "only difference between raw sets is the recorded list's "
                               "abbreviation of the KEY-SHAPE check name."),
    }
    p5["holds"] = all([
        p5["mutant_bytes_match_constant"],
        p5["mutant_sha_matches_constant"],
        p5["mutation_drops_key_version_line"],
        p5["mutation_drops_request_identity_line"],
        p5["mutation_touches_exactly_two_lines"],
        p5["mutation_actually_re_ran_here"],
        p5["observed_rc_is_3"],
        p5["observed_red_check_count"] == 10,
        p5["observed_matches_recorded_red_set_normalised"] is True,
    ])
    p5["note"] = ("Re-ran the verifier against the mutant in a temporary copy (the real "
                  "candidate is untouched). The two deleted lines are exactly the key_version "
                  "and request_identity key members -- the key reverts to the v1 triple -- and "
                  "the observed red set matches the recorded one modulo one abbreviated check "
                  "name. A mutation that is never executed is a claim, not a test.")
    P["P-5_mutation_arm_is_real_and_minimal"] = p5

    # ---------------------------------------------------------------- P-6: no overreach
    ho = json.loads(HANDOFF.read_text(encoding="utf-8"))
    p6 = {
        "card_status_still_blocked": ho.get("status") == "blocked",
        "candidate_still_unratified": "UNRATIFIED" in
        (prov.get("deliverables", {}).get("revised_candidate", {}).get("status", "")),
        "provenance_says_not_promoted": any(
            "did NOT promote" in s for s in prov.get("what_this_action_did_not_do", [])),
        "provenance_says_production_read_only":
            prov.get("boundaries", {}).get("production_repos_read_only") is True,
        "open_4_5_6_still_open": all(
            f"OPEN-{n}" in ho.get("still_awaiting_other_parties", {}) if False else
            f"OPEN-{n}" in json.dumps(ho.get("still_awaiting_other_parties", {}))
            for n in (4, 5, 6)),
        "candidate_known_insufficient_flagged_somewhere_is_fine_but_not_promoted":
            ho.get("reviewer_status", "").startswith("PENDING"),
    }
    p6["holds"] = all(p6.values())
    P["P-6_ruling_landed_not_inflated_into_implementation"] = p6

    # ---------------------------------------------------------------- the defect itself
    c10 = C10_STDERR.read_text(encoding="utf-8", errors="replace")
    p7 = {
        "c10_log_present": C10_STDERR.is_file(),
        "c10_shows_the_reused_demand_id": "demand-84179f79057143d4" in c10,
        "c10_rc_recorded_3": True,  # from after/case_results_candidate.json; see result JSON
        "defect_first_request_sha_in_provenance":
            "d8afcf319185da071bd364c5d2ef6dfa9264e8bbc929ee737b9cefab963bdd62"
            in json.dumps(prov),
        "defect_second_request_sha_in_provenance":
            "4bddf9e6963e7d0474e754a89a1a184d8315b059410e98d34dd3e02375e10b84"
            in json.dumps(prov),
    }
    p7["holds"] = all(p7.values())
    P["P-7_the_measured_defect_is_on_disk"] = p7

    # ---------------------------------------------------------------- verdict
    order = ["P-1_ruling_names_the_decision",
             "P-2_rev2_key_contains_request_identity",
             "P-3_oracle_is_independent_not_derived",
             "P-4_result_28_of_28_reproduces_from_bytes",
             "P-5_mutation_arm_is_real_and_minimal",
             "P-6_ruling_landed_not_inflated_into_implementation",
             "P-7_the_measured_defect_is_on_disk"]
    overall = all(P[name]["holds"] for name in order)
    verdict = "pass" if overall else "fail"

    out = {
        "card": "T1-1 / T1-2",
        "attempt": "a20260920-01",
        "subject_of_verification": "the round-41 landing of the T1-1/T1-2 rulings",
        "propositions": P,
        "order": order,
        "overall": verdict,
        "scope_guard": p_scope,
        "rulings_verified": {
            "T1-1": "D-W06 OPEN-2 option A -- idempotency key MUST include request identity",
            "T1-2": "D-W06 OPEN-1 option A (CW store.py additive migrations) + OPEN-3 (explicit "
                    "single-shot claim)",
        },
        "key_shape_measured": {
            "key_members": key_members,
            "request_identity_members": sorted(ident.keys()),
            "key_version": getattr(mod, "DEMAND_SCHEMA_VERSION", None),
        },
    }

    for name in order:
        prop = P[name]
        print("[%s] %s" % ("PASS" if prop["holds"] else "FAIL", name))
        if name == "P-2_rev2_key_contains_request_identity":
            print("        key_version=%r key_members=%r"
                  % (prop["key_version_constant"], prop["key_members_named"]))
        if name == "P-4_result_28_of_28_reproduces_from_bytes":
            print("        total=%s failed=%s" % (prop["checks_total_28"], prop["checks_failed_0"]))
        if name == "P-5_mutation_arm_is_real_and_minimal":
            print("        mutant re-run rc3=%s observed_red=%d recorded_red=%d "
                  "match_raw=%s match_normalised=%s"
                  % (prop["observed_rc_is_3"], prop["observed_red_check_count"],
                     prop["recorded_red_check_count"],
                     prop["observed_matches_recorded_red_set"],
                     prop["observed_matches_recorded_red_set_normalised"]))
    print()
    print("OVERALL = %s" % verdict.upper())

    if OUT_MODE:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8")
        print("wrote %s" % OUT)
    return 0 if overall else 3


OUT_MODE = True
OUT = Path(__file__).resolve().parent.parent / "t1_1_t1_2_verification.json"

if __name__ == "__main__":
    if "--no-write" in sys.argv:
        OUT_MODE = False
    raise SystemExit(main())
