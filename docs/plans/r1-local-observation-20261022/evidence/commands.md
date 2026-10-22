# Reproduce (offline)

Use an installed Python with pytest/ruff/mypy. From this worktree set PYTHONPATH to its scripts, PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1 and TEMP/TMP to a fresh owned scratch directory. No production configuration is used.

RED was run against base674d08d9 before runtime edits with test_r1_local_preparation_observation.py, yielding8F/36P. The final suite adds same-class address and transparent-owner controls; it contains56 new cases.

Final related command (absolute interpreter used on this host: company-wiki/.venv/Scripts/python.exe):

    python -m pytest tests/test_r1_local_preparation_observation.py tests/test_source_failure_cause.py tests/test_r1_source_boundary.py tests/test_filing_fetch_client.py tests/test_source_preparation.py tests/test_source_preparation_complete_result.py tests/test_source_preparation_deadline.py tests/test_m3_acquisition_usage_acceptance.py tests/test_architecture_dependency_uses.py tests/test_ci_smoke_plan.py -q --tb=short -p no:cacheprovider -o junit_family=legacy --basetemp <owned-scratch>/frozen --junitxml <owned-scratch>/frozen.xml

Result201P/1S/14.52s. The single skip is the pre-existing opt-in real CWP/FF three-checkout test (CWP_V2_CODE_ROOT/W02_FF_CODE_ROOT unset), not one of the56 new cases. Four real RF CLI replays cover small/600 diagnostics at client and source_preparation; two further real source_preparation CLI controls reject path/oversize optional data but preserve cause/exit/counters.

    python -m ruff check scripts tests tools e2e
    python -m mypy scripts/filing_upstream_cause.py scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py scripts/company_wiki_narrative_contracts.py --cache-dir <owned-scratch>/mypy

13 files includes unchanged existing12 public modules plus the directly changed cause helper. Normal git commit used default Miniconda Python with test PYTHONPATH removed; all existing hooks passed. Hook's first failed attempt is retained as commit.log, successful normal attempt as commit-final.log. No skip flags were used.

RF product does not import FF or CWP internals. The FF fixture provenance remains6dbb9e84, and public hygiene is aligned with finalFF136ab5a627083f173c60fc88b7b3f74879a4bf99. Full actual producer integration is ROOT-owned.
