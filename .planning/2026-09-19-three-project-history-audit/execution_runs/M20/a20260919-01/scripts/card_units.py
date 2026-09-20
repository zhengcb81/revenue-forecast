"""Single source of truth for the command units of one card attempt.

Every argv below is built from absolute paths of THIS attempt and nothing else, so
commands.json / command_manifest.json cannot point at a file that does not exist
(see write_commands.py, which refuses to record a path that is missing unless the
unit explicitly declares it as an output it creates).

Units are listed in chronological order; run_pipeline.py executes exactly this list.
"""

from __future__ import annotations

import os

CARDS = {
    "M17": {"model_id": "licensing_commercial", "title": "commercial sales and licensing revenue",
            "registration_line": 237},
    "M18": {"model_id": "advertising", "title": "impression fill and CPM",
            "registration_line": 238},
    "M19": {"model_id": "gaming", "title": "active-user payer monetisation",
            "registration_line": 239},
    "M20": {"model_id": "cohort_subscription", "title": "customer flow and time exposure",
            "registration_line": 240},
}

PRODUCTION_ROOT = r"C:\Users\郑曾波\Projects\revenue-forecast"
TEMPLATE_INTERPRETER = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
                        r"\2026-09-19-three-project-history-audit\execution_runs\I-00-A"
                        r"\a20260919-01\iso\venv\Scripts\python.exe")
ENTRY_POINT_LINE = 308


def paths(card, attempt_root):
    attempt = os.path.abspath(attempt_root)
    p = {
        "attempt": attempt,
        "scripts": os.path.join(attempt, "scripts"),
        "evidence": os.path.join(attempt, "evidence", card),
        "runs": os.path.join(attempt, "evidence", card, "runs"),
        "code_root": os.path.join(attempt, "iso", "checkout_scripts"),
        "venv": os.path.join(attempt, "iso", "venv"),
        "oracle_md": os.path.join(attempt, "oracle.md"),
        "recovery": os.path.join(attempt, "recovery"),
    }
    p["interpreter"] = os.path.join(p["venv"], "Scripts", "python.exe")
    return p


def _run(p, unit_id, argv, expected_rc, purpose, creates=(), note=None, extra=None,
         stdout=None, stderr=None):
    run_dir = os.path.join(p["runs"], unit_id)
    record = {
        "unit_id": unit_id,
        "purpose": purpose,
        "cwd": p["attempt"],
        "argv": list(argv),
        "network": "disabled",
        "expected_rc": expected_rc,
        "creates": [os.path.abspath(c) for c in creates],
        "stdout": stdout or os.path.join(run_dir, "stdout.txt"),
        "stderr": stderr or os.path.join(run_dir, "stderr.txt"),
        "rc_record": os.path.join(run_dir, "rc.json"),
    }
    if note:
        record["note"] = note
    if extra:
        record.update(extra)
    return record


