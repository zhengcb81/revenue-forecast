"""FC-1307-a mutation check: are the guard's own regression tests load-bearing?

The B-run discipline (F-B01-9 closure) is that a new test must be shown to KILL a
mutation of the thing it claims to protect - otherwise it is decoration.  This
harness mutates ``company-wiki/scripts/host_assumption_guard.py`` three ways and
requires the matching FC-1307-a case to fail each time:

  A. the emitting mode also writes the baseline  -> the "never writes" case must fail
     (this is the defect that made the gate itself fail CI on run 34751519232)
  B. the baseline key drops the offending value  -> the "value-level ratchet" case
     must fail (a file-keyed ratchet is a rubber stamp)
  C. rule A's scope widens from tests/ to everything -> the "product code may branch
     on the host" case must fail

Each mutant names the case (a pytest -k EXPRESSION, so one mutant may be pinned by
several cases) that must fail.  A mutant of the *author's own* harness counts too: the
first version of mutant E only broke the exemption path and "survived", which said
nothing about the test - the mutant, not the test, was wrong.

Read-only w.r.t. the product: it edits one script, runs one test file, then restores
the file from git and asserts the tree is clean.  Usage:

    python fc1307a_mutations.py [path-to-company-wiki]

Prints one line per mutant and a JSON summary on the last line.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULT_WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
GUARD = "scripts/host_assumption_guard.py"
TEST_FILE = "tests/contract/test_fc1307_host_assumption_gate.py"

MUTANTS: list[tuple[str, str, str, str]] = [
    (
        "A: emitting mode also writes the baseline",
        "            indent=2,\n        ))\n        return 0\n",
        "            indent=2,\n        ))\n"
        "        BASELINE.write_text(json.dumps(recorded), encoding=\"utf-8\")\n"
        "        return 0\n",
        "test_fc1307a_emit_baseline_only_prints_and_never_writes",
    ),
    (
        "B: baseline key drops the offending value (file-level ratchet)",
        '        return f"{item[\'rule\']}|{rel}|{item[\'value\']}"',
        '        return f"{item[\'rule\']}|{rel}"',
        "test_fc1307a_the_ratchet_is_value_level_not_file_level",
    ),
    (
        "C: rule 1 scope widens to every file",
        '    in_tests = "tests" in path.parts',
        "    in_tests = True",
        "test_fc1307a_product_code_may_branch_on_the_host",
    ),
    (
        "D: ratchet identity goes back to the 40-character prefix (B-VR1307-03)",
        "        return f\"{item['rule']}|{rel}|{item['value']}\"",
        "        return f\"{item['rule']}|{rel}|{item['value'][:40]}\"",
        "test_fc1307a_a_shared_prefix_does_not_inherit_a_baseline_entry",
    ),
    (
        "E: any skip marker ANYWHERE in the module exempts the file (B-VR1307-02)",
        "def _module_level_skip(tree: ast.AST) -> bool:",
        "def _module_level_skip(tree: ast.AST) -> bool:\n"
        "    return \"skip\" in ast.dump(tree)  # mutant: the old file-wide behaviour",
        "test_fc1307a_an_unrelated_skip_marker_does_not_exempt"
        " or test_fc1307a_a_guarded_capability_use_is_clean",
    ),
    (
        "F: HEX64 loses re.IGNORECASE (B-VR1307-05)",
        'HEX64 = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)',
        'HEX64 = re.compile(r"^[0-9a-f]{64}$")',
        "test_fc1307a_an_uppercase_digest_is_flagged_too",
    ),
    (
        "G: POSIX roots go back to the original 12-entry list (B-VR1307-04)",
        '    r"|//[^/\\s]+/"\n    r")"\n)',
        '    r")"\n)',
        "test_fc1307a_widened_posix_roots_are_flagged",
    ),
]


def _run(wiki: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *args] if args[0] != "git" else args,
        cwd=str(wiki), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=900,
    )


def _git(wiki: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(wiki), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300,
    )


def _restore(wiki: Path, guard_path: Path, original: str) -> None:
    """Put the file back byte-for-byte.  A plain write_text() is not enough on
    Windows: the read used universal newlines, so re-writing can flip the working
    copy's line endings and leave git reporting a phantom modification.  Ask git
    for the committed bytes instead, and fall back to the captured text."""
    _git(wiki, "checkout", "--", GUARD)
    if guard_path.read_text(encoding="utf-8") != original:
        guard_path.write_text(original, encoding="utf-8", newline="")


def main(argv: list[str]) -> int:
    wiki = Path(argv[1]) if len(argv) > 1 else DEFAULT_WIKI
    guard_path = wiki / GUARD
    if not guard_path.is_file():
        raise SystemExit(f"not found: {guard_path}")

    dirty = _git(wiki, "status", "--porcelain", "--", GUARD).stdout.strip()
    if dirty:
        raise SystemExit(f"refusing to mutate a dirty file: {dirty}")
    original = guard_path.read_text(encoding="utf-8")

    base = _run(wiki, [TEST_FILE])
    baseline_ok = base.returncode == 0
    print(f"baseline (unmutated): exit={base.returncode} {base.stdout.strip().splitlines()[-1]}")
    if not baseline_ok:
        print(json.dumps({"baseline_green": False, "mutants": []}, ensure_ascii=False))
        return 1

    results: list[dict[str, object]] = []
    try:
        for label, old, new, case in MUTANTS:
            if old not in original:
                results.append({"mutant": label, "case": case, "applied": False,
                                "killed": False,
                                "error": "pattern not found - harness is stale"})
                print(f"SKIP  {label}: pattern not found (harness is stale)")
                continue
            guard_path.write_text(
                original.replace(old, new, 1), encoding="utf-8", newline=""
            )
            proc = _run(wiki, ["-k", case, TEST_FILE])
            killed = proc.returncode != 0
            _restore(wiki, guard_path, original)
            results.append({"mutant": label, "case": case, "applied": True,
                            "killed": killed, "exit": proc.returncode})
            print(f"{'KILLED' if killed else 'SURVIVED'}  {label}  -> {case} exit={proc.returncode}")
    finally:
        _restore(wiki, guard_path, original)

    restored = _git(wiki, "status", "--porcelain", "--", GUARD).stdout.strip()
    summary = {
        "wiki": str(wiki),
        "baseline_green": baseline_ok,
        "mutants": results,
        "all_killed": all(bool(r.get("killed")) for r in results) and len(results) == len(MUTANTS),
        "tree_restored": restored == "",
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["all_killed"] and summary["tree_restored"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
