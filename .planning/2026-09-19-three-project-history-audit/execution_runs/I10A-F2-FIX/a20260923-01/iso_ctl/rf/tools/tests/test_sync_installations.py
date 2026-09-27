"""Installation synchronization and canonical-import contracts."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from sync_installations import (  # noqa: E402
    SKILL_NAME,
    import_installation,
    installation_diff,
    manifest,
    sync_installation,
    unique_destinations,
)


class SyncInstallationTests(unittest.TestCase):
    @staticmethod
    def _skill(root: Path, marker: str) -> Path:
        root.mkdir(parents=True)
        for name in (".gitignore", "CHANGELOG.md", "SKILL.md"):
            (root / name).write_text(f"{name}:{marker}\n", encoding="utf-8")
        for directory in ("agents", "config", "references", "scripts", "tests"):
            path = root / directory
            path.mkdir()
            (path / f"{directory}.txt").write_text(
                f"{directory}:{marker}\n", encoding="utf-8"
            )
        return root

    def test_manifest_includes_versioned_config(self) -> None:
        with TemporaryDirectory() as temporary:
            skill = self._skill(Path(temporary) / "skill", "one")
            result = manifest(skill)

        self.assertIn("config/config.txt", result)

    def test_installed_output_is_preserved_and_ignored_by_diff(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = self._skill(root / "canonical", "one")
            destination = root / "installed"
            target = self._skill(destination / SKILL_NAME, "old")
            output = target / "output"
            output.mkdir()
            artifact = output / "forecast.json"
            artifact.write_text('{"keep": true}\n', encoding="utf-8")
            expected_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()

            sync_installation(canonical, destination)

            self.assertEqual(
                hashlib.sha256(artifact.read_bytes()).hexdigest(), expected_hash
            )
            self.assertEqual(installation_diff(canonical, destination), [])

    def test_import_updates_installable_files_but_preserves_repo_tools(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self._skill(root / "source", "new")
            canonical = self._skill(root / "canonical", "old")
            tools = canonical / "tools"
            tools.mkdir()
            repository_only = tools / "keep.py"
            repository_only.write_text("KEEP = True\n", encoding="utf-8")

            import_installation(source, canonical)

            self.assertEqual(manifest(canonical), manifest(source))
            self.assertEqual(repository_only.read_text(encoding="utf-8"), "KEEP = True\n")

    def test_duplicate_destinations_are_applied_once(self) -> None:
        with TemporaryDirectory() as temporary:
            destination = Path(temporary) / "skills"
            destination.mkdir()
            result = unique_destinations([destination, destination / "."])

        self.assertEqual(result, [destination.resolve()])


if __name__ == "__main__":
    unittest.main()
