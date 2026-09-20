"""Breadcrumb the participant's own startup, before it touches the code under test."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_participant.py"
)

OLD = '''    deadline = time.monotonic() + args.request_budget
    scopes = []
'''
NEW = '''    deadline = time.monotonic() + args.request_budget
    _startup = report_path.parent / f"startup.{args.tag}.log"

    def _note(*parts: object) -> None:
        try:
            with _startup.open("a", encoding="utf-8") as handle:
                handle.write(f"{time.monotonic():.4f}|" + " ".join(str(p) for p in parts) + "\\n")
        except OSError:
            pass

    _note("participant-start", "root=", root, "hooks=", args.hooks)
    scopes = []
'''
text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''    try:
        outer = ff.PausedWorkerScope(
            root=root,
            command_prefix=prefix,
            enabled=enabled,
            graceful_timeout_seconds=args.graceful,
            resume_wait_seconds=args.resume_wait,
            deadline=deadline,
            stats=stats,
        )
        scopes.append(outer)
        report["before_enter"] = _snapshot(root)
        with outer:
            report["after_enter"] = _snapshot(root)
'''
NEW2 = '''    try:
        _note("creating-scope")
        outer = ff.PausedWorkerScope(
            root=root,
            command_prefix=prefix,
            enabled=enabled,
            graceful_timeout_seconds=args.graceful,
            resume_wait_seconds=args.resume_wait,
            deadline=deadline,
            stats=stats,
        )
        scopes.append(outer)
        _note("scope-created")
        report["before_enter"] = _snapshot(root)
        _note("entering-scope")
        with outer:
            _note("inside-scope", "action=", outer.action)
            report["after_enter"] = _snapshot(root)
'''
if OLD2 not in text:
    print("PATTERN 2 NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)

OLD3 = '''        report["after_exit"] = _snapshot(root)
        report["outer_action_final"] = outer.action
'''
NEW3 = '''        _note("left-scope", "action=", outer.action)
        report["after_exit"] = _snapshot(root)
        report["outer_action_final"] = outer.action
'''
if OLD3 not in text:
    print("PATTERN 3 NOT FOUND")
    sys.exit(1)
text = text.replace(OLD3, NEW3, 1)
PATH.write_text(text, encoding="utf-8")
print("participant startup breadcrumbs installed")
