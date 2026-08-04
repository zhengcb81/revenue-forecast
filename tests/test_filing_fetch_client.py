"""Phase 19.1 — ``filing_fetch_client`` must be a runnable CLI and must surface
the structured error that filing-fetch writes to STDOUT (findings G5/G6).

Background: ``scripts/filing_fetch_client.py`` had no ``__main__``/``main``, so
the SKILL.md examples (``echo '...' | python scripts/filing_fetch_client.py``)
silently did nothing; and on failure it read only stderr, swallowing the
structured error JSON that filing-fetch writes to stdout (``fetch_filing.py``
emits the error document to stdout and exits 2).

These tests use a hermetic *fake* filing-fetch script placed in a temporary
skill root. They never touch the real company-wiki catalog, so they cannot
contend with a live worker.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from filing_fetch_client import _ClientError, resolve_filing  # noqa: E402


SKILL_ROOT = Path(__file__).resolve().parents[1]

# A hermetic stand-in for filing-fetch's fetch_filing.py. It reads the request
# from stdin and branches on ``company_query`` so tests can drive success vs.
# structured-error without mutating the environment or touching any catalog.
_FAKE_FETCH_FILING = """\
import json
import sys

request = json.load(sys.stdin)
query = (request.get("company_query") or "").strip()
argv_record = list(sys.argv)

if query == "AMBIGUOUS_FORCE_ERROR":
    json.dump(
        {
            "schema_version": "1.1",
            "status": "identity_error",
            "error": "ambiguous identity",
            "error_code": "identity_error",
            "retryable": False,
            "candidates": [
                {"ticker": "GOOGL", "canonical_name": "Alphabet Inc.", "market": "US", "exchange": "NASDAQ"},
                {"ticker": "GOOG", "canonical_name": "Alphabet Inc.", "market": "US", "exchange": "NASDAQ"},
            ],
        },
        sys.stdout,
    )
    sys.exit(2)

handle = {
    "_received_argv": argv_record,
    "_request_company_query": query,
    "canonical_path": "companies/Fake/raw/x.pdf",
    "content_sha256": "deadbeef",
    "byte_size": 1,
    "capture_ready": True,
}
json.dump({"schema_version": "1.1", "status": "capture_ready", "handle": handle}, sys.stdout)
sys.exit(0)
"""


@contextlib.contextmanager
def _fake_root() -> Path:
    with tempfile.TemporaryDirectory(prefix="fff_client_fake_") as directory:
        root = Path(directory)
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "fetch_filing.py").write_text(
            _FAKE_FETCH_FILING, encoding="utf-8"
        )
        yield root


def _request(company_query: str = "AMD") -> dict:
    return {
        "schema_version": "1.1",
        "company_query": company_query,
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "as_of_date": "2026-07-18",
    }


class ResolveFilingErrorDiagnosticsTests(unittest.TestCase):
    """The library helper must surface filing-fetch's structured stdout error."""

    def test_resolve_filing_raises_client_error_with_stdout_error_fields(self) -> None:
        # RED today: resolve_filing reads stderr ("no stderr") and raises a
        # _ClientError whose message is a bare string. The structured fields
        # (error_code / retryable / candidates) that filing-fetch wrote to
        # stdout are discarded.
        with _fake_root() as root:
            with self.assertRaises(_ClientError) as ctx:
                resolve_filing(
                    _request("AMBIGUOUS_FORCE_ERROR"), filing_fetch_root=root
                )
        error = ctx.exception
        self.assertEqual(error.error_code, "identity_error")
        self.assertIs(error.retryable, False)
        self.assertIsInstance(error.candidates, list)
        self.assertEqual(len(error.candidates), 2)
        self.assertEqual(error.candidates[0]["ticker"], "GOOGL")

    def test_resolve_filing_missing_script_fails_closed(self) -> None:
        # Phase 6 C1: an unavailable filing-fetch root must raise a clear
        # _ClientError instead of crashing on a missing script path.
        import tempfile as _tempfile

        with _tempfile.TemporaryDirectory(prefix="fff_no_script_") as directory:
            empty = Path(directory)
            with self.assertRaises(_ClientError) as ctx:
                resolve_filing(_request("AMD"), filing_fetch_root=empty)
        self.assertIn("filing-fetch script not found", str(ctx.exception))

    def test_resolve_filing_nonzero_exit_with_non_json_stdout_uses_stderr(self) -> None:
        # Phase 6 C1: when filing-fetch exits non-zero and stdout is not a JSON
        # error document, the client must fall back to stderr detail.
        from unittest.mock import patch

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=2,
            stdout="not-json",
            stderr="boom: upstream failure",
        )
        with _fake_root() as root:
            with patch("filing_fetch_client.subprocess.run", return_value=completed):
                with self.assertRaises(_ClientError) as ctx:
                    resolve_filing(_request("AMD"), filing_fetch_root=root)
            self.assertIn("boom: upstream failure", str(ctx.exception))

    def test_resolve_filing_invalid_stdout_json_is_rejected(self) -> None:
        # Phase 6 C1: zero exit but non-JSON stdout must raise.
        from unittest.mock import patch

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="<html>not json</html>",
            stderr="",
        )
        with _fake_root() as root:
            with patch("filing_fetch_client.subprocess.run", return_value=completed):
                with self.assertRaises(_ClientError) as ctx:
                    resolve_filing(_request("AMD"), filing_fetch_root=root)
            self.assertIn("not valid JSON", str(ctx.exception))

    def test_resolve_filing_non_capture_ready_status_is_rejected(self) -> None:
        # Phase 6 C1: a capture_ready=False response must raise with status.
        from unittest.mock import patch

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {"schema_version": "1.0", "status": "not_found", "error": "no filing"}
            ),
            stderr="",
        )
        with _fake_root() as root:
            with patch("filing_fetch_client.subprocess.run", return_value=completed):
                with self.assertRaises(_ClientError) as ctx:
                    resolve_filing(_request("AMD"), filing_fetch_root=root)
            self.assertIn("status=not_found", str(ctx.exception))


