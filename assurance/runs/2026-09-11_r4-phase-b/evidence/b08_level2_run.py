"""Run the G8 level-2 build against a real filing directory chosen from the A05 output.

Read-only w.r.t. production: the chosen directory is referenced as a read-only root and
its files are hashed before/after (see b08_isolated_env.build_level2).  ASCII-only console
output on purpose - this console mangles CJK paths, and a mangled path in a log is worse
than no path.

    python b08_level2_run.py [--min-candidates 2] [--isolated-root PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import b08_isolated_env as env  # noqa: E402

RUN = HERE / "a05-readonly-manifest-run.json"
DEFAULT_ISOLATED = Path(env.tempfile.gettempdir()) / "b08-level2-isolated"


def _candidates() -> list[tuple[str, int, int]]:
    run = json.loads(RUN.read_text(encoding="utf-8"))
    entry = next(item for item in run["results"] if item["id"] == "A05-2b")
    rows = json.loads((HERE / entry["stdout_file"]).read_text(encoding="utf-8"))
    counts: Counter[str] = Counter()
    for row in rows:
        parent = Path(str(row.get("canonical_path") or "")).parent
        if parent.is_dir():
            counts[str(parent)] += 1
    out: list[tuple[str, int, int]] = []
    for directory, candidates in counts.items():
        path = Path(directory)
        files = sum(1 for child in path.iterdir() if child.is_file())
        out.append((directory, candidates, files))
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-candidates", type=int, default=2)
    parser.add_argument("--isolated-root", type=Path, default=DEFAULT_ISOLATED)
    parser.add_argument("--manifest-out", type=Path,
                        default=HERE / "b08-level2-evidence.json")
    args = parser.parse_args(argv)

    options = [item for item in _candidates() if item[1] >= args.min_candidates]
    options.sort(key=lambda item: (item[2], item[1]))
    if not options:
        raise SystemExit("no real directory with enough filing candidates was found")
    directory, candidates, files = options[0]
    print(f"chosen real root: files={files} candidates={candidates} "
          f"name_len={len(Path(directory).name)}")
    print(f"chosen real root sha256[:16]={env.hashlib.sha256(directory.encode('utf-8')).hexdigest()[:16]}")

    code = env.build_level2(Path(directory), args.isolated_root, args.manifest_out)
    evidence = json.loads(args.manifest_out.read_text(encoding="utf-8"))
    print(json.dumps({
        "isolated_counts": evidence["isolated_counts"],
        "real_root_unchanged": evidence["real_root_unchanged"],
        "production_catalog_unchanged": evidence["production_catalog_unchanged"],
        "real_files_hashed": evidence["real_root_before"]["file_count"],
        "evidence_file": args.manifest_out.name,
    }, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
