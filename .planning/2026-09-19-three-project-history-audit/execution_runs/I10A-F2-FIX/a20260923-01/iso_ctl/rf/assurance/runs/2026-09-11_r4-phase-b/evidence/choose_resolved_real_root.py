"""Choose a real filing directory whose documents carry a resolved entity.

Read-only.  The A05-2b output already lists each candidate document with its entities, so
the choice needs no new catalog command.  ASCII-only output (the console mangles CJK).

    python choose_resolved_real_root.py [--min-candidates 1]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "a05-readonly-manifest-run.json"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-candidates", type=int, default=1)
    parser.add_argument("--out", type=Path, default=HERE / "b08-real-root-choice.json")
    args = parser.parse_args(argv)

    run = json.loads(RUN.read_text(encoding="utf-8"))
    entry = next(item for item in run["results"] if item["id"] == "A05-2b")
    rows = json.loads((HERE / entry["stdout_file"]).read_text(encoding="utf-8"))

    by_dir: Counter[str] = Counter()
    resolved_by_dir: Counter[str] = Counter()
    for row in rows:
        parent = Path(str(row.get("canonical_path") or "")).parent
        if not parent.is_dir():
            continue
        key = str(parent)
        by_dir[key] += 1
        entities = row.get("entities") or []
        names = [str(item.get("name") or "") for item in entities]
        if names and not all(name.startswith("Unresolved") for name in names):
            resolved_by_dir[key] += 1

    options = []
    for directory, candidates in by_dir.items():
        if candidates < args.min_candidates or resolved_by_dir.get(directory, 0) == 0:
            continue
        path = Path(directory)
        files = sum(1 for child in path.iterdir() if child.is_file())
        options.append({"directory": directory, "candidates": candidates,
                        "with_entity": resolved_by_dir[directory], "files": files})
    options.sort(key=lambda item: (item["files"], item["candidates"]))
    if not options:
        raise SystemExit("no real directory with an entity-resolved filing candidate")
    choice = options[0]
    payload = {"choice": choice, "options": options[:8]}
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({"chosen": {"files": choice["files"],
                                 "candidates": choice["candidates"],
                                 "with_entity": choice["with_entity"],
                                 "name_len": len(Path(choice["directory"]).name),
                                 "path_sha256_16": __import__("hashlib").sha256(
                                     choice["directory"].encode("utf-8")).hexdigest()[:16]}},
                     ensure_ascii=False, indent=2))
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
