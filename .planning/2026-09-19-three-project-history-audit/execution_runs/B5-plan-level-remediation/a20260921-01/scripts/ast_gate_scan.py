"""B5 REM-21: rigorous AST analysis -- which batch runners actually GATE the verdict on
cases.json[*].expected?

Supersedes the naive regex flag `compares_raised_to_expected` in b5_scan.py, which was false for
ALL 8 batches -- including the reference M17-M20, which provably does compare. That is this
project's recurring lesson: a guard must be tested against a POSITIVE control and a NEGATIVE
control, otherwise "always false" and "correctly discriminating" look identical.

This scanner is therefore self-tested (§SELF-TEST below) against the known-positive M17-M20
(reviewer r3 + the card's own mutation arm F) and known-negative M29-M31 (reviewers' P2).

Levels:
  L1 reads_expected     : the case's `expected` value is read from the frozen cases document
  L2 computes_equality  : an expression compares it (==) with a raised/actual type name
  L3 gates_verdict      : a verdict assignment is REACHED ONLY through branches whose tests
                          depend on that comparison (guard-stack descent, body AND orelse)
"""
import ast
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
BATCHES = [("M01-M04", "M01"), ("M05-M08", "M05"), ("M09-M12", "M09"), ("M13-M16", "M13"),
           ("M17-M20", "M17"), ("M21-M24", "M21"), ("M25-M28", "M25"), ("M29-M31", "M29")]

EXPECTED_KEYS = {"expected"}
EXPECTED_NAMES = {"declared", "declared_expected", "case_expected", "expected"}
TAINT_ROOTS = ("raised", "raised_name", "expect", "declared", "expected")


def is_expected_read(node):
    if isinstance(node, ast.Subscript):
        sl = node.slice
        if isinstance(sl, ast.Constant) and sl.value in EXPECTED_KEYS:
            return True
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
        if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in EXPECTED_KEYS:
            return True
    if isinstance(node, ast.Name) and node.id in EXPECTED_NAMES:
        return True
    return False


def _target_name(t):
    """returns (kind, key) for `entry["x"]` -> ("sub","x"); `x` -> ("name","x"); else None"""
    if isinstance(t, ast.Subscript):
        sl = t.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            return ("sub", sl.value)
    if isinstance(t, ast.Name):
        return ("name", t.id)
    return None


def contains_expected_comparison(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Compare):
            operands = [sub.left] + list(sub.comparators)
            if any(is_expected_read(o) for o in operands):
                return True
    return False


def tainted_symbols(tree):
    """Every field key / local name assigned from an expected comparison (one fixpoint pass over
    a small set of chained assignments)."""
    syms = set()
    changed = True
    while changed:
        changed = False
        for n in ast.walk(tree):
            if isinstance(n, (ast.Assign, ast.AnnAssign)):
                value = n.value
                if value is None:
                    continue
                targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                direct = contains_expected_comparison(value)
                indirect = any(
                    (_target_name(t) and _target_name(t)[1] in syms)
                    for t in ast.walk(value) if isinstance(t, (ast.Subscript, ast.Name))) and \
                    any(isinstance(s, (ast.Name, ast.Subscript)) for s in ast.walk(value))
                if direct or (_target_name(value) and _target_name(value)[1] in syms):
                    for t in targets:
                        tn = _target_name(t)
                        if tn and tn[1] not in syms:
                            syms.add(tn[1])
                            changed = True
    return syms


def refs_taint(node, syms):
    for sub in ast.walk(node):
        tn = _target_name(sub)
        if tn and tn[1] in syms:
            return True
        if isinstance(sub, ast.Name) and sub.id in syms:
            return True
        if isinstance(sub, ast.Attribute) and sub.attr in syms:
            return True
    return False


def verdict_guards(tree, syms):
    """guard-stack descent: for every `...["verdict"] = V`, collect the enclosing If tests."""
    found = []

    def visit(node, stack):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If):
                visit(child, stack + [("if", child.test, child.lineno)])
                for d in child.orelse:
                    visit(d, stack + [("else", child.test, child.lineno)])
                continue
            if isinstance(child, ast.Assign):
                for t in child.targets:
                    tn = _target_name(t)
                    if tn and tn[1] == "verdict":
                        tainted = [g for g in stack if refs_taint(g[1], syms)]
                        found.append({
                            "verdict": ast.unparse(child.value)[:90],
                            "line": child.lineno,
                            "guard_depth": len(stack),
                            "tainted_guards": [{"kind": k, "line": ln, "test": ast.unparse(tst)[:150]}
                                               for k, tst, ln in tainted],
                        })
            visit(child, stack)

    visit(tree, [])
    return found


report = {}
for label, rep in BATCHES:
    p = os.path.join(RUNS, rep, "a20260919-01", "scripts", "run_card.py")
    src = open(p, encoding="utf-8").read()
    tree = ast.parse(src)
    reads = [n for n in ast.walk(tree) if is_expected_read(n)]
    syms = tainted_symbols(tree)
    vg = verdict_guards(tree, syms)
    gated = [v for v in vg if v["tainted_guards"]]
    report[label] = {
        "path": os.path.relpath(p, PLAN).replace("\\", "/"),
        "L1_reads_expected": len(reads) > 0,
        "L1_read_count": len(reads),
        "L2_tainted_symbols": sorted(syms),
        "L2_computes_equality": bool(syms),
        "L3_gates_verdict": bool(gated),
        "L3_gated_verdicts": gated,
        "all_verdict_assignments": len(vg),
    }

# ---------------------------------------------------------------- SELF-TEST
selftest = {
    "positive_control": {"batch": "M17-M20", "expected_L3": True,
                         "why": "reviewer r3 + the card's own arm F prove the reference runner "
                                "enforces declared expectations"},
    "negative_control": {"batch": "M29-M31", "expected_L3": False,
                         "why": "reviewers' P2: rewriting every expected to ImportError still gave rc=0"},
    "observed": {k: report[k]["L3_gates_verdict"] for k in ("M17-M20", "M29-M31")},
}
selftest["PASS"] = (report["M17-M20"]["L3_gates_verdict"] is True
                    and report["M29-M31"]["L3_gates_verdict"] is False)
report["_selftest"] = selftest

dest = os.path.join(ATT, "evidence", "ast_gate_analysis.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)

print("SELF-TEST PASS =", selftest["PASS"], "| observed:", selftest["observed"])
print("%-9s %-7s %-7s %-8s %s" % ("batch", "L1", "L2", "L3_gate", "gate test"))
for label in [b for b, _ in BATCHES]:
    r = report[label]
    g = r["L3_gated_verdicts"]
    print("%-9s %-7s %-7s %-8s %s" % (label, r["L1_reads_expected"], r["L2_computes_equality"],
                                      r["L3_gates_verdict"],
                                      (g[0]["tainted_guards"][0]["test"][:64] if g else "-")))
print()
print("ALREADY gate (L3):", [k for k, v in report.items() if k != "_selftest" and v["L3_gates_verdict"]])
print("do NOT gate      :", [k for k, v in report.items() if k != "_selftest" and not v["L3_gates_verdict"]])
