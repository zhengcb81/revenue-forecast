"""WU-1402: targeted mutation gate — 12 high-risk mutations, each must have
a killer test.  The mapping is machine-checked: every mutation id resolves
to a test node id that is collectable and passing.

The 12 mutations are the plan's non-negotiable failure modes; automatic
mutation score is auxiliary.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOTS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}

MUTATIONS = [
    {"id": "M01", "desc": "删除 content hash 校验",
     "repo": "revenue", "killers": ["tests/test_company_wiki_source.py::RevenueSourceRecordTests::test_tampered_local_source_is_rejected"]},
    {"id": "M02", "desc": "把 retired 当 active",
     "repo": "wiki", "killers": ["tests/contract/test_source_catalog_fail_closed.py"]},
    {"id": "M03", "desc": "company_name 广播 URL",
     "repo": "wiki", "killers": ["tests/contract/test_url_binding.py"]},
    {"id": "M04", "desc": "resolver 恢复 acquisition/dayu_meta 分支",
     "repo": "wiki", "killers": ["tests/contract/test_adapter_spi.py::test_spi02_scanner_root_branch_freeze"]},
    {"id": "M05", "desc": "future_root fallback 到 dayu",
     "repo": "wiki", "killers": ["tests/contract/test_adapter_registry.py::test_unknown_adapter_id_fails_closed"]},
    {"id": "M06", "desc": "external root 写保护失效",
     "repo": "wiki", "killers": ["tests/contract/test_adapter_conformance.py::test_write_mutation_killed"]},
    {"id": "M07", "desc": "GapPlan 把 covered 列 missing",
     "repo": "revenue", "killers": ["audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_reuse_latest_policy.py::test_latest_covered_period_not_in_gap"]},
    {"id": "M08", "desc": "下载后省略 second resolve",
     "repo": "wiki", "killers": ["tests/contract/test_latest_gap_closure.py::test_dl01_no_authorization_no_download"]},
    {"id": "M09", "desc": "SourceBundle 忽略 policy hash",
     "repo": "wiki", "killers": ["tests/contract/test_policy_and_flags.py::test_pol02_policy_hash_mismatch_rejected"]},
    {"id": "M10", "desc": "artifact selector 忽略 producer version",
     "repo": "wiki", "killers": ["tests/contract/test_assertion_upsert.py::test_tx03_metadata_change_appends_new_assertion_keeps_old"]},
    {"id": "M11", "desc": "summary 失效扩大为重跑 parser",
     "repo": "revenue", "killers": ["audit_review/2026-08-09_data_lake_refactor_plan/tools/tests/test_artifact_dag.py::test_b02_summary_producer_change_recomputes_summary_and_downstream_only"]},
    {"id": "M12", "desc": "subprocess E2E 改直接 helper 调用",
     "repo": "revenue", "killers": ["tests/test_source_preparation.py::test_process_red01_uses_real_subprocess_chain"]},
]


def verify(repo_name: str, root: Path) -> list[str]:
    """Killer tests must be green AND actually kill their mutation: we
    execute each mutation (via the mutation's own script) and require the
    killer to turn red — a green-only gate can silently guard nothing."""
    problems: list[str] = []
    for mutation in MUTATIONS:
        if mutation["repo"] != repo_name:
            continue
        # 1) killer green in the clean tree
        for killer in mutation["killers"]:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", killer, "-q"],
                cwd=str(root), capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=600,
                check=False,
            )
            if proc.returncode != 0:
                problems.append(
                    f"{mutation['id']} killer {killer} not green: "
                    f"{proc.stdout.strip().splitlines()[-1][:120]}"
                )
    # 2) mutation actually kills: each mutation script must flip its killer
    for mutation in MUTATIONS:
        if mutation["repo"] != repo_name:
            continue
        script = root / "tools" / f"mutation_{mutation['id'].lower()}.py"
        if not script.is_file():
            problems.append(
                f"{mutation['id']}: no mutation script tools/mutation_"
                f"{mutation['id'].lower()}.py — kill not machine-provable"
            )
            continue
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600,
            check=False,
        )
        if "KILLED" not in proc.stdout:
            problems.append(
                f"{mutation['id']}: mutation script did not prove a kill: "
                f"{proc.stdout.strip()[:200]}"
            )
    return problems


def main() -> int:
    problems: list[str] = []
    for name, root in REPO_ROOTS.items():
        problems.extend(verify(name, root))
    for problem in problems:
        print(f"MUTATION-GATE: {problem}")
    if not problems:
        print(f"OK: {len(MUTATIONS)} targeted mutations all have green killers")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
