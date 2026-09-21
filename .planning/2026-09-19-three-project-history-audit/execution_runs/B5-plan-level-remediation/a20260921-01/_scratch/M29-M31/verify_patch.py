"""Verify the REM-21 M29-M31 patch: syntax, AST delta, insertion lines, diff.

Read-only with respect to the historical tree.  Emits runner.diff into the batch
directory and prints the measured insertion points for evidence.json.
"""
import ast
import difflib
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.abspath(os.path.join(HERE, "..", "..", "M29-M31"))
BEFORE = os.path.join(BATCH, "run_card_before.py")
AFTER = os.path.join(BATCH, "run_card.py")
DIFF = os.path.join(BATCH, "runner.diff")

NEW_ANCHORS = [
    ("cases_json_declared_expectations_usable", "per-set declared-expectation usability gate (rc=2 prerequisite)"),
    ("raised_name == declared", "EXACT type-name equality comparison (never isinstance)"),
    ("FAIL_declared_expectation_mismatch", "mismatch verdict label"),
    ("NOT_JUDGED_declaration_unusable", "unusable-declaration verdict label"),
    ("cases_json_declared_expectation_missing:", "rc=2 reason naming the unusable cases"),
]


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def main():
    before_text = read(BEFORE)
    after_text = read(AFTER)
    out = []

    before_ast = ast.parse(before_text)
    after_ast = ast.parse(after_text)
    out.append("PARSE OK: both files parse under %s" % sys.version.split()[0])

    # top-level statement-level AST delta (line-insensitive): which top-level defs changed
    def top_map(tree):
        return {type(stmt).__name__ + ":" + getattr(stmt, "name", ""): ast.dump(stmt)
                for stmt in tree.body}

    bmap, amap = top_map(before_ast), top_map(after_ast)
    out.append("top-level keys before: %s" % sorted(bmap))
    out.append("top-level keys after : %s" % sorted(amap))
    changed = sorted(k for k in bmap if k in amap and bmap[k] != amap[k])
    added = sorted(set(amap) - set(bmap))
    removed = sorted(set(bmap) - set(amap))
    out.append("changed top-level statements: %s" % changed)
    out.append("added top-level statements: %s" % added)
    out.append("removed top-level statements: %s" % removed)

    # rc constants must be byte-identical
    b_rc = [ln for ln in before_text.splitlines() if ln.startswith("EXIT_")]
    a_rc = [ln for ln in after_text.splitlines() if ln.startswith("EXIT_")]
    out.append("rc constants identical: %s (%s)" % (b_rc == a_rc, a_rc))

    # dunder main exception-handler tail must be unchanged
    tail_b = before_text[before_text.index('if __name__ == "__main__":'):]
    tail_a = after_text[after_text.index('if __name__ == "__main__":'):]
    out.append("__main__ tail byte-identical: %s" % (tail_b == tail_a))

    # insertion points: 1-based line of each new anchor in the AFTER file
    after_lines = after_text.splitlines()
    for needle, what in NEW_ANCHORS:
        hits = [i + 1 for i, ln in enumerate(after_lines) if needle in ln]
        out.append("ANCHOR %-42s lines=%s | %s" % (needle, hits, what))

    # unified diff
    diff_lines = list(difflib.unified_diff(
        before_text.splitlines(keepends=True), after_text.splitlines(keepends=True),
        fromfile="a/M29-M31/run_card_before.py", tofile="b/M29-M31/run_card.py", n=3))
    added_lines = sum(1 for ln in diff_lines if ln.startswith("+") and not ln.startswith("+++"))
    removed_lines = sum(1 for ln in diff_lines if ln.startswith("-") and not ln.startswith("---"))
    with open(DIFF, "w", encoding="utf-8", newline="") as handle:
        handle.write("".join(diff_lines))
    out.append("DIFF written %s  added_lines=%d removed_lines=%d hunks=%d"
               % (DIFF, added_lines, removed_lines,
                  sum(1 for ln in diff_lines if ln.startswith("@@"))))

    out.append("sha256 before %s" % hashlib.sha256(before_text.encode("utf-8")).hexdigest())
    out.append("sha256 after  %s" % hashlib.sha256(after_text.encode("utf-8")).hexdigest())

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
