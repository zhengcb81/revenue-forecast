"""Exercise real native validation and recorder structure on synthetic source bytes."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path

import pytest

from b34_publication.fixtures import (
    doc, freeze_frame, native_events, raw_json, write,
)
from contracts.evidence import build_host_receipt
from publication_registry import canonical_sha256
from report_catalog import CatalogError
from report_catalog_research_attempt import _Observation
from report_catalog_research_publication import publication_layout
from report_catalog_research_publication_sources import (
    EVENT_KIND, NATIVE_MODULES, SCHEMA, retained_response, validate_source_evidence,
    validator_program,
)

ROOT = Path(__file__).resolve().parents[2]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def prepared(case):
    run = case["run"]
    data = deepcopy(case["data"])
    annual, old_web = data["sources"]
    rows = [{"source_id": annual["source_id"], "kind": "company_wiki_anchor",
             "source_record_sha256": canonical_sha256(annual)}]
    sources = [annual]
    for i in range(3):
        source = deepcopy(old_web)
        if i:
            source["source_id"] += str(i)
        source["title"] += str(i)
        body = ("Complete synthetic official result " + str(i)).encode()
        request = "synthetic-tool-call-" + str(i)
        response = {"request_id": request, "failed_results": [], "results": [
            {"url": source["url"], "title": source["title"],
             "raw_content": body.decode()}]}
        raw = raw_json(response)
        relative = f"research/body-{i + 1:02}.tool-response.json"
        (run / "research").mkdir(exist_ok=True)
        (run / relative).write_bytes(raw)
        capture = source["capture"]
        capture.update(tool_name="tavily_extract", tool_call_id=request,
                       capture_method="api_response", snapshot_sha256=digest(body))
        capture["host_receipt"] = build_host_receipt(
            issuer="controlled-test", environment="synthetic-owner",
            tool_name="tavily_extract", action="tool_body_read", event_sha256=digest(raw),
            timestamp=capture["captured_date"],
        )
        capture["receipt_sha256"] = canonical_sha256(
            {k: v for k, v in capture.items() if k != "receipt_sha256"})
        rows.append({"source_id": source["source_id"], "kind": "retained_tool_response",
                     "source_record_sha256": canonical_sha256(source),
                     "response_artifact": relative, "transport_sha256": digest(raw),
                     "snapshot_sha256": digest(body), "event_reference_kind": EVENT_KIND,
                     "event_sha256": digest(raw)})
        sources.append(source)
    data["sources"] = sources
    write(run / "forecast/input.json", data)
    scope = {"RF_code_root": str(ROOT)}
    program = run / "execution/source_validation.py"
    program.write_text(validator_program(str(ROOT)), encoding="utf-8")
    template = native_events(run)[1]["data"]
    cid = "9" * 32
    now = datetime.now(timezone.utc).isoformat()
    frames = freeze_frame(
        run, template, cid,
        ["python", "-B", str(program), str(run / "forecast/input.json")],
        {2: program, 3: run / "forecast/input.json"}, now, now,
        raw_json({"status": "SOURCE_VALIDATED", "source_ids": [s["source_id"] for s in sources],
                  "code_root": str(ROOT), "external_attestation": False}),
    )
    manifest = {"schema_version": SCHEMA, "run_id": run.name,
                "publication_version": "v1", "capture_id": cid,
                "validator_sha256": digest(program.read_bytes()),
                "native_modules": {n: digest((ROOT / n).read_bytes()) for n in NATIVE_MODULES},
                "sources": rows}
    write(run / "execution/sources.json", manifest)
    return {"obs": _Observation(case["root"]), "run": run,
            "closure": {"recovery_capture_id": cid}, "source_input": data,
            "anchor": {"source_record_sha256": canonical_sha256(annual)},
            "started": {cid: frames[0]["data"]}, "finished": {cid: frames[1]["data"]},
            "scope": scope, "layout": publication_layout(), "manifest_name": "sources.json"}


def test_four_sources_all_original_bytes_and_unsigned_kind(case):
    args = prepared(case)
    result = validate_source_evidence(**args)
    assert len(result["sources"]) == 4 and result["schema_version"] == SCHEMA
    assert result["sources"][1]["event_reference_kind"] == EVENT_KIND
    assert "not_independent_host_event" in result["attestation"]
    assert args["source_input"]["sources"][1]["capture"]["host_receipt"]["timestamp"] == args["source_input"]["sources"][1]["capture"]["captured_date"]
    assert any(row["artifact"].endswith("research/body-03.tool-response.json")
               for row in args["obs"].manifest())
    args["obs"].recheck()


@pytest.mark.parametrize("mutation", [
    "omitted", "duplicate", "foreign", "other_run", "other_version", "old_capture",
    "body", "transport", "response_url", "response_title", "request_id", "event_kind",
    "source_record", "future_source", "program", "program_semantics", "program_unfrozen", "input_unfrozen",
    "native_module", "output_root", "output_ids", "path_escape", "absolute_path",
])
def test_invalid_sources_and_actual_validator_are_refused(case, mutation):
    args = prepared(case)
    run = args["run"]
    manifest_path = run / "execution/sources.json"
    manifest = doc(manifest_path)
    row = manifest["sources"][1]
    cid = args["closure"]["recovery_capture_id"]
    if mutation == "omitted":
        manifest["sources"].pop()
    elif mutation == "duplicate":
        manifest["sources"][2] = deepcopy(row)
    elif mutation == "foreign":
        row["source_id"] = "foreign"
    elif mutation == "other_run":
        manifest["run_id"] = "foreign"
    elif mutation == "other_version":
        manifest["publication_version"] = "v2"
    elif mutation == "old_capture":
        manifest["capture_id"] = "8" * 32
    elif mutation in {"body", "transport", "response_url", "response_title", "request_id"}:
        path = run / row["response_artifact"]
        response = doc(path)
        if mutation == "body":
            response["results"][0]["raw_content"] += " altered"
        elif mutation == "transport":
            response["extra"] = "changed"
        elif mutation == "request_id":
            response["request_id"] = "foreign"
        else:
            key = {"response_url": "url", "response_title": "title"}[mutation]
            response["results"][0][key] += "changed"
        write(path, response)
    elif mutation == "event_kind":
        row["event_reference_kind"] = "independent_signed_event"
    elif mutation == "source_record":
        row["source_record_sha256"] = digest(b"foreign")
    elif mutation == "future_source":
        # Rebind the recorder input as well, so native source clock is the guard.
        args["source_input"]["sources"][1]["published_date"] = "2200-01-01"
        write(run / "forecast/input.json", args["source_input"])
        snapshot = args["finished"][cid]["input_snapshots"][1]
        raw = (run / "forecast/input.json").read_bytes()
        Path(snapshot["frozen_path"]).write_bytes(raw)
        snapshot.update(sha256=digest(raw), byte_size=len(raw), consumed_after_sha256=digest(raw), consumed_after_bytes=len(raw))
    elif mutation == "program_semantics":
        path = run / "execution/source_validation.py"
        path.write_text("print('pretend validation')\n", encoding="utf-8")
        snapshot = args["finished"][cid]["input_snapshots"][0]
        raw = path.read_bytes()
        Path(snapshot["frozen_path"]).write_bytes(raw)
        snapshot.update(sha256=digest(raw), byte_size=len(raw), consumed_after_sha256=digest(raw), consumed_after_bytes=len(raw))
        manifest["validator_sha256"] = digest(raw)
    elif mutation == "program":
        with (run / "execution/source_validation.py").open("a", encoding="utf-8") as file:
            file.write("raise SystemExit(0)\n")
    elif mutation in {"program_unfrozen", "input_unfrozen"}:
        args["finished"][cid]["input_snapshots"].pop(0 if mutation == "program_unfrozen" else 1)
    elif mutation == "native_module":
        manifest["native_modules"][NATIVE_MODULES[0]] = digest(b"foreign")
    elif mutation in {"output_root", "output_ids"}:
        path = run / "roles/executor/commands" / cid / "stdout.txt"
        response = doc(path)
        response["code_root" if mutation == "output_root" else "source_ids"] = "foreign"
        # Logs still bind old hash; either tampered stdout or typed output rejects.
        write(path, response)
    elif mutation == "path_escape":
        row["response_artifact"] = "research/../execution/scope.json"
    elif mutation == "absolute_path":
        row["response_artifact"] = str(run / "research/body-01.tool-response.json")
    write(manifest_path, manifest)
    with pytest.raises((CatalogError, ValueError)):
        validate_source_evidence(**args)


def test_body_reader_uses_exact_source_and_response(case):
    args = prepared(case)
    row = doc(args["run"] / "execution/sources.json")["sources"][3]
    source = args["source_input"]["sources"][3]
    assert retained_response(args["obs"], args["run"], source, row).endswith(b"2")
    with pytest.raises(CatalogError):
        retained_response(args["obs"], args["run"], args["source_input"]["sources"][1], row)


@pytest.mark.parametrize("mutation", [None, "sealed_hash", "missing_observation", "foreign_source", "transport_changed"])
def test_lineage_reads_only_source_selected_sealed_bytes(case, mutation):
    from types import SimpleNamespace
    from report_catalog_lineage import Sources

    args = prepared(case)
    recovery = validate_source_evidence(**args)
    seal = {"source_recovery": recovery, "input_observations": args["obs"].manifest()}
    source = deepcopy(args["source_input"]["sources"][3])
    path = args["run"] / recovery["sources"][3]["response_artifact"]
    matching = next(row for row in seal["input_observations"]
                    if row["artifact"].endswith("research/body-03.tool-response.json"))
    if mutation == "sealed_hash":
        matching["sha256"] = digest(b"changed")
    elif mutation == "missing_observation":
        seal["input_observations"].remove(matching)
    elif mutation == "foreign_source":
        source["source_id"] = "foreign"
    elif mutation == "transport_changed":
        path.write_bytes(path.read_bytes() + b" ")
    reader = Sources.__new__(Sources)
    reader.catalog = SimpleNamespace(root=case["root"])
    reader.report = {"run_id": args["run"].name}
    reader.bodies = {}
    reader.publication_seal = lambda: seal
    if mutation is None:
        assert reader._captured_body(source) == b"Complete synthetic official result 2"
        assert reader.bodies[source["source_id"]] == b"Complete synthetic official result 2"
        assert reader._captured_body(args["source_input"]["sources"][0]) is None
    else:
        with pytest.raises(CatalogError):
            reader._captured_body(source)
