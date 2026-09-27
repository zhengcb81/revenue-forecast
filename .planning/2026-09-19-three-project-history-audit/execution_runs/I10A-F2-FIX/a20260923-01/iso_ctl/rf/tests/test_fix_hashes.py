from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, validate_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
import fix_hashes  # noqa: E402


def _corrupt_receipt(data: dict) -> None:
    data["sources"][0]["capture"]["receipt_sha256"] = "0" * 64


def _corrupt_excerpt(data: dict) -> None:
    data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64


class HashLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()

    def test_clean_doc_has_no_drift(self) -> None:
        self.assertEqual(fix_hashes.find_hash_drift(self.base), [])

    def test_detects_stale_capture_receipt(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        drift = fix_hashes.find_hash_drift(data)
        self.assertTrue(any("receipt_sha256" in d["path"] for d in drift), drift)

    def test_detects_stale_claim_excerpt(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_excerpt(data)
        drift = fix_hashes.find_hash_drift(data)
        self.assertTrue(any("excerpt_sha256" in d["path"] for d in drift), drift)

    def test_detects_stale_claim_synced_hashes(self) -> None:
        data = copy.deepcopy(self.base)
        data["evidence_claims"][0]["capture_receipt_sha256"] = "0" * 64
        data["evidence_claims"][0]["content_sha256"] = "0" * 64
        drift = fix_hashes.find_hash_drift(data)
        paths = " ".join(d["path"] for d in drift)
        self.assertIn("capture_receipt_sha256", paths)
        self.assertIn("content_sha256", paths)

    def test_apply_capture_receipt_fix_passes_validate(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        with self.assertRaises(ForecastInputError):
            validate_document(copy.deepcopy(data))
        changes = fix_hashes.apply_hash_fixes(data)
        self.assertTrue(changes)
        validate_document(data)  # must not raise

    def test_apply_syncs_claim_hashes_to_source_capture(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_excerpt(data)
        data["evidence_claims"][0]["capture_receipt_sha256"] = "0" * 64
        data["evidence_claims"][0]["content_sha256"] = "0" * 64
        fix_hashes.apply_hash_fixes(data)
        claim = data["evidence_claims"][0]
        source = next(s for s in data["sources"] if s["source_id"] == claim["source_id"])
        self.assertEqual(claim["capture_receipt_sha256"], source["capture"]["receipt_sha256"])
        self.assertEqual(claim["content_sha256"], source["capture"]["snapshot_sha256"])
        validate_document(data)

    def test_snapshot_hash_is_opaque_and_not_overwritten(self) -> None:
        data = copy.deepcopy(self.base)
        original = data["sources"][0]["capture"]["snapshot_sha256"]
        fix_hashes.apply_hash_fixes(data)
        self.assertEqual(data["sources"][0]["capture"]["snapshot_sha256"], original)

    def test_idempotent_second_apply_is_noop(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        _corrupt_excerpt(data)
        fix_hashes.apply_hash_fixes(data)
        second = fix_hashes.apply_hash_fixes(data)
        self.assertEqual(second, [])


class FixHashesCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, data: dict) -> str:
        path = os.path.join(self.dir, "input.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        root = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, str(root / "scripts" / "fix_hashes.py"), *args]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_check_exit_2_on_drift(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        result = self._run(self._write(data), "--check")
        self.assertEqual(result.returncode, 2)
        self.assertIn("receipt_sha256", result.stdout + result.stderr)

    def test_check_exit_0_when_clean(self) -> None:
        result = self._run(self._write(copy.deepcopy(self.base)), "--check")
        self.assertEqual(result.returncode, 0)

    def test_default_fix_clears_drift_in_place(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        path = self._write(data)
        self.assertEqual(self._run(path).returncode, 0)
        self.assertEqual(self._run(path, "--check").returncode, 0)

    def test_dry_run_does_not_write(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        path = self._write(data)
        with open(path, encoding="utf-8") as handle:
            original = handle.read()
        result = self._run(path, "--dry-run")
        self.assertEqual(result.returncode, 0)
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), original)

    def test_output_writes_new_path_and_leaves_original(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        path = self._write(data)
        with open(path, encoding="utf-8") as handle:
            original = handle.read()
        out = os.path.join(self.dir, "fixed.json")
        self.assertEqual(self._run(path, "--output", out).returncode, 0)
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), original)
        self.assertEqual(self._run(out, "--check").returncode, 0)


class MainInProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _path(self, data: dict, name: str = "i.json") -> str:
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def test_main_check_returns_2_on_drift(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        self.assertEqual(fix_hashes.main([self._path(data), "--check"]), 2)

    def test_main_check_returns_0_when_clean(self) -> None:
        self.assertEqual(fix_hashes.main([self._path(copy.deepcopy(self.base)), "--check"]), 0)

    def test_main_default_fix_then_clean(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        path = self._path(data)
        self.assertEqual(fix_hashes.main([path]), 0)
        self.assertEqual(fix_hashes.main([path, "--check"]), 0)

    def test_main_dry_run_returns_0(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        self.assertEqual(fix_hashes.main([self._path(data), "--dry-run"]), 0)

    def test_main_output_path(self) -> None:
        data = copy.deepcopy(self.base)
        _corrupt_receipt(data)
        out = os.path.join(self.dir, "o.json")
        self.assertEqual(fix_hashes.main([self._path(data), "--output", out]), 0)
        self.assertEqual(fix_hashes.main([out, "--check"]), 0)

    def test_main_clean_default_is_noop(self) -> None:
        self.assertEqual(fix_hashes.main([self._path(copy.deepcopy(self.base))]), 0)

    def test_main_bad_json_returns_2(self) -> None:
        path = os.path.join(self.dir, "bad.json")
        Path(path).write_text("{not json", encoding="utf-8")
        self.assertEqual(fix_hashes.main([path, "--check"]), 2)

    def test_main_warns_on_malformed_snapshot(self) -> None:
        data = copy.deepcopy(self.base)
        data["sources"][0]["capture"]["snapshot_sha256"] = "not-a-hex-digest"
        self.assertEqual(fix_hashes.main([self._path(data), "--check"]), 2)


if __name__ == "__main__":
    unittest.main()
