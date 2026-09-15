"""Measure what the FC-1307-a guard WOULD report in another repository.

Read-only: imports company-wiki's guard (with -B so no bytecode lands there),
monkeypatches its REPO/BASELINE/REGISTRY to the target repo and an empty ratchet, and
prints the raw exposure by rule.  Nothing is executed in the target repo.

Usage: python -B measure_guard_exposure.py <repo-path> [roots...]
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

WIKI_SCRIPTS = Path(r"C:\Users\郑曾波\Projects\company-wiki\scripts")
sys.path.insert(0, str(WIKI_SCRIPTS))
sys.dont_write_bytecode = True

import host_assumption_guard as guard  # noqa: E402


def main(argv: list[str]) -> int:
    target = Path(argv[1]).resolve()
    roots = argv[2:] or ["tests", "tools", "src"]
    guard.REPO = target
    guard.BASELINE = target / "does-not-exist-baseline.json"
    guard.REGISTRY = target / "does-not-exist-registry.json"

    items: list[dict] = []
    scanned = 0
    for root in roots:
        base = target / root
        if not base.is_dir():
            continue
        for path in sorted(p for p in base.rglob("*.py") if p.name.endswith(".py")):
            scanned += 1
            items.extend(guard.scan_file(path))

    by_rule = collections.Counter(item["rule"] for item in items)
    by_file = collections.Counter(
        Path(item["file"]).resolve().relative_to(target).as_posix() for item in items
    )

    def rel(item: dict) -> str:
        path = Path(item["file"]).resolve().relative_to(target).as_posix()
        return f"{path}:{item['line']}"

    print(f"# {target.name}: scanned={scanned} violations={len(items)} by_rule={dict(by_rule)}")
    print(f"# files_with_violations={len(by_file)}")
    for rule in (guard.RULE_PATHS, guard.RULE_CAPABILITY, guard.RULE_FROZEN_HASH,
                 guard.RULE_SYNTAX, guard.RULE_UNREADABLE):
        hits = [item for item in items if item["rule"] == rule]
        if not hits:
            continue
        print(f"\n## {rule} ({len(hits)})")
        for item in hits:
            value = item["value"]
            if rule == guard.RULE_FROZEN_HASH:
                value = value[:16] + f"... (len {len(item['value'])})"
            print(f"  {rel(item)}  {value[:110]}")
    summary = {
        "target": str(target), "roots": roots, "scanned_py_files": scanned,
        "violations": len(items), "by_rule": dict(by_rule),
        "files_with_violations": len(by_file),
    }
    print("\n" + json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
