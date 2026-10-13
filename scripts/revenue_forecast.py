#!/usr/bin/env python3
"""CLI for auditable revenue-only forecasts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from revenue_core import (
    Collector,
    ENGINE_VERSION,
    ForecastInputError,
    run_forecast,
    validate_document,
)
from revenue_report import render_markdown, validate_forecast_output


def _atomic_write_text(path: Path, text: str) -> None:
    """REV-09 (ZR-710): atomically write a text file — write to a same-dir
    temporary file, fsync, then os.replace.  A process interruption at any
    point leaves either the previous file or no file, never a half-written
    artifact (no orphans)."""
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    try:
        with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_forecast(data: dict, *, mode: str = "formal") -> dict:
    """ZR-701: pure forecast preparation — compute and validate the result
    with zero IO side effects.  Same input always yields the same result
    (deterministic engine); the caller owns all filesystem effects.

    *mode*: ``"formal"`` registers the publication (write side effect owned
    by the caller's engine), ``"draft"`` validates strongly but builds only
    a draft receipt and writes nothing — the zero-write validate-only path.
    """
    result = run_forecast(data, mode=mode)
    if mode == "formal":
        # strong formal output validation (draft results were already
        # strongly validated inside run_forecast before the draft receipt)
        validate_forecast_output(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate a source-traceable revenue-only forecast")
    parser.add_argument(
        "input", type=Path, nargs="?", help="input JSON document (required unless --version)"
    )
    parser.add_argument("--output", type=Path, help="JSON output path; stdout when omitted")
    parser.add_argument("--markdown", type=Path, help="optional Markdown report path")
    parser.add_argument("--validate-only", action="store_true", help="validate input and output without writing")
    parser.add_argument("--verbose", action="store_true", help="with --validate-only, report every input violation in one pass")
    parser.add_argument(
        "--version",
        action="store_true",
        help="print engine version and this installation's manifest hash (R4.2)",
    )
    args = parser.parse_args()
    if args.version:
        # The shared owned-byte inventory matches the installer exactly.
        # This is a diagnostic digest, never a publication permission token.
        from installation_manifest import manifest_sha256
        root = Path(__file__).resolve().parents[1]
        print(f"revenue-forecast {ENGINE_VERSION} manifest_sha256={manifest_sha256(root)[:16]}")
        return 0
    if args.input is None:
        parser.error("the following arguments are required: input")
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if args.validate_only and args.verbose:
            validate_document(data, collector=Collector())
        # ZR-701: validate-only runs the engine in draft mode — strong
        # validation, no publication registration, zero writes.
        result = prepare_forecast(data, mode="draft" if args.validate_only else "formal")
        if args.validate_only:
            print("valid")
            return 0
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            _atomic_write_text(args.output, rendered)
        else:
            print(rendered, end="")
        if args.markdown:
            _atomic_write_text(args.markdown, render_markdown(result))
    except (OSError, json.JSONDecodeError, ForecastInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
