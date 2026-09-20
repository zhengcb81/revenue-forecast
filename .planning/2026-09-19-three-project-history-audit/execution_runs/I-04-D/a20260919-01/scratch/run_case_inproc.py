"""Run the scheduler's case functions in-process so the harness can be inspected."""

from __future__ import annotations

from pathlib import Path
import sys

ATTEMPT = Path(__file__).resolve().parents[1]
SCRIPTS = ATTEMPT / "iso" / "filing-fetch" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import i04d_schedule as sched  # noqa: E402

print("scheduler file:", sched.__file__)
out = ATTEMPT / "scratch" / "inproc"
import shutil

if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)

for name in ("I04D-CASE-F-L8d", "I04D-CASE-F-L9c"):
    run = sched.CaseRun(name, out)
    print(f"=== {name} ===")
    print("  dir       :", run.dir)
    print("  root      :", run.root)
    print("  refcount  :", run.refcount)
    try:
        sched.CASES[name](run)
        print("  case completed")
    except Exception as exc:  # noqa: BLE001
        print(f"  case raised {type(exc).__name__}: {exc}")
    print("  dir contents:", sorted(p.name for p in run.dir.iterdir()))
    catalog = run.root / ".source_catalog"
    print("  catalog:", sorted(p.name for p in catalog.iterdir()) if catalog.is_dir() else "ABSENT")
    print("  worker journal lines:", (run.worker_journal.read_text(encoding='utf-8').count('\n')) if run.worker_journal.exists() else 0)
    for tag, meta in run.meta.items():
        if isinstance(meta, dict) and "exit_code" in meta:
            print(f"  [{tag}] exit={meta['exit_code']} pid={meta.get('pid')}")
    report_path = run.dir / "report.A.json"
    print("  report A exists:", report_path.exists())
    probe = run.dir / "hook-probe.log"
    if probe.exists():
        print("  hook probe:")
        print("   ", probe.read_text(encoding="utf-8").replace("\n", "\n    ")[:1500])
    diag = run.dir / "harness-diagnostic.json"
    if diag.exists():
        print("  harness diagnostic:", diag.read_text(encoding="utf-8")[:800])
