"""Print a page's text with character offsets (read-only, UTF-8 output)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SCRATCH = Path(__file__).resolve().parents[1] / "research" / "scratch"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", type=int, required=True)
    ap.add_argument("--source", default=None)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    rows = json.loads((SCRATCH / "pages.json").read_text(encoding="utf-8"))
    matches = [r for r in rows if r["pdf_page"] == args.page
               and (args.source is None or r["source"] == args.source)]
    if not matches:
        raise SystemExit(f"no page {args.page}")
    row = matches[0]
    text = row["text"]
    end = len(text) if args.end is None else args.end
    chunk = text[args.start:end]
    header = (f"# {row['source']} PDF p{row['pdf_page']} chars={len(text)} "
              f"text_sha256={row['text_sha256']}\n# span [{args.start},{end})\n")
    body = header + chunk + "\n"
    if args.out:
        args.out.write_text(body, encoding="utf-8")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