def build_units(card, attempt_root):
    """Return the chronological unit list for one card attempt."""
    p = paths(card, attempt_root)
    interp = p["interpreter"]
    py = [interp, "-X", "utf8", "-B"]
    info = CARDS[card]
    units = []

    # A0: the attempt-local venv, created from the I-00-A template interpreter.
    units.append(_run(
        p, "A0-iso-venv-create",
        [TEMPLATE_INTERPRETER, "-m", "venv", p["venv"]],
        0,
        ("create (or refresh) the attempt-local isolated interpreter from the I-00-A template "
         "venv; no global Miniconda python is used anywhere in this card"),
        creates=[os.path.join(p["venv"], "Scripts", "python.exe")],
        note=("the template interpreter is itself an isolated venv; it is used for this creation "
              "step and for nothing else in the card")))

    # A0b: prove pytest cannot be installed offline here (recorded, not assumed).
    units.append(_run(
        p, "A0b-pytest-offline-availability",
        [interp, "-m", "pip", "download", "pytest", "--no-index", "--no-cache-dir",
         "-d", os.path.join(p["recovery"], "wheels_probe")],
        1,
        ("record whether pytest can be installed offline from the local cache; --no-index touches "
         "no network"),
        creates=[os.path.join(p["recovery"], "wheels_probe")],
        note=("expected_rc 1 means the offline probe failed, i.e. no local wheel is available; no "
              "card command requires pytest and the historical 97 tests / 216 subtests are "
              "explicitly not a substitute for this card's results")))

    # A1: read-only isolated snapshot of the two product modules.
    units.append(_run(
        p, "A1-isolated-snapshot",
        py + [os.path.join(p["scripts"], "snapshot_copy.py"),
              "--production-root", PRODUCTION_ROOT, "--dest", p["code_root"],
              "--record", os.path.join(p["runs"], "A1-isolated-snapshot", "snapshot.json")],
        0,
        ("copy scripts/model_registry.py and scripts/model_extensions.py read-only from production "
         "into this attempt and verify the copies are byte-identical"),
        creates=[os.path.join(p["runs"], "A1-isolated-snapshot", "snapshot.json"),
                 os.path.join(p["code_root"], "model_registry.py"),
                 os.path.join(p["code_root"], "model_extensions.py")]))

    # G0: repository state before any product run.
    units.append(_run(
        p, "G0-state-before",
        py + [os.path.join(p["scripts"], "hash_state.py"),
              "--out", os.path.join(p["attempt"], "before"), "--attempt-root", p["attempt"]],
        0,
        "capture git status --porcelain and watched source hashes for the three repos (read-only)",
        creates=[os.path.join(p["attempt"], "before", "state.json"),
                 os.path.join(p["attempt"], "before", "source_hashes.txt")]))

    # A2: freeze record + oracle generation (oracle.md must already exist).
    units.append(_run(
        p, "A2-oracle-generate",
        py + [os.path.join(p["scripts"], "gen_oracle.py"), "--card", card,
              "--attempt-root", p["attempt"], "--interpreter", interp],
        0,
        ("record oracle.md's sha256/mtime BEFORE generating, then generate the frozen "
         "input.json / oracle.json / cases.json with the independent stdlib oracle script"),
        creates=[os.path.join(p["evidence"], "input.json"),
                 os.path.join(p["evidence"], "oracle.json"),
                 os.path.join(p["evidence"], "cases.json"),
                 os.path.join(p["evidence"], "oracle_selfcheck.json"),
                 os.path.join(p["evidence"], "oracle_document_freeze.json")],
        note="the oracle script never imports the product; it is the only source of expectations"))

    # A3: binding, written after the freeze and before the product run.
    units.append(_run(
        p, "A3-write-binding",
        py + [os.path.join(p["scripts"], "write_binding.py"),
              "--card", card, "--attempt-root", p["attempt"], "--interpreter", interp,
              "--orchestrator-interpreter", TEMPLATE_INTERPRETER],
        0,
        ("write binding.json: absolute paths, production and isolated hashes, the model contract "
         "read back from the isolated snapshot, and the write allowlist"),
        creates=[os.path.join(p["attempt"], "binding.json")]))

    # B: the one and only product invocation.
    units.append(_run(
        p, "B-product-run",
        py + [os.path.join(p["scripts"], "run_card.py"), "--card", card,
              "--attempt", p["attempt"], "--code-root", p["code_root"],
              "--out", os.path.join(p["evidence"], "run_result.json"),
              "--run-result-out", os.path.join(p["evidence"], "formula_result.json"),
              "--negative-out", os.path.join(p["evidence"], "negative_results.json")],
        0,
        ("run the ONLY product entry point calculate_registered_model against the isolated snapshot: "
         "positive, continuity positive, defaults case, observations and 11 negative cases"),
        creates=[os.path.join(p["evidence"], "run_result.json"),
                 os.path.join(p["evidence"], "formula_result.json"),
                 os.path.join(p["evidence"], "negative_results.json")],
        stdout=os.path.join(p["evidence"], "stdout.txt"),
        stderr=os.path.join(p["evidence"], "stderr.txt"),
        extra={"expected_business_result": ("verdict pass: the positive value is within "
                                            "1e-9*max(1,|expected|), the output length equals "
                                            "len(years), the continuity positive matches and all 11 "
                                            "negatives are rejected with ModelRegistryError")}))

    # C: registry enumeration feeding oq_rulings.json counts.
    units.append(_run(
        p, "C-registry-enumeration",
        py + [os.path.join(p["scripts"], "enumerate_registry.py"), "--code-root", p["code_root"],
              "--card", card, "--out", os.path.join(p["evidence"], "registry_enumeration.json")],
        0,
        ("enumerate the whole registry from the isolated copy so every count in oq_rulings.json "
         "comes from a script rather than from prose"),
        creates=[os.path.join(p["evidence"], "registry_enumeration.json")]))

    # C2: measured boundary probes (non-gating, not part of the frozen oracle).
    units.append(_run(
        p, "C2-extra-boundary-probes",
        py + [os.path.join(p["scripts"], "probe_extra.py"), "--card", card,
              "--attempt-root", p["attempt"], "--code-root", p["code_root"]],
        0,
        ("measure the edges of the enumerated domains (signed amount driver, total-revenue guard, "
         "ratio/quantity edges, bridge tolerance) as NON-GATING observations"),
        creates=[os.path.join(p["evidence"], "extra_probes.json")],
        note=("these probes are not part of oracle.json and do not enter the runner's exit code; each "
              "expectation is computed in probe_extra.py before the call")))

    # D: byte-for-byte regeneration proof of the frozen oracle.
    units.append(_run(
        p, "D-oracle-regen-verify",
        py + [os.path.join(p["scripts"], "verify_oracle_regen.py"), "--card", card,
              "--attempt-root", p["attempt"], "--interpreter", interp],
        0,
        ("regenerate input.json / oracle.json / cases.json into an empty scratch tree and compare "
         "sha256 against the frozen files"),
        creates=[os.path.join(p["evidence"], "oracle_regen_proof.json")]))

    # E: mutation self-check (red first, then green).
    units.append(_run(
        p, "E-mutation-selfcheck",
        py + [os.path.join(p["scripts"], "mutation_selfcheck.py"), "--card", card,
              "--attempt-root", p["attempt"], "--interpreter", interp],
        0,
        ("corrupt COPIES of the frozen expectation and of a negative assertion and show the runner "
         "turns red (rc 3 / rc 2 / rc 1), then show green (rc 0) returns on the uncorrupted copy"),
        creates=[os.path.join(p["evidence"], "mutation_selfcheck.json"),
                 os.path.join(p["recovery"], "selfcheck_result.json")]))

    # G1: repository state after all product work.
    units.append(_run(
        p, "G1-state-after",
        py + [os.path.join(p["scripts"], "hash_state.py"),
              "--out", os.path.join(p["attempt"], "after"), "--attempt-root", p["attempt"]],
        0,
        "capture the same repository state again to prove no production file changed",
        creates=[os.path.join(p["attempt"], "after", "state.json"),
                 os.path.join(p["attempt"], "after", "source_hashes.txt")]))

    # F: command record (attempt root commands.json + evidence command_manifest.json).
    units.append(_run(
        p, "F-write-commands",
        py + [os.path.join(p["scripts"], "write_commands.py"), "--card", card,
              "--attempt-root", p["attempt"], "--interpreter", interp, "--phase", "post"],
        0,
        "record every unit's real argv, raw rc and outputs into commands.json and command_manifest.json",
        creates=[os.path.join(p["attempt"], "commands.json"),
                 os.path.join(p["evidence"], "command_manifest.json")]))

    # G: evidence pack (hashes last).
    units.append(_run(
        p, "G-pack-evidence",
        py + [os.path.join(p["scripts"], "pack_card.py"), "--card", card,
              "--attempt-root", p["attempt"]],
        0,
        ("pack source_manifest / qualification / oq_rulings / integrity / revision_r2 and hash every "
         "evidence file (hashes written last, so they cover the finished pack)"),
        creates=[os.path.join(p["evidence"], "source_manifest.json"),
                 os.path.join(p["evidence"], "qualification.json"),
                 os.path.join(p["evidence"], "oq_rulings.json"),
                 os.path.join(p["evidence"], "integrity.json"),
                 os.path.join(p["evidence"], "revision_r2.json"),
                 os.path.join(p["evidence"], "evidence_hashes.json"),
                 os.path.join(p["attempt"], "after", "rerun_sha256.json")]))

    return units


