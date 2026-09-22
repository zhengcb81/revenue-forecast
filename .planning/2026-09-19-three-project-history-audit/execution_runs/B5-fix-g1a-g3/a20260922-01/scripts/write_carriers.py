"""Write this attempt's own carriers: commands.json (every arm unit + real raw rc) and
binding.json (pre-run anchors: historical/patched runner shas, interpreters, code roots).
Replaces the template copies taken from B5's attempt; oracle.md and PROPAGATION_CONTRACT.md
stay as read-only context copies from B5 (flagged in handoff.json)."""
from __future__ import annotations

import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
B5 = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch")

BATCH_REP = {"M01-M04": "M01", "M05-M08": "M05", "M09-M12": "M09", "M13-M16": "M13",
             "M17-M20": "M17", "M21-M24": "M21", "M25-M28": "M25", "M29-M31": "M29"}
BATCH_SHA_BEFORE = {
    "M01-M04": "b5fcc685", "M05-M08": "fd3a11c9", "M09-M12": "997c553b",
    "M13-M16": "9e4a6450", "M17-M20": "94619a98", "M21-M24": "a5ee7599",
    "M25-M28": "eab01162", "M29-M31": "9ea69c72",
}
START_HERE_POST2 = "a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf"
PROD_SHA = {"model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def main():
    runs = json.load(open(os.path.join(SCRATCH, "arms_raw.json"), encoding="utf-8"))

    legend = {
        "0": "pass",
        "1": "harness/structural failure (M25-M28 structural branch + uncaught crash elsewhere)",
        "2": "no verdict (declaration unusable / no verdict possible) - decided before any case is judged",
        "3": "judgement possible and did not hold (incl. declared-expectation mismatch)",
    }
    units = {}
    for r in runs:
        units["%s-%s-%s" % (r["arm"], r["card"], r["batch"])] = {
            "argv": r["argv"],
            "cwd": r["cwd"],
            "raw_rc": r["raw_rc"],
            "runner_role": r["runner_role"],
            "runner_sha256": r["runner_sha256"],
            "cases_variant": r["cases_variant"],
            "mutated_case": r["mutated_case"],
            "out_written": r["out_written"],
            "verdict": r["verdict"],
        }
    commands = {
        "card": "B5-fix-g1a-g3",
        "attempt": "a20260922-01",
        "note": ("every unit below is a REAL child process started by "
                 "scripts/run_all_arms.py; raw_rc is the child's own exit code, never "
                 "inferred; all paths redirected into this attempt's _scratch; historical "
                 "trees only ever read"),
        "exit_code_legend": legend,
        "unit_count": len(units),
        "units": units,
    }
    dump_json(os.path.join(ATTEMPT, "commands.json"), commands)

    batches = {}
    for batch, rep in BATCH_REP.items():
        before = os.path.join(ATTEMPT, batch, "run_card_before.py")
        after = os.path.join(ATTEMPT, batch, "run_card.py")
        hist = os.path.join(PLAN, "execution_runs", rep, "a20260919-01", "scripts",
                            "run_card.py")
        iso = os.path.join(PLAN, "execution_runs", rep, "a20260919-01", "iso")
        batches[batch] = {
            "rep_card": rep,
            "historical_runner": {"path": os.path.relpath(hist, PLAN).replace("\\", "/"),
                                  "sha256": sha256_file(hist),
                                  "recorded_batch_prefix": BATCH_SHA_BEFORE[batch]},
            "copy_before": {"path": "%s/%s/run_card_before.py" % ("execution_runs/B5-fix-g1a-g3"
                                                                  "/a20260922-01", batch),
                            "sha256": sha256_file(before),
                            "byte_identical_to_historical": sha256_file(before)
                            == sha256_file(hist)},
            "patched_after": {"path": "%s/%s/run_card.py" % ("execution_runs/B5-fix-g1a-g3"
                                                             "/a20260922-01", batch),
                              "sha256": sha256_file(after),
                              "bytes": os.path.getsize(after),
                              "patched": sha256_file(after) != sha256_file(hist)},
            "interpreter": os.path.join(iso, "venv", "Scripts", "python.exe"),
            "iso_checkout_scripts": os.path.join(iso, "checkout_scripts"),
            "scratch_code_root": "_scratch/%s/code_root" % batch,
            "scratch_code_root_sha256": PROD_SHA,
        }
    binding = {
        "card": "B5-fix-g1a-g3",
        "attempt": "a20260922-01",
        "plan": PLAN,
        "b5_source_attempt_read_only": {
            "path": "execution_runs/B5-plan-level-remediation/a20260921-01",
            "handoff_sha256": sha256_file(os.path.join(B5, "handoff.json")),
            "reviewer_report_sha256": sha256_file(os.path.join(B5, "reviewer_report.md")),
            "copied_from": ["<batch>/run_card.py (6x)", "<batch>/run_card_before.py (6x)",
                            "decision.md", "oracle.md", "binding.json", "commands.json",
                            "PROPAGATION_CONTRACT.md", "changes.diff"],
            "written_into_b5_attempt": [],
        },
        "start_here_md": {"path": "execution_v2/START_HERE.md",
                          "sha256": sha256_file(os.path.join(PLAN, "execution_v2",
                                                             "START_HERE.md")),
                          "expected_post2_sha256": START_HERE_POST2},
        "production_read_only": {name: sha256_file(
            os.path.join(r"C:\Users\郑曾波\Projects\revenue-forecast\scripts", name))
            for name in sorted(PROD_SHA)},
        "batches": batches,
        "anchors_recorded_elsewhere": {
            "historical_runner_census_and_frozen_cases":
                "evidence/boundary_verification.json",
            "arm_matrix": "evidence/arm_matrix.json",
            "g3_reader_proof": "evidence/g3_reader_proof.json",
            "append_proof_fixed": "evidence/start_here_append_proof_fixed.json",
        },
    }
    dump_json(os.path.join(ATTEMPT, "binding.json"), binding)
    print("commands.json units:", len(units))
    print("binding.json batches:", len(batches))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
