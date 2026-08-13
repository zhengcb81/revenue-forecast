"""CA-002 environment freeze: exact-equality gate, push-state classification,
infra-error classification, and drift detection per field."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

import pytest

import uc.envfreeze as ef


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


def _make_repo(path: Path, commit_msg: str = "init") -> str:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "fcap")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "tester")
    (path / "f.txt").write_text(commit_msg, encoding="utf-8")
    _git(path, "add", "f.txt")
    _git(path, "commit", "-m", commit_msg)
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    ).stdout.strip()


@pytest.fixture
def trio(tmp_path, monkeypatch):
    """Root layout mirroring the real sibling repos."""
    root = tmp_path / "projects"
    revenue = root / "revenue-forecast"
    filing = root / "filing-fetch"
    wiki = root / "company-wiki"
    for repo in (revenue, filing, wiki):
        _make_repo(repo)
        _git(repo, "remote", "add", "origin", f"https://example.com/{repo.name}.git")
        (repo / "config").mkdir(exist_ok=True)
        (repo / "config" / "app.json").write_text(
            json.dumps({"repo": repo.name}), encoding="utf-8"
        )
    monkeypatch.setattr(ef, "SKILLS_DIR", tmp_path / "skills")
    return revenue


def _collect(root: Path, **overrides) -> dict:
    return ef.collect(root, remote_lookup=lambda url, branch: "0" * 40, **overrides)


def test_freeze_verify_roundtrip(trio, tmp_path):
    frozen = _collect(trio)
    out = tmp_path / "env.json"
    ef.freeze(trio, out, remote_lookup=lambda url, branch: "0" * 40)
    stored = json.loads(out.read_text(encoding="utf-8"))
    assert ef.verify(stored, _collect(trio)) == []
    assert stored["repos"]["revenue"]["head"] == frozen["repos"]["revenue"]["head"]


def test_head_change_is_drift_even_if_ancestor(trio):
    """Exact equality, not ancestry: moving HEAD backwards must drift."""
    frozen = _collect(trio)
    head = frozen["repos"]["revenue"]["head"]
    _git(trio, "commit", "--allow-empty", "-m", "child")
    live = _collect(trio)
    assert ef.verify(frozen, live) != []  # child commit -> drift
    _git(trio, "reset", "--hard", head)
    live_back = _collect(trio)
    assert ef.verify(frozen, live_back) == []  # exact HEAD restored -> clean


def test_dirty_allowlist_drift(trio):
    frozen = _collect(trio)
    (trio / "untracked.txt").write_text("x", encoding="utf-8")
    live = _collect(trio)
    problems = ef.verify(frozen, live)
    assert any("repos" in p for p in problems)


def test_porcelain_leading_space_status_preserved(trio):
    """Reviewer F1 regression: `git status --porcelain` lines for tracked
    modifications start with a space (' M path'); the parser must preserve
    the status column and the full path."""
    (trio / "f.txt").write_text("modified", encoding="utf-8")
    live = _collect(trio)
    entries = live["repos"]["revenue"]["dirty"]
    modified = [e for e in entries if e["path"].endswith("f.txt")]
    assert modified, f"expected dirty entry for f.txt in {entries}"
    assert modified[0]["status"] == " M"
    assert modified[0]["path"] == "f.txt"


def test_dirty_ignore_excludes_own_artifact_dir(trio):
    """The freeze artifact's own directory must be excludable from the dirty
    allowlist; the ignore list itself is frozen data."""
    (trio / "assurance" / "unified_completion" / "environment").mkdir(parents=True)
    (
        trio / "assurance" / "unified_completion" / "environment" / "env_freeze.json"
    ).write_text("{}", encoding="utf-8")
    live = _collect(trio, dirty_ignore=["assurance/unified_completion/environment/"])
    revenue_dirty = [e["path"] for e in live["repos"]["revenue"]["dirty"]]
    assert "assurance/unified_completion/environment/" not in revenue_dirty
    assert live["dirty_ignore"] == ["assurance/unified_completion/environment/"]


def test_branch_and_upstream_drift(trio):
    frozen = _collect(trio)
    live = _collect(trio)
    live["repos"]["revenue"]["branch"] = "master"
    assert ef.verify(frozen, live) != []
    live2 = _collect(trio)
    live2["repos"]["revenue"]["upstream"] = "origin/fcap"
    assert ef.verify(frozen, live2) != []


def test_toolchain_and_skills_and_config_drift(trio):
    frozen = _collect(trio)
    live = _collect(trio)
    live["toolchain"]["python"] = "Python 2.7"
    live["skills"]["__nonexistent__"] = "absent"
    live["configs"]["revenue"]["config/app.json"] = "0" * 64
    problems = ef.verify(frozen, live)
    assert len(problems) >= 3


def test_catalog_fingerprint_drift(trio):
    frozen = _collect(trio)
    live = _collect(trio)
    live["catalog"]["note"] = "tampered"
    assert ef.verify(frozen, live) != []


def test_push_state_classification(trio):
    """pushed / local_only / unverifiable via injected remote lookups."""
    frozen = _collect(trio)
    head = frozen["repos"]["revenue"]["head"]
    assert frozen["repos"]["revenue"]["push_state"] == "local_only"  # fake remote sha

    live = ef.collect(trio, remote_lookup=lambda url, branch: head)
    assert live["repos"]["revenue"]["push_state"] == "pushed"
    assert live["repos"]["revenue"]["remote_ref_sha"] == head

    def unreachable(url, branch):
        raise ef.InfraError("network down", "remote-unreachable")

    live2 = ef.collect(trio, remote_lookup=unreachable)
    assert live2["repos"]["revenue"]["push_state"] == "unverifiable"


def test_infra_error_classification_not_fake_upstream(trio, monkeypatch):
    """Git dubious-ownership must be recorded as infra_error, never as an
    ancestry/upstream mismatch."""

    def failing_git(repo, args):
        raise ef.InfraError(
            "fatal: detected dubious ownership in repository", "git-unsafe-directory"
        )

    monkeypatch.setattr(ef, "_run_git", failing_git)
    live = ef.collect(trio, remote_lookup=lambda url, branch: "0" * 40)
    assert live["repos"]["revenue"]["infra_error"] == "git-unsafe-directory"
    assert any(item["kind"] == "git-unsafe-directory" for item in live["infra_errors"])


def test_freeze_exclusive_and_cas(trio, tmp_path):
    out = tmp_path / "env.json"
    ef.freeze(trio, out, remote_lookup=lambda url, branch: "0" * 40)
    with pytest.raises(FileExistsError):
        ef.freeze(trio, out, remote_lookup=lambda url, branch: "0" * 40)
    import hashlib

    current = hashlib.sha256(out.read_bytes()).hexdigest()
    ef.freeze(
        trio, out, force_sha256=current, remote_lookup=lambda url, branch: "0" * 40
    )
    stored = json.loads(out.read_text(encoding="utf-8"))
    assert ef.verify(stored, _collect(trio)) == []


def test_catalog_fingerprint_is_zero_write(trio, tmp_path):
    """Read-only fingerprint must not modify the catalog (size/mtime stable)."""
    db = tmp_path / "catalog.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO docs VALUES (1, 'a')")
    conn.commit()
    conn.close()
    before = db.stat()
    facts = ef._catalog_facts(db)
    after = db.stat()
    assert facts["available"] is True
    assert facts["schema_objects"] >= 1
    assert (before.st_size, before.st_mtime) == (after.st_size, after.st_mtime)


def test_runtime_policy_facts(trio):
    wiki = trio.parent / "company-wiki"
    policy_dir = wiki / ".source_catalog"
    policy_dir.mkdir(exist_ok=True)
    (policy_dir / "runtime_policy.json").write_text('{"x": 1}', encoding="utf-8")
    live = _collect(trio)
    assert live["runtime_policy"]["available"] is True
    assert len(live["runtime_policy"]["sha256"]) == 64
