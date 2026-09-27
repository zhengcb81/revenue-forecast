"""ZR-703 acceptance tests: schema drift cleanup (REV-01/03 docs
consistency) + migration allowlist gate + generator schema_version pin.

  C1  "schema 3.6" no longer appears as a hardcoded version in
      generate_input_template / fix_hashes / lint_input docstrings
      (the version is now referenced dynamically via
      FORECAST_SCHEMA_VERSION or omitted).
  C2  migration allowlist consistency: every version in
      SUPPORTED_FORECAST_SCHEMA_VERSIONS has a SCHEMA_EMIT_ENGINES entry
      (a non-empty engine set); FORECAST_SCHEMA_VERSION is in
      SUPPORTED_FORECAST_SCHEMA_VERSIONS.
  C3  generator output pin: build_template().schema_version ==
      FORECAST_SCHEMA_VERSION; a fully-valid document's
      prepare_forecast(mode="draft").schema_version == same.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from contracts.constants import (  # noqa: E402
    FORECAST_SCHEMA_VERSION,
    SUPPORTED_FORECAST_SCHEMA_VERSIONS,
)
from generate_input_template import build_template  # noqa: E402
from revenue_forecast import prepare_forecast  # noqa: E402
from schema_compatibility import SCHEMA_EMIT_ENGINES  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — hardcoded "schema 3.6" no longer in docstrings
# ---------------------------------------------------------------------------

_SCRIPTS = ROOT / "scripts"
_HARDCODE_PATTERN = "schema 3.6"


def test_c1_no_hardcoded_schema_version_in_docs():
    for name in ("generate_input_template.py", "fix_hashes.py", "lint_input.py"):
        source = (_SCRIPTS / name).read_text(encoding="utf-8")
        assert _HARDCODE_PATTERN not in source, (
            f"{name} still contains '{_HARDCODE_PATTERN}'"
        )


# ---------------------------------------------------------------------------
# C2 — migration allowlist consistency
# ---------------------------------------------------------------------------


def test_c2_supported_schema_versions_have_engine_entries():
    missing = [
        version
        for version in SUPPORTED_FORECAST_SCHEMA_VERSIONS
        if version not in SCHEMA_EMIT_ENGINES
        or not SCHEMA_EMIT_ENGINES[version]
    ]
    assert missing == []


def test_c2_current_schema_version_is_supported():
    assert FORECAST_SCHEMA_VERSION in SUPPORTED_FORECAST_SCHEMA_VERSIONS


# ---------------------------------------------------------------------------
# C3 — generator output schema_version pin
# ---------------------------------------------------------------------------


def test_c3_template_schema_version_matches_constant():
    template = build_template("X", 2025, [2026], "CNY", "百万元", ["主营业务"])
    assert template["schema_version"] == FORECAST_SCHEMA_VERSION


def test_c3_engine_output_schema_version_matches_constant():
    sys.path.insert(0, str(ROOT / "tests"))
    from test_recognition_bridge import forecast_document  # noqa: E402

    result = prepare_forecast(forecast_document(), mode="draft")
    assert result["schema_version"] == FORECAST_SCHEMA_VERSION


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
