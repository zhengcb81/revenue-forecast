"""Version diagnostics and installer use one owned-byte runtime inventory."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from sync_installations import installable_files, manifest  # noqa: E402


@pytest.fixture
def packaged(tmp_path):
    root = tmp_path / "runtime"
    for source in installable_files(REPO):
        target = root / source.relative_to(REPO)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return root


def version(root):
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, "-B", str(root / "scripts/revenue_forecast.py"), "--version"],
        capture_output=True, encoding="utf-8", check=False, timeout=20, env=environment)
    assert result.returncode == 0, result.stderr
    return re.search(r"manifest_sha256=([0-9a-f]{16})", result.stdout).group(1)


def test_runtime_byte_change_updates_version_manifest(packaged):
    before = version(packaged)
    path = packaged / "scripts/model_registry.py"
    path.write_bytes(path.read_bytes() + b"\n# harmless runtime byte drift\n")
    assert version(packaged) != before


def test_runtime_hash_matches_installer_content_manifest(packaged):
    import hashlib
    payload = json.dumps(manifest(packaged), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    expected = hashlib.sha256(payload).hexdigest()[:16]
    assert version(packaged) == expected


def test_repository_outputs_and_caches_do_not_change_runtime_digest(packaged):
    before = version(packaged)
    for relative in ("output/data.json", "tools/check.py", "tests/replay.py", "scripts/__pycache__/x.pyc"):
        target = packaged / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"engineering residue")
    assert version(packaged) == before
    assert version(REPO) == before


def test_retired_shadow_queue_in_an_old_install_is_not_runtime_drift(packaged):
    before = version(packaged)
    stale = packaged / "scripts/processing_demand.py"
    stale.write_bytes(b"# retired engineering queue residue\n")
    assert version(packaged) == before
    assert "scripts/processing_demand.py" not in manifest(packaged)
    assert "tools/legacy/processing_demand.py" not in manifest(REPO)
