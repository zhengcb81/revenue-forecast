#!/usr/bin/env python3
"""I-16-A 新进程加载路径探针（只读；不写产品，不联网）。

用法：
  python -X utf8 -B _probe_newprocess.py --out probe.json [--site DIR]

行为：
  * 在**新解释器进程**中解析被测模块的加载路径（find_spec / 真实 import 两种方式分别记录），
    计算被加载文件 sha256，并读取 config/policy/flags/schema 常量。
  * 不执行 `dayu` 包体（find_spec 不执行模块代码），避免重型依赖副作用；
    `company_wiki` 与 RF `contracts.constants` 为轻量包，执行真实 import。
  * 全程只读；唯一写入 = --out 指定的 JSON。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as md
import importlib.util
import json
import sys
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
DAYU = Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent")
VENV_PY = DAYU / ".venv" / "Scripts" / "python.exe"

SPEC_ONLY = {"dayu", "dayu.cli"}
REAL_IMPORT = {
    "company_wiki",
    "company_wiki.automation.migrations",
    "company_wiki.source_contract.compatibility",
    "company_wiki.source_catalog.evidence_query",
    "contracts.constants",
    "confidence_policy",
}


def sha256_file(p: Path) -> str | None:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        return None


def pkg_version(name: str) -> dict:
    try:
        d = md.distribution(name)
        editable = None
        url = None
        try:
            du = d.read_text("direct_url.json")
            if du:
                url = du
                editable = bool(json.loads(du).get("dir_info", {}).get("editable"))
        except Exception:
            pass
        return {"version": d.version, "editable": editable, "direct_url": url}
    except Exception as exc:  # noqa: BLE001
        return {"version": None, "error": f"{type(exc).__name__}: {exc}"}


def probe(site: str | None) -> dict:
    if site:
        sys.path.insert(0, str(Path(site).resolve()))
    # RF scripts 目录（产品自身入口的真实加载方式：scripts/ 在 sys.path 上）
    scripts = str(RF / "scripts")
    if scripts not in sys.path:
        sys.path.insert(1 if site else 0, scripts)

    out: dict = {
        "interpreter": {
            "executable": sys.executable,
            "version": sys.version,
            "version_info": list(sys.version_info[:3]),
            "implementation": sys.implementation.name,
        },
        "site_arg": str(Path(site).resolve()) if site else None,
        "sys_path_head": sys.path[:6],
        "packages": {},
        "modules": {},
        "notes": [],
    }
    for name in ("company-wiki", "dayu-agent", "PyYAML", "requests", "httpx", "pydantic"):
        out["packages"][name] = pkg_version(name)

    # 1) 真实 import 的模块
    for name in sorted(REAL_IMPORT):
        entry: dict = {"load_method": "import"}
        try:
            mod = importlib.import_module(name)
            origin = getattr(mod, "__file__", None)
            entry["origin"] = origin
            entry["sha256"] = sha256_file(Path(origin)) if origin else None
            entry["import_status"] = "ok"
        except Exception as exc:  # noqa: BLE001
            entry["import_status"] = f"{type(exc).__name__}: {exc}"
            spec = None
            try:
                spec = importlib.util.find_spec(name)
            except Exception as exc2:  # noqa: BLE001
                entry["spec_error"] = f"{type(exc2).__name__}: {exc2}"
            if spec and spec.origin:
                entry["origin"] = spec.origin
                entry["sha256"] = sha256_file(Path(spec.origin))
                entry["load_method"] = "find_spec_fallback"
            else:
                entry["origin"] = None
                entry["sha256"] = None
        out["modules"][name] = entry

    # 2) 常量（仅在真实 import 成功时读取；否则记 null + 状态）
    def const(mod_name: str, attr: str):
        m = out["modules"].get(mod_name, {})
        if m.get("import_status") != "ok":
            return None
        try:
            return getattr(importlib.import_module(mod_name), attr)
        except Exception as exc:  # noqa: BLE001
            m["const_error"] = f"{type(exc).__name__}: {exc}"
            return None

    out["constants"] = {
        "FORECAST_SCHEMA_VERSION": const("contracts.constants", "FORECAST_SCHEMA_VERSION"),
        "OPT_IN_SCHEMA_VERSION": const("contracts.constants", "OPT_IN_SCHEMA_VERSION"),
        "CW_AUTOMATION_SCHEMA_VERSION": const(
            "company_wiki.automation.migrations", "SCHEMA_VERSION"
        ),
        "SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION": const(
            "company_wiki.source_contract.compatibility",
            "SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION",
        ),
        "CONFIDENCE_POLICY_VERSION": const("confidence_policy", "CONFIDENCE_POLICY_VERSION"),
    }

    # 3) dayu：只解析加载路径，不执行包体
    for name in ("dayu", "dayu.cli"):
        entry = {"load_method": "find_spec_no_import"}
        try:
            spec = importlib.util.find_spec(name)
        except Exception as exc:  # noqa: BLE001
            spec = None
            entry["spec_error"] = f"{type(exc).__name__}: {exc}"
        if spec and spec.origin and spec.origin != "namespace":
            entry["origin"] = spec.origin
            entry["sha256"] = sha256_file(Path(spec.origin))
        else:
            # dayu.cli 用 dayu 包目录推导，避免 import 父包
            top = None
            try:
                s0 = importlib.util.find_spec("dayu")
                top = Path(s0.origin).parent if (s0 and s0.origin) else None
            except Exception:  # noqa: BLE001
                top = None
            cand = (top / "cli.py") if top else None
            entry["origin"] = str(cand) if cand and cand.exists() else None
            entry["sha256"] = sha256_file(cand) if cand else None
            if not spec:
                entry["load_method"] = "derived_no_import"
        out["modules"][name] = entry

    out["notes"].append(
        "dayu 用 find_spec 解析加载路径（解析子模块会执行父包 dayu/__init__，但不执行 dayu.cli 本体），"
        "避免 docling/fastapi 等重型依赖副作用"
    )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--site", default=None)
    args = ap.parse_args()
    data = probe(args.site)
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"probe_written={p} executable={data['interpreter']['executable']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
