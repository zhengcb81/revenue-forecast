"""Negative semantics: missing/duplicate sources, identity, period, conflict and staleness."""
from __future__ import annotations

import pytest

from rf_verified_scope import fixtures as fx
from rf_verified_scope.test_golden_contract import compare


def error_code(exc):
    return exc.value.code


def build(build_env, tmp_path, **changes):
    return build_env(tmp_path, **changes)


def test_missing_source_snapshot_is_a_named_absence(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    rows = fx.witnesses()
    rows[0] = fx.witness("reporting_entity", snapshot_id="SNAP-NOT-REGISTERED")
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=fx.PublicOnlyCatalog(fx.side("R-OLD")),
                            subject_resolver=None,
                            evidence=fx.evidence("R-OLD", source_witnesses=rows))
    assert error_code(error) == "scope_source_missing"
    assert build_env is not None  # helper is available; no production state was touched


def test_absent_required_source_role_is_a_named_absence(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    rows = [row for row in fx.witnesses() if row["role"] != "fiscal_calendar"]
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=fx.PublicOnlyCatalog(fx.side("R-OLD")),
                            subject_resolver=None,
                            evidence=fx.evidence("R-OLD", source_witnesses=rows))
    assert error_code(error) == "scope_source_missing"


def test_duplicate_source_witness_is_refused(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    rows = fx.witnesses() + [fx.witness("revenue_perimeter")]
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=fx.PublicOnlyCatalog(fx.side("R-OLD")),
                            subject_resolver=None,
                            evidence=fx.evidence("R-OLD", source_witnesses=rows))
    assert error_code(error) == "scope_duplicate_source"


def test_witness_that_is_not_in_its_exact_captured_source_is_refused(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    rows = fx.witnesses()
    rows[0] = fx.witness("reporting_entity", excerpt="A quoted sentence never captured.")
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=fx.PublicOnlyCatalog(fx.side("R-OLD")),
                            subject_resolver=None,
                            evidence=fx.evidence("R-OLD", source_witnesses=rows))
    assert error_code(error) == "scope_evidence_invalid"


def test_identity_mismatch_between_report_and_verified_subject_is_refused(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding
    from report_catalog_subject_resolver import FrozenSubjectResolver, validate_subject_snapshot

    env = build_env(tmp_path)
    payload = fx.evidence("R-OLD", analysis_subject_id="SUBJ-OTHER")
    resolver = FrozenSubjectResolver([validate_subject_snapshot(
        fx.subject_snapshot(subject_id=env["left"]["analysis_subject_id"]))])
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=env["catalog"], subject_resolver=resolver, evidence=payload)
    assert error_code(error) == "scope_identity_mismatch"


def test_period_mismatch_marks_both_sides_uncovered(build_env, tmp_path):
    # Coordinates for later years are valid evidence, but they do not bind the
    # two periods actually compared. Coverage must fail by explicit public key.
    coords = [fx.coordinate(2027, period_start="2027-01-01", period_end="2027-12-31"),
              fx.coordinate(2028, period_start="2028-01-01", period_end="2028-12-31")]
    env = build_env(tmp_path, left_coordinates=coords, right_coordinates=coords)
    result = compare(env)
    for row in result["comparison"]["metrics"]:
        assert row["comparable"] is False and row["delta"] is None
        assert "left_scope_coordinate_not_covered" in row["reasons"]
        assert "right_scope_coordinate_not_covered" in row["reasons"]


