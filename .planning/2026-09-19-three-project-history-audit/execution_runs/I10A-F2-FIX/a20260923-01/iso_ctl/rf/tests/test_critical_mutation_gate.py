"""FC-1005: critical-mutation gate self-tests.

Every one of the eight critical mutation classes must have >= 1 killed-
mutation evidence (receipts or the FC-1005 evidence file).  The gate must be
honest: removing a class's evidence makes the gate fail.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "compatibility"))

import critical_mutation_gate as cmg  # noqa: E402


class TestCriticalMutationGate(unittest.TestCase):
    def test_all_eight_classes_covered(self):
        report = cmg.gate_report()
        self.assertEqual(report["gaps"], [],
                         f"critical mutation classes missing evidence: {report['gaps']}")

    def test_class_set_is_exact(self):
        self.assertEqual(set(cmg.CLASSES), {
            "root_special_case", "epoch_condition", "hash_check",
            "download_authorization", "latest_reresolve",
            "artifact_invalidation", "zero_call_event", "path_containment",
        })

    def test_evidence_file_has_latest_reresolve(self):
        text = cmg.EVIDENCE_FILE.read_text(encoding="utf-8")
        self.assertIn("## latest_reresolve", text)
        self.assertIn("M-latest", text)

    def test_receipt_scan_finds_kills(self):
        ev = cmg.collect_receipt_evidence()
        self.assertGreaterEqual(len(ev["hash_check"]), 1)
        self.assertGreaterEqual(len(ev["epoch_condition"]), 1)

    def test_gate_fails_without_file_evidence(self):
        """The gate must be honest: with NO receipt evidence (empty sibling
        set) and an empty evidence file, the latest_reresolve class becomes a
        gap — the gate never passes on nothing."""
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / "critical_mutation_evidence.md"
            fake.write_text("# empty\n", encoding="utf-8")
            empty_siblings = (Path(td) / "noreceipts",)
            with mock.patch.object(cmg, "EVIDENCE_FILE", fake), \
                    mock.patch.object(cmg, "SIBLINGS", empty_siblings):
                report = cmg.gate_report()
                self.assertIn("latest_reresolve", report["gaps"])
                # and with the evidence file present, the same empty-sibling
                # setup must NOT gap (file evidence is sufficient)
            with mock.patch.object(cmg, "EVIDENCE_FILE", cmg.EVIDENCE_FILE), \
                    mock.patch.object(cmg, "SIBLINGS", empty_siblings):
                report2 = cmg.gate_report()
                self.assertNotIn("latest_reresolve", report2["gaps"])


if __name__ == "__main__":
    unittest.main()
