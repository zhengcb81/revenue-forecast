"""RF-owned artifact layout shared by the job writer and catalog reader."""

from pathlib import Path
from typing import Any

STAGE_RESULTS = {"source": "result-envelope.json", "compute": "result.json", "publication": "audit.json"}
ATTEMPT_LAYOUT = "attempt/1"
RETAINED_ARTIFACTS = {
    "job": "job.json",
    "source_result": "stages/source/result-envelope.json",
    "compute_input": "stages/compute/input.json",
    "compute_result": "stages/compute/result.json",
    "report_markdown": "stages/compute/report.md",
    "publication_audit": "stages/publication/audit.json",
    "publication_registry": "registry/publications.jsonl",
}


def latest_attempt(stage: dict[str, Any]) -> dict[str, Any] | None:
    attempts = stage.get("attempts")
    if isinstance(attempts, list) and attempts and isinstance(attempts[-1], dict):
        return attempts[-1]
    return None


def stage_directory(stage: str, attempt: dict[str, Any]) -> Path:
    if stage not in STAGE_RESULTS:
        raise ValueError("unknown RF stage")
    directory = Path("stages", stage)
    layout = attempt.get("artifact_layout")
    if layout is None:
        return directory
    ordinal = attempt.get("attempt_no")
    if (layout != ATTEMPT_LAYOUT or type(ordinal) is not int or ordinal < 1
            or attempt.get("attempt_id") != f"{stage}-{ordinal}"):
        raise ValueError("unrecognized RF attempt artifact layout")
    return directory / f"a{ordinal}"


def selected_artifacts(job: dict[str, Any]) -> dict[str, Path]:
    """Resolve a recorded generation without discovering paths on disk."""
    directories = {}
    for stage in STAGE_RESULTS:
        state = job["stages"][stage]
        if not isinstance(state, dict):
            raise ValueError("unrecognized RF stage state")
        directories[stage] = stage_directory(stage, latest_attempt(state) or {})
    compute = directories["compute"]
    registry = (compute if compute != Path("stages", "compute") else Path("registry")) / "publications.jsonl"
    return {
        "job": Path("job.json"),
        "source_result": directories["source"] / STAGE_RESULTS["source"],
        "compute_input": compute / "input.json",
        "compute_result": compute / STAGE_RESULTS["compute"],
        "report_markdown": compute / "report.md",
        "publication_audit": directories["publication"] / STAGE_RESULTS["publication"],
        "publication_registry": registry,
    }
