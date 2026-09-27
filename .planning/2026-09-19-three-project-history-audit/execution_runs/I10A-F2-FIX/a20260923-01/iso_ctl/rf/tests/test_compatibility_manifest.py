"""FC-104 RED/green: compatibility manifest + frozen command registry.

Hard gates under test:

1. Registry tamper detection — contract/scenario/command sha256 in the
   manifest must equal the actual file hashes.
2. Baseline descendant invariant — each repo HEAD must be the frozen FCAP
   baseline or a descendant of it (sibling reset => RED).
3. Command registry structure — unique ids, valid owner/tier/argv/writes/
   network, honest observed states (ISO date or pending-first-measurement).

The frozen baseline triplet is hard-coded in the module and must never move.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

COMPAT_DIR = Path(__file__).resolve().parents[1] / "compatibility"
sys.path.insert(0, str(COMPAT_DIR))

from compatibility_manifest import (  # noqa: E402
    load_command_registry,
    load_manifest,
    validate_command_registry,
    validate_manifest,
)


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest()

    def test_manifest_is_structurally_valid(self) -> None:
        problems = validate_manifest(self.manifest)
        self.assertEqual(problems, [], f"manifest invalid: {problems}")

    def test_manifest_hashes_match_registry_files(self) -> None:
        import hashlib
        for key, name in (
            ("contract_registry_sha256", "contract_registry.json"),
            ("scenario_registry_sha256", "scenario_registry.json"),
            ("command_registry_sha256", "command_registry.json"),
        ):
            actual = hashlib.sha256((COMPAT_DIR / name).read_bytes()).hexdigest()
            self.assertEqual(self.manifest[key], actual, f"{key} drifted from {name}")

    def test_current_triplet_is_descendant_of_frozen_baseline(self) -> None:
        # The real gate: no repo may sit below the frozen baseline.
        problems = validate_manifest(self.manifest)
        self.assertEqual(problems, [])

    def test_contract_versions_match_contract_registry(self) -> None:
        registry = load_registry_json("contract_registry.json")
        for name, spec in registry["contracts"].items():
            self.assertEqual(
                self.manifest["contract_versions"][name],
                spec["version"],
                f"contract_versions.{name} drifted",
            )

    def test_command_registry_is_valid(self) -> None:
        problems = validate_command_registry(load_command_registry())
        self.assertEqual(problems, [], f"command registry invalid: {problems}")


def load_registry_json(name: str) -> dict:
    import json
    return json.loads((COMPAT_DIR / name).read_text(encoding="utf-8"))


class ManifestMutationTests(unittest.TestCase):
    """Oracle: the validator must reject tampering, drift, and bad structure."""

    def _base(self) -> dict:
        return copy.deepcopy(load_manifest())

    def test_rejects_tampered_contract_registry_hash(self) -> None:
        data = self._base()
        data["contract_registry_sha256"] = "f" * 64
        self.assertTrue(validate_manifest(data), "validator accepted tampered contract hash")

    def test_rejects_tampered_scenario_registry_hash(self) -> None:
        data = self._base()
        data["scenario_registry_sha256"] = "e" * 64
        self.assertTrue(validate_manifest(data), "validator accepted tampered scenario hash")

    def test_rejects_tampered_command_registry_hash(self) -> None:
        data = self._base()
        data["command_registry_sha256"] = "d" * 64
        self.assertTrue(validate_manifest(data), "validator accepted tampered command hash")

    def test_rejects_frozen_baseline_drift(self) -> None:
        data = self._base()
        data["frozen_baseline_triplet"]["revenue"] = "f" * 40
        self.assertTrue(validate_manifest(data), "validator accepted frozen-baseline drift")

    def test_rejects_short_current_triplet_hash(self) -> None:
        data = self._base()
        data["current_triplet"]["filing"] = "c9799b7"
        self.assertTrue(validate_manifest(data), "validator accepted a short current hash")

    def test_rejects_head_not_descendant_of_baseline(self) -> None:
        data = self._base()
        data["current_triplet"]["revenue"] = "a" * 40  # not a real commit on the line
        self.assertTrue(validate_manifest(data), "validator accepted a reset sibling")

    def test_rejects_contract_version_mismatch(self) -> None:
        data = self._base()
        data["contract_versions"]["RootPolicySnapshot"] = "9.9"
        self.assertTrue(validate_manifest(data), "validator accepted contract version drift")


class CommandRegistryMutationTests(unittest.TestCase):
    def _base(self) -> dict:
        return copy.deepcopy(load_command_registry())

    def test_rejects_duplicate_command_id(self) -> None:
        data = self._base()
        data["commands"].append(copy.deepcopy(data["commands"][0]))
        self.assertTrue(validate_command_registry(data), "validator accepted duplicate command id")

    def test_rejects_invalid_tier(self) -> None:
        data = self._base()
        data["commands"][0]["tier"] = "T9"
        self.assertTrue(validate_command_registry(data), "validator accepted invalid tier")

    def test_rejects_invalid_write_budget(self) -> None:
        data = self._base()
        data["commands"][0]["writes"] = ["production_catalog"]
        self.assertTrue(validate_command_registry(data), "validator accepted a production write budget")

    def test_rejects_missing_argv(self) -> None:
        data = self._base()
        data["commands"][0]["argv"] = []
        self.assertTrue(validate_command_registry(data), "validator accepted empty argv")

    def test_rejects_negative_collected_baseline(self) -> None:
        data = self._base()
        data["commands"][0]["expected_min_collected"] = -5
        self.assertTrue(validate_command_registry(data), "validator accepted negative collected baseline")

    def test_rejects_garbage_observed_field(self) -> None:
        data = self._base()
        data["commands"][0]["observed"] = "whenever"
        self.assertTrue(validate_command_registry(data), "validator accepted a fabricated observed value")

    def test_pending_first_measurement_is_honest(self) -> None:
        # wiki commands are legitimately unmeasured; they must say so, not fake a count.
        data = self._base()
        data["commands"][0]["observed"] = "pending-first-measurement"
        self.assertEqual(validate_command_registry(data), [])


if __name__ == "__main__":
    unittest.main()
