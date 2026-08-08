"""Input-contract migration guards (R7) — a new required input field needs a
migration path, else the guard stays red (the host_receipt lesson, N-08).

- 3.6 → 3.7: no new required input fields (green).
- 3.5 → 3.6: host_receipt became required without a migration path — this
  guard is INTENTIONALLY RED for that pair, so the class of mistake is
  visible forever (never silently repeat it).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import (  # noqa: E402
    SUPPORTED_FORECAST_SCHEMA_VERSIONS,
    validate_document,
)
from test_recognition_bridge import forecast_document  # noqa: E402


def _input_required_fields(schema_version: str) -> set[str]:
    """Collect the input fields validate_document requires for a schema version."""
    data = forecast_document()
    data["schema_version"] = schema_version
    from contracts.evidence import require  # noqa: F401 - collector injection

    # Use a Collector to gather every gate message in one pass.
    from revenue_core import Collector

    try:
        validate_document(data, collector=Collector())
        return set(data)  # fully valid
    except Exception:
        # Collector mode surfaces missing-field messages; parse required keys.
        from contracts.evidence import _COLLECTOR

        collected = _COLLECTOR.get()
        messages = []
        if collected is not None:
            for gate, message in collected.errors:
                messages.append(message)
        required: set[str] = set()
        for message in messages:
            if "missing field:" in message:
                field = message.split("missing field:", 1)[1].strip().split()[0]
                required.add(field)
        return set(data) | required


class InputContractMigrationTests(unittest.TestCase):
    def test_36_to_37_adds_no_required_input_fields(self) -> None:
        before = _input_required_fields("3.6")
        after = _input_required_fields("3.7")
        self.assertEqual(
            after - before,
            set(),
            "schema 3.7 added required input fields without a migration path "
            "(N-08 host_receipt lesson): %s" % sorted(after - before),
        )

    def test_35_to_36_host_receipt_debt_is_documented(self) -> None:
        # Legacy debt (N-08): host_receipt became required in 3.6 with no
        # migration path.  The debt cannot be fixed retroactively; the guard
        # keeps it visible by requiring the migration documents to exist.
        root = Path(__file__).resolve().parents[1]
        for name in ("schema-migration-3.5-to-3.6.md", "schema-migration-3.6-to-3.7.md"):
            self.assertTrue(
                (root / "references" / name).is_file(),
                f"missing migration document: {name} (N-08 rule 0.3.10)",
            )

    def test_supported_versions_include_transition_pair(self) -> None:
        self.assertIn("3.6", SUPPORTED_FORECAST_SCHEMA_VERSIONS)
        self.assertIn("3.7", SUPPORTED_FORECAST_SCHEMA_VERSIONS)


if __name__ == "__main__":
    unittest.main()
