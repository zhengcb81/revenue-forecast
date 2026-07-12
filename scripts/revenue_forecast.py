#!/usr/bin/env python3
"""CLI for auditable revenue-only forecasts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from revenue_core import ForecastInputError, run_forecast
from revenue_report import render_markdown, validate_forecast_output


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate a source-traceable revenue-only forecast")
    parser.add_argument("input", type=Path, help="input JSON document")
    parser.add_argument("--output", type=Path, help="JSON output path; stdout when omitted")
    parser.add_argument("--markdown", type=Path, help="optional Markdown report path")
    parser.add_argument("--validate-only", action="store_true", help="validate input and output without writing")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
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
