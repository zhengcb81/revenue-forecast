"""Provenance probe for the REM-12 vacuity run.

Records WHICH `company_wiki_source` bytes the vacuity harness actually loads,
and asserts they are the I-05-B attempt's frozen checkout copy (`A55602E5…`)
rather than production (`225FECDD…`).  Without this assertion a green result
from the adjacent carrier proves nothing — which is exactly the defect
REM-12 reports.

The module is bound here by explicit file location so that the carrier file
(which keeps its original `sys.path`-based import) receives these bytes.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

STALE_ISO = Path(
    "C:/Users/郑曾波/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs/"
    "I-05-B/a20260919-01/iso/checkout_scripts/company_wiki_source.py")
STALE_SHA256 = "A55602E5C2881E64F888F39A224F82DB918190009DF3901497A5CD1E252E94AE"
PRODUCTION_SHA256 = "225FECDD7E48938A97C68724318F0860602A4B86A8D9E834A257243480094294"

_STALE_ISO_ROOT = STALE_ISO.parent
for _entry in (str(_STALE_ISO_ROOT),
               "C:/Users/郑曾波/Projects/company-wiki/src"):
    while _entry in sys.path:
        sys.path.remove(_entry)
    sys.path.insert(0, _entry)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("company_wiki_source", STALE_ISO)
_module = importlib.util.module_from_spec(_spec)
sys.modules["company_wiki_source"] = _module
_spec.loader.exec_module(_module)

BOUND_FILE = str(Path(_module.__file__).resolve())
BOUND_SHA256 = hashlib.sha256(
    Path(_module.__file__).resolve().read_bytes()).hexdigest().upper()


def test_vacuity_harness_binds_the_stale_i05b_bytes():
    """The harness must genuinely load the stale bytes for the proof to hold."""
    assert BOUND_SHA256 == STALE_SHA256
    assert BOUND_SHA256 != PRODUCTION_SHA256


def test_record_bound_bytes_for_evidence():
    out = Path(__file__).resolve().parents[1] / "bound_bytes.json"
    out.write_text(json.dumps({
        "bound_file": BOUND_FILE,
        "bound_sha256": BOUND_SHA256,
        "stale_i05b_iso_sha256": STALE_SHA256,
        "production_sha256": PRODUCTION_SHA256,
        "is_stale": BOUND_SHA256 == STALE_SHA256,
    }, indent=2), encoding="utf-8")
    assert out.is_file()
