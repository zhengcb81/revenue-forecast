"""Read one existing NarrativeRef and emit a new linked RF input + trace.

MAIN runs the native forecast/validation/snapshot commands against linked-input.
This recipe never downloads, calls a model, or writes upstream research state.
``--narrative-reader-command-json`` is the public narrative reader port; omitting it keeps
the existing local CWP CLI deployment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from source_narrative_context import consume_narrative_input  # noqa: E402


def _reader_command(raw: str | None) -> tuple[str, ...] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, list) or not value or not all(
        isinstance(arg, str) and arg for arg in value
    ):
        raise ValueError("--narrative-reader-command-json must be a non-empty JSON array of strings")
    return tuple(value)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--narrative-request", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--catalog-config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--narrative-reader-command-json",
                        help="JSON argv prefix for the public narrative reader")
    args = parser.parse_args(argv)
    def read(path):
        return json.loads(path.read_text(encoding="utf-8"))
    data, receipt = consume_narrative_input(
        read(args.input), request=read(args.narrative_request), bindings=read(args.bindings),
        source_id=args.source_id, catalog_config=args.catalog_config.resolve(),
        reader_command=_reader_command(args.narrative_reader_command_json),
    )
    args.output_root.mkdir(parents=True, exist_ok=False)
    for name, value in (("linked-input.json", data), ("consumption.json", receipt)):
        (args.output_root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "dependencies": len(receipt["dependencies"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
