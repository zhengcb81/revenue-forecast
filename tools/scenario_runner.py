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
    "DL-04": ("wiki", "tests/contract/test_source_catalog_download_authorization.py", "CN download authorized"),
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
    # REV: revenue specific
    "REV-01": ("revenue", "tests/test_zr701_f1_draft_formal.py", "processing demand"),
    "REV-02": ("revenue", "tests/test_publication_registry.py", "publication registry"),
    # ZJ: Zijin
    "ZJ-01": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin FY2025 resolve"),
    "ZJ-02": ("revenue", "tests/test_zr709_zijin_journey.py", "Zijin FY2024 resolve"),
}

# Scenarios that need T3/T4 authorization — marked blocked
BLOCKED_SCENARIOS = {
    # DL: need real provider
    "DL-04", "DL-05", "DL-06",
    # LT: need real provider
    "LT-02", "LT-08", "LT-09",
    # UJ: need real provider
    "UJ-03", "UJ-05",
    # CTRL: need production canary
    "CTRL-04",
    # MIG: need production canary
    "MIG-04",
    # AUD: need real T3
    "AUD-06",
}


def run_test(repo: str, test_file: str, timeout: int = 300) -> tuple[bool, str]:
    """Run a single test file and return (passed, output_summary)."""
    repo_root = {
        "revenue": PROJECT_ROOT,
        "wiki": PROJECT_ROOT.parent / "company-wiki",
        "filing": PROJECT_ROOT.parent / "filing-fetch",
    }[repo]
    test_path = repo_root / test_file
    if not test_path.exists():
        return False, f"test file not found: {test_file}"
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", str(test_path), "-q", "--tb=line"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo_root),
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

        repo, test_file, desc = mapping
        run_count += 1
        print(f"[{run_count}] {sid}: {desc} ({repo}/{test_file})")
        passed, summary = run_test(repo, test_file)
        print(f"    -> {'PASS' if passed else 'FAIL'}: {summary}")

        evidence_file = EVIDENCE_ROOT / f"{sid.replace('-', '_')}.json"
        evidence = {
            "scenario_id": sid,
            "test_file": test_file,
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
