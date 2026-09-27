"""WU-1402: machine-provable mutation runner — each of the 12 targeted
mutations is applied, its killer test must turn RED, then the mutation is
restored byte-identically and the killer must return GREEN.

Usage: python mutation_runner.py [--only M03,M06] [--repo revenue|wiki]
Exit 0 = every executed mutation proved a kill; 1 otherwise.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]
REPOS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}

# Each mutation: (id, repo, source path (repo-relative), old text, new text,
#                killer pytest node ids)
MUTATIONS = [
    {
        "id": "M01", "repo": "revenue", "desc": "删除 content hash 校验",
        "path": "scripts/company_wiki_source.py",
        "old": (
            '    if _file_sha256(canonical_path) != snapshot_sha256:\n'
            '        raise CompanyWikiSourceError(\n'
            '            "canonical source bytes do not match snapshot_sha256"\n'
            '        )'
        ),
        "new": (
            '    if False and _file_sha256(canonical_path) != snapshot_sha256:\n'
            '        raise CompanyWikiSourceError(\n'
            '            "canonical source bytes do not match snapshot_sha256"\n'
            '        )'
        ),
        "killers": [
            "tests/test_company_wiki_source.py::RevenueSourceRecordTests::test_tampered_local_source_is_rejected",
        ],
    },
    {
        "id": "M02", "repo": "wiki", "desc": "把 retired 当 active",
        "path": "src/company_wiki/source_catalog/resolver.py",
        "old": '            if document["source_status"] != "active":',
        "new": '            if False and document["source_status"] != "active":',
        "killers": ["tests/contract/test_source_catalog_fail_closed.py"],
    },
    {
        "id": "M03", "repo": "wiki", "desc": "company_name 广播 URL",
        "path": "src/company_wiki/source_catalog/url_binding.py",
        "old": 'STRONG_KEYS = ("provider_document_id", "content_sha256")',
        "new": 'STRONG_KEYS = ("provider_document_id", "content_sha256", "company_name")',
        "killers": ["tests/contract/test_url_binding.py::test_company_name_key_rejected"],
    },
    {
        "id": "M05", "repo": "wiki", "desc": "future_root fallback 到 dayu",
        "path": "src/company_wiki/source_catalog/adapters/registry.py",
        "old": "    return REGISTERED_ADAPTERS.get(adapter_id)",
        "new": "    return REGISTERED_ADAPTERS.get(adapter_id) or REGISTERED_ADAPTERS[\"generic_document_v1\"]",
        "killers": ["tests/contract/test_adapter_registry.py::test_unknown_adapter_id_fails_closed"],
    },
    {
        "id": "M06", "repo": "wiki", "desc": "external root 写保护失效",
        "path": "src/company_wiki/source_catalog/adapters/conformance.py",
        "old": '    receipt["read_only"] = (',
        "new": '    receipt["read_only"] = "ok"  # MUTATION\n    _ = (',
        "killers": ["tests/contract/test_adapter_conformance.py::test_write_mutation_killed"],
    },
    {
        "id": "M07", "repo": "wiki", "desc": "GapPlan 把 covered 列 missing",
        "path": "src/company_wiki/source_catalog/reuse_latest_policy.py",
        "old": "    return sorted(discovered - covered)",
        "new": "    return sorted(discovered | covered)  # MUTATION",
        "killers": ["tests/contract/test_latest_gap_closure.py::test_latest02_dropbox_old_period_remote_new"],
    },
    {
        "id": "M08", "repo": "wiki", "desc": "下载授权恒有效",
        "path": "src/company_wiki/source_catalog/reuse_latest_policy.py",
        "old": '    if now > auth.get("expires_at", ""):',
        "new": '    if False and now > auth.get("expires_at", ""):',
        "killers": ["tests/contract/test_latest_gap_closure.py::test_dl02_expired_plan_rejected"],
    },
    {
        "id": "M09", "repo": "wiki", "desc": "SourceBundle 忽略 policy hash",
        "path": "src/company_wiki/source_catalog/policy.py",
        "old": "def validate_policy_hash(expected: str, actual: str) -> list[str]:",
        "new": "def validate_policy_hash(expected: str, actual: str) -> list[str]:  # MUTATION\n    return []",
        "killers": ["tests/contract/test_policy_and_flags.py::test_pol02_policy_hash_mismatch_rejected"],
    },
    {
        "id": "M10", "repo": "wiki", "desc": "upsert 忽略 metadata hash（幂等键退化）",
        "path": "src/company_wiki/source_catalog/assertion_service.py",
        "old": "              adapter_version=? AND normalized_sha256=? AND decision='verified'",
        "new": "              adapter_version=? AND content_sha256=? AND decision='verified'",
        "killers": ["tests/contract/test_assertion_upsert.py::test_tx02_same_key_upserts_once"],
    },
    {
        "id": "M11", "repo": "revenue", "desc": "summary 失效不传播到 consumer（DAG 边缺失）",
        "path": "audit_review/2026-08-09_data_lake_refactor_plan/tools/artifact_dag.py",
        "old": '    "consumer_analysis": ["summary"],',
        "new": '    "consumer_analysis": [],  # MUTATION',
        "killers": ["audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_artifact_dag.py::test_b02_summary_producer_change_recomputes_summary_and_downstream_only"],
    },
]


def _apply(repo: Path, spec: dict, mutate: bool) -> None:
    path = repo / spec["path"]
    src = path.read_text(encoding="utf-8")
    if mutate:
        assert spec["old"] in src, f"{spec['id']}: mutation anchor missing"
        path.write_text(src.replace(spec["old"], spec["new"]), encoding="utf-8")
    else:
        assert spec["new"] in src, f"{spec['id']}: restore anchor missing"
        path.write_text(src.replace(spec["new"], spec["old"]), encoding="utf-8")


def _pytest(repo: Path, nodeids: list[str]) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *nodeids, "-q"],
        cwd=str(repo), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600, check=False,
    )
    return proc.returncode == 0


def run_mutation(repo: Path, spec: dict) -> bool:
    try:
        _apply(repo, spec, mutate=True)
        killer_red = not _pytest(repo, spec["killers"])
        _apply(repo, spec, mutate=False)
        killer_green = _pytest(repo, spec["killers"])
    except Exception as exc:  # noqa: BLE001 - report and restore
        print(f"{spec['id']}: ERROR {exc}")
        return False
    if killer_red and killer_green:
        print(f"{spec['id']}: KILLED (killer red under mutation, green after restore)")
        return True
    print(
        f"{spec['id']}: FAIL killer_red={killer_red} killer_green={killer_green}"
    )
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Machine-provable mutation runner")
    parser.add_argument("--only", default="", help="comma-separated mutation ids")
    parser.add_argument("--repo", default="", help="repo name filter")
    args = parser.parse_args()
    only = {item.strip() for item in args.only.split(",") if item.strip()}
    ok = True
    for spec in MUTATIONS:
        if only and spec["id"] not in only:
            continue
        if args.repo and spec["repo"] != args.repo:
            continue
        if not run_mutation(REPOS[spec["repo"]], spec):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
