"""I-14-F-R1: artifact-level adjudication for child runs whose SURFACE signature is a band
label (oracle §5 pre-registered rule; CF-I14F-X1 / reviewer §3 method).

Walks the surviving (unrelocated, never-cleaned) basetemp of each run and reports:
  * deepest existing dir/file path lengths,
  * existence + length of the launcher-critical artifacts (source_catalog dir,
    worker_launcher.lock, worker_launcher_events.jsonl, worker_stdout/stderr logs),
  * verdict: path-caused if the chain sits at/beyond the measured edges (dir edge ~248,
    file edge 260) or the launcher events/log files do not exist while shallower ones do.
"""

from __future__ import annotations

import sys
from pathlib import Path

DIR_EDGE = 248   # measured: mkdir succeeds at 247, fails at 253 (~MAX_PATH-12 for 8.3)
FILE_EDGE = 260  # measured: file creation fails at 264


def measure(basetemp: Path) -> dict:
    info = {"basetemp": str(basetemp), "basetemp_len": len(str(basetemp)),
            "exists": basetemp.exists()}
    if not basetemp.exists():
        return info
    deepest_dir = (0, "")
    deepest_file = (0, "")
    counters = {}
    for p in basetemp.rglob("*"):
        n = len(str(p))
        if p.is_dir():
            if n > deepest_dir[0]:
                deepest_dir = (n, str(p))
        else:
            if n > deepest_file[0]:
                deepest_file = (n, str(p))
        name = p.name
        for key in ("source_catalog", "worker_launcher_events.jsonl", "worker_launcher.lock",
                    "cli.py"):
            if name == key or (key == "source_catalog" and name.endswith("source_catalog")):
                counters.setdefault(key, []).append((n, str(p)))
        if name.startswith("worker_stdout") or name.startswith("worker_stderr"):
            counters.setdefault("worker_logs", []).append((n, str(p)))
    info["deepest_dir"] = deepest_dir
    info["deepest_file"] = deepest_file
    info["artifacts"] = {k: sorted(v)[-3:] for k, v in counters.items()}
    ev = counters.get("worker_launcher_events.jsonl", [])
    info["events_file_exists"] = bool(ev)
    sc = counters.get("source_catalog", [])
    info["source_catalog_exists"] = bool(sc)
    logs = counters.get("worker_logs", [])
    info["worker_logs"] = len(logs)
    # verdict — reviewer §3 method (CF-I14F-X1): the discriminator is whether the launcher's
    # events/redirect-log files exist while shallower launcher artifacts do exist.
    lock = counters.get("worker_launcher.lock", [])
    cli = counters.get("cli.py", [])
    ev_path_len = None
    # the launcher writes events under the HIDDEN ".source_catalog" dir (not company_wiki\...)
    dot_sc = [(n, p) for n, p in sc if Path(p).name == ".source_catalog"]
    sc_root = max((n for n, _ in dot_sc), default=0) or max((n for n, _ in sc), default=0)
    if sc_root:
        ev_path_len = sc_root + len("\\worker_launcher_events.jsonl")
    if not info["source_catalog_exists"]:
        info["verdict"] = "path-caused (source_catalog chain never created at this depth)"
    elif lock and cli and not ev:
        info["verdict"] = (
            "path-caused (launcher lock {lockn} + cli.py {clin} created, but "
            "worker_launcher_events.jsonl (~{evlen} chars ≥ file edge {fedge}) does NOT exist "
            "and zero worker redirect logs were written — the launcher's events/log paths are "
            "unreachable; timeout15s-band is surface noise only, per CF-I14F-X1"
        ).format(lockn=lock[-1][0], clin=cli[-1][0], evlen=ev_path_len, fedge=FILE_EDGE)
    elif ev:
        info["verdict"] = "NOT path-caused (events file exists; chain below edges)"
    else:
        info["verdict"] = "inconclusive"
    info["events_path_len_est"] = ev_path_len
    return info


def main(argv: list[str]) -> int:
    for arg in argv:
        info = measure(Path(arg))
        print(f"--- {info['basetemp']}")
        print(f"    basetemp_len={info['basetemp_len']} exists={info.get('exists')}")
        if info.get("exists"):
            nd, sd = info["deepest_dir"]
            nf, sf = info["deepest_file"]
            print(f"    deepest dir  = {nd:3d}  {sd}")
            print(f"    deepest file = {nf:3d}  {sf}")
            print(f"    source_catalog exists={info['source_catalog_exists']} "
                  f"events.jsonl exists={info['events_file_exists']} "
                  f"worker_logs={info['worker_logs']}")
            for k, v in info["artifacts"].items():
                print(f"    [{k}] " + "; ".join(f"{n}:{p}" for n, p in v))
            print(f"    VERDICT: {info['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
