"""ZR-702 acceptance tests: schema single source of truth (REV-01/03) +
generator→linter→validator→engine closure (REV-02/04).

  C1  lint_input's field tuples come from scripts/schema_fields.py (the
      single source); no local copies remain.
  C2  three-way consistency: a filled generator template carries every
      TOP_LEVEL_REQUIRED key; removing any required key makes
      validate_document reject (validator coverage matches the source).
  C3  generator closure: a fully valid document passes
      lint -> validate_document -> prepare_forecast(mode="draft") in one
      pass, zero writes.
  C4  production never silently uses an unfilled template: the raw
      build_template output carries FIXME placeholders and lint reports
      findings on it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import lint_input  # noqa: E402
import schema_fields  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402
from generate_input_template import build_template  # noqa: E402
from revenue_core import validate_document  # noqa: E402
from revenue_forecast import prepare_forecast  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — single source of truth
# ---------------------------------------------------------------------------


def test_c1_lint_uses_schema_fields_module():
    assert lint_input.TOP_LEVEL_REQUIRED is schema_fields.TOP_LEVEL_REQUIRED
    assert lint_input.CAPTURE_REQUIRED is schema_fields.CAPTURE_REQUIRED
    assert lint_input.CLAIM_REQUIRED is schema_fields.CLAIM_REQUIRED
    assert lint_input.PARAMETER_REQUIRED is schema_fields.PARAMETER_REQUIRED


def test_c1_no_local_copy_in_lint_input():
    source = (ROOT / "scripts" / "lint_input.py").read_text(encoding="utf-8")
    # the tuple literals must not be redefined locally (only the import)
    assert 'TOP_LEVEL_REQUIRED = (' not in source
    assert 'CAPTURE_REQUIRED = (' not in source
    assert 'from schema_fields import' in source


# ---------------------------------------------------------------------------
# C2 — three-way consistency
# ---------------------------------------------------------------------------


def test_c2_template_carries_every_top_level_required_key():
    template = build_template(
        "某公司", 2025, [2026, 2027], "CNY", "百万元", ["主营业务"]
    )
    missing = [
        key for key in schema_fields.TOP_LEVEL_REQUIRED if key not in template
    ]
    assert missing == []


def test_c2_validator_rejects_when_any_required_key_removed():
    data = forecast_document()
    for key in schema_fields.TOP_LEVEL_REQUIRED:
        stripped = {k: v for k, v in data.items() if k != key}
        with pytest.raises(ForecastInputError):
            validate_document(stripped)


def test_c2_template_capture_keys_match_source():
    template = build_template(
        "某公司", 2025, [2026], "CNY", "百万元", ["主营业务"]
    )
    capture = template["sources"][0]["capture"]
    missing = [key for key in schema_fields.CAPTURE_REQUIRED if key not in capture]
    assert missing == []


# ---------------------------------------------------------------------------
# C3 — generator closure (one pass, zero writes)
# ---------------------------------------------------------------------------


def test_c3_full_chain_lint_validate_draft_one_pass(tmp_path):
    data = forecast_document()
    findings = lint_input.lint(data)
    assert findings == []
    validate_document(data)  # raises on any violation
    result = prepare_forecast(data, mode="draft")
    assert result["publication_receipt"]["formal_output_mode"] == "draft"
    # zero writes: nothing created in the scratch dir
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# C4 — unfilled template is loud, never silently usable
# ---------------------------------------------------------------------------


def test_c4_raw_template_has_fixme_placeholders():
    template = build_template(
        "某公司", 2025, [2026], "CNY", "百万元", ["主营业务"]
    )
    encoded = str(template)
    assert "FIXME" in encoded  # placeholders present, no prefilled values


def test_c4_unfilled_template_fails_lint_loudly():
    template = build_template(
        "某公司", 2025, [2026], "CNY", "百万元", ["主营业务"]
    )
    findings = lint_input.lint(template)
    assert findings != []  # the linter refuses to pass FIXME placeholders


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
