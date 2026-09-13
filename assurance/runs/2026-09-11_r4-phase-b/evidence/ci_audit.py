"""Compact audit: every run in the window with branch/event/conclusion, plus any
open pull request and its check statuses.

Usage: python ci_audit.py [per_page]
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

OWNER = "zhengcb81"
REPOS = ("company-wiki", "revenue-forecast", "filing-fetch")


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


def main(argv: list[str]) -> int:
    per_page = argv[1] if len(argv) > 1 else "30"
    for repo in REPOS:
        payload = _get(
            f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs?per_page={per_page}"
        )
        runs = payload.get("workflow_runs", [])
        events: dict[str, int] = {}
        branches: dict[str, int] = {}
        for run in runs:
            events[run.get("event")] = events.get(run.get("event"), 0) + 1
            branches[run.get("head_branch")] = branches.get(run.get("head_branch"), 0) + 1
        print(f"== {repo}: events={events} branches={branches}")
        problems = [r for r in runs if r.get("conclusion") not in (None, "success", "skipped")]
        for run in problems:
            print(
                "   {concl:8} {sha} {name} branch={branch} event={event} id={id} {created}".format(
                    concl=run.get("conclusion"), sha=str(run.get("head_sha"))[:7],
                    name=run.get("name"), branch=run.get("head_branch"),
                    event=run.get("event"), id=run.get("id"), created=run.get("created_at"),
                )
            )
        if not problems:
            print("   (no non-success run)")
        try:
            prs = _get(f"https://api.github.com/repos/{OWNER}/{repo}/pulls?state=open&per_page=10")
            for pr in prs:
                head = pr.get("head", {}).get("sha", "")
                print(f"   PR #{pr.get('number')} {pr.get('title')[:60]!r} head={head[:7]} state={pr.get('state')}")
            if not prs:
                print("   (no open pull requests)")
        except Exception as exc:  # noqa: BLE001
            print(f"   PR query failed: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
