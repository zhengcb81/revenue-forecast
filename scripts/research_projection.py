#!/usr/bin/env python3
"""Apply reviewed scope/scenario explanations before native input freezing.

The plan is authoring data, not a native schema, permission file or fee ledger.
This command changes explanations only; native validation remains downstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.authoring_projection import reconcile_authoring_explanations
from revenue_forecast import _atomic_write_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = reconcile_authoring_explanations(data, plan)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(args.output, rendered)
    print(json.dumps({"output": str(args.output),
                      "sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                      "operation": "reviewed_explanation_projection_not_quality_acceptance"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
