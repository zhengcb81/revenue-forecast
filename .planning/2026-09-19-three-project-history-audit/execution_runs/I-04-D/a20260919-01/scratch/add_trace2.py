"""Add outcome tracing to the I-04-D patcher (temporary diagnostic)."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = """    def _persist_locked(self, state: _LeaseState, *, resume_required: bool | None = None) -> None:
        try:
            _write_pause_state(self.root, state, resume_required=resume_required)
"""

NEW = '''    def _persist_locked(self, state: _LeaseState, *, resume_required: bool | None = None) -> None:
        _trace = os.environ.get("I04D_HOOK_TRACE")
        if _trace:
            try:
                with open(_trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"PERSIST|{os.getpid()}|{self.lease_id}|entries="
                        f"{len(state.entries)}|owner={(state.owner or {}).get('lease_id')}|"
                        f"resume={resume_required if resume_required is not None else state.resume_required}|"
                        f"path={_pause_state_path(self.root)}\\n"
                    )
            except OSError:
                pass
        try:
            _write_pause_state(self.root, state, resume_required=resume_required)
'''

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PERSIST PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = """    def _release_locked(self) -> None:
        state = _read_pause_state(self.root)
"""
NEW2 = '''    def _release_locked(self) -> None:
        _trace = os.environ.get("I04D_HOOK_TRACE")
        if _trace:
            try:
                with open(_trace, "a", encoding="utf-8") as handle:
                    handle.write(
                        f"RELEASE-START|{os.getpid()}|{self.lease_id}|"
                        f"refcount_exists={_pause_state_path(self.root).exists()}|"
                        f"catalog_listing={sorted(p.name for p in _catalog_dir(self.root).iterdir()) if _catalog_dir(self.root).exists() else 'ABSENT'}\\n"
                    )
            except OSError:
                pass
        state = _read_pause_state(self.root)
'''
if OLD2 not in text:
    print("RELEASE PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATH.write_text(text, encoding="utf-8")
print("outcome tracing installed in the patcher")
