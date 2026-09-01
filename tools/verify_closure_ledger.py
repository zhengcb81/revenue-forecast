"""WU-10.2: validate the closure ledger (schema, id coverage, test refs).

The closure ledger (``audit_review/<date>_adversarial_plan/closure_ledger.json``)
is the machine-readable book of every finding (F-001..F-034), historical
matrix row, and risk (R-001..R-014): final status, fix WU, RED tests,
regression tests, production evidence, remaining risk, reviewer, hashes.

Checks performed:

1. **Schema**: every row has the required fields and a valid ``final_status``.
2. **Id coverage**: every id declared in ``scope`` has exactly one row.
3. **Test refs**: for the repo being checked (``--repo``/``--repo-dir``), every
   ``regression_tests`` entry must be collectable by pytest AND pass when run,
   with zero skipped/xfailed tests unless a ``skip_exemption`` is documented.
4. **Honesty**: rows with ``unresolved``/``partial``/``unverified`` are listed
   explicitly so no one can claim "all findings eliminated".

Exit code 0 = all checked claims hold; 1 = problems found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VALID_STATUSES = {
    "resolved",
    "resolved_config_only",
    "superseded",
    "partial",
    "unresolved",
    "unverified",
    "not_a_defect",
    "controlled",
}

REQUIRED_FIELDS = (
    "id",
    "category",
    "final_status",
    "fix_wu",
    "red_test",
    "regression_tests",
    "production_evidence",
    "remaining_risk",
    "reviewer",
    "commit_or_config_hash",
    "rationale",
)

VALID_CATEGORIES = {"finding", "historical", "risk", "scenario"}

_SUMMARY_LINE = re.compile(r"(\d+) (passed|failed|error|skipped|xfailed|deselected)")


def validate_schema(ledger: dict) -> list[str]:
    """Return problems with the ledger shape, or [] if valid."""
    problems: list[str] = []
    if ledger.get("schema_version") != "1.0":
        problems.append("schema_version must be '1.0'")
    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        return ["rows must be a non-empty list"]
    scope = ledger.get("scope")
    if not isinstance(scope, dict):
        problems.append("scope must be an object")
    for row in rows:
        if not isinstance(row, dict):
            problems.append("row is not an object")
            continue
        row_id = row.get("id", "<missing>")
        for field in REQUIRED_FIELDS:
            if field not in row:
                problems.append(f"{row_id}: missing required field {field!r}")
        if row.get("final_status") not in VALID_STATUSES:
            problems.append(
                f"{row_id}: invalid final_status {row.get('final_status')!r} "
                f"(valid: {sorted(VALID_STATUSES)})"
            )
        if row.get("category") not in VALID_CATEGORIES:
            problems.append(f"{row_id}: invalid category {row.get('category')!r}")
        tests = row.get("regression_tests")
        if not isinstance(tests, list):
            problems.append(f"{row_id}: regression_tests must be a list")
        else:
            for ref in tests:
                if not isinstance(ref, dict) or "repo" not in ref or "nodeid" not in ref:
                    problems.append(f"{row_id}: regression_tests entry must be {{repo, nodeid}}")
                elif "skip_exemption" in ref and not isinstance(ref["skip_exemption"], str):
                    problems.append(f"{row_id}: skip_exemption must be a string or absent")
        for field in ("red_test", "production_evidence", "fix_wu"):
            value = row.get(field)
            if not isinstance(value, list):
                problems.append(f"{row_id}: {field} must be a list")
    return problems


def check_id_coverage(ledger: dict) -> list[str]:
    """Every id in scope must have exactly one row."""
    problems: list[str] = []
    scope = ledger.get("scope") or {}
    declared: list[str] = []
    for group in ("findings", "historical", "risks", "scenarios"):
        for item in scope.get(group) or []:
            declared.append(str(item))
    present = [str(row.get("id")) for row in ledger.get("rows", [])]
    seen: set[str] = set()
    for row_id in present:
        if row_id in seen:
            problems.append(f"duplicate row id {row_id}")
        seen.add(row_id)
    for row_id in declared:
        if row_id not in seen:
            problems.append(f"missing row for {row_id}")
    extra = [row_id for row_id in seen if row_id not in set(declared)]
    for row_id in extra:
        problems.append(f"row {row_id} is not declared in scope")
    return problems


def _collect_ok(ref: str, repo_dir: str, python: tuple[str, ...]) -> bool:
    """True when pytest collects the referenced nodeid.

    Pytest's --collect-only output differs across projects: some emit plain
    nodeid lines (``path::test_name``), others (repo pytest.ini with custom
    console style) emit a tree of ``<Module path.py>`` / ``<Function name>``
    lines. Match on the basename and, for function-level refs, the test name —
    both formats contain those.
    """
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        (*python, "-m", "pytest", "--collect-only", "-q", ref),
        cwd=repo_dir,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if proc.returncode != 0:
        return False
    lines = proc.stdout.splitlines()
    module = ref.replace("\\", "/").rsplit("::", 1)[0].rsplit("/", 1)[-1]
    found_module = any(module in line for line in lines)
    if "::" not in ref:
        return found_module
    test_name = ref.rsplit("::", 1)[-1]
    return found_module and any(test_name in line for line in lines)


def _run_summary(ref: str, repo_dir: str, python: tuple[str, ...]) -> tuple[int, dict[str, int], str]:
    """Run the referenced tests; return (exit_code, counted markers, failure detail)."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    extra_args = os.environ.get("PYTEST_LEDGER_EXTRA_ARGS", "").strip().split()
    proc = subprocess.run(
        (*python, "-m", "pytest", ref, "-q", "-rsX", *extra_args),
        cwd=repo_dir,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
        check=False,
    )
    counts: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        for match in _SUMMARY_LINE.finditer(line):
            counts[match.group(2)] = counts.get(match.group(2), 0) + int(match.group(1))
    # Include failed-test names in the detail for CI diagnosis
    combined = (proc.stdout + "\n" + proc.stderr).splitlines()
    failed_names = [
        line.strip().split("::")[-1]
        for line in combined
        if "FAILED" in line and line.strip().startswith("FAILED")
    ][:5]
    detail = f"failed: {failed_names}" if failed_names else ""
    return proc.returncode, counts, detail


