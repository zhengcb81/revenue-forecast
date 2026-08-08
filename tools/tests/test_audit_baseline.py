"""WU-0.1: read-only audit baseline tool contract tests.

The tool ``tools/audit_baseline.py --read-only`` must:

1.  collect baseline facts (commits, tool versions, config hashes,
    catalog schema/size/scan status, root realpaths) and print JSON;
2.  NEVER open the catalog SQLite with a write transaction — the
    connection must be ``mode=ro``;
3.  NEVER create or modify any file under a probe root it is pointed
    at (a temp writable root containing files);
4.  leave real roots byte-identical before/after (tree metadata/hash
    sampling equal).

RED phase: these tests must fail while the tool is missing — the
subprocess raises FileNotFoundError, which unittest records as an
ERROR (not a skip, not a pass).  Mutation check: changing the tool to
open ``mode=rw`` or to write a file must flip tests below to red.
"""

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
sys.path.insert(0, str(REPO_ROOT / "tools"))

from audit_baseline import open_catalog_readonly  # noqa: E402


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
        cmd = [sys.executable, str(TOOL), *args]
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

    def test_requires_readonly_flag(self) -> None:
        """Without --read-only the tool must refuse to run."""
        proc = self._run_tool()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("read-only", (proc.stdout + proc.stderr).lower())

    def test_collects_baseline_facts(self) -> None:
        """Baseline JSON must carry commits, versions, config hashes,
        catalog schema/scan status and root realpaths."""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = self._make_catalog(tmp)
            cfg = tmp / "source_catalog.yaml"
            cfg.write_text("reusable_root_kinds: [company_raw]\n", encoding="utf-8")
            proc = self._run_tool(
                "--read-only",
                "--catalog", str(catalog),
                "--config", str(cfg),
                "--repos", str(REPO_ROOT),
                "--probe-roots", str(tmp / "companies"),
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn("repos", data)
            self.assertIn("environment", data)
            self.assertIn("configs", data)
            self.assertIn("catalog", data)
            self.assertIn("roots", data)
            self.assertTrue(data["catalog"]["schema_version"] >= 0)
            self.assertIn("completed_with_errors", data["catalog"]["recent_scan_status"])

    def test_catalog_opened_readonly(self) -> None:
        """Catalog connection must be mode=ro: any write attempt must fail."""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = self._make_catalog(tmp)
            before = catalog.read_bytes()
            proc = self._run_tool("--read-only", "--catalog", str(catalog))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(catalog.read_bytes(), before, "catalog modified by tool")
            # WAL/SHM side files must not be created by a read-only opener
            for side in (catalog.parent / f"{catalog.name}-wal", catalog.parent / f"{catalog.name}-shm"):
                self.assertFalse(side.exists(), f"side file created: {side}")

    def test_open_catalog_readonly_rejects_writes(self) -> None:
        """Unit-level: the connection must reject writes even before any tool code
        decides to be careful — a mode=rw mutation must flip this test red."""
        with TemporaryDirectory() as td:
            tmp = Path(td)
            catalog = self._make_catalog(tmp)
            con = open_catalog_readonly(catalog)
            try:
                with self.assertRaises(sqlite3.OperationalError):
                    con.execute("CREATE TABLE evil (x TEXT)")
            finally:
                con.close()

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


if __name__ == "__main__":
    unittest.main()
