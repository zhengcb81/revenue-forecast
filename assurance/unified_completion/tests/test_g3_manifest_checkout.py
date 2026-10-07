"""G3-RF-ASSURANCE: manifest verification defaults to SHA+size, not mtime.

Covered here (each item maps to the G3 card's RED list):

  * a clean checkout re-verifies green — identical SHA and size with a
    different filesystem mtime is not drift;
  * mtime stays available as an explicit legacy strict check (and as a
    non-fatal diagnostic in the default mode);
  * same-size content swaps are still caught by the SHA-256 check;
  * missing inputs, path-escaping entries and a corrupt manifest itself
    fail non-zero and are never silently repaired by build/update;
  * every read entry point is read-only.

The real-repo E2E runs ``python -m uc.cli manifest-verify`` with
cwd=assurance/unified_completion against this clean worktree.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_manifest import make_fixture_repo

from uc.manifest import ManifestError, build, verify

REPO_ROOT = Path(__file__).resolve().parents[3]
UC_ROOT = Path(__file__).resolve().parents[1]


def _h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    return {
        path.relative_to(root).as_posix(): (
            path.stat().st_size,
            path.stat().st_mtime_ns,
            _h(path),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _age_every_file(root: Path, seconds: int = 600) -> None:
    """Simulate a fresh checkout: same bytes, different mtimes."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        stat = path.stat()
        os.utime(path, (stat.st_atime, stat.st_mtime + seconds))


# ---------------------------------------------------------------------------
# 1. clean checkout: same SHA+size, different mtime
# ---------------------------------------------------------------------------


def test_clean_checkout_same_sha_size_different_mtime_verifies(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)
    _age_every_file(repo)

    assert verify(repo, manifest_path) == []
    strict = verify(repo, manifest_path, check_mtime=True)
    assert any("mtime drift" in p for p in strict), strict
    # mtime never invalidates the hash/size result
    assert not any("hash drift" in p or "size drift" in p for p in strict)


def test_mtime_diagnostics_do_not_change_the_exit_semantics(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)
    _age_every_file(repo)

    from uc.manifest import mtime_diagnostics

    notes = mtime_diagnostics(repo, manifest_path)
    assert notes, "an mtime difference must still be visible as a diagnostic"
    assert all("mtime drift" in note for note in notes)
    assert verify(repo, manifest_path) == []


# ---------------------------------------------------------------------------
# 2. real input damage still fails
# ---------------------------------------------------------------------------


def test_same_size_byte_swap_is_caught_by_sha(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)

    victim = (
        repo / "audit_review" / "2026-08-09_full_completion_assurance_plan" / "a.md"
    )
    original_size = victim.stat().st_size
    _write(victim, "Z-content\n")  # same length as "A-content\n"
    assert victim.stat().st_size == original_size

    problems = verify(repo, manifest_path)
    assert any("hash drift" in p and "a.md" in p for p in problems), problems
    assert not any("size drift" in p for p in problems), problems
    assert not any("mtime drift" in p for p in problems), problems  # default = SHA+size


def test_missing_frozen_input_fails(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)
    victim = (
        repo / "audit_review" / "2026-08-09_full_completion_assurance_plan" / "b.md"
    )
    victim.unlink()
    problems = verify(repo, manifest_path)
    assert any("frozen input missing" in p and "b.md" in p for p in problems)


def test_path_escaping_entry_fails(tmp_path):
    """A manifest entry that points outside the repository root must fail
    even when the escaped file exists with the recorded hash and size."""
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)

    secret = tmp_path / "secret.md"
    _write(secret, "outside the repository\n")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["entries"].append(
        {
            "rel_path": os.path.join("..", "secret.md"),
            "sha256": _h(secret),
            "size": secret.stat().st_size,
            "mtime": None,
        }
    )
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    problems = verify(repo, manifest_path)
    assert problems, "an escaping path must not verify clean"
    assert any("escap" in p for p in problems), problems


def test_missing_manifest_fails_cleanly(tmp_path):
    repo = make_fixture_repo(tmp_path)
    with pytest.raises(ManifestError):
        verify(repo, tmp_path / "absent.json")


def test_corrupt_manifest_is_reported_and_never_repaired(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)
    manifest_path.write_text("{ this is not json", encoding="utf-8")
    damaged = manifest_path.read_bytes()

    with pytest.raises(ManifestError):
        verify(repo, manifest_path)
    assert manifest_path.read_bytes() == damaged  # read-only, no build/update


# ---------------------------------------------------------------------------
# 3. read entry points never write
# ---------------------------------------------------------------------------


def test_verify_is_read_only(tmp_path):
    repo = make_fixture_repo(tmp_path)
    manifest_path = tmp_path / "m.json"
    build(repo, manifest_path)
    before_repo = _snapshot(repo)
    before_manifest = _snapshot(tmp_path)

    assert verify(repo, manifest_path) == []
    verify(repo, manifest_path, check_mtime=True)

    assert _snapshot(repo) == before_repo
    assert _snapshot(tmp_path) == before_manifest


# ---------------------------------------------------------------------------
# 4. E2E: the real repo in this clean worktree
# ---------------------------------------------------------------------------


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "uc.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        cwd=str(UC_ROOT),
    )


def test_real_repo_manifest_verify_default_is_green_in_clean_checkout():
    before = _snapshot(REPO_ROOT / "audit_review")
    proc = _run_cli("manifest-verify")
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-500:]
    assert "OK" in out, out[-500:]
    assert _snapshot(REPO_ROOT / "audit_review") == before


def test_real_repo_mtime_strict_is_the_explicit_legacy_opt_in():
    proc = _run_cli("manifest-verify", "--mtime", "strict")
    out = proc.stdout + proc.stderr
    # in a fresh worktree the checkout mtimes differ, so strict is red —
    # which is exactly why it is no longer the default
    assert proc.returncode == 1, out[-500:]
    assert "mtime drift" in out, out[-500:]
    assert "hash drift" not in out, out[-500:]


def test_scratch_same_size_swap_fails_without_touching_historical_specs(tmp_path):
    """Copy one frozen input into scratch, swap same-size bytes there, and
    prove verification fails — the repository's own spec tables stay
    untouched (this test only writes inside tmp_path)."""
    source = (
        REPO_ROOT
        / "audit_review"
        / "2026-08-09_full_completion_assurance_plan"
        / "architecture_target.md"
    )
    specs_before = _h(REPO_ROOT / "audit_review" / "README.md")

    scratch = tmp_path / "repo"
    target = scratch / "audit_review" / "2026-08-09_full_completion_assurance_plan"
    target.mkdir(parents=True)
    victim = target / "architecture_target.md"
    original = source.read_bytes()
    victim.write_bytes(original)
    swapped = bytearray(original)
    swapped[-2] = swapped[-2] ^ 0x01  # same size, different bytes
    victim.write_bytes(bytes(swapped))
    assert victim.stat().st_size == len(original)

    manifest_path = tmp_path / "m.json"
    payload = {
        "schema_version": 1,
        "built_at_utc": "2026-01-01T00:00:00+00:00",
        "repo_root": str(scratch),
        "control_page_sha256": "",
        "sources": [],
        "entries": [
            {
                "rel_path": "audit_review/2026-08-09_full_completion_assurance_plan/"
                "architecture_target.md",
                "sha256": hashlib.sha256(original).hexdigest(),
                "size": len(original),
                "mtime": None,
            }
        ],
    }
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    problems = verify(scratch, manifest_path)
    assert any("hash drift" in p for p in problems), problems
    # the historical specs in the repository are untouched
    assert _h(REPO_ROOT / "audit_review" / "README.md") == specs_before


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
