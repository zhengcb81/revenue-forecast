from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_registry import (  # noqa: E402
    MODEL_REGISTRY,
    ModelRegistryError,
    ModelSpec,
    build_registry,
)


def _calculator(base_revenue: float, drivers: dict[str, list[float]], years: list[int]) -> list[float]:
    del base_revenue, years
    return list(drivers["revenue"])


def _spec(model_id: str) -> ModelSpec:
    return ModelSpec(
        model_id=model_id,
        required=("revenue",),
        optional=(),
        defaults={},
        dimensions={"revenue": "revenue"},
        ratio_drivers=frozenset(),
        formula="revenue[t] = direct_revenue[t]",
        calculator=_calculator,
    )


class ModelRegistryContractTests(unittest.TestCase):
    def test_registry_is_read_only(self) -> None:
        with self.assertRaises(TypeError):
            MODEL_REGISTRY["mutated"] = _spec("mutated")  # type: ignore[index]

    def test_duplicate_model_registration_is_rejected(self) -> None:
        with self.assertRaisesRegex(ModelRegistryError, "duplicate revenue model"):
            build_registry([_spec("duplicate"), _spec("duplicate")])

    def test_every_model_has_complete_metadata_and_callable(self) -> None:
        self.assertGreaterEqual(len(MODEL_REGISTRY), 22)
        for model_id, spec in MODEL_REGISTRY.items():
            with self.subTest(model=model_id):
                self.assertEqual(model_id, spec.model_id)
                self.assertTrue(spec.formula)
                self.assertTrue(callable(spec.calculator))
                self.assertEqual(set(spec.dimensions), set(spec.required) | set(spec.optional))


if __name__ == "__main__":
    unittest.main()