class FilingFetchClientCliTests(unittest.TestCase):
    """The module must be runnable as ``python scripts/filing_fetch_client.py``."""

    def test_client_cli_emits_handle_json_on_success(self) -> None:
        # RED today: no __main__/main, so the module exits 0 with empty stdout.
        # SKILL.md's `echo '...' | python scripts/filing_fetch_client.py` would
        # produce nothing.
        with _fake_root() as root:
            request_path = root / "request.json"
            request_path.write_text(json.dumps(_request("AMD")), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "filing_fetch_client.py"),
                    "--request-file",
                    str(request_path),
                    "--filing-fetch-root",
                    str(root),
                    "--timeout-seconds",
                    "10",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        handle = json.loads(completed.stdout)
        self.assertEqual(handle["_request_company_query"], "AMD")

    def test_client_cli_supports_stdin_request_and_allow_download_flag(self) -> None:
        # RED today: no __main__/main. Guards the exact SKILL.md form
        # `echo '<json>' | python scripts/filing_fetch_client.py --allow-download`.
        with _fake_root() as root:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "filing_fetch_client.py"),
                    "--allow-download",
                    "--filing-fetch-root",
                    str(root),
                    "--timeout-seconds",
                    "10",
                ],
                input=json.dumps(_request("AMD")),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        handle = json.loads(completed.stdout)
        self.assertIn("--allow-download", handle["_received_argv"])
        self.assertEqual(handle["_request_company_query"], "AMD")

    def test_client_cli_emits_structured_error_on_failure(self) -> None:
        # The CLI must surface the structured upstream error (non-zero exit,
        # JSON on stderr carrying error_code/candidates) instead of a bare
        # "filing-fetch exited 2: no stderr". The success stream (stdout) stays
        # clean.
        with _fake_root() as root:
            request_path = root / "request.json"
            request_path.write_text(
                json.dumps(_request("AMBIGUOUS_FORCE_ERROR")), encoding="utf-8"
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "filing_fetch_client.py"),
                    "--request-file",
                    str(request_path),
                    "--filing-fetch-root",
                    str(root),
                    "--timeout-seconds",
                    "10",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout.strip(), "")
        error = json.loads(completed.stderr)
        self.assertEqual(error["error_code"], "identity_error")
        self.assertEqual(len(error["candidates"]), 2)


if __name__ == "__main__":
    unittest.main()
