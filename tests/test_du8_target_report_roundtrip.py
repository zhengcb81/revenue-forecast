"""DU8 C-node: public entry round trip for the single comparison owner.

For each of three synthetic complete models (legacy annual, typed annual level,
typed YoY growth) this file drives the *real* RF command line
(``scripts/revenue_forecast.py``) in an isolated registry, then re-enters the
published artifacts through ``validate_forecast_output`` and
``render_markdown``. It then tampers each comparison field of the published
JSON and requires the round trip to refuse it.

All models are synthetic fixtures built from the repository's own test
documents. Nothing here is evidence about a real company, and no scope or
quality claim is made beyond "the public entry point accepts, validates and
renders this synthetic model consistently".
"""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from research.target_comparison import (  # noqa: E402
    LEGACY_COMPARISON_ROW_KEYS,
    compare_target_measurement,
)
from du8_models import (  # noqa: E402
    growth_model,
    legacy_annual_model,
    legacy_approximately_model,
    legacy_cumulative_model,
    typed_level_model,
)

PYTHON = [sys.executable, "-X", "utf8", "-B"]


def _run_cli(data: dict, tmp: Path, *, version: str) -> tuple[Path, Path, subprocess.CompletedProcess]:
    """Run validate + compute through the real CLI in an isolated registry."""
    input_path = tmp / "input.json"
    input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    out_json = tmp / "forecast.json"
    out_md = tmp / "forecast.md"
    environment = dict(os.environ)
    environment.update(
        PYTHONUTF8="1",
        PYTHONDONTWRITEBYTECODE="1",
        REVENUE_PUBLICATION_REGISTRY=str(tmp / "registry" / "publications.jsonl"),
    )
    validate = subprocess.run(
        [*PYTHON, str(ROOT / "scripts/revenue_forecast.py"), str(input_path), "--validate-only"],
        cwd=ROOT, env=environment, capture_output=True, encoding="utf-8", timeout=180, check=False,
    )
    assert validate.returncode == 0, validate.stderr
    compute = subprocess.run(
        [*PYTHON, str(ROOT / "scripts/revenue_forecast.py"), str(input_path),
         "--output", str(out_json), "--markdown", str(out_md)],
        cwd=ROOT, env=environment, capture_output=True, encoding="utf-8", timeout=180, check=False,
    )
    return out_json, out_md, compute


def _reseal(result: dict) -> dict:
    out = copy.deepcopy(result)
    out["result_sha256"] = canonical_sha256(
        {key: value for key, value in out.items() if key != "result_sha256"}
    )
    return out


MODELS = {
    "legacy_annual": legacy_annual_model,
    "legacy_approximately": legacy_approximately_model,
    "legacy_cumulative": legacy_cumulative_model,
    "typed_level": typed_level_model,
    "typed_growth": growth_model,
}


@pytest.mark.parametrize("name", sorted(MODELS))
def test_public_entry_round_trip_validates_and_renders(tmp_path, name):
    from revenue_report import render_markdown, validate_forecast_output

    data = MODELS[name]()
    out_json, out_md, compute = _run_cli(data, tmp_path, version=f"du8-{name}-v1")
    assert compute.returncode == 0, compute.stderr
    assert out_json.is_file() and out_md.is_file()

    result = json.loads(out_json.read_text(encoding="utf-8"))
    # The published artifact must survive its own validator.
    validate_forecast_output(result)
    markdown = render_markdown(result)
    assert markdown.strip()

    targets = result["management_target_coverage"]["targets"]
    assert targets, "the synthetic model must publish at least one target"
    for target in targets:
        comparisons = target["scenario_comparison"]
        assert comparisons, f"{name}: target {target['target_id']} published no comparison"
        assert comparisons == compare_target_measurement(target, result)

    # The Markdown must disclose each target statement, not just the numbers.
    for target in targets:
        assert target["target_id"] in markdown or target["statement"].split(".")[0][:20] in markdown


