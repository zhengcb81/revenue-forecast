"""Build changes.diff for MODEL-ORACLE-ALIGN a20260922-01.

Two clearly separated repo-prefixed sections:
  SECTION 1 - TEST ALIGNMENT      : tests/test_model_economic_guardrails.py
  SECTION 2 - REGISTRY RE-PROMOTION: scripts/model_registry.py (I-10-B B-6c)
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

BEFORE_TEST = ATTEMPT / "recovery" / "before_images" / "test_alignment" / "test_model_economic_guardrails.py"
AFTER_TEST = ATTEMPT / "iso_promoted" / "tests" / "test_model_economic_guardrails.py"
BEFORE_REG = ATTEMPT / "recovery" / "before_images" / "registry_repromotion" / "model_registry.py"
AFTER_REG = ATTEMPT / "iso" / "rf" / "scripts" / "model_registry.py"
OUT = ATTEMPT / "changes.diff"


def section(title: str, rel: str, before: Path, after: Path) -> str:
    b = before.read_text(encoding="utf-8").splitlines(keepends=True)
    a = after.read_text(encoding="utf-8").splitlines(keepends=True)
    diff = list(difflib.unified_diff(b, a, fromfile=f"a/{rel}", tofile=f"b/{rel}", n=3))
    if not diff:
        raise SystemExit(f"expected non-empty diff for {rel}")
    banner = f"# ===== {title} =====\n# {rel} (attempt-local before/after images; both pinned in binding.json)\n"
    return banner + "".join(diff)


def main() -> int:
    # production state must equal the iso/frozen sources at diff time
    prod_test = REPO / "tests" / "test_model_economic_guardrails.py"
    prod_reg = REPO / "scripts" / "model_registry.py"
    assert prod_test.read_bytes() == AFTER_TEST.read_bytes(), "production test != aligned iso test"
    assert prod_reg.read_bytes() == AFTER_REG.read_bytes(), "production registry != promoted source"

    parts = [
        section(
            "SECTION 1 - TEST ALIGNMENT (oracle alignment only: previously-implied "
            "defaults made explicit; NO assertion weakened, NO business rule changed)",
            "tests/test_model_economic_guardrails.py", BEFORE_TEST, AFTER_TEST,
        ),
        "\n",
        section(
            "SECTION 2 - REGISTRY RE-PROMOTION (row B-6c, I-10-B defect-1 省缺即抛 / "
            "defect-2 reversal-capable sign; byte-exact copy of I-10-B iso source "
            "62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081)",
            "scripts/model_registry.py", BEFORE_REG, AFTER_REG,
        ),
    ]
    OUT.write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"changes.diff {OUT.stat().st_size} B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
