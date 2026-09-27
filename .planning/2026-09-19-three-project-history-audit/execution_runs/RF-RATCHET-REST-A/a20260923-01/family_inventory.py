"""RF-RATCHET-REST-A: test-family inventory for the three owned rows.

Method (reproducible, static):
  1. Parse every scripts/**/*.py, build a module import graph (absolute imports
     resolvable to a scripts/ module).
  2. Seed closure = the three owned modules.
  3. Upward closure = every scripts module that (transitively) imports a seed.
  4. Family = test files (tests/**/*.py + tools/tests/*.py) whose source
     references by name any module in the closure, OR references any of the
     three owned files by path/name (text-lock tests), OR is the ratchet test.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCRIPTS = ROOT / "scripts"

SEEDS = ("forecast.calc", "generate_input_template", "research.targets")

# map file -> dotted module name
mod_of_file: dict[Path, str] = {}
for p in SCRIPTS.rglob("*.py"):
    rel = p.relative_to(SCRIPTS)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    mod_of_file[p] = ".".join(parts)

all_mods = set(mod_of_file.values())


def imports_of(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    found: set[str] = set()
    base = mod_of_file[path]
    is_pkg = path.name == "__init__.py"
    # package that relative imports resolve against
    containing = base if is_pkg else base.rpartition(".")[0]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)  # 'forecast.calc' etc.
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = [p for p in containing.split(".") if p]
                up = node.level - 1
                if up > len(parts):
                    continue
                target = ".".join(parts[: len(parts) - up])
                if node.module:
                    target = f"{target}.{node.module}" if target else node.module
            else:
                target = node.module or ""
            if target:
                found.add(target)
            for alias in node.names:
                if alias.name != "*" and target:
                    found.add(f"{target}.{alias.name}")
    return found


# importer edges: mod -> set of mods it imports
graph = {m: set() for m in all_mods}
for path, mod in mod_of_file.items():
    for imp in imports_of(path):
        graph[mod].add(imp)

# upward closure
closure = set(SEEDS)
changed = True
while changed:
    changed = False
    for mod, imps in graph.items():
        if mod not in closure and imps & closure:
            closure.add(mod)
            changed = True

# text-path references (tests reading sources as text)
path_tokens = [
    "forecast/calc", "forecast.calc", "forecast\\calc",
    "generate_input_template",
    "research/targets", "research.targets", "research\\targets",
]

family = []
for base in (ROOT / "tests", ROOT / "tools" / "tests"):
    if not base.is_dir():
        continue
    for p in sorted(base.rglob("test_*.py")):
        text = p.read_text(encoding="utf-8", errors="replace")
        reasons = []
        for mod in sorted(closure):
            # match import-style references to the module name
            pat = re.compile(r"\b" + re.escape(mod) + r"\b")
            if pat.search(text):
                # confirm it's an import/reference not a coincidental word
                reasons.append(mod)
        if not reasons:
            for tok in path_tokens:
                if tok in text:
                    reasons.append(f"path:{tok}")
        if str(p).endswith("test_complexity_ratchet.py"):
            reasons.append("RATCHET-TEST")
        if reasons:
            family.append({
                "test": str(p.relative_to(ROOT)).replace("\\", "/"),
                "reasons": sorted(set(reasons))[:6],
                "n_reasons": len(set(reasons)),
            })

report = {
    "seeds": list(SEEDS),
    "closure_modules": sorted(closure),
    "n_closure": len(closure),
    "family": family,
    "n_family": len(family),
}
out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
print(f"closure ({len(closure)} modules):")
for m in sorted(closure):
    print("   ", m)
print(f"\nfamily: {len(family)} test files")
for f in family:
    print(f"   {f['test']}  <- {', '.join(f['reasons'][:3])}"
          + (" ..." if f["n_reasons"] > 3 else ""))
if out:
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\njson -> {out}")
