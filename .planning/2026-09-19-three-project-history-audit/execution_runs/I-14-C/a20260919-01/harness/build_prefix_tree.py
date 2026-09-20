"""I-14-C: assemble the PRE-FIX product tree for the controlled before-pass.

Layout produced:  <snap>/src/company_wiki/...   (run the probe with --src <snap>/src)

Steps, idempotent and loud on failure:
  1. wipe <snap>, copy the live package tree (<cw>/src) so every module except the
     three edited ones is byte-identical to the tree the after-pass uses;
  2. reconstruct the three PRE-IMAGE modules from changes.diff's '-' side into a
     staging root and copy exactly those three over the copy;
  3. verify each written module differs from live AND the reconstruction is
     hash-verified against the recorded pre-edit sha256;
  4. drop __pycache__ so no stale bytecode can satisfy an import.

    python build_prefix_tree.py --cw <company-wiki> --snap <attempt>/before/prefix_src \
        --diff <attempt>/changes.diff --python <iso venv python>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVERSE = HERE / "reverse_card_diff.py"
MODULES = (
    "src/company_wiki/source_catalog/worker.py",
    "src/company_wiki/source_catalog/observability.py",
    "src/company_wiki/source_catalog/cli.py",
)


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cw", required=True)
    parser.add_argument("--snap", required=True)
    parser.add_argument("--diff", required=True)
    parser.add_argument("--python", required=True,
                        help="bound iso venv interpreter (never the global Miniconda python)")
    args = parser.parse_args(argv)

    cw = Path(args.cw).resolve()
    snap = Path(args.snap).resolve()
    staging = snap.parent / (snap.name + "_stage")
    live_src = cw / "src"
    prefix_pkg = snap / "src" / "company_wiki"
    stage_pkg = staging / "src" / "company_wiki"

    for path in (snap, staging):
        if path.exists():
            shutil.rmtree(path)
    snap.mkdir(parents=True)

    report: dict = {
        "cw": str(cw), "snap": str(snap), "prefix_import_root": str(snap / "src"),
        "modules": [], "all_ok": True,
    }
    shutil.copytree(live_src, snap / "src")

    proc = subprocess.run(
        [args.python, "-X", "utf8", "-B", str(REVERSE), "--diff", args.diff,
         "--cw", str(cw), "--out", str(staging)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    report["reverse_argv"] = [args.python, "-X", "utf8", "-B", str(REVERSE),
                              "--diff", args.diff, "--cw", str(cw), "--out", str(staging)]
    report["reverse_returncode"] = proc.returncode
    report["reverse_stdout"] = proc.stdout.decode("utf-8", "replace")
    report["reverse_stderr"] = proc.stderr.decode("utf-8", "replace")
    if proc.returncode != 0:
        report["all_ok"] = False

    for rel in MODULES:
        # rel = src/company_wiki/source_catalog/x.py ; the package roots already end
        # with .../company_wiki, so only the part below it is appended.
        rel_inside = rel[len("src/company_wiki/"):]         # source_catalog/x.py
        staged = stage_pkg / rel_inside
        target = prefix_pkg / rel_inside
        live = live_src / "company_wiki" / rel_inside
        entry = {
            "path": rel,
            "staged_path": str(staged),
            "target_path": str(target),
            "staged_exists": staged.is_file(),
        }
        if staged.is_file():
            shutil.copyfile(staged, target)
        entry["written_sha256"] = sha(target)
        entry["live_sha256"] = sha(live)
        entry["differs_from_live"] = (
            entry["written_sha256"] is not None
            and entry["written_sha256"] != entry["live_sha256"]
        )
        report["modules"].append(entry)
        if not (entry["staged_exists"] and entry["differs_from_live"]):
            report["all_ok"] = False

    shutil.rmtree(staging, ignore_errors=True)
    for cache in snap.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)

    try:
        reverse_report = json.loads(report["reverse_stdout"])
        by_path = {f["path"]: f for f in reverse_report["files"]}
        for entry in report["modules"]:
            src = by_path.get(entry["path"], {})
            entry["reverse_status"] = src.get("status")
            entry["reverse_newline_form"] = src.get("newline_form")
            entry["reverse_recorded_prefix_sha256"] = src.get("recorded_prefix_sha256") or {
                "lf": src.get("expected_lf"), "crlf": src.get("expected_crlf")
            }
            if src.get("status") != "ok":
                report["all_ok"] = False
    except json.JSONDecodeError:
        report["all_ok"] = False
        report["parse_error"] = "reverse_card_diff did not emit JSON"

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
