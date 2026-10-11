"""Public entry for the model generalization matrix.

    python -B tools/model_generalization_matrix/run.py \
        --owned-root ABS_NEW --out-root ABS_NEW

Offline, no network / source DB / extra packages.  Runs the frozen 16-case
cross-mechanism matrix against the real draft engine, then (in ``--e2e``) also
drives the shipped CLI once on a legal and a rejection sample and the support
diagnostics CLI once, capturing their real results.

Isolation and cleanup: all scratch lives under a short temp directory inside
``--owned-root``.  Before creating it the tool records whether the path was
absent (or its sentinel content).  On success, error, or timeout it closes any
subprocess/SQLite handles, deletes only files it created, and restores the
baseline.  Fixed inputs and read-only trees are never written and their SHA is
re-checked at the end.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make the package importable whether invoked as a script or module.
_HERE = Path(__file__).resolve().parent
_TOOLS = _HERE.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from model_generalization_matrix import bootstrap  # noqa: E402
from model_generalization_matrix import cases as C  # noqa: E402
from model_generalization_matrix import report as R  # noqa: E402
from model_generalization_matrix.native import NativeEngine  # noqa: E402
from model_generalization_matrix.runner import run_case  # noqa: E402


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _tree_digest(root: Path) -> dict[str, str]:
    """SHA of every file under root (relative path -> sha).  Read-only."""
    out: dict[str, str] = {}
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in {"__pycache__", ".pytest_cache"} for part in p.parts):
            out[str(p.relative_to(root)).replace("\\", "/")] = _sha_file(p)
    return out


def _snapshot(path: Path) -> dict[str, Any]:
    """Record whether a scratch path is absent or its sentinel bytes."""
    if not path.exists():
        return {"existed": False, "sentinel": None}
    if path.is_file():
        return {"existed": True, "kind": "file", "sentinel_sha256": _sha_file(path)}
    entries = sorted(e.name for e in path.iterdir())
    return {"existed": True, "kind": "dir", "entries": entries,
            "files": _tree_digest(path),
            "directories": sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_dir())}


def run_matrix(out_root: Path, owned_root: Path, *, e2e: bool) -> dict[str, Any]:
    started_wall = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    if out_root.exists():
        raise FileExistsError(f"report output already exists: {out_root}")
    if out_root == owned_root or owned_root in out_root.parents or out_root in owned_root.parents:
        raise ValueError("report and scratch roots must be separate")
    # Fixed, read-only trees whose SHA must be unchanged at the end.
    repo = bootstrap.repo_root()
    readonly_roots = [repo / "scripts", repo / "tests"]
    readonly_before = {str(r): _tree_digest(r) for r in readonly_roots if r.exists()}

    # Isolated scratch: a fresh short path under owned_root.
    owned_before = _snapshot(owned_root)
    created_parents = []
    ancestor = owned_root
    while not ancestor.exists():
        created_parents.append(ancestor)
        ancestor = ancestor.parent
    owned_root.mkdir(parents=True, exist_ok=True)
    scratch = owned_root / f"w07-{uuid.uuid4().hex}"
    scratch_before = _snapshot(scratch)
    scratch.mkdir(exist_ok=False)

    residuals: list[str] = []
    cleanup: dict[str, Any] = {
        "scratch_path": str(scratch),
        "baseline": scratch_before,
    }

    def _finalize_cleanup() -> None:
        # Restore scratch baseline: delete only what we created.
        try:
            if scratch.exists():
                if owned_root.resolve() not in scratch.resolve().parents:
                    raise ValueError("scratch escaped owned root")
                shutil.rmtree(scratch)
            for created in created_parents:
                if created.exists() and not any(created.iterdir()):
                    created.rmdir()
            cleanup["restored_absent"] = not scratch.exists()
        except Exception as exc:  # noqa: BLE001
            cleanup["restored_absent"] = False
            residuals.append(f"scratch cleanup failed: {exc}")
        cleanup["owned_root_baseline"] = owned_before
        cleanup["owned_root_restored"] = owned_before == _snapshot(owned_root)
        if not cleanup["owned_root_restored"]:
            residuals.append("owned root baseline not restored")
        # Read-only SHA re-check (recorded into the report, not just computed).
        readonly_after = {str(r): _tree_digest(r) for r in readonly_roots if r.exists()}
        cleanup["readonly_unchanged"] = readonly_before == readonly_after
        if not cleanup["readonly_unchanged"]:
            residuals.append("read-only tree SHA changed during run (investigate)")

    try:
        runtime = bootstrap.load_runtime()
        engine = NativeEngine(runtime)
        engine_versions = {
            "schema_version": getattr(runtime, "ENGINE_SCHEMA_VERSION", None),
        }
        try:
            import revenue_core

            engine_versions["SKILL_VERSION"] = getattr(revenue_core, "SKILL_VERSION", None)
            engine_versions["FORECAST_SCHEMA_VERSION"] = getattr(
                revenue_core, "FORECAST_SCHEMA_VERSION", None
            )
        except Exception:  # noqa: BLE001
            pass

        results = [run_case(spec, engine) for spec in C.CASES]

        cli_evidence: dict[str, Any] = {}
        if e2e:
            cli_evidence = _run_cli_evidence(runtime, scratch, residuals)

        if e2e:
            cli_ok = (
                cli_evidence.get("legal_validate_only", {}).get("returncode") == 0
                and cli_evidence.get("reject_validate_only", {}).get("returncode") == 2
                and "fiscal_year_end" in (cli_evidence.get("reject_validate_only", {}).get("stderr_tail", "")
                                         + cli_evidence.get("reject_validate_only", {}).get("stdout_tail", ""))
                and cli_evidence.get("support_diagnostics", {}).get("returncode") == 0
                and cli_evidence.get("support_output_schema") == "economic-support-diagnostics/1"
            )
            if not cli_ok:
                residuals.append("native CLI evidence incomplete, failed or wrong schema/rejection")
        # Finalize cleanup (restore + SHA re-check) BEFORE writing, so the report
        # carries the real recovery/SHA record, not a pre-cleanup snapshot.
        _finalize_cleanup()

        finished_at = datetime.now(timezone.utc).isoformat()
        wall = time.time() - started_wall
        rep = R.build_report(
            results,
            started_at=started_at,
            finished_at=finished_at,
            wall_seconds=wall,
            cleanup=cleanup,
            residuals=residuals,
            engine_versions=engine_versions,
        )
        if cli_evidence:
            rep["cli_evidence"] = cli_evidence
        R.write_report(rep, str(out_root))
        return rep
    finally:
        # Safety net for the exception path: still restore, never leave scratch.
        if "restored_absent" not in cleanup:
            _finalize_cleanup()


def _run_cli_evidence(runtime: Any, scratch: Path, residuals: list[str]) -> dict[str, Any]:
    """Drive the shipped CLI once on a legal and a rejection sample + support CLI."""
    import subprocess

    repo = bootstrap.repo_root()
    cli = repo / "scripts" / "revenue_forecast.py"
    support_cli = repo / "scripts" / "research_support_diagnostics.py"
    evidence: dict[str, Any] = {}

    def _run(args: list[str]) -> dict[str, Any]:
        try:
            cp = subprocess.run(
                args, capture_output=True, text=True, encoding="utf-8",
                timeout=120, check=False,
            )
            return {
                "command": " ".join(str(a) for a in args),
                "returncode": cp.returncode,
                "stdout_tail": cp.stdout[-2000:],
                "stderr_tail": cp.stderr[-2000:],
            }
        except Exception as exc:  # noqa: BLE001
            residuals.append(f"cli run failed: {exc}")
            return {"command": " ".join(str(a) for a in args), "error": f"{type(exc).__name__}: {exc}"}

    # Legal sample: a unit_sales model_document.
    from test_industry_end_to_end import model_document

    legal = model_document("unit_sales")
    legal_path = scratch / "cli_legal_input.json"
    legal_path.write_text(json.dumps(legal, ensure_ascii=False), encoding="utf-8")
    evidence["legal_validate_only"] = _run(
        [sys.executable, "-B", str(cli), str(legal_path), "--validate-only"]
    )

    # Rejection sample: invalid fiscal_year_end.
    bad = model_document("unit_sales")
    bad["fiscal_year_end"] = "13-40"
    bad_path = scratch / "cli_reject_input.json"
    bad_path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    evidence["reject_validate_only"] = _run(
        [sys.executable, "-B", str(cli), str(bad_path), "--validate-only"]
    )

    # Support diagnostics CLI on a calibrated document.
    from test_research_evidence_roles import calibrated_document

    supp = calibrated_document()
    supp_in = scratch / "cli_support_input.json"
    supp_out = scratch / "cli_support_output.json"
    supp_in.write_text(json.dumps(supp, ensure_ascii=False), encoding="utf-8")
    evidence["support_diagnostics"] = _run(
        [sys.executable, "-B", str(support_cli), "--input", str(supp_in), "--output", str(supp_out)]
    )
    if supp_out.exists():
        try:
            evidence["support_output_schema"] = json.loads(
                supp_out.read_text(encoding="utf-8")
            ).get("schema_version")
        except Exception:  # noqa: BLE001
            pass
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Model generalization matrix runner (offline).")
    parser.add_argument("--owned-root", required=True, help="New absolute dir the tool may scratch under.")
    parser.add_argument("--out-root", required=True, help="New absolute dir to write the report into.")
    parser.add_argument("--e2e", action="store_true", help="Also drive the shipped CLI + support CLI once.")
    args = parser.parse_args(argv)

    out_root = Path(args.out_root).resolve()
    owned_root = Path(args.owned_root).resolve()
    rep = run_matrix(out_root, owned_root, e2e=args.e2e)

    counts = rep["counts"]
    print(json.dumps({"schema": rep["schema"], "counts": counts,
                      "class_status": rep["class_status"]}, ensure_ascii=False))
    # A matrix run is "clean" when nothing failed/errored unexpectedly and every
    # reject landed as REJECT_OK.  NOT_RUN is never treated as a pass.
    clean = rep["status"] == "COMPLETE"
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
