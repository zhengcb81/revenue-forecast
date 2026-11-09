"""Explicit synthetic source facts; real engine and optional real recorder processes.

These fixtures are never actual company research or production evidence.
"""

from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from b34_release.test_research_identity import (  # noqa:E402
    anchored,
    pin_deployment,
    native_events,
    save_events,
    sync_budget,
    write,
    logs,
    identity,
    controlled_alias,
    ANCHOR,
    RECORDER_SHA,
    ENT,
    LISTING,
)
from contracts.evidence import build_host_receipt, canonical_sha256  # noqa:E402
from report_catalog import ReportCatalog  # noqa:E402
from test_recognition_bridge import forecast_document  # noqa:E402
from revenue_core import run_forecast  # noqa:E402
from revenue_backtest import create_snapshot  # noqa:E402
from revenue_report import render_markdown  # noqa:E402
import report_catalog_research_publication as pub  # noqa:E402

RECOVERY = "e" * 32
VALIDATE = "1" * 32
COMPUTE = "2" * 32
SNAPSHOT = "3" * 32


def raw_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode() + b"\n"


def doc(path):
    return json.loads(path.read_bytes())


def stamp():
    return datetime.now(timezone.utc).isoformat()


def freeze_frame(run, template, cid, command, inputs, begin, end, stdout=b""):
    frame = deepcopy(template)
    frame.update(
        capture_id=cid,
        command=command,
        executed_command=list(command),
        started_at=begin,
        finished_at=end,
        child_started=True,
        exit_code=0,
        timed_out=False,
        execution_error=None,
        input_complete=True,
        output_complete=True,
        input_cleanup_complete=True,
        input_cleanup_failures=0,
        input_snapshots=[],
    )
    folder = run / "roles/executor/commands" / cid
    folder.mkdir(parents=True, exist_ok=True)
    for count, (index, path) in enumerate(inputs.items(), 1):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        frozen = folder / f"input-{count:04}-{digest[:12]}.json"
        consumed = folder / f"consume-{count:04}-{digest[:12]}.json"
        frozen.write_bytes(raw)
        frame["input_snapshots"].append(
            {
                "argument_indices": [index],
                "original_path": str(path),
                "frozen_path": str(frozen),
                "consumed_path": str(consumed),
                "sha256": digest,
                "byte_size": len(raw),
                "observed_at": begin,
                "consumed_unchanged": True,
                "consumed_after_bytes": len(raw),
                "consumed_after_sha256": digest,
            }
        )
        frame["executed_command"][index] = str(consumed)
    frame["runtime_observation"]["observed_at"] = begin
    logs(run, frame, stdout)
    start = deepcopy(frame)
    for field in ["exit_code", "finished_at", "timed_out", "output_complete"]:
        start.pop(field, None)
    for row in start["input_snapshots"]:
        for field in [
            "consumed_unchanged",
            "consumed_after_bytes",
            "consumed_after_sha256",
        ]:
            row.pop(field, None)
    return [
        {
            "schema_version": "1.0",
            "event_id": uuid.uuid4().hex,
            "run_id": run.name,
            "role": "executor",
            "kind": "command_started",
            "recorded_at": begin,
            "data": start,
        },
        {
            "schema_version": "1.0",
            "event_id": uuid.uuid4().hex,
            "run_id": run.name,
            "role": "executor",
            "kind": "command_finished",
            "recorded_at": end,
            "data": frame,
        },
    ]


