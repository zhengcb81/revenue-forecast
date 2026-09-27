"""List the distinct parent directories of the filing candidates, with file counts.

Read-only: this only lists directories that the approved `query` command already named.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = json.loads((HERE / "a05-readonly-manifest-run.json").read_text(encoding="utf-8"))
entry = next(item for item in RUN["results"] if item["id"] == "A05-2b")
rows = json.loads((HERE / entry["stdout_file"]).read_text(encoding="utf-8"))

parents: Counter[str] = Counter()
sizes: dict[str, int] = {}
for row in rows:
    path = Path(str(row.get("canonical_path") or ""))
    if not path.name:
        continue
    parents[str(path.parent)] += 1
    sizes[str(path.parent)] = sizes.get(str(path.parent), 0) + int(row.get("byte_size") or 0)

print(f"candidate filings: {len(rows)}; distinct parent dirs: {len(parents)}")
for directory, count in parents.most_common(12):
    existence = Path(directory).is_dir()
    numeric = 0
    if existence:
        try:
            numeric = sum(1 for child in Path(directory).iterdir() if child.is_file())
        except OSError:
            numeric = -1
    print(f"  files_in_dir={numeric:>5} candidates={count:>3} sum_bytes={sizes[directory]:>10} "
          f"exists={existence}  ...{directory[-80:]}")
