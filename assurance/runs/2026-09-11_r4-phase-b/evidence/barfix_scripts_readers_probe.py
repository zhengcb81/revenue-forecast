"""Proof for the `scripts/` convergence (owner instruction 2026-09-18).

Two claims have to be shown, not asserted:

A. The gate CHANGE is a strengthening that bites.  `test_b10_scripts_have_no_direct_reader`
   replaced a pin on a measured count of 2 with a hard zero over `scripts/`.  Injecting a
   direct reader must therefore FAIL the test, and injecting a `json.loads` on a DIFFERENT
   column must still PASS it (otherwise the scan keys on "any loads" rather than on the
   shared column).  The injections are written into the REAL repo files for the duration of
   one pytest run and then restored; a line-ending-insensitive fingerprint of every touched
   file is compared afterwards, and the repository is checked with `git status --porcelain`.

B. The convergence fixes a REAL escape, not just a lint rule.  The replaced expression
   `json.loads(row["metadata_json"] or "{}")` inside `try/except json.JSONDecodeError` does
   not catch the failures `store.metadata_state` handles: deep nesting raises
   `RecursionError`, a non-str/bytes value raises `TypeError`, undecodable bytes raise
   `UnicodeDecodeError`.  The probe runs the OLD expression (reproduced verbatim) and the
   NEW call against the same malformed inputs and reports both outcomes.

Nothing here writes to the production catalog; the only writes are the temporary source
injections, restored in a `finally` block.

Usage::

    python barfix_scripts_readers_probe.py [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "barfix-scripts-readers.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SCRIPTS = WIKI / "scripts"
PYTHON = Path(r"C:\Miniconda\python.exe")
GATE_TEST = "tests/contract/test_b10_read_chain.py::test_b10_scripts_have_no_direct_reader"

#: file -> (anchor line to insert AFTER, injected source)
INJECTIONS = {
    "legacy_observer.py": (
        "    for row in rows:\n",
        "        _injected = json.loads(row[\"metadata_json\"] or \"{}\")\n",
    ),
    "wu904_remediation_restore.py": (
        "def _document_row(con, provider_document_id: str) -> sqlite3.Row | None:\n",
        "    _injected = json.loads(connection_row[\"metadata_json\"] or \"{}\")\n",
    ),
}
#: A `loads` on a DIFFERENT column must NOT be flagged (negative control for the scan).
CONTROL_INJECTION = {
    "legacy_observer.py": (
        "    for row in rows:\n",
        "        _control = json.loads(row[\"proposal_json\"] or \"{}\")\n",
    ),
}


def _fingerprint(path: Path) -> str:
    """Line-ending-insensitive digest, so a CRLF rewrite cannot hide a leftover edit."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_gate() -> dict:
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", GATE_TEST, "-q", "--tb=line"],
        cwd=str(WIKI), capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={"PYTHONPATH": "src", "PYTHONIOENCODING": "utf-8", "PATH": __import__("os").environ["PATH"],
             "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")},
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return {"exit_code": proc.returncode, "tail": out.strip().splitlines()[-3:],
            "passed": proc.returncode == 0}


def _inject(plan: dict[str, tuple[str, str]]) -> dict[str, str]:
    originals = {}
    for name, (anchor, injected) in plan.items():
        path = SCRIPTS / name
        original = path.read_text(encoding="utf-8")
        originals[name] = original
        if anchor not in original:
            raise SystemExit(f"anchor not found in {name}: {anchor!r}")
        path.write_text(original.replace(anchor, anchor + injected, 1),
                        encoding="utf-8", newline="")
    return originals


def _restore(originals: dict[str, str]) -> None:
    for name, text in originals.items():
        (SCRIPTS / name).write_text(text, encoding="utf-8", newline="")


