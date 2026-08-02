"""Thin subprocess client for the standalone filing-fetch skill.

Revenue-forecast no longer owns identity resolution, reuse-first lookup, market
routing, staging, dedup, or canonical write.  Those responsibilities belong to
``filing-fetch`` (which delegates to ``company-wiki``).  This module merely
constructs a request, calls the filing-fetch CLI, validates the response, and
returns a capture-ready handle.  ``company_wiki_source.py`` then converts that
handle into a revenue source/capture record.

Run as a CLI exactly as SKILL.md documents::

    echo '<request-json>' | python scripts/filing_fetch_client.py [--allow-download]

or with an explicit request file::

    python scripts/filing_fetch_client.py --request-file req.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class _ClientError(RuntimeError):
    """Raised when filing-fetch cannot return a capture-ready handle.

    Carries the structured upstream error fields (``status`` / ``error_code`` /
    ``retryable`` / ``candidates``) when filing-fetch emitted a JSON error
    document, so callers and the CLI surface diagnostics instead of a bare
    ``"no stderr"`` string.
    """

    def __init__(
        self,
        message: str,
        *,
        status: str | None = None,
        error_code: str | None = None,
        retryable: bool | None = None,
        candidates: list | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_code = error_code
        self.retryable = retryable
        self.candidates = candidates


# The location of the standalone filing-fetch canonical repo.
# When the two repos live as sibling directories inside the same parent this
# relative lookup works; a caller may override via the *filing_fetch_root*
# keyword argument.
_SKILL_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_FILING_FETCH_ROOT = _SKILL_ROOT.parent / "filing-fetch"


def _try_loads(text: str) -> Any:
    """Parse *text* as JSON, returning ``None`` when it is empty or not JSON."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def resolve_filing(
    request: dict[str, Any],
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    filing_fetch_root: Path | None = None,
) -> dict[str, Any]:
    """Resolve (or, when authorized, ensure) a filing via filing-fetch.

    Returns the capture-ready ``handle`` dict on success, or raises
    ``_ClientError`` carrying the upstream status / error_code / retryable /
    candidates when filing-fetch fails.
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
        # filing-fetch writes its structured error document to STDOUT and exits
        # non-zero (stderr is typically empty). Parse stdout first so callers
        # receive error_code / retryable / candidates; fall back to stderr only
        # when stdout is not a JSON object.
        payload = _try_loads(completed.stdout)
        if isinstance(payload, dict):
            raise _ClientError(
                f"filing-fetch exited {completed.returncode}: "
                f"{payload.get('error') or payload.get('status') or 'unknown error'}",
                status=payload.get("status"),
                error_code=payload.get("error_code"),
                retryable=payload.get("retryable"),
                candidates=payload.get("candidates"),
            )
        detail = completed.stderr.strip() or "no stderr"
        raise _ClientError(f"filing-fetch exited {completed.returncode}: {detail}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError:
        raise _ClientError("filing-fetch stdout is not valid JSON")
    if not isinstance(response, dict):
        raise _ClientError("filing-fetch response must be an object")
    status = response.get("status")
    if status != "capture_ready":
        raise _ClientError(
            f"filing-fetch returned status={status}: {response.get('error', 'unknown error')}",
            status=status,
            error_code=response.get("error_code"),
            retryable=response.get("retryable"),
            candidates=response.get("candidates"),
        )
    handle = response.get("handle")
    if not isinstance(handle, dict):
        raise _ClientError("filing-fetch response missing 'handle' object")
    return handle


def _emit_error(
    error_code: str,
    message: str,
    *,
    retryable: bool | None = False,
    candidates: list | None = None,
) -> None:
    """Write a structured error document to stderr (success stream on stdout)."""
    payload: dict[str, Any] = {
        "error_code": error_code,
        "error": message,
        "retryable": bool(retryable),
    }
    if candidates:
        payload["candidates"] = candidates
    sys.stderr.write(json.dumps(payload, ensure_ascii=False))
    sys.stderr.write("\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entry: read a request, resolve it, print the handle JSON to stdout."""
    # Speak UTF-8 on Windows regardless of the platform default (matches
    # filing-fetch's own stdin/stdout handling): handles and requests routinely
    # carry non-ASCII issuer names and canonical paths.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Resolve (or ensure) a filing via the standalone filing-fetch skill.",
    )
    parser.add_argument(
        "--request-file",
        help="Path to a request JSON file. If omitted, the request is read from stdin.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Authorize filing-fetch to download when no reusable source is found.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=900.0,
        help="Overall deadline forwarded to filing-fetch (default: 900).",
    )
    parser.add_argument(
        "--filing-fetch-root",
        help="Override the filing-fetch skill root (advanced; defaults to the sibling repo).",
    )
    args = parser.parse_args(argv)

    if args.request_file:
        try:
            request_text = Path(args.request_file).read_text(encoding="utf-8")
        except OSError as exc:
            _emit_error("config_error", f"cannot read request file: {exc}", retryable=False)
            return 1
    else:
        request_text = sys.stdin.read()

    request = _try_loads(request_text)
    if not isinstance(request, dict):
        _emit_error("config_error", "request must be a JSON object", retryable=False)
        return 1

    root = Path(args.filing_fetch_root) if args.filing_fetch_root else None
    try:
        handle = resolve_filing(
            request,
            allow_download=args.allow_download,
            timeout_seconds=args.timeout_seconds,
            filing_fetch_root=root,
        )
    except _ClientError as exc:
        _emit_error(
            exc.error_code or exc.status or "fatal",
            str(exc),
            retryable=exc.retryable,
            candidates=exc.candidates,
        )
        return 2

    sys.stdout.write(json.dumps(handle, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
