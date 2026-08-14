"""Command registry and execution attestation (CA-104).

A CommandSpec freezes what a command IS (argv, cwd, env allowlist, timeout,
expected tier, side-effect budget).  A CommandResult is an immutable artifact
of one execution: exit code, business outcome (pass / structured_failure /
infra_error via success/failure markers), collected/passed/failed/skipped
(pytest-style parsing), duration, and stdout/stderr SHA-256 — never any
environment VALUE (secrets never enter results).  Replay re-runs the spec and
reports output-hash differences against the recorded artifact.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PYTEST_RE = re.compile(
    r"(?P<count>\d+) passed(?:\D+(?P<fail>\d+) failed)?"
    r"(?:\D+(?P<skip>\d+) skipped)?"
)

BASE_ENV_KEYS = ("SYSTEMROOT", "PATH", "TEMP", "TMP", "USERPROFILE", "PYTHONIOENCODING")


@dataclass
class CommandSpec:
    id: str
    argv: list[str]
    cwd: str = "."
    env_allowlist: list[str] = field(default_factory=list)
    timeout_seconds: int = 600
    expected_tier: str = "T0"
    side_effect_budget: dict[str, Any] = field(default_factory=dict)
    success_markers: list[str] = field(default_factory=list)
    failure_markers: list[str] = field(default_factory=list)
    infra_markers: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CommandSpec":
        if not isinstance(payload.get("argv"), list) or not payload["argv"]:
            raise ValueError(f"spec {payload.get('id')!r} requires non-empty argv")
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "argv": list(self.argv),
            "cwd": self.cwd,
            "env_allowlist": list(self.env_allowlist),
            "timeout_seconds": self.timeout_seconds,
            "expected_tier": self.expected_tier,
            "side_effect_budget": dict(self.side_effect_budget),
            "success_markers": list(self.success_markers),
            "failure_markers": list(self.failure_markers),
            "infra_markers": list(self.infra_markers),
        }


def _build_env(allowlist: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for key in BASE_ENV_KEYS:
        if key in os.environ:
            env[key] = os.environ[key]
    for key in allowlist:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def _parse_pytest(text: str) -> dict[str, int]:
    match = PYTEST_RE.search(text)
    if not match:
        return {"collected": 0, "passed": 0, "failed": 0, "skipped": 0}
    passed = int(match.group("count"))
    failed = int(match.group("fail") or 0)
    skipped = int(match.group("skip") or 0)
    return {
        "collected": passed + failed + skipped,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def run(spec: CommandSpec, root: Path) -> dict[str, Any]:
    """Execute the spec; returns the result artifact (never contains env values)."""
    cwd = (root / spec.cwd).resolve()
    started = datetime.now(timezone.utc)
    proc = subprocess.run(
        spec.argv,
        cwd=str(cwd),
        env=_build_env(spec.env_allowlist),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=spec.timeout_seconds,
    )
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    duration = (datetime.now(timezone.utc) - started).total_seconds()

    outcome = "pass" if proc.returncode == 0 else "fail"
    for marker in spec.failure_markers:
        if marker in stdout or marker in stderr:
            outcome = "structured_failure"
    for marker in spec.infra_markers:
        if marker in stdout or marker in stderr:
            outcome = "infra_error"

    pytest_stats = _parse_pytest(stdout + stderr)
    return {
        "schema_version": 1,
        "spec_id": spec.id,
        "exit_code": proc.returncode,
        "business_outcome": outcome,
        "collected": pytest_stats["collected"],
        "passed": pytest_stats["passed"],
        "failed": pytest_stats["failed"],
        "skipped": pytest_stats["skipped"],
        "duration_seconds": round(duration, 3),
        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8", "replace")).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8", "replace")).hexdigest(),
        "started_at_utc": started.isoformat(),
        "argv": list(spec.argv),
        "cwd": spec.cwd,
        "expected_tier": spec.expected_tier,
    }


def replay_diff(
    spec: CommandSpec, recorded: dict[str, Any], root: Path
) -> dict[str, Any]:
    """Re-run the spec and diff output hashes against the recorded artifact."""
    current = run(spec, root)
    return {
        "spec_id": spec.id,
        "stdout_changed": current["stdout_sha256"] != recorded.get("stdout_sha256"),
        "stderr_changed": current["stderr_sha256"] != recorded.get("stderr_sha256"),
        "exit_changed": current["exit_code"] != recorded.get("exit_code"),
        "recorded_stdout_sha256": recorded.get("stdout_sha256"),
        "current_stdout_sha256": current["stdout_sha256"],
    }