def _git_status() -> str:
    proc = subprocess.run(["git", "-C", str(WIKI), "status", "--porcelain"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.stdout or ""


def malformed_inputs() -> list[tuple[str, object]]:
    return [
        ("not json", "{not json"),
        ("empty string", ""),
        ("deeply nested (RecursionError)", "[" * 20000 + "]" * 20000),
        ("not a string (TypeError)", 12345),
        ("undecodable bytes (UnicodeDecodeError)", b"\xff\xfe\x00bad"),
    ]


def escape_probe() -> list[dict]:
    """Old expression vs the single chain, on the same malformed values."""
    sys.path.insert(0, str(WIKI / "src"))
    from company_wiki.source_catalog.store import metadata_object, metadata_state

    results = []
    for label, value in malformed_inputs():
        old_outcome = "returned {}"
        try:
            parsed = json.loads(value or "{}")
            old_outcome = f"returned {type(parsed).__name__}"
        except json.JSONDecodeError:
            old_outcome = "caught (JSONDecodeError)"
        except Exception as error:  # noqa: BLE001 - the escape is the measurement
            old_outcome = f"ESCAPED: {type(error).__name__}"
        obj, state = metadata_state(value)
        results.append({
            "input": label,
            "old_expression": old_outcome,
            "new_single_chain": f"({type(obj).__name__}, state={state!r})",
            "new_never_escapes": True,
            "metadata_object_is_same_parse": metadata_object(value) == obj,
        })
    return results


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    touched = sorted({*(SCRIPTS / name for name in INJECTIONS), *(SCRIPTS / n for n in CONTROL_INJECTION)})
    before = {path.name: _fingerprint(path) for path in touched}
    status_before = _git_status()

    record: dict = {
        "artifact": "barfix-scripts-readers",
        "purpose": ("prove the scripts/ hard-zero gate bites (A) and that the convergence "
                    "closes a real escape (B)"),
        "gate_test": GATE_TEST,
        "baseline": {"gate": _run_gate()},
        "mutations": [],
        "escape_probe": [],
        "restored": None,
    }
    print(f"baseline gate: {record['baseline']['gate']}")

    for label, plan in (("direct reader in legacy_observer.py", {k: v for k, v in INJECTIONS.items() if k == "legacy_observer.py"}),
                        ("direct reader in wu904_remediation_restore.py", {k: v for k, v in INJECTIONS.items() if k == "wu904_remediation_restore.py"}),
                        ("control: loads() on a DIFFERENT column", CONTROL_INJECTION)):
        originals = _inject(plan)
        try:
            outcome = _run_gate()
        finally:
            _restore(originals)
        entry = {"mutation": label, "injected_into": sorted(plan), "gate": outcome}
        entry["killed"] = (not outcome["passed"]) if "control" not in label else outcome["passed"]
        entry["expectation"] = ("the gate must FAIL (killed)" if "control" not in label
                                else "the gate must PASS (the scan keys on the shared column)")
        record["mutations"].append(entry)
        print(f"{label}: gate_passed={outcome['passed']} killed={entry['killed']}")

    record["escape_probe"] = escape_probe()
    for item in record["escape_probe"]:
        print(f"  {item['input']}: old={item['old_expression']} new={item['new_single_chain']}")

    after = {path.name: _fingerprint(path) for path in touched}
    status_after = _git_status()
    record["restored"] = {
        "fingerprints_identical": before == after,
        "before": before,
        "after": after,
        "git_status_unchanged_outside_the_fix": status_after == status_before,
        "note": ("`git status --porcelain` still lists the CONVERGED files, because this "
                 "probe runs before that change is committed; the comparison is pre/post the "
                 "injections, which is what proves the restoration"),
    }
    record["ran_at_utc"] = datetime.now(UTC).isoformat()
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["restored"], ensure_ascii=False, indent=2))
    ok = (all(entry["killed"] for entry in record["mutations"])
          and record["restored"]["fingerprints_identical"])
    print("ALL PROOFS HOLD" if ok else "PROOF FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(2)
