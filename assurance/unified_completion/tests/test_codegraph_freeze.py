"""CA-003 codegraph freshness freeze: exclusive indexing, commit binding,
statistic equality, sentinel queries — exercised against scratch repos with
the real codegraph CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import uc.codegraph_freeze as cgf

CLI = cgf._cli_path()
pytestmark = pytest.mark.skipif(
    not CLI.is_file(), reason="codegraph CLI not installed at %s" % CLI
)

SENTINELS = {
    "absent": {
        "revenue": ["gone_symbol_rev"],
        "filing": ["gone_symbol_filing"],
        "wiki": ["gone_symbol_wiki"],
    },
    "present": {
        "revenue": ["must_exist_rev"],
        "filing": ["must_exist_filing"],
        "wiki": ["must_exist_wiki"],
    },
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=60,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo_setup(path: Path, func_name: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "fcap")
    _git(path, "config", "user.email", "t@e.c")
    _git(path, "config", "user.name", "t")
    _write(path / "mod.py", f"def {func_name}():\n    return 1\n")
    _git(path, "add", "mod.py")
    _git(path, "commit", "-m", "init")
    cgf._cg(["init", str(path)], timeout=300)


@pytest.fixture
def trio(tmp_path):
    root = tmp_path / "projects"
    revenue = root / "revenue-forecast"
    filing = root / "filing-fetch"
    wiki = root / "company-wiki"
    _repo_setup(revenue, "must_exist_rev")
    _repo_setup(filing, "must_exist_filing")
    _repo_setup(wiki, "must_exist_wiki")
    return revenue


def test_freeze_and_verify_roundtrip(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    assert cgf.verify(trio, out) == []
    payload = json.loads(out.read_text(encoding="utf-8"))
    for repo_name in ("revenue", "filing", "wiki"):
        rec = payload["repos"][repo_name]
        assert len(rec["indexed_commit"]) == 40
        assert rec["file_count"] >= 1
        assert rec["node_count"] >= 2


def test_commit_drift_detected(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    _git(trio, "commit", "--allow-empty", "-m", "advance")
    problems = cgf.verify(trio, out)
    assert any("indexed_commit" in p for p in problems)


def test_statistic_drift_detected(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    _write(trio / "extra.py", "def extra_function():\n    pass\n")
    cgf._cg(["index", "-q", str(trio)], timeout=600)  # re-index without freeze
    problems = cgf.verify(trio, out)
    assert any("statistic drift" in p for p in problems)


def test_deleted_symbol_reappearance_detected(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    _write(trio / "back.py", "def gone_symbol_rev():\n    pass\n")
    cgf._cg(["index", "-q", str(trio)], timeout=600)
    problems = cgf.verify(trio, out)
    assert any("deleted symbol 'gone_symbol_rev' present" in p for p in problems)


def test_core_symbol_missing_detected(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    (trio / "mod.py").write_text("def something_else():\n    pass\n", encoding="utf-8")
    cgf._cg(["index", "-q", str(trio)], timeout=600)
    problems = cgf.verify(trio, out)
    assert any("core symbol 'must_exist_rev' missing" in p for p in problems)


def test_exclusive_window_lock_refused(trio):
    lock = trio / ".codegraph" / "index.lock"
    _write(lock, "held")
    with pytest.raises(cgf.IndexLockError):
        cgf.index_repo(trio)
    lock.unlink()


def test_freeze_exclusive_and_cas(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    with pytest.raises(FileExistsError):
        cgf.freeze(trio, out, sentinels=SENTINELS)
    import hashlib

    current = hashlib.sha256(out.read_bytes()).hexdigest()
    cgf.freeze(trio, out, sentinels=SENTINELS, force_sha256=current)
    assert cgf.verify(trio, out) == []
