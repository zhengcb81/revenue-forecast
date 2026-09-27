"""Probe: exact-mode ensure with --allow-download but NO authorization receipt.

Evidence for the report: does the REAL chain download when the caller never
supplied a DownloadAuthorization?  Observed behavior is recorded, not fixed.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import zr102_t1_runner as runner  # noqa: E402

work = Path(tempfile.mkdtemp(prefix="zr102-probe-unauth-"))
runner.materialize_workdir(work)
runner.assert_hermetic(work)
runner.run_seed_script(work, "seed_masters.py")
scan = runner.run_wiki_cli(work, "scan")
assert scan.returncode == 0, scan.stderr[-500:]

request = dict(runner.S1_REQUEST)  # mode=exact, no authorization key
proc = runner.run_chain(
    work, request, entry="filing_client", allow_download=True, timeout_seconds=180
)
spy = runner.read_spy(work)
actions = [e.get("action") for e in spy]
files = runner._chain_files(work)
print(
    json.dumps(
        {
            "work": str(work),
            "chain_exit": proc.returncode,
            "spy_actions": actions,
            "download_fetch_count": actions.count("fetch"),
            "files_under_temp_companies": files,
            "authorization_in_request": "authorization" in request,
            "stderr_tail": proc.stderr[-400:],
        },
        indent=2,
    )
)
