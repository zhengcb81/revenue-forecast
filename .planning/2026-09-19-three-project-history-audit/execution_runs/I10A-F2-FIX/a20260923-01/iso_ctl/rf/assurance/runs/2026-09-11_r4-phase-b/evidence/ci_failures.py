"""List recent workflow runs across repos with branch/event/status, and point at
any non-success run (any branch, any workflow, including scheduled/manual).

Usage: python ci_failures.py [per_page]
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
        try:
            payload = _get(
                f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs?per_page={per_page}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"== {repo}: query failed: {exc}")
            continue
        runs = payload.get("workflow_runs", [])
        print(f"== {repo}: {len(runs)} recent runs (total_count={payload.get('total_count')})")
        bad = [r for r in runs if r.get("conclusion") not in (None, "success", "skipped")]
        for run in runs[:4]:
            print(
                "   newest: {sha} {name} branch={branch} event={event} {status}/{conclusion} id={id} {created}".format(
                    sha=str(run.get("head_sha"))[:7], name=run.get("name"),
                    branch=run.get("head_branch"), event=run.get("event"),
                    status=run.get("status"), conclusion=run.get("conclusion"),
                    id=run.get("id"), created=run.get("created_at"),
                )
            )
        if not bad:
            print("   no non-success run in this window")
        for run in bad:
            print(
                "   FAIL {sha} {name} branch={branch} event={event} {status}/{conclusion} id={id} {created} url={url}".format(
                    sha=str(run.get("head_sha"))[:7], name=run.get("name"),
                    branch=run.get("head_branch"), event=run.get("event"),
                    status=run.get("status"), conclusion=run.get("conclusion"),
                    id=run.get("id"), created=run.get("created_at"),
                    url=run.get("html_url"),
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
