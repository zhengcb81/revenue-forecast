"""FC-1301 inventory: which reason codes reach the taxonomy registry, and which do not.

The contract gate (company-wiki tests/contract/test_fc1301_reason_taxonomy.py) scans
three REGEX literal patterns, so a reason passed POSITIONALLY is invisible to it.  This
tool does the AST version of that scan:

  * collects every function/method signature in the package, plus dataclass field
    order (a dataclass __init__ is generated, so its "signature" is its field list);
  * for every call whose callee resolves inside the package, maps positional and
    keyword arguments onto those parameter names;
  * reports every argument that lands on a parameter named ``reason``/``*_reason``
    (or a dataclass field of that name) whose value is a string literal, with a
    registered / unregistered verdict against ``observability.REASONS``.

It is READ-ONLY: nothing is written except the JSON it prints.  Positional literals on
UNRESOLVED callees (imported from outside the scanned roots) are reported separately so
the inventory cannot look complete when it is not.

    python fc1301_reason_inventory.py [--root src/company_wiki] [--json-out PATH]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
# HERE = <Projects>/revenue-forecast/assurance/runs/<run>/evidence, so:
#   parents[3] = revenue-forecast, parents[3].parent = <Projects>
REPO = HERE.parents[3]
PROJECTS = REPO.parent
WIKI = PROJECTS / "company-wiki"
DEFAULT_ROOT = WIKI / "src" / "company_wiki"
REASON_PARAM = "reason"


@dataclass
class Signature:
    params: list[str] = field(default_factory=list)
    kind: str = "function"                  # function | dataclass | class


def _param_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args = node.args
    names = [arg.arg for arg in (*args.posonlyargs, *args.args)]
    if args.vararg:
        names.append(f"*{args.vararg.arg}")
    names.extend(arg.arg for arg in args.kwonlyargs)
    if args.kwarg:
        names.append(f"**{args.kwarg.arg}")
    return names


def collect_signatures(root: Path) -> dict[str, list[Signature]]:
    """name -> ALL signatures found for that name (B-VR1301-02: the first version kept
    only the first definition, which made the inventory under-report exactly like the
    gate it was measuring - a name like ``_reject`` has several shapes in this tree)."""
    signatures: dict[str, list[Signature]] = {}
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                signatures.setdefault(node.name, []).append(Signature(_param_names(node)))
            elif isinstance(node, ast.ClassDef):
                is_dataclass = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass")
                    or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                    for d in node.decorator_list
                )
                fields = [
                    stmt.target.id
                    for stmt in node.body
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
                ]
                if is_dataclass and fields:
                    signatures.setdefault(node.name, []).append(
                        Signature(fields, kind="dataclass"))
                else:
                    signatures.setdefault(node.name, []).append(Signature(kind="class"))
    return signatures


def _callee_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _literal(value: ast.AST) -> str | None:
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


REASON_SUFFIXES = ("reason", "_reason")
# `reason` has TWO meanings in this codebase: a taxonomy CODE (snake_case, must be in
# REASONS) and a free-text explanation ("receipt reviewed_at is not ISO-8601 UTC").
# Only the first kind is this package's business, so the inventory classifies by shape
# instead of pretending every reason= string is a code.
CODE_LIKE = re.compile(r"^[a-z][a-z0-9_]*$")


def _is_code_like(value: str) -> bool:
    return bool(CODE_LIKE.match(value))


def _is_reason_param(name: str) -> bool:
    return name == REASON_PARAM or name.endswith(REASON_SUFFIXES)


def inventory(root: Path, registered: dict[str, str]) -> dict:
    signatures = collect_signatures(root)
    resolved: list[dict] = []
    unresolved: list[dict] = []
    keyword_hits: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text)
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = path.relative_to(WIKI).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = _callee_name(node.func)
            for keyword in node.keywords:
                if keyword.arg and _is_reason_param(keyword.arg):
                    literal = _literal(keyword.value)
                    if literal:
                        keyword_hits.append({
                            "file": rel, "line": node.lineno, "callee": callee,
                            "param": keyword.arg, "value": literal,
                            "registered": literal in registered,
                        })
            signature_list = signatures.get(callee)
            if not signature_list or all(sig.kind == "class" for sig in signature_list):
                if node.args and any(_literal(arg) for arg in node.args):
                    unresolved.append({
                        "file": rel, "line": node.lineno, "callee": callee,
                        "positional_literals": [v for v in map(_literal, node.args) if v],
                        "note": "callee not resolvable in the scanned roots",
                    })
                continue
            for index, arg in enumerate(node.args):
                literal = _literal(arg)
                if literal is None:
                    continue
                # a position counts as a reason position if ANY definition names it so
                matched = [
                    sig for sig in signature_list
                    if index < len(sig.params) and _is_reason_param(sig.params[index])
                ]
                if not matched:
                    continue
                resolved.append({
                    "file": rel, "line": node.lineno, "callee": callee,
                    "param": matched[0].params[index],
                    "definitions": len(signature_list), "kind": matched[0].kind,
                    "value": literal, "registered": literal in registered,
                })
    def _summary(items: list[dict]) -> dict:
        values: dict[str, int] = {}
        for item in items:
            values[item["value"]] = values.get(item["value"], 0) + 1
        code_like = [item for item in items if _is_code_like(item["value"])]
        free_text = [item for item in items if not _is_code_like(item["value"])]
        code_values: dict[str, int] = {}
        for item in code_like:
            code_values[item["value"]] = code_values.get(item["value"], 0) + 1
        return {
            "sites": len(items),
            "distinct_values": len(values),
            "code_like_sites": len(code_like),
            "free_text_sites": len(free_text),
            "unregistered_sites": sum(1 for item in items if not item["registered"]),
            "unregistered_code_like_sites": sum(
                1 for item in code_like if not item["registered"]),
            # THE actionable list: snake_case values that are not in the registry
            "unregistered_code_like_values": sorted(
                value for value in code_values
                if not any(i["registered"] for i in code_like if i["value"] == value)
            ),
            "free_text_examples": sorted({item["value"] for item in free_text})[:6],
            "values": dict(sorted(values.items(), key=lambda kv: (-kv[1], kv[0]))),
        }
    return {
        "root": root.relative_to(WIKI).as_posix(),
        "registered_codes": len(registered),
        "resolved_positional": resolved,
        "keyword_style": keyword_hits,
        "unresolved_callees": unresolved[:40],
        "unresolved_count": len(unresolved),
        "summary": {
            "resolved_positional": _summary(resolved),
            "keyword_style": _summary(keyword_hits),
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args(argv)

    # Fail loudly instead of reporting an empty inventory: the first version of this
    # tool computed WIKI one level too high (parents[3] is the REPOSITORY, not its
    # parent), the root did not exist, rglob yielded nothing and every count came out
    # 0 - a silent no-op that looks like "no findings".  Third time this session that
    # a parents[N] slip produced a false negative, hence the assertions.
    if not args.root.is_dir():
        raise SystemExit(f"scan root does not exist: {args.root}")
    scanned = sorted(args.root.rglob("*.py"))
    if not scanned:
        raise SystemExit(f"scan root has no .py files: {args.root}")

    observability = WIKI / "src" / "company_wiki" / "source_catalog" / "observability.py"
    if not observability.is_file():
        raise SystemExit(f"registry module not found: {observability}")
    sys.path.insert(0, str(WIKI / "src"))
    from company_wiki.source_catalog import observability as obs  # noqa: PLC0415

    if Path(obs.__file__).resolve() != observability.resolve():
        raise SystemExit(
            f"imported a DIFFERENT copy of the registry: {obs.__file__} != {observability}"
        )

    result = inventory(args.root, dict(obs.REASONS))
    result["scanned_files"] = len(scanned)
    result["registry_module"] = str(observability)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        args.json_out.write_text(payload + "\n", encoding="utf-8", newline="")
    summary = result["summary"]
    print(f"scanned {len(scanned)} files under {args.root}")
    print(f"registered codes: {result['registered_codes']} (from {observability.name})")
    for style in ("resolved_positional", "keyword_style"):
        item = summary[style]
        print(f"{style}: sites={item['sites']} code_like={item['code_like_sites']} "
              f"free_text={item['free_text_sites']} "
              f"unregistered_code_like={item['unregistered_code_like_sites']}")
        if item["unregistered_code_like_values"]:
            print(f"  unregistered codes: {', '.join(item['unregistered_code_like_values'][:24])}")
        if item["free_text_examples"]:
            print(f"  (free-text examples, not codes: {len(item['free_text_examples'])} shown)")
    print(f"unresolved callees with positional literals: {result['unresolved_count']}")
    if args.json_out:
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
