"""REM-47 / RF-1 — property test: module provenance must refuse last-writer-wins.

Fixture (own): in one process, the target conftest's own pytest_sessionfinish is
driven twice per order with module stubs pointing at DIFFERENT bytes
(write A = the fixed copy `7D1BD8F9…`, write B = production `225FECDD…`), for
both write orders, and `scratch/module_provenance.json` is read back.

Properties asserted per order:
  Q1  `conflict` is flagged true (a conflicting write is never silent);
  Q2  the reported sha256 is the FIRST write's bytes (in either order) — i.e.
      production bytes can never silently replace the fixed copy's record, and
      the fixed copy's record can never silently replace a production record;
  Q3  BOTH distinct writes are retained under `writes` (2 entries, 2 distinct shas).

Target selection (env): B3P_PROV_CONFTEST
  default       -> <attempt>/iso/conftest.py                (expected GREEN)
  RED baseline  -> <attempt>/b3_reference/iso/conftest.py   (B3's original overwrites
                   the file each run: no conflict flag, no writes history, reported
                   value = LAST writer => Q1/Q2/Q3 must FAIL).
The probe restores any pre-existing provenance record afterwards, so runs never
pollute each other.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
PROBE = Path(__file__).resolve().parent / "b3p_probe.py"
DEFAULT_TARGET = ATTEMPT / "iso" / "conftest.py"

ORDERS = ("fixed_then_production", "production_then_fixed")


def _target() -> Path:
    raw = os.environ.get("B3P_PROV_CONFTEST", str(DEFAULT_TARGET))
    path = Path(raw)
    if not path.is_absolute():
        path = ATTEMPT / path
    return path.resolve()


def _run_probe() -> dict:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(PROBE), str(_target()), "provenance"],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
        cwd=str(ATTEMPT),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.stdout.strip(), (
        f"probe produced no stdout (rc={proc.returncode}) stderr:\n{proc.stderr}")
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert "error" not in out, f"probe failed to exercise the conftest: {out['error']}"
    return out


def test_q0_fixture_writes_really_conflict():
    out = _run_probe()
    assert out["fixed_sha"] != out["prod_sha"]


def test_q1_q2_q3_conflict_is_flagged_and_both_writes_survive_in_both_orders():
    out = _run_probe()
    expected_first = {
        "fixed_then_production": out["fixed_sha"],
        "production_then_fixed": out["prod_sha"],
    }
    both = {out["fixed_sha"], out["prod_sha"]}
    for order in ORDERS:
        record = out["orders"].get(order)
        assert isinstance(record, dict), f"no provenance record written for {order}"
        assert record.get("conflict") is True, (
            f"[{order}] conflicting writes were NOT flagged: {record.get('conflict')!r} "
            "— last-writer-wins is refused, flagged, never silent")
        module = record.get("modules", {}).get("company_wiki_source", {})
        assert module.get("sha256") == expected_first[order], (
            f"[{order}] reported provenance sha {module.get('sha256')} is not the FIRST "
            f"write's bytes {expected_first[order]} — a later writer silently replaced it")
        writes = module.get("writes")
        assert isinstance(writes, list) and len(writes) == 2, (
            f"[{order}] both writes must be retained, got {writes!r}")
        shas = {write.get("sha256") for write in writes}
        assert shas == both, (
            f"[{order}] retained writes {shas} do not cover both byte sets {both}")