def test_conflicting_scope_for_the_same_report_coordinate_is_refused(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    env = build_env(tmp_path, accounting_basis="IFRS")
    conflicting = build_scope_binding(
        catalog=env["catalog"], subject_resolver=env["resolver"],
        evidence=fx.evidence("R-OLD", accounting_basis="US GAAP",
                             coordinates=env["left"]["covered_coordinates"],
                             source_witnesses=env["left"]["source_witnesses"]))
    with pytest.raises(ScopeContractError) as error:
        env["store"].append(conflicting)
    assert error_code(error) == "scope_binding_conflict"


def test_idempotent_append_returns_the_same_binding(build_env, tmp_path):
    env = build_env(tmp_path)
    result = env["store"].append(env["left"])
    assert result["status"] == "already_present"
    assert result["binding"] == env["left"]
    assert len(env["store"].read()[0]) == 2


def test_tampered_binding_is_stale_when_checked_against_public_readers(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, validate_scope_binding

    env = build_env(tmp_path)
    tampered = dict(env["left"], accounting_basis="CAS")
    with pytest.raises(ScopeContractError) as error:
        validate_scope_binding(tampered, catalog=env["catalog"],
                               subject_resolver=env["resolver"])
    assert error_code(error) in {"scope_binding_invalid", "scope_binding_stale"}


def test_wrong_report_binding_is_refused_without_fallback(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError

    env = build_env(tmp_path)
    request = dict(env["request"], left_binding_id=env["right"]["binding_id"])
    from report_catalog_verified_compare import compare_verified_scope
    with pytest.raises(ScopeContractError) as error:
        compare_verified_scope(request, catalog=env["catalog"],
                               subject_resolver=env["resolver"], store=env["store"])
    assert error_code(error) == "scope_binding_not_found"


def test_unavailable_scope_view_creates_no_owner_state(tmp_path):
    from report_catalog_scope_binding import ScopeBindingStore, list_scope_bindings
    from report_catalog_subject_resolver import FrozenSubjectResolver, validate_subject_snapshot

    catalog = fx.PublicOnlyCatalog(fx.side("R-OLD"))
    store = ScopeBindingStore(tmp_path / "fresh-owner-data")
    resolver = FrozenSubjectResolver([validate_subject_snapshot(fx.subject_snapshot())])
    view = list_scope_bindings(catalog=catalog, store=store, subject_resolver=resolver,
                               report_id="R-OLD")
    assert view["scope_view"]["state"] == "unavailable"
    assert view["scope_view"]["missing_reason"] == "comparison_scope_binding_absent"
    assert not store.path.exists()
    assert catalog.calls == [("get_report", "R-OLD")]


@pytest.mark.parametrize("field", [
    "accounting_basis", "fiscal_year_end", "segment_ids", "covered_coordinates",
    "source_witnesses", "verified_at",
])
def test_every_explicit_scope_field_is_required(build_env, tmp_path, field):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    env = build_env(tmp_path)
    payload = fx.evidence("R-OLD", source_witnesses=env["left"]["source_witnesses"])
    payload.pop(field)
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=env["catalog"], subject_resolver=env["resolver"],
                            evidence=payload)
    assert error.value.code == "scope_evidence_invalid", field


def test_fy_period_end_must_match_the_declared_calendar(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    payload = fx.evidence(
        "R-OLD", fiscal_year_end="06-30",
        coordinates=[fx.coordinate(2025, period_start="2025-01-01",
                                   period_end="2025-12-31")])
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=fx.PublicOnlyCatalog(fx.side("R-OLD")),
                            subject_resolver=None, evidence=payload)
    assert error.value.code == "scope_period_calendar_mismatch"


def test_fy_coordinate_without_dates_is_explicit_fy_granularity(build_env, tmp_path):
    env = build_env(tmp_path, explicit_dates=False)
    assert all(row["period_start"] is None and row["period_end"] is None
               for row in env["left"]["covered_coordinates"])
    result = compare(env)
    assert all(row["comparable"] for row in result["comparison"]["metrics"])
    assert all(row["delta"] is not None for row in result["comparison"]["metrics"])


def test_report_anchor_mismatch_is_refused_before_any_write(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    env = build_env(tmp_path)
    payload = fx.evidence("R-OLD", source_witnesses=env["left"]["source_witnesses"])
    payload["expected_input_sha256"] = fx.sha("a-different-input-artifact")
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=env["catalog"], subject_resolver=env["resolver"],
                            evidence=payload)
    assert error.value.code == "scope_anchor_mismatch"
    assert len(env["store"].read()[0]) == 2


def test_scope_store_chain_corruption_is_named(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError

    env = build_env(tmp_path)
    raw = env["store"].path.read_bytes()
    env["store"].path.write_bytes(raw[:-1])
    with pytest.raises(ScopeContractError) as error:
        env["store"].read()
    assert error.value.code == "scope_store_invalid"


def test_busy_scope_store_is_refused(build_env, tmp_path):
    from owner_file_lock import OwnerFileLock
    from report_catalog_scope_binding import ScopeContractError

    env = build_env(tmp_path)
    lock = OwnerFileLock(env["store"].path.with_name(env["store"].path.name + ".lock"))
    assert lock.acquire()
    try:
        with pytest.raises(ScopeContractError) as error:
            env["store"].append(env["left"])
        assert error.value.code == "scope_store_busy"
    finally:
        lock.release()


def test_resolver_snapshot_must_match_the_exact_report_identity(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding
    from report_catalog_subject_resolver import validate_subject_snapshot

    class WrongResolver:
        def resolve(self, query):
            return validate_subject_snapshot(fx.subject_snapshot(entity_id="ENT-OTHER"))

    env = build_env(tmp_path)
    payload = fx.evidence("R-OLD", source_witnesses=env["left"]["source_witnesses"])
    with pytest.raises(ScopeContractError) as error:
        build_scope_binding(catalog=env["catalog"], subject_resolver=WrongResolver(),
                            evidence=payload)
    assert error.value.code == "scope_identity_mismatch"


def test_invalid_accounting_basis_or_calendar_is_not_defaulted(build_env, tmp_path):
    from report_catalog_scope_binding import ScopeContractError, build_scope_binding

    env = build_env(tmp_path)
    for mutation, code in (({"accounting_basis": "unknown"}, "scope_evidence_invalid"),
                           ({"fiscal_year_end": "02-30"}, "scope_evidence_invalid"),
                           ({"segment_ids": ["SEG-A", "SEG-A"]}, "scope_evidence_invalid"),
                           ({"verified_at": "2026-11-12"}, "scope_evidence_invalid")):
        payload = dict(fx.evidence("R-OLD", source_witnesses=env["left"]["source_witnesses"]),
                       **mutation)
        with pytest.raises(ScopeContractError) as error:
            build_scope_binding(catalog=env["catalog"], subject_resolver=env["resolver"],
                                evidence=payload)
        assert error.value.code == code, mutation
