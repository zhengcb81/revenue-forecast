"""F-L8g: make the liveness probe itself fail (rule 5), not merely lack evidence.

A live pid with no creation time is the CONSERVATIVE branch (alive), which is correct:
ADR-4 rule 5 fires when the probe cannot answer at all.  The case therefore injects a
probe failure and asserts the fail-closed outcome: nothing written, nothing run.
"""

from __future__ import annotations

import pathlib
import re
import sys

SCHED = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\scripts\i04d_schedule.py"
)

NEW = '''def case_f_l8g_unknown(run: CaseRun) -> None:
    """A liveness probe that CANNOT answer is UNKNOWN, never "dead" (ADR-4 rule 5).

    The ledger carries one live peer (the scheduler's own pid, which is demonstrably
    alive) and that peer's probe is forced to fail.  The request must then fail closed:
    no lease written, no worker command, and not one byte of the ledger changed.  A
    run that reclaimed the entry instead would resume or re-pause over a holder it
    never proved dead.
    """
    run.refcount.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "filing-fetch.pause-refcount/2",
        "generation": 1,
        "resume": {"required": False, "generation": 1, "lease_id": "", "phase": "idle"},
        "entries": [
            {
                "lease_id": "synthetic-probe-fails",
                "pid": os.getpid(),
                "os_start_time": "1",
                "boot_uuid": "000000000000",
                "invocations": 1,
                "joined": False,
            }
        ],
        "owner": {
            "lease_id": "synthetic-probe-fails",
            "generation": 1,
            "pid": os.getpid(),
            "boot_uuid": "000000000000",
            "os_start_time": "1",
        },
    }
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["injected"] = {
        "pid": os.getpid(),
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
    }
    run.spawn(
        "prober",
        resume_wait=0.2,
        graceful=0.2,
        extra_env={"I04D_PROBE_INJECT": json.dumps({os.getpid(): "unknown"})},
    )
    run.reap("prober")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
        "payload": _read_json(run.refcount),
    }
'''

text = SCHED.read_text(encoding="utf-8")
pattern = re.compile(
    r"^def case_f_l8g_unknown\(run: CaseRun\) -> None:\n(?:.*?\n)*?\n\n", re.MULTILINE
)
match = pattern.search(text)
if not match:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text[: match.start()] + NEW + "\n\n" + text[match.end() :]
SCHED.write_text(text, encoding="utf-8")
print("case_f_l8g_unknown rewritten")
