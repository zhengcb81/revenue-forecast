"""I-04-B review fixes, round 2: the four author-side fixture bugs in the new cases.

All four are fixture mistakes found by running them, not product defects:
  1. `_wiki_root` in the new class took one argument while the base helper takes two
  2. F-B4 still called `_register(joined=False, timeout=...)` after the signature changed
  3. F-B4d's fake worker-status answered runtime_state=stopped, so the pause path never ran
  4. F-B4e pruned an EMPTY refcount, so no probe could happen (both sub-cases)
"""
from __future__ import annotations

import pathlib

ATTEMPT = pathlib.Path(__file__).resolve().parents[1]
TESTS = ATTEMPT / "iso" / "filing-fetch" / "tests" / "test_fetch_filing.py"

FIXES = [
    (
        "helper-arity",
        '    @staticmethod\n'
        '    def _wiki_root(parent: Path) -> Path:\n'
        '        root = parent / "company-wiki"\n',
        '    @staticmethod\n'
        '    def _wiki_root(parent: Path, name: str = "company-wiki") -> Path:\n'
        '        root = parent / name\n',
    ),
    (
        "f-b4-register-signature",
        '            scope._register(joined=False, timeout=scope._request_remaining())\n',
        '            scope._register(joined=False)\n',
    ),
    (
        "f-b4d-worker-status-running",
        '            def fake_run(args, **kwargs):\n'
        '                command = args[0] if args else ""\n'
        '                grants.append((command, kwargs.get("timeout")))\n'
        '                if command == "tasklist":\n'
        '                    return subprocess.CompletedProcess(\n'
        '                        args=args, returncode=0, stdout=f"python.exe {os.getpid()}", stderr=""\n'
        '                    )\n'
        '                payload = {"desired_state": "paused", "runtime_state": "stopped"}\n'
        '                if "worker-resume" in args:\n'
        '                    payload = {"desired_state": "enabled", "runtime_state": "running"}\n',
        '            def fake_run(args, **kwargs):\n'
        '                command = args[0] if args else ""\n'
        '                grants.append((command, kwargs.get("timeout")))\n'
        '                if command == "tasklist":\n'
        '                    return subprocess.CompletedProcess(\n'
        '                        args=args, returncode=0, stdout=f"python.exe {os.getpid()}", stderr=""\n'
        '                    )\n'
        '                # the pause path only runs when the worker is RUNNING first\n'
        '                payload = {"desired_state": "paused", "runtime_state": "stopped"}\n'
        '                if "worker-status" in args:\n'
        '                    payload = {"desired_state": "enabled", "runtime_state": "running"}\n'
        '                elif "worker-resume" in args:\n'
        '                    payload = {"desired_state": "enabled", "runtime_state": "running"}\n',
    ),
    (
        "f-b4e-seed-refcount",
        '        def run_case(clock_values: list[float]) -> tuple[list[float], str]:\n'
        '            grants: list[float] = []\n'
        '            clock = list(clock_values)\n',
        '        def run_case(clock_values: list[float]) -> tuple[list[float], str]:\n'
        '            grants: list[float] = []\n'
        '            clock = list(clock_values)\n',
    ),
    (
        "f-b4e-import-refcount-name",
        '        from fetch_filing import PausedWorkerScope, _normalize_stats\n\n'
        '        def run_case',
        '        from fetch_filing import (\n'
        '            _PAUSE_REFCOUNT_NAME,\n'
        '            PausedWorkerScope,\n'
        '            _normalize_stats,\n'
        '        )\n\n'
        '        def run_case',
    ),
    (
        "f-b4e-write-entry",
        '            with TemporaryDirectory() as temporary:\n'
        '                root = self._wiki_root(Path(temporary))\n'
        '                scope = PausedWorkerScope(\n'
        '                    root=root, command_prefix=["stub"], enabled=True,\n'
        '                    graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                    deadline=1.0, stats=_normalize_stats({}),\n'
        '                )\n',
        '            with TemporaryDirectory() as temporary:\n'
        '                root = self._wiki_root(Path(temporary))\n'
        '                catalog = root / ".source_catalog"\n'
        '                catalog.mkdir(parents=True, exist_ok=True)\n'
        '                # a stale entry makes the prune probe run at all\n'
        '                (catalog / _PAUSE_REFCOUNT_NAME).write_text(\n'
        '                    json.dumps([{"pid": 999999, "joined": False}]), encoding="utf-8"\n'
        '                )\n'
        '                scope = PausedWorkerScope(\n'
        '                    root=root, command_prefix=["stub"], enabled=True,\n'
        '                    graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,\n'
        '                    deadline=1.0, stats=_normalize_stats({}),\n'
        '                )\n',
    ),
]


def main() -> int:
    if "I-04-B" not in str(TESTS):
        raise SystemExit("refusing to edit outside the I-04-B attempt")
    text = TESTS.read_text(encoding="utf-8")
    problems: list[str] = []
    for name, old, new in FIXES:
        count = text.count(old)
        if count != 1:
            problems.append(f"{name}: expected 1 match, found {count}")
            continue
        text = text.replace(old, new, 1)
        print(f"applied  {name}")
    if problems:
        print("FAILED:", *problems, sep="\n  ")
        return 1
    TESTS.write_text(text, encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
