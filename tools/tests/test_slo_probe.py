"""FC-1303: SLO probe contract tests — frozen budgets + percentile math.

The probe itself runs against the production catalog (read-only); these
tests lock the frozen budgets and the percentile computation so a budget
weakening or a percentile bug fails fast.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from slo_probe import BUDGETS, _percentiles  # noqa: E402


@pytest.mark.parametrize("owner_exit", (0, 5))
def test_probe_measures_only_successful_resolves_from_configured_owner(tmp_path, owner_exit):
    owner = tmp_path / "company_wiki" / "source_catalog"
    owner.mkdir(parents=True)
    (owner.parent / "__init__.py").touch()
    (owner / "__init__.py").touch()
    (owner / "cli.py").write_text(
        "import json, sys\n"
        "from pathlib import Path\n"
        "assert sys.argv[1] == '--config' and sys.argv[3] == 'resolve'\n"
        "assert Path(sys.argv[2]).read_text(encoding='ascii') == 'explicit owner config'\n"
        "with Path(sys.argv[2]).with_name('requests.jsonl').open('a', encoding='ascii') as log:\n"
        "    log.write(json.dumps(sys.argv[4:]) + '\\n')\n"
        "raise SystemExit(" + str(owner_exit) + ")\n",
        encoding="utf-8",
    )
    config = tmp_path / "owner.yaml"
    config.write_text("explicit owner config", encoding="ascii")
    report = tmp_path / "report.json"
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "slo_probe.py"),
         "--config", str(config), "--report", str(report), "--samples", "3"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(tmp_path), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, encoding="utf-8", timeout=30, check=False,
    )
    if owner_exit:
        assert result.returncode == 1 and "exit 5" in result.stderr
        assert not result.stdout and not report.exists()
        assert len((tmp_path / "requests.jsonl").read_text().splitlines()) == 1
    else:
        assert result.returncode == 0, result.stderr
        value = json.loads(result.stdout)
        assert value == json.loads(report.read_bytes())
        if sys.platform == "linux":
            assert value["slo_probe"]["peak_rss_gb"] > 0
        calls = [json.loads(line) for line in (tmp_path / "requests.jsonl").read_text().splitlines()]
        assert len(calls) == 6
        assert sum("--fiscal-year" in call for call in calls) == 3
        assert sum("--mode" in call for call in calls) == 3


class SloProbeContractTests(unittest.TestCase):
    def test_budgets_are_frozen_at_measured_levels(self) -> None:
        # Measured on production 2026-08-13 (findings 62): p95 ~0.6s, RSS 21MB.
        # Weakening any budget must fail this test (deliberate-review path).
        self.assertEqual(BUDGETS["exact_p95"], 5.0)
        self.assertEqual(BUDGETS["latest_p95"], 5.0)
        self.assertEqual(BUDGETS["bundle_p95"], 5.0)
        self.assertEqual(BUDGETS["peak_rss_gb"], 2.0)

    def test_percentiles_are_order_statistics(self) -> None:
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        p = _percentiles(values)
        self.assertEqual(p["p50"], 0.3)
        self.assertGreaterEqual(p["p95"], p["p50"])
        self.assertGreaterEqual(p["p99"], p["p95"])
        self.assertEqual(_percentiles([1.0])["p50"], 1.0)

    def test_probe_cli_is_read_only_by_contract(self) -> None:
        # The probe never writes to the catalog — it only spawns resolve
        # (read-only) and writes an isolated report.  Guard the docstring
        # contract with a source scan: no INSERT/UPDATE/DELETE in the tool.
        source = (ROOT / "tools" / "slo_probe.py").read_text(encoding="utf-8")
        for forbidden in ("INSERT", "UPDATE ", "DELETE FROM", "CREATE TABLE"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
