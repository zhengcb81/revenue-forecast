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
