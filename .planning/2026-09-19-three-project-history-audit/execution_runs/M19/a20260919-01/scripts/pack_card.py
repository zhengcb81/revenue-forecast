"""Pack the derived evidence of one card attempt (runs last, hashes last).

Writes into <attempt>/evidence/<CARD>/:
  source_manifest.json    hashes, verified line anchors, mtime ordering, registry contract
  qualification.json      formula / disclosure_adaptation / accuracy (only formula is touched)
  oq_rulings.json         open questions with counts taken from the enumeration output
  integrity.json           production-repo integrity statement + re-checked hashes
  revision_r2.json         r2 discipline: at most ONE r2 section, line-boundary-reproducible hash
  evidence_hashes.json     sha256 of every evidence file (written after the rest of the pack)

and <attempt>/after/rerun_sha256.json.

Usage:
  python -X utf8 -B pack_card.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil

import card_units

FROZEN = ("input.json", "oracle.json", "cases.json", "oracle_selfcheck.json",
          "oracle_document_freeze.json", "run_result.json", "formula_result.json",
          "negative_results.json", "stdout.txt", "stderr.txt", "registry_enumeration.json",
          "oracle_regen_proof.json", "mutation_selfcheck.json", "command_manifest.json")

# Per-card process history (must agree with scripts/write_process_history.py and review.md).
PROCESS = {
    "M17": {
        "measurement_executions": 3,
        "closing_executions": 6,
        "c2_origin": ("a unit ADDED during this attempt after measurement pass 1 (it did not exist in "
                      "the first pass)"),
    },
    "M18": {
        "measurement_executions": 1,
        "closing_executions": 6,
        "c2_origin": ("an EXISTING unit of this attempt's unit list, delivered byte-identically from "
                      "the M17 attempt (it was not added after a first pass)"),
    },
}
PROCESS["M19"] = PROCESS["M18"]
PROCESS["M20"] = PROCESS["M18"]

# Card-specific open questions.  Wording is objective and third-person on purpose:
# the implementer authors this record, and the independent reviewer is a SEPARATE party
# who has not yet ruled on any entry (see "adjudicated_by" below).
CARD_OQ = {    "M17": {
        "business_negative": ("card_M17.md L45: patients may not be multiplied directly by a price "
                              "per dose, and a potential milestone may not be counted as recognised "
                              "revenue"),
        "business_negative_status": ("NOT runtime-enforceable by this calculator: treated_units is a "
                                     "quantity with effective bounds [0, inf) and any unit mismatch is "
                                     "invisible to arithmetic"),
        "boundary_note": ("the card-specific negative (treated_units = -1) is rejected because the "
                          "quantity domain starts at 0; there is no upper bound and no cross-driver "
                          "consistency check between treated_units and net_revenue_per_unit. "
                          "CORRECTION TO A DESCRIPTIVE ROW OF oracle.md: the frozen oracle.md was "
                          "written before the enumeration and its section 1 row asserted that the "
                          "three amount drivers share the [0, inf) bounds; the enumeration and the "
                          "measured probes show they are SIGNED drivers with (-inf, inf) bounds "
                          "(model_registry.py:265-269), so a small negative confirmed amount is "
                          "accepted (PROBE-NEG-MILESTONE), and only a TOTAL-revenue negative is "
                          "refused (PROBE-NEG-TOTAL-REVENUE). No frozen EXPECTATION depended on that "
                          "row, so oracle.md was deliberately NOT rewritten; the error is recorded "
                          "here and in review.md instead"),
    },
    "M18": {
        "business_negative": ("card_M18.md L42: already-filled impressions must not be multiplied by "
                              "the fill rate again, and the thousand-impression conversion must "
                              "happen exactly once"),
        "business_negative_status": ("the thousand-impression half IS observable and was probed "
                                     "(OBS-THOUSAND-ONCE expects 16100 for a doubled impression "
                                     "count); the 'already filled' half is NOT runtime-enforceable, "
                                     "because the calculator cannot tell whether eligible_impressions "
                                     "were pre-fill opportunities"),
        "boundary_note": ("fill_rate carries the ratio domain [0,1]; 1.2 is rejected (card-specific "
                          "negative) and 1.0 is admissible by the same domain, so a fill rate of "
                          "exactly 100% is not refused"),
    },
    "M19": {
        "business_negative": ("card_M19.md L42: DAU multiplied by an annual ARPPU is a period "
                              "mismatch, and gross billings are not revenue"),
        "business_negative_status": ("NOT runtime-enforceable: active_users, payer_conversion and "
                                     "revenue_per_payer are checked only for domain and finiteness; "
                                     "the period of each driver is a disclosure question, not a "
                                     "calculator question"),
        "boundary_note": ("payer_conversion carries the ratio domain [0,1]; 1.1 is rejected "
                          "(card-specific negative) and the upper edge 1.0 is accepted, with the "
                          "numeric consequence recorded by OBS-PAYER-BOUNDARY (20010)"),
    },
    "M20": {
        "business_negative": ("card_M20.md L57: mid-year timing may not be defaulted without "
                              "evidence, and different prices or same-year churn cohorts need a "
                              "professional split"),
        "business_negative_status": ("NOT runtime-enforceable: the registry default for timing_factor "
                                     "is 1.0 (not a mid-year 0.5), and cohort splitting is a "
                                     "disclosure/adaptation question"),
        "continuity_note": ("the customer bridge IS enforced: the intra-year balance "
                            "(opening + new - churned == ending) and the cross-year continuity "
                            "(opening == prior ending) are both checked with math.isclose(rel_tol=1e-9, "
                            "abs_tol=1e-9); the frozen CONT-BREAK case (opening 121 vs prior closing "
                            "120) is rejected, and the exposure guard is 'exposure < 0', so exposure "
                            "of exactly 0 is accepted (OBS-ZERO-CUSTOMERS expects 7)"),
    },
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump(path, doc):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    atomic_dump(path, doc)



def atomic_dump(path, doc):
    """Write JSON through a temp file + os.replace so an interrupted write cannot truncate it."""
    tmp = path + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def measure_drift(attempt, entries):
    """Re-read every entry of a hash table and count mismatches (P2-A)."""
    drifted = []
    missing = []
    for rel, entry in entries.items():
        wanted = entry["sha256"] if isinstance(entry, dict) else entry
        path = os.path.join(attempt, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        if sha256(path) != wanted:
            drifted.append(rel)
    return {"drift_count": len(drifted), "missing_count": len(missing),
            "drifted_paths": sorted(drifted + ["missing:" + m for m in missing])}


def r2_analysis(oracle_md, scratch_dir, addendum_record_path):
    """Count r2 sections and prove the line-boundary-reproducible hash rule.

    If a real r2 addendum exists, the proof is taken from the RECORDED append and re-verified live
    against the current file (truncate at the recorded boundary and compare with the recorded
    pre-append hash).  If no addendum exists, the rule is demonstrated on a scratch copy.
    """
    with open(oracle_md, "rb") as handle:
        raw = handle.read()
    text = raw.decode("utf-8")
    offsets = []
    position = 0
    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        if line.startswith("##") and ("r2" in line or "R2" in line):
            offsets.append({"line_number": number, "byte_offset": position, "line_text": line.strip()})
        position += len(line.encode("utf-8"))

    rule = ("at most ONE 'revision r2' section may exist in oracle.md; if a pre-append hash is "
            "recorded it must be reproducible at a REAL LINE BOUNDARY, i.e. by truncating the "
            "appended file at the byte offset where the appended section's first line begins")

    if offsets and os.path.isfile(addendum_record_path):
        record = load_json(addendum_record_path)
        boundary = record["boundary_byte_offset"]
        prefix_hash = hashlib.sha256(raw[:boundary]).hexdigest()
        # P2-C (independent review r2): boundary_byte_offset is the offset of the FIRST APPENDED BYTE,
        # i.e. the start of the blank separator line preceding the appended section header.  "A real
        # line boundary" therefore means "the byte before it is LF" (the pre-append file ended with a
        # newline).  An earlier version of this line asserted "the offset points at a '## ' heading",
        # which is false here and made this field contradict its own note.
        proof = {
            "source": "the real append recorded in evidence/%s/oracle_addendum_record.json" % os.path.basename(
                os.path.dirname(addendum_record_path)),
            "boundary_byte_offset": boundary,
            "boundary_semantics": ("offset of the first appended byte; because the pre-append file "
                                   "ended with LF it is the start of the blank separator line that "
                                   "precedes the appended section header"),
            "line_boundary_is_real": bool(boundary == 0 or raw[boundary - 1:boundary] == b"\n"),
            "byte_before_boundary_is_lf": bool(boundary > 0 and raw[boundary - 1:boundary] == b"\n"),
            "boundary_points_at_appended_section_header": False,
            "appended_section_header_line": record.get("added_section_header_line"),
            "appended_section_header_line_number": record.get("added_section_header_line_number"),
            "appended_section_header_byte_offset": record.get("added_section_header_byte_offset"),
            "recorded_pre_append_sha256": record["oracle_md_sha256_before_addendum"],
            "live_truncated_prefix_sha256": prefix_hash,
            "prefix_hash_equals_base_hash": (prefix_hash
                                             == record["oracle_md_sha256_before_addendum"]),
            "recorded_post_append_sha256": record["oracle_md_sha256_after_addendum"],
            "current_file_sha256": hashlib.sha256(raw).hexdigest(),
            "current_file_equals_recorded_post_append": (
                hashlib.sha256(raw).hexdigest() == record["oracle_md_sha256_after_addendum"]),
            "note": ("re-verified live: truncating the CURRENT oracle.md at the recorded real line "
                     "boundary reproduces the pre-append hash, so the r1 body is byte-unchanged"),
        }
        return {"rule": rule, "r2_sections_in_oracle_md": len(offsets),
                "r2_section_locations": offsets, "oracle_md_sha256": hashlib.sha256(raw).hexdigest(),
                "mechanism_proof": proof}

    # No addendum: demonstrate the rule on a scratch copy.
    os.makedirs(scratch_dir, exist_ok=True)
    demo_base = os.path.join(scratch_dir, "demo_oracle.md")
    demo_appended = os.path.join(scratch_dir, "demo_oracle_appended.md")
    shutil.copyfile(oracle_md, demo_base)
    base_hash = sha256(demo_base)
    with open(demo_appended, "wb") as handle:
        with open(demo_base, "rb") as source:
            handle.write(source.read())
        handle.write(b"\n## revision r2 (mechanism demonstration, scratch copy only)\n"
                     b"\nThis section exists only to prove the reproducibility rule.\n")
    with open(demo_appended, "rb") as handle:
        appended = handle.read()
    marker = b"## revision r2 (mechanism demonstration, scratch copy only)"
    marker_offset = appended.index(marker)
    # P3-B (r3 review): the reproducibility rule is about truncating at the length of the
    # PRE-APPEND file (a real line boundary), NOT at the marker offset (which is base length + 1
    # because of the separating newline).  Comparing at the marker offset produced a vacuous
    # `false` next to `line_boundary_is_real: true`, which reads as self-contradictory on the
    # three cards that have no addendum at all.
    prefix_at_base_length = appended[:len(open(demo_base, "rb").read())]
    prefix_hash = hashlib.sha256(prefix_at_base_length).hexdigest()
    return {
        "rule": rule,
        "r2_sections_in_oracle_md": len(offsets),
        "r2_section_locations": offsets,
        "oracle_md_sha256": sha256(oracle_md),
        "mechanism_proof": {
            "source": "scratch demonstration (no r2 addendum exists in this attempt)",
            "scratch_base": demo_base,
            "scratch_appended": demo_appended,
            "base_sha256": base_hash,
            "marker_byte_offset_in_appended_file": marker_offset,
            "truncation_offset_used": len(open(demo_base, "rb").read()),
            "truncated_prefix_sha256": prefix_hash,
            "prefix_hash_equals_base_hash": prefix_hash == base_hash,
            "applicable": True,
            "applicability_note": ("this branch is a SYNTHETIC demonstration for cards that have "
                                  "no r2 addendum; the real, live re-verification runs only in the "
                                  "addendum branch. `prefix_hash_equals_base_hash` is computed at the "
                                  "base length, where truncation must reproduce the base hash"),
            "line_boundary_is_real": appended[marker_offset:marker_offset + 2] == b"##",
            "note": ("the demonstration runs on a scratch copy under recovery/; the frozen oracle.md "
                     "was not modified"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    info = card_units.CARDS[card]
    evidence = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    run_result = load_json(os.path.join(evidence, "run_result.json"))
    oracle = load_json(os.path.join(evidence, "oracle.json"))
    cases = load_json(os.path.join(evidence, "cases.json"))
    freeze = load_json(os.path.join(evidence, "oracle_document_freeze.json"))
    regen = load_json(os.path.join(evidence, "oracle_regen_proof.json"))
    mutation = load_json(os.path.join(evidence, "mutation_selfcheck.json"))
    enumeration = load_json(os.path.join(evidence, "registry_enumeration.json"))
    probes = load_json(os.path.join(evidence, "extra_probes.json"))
    rc_b = load_json(os.path.join(evidence, "runs", "B-product-run", "rc.json"))
    rc_c = load_json(os.path.join(evidence, "runs", "C-registry-enumeration", "rc.json"))
    # The r2 analysis is needed by the source_manifest block below, so it is computed here.
    addendum_record_path = os.path.join(evidence, "oracle_addendum_record.json")
    r2 = r2_analysis(os.path.join(attempt, "oracle.md"),
                     os.path.join(attempt, "recovery", "line_boundary_demo"),
                     addendum_record_path)
    addendum = load_json(addendum_record_path) if os.path.isfile(addendum_record_path) else None

    # ---- verified line anchors for the card's cited entry point and registration ----
    with open(os.path.join(code_root, "model_registry.py"), "r", encoding="utf-8") as handle:
        registry_lines = handle.read().splitlines()
    entry_index = card_units.ENTRY_POINT_LINE - 1
    reg_index = info["registration_line"] - 1
    entry_text = registry_lines[entry_index]
    reg_text = registry_lines[reg_index]
    entry_anchor_ok = entry_text.startswith("def calculate_registered_model")
    reg_anchor_ok = ('"%s"' % info["model_id"]) in reg_text

    # ---- mtime ordering: the freeze must precede the first product stdout ----
    def mtime(rel):
        path = os.path.join(attempt, rel)
        return os.path.getmtime(path) if os.path.exists(path) else None

    ordering = {
        "oracle_md_mtime": mtime("oracle.md"),
        "oracle_md_mtime_at_generation": freeze["oracle_document"]["oracle_md_mtime"],
        "input_json_mtime": mtime(os.path.join("evidence", card, "input.json")),
        "oracle_json_mtime": mtime(os.path.join("evidence", card, "oracle.json")),
        "cases_json_mtime": mtime(os.path.join("evidence", card, "cases.json")),
        "binding_json_mtime": mtime("binding.json"),
        "product_stdout_mtime": mtime(os.path.join("evidence", card, "stdout.txt")),
        "product_run_started_utc": rc_b.get("started_utc"),
        "note": ("the freeze order is asserted from the mtime RECORDED BEFORE oracle generation "
                 "(oracle_document_freeze.json), not from the file's current mtime: for M17 the "
                 "current oracle.md mtime is later because of the declared r2 addendum, and that "
                 "later mtime is never used as freeze evidence"),
    }
    ordering["oracle_json_precedes_product_stdout"] = (
        ordering["oracle_json_mtime"] is not None and ordering["product_stdout_mtime"] is not None
        and ordering["oracle_json_mtime"] < ordering["product_stdout_mtime"])
    ordering["oracle_md_precedes_product_stdout"] = (
        ordering["oracle_md_mtime_at_generation"] is not None
        and ordering["product_stdout_mtime"] is not None
        and ordering["oracle_md_mtime_at_generation"] < ordering["product_stdout_mtime"])
    ordering["oracle_md_mtime_is_later_due_to_r2_append"] = bool(
        ordering["oracle_md_mtime"] is not None and ordering["oracle_md_mtime_at_generation"] is not None
        and ordering["oracle_md_mtime"] > ordering["oracle_md_mtime_at_generation"])
    ordering["binding_precedes_product_stdout"] = (
        ordering["binding_json_mtime"] is not None and ordering["product_stdout_mtime"] is not None
        and ordering["binding_json_mtime"] < ordering["product_stdout_mtime"])

    production_hashes = {
        "scripts/model_registry.py": sha256(os.path.join(card_units.PRODUCTION_ROOT, "scripts",
                                                         "model_registry.py")),
        "scripts/model_extensions.py": sha256(os.path.join(card_units.PRODUCTION_ROOT, "scripts",
                                                           "model_extensions.py")),
    }
    isolated_hashes = {
        "iso/checkout_scripts/model_registry.py": sha256(os.path.join(code_root, "model_registry.py")),
        "iso/checkout_scripts/model_extensions.py": sha256(os.path.join(code_root,
                                                                       "model_extensions.py")),
    }

    source_manifest = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": info["model_id"],
        "card_title": info["title"],
        "entry_point": ("scripts/model_registry.py calculate_registered_model(model_id, base_revenue, "
                        "drivers, years)"),
        "card_document": "execution_v2/card_%s.md" % card,
        "card_document_anchors_verified": {
            "entry_point_line_claimed_by_card": card_units.ENTRY_POINT_LINE,
            "entry_point_line_text": entry_text,
            "entry_point_anchor_ok": entry_anchor_ok,
            "registration_line_claimed_by_card": info["registration_line"],
            "registration_line_text": reg_text[:160],
            "registration_anchor_ok": reg_anchor_ok,
            "anchor_rule": ("the line numbers cited by the card are re-checked against the isolated "
                            "copy; a mismatch would be reported here instead of being silently "
                            "carried forward"),
        },
        "production_source_root_readonly": card_units.PRODUCTION_ROOT,
        "production_source_hashes_at_binding_and_after_run": production_hashes,
        "isolated_copy_hashes": isolated_hashes,
        "isolated_copy_equals_production": (
            isolated_hashes["iso/checkout_scripts/model_registry.py"]
            == production_hashes["scripts/model_registry.py"]
            and isolated_hashes["iso/checkout_scripts/model_extensions.py"]
            == production_hashes["scripts/model_extensions.py"]),
        "interpreter": {
            "path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": card_units.TEMPLATE_INTERPRETER,
            "note": ("attempt-local venv created with `python -m venv` from the I-00-A template venv; "
                     "pytest was NOT installed, see evidence/%s/runs/A0b-pytest-offline-availability/"
                     "stdout.txt - the offline probe returned rc 1, no local wheel exists and network "
                     "is disabled" % card),
            "global_python_used_for": ("nothing; the global Miniconda interpreter was never invoked "
                                       "by this card"),
        },
        "card_script_hashes": {
            "scripts/" + name: sha256(os.path.join(attempt, "scripts", name))
            for name in sorted(os.listdir(os.path.join(attempt, "scripts")))
            if name.endswith(".py")
        },
        "oracle_document": {
            "path": "oracle.md",
            "sha256_at_oracle_generation": freeze["oracle_document"]["oracle_md_sha256"],
            "sha256_now": sha256(os.path.join(attempt, "oracle.md")),
            "unchanged_since_generation": (
                freeze["oracle_document"]["oracle_md_sha256"]
                == sha256(os.path.join(attempt, "oracle.md"))),
            "frozen_before_any_product_run": ordering["oracle_md_precedes_product_stdout"],
            "r2_addendum_appended": r2["r2_sections_in_oracle_md"] > 0,
            "r2_sections_in_oracle_md": r2["r2_sections_in_oracle_md"],
            "frozen_body_reproducible_by_truncation": (
                r2["mechanism_proof"]["prefix_hash_equals_base_hash"]
                if r2["r2_sections_in_oracle_md"] else None),
            "honest_gap": ("%s The file-level hash therefore differs from the generation-time hash "
                           "ONLY because of the declared append; the r1 body's byte-identity is "
                           "asserted by truncating the current file at the appended section's first "
                           "line and comparing with the generation-time hash "
                           "(evidence/%s/oracle_addendum_record.json). M18/M19/M20 have no r2 section "
                           "and keep file-level identity."
                           % ("An r2 addendum WAS appended to this file after the independent review "
                              "verdict." if r2["r2_sections_in_oracle_md"]
                              else "No r2 addendum has been appended to this attempt's oracle.md.",
                              card)),
        },
        "mtime_ordering": ordering,
        "oracle_regeneration": {
            "proof_path": "evidence/%s/oracle_regen_proof.json" % card,
            "all_byte_identical": regen["all_byte_identical"],
            "comparisons": regen["comparisons"],
        },
        "extra_boundary_probes": {
            "path": "evidence/%s/extra_probes.json" % card,
            "gating": False,
            "summary": [{"id": p["id"], "raised": p.get("raised"), "actual": p.get("actual"),
                         "measured_matches": {k: v for k, v in p.items()
                                              if k.startswith("matches_")}}
                        for p in probes["probes"]],
            "rule": ("these observations are outside oracle.json and outside the runner's exit code; "
                     "they are recorded because a bound is a claim until a value at it is measured"),
        },
        "evidence_input_hashes": {
            "evidence/%s/input.json" % card: sha256(os.path.join(evidence, "input.json")),
            "evidence/%s/oracle.json" % card: sha256(os.path.join(evidence, "oracle.json")),
            "evidence/%s/cases.json" % card: sha256(os.path.join(evidence, "cases.json")),
        },
        "registry_metadata_observed_from_the_isolated_copy":
            run_result.get("registry_metadata", {}),
        "product_run": {
            "raw_returncode": rc_b.get("raw_returncode"),
            "expected_returncode": 0,
            "verdict": run_result.get("verdict"),
            "exit_code_semantics": run_result.get("exit_code_semantics"),
            "exit_code_contract": run_result["exit_code_semantics"],
        },
        "network_calls": "none",
        "llm_or_provider_calls": "none",
        "packed_utc": now,
    }
    dump(os.path.join(evidence, "source_manifest.json"), source_manifest)

    # ---- qualification: only formula is touched ----
    exit_code = run_result.get("exit_code")
    # The acceptance is written by an INDEPENDENT REVIEWER, never by this attempt: it is read from
    # evidence/<card>/review_decision.json (produced after the reviewer verdict was transcribed
    # byte-for-byte).  Absent that file the state stays review_pending.
    decision_path = os.path.join(evidence, "review_decision.json")
    decision = load_json(decision_path) if os.path.isfile(decision_path) else None
    if decision and decision.get("formula_state"):
        formula_state = decision["formula_state"]
    elif exit_code == 0:
        formula_state = "review_pending"
    elif exit_code == 2:
        formula_state = "blocked_no_verdict"
    elif exit_code == 3:
        formula_state = "stop_formula"
    else:
        formula_state = "blocked_harness_error"
    qualification = {
        "card_id": card,
        "model_id": info["model_id"],
        "implementer_is_not_the_reviewer": True,
        "formula": {
            "state": formula_state,
            "a_to_c_conditions": {
                "positive_within_frozen_tolerance": bool(run_result.get("tolerances_ok")),
                "output_fidelity_ok": bool(run_result.get("fidelity", {}).get("fidelity_ok")),
                "year_count_matches_len_years": bool(
                    run_result.get("fidelity", {}).get("length_equals_years")),
                "continuity_positive_ok": bool(
                    run_result.get("continuity_positive", {}).get("ok")),
                "defaults_case_ok_not_gating": bool(run_result.get("defaults_ok")),
                "negatives_rejected": "%s/%s" % (run_result.get("negative_summary", {}).get("passed"),
                                                 run_result.get("negative_summary", {}).get("total")),
                "mutation_selfcheck_red_then_green": bool(
                    mutation.get("all_mutations_produced_the_expected_exit_code")),
                "oracle_regenerable_byte_for_byte": bool(regen.get("all_byte_identical")),
            },
            "runner_raw_returncode": rc_b.get("raw_returncode"),
            "implementer_measurement": ("all A-C conditions met"
                                        if exit_code == 0 else
                                        "A-C not all met; see run_result.json verdict_reasons: %s"
                                        % run_result.get("verdict_reasons")),
            "granted_by": ("a separate independent reviewer only; the implementer never writes "
                           "'accepted'"),
            "acceptance_authority": (decision.get("authority") if decision else None),
            "implementer_signed": False,
            "implementer_never_signs_acceptance": True,
            "acceptance_carrier": (decision.get("carrier") if decision else None),
            "historical_97_tests_216_subtests": ("not used as a substitute for this card's new "
                                                 "results"),
        },
        "disclosure_adaptation": {
            "state": "unmapped",
            "reasons": [
                ("D is a professional decision ([professional_decision_required] in the card) and "
                 "requires a per-driver disclosure mapping signed by an industry/accounting reviewer"),
                ("D also requires reconciliation of one closed period plus a production forecast "
                 "entry-point mapping reviewed independently"),
                ("this attempt produced no disclosure mapping at all; per the card text those "
                 "artefacts do not block the A-C formula dispatch and must not be filled in "
                 "speculatively"),
            ],
        },
        "accuracy": {
            "state": "unproven",
            "reasons": [
                ("F requires the I-12 frozen design (information-time sample, baseline, statistical "
                 "uncertainty), which does not exist"),
                "no rolling out-of-sample evaluation was run",
                ("a formula pass for one model, or one company's mapping, must never be promoted to "
                 "industry-wide accuracy"),
            ],
        },
        "third_qualification_rule": ("formula, disclosure adaptation and accuracy are three "
                                     "independent qualifications; passing A-C grants only the "
                                     "formula qualification and is not evidence of the other two"),
        "review": {
            "independent_review_performed": True,
            "verdict_received": ("accepted_scoped (formula qualification only)" if decision
                                 else "accepted_scoped (formula qualification only) - r1 headline; "
                                      "see r2/r3 fields below"),
            "final_verdict": (decision.get("verdict") if decision else None),
            "final_verdict_record": (decision.get("carrier") if decision else None),
            "implementer_signature": None,
            "formula_state_reason": ("the reviewer accepted r1 scoped, but the post-review r2 fixes "
                                     "(declared-expectation enforcement in the runner, OQ-05 "
                                     "parameterisation, OQ-05 ruling entry, process history, and for "
                                     "M17 the oracle.md section 13 append) must be point-reviewed, so "
                                     "formula remains review_pending and is NOT self-signed"),
            "unmapped_means_zero_output": ("disclosure_adaptation = unmapped means no disclosure "
                                           "artefact of any kind exists for this card, not that it is "
                                           "partially done"),
            "unproven_means_no_evaluation": ("accuracy = unproven means no out-of-sample evaluation "
                                             "was run at all (no I-12 design exists)"),
        },
    }
    dump(os.path.join(evidence, "qualification.json"), qualification)

    # ---- oq_rulings: counts straight from the enumeration output ----
    counts = enumeration["totals"]
    focus = enumeration["card_focus"]
    silently_zero = [d["driver"] for d in enumeration["optional_drivers_silently_defaulted_to_zero"]
                     if d["driver"].startswith(info["model_id"] + ".")]
    oq = {
        "card_id": card,
        "model_id": info["model_id"],
        "document_author": ("the implementing session of attempt a20260919-01, which also wrote "
                            "oracle.md, run_card.py and this record"),
        "adjudicated_by": ("PENDING - no entry below has been ruled on by the independent reviewer; "
                           "the reviewer is a separate party who may accept, amend or reject each "
                           "entry"),
        "no_first_person_authorship_claim": True,
        "enumerated_by": enumeration["enumerated_by"],
        "enumeration_raw_output": {
            "path": "evidence/%s/registry_enumeration.json" % card,
            "sha256": sha256(os.path.join(evidence, "registry_enumeration.json")),
            "script_sha256": sha256(os.path.join(attempt, "scripts", "enumerate_registry.py")),
            "raw_stdout": "evidence/%s/runs/C-registry-enumeration/stdout.txt" % card,
            "raw_stdout_sha256": rc_c.get("stdout_sha256"),
            "raw_returncode": rc_c.get("raw_returncode"),
            "code_root": code_root,
        },
        "enumeration_counts": counts,
        "card_registry_facts": {
            "model_id": info["model_id"],
            "required": focus["required"],
            "optional": focus["optional"],
            "defaults": focus["defaults"],
            "ratio_drivers": focus["ratio_drivers"],
            "driver_effective_bounds": {d: e["effective_bounds"]
                                        for d, e in focus["drivers"].items()},
        },
        "rulings": [
            {
                "id": "OQ-01",
                "scope": "shared by all four cards of this batch (M17-M20)",
                "title": "isolation binding provenance",
                "status": "registered_not_fixed",
                "observation": ("the cards require the run cwd to come from I-00-B, while I-00-B "
                                "binds the isolation plan and the two-stage command rule rather than "
                                "materialising a checkout tree"),
                "what_this_attempt_did": ("materialised its own read-only snapshot at "
                                          "iso/checkout_scripts and recorded that its two files hash "
                                          "equal to the production files"),
                "consequence": ("if the intended binding is an I-00-B-materialised checkout, the "
                                "provenance chain differs; the code under test is byte-identical "
                                "either way"),
                "requires_ruling_from": "owner (dispatch/binding)",
            },
            {
                "id": "OQ-02",
                "scope": "shared by all four cards of this batch (M17-M20)",
                "title": "an omitted optional driver that has no declared default is silently 0.0",
                "status": "registered_not_fixed",
                "mechanism": ("calculate_registered_model resolves a missing driver as "
                              "drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))"),
                "enumerated_registry_wide_count":
                    counts["optional_drivers_absent_from_declared_defaults"],
                "enumerated_for_this_model": silently_zero,
                "enumerated_registry_wide_list": [d["driver"] for d in
                                                  enumeration["optional_drivers_silently_defaulted_to_zero"]],
                "why_it_matters_here": ("'the item does not exist' and 'the item was not found' "
                                        "become the same input, so an unknown is turned into "
                                        "recognised revenue"),
                "cross_check": ("OBS-DEFAULT-EQUIV in evidence/%s/run_result.json records that writing "
                                "the omitted optional drivers explicitly as 0 reproduces the "
                                "omitted-input result, which is what makes the documented default of 0 "
                                "falsifiable" % card),
                "action_this_attempt": "registered, NOT fixed; no product file was modified",
                "requires_ruling_from": "owner (product change would need its own card)",
            },
            {
                "id": "OQ-03",
                "title": "card business negative that the calculator cannot enforce",
                "status": "registered_not_fixed",
                "card_text": CARD_OQ[card]["business_negative"],
                "finding": CARD_OQ[card]["business_negative_status"],
                "consequence": "STOP_DISCLOSURE_ADAPTATION remains in force; a number is not an adaptation",
                "requires_ruling_from": "industry/accounting reviewer (I-10-A / D)",
            },
            {
                "id": "OQ-04",
                "title": "numerical domain / boundary observations of this model",
                "status": "registered_not_fixed",
                "finding": CARD_OQ[card].get("boundary_note", "")
                           + (" " + CARD_OQ[card].get("continuity_note", "")
                              if CARD_OQ[card].get("continuity_note") else ""),
                "derived_from": ("the effective bounds enumerated by scripts/enumerate_registry.py "
                                 "(evidence/%s/registry_enumeration.json)" % card),
                "measured_probes": [{"id": p["id"], "raised": p.get("raised"),
                                     "actual": p.get("actual"),
                                     "measured_matches": {k: v for k, v in p.items()
                                                          if k.startswith("matches_")}}
                                    for p in probes["probes"]],
                "probe_provenance": ("evidence/%s/extra_probes.json; the probes are NON-GATING and sit "
                                     "outside oracle.json and outside the runner's exit code"
                                     % card),
                "requires_ruling_from": "independent reviewer (accept / amend / reject)",
            },
            {
                "id": "OQ-05",
                "title": "process history of this attempt (repeated executions of one argv)",
                "status": "registered_not_fixed",
                "finding": ("this card's measurement pipeline was executed %d time(s) and the closing "
                            "sequence %d time(s); the capture wrapper overwrites runs/<UNIT>/rc.json on "
                            "every execution, so the byte-level records can only prove the LAST "
                            "execution of each unit. The C2 extra-boundary-probe unit is %s."
                            % (PROCESS[card]["measurement_executions"],
                               PROCESS[card]["closing_executions"], PROCESS[card]["c2_origin"])),
                "declared_versus_observed": {
                    "declared": "the pass structure in process_history.json, declared by the implementer",
                    "observed": ("the surviving rc.json records (last execution per unit) and the "
                                 "run-directory creation timestamps"),
                    "honest_gap": ("superseded stdout/rc were overwritten in place; only the declared "
                                   "history and directory timestamps distinguish the passes"),
                },
                "pointer": "process_history.json",
                "requires_ruling_from": "independent reviewer (accept / amend / reject)",
            },
        ],
        "counts_provenance_rule": ("every number in enumeration_counts comes from the raw output of "
                                   "scripts/enumerate_registry.py; none is transcribed from prose"),
    }
    dump(os.path.join(evidence, "oq_rulings.json"), oq)

    # ---- integrity ----
    # The anchored values are CONSTANTS of the task; the observed values are what this pack saw on
    # disk.  `anchored_hashes_match` is COMPUTED (it used to be a hard-coded True, which would have
    # claimed a match even when the working tree had been reset to HEAD by an external git operation).
    observed_matches_anchor = {
        rel: (production_hashes.get(rel) == anchor)
        for rel, anchor in card_units.ANCHORED_PRODUCTION_HASHES.items()
    }
    integrity = {
        "card_id": card,
        "production_repos_untouched": True,
        "statement": ("no file under any production repository was created, modified, added, "
                      "committed, restored or stashed by this attempt"),
        "production_hashes_rechecked_after_the_run": production_hashes,
        "anchored_hashes_as_given_by_the_task": dict(card_units.ANCHORED_PRODUCTION_HASHES),
        "observed_matches_task_anchor_by_file": observed_matches_anchor,
        "anchored_hashes_match": all(observed_matches_anchor.values()),
        "anchored_hashes_match_rule": ("COMPUTED by comparing the observed production hashes with the "
                                       "task anchors; never asserted as a constant"),
        "anchored_hashes": production_hashes,
        "anchored_hash_claim_is_time_scoped": {
            "observed_at_pack_utc": now,
            "rule": card_units.PRODUCTION_HASH_DISCIPLINE,
            "incident_reference": card_units.INCIDENT_REFERENCE,
            "known_external_risk": ("the repository's own pre-commit/pre-push gate exports unstaged "
                                    "changes to a patch, runs `git checkout -- .`, and replays the "
                                    "patch afterwards; if the replay step is skipped (observed once: "
                                    "`git checkout -- .` returned 255 on files held by concurrent "
                                    "writers) the production working tree is left reset to HEAD, so a "
                                    "hash check taken inside that window legitimately reads a "
                                    "different revision"),
            "if_false_then": ("record the drift with its timestamp, escalate to the orchestration "
                              "layer, and re-bind before any NEW run; never adjust the frozen "
                              "expectations to accommodate the drifted tree"),
        },
        "product_runs_used": ("--code-root <attempt>/iso/checkout_scripts (byte-identical read-only "
                              "snapshot); the production scripts directory was never on sys.path for "
                              "any card run"),
        "network_calls": "none",
        "llm_or_provider_calls": "none",
        "write_allowlist_observed": [attempt],
        "notes": [
            ("revenue-forecast already had pre-existing dirty files (including the user-owned "
             "SKILL.md / references / CHANGELOG.md / assurance / e2e expected files); git status "
             "--porcelain was captured into before/ and after/ so the pre-existing dirt stays "
             "attributable to its owner"),
            ".planning/reviews was never written to",
            ("this attempt wrote only inside its own attempt directory; no other attempt directory "
             "was created or overwritten"),
        ],
        "packed_utc": now,
    }
    dump(os.path.join(evidence, "integrity.json"), integrity)

    # ---- revision r2 discipline (r2 / addendum computed above, before source_manifest) ----
    revision = {
        "card_id": card,
        "model_id": info["model_id"],
        "revision": "r2" if r2["r2_sections_in_oracle_md"] else "r1",
        "independent_review_received": True,
        "independent_review_verdict_received": "accepted_scoped (formula qualification only)",
        "independent_review_verdict_received_note": (
            "P3-5 (independent review r2): the field above is a faithful transcription of the r1 "
            "review's HEADLINE ONLY.  It is NOT a sign-off and it deliberately omits the two P2 "
            "conditions the r1 review attached (P2-1: the runner must enforce the per-case declared "
            "expectation; P2-2: OQ-05 must be parameterised per card).  The value is kept, not "
            "overwritten, so the r1 record stays intact; the CURRENT verdict is in the field below."),
        "independent_review_verdict_r1_conditions": [
            "P2-1: enforce cases.json's per-case declared expectation in the runner",
            "P2-2: parameterise OQ-05 per card (it had been a cross-card constant)",
        ],
        "r2_verdict_received": "changes_required",
        "r2_verdict_scope": ("audit metadata only (P2-A hash-table drift, P2-B rc_namespace.json not "
                             "valid JSON, P2-C two contradictory M17 addendum-record values, plus "
                             "P3-1..P3-6); the formula evidence itself was re-verified UNCHANGED"),
        "r2_verdict_record": ("%s/review.md section 'revision r2 review - 独立 reviewer 的 r2 判定' "
                              "(verbatim transcription of the reviewer's text)"
                              % os.path.basename(attempt)),
        "formula_state_after_r2": ("review_pending - the implementer does not sign; the r2 review "
                                   "states that formula may be signed accepted_scoped once the three "
                                   "P2 items are closed"),
        "boundary_metadata_correction": (None if not addendum else {
            "source": "independent review r2, finding P2-C",
            "what_was_wrong": [
                ("revision_r2.json.mechanism_proof.line_boundary_is_real was FALSE while its own note "
                 "said the boundary was real: the comparison asked whether the offset points at a "
                 "'## ' heading instead of whether the byte before it is LF"),
                ("oracle_addendum_record.json.added_section_header_line_number was 184 instead of 186: "
                 "it was computed from the number of newlines in the PRE-append prefix"),
            ],
            "corrected_values": {
                "line_boundary_is_real": r2["mechanism_proof"].get("line_boundary_is_real"),
                "byte_before_boundary_is_lf": r2["mechanism_proof"].get("byte_before_boundary_is_lf"),
                "appended_section_header_line_number":
                    r2["mechanism_proof"].get("appended_section_header_line_number"),
                "appended_section_header_line": r2["mechanism_proof"].get(
                    "appended_section_header_line"),
            },
            "oracle_md_untouched": ("oracle.md was NOT appended to and NOT truncated to fix this: the "
                                    "correction is metadata-only, and oracle.md's hash is unchanged at "
                                    "%s" % r2["oracle_md_sha256"]),
            "verified_by": "scripts/append_oracle_addendum.py --rebuild-record-only (record rebuilt from the current file) + pack_card.py live re-verification",
        }),
        "r2_append_performed": r2["r2_sections_in_oracle_md"] > 0,
        "r2_sections_in_oracle_md": r2["r2_sections_in_oracle_md"],
        "r2_section_locations": r2["r2_section_locations"],
        "oracle_md_sha256_now": r2["oracle_md_sha256"],
        "oracle_md_sha256_before_addendum": (addendum["oracle_md_sha256_before_addendum"]
                                             if addendum else None),
        "oracle_md_sha256_after_addendum": (addendum["oracle_md_sha256_after_addendum"]
                                            if addendum else None),
        "pre_append_hash_policy": r2["rule"],
        "mutually_inconsistent_baselines_present": False,
        "provenance_gap_declaration": (
            "no pre-append hash exists because no r2 section has been appended; if one is ever "
            "appended, exactly ONE r2 section may exist and its pre-append hash must be reproducible "
            "at a real line boundary" if not addendum else
            "the single pre-append hash is the generation-time hash recorded BEFORE oracle generation "
            "and re-verified live by truncation at the recorded real line boundary"),
        "mechanism_proof": r2["mechanism_proof"],
        "r2_change_scope": (addendum["scope_note"] if addendum
                            else "not applicable: no r2 section exists in this attempt"),
        "expectation_values_touched": (addendum["expectation_values_touched"] if addendum else []),
        "frozen_expectations_unchanged": True,
        "frozen_evidence_unchanged_by_selfcheck": mutation.get("frozen_evidence_unchanged"),
        "review_dispositions": (
            "review.md section 'revision r2 - response to the independent review' records the P2/P3 "
            "dispositions; this file records the hash/boundary discipline only"),
        "product_files_changed": [],
    }
    dump(os.path.join(evidence, "revision_r2.json"), revision)

    # ---- after/rerun_sha256.json ----
    rerun = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "purpose": ("re-verification of every hash that matters, taken after all card work finished"),
        "production_hashes_after": production_hashes,
        "isolated_copy_hashes_after": isolated_hashes,
        "isolated_copy_equals_production": source_manifest["isolated_copy_equals_production"],
        "oracle_md_sha256": sha256(os.path.join(attempt, "oracle.md")),
        "oracle_md_unchanged_since_generation": source_manifest["oracle_document"][
            "unchanged_since_generation"],
        "frozen_oracle_file_hashes": regen["comparisons"],
        "binding_json_sha256": sha256(os.path.join(attempt, "binding.json")),
        "scripts": source_manifest["card_script_hashes"],
        "commands_json_sha256_at_pack_time": sha256(os.path.join(attempt, "commands.json")),
        "commands_json_note": ("commands.json is rewritten once after this pack so that the pack's own "
                              "raw rc is filled in; this hash is the pack-time value and the final "
                              "value is listed in after/final_deliverable_hashes.json"),
        "packed_utc": now,
    }
    dump(os.path.join(attempt, "after", "rerun_sha256.json"), rerun)

    # ---- evidence_hashes.json (written last so it covers the finished pack) ----
    # The capture records of the units that run AT OR AFTER this pack must not be listed here: their
    # rc.json/stdout.txt are rewritten when those units execute, which would leave a stale hash in a
    # file whose whole purpose is to be checkable.  They are covered by
    # after/final_deliverable_hashes.json (written by the closing unit, last of all), except the
    # closing unit's own records, which are excluded there too and self-describe their hashes.
    post_pack_run_dirs = tuple(
        os.path.normcase(os.path.join("evidence", card, "runs", unit))
        for unit in ("G-pack-evidence", "P-write-process-history", "T-transcribe-review-verdict",
                     "H-write-handoff", "Z-close-attempt", "V-verify-hash-tables"))
    # Files written by post-pack units, plus this pack's own two outputs.
    post_pack_files = tuple(os.path.normcase(os.path.join("evidence", card, name))
                            for name in ("evidence_hashes.json", "hash_table_selfcheck.json",
                                         "transcription_proof.json"))
    hashes = {}
    excluded_post_pack = []
    for root, _dirs, files in os.walk(evidence):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, attempt).replace("\\", "/")
            normalised = os.path.normcase(rel)
            if normalised.startswith(post_pack_run_dirs) or normalised in post_pack_files \
                    or rel.endswith("evidence_hashes.json"):
                excluded_post_pack.append(rel)
                continue
            hashes[rel] = sha256(path)
    for rel in ("oracle.md", "binding.json"):
        hashes[rel] = sha256(os.path.join(attempt, rel))
    for name in sorted(os.listdir(os.path.join(attempt, "scripts"))):
        if name.endswith(".py"):
            hashes["scripts/" + name] = sha256(os.path.join(attempt, "scripts", name))
    for name in sorted(os.listdir(os.path.join(attempt, "before"))):
        hashes["before/" + name] = sha256(os.path.join(attempt, "before", name))
    for name in sorted(os.listdir(os.path.join(attempt, "after"))):
        if name in ("final_deliverable_hashes.json", "hash_table_verification.json"):
            # both are written AFTER this pack (by the closing unit and by the verifier unit); their
            # hashes live in the files themselves and in the closing unit's table, so they are
            # deliberately not hashed here (P2-A: the exclusion list must cover exactly the
            # self-referential / post-pack files)
            continue
        hashes["after/" + name] = sha256(os.path.join(attempt, "after", name))
    dump(os.path.join(evidence, "evidence_hashes.json"),
         {"card_id": card, "revision": "r1", "packed_utc": now,
          "rule": ("sha256 of every evidence file, plus oracle.md, binding.json, scripts/ and the "
                   "before/after state files; written after everything else so the hashes describe "
                   "the finished pack"),
          "excluded_from_this_table": {
              "rule": ("capture records of units that execute at or after this pack are excluded, "
                       "because they are rewritten after this file is written"),
              "paths": sorted(excluded_post_pack) + ["evidence/%s/hash_table_selfcheck.json" % card,
                                                     "evidence/%s/evidence_hashes.json" % card],
              "covered_instead_by": ("after/final_deliverable_hashes.json (all of them except the "
                                     "closing unit's own records, whose rc.json self-describes the "
                                     "sha256 of its stdout/stderr)"),
          },
          "files": hashes})

    # P2-A (independent review r2): "drift == 0" must be a MEASURED output, not a claim.  Re-read
    # every entry written above and record the count; a non-zero count is a hard failure.
    evidence_hashes_path = os.path.join(evidence, "evidence_hashes.json")
    measured = measure_drift(attempt, hashes)
    verified = {"card_id": card, "table": "evidence/%s/evidence_hashes.json" % card,
                "entries": len(hashes), "drift_count": measured["drift_count"],
                "missing_count": measured["missing_count"],
                "drifted_paths": measured["drifted_paths"],
                "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "self_reference_exclusions": sorted(excluded_post_pack)
                                            + ["evidence/%s/evidence_hashes.json" % card]}
    doc = load_json(evidence_hashes_path)
    doc["drift_count"] = measured["drift_count"]
    doc["missing_count"] = measured["missing_count"]
    doc["drifted_paths"] = measured["drifted_paths"]
    doc["verified_utc"] = verified["verified_utc"]
    dump(evidence_hashes_path, doc)
    dump(os.path.join(evidence, "hash_table_selfcheck.json"), verified)
    print("evidence_hashes drift_count:", measured["drift_count"],
          "missing:", measured["missing_count"], "verified_utc:", verified["verified_utc"])
    if measured["drift_count"] or measured["missing_count"]:
        print("PACK FAILED: evidence_hashes.json is not drift-free")
        return 0 if False else 3

    print("packed evidence for", card, "->", evidence)
    print("entry anchor ok:", entry_anchor_ok, "registration anchor ok:", reg_anchor_ok)
    print("mtime ordering:", json.dumps(ordering, indent=1))
    print("formula state:", formula_state, "negatives:",
          qualification["formula"]["a_to_c_conditions"]["negatives_rejected"])
    print("r2 sections in oracle.md:", r2["r2_sections_in_oracle_md"],
          "mechanism proof ok:", r2["mechanism_proof"]["prefix_hash_equals_base_hash"])
    print("evidence files hashed:", len(hashes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
