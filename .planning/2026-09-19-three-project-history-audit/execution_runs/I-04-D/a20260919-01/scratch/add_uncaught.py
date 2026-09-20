"""Make the participant record EVERY uncaught path (including no-report exits)."""

from __future__ import annotations

import pathlib
import sys

PATH = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_participant.py"
)

OLD = '''    except Exception as exc:  # noqa: BLE001 - record, never hide
        report["raised"] = type(exc).__name__
        report["error_code"] = f"unexpected:{type(exc).__name__}"
        report["error_message"] = str(exc)
        report["after_error"] = _snapshot(root)
        exit_code = 3  # oracle.md section 1: an unexpected exception is NOT "target refused"
'''
NEW = '''    except BaseException as exc:  # noqa: BLE001 - record, never hide anything
        import traceback

        report["raised"] = type(exc).__name__
        report["error_code"] = f"unexpected:{type(exc).__name__}"
        report["error_message"] = str(exc)
        report["traceback"] = traceback.format_exc()
        report["after_error"] = _snapshot(root)
        try:
            (report_path.parent / f"uncaught.{args.tag}.txt").write_text(
                traceback.format_exc(), encoding="utf-8"
            )
        except OSError:
            pass
        # BaseException includes SystemExit: a crash injection must still be visible,
        # and the frozen exit code (90-93) must survive it.
        if isinstance(exc, SystemExit) and exc.code not in (None, 0):
            exit_code = int(exc.code)
        else:
            exit_code = 3  # oracle.md section 1: unexpected is NOT "the target refused"
'''
text = PATH.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
PATH.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
print("participant uncaught-path reporting installed")
