"""Independent verifier for one M-card attempt (standard library only; no product import).

Checks, in order, that the delivered evidence is internally consistent:

  1  evidence/<CARD>/formula_result.json is byte-identical to run_result.json
  2  evidence/<CARD>/stdout.txt is the raw capture of the runner's stdout: its lines equal
     run_result.json["printed_lines"] and reproduce printed_sha256 - i.e. a printed number
     can never disagree with the recorded evidence file
  3  spot-checks parse the printed lines and compare them with the JSON fields
     (positive/continuity actual, expected, fidelity, negative summary, exit code)
  4  evidence/<CARD>/negative_results.json is exactly the declared projection of
     run_result.json (cases == negatives, summary == negative_summary, counts recomputed)
  5  the frozen files still hash to the freeze-time values in oracle_selfcheck.json
  6  mtime ordering: input.json / cases.json / oracle.json were written before stdout.txt
  7  iso/checkout_scripts/* still hash-equal the production scripts (read-only re-hash)
  8  the required evidence file set exists

Exit codes: 0 all checks pass, 5 at least one check failed, 1 harness error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time

REQUIRED_EVIDENCE = (
    "input.json", "oracle.json", "cases.json", "source_manifest.json", "command_manifest.json",
    "stdout.txt", "stderr.txt", "formula_result.json", "negative_results.json",
    "qualification.json", "oq_rulings.json", "oq_enumeration.json", "integrity.json",
    "oracle_selfcheck.json", "revision_r2.json", "negative_results_derivation.json",
    "r2_boundary_check.json",
)


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--production-root", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    card = args.card
    evidence = os.path.join(attempt, "evidence", card)
    checks = []

    def record(check_id, ok, detail):
        checks.append({"check": check_id, "ok": bool(ok), "detail": detail})
        return bool(ok)

    try:
        run_result_path = os.path.join(evidence, "run_result.json")
        formula_result_path = os.path.join(evidence, "formula_result.json")
        run_result = load_json(run_result_path)
        stdout_path = os.path.join(evidence, "stdout.txt")
        with open(stdout_path, "rb") as handle:
            stdout_bytes = handle.read()
        stdout_text = stdout_bytes.decode("utf-8")
        lines = stdout_text.splitlines()
        printed = run_result["printed_lines"]

        # 1 formula_result == run_result (byte level)
        same_bytes = (sha256_file(run_result_path) == sha256_file(formula_result_path))
        record("formula_result_is_byte_identical_to_run_result", same_bytes,
               {"run_result.json": sha256_file(run_result_path),
                "formula_result.json": sha256_file(formula_result_path)})

        # 2 raw stdout capture == printed_lines == printed_sha256
        lines_match = lines == printed
        recomputed = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
        record("stdout_lines_equal_printed_lines", lines_match,
               {"stdout_lines": len(lines), "printed_lines": len(printed),
                "first_difference": next(({"index": i, "stdout": lines[i], "json": printed[i]}
                                          for i in range(min(len(lines), len(printed)))
                                          if lines[i] != printed[i]), None)})
        record("stdout_reproduces_printed_sha256", recomputed == run_result["printed_sha256"],
               {"recomputed": recomputed, "recorded": run_result["printed_sha256"]})
        record("stdout_is_ascii_only", all(ord(ch) < 128 for ch in stdout_text),
               "GBK console safety: the runner escapes every non-ASCII character")

        # 3 spot checks: printed value vs JSON field
        def line_value(prefix):
            for line in lines:
                if line.startswith(prefix):
                    return line[len(prefix):].strip()
            return None

        spot = []
        positive_actual = line_value("positive actual:")
        spot.append({"field": "positive.actual", "printed": positive_actual,
                     "json": json.dumps(run_result["positive"]["actual"]),
                     "ok": positive_actual == json.dumps(run_result["positive"]["actual"])})
        continuity_actual = line_value("continuity_positive actual:")
        spot.append({"field": "continuity_positive.actual", "printed": continuity_actual,
                     "json": json.dumps(run_result["continuity_positive"]["actual"]),
                     "ok": continuity_actual == json.dumps(run_result["continuity_positive"]["actual"])})
        negative_summary = line_value("negative summary:")
        summary_expected = "total=%s passed=%s failed=%s" % (
            run_result["negative_summary"]["total"], run_result["negative_summary"]["passed"],
            run_result["negative_summary"]["failed"])
        spot.append({"field": "negative_summary", "printed": negative_summary,
                     "json": summary_expected, "ok": negative_summary == summary_expected})
        verdict_line = line_value("verdict:")
        verdict_expected = "%s exit_code: %s" % (run_result["verdict"]["verdict"],
                                                 run_result["exit_code"])
        spot.append({"field": "verdict/exit_code", "printed": verdict_line,
                     "json": verdict_expected, "ok": verdict_line == verdict_expected})
        fidelity_line = line_value("positive fidelity_ok:")
        spot.append({"field": "positive.fidelity.ok", "printed": fidelity_line,
                     "json": str(run_result["positive"]["fidelity"]["ok"]),
                     "ok": fidelity_line == str(run_result["positive"]["fidelity"]["ok"])})
        shape_line = line_value("positive expected:")
        shape_json = json.dumps([c["expected"] for c in
                                 run_result["positive"]["value_checks"]["per_value"]])
        spot.append({"field": "positive.expected", "printed": shape_line, "json": shape_json,
                     "ok": shape_line == shape_json})
        record("printed_value_spot_checks", all(item["ok"] for item in spot), spot)

        # 4 negative_results is the declared projection of run_result
        neg_path = os.path.join(evidence, "negative_results.json")
        neg = load_json(neg_path)
        derivation = load_json(os.path.join(evidence, "negative_results_derivation.json"))
        cases_equal = neg["cases"] == run_result["negatives"]
        summary_equal = neg["summary"] == run_result["negative_summary"]
        counts_recomputed = {
            "total": len(neg["cases"]),
            "rejected_with_ModelRegistryError": sum(
                1 for c in neg["cases"] if c.get("verdict") == "PASS_rejected"),
            "not_rejected": sum(1 for c in neg["cases"] if c.get("verdict") == "FAIL_not_rejected"),
            "wrong_exception_type": sum(
                1 for c in neg["cases"] if c.get("verdict") == "FAIL_wrong_exception_type"),
            "import_or_file_error": sum(
                1 for c in neg["cases"] if c.get("verdict") == "FAIL_import_or_file_error"),
        }
        record("negative_results_projection_is_exact",
               cases_equal and summary_equal and counts_recomputed == neg["counts"],
               {"cases_equal_run_result_negatives": cases_equal,
                "summary_equal_run_result_negative_summary": summary_equal,
                "counts_recomputed": counts_recomputed, "counts_recorded": neg["counts"],
                "declared_repack_scope": derivation.get("repack_scope"),
                "source_sha256": derivation.get("source_sha256"),
                "derived_sha256": derivation.get("derived_sha256")})

        # 5 frozen hashes still equal the freeze-time hashes
        selfcheck = load_json(os.path.join(evidence, "oracle_selfcheck.json"))
        freeze = selfcheck["frozen_file_sha256_at_freeze_time"]
        now = {"evidence/%s/%s" % (card, name): sha256_file(os.path.join(evidence, name))
               for name in ("input.json", "cases.json", "oracle.json")}
        record("frozen_files_still_equal_freeze_time_hashes", now == freeze,
               {"freeze_time": freeze, "now": now})

        # 6 mtime ordering (freeze before run)
        order = {name: os.path.getmtime(os.path.join(evidence, name))
                 for name in ("input.json", "cases.json", "oracle.json", "stdout.txt")}
        record("oracle_frozen_before_the_product_run",
               order["oracle.json"] < order["stdout.txt"]
               and order["input.json"] < order["stdout.txt"]
               and order["cases.json"] < order["stdout.txt"],
               {"mtimes_unix": order,
                "oracle_json_before_stdout": order["oracle.json"] < order["stdout.txt"]})

        # 7 isolated snapshot still equals production
        prod = args.production_root
        pairs = {}
        ok = True
        for name in ("model_registry.py", "model_extensions.py"):
            iso = os.path.join(attempt, "iso", "checkout_scripts", name)
            production = os.path.join(prod, "scripts", name)
            iso_hash = sha256_file(iso)
            prod_hash = sha256_file(production)
            pairs[name] = {"iso": iso_hash, "production": prod_hash, "equal": iso_hash == prod_hash}
            ok = ok and iso_hash == prod_hash
        record("isolated_snapshot_still_equals_production", ok, pairs)

        # 8 required file set
        missing = [name for name in REQUIRED_EVIDENCE
                   if not os.path.isfile(os.path.join(evidence, name))]
        record("required_evidence_files_present", not missing,
               {"required": list(REQUIRED_EVIDENCE), "missing": missing})

        all_ok = all(item["ok"] for item in checks)
        report = {
            "card_id": card,
            "attempt": attempt,
            "verified_at_unix": time.time(),
            "verified_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "checks": checks,
            "all_checks_passed": all_ok,
            "exit_code_observed_by_the_runner": run_result["exit_code"],
            "verdict_observed_by_the_runner": run_result["verdict"]["verdict"],
        }
        out = os.path.join(evidence, "verify_report.json")
        with open(out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, ensure_ascii=True, indent=1)
            handle.write("\n")
        for item in checks:
            print("check %-52s ok=%s" % (item["check"], item["ok"]))
        print("all_checks_passed: %s" % all_ok)
        return 0 if all_ok else 5
    except Exception as exc:  # noqa: BLE001
        print("verifier harness error: %s: %s" % (type(exc).__name__,
              str(exc).encode("ascii", "backslashreplace").decode("ascii")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
