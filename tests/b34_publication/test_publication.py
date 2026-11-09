"""Publication admission security regressions; synthetic owner roots only."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pytest
from .fixtures import (
    admit,
    doc,
    write,
    refresh_review,
    ReportCatalog,
    pub,
    identity,
)
from owner_file_lock import OwnerFileLock  # noqa: E402


def test_native_stages_and_successful_whole_run_are_distinct(case):
    before = {p: p.read_bytes() for p in case["run"].rglob("*") if p.is_file()}
    result = admit(case)
    assert result["status"] == "succeeded" and result["registered"]["reports"] == [
        result["report_id"]
    ]
    catalog = ReportCatalog(root=case["root"])
    value = catalog.get_run(case["run"].name)["run"]
    assert value["status"] == "succeeded"
    by_id = {x["attempt_id"]: x for x in value["attempts"]}
    assert (
        by_id[case["failed_id"]]["status"] == "failed"
        and by_id[case["failed_id"]]["report_ids"] == []
    )
    assert by_id[case["compute_id"]]["status"] == "succeeded" and by_id[
        case["compute_id"]
    ]["report_ids"] == [result["report_id"]]
    stages = value["model_metadata"]["native_attempts"]
    assert stages["schema_version"] == "rf-native-attempts/1"
    assert (
        stages["items"][0]["recovery_status"]
        == "recovered_by_alternative_official_source"
    )
    assert stages["items"][1]["recovery_status"] is None
    assert (
        catalog.get_report(result["report_id"])["view"]["report"]["information_as_of"]
        == "2026-11-01"
    )
    assert all(p.read_bytes() == raw for p, raw in before.items())


def test_exact_replay_keeps_catalog_and_stable_report(case):
    first = admit(case)
    catalog = ReportCatalog(root=case["root"])
    before = catalog.file.read_bytes()
    replay = admit(case)
    assert replay["replayed"] is True and replay["report_id"] == first["report_id"]
    assert (
        replay["catalog_revision"] == first["catalog_revision"]
        and catalog.file.read_bytes() == before
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "review_hash",
        "review_accepted",
        "review_artifact",
        "whole_failed",
        "running",
        "closure_ids",
        "different_company",
        "ledger_hash",
        "forecast_bytes",
        "markdown",
        "registry_chain",
        "snapshot_bytes",
        "budget_elapsed",
        "budget_download",
        "producer_hash",
        "pin_root",
        "pin_capture",
        "diagnostic_failure",
        "recovery_missing",
        "recovery_body",
        "recovery_event",
        "recovery_unused",
        "frozen_hash",
        "frozen_escape",
        "counter_undefined",
    ],
)
def test_invalid_evidence_cannot_be_admitted_even_if_review_is_resealed(case, mutation):
    run = case["run"]
    closure = doc(run / "execution/publication.json")
    if mutation == "review_hash":
        case["review_sha"] = "0" * 64
    elif mutation == "review_accepted":
        review = doc(run / "execution/publication-review.json")
        review["status"] = "rejected"
        write(run / "execution/publication-review.json", review)
    elif mutation == "review_artifact":
        review = doc(run / "execution/publication-review.json")
        review["artifacts"]["forecast/input.json"]["byte_size"] += 1
        write(run / "execution/publication-review.json", review)
    elif mutation == "whole_failed":
        write(run / "execution/terminal.json", {"status": "failed"})
    elif mutation == "running":
        value = doc(run / "execution/step-ledger.json")
        value["state"] = "RUNNING"
        write(run / "execution/step-ledger.json", value)
    elif mutation == "closure_ids":
        closure["snapshot_capture_id"] = closure["compute_capture_id"]
        write(run / "execution/publication.json", closure)
    elif mutation == "different_company":
        value = doc(run / "run.json")
        value["company_query"] = "foreign"
        write(run / "run.json", value)
    elif mutation == "ledger_hash":
        closure["research_manifest_sha256"] = "0" * 64
        write(run / "execution/publication.json", closure)
    elif mutation == "forecast_bytes":
        value = doc(run / "forecast/forecast.json")
        value["company_name"] = "foreign"
        write(run / "forecast/forecast.json", value)
    elif mutation == "markdown":
        (run / "forecast/forecast.md").write_text("fabricated report", encoding="utf-8")
    elif mutation == "registry_chain":
        p = run / "registry/publications.jsonl"
        p.chmod(0o600)
        value = json.loads(p.read_text().splitlines()[0])
        value["line_sha256"] = "0" * 64
        p.write_text(json.dumps(value) + "\n", encoding="utf-8")
    elif mutation == "snapshot_bytes":
        value = doc(run / "snapshots/v1.json")
        value["snapshot_id"] = "0" * 64
        write(run / "snapshots/v1.json", value)
    elif mutation == "budget_elapsed":
        value = doc(run / "execution/budget-observation.json")
        value["native_capture_elapsed_seconds"] = 0
        write(run / "execution/budget-observation.json", value)
    elif mutation == "budget_download":
        value = doc(run / "execution/budget-observation.json")
        value["new_source_downloads"] = 1
        write(run / "execution/budget-observation.json", value)
    elif mutation.startswith("recovery_"):
        if mutation == "recovery_missing":
            closure["recovery_capture_id"] = "f" * 32
            write(run / "execution/publication.json", closure)
        elif mutation == "recovery_body":
            (run / "execution/web-capture-q3-2026/source.markdown").write_bytes(
                b"changed"
            )
        elif mutation == "recovery_event":
            value = doc(run / "execution/company-release-capture-event.json")
            value["request_id"] = "foreign"
            write(run / "execution/company-release-capture-event.json", value)
        else:
            value = doc(run / "execution/company-release-q3-2026-source.json")
            value["source_id"] = "foreign"
            write(run / "execution/company-release-q3-2026-source.json", value)
    else:
        events = [
            json.loads(x)
            for x in (run / "roles/executor/events.jsonl").read_text().splitlines()
        ]
        if mutation == "producer_hash":
            events[-1]["data"]["runtime_observation"]["capture_tool_sha256"] = "0" * 64
        elif mutation == "pin_root":
            value = doc(run / "execution/pinned-reviewed.json")
            value["filing_fetch"]["code_root"] = str(case["root"])
            write(run / "execution/pinned-reviewed.json", value)
        elif mutation == "pin_capture":
            value = doc(run / "execution/pinned-reviewed.json")
            value["capture_id"] = case["compute_id"]
            write(run / "execution/pinned-reviewed.json", value)
        else:
            selected = next(
                e["data"]
                for e in events
                if e["kind"] == "command_finished"
                and e["data"]["capture_id"] == case["failed_id"]
            )
            if mutation == "diagnostic_failure":
                selected["exit_code"] = 2
            elif mutation == "frozen_hash":
                events[-1]["data"]["input_snapshots"][0]["sha256"] = "0" * 64
            elif mutation == "frozen_escape":
                events[-1]["data"]["input_snapshots"][0]["frozen_path"] = str(
                    case["root"] / "outside.json"
                )
            elif mutation == "counter_undefined":
                p = Path(selected["stderr_artifact"])
                value = json.loads(p.read_bytes())
                value.pop("calls")
                p.write_bytes(json.dumps(value).encode())
                selected["stderr_total_bytes"] = selected["stderr_retained_bytes"] = (
                    p.stat().st_size
                )
        (run / "roles/executor/events.jsonl").write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in events) + "\n",
            encoding="utf-8",
        )
    if mutation not in {
        "review_hash",
        "review_accepted",
        "review_artifact",
        "ledger_hash",
    }:
        case["review_sha"] = refresh_review(run)
    with pytest.raises(pub.CatalogError):
        admit(case)
    assert not ReportCatalog(root=case["root"]).file.exists()


def test_late_identity_change_under_catalog_lock_refuses_append(case, monkeypatch):
    catalog = ReportCatalog(root=case["root"])
    original = catalog._validate_report_artifact
    state = {"locked": False}

    def validation(record):
        value = original(record)
        if OwnerFileLock(catalog.file.with_name(catalog.file.name + ".lock")).is_locked():
            state["locked"] = True
        return value

    monkeypatch.setattr(
        ReportCatalog,
        "_validate_report_artifact",
        lambda self, record: validation(record),
    )

    def resolver(entity):
        value = identity(entity)
        if state["locked"]:
            value["source_revision"] = "changed-at-append"
        return value

    with pytest.raises(pub.CatalogError):
        admit(case, identity_resolver=resolver)
    assert state["locked"] and not catalog.file.exists()
    assert not OwnerFileLock(catalog.file.with_name(catalog.file.name + ".lock")).is_locked()
    assert admit(case)["status"] == "succeeded"


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_real_recorder_native_processes_publish_selected_version(case_factory, version):
    value = case_factory(real_recorder=True, version=version)
    before = {p: p.read_bytes() for p in value["run"].rglob("*") if p.is_file()}
    result = admit(value)
    assert result["status"] == "succeeded"
    assert all(p.read_bytes() == raw for p, raw in before.items())
    if version == "v2":
        assert len(value["v1_registry_prefix"].splitlines()) == 3
        assert all(
            (value["run"] / name).read_bytes() == raw
            for name, raw in value["v1_bytes"].items()
        )
        assert (
            (value["run"] / "registry/publications.jsonl")
            .read_bytes()
            .startswith(value["v1_registry_prefix"])
        )
        report = ReportCatalog(root=value["root"]).get_report(result["report_id"])[
            "view"
        ]["report"]
        assert report["artifact_revision"] == "controlled-publication-v2"
        assert report["supersedes_report_id"] is None


@pytest.mark.parametrize(
    "version",
    [
        "v0",
        "v01",
        "v1000",
        "../v2",
        "v2/else",
        Path.cwd().anchor + "v2",
        "v2.json",
        "V2",
        "v2\\x",
        "v2\n",
    ],
)
def test_version_selector_rejects_paths_and_noncanonical_basename(version):
    with pytest.raises(pub.CatalogError):
        pub.publication_layout(version)


@pytest.mark.parametrize("version", ["v1", "v2", "v999"])
def test_version_layout_is_fixed_and_shared_registry(version):
    layout = pub.publication_layout(version)
    prefix = "forecast/" if version == "v1" else "forecast/" + version + "/"
    assert layout["input"] == prefix + "input.json"
    assert layout["snapshot"] == "snapshots/" + version + ".json"
    assert layout["artifacts"][4] == "registry/publications.jsonl"


@pytest.mark.parametrize(
    "mutation",
    [
        "selector",
        "closure",
        "review",
        "snapshot_version",
        "extra_closure",
        "extra_review",
        "compute_only_review",
    ],
)
def test_version_and_complete_review_are_explicit(case, mutation):
    if mutation == "selector":
        with pytest.raises(pub.CatalogError):
            admit(case, publication_version="v2")
        return
    run = case["run"]
    if mutation in {"closure", "extra_closure"}:
        closure = doc(run / "execution/publication.json")
        closure[
            "publication_version" if mutation == "closure" else "untrusted_extra"
        ] = "v2"
        write(run / "execution/publication.json", closure)
    elif mutation == "snapshot_version":
        events = [
            json.loads(x)
            for x in (run / "roles/executor/events.jsonl").read_text().splitlines()
        ]
        for e in events:
            frame = e["data"]
            if (
                frame["capture_id"]
                == doc(run / "execution/publication.json")["snapshot_capture_id"]
            ):
                for key in ["command", "executed_command"]:
                    frame[key][frame[key].index("--version") + 1] = "unrelated-version"
        (run / "roles/executor/events.jsonl").write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in events) + "\n",
            encoding="utf-8",
        )
        case["review_sha"] = refresh_review(run)
    else:
        review = doc(run / "execution/publication-review.json")
        if mutation == "review":
            review["publication_version"] = "v2"
        elif mutation == "extra_review":
            review["untrusted_extra"] = True
        else:
            review["coverage_acceptance"]["research_workflow"] = False
        write(run / "execution/publication-review.json", review)
        case["review_sha"] = hashlib.sha256(
            (run / "execution/publication-review.json").read_bytes()
        ).hexdigest()
        closure = doc(run / "execution/publication.json")
        closure["review_receipt_sha256"] = case["review_sha"]
        write(run / "execution/publication.json", closure)
    with pytest.raises(pub.CatalogError):
        admit(case)
    assert not ReportCatalog(root=case["root"]).file.exists()


def test_simultaneous_managers_append_only_once(case):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    gate = Barrier(2)

    def execute():
        gate.wait(timeout=10)
        try:
            return admit(case)
        except pub.CatalogError as exc:
            assert exc.code == "catalog_busy"
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        values = list(pool.map(lambda _: execute(), range(2)))
    assert any(value is not None for value in values)
    catalog = ReportCatalog(root=case["root"])
    assert len(catalog.file.read_bytes().splitlines()) == 1
    assert admit(case)["replayed"] is True


def test_payload_change_after_admission_is_not_a_replay(case):
    admit(case)
    catalog = ReportCatalog(root=case["root"])
    before = catalog.file.read_bytes()
    review = doc(case["run"] / "execution/publication-review.json")
    review["report_sha256"] = "6" * 64
    write(case["run"] / "execution/publication-review.json", review)
    case["review_sha"] = hashlib.sha256(
        (case["run"] / "execution/publication-review.json").read_bytes()
    ).hexdigest()
    closure = doc(case["run"] / "execution/publication.json")
    closure["review_receipt_sha256"] = case["review_sha"]
    write(case["run"] / "execution/publication.json", closure)
    with pytest.raises(pub.CatalogError):
        admit(case)
    assert catalog.file.read_bytes() == before


def test_raw_traversal_and_alias_are_not_canonical_path_equivalence(case):
    input_path = case["run"] / "forecast/input.json"
    assert pub._equal_path(str(input_path), input_path)
    assert not pub._equal_path(
        str(input_path.parent / "../forecast/input.json"), input_path
    )
    assert not pub._equal_path(str(input_path.parent / "other.json"), input_path)


@pytest.mark.parametrize(
    "mutation",
    [
        "future",
        "before_created",
        "finish_changed",
        "missing_time",
        "wrong_time_type",
        "first_start_drift",
    ],
)
def test_native_producer_observation_is_one_prior_typed_snapshot(case, mutation):
    events = [
        json.loads(x)
        for x in (case["run"] / "roles/executor/events.jsonl").read_text().splitlines()
    ]
    target = case["compute_id"]
    if mutation == "first_start_drift":
        target = next(
            e["data"]["capture_id"]
            for e in events
            if str(e["data"]["command"][-1]).endswith("probe_pinned_cwp_runtime.py")
        )
    for e in events:
        if e["data"]["capture_id"] != target:
            continue
        observation = e["data"]["runtime_observation"]
        if mutation == "first_start_drift":
            from datetime import datetime, timedelta

            if e["kind"] == "command_started":
                e["data"]["started_at"] = (
                    datetime.fromisoformat(e["data"]["started_at"])
                    - timedelta(milliseconds=1)
                ).isoformat()
            continue
        if mutation == "future":
            observation["observed_at"] = "2999-01-01T00:00:00Z"
        elif mutation == "before_created":
            observation["observed_at"] = "2000-01-01T00:00:00Z"
        elif mutation == "finish_changed":
            if e["kind"] == "command_finished":
                observation["platform"] = "different-producer"
        elif mutation == "missing_time":
            observation.pop("observed_at")
        else:
            observation["observed_at"] = 42
    (case["run"] / "roles/executor/events.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in events),
        encoding="utf-8",
    )
    case["review_sha"] = refresh_review(case["run"])
    with pytest.raises(pub.CatalogError):
        admit(case)
    assert not ReportCatalog(root=case["root"]).file.exists()


def test_producer_snapshot_can_precede_launch_and_headers_can_append_later(case):
    from datetime import datetime, timedelta

    events = [
        json.loads(x)
        for x in (case["run"] / "roles/executor/events.jsonl").read_text().splitlines()
    ]
    for e in events:
        if e["data"]["capture_id"] != case["compute_id"]:
            continue
        frame = e["data"]
        frame["runtime_observation"]["observed_at"] = (
            datetime.fromisoformat(frame["started_at"]) - timedelta(milliseconds=5)
        ).isoformat()
        e["recorded_at"] = (
            datetime.fromisoformat(e["recorded_at"]) + timedelta(milliseconds=5)
        ).isoformat()
    (case["run"] / "roles/executor/events.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in events),
        encoding="utf-8",
    )
    case["review_sha"] = refresh_review(case["run"])
    assert admit(case)["status"] == "succeeded"
