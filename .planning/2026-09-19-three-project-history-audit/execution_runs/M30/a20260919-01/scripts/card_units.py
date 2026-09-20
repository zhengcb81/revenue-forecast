"""Single source of truth for the command units of the M30 attempt.

Every argv below is built from absolute paths of THIS attempt and nothing else, so
commands.json / command_manifest.json cannot point at a file that does not exist
(see write_commands.py, which refuses to record a path that is missing unless the
unit explicitly declares it as an output it creates).

Units are listed in chronological order; run_pipeline.py executes exactly this list.

The bootstrap steps (A0 venv creation, A2a oracle-script emit, G0 state-before) are NOT part
of this list: they ran before the pre-registered command record and their raw output is kept
in evidence/<CARD>/runs/<step>/ so the record still covers them.
"""

from __future__ import annotations

import os

CARDS = {
    "M30": {"model_id": "finite_adoption", "title": "finite market adoption",
             "registration_file": "model_extensions.py",
             "registration_line": 216},
}

PRODUCTION_ROOT = r"C:\Users\郑曾波\Projects\revenue-forecast"
TEMPLATE_INTERPRETER = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-00-A\a20260919-01\iso\venv\Scripts\python.exe")
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
        "oracle_md_src": os.path.join(attempt, "iso", "oracle_card.md"),
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
    """Return the chronological unit list for this card attempt."""
    p = paths(card, attempt_root)
    interp = p["interpreter"]
    py = [interp, "-X", "utf8", "-B"]
    units = []

    # A0-record: the attempt-local venv already exists (created in the bootstrap step).
    units.append(_run(
        p, "A0-iso-venv-record",
        py + [os.path.join(p["scripts"], "venv_probe.py"), "--out",
              os.path.join(p["recovery"], "venv_probe"), "--attempt-root", p["attempt"]],
        0,
        ("record that the attempt-local isolated interpreter exists, its sha256 and its version; the "
         "venv was created with `python -m venv` from the I-00-A template venv and no global Miniconda "
         "python is used anywhere in this card"),
        creates=[os.path.join(p["recovery"], "venv_probe", "venv_probe.json")],
        note="the venv creation itself is recorded in evidence/<CARD>/runs/A0-iso-venv-create/"))

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

    # A2: freeze record + oracle generation (oracle.md must already exist).
    units.append(_run(
        p, "A2-oracle-freeze-and-generate",
        py + [os.path.join(p["scripts"], "gen_oracle.py"), "--card", card,
              "--attempt-root", p["attempt"], "--interpreter", interp],
        0,
        ("record the oracle-script pointer's sha256/mtime BEFORE generating, then generate the frozen "
         "input.json / oracle.json / cases.json / oracle_selfcheck.json / oracle_document_freeze.json "
         "with the independent stdlib oracle script"),
        creates=[os.path.join(p["evidence"], "input.json"),
                 os.path.join(p["evidence"], "oracle.json"),
                 os.path.join(p["evidence"], "cases.json"),
                 os.path.join(p["evidence"], "oracle_selfcheck.json"),
                 os.path.join(p["evidence"], "oracle_document_freeze.json")],
        note=("the oracle script never imports the product; it is the only source of expectations. "
              "oracle.md itself is written by the implementing session with the hand arithmetic before "
              "this unit runs")))

    # A3: binding, written after the freeze and before the product run.
    units.append(_run(
        p, "A3-write-binding",
        py + [os.path.join(p["scripts"], "write_binding.py"),
              "--card", card, "--attempt-root", p["attempt"], "--interpreter", interp,
              "--orchestrator-interpreter", TEMPLATE_INTERPRETER],
        0,
        ("write binding.json: absolute paths, production and isolated hashes, the model contract read "
         "back from the isolated snapshot, the declared-driver assertion and the write allowlist"),
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
        ("enumerate the whole registry from the isolated copy so every count in oq_rulings.json comes "
         "from a script rather than from prose"),
        creates=[os.path.join(p["evidence"], "registry_enumeration.json")]))

    # C2: measured boundary probes (non-gating, not part of the frozen oracle).
    units.append(_run(
        p, "C2-extra-boundary-probes",
        py + [os.path.join(p["scripts"], "probe_extra.py"), "--card", card,
              "--attempt-root", p["attempt"], "--code-root", p["code_root"]],
        0,
        ("measure the edges of the enumerated domains (ratio edges, quantity edges, stock-flow bridge "
         "tolerance) as NON-GATING observations"),
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
        ("record every unit's real argv, raw rc and outputs into commands.json and "
         "command_manifest.json"),
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
    """Units executed after the pack: handoff, closing narrative, command record, hash ledger.

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
            ("generate handoff.json from the evidence on disk: hashes, raw exit codes, open questions "
             "and the first unfinished action for the independent reviewer"),
            creates=[os.path.join(p["attempt"], "handoff.json")]),
        _run(
            p, "H2-write-closing-docs",
            py + [os.path.join(p["scripts"], "write_closing_docs.py"), "--card", card,
                  "--attempt-root", p["attempt"]],
            0,
            ("write decision.md, review.md (self-description plus the attack points for the reviewer, "
             "never a self-signed acceptance), the explicit empty changes.diff and recovery/README.md"),
            creates=[os.path.join(p["attempt"], "decision.md"),
                     os.path.join(p["attempt"], "review.md"),
                     os.path.join(p["attempt"], "changes.diff"),
                     os.path.join(p["attempt"], "recovery", "README.md")]),
        _run(
            p, "Z-close-attempt",
            py + [os.path.join(p["scripts"], "write_commands.py"), "--card", card,
                  "--attempt-root", p["attempt"], "--interpreter", interp, "--phase", "final",
                  "--final-hashes", os.path.join(p["attempt"], "after",
                                                 "final_deliverable_hashes.json")],
            0,
            ("rewrite commands.json with the exact unit list that was executed and then write "
             "after/final_deliverable_hashes.json as the last artefact of the attempt"),
            creates=[os.path.join(p["attempt"], "commands.json"),
                     os.path.join(p["attempt"], "after", "final_deliverable_hashes.json")],
            note=("write_commands.py writes commands.json first and the hash ledger second inside "
                  "this same unit, so the ledger covers the final commands.json; the rc recorded for "
                  "this unit comes from its own rc.json, written after it returns")),
    ]
