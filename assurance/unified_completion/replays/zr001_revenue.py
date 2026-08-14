"""ZR-001 replay: revenue-forecast production counterexamples (hermetic).

Runs the real product entrypoints at the frozen triplet, with every
side-effect redirected to a throwaway temp directory via
``REVENUE_PUBLICATION_REGISTRY``.  No real catalog, no network, no provider.

Usage:  python -B assurance/unified_completion/replays/zr001_revenue.py

Emits evidence files into ``replays/evidence/``:
  r1_generator_schema_drift.json
  r2_validate_only_writes_registry.json
  r3_draft_renderer_gate_mismatch.json
  r4_publication_non_transactional.json
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tests"))
sys.path.insert(0, str(SCRIPTS))

from test_recognition_bridge import forecast_document  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_cli(
    args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    merged = dict(os.environ)
    merged["PYTHONIOENCODING"] = "utf-8"
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, "-B", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=merged,
        cwd=str(cwd) if cwd else None,
        check=False,
        timeout=600,
    )


def write_evidence(name: str, payload: dict) -> Path:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def r1_generator_schema_drift(root: Path) -> dict:
    """Finding 023 / audit §4.1-4.2: the official generator emits a schema 3.6
    skeleton, the linter is a 3.6 linter, but the engine runtime is 3.7 —
    the generated skeleton is rejected by linter/engine."""
    work = root / "r1"
    work.mkdir(parents=True)
    registry = work / "registry.jsonl"
    skeleton = work / "skeleton.json"
    env = {"REVENUE_PUBLICATION_REGISTRY": str(registry)}
    gen = run_cli(
        [
            str(SCRIPTS / "generate_input_template.py"),
            "--name",
            "ACME Replay Test Co",
            "--base-year",
            "2025",
            "--forecast-years",
            "2026",
            "2027",
            "--currency",
            "CNY",
            "--unit",
            "million",
            "--segments",
            "Alpha",
            "Beta",
            "--output",
            str(skeleton),
        ],
        env=env,
    )
    skeleton_data = {}
    if skeleton.exists():
        try:
            skeleton_data = json.loads(skeleton.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            skeleton_data = {"parse_error": str(exc)}
    lint = run_cli([str(SCRIPTS / "lint_input.py"), str(skeleton)], env=env)
    engine = run_cli(
        [
            str(SCRIPTS / "revenue_forecast.py"),
            "--validate-only",
            "--verbose",
            str(skeleton),
        ],
        env=env,
    )
    engine_error_lines = [line for line in engine.stderr.splitlines() if line.strip()]
    return {
        "generator_rc": gen.returncode,
        "generator_schema_version": skeleton_data.get("schema_version"),
        "generator_stderr_tail": gen.stderr.strip()[-800:],
        "linter_rc": lint.returncode,
        "linter_stderr_tail": lint.stderr.strip()[-800:],
        "engine_validate_rc": engine.returncode,
        "engine_error_line_count": len(engine_error_lines),
        "engine_stderr_tail": "\n".join(engine_error_lines[-12:]),
        "registry_created_even_on_failure": registry.exists(),
        "registry_size": registry.stat().st_size if registry.exists() else 0,
        "observed_at_utc": utc_now(),
    }


def r2_validate_only_writes_registry(root: Path) -> dict:
    """Audit §4.3: ``--validate-only`` on a valid fixture returns 0 but still
    creates the publication registry because the CLI runs the full formal
    ``run_forecast`` before honoring the flag."""
    work = root / "r2"
    work.mkdir(parents=True)
    registry = work / "registry.jsonl"
    valid = work / "valid_input.json"
    valid.write_text(
        json.dumps(forecast_document(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    env = {"REVENUE_PUBLICATION_REGISTRY": str(registry)}
    before = registry.exists()
    completed = run_cli(
        [str(SCRIPTS / "revenue_forecast.py"), "--validate-only", str(valid)],
        env=env,
    )
    rows = 0
    if registry.exists():
        rows = sum(
            1
            for line in registry.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return {
        "registry_existed_before": before,
        "cli_rc": completed.returncode,
        "stdout": completed.stdout.strip(),
        "registry_created": registry.exists(),
        "registry_size_bytes": registry.stat().st_size if registry.exists() else 0,
        "registry_row_count": rows,
        "observed_at_utc": utc_now(),
    }


def r3_draft_renderer_gate_mismatch(root: Path) -> dict:
    """Audit §4.4: a legal draft carries a draft receipt with empty
    ``gate_ids``; the public renderer validates against the formal gate set
    and rejects the draft."""
    from revenue_core import run_forecast
    from revenue_report import render_markdown

    data = forecast_document()
    draft = run_forecast(data, mode="draft")
    receipt = draft.get("publication_receipt") or {}
    try:
        render_markdown(draft)
        outcome = "rendered"
        message = ""
    except Exception as exc:  # noqa: BLE001 — record the observed failure verbatim
        outcome = "rejected"
        message = f"{type(exc).__name__}: {exc}"
    return {
        "draft_gate_ids": receipt.get("gate_ids"),
        "draft_formal_output_mode": receipt.get("formal_output_mode"),
        "renderer_outcome": outcome,
        "renderer_error": message,
        "observed_at_utc": utc_now(),
    }


def r4_publication_non_transactional(root: Path) -> dict:
    """Audit §4.5: registry append happens before output files are written;
    a failing output write leaves an orphan registry row, and re-running the
    same input appends duplicate rows (no idempotent registration)."""
    from publication_registry import _read_entries  # noqa: F401  (import check)

    work = root / "r4"
    work.mkdir(parents=True)
    valid = work / "valid_input.json"
    valid.write_text(
        json.dumps(forecast_document(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # (a) fault injection: output parent missing -> CLI fails AFTER the
    # registry append (run_forecast registers before writing --output).
    registry = work / "registry_a.jsonl"
    env = {"REVENUE_PUBLICATION_REGISTRY": str(registry)}
    missing_parent = work / "no" / "such" / "dir" / "forecast.json"
    failed = run_cli(
        [
            str(SCRIPTS / "revenue_forecast.py"),
            str(valid),
            "--output",
            str(missing_parent),
        ],
        env=env,
    )
    orphan_rows = 0
    if registry.exists():
        orphan_rows = sum(
            1
            for line in registry.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    # (b) idempotence: two successful formal runs of the same input.
    registry_b = work / "registry_b.jsonl"
    env_b = {"REVENUE_PUBLICATION_REGISTRY": str(registry_b)}
    first = run_cli(
        [
            str(SCRIPTS / "revenue_forecast.py"),
            str(valid),
            "--output",
            str(work / "out1.json"),
        ],
        env=env_b,
    )
    second = run_cli(
        [
            str(SCRIPTS / "revenue_forecast.py"),
            str(valid),
            "--output",
            str(work / "out2.json"),
        ],
        env=env_b,
    )
    duplicate_rows = 0
    if registry_b.exists():
        duplicate_rows = sum(
            1
            for line in registry_b.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return {
        "fault_run_rc": failed.returncode,
        "fault_run_output_written": missing_parent.exists(),
        "fault_run_orphan_registry_rows": orphan_rows,
        "repeat_run_rcs": [first.returncode, second.returncode],
        "repeat_run_registry_rows": duplicate_rows,
        "duplicate_rows_for_identical_input": duplicate_rows == 2,
        "observed_at_utc": utc_now(),
    }


def product_code_hashes() -> dict:
    files = [
        "scripts/revenue_forecast.py",
        "scripts/revenue_core.py",
        "scripts/revenue_report.py",
        "scripts/revenue_publication.py",
        "scripts/publication_registry.py",
        "scripts/generate_input_template.py",
        "scripts/lint_input.py",
    ]
    return {rel: sha256_file(REPO_ROOT / rel) for rel in files}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="zr001_revenue_") as tmp:
        root = Path(tmp)
        outputs = {
            "r1_generator_schema_drift.json": r1_generator_schema_drift(root),
            "r2_validate_only_writes_registry.json": r2_validate_only_writes_registry(
                root
            ),
            "r3_draft_renderer_gate_mismatch.json": r3_draft_renderer_gate_mismatch(
                root
            ),
            "r4_publication_non_transactional.json": r4_publication_non_transactional(
                root
            ),
        }
    for name, payload in outputs.items():
        payload["product_code_hashes"] = product_code_hashes()
        payload["revenue_head"] = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        write_evidence(name, payload)
    for name in sorted(outputs):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
