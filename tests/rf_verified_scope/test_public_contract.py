"""A-layer: public entrypoints, DTO reproducibility and dependency isolation."""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest

from rf_verified_scope import fixtures as fx

ROOT = Path(__file__).resolve().parents[2]
OWNER_MODULES = (
    "report_catalog_subject_resolver",
    "report_catalog_scope_binding",
    "report_catalog_verified_compare",
    "report_catalog_verified_compare_cli",
)
PRIVATE_CATALOG_NAMES = {
    "_index", "_entries", "_exact_report", "_public_report", "_read_json",
    "_read_artifact", "_clean_id", "_assert_pathless", "_validate_report_artifact",
    "_compare_pair", "_identity_reasons", "_load_exact", "_json", "_index_entries",
}


def test_b2_public_scope_entrypoints_are_available():
    """Capability RED: current main has no public scope/subject/verified-compare owner."""
    for name in OWNER_MODULES:
        assert importlib.util.find_spec(name) is not None, (
            f"public B2 owner entrypoint {name} is missing from the delivered runtime")


def test_public_subject_dto_is_explicit_and_reproducible():
    from contracts.evidence import canonical_sha256
    from report_catalog_subject_resolver import validate_subject_snapshot

    snapshot = validate_subject_snapshot(fx.subject_snapshot())
    public = snapshot.to_public_dict()
    assert public["schema_version"] == "rf-report-subject-snapshot/1"
    assert public["memberships"] == [{"entity_id": "ENT-1", "role": "primary_issuer"}]
    assert snapshot.snapshot_sha256 == canonical_sha256(public)
    assert snapshot.snapshot_sha256.startswith("rf") is False  # a hash, not an invented identity
    assert len(snapshot.snapshot_sha256) == 64


@pytest.mark.parametrize("mutation,code", [
    ({"schema_version": "rf-report-subject-snapshot/2"}, "subject_snapshot_invalid"),
    ({"scope_kind": ""}, "subject_snapshot_invalid"),
    ({"perimeter_coverage": "guessed"}, "subject_snapshot_invalid"),
    ({"analysis_subject_revision": True}, "subject_snapshot_invalid"),
    ({"memberships": []}, "subject_snapshot_invalid"),
    ({"memberships": [{"entity_id": "ENT-9", "role": "primary_issuer"}]}, "subject_snapshot_invalid"),
])
def test_public_subject_dto_refuses_unknown_or_forged_authority(mutation, code):
    from report_catalog_subject_resolver import ScopeContractError, validate_subject_snapshot

    value = dict(fx.subject_snapshot(), **mutation)
    with pytest.raises(ScopeContractError) as error:
        validate_subject_snapshot(value)
    assert error.value.code == code


def test_frozen_subject_resolver_uses_only_public_fixture(tmp_path):
    from report_catalog_subject_resolver import (
        FrozenSubjectResolver, ScopeContractError, SubjectQuery,
    )

    path = tmp_path / "subjects.json"
    fx.write_subject_fixture(path, fx.subject_snapshot(),
                             fx.subject_snapshot(subject_id="SUBJ-2"))
    resolver = FrozenSubjectResolver.from_public_fixture(path)
    query = SubjectQuery("ENT-1", "LST-1", "SUBJ-2", 3)
    assert resolver.resolve(query).analysis_subject_id == "SUBJ-2"
    assert resolver.resolve(query) == resolver.resolve(query)
    with pytest.raises(ScopeContractError) as error:
        resolver.resolve(SubjectQuery("ENT-1", "LST-1", "SUBJ-9", 3))
    assert error.value.code == "subject_unavailable"

    other = fx.subject_snapshot(subject_id="SUBJ-2")
    other["evidence_sha256"] = fx.sha("different-authority-bytes")
    ambiguous = tmp_path / "ambiguous.json"
    fx.write_subject_fixture(ambiguous, fx.subject_snapshot(subject_id="SUBJ-2"), other)
    with pytest.raises(ScopeContractError) as error:
        FrozenSubjectResolver.from_public_fixture(ambiguous).resolve(
            SubjectQuery("ENT-1", "LST-1", "SUBJ-2", 3))
    assert error.value.code == "subject_ambiguous"


def test_public_catalog_only_reads_through_owner_entrypoints(build_env, tmp_path):
    """Every catalog access is a declared public reader; no private fallback."""
    env = build_env(tmp_path)
    allowed = {"get_report", "get_run", "get_source_snapshot", "get_model",
               "get_calculation", "get_calculation_trace", "list_reports", "list_runs"}
    for name, argument in env["catalog"].calls:
        assert name in allowed, f"private/non-contract reader used: {name}"
        assert isinstance(argument, str) and argument
    assert ("get_source_snapshot", "R-OLD/SNAP-REPORTING-ENTITY") in env["catalog"].calls
    assert ("get_source_snapshot", "R-NEW/SNAP-FISCAL-CALENDAR") in env["catalog"].calls


def test_owner_modules_import_no_catalog_privates_or_neighbour_stores():
    """AST boundary check: no private catalog symbols and no neighbour stores."""
    for name in OWNER_MODULES:
        source = (ROOT / "scripts" / f"{name}.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        identifiers: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    identifiers.add(alias.name)
                    if node.module == "report_catalog":
                        assert not alias.name.startswith("_"), (
                            f"{name} imports catalog private {alias.name}")
                    assert not any(part in (node.module or "").lower() for part in
                                   ("stockwiki", "cwp")), (
                        f"{name} imports a neighbouring owner module: {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    identifiers.add(alias.name)
                    assert not any(part in alias.name.lower() for part in
                                   ("sqlite3", "stockwiki", "company_wiki_source", "cwp")), (
                        f"{name} imports a neighbouring private store: {alias.name}")
            if isinstance(node, ast.Name):
                identifiers.add(node.id)
            if isinstance(node, ast.Attribute):
                identifiers.add(node.attr)
                if node.attr.startswith("_"):
                    owner = node.value.id if isinstance(node.value, ast.Name) else ""
                    assert owner not in {"catalog", "store", "resolver", "subject"}, (
                        f"{name} reaches {owner}.{node.attr}")
        assert identifiers.isdisjoint(PRIVATE_CATALOG_NAMES), (
            f"{name} references private catalog symbols: "
            f"{sorted(identifiers.intersection(PRIVATE_CATALOG_NAMES))}")
