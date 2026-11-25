"""Legacy assurance tools retain local diagnostics and historical evidence."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "audit_baseline.py"


def tree_hash(root: Path) -> str:
    """Deterministic tree fingerprint: relative path + size + mtime-ns."""
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            st = path.stat()
            entries.append(f"{path.relative_to(root)}|{st.st_size}|{st.st_mtime_ns}")
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(entry.encode("utf-8"))
    return digest.hexdigest()


class AuditBaselineTests(unittest.TestCase):
    def _run_tool(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
        cmd = [sys.executable, "-B", str(TOOL), *args]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", cwd=cwd, timeout=120
        )

    def _make_catalog(self, root: Path) -> Path:
        """Create a small temp catalog with roots/scan_runs/documents rows."""
        db = root / "catalog.sqlite3"
        con = sqlite3.connect(db)
        con.execute("PRAGMA user_version = 7")
        con.execute("CREATE TABLE roots (root_id TEXT, path TEXT, kind TEXT, priority INTEGER, last_scan TEXT, last_scan_at TEXT)")
        con.execute("CREATE TABLE scan_runs (run_id TEXT, started_at TEXT, finished_at TEXT, status TEXT, summary TEXT)")
        con.execute("CREATE TABLE documents (document_id TEXT)")
        con.execute(
            "INSERT INTO roots VALUES ('company_raw', ?, 'company_raw', 10, 'scan-x', '2026-08-08T13:44:53Z')",
            (str(root / "companies"),),
        )
        con.execute("INSERT INTO scan_runs VALUES ('scan-x', '2026-08-08T13:44:53Z', '2026-08-08T13:47:06Z', 'completed_with_errors', '{}')")
        con.execute("INSERT INTO documents VALUES ('doc-1')")
        con.commit()
        con.close()
        return db

    def test_local_baseline_without_mode_acknowledgment(self) -> None:
        with TemporaryDirectory() as td:
            tmp = Path(td)
            cfg = tmp / "source_catalog.yaml"
            cfg.write_text("reusable_root_kinds: [company_raw]\n", encoding="utf-8")
            proc = self._run_tool(
                "--config", str(cfg),
                "--repos", str(REPO_ROOT),
                "--probe-roots", str(tmp / "companies"),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn(REPO_ROOT.name, data["repos"])
            self.assertIn("python", data["environment"])
            self.assertEqual(data["configs"][str(cfg)], hashlib.sha256(cfg.read_bytes()).hexdigest())
            self.assertIn(str(tmp / "companies"), data["roots"])
            self.assertEqual(data["catalog"]["status"], "not_requested")
            self.assertIsNone(data["catalog"]["schema_version"])
            self.assertIsNone(data["catalog"]["error"])

    def test_explicit_legacy_catalog_shape_is_unavailable(self) -> None:
        with TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = self._make_catalog(tmp)
            before = catalog.read_bytes()
            proc = self._run_tool("--read-only", "--catalog", str(catalog), cwd=tmp)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            response = json.loads(proc.stdout)["catalog"]
            self.assertEqual(response["status"], "unavailable")
            self.assertEqual(response["reason"], "catalog_owner_interface_required")
            self.assertIsNone(response["schema_version"])
            self.assertIsNone(response["size_bytes"])
            self.assertIsNone(response["recent_scan_status"])
            self.assertEqual(response["roots"], [])
            self.assertNotIn(catalog.name, proc.stdout)
            self.assertEqual(catalog.read_bytes(), before)
            self.assertEqual(list(tmp.iterdir()), [catalog])

    def test_explicit_catalog_does_not_open_private_sqlite(self) -> None:
        bootstrap = """\
import runpy
import sys

def guard(event, args):
    if event == "sqlite3.connect":
        raise AssertionError("RF audit opened a private SQLite database")

sys.argv = sys.argv[1:]
sys.addaudithook(guard)
runpy.run_path(sys.argv[0], run_name="__main__")
"""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = self._make_catalog(tmp)
            proc = subprocess.run(
                [sys.executable, "-B", "-c", bootstrap, str(TOOL),
                 "--read-only", "--catalog", str(catalog)],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["catalog"]["status"], "unavailable")

    def test_probe_root_unchanged(self) -> None:
        """Pointing the tool at a writable probe root must leave it byte-identical."""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            probe = tmp / "probe"
            probe.mkdir()
            (probe / "a.txt").write_text("hello\n", encoding="utf-8")
            (probe / "sub").mkdir()
            (probe / "sub" / "b.txt").write_text("world\n", encoding="utf-8")
            before = tree_hash(probe)
            proc = self._run_tool("--read-only", "--probe-roots", str(probe))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(tree_hash(probe), before, "probe root modified by tool")


class ArchivedReplayTests(unittest.TestCase):
    def test_legacy_replay_stops_before_traversal_or_owner_use(self) -> None:
        script = REPO_ROOT / "tools" / "ex05_chain_replay.py"
        receipt_path = Path("assurance/fc/FC-505/11_implementer_receipt.json")
        receipt = (REPO_ROOT / receipt_path).read_bytes()
        bootstrap = """\
import runpy
import sys
from pathlib import Path
from types import ModuleType

# Stub the old imports so old execution deterministically reaches Dropbox
# traversal without touching any real CWP, FF, Dayu or user directory.
for name, identifiers in {
    "company_wiki.source_catalog": (
        "CatalogConfig ResolutionStatus RootSpec SourceCatalog SourceRequest SourceResolver"
    ),
    "company_wiki_source": "build_revenue_source_record",
    "filing_contracts": "validate_handle",
}.items():
    module = ModuleType(name)
    for identifier in identifiers.split():
        setattr(module, identifier, None)
    sys.modules[name] = module
Path.home = classmethod(lambda cls: Path.cwd())

def guard(event, args):
    if event in {"pathlib.Path.rglob", "sqlite3.connect"}:
        raise AssertionError("archived replay tried to traverse or open owner data")

sys.argv = sys.argv[1:]
sys.addaudithook(guard)
runpy.run_path(sys.argv[0], run_name="__main__")
"""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            archived = tmp / receipt_path
            archived.parent.mkdir(parents=True)
            archived.write_bytes(receipt)
            proc = subprocess.run(
                [sys.executable, "-B", "-c", bootstrap, str(script)],
                cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=15,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertFalse(proc.stdout)
            self.assertIn("fc505_replay_retired", proc.stderr)
            self.assertIn(receipt_path.as_posix(), proc.stderr)
            self.assertEqual(archived.read_bytes(), receipt)
            self.assertEqual([f for f in tmp.rglob("*") if f.is_file()], [archived])
        self.assertEqual((REPO_ROOT / receipt_path).read_bytes(), receipt)


if __name__ == "__main__":
    unittest.main()
