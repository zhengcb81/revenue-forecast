"""Publication registry (R1.2) — append-only, tamper-evident, fail-closed."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from publication_registry import (  # noqa: E402
    RegistryError,
    audit,
    is_registered,
    lookup,
    register_publication,
)
from revenue_core import (  # noqa: E402
    ForecastInputError,
    canonical_sha256,
    run_forecast,
)
from test_recognition_bridge import forecast_document  # noqa: E402


class PublicationRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._previous = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
        self._temporary = tempfile.TemporaryDirectory()
        os.environ["REVENUE_PUBLICATION_REGISTRY"] = self._temporary.name

    def tearDown(self) -> None:
        os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
        if self._previous is not None:
            os.environ["REVENUE_PUBLICATION_REGISTRY"] = self._previous
        self._temporary.cleanup()

    def test_formal_run_forecast_registers_the_publication(self) -> None:
        result = run_forecast(forecast_document())
        history = lookup(result["input_sha256"])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["result_sha256"], result["result_sha256"])
        self.assertTrue(is_registered(result["input_sha256"]))

    def test_audit_reports_same_anchor_conflicting_results(self) -> None:
        # RED (R1.2 #2): the same input anchor registered against two distinct
        # result hashes is a conflict the audit must surface with exit != 0.
        base = run_forecast(forecast_document())
        first = base["result_sha256"]
        register_publication({**base, "result_sha256": canonical_sha256({"x": 1})})
        problems = audit()
        self.assertTrue(any("conflict" in problem for problem in problems))
        self.assertIn(base["input_sha256"][:16], problems[0])
        self.assertNotEqual(first, canonical_sha256({"x": 1}))

    def test_tampered_registry_line_is_detected(self) -> None:
        # RED (R1.2 #3): editing a single line breaks the chain hash — both the
        # lookup and the audit must report the registry as corrupt.  (The file
        # is set read-only after each append as an accidental-overwrite guard;
        # an attacker clears that attribute — the chain hash is the real gate.)
        result = run_forecast(forecast_document())
        path = Path(self._temporary.name) / "publications.jsonl"
        import stat

        path.chmod(stat.S_IWRITE | stat.S_IREAD)
        lines = path.read_text(encoding="utf-8").splitlines()
        tampered = json.loads(lines[-1])
        tampered["note"] = "TAMPERED"
        lines[-1] = json.dumps(tampered, ensure_ascii=False, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "tampered|hash mismatch"):
            lookup(result["input_sha256"])
        self.assertTrue(any("hash mismatch" in p for p in audit()))

    def test_formal_publication_fails_when_registry_unavailable(self) -> None:
        # RED (R1.2 #4): an unwritable registry must fail the whole formal
        # publication — never silently skip registration.
        blocking = Path(self._temporary.name) / "blocking" / "sub"
        blocking.parent.mkdir(parents=True)
        blocking.write_text("not a directory", encoding="utf-8")
        os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(blocking / "registry")
        with self.assertRaisesRegex(ForecastInputError, "registry unavailable"):
            run_forecast(forecast_document())

    def test_audit_reports_unregistered_claim(self) -> None:
        # An artifact anchored to an input that was never registered must be
        # flagged by the audit cross-check.
        result = run_forecast(forecast_document())
        forged = copy.deepcopy(result)
        forged["input_sha256"] = canonical_sha256({"never": "published"})
        with tempfile.TemporaryDirectory() as directory:
            artifact_path = Path(directory) / "forged.json"
            artifact_path.write_text(
                json.dumps(forged, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            problems = audit([artifact_path])
        self.assertTrue(any("unregistered claim" in problem for problem in problems))

    def test_duplicate_identical_publication_is_not_a_conflict(self) -> None:
        run_forecast(forecast_document())
        run_forecast(forecast_document())
        self.assertEqual(audit(), [])


if __name__ == "__main__":
    unittest.main()
