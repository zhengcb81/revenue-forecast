"""Copy the delivered job's artifacts into the tracked evidence tree.

The job store lives under a path the repository .gitignore excludes
(``artifacts/``), so the exact bytes a Dashboard consumer needs are copied here
with a manifest; the store itself stays the durable replay source.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOB_ID = "rfjob-20261108-eb9f2a3ed336"
SOURCE = ROOT / "job-root/artifacts/rf_jobs/jobs" / JOB_ID
TARGET = ROOT / "evidence" / f"job-{JOB_ID}"

FILES = [
    "job.json",
    "stages/source/request.json",
    "stages/source/result-envelope.json",
    "stages/compute/result.json",
    "stages/compute/report.md",
    "registry/publications.jsonl",
    "logs/source-1.stderr.txt",
    "logs/source-1.stdout.txt",
    "logs/compute-1.stderr.txt",
    "logs/publication-1.stdout.txt",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    manifest = []
    for relative in FILES:
        source = SOURCE / relative
        if not source.exists():
            continue
        destination = TARGET / relative.replace("/", "__")
        shutil.copyfile(source, destination)
        manifest.append(
            {
                "path": str(destination.relative_to(ROOT)),
                "job_relative_path": relative,
                "byte_size": destination.stat().st_size,
                "sha256": sha(destination),
            }
        )
    (TARGET / "manifest.json").write_text(
        json.dumps(
            {"schema_version": "rf-job-artifact-copy/1", "job_id": JOB_ID, "files": manifest},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"copied": len(manifest), "target": str(TARGET.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
