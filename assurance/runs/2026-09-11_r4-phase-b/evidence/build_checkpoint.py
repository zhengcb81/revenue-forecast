"""Regenerate checkpoint.json for the R4 phase-B run directory.

Same rationale as the phase-A generator: A-DR-09 found hand-written checkpoints
drift from the other ledgers, so the produced-file hashes are computed here and
merged with an explicit ledger block. The byte-stability policy of
`../2026-09-11_r4-phase-a/.gitattributes` does NOT apply to this directory: each run
directory carries its own `.gitattributes` (see the one next to this file).

Usage:  python evidence/build_checkpoint.py [--reviewed-commit <sha>|--verify-only]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
REVENUE = Path.home() / "Projects" / "revenue-forecast"
WIKI = Path.home() / "Projects" / "company-wiki"
FILING = Path.home() / "Projects" / "filing-fetch"

EXCLUDE_NAMES = {"checkpoint.json"}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def head(repo: Path) -> str:
    return subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True).stdout.strip()


def dirty(repo: Path) -> int:
    out = subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(repo), "status", "--porcelain"],
        capture_output=True, text=True).stdout
    return len([line for line in out.splitlines() if line.strip()])


def produced_files() -> dict:
    files: dict[str, dict] = {}
    for path in sorted(RUN.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(RUN)
        if rel.name in EXCLUDE_NAMES or any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        files[rel.as_posix()] = {"sha256": sha256(path), "size": path.stat().st_size}
    return files


def verify_blobs(files: dict, source: str = "index") -> dict:
    run_rel = RUN.relative_to(REVENUE).as_posix()
    mismatched = []
    for rel, meta in files.items():
        spec = f":{run_rel}/{rel}" if source == "index" else f"HEAD:{run_rel}/{rel}"
        proc = subprocess.run(
            ["git", "-c", "safe.directory=*", "-C", str(REVENUE), "show", spec],
            capture_output=True)
        if proc.returncode != 0:
            mismatched.append({"path": rel, "reason": f"not in {source}",
                               "detail": proc.stderr.decode(errors="replace").strip()[:120]})
            continue
        if hashlib.sha256(proc.stdout).hexdigest() != meta["sha256"]:
            mismatched.append({"path": rel, "reason": f"{source} digest != recorded digest",
                               "blob_bytes": len(proc.stdout), "recorded_bytes": meta["size"]})
    return {"checked": len(files), "source": source, "blob_mismatches": mismatched,
            "all_match": not mismatched}


LEDGER = {
    "run_id": "2026-09-11_r4-phase-b",
    "phase": "B (position-transparent index and read-only access) - DESIGN ONLY",
    "step": "B01-B07 design delivered; B.DR independent design review submitted",
    "last_completed_step": (
        "B run directory created; b-design.md (B01-B07 design + B08-B10 preconditions), "
        "file-scope.md (8 candidate files with absolute paths, symbols, line anchors and frozen "
        "hashes), test-acceptance-map.md (step -> L/P/O/M mapping and the definition of done), "
        "risk-and-stop-rules.md (H01 and D.SAFE intersections, 10 hard stops), findings.md; "
        "plus phase-A completion runway: a05-corpus-sample-plan.md, a06-baseline-plan.md and "
        "command-manifest-readonly.json"
    ),
    "current_gate": "B.DR (independent design review of this package)",
    "pending_review": [
        {
            "gate": "B.DR",
            "scope": "B phase design package (task_plan, b-design, file-scope, test-acceptance-map, risk-and-stop-rules)",
            "status": "pending",
            "reviewer": "independent subagent (non-author)",
        }
    ],
    "authorization_needed": [
        "OWNER: approve the B DEV work package and file scope (file-scope.md) before any product file is touched - handbook section 2.5",
        "OWNER: confirm the A05 sample list and the read-only command manifest (gate G7 + G4 for behaviour beyond --help)",
        "OWNER/OPERATOR: isolated copy for behavioural probes (gate G8) - see findings F-B00-3 for a two-level proposal",
        "OPERATOR: independent boundary observation and reviewer assignment records (G5/G6)",
    ],
    "gate_status": {
        "B.DR": "submitted (independent design review)",
        "B.VR": "blocked: needs the isolated environment (G8)",
        "B.AR": "blocked: needs G8 + the confirmed real-corpus sample list (G7)",
        "A07_A08": "not started (phase-A VR/AR of the contracts and baseline)",
        "D_SAFE_cross": "not started; B only aligns with it (no delete/write paths touched)",
    },
    "actual_side_effects": (
        "Documentation only. Read-only inspection of repository files (grep, hashes, line "
        "anchors). No CLI of any kind was executed in this run, no data command, no network, no "
        "product/config/DB/task/worker change. Note: pushing this run directory triggers "
        "revenue-forecast's mandatory pre-push gate, whose real-data suite opens the production "
        "catalog READ-ONLY (attributed in ../2026-09-11_r4-phase-a/boundary-audit.md)."
    ),
    "failed_or_unknown": [
        "no B step can be marked implemented: implementation needs the owner-approved DEV work package",
        "B08/B09 need the isolated copy (G8) and the confirmed sample list (G7)",
        "the L01-L12 mechanism-layer baseline (A06) has not been produced yet, so 'B fixed it' cannot be independently verified until A06 exists",
        "A05 has not selected real samples; only the selection rules and the bounded read-only manifest exist",
        "handbook section 3 run structure for this directory is partial: card.json, baseline.json, data-manifest.json, requirements.csv and reviews/ are not created yet",
    ],
    "next_step": (
        "Collect the B.DR verdict, correct the design in place, then (in parallel) start A07/A08 "
        "on the frozen phase-A contracts and prepare the A06 mechanism-layer baseline. Product "
        "changes wait for the owner's approval of file-scope.md."
    ),
    "inputs": {
        "note": ("phase A froze the product inputs at wiki 7d4852f; the phase-A run directory "
                 "records the twelve hashes and the drift of the two planning-ledger commits"),
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewed-commit", default=None)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)

    if args.verify_only:
        existing = json.loads((RUN / "checkpoint.json").read_text(encoding="utf-8"))
        result = verify_blobs(existing["produced_files"], source="head")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["all_match"] else 1

    ledger = dict(LEDGER)
    ledger["inputs"] = {
        "company-wiki": {"head": head(WIKI), "dirty": dirty(WIKI)},
        "revenue-forecast": {"head": head(REVENUE), "dirty": dirty(REVENUE)},
        "filing-fetch": {"head": head(FILING), "dirty": dirty(FILING)},
    }
    ledger["reviewed_commit"] = args.reviewed_commit or "PENDING (stamped in the follow-up commit)"
    ledger["produced_files"] = produced_files()
    ledger["produced_files_verification"] = verify_blobs(ledger["produced_files"], source="index")
    ledger["generated_at_utc"] = datetime.now(UTC).isoformat()
    out = RUN / "checkpoint.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(ledger['produced_files'])} files; "
          f"blob verify all_match={ledger['produced_files_verification']['all_match']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
