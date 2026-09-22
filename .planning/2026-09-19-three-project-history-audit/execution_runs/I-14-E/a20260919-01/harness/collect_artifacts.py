"""I-14-E: artifact-presence evidence per run (CF-I14F-X1 / oracle-addendum-B B1).

For every run recorded in a band JSON, walk that run's own basetemp and record, per run:

  * the real path lengths of ``fake-project`` and ``fake-project/.source_catalog``
  * presence/absence + size + sha256 of every launcher artifact
    (worker_launcher_events.jsonl, worker_launcher.lock, worker_control.json,
     fake_worker_count.txt, worker_runtime.json, worker_stdout-*/worker_stderr-* logs)
  * a causation class derived from those facts by the rules frozen in addendum B1

Small artifacts are copied into ``after/artifacts-<band>/<run-tag>/`` so the evidence survives
even if the %TEMP% scratch is cleaned later.  Read-only with respect to the scratch trees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
AFTER = ATTEMPT / "after"
ARTIFACT_NAMES = (
    "worker_launcher_events.jsonl",
    "worker_launcher.lock",
    "worker_control.json",
    "fake_worker_count.txt",
    "worker_runtime.json",
)
COPY_LIMIT_BYTES = 2_000_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(verdict: str, events_present: bool, statuses: list[str],
             runs: list[dict]) -> str:
    """Applies the rules frozen in oracle-addendum-B B1 (no post-hoc invention)."""
    if verdict == "passed":
        return "passed"
    if not events_present:
        return "artifact-absence(path/redirect cause)"
    if "child_started" not in statuses:
        return "supervisor-start-latency(no child_started seen)"
    if "child_unresponsive" not in statuses:
        return "no-watchdog-kill-observed"
    killed = [a.get("unresponsive_uptime_seconds") for a in runs
              if a.get("unresponsive_uptime_seconds") is not None]
    if killed and all(u > 0.5 for u in killed):
        return "startup-latency(child alive past the 0.5 s watchdog)"
    if killed:
        return "mixed(kill at <=0.5 s exists)"
    return "unclassified"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--band", required=True, help="after/band-*.json")
    parser.add_argument("--scratch", required=True, help="that band's scratch root")
    parser.add_argument("--out", required=True)
    parser.add_argument("--copy-to", default="")
    args = parser.parse_args(argv)

    band = json.loads(Path(args.band).read_text(encoding="utf-8"))
    scratch = Path(args.scratch)
    out_path = Path(args.out)
    copy_root = Path(args.copy_to) if args.copy_to else None
    if copy_root is not None:
        copy_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for run in band["results"]:
        tag = f"{run['condition']}-p{run['pass']}-{run['tree']}-{run['node']}-{run['run']}"
        run_dir = Path(run["cwd"])
        project = next(run_dir.rglob("fake-project"), None)
        catalog = project / ".source_catalog" if project else None
        entry: dict = {
            "tag": tag, "verdict": run["verdict"], "returncode": run["returncode"],
            "assertion": (run.get("assertion") or "")[:120],
            "project_path": str(project) if project else None,
            "project_path_len": len(str(project)) if project else None,
            "catalog_path": str(catalog) if catalog else None,
            "catalog_path_len": len(str(catalog)) if catalog else None,
            "project_exists": bool(project and project.exists()),
            "catalog_exists": bool(catalog and catalog.exists()),
            "artifacts": {},
            "max_artifact_path_len": None,
        }
        statuses = (run.get("events") or {}).get("statuses") or []
        attempts = (run.get("events") or {}).get("attempts") or []
        if catalog and catalog.exists():
            lengths = []
            for name in ARTIFACT_NAMES:
                path = catalog / name
                entry["artifacts"][name] = {
                    "exists": path.exists(),
                    "path_len": len(str(path)),
                    "bytes": path.stat().st_size if path.exists() else None,
                    "sha256": sha256(path) if path.exists() else None,
                }
                lengths.append(len(str(path)))
            logs = sorted(list(catalog.glob("worker_stdout-*.log")) +
                          list(catalog.glob("worker_stderr-*.log")))
            entry["artifacts"]["worker_logs"] = {
                "count": len(logs),
                "names": [p.name for p in logs],
                "path_lens": [len(str(p)) for p in logs],
                "exists": bool(logs),
            }
            lengths += [len(str(p)) for p in logs]
            entry["max_artifact_path_len"] = max(lengths) if lengths else None
            if copy_root is not None:
                target = copy_root / tag
                target.mkdir(parents=True, exist_ok=True)
                for path in list(catalog.glob("*")):
                    if path.is_file() and path.stat().st_size <= COPY_LIMIT_BYTES:
                        shutil.copyfile(path, target / path.name)
        events_present = bool((run.get("events") or {}).get("events_present"))
        entry["events_present"] = events_present
        entry["causation_class"] = classify(run["verdict"], events_present, statuses, attempts)
        rows.append(entry)

    summary: dict = {"band": str(args.band), "node": band["node"],
                     "condition": band["condition"], "runs": len(rows)}
    classes: dict = {}
    for row in rows:
        classes[row["causation_class"]] = classes.get(row["causation_class"], 0) + 1
    summary["causation_classes"] = classes
    summary["events_missing_runs"] = [r["tag"] for r in rows if not r["events_present"]]
    summary["max_artifact_path_len_overall"] = max(
        (r["max_artifact_path_len"] or 0) for r in rows) if rows else None
    summary["path_len_note"] = ("all artifact paths must stay <= 259 chars for the launcher's "
                               "redirect/events files; a missing events file WITH an existing "
                               ".source_catalog is the path-cause signature")
    payload = {"summary": summary, "runs": rows}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("out:", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
