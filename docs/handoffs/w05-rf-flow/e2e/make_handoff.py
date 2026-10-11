"""Generate handoff.json + manifest.json for the W05-RF-FLOW lane (run once)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
BASE = "1b616622763ece6549676f2a74f596e6c65244af"
head1 = sys.argv[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


changed = subprocess.run(
    ["git", "diff", "--name-only", f"{BASE}..HEAD"],
    capture_output=True, text=True, check=True,
).stdout.split()

PURPOSE = {
    "scripts/contracts/constants.py": "schema 3.10 constant + schema families + SKILL_VERSION 4.3.0",
    "scripts/contracts/period_flow.py": "schema-aware window validator (3.9 default) + 3.10 composition honesty",
    "scripts/contracts/document.py": "accept schema 3.10, family-gated dated basis, window semantic key, composition call",
    "scripts/contracts/annual_consumption.py": "single annual-consumption rule now covers the 3.9/3.10 family",
    "scripts/schema_compatibility.py": "3.10 emit row (4.3.0 only) + literal 4.2.1 history pins + bound-input set",
    "scripts/research/drivers.py": "role-aware mechanism triangulation keyed on the 3.9/3.10 family",
    "scripts/revenue_core.py": "public re-exports of the new schema constants",
    "scripts/revenue_report.py": "bound-input identity guard against rehashed date/currency/scope tamper",
    "scripts/generate_input_template.py": "3.10 template comment and --schema help wiring only",
    "CHANGELOG.md": "4.3.0 release entry (emit-matrix provenance for the registry)",
    "SKILL.md": "dated-contribution capability paragraph",
    "references/dated-contribution.md": "new engineering contract for dated consolidated contributions",
    "references/input-schema.md": "time_basis vocabulary note incl. 3.9/3.10 pointers",
    "references/input-construction.md": "authoring rules for schema 3.10 dated contributions",
    "references/output-schema.md": "output identity guard + real-window rendering note",
    "tests/test_data_contract.py": "engine version pin 4.2.1 -> 4.3.0 (string only, reason listed)",
    "tests/test_m3_period_flow_contract.py": "engine version pins 4.2.1 -> 4.3.0 (strings only)",
    "tests/test_m3_schema_compatibility.py": "engine version pin 4.2.1 -> 4.3.0 (string only)",
    "tests/test_schema_compatibility.py": "engine pin + schema-vocabulary pins (3.10 row added; unknown-schema probe 3.10 -> 3.11)",
}


def purpose(path: str) -> str:
    if path in PURPOSE:
        return PURPOSE[path]
    if path.startswith("tests/test_w05_dated_contribution_contract"):
        return "new TDD suite: window/date rules, 3.9/3.7/3.8 compatibility, sealed counterexample"
    if path.startswith("tests/test_w05_dated_contribution_composition"):
        return "new TDD suite: composition honesty, scope, stocks, units, conflicts"
    if path.startswith("tests/test_w05_dated_contribution_output"):
        return "new TDD suite: DAG entry, report, output/snapshot tamper, registry, role-aware"
    if path.startswith(".planning/"):
        return "lane PWF record"
    if path.startswith("docs/handoffs/"):
        return "lane handoff evidence"
    return "lane record"


changed_files = [
    {"path": p, "sha256": sha256(ROOT / p), "purpose": purpose(p)}
    for p in changed
]

input_dir = Path("docs/handoffs/w05-rf-flow/input")
input_evidence = [
    {
        "path": f"docs/handoffs/w05-rf-flow/input/{f.name}",
        "sha256": sha256(f),
        "bytes": f.stat().st_size,
    }
    for f in sorted(input_dir.iterdir()) if f.is_file()
]

logs = Path("docs/handoffs/w05-rf-flow/logs")


def log_entry(name: str) -> dict:
    p = logs / name
    return {"log": f"docs/handoffs/w05-rf-flow/logs/{name}", "log_sha256": sha256(p)}


tests = [
    {
        "phase": "RED",
        "command": "python -B -m pytest -q tests/test_w05_dated_contribution_contract.py tests/test_w05_dated_contribution_composition.py tests/test_w05_dated_contribution_output.py",
        "exit_code": 1,
        "counts": {"failed": 41, "passed": 12, "subtests_passed": 12},
        "elapsed_seconds": 6.9,
        "scope": "real business RED: native entry rejects schema 3.10 incl. the sealed 2026-05-31..2026-06-30 window; one case is an API-shape TypeError on the not-yet-existing schema_version kwarg (not claimed as business RED)",
        **log_entry("phaseA_red.txt"),
    },
    {
        "phase": "GREEN",
        "command": "python -B -m pytest -q tests/test_m3_period_flow_contract.py tests/test_m3_period_flow_consumers.py tests/test_m3_period_flow_annual_consumers.py tests/test_m3_schema_compatibility.py tests/test_schema_compatibility.py tests/test_w05_dated_contribution_contract.py tests/test_w05_dated_contribution_composition.py tests/test_w05_dated_contribution_output.py",
        "exit_code": 0,
        "counts": {"passed": 120, "subtests_passed": 33},
        "elapsed_seconds": 7.23,
        "scope": "centralized legacy suites + new 3.10 suites green; only version-string/vocabulary pins updated",
        **log_entry("phaseB_final_consolidated.txt"),
    },
    {
        "phase": "INTEGRATION",
        "command": "python -B -m pytest -q <40 consumer/report/pipeline/model test files listed in the log>",
        "exit_code": 0,
        "counts": {"passed": 448, "skipped": 4, "subtests_passed": 102},
        "elapsed_seconds": 75.7,
        "scope": "wide regression over output readers, publication pipeline, snapshot/backtest, models, calibration, acquisition usage; skips are pre-existing gates (golden lock requires 4.1.0)",
        **log_entry("phaseB_regression_all.txt"),
    },
    {
        "phase": "E2E",
        "command": "python -B scripts/revenue_forecast.py case1_acquisition.input.json --validate-only --verbose then --output case1_forecast.json --markdown case1_forecast.md",
        "exit_code": 0,
        "counts": {"validate": "valid", "forecast_report": "written"},
        "elapsed_seconds": None,
        "scope": "native CLI acquisition-contribution case: sealed window + synthetic H2 -> explicit derived FY bridge -> acquisition_contribution DAG adjustment",
        **log_entry("phaseC_case1_cli.txt"),
    },
    {
        "phase": "E2E",
        "command": "python -B docs/handoffs/w05-rf-flow/e2e/read_and_tamper.py case1_forecast.json window|currency",
        "exit_code": 0,
        "counts": {"reader": "PASS", "tamper_window": "rejected", "tamper_currency": "rejected"},
        "elapsed_seconds": None,
        "scope": "published output reader shows real windows/amounts/sources; rehash does not make the forgery pass",
        **log_entry("phaseC_case1_reader_tamper.txt"),
    },
    {
        "phase": "E2E",
        "command": "python -B scripts/revenue_forecast.py case2_offset_fy.input.json --validate-only; --output case2_forecast.json --markdown case2_forecast.md; read_and_tamper.py case2_forecast.json window",
        "exit_code": 0,
        "counts": {"validate": "valid", "forecast_report": "written", "tamper_window": "rejected"},
        "elapsed_seconds": None,
        "scope": "non-12-31 fiscal year case: 10-day window + exact partition composition (7+10+3=20) through the whole chain",
        **log_entry("phaseC_case2_cli.txt"),
    },
    {
        "phase": "E2E",
        "command": "python -B scripts/revenue_backtest.py create case1_acquisition.input.json --version w05-e2e-v1 --output case1_snapshot.json then validate_snapshot + rehashed window tamper",
        "exit_code": 0,
        "counts": {"snapshot_reader": "PASS", "snapshot_tamper": "rejected"},
        "elapsed_seconds": None,
        "scope": "native snapshot create + snapshot reader roundtrip + tamper rejection",
        **log_entry("phaseC_snapshot_report.txt"),
    },
]

interfaces = [
    {
        "name": "contracts.period_flow.validate_period_flow_fields",
        "before": "3 positional args, 3.9 semantics only (start<end, 3/6/12 months)",
        "after": "optional 4th param schema_version (default '3.9'); '3.10' admits start<=end any real window inside the FY; unknown schema fails closed",
        "compatibility": "old 3-arg calls keep the 3.9 meaning (test_pure_field_validator_defaults_to_3_9_and_takes_schema_explicitly)",
    },
    {
        "name": "contracts.period_flow.validate_windowed_composition",
        "before": "absent",
        "after": "3.10 derived dated composition honesty (containment, non-overlap or rationale, full-year completeness or rationale)",
        "compatibility": "called only for schema 3.10 derived period_flow parameters; 3.9/3.7/3.8 paths untouched",
    },
    {
        "name": "schema vocabulary (contracts.constants)",
        "before": "SUPPORTED set ends at 3.9",
        "after": "DATED_CONTRIBUTION_SCHEMA_VERSION='3.10', PERIOD_FLOW_SCHEMA_VERSIONS/MECHANISM_ROLE_SCHEMA_VERSIONS families, SUPPORTED includes 3.10; default schema still 3.7",
        "compatibility": "3.7/3.8/3.9 acceptance unchanged (centralized suites)",
    },
    {
        "name": "contracts.document.validate_*",
        "before": "accepts 3.7/3.8/3.9; period_flow gated to == 3.9",
        "after": "accepts 3.10; dated basis and window semantic-key extension follow the schema family; 3.10 derived windowed compositions validated",
        "compatibility": "3.7/3.8 reject period fields; 3.9 keeps 3/6/12 months",
    },
    {
        "name": "contracts.annual_consumption.validate_annual_consumption",
        "before": "runs only for schema 3.9",
        "after": "runs for the 3.9/3.10 family with identical rules (annual roles need full fiscal-year coverage)",
        "compatibility": "3.7/3.8 return early unchanged",
    },
    {
        "name": "schema_compatibility.SCHEMA_EMIT_ENGINES",
        "before": "3.7/3.8/3.9 rows reference the ENGINE_VERSION alias",
        "after": "4.2.1 pinned as literal versions; new 3.10 row = {4.3.0, ENGINE_VERSION}; BOUND_INPUT_SCHEMA_VERSIONS includes 3.10",
        "compatibility": "4.2.1 keeps validating 3.7/3.8/3.9 outputs/snapshots; 3.10 fails closed for every 4.2.x engine",
    },
    {
        "name": "revenue_report._validate_forecast_output (identity guard)",
        "before": "result identity fields not compared to the bound input",
        "after": "for bound-input schemas with the input present: company/as_of/currency/unit/fiscal_year_end/base_year/forecast_years/schema must equal the input",
        "compatibility": "only tightens modern strong validation; the legacy read-only path is unchanged",
    },
    {
        "name": "research.drivers role-aware triangulation",
        "before": "role_aware iff schema == 3.9",
        "after": "role_aware iff schema in {3.9, 3.10}",
        "compatibility": "3.7/3.8 legacy peer-only exclusion preserved (test_legacy_3_7_semantics_are_not_silently_changed)",
    },
    {
        "name": "revenue_core public surface / ENGINE_VERSION",
        "before": "ENGINE_VERSION = SKILL_VERSION = 4.2.1",
        "after": "ENGINE_VERSION = SKILL_VERSION = 4.3.0; DATED_CONTRIBUTION_SCHEMA_VERSION / PERIOD_FLOW_SCHEMA_VERSIONS / MECHANISM_ROLE_SCHEMA_VERSIONS re-exported",
        "compatibility": "version-string pins updated in old tests with the reason listed; no math/semantic assertion relaxed",
    },
    {
        "name": "generate_input_template.py --schema 3.10",
        "before": "skeleton notes for 3.8/3.9",
        "after": "3.10 skeleton comment carries the dated-contribution rules; old templates unchanged",
        "compatibility": "default --schema stays 3.7",
    },
]

findings = [
    {
        "id": "W05-001",
        "root_cause": "3.9 month rule ({3,6,12}) could not express real control windows; authors widened dates to fit (PROCESS-006)",
        "disposition": "fixed",
        "test_ids": ["test_real_control_window_validates_on_3_10", "test_3_9_keeps_strict_order_and_3_6_12_month_rule"],
        "evidence": ["docs/handoffs/w05-rf-flow/logs/phaseA_red.txt", "docs/handoffs/w05-rf-flow/e2e/artifacts/case1_acquisition.input.json"],
    },
    {
        "id": "W05-002",
        "root_cause": "a partial contribution could pose as a complete FY base and an out-of-scope pre-control gap could pass as zero-filled coverage",
        "disposition": "fixed",
        "test_ids": ["test_full_year_composition_without_explanation_rejected", "test_gap_is_never_silently_zero_filled", "test_partial_flow_cannot_be_annual_base_or_adjustment"],
        "evidence": ["references/dated-contribution.md"],
    },
    {
        "id": "W05-003",
        "root_cause": "overlapping same-window components (group total + acquired standalone; residual work split) double count or cross entity scope silently",
        "disposition": "fixed",
        "test_ids": ["test_overlapping_components_rejected_without_explanation", "test_cross_entity_same_window_merge_rejected_without_explanation", "test_residual_work_split_needs_explanation"],
        "evidence": ["docs/handoffs/w05-rf-flow/logs/phaseB_final_consolidated.txt"],
    },
    {
        "id": "W05-004",
        "root_cause": "output identity fields (currency/unit/dates/scope) were not compared to the frozen bound input, so rehashed tampering could pass",
        "disposition": "fixed",
        "test_ids": ["test_output_tamper_dates_currency_and_scope_rejected_even_rehashed"],
        "evidence": ["docs/handoffs/w05-rf-flow/logs/phaseC_case1_reader_tamper.txt"],
    },
    {
        "id": "W05-005",
        "root_cause": "the emit registry referenced the ENGINE_VERSION alias, so the 4.3.0 bump would erase the documented 4.2.1 emit history",
        "disposition": "fixed",
        "test_ids": ["test_4_2_1_emit_history_is_preserved_after_the_bump", "test_3_10_requires_the_new_engine_and_cannot_be_issued_by_4_2_x"],
        "evidence": ["scripts/schema_compatibility.py"],
    },
    {
        "id": "W05-006",
        "root_cause": "role-aware triangulation was keyed on schema == 3.9, so 3.10 would silently revert to legacy counting",
        "disposition": "fixed",
        "test_ids": ["test_history_background_does_not_triangulate_on_3_10", "test_true_mechanism_support_triangulates_on_3_10"],
        "evidence": ["scripts/research/drivers.py"],
    },
    {
        "id": "W05-007",
        "root_cause": "a self-consistent rewrite of a whole input plus its evidence references is not detectable by hashing alone",
        "disposition": "remaining",
        "test_ids": [],
        "evidence": ["references/dated-contribution.md", "CHANGELOG.md"],
    },
    {
        "id": "DIAG-01",
        "root_cause": "pre-existing KeyError carry_in_parameter_ids at scripts/forecast/calc.py in test_mixed_rejects_lagged_activity (reproduces at base 1b616622)",
        "disposition": "remaining",
        "test_ids": ["tests/test_mixed_aggregate_recognition.py::test_mixed_rejects_lagged_activity"],
        "evidence": [".planning/w05-rf-flow/findings.md"],
    },
    {
        "id": "DIAG-02",
        "root_cause": "tests/test_contract_registry.py and tests/test_compatibility_manifest.py fail collection: repo-root compatibility/ directory absent at baseline",
        "disposition": "remaining",
        "test_ids": [],
        "evidence": [".planning/w05-rf-flow/findings.md"],
    },
    {
        "id": "DIAG-03",
        "root_cause": "15 pre-existing mypy errors in scripts/revenue_report.py (identical at base); changed contract files clean",
        "disposition": "remaining",
        "test_ids": [],
        "evidence": [".planning/w05-rf-flow/findings.md"],
    },
]

retained = sum(
    p.stat().st_size
    for base in ("docs/handoffs/w05-rf-flow", ".planning/w05-rf-flow")
    for p in Path(base).rglob("*") if p.is_file()
)

handoff = {
    "schema_version": "w05-lane-handoff/1",
    "lane": "W05-RF-FLOW",
    "status": "COMPLETE",
    "repository": "C:/Users/郑曾波/Projects/revenue-forecast",
    "workdir": "C:/Users/郑曾波/Projects/_harness_worktrees/w05/rf-flow",
    "base_commit": BASE,
    "head_commit": head1,
    "branch": "codex/w05-rf-flow",
    "changed_files": changed_files,
    "input_evidence": input_evidence,
    "interfaces": interfaces,
    "tests": tests,
    "findings": findings,
    "cleanup": {
        "owned_root": "C:/Users/郑曾波/AppData/Local/Temp/w05-rf-flow-e2e-20261011",
        "baseline": "docs/handoffs/w05-rf-flow/logs/phaseC_scratch_initial.txt",
        "after": "docs/handoffs/w05-rf-flow/logs/phaseC_scratch_final.txt",
        "restored": True,
        "raw_unchanged": True,
    },
    "cost": {"provider_calls": 0, "model_calls": 0, "paid_usd": "0", "unknown_charge": None},
    "space": {"retained_bytes": retained, "scratch_peak_bytes": 512000, "measurement": "actual"},
    "remaining": [
        "ROOT integration: merge codex/w05-rf-flow to main; installation sync (tools/sync_installations.py) is ROOT-owned",
        "real-company economic end-to-end stays with ROOT at G4/G5; this lane's CLI E2E uses clearly synthetic fixture amounts and does not claim a buyer-grade PASS",
        "DIAG-01/02/03 pre-existing items above are outside this lane's writable set",
    ],
    "root_next_action": "integration, not claimed already merged",
}
out = Path("docs/handoffs/w05-rf-flow/handoff.json")
out.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out, "changed_files:", len(changed_files),
      "input_evidence:", len(input_evidence), "retained_bytes:", retained)

entries = []
for base in ("docs/handoffs/w05-rf-flow", ".planning/w05-rf-flow"):
    for p in sorted(Path(base).rglob("*")):
        if p.is_file() and p.resolve() != (ROOT / "docs/handoffs/w05-rf-flow/manifest.json").resolve():
            entries.append({
                "path": p.resolve().relative_to(ROOT).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": sha256(p),
            })
manifest = {"schema_version": "w05-lane-evidence-manifest/1", "lane": "W05-RF-FLOW", "files": entries}
Path("docs/handoffs/w05-rf-flow/manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote manifest.json entries:", len(entries))
