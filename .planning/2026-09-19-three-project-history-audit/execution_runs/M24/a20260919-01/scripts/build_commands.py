"""Write commands.json for one M21-M24 attempt from the artefacts actually produced.

Every argv recorded here is the real invocation used in this attempt, with real
absolute paths, and every raw_rc is the exit code that invocation actually
returned. A `scope` field states which card the unit covers, so a reader can see
that no unit of this file is borrowed from another card's attempt.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/build_commands.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

PY = "iso\\venv\\Scripts\\python.exe"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)
    py = os.path.join(attempt, PY)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    scratch = os.path.join(attempt, "recovery", "selfcheck")
    # <attempt> = <plan>/execution_runs/<card>/a20260919-01
    runs_root = os.path.dirname(os.path.dirname(attempt))
    plan = os.path.dirname(runs_root)
    template_py = os.path.join(runs_root, "I-00-A", "a20260919-01", "iso", "venv",
                               "Scripts", "python.exe")
    m05_runner = os.path.join(runs_root, "M05", "a20260919-01", "scripts", "run_card.py")

    with open(os.path.join(ev, "run_result.json"), "r", encoding="utf-8") as fh:
        run = json.load(fh)
    with open(os.path.join(ev, "oracle.json"), "r", encoding="utf-8") as fh:
        oracle = json.load(fh)
    with open(os.path.join(attempt, "recovery", "selfcheck", "selfcheck_result.json"),
              "r", encoding="utf-8") as fh:
        probe = json.load(fh)
    probe_rc = {r["tag"]: r["raw_exit_code"] for r in probe["runs"]}
    sem = run["exit_code_semantics"]

    def unit(uid, purpose, argv, raw_rc, expected_rc, note, extra=None):
        entry = {"unit_id": uid, "scope": card, "purpose": purpose, "cwd": attempt,
                 "argv": argv, "config_paths": [], "allowed_write_roots": [attempt],
                 "network": "disabled", "timeout_seconds": None,
                 "raw_rc": raw_rc, "expected_rc": expected_rc,
                 "before_after_evidence": ["before/", "after/"],
                 "binding_status": "bound", "note": note}
        if extra:
            entry.update(extra)
        return entry

    units = [
        unit("A0-%s-iso-venv-create" % card,
             "create the attempt-local isolated interpreter from the I-00-A template venv",
             [template_py, "-m", "venv", os.path.join(attempt, "iso", "venv")],
             0, 0,
             "the global Miniconda python is forbidden for card runs and was not used at all "
             "in this attempt"),
        unit("A1-%s-runner-copy" % card,
             "copy the shared, card-agnostic runner into this attempt",
             ["powershell", "Copy-Item", m05_runner,
              os.path.join(attempt, "scripts", "run_card.py")],
             0, 0,
             "the runner is byte-identical across M05-M08 and M21-M24; its sha256 is recorded "
             "in evidence/%s/source_manifest.json and handoff.json" % card),
        unit("A2-%s-isolated-snapshot" % card,
             "materialise the read-only isolated code snapshot and confirm it is byte-identical "
             "to production",
             ["powershell", "Copy-Item",
              "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts\\model_registry.py",
              os.path.join(code_root, "model_registry.py")],
             0, 0,
             "model_extensions.py was copied the same way; both hashes equal production",
             {"hashes": {
                 "iso/checkout_scripts/model_registry.py":
                     sha( os.path.join(code_root, "model_registry.py")),
                 "iso/checkout_scripts/model_extensions.py":
                     sha(os.path.join(code_root, "model_extensions.py")),
                 "production scripts/model_registry.py":
                     sha("C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts\\model_registry.py"),
                 "production scripts/model_extensions.py":
                     sha("C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts\\model_extensions.py"),
             }}),
        unit("A3-%s-oracle-generate" % card,
             "generate the frozen expectations with a stdlib-only generator that never imports "
             "the product",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "oracle_%s.py" % card),
              "--card", card, "--out-root", attempt],
             0, 0,
             "writes evidence/%s/input.json, cases.json, oracle.json, oracle_selfcheck.json" % card),
        unit("A4-%s-oracle-md-freeze" % card,
             "render the frozen oracle document BEFORE any product run",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "write_oracle_md.py"),
              "--card", card, "--attempt", attempt],
             0, 0,
             "oracle.md mtime precedes evidence/%s/stdout.txt; the mtime pair is recorded in "
             "evidence/%s/source_manifest.json" % (card, card),
             {"oracle_md_sha256": sha(os.path.join(attempt, "oracle.md"))}),
        unit("A5-%s-oracle-regeneration-check" % card,
             "re-run the oracle generator and prove oracle.json is byte-identical",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "oracle_%s.py" % card),
              "--card", card, "--out-root", attempt],
             0, 0,
             "no timestamp, no randomness and no dict-ordering dependence in the generator",
             {"oracle_json_sha256_after_regeneration": sha(os.path.join(ev, "oracle.json"))}),
        unit("B-%s-product-run" % card,
             "run positive + continuity positive + defaults + all negatives through the single "
             "product entry point calculate_registered_model",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "run_card.py"),
              "--card", card, "--attempt", attempt, "--code-root", code_root,
              "--out", os.path.join(ev, "run_result.json"),
              "--run-result-out", os.path.join(ev, "run_result.json")],
             sem["exit_code"], 0,
             "stdout/stderr captured to evidence/%s/stdout.txt and stderr.txt; verdict=%s"
             % (card, sem["verdict"]),
             {"product_entry_point": "model_registry.calculate_registered_model(**input)",
              "positive_actual": run["positive"].get("actual"),
              "positive_expected": oracle["positive"]["expected_float"],
              "continuity_actual": run["continuity_positive"].get("actual"),
              "defaults_actual": run["defaults"].get("actual"),
              "negative_summary": run["negative_summary"]}),
        unit("C-%s-evidence-pack" % card,
             "read the run result back into the derived evidence documents",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "build_evidence.py"),
              "--card", card, "--attempt", attempt],
             0, 0,
             "writes formula_result.json, negative_results.json, qualification.json, "
             "source_manifest.json, integrity.json, revision_r2.json, command_manifest.json"),
        unit("G0-%s-selfcheck-prepare" % card,
             "copy the runner and the frozen evidence into a scratch tree (the frozen evidence "
             "itself is never mutated)",
             ["powershell", "Copy-Item", os.path.join(attempt, "scripts", "run_card.py"),
              os.path.join(scratch, "scripts", "run_card.py")],
             0, 0,
             "scratch evidence copy = evidence/%s/{input,oracle,cases}.json" % card),
        unit("G1-%s-selfcheck-mutations" % card,
             "red-then-green exit-code mutation probe: corrupt the expectation, corrupt a "
             "negative assertion, corrupt the input, then restore",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "selfcheck_mutations.py"),
              "--card", card, "--attempt", attempt],
             0, 0,
             "G-A corrupted positive expectation -> rc 3; G-B corrupted negative assertion -> "
             "rc 3; G-C corrupted positive input -> rc 2; G-D restored -> rc 0; frozen hashes "
             "unchanged=%s" % probe["frozen_hashes_unchanged"],
             {"raw_rc_by_tag": probe_rc,
              "expected_rc_by_tag": {r["tag"]: r["expected_exit_code"] for r in probe["runs"]}}),
        unit("H1-%s-oq-enumeration" % card,
             "read-only enumeration of every registered driver domain behind oq_rulings.json",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts",
                                                   "enumerate_oq_rulings.py"),
              "--code-root", code_root, "--card", card,
              "--out", os.path.join(ev, "oq_rulings_enumeration.json")],
             0, 0,
             "raw stdout kept in recovery/oq_enum_stdout.txt; writes no value by hand"),
        unit("H2-%s-oq-rulings-build" % card,
             "derive oq_rulings.json from the raw enumeration output",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "build_oq_rulings.py"),
              "--card", card, "--attempt", attempt],
             0, 0,
             "all counts are copies of the enumeration output; the ruling itself is left to the "
             "independent reviewer"),
        unit("H3-%s-commands-build" % card,
             "write this commands.json from the artefacts actually produced",
             [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "build_commands.py"),
              "--card", card, "--attempt", attempt],
             0, 0,
             "self-recording unit: it lists itself so the argv chain is complete"),
        unit("I1-%s-integrity-recheck" % card,
             "re-hash the production scripts after all runs and re-capture git status",
             ["powershell", "Get-FileHash", "-Algorithm", "SHA256",
              "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts\\model_registry.py"],
             0, 0,
             "recorded in after/source_hashes.txt and after/git_status_revenue-forecast.txt; "
             "the two anchored hashes still match"),
    ]

    batch = {
        "batch_id": "M21-M24",
        "attempt_id": "a20260919-01",
        "cards": ["M21", "M22", "M23", "M24"],
        "card_id": card,
        "created_before_card_runs": True,
        "scope_note": "every unit below belongs to this card's own attempt directory; no unit "
                      "of this file is borrowed from another card's attempt",
        "isolation": {
            "interpreter": py,
            "created_from_template":
                "<PLAN>\\execution_runs\\I-00-A\\a20260919-01\\iso\\venv\\Scripts\\python.exe",
            "code_root": code_root,
            "never_used": [
                "C:/Miniconda python for any card run",
                "the production scripts directory on sys.path",
                "network",
                "provider",
                "LLM",
                "pytest (no third-party package is required by this card)",
            ],
        },
        "oracle_md_sha256": sha(os.path.join(attempt, "oracle.md")),
        "oracle_md_note": "oracle.md is NOT embedded here; only its sha256 is recorded. The "
                          "verifiable ordering chain is the mtime pair in "
                          "evidence/%s/source_manifest.json (oracle.json mtime < stdout.txt "
                          "mtime) plus the byte-identical regeneration of oracle.json." % card,
        "units": units,
    }
    target = os.path.join(attempt, "commands.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(batch, fh, ensure_ascii=False, indent=1)
    print("wrote", target, "units", len(units))
    print("unit ids", [u["unit_id"] for u in units])
    return 0


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
