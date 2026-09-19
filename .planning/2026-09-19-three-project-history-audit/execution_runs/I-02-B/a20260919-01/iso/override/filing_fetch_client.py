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
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class _ClientError(RuntimeError):
    """Raised when filing-fetch cannot return a capture-ready handle.

    Carries the structured upstream error fields (``status`` / ``error_code`` /
    ``retryable`` / ``candidates``) when filing-fetch emitted a JSON error
    document, so callers and the CLI surface diagnostics instead of a bare
    ``"no stderr"`` string.  I-02-B: also carries the frozen cross-CLI
    envelope dict when one parsed successfully (request_id/stage/cause_chain/
    side_effects/local_diag_ref) AND archives malformed upstream output via
    ``local_diag_dir`` instead of truncating it.
    """

    def __init__(
        self,
        message: str,
        *,
        status: str | None = None,
        error_code: str | None = None,
        retryable: bool | None = None,
        candidates: list | None = None,
        error_envelope: dict | None = None,
        local_diag_ref: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.error_code = error_code
        self.retryable = (
            retryable if isinstance(retryable, bool) else False
        )  # I-02-B: a string 'true' must never open the retry door
        self.candidates = candidates
        self.error_envelope = error_envelope
        self.local_diag_ref = local_diag_ref


# The location of the standalone filing-fetch canonical repo comes from an
# explicit config file (FC-1202: no implicit sibling-directory lookup).
# ``config/filing_fetch.json`` may use ${SKILL_ROOT}/${USER_PROFILE} tokens
# and must resolve to an absolute directory containing scripts/fetch_filing.py.
# A caller may override via the *filing_fetch_root* keyword argument.
_SKILL_ROOT = Path(__file__).resolve().parents[1]
FILING_FETCH_CONFIG_SCHEMA_VERSION = "1.0"
_DEFAULT_FILING_FETCH_CONFIG = _SKILL_ROOT / "config" / "filing_fetch.json"


def load_filing_fetch_root(*, config_path: Path | None = None) -> Path:
    """Load and validate the explicit filing-fetch root configuration.

    Fail closed: a missing config, an extra field (e.g. a smuggled-back
    allowlist), a relative root, or a root without ``scripts/fetch_filing.py``
    raises ``_ClientError(error_code="config_error")``.
    """
    if config_path is not None and not isinstance(config_path, Path):
        raise TypeError("config_path must be pathlib.Path or None")
    selected = config_path or _DEFAULT_FILING_FETCH_CONFIG
    try:
        selected = selected.expanduser().resolve(strict=True)
    except OSError as exc:
        raise _ClientError(
            f"filing-fetch config does not exist: {selected}",
            error_code="config_error",
            retryable=False,
        ) from exc
    if not selected.is_file():
        raise _ClientError(
            "filing-fetch config must be a file",
            error_code="config_error",
            retryable=False,
        )
    try:
        payload = json.loads(selected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _ClientError(
            f"invalid filing-fetch config: {exc}",
            error_code="config_error",
            retryable=False,
        ) from exc
    if not isinstance(payload, dict):
        raise _ClientError(
            "filing-fetch config must be an object",
            error_code="config_error",
            retryable=False,
        )
    if set(payload) != {"schema_version", "filing_fetch_root"}:
        raise _ClientError(
            "filing-fetch config must contain exactly schema_version/"
            "filing_fetch_root (FC-1202: no independent allowlist, no "
            "implicit location)",
            error_code="config_error",
            retryable=False,
        )
    if payload["schema_version"] != FILING_FETCH_CONFIG_SCHEMA_VERSION:
        raise _ClientError(
            f"filing-fetch config schema_version must be "
            f"{FILING_FETCH_CONFIG_SCHEMA_VERSION}",
            error_code="config_error",
            retryable=False,
        )
    configured = payload["filing_fetch_root"]
    if (
        not isinstance(configured, str)
        or not configured.strip()
        or configured != configured.strip()
    ):
        raise _ClientError(
            "filing-fetch config filing_fetch_root must be non-empty trimmed text",
            error_code="config_error",
            retryable=False,
        )
    tokens = {
        "SKILL_ROOT": str(_SKILL_ROOT),
        "USER_PROFILE": os.environ.get("USERPROFILE") or str(Path.home()),
    }
    expanded = re.sub(
        r"\$\{(SKILL_ROOT|USER_PROFILE)\}", lambda m: tokens[m.group(1)], configured
    )
    if "${" in expanded:
        raise _ClientError(
            f"unsupported token in filing_fetch_root: {configured}",
            error_code="config_error",
            retryable=False,
        )
    root = Path(expanded).expanduser()
    if not root.is_absolute():
        raise _ClientError(
            "filing-fetch config filing_fetch_root must be absolute after "
            "token expansion",
            error_code="config_error",
            retryable=False,
        )
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise _ClientError(
            f"configured filing_fetch_root does not exist: {root}",
            error_code="config_error",
            retryable=False,
        ) from exc
    if not resolved.is_dir():
        raise _ClientError(
            "configured filing_fetch_root must be a directory",
            error_code="config_error",
            retryable=False,
        )
    if not (resolved / "scripts" / "fetch_filing.py").is_file():
        raise _ClientError(
            f"configured filing_fetch_root lacks scripts/fetch_filing.py: {resolved}",
            error_code="config_error",
            retryable=False,
        )
    return resolved


def _try_loads(text: str) -> Any:
    """Parse *text* as JSON, returning ``None`` when it is empty or not JSON."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _archive_raw_output(
    completed: subprocess.CompletedProcess,
    local_diag_dir: Path | None,
) -> Path | None:
    """I-02-B: archive the FULL upstream stdout/stderr for an opaque failure
    (never truncated); returns the archive path or None when disabled."""
    if local_diag_dir is None:
        return None
    try:
        import time

        stamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        local_diag_dir.mkdir(parents=True, exist_ok=True)
        path = local_diag_dir / f"upstream_raw_{stamp}.txt"
        path.write_text(
            f"--- stdout ---\n{completed.stdout}\n--- stderr ---\n"
            f"{completed.stderr}\n--- exit code: {completed.returncode} ---\n",
            encoding="utf-8",
        )
        return path
    except OSError:
        return None


def resolve_filing(
    request: dict[str, Any],
    *,
    allow_download: bool = False,
    timeout_seconds: float = 900.0,
    filing_fetch_root: Path | None = None,
    company_wiki_config: Path | None = None,
    local_diag_dir: Path | None = None,
) -> dict[str, Any]:
    """Resolve (or, when authorized, ensure) a filing via filing-fetch.

    Returns the capture-ready ``handle`` dict on success, or raises
    ``_ClientError`` carrying the upstream status / error_code / retryable /
    candidates when filing-fetch fails.
    """
    root = filing_fetch_root or load_filing_fetch_root()
    script = root / "scripts" / "fetch_filing.py"
    if not script.is_file():
        raise _ClientError(
            f"filing-fetch script not found at {script}; "
            "install the skill or override filing_fetch_root"
        )
    cmd = [sys.executable, str(script)]
    if allow_download:
        cmd.append("--allow-download")
    if company_wiki_config is not None:
        cmd.extend(["--config", str(company_wiki_config)])
    cmd.extend(["--timeout-seconds", str(timeout_seconds)])
    environment = dict(os.environ)
    environment["PYTHONUTF8"] = "1"
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0  # type: ignore[attr-defined]
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
            # Flat cross-CLI envelope (already validated upstream): passthrough
            # code/retryable/request_id/stage/cause_chain verbatim.
            if isinstance(
                payload.get("error_envelope_schema_version"), str
            ) and payload.get("error_envelope_schema_version").startswith(
                "cross-cli-error-envelope"
            ):
                raise _ClientError(
                    f"filing-fetch exited {completed.returncode}: "
                    f"{payload.get('error') or 'unknown error'}",
                    status=payload.get("status"),
                    error_code=payload.get("code") or payload.get("error_type"),
                    retryable=(
                        payload.get("retryable")
                        if isinstance(payload.get("retryable"), bool)
                        else False
                    ),
                    error_envelope=payload,
                )
            # Adapter-1.0 worker shape nests the error fields under "error";
            # a flat envelope carries them at the top level.  Either way the
            # code/retryable/request_id stay structurally readable - never
            # reduced to the outer status string.  The fail-closed mirror of
            # the frozen retryable set (decision.md): a provider-declared
            # code may carry its declared retryability ONLY for
            # upstream_unavailable; unknown codes never open the retry door.
            error_obj = payload.get("error")
            if not isinstance(error_obj, dict):
                error_obj = {}
            declared_code = payload.get("error_code") or error_obj.get("code")
            declared_retryable = payload.get("retryable")
            if not isinstance(declared_retryable, bool):
                declared_retryable = error_obj.get("retryable")
            if declared_code == "upstream_unavailable":
                retryable = (
                    declared_retryable
                    if isinstance(declared_retryable, bool)
                    else False
                )
            else:
                retryable = False
            raise _ClientError(
                f"filing-fetch exited {completed.returncode}: "
                f"{payload.get('error') or payload.get('status') or 'unknown error'}",
                status=payload.get("status"),
                error_code=declared_code,
                retryable=retryable,
                candidates=payload.get("candidates"),
                error_envelope=payload,
            )
        # I-02-B: malformed/absent JSON is never guessed into fields and never
        # truncated - archive the FULL raw output and point local_diag_ref at
        # it, emitting only a short summary in the message.
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        diag_ref = _archive_raw_output(completed, local_diag_dir)
        summary = detail.splitlines()[-1][:160] if detail else "no output"
        raise _ClientError(
            f"filing-fetch exited {completed.returncode}: {summary}",
            local_diag_ref=str(diag_ref) if diag_ref else None,
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
    error_envelope: dict | None = None,
) -> None:
    """Write a structured error document to stderr (success stream on stdout).

    I-02-B: when an upstream envelope was parsed, its structured fields ride
    forward verbatim (code/retryable/request_id/stage/cause_chain/
    side_effects/local_diag_ref) - never joined back into the message."""
    payload: dict[str, Any] = {
        "error_code": error_code,
        "error": message,
        "retryable": bool(retryable),
    }
    if candidates:
        payload["candidates"] = candidates
    if isinstance(error_envelope, dict):
        payload["error_envelope"] = error_envelope
        for key in (
            "request_id",
            "stage",
            "cause_chain",
            "side_effects",
            "local_diag_ref",
        ):
            if key in error_envelope:
                payload[key] = error_envelope[key]
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
        help="Override the filing-fetch skill root (advanced; defaults to "
        "config/filing_fetch.json).",
    )
    parser.add_argument(
        "--company-wiki-config",
        type=Path,
        default=None,
        help="Override the company-wiki config passed to filing-fetch (E2E fixtures).",
    )
    parser.add_argument(
        "--diag-dir",
        type=Path,
        default=None,
        help="Where to archive FULL raw upstream output on opaque failures "
        "(I-02-B; no truncation).",
    )
    args = parser.parse_args(argv)

    if args.request_file:
        try:
            request_text = Path(args.request_file).read_text(encoding="utf-8")
        except OSError as exc:
            _emit_error(
                "config_error", f"cannot read request file: {exc}", retryable=False
            )
            return 1
    else:
        request_text = sys.stdin.read()

    request = _try_loads(request_text)
    if not isinstance(request, dict):
        _emit_error("config_error", "request must be a JSON object", retryable=False)
        return 1

    diag_dir = args.diag_dir if args.diag_dir else None
    root = Path(args.filing_fetch_root) if args.filing_fetch_root else None
    try:
        handle = resolve_filing(
            request,
            allow_download=args.allow_download,
            timeout_seconds=args.timeout_seconds,
            filing_fetch_root=root,
            company_wiki_config=args.company_wiki_config,
            local_diag_dir=diag_dir,
        )
    except _ClientError as exc:
        _emit_error(
            exc.error_code or exc.status or "fatal",
            str(exc),
            retryable=exc.retryable,
            candidates=exc.candidates,
            error_envelope=exc.error_envelope,
        )
        return 2

    sys.stdout.write(json.dumps(handle, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
