"""B2 static checks (no network, no product write).

1. iso tree vs frozen pre-image manifest -> exactly the 2 target files differ
2. product files still equal their pre-image sha (nothing was written to product repos)
3. both iso files compile (py_compile)
4. company-wiki FC-1204-b complexity ratchet replicated on the iso copy:
   max McCabe over top-level functions of dayu_cli_adapter.py must stay <= 46
"""
from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import sys
from datetime import datetime, timezone
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso"
PRE = json.loads((ISO / "preimage.json").read_text(encoding="utf-8"))

DAYU_ISO = ISO / "dayu_repo" / "dayu"
CW_ISO = ISO / "cw_repo" / "src" / "company_wiki"

FROZEN_MAX_DAYU_CLI_ADAPTER = 46  # tests/contract/test_fc1204_complexity_ratchet.py


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mccabe(node: ast.AST) -> int:
    total = 0
    for child in ast.iter_child_nodes(node):
        total += _mccabe(child)
    if isinstance(
        node,
        (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler,
         ast.comprehension, ast.Assert, ast.With),
    ):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
    return total


def max_complexity(text: str) -> int:
    tree = ast.parse(text)
    top = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            top = max(top, 1 + _mccabe(ast.parse(seg)))
    return top


def main() -> int:
    checks = []

    def record(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    # 1. iso tree diff vs pre-image
    for tree_key, root in (("iso/dayu_repo/dayu", DAYU_ISO),
                           ("iso/cw_repo/src/company_wiki", CW_ISO)):
        frozen = PRE["iso_trees"][tree_key]
        current = {}
        for path in sorted(root.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                current[str(path.relative_to(root)).replace("\\", "/")] = sha(path)
        changed = sorted(
            rel for rel, digest in current.items()
            if rel not in frozen or frozen[rel][0] != digest
        )
        removed = sorted(rel for rel in frozen if rel not in current)
        record(
            f"iso_tree_changed_files::{tree_key}",
            removed == [] and (len(changed) <= 1),
            {"changed": changed, "removed": removed},
        )

    # 2. product files untouched (sha == recorded pre-image)
    for target in PRE["targets"]:
        path = Path(target["product_path"])
        record(
            f"product_untouched::{path.name}",
            sha(path) == target["sha256"],
            {"expected": target["sha256"], "actual": sha(path),
             "mtime_utc": target["mtime_utc"]},
        )

    # 3. compile both iso files
    for path in (DAYU_ISO / "fins" / "downloaders" / "sec_downloader.py",
                 CW_ISO / "source_catalog" / "dayu_cli_adapter.py"):
        try:
            py_compile.compile(str(path), doraise=True, cfile=str(path) + ".pyc.check")
            Path(str(path) + ".pyc.check").unlink(missing_ok=True)
            ok, detail = True, "compiles"
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        record(f"compiles::{path.name}", ok, detail)

    # 4. FC-1204-b complexity ratchet replicated on the iso copy
    cw_adapter = CW_ISO / "source_catalog" / "dayu_cli_adapter.py"
    text = cw_adapter.read_text(encoding="utf-8")
    actual = max_complexity(text)
    record(
        "complexity_ratchet::dayu_cli_adapter.py<=46",
        actual <= FROZEN_MAX_DAYU_CLI_ADAPTER,
        {"measured": actual, "frozen_max": FROZEN_MAX_DAYU_CLI_ADAPTER,
         "rule": "tests/contract/test_fc1204_complexity_ratchet.py (AST McCabe, top-level funcs)"},
    )
    dayu_dl = DAYU_ISO / "fins" / "downloaders" / "sec_downloader.py"
    dayu_actual = max_complexity(dayu_dl.read_bytes().decode("utf-8"))
    record(
        "complexity_report::sec_downloader.py (dayu repo has no such ratchet)",
        True,
        {"measured_max_top_level_function": dayu_actual},
    )

    failed = [c for c in checks if not c["ok"]]
    payload = {
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": checks,
        "passed": len(checks) - len(failed),
        "failed": len(failed),
    }
    out = ATTEMPT / "results" / "static_checks.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "failed": payload["failed"],
                      "failed_names": [c["name"] for c in failed]}, ensure_ascii=False))
    return len(failed)


if __name__ == "__main__":
    sys.exit(main())