def closing_units(card, attempt_root):
    """Units executed after the pack: handoff generation, then the closing recorder.

    They are separate from build_units() because run_pipeline.py runs the measurement chain and
    stops there; the closing units only read evidence and write records, and they are executed
    individually with the same capture mechanism (run_unit.py), so each still has its own
    command-run-id directory with raw stdout/stderr/rc.
    """
    p = paths(card, attempt_root)
    interp = p["interpreter"]
    py = [interp, "-X", "utf8", "-B"]
    return [
        _run(
            p, "H-write-handoff",
            py + [os.path.join(p["scripts"], "write_handoff.py"), "--card", card,
                  "--attempt-root", p["attempt"]],
            0,
            ("generate handoff.json from the evidence on disk: hashes, raw exit codes, open "
             "questions and the first unfinished card action"),
            creates=[os.path.join(p["attempt"], "handoff.json")]),
        _run(
            p, "Z-close-attempt",
            py + [os.path.join(p["scripts"], "close_attempt.py"), "--card", card,
                  "--attempt-root", p["attempt"], "--interpreter", interp],
            0,
            ("record the completed command list into commands.json and write "
             "after/final_deliverable_hashes.json as the last artefact of the attempt"),
            creates=[os.path.join(p["attempt"], "commands.json"),
                     os.path.join(p["attempt"], "after", "final_deliverable_hashes.json")],
            note=("the rc recorded for this unit in commands.json, if present, comes from a PREVIOUS "
                  "execution of the identical argv, because this unit's rc.json is only refreshed "
                  "after it returns; the most recent execution's raw rc is always in "
                  "evidence/<card>/runs/Z-close-attempt/rc.json")),
    ]
