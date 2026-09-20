"""I-14-A final integrity witness: git heads/porcelain and the anchors this card used.

Read-only. Never opens the production catalog; it only records its (size, mtime,
-wal/-shm) identity so a reviewer can see the card did not touch it.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
ATT = RF / ".planning" / "2026-09-19-three-project-history-audit" / "execution_runs" / "I-14-A" / "a20260919-01"

ANCHORS = [
    ("RF/tools/slo_probe.py", RF / "tools" / "slo_probe.py"),
    ("RF/tools/tests/test_slo_probe.py", RF / "tools" / "tests" / "test_slo_probe.py"),
    ("RF/tools/release_readiness.py", RF / "tools" / "release_readiness.py"),
    ("CW/src/company_wiki/source_catalog/cli.py",
     CW / "src" / "company_wiki" / "source_catalog" / "cli.py"),
    ("CW/config/source_catalog.yaml", CW / "config" / "source_catalog.yaml"),
    ("PLAN/audit_report.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "audit_report.md"),
    ("PLAN/implementation_plan.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "implementation_plan.md"),
    ("PLAN/execution_v2/card_I-14-A.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "execution_v2"
     / "card_I-14-A.md"),
]

ISO_ANCHORS = [
    "iso/tool_prod/slo_probe.py",
    "iso/tool_prod/test_slo_probe.py",
    "iso/slo_probe_patched.py",
    "iso/fixtures/exit7_success_stdout.py",
    "iso/fixtures/exit0_business_failure.py",
    "iso/fixtures/alive_allocate_then_exit.py",
    "iso/fixtures/instant_exit_no_sample.py",
    "harness/fixture_spec.py",
    "harness/run_probe_cases.py",
    "harness/run_bundle_control.py",
    "harness/tests/test_i14a_failure_branches.py",
    "changes.diff",
    "oracle.md",
    "commands.json",
    "binding.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return proc.stdout.strip()


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ATT / "after"
    catalog = CW / ".source_catalog" / "catalog.sqlite3"
    item = catalog.stat()
    payload = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "repos": {
            name: {"path": str(path), "head": git(path, "rev-parse", "HEAD"),
                   "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD"),
                   "porcelain": git(path, "status", "--porcelain").splitlines()}
            for name, path in (("revenue-forecast", RF), ("company-wiki", CW),
                               ("filing-fetch", FF))
        },
        "porcelain_product_only": {
            "revenue-forecast": git(RF, "status", "--porcelain", "--", "tools").splitlines(),
            "company-wiki": git(CW, "status", "--porcelain", "--", "src", "config",
                                "scripts", "tests").splitlines(),
            "filing-fetch": git(FF, "status", "--porcelain", "--", "scripts", "src",
                                "tests").splitlines(),
        },
        "slo_probe_git": {
            "blob_at_head": git(RF, "rev-parse", "HEAD:tools/slo_probe.py"),
            "blob_of_worktree": git(RF, "hash-object", "tools/slo_probe.py"),
        },
        "production_catalog_identity": {
            "path": str(catalog),
            "bytes": item.st_size,
            "mtime_iso": datetime.fromtimestamp(item.st_mtime).isoformat(),
            "wal_present": (catalog.parent / (catalog.name + "-wal")).exists(),
            "shm_present": (catalog.parent / (catalog.name + "-shm")).exists(),
            "opened_by_this_card": False,
            "note": "I-14-A never opened the production catalog; this is an identity witness only.",
        },
        "anchors_sha256": {name: sha256_file(path) for name, path in ANCHORS},
        "anchor_sizes": {name: path.stat().st_size for name, path in ANCHORS},
        "attempt_artifacts_sha256": {
            rel: (sha256_file(ATT / rel) if (ATT / rel).is_file() else None)
            for rel in ISO_ANCHORS
        },
        "env": {"python": sys.executable, "prefix": sys.prefix,
                "is_iso_venv": str(ATT / "iso" / "venv") in sys.prefix},
    }
    write = out_dir / "snapshot.json"
    write.parent.mkdir(parents=True, exist_ok=True)
    write.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(json.dumps({
        "ok": True, "wrote": str(write),
        "rf_head": payload["repos"]["revenue-forecast"]["head"],
        "cw_head": payload["repos"]["company-wiki"]["head"],
        "ff_head": payload["repos"]["filing-fetch"]["head"],
        "tools_porcelain": payload["porcelain_product_only"]["revenue-forecast"],
        "cw_product_porcelain": payload["porcelain_product_only"]["company-wiki"],
        "slo_probe_unchanged": payload["slo_probe_git"]["blob_at_head"]
        == payload["slo_probe_git"]["blob_of_worktree"],
        "is_iso_venv": payload["env"]["is_iso_venv"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
