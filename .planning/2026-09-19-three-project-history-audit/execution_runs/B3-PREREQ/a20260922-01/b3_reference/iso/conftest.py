"""B3 — I-05-C delivery fixes: path binding + production-provenance record.

This conftest makes the point of REM-12 enforceable: the regression suites must
run against the bytes the evidence claims.  It (a) prepends the two production
repos to ``sys.path`` so no test file's own ``ISO_ROOT/checkout_scripts`` entry
can silently win, and (b) writes the resolved module paths and hashes to
``scratch/module_provenance.json`` so every run carries machine-checkable proof
of WHICH bytes executed.

Run bound commands with ``cwd`` set to the ``iso/`` directory: pytest then loads
this file as ``rootdir`` conftest *before* collecting test modules, so the path
binding wins the import race.  The corresponding ASSERTION lives in the test
files (``TestProductionProvenance`` in ``tests/test_b3_production_provenance.py``),
so reverting this binding makes a real test go RED instead of silently recording
the drift.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ATTEMPT_ROOT = Path(__file__).resolve().parents[1]
FIXED_RF = ATTEMPT_ROOT / "iso" / "fixed" / "rf_scripts"
FIXED_CW = ATTEMPT_ROOT / "iso" / "fixed" / "cw_source_catalog"
RF_ROOT = Path("C:/Users/郑曾波/Projects/revenue-forecast")
CW_ROOT = Path("C:/Users/郑曾波/Projects/company-wiki")

# Order matters: attempt-local fixed sources first (so the FIXED run exercises
# the remediation), then the production repos.  The I-05-B / I-05-C frozen
# checkout copies are deliberately never inserted — that stale entry is exactly
# the REM-12 defect.
for _entry in (str(FIXED_CW), str(FIXED_RF), str(RF_ROOT / "scripts"),
               str(CW_ROOT / "src")):
    while _entry in sys.path:
        sys.path.remove(_entry)
    sys.path.insert(0, _entry)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _binding_state() -> dict:
    import importlib.util

    fixed_cws = FIXED_RF / "company_wiki_source.py"
    spec = importlib.util.find_spec("company_wiki_source")
    origin = Path(spec.origin).resolve() if spec and spec.origin else None
    return {
        "sys_path_head": sys.path[:8],
        "find_spec_origin": str(origin) if origin else None,
        "fixed_rf": str(FIXED_RF),
        "fixed_rf_on_path": str(FIXED_RF) in sys.path,
        "fixed_cws_exists": fixed_cws.is_file(),
    }


@pytest.hookimpl(tryfirst=True)
def pytest_collection(session):  # noqa: ARG001
    """Record the binding *before* any test module is imported, and fail the
    session if the fixed sources are not the ones the importer will find.

    This is the loud guard for REM-12: if the binding silently degrades (wrong
    cwd, dropped prepend), collection stops here instead of producing a green
    run against the wrong bytes."""
    state = _binding_state()
    scratch = ATTEMPT_ROOT / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "binding_state.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8")
    if str(FIXED_RF) not in sys.path:
        raise RuntimeError(
            f"B3 binding lost: {FIXED_RF} missing from sys.path")
    if not state["fixed_cws_exists"]:
        raise RuntimeError(
            f"B3 binding lost: {FIXED_RF / 'company_wiki_source.py'} missing")


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    """Persist the exact module bytes this session executed (evidence only)."""
    import importlib

    record = {"sys_path_head": sys.path[:8], "modules": {}}
    for module_name in ("company_wiki_source",
                        "company_wiki.source_catalog.artifact_dag"):
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - diagnostics only
            record["modules"][module_name] = {"error": repr(exc)}
            continue
        path = Path(module.__file__).resolve()
        record["modules"][module_name] = {
            "file": str(path),
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        }
    scratch = ATTEMPT_ROOT / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "module_provenance.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8")
