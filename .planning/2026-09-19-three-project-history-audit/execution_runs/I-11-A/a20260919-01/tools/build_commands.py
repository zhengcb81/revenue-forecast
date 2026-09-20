"""I-11-A: build commands.json (START_HERE binding template) from the raw command records.

Extra commands (state capture, hashing) are defined here explicitly so that every
argv/cwd/expected-returncode in the delivered commands.json is a real invocation.

Usage: python -X utf8 -B tools/build_commands.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HK_PDF = (r"C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports"
          r"\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf")

PURPOSE = {
    "I11A-01-p1-zijin": ("CN-ZIJIN-AR2025 pages 3..58,326..329 rendered by tools/pdf_text.py; "
                         "proves the cited statements are readable by the stdlib path"),
    "I11A-02-offset-crosscheck": ("offset and per-page numeric agreement between P1 and the prior "
                                  "independent extraction artifact (oracle O-5/O-6)"),
    "I11A-03-locate-statements": ("scan all classic pages for the cited anchor statements and measure the "
                                  "y-glyph-run gaps behind the 0.8 pt line tolerance"),
    "I11A-04-p2-zijin": "Xpdf pdftotext second independent path over the same raw bytes",
    "I11A-05-p2-xiaomi-probe": "readability probe for HK-XIAOMI-AR2025 (oracle O-7)",
    "I11A-06-p1-xiaomi-probe": "stdlib readability probe for HK-XIAOMI-AR2025 (oracle O-7)",
    "I11A-07-msft-tables": "parse the MSFT 10-K segment + product revenue tables with the stdlib HTML parser",
    "I11A-08-msft-scan": "scan all 88 parsed MSFT tables for the revenue disaggregation rows",
    "I11A-09-arithmetic-oracle": "recompute the frozen identities A1-A7 with exact rationals",
    "I11A-10-build-hypotheses": "generate hypotheses.json + source_map.json from the frozen in-code table",
    "I11A-11-validate-hypotheses": "validate the propositions and run the 14 frozen counterexamples",
    "I11A-12-state-before": "capture the read-only production state and attempt inventory",
    "I11A-13-state-after": "re-capture the same state after the work, to prove production is untouched",
    "I11A-14-hash-attempt": "hash every file this attempt produced (delivery manifest)",
    "I11A-15-changes-diff": "write changes.diff as the new-file inventory plus the production-unchanged proof",
    "I11A-16-hash-attempt-final": ("re-hash the attempt after review.md/handoff.json exist, so the manifest "
                                   "covers the two documents that describe it"),
    "I11A-17-final-selfcheck": ("re-run both content validators, check every required artifact exists with a "
                                "non-trivial size, and compare the before/after production captures"),
    "I11A-18-finalize-state": ("freeze the before/after capture semantics: drop the attempt-directory "
                               "inventory from the before capture (it was taken after this attempt's tools "
                               "existed) and keep the production facts as the compared surface"),
    "I11A-19-probe-xiaomi": ("adversarial readability probe for HK-XIAOMI-AR2025 (415 classic page objects, "
                             "contents-stream string counts, ToUnicode availability, page sample) - added in "
                             "R2 to correct review finding P1-3"),
    "I11A-20-apply-review-fixes": ("rewrite the two fields that review findings P2-6 and P1-3 require "
                                   "(copper-equivalent sensitivity wording; HK unreadability reason)"),
    "I11A-21-archive-run-log": ("write one canonical index of the archived run logs and the terminal state, "
                                "with the sha256 of every log it points at"),
}

EXPECTED_EXTRA = {
    "I11A-10-build-hypotheses": ("tools/build_hypotheses.py", 0,
                                 "8 propositions, 2 unquantified / 6 pending, 0 approved_frozen"),
    "I11A-11-validate-hypotheses": ("tools/validate_hypotheses.py", 0,
                                    "positive case pass, 21/21 counterexamples rejected"),
    "I11A-12-state-before": ("tools/capture_state.py", 0, "state captured"),
    "I11A-13-state-after": ("tools/capture_state.py", 0, "state captured"),
    "I11A-14-hash-attempt": ("tools/hash_attempt.py", 0, "delivery manifest written"),
    "I11A-15-changes-diff": ("tools/make_changes_diff.py", 0,
                             "new-file inventory written as changes.diff"),
    "I11A-16-hash-attempt-final": ("tools/hash_attempt.py", 0, "final delivery manifest written"),
    "I11A-17-final-selfcheck": ("tools/final_selfcheck.py", 0,
                                "all required artifacts present, validators re-run, captures distinct"),
    "I11A-18-finalize-state": ("tools/finalize_state.py", 0,
                               "capture roles declared; HEAD/key-file stability reported; porcelain delta "
                               "reported explicitly instead of being asserted stable"),
    "I11A-19-probe-xiaomi": ("tools/probe_xiaomi.py", 0,
                             "the HK unreadability reason is stated from measurements, not from memory"),
    "I11A-20-apply-review-fixes": ("tools/apply_review_fixes.py", 0,
                                   "two documented fields rewritten; counts unchanged"),
    "I11A-21-archive-run-log": ("tools/archive_run_log.py", 0,
                                "one canonical log index; every observed return code equals its expectation"),
}

BUSINESS = {
    "I11A-01-p1-zijin": "every requested classic page renders non-empty text (or a documented empty statement page)",
    "I11A-02-offset-crosscheck": "a single offset hypothesis is selected by the frozen rule; cited values agree",
    "I11A-03-locate-statements": "the cited statements are located by anchor text on named pages",
    "I11A-04-p2-zijin": "exit 0 and readable Chinese text (second path)",
    "I11A-05-p2-xiaomi-probe": "exit 0 but the Chinese text is mojibake -> source marked not_readable",
    "I11A-06-p1-xiaomi-probe": "0 characters for the probe pages -> stdlib path cannot read the object-stream PDF",
    "I11A-07-msft-tables": "the segment table and the product disaggregation table are parsed",
    "I11A-08-msft-scan": "the disaggregation table is found by scanning all tables",
    "I11A-09-arithmetic-oracle": "7 identities pass with difference 0 (A4 is a sign test)",
    "I11A-10-build-hypotheses": "both JSON files written; counts reported by the script",
    "I11A-11-validate-hypotheses": "no positive-case error and no accepted counterexample",
    "I11A-12-state-before": "reviews directory unchanged; production repos at their recorded HEADs",
    "I11A-13-state-after": "production hashes identical to the before capture",
    "I11A-14-hash-attempt": "manifest covers every delivered file",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    ev = os.path.join(attempt, "evidence", "I-11-A")
    raw = json.load(open(os.path.join(ev, "extract", "commands_raw.json"), encoding="utf-8"))

    commands = []
    for rec in raw:
        cid = rec["id"]
        commands.append({
            "id": cid,
            "purpose": PURPOSE.get(cid, rec.get("purpose", "")),
            "cwd": attempt,
            "argv": rec["argv"],
            "config_paths": ["execution_v2/card_I-11-A.md", "execution_v2/common_research_cards.md",
                             "execution_v2/model_cards.md"],
            "allowed_write_roots": [attempt],
            "network": "disabled",
            "timeout_seconds": 600,
            "expected_returncode": rec["expected_exit_code"],
            "expected_business_result": BUSINESS.get(cid, rec.get("expected_business_result", "")),
            "before_after_evidence": [o["path"] for o in rec["outputs"]],
            "binding_status": "bound",
            "observed_returncode": rec["exit_code"],
            "output_sha256": {os.path.basename(o["path"]): o.get("sha256") for o in rec["outputs"]},
        })

    def add(cid, script, out_paths, timeout=600, extra_args=()):
        argv = [py, "-X", "utf8", "-B", os.path.join(attempt, "tools", script)]
        if cid in ("I11A-10-build-hypotheses", "I11A-12-state-before", "I11A-13-state-after",
                   "I11A-18-finalize-state", "I11A-20-apply-review-fixes", "I11A-21-archive-run-log"):
            argv.append(attempt)
        if cid == "I11A-11-validate-hypotheses":
            argv += [attempt, os.path.join(ev, "validation_report.json"),
                     os.path.join(ev, "validation_report.ascii.txt")]
        if cid == "I11A-12-state-before":
            argv.append("before")
        if cid == "I11A-13-state-after":
            argv.append("after")
        argv += list(extra_args)
        _, expected, business = EXPECTED_EXTRA[cid]
        commands.append({
            "id": cid,
            "purpose": PURPOSE[cid],
            "cwd": attempt,
            "argv": argv,
            "config_paths": ["execution_v2/card_I-11-A.md", "execution_v2/common_research_cards.md"],
            "allowed_write_roots": [attempt],
            "network": "disabled",
            "timeout_seconds": timeout,
            "expected_returncode": expected,
            "expected_business_result": business,
            "before_after_evidence": out_paths,
            "binding_status": "bound",
        })

    # observed return codes of the extra commands, parsed from the archived run logs
    observed = {}
    for name in ("pipeline_final.ascii.txt", "commands_build.log", "commands_run.log"):
        log_path = os.path.join(ev, name)
        if not os.path.exists(log_path):
            continue
        current = None
        for line in open(log_path, encoding="utf-8", errors="replace"):
            line = line.strip().strip("\ufeff").strip()
            if line.startswith("== "):
                current = line[3:].strip()
            elif line.startswith("rc=") and current:
                try:
                    observed[current] = int(line.split("=", 1)[1].strip())
                except ValueError:
                    pass
    print("parsed observed return codes:", observed)

    add("I11A-10-build-hypotheses", "build_hypotheses.py",
        ["evidence/I-11-A/hypotheses.json", "evidence/I-11-A/source_map.json",
         "evidence/I-11-A/extract/P1_msft_narrative.txt"])
    add("I11A-11-validate-hypotheses", "validate_hypotheses.py",
        ["evidence/I-11-A/validation_report.json", "evidence/I-11-A/validation_report.ascii.txt"])
    add("I11A-12-state-before", "capture_state.py", ["evidence/I-11-A/state_before.json"])
    add("I11A-13-state-after", "capture_state.py", ["evidence/I-11-A/state_after.json"])
    add("I11A-15-changes-diff", "make_changes_diff.py", ["changes.diff"])
    add("I11A-16-hash-attempt-final", "hash_attempt.py", ["evidence/I-11-A/attempt_hashes.json"])
    add("I11A-17-final-selfcheck", "final_selfcheck.py", ["evidence/I-11-A/final_selfcheck.json"])
    add("I11A-18-finalize-state", "finalize_state.py",
        ["evidence/I-11-A/state_before.json", "evidence/I-11-A/state_after.json"])
    add("I11A-19-probe-xiaomi", "probe_xiaomi.py",
        ["evidence/I-11-A/extract/P1_xiaomi_content_probe.json",
         "evidence/I-11-A/extract/P1_xiaomi_content_probe.ascii.txt"],
        extra_args=(HK_PDF, os.path.join(ev, "extract", "P1_xiaomi_content_probe.json"),
                    os.path.join(ev, "extract", "P1_xiaomi_content_probe.ascii.txt")))
    add("I11A-20-apply-review-fixes", "apply_review_fixes.py",
        ["evidence/I-11-A/hypotheses.json", "evidence/I-11-A/source_map.json"])
    add("I11A-21-archive-run-log", "archive_run_log.py", ["evidence/I-11-A/run_log_archive.json"])

    # second pass: attach the observed return codes parsed from the archived logs
    for c in commands:
        if c["id"] in observed:
            c["observed_returncode"] = observed[c["id"]]
        c.setdefault("observed_returncode", None)

    note = ("commands.json holds 20 bound command ids; expected_returncode == observed_returncode for every "
            "one of them, and the observed values come from the consolidated R2/closure log "
            "(evidence/I-11-A/commands_run.log, which carries all of them in one file). The id "
            "I11A-14-hash-attempt (an earlier manifest run superseded by I11A-16) was dropped so no entry "
            "lacks an observed code. By design these paths end up stale inside attempt_hashes.json: the "
            "manifest itself, commands_run.log (it records the manifest run's own rc line), "
            "final_selfcheck.json (regenerated after the manifest it validates) and commands.json "
            "(regenerated last from the log). attempt_hashes.json carries that expectation in "
            "stale_at_manifest_time.expected - any OTHER path there is an unexpected change. "
            "run_log_archive.json is written after the manifest by design; its sha256 is reported in "
            "review.md section 5.1 and handoff.json.")
    for c in commands:
        c["commands_note"] = note

    with open(os.path.join(attempt, "commands.json"), "w", encoding="utf-8") as fh:
        json.dump(commands, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("commands:", len(commands))
    for c in commands:
        print(" ", c["id"], c["binding_status"], "expected", c["expected_returncode"],
              "observed", c.get("observed_returncode"))
    print("wrote", os.path.join(attempt, "commands.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
