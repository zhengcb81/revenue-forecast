"""Per-function complexity, three metrics, for the RATCHET-FIX-B files.

gate   = tests/contract/test_fc1204_complexity_ratchet.py::_mccabe verbatim
         (the AUTHORITATIVE metric: 1 + If/For/While/And/Or-node/Except/
          comprehension/Assert/With + BoolOp(n-1); IfExp not counted).
auditB = the metric that reproduces the dispatch's 实际 numbers 3/9/11
         (gate's node set MINUS the And/Or double count, PLUS IfExp).
auditA = gate + IfExp + Match (the variant RATCHET-FIX-A prototyped).
"""
import ast
import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SRC = REPO / "src" / "company_wiki" / "source_catalog"
spec = importlib.util.spec_from_file_location(
    "rat", REPO / "tests" / "contract" / "test_fc1204_complexity_ratchet.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

BASE = {ast.If, ast.For, ast.While, ast.ExceptHandler, ast.comprehension,
        ast.Assert, ast.With}


def _count(node, *, ifexp: bool, opnode: bool) -> int:
    total = 0
    for child in ast.iter_child_nodes(node):
        total += _count(child, ifexp=ifexp, opnode=opnode)
    if isinstance(node, tuple(BASE)) or (isinstance(node, ast.And) and opnode) \
            or (isinstance(node, ast.Or) and opnode):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
    if ifexp and isinstance(node, ast.IfExp):
        total += 1
    if ifexp and isinstance(node, ast.Match):
        total += len(node.cases)
    return total


def per_func(text: str) -> dict:
    out = {}
    tree = ast.parse(text)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and not n.name.startswith("test_"):
            seg = ast.get_source_segment(text, n) or ""
            t = ast.parse(seg)
            gate = 1 + _count(t, ifexp=False, opnode=True)
            aB = 1 + _count(t, ifexp=True, opnode=False)
            aA = 1 + _count(t, ifexp=True, opnode=True)
            out[n.name] = (gate, aB, aA)
    return out


FILES = {
    "producer_events.py": 1,
    "identity_cli.py": 6,
    "artifact_read_model.py": 10,
}

PRE = Path(__file__).resolve().parent / "pre_image"
POST = Path(__file__).resolve().parent / "post_image"
PHASES = [("PRE-IMAGE", PRE), ("POST-IMAGE (worktree)", SRC)]
if (POST / "producer_events.py").is_file():
    PHASES.append(("POST-IMAGE (archived)", POST))

verdicts = {}
for label, root in PHASES:
    print(f"\n######## {label}: {root}")
    ok = True
    for rel, target in FILES.items():
        text = (root / rel).read_text(encoding="utf-8")
        print(f"\n== {rel}  target <= {target}  "
              f"file(_max_complexity) = {m._max_complexity(text)}  "
              f"frozen = {m.FROZEN_MAX.get(rel, '(new file -> 10)')}")
        rows = per_func(text)
        print(f"  {'function':32s} {'gate':>5s} {'auditB':>7s} {'auditA':>6s}")
        gmax = bmax = amax = 0
        for name, (g, b, a) in sorted(rows.items(), key=lambda kv: -max(kv[1])):
            gmax, bmax, amax = max(gmax, g), max(bmax, b), max(amax, a)
            flag = "  <-- over target" if max(g, b, a) > target else ""
            print(f"  {name:32s} {g:5d} {b:7d} {a:6d}{flag}")
        print(f"  FILE MAX: gate={gmax} auditB={bmax} auditA={amax} "
              f"-> {'PASS' if max(gmax, bmax, amax) <= target else 'FAIL'}")
        ok = ok and max(gmax, bmax, amax) <= target
    verdicts[label] = ok
    print(f"  #### {label} ALL WITHIN TARGET: {ok}")

print("\nVERDICTS:", verdicts)
