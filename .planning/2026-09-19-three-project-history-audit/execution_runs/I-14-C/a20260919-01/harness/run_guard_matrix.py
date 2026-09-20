"""I-14-C r5: refusal matrix for the shared binding guard (r4 review "unable to verify" #1).

Two kinds of evidence, deliberately kept separate:

* **Real driver runs** (``harness/drive_real_exit.py``, the script the suite uses) on scratch
  paths, so the recorded value is the REAL exit code of the real driver:
  ``declared-temp`` -> 3 (the driver's documented ``RE_RAISED_SENTINEL``, i.e. the run was
  allowed and reached its re-raise path), ``attempt`` -> 3, ``temp-undeclared`` -> 97 (refused).
* **In-process calls of the same guard function** (``run_guard.guard_run_dir``) for the
  PRODUCT-path cases.  These are called through a tiny ``python -c`` probe that only imports
  the guard and reports its verdict, so even a broken guard cannot create a directory inside a
  production checkout.  Handing a product path to the driver would make the negative test
  depend on the guard working - the failure mode would be a write into company-wiki.

The guard is a SCOPE guard: product paths are refused unconditionally; any non-product scratch
root may be declared through ``I14C_RUN_ROOT``.  Refusal exit code is 97.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ATTEMPT = HARNESS.parent
ISO = ATTEMPT / "iso"
PY = ISO / "venv" / "Scripts" / "python.exe"
DRIVER = HARNESS / "drive_real_exit.py"
# The product's own test doubles (read-only import; same value the suite uses).
TESTS = Path(os.environ.get("I14C_TESTS_DIR", r"C:\Users\郑曾波\Projects\company-wiki\tests\contract"))
OUT = ATTEMPT / "r5" / "guard"
# drive_real_exit.py returns 3 after a successful re-raise path (RE_RAISED_SENTINEL), so an
# ALLOWED run of ``token-in-message`` is rc=3 with ``RE-RAISED:`` on stderr - not 0.
ALLOWED_RC = 3

PRODUCT_ONE = Path(r"C:\Users\郑曾波\Projects\company-wiki")
PRODUCT_TWO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

PROBE = (
    "import json,sys;"
    "sys.path.insert(0, sys.argv[1]);"
    "from run_guard import guard_run_dir;"
    "r = guard_run_dir(sys.argv[2]);"
    "print(json.dumps({'allowed': r is not None, 'resolved': str(r) if r else None}))"
)


def run_driver(run_dir: Path, run_root: Path | None, label: str) -> dict[str, object]:
    cmd = [
        str(PY),
        "-X",
        "utf8",
        "-B",
        str(DRIVER),
        "--scenario",
        "token-in-message",
        "--run-dir",
        str(run_dir),
        "--src",
        str(ISO / "product_fixed" / "src"),
        "--tests-dir",
        str(TESTS),
    ]
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(HARNESS)
    env.pop("I14C_RUN_ROOT", None)
    if run_root is not None:
        env["I14C_RUN_ROOT"] = str(run_root)
    run_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(run_dir),
    )
    return {
        "case": label,
        "mode": "real-driver",
        "target": str(run_dir),
        "declared_run_root": str(run_root) if run_root is not None else None,
        "argv": cmd,
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip()[-800:],
        "stdout_tail": proc.stdout.strip()[-300:],
    }


def probe_guard(target: Path, run_root: Path | None, label: str) -> dict[str, object]:
    cmd = [str(PY), "-X", "utf8", "-B", "-c", PROBE, str(HARNESS), str(target)]
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env.pop("I14C_RUN_ROOT", None)
    if run_root is not None:
        env["I14C_RUN_ROOT"] = str(run_root)
    proc = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env
    )
    try:
        verdict = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:  # noqa: BLE001 - reported as-is
        verdict = {"allowed": None, "parse_error": proc.stdout.strip()[-300:]}
    return {
        "case": label,
        "mode": "in-process-guard-probe",
        "target": str(target),
        "declared_run_root": str(run_root) if run_root is not None else None,
        "argv": cmd,
        "returncode": proc.returncode,
        "allowed": verdict.get("allowed"),
        "stderr": proc.stderr.strip()[-800:],
    }


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True, exist_ok=True)

    temp_root = Path(tempfile.mkdtemp(prefix="i14c-guard-"))
    (temp_root / "declared").mkdir()
    (temp_root / "undeclared").mkdir()

    cases: list[dict[str, object]] = [
        run_driver(temp_root / "declared" / "run", temp_root, "declared-temp"),
        run_driver(OUT / "attempt-run", None, "attempt"),
        run_driver(temp_root / "undeclared" / "run", None, "temp-undeclared"),
        probe_guard(PRODUCT_ONE / "src" / "company_wiki", temp_root, "temp-plus-product"),
        probe_guard(PRODUCT_ONE / "src", None, "product-src-company-wiki"),
        probe_guard(
            PRODUCT_TWO / "companies" / "_catalog" / ".source_catalog",
            None,
            "product-source-catalog",
        ),
        probe_guard(PRODUCT_TWO / "src", None, "product-revenue-forecast-outside-planning"),
        probe_guard(PRODUCT_TWO / "src", temp_root, "product-revenue-with-declared-root"),
    ]

    expected: dict[str, object] = {
        "declared-temp": ("returncode", ALLOWED_RC),
        "attempt": ("returncode", ALLOWED_RC),
        "temp-undeclared": ("returncode", 97),
        "temp-plus-product": ("allowed", False),
        "product-src-company-wiki": ("allowed", False),
        "product-source-catalog": ("allowed", False),
        "product-revenue-forecast-outside-planning": ("allowed", False),
        "product-revenue-with-declared-root": ("allowed", False),
    }
    for case in cases:
        field, want = expected[str(case["case"])]
        case["expected"] = {field: want}
        case["as_expected"] = case.get(field) == want

    payload = {
        "script": "harness/run_guard_matrix.py",
        "guard": "harness/run_guard.py",
        "refusal_exit": 97,
        "cases": cases,
        "all_as_expected": all(bool(c["as_expected"]) for c in cases),
    }
    (OUT / "matrix.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = []
    for c in cases:
        field = next(iter(c["expected"]))
        lines.append(
            f"{c['case']}: {field}={c.get(field)} expected={c['expected'][field]} "
            f"as_expected={c['as_expected']}"
        )
    (OUT / "matrix.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    shutil.rmtree(temp_root, ignore_errors=True)
    return 0 if payload["all_as_expected"] else 3


if __name__ == "__main__":
    sys.exit(main())