def build(root, monkeypatch, *, real_recorder=False, version="v1"):
    layout = pub.publication_layout(version)
    run, anchor_result = anchored(root)
    anchor_result["source"]["published_date"] = "2026-02-20"
    anchor_result["source"]["company_wiki_trace"]["source_manifest"][
        "published_date"
    ] = "2026-02-20"
    es = native_events(run)
    logs(run, es[1]["data"], raw_json(anchor_result))
    save_events(run, es)
    pin_deployment(root, run)
    es = native_events(run)
    failure = es[-1]["data"]
    logs(
        run,
        failure,
        b"",
        raw_json(
            {
                "error_code": "upstream",
                "stage": "local_prepare",
                "calls": 3,
                "downloads": 0,
                "upstream_cause": {
                    "schema_version": "filing-upstream-cause/1",
                    "operation": "local_prepare",
                    "code": "local_document_kind_unresolved",
                    "provider_started": False,
                    "usage_complete": True,
                    "retry_scope": "none",
                },
            }
        ),
    )
    save_events(run, es)
    (run / "execution/terminal.json").unlink()
    scope = doc(run / "execution/scope.json")
    anchor = anchor_result["source"]
    write(run / "execution/annual2025-source-record.json", anchor)
    web = run / "execution/web-capture-q3-2026"
    web.mkdir()
    body = b"Controlled official company release: synthetic operating reference, not real research."
    url = "https://www.wuxiapptec.com/news/controlled-fixture"
    response = {
        "results": [
            {
                "url": url,
                "title": "Controlled synthetic release",
                "raw_content": body.decode(),
            }
        ],
        "failed_results": [],
        "request_id": "controlled-tool-request",
    }
    (web / "source.markdown").write_bytes(body)
    (web / "tool-response.json").write_bytes(raw_json(response))
    base_time = datetime.fromisoformat(native_events(run)[-1]["data"]["finished_at"])
    observed_at = base_time + timedelta(seconds=1)
    observed = observed_at.isoformat()
    capture_day = observed_at.date().isoformat()
    request = {"urls": [url], "format": "markdown", "query_omitted": True}
    observation = {
        "request_id": response["request_id"],
        "tool": "controlled-web-tool",
        "request": request,
    }
    write(web / "acquisition-observation.json", observation)
    event = {
        "tool": observation["tool"],
        "request_id": response["request_id"],
        "request": request,
        "response_artifact_sha256": hashlib.sha256(
            (web / "tool-response.json").read_bytes()
        ).hexdigest(),
        "retrieved_markdown_sha256": hashlib.sha256(body).hexdigest(),
        "recorded_at": observed,
        "raw_artifact_kind": "tool-returned complete markdown; not raw HTML",
    }
    write(run / "execution/company-release-capture-event.json", event)
    host = build_host_receipt(
        issuer="controlled-fixture",
        environment="synthetic test",
        tool_name=event["tool"],
        action="extract_page",
        event_sha256=canonical_sha256(event),
        timestamp=observed,
    )
    cap = {
        "capture_schema_version": "1.0",
        "capture_method": "api_response",
        "tool_name": event["tool"],
        "tool_call_id": response["request_id"],
        "captured_date": capture_day,
        "snapshot_sha256": hashlib.sha256(body).hexdigest(),
        "content_treatment": "untrusted_data_only",
        "prompt_injection_status": "not_detected",
        "host_receipt": host,
    }
    cap["receipt_sha256"] = canonical_sha256(cap)
    source = {
        "source_id": "controlled_release",
        "source_type": "company_release",
        "title": response["results"][0]["title"],
        "publisher": "Controlled source fixture",
        "url": url,
        "published_date": "2026-10-26",
        "accessed_date": capture_day,
        "page_or_section": "Controlled native contract",
        "capture": cap,
    }
    write(run / "execution/company-release-q3-2026-source.json", source)
    builder = run / "execution/build_live_release_source.py"
    builder.write_text(
        "# Retained synthetic builder is never executed as admission authority\n",
        encoding="utf-8",
    )
    command = [sys.executable, "-B", str(builder)]
    args = {
        "--web-body": web / "source.markdown",
        "--web-response": web / "tool-response.json",
        "--web-observation": web / "acquisition-observation.json",
        "--annual-source": run / "execution/annual2025-source-record.json",
        "--output": run / "execution/company-release-q3-2026-source.json",
    }
    inputs = {}
    for flag, path in args.items():
        command += [flag, str(path)]
        if flag != "--output":
            inputs[len(command) - 1] = path
    template = native_events(run)[-1]["data"]
    output = {
        "status": "source_record_validated",
        "sources_validated": [anchor["source_id"], source["source_id"]],
        "source": source,
        "body_bytes": len(body),
        "transport_bytes": len((web / "tool-response.json").read_bytes()),
    }
    recovery = freeze_frame(
        run,
        template,
        RECOVERY,
        command,
        inputs,
        (base_time + timedelta(seconds=2)).isoformat(),
        (base_time + timedelta(seconds=3)).isoformat(),
        raw_json(output),
    )
    save_events(run, native_events(run) + recovery)
    data = forecast_document()
    data.update(
        company_name="药明康德",
        as_of_date="2026-11-01",
        forecast_version="controlled-publication-" + version,
    )

    def replace(value):
        if isinstance(value, dict):
            return {k: replace(v) for k, v in value.items()}
        if isinstance(value, list):
            return [replace(v) for v in value]
        return anchor["source_id"] if value == "filing" else value

    data = replace(data)
    data["sources"] = [anchor, source]
    verification_day = max(data["as_of_date"], anchor["capture"]["captured_date"], capture_day)
    for item in data.get("management_communication_coverage", []):
        item["checked_date"] = verification_day
    by_source = {x["source_id"]: x for x in data["sources"]}
    parameter = next(x for x in data["parameters"] if x["kind"] == "analyst_assumption")
    parameter["source_ids"] = [source["source_id"]]
    for claim in data["evidence_claims"]:
        if claim["claim_id"] in parameter["claim_ids"]:
            claim["source_id"] = source["source_id"]
        capture = by_source[claim["source_id"]]["capture"]
        claim.update(
            content_sha256=capture["snapshot_sha256"],
            capture_receipt_sha256=capture["receipt_sha256"],
            verified_date=verification_day,
        )
    forecast = (run / layout["input"]).parent
    forecast.mkdir(parents=True)
    write(forecast / "input.json", data)
    (run / "snapshots").mkdir()
    (run / "registry").mkdir()
    registry = run / "registry/publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(registry))
    scope.update(
        currency=data["currency"],
        target_forecast_years=data["forecast_years"],
        harness="controlled-author",
    )
    write(run / "execution/scope.json", scope)
    v1_bytes = {}
    v1_registry_prefix = b""
    if version != "v1":
        # An earlier synthetic native-contract version stays byte-for-byte intact.
        prior = deepcopy(data)
        prior["forecast_version"] = "controlled-publication-v1"
        write(run / "forecast/input.json", prior)
        previous = run_forecast(prior)
        write(run / "forecast/forecast.json", previous)
        (run / "forecast/forecast.md").write_bytes(render_markdown(previous).encode())
        write(
            run / "snapshots/v1.json", create_snapshot(prior, prior["forecast_version"])
        )
        v1_bytes = {name: (run / name).read_bytes() for name in pub.ARTIFACTS[:4]}
        v1_registry_prefix = registry.read_bytes()
    commands = [
        (
            VALIDATE,
            [
                sys.executable,
                "-B",
                str(ROOT / "scripts/revenue_forecast.py"),
                str(forecast / "input.json"),
                "--validate-only",
            ],
        ),
        (
            COMPUTE,
            [
                sys.executable,
                "-B",
                str(ROOT / "scripts/revenue_forecast.py"),
                str(forecast / "input.json"),
                "--output",
                str(forecast / "forecast.json"),
                "--markdown",
                str(forecast / "forecast.md"),
            ],
        ),
        (
            SNAPSHOT,
            [
                sys.executable,
                "-B",
                str(ROOT / "scripts/revenue_backtest.py"),
                "create",
                str(forecast / "input.json"),
                "--version",
                data["forecast_version"],
                "--output",
                str(run / layout["snapshot"]),
            ],
        ),
    ]
    ids = {}
    recorder_sha = RECORDER_SHA
    for cid, cmd in commands:
        position = 4 if cid == SNAPSHOT else 3
        if real_recorder:
            recorder = (
                Path.home()
                / ".agents/skills/revenue-forecast-audit/scripts/audit_run.py"
            )
            recorder_sha = hashlib.sha256(recorder.read_bytes()).hexdigest()
            argv = [
                sys.executable,
                "-B",
                str(recorder),
                "capture",
                "--run",
                str(run),
                "--role",
                "executor",
                "--timeout-seconds",
                "90",
                "--freeze-input",
                str(forecast / "input.json"),
                "--freeze-arg-index",
                str(position),
                "--",
                *cmd,
            ]
            result = subprocess.run(
                argv,
                capture_output=True,
                env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
                timeout=95,
            )
            assert result.returncode == 0, (result.stdout, result.stderr)
            frame = native_events(run)[-1]["data"]
            ids[cid] = frame["capture_id"]
        else:
            begin = stamp()
            if cid == VALIDATE:
                run_forecast(data, mode="draft")
            elif cid == COMPUTE:
                result = run_forecast(data)
                write(forecast / "forecast.json", result)
                (forecast / "forecast.md").write_bytes(render_markdown(result).encode())
            else:
                write(
                    run / layout["snapshot"],
                    create_snapshot(data, data["forecast_version"]),
                )
            end = stamp()
            out = b"valid\n" if cid == VALIDATE else b""
            pair = freeze_frame(
                run,
                template,
                cid,
                cmd,
                {position: forecast / "input.json"},
                begin,
                end,
                out,
            )
            save_events(run, native_events(run) + pair)
            ids[cid] = cid
    if real_recorder:
        events = native_events(run)
        for e in events:
            e["data"]["runtime_observation"]["capture_tool_sha256"] = recorder_sha
        save_events(run, events)
    sync_budget(run)
    budget = doc(run / "execution/budget-observation.json")
    budget["state"] = "SUCCEEDED"
    write(run / "execution/budget-observation.json", budget)
    ledger = doc(run / "execution/step-ledger.json")
    result = doc(forecast / "forecast.json")
    snap = doc(run / layout["snapshot"])
    ledger.update(
        state="SUCCEEDED",
        terminal_research_failure=False,
        result_report={
            "input_sha256": result["input_sha256"],
            "result_sha256": result["result_sha256"],
            "snapshot_id": snap["snapshot_id"],
        },
    )
    write(run / "execution/step-ledger.json", ledger)
    closure = {
        "schema_version": pub.CLOSURE_SCHEMA,
        "publication_version": version,
        "run_id": run.name,
        "parent_research_attempt_id": scope["attempt_id"],
        "status": "succeeded",
        "closed_at": stamp(),
        "compute_capture_id": ids[COMPUTE],
        "validate_capture_id": ids[VALIDATE],
        "snapshot_capture_id": ids[SNAPSHOT],
        "source_stage_failure_capture_id": template["capture_id"],
        "recovery_capture_id": RECOVERY,
        "research_manifest_sha256": hashlib.sha256(
            (run / "execution/step-ledger.json").read_bytes()
        ).hexdigest(),
        "review_receipt_sha256": "PENDING",
    }
    (run / layout["closure"]).parent.mkdir(parents=True, exist_ok=True)
    write(run / layout["closure"], closure)
    review = refresh_review(run, version=version)
    return {
        "root": root,
        "run": run,
        "recorder_sha": recorder_sha,
        "review_sha": review,
        "failed_id": template["capture_id"],
        "compute_id": ids[COMPUTE],
        "anchor": ANCHOR,
        "data": data,
        "version": version,
        "v1_bytes": v1_bytes,
        "v1_registry_prefix": v1_registry_prefix,
    }


