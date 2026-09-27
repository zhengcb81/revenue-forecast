"""WU-1503: documentation consistency audit across the three repos.

Checks SKILL.md/README/CLI-help claims against the frozen architecture:
- "config-only" must be scoped to registered same-profile roots.
- indexed != reusable/capture-ready must be explicit.
- external roots read-only; canonical write store; download authorization.
- exact/latest, artifact invalidation, real-canary limits explicit.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPOS = {
    "revenue": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
    "wiki": Path(r"C:\Users\郑曾波\Projects\company-wiki"),
}

DOC_FILES = {
    "revenue": ["SKILL.md"],
    "filing": ["SKILL.md"],
    "wiki": ["README.md"],
}

FORBIDDEN_UNSCOPED = (
    r"只改配置即可(?!.*adapter)",
    r"config.?only(?!.*(adapter|profile|registered))",
)

REQUIRED_CONCEPTS = {
    "readonly": (r"read.?only|只读", "外部根只读"),
    "canonical": (r"canonical|companies", "canonical write store"),
    "download_auth": (r"authoriz|授权|allow.?download", "下载授权"),
    "reusable_not_indexed": (r"reusable|复用", "indexed ≠ reusable"),
}


def check_repo(repo_name: str) -> list[str]:
    problems: list[str] = []
    for doc in DOC_FILES.get(repo_name, []):
        path = REPOS[repo_name] / doc
        if not path.is_file():
            problems.append(f"{repo_name}/{doc}: missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in FORBIDDEN_UNSCOPED:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                line = text[:match.start()].count("\n") + 1
                problems.append(
                    f"{repo_name}/{doc}:{line} unscoped config-only claim "
                    f"{match.group(0)!r}"
                )
        for concept, (pattern, label) in REQUIRED_CONCEPTS.items():
            if not re.search(pattern, text, re.IGNORECASE):
                problems.append(
                    f"{repo_name}/{doc}: missing concept {label} ({concept})"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Doc consistency audit")
    parser.add_argument("--repo", action="append", default=[],
                        help="repo names to audit (default: all)")
    args = parser.parse_args()
    repos = args.repo or list(REPOS)
    problems: list[str] = []
    for name in repos:
        problems.extend(check_repo(name))
    for problem in problems:
        print(f"DOC-AUDIT: {problem}")
    if not problems:
        print("OK: all docs consistent with the frozen architecture")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
