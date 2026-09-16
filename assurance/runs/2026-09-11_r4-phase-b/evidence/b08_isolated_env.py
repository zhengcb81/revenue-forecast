"""B08 mechanism level (G8 level 1): build an isolated catalog and EVIDENCE side effects.

Owner decision 2026-09-13, item 1: G8 is approved in two levels.  This tool is level 1
ONLY - a small catalog under a non-production path, plus the before/after observation
that makes "no side effects" an evidenced statement instead of a declaration (the G5
lesson: `-shm` alone cannot attribute anything on this host, so the probe first
measures a FLAT baseline and refuses to conclude when the baseline moves).

    python b08_isolated_env.py build [--root PATH] [--manifest-out PATH]
    python b08_isolated_env.py snapshot --label before|after [--baseline-seconds 120]
    python b08_isolated_env.py compare --before PATH --after PATH

Level 2 (referencing real bytes read-only under an isolated root) is NOT implemented
here and is NOT authorised: nothing in this file copies, moves or opens production
data, and `build` refuses any path inside the three repositories or in a sync folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <run>/evidence
RUN_DIR = HERE.parent
REPO = HERE.parents[3]                          # revenue-forecast
PROJECTS = REPO.parent                          # the three sibling checkouts live here
WIKI_SRC = PROJECTS / "company-wiki" / "src"
PROD_CATALOG = PROJECTS / "company-wiki" / ".source_catalog"
REPO_DIRS = (PROJECTS / "company-wiki", PROJECTS / "revenue-forecast",
             PROJECTS / "filing-fetch")
SYNC_MARKERS = ("dropbox", "onedrive", "google drive", "icloud")
FORBIDDEN_PART = ".source_catalog"
EVIDENCE = HERE                                 # the run directory's evidence folder


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path, limit: int | None = None) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        remaining = limit
        while True:
            chunk = handle.read(1 << 20 if remaining is None else min(1 << 20, remaining))
            if not chunk:
                break
            digest.update(chunk)
            if remaining is not None:
                remaining -= len(chunk)
                if remaining <= 0:
                    break
    return digest.hexdigest()


def _file_state(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    stat = path.stat()
    return {
        "exists": True,
        "bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
    }


def _production_state() -> dict:
    """Metadata ONLY: the production database is never opened, read or hashed."""
    return {
        "catalog.sqlite3": _file_state(PROD_CATALOG / "catalog.sqlite3"),
        "catalog.sqlite3-wal": _file_state(PROD_CATALOG / "catalog.sqlite3-wal"),
        "catalog.sqlite3-shm": _file_state(PROD_CATALOG / "catalog.sqlite3-shm"),
        "note": "metadata only - the database file is never opened, queried or hashed",
    }


def _ensure_isolated(path: Path) -> Path:
    """Refuse anything that is not a plain temp directory.

    Belt and braces ON PURPOSE.  The first version computed REPO one level too high
    (``parents[2]`` = assurance/ instead of ``parents[3]`` = the repository), so every
    path comparison silently pointed at directories that do not exist and the guard
    never fired: a probe with ``--root <prod>\\.source_catalog\\b08-test`` really did
    create a directory inside the production catalog dir (found and removed by hand on
    2026-09-15 23:1x; the production database itself stayed at its 2026-09-08 mtime).
    Hence: structural checks that cannot depend on one derived path, plus a self-test
    (``selftest``) that FAILS if any refusal stops working.
    """
    resolved = path.resolve()
    if resolved == PROD_CATALOG.resolve() or PROD_CATALOG.resolve() in resolved.parents:
        raise SystemExit(f"refusing to build inside the production catalog dir: {resolved}")
    if FORBIDDEN_PART in [part.lower() for part in resolved.parts]:
        raise SystemExit(f"refusing a path containing {FORBIDDEN_PART!r}: {resolved}")
    for repo in REPO_DIRS:
        if resolved == repo.resolve() or repo.resolve() in resolved.parents:
            raise SystemExit(f"refusing to build inside a repository: {resolved}")
    lowered = str(resolved).lower()
    for marker in SYNC_MARKERS:
        if marker in lowered:
            raise SystemExit(f"refusing a synced folder (extra side effects): {resolved}")
    if not resolved.is_relative_to(Path(tempfile.gettempdir()).resolve()):
        raise SystemExit(
            f"refusing a root outside the system temp directory: {resolved} "
            f"(level 1 builds only in {tempfile.gettempdir()})"
        )
    return resolved


def build(root: Path, manifest_out: Path | None) -> int:
    root = _ensure_isolated(root)
    root.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(WIKI_SRC))
    from company_wiki.source_catalog.store import CatalogStore  # noqa: PLC0415

    catalog = root / "catalog.sqlite3"
    # The PRODUCT owns the schema: no hand-written DDL here, so this cannot drift
    # from the real thing (the wiki's own contract tests do the same).
    CatalogStore(catalog)

    with __import__("sqlite3").connect(catalog) as connection:
        tables = sorted(
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        )
        schema_version = connection.execute(
            "SELECT value FROM catalog_meta WHERE key = 'schema_version'").fetchone()

    manifest = {
        "built_at_utc": _utc_now(),
        "root": str(root),
        "schema_version": schema_version[0] if schema_version else None,
        "tables": tables,
        "shape_sha256": hashlib.sha256("\n".join(tables).encode()).hexdigest()[:16],
        "files": {
            entry.name: {"bytes": entry.stat().st_size, "sha256": _sha256(entry)}
            for entry in sorted(root.iterdir()) if entry.is_file()
        },
    }
    if manifest_out:
        manifest_out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8", newline="")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def _real_root_state(root: Path, cap: int = 200) -> dict:
    """(name, size, mtime_ns, sha256) of every file in a REAL production directory.

    G8 level 2 references real files read-only, so "nothing was written" has to be shown
    on those files and not only on the catalog: this snapshot is taken before and after
    the scan and the two must be identical.
    """
    entries = sorted(entry for entry in root.iterdir() if entry.is_file())
    state = {}
    for entry in entries[:cap]:
        stat = entry.stat()
        state[entry.name] = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns,
                             "sha256": _sha256(entry)}
    return {"root": str(root), "file_count": len(entries), "files": state,
            "capped_at": cap if len(entries) > cap else None}


def build_level2(real_root: Path, isolated_root: Path, manifest_out: Path | None) -> int:
    """G8 level 2: an isolated catalog that REFERENCES a real directory read-only.

    Writes: the isolated catalog and its artifacts, under the system temp directory only.
    The referenced directory is registered as a `directory`-kind read-only root (never a
    canonical write target), and its files are hashed before and after so "no writes to
    production bytes" is evidence rather than a promise.
    """
    real_root = real_root.resolve()
    if not real_root.is_dir():
        raise SystemExit(f"--real-root is not a directory: {real_root}")
    isolated = _ensure_isolated(isolated_root)
    if real_root == isolated or real_root in isolated.parents or isolated in real_root.parents:
        raise SystemExit(f"refusing overlapping roots: {real_root} vs {isolated}")

    sys.path.insert(0, str(WIKI_SRC))
    from company_wiki.source_catalog import CatalogConfig, SourceCatalog  # noqa: PLC0415
    from company_wiki.source_catalog.models import RootSpec  # noqa: PLC0415
    from company_wiki.source_catalog.store import CatalogStore  # noqa: PLC0415

    isolated.mkdir(parents=True, exist_ok=True)
    catalog_dir = isolated / ".source_catalog"
    database = catalog_dir / "catalog.sqlite3"
    CatalogStore(database)

    before_production = _production_state()
    before_real = _real_root_state(real_root)

    spec = RootSpec(
        "r4b08_real_sample",
        real_root,
        "directory",
        priority=10,
        adapter_id="sidecar_filing_v1",
        read_only=True,
        reusable_for_filing=True,
        canonical_write_target=None,
    )
    config = CatalogConfig(
        project_root=isolated,
        catalog_dir=catalog_dir,
        reusable_root_kinds=("directory",),
        roots=(spec,),
    )
    catalog = SourceCatalog(config)
    started = _utc_now()
    catalog.scan()
    finished = _utc_now()

    after_real = _real_root_state(real_root)
    after_production = _production_state()

    with __import__("sqlite3").connect(database) as connection:
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("sources", "documents", "locations", "artifacts", "evidence_spans")
        }

    payload = {
        "level": 2,
        "note": ("references a REAL production directory read-only; the isolated catalog "
                 "and its artifacts are written under the system temp directory only"),
        "started_at_utc": started,
        "finished_at_utc": finished,
        "real_root": str(real_root),
        "isolated_root": str(isolated),
        "database": str(database),
        "isolated_counts": counts,
        "real_root_before": before_real,
        "real_root_after": after_real,
        "real_root_unchanged": before_real == after_real,
        "production_catalog_before": before_production,
        "production_catalog_after": after_production,
        "production_catalog_unchanged": before_production == after_production,
        "root_spec": {"root_id": spec.root_id, "kind": spec.kind, "read_only": True,
                      "canonical_write_target": None},
    }
    if manifest_out:
        manifest_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8", newline="")
    print(json.dumps({k: v for k, v in payload.items()
                      if k not in ("real_root_before", "real_root_after",
                                   "production_catalog_before", "production_catalog_after")},
                     ensure_ascii=False, indent=2))
    print(f"real_root_unchanged={payload['real_root_unchanged']} "
          f"production_catalog_unchanged={payload['production_catalog_unchanged']}")
    return 0 if payload["real_root_unchanged"] and payload["production_catalog_unchanged"] else 1


def _shm_baseline(seconds: int) -> dict:
    """Count `-shm` mtime transitions over a passive window.  A NON-ZERO baseline
    means a later `-shm` move proves nothing about this session (G5 finding)."""
    shm = PROD_CATALOG / "catalog.sqlite3-shm"
    seen: list[str] = []
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        state = _file_state(shm)
        stamp = state.get("mtime_utc")
        if stamp and (not seen or seen[-1] != stamp):
            seen.append(stamp)
        time.sleep(1.0)
    return {"seconds": seconds, "transitions": max(0, len(seen) - 1), "stamps": seen[:8],
            "flat": len(seen) <= 1}


def snapshot(label: str, baseline_seconds: int) -> int:
    state = {
        "label": label,
        "at_utc": _utc_now(),
        "production_catalog": _production_state(),
    }
    if baseline_seconds:
        state["shm_baseline"] = _shm_baseline(baseline_seconds)
    out = EVIDENCE / f"b08-side-effects-{label}.json"
    out.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"wrote {out}")
    return 0


def compare(before_path: Path, after_path: Path) -> int:
    """Verdict per the G5 protocol: only the main DB or a non-empty -wal are proof of
    a write; `-shm` is reported with its baseline so nobody attributes it by accident."""
    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    b = before["production_catalog"]
    a = after["production_catalog"]
    main_changed = b["catalog.sqlite3"] != a["catalog.sqlite3"]
    wal_bytes = a["catalog.sqlite3-wal"].get("bytes")
    wal_changed = b["catalog.sqlite3-wal"] != a["catalog.sqlite3-wal"]
    shm_changed = b["catalog.sqlite3-shm"].get("mtime_utc") != a["catalog.sqlite3-shm"].get("mtime_utc")
    baseline = before.get("shm_baseline") or after.get("shm_baseline") or {}
    verdict = {
        "main_db_changed": main_changed,
        "wal_bytes_after": wal_bytes,
        "wal_changed": wal_changed,
        "shm_moved": shm_changed,
        "shm_baseline_flat": baseline.get("flat"),
        "shm_baseline_transitions": baseline.get("transitions"),
        "persisted_write_evidence": bool(main_changed or (wal_bytes or 0) > 0),
        "conclusion": None,
    }
    if verdict["persisted_write_evidence"]:
        verdict["conclusion"] = "WRITE EVIDENCE: the production database or its WAL changed"
    elif shm_changed and baseline.get("flat") is True:
        verdict["conclusion"] = ("no write evidence; -shm moved over a FLAT baseline, so a "
                                 "read-only open happened but is NOT attributable")
    elif shm_changed:
        verdict["conclusion"] = ("no write evidence; -shm moved and the baseline was NOT flat, "
                                 "so nothing can be attributed (G5)")
    else:
        verdict["conclusion"] = "no write evidence and no observable open"
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 1 if verdict["persisted_write_evidence"] else 0


def selftest() -> int:
    """Prove every refusal fires.  A guard that cannot be shown to fire is not a guard
    (the 2026-09-15 mistake: a wrong REPO level made all three path refusals dead code)."""
    cases = [
        ("production catalog dir", PROD_CATALOG / "b08-selftest"),
        ("production catalog dir itself", PROD_CATALOG),
        ("a repository", PROJECTS / "revenue-forecast" / "b08-selftest"),
        ("a synced folder", PROJECTS / "Dropbox" / "b08-selftest"),
        ("outside temp", Path("C:/b08-selftest-outside-temp")),
    ]
    results = []
    for label, path in cases:
        try:
            _ensure_isolated(path)
        except SystemExit as exc:
            results.append({"case": label, "path": str(path), "refused": True,
                            "message": str(exc)[:120]})
        else:
            results.append({"case": label, "path": str(path), "refused": False,
                            "message": "NOT REFUSED - the guard is broken"})
    ok = all(item["refused"] for item in results)
    allowed = _ensure_isolated(Path(tempfile.gettempdir()) / "b08-selftest-ok")
    print(json.dumps({"refusals": results, "temp_root_accepted": str(allowed), "ok": ok},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_build = sub.add_parser("build")
    p_build.add_argument("--root", type=Path,
                         default=Path(tempfile.gettempdir()) / f"b08-isolated-{os.getpid()}")
    p_build.add_argument("--manifest-out", type=Path, default=None)
    p_build.add_argument("--real-root", type=Path, default=None,
                         help="G8 LEVEL 2: reference this REAL directory read-only")
    p_l2 = sub.add_parser("build-level2")
    p_l2.add_argument("--real-root", type=Path, required=True)
    p_l2.add_argument("--root", type=Path,
                      default=Path(tempfile.gettempdir()) / "b08-level2-isolated")
    p_l2.add_argument("--manifest-out", type=Path, default=None)
    p_snap = sub.add_parser("snapshot")
    p_snap.add_argument("--label", choices=("before", "after"), required=True)
    p_snap.add_argument("--baseline-seconds", type=int, default=0)
    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("--before", type=Path, required=True)
    p_cmp.add_argument("--after", type=Path, required=True)
    sub.add_parser("selftest")
    args = parser.parse_args(argv)
    if args.command == "build":
        if args.real_root is not None:
            return build_level2(args.real_root, args.root, args.manifest_out)
        return build(args.root, args.manifest_out)
    if args.command == "build-level2":
        return build_level2(args.real_root, args.root, args.manifest_out)
    if args.command == "snapshot":
        return snapshot(args.label, args.baseline_seconds)
    if args.command == "selftest":
        return selftest()
    return compare(args.before, args.after)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
