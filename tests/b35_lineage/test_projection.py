"""Meaningful controlled lineage checks; no production reads or writes."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from .fixtures import build, write, sha
from report_catalog import CatalogError
from publication_registry import canonical_sha256
from report_catalog_lineage import locator, public_pathless, snapshot_id


def trace(c):
    return c.get_calculation_trace(c.record["report_id"], "consolidated:base:2026")[
        "trace"
    ]


def test_reachable_graph_keeps_conditional_kind_and_exact_node_links(tmp_path):
    c = build(tmp_path)
    t = trace(c)
    assert t["state"] == "available" and t["missing_reasons"] == []
    assert c.strong_reads == 1
    assert {p["parameter_id"] for p in t["parameters"]} == {
        "composed",
        "observed",
        "assumed",
    }
    assert "unused-claim" not in {v["claim_id"] for v in t["claims"]}
    parent = next(b for b in t["bindings"] if b["node_id"].startswith("consolidated"))
    assert parent["parameter_ids"] == [] and parent["calculation_node_ids"] == [
        "segment:0:base:2026"
    ]
    params = {p["parameter_id"]: p for p in t["parameters"]}
    assert params["composed"]["input_parameter_ids"] == ["observed", "assumed"]
    assert (
        params["composed"]["kind"] == "derived_fact"
        and params["composed"]["is_conditional"] is True
    )
    assert (
        params["assumed"]["is_conditional"] is True
        and params["observed"]["is_conditional"] is False
    )
    assert params["observed"]["value"] == "10" and params["composed"]["value"] == "12"
    assert all(not n["inputs"][0]["provenance"]["source_refs"] for n in t["nodes"])
    pdf = next(s for s in t["sources"] if s["source_id"] == "PDF")
    web = next(s for s in t["sources"] if s["source_id"] == "WEB")
    assert pdf["source_ref"] is not None and pdf["source_snapshot_id"] is None
    assert web["source_ref"] is None and web["source_snapshot_id"].startswith(
        "rfsnap1-"
    )
    claim = next(q for q in t["claims"] if q["claim_id"] == "assumption-claim")
    assert (
        claim["support_type"] == "rationale_support"
        and claim["extracted_value"] is None
    )
    assert (
        claim["locator"]["value"] == "8" and claim["locator"]["page_kind"] == "physical"
    )


def test_snapshot_exact_original_bytes_untrusted_markup_and_old_registry_append(
    tmp_path,
):
    c = build(tmp_path)
    t = trace(c)
    token = next(
        s["source_snapshot_id"] for s in t["sources"] if s["source_id"] == "WEB"
    )
    with (c.folder / "registry/publications.jsonl").open("ab") as handle:
        handle.write(b"future valid additional registry entry\n")
    s = c.get_source_snapshot(c.record["report_id"], token)["source_snapshot"]
    assert "=" not in s["content_base64url"]
    decoded = base64.urlsafe_b64decode(
        s["content_base64url"] + "=" * (-len(s["content_base64url"]) % 4)
    )
    assert decoded == c.body and b"<script>" in decoded
    assert (
        hashlib.sha256(decoded).hexdigest() == s["content_sha256"]
        and len(decoded) == s["byte_size"]
    )
    assert s["source"]["original_format"] == "captured_markdown"


@pytest.mark.parametrize(
    "token",
    [
        "../source.markdown",
        "absolute_file",
        "not-a-snapshot-token",
        "rfsnap1-" + "f" * 64,
    ],
)
def test_snapshot_path_or_foreign_token_never_opens_source(
    tmp_path, monkeypatch, token
):
    c = build(tmp_path)
    if token == "absolute_file":
        # Explicit untrusted input; construct the current platform's rooted
        # syntax rather than relying on one host's drive or POSIX prefix.
        token = str(Path(tmp_path.anchor) / "home" / "snapshot-private")
    monkeypatch.setattr(
        "report_catalog_lineage.Sources._captured_body",
        lambda *_: pytest.fail("invalid token opened source"),
    )
    with pytest.raises(CatalogError) as e:
        c.get_source_snapshot(c.record["report_id"], token)
    assert e.value.code in {"invalid_id", "not_found"}


def test_snapshot_token_is_bound_to_report_not_just_body(tmp_path):
    c = build(tmp_path)
    source = c.result["input_document"]["sources"][0]
    original = snapshot_id(c.record, source)
    assert original != snapshot_id({**c.record, "report_id": "rf-another"}, source)
    c.record["report_id"] = "rf-another"
    with pytest.raises(CatalogError) as e:
        c.get_source_snapshot("rf-another", original)
    assert e.value.code == "not_found"


@pytest.mark.parametrize(
    "rel",
    [
        "execution/web-capture-q3-2026/source.markdown",
        "execution/web-capture-q3-2026/tool-response.json",
        "execution/company-release-capture-event.json",
        "execution/company-release-q3-2026-source.json",
    ],
)
def test_registered_source_byte_mutations_are_hard_errors(tmp_path, rel):
    c = build(tmp_path)
    p = c.folder / rel
    p.write_bytes(p.read_bytes() + b" ")
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code == "lineage_evidence_mismatch"


@pytest.mark.parametrize(
    "mutation",
    ["claim_hash", "capture_hash", "target", "period", "scenario", "value", "cycle"],
)
def test_declared_parameter_claim_or_input_contradiction_is_not_legacy(
    tmp_path, mutation
):
    c = build(tmp_path)
    if mutation == "claim_hash":
        c.result["evidence_claims"][0]["excerpt_sha256"] = "f" * 64
    elif mutation == "capture_hash":
        c.result["evidence_claims"][0]["capture_receipt_sha256"] = "f" * 64
    elif mutation == "target":
        c.result["evidence_claims"][0]["target_id"] = "assumed"
    elif mutation == "period":
        c.result["parameter_trace"][2]["period"] = "FY2027"
    elif mutation == "scenario":
        c.result["parameter_trace"][2]["scenario"] = "high"
    elif mutation == "value":
        c.result["parameter_trace"][2]["value"] = 13
    elif mutation == "cycle":
        c.result["parameter_trace"][2]["input_parameter_ids"] = ["composed"]
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code in {"lineage_evidence_mismatch", "lineage_limit_exceeded"}


def test_absent_original_binding_is_partial_and_never_fetches(tmp_path):
    c = build(tmp_path)
    c.run.pop("source_evidence")
    t = trace(c)
    assert t["state"] == "partial"
    web = next(s for s in t["sources"] if s["source_id"] == "WEB")
    assert (
        web["original_format"] == "unavailable"
        and web["source_ref"] is None
        and web["source_snapshot_id"] is None
    )
    assert any("source_original_unavailable" in x for x in t["missing_reasons"])


def test_legacy_no_immutable_anchors_never_fabricates_zero_hashes(tmp_path):
    c = build(tmp_path)
    c.record["input_sha256"] = None
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code == "lineage_unavailable"


def test_original_get_calculation_remains_unprojected_while_new_trace_closes_binding(
    tmp_path,
):
    c = build(tmp_path)
    old = c.get_calculation(c.record["report_id"], "segment:0:base:2026")
    assert old["calculation"]["trace_state"] == "partial"
    assert (
        old["calculation"]["inputs"][0]["provenance"]["missing_reason"]
        == "parameter_source_binding_not_projected"
    )
    assert trace(c)["state"] == "available"
    assert c.get_calculation(c.record["report_id"], "segment:0:base:2026") == old


@pytest.mark.parametrize(
    "raw",
    [
        "PDF printed8",
        "PDF physical8-9",
        "page8",
        "PDF physical0",
        "PDF physical10000",
        "PDF physical8 to 9",
        "PDF physical8 through 9",
        "PDF physical8 until 9",
        "PDF physical8 thru 9",
        "PDF physical8 and 9",
        "PDF physical8 & 9",
        "PDF physical8 / 9",
        "PDF physical8 ~ 9",
        "PDF physical8; 9",
        "PDF physical8\u22129",
        "PDF physical8\u20149",
        "PDF physical8; physical9",
        "PDF physical pages8 to 9",
        "PDF physical8; PDF physical9",
        "PDF physical8 - 9",
        "PDF physical8, 9",
        "PDF physical8 TO 9",
        "PDF physical8\u20139",
    ],
)
def test_unconfirmed_physical_page_is_never_guessed(raw):
    got = locator({"locator": raw, "excerpt": "controlled"})
    assert got["kind"] == "section" and got["page_kind"] is None


@pytest.mark.parametrize(
    "url",
    [
        "file:///tmp/a",
        "https://user:secret@example.com/a",
        "https://example.com:99999/a",
        "https://example.com\\private",
        "https:///missing-host",
    ],
)
def test_url_mask_does_not_waive_private_locator_checks(url):
    with pytest.raises(CatalogError):
        public_pathless({"url": url})


def test_private_paths_in_non_url_fields_still_reject(tmp_path):
    with pytest.raises(CatalogError):
        public_pathless(
            {"definition": str(Path(tmp_path.anchor) / "home" / "lineage-private")}
        )


def test_existing_native_engine_catalog_fixture_still_uses_strong_exact_validation(
    tmp_path,
):
    from test_report_catalog import _fixture

    c, _, _, run, attempt, report = _fixture(tmp_path)
    c.add_records(runs=[run], attempts=[attempt], reports=[report])
    before = c.file.read_bytes()
    t = c.get_calculation_trace("rf-one", "segment:0:base:2026")["trace"]
    assert t["state"] in {"partial", "available"} and t["bindings"][0]["parameter_ids"]
    assert c.file.read_bytes() == before
    (tmp_path / "input.json").write_text("{}")
    with pytest.raises(CatalogError) as e:
        c.get_calculation_trace("rf-one", "segment:0:base:2026")
    assert e.value.code == "artifact_sha_mismatch"


def test_source_body_bound_is_checked_before_read(tmp_path, monkeypatch):
    c = build(tmp_path, body=b"Annual revenue RMB 10 million.\n" + b"x" * 262145)
    from report_catalog_research_attempt import _Observation

    original = _Observation.read

    def bounded(self, path):
        assert path.name != "source.markdown", "oversized body was read"
        return original(self, path)

    monkeypatch.setattr(_Observation, "read", bounded)
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code == "lineage_limit_exceeded"


def test_source_seal_misbinding_does_not_fall_back_to_legacy(tmp_path):
    c = build(tmp_path)
    seal = json.loads(c.seal_path.read_bytes())
    seal["report_id"] = "rf-foreign"
    raw = write(c.seal_path, seal)
    c.run.update(
        artifact_revision=sha(raw), source_evidence=c.artifact_ref(c.seal_path)
    )
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code == "lineage_evidence_mismatch"


def test_source_reparse_point_is_refused_even_with_identical_bytes(tmp_path):
    c = build(tmp_path / "owner")
    original = c.folder / "execution/web-capture-q3-2026"
    saved = original.with_name("saved-capture")
    original.rename(saved)
    outside = tmp_path / "outside"
    outside.mkdir()
    for p in saved.iterdir():
        (outside / p.name).write_bytes(p.read_bytes())
    if sys.platform == "win32":

        def quote(value):
            return "'" + str(value).replace("'", "''") + "'"

        command = f"New-Item -ItemType Junction -Path {quote(original)} -Target {quote(outside)} | Out-Null"
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            check=True,
        )
    else:
        try:
            original.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            saved.rename(original)
            pytest.skip("host cannot create the isolated symbolic-link fixture")
    try:
        with pytest.raises(CatalogError) as e:
            trace(c)
        assert e.value.code == "research_path_forbidden"
    finally:
        if sys.platform == "win32":
            os.rmdir(original)
        else:
            original.unlink()
        saved.rename(original)
    assert (outside / "source.markdown").read_bytes() == c.body


def test_parameter_depth_is_bounded_without_recomputing_derived_values(tmp_path):
    c = build(tmp_path)
    rows = c.result["parameter_trace"]
    template = copy.deepcopy(rows[2])
    rows[2]["input_parameter_ids"] = ["deep0"]
    for i in range(34):
        p = copy.deepcopy(template)
        p.update(
            parameter_id=f"deep{i}",
            input_parameter_ids=[f"deep{i + 1}"] if i < 33 else ["observed"],
            formula="x0",
        )
        rows.append(p)
    with pytest.raises(CatalogError) as e:
        trace(c)
    assert e.value.code == "lineage_limit_exceeded"


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("reported_fact", False),
        ("management_guidance", True),
        ("analyst_assumption", True),
        ("scenario_stress", True),
    ],
)
def test_declared_conditional_kinds_propagate_through_derived_parameter(
    tmp_path, kind, expected
):
    c = build(tmp_path)
    for rows in (c.result["input_document"]["parameters"], c.result["parameter_trace"]):
        next(p for p in rows if p["parameter_id"] == "assumed")["kind"] = kind
    c.record["input_sha256"] = canonical_sha256(c.result["input_document"])
    params = {p["parameter_id"]: p for p in trace(c)["parameters"]}
    assert params["assumed"]["kind"] == kind
    assert params["assumed"]["is_conditional"] is expected
    assert params["composed"]["is_conditional"] is expected
    assert params["observed"]["is_conditional"] is False


@pytest.mark.parametrize(
    "raw",
    [
        "PDF physical8 quarterly table",
        "PDF physical8 quarterly table, FY2025Q4 reference, revenue 1234",
        "PDF physical8; CNY revenue 1000000",
    ],
)
def test_single_physical_page_survives_unrelated_period_and_amount(raw):
    got = locator({"locator": raw, "excerpt": "controlled"})
    assert (
        got["kind"] == "page" and got["page_kind"] == "physical" and got["value"] == "8"
    )


@pytest.mark.parametrize(
    "shared,count,accepted",
    [(False, 20, True), (False, 30, True), (False, 31, False), (True, 20, False)],
)
def test_longest_parameter_path_cannot_hide_behind_shared_memo(
    tmp_path, shared, count, accepted
):
    c = build(tmp_path)
    rows = c.result["parameter_trace"]
    template = copy.deepcopy(rows[2])
    rows[2]["input_parameter_ids"] = ["shared0", "head0"] if shared else ["head0"]
    rows[2]["formula"] = "x0+x1" if shared else "x0"
    for prefix, last in (
        [("shared", "observed"), ("head", "shared0")]
        if shared
        else [("head", "observed")]
    ):
        for i in range(count):
            p = copy.deepcopy(template)
            p.update(
                parameter_id=f"{prefix}{i}",
                formula="x0",
                input_parameter_ids=[f"{prefix}{i + 1}" if i + 1 < count else last],
            )
            rows.append(p)
    if accepted:
        assert trace(c)["state"] == "available"
    else:
        with pytest.raises(CatalogError) as e:
            trace(c)
        assert e.value.code == "lineage_limit_exceeded"
