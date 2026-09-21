"""Extra regression: the two OTHER production suites that exercise
select_artifact_roles (zr706 selector contract, fc905b trusted receipt).

Run against both the unfixed production bytes and the fixed bytes; any
difference is a behaviour change this card must account for.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import shutil
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
FIXED = ATTEMPT / "iso" / "fixed"
PY = r"C:\Miniconda\python.exe"
RF_TESTS = Path("C:/Users/郑曾波/Projects/revenue-forecast/tests")
TEMP = Path(os.environ.get("TEMP", "/tmp")) / "b3-extra"

SUITES = ["test_zr706_selector_contract.py", "test_fc905b_trusted_receipt.py"]
MODES = ["production", "fixed"]


def _insert_after(text: str, block: str) -> str:
    """Insert ``block`` after the module docstring and __future__ imports.

    `from __future__ import ...` must stay the first statement, so a naive
    prepend produces a SyntaxError.
    """
    import ast

    lines = text.splitlines(keepends=True)
    tree = ast.parse(text)
    insert_at = 0
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            insert_at = node.end_lineno
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            insert_at = node.end_lineno
            continue
        break
    return "".join(lines[:insert_at]) + "\n" + block + "".join(lines[insert_at:])


def stage(mode: str) -> Path:
    """Copy each production suite next to the binding it needs."""
    out = ATTEMPT / "scratch" / f"extra_{mode}"
    if out.exists():
        shutil.rmtree(out)
    (out / "tests").mkdir(parents=True)
    for name in SUITES:
        text = (RF_TESTS / name).read_text(encoding="utf-8")
        header = (
            'import os as _b3_os, sys as _b3_sys\n'
            'from pathlib import Path as _B3Path\n'
            f'_B3_FIXED = _B3Path(r"{FIXED}")\n'
            '_B3_CWS = (_B3_FIXED / "rf_scripts" / "company_wiki_source.py")\n'
            '_B3_MODE = _b3_os.environ.get("B3_BYTES", "production")\n'
            'if _B3_MODE == "fixed":\n'
            '    for _p in (str(_B3_FIXED / "rf_scripts"),\n'
            '               "C:/Users/郑曾波/Projects/company-wiki/src"):\n'
            '        while _p in _b3_sys.path:\n'
            '            _b3_sys.path.remove(_p)\n'
            '        _b3_sys.path.insert(0, _p)\n'
            '    _b3_sys.path_importer_cache.clear()\n'
            '    import importlib.util as _b3_ilu\n'
            '    _s = _b3_ilu.spec_from_file_location("company_wiki_source",\n'
            '                                        _B3_CWS)\n'
            '    _m = _b3_ilu.module_from_spec(_s)\n'
            '    _b3_sys.modules["company_wiki_source"] = _m\n'
            '    _s.loader.exec_module(_m)\n'
            '    assert str(_B3Path(_m.__file__).resolve()) == str(_B3_CWS.resolve())\n'
            'else:\n'
            '    _p = "C:/Users/郑曾波/Projects/revenue-forecast/scripts"\n'
            '    while _p in _b3_sys.path:\n'
            '        _b3_sys.path.remove(_p)\n'
            '    _b3_sys.path.insert(0, _p)\n'
            '    _b3_sys.path_importer_cache.clear()\n'
            '    import company_wiki_source as _m\n'
            '    assert _b3_os.path.basename(str(_m.__file__)) == "company_wiki_source.py"\n'
            "\n")
        (out / "tests" / name).write_text(_insert_after(text, header),
                                          encoding="utf-8")
    return out


def main() -> int:
    results = []
    for mode in MODES:
        staged = stage(mode)
        for name in SUITES:
            basetemp = TEMP / f"{mode}-{name[:-3]}"
            if basetemp.exists():
                shutil.rmtree(basetemp)
            basetemp.mkdir(parents=True)
            env = dict(os.environ)
            env.pop("B3_BYTES", None)
            env["B3_BYTES"] = mode
            env["PYTHONPATH"] = (
                "C:/Users/郑曾波/Projects/revenue-forecast/scripts;"
                "C:/Users/郑曾波/Projects/company-wiki/src")
            argv = [PY, "-X", "utf8", "-B", "-m", "pytest",
                    "-p", "no:cacheprovider", "--basetemp", str(basetemp),
                    "-q", f"tests/{name}"]
            proc = subprocess.run(argv, cwd=str(staged), env=env, text=True,
                                  encoding="utf-8", capture_output=True,
                                  timeout=600)
            tail = (proc.stdout.strip().splitlines() or [""])[-1]
            failed = sorted(set(re.findall(r"FAILED (\S+)", proc.stdout)))
            results.append({"suite": name, "mode": mode, "rc": proc.returncode,
                            "summary": tail, "failed_nodes": failed,
                            "argv": argv, "cwd": str(staged)})
            print(f"[{proc.returncode}] {mode:10s} {name:38s} {tail}")
            for node in failed:
                print(f"        RED  {node.split('::')[-1]}")
    out = ATTEMPT / "scratch" / "extra_regression.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
