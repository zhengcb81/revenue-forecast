"""ZR-102 (phase C) gate tests for the T1 hermetic three-process runner.

Covers the runbook gates:

(a) the runner's guard refuses real paths (no subprocess needed);
(b) scenarios 1, 4, 6 end-to-end via subprocess (pytest timeouts keep each
    under ~3 minutes);
(c) the runner never modifies anything outside its temp work-dir — the real
    company-wiki ``.source_catalog`` file list and the three repo working
    trees (git status --porcelain) are fingerprinted before/after and must
    be unchanged, EXCLUDING the pre-existing dirty files
    ``.claude/settings.local.json``, ``llm_cost_log.csv``, ``.coverage`` and
    ``coverage.json``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

T1 = Path(__file__).resolve().parents[1] / "t1"
sys.path.insert(0, str(T1))

import zr102_t1_runner as runner  # noqa: E402  (path bootstrap above)

RUNNER = T1 / "zr102_t1_runner.py"
PY = sys.executable

# Pre-existing dirty files that are allowed to change across a run
# (excluded from the git-status before/after comparison).
_EXCLUDED_DIRTY = {
    ".claude/settings.local.json",
    "llm_cost_log.csv",
    ".coverage",
    "coverage.json",
}

# Real repo working trees fingerprinted by the modification gate.
_GIT_REPOS = [
    runner.REVENUE_ROOT,
    runner.WIKI_ROOT,
    runner.FILING_ROOT,
]
_REAL_CATALOG = runner.WIKI_ROOT / ".source_catalog"


# ---------------------------------------------------------------------------
# (a) guard unit checks (no subprocess)
# ---------------------------------------------------------------------------


def _run_runner(args, *, cwd=None, timeout=600):
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [PY, "-B", str(RUNNER), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        cwd=cwd,
        env=env,
        check=False,
    )


def test_guard_refuses_real_company_wiki_root(tmp_path):
    violations = runner.validate_hermetic(
        tmp_path,
        {"company_wiki_root": runner.WIKI_ROOT},
    )
    assert violations, "real company-wiki root must be refused"
    assert "escapes the temp work dir" in violations[0]
    assert str(runner.WIKI_ROOT) in violations[0]


def test_guard_refuses_real_filing_fetch_root(tmp_path):
    violations = runner.validate_hermetic(
        tmp_path,
        {"filing_fetch_root": runner.FILING_ROOT},
    )
    assert violations
    assert str(runner.FILING_ROOT) in violations[0]


def test_guard_refuses_real_catalog_dropbox_dayu(tmp_path):
    violations = runner.validate_hermetic(
        tmp_path,
        {
            "catalog_dir": runner.WIKI_ROOT / ".source_catalog",
            "root_dropbox_stock": runner.REAL_DROPBOX / "Stock",
            "root_dayu_portfolio": runner.REAL_DAYU_AGENT / "workspace" / "portfolio",
        },
    )
    assert len(violations) == 3


def test_guard_accepts_temp_paths(tmp_path):
    work = tmp_path / "work"
    (work / "wiki" / "companies").mkdir(parents=True)
    (work / "filing-fetch").mkdir(parents=True)
    violations = runner.validate_hermetic(
        work,
        runner.collect_config_paths(work),
    )
    assert violations == [], violations


# ---------------------------------------------------------------------------
# (b) scenario end-to-end via subprocess
# ---------------------------------------------------------------------------


@pytest.mark.timeout(240)
def test_scenario_1_e2e(tmp_path):
    work = tmp_path / "s1"
    proc = _run_runner(
        ["--scenario", "1", "--work-dir", str(work), "--timeout-seconds", "180"]
    )
    assert proc.returncode == 0, proc.stderr[-1500:] + proc.stdout[-1500:]
    summaries = json.loads(proc.stdout)
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary["scenario"] == 1
    assert summary["outcome"] == "PASS"
    assert summary["download_calls"] == 0
    assert summary["llm_calls"] == 0
    assert len(summary["pids"]) == 3
    assert len(set(summary["pids"])) == 3
    assert summary["details"]["reuse_receipt"]["outcome"] == "reused_existing"


@pytest.mark.timeout(240)
def test_scenario_4_e2e(tmp_path):
    work = tmp_path / "s4"
    proc = _run_runner(
        ["--scenario", "4", "--work-dir", str(work), "--timeout-seconds", "180"]
    )
    assert proc.returncode == 0, proc.stderr[-1500:] + proc.stdout[-1500:]
    summaries = json.loads(proc.stdout)
    summary = summaries[0]
    assert summary["scenario"] == 4
    assert summary["outcome"] == "PASS"
    assert summary["chain_exit"] != 0
    assert summary["provider_invocations"] == 0
    assert "not_found" in summary["details"]["stderr_tail"]


@pytest.mark.timeout(90)
def test_scenario_6_e2e(tmp_path):
    work = tmp_path / "s6"
    proc = _run_runner(["--scenario", "6", "--work-dir", str(work)])
    assert proc.returncode == 2, (proc.returncode, proc.stderr[-1000:])
    assert "escapes the temp work dir" in proc.stdout
    payload = json.loads(proc.stdout)
    assert payload["scenario"] == 6
    assert payload["outcome"] == "GUARD_REFUSED"


@pytest.mark.timeout(480)
def test_scenarios_2_and_3_e2e(tmp_path):
    """AUTHORIZED-DOWNLOAD then SECOND-RUN IDEMPOTENCE share one work dir:
    the provider download count must stay at 1 across both runs."""
    work = tmp_path / "s2"
    proc = _run_runner(
        ["--scenario", "2,3", "--work-dir", str(work), "--timeout-seconds", "240"]
    )
    assert proc.returncode == 0, proc.stderr[-2000:] + proc.stdout[-2000:]
    summaries = json.loads(proc.stdout)
    by_scenario = {item["scenario"]: item for item in summaries}
    s2, s3 = by_scenario[2], by_scenario[3]
    assert s2["outcome"] == "PASS"
    assert s3["outcome"] == "PASS"
    assert s2["download_calls"] == 1
    assert s2["details"]["envelope"]["download_events"] == 1
    assert s3["download_calls"] == 0
    assert s3["provider_fetch"] == 1
    assert s3["details"]["before_spy_fetch"] == 1
    assert s3["details"]["after_spy_fetch"] == 1


# ---------------------------------------------------------------------------
# (c) nothing outside the temp work-dir was modified
# ---------------------------------------------------------------------------


def _git_status(repo: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=60,
        check=False,
    )
    return (proc.stdout or "").splitlines()


def _catalog_file_list() -> list[str]:
    if not _REAL_CATALOG.is_dir():
        return []
    return sorted(
        str(p.relative_to(_REAL_CATALOG)).replace("\\", "/")
        for p in _REAL_CATALOG.rglob("*")
        if p.is_file()
    )


def _fingerprint() -> dict:
    return {
        "git": {str(repo): _git_status(repo) for repo in _GIT_REPOS},
        "catalog": _catalog_file_list(),
    }


def _assert_no_external_modification(before: dict, after: dict) -> None:
    for repo in _GIT_REPOS:
        key = str(repo)
        changed = set(after["git"][key]) - set(before["git"][key])
        changed = {
            line
            for line in changed
            if not any(excluded in line for excluded in _EXCLUDED_DIRTY)
        }
        assert changed == set(), (
            f"git working tree changed outside the temp work dir: {repo} -> {sorted(changed)}"
        )
    catalog_added = set(after["catalog"]) - set(before["catalog"])
    catalog_removed = set(before["catalog"]) - set(after["catalog"])
    assert not catalog_added and not catalog_removed, (
        f"real .source_catalog changed: added={sorted(catalog_added)} "
        f"removed={sorted(catalog_removed)}"
    )


@pytest.mark.timeout(300)
def test_no_external_modification(tmp_path):
    before = _fingerprint()
    work = tmp_path / "mod"
    proc = _run_runner(
        ["--scenario", "1", "--work-dir", str(work), "--timeout-seconds", "180"]
    )
    assert proc.returncode == 0, proc.stderr[-1500:]
    after = _fingerprint()
    _assert_no_external_modification(before, after)
