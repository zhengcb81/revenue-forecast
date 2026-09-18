"""Mutation proofs for the owner-approved product fixes (2026-09-18 batch).

Each mutant reverts ONE fix in a TEMP COPY of the package (never in the repository), runs the
test that is supposed to catch it, and records whether the mutant was KILLED.  Discipline
carried over from the B10 rounds:

* the copy is built from `company_wiki/` + the named contract tests + `pytest.ini`;
* a mutant that fails to PARSE is reported as `invalid_mutant_syntax` and is NOT a kill;
* `killed_by` is the pytest exit code, not the presence of a traceback;
* an unmutated run of the same copy must PASS first, otherwise the copy itself is broken;
* the repository is checked afterwards (`git status --porcelain` + a line-ending-insensitive
  fingerprint of every file the harness could touch).

Usage::

    python barfix_mutations.py [--out PATH] [--only ID]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "barfix-mutations.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
PYTHON = Path(r"C:\Miniconda\python.exe")
PACKAGE = "src/company_wiki"

#: id -> (file, old, new, test file, description)
MUTANTS: dict[str, dict] = {
    "F-BAR-10": {
        "file": "src/company_wiki/source_catalog/scanner.py",
        "old": "        use_adapter = v2_scan_shadow or root.adapter_id is not None\n",
        "new": "        use_adapter = v2_scan_shadow\n",
        "test": "tests/contract/test_r4bar10_adapter_declared_root.py",
        "reverts": ("an adapter-declared root is scanned through its adapter regardless of the "
                    "activation snapshot"),
    },
    "F-BAR-11": {
        "file": "src/company_wiki/source_catalog/resolver.py",
        "old": "        if owning_root is None or owning_root.root_id not in reusable_root_ids:\n",
        "new": "        if False:  # mutant: the deny no longer binds the byte entry point\n",
        "test": "tests/contract/test_r4bar11_deny_binds_the_byte_entry.py",
        "reverts": ("the byte entry point refuses a root whose policy does not authorize reuse "
                    "(F-BAR-11)"),
    },
    "F-BAR-12": {
        "file": "src/company_wiki/source_catalog/resolver.py",
        "old": "        bundle_usable = bundle_valid_handle_count > 0\n",
        "new": "        bundle_usable = True  # mutant: usability no longer derived\n",
        "test": "tests/contract/test_r4bar12_bundle_usability.py",
        "reverts": ("the envelope derives `bundle_usable` from the bundle's own valid handles "
                    "(F-BAR-12)"),
    },
    "F-BAR-14": {
        "file": "src/company_wiki/source_catalog/adapters/sidecar.py",
        "old": ('    normalized: dict = {key: value for key, value in payload.items() '
                'if key != "_parse_error"}\n'),
        "new": "    normalized: dict = {}\n",
        "test": "tests/contract/test_r4bar14_adapter_metadata_contract.py",
        "reverts": ("declared sidecar keys pass through into the acquisition block "
                    "(F-BAR-14)"),
    },
    "FB10R2-scanner": {
        "file": "src/company_wiki/source_catalog/scanner.py",
        # FAITHFUL revert: the pre-fix expression parsed the column with `json.loads`, which
        # RAISES on a damaged value.  (A first attempt substituted `metadata_object`, which is
        # equally never-raising - an EQUIVALENT mutant that survived for the right reason.)
        "old": "        manifest_payload, manifest_state = metadata_state(existing[\"manifest_json\"])\n",
        "new": "        manifest_payload, manifest_state = json.loads(existing[\"manifest_json\"]), None\n",
        "test": "tests/contract/test_fb10r2_unguarded_column_parses.py",
        "reverts": ("the scan's size+mtime shortcut treats an UNREADABLE manifest as 'not a "
                    "reuse candidate' instead of letting the bare parse abort the scan "
                    "(F-B10R2 family, site 4)"),
    },
    "FB10R2-activation": {
        "file": "src/company_wiki/source_catalog/activation.py",
        # FAITHFUL revert: the pre-fix code had no except clause, so the parse error escaped.
        "old": ("    except (json.JSONDecodeError, TypeError, RecursionError, "
                "UnicodeDecodeError) as exc:\n"),
        "new": "    except ():\n",
        "test": "tests/contract/test_fb10r2_unguarded_column_parses.py",
        "reverts": ("an unreadable assertion list refuses the rollback BY NAME instead of "
                    "letting the parse error escape (F-B10R2 family, site 1)"),
    },
    "FB10R2-remediation": {
        "file": "src/company_wiki/source_catalog/remediation.py",
        "old": "    proposal_payload, proposal_state = metadata_state(row[\"proposal_json\"])\n",
        "new": ("    proposal_payload, proposal_state = metadata_object("
                "row[\"proposal_json\"]), None\n"),
        "test": "tests/contract/test_fb10r2_unguarded_column_parses.py",
        "reverts": ("an unreadable proposal refuses the approval BY NAME instead of a bare "
                    "JSONDecodeError (F-B10R2 family, site 3)"),
    },
    "FB10R2-assertion": {
        "file": "src/company_wiki/source_catalog/assertion_service.py",
        "old": '        evidence_json=_evidence_payload(existing["evidence_json"], assertion_id),\n',
        "new": '        evidence_json=json.loads(existing["evidence_json"]),\n',
        "test": "tests/contract/test_fb10r2_unguarded_column_parses.py",
        "reverts": ("unreadable evidence refuses by name instead of a bare JSONDecodeError "
                    "(F-B10R2 family, site 2)"),
    },
}


def _fingerprint_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(hashlib.sha256(text.encode("utf-8")).digest())
    return digest.hexdigest()


def _build_copy(work: Path, test_file: str) -> Path:
    shutil.rmtree(work, ignore_errors=True)
    (work / "src").mkdir(parents=True)
    shutil.copytree(WIKI / PACKAGE, work / PACKAGE, dirs_exist_ok=True)
    target = work / test_file
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(WIKI / test_file, target)
    shutil.copyfile(WIKI / "pytest.ini", work / "pytest.ini")
    return work


def _run_pytest(work: Path, test_file: str) -> dict:
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", test_file, "-q", "--tb=line", "-p", "no:cacheprovider"],
        cwd=str(work), capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"PYTHONPATH": "src", "PYTHONIOENCODING": "utf-8",
             "PATH": __import__("os").environ.get("PATH", ""),
             "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""),
             "PYTHONDONTWRITEBYTECODE": "1"},
    )
    out = f"{proc.stdout or ''}{proc.stderr or ''}"
    syntax_error = "SyntaxError" in out or "IndentationError" in out
    return {"exit_code": proc.returncode, "passed": proc.returncode == 0,
            "invalid_mutant_syntax": syntax_error,
            "tail": out.strip().splitlines()[-4:]}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--only", help="run a single mutant id")
    args = parser.parse_args(argv)

    repo_before = _fingerprint_tree(WIKI / "src")
    status_before = subprocess.run(["git", "-C", str(WIKI), "status", "--porcelain"],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace").stdout

    work_root = Path(tempfile.gettempdir()) / "barfix-mutations"
    record: dict = {
        "artifact": "barfix-mutations",
        "purpose": ("prove each fix is load-bearing: reverting it in a TEMP COPY must fail the "
                    "test that claims to cover it"),
        "mutants": [],
        "repository_untouched": None,
    }
    selected = {k: v for k, v in MUTANTS.items() if args.only in (None, k)}
    if not selected:
        raise SystemExit(f"no mutant matches {args.only!r}; known: {sorted(MUTANTS)}")

    for mutant_id, spec in selected.items():
        print(f"=== {mutant_id} ===")
        work = _build_copy(work_root / mutant_id.replace("/", "_"), spec["test"])
        baseline = _run_pytest(work, spec["test"])
        entry = {"id": mutant_id, "reverts": spec["reverts"], "file": spec["file"],
                 "test": spec["test"], "baseline": baseline}
        if not baseline["passed"]:
            entry["killed"] = False
            entry["note"] = "copy baseline FAILED - the copied tree is broken, not the mutant"
            record["mutants"].append(entry)
            print(f"  baseline broken: {baseline['tail']}")
            continue

        path = work / spec["file"]
        text = path.read_text(encoding="utf-8")
        if spec["old"] not in text:
            entry["killed"] = False
            entry["note"] = "mutation anchor not found (the fix moved?)"
            record["mutants"].append(entry)
            print("  ANCHOR MISSING")
            continue
        path.write_text(text.replace(spec["old"], spec["new"], 1), encoding="utf-8", newline="")
        mutated = _run_pytest(work, spec["test"])
        entry["mutated"] = mutated
        entry["killed"] = (not mutated["passed"]) and not mutated["invalid_mutant_syntax"]
        entry["killed_by"] = ("pytest assertion" if entry["killed"] else
                              "invalid_mutant_syntax" if mutated["invalid_mutant_syntax"]
                              else "SURVIVED")
        record["mutants"].append(entry)
        print(f"  killed={entry['killed']} by={entry['killed_by']} tail={mutated['tail'][-1:]}")

    shutil.rmtree(work_root, ignore_errors=True)
    repo_after = _fingerprint_tree(WIKI / "src")
    status_after = subprocess.run(["git", "-C", str(WIKI), "status", "--porcelain"],
                                  capture_output=True, text=True, encoding="utf-8",
                                  errors="replace").stdout
    record["repository_untouched"] = {
        "src_fingerprint_identical": repo_before == repo_after,
        # `git status` legitimately changes when this batch's own edits are still uncommitted,
        # so the comparison is pre/post THIS harness run, not "clean".
        "git_status_identical": status_before == status_after,
    }
    record["ran_at_utc"] = datetime.now(UTC).isoformat()
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["repository_untouched"], indent=2))
    killed = sum(1 for entry in record["mutants"] if entry.get("killed"))
    print(f"mutants killed: {killed}/{len(record['mutants'])}")
    return 0 if killed == len(record["mutants"]) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(2)
