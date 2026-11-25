"""Explicit multi-source admission; retained unsigned tool responses, never collection.

The original B34 recovery profile remains separate. This profile requires a real
recorder capture freezing both the audited validator program and the exact input.
Native source, clock and receipt validation is called again during admission.
"""
from __future__ import annotations

import ast
from datetime import date, datetime
import hashlib
import importlib
import json
from pathlib import Path
import re

from contracts.document import validate_sources
from publication_registry import canonical_sha256
from report_catalog_research_attempt import _Observation
from report_catalog_research_identity import _code_hash
from report_catalog_retained_source import EVENT_KIND as EVENT_KIND, retained_response

SCHEMA = "rf-research-source-evidence/1"
# These are the native source validator's transitive evidence/clock/SourceRef
# primitives, rather than a second implementation of their contracts.
NATIVE_MODULES = (
    "scripts/contracts/document.py",
    "scripts/contracts/constants.py",
    "scripts/contracts/evidence.py",
    "scripts/contracts/source_clock.py",
    "scripts/company_wiki_source.py",
    "scripts/company_wiki_source_v2.py",
    "scripts/source_period_semantics.py",
)


def validator_program(code_root: str) -> str:
    """Audited, deliberately small existing research validator program template."""
    return (
        "import sys,json\nfrom datetime import date\nfrom pathlib import Path\n"
        f"sys.path.insert(0,{json.dumps(code_root + '/scripts', ensure_ascii=False)})\n"
        "from contracts.document import validate_sources\n"
        'x=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))\n'
        's=validate_sources(x,date.fromisoformat(x["as_of_date"]),require_capture=True)\n'
        'print(json.dumps({"status":"SOURCE_VALIDATED","source_ids":list(s),'
        f'"code_root":{json.dumps(code_root, ensure_ascii=False)},'
        '"external_attestation":False}))\n'
    )


def recheck_native_modules(scope: dict, hashes: dict) -> None:
    """Bind the declared native root to the admission process's actual source."""
    from report_catalog_research_publication import _need

    _need(isinstance(hashes, dict) and set(hashes) == set(NATIVE_MODULES),
          "source validator native module set differs")
    deployed = Path(scope["RF_code_root"])
    local = Path(__file__).resolve().parents[1]
    for name in NATIVE_MODULES:
        module_name = name.removeprefix("scripts/").removesuffix(".py").replace("/", ".")
        module = importlib.import_module(module_name)
        module_file = module.__file__
        _need(isinstance(module_file, str), "source validator module has no source file")
        assert isinstance(module_file, str)
        _need(Path(module_file).resolve() == (local / name).resolve(),
              "source validator imported another native module root")
        _need(_code_hash(deployed, name) == hashes[name] == _code_hash(local, name),
              "source validator native module bytes or root changed")


def validate_source_evidence(
    obs: _Observation, run: Path, closure: dict, source_input: dict, anchor: dict,
    started: dict, finished: dict, *, scope: dict, layout: dict, manifest_name: str,
) -> dict:
    from report_catalog_research_publication import (
        _capture_id, _complete, _frozen, _json, _need, _object, _script_index, _sha,
    )

    _need(isinstance(manifest_name, str)
          and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\.json", manifest_name),
          "source evidence requires one execution JSON basename")
    raw = obs.read(run / "execution" / manifest_name)
    manifest = _json(raw)
    _need(set(manifest) == {"schema_version", "run_id", "publication_version",
                           "capture_id", "validator_sha256", "native_modules", "sources"}
          and manifest.get("schema_version") == SCHEMA
          and manifest.get("run_id") == run.name
          and manifest.get("publication_version") == layout["version"],
          "source evidence belongs to another run or publication")
    cid = _capture_id(manifest.get("capture_id"))
    _need(cid == closure["recovery_capture_id"], "source validation capture differs")
    data, streams, logs = _complete(obs, run, cid, started, finished, succeeded=True)
    program = run / "execution/source_validation.py"
    index = _script_index(data["command"], program)
    _need(len(data["command"]) == index + 2,
          "source validation command has extra arguments")
    frozen = _frozen(obs, run, cid, data,
                     {index: program, index + 1: run / layout["input"]})
    code_root = scope["RF_code_root"]
    _need(isinstance(code_root, str), "source validator root is invalid")
    _need(_sha(frozen[index]) == manifest["validator_sha256"]
          and ast.dump(ast.parse(frozen[index].decode("utf-8")))
          == ast.dump(ast.parse(validator_program(code_root))),
          "frozen source validation program is not the audited native validator")
    _need(_json(frozen[index + 1]) == source_input,
          "source validation consumed a different input")
    recheck_native_modules(scope, manifest["native_modules"])
    # Reuse native eligibility, availability, capture/receipt and SourceRef guards;
    # stdout alone is never source validation authority.
    validated = validate_sources(source_input, date.fromisoformat(source_input["as_of_date"]),
                                 require_capture=True)
    result = _json(streams["stdout"])
    _need(set(result) == {"status", "source_ids", "code_root", "external_attestation"}
          and result.get("status") == "SOURCE_VALIDATED"
          and result.get("source_ids") == list(validated)
          and result.get("code_root") == code_root
          and result.get("external_attestation") is False,
          "actual source validation output differs from native sources or code root")
    rows = manifest.get("sources")
    _need(isinstance(rows, list) and 2 <= len(rows) <= 16,
          "source evidence count is outside its bound")
    indexed = {}
    for value in rows:
        row = _object(value)
        sid = row.get("source_id")
        _need(isinstance(sid, str) and sid in validated and sid not in indexed,
              "source evidence is duplicated or foreign")
        indexed[sid] = row
    _need(set(indexed) == set(validated), "source evidence omits input sources")
    annuals = 0
    used_web_source = False
    summaries = []
    responses = set()
    for source in source_input["sources"]:
        row = indexed[source["source_id"]]
        _need(row.get("source_record_sha256") == canonical_sha256(source),
              "source record bytes differ from evidence")
        if row.get("kind") == "company_wiki_anchor":
            _need(set(row) == {"source_id", "kind", "source_record_sha256"}
                  and row["source_record_sha256"] == anchor["source_record_sha256"],
                  "source evidence differs from the captured original identity anchor")
            annuals += 1
        else:
            retained_response(obs, run, source, row)
            host_time = source["capture"]["host_receipt"]["timestamp"]
            stage_time = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
            if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", host_time):
                # Date-only observations retain date precision; no invented midnight.
                before_stage = date.fromisoformat(host_time) <= stage_time.date()
            else:
                from contracts.source_clock import utc_timestamp
                before_stage = utc_timestamp(host_time, "timestamp", require_utc=False) <= stage_time
            _need(before_stage, "retained source event postdates native source validation")
            used_web_source = used_web_source or any(
                source["source_id"] in p.get("source_ids", [])
                for p in source_input.get("parameters", [])
            )
            _need(row["response_artifact"] not in responses,
                  "source evidence reuses another source response")
            responses.add(row["response_artifact"])
        summaries.append(dict(row))
    _need(annuals == 1 and len(responses) == len(rows) - 1 and used_web_source,
          "source evidence needs one native identity anchor and complete web captures")
    return {"schema_version": SCHEMA, "capture_id": cid,
            "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "validator_sha256": manifest["validator_sha256"],
            "native_modules": manifest["native_modules"], "sources": summaries,
            "native_logs": logs,
            "attestation": "unsigned_retained_tool_response_reference_not_independent_host_event"}
