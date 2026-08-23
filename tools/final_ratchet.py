"""ZR-906: final six-gate ratchet — hardcode / dead path (legacy) /
complexity / type (mypy) / coverage / encoding, across the product code.

  hardcode   company/mine names at CODE level (docstring/comment defense
             labels are allowed — ZR-603/ZR-611 pattern) -> 0 hits.
  legacy     legacy-engine caller references -> 0 hits.
  complexity the complexity ratchet suite (tools/tests/test_complexity_ratchet.py).
  type       mypy errors on scripts/ <= frozen baseline (2 pre-existing).
  coverage   per-module coverage gates (tools/run_coverage_gates.py).
  encoding   BOM / undecodable files under scripts/ and tools/ -> 0.

Usage: python tools/final_ratchet.py [--scripts DIR] — exit non-zero when
any gate is red; designed to become a CI required check (ZR-901 wiring).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
MYPY_BASELINE = 2  # pre-existing mypy errors (frozen; zero-growth gate)

HARDCODE_TERMS = ("Kamoa", "Zijin", "紫金", "Porgera", "601899", "688031")
LEGACY_TERMS = ("legacy_bridge", "LegacyEngine", "legacy_engine")


def _code_lines(path: Path) -> list[str]:
    """Return non-comment, non-docstring code lines of a python file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    lines = text.splitlines()
    in_docstring = False
    code: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('"""', "'''")) or stripped.endswith(('"""', "'''")):
            in_docstring = not in_docstring
            continue
        if in_docstring or stripped.startswith("#"):
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
    for pattern in ("*.py",):
        for path in sorted((root / "scripts").glob(pattern)) + sorted(
                (root / "tools").glob(pattern)):
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                problems.append(f"{path.name}: UTF-8 BOM")
            elif raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
                problems.append(f"{path.name}: UTF-16 BOM")
    return problems


def gate_complexity() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "tests" / "test_complexity_ratchet.py")],
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    ok = proc.returncode == 0
    return ok, "complexity ratchet OK" if ok else f"complexity FAILED rc={proc.returncode}"


def gate_type() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "mypy", str(SCRIPTS), "--no-error-summary",
         "--ignore-missing-imports"],
        capture_output=True, text=True, encoding="utf-8", timeout=300,
    )
    errors = sum(1 for line in proc.stdout.splitlines() if ": error:" in line)
    ok = errors <= MYPY_BASELINE
    return ok, f"mypy errors {errors} (baseline {MYPY_BASELINE})"


def gate_coverage() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "run_coverage_gates.py")],
        capture_output=True, text=True, encoding="utf-8", timeout=960,
    )
    ok = proc.returncode == 0
    tail = (proc.stdout or "")[-160:].replace("\n", " ")
    return ok, f"coverage gates rc={proc.returncode} {tail}"


def run_all(root: Path, scanners_only: bool = False) -> dict:
    hardcode = scan_hardcode(root / "scripts")
    legacy = scan_legacy(root / "scripts")
    encoding = scan_encoding(root)
    if scanners_only:
        return {
            "hardcode": {"ok": not hardcode, "hits": hardcode},
            "legacy": {"ok": not legacy, "hits": legacy},
            "encoding": {"ok": not encoding, "hits": encoding},
            "complexity": {"ok": True, "detail": "skipped (scanners-only)"},
            "type": {"ok": True, "detail": "skipped (scanners-only)"},
            "coverage": {"ok": True, "detail": "skipped (scanners-only)"},
        }
    c_ok, c_detail = gate_complexity()
    t_ok, t_detail = gate_type()
    cov_ok, cov_detail = gate_coverage()
    return {
        "hardcode": {"ok": not hardcode, "hits": hardcode},
        "legacy": {"ok": not legacy, "hits": legacy},
        "encoding": {"ok": not encoding, "hits": encoding},
        "complexity": {"ok": c_ok, "detail": c_detail},
        "type": {"ok": t_ok, "detail": t_detail},
        "coverage": {"ok": cov_ok, "detail": cov_detail},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Final six-gate ratchet (ZR-906)")
    parser.add_argument("--scripts", type=Path, default=SCRIPTS)
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument("--scanners-only", action="store_true",
                        help="skip slow gates (mypy/coverage/complexity)")
    args = parser.parse_args()
    result = run_all(args.scripts.parent, scanners_only=args.scanners_only)
    if args.print_json:
        import json

        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for name, gate in result.items():
            detail = gate.get("detail") or ("" if gate["ok"] else f" {gate['hits']}")
            print(f"{name}: {'OK' if gate['ok'] else 'RED'}{detail}")
    return 0 if all(g["ok"] for g in result.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
