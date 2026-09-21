"""FC-1104: audit dashboard / ledger + release gate contracts.

SCENARIO: AUD-07 (audit mechanisms gate the release)

The dashboard must aggregate run reports into a ledger and enforce the
release gate: latest T2 <= 24h and ok, latest T3 <= 7d and passed.  A stale
or failed T2/T3 must make the gate fail (release blocked).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

import audit_dashboard as ad  # noqa: E402

DASHBOARD = PROJECT_ROOT / "tools" / "audit_dashboard.py"


def _seed(report_root: Path, *, t2_ok=True, t2_age_h=1, t3_ok=True,
          t3_age_d=1, run_id_t2=None, run_id_t3=None):
    now = datetime.now(timezone.utc)
    t2_id = run_id_t2 or (now - timedelta(hours=t2_age_h)).strftime("%Y%m%dT%H%M%SZ")
    t3_id = run_id_t3 or (now - timedelta(days=t3_age_d)).strftime("%Y%m%dT%H%M%SZ")
    d2 = report_root / t2_id
    d2.mkdir(parents=True)
    (d2 / "report.json").write_text(json.dumps({
        "run_id": t2_id, "ok": t2_ok,
        "problems": [] if t2_ok else ["canary samples degraded"],
        "checks": {"latency": {"resolve_sample_sec": 0.01}},
        "triplet": {"revenue": "a" * 40},
    }), encoding="utf-8")
    d3 = report_root / t3_id
    d3.mkdir(parents=True)
    (d3 / "t3_report.json").write_text(json.dumps({
        "run_id": t3_id, "status": "passed" if t3_ok else "failed",
    }), encoding="utf-8")
    return t2_id, t3_id


class TestAuditDashboard(unittest.TestCase):
    def test_gate_passes_on_fresh_green_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed(root)
            ok, reasons = ad.release_gate(ad.collect_reports(root))
            self.assertTrue(ok, reasons)

    def test_stale_t2_fails_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed(root, t2_age_h=30)
            ok, reasons = ad.release_gate(ad.collect_reports(root))
            self.assertFalse(ok)
            self.assertTrue(any("24h" in r for r in reasons))

    def test_failed_t2_fails_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed(root, t2_ok=False)
            ok, reasons = ad.release_gate(ad.collect_reports(root))
            self.assertFalse(ok)
            self.assertTrue(any("not ok" in r for r in reasons))

    def test_stale_t3_fails_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed(root, t3_age_d=10)
            ok, reasons = ad.release_gate(ad.collect_reports(root))
            self.assertFalse(ok)
            self.assertTrue(any("7d" in r for r in reasons))

    def test_cli_writes_ledger_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _seed(root)
            proc = subprocess.run(
                [sys.executable, "-B", str(DASHBOARD), "--report-root", str(root)],
                capture_output=True, text=True, encoding="utf-8", timeout=60,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout)
            ledger = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
            self.assertTrue(ledger["release_gate"]["ok"])
            self.assertEqual(len(ledger["recent_runs"]), 2)
            # no leftover temp files
            self.assertFalse([p for p in root.rglob("*.tmp")])


if __name__ == "__main__":
    unittest.main()
