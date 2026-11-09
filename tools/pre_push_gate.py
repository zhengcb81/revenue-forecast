"""Small fixed local smoke; explicit CI retains the full behavior set.

Pre-commit already checks public types. The local push repeats only fast Ruff
and fixed source/ref/forecast controls. ``--ci`` runs the existing complete
behavior set plus types; milestone suites remain separately requested.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_GIT_REPOSITORY_CONTEXT = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX", "GIT_NAMESPACE", "GIT_QUARANTINE_PATH",
)


def _subprocess_environment() -> dict[str, str]:
    """Let child Git commands resolve their cwd instead of the parent hook."""
    environment = os.environ.copy()
    for name in _GIT_REPOSITORY_CONTEXT:
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUTF8"] = "1"
    environment["PYTHON_DOTENV_DISABLED"] = "1"
    environment["REVENUE_ATTESTATION_PROVIDER"] = ""
    return environment


def _safe_console() -> None:
    """Windows consoles default to GBK; a captured tool output containing any
    non-GBK byte would crash the gate while *reporting* a failure, masking the
    real result.  Reconfigure to UTF-8 with replacement (filing-fetch hit this
    in its gate; revenue hit it on 2026-09-08 while printing a drift diff)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def _run(
    cmd: list[str], label: str, timeout: int = 300, *, blocking: bool = True
) -> int:
    print(f"\n=== {label} ===")
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_subprocess_environment(),
        timeout=timeout,
    )
    tail = (proc.stdout or "")[-2000:] + (proc.stderr or "")[-1000:]
    if proc.returncode != 0:
        print(tail)
        if blocking:
            print(f"FAILED: {label}")
    else:
        print(tail.strip()[-500:] or "ok")
    return proc.returncode



CI_TESTS = (
    "tests/test_authoring_projection.py",
    "tests/test_authoring_projection_basis.py",
    "tests/test_architecture_dependency_uses.py",
    "tests/test_architecture_numeric_errors.py",
    "tests/test_shared_excerpt_claim_semantics.py",
    "tests/test_m3_acquisition_usage_acceptance.py",
    "tests/test_m3_period_flow_consumers.py",
    "tests/test_m3_period_flow_annual_consumers.py",
    "tests/test_m3_evidence_roles.py",
    "tests/test_w05_dated_contribution_contract.py",
    "tests/test_w05_dated_contribution_composition.py",
    "tests/test_w05_dated_contribution_output.py",
    "tests/test_w05_root_temporal_lineage.py",
    "tests/test_mixed_aggregate_recognition.py",
    "tests/test_ci_smoke_plan.py",
    "tests/test_pre_push_gate_git_hook_env.py",
    "tests/test_p5_source_default_v2.py",
    "tests/test_company_wiki_source_ref_v2.py",
    "tests/test_company_wiki_source_v2.py",
    "tests/test_source_preparation.py",
    "tests/test_decoupled_source_port.py",
    "tests/test_company_wiki_source_reader_v2.py",
    "tests/test_data_contract.py",
    "tests/test_summary_publication_lineage.py",
    "tests/test_summary_long_excerpt.py",
    "tests/test_w04_financial_communication_window.py",
    "tests/test_recognition_bridge.py",
    "tests/test_confidence_determinism.py",
    "tests/test_confidence_source_freshness.py",
    "tests/test_registry_confidence_generations.py",
    "tests/test_real_source_quote_confidence.py",
    "tests/test_sensitivity_dependency_dag.py",
    "tests/test_published_foundation_roundtrip.py",
    "tests/test_growth_driver_tree.py",
    "tests/test_revenue_constraints.py",
    "tests/test_schema_compatibility.py",
    "tests/test_research_support_diagnostics.py",
    "tests/test_scoped_calibration_support.py",
    "tests/test_r1_source_boundary.py",
    "tests/test_r1_target_scope.py",
    "tests/test_r1_narrative_availability.py",
    "tests/test_r1_local_preparation_observation.py",
    "tests/test_rf_job_facade_cli.py",
    "tests/test_report_catalog.py::test_public_report_catalog_cli_uses_only_the_selected_owner",
    "tests/test_report_catalog.py::test_default_catalog_refuses_links_to_another_owner",
    "tests/b34_publication/test_publication.py::test_native_stages_and_successful_whole_run_are_distinct",
)


# Preserve the historical imported table as the full CI behavior set.
SMOKE_TESTS = CI_TESTS

# Explicit nodes keep routine push work stable when other files gain tests.
# Authors separately run the behavior suites relevant to their change.
LOCAL_SMOKE_TESTS = (
    "tests/test_p5_source_default_v2.py::test_default_entry_uses_source_ref_v2_without_opt_in",
    "tests/test_p5_source_default_v2.py::test_repeated_default_preparation_reuses_without_shadow_jobs",
    "tests/test_company_wiki_source_ref_v2.py::test_producer_golden_is_pinned_and_accepted_by_reader",
    "tests/test_company_wiki_source_ref_v2.py::test_malformed_source_ref_is_rejected_before_reader_io",
    "tests/test_company_wiki_source_v2.py::test_verified_ref_builds_schema_compatible_record_without_physical_path",
    "tests/test_data_contract.py::DataContractTests::test_valid_document",
    "tests/test_data_contract.py::DataContractTests::test_claim_must_bind_to_captured_snapshot",
    "tests/test_data_contract.py::DataContractTests::test_rejects_future_information",
    "tests/test_data_contract.py::DataContractTests::test_reported_revenue_dimension_is_enforced",
    "tests/test_recognition_bridge.py::RecognitionBridgeTests::test_company_aggregates_recognized_segments",
    "tests/test_published_foundation_roundtrip.py::test_foundation_inventory_roundtrips_actual_base_total_and_stock_ids",
    "tests/test_published_foundation_roundtrip.py::test_forged_opening_base_or_adjustment_is_rejected",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci", action="store_true", help="Run public types and the complete CI behavior set.")
    options = parser.parse_args(argv)
    _safe_console()
    gates = [
        ([sys.executable, "-m", "ruff", "check", "scripts", "tests", "tools", "e2e"], "ruff"),
    ]
    if options.ci:
        gates.append(([sys.executable, "-m", "mypy", "scripts/contracts/", "scripts/schema_compatibility.py",
            "scripts/filing_fetch_client.py", "scripts/trust_anchor.py",
            "scripts/company_wiki_narrative_contracts.py"], "public contract types"))
    tests = CI_TESTS if options.ci else LOCAL_SMOKE_TESTS
    gates.append(([sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider", *tests],
        "complete CI source and forecast behavior" if options.ci else "fixed local source/ref/forecast smoke"))
    with tempfile.TemporaryDirectory(prefix="rf-ci-" if options.ci else "rf-local-") as scratch:
        for command, label in gates:
            if command[:3] == [sys.executable, "-m", "pytest"]:
                command = [*command, "--basetemp", scratch]
            rc = _run(command, label)
            if rc:
                return rc
    print("\nCI behavior checks GREEN" if options.ci else "\nlocal_fast_pass: fixed smoke GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
