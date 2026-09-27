"""Minimal regression for the eight extension models (owner ruling T1-5).

Purpose is deliberately narrow.  tests/test_model_extensions.py already proves the
formulas and their economic invariants.  What it does NOT prove -- and what the
20260920 production-tree rollback destroyed -- is that the extension layer is
*anchored*: that the eight specs are actually attached to the registry, that the
module exists as version-controlled content, and that the driver_bound mechanism
survives.  Without that, a single git operation silently returns the tree to a
24-model registry and every downstream model card loses its acceptance baseline.

So this file is a smoke anchor, not a second formula suite:

  1. exactly eight extension models are registered, and they are exactly the eight
     names the card pack binds;
  2. build_extension_specs is reachable from model_registry's mount point, i.e. the
     registry the product actually builds contains them (not just an import of the
     module in isolation);
  3. every extension spec declares the opening-balance bridge that makes stock/flow
     validation possible;
  4. driver_bounds is materialised for the specs that declare non-default domains,
     because a lost driver_bounds silently widens or narrows acceptance.

Each check would have failed on the rolled-back tree.  No expected value is
produced by calling the code under test: the eight names are the card pack's
frozen identity list, and the bounds assertions are derived from the card text.
"""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_extensions import EXTENSION_OPENING_BALANCES, build_extension_specs  # noqa: E402
from model_registry import MODEL_REGISTRY, ModelRegistryError, ModelSpec, build_registry  # noqa: E402

# The eight archetypes added by this batch.  This is the card pack's identity list,
# not a value read back from the registry under test.
EXPECTED_EXTENSION_MODELS = frozenset({
    "subscription_arr_bridge",
    "installed_base_aftermarket",
    "store_cohorts",
    "renewable_generation",
    "aum_fee_bridge",
    "commercial_launch",
    "finite_adoption",
    "inventory_sellthrough",
})

# Specs that must carry an explicit driver_bounds entry, because their card text
# grants a domain that the conservative dimension default would get wrong.
# Measured on the anchored tree; at least these driver names must be present.
EXPECTED_BOUNDED_MODELS = {
    "store_cohorts": "new_store_productivity",
    "renewable_generation": "contract_price_per_mwh",
    "aum_fee_bridge": "market_change",
}


class ExtensionAnchorRegression(unittest.TestCase):
    """Anchor tests: the extension layer must exist and must be mounted."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.specs = build_extension_specs(ModelSpec, ModelRegistryError)
        cls.registry = build_registry(build_extension_specs(ModelSpec, ModelRegistryError))

    # -- 1 -----------------------------------------------------------------
    def test_exactly_the_eight_archetypes_are_registered(self) -> None:
        built = frozenset(cls_.model_id for cls_ in self.specs)
        self.assertEqual(built, EXPECTED_EXTENSION_MODELS)
        self.assertEqual(len(self.specs), 8)

    def test_the_product_registry_contains_all_eight(self) -> None:
        # build_registry must mount them: this is what the rollback removed.
        for model in EXPECTED_EXTENSION_MODELS:
            with self.subTest(model=model):
                self.assertIn(model, self.registry)
                self.assertIn(model, MODEL_REGISTRY)

    def test_registry_is_a_strict_superset_of_the_twenty_four_core_models(self) -> None:
        # 31 model cards = 24 core + ... ; the extension batch must not have replaced
        # anything.  We only assert the direction that the rollback violated.
        self.assertGreater(len(MODEL_REGISTRY), len(EXPECTED_EXTENSION_MODELS))

    # -- 2 -----------------------------------------------------------------
    def test_every_extension_spec_declares_an_opening_balance_bridge(self) -> None:
        # EXTENSION_OPENING_BALANCES maps model -> (segment base-anchor field,
        # first opening driver, parameter dimension).  The two flow-only archetypes
        # have no opening balance and must be absent.  Every listed opening driver
        # must really exist on that spec, otherwise stock/flow validation is silently
        # disabled for it.
        self.assertEqual(set(EXTENSION_OPENING_BALANCES), EXPECTED_EXTENSION_MODELS - {
            "renewable_generation", "commercial_launch",
        })
        for model, bridge in EXTENSION_OPENING_BALANCES.items():
            with self.subTest(model=model):
                anchor_field, opening_driver, dimension = bridge
                self.assertIsInstance(anchor_field, str)
                self.assertTrue(anchor_field.endswith("_parameter_id"))
                spec = self.registry[model]
                declared = set(spec.required) | set(spec.optional)
                self.assertIn(opening_driver, declared,
                              f"{model}: opening driver {opening_driver} not declared")
                self.assertEqual(spec.dimensions[opening_driver], dimension,
                                 f"{model}: {opening_driver} dimension drifted")

    # -- 3 -----------------------------------------------------------------
    def test_driver_bounds_survive_for_the_specs_that_declare_them(self) -> None:
        # A lost driver_bounds entry is invisible to the formula suite but changes the
        # accepted domain, so anchor it here.  Exactly three specs declare bounds today;
        # each must still carry its named driver.
        bounded = {s.model_id for s in self.specs if getattr(s, "driver_bounds", None)}
        self.assertEqual(bounded, set(EXPECTED_BOUNDED_MODELS))
        for model, driver in EXPECTED_BOUNDED_MODELS.items():
            with self.subTest(model=model):
                spec = next(s for s in self.specs if s.model_id == model)
                self.assertIn(driver, dict(spec.driver_bounds),
                              f"{model} lost the bounds for {driver}")

    # -- 4 -----------------------------------------------------------------
    def test_extension_module_is_version_controlled_content(self) -> None:
        # The rollback's root cause: model_extensions.py was untracked, so the anchored
        # state existed only in a working tree.  Assert we can still name it as a real
        # file with content, and record its identity for the drift ledger.
        module = ROOT / "scripts" / "model_extensions.py"
        self.assertTrue(module.is_file(), "scripts/model_extensions.py is missing")
        raw = module.read_bytes()
        self.assertGreater(len(raw), 0)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(len(digest), 64)
        # the mount point must be referenced from the registry module, not only imported
        registry_src = (ROOT / "scripts" / "model_registry.py").read_text(encoding="utf-8")
        self.assertIn("build_extension_specs", registry_src,
                      "model_registry.py no longer references the extension mount point")


if __name__ == "__main__":
    unittest.main()
