"""REM-47 / RF-1 — property test: the conftest's guard order must be REAL.

Fixture (own): the probe points the target conftest at BOTH the production repo
(`RF:scripts/company_wiki_source.py`, 225FECDD…/19364) and the attempt-local
fixed copy (`7D1BD8F9…/20545`) with conflicting bytes, in one fresh process.

Properties asserted:
  P0  the two candidate files really do differ (conflicting-values precondition);
  P1  the conftest source states the order it claims ("fixed sources first");
  P2  the ACTUAL sys.path head equals that claimed order
      [FIXED_CW, FIXED_RF, RF/scripts, CW/src] — docstring = reality;
  P3  the fixed copy WINS: find_spec("company_wiki_source") resolves to the
      fixed copy, not production.

Target selection (env):
  B3P_GUARD_CONFTEST = path to the conftest under test
    default        -> <attempt>/iso/conftest.py          (expected GREEN)
    RED baseline   -> <attempt>/b3_reference/iso/conftest.py (B3's original: per-entry
                      insert(0) leaves production first and the origin is never checked
                      => P2 and P3 must FAIL — this is the RED half of REM-47).
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


def _target() -> Path:
    raw = os.environ.get("B3P_GUARD_CONFTEST", str(DEFAULT_TARGET))
    path = Path(raw)
    if not path.is_absolute():
        path = ATTEMPT / path
    return path.resolve()


def _run_probe() -> dict:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(PROBE), str(_target()), "guard"],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
        cwd=str(ATTEMPT),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.stdout.strip(), (
        f"probe produced no stdout (rc={proc.returncode}) stderr:\n{proc.stderr}")
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert "error" not in out, f"probe failed to exercise the conftest: {out['error']}"
    return out


def _norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


def test_p0_fixture_has_conflicting_bytes_on_both_candidates():
    out = _run_probe()
    assert out["fixed_exists"] and out["prod_exists"]
    assert out["fixed_sha"] != out["prod_sha"], (
        "fixture broken: fixed and production copies are not conflicting values "
        f"({out['fixed_sha']} vs {out['prod_sha']})")


def test_p1_conftest_states_the_order_it_claims():
    source = _target().read_text(encoding="utf-8")
    assert "fixed sources first" in source, (
        "the conftest no longer states the fixed-first order it is supposed to implement")


def test_p2_actual_sys_path_head_matches_the_claimed_order():
    out = _run_probe()
    expected = [out["fixed_cw"], out["fixed_rf"], out["rf_scripts"], out["cw_src"]]
    actual = out["sys_path_head"][:4]
    assert [_norm(p) for p in actual] == [_norm(p) for p in expected], (
        "docstring != reality: claimed order [FIXED_CW, FIXED_RF, RF/scripts, CW/src] "
        f"but sys.path head is {actual}")


def test_p3_fixed_copy_wins_the_import_race():
    out = _run_probe()
    expected_origin = _norm(str(Path(out["fixed_rf"]) / "company_wiki_source.py"))
    assert out["origin"] is not None, "company_wiki_source not importable at all"
    assert _norm(out["origin"]) == expected_origin, (
        "the fixed copy does NOT win: importer resolves company_wiki_source to "
        f"{out['origin']} instead of {expected_origin} (production bytes would run)")
