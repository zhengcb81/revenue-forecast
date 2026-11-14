"""Collect artifact hashes and engine results for the delivered job."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[1]
JOB_ID = "rfjob-20261108-eb9f2a3ed336"
JOB = ROOT / "job-root/artifacts/rf_jobs/jobs" / JOB_ID
COPY = ROOT / "evidence" / f"job-{JOB_ID}"
INPUT = ROOT / "inputs" / "mongodb-fy2025-input.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stage_summary(stages):
    """Normalise the two stage shapes (job-state dict vs JobView list)."""
    if isinstance(stages, dict):
        items = [{"stage": name, **value} for name, value in stages.items()]
    else:
        items = list(stages or [])
    summary = []
    for stage in items:
        attempts = stage.get("attempts") or []
        summary.append(
            {
                "stage": stage.get("stage"),
                "status": stage.get("status"),
                "attempt_count": stage.get("attempt_count", len(attempts)),
                "attempts": [
                    {
                        "attempt_id": attempt.get("attempt_id"),
                        "status": attempt.get("status"),
                        "exit_code": attempt.get("exit_code"),
                        "elapsed_seconds": attempt.get("elapsed_seconds"),
                        "observations": attempt.get("observations"),
                    }
                    for attempt in attempts
                ],
            }
        )
    return summary


def main() -> int:
    result = json.loads((JOB / "stages/compute/result.json").read_text(encoding="utf-8"))
    compute_input = JOB / "stages/compute/input.json"
    built_document = json.loads(INPUT.read_text(encoding="utf-8"))
    stored_document = json.loads(compute_input.read_text(encoding="utf-8"))
    registry_line = json.loads(
        (JOB / "registry/publications.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1]
    )
    job_state = json.loads((JOB / "job.json").read_text(encoding="utf-8"))
    report = {
        "job_id": JOB_ID,
        "input": {
            "path": str(INPUT.relative_to(WORKTREE)),
            "byte_size": INPUT.stat().st_size,
            "sha256": sha(INPUT),
            "schema_version": built_document["schema_version"],
            "forecast_version": built_document["forecast_version"],
        },
        "job_store": {
            "root_is_gitignored": True,
            "root_note": (
                "the job store lives under artifacts/, which the repository .gitignore excludes; "
                "exact copies are recorded under tracked_copies and in the copy manifest"
            ),
            "job_json": str((JOB / "job.json").relative_to(WORKTREE)),
            "compute_input_sha256": sha(compute_input),
            "compute_input_equals_built_input_bytes": sha(compute_input) == sha(INPUT),
            "compute_input_equals_built_input_content": built_document == stored_document,
            "result_json": str((JOB / "stages/compute/result.json").relative_to(WORKTREE)),
            "result_json_bytes_sha256": sha(JOB / "stages/compute/result.json"),
            "report_md": str((JOB / "stages/compute/report.md").relative_to(WORKTREE)),
            "report_md_sha256": sha(JOB / "stages/compute/report.md"),
            "source_envelope": str((JOB / "stages/source/result-envelope.json").relative_to(WORKTREE)),
            "source_envelope_sha256": sha(JOB / "stages/source/result-envelope.json"),
            "tracked_copies": {
                "directory": str(COPY.relative_to(WORKTREE)),
                "manifest": str((COPY / "manifest.json").relative_to(WORKTREE)),
                "result_json": str((COPY / "stages__compute__result.json").relative_to(WORKTREE)),
                "result_json_sha256": sha(COPY / "stages__compute__result.json"),
                "report_md": str((COPY / "stages__compute__report.md").relative_to(WORKTREE)),
                "report_md_sha256": sha(COPY / "stages__compute__report.md"),
                "job_json": str((COPY / "job.json").relative_to(WORKTREE)),
                "job_json_sha256": sha(COPY / "job.json"),
                "registry_line_file": str((COPY / "registry__publications.jsonl").relative_to(WORKTREE)),
                "registry_line_file_sha256": sha(COPY / "registry__publications.jsonl"),
            },
        },
        "job_state_summary": {
            "status": job_state.get("status"),
            "status_known": job_state.get("status_known"),
            "budget": job_state.get("budget"),
            "stages": _stage_summary(job_state.get("stages")),
        },
        "engine_result": {
            "result_sha256": result["result_sha256"],
            "input_sha256": result["input_sha256"],
            "engine_version": result["engine_version"],
            "schema_version": result["schema_version"],
            "confidence_score": result["confidence"]["score"],
            "confidence_rating": result["confidence"]["rating"],
            "base_revenue": result["base_revenue"],
            "annual_revenue": {
                scenario: result["consolidated_forecast"][scenario]["annual_revenue"]
                for scenario in ("low", "base", "high")
            },
            "cagr": {
                scenario: result["consolidated_forecast"][scenario]["cagr"]
                for scenario in ("low", "base", "high")
            },
        },
        "publication_registry_line": registry_line,
    }
    (ROOT / "evidence" / "artifacts.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "job_id": JOB_ID,
                "input_sha256": report["input"]["sha256"],
                "result_sha256": result["result_sha256"],
                "tracked_result_sha256": report["job_store"]["tracked_copies"]["result_json_sha256"],
                "content_matches": report["job_store"]["compute_input_equals_built_input_content"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