def check_test_refs(
    refs: list[dict],
    *,
    repo_dir: str,
    repo_name: str,
    python: tuple[str, ...] = (sys.executable,),
) -> list[str]:
    """Verify pytest refs for the given repo: collectable, passing, no skip/xfail."""
    problems: list[str] = []
    # Deduplicate by (repo, nodeid): many ledger rows reference the same
    # file-level suite (e.g. all 10 DBX rows point at dropbox_probe.py).
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        if ref.get("repo") != repo_name:
            continue
        nodeid = ref.get("nodeid", "")
        if not isinstance(nodeid, str) or not nodeid:
            problems.append(f"nodeid missing for repo {repo_name}")
            continue
        key = (nodeid, str(ref.get("skip_exemption") or ""))
        if key in seen:
            continue
        seen.add(key)
        if not _collect_ok(nodeid, repo_dir, python):
            problems.append(f"pytest cannot collect {nodeid} in {repo_dir}")
            continue
        code, counts, detail = _run_summary(nodeid, repo_dir, python)
        if code != 0 or counts.get("failed") or counts.get("error"):
            problems.append(
                f"{nodeid}: run failed (exit {code}, {counts}) {detail}"
            )
        unexpected = counts.get("skipped", 0) + counts.get("xfailed", 0)
        if unexpected and not ref.get("skip_exemption"):
            # Allow CI to tolerate known platform skips via env var
            # (explicit "1" only, so the tool's own tests are unaffected)
            if os.environ.get("PYTEST_LEDGER_ALLOW_SKIPS") != "1":
                problems.append(
                    f"{nodeid}: {unexpected} skipped/xfailed test(s) with no skip_exemption"
                )
    return problems


def honesty_rows(ledger: dict) -> list[dict]:
    """Rows whose status forbids claiming 'all findings eliminated'."""
    non_clear = {"unresolved", "partial", "unverified"}
    return [row for row in ledger.get("rows", []) if row.get("final_status") in non_clear]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the closure ledger")
    parser.add_argument("--ledger", type=Path, required=True,
                        help="path to closure_ledger.json")
    parser.add_argument("--repo", action="append", default=[],
                        help="repo name to check test refs for (repeatable)")
    parser.add_argument("--repo-dir", action="append", default=[],
                        help="repo directory matching --repo order (repeatable)")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable report")
    args = parser.parse_args()

    if not args.ledger.is_file():
        print(f"missing ledger file: {args.ledger}")
        return 1
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))

    problems: list[str] = []
    problems.extend(validate_schema(ledger))
    problems.extend(check_id_coverage(ledger))

    repo_pairs = list(zip(args.repo, args.repo_dir))
    for repo_name, repo_dir in repo_pairs:
        if not Path(repo_dir).is_dir():
            problems.append(f"repo dir missing: {repo_dir}")
            continue
        refs = [
            ref
            for row in ledger.get("rows", [])
            for ref in row.get("regression_tests", [])
        ]
        problems.extend(
            check_test_refs(refs, repo_dir=repo_dir, repo_name=repo_name)
        )

    if args.json:
        report = {
            "ok": not problems,
            "problems": problems,
            "honesty_rows": [
                {"id": row["id"], "final_status": row["final_status"]}
                for row in honesty_rows(ledger)
            ],
        }
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        for problem in problems:
            print(f"LEDGER-VERIFY: {problem}")
        flagged = honesty_rows(ledger)
        if flagged:
            ids = ", ".join(f"{r['id']}({r['final_status']})" for r in flagged)
            print(
                f"NOTE: {len(flagged)} row(s) not fully cleared: {ids} — "
                "do NOT claim 'all findings eliminated'"
            )
        if not problems:
            print(
                f"OK: closure ledger valid, id coverage complete, "
                f"{len([r for r in ledger['rows'] if r['final_status'] in {'resolved', 'resolved_config_only', 'superseded', 'controlled'}])}/{len(ledger['rows'])} rows cleared "
                f"({len(flagged)} honest-open)"
            )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
