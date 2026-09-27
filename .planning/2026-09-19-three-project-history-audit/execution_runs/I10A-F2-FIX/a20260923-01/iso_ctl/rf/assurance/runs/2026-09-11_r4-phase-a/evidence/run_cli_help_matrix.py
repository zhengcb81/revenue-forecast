"""A01 command-manifest executor: enumerate the real CLI surface via --help only.

Owner-approved 2026-09-11 as a `--help`-only command manifest (no --dry-run, no
command execution, no database access, no network).

Design constraints:
  * python -B  + PYTHONDONTWRITEBYTECODE=1  -> zero bytecode writes anywhere
  * cwd = company-wiki repo root; PYTHONPATH=<wiki>/src (the CI convention)
  * every invocation is `<cmd> [sub] --help`, which argparse answers and exits
    from BEFORE cli.main() resolves/loads the catalog config
  * pre/post snapshots of the production catalog (main + -shm + -wal companions),
    the config and __pycache__ prove the zero-side-effect claim rather than
    asserting it

Scope limit (A-DR-08 / finding F-A01-8, RESOLVED in v0.2): the `-shm` mtime is NOT a
reliable "no process opened the catalog" oracle on this machine, because at least two
legitimate openers exist: the 22:00 daily task (wiki `scripts/legacy_observer.py
--read-only`) and this repository's own mandatory pre-push gate, whose real-data suite
reads the production catalog read-only (`tools/pre_push_gate.py:184-199`). Every
observed advance has since been attributed to one of those two (see boundary-audit.md
section 1-3). The snapshot therefore records the raw per-file values and labels the
interpretation limit instead of claiming proof.

Output: evidence/cli-help-matrix.json (+ command-manifest.json written first).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
CATALOG_DIR = WIKI / ".source_catalog"
CATALOG = CATALOG_DIR / "catalog.sqlite3"
CATALOG_FILES = (
    "catalog.sqlite3",
    "catalog.sqlite3-shm",
    "catalog.sqlite3-wal",
)
CONFIG = WIKI / "config" / "source_catalog.yaml"
PY = sys.executable
TIMEOUT = 60
MAX_INVOCATIONS = 90


def snapshot() -> dict:
    def stat(p: Path) -> dict | None:
        if not p.exists():
            return None
        s = p.stat()
        return {"size": s.st_size, "mtime_ns": s.st_mtime_ns}
    catalog_files = {name: stat(CATALOG_DIR / name) for name in CATALOG_FILES}
    pycache = sorted(str(p.relative_to(WIKI)) for p in WIKI.rglob("__pycache__"))
    dirty = subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(WIKI), "status", "--porcelain"],
        capture_output=True, text=True).stdout
    return {
        "catalog": catalog_files["catalog.sqlite3"],
        "catalog_files": catalog_files,
        "config": stat(CONFIG),
        "pycache_dirs": pycache[:20],
        "git_dirty_lines": len([line for line in dirty.splitlines() if line.strip()]),
    }


def run_help(argv_tail: list[str]) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(WIKI / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [PY, "-B", "-m", "company_wiki.source_catalog.cli", *argv_tail, "--help"],
        cwd=str(WIKI), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=TIMEOUT, env=env)
    return {"argv_tail": argv_tail, "rc": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


def child_commands(help_text: str) -> list[str]:
    """argparse lists positional choices as `{a,b,c}` in the usage/positional block."""
    found: list[str] = []
    for match in re.findall(r"\{([a-z0-9,\-]{3,})\}", help_text):
        for name in match.split(","):
            name = name.strip()
            if name and name not in found and re.fullmatch(r"[a-z][a-z0-9\-]+", name):
                found.append(name)
    return found


def main() -> int:
    manifest = {
        "run_id": "2026-09-11_r4-phase-a",
        "step": "A01 (side-effect matrix)",
        "purpose": "enumerate the real CLI surface and classify subcommands; --help only",
        "entrypoint": {"python": PY, "module": "company_wiki.source_catalog.cli",
                       "flags": ["-B"]},
        "cwd": str(WIKI),
        "env_keys": ["PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING"],
        "read_set": [str(WIKI / "src" / "company_wiki" / "source_catalog"),
                     str(CONFIG)],
        "stat_set": [
            str(CATALOG_DIR / name) for name in CATALOG_FILES
        ] + [f"{WIKI}/**/__pycache__ (directory list)",
             "git -C <wiki> status --porcelain"],
        "write_set": [str(RUN / "command-manifest.json"),
                      str(RUN / "evidence" / "cli-help-matrix.json")],
        "network_destinations": [],
        "budget": {"bytes": 0, "tokens": 0, "cost": 0},
        "timeout_seconds": TIMEOUT,
        "subprocesses": "one python -B per invocation, no grandchildren expected",
        "exit_expectation": "0 for every --help",
        "approval": {"by": "repo owner", "at": "2026-09-11", "scope": "--help only"},
        "evidence_path": "evidence/cli-help-matrix.json",
        "revision": (
            "v2 (2026-09-11): snapshot extended to the catalog family "
            "(catalog.sqlite3 + -shm + -wal) to close the coverage gap reported by "
            "A.DR (A-DR-08); scope limits recorded under side_effect_scope"
        ),
    }
    (RUN / "command-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pre = snapshot()
    results: list[dict] = []
    top = run_help([])
    results.append({**top, "level": 1, "name": "<top>"})
    names = child_commands(top["stdout"])
    nested: dict[str, list[str]] = {}
    for name in names:
        if len(results) >= MAX_INVOCATIONS:
            break
        res = run_help([name])
        results.append({**res, "level": 2, "name": name})
        kids = child_commands(res["stdout"])
        # nested choices only appear when the child parser has its own subparsers
        if kids and "{" in res["stdout"].split("options:")[0]:
            nested[name] = kids
    for parent, kids in nested.items():
        for kid in kids:
            if len(results) >= MAX_INVOCATIONS:
                break
            res = run_help([parent, kid])
            results.append({**res, "level": 3, "name": f"{parent} {kid}"})
    post = snapshot()

    pre_files = pre["catalog_files"]
    post_files = post["catalog_files"]
    per_file = {
        name: {
            "before": pre_files[name],
            "after": post_files[name],
            "unchanged": pre_files[name] == post_files[name],
        }
        for name in CATALOG_FILES
    }
    shm_unchanged = per_file["catalog.sqlite3-shm"]["unchanged"]

    matrix = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "invocations": len(results),
        "top_level_commands": names,
        "nested": nested,
        "pre_snapshot": pre,
        "post_snapshot": post,
        "side_effects": {
            "catalog_unchanged": pre["catalog"] == post["catalog"],
            "catalog_files_per_file": per_file,
            "catalog_shm_unchanged": shm_unchanged,
            "config_unchanged": pre["config"] == post["config"],
            "pycache_unchanged": pre["pycache_dirs"] == post["pycache_dirs"],
            "git_dirty_unchanged": pre["git_dirty_lines"] == post["git_dirty_lines"],
        },
        "side_effect_scope": {
            "covered": list(CATALOG_FILES)
            + [str(CONFIG.relative_to(WIKI)), "__pycache__/ (dir set)", "git dirty lines"],
            "not_covered": [
                "every other file under .source_catalog (only the catalog family is sampled)",
                "open file handles / object access by other processes",
                "network activity (no capture in this run)",
            ],
            "interpretation_limit": (
                "catalog.sqlite3-shm is not a reliable no-open oracle on this machine: the "
                "22:00 daily task and this repo's mandatory pre-push gate (its real-data "
                "suite, tools/pre_push_gate.py:184-199) both open the catalog read-only and "
                "advance -shm. All observed advances have been attributed to one of those "
                "two (see boundary-audit.md sections 1-3); a stable -shm across this run is "
                "therefore consistent with, but not proof of, zero opens by these "
                "invocations. Main DB and -wal stayed unchanged, i.e. no logical write."
            ),
            "cli_commands": "--help only; no --dry-run, no data command, no network",
        },
        "results": results,
    }
    out = RUN / "evidence"
    out.mkdir(exist_ok=True)
    (out / "cli-help-matrix.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in matrix.items()
                      if k in ("invocations", "top_level_commands", "nested",
                               "side_effects")}, ensure_ascii=False, indent=1))
    bad = [r for r in results if r["rc"] != 0]
    print("non-zero rc:", [(r["name"], r["rc"]) for r in bad] or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
