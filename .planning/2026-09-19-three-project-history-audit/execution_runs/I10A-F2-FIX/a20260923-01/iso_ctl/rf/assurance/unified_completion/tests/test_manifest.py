"""Manifest: build from frozen specs, offline re-verification, drift taxonomy."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from conftest import REPO_ROOT
from uc.manifest import ManifestError, build, verify


def _h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mtime(path: Path) -> str:
    from datetime import datetime

    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_repo(tmp_path: Path) -> Path:
    """Synthetic repo with the same three-spec shape as the real one."""
    repo = tmp_path / "repo"
    fcap = repo / "audit_review" / "2026-08-09_full_completion_assurance_plan"
    zijin = repo / "audit_review" / "2026-08-13_zijin_data_lake_remediation_plan"
    three = repo / "audit_review" / "2026-08-13_three_repo_completion_rebaseline_plan"

    fcap_a = fcap / "a.md"
    fcap_b = fcap / "b.md"
    _write(fcap_a, "A-content\n")
    _write(fcap_b, "B-content\n")
    z_files = [zijin / f"z{i}.md" for i in (1, 2, 3, 4)]
    for index, z_file in enumerate(z_files, start=1):
        _write(z_file, f"z{index}-content\n")
    c1 = three / "c1.md"
    c2 = three / "c2.md"
    _write(c1, "c1\n")
    _write(c2, "c2\n")
    zijin_manifest = zijin / "PLAN_MANIFEST.md"
    _write(zijin_manifest, "# zijin manifest fixture\n")

    snapshot = three / "input_snapshot.md"
    fcap_rows = "\n".join(
        f"| `{path.name}` | {path.stat().st_size} | `{_h(path)}` | {_mtime(path)} |"
        for path in (fcap_a, fcap_b)
    )
    zijin_rows = "\n".join(
        f"| `{path.name}` | {path.stat().st_size} | `{_h(path)}` | {_mtime(path)} |"
        for path in [zijin_manifest, *z_files]
    )
    _write(
        snapshot,
        "# snapshot\n"
        "## `2026-08-09_full_completion_assurance_plan`\n"
        "| file | bytes | sha | mtime |\n|---|---|---|---|\n"
        f"{fcap_rows}\n"
        "## `2026-08-13_zijin_data_lake_remediation_plan`\n"
        "| file | bytes | sha | mtime |\n|---|---|---|---|\n"
        f"{zijin_rows}\n",
    )

    plan_manifest = three / "PLAN_MANIFEST.md"
    content_rows = "\n".join(
        f"| `{path.name}` | {path.stat().st_size} | `{_h(path)}` |"
        for path in (snapshot, c1, c2)
    )
    annex_rows = "\n".join(
        f"| annex{i} | `{_h(path)}` | purpose |"
        for i, path in enumerate([*z_files, fcap_a], start=1)
    )
    _write(
        plan_manifest,
        "# plan manifest\n"
        "| 文件 | bytes | SHA-256 |\n|---|---|---|\n"
        f"{content_rows}\n"
        "| 内容 | 文件hash | 数量/用途 |\n|---|---|---|\n"
        f"{annex_rows}\n",
    )

    readme = repo / "audit_review" / "README.md"
    readme_rows = "\n".join(
        f"| spec{i} | {path.relative_to(repo).as_posix()} | `{_h(path)}` |"
        for i, path in enumerate([*z_files, fcap_a], start=1)
    )
    _write(
        readme,
        "# control\n"
        "## 13. frozen\n"
        "| 规范 | 精确路径 | SHA-256 |\n|---|---|---|\n"
        f"{readme_rows}\n",
    )
    return repo


def test_build_and_verify_clean(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    assert verify(repo, manifest) == []


def test_offline_verify_detects_hash_drift(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    victim = (
        repo / "audit_review" / "2026-08-09_full_completion_assurance_plan" / "a.md"
    )
    _write(victim, "tampered\n")
    problems = verify(repo, manifest)
    assert any("hash drift" in p and "a.md" in p for p in problems)


def test_offline_verify_detects_mtime_drift(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    victim = (
        repo / "audit_review" / "2026-08-13_zijin_data_lake_remediation_plan" / "z1.md"
    )
    stat = victim.stat()
    os.utime(victim, (stat.st_atime, stat.st_mtime + 120))
    problems = verify(repo, manifest)
    assert any("mtime drift" in p and "z1.md" in p for p in problems)


def test_verify_mtime_off_skips_mtime_but_keeps_hash(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    victim = (
        repo / "audit_review" / "2026-08-13_zijin_data_lake_remediation_plan" / "z1.md"
    )
    stat = victim.stat()
    os.utime(victim, (stat.st_atime, stat.st_mtime + 120))
    assert verify(repo, manifest, check_mtime=False) == []  # mtime-only drift passes
    _write(victim, "tampered\n")
    problems = verify(repo, manifest, check_mtime=False)
    assert any("hash drift" in p for p in problems)  # hash still enforced


def test_offline_verify_detects_size_drift(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    victim = (
        repo / "audit_review" / "2026-08-13_zijin_data_lake_remediation_plan" / "z2.md"
    )
    _write(victim, "much longer content than before\n")
    problems = verify(repo, manifest)
    assert any("size drift" in p and "z2.md" in p for p in problems)


def test_offline_verify_detects_spec_source_drift(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    snapshot = (
        repo
        / "audit_review"
        / "2026-08-13_three_repo_completion_rebaseline_plan"
        / "input_snapshot.md"
    )
    _write(snapshot, snapshot.read_text(encoding="utf-8") + "# edited after freeze\n")
    problems = verify(repo, manifest)
    assert any("spec source drift" in p and "input_snapshot.md" in p for p in problems)


def test_build_refuses_inconsistent_specs(tmp_path):
    repo = make_fixture_repo(tmp_path)
    snapshot = (
        repo
        / "audit_review"
        / "2026-08-13_three_repo_completion_rebaseline_plan"
        / "input_snapshot.md"
    )
    text = snapshot.read_text(encoding="utf-8")
    tampered = text.replace(
        _h(
            repo
            / "audit_review"
            / "2026-08-13_zijin_data_lake_remediation_plan"
            / "PLAN_MANIFEST.md"
        ),
        "0" * 64,
    )
    _write(snapshot, tampered)
    with pytest.raises(ManifestError, match="PLAN_MANIFEST"):
        build(repo, tmp_path / "m.json")


def test_build_refuses_ambiguous_annex_hash(tmp_path):
    repo = make_fixture_repo(tmp_path)
    readme = repo / "audit_review" / "README.md"
    z2 = repo / "audit_review" / "2026-08-13_zijin_data_lake_remediation_plan" / "z2.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        f"| spec2 | audit_review/2026-08-13_zijin_data_lake_remediation_plan/z2.md | `{_h(z2)}` |",
        "",
    )
    _write(readme, text)
    with pytest.raises(ManifestError, match="annex"):
        build(repo, tmp_path / "m.json")


def test_build_twice_refused_without_force(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    with pytest.raises(ManifestError, match="already exists"):
        build(repo, manifest)


def test_force_cas_replace(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest = tmp_path / "m.json"
    build(repo, manifest)
    old_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    new_hash = build(repo, manifest, force_sha256=old_hash)
    assert new_hash != old_hash
    assert verify(repo, manifest) == []


def test_real_repo_offline_reverification(tmp_path):
    """The CA-001 acceptance: every real frozen input re-verifies offline."""
    manifest = tmp_path / "real_manifest.json"
    build(REPO_ROOT, manifest)
    problems = verify(REPO_ROOT, manifest)
    assert problems == []
    payload = __import__("json").loads(manifest.read_text(encoding="utf-8"))
    assert len(payload["entries"]) == 44
    paths = {entry["rel_path"] for entry in payload["entries"]}
    assert "audit_review/README.md" not in paths  # control page tracked separately
    assert (
        "audit_review/2026-08-13_three_repo_completion_rebaseline_plan/"
        "completion_assurance_registry.md" in paths
    )
