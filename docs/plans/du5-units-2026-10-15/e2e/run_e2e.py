#!/usr/bin/env python3
"""DU5-RF-UNITS offline E2E driver — synthetic data, 0 API / 0 model calls.

Usage (from the worktree root):

    python docs/plans/du5-units-2026-10-15/e2e/run_e2e.py --build-fixture
    python docs/plans/du5-units-2026-10-15/e2e/run_e2e.py
    python docs/plans/du5-units-2026-10-15/e2e/run_e2e.py --receipt-dir ABS_PATH

What it exercises, all against the shipped public entry points:

1.  hand-computed unit oracles (7.25 yi = 725 million, 5 shiyi = 5000
    million, and both reverses) — compared against hardcoded constants,
    never against numbers read back from the implementation's own report;
2.  ``scripts/revenue_forecast.py INPUT --validate-only`` on the synthetic
    HKD fixture (zero writes);
3.  the formal ``run_forecast`` path through the CLI (``--output``/
    ``--markdown`` into this run's temp dir, publication registry redirected
    into the same temp dir): intermediate units, final revenue delta and the
    stored evidence record must all agree with the hand numbers;
4.  three guard groups: same-numbers-different-currency rejection, reloaded
    record re-derivation (tamper -> refuse), and old USD/RMB samples not
    regressing.

A sentinel file must survive unchanged and only this run's temp dirs are
deleted; ``git status`` must not grow outside the PWF receipts directory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

FIXTURE = ROOT / "tests" / "fixtures" / "du5_money_units" / "hkd_synthetic_input.json"
RECEIPTS = ROOT / "docs" / "plans" / "du5-units-2026-10-15" / "receipts"

# Hand oracles — computed on paper, not read back from the engine.
HAND_YI_TO_MILLION = 725.0        # 7.25 yi (1e8) = 725 million
HAND_SHIYI_TO_MILLION = 5000.0    # 5 shiyi (1e9) = 5000 million
HAND_MILLION_TO_YI = 7.25         # reverse of the first
HAND_MILLION_TO_SHIYI = 5.0       # reverse of the second
HAND_BASE_TERMINAL = 181.5        # 121 + 60.5 on the synthetic fixture
HAND_UP_TERMINAL = 906.5          # 121 + 725 + 60.5
HAND_DOWN_TERMINAL = 60.5         # 121 - 725 clamps to 0 -> 0 + 60.5
HAND_DELTA = 725.0                # the converted shock enters the delta


def re_denominate(data: dict, currency: str, scale: str) -> dict:
    data = copy.deepcopy(data)
    data["currency"] = currency
    data["unit"] = scale
    for entry in data["parameters"]:
        if "currency" in entry:
            entry["currency"] = currency
            entry["scale"] = scale
            entry["unit"] = f"{currency} {scale}"
    for claim in data["evidence_claims"]:
        unit = claim.get("unit")
        if isinstance(unit, str) and unit.startswith("USD "):
            claim["unit"] = f"{currency} {scale}"
    return data


def base_document(currency: str, scale: str) -> dict:
    from test_recognition_bridge import forecast_document

    data = re_denominate(forecast_document(), currency, scale)
    data["company_name"] = f"SYNTHETIC DU5 {currency} issuer"
    return data


def hk_d_fixture_document() -> dict:
    from research.input_quantities import build_sensitivity_test

    data = base_document("HKD", "million")
    # Explicit HKD source quantity 7.25 yi -> the parameter's HKD million scale.
    data["sensitivity_tests"] = [
        build_sensitivity_test(
            parameter_id="0_base_2027", value=7.25, input_unit="hkd_100m",
            shock_semantics="absolute", engine_unit="hkd_million",
        )
    ]
    return data


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # LF-only bytes so the on-disk sha matches the git-blob sha everywhere.
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_bytes(text.encode("utf-8"))


def build_fixture() -> None:
    write_json(FIXTURE, hk_d_fixture_document())
    digest = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    print(f"fixture written: {FIXTURE.relative_to(ROOT).as_posix()} sha256={digest}")


def cli(args: list[str], env: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "revenue_forecast.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, cwd=cwd, timeout=300,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-fixture", action="store_true")
    parser.add_argument("--receipt-dir", type=Path, default=RECEIPTS,
                        help="receipt output directory (default: retained lane receipts)")
    args = parser.parse_args()
    receipt_dir = args.receipt_dir.resolve()
    if args.build_fixture:
        build_fixture()
        return 0
    if not FIXTURE.exists():
        print("run --build-fixture first", file=sys.stderr)
        return 2

    checks: dict[str, object] = {}
    temp_root = Path(tempfile.mkdtemp(prefix="du5-e2e-"))
    out_dir = temp_root / "out"
    out_dir.mkdir()
    sentinel = out_dir / "sentinel.txt"
    sentinel_text = "du5 sentinel: outputs must not disturb this file\n"
    sentinel.write_text(sentinel_text, encoding="utf-8")
    registry = temp_root / "publications.jsonl"
    # Redirect the publication registry for THIS process too: in-process
    # run_forecast(mode="formal") reads os.environ at call time, and the
    # production artifacts/registry must never receive this run's entries.
    previous_registry = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
    os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(registry)
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(registry)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    default_registry = ROOT / "artifacts" / "registry" / "publications.jsonl"

    def registry_state() -> tuple[bool, str]:
        if not default_registry.exists():
            return (False, "absent")
        digest = hashlib.sha256(default_registry.read_bytes()).hexdigest()
        return (True, digest)

    registry_before = registry_state()
    git_before = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", cwd=ROOT,
    ).stdout.splitlines()

    fixture_data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    failures: list[str] = []

    def check(name: str, ok: bool, detail: object = None) -> None:
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failures.append(name)

    try:
        from revenue_core import ForecastInputError, run_forecast
        from research.input_quantities import (
            convert_input_quantity,
            validate_input_quantity_record,
        )
        from revenue_report import validate_published_forecast

        # --- 1. hand-computed unit oracles ---------------------------------
        from research.input_quantities import build_sensitivity_test

        r = convert_input_quantity(7.25, input_unit="hkd_100m", engine_unit="hkd_million")
        check("hand_yi_to_million", abs(r["engine_value"] - HAND_YI_TO_MILLION) < 1e-9,
              {"engine_value": r["engine_value"], "conversion": r["conversion"]})
        r = convert_input_quantity(5, input_unit="hkd_billion", engine_unit="hkd_million")
        check("hand_shiyi_to_million", abs(r["engine_value"] - HAND_SHIYI_TO_MILLION) < 1e-9,
              {"engine_value": r["engine_value"], "conversion": r["conversion"]})
        r = convert_input_quantity(725, input_unit="hkd_million", engine_unit="hkd_100m")
        check("hand_million_to_yi", abs(r["engine_value"] - HAND_MILLION_TO_YI) < 1e-9,
              {"engine_value": r["engine_value"], "conversion": r["conversion"]})
        r = convert_input_quantity(5000, input_unit="hkd_million", engine_unit="hkd_billion")
        check("hand_million_to_shiyi", abs(r["engine_value"] - HAND_MILLION_TO_SHIYI) < 1e-9,
              {"engine_value": r["engine_value"], "conversion": r["conversion"]})

        # --- 2. public CLI validate-only (zero writes) ---------------------
        proc = cli([str(FIXTURE), "--validate-only"], env, ROOT)
        check("cli_validate_only_exit", proc.returncode == 0,
              {"stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]})

        # --- 3. formal run_forecast path via the CLI (report/products) -----
        out_json = out_dir / "forecast.json"
        out_md = out_dir / "forecast.md"
        proc = cli(
            [str(FIXTURE), "--output", str(out_json), "--markdown", str(out_md)],
            env, ROOT,
        )
        check("cli_formal_exit", proc.returncode == 0,
              {"stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]})
        if out_json.exists():
            result = json.loads(out_json.read_text(encoding="utf-8"))
            sensitivity = result["sensitivities"][0]
            record = sensitivity["input_quantity"]
            # intermediate unit record: source 7.25 yi -> parameter's million scale
            check("e2e_record_units",
                  record["input_unit"] == "hkd_100m"
                  and record["engine_unit"] == "hkd_million"
                  and abs(record["engine_value"] - HAND_YI_TO_MILLION) < 1e-9
                  and "x 100" in record["conversion"],
                  record)
            check("e2e_shock_value", abs(sensitivity["shock_value"] - HAND_YI_TO_MILLION) < 1e-9,
                  sensitivity["shock_value"])
            baseline = result["consolidated_forecast"]["base"]["terminal_revenue"]
            check("e2e_baseline_terminal", abs(baseline - HAND_BASE_TERMINAL) < 1e-9, baseline)
            delta = sensitivity["up_terminal_revenue"] - baseline
            check("e2e_final_delta", abs(delta - HAND_DELTA) < 1e-9,
                  {"delta": delta, "up": sensitivity["up_terminal_revenue"]})
            check("e2e_up_terminal", abs(sensitivity["up_terminal_revenue"] - HAND_UP_TERMINAL) < 1e-9,
                  sensitivity["up_terminal_revenue"])
            check("e2e_down_terminal", abs(sensitivity["down_terminal_revenue"] - HAND_DOWN_TERMINAL) < 1e-9,
                  {"down": sensitivity["down_terminal_revenue"],
                   "clamped": sensitivity["clamped"]})
            # evidence records consistent: the stored lineage re-derives and the
            # published output validates against the input document.
            try:
                validate_input_quantity_record(copy.deepcopy(record), field="e2e.record")
                record_ok, record_detail = True, "re-derived"
            except ForecastInputError as exc:
                record_ok, record_detail = False, str(exc)
            check("e2e_record_recomputes", record_ok, record_detail)
            try:
                validate_published_forecast(result, fixture_data)
                pub_ok, pub_detail = True, "published output validated"
            except Exception as exc:  # noqa: BLE001 - recorded honestly
                pub_ok, pub_detail = False, f"{type(exc).__name__}: {exc}"
            check("e2e_evidence_records_consistent", pub_ok, pub_detail)
            check("e2e_markdown_report", out_md.exists() and out_md.stat().st_size > 0,
                  {"bytes": out_md.stat().st_size if out_md.exists() else 0})
        else:
            check("cli_formal_outputs", False, "forecast.json missing")

        # formal path also runs in-process (same engine, registry redirected)
        formal_result = run_forecast(copy.deepcopy(fixture_data), mode="formal")
        check("run_forecast_formal_delta",
              abs(formal_result["sensitivities"][0]["up_terminal_revenue"]
                  - formal_result["consolidated_forecast"]["base"]["terminal_revenue"]
                  - HAND_DELTA) < 1e-9,
              formal_result["sensitivities"][0]["shock_value"])

        # --- 4a. same numbers, different currency -> rejected --------------
        from research.input_quantities import convert_input_quantity as conv

        cross = base_document("HKD", "million")
        cross["sensitivity_tests"] = [{
            "name": "usd_label_same_numbers", "parameter_id": "0_base_2027",
            "shock_type": "absolute", "shock_value": HAND_YI_TO_MILLION,
            "input_quantity": conv(725, input_unit="usd_million", engine_unit="usd_million"),
        }]
        cross_path = temp_root / "cross_currency.json"
        write_json(cross_path, cross)
        proc = cli([str(cross_path), "--validate-only"], env, ROOT)
        combined = proc.stdout + proc.stderr
        check("e2e_cross_currency_rejected",
              proc.returncode != 0 and "currency" in combined.lower(),
              {"exit": proc.returncode, "stderr": proc.stderr[-1200:]})

        # --- 4b. reloaded record re-derives; tampering is refused ----------
        tampered = copy.deepcopy(fixture_data)
        tampered["sensitivity_tests"][0]["input_quantity"]["conversion"] += " x 1"
        tampered_path = temp_root / "tampered_record.json"
        write_json(tampered_path, tampered)
        proc = cli([str(tampered_path), "--validate-only"], env, ROOT)
        combined = proc.stdout + proc.stderr
        check("e2e_tampered_record_rejected",
              proc.returncode != 0 and "input_quantity" in combined.lower(),
              {"exit": proc.returncode, "stderr": proc.stderr[-1200:]})

        # --- 4c. old USD/RMB samples do not regress ------------------------
        for currency, unit_name in (("USD", "usd_million"), ("CNY", "cny_million")):
            old = base_document(currency, "million")
            old["sensitivity_tests"] = [
                build_sensitivity_test(
                    parameter_id="0_base_2027", value=2.5, input_unit=unit_name,
                    shock_semantics="absolute",
                )
            ]
            old_path = temp_root / f"legacy_{currency.lower()}.json"
            write_json(old_path, old)
            proc = cli([str(old_path), "--validate-only"], env, ROOT)
            check(f"e2e_legacy_{currency.lower()}_validate",
                  proc.returncode == 0, {"exit": proc.returncode,
                                         "stderr": proc.stderr[-1200:]})
            legacy_result = run_forecast(copy.deepcopy(old), mode="formal")
            legacy = legacy_result["sensitivities"][0]
            up = legacy["up_terminal_revenue"]
            # hand: 121 + 2.5 = 123.5, terminal 123.5 + 60.5 = 184.0
            check(f"e2e_legacy_{currency.lower()}_delta",
                  abs(up - 184.0) < 1e-9 and abs(legacy["shock_value"] - 2.5) < 1e-9,
                  {"shock": legacy["shock_value"], "up_terminal": up})
    finally:
        # --- restore/cleanup: sentinel intact, temp dirs are ours only -----
        sentinel_ok = sentinel.exists() and sentinel.read_text(encoding="utf-8") == sentinel_text
        registry_isolated = str(registry).startswith(str(temp_root))
        registry_after = registry_state()
        default_registry_untouched = registry_after == registry_before
        git_after = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=ROOT,
        ).stdout.splitlines()
        allowed_prefix = "?? docs/plans/du5-units-2026-10-15/receipts/"
        new_entries = sorted(set(git_after) - set(git_before))
        stray = [e for e in new_entries if not e.startswith(allowed_prefix)]
        # The publication registry is chmod-ed read-only after each append;
        # clear that guard before removing this run's own temp tree.
        def _clear_read_only(path: Path) -> None:
            try:
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass

        for path in sorted(temp_root.rglob("*"), reverse=True):
            _clear_read_only(path)
        _clear_read_only(temp_root)
        shutil.rmtree(temp_root, ignore_errors=True)
        for _ in range(4):
            if not temp_root.exists():
                break
            time.sleep(0.5)
            shutil.rmtree(temp_root, ignore_errors=True)
        cleanup = {
            "receipt": "du5-cleanup/1",
            "sentinel_intact": sentinel_ok,
            "registry_redirected_into_temp": registry_isolated,
            "default_registry_before": {"exists": registry_before[0], "sha256": registry_before[1]},
            "default_registry_after": {"exists": registry_after[0], "sha256": registry_after[1]},
            "default_registry_untouched": default_registry_untouched,
            "temp_dir_removed": not temp_root.exists(),
            "temp_dir": str(temp_root),
            "git_new_entries_outside_receipts": stray,
        }
        if previous_registry is None:
            os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
        else:
            os.environ["REVENUE_PUBLICATION_REGISTRY"] = previous_registry
        write_json(receipt_dir / "e2e-cleanup.json", cleanup)
        checks["cleanup"] = cleanup
        if not (
            sentinel_ok and registry_isolated and default_registry_untouched
            and not temp_root.exists() and not stray
        ):
            failures.append("cleanup")

    write_json(
        receipt_dir / "e2e-run.json",
        {
            "receipt": "du5-e2e/1",
            "fixture": FIXTURE.relative_to(ROOT).as_posix(),
            "fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "hand_oracles": {
                "yi_to_million": HAND_YI_TO_MILLION,
                "shiyi_to_million": HAND_SHIYI_TO_MILLION,
                "million_to_yi": HAND_MILLION_TO_YI,
                "million_to_shiyi": HAND_MILLION_TO_SHIYI,
                "base_terminal": HAND_BASE_TERMINAL,
                "up_terminal": HAND_UP_TERMINAL,
                "down_terminal": HAND_DOWN_TERMINAL,
                "delta": HAND_DELTA,
            },
            "checks": checks,
            "failures": failures,
        },
    )
    print(json.dumps({"failures": failures, "checks": list(checks)}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
