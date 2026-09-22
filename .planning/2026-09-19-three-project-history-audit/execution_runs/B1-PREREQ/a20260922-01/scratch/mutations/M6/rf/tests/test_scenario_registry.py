"""FC-102 RED/green: the scenario registry is the single test-semantics source.

Validates that ``compatibility/scenario_registry.json`` is internally
consistent and corresponds one-to-one with the 95 mandatory scenarios in
``scenario_matrix.md``: each declared tier is decomposed into an independent
tier entry, cross-process tiers require process_count >= 3 (no fake E2E),
and side-effect budgets are well-formed.

The hard "every mandatory ID is covered by a real cross-process test" gate
is a Phase-10 concern (FC-1003); FC-102 delivers this registry + integrity
validator. Mutation oracles prove the validator rejects the defects FC-102
forbids.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

COMPAT_DIR = Path(__file__).resolve().parents[1] / "compatibility"
sys.path.insert(0, str(COMPAT_DIR))

from scenario_registry import (  # noqa: E402
    EXPECTED_TOTAL,
    load,
    validate,
)

# The closed set of 95 mandatory IDs, derived from scenario_matrix.md.
# Hard-coded so the registry cannot silently drift from the matrix.
EXPECTED_IDS = (
    {f"EX-{i:02d}" for i in range(1, 9)}
    | {f"DBX-{i:02d}" for i in range(1, 9)}
    | {f"DL-{i:02d}" for i in range(1, 11)}
    | {f"LT-{i:02d}" for i in range(1, 11)}
    | {f"AR-{i:02d}" for i in range(1, 10)}
    | {f"SAFE-{i:02d}" for i in range(1, 8)}
    | {f"CTRL-{i:02d}" for i in range(1, 6)}
    | {f"OPS-{i:02d}" for i in range(1, 4)}
    | {f"PORT-{i:02d}" for i in range(1, 4)}
    | {f"IDX-{i:02d}" for i in range(1, 9)}
    | {f"UJ-{i:02d}" for i in range(1, 9)}
    | {f"AUD-{i:02d}" for i in range(1, 9)}
    | {f"MIG-{i:02d}" for i in range(1, 9)}
)


class ScenarioRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load()

    def test_expected_id_set_is_95(self) -> None:
        self.assertEqual(len(EXPECTED_IDS), EXPECTED_TOTAL)

    def test_registry_is_structurally_valid(self) -> None:
        problems = validate(self.data)
        self.assertEqual(problems, [], f"registry invalid: {problems}")

    def test_registry_ids_match_matrix_one_to_one(self) -> None:
        registry_ids = {s["id"] for s in self.data["scenarios"]}
        self.assertEqual(registry_ids, EXPECTED_IDS)

    def test_every_declared_tier_has_a_matching_tier_entry(self) -> None:
        for scen in self.data["scenarios"]:
            self.assertEqual(
                set(scen["tier_entries"]),
                set(scen["declared_tiers"]),
                f"{scen['id']}: tier_entries != declared_tiers",
            )

    def test_cross_process_tiers_require_three_processes(self) -> None:
        cross = {"T1", "T2", "T3", "T4"}
        for scen in self.data["scenarios"]:
            for tier, entry in scen["tier_entries"].items():
                if tier in cross:
                    self.assertGreaterEqual(
                        entry["process_count"], 3, f"{scen['id']}.{tier} fake E2E"
                    )
                else:
                    self.assertEqual(entry["process_count"], 1, f"{scen['id']}.{tier}")


class ScenarioRegistryMutationTests(unittest.TestCase):
    """Oracle: the validator must reject the defects FC-102 forbids."""

    def _base(self) -> dict:
        return copy.deepcopy(load())

    def test_rejects_duplicate_scenario_id(self) -> None:
        data = self._base()
        data["scenarios"].append(copy.deepcopy(data["scenarios"][0]))
        self.assertTrue(validate(data), "validator accepted a duplicate scenario id")

    def test_rejects_missing_tier_entry_for_a_declared_tier(self) -> None:
        data = self._base()
        scen = data["scenarios"][0]
        tier = scen["declared_tiers"][-1]
        del scen["tier_entries"][tier]
        self.assertTrue(validate(data), "validator accepted a declared tier with no entry")

    def test_rejects_extra_tier_entry_not_in_declared_tiers(self) -> None:
        data = self._base()
        scen = data["scenarios"][0]
        scen["tier_entries"]["T4"] = copy.deepcopy(scen["tier_entries"][scen["declared_tiers"][0]])
        self.assertTrue(validate(data), "validator accepted a tier entry not declared")

    def test_rejects_fake_e2e_with_process_count_below_three(self) -> None:
        data = self._base()
        for scen in data["scenarios"]:
            if "T1" in scen["declared_tiers"]:
                scen["tier_entries"]["T1"]["process_count"] = 1
                break
        self.assertTrue(
            validate(data),
            "validator accepted a cross-process tier claiming E2E with process_count<3",
        )

    def test_rejects_total_mandatory_drift(self) -> None:
        data = self._base()
        data["total_mandatory"] = 94
        self.assertTrue(validate(data), "validator accepted total_mandatory drift")

    def test_rejects_short_triplet_hash(self) -> None:
        data = self._base()
        data["frozen_at_triplet"]["revenue"] = "3ce9cc4"
        self.assertTrue(validate(data), "validator accepted a short triplet hash")


if __name__ == "__main__":
    unittest.main()
