"""Fetch a GitHub Actions run's failing job log (read-only) and print the
relevant lines only - the full log can be megabytes.

Usage:
    python ci_logs.py <repo> <run_id> [pattern]

Prints, per job: name/conclusion, then up to `--max` lines matching the pattern
(default: FAILED|ERROR|AssertionError|coverage|E   ).
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

OWNER = "zhengcb81"
DEFAULT_PATTERN = r"FAILED|ERROR|Error|assert|coverage|Exceeds|exceeds|short test summary"


def _token() -> str:
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value.strip()
    raise SystemExit("no GitHub token available (set GITHUB_TOKEN)")


def _get(url: str, *, raw: bool = False):
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {_token()}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "r4-phase-b-evidence")
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    return payload.decode("utf-8", "replace") if raw else json.loads(payload)


def _get_log(url: str) -> str:
    """The logs endpoint redirects to a pre-signed blob URL: the Authorization
    header must NOT be forwarded there (it is what turns the redirect into 401).
    Follow the redirect manually and fetch the target anonymously."""
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bearer {_token()}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", "r4-phase-b-evidence")

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=120) as response:
            return response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if exc.code not in (301, 302, 303, 307, 308):
            raise
        target = exc.headers.get("Location")
    if not target:
        raise RuntimeError("redirect without a Location header")
    plain = urllib.request.Request(target)
    plain.add_header("User-Agent", "r4-phase-b-evidence")
    with urllib.request.urlopen(plain, timeout=120) as response:
        return response.read().decode("utf-8", "replace")


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        raise SystemExit(__doc__)
    repo, run_id = argv[1], argv[2]
    pattern = re.compile(argv[3] if len(argv) > 3 else DEFAULT_PATTERN)
    jobs = _get(f"https://api.github.com/repos/{OWNER}/{repo}/actions/runs/{run_id}/jobs")["jobs"]
    for job in jobs:
        conclusion = job.get("conclusion")
        print(f"== job {job['name']} -> {conclusion} (id={job['id']})")
        bad = [step for step in job.get("steps", []) if step.get("conclusion") == "failure"]
        for step in bad:
            print(f"   failing step: {step['name']}")
        if conclusion != "failure":
            continue
        try:
            log = _get_log(
                f"https://api.github.com/repos/{OWNER}/{repo}/actions/jobs/{job['id']}/logs"
            )
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"   could not fetch log: {exc}")
            continue
        lines = log.splitlines()
        hits = [line for line in lines if pattern.search(line)]
        for line in hits[-60:]:
            print("   |", line.strip()[:220])
        if not hits:
            print("   (no matching lines; tail follows)")
            for line in lines[-25:]:
                print("   |", line.strip()[:220])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
