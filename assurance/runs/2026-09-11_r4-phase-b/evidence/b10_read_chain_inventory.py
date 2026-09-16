"""B10 recon (read-only): every place that PARSES the shared documents.metadata_json column.

B10 is "converge to a single read chain; old entry points only as explicit version
adapters".  The first step is not to change anything but to enumerate, by AST rather than
by grep, every site that parses that column and WHERE it lives (module + enclosing symbol),
so the convergence gate's ratchet baseline is machine-derived instead of hand-written.

    python b10_read_chain_inventory.py [--roots src/company_wiki/source_catalog] [--out PATH]
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIKI = HERE.parents[4] / "company-wiki"
COLUMN = "metadata_json"


def _call_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - unparse is best-effort for diagnostics
        return "<unparseable>"


def _enclosing(tree: ast.AST) -> dict[int, ast.AST]:
    owner: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for child in ast.walk(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                owner.setdefault(id(child), node)
    return owner


def _symbol_source(source: str, node: ast.AST | None) -> str:
    if node is None or not hasattr(node, "lineno"):
        return ""
    end = getattr(node, "end_lineno", None) or node.lineno
    return "\n".join(source.splitlines()[node.lineno - 1:end])


def scan(root: Path) -> list[dict]:
    found: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        owner = _enclosing(tree)
        lines = source.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name not in {"loads", "metadata_object"}:
                continue
            arguments = [_call_text(argument) for argument in node.args]
            text = " ".join(arguments)
            enclosing = owner.get(id(node))
            symbol_text = _symbol_source(source, enclosing)
            # Two shapes reach the shared column: the argument names it, or the enclosing
            # symbol handles it under another name (`json.loads(row[0] or "{}")` inside a
            # function that selects `metadata_json`).  The first version of this inventory
            # only saw the first shape and therefore missed prompt_injection*.py and
            # extraction_quality.py entirely.
            names_column = COLUMN in text
            symbol_handles_column = COLUMN in symbol_text
            if name == "loads" and not (names_column or symbol_handles_column):
                continue
            confirmed = name == "loads" and names_column
            found.append({
                "module": path.name,
                "symbol": getattr(enclosing, "name", "<module>"),
                "line": node.lineno,
                "callee": name,
                "names_column_in_argument": names_column,
                "column_referenced_in_symbol": symbol_handles_column,
                # CONFIRMED = the argument itself names the shared column (`row["metadata_json"]`).
                # HEURISTIC = only the enclosing symbol mentions it, which also catches readers
                # that renamed the value (`json.loads(row[0] or "{}")`) AND false positives -
                # measured: store.read_pipeline_status parses `report_json`, not this column.
                # The convergence ratchet must key on CONFIRMED sites; the heuristic list is
                # reported for a human to classify, never enforced automatically.
                "confidence": "confirmed" if confirmed else (
                    "single_chain" if name == "metadata_object" else "heuristic"),
                "argument": text[:90],
                "source": (lines[node.lineno - 1].strip()[:90] if node.lineno <= len(lines) else ""),
            })
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roots", type=Path, nargs="+",
                        default=[WIKI / "src" / "company_wiki" / "source_catalog"])
    parser.add_argument("--out", type=Path, default=HERE / "b10-read-chain-inventory.json")
    args = parser.parse_args(argv)

    sites: list[dict] = []
    for root in args.roots:
        if not root.is_dir():
            raise SystemExit(f"root does not exist: {root}")
        sites.extend(scan(root))
    by_module: dict[str, list[dict]] = {}
    for site in sites:
        by_module.setdefault(site["module"], []).append(site)

    payload = {
        "tool": "b10_read_chain_inventory.py",
        "note": ("AST inventory of every parse of the shared documents.metadata_json column. "
                 "`metadata_object` calls are the SINGLE CHAIN; `loads` calls are direct "
                 "readers (candidates for convergence or for an explicit adapter)."),
        "roots": [str(root) for root in args.roots],
        "totals": {
            "sites": len(sites),
            "single_chain_calls": sum(1 for site in sites if site["callee"] == "metadata_object"),
            "direct_readers": sum(1 for site in sites if site["callee"] == "loads"),
            "confirmed_direct_readers": sum(1 for site in sites
                                            if site["confidence"] == "confirmed"),
            "heuristic_candidates": sum(1 for site in sites
                                        if site["confidence"] == "heuristic"),
            "modules_with_direct_readers": sum(
                1 for module, items in by_module.items()
                if any(item["callee"] == "loads" for item in items)),
        },
        "by_module": {module: items for module, items in sorted(by_module.items())},
        "sites": sites,
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({"totals": payload["totals"],
                      "direct_reader_modules": sorted(
                          module for module, items in by_module.items()
                          if any(item["callee"] == "loads" for item in items))},
                     ensure_ascii=True, indent=2))
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
