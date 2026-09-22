"""B3-PREREQ probe harness — loads a target conftest in a fresh subprocess.

Usage: python b3p_probe.py <conftest_path> <guard|provenance>

Prints ONE json line on stdout describing what the target conftest actually did.
Used unchanged against:
  * the RED baseline  : b3_reference/iso/conftest.py  (B3's original, byte-identical)
  * the fixed subject  : iso/conftest.py               (this attempt's REM-47 fix)
so the RED/GREEN difference is attributable to the conftest under test, not the harness.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _load(target: Path):
    spec = importlib.util.spec_from_file_location("b3p_conftest_under_test", target)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load conftest from {target}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _guard(mod) -> dict:
    spec = importlib.util.find_spec("company_wiki_source")
    origin = Path(spec.origin).resolve() if spec and spec.origin else None
    fixed_cws = Path(mod.FIXED_RF) / "company_wiki_source.py"
    prod_cws = Path(mod.RF_ROOT) / "scripts" / "company_wiki_source.py"
    return {
        "sys_path_head": sys.path[:8],
        "fixed_rf": str(Path(mod.FIXED_RF)),
        "fixed_cw": str(Path(mod.FIXED_CW)),
        "rf_scripts": str(Path(mod.RF_ROOT) / "scripts"),
        "cw_src": str(Path(mod.CW_ROOT) / "src"),
        "origin": str(origin) if origin else None,
        "fixed_cws": str(fixed_cws.resolve()),
        "prod_cws": str(prod_cws.resolve()),
        "fixed_exists": fixed_cws.is_file(),
        "prod_exists": prod_cws.is_file(),
        "fixed_sha": _sha256(fixed_cws) if fixed_cws.is_file() else None,
        "prod_sha": _sha256(prod_cws) if prod_cws.is_file() else None,
    }


def _provenance(mod) -> dict:
    prov_path = Path(mod.ATTEMPT_ROOT) / "scratch" / "module_provenance.json"
    saved = prov_path.read_bytes() if prov_path.exists() else None

    fixed_file = str((Path(mod.FIXED_RF) / "company_wiki_source.py").resolve())
    prod_file = str((Path(mod.RF_ROOT) / "scripts" / "company_wiki_source.py").resolve())
    dag_file = str((Path(mod.FIXED_CW) / "artifact_dag.py").resolve())

    import importlib

    real_import_module = importlib.import_module

    def make_fake(cws_file: str):
        def fake(name, package=None):  # noqa: ANN001
            if name == "company_wiki_source":
                return types.SimpleNamespace(__file__=cws_file)
            if name == "company_wiki.source_catalog.artifact_dag":
                return types.SimpleNamespace(__file__=dag_file)
            return real_import_module(name, package)
        return fake

    orders = {}
    try:
        for order_name, files in (
            ("fixed_then_production", (fixed_file, prod_file)),
            ("production_then_fixed", (prod_file, fixed_file)),
        ):
            if prov_path.exists():
                prov_path.unlink()
            for cws_file in files:
                importlib.import_module = make_fake(cws_file)
                mod.pytest_sessionfinish(None, 0)
            orders[order_name] = (
                json.loads(prov_path.read_text(encoding="utf-8"))
                if prov_path.exists() else None
            )
    finally:
        importlib.import_module = real_import_module
        if saved is None:
            if prov_path.exists():
                prov_path.unlink()
        else:
            prov_path.write_bytes(saved)

    return {
        "fixed_file": fixed_file,
        "prod_file": prod_file,
        "fixed_sha": _sha256(Path(fixed_file)),
        "prod_sha": _sha256(Path(prod_file)),
        "orders": orders,
        "restored_prior_record": saved is not None or not prov_path.exists(),
    }


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    scenario = sys.argv[2]
    out = {"target": str(target), "scenario": scenario}
    try:
        mod = _load(target)
        if scenario == "guard":
            out.update(_guard(mod))
        elif scenario == "provenance":
            out.update(_provenance(mod))
        else:
            raise RuntimeError(f"unknown scenario {scenario!r}")
    except BaseException as exc:  # noqa: BLE001 - surface, do not swallow
        out["error"] = f"{type(exc).__name__}: {exc}"
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
