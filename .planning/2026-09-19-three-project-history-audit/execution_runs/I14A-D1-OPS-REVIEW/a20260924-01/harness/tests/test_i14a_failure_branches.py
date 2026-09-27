"""I-14-A independent suite: the frozen expectations, asserted directly.

Every test imports expectations from ``fixture_spec`` (frozen in oracle.md before
any run) and drives the probe as a subprocess.  Nothing here imports the probe, so
a defect in the probe cannot satisfy its own assertion.  The suite is expected to
pass on the patched tool; running it against the unmodified production tool is the
RED demonstration recorded in ``before/``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
ATTEMPT = HERE.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SPEC = _load("fixture_spec", HERE / "fixture_spec.py")
RUNNER = _load("run_probe_cases", HERE / "run_probe_cases.py")

TOOL_ENV = "I14A_TOOL"
_DEFAULT_TOOL = Path(__file__).resolve().parents[2] / "iso" / "slo_probe_patched.py"
PROD_TOOL = Path(__file__).resolve().parents[2] / "iso" / "tool_prod" / "slo_probe.py"
OUT_ROOT_ENV = "I14A_OUT_ROOT"


def _tool() -> Path:
    """The probe under test; overridable so the SAME suite can be run against the
    unmodified production tool to produce the RED baseline (before/)."""
    import os
    return Path(os.environ.get(TOOL_ENV, str(_DEFAULT_TOOL)))


TOOL = _DEFAULT_TOOL


def _out_root() -> Path:
    import os
    root = Path(os.environ.get(OUT_ROOT_ENV, str(ATTEMPT / "harness" / "scratch" / "suite")))
    root.mkdir(parents=True, exist_ok=True)
    return root


@pytest.mark.parametrize("case_id", list(SPEC.CASES))
def test_frozen_case(case_id: str) -> None:
    if SPEC.CASES[case_id].get("excluded_from_all"):
        pytest.skip("bundle-copy control runs in run_bundle_control.py")
    result = RUNNER.run_case(_tool(), _out_root() / case_id, case_id, None)
    verdict = result["verdict"]
    assert verdict["all_ok"], json.dumps(verdict, ensure_ascii=False, indent=2)


def test_binding_mismatch_is_refused() -> None:
    result = RUNNER.binding_case(_tool(), _out_root() / "binding-mismatch", "mismatch")
    assert result["verdict"]["all_ok"], json.dumps(result["verdict"], ensure_ascii=False,
                                                   indent=2)
    assert result["raw_returncode"] == 3


def test_binding_consistent_is_accepted() -> None:
    result = RUNNER.binding_case(_tool(), _out_root() / "binding-consistent", "consistent")
    assert result["verdict"]["all_ok"], json.dumps(result["verdict"], ensure_ascii=False,
                                                   indent=2)


def test_budgets_and_percentiles_are_frozen() -> None:
    verdict = RUNNER.percentile_case(_tool(), _out_root() / "frozen-constants")
    assert verdict["all_ok"], json.dumps(verdict, ensure_ascii=False, indent=2)


def test_bundle_copy_control() -> None:
    """The copied-exact control (oracle.md E7), driven from this suite."""
    script = HERE / "run_bundle_control.py"
    proc = subprocess.run([SPEC.PYTHON, "-X", "utf8", "-B", str(script), str(_tool()),
                           str(_out_root() / "bundle-control"), str(PROD_TOOL)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=SPEC.PROBE_CASES_TIMEOUT_SECONDS)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_production_tool_is_red_on_the_frozen_counterexamples() -> None:
    """RED demonstration: the unmodified tool lacks every failure-branch guard.

    This is the audit finding reproduced as falsifiable source facts, not prose.
    Each assertion names the exact construct whose absence caused the defect.
    """
    prod_text = PROD_TOOL.read_text(encoding="utf-8")
    resolve_body = prod_text.split("def _resolve", 1)[1].split("def _percentiles", 1)[0]
    assert "result = subprocess.run" not in resolve_body          # no rc captured
    assert "returncode" not in resolve_body                       # rc never inspected
    assert "bundle = exact[:]" in prod_text                        # bundle == exact alias
    assert "def _load_bundle_measurement" not in prod_text
    assert "psutil.Process()" in prod_text                         # probe's own process
    assert "children(recursive=True)" in prod_text                 # called after exit
    assert "def check_catalog_binding" not in prod_text            # catalog only is_file()
    assert "catalog.is_file()" in prod_text
    assert "peak_rss_source" not in prod_text                      # no collected/zero split
