"""CLI for the read-only narrative adoption observation.

Explicit inputs only: one final forecast artifact (``--forecast``), optional
cross-check copies (``--input``, ``--snapshot``), explicit consumption
receipts and validated public narrative wires. No directory scanning, no
network, no database, no model execution. Every write goes to the explicit
``--output`` path, which must not exist and must not collide with any input.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for entry in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from company_wiki_narrative_contracts import NarrativeTransportError  # noqa: E402

if __package__:
    from . import audit  # noqa: E402
else:  # run as a plain script: python tools/narrative_adoption_audit/cli.py
    from narrative_adoption_audit import audit  # noqa: E402

DEFAULT_MAX_ITEMS = 20000
DEFAULT_MAX_INPUT_BYTES = 64 * 1024 * 1024


def _fail(message: str) -> int:
    print(f"narrative-adoption-audit: {message}", file=sys.stderr)
    return 2


def _read_bytes(path: Path, limit: int) -> bytes:
    size = path.stat().st_size
    if size > limit:
        raise audit.AdoptionAuditError(
            "resource_limit",
            f"{path} is {size} bytes; exceeds --max-input-bytes {limit}")
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = _gunzip_bounded(data, limit, path)
    return data


def _gunzip_bounded(data: bytes, limit: int, path: Path) -> bytes:
    """Stream-decompress at most ``limit + 1`` bytes before accepting input.

    The bound applies to the EXPANDED payload: a small archive that expands
    past the configured ceiling fails as a named resource error instead of
    allocating the whole expansion, and truncated or corrupt streams fail
    named instead of crashing.
    """
    import io

    reader = gzip.GzipFile(fileobj=io.BytesIO(data))
    out = io.BytesIO()
    remaining = limit + 1
    try:
        while remaining > 0:
            chunk = reader.read(min(65536, remaining))
            if not chunk:
                break
            out.write(chunk)
            remaining -= len(chunk)
    except (EOFError, gzip.BadGzipFile, OSError) as error:
        raise audit.AdoptionAuditError(
            "input_decompress_failed",
            f"{path} is not readable gzip: {error}") from error
    finally:
        reader.close()
    if remaining <= 0:
        raise audit.AdoptionAuditError(
            "resource_limit",
            f"{path} decompresses beyond --max-input-bytes {limit}")
    return out.getvalue()


def _read_json(path: Path, limit: int) -> dict:
    data = _read_bytes(path, limit)
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} does not hold a JSON object")
    return value


def _receipt_bytes(path: Path, limit: int) -> bytes:
    data = _read_bytes(path, limit)
    lines = [line for line in data.splitlines() if line.strip()]
    if len(lines) > 1:
        data = lines[0]
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="narrative-adoption-audit",
        description="Observe which narrative/source information the final "
                    "forecast artifact actually cites (read-only diagnostic).",
    )
    parser.add_argument("--forecast", type=Path, required=True,
                        help="final RF forecast output JSON")
    parser.add_argument("--input", type=Path, default=None,
                        help="optional input document for a binding cross-check")
    parser.add_argument("--snapshot", type=Path, default=None,
                        help="optional snapshot JSON for an identity cross-check")
    parser.add_argument("--consumption", type=Path, action="append", default=[],
                        help="narrative consumption receipt JSON (repeatable)")
    parser.add_argument("--narrative", nargs=3, action="append", default=[],
                        metavar=("REQUEST", "BUNDLE", "RECEIPT"),
                        help="public narrative wire triple: request JSON, "
                             "bundle bytes (.json/.json.gz), receipt bytes "
                             "(.json/.jsonl) (repeatable)")
    parser.add_argument("--output", type=Path, default=None,
                        help="write the report to this new path (default: stdout)")
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS,
                        help=f"resource bound on report items "
                             f"(default {DEFAULT_MAX_ITEMS})")
    parser.add_argument("--max-input-bytes", type=int,
                        default=DEFAULT_MAX_INPUT_BYTES,
                        help="resource bound per input file in bytes")
    parser.add_argument("--pretty", action="store_true",
                        help="indent the written report for humans")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        input_paths = [args.forecast, args.input, args.snapshot, *args.consumption]
        input_paths += [Path(item) for triple in args.narrative for item in triple]
        input_paths = [item for item in input_paths if item is not None]
        if args.output is not None:
            if args.output.exists():
                return _fail(f"refusing to overwrite existing output "
                             f"{args.output}")
            if args.output.resolve() in {item.resolve() for item in input_paths}:
                return _fail("--output must not point at an input file")
        forecast = _read_json(args.forecast, args.max_input_bytes)
        input_document = (
            _read_json(args.input, args.max_input_bytes)
            if args.input is not None else None)
        snapshot = (
            _read_json(args.snapshot, args.max_input_bytes)
            if args.snapshot is not None else None)
        receipts = [
            _read_json(path, args.max_input_bytes) for path in args.consumption]
        contexts: list[dict] = []
        refusals: list[dict] = []
        for request_path, bundle_path, receipt_path in args.narrative:
            try:
                contexts.append(audit.validate_narrative_wire(
                    _read_json(Path(request_path), args.max_input_bytes),
                    _read_bytes(Path(bundle_path), args.max_input_bytes),
                    _receipt_bytes(Path(receipt_path), args.max_input_bytes)))
            except NarrativeTransportError as error:
                refusals.append({"status": error.status, "reason": error.reason})
        report = audit.build_adoption_report(
            forecast,
            consumption_receipts=receipts,
            narrative_contexts=contexts,
            narrative_refusals=refusals,
            input_file_document=input_document,
            snapshot=snapshot,
            max_items=args.max_items,
        )
    except audit.AdoptionAuditError as error:
        return _fail(f"{error.code}: {error.detail}")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return _fail(f"cannot read inputs: {error}")
    if args.output is not None:
        if args.pretty:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(report, ensure_ascii=False, indent=2,
                                        sort_keys=True) + "\n")
        else:
            with args.output.open("xb") as stream:
                stream.write(audit.canonical_report_bytes(report))
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(audit.canonical_report_bytes(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
