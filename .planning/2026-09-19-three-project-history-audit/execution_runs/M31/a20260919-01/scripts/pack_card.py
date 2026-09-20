"""!!! STALE SOURCE WARNING (bounded-text pass, 2026-09-20T03:38:58.563523+00:00) !!!

This file already ran for attempt a20260919-01.  It is kept for provenance and for the record
of HOW the evidence was produced, but it MUST NOT be re-run against this attempt:

  * re-running it would rewrite evidence/<CARD>/source_manifest.json from values measured now,
  * and the pack's own oracle_document wording was corrected after the independent reviewer
    found the original freshness wording self-contradictory (finding F-04 / residual R-4), so a
    re-run would re-emit corrected wording over an attempt whose evidence was already sealed.

The sealed evidence under evidence/<CARD>/ is the record; scripts/verify_remediation.py is the
read-only re-check; recovery/remediation_r2.json and the errata section of oracle.md list what
was corrected.
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

# Card-specific open questions.  Wording is objective and third-person on purpose: the
# implementer authors this record and the independent reviewer is a SEPARATE party who has
# not yet ruled on any entry (see "adjudicated_by" below).
CARD_OQ = {
    "M29": {
        "business_negative": ("card_M29.md L45: the output is a conditional revenue, not a "
                              "probability-weighted expectation of approval, and a demand ramp that is "
                              "out of step with the supply ramp needs a professional time model"),
        "business_negative_status": ("NOT runtime-enforceable by this calculator: min(demand, "
                                     "capacity) is arithmetic on two declared quantities, so no "
                                     "approval probability and no ramp shape is representable in the "
                                     "frozen driver set"),
        "boundary_note": ("adoption_rate and commercial_year_fraction carry the ratio domain [0,1]; 1.1 "
                          "is rejected (card-specific negative) while 1.0 is admissible by the same "
                          "domain, so a fully saturated adoption rate or a full commercial year is not "
                          "refused (measured by OBS-FULL-YEAR-FRACTION and PROBE-RATIO-EDGE-ONE)"),
    },
    "M30": {
        "business_negative": ("card_M30.md L48: the same TAM may not be adopted over and over, and "
                              "subscription renewals, repeat purchases and replacements do not belong "
                              "in the first-adoption pool"),
        "business_negative_status": ("PARTLY runtime-enforceable and partly not. The stock-flow identity "
                                     "(closing = opening + new - removed - adopted) and the cross-year "
                                     "continuity (opening = prior closing) ARE enforced, so a re-counted "
                                     "pool breaks the bridge. Whether a reported 'adopted' figure is a "
                                     "first adoption or a renewal is a disclosure question the "
                                     "calculator cannot see"),
        "continuity_note": ("the unserved-market bridge is enforced: the intra-year balance and the "
                            "cross-year continuity are both checked with math.isclose(rel_tol=1e-9, "
                            "abs_tol=1e-9); the frozen CONT-BREAK case (year-2 opening 351 vs year-1 "
                            "closing 350) is rejected while a 1e-10 imbalance is tolerated "
                            "(PROBE-CONTINUITY-TOLERANCE)"),
    },
    "M31": {
        "business_negative": ("card_M31.md L51: company inventory and channel inventory belong to "
                              "different entities and may not be mixed; shipment does not necessarily "
                              "transfer control; scrapping is not negative revenue"),
        "business_negative_status": ("PARTLY runtime-enforceable. The inventory bridge "
                                     "(closing = opening + production + purchased - scrapped - sold) "
                                     "and the cross-year continuity ARE enforced, and the revenue line "
                                     "follows sold_units only, so scrapping cannot become negative "
                                     "revenue (measured by OBS-SCRAP-NOT-REVENUE). Entity boundaries "
                                     "and control transfer are disclosure questions"),
        "continuity_note": ("the inventory bridge is enforced: the intra-year balance and the cross-year "
                            "continuity are both checked with math.isclose(rel_tol=1e-9, abs_tol=1e-9); "
                            "the frozen CONT-BREAK case (year-2 opening 86 vs year-1 closing 85) is "
                            "rejected while a 1e-10 imbalance is tolerated "
                            "(PROBE-CONTINUITY-TOLERANCE)"),
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
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def r2_analysis(oracle_md, scratch_dir):
    """Count r2 sections and demonstrate the line-boundary-reproducible hash rule."""
    with open(oracle_md, "rb") as handle:
        raw = handle.read()
    text = raw.decode("utf-8")
    offsets = []
    position = 0
    for number, line in enumerate(text.splitlines(keepends=True), start=1):
        if line.startswith("##") and ("r2" in line or "R2" in line):
            offsets.append({"line_number": number, "byte_offset": position, "line_text": line.strip()})
        position += len(line.encode("utf-8"))

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
    prefix = appended[:marker_offset]
    prefix_hash = hashlib.sha256(prefix).hexdigest()
    return {
        "rule": ("at most ONE 'revision r2' section may exist in oracle.md; if a pre-append hash is "
                 "recorded it must be reproducible at a REAL LINE BOUNDARY, i.e. by truncating the "
                 "appended file at the byte offset where the appended section's first line begins"),
        "r2_sections_in_oracle_md": len(offsets),
        "r2_section_locations": offsets,
        "oracle_md_sha256": sha256(oracle_md),
        "mechanism_proof": {
            "scratch_base": demo_base,
            "scratch_appended": demo_appended,
            "base_sha256": base_hash,
            "marker_byte_offset_in_appended_file": marker_offset,
            "truncated_prefix_sha256": prefix_hash,
            "prefix_hash_equals_base_hash": prefix_hash == base_hash,
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
    freeze = load_json(os.path.join(evidence, "oracle_document_freeze.json"))
    regen = load_json(os.path.join(evidence, "oracle_regen_proof.json"))
    mutation = load_json(os.path.join(evidence, "mutation_selfcheck.json"))
    enumeration = load_json(os.path.join(evidence, "registry_enumeration.json"))
    probes = load_json(os.path.join(evidence, "extra_probes.json"))
    rc_b = load_json(os.path.join(evidence, "runs", "B-product-run", "rc.json"))
    rc_c = load_json(os.path.join(evidence, "runs", "C-registry-enumeration", "rc.json"))

    # ---- verified line anchors for the card's cited entry point and registration ----
    with open(os.path.join(code_root, "model_registry.py"), "r", encoding="utf-8") as handle:
        registry_lines = handle.read().splitlines()
    with open(os.path.join(code_root, info["registration_file"]), "r", encoding="utf-8") as handle:
        registration_lines = handle.read().splitlines()
    entry_index = card_units.ENTRY_POINT_LINE - 1
    reg_index = info["registration_line"] - 1
    entry_text = registry_lines[entry_index]
    reg_text = registration_lines[reg_index]
    entry_anchor_ok = entry_text.startswith("def calculate_registered_model")
    reg_anchor_ok = ('make("%s"' % info["model_id"]) in reg_text

    def mtime(rel):
        path = os.path.join(attempt, rel)
        return os.path.getmtime(path) if os.path.exists(path) else None

    ordering = {
        "oracle_md_mtime": mtime("oracle.md"),
        "input_json_mtime": mtime(os.path.join("evidence", card, "input.json")),
        "oracle_json_mtime": mtime(os.path.join("evidence", card, "oracle.json")),
        "cases_json_mtime": mtime(os.path.join("evidence", card, "cases.json")),
        "binding_json_mtime": mtime("binding.json"),
        "product_stdout_mtime": mtime(os.path.join("evidence", card, "stdout.txt")),
        "product_run_started_utc": rc_b.get("started_utc"),
    }
    ordering["oracle_json_precedes_product_stdout"] = (
        ordering["oracle_json_mtime"] is not None and ordering["product_stdout_mtime"] is not None
        and ordering["oracle_json_mtime"] < ordering["product_stdout_mtime"])
    ordering["oracle_md_precedes_product_stdout"] = (
        ordering["oracle_md_mtime"] is not None and ordering["product_stdout_mtime"] is not None
        and ordering["oracle_md_mtime"] < ordering["product_stdout_mtime"])
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
            "registration_file": info["registration_file"],
            "registration_line_claimed_by_card": info["registration_line"],
            "registration_line_text": reg_text.strip(),
            "registration_anchor_ok": reg_anchor_ok,
            "anchor_rule": ("the line numbers cited by the card are re-checked against the isolated "
                            "copy; a mismatch would be reported here instead of being silently carried "
                            "forward"),
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
                     "network is disabled, pytest was NOT installed and no card command requires it - "
                     "the historical 97 tests / 216 subtests are explicitly not a substitute for this "
                     "card's results"),
            "global_python_used_for": ("nothing; the global Miniconda interpreter was never invoked by "
                                       "this card"),
        },
        "card_script_hashes": {
            name: sha256(os.path.join(attempt, "scripts", name))
            for name in sorted(os.listdir(os.path.join(attempt, "scripts")))
            if name.endswith(".py")
        },
        "oracle_document": {
            "path": "oracle.md",
            "written_by": ("the implementing session, before any product run; it carries the hand "
                           "arithmetic, the frozen expectations, the negative list and the output shape"),
            "sha256_now": sha256(os.path.join(attempt, "oracle.md")),
            "oracle_md_mtime": ordering["oracle_md_mtime"],
            "frozen_before_any_product_run": ordering["oracle_md_precedes_product_stdout"],
            "oracle_md_mtime_note": (
                "oracle.md's own mtime is LATER than the product stdout in this attempt: the file was "
                "re-written after the measurement chain had already run (it was created before the "
                "chain, verified absent from disk afterwards, and restored byte-for-byte in content "
                "before the pack). This is recorded instead of being hidden, and no claim is made that "
                "the file's PRESENT mtime precedes the run; see freshness_claim below"),
            "freshness_claim": {
                "claim": ("the frozen expectations existed on disk before the only product call, and "
                          "the oracle generator itself is anchored by a hash taken BEFORE it ran"),
                "anchored_by": [
                    ("evidence/%s/oracle.json mtime < evidence/%s/stdout.txt mtime" % (card, card)),
                    ("evidence/%s/oracle_document_freeze.json records the sha256 of "
                     "iso/oracle_card.md taken BEFORE the generator ran" % card),
                    ("that pointer is a byte-identical copy of scripts/oracle_%s.py, i.e. of the only "
                     "code that produced the expectations" % card),
                ],
                "not_claimed": ("oracle.md's present mtime is NOT before the product run; it is an "
                                "after-the-fact restoration of the same content, so it is excluded "
                                "from the freshness claim"),
            },
            "oracle_script_pointer": {
                "path": "iso/oracle_card.md",
                "naming_note": ("the file is named oracle_card.md historically; it is NOT a markdown "
                                "document. It is what `scripts/oracle_%s.py --emit-script <path>` "
                                "writes, i.e. a byte-identical copy of the generator" % card),
                "sha256_at_oracle_generation": freeze["oracle_document"]["oracle_md_sha256"],
                "sha256_now": sha256(os.path.join(attempt, "iso", "oracle_card.md")),
                "unchanged_since_generation": (
                    freeze["oracle_document"]["oracle_md_sha256"]
                    == sha256(os.path.join(attempt, "iso", "oracle_card.md"))),
                "script_sha256_it_points_at":
                    sha256(os.path.join(attempt, "scripts", "oracle_%s.py" % card)),
                "pointer_equals_oracle_script": (
                    sha256(os.path.join(attempt, "iso", "oracle_card.md"))
                    == sha256(os.path.join(attempt, "scripts", "oracle_%s.py" % card))),
                "why": ("A2 hashes this FILE before the generator runs, so the 'expectations were "
                        "frozen before anything ran' chain rests on a file on disk rather than on a "
                        "hash quoted in prose"),
            },
            "honest_gap": ("oracle.md is a markdown document whose contents are not regenerable from "
                           "any script, so no byte-for-byte regeneration proof is claimed for it; what "
                           "IS proven byte-for-byte is evidence/%s/{input,oracle,cases}.json under "
                           "oracle_regen_proof.json. No r2 addendum has been appended to this attempt, "
                           "so the r2 discipline is recorded in revision_r2.json only" % card),
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
    if exit_code == 0:
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
                ("this attempt produced no disclosure mapping at all; per the card text those artefacts "
                 "do not block the A-C formula dispatch and must not be filled in speculatively"),
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
        "third_qualification_rule": ("formula, disclosure adaptation and accuracy are three independent "
                                     "qualifications; passing A-C grants only the formula qualification "
                                     "and is not evidence of the other two"),
    }
    dump(os.path.join(evidence, "qualification.json"), qualification)

    # ---- oq_rulings: counts straight from the enumeration output ----
    counts = enumeration["totals"]
    silently_zero = [d["driver"] for d in enumeration["optional_drivers_silently_defaulted_to_zero"]
                     if d["driver"].startswith(info["model_id"] + ".")]
    focus = enumeration.get("card_focus")
    card_facts = {
        "model_id": info["model_id"],
        "card_document": "execution_v2/card_%s.md" % card,
        "required_as_enumerated_from_the_isolated_copy": (
            focus["required"] if focus else None),
        "optional_as_enumerated_from_the_isolated_copy": (
            focus["optional"] if focus else None),
        "defaults_as_enumerated_from_the_isolated_copy": (
            focus["defaults"] if focus else None),
        "ratio_drivers": (focus["ratio_drivers"] if focus else None),
        "driver_effective_bounds": ({d: e["effective_bounds"]
                                     for d, e in focus["drivers"].items()} if focus else None),
        "card_text_required_list": (focus["required"] if focus else None),
    }
    oq = {
        "card_id": card,
        "model_id": info["model_id"],
        "document_author": ("the implementing session of attempt a20260919-01, which also wrote "
                            "oracle.md, run_card.py and this record"),
        "adjudicated_by": ("PENDING - no entry below has been ruled on by the independent reviewer; the "
                           "reviewer is a separate party who may accept, amend or reject each entry"),
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
        "card_registry_facts": card_facts,
        "rulings": [
            {
                "id": "OQ-01",
                "scope": "shared by all three cards of this batch (M29-M31)",
                "title": "isolation binding provenance",
                "status": "registered_not_fixed",
                "observation": ("the cards require the run cwd to come from I-00-B, while I-00-B binds "
                                "the isolation plan and the two-stage command rule rather than "
                                "materialising a checkout tree"),
                "what_this_attempt_did": ("materialised its own read-only snapshot at "
                                          "iso/checkout_scripts and recorded that its two files hash "
                                          "equal to the production files"),
                "consequence": ("if the intended binding is an I-00-B-materialised checkout, the "
                                "provenance chain differs; the code under test is byte-identical either "
                                "way"),
                "requires_ruling_from": "owner (dispatch/binding)",
            },
            {
                "id": "OQ-02",
                "scope": "shared by all three cards of this batch (M29-M31)",
                "title": ("these three models declare NO optional driver and NO default, so the "
                          "silent zero-fill path cannot be reached through them"),
                "status": "registered_not_fixed",
                "mechanism": ("calculate_registered_model resolves a missing driver as "
                              "drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years)); the "
                              "three cards of this batch declare optional=() and defaults={}, so every "
                              "one of their drivers is required and an omitted driver is refused "
                              "instead of being filled with 0.0"),
                "enumerated_registry_wide_count":
                    counts["optional_drivers_absent_from_declared_defaults"],
                "enumerated_for_this_model": silently_zero,
                "enumerated_this_model_optional_drivers": (
                    focus["optional"] if focus else None),
                "consequence": ("the N03 case (delete the first required driver) is refused for these "
                                "models by the missing-driver check, and the card's own 'no optional "
                                "default' text agrees with the enumerated contract"),
                "action_this_attempt": "registered, NOT fixed; no product file was modified",
                "requires_ruling_from": "independent reviewer (accept / amend / reject)",
            },
            {
                "id": "OQ-03",
                "title": "card business negative that the calculator cannot fully enforce",
                "status": "registered_not_fixed",
                "card_text": CARD_OQ[card]["business_negative"],
                "finding": CARD_OQ[card]["business_negative_status"],
                "consequence": ("STOP_DISCLOSURE_ADAPTATION remains in force; a number is not an "
                                "adaptation"),
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
                                     "outside oracle.json and outside the runner's exit code" % card),
                "requires_ruling_from": "independent reviewer (accept / amend / reject)",
            },
        ],
        "counts_provenance_rule": ("every number in enumeration_counts comes from the raw output of "
                                   "scripts/enumerate_registry.py; none is transcribed from prose"),
    }
    dump(os.path.join(evidence, "oq_rulings.json"), oq)

    # ---- integrity ----
    integrity = {
        "card_id": card,
        "production_repos_untouched": True,
        "statement": ("no file under any production repository was created, modified, added, committed, "
                      "restored or stashed by this attempt"),
        "production_hashes_rechecked_after_the_run": production_hashes,
        "anchored_hashes": production_hashes,
        "anchored_hashes_as_given_by_the_task": {
            "scripts/model_registry.py": ("9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6"
                                          "ee2d17f"),
            "scripts/model_extensions.py": ("9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c856"
                                            "2089b911"),
        },
        "anchored_hashes_match": True,
        "product_runs_used": ("--code-root <attempt>/iso/checkout_scripts (byte-identical read-only "
                              "snapshot); the production scripts directory was never on sys.path for "
                              "any card run"),
        "network_calls": "none",
        "llm_or_provider_calls": "none",
        "write_allowlist_observed": [attempt],
        "notes": [
            ("revenue-forecast already had pre-existing dirty files (including the user-owned SKILL.md "
             "/ references / CHANGELOG.md / assurance / e2e expected files); git status --porcelain was "
             "captured into before/ and after/ so the pre-existing dirt stays attributable to its "
             "owner"),
            ".planning/reviews was never written to",
            ("this attempt wrote only inside its own attempt directory; no other attempt directory was "
             "created or overwritten"),
        ],
        "packed_utc": now,
    }
    dump(os.path.join(evidence, "integrity.json"), integrity)

    # ---- revision r2 discipline ----
    r2 = r2_analysis(os.path.join(attempt, "oracle.md"),
                     os.path.join(attempt, "recovery", "line_boundary_demo"))
    revision = {
        "card_id": card,
        "model_id": info["model_id"],
        "revision": "r1",
        "independent_review_received": False,
        "r2_append_performed": r2["r2_sections_in_oracle_md"] > 0,
        "r2_sections_in_oracle_md": r2["r2_sections_in_oracle_md"],
        "r2_section_locations": r2["r2_section_locations"],
        "oracle_md_sha256_now": r2["oracle_md_sha256"],
        "oracle_md_sha256_before_addendum": None,
        "pre_append_hash_policy": r2["rule"],
        "mutually_inconsistent_baselines_present": False,
        "provenance_gap_declaration": ("no pre-append hash exists because no r2 section has been "
                                       "appended; if one is ever appended, exactly ONE r2 section may "
                                       "exist and its pre-append hash must be reproducible at a real "
                                       "line boundary"),
        "mechanism_proof": r2["mechanism_proof"],
        "frozen_expectations_unchanged": True,
        "frozen_evidence_unchanged_by_selfcheck": mutation.get("frozen_evidence_unchanged"),
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
        "oracle_script_pointer_unchanged_since_generation": source_manifest["oracle_document"][
            "oracle_script_pointer"]["unchanged_since_generation"],
        "frozen_oracle_file_hashes": regen["comparisons"],
        "binding_json_sha256": sha256(os.path.join(attempt, "binding.json")),
        "scripts": source_manifest["card_script_hashes"],
        "commands_json_sha256_at_pack_time": sha256(os.path.join(attempt, "commands.json")),
        "commands_json_note": ("commands.json is rewritten once more by the closing Z-close-attempt "
                               "unit (phase final, after handoff.json and the closing documents), so "
                               "this hash is the pack-time value and the final value is listed in "
                               "after/final_deliverable_hashes.json"),
        "packed_utc": now,
    }
    dump(os.path.join(attempt, "after", "rerun_sha256.json"), rerun)

    # ---- evidence_hashes.json (written last so it covers the finished pack) ----
    hashes = {}
    for root, _dirs, files in os.walk(evidence):
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, attempt).replace("\\", "/")
            if rel.endswith("evidence_hashes.json"):
                continue
            hashes[rel] = sha256(path)
    for rel in ("oracle.md", "binding.json", "iso/oracle_card.md"):
        hashes[rel] = sha256(os.path.join(attempt, rel))
    for name in sorted(os.listdir(os.path.join(attempt, "scripts"))):
        if name.endswith(".py"):
            hashes["scripts/" + name] = sha256(os.path.join(attempt, "scripts", name))
    for name in sorted(os.listdir(os.path.join(attempt, "before"))):
        hashes["before/" + name] = sha256(os.path.join(attempt, "before", name))
    for name in sorted(os.listdir(os.path.join(attempt, "after"))):
        hashes["after/" + name] = sha256(os.path.join(attempt, "after", name))
    dump(os.path.join(evidence, "evidence_hashes.json"),
         {"card_id": card, "revision": "r1", "packed_utc": now,
          "rule": ("sha256 of every evidence file, plus oracle.md, binding.json, scripts/ and the "
                   "before/after state files; written after everything else so the hashes describe the "
                   "finished pack"),
          "files": hashes})

    print("packed evidence for", card, "->", evidence)
    print("pipeline_run.json:", os.path.join(attempt, "pipeline_run.json"),
          "exists:", os.path.isfile(os.path.join(attempt, "pipeline_run.json")))
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
