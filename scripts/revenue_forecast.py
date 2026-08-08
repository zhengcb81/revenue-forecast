#!/usr/bin/env python3
"""CLI for auditable revenue-only forecasts."""

from __future__ import annotations

import argparse
import json
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
        # R4.2: the CLI reports the manifest hash of the installation it runs
        # from, so drift between canonical and installed copies is visible.
        from pathlib import Path as _Path

        root = _Path(__file__).resolve().parents[1]
        # Match tools/sync_installations.py installable_files so canonical and
        # installed copies of identical code report the same manifest hash
        # (only the files an installation actually contains are counted).
        _excluded_parts = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
        _root_files = {".gitignore", "CHANGELOG.md", "SKILL.md"}
        _root_directories = {"agents", "config", "references", "scripts", "tests"}
        installable: list[Path] = [root / name for name in _root_files]
        for directory in _root_directories:
            base = root / directory
            if base.is_dir():
                installable.extend(
                    path
                    for path in base.rglob("*")
                    if path.is_file()
                    and not (set(path.relative_to(root).parts) & _excluded_parts)
                    and path.suffix not in {".pyc", ".pyo"}
                )
        manifest = json.dumps(
            sorted(path.relative_to(root).as_posix() for path in installable),
            ensure_ascii=False,
        )
        import hashlib

        print(f"revenue-forecast {ENGINE_VERSION} manifest_sha256={hashlib.sha256(manifest.encode('utf-8')).hexdigest()[:16]}")
        return 0
    if args.input is None:
        parser.error("the following arguments are required: input")
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if args.validate_only and args.verbose:
            validate_document(data, collector=Collector())
        result = run_forecast(data)
        validate_forecast_output(result)
        if args.validate_only:
            print("valid")
            return 0
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        if args.markdown:
            args.markdown.write_text(render_markdown(result), encoding="utf-8")
    except (OSError, json.JSONDecodeError, ForecastInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
