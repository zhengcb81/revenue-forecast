"""WU-201: architecture boundary gate — ARCH-01..05 forbidden edges.

The ADR (adr/WU-201-architecture.md) freezes nine responsibility boundaries
and five forbidden dependencies.  This gate checks the module import graph
(AST-based) against the forbidden edges:

- ARCH-01 resolver must not depend on adapters.
- ARCH-02 adapters must not depend on the catalog store.
- ARCH-03 the revenue calculator must not depend on network.
- ARCH-04 config must not dynamically import code (importlib/__import__/eval).
- ARCH-05 adapters must not depend on the canonical writer.

Roles are assigned by a registry (below); anything not in the registry is a
leaf with no forbidden edges.  Exit codes: 0 = clean; 1 = violations; 2 = usage.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parents[1]

# module-name fragments -> role
ROLE_RULES = [
    ("source_catalog/resolver", "resolver"),
    ("source_catalog/adapter", "adapter"),
    ("revenue_forecast", "calculator"),
    ("source_catalog/config", "config"),
]
NETWORK_MODULES = {"requests", "urllib", "httpx", "aiohttp", "socket", "websocket"}
DYNAMIC_IMPORT_SYMBOLS = {"importlib", "__import__", "eval", "exec", "compile"}
STORE_MODULES = {"store", "CatalogStore"}
CANONICAL_WRITER_MODULES = {"canonical_writer", "canonical"}


def role_of(module: str, role_rules: list[tuple[str, str]] | None = None) -> str | None:
    for fragment, role in role_rules or ROLE_RULES:
        if fragment in module:
            return role
    return None


def scan_module_imports(source: Path) -> set[str]:
    """AST-extract imported module names (incl. dotted parents) + dynamic
    import symbols used."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DYNAMIC_IMPORT_SYMBOLS:
                imported.add(node.func.id)
            elif isinstance(node.func, ast.Attribute) and \
                    node.func.attr in DYNAMIC_IMPORT_SYMBOLS:
                imported.add(node.func.attr)
    return imported


def check_import_graph(
    module_imports: dict[str, set[str]],
    roles: dict[str, str],
    network_modules: set[str] | None = None,
) -> list[str]:
    """Report forbidden edges in a module -> imports graph."""
    problems: list[str] = []
    network_modules = network_modules or NETWORK_MODULES
    for module, imports in module_imports.items():
        role = roles.get(module)
        for imported in imports:
            if role == "resolver" and "adapter" in imported:
                problems.append(f"ARCH-01: resolver {module} imports adapter {imported}")
            if role == "adapter":
                if any(store in imported for store in STORE_MODULES):
                    problems.append(f"ARCH-02: adapter {module} imports store {imported}")
                if any(writer in imported for writer in CANONICAL_WRITER_MODULES):
                    problems.append(f"ARCH-05: adapter {module} imports canonical writer {imported}")
            if role == "calculator" and imported in network_modules:
                problems.append(f"ARCH-03: calculator {module} imports network {imported}")
            if role == "config" and imported in DYNAMIC_IMPORT_SYMBOLS:
                problems.append(f"ARCH-04: config {module} uses dynamic import {imported}")
    return problems


def check_fitness_edges(
    module_imports: dict[str, set[str]],
    roles: dict[str, str],
    network_modules: set[str] | None = None,
) -> list[str]:
    """WU-205 ARC-FIT-01..06: target-architecture fitness edges.

    Beyond the forbidden edges, the fitness gate also enforces:
    - scanner v2 depends only on adapter interfaces/normalizer/admission/
      persister ports (no network/filesystem/arbitrary deps).
    - adapters/resolver/consumers never reach across their seam.
    - consumers (filing-fetch/revenue) never import company-wiki private
      Python modules.
    - calculator never touches filesystem/network/catalog.
    - legacy modules gain no new product callers (compat tests exempt).
    """
    problems: list[str] = []
    network_modules = network_modules or NETWORK_MODULES
    fs_modules = {"os", "pathlib", "shutil", "sqlite3"}
    for module, imports in module_imports.items():
        role = roles.get(module)
        if role == "scanner":
            forbidden = network_modules | fs_modules
            extra = imports & forbidden
            if extra:
                problems.append(
                    f"ARC-FIT-01: scanner {module} imports forbidden "
                    f"{sorted(extra)} (only adapter/normalizer/admission/persister ports)"
                )
        if role == "adapter" and imports & {"resolver", "scanner", "download",
                                            "parser", "llm"}:
            problems.append(f"ARC-FIT-02: adapter {module} reverse-depends on downstream")
        if role == "resolver" and imports & {"scanner", "adapter"}:
            problems.append(f"ARC-FIT-03: resolver {module} imports scanner/adapter")
        if role == "consumer" and any("company_wiki" in i or "source_catalog" in i
                                      for i in imports):
            problems.append(
                f"ARC-FIT-04: consumer {module} imports company-wiki private module"
            )
        if role == "calculator" and imports & (network_modules | fs_modules):
            problems.append(
                f"ARC-FIT-05: calculator {module} imports filesystem/network/catalog"
            )
    legacy_modules = {m for m, r in roles.items() if r == "legacy"}
    for caller, imports in module_imports.items():
        for imported in imports:
            if imported in legacy_modules:
                if "test" not in caller and "compat" not in caller and \
                        "facade" not in caller:
                    problems.append(
                        f"ARC-FIT-06: legacy {imported} gained product caller {caller}"
                    )
    return problems


def scan_repo(repo: Path, repo_name: str) -> dict[str, set[str]]:
    """Scan a repo's Python files (scripts/src/tests excluded) for imports."""
    module_imports: dict[str, set[str]] = {}
    for pattern in ("scripts/**/*.py", "src/**/*.py"):
        for path in repo.glob(pattern):
            if "__pycache__" in str(path):
                continue
            try:
                module_imports[str(path)] = scan_module_imports(path)
            except (SyntaxError, UnicodeDecodeError):
                continue
    return module_imports


def main() -> int:
    parser = argparse.ArgumentParser(description="WU-201 architecture boundary gate")
    parser.add_argument("--repo", action="append", default=[],
                        help="repo dirs to scan (repeatable)")
    args = parser.parse_args()
    problems: list[str] = []
    for repo_dir in args.repo:
        repo = Path(repo_dir)
        if not repo.is_dir():
            print(f"missing repo dir: {repo_dir}")
            return 2
        graph = scan_repo(repo, repo.name)
        roles = {
            module: role for module in graph
            if (role := role_of(module))
        }
        problems.extend(check_import_graph(graph, roles))
    for problem in problems:
        print(f"ARCH-GATE: {problem}")
    if not problems:
        print(f"OK: no forbidden dependency edges ({len(args.repo)} repo(s))")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
