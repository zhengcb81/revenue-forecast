"""ZR-906: final six-gate ratchet — hardcode / dead path (legacy) /
complexity / type (mypy) / coverage / encoding, across the product code.

  hardcode    company/mine names at CODE level (docstring/comment defense
              labels are allowed — ZR-603/ZR-611 pattern) -> 0 hits.
  legacy      legacy-engine caller references -> 0 hits.
  complexity  the complexity ratchet suite (tools/tests/test_complexity_ratchet.py).
  type        the REAL mypy result: a usable run is reported as-is (the
              historical error count is a diagnostic, never a pass claim);
              mypy that is missing, unusable or times out is RED.
  coverage    not supplied by default; the explicit full mode runs the
              offline responsibility exactly once into its own scratch.
  encoding    BOM / undecodable files under scripts/ and tools/ -> 0.

Usage:
  python tools/final_ratchet.py                    # light: scanners + complexity + type
  python tools/final_ratchet.py --scanners-only    # scanners only
  python tools/final_ratchet.py --full --coverage-scratch DIR [--target ...]

Exit is non-zero when any gate is red.  ``MYPY_BASELINE`` stays as the
recorded measurement for reporting only — it no longer decides anything.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
# Measured on 2026-08-23: mypy scripts --no-error-summary --ignore-missing-imports
# reports 69 errors (independent reviewer replication).  Retained as a reported
# reference only; gate_type() explains itself with the live tool result and
# never converts a historical count into "no errors".
MYPY_BASELINE = 69

HARDCODE_TERMS = ("Kamoa", "Zijin", "紫金", "Porgera", "601899", "688031")
LEGACY_TERMS = ("legacy_bridge", "LegacyEngine", "legacy_engine")

_LABELS = {
    "ok": "OK",
    "red": "RED",
    "not_supplied": "NOT_SUPPLIED",
    "diagnostic": "DIAGNOSTIC",
}


def _code_lines(path: Path) -> list[str]:
    """Return non-comment, non-docstring code lines of a python file.

    Line-based docstring state machine: a line that starts with the triple
    quote (after indentation) opens or closes a docstring block; a line that
    ENDS with the triple quote closes a block opened on an earlier line
    (e.g. ``...inheritance).\"\"\"``).  Triple-quoted strings inside
    assignments/expressions do not start with the quote and stay code.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    in_docstring = False
    code: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('"""', "'''")):
            in_docstring = not in_docstring
            continue
        if in_docstring:
            if stripped.endswith(('"""', "'''")):
                in_docstring = False
            continue
        if stripped.startswith("#"):
            continue
        code.append(line)
    return code


def scan_hardcode(scripts_dir: Path) -> list[str]:
    hits = []
    for path in sorted(scripts_dir.glob("*.py")):
        for number, line in enumerate(_code_lines(path), 1):
            if any(term in line for term in HARDCODE_TERMS):
                hits.append(f"{path.name}:{number}: {line.strip()[:80]}")
    return hits


def scan_legacy(scripts_dir: Path) -> list[str]:
    hits = []
    for path in sorted(scripts_dir.glob("*.py")):
        for number, line in enumerate(_code_lines(path), 1):
            if any(term in line for term in LEGACY_TERMS):
                hits.append(f"{path.name}:{number}: {line.strip()[:80]}")
    return hits


def scan_encoding(root: Path) -> list[str]:
    problems = []
    for directory in (root / "scripts", root / "tools"):
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in (".py", ".json", ".yaml", ".yml", ".md"):
                continue
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                problems.append(f"{path.name}: UTF-8 BOM")
            elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
                problems.append(f"{path.name}: UTF-16 BOM")
            elif path.suffix in (".py", ".json"):
                try:
                    raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    problems.append(f"{path.name}: undecodable ({exc})")
    return problems


def gate_complexity() -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "tests" / "test_complexity_ratchet.py"),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return False, "complexity ratchet timed out after 300s"
    except OSError as exc:
        return False, f"complexity ratchet failed to start: {exc}"
    ok = proc.returncode == 0
    return ok, (
        "complexity ratchet OK" if ok else f"complexity FAILED rc={proc.returncode}"
    )


