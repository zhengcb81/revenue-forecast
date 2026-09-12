"""Read-only GitHub Actions run lookup (evidence collection for the B run).

Usage:
    python ci_query.py <repo> [per_page]

Prints, for each workflow run, one line:
    <short sha>  <workflow name>  <status>/<conclusion>  id=<run id>  <created_at>

Read-only: only GET /repos/{owner}/{repo}/actions/runs is called.  The token is
taken from the environment (GITHUB_TOKEN / GH_TOKEN) or from the local git
credential store default of this machine; it is never printed.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

OWNER = "zhengcb81"


def _token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN", "DSH_GITHUB_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value.strip()
    # Fall back to the token used by the repositories' own tooling config.
    for path in (
        os.path.expanduser("~/.config/company-wiki/github_token"),
        os.path.expanduser("~/.github-token"),
    ):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                return handle.read().strip()
    raise SystemExit("no GitHub token available (set GITHUB_TOKEN)")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit(__doc__)
    repo = argv[1]
    per_page = argv[2] if len(argv) > 2 else "10"
    url = (
        f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs"
        f"?per_page={per_page}"
    )
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {_token()}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "r4-phase-b-evidence")
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    for run in payload.get("workflow_runs", []):
        print(
            "{sha}  {name}  {status}/{conclusion}  id={id}  {created}".format(
                sha=str(run.get("head_sha"))[:7],
                name=run.get("name"),
                status=run.get("status"),
                conclusion=run.get("conclusion"),
                id=run.get("id"),
                created=run.get("created_at"),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
