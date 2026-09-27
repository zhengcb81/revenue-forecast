"""Build binding_before.json for RF-RATCHET-REST-B a20260923-01.

Reads scratch/binding_pins_raw.json (live-measured pins), recomputes the frozen-table
block sha with an explicit extraction rule, verifies the oracle sha, and writes
binding_before.json. Production is only READ.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
A = RF / ".planning/2026-09-19-three-project-history-audit/execution_runs/RF-RATCHET-REST-B/a20260923-01"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    pins = json.loads((A / "scratch" / "binding_pins_raw.json").read_text(encoding="utf-8-sig"))
    assert len(pins) == 40 and all(p["sha256"] != "MISSING" for p in pins)

    oracle = A / "oracle.md"
    oracle_sha = sha256_file(oracle)

    test_file = RF / "tools/tests/test_complexity_ratchet.py"
    text = test_file.read_text(encoding="utf-8")
    start = text.index("FROZEN_MAX = {")
    end = text.index("NEW_FILE_MAX = 10") + len("NEW_FILE_MAX = 10")
    block = text[start:end]
    block_sha = hashlib.sha256(block.encode("utf-8")).hexdigest()

    scan = A / "evidence/measure/scan_all_violations_before.txt"
    xchk = A / "evidence/measure/independent_crosscheck_before.txt"
    mcc = A / "evidence/measure/measure_cc_before.txt"
    bytelock = A / "evidence/bytelock/bytelock_scan_before.txt"

    binding = {
        "card": "RF-RATCHET-REST-B",
        "attempt": "a20260923-01",
        "phase": "before",
        "captured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "oracle": {"path": "oracle.md", "sha256": oracle_sha, "bytes": oracle.stat().st_size,
                   "frozen_first": True},
        "pins": pins,
        "frozen_table": {
            "source": "tools/tests/test_complexity_ratchet.py FROZEN_MAX+NEW_FILE_MAX literal block",
            "extraction": "text between (incl.) 'FROZEN_MAX = {' and (incl.) 'NEW_FILE_MAX = 10'",
            "block_sha256": block_sha,
            "test_file_sha256": sha256_file(test_file),
            "sibling_FIX_block_sha256_reference": "1e9cce36115c381683f69e391c4e680336c61faff57e635a324d2b2ecd389074",
        },
        "three_rows_before": {
            "scripts/model_registry.py": {"actual": 28, "frozen": 9,
                                          "max_function": "calculate_registered_model",
                                          "origin_commit": "5fd82de7"},
            "scripts/revenue_core.py": {"actual": 23, "frozen": 6,
                                        "max_functions": {"_validate_attestation_response": 23,
                                                          "_run_attestation_provider": 19},
                                        "origin_commit": "ec307d20"},
            "scripts/revenue_publication.py": {"actual": 16, "frozen": 10,
                                               "max_function": "validate_publication_attestation",
                                               "origin_commit": "ec307d20"},
        },
        "pre_freeze_measure_evidence": {
            "scan_all_violations_before.txt": sha256_file(scan),
            "independent_crosscheck_before.txt": sha256_file(xchk),
            "measure_cc_before.txt": sha256_file(mcc),
            "bytelock_scan_before.txt": sha256_file(bytelock),
            "double_implementation_agreement": "identical 7 frozen + 1 new violations",
        },
        "byte_lock_precheck": {
            "sha_literal_hits_tests_and_tools": 0,
            "name_reference_lines": 15,
            "assertion_needles_to_preserve": [
                "tests/test_model_extensions_anchor.py: assertIn('build_extension_specs', model_registry source)",
                "tests/test_skill_documentation.py: index('validate_published_forecast(result, data)') < index('build_publication_receipt(') in revenue_core source",
                "tests/test_structure_targets.py: revenue_core.py lines <= 2500",
            ],
            "comment_only_line_ref_disclosed": "tests/test_model_economic_guardrails.py:27 cites scripts/model_registry.py:410 (comment, not assertion; line numbers will shift)",
            "golden_behavior_lock": "tests/golden_behavior_hashes.json pins run_forecast RESULT hashes (behavior lock, not source bytes)",
            "verdict": "NO byte-lock on any of the three files -> helper-split path (card option i) compliant for all three rows; option (ii) STOP not triggered",
            "scan_evidence": "evidence/bytelock/bytelock_scan_before.txt",
        },
        "promotion_contract_evidence_pins_reverified": {
            "promotion_batch_manifest.md": "6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac",
            "test_i08c_consumer_rejection.py": "3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb",
            "note": "per-file pins for PROMOTION-EXEC/MODEL-ORACLE-ALIGN/B1 carriers live in the pins[] array above (paths under .planning/)",
        },
        "git_reads_disclosed": [
            "git show -s/--stat ec307d20, 5fd82de7 (attribution)",
            "git log -1 -- scripts/<file> x3 (last-touching commit)",
            "git status --porcelain (baseline evidence/integrity/porcelain_baseline.txt)",
        ],
        "note": "production read-only; all shas measured BEFORE the judged RED re-run and before any iso build",
    }
    (A / "binding_before.json").write_text(
        json.dumps(binding, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("binding_before.json written")
    print("oracle_sha =", oracle_sha)
    print("block_sha  =", block_sha)
    print("block matches sibling FIX reference:",
          block_sha == binding["frozen_table"]["sibling_FIX_block_sha256_reference"])


if __name__ == "__main__":
    main()
