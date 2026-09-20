"""Insert a self-diagnosing hook that records what the participant actually sees.

Temporary: removed once the F-L8d / F-L9c scheduling problem is located.
"""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''    def __call__(self, point: str, context: dict[str, Any]) -> None:
        code = self.crashes.get(point)
'''

NEW = '''    def __call__(self, point: str, context: dict[str, Any]) -> None:
        try:
            root = Path(context.get("root") or ".")
            catalog = root / ".source_catalog"
            listing = sorted(p.name for p in catalog.iterdir()) if catalog.is_dir() else "ABSENT"
            refcount = catalog / "filing_fetch_pause.refcount"
            with open(self.dir / "hook-probe.log", "a", encoding="utf-8") as handle:
                handle.write(
                    f"{point}|tag={self.tag}|pid={os.getpid()}|root={root}|listing={listing}|"
                    f"refcount_exists={refcount.exists()}|"
                    f"refcount_text={(refcount.read_text(encoding='utf-8')[:80] if refcount.is_file() else None)!r}|"
                    f"env_call_trace={os.environ.get('I04D_CALL_TRACE')!r}\\n"
                )
        except Exception as exc:  # noqa: BLE001 - diagnostics only
            try:
                with open(self.dir / "hook-probe.log", "a", encoding="utf-8") as handle:
                    handle.write(f"{point}|PROBE-ERROR|{type(exc).__name__}: {exc}\\n")
            except OSError:
                pass
        code = self.crashes.get(point)
'''

text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("hook probe installed")
