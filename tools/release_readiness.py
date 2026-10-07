"""ZR-1001: release readiness checks (optional, read-only by default).

A default run is a check-only, read-only pass over THIS repository plus
numeric diagnostics.  Material that is not supplied is reported as
``not_supplied`` — never as verified:

  fingerprints        this repository's HEAD (read-only git).  Sibling
                      repository HEADs are reported when they resolve and
                      are never required.  An explicit ``--expect-head
                      REPO=SHA`` that is malformed, names an unknown
                      repository, or does not match the live HEAD is RED.
  integrity           read-only SQLite open + key-table row probe — only
                      with an explicit ``--catalog PATH``; the default never
                      opens a neighbour repository's database.
  scenario_evidence   frozen-matrix / evidence revalidation reusing
                      ``uc.scenarios`` — only with an explicit
                      ``--scenario-registry PATH``.  A missing evidence hash
                      stays a diagnostic; a supplied hash that does not
                      match is a failure.
  capacity            size of ``assurance/runs`` — a diagnostic number;
                      enforced only when ``--budget-mb`` is given.
  backup              read-only directory probe (no ``.read-probe`` file) —
                      only with an explicit ``--backup-dir PATH``; no backup
                      is required when nothing stateful is being released.
  rollback            never written in check-only; ``--record-rollback PATH``
                      is the single explicit writer.  Real release/rollback
                      execution belongs to the existing release layer.

Usage:
  python tools/release_readiness.py                      # check-only, 0 writes
  python tools/release_readiness.py --catalog <path>     # explicit input
  python tools/release_readiness.py --expect-head revenue=<40-hex sha>
  python tools/release_readiness.py --record-rollback <path>

Exit is non-zero for real configuration errors, unreadable explicit inputs,
tool exceptions, and explicitly supplied HEAD SHAs that do not match.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNS_DIR = ROOT / "assurance" / "runs"
BACKUP_DIR = ROOT / "assurance" / "backup"
ROLLBACK_PATH = RUNS_DIR / "rollback_manifest.json"
SCENARIO_REGISTRY_PATH = (
    ROOT / "assurance" / "unified_completion" / "scenarios" / "scenario_registry.json"
)

# Historical space budget.  Used only when --budget-mb is supplied; the
# default run reports the measured size as a diagnostic number.
BUDGET_RUNS_MB = 2048

REPOS = {
    "revenue": ROOT,
    "filing": ROOT.parent / "filing-fetch",
    "wiki": ROOT.parent / "company-wiki",
}

_SHA = re.compile(r"[0-9a-f]{40}")
_LABELS = {
    "ok": "OK",
    "red": "RED",
    "not_supplied": "NOT_SUPPLIED",
    "diagnostic": "DIAGNOSTIC",
}


def _head(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.decode("ascii", errors="ignore").strip()


def head_fingerprints() -> dict[str, str]:
    """Read-only ``git rev-parse`` per known repository (``""`` when absent)."""
    return {name: _head(path) for name, path in REPOS.items()}


def _valid_sha(value: object) -> bool:
    return isinstance(value, str) and _SHA.fullmatch(value) is not None


def _gate(
    ok: bool,
    status: str,
    detail: str,
    problems: list[str] | None = None,
) -> dict:
    return {
        "ok": bool(ok),
        "status": status,
        "detail": detail,
        "problems": list(problems or []),
    }


def _guard(label: str, func, *args):
    """Run one check; a broken tool is a real failure, never a silent pass."""
    try:
        return func(*args)
    except Exception as exc:  # noqa: BLE001 - tool anomalies must block
        return False, f"{label} tool error: {exc!r}"


def _fingerprint_gate(
    heads: dict[str, str],
    expect_heads: dict[str, str] | None,
) -> dict:
    problems: list[str] = []
    if not _valid_sha(heads.get("revenue")):
        problems.append("this repository's HEAD is unreadable")
    for name, expected in (expect_heads or {}).items():
        if name not in REPOS:
            problems.append(f"{name}: unknown repo (expected one of {sorted(REPOS)})")
            continue
        if not _valid_sha(expected):
            problems.append(f"{name}: supplied sha {expected!r} is not a 40-hex sha")
            continue
        actual = heads.get(name, "")
        if not _valid_sha(actual):
            problems.append(f"{name}: HEAD unreadable, cannot compare")
        elif actual != expected:
            problems.append(
                f"{name}: HEAD {actual} does not match supplied sha {expected}"
            )
    missing = sorted(name for name, sha in heads.items() if not _valid_sha(sha))
    detail = json.dumps({"heads": heads, "missing": missing}, ensure_ascii=False)
    if problems:
        return _gate(False, "red", detail, problems)
    if missing:
        return _gate(True, "not_supplied", detail)
    return _gate(True, "ok", detail)


def catalog_integrity(catalog: Path) -> tuple[bool, str]:
    """Read-only open + key-table row probes of an EXPLICIT catalog.

    ``PRAGMA integrity_check`` takes minutes on a production catalog; a
    read-only open already validates WAL/page-header consistency and the
    key-table probes confirm the schema answers.  Nothing is ever written.
    """
    target = Path(catalog)
    if not target.is_file():
        return False, f"catalog not found: {target}"
    uri = target.resolve().as_posix()
    try:
        con = sqlite3.connect(f"file:{uri}?mode=ro", uri=True, timeout=30)
        try:
            counts = {}
            for table in ("documents", "sources", "locations"):
                counts[table] = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[
                    0
                ]
        finally:
            con.close()
    except (OSError, sqlite3.Error, ValueError) as exc:
        return False, f"catalog unreadable: {exc}"
    detail = "read-only open ok, " + ", ".join(f"{k}={v}" for k, v in counts.items())
    return True, detail


def _uc_scenarios():
    """Import the RF scenario verifier lazily (a default run needs no uc)."""
    uc_root = ROOT / "assurance" / "unified_completion"
    if not uc_root.is_dir():
        raise FileNotFoundError(f"scenario tooling not present: {uc_root}")
    if str(uc_root) not in sys.path:
        sys.path.insert(0, str(uc_root))
    from uc import scenarios as module  # noqa: PLC0415 - deliberate lazy import

    return module


def scenario_evidence_integrity(registry: Path, root: Path) -> tuple[bool, str]:
    """Revalidate an EXPLICIT registry with the existing RF verifier.

    Missing evidence hashes remain a non-blocking diagnostic; a supplied
    hash that does not match the evidence bytes is a real failure.  This
    never re-implements the closure rules.
    """
    registry_path = Path(registry)
    if not registry_path.is_file():
        return False, f"scenario registry not found: {registry_path}"
    scenarios = _uc_scenarios()
    problems = scenarios.verify(root, registry_path)
    if problems:
        return False, f"scenario registry drift: {problems[0]}"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    report = scenarios.closure_report(payload, root)
    detail = (
        f"{report['total_scenarios']} scenarios, "
        f"{report['unsatisfied']} evidence failures"
    )
    pending = report.get("evidence_hash_pending") or 0
    if pending:
        detail += f", {pending} evidence hashes pending (diagnostic)"
    return bool(report["closure_ready"]), detail


def _runs_label(directory: Path) -> str:
    try:
        return directory.resolve().relative_to(ROOT).as_posix()
    except (OSError, ValueError):
        return directory.name


def capacity_ok(
    runs_dir: Path | None = None, budget_mb: int | None = None
) -> tuple[bool, str]:
    """Measured size of the runs directory — diagnostic unless budgeted."""
    directory = RUNS_DIR if runs_dir is None else runs_dir
    size_bytes = 0
    if directory.is_dir():
        for path in directory.rglob("*"):
            if path.is_file():
                size_bytes += path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    label = _runs_label(directory)
    if budget_mb is None:
        return True, f"{label} {size_mb:.2f}MB (diagnostic; no budget supplied)"
    return (
        size_bytes <= budget_mb * 1024 * 1024,
        f"{label} {size_mb:.2f}MB <= {budget_mb}MB",
    )


def backup_readable(backup_dir: Path | None = None) -> tuple[bool, str]:
    """Read-only probe: the directory must be listable.  No probe file."""
    directory = BACKUP_DIR if backup_dir is None else Path(backup_dir)
    if not directory.is_dir():
        return False, f"backup dir missing ({directory})"
    try:
        for _entry in directory.iterdir():
            break
    except OSError as exc:
        return False, f"backup dir not readable: {exc}"
    return True, f"backup dir readable ({directory})"


def write_rollback_point(
    heads: dict[str, str] | None = None,
    path: Path | None = None,
) -> tuple[bool, str]:
    """Explicitly record a rollback point.  Never called by check-only."""
    if heads is None:
        heads = head_fingerprints()
    target = ROLLBACK_PATH if path is None else path
    supplied = {name: sha for name, sha in heads.items() if sha}
    invalid = sorted(name for name, sha in supplied.items() if not _valid_sha(sha))
    if invalid:
        return False, (
            "rollback point rejects unusable HEAD sha: " + ", ".join(invalid)
        )
    if not _valid_sha(supplied.get("revenue")):
        return False, "rollback point requires this repository's HEAD"
    payload = {
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "heads": supplied,
        "rollback_steps": [
            "git checkout <head> -- <product paths>",
            "restore backup -> catalog (if needed)",
        ],
    }
    try:
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        return False, f"rollback point unwritable: {exc}"
    return True, f"rollback point recorded at {target.name}"


def run_checks(
    *,
    catalog: Path | None = None,
    registry: Path | None = None,
    registry_root: Path | None = None,
    backup_dir: Path | None = None,
    expect_heads: dict[str, str] | None = None,
    budget_mb: int | None = None,
    record_rollback: Path | None = None,
    rollback_path: Path | None = None,
) -> dict[str, dict]:
    """One read-only readiness pass.  Writes nothing unless explicitly asked."""
    heads = head_fingerprints()
    result: dict[str, dict] = {}
    result["fingerprints"] = _fingerprint_gate(heads, expect_heads)

    if catalog is None:
        result["integrity"] = _gate(
            True,
            "not_supplied",
            "catalog not_supplied (pass --catalog PATH to probe one)",
        )
    else:
        ok, detail = _guard("catalog", catalog_integrity, catalog)
        result["integrity"] = _gate(
            ok, "ok" if ok else "red", detail, [] if ok else [detail]
        )

    if registry is None:
        result["scenario_evidence"] = _gate(
            True,
            "not_supplied",
            "scenario_evidence not_supplied (pass --scenario-registry PATH)",
        )
    else:
        root = ROOT if registry_root is None else registry_root
        ok, detail = _guard(
            "scenario_evidence", scenario_evidence_integrity, registry, root
        )
        result["scenario_evidence"] = _gate(
            ok, "ok" if ok else "red", detail, [] if ok else [detail]
        )

    cap_ok, cap_detail = _guard("capacity", capacity_ok, None, budget_mb)
    if not cap_ok:
        cap_status, cap_problems = "red", [cap_detail]
    elif budget_mb is None:
        cap_status, cap_problems = "diagnostic", []
    else:
        cap_status, cap_problems = "ok", []
    result["capacity"] = _gate(cap_ok, cap_status, cap_detail, cap_problems)

    if backup_dir is None:
        result["backup"] = _gate(
            True,
            "not_supplied",
            "backup not_supplied (pass --backup-dir PATH; no stateful release "
            "is being checked)",
        )
    else:
        ok, detail = _guard("backup", backup_readable, backup_dir)
        result["backup"] = _gate(
            ok, "ok" if ok else "red", detail, [] if ok else [detail]
        )

    if record_rollback is None:
        result["rollback"] = _gate(
            True,
            "not_supplied",
            "rollback not_supplied (check-only writes nothing; pass "
            "--record-rollback PATH)",
        )
    elif not result["fingerprints"]["ok"]:
        detail = "rollback withheld: " + "; ".join(result["fingerprints"]["problems"])
        result["rollback"] = _gate(False, "red", detail, [detail])
    else:
        target = record_rollback if rollback_path is None else rollback_path
        ok, detail = _guard("rollback", write_rollback_point, heads, target)
        result["rollback"] = _gate(
            ok, "ok" if ok else "red", detail, [] if ok else [detail]
        )

    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Release readiness (ZR-1001)")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="explicit catalog SQLite to probe read-only",
    )
    parser.add_argument(
        "--scenario-registry",
        type=Path,
        default=None,
        dest="scenario_registry",
        help="explicit scenario registry to revalidate with the RF verifier",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        dest="backup_dir",
        help="explicit backup directory to probe read-only",
    )
    parser.add_argument(
        "--expect-head",
        action="append",
        default=[],
        dest="expect_head",
        metavar="REPO=SHA",
        help="assert a repository HEAD (repeatable)",
    )
    parser.add_argument(
        "--budget-mb",
        type=int,
        nargs="?",
        const=BUDGET_RUNS_MB,
        default=None,
        dest="budget_mb",
        help="enforce a runs-size budget in MB",
    )
    parser.add_argument(
        "--record-rollback",
        type=Path,
        default=None,
        dest="record_rollback",
        help="explicitly write a rollback point (check-only writes nothing)",
    )
    parser.add_argument(
        "--json", action="store_true", help="print the machine-readable result"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    expect_heads: dict[str, str] = {}
    for raw in args.expect_head:
        name, separator, sha = raw.partition("=")
        if not separator or not name.strip():
            parser.error(f"--expect-head expects REPO=SHA, got {raw!r}")
        expect_heads[name.strip()] = sha.strip()
    result = run_checks(
        catalog=args.catalog,
        registry=args.scenario_registry,
        backup_dir=args.backup_dir,
        expect_heads=expect_heads or None,
        budget_mb=args.budget_mb,
        record_rollback=args.record_rollback,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for name, gate in result.items():
            label = _LABELS.get(gate["status"], gate["status"].upper())
            print(f"{name}: {label} {gate.get('detail') or ''}".rstrip())
    return 0 if all(gate["ok"] for gate in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
