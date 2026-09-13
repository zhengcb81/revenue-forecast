"""Read-only progress view of a GitHub Actions run: per job, the step that is
running now (or the first failing step), with elapsed time.

Usage:
    python ci_progress.py <repo> <run_id>

Only GET requests; the token comes from the environment and is never printed.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import UTC, datetime

OWNER = "zhengcb81"


def _token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value.strip()
    raise SystemExit("no GitHub token available (set GITHUB_TOKEN)")


def _get(url: str):
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {_token()}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "r4-phase-b-evidence")
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def _minutes(start: str | None, end: str | None) -> str:
    if not start:
        return "?"
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    begin = datetime.strptime(start, fmt).replace(tzinfo=UTC)
    stop = (
        datetime.strptime(end, fmt).replace(tzinfo=UTC)
        if end
        else datetime.now(UTC)
    )
    return f"{(stop - begin).total_seconds() / 60:.1f}m"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(__doc__)
    repo, run_id = argv[1], argv[2]
    run = _get(f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs/{run_id}")
    print(
        "run {id} sha={sha} {status}/{conclusion} started={started} "
        "elapsed={elapsed} updated={updated}".format(
            id=run.get("id"), sha=str(run.get("head_sha"))[:7],
            status=run.get("status"), conclusion=run.get("conclusion"),
            started=run.get("run_started_at"),
            elapsed=_minutes(run.get("run_started_at"), run.get("updated_at")),
            updated=run.get("updated_at"),
        )
    )
    jobs = _get(
        f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs/{run_id}/jobs"
    )["jobs"]
    for job in jobs:
        steps = job.get("steps", [])
        current = next(
            (s for s in steps if s.get("status") == "in_progress"), None
        )
        failed = next((s for s in steps if s.get("conclusion") == "failure"), None)
        done = sum(1 for s in steps if s.get("conclusion") == "success")
        print(
            "  {name:16} {status:12} {concl:9} steps ok={done}/{total} "
            "now={now} started={started} elapsed={elapsed}".format(
                name=job["name"], status=job.get("status"),
                concl=str(job.get("conclusion")), done=done, total=len(steps),
                now=(current or failed or {}).get("name", "-"),
                started=job.get("started_at"),
                elapsed=_minutes(job.get("started_at"), job.get("completed_at")),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
