"""Assemble explicit operating research with actual prepared source captures.

This recipe does not invent business facts or estimate missing inputs. It joins
researcher-authored native values, typed inventory/calibrations and W04 captures.
Optional narrative bindings perform an actual verified read through W04.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from contracts.evidence import canonical_sha256, require  # noqa: E402
from revenue_core import validate_document  # noqa: E402
from research.evidence_roles import analyze_operating_research  # noqa: E402
from research.timing_bridge import build_quarter_delay_bridge  # noqa: E402


def _load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def assemble_case(data, research, preparations, *, as_of):
    out = deepcopy(data)
    require(out["as_of_date"] == as_of, "assembly information date must match native input")
    out["operating_research"] = deepcopy(research)
    sources = {s["source_id"]: s for s in out["sources"]}
    prepared_ids = []
    for preparation in preparations:
        require(preparation.get("schema_version") == "source-preparation-result/1", "assembly requires actual W04 preparation result")
        source = deepcopy(preparation["source"])
        sid = source["source_id"]
        require(sid in sources and sid not in prepared_ids, "prepared source must identify one input source")
        old = sources[sid]
        require(old["capture"]["snapshot_sha256"] == source["capture"]["snapshot_sha256"], "prepared source bytes differ from authored input")
        for claim in out["evidence_claims"]:
            if claim["source_id"] == sid:
                require(claim["content_sha256"] == source["capture"]["snapshot_sha256"], "claim is not bound to prepared original bytes")
                claim["capture_receipt_sha256"] = source["capture"]["receipt_sha256"]
        sources[sid] = source
        prepared_ids.append(sid)
    out["sources"] = [sources[s["source_id"]] for s in out["sources"]]
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--company", help="caller label only; no company-specific logic")
    parser.add_argument("--input", type=Path, required=True, help="authored native input with source-bound claims and explicit values")
    parser.add_argument("--research", type=Path, required=True, help="operating-research/1 observations, inventory and calibrations")
    parser.add_argument("--preparation", type=Path, action="append", required=True, help="actual W04 source-preparation-result/1; repeat")
    parser.add_argument("--discovery", type=Path, required=True, help="W03 bounded discovery receipt retained by SHA, not treated as read coverage")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--narrative-request", type=Path)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--source-id")
    parser.add_argument("--catalog-config", type=Path)
    parser.add_argument("--delay-request", type=Path, help="optional independent illustrative dated bridge request")
    args = parser.parse_args(argv)
    require(not args.output_root.exists(), "assembly output root must be initially absent")
    data = assemble_case(_load(args.input), _load(args.research), [_load(p) for p in args.preparation], as_of=args.as_of)
    consumption = None
    if args.narrative_request is not None:
        require(args.bindings is not None and args.source_id is not None and args.catalog_config is not None, "narrative read requires bindings/source/config")
        from source_narrative_context import consume_narrative_input
        data, consumption = consume_narrative_input(data, request=_load(args.narrative_request),
            bindings=_load(args.bindings), source_id=args.source_id, catalog_config=args.catalog_config)
    elif any(x is not None for x in (args.bindings, args.source_id, args.catalog_config)):
        raise ValueError("narrative binding flags require --narrative-request")
    validated = validate_document(data)
    diagnostic = analyze_operating_research(data, validated)
    discovery = _load(args.discovery)
    require(isinstance(discovery, dict), "discovery receipt must be a JSON object")
    receipt = {"schema_version": "auditable-case-assembly/1", "as_of_date": args.as_of,
        "company_label": args.company, "input_sha256": canonical_sha256(data),
        "discovery_receipt_sha256": hashlib.sha256(args.discovery.read_bytes()).hexdigest(),
        "preparation_receipt_sha256": [hashlib.sha256(p.read_bytes()).hexdigest() for p in args.preparation],
        "source_bindings": [{"source_id": s["source_id"], "snapshot_sha256": s["capture"]["snapshot_sha256"],
                            "capture_receipt_sha256": s["capture"]["receipt_sha256"],
                            "source_ref": s.get("company_wiki_trace", {}).get("source_ref")} for s in data["sources"]],
        "narrative_status": "not_consumed" if consumption is None else consumption["status"],
        "new_supplier_calls": 0, "new_model_calls": 0, "new_downloads": 0,
        "limitations": ["Discovery receipt presence is not business content/read completeness.",
                        "Authored values and economic scope require original evidence review; unknown ranges stay unverified."]}
    args.output_root.mkdir(parents=True)
    outputs = {"linked-input.json": data, "inventory.json": diagnostic["inventory"],
               "calibration.json": diagnostic["calibrations"], "research-adequacy.json": diagnostic,
               "assembly.json": receipt}
    if consumption is not None:
        outputs["narrative-consumption.json"] = consumption
    if args.delay_request is not None:
        stressed, stress_receipt = build_quarter_delay_bridge(data, **_load(args.delay_request))
        stressed["forecast_version"] = data.get("forecast_version", args.as_of + "-v1") + "-illustrative-stress"
        validate_document(stressed)
        outputs["stress-input.json"] = stressed
        outputs["stress-receipt.json"] = stress_receipt
    for filename, value in outputs.items():
        (args.output_root / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "assembled", "input_sha256": receipt["input_sha256"],
                     "narrative_status": receipt["narrative_status"], "economic_review": "not_inferred"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
