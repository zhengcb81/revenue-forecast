"""I-14-B capability probe for the 30/60/120 s immediate-UI check.

READ-ONLY.  It answers one question with raw evidence: does THIS attempt's
environment actually support capturing the worker's login UI at +30/+60/+120 s
against a pre-placed recorder?

It deliberately does NOT claim impossibility -- it records exactly what was
looked for and what was found, so a reviewer can see the boundary of the claim.

Usage:
  <iso-python> -X utf8 -B harness/probe_ui_capture.py --out evidence/ui_capability_probe.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent

CAPTURE_MODULES = ["PIL", "pyautogui", "mss", "selenium", "playwright", "pywinauto",
                   "uiautomation", "pyscreenshot", "cv2"]
EXTERNAL_TOOLS = ["magick", "nircmd", "ffmpeg", "chrome", "msedge", "chromedriver",
                  "msedgedriver", "playwright"]

# places a pre-placed login recorder would plausibly live (read-only search)
SEARCH_ROOTS = [
    (r"C:\Users\郑曾波\Projects\company-wiki", 3),
    (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit", 3),
]
NAME_TOKENS = ["login", "recorder", "uicapture", "ui_capture", "screenshot", "webcap"]


def probe_modules() -> dict:
    found = {}
    for name in CAPTURE_MODULES:
        try:
            found[name] = importlib.util.find_spec(name) is not None
        except Exception as exc:  # pragma: no cover
            found[name] = f"error: {exc}"
    return found


def probe_tools() -> dict:
    return {name: (shutil.which(name) or None) for name in EXTERNAL_TOOLS}


def probe_recorder(limit: int = 4000) -> dict:
    hits = []
    scanned = 0
    for root, depth in SEARCH_ROOTS:
        base = Path(root)
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            current = Path(dirpath)
            try:
                level = len(current.relative_to(base).parts)
            except ValueError:
                continue
            if level >= depth:
                dirnames[:] = []
            for filename in filenames:
                scanned += 1
                if scanned > limit:
                    break
                low = filename.lower()
                if any(token in low for token in NAME_TOKENS):
                    hits.append(str(current / filename))
            if scanned > limit:
                break
    return {"files_scanned": scanned, "scan_limit": limit, "candidate_files": hits}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ATTEMPT / "evidence" / "ui_capability_probe.json"))
    args = ap.parse_args()

    user_interactive = None
    try:
        user_interactive = bool(sys.flags.interactive) or sys.stdin is not None
    except Exception:
        pass

    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "probed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "background_processes_started_by_this_attempt": 0,
        "python": sys.executable,
        "capture_modules_importable": probe_modules(),
        "external_tools_on_path": probe_tools(),
        "preplaced_recorder_candidates": probe_recorder(),
        "environment": {
            "SESSIONNAME": os.environ.get("SESSIONNAME"),
            "interactive_flag": user_interactive,
            "hostname": socket.gethostname(),
        },
        "what_this_probe_cannot_see": [
            "whether a human could log in and screenshot the worker manually",
            "whether an installed skill outside the searched roots carries a recorder",
            "whether a browser automation stack could be installed offline",
        ],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    modules = doc["capture_modules_importable"]
    tools = {k: v for k, v in doc["external_tools_on_path"].items() if v}
    print(json.dumps({
        "capture_modules_found": sorted(k for k, v in modules.items() if v is True),
        "external_tools_found": sorted(tools),
        "recorder_candidates": doc["preplaced_recorder_candidates"]["candidate_files"],
        "files_scanned": doc["preplaced_recorder_candidates"]["files_scanned"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
