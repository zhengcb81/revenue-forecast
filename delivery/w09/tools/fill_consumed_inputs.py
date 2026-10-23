"""Fill the real source-tree SHAs into consumed-inputs.json.

Run after every source edit; the handoff binds the same values.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
OUT = WORKDIR / "delivery" / "w09" / "inputs" / "consumed-inputs.json"
TOOLS = Path(r"C:\Users\郑曾波\.agents\skills\revenue-forecast-audit\scripts")

FILES = [
    "scripts/revenue_forecast.py",
    "scripts/revenue_backtest.py",
    "scripts/lint_input.py",
    "scripts/fix_hashes.py",
    "scripts/revenue_core.py",
    "scripts/revenue_report.py",
    "scripts/contracts/document.py",
    "scripts/contracts/constants.py",
    "scripts/research/evidence_roles.py",
    "scripts/research/drivers.py",
    "scripts/research/native_dependencies.py",
    "scripts/contracts/period_flow.py",
]
REFERENCES = [
    "references/buy-side-methodology.md",
    "references/evidence-role-calibration.md",
    "references/input-construction.md",
]
RECORDER = ["audit_run.py", "execution_request.py"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    record = json.loads(OUT.read_text(encoding="utf-8"))
    source_tree = {}
    for rel in FILES + REFERENCES:
        path = WORKDIR / rel
        source_tree[rel] = {"sha256": sha(path), "byte_size": path.stat().st_size}
    record["rf_cli_sha256"] = {rel: source_tree[rel]["sha256"] for rel in FILES[:4]}
    record["recorder_sha256"] = {str(TOOLS / name): sha(TOOLS / name) for name in RECORDER}
    record["source_tree"] = source_tree
    record["source_tree_sha256"] = hashlib.sha256(
        json.dumps(source_tree, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    record["method_reference_sha256"] = {rel: source_tree[rel]["sha256"] for rel in REFERENCES}
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"source_tree_sha256": record["source_tree_sha256"],
                      "files": len(source_tree)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
