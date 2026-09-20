"""Add a bounded, self-contained diagnostic to the two problem cases.

The diagnostic writes into the case directory itself (so the durable run record keeps
it) and is removed again once the cases are green.
"""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

OLD = '''    assert run.wait_reached("enter-complete", "A"), "A never finished its enter"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    payload["owner"] = THIRD_PARTY_OWNER'''

NEW = '''    assert run.wait_reached("enter-complete", "A"), "A never finished its enter"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        detail = {
            "root": str(run.root),
            "catalog": str(run.catalog),
            "catalog_is_dir": run.catalog.is_dir(),
            "catalog_listing": sorted(x.name for x in run.catalog.iterdir()),
            "refcount_path": str(run.refcount),
            "refcount_exists": run.refcount.exists(),
            "refcount_text": run.refcount.read_text(encoding="utf-8")
            if run.refcount.is_file()
            else None,
            "gate_files": sorted(x.name for x in run.dir.glob("gate.*")),
            "arrive_files": sorted(x.name for x in run.dir.glob("arrive.*")),
            "worker_state": _read_json(run.state),
        }
        (run.dir / "harness-diagnostic.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        raise AssertionError(f"refcount is not an object: {payload!r}; detail={detail!r}")
    payload["owner"] = THIRD_PARTY_OWNER'''

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("L8D PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''    assert run.wait_reached("enter-complete", "A"), "A never finished its enter"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    run.meta["live_ledger"] = {'''
NEW2 = '''    assert run.wait_reached("enter-complete", "A"), "A never finished its enter"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        detail = {
            "catalog_is_dir": run.catalog.is_dir(),
            "catalog_listing": sorted(x.name for x in run.catalog.iterdir()),
            "refcount_exists": run.refcount.exists(),
            "gate_files": sorted(x.name for x in run.dir.glob("gate.*")),
            "arrive_files": sorted(x.name for x in run.dir.glob("arrive.*")),
        }
        (run.dir / "harness-diagnostic.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        raise AssertionError(f"refcount is not an object: {payload!r}; detail={detail!r}")
    run.meta["live_ledger"] = {'''
if OLD2 not in text:
    print("L9C PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATH.write_text(text, encoding="utf-8")
print("case diagnostics installed")
