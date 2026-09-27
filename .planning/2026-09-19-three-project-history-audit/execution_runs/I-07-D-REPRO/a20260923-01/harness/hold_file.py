"""I-07-D share-none file holder (F02 scan-error / F05 producer fault).

Opens the given scratch file with Win32 CreateFileW(ShareMode=0) so that a
read attempt by the product in ANOTHER process fails with PermissionError
(WinError 32) — a genuine OSError at the product's own read site
(scanner.py:964-976 per-file path / summarizer.py:165 read_text).

Protocol:
  1. opens the handle, writes  <state_dir>/ready_<label>.json
  2. waits until <state_dir>/release_<label>.json exists (driver-controlled)
     or --max-hold seconds elapse, then closes the handle
  3. writes <state_dir>/hold_<label>.json  (opened_at/closed_at/window)

Touches ONLY the given file path (must live under %TEMP%\\i07d) and the
state_dir evidence files.  Never touches production.

Usage: hold_file.py <path> <state_dir> <label> [--max-hold 300]
"""
from __future__ import annotations

import argparse
import ctypes
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

GENERIC_READ = 0x80000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID = 0xFFFFFFFFFFFFFFFF


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("state_dir")
    ap.add_argument("label")
    ap.add_argument("--max-hold", type=float, default=300.0)
    args = ap.parse_args()

    target = Path(args.path)
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    release = state / f"release_{args.label}.json"

    if "i07d" not in str(target).lower() and "i07d" not in str(state).lower():
        rec = {"ok": False, "error": "refusing: target is not under the i07d scratch tree",
               "path": str(target)}
        (state / f"hold_{args.label}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(rec, ensure_ascii=False))
        return 1

    k32 = ctypes.windll.kernel32
    k32.CreateFileW.restype = ctypes.c_void_p
    k32.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_void_p]
    handle = k32.CreateFileW(str(target), GENERIC_READ, 0, None,
                             OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
    opened = time.time()
    if handle in (None, 0, INVALID):
        rec = {"ok": False, "error": "CreateFileW failed", "path": str(target),
               "winerror": ctypes.get_last_error(), "opened_at": _iso(opened)}
        (state / f"hold_{args.label}.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(rec, ensure_ascii=False))
        return 1

    (state / f"ready_{args.label}.json").write_text(json.dumps(
        {"ok": True, "pid": __import__("os").getpid(), "path": str(target),
         "share_mode": 0, "opened_at": _iso(opened),
         "note": "share-none handle held; product reads in other processes raise PermissionError"},
        ensure_ascii=False, indent=1), encoding="utf-8")

    deadline = opened + args.max_hold
    while time.time() < deadline and not release.exists():
        time.sleep(0.05)
    released = time.time()
    k32.CloseHandle(handle)

    rec = {"ok": True, "label": args.label, "path": str(target),
           "pid": __import__("os").getpid(), "share_mode": 0,
           "opened_at": _iso(opened), "closed_at": _iso(released),
           "held_seconds": round(released - opened, 3),
           "released_by": "release marker" if release.exists() else "max-hold deadline"}
    (state / f"hold_{args.label}.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
