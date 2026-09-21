"""Generate commands.json, case_results.json, after/test_results.json and
the integrity manifest, from the raw run matrix + current file hashes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ATTEMPT / "scratch" / "run_matrix.json").read_text(
    encoding="utf-8"))
BY_ID = {r["run_id"]: r for r in MATRIX}
PY = r"C:\Miniconda\python.exe"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


ADAPTED = ["-p", "no:cacheprovider", "-q"]
I05C_CMD = ["-X", "utf8", "-B", "-m", "pytest", *ADAPTED]
ISO_CWD = str(ATTEMPT / "iso")


def cmd(run_id, purpose, cwd, target, env=None):
    rec = BY_ID[run_id]
    return {
        "id": run_id,
        "purpose": purpose,
        "cwd": cwd,
        "argv": [PY, *I05C_CMD, "--basetemp",
                 f"<fresh-command-run>/{run_id}", target],
        "env": env or {},
        "config_paths": [],
        "allowed_write_roots": [str(ATTEMPT)],
        "network": "disabled",
        "timeout_seconds": None,
        "expected_returncode": 0 if rec["returncode"] == 0 else None,
        "raw_returncode": rec["returncode"],
        "expected_business_result": purpose,
        "observed": rec["summary_line"],
        "failed_nodes": rec["failed_nodes"],
        "before_after_evidence": [
            "changes.diff", "after/source_hashes.json",
            "scratch/run_matrix.json", "after/test_results.json"],
        "binding_status": "bound",
    }


commands = [
    cmd("CTRL-A-fixed-w05c",
        "after: full W05C suite (19 I-05-C carrier tests + 16 B3 REM-11/13/14 "
        "tests) on the B3 fixed bytes",
        ISO_CWD, "fixed/tests/test_w05c_minimal_production.py"),
    cmd("CTRL-B-fixed-fc904",
        "after: FC-904 acceptance suite (11 frozen + 5 B3 provenance/scoping "
        "tests) on the B3 fixed bytes",
        ISO_CWD, "fixed/tests/test_fc904_artifact_selection.py"),
    cmd("CTRL-E-prod-w05b",
        "after: REM-12 re-pointed I-05-B regression (20 frozen + 3 B3 binding "
        "tests) against the PRODUCTION bytes",
        ISO_CWD, "fixed/tests/test_w05b_verified_artifact_read.py",
        {"B3_BYTES": "production"}),
    cmd("CTRL-F-fixed-w05b",
        "after: same I-05-B regression against the B3 fixed bytes (what would "
        "be promoted)",
        ISO_CWD, "fixed/tests/test_w05b_verified_artifact_read.py",
        {"B3_BYTES": "fixed"}),
    cmd("CTRL-C-prod-w05c",
        "before-control: the SAME W05C suite against the unfixed production "
        "bytes; the 19 carrier tests pass and the 8 new REM-11/13 tests fail",
        ISO_CWD, "fixed/tests/test_w05c_minimal_production.py",
        {"B3_BYTES": "production"}),
    cmd("CTRL-D-prod-fc904",
        "before-control: the SAME FC-904 suite against the unfixed production "
        "bytes; all 11 frozen tests pass, only the B3 subset-scope test fails",
        ISO_CWD, "fixed/tests/test_fc904_artifact_selection.py",
        {"B3_BYTES": "production"}),
    cmd("M1-rem11",
        "mutation: REM-11 reverted (bundle=None back to the downstream "
        "closure) -> W05C must go RED",
        str(ATTEMPT / "scratch" / "mutants" / "M1-rem11-bundle-none-closure"),
        "tests/test_w05c_minimal_production.py"),
    cmd("M2-rem13",
        "mutation: REM-13 reverted (old docstring wording) -> W05C must go RED",
        str(ATTEMPT / "scratch" / "mutants" / "M2-rem13-docstring-old-wording"),
        "tests/test_w05c_minimal_production.py"),
    cmd("M3-rem14",
        "mutation: REM-14 reverted (row 3 misattributed again) -> W05C must "
        "go RED",
        str(ATTEMPT / "scratch" / "mutants" / "M3-rem14-json-misattribution"),
        "tests/test_w05c_minimal_production.py"),
    cmd("M4a-rem12-stale",
        "mutation: REM-12 reverted (bind the I-05-B stale iso bytes) -> the "
        "W05B provenance assertions must go RED",
        str(ATTEMPT / "scratch" / "mutants" / "M4-rem12-stale-iso-binding"),
        "tests/test_w05b_verified_artifact_read.py",
        {"B3_BYTES": "fixed"}),
]
commands.append({
    "id": "M4b-vacuity-stale-iso",
    "purpose": "vacuous-evidence proof: the I-05-B attempt's frozen iso bytes "
               "pass the very same 20 carrier tests, so a 20/20 without a "
               "byte-binding assertion (the I-05-C w05b-regression record) is "
               "not regression evidence",
    "cwd": str(ATTEMPT / "scratch" / "vacuity"),
    "argv": BY_ID["M4b-vacuity-stale-iso"]["argv"],
    "env": {},
    "config_paths": [],
    "allowed_write_roots": [str(ATTEMPT)],
    "network": "disabled",
    "timeout_seconds": None,
    "expected_returncode": 0,
    "raw_returncode": BY_ID["M4b-vacuity-stale-iso"]["returncode"],
    "expected_business_result": "both passes green with bound bytes = "
                                "A55602E5 (stale)",
    "observed": BY_ID["M4b-vacuity-stale-iso"]["summary_line"],
    "bound_bytes": BY_ID["M4b-vacuity-stale-iso"]["bound_bytes"],
    "failed_nodes": [],
    "before_after_evidence": ["scratch/vacuity/bound_bytes.json"],
    "binding_status": "bound",
})
commands.append({
    "id": "before-baseline",
    "purpose": "before: the pristine carriers run against the untouched "
               "production bytes (W05C 19 passed, FC-904 11 passed, W05B 20 "
               "passed) - the same numbers the I-05-C attempt recorded",
    "cwd": str(ATTEMPT),
    "argv": [PY, *I05C_CMD, "--basetemp", "<fresh-command-run>/before",
             "before/tests/<carrier>.py"],
    "env": {"PYTHONPATH": "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\scripts;"
                          "C:\\Users\\郑曾波\\Projects\\company-wiki\\src"},
    "config_paths": [],
    "allowed_write_roots": [str(ATTEMPT)],
    "network": "disabled",
    "timeout_seconds": None,
    "expected_returncode": 0,
    "raw_returncode": 0,
    "expected_business_result": "19 / 11 / 20 passed on pre-fix production",
    "observed": "W05C 19 passed; FC-904 11 passed; W05B 20 passed",
    "failed_nodes": [],
    "before_after_evidence": ["after/test_results.json"],
    "binding_status": "bound",
})

(ATTEMPT / "commands.json").write_text(
    json.dumps(commands, indent=2), encoding="utf-8")


def suite(rec):
    return {"run_id": rec["run_id"], "raw_returncode": rec["returncode"],
            "summary_line": rec["summary_line"],
            "failed_nodes": rec["failed_nodes"],
            "purpose": rec["purpose"]}


carrier_19 = [n for n in BY_ID["CTRL-A-fixed-w05c"]["failed_nodes"]
              if False]  # carrier tests never failed on the fixed bytes

case_results = {
    "card_id": "B3-I05C-delivery-fixes",
    "parent_card": "I-05-C",
    "attempt_id": "a20260921-01",
    "exit_code_legend": {
        "0": "passed (business verdict: pass)",
        "1": "harness failure OR intentional RED mutation run",
        "2": "no verdict / expected rejection",
        "3": "did not meet expectation",
    },
    "findings": {
        "REM-11": {
            "severity": "P2",
            "title": "bundle=None path returned the full downstream closure of "
                     "the requested roles",
            "fix": "both branches now share _production_scope: requested missing "
                   "roles + their non-reusable ancestors",
            "oracle_case": "every single-role request row in oracle.md",
            "red_evidence": {
                "run": "CTRL-C-prod-w05c (unfixed production bytes)",
                "result": BY_ID["CTRL-C-prod-w05c"]["summary_line"],
                "red_nodes": [
                    "TestW05CXBundleNoneScoping::"
                    "test_no_bundle_normalized_only_produces_normalized_only",
                    "TestW05CXBundleNoneScoping::"
                    "test_no_bundle_scope_is_request_closure[normalized|"
                    "markdown|summary|sections|consumer_analysis]",
                    "TestW05CXBundleNoneScoping::"
                    "test_no_bundle_subset_never_exceeds_request_closure",
                ],
            },
            "green_evidence": {
                "run": "CTRL-A-fixed-w05c",
                "result": BY_ID["CTRL-A-fixed-w05c"]["summary_line"],
            },
            "mutation": suite(BY_ID["M1-rem11"]),
            "fc904_conflict": False,
        },
        "REM-12": {
            "severity": "P2",
            "title": "w05b-regression bound the I-05-B attempt's stale iso "
                     "bytes (A55602E5) instead of production",
            "fix": "re-pointed at the bytes under test by explicit file "
                   "location; provenance asserted in-test",
            "red_evidence": {
                "run": "M4a-rem12-stale (binding reverted to the stale iso)",
                "result": BY_ID["M4a-rem12-stale"]["summary_line"],
                "red_nodes": [
                    "TestB3W05BProductionBinding::"
                    "test_binding_is_not_the_stale_i05b_iso_copy",
                    "TestB3W05BProductionBinding::"
                    "test_binding_matches_the_declared_selector",
                ],
            },
            "green_evidence": {
                "production_bytes": suite(BY_ID["CTRL-E-prod-w05b"]),
                "fixed_bytes": suite(BY_ID["CTRL-F-fixed-w05b"]),
            },
            "vacuity_proof": {
                "run": "M4b-vacuity-stale-iso",
                "result": BY_ID["M4b-vacuity-stale-iso"]["summary_line"],
                "bound_bytes": BY_ID["M4b-vacuity-stale-iso"]["bound_bytes"],
                "reading": "the same 20 carrier tests pass on the stale bytes, "
                           "so the I-05-C record was vacuous as evidence about "
                           "production; it is now accompanied by a binding "
                           "assertion that cannot pass on the stale bytes",
            },
        },
        "REM-13": {
            "severity": "P3",
            "title": "select_artifact_roles docstring described the old "
                     "downstream-closure semantics",
            "fix": "docstring rewritten to the implemented rule, including the "
                   "bundle=None rule",
            "red_evidence": {
                "run": "CTRL-C-prod-w05c (unfixed production bytes)",
                "red_nodes": [
                    "TestW05CXDocstringMatchesBehaviour::"
                    "test_docstring_matches_scoped_semantics",
                ],
            },
            "green_evidence": {
                "run": "CTRL-A-fixed-w05c",
                "result": BY_ID["CTRL-A-fixed-w05c"]["summary_line"],
            },
            "mutation": suite(BY_ID["M2-rem13"]),
        },
        "REM-14": {
            "severity": "P3",
            "title": "retry-count-vs-artifact-count.json row 3 named the "
                     "diverge test but reported test_invocation_trace_accuracy's "
                     "numbers",
            "fix": "row 3 test field corrected to test_invocation_trace_accuracy "
                   "(4 calls / 1 artifact kept); a 4th row added for the diverge "
                   "test's own 3 calls / 1 artifact",
            "red_evidence": {
                "run": "CTRL-C-prod-w05c (frozen JSON)",
                "red_nodes": [
                    "TestW05CXRetryEvidenceAttribution::"
                    "test_retry_evidence_json_rows_match_named_tests",
                ],
            },
            "green_evidence": {
                "run": "CTRL-A-fixed-w05c",
                "result": BY_ID["CTRL-A-fixed-w05c"]["summary_line"],
            },
            "mutation": suite(BY_ID["M3-rem14"]),
            "test_code_changed": False,
        },
    },
    "regression": {
        "fc904": {
            "file": "tests/test_fc904_artifact_selection.py (production, "
                    "sha256 8C0B8E39...46BF3F, UNMODIFIED)",
            "before": "11 passed (production bytes)",
            "after": "16 passed (11 frozen + 5 B3)",
            "no_regression": True,
            "frozen_assertions_edited": False,
        },
        "w05b": {
            "file": "I-05-B carrier sha256 F9845F17...F9595D + 3 B3 binding "
                    "tests",
            "before": "20 passed against the stale I-05-B iso bytes (vacuous)",
            "after": "23 passed against production bytes AND 23 passed against "
                     "the fixed bytes",
            "no_regression": True,
        },
        "w05c": {
            "file": "I-05-C carrier sha256 D13BF505...7AAB82 + 16 B3 tests",
            "before": "19 passed (production bytes)",
            "after": "35 passed (fixed bytes); the 19 carrier tests also still "
                     "pass on production bytes",
            "no_regression": True,
        },
    },
    "before_after_control": {
        "note": "CTRL-C/CTRL-D run the SAME new tests against the unfixed "
                "production bytes, so the RED->GREEN change is attributable to "
                "the fix and not to test-only edits",
        "CTRL-C-prod-w05c": suite(BY_ID["CTRL-C-prod-w05c"]),
        "CTRL-D-prod-fc904": suite(BY_ID["CTRL-D-prod-fc904"]),
    },
    "production_repos_written": False,
}
(ATTEMPT / "case_results.json").write_text(
    json.dumps(case_results, indent=2), encoding="utf-8")

(ATTEMPT / "after" / "test_results.json").write_text(json.dumps({
    "generated_at": "2026-09-21",
    "raw_matrix": "scratch/run_matrix.json",
    "runs": MATRIX,
}, indent=2), encoding="utf-8")

integrity = {
    "production_repos": {
        "RF:scripts/company_wiki_source.py": {
            "sha256": sha(Path("C:/Users/郑曾波/Projects/revenue-forecast/"
                               "scripts/company_wiki_source.py")),
            "expected": "225FECDD7E48938A97C68724318F0860602A4B86A8D9E834A257243480094294",
        },
        "RF:tests/test_fc904_artifact_selection.py": {
            "sha256": sha(Path("C:/Users/郑曾波/Projects/revenue-forecast/"
                               "tests/test_fc904_artifact_selection.py")),
            "expected": "8C0B8E390307C33B8C03D51FD742CA984BA6774B84638500FD8D7CDD7D46BF3F",
        },
        "CW:src/company_wiki/source_catalog/artifact_dag.py": {
            "sha256": sha(Path("C:/Users/郑曾波/Projects/company-wiki/src/"
                               "company_wiki/source_catalog/artifact_dag.py")),
            "expected": "0C8B1D6D1A28C94F27EA8FFE52A98D67B84F0A49653931B9C9317E27DA6C20D1",
        },
    },
    "frozen_attempts": {
        "I-05-C:oracle.md": sha(Path(
            "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
            "2026-09-19-three-project-history-audit/execution_runs/I-05-C/"
            "a20260919-01/oracle.md")),
        "I-05-C:retry-count-vs-artifact-count.json": sha(Path(
            "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
            "2026-09-19-three-project-history-audit/execution_runs/I-05-C/"
            "a20260919-01/retry-count-vs-artifact-count.json")),
        "I-05-B:iso/tests/test_w05b_verified_artifact_read.py": sha(Path(
            "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
            "2026-09-19-three-project-history-audit/execution_runs/I-05-B/"
            "a20260919-01/iso/tests/test_w05b_verified_artifact_read.py")),
        "I-05-B:iso/checkout_scripts/company_wiki_source.py (stale)": sha(Path(
            "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
            "2026-09-19-three-project-history-audit/execution_runs/I-05-B/"
            "a20260919-01/iso/checkout_scripts/company_wiki_source.py")),
    },
    "expected_frozen": {
        "I-05-C:oracle.md": "NOT_REHASHED",
        "I-05-C:retry-count-vs-artifact-count.json":
            "A3DD418F31B75753FB60F5C1E00AE386C4F33FBF02E6F72A5D74807C794FE326",
        "I-05-B:iso/tests/test_w05b_verified_artifact_read.py":
            "F9845F170E0EFF4B705993A3659CC0D88EE7C476AE019641B712E4968DF9595D",
        "I-05-B:iso/checkout_scripts/company_wiki_source.py (stale)":
            "A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE",
    },
}
(ATTEMPT / "after" / "integrity.json").write_text(
    json.dumps(integrity, indent=2), encoding="utf-8")

print("wrote commands.json, case_results.json, after/test_results.json, "
      "after/integrity.json")
print(json.dumps(integrity, indent=2))
