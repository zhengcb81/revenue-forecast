"""Make the F-L8d / F-L9c cases dump the case directory the instant the gate fires."""

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
        detail = {
            "root": str(run.root),'''

NEW = '''    reached = run.wait_reached("enter-complete", "A")
    instant = {
        "reached_returned": reached,
        "gate_path": str(run.reached("enter-complete", "A")),
        "gate_exists": run.reached("enter-complete", "A").exists(),
        "gate_bytes": run.reached("enter-complete", "A").stat().st_size
        if run.reached("enter-complete", "A").exists()
        else None,
        "gate_mtime": run.reached("enter-complete", "A").stat().st_mtime
        if run.reached("enter-complete", "A").exists()
        else None,
        "case_dir_listing": sorted(x.name for x in run.dir.iterdir()),
        "catalog_listing": sorted(x.name for x in run.catalog.iterdir())
        if run.catalog.is_dir()
        else "ABSENT",
        "worker_journal_bytes": run.worker_journal.stat().st_size
        if run.worker_journal.exists()
        else None,
        "pid_alive": run.procs["A"].poll() if "A" in run.procs else "no-proc",
    }
    (run.dir / "gate-instant.json").write_text(
        json.dumps(instant, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    assert reached, f"A never finished its enter; instant={instant!r}"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        detail = {
            "instant": instant,
            "root": str(run.root),'''

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("L8D PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''    assert run.wait_reached("enter-complete", "A"), "A never finished its enter"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        detail = {
            "catalog_is_dir": run.catalog.is_dir(),'''

NEW2 = '''    reached = run.wait_reached("enter-complete", "A")
    instant = {
        "reached_returned": reached,
        "gate_exists": run.reached("enter-complete", "A").exists(),
        "case_dir_listing": sorted(x.name for x in run.dir.iterdir()),
        "catalog_listing": sorted(x.name for x in run.catalog.iterdir())
        if run.catalog.is_dir()
        else "ABSENT",
        "worker_journal_bytes": run.worker_journal.stat().st_size
        if run.worker_journal.exists()
        else None,
        "pid_alive": run.procs["A"].poll() if "A" in run.procs else "no-proc",
    }
    (run.dir / "gate-instant.json").write_text(
        json.dumps(instant, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    assert reached, f"A never finished its enter; instant={instant!r}"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        detail = {
            "instant": instant,
            "catalog_is_dir": run.catalog.is_dir(),'''

if OLD2 not in text:
    print("L9C PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATH.write_text(text, encoding="utf-8")
print("instant dump installed")
