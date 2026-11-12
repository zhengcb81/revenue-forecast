"""Golden/parameterized contract: standards, fiscal calendars and multi-segment scopes."""
from __future__ import annotations

import json

import pytest

from rf_verified_scope import fixtures as fx


def compare(env):
    from report_catalog_verified_compare import compare_verified_scope

    return compare_verified_scope(env["request"], catalog=env["catalog"],
                                  subject_resolver=env["resolver"], store=env["store"])


@pytest.mark.parametrize("accounting_basis", ["IFRS", "US GAAP"])
@pytest.mark.parametrize("fiscal_year_end", ["06-30", "12-31"])
@pytest.mark.parametrize("segment_ids", [["SEG-A"], ["SEG-A", "SEG-B", "SEG-C"]])
def test_golden_scope_binds_every_public_dimension(build_env, tmp_path, accounting_basis,
                                                   fiscal_year_end, segment_ids):
    env = build_env(tmp_path, accounting_basis=accounting_basis,
                    fiscal_year_end=fiscal_year_end, segment_ids=segment_ids)
    left, right = env["left"], env["right"]
    for binding in (left, right):
        assert binding["accounting_basis"] == accounting_basis
        assert binding["fiscal_year_end"] == fiscal_year_end
        assert binding["segment_ids"] == segment_ids
        assert binding["measure_kind"] == "group_reported_total_as_disclosed"
        assert binding["currency"] == "USD" and binding["unit"] == "currency"
        assert binding["scale"] == 6 and binding["basis"] == "consolidated"
        assert binding["analysis_subject_revision"] == 3
        assert [row["period_end"] for row in binding["covered_coordinates"]] == [
            fx.fy_dates(year, fiscal_year_end)[1] for year in (2025, 2026)]
    result = compare(env)
    assert result["schema_version"] == "rf-verified-scope-comparison/1"
    assert result["catalog_revisions"] == {"left": "REV-R-OLD", "right": "REV-R-NEW"}
    assert len(result["comparison"]["metrics"]) == 2
    assert [row["delta"]["value"] for row in result["comparison"]["metrics"]] == [
        "3.000000", "3.000000"]
    assert all(row["comparable"] and not row["reasons"] for row in result["comparison"]["metrics"])
    scope = result["comparison"]["scope_resolution"]
    assert scope["method"] == "current_verified_scope"
    assert scope["left_binding"]["binding_id"] == left["binding_id"]
    assert scope["right_binding"]["binding_id"] == right["binding_id"]


def test_binding_id_reproduces_full_public_dto_without_hidden_clock(build_env, tmp_path):
    from contracts.evidence import canonical_sha256
    from report_catalog_scope_binding import validate_scope_binding

    env = build_env(tmp_path)
    binding = validate_scope_binding(env["left"], catalog=env["catalog"],
                                     subject_resolver=env["resolver"])
    assert binding["binding_id"] == "rfscope1-" + canonical_sha256(
        {key: value for key, value in binding.items() if key != "binding_id"})
    assert binding["verified_at"] == fx.VERIFIED_AT
    assert binding == env["left"]


def test_h1_coordinates_are_not_defaulted_to_fy(build_env, tmp_path):
    env = build_env(tmp_path, period_kind="H1", fiscal_year_end="06-30")
    assert {row["period_kind"] for row in env["left"]["covered_coordinates"]} == {"H1"}
    result = compare(env)
    assert [row["delta"]["value"] for row in result["comparison"]["metrics"]] == [
        "3.000000", "3.000000"]
    assert all(row["left"]["number"]["period_end"].endswith("-06-30")
               for row in result["comparison"]["metrics"])


def test_verified_scope_resolves_a_legacy_unknown_original_subject(build_env, tmp_path):
    """Current verified scope may resolve an old unknown subject without relabelling rows."""
    env = build_env(tmp_path, left_subject=None, right_subject="SUBJ-1",
                    verified_subject="SUBJ-1")
    result = compare(env)
    assert all(row["comparable"] for row in result["comparison"]["metrics"])
    assert [row["delta"]["value"] for row in result["comparison"]["metrics"]] == [
        "3.000000", "3.000000"]
    # Canonical original rows stay untouched.
    assert all(row["left"]["number"]["analysis_subject_id"] is None
               for row in result["comparison"]["metrics"])


def test_subject_revision_mismatch_stays_incomparable(build_env, tmp_path):
    env = build_env(tmp_path, right_revision=4)
    result = compare(env)
    for row in result["comparison"]["metrics"]:
        assert row["comparable"] is False and row["delta"] is None
        assert "scope_analysis_subject_revision_mismatch" in row["reasons"]


def test_full_candidate_result_is_never_row_or_byte_truncated(build_env, tmp_path):
    years = tuple(range(1900, 2500))
    env = build_env(tmp_path, years=years)
    result = compare(env)
    assert len(result["comparison"]["metrics"]) == len(years)
    assert all(row["delta"] is not None for row in result["comparison"]["metrics"])
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
    assert len(encoded) > 1_000_000
    assert len(result["comparison"]["scope_resolution"]["left_binding"]["covered_coordinates"]) == len(years)


def test_multiple_segment_ids_are_preserved_in_comparison_scope(build_env, tmp_path):
    segments = [f"SEG-{index}" for index in range(24)]
    env = build_env(tmp_path, segment_ids=segments)
    result = compare(env)
    assert result["comparison"]["scope_resolution"]["left_binding"]["segment_ids"] == segments
    assert result["comparison"]["scope_resolution"]["right_binding"]["segment_ids"] == segments