def refresh_review(run, *, version="v1"):
    layout = pub.publication_layout(version)
    closure = doc(run / layout["closure"])
    review = {
        "schema_version": pub.REVIEW_SCHEMA,
        "publication_version": version,
        "run_id": run.name,
        "parent_research_attempt_id": "attempt01",
        "status": "accepted",
        "reviewer": "controlled-independent-reviewer",
        "reviewed_at": stamp(),
        "report_sha256": "7" * 64,
        "research_manifest_sha256": hashlib.sha256(
            (run / "execution/step-ledger.json").read_bytes()
        ).hexdigest(),
        "captures": {
            "compute": closure["compute_capture_id"],
            "validate": closure["validate_capture_id"],
            "snapshot": closure["snapshot_capture_id"],
            "source_failure": closure["source_stage_failure_capture_id"],
            "recovery": closure["recovery_capture_id"],
        },
        "coverage_acceptance": {
            "research_workflow": True,
            "source_capture": True,
            "model_quality": "conditional_scenarios",
        },
        "artifacts": {
            n: {
                "sha256": hashlib.sha256((run / n).read_bytes()).hexdigest(),
                "byte_size": (run / n).stat().st_size,
            }
            for n in layout["artifacts"]
        },
    }
    write(run / layout["review"], review)
    sha = hashlib.sha256((run / layout["review"]).read_bytes()).hexdigest()
    closure.update(
        review_receipt_sha256=sha,
        closed_at=stamp(),
        research_manifest_sha256=review["research_manifest_sha256"],
    )
    write(run / layout["closure"], closure)
    return sha


def admit(case, **extra):
    return pub.import_research_publication(
        ReportCatalog(root=case["root"]),
        run_id=case["run"].name,
        entity_id=ENT,
        listing_id=LISTING,
        identity_resolver=extra.pop("identity_resolver", identity),
        recorder_sha256=case["recorder_sha"],
        review_receipt_sha256=case["review_sha"],
        identity_anchor_capture_id=ANCHOR,
        deployment_snapshot="pinned-reviewed.json",
        source_stage_failure_capture_id=case["failed_id"],
        source_alias_resolver=extra.pop("source_alias_resolver", controlled_alias),
        publication_version=extra.pop("publication_version", case.get("version", "v1")),
        **extra,
    )
