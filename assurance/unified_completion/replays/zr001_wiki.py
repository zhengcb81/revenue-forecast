"""ZR-001 replay: company-wiki CatalogStore write-on-read (hermetic).

W1 — constructing ``CatalogStore`` for a read path initializes a writable
database: it mkdirs the parent, switches WAL, executes the full DDL,
migrations and seed commit, even when the target database does not exist
yet.  On an OS-read-only database the same construction fails with
``attempt to write a readonly database`` — a reuse-only resolve therefore
cannot run against a strictly read-only catalog.

Usage:  python -B assurance/unified_completion/replays/zr001_wiki.py
        [--wiki-python PATH]   (default: the wiki repo's .venv python,
                                falling back to the system interpreter)

Emits evidence files into ``replays/evidence/``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WIKI_ROOT = Path(r"C:\Users\郑曾波\Projects\company-wiki")
EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"

# The probe runs inside the wiki interpreter; this bootstrap script stays
# dependency-free and delegates to it.
_PROBE = r"""
import json, os, stat, sys, tempfile
from pathlib import Path

sys.path.insert(0, r"{wiki_src}")

from company_wiki.source_catalog.store import CatalogStore

results = {{}}

# W1a: nonexistent DB -> CatalogStore creates a full writable catalog.
with tempfile.TemporaryDirectory(prefix="zr001_wiki_") as tmp:
    db = Path(tmp) / "nested" / "dirs" / "catalog.sqlite3"
    store = CatalogStore(db)
    del store
    results["w1a"] = {{
        "db_created": db.exists(),
        "db_size_bytes": db.stat().st_size if db.exists() else 0,
        "wal_created": Path(str(db) + "-wal").exists(),
        "shm_created": Path(str(db) + "-shm").exists(),
        "parent_dirs_created": db.parent.exists(),
        "journal_mode": None,
    }}
    import sqlite3
    conn = sqlite3.connect(db)
    results["w1a"]["journal_mode"] = conn.execute("PRAGMA journal_mode").fetchone()[0]
    results["w1a"]["table_count"] = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
    ).fetchone()[0]
    conn.close()

# W1b: same construction against an OS-read-only file fails closed with a
# write attempt instead of degrading to a read-only reader.
with tempfile.TemporaryDirectory(prefix="zr001_wiki_") as tmp:
    db = Path(tmp) / "ro" / "catalog.sqlite3"
    seed = CatalogStore(db)
    del seed
    os.chmod(db, stat.S_IREAD)
    try:
        CatalogStore(db)
        results["w1b"] = {{"constructed": True, "error": None}}
    except Exception as exc:
        results["w1b"] = {{
            "constructed": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }}
    finally:
        os.chmod(db, stat.S_IWRITE)

print(json.dumps(results, ensure_ascii=False))
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-python", type=Path, default=None)
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=EVIDENCE_DIR,
        help="write evidence here (default: the sealed evidence dir)",
    )
    args = parser.parse_args()
    venv_python = WIKI_ROOT / ".venv" / "Scripts" / "python.exe"
    candidates = []
    if args.wiki_python is not None:
        candidates.append(args.wiki_python)
    elif venv_python.exists():
        candidates.append(venv_python)
    candidates.append(Path(sys.executable))

    last_error: str | None = None
    for interpreter in candidates:
        completed = subprocess.run(
            [str(interpreter), "-B", "-c", _PROBE.format(wiki_src=WIKI_ROOT / "src")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=300,
        )
        if completed.returncode == 0:
            payload = json.loads(completed.stdout)
            payload["interpreter"] = str(interpreter)
            payload["wiki_head"] = subprocess.run(
                ["git", "-C", str(WIKI_ROOT), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            payload["product_code_hashes"] = {
                "src/company_wiki/source_catalog/store.py": hashlib.sha256(
                    (
                        WIKI_ROOT / "src/company_wiki/source_catalog/store.py"
                    ).read_bytes()
                ).hexdigest(),
            }
            payload["observed_at_utc"] = utc_now()
            args.evidence_dir.mkdir(parents=True, exist_ok=True)
            path = args.evidence_dir / "w1_catalog_read_path_writes.json"
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            print("w1_catalog_read_path_writes.json")
            return 0
        last_error = completed.stderr.strip()[-800:]
    print(f"all interpreters failed; last error: {last_error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