@pytest.mark.parametrize("name", sorted(MODELS))
def test_published_comparison_is_recomputed_identically_from_the_input(tmp_path, name):
    """run_forecast on the same input must reproduce the CLI's artifact body."""
    data = MODELS[name]()
    out_json, _, compute = _run_cli(data, tmp_path, version=f"du8-{name}-v2")
    assert compute.returncode == 0, compute.stderr
    published = json.loads(out_json.read_text(encoding="utf-8"))
    recomputed = run_forecast(data)
    assert (
        published["management_target_coverage"]
        == recomputed["management_target_coverage"]
    )


@pytest.mark.parametrize("name", sorted(MODELS))
@pytest.mark.parametrize(
    "field",
    [
        "modeled_value",
        "target_value",
        "attainment_ratio",
        "meets_target",
        "measurement_periods",
        "modeled_period_values",
    ],
)
def test_tampered_published_comparison_field_is_refused(tmp_path, name, field):
    from revenue_report import validate_forecast_output

    data = MODELS[name]()
    result = run_forecast(data)
    target = result["management_target_coverage"]["targets"][0]
    scenario = sorted(target["scenario_comparison"])[0]
    row = target["scenario_comparison"][scenario]
    if field not in row:
        pytest.skip(f"{name}: {field} is not part of this published row shape")

    tampered = _reseal(result)
    row = tampered["management_target_coverage"]["targets"][0]["scenario_comparison"][scenario]
    if field == "modeled_value":
        row[field] = float(row[field]) + 1.0
    elif field == "target_value":
        row[field] = float(row[field]) + 1.0
    elif field == "attainment_ratio":
        row[field] = 99.0
    elif field == "meets_target":
        row[field] = not row[field]
    elif field == "measurement_periods":
        row[field] = ["FY1999"]
    elif field == "modeled_period_values":
        row[field] = {key: 0.0 for key in row[field]}
    with pytest.raises(ForecastInputError):
        validate_forecast_output(tampered)


@pytest.mark.parametrize("name", sorted(MODELS))
def test_tampered_comparison_is_also_refused_by_input_bound_validation(tmp_path, name):
    """``validate_published_forecast`` re-derives from the input and refuses too."""
    from revenue_report import validate_published_forecast

    data = MODELS[name]()
    result = run_forecast(data)
    tampered = _reseal(result)
    row = tampered["management_target_coverage"]["targets"][0]["scenario_comparison"]
    first = sorted(row)[0]
    row[first]["modeled_value"] = float(row[first]["modeled_value"]) + 7.0
    with pytest.raises(ForecastInputError):
        validate_published_forecast(tampered, data)


def test_legacy_row_shape_is_frozen_through_the_public_entry(tmp_path):
    data = legacy_annual_model()
    out_json, _, compute = _run_cli(data, tmp_path, version="du8-legacy-shape-v1")
    assert compute.returncode == 0, compute.stderr
    result = json.loads(out_json.read_text(encoding="utf-8"))
    for comparison in result["management_target_coverage"]["targets"][0][
        "scenario_comparison"
    ].values():
        assert set(comparison) == LEGACY_COMPARISON_ROW_KEYS


def test_failed_run_leaves_the_isolated_registry_untouched(tmp_path):
    """A refused model must not write a publication record."""
    from du8_models import broken_model

    registry = tmp_path / "registry" / "publications.jsonl"
    registry.parent.mkdir(parents=True, exist_ok=True)
    sentinel = "pre-existing-sentinel\n"
    registry.write_text(sentinel, encoding="utf-8")

    data = broken_model()
    input_path = tmp_path / "broken.json"
    input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    environment = dict(os.environ)
    environment.update(
        PYTHONUTF8="1",
        PYTHONDONTWRITEBYTECODE="1",
        REVENUE_PUBLICATION_REGISTRY=str(registry),
    )
    completed = subprocess.run(
        [*PYTHON, str(ROOT / "scripts/revenue_forecast.py"), str(input_path),
         "--output", str(tmp_path / "out.json"), "--markdown", str(tmp_path / "out.md")],
        cwd=ROOT, env=environment, capture_output=True, encoding="utf-8", timeout=180, check=False,
    )
    assert completed.returncode != 0
    assert registry.read_text(encoding="utf-8") == sentinel
    assert not (tmp_path / "out.json").exists()


if __name__ == "__main__":
    unittest.main()
