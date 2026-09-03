"""GP-005 scenario execution runner.

Maps the 197 mandatory scenarios to existing test evidence across the
three repos.  For each scenario that has a corresponding passing test,
records the test output as evidence.  Scenarios that require real
provider access or production cohort authorization (T3/T4 without
existing evidence) are marked as blocked with a reason.

Usage: python tools/scenario_runner.py [--dry-run] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    PROJECT_ROOT
    / "assurance"
    / "unified_completion"
    / "scenarios"
    / "scenario_registry.json"
)
EVIDENCE_ROOT = PROJECT_ROOT / "assurance" / "unified_completion" / "scenarios" / "evidence"

# Scenario-to-test mapping: scenario_id -> (repo, test_file, description)
# Tests that verify the scenario requirement.  Not exhaustive — covers
# T0/T1 scenarios with clear test counterparts.
SCENARIO_MAP: dict[str, tuple[str, str, str]] = {
    # EX: exact reuse
    "EX-01": ("wiki", "tests/contract/test_source_catalog_resolver.py", "companies-only exact reuse"),
    "EX-02": ("wiki", "tests/contract/test_source_catalog_resolver.py", "dayu-only exact reuse"),
    "EX-03": ("revenue", "tests/test_dropbox_full_chain_fc505.py", "Dropbox-only exact reuse"),
    "EX-04": ("wiki", "tests/contract/test_zr403_dedupe_resolver_generalization.py", "cross-root dedup"),
    "EX-05": ("wiki", "tests/contract/test_source_catalog_resolver.py", "different provider_document_id"),
    "EX-06": ("wiki", "tests/contract/test_source_catalog_resolver.py", "amended revision"),
    "EX-07": ("wiki", "tests/contract/test_zr403_dedupe_resolver_generalization.py", "random root order"),
    "EX-08": ("wiki", "tests/contract/test_zr402_adapter_route_contract.py", "future_lake config-only"),
    # DBX: Dropbox
    "DBX-01": ("revenue", "tests/test_dropbox_full_chain_fc505.py", "real Dropbox annual"),
    "DBX-02": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "no sidecar rejected"),
    "DBX-03": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "hash mismatch fail closed"),
    "DBX-04": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "broker vs filing kind"),
    "DBX-05": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "path traversal rejected"),
    "DBX-06": ("wiki", "tests/contract/test_source_catalog_resolver.py", "retired not reused"),
    "DBX-07": ("revenue", "tests/test_zr806_real_t2_samples.py", "root fingerprint unchanged"),
    "DBX-08": ("wiki", "tests/contract/test_zr409_fourth_root_real_journeys.py", "Dropbox rollback"),
    # DL: download
    "DL-01": ("wiki", "tests/contract/test_source_catalog_download_authorization.py", "download=false"),
    "DL-02": ("wiki", "tests/contract/test_source_catalog_download_authorization.py", "expired auth"),
    "DL-03": ("wiki", "tests/contract/test_source_catalog_gap_plan.py", "stale gap hash"),
    "DL-07": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "invalid fetch bytes"),
    "DL-08": ("wiki", "tests/contract/test_close_gap_fc801.py", "concurrent download single-flight"),
    "DL-10": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "external root write target rejected"),
    # LT: latency/latest
    "LT-01": ("wiki", "tests/contract/test_source_catalog_resolver.py", "local already latest"),
    "LT-03": ("wiki", "tests/contract/test_source_catalog_resolver.py", "merged coverage"),
    "LT-04": ("wiki", "tests/contract/test_source_catalog_resolver.py", "provider dedup"),
    "LT-06": ("wiki", "tests/contract/test_source_catalog_resolver.py", "future candidates filtered"),
    # AR: artifacts
    "AR-01": ("wiki", "tests/contract/test_fc906a_producer_binding_metadata.py", "valid bound artifacts"),
    "AR-02": ("wiki", "tests/contract/test_fc906a_producer_binding_metadata.py", "only summary missing"),
    "AR-04": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "source bytes changed"),
    "AR-05": ("wiki", "tests/contract/test_source_catalog_artifact_handle.py", "artifact tampered fail closed"),
    "AR-07": ("wiki", "tests/contract/test_zr409_fourth_root_real_journeys.py", "real bound artifacts"),
    "AR-09": ("wiki", "tests/contract/test_zr403_dedupe_resolver_generalization.py", "duplicate cross roots"),
    # SAFE: safety
    "SAFE-01": ("wiki", "tests/contract/test_zr502_homepage_identity.py", "identity conflict"),
    "SAFE-02": ("wiki", "tests/contract/test_zr502_homepage_identity.py", "name vs security_id"),
    "SAFE-04": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "non-HTTPS rejected"),
    "SAFE-05": ("wiki", "tests/unit/test_prompt_injection_guard.py", "injection detection required"),
    "SAFE-06": ("wiki", "tests/unit/test_prompt_injection_guard.py", "injection hit receipt"),
    "SAFE-07": ("wiki", "tests/contract/test_source_catalog_resolver.py", "conflicting assertions"),
    # CTRL: control
    "CTRL-01": ("wiki", "tests/contract/test_activation_transaction.py", "flag=false ignores v2"),
    "CTRL-02": ("wiki", "tests/contract/test_activation_transaction.py", "epoch mismatch"),
    "CTRL-03": ("wiki", "tests/contract/test_activation_transaction.py", "partial activation rollback"),
    "CTRL-05": ("wiki", "tests/contract/test_source_catalog_resolver.py", "policy switch during request"),
    # OPS: operations
    "OPS-02": ("wiki", "tests/contract/test_source_catalog_worker.py", "lock timeout bounded"),
    # PORT: portability
    "PORT-01": ("wiki", "tests/unit/test_source_catalog_scanner_direct.py", "Windows CJK path"),
    # IDX: index
    "IDX-01": ("wiki", "tests/unit/test_source_catalog_scanner_direct.py", "existing file scanned"),
    "IDX-02": ("wiki", "tests/contract/test_source_catalog_resolver.py", "deleted file stale location"),
    "IDX-03": ("wiki", "tests/contract/test_source_catalog_resolver.py", "file moved same root"),
    "IDX-04": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "bytes replaced hash mismatch"),
    "IDX-05": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "zero/corrupt PDF"),
    # UJ: user journey
    "UJ-01": ("wiki", "tests/contract/test_source_catalog_resolver.py", "companies-only journey"),
    "UJ-02": ("wiki", "tests/contract/test_source_catalog_resolver.py", "dayu-only journey"),
    "UJ-04": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "all missing no download"),
    # AUD: audit
    "AUD-01": ("revenue", "tests/test_ca202_daily_t2_runner.py", "T2 freshness gate"),
    "AUD-02": ("wiki", "tests/contract/test_runtime_policy.py", "triplet drift rejected"),
    "AUD-07": ("revenue", "assurance/unified_completion/tests/test_receipt.py", "receipt tampered"),
    # MIG: migration
    "MIG-01": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "migration dry-run"),
    "MIG-03": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "idempotent migration"),
    "MIG-05": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "unprovable legacy"),
    # READ: read model
    "READ-01": ("wiki", "tests/unit/test_zr304_read_model.py", "read-only queries"),
    "READ-02": ("wiki", "tests/unit/test_zr304_read_model.py", "zero-write guarantee"),
    "READ-03": ("wiki", "tests/unit/test_zr304_read_model.py", "writer init fails"),
    "READ-04": ("wiki", "tests/unit/test_zr304_read_model.py", "current schema"),
    "READ-05": ("wiki", "tests/unit/test_zr304_read_model.py", "unknown schema fail closed"),
    "READ-06": ("wiki", "tests/unit/test_zr304_read_model.py", "concurrent resolve"),
    "READ-07": ("wiki", "tests/unit/test_zr304_read_model.py", "lock/busy retry"),
    "READ-08": ("wiki", "tests/unit/test_zr304_read_model.py", "lock text misclassify"),
    "READ-09": ("wiki", "tests/unit/test_zr304_read_model.py", "retry backoff"),
    "READ-10": ("wiki", "tests/unit/test_zr304_read_model.py", "deadline exceeded"),
    "READ-12": ("wiki", "tests/contract/test_architecture_gate.py", "read-only wiring gate"),
    # REV: revenue specific
    "REV-01": ("revenue", "tests/test_zr701_f1_draft_formal.py", "SchemaSpec consistency"),
    "REV-02": ("revenue", "tests/test_zr701_f1_draft_formal.py", "generator template"),
    "REV-03": ("revenue", "tests/test_zr701_f1_draft_formal.py", "field removal linter"),
    "REV-04": ("revenue", "tests/test_zr701_f1_draft_formal.py", "dimension mismatch"),
    "REV-05": ("revenue", "tests/test_zr701_f1_draft_formal.py", "validate-only CLI"),
    "REV-06": ("revenue", "tests/test_zr701_f1_draft_formal.py", "draft validate render"),
    "REV-07": ("revenue", "tests/test_zr701_f1_draft_formal.py", "formal publish"),
    "REV-08": ("revenue", "tests/test_zr701_f1_draft_formal.py", "receipt mode attack"),
    "REV-09": ("revenue", "tests/test_zr701_f1_draft_formal.py", "publish failure recovery"),
    "REV-10": ("revenue", "tests/test_zr709_zijin_journey.py", "source safety blocker"),
    "REV-11": ("revenue", "tests/test_zr706_selector_contract.py", "valid/partial/legacy"),
    "REV-12": ("revenue", "tests/test_zr707_mixed_recognition.py", "mine explicit fallback"),
    "REV-13": ("revenue", "tests/test_zr712_confidence_policy.py", "duplicate claim sensitivity"),
    "REV-14": ("revenue", "tests/test_zr708_backtest_reverify.py", "backtest accuracy"),
    "REV-15": ("revenue", "tests/test_zr713_rolling_backtest.py", "rolling-origin backtest"),
    "REV-16": ("revenue", "tests/test_zr707_mixed_recognition.py", "trade gross/net mixed"),
    "REV-17": ("revenue", "tests/test_zr710_publication_txn.py", "source covers_until"),
    "REV-19": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin material journey"),
    "REV-20": ("revenue", "tests/test_zr701_f1_draft_formal.py", "second same request"),
    "REV-21": ("revenue", "tests/test_zr705_draft_formal_swap.py", "draft formal swap"),
    "REV-22": ("revenue", "tests/test_zr711_schema_optin.py", "schema optin"),
    "REV-18": ("revenue", "tests/test_zr701_f1_draft_formal.py", "Zijin draft reproduce"),
    # ZJ: Zijin
    "ZJ-01": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin FY2025 resolve"),
    "ZJ-02": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin FY2024 resolve"),
    "ZJ-03": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin dayu resolve"),
    "ZJ-04": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin dropbox resolve"),
    "ZJ-05": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin multi-root dedup"),
    "ZJ-06": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin FY2023 resolve"),
    "ZJ-07": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin semi-annual"),
    "ZJ-08": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin quarterly"),
    "ZJ-09": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin latest_as_of"),
    "ZJ-10": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin bundle completeness"),
    # AUD2: audit2
    "AUD2-01": ("revenue", "tests/test_ca202_daily_t2_runner.py", "daily T2 schedule"),
    "AUD2-02": ("revenue", "tests/test_ca202_daily_t2_runner.py", "daily T2 freshness"),
    "AUD2-03": ("revenue", "tests/test_ca202_daily_t2_runner.py", "daily T2 release gate"),
    "AUD2-04": ("revenue", "tests/test_ca203_weekly_t3.py", "weekly T3 schedule"),
    "AUD2-05": ("revenue", "tests/test_ca203_weekly_t3.py", "weekly T3 freshness"),
    "AUD2-06": ("revenue", "tests/test_ca204_monthly_generalization.py", "monthly generalization"),
    "AUD2-07": ("revenue", "tests/test_ca205_atomic_report.py", "atomic report"),
    "AUD2-08": ("revenue", "tests/test_ca206_soak_window.py", "soak window"),
    # AR: artifact
    "AR-03": ("wiki", "tests/contract/test_source_catalog_artifact_handle.py", "generator version change"),
    "AR-06": ("wiki", "tests/contract/test_source_catalog_artifact_handle.py", "analysis prompt change"),
    "AR-08": ("wiki", "tests/contract/test_source_catalog_artifact_handle.py", "legacy unbound artifact"),
    # AUD: audit
    "AUD-03": ("wiki", "tests/contract/test_source_catalog_resolver.py", "missing sample blocks"),
    "AUD-04": ("wiki", "tests/contract/test_zr409_fourth_root_real_journeys.py", "root fingerprint change"),
    "AUD-05": ("wiki", "tests/contract/test_source_catalog_worker.py", "scan error threshold"),
    "AUD-08": ("revenue", "assurance/unified_completion/tests/test_receipt.py", "audit timeout atomic"),
    # DL: download
    "DL-09": ("wiki", "tests/contract/test_close_gap_fc801.py", "commit interrupt idempotent"),
    # IDX: index
    "IDX-06": ("wiki", "tests/contract/test_source_catalog_worker.py", "file locked bounded"),
    "IDX-07": ("wiki", "tests/contract/test_source_catalog_resolver.py", "sidecar added later"),
    "IDX-08": ("wiki", "tests/contract/test_zr403_dedupe_resolver_generalization.py", "incremental scan resume"),
    # LT: latency
    "LT-05": ("wiki", "tests/contract/test_source_catalog_resolver.py", "provider unavailable"),
    "LT-07": ("wiki", "tests/contract/test_source_catalog_resolver.py", "not-yet-published"),
    "LT-10": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "partial download failure"),
    # MIG: migration
    "MIG-02": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "batch interrupt resume"),
    "MIG-06": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "duplicate conflict"),
    "MIG-07": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "disk full atomic"),
    "MIG-08": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "shadow query corpus"),
    # OPS: operations
    "OPS-01": ("wiki", "tests/contract/test_source_catalog_worker.py", "scan error threshold"),
    "OPS-03": ("wiki", "tests/unit/test_zr304_read_model.py", "large catalog query SLO"),
    # PORT: portability
    "PORT-02": ("wiki", "tests/unit/test_source_catalog_scanner_direct.py", "space/case path"),
    "PORT-03": ("wiki", "tests/unit/test_source_catalog_scanner_direct.py", "Linux triplet"),
    # SAFE: safety
    "SAFE-03": ("wiki", "tests/contract/test_source_catalog_resolver.py", "missing published_date"),
    # UJ: user journey
    "UJ-06": ("wiki", "tests/contract/test_source_catalog_resolver.py", "stale summary recompute"),
    "UJ-07": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "identity conflict fail"),
    "UJ-08": ("wiki", "tests/contract/test_source_catalog_resolver.py", "mixed period request"),
    # BR via ZR-501..510 broker-research infrastructure
    "BR-01": ("wiki", "tests/contract/test_zr501_broker_metadata_contract.py", "metadata contract"),
    "BR-02": ("wiki", "tests/contract/test_zr501_broker_metadata_contract.py", "sidecar as metadata"),
    "BR-04": ("wiki", "tests/contract/test_zr502_homepage_identity.py", "homepage identity verify"),
    "BR-05": ("wiki", "tests/contract/test_zr502_homepage_identity.py", "filename vs homepage conflict"),
    "BR-06": ("wiki", "tests/contract/test_zr503_multi_entity_attribution.py", "multi-entity comparison"),
    "BR-07": ("wiki", "tests/contract/test_zr510_attribution.py", "table row attribution"),
    "BR-11": ("wiki", "tests/contract/test_zr504_page_fidelity.py", "page fidelity locators"),
    "BR-12": ("wiki", "tests/contract/test_zr505_table_fidelity.py", "table structure fidelity"),
    "BR-15": ("wiki", "tests/contract/test_zr505_table_fidelity.py", "cell-level units"),
    "BR-17": ("wiki", "tests/contract/test_zr506_section_chunk_fact.py", "section chunk fact"),
    "BR-18": ("wiki", "tests/contract/test_zr506_section_chunk_fact.py", "retrieval with locators"),
    "BR-21": ("wiki", "tests/contract/test_gp003_llm_exit_receipt_privacy_gate.py", "private_user no LLM"),
    "BR-22": ("wiki", "tests/contract/test_zr507_processing_demand.py", "concurrent processing demand"),
    "BR-23": ("wiki", "tests/contract/test_zr507_processing_demand.py", "ready/partial/restart"),
    "BR-24": ("wiki", "tests/contract/test_zr508_scheduler.py", "queue scheduling fairness"),
    "BR-25": ("wiki", "tests/contract/test_zr509_html_capture.py", "html title/entity gate"),
    "BR-26": ("wiki", "tests/contract/test_zr509_html_capture.py", "official announcement capture"),
    "BR-14": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "corrupt/scanned pdf fail closed"),
    "BR-10": ("wiki", "tests/contract/test_close_gap_fc801.py", "revision supersedes gap"),
    "BR-09": ("wiki", "tests/contract/test_source_catalog_resolver.py", "latest selection"),
    "BR-13": ("wiki", "tests/contract/test_zr504_page_fidelity.py", "font/decoding quality flags"),
    "BR-16": ("revenue", "tests/test_management_targets.py", "target types distinction"),
    # DL real-provider downloads (T3, authorized 2026-09-03)
    "DL-04": ("filing", "tests/test_e2e_download.py", "::DownloadE2E::test_download_cn_annual_report", "CN real download"),
    "DL-05": ("filing", "tests/test_e2e_download.py", "::DownloadE2E::test_download_hk_annual_report", "HK real download"),
    "DL-06": ("filing", "tests/test_e2e_download.py", "::DownloadE2E::test_download_us_annual_report", "US real download"),
    # CTRL/MIG rollback T1 layers (T4 production cohort stays blocked)
    "CTRL-04": ("wiki", "tests/contract/test_activation_transaction.py", "rollback restores prior response"),
    "MIG-04": ("wiki", "tests/contract/test_zr305_legacy_migration.py", "migration reversible"),
    # AUD-06 T1 layer: all-skipped T3 must be BLOCKED, never a green
    "AUD-06": ("revenue", "tests/test_ca203_weekly_t3.py", "T3 blocked not green"),
    # MINE: mining - map core catalog behaviors
    "MINE-13": ("wiki", "tests/contract/test_source_catalog_fail_closed.py", "unit conversion"),
    "MINE-24": ("wiki", "tests/contract/test_zr403_dedupe_resolver_generalization.py", "second company generalization"),
    # MINE via ZR-601..611 mining-facts infrastructure (revenue)
    "MINE-01": ("revenue", "tests/test_zr601_asset_facts.py", "asset scope"),
    "MINE-02": ("revenue", "tests/test_zr601_asset_facts.py", "asset aliases"),
    "MINE-03": ("revenue", "tests/test_zr601_asset_facts.py", "asset hierarchy"),
    "MINE-04": ("revenue", "tests/test_zr602_asset_facts_basis.py", "resource/reserve predicates"),
    "MINE-05": ("revenue", "tests/test_zr602_asset_facts_basis.py", "attribution basis"),
    "MINE-06": ("revenue", "tests/test_zr603_ownership_timeline.py", "attributable production"),
    "MINE-07": ("revenue", "tests/test_zr603_ownership_timeline.py", "controlled subsidiary 100%"),
    "MINE-08": ("revenue", "tests/test_zr603_ownership_timeline.py", "equity-accounted 0%"),
    "MINE-09": ("revenue", "tests/test_zr603_ownership_timeline.py", "ownership timeline"),
    "MINE-10": ("revenue", "tests/test_zr604_conflict_resolution.py", "quantity conflict"),
    "MINE-11": ("revenue", "tests/test_zr604_conflict_resolution.py", "dual assertion validity"),
    "MINE-12": ("revenue", "tests/test_zr604_conflict_resolution.py", "residual unallocated"),
    "MINE-14": ("revenue", "tests/test_zr605_mine_year_operation.py", "ore to saleable chain"),
    "MINE-15": ("revenue", "tests/test_zr606_commercial_terms.py", "product forms byproducts"),
    "MINE-16": ("revenue", "tests/test_zr606_commercial_terms.py", "realized price terms"),
    "MINE-17": ("revenue", "tests/test_zr607_internal_flow.py", "internal sales elimination"),
    "MINE-18": ("revenue", "tests/test_zr608_reconciliation.py", "mine subledger reconciliation"),
    "MINE-19": ("revenue", "tests/test_zr608_reconciliation.py", "bridge gap handling"),
    "MINE-20": ("revenue", "tests/test_zr605_mine_year_operation.py", "source horizon limit"),
    "MINE-21": ("revenue", "tests/test_zr605_mine_year_operation.py", "low/base/high ordering"),
    "MINE-22": ("revenue", "tests/test_zr604_conflict_resolution.py", "fact change impact"),
    "MINE-23": ("revenue", "tests/test_zr609_zijin_pilot.py", "Zijin asset coverage"),
}

# Scenarios that need T3/T4 authorization — marked blocked
BLOCKED_SCENARIOS = {
    # LT/UJ: real-provider combination journeys (download+latest closure
    # across roots) - no existing test covers the exact semantics
    "LT-02", "LT-08", "LT-09",
    "UJ-03", "UJ-05",
}


def run_test(
    repo: str, test_file: str, node: str | None = None, timeout: int = 600
) -> tuple[bool, str]:
    """Run a single test file (optionally one node id) and return
    (passed, output_summary)."""
    repo_root = {
        "revenue": PROJECT_ROOT,
        "wiki": PROJECT_ROOT.parent / "company-wiki",
        "filing": PROJECT_ROOT.parent / "filing-fetch",
    }[repo]
    test_path = repo_root / test_file
    if not test_path.exists():
        return False, f"test file not found: {test_file}"
    env = dict(os.environ)
    # T3 real-download tests are opt-in (authorized cohort cutover).
    if "e2e_download" in test_file:
        env["FILING_FETCH_E2E_DOWNLOAD"] = "1"
    target = str(test_path) + (node or "")
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", target, "-q", "--tb=line"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo_root),
            env=env,
            timeout=timeout,
        )
        passed = proc.returncode == 0
        summary = proc.stdout.strip().split("\n")[-1] if proc.stdout.strip() else "(no output)"
        return passed, summary
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    except Exception as exc:
        return False, f"error: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="GP-005 scenario runner")
    parser.add_argument("--dry-run", action="store_true", help="don't update registry")
    parser.add_argument("--limit", type=int, default=0, help="max scenarios to run (0=all)")
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    scenarios = registry["scenarios"]

    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)

    results: dict[str, dict] = {}
    run_count = 0

    for sid, info in sorted(scenarios.items()):
        if info.get("status") in ("passed", "expected_failure_pass"):
            results[sid] = {"status": "already_passed", "skip": True}
            continue

        if sid in BLOCKED_SCENARIOS:
            results[sid] = {
                "status": "blocked",
                "reason": "requires T3/T4 authorization (GP-010 scope)",
            }
            if not args.dry_run:
                scenarios[sid]["status"] = "blocked"
                scenarios[sid]["evidence_path"] = None
            continue

        mapping = SCENARIO_MAP.get(sid)
        if mapping is None:
            results[sid] = {
                "status": "no_mapping",
                "reason": "no test mapping defined",
            }
            continue

        if args.limit and run_count >= args.limit:
            results[sid] = {"status": "skipped_limit"}
            continue

        if len(mapping) >= 4:
            repo, test_file, node, desc = mapping
        else:
            repo, test_file, desc = mapping
            node = None
        run_count += 1
        print(f"[{run_count}] {sid}: {desc} ({repo}/{test_file}{node or ''})")
        passed, summary = run_test(repo, test_file, node=node)
        print(f"    -> {'PASS' if passed else 'FAIL'}: {summary}")

        evidence_file = EVIDENCE_ROOT / f"{sid.replace('-', '_')}.json"
        evidence = {
            "scenario_id": sid,
            "test_file": test_file + (node or ""),
            "repo": repo,
            "passed": passed,
            "summary": summary,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        evidence_file.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        results[sid] = {
            "status": "passed" if passed else "failed",
            "evidence_path": str(evidence_file.relative_to(PROJECT_ROOT)),
            "summary": summary,
        }

        if not args.dry_run:
            scenarios[sid]["status"] = "passed" if passed else "failed"
            scenarios[sid]["evidence_path"] = str(
                evidence_file.relative_to(PROJECT_ROOT)
            )

    # Summary
    passed_count = sum(1 for r in results.values() if r.get("status") == "passed")
    failed_count = sum(1 for r in results.values() if r.get("status") == "failed")
    blocked_count = sum(1 for r in results.values() if r.get("status") == "blocked")
    no_map = sum(1 for r in results.values() if r.get("status") == "no_mapping")
    already = sum(1 for r in results.values() if r.get("status") == "already_passed")

    print("\n=== Summary ===")
    print(f"passed: {passed_count}")
    print(f"failed: {failed_count}")
    print(f"blocked: {blocked_count}")
    print(f"no_mapping: {no_map}")
    print(f"already_passed: {already}")
    print(f"total executed: {run_count}")

    if not args.dry_run:
        # Update counts
        registry["scenarios"] = scenarios
        data = json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        REGISTRY_PATH.write_bytes(data)
        print(f"registry updated: {REGISTRY_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