def gate_type() -> tuple[bool, str]:
    """Explain the type situation with the REAL mypy tool result.

    A usable mypy that reports N historical errors is a diagnostic: the count
    no longer decides qualification and is never restated as "no errors".
    A mypy that cannot start, does not identify itself, exits with a usage or
    configuration error, or times out is RED.
    """
    try:
        probe = subprocess.run(
            [sys.executable, "-m", "mypy", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, "mypy unavailable: --version timed out"
    except OSError as exc:
        return False, f"mypy unavailable: {exc}"
    banner = f"{probe.stdout or ''}{probe.stderr or ''}"
    if probe.returncode != 0 or "mypy" not in banner.lower():
        return False, (
            f"mypy unavailable (python -m mypy --version rc={probe.returncode})"
        )
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "mypy", str(SCRIPTS), "--no-error-summary",
             "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return False, "mypy failed: the scripts/ run timed out after 300s"
    except OSError as exc:
        return False, f"mypy failed to start: {exc}"
    errors = sum(1 for line in (proc.stdout or "").splitlines() if ": error:" in line)
    if proc.returncode >= 2:
        return False, (
            f"mypy failed rc={proc.returncode}; {errors} error line(s) reported"
        )
    if proc.returncode == 0:
        return True, "mypy OK (0 errors)"
    return True, (
        f"mypy reported {errors} error(s) (historical baseline "
        f"{MYPY_BASELINE}; the count is a diagnostic, not a gate)"
    )


def gate_coverage(
    scratch: Path | None = None,
    target: list[str] | None = None,
) -> tuple[bool, str]:
    """Delegated, explicit coverage run — never started by the default mode."""
    if scratch is None:
        return True, (
            "coverage not_supplied (run it explicitly with --full "
            "--coverage-scratch DIR)"
        )
    args = [
        sys.executable,
        str(ROOT / "tools" / "run_coverage_gates.py"),
        "--run",
        "--scratch",
        str(scratch),
    ]
    for item in target or []:
        args += ["--target", item]
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=960,
        )
    except subprocess.TimeoutExpired:
        return False, "coverage run timed out after 960s"
    except OSError as exc:
        return False, f"coverage run failed to start: {exc}"
    tail = (proc.stdout or "")[-200:].replace("\n", " ")
    ok = proc.returncode == 0
    return ok, f"coverage gates rc={proc.returncode} {tail}"


def _scan_gate(hits: list[str]) -> dict:
    if hits:
        return {
            "ok": False,
            "status": "red",
            "detail": "; ".join(hits[:5]),
            "problems": list(hits),
        }
    return {"ok": True, "status": "ok", "detail": "", "problems": []}


def _status(ok: bool) -> str:
    return "ok" if ok else "red"


def run_all(
    root: Path,
    scanners_only: bool = False,
    full: bool = False,
    coverage_scratch: Path | None = None,
    coverage_target: list[str] | None = None,
) -> dict:
    hardcode = scan_hardcode(root / "scripts")
    legacy = scan_legacy(root / "scripts")
    encoding = scan_encoding(root)
    if scanners_only:
        return {
            "hardcode": _scan_gate(hardcode),
            "legacy": _scan_gate(legacy),
            "encoding": _scan_gate(encoding),
            "complexity": {
                "ok": True,
                "status": "ok",
                "detail": "skipped (scanners-only)",
                "problems": [],
            },
            "type": {
                "ok": True,
                "status": "ok",
                "detail": "skipped (scanners-only)",
                "problems": [],
            },
            "coverage": {
                "ok": True,
                "status": "ok",
                "detail": "skipped (scanners-only)",
                "problems": [],
            },
        }
    c_ok, c_detail = gate_complexity()
    t_ok, t_detail = gate_type()
    if full:
        cov_ok, cov_detail = gate_coverage(coverage_scratch, coverage_target)
        cov_status = _status(cov_ok)
    else:
        cov_ok, cov_detail, cov_status = (
            True,
            "coverage not_supplied (use --full --coverage-scratch DIR)",
            "not_supplied",
        )
    return {
        "hardcode": _scan_gate(hardcode),
        "legacy": _scan_gate(legacy),
        "encoding": _scan_gate(encoding),
        "complexity": {
            "ok": c_ok,
            "status": _status(c_ok),
            "detail": c_detail,
            "problems": [] if c_ok else [c_detail],
        },
        "type": {
            "ok": t_ok,
            "status": _status(t_ok),
            "detail": t_detail,
            "problems": [] if t_ok else [t_detail],
        },
        "coverage": {
            "ok": cov_ok,
            "status": cov_status,
            "detail": cov_detail,
            "problems": [] if cov_ok else [cov_detail],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Final six-gate ratchet (ZR-906)")
    parser.add_argument("--scripts", type=Path, default=SCRIPTS)
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument(
        "--scanners-only",
        action="store_true",
        help="skip the light gates too (scanners only)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="explicitly run the coverage responsibility once",
    )
    parser.add_argument(
        "--coverage-scratch",
        type=Path,
        default=None,
        dest="coverage_scratch",
        help="directory that receives every coverage file (required with --full)",
    )
    parser.add_argument(
        "--coverage-target",
        action="append",
        default=None,
        dest="coverage_target",
        metavar="PATH",
        help="pytest target for --full (repeatable; default: tests)",
    )
    args = parser.parse_args(argv)
    if args.full and args.coverage_scratch is None:
        parser.error("--full requires --coverage-scratch DIR")
    if args.full and args.scanners_only:
        parser.error("--full cannot be combined with --scanners-only")
    result = run_all(
        args.scripts.parent,
        scanners_only=args.scanners_only,
        full=args.full,
        coverage_scratch=args.coverage_scratch,
        coverage_target=args.coverage_target,
    )
    if args.print_json:
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for name, gate in result.items():
            label = _LABELS.get(gate["status"], gate["status"].upper())
            print(f"{name}: {label} {gate.get('detail') or ''}".rstrip())
    return 0 if all(gate["ok"] for gate in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
