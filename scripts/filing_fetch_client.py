"""Thin subprocess client for the standalone filing-fetch skill.

Revenue-forecast no longer owns identity resolution, reuse-first lookup, market
routing, staging, dedup, or canonical write.  Those responsibilities belong to
``filing-fetch`` (which delegates to ``company-wiki``).  This module merely
constructs a request, calls the filing-fetch CLI, validates the response, and
returns a capture-ready handle.  ``company_wiki_source.py`` then converts that
handle into a revenue source/capture record.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

class _ClientError(RuntimeError):
    """Raised when filing-fetch cannot return a capture-ready handle."""

# The location of the standalone filing-fetch canonical repo.
# When the two repos live as sibling directories inside the same parent this
# relative lookup works; a caller may override via the *filing_fetch_root*
# keyword argument.
_SKILL_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_FILING_FETCH_ROOT = _SKILL_ROOT.parent / "filing-fetch"


def resolve_filing(
    request: dict[str, Any],
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    filing_fetch_root: Path | None = None,
) -> dict[str, Any]:
    """Resolve (or, when authorized, ensure) a filing via filing-fetch.

    Returns the capture-ready ``handle`` dict on success, or raises
    ``FilingFetchError`` with the upstream error message.
    """
    root = filing_fetch_root or _DEFAULT_FILING_FETCH_ROOT
    script = root / "scripts" / "fetch_filing.py"
    if not script.is_file():
        raise _ClientError(
            f"filing-fetch script not found at {script}; "
            "install the skill or override filing_fetch_root"
        )
    cmd = [sys.executable, str(script)]
    if allow_download:
        cmd.append("--allow-download")
    cmd.extend(["--timeout-seconds", str(timeout_seconds)])
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        completed = subprocess.run(
            cmd,
            input=json.dumps(request, ensure_ascii=False),
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            timeout=timeout_seconds + 10,  # small grace beyond the deadline
            cwd=root,
            env=environment,
            check=False,
            shell=False,
            creationflags=creationflags,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _ClientError(f"filing-fetch subprocess failed: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "no stderr"
        raise _ClientError(
            f"filing-fetch exited {completed.returncode}: {detail}"
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise _ClientError("filing-fetch stdout is not valid JSON")
    if not isinstance(response, dict):
        raise _ClientError("filing-fetch response must be an object")
    status = response.get("status")
    if status != "capture_ready":
        raise _ClientError(
            f"filing-fetch returned status={status}: {response.get('error', 'unknown error')}"
        )
    handle = response.get("handle")
    if not isinstance(handle, dict):
        raise _ClientError("filing-fetch response missing 'handle' object")
    return handle
